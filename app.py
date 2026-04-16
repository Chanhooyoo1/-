import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import feedparser
from streamlit_autorefresh import st_autorefresh
/* =========================================================
   통합 오버라이드
   - MeBox 220 / UserList 연동 / RoomList 790 / Chat 790
   - 메뉴 버튼 스타일/호버 유지
   - 나머지 버튼: 빨강-보라 그라데이션 + 호버
   - 개별 창 네온 제거
   - 전체 외곽 둥근 직사각형 펄스 네온
   ========================================================= */

:root{
	--neon-pink: rgba(255, 51, 102, 0.55);
	--neon-purple: rgba(153, 51, 255, 0.45);
	--btn-grad: linear-gradient(135deg, #ff3366, #9933ff);
}

/* 1) 요청한 레이아웃 */
.MeBox{
	width: 220px !important;
}
.UserListBox{
	width: 220px !important;
}
.UserListBox .product-body,
.users-item{
	width: 210px !important;
}
.RoomListBox{
	width: 790px !important;
}
.RoomListBox .product-body{
	width: 780px !important;
	height: 330px !important; /* 기존 height: px 오류 보정 */
}
.ChatBox{
	width: 790px !important;
}
#Talk{
	width: calc(100% - 50px) !important;
	height: 25px !important;
}
#ChatBtn{
	width: 50px !important;
	height: 25px !important;
}

/* 2) 모든 버튼 공통 (메뉴 버튼은 아래에서 원복) */
button,
input[type="button"],
input[type="submit"],
input[type="reset"]{
	background: var(--btn-grad) !important;
	color: #fff !important;
	border: none !important;
	transition: all .25s ease !important;
	box-shadow:
		0 0 10px rgba(255,51,102,.35),
		0 0 16px rgba(153,51,255,.25);
}
button:hover,
input[type="button"]:hover,
input[type="submit"]:hover,
input[type="reset"]:hover{
	filter: brightness(1.12);
	transform: translateY(-1px);
	box-shadow:
		0 0 14px rgba(255,51,102,.45),
		0 0 24px rgba(153,51,255,.35);
}

/* 3) 메뉴 버튼은 기존 스타일/호버 유지 */
#Top .menu-btn{
	background: transparent !important;
	background-image: none !important;
	color: #000000 !important;
	box-shadow: none !important;
}
#Top .menu-sub-btn{
	color: #111111 !important;
	box-shadow: none !important;
}
.kkutu-menu button{
	background-color: rgba(255, 255, 255, 0.2) !important;
	color: #000 !important;
	box-shadow: none !important;
}
.kkutu-menu button:hover{
	margin-top: -5px !important;
	height: 25px !important;
	background: linear-gradient(to bottom, #ff3366, #9933ff) !important;
	color: #fff !important;
}
.kkutu-menu .toggled{
	margin-top: 5px !important;
	color: #EEEEEE !important;
	background-color: #444444 !important;
}

/* 4) 개별 창 네온 제거 */
.Product,
.dialog,
.UserListBox,
.RoomListBox,
.ShopBox,
.RoomBox,
.GameBox,
.MeBox,
.ChatBox,
.ADBox{
	box-shadow: none !important;
}

/* 5) 전체 외곽 둥근 직사각형 펄스 네온 */
#Wrap, #kkutu-wrap, .kkutu-wrap, #container{
	position: relative;
	overflow: visible !important;
	border-radius: 30px;
}

/* 프레임 */
#Wrap::after,
#kkutu-wrap::after,
.kkutu-wrap::after,
#container::after{
	content: "";
	position: absolute;
	inset: -12px;
	border-radius: 36px;
	border: 2px solid rgba(255, 102, 204, 0.6);
	box-shadow:
		0 0 18px var(--neon-pink),
		0 0 36px var(--neon-purple),
		0 0 56px rgba(153,51,255,.22);
	pointer-events: none;
	z-index: 1;
	animation: OuterNeonPulse 2.2s ease-in-out infinite;
}

@keyframes OuterNeonPulse{
	0%, 100%{
		opacity: .72;
		box-shadow:
			0 0 14px rgba(255,51,102,.35),
			0 0 28px rgba(153,51,255,.28),
			0 0 44px rgba(153,51,255,.16);
	}
	50%{
		opacity: 1;
		box-shadow:
			0 0 22px rgba(255,51,102,.62),
			0 0 42px rgba(153,51,255,.5),
			0 0 70px rgba(153,51,255,.3);
	}
}
/* 기본(인게임 포함): 넓게 */
.ChatBox{
	width: 1000px !important;
}

/* 로비(미박스가 있는 화면)만 축소 */
.MeBox ~ .ChatBox{
	width: 790px !important;
}

/* 인게임(GameBox가 보이는 구간)에서는 다시 확장 */
.GameBox ~ .ChatBox{
	width: 1000px !important;
}

/* 입력칸은 너비 자동 계산 유지 */
#Talk{
	width: calc(100% - 50px) !important;
}
#ChatBtn{
	width: 50px !important;
}
/* 기본: 홈/준비 */
.ChatBox{
	width: 790px !important;
}

/* 게임 박스가 켜진 상태에서 확장 */
.GameBox[style*="display:block"] ~ .ChatBox,
.GameBox[style*="display: block"] ~ .ChatBox,
body.state-playing .ChatBox,
body.game .ChatBox{
	width: 1000px !important;
}

#Talk{ width: calc(100% - 50px) !important; }
#ChatBtn{ width: 50px !important; }
/* =========================================
   버튼 개별 그라데이션 시스템
   대상: Spectate/SetRoom/NewRoom/QuickRoom/Shop/Dictionary/Invite/Practice/Ready/Start/Replay
   ========================================= */

/* 1) 공통 적용 규칙 (각 버튼이 자기 변수 사용) */
#SpactateBtn, #SetRoomBtn, #NewRoomBtn, #QuickRoomBtn, #ShopBtn, #DictionaryBtn,
#InviteBtn, #PracticeBtn, #ReadyBtn, #StartBtn, #ReplayBtn{
  background: var(--btn-grad, linear-gradient(135deg, #ff3366, #9933ff)) !important;
  color: var(--btn-fg, #fff) !important;
  border: 1px solid var(--btn-border, rgba(255,255,255,.18)) !important;
  transition: all .25s ease !important;
  box-shadow: 0 0 8px rgba(255,51,102,.28), 0 0 14px rgba(153,51,255,.22);
}

#SpactateBtn:hover, #SetRoomBtn:hover, #NewRoomBtn:hover, #QuickRoomBtn:hover, #ShopBtn:hover, #DictionaryBtn:hover,
#InviteBtn:hover, #PracticeBtn:hover, #ReadyBtn:hover, #StartBtn:hover, #ReplayBtn:hover{
  background: var(--btn-hover-grad, linear-gradient(135deg, #ff4d7a, #a64dff)) !important;
  color: var(--btn-hover-fg, #fff) !important;
  box-shadow: 0 0 12px rgba(255,51,102,.45), 0 0 22px rgba(153,51,255,.35);
  transform: translateY(-1px);
}

/* 토글/활성 상태 */
#SpactateBtn.toggled, #SetRoomBtn.toggled, #NewRoomBtn.toggled, #QuickRoomBtn.toggled, #ShopBtn.toggled, #DictionaryBtn.toggled,
#InviteBtn.toggled, #PracticeBtn.toggled, #ReadyBtn.toggled, #StartBtn.toggled, #ReplayBtn.toggled,
#SpactateBtn.active, #SetRoomBtn.active, #NewRoomBtn.active, #QuickRoomBtn.active, #ShopBtn.active, #DictionaryBtn.active,
#InviteBtn.active, #PracticeBtn.active, #ReadyBtn.active, #StartBtn.active, #ReplayBtn.active{
  background: var(--btn-active-grad, linear-gradient(135deg, #d12b55, #7f2ed1)) !important;
  color: var(--btn-active-fg, #fff) !important;
}

/* 2) 버튼별 그라데이션 정의 (원하는 색으로 바꾸면 됨) */
#SpactateBtn{
  --btn-grad: linear-gradient(135deg, #3a7bd5, #3a6073);
  --btn-hover-grad: linear-gradient(135deg, #4b8ff0, #4b7f96);
  --btn-active-grad: linear-gradient(135deg, #2e62aa, #304f5e);
}
#SetRoomBtn{
  --btn-grad: linear-gradient(135deg, #ff5f6d, #ffc371);
  --btn-hover-grad: linear-gradient(135deg, #ff7380, #ffd18d);
  --btn-active-grad: linear-gradient(135deg, #e14b59, #e0ab5f);
}
#NewRoomBtn{
  --btn-grad: linear-gradient(135deg, #11998e, #38ef7d);
  --btn-hover-grad: linear-gradient(135deg, #17b3a6, #51ff98);
  --btn-active-grad: linear-gradient(135deg, #0e7f76, #2fc967);
}
#QuickRoomBtn{
  --btn-grad: linear-gradient(135deg, #fc466b, #3f5efb);
  --btn-hover-grad: linear-gradient(135deg, #ff5b7f, #5571ff);
  --btn-active-grad: linear-gradient(135deg, #d83a5a, #344ed4);
}
#ShopBtn{
  --btn-grad: linear-gradient(135deg, #f7971e, #ffd200);
  --btn-hover-grad: linear-gradient(135deg, #ffab3d, #ffe14f);
  --btn-active-grad: linear-gradient(135deg, #d38218, #d9b300);
}
#DictionaryBtn{
  --btn-grad: linear-gradient(135deg, #8e2de2, #4a00e0);
  --btn-hover-grad: linear-gradient(135deg, #a045f0, #6330ff);
  --btn-active-grad: linear-gradient(135deg, #7423bb, #3e00bb);
}
#InviteBtn{
  --btn-grad: linear-gradient(135deg, #00c6ff, #0072ff);
  --btn-hover-grad: linear-gradient(135deg, #27d4ff, #2c87ff);
  --btn-active-grad: linear-gradient(135deg, #00a7d9, #0060d6);
}
#PracticeBtn{
  --btn-grad: linear-gradient(135deg, #56ab2f, #a8e063);
  --btn-hover-grad: linear-gradient(135deg, #68bf3d, #b9ee78);
  --btn-active-grad: linear-gradient(135deg, #4a9628, #93c957);
}
#ReadyBtn{
  --btn-grad: linear-gradient(135deg, #ff3366, #9933ff);
  --btn-hover-grad: linear-gradient(135deg, #ff4d7a, #ad4dff);
  --btn-active-grad: linear-gradient(135deg, #d62a55, #7f2bd1);
}
#StartBtn{
  --btn-grad: linear-gradient(135deg, #ff512f, #dd2476);
  --btn-hover-grad: linear-gradient(135deg, #ff6c4c, #f03c8d);
  --btn-active-grad: linear-gradient(135deg, #d9472a, #bc1f63);
}
#ReplayBtn{
  --btn-grad: linear-gradient(135deg, #1d976c, #93f9b9);
  --btn-hover-grad: linear-gradient(135deg, #24b080, #a9ffd0);
  --btn-active-grad: linear-gradient(135deg, #187c58, #7ed6a0);
}

/* =========================================
   부모 -> 자식 트랜지션 상속 시스템
   ========================================= */

/* 1) 전역 기본값(부모) */
:root{
  --ui-transition: all .25s ease;
  --ui-hover-transform: translateY(-1px);
  --ui-hover-filter: brightness(1.12);
}

/* 2) 부모 컨테이너별 오버라이드 가능
   예: 게임방에서만 더 느리게 */
#Wrap{
  --ui-transition: all .35s cubic-bezier(.22,.61,.36,1);
}
.GameBox{
  --ui-transition: all .18s ease-out;
}

/* 3) 대상 버튼들: 부모 변수 사용 */
#SpactateBtn, #SetRoomBtn, #NewRoomBtn, #QuickRoomBtn, #ShopBtn, #DictionaryBtn,
#InviteBtn, #PracticeBtn, #ReadyBtn, #StartBtn, #ReplayBtn{
  transition: var(--btn-transition, var(--ui-transition)) !important;
}

/* 4) hover도 부모 변수 사용 */
#SpactateBtn:hover, #SetRoomBtn:hover, #NewRoomBtn:hover, #QuickRoomBtn:hover, #ShopBtn:hover, #DictionaryBtn:hover,
#InviteBtn:hover, #PracticeBtn:hover, #ReadyBtn:hover, #StartBtn:hover, #ReplayBtn:hover{
  transform: var(--btn-hover-transform, var(--ui-hover-transform));
  filter: var(--btn-hover-filter, var(--ui-hover-filter));
}

/* 5) 버튼 개별 커스텀도 가능 */
#StartBtn{
  --btn-transition: all .45s ease-in-out;
  --btn-hover-transform: translateY(-2px) scale(1.01);
}
/* 대상 버튼 목록에 나가기 버튼 추가 */
#SpactateBtn, #SetRoomBtn, #NewRoomBtn, #QuickRoomBtn, #ShopBtn, #DictionaryBtn,
#InviteBtn, #PracticeBtn, #ReadyBtn, #StartBtn, #ReplayBtn, #ExitBtn{
  transition: var(--btn-transition, var(--ui-transition)) !important;
  background: var(--btn-grad, linear-gradient(135deg, #ff3366, #9933ff)) !important;
}

/* hover에도 추가 */
#SpactateBtn:hover, #SetRoomBtn:hover, #NewRoomBtn:hover, #QuickRoomBtn:hover, #ShopBtn:hover, #DictionaryBtn:hover,
#InviteBtn:hover, #PracticeBtn:hover, #ReadyBtn:hover, #StartBtn:hover, #ReplayBtn:hover, #ExitBtn:hover{
  transform: var(--btn-hover-transform, var(--ui-hover-transform));
  filter: var(--btn-hover-filter, var(--ui-hover-filter));
  background: var(--btn-hover-grad, linear-gradient(135deg, #ff4d7a, #ad4dff)) !important;
}

/* 나가기 버튼 개별 그라데이션 */
#ExitBtn{
  --btn-grad: linear-gradient(135deg, #ff416c, #ff4b2b);
  --btn-hover-grad: linear-gradient(135deg, #ff5c82, #ff6848);
  --btn-active-grad: linear-gradient(135deg, #d9365a, #d93f25);
}
/* 부모 기본값 */
:root{
  --ui-btn-fg: #ffffff;
  --ui-btn-hover-fg: #ffffff;
  --ui-btn-active-fg: #fff7ff;
}

/* 대상 버튼 공통 (글자색 변수 적용) */
#SpactateBtn, #SetRoomBtn, #NewRoomBtn, #QuickRoomBtn, #ShopBtn, #DictionaryBtn,
#InviteBtn, #PracticeBtn, #ReadyBtn, #StartBtn, #ReplayBtn, #ExitBtn{
  color: var(--btn-fg, var(--ui-btn-fg)) !important;
}

#SpactateBtn:hover, #SetRoomBtn:hover, #NewRoomBtn:hover, #QuickRoomBtn:hover, #ShopBtn:hover, #DictionaryBtn:hover,
#InviteBtn:hover, #PracticeBtn:hover, #ReadyBtn:hover, #StartBtn:hover, #ReplayBtn:hover, #ExitBtn:hover{
  color: var(--btn-hover-fg, var(--ui-btn-hover-fg)) !important;
}

#SpactateBtn.toggled, #SetRoomBtn.toggled, #NewRoomBtn.toggled, #QuickRoomBtn.toggled, #ShopBtn.toggled, #DictionaryBtn.toggled,
#InviteBtn.toggled, #PracticeBtn.toggled, #ReadyBtn.toggled, #StartBtn.toggled, #ReplayBtn.toggled, #ExitBtn.toggled,
#SpactateBtn.active, #SetRoomBtn.active, #NewRoomBtn.active, #QuickRoomBtn.active, #ShopBtn.active, #DictionaryBtn.active,
#InviteBtn.active, #PracticeBtn.active, #ReadyBtn.active, #StartBtn.active, #ReplayBtn.active, #ExitBtn.active{
  color: var(--btn-active-fg, var(--ui-btn-active-fg)) !important;
}
#StartBtn{
  --btn-fg: #fff;
  --btn-hover-fg: #ffe9f6;
  --btn-active-fg: #ffd2ec;
}
#ExitBtn{
  --btn-fg: #fff;
  --btn-hover-fg: #fff3f3;
  --btn-active-fg: #ffdede;
}


# 기사 가져오는 엔진
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
        if direction and "하락" in direction.text: diff_val = -diff_val
        prev_close = curr_price - diff_val
        perc = (diff_val / prev_close) * 100
        return {'curr': curr_price, 'perc': perc}
    except: return None

def get_google_stock_news(limit=10):
    rss_url = "https://news.google.com/rss/search?q=주식&hl=ko&gl=KR&ceid=KR:ko"
    try:
        feed = feedparser.parse(rss_url)
        results = []
        for entry in feed.entries[:limit]:
            title = entry.title
            if " - " in title: title = title.rsplit(" - ", 1)[0]
            if " By " in title: title = title.split(" By ")[0]
            elif " by " in title: title = title.split(" by ")[0]
            results.append({"title": title.strip(), "link": entry.link})
        return results
    except: return []

# 페이지 디자인, 설정
st.set_page_config(page_title="주식 실시간 모니터링 시스템", page_icon="📈", layout="wide")
# --- 여기에 기존 st.set_page_config 가 있을 겁니다 ---

# 1. 스타일 정의 (왼쪽 벽에 딱 붙여서 넣어주세요)
# 1. 통합 스타일 정의 (기존 스타일 + 새로운 타이틀 디자인)
st.markdown("""
    <style>
    /* 메인 타이틀: 그라데이션 및 그림자 */
    .main-title {
        font-size: 32px !important; 
        font-weight: 900 !important;
        background: linear-gradient(135deg, #FF4B4B, #764BA2);
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent;
        text-shadow: 2px 2px 10px rgba(255, 75, 75, 0.3);
        text-align: center; 
        margin-top: -20px;
        margin-bottom: 5px;
    }
    
    /* 서브 타이틀 */
    .sub-title {
        font-size: 20px !important; 
        font-weight: 400 !important; 
        color: #888888 !important;
        text-align: center; 
        margin-bottom: 30px; 
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    /* 상단 구분선 */
    .custom-divider {
        height: 2px;
        background: linear-gradient(to right, transparent, #FF4B4B, #764BA2, transparent);
        margin-bottom: 35px;
        opacity: 0.6;
    }

    /* 일반 버튼 스타일 & 애니메이션 */
    div.stButton > button {
        width: 100%; 
        border-radius: 12px; 
        background: linear-gradient(135deg, #FF4B4B, #764BA2);
        color: white !important; 
        font-weight: 700; 
        border: none; 
        padding: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* 버튼 호버 효과 */
    div.stButton > button:hover {
        background: linear-gradient(135deg, #FF6B6B, #8E5ACD) !important;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 75, 75, 0.4);
        border: none !important;
        color: white !important;
    }

    /* 버튼 클릭 시 */
    div.stButton > button:active {
        transform: translateY(0px);
    }
    
    /* 메트릭(가격표) 박스 */
    [data-testid="stMetric"] { 
        background-color: #1e1e1e; 
        padding: 15px; 
        border-radius: 15px; 
        border: 1px solid #333;
    }
    
    /* 뉴스 리스트 스타일 */
    .news-item { font-size: 13px; margin-bottom: 12px; border-bottom: 1px solid #262626; padding-bottom: 8px; }
    .news-link { color: #FF4B4B; text-decoration: none; font-weight: 500; }
    .news-link:hover { text-decoration: underline; }

    /* 모바일 사이드바 열기 버튼(삼선메뉴) 최적화 */
    button[data-testid="stSidebarCollapseButton"] {
        width: 55px !important;
        height: 55px !important;
        background-color: rgba(255, 75, 75, 0.15) !important;
        border-radius: 12px !important;
    }

    button[data-testid="stSidebarCollapseButton"] svg {
        width: 32px !important;
        height: 32px !important;
        fill: #FF4B4B !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. 실제 화면에 렌더링되는 타이틀 섹션
st.markdown('<div class="main-title">실시간 외국-국내 주식 모니터링 시스템</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">𝕽𝖊𝖆𝖑-𝖙𝖎𝖒𝖊 𝕾𝖙𝖔𝖈𝖐 𝕴𝖓𝖙𝖊𝖑𝖑𝖎𝖌𝖊𝖓𝖈𝖊 𝕾𝖞𝖘𝖙𝖊𝖒</div>', unsafe_allow_html=True)
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# --- 그다음 st_autorefresh 등이 오면 됩니다 ---
with st.sidebar:
    st.header("⚙ 종목ㆍ기간 설정")
    stock_dict = {
        "삼성전자 (Samsung)": {"id": "005930", "y": "005930.KS"},
        "현대자동차 (Hyundai)": {"id": "005380", "y": "005380.KS"},
        "SK 하이닉스 (Hynix)": {"id": "000660", "y": "000660.KS"},
        "엔비디아 (NVDA)": {"id": "NVDA", "y": "NVDA"},
        "알파벳(구글) (GOOG)": {"id": "GOOG", "y": "GOOG"},
        "LG전자": {"id": "066570", "y": "066570.KS"},
        "넷플릭스 (NFLX)": {"id": "NFLX", "y": "NFLX"},
        "맥도날드": {"id": "MCD", "y": "MCD"}

    }
    selected_names = st.multiselect("종목 선택", options=list(stock_dict.keys()), default=["삼성전자 (Samsung)"])
    
    st.divider()
    period_options = {"1주일": "7d", "1개월": "1mo", "6개월": "6mo", "1년": "1y", "5년": "5y"}
    selected_period_label = st.selectbox("모니터링 기간", options=list(period_options.keys()), index=2)
    selected_p = period_options[selected_period_label]

    st.divider()
    st.subheader("목표 가격 설정")
    target_price = st.number_input("목표 가격 설정", min_value=0.0, value=0.0, step=100.0)

    if st.button("확인", width='stretch', key="sidebar_btn"): st.rerun()

    st.divider()
    st.subheader("📰 오늘의 주식 뉴스")
    news_data = get_google_stock_news(6)
    if news_data:
        for news in news_data:
            st.markdown(f'<div class="news-item">· <a class="news-link" href="{news["link"]}" target="_blank">{news["title"]}</a></div>', unsafe_allow_html=True)

# 4. 메인
if selected_names:
    for name in selected_names:
        info = stock_dict[name]
        m_col1, m_col2 = st.columns([1, 4])
        
        with m_col1:
            if info["id"].isdigit():
                res = get_naver_stock(info["id"])
                if res: st.metric(label=name, value=f"{res['curr']:,}원", delta=f"{res['perc']:+.2f}%")
            else:
                y_t = yf.Ticker(info["y"])
                y_h = y_t.history(period="1d")
                if not y_h.empty:
                    c_v = y_h['Close'].iloc[-1]
                    p_c = y_t.info.get('regularMarketPreviousClose', c_v)
                    st.metric(label=name, value=f"${c_v:,.2f}", delta=f"{(c_v-p_c)/p_c*100:+.2f}%")

        # 그래프 생성 로직
        itv = "30m" if selected_p == "7d" else "1d"
        df = yf.Ticker(info["y"]).history(period=selected_p, interval=itv)
        
        if not df.empty:
            # 이평선 계산, 명칭 (이름)
            df['5일 이동평균선'] = df['Close'].rolling(5).mean()
            df['20일 이동평균선'] = df['Close'].rolling(20).mean()
            df['60일 이동평균선'] = df['Close'].rolling(60).mean()
            
            # 배경
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                vertical_spacing=0.05, row_width=[0.25, 0.75])
            
            # 캔들차트, 이동평균선
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price', increasing_line_color='#FF4B4B', decreasing_line_color='#0083B0'), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['5일 이동평균선'], name='5일 이동평균선', line=dict(color='#FFEE00', width=1.2)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['20일 이동평균선'], name='20일 이동평균선', line=dict(color='#FF00FF', width=1.2)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['60일 이동평균선'], name='60일 이동평균선', line=dict(color='#00FF00', width=1.2)), row=1, col=1)
            
            if target_price > 0:
                fig.add_hline(y=target_price, line_dash="dash", line_color="white", annotation_text=f"Target: {target_price:,.0f}", row=1, col=1)

            # 거래량
            fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='#FF4B4B', opacity=0.5, showlegend=False), row=2, col=1)

            fig.update_layout(
                height=550, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=10, b=10), xaxis_rangeslider_visible=False, dragmode=False,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hoverlabel=dict(font=dict(color="black", size=13), bgcolor="white") 
            )
            
            with m_col2: 
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        st.divider()
# 5.메모장
m1, m2 = st.columns([4, 1])
with m1: st.text_area("메모장", placeholder="텍스트를 입력해보세요... 삼떡기", height=100)
with m2: 
    st.write("")
    st.write("")
    if st.button("새로고침🔄", width='stretch', key="main_btn"): st.rerun()

/* =========================================
   버튼 개별 그라데이션 시스템
   대상: Spectate/SetRoom/NewRoom/QuickRoom/Shop/Dictionary/Invite/Practice/Ready/Start/Replay
   ========================================= */

/* 1) 공통 적용 규칙 (각 버튼이 자기 변수 사용) */
#SpactateBtn, #SetRoomBtn, #NewRoomBtn, #QuickRoomBtn, #ShopBtn, #DictionaryBtn,
#InviteBtn, #PracticeBtn, #ReadyBtn, #StartBtn, #ReplayBtn{
  background: var(--btn-grad, linear-gradient(135deg, #cf0034, #9933ff)) !important;
  color: var(--btn-fg, #fff) !important;
  border: 1px solid var(--btn-border, rgba(255,255,255,.18)) !important;
  transition: all .25s linear(0 0%, 0.2 45.98%, 0.68 80.86%, 1 100%) !important;
  box-shadow: 0 0 8px rgba(255,51,102,.28), 0 0 14px rgba(153,51,255,.22);
}

#SpactateBtn:hover, #SetRoomBtn:hover, #NewRoomBtn:hover, #QuickRoomBtn:hover, #ShopBtn:hover, #DictionaryBtn:hover,
#InviteBtn:hover, #PracticeBtn:hover, #ReadyBtn:hover, #StartBtn:hover, #ReplayBtn:hover{
  background: var(--btn-hover-grad, linear-gradient(135deg, #ff4d7a, #a64dff)) !important;
  color: var(--btn-hover-fg, #fff) !important;
  box-shadow: 0 0 12px rgba(255,51,102,.45), 0 0 22px rgba(153,51,255,.35);
  transform: translateY(-1px);
}

/* 토글/활성 상태 */
#SpactateBtn.toggled, #SetRoomBtn.toggled, #NewRoomBtn.toggled, #QuickRoomBtn.toggled, #ShopBtn.toggled, #DictionaryBtn.toggled,
#InviteBtn.toggled, #PracticeBtn.toggled, #ReadyBtn.toggled, #StartBtn.toggled, #ReplayBtn.toggled,
#SpactateBtn.active, #SetRoomBtn.active, #NewRoomBtn.active, #QuickRoomBtn.active, #ShopBtn.active, #DictionaryBtn.active,
#InviteBtn.active, #PracticeBtn.active, #ReadyBtn.active, #StartBtn.active, #ReplayBtn.active{
  background: var(--btn-active-grad, linear-gradient(135deg, #d12b55, #7f2ed1)) !important;
  color: var(--btn-active-fg, #fff) !important;
}

/* 2) 버튼별 그라데이션 정의 (원하는 색으로 바꾸면 됨) */
#SpectateBtn{
  --btn-grad: linear-gradient(135deg, #f83939, #ac33e3);
  --btn-hover-grad: linear-gradient(135deg, #4b8ff0, #4b7f96);
  --btn-active-grad: linear-gradient(135deg, #2e62aa, #01a0ec);
}
#SetRoomBtn{
  --btn-grad: linear-gradient(135deg, #ab33e4, #80bfe6);
  --btn-hover-grad: linear-gradient(135deg, #ab33e4, #8280E6);
  --btn-active-grad: linear-gradient(135deg, #e14b59, #e0ab5f);
}
#NewRoomBtn{
  --btn-grad: linear-gradient(135deg, #fb2525, #b800ff);
  --btn-hover-grad: linear-gradient(135deg, #ff4747, #ac33e3);
  --btn-active-grad: linear-gradient(135deg, #0e7f76, #2fc967);
}
#QuickRoomBtn{
  --btn-grad: linear-gradient(135deg, #2f71e9, #6f87ff);
  --btn-hover-grad: linear-gradient(135deg, #3d7cea, #8b9bef);
  --btn-active-grad: linear-gradient(135deg, #d83a5a, #344ed4);
}
#ShopBtn{
  --btn-grad: linear-gradient(135deg, #ff8f01, #ffd200);
  --btn-hover-grad: linear-gradient(135deg, #ffab3d, #ffe14f);
  --btn-active-grad: linear-gradient(135deg, #d38218, #d9b300);
}
#DictionaryBtn{
  --btn-grad: linear-gradient(135deg, #058300, #68d873);
  --btn-hover-grad: linear-gradient(135deg, #1e8831, #7eff88);
  --btn-active-grad: linear-gradient(135deg, #7423bb, #3e00bb);
}
#InviteBtn{
  --btn-grad: linear-gradient(135deg, #ab33e4, #d69ce3);
  --btn-hover-grad: linear-gradient(135deg, #8027ff, #ee9fec);
  --btn-active-grad: linear-gradient(135deg, #00a7d9, #0060d6);
}
#PracticeBtn{
  --btn-grad: linear-gradient(135deg, #d3dc00, #a6a600);
  --btn-hover-grad: linear-gradient(135deg, #ffe810, #987a23);
  --btn-active-grad: linear-gradient(135deg, #4a9628, #93c957);
}
#ReadyBtn{
  --btn-grad: linear-gradient(135deg, #ff3366, #b56cff);
  --btn-hover-grad: linear-gradient(135deg, #ff4d7a, #ad4dff);
  --btn-active-grad: linear-gradient(135deg, #d62a55, #7f2bd1);
}
#StartBtn{
  --btn-grad: linear-gradient(135deg, #ff3939, #8d47ef);
  --btn-hover-grad: linear-gradient(135deg, #fb1616, #f17979);
  --btn-active-grad: linear-gradient(135deg, #d9472a, #bc1f63);
}
#ReplayBtn{
  --btn-grad: linear-gradient(135deg, #ff0000, #ff8383);
  --btn-hover-grad: linear-gradient(135deg, #e30d0d, #ffcbcb);
  --btn-active-grad: linear-gradient(135deg, #187c58, #7ed6a0);
}
/* =========================================
   부모 -> 자식 트랜지션 상속 시스템
   ========================================= */

/* 1) 전역 기본값(부모) */
:root{
  --ui-transition: all .25s linear;
  --ui-hover-transform: translateY(-1px);
  --ui-hover-filter: brightness(1.12);
}

/* 2) 부모 컨테이너별 오버라이드 가능
   예: 게임방에서만 더 느리게 */
#Wrap{
  --ui-transition: all .35s linear;
}
.GameBox{
  --ui-transition: all .18s ease-out;
}

/* 3) 대상 버튼들: 부모 변수 사용 */
#SpactateBtn, #SetRoomBtn, #NewRoomBtn, #QuickRoomBtn, #ShopBtn, #DictionaryBtn,
#InviteBtn, #PracticeBtn, #ReadyBtn, #StartBtn, #ReplayBtn{
  transition: var(--btn-transition, var(--ui-transition)) !important;
}

/* 4) hover도 부모 변수 사용 */
#SpactateBtn:hover, #SetRoomBtn:hover, #NewRoomBtn:hover, #QuickRoomBtn:hover, #ShopBtn:hover, #DictionaryBtn:hover,
#InviteBtn:hover, #PracticeBtn:hover, #ReadyBtn:hover, #StartBtn:hover, #ReplayBtn:hover{
  transform: var(--btn-hover-transform, var(--ui-hover-transform));
  filter: var(--btn-hover-filter, var(--ui-hover-filter));
}

/* 5) 버튼 개별 커스텀도 가능 */
#StartBtn{
  --btn-transition: all .15s linear;
  --btn-hover-transform: translateY(-2px) scale(1.01);
}
/* 대상 버튼 목록에 나가기 버튼 추가 */
#SpactateBtn, #SetRoomBtn, #NewRoomBtn, #QuickRoomBtn, #ShopBtn, #DictionaryBtn,
#InviteBtn, #PracticeBtn, #ReadyBtn, #StartBtn, #ReplayBtn, #ExitBtn{
  transition: var(--btn-transition, var(--ui-transition)) !important;
  background: var(--btn-grad, linear-gradient(135deg, #ff3366, #9933ff)) !important;
}

/* hover에도 추가 */
#SpactateBtn:hover, #SetRoomBtn:hover, #NewRoomBtn:hover, #QuickRoomBtn:hover, #ShopBtn:hover, #DictionaryBtn:hover,
#InviteBtn:hover, #PracticeBtn:hover, #ReadyBtn:hover, #StartBtn:hover, #ReplayBtn:hover, #ExitBtn:hover{
  transform: var(--btn-hover-transform, var(--ui-hover-transform));
  filter: var(--btn-hover-filter, var(--ui-hover-filter));
  background: var(--btn-hover-grad, linear-gradient(135deg, #ff4d7a, #ad4dff)) !important;
}

/* 나가기 버튼 개별 그라데이션 */
#ExitBtn{
  --btn-grad: linear-gradient(135deg, #ff0000, #e75656);
  --btn-hover-grad: linear-gradient(135deg, #ff3434, #ff7373);
  --btn-active-grad: linear-gradient(135deg, #d9365a, #d93f25);
}
/* 대상 버튼 공통 (글자색 변수 적용) */
#SpactateBtn, #SetRoomBtn, #NewRoomBtn, #QuickRoomBtn, #ShopBtn, #DictionaryBtn,
#InviteBtn, #PracticeBtn, #ReadyBtn, #StartBtn, #ReplayBtn, #ExitBtn{
  color: var(--btn-fg, var(--ui-btn-fg)) !important;
}

#SpactateBtn:hover, #SetRoomBtn:hover, #NewRoomBtn:hover, #QuickRoomBtn:hover, #ShopBtn:hover, #DictionaryBtn:hover,
#InviteBtn:hover, #PracticeBtn:hover, #ReadyBtn:hover, #StartBtn:hover, #ReplayBtn:hover, #ExitBtn:hover{
  color: var(--btn-hover-fg, var(--ui-btn-hover-fg)) !important;
}

#SpactateBtn.toggled, #SetRoomBtn.toggled, #NewRoomBtn.toggled, #QuickRoomBtn.toggled, #ShopBtn.toggled, #DictionaryBtn.toggled,
#InviteBtn.toggled, #PracticeBtn.toggled, #ReadyBtn.toggled, #StartBtn.toggled, #ReplayBtn.toggled, #ExitBtn.toggled,
#SpactateBtn.active, #SetRoomBtn.active, #NewRoomBtn.active, #QuickRoomBtn.active, #ShopBtn.active, #DictionaryBtn.active,
#InviteBtn.active, #PracticeBtn.active, #ReadyBtn.active, #StartBtn.active, #ReplayBtn.active, #ExitBtn.active{
  color: var(--btn-active-fg, var(--ui-btn-active-fg)) !important;
}
#StartBtn{
  --btn-fg: #fff;
  --btn-hover-fg: #ffe9f6;
  --btn-active-fg: #ffd2ec;
}
#ExitBtn{
  --btn-fg: #ffffff;
  --btn-hover-fg: #fff3f3;
  --btn-active-fg: #ffdede;
}
* ===== Dark Purple Base + Static Weak Neon ===== */
:root{
  --bg-dark-purple: #140a22;
  --panel-dark-purple: rgba(36, 18, 56, 0.78);
  --panel-dark-purple-soft: rgba(28, 14, 44, 0.72);
  --neon-weak-pink: rgba(255, 90, 180, 0.16);
  --neon-weak-purple: rgba(160, 90, 255, 0.14);
}

/* 배경 */
body{
  background: var(--bg-dark-purple) !important;
  background-image:
    radial-gradient(ellipse 70% 50% at 20% 10%, rgba(120,40,190,0.16) 0%, transparent 70%),
    radial-gradient(ellipse 60% 45% at 80% 85%, rgba(80,30,160,0.14) 0%, transparent 70%) !important;
  color: #eee !important;
}

/* 패널/박스 계열을 어두운 보라로 통일 */
.Product, .dialog, .UserListBox, .RoomListBox, .ShopBox, .RoomBox, .GameBox, .MeBox, .ChatBox, .ADBox{
  background-color: var(--panel-dark-purple) !important;
  border: 1px solid rgba(220, 180, 255, 0.14) !important;
  box-shadow:
    0 0 8px var(--neon-weak-pink),
    0 0 14px var(--neon-weak-purple) !important;
}

/* 흰색으로 뜨는 카드 보정 */
.rooms-item{
  background-color: var(--panel-dark-purple-soft) !important;
}

/* 외곽 네온: 약하고 정적(반응/펄스 없음) */
#Wrap::after, #kkutu-wrap::after{
  border: 1px solid rgba(255, 140, 220, 0.28) !important;
  box-shadow:
    0 0 10px rgba(255, 90, 180, 0.18),
    0 0 20px rgba(140, 90, 255, 0.14) !important;
  animation: none !important;
  opacity: 0.8 !important;
}

/* =========================================
   버튼 + 다크보라 배경 + 약한 정적 네온 (정리본)
   ========================================= */

/* 전역 변수 */
:root{
  --ui-transition: all .25s linear;
  --ui-hover-transform: translateY(-1px);
  --ui-hover-filter: brightness(1.12);

  --ui-btn-fg: #fff;
  --ui-btn-hover-fg: #fff;
  --ui-btn-active-fg: #fff7ff;

  --bg-dark-purple: #140a22;
  --panel-dark-purple: rgba(36, 18, 56, 0.78);
  --panel-dark-purple-soft: rgba(28, 14, 44, 0.72);
  --neon-weak-pink: rgba(255, 90, 180, 0.16);
  --neon-weak-purple: rgba(160, 90, 255, 0.14);
}

/* 배경 강제 */
html, body{
  background-color: var(--bg-dark-purple) !important;
}
body{
  background-image:
    radial-gradient(ellipse 70% 50% at 20% 10%, rgba(120,40,190,0.16) 0%, transparent 70%),
    radial-gradient(ellipse 60% 45% at 80% 85%, rgba(80,30,160,0.14) 0%, transparent 70%) !important;
  color: #eee !important;
}

/* 패널 공통 */
.Product, .dialog, .UserListBox, .RoomListBox, .ShopBox, .RoomBox, .GameBox, .MeBox, .ChatBox, .ADBox{
  background-color: var(--panel-dark-purple) !important;
  border: 1px solid rgba(220, 180, 255, 0.14) !important;
  box-shadow: 0 0 8px var(--neon-weak-pink), 0 0 14px var(--neon-weak-purple) !important;
}
.rooms-item{
  background-color: var(--panel-dark-purple-soft) !important;
}

/* 외곽 네온: 정적 */
#Wrap::after, #kkutu-wrap::after{
  border: 1px solid rgba(255, 140, 220, 0.28) !important;
  box-shadow: 0 0 10px rgba(255, 90, 180, 0.18), 0 0 20px rgba(140, 90, 255, 0.14) !important;
  animation: none !important;
  opacity: .8 !important;
}

/* 버튼 공통 대상 */
#SpactateBtn, #SpectateBtn, #SetRoomBtn, #NewRoomBtn, #QuickRoomBtn, #ShopBtn, #DictionaryBtn,
#InviteBtn, #PracticeBtn, #ReadyBtn, #StartBtn, #ReplayBtn, #ExitBtn{
  transition: var(--btn-transition, var(--ui-transition)) !important;
  background: var(--btn-grad, linear-gradient(135deg, #cf0034, #9933ff)) !important;
  color: var(--btn-fg, var(--ui-btn-fg)) !important;
  border: 1px solid rgba(255,255,255,.18) !important;
}
#SpactateBtn:hover, #SpectateBtn:hover, #SetRoomBtn:hover, #NewRoomBtn:hover, #QuickRoomBtn:hover, #ShopBtn:hover, #DictionaryBtn:hover,
#InviteBtn:hover, #PracticeBtn:hover, #ReadyBtn:hover, #StartBtn:hover, #ReplayBtn:hover, #ExitBtn:hover{
  transform: var(--btn-hover-transform, var(--ui-hover-transform));
  filter: var(--btn-hover-filter, var(--ui-hover-filter));
  background: var(--btn-hover-grad, linear-gradient(135deg, #ff4d7a, #ad4dff)) !important;
  color: var(--btn-hover-fg, var(--ui-btn-hover-fg)) !important;
}
#SpactateBtn.toggled, #SpectateBtn.toggled, #SetRoomBtn.toggled, #NewRoomBtn.toggled, #QuickRoomBtn.toggled, #ShopBtn.toggled, #DictionaryBtn.toggled,
#InviteBtn.toggled, #PracticeBtn.toggled, #ReadyBtn.toggled, #StartBtn.toggled, #ReplayBtn.toggled, #ExitBtn.toggled,
#SpactateBtn.active, #SpectateBtn.active, #SetRoomBtn.active, #NewRoomBtn.active, #QuickRoomBtn.active, #ShopBtn.active, #DictionaryBtn.active,
#InviteBtn.active, #PracticeBtn.active, #ReadyBtn.active, #StartBtn.active, #ReplayBtn.active, #ExitBtn.active{
  background: var(--btn-active-grad, linear-gradient(135deg, #d12b55, #7f2ed1)) !important;
  color: var(--btn-active-fg, var(--ui-btn-active-fg)) !important;
													 
}
body{
  background:
    radial-gradient(1200px 700px at 15% 10%, rgba(170,70,255,.22), transparent 60%),
    radial-gradient(1000px 600px at 85% 90%, rgba(255,80,170,.18), transparent 60%),
    linear-gradient(160deg, #12071f 0%, #1a0c2e 45%, #12071f 100%) !important;
}
.Product, .dialog, .UserListBox, .RoomListBox, .ShopBox, .RoomBox, .GameBox, .MeBox, .ChatBox, .ADBox{
  background: linear-gradient(160deg, rgba(40,18,62,.82), rgba(28,12,45,.82)) !important;
}

 /* =========================================
   버튼 + 다크보라 배경 + 약한 정적 네온 (정리본)
   ========================================= */

:root{
  --ui-transition: all .25s linear;
  --ui-hover-transform: translateY(-1px);
  --ui-hover-filter: brightness(1.12);

  --ui-btn-fg: #fff;
  --ui-btn-hover-fg: #fff;
  --ui-btn-active-fg: #fff7ff;

  --bg-dark-purple: #000000;
  --panel-dark-purple: rgb(0 0 0 / 78%);
  --panel-dark-purple-soft: rgba(28, 14, 44, 0.72);
  --neon-weak-pink: rgba(255, 90, 180, 0.16);
  --neon-weak-purple: rgba(160, 90, 255, 0.14);
}

/* 배경 */
html, body{
  background-color: var(--bg-dark-purple) !important;
}
body{
  background:
    radial-gradient(1200px 700px at 15% 10%, rgba(170,70,255,.22), transparent 60%),
    radial-gradient(1000px 600px at 85% 90%, rgba(255,80,170,.18), transparent 60%),
    linear-gradient(160deg, #12071f 0%, #1a0c2e 45%, #12071f 100%) !important;
}

/* 패널 */
.Product, .dialog, .UserListBox, .RoomListBox, .ShopBox, .RoomBox, .GameBox, .MeBox, .ChatBox, .ADBox{
  background: linear-gradient(160deg, rgba(40,18,62,.82), rgba(28,12,45,.82)) !important;
  border: 1px solid rgba(220, 180, 255, 0.14) !important;
  box-shadow: 0 0 8px var(--neon-weak-pink), 0 0 14px var(--neon-weak-purple) !important;
}
.rooms-item{
  background-color: var(--panel-dark-purple-soft) !important;
}

/* 외곽 네온 */
#Wrap::after, #kkutu-wrap::after{
  border: 1px solid rgba(255, 140, 220, 0.28) !important;
  box-shadow: 0 0 10px rgba(255, 90, 180, 0.18), 0 0 20px rgba(140, 90, 255, 0.14) !important;
  animation: none !important;
  opacity: .8 !important;
}

/* 버튼 공통 */
#SpactateBtn, #SpectateBtn, #SetRoomBtn, #NewRoomBtn, #QuickRoomBtn, #ShopBtn, #DictionaryBtn,
#InviteBtn, #PracticeBtn, #ReadyBtn, #StartBtn, #ReplayBtn, #ExitBtn{
  transition: var(--btn-transition, var(--ui-transition)) !important;
  background: var(--btn-grad, linear-gradient(135deg, #cf0034, #200040)) !important;
  color: var(--btn-fg, var(--ui-btn-fg)) !important;
  border: 1px solid rgba(255,255,255,.18) !important;
}
