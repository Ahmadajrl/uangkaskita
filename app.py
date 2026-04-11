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

    # TABLE BARU PENGELUARAN
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
    "otp": None,
    "menu": "dashboard"
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

        # MENU NAVIGASI
        colA, colB = st.columns(2)

        with colA:
            if st.button("📊 Dashboard"):
                st.session_state.menu = "dashboard"
                st.rerun()

        with colB:
            if st.button("💸 Input Pengeluaran"):
                st.session_state.menu = "pengeluaran"
                st.rerun()

        # ================= DASHBOARD =================
        if st.session_state.menu == "dashboard":

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

            df = pd.read_sql(
                "SELECT * FROM kas WHERE kelas=? AND jurusan=?",
                conn,
                params=(st.session_state.kelas, st.session_state.jurusan)
            )

            if not df.empty:
                df["tanggal"] = pd.to_datetime(df["tanggal"]).dt.strftime("%Y-%m-%d")
                df["bulan"] = pd.to_datetime(df["tanggal"]).dt.strftime("%B %Y")

                total = df["nominal"].sum()
                st.metric("💰 Total Kas", format_rupiah(total))

            st.subheader("📈 Statistik Pembayaran")

            if not df.empty:
                tepat = len(df[df["status"] == "Tepat Waktu"])
                telat = len(df[df["status"] == "Telat"])

                col1, col2 = st.columns(2)
                col1.metric("Tepat Waktu", tepat)
                col2.metric("Telat", telat)

                st.bar_chart(df["status"].value_counts())
            else:
                st.info("Belum ada data")

            st.subheader("📊 Cek Performa Siswa")

            if not df.empty:
                siswa = st.selectbox("Pilih Siswa", sorted(df["nama"].unique()))

                if st.button("Cek Performa"):
                    data_siswa = df[df["nama"] == siswa]
                    hasil = data_siswa["status"].value_counts()

                    st.bar_chart(hasil)

                    total_s = len(data_siswa)
                    telat_s = len(data_siswa[data_siswa["status"] == "Telat"])
                    persen = (telat_s / total_s) * 100 if total_s > 0 else 0

                    if persen < 20:
                        st.success("Performa sangat baik 👍")
                    elif persen < 50:
                        st.warning("Perlu peningkatan ⚠️")
                    else:
                        st.error("Sering telat ❌")

            if not df.empty:
                for bulan in sorted(df["bulan"].unique()):
                    st.subheader(f"📅 {bulan}")
                    st.dataframe(df[df["bulan"] == bulan])

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
                    siswa_hapus = st.selectbox("Hapus Siswa", df["nama"].unique())
                    if st.button("Hapus Siswa") and konfirmasi:
                        cursor.execute(
                            "DELETE FROM kas WHERE nama=? AND kelas=? AND jurusan=?",
                            (siswa_hapus, st.session_state.kelas, st.session_state.jurusan)
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

        # ================= PENGELUARAN =================
        elif st.session_state.menu == "pengeluaran":

            st.subheader("💸 Input Pengeluaran")

            tgl = st.date_input("Tanggal")
            keterangan = st.text_input("Keterangan Pengeluaran")
            nominal = st.text_input("Nominal Pengeluaran")

            if st.button("Simpan Pengeluaran"):
                nilai = clean_nominal(nominal)

                cursor.execute(
                    "INSERT INTO pengeluaran VALUES (NULL,?,?,?,?,?)",
                    (
                        tgl.strftime("%Y-%m-%d"),
                        st.session_state.kelas,
                        st.session_state.jurusan,
                        keterangan,
                        nilai
                    )
                )
                conn.commit()
                st.success("Pengeluaran berhasil disimpan")
                st.rerun()

            df_masuk = pd.read_sql(
                "SELECT * FROM kas WHERE kelas=? AND jurusan=?",
                conn,
                params=(st.session_state.kelas, st.session_state.jurusan)
            )

            df_keluar = pd.read_sql(
                "SELECT * FROM pengeluaran WHERE kelas=? AND jurusan=?",
                conn,
                params=(st.session_state.kelas, st.session_state.jurusan)
            )

            total_masuk = df_masuk["nominal"].sum() if not df_masuk.empty else 0
            total_keluar = df_keluar["nominal"].sum() if not df_keluar.empty else 0
            saldo = total_masuk - total_keluar

            st.metric("🧮 Saldo Sekarang", format_rupiah(saldo))

            st.subheader("📋 Riwayat Pengeluaran")

            if not df_keluar.empty:
                df_keluar["tanggal"] = pd.to_datetime(df_keluar["tanggal"]).dt.strftime("%Y-%m-%d")
                st.dataframe(df_keluar)
            else:
                st.info("Belum ada pengeluaran")

    elif st.session_state.role == "user":

        st.subheader("📋 Data Pembayaran")

        df = pd.read_sql("SELECT * FROM kas", conn)

        if not df.empty:
            df["tanggal"] = pd.to_datetime(df["tanggal"]).dt.strftime("%Y-%m-%d")
            df["bulan"] = pd.to_datetime(df["tanggal"]).dt.strftime("%B %Y")

            for jurusan in sorted(df["jurusan"].dropna().unique()):
                st.header(f"🎓 Jurusan {jurusan}")

                df_jurusan = df[df["jurusan"] == jurusan]

                for bulan in sorted(df_jurusan["bulan"].unique()):
                    st.subheader(f"📅 {bulan}")
                    st.dataframe(df_jurusan[df_jurusan["bulan"] == bulan])
        else:
            st.info("Belum ada data")

    elif st.session_state.role == "dev":
        st.dataframe(pd.read_sql("SELECT * FROM kas", conn))
        st.dataframe(pd.read_sql("SELECT * FROM admin", conn))

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

st.write("© kaskita 2026")
