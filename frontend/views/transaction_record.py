"""
交易紀錄
"""

import streamlit as st
import requests
from utils.api import API_BASE_URL


def create_transaction(transaction_data: dict) -> bool:
    try:
        response = requests.post(
            f"{API_BASE_URL}/transaction_records/", json=transaction_data
        )
        return response.status_code == 200
    except Exception as e:
        st.error(f"無法建立交易紀錄: {e}")
        return False


def get_transaction_records():
    response = requests.get(f"{API_BASE_URL}/transaction_records/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("無法取得交易紀錄")
        return None


def get_transaction_of_member(member_id: int):
    """取得某會員的交易紀錄"""
    # 確認會員手機存在

    # 如果會員存在，取得交易紀錄
    response = requests.get(f"{API_BASE_URL}/transaction_records/{member_id}")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("無法取得交易紀錄")
        return None


def transaction_records_page():
    st.title("交易紀錄")
    # Add transaction viewing and processing
    st.write("write something for transaction records page")

    transaction_records = get_transaction_records()
    st.dataframe(transaction_records)
