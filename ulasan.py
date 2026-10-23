from database import FILE_ULASAN, simpan_data
from ui import konfirmasi_ya_tidak, input_angka_valid, input_teks_valid

BATAS_PANJANG_ULASAN = 500


def simpan_ulasan_buku(ulasan_buku, kode_buku, nim, nama, rating, deskripsi):
    """Simpan ulasan baru atau perbarui ulasan pengguna untuk buku yang sama."""
    daftar_ulasan = ulasan_buku.setdefault(kode_buku, [])
    ulasan_baru = {
        "nim": nim,
        "nama": nama,
        "rating": rating,
        "deskripsi": deskripsi,
    }

    for indeks, ulasan in enumerate(daftar_ulasan):
        if ulasan.get("nim") == nim:
            daftar_ulasan[indeks] = ulasan_baru
            break
    else:
        daftar_ulasan.append(ulasan_baru)

    simpan_data(ulasan_buku, FILE_ULASAN)


def minta_ulasan_buku(ulasan_buku, kode_buku, nim, nama, judul):
    """Minta rating dan deskripsi setelah pengguna mengembalikan buku."""
    if not konfirmasi_ya_tidak(
        f"\nIngin memberikan ulasan untuk '{judul}'?",
        default_ya=False,
    ):
        return

    while True:
        rating = input_angka_valid("Berikan rating (1-5): ")
        if 1 <= rating <= 5:
            break
        print("⚠️ Rating harus antara 1 sampai 5.\n")

    while True:
        deskripsi = input_teks_valid("Deskripsi/pengalaman membaca: ")
        if len(deskripsi) <= BATAS_PANJANG_ULASAN:
            break
        print(f"⚠️ Deskripsi maksimal {BATAS_PANJANG_ULASAN} karakter.\n")

    simpan_ulasan_buku(
        ulasan_buku,
        kode_buku,
        nim,
        nama,
        rating,
        deskripsi,
    )
    print("✅ Ulasan Anda berhasil disimpan.")


def format_ulasan_buku(kode_buku, ulasan_buku):
    """Siapkan rating dan komentar pembaca dalam bentuk teks untuk UI."""
    daftar_ulasan = ulasan_buku.get(kode_buku, [])
    if not daftar_ulasan:
        return ["⭐ Ulasan: Belum ada ulasan"]

    rata_rata = sum(item.get("rating", 0) for item in daftar_ulasan) / len(daftar_ulasan)
    baris_ulasan = [
        f"⭐ Rating: {rata_rata:.1f}/5 ({len(daftar_ulasan)} ulasan)"
    ]
    for item in daftar_ulasan:
        baris_ulasan.append(
            f"💬 {item.get('nama', 'Pembaca')} "
            f"({item.get('rating', 0)}/5): {item.get('deskripsi', '')}"
        )
    return baris_ulasan
