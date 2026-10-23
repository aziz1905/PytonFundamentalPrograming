from database import FILE_ULASAN, simpan_data
from ui import (
    cetak_header,
    cetak_kartu,
    konfirmasi_ya_tidak,
)


def moderasi_ulasan(ulasan_buku):
    while True:
        total_ulasan = sum(len(daftar) for daftar in ulasan_buku.values())
        cetak_header("MODERASI ULASAN", f"Total ulasan: {total_ulasan}")
        kode_buku = input("Kode buku untuk melihat ulasan (0 untuk kembali): ").strip().upper()
        if kode_buku == "0":
            return

        daftar_ulasan = ulasan_buku.get(kode_buku, [])
        if not daftar_ulasan:
            print("⚠️ Tidak ada ulasan untuk kode buku tersebut.")
            continue

        kartu_ulasan = []
        for indeks, ulasan in enumerate(daftar_ulasan, start=1):
            kartu_ulasan.append(
                (
                    indeks,
                    ulasan.get("nama", "Pembaca"),
                    ulasan.get("rating", "-"),
                    ulasan.get("deskripsi", ""),
                )
            )
        for indeks, nama, rating, deskripsi in kartu_ulasan:
            cetak_kartu(
                f"Ulasan #{indeks} — {nama}",
                [f"⭐ Rating: {rating}/5", f"💬 {deskripsi}"],
            )

        cetak_kartu(
            "AKSI MODERASI",
            [
                "Masukkan nomor ulasan untuk menghapusnya.",
                "Tekan Enter untuk melihat kode buku lain.",
            ],
        )
        pilihan = input("\nNomor ulasan atau Enter: ").strip()
        if not pilihan:
            continue
        if not pilihan.isdigit() or not 1 <= int(pilihan) <= len(daftar_ulasan):
            print("⚠️ Nomor ulasan tidak valid.")
            continue

        indeks = int(pilihan) - 1
        nama = daftar_ulasan[indeks].get("nama", "Pembaca")
        if konfirmasi_ya_tidak(
            f"Hapus ulasan dari {nama} untuk {kode_buku}?",
            default_ya=False,
        ):
            daftar_ulasan.pop(indeks)
            if not daftar_ulasan:
                del ulasan_buku[kode_buku]
            simpan_data(ulasan_buku, FILE_ULASAN)
            print("✅ Ulasan berhasil dihapus.")
