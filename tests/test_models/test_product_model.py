"""
商品類別測試
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import unittest
from models.product import Product
from database import get_connection

from icecream import ic


class TestProduct(unittest.TestCase):
    """測試商品類別的所有方法"""

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
        """測試前準備：創建測試商品資料"""

        self.test_product = {
            "gsNo": "P112",
            "pName": "測試商品",
            "salePrice": 100,
            "pImage": "gym_management/imgs/water_bottle.jpg",
        }

    def test_1_create_product(self):
        """測試創建商品"""
        # 先刪除可能存在的測試商品
        deleted_product = Product.delete_product(self.test_product["gsNo"])
        ic(deleted_product)

        result = Product.create_product(**self.test_product)
        ic(result)
        self.assertEqual(result.get("message"), "商品創建成功")

    def test_2_get_product(self):
        """測試查詢單一商品"""
        # 確保測試商品存在
        Product.create_product(**self.test_product)

        product = Product.get_product(self.test_product["gsNo"])
        ic(product)
        self.assertIsNotNone(product)
        self.assertEqual(product["pName"], self.test_product["pName"])

    def test_3_get_all_products(self):
        """測試查詢所有商品"""
        # 確保至少有一個商品
        Product.create_product(**self.test_product)

        products = Product.get_all_products()
        ic(products)
        self.assertGreater(len(products), 0)

    def test_4_update_product(self):
        """測試更新商品"""
        # 確保測試商品存在
        Product.create_product(**self.test_product)

        update_data = {
            "gsNo": self.test_product["gsNo"],
            "pName": "更新測試商品",
            "salePrice": 150,
        }
        result = Product.update_product(**update_data)
        self.assertEqual(result.get("message"), "商品更新成功")

        updated_product = Product.get_product(self.test_product["gsNo"])
        ic(updated_product)
        self.assertEqual(updated_product["pName"], "更新測試商品")
        self.assertEqual(updated_product["salePrice"], 150)

    def test_5_delete_product(self):
        """測試刪除商品"""
        # 確保測試商品存在
        Product.create_product(**self.test_product)

        deleted_product = Product.delete_product(self.test_product["gsNo"])
        ic(deleted_product)
        self.assertEqual(deleted_product.get("message"), "商品刪除成功")

    def test_6_error_cases(self):
        """測試錯誤情況"""
        # 確保測試商品存在
        Product.create_product(**self.test_product)

        # 測試創建重複商品
        duplicate_result = Product.create_product(**self.test_product)
        ic(duplicate_result)
        self.assertIn("error", duplicate_result)

        # 測試更新不存在的商品
        non_exist_update = Product.update_product(
            gsNo="P999", pName="更新測試商品", salePrice=150
        )
        ic(non_exist_update)
        self.assertIn("error", non_exist_update)

        # 測試刪除不存在的商品
        non_exist_delete = Product.delete_product("P999")
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
