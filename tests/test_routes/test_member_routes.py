"""
測試會員相關 API
"""

from fastapi.testclient import TestClient
from main import app
import unittest
from icecream import ic
from database import get_connection


class TestMemberRoutes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """在所有測試開始前清理數據庫"""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # 關閉外鍵約束
            cursor.execute("PRAGMA foreign_keys = OFF")

            # 清空相關表格
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

    def setUp(self):
        """設置測試客戶端和測試數據"""
        self.client = TestClient(app)
        self.test_member = {
            "mContactNum": "0912345678",
            "mName": "測試會員",
            "mEmail": "test@example.com",
            "mDob": "1990-01-01",
            "mEmergencyName": "緊急聯絡人",
            "mEmergencyNum": "0987654321",
            "mBalance": 1000,
            "mRewardPoints": 100,
        }

    def test_1_create_member(self):
        """測試創建會員 API"""
        response = self.client.post("/members/", json=self.test_member)
        ic(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "會員創建成功"})

    def test_2_get_member(self):
        """測試查詢單一會員 API"""
        response = self.client.get(f"/members/{self.test_member['mContactNum']}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["mName"], self.test_member["mName"])

    def test_3_get_all_members(self):
        """測試查詢所有會員 API"""
        response = self.client.get("/members/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_4_update_member(self):
        """測試更新會員資料 API"""
        update_data = {"mEmail": "updated@example.com", "mBalance": 2000}
        response = self.client.put(
            f"/members/{self.test_member['mContactNum']}/", json=update_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "會員資料更新成功"})

    def test_5_error_cases(self):
        """測試錯誤情況"""
        # 測試創建重複會員
        response = self.client.post("/members/", json=self.test_member)
        self.assertEqual(response.status_code, 400)

        # 測試查詢不存在的會員
        response = self.client.get("/members/9999999999/")
        self.assertEqual(response.status_code, 404)

        # 測試更新不存在的會員
        response = self.client.put(
            "/members/9999999999/", json={"mEmail": "nonexist@example.com"}
        )
        self.assertEqual(response.status_code, 404)

    def test_6_delete_member(self):
        """測試刪除會員 API"""
        # 先創建一個會員
        self.client.post("/members/", json=self.test_member)

        # 測試刪除會員
        response = self.client.delete(f"/members/{self.test_member['mContactNum']}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "會員刪除成功"})

        # 確認會員已被刪除
        response = self.client.get(f"/members/{self.test_member['mContactNum']}/")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
