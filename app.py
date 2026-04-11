import streamlit as st
import pandas as pd
import datetime
import sqlite3
import hashlib
import re

# ======================
# CONFIG
# ======================
st.set_page_config(layout="wide")

DEV_USER = "developer"
DEV_PASS = "kaskita"

# ======================
# HASH
# ======================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ======================
# FORMAT RUPIAH
# ======================
def format_rupiah(angka):
    return "Rp.{:,.0f}".format(angka).replace(",", ".")

# ======================
# PARSE NOMINAL (FLEKSIBEL)
# ======================
def parse_nominal(nominal_str):
    if nominal_str:
        angka = re.sub(r'[^0-9]', '', nominal_str)
        return int(angka) if angka else 0
    return 0

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
    "page": "role"
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ======================
# PILIH ROLE
# ======================
if not st.session_state.login and st.session_state.page == "role":

    st.title("KAS KITA")
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

    if st.session_state.role == "admin":

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        kelas = st.selectbox("Kelas", ["10", "11", "12"])
        jurusan = st.text_input("Jurusan")

        if st.button("Login"):
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

    elif st.session_state.role == "dev":
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")

        if st.button("Login Developer"):
            if user == DEV_USER and pw == DEV_PASS:
                st.session_state.login = True
                st.rerun()
            else:
                st.error("Login gagal")

# ======================
# MAIN APP
# ======================
else:

    st.title("📊 Dashboard KAS")

    # ================= ADMIN =================
    if st.session_state.role == "admin":

        st.success(f"Kelas {st.session_state.kelas} - {st.session_state.jurusan}")

        # ================= INPUT =================
        st.subheader("➕ Input Pembayaran")

        nama = st.text_input("Nama Siswa")
        tanggal = st.date_input("Tanggal", datetime.date.today())
        status = st.selectbox("Status", ["Tepat Waktu", "Telat"])
        keterangan = st.text_input("Keterangan (contoh: Lunas)")
        nominal_input = st.text_input("Masukan Nominal Kas (bebas format)")

        if st.button("Simpan"):
            if nama:
                nominal = parse_nominal(nominal_input)

                cursor.execute(
                    "INSERT INTO kas VALUES (NULL,?,?,?,?,?,?,?)",
                    (nama, str(tanggal), status,
                     st.session_state.kelas,
                     st.session_state.jurusan,
                     keterangan,
                     nominal)
                )
                conn.commit()
                st.success("Data tersimpan")
                st.rerun()
            else:
                st.warning("Nama tidak boleh kosong")

        # ================= DATA =================
        df = pd.read_sql(
            "SELECT * FROM kas WHERE kelas=? AND jurusan=?",
            conn,
            params=(st.session_state.kelas, st.session_state.jurusan)
        )

        st.subheader("📋 Data Siswa")
        st.dataframe(df, use_container_width=True)

        # ================= TOTAL KAS =================
        total_kas = df["nominal"].sum() if not df.empty else 0
        st.subheader("💰 Total Kas")
        st.success(format_rupiah(total_kas))

        # ================= HAPUS DATA =================
        st.subheader("🗑️ Hapus Data")

        konfirmasi = st.checkbox("Saya yakin ingin menghapus data")

        col1, col2, col3 = st.columns(3)

        # Hapus ID
        with col1:
            id_hapus = st.number_input("Hapus berdasarkan ID", step=1)
            if st.button("Hapus ID") and konfirmasi:
                cursor.execute("DELETE FROM kas WHERE id=?", (id_hapus,))
                conn.commit()
                st.success("Data dihapus")
                st.rerun()

        # Hapus per siswa
        with col2:
            if not df.empty:
                siswa = st.selectbox("Pilih siswa", df["nama"].unique())
                if st.button("Hapus Siswa") and konfirmasi:
                    cursor.execute(
                        "DELETE FROM kas WHERE nama=? AND kelas=? AND jurusan=?",
                        (siswa,
                         st.session_state.kelas,
                         st.session_state.jurusan)
                    )
                    conn.commit()
                    st.success("Data siswa dihapus")
                    st.rerun()

        # Hapus semua
        with col3:
            if st.button("Hapus Semua Data") and konfirmasi:
                cursor.execute(
                    "DELETE FROM kas WHERE kelas=? AND jurusan=?",
                    (st.session_state.kelas,
                     st.session_state.jurusan)
                )
                conn.commit()
                st.success("Semua data dihapus")
                st.rerun()

        # ================= ANALISIS =================
        st.subheader("📈 Analisis")

        if not df.empty:
            st.bar_chart(df["status"].value_counts())
        else:
            st.info("Belum ada data")

        # ================= CEK PERFORMA SISWA =================
        st.subheader("📊 Cek Performa Siswa")

        if not df.empty:
            siswa = st.selectbox("Pilih Siswa", df["nama"].unique())

            if st.button("Cek Performa"):
                data_siswa = df[df["nama"] == siswa]

                hasil = data_siswa["status"].value_counts()

                st.bar_chart(hasil)

                total = len(data_siswa)
                telat = len(data_siswa[data_siswa["status"] == "Telat"])

                persen = (telat / total) * 100 if total > 0 else 0

                if persen < 20:
                    st.success("Siswa disiplin 👍")
                elif persen < 50:
                    st.warning("Perlu perhatian ⚠️")
                else:
                    st.error("Sering telat ❌")

    # ================= USER =================
    elif st.session_state.role == "user":
        st.info("Mode User")
        df = pd.read_sql("SELECT * FROM kas", conn)
        st.dataframe(df)

    # ================= DEV =================
    elif st.session_state.role == "dev":
        st.warning("Developer Mode")

        st.subheader("Semua Data Kas")
        st.dataframe(pd.read_sql("SELECT * FROM kas", conn))

        st.subheader("Data Admin")
        st.dataframe(pd.read_sql("SELECT * FROM admin", conn))

    # ================= LOGOUT =================
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

st.write("© kaskita 2026")
