import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Analisis Saham IDX", layout="wide", page_icon="📈")
st.title("📊 Analisis Emiten Saham Indonesia")
st.markdown("**Teknikal + Intraday Scalping Signals**")

# Sidebar
st.sidebar.header("Pengaturan")
tickers_input = st.sidebar.text_area(
    "Masukkan Ticker (pisah koma)", 
    "BBCA, BBRI, BMRI, BBNI, TLKM, ASII, ADRO, GOTO, AMRT",
    height=120
)

tab1, tab2 = st.tabs(["📅 Analisis Harian (Swing)", "⚡ Scalping / Intraday"])

with tab1:
    if st.button("🚀 Analisis Harian (OBV + Trend)", type="primary"):
        # Kode harian OBV yang lama tetap di sini (bisa copy dari sebelumnya)
        st.info("Fitur harian tetap sama seperti sebelumnya...")

with tab2:
    if st.button("⚡ Analisis Intraday & Scalping Signals", type="primary"):
        tickers = [t.strip().upper() + ".JK" for t in tickers_input.split(",") if t.strip()]
        
        with st.spinner("Mengambil data 5 menit terbaru..."):
            results = []
            for ticker in tickers:
                try:
                    # Data Intraday 5 menit (hari ini)
                    data = yf.download(ticker, period="5d", interval="5m")
                    if len(data) < 20:
                        continue
                        
                    last = data.iloc[-1]
                    prev = data.iloc[-2]
                    
                    # Gap hari ini
                    today_open = data['Open'].iloc[-1] if len(data) > 0 else last['Close']
                    prev_close = data['Close'].iloc[0] if 'Prev Close' in data.columns else data['Close'].iloc[-20]
                    gap = round(((today_open - prev_close) / prev_close) * 100, 2)
                    
                    # RSI 14 (5menit)
                    delta = data['Close'].diff()
                    gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
                    loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
                    rsi = 100 - (100 / (1 + gain/loss)) if loss != 0 else 50
                    
                    # VWAP
                    data['TP'] = (data['High'] + data['Low'] + data['Close']) / 3
                    data['TPV'] = data['TP'] * data['Volume']
                    vwap = data['TPV'].cumsum().iloc[-1] / data['Volume'].cumsum().iloc[-1]
                    
                    # Momentum
                    momentum = round((last['Close'] / data['Close'].iloc[-10] - 1) * 100, 2)
                    
                    # Sinyal Scalping Sederhana
                    if rsi < 35 and last['Close'] > vwap and momentum > 0:
                        signal = "🟢 **STRONG BUY** (Scalping Up)"
                    elif rsi > 70 and last['Close'] < vwap and momentum < 0:
                        signal = "🔴 **STRONG SELL** (Scalping Down)"
                    elif rsi < 45 and last['Close'] > vwap:
                        signal = "🟢 BUY Signal"
                    elif rsi > 60 and last['Close'] < vwap:
                        signal = "🔴 SELL Signal"
                    else:
                        signal = "⚪ Neutral / Tunggu"
                    
                    results.append({
                        'Ticker': ticker.replace('.JK', ''),
                        'Harga Saat Ini': round(last['Close'], 2),
                        'Change 5m %': round(((last['Close'] - prev['Close']) / prev['Close']) * 100, 2),
                        'RSI (5m)': round(rsi, 1),
                        'VWAP': round(vwap, 2),
                        'Gap Today %': gap,
                        'Momentum 10 candle': momentum,
                        'Signal Scalping': signal,
                        'Volume': int(last['Volume'])
                    })
                except:
                    continue
            
            if results:
                df = pd.DataFrame(results)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                st.success("✅ Sinyal Scalping di-update setiap kali kamu klik tombol!")
                st.warning("⚠️ Ini bukan jaminan profit. Gunakan stop-loss ketat (0.5-1%). Scalping sangat berisiko tinggi.")
            else:
                st.error("Gagal mengambil data intraday. Coba lagi nanti.")
