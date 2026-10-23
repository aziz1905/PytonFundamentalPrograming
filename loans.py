import datetime
import time

from database import (
    simpan_data,
    FILE_JSON,
    FILE_KATALOG,
    FILE_AKUN,
    KONFIGURASI_PERPUSTAKAAN,
)
from ui import (
    LEBAR_TAMPILAN,
    cetak_header,
    cetak_kartu,
    notifikasi,
    input_angka_valid,
    konfirmasi_ya_tidak,
)
from analytics import hitung_denda_dan_status, hitung_estimasi_peminjaman
from catalog_service import dapatkan_list_buku, tampilkan_tabel_katalog
from ulasan import minta_ulasan_buku

MAKS_HARI_PINJAM, TARIF_DENDA_PER_HARI, MAKS_BUKU_SEKALIGUS = KONFIGURASI_PERPUSTAKAAN


def tambah_peminjaman_baru(
    semua_transaksi, user_aktif, nim_aktif, katalog, database_akun, ulasan_buku
):
    cetak_header("PEMINJAMAN BUKU BARU", f"Pengunjung: {user_aktif['nama'].upper()}")

    # 1. Cek Kuota Maksimal Peminjaman
    buku_aktif_user = [t for t in semua_transaksi if t['profil']['nim'] == nim_aktif]
    if len(buku_aktif_user) >= MAKS_BUKU_SEKALIGUS:
        cetak_kartu(
            "Batas Maksimal Peminjaman Tercapai",
            [
                f"Anda sedang meminjam {len(buku_aktif_user)} buku.",
                f"Batas maksimal per pengunjung adalah {MAKS_BUKU_SEKALIGUS} buku.",
                "Silakan kembalikan buku terlebih dahulu untuk meminjam lagi.",
            ],
        )
        input("\nTekan Enter untuk kembali ke Dashboard...")
        return

    # 2. Tampilkan Katalog Buku Langsung dengan Nomor Urut
    daftar_buku = dapatkan_list_buku(katalog)
    tampilkan_tabel_katalog(daftar_buku, ulasan_buku)

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
            f"Rekomendasi Pinjam  : {rek_pinjam} Hari (Aman dari Denda)",
        ],
    )

    # 5. Input Durasi dengan Smart Default
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

    # 6. Konfirmasi Transaksi
    tanggal_hari_ini = datetime.date.today()
    tanggal_jatuh_tempo = tanggal_hari_ini + datetime.timedelta(days=lama_pinjam)

    print("\n" + "─" * LEBAR_TAMPILAN)
    print("📋 RINGKASAN PEMINJAMAN:")
    print(f"  • Judul Buku   : {buku_terpilih['judul']}")
    print(f"  • Tanggal Pinjam : {tanggal_hari_ini}")
    print(f"  • Jatuh Tempo    : {tanggal_jatuh_tempo} ({lama_pinjam} Hari)")
    print("─" * LEBAR_TAMPILAN)

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
        "jatuh_tempo": str(tanggal_jatuh_tempo),
    }

    semua_transaksi.append({"profil": profil, "transaksi": transaksi})
    simpan_data(semua_transaksi, FILE_JSON)

    notifikasi(f"Buku '{buku_terpilih['judul']}' berhasil dipinjam!", "sukses")


def lihat_buku_saya(semua_transaksi, nim_aktif, katalog):
    cetak_header("DAFTAR PINJAMAN AKTIF SAYA")

    buku_saya = [data for data in semua_transaksi if data['profil']['nim'] == nim_aktif]

    if not buku_saya:
        print("\n  ℹ️ Anda sedang tidak meminjam buku apa pun saat ini.\n")
    else:
        print(f"\n  📊 Kuota Pinjam Terpakai: {len(buku_saya)} dari {MAKS_BUKU_SEKALIGUS} Buku (Maksimal)\n")
        print("─" * LEBAR_TAMPILAN)
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
            print("─" * LEBAR_TAMPILAN)

    input("\nTekan Enter untuk kembali ke Dashboard...")


def kembalikan_buku_saya(
    semua_transaksi, nim_aktif, katalog, user_aktif, database_akun, ulasan_buku
):
    cetak_header("PENGEMBALIAN BUKU MANDIRI")

    buku_dipinjam = [data for data in semua_transaksi if data['profil']['nim'] == nim_aktif]

    if not buku_dipinjam:
        print("\n  ℹ️ Anda tidak memiliki buku yang sedang dipinjam saat ini.")
        input("\nTekan Enter untuk kembali...")
        return

    print("\nBuku yang sedang Anda pinjam:")
    print("─" * LEBAR_TAMPILAN)
    for idx, data in enumerate(buku_dipinjam, 1):
        t = data['transaksi']
        print(f" [{idx}] {t['judul_buku']} ({t.get('kode_buku')}) | Jatuh tempo: {t.get('jatuh_tempo')}")
    print("─" * LEBAR_TAMPILAN)

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

    print("\n" + "─" * LEBAR_TAMPILAN)
    print("📋 HASIL PENGECEKAN STATUS PENGEMBALIAN:")
    print("─" * LEBAR_TAMPILAN)

    for data in buku_yang_akan_kembali:
        judul = data['transaksi']['judul_buku']
        kode = data['transaksi'].get('kode_buku')
        tgl_pinjam_str = data['transaksi'].get('tanggal_pinjam', str(tanggal_kembali))

        try:
            tgl_pinjam = datetime.datetime.strptime(tgl_pinjam_str, "%Y-%m-%d").date()
            durasi_aktual = max(1, (tanggal_kembali - tgl_pinjam).days)
        except Exception:
            durasi_aktual = 1

        telat_hari, denda, status_pesan = hitung_denda_dan_status(
            data['transaksi']['jatuh_tempo'],
            tanggal_kembali,
        )
        total_denda_semua += denda

        if denda > 0:
            denda_str = f"Rp {denda:,}".replace(',', '.')
            print(f" ⚠️  {judul}")
            print(f"     Status : {status_pesan} | Denda: {denda_str}")
        else:
            print(f" ✅  {judul}")
            print(f"     Status : {status_pesan} (Bebas Denda)")

        if kode and kode in katalog:
            katalog[kode]['stok'] += 1

        database_akun[nim_aktif]['riwayat_baca'].append({
            "judul": judul,
            "kode": kode,
            "tanggal_kembali": str(tanggal_kembali),
        })

        database_akun[nim_aktif]['history_peminjaman'].append({
            "kode_buku": kode,
            "judul_buku": judul,
            "tanggal_pinjam": tgl_pinjam_str,
            "tanggal_kembali": str(tanggal_kembali),
            "durasi_aktual_hari": durasi_aktual,
            "status": status_pesan,
            "denda": denda,
        })

        if kode:
            minta_ulasan_buku(
                ulasan_buku,
                kode,
                nim_aktif,
                user_aktif['nama'],
                judul,
            )

        semua_transaksi.remove(data)

    simpan_data(semua_transaksi, FILE_JSON)
    simpan_data(katalog, FILE_KATALOG)
    simpan_data(database_akun, FILE_AKUN)

    if total_denda_semua > 0:
        total_str = f"Rp {total_denda_semua:,}".replace(',', '.')
        print("─" * LEBAR_TAMPILAN)
        print(f" 💰 TOTAL DENDA KETERLAMBATAN : {total_str}")
        print("    (Harap bayar di loket kasir perpustakaan)")

    print("─" * LEBAR_TAMPILAN)
    input("\nTekan Enter untuk menyelesaikan...")
    notifikasi("Buku telah berhasil dikembalikan!", "sukses")
