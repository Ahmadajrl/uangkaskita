import streamlit as st
import pandas as pd
import datetime
import base64
import matplotlib.pyplot as plt

# ======================
# CONFIG PAGE
# ======================
st.set_page_config(layout="wide")

# ======================
# CUSTOM CSS
# ======================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #01023B;
    color: white;
}
label, .stMarkdown, .stText, p {
    color: white !important;
}
.stButton > button {
    background-color: #09F289;
    color: black;
    font-weight: bold;
    border-radius: 10px;
}
.stButton > button:hover {
    background-color: #07c96f;
    color: white;
}
input, textarea {
    background-color: #02044F !important;
    color: white !important;
}
[data-baseweb="select"] {
    background-color: #02044F !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ======================
# LOGO
# ======================
def get_base64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()

try:
    img = get_base64("logo.png")
    st.markdown(f"""
    <div style="text-align:center;">
        <img src="data:image/png;base64,{img}" width="120">
    </div>
    """, unsafe_allow_html=True)
except:
    st.warning("Logo tidak ditemukan!")

# ======================
# DATABASE
# ======================
try:
    import mysql.connector
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="091206",
        database="kas_siswa"
    )
    DB_MODE = "MYSQL"
except:
    import sqlite3
    conn = sqlite3.connect("kas.db", check_same_thread=False)
    DB_MODE = "SQLITE"

cursor = conn.cursor()

# buat tabel jika belum ada
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
st.title("📊 Aplikasi Uang Kas Siswa")
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

        cursor.execute(query, (nama, str(tanggal), status))
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
st.dataframe(df, use_container_width=True)

# ======================
# ANALISIS GLOBAL
# ======================
st.subheader("📈 Analisis Keseluruhan")

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
else:
    st.warning("Belum ada data")

# ======================
# PIE CHART PER SISWA
# ======================
st.subheader("📊 Statistik Keterlambatan Siswa")

if not df.empty:
    nama_list = df["nama"].unique()
    nama_pilih = st.selectbox("Pilih Nama Siswa", nama_list)

    if st.button("Lihat Statistik"):
        data_siswa = df[df["nama"] == nama_pilih]

        tepat = len(data_siswa[data_siswa["status"] == "Tepat Waktu"])
        telat = len(data_siswa[data_siswa["status"] == "Telat"])

        if tepat + telat > 0:
            pie_data = pd.DataFrame({
                "Status": ["Tepat Waktu", "Telat"],
                "Jumlah": [tepat, telat]
            })

            st.write(f"Statistik untuk: **{nama_pilih}**")

            # PIE CHART FIX
            fig, ax = plt.subplots()
            ax.pie(
                pie_data["Jumlah"],
                labels=pie_data["Status"],
                autopct='%1.1f%%',
                startangle=90
            )
            ax.set_title("Persentase Pembayaran")

            st.pyplot(fig)
        else:
            st.warning("Belum ada data untuk siswa ini")
else:
    st.warning("Belum ada data")

# ======================
# FOOTER
# ======================
st.write("© Project Uang Kas")
