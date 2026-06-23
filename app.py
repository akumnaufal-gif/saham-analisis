import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Analisis Saham IDX", layout="wide", page_icon="📈")
st.title("📊 Analisis Emiten Saham Indonesia")
st.markdown("**Teknikal Analysis • Uptrend • Akumulasi • RSI**")

# Sidebar
st.sidebar.header("Pengaturan")
tickers_input = st.sidebar.text_area(
    "Masukkan Ticker (pisah koma)", 
    "BBCA, BBRI, BMRI, BBNI, TLKM, ASII, ADRO, GOTO, AMRT, UNVR",
    height=150
)

if st.sidebar.button("🚀 Analisis Sekarang", type="primary"):
    tickers = [t.strip().upper() + ".JK" for t in tickers_input.split(",") if t.strip()]
    
    with st.spinner("Mengambil data dari Yahoo Finance..."):
        results = []
        for ticker in tickers:
            try:
                hist = yf.Ticker(ticker).history(period="2y")
                if len(hist) < 100:
                    continue
                    
                last = hist.iloc[-1]
                prev = hist.iloc[-2]
                change = round(((last['Close'] - prev['Close']) / prev['Close']) * 100, 2)
                
                # SMA
                sma20 = last['Close'] > hist['Close'].rolling(20).mean().iloc[-1]
                sma50 = last['Close'] > hist['Close'].rolling(50).mean().iloc[-1]
                sma200 = hist['Close'].rolling(200).mean().iloc[-1]
                
                # Trend
                if sma50 and hist['Close'].rolling(50).mean().iloc[-1] > sma200:
                    trend = "🟢 UPTREND (Bagus)"
                elif not sma50 and hist['Close'].rolling(50).mean().iloc[-1] < sma200:
                    trend = "🔴 DOWNTREND"
                else:
                    trend = "⚪ SIDEWAYS"
                
                # RSI sederhana
                delta = hist['Close'].diff()
                rsi = 100 - (100 / (1 + (delta.where(delta > 0, 0).rolling(14).mean() / 
                                      (-delta.where(delta < 0, 0).rolling(14).mean())))).iloc[-1]
                
                # Akumulasi sederhana
                akum = "💰 YA" if (rsi < 45 and change > 0) else "Tidak"
                
                results.append({
                    'Ticker': ticker.replace('.JK', ''),
                    'Harga': round(last['Close'], 2),
                    'Change %': change,
                    'RSI': round(rsi, 1),
                    'Trend': trend,
                    'Akumulasi': akum,
                    'Volume': int(last['Volume'])
                })
            except:
                continue
        
        if results:
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Filter
            col1, col2, col3 = st.columns(3)
            with col1:
                st.subheader("🟢 Uptrend")
                st.dataframe(df[df['Trend'].str.contains('UPTREND')][['Ticker','Harga','Change %','RSI']])
            with col2:
                st.subheader("💰 Akumulasi")
                st.dataframe(df[df['Akumulasi'].str.contains('YA')])
            with col3:
                st.subheader("🔴 Downtrend")
                st.dataframe(df[df['Trend'].str.contains('DOWNTREND')][['Ticker','Harga','Change %']])
            
            # Chart
            st.subheader("📈 Chart Saham")
            selected = st.selectbox("Pilih saham untuk dilihat chartnya", df['Ticker'])
            if selected:
                data = yf.download(selected + ".JK", period="6mo")
                fig = go.Figure(data=[go.Candlestick(x=data.index,
                                                     open=data['Open'], high=data['High'],
                                                     low=data['Low'], close=data['Close'])])
                fig.update_layout(title=f"{selected} - 6 Bulan Terakhir", height=600)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Gagal mengambil data. Coba lagi nanti.")
