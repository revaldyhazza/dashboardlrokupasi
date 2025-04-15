import streamlit as st
st.set_page_config(
    page_title="Dashboard Analisa LR by Kategori Okupasi",
    page_icon="📊",
    layout="wide",
)

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Header dan instruksi
st.markdown("# 📊 Dashboard Analisa Loss Ratio Berdasarkan Kategori Okupasi")
st.markdown("""
    <div style='text-align: justify'>
    📍 Untuk pengalaman yang lebih baik, tutup kembali sidebar setelah mengaplikasikan filter dan 
    membuat tampilan menjadi wide mode. Direkomendasikan juga untuk membuka menggunakan Laptop/PC
    </div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)


# Fungsi untuk baca dan bersihkan file Excel
def read_excel(file):
    df = pd.read_excel(file)
    df = df.drop(columns=[col for col in df.columns if str(col).startswith("Unnamed")])
    return df

# Upload dan preview data
# 1. Premi
file_premi = st.file_uploader("📂 Upload Data Premi (Excel)", type="xlsx", key="premi")
if file_premi:
    df_premi = read_excel(file_premi)
    df_premi['Sumber Data'] = 'Premi'
    st.write("### 1️⃣ Preview Data Premi")
    st.info(f"🔍 Data Premi memiliki **{len(df_premi):,} baris.**")
    st.dataframe(df_premi.head(), hide_index=True)

# 2. Klaim
file_klaim = st.file_uploader("📂 Upload Data Klaim (Excel)", type="xlsx", key="klaim")
if file_klaim:
    df_klaim = read_excel(file_klaim)
    df_klaim['Sumber Data'] = 'Klaim'
    st.write("### 2️⃣ Preview Data Klaim")
    st.info(f"🔍 Data Klaim memiliki **{len(df_klaim):,} baris.**")
    st.dataframe(df_klaim.head(), hide_index=True)

# 3. OS Klaim
file_os = st.file_uploader("📂 Upload Data Outstanding Klaim (Excel)", type="xlsx", key="os")
if file_os:
    df_os_klaim = read_excel(file_os)
    df_os_klaim['Sumber Data'] = 'OS Klaim'
    st.write("### 3️⃣ Preview Data Outstanding Klaim")
    st.info(f"🔍 Data OS Klaim memiliki **{len(df_os_klaim):,} baris.**")
    st.dataframe(df_os_klaim.head(), hide_index=True)

# Daftar kolom
desired_columns = [
    'AY', 'UY', 'TOC_MOD', 'Kategori Okupasi', 'Kategori Risiko Okupasi',
    'INSURED NAME', 'NO POLIS', 'NO SERTIFIKAT', 'NO KLAIM',
    'INCEPTION DATE', 'EXPIRY DATE', 'Sumber Data'
]
additional_columns = [
    'Premi Gross', 'Akuisisi', 'Premi Reas', 'Komisi Reas',
    'Paid Claim', 'Recovery Klaim Reas', 'OS Claim', 'Recovery OS Claim Reas'
]
key_columns = [
    'AY', 'UY', 'TOC_MOD', 'Kategori Okupasi', 'Kategori Risiko Okupasi',
    'INSURED NAME', 'NO POLIS', 'NO SERTIFIKAT', 'NO KLAIM',
    'INCEPTION DATE', 'EXPIRY DATE', 'Sumber Data'
]

# Proses data jika semua file diunggah
if file_premi and file_klaim and file_os:
    # Rename kolom
    df_premi = df_premi.rename(columns={
        'PREMI IDR': 'Premi Gross',
        'AKUISISI': 'Akuisisi',
        'PREMI REAS IDR': 'Premi Reas',
        'KOMISI REAS IDR': 'Komisi Reas'
    })
    df_klaim = df_klaim.rename(columns={
        'CLAIM AMOUNT (IDR)': 'Paid Claim',
        'KLAIM REAS': 'Recovery Klaim Reas'
    })
    df_os_klaim = df_os_klaim.rename(columns={
        'Gross OS Klaim': 'OS Claim',
        'Reas': 'Recovery OS Claim Reas'
    })

    # Gabungkan dataframe
    df_combined = pd.concat([df_premi, df_klaim, df_os_klaim], ignore_index=True)

    # Normalisasi key columns untuk deduplikasi
    for col in key_columns:
        if col in df_combined.columns:
            df_combined[col] = df_combined[col].astype(str).str.strip()
            df_combined[col] = df_combined[col].replace(['nan', 'None'], pd.NA)

    # Tambahkan kolom tambahan jika tidak ada
    for col in additional_columns:
        if col not in df_combined.columns:
            df_combined[col] = pd.NA

    # Deduplikasi
    df_combined = df_combined.drop_duplicates(subset=key_columns, keep='first')
    st.info(f"🔍 Data gabungan setelah deduplikasi memiliki **{len(df_combined):,} baris.**")

    # Pilih kolom yang diinginkan
    final_columns = [col for col in desired_columns if col in df_combined.columns] + additional_columns
    df_combined = df_combined[final_columns]
    df_combined = df_combined.rename(columns={"TOC_MOD": "TOC"})

    # Konversi kolom tanggal
    df_combined['INCEPTION DATE'] = pd.to_datetime(df_combined['INCEPTION DATE'], errors='coerce')
    df_combined['EXPIRY DATE'] = pd.to_datetime(df_combined['EXPIRY DATE'], errors='coerce')

    # Sidebar untuk filter
    st.sidebar.header("Filter Data")

    # Filter TOC
    toc_options = sorted(df_combined['TOC'].dropna().unique())
    selected_toc = st.sidebar.multiselect("Pilih TOC", toc_options)

    # Filter Kategori Okupasi
    kategori_okupasi_options = sorted(df_combined['Kategori Okupasi'].dropna().unique())
    selected_kategori_okupasi = st.sidebar.multiselect("Pilih Kategori Okupasi", kategori_okupasi_options)

    # Filter Kategori Risiko Okupasi
    risiko_okupasi_options = sorted(df_combined['Kategori Risiko Okupasi'].dropna().unique())
    selected_risiko_okupasi = st.sidebar.multiselect("Pilih Kategori Risiko Okupasi", risiko_okupasi_options)

    # Filter Date Range
    st.sidebar.subheader("Pilih Rentang Tanggal")
    date_filter = st.sidebar.radio("Filter Berdasarkan", ["INCEPTION DATE", "EXPIRY DATE"])
    min_date = min(df_combined[date_filter].min(), df_combined[date_filter].min())
    max_date = max(df_combined[date_filter].max(), df_combined[date_filter].max())
    date_range = st.sidebar.date_input("Pilih Rentang Tanggal", [], min_value=min_date, max_value=max_date)

    # Terapkan filter
    filtered_df = df_combined.copy()
    if selected_toc:
        filtered_df = filtered_df[filtered_df['TOC'].isin(selected_toc)]
    if selected_kategori_okupasi:
        filtered_df = filtered_df[filtered_df['Kategori Okupasi'].isin(selected_kategori_okupasi)]
    if selected_risiko_okupasi:
        filtered_df = filtered_df[filtered_df['Kategori Risiko Okupasi'].isin(selected_risiko_okupasi)]
    if date_range and len(date_range) == 2:
        start_date, end_date = date_range
        if date_filter == "INCEPTION DATE":
            filtered_df = filtered_df[
                (filtered_df['INCEPTION DATE'] >= pd.to_datetime(start_date)) &
                (filtered_df['INCEPTION DATE'] <= pd.to_datetime(end_date))
            ]
        else:
            filtered_df = filtered_df[
                (filtered_df['EXPIRY DATE'] >= pd.to_datetime(start_date)) &
                (filtered_df['EXPIRY DATE'] <= pd.to_datetime(end_date))
            ]

    # Format tanggal untuk display
    filtered_df_display = filtered_df.copy()
    if 'INCEPTION DATE' in filtered_df_display.columns:
        filtered_df_display['INCEPTION DATE'] = filtered_df_display['INCEPTION DATE'].dt.strftime('%Y-%m-%d')
    if 'EXPIRY DATE' in filtered_df_display.columns:
        filtered_df_display['EXPIRY DATE'] = filtered_df_display['EXPIRY DATE'].dt.strftime('%Y-%m-%d')

    st.write("### Preview Data Gabungan (Setelah Deduplikasi)")
    st.dataframe(filtered_df_display, hide_index=True)
    st.info(f"🔍 Data yang ditampilkan memiliki **{len(filtered_df):,} baris.**")

    # Tabel summary berdasarkan UY
    st.write("### 📅 Summary Berdasarkan Underwriting Year (UY)")
    summary_columns = [
        'Premi Gross', 'Akuisisi', 'Premi Reas', 'Komisi Reas',
        'Paid Claim', 'Recovery Klaim Reas', 'OS Claim', 'Recovery OS Claim Reas'
    ]
    summary_df = filtered_df.groupby('UY')[summary_columns].sum().reset_index()
    summary_df = summary_df.sort_values('UY', ascending=True)
    summary_df = summary_df.reset_index(drop=True)
    summary_df.index = summary_df.index + 1

    # Hitung Grand Total
    grand_total = summary_df[summary_columns].sum()
    grand_total_df = pd.DataFrame([grand_total], columns=summary_columns, index=['Grand Total'])
    grand_total_df['UY'] = 'Grand Total'
    summary_df = pd.concat([summary_df, grand_total_df], ignore_index=True)

    # Format angka
    for col in summary_columns:
        summary_df[col] = summary_df[col].apply(lambda x: f"{x:,.2f}")

    st.dataframe(summary_df, hide_index=True)

    st.write("# 📈 Informasi dan Statistik Deskriptif Data")

    def simplify_number(value):
        if value >= 1e12:
            return f"{value / 1e12:.1f} T"
        elif value >= 1e9:
            return f"{value / 1e9:.1f} B"
        elif value >= 1e6:
            return f"{value / 1e6:.1f} M"
        else:
            return f"{value:,.0f}"

    st.dataframe(filtered_df_display, use_container_width=True)

    # Hitung premi_sev dan klaim_sev
    premi_sev = filtered_df_display.groupby("INSURED NAME")["Premi Gross"].sum().nlargest(10).reset_index()
    premi_sev.columns = ["Insuredname", "Severity"]
    klaim_sev = filtered_df_display.groupby("INSURED NAME")["Paid Claim"].sum().nlargest(10).reset_index()
    klaim_sev.columns = ["Claimant", "Severity"]
    premi_sev = premi_sev.sort_values(by="Severity", ascending=True).head(10)
    klaim_sev = klaim_sev.sort_values(by="Severity", ascending=True).head(10)
    premi_sev["Severity"] = premi_sev["Severity"].apply(simplify_number)
    klaim_sev["Severity"] = klaim_sev["Severity"].apply(simplify_number)

    # Frekuensi klaim
    valid_claims = filtered_df_display[filtered_df_display["NO KLAIM"].notna()]
    total_frequency = len(valid_claims)
    valid_claims["Incurred"] = (
        valid_claims["Paid Claim"].fillna(0) +
        valid_claims["OS Claim"].fillna(0) -
        valid_claims["Recovery Klaim Reas"].fillna(0)
    )
    incurred_average = valid_claims["Incurred"].mean()
    incurred_average = f"{incurred_average:,.0f}".replace(",", ".")

    # Layout kolom
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <style>
                .custom-title {
                    text-align: center;
                    margin-bottom: -20px;
                    position: relative;
                    top: 10px;
                }
            </style>
            <h4 class="custom-title">10 Sumber Pendapatan Premi Terbesar</h4>
        """, unsafe_allow_html=True)

        colors = [
            "#7a3300", "#a34700", "#cc5c00", "#e67300", "#ff8000",
            "#ff9933", "#ffb366", "#ffcc99", "#ffe0cc", "#fff5e6"
        ]
        fig1 = px.bar(
            premi_sev,
            x="Severity",
            y="Insuredname",
            orientation="h",
            text="Severity",
            color="Insuredname",
            color_discrete_sequence=colors
        )
        fig1.update_layout(
            width=900,
            height=500,
            margin=dict(l=250, r=50, t=10, b=50),
            font=dict(size=14),
            xaxis_title=None,
            yaxis_title=None,
            showlegend=False
        )
        fig1.update_traces(textposition="auto")
        st.plotly_chart(fig1)

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
            <style>
                .section-box {{
                    background-color: #f08522;
                    padding: 5px;
                    border-radius: 5px;
                    color: white;
                    font-weight: bold;
                    text-align: center;
                    margin-bottom: 5px;
                }}
                .value-box {{
                    background-color: white;
                    color: black;
                    padding: 5px;
                    border-radius: 5px;
                    font-size: 10px;
                    text-align: center;
                }}
            </style>
            <div class="section-box">
                <h2>Frekuensi Klaim</h2>
                <div class="value-box">
                    <h1>{total_frequency}</h1>
                </div>
            </div>
            <div class="section-box">
                <h2>Average Klaim Incurred</h2>
                <div class="value-box">
                    <h1>{incurred_average}</h1>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <style>
                .custom-title {
                    text-align: center;
                    margin-bottom: -20px;
                    position: relative;
                    top: 10px;
                }
            </style>
            <h4 class="custom-title">10 Penghasil Klaim Terbesar</h4>
        """, unsafe_allow_html=True)

        colors = [
            "#7a3300", "#a34700", "#cc5c00", "#e67300", "#ff8000",
            "#ff9933", "#ffb366", "#ffcc99", "#ffe0cc", "#fff5e6"
        ]
        fig2 = px.bar(
            klaim_sev,
            x="Severity",
            y="Claimant",
            orientation="h",
            text="Severity",
            color="Claimant",
            color_discrete_sequence=colors
        )
        fig2.update_layout(
            width=900,
            height=500,
            margin=dict(l=250, r=50, t=10, b=10),
            font=dict(size=14),
            xaxis_title="Premi",
            yaxis_title=None,
            showlegend=False
        )
        fig2.update_traces(textposition="auto")
        st.plotly_chart(fig2)

    st.subheader("💸 Summary by Premi")
    filtered_df_display["Premi Gross"] = pd.to_numeric(filtered_df_display["Premi Gross"], errors="coerce")
    filtered_df_display["Paid Claim"] = pd.to_numeric(filtered_df_display["Paid Claim"], errors="coerce")

    toc_premi = filtered_df_display.groupby(by=["TOC"], as_index=False)["Premi Gross"].sum()
    occupancy_premi = filtered_df_display.groupby(by=["Kategori Okupasi"], as_index=False)["Premi Gross"].sum()
    risklevel_premi = filtered_df_display.groupby(by=["Kategori Risiko Okupasi"], as_index=False)["Premi Gross"].sum()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <style>
                .custom-title {
                    text-align: center;
                    margin-bottom: -10px;
                    position: relative;
                    left: -30px; /* Geser ke kiri */
                    top: 0px;
                }
            </style>
            <h4 class="custom-title">TOC</h4>
        """, unsafe_allow_html=True)

        fig = px.pie(
            toc_premi,
            values="Premi Gross",
            names="TOC",
            hole=0.5,
            color_discrete_sequence=["#003087", "#4D8CFF", "#B3D1FF", "#E6F0FF"]
        )
        fig.update_traces(textinfo='percent', textposition='inside', textfont=dict(color='white'))
        fig.update_layout(
            width=400,
            height=250,
            margin=dict(l=10, r=10, t=10, b=10),
            font=dict(size=12),
            legend=dict(x=1, y=0.5, xanchor="left", yanchor="middle")
        )
        st.plotly_chart(fig)

    with col2:
        st.markdown("""
            <style>
                .custom-title {
                    text-align: center;
                    margin-bottom: -10px;
                    position: relative;
                    left: -30px; /* Geser ke kiri */
                    top: 0px;
                }
            </style>
            <h4 class="custom-title">Kategori Okupasi</h4>
        """, unsafe_allow_html=True)

        fig = px.pie(
            occupancy_premi,
            values="Premi Gross",
            names="Kategori Okupasi",
            hole=0.5,
            color_discrete_sequence=["#004d00", "#339933", "#66B266"]
        )
        fig.update_traces(textinfo='percent', textposition='inside', textfont=dict(color='white'))
        fig.update_layout(
            width=400,
            height=250,
            margin=dict(l=10, r=10, t=10, b=10),
            font=dict(size=12),
            legend=dict(x=1, y=0.5, xanchor="left", yanchor="middle")
        )
        st.plotly_chart(fig)

    with col3:
        st.markdown("""
            <style>
                .custom-title {
                    text-align: center;
                    margin-bottom: -10px;
                    position: relative;
                    top: 0px;
                }
            </style>
            <h4 class="custom-title">Risk Level</h4>
        """, unsafe_allow_html=True)

        risk_order = ['C', 'B', 'D', 'A']
        risklevel_premi['Kategori Risiko Okupasi'] = pd.Categorical(
            risklevel_premi['Kategori Risiko Okupasi'],
            categories=risk_order,
            ordered=True
        )
        risklevel_premi = risklevel_premi.sort_values('Kategori Risiko Okupasi')

        fig = px.pie(
            risklevel_premi,
            values="Premi Gross",
            names="Kategori Risiko Okupasi",
            hole=0.5,
            color_discrete_sequence=["#ff8000", "#a34700", "#cc5c00", "#7a3300"]
        )
        fig.update_traces(textinfo='percent', textposition='inside', textfont=dict(color='white'))
        fig.update_layout(
            width=400,
            height=250,
            margin=dict(l=10, r=10, t=10, b=10),
            font=dict(size=12),
            legend=dict(x=1, y=0.5, xanchor="left", yanchor="middle", traceorder='normal')
        )
        st.plotly_chart(fig)

    st.subheader("💣 Summary by Klaim")
    toc_klaim = filtered_df_display.groupby(by=["TOC"], as_index=False)["Paid Claim"].sum()
    occupancy_klaim = filtered_df_display.groupby(by=["Kategori Okupasi"], as_index=False)["Paid Claim"].sum()
    risklevel_klaim = filtered_df_display.groupby(by=["Kategori Risiko Okupasi"], as_index=False)["Paid Claim"].sum()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <style>
                .custom-title {
                    text-align: center;
                    margin-bottom: -10px;
                    position: relative;
                    top: 0px;
                }
            </style>
            <h4 class="custom-title">TOC</h4>
        """, unsafe_allow_html=True)

        fig = px.pie(
            toc_klaim,
            values="Paid Claim",
            names="TOC",
            hole=0.5,
            color_discrete_sequence=["#003087", "#4D8CFF", "#B3D1FF", "#E6F0FF"]
        )
        fig.update_traces(textinfo='percent', textposition='inside', textfont=dict(color='white'))
        fig.update_layout(
            width=400,
            height=250,
            margin=dict(l=10, r=10, t=10, b=10),
            font=dict(size=12),
            legend=dict(x=1, y=0.5, xanchor="left", yanchor="middle")
        )
        st.plotly_chart(fig)

    with col2:
        st.markdown("""
            <style>
                .custom-title {
                    text-align: center;
                    margin-bottom: -10px;
                    position: relative;
                    top: 0px;
                }
            </style>
            <h4 class="custom-title">Kategori Okupasi</h4>
        """, unsafe_allow_html=True)

        fig = px.pie(
            occupancy_klaim,
            values="Paid Claim",
            names="Kategori Okupasi",
            hole=0.5,
            color_discrete_sequence=["#004d00", "#339933", "#66B266"]
        )
        fig.update_traces(textinfo='percent', textposition='inside', textfont=dict(color='white'))
        fig.update_layout(
            width=400,
            height=250,
            margin=dict(l=10, r=10, t=10, b=10),
            font=dict(size=12),
            legend=dict(x=1, y=0.5, xanchor="left", yanchor="middle")
        )
        st.plotly_chart(fig)

    with col3:
        st.markdown("""
            <style>
                .custom-title {
                    text-align: center;
                    margin-bottom: -10px;
                    position: relative;
                    top: 0px;
                }
            </style>
            <h4 class="custom-title">Risk Level</h4>
        """, unsafe_allow_html=True)

        risk_order = ['A', 'B', 'C', 'D']
        risklevel_klaim['Kategori Risiko Okupasi'] = pd.Categorical(
            risklevel_klaim['Kategori Risiko Okupasi'],
            categories=risk_order,
            ordered=True
        )
        risklevel_klaim = risklevel_klaim.sort_values('Kategori Risiko Okupasi')

        fig = px.pie(
            risklevel_klaim,
            values="Paid Claim",
            names="Kategori Risiko Okupasi",
            hole=0.5,
            color_discrete_sequence=["#ff8000", "#a34700", "#cc5c00", "#7a3300"]
        )
        fig.update_traces(textinfo='percent', textposition='inside', textfont=dict(color='white'))
        fig.update_layout(
            width=400,
            height=250,
            margin=dict(l=10, r=10, t=10, b=10),
            font=dict(size=12),
            legend=dict(x=1, y=0.5, xanchor="left", yanchor="middle", traceorder='normal')
        )
        st.plotly_chart(fig)

    # Hitung loss ratio
    lossratio = (
    ((filtered_df_display["Paid Claim"].sum()
    + filtered_df_display["OS Claim"].sum()) - (filtered_df_display["Recovery Klaim Reas"].sum() + filtered_df_display["Recovery OS Claim Reas"].sum()))
    ) / (filtered_df_display["Premi Gross"].sum()-filtered_df_display["Akuisisi"].sum()-filtered_df_display["Premi Reas"].sum()+filtered_df_display["Komisi Reas"].sum())
    
    # Histogram dan Loss Ratio
    col1, col2 = st.columns(2)

    with col1:
        st.write("### 📊 Histogram Berdasarkan Underwriting Year (UY)")
        summary_df_melted = summary_df.melt(id_vars=['UY'], value_vars=summary_columns,
                                            var_name='Metric', value_name='Value')
        summary_df_melted = summary_df_melted[summary_df_melted['UY'] != 'Grand Total']
        summary_df_melted['Value'] = pd.to_numeric(summary_df_melted['Value'].str.replace(',', ''), errors='coerce')

        fig = px.histogram(
            summary_df_melted,
            x='UY',
            y='Value',
            color='Metric',
            barmode='group',
            color_discrete_map={
                'Premi Gross': '#003087',
                'Akuisisi': '#66B2B2',
                'Premi Reas': '#FF4D94',
                'Komisi Reas': '#FF8000',
                'Paid Claim': '#FFB366',
                'Recovery Klaim Reas': '#339933',
                'OS Claim': '#4D0099',
                'Recovery OS Claim Reas': '#99CCFF'
            }
        )
        fig.update_layout(
            legend=dict(
                orientation="v",     # tetap vertical
                yanchor="middle",    # anchor vertikal di tengah
                y=0.5,               # 50% tinggi chart (tengah)
                xanchor="left",      # anchor horizontal di kiri legend box
                x=1.0                # tepat di kanan luar chart
            )
        )

        max_value = summary_df_melted['Value'].max()
        tickvals = list(range(0, int(max_value) + 100000000000, 100000000000))
        ticktext = [f"{val:,.0f}".replace(",", ".") for val in tickvals]

        fig.update_layout(
            height=600,
            width=800,
            yaxis_title=None,
            xaxis_title="Underwriting Year (UY)",
            margin=dict(l=10, r=10, t=10, b=10),
            bargap=0.2,
            yaxis=dict(tickmode='array', tickvals=tickvals, ticktext=ticktext)
        )
        st.plotly_chart(fig)

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown(f"""
            <style>
                .section-box {{
                    background-color: #f08522;
                    padding: 5px;
                    border-radius: 10px;
                    color: white;
                    font-weight: bold;
                    text-align: center;
                    margin-bottom: 5px;
                }}
                .value-box {{
                    background-color: white;
                    color: black;
                    padding: 5px;
                    border-radius: 5px;
                    font-size: 10px;
                    text-align: center;
                }}
            </style>
            <div class="center-wrapper">
                <div class="section-box">
                    <h2>Loss Ratio</h2>
                    <div class="value-box">
                        <h1>{lossratio*100:.2f}%</h1>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)