# ========================================================
# PROTOTYPE SISTEM MANAJEMEN PERPUSTAKAAN (LIBRARY MANAGEMENT)
# Versi Peningkatan: Fungsi, Loop Utama, dan Validasi Input
# ========================================================

# --- KONSTANTA ---
BATAS_VIP = 7
MAKS_HARI_PINJAM = 12
JAM_RESET_STREAK = "23:59"

# --- FUNGSI VALIDASI ---
# Fungsi ini memastikan user hanya memasukkan angka, mencegah program error (crash)
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

# --- FUNGSI LOGIKA STREAK ---
# Memisahkan logika perhitungan dari tampilan agar lebih rapi
def hitung_status_streak(streak_awal):
    streak_baru = streak_awal + 1

    if streak_awal == 0:
        status = "🔥 Day 1 (Welcome to the Challenge!)"
        pesan_bonus = f"Mulai streak-mu hari ini! Capai Day {BATAS_VIP} untuk VIP Access."
    elif 0 < streak_awal < (BATAS_VIP - 1):
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
    print(f"Durasi Pinjam    : {transaksi['lama_pinjam']} Hari")
    print("--------------------------------------------------------")
    print("STATUS STREAK KAMU HARI INI:")
    print(f">> {streak['status']}")
    print(f">> {streak['pesan_bonus']}")
    print("========================================================")
    print(f"Kembali lagi besok sebelum jam {JAM_RESET_STREAK} agar streak")
    print("kamu tidak hangus dan kembali ke angka 0!")
    print("========================================================\n")

# --- PROGRAM UTAMA (MAIN LOOP) ---
def main():
    while True:
        print("\n========================================================")
        print("             NEXUS LIBRARY & HABIT TRACKER              ")
        print("    Bangun kebiasaan membacamu. Jangan putus streak-nya!  ")
        print("========================================================")

        # 1. Registrasi
        print("\n--- [1] REGISTRASI & STATUS STREAK ---")
        nama = input("Masukkan Nama Lengkap          : ")
        nim = input("Masukkan NIM / ID Anggota      : ")

        print("\nBerapa hari berturut-turut kamu sudah meminjam/membaca buku?")
        print("(Ketik '0' jika kamu adalah pengguna baru)")
        streak_awal = input_angka_valid("Masukkan jumlah hari (angka)   : ")

        # 2. Proses Logika Streak
        streak_baru, status, pesan_bonus = hitung_status_streak(streak_awal)

        # 3. Transaksi
        print("\n--- [2] PEMINJAMAN BUKU HARI INI ---")
        judul_buku = input("Masukkan Judul Buku            : ")
        print(f"----------------Estimasi {MAKS_HARI_PINJAM} Hari-------------------")
        lama_pinjam = input_angka_valid("Lama Pinjam (hari)             : ")

        # 4. Susun Data (Dictionary)
        profil = {"nama": nama, "nim": nim}
        transaksi = {"judul_buku": judul_buku, "lama_pinjam": lama_pinjam}
        streak = {"baru": streak_baru, "status": status, "pesan_bonus": pesan_bonus}

        # 5. Tampilkan Output
        cetak_struk(profil, transaksi, streak)

        # 6. Konfirmasi Lanjut/Keluar
        lanjut = input("Proses pengunjung lain? (y/n): ").strip().lower()
        if lanjut != 'y':
            print("\nTerima kasih telah menggunakan Nexus Library System. Sistem ditutup.")
            break

# Menjalankan program utama
if __name__ == "__main__":
    main()