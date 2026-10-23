from ui import cetak_kartu
from ulasan import format_ulasan_buku


def dapatkan_list_buku(katalog, filter_kategori="Semua", filter_keyword=""):
    """
    Mengubah dictionary katalog menjadi List of Tuples yang berurutan
    sehingga mudah dipilih dengan nomor urut (Prinsip HCD).
    """
    daftar_terfilter = []
    for kode, info in katalog.items():
        kategori_list = info.get('kategori', ["Umum"])

        # Filter Kategori
        if filter_kategori != "Semua" and filter_kategori not in kategori_list:
            continue

        # Filter Keyword (Pencarian)
        if filter_keyword:
            kw = filter_keyword.lower()
            judul_match = kw in info['judul'].lower()
            kategori_match = any(kw in k.lower() for k in kategori_list)
            kode_match = kw in kode.lower()
            if not (judul_match or kategori_match or kode_match):
                continue

        daftar_terfilter.append((kode, info))

    return daftar_terfilter


def tampilkan_tabel_katalog(daftar_buku, ulasan_buku):
    """
    Menampilkan daftar buku dalam format visual kartu yang rapi.
    """
    if not daftar_buku:
        print("\n  ⚠️ Tidak ada buku yang sesuai dengan kriteria yang dipilih.")
        return

    print()
    for idx, (kode, info) in enumerate(daftar_buku, 1):
        stok = info.get('stok', 0)
        status_stok = f"✅ Tersedia: {stok} eks" if stok > 0 else "❌ STOK HABIS"

        # Tuple Unpacking lokasi buku
        lokasi = tuple(info.get('lokasi', ['Lantai 1', 'Rak Umum']))
        lantai, rak = lokasi

        kategori_str = ", ".join(info.get('kategori', ["Umum"]))
        detail_buku = [
            f"🏷️ Kategori: {kategori_str}",
            f"📍 Lokasi: {lantai} - {rak}",
            f"📦 Status: {status_stok}",
            *format_ulasan_buku(kode, ulasan_buku),
        ]
        cetak_kartu(f"{idx}. {info['judul']} ({kode})", detail_buku)
