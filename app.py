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
# DATABASE INIT (SUPER AMAN)
# ======================
def init_db():
    conn = sqlite3.connect("kas.db", check_same_thread=False)
    cursor = conn.cursor()

    # Buat tabel dengan struktur lengkap
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS kas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT,
        tanggal TEXT,
        status TEXT,
        kelas TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        email TEXT,
        kelas TEXT
    )
    ''')

    conn.commit()

    # ===== FIX KOLOM (ANTI ERROR TOTAL)
    def ensure_column(table, column):
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]

        if column not in columns:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} TEXT")
                conn.commit()
            except:
                pass  # ignore kalau sudah ada

    ensure_column("kas", "kelas")
    ensure_column("admin", "kelas")

    return conn, cursor


conn, cursor = init_db()

# ======================
# SESSION STATE
# ======================
if "login" not in st.session_state:
    st.session_state.login = False

if "role" not in st.session_state:
    st.session_state.role = None

if "kelas" not in st.session_state:
    st.session_state.kelas = None

if "otp" not in st.session_state:
    st.session_state.otp = None

# ======================
# LOGIN PAGE
# ======================
if not st.session_state.login:

    st.title("🔐 Login Sistem KAS")

    role = st.selectbox("Login sebagai", ["Admin", "User"])

    # ================= ADMIN =================
    if role == "Admin":

        menu = st.radio("Menu", ["Login", "Register", "Lupa Password"])

        # LOGIN
        if menu == "Login":
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if st.button("Login"):
                cursor.execute(
                    "SELECT * FROM admin WHERE username=? AND password=?",
                    (username, password)
                )
                data = cursor.fetchone()

                if data:
                    st.session_state.login = True
                    st.session_state.role = "admin"
                    st.session_state.kelas = data[4] if data[4] else "A"
                    st.success(f"Login berhasil (Kelas {st.session_state.kelas})")
                    st.rerun()
                else:
                    st.error("Login gagal")

        # REGISTER
        elif menu == "Register":
            user = st.text_input("Username Baru")
            pw = st.text_input("Password Baru", type="password")
            email = st.text_input("Email")
            kelas = st.selectbox("Kelas", ["A", "B", "C"])

            if st.button("Daftar"):
                cursor.execute(
                    "INSERT INTO admin (username, password, email, kelas) VALUES (?, ?, ?, ?)",
                    (user, pw, email, kelas)
                )
                conn.commit()
                st.success("Akun berhasil dibuat")

        # LUPA PASSWORD
        elif menu == "Lupa Password":
            email = st.text_input("Email")

            if st.button("Kirim OTP"):
                otp = str(random.randint(1000, 9999))
                st.session_state.otp = otp
                st.warning(f"OTP (simulasi): {otp}")

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

    # ================= USER =================
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
        st.success(f"Admin Kelas {st.session_state.kelas}")
    else:
        st.info("User (Read Only)")

    # ================= INPUT (ADMIN ONLY)
    if st.session_state.role == "admin":
        st.subheader("➕ Input Pembayaran")

        nama = st.text_input("Nama Siswa")
        tanggal = st.date_input("Tanggal", datetime.date.today())
        status = st.selectbox("Status", ["Tepat Waktu", "Telat"])

        if st.button("Simpan"):
            if nama:
                cursor.execute(
                    "INSERT INTO kas (nama, tanggal, status, kelas) VALUES (?, ?, ?, ?)",
                    (nama, str(tanggal), status, st.session_state.kelas)
                )
                conn.commit()
                st.success("Data tersimpan")
            else:
                st.warning("Nama kosong")

    # ================= AMBIL DATA (AMAN)
    if st.session_state.role == "admin":
        df = pd.read_sql(
            "SELECT * FROM kas WHERE kelas = ? OR kelas IS NULL",
            conn,
            params=(st.session_state.kelas,)
        )
    else:
        df = pd.read_sql("SELECT * FROM kas", conn)

    # ================= TABEL
    st.subheader("📋 Data")
    st.dataframe(df, use_container_width=True)

    # ================= ANALISIS
    st.subheader("📈 Statistik")

    if not df.empty:
        st.bar_chart(df["status"].value_counts())
    else:
        st.warning("Belum ada data")

    # ================= PER SISWA
    st.subheader("📊 Statistik per Siswa")

    if not df.empty:
        nama_list = df["nama"].unique()
        pilih = st.selectbox("Pilih Siswa", nama_list)

        if st.button("Lihat Statistik"):
            data = df[df["nama"] == pilih]
            hasil = data["status"].value_counts()

            st.bar_chart(hasil)
            st.write(hasil)

    # ================= LOGOUT
    if st.button("Logout"):
        st.session_state.login = False
        st.session_state.role = None
        st.session_state.kelas = None
        st.rerun()

# ======================
# FOOTER
# ======================
st.write("© kaskita 2026")
