"""
商品管理類別：負責商品相關操作，如創建、更新、查詢等
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import logging
from database import get_connection
import sqlite3
from typing import Optional, TypedDict


class ProductDict(TypedDict):
    """商品資料結構定義"""

    gsNo: str
    salePrice: int
    pName: str
    pImage: Optional[bytes]


class Product:
    """商品類別：負責商品相關操作，如創建、更新、查詢等"""

    @classmethod
    def create_product(
        cls, gsNo: str, salePrice: int, pName: str, pImage: Optional[bytes] = None
    ) -> dict[str, str]:
        """創建商品"""
        conn = get_connection()
        if conn is None:
            return {"error": "數據庫連接失敗"}

        try:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT COUNT(*) FROM Product WHERE gsNo = ?",
                (gsNo,),
            )

            if cursor.fetchone()[0] > 0:
                return {"error": "商品已存在"}

            cursor.execute(
                """
                INSERT INTO Product (gsNo, salePrice, pName, pImage) 
                VALUES (?, ?, ?, ?)
                """,
                (gsNo, salePrice, pName, pImage),
            )

            conn.commit()
            logging.info(f"商品創建成功: {pName} ({gsNo})")
            return {"message": "商品創建成功"}
        except sqlite3.IntegrityError:
            return {"error": "商品已存在"}
        except sqlite3.Error as e:
            return {"error": f"創建商品失敗: {e}"}
        finally:
            conn.close()

    @classmethod
    def get_product(cls, gsNo: str) -> Optional[ProductDict]:
        """取得商品"""
        conn = get_connection()
        if conn is None:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM Product WHERE gsNo = ?
                """,
                (gsNo,),
            )
            product = cursor.fetchone()
            if not product:
                return None

            return dict(zip(ProductDict.__annotations__.keys(), product))

        except sqlite3.Error as e:
            logging.error(f"查詢商品失敗: {e}")
            return None

        finally:
            conn.close()

    @classmethod
    def get_all_products(cls) -> list[ProductDict]:
        """取得所有商品"""
        conn = get_connection()
        if conn is None:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Product")
            products = cursor.fetchall()
            return [
                dict(zip(ProductDict.__annotations__.keys(), product))
                for product in products
            ]
        except sqlite3.Error as e:
            logging.error(f"查詢所有商品失敗: {e}")
            return []
        finally:
            conn.close()

    @classmethod
    def update_product(
        cls, gsNo: str, salePrice: int, pName: str, pImage: Optional[bytes] = None
    ) -> dict[str, str]:
        """更新商品"""
        conn = get_connection()
        if conn is None:
            return {"error": "數據庫連接失敗"}

        try:
            cursor = conn.cursor()

            update_fields = []
            values = []

            if salePrice is not None:
                update_fields.append("salePrice = ?")
                values.append(salePrice)
            if pName is not None:
                update_fields.append("pName = ?")
                values.append(pName)
            if pImage is not None:
                update_fields.append("pImage = ?")
                values.append(pImage)

            if not update_fields:
                return {"message": "沒有需要更新的資料"}

            values.append(gsNo)

            cursor.execute(
                f"""
                UPDATE Product 
                SET {', '.join(update_fields)} 
                WHERE gsNo = ?""",
                values,
            )

            if cursor.rowcount == 0:
                return {"error": "商品不存在"}

            conn.commit()
            logging.info(f"商品更新成功: {gsNo}")
            return {"message": "商品更新成功"}

        except sqlite3.Error as e:
            return {"error": f"更新商品失敗: {e}"}
        finally:
            conn.close()

    @classmethod
    def delete_product(cls, gsNo: str):
        """刪除商品"""

        logging.info(f"開始刪除商品: {gsNo}")

        conn = get_connection()
        if conn is None:
            logging.error("數據庫連接失敗")
            return {"error": "數據庫連接失敗"}

        try:
            cursor = conn.cursor()

            # 先檢查商品是否存在
            cursor.execute("SELECT COUNT(*) FROM Product WHERE gsNo = ?", (gsNo,))
            count = cursor.fetchone()[0]
            logging.info(f"找到 {count} 個商品")

            if count == 0:
                logging.warning("商品不存在")
                return {"error": "商品不存在"}

            # 關閉外鍵約束
            cursor.execute("PRAGMA foreign_keys = OFF")
            logging.info("已關閉外鍵約束")

            # 刪除相關記錄（按照順序）
            tables = ["Product", "OrderTable"]
            for table in tables:
                cursor.execute(f"DELETE FROM {table} WHERE gsNo = ?", (gsNo,))
                logging.info(f"從 {table} 刪除了 {cursor.rowcount} 條記錄")

            conn.commit()
            logging.info(f"商品刪除成功: {gsNo}")
            return {"message": "商品刪除成功"}

        except sqlite3.Error as e:
            logging.error(f"刪除商品失敗: {e}")
            return {"error": f"刪除商品失敗: {e}"}
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
    print("\n查詢所有商品:")
    products = Product.get_all_products()
    for product in products:
        print(f"商品編號: {product['gsNo']}, 商品名稱: {product['pName']}")
