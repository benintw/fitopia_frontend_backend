"""
不要用OrderTable, 用TransactionRecord就好
"""

"""
訂單表
"""

# schema
"""
    CREATE TABLE IF NOT EXISTS OrderTable (
        orderId INTEGER PRIMARY KEY AUTOINCREMENT,
        tNo INTEGER NOT NULL,
        gsNo VARCHAR(20) NOT NULL,
        salePrice INTEGER NOT NULL CHECK (salePrice > 0),
        amount INTEGER NOT NULL CHECK (amount > 0),
        paymentMethod VARCHAR(20) NOT NULL,
        orderType VARCHAR(10) NOT NULL,

        FOREIGN KEY (tNo) REFERENCES TransactionRecord(tNo)
            ON DELETE RESTRICT
            ON UPDATE CASCADE,
        CHECK (
            orderType IN ('product', 'membership') AND
            paymentMethod IN ('cash', 'credit card', 'e-transfer', 'reward points')
        )
    )
"""

# sample data
"""
    INSERT INTO TransactionRecord 
    (mContactNum, transDateTime, totalAmount) 
    VALUES 
    ('0912345678', '2024-03-01 10:00:00', 1500),
    ('0923456789', '2024-03-02 15:30:00', 2000),
    ('0934567890', '2024-03-03 18:45:00', 3000)
"""

"""
INSERT INTO OrderTable 
(tNo, gsNo, salePrice, amount, paymentMethod, orderType) 
VALUES 
('0912345678', 'P001', 500, 1, 'cash', 'product'),
('0923456789', 'P002', 1000, 2, 'credit card', 'product'),
('0912345678', 'M001', 1500, 1, 'e-transfer', 'membership')
"""

# explain
"""
    1. 訂單表包含訂單編號、交易編號、商品/會籍編號、銷售價格、數量、付款方式、訂單類型。
    2. 訂單表與交易表通過交易編號tNo建立外鍵關係。
    3. 訂單表通過商品/會籍編號gsNo與商品/會籍表建立外鍵關係。
    4. 訂單表的訂單類型orderType和付款方式paymentMethod必須是有效的值。

每一筆付款都有一個orderId。一個orderId可以有多筆付款，以下是範例資料:
Order	orderId	tNo	gsNo	salePrice	amount	paymentMethod	orderType
	123456	10101	MP001	699	6	credit_card	plan
	123444	10101	MP001	699	6	cash	plan
	123423	10101	P001	100	1	credit_card	product
	121241	10101	P002	150	1	credit_card	product
	234125	10101	P003	30	1	credit_card	product
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import TypedDict, Optional
from database import get_connection
import sqlite3
from datetime import datetime
import pytz
import logging
from icecream import ic


# TODO: 實現訂單模型 CRUD
#       1. 新增訂單
#       2. 查詢訂單
#       3. 更新訂單
#       4. 刪除訂單


class OrderTableDict(TypedDict):
    """訂單資料結構"""

    orderId: int
    tNo: int
    gsNo: str
    salePrice: int
    amount: int
    paymentMethod: str
    orderType: str


class OrderTable:
    """訂單表 CRUD"""

    @classmethod
    def create_orders_with_transaction(
        cls, mContactNum: str, orders: list[OrderTableDict]
    ) -> dict[str, str]:
        """創建訂單和對應的交易記錄"""
        conn = get_connection()
        if not conn:
            return {"error": "無法連接到資料庫"}

        try:
            cursor = conn.cursor()

            # 1. 計算所有訂單的總金額
            total_amount = sum(order["salePrice"] * order["amount"] for order in orders)

            # 2. 先創建交易記錄
            cursor.execute(
                """
                INSERT INTO TransactionRecord 
                (mContactNum, transDateTime, totalAmount)
                VALUES (?, ?, ?)
                """,
                (mContactNum, datetime.now(pytz.timezone("Asia/Taipei")), total_amount),
            )
            tNo = cursor.lastrowid  # 獲取新創建的交易編號

            # 3. 再創建所有訂單
            for order in orders:
                cursor.execute(
                    """
                    INSERT INTO OrderTable 
                    (tNo, gsNo, salePrice, amount, paymentMethod, orderType)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        tNo,  # 使用剛創建的交易編號
                        order["gsNo"],
                        order["salePrice"],
                        order["amount"],
                        order["paymentMethod"],
                        order["orderType"],
                    ),
                )

            conn.commit()  # 提交所有更改
            return {"message": f"交易記錄和訂單創建成功", "tNo": tNo}

        except sqlite3.Error as e:
            conn.rollback()  # 如果出錯，回滾所有更改
            return {"error": f"資料庫錯誤: {str(e)}"}
        finally:
            conn.close()


if __name__ == "__main__":

    # 準備訂單資料
    orders = [
        {
            "gsNo": "P001",
            "salePrice": 100,
            "amount": 2,
            "paymentMethod": "cash",
            "orderType": "product",
        },
        {
            "gsNo": "P002",
            "salePrice": 150,
            "amount": 1,
            "paymentMethod": "credit card",
            "orderType": "product",
        },
    ]

    # 一次性創建交易記錄和訂單
    result = OrderTable.create_orders_with_transaction(
        mContactNum="0912345678", orders=orders
    )

    if "error" in result:
        print(f"錯誤: {result['error']}")
    else:
        print(f"成功: {result['message']}")
        print(f"交易編號: {result['tNo']}")
