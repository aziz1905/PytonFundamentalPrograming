import json
import os
import datetime
import time

# --- KONSTANTA ---
FILE_JSON = "data_perpustakaan.json"  
FILE_AKUN = "akun_pengunjung.json" 

# ========================================================
# FUNGSI USER INTERFACE (UI) & NOTIFIKASI
# ========================================================
def clear_screen():
    # Membersihkan layar terminal (Mendukung Windows / Mac / Linux)
    os.system('cls' if os.name == 'nt' else 'clear')

def notifikasi(pesan, tipe="sukses"):
    clear_screen()
    print("\n" + "="*55)
    if tipe == "sukses":
        print("                  ✅ BERHASIL ✅                 ")
    elif tipe == "gagal":
        print("                   ❌ GAGAL ❌                   ")
    elif tipe == "info":
        print("                 ℹ️ INFORMASI ℹ️                 ")
    print("="*55)
    
    # Menempatkan teks tepat di tengah-tengah kotak
    print(pesan.center(55))
    
    print("="*55 + "\n")
    
    # Memberikan efek jeda (berhenti 1.5 detik)
    time.sleep(1.5)
    clear_screen()

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
    return {} if nama_file == FILE_AKUN else []

def simpan_data(data, nama_file):
    with open(nama_file, 'w') as file:
        json.dump(data, file, indent=4)

# ========================================================
# FUNGSI VALIDASI INPUT
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
# SISTEM LOGIN & REGISTRASI
# ========================================================
def menu_autentikasi():
    database_akun = muat_data(FILE_AKUN)
    
    while True:
        clear_screen()
        print("="*55)
        print("          SELAMAT DATANG DI NEXUS KIOSK          ")
        print("="*55)
        print("1. Login Pengunjung")
        print("2. Daftar Akun Baru (Register)")
        print("3. Matikan Mesin (Keluar)")
        print("="*55)
        
        pilihan = input("Pilih (1/2/3): ").strip()
        
        if pilihan == '1':
            print("\n--- LOGIN ---")
            nim = input("Masukkan NIM      : ").strip()
            password = input("Masukkan Password : ").strip()
            
            if nim in database_akun and database_akun[nim]['password'] == password:
                notifikasi(f"Selamat datang kembali, {database_akun[nim]['nama']}!", "sukses")
                return database_akun[nim], nim 
            else:
                notifikasi("NIM tidak terdaftar atau Password salah!", "gagal")
                
        elif pilihan == '2':
            print("\n--- REGISTRASI AKUN ---")
            nim = input_teks_valid("Buat NIM / ID Anda     : ")
            if nim in database_akun:
                notifikasi("NIM ini sudah terdaftar! Silakan Login.", "gagal")
                continue
                
            nama = input_teks_valid("Masukkan Nama Lengkap  : ")
            password = input_teks_valid("Buat Password Anda     : ")
            
            database_akun[nim] = {
                "nama": nama,
                "password": password,
                "streak_saat_ini": 0 
            }
            simpan_data(database_akun, FILE_AKUN)
            notifikasi("Akun berhasil dibuat! Silakan Login.", "sukses")
            
        elif pilihan == '3':
            return None, None
        else:
            print("⚠️ Pilihan tidak valid!")
            time.sleep(1)

# ========================================================
# FUNGSI MENU UTAMA PENGUNJUNG (SELF-SERVICE)
# ========================================================
def tambah_peminjaman_baru(semua_transaksi, user_aktif, nim_aktif):
    clear_screen()
    print("--- [1] PEMINJAMAN BUKU HARI INI ---")
    judul_buku = input_teks_valid("Masukkan Judul Buku           : ")
    kode_buku = input_teks_valid("Masukkan Kode / Kategori Buku : ")
    lama_pinjam = input_angka_valid("Lama Pinjam (maks 12 hari)    : ")

    tanggal_hari_ini = datetime.date.today()
    tanggal_jatuh_tempo = tanggal_hari_ini + datetime.timedelta(days=lama_pinjam)

    profil = {"nama": user_aktif['nama'], "nim": nim_aktif}
    transaksi = {
        "judul_buku": judul_buku, 
        "kode_buku": kode_buku, 
        "lama_pinjam": lama_pinjam,
        "tanggal_pinjam": str(tanggal_hari_ini),
        "jatuh_tempo": str(tanggal_jatuh_tempo)
    }

    semua_transaksi.append({"profil": profil, "transaksi": transaksi})
    simpan_data(semua_transaksi, FILE_JSON)
    
    notifikasi("Buku berhasil dipinjam!", "sukses")
    print(f"Buku Anda wajib dikembalikan pada: {tanggal_jatuh_tempo}")
    input("\nTekan Enter untuk kembali ke Dashboard...")

def lihat_buku_saya(semua_transaksi, nim_aktif):
    clear_screen()
    print("=======================================================")
    print("                 DAFTAR PINJAMAN SAYA                  ")
    print("=======================================================")
    
    ada_buku = False
    for index, data in enumerate(semua_transaksi, start=1):
        if data['profil']['nim'] == nim_aktif:
            ada_buku = True
            buku = data['transaksi']['judul_buku']
            jatuh_tempo = data['transaksi'].get('jatuh_tempo', 'Tidak diketahui')
            print(f"- {buku} | Jatuh Tempo: {jatuh_tempo}")
            
    if not ada_buku:
        print("Anda sedang tidak meminjam buku apa pun saat ini.")
            
    input("\nTekan Enter untuk kembali ke Dashboard...")

def kembalikan_buku_saya(semua_transaksi, nim_aktif):
    clear_screen()
    print("--- [3] PENGEMBALIAN BUKU ---")
    
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
        for data in buku_dipinjam:
            # Pengecekan Keterlambatan dan Denda
            tanggal_kembali = datetime.date.today()
            jatuh_tempo = datetime.datetime.strptime(data['transaksi']['jatuh_tempo'], "%Y-%m-%d").date()
            
            if tanggal_kembali > jatuh_tempo:
                telat = (tanggal_kembali - jatuh_tempo).days
                denda = telat * 2000
                denda_str = f"Rp {denda:,}".replace(',', '.')
                print(f"⚠️ {data['transaksi']['judul_buku']} TERLAMBAT {telat} HARI! Denda: {denda_str}")
            else:
                print(f"✅ {data['transaksi']['judul_buku']} dikembalikan TEPAT WAKTU.")
                
            semua_transaksi.remove(data)
            
        simpan_data(semua_transaksi, FILE_JSON)
        input("\nProses pengembalian selesai. Tekan Enter untuk melanjutkan...")
        notifikasi("Buku telah dikembalikan!", "sukses")
    else:
        print("Proses dibatalkan.")
        time.sleep(1)

# ========================================================
# PROGRAM UTAMA 
# ========================================================
def main():
    user_aktif, nim_aktif = menu_autentikasi()
    
    if not user_aktif:
        clear_screen()
        print("Sistem dimatikan. Sampai jumpa!")
        return False # Beri sinyal untuk mematikan mesin sepenuhnya

    semua_transaksi = muat_data(FILE_JSON)

    while True:
        clear_screen()
        print("="*55)
        print(f"        DASHBOARD PENGUNJUNG: {user_aktif['nama'].upper()}")
        print("="*55)
        print("1. Pinjam Buku Baru")
        print("2. Lihat Buku Yang Sedang Saya Pinjam")
        print("3. Kembalikan Buku")
        print("4. Logout (Keluar Akun)")
        print("="*55)
        
        pilihan = input("Pilih Menu (1/2/3/4): ").strip()
        
        if pilihan == '1':
            tambah_peminjaman_baru(semua_transaksi, user_aktif, nim_aktif)
        elif pilihan == '2':
            lihat_buku_saya(semua_transaksi, nim_aktif)
        elif pilihan == '3':
            kembalikan_buku_saya(semua_transaksi, nim_aktif)
        elif pilihan == '4':
            notifikasi("Anda telah Logout. Terima kasih!", "info")
            break 
        else:
            print("\n⚠️ Pilihan tidak valid!")
            time.sleep(1)
            
    return True # Sinyal agar mesin kembali ke menu Login

if __name__ == "__main__":
    mesin_hidup = True
    while mesin_hidup:
        mesin_hidup = main()