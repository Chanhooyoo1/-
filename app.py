import streamlit as st
import requests
import yfinance as yf
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- [1. 수페 로그인 & 쿠키 획득 함수 (No Selenium 방식)] ---
def login_to_soopeh(user_id, user_pw):
    """더 강력한 '사람 흉내' 헤더를 추가한 로그인 함수"""
    login_url = "https://www.soopeh.com/api/auth/login" # 실제 API 주소로 정밀 조정
    
    # 서버를 속이기 위한 '진짜 브라우저' 정보
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "content-type": "application/json",
        "origin": "https://www.soopeh.com",
        "referer": "https://www.soopeh.com/login",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    # 수페가 사용하는 정확한 데이터 필드명 (identifier vs username)
    payload = {
        "identifier": user_id, 
        "password": user_pw
    }
    
    try:
        # 세션을 유지하며 로그인 시도
        session = requests.Session()
        response = session.post(login_url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # 로그인 성공 시 모든 쿠키를 싹 긁어옴
            all_cookies = session.cookies.get_dict()
            cookie_str = "; ".join([f"{k}={v}" for k, v in all_cookies.items()])
            return cookie_str
        else:
            # 실패 시 서버가 보낸 에러 메시지를 터미널에 출력 (디버깅용)
            print(f"로그인 실패 원인: {response.text}")
            return None
    except Exception as e:
        print(f"네트워크 오류: {e}")
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
