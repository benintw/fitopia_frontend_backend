"""測試打卡記錄相關 API"""

from fastapi.testclient import TestClient
from gym_management.backend.main import app
import unittest
from datetime import datetime, timedelta
import pytz
from models.member import Member
from icecream import ic
from gym_management.backend.database import get_connection


class TestCheckInRecordRoutes(unittest.TestCase):

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
        self.client = TestClient(app)
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
        response = self.client.post(
            "/checkinrecord/", json={"mContactNum": self.test_member["mContactNum"]}
        )
        ic(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "打卡記錄創建成功"})

    def test_2_get_checkin_record(self):
        """測試查詢打卡記錄"""

        # 查詢打卡記錄
        response = self.client.get(f"/checkinrecord/{self.test_member['mContactNum']}/")
        ic(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["mContactNum"], self.test_member["mContactNum"]
        )

    def test_3_get_all_checkin_records(self):
        """測試查詢所有打卡記錄"""
        response = self.client.get("/checkinrecord/")
        ic(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_4_update_checkin_record(self):
        """測試更新打卡記錄"""
        response = self.client.put(f"/checkinrecord/{self.test_member['mContactNum']}/")
        ic(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "打卡記錄更新成功")

    def test_5_delete_checkin_record(self):
        """測試刪除打卡記錄"""
        # 創建打卡記錄
        self.test_1_create_checkin_record()

        # 刪除打卡記錄
        response = self.client.delete(
            f"/checkinrecord/{self.test_member['mContactNum']}/"
        )
        ic(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], "打卡記錄刪除成功")

    def test_6_error_cases(self):
        """測試錯誤情況"""

        # 創建打卡記錄
        self.test_1_create_checkin_record()

        # 測試重複打卡
        response = self.client.post(
            "/checkinrecord/", json={"mContactNum": self.test_member["mContactNum"]}
        )
        ic(response.json())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "已有未結束的打卡記錄")

        # 測試更新不存在的打卡記錄
        response = self.client.put(f"/checkinrecord/{999999}/")
        ic(response.json())
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "打卡記錄不存在")

        # 測試刪除不存在的打卡記錄
        response = self.client.delete(f"/checkinrecord/{999999}/")
        ic(response.json())
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "打卡記錄不存在")


if __name__ == "__main__":
    unittest.main()
