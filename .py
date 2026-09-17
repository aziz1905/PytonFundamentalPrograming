# ========================================================
# PROTOTYPE SISTEM MANAJEMEN PERPUSTAKAAN (LIBRARY MANAGEMENT)
# Versi Peningkatan: Modular (Fungsi, Loop Utama, Validasi Input, & Aturan Streak Hangus)
# Scope: CONDITIONAL STATEMENTS (if, elif, else, and, or)
# ========================================================

# --- KONSTANTA ---
BATAS_VIP = 7
MAKS_HARI_PINJAM = 12
BATAS_HARI_ABSEN_HANGUS = 3  # Batas maksimal hari tidak pinjam sebelum streak hangus
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

# --- FUNGSI LOGIKA STREAK DENGAN CONDITIONAL STATEMENTS ---
# Memproses status streak berdasarkan keaktifan & ketepatan waktu pengembalian
def hitung_status_streak(streak_awal, hari_absen, status_terlambat):
    terlambat = status_terlambat.strip().lower() in ['y', 'ya', 'yes', 'true']
    
    # 1. KONDISI PENGGUNA BARU
    if streak_awal == 0:
        streak_baru = 1
        status = "🔥 Day 1 (Welcome to the Challenge!)"
        pesan_bonus = f"Mulai streak-mu hari ini! Capai Day {BATAS_VIP} untuk VIP Access."

    # 2. KONDISI STREAK HANGUS (Absen >= 3 hari ATAU Terlambat)
    elif hari_absen >= BATAS_HARI_ABSEN_HANGUS or terlambat:
        streak_baru = 1  # Reset kembali ke Day 1
        status = "💔 STREAK HANGUS (Reset ke Day 1)"

        if hari_absen >= BATAS_HARI_ABSEN_HANGUS and terlambat:
            pesan_bonus = f"Streak hilang karena absen {hari_absen} hari berturut-turut DAN terlambat mengembalikan buku!"
        elif hari_absen >= BATAS_HARI_ABSEN_HANGUS:
            pesan_bonus = f"Streak hilang karena tidak meminjam selama {hari_absen} hari (Batas maks: {BATAS_HARI_ABSEN_HANGUS - 1} hari)."
        else:
            pesan_bonus = "Streak hilang karena keterlambatan pengembalian buku sebelumnya!"

    # 3. KONDISI STREAK BERHASIL DIPERTAHANKAN & BERTAMBAH
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
    print("--------------------------------------------------------")
    print("STATUS STREAK KAMU HARI INI:")
    print(f">> {streak['status']}")
    print(f">> Catatan: {streak['pesan_bonus']}")
    print("========================================================")
    print(f"Kembali lagi besok sebelum jam {JAM_RESET_STREAK} dan kembalikan")
    print(f"tepat waktu agar streak tidak hangus!")
    print("========================================================\n")

# --- PROGRAM UTAMA (MAIN LOOP) ---
def main():
    while True:
        print("\n========================================================")
        print("             NEXUS LIBRARY & HABIT TRACKER              ")
        print("    Bangun kebiasaan membacamu. Jangan putus streak-nya!  ")
        print("========================================================")

        # 1. Registrasi & Input Data Pengunjung
        print("\n--- [1] REGISTRASI & STATUS STREAK ---")
        nama = input("Masukkan Nama Lengkap                  : ")
        nim = input("Masukkan NIM / ID Anggota              : ")

        print("\nBerapa hari streak kamu sebelumnya? (Ketik '0' jika baru)")
        streak_awal = input_angka_valid("Masukkan jumlah streak awal            : ")

        # Input kondisi pengecekan streak jika bukan pengguna baru
        hari_absen = 0
        status_terlambat = "t"
        if streak_awal > 0:
            print("\n[Pengecekan Keaktifan & Ketepatan Waktu]")
            hari_absen = input_angka_valid("Berapa hari sejak peminjaman terakhir? : ")
            status_terlambat = input("Apakah pengembalian terakhir terlambat? (y/n): ")

        # 2. Proses Logika Streak
        streak_baru, status, pesan_bonus = hitung_status_streak(streak_awal, hari_absen, status_terlambat)

        # 3. Transaksi Peminjaman
        print("\n--- [2] PEMINJAMAN BUKU HARI INI ---")
        judul_buku = input("Masukkan Judul Buku                    : ")
        kode_buku = input("Masukkan Kode / Kategori Buku          : ")
        print(f"----------------Estimasi {MAKS_HARI_PINJAM} Hari-------------------")
        lama_pinjam = input_angka_valid("Lama Pinjam (hari)                     : ")

        # 4. Susun Data (Dictionary)
        profil = {"nama": nama, "nim": nim}
        transaksi = {"judul_buku": judul_buku, "kode_buku": kode_buku, "lama_pinjam": lama_pinjam}
        streak = {"baru": streak_baru, "status": status, "pesan_bonus": pesan_bonus}

        # 5. Tampilkan Output
        cetak_struk(profil, transaksi, streak)

        # 6. Konfirmasi Lanjut/Keluar
        lanjut = input("Proses pengunjung lain? (y/n): ").strip().lower()
        if lanjut not in ['y', 'ya', 'yes']:
            print("\nTerima kasih telah menggunakan Nexus Library System. Sistem ditutup.")
            break

# Menjalankan program utama
if __name__ == "__main__":
    main()