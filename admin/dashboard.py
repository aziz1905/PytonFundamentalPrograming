from admin.catalog import kelola_katalog
from admin.reports import (
    tampilkan_peminjaman,
    tampilkan_pengunjung,
    tampilkan_ringkasan,
)
from admin.reviews import moderasi_ulasan
from admin.ui import cetak_menu_admin
from ui import cetak_header, cetak_kartu, notifikasi


def dashboard_admin(admin_aktif, katalog, database_akun, semua_transaksi, ulasan_buku):
    while True:
        cetak_header(
            "DASHBOARD ADMINISTRATOR",
            f"Panel kontrol perpustakaan | Admin: {admin_aktif['username']}",
        )
        total_eksemplar = sum(buku.get("stok", 0) for buku in katalog.values())
        total_ulasan = sum(len(daftar) for daftar in ulasan_buku.values())
        cetak_kartu(
            "PANTAUAN SINGKAT",
            [
                f"📚 {len(katalog)} judul | 📦 {total_eksemplar} eksemplar",
                f"👥 {len(database_akun)} pengunjung | 🔄 {len(semua_transaksi)} peminjaman aktif",
                f"⭐ {total_ulasan} ulasan pembaca",
            ],
        )
        pilihan = cetak_menu_admin(
            "MENU UTAMA",
            [
                ("1", "Ringkasan", "Statistik koleksi dan aktivitas"),
                ("2", "Katalog buku", "Tambah, edit, dan hapus buku"),
                ("3", "Pengunjung", "Lihat akun dan aktivitas membaca"),
                ("4", "Peminjaman", "Pantau transaksi aktif dan selesai"),
                ("5", "Moderasi ulasan", "Tinjau dan hapus ulasan"),
                ("0", "Logout", "Keluar dari dashboard administrator"),
            ],
            "Pilih menu admin (0-5)",
        )

        if pilihan == "1":
            tampilkan_ringkasan(katalog, database_akun, semua_transaksi, ulasan_buku)
            input("\nTekan Enter untuk kembali ke dashboard...")
        elif pilihan == "2":
            kelola_katalog(katalog, semua_transaksi)
        elif pilihan == "3":
            tampilkan_pengunjung(database_akun)
            input("\nTekan Enter untuk kembali ke dashboard...")
        elif pilihan == "4":
            tampilkan_peminjaman(semua_transaksi, database_akun)
            input("\nTekan Enter untuk kembali ke dashboard...")
        elif pilihan == "5":
            moderasi_ulasan(ulasan_buku, katalog)
        elif pilihan == "0":
            notifikasi("Anda telah logout dari dashboard admin.", "info")
            return
        else:
            print("⚠️ Pilihan tidak valid.")
