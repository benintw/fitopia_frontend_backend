"""
會員照片類別：負責會員照片相關操作，如創建、更新、查詢等
"""

from typing import Optional, TypedDict
from database import get_connection
import sqlite3
import logging
from datetime import datetime

from icecream import ic


class MemberPhotoDict(TypedDict):
    """會員照片資料結構定義"""

    mPhotoName: str
    mPhoto: bytes
    mContactNum: str
    isActive: bool


class MemberPhoto:
    """會員照片類別：負責會員照片相關操作，如創建、更新、查詢等"""

    @classmethod
    def create_member_photo(cls, mPhoto: bytes, mContactNum: str) -> dict[str, str]:
        """創建會員照片"""
        conn = get_connection()
        if not conn:
            return {"error": "數據庫連接失敗"}
        try:
            cursor = conn.cursor()

            # 生成照片名稱
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            mPhotoName = f"member_{mContactNum}_{timestamp}.jpg"

            # 將該會員的其他照片設為inactive
            cursor.execute(
                """
                UPDATE MemberPhoto 
                SET isActive = 0 
                WHERE mContactNum = ?
                """,
                (mContactNum,),
            )

            # 插入照片資料
            cursor.execute(
                """
                INSERT INTO MemberPhoto (mPhotoName, mPhoto, mContactNum, isActive) 
                VALUES (?, ?, ?, 1)
                """,
                (mPhotoName, mPhoto, mContactNum),
            )
            conn.commit()
            return {"success": "會員照片創建成功"}

        except sqlite3.Error as e:
            return {"error": f"數據庫操作失敗: {e}"}
        finally:
            conn.close()

    @classmethod
    def get_member_photo(cls, mContactNum: str) -> Optional[MemberPhotoDict]:
        """查詢會員照片"""
        conn = get_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM MemberPhoto
                WHERE mContactNum = ?
                AND isActive = 1
                """,
                (mContactNum,),
            )
            photo_info = cursor.fetchone()
            if not photo_info:
                return None

            return dict(zip(MemberPhotoDict.__annotations__.keys(), photo_info))

        except sqlite3.Error as e:
            logging.error(f"查詢會員照片操作失敗: {e}")
            return None

        finally:
            conn.close()

    @classmethod
    def get_all_photos(cls) -> list[MemberPhotoDict]:
        """查詢所有會員照片"""
        conn = get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM MemberPhoto")
            photos = cursor.fetchall()
            return [
                dict(zip(MemberPhotoDict.__annotations__.keys(), photo))
                for photo in photos
            ]

        except sqlite3.Error as e:
            logging.error(f"查詢所有會員照片操作失敗: {e}")
            return []
        finally:
            conn.close()

    @classmethod
    def update_member_photo(cls, mContactNum: str, new_photo: bytes) -> dict[str, str]:
        """更新會員照片"""
        conn = get_connection()
        if not conn:
            return {"error": "數據庫連接失敗"}

        try:
            cursor = conn.cursor()

            # 獲取當前照片的mPhotoName
            cursor.execute(
                """
                SELECT mPhotoName
                FROM MemberPhoto
                WHERE mContactNum = ? 
                AND isActive = 1    
                """,
                (mContactNum,),
            )

            result = cursor.fetchone()
            if not result:
                return {"error": "會員照片不存在"}

            mPhotoName = result[0]

            # 插入新照片記錄
            cursor.execute(
                """
                UPDATE MemberPhoto
                SET mPhoto = ?
                WHERE mPhotoName = ?
                """,
                (new_photo, mPhotoName),
            )

            if cursor.rowcount == 0:
                return {"error": "會員照片更新失敗"}

            conn.commit()
            return {"success": "會員照片更新成功"}
        except sqlite3.Error as e:
            return {"error": f"數據庫操作失敗: {e}"}
        finally:
            conn.close()

    @classmethod
    def delete_member_photo(cls, mContactNum: str) -> dict[str, str]:
        """刪除會員照片"""
        conn = get_connection()
        if not conn:
            return {"error": "數據庫連接失敗"}

        try:
            cursor = conn.cursor()

            # 先檢查會員照片是否存在
            cursor.execute(
                "SELECT COUNT(*) FROM MemberPhoto WHERE mContactNum = ?", (mContactNum,)
            )
            count = cursor.fetchone()[0]
            if count == 0:
                return {"error": "會員照片不存在"}

            # 關閉外鍵約束
            cursor.execute("PRAGMA foreign_keys = OFF")

            tables = ["MemberPhoto"]

            for table in tables:
                cursor.execute(
                    f"DELETE FROM {table} WHERE mContactNum = ?", (mContactNum,)
                )
                logging.info(f"從 {table} 刪除了 {cursor.rowcount} 條記錄")

            conn.commit()
            logging.info("刪除操作已提交")
            return {"success": "會員照片刪除成功"}
        except sqlite3.Error as e:
            return {"error": f"數據庫操作失敗: {e}"}
        finally:
            if conn:
                cursor.execute("PRAGMA foreign_keys = ON")
                conn.commit()
                conn.close()
                logging.info("數據庫連接已關閉")
