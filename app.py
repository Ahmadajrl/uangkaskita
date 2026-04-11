import streamlit as st
import pandas as pd
import datetime
import sqlite3
import random
import hashlib

# ======================
# CONFIG
# ======================
st.set_page_config(layout="wide")

# ======================
# DEV LOGIN
# ======================
DEV_USER = "developer"
DEV_PASS = "kaskita"

# ======================
# HASH
# ======================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

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
        jurusan TEXT
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
    "otp": None,
    "reset_mode": False,
    "page": "role"
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ======================
# HALAMAN PILIH ROLE
# ======================
if not st.session_state.login and st.session_state.page == "role":

    st.title("🚀 Selamat Datang di KAS KITA")
    st.subheader("Pilih Login Sebagai")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("👨‍💼 Admin"):
            st.session_state.role = "admin"
            st.session_state.page = "login"

    with col2:
        if st.button("👤 User"):
            st.session_state.role = "user"
            st.session_state.login = True
            st.rerun()

    with col3:
        if st.button("🧑‍💻 Developer"):
            st.session_state.role = "dev"
            st.session_state.page = "login"

# ======================
# HALAMAN LOGIN
# ======================
elif not st.session_state.login and st.session_state.page == "login":

    # 🔙 TOMBOL KEMBALI
    if st.button("⬅️ Kembali"):
        st.session_state.page = "role"
        st.session_state.role = None
        st.rerun()

    st.title("🔐 Login")

    # ================= ADMIN =================
    if st.session_state.role == "admin":

        menu = st.radio("Menu", ["Login", "Register", "Lupa Password"])

        # LOGIN
        if menu == "Login":
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
                    st.session_state.reset_mode = True
                elif data[4] != kelas or data[5] != jurusan.upper():
                    st.error("Kelas/Jurusan salah")
                else:
                    st.session_state.login = True
                    st.session_state.kelas = kelas
                    st.session_state.jurusan = jurusan.upper()
                    st.rerun()

            if st.session_state.reset_mode:
                if st.button("Lupa Password?"):
                    st.session_state.page = "reset"

        # REGISTER
        elif menu == "Register":
            user = st.text_input("Username")
            pw = st.text_input("Password", type="password")
            email = st.text_input("Email")
            kelas = st.selectbox("Kelas", ["10", "11", "12"])
            jurusan = st.text_input("Jurusan")

            if st.button("Daftar"):
                cursor.execute(
                    "SELECT * FROM admin WHERE kelas=? AND jurusan=?",
                    (kelas, jurusan.upper())
                )
                if cursor.fetchone():
                    st.error("Admin sudah ada")
                else:
                    cursor.execute(
                        "INSERT INTO admin VALUES (NULL,?,?,?,?,?)",
                        (user, hash_password(pw), email, kelas, jurusan.upper())
                    )
                    conn.commit()
                    st.success("Berhasil daftar")

    # ================= DEVELOPER =================
    elif st.session_state.role == "dev":

        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")

        if st.button("Login Developer"):
            if user == DEV_USER and pw == DEV_PASS:
                st.session_state.login = True
                st.rerun()
            else:
                st.error("Login developer gagal")

# ======================
# RESET PASSWORD PAGE
# ======================
elif st.session_state.page == "reset":

    # 🔙 TOMBOL KEMBALI
    if st.button("⬅️ Kembali"):
        st.session_state.page = "login"
        st.rerun()

    st.title("🔁 Reset Password")

    email = st.text_input("Email")

    if st.button("Kirim OTP"):
        cursor.execute("SELECT * FROM admin WHERE email=?", (email,))
        if cursor.fetchone():
            otp = str(random.randint(1000, 9999))
            st.session_state.otp = otp
            st.success(f"OTP: {otp}")
        else:
            st.error("Email tidak ditemukan")

    otp_input = st.text_input("Masukkan OTP")
    new_pw = st.text_input("Password Baru", type="password")

    if st.button("Reset"):
        if otp_input == st.session_state.otp:
            cursor.execute(
                "UPDATE admin SET password=? WHERE email=?",
                (hash_password(new_pw), email)
            )
            conn.commit()
            st.success("Password berhasil diubah")
            st.session_state.page = "login"
        else:
            st.error("OTP salah")

# ======================
# MAIN APP
# ======================
elif st.session_state.login:

    st.title("📊 KAS KITA")

    if st.session_state.role == "admin":
        st.success(f"Admin {st.session_state.kelas}-{st.session_state.jurusan}")

        nama = st.text_input("Nama")
        tanggal = st.date_input("Tanggal", datetime.date.today())
        status = st.selectbox("Status", ["Tepat Waktu", "Telat"])

        if st.button("Simpan"):
            cursor.execute(
                "INSERT INTO kas VALUES (NULL,?,?,?,?,?)",
                (nama, str(tanggal), status,
                 st.session_state.kelas,
                 st.session_state.jurusan)
            )
            conn.commit()
            st.rerun()

        df = pd.read_sql(
            "SELECT * FROM kas WHERE kelas=? AND jurusan=?",
            conn,
            params=(st.session_state.kelas, st.session_state.jurusan)
        )
        st.dataframe(df)

    elif st.session_state.role == "user":
        st.info("User Mode")
        df = pd.read_sql("SELECT * FROM kas", conn)
        st.dataframe(df)

    elif st.session_state.role == "dev":
        st.warning("Developer Mode")

        df = pd.read_sql("SELECT * FROM kas", conn)
        st.dataframe(df)

        admin_df = pd.read_sql(
            "SELECT id, username, email, kelas, jurusan FROM admin",
            conn
        )
        st.dataframe(admin_df)

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

st.write("© kaskita 2026")
