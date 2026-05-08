---
module_id: KE-governance-1_2bis_runtime_plane______v1_2-003
title: 1.2bis Runtime Plane 边界铁律（v1.2.0，R69 / J1 批次）
category: governance
---

# 1.2bis Runtime Plane 边界铁律（v1.2.0，R69 / J1 批次）

1.2bis Runtime Plane 边界铁律（v1.2.0，R69 / J1 批次）

**关键澄清**：04bis 的**三运行平面**（Hot/Warm/Cold）与本视图的**治理三层**（Policy/Factory/**Runtime**）**名字都叫 "Runtime" 但意义完全不同**，二者正交独立：

| 维度 | 09-GOV Runtime 层 | 04bis Runtime Plane |
|---|---|---|
| **切片维度** | 治理维度（谁管规则）| 执行维度（代码何时以什么延迟跑）|
| **切片方式** | 按规则生命周期切（Policy/Factory/**Runtime**）| 按延迟预算切（Hot<10ms / Warm / Cold>1s）|
| **所有 Plane 都有治理 Runtime？** | — | **是**（Hot=C++ OPA / Warm=Python 拦截 / Cold=Airflow hook）|
| **Policy 层的 Plane？** | — | **无**（规则文本不执行）|
| **Factory 层的 Plane？** | — | **Cold**（linter/编译器在构建期批量执行）|

**联合引用必须使用双标签语法**（详见 04bis §7.3）：`[GOV:Runtime] × [Plane:Hot]`

**禁止**：单独使用 "Runtime" 一词——必须带限定词（"Runtime 层" 指治理 / "Runtime Plane" 指执行）。
