---
doc_type: domain_architecture_doc
title: D-ALT_DATA 另类数据架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-ALT_DATA 另类数据架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 23:25:14
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-ALT_DATA |
| 域名称 | 另类数据 |
| 架构层 | L1_foundation |
| 模块总数 | 68 |
| 设计态模块 | 61 |
| 原型态模块 | 1 |
| 生产态模块 | 0 |
| 容量 | 0/150 (正常) |
| 描述 | 另类数据域。负责另类数据源的接入与处理，包括卫星图像、社交媒体情绪、供应链数据、ESG数据。 |

## 模块清单

共 68 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-ALT-DATA/3-second Contrarian Capital Flow Identification Module 3秒级逆势资金流识别模块 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/A-011 tushare账号开通 tushare Account |  | design_only | design | 0 | 0 |
| D-ALT-DATA/A-Share Capital Flow Tracker A股资金流向追踪器 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/A-Share Event Causal Reasoner A股事件因果推理引擎 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/A-Share Industry Chain Knowledge Graph A股产业链知识图谱 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/A-Share Policy Expectation Analyzer A股政策预期分析器 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/AShareCapitalFlowTracker A股资金流向追踪器 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/AShareCapitalFlowTracker A股资金流追踪器 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/AShareEventCausalReasoner A股事件因果推理器 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/ASharePolicyExpectationAnalyzer A股政策预期分析器 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/Alt-Data Compliance Reviewer 另类数据合规审查器 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/Alt-Data Lineage Tracker 另类数据血缘追踪器 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/AltDataBacktester 另类数据回测器 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/AltDataCatalog 另类数据目录 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/AltDataComplianceReviewer 另类数据合规审查器 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/AltDataConnector 另类数据连接器 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/AltDataCostOptimizer 另类数据成本优化器 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/AltDataFeed 另类数据流 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/AltDataIngested 另类数据已接入 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/AltDataLineageTracker 另类数据血缘追踪器 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/AltDataQualityDegraded 另类数据质量降级 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/AltDataQualityScorer 另类数据质量评分器 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/AltDataSignal 另类数据信号 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/Alternative Data Domain 另类数据域 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/Alternative Data Source Health & Degradation Manager 另类数据源健康度与降级管理器 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/C-014 主播信号融合 Anchor Signal Fusion |  | design_only | design | 0 | 0 |
| D-ALT-DATA/CompositeSentimentIndex CSI情绪温度指数 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/Connector 另类数据连接器(骨架) |  | design_only | design | 0 | 0 |
| D-ALT-DATA/D-ALT-DATA |  | design_only | design | 0 | 0 |
| D-ALT-DATA/Data Change Audit 数据变更审计 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/Data Fingerprint 数据指纹 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/Filing Compliance Event 合规事件 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/Filing NLP Engine 财务公告NLP引擎 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/FilingEventDetected 申报事件检测 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/FilingNLP 监管文件NLP(骨架) |  | design_only | design | 0 | 0 |
| D-ALT-DATA/FilingNLPEngine 监管文件NLP引擎 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/FilingNLPEngine 财报NLP引擎 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/GeopoliticalRiskAnalyzer 地缘政治风险分析器 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/LLM Market Interpreter LLM市场解读 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/LLMMarketInterpreter LLM市场解读器 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/LLMMarketInterpreter LLM市场解释器 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/NLP情感分析系列 NLP Sentiment Analysis Series |  | design_only | design | 0 | 0 |
| D-ALT-DATA/PolicyThemeMapper 政策主题映射器 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/Satellite & Geospatial Engine 卫星图像与地理数据引擎 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/SatelliteGeospatialEngine 卫星地理空间引擎 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/Sentiment Engine 情绪信号引擎 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/Sentiment Factor 情绪因子 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/SentimentEngine 情感引擎 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/SentimentEngine 情绪引擎(骨架) |  | design_only | design | 0 | 0 |
| D-ALT-DATA/SentimentIndexPercentile 情绪指数历史分位数 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/SentimentSignalReady 情绪信号就绪 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/SignalExtractor 信号提取器(骨架) |  | design_only | design | 0 | 0 |
| D-ALT-DATA/Supply Chain Risk Alert 供应链风险告警 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/SupplyChainDisruption 供应链中断 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/SupplyChainGraph 产业链图谱(骨架) |  | design_only | design | 0 | 0 |
| D-ALT-DATA/Training Data Bias Assessment 训练数据偏差评估 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/Whisper ASR语音识别 |  | design_only | design | 0 | 0 |
| D-ALT-DATA/tushare待开通而非立即接入 tushare Deferred |  | design_only | design | 0 | 0 |
| D-ALT-DATA/tushare新闻为新闻主力源 tushare as News Source |  | design_only | design | 0 | 0 |
| D-ALT-DATA/另类数据PIT保障 Alternative Data PIT |  | design_only | design | 0 | 0 |
| D-ALT-DATA/另类数据集成框架缺失 Alternative Data Framework Gap |  | design_only | design | 0 | 0 |
| src/zephyr/alt_data/__init__.py | MOD-ALT_DATA | orphan | prototype | 0 | 3 |
| src/zephyr/alt_data/_extensions/__init__.py | MOD-ALT_DATA | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/alt_data/api/__init__.py | MOD-ALT_DATA | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/alt_data/core/__init__.py | MOD-ALT_DATA | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/alt_data/infrastructure/__init__.py | MOD-ALT_DATA | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/alt_data/models/__init__.py | MOD-ALT_DATA | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/alt_data/services/__init__.py | MOD-ALT_DATA | orphan | scaffold_placeholder | 0 | 0 |

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-SECURITY | 10 | event,contract,config_depends,data |
| D-RISK | 10 | contract,data,event |
| D-GOVERNANCE | 10 | config_depends,data,contract,event |
| D-AUTONOMY_CORE | 9 | data,contract,config_depends |
| D-SIGNAL | 8 | data,contract,event |
| D-INTEGRATION | 5 | contract,config_depends,event |
| D-SHARED | 4 | contract,data,event |
| D-MKT_DATA | 4 | contract,data,config_depends |
| D-INTELLIGENCE | 4 | contract,data,config_depends |
| D-FACTOR | 4 | data,contract,event |
| D-DATA_ENG | 4 | domain_dependency,event,contract |
| D-INFRA_RUNTIME | 3 | data,event,contract |
| D-TRADING | 2 | event,contract |
| D-SIMULATION | 2 | contract,config_depends |
| D-REPORTING | 2 | data,contract |
| D-POSITION | 2 | contract,data |
| D-ML_SERVE | 2 | data,event |
| D-KNOWLEDGE | 2 | event,contract |
| D-PF_CORE | 1 | event |
| D-ML_TRAIN | 1 | data |
| D-EX_SOR | 1 | config_depends |
| D-AUTONOMY_PERM | 1 | data |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-COMPLIANCE | 19 | contract,data,config_depends,event |
| D-INFRA_OPS | 11 | contract,config_depends,data,event |
| D-OPS | 4 | contract,event |
| D-PF_ALLOC | 2 | event,data |
| D-FRONTEND | 1 | contract |

## 域内依赖图

详见 [d_alt_data_dependency.mmd](d_alt_data_dependency.mmd)
