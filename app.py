import streamlit as st
import pandas as pd
import hashlib
import requests
import io
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

# ================= CONFIG =================
st.set_page_config(
    page_title="KAS KITA",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "https://script.google.com/macros/s/AKfycbyYoDZMhhhDBf3U3hlGWKepj8f4QkYekuRtx7UK4ctPzNbnlGU3QHPQjtT6C7eaZBix/exec"

# ================= STYLE =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#0f172a,#1e293b);
    color: white;
}
.block-container {
    padding: 1rem;
}
.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 16px;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# ================= HELPER =================
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def api_get(table):
    try:
        res = requests.get(API_URL, params={"action":"get","table":table})
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

    # SIDEBAR
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user}")

        if st.button("📊 Dashboard"):
            st.session_state.menu = "dashboard"

        if st.button("💸 Pengeluaran"):
            st.session_state.menu = "pengeluaran"

        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.rerun()

    # ================= DASHBOARD =================
    if st.session_state.menu == "dashboard":

        st.title("📊 Dashboard Kas")

        df = api_get("kas")

        if not df.empty:

            # FILTER USER (PENTING)
            df = df[df["owner"] == st.session_state.user]

            df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
            df["nominal"] = pd.to_numeric(df["nominal"], errors="coerce").fillna(0)
            df["bulan"] = df["tanggal"].dt.strftime("%B %Y")

            # FILTER BULAN
            bulan_list = ["Semua"] + sorted(df["bulan"].dropna().unique().tolist())
            bulan = st.selectbox("📅 Filter Bulan", bulan_list)

            if bulan != "Semua":
                df = df[df["bulan"] == bulan]

            total = df["nominal"].sum()

            st.markdown(f"<div class='card'>💰 Total Kas: {rupiah(total)}</div>", unsafe_allow_html=True)

            # GRAFIK
            grafik = df.groupby("bulan")["nominal"].sum()
            st.bar_chart(grafik)

            st.dataframe(df)

            st.download_button(
                "Download PDF",
                generate_pdf(df),
                "kas.pdf"
            )

        # INPUT DATA
        st.subheader("Tambah Data")

        nama = st.text_input("Nama")
        tanggal = st.date_input("Tanggal")
        nominal = st.number_input("Nominal", min_value=0)

        if st.button("Simpan"):
            api_post("kas", {
                "nama": nama,
                "tanggal": str(tanggal),
                "nominal": int(nominal),
                "owner": st.session_state.user
            })
            st.success("Tersimpan")
            st.rerun()

    # ================= PENGELUARAN =================
    elif st.session_state.menu == "pengeluaran":

        st.title("💸 Pengeluaran")

        df = api_get("pengeluaran")

        if not df.empty:
            df = df[df["owner"] == st.session_state.user]
            df["nominal"] = pd.to_numeric(df["nominal"], errors="coerce").fillna(0)

            total = df["nominal"].sum()
            st.markdown(f"<div class='card'>Total Pengeluaran: {rupiah(total)}</div>", unsafe_allow_html=True)

            st.dataframe(df)

            st.download_button(
                "Download PDF",
                generate_pdf(df),
                "pengeluaran.pdf"
            )

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
            st.success("Tersimpan")
            st.rerun()
