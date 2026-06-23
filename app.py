import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="IDX Stock Hunter", layout="wide", page_icon="📈")
st.title("📈 IDX Stock Hunter")
st.markdown("**Deteksi Akumulasi, Distribusi, Uptrend & Downtrend**")

st.sidebar.header("Pengaturan")
mode = st.sidebar.radio("Mode", ["🔍 Screening Utama", "⚡ Scalping Section"])

tickers_input = st.sidebar.text_area("Ticker Manual (opsional)", 
    "BBCA, BBRI, BMRI, BBNI, TLKM, ASII, ADRO, BREN, AMRT", height=80)

if st.sidebar.button("🚀 Analisis Sekarang", type="primary", use_container_width=True):
    with st.spinner("Mengambil data..."):
        if mode == "🔍 Screening Utama":
            if tickers_input.strip():
                tickers = [t.strip().upper() + ".JK" for t in tickers_input.split(",") if t.strip()]
            else:
                tickers = ["BBCA.JK","BBRI.JK","BMRI.JK","BBNI.JK","TLKM.JK","ASII.JK","ADRO.JK","BREN.JK","AMRT.JK"]

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

                    # Akumulasi vs Distribusi
                    if (obv_now > obv_30) and abs(price_30) < 15 and vol_recent > vol_avg * 1.1 and rsi < 55:
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

            if results:
                df = pd.DataFrame(results)

                # Column config dengan hover explanation
                column_config = {
                    "Trend": st.column_config.TextColumn(
                        "Trend",
                        help="🟢 UPTREND = Harga di atas SMA50 & SMA50 di atas SMA200\n🔴 DOWNTREND = Kebalikannya\n⚪ SIDEWAYS = Harga sedang konsolidasi"
                    ),
                    "Akumulasi / Distribusi": st.column_config.TextColumn(
                        "Akumulasi / Distribusi",
                        help="💰 AKUMULASI = Smart money sedang beli (OBV naik + volume tinggi + harga sideways)\n📉 DISTRIBUSI = Smart money sedang jual"
                    ),
                    "RSI": st.column_config.TextColumn(
                        "RSI (14)",
                        help="RSI < 40 = Oversold (potensi naik)\nRSI > 60 = Overbought (hati-hati)"
                    )
                }

                st.dataframe(df, use_container_width=True, hide_index=True, column_config=column_config)

                # === SECTION SCALPING KHUSUS ===
                st.subheader("⚡ Section Scalping (Intraday)")
                st.info("Sinyal untuk trading harian / scalping (data 5 menit / 15 menit)")

                scalping_results = []
                for ticker in tickers[:8]:  # batasi biar tidak terlalu lama
                    try:
                        data = yf.download(ticker, period="5d", interval="5m", progress=False)
                        if len(data) < 20: continue
                        last = data.iloc[-1]
                        rsi = 100 - (100 / (1 + (data['Close'].diff().where(data['Close'].diff() > 0, 0).rolling(14).mean().iloc[-1] / 
                                                (-data['Close'].diff().where(data['Close'].diff() < 0, 0).rolling(14).mean().iloc[-1])))) if data['Close'].diff().where(data['Close'].diff() < 0, 0).rolling(14).mean().iloc[-1] != 0 else 50
                        
                        if rsi < 35:
                            signal = "🟢 BUY (Oversold)"
                        elif rsi > 65:
                            signal = "🔴 SELL (Overbought)"
                        else:
                            signal = "⚪ Neutral"
                        
                        scalping_results.append({
                            'Ticker': ticker.replace('.JK',''),
                            'Harga': round(last['Close'],2),
                            'RSI 5m': round(rsi,1),
                            'Sinyal Scalping': signal
                        })
                    except:
                        continue

                if scalping_results:
                    st.dataframe(pd.DataFrame(scalping_results), use_container_width=True, hide_index=True)
                else:
                    st.warning("Data scalping belum tersedia (coba saat pasar buka)")

st.caption("Data dari Yahoo Finance • Hover pada judul kolom untuk penjelasan • Bukan rekomendasi trading")
