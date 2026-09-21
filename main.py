import datetime
import time

# --- PUSAT KENDALI: IMPOR DARI FILE-FILE KECIL KITA ---
from database import muat_data, simpan_data, FILE_JSON, FILE_KATALOG
from ui import clear_screen, notifikasi, input_angka_valid, input_teks_valid
from auth import menu_autentikasi

def tambah_peminjaman_baru(semua_transaksi, user_aktif, nim_aktif, katalog):
    clear_screen()
    print("--- [1] PEMINJAMAN BUKU HARI INI ---")
    
    # 1. Menampilkan Daftar Buku
    print("\n--- KATALOG BUKU ---")
    for kode, info in katalog.items():
        status_stok = info['stok'] if info['stok'] > 0 else "HABIS"
        print(f"[{kode}] {info['judul']} (Stok: {status_stok})")
    print("-" * 20)

    # 2. Loop Validasi Pemilihan Buku (Bisa Batal)
    while True:
        kode_buku = input_teks_valid("\nMasukkan Kode Buku (Ketik '0' untuk BATAL): ").upper()
        
        # Fitur Pembatalan
        if kode_buku == '0' or kode_buku == 'BATAL':
            print("\n❌ Proses peminjaman dibatalkan. Kembali ke Dashboard...")
            time.sleep(1.5)
            return 
            
        if kode_buku not in katalog:
            print("⚠️ Kode buku tidak ditemukan di katalog!")
        elif katalog[kode_buku]['stok'] <= 0:
            print("⚠️ Maaf, stok buku ini sedang kosong atau dipinjam orang lain!")
        else:
            judul_buku = katalog[kode_buku]['judul']
            break 
            
    # 3. Loop Validasi Durasi (Bisa Batal & Maks 12 Hari)
    while True:
        lama_pinjam = input_angka_valid("Lama Pinjam maks 12 hari (Ketik '0' untuk BATAL): ")
        
        if lama_pinjam == 0:
            print("\n❌ Proses peminjaman dibatalkan. Kembali ke Dashboard...")
            time.sleep(1.5)
            return
        elif lama_pinjam > 12:
            print("⚠️ Anda tidak boleh meminjam lebih dari 12 hari!")
        else:
            break

    # 4. Jika semua lolos, eksekusi peminjaman
    tanggal_hari_ini = datetime.date.today()
    tanggal_jatuh_tempo = tanggal_hari_ini + datetime.timedelta(days=lama_pinjam)

    profil = {"nama": user_aktif['nama'], "nim": nim_aktif}
    transaksi = {
        "judul_buku": judul_buku, 
        "kode_buku": kode_buku, 
        "lama_pinjam": lama_pinjam,
        "tanggal_pinjam": str(tanggal_hari_ini),
        "jatuh_tempo": str(tanggal_jatuh_tempo)
    }
    
    # Potong stok dan simpan
    katalog[kode_buku]['stok'] -= 1
    simpan_data(katalog, FILE_KATALOG)

    semua_transaksi.append({"profil": profil, "transaksi": transaksi})
    simpan_data(semua_transaksi, FILE_JSON)
    
    notifikasi(f"Buku '{judul_buku}' berhasil dipinjam!", "sukses")
    print(f"Buku Anda wajib dikembalikan pada: {tanggal_jatuh_tempo}")
    input("\nTekan Enter untuk kembali ke Dashboard...")


def lihat_buku_saya(semua_transaksi, nim_aktif):
    clear_screen()
    print("=======================================================")
    print("                 DAFTAR PINJAMAN SAYA                  ")
    print("=======================================================")
    
    ada_buku = False
    for index, data in enumerate(semua_transaksi, start=1):
        if data['profil']['nim'] == nim_aktif:
            ada_buku = True
            buku = data['transaksi']['judul_buku']
            kode = data['transaksi'].get('kode_buku', 'N/A')
            jatuh_tempo = data['transaksi'].get('jatuh_tempo', 'Tidak diketahui')
            print(f"- [{kode}] {buku} | Jatuh Tempo: {jatuh_tempo}")
            
    if not ada_buku:
        print("Anda sedang tidak meminjam buku apa pun saat ini.")
            
    input("\nTekan Enter untuk kembali ke Dashboard...")


def kembalikan_buku_saya(semua_transaksi, nim_aktif, katalog):
    clear_screen()
    print("--- [3] PENGEMBALIAN BUKU ---")
    
    buku_dipinjam = [data for data in semua_transaksi if data['profil']['nim'] == nim_aktif]
    
    if not buku_dipinjam:
        print("Anda tidak memiliki buku yang harus dikembalikan.")
        input("\nTekan Enter untuk kembali...")
        return
        
    print("Buku yang sedang Anda pinjam:")
    for data in buku_dipinjam:
        print(f">> {data['transaksi']['judul_buku']}")
        
    konfirmasi = input("\nKembalikan semua buku ini sekarang? (y/n): ").strip().lower()
    
    if konfirmasi in ['y', 'ya', 'yes']:
        for data in buku_dipinjam:
            tanggal_kembali = datetime.date.today()
            jatuh_tempo = datetime.datetime.strptime(data['transaksi']['jatuh_tempo'], "%Y-%m-%d").date()
            
            if tanggal_kembali > jatuh_tempo:
                telat = (tanggal_kembali - jatuh_tempo).days
                denda = telat * 2000
                denda_str = f"Rp {denda:,}".replace(',', '.')
                print(f"⚠️ {data['transaksi']['judul_buku']} TERLAMBAT {telat} HARI! Denda: {denda_str}")
            else:
                print(f"✅ {data['transaksi']['judul_buku']} dikembalikan TEPAT WAKTU.")
                
            # Tambahkan kembali stok buku yang dikembalikan
            kode_buku = data['transaksi'].get('kode_buku')
            if kode_buku and kode_buku in katalog:
                katalog[kode_buku]['stok'] += 1
                
            semua_transaksi.remove(data)
            
        simpan_data(semua_transaksi, FILE_JSON)
        simpan_data(katalog, FILE_KATALOG) 
        
        input("\nProses pengembalian selesai. Tekan Enter untuk melanjutkan...")
        notifikasi("Buku telah dikembalikan dan stok diperbarui!", "sukses")
    else:
        print("Proses dibatalkan.")
        time.sleep(1)


def main():
    user_aktif, nim_aktif = menu_autentikasi()
    
    if not user_aktif:
        clear_screen()
        print("Sistem dimatikan. Sampai jumpa!")
        return False

    semua_transaksi = muat_data(FILE_JSON)
    katalog_buku = muat_data(FILE_KATALOG)

    while True:
        clear_screen()
        print("="*55)
        print(f"        DASHBOARD PENGUNJUNG: {user_aktif['nama'].upper()}")
        print("="*55)
        print("1. Pinjam Buku Baru")
        print("2. Lihat Buku Yang Sedang Saya Pinjam")
        print("3. Kembalikan Buku")
        print("4. Logout (Keluar Akun)")
        print("="*55)
        
        pilihan = input("Pilih Menu (1/2/3/4): ").strip()
        
        if pilihan == '1':
            tambah_peminjaman_baru(semua_transaksi, user_aktif, nim_aktif, katalog_buku)
        elif pilihan == '2':
            lihat_buku_saya(semua_transaksi, nim_aktif)
        elif pilihan == '3':
            kembalikan_buku_saya(semua_transaksi, nim_aktif, katalog_buku)
        elif pilihan == '4':
            notifikasi("Anda telah Logout. Terima kasih!", "info")
            break 
        else:
            print("\n⚠️ Pilihan tidak valid!")
            time.sleep(1)
            
    return True 

if __name__ == "__main__":
    mesin_hidup = True
    while mesin_hidup:
        mesin_hidup = main()