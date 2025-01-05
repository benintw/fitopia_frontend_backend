"""FastAPI application for gym management"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import (
    member_routes,
    membership_plan_routes,
    product_routes,
    member_photo_routes,
    membership_status_routes,
    checkinrecord_routes,
    transaction_record_routes,
)


app = FastAPI(title="健身房管理系統")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(member_routes.router)
app.include_router(product_routes.router)
app.include_router(membership_plan_routes.router)
app.include_router(member_photo_routes.router)
app.include_router(membership_status_routes.router)
app.include_router(checkinrecord_routes.router)
app.include_router(transaction_record_routes.router)


@app.get("/", tags=["home"])
def home_page():
    return {"message": "歡迎來到 FITOPIA 健身房管理系統"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
