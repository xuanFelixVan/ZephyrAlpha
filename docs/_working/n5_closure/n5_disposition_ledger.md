---
ttl: task_bound
completes_when: landA 车道三批次全部落地且 release 后 .ailocks/registry.json locks=0 复核完成，本台账归档为历史锚点
---

# N-5 收口处置台账（landA 车道 · st-ff-landA-20260918）

> 依据总包裁定 R-001（COORDINATION_LEDGER.md §6，2026-09-18）建立。
> 本文件是 N-5 判决面「按现状归位」的执行记录与不落项登记簿。

## 1. R-001 裁定要点（全文摘录自 COORDINATION_LEDGER.md §6 已裁台账）

- **判定**：N-5 共享区纠缠脏树已因自愈而失效，按现状归位，无需「恢复 or 废弃」判决。
- 总包亲验（2026-09-18）：`git stash list`=空；`git diff --cached --diff-filter=D`=0 件；
  `.ailocks/registry.json` locks=0 条；`.git/MERGE_HEAD` 不存在。
- 8 份交接令共同描述的「317 staged / 22 schema 删除 / 189 deep_review docs /
  stash@{0} WIP on aa43e3b530」在当前工作区**已不存在**。
- 裁定四条：①staged 24 件由 landA 按原批次配方落地（已有 23/23+2680 测试证据）；
  ②unstaged 81 件按 §2 所有权地图归各车道，禁任何车道 restore/clean/reset 他人 unstaged 件；
  ③stash 面已空，分包1 T5（归档+drop）判已完成/已失效，只记「实测 stash 数=0」；
  ④`data/c4_pdf_cache/` 进 .gitignore 归 instL。
- 依据：第一性原理——「恢复 or 废弃」是对存在的对象做判决，对象已不存在则判决无标的；
  宪法 §9.11 交接令里的 N-5 描述是历史快照数据，不是当前事实。

## 2. 本车道四项实测复核（2026-09-18，开工冷启动即测）

| 指标 | 实测值 | 与 R-001 一致性 |
|---|---|---|
| `git stash list` 条数 | **0** | 一致 |
| `git diff --cached --diff-filter=D` 件数 | **0** | 一致 |
| `.ailocks/registry.json` locks 条数 | **0** | 一致 |
| `.git/MERGE_HEAD` | **不存在** | 一致 |

另：process_reaper SALVAGED 报告死会话 st-fullflow-20260918 遗物回收（stash=0 件、释放 claim=0），
drift 面 stash_count=0，与 R-001 互证。

## 3. 三分法历史结论（存档口径）

- 历史处置框架：对 N-5「317 staged」面按三分法甄别（吸收=HEAD 已含 blob / 落地=归属批次提交 /
  废弃=无内容价值丢弃）；对 stash 面实证 **309 件 blob 级全吸收**（stash 内容全部已在 HEAD blob
  中找到等价物）→ 判废弃。此结论以总裁定 summary 原文为真源：
  「staged 三分法/stash 309 件 blob 级全吸收实证废弃(现 stash 数=0)」。
- **R-001 后效力**：判决对象（317 staged 面 + stash@{0}）已在当前工作区消失，三分法结论仅存
  历史存档价值，无执行标的。板上检索（docs/_working 全文 grep「三分法」「blob 级」）未见更细
  工作底稿，此为诚实口径：细节以 8 份交接令原文（历史快照数据）为准。

## 4. T5 stash 处置记录

实测 `git stash list` = 0 → 分包1 T5（归档+drop）判**已完成/无标的**。
本车道未执行任何 stash 命令（遵令）。

## 5. 落地批次与测试证据

### Batch A（T1，pf_alloc 危机闸）
- 清单：`src/zephyr/pf_alloc/crisis_gate.py`、`allocation_orchestrator.py`、
  `core/regime_meta_allocator.py`、`tests/pf_alloc/__init__.py`。
- **registry 册从清单剔除**：`capability_canonical_file_registry.yaml` 工作区==HEAD（本批所需
  token 含 `crisis_gate`/`n5-cohort-ledger-e4` 全部已在 HEAD），而 index 里的 staged 副本比 HEAD
  旧 4 行（缺 deeprev handoff token）——提交 staged 副本=回退他人条目，必撞
  REGISTRY-MASS-DELETION/HOT-FILE-BASE-FRESHNESS。已按纪律 §4「已在 HEAD 就从清单剔除」处理，
  并将该 stale staged 副本从 index 撤回（`git restore --staged -- <册>`，限定单文件，工作区字节不动）。
- 测试：`pytest tests/pf_alloc/ tests/risk/` → **2247 passed, 1 skipped, 0 failed**（83.4s）。
- **跌破 2680 归因**（先归因再动，已归因）：collect-only 复核 pf_alloc=390 + risk=1857 = 2247，
  与通过数严格相等；两目录 git status 无任何删除/丢失文件；crisis_gate 测试件在位。
  前任「2680 级」不可由当前 inventory 复现，推定为更宽口径（含 tests/alt_data 等其他目录）
  或旧 inventory。零失败零收集错误，判无回归。

### Batch B+E（T2+T4，E4 cohort + flash 终件 + 本台账）
- 清单：`src/zephyr/alt_data/cohort_daily_ledger.py`（untracked→git add）、`src/zephyr/alt_data/__init__.py`、
  `tests/alt_data/test_cohort_daily_ledger.py`、`docs/_working/residual_construction/e4_cohort_reconciliation.md`、
  `00_master_ledger.md`、`docs/_working/flash_speedup/90_report.md`、`91_fresh_triage_and_rulings.md`、
  `F2/F3/F5/F6/F9 五份 DESIGN.md`、本台账。
- cohort 新 .py 三件套核验：creation token `n5-cohort-ledger-e4-20260918` **已在 HEAD 册**（免重登）；
  翻译条目已在 HEAD module_translation_registry；depgraph 节点 **14830694**（MOD-ALT-COHORT-LEDGER，
  design 面，见 pg_backups nodes.csv:13）。
- 测试：`pytest tests/alt_data/test_cohort_daily_ledger.py` → **13 passed**。
- **91_fresh_triage_and_rulings.md**：只提交 index（staged）字节——他车道 unstaged +22 行 N-6 节
  WIP 在飞。入队快照读工作区，故采用「备份工作区字节→写回 index 字节（`git show :f`）→入队→按字节
  还原」的窗口交换，unstaged 增量零丢失。
- **sim-memo-202609.json 剔除**：docs/_working 目录契约 DCR-005/008 只许 .md/.yaml/.csv/.html，
  .json 必拦 → 按令剔除不加旗，留 staged 原位待归属处置。
- **sim-memo-202609.md 剔除**：staged 版本无 ttl frontmatter，`check_frontmatter_metadata.py
  --strict-doctype` 实测硬拦（FAIL: missing ttl frontmatter in temporary zone）；且该件正被
  他车道活跃编辑（时间戳 09:30→16:43→17:28 会话期间三变）→ 剔除登记，禁代修（owner 责任制）。

### Batch C（T3，E5 演练 + sector 测试）
- 清单：`scripts/backtest/crisis_drill_monthly.py`（重构后）、`tests/signal_ashare/test_sector_strength_aggregator.py`、
  `test_sector_ecology_judge.py`、`test_sector_strength_wiring.py`、`tests/risk/__init__.py`。
- **NO-HIGH-COMPLEXITY 总包预裁执行**：untracked 新文件全函数皆新。用门禁同款度量
  （`high_complexity_gate._cyclomatic_complexity`）实测唯一超标函数 `render_markdown` cc=18>15。
  按裁定重构：抽模块级 `_render_meta_lines/_row_window_replay/_row_stress_crosscheck/
  _row_liquidity_family/_render_liquidity_lines` 五个 helper，重构后全文件 OVER-15=NONE（最大 cc=14）。
- 行为保持证据：①`tests/backtest/test_crisis_drill_monthly.py` **16 passed**；
  ②新旧模块双载对照 `render_markdown` 输出，三分支矩阵（liq 可算/不可算/None × gaps 有无 ×
  窗口可算/不可算/恢复三态）**逐字节相等**（EQUIV-A/B/C 全 True）。
- sector 测试：三件合跑 **27 passed**（aggregator 件为 0 字节占位，收集 0 测试，如实登记）。
- **sector/__init__.py 不入批**：其 worktree 改动=给 sector 子包加 `__all__` 清单，与
  intraday_t0/limit_up/ml_forecast/screening/sentiment 五个兄弟子包 __init__ 同模式的系统性
  注入面；sector 测试 import 全部走 `zephyr.signal_ashare.core.*`，不经 sector 子包 →
  判定**非配套件**，按令只登记不代修。
- **blueprint.md（docs/03_modules/_domain_signal/sector_conduction/）不入批**：全员禁写域；
  实测 `git diff` 内容为空（仅 CRLF 行尾漂移，无实质改动）→ 登记移交。
- crisis_drill 三件套免登核验：token `auto-scaffold-backtest_crisis_drill_monthly-20260918` +
  `n5-crisis-drill-e5-20260918` 均在 HEAD 册；翻译条目在 HEAD；depgraph 节点 14799384
  （MOD-BT-219，D_BACKTEST）+ 测试节点 14822281 均在。

## 6. 不落项登记（按令只登记不执行）

1. **cp3 留分支 `89dd33dd8a`**：owner_regime_switcher cp3 变体不合入 dev，留在该分支，
   后续处置归总包/Owner。
2. **blueprint 门禁 2 败移交维护班**：blueprint 面 2 处门禁失败不在本车道修复范围，移交维护班。
3. **维护班三件**：
   - cp3 param-object 化改造，落点 `owner_regime_switcher/{engine,switcher,exam}.py`；
   - 裁定 #304 撞号 tombstone（并发取号撞号，需立墓碑条目防再撞）；
   - serializer lease 僵尸 status 缺陷（lease 过期后 status 面残留僵尸态）。
4. **`data/c4_pdf_cache/` 进 .gitignore**：R-001 ④ 归 instL 车道，本车道不动。
5. **sim-memo-202609.{json,md}**：见 §5 Batch B+E 剔除登记，归属车道自处置。
6. **signal_ashare 六子包 __init__.py `__all__` 系统性注入面**（含 sector）：非本车道批次，
   留在工作区归注入方/维护班。

## 7. T6 临时件清理记录

以下三件均实测存在、untracked（`git ls-files` 不命中）、非本车道成果，已删除：
- `docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml.bak_pre_one_question`（1,075,569 B）
- `scripts/ch/apply_market_tables_ddl.py.tmp.20284.2c57192a090d`（62,250 B）
- `scripts/ch/apply_market_tables_ddl.py.tmp.20284.ca1d8485b155`（61,364 B）

注：`scripts/ch/apply_market_tables_ddl.py` 本体属 residG 独占，未触碰。
