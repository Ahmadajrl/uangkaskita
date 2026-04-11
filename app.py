# ======================
# MAIN APP
# ======================
else:

    st.title("📊 Dashboard KAS")

    # ================= ADMIN =================
    if st.session_state.role == "admin":

        st.success(f"Kelas {st.session_state.kelas} - {st.session_state.jurusan}")

        colA, colB = st.columns(2)

        with colA:
            if st.button("📊 Dashboard"):
                st.session_state.menu = "dashboard"
                st.rerun()

        with colB:
            if st.button("💸 Input Pengeluaran"):
                st.session_state.menu = "pengeluaran"
                st.rerun()

        # ================= DASHBOARD =================
        if st.session_state.menu == "dashboard":

            st.subheader("➕ Input Pembayaran")

            nama = st.text_input("Nama Siswa")
            tanggal = st.date_input("Tanggal")
            status = st.selectbox("Status", ["Tepat Waktu", "Telat"])
            keterangan = st.text_input("Keterangan")
            nominal = st.text_input("Nominal (bebas)")

            if st.button("Simpan"):
                nilai = clean_nominal(nominal)

                cursor.execute(
                    "INSERT INTO kas VALUES (NULL,?,?,?,?,?,?,?)",
                    (nama, tanggal.strftime("%Y-%m-%d"), status,
                     st.session_state.kelas,
                     st.session_state.jurusan,
                     keterangan,
                     nilai)
                )
                conn.commit()
                st.success("Data tersimpan")
                st.rerun()

            df = pd.read_sql(
                "SELECT * FROM kas WHERE kelas=? AND jurusan=?",
                conn,
                params=(st.session_state.kelas, st.session_state.jurusan)
            )

            if not df.empty:
                df["tanggal"] = pd.to_datetime(df["tanggal"]).dt.strftime("%Y-%m-%d")
                df["bulan"] = pd.to_datetime(df["tanggal"]).dt.strftime("%B %Y")

                total = df["nominal"].sum()
                st.metric("💰 Total Kas", format_rupiah(total))

        # ================= PENGELUARAN =================
        elif st.session_state.menu == "pengeluaran":

            st.subheader("💸 Input Pengeluaran")

            tgl = st.date_input("Tanggal")
            keterangan = st.text_input("Keterangan Pengeluaran")
            nominal = st.text_input("Nominal Pengeluaran")

            if st.button("Simpan Pengeluaran"):
                nilai = clean_nominal(nominal)

                cursor.execute(
                    "INSERT INTO pengeluaran VALUES (NULL,?,?,?,?,?)",
                    (
                        tgl.strftime("%Y-%m-%d"),
                        st.session_state.kelas,
                        st.session_state.jurusan,
                        keterangan,
                        nilai
                    )
                )
                conn.commit()
                st.success("Pengeluaran berhasil disimpan")
                st.rerun()

            df_masuk = pd.read_sql(
                "SELECT * FROM kas WHERE kelas=? AND jurusan=?",
                conn,
                params=(st.session_state.kelas, st.session_state.jurusan)
            )

            df_keluar = pd.read_sql(
                "SELECT * FROM pengeluaran WHERE kelas=? AND jurusan=?",
                conn,
                params=(st.session_state.kelas, st.session_state.jurusan)
            )

            total_masuk = df_masuk["nominal"].sum() if not df_masuk.empty else 0
            total_keluar = df_keluar["nominal"].sum() if not df_keluar.empty else 0
            saldo = total_masuk - total_keluar

            col1, col2, col3 = st.columns(3)
            col1.metric("💰 Total Kas", format_rupiah(total_masuk))
            col2.metric("💸 Total Pengeluaran", format_rupiah(total_keluar))
            col3.metric("🧮 Saldo Sekarang", format_rupiah(saldo))

            st.subheader("📋 Riwayat Pengeluaran")

            if not df_keluar.empty:
                df_keluar["tanggal"] = pd.to_datetime(df_keluar["tanggal"]).dt.strftime("%Y-%m-%d")
                st.dataframe(df_keluar)

                pdf = generate_pdf(df_keluar)
                st.download_button("⬇️ Download PDF Pengeluaran", pdf, "pengeluaran.pdf")
            else:
                st.info("Belum ada pengeluaran")

    # ================= USER =================
    elif st.session_state.role == "user":

        st.subheader("📋 Data Kas Siswa")

        df = pd.read_sql("SELECT * FROM kas", conn)

        if not df.empty:
            df["tanggal"] = pd.to_datetime(df["tanggal"])
            df["bulan"] = df["tanggal"].dt.strftime("%B %Y")

            col1, col2 = st.columns(2)

            with col1:
                jurusan_list = sorted(df["jurusan"].dropna().unique())
                pilih_jurusan = st.selectbox("🎓 Pilih Jurusan", jurusan_list)

            with col2:
                bulan_list = sorted(df["bulan"].unique())
                pilih_bulan = st.selectbox("📅 Pilih Bulan", bulan_list)

            df_filter = df[
                (df["jurusan"] == pilih_jurusan) &
                (df["bulan"] == pilih_bulan)
            ]

            if not df_filter.empty:
                df_filter["tanggal"] = df_filter["tanggal"].dt.strftime("%Y-%m-%d")
                st.dataframe(df_filter)

                pdf = generate_pdf(df_filter)
                st.download_button("⬇️ Download PDF", pdf, "data_kas_user.pdf")
            else:
                st.warning("Data tidak ditemukan")

        else:
            st.info("Belum ada data kas")

    # ================= DEV =================
    elif st.session_state.role == "dev":

        st.subheader("🛠️ Developer Mode")
        st.dataframe(pd.read_sql("SELECT * FROM kas", conn))
        st.dataframe(pd.read_sql("SELECT * FROM admin", conn))

    # ================= LOGOUT =================
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
