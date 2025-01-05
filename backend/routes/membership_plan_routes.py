"""會籍方案路由"""

from fastapi import APIRouter, HTTPException
from models.pydantic_models import (
    MembershipPlanCreate,
    MembershipPlanResponse,
    MembershipPlanUpdate,
)
from models.membership_plan import MembershipPlan

router = APIRouter(tags=["membership_plans"])


@router.post("/membership_plans/", response_model=dict[str, str])
def create_membership_plan(membership_plan: MembershipPlanCreate) -> dict[str, str]:
    """創建會籍方案"""
    result = MembershipPlan.create_membership_plan(**membership_plan.model_dump())
    if "error" in result:
        # 如果是重複會籍方案的錯誤，返回 400 狀態碼
        if "會籍方案已存在" in result["error"]:
            raise HTTPException(status_code=400, detail="會籍方案已存在")
        # 其他錯誤返回 500 狀態碼
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.get("/membership_plans/", response_model=list[MembershipPlanResponse])
def get_all_membership_plans() -> list[MembershipPlanResponse]:
    """獲取所有會籍方案"""
    membership_plans = MembershipPlan.get_all_membership_plans()
    return membership_plans


@router.get("/membership_plans/{gsNo}/", response_model=MembershipPlanResponse)
def get_membership_plan(gsNo: str) -> MembershipPlanResponse:
    """獲取單一會籍方案"""
    membership_plan = MembershipPlan.get_membership_plan(gsNo)
    if not membership_plan:
        raise HTTPException(status_code=404, detail="會籍方案不存在")
    return membership_plan


@router.put("/membership_plans/{gsNo}/", response_model=dict)
def update_membership_plan(gsNo: str, membership_plan: MembershipPlanUpdate) -> dict:
    """更新會籍方案"""
    membership_plan_data = membership_plan.model_dump(exclude_unset=True)
    result = MembershipPlan.update_membership_plan(gsNo, **membership_plan_data)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.delete("/membership_plans/{gsNo}/", response_model=dict[str, str])
def delete_membership_plan(gsNo: str) -> dict[str, str]:
    """刪除會籍方案"""
    result = MembershipPlan.delete_membership_plan(gsNo)
    if "error" in result:
        if "會籍方案不存在" in result["error"]:
            raise HTTPException(status_code=404, detail="會籍方案不存在")
        raise HTTPException(status_code=500, detail=result["error"])
    return result
