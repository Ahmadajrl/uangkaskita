import streamlit as st
import pandas as pd
import hashlib
import requests
import io
import os
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

# ================= CONFIG =================
st.set_page_config(
    page_title="KAS KITA",
    page_icon="💰",
    layout="wide"
)

# Gunakan st.secrets untuk keamanan, dengan fallback ke URL default
API_URL = st.secrets.get("API_URL", "https://script.google.com/macros/s/AKfycbxBe2m5pZoJOofUKqvf7oRrAt_UARgQ3W3pVwUYFMQVwJgMsLb3pb-7jg1rOJRgm8xz/exec")

# ================= GLOBAL CSS (SUDAH DIPERBAIKI) =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg-primary:    #080e1d;
    --bg-card:       rgba(255,255,255,0.04);
    --bg-card-hover: rgba(255,255,255,0.07);
    --border:        rgba(255,255,255,0.08);
    --accent:        #3b82f6;
    --accent-glow:   rgba(59,130,246,0.25);
    --accent2:       #06b6d4;
    --green:         #10b981;
    --red:           #f43f5e;
    --gold:          #f59e0b;
    --text-primary:  #f1f5f9;
    --text-muted:    #64748b;
    --radius:        16px;
    --radius-sm:     10px;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

.stApp {
    background: linear-gradient(135deg, #080e1d 0%, #0f1f3d 50%, #080e1d 100%) !important;
    min-height: 100vh;
}

.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(59,130,246,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(59,130,246,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1932 0%, #080e1d 100%) !important;
    border-right: 1px solid var(--border) !important;
    padding-top: 0 !important;
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    letter-spacing: -0.5px;
}

.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px 20px;
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
    backdrop-filter: blur(12px);
}
.metric-card:hover {
    background: var(--bg-card-hover);
    border-color: rgba(59,130,246,0.3);
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(59,130,246,0.12);
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    border-radius: var(--radius) var(--radius) 0 0;
}
.metric-card.blue::before  { background: linear-gradient(90deg, #3b82f6, #06b6d4); }
.metric-card.green::before { background: linear-gradient(90deg, #10b981, #34d399); }
.metric-card.red::before   { background: linear-gradient(90deg, #f43f5e, #fb7185); }
.metric-card.gold::before  { background: linear-gradient(90deg, #f59e0b, #fbbf24); }

.metric-label { font-size: 11px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; color: var(--text-muted); margin-bottom: 10px; }
.metric-value { font-family: 'Syne', sans-serif; font-size: 26px; font-weight: 800; color: var(--text-primary); line-height: 1.1; }
.metric-icon { position: absolute; top: 20px; right: 20px; font-size: 24px; opacity: 0.25; }

.glass-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 28px; backdrop-filter: blur(12px); margin-bottom: 20px; }
.glass-card-title { font-family: 'Syne', sans-serif; font-size: 15px; font-weight: 700; color: var(--text-primary); margin-bottom: 18px; display: flex; align-items: center; gap: 8px; }

.auth-wrapper { max-width: 440px; margin: 40px auto; }
.auth-logo { text-align: center; margin-bottom: 36px; }
.auth-logo h1 { font-family: 'Syne', sans-serif !important; font-size: 42px !important; font-weight: 800 !important; background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin: 0 !important; }
.auth-logo p { color: var(--text-muted); font-size: 14px; margin-top: 4px; }

.sidebar-logo { padding: 28px 24px 20px; border-bottom: 1px solid var(--border); margin-bottom: 8px; }
.sidebar-logo h2 { font-family: 'Syne', sans-serif !important; font-size: 22px !important; font-weight: 800 !important; background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin: 0 !important; }
.sidebar-logo .tagline { font-size: 11px; color: var(--text-muted); margin-top: 2px; letter-spacing: 0.5px; }

.sidebar-user { margin: 0 16px 16px; padding: 14px 16px; background: rgba(59,130,246,0.08); border: 1px solid rgba(59,130,246,0.2); border-radius: var(--radius-sm); display: flex; align-items: center; gap: 12px; }
.user-avatar { width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, #3b82f6, #06b6d4); display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: 700; color: white; font-family: 'Syne', sans-serif; flex-shrink: 0; }
.user-info .user-label { font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; }
.user-info .user-name { font-size: 14px; font-weight: 600; color: var(--text-primary); }

.section-divider { height: 1px; background: var(--border); margin: 24px 0; }
.page-header { margin-bottom: 28px; padding-bottom: 20px; border-bottom: 1px solid var(--border); }
.page-header h2 { font-family: 'Syne', sans-serif !important; font-size: 28px !important; font-weight: 800 !important; color: var(--text-primary) !important; margin: 0 0 4px !important; }
.page-header p { color: var(--text-muted); font-size: 14px; margin: 0; }

div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stDateInput"] input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: border-color 0.2s !important;
    padding: 12px 14px !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stNumberInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
    outline: none !important;
}
div[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
}
div[data-testid="stTextInput"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stDateInput"] label,
div[data-testid="stTextArea"] label {
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    color: var(--text-muted) !important;
    text-transform: uppercase !important;
}
div[data-testid="stButton"] > button[kind="primary"],
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 12px 24px !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 20px rgba(59,130,246,0.3) !important;
    letter-spacing: 0.3px !important;
}
div[data-testid="stButton"] > button:hover { transform: translateY(-1px) !important; box-shadow: 0 8px 30px rgba(59,130,246,0.45) !important; filter: brightness(1.08) !important; }
div[data-testid="stDownloadButton"] > button {
    background: rgba(255,255,255,0.05) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stDownloadButton"] > button:hover { border-color: var(--accent) !important; color: var(--accent) !important; background: rgba(59,130,246,0.08) !important; }

div[data-testid="stTabs"] [data-baseweb="tab-list"] { background: rgba(255,255,255,0.03) !important; border-radius: var(--radius-sm) !important; border: 1px solid var(--border) !important; padding: 4px !important; gap: 4px !important; }
div[data-testid="stTabs"] [data-baseweb="tab"] { border-radius: 8px !important; color: var(--text-muted) !important; font-family: 'DM Sans', sans-serif !important; font-weight: 500 !important; }
div[data-testid="stTabs"] [aria-selected="true"] { background: linear-gradient(135deg, #3b82f6, #2563eb) !important; color: white !important; }

div[data-testid="stDataFrame"] { border-radius: var(--radius-sm) !important; overflow: hidden !important; border: 1px solid var(--border) !important; }
div[data-testid="stDataFrame"] table { background: var(--bg-card) !important; }
div[data-testid="stAlert"] { border-radius: var(--radius-sm) !important; border: none !important; }
div[data-testid="stMetric"] { background: var(--bg-card) !important; border: 1px solid var(--border) !important; border-radius: var(--radius) !important; padding: 20px !important; }
div[data-testid="stArrowVegaLiteChart"] { border-radius: var(--radius-sm) !important; overflow: hidden !important; }

.nav-btn button { background: transparent !important; border: none !important; box-shadow: none !important; color: var(--text-muted) !important; font-size: 14px !important; font-weight: 500 !important; text-align: left !important; border-radius: var(--radius-sm) !important; padding: 12px 16px !important; margin: 2px 0 !important; transition: all 0.2s !important; }
.nav-btn button:hover { background: rgba(59,130,246,0.1) !important; color: var(--accent) !important; transform: none !important; box-shadow: none !important; }
.nav-btn-active button { background: rgba(59,130,246,0.15) !important; border: none !important; box-shadow: none !important; color: var(--accent) !important; font-weight: 600 !important; }

.logout-btn button { background: rgba(244,63,94,0.08) !important; border: 1px solid rgba(244,63,94,0.2) !important; color: #f43f5e !important; box-shadow: none !important; font-size: 14px !important; border-radius: var(--radius-sm) !important; padding: 12px 16px !important; transition: all 0.2s !important; }
.logout-btn button:hover { background: rgba(244,63,94,0.15) !important; transform: none !important; box-shadow: none !important; }

div[data-testid="stTextInput"] [data-testid="InputInstructions"] { display: none; }
#MainMenu, footer, header { display: none !important; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

@media (max-width: 768px) {
    .metric-value { font-size: 20px; }
    .glass-card { padding: 20px 16px; }
}
</style>
""", unsafe_allow_html=True)

# ================= HELPER =================
def hash_password(p):
    # Catatan: Gunakan bcrypt untuk production. Ini hanya untuk kompatibilitas cepat.
    salt = "KAS_KITA_SALT_2024"
    return hashlib.sha256(f"{salt}{p}".encode()).hexdigest()

@st.cache_data(ttl=60)
def api_get(table, user):
    try:
        res = requests.get(API_URL, params={"action": "get", "table": table}, timeout=10)
        res.raise_for_status()
        df = pd.DataFrame(res.json())
        if not df.empty and "owner" in df.columns:
            df["owner"] = df["owner"].astype(str)
            df = df[df["owner"] == user]
        return df
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal mengambil data API: {e}")
        return pd.DataFrame()

def api_post(table, data):
    try:
        res = requests.post(API_URL, json={"action": "insert", "table": table, "data": data}, timeout=10)
        res.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal menyimpan data: {e}")
        return False

def api_delete(table, id_val):
    try:
        res = requests.post(API_URL, json={"action": "delete", "table": table, "id": id_val}, timeout=10)
        res.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal menghapus data: {e}")
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

# ================= PDF =================
def generate_pdf(df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    df_copy = df.copy()
    
    if "nominal" in df_copy.columns:
        df_copy["nominal"] = pd.to_numeric(df_copy["nominal"], errors="coerce").fillna(0).astype(int)
        
    data = [df_copy.columns.tolist()] + df_copy.values.tolist()
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    doc.build([table])
    buffer.seek(0)
    return buffer

# ================= SESSION INIT =================
for key in ["login", "user", "menu", "kas_data", "pengeluaran_data", "delete_confirm"]:
    if key not in st.session_state:
        st.session_state[key] = False if key in ["login"] else ("dashboard" if key == "menu" else ("" if key == "user" else None))

# ================= AUTH =================
if not st.session_state.login:
    st.title("Buat Akun")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            if not user or not pw:
                st.warning("Username dan password wajib diisi")
            else:
                with st.spinner("Memverifikasi akun..."):
                    df = pd.DataFrame(requests.get(API_URL, params={"action": "get", "table": "admin"}, timeout=10).json())
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
                else:
                    st.error("Database admin kosong atau gagal terhubung.")

    with tab2:
        user = st.text_input("Username Baru")
        pw = st.text_input("Password Baru", type="password")
        if st.button("Daftar", use_container_width=True):
            if not user or not pw:
                st.warning("Username & Password wajib diisi")
            elif len(pw) < 6:
                st.warning("Password minimal 6 karakter")
            else:
                if api_post("admin", {"username": user.strip(), "password": hash_password(pw)}):
                    st.success("Akun berhasil dibuat. Silakan login.")
                else:
                    st.error("Gagal mendaftarkan akun.")

# ================= MAIN APP =================
else:<think>
# Sidebar Navigation & Layout
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">
            <h2>💰 KAS KITA</h2>
            <p class="tagline">Manajemen Keuangan Kelas</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="sidebar-user">
            <div class="user-avatar">{st.session_state.user[0].upper()}</div>
            <div class="user-info">
                <div class="user-label">Sedang Login</div>
                <div class="user-name">{st.session_state.user}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        menu = st.radio("Menu", ["Dashboard", "Pengeluaran"], key="sidebar_menu")
        st.session_state.menu = menu.lower()
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            for k in ["login", "user", "menu", "kas_data", "pengeluaran_data", "delete_confirm"]:
                st.session_state.pop(k, None)
            st.rerun()

    st.markdown(f"""
    <div class="page-header">
        <h2>{menu}</h2>
        <p>Kelola data keuangan dengan mudah dan transparan.</p>
    </div>
    """, unsafe_allow_html=True)

    # ================= DASHBOARD =================
    if st.session_state.menu == "dashboard":
        df = st.session_state.kas_data.copy()
        
        if not df.empty:
            if "tanggal" in df.columns:
                df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
                df["bulan"] = df["tanggal"].dt.strftime("%B %Y")
            df["nominal"] = pd.to_numeric(df["nominal"], errors="coerce").fillna(0)
            
            bulan_list = ["Semua"]
            if "bulan" in df.columns:
                bulan_list += sorted(df["bulan"].dropna().unique().tolist())
                
            bulan = st.selectbox("Filter Bulan", bulan_list)
            if bulan != "Semua":
                df = df[df["bulan"] == bulan]
                
            total_kas = df["nominal"].sum()
            st.metric("Total Kas", rupiah(total_kas))
            
            if "bulan" in df.columns and not df.empty:
                grafik = df.groupby("bulan")["nominal"].sum()
                st.bar_chart(grafik, use_container_width=True)
                
            st.subheader("Data Kas")
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            pdf_buffer = generate_pdf(df)
            st.download_button("📥 Download PDF", pdf_buffer, "kas.pdf", "application/pdf")
            
            # Statistik Siswa
            if "nama" in df.columns:
                st.subheader("Statistik Siswa")
                siswa_list = df["nama"].dropna().unique().tolist()
                if siswa_list:
                    siswa = st.selectbox("Pilih Siswa", siswa_list)
                    data_siswa = df[df["nama"] == siswa]
                    if not data_siswa.empty and "status" in data_siswa.columns:
                        hasil = data_siswa["status"].value_counts()
                        st.bar_chart(hasil, use_container_width=True)
        else:
            st.warning("Belum ada data kas.")

        # Tambah Data
        st.subheader("Tambah Data Kas")
        col1, col2 = st.columns(2)
        with col1:
            nama = st.text_input("Nama Lengkap")
            kelas = st.text_input("Kelas")
            jurusan = st.text_input("Jurusan")
        with col2:
            tanggal = st.date_input("Tanggal Pembayaran")
            status = st.selectbox("Status", ["Tepat Waktu", "Telat"])
            nominal = st.number_input("Nominal", min_value=0, step=1000)
            
        keterangan = st.text_input("Keterangan (contoh: Lunas)")
        
        if st.button("Simpan Data", use_container_width=True):
            error = validasi_kas(nama, kelas, jurusan, nominal)
            if error:
                st.error(f"❌ {error}")
            else:
                if api_post("kas", {
                    "nama": nama.strip(), "tanggal": str(tanggal), "status": status,
                    "kelas": kelas.strip(), "jurusan": jurusan.strip(), "keterangan": keterangan.strip(),
                    "nominal": int(nominal), "owner": st.session_state.user
                }):
                    st.session_state.kas_data = api_get("kas", st.session_state.user)
                    st.success("Data berhasil disimpan")
                    st.rerun()

        # Hapus Data (Safe)
        st.subheader("Hapus Data Kas")
        if not st.session_state.kas_data.empty and "id" in st.session_state.kas_data.columns:
            df_hapus = st.session_state.kas_data.copy()
            df_hapus["label"] = df_hapus.apply(lambda x: f"ID: {x['id']} | {x.get('nama', '-')} - {rupiah(x['nominal'])}", axis=1)
            
            id_hapus = st.selectbox("Pilih Data untuk Dihapus", df_hapus["id"], format_func=lambda x: df_hapus[df_hapus["id"]==x]["label"].iloc[0])
            
            if st.button("🗑️ Hapus Data Terpilih", type="primary", use_container_width=True):
                st.session_state.delete_confirm = id_hapus
                st.rerun()
                
            if st.session_state.delete_confirm == id_hapus:
                st.warning("⚠️ Tindakan ini tidak dapat dibatalkan. Ketik `HAPUS` untuk konfirmasi.")
                conf = st.text_input("Konfirmasi")
                if conf.upper() == "HAPUS" and st.button("Ya, Hapus Sekarang", type="primary"):
                    if api_delete("kas", int(id_hapus)):
                        st.session_state.kas_data = api_get("kas", st.session_state.user)
                        st.session_state.delete_confirm = None
                        st.success("Data berhasil dihapus")
                        st.rerun()
        else:
            st.info("Tidak ada data untuk dihapus.")

    # ================= PENGELUARAN =================
    elif st.session_state.menu == "pengeluaran":
        df_keluar = st.session_state.pengeluaran_data.copy()
        df_masuk = st.session_state.kas_data.copy()
        
        if not df_keluar.empty:
            df_keluar["nominal"] = pd.to_numeric(df_keluar["nominal"], errors="coerce").fillna(0)
        if not df_masuk.empty:
            df_masuk["nominal"] = pd.to_numeric(df_masuk["nominal"], errors="coerce").fillna(0)
            
        total_masuk = df_masuk["nominal"].sum() if not df_masuk.empty else 0
        total_keluar = df_keluar["nominal"].sum() if not df_keluar.empty else 0
        saldo = total_masuk - total_keluar
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Kas Masuk", rupiah(total_masuk))
        col2.metric("Total Pengeluaran", rupiah(total_keluar))
        col3.metric("Sisa Saldo", rupiah(saldo))
        
        if not df_keluar.empty:
            st.subheader("Riwayat Pengeluaran")
            st.dataframe(df_keluar, use_container_width=True, hide_index=True)
            pdf_buffer = generate_pdf(df_keluar)
            st.download_button("📥 Download PDF Pengeluaran", pdf_buffer, "pengeluaran.pdf", "application/pdf")
        else:
            st.info("Belum ada riwayat pengeluaran.")
            
        # Input Pengeluaran
        st.subheader("Tambah Pengeluaran")
        tgl = st.date_input("Tanggal")
        ket = st.text_input("Keterangan")
        nom = st.number_input("Nominal Pengeluaran", min_value=0, step=1000)
        
        if st.button("Simpan Pengeluaran", use_container_width=True):
            if not ket.strip():
                st.warning("Keterangan wajib diisi")
            elif nom <= 0:
                st.warning("Nominal harus lebih dari 0")
            elif nom > saldo:
                st.error(f"⚠️ Saldo tidak cukup! Sisa saldo: {rupiah(saldo)}")
            else:
                if api_post("pengeluaran", {
                    "tanggal": str(tgl), "keterangan": ket.strip(), "nominal": int(nom), "owner": st.session_state.user
                }):
                    st.session_state.pengeluaran_data = api_get("pengeluaran", st.session_state.user)
                    st.success("Pengeluaran tersimpan")
                    st.rerun()
