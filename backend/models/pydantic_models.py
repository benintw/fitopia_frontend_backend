from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date, datetime
from base64 import b64encode
from enum import Enum
from typing import Any
import pytz


"""
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


class MemberCreate(BaseModel):
    """用於創建會員的數據模型"""

    mContactNum: str = Field(..., min_length=1, max_length=20)
    mName: str = Field(..., min_length=1, max_length=50)
    mEmail: str = Field(..., min_length=1, max_length=100)
    mDob: str = Field(..., min_length=1, max_length=10)
    mEmergencyName: str = Field(..., min_length=1, max_length=25)
    mEmergencyNum: str = Field(..., min_length=1, max_length=20)
    mBalance: int = Field(default=0)
    mRewardPoints: int = Field(default=100)


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

    mName: Optional[str] = Field(None, min_length=1, max_length=50)
    mEmail: Optional[str] = Field(None, min_length=1, max_length=100)
    mEmergencyName: Optional[str] = Field(None, min_length=1, max_length=25)
    mEmergencyNum: Optional[str] = Field(None, min_length=1, max_length=20)
    mBalance: Optional[int] = Field(None, gt=0)
    mRewardPoints: Optional[int] = Field(None, gt=0)


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


class MembershipStatusCreate(BaseModel):
    mContactNum: str
    startDate: date
    endDate: date
    isActive: bool = True

    @field_validator("endDate")
    @classmethod
    def validate_end_date(cls, v: date, info: Any) -> date:
        if "startDate" in info.data and v <= info.data["startDate"]:
            raise ValueError("結束日期必須大於開始日期")
        return v


class MembershipStatusResponse(BaseModel):
    sId: int
    mContactNum: str
    startDate: date
    endDate: date
    isActive: bool


class MembershipStatusUpdate(BaseModel):
    startDate: date | None = None
    endDate: date | None = None
    isActive: bool | None = None

    @field_validator("endDate")
    @classmethod
    def validate_end_date(cls, v: date | None, info: Any) -> date | None:
        if v is None:
            return v
        if (
            "startDate" in info.data
            and info.data["startDate"] is not None
            and v <= info.data["startDate"]
        ):
            raise ValueError("結束日期必須大於開始日期")
        return v


# 打卡記錄


class CheckInRecordCreate(BaseModel):
    """創建打卡記錄用"""

    mContactNum: str  # Only need member contact for check-in


class CheckInRecordResponse(BaseModel):
    """用於返回打卡記錄資料的數據模型"""

    checkInNo: int
    mContactNum: str
    checkInDatetime: datetime
    checkOutDatetime: Optional[datetime] = None
    checkInStatus: int
    checkOutStatus: int


class CheckInRecordUpdate(BaseModel):
    """更新打卡記錄用"""

    message: str


# 交易記錄
"""
    CREATE TABLE IF NOT EXISTS TransactionRecord (
        tNo INTEGER PRIMARY KEY AUTOINCREMENT,
        mContactNum VARCHAR(20) NOT NULL,
        transDateTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        totalAmount INTEGER NOT NULL CHECK (totalAmount > 0),
        FOREIGN KEY (mContactNum) REFERENCES Member(mContactNum)
            ON DELETE RESTRICT
            ON UPDATE CASCADE
    )
"""


class PaymentMethod(str, Enum):
    """支付方式列舉"""

    CASH = "cash"
    CREDIT_CARD = "credit_card"
    E_TRANSFER = "e_transfer"
    REWARD_POINTS = "reward_points"


class TransactionDetail(BaseModel):
    """交易詳情模型"""

    gsNo: str
    count: int
    unitPrice: int
    discount: float
    paymentMethod: PaymentMethod


class TransactionRecordCreate(BaseModel):
    """創建交易記錄請求模型"""

    mContactNum: str = Field(..., min_length=1, max_length=20)
    gsNo: str = Field(..., min_length=1, max_length=20)
    count: int = Field(..., gt=0)
    unitPrice: int = Field(..., gt=0)
    discount: float = Field(...)
    paymentMethod: PaymentMethod


class TransactionRecordResponse(BaseModel):
    """交易記錄響應模型"""

    tNo: int
    mContactNum: str
    transDateTime: datetime
    gsNo: str
    count: int
    unitPrice: int
    discount: float
    totalAmount: int
    paymentMethod: PaymentMethod


class TransactionRecordUpdate(BaseModel):
    """更新交易記錄用"""

    gsNo: Optional[str] = Field(None, min_length=1, max_length=20)
    count: Optional[int] = Field(None, gt=0)
    unitPrice: Optional[int] = Field(None, gt=0)
    discount: Optional[float] = Field(None, gt=0, le=1)
    paymentMethod: Optional[PaymentMethod] = None
