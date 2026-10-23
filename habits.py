import datetime
from database import BADGE_STREAK, simpan_data, FILE_AKUN
from ui import cetak_header, cetak_kartu, notifikasi


def reading_habit_tracker(user_aktif, nim_aktif, database_akun):
    """
    Fitur Habit Tracker harian: Check-in streak, riwayat buku selesai, dan Kartu Anggota Digital.
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
    print(" [3] 🪪 Tampilkan Kartu Anggota Digital & Pass Literasi")
    print(" [0] ↩️  Kembali ke Dashboard")

    pilihan = input("\nMasukkan pilihan (0-3): ").strip()

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

    elif pilihan == '3':
        cetak_header("KARTU ANGGOTA DIGITAL & PASS LITERASI")
        print("\n ╔══════════════════════════════════════════════════════════╗")
        print(" ║            NEXUS SMART LIBRARY - DIGITAL PASS            ║")
        print(" ╠══════════════════════════════════════════════════════════╣")
        print(f" ║  Nama Lengkap  : {data_user.get('nama', '').upper().ljust(39)} ║")
        print(f" ║  Nomor Anggota : {nim_aktif.ljust(39)} ║")
        print(f" ║  Level Literasi: {badge_tercapai.ljust(39)} ║")
        print(f" ║  Streak Aktif  : {str(streak_saat_ini).ljust(2)} Hari Membaca Berturut-turut 🔥     ║")
        print(f" ║  Buku Dibaca   : {str(len(riwayat_baca)).ljust(2)} Judul Selesai                    ║")
        print(" ╠══════════════════════════════════════════════════════════╣")
        print(" ║  BARCODE: ||||| | |||| ||| || ||||| |||| || |||||| ||||  ║")
        print(" ╚══════════════════════════════════════════════════════════╝")
        input("\nTekan Enter untuk kembali ke Habit Tracker...")
