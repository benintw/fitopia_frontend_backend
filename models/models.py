from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DECIMAL,
    Date,
    DateTime,
    Boolean,
    BLOB,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

# 創建資料庫引擎
engine = create_engine("sqlite:///gym_management.db", echo=True)
Base = declarative_base()


class MemberPhoto(Base):
    __tablename__ = "member_photo"

    mPhotoName = Column(String(50), primary_key=True)
    mPhoto = Column(BLOB, nullable=False)
    # 關聯
    member = relationship("Member", back_populates="photo")


class Member(Base):
    __tablename__ = "member"

    mContactNum = Column(String(20), primary_key=True)
    mName = Column(String(50), nullable=False)
    mEmail = Column(String(100), nullable=False)
    mDob = Column(Date, nullable=False)
    mEmergencyName = Column(String(25), nullable=False)
    mEmergencyNum = Column(String(20), nullable=False)
    mPhotoName = Column(
        String(25),
        ForeignKey("member_photo.mPhotoName", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    mBalance = Column(DECIMAL(10, 1), default=0)
    mRewardPoints = Column(Integer, default=100)

    # 關聯
    photo = relationship("MemberPhoto", back_populates="member")
    membership_status = relationship("MembershipStatus", back_populates="member")
    checkin_records = relationship("CheckInRecord", back_populates="member")
    transactions = relationship("Transaction", back_populates="member")


class MembershipStatus(Base):
    __tablename__ = "membership_status"

    sid = Column(Integer, primary_key=True, autoincrement=True)
    mContactNum = Column(
        String(20),
        ForeignKey("member.mContactNum", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    startDate = Column(Date, nullable=False)
    endDate = Column(Date, nullable=False)
    isActive = Column(Boolean, default=True)

    # 關聯
    member = relationship("Member", back_populates="membership_status")

    # 檢查約束
    __table_args__ = (CheckConstraint("endDate > startDate"),)


class CheckInRecord(Base):
    __tablename__ = "check_in_record"

    checkInNo = Column(Integer, primary_key=True, autoincrement=True)
    mContactNum = Column(
        String(20),
        ForeignKey("member.mContactNum", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    checkInDatetime = Column(DateTime, nullable=False)
    checkOutDatetime = Column(DateTime)
    checkInStatus = Column(Boolean, default=True)
    checkOutStatus = Column(Boolean, default=False)

    # 關聯
    member = relationship("Member", back_populates="checkin_records")

    # 檢查約束
    __table_args__ = (CheckConstraint("checkOutDatetime > checkInDatetime"),)


class Transaction(Base):
    __tablename__ = "transaction"

    tNo = Column(Integer, primary_key=True, autoincrement=True)
    mContactNum = Column(
        String(20),
        ForeignKey("member.mContactNum", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    transDateTime = Column(DateTime, nullable=False, default=datetime.now)
    totalAmount = Column(DECIMAL(10, 2), nullable=False)

    # 關聯
    member = relationship("Member", back_populates="transactions")
    orders = relationship("Order", back_populates="transaction")

    # 檢查約束
    __table_args__ = (CheckConstraint("totalAmount > 0"),)


class MembershipPlan(Base):
    __tablename__ = "membership_plan"

    gsNo = Column(String(20), primary_key=True)
    salePrice = Column(Integer, nullable=False)
    planType = Column(String(50), nullable=False)
    planDuration = Column(Integer, nullable=False)

    # 關聯
    orders = relationship("Order", back_populates="membership_plan")

    # 檢查約束
    __table_args__ = (
        CheckConstraint("salePrice > 0"),
        CheckConstraint("planDuration > 0"),
    )


class Product(Base):
    __tablename__ = "product"

    gsNo = Column(String(20), primary_key=True)
    salePrice = Column(Integer, nullable=False)
    pName = Column(String(100), nullable=False)
    pImage = Column(BLOB)

    # 關聯
    orders = relationship("Order", back_populates="product")

    # 檢查約束
    __table_args__ = (CheckConstraint("salePrice > 0"),)


class Order(Base):
    __tablename__ = "order"

    orderId = Column(Integer, primary_key=True, autoincrement=True)
    tNo = Column(
        Integer,
        ForeignKey("transaction.tNo", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    gsNo = Column(
        String(20),
        ForeignKey("product.gsNo", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    salePrice = Column(Integer, nullable=False)
    amount = Column(Integer, nullable=False)
    paymentMethod = Column(String(20), nullable=False)

    # 關聯
    transaction = relationship("Transaction", back_populates="orders")
    product = relationship("Product", back_populates="orders")
    membership_plan = relationship("MembershipPlan", back_populates="orders")

    # 檢查約束
    __table_args__ = (
        CheckConstraint("salePrice > 0"),
        CheckConstraint("amount > 0"),
        CheckConstraint(
            "paymentMethod IN ('cash', 'credit card', 'e-transfer', 'reward points')"
        ),
    )


# 創建所有表格
Base.metadata.create_all(engine)
