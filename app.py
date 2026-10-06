import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote

# 페이지 기본 설정
st.set_page_config(
    page_title="실시간 트렌드 & 네이버 연관 검색 대시보드",
    page_icon="📈",
    layout="wide"
)

# -------------------------------------------------------------------
# 1. Google Trends RSS 실시간 키워드 수집 함수
# -------------------------------------------------------------------
@st.cache_data(ttl=600)  # 10분간 데이터 캐싱
def get_google_trending_keywords(geo="KR"):
    url = f"https://trends.google.com/trending/rss?geo={geo}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        items = root.findall('./channel/item')
        
        data = []
        for item in items:
            title = item.find('title').text if item.find('title') is not None else ""
            
            # 구글 트렌드 RSS 전용 네임스페이스 수집
            traffic_node = item.find('{https://trends.google.com/trending/rss}approx_traffic')
            traffic = traffic_node.text if traffic_node is not None else "N/A"
            
            news_items = item.findall('{https://trends.google.com/trending/rss}news_item')
            news_list = []
            for news in news_items:
                n_title = news.find('{https://trends.google.com/trending/rss}news_item_title')
                n_url = news.find('{https://trends.google.com/trending/rss}news_item_url')
                if n_title is not None and n_url is not None:
                    news_list.append({"title": n_title.text, "url": n_url.text})
            
            data.append({
                "키워드": title,
                "예상 검색량": traffic,
                "관련 뉴스": news_list
            })
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"구글 트렌드 수집 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

# -------------------------------------------------------------------
# 2. 네이버 검색 API 호출 함수 (API 키가 입력되었을 경우)
# -------------------------------------------------------------------
def search_naver_blog(query, client_id, client_secret):
    url = f"https://openapi.naver.com/v1/search/blog.json?query={quote(query)}&display=5&sort=sim"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            return res.json().get('items', [])
    except Exception:
        pass
    return []

# -------------------------------------------------------------------
# 3. 사이드바 (설정 및 네이버 API 키 입력)
# -------------------------------------------------------------------
st.sidebar.title("⚙️ 설정")
geo = st.sidebar.selectbox("국가 선택", ["KR (한국)", "US (미국)", "JP (일본)"], index=0)
geo_code = geo.split()[0]

st.sidebar.markdown("---")
st.sidebar.subheader("🔑 네이버 Open API (선택)")
naver_client_id = st.sidebar.text_input("Client ID", type="password")
naver_client_secret = st.sidebar.text_input("Client Secret", type="password")

if st.sidebar.button("🔄 데이터 새로고침"):
    st.cache_data.clear()
    st.rerun()

# -------------------------------------------------------------------
# 4. 메인 대시보드 화면
# -------------------------------------------------------------------
st.title("🔥 실시간 급상승 키워드 대시보드")
st.caption("Google Trends RSS 기반 실시간 키워드 및 연관 검색 정보")

df_trends = get_google_trending_keywords(geo=geo_code)

if df_trends.empty:
    st.warning("수집된 키워드 데이터가 없습니다.")
else:
    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.subheader("📌 실시간 급상승 키워드 목록")
        
        # 키워드 선택 radio
        selected_keyword = st.radio(
            "상세 정보를 볼 키워드를 선택하세요:",
            options=df_trends["키워드"].tolist(),
            format_func=lambda x: f"{x} ({df_trends[df_trends['키워드'] == x]['예상 검색량'].values[0]}+)"
        )

    with col2:
        st.subheader(f"🔍 '{selected_keyword}' 상세 및 연관 사이트")
        
        # 선택한 키워드의 정보 가져오기
        selected_row = df_trends[df_trends["키워드"] == selected_keyword].iloc[0]
        
        st.metric(label="예상 검색량", value=f"{selected_row['예상 검색량']}+")
        
        # 바로가기 링크 버튼
        naver_search_url = f"https://search.naver.com/search.naver?query={quote(selected_keyword)}"
        google_search_url = f"https://www.google.com/search?q={quote(selected_keyword)}"
        
        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            st.link_button("🟢 네이버 검색 결과 바로가기", naver_search_url, use_container_width=True)
        with btn_c2:
            st.link_button("🔵 구글 검색 결과 바로가기", google_search_url, use_container_width=True)

        st.markdown("---")

        # 네이버 API 연동 여부에 따른 블로그 검색 결과 표시
        if naver_client_id and naver_client_secret:
            st.markdown("### 📝 네이버 최신 블로그 글")
            blogs = search_naver_blog(selected_keyword, naver_client_id, naver_client_secret)
            if blogs:
                for b in blogs:
                    # HTML 태그 제거 처리 간단 적용
                    clean_title = b['title'].replace("<b>", "").replace("</b>", "").replace("&quot;", '"')
                    clean_desc = b['description'].replace("<b>", "").replace("</b>", "").replace("&quot;", '"')
                    
                    with st.container():
                        st.markdown(f"**[{clean_title}]({b['link']})**")
                        st.caption(f"블로그명: {b['bloggername']} | 작성일: {b['postdate']}")
                        st.text(clean_desc[:120] + "...")
                        st.write("")
            else:
                st.info("네이버 블로그 검색 결과가 없거나 API 인증에 실패했습니다.")
        else:
            st.info("💡 사이드바에 **네이버 API Key**를 입력하면 연관 블로그 검색 글이 실시간으로 표시됩니다.")

        # 구글 트렌드 연관 수집 뉴스
        st.markdown("### 📰 관련 주요 뉴스")
        news_items = selected_row["관련 뉴스"]
        if news_items:
            for n in news_items:
                st.markdown(f"- [{n['title']}]({n['url']})")
        else:
            st.text("관련 뉴스가 없습니다.")
