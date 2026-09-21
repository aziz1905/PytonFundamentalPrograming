import json
import os
import datetime

# --- KONSTANTA ---
BATAS_VIP = 7
MAKS_HARI_PINJAM = 12
BATAS_HARI_ABSEN_HANGUS = 3  
JAM_RESET_STREAK = "23:59"
FILE_JSON = "data_perpustakaan.json"  
FILE_AKUN = "akun_pengunjung.json" # FILE BARU UNTUK DATABASE AKUN

# ========================================================
# MANAJEMEN DATABASE (JSON)
# ========================================================
def muat_data(nama_file):
    if os.path.exists(nama_file):
        try:
            with open(nama_file, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            pass
    # Jika file akun, kembalikan dictionary {}. Jika file buku, kembalikan list []
    return {} if nama_file == FILE_AKUN else []

def simpan_data(data, nama_file):
    with open(nama_file, 'w') as file:
        json.dump(data, file, indent=4)

# ========================================================
# FUNGSI VALIDASI
# ========================================================
def input_angka_valid(pesan_input):
    while True:
        try:
            angka = int(input(pesan_input))
            if angka < 0:
                print("⚠️ Masukkan angka 0 atau lebih positif.\n")
                continue
            return angka
        except ValueError:
            print("⚠️ Input tidak valid! Harap masukkan angka.\n")

def input_teks_valid(pesan_input):
    while True:
        teks = input(pesan_input).strip() 
        if len(teks) == 0:
            print("⚠️ Input tidak boleh dikosongkan!\n")
        else:
            return teks

# ========================================================
# SISTEM LOGIN & REGISTRASI (FITUR BARU)
# ========================================================
def menu_autentikasi():
    database_akun = muat_data(FILE_AKUN)
    
    while True:
        print("\n" + "="*50)
        print("    SELAMAT DATANG DI NEXUS LIBRARY KIOSK    ")
        print("="*50)
        print("1. Login Pengunjung")
        print("2. Daftar Akun Baru (Register)")
        print("3. Matikan Mesin (Keluar)")
        print("="*50)
        
        pilihan = input("Pilih (1/2/3): ").strip()
        
        if pilihan == '1':
            print("\n--- LOGIN ---")
            nim = input("Masukkan NIM      : ").strip()
            password = input("Masukkan Password : ").strip()
            
            # Cek kecocokan data
            if nim in database_akun and database_akun[nim]['password'] == password:
                print(f"\n✅ Login Berhasil! Selamat datang kembali, {database_akun[nim]['nama']}.")
                return database_akun[nim], nim # Kembalikan data profil dan NIM-nya
            else:
                print("❌ GAGAL: NIM tidak terdaftar atau Password salah!")
                
        elif pilihan == '2':
            print("\n--- REGISTRASI AKUN ---")
            nim = input_teks_valid("Buat NIM / ID Anda     : ")
            if nim in database_akun:
                print("⚠️ NIM ini sudah terdaftar! Silakan Login.")
                continue
                
            nama = input_teks_valid("Masukkan Nama Lengkap  : ")
            password = input_teks_valid("Buat Password Anda     : ")
            
            # Simpan akun baru ke JSON
            database_akun[nim] = {
                "nama": nama,
                "password": password,
                "streak_saat_ini": 0 # Default pengguna baru
            }
            simpan_data(database_akun, FILE_AKUN)
            print("✅ Akun berhasil dibuat! Silakan pilih menu Login.")
            
        elif pilihan == '3':
            return None, None
        else:
            print("⚠️ Pilihan tidak valid!")

# ========================================================
# FUNGSI MENU UTAMA (SELF-SERVICE)
# ========================================================
def tambah_peminjaman_baru(semua_transaksi, user_aktif, nim_aktif):
    print("\n--- [1] PEMINJAMAN BUKU HARI INI ---")
    judul_buku = input_teks_valid("Masukkan Judul Buku           : ")
    kode_buku = input_teks_valid("Masukkan Kode / Kategori Buku : ")
    lama_pinjam = input_angka_valid("Lama Pinjam (maks 12 hari)    : ")

    tanggal_hari_ini = datetime.date.today()
    tanggal_jatuh_tempo = tanggal_hari_ini + datetime.timedelta(days=lama_pinjam)

    # Profil otomatis terisi dari Sesi Login!
    profil = {"nama": user_aktif['nama'], "nim": nim_aktif}
    
    transaksi = {
        "judul_buku": judul_buku, 
        "kode_buku": kode_buku, 
        "lama_pinjam": lama_pinjam,
        "tanggal_pinjam": str(tanggal_hari_ini),
        "jatuh_tempo": str(tanggal_jatuh_tempo)
    }

    data_pengunjung = {"profil": profil, "transaksi": transaksi}
    semua_transaksi.append(data_pengunjung)
    simpan_data(semua_transaksi, FILE_JSON)
    
    print("\n✅ Buku berhasil dipinjam!")
    print(f"Jatuh Tempo: {tanggal_jatuh_tempo}")
    input("Tekan Enter untuk kembali ke Menu Utama...")

def lihat_buku_saya(semua_transaksi, nim_aktif):
    print("\n========================================================")
    print("                 DAFTAR PINJAMAN SAYA                   ")
    print("========================================================")
    
    ada_buku = False
    for index, data in enumerate(semua_transaksi, start=1):
        # Hanya tampilkan buku milik user yang sedang Login
        if data['profil']['nim'] == nim_aktif:
            ada_buku = True
            buku = data['transaksi']['judul_buku']
            jatuh_tempo = data['transaksi'].get('jatuh_tempo', 'Tidak diketahui')
            print(f"- {buku} | Jatuh Tempo: {jatuh_tempo}")
            
    if not ada_buku:
        print("Anda sedang tidak meminjam buku apa pun saat ini.")
            
    input("\nTekan Enter untuk kembali ke Menu Utama...")

def kembalikan_buku_saya(semua_transaksi, nim_aktif):
    print("\n--- [3] PENGEMBALIAN BUKU ---")
    
    buku_dipinjam = [data for data in semua_transaksi if data['profil']['nim'] == nim_aktif]
    
    if not buku_dipinjam:
        print("Anda tidak memiliki buku yang harus dikembalikan.")
        input("\nTekan Enter untuk kembali...")
        return
        
    print("Buku yang sedang Anda pinjam:")
    for data in buku_dipinjam:
        print(f">> {data['transaksi']['judul_buku']}")
        
    konfirmasi = input("\nKembalikan semua buku ini sekarang? (y/n): ").strip().lower()
    
    if konfirmasi in ['y', 'ya', 'yes']:
        # Cari buku milik user ini, hapus dari list transaksi
        for data in buku_dipinjam:
            
            # Pengecekan Keterlambatan dan Denda
            tanggal_kembali = datetime.date.today()
            jatuh_tempo = datetime.datetime.strptime(data['transaksi']['jatuh_tempo'], "%Y-%m-%d").date()
            
            if tanggal_kembali > jatuh_tempo:
                telat = (tanggal_kembali - jatuh_tempo).days
                denda = telat * 2000
                print(f"⚠️ {data['transaksi']['judul_buku']} TERLAMBAT {telat} HARI! Denda: Rp {denda:,}".replace(',', '.'))
            else:
                print(f"✅ {data['transaksi']['judul_buku']} dikembalikan TEPAT WAKTU.")
                
            semua_transaksi.remove(data)
            
        simpan_data(semua_transaksi, FILE_JSON)
        print("\nProses pengembalian selesai.")
    else:
        print("Proses dibatalkan.")
        
    input("\nTekan Enter untuk kembali ke Menu Utama...")

# ========================================================
# PROGRAM UTAMA 
# ========================================================
def main():
    # 1. Jalankan Layar Login Dulu
    user_aktif, nim_aktif = menu_autentikasi()
    
    # Jika user pilih Keluar di menu login, program berhenti
    if not user_aktif:
        print("Sistem dimatikan.")
        return

    # 2. Muat data buku
    semua_transaksi = muat_data(FILE_JSON)

    # 3. Masuk ke Menu Kiosk Pribadi
    while True:
        print("\n" + "="*50)
        print(f"        DASHBOARD PENGUNJUNG: {user_aktif['nama'].upper()}")
        print("="*50)
        print("1. Pinjam Buku Baru")
        print("2. Lihat Buku Yang Sedang Saya Pinjam")
        print("3. Kembalikan Buku")
        print("4. Logout (Keluar Akun)")
        print("="*50)
        
        pilihan = input("Pilih Menu (1/2/3/4): ").strip()
        
        if pilihan == '1':
            tambah_peminjaman_baru(semua_transaksi, user_aktif, nim_aktif)
        elif pilihan == '2':
            lihat_buku_saya(semua_transaksi, nim_aktif)
        elif pilihan == '3':
            kembalikan_buku_saya(semua_transaksi, nim_aktif)
        elif pilihan == '4':
            print("\nAnda telah Logout. Terima kasih!")
            break # Berhenti dari loop menu pengunjung
        else:
            print("\n⚠️ Pilihan tidak valid!")

if __name__ == "__main__":
    # Agar setelah logout mesin tetap hidup untuk orang lain, kita bungkus di loop luar
    while True:
        main()
        print("\nRestarting Kiosk...\n")