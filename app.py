import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Analisis Saham IDX", layout="wide", page_icon="📈")
st.title("📊 Analisis Emiten Saham Indonesia")
st.markdown("**Teknikal Analysis • Uptrend • Akumulasi (OBV + Volume)**")

# Sidebar
st.sidebar.header("Pengaturan")
tickers_input = st.sidebar.text_area(
    "Masukkan Ticker (pisah koma)", 
    "BBCA, BBRI, BMRI, BBNI, TLKM, ASII, ADRO, GOTO, AMRT, UNVR",
    height=150
)

if st.sidebar.button("🚀 Analisis Sekarang", type="primary"):
    tickers = [t.strip().upper() + ".JK" for t in tickers_input.split(",") if t.strip()]
    
    with st.spinner("Mengambil data & menghitung OBV..."):
        results = []
        for ticker in tickers:
            try:
                hist = yf.Ticker(ticker).history(period="2y")
                if len(hist) < 100:
                    continue
                    
                last = hist.iloc[-1]
                prev = hist.iloc[-2]
                change = round(((last['Close'] - prev['Close']) / prev['Close']) * 100, 2)
                
                # === TREND ===
                sma50 = hist['Close'].rolling(50).mean().iloc[-1]
                sma200 = hist['Close'].rolling(200).mean().iloc[-1]
                
                if last['Close'] > sma50 and sma50 > sma200:
                    trend = "🟢 UPTREND (Bagus)"
                elif last['Close'] < sma50 and sma50 < sma200:
                    trend = "🔴 DOWNTREND"
                else:
                    trend = "⚪ SIDEWAYS"
                
                # === RSI ===
                delta = hist['Close'].diff()
                gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
                rsi = 100 - (100 / (1 + gain/loss)) if loss != 0 else 50
                
                # === AKUMULASI PAKAI OBV + VOLUME ===
                # Hitung OBV
                hist['OBV'] = (hist['Volume'] * np.sign(hist['Close'].diff())).cumsum()
                
                obv_now = hist['OBV'].iloc[-1]
                obv_30 = hist['OBV'].iloc[-31] if len(hist) > 30 else hist['OBV'].iloc[0]
                
                price_30_ago = hist['Close'].iloc[-31] if len(hist) > 30 else hist['Close'].iloc[0]
                price_change_30d = ((last['Close'] / price_30_ago) - 1) * 100
                
                vol_recent = hist['Volume'].tail(10).mean()
                vol_avg = hist['Volume'].mean()
                
                # Logika Akumulasi yang lebih akurat
                if (obv_now > obv_30) and \
                   (abs(price_change_30d) < 12) and \
                   (vol_recent > vol_avg * 1.1) and \
                   (rsi < 55):
                    akum = "💰 YA - Indikasi Akumulasi Kuat"
                elif (obv_now > obv_30) and (abs(price_change_30d) < 15):
                    akum = "💰 YA - Potensi Akumulasi"
                else:
                    akum = "Tidak terdeteksi"
                
                results.append({
                    'Ticker': ticker.replace('.JK', ''),
                    'Harga': round(last['Close'], 2),
                    'Change %': change,
                    'RSI': round(rsi, 1),
                    'Trend': trend,
                    'Akumulasi': akum,
                    'Vol 10d': int(vol_recent),
                    'Price 30d %': round(price_change_30d, 1)
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
                st.dataframe(df[df['Trend'].str.contains('UPTREND')])
            with col2:
                st.subheader("💰 Akumulasi")
                st.dataframe(df[df['Akumulasi'].str.contains('YA')])
            with col3:
                st.subheader("🔴 Downtrend")
                st.dataframe(df[df['Trend'].str.contains('DOWNTREND')])
            
            st.success(f"✅ Berhasil menganalisis {len(df)} emiten!")
        else:
            st.error("Gagal mengambil data. Coba lagi nanti.")
