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
    # 서버 환경에서 크롬 위치 강제 지정
    options.binary_location = "/usr/bin/chromium" 
    
    try:
        # 드라이버 경로 자동 설정 (Service 부분 수정)
        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.get("https://www.soopeh.com/login")
        time.sleep(5)
        
        # ... (이하 아이디/비번 입력 로직 동일) ...
        driver.find_element(By.ID, "login-identifier").send_keys("yd60106")
        pw_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        pw_field.send_keys("koreaCHY1488@!") 
        pw_field.send_keys(Keys.ENTER)
        
        time.sleep(8)
        cookies = driver.get_cookies()
        driver.quit()
        
        if cookies:
            return "; ".join([f"{c['name']}={c['value']}" for c in cookies])
    except Exception as e:
        st.error(f"서버 로그인 엔진 오류: {e}")
        return None

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
