"""Member management page component"""

import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from typing import Optional

from utils.api import API_BASE_URL


def view_all_members() -> Optional[pd.DataFrame]:
    """查看所有會員"""
    response = requests.get(f"{API_BASE_URL}/members/")
    if response.status_code == 200:
        members = response.json()
        df = pd.DataFrame(members)
        return df
    else:
        return None


def create_member() -> bool:
    """新增會員

    新增會員資料

    Return:
        bool: 是否新增成功

    """

    with st.form("new_member_form", clear_on_submit=True, border=True):
        name = st.text_input("姓名")
        contact_number = st.text_input("聯絡電話")
        email = st.text_input("電子郵件")
        dob = st.date_input("出生日期", min_value=datetime(1900, 1, 1))
        emergency_contact_name = st.text_input("緊急聯絡人姓名")
        emergency_contact_number = st.text_input("緊急聯絡人電話")
        balance = st.number_input("餘額", value=0)
        reward_points = st.number_input("紅利點數", value=100)

        if st.form_submit_button("新增會員"):
            data = {
                "mName": name,
                "mContactNum": contact_number,
                "mEmail": email,
                "mDob": dob.strftime("%Y-%m-%d"),
                "mEmergencyName": emergency_contact_name,
                "mEmergencyNum": emergency_contact_number,
                "mBalance": balance,
                "mRewardPoints": reward_points,
            }

            response = requests.post(f"{API_BASE_URL}/members", json=data)
            print(response.json())

            return response.status_code == 200

        return False


def search_member(mContactNum: str) -> Optional[dict]:
    """搜尋會員

    1. 如果會員不存在，則回傳 None
    2. 如果手機號碼為空，則回傳 None
    3. 如果會員存在，則回傳會員資料

    """

    if mContactNum == "":
        st.warning("請輸入會員手機號碼")
        return

    response = requests.get(f"{API_BASE_URL}/members/{mContactNum}")
    if response.status_code == 200:
        member = response.json()
        return member
    else:
        return


def update_member(search_term: str):
    """更新會員基本資料

    1. 先收尋會員，確認該會員存在
    2. 更新會員資料
    """
    # 先收尋會員，確認該會員存在
    if st.toggle("搜尋", key="update_member_search_button"):
        member = search_member(search_term)
        if member is not None:
            st.write("找到以下會員:")
            st.dataframe(member, column_config=None, width=400)

            # 更新會員資料
            with st.form("update_member_form", clear_on_submit=True, border=True):
                name = st.text_input("姓名", value=member["mName"])
                contact_number = st.text_input(
                    "聯絡電話 (不可修改)", value=member["mContactNum"]
                )
                email = st.text_input("電子郵件", value=member["mEmail"])
                dob = st.date_input("出生日期 (不可修改)", value=member["mDob"])
                emergency_contact_name = st.text_input(
                    "緊急聯絡人姓名", value=member["mEmergencyName"]
                )
                emergency_contact_number = st.text_input(
                    "緊急聯絡人電話", value=member["mEmergencyNum"]
                )
                balance = st.number_input("餘額", value=member["mBalance"])
                reward_points = st.number_input(
                    "紅利點數", value=member["mRewardPoints"]
                )

                if st.form_submit_button("更新會員資料"):
                    data = {
                        "mName": name,
                        "mContactNum": contact_number,
                        "mEmail": email,
                        "mDob": dob.strftime("%Y-%m-%d"),
                        "mEmergencyName": emergency_contact_name,
                        "mEmergencyNum": emergency_contact_number,
                        "mBalance": balance,
                        "mRewardPoints": reward_points,
                    }

                    response = requests.put(
                        f"{API_BASE_URL}/members/{search_term}", json=data
                    )
                    if response.status_code == 200:
                        st.success("會員資料更新成功")
                        st.success("重新整理頁面")
                    else:
                        st.error("無法更新會員資料")

        else:
            st.error("會員不存在")


def member_management_page():
    st.title("會員管理")
    tab1, tab2, tab3, tab4 = st.tabs(
        ["會員列表", "新增會員", "收尋會員", "更新會員資料"]
    )

    with tab1:
        """會員列表"""
        if st.button("重新整理會員列表"):
            all_members = view_all_members()

            if all_members is not None:
                st.dataframe(all_members, column_config=None)
            else:
                st.error("無法取得會員列表")

    with tab2:
        """新增會員"""
        if create_member():
            st.success("會員新增成功")
        else:
            st.warning("會員新增失敗: 資料輸入錯誤")

    with tab3:
        """收尋會員"""
        search_term = st.text_input(
            "請輸入會員聯絡電話", key="search_member_search_term"
        )
        member = search_member(search_term)
        if member is not None:
            st.dataframe(member, column_config=None, width=400)

    with tab4:
        """更新會員基本資料"""
        search_term = st.text_input(
            "請輸入會員聯絡電話", key="update_member_search_term"
        )
        update_member(search_term)
