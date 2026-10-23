import os
import time
import unicodedata

LEBAR_TAMPILAN = 72


def _lebar_teks(teks):
    """Hitung lebar teks di terminal, termasuk karakter lebar dan combining."""
    lebar = 0
    lebar_karakter_sebelumnya = 0
    for karakter in teks:
        if karakter == "\ufe0f":
            if lebar_karakter_sebelumnya == 1:
                lebar += 1
                lebar_karakter_sebelumnya = 2
            continue
        if unicodedata.combining(karakter) or karakter == "\u200d":
            continue
        lebar_karakter_sebelumnya = (
            2 if unicodedata.east_asian_width(karakter) in ("F", "W") else 1
        )
        lebar += lebar_karakter_sebelumnya
    return lebar


def _bungkus_teks(teks, lebar):
    """Bungkus teks berdasarkan lebar terminal, bukan jumlah karakter."""
    hasil = []
    for baris in str(teks).splitlines() or [""]:
        kata_kata = baris.split()
        if not kata_kata:
            hasil.append("")
            continue

        baris_aktif = ""
        for kata in kata_kata:
            if not baris_aktif:
                baris_aktif = kata
            elif _lebar_teks(f"{baris_aktif} {kata}") <= lebar:
                baris_aktif = f"{baris_aktif} {kata}"
            else:
                hasil.append(baris_aktif)
                baris_aktif = kata

            if _lebar_teks(baris_aktif) > lebar:
                karakter_aktif = ""
                sisa_kata = []
                for karakter in baris_aktif:
                    if karakter_aktif and _lebar_teks(karakter_aktif + karakter) > lebar:
                        sisa_kata.append(karakter_aktif)
                        karakter_aktif = karakter
                    else:
                        karakter_aktif += karakter
                if karakter_aktif:
                    sisa_kata.append(karakter_aktif)
                hasil.extend(sisa_kata[:-1])
                baris_aktif = sisa_kata[-1] if sisa_kata else ""

        if baris_aktif:
            hasil.append(baris_aktif)
    return hasil or [""]


def _cetak_baris_kotak(teks, lebar, rata="kiri"):
    lebar_dalam = lebar - 4
    lebar_teks = _lebar_teks(teks)
    ruang = max(0, lebar_dalam - lebar_teks)
    if rata == "tengah":
        kiri = ruang // 2
        kanan = ruang - kiri
        isi = " " * kiri + teks + " " * kanan
    else:
        isi = teks + " " * ruang
    print(f"│ {isi} │")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def cetak_header(judul, subjudul=None, lebar=60):
    """
    Mencetak header konsisten dengan pembungkusan teks yang rapi.
    """
    clear_screen()
    lebar = max(lebar, LEBAR_TAMPILAN)
    print("┌" + "─" * (lebar - 2) + "┐")
    for baris in _bungkus_teks(judul, lebar - 4):
        _cetak_baris_kotak(baris, lebar, "tengah")
    if subjudul:
        for baris in _bungkus_teks(subjudul, lebar - 4):
            _cetak_baris_kotak(baris, lebar, "tengah")
    print("└" + "─" * (lebar - 2) + "┘")

def cetak_kartu(judul_kartu, daftar_item, lebar=60):
    """
    Mencetak kartu dengan lebar isi tetap dan teks panjang dibungkus otomatis.
    """
    lebar = max(lebar, LEBAR_TAMPILAN)
    lebar_dalam = lebar - 4
    print("┌" + "─" * (lebar - 2) + "┐")
    for baris in _bungkus_teks(f"📌 {judul_kartu}", lebar_dalam):
        _cetak_baris_kotak(baris, lebar)
    print("├" + "─" * (lebar - 2) + "┤")
    for item in daftar_item:
        baris_bungkus = _bungkus_teks(item, lebar_dalam - 2)
        for indeks, baris in enumerate(baris_bungkus):
            awalan = "  " if indeks else "• "
            _cetak_baris_kotak(f"{awalan}{baris}", lebar)
    print("└" + "─" * (lebar - 2) + "┘")

def notifikasi(pesan, tipe="sukses", durasi=1.5):
    """
    Menampilkan notifikasi pop-up berwaktu dengan ikon visual yang jelas.
    """
    clear_screen()
    lebar = LEBAR_TAMPILAN
    judul_tipe = {
        "sukses": "✅  BERHASIL  ✅",
        "gagal": "❌  PERINGATAN / GAGAL  ❌",
        "info": "ℹ️  INFORMASI  ℹ️",
    }.get(tipe, "ℹ️  INFORMASI  ℹ️")
    print("\n┌" + "─" * (lebar - 2) + "┐")
    _cetak_baris_kotak(judul_tipe, lebar, "tengah")
    print("├" + "─" * (lebar - 2) + "┤")
    for baris in _bungkus_teks(pesan, lebar - 4):
        _cetak_baris_kotak(baris, lebar, "tengah")
    print("└" + "─" * (lebar - 2) + "┘\n")
    time.sleep(durasi)
    clear_screen()

def input_angka_valid(pesan_input, nilai_default=None):
    """
    Input angka dengan validasi aman dan dukungan Smart Default (tekan Enter untuk default).
    """
    while True:
        teks = input(pesan_input).strip()
        if teks == "" and nilai_default is not None:
            return nilai_default
        try:
            angka = int(teks)
            if angka < 0:
                print("⚠️ Harap masukkan angka 0 atau lebih besar.\n")
                continue
            return angka
        except ValueError:
            print("⚠️ Input harus berupa angka valid!\n")

def input_teks_valid(pesan_input, boleh_kosong=False, nilai_default=""):
    """
    Input teks dengan validasi kebersihan data.
    """
    while True:
        teks = input(pesan_input).strip()
        if len(teks) == 0:
            if boleh_kosong:
                return nilai_default
            print("⚠️ Input tidak boleh kosong!\n")
        else:
            return teks

def konfirmasi_ya_tidak(pesan_input, default_ya=True):
    """
    Prompt konfirmasi interaktif ramah pengguna (HCD).
    Tekan Enter langsung memilih opsi default.
    """
    hint = "[Y/n]" if default_ya else "[y/N]"
    pilihan = input(f"{pesan_input} {hint}: ").strip().lower()
    if pilihan == "":
        return default_ya
    return pilihan in ("y", "ya", "yes", "1")