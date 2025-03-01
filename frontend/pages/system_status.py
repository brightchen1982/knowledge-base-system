import streamlit as st
import pandas as pd
import plotly.express as px
import time
import requests
import json

def render():
    st.markdown('<div class="main-header">系统状态</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.metric(label="CPU使用率", value="42%", delta="-5%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.metric(label="内存使用率", value="68%", delta="3%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.metric(label="GPU利用率", value="76%", delta="12%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 系统组件状态
    st.markdown('<div class="sub-header">系统组件状态</div>', unsafe_allow_html=True)
    
    # 模拟API请求获取系统状态
    # response = requests.get(f"{API_URL}/api/system/status")
    # components = response.json()["components"]
    
    # 模拟组件状态数据
    components = [
        {"组件": "API服务", "状态": "运行中", "健康度": 100, "响应时间": "45ms"},
        {"组件": "DeepSeek (Ollama)", "状态": "运行中", "健康度": 100, "响应时间": "350ms"},
        {"组件": "Qdrant向量数据库", "状态": "运行中", "健康度": 98, "响应时间": "32ms"},
        {"组件": "Redis缓存", "状态": "运行中", "健康度": 100, "响应时间": "5ms"},
        {"组件": "工作进程", "状态": "运行中", "健康度": 100, "响应时间": "N/A"},
        {"组件": "前端服务", "状态": "运行中", "健康度": 100, "响应时间": "N/A"}
    ]
    
    # 显示组件状态表格
    df = pd.DataFrame(components)
    st.dataframe(df, use_container_width=True)
    
    # 性能监控
    st.markdown('<div class="sub-header">性能监控</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["资源使用", "请求统计", "索引状态"])
    
    with tab1:
        # 模拟资源使用数据
        time_points = [f"{i}:00" for i in range(24)]
        cpu_usage = [25, 28, 27, 25, 23, 22, 25, 35, 45, 55, 65, 68, 70, 72, 68, 65, 60, 58, 55, 48, 42, 38, 32, 27]
        memory_usage = [45, 45, 45, 45, 45, 45, 45, 48, 55, 65, 68, 70, 72, 75, 73, 72, 70, 68, 65, 60, 55, 50, 48, 45]
        gpu_usage = [10, 10, 10, 10, 10, 10, 10, 35, 55, 65, 75, 82, 85, 88, 85, 80, 75, 70, 65, 50, 40, 30, 20, 15]
        
        usage_data = {"时间": time_points, "CPU使用率": cpu_usage, "内存使用率": memory_usage, "GPU使用率": gpu_usage}
        usage_df = pd.DataFrame(usage_data)
        
        fig = px.line(usage_df, x="时间", y=["CPU使用率", "内存使用率", "GPU使用率"], 
                      title="24小时资源使用趋势",
                      labels={"value": "使用率 (%)", "variable": "资源类型"})
        st.plotly_chart(fig, use_container_width=True)
        
        # 自动刷新选项
        auto_refresh = st.checkbox("自动刷新数据（每60秒）")
        if auto_refresh:
            st.info("已启用自动刷新，数据将每60秒更新一次")
            # 在实际应用中，可以使用st.experimental_rerun()来自动刷新
    
    with tab2:
        # 模拟请求统计数据
        categories = ["文档上传", "文档检索", "聊天请求", "搜索查询", "分析任务"]
        today_counts = [24, 156, 432, 287, 63]
        yesterday_counts = [18, 142, 389, 253, 58]
        
        request_data = {"请求类型": categories, "今日请求数": today_counts, "昨日请求数": yesterday_counts}
        request_df = pd.DataFrame(request_data)
        
        fig = px.bar(request_df, x="请求类型", y=["今日请求数", "昨日请求数"], 
                     title="请求统计",
                     barmode="group",
                     labels={"value": "请求数", "variable": "时间"})
        st.plotly_chart(fig, use_container_width=True)
        
        # 响应时间分布
        response_times = [
            {"响应时间": "<100ms", "占比": 35},
            {"响应时间": "100-300ms", "占比": 42},
            {"响应时间": "300-500ms", "占比": 15},
            {"响应时间": "500ms-1s", "占比": 6},
            {"响应时间": ">1s", "占比": 2}
        ]
        
        response_df = pd.DataFrame(response_times)
        fig = px.pie(response_df, values="占比", names="响应时间", title="响应时间分布")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # 索引状态
        st.markdown("#### 向量索引状态")
        
        index_stats = {
            "总向量数": "1,523,482",
            "索引大小": "5.3 GB",
            "最后更新时间": "2025-02-28 14:32:45",
            "平均检索时间": "27ms",
            "索引分段数": "8",
            "删除向量占比": "3.2%"
        }
        
        # 显示统计信息
        col1, col2, col3 = st.columns(3)
        
        for i, (key, value) in enumerate(index_stats.items()):
            with [col1, col2, col3][i % 3]:
                st.metric(label=key, value=value)
        
        # 增量索引统计
        st.markdown("#### 索引任务统计")
        
        # 模拟索引任务数据
        task_data = {
            "任务类型": ["全量重建", "增量索引", "文档添加", "文档删除", "文档更新"],
            "昨日次数": [1, 24, 18, 3, 5],
            "平均耗时(秒)": [320, 45, 12, 8, 25]
        }
        task_df = pd.DataFrame(task_data)
        st.dataframe(task_df, use_container_width=True)
        
        # 优化按钮
        if st.button("优化索引"):
            with st.spinner("正在优化索引..."):
                time.sleep(3)
                st.success("索引优化完成！检索性能提升约8%")