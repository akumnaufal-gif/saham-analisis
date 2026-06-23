import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

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
                
                # SMA untuk Trend
                sma50 = hist['Close'].rolling(50).mean().iloc[-1]
                sma200 = hist['Close'].rolling(200).mean().iloc[-1]
                
                if last['Close'] > sma50 and sma50 > sma200:
                    trend = "🟢 UPTREND (Bagus)"
                elif last['Close'] < sma50 and sma50 < sma200:
                    trend = "🔴 DOWNTREND"
                else:
                    trend = "⚪ SIDEWAYS"
                
                # RSI Sederhana
                delta = hist['Close'].diff()
                gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
                rsi = 100 - (100 / (1 + gain/loss)) if loss != 0 else 50
                
                # Akumulasi
                akum = "💰 YA" if (rsi < 45 and change > -1) else "Tidak"
                
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
                st.dataframe(df[df['Trend'].str.contains('UPTREND', na=False)][['Ticker','Harga','Change %','RSI']])
            with col2:
                st.subheader("💰 Akumulasi")
                st.dataframe(df[df['Akumulasi'].str.contains('YA', na=False)])
            with col3:
                st.subheader("🔴 Downtrend")
                st.dataframe(df[df['Trend'].str.contains('DOWNTREND', na=False)][['Ticker','Harga','Change %']])
            
            st.success(f"✅ Berhasil menganalisis {len(df)} emiten!")
        else:
            st.error("Gagal mengambil data. Coba lagi beberapa saat.")
