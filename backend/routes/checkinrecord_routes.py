"""打卡記錄路由"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import pytz
from models.checkinrecord import CheckInRecord
from models.pydantic_models import (
    CheckInRecordCreate,
    CheckInRecordResponse,
    CheckInRecordUpdate,
)

router = APIRouter(tags=["checkinrecord"])


@router.post("/checkinrecord/", response_model=dict[str, str])
def create_checkin_record(record: CheckInRecordCreate) -> dict[str, str]:
    """創建打卡記錄"""
    result = CheckInRecord.create_checkin_record(record.mContactNum)
    if "error" in result:
        if "會員不存在" in result["error"]:
            raise HTTPException(status_code=400, detail="會員不存在")
        if "已有未結束的打卡記錄" in result["error"]:
            raise HTTPException(status_code=400, detail="已有未結束的打卡記錄")
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.get("/checkinrecord/{mContactNum}/", response_model=list[CheckInRecordResponse])
def get_checkin_record(mContactNum: str) -> list[CheckInRecordResponse]:
    """查詢特定會員的打卡記錄"""
    record = CheckInRecord.get_checkin_record(mContactNum)
    if not record:
        raise HTTPException(status_code=404, detail="打卡記錄不存在")
    return [CheckInRecordResponse(**record) for record in record]


@router.get("/checkinrecord/", response_model=list[CheckInRecordResponse])
def get_all_checkin_records() -> list[CheckInRecordResponse]:
    """查詢所有打卡記錄"""
    records = CheckInRecord.get_all_checkin_records()
    return [CheckInRecordResponse(**record) for record in records]


@router.put("/checkinrecord/{mContactNum}/", response_model=CheckInRecordUpdate)
def update_checkin_record(mContactNum: str) -> CheckInRecordUpdate:
    """更新打卡記錄（登出）"""

    result = CheckInRecord.update_checkin_record(mContactNum)
    if "error" in result:
        if "打卡記錄不存在" in result["error"]:
            raise HTTPException(status_code=404, detail="打卡記錄不存在")
        if "該記錄已經登出" in result["error"]:
            raise HTTPException(status_code=400, detail="該記錄已經登出")
        if "登出時間必須晚於登入時間" in result["error"]:
            raise HTTPException(status_code=400, detail="登出時間必須晚於登入時間")
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.delete("/checkinrecord/{mContactNum}/", response_model=dict[str, str])
def delete_checkin_record(mContactNum: str) -> dict[str, str]:
    """刪除打卡記錄"""
    result = CheckInRecord.delete_checkin_record(mContactNum)
    if "error" in result:
        if "打卡記錄不存在" in result["error"]:
            raise HTTPException(status_code=404, detail="打卡記錄不存在")
        raise HTTPException(status_code=500, detail=result["error"])
    return result
