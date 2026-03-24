import plotly.graph_objects as go
import streamlit as st
import yfinance as yf # 그래프용 과거 데이터는 yfinance를 쓰되, 현재가는 수페만 씁니다.
import pandas as pd
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from streamlit_autorefresh import st_autorefresh

# --- [1. 자동 토큰 갱신 시스템] ---
def refresh_soopeh_token():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://www.soopeh.com/login")
        time.sleep(3)
        
        driver.find_element(By.ID, "login-identifier").send_keys("yd60106")
        pw_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        
        # ★ 찬후님 비밀번호 입력 ★
        pw_field.send_keys("koreaCHY1488@!") 
        pw_field.send_keys(Keys.ENTER)
        
        time.sleep(7) 
        cookies = driver.get_cookies()
        driver.quit()
        
        if cookies:
            new_cookie = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
            return new_cookie
    except Exception as e:
        st.error(f"⚠️ 로그인 엔진 오류: {e}")
        return None

# --- [2. 수페 API 전용 호출 함수] ---
def get_soopeh_only_nvda():
    """yfinance 백업 없이 오직 수페 API 데이터만 가져옵니다."""
    if 'soopeh_cookie' not in st.session_state:
        # 찬후님이 처음 알려주신 그 쿠키값
        st.session_state.soopeh_cookie = "_ga=GA1.1.836760262.1774343435; soopeh_auth=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0ZmY0MjNmNS1iY2JlLTQzYWMtODFmNy1jOWUwYzg1YjdlMmUiLCJlbWFpbCI6bnVsbCwibG9naW5JZCI6InlkNjAxMDYiLCJuaWNrbmFtZSI6IuycoOywrO2bhCIsInR5cCI6IkpXVCJ9..."

    url = "https://api.soopeh.com/economy/stocks/quotes?symbols=NVDA"
    headers = {
        "cookie": st.session_state.soopeh_cookie,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "referer": "https://www.soopeh.com/",
        "origin": "https://www.soopeh.com"
    }

    res = requests.get(url, headers=headers, timeout=5)
    
    # 토큰 만료 시 자동 갱신 시도
    if res.status_code != 200:
        with st.spinner('🔄 토큰 만료됨! 자동 로그인 중...'):
            new_c = refresh_soopeh_token()
            if new_c:
                st.session_state.soopeh_cookie = new_c
                headers["cookie"] = new_c
                res = requests.get(url, headers=headers, timeout=5)
            else:
                return "LOGIN_FAILED"

    if res.status_code == 200:
        data = res.json()
        if data and len(data) > 0:
            return {'curr': data[0].get('price', 0), 'perc': data[0].get('changeRate', 0)}
    
    return "API_ERROR"

# --- [3. 디자인 및 레이아웃 (찬후님 원본)] ---
st.set_page_config(page_title="수페 API 실시간 모니터링", page_icon="📈", layout="wide")

# CSS 생략 (찬후님 원본 그대로 사용하세요)
st_autorefresh(interval=30000, key="auto_refresh_key")

with st.sidebar:
    st.header("모니터링 설정")
    selected_names = st.multiselect("종목 선택", ["엔비디아 (NVDA)"], default=["엔비디아 (NVDA)"])
    if st.button("새로고침 (수동)", use_container_width=True):
        st.rerun()

st.markdown('<p class="main-title">주식 추세 일람 그래프</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">𝕾𝖔𝖔𝖕𝖊𝖍 𝕬𝕻𝕴 𝕯𝖎𝖗𝖊𝖈𝖙 𝕮𝖔𝖓𝖓𝖊𝖈𝖙𝖎𝖔𝖓</p>', unsafe_allow_html=True)

if selected_names:
    cols = st.columns(len(selected_names))
    for i, name in enumerate(selected_names):
        with cols[i]:
            # --- 수페 데이터만 출력 ---
            result = get_soopeh_only_nvda()
            
            if isinstance(result, dict):
                st.metric(label=f"{name} (Soopeh Live)", value=f"${result['curr']:,.2f}", delta=f"{result['perc']:+.2f}%")
                
                # 그래프는 흐름을 보기 위해 yfinance에서 1분봉 데이터를 빌려오되, 현재가는 수페를 따름
                data = yf.Ticker("NVDA").history(period="1d", interval="1m")
                if not data.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], fill='tozeroy', mode='lines', line=dict(color="#FF4B4B", width=4)))
                    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            elif result == "LOGIN_FAILED":
                st.error("❌ 수페 자동 로그인 실패! 비밀번호를 확인하세요.")
            else:
                st.error("❌ 수페 API 응답 없음 (서버 점검 중일 수 있음)")

st.divider()
st.text_area("메모장", placeholder="수페 API 연동 테스트 중..", height=120)
