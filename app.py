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

            # DOWNLOAD PDF (tetap ada)
            pdf = generate_pdf(df_filter)
            st.download_button("⬇️ Download PDF", pdf, "data_kas_user.pdf")

        else:
            st.warning("Data tidak ditemukan")

    else:
        st.info("Belum ada data kas")
