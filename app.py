import streamlit as st 
import pandas as pd
import sqlite3
import hashlib
import random
import io

# PDF
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

st.set_page_config(layout="wide")

# ================= CONFIG =================
DEV_USER = "developer"
DEV_PASS = "kaskita"

# ================= FORMAT =================
def format_rupiah(angka):
    return "Rp.{:,.0f}".format(angka).replace(",", ".")

def clean_nominal(n):
    if not n:
        return 0
    n = str(n).lower().replace("rp", "").replace(".", "").replace(",", "")
    return int(n) if n.isdigit() else 0

# ================= HASH =================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ================= PDF =================
def generate_pdf(df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)

    data = [df.columns.tolist()] + df.values.tolist()

    table = Table(data)
    table.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),1,colors.black)
    ]))

    doc.build([table])
    buffer.seek(0)
    return buffer

# ================= DB =================
conn = sqlite3.connect("kas.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS kas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT,
    tanggal TEXT,
    status TEXT,
    kelas TEXT,
    jurusan TEXT,
    keterangan TEXT,
    nominal INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS pengeluaran (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT,
    kelas TEXT,
    jurusan TEXT,
    keterangan TEXT,
    nominal INTEGER
)
''')

conn.commit()

# ================= SESSION =================
if "login" not in st.session_state:
    st.session_state.login = False
if "role" not in st.session_state:
    st.session_state.role = None
if "menu" not in st.session_state:
    st.session_state.menu = "dashboard"
# ======================
# LOGO
# ======================
col_logo1, col_logo2, col_logo3 = st.columns([1,2,1])

with col_logo2:
    st.image("logo.png", use_container_width=True)
# ================= ROLE =================
if not st.session_state.login:

    st.title("KAS KITA")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Admin"):
            st.session_state.role = "admin"
            st.session_state.login = True
            st.rerun()

    with col2:
        if st.button("User"):
            st.session_state.role = "user"
            st.session_state.login = True
            st.rerun()

    with col3:
        if st.button("Developer"):
            st.session_state.role = "dev"
            st.session_state.login = True
            st.rerun()

# ================= MAIN =================
else:

    st.title("📊 Dashboard KAS")

    # ================= ADMIN =================
    if st.session_state.role == "admin":

        colA, colB = st.columns(2)

        with colA:
            if st.button("Dashboard"):
                st.session_state.menu = "dashboard"

        with colB:
            if st.button("Pengeluaran"):
                st.session_state.menu = "pengeluaran"

        # DASHBOARD
        if st.session_state.menu == "dashboard":

            st.subheader("Input Kas")

            nama = st.text_input("Nama")
            nominal = st.text_input("Nominal")

            if st.button("Simpan"):
                cursor.execute(
                    "INSERT INTO kas VALUES (NULL,?,?,?,?,?,?,?)",
                    (nama, "2026-01-01", "Tepat Waktu",
                     "10", "TKJ", "-", clean_nominal(nominal))
                )
                conn.commit()
                st.success("Tersimpan")

            df = pd.read_sql("SELECT * FROM kas", conn)
            if not df.empty:
                st.dataframe(df)

        # PENGELUARAN
        elif st.session_state.menu == "pengeluaran":

            st.subheader("Pengeluaran")

            ket = st.text_input("Keterangan")
            nominal = st.text_input("Nominal")

            if st.button("Simpan Pengeluaran"):
                cursor.execute(
                    "INSERT INTO pengeluaran VALUES (NULL,?,?,?,?,?)",
                    ("2026-01-01", "10", "TKJ", ket, clean_nominal(nominal))
                )
                conn.commit()
                st.success("Tersimpan")

            df_keluar = pd.read_sql("SELECT * FROM pengeluaran", conn)
            if not df_keluar.empty:
                st.dataframe(df_keluar)

    # ================= USER =================
    elif st.session_state.role == "user":

        st.subheader("Data Kas")

        df = pd.read_sql("SELECT * FROM kas", conn)

        if not df.empty:
            df["tanggal"] = pd.to_datetime(df["tanggal"])
            df["bulan"] = df["tanggal"].dt.strftime("%B %Y")

            jurusan = st.selectbox("Jurusan", df["jurusan"].unique())
            bulan = st.selectbox("Bulan", df["bulan"].unique())

            df = df[(df["jurusan"] == jurusan) & (df["bulan"] == bulan)]

            st.dataframe(df)

            pdf = generate_pdf(df)
            st.download_button("Download PDF", pdf, "kas.pdf")

        else:
            st.info("Kosong")

    # ================= DEV =================
    elif st.session_state.role == "dev":
        st.write("Developer Mode")

    # LOGOUT
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
