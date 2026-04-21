import streamlit as st
import pandas as pd
import hashlib
import requests

# ================= CONFIG =================
st.set_page_config(page_title="KAS KITA", layout="wide")

API_URL = "https://script.google.com/macros/s/AKfycbwDTFrVRp4LuLnwG_OAyBH4KefKfkwilzRfOlYcArMHZvK6uqV6cUvih_VQ1kVrKgr4/exec"

# ================= HELPER =================
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def api_get(table):
    try:
        res = requests.get(API_URL, params={
            "action": "get",
            "table": table
        })
        data = res.json()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"API GET ERROR: {e}")
        return pd.DataFrame()

def api_post(table, data):
    try:
        res = requests.post(API_URL, json={
            "action": "insert",
            "table": table,
            "data": data
        })

        # DEBUG WAJIB
        st.write("STATUS:", res.status_code)
        st.write("RESPONSE:", res.text)

    except Exception as e:
        st.error(f"POST ERROR: {e}")

# ================= SESSION =================
if "login" not in st.session_state:
    st.session_state.login = False

# ================= AUTH =================
if not st.session_state.login:

    st.title("💰 KAS KITA")

    tab1, tab2 = st.tabs(["Login", "Register"])

    # ================= LOGIN =================
    with tab1:
        st.subheader("Login")

        user = st.text_input("Username", key="login_user")
        pw = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):

            df = api_get("admin")

            st.write("DATA ADMIN:", df)  # DEBUG

            if df.empty:
                st.error("Data admin kosong / API gagal")
            else:
                data = df[
                    (df["username"] == user) &
                    (df["password"] == hash_password(pw))
                ]

                st.write("HASIL LOGIN:", data)  # DEBUG

                if not data.empty:
                    st.session_state.login = True
                    st.success("Login berhasil")
                    st.rerun()
                else:
                    st.error("Username / password salah")

    # ================= REGISTER =================
    with tab2:
        st.subheader("Register")

        user = st.text_input("Username Baru", key="reg_user")
        pw = st.text_input("Password Baru", type="password", key="reg_pass")

        if st.button("Daftar"):

            data = {
                "username": user,
                "password": hash_password(pw),
                "email": "-",
                "kelas": "-",
                "jurusan": "-"
            }

            api_post("admin", data)

            st.success("Akun berhasil dibuat (cek spreadsheet)")

# ================= MAIN APP =================
else:

    st.title("📊 Dashboard KAS")

    df = api_get("kas")

    if not df.empty:
        st.dataframe(df)
    else:
        st.warning("Belum ada data kas")

st.subheader("➕ Tambah Data Kas")

col1, col2 = st.columns(2)

with col1:
    nama = st.text_input("Nama")
    tanggal = st.date_input("Tanggal")
    status = st.selectbox("Status", ["Tepat Waktu", "Telat"])
    kelas = st.text_input("Kelas")

with col2:
    jurusan = st.text_input("Jurusan")
    keterangan = st.text_input("Keterangan")
    nominal = st.number_input("Nominal", min_value=0)

if st.button("Simpan Data"):

    data = {
        "nama": nama,
        "tanggal": str(tanggal),
        "status": status,
        "kelas": kelas,
        "jurusan": jurusan,
        "keterangan": keterangan,
        "nominal": int(nominal)
    }

    api_post("kas", data)

    st.success("Data berhasil disimpan")
    st.rerun()

    nama = st.text_input("Nama")

    if st.button("Tambah Data"):
        data = {
            "nama": nama,
            "tanggal": "",
            "status": "",
            "kelas": "",
            "jurusan": "",
            "keterangan": "",
            "nominal": 0
        }

        api_post("kas", data)

        st.success("Data berhasil ditambahkan")
        st.rerun()

    st.subheader("Logout")

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
