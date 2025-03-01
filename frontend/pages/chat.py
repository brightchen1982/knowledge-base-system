import streamlit as st
import pandas as pd
import time
import json
import uuid

def render():
    st.markdown('<div class="main-header">知识库问答</div>', unsafe_allow_html=True)
    
    # 初始化会话历史
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # 显示聊天设置
    with st.sidebar.expander("聊天设置", expanded=False):
        use_rag = st.checkbox("使用知识库增强", value=True)
        if use_rag:
            search_scope = st.radio("搜索范围", ["全部文档", "选定文档"])
            if search_scope == "选定文档":
                # 模拟文档选择
                selected_docs = st.multiselect(
                    "选择文档",
                    ["财务报表Q4.pdf", "产品规格说明.docx", "营销策略2025.pptx", "客户调研报告.xlsx", "法律合同模板.docx"]
                )
        
        model = st.selectbox("模型", ["DeepSeek-V3", "DeepSeek-R1"])
        temperature = st.slider("随机性", 0.0, 1.0, 0.7, 0.1)
        max_tokens = st.slider("最大生成长度", 256, 4096, 2048, 128)
    
    # 显示对话历史
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message user-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message bot-message">{message["content"]}</div>', unsafe_allow_html=True)
            
            # 显示来源（如果有）
            if "sources" in message and message["sources"]:
                st.markdown('<div class="source-box">', unsafe_allow_html=True)
                st.markdown("**参考来源:**")
                for source in message["sources"]:
                    st.markdown(f"- {source['title']} (P{source['page']})")
                st.markdown('</div>', unsafe_allow_html=True)
    
    # 输入框
    user_input = st.text_area("输入您的问题", height=100)
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("发送", use_container_width=True):
            if user_input:
                # 添加用户消息
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                # 模拟API调用
                with st.spinner("思考中..."):
                    time.sleep(1)  # 模拟响应延迟
                
                # 模拟回复
                bot_reply = {
                    "role": "assistant", 
                    "content": "根据我们的财务报表分析，2024年第四季度销售额比第三季度增长了15%，主要得益于新产品线的推出和假日促销活动的成功。总收入达到了1.2亿元，超过了预期目标8%。",
                    "sources": [
                        {"title": "财务报表Q4.pdf", "page": 12},
                        {"title": "销售预测分析.xlsx", "page": 3}
                    ]
                }
                
                # 添加回复
                st.session_state.messages.append(bot_reply)
                
                # 刷新界面显示新消息
                st.experimental_rerun()
    with col2:
        if st.button("清空对话", use_container_width=True):
            st.session_state.messages = []
            st.experimental_rerun()