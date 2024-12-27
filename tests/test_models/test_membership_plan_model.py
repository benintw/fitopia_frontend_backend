"""
會籍方案測試
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import unittest
from database import get_connection
from models.membership_plan import MembershipPlan

from icecream import ic


class TestMembershipPlan(unittest.TestCase):
    """測試會籍方案類別的所有方法"""

    @classmethod
    def setUpClass(cls):
        """
        在所有測試開始前執行一次：
        1. 關閉外鍵約束
        2. 清空相關表格
        3. 確保有預設照片
        4. 重新啟用外鍵約束
        """
        conn = get_connection()
        cursor = conn.cursor()

        try:
            # 暫時關閉外鍵約束
            cursor.execute("PRAGMA foreign_keys = OFF")

            # 清空相關表格（按照正確的順序）
            cursor.execute("DELETE FROM OrderTable")  # 先刪除訂單
            cursor.execute("DELETE FROM MembershipStatus")  # 再刪除會籍狀態
            cursor.execute("DELETE FROM CheckInRecord")  # 再刪除打卡記錄
            cursor.execute("DELETE FROM Member")  # 最後刪除會員

            conn.commit()
        finally:
            # 重新啟用外鍵約束
            cursor.execute("PRAGMA foreign_keys = ON")
            conn.commit()
            conn.close()

    def setUp(self):
        """測試前準備：創建測試會籍方案資料"""
        self.test_membership_plan = {
            "gsNo": "M112",
            "planType": "測試會籍方案",
            "salePrice": 100,
            "planDuration": 30,
        }

    def test_1_create_membership_plan(self):
        """測試創建會籍方案"""
        # 先刪除可能存在的測試會籍方案
        MembershipPlan.delete_membership_plan(self.test_membership_plan["gsNo"])

        result = MembershipPlan.create_membership_plan(**self.test_membership_plan)
        ic(result)
        self.assertEqual(result.get("message"), "會籍方案創建成功")

    def test_2_get_membership_plan(self):
        """測試查詢單一會籍方案"""
        # 確保測試會籍方案存在
        MembershipPlan.create_membership_plan(**self.test_membership_plan)

        membership_plan = MembershipPlan.get_membership_plan(
            self.test_membership_plan["gsNo"]
        )
        self.assertIsNotNone(membership_plan)
        self.assertEqual(
            membership_plan["planType"], self.test_membership_plan["planType"]
        )
        self.assertEqual(
            membership_plan["planDuration"], self.test_membership_plan["planDuration"]
        )

    def test_3_get_all_membership_plans(self):
        """測試查詢所有會籍方案"""
        # 確保至少有一個會籍方案
        MembershipPlan.create_membership_plan(**self.test_membership_plan)

        membership_plans = MembershipPlan.get_all_membership_plans()
        self.assertIsInstance(membership_plans, list)
        self.assertGreater(len(membership_plans), 0)

        # 驗證測試會籍方案在列表中
        self.assertIn(self.test_membership_plan, membership_plans)

    def test_4_update_membership_plan(self):
        """測試更新會籍方案資料"""
        # 確保測試會籍方案存在
        MembershipPlan.create_membership_plan(**self.test_membership_plan)

        updated_membership_plan = {
            "gsNo": "M112",
            "planType": "更新測試會籍方案",
            "salePrice": 200,
            "planDuration": 60,
        }

        result = MembershipPlan.update_membership_plan(**updated_membership_plan)
        self.assertEqual(result.get("message"), "會籍方案更新成功")

        updated_membership_plan = MembershipPlan.get_membership_plan(
            self.test_membership_plan["gsNo"]
        )
        self.assertEqual(updated_membership_plan["planType"], "更新測試會籍方案")
        self.assertEqual(updated_membership_plan["salePrice"], 200)
        self.assertEqual(updated_membership_plan["planDuration"], 60)

    def test_5_delete_membership_plan(self):
        """測試刪除會籍方案"""
        # 確保測試會籍方案存在
        MembershipPlan.create_membership_plan(**self.test_membership_plan)

        result = MembershipPlan.delete_membership_plan(
            self.test_membership_plan["gsNo"]
        )
        ic(result)
        self.assertEqual(result.get("message"), "會籍方案刪除成功")

        # 確認測試會籍方案已經被刪除
        membership_plan = MembershipPlan.get_membership_plan(
            self.test_membership_plan["gsNo"]
        )
        self.assertIsNone(membership_plan)
