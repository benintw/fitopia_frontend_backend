"""
會員管理類別：負責會員相關操作，如創建、更新、查詢等
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import logging
from database import get_connection
import sqlite3
from typing import Optional, TypedDict
from datetime import date


class MemberDict(TypedDict):
    """
    會員資料結構定義

    欄位說明：
    - mContactNum: 會員電話（主鍵）
    - mName: 會員姓名
    - mEmail: 電子郵件
    - mDob: 生日
    - mEmergencyName: 緊急聯絡人姓名
    - mEmergencyNum: 緊急聯絡人電話
    - mBalance: 帳戶餘額
    - mRewardPoints: 點數
    - creation_date: 創建日期
    """

    mContactNum: str
    mName: str
    mEmail: str
    mDob: str
    mEmergencyName: str
    mEmergencyNum: str
    mBalance: int
    mRewardPoints: int
    creation_date: date


class Member:
    """
    會員類別：負責會員相關操作，如創建、更新、查詢等
    """

    @classmethod
    def create_member(
        cls,
        mContactNum: str,
        mName: str,
        mEmail: str,
        mDob: str,
        mEmergencyName: str,
        mEmergencyNum: str,
        mBalance: int = 0,
        mRewardPoints: int = 100,
    ) -> dict[str, str]:
        """
        創建新會員

        Args:
            mContactNum: 會員電話
            mName: 會員姓名
            mEmail: 電子郵件
            mDob: 生日 (YYYY-MM-DD)
            mEmergencyName: 緊急聯絡人姓名
            mEmergencyNum: 緊急聯絡人電話
            mBalance: 帳戶餘額（預設：0）
            mRewardPoints: 點數（預設：0）

        Returns:
            dict: 包含操作結果訊息
        """
        conn = get_connection()
        if conn is None:
            return {"error": "數據庫連接失敗"}

        try:
            cursor = conn.cursor()

            # 先檢查會員是否已存在
            cursor.execute(
                "SELECT COUNT(*) FROM Member WHERE mContactNum = ?",
                (mContactNum,),
            )
            if cursor.fetchone()[0] > 0:
                return {"error": "會員已存在"}  # 明確返回錯誤

            # 插入會員資料
            cursor.execute(
                """
                INSERT INTO Member (
                    mContactNum, mName, mEmail, mDob,
                    mEmergencyName, mEmergencyNum,
                    mBalance, mRewardPoints
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    mContactNum,
                    mName,
                    mEmail,
                    mDob,
                    mEmergencyName,
                    mEmergencyNum,
                    mBalance,
                    mRewardPoints,
                ),
            )

            conn.commit()
            logging.info(f"會員創建成功: {mName} ({mContactNum})")
            return {"message": "會員創建成功"}

        except sqlite3.IntegrityError:
            return {"error": "會員電話已存在"}
        except sqlite3.Error as e:
            return {"error": f"創建會員失敗: {e}"}
        finally:
            conn.close()

    @classmethod
    def get_member(cls, mContactNum: str) -> Optional[MemberDict]:
        """
        查詢單一會員資料

        Args:
            mContactNum: 會員電話

        Returns:
            Optional[MemberDict]: 會員資料，如果不存在則返回 None
        """
        conn = get_connection()
        if conn is None:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT *
                FROM Member 
                WHERE mContactNum = ?
            """,
                (mContactNum,),
            )

            member = cursor.fetchone()
            if not member:
                return None

            return dict(zip(MemberDict.__annotations__.keys(), member))

        except sqlite3.Error as e:
            logging.error(f"查詢會員失敗: {e}")
            return None
        finally:
            conn.close()

    @classmethod
    def get_all_members(cls) -> list[MemberDict]:
        """
        查詢所有會員資料

        Returns:
            list[MemberDict]: 會員資料列表
        """
        conn = get_connection()
        if conn is None:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM Member
            """
            )

            members = cursor.fetchall()
            return [
                dict(zip(MemberDict.__annotations__.keys(), member))
                for member in members
            ]

        except sqlite3.Error as e:
            logging.error(f"查詢所有會員失敗: {e}")
            return []
        finally:
            conn.close()

    @classmethod
    def update_member(
        cls,
        mContactNum: str,
        mName: Optional[str] = None,
        mEmail: Optional[str] = None,
        mDob: Optional[str] = None,
        mEmergencyName: Optional[str] = None,
        mEmergencyNum: Optional[str] = None,
        mBalance: Optional[int] = None,
        mRewardPoints: Optional[int] = None,
    ) -> dict[str, str]:
        """
        更新會員資料

        Args:
            mContactNum: 會員電話（必填）
            其他參數為可選，只更新有提供的欄位

        Returns:
            dict: 包含操作結果訊息
        """
        conn = get_connection()
        if conn is None:
            return {"error": "數據庫連接失敗"}

        try:
            cursor = conn.cursor()

            # 構建更新語句
            update_fields = []
            values = []

            if mName is not None:
                update_fields.append("mName = ?")
                values.append(mName)
            if mEmail is not None:
                update_fields.append("mEmail = ?")
                values.append(mEmail)
            if mDob is not None:
                update_fields.append("mDob = ?")
                values.append(mDob)
            if mEmergencyName is not None:
                update_fields.append("mEmergencyName = ?")
                values.append(mEmergencyName)
            if mEmergencyNum is not None:
                update_fields.append("mEmergencyNum = ?")
                values.append(mEmergencyNum)
            if mBalance is not None:
                update_fields.append("mBalance = ?")
                values.append(mBalance)
            if mRewardPoints is not None:
                update_fields.append("mRewardPoints = ?")
                values.append(mRewardPoints)

            if not update_fields:
                return {"message": "沒有需要更新的資料"}

            values.append(mContactNum)

            # 執行更新
            cursor.execute(
                f"""
                UPDATE Member
                SET {', '.join(update_fields)}
                WHERE mContactNum = ?
            """,
                values,
            )

            if cursor.rowcount == 0:
                return {"error": "會員不存在"}

            conn.commit()
            logging.info(f"會員資料更新成功: {mContactNum}")
            return {"message": "會員資料更新成功"}

        except sqlite3.Error as e:
            return {"error": f"更新會員資料失敗: {e}"}
        finally:
            conn.close()

    @classmethod
    def delete_member(cls, mContactNum: str) -> dict[str, str]:
        """
        刪除會員

        Args:
            mContactNum: 會員電話

        Returns:
            dict: 包含操作結果訊息
        """
        logging.info(f"開始刪除會員: {mContactNum}")  # 添加日誌

        conn = get_connection()
        if conn is None:
            logging.error("數據庫連接失敗")  # 添加日誌
            return {"error": "數據庫連接失敗"}

        try:
            cursor = conn.cursor()

            # 先檢查會員是否存在
            cursor.execute(
                "SELECT COUNT(*) FROM Member WHERE mContactNum = ?", (mContactNum,)
            )
            count = cursor.fetchone()[0]
            logging.info(f"找到 {count} 個會員")  # 添加日誌

            if count == 0:
                logging.warning("會員不存在")  # 添加日誌
                return {"error": "會員不存在"}

            # 關閉外鍵約束
            cursor.execute("PRAGMA foreign_keys = OFF")
            logging.info("已關閉外鍵約束")  # 添加日誌

            # 刪除相關記錄（按照順序）
            tables = [
                "MembershipStatus",
                "CheckInRecord",
                "Member",
                "TransactionRecord",
                "MemberPhoto",
            ]
            for table in tables:
                cursor.execute(
                    f"DELETE FROM {table} WHERE mContactNum = ?", (mContactNum,)
                )
                logging.info(f"從 {table} 刪除了 {cursor.rowcount} 條記錄")  # 添加日誌

            conn.commit()
            logging.info("刪除操作已提交")  # 添加日誌

            return {"message": "會員刪除成功"}

        except sqlite3.Error as e:
            logging.error(f"刪除失敗: {e}")  # 添加日誌
            return {"error": f"刪除會員失敗: {e}"}
        finally:
            if conn:
                cursor.execute("PRAGMA foreign_keys = ON")
                conn.commit()
                conn.close()
                logging.info("數據庫連接已關閉")  # 添加日誌


if __name__ == "__main__":
    # 設置日誌
    logging.basicConfig(level=logging.INFO)

    # 測試代碼
    print("\n查詢所有會員:")
    members = Member.get_all_members()
    for member in members:
        print(f"姓名: {member['mName']}, 電話: {member['mContactNum']}")
