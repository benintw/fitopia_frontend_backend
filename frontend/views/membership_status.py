"""
會員會籍狀態
"""

import streamlit as st
import pandas as pd
import requests
from views.member import search_member

from utils.api import API_BASE_URL
from typing import Optional, TypedDict


class MembershipStatus(TypedDict):
    sId: int
    mContactNum: str
    startDate: str
    endDate: str
    isActive: bool


def create_membership_status(membership_data: dict) -> bool:
    """建立會籍狀態

    Args:
        membership_data (dict): The membership status data to create
            {
                "mContactNum": str,
                "startDate": str,
                "endDate": str,
                "isActive": bool
            }

    Returns:
        bool: True if successful, False if failed
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/membership_status/", json=membership_data
        )
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        return False


def get_membership_status(mContactNum: str) -> Optional[MembershipStatus]:
    """取得會籍狀態"""
    response = requests.get(f"{API_BASE_URL}/membership_status/{mContactNum}")
    if response.status_code == 200:
        return response.json()
    else:
        st.warning("該會員目前沒有, 有效會籍")
        return None


def membership_status_page():
    """
    會籍狀態的查詢

    1. 輸入會員手機號碼
    2. 確認會員存在
    3. 查詢會籍狀態
    4. 顯示會籍狀態
    """
    st.write("membership_status.py")
    st.title("會員會籍狀態查詢")

    # 1. 輸入會員手機號碼
    phone_number = st.text_input("請輸入會員手機號碼")

    col1, col2 = st.columns(2)
    with col1:
        # 2. 確認會員存在
        member = search_member(phone_number)
        if member is not None and not isinstance(member, list):
            st.subheader("會員資料:")
            st.dataframe(member, column_config=None, width=400)

            with col2:
                # 3. 查詢會籍狀態
                st.subheader("會籍狀態:")
                membership_status = get_membership_status(member["mContactNum"])
                if membership_status is not None:
                    # 4. 顯示會籍狀態
                    status_df = pd.DataFrame(
                        {
                            "會籍編號": [membership_status.get("sId", "")],
                            "會員號碼": [membership_status.get("mContactNum", "")],
                            "開始日期": [membership_status.get("startDate", "")],
                            "結束日期": [membership_status.get("endDate", "")],
                            "是否有效": [membership_status.get("isActive", "")],
                        }
                    )
                    # Display table
                    st.dataframe(status_df, hide_index=True, use_container_width=True)

        else:
            return
