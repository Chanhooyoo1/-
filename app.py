import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import feedparser
from streamlit_autorefresh import st_autorefresh
    
# 1.신문 기사 크롤링 엔진
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
        if direction and "하락" in direction.text:
            diff_val = -diff_val
        prev_close = curr_price - diff_val
        perc = (diff_val / prev_close) * 100
        return {'curr': curr_price, 'perc': perc}
    except: return None

def get_google_stock_news(limit=10):
    #언론사 제거
    rss_url = "https://news.google.com/rss/search?q=주식&hl=ko&gl=KR&ceid=KR:ko"
    try:
        import feedparser
        feed = feedparser.parse(rss_url)
        results = []
        
        for entry in feed.entries[:limit]:
            title = entry.title
            
            # 1. ' - ' 기호를 기준으로 오른쪽 끝에서부터 잘라냅니다. (언론사 제거)
            if " - " in title:
                title = title.rsplit(" - ", 1)[0]
            
            # 2. ' By ' 혹은 ' by ' 문구가 있다면 그 뒤를 모두 제거합니다.
            if " By " in title:
                title = title.split(" By ")[0]
            elif " by " in title:
                title = title.split(" [ ")[0]
            
            # 3. 양옆 공백 제거 후 저장
            results.append({
                "title": title.strip(), 
                "link": entry.link
            })
        return results
    except:
        return []

# 2. 페이지 디자인
st.set_page_config(page_title="주식 실시간 모니터링", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', sans-serif; }
    
    /* 🔥 [메인 제목 화려하게] 🔥 */
    .main-title {
        font-size: 40px !important;    /* 크기 40 */
        font-weight: 900 !important;   /* 볼드 (가장 두껍게) */
        
        /* ✨ 그라데이션 (빨강 -> 보라) */
        background: linear-gradient(135deg, #FF4B4B, #764BA2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        
        /* 🌑 그림자 (네온 느낌 살짝) */
        text-shadow: 2px 2px 8px rgba(255, 75, 75, 0.4);
        
        text-align: center;
        margin-bottom: 5px;
    }
    
    /* 🌑 [부제목 심플하게] 🌑 */
    .sub-title {
        font-size: 14px !important;    /* 작게 */
        font-weight: 400 !important;   /* 얇게 */
        color: #888888 !important;     /* 회색 */
        text-align: center;
        margin-bottom: 35px;
        letter-spacing: 1px;           /* 자간 살짝 넓힘 */
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

# 온리원호출!!!!
st_autorefresh(interval=60000, key="final_refresh_timer")

#3. 사이드바 종목 목록
with st.sidebar:
    st.header("📊 설정")
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
    
    selected_names = st.multiselect(
        "종목 선택", 
        options=list(stock_dict.keys()), 
        default=["삼성전자 (Samsung)"]
    )
    
    st.divider()
    if st.button("새로고침", width='stretch', key="sidebar_btn"):
        st.rerun()

    st.divider()
    st.subheader("📰 오늘의 주식 관련 뉴스")
    # 구글 뉴스
    news_data = get_google_stock_news(6)
    if news_data:
        for news in news_data:
            st.markdown(f'<div class="news-item">· <a class="news-link" href="{news["link"]}" target="_blank">{news["title"]}</a></div>', unsafe_allow_html=True)
    else:
        st.info("뉴스를 로딩 중이거나 가져올 수 없습니다.")

# 메인
st.markdown('<p class="main-title">주식 추세 일람 그래프</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">𝕽𝖊𝖆𝖑-𝖙𝖎𝖒𝖊 𝕱𝖎𝖓𝖆𝖓𝖈𝖎𝖆𝖑 𝕸𝖔𝖓𝖎𝖙𝖔𝖗𝖎𝖓𝖌 𝕾𝖞𝖘𝖙𝖊𝖒</p>', unsafe_allow_html=True)

search_q = st.text_input("검색", placeholder="종목명을 입력하세요", label_visibility="collapsed")
if search_q:
    c1, c2, c3 = st.columns(3)
    with c1: st.link_button("Google", f"https://www.google.com/search?q={search_q}+주가", width='stretch')
    with c2: st.link_button("네이버", f"https://search.naver.com/search.naver?query={search_q}+주가", width='stretch')
    with c3: st.link_button("다음", f"https://search.daum.net/search?q={search_q}+주가", width='stretch')

st.divider()

if selected_names:
    cols = st.columns(len(selected_names))
    for i, name in enumerate(selected_names):
        info = stock_dict[name]
        with cols[i]:
            if info["id"].isdigit(): # 국내
                res = get_naver_stock(info["id"])
                if res:
                    st.metric(label=name, value=f"{res['curr']:,}원", delta=f"{res['perc']:+.2f}%")
            else: # 해외
                y_ticker = yf.Ticker(info["y"])
                y_hist = y_ticker.history(period="1d")
                if not y_hist.empty:
                    curr_val = y_hist['Close'].iloc[-1]
                    prev_close = y_ticker.info.get('regularMarketPreviousClose', curr_val)
                    perc = (curr_val - prev_close) / prev_close * 100
                    st.metric(label=name, value=f"${curr_val:,.2f}", delta=f"{perc:+.2f}%")

            # 그래프 경고
            df = yf.Ticker(info["y"]).history(period="1d", interval="1m")
            if not df.empty:
                fig = go.Figure(go.Scatter(x=df.index, y=df['Close'], fill='tozeroy', mode='lines', line=dict(color="#FF4B4B")))
                fig.update_layout(margin=dict(l=0,r=0,t=10,b=0), height=250, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

st.divider()
m1, m2 = st.columns([4, 1])
with m1: st.text_area("메모장", placeholder="오늘의 투자 메모..", height=100)
with m2: 
    st.write("")
    st.write("")
    if st.button("새로고침🔄", width='stretch', key="main_btn"):
        st.rerun()
