import streamlit as st 
import pandas as pd
import sqlite3
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
    try:
        return "Rp.{:,.0f}".format(float(angka)).replace(",", ".")
    except:
        return "Rp.0"

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

    if df.empty:
        df = pd.DataFrame({"Info": ["Tidak ada data"]})

    data = [df.columns.tolist()] + df.astype(str).values.tolist()

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

    cursor.execute("PRAGMA journal_mode=WAL;")

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
    return conn

conn = init_db()

# ======================
# SAFE QUERY
# ======================
def safe_read_sql(query, params=()):
    try:
        return pd.read_sql(query, conn, params=params)
    except:
        return pd.DataFrame()

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

    if st.session_state.role == "admin":

        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        kelas = st.selectbox("Kelas", ["10","11","12"])
        jurusan = st.text_input("Jurusan")

        if st.button("Login Admin"):
            if jurusan:
                st.session_state.login = True
                st.session_state.kelas = kelas
                st.session_state.jurusan = jurusan.upper()
                st.rerun()
            else:
                st.warning("Jurusan wajib diisi")

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

        df = safe_read_sql("SELECT * FROM kas")

        if not df.empty:
            df["tanggal"] = pd.to_datetime(df["tanggal"], errors='coerce')
            df["bulan"] = df["tanggal"].dt.strftime("%B %Y")
            df["tanggal"] = df["tanggal"].dt.strftime("%Y-%m-%d")

            col1, col2, col3 = st.columns(3)

            with col1:
                fk = st.selectbox("Kelas", sorted(df["kelas"].dropna().unique()))
            with col2:
                fj = st.selectbox("Jurusan", sorted(df["jurusan"].dropna().unique()))
            with col3:
                fb = st.selectbox("Bulan", sorted(df["bulan"].dropna().unique()))

            df = df[
                (df["kelas"] == fk) &
                (df["jurusan"] == fj) &
                (df["bulan"] == fb)
            ]

            st.metric("Total Kas", format_rupiah(df["nominal"].sum()))
            st.dataframe(df)

            st.download_button("⬇️ Download PDF", generate_pdf(df), "user_kas.pdf")

        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

    # ================= DEVELOPER =================
    elif st.session_state.role == "dev":

        st.subheader("🛠️ Developer Panel")

        df_admin = safe_read_sql("SELECT * FROM admin")
        df_kas = safe_read_sql("SELECT * FROM kas")

        st.subheader("👤 Data Akun Admin")
        st.dataframe(df_admin)
        st.download_button("⬇️ Download PDF Akun", generate_pdf(df_admin), "akun_admin.pdf")

        if not df_admin.empty:
            id_del = st.number_input("Hapus ID Akun", min_value=1, step=1)
            if st.button("Hapus Akun"):
                conn.execute("DELETE FROM admin WHERE id=?", (id_del,))
                conn.commit()
                st.rerun()

        st.subheader("📊 Semua Data Kas")
        st.dataframe(df_kas)
        st.download_button("⬇️ Download PDF Kas", generate_pdf(df_kas), "kas_all.pdf")

        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

    # ================= ADMIN =================
    elif st.session_state.role == "admin":

        if not st.session_state.kelas or not st.session_state.jurusan:
            st.error("Session tidak valid, silakan login ulang")
            if st.button("Kembali"):
                st.session_state.clear()
                st.rerun()
            st.stop()

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

        # DASHBOARD
        if st.session_state.menu == "dashboard":

            st.subheader("➕ Input Pembayaran")

            nama = st.text_input("Nama")
            tgl = st.date_input("Tanggal")
            status = st.selectbox("Status", ["Tepat Waktu","Telat"])
            ket = st.text_input("Keterangan")
            nom = st.text_input("Nominal")

            if st.button("Simpan"):
                if nama and nom:
                    conn.execute(
                        "INSERT INTO kas VALUES (NULL,?,?,?,?,?,?,?)",
                        (nama, tgl.strftime("%Y-%m-%d"), status,
                         st.session_state.kelas,
                         st.session_state.jurusan,
                         ket,
                         clean_nominal(nom))
                    )
                    conn.commit()
                    st.rerun()

            df = safe_read_sql(
                "SELECT * FROM kas WHERE kelas=? AND jurusan=?",
                (st.session_state.kelas, st.session_state.jurusan)
            )

            if not df.empty:

                st.metric("Total Kas", format_rupiah(df["nominal"].sum()))
                st.bar_chart(df["status"].value_counts())

                st.dataframe(df)
                st.download_button("⬇️ Download PDF Kas", generate_pdf(df), "kas_admin.pdf")

                st.subheader("📊 Cek Statistik Per Siswa")
                siswa = st.selectbox("Pilih Siswa", sorted(df["nama"].unique()))

                if st.button("Cek Statistik"):
                    data = df[df["nama"] == siswa]
                    st.bar_chart(data["status"].value_counts())

        # PENGELUARAN
        elif st.session_state.menu == "pengeluaran":

            tgl = st.date_input("Tanggal")
            ket = st.text_input("Keterangan")
            nom = st.text_input("Nominal")

            if st.button("Simpan"):
                if nom:
                    conn.execute(
                        "INSERT INTO pengeluaran VALUES (NULL,?,?,?,?,?)",
                        (tgl.strftime("%Y-%m-%d"),
                         st.session_state.kelas,
                         st.session_state.jurusan,
                         ket,
                         clean_nominal(nom))
                    )
                    conn.commit()

            df_keluar = safe_read_sql(
                "SELECT * FROM pengeluaran WHERE kelas=? AND jurusan=?",
                (st.session_state.kelas, st.session_state.jurusan)
            )

            st.dataframe(df_keluar)
            st.download_button("⬇️ Download PDF Pengeluaran", generate_pdf(df_keluar), "pengeluaran.pdf")

        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

st.write("© kaskita 2026")
