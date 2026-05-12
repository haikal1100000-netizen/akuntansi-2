import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import date, datetime
from dataclasses import dataclass, asdict
from typing import Dict, List
import numpy as np

# Page config
st.set_page_config(
    page_title="🥩 Akuntansi Daging Segar",
    page_icon="🥩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk styling premium
st.markdown("""
<style>
    .main-header {
        font-size: 3rem !important;
        font-weight: bold !important;
        color: #1f77b4 !important;
        text-align: center;
        margin-bottom: 2rem !important;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .stMetric > label {
        color: white !important;
        font-size: 1.1rem !important;
    }
    .stMetric > div > div {
        color: white !important;
        font-size: 2rem !important;
    }
</style>
""", unsafe_allow_html=True)

@dataclass
class Transaksi:
    id: str
    tanggal: str
    jenis: str
    deskripsi: str
    debit: float
    kredit: float
    akun: str

class PerusahaanDaging:
    def __init__(self):
        self.nama = "PT Daging Segar Jaya"
        self.transaksi_list: List[Transaksi] = []
        self.buku_besar: Dict[str, List[Dict]] = {}
        self.neraca: Dict[str, float] = {"Aset": 50000000, "Liabilitas": 20000000, "Ekuitas": 30000000}
        self.laba_rugi: Dict[str, float] = {"Pendapatan": 0, "Beban": 0}
        self.next_id = 1
    
    def tambah_transaksi(self, tanggal: str, jenis: str, deskripsi: str, debit: float, kredit: float, akun: str):
        transaksi = Transaksi(
            id=f"T{self.next_id:04d}",
            tanggal=tanggal,
            jenis=jenis,
            deskripsi=deskripsi,
            debit=debit,
            kredit=kredit,
            akun=akun
        )
        self.transaksi_list.append(transaksi)
        self.next_id += 1
        self.update_financials(transaksi)
    
    def update_financials(self, transaksi: Transaksi):
        if "Penjualan" in transaksi.jenis:
            self.laba_rugi["Pendapatan"] += transaksi.debit
            self.neraca["Aset"] += transaksi.debit - transaksi.kredit
        elif "Biaya" in transaksi.jenis or "Pemotongan" in transaksi.jenis:
            self.laba_rugi["Beban"] += transaksi.debit
            self.neraca["Aset"] -= transaksi.debit - transaksi.kredit
    
    def get_df_transaksi(self):
        if not self.transaksi_list:
            return pd.DataFrame()
        data = [{
            'ID': t.id,
            'Tanggal': t.tanggal,
            'Jenis': t.jenis,
            'Akun': t.akun,
            'Deskripsi': t.deskripsi,
            'Debit': t.debit,
            'Kredit': t.kredit,
            'Saldo': t.debit - t.kredit
        } for t in self.transaksi_list]
        return pd.DataFrame(data)
    
    def get_metrics(self):
        df = self.get_df_transaksi()
        if df.empty:
            return {
                'total_transaksi': 0,
                'total_pendapatan': 0.0,
                'total_beban': 0.0,
                'laba_bersih': 0.0
            }
        total_transaksi = len(df)
        total_pendapatan = df[df['Jenis'].str.contains('Penjualan', na=False)]['Debit'].sum()
        total_beban = df[df['Jenis'].str.contains('Biaya|Pemotongan', na=False)]['Debit'].sum()
        laba_bersih = total_pendapatan - total_beban
        
        return {
            'total_transaksi': total_transaksi,
            'total_pendapatan': total_pendapatan,
            'total_beban': total_beban,
            'laba_bersih': laba_bersih
        }

# Initialize session state
if 'perusahaan' not in st.session_state:
    st.session_state.perusahaan = PerusahaanDaging()

# Sidebar Navigation
st.sidebar.title("🥩 Navigation")
page = st.sidebar.selectbox(
    "Pilih Menu:",
    ["📊 Dashboard", "➕ Transaksi Baru", "📋 Jurnal Umum", 
     "📚 Buku Besar", "⚖️ Neraca", "💰 Laba Rugi", "📈 Analitik", "💾 Data"]
)

# Header
st.markdown('<h1 class="main-header">Siklus Akuntansi Perusahaan Daging</h1>', unsafe_allow_html=True)
st.markdown("---")

# Main Pages
if page == "📊 Dashboard":
    st.header("📊 Dashboard Keuangan")
    
    # Metrics
    metrics = st.session_state.perusahaan.get_metrics()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div style="text-align: center;">
                <h3>🧾 Total Transaksi</h3>
            </div>
        """, unsafe_allow_html=True)
        st.metric("Total Transaksi", metrics['total_transaksi'])
    
    with col2:
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
        """, unsafe_allow_html=True)
        st.metric("💵 Pendapatan", f"Rp {metrics['total_pendapatan']:,.0f}")
    
    with col3:
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);">
        """, unsafe_allow_html=True)
        st.metric("💸 Beban", f"Rp {metrics['total_beban']:,.0f}")
    
    with col4:
        color = "normal" if metrics['laba_bersih'] >= 0 else "inverse"
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
        """, unsafe_allow_html=True)
        st.metric("📈 Laba Bersih", f"Rp {metrics['laba_bersih']:,.0f}", delta=None, delta_color=color)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        df = st.session_state.perusahaan.get_df_transaksi()
        if not df.empty:
            fig_pie = px.pie(df, names='Jenis', values='Debit', 
                           title="Distribusi Transaksi")
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        if not df.empty:
            fig_bar = px.bar(df.tail(10), x='Tanggal', y=['Debit', 'Kredit'],
                           title="10 Transaksi Terakhir", barmode='group')
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # Recent Transactions
    st.subheader("📋 10 Transaksi Terakhir")
    if not df.empty:
        st.dataframe(df.tail(10)[['ID', 'Tanggal', 'Jenis', 'Akun', 'Debit', 'Kredit']], 
                    use_container_width=True)

elif page == "➕ Transaksi Baru":
    st.header("➕ Transaksi Baru")
    
    with st.form("transaksi_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            jenis = st.selectbox("Jenis Transaksi", 
                               ["Penjualan Daging Sapi", "Penjualan Daging Kambing", 
                                "Pembelian Ternak", "Biaya Pemotongan", "Biaya Operasional"])
            tanggal = st.date_input("Tanggal", value=date.today())
            akun = st.text_input("Nama Akun", value="Kas")
        
        with col2:
            deskripsi = st.text_area("Deskripsi", height=100, 
                                   placeholder="Contoh: Penjualan 100kg daging sapi ke Resto ABC")
            debit = st.number_input("Debit (Rp)", min_value=0.0, step=10000.0, format="%.0f")
            kredit = st.number_input("Kredit (Rp)", min_value=0.0, step=10000.0, format="%.0f")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            submit = st.form_submit_button("💾 Simpan Transaksi", use_container_width=True)
        
        if submit:
            st.session_state.perusahaan.tambah_transaksi(
                tanggal.strftime("%Y-%m-%d"), jenis, deskripsi, debit, kredit, akun
            )
            st.success("✅ Transaksi berhasil disimpan!")
            st.balloons()
            st.rerun()

elif page == "📋 Jurnal Umum":
    st.header("📋 Jurnal Umum")
    df = st.session_state.perusahaan.get_df_transaksi()
    
    if df.empty:
        st.info("📝 Belum ada transaksi. Tambahkan transaksi baru terlebih dahulu!")
    else:
        # Filter
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Dari Tanggal", value=date.today())
        with col2:
            end_date = st.date_input("Sampai Tanggal", value=date.today())
        with col3:
            search = st.text_input("Cari Akun/Deskripsi")
        
        filtered_df = df[
            (pd.to_datetime(df['Tanggal']) >= pd.to_datetime(start_date)) &
            (pd.to_datetime(df['Tanggal']) <= pd.to_datetime(end_date))
        ]
        
        if search:
            filtered_df = filtered_df[
                filtered_df['Akun'].str.contains(search, case=False) |
                filtered_df['Deskripsi'].str.contains(search, case=False)
            ]
        
        st.dataframe(filtered_df, use_container_width=True, height=600)
        
        # Summary
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Total Debit", f"Rp {filtered_df['Debit'].sum():,.0f}")
        with col2: st.metric("Total Kredit", f"Rp {filtered_df['Kredit'].sum():,.0f}")
        with col3: st.metric("Total Transaksi", len(filtered_df))
        with col4: st.metric("Saldo", f"Rp {filtered_df['Saldo'].sum():,.0f}")

elif page == "⚖️ Neraca":
    st.header("⚖️ Neraca Perusahaan")
    
    metrics = st.session_state.perusahaan.get_metrics()
    laba_bersih = metrics['laba_bersih']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 AKTIVA")
        st.metric("Kas & Bank", f"Rp {st.session_state.perusahaan.neraca['Aset']:,.0f}")
        st.metric("Piutang Usaha", "Rp 0")
        st.metric("Persediaan Daging", "Rp 15.000.000")
        st.metric("**TOTAL AKTIVA**", f"Rp {st.session_state.perusahaan.neraca['Aset'] + 15000000:,.0f}", 
                 delta=f"Rp {laba_bersih:,.0f}")
    
    with col2:
        st.subheader("📉 PASIVA")
        st.metric("Utang Usaha", f"Rp {st.session_state.perusahaan.neraca['Liabilitas']:,.0f}")
        st.metric("Modal Pemilik", f"Rp {st.session_state.perusahaan.neraca['Ekuitas']:,.0f}")
        st.metric("Laba Ditahan", f"Rp {laba_bersih:,.0f}")
        st.metric("**TOTAL PASIVA**", f"Rp {(st.session_state.perusahaan.neraca['Liabilitas'] + st.session_state.perusahaan.neraca['Ekuitas'] + laba_bersih):,.0f}")

elif page == "💰 Laba Rugi":
    st.header("💰 Laporan Laba Rugi")
    
    metrics = st.session_state.perusahaan.get_metrics()
    
    st.subheader("📊 Ringkasan Keuangan")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Pendapatan", f"Rp {metrics['total_pendapatan']:,.0f}")
    with col2:
        st.metric("Total Beban", f"Rp {metrics['total_beban']:,.0f}")
    
    st.metric("**LABA BERSIH**", f"Rp {metrics['laba_bersih']:,.0f}", 
             delta=f"{(metrics['laba_bersih']/metrics['total_pendapatan']*100):.1f}%" if metrics['total_pendapatan'] > 0 else None)
    
    # Pendapatan vs Beban Chart
    df = st.session_state.perusahaan.get_df_transaksi()
    if not df.empty:
        pendapatan_df = df[df['Jenis'].str.contains('Penjualan')]['Debit'].sum()
        beban_df = df[df['Jenis'].str.contains('Biaya|Pemotongan')]['Debit'].sum()
        
        fig = go.Figure(data=[
            go.Bar(name='Pendapatan', x=['Keuangan'], y=[pendapatan_df], marker_color='#11998e'),
            go.Bar(name='Beban', x=['Keuangan'], y=[beban_df], marker_color='#ff6b6b')
        ])
        fig.update_layout(title="Pendapatan vs Beban", barmode='stack')
        st.plotly_chart(fig, use_container_width=True)

elif page == "📈 Analitik":
    st.header("📈 Analitik Keuangan")
    df = st.session_state.perusahaan.get_df_transaksi()
    
    if not df.empty:
        # Time series
        df['Tanggal'] = pd.to_datetime(df['Tanggal'])
        daily_df = df.groupby(df['Tanggal'].dt.date)['Saldo'].sum().reset_index()
        
        fig_line = px.line(daily_df, x='Tanggal', y='Saldo', 
                          title="Tren Saldo Harian")
        st.plotly_chart(fig_line, use_container_width=True)
        
        # Jenis transaksi pie chart
        jenis_fig = px.pie(df, names='Jenis', values='Debit', 
                          title="Komposisi Jenis Transaksi")
        st.plotly_chart(jenis_fig, use_container_width=True)

elif page == "💾 Data":
    st.header("💾 Kelola Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📥 Import Data")
        uploaded_file = st.file_uploader("Upload file JSON", type=['json'])
        if uploaded_file:
            data = json.load(uploaded_file)
            st.session_state.perusahaan.transaksi_list = [Transaksi(**t) for t in data['transaksi']]
            st.success("✅ Data berhasil diimport!")
            st.rerun()
    
    with col2:
        st.subheader("📤 Export Data")
        if st.button("💾 Download Data JSON"):
            data = {
                'transaksi': [asdict(t) for t in st.session_state.perusahaan.transaksi_list],
                'metrics': st.session_state.perusahaan.get_metrics()
            }
            st.download_button(
                label="Download JSON",
                data=json.dumps(data, indent=2, default=str),
                file_name=f"daging_akuntansi_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    st.subheader("🗑️ Reset Data")
    if st.button("⚠️ Reset Semua Data", type="primary"):
        if st.session_state.perusahaan.transaksi_list:
            st.session_state.perusahaan = PerusahaanDaging()
            st.success("✅ Data berhasil direset!")
            st.rerun()
        else:
            st.info("Data sudah kosong!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    🥩 PT Daging Segar Jaya | Aplikasi Akuntansi Modern dengan Streamlit
</div>
""", unsafe_allow_html=True)