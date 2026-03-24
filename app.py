import streamlit as st
import requests
import yfinance as yf
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- [1. 수페 로그인 & 쿠키 획득 함수 (No Selenium 방식)] ---
def login_to_soopeh(user_id, user_pw):
    """Selenium 없이 HTTP 요청만으로 로그인을 시도합니다."""
    login_url = "https://api.soopeh.com/auth/login" # 수페 실제 로그인 API 주소 (확인 필요)
    payload = {
        "identifier": user_id,
        "password": user_pw
    }
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
        "content-type": "application/json"
    }
    
    try:
        response = requests.post(login_url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            # 로그인 성공 시 서버가 주는 쿠키를 세션에 저장
            cookies = response.cookies.get_dict()
            cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
            return cookie_str
        return None
    except:
        return None

# --- [2. 메인 UI 설정] ---
st.set_page_config(page_title="수페 실시간 모니터링", layout="wide")
st_autorefresh(interval=30000, key="auto_refresh")

# --- [3. 사이드바: 로그인 섹션] ---
with st.sidebar:
    st.header("🔑 수페 계정 설정")
    # 찬후님의 아이디를 기본값으로 세팅
    u_id = st.text_input("아이디", value="yd60106")
    u_pw = st.text_input("비밀번호", type="password") # 여기에 비밀번호를 치면 됩니다!
    
    if st.button("수페 로그인 및 연결", use_container_width=True):
        with st.spinner("수페 서버 연결 중..."):
            new_cookie = login_to_soopeh(u_id, u_pw)
            if new_cookie:
                st.session_state.soopeh_cookie = new_cookie
                st.success("✅ 로그인 성공!")
            else:
                st.error("❌ 로그인 실패 (아이디/비번 확인)")

# --- [4. 데이터 출력 로직] ---
st.title("📈 NVDA 실시간 수페 API")

# 로그인 정보가 있을 때만 실행
if 'soopeh_cookie' in st.session_state:
    url = "https://api.soopeh.com/economy/stocks/quotes?symbols=NVDA"
    headers = {"cookie": st.session_state.soopeh_cookie}
    
    res = requests.get(url, headers=headers)
    
    if res.status_code == 200:
        data = res.json()[0]
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric(label="NVIDIA Live", value=f"${data['price']}", delta=f"{data['changeRate']}%")
        with col2:
            # 그래프는 yfinance 빌려쓰기
            df = yf.Ticker("NVDA").history(period="1d", interval="1m")
            fig = go.Figure(go.Scatter(x=df.index, y=df['Close']))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ 토큰이 만료되었습니다. 다시 로그인해주세요.")
else:
    st.info("👈 왼쪽 사이드바에서 수페 로그인을 먼저 진행해주세요!")
