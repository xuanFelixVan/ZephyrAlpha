---
ttl: task_bound
title: E8 红蓝对抗+循环检查作业簿——连续两次 0 问题门
session: st-tdchain-20260917
date: 2026-09-18
parent: docs/_working/tdchain_mine/a0_master_ledger.md
---

# E8 红蓝对抗+循环检查作业簿

## 六向台账

- **目标**：Owner 通宵令第五条——全部环节完工后：循环检查×2（连续两次 0 问题才收口）→红蓝对抗（测出即修）→与 E7 组成端到端闭环。
- **证据（攻击面清单，按本轴交付物定制）**：
  - 合并面（E0）：五路合并后 import 完整性（promotion_combo_gate 缺 import 先例 383c0af8e1）——pytest 受影响域+关键 CLI --help 冒烟。
  - 数据面（E1）：修复幂等（重跑 dry-run 应报 0 行）；板块回灌 OHLC 抽样（open=首 1m open/high=max/low=min/close=末 1m close）；备份表行数对账。
  - regime 面（E3）：tests/regime 全绿；FINAL 查询探针（CH Code 181 坑登记项，只登记不触发服务端崩溃）。
  - 判据面（E6）：flip 后 standards.yaml YAML 解析+双尺打分器消费 standards 的测试。
  - 文档面：TTL/命名/token 门禁全过（提交即验）。
  - 检出率门（#324）：红蓝套件检出率≥0.95（若触发既有 test_rule_red_blue 套件按其门位跑）。
- **块**：R1 循环检查第 1 轮（分域 pytest+冒烟+产物目检）→R2 修复→R1' 第 2 轮（连续 0 问题）→R3 红蓝子代理攻击（输入异常/空数据/CH 断连/幂等重跑/路径越界）→R4 修复+复测。
- **依赖**：E0-E7 全部收口。
- **三态**：待 W1/W2。
- **下一步**：W3 执行，结果回写 §检查记录。

## 检查记录（回写区）

| 轮次 | 范围 | 结果 | 修复 commit |
|---|---|---|---|
| R1 | | | |
| R2 | | | |
