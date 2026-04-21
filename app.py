import streamlit as st
import pandas as pd
import hashlib
import requests
import io
from datetime import date

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

# ================= CONFIG =================
st.set_page_config(
    page_title="KAS KITA",
    page_icon="icon.png",
    layout="wide"
)

API_URL = "https://script.google.com/macros/s/AKfycbx-e8pKl7d42dmKU0cIwcXKAo9Y-JiMRt0UYpIgqZEWNCZ1A7rNfW1Nc0upWYJq1_n4/exec"

DEV_USER = "developer"
DEV_PASS = "kaskita"

# ================= HELPER =================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def format_rupiah(angka):
    return "Rp.{:,.0f}".format(int(angka)).replace(",", ".")

def clean_nominal(n):
    if not n:
        return 0
    n = str(n).lower().replace("rp", "").replace(".", "").replace(",", "")
    return int(n) if n.isdigit() else 0

# ================= API =================
def api_get(table):
    try:
        res = requests.get(API_URL, params={"action":"get","table":table})
        return pd.DataFrame(res.json())
    except:
        return pd.DataFrame()

def api_post(table, data):
    requests.post(API_URL, json={
        "action":"insert",
        "table":table,
        "data":data
    })

def api_delete(table, id):
    requests.post(API_URL, json={
        "action":"delete",
        "table":table,
        "id":id
    })

def api_update(table, data):
    requests.post(API_URL, json={
        "action":"update",
        "table":table,
        "data":data
    })

# ================= PDF =================
def generate_pdf(df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)

    data = [df.columns.tolist()] + df.values.tolist()

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('GRID',(0,0),(-1,-1),1,colors.black)
    ]))

    doc.build([table])
    buffer.seek(0)
    return buffer

# ================= SESSION =================
defaults = {
    "login": False,
    "role": None,
    "kelas": None,
    "jurusan": None,
}

for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ================= LOGIN PAGE =================
if not st.session_state.login:

    st.title("💰 KAS KITA")

    tab1, tab2, tab3 = st.tabs(["Login", "Register", "Reset Password"])

    # ===== LOGIN =====
    with tab1:
        role = st.selectbox("Login sebagai", ["Admin", "Developer"])

        if role == "Admin":
            user = st.text_input("Username")
            pw = st.text_input("Password", type="password")
            kelas = st.selectbox("Kelas", ["10","11","12"])
            jurusan = st.text_input("Jurusan")

            if st.button("Login"):
                df = api_get("admin")

                if not df.empty:
                    data = df[
                        (df["username"] == user) &
                        (df["password"] == hash_password(pw))
                    ]

                    if not data.empty:
                        st.session_state.login = True
                        st.session_state.role = "admin"
                        st.session_state.kelas = kelas
                        st.session_state.jurusan = jurusan.upper()
                        st.rerun()
                    else:
                        st.error("Login gagal")

        else:
            user = st.text_input("Username Developer")
            pw = st.text_input("Password Developer", type="password")

            if st.button("Login Dev"):
                if user == DEV_USER and pw == DEV_PASS:
                    st.session_state.login = True
                    st.session_state.role = "dev"
                    st.rerun()
                else:
                    st.error("Login gagal")

    # ===== REGISTER =====
    with tab2:
        st.subheader("Register Admin")

        user = st.text_input("Username Baru")
        pw = st.text_input("Password Baru", type="password")
        email = st.text_input("Email")
        kelas = st.selectbox("Kelas", ["10","11","12"])
        jurusan = st.text_input("Jurusan")

        if st.button("Daftar"):
            data = {
                "username": user,
                "password": hash_password(pw),
                "email": email,
                "kelas": kelas,
                "jurusan": jurusan.upper()
            }
            api_post("admin", data)
            st.success("Akun berhasil dibuat")

    # ===== RESET =====
    with tab3:
        user = st.text_input("Username")
        email = st.text_input("Email")
        new_pass = st.text_input("Password Baru", type="password")

        if st.button("Reset Password"):
            df = api_get("admin")

            data = df[
                (df["username"] == user) &
                (df["email"] == email)
            ]

            if not data.empty:
                id_user = data.iloc[0]["id"]

                api_update("admin", {
                    "id": int(id_user),
                    "password": hash_password(new_pass)
                })

                st.success("Password berhasil diubah")
            else:
                st.error("Data tidak ditemukan")

# ================= MAIN APP =================
else:

    st.title("📊 Dashboard KAS")

    # ===== ADMIN =====
    if st.session_state.role == "admin":

        st.success(f"Kelas {st.session_state.kelas} - {st.session_state.jurusan}")

        menu = st.radio("Menu", ["Dashboard","Pengeluaran"])

        df = api_get("kas")

        if not df.empty:
            df["nominal"] = df["nominal"].astype(int)

        # ===== DASHBOARD =====
        if menu == "Dashboard":

            st.subheader("➕ Input Kas")

            nama = st.text_input("Nama")
            tgl = st.date_input("Tanggal")
            status = st.selectbox("Status", ["Tepat Waktu","Telat"])
            ket = st.text_input("Keterangan")
            nom = st.text_input("Nominal")

            if st.button("Simpan"):
                data = {
                    "nama": nama,
                    "tanggal": tgl.strftime("%Y-%m-%d"),
                    "status": status,
                    "kelas": st.session_state.kelas,
                    "jurusan": st.session_state.jurusan,
                    "keterangan": ket,
                    "nominal": clean_nominal(nom)
                }
                api_post("kas", data)
                st.success("Tersimpan")
                st.rerun()

            if not df.empty:
                df = df[
                    (df["kelas"] == st.session_state.kelas) &
                    (df["jurusan"] == st.session_state.jurusan)
                ]

                st.metric("Total Kas", format_rupiah(df["nominal"].sum()))
                st.bar_chart(df["status"].value_counts())

                st.dataframe(df)

                st.download_button("Download PDF", generate_pdf(df), "kas.pdf")

                # HAPUS
                id_hapus = st.number_input("ID Hapus", step=1)
                if st.button("Hapus Data"):
                    api_delete("kas", int(id_hapus))
                    st.rerun()

        # ===== PENGELUARAN =====
        elif menu == "Pengeluaran":

            st.subheader("💸 Input Pengeluaran")

            tgl = st.date_input("Tanggal")
            ket = st.text_input("Keterangan")
            nom = st.text_input("Nominal")

            if st.button("Simpan Pengeluaran"):
                data = {
                    "tanggal": tgl.strftime("%Y-%m-%d"),
                    "kelas": st.session_state.kelas,
                    "jurusan": st.session_state.jurusan,
                    "keterangan": ket,
                    "nominal": clean_nominal(nom)
                }
                api_post("pengeluaran", data)
                st.rerun()

            df_keluar = api_get("pengeluaran")

            if not df_keluar.empty:
                df_keluar["nominal"] = df_keluar["nominal"].astype(int)

                total_keluar = df_keluar["nominal"].sum()
                total_masuk = df["nominal"].sum() if not df.empty else 0
                saldo = total_masuk - total_keluar

                col1,col2,col3 = st.columns(3)
                col1.metric("Kas", format_rupiah(total_masuk))
                col2.metric("Pengeluaran", format_rupiah(total_keluar))
                col3.metric("Saldo", format_rupiah(saldo))

                st.dataframe(df_keluar)

    # ===== DEV =====
    elif st.session_state.role == "dev":

        st.subheader("🛠️ Developer Panel")

        st.dataframe(api_get("admin"))
        st.dataframe(api_get("kas"))
        st.dataframe(api_get("pengeluaran"))

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
