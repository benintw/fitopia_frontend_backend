"""
Dashboard page
"""

import streamlit as st

# import plotly.express as px
import pandas as pd


def dashboard_page():
    st.write("write something for dashboard page")
    display_dashboard()


def display_dashboard():
    st.title("Dashboard")

    # Member statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("總會員數", "100")
    with col2:
        st.metric("今日打卡人數", "25")
    with col3:
        st.metric("本月營收", "NT$ 150,000")

    # Example: Monthly check-ins
    chart_data = pd.DataFrame(
        {
            "month": ["Jan", "Feb", "Mar", "Apr", "May"],
            "check_ins": [150, 180, 200, 220, 190],
        }
    )
    # fig = px.line(chart_data, x="month", y="check_ins", title="每月打卡趨勢")
    # st.plotly_chart(fig)
