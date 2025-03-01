import streamlit as st
import requests
import json
import os
import time
import pandas as pd
import plotly.express as px
from pathlib import Path
import yaml
from io import BytesIO


# 在app.py适当位置添加以下内容

# 导入页面组件
from pages import home, documents, chat, search, analysis, system_status



# 加载配置
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../configs/api.yaml")
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# API基础URL
API_URL = f"http://{config['server']['host']}:{config['server']['port']}"

# 设置页面配置
st.set_page_config(
    page_title="DeepSeek本地知识库系统",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 添加CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #1E3A8A;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin: 1rem 0;
        color: #2563EB;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .user-message {
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
    }
    .bot-message {
        background-color: #F3F4F6;
        border: 1px solid #E5E7EB;
    }
    .source-box {
        font-size: 0.8rem;
        padding: 0.5rem;
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 0.25rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# 导航设置
def main():
        # 侧边栏菜单
    st.sidebar.markdown("## 📚 DeepSeek知识库")
    page = st.sidebar.radio(
        "导航",
        ["首页", "文档管理", "聊天问答", "搜索", "数据分析", "系统状态"]
    )
    
    # 根据页面选择渲染对应内容
    if page == "首页":
        home.render()
    elif page == "文档管理":
        documents.render()
    elif page == "聊天问答":
        chat.render()
    elif page == "搜索":
        search.render()
    elif page == "数据分析":
        analysis.render()
    elif page == "系统状态":
        system_status.render()
    # 侧边栏菜单
    # st.sidebar.markdown("## 📚 DeepSeek知识库")
    # page = st.sidebar.radio(
    #     "导航",
    #     ["首页", "文档管理", "聊天问答", "搜索", "数据分析", "系统状态"]
    # )
    
    # # 根据页面选择渲染对应内容
    # if page == "首页":
    #     render_home()
    # elif page == "文档管理":
    #     render_document_manager()
    # elif page == "聊天问答":
    #     render_chat()
    # elif page == "搜索":
    #     render_search()
    # elif page == "数据分析":
    #     render_analysis()
    # elif page == "系统状态":
    #     render_system_status()

# 首页
def render_home():
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

# 文档管理页面
def render_document_manager():
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
                    # 模拟上传处理
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

# 聊天问答页面
def render_chat():
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

# 搜索页面
def render_search():
    st.markdown('<div class="main-header">知识库搜索</div>', unsafe_allow_html=True)
    
    # 搜索输入
    search_query = st.text_input("输入搜索查询", placeholder="例如：2024年销售预测...")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        search_mode = st.radio("搜索模式", ["语义搜索", "关键词搜索", "混合搜索"])
    with col2:
        filter_category = st.multiselect("按分类筛选", ["财务", "技术", "营销", "法律", "人力资源"])
    with col3:
        date_range = st.date_input("日期范围", [])
    
    search_button = st.button("搜索", use_container_width=True)
    
    # 如果搜索按钮被点击且有查询
    if search_button and search_query:
        with st.spinner("正在搜索..."):
            time.sleep(1)  # 模拟搜索延迟
            
            # 模拟搜索结果
            search_results = [
                {
                    "title": "财务报表Q4.pdf",
                    "page": 12,
                    "text": "...2024年第四季度销售额比第三季度增长了15%，主要得益于新产品线的推出和假日促销活动的成功。总收入达到了1.2亿元，超过了预期目标8%...",
                    "score": 0.92,
                    "date": "2025-02-28"
                },
                {
                    "title": "销售预测分析.xlsx",
                    "page": 3,
                    "text": "...基于历史数据分析，我们预计2025年销售增长率将保持在12-15%之间，累计销售额预计达到4.8亿元...",
                    "score": 0.87,
                    "date": "2025-02-25"
                },
                {
                    "title": "营销策略2025.pptx",
                    "page": 8,
                    "text": "...针对2024年销售数据，新的数字营销策略将增加社交媒体投入30%，预计带来额外15%的销售增长...",
                    "score": 0.81,
                    "date": "2025-02-26"
                }
            ]
            
            # 显示搜索结果
            st.markdown(f"### 搜索结果: 找到 {len(search_results)} 条匹配项")
            
            for result in search_results:
                with st.expander(f"{result['title']} (相关度: {result['score']:.2f})"):
                    st.markdown(f"**位置**: 第{result['page']}页")
                    st.markdown(f"**更新日期**: {result['date']}")
                    st.markdown("**内容片段**:")
                    st.markdown(f"<div style='background-color:#F8F9FA;padding:10px;border-radius:5px;'>{result['text']}</div>", unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.button(f"打开文档 {result['title']}", key=f"open_{result['title']}")
                    with col2:
                        st.button(f"提问相关问题 {result['title']}", key=f"ask_{result['title']}")

# 数据分析页面
def render_analysis():
    st.markdown('<div class="main-header">数据分析</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["文档分析", "文本分析", "预测分析"])
    
    with tab1:
        st.markdown("### 文档分析")
        
        # 选择文档
        selected_doc = st.selectbox(
            "选择要分析的文档",
            ["财务报表Q4.pdf", "产品规格说明.docx", "营销策略2025.pptx", "客户调研报告.xlsx"]
        )
        
        # 分析选项
        col1, col2 = st.columns(2)
        with col1:
            focus_areas = st.multiselect(
                "分析重点领域",
                ["关键数据指标", "趋势分析", "风险评估", "机会识别", "竞争分析"],
                ["关键数据指标", "趋势分析"]
            )
        with col2:
            analysis_depth = st.select_slider(
                "分析深度",
                options=["基础概述", "标准分析", "深度分析"]
            )
        
        # 分析按钮
        if st.button("开始文档分析", use_container_width=True):
            with st.spinner("正在分析文档..."):
                time.sleep(2)  # 模拟分析延迟
                
                # 模拟分析结果
                st.success("分析完成！")
                
                st.markdown("#### 分析摘要")
                st.markdown("""
                该财务报表显示2024年第四季度业绩良好，销售额同比增长15%，总收入达1.2亿元，超预期8%。
                主要增长来自新产品线（贡献35%）和假日促销活动（贡献25%）。
                运营成本控制良好，同比下降3%，主要得益于数字化转型项目带来的效率提升。
                """)
                
                st.markdown("#### 关键发现")
                key_findings = [
                    "销售增长：Q4销售额同比增长15%，环比增长8%",
                    "成本控制：运营成本同比下降3%",
                    "利润率：毛利率提升2.5个百分点至38.5%",
                    "区域表现：华东区表现最佳，增长22%",
                    "挑战：供应链延迟导致某些产品线库存不足"
                ]
                for finding in key_findings:
                    st.markdown(f"- {finding}")
                
                # 模拟可视化
                data = {
                    "季度": ["Q1", "Q2", "Q3", "Q4"],
                    "销售额": [78, 85, 102, 120],
                    "成本": [52, 55, 65, 73],
                    "利润": [26, 30, 37, 47]
                }
                df = pd.DataFrame(data)
                
                # 绘制图表
                fig = px.line(df, x="季度", y=["销售额", "成本", "利润"], 
                              title="2024年季度业绩趋势",
                              labels={"value": "金额（百万元）", "variable": "指标"})
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### 文本分析")
        
        # 文本输入
        text_input = st.text_area(
            "输入要分析的文本",
            height=200,
            placeholder="粘贴需要分析的文本内容..."
        )
        
        # 分析类型
        analysis_type = st.multiselect(
            "选择分析类型",
            ["情感分析", "关键词提取", "主题识别", "摘要生成", "实体识别"],
            ["情感分析", "关键词提取", "摘要生成"]
        )
        
        # 分析按钮
        if st.button("分析文本", use_container_width=True):
            if text_input:
                with st.spinner("分析中..."):
                    time.sleep(1.5)  # 模拟分析延迟
                    
                    # 模拟分析结果
                    st.success("文本分析完成！")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if "情感分析" in analysis_type:
                            st.markdown("#### 情感分析")
                            st.progress(75)
                            st.markdown("总体情感：**积极** (75%)")
                        
                        if "主题识别" in analysis_type:
                            st.markdown("#### 主题识别")
                            topics = ["业务增长", "市场扩张", "产品创新"]
                            for topic in topics:
                                st.markdown(f"- {topic}")
                    
                    with col2:
                        if "关键词提取" in analysis_type:
                            st.markdown("#### 关键词")
                            keywords = ["销售增长", "市场份额", "产品线", "创新", "客户满意度"]
                            for kw in keywords:
                                st.markdown(f"- {kw}")
                        
                        if "实体识别" in analysis_type:
                            st.markdown("#### 识别的实体")
                            entities = [
                                {"text": "华东区", "type": "地理位置"},
                                {"text": "新产品A", "type": "产品"},
                                {"text": "2024年", "type": "时间"}
                            ]
                            for entity in entities:
                                st.markdown(f"- {entity['text']} ({entity['type']})")
                    
                    if "摘要生成" in analysis_type:
                        st.markdown("#### 自动摘要")
                        st.markdown("""
                        该文本主要讨论了公司2024年第四季度的业绩表现，重点关注销售增长和新产品线的成功。
                        文本表明公司在华东地区取得了显著增长，新产品线表现超出预期。
                        同时也提到了一些运营成本优化和未来增长策略。
                        """)
            else:
                st.error("请输入要分析的文本")
    
    with tab3:
        st.markdown("### 预测分析")
        
        # 预测配置
        col1, col2 = st.columns(2)
        with col1:
            prediction_target = st.selectbox(
                "预测目标",
                ["销售额预测", "市场份额预测", "客户增长预测", "成本预测"]
            )
            time_horizon = st.selectbox(
                "时间范围",
                ["下个季度", "未来6个月", "下一财年", "未来3年"]
            )
        
        with col2:
            data_source = st.multiselect(
                "数据来源",
                ["历史销售数据", "市场研究报告", "竞争对手分析", "宏观经济指标", "客户反馈"],
                ["历史销售数据", "市场研究报告"]
            )
            confidence_level = st.slider("置信度要求", 75, 99, 90)
        
        # 上传自定义数据（可选）
        upload_custom = st.checkbox("上传自定义数据")
        if upload_custom:
            custom_data = st.file_uploader("上传CSV或Excel文件", type=["csv", "xlsx"])
        
        # 预测按钮
        if st.button("生成预测", use_container_width=True):
            with st.spinner("生成预测分析..."):
                time.sleep(2)  # 模拟分析延迟
                
                # 模拟预测结果
                st.success("预测分析完成！")
                
                st.markdown("#### 预测摘要")
                st.markdown("""
                基于历史数据分析和当前市场趋势，预测2025年第一季度销售额将达到1.32亿元，同比增长17%，环比增长10%。
                预测置信区间为1.26亿元至1.38亿元（90%置信度）。
                增长主要来源预计是新产品线持续的市场渗透和线上渠道的扩展。
                """)
                
                # 预测图表
                forecast_data = {
                    "时间": ["2024 Q1", "2024 Q2", "2024 Q3", "2024 Q4", "2025 Q1 (预测)"],
                    "销售额": [78, 85, 102, 120, 132],
                    "下限": [78, 85, 102, 120, 126],
                    "上限": [78, 85, 102, 120, 138]
                }
                df = pd.DataFrame(forecast_data)
                
                fig = px.line(df, x="时间", y="销售额", 
                              title="销售额预测（含90%置信区间）",
                              labels={"销售额": "金额（百万元）", "时间": "季度"})
                
                # 添加置信区间
                fig.add_scatter(x=df["时间"], y=df["上限"], mode="lines", line=dict(width=0), showlegend=False)
                fig.add_scatter(x=df["时间"], y=df["下限"], mode="lines", line=dict(width=0), 
                                fill="tonexty", fillcolor="rgba(0,100,255,0.2)", name="90%置信区间")
                
                st.plotly_chart(fig, use_container_width=True)
                
                # 影响因素
                st.markdown("#### 关键影响因素")
                factors = [
                    {"因素": "新产品推出", "影响": "正面", "权重": 35},
                    {"因素": "市场竞争加剧", "影响": "负面", "权重": 20},
                    {"因素": "线上渠道扩展", "影响": "正面", "权重": 25},
                    {"因素": "季节性波动", "影响": "中性", "权重": 10},
                    {"因素": "宏观经济环境", "影响": "正面", "权重": 10}
                ]
                
                st.dataframe(factors, use_container_width=True)
                
                # 建议措施
                st.markdown("#### 建议措施")
                recommendations = [
                    "增加新产品线的营销投入，重点关注市场接受度高的产品",
                    "加强线上销售渠道建设，优化用户体验",
                    "密切监控竞争对手动态，调整差异化策略",
                    "提前备货应对季节性需求高峰，优化供应链弹性",
                    "建立动态预测模型，每月更新销售预测"
                ]
                
                for i, rec in enumerate(recommendations):
                    st.markdown(f"{i+1}. {rec}")

# 系统状态页面
def render_system_status():
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
        
        for key, value in index_stats.items():
            st.metric(label=key, value=value)
        
        if st.button("优化索引"):
            with st.spinner("正在优化索引..."):
                time.sleep(3)
                st.success("索引优化完成！检索性能提升约8%")

if __name__ == "__main__":
    main() 
