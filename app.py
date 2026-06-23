import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="IDX Stock Hunter", layout="wide", page_icon="🚀")
st.title("📈 IDX Stock Hunter - Versi Stabil")
st.markdown("**Deteksi Akumulasi Kuat yang Lebih Konsisten**")

st.sidebar.header("Pengaturan")
tickers_input = st.text_area("Ticker Manual", "BUVA, DEWA, BBCA, BBRI, BREN, ADRO", height=70)

if st.button("🚀 Analisis Sekarang", type="primary", use_container_width=True):
    with st.spinner("Menganalisis..."):
        broad = ["BUVA","DEWA","BBCA","BBRI","BMRI","BBNI","TLKM","ASII","ADRO","BREN","AMRT","UNVR","BRIS","GOTO"]
        tickers = [t + ".JK" for t in broad]

        if tickers_input.strip():
            manual = [t.strip().upper() + ".JK" for t in tickers_input.split(",") if t.strip()]
            tickers = list(dict.fromkeys(manual + tickers))

        results = []
        for ticker in tickers:
            try:
                hist = yf.Ticker(ticker).history(period="3mo")
                if len(hist) < 40: continue
                last = hist.iloc[-1]
                change = round(((last['Close'] - hist.iloc[-2]['Close']) / hist.iloc[-2]['Close']) * 100, 2)

                sma20 = hist['Close'].rolling(20).mean().iloc[-1]
                sma50 = hist['Close'].rolling(50).mean().iloc[-1]
                trend = "🟢 UPTREND" if last['Close'] > sma20 else "🔴 DOWNTREND" if last['Close'] < sma50 else "⚪ SIDEWAYS"

                # RSI
                delta = hist['Close'].diff()
                gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
                rsi = 100 - (100 / (1 + gain/loss)) if loss != 0 else 50

                # Volume & OBV
                hist['OBV'] = (hist['Volume'] * np.sign(hist['Close'].diff())).cumsum()
                obv_now = hist['OBV'].iloc[-1]
                obv_30 = hist['OBV'].iloc[-31] if len(hist) > 30 else obv_now
                vol_recent = hist['Volume'].tail(10).mean()
                vol_avg = hist['Volume'].mean()
                price_30d = ((last['Close'] / hist['Close'].iloc[-31]) - 1) * 100 if len(hist) > 30 else 0

                # LOGIKA BARU - LEBIH STABIL
                vol_spike = vol_recent / vol_avg
                
                if (change > 3 and vol_spike > 1.7) or \
                   (obv_now > obv_30 and vol_spike > 1.6 and rsi < 68) or \
                   (change > 5 and vol_spike > 1.4):                    # Tambahan untuk rebound kuat
                    akum = "💰 AKUMULASI KUAT"
                elif (obv_now > obv_30 and rsi < 62) or (rsi < 45):
                    akum = "💰 Akumulasi Sedang"
                elif obv_now < obv_30 and rsi > 58:
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
                    '30 Hari %': round(price_30d, 1),
                    'Vol Spike': round(vol_spike, 2)
                })
            except:
                continue

        df = pd.DataFrame(results)

        st.subheader("🏆 Top Emiten Akumulasi Kuat")
        top = df[df['Akumulasi / Distribusi'] == "💰 AKUMULASI KUAT"].sort_values('Change %', ascending=False).head(10)
        if not top.empty:
            st.success(f"✅ Ditemukan {len(top)} emiten Akumulasi Kuat")
            st.dataframe(top, use_container_width=True, hide_index=True)
        else:
            st.warning("Belum ada emiten yang memenuhi kriteria Akumulasi Kuat saat ini.")

        st.subheader("📋 Semua Hasil")
        st.dataframe(df.sort_values('Change %', ascending=False), use_container_width=True, hide_index=True)

st.caption("Logika sudah di-improve agar lebih stabil terhadap pergerakan harga intraday • Coba refresh beberapa kali")
