import os
from typing import List, Union, Optional, Dict, Any
from pydantic import BaseModel, validator

class ServerSettings(BaseModel):
    """服务器配置模型"""
    host: str
    port: int
    workers: int
    log_level: str
    debug: bool
    reload: bool

class CorsSettings(BaseModel):
    """CORS配置模型"""
    allowed_origins: List[str]
    allowed_methods: List[str]
    allowed_headers: List[str]

class SecuritySettings(BaseModel):
    """安全配置模型"""
    api_key_header: str
    api_key: str
    jwt_secret: str
    token_expire_minutes: int

class RateLimitSettings(BaseModel):
    """速率限制配置模型"""
    enabled: bool
    max_requests: int
    time_window_seconds: int

class Settings(BaseModel):
    """全局配置设置模型"""
    server: ServerSettings
    cors: CorsSettings
    security: SecuritySettings
    rate_limiting: RateLimitSettings

    @classmethod
    def from_yaml(cls, config_dict: Dict[str, Any]) -> "Settings":
        """从YAML配置字典创建设置对象"""
        return cls(
            server=ServerSettings(**config_dict.get("server", {})),
            cors=CorsSettings(**config_dict.get("cors", {})),
            security=SecuritySettings(**config_dict.get("security", {})),
            rate_limiting=RateLimitSettings(**config_dict.get("rate_limiting", {}))
        )

    class Config:
        env_file = ".env"