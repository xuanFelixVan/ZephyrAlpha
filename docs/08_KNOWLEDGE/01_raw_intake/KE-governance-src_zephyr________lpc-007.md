---
module_id: KE-governance-src_zephyr________lpc-007
title: 三、`src/zephyr/` 双轨结构（LPC）
category: governance
---

# 三、`src/zephyr/` 双轨结构（LPC）

三、`src/zephyr/` 双轨结构（LPC）

见 ADR-0022 §3.1：

```
src/zephyr/
│
│  ═══════════ C 轨：14 层业务脊柱（带 l<NN>_ 前缀） ═══════════
│
├── l00_data_source/                     # L00 数据接入
├── l01_infrastructure/                  # L01 基础设施
├── l02_alpha_factor/                    # L02 因子
├── l03_signal_generation/               # L03 信号生成
├── l04_risk_management/                 # L04 风控
├── l05_portfolio_construction/          # L05 组合构建
├── l06_trade_execution/                 # L06 交易执行
├── l07_post_trade_analytics/            # L07 归因分析
├── l08_human_ai_interface/              # L08 人机界面
├── l09_research_innovation/             # L09 研究创新
├── l10_compliance/                      # L10 合规（业务层）
├── l11_ml_platform/                     # L11 ML 平台（训练/推理/模型注册）
├── l12_system_telemetry/                # L12 系统可观测（跨层支撑子系统）
│   ├── metrics/
│   ├── logs/
│   ├── traces/
│   ├── ai_behavior/                     # AI 行为遥测（幻觉率 / token / 规则触发）
│   └── archive/
├── l13_experimentation/                 # L13 自动化实验
│
│  ═══════════ B 轨：横切平台能力（无前缀） ═══════════
│
├── llm_security/                        # LSG  · ADR-0020
├── vector_memory/                       # VMS  · ADR-0016
├── context_engine/                      # CE   · ADR-0015
├── orchestrator/                        # Orc  · ADR-0017
├── feedback_loop/                       # FLE  · ADR-0019
├── gates/                               # 合规门禁（G1-GN 运行时）
├── pipeline/                            # 管线编排 · ADR-00XX
├── core/                                # 蓝图分解器+TaskCard核心模型 · ADR-00XX
├── db/                                  # SQLite schema / atomic 事务
├── kb/                                  # 2 过渡期知识库（beta 并入 vector_memory）
├── mcp/                                 # Model Context Protocol 客户端
├── shared/                              # 跨层契约 / 共享工具
├── agent_rbac/                          # Agent 身份与权限 · MOD-INF-018
├── agent_spec/                          # 可执行 Agent Spec · MOD-INF-019
├── audit_trail/                         # 审计追踪链 · MOD-INF-020
├── rollback/                            # 回滚/撤销 · MOD-INF-021
├── escalation/                          # 升级/委托 · MOD-INF-022
├── drift_detector/                      # 漂移检测 · MOD-INF-023
├── budget_enforcer/                     # 预算强制执行 · MOD-INF-024
└── a2a/                                 # Agent-to-Agent 协调 · MOD-INF-025
└── telemetry/                          # 全系统可观测性 · MOD-INF-015
```
