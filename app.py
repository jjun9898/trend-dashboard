import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import urllib.parse
import requests
import xml.etree.ElementTree as ET

# --- 1. GS THE FRESH 전용 페이지 및 테마 설정 ---
st.set_page_config(page_title="GS THE FRESH 식품 트렌드 대시보드", page_icon="🛒", layout="wide")

custom_css = """

"""
st.markdown(custom_css, unsafe_allow_html=True)

st.markdown("""
