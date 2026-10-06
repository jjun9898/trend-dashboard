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
