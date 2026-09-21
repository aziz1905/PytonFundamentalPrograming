import json
import os

FILE_JSON = "data_perpustakaan.json"  
FILE_AKUN = "akun_pengunjung.json" 

def muat_data(nama_file):
    if os.path.exists(nama_file):
        try:
            with open(nama_file, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            pass
    return {} if nama_file == FILE_AKUN else []

def simpan_data(data, nama_file):
    with open(nama_file, 'w') as file:
        json.dump(data, file, indent=4)