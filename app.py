import streamlit as st
import pandas as pd
import hashlib
import requests
import io
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

# ================= CONFIG =================
st.set_page_config(page_title="KAS KITA", layout="wide")

API_URL = "https://script.google.com/macros/s/AKfycbwDTFrVRp4LuLnwG_OAyBH4KefKfkwilzRfOlYcArMHZvK6uqV6cUvih_VQ1kVrKgr4/exec"

# ================= HELPER =================
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def api_get(table):
    try:
        res = requests.get(API_URL, params={"action":"get","table":table})
        return pd.DataFrame(res.json())
    except:
        st.error("API ERROR")
        return pd.DataFrame()

def api_post(table, data):
    requests.post(API_URL, json={
        "action":"insert",
        "table":table,
        "data":data
    })

def api_delete(table, id):
    requests.post(API_URL, json={
        "action":"delete",
        "table":table,
        "id":id
    })

def rupiah(x):
    return f"Rp {int(x):,}".replace(",", ".")

# ================= PDF =================
def generate_pdf(df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)

    df_copy = df.copy()

    if "nominal" in df_copy.columns:
        df_copy["nominal"] = pd.to_numeric(df_copy["nominal"], errors="coerce").fillna(0)
        df_copy["nominal"] = df_copy["nominal"].astype(int).apply(lambda x: f"Rp {x:,}".replace(",", "."))

    data = [df_copy.columns.tolist()] + df_copy.values.tolist()

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('GRID',(0,0),(-1,-1),1,colors.black)
    ]))

    doc.build([table])
    buffer.seek(0)
    return buffer

# ================= SESSION =================
if "login" not in st.session_state:
    st.session_state.login = False

if "menu" not in st.session_state:
    st.session_state.menu = "dashboard"

# ================= AUTH =================
if not st.session_state.login:

    st.title("💰 KAS KITA")

    tab1, tab2 = st.tabs(["Login", "Register"])

    # LOGIN
    with tab1:
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")

        if st.button("Login"):
            df = api_get("admin")

            if not df.empty:
                df["username"] = df["username"].astype(str)
                df["password"] = df["password"].astype(str)

                data = df[
                    (df["username"] == user) &
                    (df["password"] == hash_password(pw))
                ]

                if not data.empty:
                    st.session_state.login = True
                    st.rerun()
                else:
                    st.error("Username / Password salah")

    # REGISTER
    with tab2:
        user = st.text_input("Username Baru")
        pw = st.text_input("Password Baru", type="password")

        if st.button("Daftar"):
            data = {
                "username": user,
                "password": hash_password(pw),
                "email": "-",
                "kelas": "-",
                "jurusan": "-"
            }
            api_post("admin", data)
            st.success("Akun berhasil dibuat")

# ================= MAIN =================
else:

    st.title("📊 Dashboard KAS")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📊 Dashboard"):
            st.session_state.menu = "dashboard"
            st.rerun()

    with col2:
        if st.button("💸 Pengeluaran"):
            st.session_state.menu = "pengeluaran"
            st.rerun()

    # ================= DASHBOARD =================
    if st.session_state.menu == "dashboard":

        df = api_get("kas")

        if not df.empty:

            # FIX DATA
            df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
            df["nominal"] = pd.to_numeric(df["nominal"], errors="coerce").fillna(0)

            # FIX TIPE DATA (PENTING)
            df["kelas"] = df["kelas"].astype(str)
            df["jurusan"] = df["jurusan"].astype(str)

            # BULAN
            df["bulan"] = df["tanggal"].dt.strftime("%B %Y")

            # ================= FILTER =================
            st.subheader("🔍 Filter Data")

            col1, col2, col3 = st.columns(3)

            with col1:
                f_kelas = st.selectbox(
                    "Kelas",
                    ["Semua"] + sorted(df["kelas"].dropna().astype(str).unique().tolist())
                )

            with col2:
                f_jurusan = st.selectbox(
                    "Jurusan",
                    ["Semua"] + sorted(df["jurusan"].dropna().astype(str).unique().tolist())
                )

            with col3:
                f_bulan = st.selectbox(
                    "Bulan",
                    ["Semua"] + sorted(df["bulan"].dropna().astype(str).unique().tolist())
                )

            # FILTER LOGIC
            df_filtered = df.copy()

            if f_kelas != "Semua":
                df_filtered = df_filtered[df_filtered["kelas"] == f_kelas]

            if f_jurusan != "Semua":
                df_filtered = df_filtered[df_filtered["jurusan"] == f_jurusan]

            if f_bulan != "Semua":
                df_filtered = df_filtered[df_filtered["bulan"] == f_bulan]

            # ================= TOTAL =================
            total_kas = df_filtered["nominal"].sum()
            st.metric("💰 Total Kas", rupiah(total_kas))

            # ================= GRAFIK =================
            st.subheader("📊 Grafik Kas per Bulan")
            grafik = df.groupby("bulan")["nominal"].sum()
            st.bar_chart(grafik)

            # ================= DATA =================
            st.subheader("📋 Data Kas")
            st.dataframe(df_filtered)

            st.download_button(
                "⬇️ Download Data Kas (PDF)",
                generate_pdf(df_filtered),
                file_name="data_kas.pdf"
            )

            # ================= STATISTIK SISWA =================
            st.subheader("📊 Statistik Per Siswa")

            if not df_filtered.empty:
                siswa = st.selectbox("Pilih Siswa", sorted(df_filtered["nama"].astype(str).unique()))

                if st.button("Cek Statistik"):
                    data = df_filtered[df_filtered["nama"] == siswa]
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

        else:
            st.warning("Belum ada data kas")

        # ================= TAMBAH DATA =================
        st.subheader("➕ Tambah Data Kas")

        col1, col2 = st.columns(2)

        with col1:
            nama = st.text_input("Nama")
            tanggal = st.date_input("Tanggal")
            status = st.selectbox("Status", ["Tepat Waktu", "Telat"])
            kelas = st.text_input("Kelas")

        with col2:
            jurusan = st.text_input("Jurusan")
            keterangan = st.text_input("Keterangan")
            nominal = st.number_input("Nominal", min_value=0)

        if st.button("Simpan Data"):
            data = {
                "nama": nama,
                "tanggal": str(tanggal),
                "status": status,
                "kelas": kelas,
                "jurusan": jurusan,
                "keterangan": keterangan,
                "nominal": int(nominal)
            }

            api_post("kas", data)
            st.success("Data berhasil disimpan")
            st.rerun()

        # ================= HAPUS =================
        st.subheader("🗑️ Hapus Data")

        id_hapus = st.number_input("Masukkan ID", step=1)

        if st.button("Hapus"):
            api_delete("kas", int(id_hapus))
            st.success("Data berhasil dihapus")
            st.rerun()

    # ================= PENGELUARAN =================
    elif st.session_state.menu == "pengeluaran":

        st.subheader("💸 Input Pengeluaran")

        tgl = st.date_input("Tanggal")
        ket = st.text_input("Keterangan")
        nom = st.number_input("Nominal", min_value=0)

        if st.button("Simpan Pengeluaran"):
            data = {
                "tanggal": str(tgl),
                "kelas": "-",
                "jurusan": "-",
                "keterangan": ket,
                "nominal": int(nom)
            }

            api_post("pengeluaran", data)
            st.success("Pengeluaran tersimpan")
            st.rerun()

        df_keluar = api_get("pengeluaran")
        df_masuk = api_get("kas")

        if not df_keluar.empty:
            df_keluar["nominal"] = pd.to_numeric(df_keluar["nominal"], errors="coerce").fillna(0)

        if not df_masuk.empty:
            df_masuk["nominal"] = pd.to_numeric(df_masuk["nominal"], errors="coerce").fillna(0)

        total_masuk = df_masuk["nominal"].sum() if not df_masuk.empty else 0
        total_keluar = df_keluar["nominal"].sum() if not df_keluar.empty else 0
        saldo = total_masuk - total_keluar

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Kas", rupiah(total_masuk))
        col2.metric("Pengeluaran", rupiah(total_keluar))
        col3.metric("Saldo", rupiah(saldo))

        if not df_keluar.empty:
            st.subheader("📋 Riwayat Pengeluaran")
            st.dataframe(df_keluar)

            st.download_button(
                "⬇️ Download Pengeluaran (PDF)",
                generate_pdf(df_keluar),
                file_name="data_pengeluaran.pdf"
            )

    # ================= LOGOUT =================
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
