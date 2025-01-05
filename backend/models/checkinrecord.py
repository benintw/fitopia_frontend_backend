"""
打卡記錄
"""

"""
    CREATE TABLE IF NOT EXISTS CheckInRecord (
        checkInNo INTEGER PRIMARY KEY AUTOINCREMENT,
        mContactNum VARCHAR(20) NOT NULL,
        checkInDatetime DATETIME NOT NULL,
        checkOutDatetime DATETIME,
        checkInStatus INTEGER DEFAULT 1,
        checkOutStatus INTEGER DEFAULT 0,
        FOREIGN KEY (mContactNum) REFERENCES Member(mContactNum)
            ON DELETE RESTRICT
            ON UPDATE CASCADE,
        CHECK (checkOutDatetime > checkInDatetime)
    )
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from typing import Optional, TypedDict
from database import get_connection
import sqlite3
import logging
from datetime import datetime, timezone
import pytz
from icecream import ic


class CheckInRecordDict(TypedDict):
    """打卡記錄資料結構定義"""

    checkInNo: int
    mContactNum: str
    checkInDatetime: datetime
    checkOutDatetime: datetime
    checkInStatus: int
    checkOutStatus: int


class CheckInRecord:
    """打卡記錄類別：負責打卡記錄相關操作，如創建、更新、查詢等"""

    @classmethod
    def create_checkin_record(cls, mContactNum: str) -> dict[str, str]:
        """創建打卡記錄
        當會員進場時，以mContactNum為索引，
        創建一條打卡記錄，checkInDatetime為現在時間，checkInStatus為1，checkOutStatus為0

        """
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

            # 檢查是否有未結束的打卡記錄
            cursor.execute(
                "SELECT COUNT(*) FROM CheckInRecord WHERE mContactNum = ? AND checkOutStatus = 0",
                (mContactNum,),
            )
            if cursor.fetchone()[0] > 0:
                return {"error": "已有未結束的打卡記錄"}

            # 使用台北時區
            taipei_tz = pytz.timezone("Asia/Taipei")
            current_time = datetime.now(taipei_tz)
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

            # 創建打卡記錄
            cursor.execute(
                "INSERT INTO CheckInRecord (mContactNum, checkInDatetime, checkInStatus) VALUES (?, ?, 1)",
                (mContactNum, formatted_time),
            )
            conn.commit()
            return {"message": "打卡記錄創建成功"}
        except Exception as e:
            conn.rollback()
            return {"error": str(e)}
        finally:
            conn.close()

    @classmethod
    def get_checkin_record(cls, mContactNum: str) -> list[CheckInRecordDict]:
        """查詢打卡記錄"""
        conn = get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM CheckInRecord 
                WHERE mContactNum = ?
                ORDER BY checkInDatetime DESC
                """,
                (mContactNum,),
            )
            checkin_record = cursor.fetchall()
            if not checkin_record:
                return []

            return [
                dict(zip(CheckInRecordDict.__annotations__.keys(), record))
                for record in checkin_record
            ]
        except Exception as e:
            logging.error(f"查詢打卡記錄操作失敗: {e}")
            return []
        finally:
            conn.close()

    @classmethod
    def get_all_checkin_records(cls) -> list[CheckInRecordDict]:
        """查詢所有打卡記錄"""
        conn = get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM CheckInRecord")
            checkin_records = cursor.fetchall()
            return [
                dict(zip(CheckInRecordDict.__annotations__.keys(), record))
                for record in checkin_records
            ]
        except Exception as e:
            logging.error(f"查詢所有打卡記錄操作失敗: {e}")
            return []
        finally:
            conn.close()

    @classmethod
    def update_checkin_record(cls, mContactNum: str) -> dict[str, str]:
        """更新打卡記錄
        當會員退場時，以mContactNum為索引，
        更新checkOutDatetime為現在時間，checkOutStatus為1(代表退場)
        """
        conn = get_connection()
        if not conn:
            return {"error": "數據庫連接失敗"}

        try:
            cursor = conn.cursor()

            # 使用台北時區
            taipei_tz = pytz.timezone("Asia/Taipei")
            current_time = datetime.now(taipei_tz)
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            # 檢查打卡記錄是否存在
            cursor.execute(
                "SELECT COUNT(*) FROM CheckInRecord WHERE mContactNum = ?",
                (mContactNum,),
            )
            count = cursor.fetchone()[0]
            if count == 0:
                return {"error": "打卡記錄不存在"}

            cursor.execute(
                """
                UPDATE CheckInRecord SET checkOutDatetime = ?, checkOutStatus = 1 
                WHERE mContactNum = ?
                AND checkOutStatus = 0
                AND checkInNo = (
                    SELECT MAX(checkInNo) FROM CheckInRecord WHERE mContactNum = ?
                    AND checkOutStatus = 0
                )
                """,
                (formatted_time, mContactNum, mContactNum),
            )
            conn.commit()
            return {"message": "打卡記錄更新成功"}
        except Exception as e:
            conn.rollback()
            return {"error": str(e)}
        finally:
            conn.close()

    @classmethod
    def delete_checkin_record(cls, mContactNum: str) -> dict[str, str]:
        """刪除打卡記錄"""
        conn = get_connection()
        if not conn:
            return {"error": "數據庫連接失敗"}

        try:
            cursor = conn.cursor()

            # 先檢查打卡記錄是否存在
            cursor.execute(
                "SELECT COUNT(*) FROM CheckInRecord WHERE mContactNum = ?",
                (mContactNum,),
            )
            count = cursor.fetchone()[0]
            if count == 0:
                return {"error": "打卡記錄不存在"}

            # 關閉外鍵約束
            cursor.execute("PRAGMA foreign_keys = OFF")

            tables = ["CheckInRecord"]

            for table in tables:
                cursor.execute(
                    f"DELETE FROM {table} WHERE mContactNum = ?", (mContactNum,)
                )
                logging.info(f"從 {table} 刪除了 {cursor.rowcount} 條記錄")

            conn.commit()
            logging.info("刪除操作已提交")
            return {"success": "打卡記錄刪除成功"}
        except Exception as e:
            conn.rollback()
            return {"error": str(e)}
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
    print("\n查詢所有打卡記錄:")
    records = CheckInRecord.get_all_check_in_records()
    ic(records)
