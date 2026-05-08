---
doc_type: index
status: active
title: "DOM-GOV-001 — 目录索引"
version: "1.1.0"
created: "2026-05-06"
updated: "2026-05-07"
---

# DOM-GOV-001

## 目录内容

| 文件/目录 | 类型 | 说明 |
|-----------|------|------|
| [TASK-GOV-0001.md](TASK-GOV-0001.md) | Markdown | 创建治理域模块骨架——目录结构 + __init__.py + 模块清单初始化 |
| [TASK-GOV-0002.md](TASK-GOV-0002.md) | Markdown | 实现 G-CT-001：MOD-INF-018 (RBAC) → MOD-INF-020 (Audit) 集成契约 |
| [TASK-GOV-0003.md](TASK-GOV-0003.md) | Markdown | 实现 G-CT-002：MOD-INF-020 (Audit) → MOD-INF-021 (Rollback) 集成契约 |
| [TASK-GOV-0004.md](TASK-GOV-0004.md) | Markdown | 实现 G-CT-003：MOD-INF-021 (Rollback) → MOD-INF-022 (Escalation) 集成契约 |
| [TASK-GOV-0005.md](TASK-GOV-0005.md) | Markdown | 实现 G-CT-004：MOD-INF-022 (Escalation) → MOD-INF-018 (RBAC) 集成契约 |
| [TASK-GOV-0006.md](TASK-GOV-0006.md) | Markdown | 实现 G-CT-005：MOD-INF-023 (Drift) → MOD-INF-021 (Rollback) 集成契约 |
| [TASK-GOV-0007.md](TASK-GOV-0007.md) | Markdown | 实现 G-CT-006：MOD-INF-024 (Budget) → MOD-INF-022 (Escalation) 集成契约 |
| [TASK-GOV-0008.md](TASK-GOV-0008.md) | Markdown | 实现 G-CT-007：MOD-INF-019 (Agent Spec) → MOD-INF-018 (RBAC) + MOD-INF-020 (Audit) 集成契约 |
| [TASK-GOV-0009.md](TASK-GOV-0009.md) | Markdown | 实现 G-CT-008：MOD-INF-025 (A2A) → MOD-INF-018 (RBAC) + MOD-INF-022 (Escalation) 集成契约——仅契约定义，Phase 4 Hold |
| [TASK-GOV-0010.md](TASK-GOV-0010.md) | Markdown | Phase 1 施工启动门禁：Audit Trail + Agent RBAC——验证 G-CT-001 契约实现就绪 |
| [TASK-GOV-0011.md](TASK-GOV-0011.md) | Markdown | Phase 2 施工启动门禁：Rollback System + Escalation Protocol——验证 G-CT-002/003/004 契约实现就绪 |
| [TASK-GOV-0012.md](TASK-GOV-0012.md) | Markdown | Phase 3 施工启动门禁：Drift Detector + Budget Enforcer——验证 G-CT-005/006 契约实现就绪 |
| [TASK-GOV-0013.md](TASK-GOV-0013.md) | Markdown | Phase 4 施工启动门禁：Agent Spec + A2A Protocol——验证 G-CT-007/008 契约实现就绪 |
| [TASK-GOV-0014.md](TASK-GOV-0014.md) | Markdown | 实现 §5 循环依赖裁决：Audit 不依赖 RBAC——仅 RBAC 单向调用 Audit |
| [TASK-GOV-0015.md](TASK-GOV-0015.md) | Markdown | G-CT 下游锚点验证：检查 8 个 L01 模块均已落锚 DOM-GOV-001 契约 |
| [TASK-GOV-0016.md](TASK-GOV-0016.md) | Markdown | 风险 R1 缓解：建立治理域 Phase 0——8 模块蓝图与契约落地为最小可用实现 |
| [TASK-GOV-0017.md](TASK-GOV-0017.md) | Markdown | 风险 R2 缓解：RBAC/Audit 循环依赖打破验证——确保全链路单向依赖 |
| [TASK-GOV-0018.md](TASK-GOV-0018.md) | Markdown | 风险 R3 缓解：A2A Protocol Phase 4 Hold 标记——确保 G-CT-007 先行、A2A 不提前 |
| [TASK-GOV-0019.md](TASK-GOV-0019.md) | Markdown | 实现 §8 P0 测试用例：P0-U1 冒烟测试 + P0-U2 输入校验 + P0-I1 集成测试 + P0-I2 施工顺序验证 |
| [TASK-GOV-0020.md](TASK-GOV-0020.md) | Markdown | §2 模块清单进度追踪 + §7 变更记录——治理域施工进度看板更新与变更管理 |
| [TASK-GOV-0021.md](TASK-GOV-0021.md) | Markdown | 依赖验证：SYS-MASTER-001 系统总蓝图 + MOD-MASTER-001 基建域蓝图 CT 交叉检查 |
| [TASK-GOV-0022.md](TASK-GOV-0022.md) | Markdown | d5_architecture 根目录重复脚本清理 + test_all_scripts 分层改造 |
| [completeness-report.md](completeness-report.md) | Markdown | 蓝图分解完整性报告 · 二次审计版 |
| [dependency_crosscheck.md](dependency_crosscheck.md) | Markdown | DOM-GOV-001 依赖交叉检查（SYS-MASTER-001 + MOD-MASTER-001 vs DOM-GOV-001） |
| [downstream-anchor-report.md](downstream-anchor-report.md) | Markdown | DOM-GOV-001 下游锚点报告（Phase 3 施工状态） |

## 导航

- [上级目录](../index.md)
- [项目根](../../index.md)
