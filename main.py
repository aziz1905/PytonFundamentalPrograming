import datetime
import time

# --- PUSAT KENDALI: IMPOR MODUL SISTEM ---
from database import (
    muat_data, 
    simpan_data, 
    FILE_JSON, 
    FILE_AKUN, 
    FILE_KATALOG,
    KONFIGURASI_PERPUSTAKAAN,
    BADGE_STREAK,
    FAKTOR_KECEPATAN_STREAK,
    DAFTAR_KATEGORI
)
from ui import (
    clear_screen, 
    cetak_header, 
    cetak_kartu, 
    notifikasi, 
    input_angka_valid, 
    input_teks_valid,
    konfirmasi_ya_tidak
)
from auth import menu_autentikasi

# ==============================================================================
# CONTOH PENGGUNAAN TUPLE UNPACKING:
# Mengurai tuple KONFIGURASI_PERPUSTAKAAN menjadi variabel konstan yang aman
# ==============================================================================
MAKS_HARI_PINJAM, TARIF_DENDA_PER_HARI, MAKS_BUKU_SEKALIGUS = KONFIGURASI_PERPUSTAKAAN


def hitung_denda_dan_status(jatuh_tempo_str, tanggal_kembali):
    """
    CONTOH PENGGUNAAN TUPLE RETURN:
    Mengembalikan Tuple 3-elemen: (hari_terlambat, nominal_denda, status_pesan)
    """
    try:
        jatuh_tempo = datetime.datetime.strptime(jatuh_tempo_str, "%Y-%m-%d").date()
    except Exception:
        jatuh_tempo = tanggal_kembali

    if tanggal_kembali > jatuh_tempo:
        telat = (tanggal_kembali - jatuh_tempo).days
        denda = telat * TARIF_DENDA_PER_HARI
        return (telat, denda, f"TERLAMBAT {telat} HARI")
    
    return (0, 0, "TEPAT WAKTU")


def hitung_estimasi_peminjaman(history_peminjaman, streak_hari):
    """
    FITUR ESTIMASI CERDAS (LIST & TUPLE):
    Menghitung estimasi selesai membaca dan rekomendasi durasi pinjam.
    Return berupa TUPLE:
    (estimasi_hari, rekomendasi_pinjam, rata_rata_historis, persen_efisiensi, label_streak)
    """
    # 1. Ekstraksi durasi dari List History
    durasi_list = [
        item['durasi_aktual_hari'] 
        for item in history_peminjaman 
        if item.get('durasi_aktual_hari', 0) > 0
    ]
    
    # Rata-rata dari List durasi
    rata_rata_historis = sum(durasi_list) / len(durasi_list) if durasi_list else 7.0

    # 2. Faktor Kecepatan dari Tuple of Tuples
    faktor_pengali = 1.0
    persen_efisiensi = 0
    label_streak = "Standar (Belum Ada Streak)"
    
    for min_streak, faktor, label, persen in FAKTOR_KECEPATAN_STREAK:
        if streak_hari >= min_streak:
            faktor_pengali = faktor
            persen_efisiensi = persen
            label_streak = label
            break

    # 3. Kalkulasi & Rekomendasi
    estimasi_hari = max(1, round(rata_rata_historis * faktor_pengali))
    rekomendasi_pinjam = min(MAKS_HARI_PINJAM, estimasi_hari + 1)

    return (estimasi_hari, rekomendasi_pinjam, rata_rata_historis, persen_efisiensi, label_streak)


def dapatkan_list_buku(katalog, filter_kategori="Semua", filter_keyword=""):
    """
    Mengubah dictionary katalog menjadi List of Tuples yang berurutan
    sehingga mudah dipilih dengan nomor urut (Prinsip HCD: meminimalisir pengetikan manual).
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


def tampilkan_tabel_katalog(daftar_buku):
    """
    Menampilkan daftar buku dalam format visual yang rapi dan mudah dibaca (HCD).
    """
    if not daftar_buku:
        print("\n  ⚠️ Tidak ada buku yang sesuai dengan kriteria yang dipilih.")
        return

    print("\n" + "─" * 60)
    for idx, (kode, info) in enumerate(daftar_buku, 1):
        stok = info.get('stok', 0)
        status_stok = f"✅ Tersedia: {stok} eks" if stok > 0 else "❌ STOK HABIS"
        
        # Tuple Unpacking lokasi buku
        lokasi = tuple(info.get('lokasi', ['Lantai 1', 'Rak Umum']))
        lantai, rak = lokasi
        
        kategori_str = ", ".join(info.get('kategori', []))
        
        print(f" [{idx}] {info['judul']} ({kode})")
        print(f"     🏷️ Kategori : [{kategori_str}]")
        print(f"     📍 Lokasi   : {lantai} - {rak}")
        print(f"     📦 Status   : {status_stok}")
        print("─" * 60)


def tambah_peminjaman_baru(semua_transaksi, user_aktif, nim_aktif, katalog, database_akun):
    """
    Alur peminjaman buku yang telah dioptimalkan untuk Human-Centered Design (HCD):
    - Cukup pilih nomor urut buku (tidak perlu mengetik kode manual).
    - Dilengkapi Smart Default untuk durasi pinjam (cukup tekan Enter).
    """
    cetak_header("PEMINJAMAN BUKU BARU", f"Pengunjung: {user_aktif['nama'].upper()}")
    
    # 1. Cek Kuota Maksimal Peminjaman
    buku_aktif_user = [t for t in semua_transaksi if t['profil']['nim'] == nim_aktif]
    if len(buku_aktif_user) >= MAKS_BUKU_SEKALIGUS:
        cetak_kartu(
            "Batas Maksimal Peminjaman Tercapai",
            [
                f"Anda sedang meminjam {len(buku_aktif_user)} buku.",
                f"Batas maksimal per pengunjung adalah {MAKS_BUKU_SEKALIGUS} buku.",
                "Silakan kembalikan buku terlebih dahulu untuk meminjam lagi."
            ]
        )
        input("\nTekan Enter untuk kembali ke Dashboard...")
        return

    # 2. Tampilkan Katalog Buku Langsung dengan Nomor Urut
    daftar_buku = dapatkan_list_buku(katalog)
    tampilkan_tabel_katalog(daftar_buku)
    
    print("\n💡 Petunjuk: Masukkan NOMOR BUKU (1, 2, ...) atau ketik '0' untuk Batal.")
    
    # 3. Pemilihan Buku Ramah Pengguna
    buku_terpilih = None
    kode_terpilih = None
    
    while True:
        pilihan = input("\nPilih Nomor Buku yang ingin dipinjam: ").strip()
        
        if pilihan in ("0", "batal", "BATAL"):
            print("\n❌ Proses peminjaman dibatalkan.")
            time.sleep(1)
            return
            
        try:
            nomor = int(pilihan)
            if 1 <= nomor <= len(daftar_buku):
                kode_terpilih, buku_terpilih = daftar_buku[nomor - 1]
                if buku_terpilih['stok'] <= 0:
                    print("⚠️ Maaf, stok buku ini sedang habis. Silakan pilih nomor buku lain.")
                    continue
                break
            else:
                print(f"⚠️ Harap pilih nomor antara 1 sampai {len(daftar_buku)}.")
        except ValueError:
            # Jika user mengetik kode buku secara langsung (fallback support)
            kode_input = pilihan.upper()
            if kode_input in katalog:
                kode_terpilih = kode_input
                buku_terpilih = katalog[kode_input]
                if buku_terpilih['stok'] <= 0:
                    print("⚠️ Maaf, stok buku ini sedang habis.")
                    continue
                break
            print("⚠️ Pilihan tidak valid. Masukkan nomor urut buku yang ada di atas.")

    # 4. Tampilkan Kartu Estimasi Cerdas & Rekomendasi
    data_user = database_akun.get(nim_aktif, user_aktif)
    history_user = data_user.get('history_peminjaman', [])
    streak_user = data_user.get('streak_saat_ini', 0)
    
    est_hari, rek_pinjam, avg_hist, persen_efisiensi, status_streak = hitung_estimasi_peminjaman(
        history_user, streak_user
    )
    
    print()
    cetak_kartu(
        "REKOMENDASI ESTIMASI PEMINJAMAN CERDAS",
        [
            f"Buku Terpilih       : {buku_terpilih['judul']}",
            f"Reading Streak Anda : {streak_user} Hari ({status_streak})",
            f"Efisiensi Habit     : +{persen_efisiensi}% Kecepatan Membaca ⚡",
            f"Estimasi Selesai    : {est_hari} Hari (Rata-rata: {avg_hist:.1f} Hari)",
            f"Rekomendasi Pinjam  : {rek_pinjam} Hari (Aman dari Denda)"
        ]
    )

    # 5. Input Durasi dengan Smart Default (Tinggal tekan Enter)
    print(f"\n💡 [Smart Default] Tekan [Enter] langsung untuk memilih rekomendasi {rek_pinjam} hari.")
    prompt = f"Masukkan Lama Pinjam [Maks {MAKS_HARI_PINJAM} Hari | 0: Batal]: "
    lama_pinjam = input_angka_valid(prompt, nilai_default=rek_pinjam)
    
    if lama_pinjam == 0:
        print("\n❌ Proses peminjaman dibatalkan.")
        time.sleep(1)
        return
        
    if lama_pinjam > MAKS_HARI_PINJAM:
        lama_pinjam = MAKS_HARI_PINJAM
        print(f"ℹ️ Durasi disesuaikan dengan batas maksimum perpustakaan: {MAKS_HARI_PINJAM} Hari.")

    # 6. Konfirmasi Transaksi (HCD Prevention of Errors)
    tanggal_hari_ini = datetime.date.today()
    tanggal_jatuh_tempo = tanggal_hari_ini + datetime.timedelta(days=lama_pinjam)
    
    print("\n" + "─" * 60)
    print("📋 RINGKASAN PEMINJAMAN:")
    print(f"  • Judul Buku   : {buku_terpilih['judul']}")
    print(f"  • Tanggal Pinjam : {tanggal_hari_ini}")
    print(f"  • Jatuh Tempo    : {tanggal_jatuh_tempo} ({lama_pinjam} Hari)")
    print("─" * 60)
    
    if not konfirmasi_ya_tidak("Konfirmasi peminjaman ini sekarang?"):
        print("\n❌ Transaksi dibatalkan.")
        time.sleep(1)
        return

    # 7. Eksekusi & Simpan
    katalog[kode_terpilih]['stok'] -= 1
    simpan_data(katalog, FILE_KATALOG)

    profil = {"nama": user_aktif['nama'], "nim": nim_aktif}
    transaksi = {
        "judul_buku": buku_terpilih['judul'], 
        "kode_buku": kode_terpilih, 
        "lama_pinjam": lama_pinjam,
        "tanggal_pinjam": str(tanggal_hari_ini),
        "jatuh_tempo": str(tanggal_jatuh_tempo)
    }
    
    semua_transaksi.append({"profil": profil, "transaksi": transaksi})
    simpan_data(semua_transaksi, FILE_JSON)
    
    notifikasi(f"Buku '{buku_terpilih['judul']}' berhasil dipinjam!", "sukses")


def lihat_buku_saya(semua_transaksi, nim_aktif, katalog):
    """
    Melihat daftar buku yang sedang aktif dipinjam secara terstruktur.
    """
    cetak_header("DAFTAR PINJAMAN AKTIF SAYA")
    
    buku_saya = [data for data in semua_transaksi if data['profil']['nim'] == nim_aktif]
    
    if not buku_saya:
        print("\n  ℹ️ Anda sedang tidak meminjam buku apa pun saat ini.\n")
    else:
        print(f"\n  📊 Kuota Pinjam Terpakai: {len(buku_saya)} dari {MAKS_BUKU_SEKALIGUS} Buku (Maksimal)\n")
        print("─" * 60)
        for index, data in enumerate(buku_saya, start=1):
            t = data['transaksi']
            kode = t.get('kode_buku', 'N/A')
            judul = t['judul_buku']
            jatuh_tempo = t.get('jatuh_tempo', '-')
            
            lokasi = katalog.get(kode, {}).get('lokasi', ['Lantai 1', 'Umum'])
            lantai, rak = tuple(lokasi)
            
            print(f" [{index}] {judul} ({kode})")
            print(f"     📅 Tgl Pinjam  : {t.get('tanggal_pinjam', '-')}")
            print(f"     ⏳ Jatuh Tempo : {jatuh_tempo}")
            print(f"     📍 Lokasi Asal : {lantai}, {rak}")
            print("─" * 60)
            
    input("\nTekan Enter untuk kembali ke Dashboard...")


def kembalikan_buku_saya(semua_transaksi, nim_aktif, katalog, user_aktif, database_akun):
    """
    Fitur pengembalian buku dengan alur intuitif dan konfirmasi jelas.
    """
    cetak_header("PENGEMBALIAN BUKU MANDIRI")
    
    buku_dipinjam = [data for data in semua_transaksi if data['profil']['nim'] == nim_aktif]
    
    if not buku_dipinjam:
        print("\n  ℹ️ Anda tidak memiliki buku yang sedang dipinjam saat ini.")
        input("\nTekan Enter untuk kembali...")
        return
        
    print("\nBuku yang sedang Anda pinjam:")
    print("─" * 60)
    for idx, data in enumerate(buku_dipinjam, 1):
        t = data['transaksi']
        print(f" [{idx}] {t['judul_buku']} ({t.get('kode_buku')}) | Jatuh tempo: {t.get('jatuh_tempo')}")
    print("─" * 60)
    
    print("\nPilihan Aksi Pengembalian:")
    print(" [A] Kembalikan SEMUA Buku Sekaligus")
    print(" [1-N] Pilih Nomor Buku Tertentu")
    print(" [0] Batal")
    
    opsi = input("\nMasukkan pilihan Anda: ").strip().lower()
    
    if opsi in ("0", "batal"):
        print("\nProses dibatalkan.")
        time.sleep(1)
        return
        
    buku_yang_akan_kembali = []
    if opsi in ("a", "semua", "all"):
        buku_yang_akan_kembali = list(buku_dipinjam)
    else:
        try:
            nomor = int(opsi)
            if 1 <= nomor <= len(buku_dipinjam):
                buku_yang_akan_kembali = [buku_dipinjam[nomor - 1]]
            else:
                print("⚠️ Nomor buku tidak valid.")
                time.sleep(1)
                return
        except ValueError:
            print("⚠️ Pilihan tidak dikenali.")
            time.sleep(1)
            return

    tanggal_kembali = datetime.date.today()
    total_denda_semua = 0
    
    if 'riwayat_baca' not in database_akun[nim_aktif]:
        database_akun[nim_aktif]['riwayat_baca'] = []
    if 'history_peminjaman' not in database_akun[nim_aktif]:
        database_akun[nim_aktif]['history_peminjaman'] = []

    print("\n" + "─" * 60)
    print("📋 HASIL PENGECEKAN STATUS PENGEMBALIAN:")
    print("─" * 60)
    
    for data in buku_yang_akan_kembali:
        judul = data['transaksi']['judul_buku']
        kode = data['transaksi'].get('kode_buku')
        tgl_pinjam_str = data['transaksi'].get('tanggal_pinjam', str(tanggal_kembali))
        
        try:
            tgl_pinjam = datetime.datetime.strptime(tgl_pinjam_str, "%Y-%m-%d").date()
            durasi_aktual = max(1, (tanggal_kembali - tgl_pinjam).days)
        except Exception:
            durasi_aktual = 1
        
        # Tuple Unpacking return value fungsi hitung_denda_dan_status
        telat_hari, denda, status_pesan = hitung_denda_dan_status(
            data['transaksi']['jatuh_tempo'], 
            tanggal_kembali
        )
        total_denda_semua += denda
        
        if denda > 0:
            denda_str = f"Rp {denda:,}".replace(',', '.')
            print(f" ⚠️  {judul}")
            print(f"     Status : {status_pesan} | Denda: {denda_str}")
        else:
            print(f" ✅  {judul}")
            print(f"     Status : {status_pesan} (Bebas Denda)")
            
        # Kembalikan stok
        if kode and kode in katalog:
            katalog[kode]['stok'] += 1
            
        # Catat ke riwayat baca
        database_akun[nim_aktif]['riwayat_baca'].append({
            "judul": judul,
            "kode": kode,
            "tanggal_kembali": str(tanggal_kembali)
        })
        
        # Catat ke history peminjaman
        database_akun[nim_aktif]['history_peminjaman'].append({
            "kode_buku": kode,
            "judul_buku": judul,
            "tanggal_pinjam": tgl_pinjam_str,
            "tanggal_kembali": str(tanggal_kembali),
            "durasi_aktual_hari": durasi_aktual,
            "status": status_pesan,
            "denda": denda
        })
        
        semua_transaksi.remove(data)
        
    simpan_data(semua_transaksi, FILE_JSON)
    simpan_data(katalog, FILE_KATALOG)
    simpan_data(database_akun, FILE_AKUN)
    
    if total_denda_semua > 0:
        total_str = f"Rp {total_denda_semua:,}".replace(',', '.')
        print("─" * 60)
        print(f" 💰 TOTAL DENDA KETERLAMBATAN : {total_str}")
        print("    (Harap bayar di loket kasir perpustakaan)")
    
    print("─" * 60)
    input("\nTekan Enter untuk menyelesaikan...")
    notifikasi("Buku telah berhasil dikembalikan!", "sukses")


def cari_dan_filter_katalog(katalog):
    """
    Menu eksplorasi katalog yang ramah dan interaktif (HCD):
    Pengguna diberi pilihan jelas (Cari, Filter Genre, atau Lihat Semua)
    sehingga tidak pernah melihat layar input kosong yang membingungkan.
    """
    while True:
        cetak_header("KATALOG & PENCARIAN BUKU", "Eksplorasi Koleksi Perpustakaan")
        
        print("\nPilih Cara Menjelajahi Koleksi:")
        print(" [1] 📋 Tampilkan Seluruh Koleksi Buku")
        print(" [2] 🏷️  Filter berdasarkan Kategori / Genre")
        print(" [3] 🔍 Cari dengan Kata Kunci (Judul, Topik, atau Kode)")
        print(" [0] ↩️  Kembali ke Dashboard Utama")
        print("─" * 60)
        
        pilihan = input("\nMasukkan pilihan menu (0-3): ").strip()
        
        if pilihan == "0":
            break
            
        elif pilihan == "1":
            # Tampilkan semua
            daftar = dapatkan_list_buku(katalog, filter_kategori="Semua")
            cetak_header("SELURUH KOLEKSI BUKU", f"Total: {len(daftar)} Judul Buku")
            tampilkan_tabel_katalog(daftar)
            input("\nTekan Enter untuk kembali ke menu pencarian...")
            
        elif pilihan == "2":
            # Filter Kategori
            cetak_header("FILTER KOLEKSI BERDASARKAN KATEGORI")
            print("\nDaftar Kategori yang Tersedia:")
            # Tampilkan kategori dari list DAFTAR_KATEGORI (tanpa duplikasi 'Semua')
            kategori_opsi = [k for k in DAFTAR_KATEGORI if k != "Semua"]
            for idx, kat in enumerate(kategori_opsi, 1):
                print(f" [{idx}] {kat}")
            print(" [0] Batal")
            
            pilih_k = input("\nPilih nomor kategori: ").strip()
            if pilih_k == "0":
                continue
                
            try:
                idx_k = int(pilih_k)
                if 1 <= idx_k <= len(kategori_opsi):
                    kat_terpilih = kategori_opsi[idx_k - 1]
                    daftar = dapatkan_list_buku(katalog, filter_kategori=kat_terpilih)
                    cetak_header(f"KOLEKSI KATEGORI: {kat_terpilih.upper()}", f"Ditemukan: {len(daftar)} Buku")
                    tampilkan_tabel_katalog(daftar)
                    input("\nTekan Enter untuk kembali...")
                else:
                    print("⚠️ Nomor kategori tidak valid.")
                    time.sleep(1)
            except ValueError:
                print("⚠️ Masukkan angka yang valid.")
                time.sleep(1)
                
        elif pilihan == "3":
            # Cari Keyword
            cetak_header("PENCARIAN BUKU")
            print("\n💡 Tips: Anda bisa mencari judul (misal: 'Python'), genre ('Database'), atau kode ('PY-01').")
            keyword = input("\nMasukkan kata kunci pencarian (0 untuk Batal): ").strip()
            
            if keyword in ("0", ""):
                continue
                
            daftar = dapatkan_list_buku(katalog, filter_keyword=keyword)
            cetak_header(f"HASIL PENCARIAN: '{keyword}'", f"Ditemukan {len(daftar)} Buku")
            tampilkan_tabel_katalog(daftar)
            input("\nTekan Enter untuk kembali...")


def menu_history_dan_estimasi(user_aktif, nim_aktif, database_akun):
    """
    Dashboard visual riwayat peminjaman dan estimasi kecepatan membaca (HCD).
    """
    cetak_header("RIWAYAT PEMINJAMAN & ESTIMASI BACA", f"Pengguna: {user_aktif['nama'].upper()}")
    
    data_user = database_akun.get(nim_aktif, user_aktif)
    history_peminjaman = data_user.get('history_peminjaman', [])
    streak_hari = data_user.get('streak_saat_ini', 0)
    
    est_hari, rek_pinjam, avg_hist, persen_efisiensi, status_streak = hitung_estimasi_peminjaman(
        history_peminjaman, streak_hari
    )
    
    print()
    cetak_kartu(
        "PROFIL & ANALISIS ESTIMASI KEBIASAAN MEMBACA",
        [
            f"Reading Streak Aktif : {streak_hari} Hari ({status_streak})",
            f"Total Peminjaman     : {len(history_peminjaman)} Transaksi Selesai",
            f"Rata-rata Durasi     : {avg_hist:.1f} Hari / Buku",
            f"Bonus Habit Streak   : +{persen_efisiensi}% Efisiensi Membaca ⚡",
            f"Estimasi Selesai     : {est_hari} Hari Membaca",
            f"Rekomendasi Pinjam   : {rek_pinjam} Hari (Aman dari Denda)"
        ]
    )
    
    print("\n📜 TABEL RIWAYAT PEMINJAMAN LALU:")
    if not history_peminjaman:
        print("  Belum ada riwayat peminjaman masa lalu yang tercatat.")
    else:
        print("─" * 60)
        for idx, item in enumerate(history_peminjaman, 1):
            denda_val = item.get('denda', 0)
            denda_str = f"Rp {denda_val:,}".replace(',', '.') if denda_val > 0 else "Rp 0"
            print(f" [{idx}] {item.get('judul_buku', '-')} ({item.get('kode_buku', '-')})")
            print(f"     📅 Pinjam : {item.get('tanggal_pinjam', '-')} | Kembali : {item.get('tanggal_kembali', '-')}")
            print(f"     ⏱️ Durasi : {item.get('durasi_aktual_hari', '-')} Hari | Status : {item.get('status', '-')} | Denda : {denda_str}")
            print("─" * 60)
            
    input("\nTekan Enter untuk kembali ke Dashboard...")


def reading_habit_tracker(user_aktif, nim_aktif, database_akun):
    """
    Fitur Habit Tracker harian yang ramah dan memotivasi pengunjung.
    """
    cetak_header("HABIT TRACKER & STREAK CHALLENGE", "Tingkatkan Kebiasaan Literasi Harian Anda")
    
    data_user = database_akun.get(nim_aktif, user_aktif)
    streak_saat_ini = data_user.get('streak_saat_ini', 0)
    terakhir_checkin = data_user.get('terakhir_checkin', "")
    riwayat_baca = data_user.get('riwayat_baca', [])
    
    badge_tercapai = "Belum Ada Badge"
    for target_hari, nama_badge in BADGE_STREAK:
        if streak_saat_ini >= target_hari:
            badge_tercapai = nama_badge
            
    print()
    cetak_kartu(
        "STATUS KEBIASAAN MEMBACA ANDA",
        [
            f"Pengunjung     : {data_user.get('nama', '').upper()}",
            f"Reading Streak : {streak_saat_ini} Hari Berturut-turut 🔥",
            f"Badge Prestasi : {badge_tercapai}",
            f"Terakhir Baca  : {terakhir_checkin if terakhir_checkin else 'Belum pernah check-in'}"
        ]
    )
    
    print("\n🏆 TINGKATAN BADGE PRESTASI (TUPLE MASTER):")
    for target_hari, nama_badge in BADGE_STREAK:
        status = "✅ Tercapai" if streak_saat_ini >= target_hari else f"🔒 Butuh {target_hari} hari berturut-turut"
        print(f"  • {target_hari} Hari  : {nama_badge.ljust(25)} [{status}]")
    print("─" * 60)

    print("\nPilihan Aksi:")
    print(" [1] ✅ Check-In Membaca Hari Ini (+1 Streak Harian)")
    print(" [2] 📖 Lihat Riwayat Buku Selesai Dibaca")
    print(" [0] ↩️  Kembali ke Dashboard")
    
    pilihan = input("\nMasukkan pilihan (0-2): ").strip()
    
    if pilihan == '1':
        hari_ini = datetime.date.today()
        hari_ini_str = str(hari_ini)
        
        if terakhir_checkin == hari_ini_str:
            notifikasi("Anda sudah check-in membaca hari ini! Pertahankan streak Anda besok!", "info")
            return
            
        if terakhir_checkin:
            tgl_kemarin = hari_ini - datetime.timedelta(days=1)
            if str(tgl_kemarin) == terakhir_checkin:
                streak_saat_ini += 1
            else:
                streak_saat_ini = 1
        else:
            streak_saat_ini = 1
            
        data_user['streak_saat_ini'] = streak_saat_ini
        data_user['terakhir_checkin'] = hari_ini_str
        database_akun[nim_aktif] = data_user
        simpan_data(database_akun, FILE_AKUN)
        
        notifikasi(f"Check-in Berhasil! Streak Anda: {streak_saat_ini} Hari 🔥", "sukses")
        
    elif pilihan == '2':
        cetak_header("RIWAYAT BUKU SELESAI DIBACA")
        if not riwayat_baca:
            print("\n  Belum ada buku yang selesai dibaca.")
        else:
            print(f"\n  Total Buku yang Pernah Dibaca: {len(riwayat_baca)} buku\n")
            print("─" * 60)
            for idx, item in enumerate(riwayat_baca, 1):
                print(f" [{idx}] {item.get('judul', '-')} ({item.get('kode', '-')})")
                print(f"     ✅ Selesai Dikembalikan: {item.get('tanggal_kembali', '-')}")
                print("─" * 60)
        input("\nTekan Enter untuk kembali...")


def main():
    user_aktif, nim_aktif = menu_autentikasi()
    
    if not user_aktif:
        clear_screen()
        print("Sistem dimatikan. Sampai jumpa!")
        return False

    semua_transaksi = muat_data(FILE_JSON)
    katalog_buku = muat_data(FILE_KATALOG)
    database_akun = muat_data(FILE_AKUN)

    while True:
        data_user = database_akun.get(nim_aktif, user_aktif)
        streak = data_user.get('streak_saat_ini', 0)
        terakhir_checkin = data_user.get('terakhir_checkin', "")
        hari_ini_str = str(datetime.date.today())
        
        # Indikator status check-in hari ini yang interaktif
        if terakhir_checkin == hari_ini_str:
            info_streak = f"🔥 Streak: {streak} Hari"
        elif streak > 0:
            info_streak = f"⚠️ Streak: {streak} Hari [⚡ Belum Check-In Hari Ini]"
        else:
            info_streak = f"⚪ Streak: {streak} Hari [Ketik 6 utk Nyalakan]"
        
        cetak_header(
            "NEXUS LIBRARY KIOSK (SELF-SERVICE)",
            f"👤 {user_aktif['nama'].upper()} (NIM: {nim_aktif}) | {info_streak}"
        )
        
        print("\n [1] 📖 Pinjam Buku Baru        -> Cepat pilih via nomor & estimasi AI")
        print(" [2] 📚 Pinjaman Aktif Saya     -> Cek buku & batas tanggal jatuh tempo")
        print(" [3] ↩️  Kembalikan Buku         -> Pengembalian mudah & kalkulasi denda")
        print(" [4] 🔍 Katalog & Pencarian     -> Eksplorasi koleksi & filter genre")
        print(" [5] 📜 Riwayat & Estimasi Baca -> Histori peminjaman & rekomendasi durasi")
        print(" [6] 🏆 Habit Tracker & Streak  -> Check-In harian (+1 Streak) & Badge")
        print(" [0] 🚪 Logout                  -> Keluar akun dengan aman")
        print("─" * 60)
        
        pilihan = input("Pilih menu (0-6): ").strip()
        
        if pilihan == '1':
            tambah_peminjaman_baru(semua_transaksi, user_aktif, nim_aktif, katalog_buku, database_akun)
        elif pilihan == '2':
            lihat_buku_saya(semua_transaksi, nim_aktif, katalog_buku)
        elif pilihan == '3':
            kembalikan_buku_saya(semua_transaksi, nim_aktif, katalog_buku, user_aktif, database_akun)
        elif pilihan == '4':
            cari_dan_filter_katalog(katalog_buku)
        elif pilihan == '5':
            menu_history_dan_estimasi(user_aktif, nim_aktif, database_akun)
        elif pilihan == '6':
            reading_habit_tracker(user_aktif, nim_aktif, database_akun)
        elif pilihan in ('0', '7', 'logout', 'LOGOUT'):
            notifikasi("Anda telah Logout. Sampai jumpa kembali!", "info")
            break 
        else:
            print("\n⚠️ Pilihan tidak valid! Masukkan angka antara 0 sampai 6.")
            time.sleep(1)
            
    return True 


if __name__ == "__main__":
    mesin_hidup = True
    while mesin_hidup:
        mesin_hidup = main()