"""
新增會員
"""

import streamlit as st

from views.member import create_member, search_member


def create_new_member_page():
    """
    新增會員

    1. 首先透過手機號碼查詢會員是否存在
        2. 如果會員不存在，則透過手機號碼建立會員
        3. 上傳照片


    """

    st.title("新增會員")

    # 1. 透過手機號碼查詢會員是否存在
    mContactNum = st.text_input("請輸入手機號碼")

    if mContactNum == "":
        st.error("請輸入手機號碼")
        return
    if st.checkbox("搜尋該會員是否存在", key="search_member_button"):
        member = search_member(mContactNum)
        if member is not None:
            st.warning("該會員已存在")
            st.dataframe(member, width=400)
            return
        else:
            st.warning("該會員不存在")

            if st.checkbox("建立會員", key="create_member_button"):
                st.subheader("建立會員:")
                # 2.進入建立會員表單
                if create_member():
                    st.success("會員新增成功")
                else:
                    st.warning("會員新增失敗: 資料輸入錯誤")
