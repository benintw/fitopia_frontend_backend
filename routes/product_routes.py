from fastapi import APIRouter, HTTPException
from models.product import Product
from models.pydantic_models import ProductCreate, ProductResponse, ProductUpdate


router = APIRouter(tags=["products"])


@router.post("/products/", response_model=dict[str, str])
def create_product(product: ProductCreate) -> dict[str, str]:
    """創建商品"""
    result = Product.create_product(**product.model_dump())
    if "error" in result:
        # 如果是重複的商品，返回400狀態馬
        if "商品已存在" in result["error"]:
            raise HTTPException(status_code=400, detail="商品已存在")
        # 其他錯誤返回 500
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.get("/products/", response_model=list[ProductResponse])
def get_all_products() -> list[ProductResponse]:
    """獲取所有商品"""
    products = Product.get_all_products()
    return products


@router.get("/products/{gsNo}", response_model=ProductResponse)
def get_product(gsNo: str) -> ProductResponse:
    """獲取單一商品"""
    product = Product.get_product(gsNo)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return product


@router.put("/products/{gsNo}", response_model=dict[str, str])
def update_product(gsNo: str, product: ProductUpdate) -> dict[str, str]:
    """更新商品"""
    product_data = product.model_dump(exclude_unset=True)
    result = Product.update_product(gsNo, **product.model_dump())
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.delete("/products/{gsNo}", response_model=dict[str, str])
def delete_product(gsNo: str) -> dict[str, str]:
    """刪除商品"""
    result = Product.delete_product(gsNo)
    if "error" in result:
        if "商品不存在" in result["error"]:
            raise HTTPException(status_code=404, detail="商品不存在")
        raise HTTPException(status_code=500, detail=result["error"])
    return result
