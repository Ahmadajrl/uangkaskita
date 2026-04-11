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
# DATABASE
# ======================
conn = sqlite3.connect("kas.db", check_same_thread=False)
cursor = conn.cursor()

# ======================
# CREATE TABLE
# ======================
cursor.execute('''
CREATE TABLE IF NOT EXISTS kas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT,
    tanggal TEXT,
    status TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    email TEXT
)
''')

conn.commit()

# ======================
# FIX DATABASE (AUTO UPDATE KOLOM)
# ======================
# cek kolom kas
cursor.execute("PRAGMA table_info(kas)")
columns_kas = [col[1] for col in cursor.fetchall()]

if "kelas" not in columns_kas:
    cursor.execute("ALTER TABLE kas ADD COLUMN kelas TEXT")
    conn.commit()

# cek kolom admin
cursor.execute("PRAGMA table_info(admin)")
columns_admin = [col[1] for col in cursor.fetchall()]

if "kelas" not in columns_admin:
    cursor.execute("ALTER TABLE admin ADD COLUMN kelas TEXT")
    conn.commit()

# ======================
# SESSION
# ======================
if "login_status" not in st.session_state:
    st.session_state.login_status = False

if "role" not in st.session_state:
    st.session_state.role = None

if "kelas" not in st.session_state:
    st.session_state.kelas = None

if "otp" not in st.session_state:
    st.session_state.otp = None

# ======================
# LOGIN PAGE
# ======================
if not st.session_state.login_status:

    st.title("🔐 Login Sistem KAS")

    role = st.selectbox("Login sebagai:", ["Admin", "User"])

    if role == "Admin":

        menu = st.radio("Menu", ["Login", "Register", "Lupa Password"])

        # ===== LOGIN =====
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
                    st.session_state.login_status = True
                    st.session_state.role = "admin"
                    st.session_state.kelas = data[4]  # ambil kelas
                    st.success(f"Login berhasil! Kelas: {data[4]}")
                    st.rerun()
                else:
                    st.error("Username / Password salah!")

        # ===== REGISTER =====
        elif menu == "Register":
            new_user = st.text_input("Username Baru")
            new_pass = st.text_input("Password Baru", type="password")
            email = st.text_input("Email")
            kelas = st.selectbox("Pilih Kelas", ["A", "B", "C"])

            if st.button("Daftar"):
                cursor.execute(
                    "INSERT INTO admin (username, password, email, kelas) VALUES (?, ?, ?, ?)",
                    (new_user, new_pass, email, kelas)
                )
                conn.commit()
                st.success("Akun berhasil dibuat!")

        # ===== LUPA PASSWORD =====
        elif menu == "Lupa Password":
            email = st.text_input("Masukkan Email")

            if st.button("Kirim OTP"):
                otp = random.randint(1000, 9999)
                st.session_state.otp = str(otp)
                st.warning(f"OTP (simulasi): {otp}")

            otp_input = st.text_input("Masukkan OTP")
            new_pass = st.text_input("Password Baru", type="password")

            if st.button("Reset Password"):
                if otp_input == st.session_state.otp:
                    cursor.execute(
                        "UPDATE admin SET password=? WHERE email=?",
                        (new_pass, email)
                    )
                    conn.commit()
                    st.success("Password berhasil diubah!")
                else:
                    st.error("OTP salah!")

    # ===== USER =====
    else:
        if st.button("Masuk sebagai User"):
            st.session_state.login_status = True
            st.session_state.role = "user"
            st.session_state.kelas = None
            st.rerun()

# ======================
# MAIN APP
# ======================
else:

    st.title("📊 KAS KITA")

    if st.session_state.role == "admin":
        st.success(f"Login sebagai ADMIN | Kelas {st.session_state.kelas}")
    else:
        st.info("Login sebagai USER (Read Only)")

    # ================= INPUT (ADMIN ONLY)
    if st.session_state.role == "admin":
        st.subheader("➕ Input Pembayaran")

        nama = st.text_input("Nama Siswa")
        tanggal = st.date_input("Tanggal Bayar", datetime.date.today())
        status = st.selectbox("Status", ["Tepat Waktu", "Telat"])

        if st.button("Simpan"):
            if nama.strip():
                cursor.execute(
                    "INSERT INTO kas (nama, tanggal, status, kelas) VALUES (?, ?, ?, ?)",
                    (nama, str(tanggal), status, st.session_state.kelas)
                )
                conn.commit()
                st.success("Data berhasil disimpan!")
            else:
                st.warning("Nama tidak boleh kosong!")

    # ================= AMBIL DATA (FIX ERROR NULL + FILTER)
    if st.session_state.role == "admin":
        df = pd.read_sql(
            "SELECT * FROM kas WHERE kelas = ? OR kelas IS NULL",
            conn,
            params=(st.session_state.kelas,)
        )
    else:
        df = pd.read_sql("SELECT * FROM kas", conn)

    # ================= TABEL
    st.subheader("📋 Data Pembayaran")
    st.dataframe(df, use_container_width=True)

    # ================= ANALISIS
    st.subheader("📈 Analisis Keseluruhan")

    if not df.empty:
        global_data = df["status"].value_counts()
        st.bar_chart(global_data)
    else:
        st.warning("Belum ada data")

    # ================= STATISTIK
    st.subheader("📊 Statistik Keterlambatan Siswa")

    if not df.empty:
        nama_list = df["nama"].unique()
        nama_pilih = st.selectbox("Pilih Nama Siswa", nama_list)

        if st.button("Lihat Statistik"):
            data_siswa = df[df["nama"] == nama_pilih]

            if not data_siswa.empty:
                hasil = data_siswa["status"].value_counts()

                st.write(f"Statistik untuk: **{nama_pilih}**")
                st.bar_chart(hasil)
                st.write(hasil)
            else:
                st.warning("Belum ada data siswa ini")

    # ================= LOGOUT
    if st.button("Logout"):
        st.session_state.login_status = False
        st.session_state.role = None
        st.session_state.kelas = None
        st.rerun()

# ======================
# FOOTER
# ======================
st.write("©kaskita 2026")
