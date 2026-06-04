# BitcoinZ - Electrum Web Wallet

![Logo](https://github.com/SpaceZ-Projects/electrum.btcz.rocks/blob/main/www/static/assets/Electrum.png?raw=true)

A lightweight web-based BitcoinZ wallet powered by Electrum technology.

This project brings the familiar Electrum wallet experience to the browser using:

- Python
- Electrum backend
- Toga Web
- Briefcase
- WebAssembly/Pyodide deployment

Designed for fast access, self-custody, and easy deployment.

---

# Features

- Browser-based BitcoinZ wallet
- Electrum protocol support
- Send & receive BTCZ
- Seed phrase wallet generation
- Transaction history
- Lightweight SPV wallet
- Cross-platform architecture
- Web deployment using Toga + Briefcase
- Open-source and self-hostable

---

# Installation

## Requirements

- Python 3.10+

## Create Virtual Environment

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

---

## Install Dependencies

```bash
python -m pip install --upgrade pip
pip install briefcase
```

---

# Build Web

```bash
briefcase build web -a webui -u
```

# Move Wheels

After the build completes, move generated wheels from:

```text
.build/www/static/wheels
```

to:

```text
./www/static/wheels
```

---

# Run Locally (Development Test Server)

For local testing, install FastAPI and Uvicorn:

```bash
pip install fastapi uvicorn
```

Then start the server:

```bash
python start.py
```

The application will be available at:

```
http://127.0.0.1:8080
```

---
```