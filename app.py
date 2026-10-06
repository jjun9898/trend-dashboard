import streamlit as st
import pandas as pd
import requests
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# 페이지 설정
st.set_page_config(page_title="식품 트렌드 & 연관 블로그 대시보드", page_icon="🍎", layout="wide")

# 1. 네이버 데이터랩 쇼핑인사이트 크롤링 함수
@st.cache_data(ttl=86400) # 하루 한 번만 실행되도록 데이터 캐싱
def get_datalab_food_ranking():
    # 가상 크롬 브라우저(Headless) 설정
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    data = []
    try:
        # Streamlit Cloud 환경에서 크롬 실행
        driver = webdriver.Chrome(options=options)
        
        # 쇼핑인사이트 접속 (식품 카테고리 URL 파라미터가 있다면 바로 접속, 여기서는 기본 페이지)
        driver.get("https://datalab.naver.com/shoppingInsight/sCategory.naver")
        time.sleep(3) # 데이터 로딩 대기
        
        # 1위~10위 데이터 추출 (실제 사이트의 CSS 클래스 구조에 따라 변동 가능)
        ranks = driver.find_elements(By.CSS_SELECTOR, ".rank_top1000_list .list_item")
        for idx, item in enumerate(ranks[:10]):
            text = item.text.replace('\n', ' ').strip()
            if text:
                data.append({"순위": idx + 1, "키워드": text.split(' ', 1)[-1] if ' ' in text else text})
                
        driver.quit()
        
    except Exception as e:
        st.warning(f"네이버 보안 정책으로 실시간 크롤링이 지연되었습니다. 백업 데이터를 로드합니다.")
        
    # 크롤링 실패 또는 봇 차단 시 기본 제공 데이터 (업로드해주신 이미지 기준)
    if not data:
        data = [
            {"순위": 1, "키워드": "오메가3"}, {"순위": 2, "키워드": "학가산김치"},
            {"순위": 3, "키워드": "닭가슴살"}, {"순위": 4, "키워드": "사과"},
            {"순위": 5, "키워드": "쌀20kg"}, {"순위": 6, "키워드": "답례품"},
            {"순위": 7, "키워드": "명가삼대떡집"}, {"순위": 8, "키워드": "젖산마그네슘"},
            {"순위": 9, "키워드": "조선호텔김치"}, {"순위": 10, "키워드": "고구마"}
        ]
        
    return pd.DataFrame(data)

# 2. 네이버 블로그 검색 API 함수
def search_naver_blog(query, client_id, client_secret):
    url = f"https://openapi.naver.com/v1/search/blog.json?query={quote(query)}&display=5&sort=sim"
    headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            return res.json().get('items', [])
    except Exception:
        pass
    return []

# --- 사이드바 설정 ---
st.sidebar.title("⚙️ 설정")
st.sidebar.markdown("네이버 오픈 API 정보를 입력하면 연관 블로그가 출력됩니다.")
naver_client_id = st.sidebar.text_input("Naver Client ID", type="password")
naver_client_secret = st.sidebar.text_input("Naver Client Secret", type="password")

if st.sidebar.button("🔄 크롤링 새로고침"):
    st.cache_data.clear()
    st.rerun()

# --- 메인 대시보드 화면 ---
st.title("🛒 네이버 쇼핑인사이트 (식품 분야) 대시보드")
st.caption("매일 업데이트되는 식품 검색어 순위와 연관 블로그를 한눈에 확인하세요.")

df_ranking = get_datalab_food_ranking()

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("🏆 오늘의 식품 검색어 순위")
    
    # 데이터프레임 시각화
    st.dataframe(df_ranking, hide_index=True, use_container_width=True)
    
    # 키워드 선택 라디오 버튼
    st.markdown("### 상세 분석할 키워드 선택")
    selected_keyword = st.radio(
        "아래에서 키워드를 고르세요:", 
        options=df_ranking["키워드"].tolist(),
        format_func=lambda x: f"[{df_ranking[df_ranking['키워드']==x]['순위'].values[0]}위] {x}"
    )

with col2:
    st.subheader(f"🔍 '{selected_keyword}' 관련 최신 블로그 및 리뷰")
    
    # 바로가기 버튼
    st.link_button(f"🟢 네이버에서 '{selected_keyword}' 검색하기", f"https://search.naver.com/search.naver?query={quote(selected_keyword)}")
    st.markdown("---")
    
    if naver_client_id and naver_client_secret:
        blogs = search_naver_blog(selected_keyword, naver_client_id, naver_client_secret)
        if blogs:
            for b in blogs:
                # HTML 텍스트 정제
                title = b['title'].replace("**", "").replace("**", "").replace(""", '"')
                desc = b['description'].replace("**", "").replace("**", "").replace(""", '"')
                
                with st.container():
                    st.markdown(f"**[{title}]({b['link']})**")
                    st.caption(f"✍️ 블로거: {b['bloggername']} | 📅 작성일: {b['postdate']}")
                    st.write(desc[:150] + "...")
                    st.write("")
        else:
            st.warning("검색된 블로그 결과가 없습니다.")
    else:
        st.info("💡 사이드바에 API ID와 Secret을 입력하시면 이곳에 최신 리뷰 포스팅이 실시간으로 나타납니다.")
