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
                    hist = yf.Ticker(ticker).history(period="2y", auto_adjust=True)
                    if len(hist) < 100: continue
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
                    
                    hist['OBV'] = (hist['Volume'] * np.sign(hist['Close'].diff())).cumsum()
                    akum = "💰 YA - Akumulasi" if (hist['OBV'].iloc[-1] > hist['OBV'].iloc[-31]) and rsi < 55 else "Tidak"
                    
                    results.append({'Ticker': ticker.replace('.JK',''), 'Harga':round(last['Close'],2),
                                    'Change %':change, 'RSI':round(rsi,1), 'Trend':trend, 'Akumulasi':akum})
                
                else:  # SCALPING
                    # Coba beberapa interval dan period
                    data = yf.download(ticker, period="10d", interval="5m", progress=False)
                    if len(data) < 20:
                        data = yf.download(ticker, period="5d", interval="15m", progress=False)
                    
                    if len(data) < 20: 
                        results.append({'Ticker': ticker.replace('.JK',''), 'Status': 'Data intraday tidak tersedia'})
                        continue
                        
                    last = data.iloc[-1]
                    prev = data.iloc[-2] if len(data) > 1 else last
                    
                    change5m = round(((last['Close'] - prev['Close']) / prev['Close']) * 100, 2)
                    
                    # RSI
                    delta = data['Close'].diff()
                    gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
                    loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
                    rsi = 100 - (100 / (1 + gain/loss)) if loss != 0 else 50
                    
                    # VWAP
                    data['TP'] = (data['High'] + data['Low'] + data['Close']) / 3
                    vwap = (data['TP'] * data['Volume']).cumsum().iloc[-1] / data['Volume'].cumsum().iloc[-1]
                    
                    momentum = round((last['Close'] / data['Close'].iloc[-10] - 1) * 100, 2) if len(data) > 10 else 0
                    
                    if rsi < 35 and last['Close'] > vwap and momentum > 0:
                        signal = "🟢 STRONG BUY (Scalping)"
                    elif rsi > 68 and last['Close'] < vwap and momentum < 0:
                        signal = "🔴 STRONG SELL"
                    elif rsi < 45 and last['Close'] > vwap:
                        signal = "🟢 BUY"
                    elif rsi > 62 and last['Close'] < vwap:
                        signal = "🔴 SELL"
                    else:
                        signal = "⚪ Neutral / Tunggu konfirmasi"
                    
                    results.append({
                        'Ticker': ticker.replace('.JK',''),
                        'Harga': round(last['Close'],2),
                        'Change 5m%': change5m,
                        'RSI': round(rsi,1),
                        'VWAP': round(vwap,2),
                        'Momentum': momentum,
                        'Signal Scalping': signal
                    })
                    
            except Exception as e:
                results.append({'Ticker': ticker.replace('.JK',''), 'Status': 'Error'})
                continue
        
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        if mode == "⚡ Scalping / Intraday (5 menit)":
            st.info("💡 Data Scalping paling akurat saat pasar sedang buka (09:00 - 16:00 WIB)")
            st.warning("⚠️ Scalping sangat berisiko. Gunakan stop loss ketat!")

st.caption("Data Yahoo Finance • Klik tombol setiap kali ingin refresh data")
