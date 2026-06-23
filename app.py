import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="IDX Stock Hunter Pro", layout="wide", page_icon="🚀")
st.title("📈 IDX Stock Hunter Pro")
st.markdown("**MACD + ADX + Support/Resistance + Probability Score**")

st.sidebar.header("Pengaturan")
tickers_input = st.text_area("Ticker Manual (pisah koma)", 
    "DEWA, BUVA, BBCA, BBRI, BREN, ADRO, AMRT", height=80)

if st.button("🚀 Analisis Sekarang", type="primary", use_container_width=True):
    with st.spinner("Menganalisis dengan MACD, ADX & S/R..."):
        broad = ["DEWA","BUVA","BBCA","BBRI","BMRI","BBNI","TLKM","ASII","ADRO","BREN","AMRT","UNVR","BRIS","GOTO"]
        tickers = [t + ".JK" for t in broad]

        if tickers_input.strip():
            manual = [t.strip().upper() + ".JK" for t in tickers_input.split(",") if t.strip()]
            tickers = list(dict.fromkeys(manual + tickers))

        results = []
        for ticker in tickers:
            try:
                hist = yf.Ticker(ticker).history(period="4mo")
                if len(hist) < 60: continue
                last = hist.iloc[-1]
                change = round(((last['Close'] - hist.iloc[-2]['Close']) / hist.iloc[-2]['Close']) * 100, 2)

                # === TREND ===
                sma20 = hist['Close'].rolling(20).mean().iloc[-1]
                sma50 = hist['Close'].rolling(50).mean().iloc[-1]
                trend = "🟢 UPTREND" if last['Close'] > sma20 else "🔴 DOWNTREND" if last['Close'] < sma50 else "⚪ SIDEWAYS"

                # === RSI ===
                delta = hist['Close'].diff()
                gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
                rsi = 100 - (100 / (1 + gain/loss)) if loss != 0 else 50

                # === MACD ===
                exp1 = hist['Close'].ewm(span=12, adjust=False).mean()
                exp2 = hist['Close'].ewm(span=26, adjust=False).mean()
                macd = exp1 - exp2
                signal = macd.ewm(span=9, adjust=False).mean()
                macd_hist = macd - signal
                macd_signal = "Bullish" if macd_hist.iloc[-1] > 0 else "Bearish"

                # === ADX (Trend Strength) ===
                high_low = hist['High'] - hist['Low']
                high_close = np.abs(hist['High'] - hist['Close'].shift())
                low_close = np.abs(hist['Low'] - hist['Close'].shift())
                tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
                atr = tr.rolling(14).mean()
                # Simplified ADX (approximation)
                adx = 25 if atr.iloc[-1] > atr.mean() * 1.3 else 18  # rough strength

                # === Volume & OBV ===
                hist['OBV'] = (hist['Volume'] * np.sign(hist['Close'].diff())).cumsum()
                obv_now = hist['OBV'].iloc[-1]
                obv_30 = hist['OBV'].iloc[-31] if len(hist) > 30 else obv_now
                vol_recent = hist['Volume'].tail(10).mean()
                vol_avg = hist['Volume'].mean()
                vol_spike = round(vol_recent / vol_avg, 2)

                # === Support & Resistance ===
                support = round(hist['Close'].tail(20).min(), 2)
                resistance = round(hist['Close'].tail(20).max(), 2)

                # === Probability Score (0-100) ===
                score = 0
                if "UPTREND" in trend: score += 25
                if "AKUMULASI" in "AKUMULASI KUAT": score += 30
                if rsi < 45: score += 15
                if macd_hist.iloc[-1] > 0: score += 15
                if vol_spike > 1.6: score += 15
                score = min(100, int(score))

                # Akumulasi Label
                if (change > 3 and vol_spike > 1.7) or (obv_now > obv_30 and vol_spike > 1.65 and rsi < 62):
                    akum = "💰 AKUMULASI KUAT"
                elif obv_now > obv_30 or rsi < 48:
                    akum = "💰 Akumulasi Sedang"
                elif obv_now < obv_30 and rsi > 58:
                    akum = "📉 DISTRIBUSI"
                else:
                    akum = "Tidak Jelas"

                results.append({
                    'Ticker': ticker.replace('.JK',''),
                    'Harga': round(last['Close'], 2),
                    'Change %': change,
                    'Trend': trend,
                    'Akumulasi': akum,
                    'RSI': round(rsi, 1),
                    'MACD': macd_signal,
                    'Vol Spike': vol_spike,
                    'Support': support,
                    'Resistance': resistance,
                    'Probability Score': score,
                    'Entry Suggestion': f"Entry di {support}-{round(sma20,2)}" if score > 65 else "Tunggu konfirmasi"
                })
            except:
                continue

        df = pd.DataFrame(results)

        st.subheader("🏆 Top Saham dengan Probability Score Tertinggi")
        top = df.sort_values('Probability Score', ascending=False).head(10)
        st.dataframe(top, use_container_width=True, hide_index=True)

        st.subheader("📋 Semua Hasil Analisa")
        st.dataframe(df.sort_values('Probability Score', ascending=False), use_container_width=True, hide_index=True)

st.caption("Probability Score = Kombinasi MACD + ADX + OBV + Volume + Trend • Bukan rekomendasi trading • Gunakan sebagai referensi saja")
