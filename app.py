import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from streamlit_autorefresh import st_autorefresh

# --- 1. 페이지 설정 및 디자인 (CSS) ---
st.set_page_config(page_title="국내-해외 주식 현황 모니터링", page_icon="📈", layout="wide")

st.markdown("""
   <style>
    /* 폰트 설정 (Pretendard) */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', sans-serif; }
    
    /* 메인 타이틀 스타일 */
    .main-title { 
        font-size: 40px !important; 
        font-weight: 800; 
        color: #FFFFFF; 
        text-align: center; 
        margin-bottom: 5px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .sub-title { font-size: 18px; color: #888888; text-align: center; font-style: italic; margin-bottom: 30px; }

    /* ★ 버튼 애니메이션 & 그라데이션 그림자 (Red-Purple 테마) ★ */
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        border: none;
        padding: 12px 20px;
        /* 빨강 -> 보라 그라데이션 */
        background: linear-gradient(135deg, #FF4B4B 0%, #764BA2 100%); 
        color: white !important;
        font-weight: 700;
        font-size: 16px;
        /* 은은한 보라색 그림자 */
        box-shadow: 0 4px 15px rgba(118, 75, 162, 0.4); 
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
    }

    /* 마우스 올렸을 때 (Hover) */
    div.stButton > button:hover {
        transform: translateY(-3px) scale(1.02); /* 살짝 떠오름 */
        /* 그림자 더 진해짐 (네온 광채) */
        box-shadow: 0 8px 25px rgba(118, 75, 162, 0.6); 
        /* 더 밝은 빨강-보라 그라데이션 */
        background: linear-gradient(135deg, #FF6B6B 0%, #8A54C9 100%); 
    }

    /* 클릭했을 때 (Active) - 쑥 들어가는 효과 */
    div.stButton > button:active {
        transform: translateY(1px) scale(0.95); /* 눌림 효과 */
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        transition: all 0.1s;
    }

    /* 종목 카드 스타일 개선 */
    [data-testid="stMetric"] {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 15px;
        box-shadow: inset 0 0 10px rgba(255,255,255,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 30초 자동 새로고침 설정
st_autorefresh(interval=30000, key="auto_refresh_key")

# --- 2. 강화된 데이터 크롤링 함수 ---
def get_korean_stock_price(ticker):
    try:
        # 네이버 금융 크롤링 (User-Agent 헤더 추가로 차단 방지)
        url = f"https://finance.naver.com/item/main.naver?code={ticker}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
        res = requests.get(url, headers=headers, timeout=10)
        
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            # 가격 추출 경로 보강
            price_tag = soup.select_one(".no_today .blind")
            if price_tag:
                curr = int(price_tag.text.replace(',', ''))
                exday = soup.select_one(".no_exday .blind")
                # 전일비 계산
                diff_tag = soup.select_one(".no_exday .ico")
                diff_val = int(exday.find_all("span")[0].text.replace(',', '')) if exday else 0
                
                # 상승/하락 여부에 따른 전일가 계산
                if diff_tag and 'up' in diff_tag.get('class', []):
                    prev = curr - diff_val
                elif diff_tag and 'down' in diff_tag.get('class', []):
                    prev = curr + diff_val
                else:
                    prev = curr
                return curr, prev
        
        # 네이버 실패 시 yfinance로 2차 시도 (안전장치)
        yticker = yf.Ticker(f"{ticker}.KS")
        hist = yticker.history(period="2d")
        if not hist.empty:
            return int(hist['Close'].iloc[-1]), int(hist['Close'].iloc[-2])
            
    except Exception as e:
        print(f"Error: {e}")
    return None, None

# --- 3. 사이드바 (설정 메뉴) ---
with st.sidebar:
    st.header("모니터링 설정")
    stock_dict = {
        "삼성전자 (Samsung)": {"id": "005930", "type": "KR", "y": "005930.KS"},
        "현대자동차 (Hyundai)": {"id": "005380", "type": "KR", "y": "005380.KS"},
        "알파벳(구글) (GOOG)": {"id": "GOOG", "type": "US", "y": "GOOG"},
        "맥도날드 (MCD)": {"id": "MCD", "type": "US", "y": "MCD"},
        "넷플릭스(NFLX)": {"id": "NFLX", "type": "US", "y": "NFLX"},
        "SK 하이닉스 (Hynix)": {"id": "000660", "type": "KR", "y": "000660.KS"}
        "LG전자(LEC)": {"id": "066570", "type": "KR", "y": "066570.KS"}
       
    }
    selected_names = st.multiselect("종목 선택", list(stock_dict.keys()))
    period_map = {"1주일": "7d", "1개월": "1mo", "3개월": "3mo", "1년": "1y"}
    selected_period = st.selectbox("모니터링 기간", list(period_map.keys()), index=0)
    
    st.divider()
    if st.button("새로고침 (수동)", use_container_width=True):
        st.rerun()

# --- 4. 메인 화면 --- (이 아래부터 끝까지 덮어쓰세요)
st.markdown('<p class="main-title">주식 추세 일람 그래프</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">𝕽𝖊𝖆𝖑-𝖙𝖎𝖒𝖊 𝕱𝖎𝖓𝖆𝖓𝖈𝖎𝖆𝖑 𝕸𝖔𝖓𝖎𝖙𝖔𝖗𝖎𝖓𝖌 𝕾𝖞𝖘𝖙𝖊𝖒</p>', unsafe_allow_html=True)

# 검색창 섹션
search_q = st.text_input("", placeholder="알아보고 싶은 종목명을 입력해주세요.")
if search_q:
    refined_q = f"{search_q} 주가"
    s_col1, s_col2, s_col3 = st.columns(3)
    with s_col1:
        st.link_button("🌐 Google", f"https://www.google.com/search?q={refined_q}", use_container_width=True)
    with s_col2:
        st.link_button("네이버", f"https://search.naver.com/search.naver?query={refined_q}", use_container_width=True)
    with s_col3:
        st.link_button("다음", f"https://search.daum.net/search?q={refined_q}", use_container_width=True)

st.divider()

# 종목 카드 및 그래프 레이아웃
if selected_names:
    cols = st.columns(len(selected_names))
    for i, name in enumerate(selected_names):
        # 1. 종목 정보 가져오기 (사이드바 stock_dict 기준)
        info = stock_dict[name]
        ticker_symbol = info["y"] # yfinance용 티커 (예: 005930.KS)
        
        with cols[i]:
            # 2. yfinance로 당일 1분 단위 데이터 호출
            ticker_obj = yf.Ticker(ticker_symbol)
            # '1d' 기간을 '1m' 간격으로 가져와야 이미지처럼 촘촘한 그래프가 나옵니다.
            data = ticker_obj.history(period="1d", interval="1m")
            
            if not data.empty:
                curr = data['Close'].iloc[-1]
                prev = data['Open'].iloc[0] # 당일 시가 대비 변화 확인
                diff = curr - prev
                perc = (diff / prev * 100)
                
                # 상단 메트릭 (상승 시 빨강, 하락 시 파랑)
                st.metric(label=name, value=f"{curr:,.2f}", delta=f"{perc:+.2f}%")

                # 3. 드라마틱 풀 스팬 차트 생성
                m_color = "#FF4B4B" if diff >= 0 else "#0072ff"
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=data.index, y=data['Close'],
                    fill='tozeroy', mode='lines',
                    line=dict(width=4, color=m_color),
                    # 아래쪽은 은은한 그라데이션 느낌으로 채움
                    fillcolor=f'rgba({255 if diff >= 0 else 0}, 75, 255, 0.1)'
                ))

                # 4. 이미지처럼 폭을 넓게 고정 (장 시작부터 + 6.5시간)
                start_dt = data.index[0]
                end_dt = start_dt + pd.Timedelta(hours=6.5) 
                
                fig.update_layout(
                    margin=dict(l=0, r=0, t=10, b=0), height=300,
                    template="plotly_dark", 
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(range=[start_dt, end_dt], showgrid=False, type='date'),
                    yaxis=dict(showgrid=True, gridcolor='#333', side="right"),
                    hovermode="x unified"
                )
                
                # 5. 차트 출력 (config로 우측 상단 툴바 숨김)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.error(f"{name} 데이터를 찾을 수 없습니다. 다시 시도해 주세요.")

st.divider()
m_col1, m_col2 = st.columns([4, 1])
with m_col1:
    st.text_area("메모장", placeholder="텍스트 입력..", height=120)
with m_col2:
    st.write("") 
    st.write("") 
    if st.button("새로고침🔄", use_container_width=True):
        st.rerun()
