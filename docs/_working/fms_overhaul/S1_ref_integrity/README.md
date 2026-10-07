---
ttl: task_bound
completes_when: FMS-HYGIENE 基线清偿过半（棘轮判据改写案裁定后）或本线归档
created: 2026-10-07
sid: st-mastertc-l9
status: 重建骨架
reconstruction: 本簿原件蒸发（S1-S9 九簿中未落地四簿之一），本件为重建版骨架
---

# S1 引用完整性 — 重建骨架 README

> **终态声明：本簿为重建版，原件蒸发**（2026-09-27 挖矿波产簿未落地即失；本件 2026-10-07 由 st-mastertc-l9 按 HEAD 在册资产重建，目录名 S1_ref_integrity 为重建命名，原件名不可考）。

## 本线范围（B1+B2）

全仓 docs 树 md/yaml 死引用治理：FMS-HYGIENE 门四查类（死引用棘轮基线/ASCII 新路径/永久区引临时区/CAS 残渣）+ C 类唯一可修引用的批改写清偿。

## 交付物指针（HEAD 在册实证）

| 资产 | 路径 |
|---|---|
| 棘轮基线册（机生禁手改） | docs/01_policies_and_standards/_registry/catalogs/fms_deadref_baseline.yaml |
| 基线生成器（唯一写者） | scripts/governance/generators/generate_fms_deadref_baseline.py |
| 门本体+提取器（共享 SSoT） | src/zephyr/gov_enforcement/commit_gates/read_side/fms_hygiene_gate.py + fms_ref_extractor.py |
| 死引用总清单（2,498 实测） | docs/_working/fms_overhaul/_data/deadref_missing_2498.csv |
| C 类清偿映射（412 行） | docs/_working/fms_overhaul/_data/deadref_fix_map.csv（**2026-10-07 C161 已批注 verdict：resolved 348 / pending 64**） |
| 非 ASCII 基线（126 条） | docs/_working/fms_overhaul/_data/non_ascii_paths.csv |

## 关键判据在案（收尾波结论，出处=99_delivery_report §十二）

基线 3,702 条实测分布 D1801/E3 906/B853/A136/C2=6，机械可修面≈554 条=15%——「存量过半清偿」判据不可达，门恒 warn；改提「连续 20 笔提交新增违规=0」替代案待裁（X2 处方+收尾 §十二）。FMS-REGEN-CLEAN 不进 pre-commit，挂事件核对链（X2_gate_wiring_prescription.md）。

## 残余与移交

- C 类 pending 64 行（fix_map verdict=pending）=目标文件未落地，随 B2 后续清偿批。
- 替代案裁定→L10/Owner 门位；本骨架只登记不代裁。
