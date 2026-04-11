import streamlit as st
import pandas as pd
import datetime
import base64

# ======================
# CONFIG
# ======================
st.set_page_config(layout="wide")

# ======================
# CSS
# ======================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #01023B;
    color: white;
}
label, p {
    color: white !important;
}
.stButton > button {
    background-color: #09F289;
    color: black;
    font-weight: bold;
    border-radius: 10px;
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
    pass

# ======================
# DATABASE (PAKAI SQLITE AGAR AMAN CLOUD)
# ======================
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

# ======================
# HEADER
# ======================
st.title("📊 Aplikasi Uang Kas Siswa")

# ======================
# INPUT
# ======================
st.subheader("➕ Input Pembayaran")

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
# DATA
# ======================
df = pd.read_sql("SELECT * FROM kas", conn)

st.subheader("📋 Data Pembayaran")
st.dataframe(df, use_container_width=True)

# ======================
# ANALISIS GLOBAL
# ======================
st.subheader("📈 Analisis Keseluruhan")

if not df.empty:
    chart_data = df["status"].value_counts().reset_index()
    chart_data.columns = ["Status", "Jumlah"]

    st.bar_chart(chart_data.set_index("Status"))
else:
    st.warning("Belum ada data")

# ======================
# PIE PER SISWA (TANPA MATPLOTLIB)
# ======================
st.subheader("📊 Statistik Keterlambatan Siswa")

if not df.empty:
    nama_list = df["nama"].unique()
    nama_pilih = st.selectbox("Pilih Nama Siswa", nama_list)

    if st.button("Lihat Statistik"):
        data_siswa = df[df["nama"] == nama_pilih]

        if not data_siswa.empty:
            pie_data = data_siswa["status"].value_counts().reset_index()
            pie_data.columns = ["Status", "Jumlah"]

            st.write(f"Statistik untuk: **{nama_pilih}**")

            # PIE CHART BAWAAN STREAMLIT
            st.plotly_chart({
                "data": [{
                    "labels": pie_data["Status"],
                    "values": pie_data["Jumlah"],
                    "type": "pie"
                }]
            })
        else:
            st.warning("Belum ada data untuk siswa ini")
else:
    st.warning("Belum ada data")

# ======================
# FOOTER
# ======================
st.write("© Project Uang Kas")
