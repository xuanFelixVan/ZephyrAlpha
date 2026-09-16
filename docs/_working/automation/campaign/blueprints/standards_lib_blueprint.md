---
ttl: task_bound
completes_when: 模块晋升 docs/03_modules（H-01 解冻）或工单废弃
---

# MOD-AUTO-L5-001（暂编号）standards_lib 蓝图

## 定位

骨架 §8 治理底板执行件：考纲标准库（config/standards.yaml）加载器 + 修标重考历史核心（regrade_diff）。三原则落地：版本化 / draft 不得作生效考纲 / 修标须输出翻转清单供治理层审。

## ALGO_FLOW

- I1: config/standards.yaml（std_id/version/status/thresholds/change_rule）
- A1: load_standards（frozen 标记）
- A2: get_frozen_thresholds（draft 拒绝作生效考纲）
- A3: regrade_diff（新旧尺子×候选→裁定翻转清单）
- O1: CLI 输出（check/regrade）

## 消费方

promotion_combo_gate（阈值切换点）、AI 层修标提案流水线（未来）、Owner 修宪评审。
