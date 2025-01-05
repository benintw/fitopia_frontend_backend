"""
會員照片
"""

import streamlit as st
import requests
import base64
import io
from PIL import Image
from utils.api import API_BASE_URL
from typing import Optional
from views.member import search_member


def display_member_photo(member_photo: dict) -> None:
    """Display member photo with proper error handling"""
    try:
        if not member_photo or "mPhoto" not in member_photo:
            st.warning("無會員照片")
            return

        # Get the base64 image data
        photo_data = member_photo["mPhoto"]

        # # Debug info
        # st.write("Received photo data type:", type(photo_data))
        # st.write("First 50 chars:", photo_data[:50])

        # First decode - the string appears to be base64 encoded
        try:
            decoded_data = base64.b64decode(photo_data).decode("utf-8")

            # Now we should have the data URI string
            if "base64," in decoded_data:
                # Extract the actual image data
                actual_base64 = decoded_data.split("base64,")[1]
                # Decode the actual image data
                image_bytes = base64.b64decode(actual_base64)

                # Create and display image
                image = Image.open(io.BytesIO(image_bytes))
                st.image(image, caption="會員照片", use_container_width=True)
            else:
                st.error("無法找到 base64 標記")

        except Exception as e:
            st.error(f"圖片解碼錯誤: {str(e)}")
            st.write("完整錯誤訊息:", str(e))

    except Exception as e:
        st.error(f"顯示照片時發生錯誤: {str(e)}")


def handle_photo_upload(uploaded_file) -> Optional[str]:
    """Handle photo upload and return base64 string"""
    try:
        if uploaded_file is None:
            return None

        bytes_data = uploaded_file.read()
        base64_str = base64.b64encode(bytes_data).decode()
        photo_data = (
            f"data:image/{uploaded_file.type.split('/')[-1]};base64,{base64_str}"
        )

        # # Debug info
        # st.write("Photo data before sending to API:", photo_data[:100])

        return photo_data
    except Exception as e:
        st.error(f"處理照片上傳時發生錯誤: {str(e)}")
        return None


def upload_member_photo():
    uploaded_file = st.file_uploader("上傳照片", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        st.image(bytes_data)

        return bytes_data
    else:
        return None


def create_member_photo_instance(bytes_data, mContactNum) -> bool:
    """
    建立會員照片紀錄
    """

    files = {"photo": bytes_data}
    data = {"mContactNum": mContactNum}
    response = requests.post(f"{API_BASE_URL}/member_photo/", files=files, data=data)

    return response.status_code == 200


def get_member_current_photo(mContactNum):
    """
    取得會員現有照片

    """
    response = requests.get(f"{API_BASE_URL}/member_photo/{mContactNum}")
    if response.status_code == 200:
        return response.json()
    else:
        return None


def member_photo_page():
    """
    會員照片

    主要功能:
    收尋會員與對應照片，並做更新照片
    """
    # st.write("member_photo.py")
    st.title("會員照片管理")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("收尋會員:")
        # 1. 透過手機號碼查詢會員是否存在
        mContactNum = st.text_input("請輸入手機號碼")
        if st.checkbox("搜尋該會員是否存在", key="search_member_button"):
            member = search_member(mContactNum)
            if member is not None:
                st.dataframe(member, width=400)

                with col2:

                    # 取得會員現有照片
                    st.subheader("現有照片:")
                    member_photo = get_member_current_photo(mContactNum)
                    if member_photo is not None:
                        st.write(member_photo)
                        display_member_photo(member_photo)

                    else:
                        st.warning("會員目前沒有照片")

                    st.divider()

                    # 上傳照片
                    st.subheader("上傳新照片:")
                    uploaded_file = st.file_uploader(
                        "上傳照片", type=["jpg", "jpeg", "png"]
                    )
                    if uploaded_file:
                        photo_data = handle_photo_upload(uploaded_file)
                        if photo_data:
                            st.success("照片上傳成功")
                            # preview the uploaded image
                            st.image(
                                uploaded_file,
                                caption="上傳照片",
                                use_container_width=True,
                            )

                            if st.toggle("上傳照片", key="upload_photo_button"):
                                st.write("建立會員照片紀錄中 ...")
                                if create_member_photo_instance(
                                    photo_data, mContactNum
                                ):
                                    st.success("建立會員照片紀錄成功")
                                else:
                                    st.error("建立會員照片紀錄失敗")
            else:
                st.error("會員不存在")
