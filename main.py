import datetime
import time

# --- PUSAT KENDALI: IMPOR MODUL SISTEM BERSIH & TERSTRUKTUR ---
from database import (
    muat_data,
    FILE_JSON,
    FILE_AKUN,
    FILE_KATALOG,
    FILE_ULASAN,
    DAFTAR_KATEGORI,
)
from ui import (
    LEBAR_TAMPILAN,
    clear_screen,
    cetak_header,
    cetak_kartu,
    notifikasi,
)
from auth import menu_autentikasi
from admin.dashboard import dashboard_admin
from analytics import hitung_estimasi_peminjaman
from catalog_service import dapatkan_list_buku, tampilkan_tabel_katalog
from loans import (
    tambah_peminjaman_baru,
    lihat_buku_saya,
    kembalikan_buku_saya,
)
from habits import reading_habit_tracker


def cari_dan_filter_katalog(katalog, ulasan_buku):
    """
    Menu eksplorasi katalog yang ramah dan interaktif (HCD).
    """
    while True:
        cetak_header("KATALOG & PENCARIAN BUKU", "Eksplorasi Koleksi Perpustakaan")

        print("\nPilih Cara Menjelajahi Koleksi:")
        print(" [1] 📋 Tampilkan Seluruh Koleksi Buku")
        print(" [2] 🏷️  Filter berdasarkan Kategori / Genre")
        print(" [3] 🔍 Cari dengan Kata Kunci (Judul, Topik, atau Kode)")
        print(" [0] ↩️  Kembali ke Dashboard Utama")
        print("─" * LEBAR_TAMPILAN)

        pilihan = input("\nMasukkan pilihan menu (0-3): ").strip()

        if pilihan == "0":
            break

        elif pilihan == "1":
            daftar = dapatkan_list_buku(katalog, filter_kategori="Semua")
            cetak_header("SELURUH KOLEKSI BUKU", f"Total: {len(daftar)} Judul Buku")
            tampilkan_tabel_katalog(daftar, ulasan_buku)
            input("\nTekan Enter untuk kembali ke menu pencarian...")

        elif pilihan == "2":
            cetak_header("FILTER KOLEKSI BERDASARKAN KATEGORI")
            print("\nDaftar Kategori yang Tersedia:")
            kategori_opsi = [k for k in DAFTAR_KATEGORI if k != "Semua"]
            for idx, kat in enumerate(kategori_opsi, 1):
                print(f" [{idx}] {kat}")
            print(" [0] Batal")

            pilih_k = input("\nPilih nomor kategori: ").strip()
            if pilih_k == "0":
                continue

            try:
                idx_k = int(pilih_k)
                if 1 <= idx_k <= len(kategori_opsi):
                    kat_terpilih = kategori_opsi[idx_k - 1]
                    daftar = dapatkan_list_buku(katalog, filter_kategori=kat_terpilih)
                    cetak_header(f"KOLEKSI KATEGORI: {kat_terpilih.upper()}", f"Ditemukan: {len(daftar)} Buku")
                    tampilkan_tabel_katalog(daftar, ulasan_buku)
                    input("\nTekan Enter untuk kembali...")
                else:
                    print("⚠️ Nomor kategori tidak valid.")
                    time.sleep(1)
            except ValueError:
                print("⚠️ Masukkan angka yang valid.")
                time.sleep(1)

        elif pilihan == "3":
            cetak_header("PENCARIAN BUKU")
            print("\n💡 Tips: Anda bisa mencari judul (misal: 'Python'), genre ('Database'), atau kode ('PY-01').")
            keyword = input("\nMasukkan kata kunci pencarian (0 untuk Batal): ").strip()

            if keyword in ("0", ""):
                continue

            daftar = dapatkan_list_buku(katalog, filter_keyword=keyword)
            cetak_header(f"HASIL PENCARIAN: '{keyword}'", f"Ditemukan {len(daftar)} Buku")
            tampilkan_tabel_katalog(daftar, ulasan_buku)
            input("\nTekan Enter untuk kembali...")


def menu_history_dan_estimasi(user_aktif, nim_aktif, database_akun):
    """
    Dashboard visual riwayat peminjaman dan analisis estimasi kecepatan membaca (HCD).
    """
    cetak_header("RIWAYAT PEMINJAMAN & ESTIMASI BACA", f"Pengguna: {user_aktif['nama'].upper()}")

    data_user = database_akun.get(nim_aktif, user_aktif)
    history_peminjaman = data_user.get('history_peminjaman', [])
    streak_hari = data_user.get('streak_saat_ini', 0)

    est_hari, rek_pinjam, avg_hist, persen_efisiensi, status_streak = hitung_estimasi_peminjaman(
        history_peminjaman, streak_hari
    )

    print()
    cetak_kartu(
        "PROFIL & ANALISIS ESTIMASI KEBIASAAN MEMBACA",
        [
            f"Reading Streak Aktif : {streak_hari} Hari ({status_streak})",
            f"Total Peminjaman     : {len(history_peminjaman)} Transaksi Selesai",
            f"Rata-rata Durasi     : {avg_hist:.1f} Hari / Buku",
            f"Bonus Habit Streak   : +{persen_efisiensi}% Efisiensi Membaca ⚡",
            f"Estimasi Selesai     : {est_hari} Hari Membaca",
            f"Rekomendasi Pinjam   : {rek_pinjam} Hari (Aman dari Denda)",
        ],
    )

    print("\n📜 TABEL RIWAYAT PEMINJAMAN LALU:")
    if not history_peminjaman:
        print("  Belum ada riwayat peminjaman masa lalu yang tercatat.")
    else:
        print("─" * LEBAR_TAMPILAN)
        for idx, item in enumerate(history_peminjaman, 1):
            denda_val = item.get('denda', 0)
            denda_str = f"Rp {denda_val:,}".replace(',', '.') if denda_val > 0 else "Rp 0"
            print(f" [{idx}] {item.get('judul_buku', '-')} ({item.get('kode_buku', '-')})")
            print(f"     📅 Pinjam : {item.get('tanggal_pinjam', '-')} | Kembali : {item.get('tanggal_kembali', '-')}")
            print(f"     ⏱️ Durasi : {item.get('durasi_aktual_hari', '-')} Hari | Status : {item.get('status', '-')} | Denda : {denda_str}")
            print("─" * LEBAR_TAMPILAN)

    input("\nTekan Enter untuk kembali ke Dashboard...")


def main():
    user_aktif, nim_aktif, jenis_akun = menu_autentikasi()

    if not user_aktif:
        clear_screen()
        print("Sistem dimatikan. Sampai jumpa!")
        return False

    semua_transaksi = muat_data(FILE_JSON)
    katalog_buku = muat_data(FILE_KATALOG)
    database_akun = muat_data(FILE_AKUN)
    ulasan_buku = muat_data(FILE_ULASAN)

    if jenis_akun == "admin":
        dashboard_admin(
            user_aktif,
            katalog_buku,
            database_akun,
            semua_transaksi,
            ulasan_buku,
        )
        return True

    while True:
        data_user = database_akun.get(nim_aktif, user_aktif)
        streak = data_user.get('streak_saat_ini', 0)
        terakhir_checkin = data_user.get('terakhir_checkin', "")
        hari_ini_str = str(datetime.date.today())

        if terakhir_checkin == hari_ini_str:
            info_streak = f"🔥 Streak: {streak} Hari"
        elif streak > 0:
            info_streak = f"⚠️ Streak: {streak} Hari [⚡ Belum Check-In Hari Ini]"
        else:
            info_streak = f"⚪ Streak: {streak} Hari [Ketik 6 utk Nyalakan]"

        cetak_header(
            "NEXUS LIBRARY KIOSK (SELF-SERVICE)",
            f"👤 {user_aktif['nama'].upper()} (NIM: {nim_aktif}) | {info_streak}",
        )

        print("\n [1] 📖 Pinjam Buku Baru        -> Cepat pilih via nomor & estimasi AI")
        print(" [2] 📚 Pinjaman Aktif Saya     -> Cek buku & batas tanggal jatuh tempo")
        print(" [3] ↩️  Kembalikan Buku         -> Pengembalian mudah & kalkulasi denda")
        print(" [4] 🔍 Katalog & Pencarian     -> Eksplorasi koleksi & filter genre")
        print(" [5] 📜 Riwayat & Estimasi Baca -> Histori peminjaman & rekomendasi durasi")
        print(" [6] 🏆 Habit Tracker & Streak  -> Check-In harian (+1 Streak) & Badge")
        print(" [0] 🚪 Logout                  -> Keluar akun dengan aman")
        print("─" * LEBAR_TAMPILAN)

        pilihan = input("Pilih menu (0-6): ").strip()

        if pilihan == '1':
            tambah_peminjaman_baru(
                semua_transaksi,
                user_aktif,
                nim_aktif,
                katalog_buku,
                database_akun,
                ulasan_buku,
            )
        elif pilihan == '2':
            lihat_buku_saya(semua_transaksi, nim_aktif, katalog_buku)
        elif pilihan == '3':
            kembalikan_buku_saya(
                semua_transaksi,
                nim_aktif,
                katalog_buku,
                user_aktif,
                database_akun,
                ulasan_buku,
            )
        elif pilihan == '4':
            cari_dan_filter_katalog(katalog_buku, ulasan_buku)
        elif pilihan == '5':
            menu_history_dan_estimasi(user_aktif, nim_aktif, database_akun)
        elif pilihan == '6':
            reading_habit_tracker(user_aktif, nim_aktif, database_akun)
        elif pilihan in ('0', '7', 'logout', 'LOGOUT'):
            notifikasi("Anda telah Logout. Sampai jumpa kembali!", "info")
            break
        else:
            print("\n⚠️ Pilihan tidak valid! Masukkan angka antara 0 sampai 6.")
            time.sleep(1)

    return True


if __name__ == "__main__":
    mesin_hidup = True
    while mesin_hidup:
        mesin_hidup = main()
