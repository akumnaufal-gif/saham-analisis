import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="IDX Stock Hunter Pro", layout="wide", page_icon="🚀")
st.title("📈 IDX Stock Hunter Pro - Pre-Surge Detector")
st.markdown("**Mendeteksi Saham Sebelum Naik Tajam (Early Signal)**")

st.sidebar.header("Pengaturan")
tickers_input = st.text_area("Ticker Manual (pisah koma)", 
    "BALI, DEWA, BUVA, BBCA, BBRI, BREN", height=80)

if st.button("🚀 Scan Pre-Surge Sekarang", type="primary", use_container_width=True):
    with st.spinner("Mencari saham dengan potensi naik dini..."):
        broad = ["BALI","DEWA","BUVA","BBCA","BBRI","BMRI","BBNI","TLKM","ASII","ADRO","BREN","AMRT","GOTO","BUKA","ARTO","EXCL","ISAT","PGEO","HRUM","ITMG"]
        tickers = [t + ".JK" for t in broad]

        if tickers_input.strip():
            manual = [t.strip().upper() + ".JK" for t in tickers_input.split(",") if t.strip()]
            tickers = list(dict.fromkeys(manual + tickers))

        results = []
        for ticker in tickers:
            try:
                hist = yf.Ticker(ticker).history(period="3mo")
                if len(hist) < 50: continue
                last = hist.iloc[-1]
                change = round(((last['Close'] - hist.iloc[-2]['Close']) / hist.iloc[-2]['Close']) * 100, 2)

                vol_recent = hist['Volume'].tail(10).mean()
                vol_avg = hist['Volume'].mean()
                vol_spike = round(vol_recent / vol_avg, 2)

                # RSI early rise
                delta = hist['Close'].diff()
                gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
                rsi = 100 - (100 / (1 + gain/loss)) if loss != 0 else 50

                # OBV early accumulation
                hist['OBV'] = (hist['Volume'] * np.sign(hist['Close'].diff())).cumsum()
                obv_now = hist['OBV'].iloc[-1]
                obv_30 = hist['OBV'].iloc[-31] if len(hist) > 30 else obv_now
                obv_rising = obv_now > obv_30

                # Pre-Surge Score
                pre_score = 0
                if vol_spike > 1.8: pre_score += 35
                if rsi < 55 and rsi > rsi.mean(): pre_score += 25   # RSI mulai naik dari bawah
                if obv_rising: pre_score += 25
                if change > 1: pre_score += 15
                pre_score = min(100, pre_score)

                if pre_score >= 75:
                    signal = "🔥 POTENSI PRE-SURGE KUAT"
                elif pre_score >= 60:
                    signal = "⚡ Potensi Naik Dini"
                else:
                    signal = "Normal"

                results.append({
                    'Ticker': ticker.replace('.JK',''),
                    'Harga': round(last['Close'], 2),
                    'Change %': change,
                    'Vol Spike': vol_spike,
                    'RSI': round(rsi, 1),
                    'Pre-Surge Score': pre_score,
                    'Signal': signal
                })
            except:
                continue

        df = pd.DataFrame(results).sort_values('Pre-Surge Score', ascending=False)

        st.subheader("🔥 Potensi Pre-Surge (Sebelum Naik Tajam)")
        pre_surge = df[df['Pre-Surge Score'] >= 60]
        if not pre_surge.empty:
            st.success(f"✅ Ditemukan {len(pre_surge)} saham berpotensi naik dini")
            st.dataframe(pre_surge, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada sinyal Pre-Surge kuat saat ini. Coba refresh berkala.")

        st.subheader("📋 Semua Hasil")
        st.dataframe(df, use_container_width=True, hide_index=True)

st.caption("Pre-Surge Score fokus pada Volume Spike + OBV Rising + RSI Early Rise • Cocok untuk deteksi dini seperti BALI")
