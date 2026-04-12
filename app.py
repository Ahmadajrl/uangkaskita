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
# CUSTOM CSS
# ======================
st.markdown("""
<style>
/* ---- Global ---- */
[data-testid="stAppViewContainer"] { background: #F8F7F5; }
[data-testid="stSidebar"] {
    background: #01023B;
    border-right: 1px solid #E8E7E0;
}
[data-testid="stSidebar"] > div { padding-top: 1rem; }

/* ---- Hide default header & footer ---- */
#MainMenu, footer, header { visibility: hidden; }

/* ---- Metric cards ---- */
[data-testid="stMetric"] {
    background: #01023B;
    border: 1px solid #EDECEA;
    border-radius: 12px;
    padding: 1rem 1.25rem;
}
[data-testid="stMetric"] label {
    font-size: 12px !important;
    color: #888780 !important;
    font-weight: 400 !important;
}
[data-testid="stMetricValue"] {
    font-size: 22px !important;
    font-weight: 500 !important;
    color: #1A1A1A !important;
}

/* ---- Buttons ---- */
.stButton > button {
    border-radius: 8px;
    border: 1px solid #D5D3CC;
    background: #FFFFFF;
    color: #3A3A3A;
    font-weight: 400;
    font-size: 13px;
    padding: 6px 14px;
    transition: all 0.15s;
}
.stButton > button:hover {
    background: #F1EFE8;
    border-color: #B4B2A9;
}

/* ---- Primary button (via class trick) ---- */
div[data-testid="column"] .stButton > button[kind="primary"],
.stButton > button[kind="primary"] {
    background: #534AB7 !important;
    color: #EEEDFE !important;
    border: none !important;
}
.stButton > button[kind="primary"]:hover {
    background: #3C3489 !important;
}

/* ---- Sidebar nav buttons ---- */
section[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    text-align: left;
    border: none;
    background: transparent;
    color: #5F5E5A;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    margin-bottom: 2px;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #F1EFE8;
    color: #2C2C2A;
}

/* ---- Inputs ---- */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stDateInput > div > div > input,
.stNumberInput > div > div > input {
    border-radius: 8px !important;
    border: 1px solid #D5D3CC !important;
    background: #FAFAF8 !important;
    font-size: 13px !important;
}
.stTextInput > div > div > input:focus,
.stSelectbox > div > div:focus-within {
    border-color: #534AB7 !important;
    box-shadow: 0 0 0 2px #EEEDFE !important;
}

/* ---- Dataframe ---- */
[data-testid="stDataFrame"] {
    border: 1px solid #EDECEA;
    border-radius: 10px;
    overflow: hidden;
}

/* ---- Expander ---- */
.streamlit-expanderHeader {
    background: #FFFFFF !important;
    border: 1px solid #EDECEA !important;
    border-radius: 10px !important;
    font-size: 13px !important;
    color: #3A3A3A !important;
}

/* ---- Divider ---- */
hr { border-color: #EDECEA; margin: 0.75rem 0; }

/* ---- Alerts ---- */
.stSuccess, .stWarning, .stError {
    border-radius: 10px !important;
    font-size: 13px !important;
}

/* ---- Tabs ---- */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid #EDECEA;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    font-size: 13px;
    color: #888780;
    border-bottom: 2px solid transparent;
    background: transparent;
    padding: 8px 16px;
}
.stTabs [aria-selected="true"] {
    color: #534AB7 !important;
    border-bottom: 2px solid #534AB7 !important;
    background: transparent !important;
    font-weight: 500;
}

/* ---- Bar chart ---- */
[data-testid="stVegaLiteChart"] {
    border: 1px solid #EDECEA;
    border-radius: 10px;
    padding: 0.5rem;
    background: #FFFFFF;
}

/* ---- Sidebar section label ---- */
.sidebar-section {
    font-size: 11px;
    color: #B4B2A9;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 12px 12px 4px;
    font-weight: 500;
}
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
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#534AB7")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F7F5")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#EDECEA")),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
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
    "kelas": None, "jurusan": None,
    "page": "role", "menu": "dashboard"
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ======================
# LOGO / BRAND (sidebar & top)
# ======================
def render_logo(size="large"):
    if size == "large":
        st.markdown("""
        <div style="text-align:center; padding: 1rem 0 0.5rem;">
            <div style="display:inline-flex; align-items:center; gap:10px;">
                <div style="width:40px; height:40px; background:#534AB7; border-radius:10px;
                            display:flex; align-items:center; justify-content:center;">
                    <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
                        <rect x="2" y="6" width="18" height="11" rx="2.5" stroke="#EEEDFE" stroke-width="1.6"/>
                        <path d="M2 9.5h18" stroke="#EEEDFE" stroke-width="1.6"/>
                        <rect x="4.5" y="12" width="6" height="2" rx="0.6" fill="#EEEDFE"/>
                    </svg>
                </div>
                <div style="text-align:left;">
                    <div style="font-size:20px; font-weight:600; color:#1A1A1A; line-height:1.1;">KasKita</div>
                    <div style="font-size:11px; color:#888780;">Manajemen kas kelas</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="display:flex; align-items:center; gap:8px; padding: 0.25rem 0 1rem;">
            <div style="width:30px; height:30px; background:#534AB7; border-radius:8px;
                        display:flex; align-items:center; justify-content:center; flex-shrink:0;">
                <svg width="17" height="17" viewBox="0 0 22 22" fill="none">
                    <rect x="2" y="6" width="18" height="11" rx="2.5" stroke="#EEEDFE" stroke-width="1.6"/>
                    <path d="M2 9.5h18" stroke="#EEEDFE" stroke-width="1.6"/>
                    <rect x="4.5" y="12" width="6" height="2" rx="0.6" fill="#EEEDFE"/>
                </svg>
            </div>
            <div>
                <div style="font-size:15px; font-weight:600; color:#1A1A1A; line-height:1.1;">KasKita</div>
                <div style="font-size:10px; color:#888780;">Manajemen kas kelas</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def sidebar_section(label):
    st.markdown(f'<div class="sidebar-section">{label}</div>', unsafe_allow_html=True)

def info_badge(text, color="#534AB7", bg="#EEEDFE"):
    st.markdown(f"""
    <div style="display:inline-block; background:{bg}; color:{color};
                font-size:11px; padding:3px 10px; border-radius:20px; font-weight:500;">
        {text}
    </div>""", unsafe_allow_html=True)

def page_header(title, subtitle=None):
    st.markdown(f"<h2 style='font-size:20px; font-weight:500; color:#1A1A1A; margin:0;'>{title}</h2>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<p style='font-size:13px; color:#888780; margin:2px 0 1rem;'>{subtitle}</p>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)

def card_divider():
    st.markdown("<hr style='border:0; border-top:1px solid #EDECEA; margin:0.75rem 0;'>", unsafe_allow_html=True)

# ======================
# VIEW: ROLE PICKER
# ======================
if not st.session_state.login and st.session_state.page == "role":

    render_logo("large")
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; margin-bottom:1.5rem;">
        <p style="font-size:14px; color:#888780;">Pilih peran untuk melanjutkan</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns([1, 1.2, 0.3, 1.2, 1])

    with col2:
        st.markdown("""
        <div style="background:#FFFFFF; border:1px solid #EDECEA; border-radius:12px;
                    padding:1.25rem; text-align:center; margin-bottom:8px;">
            <div style="width:44px; height:44px; background:#EEEDFE; border-radius:10px;
                        display:flex; align-items:center; justify-content:center; margin:0 auto 10px;">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="8" r="4" stroke="#3C3489" stroke-width="1.6"/>
                    <path d="M4 20c0-4 3.582-7 8-7s8 3 8 7" stroke="#3C3489" stroke-width="1.6" stroke-linecap="round"/>
                </svg>
            </div>
            <div style="font-size:14px; font-weight:500; color:#1A1A1A;">Admin</div>
            <div style="font-size:11px; color:#888780; margin-top:3px;">Kelola kas kelas</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Masuk sebagai Admin", key="btn_admin"):
            st.session_state.role = "admin"
            st.session_state.page = "login"
            st.rerun()

    with col4:
        st.markdown("""
        <div style="background:#FFFFFF; border:1px solid #EDECEA; border-radius:12px;
                    padding:1.25rem; text-align:center; margin-bottom:8px;">
            <div style="width:44px; height:44px; background:#E1F5EE; border-radius:10px;
                        display:flex; align-items:center; justify-content:center; margin:0 auto 10px;">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                    <path d="M4 6h16M4 10h16M4 14h10" stroke="#085041" stroke-width="1.6" stroke-linecap="round"/>
                </svg>
            </div>
            <div style="font-size:14px; font-weight:500; color:#1A1A1A;">User</div>
            <div style="font-size:11px; color:#888780; margin-top:3px;">Lihat data kas</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Masuk sebagai User", key="btn_user"):
            st.session_state.role = "user"
            st.session_state.login = True
            st.rerun()

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    with st.expander("🔧 Login Developer"):
        du = st.text_input("Username Developer", key="dev_u")
        dp = st.text_input("Password Developer", type="password", key="dev_p")
        if st.button("Login Developer", key="btn_dev"):
            if du == DEV_USER and dp == DEV_PASS:
                st.session_state.role = "dev"
                st.session_state.login = True
                st.rerun()
            else:
                st.error("Username atau password salah.")

    st.markdown("""
    <div style="text-align:center; margin-top:2rem;">
        <span style="font-size:11px; color:#B4B2A9;">© KasKita 2026</span>
    </div>
    """, unsafe_allow_html=True)

# ======================
# VIEW: LOGIN ADMIN
# ======================
elif not st.session_state.login and st.session_state.page == "login":

    render_logo("large")

    col_l, col_m, col_r = st.columns([1, 1.6, 1])
    with col_m:
        st.markdown("""
        <div style="background:#FFFFFF; border:1px solid #EDECEA; border-radius:14px; padding:1.5rem;">
        """, unsafe_allow_html=True)

        st.markdown("<div style='font-size:16px; font-weight:500; color:#1A1A1A; margin-bottom:1rem;'>Login Admin</div>", unsafe_allow_html=True)

        user = st.text_input("Username", placeholder="Masukkan username")
        pw   = st.text_input("Password", type="password", placeholder="••••••••")

        c1, c2 = st.columns(2)
        with c1:
            kelas = st.selectbox("Kelas", ["10", "11", "12"])
        with c2:
            jurusan = st.text_input("Jurusan", placeholder="Contoh: RPL")

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        if st.button("Masuk ke Dashboard →", type="primary", use_container_width=True):
            if not jurusan.strip():
                st.warning("Jurusan tidak boleh kosong.")
            else:
                st.session_state.login = True
                st.session_state.kelas = kelas
                st.session_state.jurusan = jurusan.upper()
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("← Kembali pilih role"):
            st.session_state.page = "role"
            st.rerun()

# ======================
# MAIN APP (LOGGED IN)
# ======================
else:

    # ==================== USER ====================
    if st.session_state.role == "user":

        with st.sidebar:
            render_logo("small")
            info_badge("Mode: Publik", "#085041", "#E1F5EE")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            sidebar_section("Filter data")

        df_all = pd.read_sql("SELECT * FROM kas", conn)

        with st.sidebar:
            if not df_all.empty:
                df_all["bulan"] = pd.to_datetime(df_all["tanggal"]).dt.strftime("%B %Y")
                fk = st.selectbox("Kelas", sorted(df_all["kelas"].unique()))
                fj = st.selectbox("Jurusan", sorted(df_all["jurusan"].unique()))
                fb = st.selectbox("Bulan", sorted(df_all["bulan"].unique()))
            st.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)
            card_divider()
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
            m1.metric("Total kas", format_rupiah(df["nominal"].sum()))
            m2.metric("Jumlah pembayaran", f"{len(df)} transaksi")
            tl = len(df[df["status"] == "Telat"])
            m3.metric("Pembayaran telat", f"{tl} siswa")

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            tab1, tab2 = st.tabs(["📋 Tabel data", "📊 Statistik"])

            with tab1:
                st.dataframe(df.drop(columns=["bulan"], errors="ignore"),
                             use_container_width=True, hide_index=True)
                st.download_button(
                    "⬇ Download PDF",
                    generate_pdf(df.drop(columns=["bulan"], errors="ignore"), f"Laporan Kas {fk} {fj} — {fb}"),
                    f"kas_{fk}_{fj}.pdf",
                    mime="application/pdf"
                )

            with tab2:
                st.markdown("**Status pembayaran**")
                st.bar_chart(df["status"].value_counts())

    # ==================== DEVELOPER ====================
    elif st.session_state.role == "dev":

        with st.sidebar:
            render_logo("small")
            info_badge("Developer panel", "#633806", "#FAEEDA")
            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            sidebar_section("Menu")
            menu_dev = st.radio("", ["Akun Admin", "Semua Data Kas"], label_visibility="collapsed")
            card_divider()
            if st.button("Keluar", use_container_width=True):
                st.session_state.clear()
                st.rerun()

        page_header("Developer panel", "Manajemen sistem KasKita")

        df_admin = pd.read_sql("SELECT * FROM admin", conn)
        df_kas   = pd.read_sql("SELECT * FROM kas", conn)

        if menu_dev == "Akun Admin":
            st.markdown("#### Daftar akun admin")

            if df_admin.empty:
                st.info("Belum ada akun admin.")
            else:
                st.dataframe(df_admin, use_container_width=True, hide_index=True)
                st.download_button(
                    "⬇ Download PDF akun",
                    generate_pdf(df_admin, "Data Akun Admin"),
                    "akun_admin.pdf",
                    mime="application/pdf"
                )
                card_divider()
                st.markdown("**Hapus akun berdasarkan ID**")
                id_del = st.number_input("ID akun", min_value=1, step=1)
                if st.button("Hapus akun", type="primary"):
                    cursor.execute("DELETE FROM admin WHERE id=?", (int(id_del),))
                    conn.commit()
                    st.success(f"Akun ID {int(id_del)} berhasil dihapus.")
                    st.rerun()

        else:
            st.markdown("#### Semua data kas")
            if df_kas.empty:
                st.info("Belum ada data kas.")
            else:
                st.dataframe(df_kas, use_container_width=True, hide_index=True)
                st.download_button(
                    "⬇ Download PDF kas",
                    generate_pdf(df_kas, "Semua Data Kas"),
                    "kas_all.pdf",
                    mime="application/pdf"
                )

    # ==================== ADMIN ====================
    elif st.session_state.role == "admin":

        kls = st.session_state.kelas
        jrs = st.session_state.jurusan

        with st.sidebar:
            render_logo("small")
            st.markdown(f"""
            <div style="background:#EEEDFE; border-radius:8px; padding:8px 12px; margin-bottom:4px;">
                <div style="font-size:11px; color:#534AB7; font-weight:500;">Kelas {kls} · {jrs}</div>
                <div style="font-size:10px; color:#7F77DD;">Admin aktif</div>
            </div>
            """, unsafe_allow_html=True)

            sidebar_section("Navigasi")

            if st.button("📊  Dashboard", use_container_width=True):
                st.session_state.menu = "dashboard"
                st.rerun()
            if st.button("💸  Pengeluaran", use_container_width=True):
                st.session_state.menu = "pengeluaran"
                st.rerun()
            if st.button("👤  Per Siswa", use_container_width=True):
                st.session_state.menu = "siswa"
                st.rerun()

            sidebar_section("Lainnya")
            if st.button("🗑️  Hapus Data", use_container_width=True):
                st.session_state.menu = "hapus"
                st.rerun()

            st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
            card_divider()
            if st.button("Keluar", use_container_width=True):
                st.session_state.clear()
                st.rerun()

        # ---- load data ----
        df = pd.read_sql(
            "SELECT * FROM kas WHERE kelas=? AND jurusan=?", conn,
            params=(kls, jrs)
        )
        if not df.empty:
            df["tanggal"] = pd.to_datetime(df["tanggal"]).dt.strftime("%Y-%m-%d")

        # ==================== MENU: DASHBOARD ====================
        if st.session_state.menu == "dashboard":

            page_header("Dashboard kas", f"Kelas {kls} · {jrs}")

            # Metrics
            total_kas  = df["nominal"].sum() if not df.empty else 0
            tepat      = len(df[df["status"] == "Tepat Waktu"]) if not df.empty else 0
            telat      = len(df[df["status"] == "Telat"])       if not df.empty else 0

            m1, m2, m3 = st.columns(3)
            m1.metric("Total kas masuk", format_rupiah(total_kas))
            m2.metric("Tepat waktu", f"{tepat} siswa")
            m3.metric("Telat bayar",  f"{telat} siswa")

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            # Input form
            with st.expander("➕ Input pembayaran baru", expanded=False):
                c1, c2 = st.columns(2)
                with c1:
                    nama   = st.text_input("Nama siswa")
                    status = st.selectbox("Status", ["Tepat Waktu", "Telat"])
                with c2:
                    tgl    = st.date_input("Tanggal")
                    nom    = st.text_input("Nominal", placeholder="Contoh: 25000")
                ket = st.text_input("Keterangan", placeholder="Kas bulan April...")
                if st.button("Simpan pembayaran", type="primary"):
                    if not nama.strip():
                        st.warning("Nama siswa tidak boleh kosong.")
                    else:
                        cursor.execute(
                            "INSERT INTO kas VALUES (NULL,?,?,?,?,?,?,?)",
                            (nama.strip(), tgl.strftime("%Y-%m-%d"), status, kls, jrs, ket, clean_nominal(nom))
                        )
                        conn.commit()
                        st.success(f"Pembayaran {nama} berhasil disimpan.")
                        st.rerun()

            card_divider()

            if df.empty:
                st.info("Belum ada data kas untuk kelas ini.")
            else:
                tab1, tab2 = st.tabs(["📋 Data kas", "📊 Statistik"])

                with tab1:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    st.download_button(
                        "⬇ Download PDF kas",
                        generate_pdf(df, f"Laporan Kas Kelas {kls} {jrs}"),
                        f"kas_{kls}_{jrs}.pdf",
                        mime="application/pdf"
                    )

                with tab2:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**Status pembayaran**")
                        st.bar_chart(df["status"].value_counts())
                    with c2:
                        st.markdown("**Nominal per siswa**")
                        st.bar_chart(df.set_index("nama")["nominal"])

        # ==================== MENU: PENGELUARAN ====================
        elif st.session_state.menu == "pengeluaran":

            page_header("Pengeluaran", f"Kelas {kls} · {jrs}")

            with st.expander("➕ Input pengeluaran baru", expanded=False):
                c1, c2 = st.columns(2)
                with c1:
                    tgl_k = st.date_input("Tanggal", key="tgl_keluar")
                with c2:
                    nom_k = st.text_input("Nominal", placeholder="Contoh: 100000", key="nom_keluar")
                ket_k = st.text_input("Keterangan", placeholder="Pembelian ATK...", key="ket_keluar")
                if st.button("Simpan pengeluaran", type="primary", key="save_keluar"):
                    if not ket_k.strip():
                        st.warning("Keterangan tidak boleh kosong.")
                    else:
                        cursor.execute(
                            "INSERT INTO pengeluaran VALUES (NULL,?,?,?,?,?)",
                            (tgl_k.strftime("%Y-%m-%d"), kls, jrs, ket_k, clean_nominal(nom_k))
                        )
                        conn.commit()
                        st.success("Pengeluaran berhasil disimpan.")
                        st.rerun()

            df_keluar = pd.read_sql(
                "SELECT * FROM pengeluaran WHERE kelas=? AND jurusan=?", conn,
                params=(kls, jrs)
            )
            df_masuk = pd.read_sql(
                "SELECT nominal FROM kas WHERE kelas=? AND jurusan=?", conn,
                params=(kls, jrs)
            )

            total_masuk  = df_masuk["nominal"].sum()  if not df_masuk.empty  else 0
            total_keluar = df_keluar["nominal"].sum()  if not df_keluar.empty else 0
            saldo        = total_masuk - total_keluar

            card_divider()

            m1, m2, m3 = st.columns(3)
            m1.metric("Total kas masuk",    format_rupiah(total_masuk))
            m2.metric("Total pengeluaran",  format_rupiah(total_keluar))
            m3.metric("Saldo tersisa",      format_rupiah(saldo),
                      delta=format_rupiah(saldo - total_keluar) if total_keluar else None)

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            if df_keluar.empty:
                st.info("Belum ada data pengeluaran.")
            else:
                df_keluar["tanggal"] = pd.to_datetime(df_keluar["tanggal"]).dt.strftime("%Y-%m-%d")
                st.dataframe(df_keluar, use_container_width=True, hide_index=True)
                st.download_button(
                    "⬇ Download PDF pengeluaran",
                    generate_pdf(df_keluar, f"Laporan Pengeluaran Kelas {kls} {jrs}"),
                    f"pengeluaran_{kls}_{jrs}.pdf",
                    mime="application/pdf"
                )

        # ==================== MENU: PER SISWA ====================
        elif st.session_state.menu == "siswa":

            page_header("Statistik per siswa", f"Kelas {kls} · {jrs}")

            if df.empty:
                st.info("Belum ada data siswa.")
            else:
                siswa_list = sorted(df["nama"].unique())
                siswa = st.selectbox("Pilih siswa", siswa_list)

                if st.button("Lihat statistik", type="primary"):
                    data_siswa = df[df["nama"] == siswa]
                    hasil      = data_siswa["status"].value_counts()

                    card_divider()

                    total = len(data_siswa)
                    telat = len(data_siswa[data_siswa["status"] == "Telat"])
                    persen = (telat / total * 100) if total > 0 else 0

                    st.markdown(f"**Siswa:** {siswa} &nbsp;·&nbsp; **Total pembayaran:** {total} kali")
                    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

                    c1, c2 = st.columns([1.4, 1])
                    with c1:
                        st.bar_chart(hasil)
                    with c2:
                        st.metric("Tepat waktu", f"{total - telat}x")
                        st.metric("Telat",        f"{telat}x")
                        st.metric("% Telat",      f"{persen:.0f}%")

                    if persen < 20:
                        st.success("Performa sangat baik")
                    elif persen < 50:
                        st.warning("Perlu peningkatan")
                    else:
                        st.error("Sering telat — perlu tindak lanjut")

        # ==================== MENU: HAPUS DATA ====================
        elif st.session_state.menu == "hapus":

            page_header("Hapus data", f"Kelas {kls} · {jrs}")
            st.warning("Tindakan hapus bersifat permanen dan tidak bisa dibatalkan.")

            konfirmasi = st.checkbox("Saya memahami risiko dan ingin melanjutkan")

            card_divider()

            c1, c2, c3 = st.columns(3)

            with c1:
                st.markdown("**Hapus berdasarkan ID**")
                id_hapus = st.number_input("ID data", min_value=1, step=1, key="id_hp")
                if st.button("Hapus ID ini", key="btn_hid"):
                    if konfirmasi:
                        cursor.execute("DELETE FROM kas WHERE id=?", (int(id_hapus),))
                        conn.commit()
                        st.success(f"ID {int(id_hapus)} dihapus.")
                        st.rerun()
                    else:
                        st.error("Centang konfirmasi terlebih dahulu.")

            with c2:
                st.markdown("**Hapus semua data siswa**")
                if not df.empty:
                    siswa_del = st.selectbox("Pilih siswa", df["nama"].unique(), key="siswa_del")
                    if st.button("Hapus siswa ini", key="btn_hsiswa"):
                        if konfirmasi:
                            cursor.execute("DELETE FROM kas WHERE nama=?", (siswa_del,))
                            conn.commit()
                            st.success(f"Data {siswa_del} dihapus.")
                            st.rerun()
                        else:
                            st.error("Centang konfirmasi terlebih dahulu.")

            with c3:
                st.markdown("**Hapus semua data kelas**")
                st.caption(f"Akan menghapus seluruh data kelas {kls} {jrs}")
                if st.button("Hapus semua", key="btn_hall", type="primary"):
                    if konfirmasi:
                        cursor.execute(
                            "DELETE FROM kas WHERE kelas=? AND jurusan=?", (kls, jrs)
                        )
                        conn.commit()
                        st.success("Semua data kelas dihapus.")
                        st.rerun()
                    else:
                        st.error("Centang konfirmasi terlebih dahulu.")

# ======================
# FOOTER
# ======================
st.markdown("""
<div style="text-align:center; padding:2rem 0 0.5rem;">
    <span style="font-size:11px; color:#B4B2A9;">© KasKita 2026</span>
</div>
""", unsafe_allow_html=True)
