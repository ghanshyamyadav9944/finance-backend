from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum
import datetime

class RoleEnum(str, Enum):
    admin = "admin"
    analyst = "analyst"
    viewer = "viewer"

class TypeEnum(str, Enum):
    income = "income"
    expense = "expense"

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: RoleEnum = RoleEnum.viewer

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: RoleEnum
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TransactionCreate(BaseModel):
    amount: float
    type: TypeEnum
    category: str
    date: datetime.date
    notes: Optional[str] = None

class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    type: Optional[TypeEnum] = None
    category: Optional[str] = None
    date: Optional[datetime.date] = None
    notes: Optional[str] = None

class TransactionOut(BaseModel):
    id: int
    amount: float
    type: TypeEnum
    category: str
    date: datetime.date
    notes: Optional[str]
    user_id: int
    is_deleted: bool

    class Config:
        from_attributes = True
