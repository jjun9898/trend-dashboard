import streamlit as st
import pandas as pd
import urllib.parse
import requests
import xml.etree.ElementTree as ET

# --- 1. 기본 설정 및 테마 ---
st.set_page_config(page_title="GS THE FRESH 식품 트렌드", page_icon="🥬", layout="wide")

# 줄바꿈 에러가 절대 나지 않는 가장 안전한 방식의 디자인 코드
st.markdown("", unsafe_allow_html=True)
st.markdown("
