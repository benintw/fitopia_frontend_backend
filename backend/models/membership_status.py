"""
會籍狀態管理類別：負責會籍狀態相關操作，如創建、更新、查詢等
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import logging
from database import get_connection
import sqlite3
from typing import Optional, TypedDict
from datetime import date


"""
    CREATE TABLE IF NOT EXISTS MembershipStatus (
        sid INTEGER PRIMARY KEY AUTOINCREMENT,
        mContactNum VARCHAR(20) NOT NULL,
        startDate DATE NOT NULL,
        endDate DATE NOT NULL,
        isActive INTEGER DEFAULT 1,
        FOREIGN KEY (mContactNum) REFERENCES Member(mContactNum)
            ON DELETE RESTRICT
            ON UPDATE CASCADE,
        CHECK (endDate > startDate)
    )
"""


class MembershipStatusDict(TypedDict):
    """
    會籍狀態資料結構定義
    """

    sId: int
    mContactNum: str
    startDate: date
    endDate: date
    isActive: bool


class MembershipStatus:
    """
    會籍狀態類別：負責會籍狀態相關操作，如創建、更新、查詢等
    """

    @classmethod
    def create_membership_status(
        cls,
        mContactNum: str,
        startDate: date,
        endDate: date,
        isActive: bool = True,
    ) -> dict[str, str]:
        """
        創建會籍狀態
        """

        conn = get_connection()
        if not conn:
            return {"error": "數據庫連接失敗"}

        try:
            cursor = conn.cursor()

            if endDate <= startDate:
                return {"error": "結束日期不能小於開始日期"}

            # 檢查會籍狀態是否已存在
            cursor.execute(
                "SELECT COUNT(*) FROM MembershipStatus WHERE mContactNum = ? AND isActive = 1",
                (mContactNum,),
            )
            count = cursor.fetchone()[0]
            if count > 0:
                return {"error": "會籍狀態已存在"}

            cursor.execute(
                "INSERT INTO MembershipStatus (mContactNum, startDate, endDate, isActive) VALUES (?, ?, ?, ?)",
                (mContactNum, startDate, endDate, isActive),
            )
            conn.commit()
            return {"message": "會籍狀態創建成功"}

        except sqlite3.IntegrityError as e:
            return {"error": f"資料完整性錯誤: {str(e)}"}
        except sqlite3.Error as e:
            return {"error": f"數據庫錯誤: {str(e)}"}
        finally:
            conn.close()

    @classmethod
    def get_membership_status(cls, mContactNum: str) -> Optional[MembershipStatusDict]:
        """
        獲取會籍狀態
        """

        conn = get_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM MembershipStatus WHERE mContactNum = ?
                AND isActive = 1
                """,
                (mContactNum,),
            )
            result = cursor.fetchone()
            if not result:
                return None
            else:
                return dict(zip(MembershipStatusDict.__annotations__.keys(), result))
        except sqlite3.Error as e:
            logging.error(f"查詢會籍狀態失敗: {e}")
            return None
        finally:
            conn.close()

    @classmethod
    def get_all_membership_status(cls) -> list[MembershipStatusDict]:
        """
        獲取所有有效會籍狀態
        """

        conn = get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM MembershipStatus WHERE isActive = 1")
            result = cursor.fetchall()
            return [
                dict(zip(MembershipStatusDict.__annotations__.keys(), row))
                for row in result
            ]
        except sqlite3.Error as e:
            return []
        finally:
            conn.close()

    @classmethod
    def update_membership_status(
        cls, mContactNum: str, startDate: date, endDate: date, isActive: bool
    ):
        """
        更新會籍狀態
        """

        conn = get_connection()
        if not conn:
            return {"error": "數據庫連接失敗"}

        try:
            cursor = conn.cursor()

            update_fields = []
            values = []

            if startDate is not None:
                update_fields.append("startDate = ?")
                values.append(startDate)
            if endDate is not None:
                update_fields.append("endDate = ?")
                values.append(endDate)
            if isActive is not None:
                update_fields.append("isActive = ?")
                values.append(isActive)

            if not update_fields:
                return {"message": "沒有需要更新的資料"}

            values.append(mContactNum)

            cursor.execute(
                f"""
                UPDATE MembershipStatus 
                SET {', '.join(update_fields)}
                WHERE mContactNum = ?
            """,
                values,
            )

            if cursor.rowcount == 0:
                return {"error": "會籍狀態不存在"}

            conn.commit()
            logging.info(f"會籍狀態更新成功: {mContactNum}")
            return {"message": "會籍狀態更新成功"}
        except sqlite3.Error as e:
            return {"error": f"數據庫錯誤: {str(e)}"}
        finally:
            conn.close()

    @classmethod
    def delete_membership_status(cls, mContactNum: str) -> dict[str, str]:
        """
        刪除會籍狀態
        """

        logging.info(f"開始刪除會籍狀態: {mContactNum}")

        conn = get_connection()
        if not conn:
            return {"error": "數據庫連接失敗"}

        try:
            cursor = conn.cursor()

            # 先檢查會籍狀態是否存在
            cursor.execute(
                "SELECT COUNT(*) FROM MembershipStatus WHERE mContactNum = ?",
                (mContactNum,),
            )
            count = cursor.fetchone()[0]
            logging.info(f"找到 {count} 個會籍狀態")

            if count == 0:
                logging.warning("會籍狀態不存在")
                return {"error": "會籍狀態不存在"}

            # 關閉外鍵約束
            cursor.execute("PRAGMA foreign_keys = OFF")
            logging.info("已關閉外鍵約束")

            tables = ["MembershipStatus"]

            for table in tables:
                cursor.execute(
                    f"DELETE FROM {table} WHERE mContactNum = ?", (mContactNum,)
                )
                logging.info(f"從 {table} 刪除了 {cursor.rowcount} 條記錄")

            conn.commit()
            logging.info("刪除操作已提交")

            return {"message": "會籍狀態刪除成功"}

        except sqlite3.Error as e:
            logging.error(f"刪除失敗: {e}")
            return {"error": f"刪除會籍狀態失敗: {e}"}
        finally:
            if conn:
                cursor.execute("PRAGMA foreign_keys = ON")
                conn.commit()
                conn.close()
                logging.info("數據庫連接已關閉")


if __name__ == "__main__":
    # 設置日誌
    logging.basicConfig(level=logging.INFO)

    # 測試代碼
    print("\n查詢所有會籍狀態:")
    membership_statuses = MembershipStatus.get_all_membership_status()
    for membership_status in membership_statuses:
        print(membership_status)
