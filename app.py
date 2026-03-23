import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from streamlit_autorefresh import st_autorefresh

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="주가분석 일람 시스템", page_icon="📈", layout="wide")

# --- 2. 30초 자동 새로고침 ---
st_autorefresh(interval=30000, key="stock_refresh")

# --- 3. 데이터 로직 ---
def get_korean_stock_price(ticker):
    try:
        url = f"https://finance.naver.com/item/main.naver?code={ticker}"
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        price = int(soup.select_one(".no_today .blind").text.replace(',', ''))
        exday = soup.select_one(".no_exday .blind")
        yesterday = int(exday.find_all("span")[0].text.replace(',', '')) if exday else price
        return price, yesterday
    except: return None, None

# --- 4. 사이드바 설정 ---
with st.sidebar:
    st.header("⚙️ 모니터링 설정")
    stock_dict = {
        "삼성전자": {"id": "005930", "type": "KR", "y": "005930.KS"},
        "현대자동차": {"id": "005380", "type": "KR", "y": "005380.KS"},
        "알파벳(구글)": {"id": "GOOG", "type": "US", "y": "GOOG"},
        "맥도날드": {"id": "MCD", "type": "US", "y": "MCD"},
        "테슬라": {"id": "TSLA", "type": "US", "y": "TSLA"}
    }
    selected_names = st.multiselect("종목 선택", list(stock_dict.keys()), default=["삼성전자", "알파벳(구글)"])
    period_map = {"1일": "1d", "1주일": "7d", "1개월": "1mo", "3개월": "3mo", "1년": "1y"}
    selected_period = st.selectbox("조회 기간", list(period_map.keys()), index=1)

# --- 5. 메인 화면 ---
st.title("📈 실시간 주가분석 시스템")
st.caption(f"🕒 마지막 업데이트: {datetime.now().strftime('%H:%M:%S')} (30초마다 자동 갱신)")

if selected_names:
    cols = st.columns(len(selected_names))
    for i, name in enumerate(selected_names):
        info = stock_dict[name]
        with cols[i]:
            if info["type"] == "KR":
                curr, prev = get_korean_stock_price(info["id"])
            else:
                ticker_obj = yf.Ticker(info["id"])
                hist2d = ticker_obj.history(period="2d")
                curr = round(hist2d['Close'].iloc[-1], 2) if not hist2d.empty else None
                prev = round(hist2d['Close'].iloc[-2], 2) if len(hist2d) > 1 else curr
            
            if curr:
                st.metric(label=name, value=f"{curr:,.2f}", delta=f"{(curr-prev)/prev*100:+.2f}%")
                # 그래프 출력
                chart_data = yf.Ticker(info["y"]).history(period=period_map[selected_period])
                st.area_chart(chart_data['Close'])

st.text_area("📝 투자 메모장", placeholder="전략을 기록하세요.")
