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
# CUSTOM CSS — Navy #01023B + Font #2A223B (Sidebar)
# ======================
st.markdown("""
<style>
/* ── Global ── */
[data-testid="stAppViewContainer"] {
    background: #F3FDF9;
}
[data-testid="stSidebar"] {
    background: #01023B !important;
    border-right: none;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0.75rem;
}

/* ── Hide chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Sidebar text overrides ── */
section[data-testid="stSidebar"] * {
    color: #2A223B !important; /* Font Utama Sidebar */
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #FFFFFF !important; /* Header tetap putih agar kontras */
}
section[data-testid="stSidebar"] label {
    color: #2A223B !important; 
    font-size: 12px !important;
    font-weight: 600 !important;
}

/* ── Sidebar Inputs (Selectbox, Text Input) ── */
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255, 255, 255, 0.9) !important; /* Background agak terang agar font gelap terlihat */
    border-color: rgba(9,242,137,0.2) !important;
    color: #2A223B !important;
}
section[data-testid="stSidebar"] input {
    background: rgba(255, 255, 255, 0.9) !important;
    border-color: rgba(9,242,137,0.2) !important;
    color: #2A223B !important;
}

/* ── Sidebar buttons ── */
section[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    text-align: left;
    border: none !important;
    background: rgba(255, 255, 255, 0.1) !important;
    color: #2A223B !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    font-size: 13px !important;
    margin-bottom: 2px;
    transition: all 0.15s;
    font-weight: 500;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #09F289 !important;
    color: #01023B !important;
}

/* ── Main area buttons ── */
div:not(section[data-testid="stSidebar"]) .stButton > button {
    border-radius: 8px !important;
    border: 1px solid #D1FAE5 !important;
    background: #FFFFFF !important;
    color: #01023B !important;
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
    color: #01023B !important;
    border: none !important;
    font-weight: 500 !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #D1FAE5;
    border-radius: 12px;
    padding: 1rem 1.25rem !important;
}
[data-testid="stMetricValue"] {
    font-size: 22px !important;
    font-weight: 500 !important;
    color: #01023B !important;
}

/* ── Radio (sidebar) ── */
section[data-testid="stSidebar"] .stRadio > label {
    color: #2A223B !important;
}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #2A223B !important;
}

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.1) !important; }
</style>
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
        ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor("#01023B")),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.HexColor("#09F289")),
        ("FONTSIZE",      (0, 0), (-1, 0),  10),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, colors.HexColor("#F3FDF9")]),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#D1FAE5")),
        ("FONTSIZE",      (0, 1), (-1, -1), 9),
        ("PADDING",       (0, 0), (-1, -1), 6),
        ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
        ("TEXTCOLOR",     (0, 1), (-1, -1), colors.HexColor("#01023B")),
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
                <rect x="2" y="6" width="18" height="11" rx="2.5" stroke="#01023B" stroke-width="1.7"/>
                <path d="M2 9.5h18" stroke="#01023B" stroke-width="1.7"/>
                <rect x="4.5" y="12" width="6" height="2" rx="0.6" fill="#01023B"/>
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
    <div style="background:rgba(255,255,255,0.9);border:1px solid rgba(9,242,137,0.22);
                border-radius:8px;padding:8px 10px;margin-bottom:1rem;">
        <div style="font-size:10px;color:#01023B;font-weight:700;letter-spacing:.04em;">SESI AKTIF</div>
        <div style="font-size:12px;color:#2A223B;margin-top:2px;font-weight:500;">
            Kelas {kls} &nbsp;·&nbsp; {jrs}
        </div>
    </div>
    """, unsafe_allow_html=True)

def sidebar_label(text):
    st.markdown(f"""
    <div style="font-size:10px;color:#2A223B;text-transform:uppercase;
                letter-spacing:.06em;padding:8px 4px 4px;font-weight:700;opacity:0.8;">{text}</div>
    """, unsafe_allow_html=True)

def sidebar_sep():
    st.markdown(
        '<div style="height:1px;background:rgba(255,255,255,0.1);margin:6px 0;"></div>',
        unsafe_allow_html=True
    )

def sidebar_user(label):
    initial = label[0].upper() if label else "U"
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.9);border-radius:8px;
                padding:8px 10px;display:flex;align-items:center;gap:8px;">
        <div style="width:26px;height:26px;border-radius:50%;background:#09F289;
                    display:flex;align-items:center;justify-content:center;
                    font-size:10px;color:#01023B;font-weight:700;flex-shrink:0;">{initial}</div>
        <div style="font-size:11px;color:#2A223B;font-weight:600;">{label}</div>
    </div>
    """, unsafe_allow_html=True)

def info_badge_sidebar(text, color="#01023B", bg="#09F289"):
    st.markdown(f"""
    <div style="display:inline-block;background:{bg};color:{color};
                font-size:11px;padding:3px 10px;border-radius:20px;
                font-weight:700;margin-bottom:0.5rem;">{text}</div>
    """, unsafe_allow_html=True)

def page_header(title, subtitle=None):
    st.markdown(
        f"<h2 style='font-size:20px;font-weight:500;color:#01023B;margin:0;'>{title}</h2>",
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
            <div style="width:48px;height:48px;background:#01023B;border-radius:12px;
                        display:flex;align-items:center;justify-content:center;">
                <svg width="26" height="26" viewBox="0 0 22 22" fill="none">
                    <rect x="2" y="6" width="18" height="11" rx="2.5" stroke="#09F289" stroke-width="1.7"/>
                    <path d="M2 9.5h18" stroke="#09F289" stroke-width="1.7"/>
                    <rect x="4.5" y="12" width="6" height="2" rx="0.6" fill="#09F289"/>
                </svg>
            </div>
            <div style="text-align:left;">
                <div style="font-size:28px;font-weight:700;color:#01023B;line-height:1.1;">KasKita</div>
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
                    <circle cx="12" cy="8" r="4" stroke="#01023B" stroke-width="1.6"/>
                    <path d="M4 20c0-4 3.582-7 8-7s8 3 8 7" stroke="#01023B"
                          stroke-width="1.6" stroke-linecap="round"/>
                </svg>
            </div>
            <div style="font-size:15px;font-weight:500;color:#01023B;">Admin</div>
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
                    <path d="M4 6h16M4 10h16M4 14h10" stroke="#01023B"
                          stroke-width="1.6" stroke-linecap="round"/>
                </svg>
            </div>
            <div style="font-size:15px;font-weight:500;color:#01023B;">User</div>
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

# ======================
# VIEW: LOGIN ADMIN
# ======================
elif not st.session_state.login and st.session_state.page == "login":

    st.markdown("""
    <div style="text-align:center;padding:2rem 0 1.5rem;">
        <div style="font-size:22px;font-weight:600;color:#01023B;">Login Admin</div>
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

        if st.button("Masuk ke Dashboard →", type="primary", use_container_width=True):
            if not jurusan.strip():
                st.warning("Jurusan tidak boleh kosong.")
            else:
                st.session_state.login   = True
                st.session_state.kelas   = kelas
                st.session_state.jurusan = jurusan.upper()
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("← Kembali pilih role", use_container_width=True):
            st.session_state.page = "role"
            st.rerun()

# ======================
# MAIN APP
# ======================
else:
    if st.session_state.role == "user":
        with st.sidebar:
            render_logo_sidebar()
            info_badge_sidebar("Mode Publik")
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
            if st.button("Keluar", use_container_width=True):
                st.session_state.clear()
                st.rerun()

        page_header("Data kas kelas", "Lihat rekap pembayaran kas")

        if df_all.empty:
            st.info("Belum ada data kas yang tersedia.")
        else:
            df = df_all[
                (df_all["kelas"] == fk) &
                (df_all["jurusan"] == fj) &
                (df_all["bulan"] == fb)
            ].copy()
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Total kas", format_rupiah(df["nominal"].sum()))
            m2.metric("Jumlah transaksi", f"{len(df)}")
            m3.metric("Pembayaran telat", f"{len(df[df['status']=='Telat'])} siswa")

            tab1, tab2 = st.tabs(["📋  Tabel data", "📊  Statistik"])
            with tab1:
                st.dataframe(df.drop(columns=["bulan"], errors="ignore"), use_container_width=True, hide_index=True)
            with tab2:
                st.bar_chart(df["status"].value_counts())

    elif st.session_state.role == "admin":
        kls = st.session_state.kelas
        jrs = st.session_state.jurusan

        with st.sidebar:
            render_logo_sidebar()
            render_class_chip(kls, jrs)
            sidebar_label("Navigasi")

            if st.button("📊  Dashboard", use_container_width=True):
                st.session_state.menu = "dashboard"
                st.rerun()
            if st.button("💸  Pengeluaran", use_container_width=True):
                st.session_state.menu = "pengeluaran"
                st.rerun()

            sidebar_sep()
            sidebar_user(f"Admin · {jrs}")
            if st.button("Keluar", use_container_width=True):
                st.session_state.clear()
                st.rerun()

        df = pd.read_sql("SELECT * FROM kas WHERE kelas=? AND jurusan=?", conn, params=(kls, jrs))
        
        if st.session_state.menu == "dashboard":
            page_header("Dashboard kas", f"Kelas {kls} · {jrs}")
            
            with st.expander("➕  Input pembayaran baru"):
                c1, c2 = st.columns(2)
                with c1:
                    nama = st.text_input("Nama siswa")
                    status = st.selectbox("Status", ["Tepat Waktu", "Telat"])
                with c2:
                    tgl = st.date_input("Tanggal")
                    nom = st.text_input("Nominal")
                
                if st.button("Simpan pembayaran", type="primary"):
                    cursor.execute("INSERT INTO kas VALUES (NULL,?,?,?,?,?,?,?)",
                                   (nama, tgl.strftime("%Y-%m-%d"), status, kls, jrs, "", clean_nominal(nom)))
                    conn.commit()
                    st.success("Berhasil disimpan!")
                    st.rerun()

            if not df.empty:
                st.dataframe(df, use_container_width=True, hide_index=True)
