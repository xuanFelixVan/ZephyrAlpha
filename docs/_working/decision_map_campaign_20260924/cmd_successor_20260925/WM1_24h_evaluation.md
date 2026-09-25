---
ttl: task_bound
title: "W-M1 双轨 24h 三判据补跑评估（LANE-WM1 · 2026-09-25 21:20 实测）"
session: st-qmine-20260925
lane: LANE-WM1
---

# W-M1 双轨 24h 三判据补跑评估

> 车道=LANE-WM1（执行人）·总筹=st-qmine-20260925·评估对象=W-M1 Phase 1 双轨并行观察窗
> 性质=**漏跑补评**：原应 09-25/09-26 正午由守望器自动跑，实测自动化断链（证据见 §1.4）
> 本卷只出材料，不做任何翻转动作（flag 出厂翻转=Owner 门位，见 §5）

## 0. 结论一览

| 判据 | 阈值（真源原句，未放松） | 实测（本卷 §2） | 判定 |
|---|---|---|---|
| ① 高峰并发期零漂移 | 17 号文 §八：「高峰并发期（小时级 done≥10）零漂移」；漂移机械口径=baseline.py:615 | 窗内确有 2 波 done≥10（09-24 22:xx=18、09-25 11:xx=11 笔/时）；峰后首跑 09-25 13:11 实测需**人工**回填 95 条+吸收 9 条才归零，该次报告 verdict=**Phase 0 FAIL**；13:12 复跑才全绿；21:20 只读复算缺账 26 条+同键 sha 差 2 条+**未解释漂移 2 条**（21:30 由自动探针回填/吸收后，未解释 2 条仍在） | **不绿** |
| ② 对账零异常 | 17 号文 §八：「对账零异常」 | 名义 24h 点（09-25 12:30）**自动对账执行 0 次**（探针载体 09-25 21:27:21 才换血，commit 437b1dbf15 代码 12:56 才入 HEAD）；21:30:11 / 21:34:37 自动跑 2 次，**首跑即报 1 册 zero_unexplained_drift=False**；窗内手动 6 次中 1 次 FAIL | **不绿** |
| ③ 11 读端零改动 | 17 号文 §八：「11 读端零改动」；名单真源=03 号文 §1.3（:57-69） | 9/11 窗内零提交；registry_yaml_parse_gate.py +1（09-25 12:56，**即 W-M1 波0 本车道**，未武装态 fail-open）；create_guard.py +1（09-25 19:36，他车道 st-commitspeed-tbl，非 W-M1）。读端结构契约实测零破坏（§2.3） | **不绿（严格字面）/有条件绿（按归因口径）**——口径待裁，本卷保守取不绿 |

**总判：三判据无一具备"全绿"资格 → 不具备提请 Owner 提前翻转的条件。处置=继续观察至 72h 兜底点（09-27 中午），差额见 §4。**

补充事实（不是判据但影响裁定）：**乙号文 §4 出口判据的第 3 条（快照 render 与盘上 YAML 逐字节一致）当前物理不可执行**——投影读端与快照写端 bundle 契约不一致（§3.1），实跑直接抛 `bundle 结构不符契约: 'sections'`。翻转前必修。

## 1. 真源坐标（判据/阈值/窗起点/门位）

### 1.1 三判据（唯一成文处）

`docs/_working/decision_map_campaign_20260924/17_quantified_acceptance.md:75`（§八 W-M1 双轨，已报备）：

> **24h 评估点（09-26 中午）**：高峰并发期（小时级 done≥10）零漂移+对账零异常+11 读端零改动，三项全绿→提请 P-3 提前翻转（新账本转正，旧账本备胎）。

同文件 `:76`：「72h（09-27 中午）：同判据兜底完全切换。」

仓内对"三判据"的另一处引用（`docs/_working/cmd_ledger/overnight_decisions_20260924.md:172`、`HANDOVER.md:21/68`、`19_gpu_plan_and_master_backlog.md:32/91`）均为**转引不枚举**，全仓 `git grep "三判据" HEAD` 仅此一处枚举 → 判据真源=17 号文 §八，无第二说。

### 1.2 漂移机械口径

`src/zephyr/governance/registry_ledger/baseline.py:615`：

    report["zero_unexplained_drift"] = report["content_mismatch"] == 0 and report["pg_only"] == 0

同函数注释（:467-469）定性：**PG 缺=补登记（可解释）**；同键异内容按 YAML 吸收（:548-585，可解释）；**content_mismatch 仅在 CAS 冲突（真并发）时计数**、**pg_only=PG 有而 YAML 无=未解释**。本卷一律照此口径，不自定义。

### 1.3 观察窗起点与时长

- 旗文件真源：`.runtime/registry_ledger/dual_track.enabled` 正文＝「dual_track started 2026-09-24T12:3x+08:00 by st-wm1-wave0-20260924 (P0 7 registries, insert-only+absorb reconcile, **72h window**)」
- 本卷补跑时刻：2026-09-25 21:20:43+08:00 → **已观察 32h50m**
- 窗内样本量：HEAD 新增提交 **151 笔**（09-24 12:00→09-25 21:35，按小时分布见 §2.1）/ 队列 done **142 件** / 账本 active 行 **22,677** 条（P0 七册）/ 事件表 **23,104** 行
- **口径歧义登记（不改判据，只如实报）**：17 号文把"24h 评估点"标为 09-26 中午，而旗文件起点=09-24 12:3x、72h 点=09-27 中午 ⇒ 09-26 中午实为 **48h** 点。两处真源互斥，本卷按"应跑未跑的 24h 点在 09-25 中午、现已 32h50m"从严评估。

### 1.4 断链取证（为什么漏跑）

| 环节 | 实测 | 证据 |
|---|---|---|
| 载体 cron（v1 automation-749df40e） | 已消失 | LEDGER_wave0.md:60（09-24 12:4x 在岗）→ :62（09-24 晚"发现消失"）→ 重建 v2 |
| 载体 cron（v2 automation-f250b992） | **被主动删除** | LEDGER_wave0.md:63「Cron v2 automation-f250b992 按 Owner'不需要定时'指令删除；双轨 24h 对账由 belt daemon 双轨探针（下纪元换血生效）或手动 wave0_phase0_gate.py reconcile 承接」 |
| 载体 cron（v3 automation-5f742031） | 总指挥 09-25 晚 HANDOVER.md:21 声称在岗且"勿删"，继任轮 21:00 实测 `qoder_cron list` 无此条、正午窗零执行痕迹 | cmd_successor_20260925/LEDGER.md §四 N-2 |
| 承接者 a：belt daemon 探针 | 代码 09-25 12:56 才入 HEAD（commit 437b1dbf15），**换血时刻 09-25 21:27:21**（PID 28424 命令行 `-m zephyr.gov_enforcement.rule_bridge.commit_belt_daemon`）⇒ 整个 32h50m 窗内探针**不在岗** | 进程 CIM 实测 + `git log -1 437b1dbf15` |
| 承接者 b：手动 reconcile | 窗内仅 09-25 13:11/13:12 两次（波0 收官自验），正午 12:00-13:00 **无执行痕迹** | .runtime/registry_ledger/ 目录 mtime 清单 |

**根因判定（一句话）**：真源之间存在互斥指令——LEDGER_wave0.md:63 记"Owner 说不需要定时"（口头、ruling_registry 查无，见 §5），17 号文 §八 又要求 24h/72h 定时评估；矛盾未消解 + 评估载体是仓外不可测的 cron ⇒ 断链是必然产物，不是偶发。**该矛盾归总筹/Owner 消解，本车道不代裁。**

## 2. 三判据逐项实测（取数口径可复算）

### 2.1 判据① 高峰并发期（小时级 done≥10）零漂移

高峰判定口径 A=队列落地回执（`.runtime/commit_queue/done/*.json` 的 `landed_at` 小时聚合）；口径 B=HEAD 提交（`git log --since --pretty=%ad --date=format:%Y-%m-%dT%H`）。

| 小时 | 队列 done | HEAD 提交 | ≥10？ |
|---|---|---|---|
| 2026-09-24T22 | **18** | **18** | 是（峰 1） |
| 2026-09-25T11 | 8 | **11** | 是（峰 2，按 HEAD 口径） |
| 其余 31 个小时 | ≤9 | ≤8 | 否 |

漂落实测（账本侧）：

- 上一次对账基线=09-24 12:23（`reconcile_20260924_122327.json`，PASS）→ 之后跨两个高峰 **24h47m 无人对账**。
- 09-25 13:11 首跑（`reconcile_20260925_131104.json`）verdict=**「Phase 0 FAIL (drift present)」all_pass=false**：七册合计 **回填 95 条 + 按 YAML 吸收 9 条 + 未解释漂移 1 条**（REG-CAPCAN-001 pg_only=1，即改名前的 projection/generator.py 旧路径行，后经意图 API retire 首战清账）。
- 09-25 13:12 复跑（`reconcile_20260925_131258.json`）才 all_pass=true（七册 zero_unexplained_drift 全 true）。
- 本卷 21:20 只读复算（零写，见 §2.4 口径）：距 13:12 已 **8h08m**，REG-CAPCAN-001 YAML 侧新增 20 条未入 PG、REG-MODULE-TRANSLATION-001 新增 6 条 + **2 条同键 sha 差（待吸收）** + **2 条 pg_only（未解释）**。
- 累积速率实算：20 条 / 8.13h = **2.46 条/小时** 缺账；72h 窗若不自动对账预计欠账 ~177 条。
- 21:30:11 / 21:34:37 自动探针两跑（本卷复核其落盘报告，见 §2.2）：26 条缺账已回填、5 条按 YAML 吸收、**未解释漂移仍 2 条** ⇒ REG-MODULE-TRANSLATION-001 `zero_unexplained_drift=False` 延续至今。

**判①=不绿**：真源阈值的"零漂移"在窗内至少两次不成立（13:11 报告自身 FAIL + 21:20 复算 1 册 False）；且"高峰并发期"的漂移恰恰需要**在岗的自动对账**才可能在窗口内被观测/消化，本窗内该机制为 0 次。

### 2.2 判据② 对账零异常

| 项 | 实测 | 取数 |
|---|---|---|
| 手动对账次数/结果 | 6 次（09-24 12:17/12:19/12:21/12:23、09-25 13:11/13:12），其中 1 次 FAIL | .runtime/registry_ledger/reconcile_*.json + 各文件 verdict 字段 |
| **自动对账次数/结果** | 名义 24h 点（09-25 12:30）**0 次**；09-25 **21:30:11 / 21:34:37 共 2 次**（换血后 3 分钟内起跑）：首跑七册合计 backfill 26 / absorb 2 / **pg_only 2 → 该册 zero_unexplained_drift=False**；次跑 absorb 3 / **pg_only 仍 2 → 仍 False** | `.runtime/registry_ledger/dualtrack_20260925_213011.json`+`dualtrack_20260925_213437.json` 逐册字段（本卷读盘复核，与 §2.4 只读复算逐项吻合=红证自校） |
| 探针载体在岗性 | 换血前（09-24 12:3x→09-25 21:27）**不在岗**：探针代码 09-25 12:56 才入 HEAD（437b1dbf15），daemon 现进程 PID 28424 起于 09-25 21:27:21 ⇒ **24h 点整段无自动执行者**；换血后 `run_daemon` 启动即调 `_projection_drift_probe`（commit_belt_daemon.py:785），21:30/21:34 两跑已证成 | CIM 进程清单 + `git log -1 437b1dbf15` + dualtrack 报告 |
| 窗内账本事件 | 合计 23,104 行：import 21,923 / reconcile_drift 1,173 / publish 7 / retire 1；reconcile_drift 细分=missing_in_pg_backfilled 755、content_mismatch 405、content_mismatch_absorbed_from_yaml 11、pg_only_no_yaml_entry 2 | `SELECT action,count(*) FROM registry_ledger.registry_event GROUP BY action` |
| 探针历史故障 | 09-24 23:15 一条 daemon 崩溃尾迹 `ModuleNotFoundError: No module named 'scripts.governance'`（.runtime/logs/belt_daemon_csx.log:2094 末段），即探针宿主在窗早期曾整段死循环报错 | 该日志尾部 |

**判②=不绿**：名义 24h 点（09-25 中午）自动对账执行数=0（载体未换血，探针代码当天 12:56 才入 HEAD）；窗内 6 次手动跑里有 1 次 FAIL；换血后 21:30 首跑仍报 1 册 False——三类都属"对账异常"（含"该跑没跑"与"跑了仍红"）。

### 2.3 判据③ 11 读端零改动

读端名单=03_projection_design.md §1.3（:55-69，11 个真实代码读端，全部读本地 YAML，零 PG 依赖）。逐个按 `git log --since="2026-09-24 12:30"` 计数：

| 读端（HEAD 路径） | 窗内提交 | 归因 |
|---|---|---|
| src/zephyr/gov_enforcement/commit_gates/registry_yaml_parse_gate.py | **1** | **W-M1 波0**（437b1dbf15 12:56，投影私改检测扩展；未武装态 fail-open） |
| src/zephyr/gov_enforcement/commit_gates/create_guard.py | **1** | 他车道 st-commitspeed-tbl（6e47377b8f 19:36，CREATE-GUARD 册解析进程内缓存） |
| capability_lookup.py / ssot_redefinition_gate.py / batch_creation_tokens.py / scaffold.py / architecture_health_dashboard.py / generate_project_depgraph.py / algo_flow_reverse_orphan_reconciler.py / agents_cheatsheet_drift_reconciler.py / metric_count_drift_reconciler.py | 0 | 零改动（9 台） |

读端契约（03 号文 §不变量 5：输出 YAML 必须让 11 读端零改动照常工作）实测零破坏：

- 顶层根键唯一（compose 判重）=0 重复；键序末位=`di_seam_exemptions`（值 `[]`）✓；`creation_tokens` 为 list（11,005 条）✓；`capabilities` 段在位（388 条）✓
- P0 七册 `yaml.safe_load` + `_split_registry_entries` 族切分全通过（本卷只读复算即依赖该路径，无一本册解析失败）

**判③双口径**：
- 口径 X（字面：窗内 11 读端文件零修改）= **不绿**（2 台有改动，含本车道 1 台）。
- 口径 Y（W-M1 施工面是否破坏其余读端/读端契约）= **绿**（其余 10 台 W-M1 零触碰，结构契约实测零破坏；且台账 LEDGER_wave0.md:60 当年即以"批3-6 改面仅 parse_gate/belt_daemon 两挂点且均为增量插段"作"零改动"实证——**该表述与 03 号文读端名单自相矛盾：parse_gate 本身就是 11 读端第 3 行**，登记为案卷瑕疵，不代改）。
- 本卷取**从严口径 X=不绿**，口径归总筹/Owner 定。

### 2.4 本卷取数口径与复算命令（全只读）

- 只读正门：`zephyr.infrastructure.database_service.DatabaseService().get_depgraph_conn(read_only=True)`（depgraph_reader 只读角色，技术阻断写入）。**本卷未执行任何写库/写 YAML/写 flag 动作**（未跑 `reconcile`，因 reconcile 设计即 insert-only+absorb=会写 PG 与事件表）。
- 七册只读复算=复刻 `reconcile_registry` 的读半（同一 `entry_composite_key` 身份 + 同一 `canonical_payload_sha256` + 同一 first-wins 去重），把"PG 缺/同键 sha 异/PG 独有"三类计数留内存不落库。
- 高峰分布：`git log --since="2026-09-24 12:30" --pretty=%ad --date=format:%Y-%m-%dT%H | sort | uniq -c`；`python -c` 聚合 `.runtime/commit_queue/done/*.json` 的 `landed_at`。
- 事件普查：`SELECT action,count(*) FROM registry_ledger.registry_event GROUP BY action`；`SELECT detail->>'kind',count(*) FROM registry_ledger.registry_event WHERE action='reconcile_drift' GROUP BY 1`。
- 载体在岗：`Get-CimInstance Win32_Process -Filter "Name='python.exe'"`（找 commit_belt_daemon）+ `Get-ScheduledTaskInfo ZephyrAlpha_BeltDaemon`。

## 3. 附带发现（判据之外，翻转前必须知情）

### 3.1 快照 bundle 契约断裂（阻断"逐字节一致"演练）

- 写端：`baseline.py:382-383` `publish_snapshot` 落 `bundle = {f"{family_key}||{entry_key}": payload}`（扁平 map）。
- 读端：`pg_source.py:54-74` `snapshot_from_bundle` 要求 `{registry_id, header_lines[], sections[{root_key,entries[]}], trailing_scalars[], ledger_revision, snapshot_version, content_sha256}`。
- 实跑：`load_latest_snapshot('REG-CAPCAN-001', …)` → **`ProjectionUnavailable: bundle 结构不符契约: 'sections'`**（本卷 §2.4 连接实测，快照 v1 于 09-24 12:16 发布在册 7 条，非"无数据"）。
- 全仓 grep `header_lines`：**无任何生产者**向 registry_snapshot 写该形状（只有 model/renderer 消费）。⇒ 两车道（乙=账本/丙=投影）各造一半契约，投影 PG 读路径目前**永不成立**；`--check` 因未武装直接返回 `quadrant="unmanaged", ok=True`（projection_generator.py:313-315），**不可当绿灯证据**。
- 后果：03 号文 §5 W3「影子期语义双跑」与乙号文 §4 判据 3「快照 render 逐字节一致」**均无可执行体**；P-3 翻转后的"私改自动纠正"实际能力 = 0。

### 3.2 PG 侧 2 条幽灵行（判据① 的未解释漂移本体）

`registry_entry` entry_pk 68209/68210（REG-MODULE-TRANSLATION-001 / family=entries / module_path=scripts/backtest/t0_rule_engine.py 与 t0_state_match_matrix.py），`created_at=2026-09-25 13:10:53`、`created_by=st-wm1-wave0-20260924`、事件 23526/23527 均 `missing_in_pg_backfilled`。

- 这两条被"按 YAML 吸收"自 **09-25 13:10 的盘上未提交变体**：`git log -S"t0_rule_engine" -- <翻译册>` 全史**零命中**（HEAD 从未有过该条目）。
- 之后注册册恢复批 v3（0b3724ed14，"emotion/candidate 冲突条目已对齐 HEAD 放弃盘面变体"）放弃盘面 ⇒ PG 留下 2 条 HEAD 从未存在的 active 行。
- 性质：双轨吸收机制把"盘上脏变体"当真源吃进了账本——这是 Phase 1「YAML=commit 真源」口径下的一处**口径漏洞**（应取 HEAD 版而非工作树版：`baseline.py:228-246 _iter_scan_entries` 读的是 `repo_root/path` 盘上文本）。21:30/21:34 两次自动跑继续按同一口径吸收（absorb 2+3 条），风险未收口。
- 处置建议=走意图 API `retire` 留痕（与 09-25 CAPCAN 旧路径行同法，LEDGER_wave0.md:63 已有一次成功先例）+ 对账读源改 HEAD blob，**但那是写库/改代码动作，归 LANE-LAND 与施工车道，本车道未动**。

### 3.3 观察覆盖的真实统计意义

窗内 32h50m，自动对账样本 = **2 次，且都在 09-25 21:30 之后**（名义 24h 点之前=0 次）；人工对账样本 = 6 次瞬时快照。**"连续观察"证据链仍不成立**：任何"7 天零漂移"（乙号文 §4 判据 1 与 D-5）与"3 天影子期"（丙号文 §5 W3/决策点 3）计数都尚未起算——最早起算点=09-25 21:30。

## 4. 裁定材料：继续观察至 72h 兜底点（不提请翻转）

**结论=三判据不绿，不向 Owner 提请 P-3 提前翻转**（原判据语义即"三项全绿才提请"，17 号文 §八）。差额清单（补齐即具备提请资格）：

| # | 差额 | 需要多少 | 归口 |
|---|---|---|---|
| 1 | 自动对账在岗且**跑绿** | 载体已复活（09-25 21:27:21 换血，PID 28424）并已产出 2 份 dualtrack 报告；**缺的是"七册全 true"的那一次**——现每跑必因 2 条幽灵行报 False | 差额 #3 一清即自动转绿；载体侧归 LANE-AUTO（把判据评估变仓内可测代码） |
| 2 | 缺账清零 | **已达成**：26 条（CAPCAN 20 + TRANSLATION 6）由 21:30/21:34 两跑自动回填，CAPCAN 现 11393==11393、另 5 条同键 sha 差按 YAML 吸收 | 无需人工动作（幂等），但要防 §3.2 口径漏洞再放大 |
| 3 | 未解释漂移清零 | 2 条幽灵行走意图 API retire 留痕（§3.2） | 注册表净删/条目退役=high 门位，须 Owner 或授权批次 |
| 4 | 判据③口径裁定 | 明确"11 读端零改动"是字面（含本车道挂点）还是归因（W-M1 未破坏其余读端） | 总筹→Owner 一句话 |
| 5 | render 通道修通 | 统一快照 bundle 契约（§3.1）并演练一次"快照 render 与盘上 YAML 逐字节一致" | 施工车道（代码件，非本车道权限） |
| 6 | 影子期时长 | 判据全绿后仍需 03 号文「连续 3 天零私改/冲突象限」起算；最早 72h 点（09-27 中午）也仅能给出"同判据兜底"结论，不能凭空补出 3 天记录 | 时间，不可压缩 |

72h 兜底点（09-27 中午）的执行者现状（09-25 21:47 更新）：**belt daemon 双轨探针已在岗**（21:30/21:34 两跑实证），每次落地事件+300s 冷却会自行对账 ⇒ 对账动作不再无人跑；**但"三判据评估+出案卷"仍无执行者**（v3 cron 不存在，daemon 只写原始报告不做判绿裁定），故仍按下述命令建薄壳守望。

## 5. 若将来全绿，提请材料要点（预置，不生效）

- **门位**：`docs/01_policies_and_standards/_registry/catalogs/risk_tier_registry.yaml:45`「门禁 flag 出厂默认翻转（宪章 B-007 production 行为变更窗口）」= **high → Owner**。本车道与任何车道不得自翻。
- **"flag"的确切对象（实测纠偏）**：**不是** `config/flags.yaml` 任何条目（该文件 grep `registry|ledger|projection|dual|shadow|enforce` **零命中**）。真对象是两个运行时武装物 + 一个批次：
  1. 建立 `.runtime/projection/registry_projection_state.json` → 同时点亮两处执法：`registry_yaml_parse_gate.py:112` 的 `_PROJECTION_STATE_REL` 私改阻断（staged sha ≠ 状态 sha 即 fail-closed）与 `commit_belt_daemon.py:411-413` 的 PG-wins 自愈；
  2. 切主批次 W4/W5（03 号文 §5 :259-261）：生成器全量重写 YAML（退出合并器白名单 + ROOR `maintenance` 置 `pg_ledger` + 登记 generator_registry）；
  3. 硬前置：W5 必须晚于队列排空（03 号文 :265 时序硬约束，在途旧快照会覆写投影）。
- **回滚路径**（乙号文 §4 Phase 3 表 :225-227 + 丙号文 :260）：Phase 1 双轨期=停记账 hook，代价零；W4 cutover 回滚点=cutover 前一 commit（revert 即回手工态，PG 账本保留不回滚）；切主后=末次快照 `render_yaml` 重生成全册 YAML + ROOR `maintenance` 翻回 manual + 门禁走文件读路径，≤1 发布周期，事件表为全历史超集可重放。
- **已观察时长与样本量（提请页须带的数字）**：截至本卷 32h50m / 151 笔提交 / 22,677 active 行 / 23,104 事件行 / 自动对账样本 0 ⇒ **本卷如实标注：样本不足以支撑"提前"翻转**。
- **授权链现状**：P-3（09 号文 §四「影子期 3 天后执法翻转」，:61）的"批"列=**推荐值，非 Owner 签批**；`docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml`（240 条 ruling_id）对 `W-M1`/`影子期`/`执法翻转`/`registry_ledger` **全部零命中 ⇒ ruling_registry 查无**。LEDGER_wave0.md:63 记录的 Owner"不需要定时"是**台账内口头转述**，同样查无裁定号。任何提请材料不得署 Owner 名，只能署"提请"。

## 6. 给总筹的自动化补链（本车道不调 qoder_cron）

72h 点（09-27 中午）可复用调用串（先仓内、后 cron 薄壳；两条都是**写库动作**，须按 RULE-GUARDIAN/RULE-WORKTREE 在岗执行）：

    cd /d/ZephyrAlpha && python scripts/governance/registry_migration/wave0_phase0_gate.py reconcile --session st-qmine-20260925 \
      && python -c "import json,glob;p=sorted(glob.glob('.runtime/registry_ledger/reconcile_*.json'))[-1];d=json.load(open(p,encoding='utf-8'));print('REPORT',p);print('ALL_PASS',d['all_pass']);[print(r['registry_id'],'yaml',r['yaml_entries'],'pg',r.get('pg_entries'),'backfill',r['backfilled'],'absorb',r.get('absorbed_from_yaml',0),'mismatch',r['content_mismatch'],'pg_only',r['pg_only'],'green',r['zero_unexplained_drift']) for r in d['registries']]"

判绿口径（机械，勿肉眼）： stdout 的 `ALL_PASS True` **且** 七行 `green True` = 判据①②绿。

只读旁证（零写，可随时跑，适合 30 分钟守望器）：

    cd /d/ZephyrAlpha && python -c "import glob,os,json;fs=sorted(glob.glob('.runtime/registry_ledger/dualtrack_*.json'));print('AUTO_RUNS',len(fs));print(fs[-3:]);import subprocess;print(subprocess.run(['powershell','-NoProfile','-Command','Get-CimInstance Win32_Process -Filter \"Name=\'python.exe\'\" | Where-Object { $_.CommandLine -match \'commit_belt_daemon\' } | ForEach-Object { $_.ProcessId }'],capture_output=True,text=True).stdout)"

`AUTO_RUNS 0` 或 daemon PID 年龄 < 报告年龄 ⇒ 断链仍在，直接报红，不要等人盯。

补链建议三条（供 LANE-AUTO 立项，本车道不施工）：
1. 判据评估体落仓内可测代码（含幂等 claim 护栏），cron 只做薄壳调用 ⇒ 消除"cron 在仓外、消失无痕迹"这一类断链（LEDGER §四 N-2 已同判）。
2. 评估器必须自带"执行者存活证明"（读 PID+报告时间戳配对），否则"全绿"可以是"全没跑"的假绿——**本次 24h 点正是这个形态**。
3. 消解 §1.4 的互斥真源（"不需要定时" vs 17 号文定时评估）并把结论登记为裁定号；在裁定落地前，24h/72h 点按 17 号文继续跑（有裁定优先）。

## 7. 本车道待落与边界

- 本卷唯一产出=本文件 + `landing/lane_wm1.yaml`（待落清单）。**未做任何 git 动作、未改任何 flag、未写 PG、未动他人文件**。
- 临时探针件留在 `.runtime/tmp/`（wm1_24h_probe.py / wm1_proc_probe.ps1 / wm1_task_probe.ps1 / wm1_24h_probe_out.json），按 24h TTL 自然清，未入 `scripts/`。
- 案卷瑕疵登记（不代改，归其 owner）：`cmd_successor_20260925/LEDGER.md` frontmatter `doc_type: log` 不在 `doc_type_vocabulary.yaml` 九值词表内（policy/register/index/template/vocabulary/blueprint/audit_report/architecture_view/gate），TTL-METADATA strict-doctype 有拦的风险；本卷取 `audit_report`（ttl_default 即 task_bound，同族先例）。
