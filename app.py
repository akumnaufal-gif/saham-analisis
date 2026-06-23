import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="IDX Stock Hunter", layout="wide", page_icon="🚀")
st.title("📈 IDX Stock Hunter")
st.markdown("**Deteksi Akumulasi Kuat • Uptrend • Distribusi**")

st.sidebar.header("Pengaturan")
tickers_input = st.sidebar.text_area("Tambah Ticker Manual (pisah koma)", 
    "BBCA, BBRI, BMRI, BBNI, TLKM, ASII, ADRO, BREN, AMRT, GOTO", height=80)

if st.sidebar.button("🚀 Analisis Sekarang", type="primary", use_container_width=True):
    with st.spinner("Mengambil data dan menganalisis..."):
        tickers = [t.strip().upper() + ".JK" for t in tickers_input.split(",") if t.strip()]
        
        # Default ticker jika kosong
        if not tickers:
            tickers = ["BBCA.JK","BBRI.JK","BMRI.JK","BBNI.JK","TLKM.JK","ASII.JK","ADRO.JK","BREN.JK",
                       "AMRT.JK","UNVR.JK","BRIS.JK","CPIN.JK","KLBF.JK","MDKA.JK"]

        results = []
        for ticker in tickers:
            try:
                hist = yf.Ticker(ticker).history(period="2y")
                if len(hist) < 100: continue
                last = hist.iloc[-1]

                # Trend
                sma50 = hist['Close'].rolling(50).mean().iloc[-1]
                sma200 = hist['Close'].rolling(200).mean().iloc[-1]
                trend = "🟢 UPTREND" if (last['Close'] > sma50 and sma50 > sma200) else \
                        "🔴 DOWNTREND" if (last['Close'] < sma50 and sma50 < sma200) else "⚪ SIDEWAYS"

                # RSI
                delta = hist['Close'].diff()
                gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
                rsi = 100 - (100 / (1 + gain/loss)) if loss != 0 else 50

                # OBV untuk Akumulasi
                hist['OBV'] = (hist['Volume'] * np.sign(hist['Close'].diff())).cumsum()
                obv_now = hist['OBV'].iloc[-1]
                obv_30 = hist['OBV'].iloc[-31] if len(hist) > 30 else obv_now
                price_30 = ((last['Close'] / hist['Close'].iloc[-31]) - 1) * 100 if len(hist) > 30 else 0
                vol_recent = hist['Volume'].tail(10).mean()
                vol_avg = hist['Volume'].mean()

                # Logika Akumulasi
                if (obv_now > obv_30) and abs(price_30) < 15 and vol_recent > vol_avg * 1.15 and rsi < 55:
                    akum_status = "💰 AKUMULASI KUAT"
                elif obv_now > obv_30 and rsi < 60:
                    akum_status = "💰 Akumulasi Sedang"
                elif obv_now < obv_30 and rsi > 55:
                    akum_status = "📉 DISTRIBUSI"
                else:
                    akum_status = "Tidak Jelas"

                results.append({
                    'Ticker': ticker.replace('.JK',''),
                    'Harga': round(last['Close'], 2),
                    'Change %': round(((last['Close'] - hist.iloc[-2]['Close']) / hist.iloc[-2]['Close']) * 100, 2),
                    'RSI': round(rsi, 1),
                    'Trend': trend,
                    'Akumulasi/Distribusi': akum_status,
                    '30 Hari %': round(price_30, 1),
                    'Score': 85 if "KUAT" in akum_status else 65 if "Sedang" in akum_status else 40
                })
            except:
                continue

        df = pd.DataFrame(results)

        # ==================== TOP 10 AKUMULASI KUAT ====================
        st.subheader("🏆 TOP 10 EMITEN DENGAN AKUMULASI KUAT HARI INI")
        top10 = df[df['Akumulasi/Distribusi'] == "💰 AKUMULASI KUAT"].sort_values('Score', ascending=False).head(10)
        
        if not top10.empty:
            st.dataframe(top10[['Ticker', 'Harga', 'Change %', 'RSI', 'Trend', '30 Hari %']], 
                        use_container_width=True, hide_index=True)
            st.success(f"✅ Ditemukan {len(top10)} emiten dengan Akumulasi Kuat")
        else:
            st.warning("Belum ada emiten yang memenuhi kriteria Akumulasi Kuat saat ini.")

        # ==================== TABEL LENGKAP ====================
        st.subheader("📋 Semua Hasil Analisa")
        st.dataframe(df.sort_values('Score', ascending=False), use_container_width=True, hide_index=True)

        # ==================== SCALPING SECTION ====================
        st.subheader("⚡ Sinyal Scalping (Intraday)")
        st.info("Update saat pasar buka untuk hasil terbaik")
        # (bisa di-expand nanti)

st.caption("💡 Hover pada kolom untuk penjelasan • Data real-time dari Yahoo Finance • Bukan rekomendasi trading")
