---
doc_type: domain_architecture_diagram
title: D-ALT_DATA 另类数据架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 03_d_alt_data / 另类数据 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示另类数据（D-ALT_DATA）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 23:57:37
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 另类数据（D-ALT_DATA）的模块分布。共 69 个模块 / 69 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│               L2 领域层 / Domain Layer (7 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/alt_data/__init__.py  [prototype]                   │
│   src/zephyr/alt_data/_extensions/__init__.py  [scaffold_plac... │
│   src/zephyr/alt_data/api/__init__.py  [scaffold_placeholder]    │
│   src/zephyr/alt_data/core/__init__.py  [scaffold_placeholder]   │
│   src/zephyr/alt_data/infrastructure/__init__.py  [scaffold_p... │
│   src/zephyr/alt_data/models/__init__.py  [scaffold_placeholder] │
│   src/zephyr/alt_data/services/__init__.py  [scaffold_placeho... │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                未分类 / Unclassified (62 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   3-second Contrarian Capital Flow Identification Module 3秒...  │
│   A-011 tushare账号开通 tushare Account  [design]                │
│   A-Share Capital Flow Tracker A股资金流向追踪器  [design]       │
│   A-Share Event Causal Reasoner A股事件因果推理引擎  [design]    │
│   A-Share Industry Chain Knowledge Graph A股产业链知识图谱  [... │
│   A-Share Policy Expectation Analyzer A股政策预期分析器  [des... │
│   AShareCapitalFlowTracker A股资金流向追踪器  [design]           │
│   AShareCapitalFlowTracker A股资金流追踪器  [design]             │
│   AShareEventCausalReasoner A股事件因果推理器  [design]          │
│   ASharePolicyExpectationAnalyzer A股政策预期分析器  [design]    │
│   Alt-Data Compliance Reviewer 另类数据合规审查器  [design]      │
│   Alt-Data Lineage Tracker 另类数据血缘追踪器  [design]          │
│   AltDataBacktester 另类数据回测器  [design]                     │
│   AltDataCatalog 另类数据目录  [design]                          │
│   AltDataComplianceReviewer 另类数据合规审查器  [design]         │
│   AltDataConnector 另类数据连接器  [design]                      │
│   AltDataCostOptimizer 另类数据成本优化器  [design]              │
│   AltDataFeed 另类数据流  [design]                               │
│   ...还有 44 个模块 / 44 more modules                            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 69 个模块 / 69 modules）。

### L2 领域层 / Domain Layer (7 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/alt_data/__init__.py | src/zephyr/alt_data/__init__.py | prototype | orphan |
| 2 | src/zephyr/alt_data/_extensions/__init__.py | src/zephyr/alt_data/_extensions/__ini... | scaffold_placeholder | orphan |
| 3 | src/zephyr/alt_data/api/__init__.py | src/zephyr/alt_data/api/__init__.py | scaffold_placeholder | orphan |
| 4 | src/zephyr/alt_data/core/__init__.py | src/zephyr/alt_data/core/__init__.py | scaffold_placeholder | orphan |
| 5 | src/zephyr/alt_data/infrastructure/__init__.py | src/zephyr/alt_data/infrastructure/__... | scaffold_placeholder | orphan |
| 6 | src/zephyr/alt_data/models/__init__.py | src/zephyr/alt_data/models/__init__.py | scaffold_placeholder | orphan |
| 7 | src/zephyr/alt_data/services/__init__.py | src/zephyr/alt_data/services/__init__.py | scaffold_placeholder | orphan |

### 未分类 / Unclassified (62 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-ALT-DATA/3-second Contrarian Capital Flow Identificatio... | 3-second Contrarian Capital Flow Iden... | design | design_only |
| 2 | D-ALT-DATA/A-011 tushare账号开通 tushare Account | A-011 tushare账号开通 tushare Account | design | design_only |
| 3 | D-ALT-DATA/A-Share Capital Flow Tracker A股资金流向追踪器 | A-Share Capital Flow Tracker A股资金... | design | design_only |
| 4 | D-ALT-DATA/A-Share Event Causal Reasoner A股事件因果推理引擎 | A-Share Event Causal Reasoner A股事件... | design | design_only |
| 5 | D-ALT-DATA/A-Share Industry Chain Knowledge Graph A股产业... | A-Share Industry Chain Knowledge Grap... | design | design_only |
| 6 | D-ALT-DATA/A-Share Policy Expectation Analyzer A股政策预... | A-Share Policy Expectation Analyzer A... | design | design_only |
| 7 | D-ALT-DATA/AShareCapitalFlowTracker A股资金流向追踪器 | AShareCapitalFlowTracker A股资金流向... | design | design_only |
| 8 | D-ALT-DATA/AShareCapitalFlowTracker A股资金流追踪器 | AShareCapitalFlowTracker A股资金流追踪器 | design | design_only |
| 9 | D-ALT-DATA/AShareEventCausalReasoner A股事件因果推理器 | AShareEventCausalReasoner A股事件因果... | design | design_only |
| 10 | D-ALT-DATA/ASharePolicyExpectationAnalyzer A股政策预期分析器 | ASharePolicyExpectationAnalyzer A股政... | design | design_only |
| 11 | D-ALT-DATA/Alt-Data Compliance Reviewer 另类数据合规审查器 | Alt-Data Compliance Reviewer 另类数据... | design | design_only |
| 12 | D-ALT-DATA/Alt-Data Lineage Tracker 另类数据血缘追踪器 | Alt-Data Lineage Tracker 另类数据血缘... | design | design_only |
| 13 | D-ALT-DATA/AltDataBacktester 另类数据回测器 | AltDataBacktester 另类数据回测器 | design | design_only |
| 14 | D-ALT-DATA/AltDataCatalog 另类数据目录 | AltDataCatalog 另类数据目录 | design | design_only |
| 15 | D-ALT-DATA/AltDataComplianceReviewer 另类数据合规审查器 | AltDataComplianceReviewer 另类数据合... | design | design_only |
| 16 | D-ALT-DATA/AltDataConnector 另类数据连接器 | AltDataConnector 另类数据连接器 | design | design_only |
| 17 | D-ALT-DATA/AltDataCostOptimizer 另类数据成本优化器 | AltDataCostOptimizer 另类数据成本优化器 | design | design_only |
| 18 | D-ALT-DATA/AltDataFeed 另类数据流 | AltDataFeed 另类数据流 | design | design_only |
| 19 | D-ALT-DATA/AltDataIngested 另类数据已接入 | AltDataIngested 另类数据已接入 | design | design_only |
| 20 | D-ALT-DATA/AltDataLineageTracker 另类数据血缘追踪器 | AltDataLineageTracker 另类数据血缘追踪器 | design | design_only |
| 21 | D-ALT-DATA/AltDataQualityDegraded 另类数据质量降级 | AltDataQualityDegraded 另类数据质量降级 | design | design_only |
| 22 | D-ALT-DATA/AltDataQualityScorer 另类数据质量评分器 | AltDataQualityScorer 另类数据质量评分器 | design | design_only |
| 23 | D-ALT-DATA/AltDataSignal 另类数据信号 | AltDataSignal 另类数据信号 | design | design_only |
| 24 | D-ALT-DATA/Alternative Data Domain 另类数据域 | Alternative Data Domain 另类数据域 | design | design_only |
| 25 | D-ALT-DATA/Alternative Data Source Health & Degradation M... | Alternative Data Source Health & Degr... | design | design_only |
| 26 | D-ALT-DATA/C-014 主播信号融合 Anchor Signal Fusion | C-014 主播信号融合 Anchor Signal Fusion | design | design_only |
| 27 | D-ALT-DATA/CompositeSentimentIndex CSI情绪温度指数 | CompositeSentimentIndex CSI情绪温度指数 | design | design_only |
| 28 | D-ALT-DATA/Connector 另类数据连接器(骨架) | Connector 另类数据连接器(骨架) | design | design_only |
| 29 | D-ALT-DATA/D-ALT-DATA | D-ALT-DATA | design | design_only |
| 30 | D-ALT-DATA/Data Change Audit 数据变更审计 | Data Change Audit 数据变更审计 | design | design_only |
| 31 | D-ALT-DATA/Data Fingerprint 数据指纹 | Data Fingerprint 数据指纹 | design | design_only |
| 32 | D-ALT-DATA/Filing Compliance Event 合规事件 | Filing Compliance Event 合规事件 | design | design_only |
| 33 | D-ALT-DATA/Filing NLP Engine 财务公告NLP引擎 | Filing NLP Engine 财务公告NLP引擎 | design | design_only |
| 34 | D-ALT-DATA/FilingEventDetected 申报事件检测 | FilingEventDetected 申报事件检测 | design | design_only |
| 35 | D-ALT-DATA/FilingNLP 监管文件NLP(骨架) | FilingNLP 监管文件NLP(骨架) | design | design_only |
| 36 | D-ALT-DATA/FilingNLPEngine 监管文件NLP引擎 | FilingNLPEngine 监管文件NLP引擎 | design | design_only |
| 37 | D-ALT-DATA/FilingNLPEngine 财报NLP引擎 | FilingNLPEngine 财报NLP引擎 | design | design_only |
| 38 | D-ALT-DATA/GeopoliticalRiskAnalyzer 地缘政治风险分析器 | GeopoliticalRiskAnalyzer 地缘政治风险... | design | design_only |
| 39 | D-ALT-DATA/LLM Market Interpreter LLM市场解读 | LLM Market Interpreter LLM市场解读 | design | design_only |
| 40 | D-ALT-DATA/LLMMarketInterpreter LLM市场解读器 | LLMMarketInterpreter LLM市场解读器 | design | design_only |
| 41 | D-ALT-DATA/LLMMarketInterpreter LLM市场解释器 | LLMMarketInterpreter LLM市场解释器 | design | design_only |
| 42 | D-ALT-DATA/NLP情感分析系列 NLP Sentiment Analysis Series | NLP情感分析系列 NLP Sentiment Analysi... | design | design_only |
| 43 | D-ALT-DATA/PolicyThemeMapper 政策主题映射器 | PolicyThemeMapper 政策主题映射器 | design | design_only |
| 44 | D-ALT-DATA/Satellite & Geospatial Engine 卫星图像与地理数... | Satellite & Geospatial Engine 卫星图... | design | design_only |
| 45 | D-ALT-DATA/SatelliteGeospatialEngine 卫星地理空间引擎 | SatelliteGeospatialEngine 卫星地理空... | design | design_only |
| 46 | D-ALT-DATA/Sentiment Engine 情绪信号引擎 | Sentiment Engine 情绪信号引擎 | design | design_only |
| 47 | D-ALT-DATA/Sentiment Factor 情绪因子 | Sentiment Factor 情绪因子 | design | design_only |
| 48 | D-ALT-DATA/SentimentEngine 情感引擎 | SentimentEngine 情感引擎 | design | design_only |
| 49 | D-ALT-DATA/SentimentEngine 情绪引擎(骨架) | SentimentEngine 情绪引擎(骨架) | design | design_only |
| 50 | D-ALT-DATA/SentimentIndexPercentile 情绪指数历史分位数 | SentimentIndexPercentile 情绪指数历史... | design | design_only |
| 51 | D-ALT-DATA/SentimentSignalReady 情绪信号就绪 | SentimentSignalReady 情绪信号就绪 | design | design_only |
| 52 | D-ALT-DATA/SignalExtractor 信号提取器(骨架) | SignalExtractor 信号提取器(骨架) | design | design_only |
| 53 | D-ALT-DATA/Supply Chain Risk Alert 供应链风险告警 | Supply Chain Risk Alert 供应链风险告警 | design | design_only |
| 54 | D-ALT-DATA/SupplyChainDisruption 供应链中断 | SupplyChainDisruption 供应链中断 | design | design_only |
| 55 | D-ALT-DATA/SupplyChainGraph 产业链图谱(骨架) | SupplyChainGraph 产业链图谱(骨架) | design | design_only |
| 56 | D-ALT-DATA/Training Data Bias Assessment 训练数据偏差评估 | Training Data Bias Assessment 训练数... | design | design_only |
| 57 | D-ALT-DATA/Whisper ASR语音识别 | Whisper ASR语音识别 | design | design_only |
| 58 | D-ALT-DATA/tushare待开通而非立即接入 tushare Deferred | tushare待开通而非立即接入 tushare Def... | design | design_only |
| 59 | D-ALT-DATA/tushare新闻为新闻主力源 tushare as News Source | tushare新闻为新闻主力源 tushare as Ne... | design | design_only |
| 60 | D-ALT-DATA/另类数据PIT保障 Alternative Data PIT | 另类数据PIT保障 Alternative Data PIT | design | design_only |
| 61 | D-ALT-DATA/另类数据集成框架缺失 Alternative Data Framewor... | 另类数据集成框架缺失 Alternative Data... | design | design_only |
| 62 | src/zephyr/data/__init__.py | src/zephyr/data/__init__.py | production | draft |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 61 条 / 61 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│       依赖关系图 / Dependency Graph (共 61 条 / 61 edges)        │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 5                               │
│   [import_depends]: 49 条 / edges                                │
│   [event]: 6 条 / edges                                          │
│   [contract]: 3 条 / edges                                       │
│   [runtime]: 2 条 / edges                                        │
│   [config_depends]: 1 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (49 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   D-ALT-DATA → Whisper ASR语音识别                               │
│   Whisper ASR语音识别 → Sentiment Engine 情绪信号...             │
│   另类数据集成框架缺失 Alte... → AltDataBacktester 另类数...     │
│   另类数据PIT保障 Alternati... → AltDataBacktester 另类数...     │
│   Sentiment Engine 情绪信号... → Filing NLP Engine 财务公...     │
│   Filing NLP Engine 财务公... → Satellite & Geospatial En...     │
│   Satellite & Geospatial En... → LLM Market Interpreter LL...    │
│   LLM Market Interpreter LL... → Alt-Data Compliance Revie...    │
│   Alt-Data Compliance Revie... → PolicyThemeMapper 政策主...     │
│   PolicyThemeMapper 政策主... → A-Share Capital Flow Trac...     │
│   A-Share Capital Flow Trac... → A-Share Event Causal Reas...    │
│   A-Share Event Causal Reas... → C-014 主播信号融合 Anchor...    │
│   A-Share Event Causal Reas... → A-011 tushare账号开通 tus...    │
│   C-014 主播信号融合 Anchor... → AltDataConnector 另类数据...    │
│   AltDataConnector 另类数据... → FilingNLPEngine 监管文件N...    │
│   FilingNLPEngine 监管文件N... → AltDataQualityScorer 另类...    │
│   AltDataQualityScorer 另类... → AltDataCostOptimizer 另类...    │
│   AltDataCostOptimizer 另类... → AltDataBacktester 另类数...     │
│   AltDataBacktester 另类数... → AltDataCatalog 另类数据目录      │
│   AltDataCatalog 另类数据目录 → LLMMarketInterpreter LLM...      │
│   LLMMarketInterpreter LLM... → GeopoliticalRiskAnalyzer ...     │
│   GeopoliticalRiskAnalyzer ... → AltDataComplianceReviewer...    │
│   AltDataComplianceReviewer... → AShareCapitalFlowTracker ...    │
│   AShareCapitalFlowTracker ... → ASharePolicyExpectationAn...    │
│   ASharePolicyExpectationAn... → AShareEventCausalReasoner...    │
│   AShareEventCausalReasoner... → Alternative Data Source H...    │
│   Alternative Data Source H... → Alt-Data Lineage Tracker ...    │
│   Alt-Data Lineage Tracker ... → A-Share Policy Expectatio...    │
│   A-Share Policy Expectatio... → A-Share Industry Chain Kn...    │
│   A-Share Industry Chain Kn... → SentimentEngine 情感引擎        │
│   SentimentEngine 情感引擎 → FilingNLPEngine 财报NLP引擎         │
│   FilingNLPEngine 财报NLP引擎 → SatelliteGeospatialEngine...     │
│   SatelliteGeospatialEngine... → LLMMarketInterpreter LLM...     │
│   LLMMarketInterpreter LLM... → AShareCapitalFlowTracker ...     │
│   AShareCapitalFlowTracker ... → AltDataLineageTracker 另...     │
│   AShareCapitalFlowTracker ... → Alternative Data Domain ...     │
│   AltDataLineageTracker 另... → NLP情感分析系列 NLP Senti...     │
│   NLP情感分析系列 NLP Senti... → CompositeSentimentIndex C...    │
│   CompositeSentimentIndex C... → SentimentIndexPercentile ...    │
│   SentimentIndexPercentile ... → 3-second Contrarian Capit...    │
│   AltDataFeed 另类数据流 → Data Fingerprint 数据指纹             │
│   3-second Contrarian Capit... → Data Fingerprint 数据指纹       │
│   Data Fingerprint 数据指纹 → Data Change Audit 数据变...        │
│   Data Change Audit 数据变... → Training Data Bias Assess...     │
│   Training Data Bias Assess... → Connector 另类数据连接器(...    │
│   Connector 另类数据连接器(... → SentimentEngine 情绪引擎(...    │
│   SentimentEngine 情绪引擎(... → FilingNLP 监管文件NLP(骨架)     │
│   FilingNLP 监管文件NLP(骨架) → SupplyChainGraph 产业链图...     │
│   SupplyChainGraph 产业链图... → SignalExtractor 信号提取...     │
└──────────────────────────────────────────────────────────────────┘

**[event]** (6 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (3 条 / edges) — 已达显示上限，省略 / limit reached

**[runtime]** (2 条 / edges) — 已达显示上限，省略 / limit reached

**[config_depends]** (1 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 61 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `03_d_alt_data_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
