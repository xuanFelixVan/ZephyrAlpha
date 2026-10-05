---
ttl: task_bound
completes_when: 两道 CH 门禁报红改造落 dev＋本卷派单被总包接件分派
session: st-ff-chfail-20260926
creation_token: probe-fail-red-01-casefile-probe-green-lies-20260925
---

# 案卷：可观测面"探测失败被读成没问题"同型族普查与处方

- 车道：`lane_ff_chfail`（会话 `st-ff-chfail-20260926`），B 队，2026-09-26
- 病根事件：ClickHouse 累积 187 个 0 字节 part ⇒ `system.*` 查询**永久失败**
  （已由他道 `bb09a39848` 清障）。依赖它的两道门禁失灵的姿势是**装绿灯**，不是报红。
- 本卷分三部分：①已修（本道落地）②同型族普查表（只登记处方，不动他道代码）③永久尺。

## ① 本道已修（两道 CH 门禁）

机制根因唯一：**探测失败的返回值与"探测通过"的返回值不可区分**
（`ch_writer.query()` 对 TCP 失败 / HTTP 失败 / 零行 **同返空串**）。

| 件 | 改法 |
|----|------|
| `src/zephyr/data/ch_parts_monitor.py` | 新增三态原语 `probe_readonly()`（OK/EMPTY/ABSENT/UNAVAILABLE）；`check_parts_threshold` 在 UNAVAILABLE 时**抛 `ProbeUnavailableError`**（旧：`log.warning`+`return []`）；`check_and_alert` 先另发一条 CRITICAL `ch_data_parts_probe_unavailable` 再抛；`main()` 退出码 0/1/**2**（2=监控瞎了，与 1=看见问题分开）。INVARIANTS/ERROR_CONTRACT 契约头同步改判。 |
| `src/zephyr/gov_enforcement/commit_gates/ch_final_gate.py` | `_resolve_engine`→`_probe_engine`（engine/absent/unavailable 三态）；判据②的"引擎不可解析"由 **WARNING+放行** 改为 **GateSpec passed=False**（红）；待检文件读不到亦计红（看不见=没判定）；红字含"哪张表哪个查询、是连接失败还是元数据缺失"+修法。三态探针不复制真源，延迟 import 复用 `ch_parts_monitor.probe_readonly`。 |

语义分流（两条都要，缺一即偏）：
- **表/库确实不存在** ⇒ 按语义 0 违规（可绿），但如实上报 `absent`，不混进故障账；
- **查询失败** ⇒ 必红。二者由"同一数据源上的聚合探针"（恒返一行，故空串=该面不可查）
  与"存在性探针"（答 "0"=不在册）拆开。
- 反例教训：用 `SELECT version()` 探活**不足以**定性——`SELECT 1` 存活而 `system.*` 全灭
  正是本次事故的真实形态，故聚合探针必须打在**被依赖的同一张系统表**上。

实测读数（本道复验）：
- 正常（真 CH 在线）：`OK: 无分区 active parts 超阈值（30）` → RC=0；
- 打挂 `system.*`（保留 `SELECT 1`）：`PROBE FAILED: [system.parts(active=1)] 探测失败（unavailable）⇒ 读数不可信，不得按零违规放行。元数据面故障：SELECT 1 存活但 … 均无应答（2026-09 事故同型＝破损 0 字节 part 使 system.* 永久失败）` → **RC=2**；
- 全通道失联：`连接失败：SELECT 1 亦无应答（…）` → RC=2；
- 门禁侧：`_probe_engine` 三态实测 = `('engine','ReplacingMergeTree')` /
  `('absent', '表 … 不在 system.tables 在册…')` / `('unavailable', '元数据面故障…')`。

## ② 同型族普查表（**只登记处方，不动他道代码**——交总包派单）

机检：AST 扫 `src/zephyr` + `scripts` + `tools`，筛"可观测面函数 try 体发起查询/探测、
except 只 log 或 return falsy"（A 族）、"查询返回值以空做真值判定"（B 族）、
"巡检 CLI 异常路径 return 0"（C 族），命中 309 处；按族去重+人工核读者语义后
定 **15 条同型面**（下表）。★=与本道两件同一形状（已核实调用方据此判绿）。

| # | file:line | 失败时的读数 | 应为哪种 | 归属 |
|---|-----------|-------------|---------|------|
| 1 | `src/zephyr/data/ch_parts_monitor.py:107`（改前） | `log.warning`+`return []`，`main()` 退 0 打 OK | UNAVAILABLE⇒抛错/退 2 | 本道已修 |
| 2 | `src/zephyr/gov_enforcement/commit_gates/ch_final_gate.py:180-187,285-291`（改前） | 引擎不可解析⇒WARNING+放行 | unavailable⇒passed=False | 本道已修 |
| 3 ★ | `src/zephyr/gov_enforcement/commit_gates/reconciler_health_gate.py:150-154,170-174` ⇒ `:261` | 两个查询都失败⇒`blocks=[]/warns=[]`，门**返回 `True, "reconciler health OK (0 block_next, 0 critical_warn in last 24h)"`** | 查询失败⇒红；至少不得把未知印成 "OK 0 条" | 提交门道 |
| 4 ★ | `src/zephyr/governance/audit/reconciliation_registry.py:1596-1599`（critical_warns）、`:1695-1698`（blocks） | 治理库查询失败⇒`return []`，上游（含 #3）读成"零失败" | OperationalError(表不存在) 与连接失败分流；后者⇒UNKNOWN 且出声 | 治理审计道 |
| 5 ★ | `src/zephyr/governance/audit/remediation_progress_reconciler.py:268-270,312-314` | `except Exception: return []`（覆盖 sqlite 连接失败）⇒ 判"无超期维度" | 同 #4；reconciler 侧须能表达"本轮未判定" | 治理审计道 |
| 6 | `src/zephyr/governance/audit/schedule_consistency_reconciler.py:435-439` | `OperationalError⇒[]`，status 把"读不到"当"无执行记录" | 区分"库未建"（首启合法）与"查询失败" | 治理审计道 |
| 7 ★ | `src/zephyr/governance/audit/pg_probe.py:219-226` | 状态文件缺失/陈旧/坏⇒`pg_probe_shows_offline()` 返回 False（"未知"并入"在线"） | 第三态 UNKNOWN 须单列并出声（现在只有 reachable=not-known） | 基础设施道 |
| 8 ★ | `scripts/ch/verify_schema_truth.py:356-363` | `--ci` 下 CH 连不上⇒`[WARN] 跳过`+**`return 0`**（=门禁通过） | 不可测⇒非 0，或要求显式 allow-skip 旗并落审计 | CH/数据道 |
| 9 ★ | `scripts/ch/verify_exchange_coverage.py:399-408` | 同上（ping 失败 + `--ci` ⇒ return 0） | 同 #8 | CH/数据道 |
| 10 ★ | `scripts/ops/ch_health_probe.py:146-147` | tick 新鲜度检查任何异常⇒`log.warning`+return，**断供与探针故障同读数**；`_real_ch_ping` 异常⇒False 但主循环保活计数不区分 | 探测自身失败须告警（与"链路断供"分别计） | CH/数据道 |
| 11 | `scripts/automation/flowthrough_verifier.py:719-733,741-788` | 已建 `-2 UNMEASURABLE` 好面，但探活打在 `SELECT version()` 上（与 `system.parts` 不同源），且 `unmeasurable_tables` 不进退出码 | 探活须打在**被依赖的同一数据源**；不可测面占比过高⇒退出非 0 | 全链验证道 |
| 12 | `src/zephyr/data/backfill_checker.py:624-629` | `ch_reader.query` 空串⇒`set()`；基线日查询失败=该日"无缺口"（静默绿） | 走三态原语；不可测日须显式标 unavailable 而非跳过 | 数据道 |
| 13 | 家族级：`src/zephyr/gov_enforcement/commit_gates/_diff_helpers.py:264-272`、`_tree_view.py:651-653,673-675`、`vocab_hardcode_gate.py:96-100,145-152`、`bare_getenv_gate.py:186-190,233-241`、`new_file_depgraph_gate.py:163,193`、`depgraph_pre_registration_gate.py`、`rename_depgraph_sync_gate.py` | `git diff`/depgraph 查询/子进程超时 ⇒ `logger.warning` + 返回空集 ⇒ 门"无可检文件"而绿（检测器失效与零违规同读数） | 统一处方：检测器失效计 `gate_failure`（可 warn 级不阻断，但必须落账并在门输出里显式写 "NOT EVALUATED"），禁把空集当零违规 | 提交门道（一次改族，勿逐门） |
| 14 ★根因 | `src/zephyr/data/ch_writer.py:426-483` | `query()` 对 TCP 失败/HTTP 失败/零行同返 `""`；`get_table_engine():776-805` 同病并把失败值**写入进程内缓存**（一次抖动⇒该表永久"不存在"） | 治本位：`query` 返回三态或提供 `query_checked()` 抛错版；引擎缓存不得缓存失败值。全仓 CH 读面受影响，须专道派单+回归 | 数据层道 |
| 15 | `src/zephyr/data/ch_reader.py:95-140` | `count()` 失败⇒0、`query_table()` 失败⇒""；`inject_final` 吞引擎查询异常⇒**静默不注入 FINAL**（正是要防的未去重读） | 随 #14 同批改判；`inject_final` 失败至少要出声 | 数据层道 |

处置约定：#3-#15 **本道未动一刀**（跨道越界禁止）。派单优先级建议 #14（根因）→ #3/#4/#5/#8/#9
（已核实调用方据此判绿）→ 其余。永久尺 `tests/governance/test_probe_failure_must_report_red.py`
只钉本道两件与可复用的三态原语；各道改自己那条时，请按该尺的形状补阳性/阴性例。

## ③ 净零与复用声明

- 未新增 gate、未新增注册册、未新增脚本；`probe_readonly` 落在既有模块
  `zephyr.data.ch_parts_monitor`，供 #2 复用（禁第二真源），也作为 #4-#15 的落地模板。
- 契约头（INVARIANTS/ERROR_CONTRACT）与被测行为同批改；ALGO_FLOW 外部件
  `docs/03_modules/_domain_data/algo_flow/ch_parts_monitor.yaml` 未随批刷新（其"源码 L152-L163"
  行号在本批之前即已漂移，属他道衍生件，登记不代改）。
