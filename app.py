import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import feedparser
from streamlit_autorefresh import st_autorefresh

# --- [1. 엔진 함수 정의] ---
def get_naver_stock(code):
    url = f"https://finance.naver.com/item/main.naver?code={code}"
    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        price_tag = soup.select_one(".today .no_today .blind")
        curr_price = int(price_tag.text.replace(",", ""))
        diff_tag = soup.select_one(".today .no_exday .blind")
        diff_val = int(diff_tag.text.replace(",", ""))
        direction = soup.select_one(".today .no_exday .ico")
        if direction and "하락" in direction.text: diff_val = -diff_val
        prev_close = curr_price - diff_val
        perc = (diff_val / prev_close) * 100
        return {'curr': curr_price, 'perc': perc}
    except: return None

def get_google_stock_news(limit=10):
    rss_url = "https://news.google.com/rss/search?q=주식&hl=ko&gl=KR&ceid=KR:ko"
    try:
        feed = feedparser.parse(rss_url)
        results = []
        for entry in feed.entries[:limit]:
            title = entry.title
            if " - " in title: title = title.rsplit(" - ", 1)[0]
            if " By " in title: title = title.split(" By ")[0]
            elif " by " in title: title = title.split(" by ")[0]
            results.append({"title": title.strip(), "link": entry.link})
        return results
    except: return []

# --- [2. 페이지 설정 및 디자인] ---
st.set_page_config(page_title="주식 실시간 모니터링 시스템", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', sans-serif; }
    .main-title {
        font-size: 40px !important; font-weight: 900 !important;
        background: linear-gradient(135deg, #FF4B4B, #764BA2);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-shadow: 2px 2px 8px rgba(255, 75, 75, 0.4); text-align: center; margin-bottom: 5px;
    }
    .sub-title {
        font-size: 14px !important; font-weight: 400 !important; color: #888888 !important;
        text-align: center; margin-bottom: 35px; letter-spacing: 1px;
    }
    div.stButton > button {
        width: 100%; border-radius: 10px; background: linear-gradient(135deg, #FF4B4B, #764BA2);
        color: white !important; font-weight: 700; border: none; padding: 10px;
    }
    [data-testid="stMetric"] { background-color: #1e1e1e; padding: 15px; border-radius: 12px; margin-bottom: 15px; }
    .news-item { font-size: 13px; margin-bottom: 10px; border-bottom: 1px solid #333; padding-bottom: 5px; }
    .news-link { color: #FF4B4B; text-decoration: none; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

st_autorefresh(interval=60000, key="final_refresh_timer")

# --- [3. 사이드바 설정] ---
with st.sidebar:
    st.header("⚙ 종목ㆍ기간 설정")
    stock_dict = {
        "삼성전자 (Samsung)": {"id": "005930", "y": "005930.KS"},
        "현대자동차 (Hyundai)": {"id": "005380", "y": "005380.KS"},
        "SK 하이닉스 (Hynix)": {"id": "000660", "y": "000660.KS"},
        "엔비디아 (NVDA)": {"id": "NVDA", "y": "NVDA"},
        "알파벳(구글) (GOOG)": {"id": "GOOG", "y": "GOOG"},
        "LG전자": {"id": "066570", "y": "066570.KS"},
        "넷플릭스 (NFLX)": {"id": "NFLX", "y": "NFLX"},
        "맥도날드": {"id": "MCD", "y": "MCD"}

    }
    selected_names = st.multiselect("종목 선택", options=list(stock_dict.keys()), default=["삼성전자 (Samsung)"])
    
    st.divider()
    period_options = {"1주일": "7d", "1개월": "1mo", "6개월": "6mo", "1년": "1y", "5년": "5y"}
    selected_period_label = st.selectbox("모니터링 기간", options=list(period_options.keys()), index=2)
    selected_p = period_options[selected_period_label]

    st.divider()
    st.subheader("목표 가격 설정")
    target_price = st.number_input("목표 가격 설정", min_value=0.0, value=0.0, step=100.0)

    if st.button("확인", width='stretch', key="sidebar_btn"): st.rerun()

    st.divider()
    st.subheader("📰 오늘의 주식 뉴스")
    news_data = get_google_stock_news(6)
    if news_data:
        for news in news_data:
            st.markdown(f'<div class="news-item">· <a class="news-link" href="{news["link"]}" target="_blank">{news["title"]}</a></div>', unsafe_allow_html=True)

# --- [4. 메인 화면] ---
st.markdown('<p class="main-title">주식 추세 일람 그래프</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">𝕽𝖊𝖆𝖑-𝖙𝖎𝖒𝖊 𝕱𝖎𝖓𝖆𝖓𝖈𝖎𝖆𝖑 𝕸𝖔𝖓𝖎𝖙𝖔𝖗𝖎𝖓𝖌 𝕾𝖞𝖘𝖙𝖊𝖒</p>', unsafe_allow_html=True)

if selected_names:
    for name in selected_names:
        info = stock_dict[name]
        m_col1, m_col2 = st.columns([1, 4])
        
        with m_col1:
            if info["id"].isdigit():
                res = get_naver_stock(info["id"])
                if res: st.metric(label=name, value=f"{res['curr']:,}원", delta=f"{res['perc']:+.2f}%")
            else:
                y_t = yf.Ticker(info["y"])
                y_h = y_t.history(period="1d")
                if not y_h.empty:
                    c_v = y_h['Close'].iloc[-1]
                    p_c = y_t.info.get('regularMarketPreviousClose', c_v)
                    st.metric(label=name, value=f"${c_v:,.2f}", delta=f"{(c_v-p_c)/p_c*100:+.2f}%")

        # --- [차트 생성] ---
        itv = "30m" if selected_p == "7d" else "1d"
        df = yf.Ticker(info["y"]).history(period=selected_p, interval=itv)
        
        if not df.empty:
            df['MA5'] = df['Close'].rolling(5).mean(); df['MA20'] = df['Close'].rolling(20).mean(); df['MA60'] = df['Close'].rolling(60).mean()
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_width=[0.2, 0.8])
            
            # 캔들 & 이평선
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price', increasing_line_color='#FF4B4B', decreasing_line_color='#0083B0'), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['5일 이동평균선'], name='MA5', line=dict(color='#FFEE00', width=1.2)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['20일 이동평균선'], name='MA20', line=dict(color='#FF00FF', width=1.2)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['60일 이동평균선'], name='MA60', line=dict(color='#00FF00', width=1.2)), row=1, col=1)
            
            if target_price > 0:
                fig.add_hline(y=target_price, line_dash="dash", line_color="white", annotation_text=f"Target: {target_price:,.0f}", row=1, col=1)

            fig.add_trace(go.Bar(x=df.index, y=df['거래량'], name='Volume', marker_color='#FF4B4B', opacity=0.5), row=2, col=1)

            # 레이아웃 & 🔥 호버 글자 검정색 설정
            fig.update_layout(
                height=550, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=10, b=10), xaxis_rangeslider_visible=False, dragmode=False,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hoverlabel=dict(font=dict(color="black", size=13), bgcolor="white") # 호버 스타일링
            )
            with m_col2: st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.divider()
# --- [5. 메모장] ---
m1, m2 = st.columns([4, 1])
with m1: st.text_area("메모장", placeholder="텍스트를 입력해보세요... 삼떡기", height=100)
with m2: 
    st.write("")
    st.write("")
    if st.button("새로고침🔄", width='stretch', key="main_btn"): st.rerun()
