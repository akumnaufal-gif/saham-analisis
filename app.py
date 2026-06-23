import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="IDX Stock Hunter Pro", layout="wide", page_icon="🚀")
st.title("🚀 IDX Stock Hunter Pro")
st.markdown("**Aplikasi Screening Saham Indonesia Terlengkap** — Kombinasi Indikator Terbaik")

# ==================== SIDEBAR ====================
st.sidebar.header("⚙️ Filter & Pengaturan")

tickers_input = st.sidebar.text_area("Ticker Manual (opsional)", 
    "BBCA, BBRI, BMRI, BBNI, TLKM, ASII, ADRO, GOTO, AMRT, UNVR, BRIS, CPIN, KLBF, MDKA", 
    height=100)

mode = st.sidebar.radio("Mode Analisa", 
    ["🔍 Screen Semua (Rekomendasi)", "📋 Manual Ticker"])

min_score = st.sidebar.slider("Minimum Composite Score", 0, 100, 60)
show_only_uptrend = st.sidebar.checkbox("Hanya tampilkan UPTREND", value=True)
show_only_akum = st.sidebar.checkbox("Hanya tampilkan Akumulasi Kuat/Sedang", value=False)

if st.sidebar.button("🚀 JALANKAN SCREENING", type="primary", use_container_width=True):
    if mode == "📋 Manual Ticker":
        tickers = [t.strip().upper() + ".JK" for t in tickers_input.split(",") if t.strip()]
    else:
        # Daftar saham populer (bisa kamu tambah sendiri)
        popular = ["BBCA","BBRI","BMRI","BBNI","TLKM","ASII","ADRO","GOTO","AMRT","UNVR",
                   "BRIS","BTPS","CPIN","KLBF","MDKA","ANTM","INKP","PTBA","BREN","ISAT",
                   "EXCL","PGAS","MEDC","SMGR","UNTR","ICBP","INDF","SCMA","PGAS","PGEO"]
        tickers = [t + ".JK" for t in popular]

    with st.spinner("Menganalisis saham... (bisa 1-3 menit)"):
        results = []
        for ticker in tickers:
            try:
                hist = yf.Ticker(ticker).history(period="2y")
                if len(hist) < 100: continue
                last = hist.iloc[-1]
                
                # === INDICATORS ===
                change = round(((last['Close'] - hist.iloc[-2]['Close']) / hist.iloc[-2]['Close']) * 100, 2)
                
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
                
                # OBV Akumulasi
                hist['OBV'] = (hist['Volume'] * np.sign(hist['Close'].diff())).cumsum()
                obv_now = hist['OBV'].iloc[-1]
                obv_30 = hist['OBV'].iloc[-31] if len(hist) > 30 else obv_now
                price_change_30 = ((last['Close'] / hist['Close'].iloc[-31]) - 1) * 100 if len(hist) > 30 else 0
                vol_recent = hist['Volume'].tail(10).mean()
                vol_avg = hist['Volume'].mean()
                
                if (obv_now > obv_30) and abs(price_change_30) < 15 and vol_recent > vol_avg * 1.15 and rsi < 55:
                    akum = "💰 KUAT"
                elif obv_now > obv_30 and rsi < 60:
                    akum = "💰 Sedang"
                else:
                    akum = "Tidak"
                
                # Composite Score (0-100)
                score = 0
                if "UPTREND" in trend: score += 30
                if "KUAT" in akum: score += 25
                elif "Sedang" in akum: score += 15
                if rsi < 40: score += 20
                elif rsi < 50: score += 10
                if vol_recent > vol_avg * 1.2: score += 15
                if abs(price_change_30) < 10: score += 10
                
                results.append({
                    'Ticker': ticker.replace('.JK', ''),
                    'Harga': round(last['Close'], 2),
                    'Change %': change,
                    'RSI': round(rsi, 1),
                    'Trend': trend,
                    'Akumulasi': akum,
                    'Composite Score': min(score, 100),
                    '30d Change %': round(price_change_30, 1)
                })
            except:
                continue
        
        if results:
            df = pd.DataFrame(results)
            
            # Filter
            if show_only_uptrend:
                df = df[df['Trend'].str.contains('UPTREND')]
            if show_only_akum:
                df = df[df['Akumulasi'].str.contains('KUAT|Sedang')]
            df = df[df['Composite Score'] >= min_score]
            
            # Sort by score
            df = df.sort_values('Composite Score', ascending=False)
            
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.subheader("🏆 Top 10 Saham Terbaik Saat Ini")
            st.dataframe(df.head(10), use_container_width=True)
            
            st.success(f"✅ Berhasil menganalisis {len(df)} saham!")
        else:
            st.error("Gagal mengambil data.")

st.markdown("---")
st.warning("⚠️ **PENTING**: Tidak ada aplikasi yang bisa memberikan akurasi 100%. Ini adalah alat screening terbaik yang bisa dibuat dengan data saat ini. Selalu lakukan analisa sendiri + gunakan manajemen risiko.")
