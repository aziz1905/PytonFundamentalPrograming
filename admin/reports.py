from ui import cetak_header, cetak_kartu


def tampilkan_ringkasan(katalog, database_akun, semua_transaksi, ulasan_buku):
    total_buku = sum(buku.get("stok", 0) for buku in katalog.values())
    total_ulasan = sum(len(ulasan) for ulasan in ulasan_buku.values())
    cetak_header("RINGKASAN PERPUSTAKAAN", "Statistik sistem saat ini")
    cetak_kartu(
        "IKHTISAR SISTEM",
        [
            f"📚 Judul buku: {len(katalog)}",
            f"📦 Total eksemplar: {total_buku}",
            f"👥 Akun pengunjung: {len(database_akun)}",
            f"🔄 Peminjaman aktif: {len(semua_transaksi)}",
            f"⭐ Ulasan pembaca: {total_ulasan}",
        ],
    )


def tampilkan_pengunjung(database_akun):
    cetak_header("DAFTAR PENGUNJUNG", f"Total akun: {len(database_akun)}")
    if not database_akun:
        cetak_kartu("BELUM ADA DATA", ["Belum ada akun pengunjung."])
    for nim, akun in database_akun.items():
        cetak_kartu(
            akun.get("nama", "Tanpa nama"),
            [
                f"🪪 ID pengunjung: {nim}",
                f"🔥 Reading streak: {akun.get('streak_saat_ini', 0)} hari",
                f"📖 Riwayat selesai: {len(akun.get('history_peminjaman', []))} buku",
            ],
        )


def tampilkan_peminjaman(semua_transaksi, database_akun):
    riwayat_selesai = [
        (nim, akun, riwayat)
        for nim, akun in database_akun.items()
        for riwayat in akun.get("history_peminjaman", [])
    ]
    cetak_header(
        "LAPORAN PEMINJAMAN",
        f"{len(semua_transaksi)} aktif | {len(riwayat_selesai)} selesai",
    )

    daftar_aktif = []
    if not semua_transaksi:
        daftar_aktif.append("Tidak ada peminjaman aktif.")
    for data in semua_transaksi:
        profil = data.get("profil", {})
        transaksi = data.get("transaksi", {})
        daftar_aktif.extend(
            [
                f"📘 {transaksi.get('judul_buku', '-')} ({transaksi.get('kode_buku', '-')})",
                f"👤 Peminjam: {profil.get('nama', '-')} ({profil.get('nim', '-')})",
                f"📅 Pinjam: {transaksi.get('tanggal_pinjam', '-')} | Jatuh tempo: {transaksi.get('jatuh_tempo', '-')}",
            ]
        )
    cetak_kartu("PEMINJAMAN AKTIF", daftar_aktif)

    daftar_selesai = []
    if not riwayat_selesai:
        daftar_selesai.append("Belum ada transaksi yang selesai.")
    for nim, akun, transaksi in riwayat_selesai:
        daftar_selesai.extend(
            [
                f"📗 {transaksi.get('judul_buku', '-')} ({transaksi.get('kode_buku', '-')})",
                f"👤 Peminjam: {akun.get('nama', '-')} ({nim})",
                f"✅ Kembali: {transaksi.get('tanggal_kembali', '-')} | Status: {transaksi.get('status', '-')}",
            ]
        )
    cetak_kartu("RIWAYAT SELESAI", daftar_selesai)
