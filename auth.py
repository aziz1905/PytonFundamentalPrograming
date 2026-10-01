import datetime
import time

from database import muat_data, simpan_data, FILE_AKUN
from ui import cetak_header, notifikasi, input_teks_valid

def menu_autentikasi():
    database_akun = muat_data(FILE_AKUN)
    
    while True:
        cetak_header("NEXUS KIOSK - PERPUSTAKAAN MANDIRI", "Silakan Masuk atau Daftarkan Akun Anda")
        
        print("\n [1] 🔑 Login Pengunjung (NIM & Password)")
        print(" [2] 📝 Daftar Akun Baru (Registrasi)")
        print(" [0] 🔌 Matikan Kiosk (Keluar)")
        print("─" * 60)
        
        pilihan = input("\nMasukkan pilihan menu (0-2): ").strip()
        
        if pilihan == '1':
            cetak_header("LOGIN PENGUNJUNG", "Masukkan Akun Terdaftar")
            print("\n💡 Ketik '0' pada kolom NIM jika ingin kembali ke menu awal.\n")
            nim = input(" Masukkan NIM / ID : ").strip()
            
            if nim in ("0", "batal", "BATAL"):
                continue
                
            password = input(" Masukkan Password : ").strip()
            
            if nim in database_akun and database_akun[nim]['password'] == password:
                user = database_akun[nim]
                
                # ==============================================================
                # 🚀 LOGIKA PENAMBAHAN STREAK OTOMATIS SAAT LOGIN:
                # ==============================================================
                hari_ini = datetime.date.today()
                hari_ini_str = str(hari_ini)
                terakhir_login = user.get('terakhir_checkin', "")
                streak_sekarang = user.get('streak_saat_ini', 0)
                
                if terakhir_login == hari_ini_str:
                    # Sudah login hari ini, streak dipertahankan
                    pesan_streak = f"🔥 Reading Streak: {streak_sekarang} Hari [Aktif Hari Ini ✅]"
                elif terakhir_login == str(hari_ini - datetime.timedelta(days=1)):
                    # Login konsisten berturut-turut hari berikutnya (+1 Streak)
                    streak_sekarang += 1
                    user['streak_saat_ini'] = streak_sekarang
                    user['terakhir_checkin'] = hari_ini_str
                    pesan_streak = f"🔥 STREAK NAIK! Menjadi {streak_sekarang} Hari Berturut-turut 🎉"
                else:
                    # Login pertama kali atau memulai kembali setelah terputus (Streak = 1)
                    streak_sekarang = 1
                    user['streak_saat_ini'] = streak_sekarang
                    user['terakhir_checkin'] = hari_ini_str
                    pesan_streak = f"🔥 Streak Menyala: 1 Hari! Pertahankan besok 🚀"
                    
                # Simpan update streak akun ke database JSON
                simpan_data(database_akun, FILE_AKUN)
                
                notifikasi(
                    f"Selamat datang kembali, {user['nama']}!\n{pesan_streak}", 
                    "sukses", 
                    durasi=2.0
                )
                return user, nim 
            else:
                notifikasi("NIM tidak terdaftar atau Password salah!", "gagal")
                
        elif pilihan == '2':
            cetak_header("REGISTRASI AKUN BARU", "Lengkapi Data Diri Pengunjung")
            print("\n💡 Ketik '0' jika ingin membatalkan pendaftaran.\n")
            nim = input_teks_valid(" Buat NIM / ID Pengunjung : ")
            
            if nim in ("0", "batal", "BATAL"):
                continue
                
            if nim in database_akun:
                notifikasi("NIM ini sudah terdaftar! Silakan pilih menu Login.", "gagal")
                continue
                
            nama = input_teks_valid(" Masukkan Nama Lengkap    : ")
            password = input_teks_valid(" Buat Password Akun Anda  : ")
            
            # Inisialisasi akun baru
            database_akun[nim] = {
                "nama": nama,
                "password": password,
                "streak_saat_ini": 0,
                "terakhir_checkin": "",
                "riwayat_baca": [],
                "history_peminjaman": []
            }
            simpan_data(database_akun, FILE_AKUN)
            notifikasi("Akun berhasil dibuat! Silakan Login sekarang.", "sukses")
            
        elif pilihan in ('0', '3', 'keluar', 'exit'):
            return None, None
        else:
            print("\n⚠️ Pilihan tidak valid! Harap pilih menu yang tersedia.")
            time.sleep(1)