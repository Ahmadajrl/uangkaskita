import streamlit as st
import pandas as pd
import datetime
import sqlite3
import random

# ======================
# CONFIG
# ======================
st.set_page_config(layout="wide")

# ======================
# DATABASE INIT (ANTI ERROR TOTAL)
# ======================
def init_db():
    conn = sqlite3.connect("kas.db", check_same_thread=False)
    cursor = conn.cursor()

    # tabel utama
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

    # ===== FIX KOLOM (PENTING BANGET)
    def ensure_column(table, column):
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]

        if column not in columns:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} TEXT")
                conn.commit()
            except:
                pass

    ensure_column("kas", "kelas")
    ensure_column("kas", "jurusan")
    ensure_column("admin", "kelas")
    ensure_column("admin", "jurusan")

    return conn, cursor


conn, cursor = init_db()

# ======================
# SESSION
# ======================
if "login" not in st.session_state:
    st.session_state.login = False
if "role" not in st.session_state:
    st.session_state.role = None
if "kelas" not in st.session_state:
    st.session_state.kelas = None
if "jurusan" not in st.session_state:
    st.session_state.jurusan = None
if "otp" not in st.session_state:
    st.session_state.otp = None

# ======================
# LOGIN PAGE
# ======================
if not st.session_state.login:

    st.title("🔐 Login Sistem KAS")

    role = st.selectbox("Login sebagai", ["Admin", "User"])

    if role == "Admin":

        menu = st.radio("Menu", ["Login", "Register", "Lupa Password"])

        # ===== LOGIN =====
        if menu == "Login":
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            kelas = st.selectbox("Kelas", ["A", "B", "C"])
            jurusan = st.text_input("Jurusan (contoh: RPL)")

            if st.button("Login"):
                cursor.execute(
                    """SELECT * FROM admin 
                    WHERE username=? AND password=? AND kelas=? AND jurusan=?""",
                    (username, password, kelas, jurusan)
                )
                data = cursor.fetchone()

                if data:
                    st.session_state.login = True
                    st.session_state.role = "admin"
                    st.session_state.kelas = kelas
                    st.session_state.jurusan = jurusan
                    st.success("Login berhasil")
                    st.rerun()
                else:
                    st.error("Login gagal")

        # ===== REGISTER =====
        elif menu == "Register":
            user = st.text_input("Username Baru")
            pw = st.text_input("Password Baru", type="password")
            email = st.text_input("Email")
            kelas = st.selectbox("Kelas", ["A", "B", "C"])
            jurusan = st.text_input("Jurusan")

            if st.button("Daftar"):

                # CEK DUPLIKAT
                cursor.execute(
                    "SELECT * FROM admin WHERE kelas=? AND jurusan=?",
                    (kelas, jurusan)
                )
                existing = cursor.fetchone()

                if existing:
                    st.error("Admin untuk kelas & jurusan ini sudah ada!")
                else:
                    cursor.execute(
                        """INSERT INTO admin 
                        (username, password, email, kelas, jurusan)
                        VALUES (?, ?, ?, ?, ?)""",
                        (user, pw, email, kelas, jurusan)
                    )
                    conn.commit()
                    st.success("Akun berhasil dibuat!")

        # ===== LUPA PASSWORD =====
        elif menu == "Lupa Password":
            email = st.text_input("Email")

            if st.button("Kirim OTP"):
                otp = str(random.randint(1000, 9999))
                st.session_state.otp = otp
                st.warning(f"OTP: {otp}")

            otp_input = st.text_input("Masukkan OTP")
            new_pw = st.text_input("Password Baru", type="password")

            if st.button("Reset Password"):
                if otp_input == st.session_state.otp:
                    cursor.execute(
                        "UPDATE admin SET password=? WHERE email=?",
                        (new_pw, email)
                    )
                    conn.commit()
                    st.success("Password berhasil diubah")
                else:
                    st.error("OTP salah")

    else:
        if st.button("Masuk sebagai User"):
            st.session_state.login = True
            st.session_state.role = "user"
            st.rerun()

# ======================
# MAIN APP
# ======================
else:

    st.title("📊 KAS KITA")

    if st.session_state.role == "admin":
        st.success(f"Kelas {st.session_state.kelas} - {st.session_state.jurusan}")
    else:
        st.info("User (Read Only)")

    # ===== INPUT =====
    if st.session_state.role == "admin":
        nama = st.text_input("Nama Siswa")
        tanggal = st.date_input("Tanggal", datetime.date.today())
        status = st.selectbox("Status", ["Tepat Waktu", "Telat"])

        if st.button("Simpan"):
            if nama:
                cursor.execute(
                    """INSERT INTO kas (nama, tanggal, status, kelas, jurusan)
                    VALUES (?, ?, ?, ?, ?)""",
                    (nama, str(tanggal), status,
                     st.session_state.kelas,
                     st.session_state.jurusan)
                )
                conn.commit()
                st.success("Data tersimpan")
                st.rerun()

    # ===== AMBIL DATA =====
    if st.session_state.role == "admin":
        df = pd.read_sql(
            "SELECT * FROM kas WHERE kelas=? AND jurusan=?",
            conn,
            params=(st.session_state.kelas, st.session_state.jurusan)
        )
    else:
        df = pd.read_sql("SELECT * FROM kas", conn)

    st.dataframe(df, use_container_width=True)

    # ===== LOGOUT =====
    if st.button("Logout"):
        st.session_state.login = False
        st.session_state.role = None
        st.session_state.kelas = None
        st.session_state.jurusan = None
        st.rerun()
        
cursor.execute("DELETE FROM kas WHERE kelas IS NULL")
conn.commit()

st.write("© kaskita 2026")
