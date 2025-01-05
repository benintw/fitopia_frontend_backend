"""
會員類別測試
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import unittest
from gym_management.backend.database import get_connection
from models.member import Member

from icecream import ic


class TestMember(unittest.TestCase):
    """測試會員類別的所有方法"""

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
        """測試前準備：創建測試會員資料"""
        self.test_member = {
            "mContactNum": "0912345699",
            "mName": "測試會員",
            "mEmail": "test@example.com",
            "mDob": "1990-01-01",
            "mEmergencyName": "緊急聯絡人",
            "mEmergencyNum": "0987654321",
            "mBalance": 1000,
            "mRewardPoints": 100,
        }

    def test_1_create_member(self):
        """測試創建會員"""
        # 先刪除可能存在的測試會員
        Member.delete_member(self.test_member["mContactNum"])

        result = Member.create_member(**self.test_member)
        self.assertEqual(result.get("message"), "會員創建成功")

    def test_2_get_member(self):
        """測試查詢單一會員"""
        # 確保測試會員存在
        Member.create_member(**self.test_member)

        member = Member.get_member(self.test_member["mContactNum"])
        ic(member)
        self.assertIsNotNone(member)
        self.assertEqual(member["mName"], self.test_member["mName"])
        self.assertEqual(member["mEmail"], self.test_member["mEmail"])

    def test_3_get_all_members(self):
        """測試查詢所有會員"""
        # 確保至少有一個會員
        Member.create_member(**self.test_member)

        members = Member.get_all_members()
        self.assertIsInstance(members, list)
        self.assertGreater(len(members), 0)

        # 驗證測試會員在列表中
        test_member_found = False
        for member in members:
            if member["mContactNum"] == self.test_member["mContactNum"]:
                test_member_found = True
                break
        self.assertTrue(test_member_found)

    def test_4_update_member(self):
        """測試更新會員資料"""
        # 確保測試會員存在
        Member.create_member(**self.test_member)

        update_data = {
            "mContactNum": self.test_member["mContactNum"],
            "mEmail": "updated@example.com",
            "mBalance": 2000,
        }
        result = Member.update_member(**update_data)
        self.assertEqual(result.get("message"), "會員資料更新成功")

        updated_member = Member.get_member(self.test_member["mContactNum"])
        self.assertEqual(updated_member["mEmail"], "updated@example.com")
        self.assertEqual(updated_member["mBalance"], 2000)

    def test_5_delete_member(self):
        """測試刪除會員"""
        # 確保測試會員存在
        Member.create_member(**self.test_member)

        result = Member.delete_member(self.test_member["mContactNum"])
        self.assertEqual(result.get("message"), "會員刪除成功")

        member = Member.get_member(self.test_member["mContactNum"])
        self.assertIsNone(member)

    def test_6_error_cases(self):
        """測試錯誤情況"""
        # 確保測試會員存在
        Member.create_member(**self.test_member)

        # 測試創建重複會員
        duplicate_result = Member.create_member(**self.test_member)
        ic(duplicate_result)
        self.assertIn("error", duplicate_result)

        # 測試更新不存在的會員
        non_exist_update = Member.update_member(
            mContactNum="9999999999", mEmail="nonexist@example.com"
        )
        ic(non_exist_update)
        self.assertIn("error", non_exist_update)

        # 測試刪除不存在的會員
        non_exist_delete = Member.delete_member("9999999999")
        ic(non_exist_delete)
        self.assertIn("error", non_exist_delete)

    @classmethod
    def tearDownClass(cls):
        """
        在所有測試結束後清理數據
        """
        conn = get_connection()
        cursor = conn.cursor()

        try:
            # 暫時關閉外鍵約束
            cursor.execute("PRAGMA foreign_keys = OFF")

            # 清空相關表格（按照正確的順序）
            cursor.execute("DELETE FROM OrderTable")
            cursor.execute("DELETE FROM MembershipStatus")
            cursor.execute("DELETE FROM CheckInRecord")
            cursor.execute("DELETE FROM Member")

            conn.commit()

        finally:
            # 重新啟用外鍵約束
            cursor.execute("PRAGMA foreign_keys = ON")
            conn.commit()
            conn.close()
