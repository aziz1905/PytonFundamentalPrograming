import hashlib
import hmac
import json
import os
import secrets
from getpass import getpass

from ui import cetak_header, input_teks_valid, notifikasi

FILE_ADMIN = os.path.join(os.path.dirname(__file__), "admin_accounts.json")
ITERASI_HASH = 310_000
PANJANG_MIN_PASSWORD = 8


def _muat_admin():
    if not os.path.exists(FILE_ADMIN):
        return {}

    with open(FILE_ADMIN, "r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError("Format data administrator harus berupa objek JSON.")
    return data


def _buat_hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    hash_password = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        ITERASI_HASH,
    ).hex()
    return {"salt": salt, "hash": hash_password}


def _verifikasi_password(password, data_password):
    hash_tersimpan = data_password.get("hash", "")
    salt = data_password.get("salt", "")
    if not hash_tersimpan or not salt:
        return False

    hash_input = _buat_hash_password(password, salt)["hash"]
    return hmac.compare_digest(hash_input, hash_tersimpan)


def _simpan_admin(data_admin):
    with open(FILE_ADMIN, "w", encoding="utf-8") as file:
        json.dump(data_admin, file, indent=4, ensure_ascii=False)


def _setup_admin_pertama():
    cetak_header("SETUP ADMIN PERTAMA", "Buat kredensial administrator")
    print("\nPassword administrator minimal 8 karakter.")
    while True:
        username = input_teks_valid("Username admin: ")
        if username != "0":
            break
        print("⚠️ Username '0' tidak dapat digunakan.\n")

    while True:
        password = getpass("Password admin: ")
        if len(password) < PANJANG_MIN_PASSWORD:
            print(f"⚠️ Password minimal {PANJANG_MIN_PASSWORD} karakter.\n")
            continue
        konfirmasi = getpass("Ulangi password admin: ")
        if password != konfirmasi:
            print("⚠️ Password tidak sama. Silakan ulangi.\n")
            continue
        break

    data_admin = {
        username: {
            "password": _buat_hash_password(password),
        }
    }
    _simpan_admin(data_admin)
    notifikasi("Akun administrator berhasil dibuat.", "sukses")
    return {"username": username}


def login_admin():
    """Setup admin pertama saat diperlukan, atau autentikasi admin terdaftar."""
    data_admin = _muat_admin()
    if not data_admin:
        return _setup_admin_pertama()

    cetak_header("LOGIN ADMIN", "Masuk ke dashboard administrator")
    username = input_teks_valid("Username admin (0 untuk kembali): ")
    if username == "0":
        return None

    password = getpass("Password admin: ")
    akun = data_admin.get(username)
    if akun and _verifikasi_password(password, akun.get("password", {})):
        return {"username": username}

    notifikasi("Username atau password admin salah.", "gagal")
    return None
