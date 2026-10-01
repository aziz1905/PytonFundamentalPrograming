import os
import time

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def cetak_header(judul, subjudul=None, lebar=60):
    """
    Mencetak header aplikasi yang rapi, modern, dan konsisten (HCD).
    """
    clear_screen()
    print("┌" + "─" * (lebar - 2) + "┐")
    print(f"│ {judul.center(lebar - 4)} │")
    if subjudul:
        print(f"│ {subjudul.center(lebar - 4)} │")
    print("└" + "─" * (lebar - 2) + "┘")

def cetak_kartu(judul_kartu, daftar_item, lebar=60):
    """
    Mencetak kartu informasi (box layout) yang terstruktur dan mudah dibaca sekilas.
    """
    print("┌" + "─" * (lebar - 2) + "┐")
    print(f"│  📌 {judul_kartu.ljust(lebar - 8)} │")
    print("├" + "─" * (lebar - 2) + "┤")
    for item in daftar_item:
        print(f"│  • {item.ljust(lebar - 8)} │")
    print("└" + "─" * (lebar - 2) + "┘")

def notifikasi(pesan, tipe="sukses", durasi=1.5):
    """
    Menampilkan notifikasi pop-up berwaktu dengan ikon visual yang jelas.
    """
    clear_screen()
    lebar = 60
    print("\n┌" + "─" * (lebar - 2) + "┐")
    if tipe == "sukses":
        print(f"│ {'✅  BERHASIL  ✅'.center(lebar - 6)} │")
    elif tipe == "gagal":
        print(f"│ {'❌  PERINGATAN / GAGAL  ❌'.center(lebar - 6)} │")
    elif tipe == "info":
        print(f"│ {'ℹ️  INFORMASI  ℹ️'.center(lebar - 6)} │")
    print("├" + "─" * (lebar - 2) + "┤")
    print(f"│ {pesan.center(lebar - 4)} │")
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