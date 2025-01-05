"""
商品購買
"""

import streamlit as st
import requests
from utils.api import API_BASE_URL
from typing import Optional


def show_all_products() -> Optional[list]:
    response = requests.get(f"{API_BASE_URL}/products/")
    if response.status_code == 200:
        # st.write(response.json())
        all_products = response.json()
        st.dataframe(all_products, width=500)
        return all_products
    else:
        st.error("無法取得商品資料")
        return None


def search_member_by_phone_number(phone_number: str) -> Optional[dict]:
    response = requests.get(f"{API_BASE_URL}/members/{phone_number}")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("無法取得會員資料")
        return None


def buy_product_page():
    """商品購買頁面

    1. 顯示所有商品
    2. 輸入會員號碼，確認該會員存在
    3. 選擇商品
    4. 購買數量
    5. 選擇付款方式
    6. 確認購買
    7. 點下購買鍵，即建立交易
    """

    st.title("商品購買")

    # 顯示所有商品
    st.write("請選擇要購買的商品")
    all_products = show_all_products()

    if all_products is None:
        return

    # 輸入會員號碼
    phone_number = st.text_input("請輸入會員號碼")

    if st.checkbox("查詢會員"):
        member = search_member_by_phone_number(phone_number)

        if member is not None:

            # st.dataframe(member, width=500)

            info_to_show = {
                "會員姓名": member["mName"],
                "會員手機號碼": member["mContactNum"],
                "會員回饋點數": member["mRewardPoints"],
                "會員餘額": member["mBalance"],
            }
            st.dataframe(info_to_show, width=500)

            # 選擇商品
            selected_product_name = st.selectbox(
                "選擇商品", [product["pName"] for product in all_products]
            )

            # 購買數量
            selected_product_quantity = st.number_input(
                "購買數量", min_value=1, value=1
            )

            # gsNo of the selected product
            selected_product_gsNo, selected_product_salePrice = next(
                (product["gsNo"], product["salePrice"])
                for product in all_products
                if product["pName"] == selected_product_name
            )

            st.divider()
            st.write(
                f"你選擇了: {selected_product_name}, 金額為: ${selected_product_salePrice}"
            )
            st.write(f"購買數量: {selected_product_quantity}")
            st.write(
                f"總金額: ${selected_product_salePrice * selected_product_quantity}"
            )

            st.divider()

            # 選擇付款方式
            selected_payment_method = st.selectbox(
                "選擇付款方式", ["現金", "信用卡", "轉帳", "回饋點數", "會員點數"]
            )

            if selected_payment_method == "現金":
                st.write("現金付款")
                payment_method = "cash"
            elif selected_payment_method == "信用卡":
                st.write("信用卡付款")
                payment_method = "credit_card"
            elif selected_payment_method == "轉帳":
                st.write("轉帳付款")
                payment_method = "e_transfer"
            elif selected_payment_method == "回饋點數":
                payment_method = "reward_points"
                if (
                    member["mRewardPoints"]
                    < selected_product_salePrice * selected_product_quantity
                ):
                    st.error("回饋點數不足")
                    payment_method = None
                st.write(f"回饋點數: {member['mRewardPoints']}")

            elif selected_payment_method == "會員點數":
                payment_method = "member_points"
                if (
                    member["mBalance"]
                    < selected_product_salePrice * selected_product_quantity
                ):
                    st.error("會員點數不足")
                    payment_method = None
                st.write(f"會員點數: {member['mBalance']}")

            discount = st.number_input(
                "折扣%", min_value=1, max_value=100, value=100, step=10
            )

            st.divider()

            original_price = selected_product_salePrice * selected_product_quantity
            st.write(f"原價: {original_price}")
            st.write(f"折扣: {100 - discount}%")
            st.write(f"折扣後價格: {original_price * (discount / 100)}")

            st.divider()

            if payment_method is not None:
                if st.button("購買"):
                    st.write("購買成功")

                    # 建立交易
                    transaction_data = {
                        "mContactNum": member["mContactNum"],
                        "gsNo": selected_product_gsNo,
                        "count": selected_product_quantity,
                        "unitPrice": selected_product_salePrice,
                        "discount": discount / 100,
                        "paymentMethod": payment_method,
                    }

                    st.write(transaction_data)

                    response = requests.post(
                        f"{API_BASE_URL}/transaction_records/", json=transaction_data
                    )

                    st.write(response.json())
                    if response.status_code == 200:
                        st.success("交易建立成功")
                    else:
                        st.error("交易建立失敗")
            else:
                st.error("購買失敗")
        else:
            st.error("無法取得會員資料")
