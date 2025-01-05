"""
創建商品
"""

import streamlit as st
import requests

from utils.api import API_BASE_URL


def create_product_page():
    st.title("創建商品")
    with st.form("create_product_form", clear_on_submit=True, border=True):
        gsNo = st.text_input("商品編號 (以P開頭+數字)", placeholder="例如: P111")
        pName = st.text_input("商品名稱")
        salePrice = st.number_input("商品價格", value=0)

        # NOTE: 先不用上傳商品圖片了
        # pImage = st.file_uploader("商品圖片", type=["jpg", "jpeg", "png"])

        if st.form_submit_button("創建商品"):
            new_product = {
                "gsNo": gsNo,
                "pName": pName,
                "salePrice": salePrice,
            }

            response = requests.post(f"{API_BASE_URL}/products/", json=new_product)
            if response.status_code == 200:
                st.success("商品創建成功")
            else:
                st.error("商品創建失敗")
