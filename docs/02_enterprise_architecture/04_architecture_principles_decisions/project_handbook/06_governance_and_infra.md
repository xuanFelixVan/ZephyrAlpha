---
ttl: permanent
doc_type: architecture_view
title: 治理与基础设施域 / Governance & Infrastructure
owner: ZephyrAlpha-Owner
language: zh
---

# 06 · 治理与基础设施域

> 大白话项目现状。提交链 + Commit Gates + Reconciler + depgraph 双态 + Registry + AUTO 计数。

## 1. 提交链（GitCommitGateway / session_worktree）

| 组件 | 位置 | 职责 |
|------|------|------|
| `GitCommitGateway` | `gov_enforcement/rule_bridge/git_commit_gateway.py` | 全项目唯一合法 git commit 入口（串行锁 `_GlobalCommitLock` + stash 隔离 + GW 标记）；CLI `scripts/git_commit.py` |
| `CommitGateRegistry` | `gov_enforcement/commit_gates/` | 门禁注册表 |
| `session_worktree` | `gov_enforcement/rule_bridge/session_worktree.py` | worktree 会话隔离（君子协定 FP-ISO.4C；TRAE-079 Phase 2 已降级为可选，直接走 GitCommitGateway 文件锁串行提交） |

> **铁律**：裸 `git commit` 被 pre-commit gate 硬阻断（GATE-COMMIT-GW）。逃生通道：`allow_overlap`/`force_merge`（开发期，会产生 abuse-monitor critical_warn，需 ack）。

## 2. Commit Gates 体系（pre-commit 门禁）

`gov_enforcement/commit_gates/` 下 ~80 个 gate（AST/diff/路径/命名/依赖/blueprint 格式/depgraph 预登记/能力反查等维度），按 priority 升序执行。

<!-- AUTO-START:gate_counts -->
<!-- 数据源：commit_gates 目录扫描 | 最后同步：2026-08-17 -->

| 指标 | 值 |
|------|----|
| commit_gates 目录 / Directory | `src\zephyr\gov_enforcement\commit_gates` |
| 门禁 .py 文件数 / Gate files (excl. __init__) | 103 |

> 门禁按 priority 升序执行（AST/diff/路径/命名/依赖/blueprint 格式/depgraph 预登记/能力反查等维度）。
<!-- AUTO-END:gate_counts -->

## 3. Post-commit Reconciler 体系

事件触发（非时间/手动）的 reconciler 体系，失败结果持久化到 `reconcile_execution_log` 表（错误详情不截断）。含 `worktree_lifecycle_reconciler`（worktree TTL 回收，P1-2 跨进程互斥已治本）。

## 4. depgraph 机制（设计态 / 运营态）

- **存储**：PostgreSQL 16（P2 迁移 2026-06-27，MVCC 行级锁）
- **双态模型**：`design`（设计态，蓝图）→ `production`（运营态，代码已写），单调推进
- **三层防御**（RULE-DEPGRAPH）：①依赖关系先行 ②五图对齐 ③双态机械判定
- 详见 [../panorama/dependency_path_panorama.md](../panorama/dependency_path_panorama.md)

**关键工具**：
```bash
python scripts/governance/generate_project_depgraph.py    # 刷新运营态（扫描代码）
python scripts/governance/apply_depgraph.py --add-design-node PATH BLUEPRINT_ID DOMAIN_ID  # 登记设计态
python scripts/governance/sync_panorama_module.py --all      # 派生其余3图
python scripts/governance/d5_architecture/generators/align_panoramas.py  # 五图对齐验证
```

## 5. Registry 体系

32 个 registry 总索引（module_id / capability / data_source / cross_layer_contracts / error_code / 等）。真源 = YAML，`sync_yaml_to_depgraph.py` 单向同步到 DB。

## 6. 治理脚本系统

`scripts/governance/` 12 维度审计扫描器套件（`script_manifest.yaml` 记录），入口 `run_all.py`，~60 秒全量扫描。退出码：0=通过 / 1=警告 / 2=阻断 / 3=崩溃。

<!-- AUTO-START:governance_script_counts -->
| 维度 | 职责 | 脚本数 |
|------|------|--------|
| d10_performance | 性能基准 / Performance benchmark | 1 |
| d11_compliance | 合规检查 / Compliance check | 24 |
| d12_ai_hallucination | d12_ai_hallucination / d12_ai_hallucination | 4 |
| d1_structure | 目录结构验证 / Directory structure | 25 |
| d2_links | 断链检测 / Broken link detection | 2 |
| d3_metadata | frontmatter 校验 / Frontmatter validation | 26 |
| d4_paths | 路径守卫 / Path guard | 4 |
| d5_architecture | 架构合规（最大） / Architecture compliance (largest) | 13 |
| d6_security | 安全扫描 / Security scan | 15 |
| d7_code | d7_code / d7_code | 41 |
| d8_doc_sync | 文档一致性 / Doc consistency | 14 |
| d9_knowledge | 知识库 / Knowledge base | 2 |
| data_quality | data_quality / data_quality | 2 |
| **合计** | **Total** | **173** |
<!-- AUTO-END:governance_script_counts -->

## 7. 基础设施件（永久系统）

| 组件 | 文件 | 职责 |
|------|------|------|
| `CostTracker` | `infrastructure/cost_tracker.py` | AI Agent 执行成本追踪（token/API/费用，日预算告警） |
| `EventStore` | `infrastructure/event_store.py` | 不可篡改审计日志（SQLite WAL + SHA256） |
| `SLAMonitor` | `infrastructure/sla/sla_monitor.py` | RTO/RPO 自动记录（事件驱动） |
| `EventBus` | `shared/event_bus.py` | 异步事件总线 + 背压（CAP-006=500 队列） |

## 8. 外部权威源

| 权威源 | 内容 | 路径 |
|--------|------|------|
| 治理报告 | 容量/约束违反/设计 vs 运营态 | `docs/02_enterprise_architecture/03_governance_reports/` |
| 全景注册表 | 全 registry 总索引 | `docs/02_enterprise_architecture/00_overview_entry/panorama_registry.md` |

> 治理原则（三层边界/D2-B/D3-B/D4）由 `architecture_model/governance_systems_registry.yaml` 强制执行（原 governance_principles.md 已删 2026-07-30，git 历史可查）。
