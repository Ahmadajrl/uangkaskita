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
            "action":"get",
            "table":table,
            "owner": st.session_state.user
        })
        return pd.DataFrame(res.json())
    except:
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

    df = df.copy()
    if "nominal" in df.columns:
        df["nominal"] = pd.to_numeric(df["nominal"], errors="coerce").fillna(0)

    data = [df.columns.tolist()] + df.values.tolist()

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('GRID',(0,0),(-1,-1),1,colors.black)
    ]))

    doc.build([table])
    buffer.seek(0)
    return buffer

# ================= SESSION =================
if "login" not in st.session_state:
    st.session_state.login = False
if "user" not in st.session_state:
    st.session_state.user = ""
if "menu" not in st.session_state:
    st.session_state.menu = "dashboard"

# ================= AUTH =================
if not st.session_state.login:

    st.title("💰 KAS KITA")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")

        if st.button("Login"):
            df = requests.get(API_URL, params={"action":"get","table":"admin"}).json()
            df = pd.DataFrame(df)

            if not df.empty:
                data = df[
                    (df["username"] == user) &
                    (df["password"] == hash_password(pw))
                ]

                if not data.empty:
                    st.session_state.login = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Login gagal")

    with tab2:
        user = st.text_input("Username Baru")
        pw = st.text_input("Password Baru", type="password")

        if st.button("Daftar"):
            api_post("admin", {
                "username": user,
                "password": hash_password(pw)
            })
            st.success("Akun dibuat")

# ================= MAIN =================
else:

    # ===== SIDEBAR =====
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user}")

        menu = st.radio(
            "Menu",
            ["Dashboard", "Pengeluaran"]
        )

        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

    # ================= DASHBOARD =================
    if menu == "Dashboard":

        st.title("📊 Dashboard Kas")

        df = api_get("kas")

        if not df.empty:
            df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
            df["nominal"] = pd.to_numeric(df["nominal"], errors="coerce").fillna(0)
            df["bulan"] = df["tanggal"].dt.strftime("%B %Y")

            bulan_list = ["Semua"] + sorted(df["bulan"].dropna().unique())
            bulan = st.selectbox("Filter Bulan", bulan_list)

            df_filtered = df if bulan == "Semua" else df[df["bulan"] == bulan]

            total = df_filtered["nominal"].sum()
            st.metric("Total Kas", rupiah(total))

            st.subheader("Grafik Kas per Bulan")
            grafik = df.groupby("bulan")["nominal"].sum()
            st.bar_chart(grafik)

            st.dataframe(df_filtered)

            st.download_button("Download PDF", generate_pdf(df_filtered), "kas.pdf")

        st.subheader("Tambah Data")
        nama = st.text_input("Nama")
        tanggal = st.date_input("Tanggal")
        status = st.selectbox("Status", ["Tepat Waktu", "Telat"])
        nominal = st.number_input("Nominal", min_value=0)

        if st.button("Simpan"):
            api_post("kas", {
                "nama": nama,
                "tanggal": str(tanggal),
                "status": status,
                "nominal": int(nominal),
                "owner": st.session_state.user
            })
            st.success("Data tersimpan")
            st.rerun()

    # ================= PENGELUARAN =================
    elif menu == "Pengeluaran":

        st.title("💸 Menu Pengeluaran")

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

        st.subheader("Riwayat Pengeluaran")

        if not df_keluar.empty:
            st.dataframe(df_keluar)

            st.download_button(
                "Download PDF",
                generate_pdf(df_keluar),
                "pengeluaran.pdf"
            )
        else:
            st.info("Belum ada data pengeluaran")

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
