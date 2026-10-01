import json
import os

FILE_JSON = "data_perpustakaan.json"  
FILE_AKUN = "akun_pengunjung.json" 
FILE_KATALOG = "katalog_buku.json"

# ==============================================================================
# CONTOH PENGGUNAAN TUPLE:
# Data konfigurasi sistem bersifat tetap (immutable) sehingga sangat tepat
# disimpan dalam bentuk TUPLE agar tidak sengaja termodifikasi saat runtime.
# Format Tuple: (MAKS_HARI_PINJAM, TARIF_DENDA_PER_HARI, MAKS_BUKU_SEKALIGUS)
# ==============================================================================
KONFIGURASI_PERPUSTAKAAN = (12, 2000, 3)

# ==============================================================================
# CONTOH PENGGUNAAN TUPLE OF TUPLES:
# Master data penghargaan / badge reading streak (Target Hari, Nama Badge)
# ==============================================================================
BADGE_STREAK = (
    (1, "Bibliofil Pemula 🥉"),
    (3, "Pembaca Rajin 🥈"),
    (7, "Kutu Buku Sejati 🥇"),
    (14, "Legenda Literasi 👑")
)

# ==============================================================================
# CONTOH PENGGUNAAN TUPLE OF TUPLES:
# Faktor kecepatan membaca berdasarkan habit reading streak
# Format: (Min_Streak_Hari, Faktor_Pengali, Label_Status, Persen_Efisiensi)
# ==============================================================================
FAKTOR_KECEPATAN_STREAK = (
    (14, 0.50, "Master Literasi 👑", 50),
    (7, 0.65, "Kutu Buku Aktif 🥇", 35),
    (3, 0.80, "Pembaca Konsisten 🥈", 20),
    (1, 0.90, "Pembaca Pemula 🥉", 10),
    (0, 1.00, "Standar (Belum Ada Streak)", 0)
)

# ==============================================================================
# CONTOH PENGGUNAAN LIST:
# Kategori buku bersifat dinamis (mutable) sehingga mudah ditambah/dikelola
# ==============================================================================
DAFTAR_KATEGORI = ["Semua", "Pemrograman", "Database", "AI & Data", "Web Development"]

def muat_data(nama_file):
    if os.path.exists(nama_file):
        try:
            with open(nama_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except json.JSONDecodeError:
            pass
            
    # --- FITUR KATALOG (DEFAULT DATA DENGAN LIST KATEGORI & LOKASI) ---
    if nama_file == FILE_KATALOG:
        buku_default = {
            "PY-01": {
                "judul": "Python Fundamental & OOP",
                "stok": 3,
                "kategori": ["Pemrograman", "Python", "Dasar"],
                "lokasi": ["Lantai 1", "Rak A-01"]
            },
            "DB-02": {
                "judul": "Database Relational & SQL",
                "stok": 2,
                "kategori": ["Database", "Backend"],
                "lokasi": ["Lantai 1", "Rak B-02"]
            },
            "ML-03": {
                "judul": "Machine Learning & AI 101",
                "stok": 5,
                "kategori": ["AI & Data", "Python"],
                "lokasi": ["Lantai 2", "Rak C-03"]
            },
            "WEB-04": {
                "judul": "Modern Web Development",
                "stok": 1,
                "kategori": ["Web Development", "Frontend"],
                "lokasi": ["Lantai 2", "Rak D-04"]
            }
        }
        simpan_data(buku_default, FILE_KATALOG)
        return buku_default
        
    return {} if nama_file == FILE_AKUN else []

def simpan_data(data, nama_file):
    with open(nama_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)