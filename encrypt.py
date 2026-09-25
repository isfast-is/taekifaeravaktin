#!/usr/bin/env python3
"""Encrypt app.html -> content.enc for the Tækifæravaktin.

Usage: python3 encrypt.py            (passphrase read from .passphrase file)
Same parameters as the landing page (index.html WebCrypto):
PBKDF2-SHA256 / 300000 iterations / 16-byte salt -> AES-256-GCM / 12-byte IV.
app.html and .passphrase are gitignored — only content.enc is published.
"""
import base64
import json
import os
import sys

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, ".passphrase")) as f:
    passphrase = f.read().strip()
with open(os.path.join(HERE, "app.html"), "rb") as f:
    plaintext = f.read()

salt = os.urandom(16)
iv = os.urandom(12)
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt,
                 iterations=300000).derive(passphrase.encode())
ciphertext = AESGCM(key).encrypt(iv, plaintext, None)

b64 = lambda b: base64.b64encode(b).decode()
with open(os.path.join(HERE, "content.enc"), "w") as f:
    json.dump({"salt": b64(salt), "iv": b64(iv), "data": b64(ciphertext)}, f)
print("content.enc written")
