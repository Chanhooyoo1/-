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

# --- [2. RSS 뉴스 가져오기] ---
def get_stock_news(limit=6):
    rss_url = "https://www.mk.co.kr/rss/30200001/" # 매일경제 증권 RSS
    try:
        feed = feedparser.parse(rss_url)
        if not feed.entries:
            return []
        return [{"title": entry.title, "link": entry.link} for entry in feed.entries[:limit]]
    except:
        return []

# --- [3. 페이지 설정 및 디자인 (CSS)] ---
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

    /* 찬후님 전용 빨강-보라 그라데이션 버튼 */
    div.stButton > button {
        width: 100%; border-radius: 12px; border: none; padding: 12px 20px;
        background: linear-gradient(135deg, #FF4B4B 0%, #764BA2 100%); 
        color: white !important; font-weight: 700; font-size: 16px;
        box-shadow: 0 4px 15px rgba(118, 75, 162, 0.4); 
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); cursor: pointer;
    }
    div.stButton > button:hover { 
        transform: translateY(-3px) scale(1.02); 
        box-shadow: 0
