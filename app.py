import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="IDX Stock Hunter", layout="wide", page_icon="🚀")
st.title("📈 IDX Stock Hunter")
st.markdown("**Deteksi Akumulasi Kuat & Manual Screening**")

st.sidebar.header("Pengaturan")

# ==================== SECTION 1: MANUAL TICKER ====================
st.subheader("🔍 1. Screening Manual Ticker")
tickers_input = st.text_area("Masukkan Ticker (pisah koma)", 
    "BBCA, BBRI, BMRI, BBNI, TLKM, ASII, ADRO, BREN", height=80)

if st.button("Analisis Manual Ticker", type="primary"):
    with st.spinner("Menganalisis ticker manual..."):
        tickers = [t.strip().upper() + ".JK" for t in tickers_input.split(",") if t.strip()]
        results = []
        for ticker in tickers:
            try:
                hist = yf.Ticker(ticker).history(period="2y")
                if len(hist) < 100: continue
                # ... (logika sama seperti sebelumnya)
                last = hist.iloc[-1]
                sma50 = hist['Close'].rolling(50).mean().iloc[-1]
                sma200 = hist['Close'].rolling(200).mean().iloc[-1]
                trend = "🟢 UPTREND" if (last['Close'] > sma50 and sma50 > sma200) else "🔴 DOWNTREND" if (last['Close'] < sma50 and sma50 < sma200) else "⚪ SIDEWAYS"

                delta = hist['Close'].diff()
                gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
                rsi = 100 - (100 / (1 + gain/loss)) if loss != 0 else 50

                hist['OBV'] = (hist['Volume'] * np.sign(hist['Close'].diff())).cumsum()
                obv_now = hist['OBV'].iloc[-1]
                obv_30 = hist['OBV'].iloc[-31] if len(hist) > 30 else obv_now
                price_30 = ((last['Close'] / hist['Close'].iloc[-31]) - 1) * 100 if len(hist) > 30 else 0
                vol_recent = hist['Volume'].tail(10).mean()
                vol_avg = hist['Volume'].mean()

                if (obv_now > obv_30) and abs(price_30) < 15 and vol_recent > vol_avg * 1.15 and rsi < 55:
                    akum = "💰 AKUMULASI KUAT"
                elif obv_now > obv_30 and rsi < 60:
                    akum = "💰 Akumulasi Sedang"
                elif obv_now < obv_30 and rsi > 55:
                    akum = "📉 DISTRIBUSI"
                else:
                    akum = "Tidak Jelas"

                results.append({
                    'Ticker': ticker.replace('.JK',''),
                    'Harga': round(last['Close'], 2),
                    'Change %': round(((last['Close'] - hist.iloc[-2]['Close']) / hist.iloc[-2]['Close']) * 100, 2),
                    'RSI': round(rsi, 1),
                    'Trend': trend,
                    'Akumulasi / Distribusi': akum,
                    '30 Hari %': round(price_30, 1)
                })
            except:
                continue
        if results:
            st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)

# ==================== SECTION 2: AUTO AKUMULASI KUAT ====================
st.subheader("🏆 2. Emiten dengan Akumulasi Kuat (Auto Detection)")
st.caption("Mencari dari ratusan saham termasuk small cap / gocap")

if st.button("🔍 Cari Emiten Akumulasi Kuat Saat Ini", type="primary", use_container_width=True):
    with st.spinner("Mencari emiten Akumulasi Kuat dari banyak saham..."):
        # Daftar yang lebih luas (termasuk gocap)
        broad_tickers = [
            "BBCA","BBRI","BMRI","BBNI","TLKM","ASII","ADRO","BREN","AMRT","UNVR","BRIS","BTPS","CPIN","KLBF","MDKA",
            "ANTM","INKP","PTBA","ISAT","EXCL","PGAS","MEDC","SMGR","UNTR","ICBP","INDF","SCMA","GOTO","BUKA","MLPT",
            "RAJA","BUMI","CNKO","BSSR","ITMG","TAPG","HRUM","ARTO","JAST","SRTG","WOOD","TINS","PGEO","AKRA","TPIA"
        ]
        tickers = [t + ".JK" for t in broad_tickers]

        results = []
        for ticker in tickers:
            try:
                hist = yf.Ticker(ticker).history(period="2y")
                if len(hist) < 100: continue
                last = hist.iloc[-1]

                sma50 = hist['Close'].rolling(50).mean().iloc[-1]
                sma200 = hist['Close'].rolling(200).mean().iloc[-1]
                trend = "🟢 UPTREND" if (last['Close'] > sma50 and sma50 > sma200) else "🔴 DOWNTREND" if (last['Close'] < sma50 and sma50 < sma200) else "⚪ SIDEWAYS"

                delta = hist['Close'].diff()
                gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
                rsi = 100 - (100 / (1 + gain/loss)) if loss != 0 else 50

                hist['OBV'] = (hist['Volume'] * np.sign(hist['Close'].diff())).cumsum()
                obv_now = hist['OBV'].iloc[-1]
                obv_30 = hist['OBV'].iloc[-31] if len(hist) > 30 else obv_now
                price_30 = ((last['Close'] / hist['Close'].iloc[-31]) - 1) * 100 if len(hist) > 30 else 0
                vol_recent = hist['Volume'].tail(10).mean()
                vol_avg = hist['Volume'].mean()

                if (obv_now > obv_30) and abs(price_30) < 15 and vol_recent > vol_avg * 1.15 and rsi < 55:
                    results.append({
                        'Ticker': ticker.replace('.JK',''),
                        'Harga': round(last['Close'], 2),
                        'Change %': round(((last['Close'] - hist.iloc[-2]['Close']) / hist.iloc[-2]['Close']) * 100, 2),
                        'RSI': round(rsi, 1),
                        'Trend': trend,
                        '30 Hari %': round(price_30, 1)
                    })
            except:
                continue

        if results:
            df_akum = pd.DataFrame(results).sort_values(by='RSI')
            st.success(f"✅ Ditemukan {len(df_akum)} emiten dengan Akumulasi Kuat")
            st.dataframe(df_akum, use_container_width=True, hide_index=True)
        else:
            st.warning("Saat ini belum ditemukan emiten yang memenuhi kriteria Akumulasi Kuat.")

st.caption("Data dari Yahoo Finance • Auto detection termasuk small cap • Bukan rekomendasi trading")
