---
ttl: task_bound
completes_when: 退役自动化 P2-P4（pre-commit 挂门/trae_032 修正/successor 双写）落地
created: 2026-10-07
sid: st-mastertc-l9
status: 重建骨架
reconstruction: 本簿原件蒸发（S1-S9 九簿中未落地四簿之一），本件为重建版骨架
---

# S9 模块退役自动化 — 重建骨架 README

> **终态声明：本簿为重建版，原件蒸发**（挖矿波产簿未落地即失；本件 2026-10-07 由 st-mastertc-l9 按 HEAD 在册资产重建，目录名 S9_retire_automation 为重建命名，原件名不可考）。Owner 2026-09-27 深夜增补令设线。

## 本线范围（B10）

模块退役全自动化：检测、标准、流程、接线四缺补齐——MLC-003 退役七步执行器 + 退役候选机械判定 + IFC-007 契约级联 + 生命周期转换门。

## 交付物指针（HEAD 在册实证，B10-P1 已落地）

| 资产 | 路径 |
|---|---|
| 四路机械探测器 | scripts/governance/d5_architecture/lifecycle/detect_retirement_candidates.py |
| MLC-003 七步执行器（--execute 缺 owner-ruling 硬拒） | scripts/governance/d5_architecture/lifecycle/retire_module.py |
| retirement_records 账本 | architecture_model/module_id_registry.yaml（retirement_records 节） |
| 生命周期转换门 | PS-VOC-027 next_states（经 ROOR/规则册解析） |

## 首份退役候选情报（在案读数）

严格候选 0 / 观察名单 10 / P0 提示 1（99_delivery_report §四）。

## 残余与移交（P2-P4 处方在案，禁车道代裁）

1. P2：.pre-commit 挂门（退役探测进提交链）。
2. P3：trae_032 修正批五件 + step7 契约级联启用=**需 Owner 批文**（B10-P3 处方已备）。
3. P4：successor 双写（经 S5 处方 librarian 通道，lib_assets.successor_of）。
