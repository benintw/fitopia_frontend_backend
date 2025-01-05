"""
測試會籍狀態模型
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import unittest
from datetime import date, timedelta
from gym_management.backend.database import get_connection
from models.membership_status import MembershipStatus
from models.member import Member
import logging

from icecream import ic


class TestMembershipStatus(unittest.TestCase):
    """測試會籍狀態類別的所有方法"""

    @classmethod
    def setUpClass(cls):
        """在所有測試開始前執行一次"""
        cls.test_member = {
            "mContactNum": "0912345699",
            "mName": "測試會員",
            "mEmail": "test@example.com",
            "mDob": "1990-01-01",
            "mEmergencyName": "緊急聯絡人",
            "mEmergencyNum": "0987654321",
            "mBalance": 1000,
            "mRewardPoints": 100,
        }

        # 第二個測試會員
        cls.test_member2 = {
            "mContactNum": "0923456789",
            "mName": "測試會員2",
            "mEmail": "test2@example.com",
            "mDob": "1992-02-02",
            "mEmergencyName": "緊急聯絡人2",
            "mEmergencyNum": "0912345678",
            "mBalance": 2000,
            "mRewardPoints": 200,
        }
        # 設置測試日期
        cls.today = date.today()
        cls.future_date = cls.today + timedelta(days=30)

    def setUp(self):
        """每個測試方法執行前都會執行"""
        conn = get_connection()
        cursor = conn.cursor()

        try:
            # 暫時關閉外鍵約束
            cursor.execute("PRAGMA foreign_keys = OFF")

            # 清空相關表格
            cursor.execute("DELETE FROM MembershipStatus")
            cursor.execute("DELETE FROM Member")

            # 重新啟用外鍵約束
            cursor.execute("PRAGMA foreign_keys = ON")
            conn.commit()

            # 創建測試會員
            result1 = Member.create_member(**self.test_member)
            result2 = Member.create_member(**self.test_member2)
            ic(result1)
            ic(result2)

            if "error" in result1 or "error" in result2:
                raise Exception("測試會員創建失敗")

        finally:
            conn.close()

    def test_1_create_membership_status(self):
        """測試創建會籍狀態"""
        # 測試正常創建
        result = MembershipStatus.create_membership_status(
            mContactNum=self.test_member["mContactNum"],
            startDate=self.today,
            endDate=self.future_date,
            isActive=True,
        )
        ic(result)
        self.assertEqual(result.get("message"), "會籍狀態創建成功")

        # 測試結束日期小於開始日期
        invalid_result = MembershipStatus.create_membership_status(
            mContactNum=self.test_member["mContactNum"],
            startDate=self.future_date,
            endDate=self.today,
            isActive=True,
        )
        ic(invalid_result)
        self.assertEqual(invalid_result.get("error"), "結束日期不能小於開始日期")

    def test_2_get_membership_status(self):
        """測試查詢會籍狀態"""
        # 創建會籍狀態
        self.test_1_create_membership_status()

        # 測試正常查詢
        result = MembershipStatus.get_membership_status(
            mContactNum=self.test_member["mContactNum"]
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["mContactNum"], self.test_member["mContactNum"])

        # 將字符串轉換為 date 對象進行比較
        self.assertEqual(date.fromisoformat(result["startDate"]), self.today)
        self.assertEqual(date.fromisoformat(result["endDate"]), self.future_date)
        self.assertEqual(result["isActive"], True)

    def test_3_get_all_membership_status(self):
        """測試查詢所有會籍狀態"""

        # 確認兩個會員都存在
        member1 = Member.get_member(self.test_member["mContactNum"])
        member2 = Member.get_member(self.test_member2["mContactNum"])
        self.assertIsNotNone(member1)
        self.assertIsNotNone(member2)

        # 創建多個會籍狀態
        first_start = self.today
        first_end = first_start + timedelta(days=30)
        first_create_result = MembershipStatus.create_membership_status(
            mContactNum=self.test_member["mContactNum"],
            startDate=first_start,
            endDate=first_end,
            isActive=True,
        )
        ic(first_create_result)
        self.assertIn("message", first_create_result)

        second_create_result = MembershipStatus.create_membership_status(
            mContactNum=self.test_member2["mContactNum"],
            startDate=self.today + timedelta(days=1),
            endDate=self.today + timedelta(days=31),
            isActive=True,
        )
        ic(second_create_result)
        self.assertIn("message", second_create_result)

        # 查詢所有會籍狀態
        result = MembershipStatus.get_all_membership_status()
        ic(result)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

        # 驗證測試會籍狀態在列表中
        test_membership_status_found = False
        for membership_status in result:
            if membership_status["mContactNum"] == self.test_member["mContactNum"]:
                test_membership_status_found = True
                break
        self.assertTrue(test_membership_status_found)

        member_numebers = {status["mContactNum"] for status in result}
        self.assertIn(self.test_member["mContactNum"], member_numebers)
        self.assertIn(self.test_member2["mContactNum"], member_numebers)

    def test_4_update_membership_status(self):
        """測試更新會籍狀態"""
        # 創建會籍狀態
        self.test_1_create_membership_status()

        # 測試正常更新
        update_data = {
            "mContactNum": self.test_member["mContactNum"],
            "startDate": self.today + timedelta(days=2),
            "endDate": self.future_date,
            "isActive": True,
        }

        result = MembershipStatus.update_membership_status(**update_data)
        ic(result)
        self.assertEqual(result.get("message"), "會籍狀態更新成功")

        updated_membership_status = MembershipStatus.get_membership_status(
            mContactNum=self.test_member["mContactNum"]
        )
        ic(updated_membership_status)
        self.assertEqual(
            date.fromisoformat(updated_membership_status["startDate"]),
            self.today + timedelta(days=2),
        )
        self.assertEqual(
            date.fromisoformat(updated_membership_status["endDate"]), self.future_date
        )
        self.assertEqual(updated_membership_status["isActive"], True)

    def test_5_delete_membership_status(self):
        """測試刪除會籍狀態"""
        # 創建會籍狀態
        self.test_1_create_membership_status()

        # 測試正常刪除
        result = MembershipStatus.delete_membership_status(
            mContactNum=self.test_member["mContactNum"]
        )
        ic(result)
        self.assertEqual(result.get("message"), "會籍狀態刪除成功")

        # 確認會籍狀態已刪除
        membership_status = MembershipStatus.get_membership_status(
            mContactNum=self.test_member["mContactNum"]
        )
        ic(membership_status)
        self.assertIsNone(membership_status)

    def test_6_error_cases(self):
        """測試錯誤情況"""
        # 創建會籍狀態
        self.test_1_create_membership_status()

        # 測試創建重複會籍狀態
        duplicate_result = MembershipStatus.create_membership_status(
            mContactNum=self.test_member["mContactNum"],
            startDate=self.today,
            endDate=self.future_date,
            isActive=True,
        )
        ic(duplicate_result)
        self.assertIn("error", duplicate_result)

        # 測試更新不存在的會籍狀態
        non_exist_update = MembershipStatus.update_membership_status(
            mContactNum="9999999999",
            startDate=self.today,
            endDate=self.future_date,
            isActive=True,
        )
        ic(non_exist_update)
        self.assertIn("error", non_exist_update)

        # 測試刪除不存在的會籍狀態
        non_exist_delete = MembershipStatus.delete_membership_status("9999999999")
        ic(non_exist_delete)
        self.assertIn("error", non_exist_delete)
