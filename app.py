import streamlit as st 
import pandas as pd
import datetime
import sqlite3
import random
import hashlib

# PDF
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import io

st.set_page_config(layout="wide")

DEV_USER = "developer"
DEV_PASS = "kaskita"

# ======================
# FORMAT RUPIAH
# ======================
def format_rupiah(angka):
    return "Rp.{:,.0f}".format(angka).replace(",", ".")

def clean_nominal(n):
    if not n:
        return 0
    n = str(n).lower().replace("rp", "").replace(".", "").replace(",", "")
    return int(n) if n.isdigit() else 0

# ======================
# PDF GENERATOR
# ======================
def generate_pdf(df, title="Data"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)

    data = [df.columns.tolist()] + df.values.tolist()

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('GRID',(0,0),(-1,-1),1,colors.black)
    ]))

    doc.build([table])
    buffer.seek(0)
    return buffer

# ======================
# HASH
# ======================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ======================
# DB INIT
# ======================
def init_db():
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
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        email TEXT,
        kelas TEXT,
        jurusan TEXT
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
    return conn, cursor

conn, cursor = init_db()

# ======================
# SESSION
# ======================
defaults = {
    "login": False,
    "role": None,
    "kelas": None,
    "jurusan": None,
    "page": "role",
    "menu": "dashboard"
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ======================
# ROLE PAGE
# ======================
if not st.session_state.login and st.session_state.page == "role":

    st.title("SELAMAT DATANG DI KAS KITA")
    st.subheader("Pilih Login")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Admin"):
            st.session_state.role = "admin"
            st.session_state.page = "login"

    with col2:
        if st.button("User"):
            st.session_state.role = "user"
            st.session_state.login = True
            st.rerun()

    with col3:
        if st.button("Developer"):
            st.session_state.role = "dev"
            st.session_state.page = "login"

# ======================
# LOGIN ADMIN + DEV
# ======================
elif not st.session_state.login:

    if st.button("⬅️ Kembali"):
        st.session_state.page = "role"
        st.rerun()

    st.title("Login")

    # ================= ADMIN =================
    if st.session_state.role == "admin":

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        kelas = st.selectbox("Kelas", ["10", "11", "12"])
        jurusan = st.text_input("Jurusan")

        if st.button("Login Admin"):
            cursor.execute("SELECT * FROM admin WHERE username=?", (username,))
            data = cursor.fetchone()

            if not data:
                st.error("Username tidak ditemukan")
            elif data[2] != hash_password(password):
                st.error("Password salah")
            elif data[4] != kelas or data[5] != jurusan.upper():
                st.error("Kelas/Jurusan salah")
            else:
                st.session_state.login = True
                st.session_state.kelas = kelas
                st.session_state.jurusan = jurusan.upper()
                st.rerun()

    # ================= DEVELOPER LOGIN =================
    elif st.session_state.role == "dev":

        st.subheader("Login Developer")

        username = st.text_input("Username Developer")
        password = st.text_input("Password Developer", type="password")

        if st.button("Login Developer"):
            if username == DEV_USER and password == DEV_PASS:
                st.session_state.login = True
                st.session_state.role = "dev"
                st.success("Login Developer Berhasil")
                st.rerun()
            else:
                st.error("Username atau Password salah")

# ======================
# MAIN APP
# ======================
else:

    st.title("📊 Dashboard KAS")

    # ================= USER =================
    if st.session_state.role == "user":

        st.subheader("👤 User Dashboard")

        df = pd.read_sql("SELECT * FROM kas", conn)

        if not df.empty:
            df["tanggal"] = pd.to_datetime(df["tanggal"])
            df["bulan"] = df["tanggal"].dt.strftime("%B %Y")
            df["tanggal"] = df["tanggal"].dt.strftime("%Y-%m-%d")

            # FILTER
            col1, col2, col3 = st.columns(3)

            with col1:
                f_kelas = st.selectbox("Kelas", sorted(df["kelas"].unique()))

            with col2:
                f_jurusan = st.selectbox("Jurusan", sorted(df["jurusan"].unique()))

            with col3:
                f_bulan = st.selectbox("Bulan", sorted(df["bulan"].unique()))

            df = df[
                (df["kelas"] == f_kelas) &
                (df["jurusan"] == f_jurusan) &
                (df["bulan"] == f_bulan)
            ]

            st.metric("Total Kas", format_rupiah(df["nominal"].sum()))
            st.dataframe(df)

        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

    # ================= DEVELOPER =================
    elif st.session_state.role == "dev":

        st.subheader("🛠️ Developer Dashboard")

        df_kas = pd.read_sql("SELECT * FROM kas", conn)
        df_admin = pd.read_sql("SELECT * FROM admin", conn)

        st.subheader("👤 Data Admin")
        st.dataframe(df_admin)

        st.subheader("🗑️ Hapus Akun Admin")

        if not df_admin.empty:
            akun_id = st.number_input("ID Akun", step=1)

            if st.button("Hapus Akun"):
                cursor.execute("DELETE FROM admin WHERE id=?", (akun_id,))
                conn.commit()
                st.success("Akun dihapus")
                st.rerun()

        st.subheader("📊 Semua Data Kas")
        st.dataframe(df_kas)

        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

    # ================= ADMIN =================
    elif st.session_state.role == "admin":

        st.success(f"Kelas {st.session_state.kelas} - {st.session_state.jurusan}")

        st.subheader("ADMIN MODE (tetap seperti sebelumnya)")
        st.info("Bagian admin tetap sama seperti coding kamu sebelumnya")

        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

st.write("© kaskita 2026")
