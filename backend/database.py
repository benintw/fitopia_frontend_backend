"""
健身房管理系統數據庫模組

這個模組負責：
1. 數據庫的初始化
2. 表格的創建
3. 範例數據的插入
4. 數據庫連接的管理

表格結構：
- MemberPhoto: 會員照片
- Member: 會員基本資料
- MembershipStatus: 會籍狀態
- CheckInRecord: 進出場紀錄
- TransactionRecord: 交易紀錄
- Product: 商品資料
- MembershipPlan: 會籍方案
- OrderTable: 訂單資料
"""

import os
import sqlite3
from pathlib import Path
import logging
from models.pydantic_models import PaymentMethod


# 確保數據庫文件在正確的目錄
DB_PATH = Path(__file__).parent / "gym.db"


def get_connection():
    """
    建立並返回數據庫連接

    Returns:
        sqlite3.Connection | None: 數據庫連接對象，連接失敗時返回 None
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        print(f"數據庫連接錯誤: {e}")
        return None


def execute_query(query, error_message="執行查詢時發生錯誤"):
    """
    執行 SQL 查詢的通用函數

    Args:
        query (str): SQL 查詢語句
        error_message (str): 發生錯誤時顯示的訊息

    Returns:
        bool: 查詢執行成功返回 True，失敗返回 False
    """
    conn = get_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"{error_message}: {e}")
        return False
    finally:
        conn.close()


# 設置日誌
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# 表格創建 SQL 語句

CREATE_MEMBER_TABLE = """
    CREATE TABLE IF NOT EXISTS Member (
        mContactNum VARCHAR(20) PRIMARY KEY,
        mName VARCHAR(50) NOT NULL,
        mEmail VARCHAR(100) NOT NULL,
        mDob DATE NOT NULL,
        mEmergencyName VARCHAR(25) NOT NULL,
        mEmergencyNum VARCHAR(20) NOT NULL,
        mBalance INTEGER DEFAULT 0,
        mRewardPoints INTEGER DEFAULT 100,
        creation_date DATE DEFAULT (DATE('now', 'localtime'))
    )
"""

CREATE_MEMBER_PHOTO_TABLE = """
    CREATE TABLE IF NOT EXISTS MemberPhoto (
        mPhotoName VARCHAR(50) PRIMARY KEY,
        mPhoto BLOB NOT NULL,
        mContactNum VARCHAR(20) NOT NULL,
        isActive INTEGER DEFAULT 1,
        
        FOREIGN KEY (mContactNum) REFERENCES Member(mContactNum)
            ON DELETE CASCADE
            ON UPDATE CASCADE
    )
"""


CREATE_MEMBERSHIP_STATUS_TABLE = """
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


CREATE_CHECK_IN_RECORD_TABLE = """
    CREATE TABLE IF NOT EXISTS CheckInRecord (
        checkInNo INTEGER PRIMARY KEY AUTOINCREMENT,
        mContactNum VARCHAR(20) NOT NULL,
        checkInDatetime DATETIME NOT NULL DEFAULT (datetime('now', 'localtime')),
        checkOutDatetime DATETIME,
        checkInStatus INTEGER DEFAULT 1,
        checkOutStatus INTEGER DEFAULT 0,
        FOREIGN KEY (mContactNum) REFERENCES Member(mContactNum)
        CHECK (checkOutDatetime IS NULL OR checkOutDatetime > checkInDatetime)
    )
"""


CREATE_PRODUCT_TABLE = """
    CREATE TABLE IF NOT EXISTS Product (
        gsNo VARCHAR(20) PRIMARY KEY,
        salePrice INTEGER NOT NULL CHECK (salePrice > 0),
        pName VARCHAR(100) NOT NULL,
        pImage BLOB
    )
"""

CREATE_MEMBERSHIP_PLAN_TABLE = """
    CREATE TABLE IF NOT EXISTS MembershipPlan (
        gsNo VARCHAR(20) PRIMARY KEY,
        salePrice INTEGER NOT NULL CHECK (salePrice > 0),
        planType VARCHAR(50) NOT NULL,
        planDuration INTEGER NOT NULL CHECK (planDuration > 0)
    )
"""

CREATE_TRANSACTION_TABLE = """
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


def create_all_tables():
    """
    創建所有必要的數據庫表格

    包含以下表格：
    - MemberPhoto: 會員照片
    - Member: 會員基本資料
    - MembershipStatus: 會籍狀態
    - CheckInRecord: 進出場紀錄
    - TransactionRecord: 交易紀錄
    - Product: 商品資料
    - MembershipPlan: 會籍方案
    Returns:
        bool: 所有表格創建成功返回 True，任一表格創建失敗返回 False
    """

    tables = [
        ("MemberPhoto", CREATE_MEMBER_PHOTO_TABLE),
        ("Member", CREATE_MEMBER_TABLE),
        ("MembershipStatus", CREATE_MEMBERSHIP_STATUS_TABLE),
        ("CheckInRecord", CREATE_CHECK_IN_RECORD_TABLE),
        ("Product", CREATE_PRODUCT_TABLE),
        ("MembershipPlan", CREATE_MEMBERSHIP_PLAN_TABLE),
        ("TransactionRecord", CREATE_TRANSACTION_TABLE),
    ]

    for table_name, create_query in tables:
        if not execute_query(create_query, f"創建 {table_name} 表格時發生錯誤"):
            print(f"創建 {table_name} 表格失敗")
            return False
    return True


def insert_sample_data():
    """
    插入範例資料到所有表格

    插入順序：
    1. 會員照片
    2. 會員基本資料
    3. 會籍狀態
    4. 進出場紀錄
    5. 交易紀錄
    6. 商品資料
    7. 會籍方案

    Returns:
        bool: 所有資料插入成功返回 True，任一插入失敗返回 False
    """
    conn = get_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()

        # 1. 先清空所有表格（按照外鍵約束的相反順序）
        tables = [
            "OrderTable",
            "MembershipPlan",
            "Product",
            "TransactionRecord",
            "CheckInRecord",
            "MembershipStatus",
            "Member",
            "MemberPhoto",
        ]

        print("\n清空表格...")
        for table in tables:
            try:
                cursor.execute(f"DELETE FROM {table}")
                print(f"✓ 清空 {table}")
            except sqlite3.Error as e:
                print(f"✗ 清空 {table} 失敗: {e}")

        # 3. 插入會員
        print("\n插入會員...")
        try:
            cursor.execute(
                """
                INSERT INTO Member 
                (mContactNum, mName, mEmail, mDob, mEmergencyName, mEmergencyNum, mBalance, mRewardPoints) 
                VALUES 
                ('0912345678', '王小明', 'wang@example.com', '1990-01-01', '王大明', '0987654321', 1000, 100),
                ('0923456789', '李小華', 'lee@example.com', '1992-03-15', '李大華', '0976543210', 500, 50),
                ('0934567890', '張小美', 'chang@example.com', '1988-12-25', '張大美', '0965432109', 2000, 200)
            """
            )
            print("✓ 會員資料插入成功")
        except sqlite3.Error as e:
            print(f"✗ 會員資料插入失敗: {e}")
            raise

        # 2. 插入會員照片
        print("\n插入會員照片...")
        try:
            cursor.execute(
                """
                INSERT INTO MemberPhoto (mPhotoName, mPhoto, mContactNum) VALUES 
                ('default1.jpg', X'00', '0912345678'),
                ('default2.jpg', X'00', '0923456789'),
                ('default3.jpg', X'00', '0934567890')
            """
            )
            print("✓ 會員照片插入成功")
        except sqlite3.Error as e:
            print(f"✗ 會員照片插入失敗: {e}")
            raise

        # 4. 插入會籍狀態
        print("\n插入會籍狀態...")
        try:
            cursor.execute(
                """
                INSERT INTO MembershipStatus 
                (mContactNum, startDate, endDate, isActive) 
                VALUES 
                ('0912345678', '2024-01-01', '2024-12-31', 1),
                ('0923456789', '2024-02-01', '2024-07-31', 1),
                ('0934567890', '2024-03-01', '2025-02-28', 1)
            """
            )
            print("✓ 會籍狀態插入成功")
        except sqlite3.Error as e:
            print(f"✗ 會籍狀態插入失敗: {e}")
            raise

        # 5. 插入進場紀錄
        print("\n插入進場紀錄...")
        try:
            cursor.execute(
                """
                INSERT INTO CheckInRecord 
                (mContactNum, checkInDatetime, checkOutDatetime, checkInStatus, checkOutStatus) 
                VALUES 
                ('0912345678', '2024-03-15 09:00:00', '2024-03-15 11:00:00', 1, 1),
                ('0923456789', '2024-03-15 14:00:00', '2024-03-15 16:00:00', 1, 1),
                ('0934567890', '2024-03-15 18:00:00', '2024-03-15 20:00:00', 1, 1),
                ('0912345678', '2024-03-15 09:00:00', NULL, 1, 0)
            """
            )
            print("✓ 進場紀錄插入成功")
        except sqlite3.Error as e:
            print(f"✗ 進場紀錄插入失敗: {e}")
            raise

        # 7. 插入商品
        print("\n插入商品...")
        try:
            cursor.execute(
                """
                INSERT INTO Product 
                (gsNo, salePrice, pName) 
                VALUES 
                ('P001', 500, '運動毛巾'),
                ('P002', 1000, '運動水壺'),
                ('P003', 2000, '運動背包')
            """
            )
            print("✓ 商品插入成功")
        except sqlite3.Error as e:
            print(f"✗ 商品插入失敗: {e}")
            raise

        # 8. 插入會籍方案
        print("\n插入會籍方案...")
        try:
            cursor.execute(
                """
                INSERT INTO MembershipPlan 
                (gsNo, salePrice, planType, planDuration) 
                VALUES 
                ('M001', 1500, '月費會員', 1),
                ('M002', 4000, '季費會員', 3),
                ('M003', 15000, '年費會員', 12)
            """
            )
            print("✓ 會籍方案插入成功")
        except sqlite3.Error as e:
            print(f"✗ 會籍方案插入失敗: {e}")
            raise

        # 6. 插入交易紀錄
        print("\n插入交易紀錄...")
        try:
            cursor.execute(
                f"""
                INSERT INTO TransactionRecord 
                (mContactNum, transDateTime, gsNo, count, unitPrice, discount, totalAmount, paymentMethod) 
                VALUES 
                ('0912345678', '2024-03-01 10:00:00', 'P001', 2, 500, 1.0, 1000, '{PaymentMethod.CASH.value}'),
                ('0912345678', '2024-03-01 10:00:00', 'P002', 1, 500, 1.0, 500, '{PaymentMethod.CREDIT_CARD.value}'),
                ('0923456789', '2024-03-02 15:30:00', 'M001', 1, 2000, 0.9, 1800, '{PaymentMethod.E_TRANSFER.value}'),
                ('0934567890', '2024-03-03 18:45:00', 'P003', 3, 1000, 0.8, 2400, '{PaymentMethod.REWARD_POINTS.value}')
            """
            )
            print("✓ 交易紀錄插入成功")
        except sqlite3.Error as e:
            print(f"✗ 交易紀錄插入失敗: {e}")
            raise

        conn.commit()
        print("範例資料插入成功")
        return True

    except sqlite3.Error as e:
        print(f"插入範例資料時發生錯誤: {e}")
        return False
    finally:
        conn.close()


def init_db(create_with_sample_data=True):
    """初始化數據庫"""
    if create_all_tables():
        if create_with_sample_data:
            if insert_sample_data():
                print("範例資料插入成功")
            else:
                print("範例資料插入失敗")
    else:
        print("數據庫表格創建失敗")


def get_all_members() -> list[tuple]:
    conn = get_connection()
    if conn is None:
        return []

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Member")
    members = cursor.fetchall()
    conn.close()
    return members


def display_database_summary(conn, cursor):
    """
    顯示數據庫內容摘要

    Args:
        conn (sqlite3.Connection): 數據庫連接
        cursor (sqlite3.Cursor): 數據庫游標
    """
    print("\n數據庫現有資料概要:")
    print("-" * 50)

    # 檢查每個表格的記錄數
    tables = [
        "MemberPhoto",
        "Member",
        "MembershipStatus",
        "CheckInRecord",
        "TransactionRecord",
        "Product",
        "MembershipPlan",
    ]

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table}: {count} 筆記錄")

    # 顯示會員資料範例
    print("\n會員資料範例:")
    print("-" * 50)
    cursor.execute(
        """
        SELECT mContactNum, mName, mEmail, mBalance, mRewardPoints 
        FROM Member 
        LIMIT 3
    """
    )
    members = cursor.fetchall()
    for member in members:
        print(f"姓名: {member[1]}, 電話: {member[0]}, Email: {member[2]}")
        print(f"餘額: {member[3]}, 點數: {member[4]}")


if __name__ == "__main__":
    """
    主程序入口

    執行順序：
    1. 刪除現有數據庫（如果存在）
    2. 創建新的數據庫和表格
    3. 插入範例數據
    4. 顯示數據庫概要
    """
    # 1. 刪除現有數據庫文件（如果存在）
    import os

    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print(f"✓ 已刪除現有數據庫文件: {DB_PATH}")
        except Exception as e:
            print(f"✗ 刪除數據庫文件失敗: {e}")

    # 2. 初始化數據庫
    print("\n開始初始化數據庫...")
    if create_all_tables():
        print("✓ 數據庫表格創建成功")
        if insert_sample_data():
            print("✓ 範例資料插入成功")

            # 3. 顯示插入的數據概要
            conn = get_connection()
            if conn:
                cursor = conn.cursor()

                try:
                    display_database_summary(conn, cursor)

                except sqlite3.Error as e:
                    print(f"查詢數據時發生錯誤: {e}")

                finally:
                    conn.close()
        else:
            print("✗ 範例資料插入失敗")
    else:
        print("✗ 數據庫表格創建失敗")

    # if init_db():
    #     print("✓ 數據庫表格創建成功")
    # else:
    #     print("✗ 數據庫表格創建失敗")
