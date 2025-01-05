"""
交易記錄的測試
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import unittest
from gym_management.backend.database import get_connection
from models.transaction_record import TransactionRecord
from models.member import Member
from models.product import Product
from models.membership_plan import MembershipPlan
from models.pydantic_models import TransactionDetail, PaymentMethod
from datetime import datetime
import pytz
from icecream import ic


class TestTransactionRecordModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        在所有測試開始前執行一次：
        1. 關閉外鍵約束
        2. 清空相關表格
        3. 重新啟用外鍵約束
        """
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
        """測試前準備：創建測試會員和交易記錄資料"""
        # 創建測試會員
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
            "transaction_dict": {
                "mContactNum": "0912345699",
                "gsNo": "P001",
                "count": 1,
                "unitPrice": 500,
                "discount": 1.0,
                "paymentMethod": "cash",
            },
        }

        self.test_transaction2 = {
            "transaction_dict": {
                "mContactNum": "0912345699",
                "gsNo": "M001",
                "count": 1,
                "unitPrice": 1000,
                "discount": 1.0,
                "paymentMethod": "cash",
            },
        }

    def test_1_create_transaction_record(self):
        """測試創建交易記錄"""
        result = TransactionRecord.create_transaction_record(
            transaction_dict=self.test_transaction1["transaction_dict"],
        )
        result2 = TransactionRecord.create_transaction_record(
            transaction_dict=self.test_transaction2["transaction_dict"],
        )
        self.assertIn("message", result)
        self.assertEqual(result["message"], "交易記錄創建成功")
        self.assertIn("message", result2)
        self.assertEqual(result2["message"], "交易記錄創建成功")

    def test_2_get_member_transactions(self):
        """測試獲取會員的交易記錄"""
        # 確保有交易記錄
        result = TransactionRecord.create_transaction_record(
            transaction_dict=self.test_transaction1["transaction_dict"],
        )
        result2 = TransactionRecord.create_transaction_record(
            transaction_dict=self.test_transaction2["transaction_dict"],
        )

        records = TransactionRecord.get_member_transaction_record(
            self.test_transaction1["transaction_dict"]["mContactNum"]
        )
        ic(records)
        self.assertIsNotNone(records)
        self.assertIsInstance(records, list)

    def test_3_get_all_transactions(self):
        """測試獲取所有交易記錄"""
        # 確保有交易記錄
        self.test_1_create_transaction_record()

        result = TransactionRecord.get_all_transaction_records()
        # ic(result)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_4_update_transaction_record(self):
        """測試更新交易記錄"""
        # 確保有交易記錄
        result2 = TransactionRecord.create_transaction_record(
            transaction_dict=self.test_transaction2["transaction_dict"],
        )

        records = TransactionRecord.get_member_transaction_record(
            self.test_transaction2["transaction_dict"]["mContactNum"]
        )
        ic(records[0]["tNo"])

        new_amount = 2000
        updates = {
            "count": 2,
            "unitPrice": new_amount,
            "discount": 0.5,
        }
        tNo = records[0]["tNo"]

        result = TransactionRecord.update_transaction_record(
            mContactNum=self.test_transaction2["transaction_dict"]["mContactNum"],
            tNo=tNo,
            updates=updates,
        )
        self.assertIn("message", result)
        self.assertEqual(result["message"], "交易記錄更新成功")

        updated_transaction = TransactionRecord.get_member_transaction_record(
            mContactNum=self.test_transaction2["transaction_dict"]["mContactNum"]
        )
        ic(updated_transaction)
        self.assertEqual(updated_transaction[0]["totalAmount"], new_amount)

    def test_5_delete_transaction_record(self):
        """測試刪除交易記錄"""
        # 確保有交易記錄
        # 確保有交易記錄
        result2 = TransactionRecord.create_transaction_record(
            transaction_dict=self.test_transaction2["transaction_dict"],
        )

        records = TransactionRecord.get_member_transaction_record(
            self.test_transaction2["transaction_dict"]["mContactNum"]
        )

        tNo = records[0]["tNo"]

        result = TransactionRecord.delete_transaction_record(
            mContactNum=self.test_transaction2["transaction_dict"]["mContactNum"],
            tNo=tNo,
        )
        ic(result)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "交易記錄刪除成功")

    @classmethod
    def tearDownClass(cls):
        """在所有測試結束後清理數據"""
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("PRAGMA foreign_keys = OFF")
            cursor.execute("DELETE FROM TransactionRecord")
            cursor.execute("DELETE FROM Member")
            conn.commit()
        finally:
            cursor.execute("PRAGMA foreign_keys = ON")
            conn.commit()
            conn.close()


if __name__ == "__main__":
    unittest.main()
