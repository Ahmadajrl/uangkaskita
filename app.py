import streamlit as st
import pandas as pd
import datetime
import sqlite3
import hashlib
import re
import random

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
# PARSE NOMINAL
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
    "page": "role",
    "otp": None
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
# LOGIN / REGISTER / LUPA PASSWORD
# ======================
elif not st.session_state.login:

    if st.button("Kembali"):
        st.session_state.page = "role"
        st.rerun()

    st.title("Login")

    if st.session_state.role == "admin":

        menu = st.radio("Menu", ["Login", "Register", "Lupa Password"])

        # ===== LOGIN =====
        if menu == "Login":

            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            kelas = st.selectbox("Kelas", ["10", "11", "12"])
            jurusan = st.text_input("Jurusan (contoh: TKJ 1)")

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

        # ===== REGISTER =====
        elif menu == "Register":

            st.subheader("Daftar Admin Baru")

            user = st.text_input("Username Baru")
            pw = st.text_input("Password Baru", type="password")
            email = st.text_input("Email")
            kelas = st.selectbox("Kelas", ["10", "11", "12"])
            jurusan = st.text_input("Jurusan (contoh: TKJ 1)")

            if st.button("Daftar"):

                if not user or not pw or not email or not jurusan:
                    st.warning("Semua field wajib diisi")
                else:
                    cursor.execute(
                        "SELECT * FROM admin WHERE kelas=? AND jurusan=?",
                        (kelas, jurusan.upper())
                    )

                    if cursor.fetchone():
                        st.error("Admin untuk kelas & jurusan ini sudah ada!")
                    else:
                        cursor.execute(
                            """INSERT INTO admin 
                            (username,password,email,kelas,jurusan)
                            VALUES (?,?,?,?,?)""",
                            (user,
                             hash_password(pw),
                             email,
                             kelas,
                             jurusan.upper())
                        )
                        conn.commit()
                        st.success("Akun admin berhasil dibuat!")

        # ===== LUPA PASSWORD =====
        elif menu == "Lupa Password":

            st.subheader("Reset Password")

            email = st.text_input("Masukkan Email")

            if st.button("Kirim OTP"):
                cursor.execute("SELECT * FROM admin WHERE email=?", (email,))
                if cursor.fetchone():
                    otp = str(random.randint(1000, 9999))
                    st.session_state.otp = otp
                    st.success(f"OTP (simulasi): {otp}")
                else:
                    st.error("Email tidak ditemukan")

            otp_input = st.text_input("Masukkan OTP")
            new_pw = st.text_input("Password Baru", type="password")

            if st.button("Reset Password"):
                if otp_input == st.session_state.otp:
                    cursor.execute(
                        "UPDATE admin SET password=? WHERE email=?",
                        (hash_password(new_pw), email)
                    )
                    conn.commit()
                    st.success("Password berhasil diubah")
                else:
                    st.error("OTP salah")

    # ================= DEV =================
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

    st.title("Dashboard KAS")

    if st.session_state.role == "admin":

        st.success(f"Kelas {st.session_state.kelas} - {st.session_state.jurusan}")

        st.subheader("Input Pembayaran")

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

        df = pd.read_sql(
            "SELECT * FROM kas WHERE kelas=? AND jurusan=?",
            conn,
            params=(st.session_state.kelas, st.session_state.jurusan)
        )

        st.dataframe(df, use_container_width=True)

        total_kas = df["nominal"].sum() if not df.empty else 0
        st.success(format_rupiah(total_kas))

    elif st.session_state.role == "user":
        st.dataframe(pd.read_sql("SELECT * FROM kas", conn))

    elif st.session_state.role == "dev":
        st.dataframe(pd.read_sql("SELECT * FROM kas", conn))
        st.dataframe(pd.read_sql("SELECT * FROM admin", conn))

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

st.write("© kaskita 2026")
