import streamlit as st
import pandas as pd
import hashlib
import requests
import io
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

# ================= CONFIG =================
st.set_page_config(page_title="KAS KITA", layout="wide")

API_URL = "https://script.google.com/macros/s/AKfycbyYoDZMhhhDBf3U3hlGWKepj8f4QkYekuRtx7UK4ctPzNbnlGU3QHPQjtT6C7eaZBix/exec"

# ================= HELPER =================
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def api_get(table):
    try:
        res = requests.get(API_URL, params={
            "action": "get",
            "table": table
        })
        df = pd.DataFrame(res.json())

        # FILTER OWNER (AMAN)
        if not df.empty and "owner" in df.columns:
            df["owner"] = df["owner"].astype(str)
            df = df[df["owner"] == st.session_state.user]

        return df
    except:
        st.error("API ERROR")
        return pd.DataFrame()

def api_post(table, data):
    requests.post(API_URL, json={
        "action": "insert",
        "table": table,
        "data": data
    })

def api_delete(table, id):
    requests.post(API_URL, json={
        "action": "delete",
        "table": table,
        "id": id
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
        df_copy["nominal"] = df_copy["nominal"].astype(int)

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

if "user" not in st.session_state:
    st.session_state.user = ""

# ================= AUTH =================
if not st.session_state.login:

    st.title("💰 KAS KITA")

    tab1, tab2 = st.tabs(["Login", "Register"])

    # LOGIN
    with tab1:
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")

        if st.button("Login"):
            df = pd.DataFrame(requests.get(API_URL, params={
                "action": "get",
                "table": "admin"
            }).json())

            if not df.empty:
                df["username"] = df["username"].astype(str)
                df["password"] = df["password"].astype(str)

                data = df[
                    (df["username"] == user) &
                    (df["password"] == hash_password(pw))
                ]

                if not data.empty:
                    st.session_state.login = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Username / Password salah")

    # REGISTER
    with tab2:
        user = st.text_input("Username Baru")
        pw = st.text_input("Password Baru", type="password")

        if st.button("Daftar"):
            api_post("admin", {
                "username": user,
                "password": hash_password(pw)
            })
            st.success("Akun berhasil dibuat")

# ================= MAIN =================
else:

    st.title("📊 Dashboard KAS")
    st.write(f"👤 User: {st.session_state.user}")

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
            if "tanggal" in df.columns:
                df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
                df["bulan"] = df["tanggal"].dt.strftime("%B %Y")

            df["nominal"] = pd.to_numeric(df["nominal"], errors="coerce").fillna(0)

            # ================= FILTER BULAN =================
            bulan_list = ["Semua"]
            if "bulan" in df.columns:
                bulan_list += sorted(df["bulan"].dropna().unique().tolist())

            bulan = st.selectbox("📅 Filter Bulan", bulan_list)

            if bulan != "Semua":
                df = df[df["bulan"] == bulan]

            # ================= TOTAL =================
            total_kas = df["nominal"].sum()
            st.metric("💰 Total Kas", rupiah(total_kas))

            # ================= GRAFIK =================
            if "bulan" in df.columns:
                grafik = df.groupby("bulan")["nominal"].sum()
                st.bar_chart(grafik)

            # ================= TABEL =================
            st.subheader("📋 Data Kas")
            st.dataframe(df)

            # ================= PDF =================
            st.download_button(
                "⬇️ Download PDF",
                generate_pdf(df),
                "kas.pdf"
            )

            # ================= STATISTIK SISWA =================
            if "nama" in df.columns:
                st.subheader("📊 Statistik Siswa")

                siswa_list = df["nama"].dropna().unique().tolist()
                if siswa_list:
                    siswa = st.selectbox("Pilih Siswa", siswa_list)

                    if st.button("Cek Statistik"):
                        data = df[df["nama"] == siswa]

                        if "status" in df.columns:
                            hasil = data["status"].value_counts()
                            st.bar_chart(hasil)

        else:
            st.warning("Belum ada data kas")

        # ================= TAMBAH DATA =================
        st.subheader("➕ Tambah Data Kas")

        nama = st.text_input("Nama")
        tanggal = st.date_input("Tanggal")
        status = st.selectbox("Status", ["Tepat Waktu", "Telat"])
        kelas = st.text_input("Kelas")
        jurusan = st.text_input("Jurusan")
        keterangan = st.text_input("Keterangan")
        nominal = st.number_input("Nominal", min_value=0)

        if st.button("Simpan Data"):
            api_post("kas", {
                "nama": nama,
                "tanggal": str(tanggal),
                "status": status,
                "kelas": kelas,
                "jurusan": jurusan,
                "keterangan": keterangan,
                "nominal": int(nominal),
                "owner": st.session_state.user
            })
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

        st.title("💸 Pengeluaran")

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
                "⬇️ Download PDF",
                generate_pdf(df_keluar),
                "pengeluaran.pdf"
            )

        # INPUT
        st.subheader("Tambah Pengeluaran")

        tgl = st.date_input("Tanggal")
        ket = st.text_input("Keterangan")
        nom = st.number_input("Nominal", min_value=0)

        if st.button("Simpan Pengeluaran"):
            api_post("pengeluaran", {
                "tanggal": str(tgl),
                "keterangan": ket,
                "nominal": int(nom),
                "owner": st.session_state.user
            })
            st.success("Pengeluaran tersimpan")
            st.rerun()

    # ================= LOGOUT =================
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
