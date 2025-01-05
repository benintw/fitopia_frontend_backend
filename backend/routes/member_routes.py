from fastapi import APIRouter, HTTPException
from models.pydantic_models import MemberCreate, MemberResponse, MemberUpdate
from models.member import Member

router = APIRouter(tags=["members"])


@router.post("/members/", response_model=dict[str, str])
def create_member(member: MemberCreate) -> dict[str, str]:
    """創建會員"""
    result = Member.create_member(**member.model_dump())
    if "error" in result:
        # 如果是重複會員的錯誤，返回 400 狀態碼
        if "會員已存在" in result["error"]:
            raise HTTPException(status_code=400, detail="會員已存在")
        # 其他錯誤返回 500 狀態碼
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.get("/members/", response_model=list[MemberResponse])
def get_all_members() -> list[MemberResponse]:
    """獲取所有會員"""
    members = Member.get_all_members()
    return members


@router.get("/members/{mContactNum}/", response_model=MemberResponse)
def get_member(mContactNum: str) -> MemberResponse:
    """獲取單一會員"""
    member = Member.get_member(mContactNum)
    if not member:
        raise HTTPException(status_code=404, detail="會員不存在")
    return member


@router.put("/members/{mContactNum}/", response_model=dict)
def update_member(mContactNum: str, member: MemberUpdate):
    """更新會員資料"""
    member_data = member.model_dump(exclude_unset=True)
    result = Member.update_member(mContactNum=mContactNum, **member_data)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.delete("/members/{mContactNum}/", response_model=dict[str, str])
def delete_member(mContactNum: str) -> dict[str, str]:
    """刪除會員"""
    result = Member.delete_member(mContactNum)
    if "error" in result:
        if "會員不存在" in result["error"]:
            raise HTTPException(status_code=404, detail="會員不存在")
        raise HTTPException(status_code=500, detail=result["error"])
    return result
