import streamlit as st 
import pandas as pd
import sqlite3
import hashlib
import io

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

st.set_page_config(layout="wide")

DEV_USER = "developer"
DEV_PASS = "kaskita"

# ======================
# FORMAT
# ======================
def format_rupiah(angka):
    return "Rp.{:,.0f}".format(angka).replace(",", ".")

def clean_nominal(n):
    if not n:
        return 0
    n = str(n).lower().replace("rp", "").replace(".", "").replace(",", "")
    return int(n) if n.isdigit() else 0

# ======================
# DB
# ======================
def init_db():
    conn = sqlite3.connect("kas.db", check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS kas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT,
        tanggal TEXT,
        status TEXT,
        kelas TEXT,
        jurusan TEXT,
        keterangan TEXT,
        nominal INTEGER
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        email TEXT,
        kelas TEXT,
        jurusan TEXT
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS pengeluaran (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tanggal TEXT,
        kelas TEXT,
        jurusan TEXT,
        keterangan TEXT,
        nominal INTEGER
    )''')

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
# LOGO
# ======================
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("logo.png", use_container_width=True)

# ======================
# ROLE
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
# LOGIN
# ======================
elif not st.session_state.login:

    st.title("Login")

    # ADMIN
    if st.session_state.role == "admin":

        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        kelas = st.selectbox("Kelas", ["10","11","12"])
        jurusan = st.text_input("Jurusan")

        if st.button("Login"):
            st.session_state.login = True
            st.session_state.kelas = kelas
            st.session_state.jurusan = jurusan.upper()
            st.rerun()

    # DEV
    elif st.session_state.role == "dev":

        user = st.text_input("Username Developer")
        pw = st.text_input("Password Developer", type="password")

        if st.button("Login Developer"):
            if user == DEV_USER and pw == DEV_PASS:
                st.session_state.login = True
                st.session_state.role = "dev"
                st.rerun()
            else:
                st.error("Login gagal")

# ======================
# MAIN APP
# ======================
else:

    st.title("📊 Dashboard KAS")

    # ================= USER =================
    if st.session_state.role == "user":

        df = pd.read_sql("SELECT * FROM kas", conn)

        if not df.empty:
            df["tanggal"] = pd.to_datetime(df["tanggal"])
            df["bulan"] = df["tanggal"].dt.strftime("%B %Y")
            df["tanggal"] = df["tanggal"].dt.strftime("%Y-%m-%d")

            col1, col2, col3 = st.columns(3)

            with col1:
                fk = st.selectbox("Kelas", sorted(df["kelas"].unique()))
            with col2:
                fj = st.selectbox("Jurusan", sorted(df["jurusan"].unique()))
            with col3:
                fb = st.selectbox("Bulan", sorted(df["bulan"].unique()))

            df = df[
                (df["kelas"] == fk) &
                (df["jurusan"] == fj) &
                (df["bulan"] == fb)
            ]

            st.metric("Total Kas", format_rupiah(df["nominal"].sum()))
            st.dataframe(df)

    # ================= DEVELOPER =================
    elif st.session_state.role == "dev":

        st.subheader("Developer Panel")

        st.dataframe(pd.read_sql("SELECT * FROM admin", conn))

        idd = st.number_input("Hapus Akun ID", step=1)
        if st.button("Hapus"):
            cursor.execute("DELETE FROM admin WHERE id=?", (idd,))
            conn.commit()
            st.rerun()

        st.dataframe(pd.read_sql("SELECT * FROM kas", conn))

    # ================= ADMIN =================
    elif st.session_state.role == "admin":

        st.success(f"{st.session_state.kelas} - {st.session_state.jurusan}")

        colA, colB = st.columns(2)

        with colA:
            if st.button("Dashboard"):
                st.session_state.menu = "dashboard"
                st.rerun()

        with colB:
            if st.button("Pengeluaran"):
                st.session_state.menu = "pengeluaran"
                st.rerun()

        # ================= DASHBOARD =================
        if st.session_state.menu == "dashboard":

            nama = st.text_input("Nama")
            tgl = st.date_input("Tanggal")
            status = st.selectbox("Status", ["Tepat Waktu","Telat"])
            ket = st.text_input("Keterangan")
            nom = st.text_input("Nominal")

            if st.button("Simpan"):
                cursor.execute("INSERT INTO kas VALUES (NULL,?,?,?,?,?,?,?)",
                               (nama,tgl.strftime("%Y-%m-%d"),status,
                                st.session_state.kelas,
                                st.session_state.jurusan,
                                ket,
                                clean_nominal(nom)))
                conn.commit()
                st.rerun()

            # ================= STATISTIK =================
            df = pd.read_sql("SELECT * FROM kas WHERE kelas=? AND jurusan=?",
                             conn, params=(st.session_state.kelas, st.session_state.jurusan))

            if not df.empty:
                st.subheader("Statistik")

                st.metric("Total Kas", format_rupiah(df["nominal"].sum()))

        # ================= PENGELUARAN (FIX SALDO) =================
        elif st.session_state.menu == "pengeluaran":

            tgl = st.date_input("Tanggal")
            ket = st.text_input("Keterangan")
            nom = st.text_input("Nominal")

            if st.button("Simpan"):
                cursor.execute("INSERT INTO pengeluaran VALUES (NULL,?,?,?,?,?)",
                               (tgl.strftime("%Y-%m-%d"),
                                st.session_state.kelas,
                                st.session_state.jurusan,
                                ket,
                                clean_nominal(nom)))
                conn.commit()

            # ================= SALDO (FIXED) =================
            df_masuk = pd.read_sql("SELECT nominal FROM kas WHERE kelas=? AND jurusan=?",
                                   conn, params=(st.session_state.kelas, st.session_state.jurusan))

            df_keluar = pd.read_sql("SELECT nominal FROM pengeluaran WHERE kelas=? AND jurusan=?",
                                    conn, params=(st.session_state.kelas, st.session_state.jurusan))

            total_masuk = df_masuk["nominal"].sum() if not df_masuk.empty else 0
            total_keluar = df_keluar["nominal"].sum() if not df_keluar.empty else 0
            saldo = total_masuk - total_keluar

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Kas", format_rupiah(total_masuk))
            col2.metric("Total Pengeluaran", format_rupiah(total_keluar))
            col3.metric("Saldo", format_rupiah(saldo))

st.write("© kaskita 2026")
