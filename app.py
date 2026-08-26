from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
pandas_available = True
try:
    import pandas as pd
except ImportError:
    pandas_available = False
import streamlit as st

# Konfigurasi Halaman Web
st.set_page_config(page_title="Upload Data Warehouse TTRS/TTRB", page_icon="📦", layout="centered")

st.title("📦 Upload Laporan Oracle ke Sistem")
st.write("Silakan upload file Excel hasil export dari Oracle untuk memperbarui data di Google Sheet secara otomatis.")

# Fungsi untuk menghubungkan ke Google Sheet
def connect_to_gspread():
    # Mengambil kredensial dari Streamlit Secrets (aman untuk GitHub)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # Ganti dengan nama Google Sheet Anda
    sheet_name = "Database_TTRS_TTRB" # Sesuaikan dengan nama Google Sheet Anda
    sheet = client.open(sheet_name).sheet1
    return sheet

# Komponen Upload File di Web
uploaded_file = st.file_uploader("Pilih file Excel (.xlsx / .xls)", type=["xlsx", "xls"])

if uploaded_file is not None:
    if not pandas_available:
        st.error("Library pandas belum terinstal. Harap periksa file requirements.txt.")
    else:
        try:
            # Membaca file Excel yang diupload
            df = pd.read_excel(uploaded_file)
            
            st.subheader("Preview Data yang Di-upload:")
            st.dataframe(df.head()) # Menampilkan 5 baris pertama di web
            
            if st.button("🚀 Proses dan Masukkan ke Google Sheet"):
                with st.spinner("Sedang mengirim data ke Google Sheet..."):
                    sheet = connect_to_gspread()
                    
                    # Konversi DataFrame ke list data baris
                    # Pastikan nama kolom di Excel Anda disesuaikan dengan kebutuhan sistem
                    # Contoh kolom: No TTRS/TTRB, Outlet, Direktorat
                    
                    rows_added = 0
                    for index, row in df.iterrows():
                        # Ambil data berdasarkan nama header di Excel Anda
                        # Sesuaikan string di dalam ['...'] dengan header asli dari Oracle/Excel
                        no_ttrs = str(row.get('No TTRS/TTRB', row.get('No TTRS', '')))
                        outlet = str(row.get('Outlet', ''))
                        direktorat = str(row.get('Direktorat', ''))
                        tanggal_upload = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        status = "Belum Diproses" # Status default
                        
                        # Masukkan ke Google Sheet (urutan kolom: No TTRS, Outlet, Direktorat, Waktu, Status)
                        sheet.append_row([no_ttrs, outlet, direktorat, tanggal_upload, status])
                        rows_added += 1
                        
                    st.success(f"Berhasil! Sebanyak {rows_added} baris data berhasil dimasukkan ke Google Sheet.")
                    st.balloons()
                    
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses file: {e}")
