---
task_id: "TASK-INF-0131"
module_id: "MOD-INF-024"
title: "Solo Maintainer Optimizations — 自学习阈值 + 自静默告警 + 周自动摘要 + 单线程降级（§3）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P1
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: self_calibrating
blueprint_section: "§3"
estimated_tokens: 4500
estimated_time_minutes: 150
owner_signal_required: false
depends_on:
  - "TASK-INF-0101"
  - "TASK-INF-0105"
  - "TASK-INF-0108"
  - "TASK-INF-0110"
  - "TASK-INF-0120"
  - "TASK-INF-0130"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\degradation_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\cost_attributor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\burn_rate_monitor.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\solo_maintainer.py"
  - "D:\\ZephyrAlpha\\docs\\09_audit\\cost_reports\\weekly-auto-summary.md"
acceptance_criteria:
  - "AC-01: self_learning_thresholds——基于 30 天历史消耗的 90th percentile + 15% buffer 自动更新 budget_policy.yaml 中的 soft_limit"
  - "AC-02: 学习时自动忽略 outlier spikes（Z-score > 3）——不因一次事故就把阈值永久抬高"
  - "AC-03: 每次更新写入变更理由 + actual_pXX_values + baseline_trend（可审计）"
  - "AC-04: auto_silence_alerts——同一告警 1 天内出现 5 次+ → 自动降级为 daily summary（不反复 ping Owner）"
  - "AC-05: daily digest（daily_summary）——每 24h 发送一条 5 行以内的 Slack/终端消息"
  - "AC-06: WeeklyAutoSummary——每周日生成一份 Markdown 报告（总览/异常/归因 Top3/ROI趋势/预测/建议/新模型）"
  - "AC-07: storage_path——docs/09_audit/cost_reports/weekly-auto-summary-{date}.md"
  - "AC-08: single_threaded_degradation——Solo 模式不允许并发降级协商，所有 Degradation Action 队列化"
  - "AC-09: 自监测任务负载——如果每周 > 500 活跃任务 → 触发拆分阈值（暂上报不提执行）"
  - "AC-10: Env Profile auto-sync——ide→dev 自动匹配 Profile 不弹窗确认"
rollback_instructions: "删除 solo_maintainer.py。系统退化为无 Solo 优化的多人模式——所有告警按标准频率，阈值需手动维护"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L1356-L1417 (§3 Solo Maintainer)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [solo-maintainer, self-learning, auto-silence, weekly-summary, single-threaded, self_calibrating]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0131: Solo Maintainer Optimizations

## 1. 任务目标

实现 Solo Maintainer（单人维护）的极致优化——没有运营团队，没有 on-call 轮班，一切需要系统自处理。四大能力：自学习阈值（auto-calibration）、自静默告警（auto-silence）、周自动摘要（auto-daily + weekly digest）、单线程降级队列。

## 2. 背景

蓝图 §3：在没有 SRE/FinOps 团队的情况下，Budget Enforcer 的三个"极简人"原则。对标 Solo maintainer tool budget 的日常体验设计。

## 3. 实施步骤

```python
class SoloMaintainer:
    def __init__(self, policy_manager, degradation_queue, alert_engine):
        self.learner = SelfLearningThresholds()
        self.silencer = AlertSilencer(daily_limit=5)
        self.summarizer = WeeklyAutoSummarizer()
        self.degradation_queue = SingleThreadDequeue()

    def on_task_complete(self, task_id: str, stats: TaskStats):
        # update self-learning model
        self.learner.record(stats)

    def on_alert_trigger(self, alert: Alert) -> bool:
        # decide whether to silence or forward
        return self.silencer.should_send(alert)

    def generate_weekly_summary(self) -> str:
        return self.summarizer.generate()

class SelfLearningThresholds:
    def update_thresholds(self, history: list[float]) -> dict[str, float]:
        # remove outliers (Z-score > 3)
        # calculate p90 of remaining
        # add 15% buffer
        # return new thresholds
```

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/solo_maintainer.py` | 新建 |
