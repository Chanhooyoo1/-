import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import feedparser
from streamlit_autorefresh import st_autorefresh

# --- [1. 네이버 파이낸스 실시간 엔진] ---
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
    except:
        return None
# --- [2. RSS 뉴스 가져오기 (연합뉴스 정밀 버전)] ---
def get_stock_news_naver(limit=6):
    # '주식' 키워드로 검색한 네이버 뉴스 최신순 결과
    url = "https://search.naver.com/search.naver?where=news&query=주식&sm=tab_pge&sort=1"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        news_items = soup.select(".news_tit") # 뉴스 제목 클래스 추출
        
        results = []
        for item in news_items[:limit]:
            results.append({
                "title": item.get("title"),
                "link": item.get("href")
            })
        return results
    except:
        return []
        st.info("💡 인터넷 연결을 확인하거나 잠시 후 새로고침을 눌러주세요.")
# --- [3. 페이지 설정 및 디자인 (CSS)] ---
st.set_page_config(page_title="국내-해외 주식 현황 모니터링", page_icon="📈", layout="wide")

# CSS의 따옴표 닫힘을 완벽하게 확인했습니다.
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', sans-serif; }
    
    .main-title { 
        font-size: 40px !important; font-weight: 800; color: #FFFFFF; 
        text-align: center; margin-bottom: 5px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); 
    }
    .sub-title { 
        font-size: 18px; color: #888888; text-align: center; 
        font-style: italic; margin-bottom: 30px; 
    }

    div.stButton > button {
        width: 100%; border-radius: 12px; border: none; padding: 12px 20px;
        background: linear-gradient(135deg, #FF4B4B 0%, #764BA2 100%); 
        color: white !important; font-weight: 700; font-size: 16px;
        box-shadow: 0 4px 15px rgba(118, 75, 162, 0.4); 
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); cursor: pointer;
    }

    [data-testid="stMetric"] { background-color: #1e1e1e; padding: 20px; border-radius: 15px; }
    
    .news-item { font-size: 13px; margin-bottom: 8px; border-bottom: 1px solid #222; padding-bottom: 5px; }
    .news-link { color: #FF4B4B; text-decoration: none; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

st_autorefresh(interval=60000, key="auto_refresh")

# --- [4. 사이드바 (2026 표준 문법 적용)] ---
with st.sidebar:
    st.header("📊 모니터링 설정")
    stock_dict = {
        "삼성전자 (Samsung)": {"id": "005930", "y": "005930.KS"},
        "현대자동차 (Hyundai)": {"id": "005380", "y": "005380.KS"},
        "SK 하이닉스 (Hynix)": {"id": "000660", "y": "000660.KS"},
        "엔비디아 (NVDA)": {"id": "NVDA", "y": "NVDA"},
        "알파벳(구글) (GOOG)": {"id": "GOOG", "y": "GOOG"},
        "애플 (AAPL)": {"id": "AAPL", "y": "AAPL"}
    }
    selected_names = st.multiselect("종목 선택", list(stock_dict.keys()), default=["엔비디아 (NVDA)", "삼성전자 (Samsung)"])
    
    # use_container_width=True -> width='stretch'로 변경 완료
    if st.button("새로고침 (수동)", width='stretch'):
        st.rerun()

    st.divider()
    st.subheader("📰 실시간 주요 뉴스")
    news_list = get_stock_news(6)
    if news_list:
        for news in news_list:
            short_title = news["title"][:25] + ".." if len(news["title"]) > 25 else news["title"]
            st.markdown(f'<div class="news-item">· <a class="news-link" href="{news["link"]}" target="_blank">{short_title}</a></div>', unsafe_allow_html=True)
    else:
        st.info("뉴스를 불러올 수 없습니다.")

# --- [5. 메인 화면 (로그 경고 해결)] ---
st.markdown('<p class="main-title">주식 추세 일람 그래프</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">𝕽𝖊𝖆𝖑-𝖙𝖎𝖒𝖊 𝕱𝖎𝖓𝖆𝖓𝖈𝖎𝖆𝖑 𝕸𝖔𝖓𝖎𝖙𝖔𝖗𝖎𝖓𝖌 𝕾𝖞𝖘𝖙𝖊𝖒</p>', unsafe_allow_html=True)

# empty label 경고 해결: 라벨을 넣고 visibility를 collapsed로 설정
search_q = st.text_input("종목명 검색", placeholder="알아보고 싶은 종목명을 입력해주세요.", label_visibility="collapsed")

if search_q:
    refined_q = f"{search_q} 주가"
    s_col1, s_col2, s_col3 = st.columns(3)
    # 모든 버튼 width='stretch' 적용
    with s_col1: st.link_button("🌐 Google", f"https://www.google.com/search?q={refined_q}", width='stretch')
    with s_col2: st.link_button("네이버", f"https://search.naver.com/search.naver?query={refined_q}", width='stretch')
    with s_col3: st.link_button("다음", f"https://search.daum.net/search?q={refined_q}", width='stretch')

st.divider()

if selected_names:
    cols = st.columns(len(selected_names))
    for i, name in enumerate(selected_names):
        info = stock_dict[name]
        with cols[i]:
            if info["id"].isdigit():
                data = get_naver_stock(info["id"])
                if data:
                    st.metric(label=name, value=f"{data['curr']:,}원", delta=f"{data['perc']:+.2f}%")
            else:
                y_data = yf.Ticker(info["y"]).history(period="1d")
                if not y_data.empty:
                    curr = y_data['Close'].iloc[-1]
                    prev = y_data['Open'].iloc[0]
                    perc = (curr - prev) / prev * 100
                    st.metric(label=name, value=f"${curr:,.2f}", delta=f"{perc:+.2f}%")

            df = yf.Ticker(info["y"]).history(period="1d", interval="1m")
            if not df.empty:
                fig = go.Figure(go.Scatter(x=df.index, y=df['Close'], fill='tozeroy', mode='lines', line=dict(color="#FF4B4B", width=3)))
                fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

st.divider()
st.text_area("메모장", placeholder="텍스트 입력..", height=120)
