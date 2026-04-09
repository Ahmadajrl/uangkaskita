import streamlit as st
import pandas as pd
import datetime
import os
import sqlite3

from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier

# ======================
# DATABASE (SQLite - Aman untuk Streamlit Cloud)
# ======================
DB_PATH = "kas.db"

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# Buat tabel jika belum ada
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
# UI
# ======================
st.title("📊 Aplikasi Uang Kas Siswa + AI")
st.caption("Mode Database: SQLite")

# ======================
# INPUT DATA (PAKAI FORM)
# ======================
st.subheader("➕ Input Pembayaran")

with st.form("form_input"):
    nama = st.text_input("Nama Siswa")
    tanggal = st.date_input("Tanggal Bayar", datetime.date.today())
    status = st.selectbox("Status", ["Tepat Waktu", "Telat"])

    submit = st.form_submit_button("Simpan")

    if submit:
        if nama.strip() != "":
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
try:
    df = pd.read_sql("SELECT * FROM kas", conn)
except:
    df = pd.DataFrame(columns=["id", "nama", "tanggal", "status"])

# ======================
# TAMPILKAN DATA
# ======================
st.subheader("📋 Data Pembayaran")
st.dataframe(df)

# ======================
# DOWNLOAD DATABASE
# ======================
with open(DB_PATH, "rb") as f:
    st.download_button(
        label="⬇️ Download Database",
        data=f,
        file_name="kas.db",
        mime="application/octet-stream"
    )

# ======================
# ANALISIS DATA
# ======================
st.subheader("📈 Analisis Data")

if not df.empty:
    total = len(df)
    telat = len(df[df["status"] == "Telat"])
    tepat = len(df[df["status"] == "Tepat Waktu"])

    st.write(f"Total Data: {total}")
    st.write(f"Tepat Waktu: {tepat}")
    st.write(f"Telat: {telat}")

    chart_data = pd.DataFrame({
        "Status": ["Tepat Waktu", "Telat"],
        "Jumlah": [tepat, telat]
    })

    st.bar_chart(chart_data.set_index("Status"))

# ======================
# AI PREDIKSI
# ======================
st.subheader("🤖 Prediksi Keterlambatan")

if len(df) > 5:
    try:
        le_nama = LabelEncoder()
        le_status = LabelEncoder()

        df["nama_enc"] = le_nama.fit_transform(df["nama"])
        df["status_enc"] = le_status.fit_transform(df["status"])

        X = df[["nama_enc"]]
        y = df["status_enc"]

        model = DecisionTreeClassifier()
        model.fit(X, y)

        nama_pred = st.selectbox("Pilih Nama untuk Prediksi", df["nama"].unique())

        if st.button("Prediksi"):
            nama_encoded = le_nama.transform([nama_pred])

            hasil = model.predict(nama_encoded.reshape(1, -1))
            hasil_label = le_status.inverse_transform(hasil)

            st.success(f"Prediksi: {hasil_label[0]}")

    except Exception as e:
        st.error(f"Error AI: {e}")

else:
    st.warning("Data minimal 6 untuk menjalankan AI")

# ======================
# FOOTER
# ======================
st.write("© Project Uang Kas + AI")
