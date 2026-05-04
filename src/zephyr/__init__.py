"""
ZephyrAlpha 核心包索引 — LPC 双轨架构
======================================

.. 版本:: v4.6.0 | 2026-05-02

C 轨 — 14 层业务脊柱（按编号顺序，数据从左到右逐层加工）
-------------------------------------------------------
l00_data_source          — 数据接入层：行情、基本面、另类数据源
l01_infrastructure       — 基础设施层：编码、脚本系统、API 网关
l02_alpha_factor         — Alpha 因子层：因子定义、计算、注册、回测
l03_signal_generation    — 信号生成层：因子合成、信号生成、衰减模型
l04_risk_management      — 风险管理层：风控模型、头寸限制、压力测试
l05_portfolio_construction — 组合构建层：优化器、权重分配、再平衡
l06_trade_execution      — 交易执行层：订单生成、TWAP/VWAP 算法、路由
l07_post_trade_analytics — 盘后分析层：成交分析、滑点归因、交易成本
l08_human_ai_interface   — 人机界面层：仪表盘、告警、可视化
l09_research_innovation  — 研究创新层：实验框架、论文复现、新思路原型
l10_compliance           — 合规层：监管报告、持仓披露、交易审计
l11_ml_platform          — ML 平台层：训练 pipeline、模型注册、特征存储
l12_system_telemetry     — 遥测层：Metrics/Logs/Traces/AI 行为记录
l13_experimentation      — 实验层：A/B 测试、影子模式、回测对比

B 轨 — 10 横切平台能力（所有 C 轨层依赖的平台基础设施）
--------------------------------------------------------
context_engine           — 上下文引擎：四阶段流水线（构建→压缩→验证→注入）
db                       — 元数据持久化层：SQLite + 原子事务管理器
feedback_loop            — 反馈循环引擎：指标采集→异常检测→自动纠错
gates                    — 门禁系统：任务启动前 G1~G5 多阶段合规检查
kb                       — 知识库：KE 摄入/提取/分析/分类，ChromaDB 向量存储
llm_security             — LLM 安全：Prompt Injection 防御 + 行为审计
mcp                      — 多组件平台：模块间统一通信路由
orchestrator             — 编排器：Wave 任务调度 + 状态同步 + 故障回滚
shared                   — 共享契约：Pydantic Schema、常量、公共工具（SSoT）
vector_memory            — 向量内存：语义检索基础设施，kb/context_engine 底层

快速导入参考
-----------
核心数据模型:    from zephyr.shared.schemas import Task, TaskNamespace, TaskStatus
知识库操作:      from zephyr.kb import ingest, extract, analyze
门禁检查:        from zephyr.gates import gate_engine
任务调度:        from zephyr.orchestrator import wave_generator, agent_orchestrator
上下文构建:      from zephyr.context_engine import intent_parser, pattern_library

目录结构权威来源（SSoT）
-----------------------
docs/01_policies_and_standards/governance/document/directory-structure-standard.md §三
本索引仅用于快速导航。如果找不到你需要的模块，请先查上述 SSoT。
"""
