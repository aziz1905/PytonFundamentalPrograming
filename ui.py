import os
import time

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def notifikasi(pesan, tipe="sukses"):
    clear_screen()
    print("\n" + "="*55)
    if tipe == "sukses":
        print("                  ✅ BERHASIL ✅                 ")
    elif tipe == "gagal":
        print("                   ❌ GAGAL ❌                   ")
    elif tipe == "info":
        print("                 ℹ️ INFORMASI ℹ️                 ")
    print("="*55)
    print(pesan.center(55))
    print("="*55 + "\n")
    time.sleep(1.5)
    clear_screen()

def input_angka_valid(pesan_input):
    while True:
        try:
            angka = int(input(pesan_input))
            if angka < 0:
                print("⚠️ Masukkan angka 0 atau lebih positif.\n")
                continue
            return angka
        except ValueError:
            print("⚠️ Input tidak valid! Harap masukkan angka.\n")

def input_teks_valid(pesan_input):
    while True:
        teks = input(pesan_input).strip() 
        if len(teks) == 0:
            print("⚠️ Input tidak boleh dikosongkan!\n")
        else:
            return teks