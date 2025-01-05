"""
測試交易記錄相關 API
"""

from fastapi.testclient import TestClient
from gym_management.backend.main import app
import unittest
from icecream import ic
from gym_management.backend.database import get_connection
from models.member import Member
from models.transaction_record import TransactionRecord
from models.product import Product
from models.membership_plan import MembershipPlan
from models.pydantic_models import TransactionDetail, PaymentMethod
from datetime import datetime
import pytz


class TestTransactionRecordRoutes(unittest.TestCase):
    """測試交易記錄類別的所有方法"""

    @classmethod
    def setUpClass(cls):
        """在所有測試開始前執行一次"""

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("PRAGMA foreign_keys = OFF")
            cursor.execute("DELETE FROM TransactionRecord")
            cursor.execute("DELETE FROM Member")
            cursor.execute("DELETE FROM Product")
            cursor.execute("DELETE FROM MembershipPlan")
            conn.commit()
        finally:
            cursor.execute("PRAGMA foreign_keys = ON")
            conn.commit()
            conn.close()

    def setUp(self):
        """每個測試方法執行前都會執行"""
        self.client = TestClient(app)
        # 測試會員資料
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
        # 創建測試會員
        Member.create_member(**self.test_member)

        # 創建測試商品
        self.test_product = {
            "gsNo": "P001",
            "salePrice": 500,
            "pName": "測試商品",
            "pImage": "test.jpg",
        }
        Product.create_product(**self.test_product)

        # 創建測試會籍

        self.test_membership_plan = {
            "gsNo": "M001",
            "salePrice": 1000,
            "planType": "月費會員",
            "planDuration": 1,
        }
        MembershipPlan.create_membership_plan(**self.test_membership_plan)

        # 創建測試交易記錄
        self.test_transaction1 = {
            "mContactNum": "0912345699",
            "gsNo": "P001",
            "count": 1,
            "unitPrice": 500,
            "discount": 1.0,
            "paymentMethod": PaymentMethod.CASH,
        }

        self.test_transaction2 = {
            "mContactNum": "0912345699",
            "gsNo": "M001",
            "count": 1,
            "unitPrice": 1000,
            "discount": 1.0,
            "paymentMethod": PaymentMethod.CASH,
        }

    def test_1_create_transaction_record(self):
        """測試創建交易記錄 API"""

        transaction_data = {
            "mContactNum": "0912345699",
            "gsNo": "P001",
            "count": 1,
            "unitPrice": 500,
            "discount": 1.0,
            "paymentMethod": PaymentMethod.CASH,
        }

        response = self.client.post("/transaction_records/", json=transaction_data)
        ic(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "交易記錄創建成功"})

        # 測試無效金額
        invalid_transaction = transaction_data.copy()
        invalid_transaction["unitPrice"] = -100
        response = self.client.post("/transaction_records/", json=invalid_transaction)
        ic(response.json())
        ic(response.status_code)
        self.assertEqual(response.status_code, 422)

        # 測試不存在的會員
        invalid_transaction = transaction_data.copy()
        invalid_transaction["mContactNum"] = "9999999999"
        response = self.client.post("/transaction_records/", json=invalid_transaction)
        ic(response.json())
        self.assertEqual(response.status_code, 400)

    def test_4_get_all_transaction_record(self):
        """測試查詢所有交易記錄 API"""
        # 先創建兩筆交易
        self.client.post("/transaction_records/", json=self.test_transaction1)
        self.client.post("/transaction_records/", json=self.test_transaction2)

        # 查詢所有交易記錄
        response = self.client.get("/transaction_records/")
        ic(response.json())
        self.assertEqual(response.status_code, 200)
        # 驗證返回的是列表
        self.assertIsInstance(response.json(), list)

    def test_3_get_member_transaction_record(self):
        """測試查詢會員所有交易記錄 API"""
        # 先創建兩筆交易
        self.client.post("/transaction_records/", json=self.test_transaction1)
        self.client.post("/transaction_records/", json=self.test_transaction2)

        # 查詢會員所有交易記錄
        response = self.client.get(
            f"/transaction_records/member/{self.test_member['mContactNum']}/"
        )
        ic(response.json())

        self.assertEqual(response.status_code, 200)
        # 驗證返回的是列表
        self.assertIsInstance(response.json(), list)

        # 驗證每筆記錄的內容
        for transaction in response.json():
            self.assertEqual(
                transaction["mContactNum"], self.test_member["mContactNum"]
            )
            self.assertIn("tNo", transaction)
            self.assertIn("transDateTime", transaction)
            self.assertIn("gsNo", transaction)
            self.assertIn("count", transaction)
            self.assertIn("unitPrice", transaction)
            self.assertIn("discount", transaction)
            self.assertIn("paymentMethod", transaction)

    def test_5_update_transaction_record(self):
        """測試更新交易記錄 API"""
        # 先創建一筆交易
        create_response = self.client.post(
            "/transaction_records/", json=self.test_transaction1
        )
        ic(create_response.json())
        self.assertEqual(create_response.status_code, 200)
        # 獲取交易記錄以取得 tNo
        get_response = self.client.get(
            f"/transaction_records/member/{self.test_transaction1['mContactNum']}/"
        )
        self.assertEqual(get_response.status_code, 200)
        transactions = get_response.json()
        self.assertTrue(len(transactions) > 0)
        tNo = transactions[0]["tNo"]
        ic(tNo)
        # 更新交易記錄
        update_data = {"unitPrice": 6000, "count": 2, "discount": 1.0}

        update_response = self.client.put(
            f"/transaction_records/{self.test_transaction1['mContactNum']}/{tNo}",
            json=update_data,
        )
        ic(update_response.json())
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json(), {"message": "交易記錄更新成功"})

        # 查詢更新後的交易記錄
        get_updated_response = self.client.get(
            f"/transaction_records/member/{self.test_transaction1['mContactNum']}/"
        )
        self.assertEqual(get_updated_response.status_code, 200)
        updated_transaction = next(
            (t for t in get_updated_response.json() if t["tNo"] == tNo), None
        )
        self.assertIsNotNone(updated_transaction)
        self.assertEqual(updated_transaction["unitPrice"], update_data["unitPrice"])
        self.assertEqual(updated_transaction["count"], update_data["count"])
        self.assertEqual(updated_transaction["discount"], update_data["discount"])

    def test_6_delete_transaction_record(self):
        """測試刪除交易記錄 API"""
        # 先創建一筆交易
        create_response = self.client.post(
            "/transaction_records/", json=self.test_transaction1
        )
        ic(create_response.json())
        self.assertEqual(create_response.status_code, 200)
        # 獲取交易記錄以取得 tNo
        get_response = self.client.get(
            f"/transaction_records/member/{self.test_transaction1['mContactNum']}/"
        )
        self.assertEqual(get_response.status_code, 200)
        transactions = get_response.json()
        self.assertTrue(len(transactions) > 0)
        tNo = transactions[0]["tNo"]

        # 刪除交易記錄
        delete_response = self.client.delete(
            f"/transaction_records/{self.test_transaction1['mContactNum']}/{tNo}/"
        )
        ic(delete_response.json())
        self.assertEqual(delete_response.status_code, 200)

        self.assertEqual(delete_response.json(), {"message": "交易記錄刪除成功"})

        # 查詢刪除後的交易記錄
        response = self.client.get(
            f"/transaction_records/member/{self.test_transaction1['mContactNum']}/{tNo}"
        )
        ic(response.json())
        self.assertEqual(response.status_code, 404)

    @classmethod
    def tearDownClass(cls):
        """在所有測試結束後清理數據"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute("DELETE FROM TransactionRecord")
        cursor.execute("DELETE FROM Member")
        cursor.execute("PRAGMA foreign_keys = ON")
        conn.commit()
        conn.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
