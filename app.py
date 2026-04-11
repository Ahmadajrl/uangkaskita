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
# DEVELOPER LOGIN
# ======================
DEV_USER = "dev"
DEV_PASS = "dev123"

# ======================
# HASH
# ======================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ======================
# DATABASE
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
for key in ["login","role","kelas","jurusan"]:
    if key not in st.session_state:
        st.session_state[key] = None

# ======================
# LOGIN PAGE
# ======================
if not st.session_state.login:

    st.title("🔐 Login Sistem KAS")

    role = st.selectbox("Login sebagai", ["Admin", "User", "Developer"])

    # ================= ADMIN =================
    if role == "Admin":

        menu = st.radio("Menu", ["Login", "Register"])

        if menu == "Login":
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            kelas = st.selectbox("Kelas", ["10", "11", "12"])
            jurusan = st.text_input("Jurusan")

            if st.button("Login"):
                cursor.execute(
                    """SELECT * FROM admin 
                    WHERE username=? AND password=? AND kelas=? AND jurusan=?""",
                    (username.strip(),
                     hash_password(password),
                     kelas,
                     jurusan.strip().upper())
                )
                if cursor.fetchone():
                    st.session_state.login = True
                    st.session_state.role = "admin"
                    st.session_state.kelas = kelas
                    st.session_state.jurusan = jurusan.upper()
                    st.rerun()
                else:
                    st.error("Login gagal")

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
                    st.error("Sudah ada admin di kelas ini")
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
                    st.success("Akun dibuat")

    # ================= USER =================
    elif role == "User":
        if st.button("Masuk sebagai User"):
            st.session_state.login = True
            st.session_state.role = "user"
            st.rerun()

    # ================= DEVELOPER =================
    else:
        user = st.text_input("Developer Username")
        pw = st.text_input("Developer Password", type="password")

        if st.button("Login Developer"):
            if user == DEV_USER and pw == DEV_PASS:
                st.session_state.login = True
                st.session_state.role = "dev"
                st.rerun()
            else:
                st.error("Akses ditolak")

# ======================
# MAIN APP
# ======================
else:

    st.title("📊 KAS KITA")

    # ================= ADMIN =================
    if st.session_state.role == "admin":
        st.success(f"Admin {st.session_state.kelas}-{st.session_state.jurusan}")

        nama = st.text_input("Nama Siswa")
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

    # ================= USER =================
    elif st.session_state.role == "user":
        st.info("User mode")
        df = pd.read_sql("SELECT * FROM kas", conn)
        st.dataframe(df)

    # ================= DEVELOPER =================
    elif st.session_state.role == "dev":
        st.warning("Developer Mode 🔧")

        # lihat semua data kas
        st.subheader("📊 Semua Data Kas")
        df = pd.read_sql("SELECT * FROM kas", conn)
        st.dataframe(df)

        # lihat semua admin
        st.subheader("👤 Data Admin")
        admin_df = pd.read_sql(
            "SELECT id, username, email, kelas, jurusan FROM admin",
            conn
        )
        st.dataframe(admin_df)

        # hapus admin
        id_hapus = st.number_input("Masukkan ID Admin", step=1)

        if st.button("Hapus Admin"):
            cursor.execute("DELETE FROM admin WHERE id=?", (id_hapus,))
            conn.commit()
            st.success("Admin dihapus")
            st.rerun()

    # ================= LOGOUT =================
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

st.write("© kaskita 2026")
