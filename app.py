import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime

st.set_page_config(page_title="IDX Stock Hunter Pro", layout="wide", page_icon="🚀")
st.title("📈 IDX Stock Hunter Pro")
st.markdown("**Analisis Teknikal Lengkap + Verdict Final: MASUK / TUNGGU / HINDARI**")

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
    "MEGA","NISP","BNLI","BNGA","BDMN","BJBR","BJTM","PNBS","MAYA","NOBU",
    "AGRO","BMAS","BCIC","MCOR","DNAR","AMAR",
    "LPKR","SMRA","PWON","BSDE","MTLA","BEST","DILD","KIJA","NIRO",
    "MKPI","PPRO","SMDM","GPSO","OMRE","GWSA","PJAA","JSPT","KPIG",
    "ELSA","INDY","PTRO","RUIS","SMMT","MBAP","KKGI","PKPK","DOID","GEMS",
    "INPC","ENRG","GZCO","SSMS","SGRO","SIMP","PALM","LSIP","TBLA",
    "ROTI","MYOR","SIDO","HOKI","SKBM","SKLT","WIIM","GOOD","COCO","BOBA",
    "LPPF","RALS","MAPI","MIKA","SILO","HERO","TGKA","TIRA","MTDL","EPMT",
    "SMCB","WTON","TOTO","LION","LMSH","KBLI","KBLM","SCCO","SPMA","TRST",
    "IMPC","IGAR","ISSP","LAMI","PICO","YPAS","UNIC","SOCI","GJTL","INDS",
    "SUPR","TBMS","IBST","GHON","GLOB","CASH","ARTO","PYFA",
    "TOTL","WIKA","WSKT","PTPP","NRCA","JKPL","PBID","CSIS",
    "TURI","MPPA","PDES","TOPS","LUCK","KREN","NELY","FORU","PLAS",
]
LAYER3_SPECULATIVE = [
    "ARMY","BHAT","BIMA","BLTZ","BPTR","BSML","CARS","CBPE","CCSI",
    "CLAY","DAJK","DOSS","DPUM","DWGL","EAST","FIRE","FLMC","FMII",
    "GAMA","GETS","HOTL","HRME","HKMU","IIKP","IKAI","INCI","ISAP",
    "ITMA","ITIC","JAWA","JKSW","KOIN","KONI","KPAL","KRAS",
    "LCKM","LEAD","LMPI","LPGI","MABA","MAMI","MDRN","MGRO","MITI",
    "MPOW","MRPH","MSIN","MTRA","MYRX","NASI","NETV","NICK","NKPI",
    "NUSA","OBMD","OCAP","OKAS","PADI","PANR","PBRX","PCAR",
    "PMMP","PNGO","POLA","PTIS","PTSP","PUDP","PURA","RBMS","RIMO",
    "SAFE","SDMU","SFAN","SIMA","SMBR","SMDR","SONA","SRAJ","STAR",
    "SUGI","TBIG","TCPI","TEBE","TKGA","TKIM","TMAS","TMPO","TNCA",
    "UANG","UNIT","UNSP","VICO","VINS","VIVA","WICO","WINS","YULE",
    "ZBRA","ABBA","ABDA","ACST","AADI","FREN","MNCN","MLBI",
    "AIMS","ANDI","APEX","APLI","ARNA","ARTI","ASBI","ASMI","ASSA",
    "ATAP","ATPK","AUDA","BACA","BAJA","BANK","BAPA","BATA",
    "BCAP","BCIP","BDKI","BEKS","BFIN","BGTG","BHIT","BIKA","BIPI","BIRD",
    "BMSR","BNBR","BOSS","BRMS","BTEK","BTON","BUDI","CAKK",
    "CASS","CEKA","CFIN","CITY","CLPI","CMPP","CNTB","COAL","COWL",
    "CPRI","CSAP","CYBR","DART","DAYS","DIGI","DKFT","DLTA",
    "DNET","DPNS","DRMA","DSFI","DSNG","DUCK","DUTI","ECII","EDGE",
    "EMDE","EMTK","ENAK","ENZO","ERAA","ESTE","FAST","FILM","FITT",
    "FWCT","GEMA","GEPO","GOLL","GRIS","GTSI","HAIS","HDFA","HEAL",
    "HEXA","HMSP","IBFN","IKBI","IMAS","IMJS","INAI","INDO","INDR",
    "INPP","INSW","IPCC","IPCM","IPOL","IPPE","JMAS","JRPT","JTPE",
    "KAEF","KARW","KEEN","KIAS","KICI","KIMI","KMTR","KOBX","KOKA","KPAS","LAUT",
]
GOCAP_WATCHLIST = [
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
tickers_input = st.sidebar.text_area("➕ Ticker Tambahan (pisah koma)", "BELL, BULL, BUMI, BUVA", height=70)
scan_mode     = st.sidebar.multiselect(
    "📦 Kelompok Saham",
    ["Layer 1 (Blue Chip)", "Layer 2 (Mid Cap)", "Layer 3 (Spekulatif)", "Gocap Watchlist"],
    default=["Layer 1 (Blue Chip)", "Layer 2 (Mid Cap)", "Gocap Watchlist"],
)
min_score     = st.sidebar.slider("Min Probability Score", 40, 90, 60)
risk_rp       = st.sidebar.number_input("💰 Risk per Trade (Rp)", value=500_000, step=100_000,
                                         help="Digunakan untuk hitung ukuran posisi berdasarkan ATR")
show_detail   = st.sidebar.checkbox("Tampilkan Detail Expander (Top 5)", value=True)
st.sidebar.divider()
debug_mode = st.sidebar.checkbox("🐛 Debug Mode (tampilkan error)", value=False)
st.sidebar.caption(
    f"Layer 1: {len(LAYER1)} · Layer 2: {len(LAYER2)}\n\n"
    f"Layer 3: {len(set(LAYER3_SPECULATIVE))} · Gocap: {len(set(GOCAP_WATCHLIST))}"
)

# ── Tombol test koneksi ──────────────────────────────────────────────────
if st.sidebar.button("🔌 Test Koneksi yfinance"):
    with st.sidebar:
        with st.spinner("Testing BBCA.JK..."):
            try:
                _test = yf.Ticker("BBCA.JK").history(period="5d")
                if len(_test) > 0:
                    st.success(f"OK — {len(_test)} hari data.\nyfinance berfungsi normal.")
                else:
                    st.error("Data kosong — tunggu beberapa menit lalu coba lagi.")
            except Exception as _e:
                st.error(f"Error: {_e}")

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def calc_rsi_series(close, period=14):
    delta = close.diff()
    gain  = delta.where(delta > 0, 0.0).rolling(period).mean()
    loss  = (-delta.where(delta < 0, 0.0)).rolling(period).mean()
    return 100 - (100 / (1 + gain / loss.replace(0, np.nan)))

def calc_adx(high, low, close, period=14):
    """Return (ADX, +DI, -DI) using Wilder smoothing."""
    up   = high.diff()
    down = -low.diff()
    plus_dm  = up.where((up > down) & (up > 0), 0.0)
    minus_dm = down.where((down > up) & (down > 0), 0.0)
    tr = pd.concat([high - low,
                    (high - close.shift()).abs(),
                    (low  - close.shift()).abs()], axis=1).max(axis=1)
    atr      = tr.ewm(span=period, adjust=False).mean()
    plus_di  = 100 * plus_dm.ewm(span=period, adjust=False).mean()  / atr.replace(0, np.nan)
    minus_di = 100 * minus_dm.ewm(span=period, adjust=False).mean() / atr.replace(0, np.nan)
    dx  = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    adx = dx.ewm(span=period, adjust=False).mean()
    return round(adx.iloc[-1], 1), round(plus_di.iloc[-1], 1), round(minus_di.iloc[-1], 1)

def calc_atr(high, low, close, period=14):
    tr = pd.concat([high - low,
                    (high - close.shift()).abs(),
                    (low  - close.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(period).mean().iloc[-1]

def add_trading_days(start_date, n):
    d = start_date
    added = 0
    while added < n:
        d += datetime.timedelta(days=1)
        if d.weekday() < 5:
            added += 1
    return d

def searchable_table(df, cols, key_suffix=""):
    q = st.text_input("🔍 Cari Ticker", key=f"search_{key_suffix}",
                       placeholder="Ketik nama saham, misal: BBRI")
    available = [c for c in cols if c in df.columns]
    filtered  = df[available].copy()
    if q.strip():
        filtered = filtered[filtered["Ticker"].str.contains(q.strip().upper(), na=False)]
    st.caption(f"{len(filtered)} saham ditampilkan")
    st.dataframe(filtered, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
if st.button("🚀 Analisis Sekarang", type="primary", use_container_width=True):
    pool = []
    if "Layer 1 (Blue Chip)"  in scan_mode: pool += LAYER1
    if "Layer 2 (Mid Cap)"    in scan_mode: pool += LAYER2
    if "Layer 3 (Spekulatif)" in scan_mode: pool += LAYER3_SPECULATIVE
    if "Gocap Watchlist"      in scan_mode: pool += GOCAP_WATCHLIST
    manual  = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    pool    = list(dict.fromkeys(manual + pool))
    tickers = [t + ".JK" for t in pool]

    st.info(f"Memindai **{len(tickers)}** saham…")
    today      = datetime.date.today()
    results    = []
    errors     = []   # kumpulkan error untuk debug
    skipped    = []   # kumpulkan yang dilewati karena data kurang
    progress   = st.progress(0, text="Memulai…")

    for i, ticker in enumerate(tickers):
        progress.progress((i + 1) / len(tickers), text=f"{ticker} ({i+1}/{len(tickers)})")
        try:
            hist = yf.Ticker(ticker).history(period="4mo")
            if len(hist) < 60:
                skipped.append(f"{ticker}: hanya {len(hist)} baris data (min 60)")
                continue
            close  = hist["Close"]
            high   = hist["High"]
            low    = hist["Low"]
            volume = hist["Volume"]
            price  = close.iloc[-1]
            change = round((price - close.iloc[-2]) / close.iloc[-2] * 100, 2)

            # ── Trend (SMA 20 / 50) ─────────────────────────────────────
            sma20 = close.rolling(20).mean().iloc[-1]
            sma50 = close.rolling(50).mean().iloc[-1]
            if price > sma20 and sma20 > sma50:   trend = "🟢 UPTREND"
            elif price < sma50:                    trend = "🔴 DOWNTREND"
            else:                                  trend = "⚪ SIDEWAYS"

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
            macd_line  = close.ewm(span=12,adjust=False).mean() - close.ewm(span=26,adjust=False).mean()
            sig_line   = macd_line.ewm(span=9, adjust=False).mean()
            macd_cross = macd_line.iloc[-1] > sig_line.iloc[-1] and macd_line.iloc[-2] <= sig_line.iloc[-2]
            macd_above = macd_line.iloc[-1] > sig_line.iloc[-1]
            macd_score = 20 if macd_cross else (10 if macd_above else 0)

            # ── Bollinger Bands (20, 2σ) ─────────────────────────────────
            bb_mid_s = close.rolling(20).mean()
            bb_std_s = close.rolling(20).std()
            bb_upper = (bb_mid_s + 2*bb_std_s).iloc[-1]
            bb_lower = (bb_mid_s - 2*bb_std_s).iloc[-1]
            bb_mid_v = bb_mid_s.iloc[-1]
            bb_width = round((bb_upper - bb_lower) / bb_mid_v * 100, 2)
            bb_pct_b = round((price - bb_lower) / max(bb_upper - bb_lower, 0.01) * 100, 1)
            if   price <= bb_lower: bb_label = "🟢 Di Bawah Lower"; bb_score = 22
            elif price <= bb_mid_v: bb_label = "🔵 Lower–Mid";       bb_score = 10
            elif price <= bb_upper: bb_label = "⚪ Mid–Upper";        bb_score =  0
            else:                   bb_label = "🔴 Di Atas Upper";    bb_score = -10

            # ── Stochastic (14,3,3) ─────────────────────────────────────
            raw_k   = (close - low.rolling(14).min()) / (high.rolling(14).max() - low.rolling(14).min()).replace(0, np.nan) * 100
            stoch_k = raw_k.rolling(3).mean()
            stoch_d = stoch_k.rolling(3).mean()
            k_val   = round(stoch_k.iloc[-1], 1)
            d_val   = round(stoch_d.iloc[-1], 1)
            stoch_golden = k_val > d_val and stoch_k.iloc[-2] <= stoch_d.iloc[-2]
            if k_val < 20:
                stoch_label = "🟢 Oversold" + (" ✨GC" if stoch_golden else ""); stoch_score = 22 + (8 if stoch_golden else 0)
            elif k_val < 40:
                stoch_label = "🟡 Mulai Naik"; stoch_score = 10
            elif k_val > 80:
                stoch_label = "🔴 Overbought"; stoch_score = -10
            else:
                stoch_label = "⚪ Netral"; stoch_score = 0

            # ── ADX (14) — kekuatan trend ────────────────────────────────
            adx_val, plus_di, minus_di = calc_adx(high, low, close, 14)
            if   adx_val >= 30: adx_label = "💪 Trend Kuat"
            elif adx_val >= 20: adx_label = "➡️ Trend Lemah"
            else:               adx_label = "↔️ Sideways/Choppy"
            adx_bullish = plus_di > minus_di  # arah trend: bullish jika +DI > -DI

            # ── ATR (14) — volatilitas nyata ─────────────────────────────
            atr_val  = calc_atr(high, low, close, 14)
            sl_atr   = round(price - 1.5 * atr_val, 2)   # SL lebih akurat dari % fixed
            lot_saran = int(risk_rp / max(price - sl_atr, 1) / 100) * 100  # lot (1 lot=100 lembar)
            lot_saran = max(lot_saran, 100)

            # ── Volume & OBV ─────────────────────────────────────────────
            vol_recent = volume.tail(10).mean()
            vol_avg    = volume.mean()
            vol_spike  = round(vol_recent / max(vol_avg, 1), 2)
            hist["OBV"] = (volume * np.sign(close.diff())).cumsum()
            obv_now = hist["OBV"].iloc[-1]
            obv_30  = hist["OBV"].iloc[-31] if len(hist) > 30 else obv_now

            # ── LIKUIDITAS — nilai transaksi harian (IDR) ─────────────────
            turnover_series = (close * volume).tail(20)
            turnover_m      = round(turnover_series.mean() / 1_000_000, 1)   # juta IDR
            if   turnover_m >= 5_000: liq_label = "🟢 Sangat Likuid";  liq_ok = True
            elif turnover_m >= 1_000: liq_label = "🟢 Likuid";          liq_ok = True
            elif turnover_m >=   500: liq_label = "🟡 Cukup Likuid";    liq_ok = True
            elif turnover_m >=   100: liq_label = "🟠 Kurang Likuid";   liq_ok = False
            else:                     liq_label = "🔴 Tidak Likuid";    liq_ok = False

            # ── STEALTH ACCUMULATION — proxy bandar tanpa broker flow ─────
            # Sinyal 1: OBV naik konsisten 5 hari terakhir
            obv5 = hist["OBV"].tail(5)
            obv_rising = (obv5.diff().dropna() > 0).sum() >= 4   # ≥4 dari 5 hari naik

            # Sinyal 2: OBV naik tapi harga stagnan/turun (akumulasi diam)
            price_5d_change = (close.iloc[-1] - close.iloc[-6]) / close.iloc[-6] * 100
            obv_5d_change   = (hist["OBV"].iloc[-1] - hist["OBV"].iloc[-6]) / max(abs(hist["OBV"].iloc[-6]), 1) * 100
            divergence      = obv_5d_change > 5 and price_5d_change < 1   # OBV naik, harga diam

            # Sinyal 3: volume bertahap naik (5d avg > 10d avg > 20d avg)
            vol5d  = volume.tail(5).mean()
            vol10d = volume.tail(10).mean()
            vol20d = volume.tail(20).mean()
            gradual_build = vol5d > vol10d > vol20d

            # Sinyal 4: BB Squeeze + volume naik (coiling sebelum breakout)
            bb_hist_widths = ((bb_mid_s + 2*bb_std_s) - (bb_mid_s - 2*bb_std_s)) / bb_mid_s * 100
            bb_width_pct   = (bb_width - bb_hist_widths.tail(60).min()) / max(bb_hist_widths.tail(60).ptp(), 0.01) * 100
            squeeze_vol    = bb_width_pct < 25 and vol_spike > 1.3  # squeeze + volume mulai naik

            stealth_score  = sum([obv_rising, divergence, gradual_build, squeeze_vol])
            if   stealth_score >= 3: stealth_label = "💎 AKUMULASI KUAT"
            elif stealth_score == 2: stealth_label = "🔍 Ada Akumulasi"
            elif stealth_score == 1: stealth_label = "〰️ Tanda Minor"
            else:                    stealth_label = "—"

            # ── Support / Resistance ─────────────────────────────────────
            support    = round(low.tail(20).min(), 2)
            resistance = round(high.tail(20).max(), 2)
            pot_gain   = round((resistance - price) / max(price, 1) * 100, 1)

            # ── Probability Score ─────────────────────────────────────────
            score = 0
            if "UPTREND" in trend: score += 15
            if obv_now > obv_30:   score += 10
            if vol_spike > 1.6:    score += 10
            score += rsi_score + bb_score + stoch_score + macd_score
            score += stealth_score * 5   # bonus dari akumulasi diam
            if adx_val >= 25 and adx_bullish: score += 5   # trend kuat ke atas
            is_gocap = price <= 55
            is_penny = 55 < price <= 200
            if (is_gocap or is_penny) and vol_spike > 1.8: score += 8
            score = max(0, min(100, score))

            layer_flag = "🪙 GOCAP" if is_gocap else ("💸 Penny" if is_penny else "📊 Regular")

            # ── Akumulasi / Pre-Surge ─────────────────────────────────────
            if (change > 3 and vol_spike > 1.7) or (obv_now > obv_30 and vol_spike > 1.65 and rsi < 62):
                akum = "💰 AKUMULASI KUAT"
            elif obv_now > obv_30 or rsi < 48:
                akum = "💰 Akumulasi Sedang"
            else:
                akum = "—"

            if vol_spike > 2.5 and change > 2:     pre_surge = "🔥 POTENSI PUMP"
            elif vol_spike > 1.8:                   pre_surge = "⚡ Potensi Naik Dini"
            else:                                   pre_surge = "—"

            # ── Trading Style ─────────────────────────────────────────────
            if vol_spike > 2.5 and rsi > 65:
                style = "⚡ SCALPING"; style_why = "Volume ekstrem + momentum kuat"
            elif is_gocap and vol_spike > 1.5 and score >= 55:
                style = "🪙 GOCAP SWING"; style_why = "Gocap vol spike → potensi gain besar"
            elif score >= 75 and "UPTREND" in trend and vol_spike > 1.4:
                style = "📈 SWING TRADING"; style_why = "Trend kuat + akumulasi"
            elif score >= 60 and "Akumulasi" in akum:
                style = "📈 SWING TRADING"; style_why = "Akumulasi + potensi reversal"
            else:
                style = "🕒 HOLD/MENENGAH"; style_why = "Belum ada trigger kuat"

            # ── Entry Timing ──────────────────────────────────────────────
            strong_now    = price <= bb_lower and k_val < 25 and rsi < 38 and rsi > rsi_prev
            moderate_now  = (price <= bb_lower or k_val < 25 or rsi < 35) and rsi > rsi_prev
            setup_forming = (k_val < 40 and rsi < 50 and "UPTREND" in trend) or \
                            (stoch_golden and k_val < 50) or (macd_cross and rsi < 55)

            if strong_now:
                days_out=0; timing_tag="⚡ MASUK SEKARANG"; timing_why="BB Lower+Stoch OS+RSI naik"
            elif moderate_now:
                days_out=1; timing_tag="📅 1–2 Hari"; timing_why="Oversold zone, tunggu konfirmasi"
            elif setup_forming:
                days_out=3; timing_tag="📅 ~3 Hari"; timing_why="Setup terbentuk, tunggu pullback"
            elif score >= 55:
                days_out=5; timing_tag="📅 ~1 Minggu"; timing_why="Score cukup, sinyal belum kompak"
            else:
                days_out=999; timing_tag="⏳ Belum Waktunya"; timing_why="Sinyal belum ada"

            est_date = ("Hari Ini" if days_out == 0 else
                        "Tunggu Sinyal" if days_out == 999 else
                        add_trading_days(today, days_out).strftime("%-d %b %Y"))

            # ── Entry / SL / Target ───────────────────────────────────────
            ideal_entry = round(price * 0.99, 2) if score >= 75 else round(support * 1.01, 2)
            stop_loss   = max(sl_atr, round(ideal_entry * 0.93, 2))   # ATR-based, min -7%
            target_pr   = round(resistance, 2)
            rr_ratio    = round((target_pr - ideal_entry) / max(ideal_entry - stop_loss, 1), 2)

            # ── FINAL VERDICT ─────────────────────────────────────────────
            # Cek semua syarat secara bersamaan — bukan hanya score
            strong_downtrend = "DOWNTREND" in trend and adx_val >= 25
            overbought       = rsi >= 70 or k_val >= 75
            not_ready        = timing_tag == "⏳ Belum Waktunya"
            illiquid         = not liq_ok and turnover_m < 100

            masuk_syarat = [
                score >= 60,
                liq_ok,                      # min Rp 500 Juta/hari
                not strong_downtrend,         # tidak downtrend kuat
                not overbought,               # tidak overbought
                not not_ready,               # ada timing signal
                rr_ratio >= 1.0,             # risk-reward layak
            ]
            tunggu_syarat = [
                score >= 45,
                turnover_m >= 100,           # min likuid sedikit
                not strong_downtrend,
                not illiquid,
            ]

            if all(masuk_syarat):
                # Tambahan: jika stealth akumulasi kuat, verdict lebih yakin
                if stealth_score >= 2:
                    verdict = "🟢 MASUK ✨"
                    verdict_why = "Semua syarat terpenuhi + ada tanda akumulasi"
                else:
                    verdict = "🟢 MASUK"
                    verdict_why = "Teknikal OK, likuid, R:R layak"
            elif all(tunggu_syarat):
                if strong_downtrend:
                    verdict = "🟡 TUNGGU"
                    verdict_why = "Trend turun kuat, tunggu reversal konfirmasi"
                elif overbought:
                    verdict = "🟡 TUNGGU"
                    verdict_why = "Overbought — tunggu pullback dulu"
                elif not liq_ok:
                    verdict = "🟡 TUNGGU"
                    verdict_why = "Sinyal bagus tapi likuiditas rendah, sizing kecil"
                else:
                    verdict = "🟡 TUNGGU"
                    verdict_why = "Setup belum sempurna, masih perlu konfirmasi"
            else:
                if illiquid:
                    verdict = "🔴 HINDARI"
                    verdict_why = "Volume terlalu sepi, susah keluar posisi"
                elif strong_downtrend:
                    verdict = "🔴 HINDARI"
                    verdict_why = "Downtrend kuat (ADX tinggi), jangan lawan trend"
                elif score < 45:
                    verdict = "🔴 HINDARI"
                    verdict_why = "Sinyal teknikal lemah"
                else:
                    verdict = "🔴 HINDARI"
                    verdict_why = "Beberapa syarat penting tidak terpenuhi"

            results.append({
                # Identitas
                "Verdict":         verdict,
                "Layer":           layer_flag,
                "Ticker":          ticker.replace(".JK",""),
                "Harga":           round(price, 2),
                "Change %":        change,
                "Pot. Gain %":     pot_gain,
                # Trend
                "Trend":           trend,
                "ADX":             adx_val,
                "ADX Signal":      adx_label,
                # Indikator
                "RSI":             rsi,
                "RSI Signal":      rsi_label,
                "BB %B":           bb_pct_b,
                "BB Width %":      bb_width,
                "BB Signal":       bb_label,
                "Stoch %K":        k_val,
                "Stoch %D":        d_val,
                "Stoch Signal":    stoch_label,
                # Volume & Likuiditas
                "Vol Spike":       vol_spike,
                "Turnover (Jt)":   turnover_m,
                "Likuiditas":      liq_label,
                # Akumulasi
                "Stealth Akum":    stealth_label,
                "Akumulasi":       akum,
                "Pre-Surge":       pre_surge,
                # Score
                "Probability":     score,
                "Style":           style,
                "Style Reason":    style_why,
                # Entry Plan
                "Entry":           ideal_entry,
                "Stop Loss":       stop_loss,
                "ATR":             round(atr_val, 2),
                "Target":          target_pr,
                "R:R":             f"1:{rr_ratio}",
                "Lot Saran":       lot_saran,
                # Timing
                "Timing":          timing_tag,
                "Est. Masuk":      est_date,
                "Alasan Timing":   timing_why,
                # Verdict detail
                "Verdict Why":     verdict_why,
            })

        except Exception as e:
            errors.append(f"{ticker}: {type(e).__name__}: {e}")
            continue

    progress.empty()

    # ── Tampilkan ringkasan debug ────────────────────────────────────────
    if debug_mode:
        with st.expander(f"🐛 Debug: {len(errors)} error, {len(skipped)} dilewati"):
            if errors:
                st.markdown("**Error:**")
                for err in errors[:20]:   # max 20 baris
                    st.code(err)
            if skipped:
                st.markdown("**Dilewati (data kurang):**")
                for sk in skipped[:20]:
                    st.text(sk)

    if not results:
        st.error(
            "Tidak ada data berhasil dianalisa. Kemungkinan penyebab:\n\n"
            "1. **yfinance error** — klik **🔌 Test Koneksi** di sidebar\n"
            "2. **Rate limit** — terlalu banyak request, tunggu 1–2 menit\n"
            "3. **yfinance versi lama** — jalankan: `pip install --upgrade yfinance`\n\n"
            "Aktifkan **🐛 Debug Mode** di sidebar lalu analisis ulang untuk lihat error detail."
        )
        st.stop()

    st.session_state["df"]       = pd.DataFrame(results)
    st.session_state["analyzed"] = True
    st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# KOLOM TABEL
# ─────────────────────────────────────────────────────────────────────────────
COL_VERDICT = [
    "Verdict","Ticker","Layer","Harga","Change %","Pot. Gain %",
    "Trend","ADX","ADX Signal",
    "RSI","BB %B","Stoch %K","Stoch Signal",
    "Stealth Akum","Likuiditas","Turnover (Jt)",
    "Probability","Style",
    "Entry","Stop Loss","Target","R:R","Lot Saran",
    "Timing","Est. Masuk","Verdict Why",
]
COL_SUMMARY = [
    "Verdict","Layer","Ticker","Harga","Change %","Pot. Gain %","Trend",
    "RSI","RSI Signal","BB %B","BB Signal",
    "Stoch %K","Stoch %D","Stoch Signal",
    "Probability","Style",
    "Entry","Stop Loss","Target","R:R",
    "Vol Spike","Timing","Est. Masuk",
]
COL_TECH = [
    "Ticker","Layer","Harga","Trend","ADX","ADX Signal",
    "RSI","RSI Signal","BB %B","BB Width %","BB Signal",
    "Stoch %K","Stoch %D","Stoch Signal",
    "Stealth Akum","Akumulasi","Pre-Surge",
    "Vol Spike","Turnover (Jt)","Likuiditas","Probability",
]

# ─────────────────────────────────────────────────────────────────────────────
# DISPLAY  —  di luar button handler, session_state menjaga data tetap ada
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.get("analyzed") and "df" in st.session_state:
    df = st.session_state["df"]

    # ── Ringkasan metrik ─────────────────────────────────────────────────
    n_masuk  = len(df[df["Verdict"].str.startswith("🟢")])
    n_tunggu = len(df[df["Verdict"].str.startswith("🟡")])
    n_hindari= len(df[df["Verdict"].str.startswith("🔴")])
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("🟢 MASUK",   n_masuk)
    m2.metric("🟡 TUNGGU",  n_tunggu)
    m3.metric("🔴 HINDARI", n_hindari)
    m4.metric("📊 Total Scan", len(df))

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🟢 Verdict Final",
        "🔥 Rekomendasi Teratas",
        "🪙 Gocap / Penny",
        "📋 Semua Saham",
        "📊 Detail Teknikal",
        "📖 Panduan",
    ])

    # ── Tab 1: Verdict Final ──────────────────────────────────────────────
    with tab1:
        vcol1, vcol2 = st.columns(2)
        with vcol1:
            vf = st.radio("Filter Verdict", ["Semua","🟢 MASUK","🟡 TUNGGU","🔴 HINDARI"],
                          horizontal=True, key="vf")
        with vcol2:
            vs = st.multiselect("Filter Likuiditas",
                                ["🟢 Sangat Likuid","🟢 Likuid","🟡 Cukup Likuid",
                                 "🟠 Kurang Likuid","🔴 Tidak Likuid"],
                                default=[], key="vl")

        vdf = df.sort_values(["Verdict","Probability"], ascending=[True, False])
        if vf != "Semua":
            vdf = vdf[vdf["Verdict"].str.startswith(vf[:2])]
        if vs:
            vdf = vdf[vdf["Likuiditas"].isin(vs)]

        searchable_table(vdf, COL_VERDICT, "verdict")

        if show_detail:
            masuk_df = df[df["Verdict"].str.startswith("🟢")].sort_values("Probability", ascending=False)
            if not masuk_df.empty:
                st.divider()
                st.subheader("🔬 Detail Saham MASUK")
                for _, row in masuk_df.head(5).iterrows():
                    with st.expander(
                        f"{'🟢' if row['Verdict'].startswith('🟢') else '🟡'} "
                        f"{row['Ticker']} | Score {row['Probability']} | "
                        f"{row['Timing']} | {row['Likuiditas']}"
                    ):
                        c1,c2,c3,c4,c5,c6 = st.columns(6)
                        c1.metric("RSI",           row["RSI"])
                        c2.metric("BB %B",         f"{row['BB %B']}%")
                        c3.metric("Stoch %K",      row["Stoch %K"])
                        c4.metric("ADX",           row["ADX"])
                        c5.metric("Vol Spike",     f"{row['Vol Spike']}×")
                        c6.metric("Turnover",      f"Rp{row['Turnover (Jt)']:,.0f}Jt")

                        # Stealth akumulasi highlight
                        if row["Stealth Akum"] != "—":
                            st.success(f"🔍 **Stealth Akumulasi:** {row['Stealth Akum']}")

                        st.info(
                            f"✅ **Verdict:** {row['Verdict']}  ·  {row['Verdict Why']}\n\n"
                            f"⏰ **Timing:** {row['Timing']}  ·  📅 **Est.:** {row['Est. Masuk']}\n\n"
                            f"💡 {row['Alasan Timing']}"
                        )
                        ca,cb,cc,cd,ce = st.columns(5)
                        ca.metric("Entry",         f"Rp {row['Entry']:,.0f}")
                        cb.metric("Stop Loss",     f"Rp {row['Stop Loss']:,.0f}")
                        cc.metric("Target",        f"Rp {row['Target']:,.0f}")
                        cd.metric("R:R",           row["R:R"])
                        ce.metric("Lot Saran",     f"{row['Lot Saran']:,} lbr",
                                  help=f"Berdasarkan risk Rp{risk_rp:,}/trade")
                        st.caption(f"ATR: {row['ATR']}  ·  {row['Style']}  ·  {row['Style Reason']}")

    # ── Tab 2: Rekomendasi Teratas ────────────────────────────────────────
    with tab2:
        top = df[df["Probability"] >= min_score].sort_values("Probability", ascending=False)
        st.markdown(f"**{len(top)} saham** score ≥ {min_score}")
        searchable_table(top, COL_SUMMARY, "top")

    # ── Tab 3: Gocap / Penny ─────────────────────────────────────────────
    with tab3:
        gdf = df[df["Harga"] <= 200].sort_values("Probability", ascending=False)
        cg1,cg2,cg3,cg4 = st.columns(4)
        cg1.metric("Gocap ≤55",    len(df[df["Harga"] <= 55]))
        cg2.metric("Penny 56–200", len(df[(df["Harga"]>55)&(df["Harga"]<=200)]))
        cg3.metric("Pump Potential",len(gdf[gdf["Pre-Surge"]=="🔥 POTENSI PUMP"]))
        cg4.metric("Verdict MASUK", len(gdf[gdf["Verdict"].str.startswith("🟢")]))

        st.info("Saham gocap/penny: risiko tinggi, potensi % gain besar. Prioritaskan yang MASUK + Likuid.")
        gf2 = st.radio("Filter",["Semua","Gocap ≤55","Penny 56–200","Vol Spike >2×","Verdict MASUK"],
                        horizontal=True, key="gf2")
        if gf2 == "Gocap ≤55":               gdf = gdf[gdf["Harga"] <= 55]
        elif gf2 == "Penny 56–200":           gdf = gdf[(gdf["Harga"]>55)&(gdf["Harga"]<=200)]
        elif gf2 == "Vol Spike >2×":          gdf = gdf[gdf["Vol Spike"] > 2.0]
        elif gf2 == "Verdict MASUK":          gdf = gdf[gdf["Verdict"].str.startswith("🟢")]
        searchable_table(gdf, COL_VERDICT, "gocap")

    # ── Tab 4: Semua Saham ────────────────────────────────────────────────
    with tab4:
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            ft = st.multiselect("Filter Trend", ["🟢 UPTREND","⚪ SIDEWAYS","🔴 DOWNTREND"],
                                default=[], key="ft")
        with col_f2:
            fti = st.multiselect("Filter Timing",
                                 ["⚡ MASUK SEKARANG","📅 1–2 Hari","📅 ~3 Hari","📅 ~1 Minggu","⏳ Belum Waktunya"],
                                 default=[], key="fti")
        with col_f3:
            fv = st.multiselect("Filter Verdict",
                                ["🟢 MASUK ✨","🟢 MASUK","🟡 TUNGGU","🔴 HINDARI"],
                                default=[], key="fv")

        adf = df.sort_values("Probability", ascending=False)
        if ft:  adf = adf[adf["Trend"].isin(ft)]
        if fti: adf = adf[adf["Timing"].isin(fti)]
        if fv:  adf = adf[adf["Verdict"].isin(fv)]
        searchable_table(adf, COL_SUMMARY, "all")

    # ── Tab 5: Detail Teknikal ────────────────────────────────────────────
    with tab5:
        searchable_table(df.sort_values("Probability", ascending=False), COL_TECH, "tech")

    # ── Tab 6: Panduan ────────────────────────────────────────────────────
    with tab6:
        st.markdown("""
### 🟢🟡🔴 Logika Verdict Final

Verdict mengecek **semua syarat sekaligus**, bukan hanya score:

| Verdict | Syarat |
|---|---|
| **🟢 MASUK ✨** | Score ≥60 + Likuid + Tidak downtrend kuat + Tidak OB + Ada timing + R:R ≥1 + **Ada stealth akumulasi** |
| **🟢 MASUK** | Score ≥60 + Likuid + Tidak downtrend kuat + Tidak OB + Ada timing + R:R ≥1 |
| **🟡 TUNGGU** | Score ≥45 + Cukup likuid + Tidak downtrend kuat, tapi ada syarat yang belum |
| **🔴 HINDARI** | Score <45, atau tidak likuid, atau downtrend kuat (ADX≥25) |

### 📊 Indikator Baru

| Indikator | Penjelasan |
|---|---|
| **ADX** | Kekuatan trend. ≥25 = trend kuat, <20 = sideways. Lihat juga arah (+DI vs -DI). |
| **ATR** | Average True Range — volatilitas harian nyata. Stop Loss pakai 1.5×ATR dari entry. |
| **Turnover (Jt)** | Nilai transaksi harian rata-rata dalam juta IDR. Lebih akurat dari Vol Spike untuk likuiditas. |
| **Likuiditas** | ≥Rp5M/hari = Sangat Likuid. ≥Rp500Jt = Cukup. <Rp100Jt = Tidak Likuid (hindari). |
| **Stealth Akum** | Proxy akumulasi bandar dari 4 sinyal: OBV naik konsisten, OBV↑ harga stagnan, volume bertahap naik, BB squeeze+volume naik. |
| **Lot Saran** | Jumlah lembar yang disarankan berdasarkan Risk per Trade yang kamu set di sidebar. |

### 🔍 Kenapa Saham Teknikal Bagus Bisa Tidak Ada Bandarnya?

Indikator teknikal hanya membaca **pola matematis** dari harga & volume historis. Mereka tidak tahu apakah ada pemain besar yang aktif. **Stealth Akum** di app ini adalah *proxy* — bukan pengganti broker flow.

Untuk konfirmasi bandar, cek manual di Stockbit/RTI Business:
- **Broker Flow** — apakah ada 1-2 broker konsisten beli dalam beberapa hari?
- **Bid-Ask Depth** — bid tebal tapi offer tipis = ada yang support harga
- **Unusual Transaction** — block trade atau odd-lot besar

---
> ⚠️ **Bukan saran investasi.** Selalu lakukan riset sendiri dan terapkan manajemen risiko.
        """)

st.caption(
    f"Data: Yahoo Finance · RSI 14 · MACD 12/26/9 · BB 20-2σ · Stoch 14-3-3 · ADX 14 · ATR 14 · "
    f"Universe: {len(set(LAYER1+LAYER2+LAYER3_SPECULATIVE+GOCAP_WATCHLIST))}+ ticker IDX"
)
