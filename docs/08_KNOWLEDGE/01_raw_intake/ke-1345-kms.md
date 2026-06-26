---
module_id: KE-1257-------kms-004
status: active
title: ZephyrAlpha 5 级门禁策略（KMS 知识管道门禁体系）
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# ZephyrAlpha 5 级门禁策略（KMS 知识管道门禁体系）

ZephyrAlpha 5 级门禁策略（KMS 知识管道门禁体系）

> **本文件定位**：`zephyr.gates.gate_engine`（T-2-17，`src/zephyr/gates/gate_engine.py`）与 `g1~g5.yaml` 策略文件的**唯一权威策略 SSoT**。门禁触发条件、检查项、裁决逻辑、YAML schema、与 `task_repo` 状态机的集成边界，均以本文件为准。
>
> **适用范围**：KMS（Knowledge Management System）知识管道全过程 —— 从外部文档被管道吸入，到最终被提取成知识条目并激活入库。
>
> **不覆盖范围**：生命周期横切守卫（pre-commit hooks、Sentinel 扫描、Pydantic 契约校验、ATM 原子写入、运行时观测）不属于本 5 级门禁，归类为 **Lifecycle Guards**，见本文附录 A"与 Lifecycle Guards 的边界"。
>
> **版本说明**：v2.0.0 替换 v1.0.0（B10 session 权宜版）。原版本将 5 级门禁错位定义为 `Write/Commit/Phase/Contract/Runtime`，与 `gate_engine.py` 加载的 `g1_ingest~g5-extract.yaml` 语义不一致。本版本以**代码实现**为锚定点重新定义门禁语义。v2.1.0：2026-05-01 从 `02_enterprise_architecture/` 迁移至 `01_policies_and_standards/governance/architecture/`（`standard` 类文档按 PS-STD-001 §3.4 规定归入治理目录）。

---
