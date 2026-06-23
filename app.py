import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="IDX Stock Hunter", layout="wide", page_icon="🚀")
st.title("📈 IDX Stock Hunter")
st.markdown("**Deteksi Akumulasi, Distribusi, Uptrend & Downtrend**")

st.sidebar.header("Pengaturan")
mode = st.sidebar.radio("Mode", ["🔍 Screening Utama", "⚡ Scalping Section"])

tickers_input = st.sidebar.text_area("Ticker Manual (opsional)", 
    "BBCA, BBRI, BMRI, BBNI, TLKM, ASII, ADRO, BREN, AMRT", height=80)

if st.sidebar.button("🚀 Analisis Sekarang", type="primary", use_container_width=True):
    with st.spinner("Mengambil data..."):
        if mode == "🔍 Screening Utama":
            # ==================== TABEL TOP AKUMULASI KUAT ====================
            st.subheader("🏆 TOP EMITEN DENGAN AKUMULASI KUAT")
            
            # Daftar saham populer (bisa ditambah)
            popular_tickers = [
                "BBCA","BBRI","BMRI","BBNI","TLKM","ASII","ADRO","BREN","AMRT","UNVR",
                "BRIS","BTPS","CPIN","KLBF","MDKA","ANTM","INKP","PTBA","ISAT","EXCL",
                "PGAS","MEDC","SMGR","UNTR","ICBP","INDF","SCMA","GOTO","BUKA"
            ]
            tickers = [t + ".JK" for t in popular_tickers]

            results = []
            for ticker in tickers:
                try:
                    hist = yf.Ticker(ticker).history(period="2y")
                    if len(hist) < 100: continue
                    last = hist.iloc[-1]

                    # Trend
                    sma50 = hist['Close'].rolling(50).mean().iloc[-1]
                    sma200 = hist['Close'].rolling(200).mean().iloc[-1]
                    if last['Close'] > sma50 and sma50 > sma200:
                        trend = "🟢 UPTREND"
                    elif last['Close'] < sma50 and sma50 < sma200:
                        trend = "🔴 DOWNTREND"
                    else:
                        trend = "⚪ SIDEWAYS"

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

                    # Logika Akumulasi
                    if (obv_now > obv_30) and abs(price_30) < 15 and vol_recent > vol_avg * 1.15 and rsi < 55:
                        akum = "💰 AKUMULASI KUAT"
                    elif obv_now > obv_30 and rsi < 60:
                        akum = "💰 Akumulasi Sedang"
                    elif obv_now < obv_30 and abs(price_30) < 15 and vol_recent > vol_avg * 1.1 and rsi > 50:
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

            df = pd.DataFrame(results)

            # Tampilkan Top 10 Akumulasi Kuat
            top_akum = df[df['Akumulasi / Distribusi'] == "💰 AKUMULASI KUAT"].sort_values(by=['RSI', '30 Hari %']).head(10)
            if not top_akum.empty:
                st.success(f"✅ Ditemukan {len(top_akum)} emiten dengan Akumulasi Kuat")
                st.dataframe(top_akum, use_container_width=True, hide_index=True)
            else:
                st.warning("Saat ini belum ada emiten yang memenuhi kriteria Akumulasi Kuat.")

            # ==================== TABEL LENGKAP ====================
            st.subheader("📋 Semua Hasil Analisa")
            st.dataframe(df.sort_values(by='Akumulasi / Distribusi'), use_container_width=True, hide_index=True)

            # Column hover explanation
            # (bisa ditambah lagi jika mau)

        # ==================== SCALPING SECTION ====================
        else:
            st.subheader("⚡ Section Scalping (Intraday)")
            st.info("Sinyal untuk trading harian / scalping")

            # ... (scalping code tetap sama seperti sebelumnya)

st.caption("Data dari Yahoo Finance • Bagian atas otomatis menampilkan emiten Akumulasi Kuat • Bukan rekomendasi trading")
