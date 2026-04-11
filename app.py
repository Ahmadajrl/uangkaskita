import streamlit as st 
import pandas as pd
import datetime
import sqlite3
import hashlib
import io

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

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
# PDF
# ======================
def generate_pdf(df):
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
# DB
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
# LOGO
# ======================
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("logo.png", use_container_width=True)

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
# LOGIN
# ======================
elif not st.session_state.login:

    if st.button("⬅️ Kembali"):
        st.session_state.page = "role"
        st.rerun()

    st.title("Login")

    # ================= ADMIN LOGIN =================
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
            else:
                st.session_state.login = True
                st.session_state.kelas = kelas
                st.session_state.jurusan = jurusan.upper()
                st.rerun()

    # ================= DEV LOGIN =================
    elif st.session_state.role == "dev":

        username = st.text_input("Username Developer")
        password = st.text_input("Password Developer", type="password")

        if st.button("Login Developer"):
            if username == DEV_USER and password == DEV_PASS:
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

        st.subheader("🛠️ Developer")

        df_admin = pd.read_sql("SELECT * FROM admin", conn)
        df_kas = pd.read_sql("SELECT * FROM kas", conn)

        st.subheader("👤 Data Akun")
        st.dataframe(df_admin)

        if not df_admin.empty:
            id_del = st.number_input("Hapus ID Akun", step=1)
            if st.button("Hapus Akun"):
                cursor.execute("DELETE FROM admin WHERE id=?", (id_del,))
                conn.commit()
                st.success("Akun dihapus")
                st.rerun()

        st.subheader("📊 Semua Data Kas")
        st.dataframe(df_kas)

        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

    # ================= ADMIN (FULL RESTORE + STATISTIK + HAPUS) =================
    elif st.session_state.role == "admin":

        st.success(f"Kelas {st.session_state.kelas} - {st.session_state.jurusan}")

        colA, colB = st.columns(2)

        with colA:
            if st.button("📊 Dashboard"):
                st.session_state.menu = "dashboard"
                st.rerun()

        with colB:
            if st.button("💸 Pengeluaran"):
                st.session_state.menu = "pengeluaran"
                st.rerun()

        # ================= DASHBOARD =================
        if st.session_state.menu == "dashboard":

            st.subheader("➕ Input Pembayaran")

            nama = st.text_input("Nama")
            tanggal = st.date_input("Tanggal")
            status = st.selectbox("Status", ["Tepat Waktu", "Telat"])
            keterangan = st.text_input("Keterangan")
            nominal = st.text_input("Nominal")

            if st.button("Simpan"):
                nilai = clean_nominal(nominal)

                cursor.execute(
                    "INSERT INTO kas VALUES (NULL,?,?,?,?,?,?,?)",
                    (nama, tanggal.strftime("%Y-%m-%d"), status,
                     st.session_state.kelas,
                     st.session_state.jurusan,
                     keterangan,
                     nilai)
                )
                conn.commit()
                st.success("Data tersimpan")
                st.rerun()

            df = pd.read_sql(
                "SELECT * FROM kas WHERE kelas=? AND jurusan=?",
                conn,
                params=(st.session_state.kelas, st.session_state.jurusan)
            )

            if not df.empty:
                df["tanggal"] = pd.to_datetime(df["tanggal"])
                df["bulan"] = df["tanggal"].dt.strftime("%B %Y")
                df["tanggal"] = df["tanggal"].dt.strftime("%Y-%m-%d")

                # ================= STATISTIK =================
                st.subheader("📈 Statistik")

                tepat = len(df[df["status"] == "Tepat Waktu"])
                telat = len(df[df["status"] == "Telat"])

                col1, col2 = st.columns(2)
                col1.metric("Tepat Waktu", tepat)
                col2.metric("Telat", telat)

                st.bar_chart(df["status"].value_counts())

                st.metric("Total Kas", format_rupiah(df["nominal"].sum()))

            # ================= HAPUS DATA =================
            st.subheader("🗑️ Hapus Data")
            konfirmasi = st.checkbox("Konfirmasi")

            col1, col2, col3 = st.columns(3)

            with col1:
                id_hapus = st.number_input("Hapus ID", step=1)
                if st.button("Hapus ID") and konfirmasi:
                    cursor.execute("DELETE FROM kas WHERE id=?", (id_hapus,))
                    conn.commit()
                    st.rerun()

            with col2:
                if not df.empty:
                    siswa = st.selectbox("Hapus Siswa", df["nama"].unique())
                    if st.button("Hapus Siswa") and konfirmasi:
                        cursor.execute("DELETE FROM kas WHERE nama=?", (siswa,))
                        conn.commit()
                        st.rerun()

            with col3:
                if st.button("Hapus Semua") and konfirmasi:
                    cursor.execute("DELETE FROM kas WHERE kelas=? AND jurusan=?",
                                   (st.session_state.kelas, st.session_state.jurusan))
                    conn.commit()
                    st.rerun()

        # ================= PENGELUARAN =================
        elif st.session_state.menu == "pengeluaran":

            st.subheader("💸 Input Pengeluaran")

            tgl = st.date_input("Tanggal")
            ket = st.text_input("Keterangan")
            nominal = st.text_input("Nominal")

            if st.button("Simpan"):
                nilai = clean_nominal(nominal)

                cursor.execute(
                    "INSERT INTO pengeluaran VALUES (NULL,?,?,?,?,?)",
                    (tgl.strftime("%Y-%m-%d"),
                     st.session_state.kelas,
                     st.session_state.jurusan,
                     ket,
                     nilai)
                )
                conn.commit()

        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

st.write("© kaskita 2026")
