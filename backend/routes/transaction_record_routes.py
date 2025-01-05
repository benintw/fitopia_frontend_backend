"""交易記錄路由"""

from fastapi import APIRouter, HTTPException

from models.transaction_record import TransactionRecord
from models.pydantic_models import (
    TransactionRecordCreate,
    TransactionRecordUpdate,
    TransactionRecordResponse,
)

router = APIRouter(tags=["transaction_record"])


@router.post("/transaction_records/", response_model=dict[str, str])
async def create_transaction_record(
    transaction_record: TransactionRecordCreate,
) -> dict[str, str]:
    """創建交易記錄"""
    transaction_dict = transaction_record.model_dump()
    result = TransactionRecord.create_transaction_record(transaction_dict)

    if "error" in result:
        if "會員不存在" in result["error"]:
            raise HTTPException(status_code=400, detail="會員不存在")
        elif "金額必須大於0" in result["error"]:
            raise HTTPException(status_code=400, detail="金額必須大於0")
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@router.get("/transaction_records/", response_model=list[TransactionRecordResponse])
async def get_all_transaction_records() -> list[TransactionRecordResponse]:
    """獲取所有交易記錄"""
    transaction_records = TransactionRecord.get_all_transaction_records()
    return transaction_records


@router.get(
    "/transaction_records/member/{mContactNum}/",
    response_model=list[TransactionRecordResponse],
)
async def get_member_transaction_record(
    mContactNum: str,
) -> list[TransactionRecordResponse]:
    """獲取會員的所有交易記錄"""
    transaction_records = TransactionRecord.get_member_transaction_record(mContactNum)
    if not transaction_records:
        raise HTTPException(status_code=404, detail="找不到該會員的交易記錄")
    return transaction_records


"""
class TransactionRecordUpdate(BaseModel):
    更新交易記錄用

    count: Optional[int] = Field(None, gt=0)
    unitPrice: Optional[int] = Field(None, gt=0)
    discount: Optional[float] = Field(None, gt=0, le=1)
    paymentMethod: Optional[PaymentMethod] = None

"""


@router.put("/transaction_records/{mContactNum}/{tNo}", response_model=dict[str, str])
async def update_transaction_record(
    mContactNum: str, tNo: int, transaction_record: TransactionRecordUpdate
) -> dict[str, str]:
    """更新交易記錄"""

    result = TransactionRecord.update_transaction_record(
        mContactNum, tNo, updates=transaction_record.model_dump()
    )
    if "error" in result:
        if "會員不存在" in result["error"]:
            raise HTTPException(status_code=400, detail="會員不存在")
        elif "金額必須大於0" in result["error"]:
            raise HTTPException(status_code=400, detail="金額必須大於0")
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.delete(
    "/transaction_records/{mContactNum}/{tNo}", response_model=dict[str, str]
)
async def delete_transaction_record(mContactNum: str, tNo: int) -> dict[str, str]:
    """刪除交易記錄"""
    result = TransactionRecord.delete_transaction_record(mContactNum, tNo)
    if "error" in result:
        if "找不到該會員的交易記錄" in result["error"]:
            raise HTTPException(status_code=404, detail="找不到該會員的交易記錄")
        raise HTTPException(status_code=500, detail=result["error"])
    return result
