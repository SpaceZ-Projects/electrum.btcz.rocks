
import asyncio
import json
import uuid
import base64
from js import localStorage


STORAGE_KEY = "electrum_btcz"

def encrypt_key(seed, password):
    from btczpy.crypto import pw_encode
    return pw_encode(seed, password)


def decrypt_key(enc_seed, password):
    from btczpy.crypto import pw_decode
    return pw_decode(enc_seed, password)


def load_accounts():
    data = localStorage.getItem(STORAGE_KEY)
    return json.loads(data) if data else []


def get_account(account_id):
    accounts = load_accounts()
    for acc in accounts:
        if acc["id"] == account_id:
            return acc
    return None


def save_accounts(accounts):
    localStorage.setItem(STORAGE_KEY, json.dumps(accounts))


def clear_accounts():
    localStorage.removeItem(STORAGE_KEY)


def create_account(key, password, name=None, type="standard", status="created"):
    accounts = load_accounts()
    if name:
        for acc in accounts:
            if acc["name"].lower() == name.lower():
                return False
    account_id = uuid.uuid4().hex[:10]
    encrypt = encrypt_key(key, password)
    if not name or not name.strip():
        name = f"wallet-{account_id}"
    account = {
        "id": account_id,
        "name": name,
        "encrypt": encrypt,
        "type": type,
        "status": status
    }
    accounts.append(account)
    save_accounts(accounts)
    return True


def delete_account(account_id):
    accounts = load_accounts()
    accounts = [a for a in accounts if a["id"] != account_id]
    save_accounts(accounts)


def list_accounts():
    return [
        {"id": acc["id"], "name": acc["name"]}
        for acc in load_accounts()
    ]


def rename_account(account_id, new_name):
    accounts = load_accounts()
    for acc in accounts:
        if acc["name"].lower() == new_name.lower() and acc["id"] != account_id:
            return False
    for acc in accounts:
        if acc["id"] == account_id:
            acc["name"] = new_name
    save_accounts(accounts)
    return True


def update_password(account_id, old_password, new_password):
    accounts = load_accounts()
    for acc in accounts:
        if acc["id"] == account_id:
            try:
                seed = decrypt_key(acc["encrypt"], old_password)
            except Exception:
                return None
            enc_seed = encrypt_key(seed, new_password)
            acc["encrypt"] = enc_seed
            save_accounts(accounts)
            return enc_seed
    return None



class Wallet:
    def __init__(self):
        
        self.id = None
        self.name = None
        self.address = None

        self._cached_password = None
        self._unlock_task = None
    
    def update(self, enc_key, type = None, status = None, password = None):
        self.enc_key = enc_key
        if type:
            self.type = type
        if status:
            self.status = status
        if password and self._cached_password:
            self._cached_password = password

    def cache_password(self, password, timer):
        self._cached_password = password
        if self._unlock_task:
            self._unlock_task.cancel()

        if timer > 0:
            seconds = int(timer * 60)
            self._unlock_task = asyncio.create_task(
                self._clear_password_after(seconds)
            )

    async def _clear_password_after(self, seconds):
        try:
            await asyncio.sleep(seconds)
            self._cached_password = None
            self._unlock_task = None
        except asyncio.CancelledError:
            pass

    def is_unlocked(self):
        return self._cached_password is not None

    def lock(self):
        self._cached_password = None
        if self._unlock_task:
            self._unlock_task.cancel()
            self._unlock_task = None

    def unlock(self, password):
        if password is None:
            password = self._cached_password
        if not password:
            raise Exception("Wallet locked")
        key = decrypt_key(self.enc_key, password)
        if self.type == "standard":
            from btczpy.keystore import from_seed
            return from_seed(key, '', False)
        elif self.type == "wif":
            return key
        
    def clear(self):
        self.lock()
        self.enc_key = None
        self.type = None
        self.status = None
        self.id = None
        self.name = None
        self.address = None


    def decrypt_key(self, password):
        if password is None:
            password = self._cached_password
        if not password:
            raise Exception("Wallet locked")
        key = decrypt_key(self.enc_key, password)
        return key

    def scripthash(self):
        if self.address:
            from btczpy.crypto import address_to_scripthash
            return address_to_scripthash(self.address)

    def get_address(self, password):
        from btczpy.crypto import public_key_to_p2pkh
        ks = self.unlock(password)
        if self.type == "standard":
            pubkey = ks.derive_pubkey(0, 0)
        else:
            from btczpy.crypto import deserialize_privkey, public_key_from_private_key
            _, privkey, compressed = deserialize_privkey(ks)
            pubkey = public_key_from_private_key(privkey, compressed)
            
        address = public_key_to_p2pkh(bytes.fromhex(pubkey))
        if not self.address:
            self.address = address
        return address
        
    
    def sign_message(self, message, password):
        ks = self.unlock(password)
        if self.type == "standard":
            sig_bytes = ks.sign_message((0, 0), message, None)
        elif self.type == "wif":
            from btczpy.crypto import deserialize_privkey, EC_KEY
            _, privkey, compressed = deserialize_privkey(ks)
            key = EC_KEY(privkey)
            sig_bytes = key.sign_message(message, compressed)
        return base64.b64encode(sig_bytes).decode()

        
    def sign_transaction(self, tx, password):
        ks = self.unlock(password)
        if self.type == "standard":
            x_pubkey = ks.get_xpubkey(0, 0)
            pubkey = ks.derive_pubkey(0, 0)
            for txin in tx.inputs():
                txin["x_pubkeys"] = [x_pubkey]
                txin["pubkeys"] = [pubkey]
            ks.sign_transaction(tx, None)
            if not tx.is_complete():
                return None
            return tx
        elif self.type == "wif":
            from btczpy.crypto import deserialize_privkey, public_key_from_private_key
            _, privkey, compressed = deserialize_privkey(ks)
            pubkey = public_key_from_private_key(privkey, compressed)
            for txin in tx.inputs():
                txin["x_pubkeys"] = [pubkey]
                txin["pubkeys"] = [pubkey]
            keypairs = {
                pubkey: (privkey, compressed)
            }
            tx.sign(keypairs)
            if not tx.is_complete():
                return None
            return tx