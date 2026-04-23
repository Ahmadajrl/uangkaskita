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

API_URL = "https://script.google.com/macros/s/AKfycbym98CvlKkmJ2BawYlaEEqGKkN5BTdEcmvWdfzB2B6J_zSBY8he0S1r7e70T8phQ3nR/exec"

# ================= GLOBAL CSS =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ===== ROOT THEME ===== */
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

/* ===== GLOBAL ===== */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

.stApp {
    background: linear-gradient(135deg, #080e1d 0%, #0f1f3d 50%, #080e1d 100%) !important;
    min-height: 100vh;
}

/* Subtle animated grid bg */
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

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1932 0%, #080e1d 100%) !important;
    border-right: 1px solid var(--border) !important;
    padding-top: 0 !important;
}

section[data-testid="stSidebar"] > div {
    padding: 0 !important;
}

/* ===== HEADINGS ===== */
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    letter-spacing: -0.5px;
}

/* ===== METRIC CARDS ===== */
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

.metric-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 10px;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 26px;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1.1;
}
.metric-icon {
    position: absolute;
    top: 20px; right: 20px;
    font-size: 24px;
    opacity: 0.25;
}

/* ===== GLASS CARD ===== */
.glass-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 28px;
    backdrop-filter: blur(12px);
    margin-bottom: 20px;
}
.glass-card-title {
    font-family: 'Syne', sans-serif;
    font-size: 15px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ===== AUTH PAGE ===== */
.auth-wrapper {
    max-width: 440px;
    margin: 40px auto;
}
.auth-logo {
    text-align: center;
    margin-bottom: 36px;
}
.auth-logo h1 {
    font-family: 'Syne', sans-serif !important;
    font-size: 42px !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 !important;
}
.auth-logo p {
    color: var(--text-muted);
    font-size: 14px;
    margin-top: 4px;
}

/* ===== SIDEBAR LOGO ===== */
.sidebar-logo {
    padding: 28px 24px 20px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 8px;
}
.sidebar-logo h2 {
    font-family: 'Syne', sans-serif !important;
    font-size: 22px !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 !important;
}
.sidebar-logo .tagline {
    font-size: 11px;
    color: var(--text-muted);
    margin-top: 2px;
    letter-spacing: 0.5px;
}

/* ===== SIDEBAR USER ===== */
.sidebar-user {
    margin: 0 16px 16px;
    padding: 14px 16px;
    background: rgba(59,130,246,0.08);
    border: 1px solid rgba(59,130,246,0.2);
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    gap: 12px;
}
.user-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, #3b82f6, #06b6d4);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    font-weight: 700;
    color: white;
    font-family: 'Syne', sans-serif;
    flex-shrink: 0;
}
.user-info .user-label {
    font-size: 10px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
}
.user-info .user-name {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
}

/* ===== DIVIDER ===== */
.section-divider {
    height: 1px;
    background: var(--border);
    margin: 24px 0;
}

/* ===== PAGE HEADER ===== */
.page-header {
    margin-bottom: 28px;
    padding-bottom: 20px;
    border-bottom: 1px solid var(--border);
}
.page-header h2 {
    font-family: 'Syne', sans-serif !important;
    font-size: 28px !important;
    font-weight: 800 !important;
    color: var(--text-primary) !important;
    margin: 0 0 4px !important;
}
.page-header p {
    color: var(--text-muted);
    font-size: 14px;
    margin: 0;
}

/* ===== STREAMLIT OVERRIDES ===== */

/* Inputs */
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

/* Select */
div[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
}

/* Labels */
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

/* Primary buttons */
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
div[data-testid="stButton"] > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 30px rgba(59,130,246,0.45) !important;
    filter: brightness(1.08) !important;
}
div[data-testid="stButton"] > button:active {
    transform: translateY(0) !important;
}

/* Download button */
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
div[data-testid="stDownloadButton"] > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    background: rgba(59,130,246,0.08) !important;
}

/* Tabs */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03) !important;
    border-radius: var(--radius-sm) !important;
    border: 1px solid var(--border) !important;
    padding: 4px !important;
    gap: 4px !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: var(--text-muted) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
}
div[data-testid="stTabs"] [aria-selected="true"] {
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
    color: white !important;
}

/* Dataframe */
div[data-testid="stDataFrame"] {
    border-radius: var(--radius-sm) !important;
    overflow: hidden !important;
    border: 1px solid var(--border) !important;
}
div[data-testid="stDataFrame"] table {
    background: var(--bg-card) !important;
}

/* Alerts / warnings */
div[data-testid="stAlert"] {
    border-radius: var(--radius-sm) !important;
    border: none !important;
}

/* Metric (fallback) */
div[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 20px !important;
}

/* Bar chart */
div[data-testid="stArrowVegaLiteChart"] {
    border-radius: var(--radius-sm) !important;
    overflow: hidden !important;
}

/* Sidebar nav buttons */
.nav-btn button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: var(--text-muted) !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    text-align: left !important;
    border-radius: var(--radius-sm) !important;
    padding: 12px 16px !important;
    margin: 2px 0 !important;
    transition: all 0.2s !important;
}
.nav-btn button:hover {
    background: rgba(59,130,246,0.1) !important;
    color: var(--accent) !important;
    transform: none !important;
    box-shadow: none !important;
}
.nav-btn-active button {
    background: rgba(59,130,246,0.15) !important;
    border: none !important;
    box-shadow: none !important;
    color: var(--accent) !important;
    font-weight: 600 !important;
}

/* Logout button special */
.logout-btn button {
    background: rgba(244,63,94,0.08) !important;
    border: 1px solid rgba(244,63,94,0.2) !important;
    color: #f43f5e !important;
    box-shadow: none !important;
    font-size: 14px !important;
    border-radius: var(--radius-sm) !important;
    padding: 12px 16px !important;
    transition: all 0.2s !important;
}
.logout-btn button:hover {
    background: rgba(244,63,94,0.15) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* Password type toggle */
div[data-testid="stTextInput"] [data-testid="InputInstructions"] {
    display: none;
}

/* Hide streamlit branding */
#MainMenu, footer, header { display: none !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

/* Mobile responsive */
@media (max-width: 768px) {
    .metric-value { font-size: 20px; }
    .glass-card { padding: 20px 16px; }
}
</style>
""", unsafe_allow_html=True)

# ================= HELPER =================
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def api_get(table):
    try:
        res = requests.get(API_URL, params={"action": "get", "table": table})
        df = pd.DataFrame(res.json())
        if not df.empty and "owner" in df.columns:
            df["owner"] = df["owner"].astype(str)
            df = df[df["owner"] == st.session_state.user]
        return df
    except:
        st.error("❌ Gagal menghubungi server. Periksa koneksi internet Anda.")
        return pd.DataFrame()

def api_post(table, data):
    requests.post(API_URL, json={"action": "insert", "table": table, "data": data})

def api_delete(table, id):
    requests.post(API_URL, json={"action": "delete", "table": table, "id": id})

def rupiah(x):
    return f"Rp {int(x):,}".replace(",", ".")

def rupiah_short(x):
    x = int(x)
    if x >= 1_000_000:
        return f"Rp {x/1_000_000:.1f}jt"
    elif x >= 1_000:
        return f"Rp {x/1_000:.0f}rb"
    return rupiah(x)

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
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2d3748')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.white]),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    doc.build([table])
    buffer.seek(0)
    return buffer

# ================= METRIC CARD =================
def metric_card(label, value, icon, color="blue", sub=None):
    sub_html = f'<div style="font-size:12px;color:#64748b;margin-top:6px;">{sub}</div>' if sub else ""
    st.markdown(f"""
    <div class="metric-card {color}">
        <div class="metric-icon">{icon}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)

# ================= SESSION =================
if "login" not in st.session_state:
    st.session_state.login = False
if "menu" not in st.session_state:
    st.session_state.menu = "dashboard"
if "user" not in st.session_state:
    st.session_state.user = ""

# ================= AUTH PAGE =================
if not st.session_state.login:

    # Center auth card
    col_l, col_c, col_r = st.columns([1, 1.5, 1])
    with col_c:
        st.markdown("""
        <div class="auth-logo">
            <h1>💰 KAS KITA</h1>
            <p>Sistem Manajemen Keuangan Sekolah</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔐  Masuk", "📝  Daftar"])

        # LOGIN
        with tab1:
            user = st.text_input("Username", placeholder="Masukkan username", key="login_user")
            pw = st.text_input("Password", type="password", placeholder="Masukkan password", key="login_pw")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Masuk ke Dashboard →", key="btn_login"):
                with st.spinner("Memverifikasi akun..."):
                    try:
                        df = pd.DataFrame(requests.get(API_URL, params={
                            "action": "get", "table": "admin"
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
                                st.error("❌ Username atau Password salah")
                    except:
                        st.error("❌ Gagal terhubung ke server")

        # REGISTER
        with tab2:
            new_user = st.text_input("Username Baru", placeholder="Pilih username", key="reg_user")
            new_pw = st.text_input("Password Baru", type="password", placeholder="Buat password kuat", key="reg_pw")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Buat Akun →", key="btn_register"):
                if new_user and new_pw:
                    with st.spinner("Membuat akun..."):
                        api_post("admin", {
                            "username": new_user,
                            "password": hash_password(new_pw)
                        })
                    st.success("✅ Akun berhasil dibuat! Silakan masuk.")
                else:
                    st.warning("⚠️ Username dan Password tidak boleh kosong")

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align:center; margin-top:24px; color:#334155; font-size:12px;">
            © 2024 KAS KITA · Sistem Keuangan Digital
        </div>
        """, unsafe_allow_html=True)

# ================= MAIN APP =================
else:
    # ===== SIDEBAR =====
    with st.sidebar:
        # Logo
        st.markdown(f"""
        <div class="sidebar-logo">
            <h2>💰 KAS KITA</h2>
            <div class="tagline">Manajemen Keuangan Digital</div>
        </div>
        """, unsafe_allow_html=True)

        # User badge
        initial = st.session_state.user[0].upper() if st.session_state.user else "U"
        st.markdown(f"""
        <div class="sidebar-user">
            <div class="user-avatar">{initial}</div>
            <div class="user-info">
                <div class="user-label">Logged in as</div>
                <div class="user-name">{st.session_state.user}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation
        st.markdown('<div style="padding: 0 8px;">', unsafe_allow_html=True)

        is_dashboard = st.session_state.menu == "dashboard"
        is_pengeluaran = st.session_state.menu == "pengeluaran"

        cls_dash = "nav-btn-active nav-btn" if is_dashboard else "nav-btn"
        cls_peng = "nav-btn-active nav-btn" if is_pengeluaran else "nav-btn"

        st.markdown(f'<div class="{cls_dash}">', unsafe_allow_html=True)
        if st.button("📊  Dashboard", key="nav_dashboard"):
            st.session_state.menu = "dashboard"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="{cls_peng}">', unsafe_allow_html=True)
        if st.button("💸  Pengeluaran", key="nav_pengeluaran"):
            st.session_state.menu = "pengeluaran"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Spacer
        st.markdown('<div style="flex:1"></div>', unsafe_allow_html=True)
        st.markdown('<div style="padding: 0 8px; margin-top: 24px;">', unsafe_allow_html=True)
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("🚪  Keluar", key="nav_logout"):
            st.session_state.clear()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div style="padding: 20px 24px 16px; color: #334155; font-size: 11px; margin-top: 12px;">
            KAS KITA v2.0 · 2024
        </div>
        """, unsafe_allow_html=True)

    # ===========================
    # ===== DASHBOARD PAGE ======
    # ===========================
    if st.session_state.menu == "dashboard":

        st.markdown("""
        <div class="page-header">
            <h2>📊 Dashboard Kas</h2>
            <p>Pantau dan kelola pemasukan kas sekolah</p>
        </div>
        """, unsafe_allow_html=True)

        df = api_get("kas")

        if not df.empty:
            if "tanggal" in df.columns:
                df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
                df["bulan"] = df["tanggal"].dt.strftime("%B %Y")

            df["nominal"] = pd.to_numeric(df["nominal"], errors="coerce").fillna(0)

            # Filter bulan
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="glass-card-title">🔍 Filter Data</div>', unsafe_allow_html=True)
            bulan_list = ["Semua"]
            if "bulan" in df.columns:
                bulan_list += sorted(df["bulan"].dropna().unique().tolist())
            bulan = st.selectbox("Periode", bulan_list, label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)

            df_filtered = df.copy()
            if bulan != "Semua":
                df_filtered = df[df["bulan"] == bulan]

            total_kas = df_filtered["nominal"].sum()
            jumlah_transaksi = len(df_filtered)
            rata2 = total_kas / jumlah_transaksi if jumlah_transaksi > 0 else 0

            # Stats cards
            col1, col2, col3 = st.columns(3)
            with col1:
                metric_card("Total Kas", rupiah(total_kas), "💰", "blue")
            with col2:
                metric_card("Transaksi", str(jumlah_transaksi), "📝", "green", "entri data")
            with col3:
                metric_card("Rata-rata", rupiah_short(rata2), "📈", "gold", "per transaksi")

            st.markdown("<br>", unsafe_allow_html=True)

            # Chart
            if "bulan" in df.columns:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('<div class="glass-card-title">📈 Grafik Pemasukan per Bulan</div>', unsafe_allow_html=True)
                grafik = df.groupby("bulan")["nominal"].sum().reset_index()
                grafik.columns = ["Bulan", "Total Kas"]
                st.bar_chart(grafik.set_index("Bulan"), height=280)
                st.markdown('</div>', unsafe_allow_html=True)

            # Table
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="glass-card-title">📋 Tabel Data Kas</div>', unsafe_allow_html=True)
            st.dataframe(df_filtered, use_container_width=True, hide_index=True)

            col_dl, col_sp = st.columns([1, 3])
            with col_dl:
                st.download_button(
                    "⬇️ Download PDF",
                    generate_pdf(df_filtered),
                    "kas.pdf",
                    mime="application/pdf"
                )
            st.markdown('</div>', unsafe_allow_html=True)

            # Statistik Siswa
            if "nama" in df_filtered.columns:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('<div class="glass-card-title">👤 Statistik per Siswa</div>', unsafe_allow_html=True)

                siswa_list = df_filtered["nama"].dropna().unique().tolist()
                if siswa_list:
                    siswa = st.selectbox("Pilih Siswa", siswa_list)
                    if st.button("🔍 Tampilkan Statistik", key="btn_statistik"):
                        data_siswa = df_filtered[df_filtered["nama"] == siswa]
                        if "status" in df_filtered.columns:
                            hasil = data_siswa["status"].value_counts()
                            st.bar_chart(hasil, height=220)
                st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.markdown("""
            <div class="glass-card" style="text-align:center; padding: 48px;">
                <div style="font-size:48px; margin-bottom:16px;">📭</div>
                <div style="font-size:18px; font-weight:600; color:#94a3b8;">Belum Ada Data Kas</div>
                <div style="color:#64748b; font-size:14px; margin-top:8px;">Tambahkan data pertama Anda di bawah</div>
            </div>
            """, unsafe_allow_html=True)

        # ===== FORM TAMBAH DATA =====
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="glass-card-title">➕ Tambah Data Kas</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            nama = st.text_input("Nama Siswa", placeholder="Contoh: Ahmad Fauzi")
            tanggal = st.date_input("Tanggal Pembayaran")
            status = st.selectbox("Status Pembayaran", ["Tepat Waktu", "Telat"])
            kelas = st.text_input("Kelas", placeholder="Contoh: XII")
        with col2:
            jurusan = st.text_input("Jurusan", placeholder="Contoh: IPA")
            keterangan = st.text_input("Keterangan", placeholder="Contoh: Kas bulan Januari")
            nominal = st.number_input("Nominal (Rp)", min_value=0, step=5000,
                                      placeholder="Masukkan jumlah kas")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Simpan Data Kas", key="btn_simpan_kas"):
            if nama and nominal > 0:
                with st.spinner("Menyimpan data..."):
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
                st.success("✅ Data berhasil disimpan!")
                st.rerun()
            else:
                st.warning("⚠️ Nama dan Nominal wajib diisi")

        st.markdown('</div>', unsafe_allow_html=True)

        # ===== HAPUS DATA =====
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="glass-card-title">🗑️ Hapus Data</div>', unsafe_allow_html=True)
        st.markdown('<div style="color:#f59e0b; font-size:13px; margin-bottom:16px;">⚠️ Tindakan ini tidak dapat dibatalkan. Pastikan ID benar sebelum menghapus.</div>', unsafe_allow_html=True)

        col_id, col_btn = st.columns([2, 1])
        with col_id:
            id_hapus = st.number_input("ID Data yang Ingin Dihapus", step=1, min_value=0)
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ Hapus Data", key="btn_hapus"):
                with st.spinner("Menghapus..."):
                    api_delete("kas", int(id_hapus))
                st.success("✅ Data berhasil dihapus")
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # ==============================
    # ===== PENGELUARAN PAGE =======
    # ==============================
    elif st.session_state.menu == "pengeluaran":

        st.markdown("""
        <div class="page-header">
            <h2>💸 Pengeluaran</h2>
            <p>Kelola dan pantau pengeluaran kas sekolah</p>
        </div>
        """, unsafe_allow_html=True)

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
        with col1:
            metric_card("Total Pemasukan", rupiah(total_masuk), "💰", "blue")
        with col2:
            metric_card("Total Pengeluaran", rupiah(total_keluar), "💸", "red")
        with col3:
            saldo_color = "green" if saldo >= 0 else "red"
            metric_card("Saldo Bersih", rupiah(saldo), "🏦", saldo_color)

        st.markdown("<br>", unsafe_allow_html=True)

        if not df_keluar.empty:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="glass-card-title">📋 Riwayat Pengeluaran</div>', unsafe_allow_html=True)
            st.dataframe(df_keluar, use_container_width=True, hide_index=True)
            col_dl, _ = st.columns([1, 3])
            with col_dl:
                st.download_button(
                    "⬇️ Download PDF",
                    generate_pdf(df_keluar),
                    "pengeluaran.pdf",
                    mime="application/pdf"
                )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="glass-card" style="text-align:center; padding: 40px;">
                <div style="font-size:40px; margin-bottom:12px;">💳</div>
                <div style="font-size:16px; color:#94a3b8; font-weight:600;">Belum Ada Pengeluaran</div>
            </div>
            """, unsafe_allow_html=True)

        # Form pengeluaran
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="glass-card-title">➕ Tambah Pengeluaran</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            tgl = st.date_input("Tanggal Pengeluaran")
            ket = st.text_input("Keterangan Pengeluaran", placeholder="Contoh: Pembelian ATK")
        with col2:
            nom = st.number_input("Nominal Pengeluaran (Rp)", min_value=0, step=5000,
                                   placeholder="Masukkan jumlah")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Simpan Pengeluaran", key="btn_simpan_pengeluaran"):
            if ket and nom > 0:
                with st.spinner("Menyimpan pengeluaran..."):
                    api_post("pengeluaran", {
                        "tanggal": str(tgl),
                        "keterangan": ket,
                        "nominal": int(nom),
                        "owner": st.session_state.user
                    })
                st.success("✅ Pengeluaran berhasil disimpan!")
                st.rerun()
            else:
                st.warning("⚠️ Keterangan dan Nominal wajib diisi")

        st.markdown('</div>', unsafe_allow_html=True)
