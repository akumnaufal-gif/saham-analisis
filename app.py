import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="IDX Stock Hunter", layout="wide", page_icon="🚀")
st.title("📈 IDX Stock Hunter - Dengan Entry Strategy")
st.markdown("**Deteksi Akumulasi + Rekomendasi Entry Zone**")

st.sidebar.header("Pengaturan")
tickers_input = st.text_area("Ticker Manual (pisah koma)", 
    "DEWA, BUVA, BBCA, BBRI, BREN, ADRO", height=80)

if st.button("🚀 Analisis Sekarang", type="primary", use_container_width=True):
    with st.spinner("Menganalisis..."):
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
                recent_high = hist['Close'].tail(20).max()
                recent_low = hist['Close'].tail(20).min()

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
                vol_spike = round(vol_recent / vol_avg, 2)

                price_30d = ((last['Close'] / hist['Close'].iloc[-31]) - 1) * 100 if len(hist) > 30 else 0

                # Logika Akumulasi
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

                # === ENTRY STRATEGY ===
                if "AKUMULASI KUAT" in akum:
                    if "UPTREND" in trend:
                        entry_price = round(sma20, 2)
                        entry_note = "Pullback ke SMA20"
                    else:
                        entry_price = round(recent_high * 1.01, 2)
                        entry_note = "Breakout di atas recent high"
                elif "Akumulasi Sedang" in akum and "DOWNTREND" in trend:
                    entry_price = round(sma20, 2)
                    entry_note = "Tunggu break SMA20 ke atas"
                else:
                    entry_price = round(last['Close'], 2)
                    entry_note = "Ikuti harga saat ini"

                results.append({
                    'Ticker': ticker.replace('.JK',''),
                    'Harga Saat Ini': round(last['Close'], 2),
                    'Change %': change,
                    'Trend': trend,
                    'Akumulasi': akum,
                    'Vol Spike': vol_spike,
                    'Entry Harga': entry_price,
                    'Entry Note': entry_note
                })
            except:
                continue

        df = pd.DataFrame(results)

        # Top Akumulasi
        st.subheader("🏆 Top Emiten Akumulasi Kuat + Entry Strategy")
        top = df[df['Akumulasi'].str.contains("KUAT")].sort_values('Change %', ascending=False)
        if not top.empty:
            st.dataframe(top, use_container_width=True, hide_index=True)
        else:
            st.warning("Belum ada emiten Akumulasi Kuat.")

        # Semua Hasil
        st.subheader("📋 Semua Hasil + Entry Suggestion")
        st.dataframe(df, use_container_width=True, hide_index=True)

st.caption("Entry Strategy hanya sebagai referensi berdasarkan indikator • Bukan rekomendasi trading • Selalu gunakan risk management")
