# ═══════════════════════════════════════════════════════════
#  KAS KITA — Streamlit App (Fixed: no emoji in HTML blocks)
#  Design: dark navy #01023B + neon green #09F289
# ═══════════════════════════════════════════════════════════
import streamlit as st
import pandas as pd
import sqlite3
import io
import time
from datetime import date
from contextlib import contextmanager

from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# ───────────────────────────────────────────────
#  1. PAGE CONFIG
# ───────────────────────────────────────────────
st.set_page_config(
    page_title="KAS KITA",
    page_icon="💳",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ───────────────────────────────────────────────
#  2. GLOBAL CSS
#  FIX: removed all emoji from inside HTML strings
#  to prevent Streamlit Cloud encoding issues
# ───────────────────────────────────────────────
st.markdown("""
<style>
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {
    background: #01023B !important;
    color: #FFFFFF;
}
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebar"] {
    display: none !important;
    visibility: hidden !important;
}
.block-container {
    max-width: 460px !important;
    padding: 0 1rem 7rem !important;
    margin: 0 auto !important;
}
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTextArea textarea {
    background: #080B2E !important;
    border: 1.5px solid #1C2060 !important;
    border-radius: 12px !important;
    color: #FFFFFF !important;
    font-size: 14px !important;
    caret-color: #09F289;
}
.stTextInput input::placeholder,
.stTextArea textarea::placeholder { color: #3D4280 !important; }
.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: #09F289 !important;
    box-shadow: 0 0 0 2px rgba(9,242,137,.18) !important;
}
.stSelectbox > div > div > div {
    background: #080B2E !important;
    border: 1.5px solid #1C2060 !important;
    border-radius: 12px !important;
    color: #FFFFFF !important;
}
.stSelectbox svg { fill: #09F289 !important; }
.stTextInput label,
.stNumberInput label,
.stDateInput label,
.stSelectbox label,
.stTextArea label {
    color: #6B72B0 !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: .07em !important;
    text-transform: uppercase !important;
}
.stButton > button {
    width: 100% !important;
    background: #09F289 !important;
    color: #01023B !important;
    border: none !important;
    border-radius: 14px !important;
    font-size: 15px !important;
    font-weight: 800 !important;
    padding: 13px 20px !important;
    letter-spacing: .5px !important;
    transition: opacity .15s !important;
    cursor: pointer !important;
}
.stButton > button:hover  { opacity: .87 !important; }
.stButton > button:active { opacity: .72 !important; }
.stDownloadButton > button {
    background: #09F289 !important;
    color: #01023B !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
    width: 100% !important;
    padding: 12px 20px !important;
}
[data-testid="stAlert"] {
    border-radius: 12px !important;
    font-size: 13px !important;
}
[data-testid="stDataFrame"] {
    background: #0C1040 !important;
    border-radius: 14px !important;
    border: 1px solid #1C2060 !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] * { color: #FFFFFF !important; }
.streamlit-expanderHeader {
    background: #0C1040 !important;
    border: 1px solid #1C2060 !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
}
.streamlit-expanderContent {
    background: #080B2E !important;
    border: 1px solid #1C2060 !important;
    border-radius: 0 0 10px 10px !important;
}
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #01023B; }
::-webkit-scrollbar-thumb { background: #1C2060; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ───────────────────────────────────────────────
#  3. DATABASE
# ───────────────────────────────────────────────
DB = "kaskita.db"

@st.cache_resource
def _bootstrap_db() -> str:
    conn = sqlite3.connect(DB, check_same_thread=False)
    conn.executescript("""
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS kas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL, tanggal TEXT NOT NULL,
            status TEXT NOT NULL, kelas TEXT NOT NULL,
            jurusan TEXT NOT NULL, keterangan TEXT,
            nominal INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS admin_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL, password TEXT NOT NULL,
            email TEXT, kelas TEXT, jurusan TEXT);
        CREATE TABLE IF NOT EXISTS pengeluaran (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT NOT NULL, kelas TEXT NOT NULL,
            jurusan TEXT NOT NULL, keterangan TEXT,
            nominal INTEGER NOT NULL DEFAULT 0);
    """)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM admin_accounts")
    if cur.fetchone()[0] == 0:
        conn.executemany(
            "INSERT OR IGNORE INTO admin_accounts"
            "(username,password,email,kelas,jurusan) VALUES(?,?,?,?,?)",
            [
                ("admin_dhimas",   "pass","dhimas.dev@kaskita.id", "XII","RPL"),
                ("sari_keuangan",  "pass","sari.p@kaskita.id",     "XI", "IPA"),
                ("rendy_bendahara","pass","rendy.b@kaskita.id",    "X",  "IPS"),
                ("fauzan_monitor", "pass","fauzan.m@kaskita.id",   "XII","MIPA"),
            ]
        )
    conn.commit()
    conn.close()
    return DB

_bootstrap_db()

@contextmanager
def _db():
    conn = sqlite3.connect(DB, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def db_read(sql: str, params: tuple = ()) -> pd.DataFrame:
    with _db() as c:
        try:
            return pd.read_sql_query(sql, c, params=params)
        except Exception as e:
            st.error(f"DB read error: {e}")
            return pd.DataFrame()

def db_write(sql: str, params: tuple = ()) -> bool:
    with _db() as c:
        try:
            c.execute(sql, params)
            return True
        except Exception as e:
            st.error(f"DB write error: {e}")
            return False

# ───────────────────────────────────────────────
#  4. SESSION STATE
# ───────────────────────────────────────────────
_SESS = {
    "page":"role","role":None,"login":False,
    "kelas":"XII","jurusan":"RPL","subnav":"dashboard",
}

def _init_sess():
    for k, v in _SESS.items():
        if k not in st.session_state:
            st.session_state[k] = v

def _reset_sess():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    _init_sess()

_init_sess()

# ───────────────────────────────────────────────
#  5. HELPERS
# ───────────────────────────────────────────────
def fmt_rp(n) -> str:
    try:
        return "Rp {:,.0f}".format(int(n)).replace(",",".")
    except Exception:
        return "Rp 0"

def clean_nom(raw) -> int:
    if raw is None: return 0
    s = str(raw).strip().lower()
    for ch in ["rp"," ",".",","]: s = s.replace(ch,"")
    return int(s) if s.isdigit() else 0

def safe(v) -> str:
    return str(v) if v is not None else ""

def gen_pdf(df: pd.DataFrame, title: str = "Laporan KasKita") -> bytes:
    try:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                topMargin=40, bottomMargin=40,
                                leftMargin=30, rightMargin=30)
        sty = getSampleStyleSheet()
        safe_df = df.fillna("").astype(str)
        data = [list(safe_df.columns)] + safe_df.values.tolist()
        cw = [doc.width / len(safe_df.columns)] * len(safe_df.columns)
        t = Table(data, repeatRows=1, colWidths=cw)
        t.setStyle(TableStyle([
            ("BACKGROUND",     (0,0),(-1,0), colors.HexColor("#01023B")),
            ("TEXTCOLOR",      (0,0),(-1,0), colors.HexColor("#09F289")),
            ("FONTNAME",       (0,0),(-1,0), "Helvetica-Bold"),
            ("FONTSIZE",       (0,0),(-1,0), 9),
            ("ROWBACKGROUNDS", (0,1),(-1,-1),[colors.white,colors.HexColor("#F0F8FF")]),
            ("TEXTCOLOR",      (0,1),(-1,-1), colors.HexColor("#01023B")),
            ("FONTSIZE",       (0,1),(-1,-1), 8),
            ("GRID",           (0,0),(-1,-1),.4, colors.HexColor("#CCDDEE")),
            ("PADDING",        (0,0),(-1,-1), 5),
            ("VALIGN",         (0,0),(-1,-1), "MIDDLE"),
        ]))
        doc.build([Paragraph(f"<b>{title}</b>", sty["Title"]),
                   Spacer(1,12), t, Spacer(1,16),
                   Paragraph("KasKita 2026", sty["Normal"])])
        return buf.getvalue()
    except Exception as e:
        st.error(f"PDF error: {e}")
        return b""

# ───────────────────────────────────────────────
#  6. SHARED UI COMPONENTS
#  FIX: topbars now use st.columns (native Streamlit)
#  instead of st.markdown HTML to avoid raw-text
#  rendering bug on Streamlit Cloud
# ───────────────────────────────────────────────

def _logo_html(subtitle: str = "") -> str:
    """Pure HTML logo block — NO emoji inside."""
    sub = (f'<div style="font-size:10px;color:#6B72B0;margin-top:1px;">'
           f'{subtitle}</div>') if subtitle else ""
    return f"""
    <div style="display:flex;align-items:center;gap:10px;">
        <div style="width:36px;height:36px;background:#09F289;border-radius:9px;
                    display:flex;align-items:center;justify-content:center;flex-shrink:0;">
            <svg width="19" height="19" viewBox="0 0 22 22" fill="none">
                <rect x="2" y="6" width="18" height="11" rx="2.5"
                      stroke="#01023B" stroke-width="1.9"/>
                <path d="M2 9.5h18" stroke="#01023B" stroke-width="1.9"/>
                <rect x="4.5" y="12" width="6" height="2" rx=".6" fill="#01023B"/>
            </svg>
        </div>
        <div>
            <div style="font-size:16px;font-weight:900;color:#09F289;
                        letter-spacing:.6px;line-height:1.1;">KASKITA</div>
            {sub}
        </div>
    </div>"""


def _topbar(subtitle: str = "", show_avatar: bool = False):
    """
    FIX: use st.columns so Streamlit renders it natively.
    Bell icon rendered via st.markdown separately (no emoji in f-string HTML).
    """
    left_col, right_col = st.columns([5, 1])
    with left_col:
        if show_avatar:
            av_col, logo_col = st.columns([1, 5])
            with av_col:
                st.markdown("""
                <div style="width:34px;height:34px;border-radius:50%;
                            background:#1C2060;border:2px solid #09F289;
                            display:flex;align-items:center;justify-content:center;
                            margin-top:14px;">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                         stroke="#09F289" stroke-width="2"
                         stroke-linecap="round" stroke-linejoin="round">
                        <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
                        <circle cx="12" cy="7" r="4"/>
                    </svg>
                </div>""", unsafe_allow_html=True)
            with logo_col:
                st.markdown(
                    f'<div style="padding-top:14px;">{_logo_html(subtitle)}</div>',
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                f'<div style="padding-top:14px;">{_logo_html(subtitle)}</div>',
                unsafe_allow_html=True
            )
    with right_col:
        st.markdown(
            '<div style="padding-top:16px;text-align:right;font-size:20px;">&#128276;</div>',
            unsafe_allow_html=True
        )


def _card(html, pad="1.2rem 1.4rem", mb="1rem",
          border="1px solid #1C2060", bg="#0C1040",
          radius="18px", extra=""):
    st.markdown(f"""
    <div style="background:{bg};border:{border};border-radius:{radius};
                padding:{pad};margin-bottom:{mb};{extra}">{html}</div>
    """, unsafe_allow_html=True)


def _sec(text, right=""):
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
                margin:1.2rem 0 .65rem;">
        <span style="font-size:17px;font-weight:700;color:#FFFFFF;">{text}</span>
        {right}
    </div>""", unsafe_allow_html=True)


def _bottom_nav(active="dashboard"):
    """Visual-only fixed bottom nav bar (HTML, no emoji)."""
    ITEMS = [
        ("dashboard",
         "M3 3h7v7H3V3zm0 11h7v7H3v-7zm11-11h7v7h-7V3zm0 11h7v7h-7v-7z",
         "DASHBOARD"),
        ("history",
         "M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z",
         "HISTORY"),
        ("logout",
         "M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-6 0v-1m0-8V7a3 3 0 016 0v1",
         "LOGOUT"),
    ]
    parts = ""
    for key, path, lbl in ITEMS:
        is_on = active == key
        col   = "#09F289" if is_on else "#3D4499"
        bgc   = "background:rgba(9,242,137,.12);border-radius:12px;" if is_on else ""
        parts += f"""
        <div style="{bgc}padding:6px 18px;display:flex;flex-direction:column;
                    align-items:center;gap:3px;">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
                 stroke="{col}" stroke-width="2"
                 stroke-linecap="round" stroke-linejoin="round">
                <path d="{path}"/>
            </svg>
            <span style="font-size:9px;font-weight:700;color:{col};
                         letter-spacing:.06em;">{lbl}</span>
        </div>"""

    st.markdown(f"""
    <div style="position:fixed;bottom:0;left:50%;transform:translateX(-50%);
                width:100%;max-width:460px;background:#01023B;
                border-top:1px solid #1C2060;padding:8px 16px 10px;
                z-index:9000;display:flex;justify-content:space-around;
                align-items:center;">{parts}</div>
    """, unsafe_allow_html=True)


def _nav_row(key_prefix):
    """Actual clickable Streamlit buttons for navigation."""
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Dashboard", key=f"{key_prefix}_db"):
            st.session_state["subnav"] = "dashboard"
            st.rerun()
    with c2:
        if st.button("History", key=f"{key_prefix}_hs"):
            st.session_state["subnav"] = "history"
            st.rerun()
    with c3:
        if st.button("Logout", key=f"{key_prefix}_lo"):
            _reset_sess()
            st.rerun()

# ───────────────────────────────────────────────
#  7. PAGE: ROLE SELECTION
# ───────────────────────────────────────────────
def _page_role():
    st.markdown("""
    <div style="text-align:center;padding:2.5rem 0 1.5rem;">
        <div style="display:inline-flex;align-items:center;gap:10px;
                    margin-bottom:1.5rem;">
            <div style="width:44px;height:44px;background:#09F289;
                        border-radius:12px;display:flex;align-items:center;
                        justify-content:center;">
                <svg width="24" height="24" viewBox="0 0 22 22" fill="none">
                    <rect x="2" y="6" width="18" height="11" rx="2.5"
                          stroke="#01023B" stroke-width="1.9"/>
                    <path d="M2 9.5h18" stroke="#01023B" stroke-width="1.9"/>
                    <rect x="4.5" y="12" width="6" height="2"
                          rx=".6" fill="#01023B"/>
                </svg>
            </div>
            <span style="font-size:21px;font-weight:900;color:#09F289;
                         letter-spacing:.6px;">KAS KITA</span>
        </div>
        <h1 style="font-size:28px;font-weight:800;color:#FFFFFF;
                   margin:0 0 .8rem;line-height:1.25;">
            Selamat Datang di<br>Kas Kita</h1>
        <p style="font-size:14px;color:#6B72B0;margin:0;line-height:1.7;">
            Tentukan peran Anda untuk mulai<br>
            mengelola ekosistem finansial digital yang cerdas.
        </p>
    </div>""", unsafe_allow_html=True)

    ROLES = [
        ("admin","#1A2460","Admin",
         "Manajemen sistem penuh, kontrol otorisasi, dan audit laporan konsolidasi.",
         "border:1px solid #1C2060;",
         "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"),
        ("user","#09F289","User",
         "Akses personal untuk mencatat transaksi, memantau saldo, dan laporan individu.",
         "border:2px solid #09F289;",
         "M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2 M12 11a4 4 0 100-8 4 4 0 000 8z"),
        ("dev","#1A2460","Developer",
         "Integrasi API, kustomisasi teknis, dan pemeliharaan struktur basis data.",
         "border:1px solid #1C2060;",
         "M8 3H5a2 2 0 00-2 2v3m18 0V5a2 2 0 00-2-2h-3M3 16v3a2 2 0 002 2h3m10 0h3a2 2 0 002-2v-3"),
    ]

    for key, icon_bg, label, desc, bstyle, svg_path in ROLES:
        stroke_col = "#01023B" if icon_bg == "#09F289" else "#09F289"
        st.markdown(f"""
        <div style="background:#0C1040;{bstyle}border-radius:20px;
                    padding:1.4rem 1.4rem .6rem;margin-bottom:.5rem;">
            <div style="width:54px;height:54px;background:{icon_bg};
                        border-radius:14px;display:flex;align-items:center;
                        justify-content:center;margin-bottom:1rem;">
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none"
                     stroke="{stroke_col}" stroke-width="2"
                     stroke-linecap="round" stroke-linejoin="round">
                    <path d="{svg_path}"/>
                </svg>
            </div>
            <div style="font-size:20px;font-weight:700;color:#FFFFFF;
                        margin-bottom:.4rem;">{label}</div>
            <div style="font-size:13px;color:#6B72B0;line-height:1.65;
                        margin-bottom:.75rem;">{desc}</div>
            <div style="font-size:11px;font-weight:700;color:#09F289;
                        letter-spacing:.07em;margin-bottom:.75rem;">
                PILIH ROLE &nbsp;&rarr;
            </div>
        </div>""", unsafe_allow_html=True)

        if st.button("PILIH ROLE", key=f"r_{key}"):
            if key == "admin":
                st.session_state.update(role="admin", page="login_admin")
            elif key == "user":
                st.session_state.update(role="user", login=True, page="user")
            elif key == "dev":
                st.session_state.update(role="dev", page="login_dev")
            st.rerun()

    st.markdown("""
    <div style="text-align:center;margin-top:1.5rem;padding-bottom:1rem;">
        <span style="font-size:10px;color:#1C2560;letter-spacing:.14em;
                     text-transform:uppercase;">
            &mdash;&mdash; ENKRIPSI VAULT 256-BIT &mdash;&mdash;
        </span>
    </div>""", unsafe_allow_html=True)

# ───────────────────────────────────────────────
#  8. PAGE: LOGIN ADMIN
# ───────────────────────────────────────────────
def _page_login_admin():
    _topbar("Masuk sebagai Admin")
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="padding:.5rem 0 1.25rem;">
        <h2 style="font-size:23px;font-weight:800;color:#FFFFFF;margin:0 0 .3rem;">
            Login Admin</h2>
        <p style="font-size:13px;color:#6B72B0;margin:0;">
            Masukkan detail kelas untuk melanjutkan</p>
    </div>""", unsafe_allow_html=True)

    username = st.text_input("USERNAME", placeholder="Contoh: admin_dhimas", key="la_u")
    st.text_input("PASSWORD", type="password", placeholder="Password", key="la_p")
    c1, c2 = st.columns(2)
    with c1: kelas   = st.selectbox("KELAS", ["X","XI","XII"], index=2, key="la_k")
    with c2: jurusan = st.text_input("JURUSAN", placeholder="RPL", key="la_j")

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    if st.button("MASUK KE DASHBOARD", key="la_go"):
        if not username.strip():
            st.error("Username tidak boleh kosong.")
        elif not jurusan.strip():
            st.error("Jurusan tidak boleh kosong.")
        else:
            st.session_state.update(
                login=True, kelas=kelas,
                jurusan=jurusan.strip().upper(),
                page="admin", subnav="dashboard"
            )
            st.rerun()

    if st.button("Kembali ke pilih role", key="la_back"):
        st.session_state["page"] = "role"
        st.rerun()

# ───────────────────────────────────────────────
#  9. PAGE: LOGIN DEVELOPER
# ───────────────────────────────────────────────
def _page_login_dev():
    _topbar("Developer Access")
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="padding:.5rem 0 1.25rem;">
        <h2 style="font-size:23px;font-weight:800;color:#FFFFFF;margin:0 0 .3rem;">
            Login Developer</h2>
        <p style="font-size:13px;color:#6B72B0;margin:0;">
            Kredensial akses sistem backend</p>
    </div>""", unsafe_allow_html=True)

    du = st.text_input("USERNAME", placeholder="developer", key="ld_u")
    dp = st.text_input("PASSWORD", type="password", placeholder="Password", key="ld_p")
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    if st.button("MASUK DEVELOPER PANEL", key="ld_go"):
        if not du.strip() or not dp:
            st.error("Isi username dan password.")
        elif du.strip() == "developer" and dp == "kaskita":
            st.session_state.update(
                login=True, role="dev",
                page="dev", subnav="dashboard"
            )
            st.rerun()
        else:
            st.error("Kredensial salah. Gunakan: developer / kaskita")

    if st.button("Kembali ke pilih role", key="ld_back"):
        st.session_state["page"] = "role"
        st.rerun()

# ───────────────────────────────────────────────
#  10. PAGE: ADMIN DASHBOARD
# ───────────────────────────────────────────────
def _page_admin():
    kls = st.session_state["kelas"]
    jrs = st.session_state["jurusan"]
    nav = st.session_state["subnav"]

    # Topbar with avatar using st.columns
    col_av, col_logo, col_bell = st.columns([1, 5, 1])
    with col_av:
        st.markdown("""
        <div style="padding-top:14px;">
            <div style="width:34px;height:34px;border-radius:50%;
                        background:#1C2060;border:2px solid #09F289;
                        display:flex;align-items:center;justify-content:center;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                     stroke="#09F289" stroke-width="2"
                     stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                </svg>
            </div>
        </div>""", unsafe_allow_html=True)
    with col_logo:
        st.markdown(f'<div style="padding-top:14px;">{_logo_html()}</div>',
                    unsafe_allow_html=True)
    with col_bell:
        st.markdown(
            '<div style="padding-top:16px;text-align:right;font-size:20px;">&#128276;</div>',
            unsafe_allow_html=True
        )

    st.markdown(f"""
    <div style="padding:.4rem 0 1rem;">
        <div style="font-size:23px;font-weight:800;color:#FFFFFF;">
            Halo, <span style="color:#09F289;">Admin</span></div>
        <div style="font-size:13px;color:#6B72B0;margin-top:3px;">
            Status Keuangan Kelas:
            <span style="color:#09F289;font-weight:700;">{kls} {jrs}</span>
        </div>
    </div>""", unsafe_allow_html=True)

    df = db_read("SELECT * FROM kas WHERE kelas=? AND jurusan=?", (kls, jrs))
    if not df.empty:
        df["tanggal"] = pd.to_datetime(
            df["tanggal"], errors="coerce"
        ).dt.strftime("%Y-%m-%d")

    total_kas   = int(df["nominal"].sum()) if not df.empty else 0
    tepat_count = int((df["status"]=="Tepat Waktu").sum()) if not df.empty else 0
    telat_count = int((df["status"]=="Telat").sum())       if not df.empty else 0

    # ────────── DASHBOARD ──────────
    if nav == "dashboard":

        # Total kas card
        _card(f"""
        <div style="display:flex;align-items:flex-start;justify-content:space-between;">
            <div>
                <div style="font-size:10px;font-weight:700;color:#6B72B0;
                            letter-spacing:.09em;text-transform:uppercase;
                            margin-bottom:.4rem;">TOTAL KAS</div>
                <div style="font-size:28px;font-weight:800;color:#FFFFFF;
                            margin-bottom:.3rem;">{fmt_rp(total_kas)}</div>
                <div style="font-size:12px;color:#09F289;font-weight:700;">
                    &#8593; 12% dari bulan lalu</div>
            </div>
            <div style="width:34px;height:34px;background:#09F289;border-radius:9px;
                        display:flex;align-items:center;justify-content:center;">
                <svg width="18" height="18" viewBox="0 0 22 22" fill="none">
                    <rect x="2" y="6" width="18" height="11" rx="2.5"
                          stroke="#01023B" stroke-width="1.9"/>
                    <path d="M2 9.5h18" stroke="#01023B" stroke-width="1.9"/>
                    <rect x="4.5" y="12" width="6" height="2"
                          rx=".6" fill="#01023B"/>
                </svg>
            </div>
        </div>""")

        # Statistik Siswa
        _sec("Statistik Siswa")
        st.markdown("""
        <div style="background:#0C1040;border:1px solid #1C2060;border-radius:18px;
                    padding:1.2rem 1.4rem;margin-bottom:1rem;">
        <div style="font-size:10px;font-weight:700;color:#6B72B0;
                    letter-spacing:.09em;text-transform:uppercase;
                    margin-bottom:.4rem;">PILIH SISWA</div>
        """, unsafe_allow_html=True)

        if df.empty:
            st.info("Belum ada data siswa.")
        else:
            siswa_list = sorted(df["nama"].dropna().unique().tolist())
            sel = st.selectbox("", siswa_list, label_visibility="collapsed",
                               key="adm_siswa_sel")
            ds  = df[df["nama"] == sel]
            tot = len(ds)
            tel = int((ds["status"]=="Telat").sum())
            tpt = tot - tel
            pct = int((tpt / tot) * 100) if tot > 0 else 0
            pct_bad = (tel / tot * 100) if tot > 0 else 0
            if pct_bad < 20:
                perf, pc = "PERFORMA SANGAT BAIK", "#09F289"
            elif pct_bad < 50:
                perf, pc = "PERLU PENINGKATAN", "#F5A623"
            else:
                perf, pc = "SERING TELAT", "#FF5050"

            CIRC = 99.9
            dash_g = round(pct / 100 * CIRC, 1)
            dash_e = round(CIRC - dash_g, 1)

            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:1.4rem;margin-top:.8rem;">
                <div style="position:relative;width:80px;height:80px;flex-shrink:0;">
                    <svg viewBox="0 0 36 36" width="80" height="80">
                        <circle cx="18" cy="18" r="15.9" fill="none"
                                stroke="#1C2060" stroke-width="3.5"/>
                        <circle cx="18" cy="18" r="15.9" fill="none"
                                stroke="#09F289" stroke-width="3.5"
                                stroke-dasharray="{dash_g} {dash_e}"
                                stroke-dashoffset="25"
                                stroke-linecap="round"/>
                    </svg>
                    <div style="position:absolute;top:50%;left:50%;
                                transform:translate(-50%,-50%);
                                font-size:14px;font-weight:800;color:#FFFFFF;">
                        {pct}%</div>
                </div>
                <div>
                    <div style="display:flex;gap:1rem;margin-bottom:.5rem;">
                        <span style="font-size:12px;color:#6B72B0;">
                            TEPAT WAKTU:
                            <b style="color:#09F289;">{tpt}</b></span>
                        <span style="font-size:12px;color:#6B72B0;">
                            TELAT:
                            <b style="color:#FF5050;">{tel}</b></span>
                    </div>
                    <span style="background:rgba(9,242,137,.12);color:{pc};
                                 font-size:10px;font-weight:700;padding:4px 10px;
                                 border-radius:8px;letter-spacing:.04em;">
                        &#9679; {perf}</span>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Input Pembayaran
        _sec("Input Pembayaran")
        st.markdown("""
        <div style="background:#0C1040;border:1px solid #1C2060;border-radius:18px;
                    padding:1.2rem 1.4rem 1rem;margin-bottom:1rem;">
        """, unsafe_allow_html=True)

        with st.form("kas_form", clear_on_submit=True):
            nama    = st.text_input("NAMA SISWA",
                                    placeholder="Contoh: Ahmad Fauzan", key="fi_nama")
            c1, c2  = st.columns(2)
            with c1: tgl    = st.date_input("TANGGAL", value=date.today(), key="fi_tgl")
            with c2: status = st.selectbox("STATUS", ["Tepat Waktu","Telat"],
                                            key="fi_status")
            nominal = st.text_input("NOMINAL (RP)", placeholder="20000", key="fi_nom")
            ket     = st.text_area("KETERANGAN",
                                   placeholder="Kas Minggu ke-2 Februari",
                                   key="fi_ket", height=80)
            submit  = st.form_submit_button("Simpan Data")

        st.markdown("</div>", unsafe_allow_html=True)

        if submit:
            if not nama.strip():
                st.error("Nama siswa tidak boleh kosong.")
            elif clean_nom(nominal) <= 0:
                st.error("Nominal harus lebih dari 0.")
            else:
                ok = db_write(
                    "INSERT INTO kas(nama,tanggal,status,kelas,jurusan,"
                    "keterangan,nominal) VALUES(?,?,?,?,?,?,?)",
                    (nama.strip(), str(tgl), status, kls, jrs,
                     ket.strip(), clean_nom(nominal))
                )
                if ok:
                    st.success(f"Data {nama.strip()} tersimpan!")
                    time.sleep(.4)
                    st.rerun()

        # Distribusi
        _sec("Distribusi Status Bayar")
        st.markdown(f"""
        <div style="background:#0C1040;border:1px solid #1C2060;border-radius:18px;
                    padding:1.4rem 1.8rem;margin-bottom:1rem;display:flex;gap:3rem;">
            <div style="text-align:center;">
                <div style="font-size:40px;font-weight:800;color:#09F289;">
                    {tepat_count}</div>
                <div style="font-size:10px;font-weight:700;color:#6B72B0;
                            letter-spacing:.07em;text-transform:uppercase;
                            margin-top:4px;">TEPAT WAKTU</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:40px;font-weight:800;color:#FF5050;">
                    {telat_count}</div>
                <div style="font-size:10px;font-weight:700;color:#6B72B0;
                            letter-spacing:.07em;text-transform:uppercase;
                            margin-top:4px;">TELAT</div>
            </div>
        </div>""", unsafe_allow_html=True)

        # Riwayat
        _sec("Riwayat Data Kas",
             right='<span style="font-size:12px;color:#09F289;font-weight:700;">'
                   'LIHAT SEMUA</span>')

        if df.empty:
            st.info("Belum ada data kas.")
        else:
            for _, row in df.tail(10).iloc[::-1].iterrows():
                is_t = row["status"] == "Tepat Waktu"
                sc   = "#09F289" if is_t else "#FF5050"
                sbg  = "rgba(9,242,137,.12)" if is_t else "rgba(255,80,80,.12)"
                slbl = "TEPAT WAKTU" if is_t else "TELAT"
                _card(f"""
                <div style="display:flex;align-items:flex-start;
                            justify-content:space-between;gap:.5rem;">
                    <div style="flex:1;min-width:0;">
                        <div style="font-size:14px;font-weight:700;color:#FFFFFF;
                                    white-space:nowrap;overflow:hidden;
                                    text-overflow:ellipsis;">
                            {safe(row.get("nama",""))}</div>
                        <div style="font-size:11px;color:#6B72B0;margin-top:2px;">
                            {safe(row.get("keterangan",""))}</div>
                        <div style="font-size:11px;color:#3D4499;margin-top:4px;">
                            {safe(row.get("tanggal",""))}</div>
                    </div>
                    <div style="text-align:right;flex-shrink:0;">
                        <span style="background:{sbg};color:{sc};font-size:9px;
                                     font-weight:700;padding:3px 8px;
                                     border-radius:6px;">{slbl}</span>
                        <div style="font-size:14px;font-weight:700;
                                    color:#09F289;margin-top:5px;">
                            + {fmt_rp(row.get("nominal",0))}</div>
                    </div>
                </div>""", pad=".9rem 1.1rem", mb=".5rem")

            pdf = gen_pdf(df, f"Laporan Kas {kls} {jrs}")
            if pdf:
                st.download_button("Download PDF Kas", pdf,
                                   f"kas_{kls}_{jrs}.pdf",
                                   mime="application/pdf", key="dl_adm")

        # Hapus data
        with st.expander("Hapus Data"):
            st.markdown(
                '<div style="font-size:12px;color:#FF5050;margin-bottom:.6rem;">'
                'Tindakan ini tidak bisa dibatalkan.</div>',
                unsafe_allow_html=True
            )
            konfirmasi = st.checkbox("Saya memahami risiko ini", key="adm_confirm")
            cc1, cc2, cc3 = st.columns(3)
            with cc1:
                id_hp = st.number_input("Hapus ID", min_value=1, step=1,
                                        key="adm_del_id")
                if st.button("Hapus ID", key="adm_del_id_btn"):
                    if konfirmasi:
                        db_write("DELETE FROM kas WHERE id=?", (int(id_hp),))
                        st.success("Dihapus.")
                        st.rerun()
                    else:
                        st.error("Centang konfirmasi.")
            with cc2:
                if not df.empty:
                    sdel = st.selectbox("Hapus Siswa",
                                        df["nama"].dropna().unique(),
                                        key="adm_del_siswa")
                    if st.button("Hapus Siswa", key="adm_del_s_btn"):
                        if konfirmasi:
                            db_write("DELETE FROM kas WHERE nama=? "
                                     "AND kelas=? AND jurusan=?",
                                     (sdel, kls, jrs))
                            st.success("Dihapus.")
                            st.rerun()
                        else:
                            st.error("Centang konfirmasi.")
            with cc3:
                st.caption(f"Hapus semua data kelas {kls} {jrs}")
                if st.button("Hapus Semua", key="adm_del_all_btn"):
                    if konfirmasi:
                        db_write("DELETE FROM kas WHERE kelas=? AND jurusan=?",
                                 (kls, jrs))
                        st.success("Semua data dihapus.")
                        st.rerun()
                    else:
                        st.error("Centang konfirmasi.")

    # ────────── HISTORY ──────────
    elif nav == "history":
        _sec("Riwayat Lengkap")
        if df.empty:
            st.info("Belum ada data.")
        else:
            dh = df.copy()
            dh["nominal"] = dh["nominal"].apply(fmt_rp)
            st.dataframe(dh, use_container_width=True, hide_index=True)
            pdf = gen_pdf(df, f"Riwayat Kas {kls} {jrs}")
            if pdf:
                st.download_button("Download PDF", pdf,
                                   f"riwayat_{kls}_{jrs}.pdf",
                                   mime="application/pdf", key="dl_adm_h")

    _bottom_nav(nav)
    _nav_row("adm")

# ───────────────────────────────────────────────
#  11. PAGE: USER
# ───────────────────────────────────────────────
def _page_user():
    # Topbar with avatar
    col_av, col_logo, col_bell = st.columns([1, 5, 1])
    with col_av:
        st.markdown("""
        <div style="padding-top:14px;">
            <div style="width:34px;height:34px;border-radius:50%;
                        background:#1C2060;border:2px solid #09F289;
                        display:flex;align-items:center;justify-content:center;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                     stroke="#09F289" stroke-width="2"
                     stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                </svg>
            </div>
        </div>""", unsafe_allow_html=True)
    with col_logo:
        st.markdown(f'<div style="padding-top:14px;">{_logo_html()}</div>',
                    unsafe_allow_html=True)
    with col_bell:
        st.markdown(
            '<div style="padding-top:16px;text-align:right;font-size:20px;">&#128276;</div>',
            unsafe_allow_html=True
        )

    df_all = db_read("SELECT * FROM kas")
    if df_all.empty:
        st.info("Belum ada data kas tersedia.")
        if st.button("Logout", key="usr_lo_e"):
            _reset_sess(); st.rerun()
        return

    df_all["bulan_label"] = pd.to_datetime(
        df_all["tanggal"], errors="coerce"
    ).dt.strftime("%B %Y").fillna("—")

    # Filter card
    st.markdown("""
    <div style="background:#0C1040;border:1px solid #1C2060;border-radius:18px;
                padding:1.2rem 1.4rem;margin-bottom:1rem;">
    """, unsafe_allow_html=True)

    jrs_opts = ["Semua"] + sorted(df_all["jurusan"].dropna().unique().tolist())
    kls_opts = ["Semua"] + sorted(df_all["kelas"].dropna().unique().tolist())
    bln_opts = ["Semua"] + sorted(df_all["bulan_label"].dropna().unique().tolist())

    fj = st.selectbox("Pilih Jurusan", jrs_opts, key="uf_j")
    fk = st.selectbox("Pilih Kelas",   kls_opts, key="uf_k")
    fb = st.selectbox("Pilih Bulan",   bln_opts, key="uf_b")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("CEK SEKARANG", key="usr_cek"):
        df_f = df_all.copy()
        if fj != "Semua": df_f = df_f[df_f["jurusan"] == fj]
        if fk != "Semua": df_f = df_f[df_f["kelas"]   == fk]
        if fb != "Semua": df_f = df_f[df_f["bulan_label"] == fb]
        st.session_state["usr_res"] = df_f.to_dict(orient="records")

    recs    = st.session_state.get("usr_res", None)
    df_show = pd.DataFrame(recs) if recs is not None else df_all.copy()

    if "bulan_label" in df_show.columns:
        df_show = df_show.drop(columns=["bulan_label"])
    if not df_show.empty:
        df_show["tanggal"] = pd.to_datetime(
            df_show["tanggal"], errors="coerce"
        ).dt.strftime("%d %b %Y").fillna("—")

    _sec("Riwayat Data Kas",
         right='<span style="font-size:12px;color:#09F289;font-weight:700;">'
               'LIHAT SEMUA</span>')

    # Table header
    st.markdown("""
    <div style="background:#080B2E;border:1px solid #1C2060;
                border-radius:14px 14px 0 0;padding:.7rem 1rem;
                display:grid;grid-template-columns:2fr 1.3fr 1.2fr 1fr;gap:.5rem;">
        <span style="font-size:10px;font-weight:700;color:#3D4499;
                     text-transform:uppercase;letter-spacing:.06em;">NAMA SISWA</span>
        <span style="font-size:10px;font-weight:700;color:#3D4499;
                     text-transform:uppercase;letter-spacing:.06em;">TANGGAL</span>
        <span style="font-size:10px;font-weight:700;color:#3D4499;
                     text-transform:uppercase;letter-spacing:.06em;">STATUS</span>
        <span style="font-size:10px;font-weight:700;color:#3D4499;
                     text-transform:uppercase;letter-spacing:.06em;">NOMINAL</span>
    </div>""", unsafe_allow_html=True)

    if df_show.empty:
        st.info("Tidak ada data untuk filter ini.")
    else:
        rows = ""
        for i, (_, row) in enumerate(df_show.head(20).iterrows()):
            is_t  = str(row.get("status","")) == "Tepat Waktu"
            sc    = "#09F289" if is_t else "#FF5050"
            sbg   = "rgba(9,242,137,.12)" if is_t else "rgba(255,80,80,.12)"
            slbl  = "BERHASIL" if is_t else "PENDING"
            nc    = "#09F289" if is_t else "#FFFFFF"
            pfx   = "+" if is_t else ""
            sep   = ("" if i == len(df_show.head(20))-1
                     else "border-bottom:1px solid #1C2060;")
            try:   nom_k = int(row.get("nominal",0)) // 1000
            except: nom_k = 0

            rows += f"""
            <div style="padding:.85rem 1rem;display:grid;
                        grid-template-columns:2fr 1.3fr 1.2fr 1fr;
                        gap:.5rem;align-items:center;{sep}">
                <div>
                    <div style="font-size:13px;font-weight:600;color:#FFFFFF;
                                white-space:nowrap;overflow:hidden;
                                text-overflow:ellipsis;">
                        {safe(row.get("nama",""))}</div>
                    <div style="font-size:10px;color:#3D4499;margin-top:2px;">
                        {safe(row.get("kelas",""))}
                        {safe(row.get("jurusan",""))}</div>
                </div>
                <div style="font-size:11px;color:#6B72B0;">
                    {safe(row.get("tanggal",""))}</div>
                <div>
                    <span style="background:{sbg};color:{sc};font-size:9px;
                                 font-weight:700;padding:3px 8px;
                                 border-radius:6px;">{slbl}</span>
                </div>
                <div style="font-size:12px;font-weight:700;color:{nc};">
                    {pfx} {nom_k}k</div>
            </div>"""

        st.markdown(f"""
        <div style="background:#0C1040;border:1px solid #1C2060;border-top:none;
                    border-radius:0 0 14px 14px;margin-bottom:1rem;">{rows}</div>
        """, unsafe_allow_html=True)

        pdf = gen_pdf(df_show, "Laporan Kas User")
        if pdf:
            st.download_button("Download PDF", pdf, "kas_user.pdf",
                               mime="application/pdf", key="dl_usr")

    _bottom_nav("dashboard")
    c1, _, c3 = st.columns([1,1,1])
    with c1:
        if st.button("Dashboard", key="usr_db"): st.rerun()
    with c3:
        if st.button("Logout", key="usr_lo"):
            _reset_sess(); st.rerun()

# ───────────────────────────────────────────────
#  12. PAGE: DEVELOPER
# ───────────────────────────────────────────────
def _page_dev():
    nav = st.session_state["subnav"]

    # Topbar: KAS KITA | Developer Panel | bell + avatar
    col_brand, col_right = st.columns([3, 1])
    with col_brand:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;padding-top:14px;">
            <div style="display:flex;flex-direction:column;line-height:1.05;">
                <span style="font-size:17px;font-weight:900;color:#09F289;
                             letter-spacing:.6px;">KAS</span>
                <span style="font-size:17px;font-weight:900;color:#09F289;
                             letter-spacing:.6px;">KITA</span>
            </div>
            <div style="width:1px;height:32px;background:#1C2060;margin:0 6px;">
            </div>
            <div>
                <div style="font-size:15px;font-weight:700;color:#FFFFFF;">
                    Developer</div>
                <div style="font-size:15px;font-weight:700;color:#FFFFFF;">
                    Panel</div>
            </div>
        </div>""", unsafe_allow_html=True)
    with col_right:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:8px;
                    justify-content:flex-end;padding-top:16px;">
            <span style="font-size:18px;">&#128276;</span>
            <div style="width:32px;height:32px;border-radius:50%;
                        background:#1C2060;display:flex;align-items:center;
                        justify-content:center;">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
                     stroke="#6B72B0" stroke-width="2"
                     stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                </svg>
            </div>
        </div>""", unsafe_allow_html=True)

    df_admin = db_read("SELECT * FROM admin_accounts")
    df_kas   = db_read("SELECT * FROM kas")

    if nav == "dashboard":
        st.markdown("""
        <h2 style="font-size:24px;font-weight:800;color:#FFFFFF;
                   margin:.5rem 0 .3rem;">Data Akun Admin</h2>
        <p style="font-size:13px;color:#6B72B0;margin:0 0 1.2rem;line-height:1.65;">
            Manage system administrators and monitor account statuses
            within the KAS KITA ecosystem.</p>
        """, unsafe_allow_html=True)

        # Admin table header
        st.markdown("""
        <div style="background:#080B2E;border:1px solid #1C2060;
                    border-radius:14px 14px 0 0;padding:.7rem 1rem;
                    display:grid;grid-template-columns:2fr 2fr;gap:.5rem;">
            <span style="font-size:10px;font-weight:700;color:#3D4499;
                         text-transform:uppercase;letter-spacing:.07em;">USERNAME</span>
            <span style="font-size:10px;font-weight:700;color:#3D4499;
                         text-transform:uppercase;letter-spacing:.07em;">EMAIL</span>
        </div>""", unsafe_allow_html=True)

        rows = ""
        for i, (_, row) in enumerate(df_admin.iterrows()):
            uname    = safe(row.get("username",""))
            email    = safe(row.get("email",""))
            initials = "".join(w[0].upper() for w in uname.split("_")[:2]) or "??"
            sep = ("" if i==len(df_admin)-1
                   else "border-bottom:1px solid #1C2060;")
            rows += f"""
            <div style="padding:.9rem 1rem;display:grid;
                        grid-template-columns:2fr 2fr;gap:.5rem;
                        align-items:center;{sep}">
                <div style="display:flex;align-items:center;gap:.7rem;">
                    <div style="width:36px;height:36px;background:#1A2460;
                                border-radius:10px;display:flex;
                                align-items:center;justify-content:center;
                                font-size:11px;font-weight:700;color:#09F289;
                                flex-shrink:0;">{initials}</div>
                    <span style="font-size:13px;font-weight:600;color:#FFFFFF;
                                 white-space:nowrap;overflow:hidden;
                                 text-overflow:ellipsis;">{uname}</span>
                </div>
                <div style="font-size:12px;color:#6B72B0;overflow:hidden;
                            text-overflow:ellipsis;white-space:nowrap;">
                    {email}</div>
            </div>"""

        st.markdown(f"""
        <div style="background:#0C1040;border:1px solid #1C2060;border-top:none;
                    border-radius:0 0 14px 14px;margin-bottom:1rem;">{rows}</div>
        """, unsafe_allow_html=True)

        # Stat cards
        total_adm = len(df_admin)
        for icon_path, lbl, val, icon_bg in [
            ("M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2 M23 21v-2a4 4 0 00-3-3.87 M16 3.13a4 4 0 010 7.75",
             "Total Admin", f"{total_adm} Active", "#0A1450"),
            ("M22 11.08V12a10 10 0 11-5.93-9.14 M22 4L12 14.01l-3-3",
             "New Requests", "03 Pending", "#0A1450"),
            ("M18 20V10 M12 20V4 M6 20v-6",
             "System Uptime", "99.9%", "#0A1450"),
        ]:
            st.markdown(f"""
            <div style="background:#0C1040;border:1px solid #1C2060;
                        border-radius:18px;padding:1rem 1.2rem;margin-bottom:.6rem;
                        display:flex;align-items:center;gap:1rem;">
                <div style="width:44px;height:44px;background:{icon_bg};
                            border-radius:12px;display:flex;align-items:center;
                            justify-content:center;flex-shrink:0;">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
                         stroke="#09F289" stroke-width="2"
                         stroke-linecap="round" stroke-linejoin="round">
                        <path d="{icon_path}"/>
                    </svg>
                </div>
                <div>
                    <div style="font-size:12px;color:#6B72B0;margin-bottom:2px;">
                        {lbl}</div>
                    <div style="font-size:18px;font-weight:800;color:#FFFFFF;">
                        {val}</div>
                </div>
            </div>""", unsafe_allow_html=True)

        # Hapus akun
        with st.expander("Hapus akun admin"):
            if df_admin.empty:
                st.info("Tidak ada akun.")
            else:
                did = st.number_input("ID akun", min_value=1, step=1,
                                      key="dev_del_id")
                if st.button("Hapus Akun", key="dev_del_btn"):
                    ok = db_write(
                        "DELETE FROM admin_accounts WHERE id=?", (int(did),)
                    )
                    if ok:
                        st.success(f"Akun ID {int(did)} dihapus.")
                        time.sleep(.4)
                        st.rerun()

    elif nav == "history":
        _sec("Semua Data Kas")
        if df_kas.empty:
            st.info("Belum ada data kas.")
        else:
            st.dataframe(df_kas, use_container_width=True, hide_index=True)
            pdf = gen_pdf(df_kas, "Semua Data Kas")
            if pdf:
                st.download_button("Download PDF", pdf, "kas_all.pdf",
                                   mime="application/pdf", key="dl_dev_h")

    _bottom_nav(nav)
    _nav_row("dev")

# ───────────────────────────────────────────────
#  13. ROUTER
# ───────────────────────────────────────────────
_PAGES  = {"role","login_admin","login_dev","admin","user","dev"}
_SECURE = {"admin","user","dev"}

def main():
    page = st.session_state.get("page","role")
    if page not in _PAGES:
        page = "role"
    if page in _SECURE and not st.session_state.get("login", False):
        page = "role"
    st.session_state["page"] = page

    {
        "role":        _page_role,
        "login_admin": _page_login_admin,
        "login_dev":   _page_login_dev,
        "admin":       _page_admin,
        "user":        _page_user,
        "dev":         _page_dev,
    }[page]()

if __name__ == "__main__":
    main()
