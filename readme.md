# 📚 Nexus Library & Habit Tracker (Kiosk Edition)

## 📖 Deskripsi Proyek
Nexus Library Kiosk adalah sistem manajemen perpustakaan berbasis *Command Line Interface (CLI)* yang beroperasi menggunakan model *Self-Service* (Kiosk Mandiri). Dikembangkan dengan pendekatan **Human-Centered Design (HCD)** agar antarmuka terminal terasa intuitif, minim beban kognitif (*low cognitive load*), dan ramah pengguna layaknya mesin Kiosk modern.

Aplikasi ini juga dirancang sebagai media pembelajaran komprehensif **Fundamental Pemrograman Python**, mengintegrasikan konsep **Tuple**, **List**, **Dictionary**, *File Handling (JSON)*, *Modular Architecture*, serta pemodelan estimasi analitik (*Datetime & Mathematical Modeling*).

---

## 🎨 Pendekatan Human-Centered Design (HCD)
Untuk meningkatkan pengalaman pengguna (*User Experience*), sistem ini menerapkan prinsip-prinsip HCD:
1. **Nomor Pilihan Terindeks (No Manual Code Typing)**:
   Pengguna tidak perlu mengetik kode buku (misal `PY-01`), melainkan cukup memilih **Nomor Buku (1, 2, 3...)** yang terpampang jelas.
2. **Smart Default Input (Zero-Friction UX)**:
   Sistem secara otomatis menghitung rekomendasi durasi pinjam ideal. Pengguna cukup menekan **[Enter]** untuk langsung menyetujui tanpa perlu mengetik ulang angka.
3. **Menu Eksplorasi Interaktif (No Empty Blank Screen)**:
   Menu pencarian dan filter dilengkapi panduan visual, tips kata kunci, dan pilihan filter kategori yang rapi.
4. **Hierarki Visual & Card Layout**:
   Menggunakan bingkai kotak (*Box Card Layout*) yang rapi untuk memisahkan informasi penting (Status Streak, Rekomendasi Durasi, Riwayat Transaksi).
5. **Pencegahan Kesalahan (*Error Prevention & Confirmation*)**:
   Menyediakan kartu ringkasan transaksi sebelum eksekusi dan tombol pembatalan (`0`) yang konsisten di semua alur.

---

## ✨ Penerapan Struktur Data Python (Tuple & List)

### 🧩 1. Penerapan Tuple (Immutable Sequence)
- **Konfigurasi Aturan Perpustakaan**: `KONFIGURASI_PERPUSTAKAAN = (12, 2000, 3)` merepresentasikan `(MAKS_HARI_PINJAM, TARIF_DENDA_PER_HARI, MAKS_BUKU_SEKALIGUS)` yang diekstrak menggunakan *Tuple Unpacking*.
- **Master Data Kecepatan Habit Membaca**: `FAKTOR_KECEPATAN_STREAK` menyimpan tuple bertingkat untuk menghitung efisiensi kecepatan membaca berdasarkan streak harian.
- **Master Data Badge Literasi**: `BADGE_STREAK` menyimpan pasangan `(target_hari, nama_badge)` sebagai referensi tetap.
- **Lokasi Fisik Rak Buku**: Tiap buku memiliki koordinat lokasi tetap `(Lantai, Rak)` yang di-unpack saat ditampilkan.
- **Multi-Value Return**:
  - `hitung_denda_dan_status()` -> tuple `(hari_terlambat, total_denda, status_pesan)`.
  - `hitung_estimasi_peminjaman()` -> tuple `(estimasi_hari, rekomendasi_pinjam, rata_rata_historis, persen_efisiensi, label_streak)`.

### 📋 2. Penerapan List (Mutable Sequence)
- **History Peminjaman (`history_peminjaman`)**: List dictionary catatan lengkap transaksi peminjaman masa lalu (durasi aktual, tanggal, status denda).
- **Kategori & Tag Buku**: `DAFTAR_KATEGORI` dan tag per buku `["Pemrograman", "Python", "Dasar"]`.
- **Pencarian & Filter Cerdas**: Pencarian judul dan genre menggunakan *List Comprehension*.
- **Riwayat Membaca (`riwayat_baca`)**: Menyimpan log buku yang telah selesai dibaca menggunakan method `.append()`.
- **Antrean Transaksi Aktif**: Manipulasi list transaksi aktif dengan `.append()`, `.remove()`, dan `len()`.

---

## 🚀 Menu Utama Dashboard Pengunjung
```text
┌────────────────────────────────────────────────────────────┐
│            NEXUS LIBRARY KIOSK (SELF-SERVICE)              │
│      👤 BUDI SANTOSO (NIM: 1001) | 🔥 Streak: 4 Hari       │
└────────────────────────────────────────────────────────────┘
 [1] 📖 Pinjam Buku Baru        -> Cepat pilih via nomor & estimasi AI
 [2] 📚 Pinjaman Aktif Saya     -> Cek buku & batas tanggal jatuh tempo
 [3] ↩️  Kembalikan Buku         -> Pengembalian mudah & kalkulasi denda
 [4] 🔍 Katalog & Pencarian     -> Eksplorasi koleksi & filter genre
 [5] 📜 Riwayat & Estimasi Baca -> Histori peminjaman & rekomendasi durasi
 [6] 🏆 Habit Tracker & Streak  -> Check-in harian & koleksi badge
 [0] 🚪 Logout                  -> Keluar akun dengan aman
```

---

## 🚀 Cara Menjalankan Program
1. Buka Terminal / CMD di direktori proyek:
   ```bash
   cd c:\git\PytonFundamentalPrograming
   ```
2. Jalankan file utama:
   ```bash
   python main.py
   ```