"""
會籍方案類別：負責會籍方案相關操作，如創建、更新、查詢等
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import logging
from database import get_connection
import sqlite3
from typing import Optional, TypedDict
from datetime import date


class MembershipPlanDict(TypedDict):
    """會籍方案資料結構定義"""

    gsNo: str
    salePrice: int
    planType: str
    planDuration: int


class MembershipPlan:
    """會籍方案類別：負責會籍方案相關操作，如創建、更新、查詢等"""

    @classmethod
    def create_membership_plan(
        cls,
        gsNo: str,
        salePrice: int,
        planType: str,
        planDuration: int,
    ) -> dict[str, str]:
        """創建新會籍方案"""
        conn = get_connection()
        if conn is None:
            return {"error": "數據庫連接失敗"}

        try:
            cursor = conn.cursor()

            # 先檢查會籍方案是否已存在
            cursor.execute(
                "SELECT COUNT(*) FROM MembershipPlan WHERE gsNo = ?",
                (gsNo,),
            )
            if cursor.fetchone()[0] > 0:
                return {"error": "會籍方案已存在"}

            # 插入會籍方案資料
            cursor.execute(
                """
                INSERT INTO MembershipPlan (gsNo, salePrice, planType, planDuration) VALUES (?, ?, ?, ?)
            """,
                (gsNo, salePrice, planType, planDuration),
            )
            conn.commit()
            logging.info(f"會籍方案創建成功: {gsNo}")
            return {"message": "會籍方案創建成功"}

        except sqlite3.IntegrityError:
            return {"error": "會籍方案編號已存在"}
        except sqlite3.Error as e:
            return {"error": f"創建會籍方案失敗: {e}"}
        finally:
            conn.close()

    @classmethod
    def get_membership_plan(cls, gsNo: str) -> Optional[MembershipPlanDict]:
        """查詢單一會籍方案資料"""
        conn = get_connection()
        if conn is None:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                    SELECT * 
                    FROM MembershipPlan 
                    WHERE gsNo = ?
                    """,
                (gsNo,),
            )

            membership_plan = cursor.fetchone()
            if not membership_plan:
                return None

            return dict(zip(MembershipPlanDict.__annotations__.keys(), membership_plan))

        except sqlite3.Error as e:
            logging.error(f"查詢會籍方案失敗: {e}")
            return None
        finally:
            conn.close()

    @classmethod
    def get_all_membership_plans(cls) -> list[MembershipPlanDict]:
        """查詢所有會籍方案資料"""
        conn = get_connection()
        if conn is None:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM MembershipPlan")
            membership_plans = cursor.fetchall()
            return [
                dict(zip(MembershipPlanDict.__annotations__.keys(), plan))
                for plan in membership_plans
            ]

        except sqlite3.Error as e:
            logging.error(f"查詢所有會籍方案失敗: {e}")
            return []
        finally:
            conn.close()

    @classmethod
    def update_membership_plan(cls, gsNo: str, **kwargs) -> dict[str, str]:
        """更新會籍方案資料"""
        conn = get_connection()
        if conn is None:
            return {"error": "數據庫連接失敗"}

        try:
            cursor = conn.cursor()
            # 構建更新語句
            update_sql = "UPDATE MembershipPlan SET "
            update_fields = []
            values = []
            for key, value in kwargs.items():
                if value is not None:
                    update_fields.append(f"{key} = ?")
                    values.append(value)

            if not update_fields:
                return {"message": "沒有需要更新的資料"}

            values.append(gsNo)  # 添加gsNo到values列表中

            # 執行更新
            cursor.execute(
                f"""
                UPDATE MembershipPlan
                SET {', '.join(update_fields)}
                WHERE gsNo = ?
                """,
                values,
            )

            if cursor.rowcount == 0:
                return {"error": "會籍方案不存在"}

            conn.commit()
            logging.info(f"會籍方案更新成功: {gsNo}")
            return {"message": "會籍方案更新成功"}

        except sqlite3.Error as e:
            return {"error": f"更新會籍方案失敗: {e}"}
        finally:
            conn.close()

    @classmethod
    def delete_membership_plan(cls, gsNo: str) -> dict[str, str]:
        """刪除會籍方案"""
        conn = get_connection()
        if conn is None:
            return {"error": "數據庫連接失敗"}

        try:
            cursor = conn.cursor()

            # 先檢查會籍方案是否存在
            cursor.execute(
                "SELECT COUNT(*) FROM MembershipPlan WHERE gsNo = ?", (gsNo,)
            )
            count = cursor.fetchone()[0]
            logging.info(f"找到 {count} 個會籍方案")

            if count == 0:
                logging.warning("會籍方案不存在")
                return {"error": "會籍方案不存在"}

            # 關閉外鍵約束
            cursor.execute("PRAGMA foreign_keys = OFF")
            logging.info("已關閉外鍵約束")

            # 刪除相關記錄（按照順序）
            tables = ["MembershipPlan", "OrderTable"]
            for table in tables:
                cursor.execute(f"DELETE FROM {table} WHERE gsNo = ?", (gsNo,))
                logging.info(f"從 {table} 刪除了 {cursor.rowcount} 條記錄")

            conn.commit()
            logging.info("刪除操作已提交")
            return {"message": "會籍方案刪除成功"}

        except sqlite3.Error as e:
            logging.error(f"刪除失敗: {e}")
            return {"error": f"刪除失敗: {e}"}
        finally:
            conn.close()


if __name__ == "__main__":
    # 設置日誌
    logging.basicConfig(level=logging.INFO)

    # 測試代碼
    print("\n查詢所有會籍方案:")
    membership_plans = MembershipPlan.get_all_membership_plans()
    for membership_plan in membership_plans:
        print(
            f"會籍方案編號: {membership_plan['gsNo']}, 方案類型: {membership_plan['planType']}"
        )
