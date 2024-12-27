"""
測試會員照片相關 API
"""

from fastapi.testclient import TestClient
from main import app
import unittest
from icecream import ic
from database import get_connection


class TestMemberPhotoRoutes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """在所有測試開始前清理數據庫"""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # 關閉外鍵約束
            cursor.execute("PRAGMA foreign_keys = OFF")

            # 清空相關表格
            cursor.execute("DELETE FROM MemberPhoto")
            cursor.execute("DELETE FROM Member")
            conn.commit()
        finally:
            # 重新啟用外鍵約束
            cursor.execute("PRAGMA foreign_keys = ON")
            conn.commit()
            conn.close()

    def setUp(self):
        """每個測試前的設置"""
        self.client = TestClient(app)
        # 清理數據庫
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM MemberPhoto")
            conn.commit()
        finally:
            conn.close()

        self.test_member = {
            "mContactNum": "0912345678",
            "mName": "測試會員",
            "mEmail": "test@example.com",
            "mDob": "1990-01-01",
            "mEmergencyName": "緊急聯絡人",
            "mEmergencyNum": "0987654321",
        }

        # 創建測試會員
        self.client.post("/members/", json=self.test_member)

        self.test_member_photo = {
            "mContactNum": "0912345678",
            "mPhotoName": "test.jpg",
            "mPhoto": b"test_photo",
        }

    def test_1_create_member_photo(self):
        """測試創建會員照片 API"""
        with open("imgs/test_member_photo.jpg", "rb") as f:
            photo_data = f.read()

        # 使用 files 和 data 參數
        files = {"photo": ("test.jpg", photo_data, "image/jpeg")}
        data = {"mContactNum": self.test_member["mContactNum"]}

        response = self.client.post("/member_photo/", files=files, data=data)

        ic(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("success"), "會員照片創建成功")

    def test_2_get_member_photo(self):
        """測試查詢會員照片 API"""
        # 先創建一個會員照片
        self.test_1_create_member_photo()

        response = self.client.get(f"/member_photo/{self.test_member['mContactNum']}/")
        # ic(response.json())
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("mPhotoName", data)
        self.assertIn("mPhoto", data)  # 這將是 base64 字符串
        self.assertIn("mContactNum", data)
        self.assertEqual(data["mContactNum"], self.test_member["mContactNum"])
        self.assertTrue(data["isActive"])

    def test_3_get_all_member_photos(self):
        """測試查詢所有會員照片 API"""
        response = self.client.get("/member_photo/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_4_update_member_photo(self):
        """測試更新會員照片 API"""

        self.test_1_create_member_photo()

        with open("imgs/test_member_photo.jpg", "rb") as f:
            new_photo_data = f.read()

        # 使用 files 和 data 參數
        files = {"photo": ("new_photo.jpg", new_photo_data, "image/jpeg")}

        response = self.client.put(
            f"/member_photo/{self.test_member['mContactNum']}/",
            files=files,
        )
        # ic(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("message"), "會員照片更新成功")

    def test_5_error_cases(self):
        """測試錯誤情況"""
        # 測試創建重複會員照片

        # 先創建一個會員照片
        with open("imgs/test_member_photo.jpg", "rb") as f:
            photo_data = f.read()

        # 使用 files 和 data 參數
        files = {"photo": ("test.jpg", photo_data, "image/jpeg")}
        data = {"mContactNum": self.test_member["mContactNum"]}
        response = self.client.post("/member_photo/", files=files, data=data)
        ic(response.json())
        self.assertEqual(response.status_code, 200)

        # 嘗試創建重複的會員照片
        response = self.client.post("/member_photo/", files=files, data=data)
        ic(response.json())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get("detail"), "會員照片已存在")

        # 測試查詢不存在的會員照片
        response = self.client.get("/member_photo/9999999999/")
        self.assertEqual(response.status_code, 404)

        # 測試更新不存在的會員照片
        response = self.client.put(
            "/member_photo/9999999999/",
            files={"photo": ("test.jpg", photo_data, "image/jpeg")},
        )
        self.assertEqual(response.status_code, 404)

    def test_6_delete_member_photo(self):
        """測試刪除會員照片 API"""
        # 先創建一個會員照片
        self.test_1_create_member_photo()

        response = self.client.delete(
            f"/member_photo/{self.test_member['mContactNum']}/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("success"), "會員照片刪除成功")

        # 確認會員照片已被刪除
        response = self.client.get(f"/member_photo/{self.test_member['mContactNum']}/")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
