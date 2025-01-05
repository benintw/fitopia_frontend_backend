"""
變動管理
"""

import streamlit as st
import requests
from utils.api import API_BASE_URL


def update_balance_page():
    """
    變動管理

    1. 透過手機號碼，確認會員存在
    2. 顯示:
        - 會員姓名
        - 會員手機號碼
        - 會員目前點數餘額
        - 會員回饋點數
    3. 輸入:
        - 選擇變動標的: 回饋點數、點數餘額
        - 新增或減少
        - 變動數量
        - 變動原因 # 沒做這個表單

    4. 按下按鈕，更新會員點數餘額
    """

    st.title("變動管理")

    # 1. 透過手機號碼，確認會員存在
    phone_number = st.text_input("請輸入會員手機號碼")
    if st.toggle("查詢"):
        response = requests.get(f"{API_BASE_URL}/members/{phone_number}/")
        if response.status_code == 200:
            member = response.json()
            # st.write(member)

            info_to_show = {
                "姓名": member["mName"],
                "手機號碼": member["mContactNum"],
                "目前點數餘額": member["mBalance"],
                "回饋點數": member["mRewardPoints"],
            }
            st.write("會員資料:")
            st.dataframe(info_to_show, width=500)

            col1, col2 = st.columns(2, gap="large")
            with col1:
                target = st.radio("選擇變動標的", ["回饋點數", "點數餘額"])
                if target == "回饋點數":
                    target_value = member["mRewardPoints"]
                else:
                    target_value = member["mBalance"]

                st.write(f"目前{target}值: {target_value}")

            with col2:
                change_type = st.radio("新增或減少", ["新增", "減少"])
                change_amount = st.number_input("變動數量 (金額)", value=0)

            if change_type == "新增":
                new_value = target_value + change_amount
            else:
                new_value = target_value - change_amount

            st.write(f"新{target}值: {new_value}")

            if target == "回饋點數":
                target_name = "mRewardPoints"
            else:
                target_name = "mBalance"

            if st.button("更新"):
                update_data = {
                    f"{target_name}": new_value,
                }
                response = requests.put(
                    f"{API_BASE_URL}/members/{phone_number}/", json=update_data
                )
                if response.status_code == 200:
                    st.success("更新成功")
                else:
                    st.error("更新失敗")

                # 更新後，顯示會員資料
                response = requests.get(f"{API_BASE_URL}/members/{phone_number}/")
                if response.status_code == 200:
                    member = response.json()
                    st.dataframe(member, width=500)

            st.divider()

        else:
            st.error("會員不存在")
