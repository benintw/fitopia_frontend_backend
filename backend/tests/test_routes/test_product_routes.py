"""
測試商品相關 API
"""

from fastapi.testclient import TestClient
from gym_management.backend.main import app
import unittest
from icecream import ic
from gym_management.backend.database import get_connection


class TestProductRoutes(unittest.TestCase):

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
        self.test_product = {
            "gsNo": "P111",
            "pName": "測試商品",
            "salePrice": 100,
            "pImage": "gym_management/imgs/water_bottle.jpg",
        }

    def test_1_create_product(self):
        """測試創建商品 API"""
        response = self.client.post("/products/", json=self.test_product)
        ic(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "商品創建成功"})

    def test_2_get_product(self):
        """測試查詢單一商品 API"""
        response = self.client.get(f"/products/{self.test_product['gsNo']}/")
        ic(response.json())
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["pName"], self.test_product["pName"])

    def test_3_get_all_products(self):
        """測試查詢所有商品 API"""
        response = self.client.get("/products/")
        ic(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_4_update_product(self):
        """測試更新商品 API"""
        update_data = {"pName": "更新商品", "salePrice": 150}
        response = self.client.put(
            f"/products/{self.test_product['gsNo']}/", json=update_data
        )
        ic(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "商品更新成功"})

    def test_5_error_cases(self):
        """測試錯誤情況"""
        # 測試創建重複商品
        response = self.client.post("/products/", json=self.test_product)
        self.assertEqual(response.status_code, 400)

        # 測試查詢不存在的商品
        response = self.client.get("/products/9999999999/")
        self.assertEqual(response.status_code, 404)

        # 測試更新不存在的商品
        response = self.client.put("/products/9999999999/", json=self.test_product)
        self.assertEqual(response.status_code, 404)

    def test_6_delete_product(self):
        """測試刪除商品 API"""
        response = self.client.delete(f"/products/{self.test_product['gsNo']}/")
        ic(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "商品刪除成功"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
