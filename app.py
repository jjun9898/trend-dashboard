import streamlit as st
import pandas as pd
import requests
from urllib.parse import quote
from datetime import datetime, timedelta

# --- 1. GS THE FRESH 테마 설정 ---
st.set_page_config(page_title="GS THE FRESH 실시간 트렌드", page_icon="🥬", layout="wide")

# 에러 방지를 위해 괄호로 안전하게 묶은 GS THE FRESH 테마
custom_css = (
    ""
)
st.markdown(custom_css, unsafe_allow_html=True)

# --- 2. 네이버 데이터랩 '식품' 분야 통신 함수 (무거운 크롬 브라우저 대신 직접 통신) ---
@st.cache_data(ttl=3600)
def get_datalab_food_ranking():
    # 네이버 쇼핑인사이트 식품 카테고리 고유 ID = 50000006
    url = "https://datalab.naver.com/shoppingInsight/getCategoryKeywordRank.naver"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://datalab.naver.com/shoppingInsight/sCategory.naver"
    }
    
    # 네이버 데이터랩 통계는 2일 전 데이터가 가장 최신입니다.
    target_date_obj = datetime.now() - timedelta(days=2)
    target_date_str = target_date_obj.strftime("%Y-%m-%d")
    
    payload = {
        "cid": "50000006", 
        "timeUnit": "date",
        "startDate": target_date_str,
        "endDate": target_date_str,
        "page": 1,
        "count": 10
    }
    
    try:
        # 데이터랩 서버에 직접 1~10위 데이터를 요청합니다.
        response = requests.post(url, headers=headers, data=payload, timeout=5)
        data = response.json()
        
        ranking_list = []
        for item in data.get("ranks", []):
            ranking_list.append({
                "순위": item["rank"],
                "키워드": item["keyword"]
            })
            
        date_text = data.get("datetime", target_date_str)
        return pd.DataFrame(ranking_list), date_text
        
    except Exception as e:
        # 실패 시 예외 처리 (이미지 백업본)
        fallback_data = [
            {"순위": 1, "키워드": "오메가3"}, {"순위": 2, "키워드": "학가산김치"},
            {"순위": 3, "키워드": "닭가슴살"}, {"순위": 4, "키워드": "사과"},
            {"순위": 5, "키워드": "쌀20kg"}, {"순위": 6, "키워드": "답례품"},
            {"순위": 7, "키워드": "명가삼대떡집"}, {"순위": 8, "키워드": "젖산마그네슘"},
            {"순위": 9, "키워드": "조선호텔김치"}, {"순위": 10, "키워드": "고구마"}
        ]
        return pd.DataFrame(fallback_data), f"{target_date_str} (통신 지연)"

# --- 3. 메인 대시보드 화면 ---
st.title("🥬 GS THE FRESH 실시간 식품 트렌드 대시보드")
st.markdown("**매장 발주 및 상품 기획**을 위해 네이버 데이터랩에서 1시간마다 가져오는 식품 검색어 랭킹입니다.")

df_ranking, extracted_date = get_datalab_food_ranking()

st.info(f"📅 **네이버 데이터랩 기준일:** {extracted_date}")

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("🏆 네이버 식품 인기 검색어 (Top 10)")
    st.dataframe(df_ranking, hide_index=True, use_container_width=True)
    
    st.markdown("### 🔍 상세 분석 키워드 선택")
    selected_keyword = st.radio(
        "트렌드를 확인할 키워드를 고르세요:", 
        options=df_ranking["키워드"].tolist()
    )

with col2:
    st.subheader(f"💬 '{selected_keyword}' 연관 사이트 및 반응")
    
    # 💡 네이버 블로그 검색 탭으로 바로 넘어가는 전용 링크
    naver_blog_url = f"https://m.search.naver.com/search.naver?where=m_blog&sm=mtb_viw.blog&query={quote(selected_keyword)}"
    google_search_url = f"https://www.google.com/search?q={quote(selected_keyword)}"
    
    st.link_button(f"🟢 네이버 블로그에서 '{selected_keyword}' 리뷰 바로보기", naver_blog_url, use_container_width=True)
    st.markdown("
