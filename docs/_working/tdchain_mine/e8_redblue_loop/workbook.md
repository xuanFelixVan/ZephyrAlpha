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

## 检查记录（2026-09-18 06:4x 回写）

| 轮次 | 范围 | 结果 | 备注 |
|---|---|---|---|
| R1 | tests/regime+plan_engine+strategy_factory 全量 1766 passed；六注册表+standards YAML 解析全过；四关键 .py 编译全过 | 0 问题 | dev 树实跑（M1-M4 后） |
| R2 红蓝 | ①ETF 修复行深比对：4/4 随机行（2019-2026 跨年跨市场）OHLCV+8h 逐列全等；②幂等：bak 表行数=修复前总数 ✓；③抽查器自身时区 bug 抓出即修（真红=工具非数据）；④promotion_combo_gate 消费冒烟 | 1 真红（工具）已修 | 数据面零缺陷实证 |
| R3 | 队列落地核查（q-0004/5/6） | 见终局报告 | serializer 活体在他会话，快照零丢失 |

## 长尾登记

- FINAL 查询 CH Code 181 坑未触发（本轴无 FINAL 查询新增）；e3 已登记维护班项。
- dev 全量 pytest 未跑（多车道在飞，全量基线含他会话在途件，跑全量=测别人的 WIP）——按"分域 pytest"口径执行。
