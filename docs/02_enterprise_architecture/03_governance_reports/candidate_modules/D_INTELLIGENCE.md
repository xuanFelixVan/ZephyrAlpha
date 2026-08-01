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
| CAND-HARVEST-0061 | Cross-Market Transmission Quantitative Model 跨市场传导量化模型 | C 039：跨市场传导量化模型 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0083 | AI协作策略与人机信任模型 | C 031：AI协作策略与人机信任模型（P0） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0084 | Auto Backtest & Simulation 自动回测与仿真 | C 003：自动回测与仿真 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0086 | AI自治运维 | C 008：AI自治运维 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0087 | ML模型工厂 | C 029：ML模型工厂 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0095 | 知识模型自进化 Model Knowledge | C 024：知识模型自进化 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0245 | Feature Store特征存储 | / D-RESEARCH-02 / Feature Store特征存储 / ✅ 能建 / 📋 项目内有蓝图编号MOD-L02-001部分建设 / 离线+在线特征+Point-in-Time正确性 / | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0246 | Experiment Tracker实验追踪 | / D-RESEARCH-03 / Experiment Tracker实验追踪 / ✅ 能建 / 📋 项目内有蓝图编号ML-EXPERIMENT-DOMAIN-001部分建设 / 超参/数据版本/代码commit→完整实验快照 / | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0247 | Notebook Integration Notebook集成 | / D-RESEARCH-04 / Notebook Integration Notebook集成 / ✅ 能建 / / Jupyter因子探索+可视化+papermill参数化执行 / | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0248 | Reproducibility Manager可复现性管理 | / D-RESEARCH-05 / Reproducibility Manager可复现性管理 / ✅ 能建 / / 环境快照+依赖锁定+种子管理+结果校验 / | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0249 | Hypothesis Manager假设管理 | / D-RESEARCH-08 / Hypothesis Manager假设管理 / ✅ 能建 / / 假设CRUD+证据关联+状态机(提出→验证→接受/拒绝) / | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0250 | LLM Research Agent LLM研究助手 | / D-RESEARCH-11 / LLM Research Agent LLM研究助手 / ✅ 能建 / / 规划器+工具调用+反思循环+记忆管理 / | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0251 | Strategy Iteration Upgrader策略迭代升级 | / D-RESEARCH-17 / Strategy Iteration Upgrader策略迭代升级 / ✅ 能建 / / 基于归因的权重调整+新因子挖掘+策略迭代 / | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0597 | Data Quality Scorer 数据质量评分器 | 8. Data Quality Scorer（v7.0新增，裁定✅R-74） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0694 | Research Data Manager 研究数据管理器 | / D-RESEARCH-01 / Research Data Manager / 数据集版本化(Git-like)+血缘追踪+质量评分+搜索发现+访问控制+生命周期管理 / ✅能建。与§9数据血缘+§10数据质量对齐，增量：增加研究数据沙 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0695 | Research Data Sandbox 研究数据沙箱 | 隔离研究环境+数据隔离+代码隔离+资源隔离 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0696 | Research Information Barrier 研究信息隔离 | 研究信息隔离+跨墙审批+信息访问控制(中国墙/MNPI管理) | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0697 | Research Asset Versioning 研究资产版本化 | 研究资产(因子/模型/策略)的版本化管理与跨项目复用 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0878 | Research Catalog 研究目录 | 研究目录搜索引擎/标签系统/引用图谱/推荐器/访问控制 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0879 | Paper Tracker 论文追踪器 | 论文追踪爬取器+去重+摘要生成+引用分析+趋势检测 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0880 | Research Workflow Engine 研究工作流引擎 | 研究工作流引擎DAG编排器+任务调度+依赖管理+重试+并行+通知 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0881 | Research Collaboration Hub 研究协作中心 | 研究协作中心讨论区+评审系统+知识库+权限管理+活动流 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0882 | Research Experiment Anomaly Detector 研究实验异常检测器 | 研究实验异常检测器实验异常检测+异常分类+异常响应+实验暂停 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0883 | Research Discovery Knowledge Base 研究发现知识库 | 研究发现知识库研究发现沉淀+知识抽取+知识关联+知识检索 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0884 | Research Reproducibility Pack Generator 研究复现包生成器 | 研究复现包生成器一键复现包+环境锁定+依赖锁定+代码快照 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1237 | Research Knowledge Precipitator 研究知识沉淀器 | 研究结论自动沉淀:实验结果+研究笔记→结构化知识自动归档 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1896 | AutoML Engine 自动ML引擎 | Optuna自动超参搜索+模型选择(随机森林/XGBoost/LightGBM) | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1929 | Backtest-to-Production Deployer 回测到生产部署器 | 回测→生产部署必须经过门控验证+灰度发布+回滚 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1931 | S0 多模态知识采集层 S0 Multimodal Knowledge Collection Layer | > **v8.0 统一架构**：7阶段流水线+横切层+安全约束合并为唯一真源。v4.0升级：S0新增漂移感知+VLM+PIT门控+基础模型骨干；S1新增信息价值评分；S2新增因果发现引擎(PC+LiNGAM)+辩论式因子精炼+10类知识（v | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1932 | Whisper 语音转写引擎 | 语音/视频采集用Whisper转写 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1933 | OCR 光学字符识别 | 视频采集用Whisper+OCR | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1934 | 漂移感知调度 Drift-Aware Scheduling | 定时抓取+事件触发+手动提交+漂移感知调度(ADWIN/DDM) | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1935 | VLM图表视觉理解 VLM Chart Visual Understanding | VLM解析K线图/技术图表→结构化信号描述 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1936 | 时序基础模型骨干 TimesFM Foundation Model Backbone | ║  │  🆕VLM图表视觉理解 + 🆕Point-in-Time门控 + 🆕时序基础模型骨干(TimesFM)  │  ║ | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1937 | S1 知识清洗与结构化层 S1 Knowledge Cleaning & Structuring Layer | 去重+去噪+时间戳对齐+说话人分离+术语标准化 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1938 | 信息价值评分 Information Value Scoring | 相关性/时效性/信息量/可靠性多维度评分 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1939 | S2 知识分类与策略提取层 S2 Knowledge Classification & Strategy Extraction Layer | LLM语义理解→知识类型分类(11类)→交易逻辑提取 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1940 | 因果发现引擎 Causal Discovery Engine | PC算法→LiNGAM→时滞因果图→LLM语义校验 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1941 | 辩论式因子精炼 Debate-based Factor Refinement | ║  │  🆕辩论式因子精炼: Generator(GLM-5.1)⇄Critic(DeepSeek)→IC显著提升        │  ║ | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1942 | S3 模块映射与工厂匹配层 S3 Module Mapping & Factory Matching Layer | 分类知识包→目标层级映射→模块工厂查询 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1943 | S4 模块创建与接入层 S4 Module Creation & Integration Layer | 模块需求规格→DSL约束→AST沙箱→人工审核 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1945 | 三重语义一致性 Triple Semantic Consistency | 假设⇄因子表达式⇄代码三者必须语义一致 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1948 | S5 试运行与验证层 S5 Trial Run & Validation Layer | 新模块→C-003完整回测验证→模拟盘观察→效果评估 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1949 | 参数稳定性区域 Parameter Stability Plateau | 参数扫描→识别稳定高原→选高原中心→避悬崖型参数 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1950 | 数学反思闭环 Mathematical Reflection Loop | 反馈→形式化为约束优化→精确求解替代LLM直觉 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1951 | Purge Gap 清洗间隔 | 训练集→Gap期(≥5交易日)→测试集防信息泄漏 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1952 | S6 元学习与自我进化层 S6 Meta-Learning & Self-Evolution Layer | ║  │  S6  元学习与自我进化层                                                   │  ║ | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1953 | STOP Prompt自优化 Prompt Self-Optimization | ║  │  🆕RSI架构: STOP(Prompt自优化) + RISE(代码自纠正) + Voyager(技能库) + Meta-Harness(元优化器) │  ║ | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1954 | RISE 代码自纠正 Code Self-Correction | 模块代码运行异常→LLM自动定位+修正→人工审核 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1955 | Voyager 技能库 Skill Library | 成功代码/模板/公式→结构化存储→新任务优先检索复用 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1956 | Meta-Harness 元优化器 Meta-Optimizer | 优化学习系统自身的超参数:变异率/匹配阈值/审核策略 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1957 | 在线EWC Online Elastic Weight Consolidation | Fisher信息正则化→防灾难性遗忘→保留历史+适应新知 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1958 | 轻量Agent化 Lightweight Agentification | 4维度→4个逻辑Agent+消息队列协调(非物理分布式) | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1960 | 模块工厂 Module Factory | 交易模块池的全生命周期管理:注册/查询/版本/依赖/退役 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1961 | Module Registry 模块注册表 | 因子/信号/策略/风控/模型/功能模块的注册信息 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1965 | MLOps闭环 MLOps Closed Loop | 监控效果→漂移检测→自动重训练→影子验证→金丝雀上线 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1966 | 共形漂移检测 Conformal Drift Detection | 基于共形推断的漂移检测提供统计保证的误报率控制 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1967 | 多尺度漂移检测 Multi-Scale Drift Detection | 微观漂移/中观漂移/宏观漂移三级漂移检测与分级响应 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1968 | 表示学习驱动漂移检测 Representation Learning Drift Detection | hook机制提取模型中间层表示仅用于漂移检测预警 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1969 | 人机协作模式 Human-AI Collaboration Mode | AI自动采集+提取→人类PM审核+补充→AI继续映射 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1970 | K线分词机制 K-line Tokenization | 将K线序列视为金融语言进行分词和自回归预训练 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1972 | Sentiment Engine 情感分析引擎 | finBERT金融情感分析+vaderSentiment规则情感分析双引擎 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1973 | Filing NLP Engine 公告NLP引擎 | 公告文本结构化提取:标题/摘要/关键数据/事件类型 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1974 | 多模态融合引擎 Multimodal Fusion Engine | 早期融合+晚期融合+注意力融合多模态特征 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1975 | A股特色数据 A-Share Special Data | 五类资金追踪+政策预期量化(❌裁定需付费数据源) | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1976 | Trading Domain NLP Engine 交易领域NLP引擎 | 交易领域术语识别+意图解析+领域实体提取 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1977 | Knowledge Quality Assessor 知识质量评估器 | 知识质量4维评估:过时检测+冲突检测+可信度+新鲜度 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1978 | Signal Extractor 信号提取器 | 特征工程+IC测试+信号衰减分析+正交化去冗 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1979 | CausalNLP 文本因果声明提取 | 从文本中提取显式/隐式因果声明 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1980 | TimePC时序因果发现 TimePC Temporal Causal Discovery | 在PC算法基础上增加时序约束专门处理金融时序数据 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1981 | Neural Granger Causality 神经Granger因果 | │   │   ├─ Neural Granger Causality（v5.0新增，ICML 2025） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1982 | Causal KG 因果方向标注 | 在知识图谱的边上标注因果方向(A→B/A←B/A↔B) | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1983 | LLM引导因果发现先验 LLM Prior Causal Discovery | LLM生成因果边白名单/黑名单→约束PC算法搜索空间 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1984 | 带干预的时序因果发现 Intervention-Enhanced Temporal Causal Discovery | 检测政策事件窗口→分别估计前后因果图→比较差异 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1985 | 因果验证层 Causal Validation Layer | 检查是否存在自然实验/工具变量支持→无支持降权 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1986 | 因子语义去重 Factor Semantic Deduplication | LLM判断两个因子的经济学逻辑是否等价 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1987 | GraphRAG图增强检索 GraphRAG Graph-Enhanced Retrieval | 先构建/查询知识图谱子图基于子图上下文进行LLM提取 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1988 | 带推理路径的KG-RAG KG-RAG with Reasoning Path | GraphRAG的演进增强版增加因果图推理路径引导 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1989 | KG引导多跳推理 KG-Guided Multi-Hop Reasoning | 复杂问题→KG检索相关子图→LLM基于子图推理 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1990 | 神经符号融合推理 Neuro-Symbolic Fusion Reasoning | LLM提取(神经)+规则验证(符号)→融合推理 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1991 | 宏观因果传导路径 Macro Causal Transmission Path | 宏观经济指标作为因果图的内在节点显式追踪传导路径 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1992 | 创意拓宽模式 Creative Broadening Mode | LLM一次生成10+假设→快速预评估→仅高潜力假设进入深度提取 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1993 | 因果发现三阶段扩展 Causal Discovery 3-Stage Extension | 工具变量法+Do-calculus+反事实推理 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1994 | Causal Factor Validator 因果因子验证器 | DoWhy因果效应验证+反驳测试 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1995 | PDF预测引擎 PDF Prediction Engine | PDF文档结构化解析→预测模型输入→策略信号生成(❌) | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1996 | Module Matcher 模块匹配器 | │  │  Module Matcher (模块匹配器)                               │   │ | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1997 | 质量-多样性优化 Quality-Diversity Optimization | 维护策略特征图不寻找单一最优策略维护多样化高性能策略集合 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1998 | LLM遗传编程变异算子 LLM Genetic Programming Mutation | LLM作为遗传编程的变异算子替代随机变异 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1999 | Module Dependency Graph 模块依赖图 | 新模块接入前检查依赖/产出/冲突/循环依赖 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2000 | Market Regime Detector 市场制度检测器 | hmmlearn HMM市场制度检测+12种Regime分类 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2003 | 三重语义一致性约束 Triple Semantic Consistency Constraint | 假设→因子表达式→可执行代码三者必须语义一致 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2004 | Generator 生成器Agent | GLM-5.1生成模块代码/因子假设 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2005 | Critic 批判器Agent | DeepSeek V4 Pro审查代码识别逻辑漏洞/过拟合风险 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2006 | Judge 裁判Agent | Claude综合评估→通过AST沙箱→人工审核 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2007 | 轨迹级进化 Trajectory-level Evolution | 每次知识→模块映射视为一条研究轨迹进化时定位次优步骤 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2008 | 可解释设计约束 Explainable By Design Constraint | 可解释设计约束（v5.0新增，Explainable By Design JFML 2025）: | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2009 | Factor Mining Agent 因子挖掘Agent | LLM并发因子假设生成+去重+回测验证 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2010 | Hypothesis Manager 假设管理器 | 假设CRUD+证据关联+状态机(提出→验证→已验证→已推翻) | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2011 | 决策树学习 Decision Tree Learning | **核心逻辑**: 23节点决策流程是人为设定的固定决策树，不适应市场状态变化。专业机构用**Decision Tree Learning**从数据中自动学习决策规则，或用**Reinforcement Learning**端到端优化交易策 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2013 | SHAP值解释 SHAP Value Explanation | 每个交易决策必须可解释。用SHAP值解释模型决策。人工干预接口保留在关键节点。 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2014 | 决策路径可视化 Decision Path Visualization | 决策树的路径可视化理解模型为什么做出某个决策 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2015 | DSR扩展 Deflated Sharpe Ratio Extension | Deflated Sharpe Ratio考虑策略间相关性调整多重检验阈值 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2016 | CPCV v2 Combinatorial Purged Cross-Validation v2 CPCV v2组合净化交叉验证v2 | Combinatorial Purged Cross-Validation扩展版支持非IID数据 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2017 | White's Reality Check 怀特现实检验 | 过拟合检测统计功效提升30%改进bootstrap重采样方法 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2018 | Adaptive Walk-Forward 自适应Walk-Forward | 自适应窗口步进:根据市场波动率动态调整训练/测试窗口长度 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2019 | Probabilistic Backtesting 概率回测 | 贝叶斯回测:输出策略性能的后验分布而非点估计 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2020 | 信息论过拟合检测 Information-Theoretic Overfitting Detection | 互信息/KL散度量化训练集vs测试集信息增益差异 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2021 | 市场状态感知Walk-Forward Regime-Aware Walk-Forward | └─ 市场状态感知Walk-Forward（v6.0新增，Regime-Aware Walk-Forward 2025-2026） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2022 | 对抗性知识增强 Adversarial Knowledge Enhancement | 在特征空间注入扰动进行对抗训练测试模块对分布漂移的鲁棒性 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2023 | 延迟离线学习模式 Delayed Offline Learning Mode | 新知识先记录→离线训练→验证通过→才进入试运行 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2024 | A/B测试框架 A/B Testing Framework | 新模块与旧模块并行运行(影子部署)统计比较效果 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2028 | Strategy Sandbox轻量版 策略沙盒轻量版 | 15. Strategy Sandbox轻量版（v8.0新增，裁定✅R-117） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2029 | Liquidity & Slippage Simulator 流动性与滑点模拟器 | Almgren-Chriss市场冲击模型+滑点模拟 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2030 | Order Matching Simulator 订单匹配模拟器 | 限价订单簿模拟:买卖五档挂单+撮合引擎 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2031 | Scenario Generator基础版 情景生成器基础版 | 历史数据重采样+自定义情景生成(CPU版) | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2032 | 技能三元组 Skill Triple | 每个技能存储为(条件动作效果)三元组使技能检索更精确 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2034 | AutoSkill自动技能发现 AutoSkill Automatic Skill Discovery | LLM分析成功/失败的研究轨迹→自动抽象为新技能 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2035 | MAML快速适应 MAML Fast Adaptation | MAML(Model-Agnostic Meta-Learning)变体新市场5-10 episode适应 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2036 | ICL作为元学习 ICL as Meta-Learning | └─ v6.0增强: ICL作为元学习替代方案（精心设计prompt含历史成功/失败案例→LLM上下文中适应新市场→无需显式元训练→与维度5 MAML互补：小样本用ICL，大样本用MAML） | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2037 | 元反思 Meta-Reflection | 经验回放+反思提炼+技能注册+元反思四步闭环 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2038 | PromptOptimizer Agent 提示词优化Agent | 负责维度1学习如何学习Prompt自优化循环 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2039 | ArchitectureOptimizer Agent 架构优化Agent | 负责维度2学习架构优化代码自纠正循环 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2040 | CodeGenerator Agent 代码生成Agent | 负责维度3学习代码生成技能库积累 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2041 | MethodologyLearner Agent 方法论学习Agent | 负责维度4学习方法论元优化器优化自身超参 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2042 | Walk-Forward Analyzer完整版 Walk-Forward Analyzer Full Version | 滚动Walk-Forward+锚定Walk-Forward+扩展Walk-Forward | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2043 | 过拟合检测扩展 Overfitting Detection Extension | Bonferroni校正+FDR(Benjamini-Hochberg)+BHY多重检验校正 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2044 | Signal Confidence Scorer 信号置信度评分器 | Platt Scaling+Isotonic Regression概率校准+MC Dropout不确定性 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2045 | 三层参数优化 3-Layer Parameter Optimization | 实时微调+周期优化+结构进化三层参数优化 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2046 | Monte Carlo Engine 蒙特卡洛引擎 | GPU加速蒙特卡洛模拟:策略风险分布估计+压力测试(❌) | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2062 | Synthetic Data Generator基础版 合成数据生成器基础版 | SMOTE过采样+轻量GAN生成稀有市场条件数据 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2070 | Causal SHAP 因果Shapley值 | 基于因果图计算Shapley值区分真因果与伪相关 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2071 | 因果约束反事实解释 Causal-Constrained Counterfactual Explanation | 因果图约束反事实生成空间→确保反事实场景因果合理 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2072 | 交互式解释 Interactive Explanation | LLM+SHAP/因果图RAG问答→审批者可追问AI决策理由 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2073 | 漂移感知集成 Drift-Aware Ensemble | 根据各模型漂移适应能力动态调整集成权重 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2074 | 定时采集 Scheduled Collection | 每日固定时间抓取指定直播/专栏盘后集中采集当日分析师内容 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2075 | 事件触发采集 Event-Triggered Collection | 重大政策发布/市场异动/新研报发布触发紧急解读采集 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2076 | 手动提交 Manual Submission | 用户粘贴文字/上传PDF音频视频/提交网址链接 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2077 | 格式转换 Format Conversion | 音频视频Whisper转写+PDF文本提取+网址正文提取+文字直接通过 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2078 | 去重 Deduplication | 精确去重(内容哈希)+近似去重(SimHash/MinHash)+跨源去重 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2079 | 去噪 Denoising | 口语化填充词去除+重复语句合并+无关内容裁剪+时间戳对齐 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2080 | 术语标准化 Terminology Normalization | 口语→标准术语+股票代码标准化+板块名称标准化 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2081 | 说话人分离 Speaker Diarization | 5. 说话人分离 (Speaker Diarization) — 仅语音/视频 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2082 | LLM语义理解 LLM Semantic Understanding | 理解文本交易含义+识别隐含交易逻辑+文本因果声明提取 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2083 | 知识类型分类 Knowledge Type Classification | 规则+LLM混合分类策略/因子/市场状态等多标签分类 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2084 | 交易逻辑提取 Trading Logic Extraction | 按知识类型使用不同提取模板输出结构化交易逻辑 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2085 | 矛盾检测 Conflict Detection | 语义相似度+逻辑冲突检测一致增强/矛盾标记/新增 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2086 | PC算法 PC Algorithm | causal-learn从因子数据中自动发现因果骨架无向边 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2087 | LiNGAM | causal-learn确定因果方向输出有向因果边A→B | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2088 | 时滞因果扩展 Lagged Causal Extension | 因果边从即时→时滞支持X滞后k期影响Y的时滞因果关系 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2095 | DeepSCM深度因果模型 DeepSCM Deep Causal Model | / R-37 / DeepSCM深度因果模型 / ❌ / 硬边界约束二（单机Windows+Python，深度因果模型需GPU集群训练） / GPU集群+Linux+PyTorch分布式训练就绪 / | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2096 | ODL-Net在线深度学习 ODL-Net Online Deep Learning | / R-38 / ODL-Net在线深度学习 / ❌ / 硬边界约束二（在线深度学习需GPU集群） / GPU集群+在线训练框架就绪 / | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2099 | Synthetic Backtesting合成回测 Synthetic Backtesting | / R-41 / Synthetic Backtesting合成回测 / ❌ / 硬边界约束二（生成模型需GPU集群） / GPU集群+扩散模型/GAN训练框架就绪 / | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2101 | 高级回测 Advanced Backtesting | / R-48 / 高级回测(DSR+CPCV v2+White's Reality Check+Adaptive Walk-Forward+Probabilistic Backtesting) / ✅ / 统计检验+贝叶斯回测，纯Pytho | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2102 | AlphaFin统一多模态框架 AlphaFin Unified Multimodal Framework | / R-64 / AlphaFin统一多模态框架 / ❌ / 硬边界约束二（统一多模态模型需GPU集群） / 统一多模态模型量化部署方案就绪+RTX 3090 24GB显存验证通过 / | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2103 | FinVision端到端图表→策略 FinVision End-to-End Chart to Strategy | / R-65 / FinVision端到端图表→策略 / ❌ / 硬边界约束三（端到端生成绕过DSL+AST沙箱安全约束） / 端到端生成不绕过DSL+AST沙箱的安全方案设计完成 / | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2104 | AlphaEvolve元级基础设施进化 AlphaEvolve Meta-Level Infrastructure Evolution | / R-66 / AlphaEvolve元级基础设施进化 / ❌ / 硬边界约束三（DSL语法进化可能破坏AST沙箱安全约束） / DSL语法进化不破坏AST沙箱安全约束的验证方案就绪 / | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2105 | 可微因果发现 Differentiable Causal Discovery NOTEARS+ | / R-67 / 可微因果发现(NOTEARS+) / ❌ / 硬边界约束二（连续优化需GPU长时间训练） / RTX 3090上<100变量训练时间<4h验证通过 / | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2106 | Knowledge Effectiveness Evaluator 知识效果评估器 | §11.2效果反馈接口接收C-010数据评估注入知识是否有效 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2108 | End-to-End Causal Factor Analysis 端到端因果因子分析 | / **端到端因果因子分析**：从因果发现到因果情景建模的完整管线，应用于因子投资 / Toward Automating Causal Discovery (World Scientific 2025) / 因子知识仅做IC验证，无因果验 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2110 | Researcher Agent 研究Agent | 战略层研究Agent策略研究因子发现 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2134 | Factor Proposal 因子提案 | 研究Agent技能因子提案ACTIVE | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2135 | Strategy Code Generation 策略代码生成 | 研究Agent技能策略代码生成ACTIVE | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2137 | Paper Search 论文搜索 | 研究Agent技能论文搜索ACTIVE | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2386 | Learning System Performance Attribution 学习系统绩效归因 | 学习系统绩效归因3功能点收益归因Brinson模型到因子归因到风险归因来源A8 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2409 | Effect Feedback Path 效果反馈路径 | 效果反馈路径2路径C-010归因报告到学习系统知识效果评估CTR-P1-009每日+C-033过拟合检测到学习系统过拟合标记归因报告每周 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2585 | C-029 Model Factory 模型工厂 | 模型工厂训练数据审计+漂移检测 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2586 | C-030 Decision Explainability 决策可解释性 | 决策可解释性AI决策过程日志 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2642 | 7 Stage Learning Pipeline 7阶段学习流水线 | S0~S6七阶段学习流水线 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2643 | Module Factory Architecture 模块工厂架构 | 模块工厂架构与模块生命周期核心独创 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2644 | Knowledge Classification System 知识分类体系 | 11类知识分类+因果发现引擎+辩论式因子精炼 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2645 | Meta Learning Ability 元学习能力定义 | / 元学习能力定义与学习策略（RSI架构4维度+技能库+在线EWC+MAML+AutoSkill） / 风险约束（→A4） / | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2646 | Multi Modal Knowledge Acquisition 多模态知识采集 | / 多模态知识采集（Whisper/VLM/PDF/爬虫+漂移感知调度+PIT门控） / Agent内部架构（→A7） / | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2647 | DSL AST Sandbox Code Generation DSL+AST沙箱安全代码生成 | 进化式代码生成+三重语义一致性 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2648 | 4 Level Risk Control Decision Gating 4级风控决策门控 | / 4级风控决策门控（APPROVE/REDUCE/REJECT/FLATTEN）+可解释性门控（SHAP/LIME/Causal SHAP） / / | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4871 | Module Factory 模块工厂 | 交易模块池全生命周期管理注册查询版本依赖退役 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4872 | Agent Drift Detection Agent漂移检测 | KL散度大于阈值自动降级为仅建议模式 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4873 | Cluster Behavior Protection 群集行为防护 | 与行业模型相关性>0.7自动差异化+市场压力时降仓 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4874 | RSI Architecture RSI自进化架构 | ║  │  🆕RSI架构: STOP(Prompt自优化) + RISE(代码自纠正) + Voyager(技能库) + Meta-Harness(元优化器) │  ║ | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4875 | Security Governance 安全与治理 | 知识来源追溯+模块变更审计+自动操作日志+人工审批 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5038 | Learning System 7-Stage Pipeline 学习系统7阶段流水线 | / — / 学习系统7阶段流水线 / S0感知→S1采集→S2映射→S3验证→S4注入→S5反馈→S6进化 / ✅ / | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5039 | Meta-Learning Capability 元学习能力 | / — / 元学习能力 / RSI架构4维度+技能库+在线EWC+MAML+AutoSkill / ✅ / | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5040 | DSL AST Sandbox DSL+AST沙箱 | 安全代码生成+进化式代码生成+三重语义一致性 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5041 | Multimodal Knowledge Collection 多模态知识采集 | / — / 多模态知识采集 / Whisper/VLM/PDF/爬虫+漂移感知调度+PIT门控 / ✅ / | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5042 | MLOps Closed Loop MLOps闭环 | 模型版本管理/实验追踪/自动重训练/模型注册/部署管道 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5043 | Reproducibility Pack Generator 可复现性包生成器 | 实验环境+数据+代码打包+版本锁定 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5044 | Research Information Isolation 研究信息隔离 | 研究域与交易域信息隔离+合规约束 | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5094 | FeatureStore PIT Feature Feed FeatureStore PIT特征供给 | / SIM-RES-01 / D-RESEARCH→SIM / — / D-RESEARCH / FeatureStore PIT特征→回测数据输入 / P1 / | D_INTELLIGENCE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |

## 按四问卡点分组（为什么没开发）

> 四问过滤：q1已实现 / q2需求驱动 / q3域活着 / q4 AI替代。任一问「否」即不进 depgraph 设计态，登记在候选库。

### 待评估（188 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-AISA-001 | AI Sentiment Analyzer / AI 舆情分析器 | A股受政策和新闻影响大。这模块用AI读新闻/公告/研报打情绪分，给交易决策参考。但还在评估：是不是直接让AI运行时做就行，不用专门建模块。 | D_INTELLIGENCE | 首次登记为 candidate,待四问评估。重点评估 q4:TRAE AI 是否可替代独立模块 | 依赖 TRAE AI 运行时做舆情理解(不建模块)。代价:无固化信号产出,每次需 AI 重新分析 |
| CAND-HARVEST-0061 | Cross-Market Transmission Quantitative Model 跨市场传导量化模型 | C 039：跨市场传导量化模型 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0083 | AI协作策略与人机信任模型 | C 031：AI协作策略与人机信任模型（P0） | D_INTELLIGENCE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0084 | Auto Backtest & Simulation 自动回测与仿真 | C 003：自动回测与仿真 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0086 | AI自治运维 | C 008：AI自治运维 | D_INTELLIGENCE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0087 | ML模型工厂 | C 029：ML模型工厂 | D_INTELLIGENCE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0095 | 知识模型自进化 Model Knowledge | C 024：知识模型自进化 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0245 | Feature Store特征存储 | / D-RESEARCH-02 / Feature Store特征存储 / ✅ 能建 / 📋 项目内有蓝图编号MOD-L02-001部分建设 / 离线+在线特征+Point-in-Time正确性 / | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0246 | Experiment Tracker实验追踪 | / D-RESEARCH-03 / Experiment Tracker实验追踪 / ✅ 能建 / 📋 项目内有蓝图编号ML-EXPERIMENT-DOMAIN-001部分建设 / 超参/数据版本/代码commit→完整实验快照 / | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0247 | Notebook Integration Notebook集成 | / D-RESEARCH-04 / Notebook Integration Notebook集成 / ✅ 能建 / / Jupyter因子探索+可视化+papermill参数化执行 / | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0248 | Reproducibility Manager可复现性管理 | / D-RESEARCH-05 / Reproducibility Manager可复现性管理 / ✅ 能建 / / 环境快照+依赖锁定+种子管理+结果校验 / | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0249 | Hypothesis Manager假设管理 | / D-RESEARCH-08 / Hypothesis Manager假设管理 / ✅ 能建 / / 假设CRUD+证据关联+状态机(提出→验证→接受/拒绝) / | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0250 | LLM Research Agent LLM研究助手 | / D-RESEARCH-11 / LLM Research Agent LLM研究助手 / ✅ 能建 / / 规划器+工具调用+反思循环+记忆管理 / | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0251 | Strategy Iteration Upgrader策略迭代升级 | / D-RESEARCH-17 / Strategy Iteration Upgrader策略迭代升级 / ✅ 能建 / / 基于归因的权重调整+新因子挖掘+策略迭代 / | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0597 | Data Quality Scorer 数据质量评分器 | 8. Data Quality Scorer（v7.0新增，裁定✅R-74） | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0694 | Research Data Manager 研究数据管理器 | / D-RESEARCH-01 / Research Data Manager / 数据集版本化(Git-like)+血缘追踪+质量评分+搜索发现+访问控制+生命周期管理 / ✅能建。与§9数据血缘+§10数据质量对齐，增量：增加研究数据沙 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0695 | Research Data Sandbox 研究数据沙箱 | 隔离研究环境+数据隔离+代码隔离+资源隔离 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0696 | Research Information Barrier 研究信息隔离 | 研究信息隔离+跨墙审批+信息访问控制(中国墙/MNPI管理) | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0697 | Research Asset Versioning 研究资产版本化 | 研究资产(因子/模型/策略)的版本化管理与跨项目复用 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0878 | Research Catalog 研究目录 | 研究目录搜索引擎/标签系统/引用图谱/推荐器/访问控制 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0879 | Paper Tracker 论文追踪器 | 论文追踪爬取器+去重+摘要生成+引用分析+趋势检测 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0880 | Research Workflow Engine 研究工作流引擎 | 研究工作流引擎DAG编排器+任务调度+依赖管理+重试+并行+通知 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0881 | Research Collaboration Hub 研究协作中心 | 研究协作中心讨论区+评审系统+知识库+权限管理+活动流 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0882 | Research Experiment Anomaly Detector 研究实验异常检测器 | 研究实验异常检测器实验异常检测+异常分类+异常响应+实验暂停 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0883 | Research Discovery Knowledge Base 研究发现知识库 | 研究发现知识库研究发现沉淀+知识抽取+知识关联+知识检索 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0884 | Research Reproducibility Pack Generator 研究复现包生成器 | 研究复现包生成器一键复现包+环境锁定+依赖锁定+代码快照 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1237 | Research Knowledge Precipitator 研究知识沉淀器 | 研究结论自动沉淀:实验结果+研究笔记→结构化知识自动归档 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1896 | AutoML Engine 自动ML引擎 | Optuna自动超参搜索+模型选择(随机森林/XGBoost/LightGBM) | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1929 | Backtest-to-Production Deployer 回测到生产部署器 | 回测→生产部署必须经过门控验证+灰度发布+回滚 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1931 | S0 多模态知识采集层 S0 Multimodal Knowledge Collection Layer | > **v8.0 统一架构**：7阶段流水线+横切层+安全约束合并为唯一真源。v4.0升级：S0新增漂移感知+VLM+PIT门控+基础模型骨干；S1新增信息价值评分；S2新增因果发现引擎(PC+LiNGAM)+辩论式因子精炼+10类知识（v | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1932 | Whisper 语音转写引擎 | 语音/视频采集用Whisper转写 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1933 | OCR 光学字符识别 | 视频采集用Whisper+OCR | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1934 | 漂移感知调度 Drift-Aware Scheduling | 定时抓取+事件触发+手动提交+漂移感知调度(ADWIN/DDM) | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1935 | VLM图表视觉理解 VLM Chart Visual Understanding | VLM解析K线图/技术图表→结构化信号描述 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1936 | 时序基础模型骨干 TimesFM Foundation Model Backbone | ║  │  🆕VLM图表视觉理解 + 🆕Point-in-Time门控 + 🆕时序基础模型骨干(TimesFM)  │  ║ | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1937 | S1 知识清洗与结构化层 S1 Knowledge Cleaning & Structuring Layer | 去重+去噪+时间戳对齐+说话人分离+术语标准化 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1938 | 信息价值评分 Information Value Scoring | 相关性/时效性/信息量/可靠性多维度评分 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1939 | S2 知识分类与策略提取层 S2 Knowledge Classification & Strategy Extraction Layer | LLM语义理解→知识类型分类(11类)→交易逻辑提取 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1940 | 因果发现引擎 Causal Discovery Engine | PC算法→LiNGAM→时滞因果图→LLM语义校验 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1941 | 辩论式因子精炼 Debate-based Factor Refinement | ║  │  🆕辩论式因子精炼: Generator(GLM-5.1)⇄Critic(DeepSeek)→IC显著提升        │  ║ | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1942 | S3 模块映射与工厂匹配层 S3 Module Mapping & Factory Matching Layer | 分类知识包→目标层级映射→模块工厂查询 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1943 | S4 模块创建与接入层 S4 Module Creation & Integration Layer | 模块需求规格→DSL约束→AST沙箱→人工审核 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1945 | 三重语义一致性 Triple Semantic Consistency | 假设⇄因子表达式⇄代码三者必须语义一致 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1948 | S5 试运行与验证层 S5 Trial Run & Validation Layer | 新模块→C-003完整回测验证→模拟盘观察→效果评估 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1949 | 参数稳定性区域 Parameter Stability Plateau | 参数扫描→识别稳定高原→选高原中心→避悬崖型参数 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1950 | 数学反思闭环 Mathematical Reflection Loop | 反馈→形式化为约束优化→精确求解替代LLM直觉 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1951 | Purge Gap 清洗间隔 | 训练集→Gap期(≥5交易日)→测试集防信息泄漏 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1952 | S6 元学习与自我进化层 S6 Meta-Learning & Self-Evolution Layer | ║  │  S6  元学习与自我进化层                                                   │  ║ | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1953 | STOP Prompt自优化 Prompt Self-Optimization | ║  │  🆕RSI架构: STOP(Prompt自优化) + RISE(代码自纠正) + Voyager(技能库) + Meta-Harness(元优化器) │  ║ | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1954 | RISE 代码自纠正 Code Self-Correction | 模块代码运行异常→LLM自动定位+修正→人工审核 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1955 | Voyager 技能库 Skill Library | 成功代码/模板/公式→结构化存储→新任务优先检索复用 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1956 | Meta-Harness 元优化器 Meta-Optimizer | 优化学习系统自身的超参数:变异率/匹配阈值/审核策略 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1957 | 在线EWC Online Elastic Weight Consolidation | Fisher信息正则化→防灾难性遗忘→保留历史+适应新知 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1958 | 轻量Agent化 Lightweight Agentification | 4维度→4个逻辑Agent+消息队列协调(非物理分布式) | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1960 | 模块工厂 Module Factory | 交易模块池的全生命周期管理:注册/查询/版本/依赖/退役 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1961 | Module Registry 模块注册表 | 因子/信号/策略/风控/模型/功能模块的注册信息 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1965 | MLOps闭环 MLOps Closed Loop | 监控效果→漂移检测→自动重训练→影子验证→金丝雀上线 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1966 | 共形漂移检测 Conformal Drift Detection | 基于共形推断的漂移检测提供统计保证的误报率控制 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1967 | 多尺度漂移检测 Multi-Scale Drift Detection | 微观漂移/中观漂移/宏观漂移三级漂移检测与分级响应 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1968 | 表示学习驱动漂移检测 Representation Learning Drift Detection | hook机制提取模型中间层表示仅用于漂移检测预警 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1969 | 人机协作模式 Human-AI Collaboration Mode | AI自动采集+提取→人类PM审核+补充→AI继续映射 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1970 | K线分词机制 K-line Tokenization | 将K线序列视为金融语言进行分词和自回归预训练 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1972 | Sentiment Engine 情感分析引擎 | finBERT金融情感分析+vaderSentiment规则情感分析双引擎 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1973 | Filing NLP Engine 公告NLP引擎 | 公告文本结构化提取:标题/摘要/关键数据/事件类型 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1974 | 多模态融合引擎 Multimodal Fusion Engine | 早期融合+晚期融合+注意力融合多模态特征 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1975 | A股特色数据 A-Share Special Data | 五类资金追踪+政策预期量化(❌裁定需付费数据源) | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1976 | Trading Domain NLP Engine 交易领域NLP引擎 | 交易领域术语识别+意图解析+领域实体提取 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1977 | Knowledge Quality Assessor 知识质量评估器 | 知识质量4维评估:过时检测+冲突检测+可信度+新鲜度 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1978 | Signal Extractor 信号提取器 | 特征工程+IC测试+信号衰减分析+正交化去冗 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1979 | CausalNLP 文本因果声明提取 | 从文本中提取显式/隐式因果声明 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1980 | TimePC时序因果发现 TimePC Temporal Causal Discovery | 在PC算法基础上增加时序约束专门处理金融时序数据 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1981 | Neural Granger Causality 神经Granger因果 | │   │   ├─ Neural Granger Causality（v5.0新增，ICML 2025） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1982 | Causal KG 因果方向标注 | 在知识图谱的边上标注因果方向(A→B/A←B/A↔B) | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1983 | LLM引导因果发现先验 LLM Prior Causal Discovery | LLM生成因果边白名单/黑名单→约束PC算法搜索空间 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1984 | 带干预的时序因果发现 Intervention-Enhanced Temporal Causal Discovery | 检测政策事件窗口→分别估计前后因果图→比较差异 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1985 | 因果验证层 Causal Validation Layer | 检查是否存在自然实验/工具变量支持→无支持降权 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1986 | 因子语义去重 Factor Semantic Deduplication | LLM判断两个因子的经济学逻辑是否等价 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1987 | GraphRAG图增强检索 GraphRAG Graph-Enhanced Retrieval | 先构建/查询知识图谱子图基于子图上下文进行LLM提取 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1988 | 带推理路径的KG-RAG KG-RAG with Reasoning Path | GraphRAG的演进增强版增加因果图推理路径引导 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1989 | KG引导多跳推理 KG-Guided Multi-Hop Reasoning | 复杂问题→KG检索相关子图→LLM基于子图推理 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1990 | 神经符号融合推理 Neuro-Symbolic Fusion Reasoning | LLM提取(神经)+规则验证(符号)→融合推理 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1991 | 宏观因果传导路径 Macro Causal Transmission Path | 宏观经济指标作为因果图的内在节点显式追踪传导路径 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1992 | 创意拓宽模式 Creative Broadening Mode | LLM一次生成10+假设→快速预评估→仅高潜力假设进入深度提取 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1993 | 因果发现三阶段扩展 Causal Discovery 3-Stage Extension | 工具变量法+Do-calculus+反事实推理 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1994 | Causal Factor Validator 因果因子验证器 | DoWhy因果效应验证+反驳测试 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1995 | PDF预测引擎 PDF Prediction Engine | PDF文档结构化解析→预测模型输入→策略信号生成(❌) | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1996 | Module Matcher 模块匹配器 | │  │  Module Matcher (模块匹配器)                               │   │ | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1997 | 质量-多样性优化 Quality-Diversity Optimization | 维护策略特征图不寻找单一最优策略维护多样化高性能策略集合 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1998 | LLM遗传编程变异算子 LLM Genetic Programming Mutation | LLM作为遗传编程的变异算子替代随机变异 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1999 | Module Dependency Graph 模块依赖图 | 新模块接入前检查依赖/产出/冲突/循环依赖 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2000 | Market Regime Detector 市场制度检测器 | hmmlearn HMM市场制度检测+12种Regime分类 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2003 | 三重语义一致性约束 Triple Semantic Consistency Constraint | 假设→因子表达式→可执行代码三者必须语义一致 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2004 | Generator 生成器Agent | GLM-5.1生成模块代码/因子假设 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2005 | Critic 批判器Agent | DeepSeek V4 Pro审查代码识别逻辑漏洞/过拟合风险 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2006 | Judge 裁判Agent | Claude综合评估→通过AST沙箱→人工审核 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2007 | 轨迹级进化 Trajectory-level Evolution | 每次知识→模块映射视为一条研究轨迹进化时定位次优步骤 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2008 | 可解释设计约束 Explainable By Design Constraint | 可解释设计约束（v5.0新增，Explainable By Design JFML 2025）: | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2009 | Factor Mining Agent 因子挖掘Agent | LLM并发因子假设生成+去重+回测验证 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2010 | Hypothesis Manager 假设管理器 | 假设CRUD+证据关联+状态机(提出→验证→已验证→已推翻) | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2011 | 决策树学习 Decision Tree Learning | **核心逻辑**: 23节点决策流程是人为设定的固定决策树，不适应市场状态变化。专业机构用**Decision Tree Learning**从数据中自动学习决策规则，或用**Reinforcement Learning**端到端优化交易策 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2013 | SHAP值解释 SHAP Value Explanation | 每个交易决策必须可解释。用SHAP值解释模型决策。人工干预接口保留在关键节点。 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2014 | 决策路径可视化 Decision Path Visualization | 决策树的路径可视化理解模型为什么做出某个决策 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2015 | DSR扩展 Deflated Sharpe Ratio Extension | Deflated Sharpe Ratio考虑策略间相关性调整多重检验阈值 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2016 | CPCV v2 Combinatorial Purged Cross-Validation v2 CPCV v2组合净化交叉验证v2 | Combinatorial Purged Cross-Validation扩展版支持非IID数据 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2017 | White's Reality Check 怀特现实检验 | 过拟合检测统计功效提升30%改进bootstrap重采样方法 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2018 | Adaptive Walk-Forward 自适应Walk-Forward | 自适应窗口步进:根据市场波动率动态调整训练/测试窗口长度 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2019 | Probabilistic Backtesting 概率回测 | 贝叶斯回测:输出策略性能的后验分布而非点估计 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2020 | 信息论过拟合检测 Information-Theoretic Overfitting Detection | 互信息/KL散度量化训练集vs测试集信息增益差异 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2021 | 市场状态感知Walk-Forward Regime-Aware Walk-Forward | └─ 市场状态感知Walk-Forward（v6.0新增，Regime-Aware Walk-Forward 2025-2026） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2022 | 对抗性知识增强 Adversarial Knowledge Enhancement | 在特征空间注入扰动进行对抗训练测试模块对分布漂移的鲁棒性 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2023 | 延迟离线学习模式 Delayed Offline Learning Mode | 新知识先记录→离线训练→验证通过→才进入试运行 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2024 | A/B测试框架 A/B Testing Framework | 新模块与旧模块并行运行(影子部署)统计比较效果 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2028 | Strategy Sandbox轻量版 策略沙盒轻量版 | 15. Strategy Sandbox轻量版（v8.0新增，裁定✅R-117） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2029 | Liquidity & Slippage Simulator 流动性与滑点模拟器 | Almgren-Chriss市场冲击模型+滑点模拟 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2030 | Order Matching Simulator 订单匹配模拟器 | 限价订单簿模拟:买卖五档挂单+撮合引擎 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2031 | Scenario Generator基础版 情景生成器基础版 | 历史数据重采样+自定义情景生成(CPU版) | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2032 | 技能三元组 Skill Triple | 每个技能存储为(条件动作效果)三元组使技能检索更精确 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2034 | AutoSkill自动技能发现 AutoSkill Automatic Skill Discovery | LLM分析成功/失败的研究轨迹→自动抽象为新技能 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2035 | MAML快速适应 MAML Fast Adaptation | MAML(Model-Agnostic Meta-Learning)变体新市场5-10 episode适应 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2036 | ICL作为元学习 ICL as Meta-Learning | └─ v6.0增强: ICL作为元学习替代方案（精心设计prompt含历史成功/失败案例→LLM上下文中适应新市场→无需显式元训练→与维度5 MAML互补：小样本用ICL，大样本用MAML） | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2037 | 元反思 Meta-Reflection | 经验回放+反思提炼+技能注册+元反思四步闭环 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2038 | PromptOptimizer Agent 提示词优化Agent | 负责维度1学习如何学习Prompt自优化循环 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2039 | ArchitectureOptimizer Agent 架构优化Agent | 负责维度2学习架构优化代码自纠正循环 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2040 | CodeGenerator Agent 代码生成Agent | 负责维度3学习代码生成技能库积累 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2041 | MethodologyLearner Agent 方法论学习Agent | 负责维度4学习方法论元优化器优化自身超参 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2042 | Walk-Forward Analyzer完整版 Walk-Forward Analyzer Full Version | 滚动Walk-Forward+锚定Walk-Forward+扩展Walk-Forward | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2043 | 过拟合检测扩展 Overfitting Detection Extension | Bonferroni校正+FDR(Benjamini-Hochberg)+BHY多重检验校正 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2044 | Signal Confidence Scorer 信号置信度评分器 | Platt Scaling+Isotonic Regression概率校准+MC Dropout不确定性 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2045 | 三层参数优化 3-Layer Parameter Optimization | 实时微调+周期优化+结构进化三层参数优化 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2046 | Monte Carlo Engine 蒙特卡洛引擎 | GPU加速蒙特卡洛模拟:策略风险分布估计+压力测试(❌) | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2062 | Synthetic Data Generator基础版 合成数据生成器基础版 | SMOTE过采样+轻量GAN生成稀有市场条件数据 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2070 | Causal SHAP 因果Shapley值 | 基于因果图计算Shapley值区分真因果与伪相关 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2071 | 因果约束反事实解释 Causal-Constrained Counterfactual Explanation | 因果图约束反事实生成空间→确保反事实场景因果合理 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2072 | 交互式解释 Interactive Explanation | LLM+SHAP/因果图RAG问答→审批者可追问AI决策理由 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2073 | 漂移感知集成 Drift-Aware Ensemble | 根据各模型漂移适应能力动态调整集成权重 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2074 | 定时采集 Scheduled Collection | 每日固定时间抓取指定直播/专栏盘后集中采集当日分析师内容 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2075 | 事件触发采集 Event-Triggered Collection | 重大政策发布/市场异动/新研报发布触发紧急解读采集 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2076 | 手动提交 Manual Submission | 用户粘贴文字/上传PDF音频视频/提交网址链接 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2077 | 格式转换 Format Conversion | 音频视频Whisper转写+PDF文本提取+网址正文提取+文字直接通过 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2078 | 去重 Deduplication | 精确去重(内容哈希)+近似去重(SimHash/MinHash)+跨源去重 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2079 | 去噪 Denoising | 口语化填充词去除+重复语句合并+无关内容裁剪+时间戳对齐 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2080 | 术语标准化 Terminology Normalization | 口语→标准术语+股票代码标准化+板块名称标准化 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2081 | 说话人分离 Speaker Diarization | 5. 说话人分离 (Speaker Diarization) — 仅语音/视频 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2082 | LLM语义理解 LLM Semantic Understanding | 理解文本交易含义+识别隐含交易逻辑+文本因果声明提取 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2083 | 知识类型分类 Knowledge Type Classification | 规则+LLM混合分类策略/因子/市场状态等多标签分类 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2084 | 交易逻辑提取 Trading Logic Extraction | 按知识类型使用不同提取模板输出结构化交易逻辑 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2085 | 矛盾检测 Conflict Detection | 语义相似度+逻辑冲突检测一致增强/矛盾标记/新增 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2086 | PC算法 PC Algorithm | causal-learn从因子数据中自动发现因果骨架无向边 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2087 | LiNGAM | causal-learn确定因果方向输出有向因果边A→B | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2088 | 时滞因果扩展 Lagged Causal Extension | 因果边从即时→时滞支持X滞后k期影响Y的时滞因果关系 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2095 | DeepSCM深度因果模型 DeepSCM Deep Causal Model | / R-37 / DeepSCM深度因果模型 / ❌ / 硬边界约束二（单机Windows+Python，深度因果模型需GPU集群训练） / GPU集群+Linux+PyTorch分布式训练就绪 / | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2096 | ODL-Net在线深度学习 ODL-Net Online Deep Learning | / R-38 / ODL-Net在线深度学习 / ❌ / 硬边界约束二（在线深度学习需GPU集群） / GPU集群+在线训练框架就绪 / | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2099 | Synthetic Backtesting合成回测 Synthetic Backtesting | / R-41 / Synthetic Backtesting合成回测 / ❌ / 硬边界约束二（生成模型需GPU集群） / GPU集群+扩散模型/GAN训练框架就绪 / | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2101 | 高级回测 Advanced Backtesting | / R-48 / 高级回测(DSR+CPCV v2+White's Reality Check+Adaptive Walk-Forward+Probabilistic Backtesting) / ✅ / 统计检验+贝叶斯回测，纯Pytho | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2102 | AlphaFin统一多模态框架 AlphaFin Unified Multimodal Framework | / R-64 / AlphaFin统一多模态框架 / ❌ / 硬边界约束二（统一多模态模型需GPU集群） / 统一多模态模型量化部署方案就绪+RTX 3090 24GB显存验证通过 / | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2103 | FinVision端到端图表→策略 FinVision End-to-End Chart to Strategy | / R-65 / FinVision端到端图表→策略 / ❌ / 硬边界约束三（端到端生成绕过DSL+AST沙箱安全约束） / 端到端生成不绕过DSL+AST沙箱的安全方案设计完成 / | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2104 | AlphaEvolve元级基础设施进化 AlphaEvolve Meta-Level Infrastructure Evolution | / R-66 / AlphaEvolve元级基础设施进化 / ❌ / 硬边界约束三（DSL语法进化可能破坏AST沙箱安全约束） / DSL语法进化不破坏AST沙箱安全约束的验证方案就绪 / | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2105 | 可微因果发现 Differentiable Causal Discovery NOTEARS+ | / R-67 / 可微因果发现(NOTEARS+) / ❌ / 硬边界约束二（连续优化需GPU长时间训练） / RTX 3090上<100变量训练时间<4h验证通过 / | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2106 | Knowledge Effectiveness Evaluator 知识效果评估器 | §11.2效果反馈接口接收C-010数据评估注入知识是否有效 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2108 | End-to-End Causal Factor Analysis 端到端因果因子分析 | / **端到端因果因子分析**：从因果发现到因果情景建模的完整管线，应用于因子投资 / Toward Automating Causal Discovery (World Scientific 2025) / 因子知识仅做IC验证，无因果验 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2110 | Researcher Agent 研究Agent | 战略层研究Agent策略研究因子发现 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2134 | Factor Proposal 因子提案 | 研究Agent技能因子提案ACTIVE | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2135 | Strategy Code Generation 策略代码生成 | 研究Agent技能策略代码生成ACTIVE | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2137 | Paper Search 论文搜索 | 研究Agent技能论文搜索ACTIVE | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2386 | Learning System Performance Attribution 学习系统绩效归因 | 学习系统绩效归因3功能点收益归因Brinson模型到因子归因到风险归因来源A8 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2409 | Effect Feedback Path 效果反馈路径 | 效果反馈路径2路径C-010归因报告到学习系统知识效果评估CTR-P1-009每日+C-033过拟合检测到学习系统过拟合标记归因报告每周 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2585 | C-029 Model Factory 模型工厂 | 模型工厂训练数据审计+漂移检测 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2586 | C-030 Decision Explainability 决策可解释性 | 决策可解释性AI决策过程日志 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2642 | 7 Stage Learning Pipeline 7阶段学习流水线 | S0~S6七阶段学习流水线 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2643 | Module Factory Architecture 模块工厂架构 | 模块工厂架构与模块生命周期核心独创 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2644 | Knowledge Classification System 知识分类体系 | 11类知识分类+因果发现引擎+辩论式因子精炼 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2645 | Meta Learning Ability 元学习能力定义 | / 元学习能力定义与学习策略（RSI架构4维度+技能库+在线EWC+MAML+AutoSkill） / 风险约束（→A4） / | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2646 | Multi Modal Knowledge Acquisition 多模态知识采集 | / 多模态知识采集（Whisper/VLM/PDF/爬虫+漂移感知调度+PIT门控） / Agent内部架构（→A7） / | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2647 | DSL AST Sandbox Code Generation DSL+AST沙箱安全代码生成 | 进化式代码生成+三重语义一致性 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2648 | 4 Level Risk Control Decision Gating 4级风控决策门控 | / 4级风控决策门控（APPROVE/REDUCE/REJECT/FLATTEN）+可解释性门控（SHAP/LIME/Causal SHAP） / / | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-4871 | Module Factory 模块工厂 | 交易模块池全生命周期管理注册查询版本依赖退役 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-4872 | Agent Drift Detection Agent漂移检测 | KL散度大于阈值自动降级为仅建议模式 | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4873 | Cluster Behavior Protection 群集行为防护 | 与行业模型相关性>0.7自动差异化+市场压力时降仓 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-4874 | RSI Architecture RSI自进化架构 | ║  │  🆕RSI架构: STOP(Prompt自优化) + RISE(代码自纠正) + Voyager(技能库) + Meta-Harness(元优化器) │  ║ | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-4875 | Security Governance 安全与治理 | 知识来源追溯+模块变更审计+自动操作日志+人工审批 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-5038 | Learning System 7-Stage Pipeline 学习系统7阶段流水线 | / — / 学习系统7阶段流水线 / S0感知→S1采集→S2映射→S3验证→S4注入→S5反馈→S6进化 / ✅ / | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-5039 | Meta-Learning Capability 元学习能力 | / — / 元学习能力 / RSI架构4维度+技能库+在线EWC+MAML+AutoSkill / ✅ / | D_INTELLIGENCE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-5040 | DSL AST Sandbox DSL+AST沙箱 | 安全代码生成+进化式代码生成+三重语义一致性 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-5041 | Multimodal Knowledge Collection 多模态知识采集 | / — / 多模态知识采集 / Whisper/VLM/PDF/爬虫+漂移感知调度+PIT门控 / ✅ / | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-5042 | MLOps Closed Loop MLOps闭环 | 模型版本管理/实验追踪/自动重训练/模型注册/部署管道 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-5043 | Reproducibility Pack Generator 可复现性包生成器 | 实验环境+数据+代码打包+版本锁定 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-5044 | Research Information Isolation 研究信息隔离 | 研究域与交易域信息隔离+合规约束 | D_INTELLIGENCE | harvest待评估（likely_new） |  |
| CAND-HARVEST-5094 | FeatureStore PIT Feature Feed FeatureStore PIT特征供给 | / SIM-RES-01 / D-RESEARCH→SIM / — / D-RESEARCH / FeatureStore PIT特征→回测数据输入 / P1 / | D_INTELLIGENCE | harvest待评估（likely_new） |  |

## 复查时间表

> 按 next_review_date 升序。复查时重新过四问，触发信号命中则晋升到 depgraph 设计态。

| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |
|------|------|------|------|------|------|------|
| 2026-10-31 | quarterly | CAND-AISA-001 | AI Sentiment Analyzer / AI 舆情分析器 | D_INTELLIGENCE | 候选待评（candidate） | 首次登记为 candidate,待四问评估。重点评估 q4:TRAE AI 是否可替代独立模块 |
| 2026-11-30 | quarterly | CAND-HARVEST-0061 | Cross-Market Transmission Quantitative Model 跨市场传导量化模型 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0083 | AI协作策略与人机信任模型 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0084 | Auto Backtest & Simulation 自动回测与仿真 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0086 | AI自治运维 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0087 | ML模型工厂 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0095 | 知识模型自进化 Model Knowledge | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0245 | Feature Store特征存储 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0246 | Experiment Tracker实验追踪 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0247 | Notebook Integration Notebook集成 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0248 | Reproducibility Manager可复现性管理 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0249 | Hypothesis Manager假设管理 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0250 | LLM Research Agent LLM研究助手 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0251 | Strategy Iteration Upgrader策略迭代升级 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0597 | Data Quality Scorer 数据质量评分器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0694 | Research Data Manager 研究数据管理器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0695 | Research Data Sandbox 研究数据沙箱 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0696 | Research Information Barrier 研究信息隔离 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0697 | Research Asset Versioning 研究资产版本化 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0878 | Research Catalog 研究目录 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0879 | Paper Tracker 论文追踪器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0880 | Research Workflow Engine 研究工作流引擎 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0881 | Research Collaboration Hub 研究协作中心 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0882 | Research Experiment Anomaly Detector 研究实验异常检测器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0883 | Research Discovery Knowledge Base 研究发现知识库 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0884 | Research Reproducibility Pack Generator 研究复现包生成器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1237 | Research Knowledge Precipitator 研究知识沉淀器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1896 | AutoML Engine 自动ML引擎 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1929 | Backtest-to-Production Deployer 回测到生产部署器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1931 | S0 多模态知识采集层 S0 Multimodal Knowledge Collection Layer | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1932 | Whisper 语音转写引擎 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1933 | OCR 光学字符识别 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1934 | 漂移感知调度 Drift-Aware Scheduling | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1935 | VLM图表视觉理解 VLM Chart Visual Understanding | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1936 | 时序基础模型骨干 TimesFM Foundation Model Backbone | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1937 | S1 知识清洗与结构化层 S1 Knowledge Cleaning & Structuring Layer | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1938 | 信息价值评分 Information Value Scoring | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1939 | S2 知识分类与策略提取层 S2 Knowledge Classification & Strategy Extraction Layer | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1940 | 因果发现引擎 Causal Discovery Engine | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1941 | 辩论式因子精炼 Debate-based Factor Refinement | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1942 | S3 模块映射与工厂匹配层 S3 Module Mapping & Factory Matching Layer | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1943 | S4 模块创建与接入层 S4 Module Creation & Integration Layer | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1945 | 三重语义一致性 Triple Semantic Consistency | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1948 | S5 试运行与验证层 S5 Trial Run & Validation Layer | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1949 | 参数稳定性区域 Parameter Stability Plateau | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1950 | 数学反思闭环 Mathematical Reflection Loop | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1951 | Purge Gap 清洗间隔 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1952 | S6 元学习与自我进化层 S6 Meta-Learning & Self-Evolution Layer | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1953 | STOP Prompt自优化 Prompt Self-Optimization | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1954 | RISE 代码自纠正 Code Self-Correction | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1955 | Voyager 技能库 Skill Library | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1956 | Meta-Harness 元优化器 Meta-Optimizer | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1957 | 在线EWC Online Elastic Weight Consolidation | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1958 | 轻量Agent化 Lightweight Agentification | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1960 | 模块工厂 Module Factory | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1961 | Module Registry 模块注册表 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1965 | MLOps闭环 MLOps Closed Loop | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1966 | 共形漂移检测 Conformal Drift Detection | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1967 | 多尺度漂移检测 Multi-Scale Drift Detection | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1968 | 表示学习驱动漂移检测 Representation Learning Drift Detection | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1969 | 人机协作模式 Human-AI Collaboration Mode | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1970 | K线分词机制 K-line Tokenization | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1972 | Sentiment Engine 情感分析引擎 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1973 | Filing NLP Engine 公告NLP引擎 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1974 | 多模态融合引擎 Multimodal Fusion Engine | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1975 | A股特色数据 A-Share Special Data | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1976 | Trading Domain NLP Engine 交易领域NLP引擎 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1977 | Knowledge Quality Assessor 知识质量评估器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1978 | Signal Extractor 信号提取器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1979 | CausalNLP 文本因果声明提取 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1980 | TimePC时序因果发现 TimePC Temporal Causal Discovery | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1981 | Neural Granger Causality 神经Granger因果 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1982 | Causal KG 因果方向标注 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1983 | LLM引导因果发现先验 LLM Prior Causal Discovery | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1984 | 带干预的时序因果发现 Intervention-Enhanced Temporal Causal Discovery | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1985 | 因果验证层 Causal Validation Layer | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1986 | 因子语义去重 Factor Semantic Deduplication | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1987 | GraphRAG图增强检索 GraphRAG Graph-Enhanced Retrieval | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1988 | 带推理路径的KG-RAG KG-RAG with Reasoning Path | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1989 | KG引导多跳推理 KG-Guided Multi-Hop Reasoning | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1990 | 神经符号融合推理 Neuro-Symbolic Fusion Reasoning | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1991 | 宏观因果传导路径 Macro Causal Transmission Path | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1992 | 创意拓宽模式 Creative Broadening Mode | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1993 | 因果发现三阶段扩展 Causal Discovery 3-Stage Extension | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1994 | Causal Factor Validator 因果因子验证器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1995 | PDF预测引擎 PDF Prediction Engine | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1996 | Module Matcher 模块匹配器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1997 | 质量-多样性优化 Quality-Diversity Optimization | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1998 | LLM遗传编程变异算子 LLM Genetic Programming Mutation | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1999 | Module Dependency Graph 模块依赖图 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2000 | Market Regime Detector 市场制度检测器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2003 | 三重语义一致性约束 Triple Semantic Consistency Constraint | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2004 | Generator 生成器Agent | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2005 | Critic 批判器Agent | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2006 | Judge 裁判Agent | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2007 | 轨迹级进化 Trajectory-level Evolution | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2008 | 可解释设计约束 Explainable By Design Constraint | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2009 | Factor Mining Agent 因子挖掘Agent | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2010 | Hypothesis Manager 假设管理器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2011 | 决策树学习 Decision Tree Learning | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2013 | SHAP值解释 SHAP Value Explanation | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2014 | 决策路径可视化 Decision Path Visualization | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2015 | DSR扩展 Deflated Sharpe Ratio Extension | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2016 | CPCV v2 Combinatorial Purged Cross-Validation v2 CPCV v2组合净化交叉验证v2 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2017 | White's Reality Check 怀特现实检验 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2018 | Adaptive Walk-Forward 自适应Walk-Forward | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2019 | Probabilistic Backtesting 概率回测 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2020 | 信息论过拟合检测 Information-Theoretic Overfitting Detection | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2021 | 市场状态感知Walk-Forward Regime-Aware Walk-Forward | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2022 | 对抗性知识增强 Adversarial Knowledge Enhancement | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2023 | 延迟离线学习模式 Delayed Offline Learning Mode | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2024 | A/B测试框架 A/B Testing Framework | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2028 | Strategy Sandbox轻量版 策略沙盒轻量版 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2029 | Liquidity & Slippage Simulator 流动性与滑点模拟器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2030 | Order Matching Simulator 订单匹配模拟器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2031 | Scenario Generator基础版 情景生成器基础版 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2032 | 技能三元组 Skill Triple | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2034 | AutoSkill自动技能发现 AutoSkill Automatic Skill Discovery | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2035 | MAML快速适应 MAML Fast Adaptation | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2036 | ICL作为元学习 ICL as Meta-Learning | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2037 | 元反思 Meta-Reflection | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2038 | PromptOptimizer Agent 提示词优化Agent | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2039 | ArchitectureOptimizer Agent 架构优化Agent | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2040 | CodeGenerator Agent 代码生成Agent | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2041 | MethodologyLearner Agent 方法论学习Agent | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2042 | Walk-Forward Analyzer完整版 Walk-Forward Analyzer Full Version | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2043 | 过拟合检测扩展 Overfitting Detection Extension | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2044 | Signal Confidence Scorer 信号置信度评分器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2045 | 三层参数优化 3-Layer Parameter Optimization | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2046 | Monte Carlo Engine 蒙特卡洛引擎 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2062 | Synthetic Data Generator基础版 合成数据生成器基础版 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2070 | Causal SHAP 因果Shapley值 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2071 | 因果约束反事实解释 Causal-Constrained Counterfactual Explanation | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2072 | 交互式解释 Interactive Explanation | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2073 | 漂移感知集成 Drift-Aware Ensemble | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2074 | 定时采集 Scheduled Collection | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2075 | 事件触发采集 Event-Triggered Collection | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2076 | 手动提交 Manual Submission | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2077 | 格式转换 Format Conversion | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2078 | 去重 Deduplication | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2079 | 去噪 Denoising | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2080 | 术语标准化 Terminology Normalization | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2081 | 说话人分离 Speaker Diarization | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2082 | LLM语义理解 LLM Semantic Understanding | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2083 | 知识类型分类 Knowledge Type Classification | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2084 | 交易逻辑提取 Trading Logic Extraction | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2085 | 矛盾检测 Conflict Detection | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2086 | PC算法 PC Algorithm | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2087 | LiNGAM | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2088 | 时滞因果扩展 Lagged Causal Extension | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2095 | DeepSCM深度因果模型 DeepSCM Deep Causal Model | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2096 | ODL-Net在线深度学习 ODL-Net Online Deep Learning | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2099 | Synthetic Backtesting合成回测 Synthetic Backtesting | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2101 | 高级回测 Advanced Backtesting | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2102 | AlphaFin统一多模态框架 AlphaFin Unified Multimodal Framework | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2103 | FinVision端到端图表→策略 FinVision End-to-End Chart to Strategy | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2104 | AlphaEvolve元级基础设施进化 AlphaEvolve Meta-Level Infrastructure Evolution | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2105 | 可微因果发现 Differentiable Causal Discovery NOTEARS+ | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2106 | Knowledge Effectiveness Evaluator 知识效果评估器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2108 | End-to-End Causal Factor Analysis 端到端因果因子分析 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2110 | Researcher Agent 研究Agent | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2134 | Factor Proposal 因子提案 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2135 | Strategy Code Generation 策略代码生成 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2137 | Paper Search 论文搜索 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2386 | Learning System Performance Attribution 学习系统绩效归因 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2409 | Effect Feedback Path 效果反馈路径 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2585 | C-029 Model Factory 模型工厂 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2586 | C-030 Decision Explainability 决策可解释性 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2642 | 7 Stage Learning Pipeline 7阶段学习流水线 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2643 | Module Factory Architecture 模块工厂架构 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2644 | Knowledge Classification System 知识分类体系 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2645 | Meta Learning Ability 元学习能力定义 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2646 | Multi Modal Knowledge Acquisition 多模态知识采集 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2647 | DSL AST Sandbox Code Generation DSL+AST沙箱安全代码生成 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2648 | 4 Level Risk Control Decision Gating 4级风控决策门控 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4871 | Module Factory 模块工厂 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4872 | Agent Drift Detection Agent漂移检测 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4873 | Cluster Behavior Protection 群集行为防护 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4874 | RSI Architecture RSI自进化架构 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4875 | Security Governance 安全与治理 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-5038 | Learning System 7-Stage Pipeline 学习系统7阶段流水线 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-5039 | Meta-Learning Capability 元学习能力 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-5040 | DSL AST Sandbox DSL+AST沙箱 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-5041 | Multimodal Knowledge Collection 多模态知识采集 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-5042 | MLOps Closed Loop MLOps闭环 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-5043 | Reproducibility Pack Generator 可复现性包生成器 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-5044 | Research Information Isolation 研究信息隔离 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-5094 | FeatureStore PIT Feature Feed FeatureStore PIT特征供给 | D_INTELLIGENCE | 候选待评（candidate） | harvest待评估（likely_new） |
