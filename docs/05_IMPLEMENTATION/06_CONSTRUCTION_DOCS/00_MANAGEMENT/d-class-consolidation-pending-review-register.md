---
module_id: D_CLASS_CONSOLIDATION_PENDING_REVIEW_REGISTER_001
version: 1.0.5
status: Active
created_date: 2026-04-11
last_updated: '2026-04-11'
owner: 仓库 Owner
responsibility:
  - 登记「低置信」D 类合稿：新稿路径、旧稿 stub/归档位置，供后续统一审核
standard_type: 登记表
applicable_scope: D 类合稿 — **仅低置信**分支（见 D 类蓝图重叠 Playbook **§2.5** 置信度分级、**§5** 双轨）
layer: layer_05
---


# D 类合稿 — 待统一审核登记（低置信分支）

> **用途**：机器生成 `*_CONSOLIDATED_YYYYMMDD.md`（或等价新路径）后，**旧稿不删**（stub 或正文迁 archive + 原路径 stub）。本表集中记录 **待你后审** 的条目，避免散落在 commit message 里找不到。
> **高置信**合并 **不登记本表**（准入与「高置信可合并」见 Playbook **§2.5.2**、收口形态 **§5.1**）；若仍希望留审计痕，可写在 commit body 或 `docs/09_AUDIT/STATE/` 简短日志。
> **机器候选池（启发式）**：最新 `BLUEPRINT_D_OVERLAP_CANDIDATES_20260412.md`（[`JSON`](../../../09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_CANDIDATES_20260412.json)）。可选 **A 档分流 + 二审队列**：`BLUEPRINT_D_OVERLAP_TRIAGE_20260412.md`（[`.json`](../../../09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_TRIAGE_20260412.json)）、[`BLUEPRINT_D_OVERLAP_SECOND_PASS_QUEUE_20260412.jsonl`](../../../09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_SECOND_PASS_QUEUE_20260412.jsonl)（脚本 `triage_blueprint_d_overlap_pairs.py`，Playbook **§3.5**）；更强模型二审配合 二审提示词模板（输出 `confidence`、`low_confidence_register` 等，与 Playbook **§2.5** 对齐）。评审顺序与双轨见 D 类蓝图重叠 Playbook。

## 列说明

**「一点就跳」**：**合稿新路径**、**旧稿路径**、**旧正文归档**（有文件时）三列请写 **Markdown 链接**（方括号内为显示文字，紧接圆括号内为从本文件起算的相对路径）。
**相对路径以本登记表文件所在目录为基准**（即与 `D_CLASS_CONSOLIDATION_PENDING_REVIEW_REGISTER.md` 同级起算的 `../`、`../../` 等），这样在 IDE / GitHub / 飞书文档渲染里均可点击打开目标稿。
显示文字建议含短文件名或 `stub` / `archive` 提示；无归档时 **旧正文归档** 列仍填 `-`（纯文字即可）。

| 列 | 含义 |
|----|------|
| **批次** | 如 `20260411-D3` |
| **合稿新路径** | 新稿：与下表「登记行」同列格式；合稿文件尚未落盘时请写**纯文字路径**，勿留死链。 |
| **旧稿路径** | 仍为 stub 的原路径：可点击链至 `../01_BLUEPRINTS/` 下真实 stub。 |
| **旧正文归档** | 长文若在 archive：链至 `../../../06_ARCHIVE/...` 下真实文件；否则 `-`。 |
| **状态** | `pending_review` / `accepted` / `reverted` / `superseded` |
| **备注** | 候选 score、涉及文档、PR 号等 |

## 登记行（在表末追加）

| 批次 | 合稿新路径 | 旧稿路径 | 旧正文归档 | 状态 | 备注 |
|------|------------|----------|------------|------|------|
| _示例_ | `../01_BLUEPRINTS/EXECUTION_STRATEGY_BACKTESTER_CONSOLIDATED_20260411.md`（占位文件名，待产出后改为可点击链） | EXECUTION_STRATEGY_BACKTESTER_BLUEPRINT（stub） | - | pending_review | **语法演示**：合稿列在文件未入库前用反引号路径避免 L1 死链；stub 列为真实可点链。 |

```
```---
```

## 版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.5 | 2026-04-11 | 文首与 `applicable_scope` 互指 Playbook **§2.5**（置信度与「高置信可合并」）、二审字段与 **§5.1** |
| 1.0.4 | 2026-04-10 | 文首互指 `TRIAGE_*`、`SECOND_PASS_QUEUE_*.jsonl`、二审模板 与 Playbook **§3.5** |
| 1.0.3 | 2026-04-12 | 文首互指最新 `BLUEPRINT_D_OVERLAP_CANDIDATES_20260412` 与 Playbook |
| 1.0.2 | 2026-04-11 | 去除会被 L1 判无效的示例死链与字面 `](相对路径)`；列说明改叙述；示例合稿列改用反引号占位路径 |
| 1.0.1 | 2026-04-10 | 列说明与示例行改为 Markdown 相对链接，支持「一点就跳」 |
| 1.0.0 | 2026-04-11 | 首版：低置信合稿待审台账 |
