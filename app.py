# ============================================================
#  KAS KITA — Streamlit App (Fixed & Optimized)
#  Fixes: SQLite threading, session state, CSS, PDF, nav bugs
# ============================================================
import streamlit as st
import pandas as pd
import sqlite3
import io
import time
import traceback
from datetime import date
from contextlib import contextmanager

# ReportLab
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# ─────────────────────────────────────────────
#  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="KAS KITA",
    page_icon="💳",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  GLOBAL CSS
#  FIX: scoped selectors instead of broad
#  `h1,h2,...,div { color }` which broke
#  Streamlit's own widgets
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── base ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main { background: #03043D !important; }

/* ── hide streamlit chrome ── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebar"]
{ display:none !important; visibility:hidden !important; }

/* ── container ── */
.block-container {
    max-width: 480px !important;
    padding: 0 1rem 7rem !important;
    margin: 0 auto !important;
}

/* ── custom HTML elements only ── */
.kk-text  { color: #FFFFFF; }
.kk-muted { color: #7B82C4; }
.kk-green { color: #09F289; }

/* ── inputs ── */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTextArea textarea {
    background: #0A0E3A !important;
    border: 1.5px solid #1E2560 !important;
    border-radius: 12px !important;
    color: #FFFFFF !important;
    font-size: 14px !important;
}
.stTextInput input::placeholder,
.stTextArea textarea::placeholder { color: #4A5099 !important; }
.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: #09F289 !important;
    box-shadow: 0 0 0 2px rgba(9,242,137,.15) !important;
    outline: none !important;
}

/* ── selectbox ── */
.stSelectbox > div > div > div {
    background: #0A0E3A !important;
    border: 1.5px solid #1E2560 !important;
    border-radius: 12px !important;
    color: #FFFFFF !important;
}
.stSelectbox svg { fill: #09F289 !important; }

/* ── all labels ── */
.stTextInput label,
.stNumberInput label,
.stDateInput label,
.stSelectbox label,
.stTextArea label,
.stCheckbox label {
    color: #7B82C4 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: .06em !important;
    text-transform: uppercase !important;
}

/* ── buttons ── */
.stButton > button {
    width: 100% !important;
    background: #09F289 !important;
    color: #03043D !important;
    border: none !important;
    border-radius: 14px !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    padding: 13px 20px !important;
    letter-spacing: .5px !important;
    transition: opacity .15s !important;
}
.stButton > button:hover  { opacity: .86 !important; }
.stButton > button:active { opacity: .72 !important; }

/* secondary / back buttons */
[data-testid="baseButton-secondary"] {
    background: transparent !important;
    color: #09F289 !important;
    border: 1.5px solid #09F289 !important;
    border-radius: 12px !important;
}

/* ── download button ── */
.stDownloadButton > button {
    background: #09F289 !important;
    color: #03043D !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    width: 100% !important;
    padding: 11px 20px !important;
}

/* ── dataframe ── */
[data-testid="stDataFrame"] {
    background: #121A4D !important;
    border-radius: 14px !important;
    border: 1px solid #1E2560 !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] * { color: #FFFFFF !important; }

/* ── alerts ── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    font-size: 13px !important;
}
div[data-testid="stNotification"] { border-radius: 12px !important; }

/* ── expander ── */
.streamlit-expanderHeader {
    background: #121A4D !important;
    border: 1px solid #1E2560 !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
}
.streamlit-expanderContent {
    background: #0D1245 !important;
    border: 1px solid #1E2560 !important;
    border-radius: 0 0 10px 10px !important;
}

/* ── spinner ── */
[data-testid="stSpinner"] > div { border-top-color: #09F289 !important; }

/* ── scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #03043D; }
::-webkit-scrollbar-thumb { background: #1E2560; border-radius: 4px; }

/* ── date input calendar icon ── */
.stDateInput svg { fill: #7B82C4 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  DATABASE  — safe connection per-call
#  FIX: @st.cache_resource only caches the
#  DB path; each write gets a fresh cursor
#  to avoid "objects created in a thread can
#  only be used in that same thread" errors.
# ─────────────────────────────────────────────
DB_PATH = "kaskita.db"

@st.cache_resource
def get_db_path() -> str:
    """Bootstrap schema once; return path."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS kas (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nama      TEXT    NOT NULL,
            tanggal   TEXT    NOT NULL,
            status    TEXT    NOT NULL,
            kelas     TEXT    NOT NULL,
            jurusan   TEXT    NOT NULL,
            keterangan TEXT,
            nominal   INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS admin_accounts (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email    TEXT,
            kelas    TEXT,
            jurusan  TEXT
        );
        CREATE TABLE IF NOT EXISTS pengeluaran (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal    TEXT    NOT NULL,
            kelas      TEXT    NOT NULL,
            jurusan    TEXT    NOT NULL,
            keterangan TEXT,
            nominal    INTEGER NOT NULL DEFAULT 0
        );
    """)
    # seed dummy admins if table empty
    c.execute("SELECT COUNT(*) FROM admin_accounts")
    if c.fetchone()[0] == 0:
        c.executemany(
            "INSERT OR IGNORE INTO admin_accounts"
            "(username,password,email,kelas,jurusan) VALUES(?,?,?,?,?)",
            [
                ("admin_dhimas",   "pass", "dhimas.dev@kaskita.id",  "XII", "RPL"),
                ("sari_keuangan",  "pass", "sari.p@kaskita.id",      "XI",  "IPA"),
                ("rendy_bendahara","pass", "rendy.b@kaskita.id",     "X",   "IPS"),
                ("fauzan_monitor", "pass", "fauzan.m@kaskita.id",    "XII", "MIPA"),
            ]
        )
    conn.commit()
    conn.close()
    return DB_PATH


@contextmanager
def db_conn():
    """
    FIX: yield a fresh connection per operation.
    check_same_thread=False + WAL mode = safe for Streamlit.
    """
    path = get_db_path()
    conn = sqlite3.connect(path, check_same_thread=False)
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
    """Safe read → DataFrame."""
    with db_conn() as conn:
        try:
            df = pd.read_sql_query(sql, conn, params=params)
            return df
        except Exception as e:
            st.error(f"Database read error: {e}")
            return pd.DataFrame()


def db_write(sql: str, params: tuple = ()) -> bool:
    """Safe write → True on success."""
    with db_conn() as conn:
        try:
            conn.execute(sql, params)
            return True
        except Exception as e:
            st.error(f"Database write error: {e}")
            return False

# ─────────────────────────────────────────────
#  SESSION STATE — centralised init
#  FIX: explicit typed defaults prevent
#  KeyError / unexpected None bugs
# ─────────────────────────────────────────────
_DEFAULTS: dict = {
    "role":    None,
    "login":   False,
    "kelas":   "XII",
    "jurusan": "RPL",
    "page":    "role",
    "subnav":  "dashboard",
}

def init_session():
    for k, v in _DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v

def reset_session():
    """
    FIX: delete keys individually so
    st.session_state itself is not replaced
    (which can cause Streamlit widget key
    conflicts on next render).
    """
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    init_session()
    st.session_state["page"] = "role"

init_session()

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def fmt_rp(n) -> str:
    try:
        return "Rp {:,.0f}".format(int(n)).replace(",", ".")
    except (TypeError, ValueError):
        return "Rp 0"


def clean_nom(raw) -> int:
    """
    FIX: robust parser — handles None, empty,
    spaces, 'Rp', commas, dots.
    """
    if raw is None:
        return 0
    s = str(raw).strip().lower()
    s = s.replace("rp", "").replace(" ", "").replace(".", "").replace(",", "")
    return int(s) if s.isdigit() else 0


def sanitize_str(val) -> str:
    """Return empty string instead of None."""
    return str(val) if val is not None else ""


def gen_pdf(df: pd.DataFrame, title: str = "Laporan KasKita") -> bytes:
    """
    FIX:
    - Convert all cell values to str to avoid
      ReportLab crash on None / int / float.
    - Catch and re-raise with useful message.
    """
    try:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=A4,
            topMargin=40, bottomMargin=40,
            leftMargin=30, rightMargin=30,
        )
        styles = getSampleStyleSheet()
        elements = [
            Paragraph(f"<b>{title}</b>", styles["Title"]),
            Spacer(1, 12),
        ]

        # sanitise: convert everything to str
        safe_df = df.fillna("").astype(str)
        data = [list(safe_df.columns)] + safe_df.values.tolist()

        col_widths = [doc.width / len(safe_df.columns)] * len(safe_df.columns)
        t = Table(data, repeatRows=1, colWidths=col_widths)
        t.setStyle(TableStyle([
            ("BACKGROUND",     (0, 0), (-1, 0),  colors.HexColor("#03043D")),
            ("TEXTCOLOR",      (0, 0), (-1, 0),  colors.HexColor("#09F289")),
            ("FONTNAME",       (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",       (0, 0), (-1, 0),  9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.white, colors.HexColor("#F0F9FF")]),
            ("TEXTCOLOR",      (0, 1), (-1, -1),  colors.HexColor("#03043D")),
            ("FONTSIZE",       (0, 1), (-1, -1),  8),
            ("GRID",           (0, 0), (-1, -1), 0.4, colors.HexColor("#CCDDEE")),
            ("PADDING",        (0, 0), (-1, -1), 5),
            ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
            ("WORDWRAP",       (0, 0), (-1, -1), True),
        ]))
        elements.extend([t, Spacer(1, 16),
                         Paragraph("© KasKita 2026", styles["Normal"])])
        doc.build(elements)
        return buf.getvalue()
    except Exception as e:
        st.error(f"PDF generation failed: {e}")
        return b""

# ─────────────────────────────────────────────
#  REUSABLE UI COMPONENTS
# ─────────────────────────────────────────────
def topbar(subtitle: str = "", show_bell: bool = True):
    bell_html = '<span style="font-size:20px;line-height:1;">🔔</span>' if show_bell else ""
    sub_html  = (f'<div style="font-size:11px;color:#7B82C4;margin-top:1px;">'
                 f'{subtitle}</div>') if subtitle else ""
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
                padding:16px 0 10px;">
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:38px;height:38px;background:#09F289;border-radius:10px;
                        display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                <svg width="20" height="20" viewBox="0 0 22 22" fill="none">
                    <rect x="2" y="6" width="18" height="11" rx="2.5"
                          stroke="#03043D" stroke-width="1.8"/>
                    <path d="M2 9.5h18" stroke="#03043D" stroke-width="1.8"/>
                    <rect x="4.5" y="12" width="6" height="2" rx=".6" fill="#03043D"/>
                </svg>
            </div>
            <div>
                <div style="font-size:16px;font-weight:800;color:#09F289;
                            letter-spacing:.5px;line-height:1.1;">KASKITA</div>
                {sub_html}
            </div>
        </div>
        {bell_html}
    </div>
    """, unsafe_allow_html=True)


def kk_card(html: str, padding: str = "1.2rem 1.4rem",
            mb: str = "1rem", extra: str = ""):
    st.markdown(f"""
    <div style="background:#121A4D;border:1px solid #1E2560;border-radius:18px;
                padding:{padding};margin-bottom:{mb};{extra}">
        {html}
    </div>""", unsafe_allow_html=True)


def section_title(text: str, right_html: str = ""):
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
                margin:1.2rem 0 .6rem;">
        <span style="font-size:17px;font-weight:700;color:#FFFFFF;">{text}</span>
        {right_html}
    </div>""", unsafe_allow_html=True)


def bottom_nav_html(active: str = "dashboard"):
    """
    FIX: pure visual HTML nav.
    Real navigation is handled by Streamlit
    buttons BELOW (invisible via CSS trick).
    The HTML nav is decoration only.
    """
    items = [
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
    items_html = ""
    for key, path, label in items:
        is_active = active == key
        col = "#09F289" if is_active else "#4A5099"
        bg  = ("background:rgba(9,242,137,.12);border-radius:12px;padding:6px 18px;"
               if is_active else "padding:6px 18px;")
        items_html += f"""
        <div style="{bg}display:flex;flex-direction:column;align-items:center;gap:3px;">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
                 stroke="{col}" stroke-width="2"
                 stroke-linecap="round" stroke-linejoin="round">
                <path d="{path}"/>
            </svg>
            <span style="font-size:9px;font-weight:700;color:{col};
                         letter-spacing:.06em;">{label}</span>
        </div>"""

    st.markdown(f"""
    <div style="position:fixed;bottom:0;left:50%;transform:translateX(-50%);
                width:100%;max-width:480px;background:#03043D;
                border-top:1px solid #1E2560;padding:10px 24px;z-index:9000;
                display:flex;justify-content:space-around;align-items:center;">
        {items_html}
    </div>
    <style>
    /* make streamlit nav buttons invisible but still clickable */
    div[data-testid="stHorizontalBlock"] > div > div > .stButton > button {{
        opacity: 0 !important;
        height: 60px !important;
        margin-top: -70px !important;
        position: relative !important;
        z-index: 9999 !important;
        cursor: pointer !important;
    }}
    </style>
    """, unsafe_allow_html=True)


def nav_buttons(keys: list, labels: list, targets: list,
                active: str, logout_idx: int = 2):
    """Render invisible nav buttons above the bottom nav bar."""
    cols = st.columns(len(keys))
    for i, (col, key, label, target) in enumerate(zip(cols, keys, labels, targets)):
        with col:
            if st.button(label, key=key):
                if i == logout_idx:
                    reset_session()
                else:
                    st.session_state["subnav"] = target
                st.rerun()


# ─────────────────────────────────────────────
#  VALIDATION HELPERS
# ─────────────────────────────────────────────
def validate_nama(nama: str) -> str | None:
    """Return error string or None if valid."""
    if not nama or not nama.strip():
        return "Nama siswa tidak boleh kosong."
    if len(nama.strip()) < 2:
        return "Nama terlalu pendek (min 2 karakter)."
    return None


def validate_nominal(raw) -> str | None:
    val = clean_nom(raw)
    if val <= 0:
        return "Nominal harus lebih dari 0."
    if val > 100_000_000:
        return "Nominal terlalu besar."
    return None


# ─────────────────────────────────────────────
#  PAGE: ROLE SELECTION
# ─────────────────────────────────────────────
def page_role():
    st.markdown("""
    <div style="text-align:center;padding:2rem 0 1.5rem;">
        <div style="display:inline-flex;align-items:center;gap:10px;margin-bottom:1.5rem;">
            <div style="width:44px;height:44px;background:#09F289;border-radius:12px;
                        display:flex;align-items:center;justify-content:center;">
                <svg width="24" height="24" viewBox="0 0 22 22" fill="none">
                    <rect x="2" y="6" width="18" height="11" rx="2.5"
                          stroke="#03043D" stroke-width="1.8"/>
                    <path d="M2 9.5h18" stroke="#03043D" stroke-width="1.8"/>
                    <rect x="4.5" y="12" width="6" height="2" rx=".6" fill="#03043D"/>
                </svg>
            </div>
            <span style="font-size:22px;font-weight:900;color:#09F289;
                         letter-spacing:.5px;">KAS KITA</span>
        </div>
        <h1 style="font-size:27px;font-weight:800;color:#FFFFFF;
                   margin:0 0 .75rem;line-height:1.25;">
            Selamat Datang di<br>Kas Kita
        </h1>
        <p style="font-size:14px;color:#7B82C4;margin:0;line-height:1.7;">
            Tentukan peran Anda untuk mulai<br>
            mengelola ekosistem finansial digital yang cerdas.
        </p>
    </div>""", unsafe_allow_html=True)

    roles = [
        ("admin", "🛡️",  "#1A2260", "Admin",
         "Manajemen sistem penuh, kontrol otorisasi, dan audit laporan konsolidasi.",
         "1px solid #1E2560"),
        ("user",  "👤",  "#09F289", "User",
         "Akses personal untuk mencatat transaksi, memantau saldo, dan laporan individu.",
         "2px solid #09F289"),
        ("dev",   "⟨/⟩", "#1A2260", "Developer",
         "Integrasi API, kustomisasi teknis, dan pemeliharaan struktur basis data.",
         "1px solid #1E2560"),
    ]

    for key, icon, icon_bg, label, desc, border in roles:
        st.markdown(f"""
        <div style="background:#121A4D;border:{border};border-radius:20px;
                    padding:1.4rem 1.4rem .6rem;margin-bottom:.5rem;">
            <div style="width:52px;height:52px;background:{icon_bg};border-radius:14px;
                        display:flex;align-items:center;justify-content:center;
                        font-size:22px;margin-bottom:1rem;">{icon}</div>
            <div style="font-size:20px;font-weight:700;color:#FFFFFF;
                        margin-bottom:.4rem;">{label}</div>
            <div style="font-size:13px;color:#7B82C4;line-height:1.6;
                        margin-bottom:.75rem;">{desc}</div>
            <div style="font-size:11px;font-weight:700;color:#09F289;
                        letter-spacing:.06em;margin-bottom:.75rem;">
                PILIH ROLE &nbsp;→
            </div>
        </div>""", unsafe_allow_html=True)

        if st.button("PILIH ROLE", key=f"role_{key}"):
            if key == "admin":
                st.session_state["role"] = "admin"
                st.session_state["page"] = "login_admin"
            elif key == "user":
                st.session_state["role"] = "user"
                st.session_state["login"] = True
                st.session_state["page"] = "user"
            elif key == "dev":
                st.session_state["role"] = "dev"
                st.session_state["page"] = "login_dev"
            st.rerun()

    st.markdown("""
    <div style="text-align:center;margin-top:1.5rem;padding-bottom:1rem;">
        <span style="font-size:10px;color:#2D3580;letter-spacing:.12em;
                     text-transform:uppercase;">── ENKRIPSI VAULT 256-BIT ──</span>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE: LOGIN ADMIN
# ─────────────────────────────────────────────
def page_login_admin():
    topbar("Masuk sebagai Admin")
    st.markdown("""
    <div style="padding:.75rem 0 1.25rem;">
        <h2 style="font-size:23px;font-weight:800;color:#FFFFFF;margin:0 0 .3rem;">
            Login Admin</h2>
        <p style="font-size:13px;color:#7B82C4;margin:0;">
            Masukkan detail kelas untuk melanjutkan</p>
    </div>""", unsafe_allow_html=True)

    username = st.text_input("USERNAME", placeholder="Contoh: admin_dhimas",
                             key="la_user")
    st.text_input("PASSWORD", type="password", placeholder="••••••••",
                  key="la_pass")
    c1, c2 = st.columns(2)
    with c1:
        kelas = st.selectbox("KELAS", ["X", "XI", "XII"], index=2, key="la_kls")
    with c2:
        jurusan = st.text_input("JURUSAN", placeholder="RPL", key="la_jrs")

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    if st.button("MASUK KE DASHBOARD", key="la_submit"):
        err = None
        if not username.strip():
            err = "Username tidak boleh kosong."
        elif not jurusan.strip():
            err = "Jurusan tidak boleh kosong."
        if err:
            st.error(err)
        else:
            st.session_state["login"]   = True
            st.session_state["kelas"]   = kelas
            st.session_state["jurusan"] = jurusan.strip().upper()
            st.session_state["page"]    = "admin"
            st.session_state["subnav"]  = "dashboard"
            st.rerun()

    if st.button("← Kembali", key="la_back"):
        st.session_state["page"] = "role"
        st.rerun()


# ─────────────────────────────────────────────
#  PAGE: LOGIN DEVELOPER
# ─────────────────────────────────────────────
def page_login_dev():
    topbar("Developer Access")
    st.markdown("""
    <div style="padding:.75rem 0 1.25rem;">
        <h2 style="font-size:23px;font-weight:800;color:#FFFFFF;margin:0 0 .3rem;">
            Login Developer</h2>
        <p style="font-size:13px;color:#7B82C4;margin:0;">
            Kredensial akses sistem backend</p>
    </div>""", unsafe_allow_html=True)

    du = st.text_input("USERNAME", placeholder="username developer", key="ld_u")
    dp = st.text_input("PASSWORD", type="password", placeholder="••••••••",
                       key="ld_p")
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    if st.button("MASUK DEVELOPER PANEL", key="ld_submit"):
        # FIX: validate both fields before comparing
        if not du.strip() or not dp:
            st.error("Username dan password wajib diisi.")
        elif du.strip() == "admin" and dp == "12345":
            st.session_state["login"]  = True
            st.session_state["page"]   = "dev"
            st.session_state["subnav"] = "dashboard"
            st.rerun()
        else:
            st.error("Kredensial salah. Gunakan: username=admin, password=12345")

    if st.button("← Kembali", key="ld_back"):
        st.session_state["page"] = "role"
        st.rerun()


# ─────────────────────────────────────────────
#  PAGE: ADMIN DASHBOARD
# ─────────────────────────────────────────────
def page_admin():
    kls = st.session_state["kelas"]
    jrs = st.session_state["jurusan"]
    nav = st.session_state["subnav"]

    topbar("Admin Panel")
    st.markdown(f"""
    <div style="padding:.5rem 0 1rem;">
        <div style="font-size:22px;font-weight:800;color:#FFFFFF;">
            Halo, <span style="color:#09F289;">Admin</span>
        </div>
        <div style="font-size:13px;color:#7B82C4;margin-top:3px;">
            Status Keuangan Kelas:
            <span style="color:#09F289;font-weight:600;">{kls} {jrs}</span>
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Load data fresh every render ──
    df = db_read(
        "SELECT * FROM kas WHERE kelas=? AND jurusan=?",
        (kls, jrs)
    )
    if not df.empty:
        df["tanggal"] = pd.to_datetime(
            df["tanggal"], errors="coerce"
        ).dt.strftime("%Y-%m-%d")

    total_kas   = int(df["nominal"].sum())    if not df.empty else 0
    tepat_count = int((df["status"] == "Tepat Waktu").sum()) if not df.empty else 0
    telat_count = int((df["status"] == "Telat").sum())       if not df.empty else 0

    # ════════════════════════════════
    if nav == "dashboard":
        # Total Kas card
        kk_card(f"""
        <div style="font-size:10px;font-weight:700;color:#7B82C4;
                    letter-spacing:.08em;text-transform:uppercase;
                    margin-bottom:.5rem;">TOTAL KAS</div>
        <div style="font-size:28px;font-weight:800;color:#FFFFFF;
                    margin-bottom:.4rem;">{fmt_rp(total_kas)}</div>
        <div style="font-size:12px;color:#09F289;font-weight:600;">
            ↑ 12% dari bulan lalu</div>
        """)

        # ── Statistik Siswa ──
        section_title("Statistik Siswa")
        st.markdown("""
        <div style="background:#121A4D;border:1px solid #1E2560;
                    border-radius:18px;padding:1.2rem 1.4rem;margin-bottom:1rem;">
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:10px;font-weight:700;color:#7B82C4;
                    letter-spacing:.08em;text-transform:uppercase;
                    margin-bottom:.4rem;">PILIH SISWA</div>
        """, unsafe_allow_html=True)

        if df.empty:
            st.info("Belum ada data siswa. Tambahkan melalui form di bawah.")
        else:
            siswa_list = sorted(df["nama"].unique().tolist())
            siswa_sel  = st.selectbox("", siswa_list,
                                      label_visibility="collapsed",
                                      key="stat_siswa")
            ds  = df[df["nama"] == siswa_sel]
            tot = len(ds)
            tel = int((ds["status"] == "Telat").sum())
            tpt = tot - tel
            pct = int((tpt / tot) * 100) if tot > 0 else 0
            pct_bad = (tel / tot * 100) if tot > 0 else 0
            if pct_bad < 20:
                perf, perf_col = "PERFORMA SANGAT BAIK", "#09F289"
            elif pct_bad < 50:
                perf, perf_col = "PERLU PENINGKATAN", "#F5A623"
            else:
                perf, perf_col = "SERING TELAT", "#FF5050"

            # SVG circle: circumference = 2π×15.9 ≈ 99.9
            CIRC = 99.9
            dash_green = round(pct / 100 * CIRC, 1)
            dash_empty = round(CIRC - dash_green, 1)

            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:1.5rem;margin-top:.75rem;">
                <div style="position:relative;width:82px;height:82px;flex-shrink:0;">
                    <svg viewBox="0 0 36 36" width="82" height="82">
                        <circle cx="18" cy="18" r="15.9" fill="none"
                                stroke="#1E2560" stroke-width="3.2"/>
                        <circle cx="18" cy="18" r="15.9" fill="none"
                                stroke="#09F289" stroke-width="3.2"
                                stroke-dasharray="{dash_green} {dash_empty}"
                                stroke-dashoffset="25"
                                stroke-linecap="round"/>
                    </svg>
                    <div style="position:absolute;top:50%;left:50%;
                                transform:translate(-50%,-50%);
                                font-size:14px;font-weight:800;
                                color:#FFFFFF;">{pct}%</div>
                </div>
                <div>
                    <div style="display:flex;gap:1.2rem;margin-bottom:.5rem;">
                        <span style="font-size:12px;color:#7B82C4;">
                            TEPAT WAKTU:
                            <b style="color:#09F289;">{tpt}</b>
                        </span>
                        <span style="font-size:12px;color:#7B82C4;">
                            TELAT:
                            <b style="color:#FF5050;">{tel}</b>
                        </span>
                    </div>
                    <span style="background:rgba(9,242,137,.12);
                                 color:{perf_col};font-size:10px;
                                 font-weight:700;padding:4px 10px;
                                 border-radius:8px;letter-spacing:.04em;">
                        ● {perf}
                    </span>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # ── Input Pembayaran ──
        section_title("Input Pembayaran")
        with st.form("form_kas", clear_on_submit=True):
            st.markdown("""
            <div style="background:#0D1245;border:1px solid #1E2560;
                        border-radius:14px;padding:1rem 1.2rem;margin-bottom:.5rem;">
            """, unsafe_allow_html=True)
            nama    = st.text_input("NAMA SISWA",
                                    placeholder="Contoh: Ahmad Fauzan",
                                    key="f_nama")
            c1, c2  = st.columns(2)
            with c1:
                tgl    = st.date_input("TANGGAL", value=date.today(), key="f_tgl")
            with c2:
                status = st.selectbox("STATUS", ["Tepat Waktu", "Telat"],
                                      key="f_status")
            nominal = st.text_input("NOMINAL (RP)", placeholder="20000",
                                    key="f_nom")
            ket     = st.text_area("KETERANGAN",
                                   placeholder="Kas Minggu ke-2 Februari",
                                   key="f_ket", height=80)
            st.markdown("</div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Simpan Data")

        if submitted:
            err_nama = validate_nama(nama)
            err_nom  = validate_nominal(nominal)
            if err_nama:
                st.error(err_nama)
            elif err_nom:
                st.error(err_nom)
            else:
                ok = db_write(
                    "INSERT INTO kas(nama,tanggal,status,kelas,jurusan,keterangan,nominal)"
                    " VALUES(?,?,?,?,?,?,?)",
                    (nama.strip(), str(tgl), status, kls, jrs,
                     ket.strip(), clean_nom(nominal))
                )
                if ok:
                    st.success(f"✓ Data {nama.strip()} berhasil disimpan!")
                    time.sleep(0.4)
                    st.rerun()

        # ── Distribusi Status ──
        section_title("Distribusi Status Bayar")
        st.markdown(f"""
        <div style="background:#121A4D;border:1px solid #1E2560;border-radius:18px;
                    padding:1.4rem 1.8rem;margin-bottom:1rem;display:flex;gap:3rem;">
            <div style="text-align:center;">
                <div style="font-size:38px;font-weight:800;color:#09F289;">
                    {tepat_count}</div>
                <div style="font-size:10px;font-weight:700;color:#7B82C4;
                            letter-spacing:.06em;text-transform:uppercase;
                            margin-top:4px;">TEPAT WAKTU</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:38px;font-weight:800;color:#FF5050;">
                    {telat_count}</div>
                <div style="font-size:10px;font-weight:700;color:#7B82C4;
                            letter-spacing:.06em;text-transform:uppercase;
                            margin-top:4px;">TELAT</div>
            </div>
        </div>""", unsafe_allow_html=True)

        # ── Riwayat ──
        section_title(
            "Riwayat Data Kas",
            right_html='<span style="font-size:12px;color:#09F289;font-weight:700;">'
                       'LIHAT SEMUA</span>',
        )

        if df.empty:
            st.info("Belum ada data kas untuk kelas ini.")
        else:
            for _, row in df.tail(10).iloc[::-1].iterrows():
                s_col = "#09F289" if row["status"] == "Tepat Waktu" else "#FF5050"
                s_bg  = ("rgba(9,242,137,.12)" if row["status"] == "Tepat Waktu"
                         else "rgba(255,80,80,.12)")
                s_lbl = "TEPAT WAKTU" if row["status"] == "Tepat Waktu" else "TELAT"
                kk_card(f"""
                <div style="display:flex;align-items:flex-start;
                            justify-content:space-between;gap:.5rem;">
                    <div style="flex:1;min-width:0;">
                        <div style="font-size:14px;font-weight:700;color:#FFFFFF;
                                    white-space:nowrap;overflow:hidden;
                                    text-overflow:ellipsis;">
                            {sanitize_str(row["nama"])}</div>
                        <div style="font-size:11px;color:#7B82C4;margin-top:2px;">
                            {sanitize_str(row["keterangan"])}</div>
                        <div style="font-size:11px;color:#4A5099;margin-top:4px;">
                            {sanitize_str(row["tanggal"])}</div>
                    </div>
                    <div style="text-align:right;flex-shrink:0;">
                        <span style="background:{s_bg};color:{s_col};font-size:9px;
                                     font-weight:700;padding:3px 8px;
                                     border-radius:6px;">{s_lbl}</span>
                        <div style="font-size:14px;font-weight:700;color:#09F289;
                                    margin-top:6px;">
                            + {fmt_rp(row["nominal"])}
                        </div>
                    </div>
                </div>""", padding=".9rem 1.1rem", mb=".5rem")

            pdf_bytes = gen_pdf(df, f"Laporan Kas {kls} {jrs}")
            if pdf_bytes:
                st.download_button(
                    "⬇ Download PDF Kas",
                    data=pdf_bytes,
                    file_name=f"kas_{kls}_{jrs}.pdf",
                    mime="application/pdf",
                    key="dl_kas",
                )

    # ════════════════════════════════
    elif nav == "history":
        section_title("Riwayat Lengkap")
        if df.empty:
            st.info("Belum ada data.")
        else:
            df_show = df.copy()
            df_show["nominal"] = df_show["nominal"].apply(fmt_rp)
            st.dataframe(df_show, use_container_width=True, hide_index=True)
            pdf_bytes = gen_pdf(df, f"Riwayat Kas {kls} {jrs}")
            if pdf_bytes:
                st.download_button(
                    "⬇ Download PDF",
                    data=pdf_bytes,
                    file_name=f"riwayat_{kls}_{jrs}.pdf",
                    mime="application/pdf",
                    key="dl_hist",
                )

    # ── Bottom nav ──
    bottom_nav_html(nav)
    nav_buttons(
        keys    = ["adm_nav_db", "adm_nav_hs", "adm_nav_lo"],
        labels  = ["Dashboard",  "History",    "Logout"],
        targets = ["dashboard",  "history",    ""],
        active  = nav,
        logout_idx=2,
    )


# ─────────────────────────────────────────────
#  PAGE: USER
# ─────────────────────────────────────────────
def page_user():
    topbar()
    st.markdown("""
    <div style="padding:.5rem 0 1rem;">
        <h2 style="font-size:22px;font-weight:800;color:#FFFFFF;margin:0 0 .3rem;">
            Riwayat Data Kas</h2>
        <p style="font-size:13px;color:#7B82C4;margin:0;">
            Cari data kas berdasarkan kelas dan bulan</p>
    </div>""", unsafe_allow_html=True)

    df_all = db_read("SELECT * FROM kas")

    if df_all.empty:
        st.info("Belum ada data kas tersedia.")
        if st.button("Logout", key="usr_lo_empty"):
            reset_session()
            st.rerun()
        return

    # FIX: compute bulan_label safely
    df_all["bulan_label"] = pd.to_datetime(
        df_all["tanggal"], errors="coerce"
    ).dt.strftime("%B %Y").fillna("Unknown")

    # ── Filters ──
    st.markdown("""
    <div style="background:#121A4D;border:1px solid #1E2560;border-radius:18px;
                padding:1.2rem 1.4rem;margin-bottom:1rem;">
    """, unsafe_allow_html=True)

    jurusan_opts = ["Semua"] + sorted(df_all["jurusan"].dropna().unique().tolist())
    kelas_opts   = ["Semua"] + sorted(df_all["kelas"].dropna().unique().tolist())
    bulan_opts   = ["Semua"] + sorted(df_all["bulan_label"].dropna().unique().tolist())

    fj = st.selectbox("PILIH JURUSAN", jurusan_opts, key="uf_jrs")
    fk = st.selectbox("PILIH KELAS",   kelas_opts,   key="uf_kls")
    fb = st.selectbox("PILIH BULAN",   bulan_opts,   key="uf_bln")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🔍  CEK SEKARANG", key="usr_cek"):
        df_f = df_all.copy()
        if fj != "Semua": df_f = df_f[df_f["jurusan"] == fj]
        if fk != "Semua": df_f = df_f[df_f["kelas"] == fk]
        if fb != "Semua": df_f = df_f[df_f["bulan_label"] == fb]
        # FIX: store as records (list of dicts) — avoids int-key bug
        st.session_state["user_filter_result"] = df_f.to_dict(orient="records")

    # Retrieve filter result
    if "user_filter_result" in st.session_state:
        recs = st.session_state["user_filter_result"]
        df_show = pd.DataFrame(recs) if recs else pd.DataFrame()
    else:
        df_show = df_all.copy()

    if "bulan_label" in df_show.columns:
        df_show = df_show.drop(columns=["bulan_label"])

    if not df_show.empty:
        df_show["tanggal"] = pd.to_datetime(
            df_show["tanggal"], errors="coerce"
        ).dt.strftime("%d %b %Y").fillna("")

    section_title(
        "Riwayat Data Kas",
        right_html='<span style="font-size:12px;color:#09F289;font-weight:700;">'
                   'LIHAT SEMUA</span>',
    )

    # Table header
    st.markdown("""
    <div style="background:#0A0E3A;border:1px solid #1E2560;
                border-radius:14px 14px 0 0;padding:.7rem 1rem;
                display:grid;grid-template-columns:2fr 1.2fr 1.2fr 1fr;gap:.5rem;">
        <span style="font-size:10px;font-weight:700;color:#4A5099;
                     text-transform:uppercase;letter-spacing:.06em;">NAMA SISWA</span>
        <span style="font-size:10px;font-weight:700;color:#4A5099;
                     text-transform:uppercase;letter-spacing:.06em;">TANGGAL</span>
        <span style="font-size:10px;font-weight:700;color:#4A5099;
                     text-transform:uppercase;letter-spacing:.06em;">STATUS</span>
        <span style="font-size:10px;font-weight:700;color:#4A5099;
                     text-transform:uppercase;letter-spacing:.06em;">NOMINAL</span>
    </div>""", unsafe_allow_html=True)

    if df_show.empty:
        st.info("Tidak ada data untuk filter ini.")
    else:
        rows_html = ""
        for i, (_, row) in enumerate(df_show.head(20).iterrows()):
            is_tepat  = str(row.get("status", "")) == "Tepat Waktu"
            s_col     = "#09F289" if is_tepat else "#FF5050"
            s_bg      = "rgba(9,242,137,.12)" if is_tepat else "rgba(255,80,80,.12)"
            s_lbl     = "BERHASIL" if is_tepat else "PENDING"
            nom_col   = "#09F289" if is_tepat else "#FFFFFF"
            prefix    = "+" if is_tepat else ""
            border_b  = ("" if i == len(df_show.head(20)) - 1
                         else "border-bottom:1px solid #1E2560;")
            try:
                nom_k = int(row.get("nominal", 0)) // 1000
            except (ValueError, TypeError):
                nom_k = 0

            rows_html += f"""
            <div style="padding:.85rem 1rem;display:grid;
                        grid-template-columns:2fr 1.2fr 1.2fr 1fr;
                        gap:.5rem;align-items:center;{border_b}">
                <div>
                    <div style="font-size:13px;font-weight:600;color:#FFFFFF;
                                white-space:nowrap;overflow:hidden;
                                text-overflow:ellipsis;">
                        {sanitize_str(row.get("nama",""))}</div>
                    <div style="font-size:10px;color:#4A5099;margin-top:2px;">
                        {sanitize_str(row.get("kelas",""))}
                        {sanitize_str(row.get("jurusan",""))}</div>
                </div>
                <div style="font-size:11px;color:#7B82C4;">
                    {sanitize_str(row.get("tanggal",""))}</div>
                <div>
                    <span style="background:{s_bg};color:{s_col};font-size:9px;
                                 font-weight:700;padding:3px 8px;
                                 border-radius:6px;">{s_lbl}</span>
                </div>
                <div style="font-size:12px;font-weight:700;color:{nom_col};">
                    {prefix}{nom_k}k</div>
            </div>"""

        st.markdown(f"""
        <div style="background:#121A4D;border:1px solid #1E2560;border-top:none;
                    border-radius:0 0 14px 14px;margin-bottom:1rem;">
            {rows_html}
        </div>""", unsafe_allow_html=True)

        pdf_bytes = gen_pdf(df_show, "Laporan Kas User")
        if pdf_bytes:
            st.download_button(
                "⬇ Download PDF",
                data=pdf_bytes,
                file_name="kas_user.pdf",
                mime="application/pdf",
                key="dl_user",
            )

    bottom_nav_html("dashboard")
    c1, _, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("Dashboard", key="usr_db"):
            st.rerun()
    with c3:
        if st.button("Logout", key="usr_lo"):
            reset_session()
            st.rerun()


# ─────────────────────────────────────────────
#  PAGE: DEVELOPER PANEL
# ─────────────────────────────────────────────
def page_dev():
    nav = st.session_state["subnav"]

    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:space-between;
                padding:16px 0 10px;">
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:38px;height:38px;background:#09F289;border-radius:10px;
                        display:flex;align-items:center;justify-content:center;">
                <svg width="20" height="20" viewBox="0 0 22 22" fill="none">
                    <rect x="2" y="6" width="18" height="11" rx="2.5"
                          stroke="#03043D" stroke-width="1.8"/>
                    <path d="M2 9.5h18" stroke="#03043D" stroke-width="1.8"/>
                    <rect x="4.5" y="12" width="6" height="2" rx=".6"
                          fill="#03043D"/>
                </svg>
            </div>
            <div>
                <div style="font-size:14px;font-weight:800;color:#09F289;">
                    KAS KITA</div>
                <div style="font-size:10px;color:#7B82C4;">Developer Panel</div>
            </div>
        </div>
        <div style="display:flex;align-items:center;gap:10px;">
            <span style="font-size:18px;">🔔</span>
            <div style="width:34px;height:34px;border-radius:50%;
                        background:#1E2560;display:flex;align-items:center;
                        justify-content:center;font-size:16px;">👨‍💻</div>
        </div>
    </div>""", unsafe_allow_html=True)

    df_admin = db_read("SELECT * FROM admin_accounts")
    df_kas   = db_read("SELECT * FROM kas")

    if nav == "dashboard":
        st.markdown("""
        <h2 style="font-size:23px;font-weight:800;color:#FFFFFF;
                   margin:.5rem 0 .3rem;">Data Akun Admin</h2>
        <p style="font-size:13px;color:#7B82C4;margin:0 0 1.2rem;line-height:1.6;">
            Manage system administrators and monitor account statuses
            within the KAS KITA ecosystem.
        </p>""", unsafe_allow_html=True)

        # Table header
        st.markdown("""
        <div style="background:#0A0E3A;border:1px solid #1E2560;
                    border-radius:14px 14px 0 0;padding:.7rem 1rem;
                    display:grid;grid-template-columns:2fr 2fr;gap:.5rem;">
            <span style="font-size:10px;font-weight:700;color:#4A5099;
                         text-transform:uppercase;letter-spacing:.06em;">USERNAME</span>
            <span style="font-size:10px;font-weight:700;color:#4A5099;
                         text-transform:uppercase;letter-spacing:.06em;">EMAIL</span>
        </div>""", unsafe_allow_html=True)

        rows_html = ""
        for i, (_, row) in enumerate(df_admin.iterrows()):
            uname    = sanitize_str(row.get("username", ""))
            email    = sanitize_str(row.get("email", ""))
            initials = "".join(
                w[0].upper() for w in uname.split("_")[:2]
            ) or "??"
            border_b = ("" if i == len(df_admin) - 1
                        else "border-bottom:1px solid #1E2560;")
            rows_html += f"""
            <div style="padding:.9rem 1rem;display:grid;
                        grid-template-columns:2fr 2fr;gap:.5rem;
                        align-items:center;{border_b}">
                <div style="display:flex;align-items:center;gap:.7rem;">
                    <div style="width:36px;height:36px;background:#1A2260;
                                border-radius:10px;display:flex;
                                align-items:center;justify-content:center;
                                font-size:11px;font-weight:700;color:#09F289;
                                flex-shrink:0;">{initials}</div>
                    <span style="font-size:13px;font-weight:600;color:#FFFFFF;
                                 white-space:nowrap;overflow:hidden;
                                 text-overflow:ellipsis;">{uname}</span>
                </div>
                <div style="font-size:12px;color:#7B82C4;overflow:hidden;
                            text-overflow:ellipsis;white-space:nowrap;">
                    {email}</div>
            </div>"""

        st.markdown(f"""
        <div style="background:#121A4D;border:1px solid #1E2560;
                    border-top:none;border-radius:0 0 14px 14px;
                    margin-bottom:1rem;">{rows_html}</div>
        """, unsafe_allow_html=True)

        # Stat cards
        total_admin = len(df_admin)
        for icon, lbl, val in [
            ("👥", "Total Admin",   f"{total_admin} Active"),
            ("🛡️", "New Requests", "03 Pending"),
            ("📊", "System Uptime","99.9%"),
        ]:
            kk_card(f"""
            <div style="display:flex;align-items:center;gap:1rem;">
                <div style="width:44px;height:44px;background:#0A1A50;
                            border-radius:12px;display:flex;
                            align-items:center;justify-content:center;
                            font-size:20px;flex-shrink:0;">{icon}</div>
                <div>
                    <div style="font-size:12px;color:#7B82C4;margin-bottom:2px;">
                        {lbl}</div>
                    <div style="font-size:18px;font-weight:800;color:#FFFFFF;">
                        {val}</div>
                </div>
            </div>""", mb=".6rem")

        # Delete admin
        with st.expander("🗑️ Hapus akun admin"):
            if df_admin.empty:
                st.info("Tidak ada akun admin.")
            else:
                del_id = st.number_input("ID akun yang akan dihapus",
                                         min_value=1, step=1, key="del_adm_id")
                if st.button("Hapus Akun", key="btn_del_adm"):
                    ok = db_write(
                        "DELETE FROM admin_accounts WHERE id=?", (int(del_id),)
                    )
                    if ok:
                        st.success(f"Akun ID {int(del_id)} berhasil dihapus.")
                        time.sleep(0.4)
                        st.rerun()

    elif nav == "history":
        section_title("Semua Data Kas")
        if df_kas.empty:
            st.info("Belum ada data kas.")
        else:
            st.dataframe(df_kas, use_container_width=True, hide_index=True)
            pdf_bytes = gen_pdf(df_kas, "Semua Data Kas")
            if pdf_bytes:
                st.download_button(
                    "⬇ Download PDF",
                    data=pdf_bytes,
                    file_name="kas_all.pdf",
                    mime="application/pdf",
                    key="dl_dev_hist",
                )

    bottom_nav_html(nav)
    nav_buttons(
        keys    = ["dev_nav_db", "dev_nav_hs", "dev_nav_lo"],
        labels  = ["Dashboard",  "History",    "Logout"],
        targets = ["dashboard",  "history",    ""],
        active  = nav,
        logout_idx=2,
    )


# ─────────────────────────────────────────────
#  ROUTER
#  FIX: guard against invalid page values
# ─────────────────────────────────────────────
VALID_PAGES = {"role", "login_admin", "login_dev", "admin", "user", "dev"}

def main():
    page = st.session_state.get("page", "role")
    if page not in VALID_PAGES:
        st.session_state["page"] = "role"
        page = "role"

    # Auth guard: if page needs login but user is not logged in → role
    protected = {"admin", "user", "dev"}
    if page in protected and not st.session_state.get("login", False):
        st.session_state["page"] = "role"
        page = "role"

    dispatch = {
        "role":        page_role,
        "login_admin": page_login_admin,
        "login_dev":   page_login_dev,
        "admin":       page_admin,
        "user":        page_user,
        "dev":         page_dev,
    }
    dispatch[page]()


if __name__ == "__main__":
    main()
