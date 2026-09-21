import time

# Memanggil fungsi-fungsi dari file ui.py dan database.py yang baru kita buat
from database import muat_data, simpan_data, FILE_AKUN
from ui import clear_screen, notifikasi, input_teks_valid

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
            
            database_akun[nim] = {"nama": nama, "password": password, "streak_saat_ini": 0}
            simpan_data(database_akun, FILE_AKUN)
            notifikasi("Akun berhasil dibuat! Silakan Login.", "sukses")
            
        elif pilihan == '3':
            return None, None
        else:
            print("⚠️ Pilihan tidak valid!")
            time.sleep(1)