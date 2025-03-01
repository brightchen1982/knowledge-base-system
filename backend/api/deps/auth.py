from fastapi import Depends, HTTPException, status, WebSocket
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from typing import Optional
from ..core.security import decode_token, API_KEY
from ..models.user import User, TokenData

# OAuth2配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# API密钥配置
api_key_scheme = APIKeyHeader(name="X-API-Key")

# 模拟用户数据库（实际应用中应从数据库获取）
fake_users_db = {
    "admin": {
        "id": "user_001",
        "username": "admin",
        "email": "admin@example.com",
        "full_name": "Admin User",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
        "disabled": False,
        "role": "admin"
    },
    "user": {
        "id": "user_002",
        "username": "user",
        "email": "user@example.com",
        "full_name": "Normal User",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
        "disabled": False,
        "role": "user"
    }
}

async def get_user_by_token(token_data: TokenData) -> User:
    """通过令牌数据获取用户"""
    if token_data.username not in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    user_data = fake_users_db[token_data.username]
    return User(**user_data)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """获取当前用户"""
    # 尝试解码令牌
    token_data = decode_token(token)
    
    # 获取用户
    user = await get_user_by_token(token_data)
    
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已禁用"
        )
    
    return user

async def validate_api_key(api_key: str = Depends(api_key_scheme)) -> bool:
    """验证API密钥"""
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的API密钥"
        )
    return True

async def get_token_from_websocket(websocket: WebSocket) -> Optional[str]:
    """从WebSocket连接获取令牌"""
    # 尝试从查询参数获取令牌
    token = websocket.query_params.get("token")
    
    # 如果查询参数中没有令牌，尝试从头部获取
    if not token:
        # 从Authorization头部获取
        auth_header = websocket.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
    
    return token