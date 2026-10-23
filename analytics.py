import datetime
from database import KONFIGURASI_PERPUSTAKAAN, FAKTOR_KECEPATAN_STREAK

MAKS_HARI_PINJAM, TARIF_DENDA_PER_HARI, MAKS_BUKU_SEKALIGUS = KONFIGURASI_PERPUSTAKAAN


def hitung_denda_dan_status(jatuh_tempo_str, tanggal_kembali):
    """
    Kalkulasi denda keterlambatan pengembalian buku.
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

    durasi_list = [
        item['durasi_aktual_hari']
        for item in history_peminjaman
        if item.get('durasi_aktual_hari', 0) > 0
    ]

    # Rata-rata dari List durasi historis
    rata_rata_historis = sum(durasi_list) / len(durasi_list) if durasi_list else 7.0

    # Faktor Kecepatan dari Tuple of Tuples
    faktor_pengali = 1.0
    persen_efisiensi = 0
    label_streak = "Standar (Belum Ada Streak)"

    for min_streak, faktor, label, persen in FAKTOR_KECEPATAN_STREAK:
        if streak_hari >= min_streak:
            faktor_pengali = faktor
            persen_efisiensi = persen
            label_streak = label
            break

    # Boundary Guard & Rekomendasi
    estimasi_hari = max(1, round(rata_rata_historis * faktor_pengali))
    rekomendasi_pinjam = min(MAKS_HARI_PINJAM, estimasi_hari + 1)

    return (estimasi_hari, rekomendasi_pinjam, rata_rata_historis, persen_efisiensi, label_streak)
