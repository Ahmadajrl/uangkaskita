import streamlit as st
import pandas as pd
import sqlite3
import io
from datetime import date
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="KAS KITA",
    page_icon="💳",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────
# GLOBAL CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main          { background: #03043D !important; }
[data-testid="stAppViewContainer"]     { font-family: 'Inter', sans-serif !important; }

/* ── Hide streamlit chrome ── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebar"]              { display: none !important; visibility: hidden !important; }

/* ── Container width ── */
.block-container { max-width: 480px !important; padding: 0 1rem 6rem !important; margin: 0 auto !important; }

/* ── Typography ── */
h1,h2,h3,h4,h5,h6,p,span,label,div   { color: #FFFFFF; }

/* ── Inputs ── */
input, textarea,
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTextArea textarea {
    background: #0A0E3A !important;
    border: 1.5px solid #1E2560 !important;
    border-radius: 12px !important;
    color: #FFFFFF !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
}
input::placeholder, textarea::placeholder { color: #4A5099 !important; }
input:focus, textarea:focus {
    border-color: #09F289 !important;
    box-shadow: 0 0 0 2px rgba(9,242,137,0.15) !important;
    outline: none !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: #0A0E3A !important;
    border: 1.5px solid #1E2560 !important;
    border-radius: 12px !important;
    color: #FFFFFF !important;
}
.stSelectbox svg { fill: #09F289 !important; }

/* ── Buttons ── */
.stButton > button {
    width: 100% !important;
    background: #09F289 !important;
    color: #03043D !important;
    border: none !important;
    border-radius: 14px !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    padding: 14px 20px !important;
    letter-spacing: .5px;
    transition: opacity .15s;
    cursor: pointer;
}
.stButton > button:hover   { opacity: .88 !important; }
.stButton > button:active  { opacity: .75 !important; }

/* ghost button override */
.ghost-btn button {
    background: transparent !important;
    color: #09F289 !important;
    border: 1.5px solid #09F289 !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
}

/* ── Labels ── */
.stTextInput label,
.stNumberInput label,
.stDateInput label,
.stSelectbox label,
.stTextArea label {
    color: #7B82C4 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: .06em !important;
    text-transform: uppercase !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    background: #121A4D !important;
    border-radius: 14px !important;
    border: 1px solid #1E2560 !important;
    overflow: hidden !important;
}

/* ── Alerts ── */
.stSuccess { background: rgba(9,242,137,.1)!important; border:1px solid rgba(9,242,137,.3)!important; border-radius:12px!important; color:#09F289!important; }
.stError   { background: rgba(255,80,80,.1)!important;  border:1px solid rgba(255,80,80,.3)!important;  border-radius:12px!important; }
.stWarning { border-radius:12px!important; }
.stInfo    { background: rgba(9,242,137,.06)!important; border:1px solid #1E2560!important; border-radius:12px!important; color:#7B82C4!important; }

/* ── Divider ── */
hr { border-color: #1E2560 !important; margin: 1rem 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #03043D; }
::-webkit-scrollbar-thumb { background: #1E2560; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────
_defaults = {
    "role": None, "login": False,
    "kelas": "XII RPL 1", "jurusan": "Rekayasa Perangkat Lunak",
    "page": "role", "subnav": "dashboard",
    "dev_menu": "Akun Admin",
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ──────────────────────────────────────────────
# DB
# ──────────────────────────────────────────────
@st.cache_resource
def init_db():
    conn = sqlite3.connect("kaskita.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS kas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT, tanggal TEXT, status TEXT,
        kelas TEXT, jurusan TEXT, keterangan TEXT, nominal INTEGER)""")
    c.execute("""CREATE TABLE IF NOT EXISTS admin_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, password TEXT, email TEXT, kelas TEXT, jurusan TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS pengeluaran (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tanggal TEXT, kelas TEXT, jurusan TEXT, keterangan TEXT, nominal INTEGER)""")
    # seed dummy admin accounts
    c.execute("SELECT COUNT(*) FROM admin_accounts")
    if c.fetchone()[0] == 0:
        seed = [
            ("admin_dhimas",  "pass","dhimas.dev@kaskita.id",  "XII","RPL"),
            ("sari_keuangan", "pass","sari.p@kaskita.id",      "XI", "IPA"),
            ("rendy_bendahara","pass","rendy.b@kaskita.id",    "X",  "IPS"),
            ("fauzan_monitor","pass","fauzan.m@kaskita.id",    "XII","MIPA"),
        ]
        c.executemany("INSERT INTO admin_accounts(username,password,email,kelas,jurusan) VALUES(?,?,?,?,?)", seed)
    conn.commit()
    return conn, c

conn, cursor = init_db()

# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────
def fmt_rp(n):
    return "Rp {:,.0f}".format(n).replace(",", ".")

def clean_nom(n):
    if not n: return 0
    s = str(n).lower().replace("rp","").replace(".","").replace(",","").strip()
    return int(s) if s.isdigit() else 0

def gen_pdf(df, title="Laporan KasKita"):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=40, bottomMargin=40)
    st_pdf = getSampleStyleSheet()
    els = [Paragraph(f"<b>{title}</b>", st_pdf["Title"]), Spacer(1,12)]
    data = [df.columns.tolist()] + df.values.tolist()
    t = Table(data, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#03043D")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.HexColor("#09F289")),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,0),10),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F3FDF9")]),
        ("GRID",(0,0),(-1,-1),.5,colors.HexColor("#D1FAE5")),
        ("FONTSIZE",(0,1),(-1,-1),9),
        ("PADDING",(0,0),(-1,-1),6),
    ]))
    els += [t, Spacer(1,16), Paragraph("© KasKita 2026", st_pdf["Normal"])]
    doc.build(els)
    buf.seek(0)
    return buf

# ──────────────────────────────────────────────
# REUSABLE UI COMPONENTS
# ──────────────────────────────────────────────
def topbar(subtitle="", show_bell=True):
    bell = "🔔" if show_bell else ""
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
                padding:18px 0 10px;">
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:38px;height:38px;background:#09F289;border-radius:10px;
                        display:flex;align-items:center;justify-content:center;">
                <svg width="20" height="20" viewBox="0 0 22 22" fill="none">
                    <rect x="2" y="6" width="18" height="11" rx="2.5" stroke="#03043D" stroke-width="1.8"/>
                    <path d="M2 9.5h18" stroke="#03043D" stroke-width="1.8"/>
                    <rect x="4.5" y="12" width="6" height="2" rx=".6" fill="#03043D"/>
                </svg>
            </div>
            <div>
                <div style="font-size:16px;font-weight:800;color:#09F289;letter-spacing:.5px;">KASKITA</div>
                {f'<div style="font-size:11px;color:#7B82C4;">{subtitle}</div>' if subtitle else ""}
            </div>
        </div>
        <div style="display:flex;align-items:center;gap:12px;">
            {f'<span style="font-size:20px;">{bell}</span>' if show_bell else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)

def card(content_html, padding="1.2rem 1.4rem", mb="1rem", extra_style=""):
    st.markdown(f"""
    <div style="background:#121A4D;border:1px solid #1E2560;border-radius:18px;
                padding:{padding};margin-bottom:{mb};{extra_style}">
        {content_html}
    </div>""", unsafe_allow_html=True)

def badge(text, color="#09F289", bg="rgba(9,242,137,.15)", radius="8px"):
    return (f'<span style="background:{bg};color:{color};font-size:10px;font-weight:700;'
            f'padding:4px 10px;border-radius:{radius};letter-spacing:.04em;">{text.upper()}</span>')

def section_title(text, right_html=""):
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;margin:1.2rem 0 .6rem;">
        <span style="font-size:17px;font-weight:700;color:#FFFFFF;">{text}</span>
        {right_html}
    </div>""", unsafe_allow_html=True)

def bottom_nav(active="dashboard"):
    tabs = [
        ("dashboard","M3 3h7v7H3V3zm0 11h7v7H3v-7zm11-11h7v7h-7V3zm0 11h7v7h-7v-7z","DASHBOARD"),
        ("history",  "M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z","HISTORY"),
        ("logout",   "M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-6 0v-1m0-8V7a3 3 0 016 0v1","LOGOUT"),
    ]
    items_html = ""
    for key, path, label in tabs:
        col = "#09F289" if active == key else "#4A5099"
        bg  = "background:rgba(9,242,137,.1);border-radius:12px;padding:6px 18px;" if active==key else "padding:6px 18px;"
        items_html += f"""
        <div style="{bg}display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;"
             onclick="void(0)">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
                 stroke="{col}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="{path}"/>
            </svg>
            <span style="font-size:9px;font-weight:700;color:{col};letter-spacing:.06em;">{label}</span>
        </div>"""

    st.markdown(f"""
    <div style="position:fixed;bottom:0;left:50%;transform:translateX(-50%);width:100%;max-width:480px;
                background:#03043D;border-top:1px solid #1E2560;padding:10px 24px;z-index:9999;
                display:flex;justify-content:space-around;align-items:center;">
        {items_html}
    </div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# PAGE: ROLE SELECTION
# ──────────────────────────────────────────────
def page_role():
    # header logo
    st.markdown("""
    <div style="text-align:center;padding:2rem 0 1.5rem;">
        <div style="display:inline-flex;align-items:center;gap:10px;margin-bottom:1.5rem;">
            <div style="width:44px;height:44px;background:#09F289;border-radius:12px;
                        display:flex;align-items:center;justify-content:center;">
                <svg width="24" height="24" viewBox="0 0 22 22" fill="none">
                    <rect x="2" y="6" width="18" height="11" rx="2.5" stroke="#03043D" stroke-width="1.8"/>
                    <path d="M2 9.5h18" stroke="#03043D" stroke-width="1.8"/>
                    <rect x="4.5" y="12" width="6" height="2" rx=".6" fill="#03043D"/>
                </svg>
            </div>
            <span style="font-size:22px;font-weight:900;color:#09F289;letter-spacing:.5px;">KAS KITA</span>
        </div>
        <h1 style="font-size:28px;font-weight:800;color:#FFFFFF;margin:0 0 .75rem;line-height:1.2;">
            Selamat Datang di<br>Kas Kita
        </h1>
        <p style="font-size:14px;color:#7B82C4;margin:0;line-height:1.6;">
            Tentukan peran Anda untuk mulai<br>mengelola ekosistem finansial digital yang cerdas.
        </p>
    </div>
    """, unsafe_allow_html=True)

    roles = [
        ("admin","🛡️","#1A2260","Admin",
         "Manajemen sistem penuh, kontrol otorisasi, dan audit laporan konsolidasi."),
        ("user","👤","#09F289","User",
         "Akses personal untuk mencatat transaksi, memantau saldo, dan laporan individu."),
        ("dev","⟨/⟩","#1A2260","Developer",
         "Integrasi API, kustomisasi teknis, dan pemeliharaan struktur basis data."),
    ]

    for key, icon, icon_bg, label, desc in roles:
        border = "border:2px solid #09F289;" if key=="user" else "border:1px solid #1E2560;"
        st.markdown(f"""
        <div style="background:#121A4D;{border}border-radius:20px;padding:1.4rem 1.4rem 1rem;margin-bottom:1rem;">
            <div style="width:52px;height:52px;background:{icon_bg};border-radius:14px;
                        display:flex;align-items:center;justify-content:center;
                        font-size:22px;margin-bottom:1rem;">{icon}</div>
            <div style="font-size:20px;font-weight:700;color:#FFFFFF;margin-bottom:.4rem;">{label}</div>
            <div style="font-size:13px;color:#7B82C4;line-height:1.6;margin-bottom:1rem;">{desc}</div>
        </div>""", unsafe_allow_html=True)

        if st.button(f"PILIH ROLE  →", key=f"role_{key}"):
            if key == "admin":
                st.session_state.role = "admin"
                st.session_state.page = "login_admin"
                st.rerun()
            elif key == "user":
                st.session_state.role = "user"
                st.session_state.login = True
                st.session_state.page = "user"
                st.rerun()
            elif key == "dev":
                st.session_state.role = "dev"
                st.session_state.page = "login_dev"
                st.rerun()

    st.markdown("""
    <div style="text-align:center;margin-top:2rem;padding-bottom:1rem;">
        <span style="font-size:10px;color:#2D3580;letter-spacing:.12em;text-transform:uppercase;">
            ── ENKRIPSI VAULT 256-BIT ──
        </span>
    </div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# PAGE: LOGIN ADMIN
# ──────────────────────────────────────────────
def page_login_admin():
    topbar("Masuk sebagai Admin")
    st.markdown("""
    <div style="padding:1rem 0 1.5rem;">
        <h2 style="font-size:24px;font-weight:800;margin:0 0 .3rem;">Login Admin</h2>
        <p style="font-size:13px;color:#7B82C4;margin:0;">Masukkan detail kelas untuk melanjutkan</p>
    </div>""", unsafe_allow_html=True)

    username = st.text_input("Username", placeholder="Contoh: admin_dhimas")
    password = st.text_input("Password", type="password", placeholder="••••••••")
    c1, c2 = st.columns(2)
    with c1: kelas   = st.selectbox("Kelas", ["X","XI","XII"], index=2)
    with c2: jurusan = st.text_input("Jurusan", placeholder="RPL")

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    if st.button("MASUK KE DASHBOARD"):
        if not jurusan.strip():
            st.error("Jurusan tidak boleh kosong.")
        else:
            st.session_state.login   = True
            st.session_state.kelas   = kelas
            st.session_state.jurusan = jurusan.upper()
            st.session_state.page    = "admin"
            st.rerun()

    if st.button("← Kembali", key="back_admin"):
        st.session_state.page = "role"
        st.rerun()

# ──────────────────────────────────────────────
# PAGE: LOGIN DEVELOPER
# ──────────────────────────────────────────────
def page_login_dev():
    topbar("Developer Access")
    st.markdown("""
    <div style="padding:1rem 0 1.5rem;">
        <h2 style="font-size:24px;font-weight:800;margin:0 0 .3rem;">Login Developer</h2>
        <p style="font-size:13px;color:#7B82C4;margin:0;">Kredensial akses sistem backend</p>
    </div>""", unsafe_allow_html=True)

    du = st.text_input("Username", placeholder="developer username", key="dev_u")
    dp = st.text_input("Password", type="password", placeholder="••••••••", key="dev_p")
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    if st.button("MASUK DEVELOPER PANEL"):
        if du == "admin" and dp == "12345":
            st.session_state.login = True
            st.session_state.page  = "dev"
            st.rerun()
        else:
            st.error("Username atau password salah. Gunakan admin / 12345")

    if st.button("← Kembali", key="back_dev"):
        st.session_state.page = "role"
        st.rerun()

# ──────────────────────────────────────────────
# PAGE: ADMIN DASHBOARD
# ──────────────────────────────────────────────
def page_admin():
    kls = st.session_state.kelas
    jrs = st.session_state.jurusan

    nav = st.session_state.subnav

    # ── Top bar ──
    topbar(f"Admin Panel")
    st.markdown(f"""
    <div style="padding:.5rem 0 1rem;">
        <div style="font-size:22px;font-weight:800;">Halo, <span style="color:#09F289;">Admin</span></div>
        <div style="font-size:13px;color:#7B82C4;margin-top:2px;">
            Status Keuangan Kelas: <span style="color:#09F289;font-weight:600;">{kls} {jrs}</span>
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Load data ──
    df = pd.read_sql("SELECT * FROM kas WHERE kelas=? AND jurusan=?",
                     conn, params=(kls, jrs))
    if not df.empty:
        df["tanggal"] = pd.to_datetime(df["tanggal"]).dt.strftime("%Y-%m-%d")

    total_kas   = df["nominal"].sum() if not df.empty else 0
    tepat_count = len(df[df["status"]=="Tepat Waktu"]) if not df.empty else 0
    telat_count = len(df[df["status"]=="Telat"])       if not df.empty else 0
    total_count = len(df)

    if nav == "dashboard":
        # ── Total Kas Card ──
        card(f"""
        <div style="font-size:10px;font-weight:700;color:#7B82C4;letter-spacing:.08em;
                    text-transform:uppercase;margin-bottom:.5rem;">TOTAL KAS</div>
        <div style="font-size:28px;font-weight:800;color:#FFFFFF;margin-bottom:.4rem;">
            {fmt_rp(total_kas)}
        </div>
        <div style="font-size:12px;color:#09F289;font-weight:600;">
            ↑ 12% dari bulan lalu
        </div>""")

        # ── Statistik Siswa ──
        section_title("Statistik Siswa")
        st.markdown('<div style="background:#121A4D;border:1px solid #1E2560;border-radius:18px;padding:1.2rem 1.4rem;margin-bottom:1rem;">', unsafe_allow_html=True)

        st.markdown('<div style="font-size:10px;font-weight:700;color:#7B82C4;letter-spacing:.08em;text-transform:uppercase;margin-bottom:.5rem;">PILIH SISWA</div>', unsafe_allow_html=True)

        if df.empty:
            st.info("Belum ada data siswa.")
        else:
            siswa_list = sorted(df["nama"].unique())
            siswa_sel  = st.selectbox("", siswa_list, label_visibility="collapsed", key="stat_siswa")
            ds = df[df["nama"]==siswa_sel]
            tot  = len(ds)
            tel  = len(ds[ds["status"]=="Telat"])
            tpt  = tot - tel
            pct  = int((tpt/tot)*100) if tot>0 else 0
            perf = "PERFORMA SANGAT BAIK" if (tel/tot*100 if tot else 0)<20 else ("PERLU PENINGKATAN" if (tel/tot*100 if tot else 0)<50 else "SERING TELAT")
            perf_col = "#09F289" if perf=="PERFORMA SANGAT BAIK" else ("#F5A623" if "PENINGKATAN" in perf else "#FF5050")

            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:1.5rem;margin-top:.75rem;">
                <div style="position:relative;width:80px;height:80px;flex-shrink:0;">
                    <svg viewBox="0 0 36 36" width="80" height="80">
                        <circle cx="18" cy="18" r="15.9" fill="none"
                                stroke="#1E2560" stroke-width="3"/>
                        <circle cx="18" cy="18" r="15.9" fill="none"
                                stroke="#09F289" stroke-width="3"
                                stroke-dasharray="{pct} {100-pct}"
                                stroke-dashoffset="25" stroke-linecap="round"/>
                    </svg>
                    <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
                                font-size:15px;font-weight:800;color:#FFFFFF;">{pct}%</div>
                </div>
                <div>
                    <div style="display:flex;gap:1rem;margin-bottom:.5rem;">
                        <span style="font-size:12px;color:#7B82C4;">TEPAT WAKTU: <b style="color:#09F289;">{tpt}</b></span>
                        <span style="font-size:12px;color:#7B82C4;">TELAT: <b style="color:#FF5050;">{tel}</b></span>
                    </div>
                    <span style="background:rgba(9,242,137,.12);color:{perf_col};font-size:10px;
                                 font-weight:700;padding:4px 10px;border-radius:8px;letter-spacing:.04em;">
                        ● {perf}
                    </span>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Input Pembayaran ──
        section_title("Input Pembayaran")
        st.markdown('<div style="background:#121A4D;border:1px solid #1E2560;border-radius:18px;padding:1.2rem 1.4rem;margin-bottom:1rem;">', unsafe_allow_html=True)

        nama   = st.text_input("NAMA SISWA", placeholder="Contoh: Ahmad Fauzan", key="inp_nama")
        c1, c2 = st.columns(2)
        with c1: tgl    = st.date_input("TANGGAL", value=date.today(), key="inp_tgl")
        with c2: status = st.selectbox("STATUS", ["Tepat Waktu","Telat"], key="inp_status")
        nominal = st.text_input("NOMINAL (RP)", placeholder="20000", key="inp_nom")
        ket     = st.text_area("KETERANGAN", placeholder="Kas Minggu ke-2 Februari", key="inp_ket", height=80)

        if st.button("Simpan Data"):
            if not nama.strip():
                st.error("Nama siswa tidak boleh kosong.")
            else:
                cursor.execute(
                    "INSERT INTO kas VALUES(NULL,?,?,?,?,?,?,?)",
                    (nama.strip(), str(tgl), status, kls, jrs, ket, clean_nom(nominal))
                )
                conn.commit()
                st.success(f"Data {nama.strip()} berhasil disimpan!")
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Distribusi Status ──
        section_title("Distribusi Status Bayar")
        st.markdown(f"""
        <div style="background:#121A4D;border:1px solid #1E2560;border-radius:18px;
                    padding:1.4rem;margin-bottom:1rem;display:flex;gap:2rem;">
            <div style="text-align:center;">
                <div style="font-size:36px;font-weight:800;color:#09F289;">{tepat_count}</div>
                <div style="font-size:10px;font-weight:700;color:#7B82C4;letter-spacing:.06em;
                            text-transform:uppercase;margin-top:4px;">TEPAT WAKTU</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:36px;font-weight:800;color:#FF5050;">{telat_count}</div>
                <div style="font-size:10px;font-weight:700;color:#7B82C4;letter-spacing:.06em;
                            text-transform:uppercase;margin-top:4px;">TELAT</div>
            </div>
        </div>""", unsafe_allow_html=True)

        # ── Riwayat ──
        section_title("Riwayat Data Kas",
                      right_html='<span style="font-size:12px;color:#09F289;font-weight:700;cursor:pointer;">LIHAT SEMUA</span>')

        if df.empty:
            st.info("Belum ada data kas.")
        else:
            for _, row in df.tail(10).iloc[::-1].iterrows():
                s_col  = "#09F289" if row["status"]=="Tepat Waktu" else "#FF5050"
                s_bg   = "rgba(9,242,137,.12)" if row["status"]=="Tepat Waktu" else "rgba(255,80,80,.12)"
                s_lbl  = "TEPAT WAKTU" if row["status"]=="Tepat Waktu" else "TELAT"
                card(f"""
                <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:.5rem;">
                    <div style="flex:1;">
                        <div style="font-size:14px;font-weight:700;color:#FFFFFF;">{row["nama"]}</div>
                        <div style="font-size:11px;color:#7B82C4;margin-top:2px;">{row["keterangan"] or ""}</div>
                        <div style="font-size:11px;color:#4A5099;margin-top:4px;">{row["tanggal"]}</div>
                    </div>
                    <div style="text-align:right;flex-shrink:0;">
                        <span style="background:{s_bg};color:{s_col};font-size:9px;font-weight:700;
                                     padding:3px 8px;border-radius:6px;">{s_lbl}</span>
                        <div style="font-size:14px;font-weight:700;color:#09F289;margin-top:6px;">
                            + {fmt_rp(row["nominal"])}
                        </div>
                    </div>
                </div>""", padding=".9rem 1.1rem", mb=".5rem")

            st.download_button("⬇ Download PDF Kas",
                gen_pdf(df, f"Laporan Kas {kls} {jrs}"),
                f"kas_{kls}_{jrs}.pdf", mime="application/pdf")

    elif nav == "history":
        section_title("Riwayat Lengkap")
        if df.empty:
            st.info("Belum ada data.")
        else:
            df_show = df.copy()
            df_show["nominal"] = df_show["nominal"].apply(fmt_rp)
            st.dataframe(df_show, use_container_width=True, hide_index=True)
            st.download_button("⬇ Download PDF",
                gen_pdf(df, f"Riwayat Kas {kls} {jrs}"),
                f"riwayat_{kls}_{jrs}.pdf", mime="application/pdf")

    # ── Bottom Nav ──
    bottom_nav(nav)

    c1,c2,c3 = st.columns(3)
    with c1:
        if st.button("Dashboard", key="nav_db"):
            st.session_state.subnav="dashboard"; st.rerun()
    with c2:
        if st.button("History",   key="nav_hs"):
            st.session_state.subnav="history";   st.rerun()
    with c3:
        if st.button("Logout",    key="nav_lo"):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()

# ──────────────────────────────────────────────
# PAGE: USER
# ──────────────────────────────────────────────
def page_user():
    topbar()
    st.markdown("""
    <div style="padding:.5rem 0 1.2rem;">
        <h2 style="font-size:22px;font-weight:800;margin:0 0 .3rem;">Riwayat Data Kas</h2>
        <p style="font-size:13px;color:#7B82C4;margin:0;">Cari data kas berdasarkan kelas dan bulan</p>
    </div>""", unsafe_allow_html=True)

    df_all = pd.read_sql("SELECT * FROM kas", conn)

    if df_all.empty:
        st.info("Belum ada data kas tersedia.")
        if st.button("Logout", key="user_lo"):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()
        return

    df_all["bulan_label"] = pd.to_datetime(df_all["tanggal"]).dt.strftime("%B %Y")

    # ── Filters ──
    st.markdown('<div style="background:#121A4D;border:1px solid #1E2560;border-radius:18px;padding:1.2rem 1.4rem;margin-bottom:1rem;">', unsafe_allow_html=True)
    fj = st.selectbox("Pilih Jurusan", ["Semua"] + sorted(df_all["jurusan"].unique().tolist()), key="uf_jrs")
    fk = st.selectbox("Pilih Kelas",   ["Semua"] + sorted(df_all["kelas"].unique().tolist()),   key="uf_kls")
    fb = st.selectbox("Pilih Bulan",   ["Semua"] + sorted(df_all["bulan_label"].unique().tolist()), key="uf_bln")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🔍  CEK SEKARANG"):
        df_f = df_all.copy()
        if fj != "Semua": df_f = df_f[df_f["jurusan"]==fj]
        if fk != "Semua": df_f = df_f[df_f["kelas"]==fk]
        if fb != "Semua": df_f = df_f[df_f["bulan_label"]==fb]
        st.session_state["user_df"] = df_f.to_dict()

    df_show = df_all.copy()
    if "user_df" in st.session_state:
        df_show = pd.DataFrame(st.session_state["user_df"])

    df_show["tanggal"] = pd.to_datetime(df_show["tanggal"]).dt.strftime("%d %b %Y")

    section_title("Riwayat Data Kas",
                  right_html='<span style="font-size:12px;color:#09F289;font-weight:700;">LIHAT SEMUA</span>')

    # Table header
    st.markdown("""
    <div style="background:#0A0E3A;border:1px solid #1E2560;border-radius:14px 14px 0 0;
                padding:.7rem 1rem;display:grid;grid-template-columns:2fr 1.2fr 1.2fr 1fr;gap:.5rem;">
        <span style="font-size:10px;font-weight:700;color:#4A5099;text-transform:uppercase;letter-spacing:.06em;">NAMA SISWA</span>
        <span style="font-size:10px;font-weight:700;color:#4A5099;text-transform:uppercase;letter-spacing:.06em;">TANGGAL</span>
        <span style="font-size:10px;font-weight:700;color:#4A5099;text-transform:uppercase;letter-spacing:.06em;">STATUS</span>
        <span style="font-size:10px;font-weight:700;color:#4A5099;text-transform:uppercase;letter-spacing:.06em;">NOMINAL</span>
    </div>""", unsafe_allow_html=True)

    if df_show.empty:
        st.info("Tidak ada data untuk filter ini.")
    else:
        rows_html = ""
        for i, (_, row) in enumerate(df_show.head(20).iterrows()):
            s_col = "#09F289" if row["status"]=="Tepat Waktu" else "#FF5050"
            s_bg  = "rgba(9,242,137,.12)" if row["status"]=="Tepat Waktu" else "rgba(255,80,80,.12)"
            s_lbl = "BERHASIL" if row["status"]=="Tepat Waktu" else "PENDING"
            nom_col = "#09F289" if row["status"]=="Tepat Waktu" else "#FFFFFF"
            nom_prefix = "+" if row["status"]=="Tepat Waktu" else ""
            border_b = "" if i == len(df_show.head(20))-1 else "border-bottom:1px solid #1E2560;"
            rows_html += f"""
            <div style="padding:.85rem 1rem;display:grid;grid-template-columns:2fr 1.2fr 1.2fr 1fr;
                        gap:.5rem;align-items:center;{border_b}">
                <div>
                    <div style="font-size:13px;font-weight:600;color:#FFFFFF;">{row["nama"]}</div>
                    <div style="font-size:10px;color:#4A5099;margin-top:2px;">{row["kelas"]} {row["jurusan"]}</div>
                </div>
                <div style="font-size:11px;color:#7B82C4;">{row["tanggal"]}</div>
                <div><span style="background:{s_bg};color:{s_col};font-size:9px;font-weight:700;
                               padding:3px 8px;border-radius:6px;">{s_lbl}</span></div>
                <div style="font-size:12px;font-weight:700;color:{nom_col};">
                    {nom_prefix} {int(row["nominal"])//1000 if row["nominal"] else 0}k
                </div>
            </div>"""

        st.markdown(f"""
        <div style="background:#121A4D;border:1px solid #1E2560;border-top:none;
                    border-radius:0 0 14px 14px;margin-bottom:1rem;">
            {rows_html}
        </div>""", unsafe_allow_html=True)

        st.download_button("⬇ Download PDF",
            gen_pdf(df_show.drop(columns=["bulan_label"], errors="ignore"),
                    "Laporan Kas User"),
            "kas_user.pdf", mime="application/pdf")

    bottom_nav("dashboard")
    c1, _, c3 = st.columns([1,1,1])
    with c1:
        if st.button("Dashboard", key="usr_db"): st.rerun()
    with c3:
        if st.button("Logout", key="usr_lo"):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()

# ──────────────────────────────────────────────
# PAGE: DEVELOPER PANEL
# ──────────────────────────────────────────────
def page_dev():
    nav = st.session_state.subnav

    # topbar with developer badge
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:space-between;padding:18px 0 10px;">
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:38px;height:38px;background:#09F289;border-radius:10px;
                        display:flex;align-items:center;justify-content:center;">
                <svg width="20" height="20" viewBox="0 0 22 22" fill="none">
                    <rect x="2" y="6" width="18" height="11" rx="2.5" stroke="#03043D" stroke-width="1.8"/>
                    <path d="M2 9.5h18" stroke="#03043D" stroke-width="1.8"/>
                    <rect x="4.5" y="12" width="6" height="2" rx=".6" fill="#03043D"/>
                </svg>
            </div>
            <div>
                <div style="font-size:14px;font-weight:800;color:#09F289;">KAS KITA</div>
                <div style="font-size:10px;color:#7B82C4;">Developer Panel</div>
            </div>
        </div>
        <div style="display:flex;align-items:center;gap:10px;">
            <span style="font-size:18px;">🔔</span>
            <div style="width:34px;height:34px;border-radius:50%;background:#1E2560;
                        display:flex;align-items:center;justify-content:center;font-size:16px;">👨‍💻</div>
        </div>
    </div>""", unsafe_allow_html=True)

    df_admin = pd.read_sql("SELECT * FROM admin_accounts", conn)
    df_kas   = pd.read_sql("SELECT * FROM kas", conn)

    if nav == "dashboard":
        st.markdown("""
        <h2 style="font-size:24px;font-weight:800;margin:.5rem 0 .3rem;">Data Akun Admin</h2>
        <p style="font-size:13px;color:#7B82C4;margin:0 0 1.2rem;line-height:1.6;">
            Manage system administrators and monitor account statuses within the KAS KITA ecosystem.
        </p>""", unsafe_allow_html=True)

        # ── Table header ──
        st.markdown("""
        <div style="background:#0A0E3A;border:1px solid #1E2560;border-radius:14px 14px 0 0;
                    padding:.7rem 1rem;display:grid;grid-template-columns:2fr 2fr;gap:.5rem;">
            <span style="font-size:10px;font-weight:700;color:#4A5099;text-transform:uppercase;letter-spacing:.06em;">USERNAME</span>
            <span style="font-size:10px;font-weight:700;color:#4A5099;text-transform:uppercase;letter-spacing:.06em;">EMAIL</span>
        </div>""", unsafe_allow_html=True)

        rows_html = ""
        for i, (_, row) in enumerate(df_admin.iterrows()):
            initials = "".join([w[0].upper() for w in row["username"].split("_")[:2]])
            border_b = "" if i == len(df_admin)-1 else "border-bottom:1px solid #1E2560;"
            rows_html += f"""
            <div style="padding:.9rem 1rem;display:grid;grid-template-columns:2fr 2fr;
                        gap:.5rem;align-items:center;{border_b}">
                <div style="display:flex;align-items:center;gap:.7rem;">
                    <div style="width:36px;height:36px;background:#1A2260;border-radius:10px;
                                display:flex;align-items:center;justify-content:center;
                                font-size:11px;font-weight:700;color:#09F289;flex-shrink:0;">{initials}</div>
                    <span style="font-size:13px;font-weight:600;color:#FFFFFF;">{row["username"]}</span>
                </div>
                <div style="font-size:12px;color:#7B82C4;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                    {row["email"]}
                </div>
            </div>"""

        st.markdown(f"""
        <div style="background:#121A4D;border:1px solid #1E2560;border-top:none;
                    border-radius:0 0 14px 14px;margin-bottom:1rem;">
            {rows_html}
        </div>""", unsafe_allow_html=True)

        # ── Stats cards ──
        total_admin = len(df_admin)
        total_kas_n = len(df_kas)

        for icon, label, value in [
            ("👥", "Total Admin",    f"{total_admin} Active"),
            ("🛡️", "New Requests",  "03 Pending"),
            ("📊", "System Uptime", "99.9%"),
        ]:
            card(f"""
            <div style="display:flex;align-items:center;gap:1rem;">
                <div style="width:44px;height:44px;background:#0A1A50;border-radius:12px;
                            display:flex;align-items:center;justify-content:center;
                            font-size:20px;flex-shrink:0;">{icon}</div>
                <div>
                    <div style="font-size:12px;color:#7B82C4;margin-bottom:2px;">{label}</div>
                    <div style="font-size:18px;font-weight:800;color:#FFFFFF;">{value}</div>
                </div>
            </div>""", mb=".6rem")

        # Hapus admin by ID
        st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
        with st.expander("🗑️ Hapus akun admin"):
            if not df_admin.empty:
                del_id = st.number_input("ID akun", min_value=1, step=1, key="del_adm")
                if st.button("Hapus akun", key="btn_del_adm"):
                    cursor.execute("DELETE FROM admin_accounts WHERE id=?", (int(del_id),))
                    conn.commit()
                    st.success(f"Akun ID {int(del_id)} dihapus.")
                    st.rerun()

    elif nav == "history":
        section_title("Semua Data Kas")
        if df_kas.empty:
            st.info("Belum ada data kas.")
        else:
            st.dataframe(df_kas, use_container_width=True, hide_index=True)
            st.download_button("⬇ Download PDF",
                gen_pdf(df_kas, "Semua Data Kas"), "kas_all.pdf", mime="application/pdf")

    bottom_nav(nav)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Dashboard", key="dev_db"):
            st.session_state.subnav = "dashboard"; st.rerun()
    with c2:
        if st.button("History",   key="dev_hs"):
            st.session_state.subnav = "history";   st.rerun()
    with c3:
        if st.button("Logout",    key="dev_lo"):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()

# ──────────────────────────────────────────────
# ROUTER
# ──────────────────────────────────────────────
p = st.session_state.page

if   p == "role":        page_role()
elif p == "login_admin": page_login_admin()
elif p == "login_dev":   page_login_dev()
elif p == "admin":       page_admin()
elif p == "user":        page_user()
elif p == "dev":         page_dev()
else:
    st.session_state.page = "role"
    st.rerun()
