from database import FILE_KATALOG, simpan_data
from admin.ui import cetak_menu_admin
from ui import (
    cetak_header,
    cetak_kartu,
    input_teks_valid,
    konfirmasi_ya_tidak,
)


def _tampilkan_katalog(katalog):
    cetak_header("MANAJEMEN KATALOG", f"Total koleksi: {len(katalog)}")
    if not katalog:
        print("\nKatalog masih kosong.")
        return

    daftar_buku = []
    for kode, buku in katalog.items():
        kategori = ", ".join(buku.get("kategori", ["Umum"]))
        lokasi = " - ".join(buku.get("lokasi", ["Lantai 1", "Rak Umum"]))
        daftar_buku.append(
            (
                kode,
                buku.get("judul", "Tanpa judul"),
                kategori,
                buku.get("stok", 0),
                lokasi,
            )
        )
    for kode, judul, kategori, stok, lokasi in daftar_buku:
        cetak_kartu(
            f"{judul} ({kode})",
            [f"🏷️ Kategori: {kategori}", f"📦 Stok: {stok}", f"📍 Lokasi: {lokasi}"],
        )


def _input_data_buku(buku_lama=None):
    buku_lama = buku_lama or {}
    judul = input_teks_valid(
        f"Judul [{buku_lama.get('judul', '-')}] (Enter untuk pakai nilai lama): ",
        boleh_kosong=True,
        nilai_default=buku_lama.get("judul", ""),
    )
    while not judul:
        judul = input_teks_valid("Judul buku: ")

    stok_default = buku_lama.get("stok", 0)
    while True:
        teks_stok = input(
            f"Stok [{stok_default}] (Enter untuk pakai nilai lama): "
        ).strip()
        if not teks_stok:
            stok = stok_default
            break
        if teks_stok.isdigit():
            stok = int(teks_stok)
            break
        print("⚠️ Stok harus berupa bilangan bulat 0 atau lebih.")

    kategori_lama = ", ".join(buku_lama.get("kategori", []))
    kategori_input = input(
        f"Kategori, pisahkan dengan koma [{kategori_lama}]: "
    ).strip()
    kategori = (
        [item.strip() for item in kategori_input.split(",") if item.strip()]
        if kategori_input
        else buku_lama.get("kategori", ["Umum"])
    )

    lokasi_lama = buku_lama.get("lokasi", ["Lantai 1", "Rak Umum"])
    lokasi_lantai = input(f"Lantai [{lokasi_lama[0]}]: ").strip() or lokasi_lama[0]
    lokasi_rak = input(f"Rak [{lokasi_lama[1]}]: ").strip() or lokasi_lama[1]
    return {
        "judul": judul,
        "stok": stok,
        "kategori": kategori,
        "lokasi": [lokasi_lantai, lokasi_rak],
    }


def kelola_katalog(katalog, semua_transaksi):
    while True:
        _tampilkan_katalog(katalog)
        pilihan = cetak_menu_admin(
            "AKSI KATALOG",
            [
                ("1", "Tambah buku", "Tambahkan koleksi baru"),
                ("2", "Edit buku", "Perbarui data dan stok"),
                ("3", "Hapus buku", "Hapus koleksi yang tidak dipinjam"),
                ("0", "Kembali", "Kembali ke dashboard admin"),
            ],
            "Pilih aksi katalog",
        )

        if pilihan == "0":
            return
        if pilihan == "1":
            kode = input_teks_valid("Kode buku baru: ").upper()
            if kode in katalog:
                print("⚠️ Kode buku sudah digunakan.")
                continue
            katalog[kode] = _input_data_buku()
            simpan_data(katalog, FILE_KATALOG)
            print("✅ Buku berhasil ditambahkan.")
        elif pilihan in ("2", "3"):
            kode = input_teks_valid("Kode buku: ").upper()
            if kode not in katalog:
                print("⚠️ Kode buku tidak ditemukan.")
                continue

            if pilihan == "2":
                katalog[kode].update(_input_data_buku(katalog[kode]))
                simpan_data(katalog, FILE_KATALOG)
                print("✅ Data buku berhasil diperbarui.")
                continue

            sedang_dipinjam = any(
                transaksi.get("transaksi", {}).get("kode_buku") == kode
                for transaksi in semua_transaksi
            )
            if sedang_dipinjam:
                print("⚠️ Buku tidak dapat dihapus karena masih dipinjam.")
                continue
            if konfirmasi_ya_tidak(f"Hapus buku {kode} dari katalog?", default_ya=False):
                del katalog[kode]
                simpan_data(katalog, FILE_KATALOG)
                print("✅ Buku berhasil dihapus.")
        else:
            print("⚠️ Pilihan tidak valid.")
