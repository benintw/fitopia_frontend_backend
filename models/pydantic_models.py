from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date
from base64 import b64encode


class MemberCreate(BaseModel):
    """用於創建會員的數據模型"""

    mContactNum: str
    mName: str
    mEmail: str
    mDob: str
    mEmergencyName: str
    mEmergencyNum: str
    mBalance: int = 0
    mRewardPoints: int = 100


class MemberResponse(BaseModel):
    """用於返回會員資料的數據模型"""

    mContactNum: str
    mName: str
    mEmail: str
    mDob: str
    mEmergencyName: str
    mEmergencyNum: str
    mBalance: int
    mRewardPoints: int
    creation_date: date


class MemberUpdate(BaseModel):
    """用於更新會員資料的數據模型"""

    mEmail: Optional[str] = None
    mEmergencyName: Optional[str] = None
    mEmergencyNum: Optional[str] = None
    mBalance: Optional[int] = None
    mRewardPoints: Optional[int] = None


class ProductBase(BaseModel):
    """商品基本資料"""

    """ gsNo VARCHAR(20) PRIMARY KEY,
        salePrice INTEGER NOT NULL CHECK (salePrice > 0),
        pName VARCHAR(100) NOT NULL,
        pImage BLOB"""

    gsNo: str = Field(..., min_length=1, max_length=20)
    salePrice: int = Field(..., gt=0)  # 確保價格大於 0
    pName: str = Field(..., min_length=1, max_length=100)
    pImage: Optional[bytes] = None


class ProductCreate(ProductBase):
    """創建產品用"""

    pass


class ProductResponse(ProductBase):
    """用於返回商品資料的數據模型"""

    pass


class ProductUpdate(BaseModel):
    """更新產品用"""

    salePrice: Optional[int] = None
    pName: Optional[str] = None
    pImage: Optional[bytes] = None


class MembershipPlanBase(BaseModel):
    """會籍方案基本資料"""

    """
        CREATE TABLE IF NOT EXISTS MembershipPlan (
            gsNo VARCHAR(20) PRIMARY KEY,
            salePrice INTEGER NOT NULL CHECK (salePrice > 0),
            planType VARCHAR(50) NOT NULL,
            planDuration INTEGER NOT NULL CHECK (planDuration > 0)
        )
    """
    gsNo: str = Field(..., min_length=1, max_length=20)
    salePrice: int = Field(..., gt=0)
    planType: str = Field(..., min_length=1, max_length=50)
    planDuration: int = Field(..., gt=0)

    class Config:
        json_schema_extra = {
            "example": {
                "gsNo": "MP001",
                "salePrice": 3000,
                "planType": "月費會員",
                "planDuration": 30,
            }
        }


class MembershipPlanCreate(MembershipPlanBase):
    """創建會籍方案用"""

    pass  # 繼承所有 Base 的欄位，全部必填


class MembershipPlanResponse(MembershipPlanBase):
    """用於返回會籍方案資料的數據模型"""

    pass


class MembershipPlanUpdate(BaseModel):
    """更新會籍方案用"""

    salePrice: Optional[int] = None
    planType: Optional[str] = None
    planDuration: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {"salePrice": 3500, "planType": "季費會員", "planDuration": 90}
        }


class MemberPhotoBase(BaseModel):
    """會員照片基本資料"""

    mPhotoName: str = Field(..., min_length=1, max_length=50)
    mPhoto: bytes = Field(...)
    mContactNum: str = Field(..., min_length=1, max_length=20)
    isActive: bool = Field(default=True)

    class Config:
        json_schema_extra = {
            "example": {
                "mPhotoName": "member_001_profile.jpg",
                "mPhoto": b"<binary_data>",  # 實際使用時會是真實的二進制數據
                "mContactNum": "0912345678",
            }
        }


class MemberPhotoCreate(MemberPhotoBase):
    """創建會員照片用"""

    pass  # 繼承所有必填欄位


class MemberPhotoResponse(BaseModel):
    """會員照片回應模型"""

    mPhotoName: str
    mPhoto: str  # 將以 base64 字符串形式返回
    mContactNum: str
    isActive: bool = True

    @classmethod
    def from_db(cls, db_data: dict):
        """從數據庫數據創建響應模型"""
        if not db_data:
            return None
        # 將二進制照片轉換為 base64 字符串
        photo_base64 = b64encode(db_data["mPhoto"]).decode("utf-8")
        return cls(
            mPhotoName=db_data["mPhotoName"],
            mPhoto=photo_base64,
            mContactNum=db_data["mContactNum"],
            isActive=db_data["isActive"],
        )


class MemberPhotoUpdate(BaseModel):
    """更新會員照片用"""

    mPhoto: bytes = Field(...)

    # mPhotoName: Optional[str] = None # 是主鍵，不允許更新
    # mContactNum: Optional[str] = None # 是外鍵，不建議直接更新
    class Config:
        json_schema_extra = {
            "example": {"mPhoto": b"<binary_data>"}  # 實際使用時會是真實的二進制數據
        }


# 會籍狀態
class MembershipStatusBase(BaseModel):
    """會籍狀態基本資料"""

    mContactNum: str = Field(..., min_length=1, max_length=20)
    startDate: date
    endDate: date
    isActive: bool = Field(default=True)

    @field_validator("endDate")
    def validate_end_date(cls, v, values):
        """驗證結束日期必須大於開始日期"""
        if "startDate" in values and v <= values["startDate"]:
            raise ValueError("結束日期必須大於開始日期")
        return v


class MembershipStatusCreate(MembershipStatusBase):
    """創建會籍狀態用"""

    pass  # 繼承所有 Base 的欄位，全部必填


class MembershipStatusResponse(MembershipStatusBase):
    """用於返回會籍狀態資料的數據模型"""

    sid: int  # 添加主鍵欄位


class MembershipStatusUpdate(BaseModel):
    """更新會籍狀態用"""

    startDate: date | None = None
    endDate: date | None = None
    isActive: bool | None = None

    @field_validator("endDate")
    def validate_end_date(cls, v, values):
        """驗證結束日期必須大於開始日期（如果兩個日期都提供）"""
        if v is not None and "startDate" in values and values["startDate"] is not None:
            if v <= values["startDate"]:
                raise ValueError("結束日期必須大於開始日期")
        return v
