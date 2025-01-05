"""
打卡紀錄
"""

import streamlit as st
import requests
from utils.api import API_BASE_URL
import pandas as pd
from datetime import datetime


def get_today_checkin_records():
    selected_date = datetime.now().date()
    checkin_records = get_all_checkin_records()
    df = pd.DataFrame(checkin_records)
    if checkin_records:
        df["checkInDatetime"] = pd.to_datetime(df["checkInDatetime"])
        df["checkInDatetime"] = pd.to_datetime(
            df["checkInDatetime"], format="mixed"
        ).dt.tz_localize("Asia/Taipei")
        df["checkInDate"] = df["checkInDatetime"].apply(lambda x: x.date())
        df_filtered = df.query("checkInDate == @selected_date")

        return df_filtered
    else:
        return []


def display_hourly_stats(df_filetered):
    st.subheader("每小時入場統計")
    hourly_stats = df_filetered["checkInDatetime"].dt.hour.value_counts().sort_index()
    st.bar_chart(hourly_stats)


def display_tab1_stats(df_filtered):
    if not df_filtered.empty:
        display_hourly_stats(df_filtered)
    else:
        st.warning("所選日期無打卡記錄")


def create_checkin_record(mContactNum: str) -> bool:
    """
    快速打卡
    """
    data = {"mContactNum": mContactNum}
    response = requests.post(f"{API_BASE_URL}/checkinrecord/", json=data)
    st.write(response.json())
    return response.status_code == 200


def get_member_checkin_record(mContactNum: str):
    """
    取得會員打卡記錄
    response = requests.get(f"{API_BASE_URL}/checkinrecord")
    """
    st.write("取得會員打卡記錄")
    response = requests.get(f"{API_BASE_URL}/checkinrecord/{mContactNum}")

    if response.status_code == 200:
        return response.json()
    else:
        return []


def get_all_checkin_records():
    """
    取得所有打卡記錄
    response = requests.get(f"{API_BASE_URL}/checkinrecord")
    """
    response = requests.get(f"{API_BASE_URL}/checkinrecord")

    if response.status_code == 200:
        return response.json()

    return []


def update_member_checkin_record(mContactNum: str):
    """
    更新會員打卡記錄
    response = requests.put(f"{API_BASE_URL}/checkinrecord", json={"mContactNum": mContactNum})
    """
    st.write("更新會員打卡記錄-出場")

    response = requests.put(f"{API_BASE_URL}/checkinrecord/{mContactNum}")
    st.write(response)
    if response.status_code == 200:
        st.success("出場打卡成功")
    elif response.status_code == 500:
        st.error("出場打卡失敗")
    else:
        st.error("無法出場打卡")


def checkin_record_page():
    st.title("打卡記錄")

    st.divider()
    st.subheader("模擬入場/出場")
    col1, col2 = st.columns(2)

    with col1:
        st.info("入場")
        contact_number = st.text_input("請輸入會員聯絡電話", key="simulate_checkin_in")
        if st.button("入場"):
            if contact_number:
                if create_checkin_record(contact_number):
                    st.success("入場打卡成功")
                else:
                    st.error("無法入場打卡")
    with col2:
        st.info("出場")
        contact_number = st.text_input("請輸入會員聯絡電話", key="simulate_checkin_out")

        if st.button("出場"):
            if contact_number:
                update_member_checkin_record(contact_number)

    st.divider()
    tab1, tab2, tab3 = st.tabs(["今日打卡紀錄", "所有打卡紀錄", "特定會員打卡紀錄"])

    with tab1:
        st.subheader("今日打卡紀錄")

        selected_date = st.date_input("選擇日期", value=pd.Timestamp.now())

        if st.button("重新整理", key="refresh_today_checkin_record"):

            checkin_records = get_all_checkin_records()
            if checkin_records:
                df = pd.DataFrame(checkin_records)

                # st.dataframe(df)  # correct dates times

                df["checkInDatetime"] = pd.to_datetime(df["checkInDatetime"])

                # Convert string to datetime
                df["checkInDatetime"] = pd.to_datetime(
                    df["checkInDatetime"], format="mixed"
                ).dt.tz_localize("Asia/Taipei")

                # Convert timestamps to dates for filtering
                df["checkInDate"] = df["checkInDatetime"].apply(lambda x: x.date())
                # Filter records using query
                df_filtered = df.query("checkInDate == @selected_date")

                if not df_filtered.empty:
                    st.write(f"找到 {len(df_filtered)} 筆 {selected_date} 的打卡記錄")
                    st.dataframe(df_filtered)

                    # Make sure checkInDatetime is in datetime format
                    df_filtered["checkInDatetime"] = pd.to_datetime(
                        df_filtered["checkInDatetime"], format="mixed"
                    )
                    df_filtered["checkOutDatetime"] = pd.to_datetime(
                        df_filtered["checkOutDatetime"], format="mixed"
                    )

                    # 顯示每小時的入場統計
                    st.subheader("每小時入場統計")
                    hourly_stats = (
                        df_filtered["checkInDatetime"]
                        .dt.hour.value_counts()
                        .sort_index()
                    )
                    st.bar_chart(hourly_stats)

                else:
                    st.warning(f"所選日期 {selected_date} 無打卡記錄")
            else:
                st.error("無法取得打卡紀錄")

    with tab2:
        st.subheader("所有打卡紀錄")
        if st.button("重新整理", key="refresh_all_checkin_record"):
            checkin_records = get_all_checkin_records()
            if checkin_records:
                df = pd.DataFrame(checkin_records)
                st.dataframe(df)
            else:
                st.error("無法取得打卡紀錄")

    with tab3:
        st.subheader("特定會員打卡紀錄")
        contact_number = st.text_input(
            "請輸入會員聯絡電話", key="specific_checkin_record"
        )
        if st.button("取得"):
            checkin_records = get_member_checkin_record(contact_number)
            if checkin_records:
                df = pd.DataFrame(checkin_records)
                st.dataframe(df)
            else:
                st.error("無法取得打卡紀錄")
