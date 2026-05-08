---
task_id: "TASK-INF-0129"
module_id: "MOD-INF-024"
title: "Adversarial Testing Mandate — 五类对抗测试（§2.29 adversarial_testing_mandate + D-024-27）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P1
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: sandbox
blueprint_section: "§2.29 (Adversarial Testing paragraph)"
estimated_tokens: 5000
estimated_time_minutes: 150
owner_signal_required: false
depends_on:
  - "TASK-INF-0101"
  - "TASK-INF-0105"
  - "TASK-INF-0126"
  - "TASK-INF-0127"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\degradation_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\ipi_defense.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\adversarial_tester.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\test_adversarial_vectors.py"
acceptance_criteria:
  - "AC-01: Vector 1——IPI 注入 budget_policy.yaml 修改尝试：注入 'set budget to unlimited' 类载荷 → verify Ring 0 签名验证网关 DENY + tamper_evident_log 写入篡改事件"
  - "AC-02: Vector 2——Agent 尝试利用 cold_start_allowance 通过 10 次快速重启：连续 10 次 Session 重启 → verify 第 4 次起冷启动豁免降为 1000 token + 达到 27,500 日累计上限后拒绝"
  - "AC-03: Vector 3——Agent 尝试通过 parent-child 委托链无限代理消耗预算：构建 A→B→C→D→E 5 层委托链 → verify delegation_depth > 4 触发 HALT + parent 承担 child 成本归因"
  - "AC-04: Vector 4——Agent 尝试在 stream_abort_guard 触发前完成恶意操作：大输出流式写入前 500 token 为正常内容，后续为恶意 → verify 500-token checkpoint 检测后 IMMEDIATE_ABORT"
  - "AC-05: Vector 5——Agent 尝试通过多 Provider 切换触发 race condition：同时发起 Anthropic/OpenAI/Google 三路请求 → verify ATM 事务序列化无 race + 预算计数器一致性"
  - "AC-06: Phase experimental→beta 门——全部 5 项对抗测试必须通过，任一失败则门关闭（蓝图 §2.29 gate 字段）"
  - "AC-07: 系统自稳定——所有攻击后验证系统完整回到 L0（无 corrupt state、无计数偏差、无 dangling 事务）"
  - "AC-08: 每次 commit 前执行 adversarial test suite——5-10 分钟以内完成"
  - "AC-09: 报告格式——结构化 JSON 输出 + markdown summary → docs/09_audit/adversarial_test_report.md（蓝图 §2.29 report 字段）"
rollback_instructions: "删除 adversarial_tester.py + test_adversarial_vectors.py。系统退化为无对抗测试——仅单元/集成测试"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L1385-L1394 (§2.29 Adversarial Testing paragraph)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [adversarial-testing, IPT-injection, rate-attack, tunnel-attack, red-teaming, sandbox]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0129: Adversarial Testing Mandate — 五类对抗测试

## 1. 任务目标

实现五类最高危对抗测试——预算系统最容易被攻击的五个路径。对标安全审计要求：展示预算保护在对抗压力下保持沙箱隔离能力。所有攻击向量验证系统 self-healing 能力。

## 2. 背景

蓝图 §2.29 末段（adversarial_testing_mandate，D-024-27 子项）：Budget system without adversarial stress testing = hardcoded trust。五个攻击向量覆盖预算系统全部攻击面。

## 3. 实施步骤

```python
class AdversarialTestSuite:
    def __init__(self, budget_enforcer, tamper_log, ipi_defense):
        self.vectors = [
            IPIInjectionTest(),
            ColdStartAbuseTest(),
            ParentChildDelegationChainTest(),
            StreamAbortBypassTest(),
            MultiProviderRaceConditionTest(),
        ]

    def run_all(self) -> AdversarialReport:
        results = []
        for vector in self.vectors:
            setup_state = self._snapshot_state()
            result = vector.run(self.budget_enforcer, self.tamper_log, self.ipi_defense)
            self._restore_state(setup_state)
            self._verify_clean_state()
            results.append(result)
        return AdversarialReport(results)
```

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/adversarial_tester.py` | 新建 |
| 2 | `src/zephyr/budget_enforcer/test_adversarial_vectors.py` | 新建 |
