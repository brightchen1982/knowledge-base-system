from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

class User(BaseModel):
    """用户数据模型"""
    id: str
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    disabled: Optional[bool] = False
    role: str = "user"
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None

class UserCreate(BaseModel):
    """创建用户请求模型"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserUpdate(BaseModel):
    """更新用户请求模型"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    disabled: Optional[bool] = None
    role: Optional[str] = None

class UserInDB(User):
    """数据库存储的用户模型，包含哈希密码"""
    hashed_password: str

class Token(BaseModel):
    """认证令牌模型"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """认证令牌数据模型"""
    username: Optional[str] = None
    exp: Optional[int] = None