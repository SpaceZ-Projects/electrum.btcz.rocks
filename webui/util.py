
import re
from decimal import Decimal

from .widget import Alert


async def get_market():
    from js import fetch
    api = "https://explorer.btcz.rocks/api/market"
    try:
        options = {
            "method": "GET"
        }
        resp = await fetch(api, options)
        if not resp:
            return None
        return (await resp.json()).to_py()
    except Exception as e:
        print(f"[API ERROR] {e}")
        return None


def clipboard_copy(text):
    try:
        from js import navigator
        navigator.clipboard.writeText(text)
        Alert().show("Copied to clipboard", "success")
    except Exception:
        try:
            from js import document
            textarea = document.createElement("textarea")
            textarea.value = text
            textarea.style.position = "fixed"
            textarea.style.opacity = "0"
            document.body.appendChild(textarea)
            textarea.focus()
            textarea.select()
            document.execCommand("copy")
            document.body.removeChild(textarea)
            Alert().show("Copied to clipboard", "success")
        except Exception:
            Alert().show("Copy failed", "danger")


def format_address(addr):
    chunks = [addr[i:i+5] for i in range(0, len(addr), 5)]
    mid = (len(chunks) + 1) // 2
    line1 = " ".join(chunks[:mid])
    line2 = " ".join(chunks[mid:])
    return line1 + "\n" + line2


def is_strong_password(password: str) -> str | None:
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    if len(password) > 64:
        return "Password is too long"
    if " " in password:
        return "Password must not contain spaces"
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter"
    if not re.search(r"[0-9]", password):
        return "Password must contain at least one number"
    if not re.search(r"[!@#$%^&*()_+=\-{}\[\]:;\"'<>,.?/\\|]", password):
        return "Password must contain at least one special character"
    return None


def format_balance(value):
    value = Decimal(value)
    formatted_value = f"{value:.8f}"
    integer_part, decimal_part = formatted_value.split('.')
    if len(integer_part) > 4:
        digits_to_remove = len(integer_part) - 4
        formatted_decimal = decimal_part[:-digits_to_remove]
    else:
        formatted_decimal = decimal_part
    formatted_balance = f"{integer_part}.{formatted_decimal}"
    return formatted_balance


def format_price(price):
    price = Decimal(price)

    if price > Decimal('0.00000001') and price < Decimal('0.0000001'):
        return f"{price:.10f}"
    elif price > Decimal('0.0000001') and price < Decimal('0.000001'):
        return f"{price:.9f}"
    elif price > Decimal('0.000001') and price < Decimal('0.00001'):
        return f"{price:.8f}"
    elif price > Decimal('0.00001') and price < Decimal('0.0001'):
        return f"{price:.7f}"
    elif price > Decimal('0.0001') and price < Decimal('0.001'):
        return f"{price:.6f}"
    elif price > Decimal('0.001') and price < Decimal('0.01'):
        return f"{price:.5f}"
    elif price > Decimal('0.01') and price < Decimal('0.1'):
        return f"{price:.4f}"
    elif price > Decimal('0.1') and price < Decimal('1'):
        return f"{price:.3f}"
    elif price > Decimal('1') and price < Decimal('10'):
        return f"{price:.2f}"
    elif price > Decimal('10') and price < Decimal('100'):
        return f"{price:.1f}"
    else:
        return f"{price:.0f}"


def normalize_tx(tx, wallet_address):
    total_in = 0
    total_out = 0

    from_addresses = set()
    to_addresses = set()

    for vin in tx.get("vin", []):
        addr = vin.get("address")
        value = vin.get("value", 0)

        if addr:
            from_addresses.add(addr)

        if addr == wallet_address:
            total_in += value

    for vout in tx.get("vout", []):
        value = vout.get("value", 0)
        script = vout.get("scriptPubKey", {})
        addresses = script.get("addresses", [])

        if not addresses:
            to_addresses.add("shielded")
        else:
            addr = addresses[0]
            to_addresses.add(addr)

            if addr == wallet_address:
                total_out += value

    total_inputs = sum(vin.get("value", 0) for vin in tx.get("vin", []))
    total_outputs = sum(vout.get("value", 0) for vout in tx.get("vout", []))
    fee = max(total_inputs - total_outputs, 0)

    inputs_mine = any(vin.get("address") == wallet_address for vin in tx.get("vin", []))
    outputs_mine = wallet_address in to_addresses
    if inputs_mine and outputs_mine and len(from_addresses) == 1 and len(to_addresses) == 1:
        direction = "self"
        amount = fee
    else:
        net = total_out - total_in
        if net > 0:
            direction = "received"
            amount = net
        else:
            direction = "sent"
            amount = abs(net)
    if direction == "self":
        senders = list(from_addresses)
        receivers = list(to_addresses)
    else:
        senders = [a for a in from_addresses if a != wallet_address]
        receivers = [a for a in to_addresses if a != wallet_address]
        if not senders:
            senders = list(from_addresses) or ["Shielded"]
        if not receivers:
            receivers = list(to_addresses) or ["Shielded"]

    return {
        "txid": tx.get("txid"),
        "height": tx.get("height", 0),
        "amount": round(amount, 8),
        "direction": direction,
        "from": senders,
        "to": receivers,
        "confirmations": tx.get("confirmations", 0),
        "time": tx.get("time"),
        "size": tx.get("size"),
        "locktime": tx.get("locktime", 0),
        "fee": round(fee, 8),
    }