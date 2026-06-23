import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="IDX Stock Hunter", layout="wide", page_icon="🚀")
st.title("📈 IDX Stock Hunter")
st.markdown("**Deteksi Akumulasi Kuat & Rebound** - Versi Stabil")

st.sidebar.header("Pengaturan")
tickers_input = st.text_area("🔍 Ticker Manual (pisah koma)", 
    "DEWA, BBCA, BBRI, BMRI, BREN, ADRO, AMRT", height=80)

# ==================== TOMBOL UTAMA ====================
if st.button("🚀 Analisis Sekarang", type="primary", use_container_width=True):
    with st.spinner("Mengambil data dari Yahoo Finance..."):
        # Daftar saham untuk auto detection
        broad_list = ["DEWA","BBCA","BBRI","BMRI","BBNI","TLKM","ASII","ADRO","BREN","AMRT","UNVR","BRIS",
                     "BTPS","CPIN","KLBF","MDKA","ANTM","INKP","PTBA","GOTO","BUKA","RAJA","ITMG"]
        tickers = [t + ".JK" for t in broad_list]

        if tickers_input.strip():
            manual = [t.strip().upper() + ".JK" for t in tickers_input.split(",") if t.strip()]
            tickers = list(dict.fromkeys(manual + tickers))  # gabung tanpa duplikat

        results = []
        for ticker in tickers:
            try:
                hist = yf.Ticker(ticker).history(period="3mo")
                if len(hist) < 30: continue
                
                last = hist.iloc[-1]
                prev = hist.iloc[-2]
                change = round(((last['Close'] - prev['Close']) / prev['Close']) * 100, 2)

                # Trend
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
                obv_20 = hist['OBV'].iloc[-21] if len(hist) > 20 else obv_now
                vol_recent = hist['Volume'].tail(5).mean()
                vol_avg = hist['Volume'].mean()

                price_change_20d = ((last['Close'] / hist['Close'].iloc[-21]) - 1) * 100 if len(hist) > 20 else 0

                # === LOGIKA DETEKSI YANG DI-IMPROVE ===
                if (change >= 3.0 and vol_recent > vol_avg * 1.8) or \
                   (change >= 2.0 and vol_recent > vol_avg * 1.6 and rsi < 68):
                    akum = "💰 AKUMULASI KUAT"
                elif (obv_now > obv_20 and vol_recent > vol_avg * 1.4) or (rsi < 45):
                    akum = "💰 Akumulasi Sedang"
                elif obv_now < obv_20 and rsi > 58:
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
                    '20 Hari %': round(price_change_20d, 1),
                    'Vol Spike': round(vol_recent / vol_avg, 2)
                })
            except:
                continue

        df = pd.DataFrame(results)

        # ==================== TOP AKUMULASI KUAT ====================
        st.subheader("🏆 Top 10 Emiten Akumulasi Kuat / Rebound Saat Ini")
        top_akum = df[df['Akumulasi / Distribusi'] == "💰 AKUMULASI KUAT"].sort_values(by='Change %', ascending=False).head(10)
        
        if not top_akum.empty:
            st.success(f"✅ Ditemukan {len(top_akum)} emiten Akumulasi Kuat")
            st.dataframe(top_akum, use_container_width=True, hide_index=True)
        else:
            st.warning("Belum ada emiten yang memenuhi kriteria Akumulasi Kuat saat ini.")

        # ==================== TABEL LENGKAP ====================
        st.subheader("📋 Semua Hasil Analisa")
        st.dataframe(df.sort_values(by='Change %', ascending=False), use_container_width=True, hide_index=True)

st.caption("🔄 Refresh berkala untuk data terbaru • Logika sudah di-tune untuk mendeteksi rebound seperti DEWA")
