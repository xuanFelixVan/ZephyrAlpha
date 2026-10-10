---
ttl: task_bound
title: 终清四号总队 · 99_delivery（战役甲残件清账 + 战役乙门控状态）
session: st-final4-20261010
completes_when: 战役乙四态终扫全覆 + Owner 呈报十项被路由（本件=甲面收账与呈报开面）
---

# 终清四号总队 99_delivery（sid=st-final4-20261010，2026-10-10）

> 一句话：**战役甲五面已全部处置或给出可执行判据；两处"指令卡前提与实测不符"如实上报未代改；
> 战役乙开工门未开（注册表车道仍在飞），本件只给门开后的取数口径与面积实测。**

## 〇、冷启动与在岗证据

| 项 | 实测 |
|---|---|
| RULE-ENV | `python --version`=3.12.8；`setup_dev_env.py --check` installed=True |
| RULE-GUARDIAN | `lock_files.py cleanup`=CLEAN；计划任务 `ZephyrAlpha_ProcessReaper`=Running；reaper `--status` source=live |
| RULE-WORKTREE | `session_worktree_start('st-final4-20261010', allow_workspace_drift=True)` ok=True，棚 `.aidrafts/st-final4-20261010`，开工即 ff 到 dev 尖（零 ahead 才动） |
| 心跳 | keeper pid 53344 + heartbeat_daemon（session_worktree 自带 38640 + keeper 起 53788）；reaper keep 加 `st-final4-20261010` 一行 |
| RULE-CAPABILITY-LOOKUP | `CapabilityLookup().find(..., session_id=...)` 留审计 `.runtime/lookup_audit/st-final4-20261010.jsonl`（首次入队被 CAPABILITY-LOOKUP-REQUIRED 拦——不带 session_id 的调用不记账，已纠正，这是本队第一条自犯） |

---

## 一、战役甲 A：数据车道 backfill 四件

落地 commit：`76fec968f8`（4 件零外来，`git show --stat` 核归属）。处方真源=
`docs/_working/dexp_campaign/00_finding_and_gate.md` §10/§11；P2 已由 dexp 车队落 HEAD（未重做）。

| 件 | 终态 | 交付 | 能红证据 |
|---|---|---|---|
| P3 单实例互斥 | **已落地** | 入口一把 OS 级文件锁，复用 `zephyr.data.scheduler.acquire_single_instance_lock`（未造第二判据）；锁文件与 state 同目录⇒`--state-dir` 指 tmp 即天然隔离；二实例打 `TILIB_LOCK_HELD_BY_OTHER_INSTANCE` 后 rc=0 让路 | 同目录二取必 None + 句柄关后可再取（装饰件判别）；摘掉判空⇒让路用例红（实测） |
| P4 年切窗+超时留态 | **已落地** | 片内按自然年切窗（`--window-timeout` 缺省 1800s）；窗跑完**增量**落 state；开跑先落 `exit="running"`；超时窗写 `exit="timeout"`+`timed_out_window`；续跑仅"当日+同标的指纹+同起止"三条件齐才复用 | 摘掉超时 except（模拟 P4 前行为）⇒TimeoutExpired 直穿、片态不落＝正是被治的死法（实测 1 failed）；跑前即有 running 态；三条件各自作废各有负例 |
| P1 值级跳过 | **判据+熔断+可观测已落地；止血实效未达成（如实报）** | 写前按批现读同键当前可见版，逐列相对差 ≤1e-9 不 INSERT；阈值未改（Owner 批复那个）；跳过计数经 `TI_VALUE_SKIP{...}` 标记行进片态 `value_skip` | 1e-8 绝对差在 1e6 上必跳/在 1e-3 上必写（相对尺双向）；阈值放松到 1e-3 时 1e-6 变更被吞（判别力自证）；改绝对尺⇒红（实测）；熔断不误伤正常路径（阴性对照=正常时逐批都取基） |

### ⚑ P1 的实测证伪（本队最重要的一条上报）

处方 §11 的隐含前提是"比对基读得动、比完能省"。**本班实测证伪**：技术指标宽表 215 个
Nullable(Float64) 列的现读，在本夜跑自身的负载下三形态全灭——

| 探针形态 | 结果 | 用时 |
|---|---|---|
| `argMax(col,ingest_ts)` × 215 + GROUP BY（2 标的×20 日） | CH `Code: 241 memory limit exceeded`（上限 6.71GiB，RSS 已 5.3-5.8GiB） | 81s 死 |
| 宽表 `FINAL` 直读 | 同 241 | 65.6s 死 |
| 剪枝窄窗（`symbol=` + `trade_time` 范围，主键可剪枝） | 同 241，连 2 标的×1 天也死 | 54.4s 死 |

根因不是 SQL 写法：`toDate(trade_time) BETWEEN` 那一版确实不剪枝（PARTITION BY 含
`toYYYYMM(trade_date)`、ORDER BY `(symbol,period,trade_time)`），但**换成可剪枝形态仍死**——
杀死查询的是 OvercommitTracker 在"夜跑自己把 RSS 抬到 5.7GiB"的基线上抢不到内存。
⇒ **P1 运行环境与 P1 要压的那个负载是同一个东西**，这是设计前提问题，不是本班能修的实现问题。

处方已落：连续 3 次取不到比对基即**熔断停用**，`mode=disabled-after-N-base-failures` 进度量行与
片态——宁"少省"绝不"少写"，且账面看得见它没生效（不装哑、不做装饰件）。
熔断的必要性有实测支撑：不熔断则每批白烧一轮 TCP+HTTP 重试≈50s，一片 250 批＝把夜跑
从 21 分钟/片拖成几小时/片。

**给 Owner 的连带结论（不要照原计划推进 P5）**：铁律"P1 先落再 P5"的本意＝别一边 OPTIMIZE
收敛一边被下一趟灌回。现状是 P1 落了三件中的"可观测"层，但**止盈未成立**，
按原节奏排 23:30 的 P5＝先收敛、明晚再被全史重灌吹掉（白占 IO 且不归还空间）。
P5 建议等下面任一条成立后再排：
(a) CH 空闲窗复测证明窄窗读能通（则熔断只是偶发，P1 真生效）；
(b) 采纳"退役指标不再算"这条治本（见 §二·三），使单趟写入量结构性下降；
(c) 给比对基换低内存通道（列分片读/物化视图/换名双写）——**均属改判据或改架构面，本班不自拍**。

### 验收口径（按指令卡新口径，本班实测）

`state 存活 + finished_at=当日 + 单趟 3.5-4M = 达标`：夜跑 02:30 起跑，shard 000
`finished_at=2026-10-10T02:51:10`、exit=0 ✓；当日 state 49 片存活 ✓；**新码今晚不生效**
（夜跑 02:30 起的是主区磁盘旧码，本班落地后已做主区对平，下一轮 02:30 才读得到新码）——
这一条必须写清，否则明早按"今晚没变化"误判落地失败。

### 现场实测账（P4 的病确实在）

`.runtime/.../data/runtime/dwm_shard_state/` 本班 03:3x 实测：state 文件 49 只；
`daily_shard_024 ~ 048` 共 **25 片零 state**（R3 超时静默无态的直接后果，每晚从头再来）；
`shard 008/015` `exit=1`，log_tail 实见 `RuntimeError: [daily] BufferedWriter.add 失败`。

---

## 二、战役甲 B：矩阵 P1 五件

### 1. SQUEEZE / WAD 修复 —— **已落地** `1a9ab332f58`

施工前按指令先核 HEAD：处方所指行号与 dev 逐字吻合 ⇒ 确认未有人做过（非重复施工）。

- SQUEEZE 三处：KC 通道改 `_true_range`（复用 volatility 单口）、KC 中轨 EMA→SMA、
  动量改 `linreg(close − avg(avg(HH20,LL20), SMA20))` 并删尾减 kc_mid；
  BB 倍率**保持 2.0** 不跟 LazyBear 原版那处知名 bug（注释已写明防被"顺手对齐"改回）。
- WAD 两行：`C−min(昨收,今低)` / `C−max(昨收,今高)`；docstring 自称"Tulip 权威"的误读一并修。
- meta.version 两件各 1.0.0→1.1.0，description 改述为可核对的具体口径。

**本件最该记的一条**：既有用例里**确实钉着误读版**——`test_volume.py` 的
`test_wad_hand_computed` 与 `test_wad_independent_recompute` 逐行按 C−L_prev/C−H_prev 算期望。
已按真口径改写并留对照注释（手算样本第 1 行两版差 1、第 3 行巧合同值 ⇒ 只看末行看不出区别）。
留着这种用例＝给下次回归发通行证。

能红证据（四发摘实现，全绿转红后原样还原并断言还原等值）：通道退回 H−L⇒1 failed；
中轨退回 EMA⇒2 failed；动量退回旧写法⇒3 failed；WAD 退回误读⇒1 failed；还原后 11 passed。
指标全目录 1164 passed / 5 skipped。ruff check+format 净（既有三件本就格式干净，未连坐）。

**⚑ 本班自犯并已纠正的假绿**：在车道里裸跑 pytest 时，site-packages 的 .pth + usercustomize
把主区 src 钉在 sys.modules，**测的是主区旧码**——第一次跑 463 passed 就是这么来的，
而实际有两个钉旧口径的用例是红的。验 src 改动必须 `PYTHONNOUSERSITE=1` 且核对
`zephyr.__file__` 落在车道内。这条已写进 commit message，防下一个班重踩。

### 2. 修复后重考 —— **未跑，且当前跑不出有效结果（不是偷懒）**

考试尺读的是技术指标宽表存量值，而那两列存量是**旧口径**算出来的；该表引擎无版本列
（同键最多 7 版并存，未合并期读哪版取决于行序）。⇒ 直接重考＝拿旧数判新公式。
重考前必须先定"这两列存量怎么办"，见本节第 5 条呈报。

### 3. famex v2 entry_role 路由立项 —— **未立项，前提有硬缺陷须先裁**

实测（HEAD）：`entry_role` 在指标册出现 146 处，其中 **143 条全为 `state`**，而册头注释原文
"既有条目为默认值/空值占位，禁止视为已填写内容"；另有 3 条非 state（图式册全 `trigger`、
基准册全 `reference`）。考场侧 `run_fexam.py` 子命令只有 `factor|indicator|strategy`，
indicator 支一律走 `judge_indicator` 的 rank IC，**无 entry_role 路由消费点**
（`ic_exam.py:151` 那处命中是注释）。
⇒ 立项若直接按 entry_role 分派，**四路会全落同一支**（143/146 都是 state），
"路由"变成把现在的错尺换个名字。前置工作＝角色标定本身（143 条逐条定 role），
那是业务资产面（指标条目属性）的大面积改动，**不属本班可自决的施工**，已列呈报。

### 4. 离场族 12 节点冻卡施工 —— **B1 属 Owner 门位，本班只呈不拍**

现状实测：卡已登记在册（`config/strategy_card_lifecycle_map.yaml:3517`
`experiment_id: CARD-EXIT-FAMILY-12NODES`，`card_state: draft`，代登人=st-chiefc-20261009），
`git grep X_tp / X_ladder` 在 config 与 scripts **零命中** ⇒ B1 新配置维确实未开。
门位依据是原文而非本班推测：`mining/m2_exit_sector/00_exit_sector_index.md:85`
"schema 增维（X_stop/X_tp/X_sector 等）**须裁定**"；`exit_family_12nodes_prereg_draft_v1.md:94` B1。
余下 B2-B5（冻卡 prereg 缺、E 道增益 vs t3b FAIL 证据冲突未裁、GPU 预算+T0 重标定、
X-R1-03 资金门位）逐条也都在册。**施工面被 B1 卡死，B1 是门位** ⇒ 本班不动 config。

### 5. 施工中发现的真问题（交数据车道/Owner，本班未代裁）

指标计算入口 `_compute_all_indicators` 取 `TechnicalIndicatorRegistry.list_all()`，
**不按注册表 status 过滤** ⇒ 已按 裁定#489 退役的指标仍在夜跑全量重算并写库。
三重后果：① 这是 dexp 战役"224.5GiB 只涨不缩"的结构性成因之一（退役≠停算）；
② 本修复落地后下一次夜跑会开始用**新口径**写 squeeze/wad 两列，与表内旧口径存量同键并存，
合并前读数取决于行序（`repolluting` 老病的新实例）；
③ 若要重考，这两列的存量必须先定点重算。
可选处置（计算腿按 status 过滤 / 换名列重灌 / 定点重算两列）分别属改判据面与业务资产面，
**本班不自拍**，列为呈报第 3 项。

### 6. 情绪快照器计划任务 —— **未钉任务，对象歧义须先认对象**

实测三态：战役所指"情绪快照器"=`scripts/data/emotion_index_snapshot.py`（**在 HEAD**，
9264B），产物目录实测仅 2 件（10-07/10-08 各一）+ manifest，**10-08 后零新增，且无计划任务**。
在册要求原文（`matrix_campaign/dispatch_blockers.md:22`）是"快照器日批持续跑 + 登 reaper
白名单/计划任务"，`HANDOFF_NEXT_SESSION.md:60` 要"人工连跑 2-3 天稳定后钉 Windows 计划任务"。
⇒ **连跑证据不足**（最近一份产物已是 2 天前），钉任务的前置没满足，本班不钉、也不加 keep。
另两处 Ready 任务（`ZephyrAlpha_NightlySentiment`/`ZephyrAlpha_SectorSnapshot`，LastTaskResult
均=0）跑的是**新闻情绪**与**板块成分快照**，且两个 runner 脚本 `.gitignore:610 scripts/data/*`
命中、**不在 HEAD**——把"那两个在跑"读成"情绪快照器已运维化"会认错对象（已列呈报第 6 项）。

### 7. 路由政策丰富两件 —— **①前提被证伪 ②可做但依赖在飞的投影**

① ADR/RFC 对表：`git grep -iE "ADR.*RFC|adr_rfc"` 在 HEAD 零命中，政策册 v2.1.0 内
`grep -c RFC`=0；反向硬证据 `docs/02_enterprise_architecture/.../architecture_lock.yaml:163`
**明文"项目禁用 ADR 术语"**（理由=ADR 暗示不可推翻）。⇒ 这件要么先撤那条 lock，
要么改成项目自有词族对表；**指令卡前提（存在可"对表"的 ADR/RFC 双轨）与在册裁定冲突**，
按 [[premise-falsified-stop-and-probe]] 停手上报，不自造一套术语册。
② 489 条先例归类：工具在 HEAD（`src/zephyr/library/ruling_precedent.py`，八类普查、
`classify_ruling` 支持册内 `route_class/d_class` 字段优先），但投影册 **317 条 vs 最大号 503**，
且 499/500/501 仅在账本（投影落后，属 裁定#502 战役的 render 面）。
册内 `grep route_class|d_class` 仅 2 处且都在正文串里 ⇒ 逐条归类**零落地**。
本班不重打投影（Owner 已裁"禁出重打投影袋"，且会把 1632 行他人登记混进我 commit＝归属篡改）；
归类动作应在投影跟上账本后由注册表车道专跑。

---

## 三、战役甲 C：三号移交 AI 面五件

| # | 件 | 本班处置 | 依据（实测/原文） |
|---|---|---|---|
| C1 | 治理双向 5（align 硬余额） | **门未开，等触发器**（非"拖"）：处方＝PG 账本侧登 ARCH-367 议题 + 摘 #443/#445 的 `related_arch: INFRA-STORE-003` + render 跟上。实测五处错指**原样零消解**（ARCH-367 议题查无，原文在 related_arch 值里带 # 前缀；#443/#445 仍挂基建 id）。阻塞门与触发器都在 71 号件 §三簇3 原文里写死：触发器=「regsolo 战役收官 + 两册 staged 面清空」，而本班 05:0x 实测 `pending/processing` 仍有 `q-…-st-regsolo-20261010-0027`，且 `ruling_registry.yaml`/`architecture_issue_registry.yaml` 工作区态仍是 `M/MM` ⇒ 现在改＝把他人未落地条目随我袋带出去（归属篡改，宪法 §3.4）。G3-6 现在性检验：存在**现在时点的客观阻碍**，不是缺料缺判据 | 71 号件:42；`ruling_registry.yaml` #435/#436/#437 related_arch 值指向 ARCH-367（议题册查无），#443:3650/#445:3671=`INFRA-STORE-003` |
| C2 | ROOR 两件 | **撤手，转可粘贴呈报件** `.runtime/tmp/st-final4-20261010/roor_pending_entry.yaml`（条目体已写好、机械计数已现算：gates 数组 106＝册内 total_gates 106；登记前 ROOR grep 该路径 0 命中，无双挂号风险；加该条目后 `check_registry_consistency.py` 的 CR-007 不新增 STALE，实测） | 理由：ROOR 是 裁定#502"热册单口写·直写轨退役"战役**正在拆的那条轨**，且该车道在飞；该册头标 `ai_autonomy=human_gated`。手改它=明知故犯撞别人施工面。附带纠正：移交单说的"REG-GATE-CAT-001 描述 25→190 陈旧"口径不准——ROOR:298 的 `entry_count` 早就是 190，"25"在 `known_issues` ISS-003（:1066）散文里，且同一族散文违规还有 REG-GATE-001（"43 个" vs entry_count=91）、REG-INFRA-001（"9 个" vs 17）等，属 §4.3 系统性病，建议一并清（面积交注册表车道，本班不扩大范围） |
| C3 | CWM `rollback_to` 判据缺位 | **Owner 门位，呈报** | `git grep rollback_to dev -- scripts/governance` 零命中 ⇒ 校验器确无该子项。71 号件:65 原话："增判据=改判据程序须与图 YAML+gate+对抗测试同批"；应然语义在 `fig14_construction/00_skeleton.md:168`（回边只许指向编号更小的环节）。**加判据=改判据面**，本班不自加 |
| C4 | frontend R2 warn 口径 | **Owner 门位，呈报** | `check_frontend_map.py:62` `warns.append("R2 …")`，`:13` [ERROR_CONTRACT] "warn 不影响 exit code" ⇒ 现态确为 warn 非 block；升 error 同属改判据程序 |
| C5 | coverage dangling 2 | **待 C1 同窗处理，本班不动 map** | 工具=`generate_map_coverage_attribution.py`（MOD-* 反查 depgraph PG nodes，查无入 dangling_keys）；现态 report-only（`align_all.py:843` 原文："--orphan-threshold 未设，恒 exit 0，判罚归填充班"）。两 id 出处=`config/strategy_production_map.yaml:3079`(MOD-BT-228)、`:4901`(MOD-BT-081)；处置二选一（改键 或 登记 MOD）都落在那本正被 regsolo 动的 map/config 面上，同 C1 逻辑等窗 |

另记三条只读发现（不在移交单内，本班未动）：
1. `align_all.py --no-report` 只返回 exit code，5 条硬余额的**逐条明细只在写盘路径产出**
   （`:1108 output_path.write_text`）⇒ 想"只读复诊"目前没有安全跑法，终清窗禁跑默认形态。
2. `capability_canonical_file_registry.yaml` 在册登记了 `docs/_working/regsolo_campaign/99_delivery.md`
   等三件（token `regsolo-99-delivery-20261009`，created_by st-regsolo-20261010），但该路径
   **HEAD 查无、磁盘 MISSING** ⇒ 册指空。归注册表车道。
3. `data/runtime/process_reaper_keep.txt` 不在 HEAD（磁盘件），却是 `fire_grid.py:60` 的
   G3 硬门依赖（`_REAPER_KEEP`，`:249-253` fail-closed）⇒ 门读之物非受控资产，clean clone 即红。

---

## 四、战役甲 D：F-1b 持出件逐件判

### 先纠一条口径（否则整件会做错）

指令卡说"白名单 5 + 余 35 逐件判"。**台账实际形状不是 40 个文件**：
`.runtime/tmp/st-chiefc-20261009/f1b/stale_holdouts.json` = **40 条 entries**，
其中 8 条用 `paths[]` 展开、1 条是 glob 虚指（`tests/ai/ai/** → tests/ai/** (64 files)`），
展开后 = **70 条路径串**。且 40 条**不是** 99_delivery "2150+175=2325" 之外的加项
（2325 已穷尽 manifest）——同句里还另有"盘面在途 40"，四个互不相干的"40"
（另有 Owner 批文"40 件全批 A"、deadcure2 §十四"40 袋/396 件"）跨引必错。

### 本班实测的存活态（判据=HEAD 跟踪面 / 磁盘 / 队列活区 blob，逐条 join，
反斜杠路径先归一为正斜杠——不归一会假报"查无"）

| 态 | 路径串数 | 含义 |
|---|---|---|
| HEAD | 15 | 字节已在 dev ⇒ 台账可销 |
| DISK（非 HEAD） | 4 | 只在磁盘，含 1 条无证据键 |
| 队列活区 `blobs/<sha>` | 46 | 含白名单 5 件；**源袋多为死袋**（cure-p01-0072 / cure-p05-0042 / deadcure2-0008） |
| join 查无 | 5 | 其中相当比例是反斜杠/GLOB 虚指造成的假查无，**不等于内容真丢** |
| `blobs/dead/` | **0** | 全程未触碰该区（死信二期取证红线） |

### 四终态判定（按类给，不逐文件伪裁）

| 类（disposition 前缀） | 条数 | 终态 | 动作 | 回滚 |
|---|---|---|---|---|
| `stale_align_*`（已对齐并落地：FOLDER-CAPACITY 移册 7 件 / anchor+1 3 件 / import 迁移 / module_skip / mixed） | 15 | **态①** | 台账销账，逐件附 `git log dev -- <path>` 铁证 | 无需（字节在 dev） |
| `stale_holdout_gate_protected`（REAL-KEY-REFERENCE-SCAN 硬拦） | 2 条=**5 文件＝指令卡白名单** | **态④ 留**（死信二期在办，勿碰） | 本班零动作 | — |
| `true_positive_red_held_for_depgraph_lane` / `_src_lane`（db_integration 等） | 2 | **态② 转工单** | 真阳性哨兵，**不得当"过时 stale 断言"批删**（§九与§四口径不一的正是这条）；等 depgraph 30 条重建/src 车道 | 保留即无 |
| `stale_holdout_src_never_existed` / `src_api_drift` / `src_*`（被测面缺失或漂移） | 15 | **态②/态③ 待属主认** | 测试对象在 HEAD 不存在——要么 src 车道补对象（态②），要么判这测试无主可归（态③ 墓碑 30 天）。**判死需被测面属主认，本班不代裁** | 态③走 `E:\_tomb_quarantine` 30 天复活窗 |
| `env_skip_heavy`（串跑 870s+ 需专用长窗） | 3 | **态② 转工单** | 排长窗专跑（非门禁问题，是运行预算问题） | — |
| `red_registered` / 其余 `stale_holdout` | 2 | **态④ 留** | 红已登记在册，等对应车道 | — |

### ⚑ 三条数据完整性缺陷（照单执行会出错，必须先由属主认）

1. **同一文件两条互斥裁定**：`tests/gov/governance/test_chart_wiring_inventory.py` 在台账里
   出现两次，一次判 `stale_align_anchor_plus1`（已落地），一次判
   `stale_holdout_src_never_existed`（被测面从未入库）。照单执行会"既改又持"。
2. **白名单第 5 件路径两册不一致**：stale_holdouts 记 `tests/meta/pipeline/test_run_post_settlement.py`，
   deadcure2 §十三 记 `tests/meta/scripts/…`。§十五 那段"parents[3] 恰=仓库根"的深度论证
   **只对 scripts/ 成立**——落错目录会同时踩锚定与 path_ownership_map。
3. **证据链是单点且不在交付面**：34/40 条 `blob_sha256` 的值就是字符串"见 reconcile.jsonl"，
   6 条连该键都没有；字节真值只在**磁盘 untracked** 的 `reconcile.jsonl`（983,953B）里。
   `.runtime/tmp` 一旦被清理，40 条台账退化为不可复核散文。**本班已把两份的 sha256 与
   体积记在本节下方**，至少保住"内容是否被动过"的可证伪性；
   真正保全需把它们 promote 到交付面（属 F-1b 车道成果，本班不代 promote）。
   `stale_holdouts.json` = `97ad5213503fc400…`（19,946B，mtime 10-09 13:33）
   `reconcile.jsonl` = `48fe04ec3b2b3702…`（983,953B，mtime 10-09 08:10）

### 实盘密钥标记字面量类（指令卡点名；该字面量在本节一律拆写，否则本件会被它正在描述的那道门打死）——本班核实到"待改门"的确切位置

门体 `src/zephyr/ai_layer/redline/negative_list_gates.py:150-199`（priority=149），
白名单是**代码常量** `:98 _REAL_KEY_WHITELIST = ("secret_registry.yaml","SECRETS.md")`（无登记面）；
字面量拆写在 `negative_list.py:91 REAL_KEY_MARKER = "QMT" "_REAL"`。
恢复件必撞的机理在增量口径 `:171`：`if head_text is not None and text.count(MARKER) <= head_text.count(MARKER): continue`
——恢复件 HEAD 无本体 ⇒ `head_text is None` ⇒ **不跳过 ⇒ 新增即拦**。
"改门"＝给 :98 加白名单位，而 `scripts/governance/wave1b/dead_letter_prescriptions.py:582-588`
逐字写着 forbid=**"禁改白名单"** ⇒ 这条路被在册处方封着，只能等死信二期的复活通道（与指令卡一致）。
deadcure2 已实测两次撞同一门（袋 -0006 死于 ghost_session、-0008 死于 REAL-KEY），并自陈选
"丙｜维持持出+上报"，未第三次重投（第三次同门会被复发熔断判为盲重投）。**本班不动这 5 件。**

---

## 五、战役甲 E：F 盘晨报核查 —— **读数未成立，且"06:05"这个读数锚点被实测证伪（早了约 2 小时）**

指令卡说"06:05 三绿终验 + E-1 判读结果若已落册则验收销账；未落则向 Owner 报（它的闹钟已响）"。
本班把三件事分开核清了：

### 1. "闹钟"到底是什么（三路都查过）
- **Windows 计划任务**：NextRunTime 落在 06:00-06:10 的只有 `ZephyrAlpha-DailyBackup`
  （`wscript.exe launch_hidden.vbs backup.ps1 -Mode all -Force`，WD=D:\ZephyrAlpha）。
- **Qoder 定时**：`~/.qoder-cn/tasks` 只有会话后台任务目录（uuid+lease），无 cron 登记件；
  仓内 `data/runtime`、`config` 亦无排班册登记 06:05。
- **仓内排班**：`resource_optimization.yaml` / `resource_profile_registry.yaml` /
  `evolution_schedule_seeds.yaml` / `schedule_gate_policy.yaml` grep "06:05" **零命中**。
- ⇒ **"06:05"不是机器时点**，它是 `disk_reorg_campaign/LEDGER_final.md:779` 预写的**人工合并读卡时点**
  （真定时器=06:00）。同时 `:774` 与 dexp `01_ledger.md:225` 写的是 **06:00**——同一件事三处时点不一致，
  报告口径本身要统一（这是 chief3 移交单之外我自己撞到的一条账面断裂）。

### 2. 06:00 轮次实测两读（本班亲读，非转述）
| 时刻 | 读数 |
|---|---|
| 05:12 基线 | `LastRunTime=10/09 06:00:01`、`Next=10/10 06:00`、`Result=0`；10-10 零报告；`backup_state.last_backup_time=10-09T07:48`、`last_backup_status=failed`；`.runtime/backup.lock` 被 PID 31376（03:56 起，worktree 上下文那份 backup.ps1）持有 |
| 06:02 | `LastRunTime=10/10 **06:00:01**` ✓ 准点起跑；`LastTaskResult=**267009**`（0x41301＝**任务正在运行**，不是失败）；lock 易主 PID 34184 `START:06:00:04` ⇒ **没有 lock-skip**；仍无 10-10 报告 |
| 06:13 | 仍 `267009`（运行中）、lock 仍被 34184 持、10-10 报告零、`backup_state` 未回写、G 侧 `db_dumps/20261010` mtime 仍 05:50 |

### 3. 为什么"现在读不出三绿"不是失败而是时点错
**实跑时长有账**：`logs/backup_report_20261009_052740.json` 文件名时点 05:27、mtime **07:48**
＝同一轮跑了 **≈2h21m**（另两枚 04:06→04:24、00:40→03:09 同量级）。
⇒ 06:00 起跑的轮次**最早有效读数≈08:20-08:30**。在 06:05 去读"有没有报告"，
**必然读到"无"**，而 LEDGER:779 那张两态判读表里没有"仍在跑"这第三态——
照表判就会把"正常长跑"误读成"仍死 ⇒ 三处留痕定位"，即一次**结构性假红**。
这条判读表缺陷归 F 盘车道（本班不代改它的判读表），本班只报机理。

### 4. 本班已做与未做
- 已做：三绿中**唯一当下可判的一绿**——③"F 不存在"实测成立
  （`/f/ch_backup_disk.vhdx` No such file；F 根剩余 1,588,531,142,656B）。
  ②G mtime 曾于 10-10 00:55 前进过，但那是**06:00 轮之前**，按判读表口径不能拿来充 ②（会假绿）。
- 未做（不装做）：①"报告绿"与状态回写 = **待 08:2x 后读**；E-1 两态判读因此**本班不下结论**。
- 已派后台盯终值（约 08:35 落盘证据：报告名/mtime、lock 是否释、LastTaskResult 终值、
  G 侧今日目录、F 复验）。**若本袋先落，§五 的终值随第三袋补**——这不是拖，
  是读数本身要到点才存在（G3-6 现在性检验：现在跑不出这个数）。
- 顺带一条只读发现：`backup_state.json` 里 `last_backup_status=failed` 是 10-09T07:48 的陈值，
  而 `last_lock_skip_time=10-09T21:47`（UTC）、`last_ch_backup_status=skipped` ——
  与 dexp 00 号文 §4 记的"`_backup_fresh()` 把健康的 skipped 天天判红"是同一处仪表病，
  本班未改判据（那是 F 盘/备份班的地盘）。
- 属主收线三证：`st-fwin-exec-20261009` 队列 done 三袋（末袋 20:13 `landed_id=436bbd899cd`）、
  零在途、`git log --all --grep` 三枚尾标全在 dev 且 20:13 后零、棚内 `git status`=0 行；
  **但缺第四证（无该 sid 心跳/pid 件）** ⇒ 按 [[predecessor-session-alive-check]]
  判"**账面已交完、无在途**"，不判"会话已死"。所以这条晨报**没有"其会话已报给 Owner"的替代来源**，
  本班这即是它的落册位。


---

## 六、呈报 Owner / 总统筹（十项，本班一律未自决）

1. **P5 排窗建议暂缓**：P1 止血实效未成立（CH 241 实测三形态全灭），按原节奏 23:30 OPTIMIZE
   会被明晚全史重灌吹掉。三条可选前置见 §一。
2. **fwin/E-1 晨报**：见 §五（06:00 轮读数 + 那条会污染读卡的活体 lock）。
3. **退役指标仍在算**：`_compute_all_indicators` 不按 status 过滤 ⇒ 退役≠停算，
   既是 224.5GiB 只涨不缩的成因，也让本修复的两列出现新旧口径同键并存。三选一处置。
4. **B1 离场族 schema 增维**（原文"须裁定"）＋B2-B5 四项（证据冲突/GPU 预算/资金门位）。
5. **CWM `rollback_to` 加判据** 与 **frontend R2 升 error**：都走改判据程序（图 YAML+gate+对抗测试同批）。
6. **情绪快照器对象歧义**：在 HEAD 的那个（emotion_index_snapshot.py，10-08 后停更、无任务）
   与两个在跑但不在 HEAD 的（被 `.gitignore:610 scripts/data/*` 忽略）是不同东西；
   `fms_deadref_baseline.yaml` 还把后两者记成 dead ref，同时 capreg/resource_profile 把
   `run_nightly_sentiment.py` 当活资产登记——同一物件三册互斥定性。
7. **ADR/RFC 对表与 architecture_lock:163 禁 ADR 术语冲突**：要么撤 lock 要么改词族，请给方向。
8. **ROOR 两件**：条目体与机械计数已备好（`roor_pending_entry.yaml`），等 裁定#502 收官后走正道入账；
   同族散文计数违规面积见 §三 C2。
9. **F-1b 台账三条完整性缺陷**（同文件双裁定 / 白名单路径两册不一 / 证据链单点 untracked）：
   需 F-1b 属主认，认之前不宜批量执行。
10. **治理双向 5 与 coverage dangling 2 的执行窗**：触发器＝regsolo 收官＋两册 staged 面清空；
    门开后本班可即刻执行（处方明确，非悬案）。

---

## 七、战役乙（终清大扫除）——门未开，本班给出的开门后取数口径与面积实测

开门判据（指令卡）＝死信二期/二号/dexp/regsolo/F 盘全部收线或领地已 resolve。

本班 05:3x 实测：

| 面 | 读数 | 判 |
|---|---|---|
| `list_chat_sessions` | 仅 4 会话：本班 running；「死信二期总指令执行」ready；「D盘并发清理」ready(unread)；「飞书和遥测」cold | ready≠收线，只是不在本轮 |
| SessionRegistry `list_active` | 7 条心跳新鲜：chief3 / deadcure2 / dexp / examchief / **final4(本班)** / fullflow2 / **regsolo** | 心跳只证 daemon 活，不证会话死（[[predecessor-session-alive-check]]） |
| 队列 | 本班入袋时 pending/processing 内仍有 `q-…-st-regsolo-20261010-0027`（4 件） | **regsolo 在飞＝门未开的硬证** |
| `.aidrafts` | 18 棚（含本班） | 面积基线，非 106 棚旧数（dexp 那轮已处置 91 棚态①） |

### 本班已做的只读预扫（05:40 实测，**零写零删**；门开后即是机械执行）

`.aidrafts/` 现共 20 目录＝18 会话棚 + 2 非会话棚（`verify_v1`、`regsolo_wt_backup`，
后者名指 regsolo 自带备份，归其属主认）。判据取 dexp 已验真那条（HEAD 是 dev 祖先 + 零脏件 +
`--ignored=matching` 递归展开 + 属主活性），逐棚实测：

| 棚 | HEAD 是 dev 祖先 | ahead | 脏件 | 最近写 | 预判 |
|---|---|---|---|---|---|
| st-chief3-20261009 | ✓ | 0 | 0 | 145m | **态①** |
| st-chiefc-20261009 / -D / -rb1 | ✓ ✓ ✓ | 0 | 0 | 476/1113/680m | **态①×3** |
| st-examchief-20261009 | ✓ | 0 | 0 | 375m | **态①**（但 43m 前有其 dev commit，判态①前须再复核一次活性） |
| st-fullflow2-20261008 | ✓ | 0 | 0 | 1733m | **态①** |
| st-fwin-exec-20261009 | ✓ | 0 | 0 | 463m | **态①**（账面已交完：done 三袋、零在途、20:13 后无 commit 尾标） |
| st-libfront-20261009 | ✓ | 0 | 0 | 251m | **态①** |
| st-mx07-W2 | ✓ | 0 | 0 | 2399m | **态①** |
| st-tclose-fwire-20261004 | ✓ | 0 | 0 | 8760m | **态①** |
| st-deadcure2-20261009 | **✗** | **2** | **126** | 83m | **态②**——有未并入 commit＋大片脏件＝**他役在途现场，门开后第一步也必须绕开它** |
| st-dexp-20261009 | ✓ | 0 | 72 | 55m | **态④**（47m 前有新袋、心跳活） |
| st-regsolo-20261010 | ✓ | 0 | 132 | **0m** | **态④**（预扫当下仍在写＝战役乙门未开的硬证） |
| st-govfix-g2 / g6-20261007 | ✓ ✓ | 0 | 10 / 20 | 3165/3177m | **态②**（脏件 53h 未动，需属主认或走接管台账判"遗留在途"） |
| st-mx07-L3 | ✓ | 0 | 52 | 3279m | **态②**（同上，54h 未动） |
| st-mastertc-mine | **✗** | **1** | 0 | 4359m | **态②→接管正道**：有 1 枚未并入 commit、73h 无写；rescue tag 先行→resolve→archive，禁裸 remove |
| st-final4-20261010 | ✓ | 0 | 71 | 2m | 本班自家棚（收尾按会话收尾序处置，不自清） |

**门开硬判据（不拿心跳当命）**：预扫时 `st-regsolo-20261010` 最近写＝**0 分钟前**、
`st-dexp-20261009` 47 分钟前还在出袋 ⇒ 至少这两路在飞，**战役乙门确证未开**。
判"前任会话已死"须三证齐（该 sid 队列无新袋／棚内无新写／dev 无新 commit 尾标），
本表三列并排就是让下一个班不必重做这套测量。

### 本班一条自犯（写在这儿防后人）
本文件在 05:43 的一次 §七 编辑**未提交即被 `git merge --ff-only dev` 覆盖丢弃**——
那时该路径在车道里仍是 untracked，而 dev 刚由队列袋把它变成 tracked。
教训：**车道里对"即将由队列落地"的新文件做任何编辑，先入袋再 ff**；
untracked 同名件在 ff 时不是"会被拒绝"，而是可能被静默替换。本节即按该教训重贴一次。

开门后四件事的**本班口径**（免后人重research）：

1. 工棚终扫：判据直接复用 dexp 已验真的那条（HEAD 是 dev 祖先 + 零脏件 + `--ignored=matching`
   递归展开后非垃圾增量件=0 + 属主心跳死）。**两条必修的坑**已在册：
   `git status` 默认不列被忽略件而本仓 `.gitignore:265` 是 `/*`（顶层默认全忽略）；
   porcelain 把被忽略**目录**折叠成一行 ⇒ 会漏整目录。判死走 `E:\_tomb_quarantine` 30 天复活窗。
2. worktree 终扫：死会话一律走 `session_takeover_ledger` 正道（rescue tag 先行→resolve→archive），
   **禁裸 `git worktree remove`**（接管台账原文），双 force 旗正是被禁形态。
3. 暂存区终验：本班这两轮已实测到同一个形态——belt 落 dev 后主区磁盘/索引停在落地前，
   新落地件在主区被挂成 **staged-deletion**（`D `），他队一 commit 即真删。
   本班对自家 8 个路径做了四态核账（disk/index/pre-landing/dev 四方比对，证零独有字节）后
   `git restore --staged --worktree --source=dev -- <只我的路径>` 对平，**禁全量 restore**。
   终扫时这一步要按"每个已落袋的 sid 各自核自家路径"做，不能一把梭。
4. `.runtime/tmp` 与根 tmp：逐件 hash==HEAD 才删；`blobs/dead/` 死信二期 Phase 2 前禁碰
   （本班全程未触碰，实测命中 0）。

---

## 八、本班袋账与全项目收线快照（06:15 实测）

| qid | 内容 | 态 | 落地 commit（`git show --stat` 核归属，非回执） |
|---|---|---|---|
| …-0001 | P1/P3/P4 三件（2 脚本+2 测试） | done | `76fec968f8` 恰 4 件零外来 |
| …-0002 | SQUEEZE/WAD 修复（2 src+2 tests） | done | `1a9ab332f58` 恰 4 件零外来 |
| …-0003 | token 先行袋（capreg） | done | 投影差集 +5 行 −0 行（键集合差自证） |
| …-0004 | 终报册首投 | **dead** | 死因 REAL-KEY-REFERENCE-SCAN：本件正文写了那个实盘密钥字面量——**自己撞了自己正在描述的门**；按"内容修复后的死袋禁 requeue"处方，改拆写后另起新袋 |
| …-0005 | 终报册（拆写修正版） | done | 337 行进 dev |
| …-0006 | token 先行袋（F-1b 台账） | done | 投影差集 +5 行 −0 行 |
| …-0007 | F-1b 逐件台账 yaml | done | 645 行进 dev |
| …-0008 | 终报册 §五+§七 增补（本袋） | 本袋 | — |

**全项目收线快照（06:15）**：dev HEAD=`efb5a72…` 一线；`docs/_working` 在册 4208 件、
99_delivery 共 16 本；五役终报在位情况 chiefc ✓ / chief3 ✓ / dexp ✓ / map_build(71 号件) ✓ /
final4 ✓，**deadcure_campaign2 仅 01_phase0_ledger.md 在册（其 99_delivery 未落）**，
F 盘役终报落在 `disk_reorg_campaign/LEDGER_final.md`（不叫 99_delivery，属命名族差异非缺失）。
队列 counts（03:3x→05:5x 全程本班观察）：pending/processing 由 8 → **0**（06:00 后仍零）；
done 668→720+ 自然增；dead 1373（含本班 0004 一枚，已对症改投）。
`.aidrafts` 20 目录（见 §七 预扫表）。claims：本班自投自放，未留 stale claim。
reaper keep：本班仅追加 `st-final4-20261010` 一行，收尾按内容删（删除集=={该行}、总行数恰 −1）。

## 九、复核命令（整段可复制）

```bash
# 甲 A（数据车道三件）
git show dev:scripts/data/tilib_dwm_shard_runner.py | grep -c "def year_windows\|def acquire_instance_lock"   # 期望 2
git show dev:scripts/data/backfill_technical_indicator_dwm.py | grep -c "_VALUE_SKIP_REL_TOL"                  # 期望 7
PYTHONNOUSERSITE=1 python -m pytest tests/data/data/data/test_ti_backfill_value_skip_and_shard_windows.py \
  tests/data/data/data/test_tilib_dwm_shard_state_stamp.py -q                                                  # 期望 34 passed
git show dev:scripts/data/backfill_night.ps1 | grep -c "Remove-Item.*dwm_shard_state"                          # 期望 0（P2 既证）

# 甲 B（两件修复）
git show dev:src/zephyr/factor/technical_indicators/volume.py | grep -c "np.minimum(cp, l)"                    # 期望 1
git show dev:src/zephyr/factor/technical_indicators/momentum.py | grep -c "tr = _true_range"                   # 期望 1
PYTHONNOUSERSITE=1 python -m pytest tests/legacy_zephyr/factor/technical_indicators/ -q                        # 期望 1164 passed

# 甲 D（F-1b 判态，只读）
python - <<'PY'   # 见 §四 表；反斜杠必先归一，否则假报查无
PY

# 归属核验（禁凭 message 自述）
git show --stat 76fec968f8   # 恰 4 件
git show --stat 1a9ab332f58  # 恰 4 件
```

```bash
# 甲 E（F 盘晨报）读数复核——08:2x 后跑，06:05 跑必然假红
powershell -NoProfile -Command "(Get-ScheduledTaskInfo -TaskName 'ZephyrAlpha-DailyBackup') | Select LastRunTime,LastTaskResult"  # 267009=仍在跑(0x41301)
ls -la --time-style=+%m-%d_%H:%M logs/backup_report_20261010_*.json        # 报告绿=出现当日件且 mtime 稳定
cat .runtime/backup.lock                                                    # 锁释=轮次收尾
ls /g/backup/db_dumps/                                                      # ②G mtime 前进须晚于 06:00 才作数
ls /f/ch_backup_disk.vhdx                                                   # ③F 不存在=已成立（06:13 复验）
python -c "import json;d=json.load(open('data/databases/backup_state.json',encoding='utf-8'));print(d['last_backup_time'],d['last_backup_status'])"
```

---

## 乙、战役乙执行令（总统筹 2026-10-10 晨令，Owner 授权夜间自动执行）——四态台账

### 计数总账
| 动作 | 数 | 说明 |
|---|---|---|
| **清理（态① 归档）** | **10 棚** | 全部走 rescue tag → takeover ledger resolve → **非 force** worktree remove；分支全保留 |
| **保留（白名单/在飞）** | 7 棚 | deadcure2(R-a)、dexp、examchief、fullflow2(R-e)、regsolo(R-c)、nightmine(新班·R-f)、final4(R-d 自家) |
| **留棚待认（态② 真增量/前置不复现）** | 2 棚 | govfix-g6（非 force remove 被 git 拒绝：4 改件+12 未跟踪件）、mastertc-mine（ahead=1 枚未并入 commit，已 tag 救住） |
| **记表（判据未覆盖）** | 1 棚 | `verify_v1`（非会话棚、detached HEAD、20 项仓库根快照件） |
| **救回包** | 4 份 | `.runtime/tmp/rescue_<sid>/`（tar+dirty_list）+ **14 枚 rescue tag** |
| **墓碑（态③）** | **0** | 无一棚满足"零触发∧零消费者∧无价值主张∧无重启条件"四元联言 ⇒ 全部未入 `E:\_tomb_quarantine`（墓碑区本次零写） |
| **主区暂存区处置** | **0 条** | 判据第二条全体不成立（见下 T2） |
| **tmp/ 与 .runtime/tmp 删除** | **0 件** | 判据"hash==HEAD 才删"对 36/37 不适用（见下 T3） |
| 磁盘 | D 剩余 39.5G → **60G** | 本班清 10 棚贡献 ≈2.8G，余为并发班 |

### T1 工棚终扫 18→10 棚（三源现测先行，禁单源判死）
每棚三源＝①SessionRegistry 在册 ②heartbeat 末条 status/年龄 ③棚内 fs。执行前逐棚**复测**（不用预扫表当结论）。

| 棚 | 三源 | 判定 | 动作 | 结果与回滚 |
|---|---|---|---|---|
| st-chief3-20261009 | 不在册/exited 160m/无新写 | 态① | tag `1dc37c7a92` + resolve + remove | 目录灭、分支留；`git worktree add .aidrafts/st-chief3-20261009 session/st-chief3-20261009` |
| st-chiefc-20261009 | exited 535m | 态① | tag `c61765bf25` + resolve + remove | 同上格式回滚 |
| st-chiefc-20261009-D | exited 1075m | 态① | tag `0f391c7d1c` + resolve + remove | 同上 |
| st-chiefc-20261009-rb1 | exited 541m | 态① | tag `89efc8202b` + resolve + remove | 同上 |
| st-fwin-exec-20261009 | exited 498m | 态① | tag `769c59bda1` + resolve + remove | 同上（其 99 面早已入 dev，本令与其晨报读数互不阻塞） |
| st-libfront-20261009 | exited 272m | 态① | tag `e942ef510a` + resolve + remove | 同上 |
| st-mx07-W2 | exited 2428m | 态① | tag + resolve + **unlock** + remove | initializing 锁（dexp 移交单在册两棚之一）；走 git 自己的弱一档 `worktree unlock` 后非 force remove，**未用双 force** |
| st-tclose-fwire-20261004 | exited 8684m | 态① | tag `6eb3ab181b` + resolve + **unlock** + remove | 同上（另一枚 initializing 锁棚） |
| st-govfix-g2-20261007 | 不在册/无心跳件 | **改判态①** | tag + resolve + remove | 初判态②（脏件 10）系 `--ignored=matching` 展开的构建物；真增量复测 `tracked_mod=0 ∧ untracked_nonignored=0` ⇒ 空手棚 |
| st-mx07-L3 | exited 3315m | **改判态①** | tag + resolve + remove | 同上（52 件全为忽略面） |
| st-govfix-g6-20261007 | exited 3229m(陈旧 status) | 态②→留 | 救回 tar 1.6MB + 双 tag；resolve 已记 | 5 件与 dev 不同但 **dev_lastcommit 晚于棚内 mtime 且行数等值(±1)**＝落地前草稿非独有增量；然而 `untracked=12` 使非 force remove 被 git 正确拒绝 ⇒ 按纪律"判据未覆盖=停手记表"，留棚 |
| st-mastertc-mine | exited 4395m | 态② | 救回＝`rescue/st-mastertc-mine` 含 1 枚未并入 commit（W1 挖矿骨架 7 件 856 行） | 前置 `anc` 不复现 ⇒ **SKIP 留棚**；内容已由 tag 永久保住，落地与否属 master_tc 战役价值判断 |
| 其余 7 棚 | 在册/alive/白名单 | 态④ | **零动作** | R-a/R-b/R-c/R-d/R-e/R-f 一票否决 |

⚑ **两班必读的两条实锤（本次撞到）**
1. **台账判 regsolo 死，本令 R-c 判它禁碰**：`--scan` 给 `st-regsolo-20261010` 生成 open 条目
   （理由=心跳 exited/11m + 注册表无在册），而 R-c 写明"其工作树 staged 是宪法 §0 升级唯一载体，
   删除=已批宪法丢失"。**白名单优先**，本班只读其棚、**未 resolve 该条目**——留给 R9 落地班自判，
   别让台账的机器判死越权替 Owner 批文做决定。
2. **`--resolve` 对没有 open 条目的 sid 直接 LookupError**：所以"rescue tag→resolve→archive"
   三步的**前置是 `--scan`**（本令未写）。本班按此补齐后再走三步，未因此跳过登记。

### T2 主区暂存区终验 = **零处置**（数字决定，不是判断）
949 条 staged 逐条测 `index ↔ dev`：**等值 0 条、不等 949 条**
⇒ 本令②要求的两条（属主已收官 **AND** staged 与 dev 字节一致）里第二条**全体不成立**，
没有任何一条具备复位资格；另有 465 ` M`/99 `MM`/146 `??`/13 `D ` 等工作区面同属他队现场。
按纪律 1 与红线"禁全量 restore/禁 stash drop/禁裸 reset"=**一条不碰，出表**
（`.runtime/tmp/st-final4-20261010/staged_audit_v3.json`）。
归属分布（按队列袋声明的路径反查）：可按袋归属 446 条，**归属不明 503 条**——
其中绝大多数是自动接链进程给 `docs/_working/**/index.md` 生成的骨架件（在册教训：
非本会话 authored、交回该进程属主、禁代提交）。属主 top：tests-chief 242 / regsolo 37 /
chiefc 28 / dexp 15 / deadcure2 9。

⚑ **本班发现的最高价值隐患（不代修，但请优先处置）**：13 条 `D `（staged 删除）**逐条验 dev 仍在册＝13/13 全是回退弹**，
任何会话一次 `add -A` 式提交即真删这 13 个已入库测试件。其中 **5 条正是 F-1b 白名单件**
（`tests/ai/ai_layer/redline/` 四件 + `tests/meta/scripts/test_run_post_settlement.py`）——
说明死信二期已把它们**复活入 dev**（本班实测与 §四 早前"HEAD 零落地"记录相比是**状态推进**，
§四 那条判据请随之更新）。一条命令即可归零（**须由各属主自查自家路径，禁全量**）：
`git restore --staged --worktree --source=dev -- <仅自家路径>`。

### T3 根区与 tmp = **零删除**（判据不适用，非"没做"）
- 项目根未跟踪临时文件 **0 条**（146 条未跟踪全在子目录）⇒ 宪法 §9.4"根零临时"满足。
- 根 `tmp/`：37 个顶层件 / 100,995KB（**指令卡写"1009MB"与实测差一个量级**，以本表为准）；
  其中 **dev 在册仅 1 件**（`.gitkeep`），36 件不在 HEAD ⇒ "逐件 hash==HEAD 才删"这条判据
  对 36/37 **无法成立**；且 9 件 24h 内有写（`catchup_guard.lock` 06:59 刚写、
  `metaq_audit_reconcile_report.log` 03:50）＝**活跃写者在岗**。⇒ 零删除，出表留认。
- `.runtime/tmp`：本班救援包与案卷都写在这里，**未做任何清理**（并发班仍在用；
  dexp 的 140 件备份目录按令保留）。
- 红线遵守：`.runtime/commit_queue/blobs/`（含 `blobs/dead/`）**一个字节未碰**；
  `data/`、`logs/`、夜跑 state 只读；`E:\_tomb_quarantine` 本次零写（无态③）。

---

## 丙、收尾语（按实际计数，不套模板）

**工棚：清 10、留 10、墓碑 0、救回 4 包＋14 tag；暂存区 949 条零处置（判据第二条全体不成立）；
tmp 零删除（36/37 无 HEAD 对拍基准且活跃写者在岗）。战役甲 5/5 收账，战役乙 T1-T3 执行完，
T4 即本册。**

原令模板句"残件清零，终清完成，全项目收线"本班**不改写也不套用**，因为三项事实现上未到：
① F 盘 06:00 备份轮三绿读数要到 ≈08:20-08:30 才存在（实跑时长 2h21m 有账），§五 已按"互不阻塞"
先行落账，读数随第三袋补；② 四路（deadcure2/dexp/regsolo/nightmine）仍在飞，
暂存区与 `.runtime/tmp` 的终态要等它们收线后再量一次才算终清；③ F-1b 的 22 条
"账面已落实测未达"与本次 13 条回退弹，都要属主认，不是本班能替画的句号。
可断言的部分：**散落的未派残件已无遗留——每一条要么落地、要么给出不可执行的实证理由。**

### §乙补录（执行后复核三则，07:20 实测）
1. **worktree 元数据无债**：`git worktree prune --dry-run --verbose` **零输出** ⇒ 35 条注册项的目录全部在盘，
   本班 10 次移除都已正常注销，**无需也不应 prune**（原判"25 条陈旧注册"是我按 `35 vs 10` 的算术猜，
   被 dry-run 证伪——分布实为 `.worktrees` 17 + 队列池 6 + 主区 1 + `.aidrafts_pool` 1 + `.aidrafts` 11）。
2. **另一处遗留区未动（超出本令范围，非躲）**：`.worktrees`＝**21 目录 / 5.50 GB**（比 `.aidrafts` 那 10 棚还大），
   本令清单只写"18 个工棚＝`.aidrafts`"，且其中多棚 7 天内有写（st-bcure-wt / st-bt-fast-w5 / st-chief7z /
   st-cure-p0…）⇒ 按纪律 1"判据没写到的情况=停下记表，不自行发挥"**零动作**。
   要清它需要一条自己的令（含属主白名单与三源判据），面积已量好可直接引用。
3. **主区自家路径已四态核账后复位**：`99_delivery.md` 与 `02_f1b_holdout_ledger.yaml` 逐件测
   disk/index/pre-landing/dev 四方，证零独有字节后方才复位，复位后 `git status` 该目录 **0 脏件**。

### §五终录（08:34 到点读数，三绿仍未成立——但成因已定谳，不是"死"）
| 判据 | 08:34 实测 | 结论 |
|---|---|---|
| 锁主是否活着 | `Get-Process -Id 34184` ⇒ **powershell 存活，StartTime 06:00:02**，命令行 =`backup.ps1 -Mode all -Force`；父 wscript 39240 亦活 | **在跑，不是死锁**（这一格是判读表两态的分岔关键，本班按进程实证判，不按 lock 文件存在判） |
| 已跑时长 | 06:00:04 起 → 08:34 = **2h34m**；上轮完整报告自记 `duration_seconds=8434.5`（=2h20m34s） | **超历史时长约 14 分钟**＝迟到，未达"判死" |
| ①报告绿 | `logs/backup_report_20261010_*.json` **零件** | 未成立（待跑完） |
| ②G mtime 前进 | `/g/backup/db_dumps/20261010` 目录已建但 08:33 实测 **total 0**（空） | 未成立 |
| ③F 不存在 | `/f/ch_backup_disk.vhdx` No such file | **成立**（复验第三次） |
| 附带面积 | 今日 `backup_skipped_*.json` **15 件，reason 全 = lock_held**（00:20-07:56，含 03:56 那枚 worktree 上下文发起的长跑与 06:00 本轮） | 阀门在起作用不是事故；但代价＝**当日其它班次一律没产出备份报告**，这条要 F 盘班知道 |

⇒ 本班判读结论：**两态判读表（`LEDGER_final.md:779`）今天哪一栏都不该勾**——它缺"仍在跑/迟到"这第三格。
既不"验收销账"（①②未成立），也**不该**触发"仍死⇒三处留痕定位+最小修补归己"（进程活着，判死无据）。
建议 **09:30 前后再读一次**；若届时 PID 34184 仍持锁且仍无报告，则升级为卡死分支处置——
那是 F 盘/备份班的地盘（改判读表加第三格＋查长时段卡在哪一 stage），**本班不代判、不代改其判读表**。

本班对 §五 的账到此为止：**机理已证伪（06:05 锚点早约 2 小时）、成因已定谳（在跑非死）、
三绿已逐格实测（一绿成立两绿待点）、面积已量（15 次 lock-skip）**。剩下一格读数属时间未到，不属未做。
