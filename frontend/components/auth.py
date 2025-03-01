import streamlit as st
import requests
import json
from typing import Dict, Any, Optional

class AuthManager:
    """认证管理器"""
    
    def __init__(self, api_url: str):
        """初始化认证管理器"""
        self.api_url = api_url
        
        # 初始化会话状态
        if "user" not in st.session_state:
            st.session_state.user = None
        if "token" not in st.session_state:
            st.session_state.token = None
    
    def login_form(self) -> bool:
        """显示登录表单并处理登录"""
        st.markdown('<div class="main-header">用户登录</div>', unsafe_allow_html=True)
        
        # 登录表单
        with st.form("login_form"):
            username = st.text_input("用户名")
            password = st.text_input("密码", type="password")
            submit = st.form_submit_button("登录")
            
            if submit:
                if self._try_login(username, password):
                    return True
        
        # 模拟登录
        st.markdown("### 快速测试登录")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("管理员登录"):
                if self._try_login("admin", "password"):
                    return True
        with col2:
            if st.button("普通用户登录"):
                if self._try_login("user", "password"):
                    return True
        
        return False
    
    def _try_login(self, username: str, password: str) -> bool:
        """尝试登录"""
        try:
            # 模拟API调用
            # 实际应调用登录API
            # response = requests.post(
            #     f"{self.api_url}/api/auth/token",
            #     data={"username": username, "password": password}
            # )
            # if response.status_code == 200:
            #     data = response.json()
            #     st.session_state.token = data["access_token"]
            #     st.session_state.user = data["user"]
            #     return True
            
            # 模拟成功登录
            if (username == "admin" and password == "password") or (username == "user" and password == "password"):
                # 模拟用户信息
                st.session_state.token = "fake_token_123456"
                st.session_state.user = {
                    "id": "user_001" if username == "admin" else "user_002",
                    "username": username,
                    "role": "admin" if username == "admin" else "user",
                    "full_name": "Admin User" if username == "admin" else "Normal User"
                }
                return True
            else:
                st.error("用户名或密码错误")
                return False
                
        except Exception as e:
            st.error(f"登录失败: {str(e)}")
            return False
    
    def logout(self):
        """退出登录"""
        st.session_state.token = None
        st.session_state.user = None
    
    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        return st.session_state.token is not None
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """获取当前用户"""
        return st.session_state.user
    
    def show_user_info(self):
        """显示用户信息"""
        user = self.get_current_user()
        if user:
            st.sidebar.markdown(f"### 欢迎, {user.get('full_name', user.get('username'))}")
            st.sidebar.markdown(f"角色: {user.get('role', 'user')}")
            
            if st.sidebar.button("退出登录"):
                self.logout()
                st.experimental_rerun()