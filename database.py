import json
import os

FILE_JSON = "data_perpustakaan.json"  
FILE_AKUN = "akun_pengunjung.json" 
FILE_KATALOG = "katalog_buku.json"  # <-- FILE BARU UNTUK STOK BUKU

def muat_data(nama_file):
    if os.path.exists(nama_file):
        try:
            with open(nama_file, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            pass
            
    # --- FITUR KATALOG (DEFAULT DATA) ---
    if nama_file == FILE_KATALOG:
        # Jika file belum ada, kita injeksi (masukkan) data buku default
        buku_default = {
            "PY-01": {"judul": "Python Fundamental", "stok": 3},
            "DB-02": {"judul": "Database Relational Basic", "stok": 2},
            "ML-03": {"judul": "Machine Learning 101", "stok": 5},
            "WEB-04": {"judul": "Web Development HTML", "stok": 1}
        }
        simpan_data(buku_default, FILE_KATALOG)
        return buku_default
        
    return {} if nama_file == FILE_AKUN else []

def simpan_data(data, nama_file):
    with open(nama_file, 'w') as file:
        json.dump(data, file, indent=4)