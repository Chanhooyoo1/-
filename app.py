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



		   ㅊㄴㄴ
 /**
 * Rule the words! KKuTu Online
 * 원본 in_kkutu.css의 모든 레이아웃 수치를 1:1로 유지하며 스타일만 변경했습니다.
 * [FIX] float 레이아웃 붕괴 방지: clearfix 및 overflow 처리 추가
 */

/* ─── 공통 Clearfix ─────────────────────────────────────────── */
.Product::after,
.dialog::after,
.UserListBox::after,
.RoomListBox::after,
.ShopBox::after,
.RoomBox::after,
.GameBox::after,
.MeBox::after,
.ChatBox::after,
.ADBox::after,
.kkutu-menu::after,
.dialog-bar::after,
.tail-button::after,
.rooms-item::after,
.room-user::after,
.game-user::after,
.result-board-item::after,
.result-me::after,
.cf-item::after,
.chat-item::after,
.replay-player-bar::after,
.ri-player::after,
.profile-head-item::after {
	content: "";
	display: table;
	clear: both;
}

equ{
	font-family: consolas;
	font-style: italic;
	color: #ff3366;
}
#Intro{
	position: fixed;
	z-index: 4;
}
#Intro img{
	width: 1010px;
	height: 604px;
	border-radius: 20px;
}
	#version{
		position: absolute;
		top: 4px;
		left: 4px;
		font-size: 13px;
		text-shadow: 0px 0px 3px #000000;
		color: #fff;
	}
	#intro-text{
		position: absolute;
		top: 360px;
		left: 0px;
		width: 100%;
		font-size: 15px;
		text-align: center;
		text-shadow: 0px 0px 3px #000000;
		color: #eee;
	}
#Loading{
	position: fixed;
	padding-top: 200px;
	width: 100%;
	height: 100%;
	text-align: center;
	background-color: rgba(20, 10, 30, 0.6);
	backdrop-filter: blur(15px);
	z-index: 5;
}
#Top{
	background-color: rgba(255, 255, 255, 0.2);
	backdrop-filter: blur(20px);
	background-image: none;
	border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
#Top .menu-btn{
	color: #000000 !important;
	background-color: transparent;
	background-image: none;
	font-weight: bold;
}
#Top .menu-sub-btn{ color: #111111; }
#Bottom .bottom-text{ display: none; }

#facebook-menu{
	float: right;
}
iframe{
	border: none;
}
#Yell{
	position: fixed;
	padding: 10px 0px;
	margin-top: 200px;
	width: 100%;
	font-size: 32px;
	font-weight: bold;
	text-align: center;
	text-shadow: 0px 1px 1px #141414;
	pointer-events: none;
	background: linear-gradient(90deg, transparent, rgba(255, 51, 102, 0.6), rgba(153, 51, 255, 0.6), transparent);
	color: #fff;
}
#ReadyBtn{
	animation: ReadyBlink 1s linear infinite;
	background: linear-gradient(135deg, #f93636, #9933ff) !important;
	border: none;
	color: #fff;
	border-radius: 10px;
}
#ReadyBtn:hover, #ReadyBtn.toggled{
	animation: none;
}
.product-body{ font-size: 12px; }
.deltaScore{
	width: 100%;
	color: #ff3366;
	font-weight: bold;
	text-align: center;
	text-shadow: 0px 1px 2px rgba(0,0,0,0.5);
	animation: ScoreGoing 2s ease 1;
}
	.bonus{ color: #9933ff; }
	.lost{ color: #ff8888; }
.kkutu-menu{
	float: left;
	width: 1010px;
	height: 30px;
	overflow: hidden; /* [FIX] 버튼 float 감싸기 */
}
.kkutu-menu button{
	float: left;
	border: none;
	border-bottom-left-radius: 0px;
	border-bottom-right-radius: 0px;
	width: 98px;
	height: 20px;
	border-radius: 10px 10px 0 0;
	background-color: rgba(255, 255, 255, 0.2);
	color: #ffffffab !important;
	font-weight: bold;
}
	.kkutu-menu button:hover{
		margin-top: -5px;
		height: 25px;
		background: linear-gradient(to bottom, #ff3366, #9933ff);
		color: #fff !important;
	}
	.kkutu-menu .toggled{
		margin-top: 5px !important;
		color: #EEEEEE !important;
		background-color: #444444 !important;
	}
	.tiny-menu{
		width: 20px !important;
	}
.dialog{
	display: none;
	position: fixed;
	padding: 5px;
	border-radius: 15px;
	color: #ffffff;
	box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.5);
	background-color: rgba(40, 20, 50, 0.8) !important;
	backdrop-filter: blur(20px);
	border: 1px solid rgba(255, 255, 255, 0.1);
	z-index: 2;
	overflow: hidden; /* [FIX] 내부 float 감싸기 */
}
	.dialog-bar{
		float: left;
		margin: 3px 0px;
		width: 100%;
		overflow: hidden; /* [FIX] */
	}
	.dialog-bar h4{ float: left; padding-top: 6px; width: 100px; text-align: center; color: #ffb3c6; }
	.dialog-bar-value{ width: calc(100% - 100px) !important; text-align: left !important; }
	.dialog-bar input, .dialog-bar select{ float: left; width: 187px; height: 14px; box-sizing: inherit; outline: none; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.2); color: #fff; border-radius: 4px; }
	.dialog-bar label{ font-size: 13px; }
	.dialog-bar button{ float: left; }
		.dialog-opt{ float: left; width: 100px; }
	.tail-button{
		margin-top: 7px;
		overflow: hidden; /* [FIX] */
	}
	.tail-button button{ float: right; margin-right: 5px; width: 80px; height: 20px; background: linear-gradient(135deg, #ff3366, #9933ff); border: none; color: white; border-radius: 4px; }
	.dialog .closeBtn{
		float: right;
		border-radius: 50%;
		margin-top: 1px;
		width: 12px;
		height: 12px;
		background-color: #ff3366;
	}
	.dialog .closeBtn:hover{ background-color: #ff6688; }
	.dialog-head{
		padding: 3px;
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: 10px 10px 0 0;
		margin-bottom: 5px;
		height: 12px;
		color: #ffffff;
		font-size: 11px;
		background-color: rgba(255, 255, 255, 0.1) !important;
		overflow: hidden; /* [FIX] closeBtn float 감싸기 */
	}
		.dialog-head .dialog-title{ float: left; cursor: move; }
#replay-players{ height: 140px; overflow-y: scroll; }
	.replay-player-bar{
		float: left;
		width: 100%;
		overflow: hidden; /* [FIX] */
	}
		.replay-player-bar img{ float: left; margin-right: 3px; width: 20px; height: 20px; }
		.replay-player-bar label{ float: left; }
#ranking{
	font-size: 13px;
}
	.ranking-me{ font-weight: bold; background: linear-gradient(90deg, rgba(255, 51, 102, 0.2), rgba(153, 51, 255, 0.2)); }
	.ranking-image{ margin-right: 2px; width: 18px; height: 18px; }
	.ranking-1 td:first-child{ font-weight: bold; background-color: gold; color: #000; }
	.ranking-2 td:first-child{ font-weight: bold; background-color: silver; color: #000; }
	.ranking-3 td:first-child{ font-weight: bold; background-color: chocolate; color: #000; }
.moremi{
	position: relative;
}
.moremi img{
	position: absolute;
}
.Product{
	border-radius: px;
	color: #ffffff;
	box-shadow: 0px 8px 32px rgba(0, 0, 0, 0.3);
	background-color: rgba(255, 255, 255, 0.05) !important;
	backdrop-filter: blur(10px);
	border: 1px solid rgba(255, 255, 255, 0.1);
	overflow: hidden; /* [FIX] 내부 float 자식이 박스 밖으로 나가지 않도록 */
	box-sizing: border-box; /* [FIX] padding/border 포함 크기 계산 */
}
.product-title{
	border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	border-radius: 15px 15px 0 0;
	color: #ffffff;
	background: linear-gradient(90deg, rgb(255 40 40 / 82%), rgb(101 21 181 / 86%)) !important;
	overflow: hidden; /* [FIX] h5 float 감싸기 */
}
.product-title i{ color: #ffb3c6; }
.dialog-front{ z-index: 3; }
#comm-friends div{ float: left; }
	.cf-item{
		margin: 2px 0px;
		width: 100%;
		overflow: hidden; /* [FIX] */
	}
		.cfi-status{ border-radius: 7px; margin-right: 2px; width: 12px; height: 12px; }
			.cfi-stat-on{ background-color: #00ff00; }
			.cfi-stat-off{ background-color: gray; }
		.cfi-server{ width: 46px; text-align: center; }
		.cfi-name{ width: 60px; }
		.cfi-memo{ width: calc(100% - 150px); }
		.cfi-menu{ width: 30px; }
			.cfi-menu>i{ margin-right: 3px; cursor: pointer; }
			.cfi-menu>i:hover{ color: #ff3366; }
#ProfileDiag .dialog-body div{ float: left; }
	.profile-moremi{ margin-right: 3px; width: 80px; height: 80px; }
	.profile-head-item{
		margin: 3px 2px;
		width: 213px;
		overflow: hidden; /* [FIX] */
	}
		.profile-image{ margin-right: 3px; width: 20px; height: 20px; }
		.profile-level{ margin-right: 3px; width: 20px; height: 20px; }
		.profile-title{ padding-top: 1px; font-size: 15px; font-weight: bold; width: 190px; }
		.profile-tag{ font-size: 11px; color: #aaa; }
		.profile-level-text{ padding-top: 2px; font-size: 13px; }
		.profile-score-text{ float: right !important; padding-top: 3px; font-size: 11px; color: #ccc; }
	.profile-record-field{ margin: 2px 0px; width: 100%; }
		.profile-field-name{ width: 35%; text-align: center; }
		.profile-field-record{ width: 32%; text-align: center; }
		.profile-field-score{ width: 32%; text-align: center; }
#RoomInfoDiag .dialog-body div{ float: left; }
	.ri-player{
		margin: 2px 0px;
		width: 100%;
		overflow: hidden; /* [FIX] */
	}
		.rip-moremi{ margin-right: 3px; width: 40px; height: 40px; }
		.rip-master{ font-weight: bold; color: #ff3366; }
		.rip-title{ width: calc(100% - 43px); }
		.rip-team{ margin: 3px 3px 0px 0px; width: 44px; text-align: center; }
		.rip-form{ margin-top: 3px; width: calc(100% - 90px); }
.UserListBox{
	width: 200px;
	height: 360px;
	overflow: hidden; /* [FIX] */
	box-sizing: border-box; /* [FIX] */
}
	.UserListBox div{ float: left; }
	.UserListBox .product-body{ width: 190px; height: 330px; overflow-x: hidden; overflow-y: scroll; }
	.users-item{
		width: 190px;
		border-radius: 5px;
		overflow: hidden; /* [FIX] */
	}
		.users-image{ margin: 1px; width: 18px; height: 18px; }
		.users-level{ margin: 1px; width: 18px; height: 18px; }
		.users-name{ padding: 2px 0px 0px 3px; width: 147px; font-size: 13px; color: #eee; }
		.users-item:hover{ cursor: pointer; background-color: rgba(255, 255, 255, 0.1); }
	.invite-item{
		margin: 2px 0px;
		width: 100%;
		height: 20px;
		overflow: hidden; /* [FIX] */
	}
		.invite-item .users-name{ width: 270px; }
.RoomListBox{
	width: 807px;
	height: 360px;
	overflow: hidden; /* [FIX] */
	box-sizing: border-box; /* [FIX] */
}
	.RoomListBox div{ float: left; }
	.RoomListBox .product-body{ width: 780px; height: px; overflow-x: hidden; overflow-y: scroll; }
	.rooms-item{
		padding: 5px;
		border-radius: 12px;
		margin: 3px;
		width: 380px;
		height: 70px;
		box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
		cursor: pointer;
		background-color: rgb(255 255 255);
		transition: all 300ms ease;
		border: 1px solid rgba(255, 255, 255, 0.05);
		overflow: hidden; /* [FIX] 내부 float 감싸기 */
		box-sizing: border-box; /* [FIX] */
	}
.rooms-create {
  background: linear-gradient(to right, #ff2b2b, #7b33c2); /* 빨강-보라 그라데이션 */
}
		.rooms-create>div{ float: none; padding: 20px 0px; text-align: center; font-size: 15px; font-weight: bold; color: #fff; }
		.rooms-channel{ position: relative; width: 10px; height: 10px; border-radius: 5px; margin-right: -10px; }
			.rooms-channel:hover{ width: 8px; height: 8px; border: 1px solid #ff3366; }
			.channel-1{ background-color: #ff3366; }
			.channel-2{ background-color: #ffbf30; }
			.channel-3{ background-color: #88c525; }
			.channel-4{ background-color: #4a90d6; }
		.rooms-gaming{ background-color: rgba(255, 51, 102, 0.2); }
			.rooms-gaming .rooms-number{ border-color: rgba(255, 51, 102, 0.3); }
		.rooms-item:hover{ background-color: rgba(255, 255, 255, 0.15); transform: translateY(-2px); border-color: #ff3366; }
			.rooms-gaming:hover{ background-color: rgba(255, 51, 102, 0.3); }
			.rooms-create:hover{ background-color: rgba(153, 51, 255, 0.4); }
		.rooms-number{ padding-top: 18px; border-right: 1px solid rgba(255, 255, 255, 0.1); margin-right: 4px; width: 49px; height: 46px; font-size: 24px; color: #ffb3c6; }
		.rooms-title{ padding-top: 4px; width: 270px; height: 20px; font-size: 16px; font-weight: bold; color: #fff; }
		.rooms-limit{ padding-top: 7px; width: 39px; height: 17px; text-align: center; color: #ccc; }
		.rooms-mode{ padding-top: 5px; width: 270px; }
		.rooms-info{ width: 270px; }
			.rooms-round{ padding-top: 5px; margin-right: 10px; }
			.rooms-time{ padding-top: 5px; }
		.rooms-lock{ padding-top: 8px; width: 39px; text-align: center; font-size: 24px; color: #ff3366; }
.ShopBox{
	width: 790px;
	height: 360px;
	overflow: hidden; /* [FIX] */
	box-sizing: border-box; /* [FIX] */
}
	.ShopBox div{ float: left; }
	.ShopBox .product-body{ width: 780px; height: 330px; }
.RoomBox{
	width: 1000px;
	height: 390px;
	overflow: hidden; /* [FIX] */
	box-sizing: border-box; /* [FIX] */
}
.RoomBox{
	width: 1020px;
	height: 390px;
	overflow: hidden; /* [FIX] */
	box-sizing: border-box; /* [FIX] */
}
	.RoomBox .product-title{ height: 12px; }
	.RoomBox .product-title h5{ float: left; }
		.room-head-modified{ animation: ModifiedBlink 1s ease 3; }
		.room-head-number{ width: 35px; text-align: center; }
		.room-head-title{ font-weight: bold; width: 505px; }
		.room-head-mode{ margin-right: 5px; width: 255px; text-align: right; }
		.room-head-limit{ width: 70px; text-align: center; }
		.room-head-round{ width: 70px; text-align: center; }
		.room-head-time{ width: 14px; text-align: center; }
	.team-selector{
		float: left;
		padding-right: 3px;
		border-right: 1px solid rgba(255, 255, 255, 0.1);
		margin: 0px 2px 0px -5px;
		width: 40px;
		height: 320px;
		overflow: hidden; /* [FIX] */
	}
		.team-button{
			float: left;
			padding-top: 20px;
			border-radius: 10px;
			margin: 2px 0px;
			width: 100%;
			height: 40px;
			text-align: center;
			font-size: 13px;
			cursor: pointer;
			background: rgba(255, 255, 255, 0.05);
			transition: all 0.2s;
		}
		.team-button:hover{ border-bottom: 4px solid rgba(255, 51, 102, 0.5); margin-top: -2px; }
		.team-unable div{ background-color: #555; cursor: not-allowed; }
		.team-chosen{ font-weight: bold; border: 1px solid #fff; }
		.team-0{ background-color: rgba(255, 255, 255, 0.1); }
		.team-1{ background-color: rgba(255, 85, 85, 0.5); }
		.team-2{ background-color: rgba(255, 191, 48, 0.5); }
		.team-3{ background-color: rgba(136, 197, 37, 0.5); }
		.team-4{ background-color: rgba(74, 144, 214, 0.5); }
	.room-user{
		float: left;
		padding: 3px;
		border-radius: 10px;
		margin: 3px;
		width: 224px;
		height: 151px;
		box-shadow: 0px 1px 1px #777777;
		background-color: #6F6F66;
	}
		.room-user div{ float: left; }
		.room-user-image{ margin: 3px; width: 100px; height: 100px; }
		.room-user-stat{ padding: 3px; width: 112px; height: 100px; font-size: 15px; }
			.room-user-stat div{ margin-bottom: 4px; }
			.room-user-ready{ width: 90%; text-align: right; font-weight: bold; }
				.room-user-readied{ color: #3A8BDF; }
				.room-user-spectate{ color: #8160FF; }
				.room-user-practice{ color: #E1BA2D; }
				.room-user-master{ color: #E14E2D; }
			.room-user-team{ margin-left: 60%; width: 30%; text-align: center; }
		.room-user-title{ padding: 5px 1px; width: 150px; font-size: 15px; }
		.room-user-level{ width: 30px; height: 30px; }
		.room-user-name{ padding: 5px 0px 0px 4px; font-weight: bold; }
		.room-user:hover{ cursor: pointer; background-color: #123456; }
.GameBox{
	width: 1011px;
	height: 410px;
	background-image: linear-gradient(rgba(20, 10, 30, 0.8), rgba(20, 10, 30, 0.8)), url('/img/kkutu/gamebg.png');
	background-size: cover;
	border-radius: 15px;
	overflow: hidden; /* [FIX] */
	box-sizing: border-box; /* [FIX] */
}
	.GameBox .product-title{ height: 12px; }
	.GameBox .product-title h5{ float: left; }
	.GameBox div{ float: left; }
	.GameBox .product-body{ padding-top: 0px; }
	.game-replay-controller{ float: right !important; width: 100px; }
	.game-replay-controller button{
		float: right;
		margin-top: -2px;
		padding: 1px;
		width: 20px;
		font-size: 11px;
		background: rgba(255, 255, 255, 0.1);
		color: #fff;
		border: 1px solid rgba(255, 255, 255, 0.2);
	}
	.hints{
		margin: 40px 10px 0px 10px;
		width: 225px;
		height: 110px;
	}
		.hint-item{
			padding: 5px;
			border-radius: 5px;
			margin: 1px 0px;
			color: #EEEEEE;
			font-size: 13px;
			max-height: 63px;
			overflow: hidden;
			background-color: rgba(0, 0, 0, 0.7);
			border-left: 3px solid #ff3366;
		}
	.b-left{
		padding: 5px;
		margin-top: 25px;
		width: 324px;
		z-index: 1;
	}
		.bb-word{
			width: 50%;
			color: #EEEEEE;
		}
		.bb-char{
			padding: 2px;
			border-radius: 5px;
			margin: 1px;
			width: 10px;
			text-align: center;
			background-color: #111111;
		}
		.cw-q-head{
			margin: 3px 0px;
			width: 110%;
			font-size: 10px;
			color: #EEEEEE;
			text-align: center;
			text-shadow: 0px 1px 1px #000000;
		}
		.cw-q-body{
			padding: 5px;
			border-radius: 10px;
			margin-top: 5px;
			color: #CCCCCC;
			background-color: rgba(0, 0, 0, 0.7);
		}
	.items{
		padding-top: 55px;
		margin: 50px 40px 0px 105px;
		width: 100px;
		height: 45px;
		font-size: 24px;
		color: #EEEEEE;
		font-weight: bold;
		text-align: center;
		text-shadow: 0px 1px 5px #141414;
		background-image: url('/img/kkutu/lefthand.png');
	}
	.jjoriping{ width: 500px; }
	.cw.jjoriping{ margin-top: -10px; width: 322px; }
		.jjoObj{ position: relative; }
		.jjoNose{ top: 9px; left: 181px; }
		.cw .jjoNose{ left: 94px; }
		.jjoDisplayBar{
			padding: 1px 5px 5px 1px;
			border: 2px solid #ff3366;
			border-bottom-left-radius: 15px;
			border-bottom-right-radius: 15px;
			margin-top: -5px;
			width: 492px;
			height: 100px;
			background-color: rgba(40, 20, 60, 0.75);
			backdrop-filter: blur(10px);
			overflow: hidden; /* [FIX] */
			box-sizing: border-box; /* [FIX] */
		}
		.cw .jjoDisplayBar{ width: 308px; height: 330px; transition: all 0.5s ease; }
			.jjo-display{
				padding: 8px 10px;
				border-radius: 10px;
				border-bottom-left-radius: 0px;
				border-bottom-right-radius: 0px;
				width: 476px;
				height: 23px;
				font-size: 20px;
				text-align: center;
				color: #EEEEEE;
				background-color: rgba(0, 0, 0, 0.6);
			}
			.jjo-display-word-length{ color: #ffb3c6; font-size: 14px; }
			.cw .jjo-display{ position: relative; padding: 5px; width: 298px; height: 298px; }
				.display-text{ width: 20px; text-align: center; z-index: 1; }
				.game-fail-text{ animation: FailBlink 2s linear; color: #FF7777; }
				.cw-bar{
					position: absolute;
					border-radius: 10px;
					cursor: pointer;
					background-color: rgba(255, 255, 255, 0.2);
				}
				.cw-bar:hover{ background-color: rgba(255, 255, 255, 0.4); z-index: 1; }
				.cw-bar.cw-open{ background-color: #ff3366; pointer-events: none; z-index: 2; }
				.cw-bar.cw-my-open{ background-color: #9933ff; }
					.cw-cell{ padding-top: 4px; border-radius: 5px; margin: 3px; width: 32.5px; height: 28.5px; box-shadow: 0px 1px 5px rgba(0,0,0,0.5); }
			.jjoDisplayBar .graph{
				border-left: 1px solid rgba(0, 0, 0, 0.3);
				border-right: 1px solid rgba(0, 0, 0, 0.3);
				width: 484px;
				height: 20px;
				color: #FFFFFF;
				box-shadow: none;
				text-align: right;
				text-shadow: 0px 1px 3px #141414;
				overflow: hidden;
			}
			.jjoDisplayBar .graph-bar{
				padding-top: 4px;
				height: 16px;
				font-size: 11px;
				white-space: nowrap;
				overflow: hidden;
				border-radius: 4px;
			}
			.jjo-turn-time{ background-color: rgba(0, 0, 0, 0.3); }
			.jjo-round-time{
				border-bottom: 1px solid rgba(0, 0, 0, 0.3);
				border-bottom-left-radius: 10px;
				border-bottom-right-radius: 10px;
				background-color: rgba(0, 0, 0, 0.4);
			}
			.jjo-turn-time .graph-bar{ background: linear-gradient(90deg, #ff3366, #ff88a5); }
			.jjo-round-time .graph-bar{ background: linear-gradient(90deg, #9933ff, #d4a5ff); }
				.round-extreme{ background-color: #ff3366 !important; box-shadow: 0 0 10px #ff3366; }
			.cw .jjo-turn-time{ display: none; }
			.cw .jjo-round-time{ width: 306px; }
		.sock-char{ text-align: center; }
			.sock-picked{ color: #ff3366; font-weight: bold; font-size: 24px; text-shadow: 0 0 5px #ff3366; }
	.chain{
		padding-top: 55px;
		margin: 50px 105px 0px 40px;
		width: 100px;
		height: 45px;
		font-size: 24px;
		color: #EEEEEE;
		font-weight: bold;
		text-align: center;
		text-shadow: 0px 1px 5px #141414;
		background-image: url('/img/kkutu/righthand.png');
	}
	.rounds{
		margin-top: -130px;
		width: 990px;
		color: #FFFFFF;
		text-align: center;
		text-shadow: 0px 1px 1px #141414;
	}
	.cw.rounds{ margin-top: -380px; }
		.rounds label{ margin: 0px 3px; }
		.cw.rounds label{ cursor: pointer; }
		.rounds-current{ color: #ff3366; font-size: 16px; font-weight: bold; }
		.round-effect{ animation: RoundEffect 0.8s ease 1; }
	.history-holder{
		width: 990px;
		height: 40px;
		overflow: hidden;
	}
		.history{
			width: 1200px;
			height: 42px;
		}
			.history-item{
				height: 28px;
				padding: 4px 0px;
				border-radius: 10px;
				margin: 3px;
				color: #EEEEEE;
				text-align: center;
				background-color: rgba(0, 0, 0, 0.5);
				border: 1px solid rgba(255, 255, 255, 0.1);
			}
			.history-theme{
				float: none !important;
				margin: 3px;
				font-size: 11px;
				color: #ffb3c6;
			}
			.history-class{
				padding: 1px;
				border-radius: 5px;
				margin-left: 4px;
				font-size: 11px;
				color: #fff;
				background-color: #ff3366;
			}
			.history-mean-c{ color: #AAAAAA; }
			.history-mean{
				float: none !important;
				padding: 3px 2px 0px 1px;
				font-size: 11px;
				color: #AAAAAA;
			}
			.word-head{ margin-right: 3px; }
				.word-m1-head{
					padding: 0px 1px;
					margin: 0px 1px;
					color: #fff;
					font-weight: bold;
					background-color: #9933ff;
				}
				.word-m2-head{ color: #ff3366; }
				.word-m3-head{ color: #EEEEEE; }
					.word-m3-head::before{ content: "("; }
					.word-m3-head::after{ content: ")"; }
			.word-theme{ color: #ffb3c6; }
				.word-theme::before{ content: "<"; }
				.word-theme::after{ content: ">"; }
	.game-input{
		position: relative;
		top: -220px;
		left: 244px;
		padding: 5px;
		border-radius: 10px;
		background-color: rgba(0, 0, 0, 0.6);
		backdrop-filter: blur(5px);
	}
		#game-input{
			width: 478px;
			height: 40px;
			font-size: 20px;
			background: rgba(255, 255, 255, 0.1);
			color: #fff;
			border: 1px solid rgba(255, 255, 255, 0.2);
			border-radius: 6px;
			text-align: center;
		}
	.game-body{
		margin: 0px -1px;
		width: 992px;
		height: 180px;
		overflow: hidden; /* [FIX] */
	}
	.cw.game-body{ position: relative; top: -378px; left: 660px; width: 334px; }
		.game-user{
			padding: 1px;
			border: 3px solid rgba(255, 255, 255, 0.1);
			border-radius: 15px;
			margin: 13px 3px 3px 3px;
			width: 120px;
			height: 167px;
			box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.4);
			background-color: rgba(255, 255, 255, 0.05);
			backdrop-filter: blur(5px);
			transition: all 300ms ease;
			overflow: hidden; /* [FIX] 내부 float 감싸기 */
			box-sizing: border-box; /* [FIX] */
		}
		.cw .game-user{
			border: 2px solid rgba(255, 255, 255, 0.1);
			margin: 1px;
			width: 330px;
			height: 22px;
		}
		.game-user-current{
			animation: CurrentBlink 2s linear infinite;
			margin-top: 0px;
			height: 177px;
			background-color: rgba(153, 51, 255, 0.2);
			border-color: #ff3366;
		}
		.game-user-bomb{ border-color: #FF6666; box-shadow: 0 0 15px rgba(255, 51, 102, 0.6); }
			.game-user-image{ margin: 3px 5px; width: 100px; height: 100px; border-radius: 8px; }
			.game-user-level{ margin: 1px; width: 18px; height: 18px; }
			.game-user-name{ padding-left: 3px; margin: 3px 0px; width: 87px; height: 20px; font-size: 15px; color: #fff; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
			.game-user-score{ padding: 0px 5px; border-radius: 10px; width: 100px; font-size: 30px; font-weight: bold; color: #ffb3c6; text-shadow: 0 0 5px rgba(0,0,0,0.5); }
				.game-user-score-char{ width: 20px; text-align: center; }
			.cw .game-user-score{ padding-top: 3px; font-size: 15px; }
	#ResultDiag .dialog-body div{ float: left; }
		.result-board{
			width: 400px;
			height: 260px;
		}
			.result-board-item{
				padding: 5px;
				border-radius: 6px;
				margin: 1px;
				width: 388px;
				height: 20px;
				box-shadow: 0px 1px 3px rgba(0,0,0,0.2);
				background-color: rgba(255, 255, 255, 0.1);
				overflow: hidden; /* [FIX] */
			}
			.result-board-me{
				padding: 4px;
				border: 1px solid #ff3366;
				background-color: rgba(255, 51, 102, 0.1);
			}
				.result-board-rank{ padding-top: 3px; border-radius: 10px; width: 45px; height: 17px; text-align: center; background: #ff3366; color: #fff; }
				.result-board-level{ width: 20px; height: 20px; }
				.result-board-name{ padding-top: 3px; margin-left: 5px; width: 100px; }
				.result-board-score{ padding-top: 3px; width: 80px; text-align: center; }
				.result-board-reward{ padding-top: 3px; width: 80px; text-align: center; }
				.result-board-lvup{
					width: 58px;
					height: 20px;
					color: #ffb3c6;
					font-size: 13px;
					text-align: center;
					text-shadow: 0px 0px 3px #ff3366;
				}
					.result-board-lvup i{ float: left; margin-right: 1px; animation: LvUpBlink 1s infinite; }
					.result-board-lvup div{ padding-top: 3px; }
		.result-me{
			padding: 3px;
			border: 1px solid rgba(255, 255, 255, 0.1);
			border-radius: 10px;
			margin: 1px;
			width: 390px;
			height: 80px;
			font-size: 13px;
			background: rgba(0, 0, 0, 0.2);
			overflow: hidden; /* [FIX] */
		}
			.result-me-score{ width: 195px; color: #ffb3c6; text-align: center; }
				.result-me-bonus{ color: #ff3366; font-weight: bold; text-shadow: 0px 0px 5px #ff88a5; }
			.result-me-money{ width: 195px; color: #ccc; text-align: center; }
			.result-me-level{ margin-top: 5px; width: 80px; }
				.result-me-level-head{ width: 80px; text-align: center; }
				.result-me-level-body{
					width: 80px;
					text-align: center;
					font-size: 30px;
					font-weight: bold;
					color: #fff;
				}
			.result-me-gauge{
				border-radius: 10px;
				margin-top: 5px;
				width: 308px;
				height: 49px;
				overflow: hidden;
				box-shadow: 0px 1px 3px rgba(0,0,0,0.5);
				background-color: #111;
			}
				.result-me-before-bar{ background-color: #555; }
				.result-me-current-bar{ background: linear-gradient(90deg, #ff3366, #9933ff); }
				.result-me-bonus-bar{ background-color: #ffbf30; }
				.result-me-score-text{
					margin-top: -32px;
					margin-left: 80px;
					width: 308px;
					color: #EEEEEE;
					text-align: center;
					text-shadow: 0px 1px 1px #141414;
				}
			.result-me-expl h4{ color: #ff3366; }
			.result-me-expl div{ margin-bottom: 4px; width: 140px; }
			.result-me-blog-head{ float: left; width: 80px; color: #EEEEEE; }
			.result-me-blog-body{ float: left; width: 60px; color: #C7C7C7; }
	#KickVoteDiag{}
		.kick-vote-time{ border-radius: 10px; width: 100%; height: 40px; overflow: hidden; background-color: #4a1010; }
		.kick-vote-time .graph-bar{ background-color: #ff3366; }
	.purchase-not-enough{ color: #EE2222; }
.MeBox{
	width: 205px;
	height: 200px;
	cursor: pointer;
	overflow: hidden; /* [FIX] */
	box-sizing: border-box; /* [FIX] */
}
	.MeBox div{ float: left; }
	.bar-text{ color: #EEEEEE; text-align: center; text-shadow: 0px 1px 1px #141414; }
	.my-image{ width: 80px; height: 80px; border-radius: 12px; border: 2px solid rgba(255,255,255,0.1); }
	.my-stat{ padding-left: 5px; width: 105px; }
		.my-stat-level{ margin: 1px; width: 18px; height: 18px; }
		.my-stat-name{ padding-top: 3px; padding-left: 4px; width: 76px; height: 17px; font-weight: bold; color: #fff; }
		.my-stat-record{ margin-top: 3px; width: 100%; color: #ccc; }
		.my-stat-ping{ margin-top: 3px; width: 100%; color: #aaa; }
		.my-okg{ border-radius: 5px; margin-top: 3px; width: 100%; height: 20px; overflow: hidden; background-color: #221133; }
			.my-okg .graph-bar{ background: linear-gradient(90deg, #ff3366, #9933ff); }
		.my-okg-text{ margin-top: -15px; width: 100px; font-size: 11px; }
	.my-level{ margin: 13px 0px; width: 190px; font-size: 15px; text-align: center; color: #ffb3c6; font-weight: bold; }
	.my-gauge{ border-radius: 10px; margin: 3px 0px; width: 190px; height: 30px; overflow: hidden; background-color: rgba(0,0,0,0.5); }
		.my-gauge .graph-bar{ background: linear-gradient(90deg, #ff3366, #9933ff); }
	.my-gauge-text{ margin-top: -25px; width: 190px; }
	.category-filter{
		border-radius: 6px;
		text-align: center;
		font-size: 11px;
		cursor: pointer;
		background-color: rgba(255, 255, 255, 0.1);
		color: #000000;
		transition: all 300ms ease;
	}
	.goods-box{
		margin-top: 5px;
		height: 125px;
		overflow-y: scroll;
	}
		.dress-type{
			float: left;
			padding: 1px 0px;
			border: 1px solid rgba(255, 255, 255, 0.2);
			margin: 1px;
			width: 40px;
		}
		.category-filter.selected{ color: #EEEEEE; background: #ff3366; }
		.category-filter:hover{ background-color: rgba(255, 255, 255, 0.3); }
		.category-filter.selected:hover{ background-color: #ff6688; }
		.dress-item{
			float: left;
			padding: 1px;
			border: 1px solid rgba(255, 255, 255, 0.1);
			margin: 1px;
			width: 40px;
			height: 40px;
			background: rgba(0,0,0,0.2);
			border-radius: 4px;
		}
		.dress-equipped{ padding: 0px; border: 2px solid #ff3366; box-shadow: 0 0 10px #ff3366; }
		.dress-expl{ width: 240px; font-size: 11px; color: #eee; }
			.dress-item-title{ float: left; width: 160px; font-size: 13px; color: #ffb3c6; }
			.dress-item-group{ float: left; padding-top: 1px; width: 80px; color: #888; text-align: right; }
			.dress-item-term{ float: left; color: #ff88a5; }
			.dress-expl label{ display: inline; padding: none; font-size: inherit; }
			.dress-item-image{ width: 40px; height: 40px; font-size: 11px; text-align: right; text-shadow: 0px 0px 3px #111111; }
			.dress-item-expl{ float: left; margin: 2px 0px; width: 100%; }
			.dress-item-opts{ float: left; padding-top: 4px; border-top: 1px dashed rgba(255, 255, 255, 0.2); margin-top: 2px; width: 100%; }
				.item-opts-head{ color: #ffff44; }
					.item-opts-head::after{ content: ": " }
	#cf-tray{
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
		margin-top: -2px;
		height: 32px;
		overflow: hidden; /* [FIX] */
	}
		#cf-tray div{ width: 30px; height: 30px; cursor: pointer; border-radius: 6px; }
		.cf-tray-selected{ padding: 0px; border: 2px solid #ff3366; }
	#cf-dict{ margin: 2px 0px; height: 166px; color: #BBBBBB; overflow-y: scroll; background-color: rgba(0, 0, 0, 0.4); border-radius: 10px; }
	#cf-reward{ float: left; width: 100%; height: 148px; overflow-y: scroll; }
		.cf-rew-item{
			float: left;
			border-bottom: 1px dashed rgba(255, 255, 255, 0.1);
			margin-bottom: 1px;
			width: 100%;
			overflow: hidden; /* [FIX] */
		}
		.cf-rew-item div{ float: left; }
			.cf-rew-image{ width: 30px; height: 30px; }
			.cf-rew-value{ width: calc(100% - 80px); padding-left: 5px; padding-top: 6px; }
			.cf-rew-rate{ padding-top: 6px; width: 50px; text-align: right; color: #ff3366; }
	#cf-cost{ text-align: center; background-color: rgba(255, 255, 255, 0.1); color: #fff; border-radius: 6px; }
	.cf-composable{ background-color: #9933ff !important; color: #fff; }
.ChatBox{
	width: 1000px;
	overflow: hidden; /* [FIX] */
}
	.chat-balloon{
		position: absolute;
		width: 123px;
		color: #fff;
		z-index: 1;
	}
	.chat-balloon h4{
		padding: 8px;
		border: 1px solid rgba(255, 255, 255, 0.2);
		border-radius: 12px;
		width: 110px;
		max-height: 100px;
		overflow: hidden;
		background-col
element {
  min-width: 640px;
  zoom: 1;
}
body {
  color: #EEEEEE;
  padding: 0px;

  margin: 0px;

  min-width: 480px;
  font-family: NBGothic, 돋움;
}

    margin
    border
    padding

    ×

    1649.08×0
    static
    box-sizing
    content-box
    display
    block
    float
    none
    line-height
    normal
    position
    static
    z-index
    auto

or: rgba(40, 20, 50, 0.9);
		backdrop-filter: blur(5px);
	}
	.chat-balloon-tip{
		margin: -1px -12px 0px -7px;
		width: 20px;
		height: 20px;
		background-image: url('/img/kkutu/balloontip.png');
		filter: hue-rotate(280deg);
	}
	.chat-balloon-bot{
		margin: -1px -12px 0px 50px;
		width: 20px;
		height: 20px;
		background-image: url('/img/kkutu/balloonbot.png');
		filter: hue-rotate(280deg);
	}
#Chat{
	width: 100%;
	height: 100px;
	overflow-y: scroll;
	background: rgba(0, 0, 0, 0.2);
	border-radius: 12px;
	padding: 5px;
	box-sizing: border-box; /* [FIX] padding이 width를 초과하지 않도록 */
}
#Talk{
	float: left;
	border-right: none;
	border-top-right-radius: 0px;
	border-bottom-right-radius: 0px;
	margin-top: 5px;
	width: calc(101.5% - 82px);
	height: 25px;
	background: rgba(255, 255, 255, 0.1);
	color: #fff;
	border: 1px solid rgba(255, 255, 255, 0.1);
	border-radius: 8px 0 0 8px;
	padding-left: 10px;
	box-sizing: border-box; /* [FIX] */
}
#ChatBtn{
	float: left;
	border-left: none;
	border-top-left-radius: 0px;
	border-bottom-left-radius: 0px;
	margin-top: 5px;
	width: 45px;
	height: 15px;
	background: linear-gradient(135deg, #ff3366, #9933ff);
	color: #fff;
	border: none;
	border-radius: 0 8px 8px 0;
	cursor: pointer;
}
	#Chat hr, #chat-log-board hr{
		padding-top: 0px;
		border: 0px;
		border-bottom: 1px dashed rgba(255, 255, 255, 0.2);
		margin: 2px 0px;
	}
	.chat-item{
		float: left;
		padding: 1px 0px;
		margin: 1px 0px;
		width: 100%;
		overflow: hidden;
	}
	.chat-notice{ background-color: rgba(153, 51, 255, 0.2); }
		.chat-notice .chat-head{ color: #ffb3c6; }
		.chat-stamp{
element {
  min-width: 640px;
  zoom: 1;
}
body {
  color: #EEEEEE;
  padding: 0px;

  margin: 0px;

  min-width: 480px;
  font-family: NBGothic, 돋움;
}

    margin
    border
    padding

    ×

    1649.08×0
    static
    box-sizing
    content-box
    display
    block
    float
    none
    line-height
    normal
    position
    static
    z-index
    auto


			float: left;
			padding-top: 2px;
			width: 70px;
			font-size: 11px;
			text-align: right;
			color: #888;
		}
		.chat-head{
			float: left;
			padding-right: 4px;
			margin-right: 5px;
			width: 90px;
			font-weight: bold;
			text-align: center;
			cursor: pointer;
			color: #ffb3c6;
		}
			.chat-head:hover{ background-color: rgba(255, 255, 255, 0.1); border-radius: 4px; }
		.chat-body{ float: left; width: calc(100% - 190px); min-height: 14px; color: #eee; word-break: break-all; white-space: normal; }
.ADBox{
	width: 1013px;
	box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.5);
	background-color: rgba(15, 5, 25, 0.8) !important;
	border-radius: 12px;
	overflow: hidden; /* [FIX] */
}
.ADBox .product-title{
	border-bottom-color: rgba(255, 255, 255, 0.1);
	color: #ffb3c6;
	background-color: inherit;
}
.ADBox .product-body{
	padding-left: 131px;
}

@keyframes RoundEffect{
	0%		{ font-size: 16px; color: #ff3366; background-color: rgba(0, 0, 0, 1); }
	100%	{ font-size: 12px; color: #FFFFFF; background-color: rgba(0, 0, 0, 0); }
}
@keyframes ReadyBlink{
	0%		{ margin-top: 0px; height: 20px; opacity: 0.8; }
	50%		{ margin-top: -5px; height: 25px; opacity: 1; box-shadow: 0 0 15px #ff3366; }
	100%	{ margin-top: 0px; height: 20px; opacity: 0.8; }
}
@keyframes CurrentBlink{
	0%		{ border-color: #ff3366; box-shadow: 0 0 5px #ff3366; }
	50%		{ border-color: #9933ff; box-shadow: 0 0 15px #9933ff; }
	100%	{ border-color: #ff3366; box-shadow: 0 0 5px #ff3366; }
}
@keyframes FailBlink{
	0%		{ text-decoration: line-through; color: #ff3366; }
	25%		{ text-decoration: inherit; }
	50%		{ text-decoration: line-through; color: #ff3366; }
	75%		{ text-decoration: inherit; }
}
@keyframes ModifiedBlink{
	0%		{ background-color: #ff3366; }
	100%	{ background-color: rgba(255, 255, 255, 0.1); }
}
@keyframes LvUpBlink{
	0%		{ margin-top: 6px; }
	100%	{ margin-top: 1px; }
}
@keyframes ScoreGoing{
	0%		{ margin-top: -80px; font-size: 24px; opacity: 1; color: #ff3366; }
	10%		{ margin-top: -95px; font-size: 36px; opacity: 0.95; color: #ffb3c6; }
	100%	{ margin-top: -25px; font-size: 20px; opacity: 0.1; color: #9933ff; }
}

::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-thumb { background: linear-gradient(to bottom, #ff3366, #9933ff); border-radius: 10px; }
::-webkit-scrollbar-track { background: rgba(0,0,0,0.1); }
/* =========================================================
   통합 오버라이드 (가변 로직 포함 버전)
   ========================================================= */

/* [1] 기본 레이아웃 설정 (대기실/홈 화면) */
#Wrap, #kkutu-wrap {
    width: 1050px !important; /* 대기실 기본 너비 */
    margin: 0 auto;
    position: relative;
    overflow: visible !important;
    border-radius: 30px;
    transition: width 0.3s ease; /* 부드러운 전환 */
}

.MeBox { width: 220px !important; }
.UserListBox { width: 220px !important; }
.UserListBox .product-body, .users-item { width: 210px !important; }

.RoomListBox { width: 790px !important; }
.RoomListBox .product-body { width: 780px !important; height: 330px !important; }

/* 채팅창 기본 (790px) */
.ChatBox {
    width: 790px !important;
    float: left;
    transition: width 0.01s linear;
    box-shadow: none !important;
}

/* [2] 가변 로직: 게임 중일 때 (GameBox가 나타나면 발동) */
/* 게임 중일 때 전체 틀 확장 (1250px~1280px) */
body:has(.GameBox:not([style*="display: none"])) #Wrap,
body:has(.GameBox:not([style*="display: none"])) #kkutu-wrap {
    width: 1280px !important; 
}

/* 게임 중일 때 채팅창 확장 (1012px) */
body:has(.GameBox:not([style*="display: none"])) .ChatBox {
    width: 1012px !important;
}

/* [3] 채팅 내부 입력창 가변 로직 */
#Chat { width: 100% !important; box-sizing: border-box; }

#Talk {
    width: calc(100% - 60px) !important; /* 부모 너비에 따라 자동 조절 */
    height: 25px !important;
    float: left;
}

#ChatBtn {
    width: 50px !important;
    height: 15px !important;
    float: left;
}

/* [4] 버튼 및 디자인 (기존 스타일 보존) */
:root {
    --neon-pink: rgba(255, 51, 102, 0.55);
    --neon-purple: rgba(153, 51, 255, 0.45);
    --btn-grad: linear-gradient(135deg, #ff3366, #9933ff);
}

button, input[type="button"], input[type="submit"] {
    background: var(--btn-grad) !important;
    color: #fff !important;
    border: none !important;
    transition: all .25s cubic-bezier(0.92, 0, 0.25, 1) !important;
    box-shadow: 0 0 10px rgba(255,51,102,.35), 0 0 16px rgba(153,51,255,.25);
}

button:hover {
    filter: brightness(1.12);
    transform: translateY(-1px);
}

/* 메뉴 버튼 스타일 원복 */
#Top .menu-btn { background: transparent !important; color: #ffffff !important; box-shadow: none !important; }
.kkutu-menu button { background-color: rgba(255, 255, 255, 0.2) !important; box-shadow: none !important; }

/* 개별 창 네온 제거 */
.Product, .dialog, .UserListBox, .RoomListBox, .ShopBox, .RoomBox, .GameBox, .MeBox, .ChatBox {
    box-shadow: none !important;
}

/* [5] 전체 외곽 펄스 네온 */
#Wrap::after, #kkutu-wrap::after {
    content: "";
    position: absolute;
    inset: -12px;
    border-radius: 36px;
    border: 2px solid rgba(255, 102, 204, 0.6);
    pointer-events: none;
    z-index: 1;
    animation: OuterNeonPulse 2.2s ease-in-out infinite;
}

@keyframes OuterNeonPulse {
    0%, 100% { opacity: .72; }
    50% { opacity: 1; }
}
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








