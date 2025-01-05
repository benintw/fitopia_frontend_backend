"""會籍狀態路由"""

from fastapi import APIRouter, HTTPException
from models.pydantic_models import (
    MembershipStatusCreate,
    MembershipStatusResponse,
    MembershipStatusUpdate,
)

from models.membership_status import MembershipStatus


router = APIRouter(tags=["membership_status"])


@router.post("/membership_status/", response_model=dict[str, str])
def create_membership_status(
    membership_status: MembershipStatusCreate,
) -> dict[str, str]:
    """創建會籍狀態"""
    result = MembershipStatus.create_membership_status(**membership_status.model_dump())
    if "error" in result:
        if "會員不存在" in result["error"]:
            raise HTTPException(status_code=400, detail="會員不存在")
        if "會籍狀態已存在" in result["error"]:
            raise HTTPException(status_code=400, detail="會籍狀態已存在")
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.get("/membership_status/", response_model=list[MembershipStatusResponse])
def get_all_membership_status() -> list[MembershipStatusResponse]:
    """獲取所有會籍狀態"""
    membership_statuses = MembershipStatus.get_all_membership_status()
    return membership_statuses


@router.get(
    "/membership_status/{mContactNum}/", response_model=MembershipStatusResponse
)
def get_membership_status(mContactNum: str) -> MembershipStatusResponse:
    """獲取單一會籍狀態"""
    membership_status = MembershipStatus.get_membership_status(mContactNum)
    if not membership_status:
        raise HTTPException(status_code=404, detail="會籍狀態不存在")
    return membership_status


@router.put("/membership_status/{mContactNum}/", response_model=dict[str, str])
def update_membership_status(
    mContactNum: str, membership_status: MembershipStatusUpdate
) -> dict[str, str]:
    """更新會籍狀態"""
    membership_status_data = membership_status.model_dump(exclude_unset=True)
    result = MembershipStatus.update_membership_status(
        mContactNum=mContactNum, **membership_status_data
    )
    if "error" in result:
        if "會籍狀態不存在" in result["error"]:
            raise HTTPException(status_code=404, detail="會籍狀態不存在")
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.delete("/membership_status/{mContactNum}/", response_model=dict[str, str])
def delete_membership_status(mContactNum: str) -> dict[str, str]:
    """刪除會籍狀態"""
    result = MembershipStatus.delete_membership_status(mContactNum)
    if "error" in result:
        if "會籍狀態不存在" in result["error"]:
            raise HTTPException(status_code=404, detail="會籍狀態不存在")
        raise HTTPException(status_code=500, detail=result["error"])
    return result
