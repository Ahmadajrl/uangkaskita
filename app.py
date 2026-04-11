# ================= USER =================
elif st.session_state.role == "user":

    st.subheader("📋 Data Pembayaran")

    df = pd.read_sql("SELECT * FROM kas", conn)

    if not df.empty:
        df["tanggal"] = pd.to_datetime(df["tanggal"]).dt.strftime("%Y-%m-%d")
        df["bulan"] = pd.to_datetime(df["tanggal"]).dt.strftime("%B %Y")

        # ===== PISAH PER JURUSAN =====
        for jurusan in sorted(df["jurusan"].dropna().unique()):
            st.header(f"🎓 Jurusan {jurusan}")

            df_jurusan = df[df["jurusan"] == jurusan]

            # ===== PISAH PER BULAN =====
            for bulan in sorted(df_jurusan["bulan"].unique()):
                st.subheader(f"📅 {bulan}")
                st.dataframe(df_jurusan[df_jurusan["bulan"] == bulan])

    else:
        st.info("Belum ada data")
