---
ttl: task_bound
completes_when: the canonical-inheritance invariant is asserted by landed tests and the 567-entry translation collision backlog is explained as pre-fix damage
---

# 包 24 · 写手治本：`add_module_translation` 规范字段不再被缺省清空

## 病（一句话）

重登记同一个 `module_path` 时，调用方没给的那几个规范字段（`name_en` / `desc_zh` / `desc_en`）
会被**静默写成空串**——不是整条覆盖，是字段级蒸发。

## 复现（本窗实跑，改前）

```
entry = {module_path: 已存在, name_zh: 改, plain_zh: 新句, name_en: "", desc_zh: "", desc_en: ""}
_upsert_entry(在册 YAML, entry) →
  name_en: ""        ← 原 "Demo Mod"
  desc_zh: ""        ← 原 "这是一段已有的中文描述，信息量很高"
  desc_en: ""        ← 原 "an existing informative description"
  module_id / build_status / battle_map_steps 段：保留
```

机制两处合一才成立：`_upsert_entry` 合并旧块时把整族 `_CANONICAL_KEYS` `continue` 掉
（旧 L413），而 `_format_entry_block` 对规范字段用 `entry.get(k, '')`（L294-300）。
⇒ 文件头 `[INVARIANTS]` 原本只写了"**派生字段**永不从旧块继承"，旧实现把它做成了
"**规范字段+派生字段**都不继承"，是**实现超出在册不变量**的一次加严，代价是数据。

## 修

合并范围＝全部字段（含规范 7 字段），仍遵守两条既有例外：
`_DERIVED_KEYS`（`responsibility_layer` 只认 `--sync-layer` 重算，继承会让"映射已删域"的陈旧层值复活）
与 `module_path`（身份键）。仲裁不复发明：先把旧块喂给 `--dedupe` 已有的
`_merge_duplicate_blocks`（`L575-587`）合成"在册最优视图"，再**只填调用方缺省**，
调用方给的实值永远赢。⇒ 净零（没有第二套合并语义、没有新脚本、没有新旗标、没有新门禁台数）。

`[INVARIANTS]` 同步补一句："重登记同一 `module_path` 时规范字段的在册非空值永不因调用方缺省而被清空"。

## 判据（四条，先能红才算绿）

`tests/governance/d3_metadata/test_add_module_translation.py::TestUpsertCanonicalPreservation`

| # | 断言 | 改前 | 改后 |
|---|---|---|---|
| 1 | 缺省登记⇒`name_en/desc_zh/desc_en` 原样保留，且结果里**不得出现** `desc_zh: ""` | FAIL（三字段被清空） | PASS |
| 2 | 调用方显式给 `desc_zh` 新值⇒覆盖生效（修复不得变成"永远改不动"） | PASS | PASS |
| 3 | 派生字段 `responsibility_layer` 不得从旧块复活 | PASS | PASS |
| 4 | 扩展字段与 `entries:` 之外的顶层段（`battle_map_steps`）零损失 | PASS | PASS |

## 跑量

- 目标文件：`tests/governance/d3_metadata/test_add_module_translation.py` **46 passed**（改前 42 passed + 本包 4 条）。
- 邻域回归：`tests/governance/d3_metadata/` **205 passed**。
- `ruff check`：本包两文件 0 错误（顺带修掉 `test_stale_base_refused` 内联 import 的既有 I001 一处，
  因它与本包同文件，ruff-format 整档连坐会打死本袋）。

## 与本窗其它结论的关系

- 这条是 `storage_decision/ADJUDICATION_20260927.md` §四.1（"无论选谁都立刻做的事"第一条）。
  它证明"总台账要不要搬数据库"这个问题里，**至少这一类数据损失与存储引擎无关**。
- ⚠ 残余损失面（不在本包内，须由对账回答）：历史上被本缺陷清空的在册字段有多少？
  已知线索＝双轨对账最新报告 `REG-MODULE-TRANSLATION-001` 报
  `identity_collisions 567 / identity_collisions_diff_payload 567`
  （`.runtime/registry_ledger/dualtrack_20260926_234814.json`）——567 条身份撞车**可能**正是
  "同一 module_path 被清空后又被补齐"形成的 PG/YAML 两侧差异。本包不据此定性，
  留给下一条尺：按 `module_path` 聚合，列 `desc_zh='' AND name_en='' AND 存在同名非空历史值` 的件数。
