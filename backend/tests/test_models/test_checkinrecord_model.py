"""
測試打卡記錄模型
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import unittest
from gym_management.backend.database import get_connection
from models.checkinrecord import CheckInRecord
from models.member import Member
from datetime import datetime

from icecream import ic


class TestCheckInRecord(unittest.TestCase):
    """測試打卡記錄模型"""

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
            cursor.execute("DELETE FROM CheckInRecord")
            cursor.execute("DELETE FROM Member")  # 最後刪除會員
            conn.commit()

        finally:
            # 重新啟用外鍵約束
            cursor.execute("PRAGMA foreign_keys = ON")
            conn.commit()
            conn.close()

    def setUp(self):
        """測試前準備：創建測試會員和打卡記錄資料"""
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
        # 確保測試會員存在
        Member.create_member(**self.test_member)

        self.test_checkin = {
            "mContactNum": "0912345699",
        }

    def test_1_create_checkin_record(self):
        """測試創建打卡記錄"""
        result = CheckInRecord.create_checkin_record(**self.test_checkin)
        ic(result)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "打卡記錄創建成功")

    def test_2_get_checkin_record(self):
        """測試獲取某一會員的某一打卡記錄"""
        result = CheckInRecord.get_checkin_record(
            mContactNum=self.test_checkin["mContactNum"]
        )
        ic(result)
        self.assertIsNotNone(result)
        self.assertEqual(result["mContactNum"], self.test_checkin["mContactNum"])

    def test_3_get_all_checkin_records(self):
        """測試獲取所有打卡記錄"""
        result = CheckInRecord.get_all_checkin_records()
        ic(result)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)

    def test_4_update_checkin_record(self):
        """測試更新打卡記錄"""
        result = CheckInRecord.update_checkin_record(
            mContactNum=self.test_checkin["mContactNum"],
        )
        ic(result)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "打卡記錄更新成功")

    def test_5_delete_checkin_record(self):
        """測試刪除打卡記錄"""
        self.test_1_create_checkin_record()
        result = CheckInRecord.delete_checkin_record(
            mContactNum=self.test_checkin["mContactNum"],
        )
        ic(result)
        self.assertIn("success", result)
        self.assertEqual(result["success"], "打卡記錄刪除成功")

    def test_6_create_two_checkin_records(self):
        """測試創建兩個打卡記錄"""
        result = CheckInRecord.create_checkin_record(**self.test_checkin)
        ic(result)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "打卡記錄創建成功")

        # update checkin record
        self.test_4_update_checkin_record()

        """測試創建兩個打卡記錄"""
        result = CheckInRecord.create_checkin_record(**self.test_checkin)
        ic(result)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "打卡記錄創建成功")

        # 收尋所有打卡記錄
        result = CheckInRecord.get_all_checkin_records()
        ic(result)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)


if __name__ == "__main__":
    unittest.main()
