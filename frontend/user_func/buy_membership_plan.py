"""
會籍方案購買
"""

import streamlit as st

import pandas as pd

from typing import Optional, Dict, Any


from views.membership_plan import get_all_membership_plans
from views.member import search_member
from views.membership_status import get_membership_status, create_membership_status
from views.transaction_record import create_transaction


def display_available_plans_df(membership_plans: list) -> pd.DataFrame:
    df = pd.DataFrame(membership_plans)

    st.dataframe(
        df,
        width=500,
        column_order=["gsNo", "salePrice", "planType", "planDuration"],
        column_config={
            "gsNo": "會籍方案編號",
            "salePrice": "售價",
            "planType": "方案類型",
            "planDuration": "方案期限 (月)",
        },
    )

    return df


def display_selected_plan(df: pd.DataFrame, membership_plan: str) -> None:
    plan_details = df[df["gsNo"] == membership_plan].iloc[0]

    st.write(f"選擇的會籍方案: {membership_plan}")
    st.write(f"售價: ${plan_details['salePrice']}")
    st.write(f"方案類型: {plan_details['planType']}")
    st.write(f"方案期限: {plan_details['planDuration']}")


def handle_payment_method(member: Dict[str, Any], plan_price: int) -> Optional[str]:
    """處理付款方式選擇"""
    payment_methods = {
        "現金": "cash",
        "信用卡": "credit_card",
        "轉帳": "e_transfer",
        "回饋點數": "reward_points",
        "會員點數": "member_points",
    }

    selected = st.selectbox("付款方式", list(payment_methods.keys()))
    payment_method = payment_methods[selected]

    if payment_method in ["reward_points", "member_points"]:
        points_field = (
            "mRewardPoints" if payment_method == "reward_points" else "mBalance"
        )
        if member[points_field] < plan_price:
            st.error(
                f"{'回饋點數' if payment_method == 'reward_points' else '會員點數'} 不足"
            )
            st.write(f"目前點數: {member[points_field]}")
            return None

    return payment_method


def buy_membership_plan_page():
    """會籍方案購買頁面

    0. 顯示所有會籍方案
    1. 輸入會員手機號碼
    2. 確認會員存在
    3. 檢視會員目前會籍
    4. 選擇要購買的會籍方案
    5. 確認付款方式
    6. 確認購買
    7. 建立交易紀錄
    """

    st.title("會籍方案購買")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        # 0. 顯示所有會籍方案
        st.subheader("1. 所有會籍方案:")
        membership_plans = get_all_membership_plans()
        if not membership_plans:
            st.error("無法取得會籍方案資料")
            return

        df = display_available_plans_df(membership_plans)

    # 4. 選擇要購買的會籍方案
    with col2:

        st.subheader("2. 選擇要購買的會籍方案:")
        membership_plan = st.selectbox("會籍方案", df["gsNo"].tolist())
        display_selected_plan(df, membership_plan)

    # 1. 輸入會員手機號碼
    phone_number = st.text_input("請輸入會員手機號碼")
    if phone_number == "":
        st.warning("請輸入會員手機號碼")
        return

    # 2. 確認會員存在
    if st.checkbox("搜尋該會員是否存在", key="search_member_button"):
        member = search_member(phone_number)

        if member is None:
            st.warning("該會員不存在")
            return

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("3. 會員資料:")
            st.dataframe(member, column_config=None, width=400)

        with col2:
            st.subheader("4. 會員目前會籍:")
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

            st.divider()
            st.subheader("5. 確認方案效期:")
            # 選擇方案開始日期
            plan_duration = int(
                df[df["gsNo"] == membership_plan]["planDuration"].values[0]
            )

            st.write(f"⏳ 方案期限: {plan_duration} 個月")
            st.write("請選擇方案開始日期")

            # Select start date
            start_date = st.date_input(
                "請選擇方案開始日期",
                min_value="today",
                value="today",
                format="YYYY-MM-DD",
            )
            # Calculate end date
            end_date = pd.to_datetime(start_date) + pd.DateOffset(months=plan_duration)

            # Display in a more organized way
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"📅 方案開始日期: {start_date.strftime('%Y-%m-%d')}")
            with col2:
                st.info(f"📅 方案結束日期: {end_date.strftime('%Y-%m-%d')}")

        st.divider()
        st.subheader("6. 確認付款方式:")

        plan_price = df[df["gsNo"] == membership_plan]["salePrice"].values[0]
        payment_method = handle_payment_method(member, plan_price)

        if not payment_method:
            st.error("無法確認付款方式")
            return

        st.divider()
        col3, col4 = st.columns(2)

        with col3:
            st.subheader("7. 建立交易紀錄")
            if payment_method is not None:
                # 7. 建立交易紀錄
                transaction_data = {
                    "mContactNum": str(member["mContactNum"]),
                    "gsNo": str(membership_plan),  # M003
                    "count": int(1),
                    "unitPrice": int(
                        df[df["gsNo"] == membership_plan]["salePrice"].values[0]
                    ),
                    "discount": float(1),
                    "paymentMethod": str(payment_method),
                }
                st.write(f"會員號碼: {member['mContactNum']}")
                st.write(f"會籍方案編號: {membership_plan}")
                st.write(f"數量: {1}")
                st.write(
                    f"單價: {df[df['gsNo'] == membership_plan]['salePrice'].values[0]}"
                )
                st.write(f"付款方式: {payment_method}")

                st.divider()
            with col4:
                st.subheader("8. 確認購買")
                if st.toggle("確認購買"):
                    if st.button("購買"):
                        if create_transaction(transaction_data):

                            # 交易成功之後再建立新會籍狀態
                            membership_status = {
                                "mContactNum": str(member["mContactNum"]),
                                "startDate": str(start_date),
                                "endDate": str(end_date),
                                "isActive": True,
                            }
                            if create_membership_status(membership_status):
                                st.success("交易建立成功")
                                st.success("會籍狀態建立成功")
                                st.warning("請重新整理頁面")
                            else:
                                st.error("會籍狀態建立失敗, 查看是否已存在有效會籍")

                        else:
                            st.error("交易建立失敗")
