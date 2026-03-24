import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
from streamlit_autorefresh import st_autorefresh

# --- [1. 엔진 함수 정의] ---

def get_naver_stock(code):
    """네이버 파이낸스 실시간 주가 크롤링"""
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

def get_naver_news_search(limit=6):
    """네이버 뉴스에서 '주식' 키워드로 최신 뉴스 검색 결과 가져오기"""
    # '주식' 키워드 + 최신순(sort=1) 정렬 주소입니다.
    url = "https://search.naver.com/search.naver?where=news&query=주식&sm=tab_pge&sort=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 네이버 뉴스 검색 결과의 제목 태그 선택자입니다.
        news_items = soup.select(".news_tit")
        
        results = []
        for item in news_items[:limit]:
            results.append({
                "title": item.get("title"),
                "link": item.get("href")
            })
        return results
    except Exception as e:
        print(f"뉴스 로딩에 실패했어요. 나중에 다시 시도해주세요.: {e}")
        return []

# --- [2. 페이지 설정 및 디자인] ---
st.set_page_config(page_title="주식 실시간 모니터링", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', sans-serif; }
    .main-title { font-size: 35px; font-weight: 800; color: white; text-align: center; margin-bottom: 20px; }
    div.stButton > button {
        width: 100%; border-radius: 10px; background: linear-gradient(135deg, #FF4B4B, #764BA2);
        color: white !important; font-weight: 700; border: none; padding: 10px;
    }
    [data-testid="stMetric"] { background-color: #1e1e1e; padding: 15px; border-radius: 12px; }
    .news-item { font-size: 13px; margin-bottom: 10px; border-bottom: 1px solid #333; padding-bottom: 5px; }
    .news-link { color: #FF4B4B; text-decoration: none; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

st_autorefresh(interval=60000, key="auto_refresh")

# --- [3. 사이드바] ---
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
        default=["엔비디아 (NVDA)", "삼성전자 (Samsung)"]
    )
    
    st.divider()

    if st.button("새로고침", width='stretch', key="sidebar_btn"):
        st.rerun()

    st.divider()
    st.subheader("📰 네이버 주식 뉴스")
    # RSS 대신 네이버 검색 함수 사용
    news_data = get_naver_news_search(6)
    
    if news_data:
        for news in news_data:
            short_t = news["title"][:22] + ".." if len(news["title"]) > 22 else news["title"]
            st.markdown(f'<div class="news-item">· <a class="news-link" href="{news["link"]}" target="_blank" title="{news["title"]}">{short_t}</a></div>', unsafe_allow_html=True)
    else:
        st.info("네이버 뉴스를 가져올 수 없습니다.")

# --- [4. 메인 화면] ---
st.markdown('<p class="main-title">실시간 주식 대시보드</p>', unsafe_allow_html=True)

search_q = st.text_input("검색", placeholder="종목명을 입력하세요", label_visibility="collapsed")
if search_q:
    c1, c2, c3 = st.columns(3)
    with c1: st.link_button("🌐 Google", f"https://www.google.com/search?q={search_q}+주가", width='stretch')
    with c2: st.link_button("네이버", f"https://search.naver.com/search.naver?query={search_q}+주가", width='stretch')
    with c3: st.link_button("다음", f"https://search.daum.net/search?q={search_q}+주가", width='stretch')

st.divider()

if selected_names:
    cols = st.columns(len(selected_names))
    for i, name in enumerate(selected_names):
        info = stock_dict[name]
        with cols[i]:
            if info["id"].isdigit(): # 국내주식
                res = get_naver_stock(info["id"])
                if res:
                    st.metric(label=name, value=f"{res['curr']:,}원", delta=f"{res['perc']:+.2f}%")
            else: # 해외주식
                y_ticker = yf.Ticker(info["y"])
                y_hist = y_ticker.history(period="1d")
                if not y_hist.empty:
                    curr_val = y_hist['Close'].iloc[-1]
                    prev_close = y_ticker.info.get('regularMarketPreviousClose', curr_val)
                    perc = (curr_val - prev_close) / prev_close * 100
                    st.metric(label=name, value=f"${curr_val:,.2f}", delta=f"{perc:+.2f}%")

            df = yf.Ticker(info["y"]).history(period="1d", interval="1m")
            if not df.empty:
                fig = go.Figure(go.Scatter(x=df.index, y=df['Close'], fill='tozeroy', mode='lines', line=dict(color="#FF4B4B")))
                fig.update_layout(margin=dict(l=0,r=0,t=10,b=0), height=250, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

st.divider()
m1, m2 = st.columns([4, 1])
with m1: st.text_area("메모장", placeholder="오늘의 투자 메모..", height=100)
with m2: 
    st.write("")
    st.write("")
    if st.button("새로고침🔄", width='stretch', key="main_btn"):
        st.rerun()
