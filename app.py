import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from streamlit_autorefresh import st_autorefresh

# --- [자동 토큰 갱신 시스템] ---
def refresh_soopeh_token():
    """토큰이 죽으면 몰래 브라우저를 띄워 다시 로그인합니다."""
    options = Options()
    options.add_argument("--headless") # 창 안 띄움
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://www.soopeh.com/login")
        time.sleep(3)
        
        # 관심술사가 예측한 그 ID들!
        driver.find_element(By.ID, "login-identifier").send_keys("yd60106")
        # 혹시 ID가 다를 경우를 대비해 type='password'로 한 번 더 체크
        try:
            pw_field = driver.find_element(By.ID, "login-password")
        except:
            pw_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            
        pw_field.send_keys("koreaCHY1488@!") # <--- 찬후님 비번!
        pw_field.submit() # 엔터 효과
        
        time.sleep(5) # 로그인 로딩
        
        cookies = driver.get_cookies()
        driver.quit()
        
        # 새 쿠키 문자열 조립
        new_cookie = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
        return new_cookie
    except Exception as e:
        return None

def get_soopeh_nvda():
    """수페 API 호출 (실패 시 자동 갱신)"""
    if 'soopeh_cookie' not in st.session_state:
        st.session_state.soopeh_cookie = "기본_쿠키_값" # 처음엔 아까 찾은 거 넣어도 됨
        
    url = "https://api.soopeh.com/economy/stocks/quotes?symbols=NVDA"
    headers = {
        "cookie": st.session_state.soopeh_cookie,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=5)
        # 토큰 만료(401/403) 시 자동 갱신 실행
        if res.status_code != 200:
            new_c = refresh_soopeh_token()
            if new_c:
                st.session_state.soopeh_cookie = new_c
                headers["cookie"] = new_c
                res = requests.get(url, headers=headers, timeout=5)
        
        if res.status_code == 200:
            data = res.json()[0]
            return {'curr': data.get('price', 0), 'perc': data.get('changeRate', 0)}
    except:
        pass
    return None
# --- 1. 페이지 설정 및 디자인 (CSS) - 찬후님 원본 100% 동일 ---
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

# --- 2. 사이드바 (설정 메뉴) - 찬후님 원본 100% 동일 ---
with st.sidebar:
    st.header("모니터링 설정")
    stock_dict = {
        "삼성전자 (Samsung)": {"id": "005930", "type": "KR", "y": "005930.KS"},
        "현대자동차 (Hyundai)": {"id": "005380", "type": "KR", "y": "005380.KS"},
        "알파벳(구글) (GOOG)": {"id": "GOOG", "type": "US", "y": "GOOG"},
        "맥도날드 (MCD)": {"id": "MCD", "type": "US", "y": "MCD"},
        "넷플릭스(NFLX)": {"id": "NFLX", "type": "US", "y": "NFLX"},
        "SK 하이닉스 (Hynix)": {"id": "000660", "type": "KR", "y": "000660.KS"},
        "LG전자(LEC)": {"id": "066570", "type": "KR", "y": "066570.KS"},
        "엔비디아 (NVDA)": {"id": "NVDA", "type": "US", "y": "NVDA"} # 타입 US 유지하되 로직에서 분기
    }
    selected_names = st.multiselect("종목 선택", list(stock_dict.keys()), default=["엔비디아 (NVDA)", "삼성전자 (Samsung)"])
    period_map = {"1주일": "7d", "1개월": "1mo", "3개월": "3mo", "1년": "1y"}
    selected_period = st.selectbox("모니터링 기간", list(period_map.keys()), index=0)
    
    st.divider()
    if st.button("새로고침 (수동)", use_container_width=True):
        st.rerun()

# --- 3. 메인 화면 ---
# [완벽 복사] 타이틀 및 캡션
st.markdown('<p class="main-title">주식 추세 일람 그래프</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">𝕽𝖊𝖆𝖑-𝖙𝖎𝖒𝖊 𝕱𝖎𝖓𝖆𝖓𝖈𝖎𝖆𝖑 𝕸𝖔𝖓𝖎𝖙𝖔𝖗𝖎𝖓𝖌 𝕾𝖞𝖘𝖙𝖊𝖒</p>', unsafe_allow_html=True)

# [완벽 복사] 검색창 섹션
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

# [로직 통합] 종목 카드 및 그래프 레이아웃
if selected_names:
    cols = st.columns(len(selected_names))
    for i, name in enumerate(selected_names):
        info = stock_dict[name]
        
        with cols[i]:
            # [조건부 로직] 엔비디아(NVDA)면 수페 API 호출, 아니면 yfinance 호출
            if info["id"] == "NVDA":
                soopeh_data = get_soopeh_nvda()
                if soopeh_data:
                    curr = soopeh_data['curr']
                    perc = soopeh_data['perc']
                    # 수페는 실시간 데이터이므로 그래프용 과거 데이터는 yfinance에서 빌려옴
                    ticker_obj = yf.Ticker("NVDA")
                    data = ticker_obj.history(period="1d", interval="1m")
                    # yfinance로 계산한 시가 대비 변동률 (원본 디자인 유지용)
                    if not data.empty:
                        prev_open = data['Open'].iloc[0]
                        perc_yfin = (curr - prev_open) / prev_open * 100
                    
                    # [완벽 복사] 상단 메트릭 (원본 이름 유지)
                    st.metric(label=name, value=f"${curr:,.2f}", delta=f"{perc:+.2f}%")
                else:
                    st.error("수페 토큰 만료!")
                    st.info("토큰을 갱신해주세요.")
                    data = pd.DataFrame()
            else:
                ticker_obj = yf.Ticker(info["y"])
                data = ticker_obj.history(period="1d", interval="1m")
                if not data.empty:
                    curr = data['Close'].iloc[-1]
                    prev = data['Open'].iloc[0]
                    perc = (curr - prev) / prev * 100
                    # [완벽 복사] 상단 메트릭
                    st.metric(label=name, value=f"{curr:,.2f}", delta=f"{perc:+.2f}%")

            # [완벽 복사] 드라마틱 풀 스팬 차트 생성 (디자인 동일)
            if not data.empty:
                diff = data['Close'].iloc[-1] - data['Open'].iloc[0]
                m_color = "#FF4B4B" if diff >= 0 else "#0072ff"
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=data.index, y=data['Close'],
                    fill='tozeroy', mode='lines',
                    line=dict(width=4, color=m_color),
                    fillcolor=f'rgba({255 if diff >= 0 else 0}, 75, 255, 0.1)'
                ))

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
                
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.error(f"{name} 데이터를 찾을 수 없습니다. 다시 시도해 주세요.")

st.divider()
# [완벽 복사] 메모장 섹션
m_col1, m_col2 = st.columns([4, 1])
with m_col1:
    st.text_area("메모장", placeholder="텍스트 입력..", height=120)
with m_col2:
    st.write("") 
    st.write("") 
    if st.button("새로고침🔄", use_container_width=True):
        st.rerun()
