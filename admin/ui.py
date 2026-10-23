from ui import cetak_kartu


def cetak_menu_admin(judul, pilihan, prompt):
    """Tampilkan pilihan menu administrator dalam format seragam."""
    isi_menu = [f"[{nomor}] {label} — {keterangan}" for nomor, label, keterangan in pilihan]
    cetak_kartu(judul, isi_menu)
    return input(f"\n{prompt}: ").strip()
