"""
會員照片類別測試
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import unittest
from gym_management.backend.database import get_connection
from models.member_photo import MemberPhoto
from models.member import Member

from icecream import ic

    
class TestMemberPhoto(unittest.TestCase):
    """測試會員照片類別的所有方法"""

    @classmethod
    def setUpClass(cls):
        """
        在所有測試開始前執行一次：
        1. 關閉外鍵約束
        2. 清空相關表格
        3. 確保有預設照片
        4. 重新啟用外鍵約束
        """
        conn = get_connection()
        cursor = conn.cursor()

        try:
            # 暫時關閉外鍵約束
            cursor.execute("PRAGMA foreign_keys = OFF")

            # 清空相關表格（按照正確的順序）
            cursor.execute("DELETE FROM MemberPhoto")
            cursor.execute("DELETE FROM Member")  # 最後刪除會員

            conn.commit()

        finally:
            # 重新啟用外鍵約束
            cursor.execute("PRAGMA foreign_keys = ON")
            conn.commit()
            conn.close()

    def setUp(self):
        # 1. 準備測試會員資料
        self.test_member = {
            "mContactNum": "0912345678",
            "mName": "測試會員",
            "mEmail": "test@example.com",
            "mDob": "1990-01-01",
            "mEmergencyName": "緊急聯絡人",
            "mEmergencyNum": "0987654321",
            "mBalance": 1000,
            "mRewardPoints": 100,
        }

        # 2. 創建測試會員
        Member.create_member(**self.test_member)

        # 3. 準備測試會員照片資料
        self.test_member_photo = {}
        with open("imgs/test_member_photo.jpg", "rb") as f:
            self.test_member_photo["mPhoto"] = f.read()

        self.test_member_photo["mContactNum"] = self.test_member["mContactNum"]

    def test_1_create_member_photo(self):
        """測試創建會員照片"""
        result = MemberPhoto.create_member_photo(**self.test_member_photo)
        self.assertEqual(result.get("success"), "會員照片創建成功")

    def test_2_get_active_photo(self):
        """測試查詢會員照片"""
        result = MemberPhoto.get_member_photo(self.test_member_photo["mContactNum"])
        self.assertIsNotNone(result)
        self.assertEqual(
            result.get("mContactNum"), self.test_member_photo["mContactNum"]
        )

    def test_3_get_all_photos(self):
        """測試查詢所有會員照片"""
        # 確保至少有一張照片
        MemberPhoto.create_member_photo(**self.test_member_photo)

        # 查詢所有照片
        photos = MemberPhoto.get_all_photos()
        self.assertIsInstance(photos, list)
        self.assertGreater(len(photos), 0)

        # 驗證測試照片在列表中
        test_photo_found = False
        for photo in photos:
            if photo["mContactNum"] == self.test_member_photo["mContactNum"]:
                test_photo_found = True
                break
        self.assertTrue(test_photo_found)

    def test_4_update_member_photo(self):
        """測試更新會員照片"""
        # 確保測試會員照片存在
        MemberPhoto.create_member_photo(**self.test_member_photo)

        # 更新照片
        result = MemberPhoto.update_member_photo(
            mContactNum=self.test_member_photo["mContactNum"],
            new_photo=b"new_photo_data",
        )
        ic(result)
        self.assertEqual(result.get("success"), "會員照片更新成功")

        updated_photo = MemberPhoto.get_member_photo(
            self.test_member_photo["mContactNum"]
        )
        self.assertEqual(
            updated_photo.get("mContactNum"), self.test_member_photo["mContactNum"]
        )

    def test_5_delete_member_photo(self):
        """測試刪除會員照片"""
        # 確保測試會員照片存在
        MemberPhoto.create_member_photo(**self.test_member_photo)

        result = MemberPhoto.delete_member_photo(self.test_member_photo["mContactNum"])
        self.assertEqual(result.get("success"), "會員照片刪除成功")

        member_photo = MemberPhoto.get_member_photo(
            self.test_member_photo["mContactNum"]
        )
        self.assertIsNone(member_photo)

    def test_6_error_cases(self):
        """測試錯誤情況"""
        # 確保測試會員照片存在
        MemberPhoto.create_member_photo(**self.test_member_photo)

        # 測試創建重複會員照片
        duplicate_result = MemberPhoto.create_member_photo(**self.test_member_photo)
        ic(duplicate_result)
        self.assertIn("error", duplicate_result)

        # 測試更新不存在的會員照片
        non_exist_update = MemberPhoto.update_member_photo(
            mContactNum="9999999999", new_photo=b"new_photo_data"
        )
        ic(non_exist_update)
        self.assertIn("error", non_exist_update)

        # 測試刪除不存在的會員照片
        result = MemberPhoto.delete_member_photo("9999999999")
        ic(result)
        self.assertEqual(result.get("error"), "會員照片不存在")

    @classmethod
    def tearDownClass(cls):
        """
        在所有測試結束後清理數據
        """
        conn = get_connection()
        cursor = conn.cursor()

        try:
            # 清空相關表格（按照正確的順序）
            cursor.execute("DELETE FROM MemberPhoto")
            conn.commit()

        finally:
            cursor.execute("PRAGMA foreign_keys = ON")
            conn.commit()
            conn.close()
