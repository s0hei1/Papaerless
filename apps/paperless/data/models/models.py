from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
)
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from datetime import datetime, UTC
from apps.paperless.data.enums.approval_status import ApprovalStatus
from apps.paperless.data.enums.unit_of_measure import UOMs
from apps.paperless.data.enums.user_rolls import UserRoll
from apps.paperless.data.models.custom_types import String1024, String512, String128, String64, String32, String16, \
    String8, String256

class SQLAlchemyModel(DeclarativeBase):
    type_annotation_map = {
        String1024: String(1024),
        String512: String(512),
        String128: String(128),
        String64: String(64),
        String32: String(32),
        String16: String(16),
        String8: String(8),
    }

class Department(SQLAlchemyModel):
    __tablename__ = "departments"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[String128] = mapped_column(unique=True)
    code: Mapped[int] = mapped_column(unique=True)
    manager_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", use_alter=True))

    users: Mapped[list['User']] = relationship(
        "User", back_populates="department", foreign_keys="User.department_id"
    )
    manager_user = relationship(
        "User",
        back_populates="managed_department",
        foreign_keys=[manager_id],
        uselist=False
    )

class User(SQLAlchemyModel):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name: Mapped[String32]
    last_name: Mapped[String32]
    user_name: Mapped[String32] = mapped_column(unique=True)
    password: Mapped[String32]
    user_roll: Mapped[UserRoll] = mapped_column(default=UserRoll.PERSONNEL)

    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False)

    department : Mapped['Department'] = relationship(
        "Department",
        back_populates="users",
        foreign_keys=[department_id],
        uselist=False
    )
    managed_department = relationship(
        "Department",
        back_populates="manager_user",
        foreign_keys="Department.manager_id",
        uselist=False,
    )
    goods_exit_approvals = relationship("GoodsExitApproval", back_populates="user")

class GoodsExitApproval(SQLAlchemyModel):
    __tablename__ = "approvals"
    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[ApprovalStatus]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    doc_id: Mapped[int] = mapped_column(ForeignKey("goods_exit_docs.id"))
    modification_date_time: Mapped[datetime] = mapped_column(default=datetime.now(UTC))
    user = relationship("User", back_populates="goods_exit_approvals")
    doc = relationship("GoodsExitDoc", back_populates="approvals")

class GoodsExitDoc(SQLAlchemyModel):
    __tablename__ = "goods_exit_docs"
    id: Mapped[int] = mapped_column(primary_key=True)
    doc_code: Mapped[String8] = mapped_column( unique=True)
    creation_date_time: Mapped[datetime] = mapped_column(default=datetime.now(UTC))
    sending_department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
    sending_department_name: Mapped[String128]
    exit_reason: Mapped[String256]
    destination: Mapped[String128]
    address_: Mapped[String512]
    sending_user_fullname: Mapped[String128]
    exit_for_ever: Mapped[bool]
    receiver_name: Mapped[String128 | None]
    status: Mapped[ApprovalStatus]
    approval_status: Mapped[ApprovalStatus]
    creator_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    approvals = relationship("GoodsExitApproval", back_populates="doc")
    creator_user = relationship("User", backref="goods_exit_docs")
    sending_department = relationship("Department")
    items = relationship("GoodsExit", back_populates="goods_exit_doc")

class GoodsExit(SQLAlchemyModel):
    __tablename__ = "goods_exits"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[String256]
    sap_code: Mapped[String16 | None]
    count: Mapped[int]
    unit_of_measure: Mapped[UOMs]
    goods_exit_doc_id: Mapped[int] = mapped_column(ForeignKey("goods_exit_docs.id"))

    goods_exit_doc = relationship("GoodsExitDoc", back_populates="items")
