import streamlit as st
import pandas as pd
import plotly.express as px

def render():
    st.markdown('<div class="main-header">DeepSeek本地知识库系统</div>', unsafe_allow_html=True)
    
    # 系统概览
    st.markdown('<div class="sub-header">系统概览</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.metric(label="文档总数", value="123")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.metric(label="向量数据量", value="5.3 GB")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.metric(label="当日查询次数", value="457")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 快速导航
    st.markdown('<div class="sub-header">快速导航</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 上传新文档", use_container_width=True):
            st.session_state.page = "文档管理"
            st.experimental_rerun()
    
    with col2:
        if st.button("💬 开始聊天", use_container_width=True):
            st.session_state.page = "聊天问答"
            st.experimental_rerun()
    
    # 最近活动
    st.markdown('<div class="sub-header">最近活动</div>', unsafe_allow_html=True)
    
    # 模拟活动数据
    activities = [
        {"时间": "2025-02-28 14:32", "活动": "上传文档", "详情": "财务报表Q4.pdf"},
        {"时间": "2025-02-28 13:45", "活动": "搜索查询", "详情": "2024年销售预测"},
        {"时间": "2025-02-28 11:20", "活动": "数据分析", "详情": "市场趋势分析"},
        {"时间": "2025-02-28 10:05", "活动": "聊天会话", "详情": "5条消息交互"},
        {"时间": "2025-02-27 16:50", "活动": "上传文档", "详情": "战略规划2025.docx"}
    ]
    
    st.table(activities)
    
    # 性能概览
    st.markdown('<div class="sub-header">系统性能</div>', unsafe_allow_html=True)
    
    # 模拟性能数据
    dates = pd.date_range(start='2025-02-20', end='2025-02-28')
    query_times = [120, 115, 118, 105, 98, 92, 85, 88, 90]
    
    performance_data = pd.DataFrame({
        "日期": dates,
        "平均查询时间(ms)": query_times
    })
    
    fig = px.line(performance_data, x='日期', y='平均查询时间(ms)', 
                 title='知识库查询性能趋势',
                 labels={"平均查询时间(ms)": "毫秒"})
    st.plotly_chart(fig, use_container_width=True)