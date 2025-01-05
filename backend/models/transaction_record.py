"""
交易記錄
"""

# new  schema
"""
    CREATE TABLE IF NOT EXISTS TransactionRecord (
        tNo INTEGER PRIMARY KEY AUTOINCREMENT,
        mContactNum VARCHAR(20) NOT NULL,
        transDateTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        gsNo VARCHAR(20) NOT NULL,
        count INTEGER NOT NULL CHECK (count > 0),
        unitPrice INTEGER NOT NULL CHECK (unitPrice > 0),
        discount REAL NOT NULL DEFAULT 1 CHECK (discount <= 1 AND discount > 0),
        totalAmount INTEGER NOT NULL CHECK (totalAmount > 0),
        paymentMethod VARCHAR(20) NOT NULL CHECK (paymentMethod IN ('cash', 'credit_card', 'e_transfer', 'reward_points')),
        FOREIGN KEY (mContactNum) REFERENCES Member(mContactNum)
    )
"""

# sample data
"""
    INSERT INTO TransactionRecord 
    (mContactNum, transDateTime, gsNo, count, unitPrice, discount, totalAmount, paymentMethod) 
    VALUES 
    ('0912345678', '2024-03-01 10:00:00', 'P001', 2, 500, 1.0, 1000, 'cash'),
    ('0912345678', '2024-03-01 10:00:00', 'P002', 1, 500, 1.0, 500, 'credit_card'),
    ('0923456789', '2024-03-02 15:30:00', 'M001', 1, 2000, 0.9, 1800, 'e_transfer'),
    ('0934567890', '2024-03-03 18:45:00', 'P003', 3, 1000, 0.8, 2400, 'reward_points')
"""


"""

The transactionRecord is associated with a member,
and the member's mContactNum is used as the foreign key.

Implement the CRUD operations for the transactionRecord model.

"""
import sys
from pathlib import Path

# 將專案根目錄加入 Python 路徑
sys.path.append(str(Path(__file__).resolve().parent.parent))
from typing import TypedDict, Optional
from database import get_connection
import sqlite3
from datetime import datetime
import pytz
import logging
from icecream import ic
from pydantic import BaseModel, Field
from typing import Literal


class TransactionRecordDict(TypedDict):
    """交易記錄資料結構"""

    tNo: int
    mContactNum: str
    transDateTime: datetime
    gsNo: str
    count: int
    unitPrice: int
    discount: float
    totalAmount: int
    paymentMethod: str


class TransactionDetail(BaseModel):
    """交易詳情模型"""

    gsNo: str
    count: int = Field(gt=0)
    unitPrice: int = Field(gt=0)
    discount: float = Field(default=1.0, gt=0, le=1)
    paymentMethod: Literal["cash", "credit_card", "e_transfer", "reward_points"]


class TransactionRecord:
    """交易記錄模型"""

    @classmethod
    def create_transaction_record(cls, transaction_dict: dict) -> dict[str, str]:
        """新增交易記錄

        transaction_dict: {
            "mContactNum": str,
            "gsNo": str,
            "count": int,
            "unitPrice": int,
            "discount": float,
            "paymentMethod": Literal["cash", "credit_card", "e_transfer", "reward_points"]
        }

        """

        conn = get_connection()
        if not conn:
            return {"error": "數據庫連接失敗"}

        try:
            cursor = conn.cursor()

            # 檢查會員是否存在
            cursor.execute(
                "SELECT COUNT(*) FROM Member WHERE mContactNum = ?",
                (transaction_dict["mContactNum"],),
            )
            member_count = cursor.fetchone()[0]
            if member_count == 0:
                return {"error": "會員不存在"}

            # 使用台北時區
            taipei_tz = pytz.timezone("Asia/Taipei")
            trans_datetime = datetime.now(taipei_tz)

            cursor.execute(
                """
                SELECT
                    CASE
                        WHEN EXISTS (SELECT 1 FROM Product WHERE gsNo = ?) THEN 'product'
                        WHEN EXISTS (SELECT 1 FROM MembershipPlan WHERE gsNo = ?) THEN 'membership_plan'
                        ELSE 'not_found'
                    END
                """,
                (transaction_dict["gsNo"], transaction_dict["gsNo"]),
            )
            item_type = cursor.fetchone()[0]
            if item_type == "not_found":
                return {"error": "商品或會籍方案不存在"}

            # 計算總金額
            total_amount = (
                transaction_dict["unitPrice"]
                * transaction_dict["count"]
                * transaction_dict["discount"]
            )

            # 新增交易記錄
            cursor.execute(
                """
                INSERT INTO TransactionRecord (mContactNum, transDateTime, gsNo, count, unitPrice, discount, totalAmount, paymentMethod) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    transaction_dict["mContactNum"],
                    trans_datetime,
                    transaction_dict["gsNo"],
                    transaction_dict["count"],
                    transaction_dict["unitPrice"],
                    transaction_dict["discount"],
                    total_amount,
                    transaction_dict["paymentMethod"],
                ),
            )

            conn.commit()
            return {"message": "交易記錄創建成功"}
        except sqlite3.Error as e:
            return {"error": f"數據庫操作失敗: {e}"}
        finally:
            conn.close()

    @classmethod
    def get_member_transaction_record(
        cls, mContactNum: str
    ) -> list[TransactionRecordDict]:
        """查詢會員的所有交易記錄"""

        conn = get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()

            # 檢查會員是否存在
            cursor.execute(
                "SELECT COUNT(*) FROM Member WHERE mContactNum = ?", (mContactNum,)
            )
            member_count = cursor.fetchone()[0]
            if member_count == 0:
                return []

            # 查詢該會員交易記錄
            cursor.execute(
                """
                SELECT * FROM TransactionRecord WHERE mContactNum = ?
                ORDER BY transDateTime DESC
                """,
                (mContactNum,),
            )
            transaction_records = cursor.fetchall()

            if not transaction_records:
                return []

            # 將查詢結果轉換為TransactionRecordDict
            return [
                dict(zip(TransactionRecordDict.__annotations__.keys(), record))
                for record in transaction_records
            ]
        except sqlite3.Error as e:
            logging.error(f"查詢交易記錄失敗: {str(e)}")
            return []
        finally:
            conn.close()

    @classmethod
    def get_all_transaction_records(cls) -> list[TransactionRecordDict]:
        """查詢所有交易記錄"""

        conn = get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM TransactionRecord")
            transaction_records = cursor.fetchall()
            return [
                dict(zip(TransactionRecordDict.__annotations__.keys(), record))
                for record in transaction_records
            ]
        except sqlite3.Error as e:
            logging.error(f"查詢交易記錄失敗: {str(e)}")
            return []
        finally:
            conn.close()

    @classmethod
    def update_transaction_record(
        cls, mContactNum: str, tNo: int, updates: dict
    ) -> dict[str, str]:
        """更新交易記錄"""

        conn = get_connection()
        if not conn:
            return {"error": "數據庫連接失敗"}

        try:
            cursor = conn.cursor()

            # 檢查會員是否存在
            cursor.execute(
                "SELECT COUNT(*) FROM Member WHERE mContactNum = ?", (mContactNum,)
            )
            member_count = cursor.fetchone()[0]
            if member_count == 0:
                return {"error": "會員不存在"}

            # 檢查交易紀錄是否存在
            cursor.execute(
                "SELECT COUNT(*) FROM TransactionRecord WHERE tNo = ?",
                (tNo,),
            )
            transaction_count = cursor.fetchone()[0]
            if transaction_count == 0:
                return {"error": "交易紀錄不存在"}

            new_gsNo = updates.get("gsNo", None)
            new_count = updates.get("count", None)
            new_unitPrice = updates.get("unitPrice", None)
            new_discount = updates.get("discount", None)
            new_paymentMethod = updates.get("paymentMethod", None)

            update_fields = []
            update_values = []

            if new_gsNo is not None:
                update_fields.append("gsNo = ?")
                update_values.append(new_gsNo)
            if new_count is not None:
                if not isinstance(new_count, int) or new_count <= 0:
                    return {"error": "無效的數量值"}
                update_fields.append("count = ?")
                update_values.append(new_count)
            if new_unitPrice is not None:
                if not isinstance(new_unitPrice, int) or new_unitPrice <= 0:
                    return {"error": "無效的單價值"}
                update_fields.append("unitPrice = ?")
                update_values.append(new_unitPrice)
            if new_discount is not None:
                if (
                    not isinstance(new_discount, (int, float))
                    or new_discount <= 0
                    or new_discount > 1
                ):
                    return {"error": "無效的折扣值"}
                update_fields.append("discount = ?")
                update_values.append(new_discount)
            if new_paymentMethod is not None:
                valid_methods = ["cash", "credit_card", "e_transfer", "reward_points"]
                if new_paymentMethod not in valid_methods:
                    return {"error": "無效的支付方式"}
                update_fields.append("paymentMethod = ?")
                update_values.append(new_paymentMethod)

            if not update_fields:
                return {"error": "沒有有效的更新欄位"}

            # 更新交易記錄
            update_values.append(tNo)  # 添加 WHERE 條件的參數
            sql = f"""
                UPDATE TransactionRecord 
                SET {', '.join(update_fields)}
                WHERE tNo = ?
            """
            cursor.execute(sql, tuple(update_values))

            if any(field in ["count", "unitPrice", "discount"] for field in updates):
                # 更新總金額
                cursor.execute(
                    """
                    UPDATE TransactionRecord 
                    SET totalAmount = (count * unitPrice * discount)
                    WHERE tNo = ?
                    """,
                    (tNo,),
                )
            conn.commit()
            return {"message": "交易記錄更新成功"}

        except sqlite3.Error as e:
            return {"error": f"數據庫操作失敗: {e}"}
        finally:
            conn.close()

    @classmethod
    def delete_transaction_record(cls, mContactNum: str, tNo: int) -> dict[str, str]:
        """刪除交易記錄"""

        conn = get_connection()
        if not conn:
            return {"error": "數據庫連接失敗"}

        try:
            cursor = conn.cursor()

            # 檢查會員是否存在
            cursor.execute(
                "SELECT COUNT(*) FROM Member WHERE mContactNum = ?", (mContactNum,)
            )
            member_count = cursor.fetchone()[0]
            if member_count == 0:
                return {"error": "會員不存在"}

            # 檢查交易紀錄是否存在
            cursor.execute(
                "SELECT COUNT(*) FROM TransactionRecord WHERE tNo = ?",
                (tNo,),
            )
            transaction_count = cursor.fetchone()[0]
            if transaction_count == 0:
                return {"error": "交易紀錄不存在"}

            # 刪除交易記錄
            cursor.execute(
                "DELETE FROM TransactionRecord WHERE tNo = ?",
                (tNo,),
            )
            conn.commit()
            return {"message": "交易記錄刪除成功"}

        except sqlite3.Error as e:
            return {"error": f"數據庫操作失敗: {e}"}
        finally:
            conn.close()


if __name__ == "__main__":

    transaction_detail = TransactionDetail(
        gsNo="M001", count=2, unitPrice=100, discount=1, paymentMethod="cash"
    )

    ic(TransactionRecord.create_transaction_record("0912345678", transaction_detail))
    ic(TransactionRecord.get_member_transaction_record("0912345678"))
