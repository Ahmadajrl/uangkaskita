import streamlit as st 
import pandas as pd
import datetime

from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier

# ======================
# KONEKSI DATABASE (AUTO SWITCH)
# ======================
try:
    import mysql.connector

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="091206",  # ganti jika perlu
        database="kas_siswa"
    )
    cursor = conn.cursor()
    DB_MODE = "MYSQL"

except:
    import sqlite3

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

    DB_MODE = "SQLITE"

# ======================
# UI TITLE
# ======================
st.title("📊 Aplikasi Uang Kas Siswa + AI")
st.caption(f"Mode Database: {DB_MODE}")

# ======================
# INPUT DATA
# ======================
st.subheader("➕ Input Pembayaran")

nama = st.text_input("Nama Siswa")
tanggal = st.date_input("Tanggal Bayar", datetime.date.today())
status = st.selectbox("Status", ["Tepat Waktu", "Telat"])

if st.button("Simpan"):
    if nama.strip() != "":
        if DB_MODE == "MYSQL":
            query = "INSERT INTO kas (nama, tanggal, status) VALUES (%s, %s, %s)"
        else:
            query = "INSERT INTO kas (nama, tanggal, status) VALUES (?, ?, ?)"

        data = (nama, str(tanggal), status)

        cursor.execute(query, data)
        conn.commit()

        st.success("Data berhasil disimpan!")
    else:
        st.warning("Nama tidak boleh kosong!")

# ======================
# AMBIL DATA
# ======================
df = pd.read_sql("SELECT * FROM kas", conn)

# ======================
# TAMPILKAN DATA
# ======================
st.subheader("📋 Data Pembayaran")
st.dataframe(df)

# ======================
# DATA SCIENCE
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
            hasil = model.predict([nama_encoded])
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
