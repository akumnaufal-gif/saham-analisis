import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="IDX Stock Hunter", layout="wide", page_icon="🚀")
st.title("📈 IDX Stock Hunter - Versi Improved")
st.markdown("**Deteksi Akumulasi Kuat + Rebound**")

st.sidebar.header("Pengaturan")
tickers_input = st.text_area("Ticker Manual (opsional)", 
    "BBCA, BBRI, BMRI, DEWA, BREN, ADRO", height=80)

if st.button("🚀 Analisis Sekarang", type="primary", use_container_width=True):
    with st.spinner("Menganalisis..."):
        # Daftar luas untuk auto detection
        broad_list = ["BBCA","BBRI","BMRI","BBNI","TLKM","ASII","ADRO","BREN","AMRT","UNVR","BRIS","BTPS","CPIN","KLBF",
                     "MDKA","ANTM","INKP","PTBA","ISAT","EXCL","PGAS","MEDC","SMGR","DEWA","BUMI","RAJA","ITMG","ARTO","GOTO"]
        tickers = [t + ".JK" for t in broad_list]

        results = []
        for ticker in tickers:
            try:
                hist = yf.Ticker(ticker).history(period="2y")
                if len(hist) < 100: continue
                last = hist.iloc[-1]
                prev = hist.iloc[-2]

                change = round(((last['Close'] - prev['Close']) / prev['Close']) * 100, 2)

                sma50 = hist['Close'].rolling(50).mean().iloc[-1]
                sma200 = hist['Close'].rolling(200).mean().iloc[-1]
                trend = "🟢 UPTREND" if (last['Close'] > sma50 and sma50 > sma200) else "🔴 DOWNTREND" if (last['Close'] < sma50 and sma50 < sma200) else "⚪ SIDEWAYS"

                # RSI
                delta = hist['Close'].diff()
                gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
                rsi = 100 - (100 / (1 + gain/loss)) if loss != 0 else 50

                # OBV
                hist['OBV'] = (hist['Volume'] * np.sign(hist['Close'].diff())).cumsum()
                obv_now = hist['OBV'].iloc[-1]
                obv_30 = hist['OBV'].iloc[-31] if len(hist) > 30 else obv_now
                price_30 = ((last['Close'] / hist['Close'].iloc[-31]) - 1) * 100 if len(hist) > 30 else 0
                vol_recent = hist['Volume'].tail(10).mean()
                vol_avg = hist['Volume'].mean()

                # LOGIKA BARU YANG LEBIH SENSITIF
                if (change > 3 and vol_recent > vol_avg * 1.8 and rsi < 65) or \
                   (obv_now > obv_30 and abs(price_30) < 20 and vol_recent > vol_avg * 1.3 and rsi < 58):
                    akum = "💰 AKUMULASI KUAT"
                elif obv_now > obv_30 and rsi < 62:
                    akum = "💰 Akumulasi Sedang"
                elif obv_now < obv_30 and rsi > 55:
                    akum = "📉 DISTRIBUSI"
                else:
                    akum = "Tidak Jelas"

                results.append({
                    'Ticker': ticker.replace('.JK',''),
                    'Harga': round(last['Close'], 2),
                    'Change %': change,
                    'RSI': round(rsi, 1),
                    'Trend': trend,
                    'Akumulasi / Distribusi': akum,
                    '30 Hari %': round(price_30, 1),
                    'Volume Spike': round(vol_recent / vol_avg, 2)
                })
            except:
                continue

        df = pd.DataFrame(results)

        # Top Akumulasi Kuat
        st.subheader("🏆 Top Emiten Akumulasi Kuat Hari Ini")
        top = df[df['Akumulasi / Distribusi'] == "💰 AKUMULASI KUAT"].sort_values(by='Change %', ascending=False)
        if not top.empty:
            st.dataframe(top, use_container_width=True, hide_index=True)
        else:
            st.warning("Belum ada sinyal Akumulasi Kuat yang kuat saat ini.")

        st.subheader("📋 Semua Hasil")
        st.dataframe(df.sort_values(by='Akumulasi / Distribusi'), use_container_width=True, hide_index=True)

st.caption("Logika sudah di-improve untuk mendeteksi rebound + volume spike seperti DEWA • Coba refresh beberapa kali")
