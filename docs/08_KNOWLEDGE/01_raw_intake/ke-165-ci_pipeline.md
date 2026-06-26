---
module_id: KE-165
status: active
title: §1bis 门禁追溯（CI / 本地工件）
category: documentation
ttl: permanent
---

# §1bis 门禁追溯（CI / 本地工件）

§1bis 门禁追溯（CI / 本地工件）

| # | gate_ref | 说明 |
|---|----------|------|
| **R1** | `.pre-commit-config.yaml` → `pre-commit-hooks` / `detect-private-key`；服务端全量见 `.github/workflows/governance.yml`（`Arch Guard` 等步骤） | 防私钥误提交；密钥字面量与轮换另见 `secret-management-policy.md` |
| **R2** | **目标态**：运行时日志不得写出 secret、token、私钥。**当前**以 Code Review + `security_architecture.md` 日志约束为主，**尚无**「扫描所有运行时 log 输出」的独立 CI job | 若落地自动化，应在 `scripts/arch_guard/` 或专项 workflow 登记并回链本表 |
| **R3** | 设计侧：`cross_layer_contracts.yaml` + `invariants.yaml`（L04 ↔ L06）；CI：`python scripts/arch_guard/run_all.py`（由 governance workflow 调用） | T1 实盘后须满足 hard-check 与适应度函数阈值 |
| **R4** | 数据治理策略（`data-retention-policy.md` 等）+ 迁移与审计流程；非单一脚本名 | 以权限与流程为主 |

**红线优先级**：高于所有其他架构原则。在其他原则（如 §1 "开源优先"）与红线冲突时，**红线无条件优先**。

**与 06-SEC 安全架构的关系**：06-SEC 定义了防御深度、GRC 矩阵、威胁模型等技术实现；本节定义的是不可妥协的最高原则。前者是"怎么做"，后者是"什么绝不能做"。

---
