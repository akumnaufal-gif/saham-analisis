import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="IDX Stock Hunter", layout="wide", page_icon="🚀")
st.title("📈 IDX Stock Hunter")
st.markdown("**Deteksi Akumulasi Kuat & Rebound - Versi Stabil**")

st.sidebar.header("Pengaturan")
tickers_input = st.text_area("Ticker Manual (pisah koma)", 
    "DEWA, BUVA, BBCA, BBRI, BREN, ADRO, AMRT", height=80)

if st.button("🚀 Analisis Sekarang", type="primary", use_container_width=True):
    with st.spinner("Mengambil data..."):
        broad = ["DEWA","BUVA","BBCA","BBRI","BMRI","BBNI","TLKM","ASII","ADRO","BREN","AMRT","UNVR","BRIS","GOTO"]
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

                delta = hist['Close'].diff()
                gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
                rsi = 100 - (100 / (1 + gain/loss)) if loss != 0 else 50

                hist['OBV'] = (hist['Volume'] * np.sign(hist['Close'].diff())).cumsum()
                obv_now = hist['OBV'].iloc[-1]
                obv_30 = hist['OBV'].iloc[-31] if len(hist) > 30 else obv_now
                vol_recent = hist['Volume'].tail(10).mean()
                vol_avg = hist['Volume'].mean()
                price_30d = ((last['Close'] / hist['Close'].iloc[-31]) - 1) * 100 if len(hist) > 30 else 0
                vol_spike = round(vol_recent / vol_avg, 2)

                if (change > 4 and vol_spike > 1.75) or \
                   (change > 2.5 and vol_spike > 1.65 and rsi < 65) or \
                   (obv_now > obv_30 and vol_spike > 1.6 and rsi < 58):
                    akum = "💰 AKUMULASI KUAT"
                elif (obv_now > obv_30 and rsi < 62) or (rsi < 48):
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
                    'Vol Spike': vol_spike
                })
            except:
                continue

        df = pd.DataFrame(results)

        # ==================== TOP AKUMULASI ====================
        st.subheader("🏆 Top Emiten Akumulasi Kuat Hari Ini")
        top = df[df['Akumulasi / Distribusi'] == "💰 AKUMULASI KUAT"].sort_values('Change %', ascending=False).head(10)
        if not top.empty:
            st.success(f"✅ Ditemukan {len(top)} emiten Akumulasi Kuat")
            st.dataframe(top, use_container_width=True, hide_index=True)
        else:
            st.warning("Belum ada emiten Akumulasi Kuat saat ini.")

        # ==================== TABEL LENGKAP DENGAN WARNA ====================
        st.subheader("📋 Semua Hasil Analisa")

        def highlight_akum(val):
            if val == "💰 AKUMULASI KUAT":
                return 'background-color: #90EE90; color: black; font-weight: bold'
            elif val == "💰 Akumulasi Sedang":
                return 'background-color: #D4EDDA'
            elif val == "📉 DISTRIBUSI":
                return 'background-color: #FFB3B3'
            return ''

        # Styling
        styled_df = df.style.applymap(highlight_akum, subset=['Akumulasi / Distribusi'])

        # Column Config dengan Tooltip
        column_config = {
            "Trend": st.column_config.TextColumn("Trend", help="🟢 UPTREND = Harga di atas SMA20\n🔴 DOWNTREND = Harga di bawah SMA50"),
            "Akumulasi / Distribusi": st.column_config.TextColumn(
                "Akumulasi / Distribusi", 
                help="💰 AKUMULASI KUAT = Smart money masuk kuat (OBV naik + Volume tinggi + RSI tidak mahal)"
            ),
            "RSI": st.column_config.TextColumn("RSI (14)", help="RSI < 48 = Potensi naik (Oversold)"),
            "Vol Spike": st.column_config.TextColumn("Vol Spike", help="> 1.6 = Volume meningkat signifikan (sinyal kuat)")
        }

        st.dataframe(styled_df, use_container_width=True, hide_index=True, column_config=column_config)

st.caption("Logika realistis • Warna hijau = Akumulasi Kuat • Refresh berkala")
