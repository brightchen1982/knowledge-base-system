import streamlit as st
import pandas as pd
import time
import requests
import json
from datetime import datetime

def render():
    st.markdown('<div class="main-header">文档管理</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["上传文档", "文档列表"])
    
    with tab1:
        st.markdown('<div class="sub-header">上传新文档</div>', unsafe_allow_html=True)
        
        # 文件上传界面
        uploaded_file = st.file_uploader("选择要上传的文件", 
                                         type=["pdf", "docx", "txt", "xlsx", "html"])
        
        # 元数据输入
        with st.expander("添加文档元数据"):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("标题")
                category = st.selectbox("分类", ["财务", "技术", "营销", "法律", "人力资源", "其他"])
            with col2:
                tags = st.text_input("标签（用逗号分隔）")
                importance = st.slider("重要性", 1, 5, 3)
        
        # 上传按钮
        if st.button("上传并索引"):
            if uploaded_file is not None:
                with st.spinner("正在处理文档..."):
                    # 准备元数据
                    metadata = {
                        "title": title if title else uploaded_file.name,
                        "category": category,
                        "tags": tags.split(",") if tags else [],
                        "importance": importance,
                        "upload_time": datetime.now().isoformat()
                    }
                    
                    # 模拟上传请求
                    # 注意：实际代码中应该调用API上传文档
                    # files = {"file": uploaded_file.getbuffer()}
                    # data = {"metadata": json.dumps(metadata)}
                    # response = requests.post(f"{API_URL}/api/documents/upload", files=files, data=data)
                    
                    # 模拟上传进度
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.05)
                        progress_bar.progress(i + 1)
                    
                    # 模拟成功消息
                    st.success(f"文档 '{uploaded_file.name}' 上传成功并已添加到索引！")
            else:
                st.error("请先选择要上传的文件")
    
    with tab2:
        st.markdown('<div class="sub-header">文档列表</div>', unsafe_allow_html=True)
        
        # 搜索和过滤
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search_term = st.text_input("搜索文档", placeholder="输入关键词...")
        with col2:
            category_filter = st.selectbox("分类筛选", ["全部", "财务", "技术", "营销", "法律", "人力资源", "其他"])
        with col3:
            sort_option = st.selectbox("排序方式", ["上传时间", "名称", "大小", "重要性"])
        
        # 模拟文档列表
        documents = [
            {"id": "doc1", "名称": "财务报表Q4.pdf", "大小": "2.3 MB", "上传时间": "2025-02-28", "分类": "财务", "状态": "已索引"},
            {"id": "doc2", "名称": "产品规格说明.docx", "大小": "1.1 MB", "上传时间": "2025-02-27", "分类": "技术", "状态": "已索引"},
            {"id": "doc3", "名称": "营销策略2025.pptx", "大小": "5.4 MB", "上传时间": "2025-02-26", "分类": "营销", "状态": "处理中"},
            {"id": "doc4", "名称": "客户调研报告.xlsx", "大小": "3.7 MB", "上传时间": "2025-02-25", "分类": "营销", "状态": "已索引"},
            {"id": "doc5", "名称": "法律合同模板.docx", "大小": "0.5 MB", "上传时间": "2025-02-24", "分类": "法律", "状态": "已索引"}
        ]
        
        # 过滤文档
        if search_term:
            documents = [doc for doc in documents if search_term.lower() in doc["名称"].lower()]
            
        if category_filter != "全部":
            documents = [doc for doc in documents if doc["分类"] == category_filter]
            
        # 排序文档
        if sort_option == "上传时间":
            documents.sort(key=lambda x: x["上传时间"], reverse=True)
        elif sort_option == "名称":
            documents.sort(key=lambda x: x["名称"])
        elif sort_option == "大小":
            # 转换大小字符串为数字进行排序
            def size_to_mb(size_str):
                value = float(size_str.split()[0])
                return value
            documents.sort(key=lambda x: size_to_mb(x["大小"]), reverse=True)
        
        # 显示文档列表
        st.dataframe(documents, use_container_width=True)
        
        # 批量操作
        col1, col2 = st.columns(2)
        with col1:
            if st.button("删除选中文档"):
                st.warning("请确认是否删除选中的文档？")
        with col2:
            if st.button("重新索引"):
                with st.spinner("正在重新索引..."):
                    time.sleep(2)
                    st.success("重新索引完成！")