import streamlit as st
import pandas as pd
import sqlite3
import io
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# ======================
# PAGE CONFIG
# ======================
st.set_page_config(
    page_title="KasKita",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================
# CUSTOM CSS — Navy #2D303E + Green #09F289
# ======================
st.markdown("""
<style>
/* ── Global ── */
[data-testid="stAppViewContainer"] {
    background: #F3FDF9;
}
[data-testid="stSidebar"] {
    background: #2D303E !important;
    border-right: none;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0.75rem;
}

/* ── Hide chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Hamburger Menu Toggle ── */
.hamburger-toggle {
    position: fixed;
    top: 15px;
    left: 15px;
    z-index: 999999;
    cursor: pointer;
    width: 40px;
    height: 40px;
    background: #2D303E;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid rgba(9,242,137,0.3);
    transition: all 0.3s ease;
}
.hamburger-toggle:hover {
    background: #3D4050;
    border-color: #09F289;
}
.hamburger-toggle svg {
    width: 22px;
    height: 22px;
}
.hamburger-toggle .line {
    fill: none;
    stroke: #09F289;
    stroke-width: 2.5;
    stroke-linecap: round;
    transition: all 0.3s ease;
}
.hamburger-toggle:hover .line {
    stroke: #09F289;
}

/* Sidebar collapsed state */
[data-testid="stSidebar"][aria-expanded="false"] {
    transform: translateX(-100%);
    transition: transform 0.3s ease;
}
[data-testid="stSidebar"][aria-expanded="true"] {
    transform: translateX(0);
    transition: transform 0.3s ease;
}

/* Adjust main content when sidebar is collapsed */
section.main > div {
    padding-left: 1rem !important;
}

/* Hide default collapse button */
button[kind="header"] {
    display: none !important;
}

/* ── Sidebar text overrides ── */
section[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.65) !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #FFFFFF !important;
}
section[data-testid="stSidebar"] label {
    color: rgba(255,255,255,0.45) !important;
    font-size: 11px !important;
}
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(9,242,137,0.08) !important;
    border-color: rgba(9,242,137,0.2) !important;
    color: #FFFFFF !important;
}
section[data-testid="stSidebar"] input {
    background: rgba(9,242,137,0.08) !important;
    border-color: rgba(9,242,137,0.2) !important;
    color: #FFFFFF !important;
}

/* ── Sidebar buttons ── */
section[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    text-align: left;
    border: none !important;
    background: transparent !important;
    color: rgba(255,255,255,0.55) !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    font-size: 13px !important;
    margin-bottom: 2px;
    transition: all 0.15s;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(9,242,137,0.1) !important;
    color: rgba(255,255,255,0.9) !important;
}

/* ── Main area buttons ── */
div:not(section[data-testid="stSidebar"]) .stButton > button {
    border-radius: 8px !important;
    border: 1px solid #D1FAE5 !important;
    background: #FFFFFF !important;
    color: #2D303E !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    padding: 6px 14px !important;
    transition: all 0.15s;
}
div:not(section[data-testid="stSidebar"]) .stButton > button:hover {
    background: #E6FDF5 !important;
    border-color: #09F289 !important;
}
div:not(section[data-testid="stSidebar"]) .stButton > button[kind="primary"] {
    background: #09F289 !important;
    color: #2D303E !important;
    border: none !important;
    font-weight: 500 !important;
}
div:not(section[data-testid="stSidebar"]) .stButton > button[kind="primary"]:hover {
    background: #07C46E !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #D1FAE5;
    border-radius: 12px;
    padding: 1rem 1.25rem !important;
}
[data-testid="stMetric"] label {
    font-size: 11px !important;
    color: #6B7280 !important;
    font-weight: 400 !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
[data-testid="stMetricValue"] {
    font-size: 22px !important;
    font-weight: 500 !important;
    color: #2D303E !important;
}

/* ── Inputs & selects (main area) ── */
div:not(section[data-testid="stSidebar"]) .stTextInput > div > div > input,
div:not(section[data-testid="stSidebar"]) .stDateInput > div > div > input,
div:not(section[data-testid="stSidebar"]) .stNumberInput > div > div > input,
div:not(section[data-testid="stSidebar"]) .stSelectbox > div > div {
    border-radius: 8px !important;
    border: 1px solid #D1FAE5 !important;
    background: #FAFFFE !important;
    font-size: 13px !important;
    color: #2D303E !important;
}
div:not(section[data-testid="stSidebar"]) .stTextInput > div > div > input:focus {
    border-color: #09F289 !important;
    box-shadow: 0 0 0 2px rgba(9,242,137,0.2) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid #D1FAE5;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    font-size: 13px;
    color: #6B7280;
    border-bottom: 2px solid transparent;
    background: transparent;
    padding: 8px 16px;
}
.stTabs [aria-selected="true"] {
    color: #2D303E !important;
    border-bottom: 2px solid #09F289 !important;
    background: transparent !important;
    font-weight: 500;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #FFFFFF !important;
    border: 1px solid #D1FAE5 !important;
    border-radius: 10px !important;
    font-size: 13px !important;
    color: #2D303E !important;
    font-weight: 400 !important;
}
.streamlit-expanderContent {
    border: 1px solid #D1FAE5 !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
    background: #FAFFFE !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid #D1FAE5 !important;
    border-radius: 10px !important;
    overflow: hidden;
}
[data-testid="stDataFrame"] th {
    background: #F3FDF9 !important;
    color: #6B7280 !important;
    font-size: 11px !important;
}

/* ── Alerts ── */
.stSuccess {
    background: rgba(9,242,137,0.08) !important;
    border: 1px solid rgba(9,242,137,0.3) !important;
    border-radius: 10px !important;
    color: #065F46 !important;
    font-size: 13px !important;
}
.stWarning {
    border-radius: 10px !important;
    font-size: 13px !important;
}
.stError {
    border-radius: 10px !important;
    font-size: 13px !important;
}
.stInfo {
    background: #E6FDF5 !important;
    border: 1px solid #D1FAE5 !important;
    border-radius: 10px !important;
    color: #2D303E !important;
    font-size: 13px !important;
}

/* ── Checkbox ── */
.stCheckbox > label {
    font-size: 13px !important;
    color: #2D303E !important;
}

/* ── Radio (sidebar) ── */
.stRadio > label {
    color: rgba(255,255,255,0.55) !important;
    font-size: 13px !important;
}
.stRadio [data-testid="stMarkdownContainer"] p {
    color: rgba(255,255,255,0.7) !important;
}

/* ── Bar chart ── */
[data-testid="stVegaLiteChart"] {
    border: 1px solid #D1FAE5 !important;
    border-radius: 10px !important;
    background: #FFFFFF !important;
    padding: 0.5rem !important;
}

/* ── Download button ── */
.stDownloadButton > button {
    border-radius: 8px !important;
    border: 1px solid #D1FAE5 !important;
    background: #FFFFFF !important;
    color: #2D303E !important;
    font-size: 13px !important;
}
.stDownloadButton > button:hover {
    background: #E6FDF5 !important;
    border-color: #09F289 !important;
}

/* ── Divider ── */
hr { border-color: #D1FAE5 !important; }
</style>
""", unsafe_allow_html=True)

# ======================
# HAMBURGER MENU SCRIPT
# ======================
st.markdown("""
<script>
(function() {
    function createHamburger() {
        // Check if already exists
        if (document.getElementById('custom-hamburger')) return;
        
        const hamburger = document.createElement('div');
        hamburger.id = 'custom-hamburger';
        hamburger.className = 'hamburger-toggle';
        hamburger.innerHTML = `
            <svg viewBox="0 0 24 24">
                <line class="line" x1="3" y1="6" x2="21" y2="6" />
                <line class="line" x1="3" y1="12" x2="21" y2="12" />
                <line class="line" x1="3" y1="18" x2="21" y2="18" />
            </svg>
        `;
        
        hamburger.addEventListener('click', function() {
            const sidebar = document.querySelector('[data-testid="stSidebar"]');
            const closeButton = sidebar?.querySelector('button[kind="header"]');
            
            if (closeButton) {
                closeButton.click();
            }
            
            // Update hamburger position based on sidebar state
            setTimeout(() => {
                const isExpanded = sidebar?.getAttribute('aria-expanded') === 'true';
                hamburger.style.left = isExpanded ? '15px' : '15px';
            }, 100);
        });
        
        document.body.appendChild(hamburger);
        
        // Initial position
        setTimeout(() => {
            const sidebar = document.querySelector('[data-testid="stSidebar"]');
            const isExpanded = sidebar?.getAttribute('aria-expanded') === 'true';
            hamburger.style.left = '15px';
        }, 100);
    }
    
    // Create hamburger after page loads
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createHamburger);
    } else {
        createHamburger();
    }
    
    // Re-create on navigation
    let lastUrl = location.href;
    new MutationObserver(() => {
        const url = location.href;
        if (url !== lastUrl) {
            lastUrl = url;
            setTimeout(createHamburger, 500);
        }
    }).observe(document, {subtree: true, childList: true});
})();
</script>
""", unsafe_allow_html=True)

DEV_USER = "developer"
DEV_PASS = "kaskita"

# ======================
# HELPERS
# ======================
def format_rupiah(angka):
    return "Rp {:,.0f}".format(angka).replace(",", ".")

def clean_nominal(n):
    if not n:
        return 0
    n = str(n).lower().replace("rp", "").replace(".", "").replace(",", "").strip()
    return int(n) if n.isdigit() else 0

# ======================
# PDF
# ======================
def generate_pdf(df, title="Laporan KasKita"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"<b>{title}</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    data = [df.columns.tolist()] + df.values.tolist()
    t = Table(data, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor("#2D303E")),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.HexColor("#09F289")),
        ("FONTSIZE",      (0, 0), (-1, 0),  10),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, colors.HexColor("#F3FDF9")]),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#D1FAE5")),
        ("FONTSIZE",      (0, 1), (-1, -1), 9),
        ("PADDING",       (0, 0), (-1, -1), 6),
        ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
        ("TEXTCOLOR",     (0, 1), (-1, -1), colors.HexColor("#2D303E")),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 16))
    elements.append(Paragraph("© KasKita 2026", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ======================
# DB
# ======================
@st.cache_resource
def init_db():
    conn = sqlite3.connect("kas.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS kas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT, tanggal TEXT, status TEXT,
        kelas TEXT, jurusan TEXT, keterangan TEXT, nominal INTEGER
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, password TEXT, email TEXT, kelas TEXT, jurusan TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS pengeluaran (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tanggal TEXT, kelas TEXT, jurusan TEXT, keterangan TEXT, nominal INTEGER
    )''')
    conn.commit()
    return conn, cursor

conn, cursor = init_db()

# ======================
# SESSION STATE
# ======================
defaults = {
    "login": False, "role": None,
    "kelas": None,  "jurusan": None,
    "page": "role", "menu": "dashboard"
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ======================
# KOMPONEN UI
# ======================
def render_logo_sidebar():
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:0.5rem 0.25rem 1rem;">
        <div style="width:34px;height:34px;background:#09F289;border-radius:9px;
                    display:flex;align-items:center;justify-content:center;flex-shrink:0;">
            <svg width="19" height="19" viewBox="0 0 22 22" fill="none">
                <rect x="2" y="6" width="18" height="11" rx="2.5" stroke="#2D303E" stroke-width="1.7"/>
                <path d="M2 9.5h18" stroke="#2D303E" stroke-width="1.7"/>
                <rect x="4.5" y="12" width="6" height="2" rx="0.6" fill="#2D303E"/>
            </svg>
        </div>
        <div>
            <div style="font-size:15px;font-weight:600;color:#FFFFFF;line-height:1.1;">KasKita</div>
            <div style="font-size:10px;color:rgba(9,242,137,0.6);">Manajemen kas kelas</div>
        </div>
    </div>
    <div style="height:1px;background:rgba(9,242,137,0.12);margin-bottom:0.75rem;"></div>
    """, unsafe_allow_html=True)

def render_class_chip(kls, jrs):
    st.markdown(f"""
    <div style="background:rgba(9,242,137,0.1);border:1px solid rgba(9,242,137,0.22);
                border-radius:8px;padding:8px 10px;margin-bottom:1rem;">
        <div style="font-size:10px;color:#09F289;font-weight:500;letter-spacing:.04em;">SESI AKTIF</div>
        <div style="font-size:12px;color:rgba(255,255,255,0.75);margin-top:2px;">
            Kelas {kls} &nbsp;·&nbsp; {jrs}
        </div>
    </div>
    """, unsafe_allow_html=True)

def sidebar_label(text):
    st.markdown(f"""
    <div style="font-size:10px;color:rgba(255,255,255,0.28);text-transform:uppercase;
                letter-spacing:.06em;padding:8px 4px 4px;font-weight:500;">{text}</div>
    """, unsafe_allow_html=True)

def sidebar_sep():
    st.markdown(
        '<div style="height:1px;background:rgba(255,255,255,0.07);margin:6px 0;"></div>',
        unsafe_allow_html=True
    )

def sidebar_user(label):
    initial = label[0].upper() if label else "U"
    st.markdown(f"""
    <div style="background:rgba(9,242,137,0.07);border-radius:8px;
                padding:8px 10px;display:flex;align-items:center;gap:8px;">
        <div style="width:26px;height:26px;border-radius:50%;background:rgba(9,242,137,0.18);
                    display:flex;align-items:center;justify-content:center;
                    font-size:10px;color:#09F289;font-weight:500;flex-shrink:0;">{initial}</div>
        <div style="font-size:11px;color:rgba(255,255,255,0.6);">{label}</div>
    </div>
    """, unsafe_allow_html=True)

def info_badge_sidebar(text, color="#09F289", bg="rgba(9,242,137,0.12)"):
    st.markdown(f"""
    <div style="display:inline-block;background:{bg};color:{color};
                font-size:11px;padding:3px 10px;border-radius:20px;
                font-weight:500;margin-bottom:0.5rem;">{text}</div>
    """, unsafe_allow_html=True)

def page_header(title, subtitle=None):
    st.markdown(
        f"<h2 style='font-size:20px;font-weight:500;color:#2D303E;margin:0;'>{title}</h2>",
        unsafe_allow_html=True
    )
    if subtitle:
        st.markdown(
            f"<p style='font-size:12px;color:#6B7280;margin:3px 0 1rem;'>{subtitle}</p>",
            unsafe_allow_html=True
        )
    else:
        st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)

def hdivider():
    st.markdown(
        '<hr style="border:0;border-top:1px solid #D1FAE5;margin:0.75rem 0;">',
        unsafe_allow_html=True
    )

# ======================
# VIEW: ROLE PICKER
# ======================
if not st.session_state.login and st.session_state.page == "role":

    st.markdown("""
    <div style="text-align:center;padding:2.5rem 0 1rem;">
        <div style="display:inline-flex;align-items:center;gap:12px;margin-bottom:8px;">
            <div style="width:48px;height:48px;background:#2D303E;border-radius:12px;
                        display:flex;align-items:center;justify-content:center;">
                <svg width="26" height="26" viewBox="0 0 22 22" fill="none">
                    <rect x="2" y="6" width="18" height="11" rx="2.5" stroke="#09F289" stroke-width="1.7"/>
                    <path d="M2 9.5h18" stroke="#09F289" stroke-width="1.7"/>
                    <rect x="4.5" y="12" width="6" height="2" rx="0.6" fill="#09F289"/>
                </svg>
            </div>
            <div style="text-align:left;">
                <div style="font-size:28px;font-weight:700;color:#2D303E;line-height:1.1;">KasKita</div>
                <div style="font-size:12px;color:#6B7280;">Manajemen kas kelas digital</div>
            </div>
        </div>
        <p style="font-size:14px;color:#6B7280;margin-top:0.75rem;">Pilih peran untuk melanjutkan</p>
    </div>
    """, unsafe_allow_html=True)

    _, col1, col2, _ = st.columns([1, 1.1, 1.1, 1])

    with col1:
        st.markdown("""
        <div style="background:#FFFFFF;border:1px solid #D1FAE5;border-radius:14px;
                    padding:1.5rem;text-align:center;margin-bottom:10px;">
            <div style="width:48px;height:48px;background:#E6FDF5;border-radius:12px;
                        display:flex;align-items:center;justify-content:center;margin:0 auto 12px;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="8" r="4" stroke="#2D303E" stroke-width="1.6"/>
                    <path d="M4 20c0-4 3.582-7 8-7s8 3 8 7" stroke="#2D303E"
                          stroke-width="1.6" stroke-linecap="round"/>
                </svg>
            </div>
            <div style="font-size:15px;font-weight:500;color:#2D303E;">Admin</div>
            <div style="font-size:11px;color:#6B7280;margin-top:4px;">Kelola kas kelas</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Masuk sebagai Admin", key="btn_admin", type="primary", use_container_width=True):
            st.session_state.role = "admin"
            st.session_state.page = "login"
            st.rerun()

    with col2:
        st.markdown("""
        <div style="background:#FFFFFF;border:1px solid #D1FAE5;border-radius:14px;
                    padding:1.5rem;text-align:center;margin-bottom:10px;">
            <div style="width:48px;height:48px;background:#E6FDF5;border-radius:12px;
                        display:flex;align-items:center;justify-content:center;margin:0 auto 12px;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M4 6h16M4 10h16M4 14h10" stroke="#2D303E"
                          stroke-width="1.6" stroke-linecap="round"/>
                </svg>
            </div>
            <div style="font-size:15px;font-weight:500;color:#2D303E;">User</div>
            <div style="font-size:11px;color:#6B7280;margin-top:4px;">Lihat data kas</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Masuk sebagai User", key="btn_user", type="primary", use_container_width=True):
            st.session_state.role = "user"
            st.session_state.login = True
            st.rerun()

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        with st.expander("🔧  Login Developer"):
            du = st.text_input("Username", key="dev_u")
            dp = st.text_input("Password", type="password", key="dev_p")
            if st.button("Login Developer", key="btn_dev"):
                if du == DEV_USER and dp == DEV_PASS:
                    st.session_state.role = "dev"
                    st.session_state.login = True
                    st.rerun()
                else:
                    st.error("Username atau password salah.")

    st.markdown("""
    <div style="text-align:center;margin-top:2.5rem;">
        <span style="font-size:11px;color:#B0BEC5;">© KasKita 2026</span>
    </div>
    """, unsafe_allow_html=True)

# ======================
# VIEW: LOGIN ADMIN
# ======================
elif not st.session_state.login and st.session_state.page == "login":

    st.markdown("""
    <div style="text-align:center;padding:2rem 0 1.5rem;">
        <div style="font-size:22px;font-weight:600;color:#2D303E;">Login Admin</div>
        <div style="font-size:13px;color:#6B7280;margin-top:4px;">Masukkan detail akun kelas kamu</div>
    </div>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 1.4, 1])
    with mid:
        st.markdown("""
        <div style="background:#FFFFFF;border:1px solid #D1FAE5;border-radius:14px;padding:1.5rem;">
        """, unsafe_allow_html=True)

        st.text_input("Username", placeholder="Masukkan username", key="adm_user")
        st.text_input("Password", type="password", placeholder="••••••••", key="adm_pass")

        c1, c2 = st.columns(2)
        with c1:
            kelas = st.selectbox("Kelas", ["10", "11", "12"])
        with c2:
            jurusan = st.text_input("Jurusan", placeholder="Contoh: RPL")

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        if st.button("Masuk ke Dashboard →", type="primary", use_container_width=True):
            if not jurusan.strip():
                st.warning("Jurusan tidak boleh kosong.")
            else:
                st.session_state.login   = True
                st.session_state.kelas   = kelas
                st.session_state.jurusan = jurusan.upper()
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button("← Kembali pilih role", use_container_width=True):
            st.session_state.page = "role"
            st.rerun()

# ======================
# MAIN APP
# ======================
else:

    # ==================== USER ====================
    if st.session_state.role == "user":

        with st.sidebar:
            render_logo_sidebar()
            info_badge_sidebar("Mode Publik", "#09F289", "rgba(9,242,137,0.12)")
            sidebar_label("Filter data")

        df_all = pd.read_sql("SELECT * FROM kas", conn)

        with st.sidebar:
            if not df_all.empty:
                df_all["bulan"] = pd.to_datetime(df_all["tanggal"]).dt.strftime("%B %Y")
                fk = st.selectbox("Kelas",   sorted(df_all["kelas"].unique()))
                fj = st.selectbox("Jurusan", sorted(df_all["jurusan"].unique()))
                fb = st.selectbox("Bulan",   sorted(df_all["bulan"].unique()))

            sidebar_sep()
            sidebar_user("User Publik")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            if st.button("Keluar", use_container_width=True):
                st.session_state.clear()
                st.rerun()

        page_header("Data kas kelas", "Lihat rekap pembayaran kas")

        if df_all.empty:
            st.info("Belum ada data kas yang tersedia.")
        else:
            df_all["bulan"] = pd.to_datetime(df_all["tanggal"]).dt.strftime("%B %Y")
            df = df_all[
                (df_all["kelas"] == fk) &
                (df_all["jurusan"] == fj) &
                (df_all["bulan"] == fb)
            ].copy()
            df["tanggal"] = pd.to_datetime(df["tanggal"]).dt.strftime("%Y-%m-%d")

            m1, m2, m3 = st.columns(3)
            m1.metric("Total kas",         format_rupiah(df["nominal"].sum()))
            m2.metric("Jumlah transaksi",  f"{len(df)}")
            m3.metric("Pembayaran telat",  f"{len(df[df['status']=='Telat'])} siswa")

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            tab1, tab2 = st.tabs(["📋  Tabel data", "📊  Statistik"])

            with tab1:
                st.dataframe(
                    df.drop(columns=["bulan"], errors="ignore"),
                    use_container_width=True, hide_index=True
                )
                st.download_button(
                    "⬇  Download PDF",
                    generate_pdf(
                        df.drop(columns=["bulan"], errors="ignore"),
                        f"Laporan Kas {fk} {fj} — {fb}"
                    ),
                    f"kas_{fk}_{fj}.pdf",
                    mime="application/pdf"
                )
            with tab2:
                st.markdown("**Status pembayaran**")
                st.bar_chart(df["status"].value_counts())

    # ==================== DEVELOPER ====================
    elif st.session_state.role == "dev":

        with st.sidebar:
            render_logo_sidebar()
            info_badge_sidebar("Developer Panel", "#EF9F27", "rgba(239,159,39,0.15)")
            sidebar_label("Menu")
            menu_dev = st.radio("", ["Akun Admin", "Semua Data Kas"], label_visibility="collapsed")
            sidebar_sep()
            sidebar_user("Developer")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            if st.button("Keluar", use_container_width=True):
                st.session_state.clear()
                st.rerun()

        page_header("Developer panel", "Manajemen sistem KasKita")

        df_admin = pd.read_sql("SELECT * FROM admin", conn)
        df_kas   = pd.read_sql("SELECT * FROM kas",   conn)

        if menu_dev == "Akun Admin":
            st.markdown(
                "<div style='font-size:14px;font-weight:500;color:#2D303E;margin-bottom:.75rem;'>"
                "Daftar akun admin</div>", unsafe_allow_html=True
            )
            if df_admin.empty:
                st.info("Belum ada akun admin.")
            else:
                st.dataframe(df_admin, use_container_width=True, hide_index=True)
                st.download_button(
                    "⬇  Download PDF akun",
                    generate_pdf(df_admin, "Data Akun Admin"),
                    "akun_admin.pdf", mime="application/pdf"
                )
                hdivider()
                st.markdown("**Hapus akun berdasarkan ID**")
                id_del = st.number_input("ID akun", min_value=1, step=1)
                if st.button("Hapus akun", type="primary"):
                    cursor.execute("DELETE FROM admin WHERE id=?", (int(id_del),))
                    conn.commit()
                    st.success(f"Akun ID {int(id_del)} berhasil dihapus.")
                    st.rerun()
        else:
            st
