import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
import pandas as p
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
    except: return None

# --- [2. RSS 뉴스 (에러 방지 강화 버전)] ---
def get_stock_news(limit=6):
    # 매일경제 RSS (만약 이게 안 되면 아래 주석의 연합뉴스로 바꿔보세요)
    rss_url = "https://www.mk.co.kr/rss/30200001/" 
    # rss_url = "https://www.yonhapnewstv.co.kr/browse/feed/" # 연합뉴스 TV (대안)
    
    try:
        feed = feedparser.parse(rss_url)
        # 피드가 비어있거나 에러가 났을 때 처리
        if not feed.entries:
            return []
        return [{"title": entry.title, "link": entry.link} for entry in feed.entries[:limit]]
    except Exception as e:
        print(f"RSS Error: {e}")
        return []

# --- [3. 디자인 설정 (찬후님 원본 CSS 100% 복사)] ---
st.set_page_config(page_title="국내-해외 주식 현황 모니터링", page_icon="📈", layout="wide")

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

    /* ★ 찬후님 전용 빨강-보라 그라데이션 버튼 애니메이션 ★ */
    div.stButton > button {
        width: 100%; border-radius: 12px; border: none; padding: 12px 20px;
        background: linear-gradient(135deg, #FF4B4B 0%, #764BA2 100%); 
        color: white !important; font-weight: 700; font-size: 16px;
        box-shadow: 0 4px 15px rgba(118, 75, 162, 0.4); 
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); cursor: pointer;
    }
    div.stButton > button:hover { 
        transform: translateY(-3px) scale(1.02); 
        box-shadow: 0 8px 25px rgba(118, 75, 162, 0.6); 
        background: linear-gradient(135deg, #FF6B6B 0%, #8A54C9 100%); 
    }
    div.stButton > button:active { transform: translateY(1px) scale(0.95); }

    [data-testid="stMetric"] { 
        background-color: #1e1e1e; padding: 20px; border-radius: 15px; 
        box-shadow: inset 0 0 10px rgba(255,255,255,0.05); 
    }
    
    /* 뉴스 리스트 스타일 */
    .news-box { padding: 10px; background: #111; border-radius: 10px; margin-top: 10px; }
    .news-item { font-size: 13px; margin-bottom: 8px; border-bottom: 1px solid #222; padding-bottom: 5px; }
    .news-link { color: #FF4B4B; text-decoration: none; }
    </style>
    """, unsafe_allow_html=True)

st_autorefresh(interval=60000, key="auto_refresh")

# --- [4. 사이드바 (원본 메뉴 + RSS)] ---
with st.sidebar:
    st.header("모니터링 설정")
    stock_dict = {
        "삼성전자 (Samsung)": {"id": "005930", "y": "005930.KS"},
        "현대자동차 (Hyundai)": {"id": "005380", "y": "005380.KS"},
        "알파벳(구글) (GOOG)": {"id": "GOOG", "y": "GOOG"},
        "맥도날드 (MCD)": {"id": "MCD", "y": "MCD"},
        "넷플릭스(NFLX)": {"id": "NFLX", "y": "NFLX"},
        "SK 하이닉스 (Hynix)": {"id": "000660", "y": "000660.KS"},
        "LG전자(LEC)": {"id": "066570", "y": "066570.KS"},
        "엔비디아 (NVDA)": {"id": "NVDA", "y": "NVDA"}
    }
    selected_names = st.multiselect("종목 선택", list(stock_dict.keys()), default=["엔비디아 (NVDA)", "삼성전자 (Samsung)"])
    
st.divider()
    st.subheader("📰 실시간 주요 뉴스")
    
    with st.spinner('뉴스를 불러오는 중...'):
        news_list = get_stock_news(6)
        
    if news_list:
        for news in news_list:
            # 뉴스 제목이 너무 길면 잘라주는 센스!
            display_title = news["title"][:30] + "..." if len(news["title"]) > 30 else news["title"]
            st.markdown(f'<div class="news-item">· <a class="news-link" href="{news["link"]}" target="_blank" title="{news["title"]}">{display_title}</a></div>', unsafe_allow_html=True)
    else:
        st.info("현재 뉴스를 가져올 수 없습니다. 잠시 후 다시 시도해주세요.")

# --- [5. 메인 화면 (레이아웃 완벽 복구)] ---
st.markdown('<p class="main-title">주식 추세 일람 그래프</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">𝕽𝖊𝖆𝖑-𝖙𝖎𝖒𝖊 𝕱𝖎𝖓𝖆𝖓𝖈𝖎𝖆𝖑 𝕸𝖔𝖓𝖎𝖙𝖔𝖗𝖎𝖓𝖌 𝕾𝖞𝖘𝖙𝖊𝖒</p>', unsafe_allow_html=True)

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
            # 데이터 엔진 선택 (국내주: 네이버 / 해외주: yf)
            if info["id"].isdigit():
                data_api = get_naver_stock(info["id"])
                if data_api:
                    st.metric(label=name, value=f"{data_api['curr']:,}원", delta=f"{data_api['perc']:+.2f}%")
            else:
                data_api = yf.Ticker(info["y"]).history(period="1d")
                if not data_api.empty:
                    curr = data_api['Close'].iloc[-1]
                    prev = data_api['Open'].iloc[0]
                    perc = (curr - prev) / prev * 100
                    st.metric(label=name, value=f"${curr:,.2f}", delta=f"{perc:+.2f}%")

            # 그래프 디자인 (드라마틱 풀 스팬 차트)
            df = yf.Ticker(info["y"]).history(period="1d", interval="1m")
            if not df.empty:
                diff = df['Close'].iloc[-1] - df['Open'].iloc[0]
                m_color = "#FF4B4B" if diff >= 0 else "#0072ff"
                fig = go.Figure(go.Scatter(x=df.index, y=df['Close'], fill='tozeroy', mode='lines', line=dict(width=4, color=m_color)))
                fig.update_layout(margin=dict(l=0,r=0,t=10,b=0), height=300, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#333', side="right"))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

st.divider()
m_col1, m_col2 = st.columns([4, 1])
with m_col1: st.text_area("메모장", placeholder="텍스트 입력..", height=120)
with m_col2: 
    st.write("") 
    st.write("") 
    if st.button("새로고침🔄", use_container_width=True): st.rerun()
        
