import streamlit as st
import pandas as pd
import hashlib
import requests
import io
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

# ================= CONFIG =================
st.set_page_config(page_title="KAS KITA", page_icon="💰", layout="wide")
API_URL = "https://script.google.com/macros/s/AKfycbxaG-pIQP5_-NY8zPZeE_rPMudT7-VC-UsXHZe9P4QjTRYLT2bAGFZI4VVcdgywebAX/exec"

# ================= GLOBAL CSS (SUDAH DIPERBAIKI 100%) =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');
:root { --bg-primary: #080e1d; --bg-card: rgba(255,255,255,0.04); --bg-card-hover: rgba(255,255,255,0.07); --border: rgba(255,255,255,0.08); --accent: #3b82f6; --accent-glow: rgba(59,130,246,0.25); --green: #10b981; --red: #f43f5e; --text-primary: #f1f5f9; --text-muted: #64748b; --radius: 16px; --radius-sm: 10px; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; background-color: var(--bg-primary) !important; color: var(--text-primary) !important; }
.stApp { background: linear-gradient(135deg, #080e1d 0%, #0f1f3d 50%, #080e1d 100%) !important; min-height: 100vh; }
.stApp::before { content: ''; position: fixed; inset: 0; background-image: linear-gradient(rgba(59,130,246,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(59,130,246,0.03) 1px, transparent 1px); background-size: 40px 40px; pointer-events: none; z-index: 0; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0d1932 0%, #080e1d 100%) !important; border-right: 1px solid var(--border) !important; padding-top: 0 !important; }
h1, h2, h3 { font-family: 'Syne', sans-serif !important; letter-spacing: -0.5px; }
.glass-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 24px; backdrop-filter: blur(12px); margin-bottom: 20px; }
.sidebar-logo { padding: 28px 24px 20px; border-bottom: 1px solid var(--border); margin-bottom: 8px; }
.sidebar-logo h2 { font-family: 'Syne', sans-serif !important; font-size: 22px !important; font-weight: 800 !important; background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin: 0 !important; }
.sidebar-user { margin: 0 16px 16px; padding: 14px 16px; background: rgba(59,130,246,0.08); border: 1px solid rgba(59,130,246,0.2); border-radius: var(--radius-sm); display: flex; align-items: center; gap: 12px; }
.user-avatar { width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, #3b82f6, #06b6d4); display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: 700; color: white; font-family: 'Syne', sans-serif; }
.user-info .user-label { font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; }
.user-info .user-name { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.section-divider { height: 1px; background: var(--border); margin: 24px 0; }
.page-header { margin-bottom: 28px; padding-bottom: 20px; border-bottom: 1px solid var(--border); }
.page-header h2 { font-family: 'Syne', sans-serif !important; font-size: 28px !important; font-weight: 800 !important; color: var(--text-primary) !important; margin: 0 0 4px !important; }
.page-header p { color: var(--text-muted); font-size: 14px; margin: 0; }
div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-testid="stDateInput"] input { background: rgba(255,255,255,0.04) !important; border: 1px solid var(--border) !important; border-radius: var(--radius-sm) !important; color: var(--text-primary) !important; padding: 12px 14px !important; }
div[data-testid="stSelectbox"] > div > div { background: rgba(255,255,255,0.04) !important; border: 1px solid var(--border) !important; border-radius: var(--radius-sm) !important; color: var(--text-primary) !important; }
div[data-testid="stButton"] > button { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important; color: white !important; border: none !important; border-radius: var(--radius-sm) !important; padding: 12px 24px !important; width: 100% !important; font-weight: 600 !important; box-shadow: 0 4px 20px rgba(59,130,246,0.3) !important; }
div[data-testid="stDownloadButton"] > button { background: rgba(255,255,255,0.05) !important; color: var(--text-primary) !important; border: 1px solid var(--border) !important; border-radius: var(--radius-sm) !important; width: 100% !important; }
#MainMenu, footer, header { display: none !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ================= HELPER & API =================
def hash_password(p):
    return hashlib.sha256(f"KAS_KITA_SALT_{p}".encode()).hexdigest()

@st.cache_data(ttl=60)
def api_get(table, user):
    try:
        res = requests.get(API_URL, params={"action": "get", "table": table}, timeout=10)
        res.raise_for_status()
        df = pd.DataFrame(res.json())
        if not df.empty and "owner" in df.columns:
            df = df[df["owner"].astype(str) == user]
        return df.reset_index(drop=True)
    except Exception as e:
        st.error(f"Gagal mengambil  {e}")
        return pd.DataFrame()

def api_post(table, data):
    try:
        res = requests.post(API_URL, json={"action": "insert", "table": table, "data": data}, timeout=10)
        res.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Gagal menyimpan  {e}")
        return False

def api_delete(table, id_val):
    try:
        res = requests.post(API_URL, json={"action": "delete", "table": table, "id": id_val}, timeout=10)
        res.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Gagal menghapus  {e}")
        return False

def rupiah(x):
    return f"Rp {int(x):,}".replace(",", ".")

def validasi_kas(nama, kelas, jurusan, nominal):
    if not nama.strip(): return "Nama tidak boleh kosong"
    if len(nama.strip()) < 3: return "Nama terlalu pendek"
    if not kelas.strip(): return "Kelas tidak boleh kosong"
    if not jurusan.strip(): return "Jurusan tidak boleh kosong"
    if nominal <= 0: return "Nominal harus lebih dari 0"
    if nominal > 1_000_000: return "Nominal terlalu besar (Maks 1 Juta)"
    return None

# ================= PDF GENERATOR =================
def generate_pdf(df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    df_copy = df.copy()
    if "nominal" in df_copy.columns:
        df_copy["nominal"] = pd.to_numeric(df_copy["nominal"], errors="coerce").fillna(0).astype(int)
    data = [df_copy.columns.tolist()] + df_copy.values.tolist()
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ]))
    doc.build([table])
    buffer.seek(0)
    return buffer

# ================= SESSION INIT =================
defaults = {"login": False, "menu": "dashboard", "user": "", "kas_data": pd.DataFrame(), "pengeluaran_data": pd.DataFrame()}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# ================= AUTH =================
if not st.session_state.login:
    st.markdown("<div style='max-width:440px; margin:60px auto; text-align:center;'><h1 style='font-size:42px; font-weight:800; background:linear-gradient(135deg,#3b82f6,#06b6d4); -webkit-background-clip:text; color:transparent;'>💰 KAS KITA</h1><p style='color:#64748b;'>Sistem Manajemen Keuangan</p></div>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Login", "Daftar Akun"])
    
    with tab1:
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.button("Masuk", use_container_width=True):
            if not user or not pw:
                st.warning("Username dan password wajib diisi")
            else:
                with st.spinner("Memverifikasi..."):
                    try:
                        res = requests.get(API_URL, params={"action": "get", "table": "admin"}, timeout=10)
                        res.raise_for_status()
                        df = pd.DataFrame(res.json())
                    except:
                        st.error("Gagal terhubung ke server"); st.stop()
                if not df.empty:
                    df["username"] = df["username"].astype(str)
                    df["password"] = df["password"].astype(str)
                    match = df[(df["username"] == user.strip()) & (df["password"] == hash_password(pw))]
                    if not match.empty:
                        st.session_state.login = True
                        st.session_state.user = user.strip()
                        st.session_state.kas_data = api_get("kas", st.session_state.user)
                        st.session_state.pengeluaran_data = api_get("pengeluaran", st.session_state.user)
                        st.rerun()
                    else:
                        st.error("Username / Password salah")

    with tab2:
        user = st.text_input("Username Baru")
        pw = st.text_input("Password Baru", type="password")
        if st.button("Daftar", use_container_width=True):
            if not user or not pw: st.warning("Wajib diisi")
            elif len(pw) < 6: st.warning("Password minimal 6 karakter")
            else:
                if api_post("admin", {"username": user.strip(), "password": hash_password(pw)}):
                    st.success("Akun dibuat! Silakan login.")
                else:
                    st.error("Gagal membuat akun")

# ================= MAIN APP =================
else:
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-logo"><h2>💰 KAS KITA</h2></div>
        <div class="sidebar-user">
            <div class="user-avatar">{st.session_state.user[0].upper()}</div>
            <div class="user-info"><div class="user-label">AKTIF</div><div class="user-name">{st.session_state.user}</div></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        menu = st.radio("Menu Utama", ["📊 Dashboard", "💸 Pengeluaran"], key="sidebar_menu")
        st.session_state.menu = menu.split()[-1].lower()
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            for k in ["login", "user", "menu", "kas_data", "pengeluaran_data"]:
                st.session_state.pop(k, None)
            st.rerun()

    st.markdown(f"""<div class="page-header"><h2>{menu}</h2><p>Kelola data keuangan secara transparan.</p></div>""", unsafe_allow_html=True)

    # ================= DASHBOARD =================
    if st.session_state.menu == "dashboard":
        df = st.session_state.kas_data.copy()
        if not df.empty:
            if "tanggal" in df.columns:
                df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
                df["bulan"] = df["tanggal"].dt.strftime("%B %Y")
            df["nominal"] = pd.to_numeric(df["nominal"], errors="coerce").fillna(0)
            
            bulan_list = ["Semua"] + sorted(df["bulan"].dropna().unique().tolist())
            bulan = st.selectbox("Filter Bulan", bulan_list)
            if bulan != "Semua": df = df[df["bulan"] == bulan]
            
            st.metric("Total Kas Masuk", rupiah(df["nominal"].sum()))
            if "bulan" in df.columns: st.bar_chart(df.groupby("bulan")["nominal"].sum(), use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button("📥 Export PDF", generate_pdf(df), f"kas_{st.session_state.user}.pdf", "application/pdf")
        else:
            st.warning("Belum ada data kas.")

        st.subheader("Tambah Data Kas")
        c1, c2 = st.columns(2)
        with c1:
            nama = st.text_input("Nama Lengkap"); kelas = st.text_input("Kelas"); jurusan = st.text_input("Jurusan")
        with c2:
            tgl = st.date_input("Tanggal"); status = st.selectbox("Status", ["Tepat Waktu", "Telat"]); nominal = st.number_input("Nominal", min_value=0, step=1000)
        ket = st.text_input("Keterangan")
        
        if st.button("Simpan Kas", use_container_width=True):
            err = validasi_kas(nama, kelas, jurusan, nominal)
            if err: st.error(f"❌ {err}")
            elif api_post("kas", {"nama": nama.strip(), "tanggal": str(tgl), "status": status, "kelas": kelas.strip(), "jurusan": jurusan.strip(), "keterangan": ket.strip(), "nominal": int(nominal), "owner": st.session_state.user}):
                st.session_state.kas_data = api_get("kas", st.session_state.user)
                st.success("Tersimpan"); st.rerun()

    # ================= PENGELUARAN (SESUAI REQUEST) =================
    elif st.session_state.menu == "pengeluaran":
        df_keluar = st.session_state.pengeluaran_data.copy()
        df_masuk = st.session_state.kas_data.copy()
        
        total_masuk = pd.to_numeric(df_masuk["nominal"], errors="coerce").fillna(0).sum() if not df_masuk.empty else 0
        total_keluar = pd.to_numeric(df_keluar["nominal"], errors="coerce").fillna(0).sum() if not df_keluar.empty else 0
        saldo = total_masuk - total_keluar
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Kas Masuk", rupiah(total_masuk))
        c2.metric("Pengeluaran", rupiah(total_keluar))
        c3.metric("Sisa Saldo", rupiah(saldo))
        
        if not df_keluar.empty:
            st.dataframe(df_keluar, use_container_width=True, hide_index=True)
            st.download_button("📥 Export PDF Pengeluaran", generate_pdf(df_keluar), f"pengeluaran_{st.session_state.user}.pdf", "application/pdf")
            
        st.subheader("Catat Pengeluaran")
        tgl = st.date_input("Tanggal")
        ket = st.text_input("Keterangan")
        nom = st.number_input("Nominal", min_value=0, step=1000)
        
        if st.button("Simpan Pengeluaran", use_container_width=True):
            if not ket.strip():
                st.warning("Keterangan wajib diisi")
            elif nom <= 0:
                st.warning("Nominal harus lebih dari 0")
            elif nom > saldo:
                st.error(f"⚠️ Saldo tidak cukup! Sisa saldo: {rupiah(saldo)}")
            else:
                if api_post("pengeluaran", {"tanggal": str(tgl), "keterangan": ket.strip(), "nominal": int(nom), "owner": st.session_state.user}):
                    st.session_state.pengeluaran_data = api_get("pengeluaran", st.session_state.user)
                    st.success("Pengeluaran tersimpan")
                    st.rerun()
