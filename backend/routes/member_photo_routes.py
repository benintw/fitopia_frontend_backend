"""
會員照片路由
"""

from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from models.member_photo import MemberPhoto
from models.pydantic_models import (
    MemberPhotoCreate,
    MemberPhotoResponse,
    MemberPhotoUpdate,
)

router = APIRouter(tags=["member_photo"])


@router.post("/member_photo/", response_model=dict[str, str])
async def create_member_photo(
    mContactNum: str = Form(...),
    photo: UploadFile = File(...),
):
    """創建會員照片"""
    photo_bytes = await photo.read()
    result = MemberPhoto.create_member_photo(
        mPhoto=photo_bytes, mContactNum=mContactNum
    )
    # 檢查錯誤情況
    if "error" in result:
        # 如果是重複照片的錯誤
        if "UNIQUE constraint" in result["error"]:
            raise HTTPException(status_code=400, detail="會員照片已存在")
        # 其他錯誤
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@router.get("/member_photo/", response_model=list[MemberPhotoResponse])
def get_all_member_photos() -> list[MemberPhotoResponse]:
    """獲取所有會員照片"""
    member_photos = MemberPhoto.get_all_photos()
    return [MemberPhotoResponse.from_db(photo) for photo in member_photos]


@router.get("/member_photo/{mContactNum}/", response_model=MemberPhotoResponse)
def get_member_photo(mContactNum: str):
    """獲取單一會員照片"""
    member_photo = MemberPhoto.get_member_photo(mContactNum)
    if not member_photo:
        raise HTTPException(status_code=404, detail="會員照片不存在")
    return MemberPhotoResponse.from_db(member_photo)


@router.put("/member_photo/{mContactNum}/", response_model=dict[str, str])
async def update_member_photo(
    mContactNum: str, photo: UploadFile = File(..., alias="photo")
) -> dict[str, str]:
    """更新會員照片"""
    photo_bytes = await photo.read()
    result = MemberPhoto.update_member_photo(mContactNum, new_photo=photo_bytes)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {"message": "會員照片更新成功"}


@router.delete("/member_photo/{mContactNum}/", response_model=dict[str, str])
def delete_member_photo(mContactNum: str) -> dict[str, str]:
    """刪除會員照片"""
    result = MemberPhoto.delete_member_photo(mContactNum)
    if "error" in result:
        if "會員照片不存在" in result["error"]:
            raise HTTPException(status_code=404, detail="會員照片不存在")
        raise HTTPException(status_code=500, detail=result["error"])
    return result
