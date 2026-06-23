import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="IDX Stock Hunter Pro", layout="wide", page_icon="🚀")
st.title("📈 IDX Stock Hunter Pro")
st.markdown("**Pre-Surge Detector + MACD + Probability Score + Entry Strategy**")

st.sidebar.header("Pengaturan")
tickers_input = st.text_area("Ticker Manual (pisah koma)", 
    "BALI, DEWA, BUVA, BBCA, BBRI, BREN, ADRO", height=80)

if st.button("🚀 Analisis Sekarang", type="primary", use_container_width=True):
    with st.spinner("Menganalisis..."):
        broad = ["BALI","DEWA","BUVA","BBCA","BBRI","BMRI","BBNI","TLKM","ASII","ADRO","BREN","AMRT","UNVR","BRIS","GOTO","BUKA"]
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

                # Trend
                sma20 = hist['Close'].rolling(20).mean().iloc[-1]
                sma50 = hist['Close'].rolling(50).mean().iloc[-1]
                trend = "🟢 UPTREND" if last['Close'] > sma20 else "🔴 DOWNTREND" if last['Close'] < sma50 else "⚪ SIDEWAYS"

                # RSI
                delta = hist['Close'].diff()
                gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
                rsi = 100 - (100 / (1 + gain/loss)) if loss != 0 else 50

                # MACD
                exp1 = hist['Close'].ewm(span=12, adjust=False).mean()
                exp2 = hist['Close'].ewm(span=26, adjust=False).mean()
                macd = exp1 - exp2
                signal = macd.ewm(span=9, adjust=False).mean()
                macd_hist = macd - signal
                macd_signal = "Bullish" if macd_hist.iloc[-1] > 0 else "Bearish"

                # Volume & OBV
                hist['OBV'] = (hist['Volume'] * np.sign(hist['Close'].diff())).cumsum()
                obv_now = hist['OBV'].iloc[-1]
                obv_30 = hist['OBV'].iloc[-31] if len(hist) > 30 else obv_now
                vol_recent = hist['Volume'].tail(10).mean()
                vol_avg = hist['Volume'].mean()
                vol_spike = round(vol_recent / vol_avg, 2)

                # Support & Resistance
                support = round(hist['Close'].tail(20).min(), 2)
                resistance = round(hist['Close'].tail(20).max(), 2)

                # Probability Score
                score = 0
                if "UPTREND" in trend: score += 25
                if rsi < 50: score += 20
                if macd_hist.iloc[-1] > 0: score += 20
                if vol_spike > 1.6: score += 20
                if obv_now > obv_30: score += 15
                score = min(100, score)

                # Akumulasi
                if (change > 3 and vol_spike > 1.7) or (obv_now > obv_30 and vol_spike > 1.65 and rsi < 62):
                    akum = "💰 AKUMULASI KUAT"
                elif obv_now > obv_30 or rsi < 48:
                    akum = "💰 Akumulasi Sedang"
                else:
                    akum = "Tidak Jelas"

                # Pre-Surge Detector
                if vol_spike > 2.5 and change > 2:
                    pre_surge = "🔥 POTENSI PUMP KUAT"
                elif vol_spike > 1.8 and rsi < 65:
                    pre_surge = "⚡ Potensi Naik Dini"
                else:
                    pre_surge = "-"

                # Entry Strategy
                if score >= 80:
                    entry = round(last['Close'] * 0.985, 2)
                    note = "Entry sekarang"
                else:
                    entry = round(support * 1.01, 2)
                    note = "Tunggu dekat support"

                stop_loss = round(entry * 0.94, 2)
                target = round(resistance, 2)
                rr = round((target - entry) / (entry - stop_loss), 2) if (entry - stop_loss) > 0 else 0

                results.append({
                    'Ticker': ticker.replace('.JK',''),
                    'Harga': round(last['Close'], 2),
                    'Change %': change,
                    'Trend': trend,
                    'Akumulasi': akum,
                    'Pre-Surge': pre_surge,
                    'Probability': score,
                    'Entry': entry,
                    'Stop Loss': stop_loss,
                    'Target': target,
                    'R:R': f"1:{rr}",
                    'Vol Spike': vol_spike,
                    'RSI': round(rsi, 1)
                })
            except:
                continue

        df = pd.DataFrame(results)

        # Top Pre-Surge & High Probability
        st.subheader("🔥 Top Pre-Surge + Probability Tinggi")
        top = df[(df['Pre-Surge'] != "-") | (df['Probability'] >= 75)].sort_values('Probability', ascending=False)
        if not top.empty:
            st.dataframe(top, use_container_width=True, hide_index=True)
        else:
            st.warning("Belum ada sinyal kuat saat ini.")

        st.subheader("📋 Semua Hasil Analisa")
        st.dataframe(df.sort_values('Probability', ascending=False), use_container_width=True, hide_index=True)

st.caption("Pre-Surge = Deteksi dini potensi naik tajam • Probability Score semakin tinggi = semakin kuat sinyal • Refresh berkala")
