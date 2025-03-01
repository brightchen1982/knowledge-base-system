import streamlit as st
from typing import Dict, List, Any, Optional

def display_header(title: str, subtitle: Optional[str] = None):
    """显示页面标题和副标题"""
    st.markdown(f'<div class="main-header">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<p class="subtitle">{subtitle}</p>', unsafe_allow_html=True)

def display_info_card(label: str, value: str, delta: Optional[str] = None, color: str = "#EFF6FF"):
    """显示信息卡片"""
    st.markdown(f'<div class="info-box" style="background-color: {color};">', unsafe_allow_html=True)
    st.metric(label=label, value=value, delta=delta)
    st.markdown('</div>', unsafe_allow_html=True)

def display_document_card(doc: Dict[str, Any], on_click_callback=None):
    """显示文档卡片"""
    with st.container():
        st.markdown(f"""
        <div style="padding:1rem;border:1px solid #E5E7EB;border-radius:0.5rem;margin:0.5rem 0;">
            <h3>{doc.get('名称', 'Untitled')}</h3>
            <p><b>大小:</b> {doc.get('大小', 'Unknown')}</p>
            <p><b>上传时间:</b> {doc.get('上传时间', 'Unknown')}</p>
            <p><b>分类:</b> {doc.get('分类', 'Uncategorized')}</p>
            <p><b>状态:</b> <span style="color:{get_status_color(doc.get('状态', ''))};">{doc.get('状态', 'Unknown')}</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        if on_click_callback:
            if st.button("查看详情", key=f"view_{doc.get('id', '')}"):
                on_click_callback(doc)

def display_chat_message(message: Dict[str, Any]):
    """显示聊天消息"""
    role = message.get("role", "unknown")
    content = message.get("content", "")
    
    if role == "user":
        st.markdown(f'<div class="chat-message user-message">{content}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-message bot-message">{content}</div>', unsafe_allow_html=True)
        
        # 显示来源（如果有）
        sources = message.get("sources", [])
        if sources:
            st.markdown('<div class="source-box">', unsafe_allow_html=True)
            st.markdown("**参考来源:**")
            for source in sources:
                st.markdown(f"- {source.get('title', 'Unknown')} (P{source.get('page', '?')})")
            st.markdown('</div>', unsafe_allow_html=True)

def display_search_result(result: Dict[str, Any]):
    """显示搜索结果"""
    with st.expander(f"{result.get('title', 'Untitled')} (相关度: {result.get('score', 0):.2f})"):
        st.markdown(f"**位置**: 第{result.get('page', '?')}页")
        st.markdown(f"**更新日期**: {result.get('date', 'Unknown')}")
        st.markdown("**内容片段**:")
        st.markdown(f"<div style='background-color:#F8F9FA;padding:10px;border-radius:5px;'>{result.get('text', '')}</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.button(f"打开文档", key=f"open_{result.get('title', '')}")
        with col2:
            st.button(f"提问相关问题", key=f"ask_{result.get('title', '')}")

def get_status_color(status: str) -> str:
    """根据状态返回颜色"""
    status_colors = {
        "已索引": "green",
        "处理中": "orange",
        "错误": "red",
        "等待中": "blue"
    }
    return status_colors.get(status, "gray")