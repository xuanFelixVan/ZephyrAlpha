---
module_id: KE-1738-------------------------d-000
status: active
title: 2.19 冷启动策略——零基线状态下的漂移检测引导（决策 D-023-33）
category: module_blueprint
---

# 2.19 冷启动策略——零基线状态下的漂移检测引导（决策 D-023-33）

2.19 冷启动策略——零基线状态下的漂移检测引导（决策 D-023-33）

> **决策 D-023-33**：Drift detector 首次运行时没有基线、没有 drift_events 历史、没有关联数据。不能要求先人工创建基线再开始工作——需要在"先信任当前状态为 known-good"的假设下自动引导。冷启动分三步：扫描→信任→建立基线。
>
> **决策依据**：1500 模块上线第一天，不能要求 Owner 逐个确认基线。自动信任当前 HEAD 为初始基线——后续漂移检测从此基线开始。

```yaml
cold_start:
  phase_1_bootstrap_scan:
    description: "首次运行——全量 DEEP scan 但模式为 BOOTSTRAP"
    behavior:
      - "运行所有检测器——但结果只记录为 INITIAL_BASELINE，不标记为 DETECTED"
      - "不消耗漂移预算"
      - "不触发告警"
    output: "COLD_START_REPORT: {N} 个问题在初始状态中已存在——不是漂移，是'遗产债务'"

  phase_2_trust_establishment:
    description: "Owner 审查 COLD_START_REPORT → 两种选择"
    option_a: "ACCEPT_CURRENT——接受当前状态为初始基线（known-good）"
    option_b: "DECLARE_DEBT——标记特定问题为 LEGACY_DEBT（已知债务，不计入预算，但持续追踪）"

  phase_3_baseline_creation:
    description: "初始基线拍摄——从此开始正常漂移检测生命周期"
    trigger: "Owner 完成 phase 2 审查"
    action: "拍摄全量基线快照 → 漂移状态机进入正常模式"

  re_bootstrap:
    description: "若 drift_events.db 损坏或丢失 → 触发重新冷启动"
    detection: "drift_events.db 不存在 或 所有 baseline 快照丢失"
    action: "保留旧数据到 backup → 重新执行冷启动流程"

  shallow_clone_awareness:
    description: "检测 git 是否为 shallow clone（git rev-parse --is-shallow-repository）"
    impact: "shallow clone → git bisect 不可用 → 禁用溯源功能 → 通知 Owner"
    resolution: "提示 Owner 运行 git fetch --unshallow 或接受无溯源模式"
```
