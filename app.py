import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import feedparser  # RSS 파싱용 (pip install feedparser)
from streamlit_autorefresh import st_autorefresh

# --- [1. 네이버 파이낸스 API (스크레이핑) 함수] ---
def get_naver_stock(code):
    """네이버 파이낸스에서 실시간 주가와 등락률을 가져옵니다."""
    url = f"https://finance.naver.com/item/main.naver?code={code}"
    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 실시간 가격 추출
        price_tag = soup.select_one(".today .no_today .blind")
        curr_price = int(price_tag.text.replace(",", ""))
        
        # 전일 대비 변동폭 및 등락률 계산용
        diff_tag = soup.select_one(".today .no_exday .blind")
        diff_val = int(diff_tag.text.replace(",", ""))
        
        # 상승/하락 여부에 따른 부호 설정
        direction = soup.select_one(".today .no_exday .ico")
        if direction and "상승" in direction.text:
            pass 
        elif direction and "하락" in direction.text:
            diff_val = -diff_val
            
        prev_close = curr_price - diff_val
        perc = (diff_val / prev_close) * 100
        
        return {'curr': curr_price, 'perc': perc}
    except:
        return None

# --- [2. RSS 뉴스 가져오기 함수] ---
def get_stock_news(limit=6):
    """매일경제 주식 RSS에서 최신 뉴스 6개를 가져옵니다."""
    rss_url = "https://www.mk.co.kr/rss/30200001/" # 매경 증권 RSS
    feed = feedparser.parse(rss_url)
    news_list = []
    for entry in feed.entries[:limit]:
        news_list.append({
            "title": entry.title,
            "link": entry.link
        })
    return news_list

# --- [3. 페이지 설정 및 찬후님 원본 디자인 (CSS)] ---
st.set_page_config(page_title="국내-해외 주식 현황 모니터링", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', sans-serif; }
    .main-title { font-size: 40px !important; font-weight: 800; color: #FFFFFF; text-align: center; margin-bottom: 5px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }
    .sub-title { font-size: 18px; color: #888888; text-align: center; font-style: italic; margin-bottom: 30_0px; }

    /* 찬후님 전용 빨강-보라 그라데이션 버튼 */
    div.stButton > button {
        width: 100%; border-radius: 12px; border: none; padding: 12px 20px;
        background: linear-gradient(135deg, #FF4B4B 0%, #764BA2 100%); 
        color: white !important; font-weight: 700; font-size: 16px;
        box-shadow: 0 4px 15px rgba(118, 75, 162, 0.4); 
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); cursor: pointer;
    }
    div.stButton > button:hover { transform: translateY(-3px) scale(1.02); box-shadow: 0 8px 25px rgba(118, 75, 162, 0.6); }
    [data-testid="stMetric"] { background-color: #1e1e1e; padding: 20px; border-radius: 15px; }
    
    /* RSS 뉴스 스타일 */
    .news-item { font-size: 14px; margin-bottom: 10px; padding: 8px; border-bottom: 1px solid #333; }
    .news-link { color: #FF4B4B; text-decoration: none; font-weight: 500; }
    .news-link:hover { text-decoration: underline; }
    </style>
    """, unsafe_allow_html=True)

st_autorefresh(interval=60000, key="auto_refresh")

# --- [4. 사이드바 (설정 + RSS 뉴스)] ---
with st.sidebar:
    st.header("📊 모니터링 설정")
    stock_dict = {
        "삼성전자 (Samsung)": {"id": "005930", "y": "005930.KS"},
        "SK 하이닉스 (Hynix)": {"id": "000660", "y": "000660.KS"},
        "엔비디아 (NVDA)": {"id": "NVDA", "y": "NVDA"} # 해외주는 yfinance 병행
    }
    selected_names = st.multiselect("종목 선택", list(stock_dict.keys()), default=["삼성전자 (Samsung)", "엔비디아 (NVDA)"])
    
    if st.button("새로고침 (수동)", use_container_width=True):
        st.rerun()

    st.divider()
    st.header("📰 최신 증권 뉴스 (RSS)")
    news_data = get_stock_news(6)
    for news in news_data:
        st.markdown(f"""
        <div class="news-item">
            <a class="news-link" href="{news['link']}" target="_blank">· {news['title']}</a>
        </div>
        """, unsafe_allow_html=True)

# --- [5. 메인 화면 출력] ---
st.markdown('<p class="main-title">주식 추세 일람 그래프</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">𝕽𝖊𝖆𝖑-𝖙𝖎𝖒𝖊 𝕱𝖎𝖓𝖆𝖓𝖈𝖎𝖆𝖑 𝕸𝖔𝖓𝖎𝖙𝖔𝖗𝖎𝖓𝖌 𝕾𝖞𝖘𝖙𝖊𝖒</p>', unsafe_allow_html=True)

# 검색창 (찬후님 원본 100% 복구)
search_q = st.text_input("", placeholder="알아보고 싶은 종목명을 입력해주세요.")
if search_q:
    refined_q = f"{search_q} 주가"
    s_col1, s_col2, s_col3 = st.columns(3)
    with s_col1: st.link_button("🌐 Google", f"https://www.google.com/search?q={refined_q}", use_container_width=True)
    with s_col2: st.link_button("네이버", f"https://search.naver.com/search.naver?query={refined_q}", use_container_width=True)
    with s_col3: st.link_button("다음", f"https://search.daum.net/search?q={refined_q}", use_container_width=True)

st.divider()

if selected_names:
    cols = st.columns(len(selected_names))
    for i, name in enumerate(selected_names):
        info = stock_dict[name]
        with cols[i]:
            # 국내주는 네이버 파이낸스, 해외주는 yfinance 엔진 사용
            if info["id"].isdigit(): # 종목코드가 숫자면 국내주
                n_data = get_naver_stock(info["id"])
                if n_data:
                    st.metric(label=name, value=f"{n_data['curr']:,}원", delta=f"{n_data['perc']:+.2f}%")
            else:
                y_data = yf.Ticker(info["y"]).history(period="1d")
                if not y_data.empty:
                    curr = y_data['Close'].iloc[-1]
                    st.metric(label=name, value=f"${curr:,.2f}")

            # 그래프는 기존 찬후님 스타일 그대로
            df = yf.Ticker(info["y"]).history(period="1d", interval="1m")
            if not df.empty:
                fig = go.Figure(go.Scatter(x=df.index, y=df['Close'], fill='tozeroy', mode='lines', line=dict(color="#FF4B4B", width=3)))
                fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=250, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

st.divider()
st.text_area("메모장", placeholder="텍스트 입력..", height=120)
