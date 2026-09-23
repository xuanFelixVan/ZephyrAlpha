---
ttl: task_bound
completes_when: 随 tdm20 战役归档（探测器再跑即刷新本件）
title: chain_refs 双向对账首跑报告（st-tdm20-20260923 W4）
owner: st-tdm20-20260923
session: st-tdm20-20260923
date: 2026-09-23
---

# chain_refs 双向对账首跑报告（st-tdm20-20260923 W4）

> 生成: scripts/governance/reconcile_chain_refs.py @ 2026-09-22T23:54:24Z（UTC）
> 纪律=只报不清：本报告是遗漏探测器读数，不做任何删除/清理/改写。

## 读数

- 正向（图→库）：TDM chain_refs 引用合计 **8** 条，断链 **0** 条（须为 0）
- 反向（库→图）：有效链（covered，w4_1 triage canonical 口径）**583** / 873；其中被图引用 **8** 条，未引用 **575** 条（=传导链吸收遗漏读数，只报不清）
- 资产面：挂 chain_refs 的 TDM 节点 **1** / 182（无标记节点数=181=资产遗漏探测读数）
- 值域健康：chain_registry 在册 **873** 链（生成器=scripts/governance/generate_chain_registry.py，禁手改）
- PG 实库复核：canonical 覆盖数=583（与注册表 covered 口径一致）

## 节点引用明细

- TDM-E-L9-G1: 8 条（CH-985a1b1852e5, CH-c4902e175ffb, CH-dccc45c14a88, CH-6a82b10e0891…）
