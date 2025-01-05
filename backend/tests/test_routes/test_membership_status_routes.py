"""
測試會籍狀態相關 API
"""

from fastapi.testclient import TestClient
from gym_management.backend.main import app
import unittest
from icecream import ic
from gym_management.backend.database import get_connection
from models.member import Member
from datetime import date, timedelta


class TestMembershipStatusRoutes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """在所有測試開始前執行一次"""
        cls.client = TestClient(app)
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

            if "error" in result1 or "error" in result2:
                raise Exception("測試會員創建失敗")

        finally:
            conn.close()

    def test_1_create_membership_status(self):
        """測試創建會籍狀態 API"""
        membership_data = {
            "mContactNum": self.test_member["mContactNum"],
            "startDate": self.today.isoformat(),
            "endDate": self.future_date.isoformat(),
            "isActive": True,
        }
        response = self.client.post("/membership_status/", json=membership_data)
        ic(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "會籍狀態創建成功"})

        # 測試無效日期
        invalid_date_data = membership_data.copy()
        invalid_date_data["endDate"] = self.today.isoformat()  # 結束日期等於開始日期
        response = self.client.post("/membership_status/", json=invalid_date_data)
        ic(response.json())
        self.assertEqual(response.status_code, 422)  # Validation Error

    def test_2_get_membership_status(self):
        """測試查詢會籍狀態 API"""
        # 先創建一個會籍狀態
        self.test_1_create_membership_status()
        response = self.client.get(
            f"/membership_status/{self.test_member['mContactNum']}/"
        )
        ic(response.json())
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("mContactNum", data)
        self.assertIn("startDate", data)
        self.assertIn("endDate", data)
        self.assertIn("isActive", data)
        self.assertEqual(data["mContactNum"], self.test_member["mContactNum"])

    def test_3_get_all_membership_status(self):
        """測試查詢所有會籍狀態 API"""
        response = self.client.get("/membership_status/")
        ic(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_4_update_membership_status(self):
        """測試更新會籍狀態 API"""
        self.test_1_create_membership_status()

        # 更新會籍狀態
        update_data = {
            "startDate": self.today.isoformat(),
            "endDate": self.future_date.isoformat(),
            "isActive": False,
        }

        response = self.client.put(
            f"/membership_status/{self.test_member['mContactNum']}/",
            json=update_data,
        )
        ic(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("message"), "會籍狀態更新成功")

    def test_5_error_cases(self):
        """測試錯誤情況"""

        # 先創建一個會籍狀態
        membership_data = {
            "mContactNum": self.test_member["mContactNum"],
            "startDate": self.today.isoformat(),
            "endDate": self.future_date.isoformat(),
            "isActive": True,
        }

        response = self.client.post("/membership_status/", json=membership_data)
        ic(response.json())
        self.assertEqual(response.status_code, 200)

        # 測試創建重複會籍狀態（使用相同的數據）
        response = self.client.post("/membership_status/", json=membership_data)
        ic(response.json())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "會籍狀態已存在")

        # # 測試創建不存在會員的會籍狀態
        # invalid_member_data = membership_data.copy()
        # invalid_member_data["mContactNum"] = "9999999999"
        # response = self.client.post("/membership_status/", json=invalid_member_data)
        # ic(response.json())
        # self.assertEqual(response.status_code, 500)
        # self.assertEqual(response.json()["detail"], "會員不存在")

        # # 測試查詢不存在的會籍狀態
        # response = self.client.get("/membership_status/9999999999/")
        # ic(response.json())
        # self.assertEqual(response.status_code, 404)
        # self.assertEqual(response.json()["detail"], "會籍狀態不存在")

        # # 測試更新不存在的會籍狀態
        # update_data = {
        #     "startDate": self.today.isoformat(),
        #     "endDate": self.future_date.isoformat(),
        #     "isActive": False,
        # }
        # response = self.client.put("/membership_status/9999999999/", json=update_data)
        # ic(response.json())
        # self.assertEqual(response.status_code, 404)
        # self.assertEqual(response.json()["detail"], "會籍狀態不存在")


if __name__ == "__main__":
    unittest.main(verbosity=2)
