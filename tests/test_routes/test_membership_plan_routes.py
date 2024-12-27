"""
測試會籍方案相關 API
"""

from fastapi.testclient import TestClient
from main import app
import unittest
from icecream import ic
from database import get_connection


class TestMembershipPlanRoutes(unittest.TestCase):
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
        """在每個測試開始前創建測試數據"""
        self.client = TestClient(app)
        self.test_membership_plan = {
            "gsNo": "MP999",
            "salePrice": 3000,
            "planType": "測試會籍方案",
            "planDuration": 30,
        }

    def test_1_create_membership_plan(self):
        """測試創建會籍方案 API"""
        response = self.client.post(
            "/membership_plans/", json=self.test_membership_plan
        )
        ic(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "會籍方案創建成功"})

    def test_2_get_membership_plan(self):
        """測試查詢單一會籍方案 API"""
        response = self.client.get(
            f"/membership_plans/{self.test_membership_plan['gsNo']}/"
        )
        ic(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.test_membership_plan)

    def test_3_get_all_membership_plans(self):
        """測試查詢所有會籍方案 API"""
        response = self.client.get("/membership_plans/")
        ic(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_4_update_membership_plan(self):
        """測試更新會籍方案 API"""
        update_data = {"salePrice": 3500, "planType": "季費會員", "planDuration": 90}
        response = self.client.put(
            f"/membership_plans/{self.test_membership_plan['gsNo']}/", json=update_data
        )
        ic(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "會籍方案更新成功"})

    def test_5_error_cases(self):
        """測試錯誤情況"""
        # 測試創建重複會籍方案
        response = self.client.post(
            "/membership_plans/", json=self.test_membership_plan
        )
        self.assertEqual(response.status_code, 400)

        # 測試查詢不存在的會籍方案
        response = self.client.get("/membership_plans/9999999999/")
        self.assertEqual(response.status_code, 404)

        # 測試刪除不存在的會籍方案
        response = self.client.delete("/membership_plans/9999999999/")
        self.assertEqual(response.status_code, 404)

    def test_6_delete_membership_plan(self):
        """測試刪除會籍方案 API"""
        # 先創建一個會籍方案
        self.client.post("/membership_plans/", json=self.test_membership_plan)

        # 測試刪除會籍方案
        response = self.client.delete(
            f"/membership_plans/{self.test_membership_plan['gsNo']}/"
        )
        ic(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "會籍方案刪除成功"})

        # 確認會籍方案已被刪除
        response = self.client.get(
            f"/membership_plans/{self.test_membership_plan['gsNo']}/"
        )
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
