"""
商品管理
"""

import streamlit as st
import requests
from utils.api import API_BASE_URL
from user_func.create_product import create_product_page


def show_all_products():
    response = requests.get(f"{API_BASE_URL}/products/")
    if response.status_code == 200:
        # st.write(response.json())
        all_products = response.json()
        st.dataframe(all_products, width=500)
    else:
        st.error("無法取得商品資料")


def update_product():
    """更新商品"""

    gsNo = st.text_input("商品編號", placeholder="P111")
    pName = st.text_input("商品名稱")
    salePrice = st.number_input("商品價格", value=0)

    if st.button("更新商品"):
        update_data = {
            "pName": pName,
            "salePrice": salePrice,
        }
        response = requests.put(f"{API_BASE_URL}/products/{gsNo}/", json=update_data)
        st.write(response.json())


def product_page():
    st.title("商品管理")

    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.subheader("商品列表")
        if st.button("重新整理"):
            show_all_products()

    with col2:
        st.subheader("商品更新")
        update_product()

    with col3:
        st.subheader("商品新增")
        create_product_page()
