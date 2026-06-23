import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="IDX Stock Hunter Pro", layout="wide", page_icon="🚀")
st.title("🚀 IDX Stock Hunter Pro")
st.markdown("**Screening Saham Indonesia Terbaik**")

st.sidebar.header("Pengaturan")
mode = st.sidebar.radio("Pilih Mode", 
    ["🔍 Screen Semua Saham", "📋 Manual Ticker", "📊 Backtest", "📈 Heatmap Sektor"])

tickers_input = st.sidebar.text_area("Ticker Manual (pisah koma)", 
    "BBCA, BBRI, BMRI, BBNI, TLKM, ASII, ADRO, GOTO, AMRT, BREN, BUKA", height=80)

if st.sidebar.button("🚀 JALANKAN ANALISA", type="primary", use_container_width=True):
    with st.spinner("Mengambil data..."):
        results = []

        if mode in ["🔍 Screen Semua Saham", "📋 Manual Ticker"]:
            if mode == "📋 Manual Ticker":
                tickers = [t.strip().upper() + ".JK" for t in tickers_input.split(",") if t.strip()]
            else:
                popular = ["BBCA","BBRI","BMRI","BBNI","TLKM","ASII","ADRO","GOTO","AMRT","UNVR","BRIS","BTPS","CPIN","KLBF","MDKA","BREN"]
                tickers = [t + ".JK" for t in popular]

            for ticker in tickers:
                try:
                    hist = yf.Ticker(ticker).history(period="2y")
                    if len(hist) < 100: continue
                    last = hist.iloc[-1]
                    change = round(((last['Close'] - hist.iloc[-2]['Close']) / hist.iloc[-2]['Close']) * 100, 2)

                    sma50 = hist['Close'].rolling(50).mean().iloc[-1]
                    sma200 = hist['Close'].rolling(200).mean().iloc[-1]
                    trend = "🟢 UPTREND" if (last['Close'] > sma50 and sma50 > sma200) else "🔴 DOWNTREND" if (last['Close'] < sma50 and sma50 < sma200) else "⚪ SIDEWAYS"

                    delta = hist['Close'].diff()
                    gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
                    loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
                    rsi = 100 - (100 / (1 + gain/loss)) if loss != 0 else 50

                    hist['OBV'] = (hist['Volume'] * np.sign(hist['Close'].diff())).cumsum()
                    obv_now = hist['OBV'].iloc[-1]
                    obv_30 = hist['OBV'].iloc[-31] if len(hist) > 30 else obv_now
                    price_30 = ((last['Close'] / hist['Close'].iloc[-31]) - 1) * 100 if len(hist) > 30 else 0
                    vol_recent = hist['Volume'].tail(10).mean()
                    vol_avg = hist['Volume'].mean()

                    akum = "💰 KUAT" if (obv_now > obv_30 and abs(price_30) < 15 and vol_recent > vol_avg*1.15 and rsi < 55) else \
                           "💰 Sedang" if (obv_now > obv_30 and rsi < 60) else "Tidak"

                    score = 0
                    if "UPTREND" in trend: score += 35
                    if "KUAT" in akum: score += 30
                    elif "Sedang" in akum: score += 15
                    if rsi < 40: score += 20
                    if vol_recent > vol_avg * 1.2: score += 15

                    results.append({
                        'Ticker': ticker.replace('.JK',''), 'Harga':round(last['Close'],2),
                        'Change%':change, 'RSI':round(rsi,1), 'Trend':trend, 'Akumulasi':akum,
                        'Score':min(score,100), '30d%':round(price_30,1)
                    })
                except: continue

            df = pd.DataFrame(results).sort_values('Score', ascending=False)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # CHART INTERAKTIF (sudah diperbaiki)
            st.subheader("📈 Chart Interaktif")
            if not df.empty:
                selected = st.selectbox("Pilih saham untuk melihat chart", df['Ticker'].tolist())
                if selected:
                    try:
                        data = yf.download(selected + ".JK", period="6mo", progress=False)
                        if data.empty:
                            st.warning(f"Tidak ada data chart untuk {selected}")
                        else:
                            fig = go.Figure()
                            fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'],
                                                        low=data['Low'], close=data['Close'], name="Price"))
                            fig.add_trace(go.Scatter(x=data.index, y=data['Close'].rolling(20).mean(), 
                                                   name="SMA20", line=dict(color='orange')))
                            fig.add_trace(go.Scatter(x=data.index, y=data['Close'].rolling(50).mean(), 
                                                   name="SMA50", line=dict(color='blue')))
                            fig.update_layout(title=f"{selected} - 6 Bulan Terakhir", height=650)
                            st.plotly_chart(fig, use_container_width=True)
                    except:
                        st.error(f"Gagal memuat chart untuk {selected}. Coba ticker lain.")

        elif mode == "📊 Backtest":
            st.subheader("🔙 Backtest Strategi")
            ticker_bt = st.text_input("Masukkan Ticker untuk Backtest", "BBCA")
            if st.button("Jalankan Backtest"):
                try:
                    hist = yf.Ticker(ticker_bt + ".JK").history(period="2y")
                    if len(hist) > 100:
                        hist['Return'] = hist['Close'].pct_change()
                        hist['Signal'] = (hist['Close'] > hist['Close'].rolling(50).mean()) & (hist['Close'].rolling(50).mean() > hist['Close'].rolling(200).mean())
                        hist['Strategy'] = hist['Signal'].shift(1) * hist['Return']
                        
                        total = (1 + hist['Strategy']).prod() - 1
                        buyhold = (hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1
                        
                        col1, col2 = st.columns(2)
                        col1.metric("Strategi Return", f"{total:.1%}")
                        col2.metric("Buy & Hold Return", f"{buyhold:.1%}")
                        st.line_chart(hist[['Close', 'Strategy']].cumsum())
                except:
                    st.error("Gagal menjalankan backtest. Coba ticker lain.")

st.caption("Score = Gabungan indikator terbaik • Semakin tinggi semakin bagus • Bukan rekomendasi trading")
