import streamlit as st
import pandas as pd
import time
import plotly.express as px
import requests
import json

def render():
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
                
                # 模拟API请求
                # focus_areas_str = ", ".join(focus_areas)
                # response = requests.post(
                #     f"{API_URL}/api/analysis/document",
                #     json={"document_id": "doc1", "focus_areas": focus_areas_str, "instructions": analysis_depth}
                # )
                # analysis_result = response.json()
                
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
                    
                    # 模拟API请求
                    # focus_areas = ", ".join(analysis_type)
                    # response = requests.post(
                    #     f"{API_URL}/api/analysis/text",
                    #     json={"text": text_input, "focus_areas": focus_areas}
                    # )
                    # analysis_result = response.json()
                    
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
                
                # 模拟API请求
                # historical_data = "历史销售数据..." if not custom_data else "上传的数据..."
                # context = f"数据来源: {', '.join(data_source)}; 置信度: {confidence_level}%"
                # response = requests.post(
                #     f"{API_URL}/api/analysis/predict",
                #     json={
                #         "historical_data": historical_data, 
                #         "target": prediction_target, 
                #         "context": context
                #     }
                # )
                # prediction_result = response.json()
                
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