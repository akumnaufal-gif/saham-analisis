import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="IDX Stock Hunter", layout="wide", page_icon="🚀")
st.title("📈 IDX Stock Hunter - Deteksi Bandar / Akumulasi")
st.markdown("**Fokus: Akumulasi Kuat + Bandar Activity**")

st.sidebar.header("Pengaturan")
tickers_input = st.text_area("Ticker Manual (pisah koma)", 
    "DEWA, BUVA, BBCA, BBRI, BREN, ADRO", height=80)

if st.button("🚀 Analisis Sekarang", type="primary", use_container_width=True):
    with st.spinner("Menganalisis..."):
        broad = ["DEWA","BUVA","BBCA","BBRI","BMRI","BBNI","TLKM","ASII","ADRO","BREN","AMRT","UNVR","BRIS","GOTO","BUKA"]
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
                trend = "🟢 UPTREND" if last['Close'] > sma20 else "🔴 DOWNTREND"

                delta = hist['Close'].diff()
                gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
                rsi = 100 - (100 / (1 + gain/loss)) if loss != 0 else 50

                hist['OBV'] = (hist['Volume'] * np.sign(hist['Close'].diff())).cumsum()
                obv_now = hist['OBV'].iloc[-1]
                obv_30 = hist['OBV'].iloc[-31] if len(hist) > 30 else obv_now
                vol_recent = hist['Volume'].tail(10).mean()
                vol_avg = hist['Volume'].mean()
                vol_spike = round(vol_recent / vol_avg, 2)

                price_30d = ((last['Close'] / hist['Close'].iloc[-31]) - 1) * 100 if len(hist) > 30 else 0

                # Logika Deteksi Bandar / Akumulasi Kuat
                if (change > 3.0 and vol_spike > 2.0) or \
                   (change > 2.0 and vol_spike > 1.8 and obv_now > obv_30 and rsi < 65):
                    akum = "💰 BANDAR MASUK KUAT"
                elif (obv_now > obv_30 and vol_spike > 1.5) or (rsi < 45 and change > 0):
                    akum = "💰 Akumulasi / Bandar Sedang Masuk"
                elif obv_now < obv_30 and vol_spike > 1.5:
                    akum = "📉 BANDAR KELUAR"
                else:
                    akum = "Tidak Jelas"

                results.append({
                    'Ticker': ticker.replace('.JK',''),
                    'Harga': round(last['Close'], 2),
                    'Change %': change,
                    'RSI': round(rsi, 1),
                    'Trend': trend,
                    'Akumulasi / Bandar': akum,
                    'Vol Spike': vol_spike,
                    '30 Hari %': round(price_30d, 1)
                })
            except:
                continue

        df = pd.DataFrame(results)

        st.subheader("🏆 Top Emiten Bandar / Akumulasi Kuat")
        top = df[df['Akumulasi / Bandar'].str.contains("KUAT|BANDAR MASUK")].sort_values('Change %', ascending=False)
        if not top.empty:
            st.dataframe(top, use_container_width=True, hide_index=True)
        else:
            st.warning("Belum ada sinyal bandar kuat saat ini.")

        st.subheader("📋 Semua Hasil")
        st.dataframe(df.sort_values('Change %', ascending=False), use_container_width=True, hide_index=True)

st.caption("Deteksi berdasarkan Volume Spike + OBV + Price Action • Bukan data broker resmi • Refresh berkala")
