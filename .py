# ========================================================
# PROTOTYPE SISTEM MANAJEMEN PERPUSTAKAAN (LIBRARY MANAGEMENT)
# Versi Peningkatan: Modular, Auto-Save JSON, Menu, Return Book, Text Validation, & DATETIME
# ========================================================

import json
import os
import datetime  # MENGIMPOR MODUL TANGGAL & WAKTU BAWAAN PYTHON

# --- KONSTANTA ---
BATAS_VIP = 7
MAKS_HARI_PINJAM = 12
BATAS_HARI_ABSEN_HANGUS = 3  
JAM_RESET_STREAK = "23:59"
FILE_JSON = "data_perpustakaan.json"  

# --- FUNGSI MANAJEMEN JSON ---
def muat_data():
    if os.path.exists(FILE_JSON):
        try:
            with open(FILE_JSON, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            return []
    return []

def simpan_data(data):
    with open(FILE_JSON, 'w') as file:
        json.dump(data, file, indent=4)
    print("\n[INFO] Perubahan data berhasil disimpan otomatis ke JSON.")

# --- FUNGSI VALIDASI INPUT ---
def input_angka_valid(pesan_input):
    while True:
        try:
            angka = int(input(pesan_input))
            if angka < 0:
                print("⚠️ Peringatan: Masukkan angka 0 atau lebih positif.\n")
                continue
            return angka
        except ValueError:
            print("⚠️ Peringatan: Input tidak valid! Harap masukkan format angka (contoh: 0, 1, 2).\n")

def input_teks_valid(pesan_input):
    while True:
        teks = input(pesan_input).strip() 
        if len(teks) == 0:
            print("⚠️ Peringatan: Input tidak boleh dikosongkan! Harap isi datanya.\n")
        else:
            return teks

# --- FUNGSI LOGIKA STREAK ---
def hitung_status_streak(streak_awal, hari_absen, status_terlambat):
    terlambat = status_terlambat.strip().lower() in ['y', 'ya', 'yes', 'true']
    
    if streak_awal == 0:
        streak_baru = 1
        status = "🔥 Day 1 (Welcome to the Challenge!)"
        pesan_bonus = f"Mulai streak-mu hari ini! Capai Day {BATAS_VIP} untuk VIP Access."
    elif hari_absen >= BATAS_HARI_ABSEN_HANGUS or terlambat:
        streak_baru = 1  
        status = "💔 STREAK HANGUS (Reset ke Day 1)"
        if hari_absen >= BATAS_HARI_ABSEN_HANGUS and terlambat:
            pesan_bonus = f"Streak hilang karena absen {hari_absen} hari berturut-turut DAN terlambat mengembalikan buku!"
        elif hari_absen >= BATAS_HARI_ABSEN_HANGUS:
            pesan_bonus = f"Streak hilang karena tidak meminjam selama {hari_absen} hari (Batas maks: {BATAS_HARI_ABSEN_HANGUS - 1} hari)."
        else:
            pesan_bonus = "Streak hilang karena keterlambatan pengembalian buku sebelumnya!"
    else:
        streak_baru = streak_awal + 1
        if streak_baru < BATAS_VIP:
            status = f"🔥 Day {streak_baru} (On Fire!)"
            sisa_hari = BATAS_VIP - streak_baru
            pesan_bonus = f"Pertahankan! {sisa_hari} hari lagi menuju VIP Access."
        else:
            status = f"👑 Day {streak_baru} (Legendary Reader!)"
            pesan_bonus = "VIP UNLOCKED! Kamu berhak meminjam 2 buku ekstra & Bebas Denda."

    return streak_baru, status, pesan_bonus

# --- FUNGSI CETAK STRUK ---
def cetak_struk(profil, transaksi, streak):
    print("\n========================================================")
    print("              STRUK PEMINJAMAN & STREAK                 ")
    print("========================================================")
    print(f"Nama Member      : {profil['nama']}")
    print(f"NIM / ID         : {profil['nim']}")
    print("--------------------------------------------------------")
    print(f"Buku Dipinjam    : {transaksi['judul_buku']}")
    print(f"Kode/Kategori    : {transaksi['kode_buku']}")
    print(f"Durasi Pinjam    : {transaksi['lama_pinjam']} Hari")
    # MENAMPILKAN TANGGAL
    print(f"Tanggal Pinjam   : {transaksi['tanggal_pinjam']}")
    print(f"Jatuh Tempo      : {transaksi['jatuh_tempo']}")
    print("--------------------------------------------------------")
    print("STATUS STREAK KAMU HARI INI:")
    print(f">> {streak['status']}")
    print(f">> Catatan: {streak['pesan_bonus']}")
    print("========================================================")
    print(f"Kembalikan tepat waktu sebelum {transaksi['jatuh_tempo']}")
    print(f"agar streak tidak hangus!")
    print("========================================================\n")


# ========================================================
# BAGIAN MENU & MODULARISASI 
# ========================================================

def tambah_peminjaman_baru(semua_transaksi):
    print("\n--- [1] REGISTRASI & STATUS STREAK ---")
    nama = input_teks_valid("Masukkan Nama Lengkap                  : ")
    nim = input_teks_valid("Masukkan NIM / ID Anggota              : ")

    print("\nBerapa hari streak kamu sebelumnya? (Ketik '0' jika baru)")
    streak_awal = input_angka_valid("Masukkan jumlah streak awal            : ")

    hari_absen = 0
    status_terlambat = "t"
    
    # Keterlambatan dan hari absen manual (untuk peminjam lama yang datanya belum otomatis)
    if streak_awal > 0:
        print("\n[Pengecekan Keaktifan & Ketepatan Waktu]")
        hari_absen = input_angka_valid("Berapa hari sejak peminjaman terakhir? : ")
        status_terlambat = input("Apakah pengembalian terakhir terlambat? (y/n): ")

    streak_baru, status, pesan_bonus = hitung_status_streak(streak_awal, hari_absen, status_terlambat)

    print("\n--- [2] PEMINJAMAN BUKU HARI INI ---")
    judul_buku = input_teks_valid("Masukkan Judul Buku                    : ")
    kode_buku = input_teks_valid("Masukkan Kode / Kategori Buku          : ")
    print(f"----------------Estimasi {MAKS_HARI_PINJAM} Hari-------------------")
    lama_pinjam = input_angka_valid("Lama Pinjam (hari)                     : ")

    # ================= FITUR DATETIME =================
    tanggal_hari_ini = datetime.date.today()
    # timedelta digunakan untuk menambahkan durasi hari ke tanggal hari ini
    tanggal_jatuh_tempo = tanggal_hari_ini + datetime.timedelta(days=lama_pinjam)
    
    # Kita ubah formatnya menjadi String agar bisa masuk ke JSON
    str_hari_ini = str(tanggal_hari_ini)
    str_jatuh_tempo = str(tanggal_jatuh_tempo)
    # ==================================================

    profil = {"nama": nama, "nim": nim}
    
    # Tambahkan field tanggal_pinjam dan jatuh_tempo ke transaksi
    transaksi = {
        "judul_buku": judul_buku, 
        "kode_buku": kode_buku, 
        "lama_pinjam": lama_pinjam,
        "tanggal_pinjam": str_hari_ini,
        "jatuh_tempo": str_jatuh_tempo
    }
    
    streak = {"baru": streak_baru, "status": status, "pesan_bonus": pesan_bonus}

    data_pengunjung = {
        "profil": profil,
        "transaksi": transaksi,
        "streak": streak
    }
    
    semua_transaksi.append(data_pengunjung)
    simpan_data(semua_transaksi)
    cetak_struk(profil, transaksi, streak)
    
    input("Tekan Enter untuk kembali ke Menu Utama...")


def lihat_data_peminjam(semua_transaksi):
    print("\n========================================================")
    print("             DAFTAR PEMINJAM AKTIF                      ")
    print("========================================================")
    
    if len(semua_transaksi) == 0:
        print("Belum ada data peminjaman di sistem.")
    else:
        for index, data in enumerate(semua_transaksi, start=1):
            nama = data['profil']['nama']
            nim = data['profil']['nim']
            buku = data['transaksi']['judul_buku']
            jatuh_tempo = data['transaksi'].get('jatuh_tempo', 'Tidak diketahui')
            
            print(f"{index}. {nama} ({nim}) | Buku: {buku}")
            print(f"   Jatuh Tempo: {jatuh_tempo}")
            print("   -----------------------------------------------------")
            
    input("\nTekan Enter untuk kembali ke Menu Utama...")


def pengembalian_buku(semua_transaksi):
    print("\n--- [3] PENGEMBALIAN BUKU ---")
    
    if len(semua_transaksi) == 0:
        print("Belum ada data peminjaman aktif.")
        input("\nTekan Enter untuk kembali ke Menu Utama...")
        return
        
    cari_nim = input_teks_valid("Masukkan NIM Peminjam yang mengembalikan buku: ")
    
    data_ditemukan = False
    
    for index, data in enumerate(semua_transaksi):
        if data['profil']['nim'] == cari_nim:
            data_ditemukan = True
            print("\n>> Data Ditemukan!")
            print(f"Nama : {data['profil']['nama']}")
            print(f"Buku : {data['transaksi']['judul_buku']}")
            
            # ================= PENGECEKAN KETERLAMBATAN =================
            tanggal_kembali = datetime.date.today()
            jatuh_tempo_str = data['transaksi'].get('jatuh_tempo', str(tanggal_kembali))
            
            # strptime: mengubah string "YYYY-MM-DD" kembali menjadi objek date Python
            jatuh_tempo = datetime.datetime.strptime(jatuh_tempo_str, "%Y-%m-%d").date()
            
            print(f"Tgl Jatuh Tempo    : {jatuh_tempo_str}")
            print(f"Tgl Dikembalikan   : {tanggal_kembali}")
            
            # Cek keterlambatan menggunakan operator perbandingan (>)
            if tanggal_kembali > jatuh_tempo:
                telat = (tanggal_kembali - jatuh_tempo).days
                print(f"⚠️ STATUS: TERLAMBAT {telat} HARI!")
                print("⚠️ STREAK HANGUS: Keterlambatan ini akan menghanguskan streak peminjam di kunjungan berikutnya!")
            else:
                print("✅ STATUS: TEPAT WAKTU (Streak Aman!)")
            # ============================================================

            konfirmasi = input("\nSelesaikan peminjaman (kembalikan buku)? (y/n): ").strip().lower()
            if konfirmasi in ['y', 'ya', 'yes']:
                semua_transaksi.pop(index)
                simpan_data(semua_transaksi)
                print("✅ Buku berhasil dikembalikan. Data peminjaman telah dihapus dari sistem aktif.")
            else:
                print("❌ Proses pengembalian dibatalkan.")
                
            break 
            
    if not data_ditemukan:
        print(f"\n⚠️ Data dengan NIM '{cari_nim}' tidak ditemukan di sistem.")
        
    input("\nTekan Enter untuk kembali ke Menu Utama...")


# --- PROGRAM UTAMA (MAIN LOOP) ---
def main():
    semua_transaksi = muat_data()
    print(f"[SYSTEM] Berhasil memuat {len(semua_transaksi)} data pengunjung dari database.")

    while True:
        print("\n========================================================")
        print("             NEXUS LIBRARY & HABIT TRACKER              ")
        print("    Bangun kebiasaan membacamu. Jangan putus streak-nya!  ")
        print("========================================================")
        print("1. Tambah Peminjaman Baru")
        print("2. Lihat Semua Data Peminjam Aktif")
        print("3. Pengembalian Buku (Cek Keterlambatan)")
        print("4. Keluar dari Program")
        print("========================================================")
        
        pilihan = input("Pilih Menu (1/2/3/4): ").strip()
        
        if pilihan == '1':
            tambah_peminjaman_baru(semua_transaksi)
        elif pilihan == '2':
            lihat_data_peminjam(semua_transaksi)
        elif pilihan == '3':
            pengembalian_buku(semua_transaksi)
        elif pilihan == '4':
            print("\nTerima kasih telah menggunakan Nexus Library System. Sistem ditutup.")
            break
        else:
            print("\n⚠️ Pilihan tidak valid! Silakan ketik angka 1, 2, 3, atau 4.")

if __name__ == "__main__":
    main()