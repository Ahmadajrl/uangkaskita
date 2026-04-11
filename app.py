import streamlit as st
import pandas as pd
import datetime
import sqlite3

# ======================
# CONFIG
# ======================
st.set_page_config(layout="wide")

# ======================
# DATABASE SQLITE (AMAN CLOUD)
# ======================
conn = sqlite3.connect("kas.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS kas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT,
    tanggal TEXT,
    status TEXT
)
''')
conn.commit()

# ======================
# HEADER
# ======================
st.title("KAS KITA")

# ======================
# INPUT
# ======================
st.subheader("Input Pembayaran")

nama = st.text_input("Nama Siswa")
tanggal = st.date_input("Tanggal Bayar", datetime.date.today())
status = st.selectbox("Status", ["Tepat Waktu", "Telat"])

if st.button("Simpan"):
    if nama.strip():
        cursor.execute(
            "INSERT INTO kas (nama, tanggal, status) VALUES (?, ?, ?)",
            (nama, str(tanggal), status)
        )
        conn.commit()
        st.success("Data berhasil disimpan!")
    else:
        st.warning("Nama tidak boleh kosong!")

# ======================
# AMBIL DATA
# ======================
df = pd.read_sql("SELECT * FROM kas", conn)

# ======================
# TABEL
# ======================
st.subheader("Data Pembayaran")
st.dataframe(df, use_container_width=True)

# ======================
# ANALISIS GLOBAL
# ======================
st.subheader("Analisis Keseluruhan")

if not df.empty:
    global_data = df["status"].value_counts()
    st.bar_chart(global_data)
else:
    st.warning("Belum ada data")

# ======================
# STATISTIK PER SISWA
# ======================
st.subheader("Statistik Keterlambatan Siswa")

if not df.empty:
    nama_list = df["nama"].unique()
    nama_pilih = st.selectbox("Pilih Nama Siswa", nama_list)

    if st.button("Lihat Statistik"):
        data_siswa = df[df["nama"] == nama_pilih]

        if not data_siswa.empty:
            st.write(f"Statistik untuk: **{nama_pilih}**")

            # HITUNG
            hasil = data_siswa["status"].value_counts()

            # TAMPILKAN BAR CHART (PALING AMAN)
            st.bar_chart(hasil)

            # TAMPILKAN ANGKA
            st.write("Detail:")
            st.write(hasil)
        else:
            st.warning("Belum ada data siswa ini")
else:
    st.warning("Belum ada data")

# ======================
# FOOTER
# ======================
st.write("©KasKita 2026")
