import streamlit as st
import pandas as pd
import sqlite3
import io

# ======================
# PDF GENERATOR
# ======================
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

def generate_pdf(df, title="Laporan KasKita"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    styles = getSampleStyleSheet()
    elements = []

    # Judul
    elements.append(Paragraph(f"<b>{title}</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    # Data tabel
    data = [df.columns.tolist()] + df.values.tolist()
    table = Table(data, repeatRows=1)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#01023B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#09F289")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),

        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3FDF9")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1FAE5")),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#01023B")),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("© KasKita 2026", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)

    return buffer

# ======================
# SESSION STATE (HARUS DI ATAS)
# ======================
defaults = {
    "login": False,
    "role": None,
    "kelas": None,
    "jurusan": None,
    "page": "role",
    "menu": "dashboard"
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v
# ======================
# DATABASE
# ======================
conn = sqlite3.connect("kas.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS kas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT,
    tanggal TEXT,
    status TEXT,
    kelas TEXT,
    jurusan TEXT,
    keterangan TEXT,
    nominal INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    email TEXT,
    kelas TEXT,
    jurusan TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS pengeluaran (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT,
    kelas TEXT,
    jurusan TEXT,
    keterangan TEXT,
    nominal INTEGER
)
''')

conn.commit()
# ======================
# HELPER
# ======================
def format_rupiah(angka):
    return "Rp {:,}".format(int(angka)).replace(",", ".")

def hdivider():
    st.markdown("""---""", unsafe_allow_html=True)

def page_header(title, subtitle=None):
    st.title(title)
    if subtitle:
        st.caption(subtitle)

# ======================
# SIDEBAR UI
# ======================
def render_logo_sidebar():
    st.markdown("""💳 KasKita""", unsafe_allow_html=True)

def info_badge_sidebar(text, color="#09F289", bg="rgba(9,242,137,0.12)"):
    st.markdown(f"""{text}""", unsafe_allow_html=True)

def sidebar_label(text):
    st.markdown(f""" {text}""", unsafe_allow_html=True)

def sidebar_sep():
    st.markdown("""---""", unsafe_allow_html=True)

def sidebar_user(text):
    st.markdown(f"""👤 {text}""", unsafe_allow_html=True)

DEV_USER = "developer"
DEV_PASS = "kaskita"

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
                    <rect x="2" y="6" width="18" height="11" rx="2.5"
                          stroke="#09F289" stroke-width="1.7"/>
                    <path d="M2 9.5h18" stroke="#09F289" stroke-width="1.7"/>
                    <rect x="4.5" y="12" width="6" height="2"
                          rx="0.6" fill="#09F289"/>
                </svg>
            </div>

            <div style="text-align:left;">
                <div style="font-size:28px;font-weight:700;color:#01023B;line-height:1.1;">
                    KasKita
                </div>
                <div style="font-size:12px;color:#6B7280;">
                    Manajemen kas kelas digital
                </div>
            </div>

        </div>

        <p style="font-size:14px;color:#6B7280;margin-top:0.75rem;">
            Pilih peran untuk melanjutkan
        </p>

    </div>
    """, unsafe_allow_html=True)

    _, col1, col2, _ = st.columns([1, 1.1, 1.1, 1])

    # ================= ADMIN CARD =================
    with col1:
        st.markdown("""
        <div style="background:#FFFFFF;border:1px solid #D1FAE5;border-radius:14px;
                    padding:1.5rem;text-align:center;margin-bottom:10px;">

            <div style="width:48px;height:48px;background:#E6FDF5;border-radius:12px;
                        display:flex;align-items:center;justify-content:center;margin:0 auto 12px;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="8" r="4" stroke="#01023B" stroke-width="1.6"/>
                    <path d="M4 20c0-4 3.582-7 8-7s8 3 8 7"
                          stroke="#01023B" stroke-width="1.6" stroke-linecap="round"/>
                </svg>
            </div>

            <div style="font-size:15px;font-weight:500;color:#01023B;">
                Admin
            </div>

            <div style="font-size:11px;color:#6B7280;margin-top:4px;">
                Kelola kas kelas
            </div>

        </div>
        """, unsafe_allow_html=True)

        if st.button("Masuk sebagai Admin", key="btn_admin", type="primary", use_container_width=True):
            st.session_state.role = "admin"
            st.session_state.page = "login"
            st.rerun()

    # ================= USER CARD =================
    with col2:
        st.markdown("""
        <div style="background:#FFFFFF;border:1px solid #D1FAE5;border-radius:14px;
                    padding:1.5rem;text-align:center;margin-bottom:10px;">

            <div style="width:48px;height:48px;background:#E6FDF5;border-radius:12px;
                        display:flex;align-items:center;justify-content:center;margin:0 auto 12px;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M4 6h16M4 10h16M4 14h10"
                          stroke="#01023B" stroke-width="1.6" stroke-linecap="round"/>
                </svg>
            </div>

            <div style="font-size:15px;font-weight:500;color:#01023B;">
                User
            </div>

            <div style="font-size:11px;color:#6B7280;margin-top:4px;">
                Lihat data kas
            </div>

        </div>
        """, unsafe_allow_html=True)

        if st.button("Masuk sebagai User", key="btn_user", type="primary", use_container_width=True):
            st.session_state.role = "user"
            st.session_state.login = True
            st.rerun()

    st.markdown("""<div style='height:1rem'></div>""", unsafe_allow_html=True)

    # ================= DEV LOGIN =================
    _, mid, _ = st.columns([1, 2, 1])

    with mid:
        with st.expander("🔧 Login Developer"):
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
        <div style="font-size:22px;font-weight:600;color:#01023B;">
            Login Admin
        </div>
        <div style="font-size:13px;color:#6B7280;margin-top:4px;">
            Masukkan detail akun kelas kamu
        </div>
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

        st.markdown("""<div style='height:6px'></div>""", unsafe_allow_html=True)

        if st.button("Masuk ke Dashboard →", type="primary", use_container_width=True):
            if not jurusan.strip():
                st.warning("Jurusan tidak boleh kosong.")
            else:
                st.session_state.login = True
                st.session_state.kelas = kelas
                st.session_state.jurusan = jurusan.upper()
                st.rerun()

        st.markdown("""</div>""", unsafe_allow_html=True)

        st.markdown("""<div style='height:8px'></div>""", unsafe_allow_html=True)

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

                fk = st.selectbox("Kelas", sorted(df_all["kelas"].unique()))
                fj = st.selectbox("Jurusan", sorted(df_all["jurusan"].unique()))
                fb = st.selectbox("Bulan", sorted(df_all["bulan"].unique()))

        with st.sidebar:
            sidebar_sep()
            sidebar_user("User Publik")
            st.markdown("""<div style='height:8px'></div>""", unsafe_allow_html=True)

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
            m2.metric("Jumlah transaksi", f"{len(df)}")
            m3.metric("Pembayaran telat", f"{len(df[df['status'] == 'Telat'])} siswa")

            st.markdown("""<div style='height:8px'></div>""", unsafe_allow_html=True)

            tab1, tab2 = st.tabs(["📋 Tabel data", "📊 Statistik"])

            with tab1:
                st.dataframe(
                    df.drop(columns=["bulan"], errors="ignore"),
                    use_container_width=True,
                    hide_index=True
                )

                st.download_button(
                    "⬇ Download PDF",
                    generate_pdf(
                        df.drop(columns=["bulan"], errors="ignore"),
                        f"Laporan Kas {fk} {fj} — {fb}"
                    ),
                    f"kas_{fk}_{fj}.pdf",
                    mime="application/pdf"
                )

            with tab2:
                st.markdown("""Status pembayaran""", unsafe_allow_html=True)
                st.bar_chart(df["status"].value_counts())

    # ==================== DEVELOPER ====================
    elif st.session_state.role == "dev":

        with st.sidebar:
            render_logo_sidebar()
            info_badge_sidebar("Developer Panel", "#EF9F27", "rgba(239,159,39,0.15)")
            sidebar_label("Menu")

            menu_dev = st.radio(
                "",
                ["Akun Admin", "Semua Data Kas"],
                label_visibility="collapsed"
            )

            sidebar_sep()
            sidebar_user("Developer")

            st.markdown("""<div style='height:8px'></div>""", unsafe_allow_html=True)

            if st.button("Keluar", use_container_width=True):
                st.session_state.clear()
                st.rerun()

        page_header("Developer panel", "Manajemen sistem KasKita")

        df_admin = pd.read_sql("SELECT * FROM admin", conn)
        df_kas = pd.read_sql("SELECT * FROM kas", conn)

        # ===== AKUN ADMIN =====
        if menu_dev == "Akun Admin":

            st.markdown(
                """<div style='font-size:14px;font-weight:500;color:#01023B;margin-bottom:.75rem;'>"
                "Daftar akun admin</div>""",
                unsafe_allow_html=True
            )

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

            hdivider()

            st.markdown("""Hapus akun berdasarkan ID""", unsafe_allow_html=True)
            id_del = st.number_input("ID akun", min_value=1, step=1)

            if st.button("""Hapus akun", type="primary"""):
                cursor.execute("DELETE FROM admin WHERE id=?", (int(id_del),))
                conn.commit()
                st.success(f"Akun ID {int(id_del)} berhasil dihapus.")
                st.rerun()

        # ===== SEMUA DATA KAS =====
        else:

            st.markdown("""
                "<div style='font-size:14px;font-weight:500;color:#01023B;margin-bottom:.75rem;'>"
                "Semua data kas</div>",
                unsafe_allow_html=True """, unsafe_allow_html=True
            )

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
