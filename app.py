import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote

# --- 1. GS THE FRESH 테마 설정 ---
st.set_page_config(page_title="GS THE FRESH 실시간 트렌드", page_icon="🥬", layout="wide")

# 에러 방지를 위해 문자열을 괄호로 안전하게 묶어 CSS를 적용했습니다.
custom_css = (
    ""
)
st.markdown(custom_css, unsafe_allow_html=True)

# --- 2. 실시간 키워드 수집 함수 (서버 충돌 없는 맨 처음 안정적인 방식) ---
@st.cache_data(ttl=600)
def get_google_trending_keywords():
    url = "https://trends.google.com/trending/rss?geo=KR"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        items = root.findall('./channel/item')
        
        data = []
        for item in items:
            title = item.find('title').text if item.find('title') is not None else ""
            traffic_node = item.find('{https://trends.google.com/trending/rss}approx_traffic')
            traffic = traffic_node.text if traffic_node is not None else "N/A"
            
            data.append({
                "키워드": title,
                "예상 검색량": traffic
            })
        return pd.DataFrame(data)
    except Exception as e:
        return pd.DataFrame([{"키워드": "데이터 수집 지연", "예상 검색량": "-"}])

# --- 3. 메인 대시보드 화면 ---
st.title("🥬 GS THE FRESH 실시간 트렌드 대시보드")
st.markdown("**매장 발주 및 상품 기획**을 위해 현재 가장 이슈가 되고 있는 실시간 트렌드입니다.")

df_trends = get_google_trending_keywords()

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("🏆 실시간 급상승 키워드 목록")
    st.dataframe(df_trends, hide_index=True, use_container_width=True)
    
    st.markdown("### 🔍 상세 분석 키워드 선택")
    selected_keyword = st.radio(
        "트렌드를 확인할 키워드를 고르세요:", 
        options=df_trends["키워드"].tolist()
    )

with col2:
    st.subheader(f"💬 '{selected_keyword}' 연관 사이트 및 반응")
    
    # 선택한 키워드의 검색량 표시
    try:
        traffic_val = df_trends[df_trends['키워드'] == selected_keyword]['예상 검색량'].values[0]
        st.metric(label="예상 검색량", value=f"{traffic_val}+")
    except:
        pass
    
    # 💡 네이버 블로그 검색 탭으로 바로 넘어가는 전용 링크
    naver_blog_url = f"https://m.search.naver.com/search.naver?where=m_blog&sm=mtb_viw.blog&query={quote(selected_keyword)}"
    google_search_url = f"https://www.google.com/search?q={quote(selected_keyword)}"
    
    btn_c1, btn_c2 = st.columns(2)
    with btn_c1:
        st.link_button("🟢 네이버 블로그 검색 바로가기", naver_blog_url, use_container_width=True)
    with btn_c2:
        st.link_button("🔵 구글 검색 결과 바로가기", google_search_url, use_container_width=True)
        
    st.markdown("---")
    st.info("💡 위의 초록색 버튼을 누르시면, 선택한 트렌드 상품에 대해 고객들이 남긴 최신 네이버 블로그 포스팅과 리뷰를 즉시 확인하실 수 있습니다.")
