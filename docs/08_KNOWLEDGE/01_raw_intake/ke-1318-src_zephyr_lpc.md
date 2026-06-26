---
module_id: KE-GOVERNANCE-SRC-ZEPHYR-LPC-007
status: active
title: 三、`src/zephyr/` 双轨结构（LPC）
category: governance
ttl: permanent
---

# 三、`src/zephyr/` 双轨结构（LPC）

三、`src/zephyr/` 双轨结构（LPC）

见 KBG-0022 §3.1：

```
src/zephyr/
│
│  ═══════════ C 轨：14 层业务脊柱（带 l<NN>_ 前缀） ═══════════
│
├── data/                     # L00 数据接入
├── infra_ops/                  # L01 基础设施
├── factor/                    # L02 因子
├── signal/               # L03 信号生成
├── risk/                 # L04 风控
├── pf_core/          # L05 组合构建
├── ex_core/                 # L06 交易执行
├── reporting/            # L07 归因分析
├── frontend/              # L08 人机界面
├── research/             # L09 研究创新
├── compliance/                      # L10 合规（业务层）
├── ml_train/                     # L11 ML 平台（训练/推理/模型注册）
├── infra_ops/                # L12 系统可观测（跨层支撑子系统）
│   ├── metrics/
│   ├── logs/
│   ├── traces/
│   ├── ai_behavior/                     # AI 行为遥测（幻觉率 / token / 规则触发）
│   └── archive/
├── simulation/                 # L13 自动化实验
│
│  ═══════════ B 轨：横切平台能力（无前缀） ═══════════
│
├── llm-security/                        # LSG  · KBG-0020
├── vector-memory/                       # VMS  · KBG-0016
├── context-engine/                      # CE   · KBG-0015
├── orchestrator/                        # Orc  · KBG-0017
├── feedback-loop/                       # FLE  · KBG-0019
├── gates/                               # 合规门禁（G1-GN 运行时）
├── pipeline/                            # 管线编排 · ADR-00XX
├── core/                                # 蓝图分解器+TaskCard核心模型 · ADR-00XX
├── db/                                  # SQLite schema / atomic 事务
├── kb/                                  # 2 过渡期知识库（beta 并入 vector_memory）
├── mcp/                                 # Model Context Protocol 客户端
├── shared/                              # 跨层契约 / 共享工具
├── agent-rbac/                          # Agent 身份与权限 · MOD-INF-018
├── agent-spec/                          # 可执行 Agent Spec · MOD-INF-019
├── audit-trail/                         # 审计追踪链 · MOD-INF-020
├── rollback/                            # 回滚/撤销 · MOD-INF-021
├── escalation/                          # 升级/委托 · MOD-INF-022
├── drift-detector/                      # 漂移检测 · MOD-INF-023
├── budget-enforcer/                     # 预算强制执行 · MOD-INF-024
└── a2a/                                 # Agent-to-Agent 协调 · MOD-INF-025
└── telemetry/                          # 全系统可观测性 · MOD-INF-015
```
