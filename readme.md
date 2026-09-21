# 📚 Nexus Library & Habit Tracker (Kiosk Edition)

## 📖 Deskripsi Proyek
Nexus Library Kiosk adalah sistem manajemen perpustakaan berbasis *Command Line Interface (CLI)* yang beroperasi menggunakan model *Self-Service* (Kiosk). Layaknya mesin ATM, pengunjung dapat mendaftarkan akun, masuk (login) ke *dashboard* pribadi mereka, meminjam buku, dan mengembalikan buku secara mandiri.

Aplikasi ini dikembangkan sebagai proyek tingkat lanjut untuk **Fundamental Pemrograman Python**, mengintegrasikan berbagai konsep inti seperti *File Handling*, *State Management*, *Authentication*, dan Penghitungan Waktu Dinamis (*Datetime*).

---

## ✨ Fitur Utama
1. **Sistem Autentikasi (Login & Register)** 🔐
   Pengunjung harus membuat akun menggunakan NIM dan Password. Sistem akan mengingat sesi (*Session*) pengunjung hingga mereka menekan tombol *Logout*.
2. **Dashboard Privasi Pribadi (Self-Service)** 👤
   Setiap pengguna hanya dapat melihat dan memanajemen buku yang mereka pinjam sendiri. Data tidak bercampur dengan pengunjung lain.
3. **Penyimpanan Permanen (Auto-Save JSON)** 💾
   Seluruh data akun pengguna dan riwayat peminjaman disimpan secara otomatis ke dalam *database* JSON. Data tidak akan hilang meskipun program ditutup atau komputer dimatikan.
4. **Sistem Jatuh Tempo & Denda Otomatis (Datetime)** 🗓️
   Menggunakan modul `datetime` bawaan Python, program secara otomatis menghitung *Tanggal Jatuh Tempo*. Jika buku dikembalikan melewati batas waktu, sistem akan mendeteksi selisih hari dan secara otomatis menghitung biaya denda (Rp 2.000 / hari).
5. **Transisi UI Interaktif (Clear Screen & Delay)** 🖥️
   Tampilan CLI terminal dibuat bersih dan dinamis layaknya aplikasi modern menggunakan fitur *Clear Screen* dan pop-up *Notifikasi* berwaktu.

---

## 🛠️ Teknologi & Modul
Program ini dibangun menggunakan **100% Python Native (Bawaan)**, sehingga tidak membutuhkan instalasi *library* eksternal (tidak perlu `pip install`). Modul yang digunakan:
- `json` : Untuk membaca dan menulis database lokal.
- `os` : Untuk mendeteksi keberadaan file database dan membersihkan layar terminal.
- `datetime` : Untuk mendeteksi waktu hari ini dan melakukan perhitungan *Time Delta* (selisih hari).
- `time` : Untuk memberikan efek jeda animasi/transisi saat notifikasi muncul.

---

## 🚀 Cara Menjalankan Program
1. Pastikan **Python 3.x** sudah terinstal di komputer Anda.
2. Buka Terminal atau *Command Prompt* (CMD).
3. Arahkan *path* ke dalam folder proyek ini.
4. Jalankan perintah berikut:
   ```bash
   python nama_file_anda.py