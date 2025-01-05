"""Home page component"""

import streamlit as st
import pandas as pd
from datetime import datetime

from views.member import view_all_members
from views.checkin_record import get_today_checkin_records


def home_page():
    st.title("歡迎來到 FITOPIA 健身房管理系統")
    st.subheader(f"🗓️ {datetime.now().strftime('%Y-%m-%d')}")
    st.write("-" * 30)
    display_dashboard()


def display_dashboard():
    st.subheader("📊 Dashboard")

    # Member statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        all_members = view_all_members()
        if all_members is not None:
            st.metric("總會員數", all_members.shape[0])
        else:
            st.metric("總會員數", "0")
    with col2:
        df_filtered = get_today_checkin_records()
        st.metric("今日入場人數", len(df_filtered))
    with col3:
        st.metric("本月訂單總額", "NT$ 500,000")

    st.divider()
    col4, col5 = st.columns(2)
    with col4:
        st.metric("當日現金收入", "NT$ 100,000")
        st.metric("當日信用卡收入", "NT$ 150,000")
        st.metric("當日轉帳收入", "NT$ 50,000")
    with col5:
        st.metric("當日總營收", "NT$ 300,000")

    st.divider()

    st.subheader("🔍 本月尖峰入場時間")
    st.metric("尖峰入場時間", "10:00 - 12:00")
    st.metric("尖峰入場平均人數", "300 人")

    st.divider()
    st.subheader("🔍 歷年總營收查詢")
    st.warning("此功能尚未開發")
