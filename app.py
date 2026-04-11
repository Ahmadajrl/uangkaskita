import streamlit as st 
import pandas as pd
import datetime
import base64

# ======================
# CONFIG PAGE
# ======================
st.set_page_config(layout="wide")

# ======================
# CUSTOM CSS
# ======================
st.markdown("""
<style>

/* BACKGROUND */
[data-testid="stAppViewContainer"] {
    background-color: #01023B;
    color: white;
}

/* TEXT */
label, .stMarkdown, .stText, p {
    color: white !important;
}

/* BUTTON */
.stButton > button {
    background-color: #09F289;
    color: black;
    font-weight: bold;
    border-radius: 10px;
    border: none;
    padding: 10px 20px;
}

.stButton > button:hover {
    background-color: #07c96f;
    color: white;
}

/* INPUT */
input, textarea {
    background-color: #02044F !important;
    color: white !important;
    border-radius: 8px !important;
}

/* SELECTBOX */
[data-baseweb="select"] {
    background-color: #02044F !important;
    color: white !important;
}

/* DATE */
[data-testid="stDateInput"] input {
    background-color: #02044F !important;
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# ======================
# LOGO BASE64 (TENGAH ATAS)
# ======================
def get_base64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()

try:
    img = get_base64("logo.png")

    st.markdown(f"""
    <div style="text-align:center; margin-top:10px;">
        <img src="data:image/png;base64,{img}" width="120">
    </div>
    """, unsafe_allow_html=True)
except:
    st.warning("Logo tidak ditemukan!")

# ======================
# DATABASE (AUTO SWITCH)
# ======================
try:
    import mysql.connector

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="091206",
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

# ======================
# STATISTIK PER SISWA (PIE CHART)
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

            st.pyplot(
                pie_data.set_index("Status").plot.pie(
                    y="Jumlah",
                    autopct='%1.1f%%',
                    figsize=(5,5)
                ).get_figure()
            )
        else:
            st.warning("Belum ada data untuk siswa ini")
else:
    st.warning("Belum ada data")

# ======================
# FOOTER
# ======================
st.write("© Project Uang Kas")
