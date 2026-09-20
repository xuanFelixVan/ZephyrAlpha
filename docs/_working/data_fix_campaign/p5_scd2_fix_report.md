---
ttl: task_bound
session: st-data-fix-20260921
title: 数据正确性线分包5——index_constituent SCD2 四条疑似真 bug 复现定性红绿双向报告
---

# p5 SCD2×4 复盘报告（2026-09-20 深夜 · st-data-fix-20260921）

真源：`docs/_working/dataqa_audit/test_health_report.md` R3 C 类 C1-C4 ｜ 测试族
`tests/zephyr/data/test_index_constituent_scd2.py` ｜ 实现
`src/zephyr/data/implementations/akshare_provider.py::_fetch_index_constituent`（L7320-7379）。

## 结论一句话

**四条全部为测试病（同一根因），src 无 bug，零 src 改动**：测试白盒断言停留在
2026-08-24 GAP-B3-03 初版"开新批 6 列"契约；2026-08-30 commit `2a16988d05` 已按
writer 实约束统一闭旧/开新批 7 列（开新行 valid_to=None），测试未跟进。SCD2 语义
（闭旧开新/同日不互闭/空快照不闭/闭旧失败不阻断）实测全部健在。

## 根因链（证据等级[亲验]）

1. **writer 约束属实**：`src/zephyr/data/buffered_writer.py` `add()` L111-112 列子句由
   **首个 FetchResult** 固定（`_init_columns`）；L115-119 当后续批次列数 ≤ keep_indices
   时走 `extend(result.rows)` 原样入缓冲 → 窄行按宽子句 flush = CH Code 27。
   即"闭旧 7 列 + 开新 6 列"混宽在同表同任务内必然炸 flush——2026-08-30 docstring
   所记生产实证（000300 混宽 Code 27）与代码逐行吻合。
2. **统一 7 列语义无损**：开新行 `(…, None)` 与 6 列缺省在 CH Nullable 列上等价
   （NULL=开新）；`valid_to` 在 `c1_market.index_constituent` 为可插入列
   （`ch_writer.get_insertable_columns_set` 实测在集，[亲验]）。
3. **测试未跟进**：5 测中 4 处断言 `"valid_to" not in r.columns` / `columns == _BASE_COLUMNS`
   锁死旧 6 列形状 → R3 报成疑似回归。第 5 测（`test_two_sequential_snapshots_single_open_version`）
   断言语义而非列形状，故始终绿（R3 报 ×4 与实测 4F/1P 吻合）。

## 四条逐条

### C1 新快照行携带 valid_to 列（应 NULL=开新）
- 复现[亲验]：`test_new_snapshot_closes_old_open_versions` FAILED @L167
  `new_batch.columns == _BASE_COLUMNS` → 实得 7 列（+valid_to）。
- 定性：**测试病**。闭旧批断言（results[0] 行集/valid_to=2026-08-17）全过，仅列形状断言过期；
  开新行 valid_to 值=None 语义正确。
- 修：改断 `columns == [*_BASE_COLUMNS, "valid_to"]` + `all(row[-1] is None)`（语义锁死）。

### C2 同日重跑闭旧批
- 复现[亲验]：`test_same_day_rerun_no_closure` FAILED @L207 `"valid_to" not in r.columns`。
- 定性：**测试病**。语义断言 `open_versions==1`（L210）实测通过——同日重跑零闭旧行，
  仅"无 valid_to 列"这一旧形状代理断言失效。
- 修：改断 `all(row[-1] is None for r in results for row in r.rows)`。

### C3 空快照闭行
- 复现[亲验]：`test_empty_snapshot_no_closure` FAILED @L231（同列形状断言）。
- 定性：**测试病**。src 侧 `if rows:` 护栏健在：空快照零行、零 open 查询
  （`r.rows==[]`、`called==[]` 两断言均过）→ 不可能闭行。
- 修：删过期列断言，留 `rows==[]`+`called==[]`（语义已全覆盖），注释留痕。

### C4 闭行查询失败未保新行
- 复现[亲验]：`test_closure_query_failure_keeps_new_rows` FAILED @L246（同列形状断言）。
- 定性：**测试病**。CH down 时 `except→return []` 护栏实测健在：5 批零 error、
  开新行照常产出（L245/L247 原断言过）。
- 修：改断 `all(row[-1] is None …)`（仅开新行无闭旧行）。

## 红绿双向证据（命令与实测摘要，全程[亲验]）

- **红（修复前基线）**：`python -m pytest tests/zephyr/data/test_index_constituent_scd2.py`
  → `4 failed, 1 passed`（C1@L167 列差 diff；C2/C3/C4 均败于 `"valid_to" not in r.columns`）。
- **绿（测试修后）**：同命令 → `5 passed in 1.35s`。
- **红（mutation 再注入，证新测试仍守四语义，src 临时注入后逐一还原）**：
  - M1 新行出生即闭（`(*row, trade_date)` 替 `(*row, None)`）→ `4 failed, 1 passed`
    （C1/C2/C4 同族断言+两版本连续场景全红）。
  - M2 过闭（闭旧 as_of=生效日+1d，同日重跑被闭）→ `3 failed`（含
    `test_same_day_rerun_no_closure`）。
  - M3 空快照也闭旧（`if rows:` 护栏外提）→ `1 failed` =
    `test_empty_snapshot_no_closure`（`called` 5 项 open 查询实锤）。
  - M4 闭旧失败阻断开新（`except Exception`→`except ValueError`）→ `1 failed` =
    `test_closure_query_failure_keeps_new_rows`（"获取失败: CH down" 5 指数全灭）。
  - M1-M4 还原后 `git status --porcelain` 该文件空、`git diff --stat` 空=字节级还原；
    复跑 `5 passed`。
- **能力反查审计**：`capability_lookup.find('index_constituent', session_id=…)` 已落
  `.runtime/lookup_audit/st-data-fix-20260921.jsonl`（15 行，find 对 0 命中也落审计）。
- **写域隔离**：`src/zephyr/data/implementations/akshare_provider.py` 最终零 diff
  （仅 mutation 实验，已还原）；估值链/index_quote/news/auction/crypto/夜跑链零触碰。

## 待数据订正项（交总包）

**无**。本四条不涉 CH 数据订正：SCD2 语义修复（存量闭合 34,614 行、open 违例
6,922→0、PIT 000300.SH@08-20 1500→300）已由 2026-08-24 commit `12caf83a11` 落地，
2026-08-30 `2a16988d05` 仅改批次列形状不改数据语义 [转报·commit 文档，未亲查 CH]。

## 变更清单（本 commit 白名单）

1. `tests/zephyr/data/test_index_constituent_scd2.py` — 4 处断言对齐统一 7 列契约
   +模块 docstring 契约史留痕（唯一实质变更）。
2. `docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`
   — 顶级 creation_tokens 追加四行式 1 条（safe_write_text CAS 写，yaml.safe_load
   进程外核实 token=`data-fix-p5-scd2-report-20260921`）。
3. 本报告（token 同上）。

## 证据等级与未完成项

- 四条定性/红绿双向/buffered_writer 约束/valid_to 可插入性：[亲验]。
- GAP-B3-03 存量闭合数字与 Code 27 生产实证出处：[转报]（commit `12caf83a11`/`2a16988d05`
  文档记载，未亲查 CH——任务红线禁碰 CH）。
- `capability_lookup.find('index constituent scd2')` 0 命中（能力注册表未索引该组合词），
  已按规留审计后施工：[亲验]。
- 无未完成项。
