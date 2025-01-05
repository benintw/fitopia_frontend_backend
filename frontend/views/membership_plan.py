"""
會籍方案
"""

import streamlit as st
import requests
import pandas as pd
from typing import Optional, List, TypedDict
from utils.api import API_BASE_URL


class MembershipPlan(TypedDict):

    gsNo: str
    salePrice: int
    planType: str
    planDuration: int  # months


def get_all_membership_plans() -> Optional[List[MembershipPlan]]:
    response = requests.get(f"{API_BASE_URL}/membership_plans/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("無法取得會籍方案資料")
        return None


def create_membership_plan() -> None:
    """Create a new membership plan.

    Displays a form to input new membership plan details.
    Handles API communication for creating the plan.
    """

    try:
        st.write("請輸入會籍方案編號、售價、方案類型、方案期限 (月)")

        # input fields
        gsNo = st.text_input(
            "會籍方案編號", placeholder="以M開頭, 例如: M004", key="create_gsno"
        )
        salePrice = st.number_input(
            "售價 ($)",
            min_value=0,
            placeholder="為購買一次的價格",
            key="create_salePrice",
        )
        planType = st.text_input(
            "方案類型", placeholder="包月、包半年、包年", key="create_planType"
        )
        planDuration = st.number_input(
            "方案期限 (月)", min_value=0, key="create_planDuration"
        )

        # create new membership plan
        new_membership_plan = {
            "gsNo": gsNo,
            "salePrice": salePrice,
            "planType": planType,
            "planDuration": planDuration,
        }

        # validate inputs before enabling create button
        is_valid = all(
            [
                gsNo.startswith("M"),
                len(gsNo) > 1,
                salePrice > 0,
                planType,
                planDuration > 0,
            ]
        )

        if is_valid and st.button("新增", key="create_button"):
            with st.spinner("新增會籍方案中..."):

                response = requests.post(
                    f"{API_BASE_URL}/membership_plans/", json=new_membership_plan
                )

                if response.status_code == 200:
                    st.success("新增會籍方案成功")

                    # show creation details
                    st.write("新增方案詳情:")
                    st.json(new_membership_plan)

                    st.info("請重新整理頁面以查看新增的會籍方案")
                    return
                else:
                    st.error(f"新增會籍方案失敗: {response.text}")
                    return
        elif not is_valid and st.button("新增", key="create_button_disabled"):
            st.warning("請輸入正確的會籍方案編號、售價、方案類型、方案期限")
            if not gsNo.startswith("M"):
                st.warning("會籍方案編號必須以M開頭")

    except Exception as e:
        st.error(f"發生錯誤: {str(e)}")
        return


def update_membership_plan() -> None:
    """Update an existing membership plan.

    Displays a form to select and update membership plan details.
    Handles API communication for updating the plan.
    """
    st.write("請選擇要更新的會籍方案編號、售價、方案類型、方案期限")

    membership_plans = get_all_membership_plans()
    if not membership_plans:
        st.error("無法取得會籍方案資料")
        return

    try:
        df = pd.DataFrame(membership_plans)
        st.dataframe(df)

    except Exception as e:
        st.error(f"無法取得會籍方案資料: {e}")
        return

    try:
        # 選擇要更新的會籍方案編號
        gsNo_to_update = st.selectbox("選擇要更新的會籍方案編號", df["gsNo"])

        # get current plan data
        current_plan = df[df["gsNo"] == gsNo_to_update].iloc[0]

        updated_salePrice = st.number_input(
            "新的售價 ($)",
            min_value=0,
            value=int(current_plan["salePrice"]),
            key="updated_salePrice",
        )
        updated_planType = st.text_input(
            "新的方案類型",
            placeholder="包月、包半年、包年",
            value=current_plan["planType"],
            key="updated_planType",
        )
        updated_planDuration = st.number_input(
            "新的方案期限 (月)",
            min_value=0,
            value=int(current_plan["planDuration"]),
            key="updated_planDuration",
        )

        new_membership_plan = {
            "gsNo": gsNo_to_update,
            "salePrice": updated_salePrice,
            "planType": updated_planType,
            "planDuration": updated_planDuration,
        }

        if st.button("更新"):
            st.write(
                f"更新會籍方案: 會籍編號{gsNo_to_update}, 售價{updated_salePrice}, 方案類型{updated_planType}, 方案期限{updated_planDuration}"
            )
            response = requests.put(
                f"{API_BASE_URL}/membership_plans/{gsNo_to_update}",
                json=new_membership_plan,
            )
            if response.status_code == 200:
                st.success("更新會籍方案成功")
                st.write("請重新整理頁面")
            else:
                st.error("更新會籍方案失敗")

    except Exception as e:
        st.error(f"無法更新會籍方案: {str(e)}")


def delete_membership_plan() -> None:
    """Delete an existing membership plan.

    Displays a form to select and delete membership plan.
    Handles API communication for deleting the plan.
    """

    try:
        st.write("請選擇要刪除的會籍方案編號")

        membership_plans = get_all_membership_plans()
        if not membership_plans:
            st.error("無法取得會籍方案資料")
            return

        # display current plans

        try:
            df = pd.DataFrame(membership_plans)
            st.dataframe(
                df,
                column_order=["gsNo", "salePrice", "planType", "planDuration"],
                column_config={
                    "gsNo": "會籍方案編號",
                    "salePrice": "售價",
                    "planType": "方案類型",
                    "planDuration": "方案期限 (月)",
                },
            )
        except Exception as e:
            st.error(f"無法取得會籍方案資料: {e}")
            return

        # 選擇要刪除的會籍方案編號
        gsNo_to_delete = st.selectbox(
            "選擇要刪除的會籍方案編號", df["gsNo"], key="delete_gsNo"
        )

        # show plan details before deletion
        plan_to_delete = df[df["gsNo"] == gsNo_to_delete].iloc[0]
        st.write("即將刪除的會籍方案:")
        st.info(
            f"""
            - 會籍方案編號: {plan_to_delete["gsNo"]}
            - 售價: {plan_to_delete["salePrice"]}
            - 方案類型: {plan_to_delete["planType"]}
            - 方案期限 (月): {plan_to_delete["planDuration"]}
            """
        )

        # confirms deletion
        if st.button("確定刪除", key="confirm_delete_button"):

            with st.spinner("刪除會籍方案中..."):
                response = requests.delete(
                    f"{API_BASE_URL}/membership_plans/{gsNo_to_delete}"
                )

            st.write(response.json())

            if response.status_code == 200:
                st.success("刪除會籍方案成功")
                st.info("請重新整理頁面以查看刪除的會籍方案")

            else:
                st.error("刪除會籍方案失敗")

    except Exception as e:
        st.error(f"發生錯誤: {str(e)}")


def membership_plans_page():
    """
    會籍方案

    - 顯示所有會籍方案
    - 可以新增會籍方案
    - 可以編輯會籍方案
    - 可以刪除會籍方案

    """

    st.write("membership_plan.py")
    st.title("會籍方案")
    st.divider()

    st.subheader("顯示所有會籍方案")
    # 顯示所有會籍方案
    membership_plans = get_all_membership_plans()
    if membership_plans:
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
    else:
        st.error("無法取得會籍方案資料")

    st.subheader("新增、編輯、刪除會籍方案")
    tab1, tab2, tab3 = st.tabs(["新增會籍方案", "編輯會籍方案", "刪除會籍方案"])

    # 新增會籍方案
    with tab1:
        create_membership_plan()

    # 編輯會籍方案
    with tab2:
        update_membership_plan()

    # 刪除會籍方案
    with tab3:
        delete_membership_plan()
