from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from passlib.context import CryptContext
from ..models.user import User, TokenData

# 密码处理上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# API密钥配置
api_key_scheme = APIKeyHeader(name="X-API-Key")

# 从配置加载设置
try:
    import yaml
    with open("configs/api.yaml", "r") as f:
        config = yaml.safe_load(f)
        SECRET_KEY = config["security"]["jwt_secret"]
        ALGORITHM = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES = config["security"]["token_expire_minutes"]
        API_KEY = config["security"]["api_key"]
except:
    # 默认值，实际生产中应该从环境变量或安全存储加载
    SECRET_KEY = "your-jwt-secret-here"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24小时
    API_KEY = "your-api-key-here"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    
    # 设置过期时间
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # 编码JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> TokenData:
    """解码令牌"""
    try:
        # 解码JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        exp = payload.get("exp")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭证",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return TokenData(username=username, exp=exp)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )