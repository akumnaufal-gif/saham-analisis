import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime

st.set_page_config(page_title="IDX Stock Hunter Pro", layout="wide", page_icon="🚀")

st.title("📈 IDX Stock Hunter Pro")
st.markdown("**Pre-Surge · Probability Score · Bollinger Band · RSI · Stochastic · Entry Timing**")

# ── Sidebar ─────────────────────────────────────────────────────────────────
st.sidebar.header("⚙️ Pengaturan")
tickers_input = st.sidebar.text_area(
    "Ticker Manual (pisah koma)",
    "BALI, DEWA, BUVA, BBCA, BBRI, BREN, ADRO",
    height=80,
)
min_score = st.sidebar.slider("Min Probability Score (rekomendasi teratas)", 50, 90, 65)
show_detail = st.sidebar.checkbox("Tampilkan Detail Expander (Top 5)", value=True)

# ── Helper: RSI series ────────────────────────────────────────────────────
def calc_rsi_series(close, period=14):
    delta = close.diff()
    gain  = delta.where(delta > 0, 0.0).rolling(period).mean()
    loss  = (-delta.where(delta < 0, 0.0)).rolling(period).mean()
    rs    = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


# ── Helper: skip weekends ────────────────────────────────────────────────
def add_trading_days(start_date, n):
    d = start_date
    added = 0
    while added < n:
        d += datetime.timedelta(days=1)
        if d.weekday() < 5:   # Mon–Fri
            added += 1
    return d


# ── Main analysis ────────────────────────────────────────────────────────
if st.button("🚀 Analisis Sekarang", type="primary", use_container_width=True):
    with st.spinner("Menganalisis saham IDX..."):

        BROAD = [
            "BBCA","BBRI","BMRI","BBNI","TLKM","ASII","ADRO","AMRT","UNVR","CPIN",
            "KLBF","MDKA","ANTM","INKP","PTBA","PGAS","MEDC","SMGR","UNTR","ICBP",
            "INDF","SCMA","BRIS","BTPS","GOTO","BUKA","BREN","AMMN","AKRA","TPIA",
            "ARTO","EXCL","ISAT","PGEO","HRUM","ITMG","TAPG","RAJA","BUMI","CNKO",
            "SRTG","WOOD","TINS","ESSA","CUAN","WIFI","HRTA","PLAN","BMBL","HADE",
            "INDX","JPFA","CTRA","MAPA","GGRM","DSSA","MTEL","BKSL","CBDK","ABMM",
            "ACES","AALI","ADMR","BSSR","BYAN","DEWA","BUVA","JAST","MLPT","NCKL",
            "ABBA","ABDA","ACST","AADI","BALI","BULL",
        ]
        tickers = [t + ".JK" for t in BROAD]
        if tickers_input.strip():
            manual = [t.strip().upper() + ".JK" for t in tickers_input.split(",") if t.strip()]
            tickers = list(dict.fromkeys(manual + tickers))

        today = datetime.date.today()
        results = []
        progress = st.progress(0, text="Memulai…")

        for i, ticker in enumerate(tickers):
            progress.progress((i + 1) / len(tickers), text=f"Analisis {ticker}…")
            try:
                hist = yf.Ticker(ticker).history(period="4mo")
                if len(hist) < 60:
                    continue

                close  = hist["Close"]
                high   = hist["High"]
                low    = hist["Low"]
                volume = hist["Volume"]
                last   = hist.iloc[-1]
                prev   = hist.iloc[-2]

                change = round(((last["Close"] - prev["Close"]) / prev["Close"]) * 100, 2)

                # ── Trend (SMA20 / SMA50) ────────────────────────────────
                sma20 = close.rolling(20).mean().iloc[-1]
                sma50 = close.rolling(50).mean().iloc[-1]
                price = last["Close"]
                if price > sma20 and sma20 > sma50:
                    trend = "🟢 UPTREND"
                elif price < sma50:
                    trend = "🔴 DOWNTREND"
                else:
                    trend = "⚪ SIDEWAYS"

                # ── RSI (14) ─────────────────────────────────────────────
                rsi_ser  = calc_rsi_series(close, 14)
                rsi      = round(rsi_ser.iloc[-1], 1)
                rsi_prev = rsi_ser.iloc[-2]
                rsi_dir  = "naik" if rsi > rsi_prev else "turun"

                if rsi < 30:
                    rsi_label = "🟢 Sangat Oversold"
                    rsi_score = 25
                elif rsi < 45:
                    rsi_label = "🟡 Oversold"
                    rsi_score = 15
                elif rsi < 60:
                    rsi_label = "⚪ Netral"
                    rsi_score = 5
                elif rsi < 75:
                    rsi_label = "🟠 Overbought Ringan"
                    rsi_score = -5
                else:
                    rsi_label = "🔴 Overbought"
                    rsi_score = -15

                # ── MACD ─────────────────────────────────────────────────
                exp1      = close.ewm(span=12, adjust=False).mean()
                exp2      = close.ewm(span=26, adjust=False).mean()
                macd_line = exp1 - exp2
                sig_line  = macd_line.ewm(span=9, adjust=False).mean()
                macd_hist = macd_line - sig_line

                macd_bullish_cross = (
                    macd_line.iloc[-1] > sig_line.iloc[-1]
                    and macd_line.iloc[-2] <= sig_line.iloc[-2]
                )
                macd_above = macd_line.iloc[-1] > sig_line.iloc[-1]
                macd_score = 20 if macd_bullish_cross else (10 if macd_above else 0)

                # ── Bollinger Bands (20, 2σ) ──────────────────────────────
                bb_mid   = close.rolling(20).mean()
                bb_std   = close.rolling(20).std()
                bb_upper = (bb_mid + 2 * bb_std).iloc[-1]
                bb_lower = (bb_mid - 2 * bb_std).iloc[-1]
                bb_mid_v = bb_mid.iloc[-1]
                bb_width = round((bb_upper - bb_lower) / bb_mid_v * 100, 2)   # %
                bb_pct_b = round((price - bb_lower) / (bb_upper - bb_lower) * 100, 1)  # %B

                if price <= bb_lower:
                    bb_label = "🟢 Di Bawah Lower"
                    bb_score = 20
                elif price <= bb_mid_v:
                    bb_label = "🔵 Lower–Mid"
                    bb_score = 10
                elif price <= bb_upper:
                    bb_label = "⚪ Mid–Upper"
                    bb_score = 0
                else:
                    bb_label = "🔴 Di Atas Upper"
                    bb_score = -10

                # ── Stochastic Oscillator (14,3,3) ────────────────────────
                low14   = low.rolling(14).min()
                high14  = high.rolling(14).max()
                raw_k   = (close - low14) / (high14 - low14) * 100
                stoch_k = raw_k.rolling(3).mean()          # smooth %K
                stoch_d = stoch_k.rolling(3).mean()        # %D (signal)

                k_val   = round(stoch_k.iloc[-1], 1)
                d_val   = round(stoch_d.iloc[-1], 1)
                k_prev  = stoch_k.iloc[-2]
                d_prev  = stoch_d.iloc[-2]

                stoch_golden_cross = k_val > d_val and k_prev <= d_prev
                stoch_dead_cross   = k_val < d_val and k_prev >= d_prev

                if k_val < 20:
                    stoch_label = "🟢 Oversold"
                    stoch_score = 20
                elif k_val < 40:
                    stoch_label = "🟡 Mulai Naik"
                    stoch_score = 10
                elif k_val > 80:
                    stoch_label = "🔴 Overbought"
                    stoch_score = -10
                else:
                    stoch_label = "⚪ Netral"
                    stoch_score = 0

                if stoch_golden_cross and k_val < 30:
                    stoch_label += " ✨ Golden Cross"
                    stoch_score += 10

                # ── Volume & OBV ─────────────────────────────────────────
                vol_recent = volume.tail(10).mean()
                vol_avg    = volume.mean()
                vol_spike  = round(vol_recent / vol_avg, 2)

                hist["OBV"] = (volume * np.sign(close.diff())).cumsum()
                obv_now = hist["OBV"].iloc[-1]
                obv_30  = hist["OBV"].iloc[-31] if len(hist) > 30 else obv_now

                # ── Support & Resistance ─────────────────────────────────
                support    = round(low.tail(20).min(), 2)
                resistance = round(high.tail(20).max(), 2)

                # ── Probability Score ────────────────────────────────────
                score = 0
                if "UPTREND" in trend:        score += 15
                if obv_now > obv_30:          score += 10
                if vol_spike > 1.6:           score += 10
                score += rsi_score
                score += bb_score
                score += stoch_score
                score += macd_score
                score = max(0, min(100, score))

                # ── Akumulasi ────────────────────────────────────────────
                if (change > 3 and vol_spike > 1.7) or (obv_now > obv_30 and vol_spike > 1.65 and rsi < 62):
                    akum = "💰 AKUMULASI KUAT"
                elif obv_now > obv_30 or rsi < 48:
                    akum = "💰 Akumulasi Sedang"
                else:
                    akum = "—"

                # ── Pre-Surge ────────────────────────────────────────────
                if vol_spike > 2.5 and change > 2:
                    pre_surge = "🔥 POTENSI PUMP"
                elif vol_spike > 1.8:
                    pre_surge = "⚡ Potensi Naik Dini"
                else:
                    pre_surge = "—"

                # ── Trading Style ─────────────────────────────────────────
                if vol_spike > 2.5 and rsi > 65:
                    style  = "⚡ SCALPING / HARIAN"
                    style_reason = "Volume ekstrem + momentum kuat"
                elif score >= 75 and "UPTREND" in trend and vol_spike > 1.4:
                    style  = "📈 SWING TRADING"
                    style_reason = "Trend kuat + akumulasi bagus"
                elif score >= 60 and "Akumulasi" in akum:
                    style  = "📈 SWING TRADING"
                    style_reason = "Akumulasi + potensi reversal"
                else:
                    style  = "🕒 HOLD / MENENGAH"
                    style_reason = "Belum ada trigger kuat"

                # ── Entry Timing ─────────────────────────────────────────
                # Combinasi indikator → estimasi berapa hari lagi masuk
                strong_now = (
                    price <= bb_lower
                    and k_val < 25
                    and rsi < 38
                    and (stoch_golden_cross or rsi > rsi_prev)
                )
                moderate_now = (
                    (price <= bb_lower or k_val < 25 or rsi < 35)
                    and rsi > rsi_prev
                )
                setup_forming = (
                    (k_val < 40 and rsi < 50 and "UPTREND" in trend)
                    or (stoch_golden_cross and k_val < 50)
                    or (macd_bullish_cross and rsi < 55)
                )
                weak_setup = score >= 55

                if strong_now:
                    days_out   = 0
                    timing_tag = "⚡ MASUK SEKARANG"
                    timing_why = "BB Lower + Stoch Oversold + RSI oversold & mulai naik"
                elif moderate_now:
                    days_out   = 1
                    timing_tag = "📅 1–2 Hari Lagi"
                    timing_why = "Oversold zone — tunggu 1 hari konfirmasi"
                elif setup_forming:
                    days_out   = 3
                    timing_tag = "📅 ~3 Hari Lagi"
                    timing_why = "Setup sedang terbentuk, tunggu pullback minor"
                elif weak_setup:
                    days_out   = 5
                    timing_tag = "📅 ~1 Minggu"
                    timing_why = "Score cukup tapi sinyal belum kompak"
                else:
                    days_out   = 999
                    timing_tag = "⏳ Belum Waktunya"
                    timing_why = "Belum ada sinyal teknikal yang jelas"

                if days_out == 0:
                    est_date = "Hari Ini"
                elif days_out == 999:
                    est_date = "Tunggu Sinyal"
                else:
                    est_date = add_trading_days(today, days_out).strftime("%-d %b %Y")

                # ── Entry / SL / Target ──────────────────────────────────
                ideal_entry = round(price * 0.99, 2) if score >= 75 else round(support * 1.01, 2)
                stop_loss   = round(ideal_entry * 0.94, 2)
                target      = round(resistance, 2)
                rr_ratio    = round((target - ideal_entry) / max(ideal_entry - stop_loss, 1), 2)

                results.append({
                    "Ticker":        ticker.replace(".JK", ""),
                    "Harga":         round(price, 2),
                    "Change %":      change,
                    "Trend":         trend,
                    # RSI
                    "RSI":           rsi,
                    "RSI Signal":    rsi_label,
                    # Bollinger
                    "BB %B":         bb_pct_b,
                    "BB Width %":    bb_width,
                    "BB Signal":     bb_label,
                    # Stochastic
                    "Stoch %K":      k_val,
                    "Stoch %D":      d_val,
                    "Stoch Signal":  stoch_label,
                    # Akumulasi / Surge
                    "Akumulasi":     akum,
                    "Pre-Surge":     pre_surge,
                    # Score & Style
                    "Probability":   score,
                    "Style":         style,
                    "Style Reason":  style_reason,
                    # Entry Plan
                    "Entry":         ideal_entry,
                    "Stop Loss":     stop_loss,
                    "Target":        target,
                    "R:R":           f"1:{rr_ratio}",
                    "Vol Spike":     vol_spike,
                    # Timing
                    "Timing":        timing_tag,
                    "Est. Masuk":    est_date,
                    "Alasan Timing": timing_why,
                })

            except Exception:
                continue

        progress.empty()

        if not results:
            st.warning("Tidak ada data yang berhasil dianalisa.")
            st.stop()

        df = pd.DataFrame(results)

        # ── Kolom untuk tabel ringkasan ──────────────────────────────────
        SUMMARY_COLS = [
            "Ticker", "Harga", "Change %", "Trend",
            "RSI", "RSI Signal",
            "BB %B", "BB Signal",
            "Stoch %K", "Stoch %D", "Stoch Signal",
            "Probability", "Style",
            "Entry", "Stop Loss", "Target", "R:R",
            "Vol Spike", "Timing", "Est. Masuk",
        ]

        # ── Tab layout ────────────────────────────────────────────────────
        tab1, tab2, tab3 = st.tabs(["🔥 Rekomendasi Teratas", "📋 Semua Saham", "📊 Detail Teknikal"])

        with tab1:
            top = df[df["Probability"] >= min_score].sort_values("Probability", ascending=False)
            st.markdown(f"**{len(top)} saham** memenuhi syarat (score ≥ {min_score})")
            st.dataframe(top[SUMMARY_COLS], use_container_width=True, hide_index=True)

            if show_detail and not top.empty:
                st.divider()
                st.subheader("🔬 Detail Top 5")
                for _, row in top.head(5).iterrows():
                    with st.expander(
                        f"📌 {row['Ticker']}  |  Score: {row['Probability']}  |  {row['Timing']}"
                    ):
                        c1, c2, c3, c4, c5 = st.columns(5)
                        c1.metric("RSI", row["RSI"],
                                  delta=row["RSI Signal"].split(" ", 1)[-1] if " " in row["RSI Signal"] else "")
                        c2.metric("BB %B", f"{row['BB %B']}%",
                                  help="%B = 0% di Lower Band, 100% di Upper Band")
                        c3.metric("Stoch %K", row["Stoch %K"])
                        c4.metric("Stoch %D", row["Stoch %D"])
                        c5.metric("Vol Spike", f"{row['Vol Spike']}×")

                        st.info(
                            f"⏰ **Timing:** {row['Timing']}  ·  📅 **Est. Tanggal:** {row['Est. Masuk']}\n\n"
                            f"💡 {row['Alasan Timing']}"
                        )

                        ca, cb, cc = st.columns(3)
                        ca.metric("Entry Ideal",  f"Rp {row['Entry']:,.0f}")
                        cb.metric("Stop Loss",    f"Rp {row['Stop Loss']:,.0f}")
                        cc.metric("Target",       f"Rp {row['Target']:,.0f}")

                        st.caption(
                            f"Style: {row['Style']}  ·  Alasan: {row['Style Reason']}  ·  R:R = {row['R:R']}"
                        )

        with tab2:
            st.dataframe(
                df[SUMMARY_COLS].sort_values("Probability", ascending=False),
                use_container_width=True, hide_index=True,
            )

        with tab3:
            st.markdown("### Indikator Teknikal Lengkap")
            TECH_COLS = [
                "Ticker", "Harga", "Trend",
                "RSI", "RSI Signal",
                "BB %B", "BB Width %", "BB Signal",
                "Stoch %K", "Stoch %D", "Stoch Signal",
                "Akumulasi", "Pre-Surge", "Vol Spike",
                "Probability",
            ]
            st.dataframe(
                df[TECH_COLS].sort_values("Probability", ascending=False),
                use_container_width=True, hide_index=True,
            )

            # Mini legend
            with st.expander("📖 Keterangan Indikator"):
                st.markdown("""
| Indikator | Penjelasan |
|-----------|------------|
| **RSI** | < 30 = Sangat Oversold (potensi buy). > 70 = Overbought (hati-hati). |
| **BB %B** | 0% = harga di Lower Band (potential bounce). 100% = di Upper Band. |
| **BB Width %** | Makin kecil = Bollinger Squeeze → kemungkinan breakout dekat. |
| **Stoch %K** | < 20 = Oversold. > 80 = Overbought. Ikuti persilangan %K dan %D. |
| **Stoch Golden Cross** | %K memotong %D dari bawah saat keduanya di zona < 30 → sinyal beli kuat. |
| **Vol Spike** | Rasio volume 10 hari vs rata-rata. > 1.5 = volume mulai tinggi. |
| **Probability Score** | Skor 0–100 gabungan semua indikator di atas. ≥ 70 = setup bagus. |
| **Timing** | Estimasi kapan masuk berdasarkan kombinasi RSI + BB + Stochastic. |
                """)

st.caption(
    "Data: Yahoo Finance (yfinance)  ·  "
    "Indikator: SMA/EMA, RSI 14, MACD 12/26/9, Bollinger Band 20-2σ, Stochastic 14-3-3  ·  "
    "Bukan saran investasi — selalu lakukan riset sendiri."
)
