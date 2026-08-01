---
doc_type: audit_report
title: 候选模块清单 — D_INTELLIGENCE
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# D_INTELLIGENCE 候选模块清单

> [← 返回索引](index.md)

> 本域候选 **188** 条（原有 1 + harvest 187）。
> harvest 去重四态: likely_new=134 / likely_implemented=50 / uncertain=3

## 完整清单

| ID | 名称 / Name | 大白话（干什么用） | 域 | 状态 | 四问卡点 | 优先级 | 触发信号摘要 | 下次复查 |
|------|------|------|------|------|------|:---:|------|------|
| CAND-AISA-001 | AI Sentiment Analyzer / AI 舆情分析器 | A股受政策和新闻影响大。这模块用AI读新闻/公告/研报打情绪分，给交易决策参考。但还在评估：是不是直接让AI运行时做就行，不用专门建模块。 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P1 | 实盘出现政策驱动的板块异动但信号系统未捕获 等3条 | 2026-10-31 |
| CAND-HARVEST-0009 | Cross-Market Transmission Quantitative Model 跨市场传导量化模型 | Cross-Market Transmission Quantitative Model 跨市场传导量化模型（来源:交易决策架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0031 | AI协作策略与人机信任模型 | AI协作策略与人机信任模型（来源:交易决策架构.md, uncertain） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0032 | Auto Backtest & Simulation 自动回测与仿真 | Auto Backtest & Simulation 自动回测与仿真（来源:交易决策架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0034 | AI自治运维 | AI自治运维（来源:交易决策架构.md, uncertain） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0035 | ML模型工厂 | ML模型工厂（来源:交易决策架构.md, uncertain） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0043 | 知识模型自进化 Model Knowledge | 知识模型自进化 Model Knowledge（来源:交易决策架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0193 | Feature Store特征存储 | Feature Store特征存储（来源:交易决策架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0194 | Experiment Tracker实验追踪 | Experiment Tracker实验追踪（来源:交易决策架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0195 | Notebook Integration Notebook集成 | Notebook Integration Notebook集成（来源:交易决策架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0196 | Reproducibility Manager可复现性管理 | Reproducibility Manager可复现性管理（来源:交易决策架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0197 | Hypothesis Manager假设管理 | Hypothesis Manager假设管理（来源:交易决策架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0198 | LLM Research Agent LLM研究助手 | LLM Research Agent LLM研究助手（来源:交易决策架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0199 | Strategy Iteration Upgrader策略迭代升级 | Strategy Iteration Upgrader策略迭代升级（来源:交易决策架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0545 | Data Quality Scorer 数据质量评分器 | Data Quality Scorer 数据质量评分器（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0643 | Research Data Manager 研究数据管理器 | Research Data Manager 研究数据管理器（来源:数据架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0644 | Research Data Sandbox 研究数据沙箱 | Research Data Sandbox 研究数据沙箱（来源:数据架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0645 | Research Information Barrier 研究信息隔离 | Research Information Barrier 研究信息隔离（来源:数据架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0646 | Research Asset Versioning 研究资产版本化 | Research Asset Versioning 研究资产版本化（来源:数据架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0847 | Research Catalog 研究目录 | Research Catalog 研究目录（来源:ZephyrAlpha全系统模块清单.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0848 | Paper Tracker 论文追踪器 | Paper Tracker 论文追踪器（来源:ZephyrAlpha全系统模块清单.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0849 | Research Workflow Engine 研究工作流引擎 | Research Workflow Engine 研究工作流引擎（来源:ZephyrAlpha全系统模块清单.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0850 | Research Collaboration Hub 研究协作中心 | Research Collaboration Hub 研究协作中心（来源:ZephyrAlpha全系统模块清单.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0851 | Research Experiment Anomaly Detector 研究实验异常检测器 | Research Experiment Anomaly Detector 研究实验异常检测器（来源:ZephyrAlpha全系统模块清单.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0852 | Research Discovery Knowledge Base 研究发现知识库 | Research Discovery Knowledge Base 研究发现知识库（来源:ZephyrAlpha全系统模块清单.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0853 | Research Reproducibility Pack Generator 研究复现包生成器 | Research Reproducibility Pack Generator 研究复现包生成器（来源:ZephyrAlpha全系统模块清单.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1214 | Research Knowledge Precipitator 研究知识沉淀器 | Research Knowledge Precipitator 研究知识沉淀器（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1874 | AutoML Engine 自动ML引擎 | AutoML Engine 自动ML引擎（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1908 | Backtest-to-Production Deployer 回测到生产部署器 | Backtest-to-Production Deployer 回测到生产部署器（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1910 | S0 多模态知识采集层 S0 Multimodal Knowledge Collection Layer | S0 多模态知识采集层 S0 Multimodal Knowledge Collection Layer（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1911 | Whisper 语音转写引擎 | Whisper 语音转写引擎（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1912 | OCR 光学字符识别 | OCR 光学字符识别（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1913 | 漂移感知调度 Drift-Aware Scheduling | 漂移感知调度 Drift-Aware Scheduling（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1914 | VLM图表视觉理解 VLM Chart Visual Understanding | VLM图表视觉理解 VLM Chart Visual Understanding（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1915 | 时序基础模型骨干 TimesFM Foundation Model Backbone | 时序基础模型骨干 TimesFM Foundation Model Backbone（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1916 | S1 知识清洗与结构化层 S1 Knowledge Cleaning & Structuring Layer | S1 知识清洗与结构化层 S1 Knowledge Cleaning & Structuring Layer（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1917 | 信息价值评分 Information Value Scoring | 信息价值评分 Information Value Scoring（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1918 | S2 知识分类与策略提取层 S2 Knowledge Classification & Strategy Extraction Layer | S2 知识分类与策略提取层 S2 Knowledge Classification & Strategy Extraction Layer（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1919 | 因果发现引擎 Causal Discovery Engine | 因果发现引擎 Causal Discovery Engine（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1920 | 辩论式因子精炼 Debate-based Factor Refinement | 辩论式因子精炼 Debate-based Factor Refinement（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1921 | S3 模块映射与工厂匹配层 S3 Module Mapping & Factory Matching Layer | S3 模块映射与工厂匹配层 S3 Module Mapping & Factory Matching Layer（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1922 | S4 模块创建与接入层 S4 Module Creation & Integration Layer | S4 模块创建与接入层 S4 Module Creation & Integration Layer（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1924 | 三重语义一致性 Triple Semantic Consistency | 三重语义一致性 Triple Semantic Consistency（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1927 | S5 试运行与验证层 S5 Trial Run & Validation Layer | S5 试运行与验证层 S5 Trial Run & Validation Layer（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1928 | 参数稳定性区域 Parameter Stability Plateau | 参数稳定性区域 Parameter Stability Plateau（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1929 | 数学反思闭环 Mathematical Reflection Loop | 数学反思闭环 Mathematical Reflection Loop（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1930 | Purge Gap 清洗间隔 | Purge Gap 清洗间隔（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1931 | S6 元学习与自我进化层 S6 Meta-Learning & Self-Evolution Layer | S6 元学习与自我进化层 S6 Meta-Learning & Self-Evolution Layer（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1932 | STOP Prompt自优化 Prompt Self-Optimization | STOP Prompt自优化 Prompt Self-Optimization（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1933 | RISE 代码自纠正 Code Self-Correction | RISE 代码自纠正 Code Self-Correction（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1934 | Voyager 技能库 Skill Library | Voyager 技能库 Skill Library（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1935 | Meta-Harness 元优化器 Meta-Optimizer | Meta-Harness 元优化器 Meta-Optimizer（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1936 | 在线EWC Online Elastic Weight Consolidation | 在线EWC Online Elastic Weight Consolidation（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1937 | 轻量Agent化 Lightweight Agentification | 轻量Agent化 Lightweight Agentification（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1939 | 模块工厂 Module Factory | 模块工厂 Module Factory（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1940 | Module Registry 模块注册表 | Module Registry 模块注册表（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1944 | MLOps闭环 MLOps Closed Loop | MLOps闭环 MLOps Closed Loop（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1945 | 共形漂移检测 Conformal Drift Detection | 共形漂移检测 Conformal Drift Detection（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1946 | 多尺度漂移检测 Multi-Scale Drift Detection | 多尺度漂移检测 Multi-Scale Drift Detection（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1947 | 表示学习驱动漂移检测 Representation Learning Drift Detection | 表示学习驱动漂移检测 Representation Learning Drift Detection（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1948 | 人机协作模式 Human-AI Collaboration Mode | 人机协作模式 Human-AI Collaboration Mode（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1949 | K线分词机制 K-line Tokenization | K线分词机制 K-line Tokenization（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1951 | Sentiment Engine 情感分析引擎 | Sentiment Engine 情感分析引擎（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1952 | Filing NLP Engine 公告NLP引擎 | Filing NLP Engine 公告NLP引擎（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1953 | 多模态融合引擎 Multimodal Fusion Engine | 多模态融合引擎 Multimodal Fusion Engine（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1954 | A股特色数据 A-Share Special Data | A股特色数据 A-Share Special Data（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1955 | Trading Domain NLP Engine 交易领域NLP引擎 | Trading Domain NLP Engine 交易领域NLP引擎（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1956 | Knowledge Quality Assessor 知识质量评估器 | Knowledge Quality Assessor 知识质量评估器（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1957 | Signal Extractor 信号提取器 | Signal Extractor 信号提取器（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1958 | CausalNLP 文本因果声明提取 | CausalNLP 文本因果声明提取（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1959 | TimePC时序因果发现 TimePC Temporal Causal Discovery | TimePC时序因果发现 TimePC Temporal Causal Discovery（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1960 | Neural Granger Causality 神经Granger因果 | Neural Granger Causality 神经Granger因果（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1961 | Causal KG 因果方向标注 | Causal KG 因果方向标注（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1962 | LLM引导因果发现先验 LLM Prior Causal Discovery | LLM引导因果发现先验 LLM Prior Causal Discovery（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1963 | 带干预的时序因果发现 Intervention-Enhanced Temporal Causal Discovery | 带干预的时序因果发现 Intervention-Enhanced Temporal Causal Discovery（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1964 | 因果验证层 Causal Validation Layer | 因果验证层 Causal Validation Layer（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1965 | 因子语义去重 Factor Semantic Deduplication | 因子语义去重 Factor Semantic Deduplication（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1966 | GraphRAG图增强检索 GraphRAG Graph-Enhanced Retrieval | GraphRAG图增强检索 GraphRAG Graph-Enhanced Retrieval（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1967 | 带推理路径的KG-RAG KG-RAG with Reasoning Path | 带推理路径的KG-RAG KG-RAG with Reasoning Path（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1968 | KG引导多跳推理 KG-Guided Multi-Hop Reasoning | KG引导多跳推理 KG-Guided Multi-Hop Reasoning（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1969 | 神经符号融合推理 Neuro-Symbolic Fusion Reasoning | 神经符号融合推理 Neuro-Symbolic Fusion Reasoning（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1970 | 宏观因果传导路径 Macro Causal Transmission Path | 宏观因果传导路径 Macro Causal Transmission Path（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1971 | 创意拓宽模式 Creative Broadening Mode | 创意拓宽模式 Creative Broadening Mode（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1972 | 因果发现三阶段扩展 Causal Discovery 3-Stage Extension | 因果发现三阶段扩展 Causal Discovery 3-Stage Extension（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1973 | Causal Factor Validator 因果因子验证器 | Causal Factor Validator 因果因子验证器（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1974 | PDF预测引擎 PDF Prediction Engine | PDF预测引擎 PDF Prediction Engine（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1975 | Module Matcher 模块匹配器 | Module Matcher 模块匹配器（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1976 | 质量-多样性优化 Quality-Diversity Optimization | 质量-多样性优化 Quality-Diversity Optimization（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1977 | LLM遗传编程变异算子 LLM Genetic Programming Mutation | LLM遗传编程变异算子 LLM Genetic Programming Mutation（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1978 | Module Dependency Graph 模块依赖图 | Module Dependency Graph 模块依赖图（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1979 | Market Regime Detector 市场制度检测器 | Market Regime Detector 市场制度检测器（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1982 | 三重语义一致性约束 Triple Semantic Consistency Constraint | 三重语义一致性约束 Triple Semantic Consistency Constraint（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1983 | Generator 生成器Agent | Generator 生成器Agent（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1984 | Critic 批判器Agent | Critic 批判器Agent（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1985 | Judge 裁判Agent | Judge 裁判Agent（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1986 | 轨迹级进化 Trajectory-level Evolution | 轨迹级进化 Trajectory-level Evolution（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1988 | 可解释设计约束 Explainable By Design Constraint | 可解释设计约束 Explainable By Design Constraint（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1989 | Factor Mining Agent 因子挖掘Agent | Factor Mining Agent 因子挖掘Agent（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1990 | Hypothesis Manager 假设管理器 | Hypothesis Manager 假设管理器（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1991 | 决策树学习 Decision Tree Learning | 决策树学习 Decision Tree Learning（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1993 | SHAP值解释 SHAP Value Explanation | SHAP值解释 SHAP Value Explanation（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1994 | 决策路径可视化 Decision Path Visualization | 决策路径可视化 Decision Path Visualization（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1995 | DSR扩展 Deflated Sharpe Ratio Extension | DSR扩展 Deflated Sharpe Ratio Extension（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1996 | CPCV v2 Combinatorial Purged Cross-Validation v2 CPCV v2组合净化交叉验证v2 | CPCV v2 Combinatorial Purged Cross-Validation v2 CPCV v2组合净化交叉验证v2（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1997 | White's Reality Check 怀特现实检验 | White's Reality Check 怀特现实检验（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1998 | Adaptive Walk-Forward 自适应Walk-Forward | Adaptive Walk-Forward 自适应Walk-Forward（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1999 | Probabilistic Backtesting 概率回测 | Probabilistic Backtesting 概率回测（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2000 | 信息论过拟合检测 Information-Theoretic Overfitting Detection | 信息论过拟合检测 Information-Theoretic Overfitting Detection（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2001 | 市场状态感知Walk-Forward Regime-Aware Walk-Forward | 市场状态感知Walk-Forward Regime-Aware Walk-Forward（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2002 | 对抗性知识增强 Adversarial Knowledge Enhancement | 对抗性知识增强 Adversarial Knowledge Enhancement（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2003 | 延迟离线学习模式 Delayed Offline Learning Mode | 延迟离线学习模式 Delayed Offline Learning Mode（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2004 | A/B测试框架 A/B Testing Framework | A/B测试框架 A/B Testing Framework（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2008 | Strategy Sandbox轻量版 策略沙盒轻量版 | Strategy Sandbox轻量版 策略沙盒轻量版（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2009 | Liquidity & Slippage Simulator 流动性与滑点模拟器 | Liquidity & Slippage Simulator 流动性与滑点模拟器（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2010 | Order Matching Simulator 订单匹配模拟器 | Order Matching Simulator 订单匹配模拟器（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2011 | Scenario Generator基础版 情景生成器基础版 | Scenario Generator基础版 情景生成器基础版（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2012 | 技能三元组 Skill Triple | 技能三元组 Skill Triple（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2014 | AutoSkill自动技能发现 AutoSkill Automatic Skill Discovery | AutoSkill自动技能发现 AutoSkill Automatic Skill Discovery（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2015 | MAML快速适应 MAML Fast Adaptation | MAML快速适应 MAML Fast Adaptation（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2016 | ICL作为元学习 ICL as Meta-Learning | ICL作为元学习 ICL as Meta-Learning（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2017 | 元反思 Meta-Reflection | 元反思 Meta-Reflection（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2018 | PromptOptimizer Agent 提示词优化Agent | PromptOptimizer Agent 提示词优化Agent（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2019 | ArchitectureOptimizer Agent 架构优化Agent | ArchitectureOptimizer Agent 架构优化Agent（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2020 | CodeGenerator Agent 代码生成Agent | CodeGenerator Agent 代码生成Agent（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2021 | MethodologyLearner Agent 方法论学习Agent | MethodologyLearner Agent 方法论学习Agent（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2022 | Walk-Forward Analyzer完整版 Walk-Forward Analyzer Full Version | Walk-Forward Analyzer完整版 Walk-Forward Analyzer Full Version（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2023 | 过拟合检测扩展 Overfitting Detection Extension | 过拟合检测扩展 Overfitting Detection Extension（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2024 | Signal Confidence Scorer 信号置信度评分器 | Signal Confidence Scorer 信号置信度评分器（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2025 | 三层参数优化 3-Layer Parameter Optimization | 三层参数优化 3-Layer Parameter Optimization（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2026 | Monte Carlo Engine 蒙特卡洛引擎 | Monte Carlo Engine 蒙特卡洛引擎（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2042 | Synthetic Data Generator基础版 合成数据生成器基础版 | Synthetic Data Generator基础版 合成数据生成器基础版（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2050 | Causal SHAP 因果Shapley值 | Causal SHAP 因果Shapley值（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2051 | 因果约束反事实解释 Causal-Constrained Counterfactual Explanation | 因果约束反事实解释 Causal-Constrained Counterfactual Explanation（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2052 | 交互式解释 Interactive Explanation | 交互式解释 Interactive Explanation（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2053 | 漂移感知集成 Drift-Aware Ensemble | 漂移感知集成 Drift-Aware Ensemble（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2054 | 定时采集 Scheduled Collection | 定时采集 Scheduled Collection（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2055 | 事件触发采集 Event-Triggered Collection | 事件触发采集 Event-Triggered Collection（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2056 | 手动提交 Manual Submission | 手动提交 Manual Submission（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2057 | 格式转换 Format Conversion | 格式转换 Format Conversion（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2058 | 去重 Deduplication | 去重 Deduplication（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2059 | 去噪 Denoising | 去噪 Denoising（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2060 | 术语标准化 Terminology Normalization | 术语标准化 Terminology Normalization（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2061 | 说话人分离 Speaker Diarization | 说话人分离 Speaker Diarization（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2062 | LLM语义理解 LLM Semantic Understanding | LLM语义理解 LLM Semantic Understanding（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2063 | 知识类型分类 Knowledge Type Classification | 知识类型分类 Knowledge Type Classification（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2064 | 交易逻辑提取 Trading Logic Extraction | 交易逻辑提取 Trading Logic Extraction（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2065 | 矛盾检测 Conflict Detection | 矛盾检测 Conflict Detection（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2066 | PC算法 PC Algorithm | PC算法 PC Algorithm（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2067 | LiNGAM | LiNGAM（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2068 | 时滞因果扩展 Lagged Causal Extension | 时滞因果扩展 Lagged Causal Extension（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2075 | DeepSCM深度因果模型 DeepSCM Deep Causal Model | DeepSCM深度因果模型 DeepSCM Deep Causal Model（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2076 | ODL-Net在线深度学习 ODL-Net Online Deep Learning | ODL-Net在线深度学习 ODL-Net Online Deep Learning（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2079 | Synthetic Backtesting合成回测 Synthetic Backtesting | Synthetic Backtesting合成回测 Synthetic Backtesting（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2081 | 高级回测 Advanced Backtesting | 高级回测 Advanced Backtesting（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2082 | AlphaFin统一多模态框架 AlphaFin Unified Multimodal Framework | AlphaFin统一多模态框架 AlphaFin Unified Multimodal Framework（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2083 | FinVision端到端图表→策略 FinVision End-to-End Chart to Strategy | FinVision端到端图表→策略 FinVision End-to-End Chart to Strategy（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2084 | AlphaEvolve元级基础设施进化 AlphaEvolve Meta-Level Infrastructure Evolution | AlphaEvolve元级基础设施进化 AlphaEvolve Meta-Level Infrastructure Evolution（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2085 | 可微因果发现 Differentiable Causal Discovery NOTEARS+ | 可微因果发现 Differentiable Causal Discovery NOTEARS+（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2086 | Knowledge Effectiveness Evaluator 知识效果评估器 | Knowledge Effectiveness Evaluator 知识效果评估器（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2088 | End-to-End Causal Factor Analysis 端到端因果因子分析 | End-to-End Causal Factor Analysis 端到端因果因子分析（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2090 | Researcher Agent 研究Agent | Researcher Agent 研究Agent（来源:Agent架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2114 | Factor Proposal 因子提案 | Factor Proposal 因子提案（来源:Agent架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2115 | Strategy Code Generation 策略代码生成 | Strategy Code Generation 策略代码生成（来源:Agent架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2117 | Paper Search 论文搜索 | Paper Search 论文搜索（来源:Agent架构.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2366 | Learning System Performance Attribution 学习系统绩效归因 | Learning System Performance Attribution 学习系统绩效归因（来源:10-D-REPORTING-报告域.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2389 | Effect Feedback Path 效果反馈路径 | Effect Feedback Path 效果反馈路径（来源:10-D-REPORTING-报告域.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2565 | C-029 Model Factory 模型工厂 | C-029 Model Factory 模型工厂（来源:17-D-COMPLIANCE-合规监管域.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2566 | C-030 Decision Explainability 决策可解释性 | C-030 Decision Explainability 决策可解释性（来源:17-D-COMPLIANCE-合规监管域.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2622 | 7 Stage Learning Pipeline 7阶段学习流水线 | 7 Stage Learning Pipeline 7阶段学习流水线（来源:00-架构图总览与索引.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2623 | Module Factory Architecture 模块工厂架构 | Module Factory Architecture 模块工厂架构（来源:00-架构图总览与索引.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2624 | Knowledge Classification System 知识分类体系 | Knowledge Classification System 知识分类体系（来源:00-架构图总览与索引.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2625 | Meta Learning Ability 元学习能力定义 | Meta Learning Ability 元学习能力定义（来源:00-架构图总览与索引.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2626 | Multi Modal Knowledge Acquisition 多模态知识采集 | Multi Modal Knowledge Acquisition 多模态知识采集（来源:00-架构图总览与索引.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2627 | DSL AST Sandbox Code Generation DSL+AST沙箱安全代码生成 | DSL AST Sandbox Code Generation DSL+AST沙箱安全代码生成（来源:00-架构图总览与索引.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2628 | 4 Level Risk Control Decision Gating 4级风控决策门控 | 4 Level Risk Control Decision Gating 4级风控决策门控（来源:00-架构图总览与索引.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4870 | Module Factory 模块工厂 | Module Factory 模块工厂（来源:20-D-RESEARCH-研究基础设施域.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4871 | Agent Drift Detection Agent漂移检测 | Agent Drift Detection Agent漂移检测（来源:20-D-RESEARCH-研究基础设施域.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4872 | Cluster Behavior Protection 群集行为防护 | Cluster Behavior Protection 群集行为防护（来源:20-D-RESEARCH-研究基础设施域.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4873 | RSI Architecture RSI自进化架构 | RSI Architecture RSI自进化架构（来源:20-D-RESEARCH-研究基础设施域.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4874 | Security Governance 安全与治理 | Security Governance 安全与治理（来源:20-D-RESEARCH-研究基础设施域.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5038 | Learning System 7-Stage Pipeline 学习系统7阶段流水线 | Learning System 7-Stage Pipeline 学习系统7阶段流水线（来源:01-跨域交叉点与因果链.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5039 | Meta-Learning Capability 元学习能力 | Meta-Learning Capability 元学习能力（来源:01-跨域交叉点与因果链.md, likely_implemented） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5040 | DSL AST Sandbox DSL+AST沙箱 | DSL AST Sandbox DSL+AST沙箱（来源:01-跨域交叉点与因果链.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5041 | Multimodal Knowledge Collection 多模态知识采集 | Multimodal Knowledge Collection 多模态知识采集（来源:01-跨域交叉点与因果链.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5042 | MLOps Closed Loop MLOps闭环 | MLOps Closed Loop MLOps闭环（来源:01-跨域交叉点与因果链.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5043 | Reproducibility Pack Generator 可复现性包生成器 | Reproducibility Pack Generator 可复现性包生成器（来源:01-跨域交叉点与因果链.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5044 | Research Information Isolation 研究信息隔离 | Research Information Isolation 研究信息隔离（来源:01-跨域交叉点与因果链.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5094 | FeatureStore PIT Feature Feed FeatureStore PIT特征供给 | FeatureStore PIT Feature Feed FeatureStore PIT特征供给（来源:19-D-SIMULATION-仿真域.md, likely_new） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |

## 按四问卡点分组（为什么没开发）

> 四问过滤：q1已实现 / q2需求驱动 / q3域活着 / q4 AI替代。任一问「否」即不进 depgraph 设计态，登记在候选库。

### 待评估（188 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-AISA-001 | AI Sentiment Analyzer / AI 舆情分析器 | A股受政策和新闻影响大。这模块用AI读新闻/公告/研报打情绪分，给交易决策参考。但还在评估：是不是直接让AI运行时做就行，不用专门建模块。 | D_INTELLIGENCE | 首次登记为 candidate,待四问评估。重点评估 q4:TRAE AI 是否可替代独立模块 | 依赖 TRAE AI 运行时做舆情理解(不建模块)。代价:无固化信号产出,每次需 AI 重新分析 |
| CAND-HARVEST-0009 | Cross-Market Transmission Quantitative Model 跨市场传导量化模型 | Cross-Market Transmission Quantitative Model 跨市场传导量化模型（来源:交易决策架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0031 | AI协作策略与人机信任模型 | AI协作策略与人机信任模型（来源:交易决策架构.md, uncertain） | D_INTELLIGENCE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0032 | Auto Backtest & Simulation 自动回测与仿真 | Auto Backtest & Simulation 自动回测与仿真（来源:交易决策架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0034 | AI自治运维 | AI自治运维（来源:交易决策架构.md, uncertain） | D_INTELLIGENCE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0035 | ML模型工厂 | ML模型工厂（来源:交易决策架构.md, uncertain） | D_INTELLIGENCE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0043 | 知识模型自进化 Model Knowledge | 知识模型自进化 Model Knowledge（来源:交易决策架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0193 | Feature Store特征存储 | Feature Store特征存储（来源:交易决策架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0194 | Experiment Tracker实验追踪 | Experiment Tracker实验追踪（来源:交易决策架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0195 | Notebook Integration Notebook集成 | Notebook Integration Notebook集成（来源:交易决策架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0196 | Reproducibility Manager可复现性管理 | Reproducibility Manager可复现性管理（来源:交易决策架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0197 | Hypothesis Manager假设管理 | Hypothesis Manager假设管理（来源:交易决策架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0198 | LLM Research Agent LLM研究助手 | LLM Research Agent LLM研究助手（来源:交易决策架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0199 | Strategy Iteration Upgrader策略迭代升级 | Strategy Iteration Upgrader策略迭代升级（来源:交易决策架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0545 | Data Quality Scorer 数据质量评分器 | Data Quality Scorer 数据质量评分器（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0643 | Research Data Manager 研究数据管理器 | Research Data Manager 研究数据管理器（来源:数据架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0644 | Research Data Sandbox 研究数据沙箱 | Research Data Sandbox 研究数据沙箱（来源:数据架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0645 | Research Information Barrier 研究信息隔离 | Research Information Barrier 研究信息隔离（来源:数据架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0646 | Research Asset Versioning 研究资产版本化 | Research Asset Versioning 研究资产版本化（来源:数据架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0847 | Research Catalog 研究目录 | Research Catalog 研究目录（来源:ZephyrAlpha全系统模块清单.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0848 | Paper Tracker 论文追踪器 | Paper Tracker 论文追踪器（来源:ZephyrAlpha全系统模块清单.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0849 | Research Workflow Engine 研究工作流引擎 | Research Workflow Engine 研究工作流引擎（来源:ZephyrAlpha全系统模块清单.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0850 | Research Collaboration Hub 研究协作中心 | Research Collaboration Hub 研究协作中心（来源:ZephyrAlpha全系统模块清单.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0851 | Research Experiment Anomaly Detector 研究实验异常检测器 | Research Experiment Anomaly Detector 研究实验异常检测器（来源:ZephyrAlpha全系统模块清单.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0852 | Research Discovery Knowledge Base 研究发现知识库 | Research Discovery Knowledge Base 研究发现知识库（来源:ZephyrAlpha全系统模块清单.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0853 | Research Reproducibility Pack Generator 研究复现包生成器 | Research Reproducibility Pack Generator 研究复现包生成器（来源:ZephyrAlpha全系统模块清单.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1214 | Research Knowledge Precipitator 研究知识沉淀器 | Research Knowledge Precipitator 研究知识沉淀器（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1874 | AutoML Engine 自动ML引擎 | AutoML Engine 自动ML引擎（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1908 | Backtest-to-Production Deployer 回测到生产部署器 | Backtest-to-Production Deployer 回测到生产部署器（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1910 | S0 多模态知识采集层 S0 Multimodal Knowledge Collection Layer | S0 多模态知识采集层 S0 Multimodal Knowledge Collection Layer（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1911 | Whisper 语音转写引擎 | Whisper 语音转写引擎（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1912 | OCR 光学字符识别 | OCR 光学字符识别（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1913 | 漂移感知调度 Drift-Aware Scheduling | 漂移感知调度 Drift-Aware Scheduling（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1914 | VLM图表视觉理解 VLM Chart Visual Understanding | VLM图表视觉理解 VLM Chart Visual Understanding（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1915 | 时序基础模型骨干 TimesFM Foundation Model Backbone | 时序基础模型骨干 TimesFM Foundation Model Backbone（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1916 | S1 知识清洗与结构化层 S1 Knowledge Cleaning & Structuring Layer | S1 知识清洗与结构化层 S1 Knowledge Cleaning & Structuring Layer（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1917 | 信息价值评分 Information Value Scoring | 信息价值评分 Information Value Scoring（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1918 | S2 知识分类与策略提取层 S2 Knowledge Classification & Strategy Extraction Layer | S2 知识分类与策略提取层 S2 Knowledge Classification & Strategy Extraction Layer（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1919 | 因果发现引擎 Causal Discovery Engine | 因果发现引擎 Causal Discovery Engine（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1920 | 辩论式因子精炼 Debate-based Factor Refinement | 辩论式因子精炼 Debate-based Factor Refinement（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1921 | S3 模块映射与工厂匹配层 S3 Module Mapping & Factory Matching Layer | S3 模块映射与工厂匹配层 S3 Module Mapping & Factory Matching Layer（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1922 | S4 模块创建与接入层 S4 Module Creation & Integration Layer | S4 模块创建与接入层 S4 Module Creation & Integration Layer（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1924 | 三重语义一致性 Triple Semantic Consistency | 三重语义一致性 Triple Semantic Consistency（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1927 | S5 试运行与验证层 S5 Trial Run & Validation Layer | S5 试运行与验证层 S5 Trial Run & Validation Layer（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1928 | 参数稳定性区域 Parameter Stability Plateau | 参数稳定性区域 Parameter Stability Plateau（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1929 | 数学反思闭环 Mathematical Reflection Loop | 数学反思闭环 Mathematical Reflection Loop（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1930 | Purge Gap 清洗间隔 | Purge Gap 清洗间隔（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1931 | S6 元学习与自我进化层 S6 Meta-Learning & Self-Evolution Layer | S6 元学习与自我进化层 S6 Meta-Learning & Self-Evolution Layer（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1932 | STOP Prompt自优化 Prompt Self-Optimization | STOP Prompt自优化 Prompt Self-Optimization（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1933 | RISE 代码自纠正 Code Self-Correction | RISE 代码自纠正 Code Self-Correction（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1934 | Voyager 技能库 Skill Library | Voyager 技能库 Skill Library（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1935 | Meta-Harness 元优化器 Meta-Optimizer | Meta-Harness 元优化器 Meta-Optimizer（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1936 | 在线EWC Online Elastic Weight Consolidation | 在线EWC Online Elastic Weight Consolidation（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1937 | 轻量Agent化 Lightweight Agentification | 轻量Agent化 Lightweight Agentification（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1939 | 模块工厂 Module Factory | 模块工厂 Module Factory（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1940 | Module Registry 模块注册表 | Module Registry 模块注册表（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1944 | MLOps闭环 MLOps Closed Loop | MLOps闭环 MLOps Closed Loop（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1945 | 共形漂移检测 Conformal Drift Detection | 共形漂移检测 Conformal Drift Detection（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1946 | 多尺度漂移检测 Multi-Scale Drift Detection | 多尺度漂移检测 Multi-Scale Drift Detection（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1947 | 表示学习驱动漂移检测 Representation Learning Drift Detection | 表示学习驱动漂移检测 Representation Learning Drift Detection（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1948 | 人机协作模式 Human-AI Collaboration Mode | 人机协作模式 Human-AI Collaboration Mode（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1949 | K线分词机制 K-line Tokenization | K线分词机制 K-line Tokenization（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1951 | Sentiment Engine 情感分析引擎 | Sentiment Engine 情感分析引擎（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1952 | Filing NLP Engine 公告NLP引擎 | Filing NLP Engine 公告NLP引擎（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1953 | 多模态融合引擎 Multimodal Fusion Engine | 多模态融合引擎 Multimodal Fusion Engine（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1954 | A股特色数据 A-Share Special Data | A股特色数据 A-Share Special Data（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1955 | Trading Domain NLP Engine 交易领域NLP引擎 | Trading Domain NLP Engine 交易领域NLP引擎（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1956 | Knowledge Quality Assessor 知识质量评估器 | Knowledge Quality Assessor 知识质量评估器（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1957 | Signal Extractor 信号提取器 | Signal Extractor 信号提取器（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1958 | CausalNLP 文本因果声明提取 | CausalNLP 文本因果声明提取（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1959 | TimePC时序因果发现 TimePC Temporal Causal Discovery | TimePC时序因果发现 TimePC Temporal Causal Discovery（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1960 | Neural Granger Causality 神经Granger因果 | Neural Granger Causality 神经Granger因果（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1961 | Causal KG 因果方向标注 | Causal KG 因果方向标注（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1962 | LLM引导因果发现先验 LLM Prior Causal Discovery | LLM引导因果发现先验 LLM Prior Causal Discovery（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1963 | 带干预的时序因果发现 Intervention-Enhanced Temporal Causal Discovery | 带干预的时序因果发现 Intervention-Enhanced Temporal Causal Discovery（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1964 | 因果验证层 Causal Validation Layer | 因果验证层 Causal Validation Layer（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1965 | 因子语义去重 Factor Semantic Deduplication | 因子语义去重 Factor Semantic Deduplication（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1966 | GraphRAG图增强检索 GraphRAG Graph-Enhanced Retrieval | GraphRAG图增强检索 GraphRAG Graph-Enhanced Retrieval（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1967 | 带推理路径的KG-RAG KG-RAG with Reasoning Path | 带推理路径的KG-RAG KG-RAG with Reasoning Path（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1968 | KG引导多跳推理 KG-Guided Multi-Hop Reasoning | KG引导多跳推理 KG-Guided Multi-Hop Reasoning（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1969 | 神经符号融合推理 Neuro-Symbolic Fusion Reasoning | 神经符号融合推理 Neuro-Symbolic Fusion Reasoning（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1970 | 宏观因果传导路径 Macro Causal Transmission Path | 宏观因果传导路径 Macro Causal Transmission Path（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1971 | 创意拓宽模式 Creative Broadening Mode | 创意拓宽模式 Creative Broadening Mode（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1972 | 因果发现三阶段扩展 Causal Discovery 3-Stage Extension | 因果发现三阶段扩展 Causal Discovery 3-Stage Extension（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1973 | Causal Factor Validator 因果因子验证器 | Causal Factor Validator 因果因子验证器（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1974 | PDF预测引擎 PDF Prediction Engine | PDF预测引擎 PDF Prediction Engine（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1975 | Module Matcher 模块匹配器 | Module Matcher 模块匹配器（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1976 | 质量-多样性优化 Quality-Diversity Optimization | 质量-多样性优化 Quality-Diversity Optimization（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1977 | LLM遗传编程变异算子 LLM Genetic Programming Mutation | LLM遗传编程变异算子 LLM Genetic Programming Mutation（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1978 | Module Dependency Graph 模块依赖图 | Module Dependency Graph 模块依赖图（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1979 | Market Regime Detector 市场制度检测器 | Market Regime Detector 市场制度检测器（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1982 | 三重语义一致性约束 Triple Semantic Consistency Constraint | 三重语义一致性约束 Triple Semantic Consistency Constraint（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1983 | Generator 生成器Agent | Generator 生成器Agent（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1984 | Critic 批判器Agent | Critic 批判器Agent（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1985 | Judge 裁判Agent | Judge 裁判Agent（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1986 | 轨迹级进化 Trajectory-level Evolution | 轨迹级进化 Trajectory-level Evolution（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1988 | 可解释设计约束 Explainable By Design Constraint | 可解释设计约束 Explainable By Design Constraint（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1989 | Factor Mining Agent 因子挖掘Agent | Factor Mining Agent 因子挖掘Agent（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1990 | Hypothesis Manager 假设管理器 | Hypothesis Manager 假设管理器（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1991 | 决策树学习 Decision Tree Learning | 决策树学习 Decision Tree Learning（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1993 | SHAP值解释 SHAP Value Explanation | SHAP值解释 SHAP Value Explanation（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1994 | 决策路径可视化 Decision Path Visualization | 决策路径可视化 Decision Path Visualization（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1995 | DSR扩展 Deflated Sharpe Ratio Extension | DSR扩展 Deflated Sharpe Ratio Extension（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1996 | CPCV v2 Combinatorial Purged Cross-Validation v2 CPCV v2组合净化交叉验证v2 | CPCV v2 Combinatorial Purged Cross-Validation v2 CPCV v2组合净化交叉验证v2（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1997 | White's Reality Check 怀特现实检验 | White's Reality Check 怀特现实检验（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1998 | Adaptive Walk-Forward 自适应Walk-Forward | Adaptive Walk-Forward 自适应Walk-Forward（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1999 | Probabilistic Backtesting 概率回测 | Probabilistic Backtesting 概率回测（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2000 | 信息论过拟合检测 Information-Theoretic Overfitting Detection | 信息论过拟合检测 Information-Theoretic Overfitting Detection（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2001 | 市场状态感知Walk-Forward Regime-Aware Walk-Forward | 市场状态感知Walk-Forward Regime-Aware Walk-Forward（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2002 | 对抗性知识增强 Adversarial Knowledge Enhancement | 对抗性知识增强 Adversarial Knowledge Enhancement（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2003 | 延迟离线学习模式 Delayed Offline Learning Mode | 延迟离线学习模式 Delayed Offline Learning Mode（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2004 | A/B测试框架 A/B Testing Framework | A/B测试框架 A/B Testing Framework（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2008 | Strategy Sandbox轻量版 策略沙盒轻量版 | Strategy Sandbox轻量版 策略沙盒轻量版（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2009 | Liquidity & Slippage Simulator 流动性与滑点模拟器 | Liquidity & Slippage Simulator 流动性与滑点模拟器（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2010 | Order Matching Simulator 订单匹配模拟器 | Order Matching Simulator 订单匹配模拟器（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2011 | Scenario Generator基础版 情景生成器基础版 | Scenario Generator基础版 情景生成器基础版（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2012 | 技能三元组 Skill Triple | 技能三元组 Skill Triple（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2014 | AutoSkill自动技能发现 AutoSkill Automatic Skill Discovery | AutoSkill自动技能发现 AutoSkill Automatic Skill Discovery（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2015 | MAML快速适应 MAML Fast Adaptation | MAML快速适应 MAML Fast Adaptation（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2016 | ICL作为元学习 ICL as Meta-Learning | ICL作为元学习 ICL as Meta-Learning（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2017 | 元反思 Meta-Reflection | 元反思 Meta-Reflection（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2018 | PromptOptimizer Agent 提示词优化Agent | PromptOptimizer Agent 提示词优化Agent（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2019 | ArchitectureOptimizer Agent 架构优化Agent | ArchitectureOptimizer Agent 架构优化Agent（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2020 | CodeGenerator Agent 代码生成Agent | CodeGenerator Agent 代码生成Agent（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2021 | MethodologyLearner Agent 方法论学习Agent | MethodologyLearner Agent 方法论学习Agent（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2022 | Walk-Forward Analyzer完整版 Walk-Forward Analyzer Full Version | Walk-Forward Analyzer完整版 Walk-Forward Analyzer Full Version（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2023 | 过拟合检测扩展 Overfitting Detection Extension | 过拟合检测扩展 Overfitting Detection Extension（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2024 | Signal Confidence Scorer 信号置信度评分器 | Signal Confidence Scorer 信号置信度评分器（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2025 | 三层参数优化 3-Layer Parameter Optimization | 三层参数优化 3-Layer Parameter Optimization（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2026 | Monte Carlo Engine 蒙特卡洛引擎 | Monte Carlo Engine 蒙特卡洛引擎（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2042 | Synthetic Data Generator基础版 合成数据生成器基础版 | Synthetic Data Generator基础版 合成数据生成器基础版（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2050 | Causal SHAP 因果Shapley值 | Causal SHAP 因果Shapley值（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2051 | 因果约束反事实解释 Causal-Constrained Counterfactual Explanation | 因果约束反事实解释 Causal-Constrained Counterfactual Explanation（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2052 | 交互式解释 Interactive Explanation | 交互式解释 Interactive Explanation（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2053 | 漂移感知集成 Drift-Aware Ensemble | 漂移感知集成 Drift-Aware Ensemble（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2054 | 定时采集 Scheduled Collection | 定时采集 Scheduled Collection（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2055 | 事件触发采集 Event-Triggered Collection | 事件触发采集 Event-Triggered Collection（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2056 | 手动提交 Manual Submission | 手动提交 Manual Submission（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2057 | 格式转换 Format Conversion | 格式转换 Format Conversion（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2058 | 去重 Deduplication | 去重 Deduplication（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2059 | 去噪 Denoising | 去噪 Denoising（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2060 | 术语标准化 Terminology Normalization | 术语标准化 Terminology Normalization（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2061 | 说话人分离 Speaker Diarization | 说话人分离 Speaker Diarization（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2062 | LLM语义理解 LLM Semantic Understanding | LLM语义理解 LLM Semantic Understanding（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2063 | 知识类型分类 Knowledge Type Classification | 知识类型分类 Knowledge Type Classification（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2064 | 交易逻辑提取 Trading Logic Extraction | 交易逻辑提取 Trading Logic Extraction（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2065 | 矛盾检测 Conflict Detection | 矛盾检测 Conflict Detection（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2066 | PC算法 PC Algorithm | PC算法 PC Algorithm（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2067 | LiNGAM | LiNGAM（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2068 | 时滞因果扩展 Lagged Causal Extension | 时滞因果扩展 Lagged Causal Extension（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2075 | DeepSCM深度因果模型 DeepSCM Deep Causal Model | DeepSCM深度因果模型 DeepSCM Deep Causal Model（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2076 | ODL-Net在线深度学习 ODL-Net Online Deep Learning | ODL-Net在线深度学习 ODL-Net Online Deep Learning（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2079 | Synthetic Backtesting合成回测 Synthetic Backtesting | Synthetic Backtesting合成回测 Synthetic Backtesting（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2081 | 高级回测 Advanced Backtesting | 高级回测 Advanced Backtesting（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2082 | AlphaFin统一多模态框架 AlphaFin Unified Multimodal Framework | AlphaFin统一多模态框架 AlphaFin Unified Multimodal Framework（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2083 | FinVision端到端图表→策略 FinVision End-to-End Chart to Strategy | FinVision端到端图表→策略 FinVision End-to-End Chart to Strategy（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2084 | AlphaEvolve元级基础设施进化 AlphaEvolve Meta-Level Infrastructure Evolution | AlphaEvolve元级基础设施进化 AlphaEvolve Meta-Level Infrastructure Evolution（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2085 | 可微因果发现 Differentiable Causal Discovery NOTEARS+ | 可微因果发现 Differentiable Causal Discovery NOTEARS+（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2086 | Knowledge Effectiveness Evaluator 知识效果评估器 | Knowledge Effectiveness Evaluator 知识效果评估器（来源:学习系统架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2088 | End-to-End Causal Factor Analysis 端到端因果因子分析 | End-to-End Causal Factor Analysis 端到端因果因子分析（来源:学习系统架构.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2090 | Researcher Agent 研究Agent | Researcher Agent 研究Agent（来源:Agent架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2114 | Factor Proposal 因子提案 | Factor Proposal 因子提案（来源:Agent架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2115 | Strategy Code Generation 策略代码生成 | Strategy Code Generation 策略代码生成（来源:Agent架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2117 | Paper Search 论文搜索 | Paper Search 论文搜索（来源:Agent架构.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2366 | Learning System Performance Attribution 学习系统绩效归因 | Learning System Performance Attribution 学习系统绩效归因（来源:10-D-REPORTING-报告域.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2389 | Effect Feedback Path 效果反馈路径 | Effect Feedback Path 效果反馈路径（来源:10-D-REPORTING-报告域.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2565 | C-029 Model Factory 模型工厂 | C-029 Model Factory 模型工厂（来源:17-D-COMPLIANCE-合规监管域.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2566 | C-030 Decision Explainability 决策可解释性 | C-030 Decision Explainability 决策可解释性（来源:17-D-COMPLIANCE-合规监管域.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2622 | 7 Stage Learning Pipeline 7阶段学习流水线 | 7 Stage Learning Pipeline 7阶段学习流水线（来源:00-架构图总览与索引.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2623 | Module Factory Architecture 模块工厂架构 | Module Factory Architecture 模块工厂架构（来源:00-架构图总览与索引.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2624 | Knowledge Classification System 知识分类体系 | Knowledge Classification System 知识分类体系（来源:00-架构图总览与索引.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2625 | Meta Learning Ability 元学习能力定义 | Meta Learning Ability 元学习能力定义（来源:00-架构图总览与索引.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2626 | Multi Modal Knowledge Acquisition 多模态知识采集 | Multi Modal Knowledge Acquisition 多模态知识采集（来源:00-架构图总览与索引.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2627 | DSL AST Sandbox Code Generation DSL+AST沙箱安全代码生成 | DSL AST Sandbox Code Generation DSL+AST沙箱安全代码生成（来源:00-架构图总览与索引.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2628 | 4 Level Risk Control Decision Gating 4级风控决策门控 | 4 Level Risk Control Decision Gating 4级风控决策门控（来源:00-架构图总览与索引.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-4870 | Module Factory 模块工厂 | Module Factory 模块工厂（来源:20-D-RESEARCH-研究基础设施域.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-4871 | Agent Drift Detection Agent漂移检测 | Agent Drift Detection Agent漂移检测（来源:20-D-RESEARCH-研究基础设施域.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4872 | Cluster Behavior Protection 群集行为防护 | Cluster Behavior Protection 群集行为防护（来源:20-D-RESEARCH-研究基础设施域.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-4873 | RSI Architecture RSI自进化架构 | RSI Architecture RSI自进化架构（来源:20-D-RESEARCH-研究基础设施域.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-4874 | Security Governance 安全与治理 | Security Governance 安全与治理（来源:20-D-RESEARCH-研究基础设施域.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-5038 | Learning System 7-Stage Pipeline 学习系统7阶段流水线 | Learning System 7-Stage Pipeline 学习系统7阶段流水线（来源:01-跨域交叉点与因果链.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-5039 | Meta-Learning Capability 元学习能力 | Meta-Learning Capability 元学习能力（来源:01-跨域交叉点与因果链.md, likely_implemented） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-5040 | DSL AST Sandbox DSL+AST沙箱 | DSL AST Sandbox DSL+AST沙箱（来源:01-跨域交叉点与因果链.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-5041 | Multimodal Knowledge Collection 多模态知识采集 | Multimodal Knowledge Collection 多模态知识采集（来源:01-跨域交叉点与因果链.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-5042 | MLOps Closed Loop MLOps闭环 | MLOps Closed Loop MLOps闭环（来源:01-跨域交叉点与因果链.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-5043 | Reproducibility Pack Generator 可复现性包生成器 | Reproducibility Pack Generator 可复现性包生成器（来源:01-跨域交叉点与因果链.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-5044 | Research Information Isolation 研究信息隔离 | Research Information Isolation 研究信息隔离（来源:01-跨域交叉点与因果链.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-5094 | FeatureStore PIT Feature Feed FeatureStore PIT特征供给 | FeatureStore PIT Feature Feed FeatureStore PIT特征供给（来源:19-D-SIMULATION-仿真域.md, likely_new） | D_INTELLIGENCE | harvest待评估（likely_new） |  |

## 复查时间表

> 按 next_review_date 升序。复查时重新过四问，触发信号命中则晋升到 depgraph 设计态。

| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |
|------|------|------|------|------|------|------|
| 2026-10-31 | quarterly | CAND-AISA-001 | AI Sentiment Analyzer / AI 舆情分析器 | D_INTELLIGENCE | 候选待评（candidate） | 首次登记为 candidate,待四问评估。重点评估 q4:TRAE AI 是否可替代独立模块 |
| 2026-11-30 | quarterly | CAND-HARVEST-0009 | Cross-Market Transmission Quantitative Model 跨市场传导量化模型 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0031 | AI协作策略与人机信任模型 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0032 | Auto Backtest & Simulation 自动回测与仿真 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0034 | AI自治运维 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0035 | ML模型工厂 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0043 | 知识模型自进化 Model Knowledge | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0193 | Feature Store特征存储 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0194 | Experiment Tracker实验追踪 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0195 | Notebook Integration Notebook集成 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0196 | Reproducibility Manager可复现性管理 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0197 | Hypothesis Manager假设管理 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0198 | LLM Research Agent LLM研究助手 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0199 | Strategy Iteration Upgrader策略迭代升级 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0545 | Data Quality Scorer 数据质量评分器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0643 | Research Data Manager 研究数据管理器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0644 | Research Data Sandbox 研究数据沙箱 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0645 | Research Information Barrier 研究信息隔离 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0646 | Research Asset Versioning 研究资产版本化 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0847 | Research Catalog 研究目录 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0848 | Paper Tracker 论文追踪器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0849 | Research Workflow Engine 研究工作流引擎 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0850 | Research Collaboration Hub 研究协作中心 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0851 | Research Experiment Anomaly Detector 研究实验异常检测器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0852 | Research Discovery Knowledge Base 研究发现知识库 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0853 | Research Reproducibility Pack Generator 研究复现包生成器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1214 | Research Knowledge Precipitator 研究知识沉淀器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1874 | AutoML Engine 自动ML引擎 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1908 | Backtest-to-Production Deployer 回测到生产部署器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1910 | S0 多模态知识采集层 S0 Multimodal Knowledge Collection Layer | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1911 | Whisper 语音转写引擎 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1912 | OCR 光学字符识别 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1913 | 漂移感知调度 Drift-Aware Scheduling | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1914 | VLM图表视觉理解 VLM Chart Visual Understanding | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1915 | 时序基础模型骨干 TimesFM Foundation Model Backbone | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1916 | S1 知识清洗与结构化层 S1 Knowledge Cleaning & Structuring Layer | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1917 | 信息价值评分 Information Value Scoring | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1918 | S2 知识分类与策略提取层 S2 Knowledge Classification & Strategy Extraction Layer | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1919 | 因果发现引擎 Causal Discovery Engine | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1920 | 辩论式因子精炼 Debate-based Factor Refinement | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1921 | S3 模块映射与工厂匹配层 S3 Module Mapping & Factory Matching Layer | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1922 | S4 模块创建与接入层 S4 Module Creation & Integration Layer | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1924 | 三重语义一致性 Triple Semantic Consistency | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1927 | S5 试运行与验证层 S5 Trial Run & Validation Layer | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1928 | 参数稳定性区域 Parameter Stability Plateau | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1929 | 数学反思闭环 Mathematical Reflection Loop | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1930 | Purge Gap 清洗间隔 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1931 | S6 元学习与自我进化层 S6 Meta-Learning & Self-Evolution Layer | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1932 | STOP Prompt自优化 Prompt Self-Optimization | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1933 | RISE 代码自纠正 Code Self-Correction | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1934 | Voyager 技能库 Skill Library | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1935 | Meta-Harness 元优化器 Meta-Optimizer | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1936 | 在线EWC Online Elastic Weight Consolidation | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1937 | 轻量Agent化 Lightweight Agentification | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1939 | 模块工厂 Module Factory | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1940 | Module Registry 模块注册表 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1944 | MLOps闭环 MLOps Closed Loop | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1945 | 共形漂移检测 Conformal Drift Detection | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1946 | 多尺度漂移检测 Multi-Scale Drift Detection | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1947 | 表示学习驱动漂移检测 Representation Learning Drift Detection | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1948 | 人机协作模式 Human-AI Collaboration Mode | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1949 | K线分词机制 K-line Tokenization | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1951 | Sentiment Engine 情感分析引擎 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1952 | Filing NLP Engine 公告NLP引擎 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1953 | 多模态融合引擎 Multimodal Fusion Engine | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1954 | A股特色数据 A-Share Special Data | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1955 | Trading Domain NLP Engine 交易领域NLP引擎 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1956 | Knowledge Quality Assessor 知识质量评估器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1957 | Signal Extractor 信号提取器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1958 | CausalNLP 文本因果声明提取 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1959 | TimePC时序因果发现 TimePC Temporal Causal Discovery | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1960 | Neural Granger Causality 神经Granger因果 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1961 | Causal KG 因果方向标注 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1962 | LLM引导因果发现先验 LLM Prior Causal Discovery | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1963 | 带干预的时序因果发现 Intervention-Enhanced Temporal Causal Discovery | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1964 | 因果验证层 Causal Validation Layer | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1965 | 因子语义去重 Factor Semantic Deduplication | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1966 | GraphRAG图增强检索 GraphRAG Graph-Enhanced Retrieval | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1967 | 带推理路径的KG-RAG KG-RAG with Reasoning Path | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1968 | KG引导多跳推理 KG-Guided Multi-Hop Reasoning | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1969 | 神经符号融合推理 Neuro-Symbolic Fusion Reasoning | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1970 | 宏观因果传导路径 Macro Causal Transmission Path | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1971 | 创意拓宽模式 Creative Broadening Mode | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1972 | 因果发现三阶段扩展 Causal Discovery 3-Stage Extension | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1973 | Causal Factor Validator 因果因子验证器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1974 | PDF预测引擎 PDF Prediction Engine | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1975 | Module Matcher 模块匹配器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1976 | 质量-多样性优化 Quality-Diversity Optimization | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1977 | LLM遗传编程变异算子 LLM Genetic Programming Mutation | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1978 | Module Dependency Graph 模块依赖图 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1979 | Market Regime Detector 市场制度检测器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1982 | 三重语义一致性约束 Triple Semantic Consistency Constraint | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1983 | Generator 生成器Agent | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1984 | Critic 批判器Agent | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1985 | Judge 裁判Agent | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1986 | 轨迹级进化 Trajectory-level Evolution | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1988 | 可解释设计约束 Explainable By Design Constraint | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1989 | Factor Mining Agent 因子挖掘Agent | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1990 | Hypothesis Manager 假设管理器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1991 | 决策树学习 Decision Tree Learning | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1993 | SHAP值解释 SHAP Value Explanation | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1994 | 决策路径可视化 Decision Path Visualization | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1995 | DSR扩展 Deflated Sharpe Ratio Extension | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1996 | CPCV v2 Combinatorial Purged Cross-Validation v2 CPCV v2组合净化交叉验证v2 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1997 | White's Reality Check 怀特现实检验 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1998 | Adaptive Walk-Forward 自适应Walk-Forward | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1999 | Probabilistic Backtesting 概率回测 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2000 | 信息论过拟合检测 Information-Theoretic Overfitting Detection | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2001 | 市场状态感知Walk-Forward Regime-Aware Walk-Forward | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2002 | 对抗性知识增强 Adversarial Knowledge Enhancement | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2003 | 延迟离线学习模式 Delayed Offline Learning Mode | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2004 | A/B测试框架 A/B Testing Framework | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2008 | Strategy Sandbox轻量版 策略沙盒轻量版 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2009 | Liquidity & Slippage Simulator 流动性与滑点模拟器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2010 | Order Matching Simulator 订单匹配模拟器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2011 | Scenario Generator基础版 情景生成器基础版 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2012 | 技能三元组 Skill Triple | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2014 | AutoSkill自动技能发现 AutoSkill Automatic Skill Discovery | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2015 | MAML快速适应 MAML Fast Adaptation | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2016 | ICL作为元学习 ICL as Meta-Learning | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2017 | 元反思 Meta-Reflection | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2018 | PromptOptimizer Agent 提示词优化Agent | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2019 | ArchitectureOptimizer Agent 架构优化Agent | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2020 | CodeGenerator Agent 代码生成Agent | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2021 | MethodologyLearner Agent 方法论学习Agent | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2022 | Walk-Forward Analyzer完整版 Walk-Forward Analyzer Full Version | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2023 | 过拟合检测扩展 Overfitting Detection Extension | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2024 | Signal Confidence Scorer 信号置信度评分器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2025 | 三层参数优化 3-Layer Parameter Optimization | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2026 | Monte Carlo Engine 蒙特卡洛引擎 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2042 | Synthetic Data Generator基础版 合成数据生成器基础版 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2050 | Causal SHAP 因果Shapley值 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2051 | 因果约束反事实解释 Causal-Constrained Counterfactual Explanation | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2052 | 交互式解释 Interactive Explanation | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2053 | 漂移感知集成 Drift-Aware Ensemble | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2054 | 定时采集 Scheduled Collection | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2055 | 事件触发采集 Event-Triggered Collection | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2056 | 手动提交 Manual Submission | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2057 | 格式转换 Format Conversion | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2058 | 去重 Deduplication | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2059 | 去噪 Denoising | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2060 | 术语标准化 Terminology Normalization | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2061 | 说话人分离 Speaker Diarization | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2062 | LLM语义理解 LLM Semantic Understanding | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2063 | 知识类型分类 Knowledge Type Classification | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2064 | 交易逻辑提取 Trading Logic Extraction | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2065 | 矛盾检测 Conflict Detection | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2066 | PC算法 PC Algorithm | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2067 | LiNGAM | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2068 | 时滞因果扩展 Lagged Causal Extension | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2075 | DeepSCM深度因果模型 DeepSCM Deep Causal Model | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2076 | ODL-Net在线深度学习 ODL-Net Online Deep Learning | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2079 | Synthetic Backtesting合成回测 Synthetic Backtesting | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2081 | 高级回测 Advanced Backtesting | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2082 | AlphaFin统一多模态框架 AlphaFin Unified Multimodal Framework | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2083 | FinVision端到端图表→策略 FinVision End-to-End Chart to Strategy | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2084 | AlphaEvolve元级基础设施进化 AlphaEvolve Meta-Level Infrastructure Evolution | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2085 | 可微因果发现 Differentiable Causal Discovery NOTEARS+ | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2086 | Knowledge Effectiveness Evaluator 知识效果评估器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2088 | End-to-End Causal Factor Analysis 端到端因果因子分析 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2090 | Researcher Agent 研究Agent | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2114 | Factor Proposal 因子提案 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2115 | Strategy Code Generation 策略代码生成 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2117 | Paper Search 论文搜索 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2366 | Learning System Performance Attribution 学习系统绩效归因 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2389 | Effect Feedback Path 效果反馈路径 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2565 | C-029 Model Factory 模型工厂 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2566 | C-030 Decision Explainability 决策可解释性 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2622 | 7 Stage Learning Pipeline 7阶段学习流水线 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2623 | Module Factory Architecture 模块工厂架构 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2624 | Knowledge Classification System 知识分类体系 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2625 | Meta Learning Ability 元学习能力定义 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2626 | Multi Modal Knowledge Acquisition 多模态知识采集 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2627 | DSL AST Sandbox Code Generation DSL+AST沙箱安全代码生成 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2628 | 4 Level Risk Control Decision Gating 4级风控决策门控 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4870 | Module Factory 模块工厂 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4871 | Agent Drift Detection Agent漂移检测 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4872 | Cluster Behavior Protection 群集行为防护 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4873 | RSI Architecture RSI自进化架构 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4874 | Security Governance 安全与治理 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-5038 | Learning System 7-Stage Pipeline 学习系统7阶段流水线 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-5039 | Meta-Learning Capability 元学习能力 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-5040 | DSL AST Sandbox DSL+AST沙箱 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-5041 | Multimodal Knowledge Collection 多模态知识采集 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-5042 | MLOps Closed Loop MLOps闭环 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-5043 | Reproducibility Pack Generator 可复现性包生成器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-5044 | Research Information Isolation 研究信息隔离 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-5094 | FeatureStore PIT Feature Feed FeatureStore PIT特征供给 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
