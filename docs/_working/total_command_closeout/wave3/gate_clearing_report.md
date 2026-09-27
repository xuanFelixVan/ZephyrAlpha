---
ttl: task_bound
completes_when: 本袋（波 3 数据链 data_supply + src/zephyr/data 三件 + tests）入队预检的判据无关内容硬阻断清零（assigned 6 项全清，CREATE-GUARD 与外来袋文件交总包）
---

# 波 3 入队预检清障案卷（gate_clearing_report）

- **车道**：`.aidrafts/st-final-build-20260926`（worktree `session/st-final-build-20260926`）
- **会话**：st-final-build-20260926
- **本册性质**：施工执行队"改到能过入队预检"的清障记录。只改判据无关的写法面；未动任何算法判据/阈值/断言/skip/xfail。
- **turn_budget**：≤1 施工轮（约 12 次编辑 + 预检/测试复跑；未 commit/未 add/未 enqueue，遵硬禁）。
- **verified（本车道实跑，E2）**：
  - 预检读数：`gate_prerun.py` 三态实测（主区全袋 / 主区本队面 / 车道全袋），见 §复跑读数。
  - 测试：`tests/data/test_wave3_*.py` 24 passed；`tests/governance/data_supply/` 28 passed；`tests/data/` 全目录 612 passed / 1 环境红(CH 未配置) / 1 skipped。
  - `check_wave3_rulers.py --counterfactual` RC=0（三把尺负控制转红、正控制保持绿——红逻辑未被削弱）。
  - 判据无关性：入队等价态（磁盘内容 + `git diff HEAD` 新增行）用各 gate 判据器实调，命中 0。
- **assumed（未直证，据纪律推断）**：
  - 预检 diff 类门（NO-BARE-SQL/TABLE-NAME/MUTABLE-CONST）读**暂存区**；本队被硬禁 `git add`，故车道 index 仍是 总包 投袋时的旧快照。本文以"磁盘内容 + `git diff HEAD` 新增行"作为 总包 重新 add 后的等价态来判定——**总包 投袋重 stage 后这些门即读到本队已修磁盘内容**。
  - `src/zephyr/data/__init__.py` 不在 `files_bag3_rel.txt` 内，但按违规 #2 指令须挂导出面——**投袋清单须补列本件**，否则 TEST-SOURCE 门读旧 __init__。
  - 外来 `wave1a` 测试/docs、`docs/_working/**` 属别的袋；本队禁碰（§3 会主责任制），其残留交总包。
- **input_set_disjoint_with**：`docs/01_policies_and_standards/**`（热册，总包写）；`src/zephyr/gov_enforcement/**`；`scripts/governance/{wave1a,wave1b,wave2,d5_architecture}/**`；`docs/_working/**` 既有件；`config/flags.yaml` 与任何 prereg 冻结件；`business_data_categories.yaml`（表名真源，只读）。
- **evidence_ref.cmd**：
  - 清障前基线（车道全袋，仅 assigned 门）：`python scripts/governance/meta/gate_prerun.py --session st-final-build-20260926 --project-root D:/ZephyrAlpha/.aidrafts/st-final-build-20260926 --files "<全袋绝对路径, D:/ 前缀>" --message-file .../msg_bag3.md --only NO-BARE-SQL --only TABLE-NAME-REGISTRY --only TEST-SOURCE-CONSISTENCY --only TTL-METADATA` → 内容硬阻断命中 NO-BARE-SQL + TABLE-NAME-REGISTRY（行号见 §3/§4）。
  - 清障后主区命令（题给原文）：`cd 主区 /d/ZephyrAlpha && python scripts/governance/meta/gate_prerun.py --session st-final-build-20260926 --files "<全袋绝对路径>" --message-file .../msg_bag3.md` → 内容硬阻断 2（全为外来文件）。
  - 本队面隔离判定：同上但 `--files` 仅本队 21 件 → 内容硬阻断 0。
  - 入队等价判据器实调：`python .runtime/tmp/st-final-build-20260926/verify_enqueue_sim.py`（磁盘内容 + `git diff HEAD` 新增行）→ NONE。

> 方法学注记：首轮预检曾误报"全绿"——因用 MSYS `/d/...` 路径喂 `--files`，Windows Python 解析不出绝对路径，diff 类门对空清单 fail-open。改用 `D:/ZephyrAlpha/...` 绝对车道路径后方得真读数。此为"不能红的检查器要防自欺"的现场教训，非内容改动。

---

## 逐条：违规原文 → 改法 → 复跑读数

### #1 TTL-METADATA（`src/zephyr/data/date_normalize.py`）
- **原文**：`# [TTL] task_bound: 波 3.1`（[TTL] 值须裸词 `task_bound`/`permanent`，后不得跟冒号/说明）。
- **改法**：磁盘现状 `date_normalize.py:2` 已是裸 `# [TTL] task_bound`（说明在第 3 行独立注释），合法规。据此把本袋全部 .py 的 `[TTL]` 行统一扫一遍：`__init__`/`date_normalize`/`dual_source_guard`/`miniqmt_caliber_sentinel`/`consensus_crosscheck` + `data_supply/*`(8) + `ch_probe` + `tests/**`，全部为裸 `task_bound`/`permanent`，无一处带冒号/括号——无需再改。
  - 唯一非法的 `task_bound: 波 3.1` 仅存在于**车道暂存旧快照**（AM 件的 index 侧），投袋重 stage 读磁盘即合法。
- **复跑读数**：主区命令 TTL-METADATA 对本队文件 0 命中；车道 TTL 读磁盘亦 0（`verify_enqueue_sim` 之外，TTL 走 `check_frontmatter_metadata.py` 读盘实测 date_normalize PASS）。

### #2 TEST-SOURCE-CONSISTENCY（三件新模块挂 `__init__` 导出面）
- **原文**：`from zephyr.data import date_normalize / dual_source_guard / miniqmt_caliber_sentinel` 报"符号在 __init__.py 未定义"。
- **改法**：照既有 `trading_calendar` 模块导出惯例（`from zephyr.data import X  # noqa: E402,F401 …` + `__all__.append("X")`），在 `src/zephyr/data/__init__.py` 的 `trading_calendar` 块后、ORPHAN-MODULE 块前追加三件；未自创风格，未改测试为 skip。
- **复跑读数**：中立 cwd + 车道路径下 `from zephyr.data import date_normalize, dual_source_guard, miniqmt_caliber_sentinel` OK；`hasattr(zephyr.data, …)` 三真；门 PASS。

### #3 TABLE-NAME-REGISTRY（block）
- **原文**：`consensus_crosscheck.py:162`（`'c3_fundamental.consensus_daily'`）、`supply_conservation.py:269,281`（`'c1_market.etf_benchmark'`）硬编码表名。
- **改法**：走 TableRegistry 真源，照仓内既有消费者写法 `get_registry().table(<category_id>)`（先例 `decision_chain_sentinel.py`/`redblue_metaq_suite.py`）。真源反查 category_id：`c3_fundamental.consensus_daily`→`fund_consensus_daily`，`c1_market.etf_benchmark`→`market_etf_benchmark`。
  - `consensus_crosscheck.check_reconciliation`：lazy `from zephyr.data.table_registry import get_registry`，`b_name=f"self_agg({get_registry().table('fund_consensus_daily')})"`（展示串逐字不变，仅源改真源派生）。
  - `supply_conservation._cons_control_inputs`：同法拉出 `bench_table`，替换 269/281 三处字面量（含 dict 键与 `SentinelLeg` 参数）。
  - 未改 `business_data_categories.yaml`（只读真源）；`consensus` 其余 65/220-222/67-100 存量表名属未改动行（门只检 added 行，diff-based），不动。
- **复跑读数**：`verify_enqueue_sim`（磁盘内容 + git-diff-HEAD 新增行）对 TABLE-NAME 命中 **NONE**；测试 3.3 守恒尺反事实仍 `UNDECLARED_EVAPORATION` 转红（RC=0），行为等价。

### #4 NO-BARE-SQL（§5.160.2）
- **原文**：`strict_truth_reader.py:86,96` f-string 裸 SQL（新写判据 SQL）。
- **改法**：**集中化**（新逻辑不许用 noqa 蒙）：提模块级 `SQL_WINDOW_TMPL / SQL_LATEST_TMPL / SQL_LATEST_WHERE_TMPL`（普通 `Assign`，命中 `_extract_sql_constant_lines` 的 AST 豁免；不用 AnnAssign 以免脱离豁免），`build_window_sql/build_latest_sql` 改为 `.format(...)` 填已校验标识符与日期常量；删原 84/95 行的错位 `# noqa: bare-sql`（既躲不过同门、留任又触发 NOQA-VALIDATION）。生成 SQL **逐字节等价**（实测打印核对）。
- **复跑读数**：`verify_enqueue_sim` 对 NO-BARE-SQL 命中 **NONE**；车道 stale-index 复跑仍报（读旧暂存）——重 stage 即清；测试无回归。

### #5 CREATE-GUARD（`scripts/governance/data_supply/ch_probe.py（注：施工方案原指 `scripts/data/`，实测该目录被 .gitignore 第 603 行整体排除，故改道）` 无 creation_token）—— 交总包，不自注
- **现状**：`ch_probe.py` 缺 creation_token；本队按令**不注册热册**。
- **待总包登记节**：`creation_token` 登记 = `scripts/governance/data_supply/ch_probe.py（注：施工方案原指 `scripts/data/`，实测该目录被 .gitignore 第 603 行整体排除，故改道）`（MOD-GOV-wave1a-ch_probe）。
- **附带 CREATE-GUARD 面（同属登记/命名面，一并交总包）**：`false_green_crosscheck.py`/`no_cache_endorsement.py` 定义 `class Finding`/`class Verdict` 触发 CLASS-UNIQUENESS 同名冲突——重命名会波及 `from … import Finding` 的测试与 `supply_conservation` 消费者，非判据无关写法面，不自改。
- **复跑读数**：本队主区面未触发该门；车道全袋/本队面 CREATE-GUARD 命中（token + 类名），归本条交总包裁定。

### #6 复跑预检
见下"总读数"。

---

## 总读数（复跑预检）

| 口径 | 内容硬阻断 | 明细与归属 |
|---|---|---|
| 清障前·车道全袋·仅 assigned 门 | NO-BARE-SQL + TABLE-NAME-REGISTRY（+TTL 暂存旧快照） | strict_truth_reader 86/96；consensus 162 / supply_conservation 269,281 |
| 清障后·**主区命令·本队 21 件** | **0** | `prerun_mine.json`；本队判据无关硬阻断全清 |
| 清障后·主区命令·全袋 35 件 | **2** | TTL-METADATA + DOC-HEADER-SUITE——命中项**全部**是外来件：`tests/governance/test_wave1a_query_shape_ruler.py`、`test_wave1a_strict_read_canary.py`（[TTL] 冒号非法）与 `docs/_working/**/wave1a/wave3` 的 `read_shape_violations.md`/`store_liveness_census.md`/`data_chain_report.md`/`supply_ledger_report.md`（ttl/doc_type frontmatter）——禁碰，会主责任制，交总包 |
| 入队等价判据器实调（本队件） | **NONE** | NO-BARE-SQL / TABLE-NAME / MUTABLE-CONST / DANGLING-REFERENCE 命中 0；TEST-SOURCE 导出 True |

**第 5 项外的"全部清零"达成口径**：以主区命令对**本队可改文件面**判定 → 内容硬阻断 **0**（题给命令的绝对车道路径清单含别的袋文件，其 2 项残留在本队写域外，属 §3 owner 责任制，非本队能清）。

## 本队额外清掉的判据无关硬阻断（非 assigned 6，属安全写法面顺手清）
- **MUTABLE-CONST-WITHOUT-FINAL**：`date_normalize.__all__`、`dual_source_guard.__all__/_STATUS`、`miniqmt_caliber_sentinel.__all__` 由 `Assign` 改 `X: Final = …`（AnnAssign+Final，命中门豁免；纯类型注解，零语义变更；`SOURCE_PAIR_RED=frozenset(...)`、tuple 常量不可变不动）。补 `from typing import Final`。
- **DANGLING-REFERENCE（REFERENCE-INTEGRITY）**：`gen_registration_needs.py` `根宪法 §9 条目 5`（无 `## 9.5` 标题，悬空）→ 改为合法锚「宪法 §9 第 5 条」（不带 AGENTS.md 前缀；带前缀本身即 REFERENCE-INTEGRITY 自触形态，两处）。纯注释/docstring，无逻辑改动。

## 残留交总包裁定（**非判据无关写法面，本队按"改不动如实报红"不动**）
入队全袋扫描（车道·staged==disk 时）对本队件仍会命中以下**内容块**，均**不在 assigned 6**、且修改将触及错误契约/源方向/接口/命名，越出"只改判据无关写法面"授权：
1. **MSG-EXPOSURE**：`strict_truth_reader`/`no_cache_endorsement`/`supply_sources` 的 `raise …Error(f"…{sql/path}…")` 把 SQL/路径放进消息文本——其 `[ERROR_CONTRACT] 失败必抛并点名` 是在册设计判据（"点名失败 SQL"即本件目的）。改投 `details` 字段=削弱契约，非清障。→ 交总包。
2. **SSOT-REDEFINITION**：`miniqmt_caliber_sentinel.py:49` 重定义 `REPO_ROOT`（canonical=`shared/io/paths.py`）。改引 canonical 会改尺的默认扫描根（行为面），非纯写法。→ 交总包定源方向。
3. **COMPLEXITY-GUARD/NO-LONG-PARAM-LIST**：`dual_source_guard.classify_source_pair` 8 参（>7）。收敛参数对象=改函数签名（算法接口），波及 `consensus_crosscheck` 调用点与 `test_wave3_dual_source_guard` 断言。→ 禁改算法，交总包。
4. **CREATE-GUARD**：ch_probe creation_token + `Finding`/`Verdict` 类名唯一性（见 #5）。→ 交总包登记。

## 测试 before/after
| 目标集 | before（本袋 自证 E2 基线） | after（本车道实跑） |
|---|---|---|
| tests/data/test_wave3_*.py | 24 | **24 passed** |
| tests/governance/data_supply/ | 28 | **28 passed** |
| tests/data/ 全目录 | 612 passed / 1 环境红 | **612 passed / 1 failed(CH 未配置·非本袋件) / 1 skipped** |
| check_wave3_rulers --counterfactual | RC=0 | **RC=0**（红逻辑未削弱） |
| 邻居尺 66 条（msg 自证） | 66 | 未逐跑（本队改动不触其宿主；见残留说明） |

> 说明：被硬禁 `git add`，无法把车道 index 对齐磁盘后跑 staged-类门，故以"磁盘 + `git diff HEAD` 新增行"的入队等价态判定（`verify_enqueue_sim.py`），与 总包 投袋重 stage 后门读到的内容一致。写盘均 `newline='\n'`；测试用 `--basetemp=.runtime/tmp/st-final-build-20260926/bt_*` 与 tmp_path，未写 data/ 生产路径；未跑 test_ops_guard_red_team.py；无删除动作；未 commit/add/enqueue。
