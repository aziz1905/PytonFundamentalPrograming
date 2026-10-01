import datetime

BATAS_VIP = 7

def update_login_streak(user_aktif):
    """
    Menghitung streak berdasarkan kehadiran harian (Daily Login).
    """
    hari_ini = datetime.date.today()
    tanggal_terakhir_str = user_aktif.get('tanggal_terakhir_login', "")
    streak_lama = user_aktif.get('streak_saat_ini', 0)
    
    if tanggal_terakhir_str == "":
        # Pertama kali login setelah mendaftar
        user_aktif['streak_saat_ini'] = 1
        pesan = "🔥 Hari Pertama! Kunjungi Kiosk besok untuk menambah streak Anda."
    else:
        tanggal_terakhir = datetime.datetime.strptime(tanggal_terakhir_str, "%Y-%m-%d").date()
        selisih_hari = (hari_ini - tanggal_terakhir).days
        
        if selisih_hari == 0:
            pesan = None # Sudah login hari ini, tidak ada notif baru
        elif selisih_hari == 1:
            streak_baru = streak_lama + 1
            user_aktif['streak_saat_ini'] = streak_baru
            if streak_baru < BATAS_VIP:
                pesan = f"🔥 STREAK NAIK! (Day {streak_baru})."
            else:
                pesan = f"👑 VIP UNLOCKED! (Day {streak_baru})."
        else:
            user_aktif['streak_saat_ini'] = 1
            pesan = f"💔 STREAK HANGUS! Anda absen {selisih_hari} hari. Kembali ke Day 1."
            
    # Update tanggal terakhir login ke hari ini
    user_aktif['tanggal_terakhir_login'] = str(hari_ini)
    return pesan

def cek_status_streak(user_aktif):
    streak = user_aktif.get('streak_saat_ini', 0)
    if streak == 0:
        return "Belum ada streak (Day 0)"
    elif streak < BATAS_VIP:
        return f"🔥 On Fire (Day {streak})"
    else:
        return f"👑 VIP Member (Day {streak})"