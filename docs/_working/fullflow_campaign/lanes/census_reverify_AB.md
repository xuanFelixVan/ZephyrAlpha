---
ttl: task_bound
completes_when: 总包据本表把 BRK-001..026 的四态判并入可信分母，且 §4 改判建议被采纳或驳回留痕
---

# 普查复测 · A/B 族切片（BRK-001..026）四态重判

产出者=`st-ff-rv1-20260918`（普查复测车道，总包=`st-fullflow-20260918`）
复测时刻=2026-09-18 21:1x～22:0x（本地）｜施工模式=**只读**（未改 `src/**`/`scripts/**`/注册表/config，未建任务条目，未取裁定号）
复测对象=`skeleton/01_break_census.md` A 族 19 条 + B 族 7 条 = **26 条，全部复跑，0 条未跑**
每条判据均标依据等级：`亲验`=本会话亲自复跑原始命令；`转报`=引他腿产物未复跑；`推断`=未取证。

> 论域声明（裁定#325 表述禁令）：本文**不说"全绿/全部确认"**。本文只覆盖 A/B 两族 26 条；
> 普查其余 59 条（C/D/E/F/G/H/I 族）不在本切片，仍是 `未复测`。
> 临时件全部在 `.runtime/tmp/st-ff-rv1-20260918/`（`rv_scan.py` `scan_out.json`
> `import_smoke.py/.txt/.json` `exec_as_file_smoke.py/.txt/.json_v2` `brk019.json` `gitstatus_before/after.txt`），项目根目录零临时文件。

---

## 1. 四态计数表（分母 = 26，无缺件）

| 四态 | 件数 | BRK 清单 |
|---|---|---|
| 仍成立 | **18** | 001, 003, 006, 009, 010, 011, 012, 013, 014, 015, 016, 017, 018, 019, 023, 024, 025, 026 |
| 已闭合 | **5** | 004, 005, 020, 021, 022（其中 021 为**条件闭合**，见 §2 该行） |
| 归属错 | **0** | —（A/B 族记的模块路径逐条核对无挂错对象者；影响叙述的错位见 §4-C/§4-D） |
| 口径不符 | **3** | 002, 007, 008 |
| 未可判 | **0** | —（26 条全部有判据；仅 2 个**子项**证据不足，已在明细内显式标 `未获证`，不牵连整条判态） |
| **合计** | **26** | |

对照 z-verifier3 的入口分布（仍成立 3 / 口径不符 2 / 未复测 80）：本切片把 26 条从"未复测"里取出，
可信基线推进为 **仍成立 18 / 口径不符 3 / 已闭合 5 / 其余 59 未复测**。

**本切片最实的两个数**：
1. A/B 族 26 条里 **5 条（19.2%）在普查落笔前后已被闭合**——其中 BRK-004/005 的闭合（09-16 02:40）
   **早于普查落笔（09-18 17:47）两天**，属 R-041「自愈仍挂账」的**加重版**（不是当天治好，是普查时就已经治好了两天）。
2. 普查 A 族的证据源分两类：GOMAP 机器字段 `families.*.wiring`（可复现）与 GOMAP 散文注记
   `pipeline.layers[].disconnected.note_zh`（**不可复现、且与同文件机器字段自相矛盾**）。
   BRK-004/005 恰好引的是后者——这是本切片定位到的**普查取证方法缺陷**，不是单条笔误。

---

## 2. 逐条明细

| BRK | 原命令（普查记载，逐字复跑） | 我的实测输出 | 与记载 | 四态 | 依据 |
|---|---|---|---|---|---|
| 001 | `python -c "...yaml.safe_load('config/governance_operations_map.yaml')['counts']"` | `{'total_modules':416,'wired':244,'wired_dynamic':6,'wired_by_header':71,'suspect_orphans':95}` | **逐字段一致** | 仍成立 | 亲验 |
| 002 | 同上遍历 families | wiring dist `244/71/95/6` **精确一致**；族分布（全口径）`L1 21 / L2 26 / L0 24 / L5 11 / L4 10 / L3 3 / L6 0`（和=95）；再按 maturity=production 过滤=`L1 18/L2 24/L0 19/L5 9/L4 9/L3 3/L6 0`（和=82） | **族明细三种口径都凑不出普查的 21/25/21/10/10/3/0**，且普查自身七个数**相加=90≠95** | **口径不符** | 亲验 |
| 003 | GOMAP `families.L0_lifecycle` wiring=suspect_orphan 逐条列 9 件 | 9 件（startup_sequencer/teardown_manager/rolling_upgrade/state_synchronizer/state_propagation/system_transfer/session_conflict/incident_postmortem/housekeeping）**全部仍在 suspect_orphan**；另用 AST 独立扫 src+scripts 4512 文件：9 件精确导入者 **0**（含 scripts/）；磁盘 9 个 .py 存在（09-16 后未改） | 一致（9/9） | 仍成立 | 亲验 |
| 004 | GOMAP `pipeline.layers[GOM-L3].disconnected` note "五域编排层无人 import(A3 降级执行…)" | 同文件**机器字段** `families.L3_fuse[zephyr.autonomy_core.kill_switch_orchestrator].wiring = **wired**`；独立 AST：导入者 2 个＝`src/zephyr/trading/boot_hooks.py:608`、`src/zephyr/governance/resilience_governance/emergency_track_guardian.py:551`；`boot_hooks.py:684` 启动链实调 `_init_kill_switch_orchestrator()` | **不一致：断点已不存在** | **已闭合** | 亲验 |
| 005 | GOMAP 同层 note "蓝图声明 CONSUMERS=escalation 但无 import(A4 待接线)" | 机器字段 `families.L1_monitor[last_resort_watchdog].wiring = **wired**`；写方 `escalation_engine.py:390-394 get_last_resort_watchdog().activate()`、读方 `emergency_track_guardian.py:402-406` | **不一致：断点已不存在** | **已闭合** | 亲验 |
| 006 | GOMAP `pipeline.layers[GOM-L2].disconnected` "未反查到消费方(A5)" | note 原文未改（唯一未被本战役动过的 A5 注记）；AST 精确导入者 **0**；全仓 grep 仅 2 命中＝`infrastructure/__init__.py:38` 的 `__all__` 字符串 + 生成器自己的正则模式串 | 一致 | 仍成立 | 亲验 |
| 007 | `python .runtime/tmp/ff-mine0/orphan_scan.py` | **逐字跑：`scanned: 4512  src modules: 0  zero-indegree: 0`**——归档脚本在仓库根目录下恒返回 0（`mod_name` 用 `relative_to(ROOT/"src")` 绝对路径比对失配）。普查真值来自**未归档的"修正版内联脚本"**。按同语义自建复跑（`rv_scan.py`）：`4512 py / 3480 src 模块 / ZERO-INDEGREE 1685`；Top 包 `commit_gates 88 / access_control 73 / code_dedup 52 / skills 46 / diagnosers 46 / detectors 41 / gates 41 / rollback 39 / shared.contracts 36 / a2a_protocol 33`；"leaf(non-entry) 1585" 无可复现定义 | **不一致**（3477→3480、1593→**1685**、1585 不可复现、Top1 由 access_control 73 变 commit_gates 88——归档件里 commit_gates 只有 11） | **口径不符** | 亲验 |
| 008 | `python scripts/governance/extract_depgraph.py --summary` + 读手册 :135 | `--summary`→`total_domains 75 / total_modules 7880 / total_production_nodes 11826`（普查 7853/11827）；真源 DB（只读 `get_depgraph_pg_connection(read_only=True)`）→`nodes 12022 / edges 22843 / 孤儿(production 且无入边) 388`；手册 **HEAD 版** 11894/22164/**383**，手册**工作区未提交版** 12023/22845/**388**；`最后同步：2026-08-17` 由 `idempotent_timestamp(生成器自身)` 派生＝该脚本最后一次 commit 日（`cc31c7e736` 2026-08-17 05:30），**与数据新鲜度无关** | **因果说反**：数字是活的，"过期"是幂等时间戳的设计本意（宪法 §11.1.1 禁 datetime.now） | **口径不符** | 亲验 |
| 009 | 同 BRK-007 扫描 → `autonomy_core.skills: 46` | **46 件精确一致**；且**普查要求的"以技能注册表口径复核"我做了**：全仓唯一技能册 `src/zephyr/autonomy_core/skills/skill-registry.yaml` `metadata.total_skills=2`，两条均为 SKILL.md 型域技能（database-specialist / master-blueprint），**不含这 46 个 `skill_*.py`**；发现链自身也死：`all_skill_modules`、`skills/skill_discovery` 均零入度（唯一外部命中是 `__init__.__all__` 字符串） | 一致（并要求复核的部分现在有了机械负证据） | 仍成立 | 亲验 |
| 010 | 同 BRK-007 → `security.access_control: 73` | **73 精确一致**（零入度第一大族，按现口径为第二大，次于 commit_gates 88）；普查"需辨真伪"半句未复算（见 §5 未跑子项） | 一致 | 仍成立 | 亲验 |
| 011 | 同 BRK-007 + depgraph | 七子包 `46+41+41+20+18+18+16=`**200 精确一致**；全包 `.py` 实测 **340** ✓；depgraph `D_FEEDBACK_LOOP nodes=240` ✓；全包零入度合计实为 **241**（含 actors 10 / resilience 5 / security 4 等）→"过半"成立且更高（241/340=70.9%）；**"FBL 三域 213 节点" 未获证**：nodes 表无 `blueprint_id LIKE 'FBL%'` 也无 `subdomain_id LIKE 'FBL%'`（均 0），反馈域只有 `D_FEEDBACK_LOOP` 一个 | 主体一致，1 子项未获证 | 仍成立 | 亲验（子项未获证） |
| 012 | 同 BRK-007 → `gov_code_quality.code_dedup: 52` | **52 精确一致** | 一致 | 仍成立 | 亲验 |
| 013 | 同 BRK-007 → `infrastructure.rollback: 39`；depgraph `D_INFRA_RECOVERY` 100 | 39 ✓ / 100 ✓ | 一致 | 仍成立 | 亲验 |
| 014 | 同 BRK-007 → `infrastructure.a2a_protocol: 33`；depgraph `D_INFRA_A2A` 135 | 33 ✓ / 135 ✓ | 一致 | 仍成立 | 亲验 |
| 015 | GOMAP `families.L2_resource` 中 capacity_assurance suspect_orphan 8 件 | 8 件清单**逐字一致**（budget_forecaster / contracts / cross_module_integration / host_resource_governor / risk_mitigation / schema / sli_instrumentation / tech_stack）；但今日全仓 grep：唯一被消费的是 `host_resource_governor`←`src/zephyr/trading/process_reaper.py:1064`（BRK-066 治本批）→ **实剩 7 件孤儿** | 成分漂移 8→7 | 仍成立 | 亲验 |
| 016 | GOMAP `families.L5_selfheal` position_reconciler suspect_orphan+maturity=production | 字段一致；AST 精确导入者 **0**；**但普查漏了同名双物**：`src/zephyr/ex_core/position_reconciler.py` 是**活链**，被 4 处 import（`ex_core/eod_reconciliation.py:47`、`ex_core/risk_layer_orchestrator.py:143`、`trading/recon_runner.py:78`、`scripts/start_paper_session.py:99`）。即"持仓与券商不一致无自动纠偏"这条**影响叙述不成立**，真症状是"同一职责两份实现、僵尸那份在册" | 对象真、影响错 | 仍成立 | 亲验 |
| 017 | GOMAP L5_selfheal `reconciliation_loop` suspect_orphan | 字段一致；AST 精确导入者 **0**、stem 命中 **0**（全仓 `reconciliation_loop` 只在该文件自身与其 docstring） | 一致 | 仍成立 | 亲验 |
| 018 | GOMAP L5_selfheal `blueprint_code_reconciler` suspect_orphan | 字段一致；AST 精确导入者 **0** | 一致 | 仍成立 | 亲验 |
| 019 | `python scripts/governance/d8_doc_sync/algo_flow_reverse_orphan_reconciler.py --json` | `{"scanned":3231,"orphans":0,"broken_source_references":0,"unreadable":2}` | **逐字段一致** | 仍成立（**阴性证据条目，不计断点**） | 亲验 |
| 020 | `grep -rn build_execution_report --include=*.py src scripts` → 仅 3 命中、零 import 零调用 | 命中 **10**；关键差异＝出现**真调用**：`src/zephyr/ex_core/execution_report_producer.py:70` import、`:363 report = build_execution_report(order, record)`；生产端已装配：`adapters/qmt_file_bridge_integration.py:40,160 broker.attach_execution_report_producer(producer)`，且 `_enable_execution_report = True` 默认开；再上游 `ex_core/qmt_trading_session.py:41` import 该装配件 | **不一致：已闭合** | **已闭合** | 亲验 |
| 021 | `grep -rn hedge_execution_skill --include=*.py src scripts` → 5 命中全为自身头注释 | 命中 **9**；新增真 import：`src/zephyr/risk/paper_hedge_leg.py:67 from zephyr.risk.hedge_execution_skill import (...)`，且 `src/zephyr/risk/__init__.py` 工作区已加 `from zephyr.risk.paper_hedge_leg import PaperHedgeLeg` + `__all__` | **不一致：症状消失但闭合件未入库** | **已闭合（条件）** | 亲验 |
| 022 | 读 `known_data_gaps.yaml` 该条 status + grep 写入器 + schedule 槽位 | status 实测 = **`completed`**（普查记 `monitoring`）；`root_cause` 保留、`resolution_plan` 尾部由 `st-ff-dag-20260918` 写明复核与改判理由；`scripts/data/run_nightly_sentiment.py:41-42` 与 `schedule.yaml:169-172 nightly_sentiment cron "20 8 * * *"` 均在（与普查一致） | **不一致：台账已自更新** | **已闭合** | 亲验 |
| 023 | `python .runtime/tmp/ff-mine0/dg_census.py` → `decision_build: [["planned","213"]]` | `decision_build [["planned","213"]]` 逐字一致；旁证 `decision_node_count=213`、`decision_edge_count=211` | **逐字一致** | 仍成立 | 亲验 |
| 024 | `dg_agg.py` → `decision_layer_track_counts: [['placeholder','1744'],['model_driven','10']]` | 实测 `placeholder **1749** / model_driven **10**`（总 1754→**1759**）；真实 10 层 ✓；其中 `design_maturity=design 且 build_status=planned` 恰 **6 层＝L2A 信号层 / L2B 主力行为层 / L2C 市场状态与大盘预测层 / L2D 知识图谱与因果推演层 / L5 学习层 / L6 自评估层**（逐字一致）；99.4% 占比不变 | 结构一致、计数漂 +5（战役在途新增占位） | 仍成立 | 亲验 |
| 025 | `python -c "...strategy_production_map.yaml['nodes'] 里 node_id=='FAC-E7'"` | `{'node_id':'FAC-E7','stage':'E7','build_status':'pending','module_ref':None, ...}` | **一致** | 仍成立 | 亲验 |
| 026 | 同脚本遍历 build_status 分布 | 16 节点：`built 4 / partial 11 / pending 1`；built=`FAC-E1A,E4,E5,E6` ✓、pending=`FAC-E7` ✓、partial=`E0,E1,E1B,E1C,E1D,E1E,E1G,E2,E3,E8,E9` ✓ 逐个一致 | **逐 ID 一致** | 仍成立 | 亲验 |

### 闭合证据（判 `已闭合` 必附）

| BRK | 闭合它的 commit / 磁盘件 |
|---|---|
| 004 | `49dde8fda5`（2026-09-16 02:40，"治理加法批 A3+A4 production 接线（裁定#254 Owner 门位放行）——kill switch 开机即编排"）；追加 `7b451b7f76`（09-18 19:09 保命链批1，注册 MOD-AU-004 唯一权威 dispatcher）。`git show --stat 7b451b7f76` 的 commit body 自带一条更正："BRK-004/005 普查记载陈旧更正：A3/A4 接线已于 2026-09-16 落地" |
| 005 | 写方 `49dde8fda5`；读方 `7b451b7f76`（`emergency_track_guardian.py` 由该 commit `--diff-filter=A` 新增，实测 `git log --diff-filter=A` 唯一命中） |
| 020 | `175f837e89`（2026-09-18 **19:41**，"[FLOWTHROUGH][FF-12] G1 治本：execution_report 生产端四件套原子落地"）——晚于普查落笔（`01_break_census.md` mtime 09-18 **17:47**）1h54m |
| 021 | **仅磁盘件**：`src/zephyr/risk/paper_hedge_leg.py`（`git ls-files --error-unmatch` 报 did not match → **UNTRACKED**）+ 工作区 `src/zephyr/risk/__init__.py` 未提交改动。**无 commit 证据** |
| 022 | `23311f9e73`（2026-09-18 19:36，"[FLOWTHROUGH][FF-01] datagap 车道登记批"）——`git log -L 416,424:src/zephyr/data/config/known_data_gaps.yaml` 命中该 commit 把 status 由 monitoring 改 completed |

---

## 3. 第 11 族：入口冒烟清单（普查 A/B 族检出面盲区）

普查只判"有没有人调"，不判"被调会不会当场炸"。本车道对 A/B 族涉及文件做了**两级冒烟**，结论先行：

### 3.1 第一级 `python -c "import <mod>"` —— **35/35 全部 rc=0，一条都没炸**

（清单=生命周期 9 + kill_switch_orchestrator / last_resort_watchdog / emergency_track_guardian /
escalation_engine / hot_plane_budget / position.position_reconciler / ex_core.position_reconciler /
reconciliation_loop / blueprint_code_reconciler / all_skill_modules / skill_discovery /
capacity_assurance 8 + execution_report / execution_report_producer / hedge_execution_skill /
paper_hedge_leg / nightly_sentiment_window + 两个对照件；`-B` 跑，`PYTHONDONTWRITEBYTECODE=1`，
全程零写入，事后 `git status` 差异仅他道在途件）

⇒ **裸 import 冒烟不是第 11 族的探测器**。它把 sys.path[0] 固定为仓库根，恰好绕开了 z-verifier3
抓到的两种崩法的触发条件。若只按作业书做 `python -c "import <mod>"`，本切片会报"零崩点"，
把 V3-N01/N02 同型问题全部漏掉。

### 3.2 第二级「按文件方式装载 + cwd=该文件自己的目录」（模块级代码执行，`__main__` 不执行）

真实崩点（已剔本车道装载器自身的噪声，见 §3.4）：

| 崩点件 | 崩法 | 根因（本车道现场定位） |
|---|---|---|
| `src/zephyr/ex_core/execution_report_producer.py` | `ModuleNotFoundError: No module named 'schemas.categories'` | 模块级 `from schemas.categories.intraday.market_execution_report import ...`；`schemas` 是**仓库根的顶层包**（实测 `D:\ZephyrAlpha\schemas\__init__.py`，不在 `src/` 下），只有仓库根进 sys.path 才解析。**此件=本切片（BRK-020 的闭合件）自带 V3-N01 同型缺陷** |
| `src/zephyr/alt_data/cohort_daily_ledger.py` | 同上 | 同上（对照件，独立复现 z-verifier3 的 V3-N01） |
| `src/zephyr/data/ch_parts_monitor.py` | `AttributeError: module 'calendar' has no attribute 'day_abbr'` | `src/zephyr/data/calendar/` 是**带 `__init__.py` 的真包**，当 sys.path[0]=`src/zephyr/data` 时**遮蔽 stdlib `calendar`**；一条零项目代码的一行式即复现：在该目录 `python -B -c "import calendar"` → 本地包 `__init__` → `zephyr.data.__init__` → `data_service` → `shared.contracts` → `import pandas` → `Lib/_strptime.py:96 calendar.day_abbr` → 炸 |

### 3.3 对 z-verifier3 第 11 族的一条**改判**：V3-N02 不是"两种崩法两种根因"，是"一个根因两个症状"

同一次复现里，两条 traceback 出自**同一进程、同一遮蔽链**：先是 `_strptime` 撞上被遮蔽的
`calendar`（`no attribute 'day_abbr'`），紧随其后 `service_registration failed:
partially initialized module 'pandas' has no attribute '_pandas_datetime_CAPI'`
——后者正是 z-verifier3 在 FF-04 记为"另一种崩法"的那条。
⇒ 建议把 V3-N02 从"同对象不同根因，登记两症状"**收敛为一条根因**：
**`src/zephyr/data/calendar/` 目录名遮蔽 stdlib**。修复难度从"两处排查"降为"一次改名"（改名是施工，本车道不做）。

### 3.4 冒烟噪声（诚实标注，不计入崩点）

- `zephyr.governance.escalation.escalation_engine`：第二级报 `cannot import name 'EscalationEngine'`＝
  本车道装载器把模块注册进 `sys.modules` 后与 `zephyr/governance/escalation/__init__.py` 的再导入成环，
  裸 import（第一级）rc=0 ⇒ **装载器伪影，不是断点**。
- 第一版装载器另有 11 件报 `AttributeError: 'NoneType' object has no attribute '__dict__'`（未注册
  `sys.modules` 导致 dataclass/typing 自省失败）⇒ 全部为伪影，已在 v2 修掉，**不写入崩点清单**。
- `zephyr.infrastructure.capacity_assurance.contracts`：路径映射为 `contracts.py` 未命中，改按
  `contracts/__init__.py` 后 rc=0。

### 3.5 第 11 族的**分母**（普查/尺子都没给过的量）

- 直接位于 `src/zephyr/data/` 下的 `.py`：**67 件** ⇒ 任何一件被"以文件方式"启动都会撞 `calendar` 遮蔽。
- `src/**` 里 import 顶层 `schemas.` 的文件：**23 件**，其中**模块级（顶格）导入 11 件** ⇒ 11 件在"仓库根不在 sys.path"的宿主里**import 期即崩**（与 V3-N01 同型）。
- `src/` 下与 stdlib 同名的目录：除 `calendar` 外另有 2 处名为 `io` 的目录（同类遮蔽候选，本车道**未做崩验**）。
- 本车道列表内带 `__main__` 块（即可能被当入口跑）的 A/B 件只有 3 件：`risk/paper_hedge_leg.py`、
  `alt_data/cohort_daily_ledger.py`、`data/ch_parts_monitor.py`；**其余 32 件是库件**，
  其"以文件方式启动"在现行装配下不会发生，故 `execution_report_producer` 记为**同型隐患**而非现行断点。

---

## 4. 修正建议（本车道**不改** `01_break_census.md` 原件；改原件归总包或专门车道）

### A. 应从普查正文划掉（判 `已闭合`，附 commit）

1. **BRK-004 / BRK-005 → 移出 A 族**。二者闭合于 `49dde8fda5`（**09-16 02:40**），普查落笔 09-18 17:47，
   即**断点在被登记成断点之前就已闭合 2 天**。这不是 R-041（当天治好仍挂账），是 R-041 的加重形态，
   建议单立一条失效记账：**「以散文注记为证据源 ⇒ 普查可以把两天前的已闭合项当新断点登出」**。
2. **BRK-020 → 移出 B 族**，闭合件 `175f837e89`（09-18 19:41）。
3. **BRK-022 → 移出 B 族**，闭合件 `23311f9e73`（09-18 19:36），且台账真源 `known_data_gaps.yaml` 已自更新为 `completed`（普查该条的"影响"栏"会误导后续派工"已不成立）。
4. **BRK-021 → 挂"待落地"而非"已闭合"**：闭合件 `src/zephyr/risk/paper_hedge_leg.py` 实测 **UNTRACKED**。
   连带风险：工作区 `src/zephyr/risk/__init__.py` 已 `from ...paper_hedge_leg import PaperHedgeLeg`——
   **若 `__init__.py` 先于该未跟踪件被提交，`import zephyr.risk` 将全域炸**（风控域全包消费者受害）。
   同批未跟踪的还有 `config/paper_hedge.yaml`（实测 `git status --porcelain` 报 `??`，本车道未碰）
   ⇒ 该车道是"代码+配置两件套"都浮在仓外，一件落地一件漏 = 直接炸。
   本车道只读不动，移交总包：要么把三件同批收编，要么把 `__init__.py` 的 import 撤出。

### B. 应改判 `口径不符`（数字或因果要重写）

5. **BRK-002**：族分布七个数**相加=90，与自身总数 95 矛盾**；实测三套口径（全量 24/21/26/3/10/11/0、
   maturity=production 19/18/24/3/9/9/0、剔除 maturity 空白 19/18/24/3/9/9/0）均无法复现。建议只保留
   `wiring dist 244/71/95/6`（可复现），族明细改为**生成器产出**（宪法 §9.5"条目清单禁手工维护"）。
6. **BRK-007**：① 证据命令指向的归档脚本在仓库根跑出 `src modules: 0`，**命令自身失效**；
   ② "3477 / 1593 / 1585" 不可复现，同语义重跑为 **3480 / 1685**（+92），Top1 已是
   `gov_enforcement.commit_gates 88`（归档件记 11），普查 Top 表整块需重出；
   ③ 建议把"权威口径"从三套里显式选一并写死在条目的 `口径` 字段——实测三套为
   **GOMAP 95 ｜ 裸 AST 1685 ｜ 装配超期门禁 `check_wiring_orphan.py` = orphans 0**（其册
   `wiring_registry.yaml` 313 条中 **304 条 wiring_status=exempt(97.1%)、generated_at 2026-08-27**），
   三套差 **16 倍以上且互为矛盾**，且被普查 §J.5 点名为"权威口径"的那个门禁**自免 97%、3 周未重生成**，
   不具备权威性。**"哪个是权威"这一问，目前没有答案，须 Owner 立项定口径**。
7. **BRK-008**：**因果方向说反**——`最后同步：2026-08-17` 是生成器自身 commit 日的幂等派生
   （`_common.idempotent_timestamp`，为宪法 §11.1.1"禁 datetime.now"而设计），**不是快照年龄**；
   真源 DB 是活的（`nodes 12022 / edges 22843 / 孤儿 388`，域 `updated_at=2026-09-18T13:06Z`）。
   该条应改写为真问题：**手册 AUTO 块与真源 DB 差 130 节点 / 680 边，且重生成结果（388/22845）
   仍躺在工作区未提交**——即"生成器产物入册滞后 + 成品未落地"，而非"快照过期"。

### C. 应改写影响叙述（对象真、后果错）

8. **BRK-016**：`zephyr.position.position_reconciler` 确为零入度，但**同职责活件是
   `zephyr.ex_core.position_reconciler`**（4 处 import）。"系统持仓视图与券商实际不一致无自动纠偏"
   **不成立**；应改为"**持仓对账两份实现并存，僵尸那份在册且 maturity=production**"（与 BRK-064
   的 KS/CB 重复族同根因，建议归并到"重复实现收敛"一簇，别单列保命级）。
9. **BRK-003**：证据是 9 件，正文写"**整族** L0 引导/收尾链零消费"。实测该族 **72 件、24 件孤儿**，
   9/72=12.5%，"整族"是夸大。建议改"整族"为"L0 族 9 个编排件"。
10. **BRK-011**：删去"（FBL 三域 213 节点）"——depgraph 无 FBL 前缀节点（0 命中），反馈只有一个域
    `D_FEEDBACK_LOOP`（240 节点 ✓）。主体 200 件零入度 ✓ 不动。
11. **BRK-015**：孤儿数 8 → **7**（`host_resource_governor` 已由 `7b451b7f76` 接进 `process_reaper`）。
12. **BRK-001**：总数 95 不动，但建议加一行"其中 ≥1 件（capacity_assurance.host_resource_governor）
    经实测已于 09-18 闭合，GOMAP 因 `generated_at=2026-09-16T23:41` 未重生成仍挂账"——
    **95 是两天前的数，不是今天可施工的数**。

### D. 给普查取证方法的建议（比改单条更值钱）

13. **GOMAP 有两个真源层，普查混用了**：`families.*.wiring`（AST 机生，可复现）与
    `pipeline.layers[].disconnected[].note_zh`（**人写散文，不可复现**）。本切片 2 条误判（BRK-004/005）
    全部来自后者。建议普查作业簿加一条硬判据：**A/B 族条目只允许引 `wiring` 字段或自己重跑的命令，
    禁引 note 文本作证据**。
14. **普查证据命令必须"逐字可跑"**：`orphan_scan.py` 与 `dg_*.py` 五个复现脚本里，只有
    `dg_census.py / dg_agg.py` 能跑出与记载同量级的数；`orphan_scan.py` 已坏（恒 0），
    "修正版"从未归档。建议后续车道**改完脚本必须回填自己的 tmp 目录并登记文件名+sha**。

---

## 5. 未跑与不跑清单（如实标注）

**26 条主证据命令：全部复跑，0 条未跑。** 以下为**子项/外延**未做，逐条给原因：

| 未做项 | 原因 |
|---|---|
| BRK-010 "需辨真伪"（access_control 73 件逐件真伪） | 需要 RBAC 动态注册面口径，属 §J.5 派给 FF-14 子挖矿的活；本切片预算用于把 26 条主证据跑实，不越界代做 |
| BRK-011 子项"FBL 三域 213 节点"的证伪 | 已做（0 命中，见 §2 该行）——标 `未获证`，不牵连整条判态 |
| 33 件 A/B 件的**②向真跑**（作为入口执行） | 红线：真跑 `cohort_daily_ledger` / `ch_parts_monitor` 会写 ClickHouse，本车道只读；已用"模块级装载、`__main__` 不执行"的第二级冒烟替代（§3.2） |
| `src/zephyr/data/` 其余 64 件的遮蔽崩验 | 已用一条零项目代码的 `import calendar` 定根因，逐件跑属重复取证（施工后复测更省） |
| 2 处名为 `io` 的目录遮蔽验证 | 同上，只登记候选未验崩 |
| `generate_governance_map.py` 重生成以自证 95 | 该生成器**写 `config/governance_operations_map.yaml`**（注册表/config），本车道禁写；改用"同语义只读重算 AST"替代（`rv_scan.py`） |
| 普查其余 59 条（C..I 族） | 不在本车道切片 |

---

## 6. R-018 高风险判断表（本文内所有可能让总包改派工的判断）

| # | 判断 | 依据等级 | 若我错了会怎样 | Max 一条验真命令 |
|---|---|---|---|---|
| 1 | BRK-004/005 是"普查时已闭合 2 天"，而非"普查后被人治好"（→ R-041 加重形态新记账） | 亲验 | 总包把"普查后自愈"的节奏判断带偏，误估施工吞吐 | `git log -1 --format="%h %ad" --date=iso 49dde8fda5 && ls -l --time-style=full-iso docs/_working/fullflow_campaign/skeleton/01_break_census.md` |
| 2 | 可信分母：A/B 26 条里"仍成立 18 / 口径不符 3 / 已闭合 5"，A 族孤儿面**没有 95 那么多、也没有 1685 那么可施工** | 亲验 | 下游派工按 95 或 1685 排产能，两头都错 | `python scripts/governance/extract_depgraph.py --summary \| head -5 && python .runtime/tmp/st-ff-rv1-20260918/rv_scan.py \| head -3` |
| 3 | V3-N02 的两种崩法＝**同一根因**（`src/zephyr/data/calendar/` 遮蔽 stdlib），修一次即可 | 亲验 | 两条车道分头治两个"不同 bug"，其中一个白干、另一个改错地方 | `cd src/zephyr/data && python -B -c "import calendar,traceback;print(calendar.__file__)"` |
| 4 | `paper_hedge_leg.py` 未跟踪 + `risk/__init__.py` 已引它＝**一颗全域炸雷**（风控域 import 面） | 亲验 | 某车道只提交 `__init__.py` → `import zephyr.risk` 崩，连坐所有风控消费者与提交门禁 | `git ls-files --error-unmatch src/zephyr/risk/paper_hedge_leg.py; git diff -- src/zephyr/risk/__init__.py \| head` |
| 5 | 普查 §J.5 点名的"权威孤儿门禁" `check_wiring_orphan.py` 实为 97% 自免（304/313 exempt）、册子 3 周未重生成 ⇒ 不能当权威口径用 | 亲验 | 后续车道拿 `orphans=0` 当"无孤儿"结论，A 族断点被整体判没 | `python scripts/governance/check_wiring_orphan.py; python -c "import yaml,collections;d=yaml.safe_load(open('docs/01_policies_and_standards/_registry/catalogs/wiring_registry.yaml',encoding='utf-8'));print(collections.Counter(x['wiring_status'] for x in d['modules']),d['generated_at'])"` |
| 6 | `schemas` 是**仓库根顶层包**，11 件模块级 `import schemas.*` 的 src 件在任何非仓库根宿主里 import 期即崩（第 11 族的结构性成因，不是两个孤立 bug） | 亲验 | 逐个修脚本，漏掉整族；E7 模拟盘前哨（BRK-025）接线时再炸一遍 | `python -B -c "import schemas;print(schemas.__file__)" && grep -rn "^from schemas\.\|^import schemas" --include=*.py src \| wc -l` |
| 7 | BRK-016 的影响叙述（"持仓无自动纠偏"）不成立，真活链在 `ex_core/position_reconciler` | 亲验 | 保命级施工被排进"新建对账器"，与既有件重复第三份 | `grep -rn "from zephyr.ex_core.position_reconciler import" --include=*.py src scripts` |

**低风险的其余 19 条判定**：逐条依据等级均为 `亲验`（原始命令逐字复跑），无转报、无推断。
