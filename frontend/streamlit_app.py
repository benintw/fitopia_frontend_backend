"""
Streamlit application for gym management
"""

import streamlit as st
import requests


from views.home import home_page
from views.products import product_page
from views.member import member_management_page
from views.checkin_record import checkin_record_page
from views.membership_plan import membership_plans_page
from views.transaction_record import transaction_records_page
from views.member_photo import member_photo_page
from views.membership_status import membership_status_page

from user_func.create_product import create_product_page
from user_func.update_balance import update_balance_page
from user_func.buy_product import buy_product_page
from user_func.buy_membership_plan import buy_membership_plan_page
from user_func.create_new_member import create_new_member_page
from user_func.checkin_out_record import checkin_out_record_page

# CONSTANTS
API_BASE_URL = "http://localhost:8000"

# Page Configs
st.set_page_config(
    page_title="FITOPIA 健身房管理系統",
    page_icon=":muscle:",
    layout="wide",
)


def login_page():
    st.title("登入")
    username = st.text_input("帳號")
    password = st.text_input("密碼", type="password")
    if st.button("登入"):
        # Implement login logic
        pass


# main page
def main_page():

    # Define pages with sections
    pages = {
        "FITOPIA 健身房": [
            st.Page(home_page, title="首頁", icon="🏠")
            # st.Page(dashboard_page, title="儀表板", icon="📊"),
        ],
        "業主要求": [
            # 新增會員
            st.Page(create_new_member_page, title="新增會員", icon="👥"),
            # 方案購買
            st.Page(buy_membership_plan_page, title="方案購買", icon="🛒"),
            # 商品購買
            st.Page(buy_product_page, title="商品購買", icon="🛒"),
            # 商品創建
            st.Page(create_product_page, title="商品創建", icon="🛍️"),
            # 變動管理
            st.Page(update_balance_page, title="變動管理", icon="💰"),
            # 進出場紀錄
            st.Page(checkin_record_page, title="進出場紀錄", icon="✅"),
        ],
        "會員管理": [
            st.Page(member_management_page, title="會員資料", icon="👥"),
            st.Page(member_photo_page, title="會員照片", icon="📸"),
            st.Page(membership_status_page, title="會籍狀態", icon="📋"),
        ],
        "營運管理": [
            st.Page(membership_plans_page, title="會籍方案", icon="📝"),  # done
            st.Page(product_page, title="商品管理", icon="🛍️"),  # done
            st.Page(transaction_records_page, title="交易紀錄", icon="💰"),
        ],
    }

    pg = st.navigation(pages)
    pg.run()

    st.sidebar.markdown("© 2025 FITOPIA 健身房")


if __name__ == "__main__":
    main_page()
