import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Analisis Saham IDX", layout="wide", page_icon="📈")
st.title("📊 Screening Semua Emiten IDX")
st.markdown("**Trend • Akumulasi • RSI • Uptrend Filter**")

st.sidebar.header("Pengaturan")
tickers_input = st.sidebar.text_area("Ticker Manual (opsional)", "BBCA, BBRI, BMRI", height=100)

mode = st.radio("Pilih Mode", ["📋 Manual Ticker", "🔍 Screen Semua Emiten (Rekomendasi)"], horizontal=True)

if st.button("🚀 JALANKAN SCREENING", type="primary", use_container_width=True):
    with st.spinner("Mengambil data... (bisa agak lama di mode Screen All)"):
        if mode == "📋 Manual Ticker":
            tickers = [t.strip().upper() + ".JK" for t in tickers_input.split(",") if t.strip()]
        else:
            # Daftar saham populer + LQ45 (bisa ditambah)
            popular_tickers = [
                "BBCA","BBRI","BMRI","BBNI","TLKM","ASII","ADRO","GOTO","AMRT","UNVR",
                "BRIS","BTPS","CPIN","KLBF","MDKA","ANTM","INKP","PTBA","ADRO","BREN",
                "ISAT","EXCL","PGAS","PGEO","MEDC","SMGR","UNTR","SCMA","ICBP","INDF"
            ]
            tickers = [t + ".JK" for t in popular_tickers]
        
        results = []
        for ticker in tickers:
            try:
                hist = yf.Ticker(ticker).history(period="1y")
                if len(hist) < 100: continue
                
                last = hist.iloc[-1]
                change = round(((last['Close'] - hist.iloc[-2]['Close']) / hist.iloc[-2]['Close']) * 100, 2)
                
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
                
                # Akumulasi OBV
                hist['OBV'] = (hist['Volume'] * np.sign(hist['Close'].diff())).cumsum()
                obv_now = hist['OBV'].iloc[-1]
                obv_30 = hist['OBV'].iloc[-31] if len(hist) > 30 else obv_now
                price_change_30 = ((last['Close'] / hist['Close'].iloc[-31]) - 1) * 100 if len(hist) > 30 else 0
                
                vol_recent = hist['Volume'].tail(10).mean()
                vol_avg = hist['Volume'].mean()
                
                if (obv_now > obv_30) and abs(price_change_30) < 15 and vol_recent > vol_avg * 1.1 and rsi < 55:
                    akum = "💰 KUAT"
                elif obv_now > obv_30 and rsi < 60:
                    akum = "💰 Sedang"
                else:
                    akum = "Tidak"
                
                results.append({
                    'Ticker': ticker.replace('.JK', ''),
                    'Harga': round(last['Close'], 2),
                    'Change %': change,
                    'RSI': round(rsi, 1),
                    'Trend': trend,
                    'Akumulasi': akum,
                    '30d %': round(price_change_30, 1)
                })
            except:
                continue
        
        if results:
            df = pd.DataFrame(results)
            
            # Sorting prioritas
            df['Priority'] = df['Trend'].apply(lambda x: 0 if 'UPTREND' in x else 1)
            df = df.sort_values(['Priority', 'Akumulasi'], ascending=[True, False])
            
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.subheader("🔥 Rekomendasi Saat Ini")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Uptrend + Akumulasi Kuat**")
                st.dataframe(df[(df['Trend'].str.contains('UPTREND')) & (df['Akumulasi'].str.contains('KUAT'))])
            with col2:
                st.write("**RSI Rendah (Oversold)**")
                st.dataframe(df[df['RSI'] < 40])
            
            st.success(f"✅ Berhasil screening {len(df)} emiten!")
        else:
            st.error("Gagal mengambil data. Coba lagi.")

st.caption("Mode Screen All menggunakan daftar saham populer • Lebih lengkap = lebih lambat")
