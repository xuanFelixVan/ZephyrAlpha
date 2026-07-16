---
blueprint_id: MOD-INF-005
ttl: task_bound
doc_type: index
---

# 脚本系统 — 人类维护者速览卡片

> **不看这个你 6 个月后回来完全不知道发生了什么事。**

---

## 这个系统是什么

**ZephyrAlpha 的自动化治理基础设施** = 12维度扫描 × C1-C5五阶段 × Finding Schema × 73+脚本统一编排 × 自我审计。

你的角色：**1 人 Owner**。维护搭档：**AI Agent（Claude/Cursor）**。

## 我离开 6 个月了，现在该干什么

```bash
# 1. 先看系统还在不在
python scripts/governance/meta/validate_script_system_health.py

# 2. 全量扫一次看有多少新问题
python scripts/governance/run_all.py --output meta/quick_check.jsonl

# 3. 对比上次基线看是变好了还是变坏了
python scripts/governance/meta/manage_baseline.py --compare meta/quick_check.jsonl

# 4. 看趋势
python scripts/governance/meta/manage_finding_timeseries.py --trend 90d
```

## 这个系统跟上次我离开时有什么变化

```bash
# 检查有没有人（或AI）悄悄改了规则文件
python scripts/governance/meta/validate_rules_integrity.py --check

# 看哪些脚本是新来的、谁写的
python scripts/governance/meta/validate_script_provenance.py --list

# 看AI维护花了多少钱
python scripts/governance/meta/track_script_costs.py --report
```

## 核心阈值——改了这些会炸

| 阈值 | 在哪个文件 | 当前值 | 含义 |
|------|-----------|--------|------|
| 假阳性率上限 | `_shared/thresholds.yaml` → finding_quality | 5% | 超过 = Error Budget 消耗 |
| AST 相似度 | `_shared/thresholds.yaml` → ast_similarity | 0.80 | 新脚本与已有脚本 > 80% → 视为重复 |
| CRITICAL 修复截止 | `_shared/thresholds.yaml` → sla_timers | 24h | 24小时不修复 → OVERDUE |
| Error Budget 窗口 | `meta/error_budget_state.yaml` | 30天 | 30天自动重置 |
| Burn Rate 1h告警 | `_shared/thresholds.yaml` → error_budget | 2% | 1h 消耗 > 2% → Feature Freeze |
| Feature Freeze 解冻 | `_shared/thresholds.yaml` → error_budget | 72h | 自动解冻前你要确认是安全的 |

## 紧急操作

```bash
# 某个脚本发疯疯狂误报 → 暂停它
python scripts/governance/meta/manage_kill_switch.py --disable <script_path> --reason "误报过高"

# 全局冻结 → 所有新脚本开发停下来
python scripts/governance/meta/manage_kill_switch.py --global-freeze --reason "生产事故"

# 解冻
python scripts/governance/meta/manage_kill_switch.py --global-thaw

# 某个脚本该退役了
python scripts/governance/meta/manage_script_retirement.py --retire <script_path>
```

## 给新 AI session 看什么

让它先读 `scripts/governance/quickstart.md`（≤500 tokens），再让它 `python scripts/governance/run_all.py --list` 看全貌。
