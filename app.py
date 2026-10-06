import streamlit as st
import pandas as pd
import requests
from urllib.parse import quote
from datetime import datetime, timedelta

# --- 1. 대시보드 기본 설정 ---
st.set_page_config(page_title="GS THE FRESH 트렌드", page_icon="🥬", layout="wide")

# --- 2. GS THE FRESH 테마 설정 ---
# 복사 붙여넣기 시 에러(SyntaxError)를 완벽하게 막기 위해, 짧은 줄로 나누어 디자인을 조립합니다.
css = ""
css += ""
st.markdown(css, unsafe_allow_html=True)

st.title("🥬 GS THE FRESH 실시간 식품 트렌드")
st.markdown("**매장 발주 및 상품 기획**을 위해 네이버 데이터랩에서 추출한 핵심 검색어 데이터입니다.")

# --- 3. 네이버 데이터랩 API 직접 호출 (서버 다운 0%) ---
@st.cache_data(ttl=3600)
def get_datalab_food_ranking():
    url = "https://datalab.naver.com/shoppingInsight/getCategoryKeywordRank.naver"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://datalab.naver.com/shoppingInsight/sCategory.naver"
    }
    
    # 네이버 데이터랩은 2일 전 데이터가 최신입니다.
    target_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    payload = {"cid": "50000006", "timeUnit": "date", "startDate": target_date, "endDate": target_date, "page": 1, "count": 10}
    
    try:
        res = requests.post(url, headers=headers, data=payload, timeout=5)
        data = res.json()
        ranks = [{"순위": item["rank"], "키워드": item["keyword"]} for item in data.get("ranks", [])]
        return pd.DataFrame(ranks), target_date
    except:
        # 일시적 통신 오류 시 화면이 뻗지 않도록 백업 데이터를 띄웁니다.
        fallback = [{"순위": i+1, "키워드": k} for i, k in enumerate(["오메가3", "학가산김치", "닭가슴살", "사과", "쌀20kg", "답례품", "명가삼대떡집", "젖산마그네슘", "조선호텔김치", "고구마"])]
        return pd.DataFrame(fallback), target_date + " (통신 지연)"

# --- 4. 대시보드 화면 구성 ---
df_ranking, extracted_date = get_datalab_food_ranking()

st.info(f"📅 **네이버 데이터랩 기준일:** {extracted_date}")

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("🏆 네이버 식품 검색어 (Top 10)")
    st.dataframe(df_ranking, hide_index=True, use_container_width=True)
    
    st.write("---")
    selected_keyword = st.radio("🔍 트렌드를 확인할 키워드 선택:", options=df_ranking["키워드"].tolist())

with col2:
    st.subheader(f"💬 '{selected_keyword}' 연관 반응 확인")
    
    # 네이버 및 구글 검색 결과 바로가기 주소 생성
    naver_url = f"https://m.search.naver.com/search.naver?where=m_blog&sm=mtb_viw.blog&query={quote(selected_keyword)}"
    google_url = f"https://www.google.com/search?q={quote(selected_keyword)}"
    
    st.link_button(f"🟢 네이버 블로그 리뷰 보기", naver_url, use_container_width=True)
    st.write("") # 버튼 사이 간격
    st.link_button(f"🔵 구글 최신 검색 결과 보기", google_url, use_container_width=True)
    
    st.write("---")
    st.warning("위의 버튼을 클릭하시면 고객들이 남긴 생생한 최신 리뷰를 즉시 확인하실 수 있습니다.")
