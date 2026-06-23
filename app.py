import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Analisis Saham IDX", layout="wide")
st.title("📈 Analisis Emiten Saham Indonesia")

st.sidebar.header("Pengaturan")
tickers_input = st.sidebar.text_area(
    "Masukkan Ticker (pisah dengan koma)", 
    "BBCA, BBRI, BMRI, BBNI, TLKM, ASII, ADRO, GOTO, AMRT",
    height=150
)

if st.sidebar.button("🚀 Analisis Sekarang", type="primary"):
    tickers = [t.strip().upper() + ".JK" for t in tickers_input.split(",") if t.strip()]
    
    with st.spinner("Mengambil data dari Yahoo Finance..."):
        results = []
        for ticker in tickers:
            try:
                hist = yf.Ticker(ticker).history(period="1y")
                if len(hist) < 30:
                    continue
                last = hist.iloc[-1]
                prev = hist.iloc[-2]
                change = round(((last['Close'] - prev['Close']) / prev['Close']) * 100, 2)
                
                results.append({
                    'Ticker': ticker.replace('.JK', ''),
                    'Harga': round(last['Close'], 2),
                    'Change %': change,
                    'RSI': 'N/A',
                    'Trend': 'N/A'
                })
            except:
                pass
        
        if results:
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
            st.success(f"✅ Berhasil menganalisis {len(df)} emiten!")
        else:
            st.error("Tidak ada data yang berhasil diambil.")
