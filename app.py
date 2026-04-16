import streamlit as st 
import pandas as pd
import sqlite3
import hashlib
import io

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

st.set_page_config(layout="wide")
st.set_page_config(
    page_title="KAS KITA",
    page_icon="icon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>

/* BACKGROUND */
.stApp{
    background: linear-gradient(135deg,#01023B,#09124f,#10297a);
    color:white;
}

/* FONT */
html, body, [class*="css"]{
    font-family: 'Segoe UI', sans-serif;
}

/* SIDEBAR */
section[data-testid="stSidebar"]{
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(10px);
}

/* BUTTON */
.stButton>button{
    width:100%;
    border:none;
    border-radius:12px;
    padding:12px;
    background:#09F289;
    color:#01023B;
    font-weight:bold;
    font-size:16px;
    transition:0.3s;
}

.stButton>button:hover{
    background:#07d978;
    color:#ffffff;
    transform:scale(1.03);
}

/* INPUT */
.stTextInput input,
.stNumberInput input,
.stDateInput input{
    border-radius:12px !important;
    border:1px solid #4da6ff !important;
}

/* CARD METRIC */
[data-testid="metric-container"]{
    background: rgba(255,255,255,0.07);
    border-radius:15px;
    padding:15px;
}

/* HIDE */
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}

</style>
""", unsafe_allow_html=True)
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
# PDF
# ======================
def generate_pdf(df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)

    data = [df.columns.tolist()] + df.values.tolist()

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
    "menu": "dashboard",
    "auth_page": "login"
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ======================
# LOGO
# ======================
st.markdown("""<br>""", unsafe_allow_html=True)

col1,col2,col3 = st.columns([1,1.5,1])

with col2:
    st.image("logo.png", width=500)
# ======================
# ROLE / HALAMAN PILIH LOGIN (FINAL REVISI)
# ======================
if not st.session_state.login and st.session_state.page == "role":

    # ======================
    # CSS LOGIN PREMIUM
    # ======================
    st.markdown("""
    <style>

    .login-box{
        background: rgba(255,255,255,0.08);
        padding:40px;
        border-radius:28px;
        backdrop-filter: blur(14px);
        box-shadow:0 15px 35px rgba(0,0,0,0.35);
        text-align:center;
        max-width:520px;
        margin:auto;
        margin-top:30px;
        border:1px solid rgba(255,255,255,0.08);
    }

    .title-login{
        font-size:42px;
        font-weight:800;
        color:white;
        margin-top:10px;
        margin-bottom:8px;
    }

    .sub-login{
        color:#d9d9d9;
        font-size:17px;
        margin-bottom:5px;
        line-height:1.7;
    }

    </style>
    """, unsafe_allow_html=True)

    # ======================
    # LOGO TENGAH
    # ======================
    col1, col2, col3 = st.columns([1,1,1])

    with col2:
        st.image("icon.png", width=95)

    # ======================
    # BOX LOGIN
    # ======================
# ======================
# BOX LOGIN FINAL FIX
# ======================

st.markdown(
    """
    <div class="login-box">

        <h1 class="title-login">KAS KITA</h1>

        <p class="sub-login">
            Aplikasi Keuangan Kas Modern <br>
            Smart School Finance System
        </p>

    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)

    # ======================
    # BUTTON LOGIN TENGAH
    # ======================
col1, col2, col3 = st.columns([1.4,2.2,1.4])

with col2:

    if st.button("👨‍💼 Login Admin", use_container_width=True):
        st.session_state.role = "admin"
        st.session_state.page = "login"
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("👨‍🎓 Masuk Sebagai User", use_container_width=True):
        st.session_state.role = "user"
        st.session_state.login = True
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("👨‍💻 Developer Mode", use_container_width=True):
        st.session_state.role = "dev"
        st.session_state.page = "login"
        st.rerun()
# ======================
# LOGIN / REGISTER / FORGOT
# ======================
elif not st.session_state.login:

    st.title("Authentication")

    tab1, tab2, tab3 = st.tabs(["Login", "Register", "Lupa Password"])

    # ================= LOGIN =================
    with tab1:

        if st.session_state.role == "admin":

            user = st.text_input("Username", key="login_user")
            pw = st.text_input("Password", type="password", key="login_pass")
            kelas = st.selectbox("Kelas", ["10","11","12"])
            jurusan = st.text_input("Jurusan")

            if st.button("Login Admin"):
                hashed = hash_password(pw)

                cursor.execute(
                    "SELECT * FROM admin WHERE username=? AND password=?",
                    (user, hashed)
                )
                data = cursor.fetchone()

                if data:
                    st.session_state.login = True
                    st.session_state.kelas = kelas
                    st.session_state.jurusan = jurusan.upper()
                    st.rerun()
                else:
                    st.error("Username atau password salah")

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

    # ================= REGISTER =================
    with tab2:

        st.subheader("Register Admin")

        new_user = st.text_input("Username Baru", key="reg_user")
        new_pass = st.text_input("Password Baru", type="password", key="reg_pass")
        email = st.text_input("Email", key="reg_email")
        jurusan = st.text_input("Jurusan Register", key="reg_jurusan")
        if st.button("Daftar"):
            if new_user and new_pass:
                hashed = hash_password(new_pass)

                cursor.execute(
                    "INSERT INTO admin VALUES (NULL,?,?,?,?,?)",
                    (new_user, hashed, email, kelas, jurusan.upper())
                )
                conn.commit()

                st.success("Akun berhasil dibuat")
            else:
                st.warning("Isi semua field")

    # ================= LUPA PASSWORD =================
    with tab3:

        st.subheader("Reset Password")

        user = st.text_input("Username", key="forgot_user")
        email = st.text_input("Email Terdaftar", key="forgot_email")
        new_pass = st.text_input("Password Baru", type="password", key="forgot_pass")

        if st.button("Reset Password"):
            hashed = hash_password(new_pass)

            cursor.execute(
                "SELECT * FROM admin WHERE username=? AND email=?",
                (user, email)
            )
            data = cursor.fetchone()

            if data:
                cursor.execute(
                    "UPDATE admin SET password=? WHERE username=?",
                    (hashed, user)
                )
                conn.commit()
                st.success("Password berhasil diubah")
            else:
                st.error("Data tidak ditemukan")

# ======================
# MAIN APP
# ======================
else:

    st.title("📊 Dashboard KAS")

    # ================= USER =================
    if st.session_state.role == "user":

        df = pd.read_sql("SELECT * FROM kas", conn)

        if not df.empty:
            df["tanggal"] = pd.to_datetime(df["tanggal"])
            df["bulan"] = df["tanggal"].dt.strftime("%B %Y")
            df["tanggal"] = df["tanggal"].dt.strftime("%Y-%m-%d")

            col1, col2, col3 = st.columns(3)

            with col1:
                fk = st.selectbox("Kelas", sorted(df["kelas"].unique()))
            with col2:
                fj = st.selectbox("Jurusan", sorted(df["jurusan"].unique()))
            with col3:
                fb = st.selectbox("Bulan", sorted(df["bulan"].unique()))

            df = df[
                (df["kelas"] == fk) &
                (df["jurusan"] == fj) &
                (df["bulan"] == fb)
            ]

            st.metric("Total Kas", format_rupiah(df["nominal"].sum()))
            st.dataframe(df)

            st.download_button(
                "⬇️ Download PDF",
                generate_pdf(df),
                "user_kas.pdf"
            )

        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

    # ================= DEVELOPER =================
    elif st.session_state.role == "dev":

        st.subheader("🛠️ Developer Panel")

        df_admin = pd.read_sql("SELECT * FROM admin", conn)
        df_kas = pd.read_sql("SELECT * FROM kas", conn)

        st.subheader("👤 Data Akun Admin")
        st.dataframe(df_admin)

        st.download_button(
            "⬇️ Download PDF Akun",
            generate_pdf(df_admin),
            "akun_admin.pdf"
        )

        if not df_admin.empty:
            id_del = st.number_input("Hapus ID Akun", step=1)
            if st.button("Hapus Akun"):
                cursor.execute("DELETE FROM admin WHERE id=?", (id_del,))
                conn.commit()
                st.rerun()

        st.subheader("📊 Semua Data Kas")
        st.dataframe(df_kas)

        st.download_button(
            "⬇️ Download PDF Kas",
            generate_pdf(df_kas),
            "kas_all.pdf"
        )

        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

    # ================= ADMIN =================
    elif st.session_state.role == "admin":

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

        # ================= DASHBOARD =================
        if st.session_state.menu == "dashboard":

            st.subheader("➕ Input Pembayaran")

            nama = st.text_input("Nama")
            tgl = st.date_input("Tanggal")
            status = st.selectbox("Status", ["Tepat Waktu","Telat"])
            ket = st.text_input("Keterangan")
            nom = st.text_input("Nominal")

            if st.button("Simpan"):
                cursor.execute(
                    "INSERT INTO kas VALUES (NULL,?,?,?,?,?,?,?)",
                    (nama, tgl.strftime("%Y-%m-%d"), status,
                     st.session_state.kelas,
                     st.session_state.jurusan,
                     ket,
                     clean_nominal(nom))
                )
                conn.commit()
                st.rerun()

            df = pd.read_sql(
                "SELECT * FROM kas WHERE kelas=? AND jurusan=?",
                conn,
                params=(st.session_state.kelas, st.session_state.jurusan)
            )

            if not df.empty:

                st.subheader("📈 Statistik")
                st.metric("Total Kas", format_rupiah(df["nominal"].sum()))
                st.bar_chart(df["status"].value_counts())

                st.subheader("📋 Data Kas")
                df["tanggal"] = pd.to_datetime(df["tanggal"]).dt.strftime("%Y-%m-%d")
                st.dataframe(df)

                st.download_button(
                    "⬇️ Download PDF Kas",
                    generate_pdf(df),
                    "kas_admin.pdf"
                )

                # ================= CEK STATISTIK SISWA (RESTORED AGAIN) =================
                st.subheader("📊 Cek Statistik Per Siswa")

                siswa = st.selectbox("Pilih Siswa", sorted(df["nama"].unique()))

                if st.button("Cek Statistik"):
                    data = df[df["nama"] == siswa]
                    hasil = data["status"].value_counts()

                    st.bar_chart(hasil)

                    total = len(data)
                    telat = len(data[data["status"] == "Telat"])
                    persen = (telat / total) * 100 if total > 0 else 0

                    if persen < 20:
                        st.success("Performa sangat baik 👍")
                    elif persen < 50:
                        st.warning("Perlu peningkatan ⚠️")
                    else:
                        st.error("Sering telat ❌")

            st.subheader("🗑️ Hapus Data")
            konfirmasi = st.checkbox("Konfirmasi")

            col1, col2, col3 = st.columns(3)

            with col1:
                id_hapus = st.number_input("Hapus ID", step=1)
                if st.button("Hapus ID") and konfirmasi:
                    cursor.execute("DELETE FROM kas WHERE id=?", (id_hapus,))
                    conn.commit()
                    st.rerun()

            with col2:
                if not df.empty:
                    siswa_del = st.selectbox("Hapus Siswa", df["nama"].unique())
                    if st.button("Hapus Siswa") and konfirmasi:
                        cursor.execute("DELETE FROM kas WHERE nama=?", (siswa_del,))
                        conn.commit()
                        st.rerun()

            with col3:
                if st.button("Hapus Semua") and konfirmasi:
                    cursor.execute("DELETE FROM kas WHERE kelas=? AND jurusan=?",
                                   (st.session_state.kelas, st.session_state.jurusan))
                    conn.commit()
                    st.rerun()

        # ================= PENGELUARAN =================
        elif st.session_state.menu == "pengeluaran":

            st.subheader("💸 Input Pengeluaran")

            tgl = st.date_input("Tanggal")
            ket = st.text_input("Keterangan")
            nom = st.text_input("Nominal")

            if st.button("Simpan"):
                cursor.execute(
                    "INSERT INTO pengeluaran VALUES (NULL,?,?,?,?,?)",
                    (tgl.strftime("%Y-%m-%d"),
                     st.session_state.kelas,
                     st.session_state.jurusan,
                     ket,
                     clean_nominal(nom))
                )
                conn.commit()

            df_keluar = pd.read_sql(
                "SELECT * FROM pengeluaran WHERE kelas=? AND jurusan=?",
                conn,
                params=(st.session_state.kelas, st.session_state.jurusan)
            )

            df_masuk = pd.read_sql(
                "SELECT nominal FROM kas WHERE kelas=? AND jurusan=?",
                conn,
                params=(st.session_state.kelas, st.session_state.jurusan)
            )

            total_masuk = df_masuk["nominal"].sum() if not df_masuk.empty else 0
            total_keluar = df_keluar["nominal"].sum() if not df_keluar.empty else 0
            saldo = total_masuk - total_keluar

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Kas", format_rupiah(total_masuk))
            col2.metric("Total Pengeluaran", format_rupiah(total_keluar))
            col3.metric("Saldo", format_rupiah(saldo))

            st.subheader("📋 Riwayat Pengeluaran")

            if not df_keluar.empty:
                df_keluar["tanggal"] = pd.to_datetime(df_keluar["tanggal"]).dt.strftime("%Y-%m-%d")
                st.dataframe(df_keluar)

                st.download_button(
                    "⬇️ Download PDF Pengeluaran",
                    generate_pdf(df_keluar),
                    "pengeluaran.pdf"
                )

        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

st.markdown("""
<div style='text-align:center;margin-top:40px;color:#cccccc'>
© KASKITA 2026 | Design by Kelompok 2
</div>
""", unsafe_allow_html=True)
