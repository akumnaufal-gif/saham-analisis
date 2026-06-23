import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Analisis Saham IDX", layout="wide", page_icon="📈")
st.title("📊 Analisis Emiten Saham Indonesia")
st.markdown("**Harian + Scalping Intraday**")

st.sidebar.header("Pengaturan")
tickers_input = st.sidebar.text_area(
    "Masukkan Ticker (pisah koma)", 
    "BBCA, BBRI, BMRI, BBNI, TLKM, ASII, ADRO",
    height=120
)

mode = st.radio("Pilih Jenis Analisa", 
                ["📅 Harian (Swing/Trend)", "⚡ Scalping / Intraday (5 menit)"], 
                horizontal=True)

if st.button("🚀 JALANKAN ANALISA SEKARANG", type="primary", use_container_width=True):
    tickers = [t.strip().upper() + ".JK" for t in tickers_input.split(",") if t.strip()]
    
    with st.spinner(f"Mengambil data {mode}..."):
        results = []
        
        for ticker in tickers:
            try:
                if mode == "📅 Harian (Swing/Trend)":
                    # Harian - tetap stabil
                    hist = yf.Ticker(ticker).history(period="2y")
                    if len(hist) < 100:
                        results.append({'Ticker': ticker.replace('.JK',''), 'Status': 'Data harian kurang'})
                        continue
                    
                    last = hist.iloc[-1]
                    prev = hist.iloc[-2]
                    change = round(((last['Close'] - prev['Close']) / prev['Close']) * 100, 2)
                    
                    sma50 = hist['Close'].rolling(50).mean().iloc[-1]
                    sma200 = hist['Close'].rolling(200).mean().iloc[-1]
                    
                    trend = "🟢 UPTREND" if (last['Close'] > sma50 and sma50 > sma200) else \
                            "🔴 DOWNTREND" if (last['Close'] < sma50 and sma50 < sma200) else "⚪ SIDEWAYS"
                    
                    delta = hist['Close'].diff()
                    gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
                    loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
                    rsi = 100 - (100 / (1 + gain/loss)) if loss != 0 else 50
                    
                    results.append({
                        'Ticker': ticker.replace('.JK',''),
                        'Harga': round(last['Close'],2),
                        'Change %': change,
                        'RSI': round(rsi,1),
                        'Trend': trend,
                        'Status': 'OK'
                    })
                
                else:  # SCALPING
                    # Percobaan bertahap
                    data = None
                    for attempt in ["5m", "15m", "1h"]:
                        try:
                            data = yf.download(ticker, period="10d", interval=attempt, progress=False)
                            if len(data) >= 20:
                                break
                        except:
                            continue
                    
                    if data is None or len(data) < 20:
                        results.append({'Ticker': ticker.replace('.JK',''), 'Status': 'Data intraday tidak tersedia (coba saat pasar buka)'})
                        continue
                        
                    last = data.iloc[-1]
                    prev = data.iloc[-2] if len(data) > 1 else last
                    
                    change = round(((last['Close'] - prev['Close']) / prev['Close']) * 100, 2)
                    
                    # RSI
                    delta = data['Close'].diff()
                    gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
                    loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
                    rsi = 100 - (100 / (1 + gain/loss)) if loss != 0 else 50
                    
                    # VWAP
                    data['TP'] = (data['High'] + data['Low'] + data['Close']) / 3
                    vwap = (data['TP'] * data['Volume']).cumsum().iloc[-1] / data['Volume'].cumsum().iloc[-1]
                    
                    momentum = round((last['Close'] / data['Close'].iloc[-10] - 1) * 100, 2) if len(data) > 10 else 0
                    
                    if rsi < 35 and last['Close'] > vwap:
                        signal = "🟢 STRONG BUY"
                    elif rsi > 68 and last['Close'] < vwap:
                        signal = "🔴 STRONG SELL"
                    else:
                        signal = "⚪ Neutral"
                    
                    results.append({
                        'Ticker': ticker.replace('.JK',''),
                        'Harga': round(last['Close'],2),
                        'Change %': change,
                        'RSI': round(rsi,1),
                        'VWAP': round(vwap,2),
                        'Momentum': momentum,
                        'Signal Scalping': signal,
                        'Status': 'OK'
                    })
                    
            except:
                results.append({'Ticker': ticker.replace('.JK',''), 'Status': 'Error'})
                continue
        
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        if mode.startswith("⚡"):
            st.info("💡 Scalping terbaik saat **pasar sedang buka** (09:00 - 16:00 WIB)")
            st.warning("⚠️ Tidak ada jaminan profit. Scalping sangat berisiko!")

st.caption("Data dari Yahoo Finance • Refresh dengan klik tombol")
