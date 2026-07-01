import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime

st.set_page_config(page_title="IDX Stock Hunter Pro", layout="wide", page_icon="🚀")

st.title("📈 IDX Stock Hunter Pro")
st.markdown("**Pre-Surge · BB · RSI · Stochastic · Entry Timing · Gocap Watch**")

# ─────────────────────────────────────────────────────────────────────────────
# TICKER MASTER LIST
# ─────────────────────────────────────────────────────────────────────────────
LAYER1 = [
    "BBCA","BBRI","BMRI","BBNI","TLKM","ASII","ADRO","AMRT","UNVR","CPIN",
    "KLBF","MDKA","ANTM","INKP","PTBA","PGAS","MEDC","SMGR","UNTR","ICBP",
    "INDF","SCMA","BRIS","BTPS","GOTO","BUKA","BREN","AMMN","AKRA","TPIA",
    "EXCL","ISAT","PGEO","HRUM","ITMG","TAPG","RAJA","CNKO","SRTG","WOOD",
    "TINS","ESSA","CUAN","WIFI","HRTA","PLAN","BMBL","HADE","INDX","JPFA",
    "CTRA","MAPA","GGRM","DSSA","MTEL","BKSL","CBDK","ABMM","ACES","AALI",
    "ADMR","BSSR","BYAN","DEWA","BUVA","JAST","MLPT","NCKL","BULL","BUMI",
    "BALI","BELL",
]

LAYER2 = [
    # Perbankan & Keuangan
    "MEGA","NISP","BNLI","BNGA","BDMN","BJBR","BJTM","PNBS","MAYA","NOBU",
    "AGRO","BMAS","BCIC","MCOR","DNAR","AMAR",
    # Properti
    "LPKR","SMRA","CTRA","PWON","BSDE","MTLA","BEST","DILD","KIJA","NIRO",
    "MKPI","PPRO","SMDM","GPSO","OMRE","GWSA","PJAA","JSPT","KPIG",
    # Energi & Tambang
    "ELSA","INDY","PTRO","RUIS","SMMT","MBAP","KKGI","PKPK","DOID","GEMS",
    "INPC","ENRG","GZCO","SSMS","SGRO","SIMP","PALM","LSIP","TBLA",
    # Konsumer & Ritel
    "ROTI","MYOR","SIDO","HOKI","SKBM","SKLT","WIIM","GOOD","COCO","BOBA",
    "LPPF","RALS","MAPI","MIKA","SILO","HERO","TGKA","TIRA","MTDL","EPMT",
    # Industri & Manufaktur
    "SMCB","WTON","TOTO","LION","LMSH","KBLI","KBLM","SCCO","SPMA","TRST",
    "IMPC","IGAR","ISSP","LAMI","PICO","YPAS","UNIC","SOCI","GJTL","INDS",
    # Teknologi & Telco
    "SUPR","TBMS","IBST","GHON","MTDL","GLOB","CASH","ARTO","PYFA",
    # Konstruksi & Infrastruktur
    "TOTL","WIKA","WSKT","PTPP","NRCA","JKPL","PBID","CSIS",
    # Lain-lain
    "TURI","MPPA","PDES","TOPS","LUCK","KREN","NELY","FORU","PLAS",
]

LAYER3_SPECULATIVE = [
    # Layer 3 dan saham spekulatif aktif
    "ARMY","BHAT","BIMA","BLTZ","BPTR","BSML","CARS","CBPE","CCSI",
    "CLAY","DAJK","DOSS","DPUM","DWGL","EAST","FIRE","FLMC","FMII",
    "GAMA","GETS","HOTL","HRME","HKMU","IIKP","IKAI","INCI","ISAP",
    "ITMA","ITIC","JAWA","JKSW","JSPT","KOIN","KONI","KPAL","KRAS",
    "LCKM","LEAD","LMPI","LPGI","MABA","MAMI","MDRN","MGRO","MITI",
    "MPOW","MRPH","MSIN","MTRA","MYRX","NASI","NETV","NICK","NKPI",
    "NUSA","OBMD","OCAP","OKAS","PADI","PANR","PBRX","PCAR","PBID",
    "PMMP","PNGO","POLA","PTIS","PTSP","PUDP","PURA","RBMS","RIMO",
    "SAFE","SDMU","SFAN","SIMA","SMBR","SMDR","SONA","SRAJ","STAR",
    "SUGI","TBIG","TCPI","TEBE","TKGA","TKIM","TMAS","TMPO","TNCA",
    "UANG","UNIT","UNSP","VICO","VINS","VIVA","WICO","WINS","YULE",
    "ZBRA","BHAT","ABBA","ABDA","ACST","AADI","FREN","MNCN","MLBI",
    "KREN","PNBS","ROTI","WIIM","NUSA","AIMS","ANDI","APEX","APLI",
    "ARNA","ARTI","ASBI","ASMI","ASSA","ATAP","ATPK","AUDA","AYTV",
    "BACA","BAJA","BANK","BAPA","BATA","BBLD","BCAP","BCIP","BDKI",
    "BEKS","BFIN","BGTG","BHAT","BHIT","BIKA","BIMA","BIPI","BIRD",
    "BMSR","BNBR","BOSS","BRMS","BSDE","BTEK","BTON","BUDI","CAKK",
    "CASS","CEKA","CFIN","CITY","CLPI","CMPP","CNTB","COAL","COWL",
    "CPIN","CPRI","CSAP","CTRA","CUAN","CYBR","DART","DAYS","DEWA",
    "DIGI","DKFT","DLTA","DNET","DPNS","DRMA","DSFI","DSNG","DUCK",
    "DUTI","ECII","EDGE","EMDE","EMTK","ENAK","ENZO","ERAA","ESTE",
    "FAST","FILM","FITT","FWCT","GEMA","GEPO","GHON","GJTL","GLOB",
    "GOLL","GRIS","GTSI","HAIS","HDFA","HEAL","HEXA","HMSP","HOKI",
    "HOTL","HRUM","IBFN","IBST","IKAI","IKBI","IMAS","IMJS","IMPC",
    "INAI","INCI","INDO","INDR","INDS","INPP","INSW","IPCC","IPCM",
    "IPOL","IPPE","ISAP","JMAS","JRPT","JTPE","KAEF","KARW","KEEN",
    "KIAS","KICI","KIMI","KMTR","KOBX","KOKA","KPAS","KRAS","LAUT",
]

GOCAP_WATCHLIST = [
    # Saham yang sering main di area gocap-200 dengan potensi naik drastis
    "BUMI","CNKO","DEWA","ENRG","FMII","GAMA","GPSO","GWSA","GZCO",
    "IIKP","IKAI","INPC","JAWA","JKSW","KOIN","KONI","KPAL","KRAS",
    "LAMI","MABA","MAMI","MDRN","MITI","MPPA","MRPH","MSIN","MTRA",
    "MYRX","NKPI","NRCA","NUSA","OBMD","OCAP","OKAS","OMRE","PADI",
    "PKPK","PLAS","PMMP","POLA","PTIS","RBMS","RIMO","SAFE","SDMU",
    "SFAN","SIMA","SMBR","SMDM","SMMT","SONA","SRAJ","STAR","SUGI",
    "TEBE","TIRA","TKGA","TMAS","TMPO","TNCA","TOPS","UANG","UNIT",
    "VICO","VINS","VIVA","WICO","WINS","YPAS","YULE","ZBRA","ABBA",
    "BHAT","BIMA","BLTZ","CLAY","DAJK","DWGL","FIRE","FLMC","BEKS",
    "BGTG","BIPI","BNBR","BOSS","BRMS","BTEK","CAKK","CMPP","COWL",
    "DART","DKFT","DPNS","DRMA","DSFI","DUCK","GEMA","GEPO","GOLL",
    "GRIS","HDFA","HAIS","IBFN","IMAS","IMJS","INDO","KARW","KICI",
    "KIMI","KOBX","KOKA","KPAS","LAUT",
]

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.header("⚙️ Pengaturan")

tickers_input = st.sidebar.text_area(
    "➕ Ticker Tambahan (pisah koma)",
    "BELL, BULL, BUMI, BUVA",
    height=70,
)

scan_mode = st.sidebar.multiselect(
    "📦 Kelompok Saham",
    ["Layer 1 (Blue Chip)", "Layer 2 (Mid Cap)", "Layer 3 (Spekulatif)", "Gocap Watchlist"],
    default=["Layer 1 (Blue Chip)", "Layer 2 (Mid Cap)", "Gocap Watchlist"],
)

min_score = st.sidebar.slider("Min Probability Score", 40, 90, 60)
show_detail = st.sidebar.checkbox("Tampilkan Detail Expander", value=True)

st.sidebar.divider()
st.sidebar.caption(
    f"Layer 1: {len(LAYER1)} ticker\n\n"
    f"Layer 2: {len(LAYER2)} ticker\n\n"
    f"Layer 3: {len(set(LAYER3_SPECULATIVE))} ticker\n\n"
    f"Gocap WL: {len(set(GOCAP_WATCHLIST))} ticker"
)

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def calc_rsi_series(close, period=14):
    delta = close.diff()
    gain  = delta.where(delta > 0, 0.0).rolling(period).mean()
    loss  = (-delta.where(delta < 0, 0.0)).rolling(period).mean()
    rs    = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def add_trading_days(start_date, n):
    d = start_date
    added = 0
    while added < n:
        d += datetime.timedelta(days=1)
        if d.weekday() < 5:
            added += 1
    return d


def searchable_table(df, cols, key_suffix=""):
    """Render a dataframe with a search box that filters by Ticker."""
    q = st.text_input(
        "🔍 Cari Ticker",
        key=f"search_{key_suffix}",
        placeholder="Ketik nama saham, misal: BBRI",
    )
    filtered = df[cols].copy()
    if q.strip():
        mask = filtered["Ticker"].str.contains(q.strip().upper(), na=False)
        filtered = filtered[mask]
    st.caption(f"{len(filtered)} saham ditampilkan")
    st.dataframe(filtered, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
if st.button("🚀 Analisis Sekarang", type="primary", use_container_width=True):
    with st.spinner("Membangun daftar saham..."):
        pool = []
        if "Layer 1 (Blue Chip)"    in scan_mode: pool += LAYER1
        if "Layer 2 (Mid Cap)"      in scan_mode: pool += LAYER2
        if "Layer 3 (Spekulatif)"   in scan_mode: pool += LAYER3_SPECULATIVE
        if "Gocap Watchlist"        in scan_mode: pool += GOCAP_WATCHLIST

        manual = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
        pool   = manual + pool
        pool   = list(dict.fromkeys(pool))   # deduplicate, preserve order
        tickers = [t + ".JK" for t in pool]

    st.info(f"Memindai **{len(tickers)}** saham…")

    today   = datetime.date.today()
    results = []
    progress = st.progress(0, text="Memulai…")

    for i, ticker in enumerate(tickers):
        progress.progress((i + 1) / len(tickers), text=f"{ticker} ({i+1}/{len(tickers)})")
        try:
            hist = yf.Ticker(ticker).history(period="4mo")
            if len(hist) < 60:
                continue

            close  = hist["Close"]
            high   = hist["High"]
            low    = hist["Low"]
            volume = hist["Volume"]
            last   = hist.iloc[-1]
            price  = last["Close"]
            change = round(((price - hist.iloc[-2]["Close"]) / hist.iloc[-2]["Close"]) * 100, 2)

            # ── Trend ──────────────────────────────────────────────────
            sma20 = close.rolling(20).mean().iloc[-1]
            sma50 = close.rolling(50).mean().iloc[-1]
            if price > sma20 and sma20 > sma50:
                trend = "🟢 UPTREND"
            elif price < sma50:
                trend = "🔴 DOWNTREND"
            else:
                trend = "⚪ SIDEWAYS"

            # ── RSI ─────────────────────────────────────────────────────
            rsi_ser  = calc_rsi_series(close, 14)
            rsi      = round(rsi_ser.iloc[-1], 1)
            rsi_prev = rsi_ser.iloc[-2]

            if   rsi < 25: rsi_label = "🟢 Sangat Oversold"; rsi_score = 30
            elif rsi < 40: rsi_label = "🟡 Oversold";         rsi_score = 18
            elif rsi < 55: rsi_label = "⚪ Netral";            rsi_score =  5
            elif rsi < 70: rsi_label = "🟠 Overbought Ringan"; rsi_score = -5
            else:           rsi_label = "🔴 Overbought";       rsi_score = -15

            # ── MACD ────────────────────────────────────────────────────
            exp1       = close.ewm(span=12, adjust=False).mean()
            exp2       = close.ewm(span=26, adjust=False).mean()
            macd_line  = exp1 - exp2
            sig_line   = macd_line.ewm(span=9, adjust=False).mean()
            macd_hist  = macd_line - sig_line
            macd_cross = (macd_line.iloc[-1] > sig_line.iloc[-1]
                          and macd_line.iloc[-2] <= sig_line.iloc[-2])
            macd_above = macd_line.iloc[-1] > sig_line.iloc[-1]
            macd_score = 20 if macd_cross else (10 if macd_above else 0)

            # ── Bollinger Bands ─────────────────────────────────────────
            bb_mid_s = close.rolling(20).mean()
            bb_std_s = close.rolling(20).std()
            bb_upper = (bb_mid_s + 2 * bb_std_s).iloc[-1]
            bb_lower = (bb_mid_s - 2 * bb_std_s).iloc[-1]
            bb_mid_v = bb_mid_s.iloc[-1]
            bb_width = round((bb_upper - bb_lower) / bb_mid_v * 100, 2)
            bb_pct_b = round((price - bb_lower) / max(bb_upper - bb_lower, 0.01) * 100, 1)

            if   price <= bb_lower:  bb_label = "🟢 Di Bawah Lower"; bb_score = 22
            elif price <= bb_mid_v:  bb_label = "🔵 Lower–Mid";       bb_score = 10
            elif price <= bb_upper:  bb_label = "⚪ Mid–Upper";        bb_score =  0
            else:                     bb_label = "🔴 Di Atas Upper";   bb_score = -10

            # ── Stochastic (14,3,3) ─────────────────────────────────────
            low14   = low.rolling(14).min()
            high14  = high.rolling(14).max()
            raw_k   = (close - low14) / (high14 - low14).replace(0, np.nan) * 100
            stoch_k = raw_k.rolling(3).mean()
            stoch_d = stoch_k.rolling(3).mean()

            k_val  = round(stoch_k.iloc[-1], 1)
            d_val  = round(stoch_d.iloc[-1], 1)
            k_prev = stoch_k.iloc[-2]
            d_prev = stoch_d.iloc[-2]

            stoch_golden = k_val > d_val and k_prev <= d_prev   # %K cross above %D
            stoch_dead   = k_val < d_val and k_prev >= d_prev

            if k_val < 20:
                stoch_label = "🟢 Oversold" + (" ✨GC" if stoch_golden else "")
                stoch_score = 22 + (8 if stoch_golden else 0)
            elif k_val < 40:
                stoch_label = "🟡 Mulai Naik"
                stoch_score = 10
            elif k_val > 80:
                stoch_label = "🔴 Overbought"
                stoch_score = -10
            else:
                stoch_label = "⚪ Netral"
                stoch_score = 0

            # ── Volume & OBV ────────────────────────────────────────────
            vol_recent = volume.tail(10).mean()
            vol_avg    = volume.mean()
            vol_spike  = round(vol_recent / max(vol_avg, 1), 2)

            hist["OBV"] = (volume * np.sign(close.diff())).cumsum()
            obv_now = hist["OBV"].iloc[-1]
            obv_30  = hist["OBV"].iloc[-31] if len(hist) > 30 else obv_now

            # ── Support / Resistance ────────────────────────────────────
            support    = round(low.tail(20).min(), 2)
            resistance = round(high.tail(20).max(), 2)

            # ── Probability Score ───────────────────────────────────────
            score = 0
            if "UPTREND" in trend: score += 15
            if obv_now > obv_30:   score += 10
            if vol_spike > 1.6:    score += 10
            score += rsi_score + bb_score + stoch_score + macd_score
            score  = max(0, min(100, score))

            # ── Akumulasi ───────────────────────────────────────────────
            if (change > 3 and vol_spike > 1.7) or (obv_now > obv_30 and vol_spike > 1.65 and rsi < 62):
                akum = "💰 AKUMULASI KUAT"
            elif obv_now > obv_30 or rsi < 48:
                akum = "💰 Akumulasi Sedang"
            else:
                akum = "—"

            # ── Pre-Surge ───────────────────────────────────────────────
            if vol_spike > 2.5 and change > 2:
                pre_surge = "🔥 POTENSI PUMP"
            elif vol_spike > 1.8:
                pre_surge = "⚡ Potensi Naik Dini"
            else:
                pre_surge = "—"

            # ── Gocap / Penny Flag ──────────────────────────────────────
            is_gocap   = price <= 55
            is_penny   = 55 < price <= 200
            layer_flag = (
                "🪙 GOCAP"    if is_gocap else
                "💸 Penny"    if is_penny else
                "📊 Regular"
            )

            # Bonus score untuk saham gocap/penny dengan volume spike:
            # potensi gain % lebih drastis dari harga rendah
            if (is_gocap or is_penny) and vol_spike > 1.8:
                score = min(100, score + 8)

            # Potential % gain kalau ke resistance
            pot_gain = round((resistance - price) / max(price, 1) * 100, 1)

            # ── Trading Style ───────────────────────────────────────────
            if vol_spike > 2.5 and rsi > 65:
                style = "⚡ SCALPING/HARIAN"; style_why = "Volume ekstrem + momentum kuat"
            elif is_gocap and vol_spike > 1.5 and score >= 55:
                style = "🪙 GOCAP SWING"; style_why = "Saham gocap vol spike → potensi gain besar"
            elif score >= 75 and "UPTREND" in trend and vol_spike > 1.4:
                style = "📈 SWING TRADING"; style_why = "Trend kuat + akumulasi"
            elif score >= 60 and "Akumulasi" in akum:
                style = "📈 SWING TRADING"; style_why = "Akumulasi + potensi reversal"
            else:
                style = "🕒 HOLD/MENENGAH"; style_why = "Belum ada trigger kuat"

            # ── Entry Timing ────────────────────────────────────────────
            strong_now = (
                price <= bb_lower and k_val < 25 and rsi < 38 and rsi > rsi_prev
            )
            moderate_now = (
                (price <= bb_lower or k_val < 25 or rsi < 35) and rsi > rsi_prev
            )
            setup_forming = (
                (k_val < 40 and rsi < 50 and "UPTREND" in trend)
                or (stoch_golden and k_val < 50)
                or (macd_cross and rsi < 55)
            )

            if strong_now:
                days_out = 0; timing_tag = "⚡ MASUK SEKARANG"
                timing_why = "BB Lower + Stoch Oversold + RSI mulai naik"
            elif moderate_now:
                days_out = 1; timing_tag = "📅 1–2 Hari"
                timing_why = "Oversold zone — tunggu 1 hari konfirmasi"
            elif setup_forming:
                days_out = 3; timing_tag = "📅 ~3 Hari"
                timing_why = "Setup terbentuk, tunggu pullback minor"
            elif score >= 55:
                days_out = 5; timing_tag = "📅 ~1 Minggu"
                timing_why = "Score cukup tapi sinyal belum kompak"
            else:
                days_out = 999; timing_tag = "⏳ Belum Waktunya"
                timing_why = "Sinyal teknikal belum ada"

            if days_out == 0:
                est_date = "Hari Ini"
            elif days_out == 999:
                est_date = "Tunggu Sinyal"
            else:
                est_date = add_trading_days(today, days_out).strftime("%-d %b %Y")

            # ── Entry / SL / Target ─────────────────────────────────────
            ideal_entry = round(price * 0.99, 2) if score >= 75 else round(support * 1.01, 2)
            stop_loss   = round(ideal_entry * 0.94, 2)
            target_pr   = round(resistance, 2)
            rr_ratio    = round((target_pr - ideal_entry) / max(ideal_entry - stop_loss, 1), 2)

            results.append({
                "Layer":         layer_flag,
                "Ticker":        ticker.replace(".JK", ""),
                "Harga":         round(price, 2),
                "Change %":      change,
                "Pot. Gain %":   pot_gain,
                "Trend":         trend,
                "RSI":           rsi,
                "RSI Signal":    rsi_label,
                "BB %B":         bb_pct_b,
                "BB Width %":    bb_width,
                "BB Signal":     bb_label,
                "Stoch %K":      k_val,
                "Stoch %D":      d_val,
                "Stoch Signal":  stoch_label,
                "Akumulasi":     akum,
                "Pre-Surge":     pre_surge,
                "Probability":   score,
                "Style":         style,
                "Style Reason":  style_why,
                "Entry":         ideal_entry,
                "Stop Loss":     stop_loss,
                "Target":        target_pr,
                "R:R":           f"1:{rr_ratio}",
                "Vol Spike":     vol_spike,
                "Timing":        timing_tag,
                "Est. Masuk":    est_date,
                "Alasan Timing": timing_why,
            })

        except Exception:
            continue

    progress.empty()

    if not results:
        st.warning("Tidak ada data berhasil dianalisa.")
        st.stop()

    # ── Simpan ke session_state agar tidak hilang saat filter diklik ──────
    st.session_state["df"] = pd.DataFrame(results)
    st.session_state["analyzed"] = True
    st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# KOLOM TABEL  (didefinisikan di level modul, bukan di dalam button handler)
# ─────────────────────────────────────────────────────────────────────────────
SUMMARY = [
    "Layer","Ticker","Harga","Change %","Pot. Gain %","Trend",
    "RSI","RSI Signal","BB %B","BB Signal",
    "Stoch %K","Stoch %D","Stoch Signal",
    "Probability","Style",
    "Entry","Stop Loss","Target","R:R",
    "Vol Spike","Timing","Est. Masuk",
]
TECH = [
    "Layer","Ticker","Harga","Trend",
    "RSI","RSI Signal","BB %B","BB Width %","BB Signal",
    "Stoch %K","Stoch %D","Stoch Signal",
    "Akumulasi","Pre-Surge","Vol Spike","Probability",
]

# ─────────────────────────────────────────────────────────────────────────────
# DISPLAY — di luar blok button agar filter/search tidak reset halaman
# Setiap interaksi UI (filter, search, tab) hanya menjalankan bagian ini,
# bukan ulang analisis. Data tetap aman di st.session_state["df"].
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.get("analyzed") and "df" in st.session_state:
    df = st.session_state["df"]

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔥 Rekomendasi Teratas",
        "🪙 Gocap / Penny Watch",
        "📋 Semua Saham",
        "📊 Detail Teknikal",
        "📖 Panduan",
    ])

    # ── Tab 1: Top Picks ─────────────────────────────────────────────────
    with tab1:
        top = df[df["Probability"] >= min_score].sort_values("Probability", ascending=False)
        st.markdown(f"**{len(top)} saham** memenuhi score ≥ {min_score}")
        searchable_table(top, SUMMARY, "top")

        if show_detail and not top.empty:
            st.divider()
            st.subheader("🔬 Detail Top 5")
            for _, row in top.head(5).iterrows():
                with st.expander(
                    f"📌 {row['Ticker']}  |  {row['Layer']}  |  Score: {row['Probability']}  |  {row['Timing']}"
                ):
                    c1, c2, c3, c4, c5 = st.columns(5)
                    c1.metric("RSI", row["RSI"])
                    c2.metric("BB %B", f"{row['BB %B']}%")
                    c3.metric("Stoch %K", row["Stoch %K"])
                    c4.metric("Stoch %D", row["Stoch %D"])
                    c5.metric("Vol Spike", f"{row['Vol Spike']}×")

                    st.info(
                        f"⏰ **Timing:** {row['Timing']}  ·  📅 **Est.:** {row['Est. Masuk']}\n\n"
                        f"💡 {row['Alasan Timing']}"
                    )
                    ca, cb, cc, cd = st.columns(4)
                    ca.metric("Entry Ideal", f"Rp {row['Entry']:,.0f}")
                    cb.metric("Stop Loss",   f"Rp {row['Stop Loss']:,.0f}")
                    cc.metric("Target",      f"Rp {row['Target']:,.0f}")
                    cd.metric("Pot. Gain %", f"{row['Pot. Gain %']}%")
                    st.caption(f"Style: {row['Style']}  ·  {row['Style Reason']}  ·  R:R = {row['R:R']}")

    # ── Tab 2: Gocap / Penny ─────────────────────────────────────────────
    with tab2:
        gocap_df = df[df["Harga"] <= 200].sort_values("Probability", ascending=False)
        col_g1, col_g2, col_g3 = st.columns(3)
        col_g1.metric("Total Gocap (≤55)",    len(df[df["Harga"] <= 55]))
        col_g2.metric("Total Penny (56–200)",  len(df[(df["Harga"] > 55) & (df["Harga"] <= 200)]))
        col_g3.metric("Pump Potential 🔥",     len(gocap_df[gocap_df["Pre-Surge"] == "🔥 POTENSI PUMP"]))

        st.markdown(
            "> **Catatan:** Saham gocap/penny punya potensi % gain besar karena harga rendah, "
            "tapi juga risiko tinggi. Prioritaskan yang ada volume spike kuat."
        )

        gocap_filter = st.radio(
            "Filter",
            ["Semua", "Gocap Saja (≤55)", "Penny (56–200)", "Vol Spike > 2×", "Pump Potential"],
            horizontal=True,
            key="gocap_filter",
        )
        if gocap_filter == "Gocap Saja (≤55)":
            gocap_df = gocap_df[gocap_df["Harga"] <= 55]
        elif gocap_filter == "Penny (56–200)":
            gocap_df = gocap_df[(gocap_df["Harga"] > 55) & (gocap_df["Harga"] <= 200)]
        elif gocap_filter == "Vol Spike > 2×":
            gocap_df = gocap_df[gocap_df["Vol Spike"] > 2.0]
        elif gocap_filter == "Pump Potential":
            gocap_df = gocap_df[gocap_df["Pre-Surge"] == "🔥 POTENSI PUMP"]

        searchable_table(gocap_df, SUMMARY, "gocap")

    # ── Tab 3: Semua Saham ───────────────────────────────────────────────
    with tab3:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filter_trend = st.multiselect(
                "Filter Trend",
                ["🟢 UPTREND", "⚪ SIDEWAYS", "🔴 DOWNTREND"],
                default=[],
                key="filter_trend",
            )
        with col_f2:
            filter_timing = st.multiselect(
                "Filter Timing",
                ["⚡ MASUK SEKARANG", "📅 1–2 Hari", "📅 ~3 Hari", "📅 ~1 Minggu", "⏳ Belum Waktunya"],
                default=[],
                key="filter_timing",
            )

        all_df = df.sort_values("Probability", ascending=False)
        if filter_trend:
            all_df = all_df[all_df["Trend"].isin(filter_trend)]
        if filter_timing:
            all_df = all_df[all_df["Timing"].isin(filter_timing)]

        searchable_table(all_df, SUMMARY, "all")

    # ── Tab 4: Detail Teknikal ───────────────────────────────────────────
    with tab4:
        searchable_table(df.sort_values("Probability", ascending=False), TECH, "tech")

    # ── Tab 5: Panduan ───────────────────────────────────────────────────
    with tab5:
        st.markdown("""
### 📖 Panduan Indikator

| Indikator | Penjelasan |
|---|---|
| **RSI** | < 30 = Sangat Oversold (potensi buy). > 70 = Overbought. |
| **BB %B** | 0% = harga di Lower Band (potensi bounce). 100% = Upper Band. |
| **BB Width %** | Kecil = BB Squeeze → breakout kemungkinan dekat. |
| **Stoch %K** | < 20 = Oversold. > 80 = Overbought. |
| **Stoch ✨GC** | Golden Cross: %K motong %D dari bawah saat di zona oversold → sinyal beli kuat. |
| **Vol Spike** | > 1.5 = volume mulai naik. > 2.5 = potensi pump. |
| **Pot. Gain %** | % gain jika harga naik ke resistance 20 hari. |
| **Probability** | 0–100, gabungan semua indikator. ≥70 = setup bagus. |

### ⏰ Logika Timing Entry

| Kondisi | Timing |
|---|---|
| BB Lower + Stoch <25 + RSI <38 & naik | ⚡ Masuk Sekarang |
| Salah satu oversold + RSI mulai naik | 📅 1–2 Hari |
| Setup forming (golden cross / MACD cross) | 📅 ~3 Hari |
| Score ≥55 tapi belum kompak | 📅 ~1 Minggu |
| Tidak ada sinyal | ⏳ Belum Waktunya |

### 🪙 Gocap & Penny

Saham **gocap** = harga ≤ Rp 50 (floor harga BEI). Saham **penny** = Rp 51–200.
Keduanya punya risiko lebih tinggi tapi potensi % gain jauh lebih besar.
Prioritaskan yang punya **Vol Spike > 2×** dan minimal **Pre-Surge ⚡**.

---
> ⚠️ **Bukan saran investasi.** Selalu lakukan riset sendiri dan gunakan manajemen risiko.
        """)

st.caption(
    "Data: Yahoo Finance · Indikator: SMA, RSI 14, MACD 12/26/9, BB 20-2σ, Stochastic 14-3-3 · "
    f"Total universe: {len(set(LAYER1+LAYER2+LAYER3_SPECULATIVE+GOCAP_WATCHLIST))}+ ticker IDX"
)
