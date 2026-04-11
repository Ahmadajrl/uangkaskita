import streamlit as st
import pandas as pd
import datetime
import sqlite3
import random
import hashlib

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
# HASH
# ======================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

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
# ROLE PAGE
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

        menu = st.radio("Menu", ["Login", "Register", "Lupa Password"])

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
                elif data[4] != kelas or data[5] != jurusan.upper():
                    st.error("Kelas/Jurusan salah")
                else:
                    st.session_state.login = True
                    st.session_state.kelas = kelas
                    st.session_state.jurusan = jurusan.upper()
                    st.rerun()

        elif menu == "Register":
            user = st.text_input("Username Baru")
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
                    st.success("Akun dibuat")

        elif menu == "Lupa Password":
            email = st.text_input("Email")

            if st.button("Kirim OTP"):
                cursor.execute("SELECT * FROM admin WHERE email=?", (email,))
                if cursor.fetchone():
                    otp = str(random.randint(1000, 9999))
                    st.session_state.otp = otp
                    st.success(f"OTP: {otp}")
                else:
                    st.error("Email tidak ditemukan")

            otp_input = st.text_input("OTP")
            new_pw = st.text_input("Password Baru", type="password")

            if st.button("Reset"):
                if otp_input == st.session_state.otp:
                    cursor.execute(
                        "UPDATE admin SET password=? WHERE email=?",
                        (hash_password(new_pw), email)
                    )
                    conn.commit()
                    st.success("Password diubah")
                else:
                    st.error("OTP salah")

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

    if st.session_state.role == "admin":

        st.success(f"Kelas {st.session_state.kelas} - {st.session_state.jurusan}")

        # INPUT
        st.subheader("➕ Input Pembayaran")

        nama = st.text_input("Nama Siswa")
        tanggal = st.date_input("Tanggal")
        status = st.selectbox("Status", ["Tepat Waktu", "Telat"])
        keterangan = st.text_input("Keterangan")
        nominal = st.text_input("Nominal (bebas)")

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

        # DATA
        df = pd.read_sql(
            "SELECT * FROM kas WHERE kelas=? AND jurusan=?",
            conn,
            params=(st.session_state.kelas, st.session_state.jurusan)
        )

        if not df.empty:
            df["tanggal"] = pd.to_datetime(df["tanggal"]).dt.strftime("%Y-%m-%d")
            df["bulan"] = pd.to_datetime(df["tanggal"]).dt.strftime("%B %Y")

        # TOTAL
        if not df.empty:
            total = df["nominal"].sum()
            st.metric("💰 Total Kas", format_rupiah(total))

        # TABEL PER BULAN
        if not df.empty:
            for bulan in sorted(df["bulan"].unique()):
                st.subheader(f"📅 {bulan}")
                st.dataframe(df[df["bulan"] == bulan])

        # ================= HAPUS DATA =================
        st.subheader("🗑️ Hapus Data")
        konfirmasi = st.checkbox("Saya yakin")

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
                    cursor.execute(
                        "DELETE FROM kas WHERE nama=? AND kelas=? AND jurusan=?",
                        (siswa, st.session_state.kelas, st.session_state.jurusan)
                    )
                    conn.commit()
                    st.rerun()

        with col3:
            if st.button("Hapus Semua") and konfirmasi:
                cursor.execute(
                    "DELETE FROM kas WHERE kelas=? AND jurusan=?",
                    (st.session_state.kelas, st.session_state.jurusan)
                )
                conn.commit()
                st.rerun()

    elif st.session_state.role == "user":
        df = pd.read_sql("SELECT * FROM kas", conn)
        st.dataframe(df)

    elif st.session_state.role == "dev":
        st.dataframe(pd.read_sql("SELECT * FROM kas", conn))
        st.dataframe(pd.read_sql("SELECT * FROM admin", conn))

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

st.write("© kaskita 2026")
