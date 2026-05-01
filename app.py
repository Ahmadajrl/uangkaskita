# =============================================================================
# KAS KITA — Aplikasi Manajemen Kas Sekolah
# =============================================================================
# Struktur file:
#   1. Import & Konfigurasi
#   2. CSS Global
#   3. Fungsi Helper (hashing, API, format, validasi, PDF)
#   4. Inisialisasi Session State
#   5. Halaman Auth (Login & Register)
#   6. Halaman Utama
#      6a. Sidebar Navigasi
#      6b. Halaman Dashboard (Data Kas)
#      6c. Halaman Pengeluaran
#   7. Entry Point — Routing
# =============================================================================


# =============================================================================
# 1. IMPORT & KONFIGURASI
# =============================================================================

import hashlib
import io

import pandas as pd
import requests
import streamlit as st
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

# Harus dipanggil sebelum elemen Streamlit lainnya
st.set_page_config(
    page_title="KAS KITA",
    page_icon="icon.png",
    layout="wide",
)

# Endpoint Google Apps Script sebagai backend API
API_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbxBe2m5pZoJOofUKqvf7oRrAt_UARgQ3W3pVwUYFMQVwJgMsLb3pb-7jg1rOJRgm8xz/exec"
)


# =============================================================================
# 2. CSS GLOBAL
# =============================================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Variabel Tema ─────────────────────────────────────────────────────── */
:root {
    --bg-primary:    #080e1d;
    --bg-card:       rgba(255,255,255,0.04);
    --bg-card-hover: rgba(255,255,255,0.07);
    --border:        rgba(255,255,255,0.08);
    --accent:        #3b82f6;
    --accent-glow:   rgba(59,130,246,0.25);
    --green:         #10b981;
    --red:           #f43f5e;
    --gold:          #f59e0b;
    --text-primary:  #f1f5f9;
    --text-muted:    #64748b;
    --radius:        16px;
    --radius-sm:     10px;
}

/* ── Global ────────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}
.stApp {
    background: linear-gradient(135deg, #080e1d 0%, #0f1f3d 50%, #080e1d 100%) !important;
    min-height: 100vh;
}
/* Grid background dekoratif */
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

/* ── Heading ───────────────────────────────────────────────────────────── */
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    letter-spacing: -0.5px;
}

/* ── Sidebar ───────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1932 0%, #080e1d 100%) !important;
    border-right: 1px solid var(--border) !important;
    padding-top: 0 !important;
}
section[data-testid="stSidebar"] > div { padding: 0 !important; }

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
    width: 36px; height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, #3b82f6, #06b6d4);
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; font-weight: 700;
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

/* ── Navigasi Sidebar ──────────────────────────────────────────────────── */
/* Override global button style khusus untuk tombol navigasi di sidebar */
.nav-btn > div[data-testid="stButton"] > button,
.nav-btn div[data-testid="stButton"] > button {
    background: transparent !important;
    background-image: none !important;
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
    width: 100% !important;
}
.nav-btn > div[data-testid="stButton"] > button:hover,
.nav-btn div[data-testid="stButton"] > button:hover {
    background: rgba(59,130,246,0.1) !important;
    color: var(--accent) !important;
    transform: none !important;
    box-shadow: none !important;
    filter: none !important;
}
.nav-btn-active > div[data-testid="stButton"] > button,
.nav-btn-active div[data-testid="stButton"] > button {
    background: rgba(59,130,246,0.15) !important;
    background-image: none !important;
    border: none !important;
    box-shadow: none !important;
    color: var(--accent) !important;
    font-weight: 600 !important;
}

/* Override global button style khusus untuk tombol logout */
.logout-btn > div[data-testid="stButton"] > button,
.logout-btn div[data-testid="stButton"] > button {
    background: rgba(244,63,94,0.08) !important;
    background-image: none !important;
    border: 1px solid rgba(244,63,94,0.2) !important;
    color: #f43f5e !important;
    box-shadow: none !important;
    font-size: 14px !important;
    border-radius: var(--radius-sm) !important;
    padding: 12px 16px !important;
    transition: all 0.2s !important;
    width: 100% !important;
}
.logout-btn > div[data-testid="stButton"] > button:hover,
.logout-btn div[data-testid="stButton"] > button:hover {
    background: rgba(244,63,94,0.15) !important;
    transform: none !important;
    box-shadow: none !important;
    filter: none !important;
}

/* ── Metric Cards ──────────────────────────────────────────────────────── */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px 20px;
    position: relative; overflow: hidden;
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
    position: absolute; top: 0; left: 0; right: 0;
    height: 2px;
    border-radius: var(--radius) var(--radius) 0 0;
}
.metric-card.blue::before  { background: linear-gradient(90deg, #3b82f6, #06b6d4); }
.metric-card.green::before { background: linear-gradient(90deg, #10b981, #34d399); }
.metric-card.red::before   { background: linear-gradient(90deg, #f43f5e, #fb7185); }
.metric-card.gold::before  { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.metric-label {
    font-size: 11px; font-weight: 600; letter-spacing: 1.5px;
    text-transform: uppercase; color: var(--text-muted); margin-bottom: 10px;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 26px; font-weight: 800;
    color: var(--text-primary); line-height: 1.1;
}
.metric-icon {
    position: absolute; top: 20px; right: 20px;
    font-size: 24px; opacity: 0.25;
}

/* ── Glass Card ────────────────────────────────────────────────────────── */
.glass-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 28px; backdrop-filter: blur(12px); margin-bottom: 20px;
}
.glass-card-title {
    font-family: 'Syne', sans-serif;
    font-size: 15px; font-weight: 700;
    color: var(--text-primary); margin-bottom: 18px;
    display: flex; align-items: center; gap: 8px;
}

/* ── Halaman Auth ──────────────────────────────────────────────────────── */
.auth-wrapper { max-width: 440px; margin: 40px auto; }
.auth-logo { text-align: center; margin-bottom: 36px; }
.auth-logo h1 {
    font-family: 'Syne', sans-serif !important;
    font-size: 42px !important; font-weight: 800 !important;
    background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text; margin: 0 !important;
}
.auth-logo p { color: var(--text-muted); font-size: 14px; margin-top: 4px; }

/* ── Page Header ───────────────────────────────────────────────────────── */
.page-header {
    margin-bottom: 28px; padding-bottom: 20px;
    border-bottom: 1px solid var(--border);
}
.page-header h2 {
    font-family: 'Syne', sans-serif !important;
    font-size: 28px !important; font-weight: 800 !important;
    color: var(--text-primary) !important; margin: 0 0 4px !important;
}
.page-header p { color: var(--text-muted); font-size: 14px; margin: 0; }

/* ── Form Inputs ───────────────────────────────────────────────────────── */
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
    font-size: 12px !important; font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    color: var(--text-muted) !important; text-transform: uppercase !important;
}

/* ── Tombol Utama ──────────────────────────────────────────────────────── */
div[data-testid="stButton"] > button[kind="primary"],
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    color: white !important; border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 14px !important;
    padding: 12px 24px !important; width: 100% !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 20px rgba(59,130,246,0.3) !important;
    letter-spacing: 0.3px !important;
}
div[data-testid="stButton"] > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 30px rgba(59,130,246,0.45) !important;
    filter: brightness(1.08) !important;
}
div[data-testid="stButton"] > button:active { transform: translateY(0) !important; }

/* ── Tombol Download ───────────────────────────────────────────────────── */
div[data-testid="stDownloadButton"] > button {
    background: rgba(255,255,255,0.05) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important; width: 100% !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    background: rgba(59,130,246,0.08) !important;
}

/* ── Tabs ──────────────────────────────────────────────────────────────── */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03) !important;
    border-radius: var(--radius-sm) !important;
    border: 1px solid var(--border) !important;
    padding: 4px !important; gap: 4px !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"] {
    border-radius: 8px !important; color: var(--text-muted) !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 500 !important;
}
div[data-testid="stTabs"] [aria-selected="true"] {
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
    color: white !important;
}

/* ── Tabel & Chart ─────────────────────────────────────────────────────── */
div[data-testid="stDataFrame"] {
    border-radius: var(--radius-sm) !important;
    overflow: hidden !important; border: 1px solid var(--border) !important;
}
div[data-testid="stDataFrame"] table { background: var(--bg-card) !important; }
div[data-testid="stArrowVegaLiteChart"] {
    border-radius: var(--radius-sm) !important; overflow: hidden !important;
}

/* ── Komponen Lain ─────────────────────────────────────────────────────── */
div[data-testid="stAlert"] { border-radius: var(--radius-sm) !important; border: none !important; }
div[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important; padding: 20px !important;
}
div[data-testid="stTextInput"] [data-testid="InputInstructions"] { display: none; }
#MainMenu, footer, header { display: none !important; }

/* ── Scrollbar ─────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

/* ── Responsive ────────────────────────────────────────────────────────── */
@media (max-width: 768px) {
    .metric-value { font-size: 20px; }
    .glass-card { padding: 20px 16px; }
}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# 3. FUNGSI HELPER
# =============================================================================

def hash_password(password: str) -> str:
    """Mengembalikan hash SHA-256 dari password yang diberikan."""
    return hashlib.sha256(password.encode()).hexdigest()


def rupiah(nominal) -> str:
    """Memformat angka menjadi string mata uang Rupiah. Contoh: Rp 10.000"""
    return f"Rp {int(nominal):,}".replace(",", ".")


# ── Fungsi API ───────────────────────────────────────────────────────────────

def api_get(table: str) -> pd.DataFrame:
    """
    Mengambil data dari tabel tertentu melalui API.
    Data otomatis difilter berdasarkan 'owner' (user yang sedang login).
    Mengembalikan DataFrame kosong jika terjadi error.
    """
    try:
        res = requests.get(API_URL, params={"action": "get", "table": table})
        res.raise_for_status()
        df = pd.DataFrame(res.json())

        # Filter data hanya milik user yang sedang login
        if not df.empty and "owner" in df.columns:
            df["owner"] = df["owner"].astype(str)
            df = df[df["owner"] == st.session_state.user]

        return df
    except Exception as e:
        st.error(f"Gagal mengambil data dari '{table}': {e}")
        return pd.DataFrame()


def api_post(table: str, data: dict) -> None:
    """Mengirim (insert) data baru ke tabel tertentu melalui API."""
    try:
        requests.post(API_URL, json={"action": "insert", "table": table, "data": data})
    except Exception as e:
        st.error(f"Gagal menyimpan data ke '{table}': {e}")


def api_delete(table: str, row_id: int) -> None:
    """Menghapus satu baris data berdasarkan ID dari tabel tertentu."""
    try:
        requests.post(API_URL, json={"action": "delete", "table": table, "id": row_id})
    except Exception as e:
        st.error(f"Gagal menghapus data dari '{table}': {e}")


# ── Fungsi Validasi ──────────────────────────────────────────────────────────

def validasi_kas(nama: str, kelas: str, jurusan: str, nominal: float) -> str | None:
    """
    Memvalidasi input form data kas.
    Mengembalikan string pesan error jika tidak valid, atau None jika valid.
    """
    if not nama.strip():
        return "Nama tidak boleh kosong"
    if len(nama.strip()) < 3:
        return "Nama terlalu pendek (minimal 3 karakter)"
    if not kelas.strip():
        return "Kelas tidak boleh kosong"
    if not jurusan.strip():
        return "Jurusan tidak boleh kosong"
    if nominal <= 0:
        return "Nominal harus lebih dari 0"
    if nominal > 1_000_000:
        return "Nominal terlalu besar (maksimal Rp 1.000.000)"
    return None


def validasi_pengeluaran(keterangan: str, nominal: float) -> str | None:
    """
    Memvalidasi input form pengeluaran.
    Mengembalikan string pesan error jika tidak valid, atau None jika valid.
    """
    if not keterangan.strip():
        return "Keterangan wajib diisi"
    if nominal <= 0:
        return "Nominal harus lebih dari 0"
    return None


# ── Fungsi PDF ───────────────────────────────────────────────────────────────

def generate_pdf(df: pd.DataFrame) -> io.BytesIO:
    """
    Membuat file PDF dari DataFrame.
    Mengembalikan buffer BytesIO yang siap diunduh oleh pengguna.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)

    df_copy = df.copy()

    # Konversi nominal ke integer agar tampil rapi di PDF
    if "nominal" in df_copy.columns:
        df_copy["nominal"] = (
            pd.to_numeric(df_copy["nominal"], errors="coerce")
            .fillna(0)
            .astype(int)
        )

    data = [df_copy.columns.tolist()] + df_copy.values.tolist()

    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0),  colors.grey),
        ("TEXTCOLOR",      (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",       (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("GRID",           (0, 0), (-1, -1), 1, colors.black),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))

    doc.build([table])
    buffer.seek(0)
    return buffer


# =============================================================================
# 4. INISIALISASI SESSION STATE
# =============================================================================

# Inisialisasi semua state dalam satu blok agar tidak berulang
_session_defaults = {
    "login": False,
    "user":  "",
    "menu":  "dashboard",
}
for _key, _val in _session_defaults.items():
    if _key not in st.session_state:
        st.session_state[_key] = _val


# =============================================================================
# 5. HALAMAN AUTH (BELUM LOGIN)
# =============================================================================

def render_auth():
    """Menampilkan halaman login dan registrasi."""
    st.markdown("""
        <div class="auth-wrapper">
            <div class="auth-logo">
                <h1>KAS KITA</h1>
                <p>Sistem Manajemen Kas Sekolah</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["🔑 Login", "📝 Daftar Akun"])

    # ── Tab Login ────────────────────────────────────────────────────────────
    with tab_login:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pw")

        if st.button("Masuk", key="btn_login"):
            if not username or not password:
                st.warning("Username dan password wajib diisi.")
                return

            try:
                res = requests.get(API_URL, params={"action": "get", "table": "admin"})
                res.raise_for_status()
                df_admin = pd.DataFrame(res.json())
            except Exception:
                st.error("Gagal terhubung ke server. Coba lagi.")
                return

            if df_admin.empty:
                st.error("Tidak ada data akun di server.")
                return

            df_admin["username"] = df_admin["username"].astype(str)
            df_admin["password"] = df_admin["password"].astype(str)

            cocok = df_admin[
                (df_admin["username"] == username) &
                (df_admin["password"] == hash_password(password))
            ]

            if not cocok.empty:
                st.session_state.login = True
                st.session_state.user  = username
                st.rerun()
            else:
                st.error("Username atau password salah.")

    # ── Tab Registrasi ───────────────────────────────────────────────────────
    with tab_register:
        new_user = st.text_input("Username Baru", key="reg_user")
        new_pw   = st.text_input("Password Baru", type="password", key="reg_pw")

        if st.button("Daftar", key="btn_register"):
            if not new_user or not new_pw:
                st.warning("Username dan password wajib diisi.")
            elif len(new_pw) < 6:
                st.warning("Password minimal 6 karakter.")
            else:
                api_post("admin", {
                    "username": new_user.strip(),
                    "password": hash_password(new_pw),
                })
                st.success("✅ Akun berhasil dibuat. Silakan login.")


# =============================================================================
# 6. HALAMAN UTAMA (SUDAH LOGIN)
# =============================================================================

# ── 6a. Sidebar Navigasi ─────────────────────────────────────────────────────

def render_sidebar():
    """Menampilkan sidebar berisi logo, info user, menu navigasi, dan tombol logout."""
    with st.sidebar:
        # Logo aplikasi
        st.markdown("""
            <div class="sidebar-logo">
                <h2>💰 KAS KITA</h2>
                <div class="tagline">Manajemen Kas Sekolah</div>
            </div>
        """, unsafe_allow_html=True)

        # Avatar dan info user yang sedang login
        inisial = st.session_state.user[0].upper() if st.session_state.user else "?"
        st.markdown(f"""
            <div class="sidebar-user">
                <div class="user-avatar">{inisial}</div>
                <div class="user-info">
                    <div class="user-label">Logged in as</div>
                    <div class="user-name">{st.session_state.user}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Menu navigasi dengan highlight aktif
        menu_items = {
            "dashboard":   "📊  Dashboard",
            "pengeluaran": "💸  Pengeluaran",
        }
        for key, label in menu_items.items():
            css_class = "nav-btn-active" if st.session_state.menu == key else "nav-btn"
            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            if st.button(label, key=f"nav_{key}"):
                st.session_state.menu = key
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")

        # Tombol logout
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("🚪  Logout", key="btn_logout"):
            st.session_state.clear()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ── 6b. Halaman Dashboard ────────────────────────────────────────────────────

def render_dashboard():
    """Menampilkan dashboard: ringkasan kas, grafik, tabel, form tambah & hapus."""
    st.markdown("""
        <div class="page-header">
            <h2>📊 Dashboard Kas</h2>
            <p>Kelola dan pantau pemasukan kas</p>
        </div>
    """, unsafe_allow_html=True)

    df = api_get("kas")

    # ── Tampilkan data jika tersedia ─────────────────────────────────────────
    if not df.empty:
        # Normalisasi tipe data
        if "tanggal" in df.columns:
            df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
            df["bulan"]   = df["tanggal"].dt.strftime("%B %Y")
        df["nominal"] = pd.to_numeric(df["nominal"], errors="coerce").fillna(0)

        # Filter berdasarkan bulan
        bulan_list = ["Semua"]
        if "bulan" in df.columns:
            bulan_list += sorted(df["bulan"].dropna().unique().tolist())

        bulan_pilih = st.selectbox("🗓️ Filter Bulan", bulan_list)
        if bulan_pilih != "Semua":
            df = df[df["bulan"] == bulan_pilih]

        # Metrik total kas
        st.metric("💰 Total Kas", rupiah(df["nominal"].sum()))

        # Grafik per bulan (hanya saat tidak difilter per bulan)
        if "bulan" in df.columns and bulan_pilih == "Semua":
            st.subheader("📈 Grafik Kas per Bulan")
            st.bar_chart(df.groupby("bulan")["nominal"].sum())

        # Tabel data kas
        st.subheader("📋 Data Kas")
        st.dataframe(df, use_container_width=True)

        # Unduh PDF
        st.download_button(
            label="⬇️ Download PDF",
            data=generate_pdf(df),
            file_name="kas.pdf",
            mime="application/pdf",
        )

        # Statistik per siswa
        if "nama" in df.columns:
            st.subheader("👤 Statistik Siswa")
            siswa_list = df["nama"].dropna().unique().tolist()
            if siswa_list:
                siswa_pilih = st.selectbox("Pilih Siswa", siswa_list)
                if st.button("🔍 Lihat Statistik"):
                    data_siswa = df[df["nama"] == siswa_pilih]
                    if "status" in data_siswa.columns:
                        st.bar_chart(data_siswa["status"].value_counts())
                    else:
                        st.info("Kolom 'status' tidak tersedia pada data.")
    else:
        st.warning("⚠️ Belum ada data kas.")

    st.divider()

    # ── Form Tambah Data Kas ─────────────────────────────────────────────────
    st.subheader("➕ Tambah Data Kas")

    with st.form("form_tambah_kas"):
        col_a, col_b = st.columns(2)
        with col_a:
            nama      = st.text_input("Nama Lengkap")
            kelas     = st.text_input("Kelas")
            jurusan   = st.text_input("Jurusan")
        with col_b:
            tanggal   = st.date_input("Tanggal Pembayaran")
            status    = st.selectbox("Status", ["Tepat Waktu", "Telat"])
            nominal   = st.number_input("Nominal (Rp)", min_value=0, step=1_000)

        keterangan = st.text_input("Keterangan (contoh: Lunas)")
        submit_kas = st.form_submit_button("💾 Simpan Data")

    if submit_kas:
        error = validasi_kas(nama, kelas, jurusan, nominal)
        if error:
            st.error(f"❌ {error}")
        else:
            api_post("kas", {
                "nama":       nama.strip(),
                "tanggal":    str(tanggal),
                "status":     status,
                "kelas":      kelas.strip(),
                "jurusan":    jurusan.strip(),
                "keterangan": keterangan.strip(),
                "nominal":    int(nominal),
                "owner":      st.session_state.user,
            })
            st.success("✅ Data berhasil disimpan.")
            st.rerun()

    st.divider()

    # ── Form Hapus Data Kas ──────────────────────────────────────────────────
    st.subheader("🗑️ Hapus Data Kas")

    with st.form("form_hapus_kas"):
        id_hapus     = st.number_input("Masukkan ID Data", min_value=1, step=1)
        submit_hapus = st.form_submit_button("Hapus Data")

    if submit_hapus:
        api_delete("kas", int(id_hapus))
        st.success(f"✅ Data dengan ID {id_hapus} berhasil dihapus.")
        st.rerun()


# ── 6c. Halaman Pengeluaran ──────────────────────────────────────────────────

def render_pengeluaran():
    """Menampilkan halaman pengeluaran: ringkasan saldo, riwayat, dan form tambah."""
    st.markdown("""
        <div class="page-header">
            <h2>💸 Pengeluaran</h2>
            <p>Catat dan pantau pengeluaran kas</p>
        </div>
    """, unsafe_allow_html=True)

    # Ambil data dari kedua tabel secara bersamaan
    df_keluar = api_get("pengeluaran")
    df_masuk  = api_get("kas")

    # Normalisasi kolom nominal
    if not df_keluar.empty:
        df_keluar["nominal"] = pd.to_numeric(df_keluar["nominal"], errors="coerce").fillna(0)
    if not df_masuk.empty:
        df_masuk["nominal"] = pd.to_numeric(df_masuk["nominal"], errors="coerce").fillna(0)

    # Hitung ringkasan keuangan
    total_masuk  = df_masuk["nominal"].sum()  if not df_masuk.empty  else 0
    total_keluar = df_keluar["nominal"].sum() if not df_keluar.empty else 0
    saldo        = total_masuk - total_keluar

    # Tampilkan ringkasan dalam 3 kolom
    col1, col2, col3 = st.columns(3)
    col1.metric("📥 Total Pemasukan",    rupiah(total_masuk))
    col2.metric("📤 Total Pengeluaran",  rupiah(total_keluar))
    col3.metric("💳 Saldo Saat Ini",     rupiah(saldo))

    # Riwayat pengeluaran
    if not df_keluar.empty:
        st.subheader("📋 Riwayat Pengeluaran")
        st.dataframe(df_keluar, use_container_width=True)
        st.download_button(
            label="⬇️ Download PDF",
            data=generate_pdf(df_keluar),
            file_name="pengeluaran.pdf",
            mime="application/pdf",
        )
    else:
        st.info("Belum ada data pengeluaran.")

    st.divider()

    # ── Form Tambah Pengeluaran ──────────────────────────────────────────────
    st.subheader("➕ Tambah Pengeluaran")

    with st.form("form_tambah_pengeluaran"):
        tgl_keluar    = st.date_input("Tanggal")
        ket_keluar    = st.text_input("Keterangan")
        nom_keluar    = st.number_input("Nominal (Rp)", min_value=0, step=1_000)
        submit_keluar = st.form_submit_button("💾 Simpan Pengeluaran")

    if submit_keluar:
        error = validasi_pengeluaran(ket_keluar, nom_keluar)
        if error:
            st.warning(f"⚠️ {error}")
        else:
            api_post("pengeluaran", {
                "tanggal":    str(tgl_keluar),
                "keterangan": ket_keluar.strip(),
                "nominal":    int(nom_keluar),
                "owner":      st.session_state.user,
            })
            st.success("✅ Pengeluaran berhasil disimpan.")
            st.rerun()


# =============================================================================
# 7. ENTRY POINT — Routing Halaman
# =============================================================================

if not st.session_state.login:
    # Tampilkan halaman autentikasi jika belum login
    render_auth()
else:
    # Render sidebar navigasi
    render_sidebar()

    # Routing ke halaman yang dipilih
    if st.session_state.menu == "dashboard":
        render_dashboard()
    elif st.session_state.menu == "pengeluaran":
        render_pengeluaran()
