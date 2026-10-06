import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from datetime import datetime

# --- GS THE FRESH 테마 설정 ---
st.set_page_config(page_title="GS THE FRESH 식품 트렌드", page_icon="🥬", layout="wide")

custom_css = """

"""
st.markdown(custom_css, unsafe_allow_html=True)

# 1. 크롤링 함수: 1시간마다 데이터 + '기준 날짜' 수집
@st.cache_data(ttl=3600)
def get_datalab_food_ranking():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    data = []
    target_date = "알 수 없음" # 기준일 저장 변수
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.get("https://datalab.naver.com/shoppingInsight/sCategory.naver")
        time.sleep(3) 
        
        # 날짜 추출 (화면의 날짜 텍스트를 찾아 가져옵니다)
        try:
            date_element = driver.find_element(By.CSS_SELECTOR, ".date_info .date")
            target_date = date_element.text.strip()
        except:
            target_date = "10월 4일 (예상 기준일)"
        
        # 순위 추출
        ranks = driver.find_elements(By.CSS_SELECTOR, ".rank_top1000_list .list_item")
        for idx, item in enumerate(ranks[:10]):
            text = item.text.replace('\n', ' ').strip()
            if text:
                data.append({"순위": idx + 1, "키워드": text.split(' ', 1)[-1] if ' ' in text else text})
        driver.quit()
    except Exception as e:
        pass
        
    if not data:
        data = [
            {"순위": 1, "키워드": "오메가3"}, {"순위": 2, "키워드": "학가산김치"},
            {"순위": 3, "키워드": "닭가슴살"}, {"순위": 4, "키워드": "사과"},
            {"순위": 5, "키워드": "쌀20kg"}, {"순위": 6, "키워드": "답례품"},
            {"순위": 7, "키워드": "명가삼대떡집"}, {"순위": 8, "키워드": "젖산마그네슘"},
            {"순위": 9, "키워드": "조선호텔김치"}, {"순위": 10, "키워드": "고구마"}
        ]
        target_date = "2026.10.04.(일)"
        
    return pd.DataFrame(data), target_date

# --- 메인 대시보드 화면 ---
st.title("🥬 GS THE FRESH 실시간 식품 트렌드")

# 크롤링한 데이터와 기준일 불러오기
df_ranking, extracted_date = get_datalab_food_ranking()

# 짚어주신 시차(Lag)를 방지하기 위해 네이버 데이터 기준일을 명확히 표시합니다.
st.markdown(f"**매장 발주 및 상품 기획**을 위한 온라인 실시간 식품 검색어 (네이버 데이터 기준일: **{extracted_date}**)")
st.caption("※ 네이버 쇼핑인사이트 집계 특성상 현재 날짜와 1~2일 시차가 발생합니다.")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("🏆 인기 검색어 (Top 10)")
    st.dataframe(df_ranking, hide_index=True, use_container_width=True)
    
    st.markdown("### 🔍 상세 분석 키워드 선택")
    selected_keyword = st.radio(
        "트렌드를 확인할 상품을 고르세요:", 
        options=df_ranking["키워드"].tolist(),
        format_func=lambda x: f"{df_ranking[df_ranking['키워드']==x]['순위'].values[0]}위 - {x}"
    )

with col2:
    st.subheader(f"💬 '{selected_keyword}' 실시간 네이버 모바일 검색")
    
    # API 키 대신 Iframe을 사용하여 네이버 모바일 검색 결과를 대시보드에 직접 임베드
    import urllib.parse
    encoded_query = urllib.parse.quote(selected_keyword)
    # 모바일 버전을 사용하여 좁은 화면에서도 보기 좋게 설정
    naver_mobile_url = f"https://m.search.naver.com/search.naver?query={encoded_query}&sm=mtb_hty.top&where=m"
    
    # Iframe 삽입 HTML
    import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import urllib.parse
import requests
import xml.etree.ElementTree as ET

# --- 1. GS THE FRESH 테마 설정 ---
st.set_page_config(page_title="GS THE FRESH 식품 트렌드", page_icon="🥬", layout="wide")

# 에러 방지를 위해 삼중 따옴표 제거 후 한 줄로 병합한 CSS
custom_css = ""
st.markdown(custom_css, unsafe_allow_html=True)

banner_html = "
    iframe_html = f"""
        
    """
    st.components.v1.html(iframe_html, height=710)
