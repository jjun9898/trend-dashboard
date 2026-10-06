import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import urllib.parse

# --- 1. GS THE FRESH 전용 페이지 및 테마 설정 ---
st.set_page_config(page_title="GS THE FRESH 식품 트렌드 대시보드", page_icon="🛒", layout="wide")

# GS THE FRESH 브랜드 컬러를 활용한 커스텀 CSS
custom_css = """

"""
st.markdown(custom_css, unsafe_allow_html=True)

# 상단 간판(배너) 출력
st.markdown("""
