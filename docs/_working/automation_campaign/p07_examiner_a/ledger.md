---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑦考工A·findings台账
---

# findings 台账（追加式，禁删改他人行）

格式：`## <MM-DD HH:MM> · <一批摘要>` + 要点若干 + 自检结论（两轮）。

## 10-15 07:23 · 班次 01（st-qoder-p07-1015-01）entry 族 class D 八张出分

**本班实际耗时**：起 07:10 冷启动 → 07:23 交账 ≈ 13 分钟（钟点为 `date` 实测非体感；保底口径：8/8 张出分达成，未跑满 4 小时）。

### 一、领卡与通道判定（先实测后动手）
- 分母实测：entry 族 preregistered 卡 113 张；只读普查 `card_binding --mode classify` 出
  `{A:2, A?:7, B:15, C:49, D:0, U:40}`。
- `D=0` 系测量伪影非事实：卡面申报本地序列的 entry 卡实有 8 张（grep derived_series 命中 8），
  且 8 枚 CSV 全部在盘。根因=绑定层 `SERIES_DIR` 仍指迁移前旧路（见堵点①）。
- 通道选定 **run_card API 双注入**，不走 `card_binding --mode run`：绑定层全文零引用
  `target_series`（grep 命中 0），非双臂通道会无条件灌 `index_next_day_return()`
  （card_binding.py:2019 一带）——本批 8 卡的 r 位是卡面冻结的 `mkt_fwd5/mkt_fwd10` 前向面
  （`target_forward_face: precomputed`），灌指数面＝喂错面出假分。
- 装载口径：按卡面 `data_binding.derived_series/target_series` 申报名从迁移后真目录
  `docs/04_research_records/mining/ledgers/nightmine_20261010/series/` 单次 `read_csv` 向量化装载，
  列名规则与 `_load_csv_series` 同（value 优先否则首列），零逐日 `.loc` 循环。
- 断供核查：`known_data_gaps.yaml` grep `hfq` 零命中；`kline_index_399106_breadth_stale` 那条属
  regime_feature_builder 消费面，与本批 agg8 面板等权序列不同源，不构成避让。
- 序列面实测：8 枚序列 nan=0，覆盖 2019-02-11..2026-10-12（mkt_fwd5 至 09-28、mkt_fwd10 至 09-18，
  前向窗口右端自然截断，OOS 段交集仍 ≥60 日）。

### 二、出分明细（8/8，run_id 前缀 p07a-agg8-20261015）
| 卡 | 族/面 | verdict | ic_mean | mono | n | oos_ic | bull/bear | 判据命中 |
|---|---|---|---|---|---|---|---|---|
| 40 lu_count level fwd10 | series | fail | 0.0961 | 0.818 | 1850 | -0.1102 | +0.0024/+0.1633 | oos_sign_flip |
| 41 lu_count_z20 fwd10 | series | **pass** | 0.1037 | 0.733 | 1846 | +0.0997 | +0.1028/+0.0767 | 全过 |
| 42 lu_ratio level fwd10 | series | fail | 0.1023 | 0.842 | 1849 | -0.0979 | +0.0062/+0.1711 | oos_sign_flip |
| 43 lu_ratio_z20 fwd10 | series | **pass** | 0.1022 | 0.745 | 1845 | +0.1016 | +0.0980/+0.0766 | 全过 |
| 44 avg_abs_ret level fwd5 | series | fail | 0.0828 | 0.721 | 1854 | -0.0643 | +0.0114/+0.1670 | oos_sign_flip |
| 45 avg_abs_ret level fwd10 | series | fail | 0.0826 | 0.855 | 1849 | -0.0954 | **-0.0200**/+0.1958 | regime_sign_flip + oos_sign_flip |
| 46 avg_abs_ret_z20 fwd5 | series | fail | 0.1028 | 0.927 | 1850 | -0.0324 | +0.1281/+0.1272 | oos_sign_flip |
| 47 avg_abs_ret_z20 fwd10 | series | fail | 0.1132 | 0.915 | 1845 | -0.1080 | +0.1663/+0.1183 | oos_sign_flip |

- 单卡耗时实测 0.39–1.70 秒（纯本地序列，零 CH），距 15 分钟 kill 线极远。
- 分数册：75 行 → 83 行（追加 8 行）。
- 卡面：8 张 status 全部 preregistered → examined，lineage.run_id/score_row 已回填。
- 试次：`trial_ledger_registry.yaml` 本机新增 8 条 `recorded_by=st-qoder-p07-1015-01`
  （kind=exam_card，n_trials=1，note=verdict=…），分数行 `ledger_warning` 键零命中＝入账无警告。

### 三、堵点与移交（不改判据、不挪门柱，只登记）
- **堵点①（转⑥制卡／①数据席·基建面）**：`card_binding.py:74` 的 `SERIES_DIR` 仍写
  `docs/_working/nightmine_campaign/series`，而 10-15 研究资产搬迁已把序列件移到
  `docs/04_research_records/mining/ledgers/nightmine_20261010/series/`。该缺陷在 HEAD 上（工作树
  对 HEAD 干净），后果=class D 卡永久判 D=0、`_declared_local_faces` 缺省装载静默返回 None。
  本班未动该文件（他席共享码面＋非本席写域），改走注入口绕过。**修法建议**：一行路径指针更正，
  属"改指向"非"改判据"。
- **堵点②（转绑定层属主）**：`card_binding` 全文不消费卡面 `target_series`，故 class D 的
  precomputed 前向目标面在 `--mode run` 通道下会被指数次日面顶替。本班已在分数行留
  `binding_evidence` 自证注入的是卡面申报面；长期解=绑定层补 target_series 腿或显式拒收。
- **堵点③（工具小缺陷，已有绕法）**：`card_binding --cards-dir` 传相对路径时
  `p.relative_to(RUN_ROOT)` 抛 ValueError（RUN_ROOT 是绝对而入参相对）⇒ 必须传绝对路径。
- **移交①（热册归属）**：`trial_ledger_registry.yaml` 工作树面除本班 8 条外，还挂
  `st-e2e-test-p09`（10-14T14:46）与 `st-probe-04mig-20261015`（10-14T19:37）两条他班未落地条目。
  按在册教训（袋=整档快照，随袋提交他人未落地条目＝归属篡改），本班**不随袋提交该册**，
  留属主班或⑩线长席串行落地。若因此出现"分数册已落而试次册未落"的账面差，请 ⑩ 席按本条追认。
- **观察（供⑥/⑨，非裁定）**：过闸的 2 张全在 z20（标准化）面，4 张 level（原值）面 fwd10 无一
  例外死在 `oos_sign_flip`；卡面 `known_weakness` 第三条早自披露 level 面含大票偏置。是否构成
  "level 面 OOS 不稳、z20 面稳"的族级结论须由 ⑨ 成绩官按复制账判，本班不自加门槛。
- **观察②**：`run_card` 翻卡走 `yaml.safe_dump`，卡内行内注释与 `# ──` 分节注释在 examined 卡上
  丢失（对照既有 examined 卡注释命中=0，属既有工具形态，非本班新造）。键值面零丢失（下节自证）。

### 四、自检两轮
- **第一轮（only-add 未动旧行）**：以分数册 index 面为班前基线（班前 sha
  `c7e5b1f8bfb98ae2f454e8180369d4dbdf146bbf19a0ae3f69c54b4be18c006d`，75 行）逐行深比对——
  现册 83 行的前 75 行与基线 `json.dumps(sort_keys)` 全等 ⇒ **前缀零改动通过**；
  卡面侧对 `JUDGMENT_KEYS`（11 键）逐键对 index 基线差分，8/8 张 `判据改动=[]`，
  其他改动集合恰为 `['lineage','status']` ⇒ **反挪门柱自闸通过**。
- **第二轮（分数与门柱一致）**：对 8 行逐一按卡面冻结 `pillars_numeric`
  （mono≥0.6、ic_mean≥0.02、regime 同号、oos 同号）复算判读——8/8 verdict 与读数自洽，
  pass 的两张（41/43）四键全过、fail 的六张 fails 逐条能指到具体柱。
  `ic_ir_min=0.3` 在 series 路无机器面（`_series_metrics` 恒置 None），8 行的
  `unjudged.numeric_keys_no_machine_face` 均如实挂 `ic_ir_min` ⇒
  **引用本批 pass 分数时禁叙述成"门柱全过"，ic_ir 一柱未判**。

### 五、本批不做（带承重证据）
- panel 族 15 张（class B）本班不开考：绑定层自立法即判"本班后置（去重与撮合口径须逐表面核，
  禁批量近似）"，且本班若自建宽表面即成数据面 implementer，超出考工写域。按工序第 4 条转 ⑥/① 席。
- class C 49 张需重放引擎（NAV/权重帧/双臂），属 T3 实现面，非考工席产出。

### 六、收班记录（07:32 实测钟追加，本段属班次 01 同一班）
- 入队：`q-20261015-st-qoder-p07-1015-01-0001`（files=11，07:30:18 建袋）。
- 袋内字节自证：逐件比对 `blob sha == 工作区字节` ⇒ **11/11 全等**；袋内分数册行数实测 **83**；
  袋内件面零外来路径（除分数册/8 卡/本席 ledger+checkpoint 外无他项）。
- 预检两处拦与处方（记档备周审计）：
  ①`SESSION-REQUIRED`（会话未注册）——按在册正解走注册而非加旗：
    `SessionRegistry.open_session(sid)`＝`register(pid=0, logical=True)` 一口＋同进程
    `_spawn_heartbeat_daemon(sid, REPO, 30)`（勿手拼 CLI、勿跨命令），实测 daemon pid=47612、
    6s 后 `get_session` hb_age=12.5s 在册。注：W-29 把 logical 机械降级为 False（本 sid 非 chief 形），
    降级≠失败，活性仍走 90s 心跳判据。
  ②`WORKTREE-REQUIRED`（主区直提且有他班活跃）——用 2026-08-13 裁定的 AI 默认可用旗
    `--allow-non-worktree`。**降级直改主区的原因**：本席出分装置 `run_card` 就地写分数册与卡面
    （分数册路径与卡路径皆绝对锚在主区），指令书亦点名主区路径；先注册后碰 sid 的顺序纪律已守
    （acquire 早于注册，但 takeover_ledger 实测本 sid 零条目，未触发 10-12 那条实 pid 反例）。
- 首投预检被这两项挡在锁外（未烧锁内时间），修正后同一命令链二次入队成功；GW 旗债＝`--allow-non-worktree`
  一项，已在此留痕供⑩席周审计。
- 锁纪律：11 件 claim 由 gateway 续租 ttl=7200s，**袋在飞期间不放锁**（在册死因"袋在飞禁放锁"）。
- 本节自身经"第二袋"落地：后袋对本节所在的 ledger.md 为严格超集（同会话后袋覆盖前袋为在册已知形态，
  超集判定已做），非重复施工。

## 10-15 09:38 · 班次 02（st-qoder-p07-1015-02）entry 族 panel 面开一张＋装载面堵点呈批

**本班钟点（全部 `date` 实测，不写自估终值）**：冷启动 08:10 → 搬账写本段时 10-15 09:38（累计 89 分钟，**这是写账时刻的快照、不是本班总耗时**，
其后入队与汇报另计）。其中两处非产出面耗时按性质分账、不自估分钟：
①例行等待=前班 claim 未到期（08:28 实测剩余 63.3 分、09:0x 实测剩余 24 分 ⇒ 本班实际等待以两钟点差为准）；
②返工=本班自犯三处（证据脚本 `yaml.safe_dump(default=str)`＋`git show :<反斜杠路径>` 崩点后改写重跑；
解锁账谓词 `route=="calibration"` 恒 False 被正面对照证伪后同分母重算；底率对照把信号/收益变量接反后二次实跑）。
**保底口径如实报负**：出分 1 张（<8），4 小时口径未达（白班 09:15 起禁跑算力，本班不硬凑）。
本班不凑数：entry 族真可考面（判据面通＋装载面可按卡面冻结口径忠实物化）实测=1 张，承重证据见第五节。

### 一、领卡面与通道判定（先实测后动手，只读普查脚本=.runtime/tmp/p07/census_1015_02.py＋gate_census_1015_02.py）
- 分母实测（entry_flow 392 件 yaml）：`preregistered 109 / empty 133 / blocked_on_data 69 / blocked_on_impl 20 / examined 61`。
- 绑定层 classify 现算：`A 2 / A? 7 / B 17 / C 51 / U 32 / D 0`（上班烧完 class D 8 张后本族 D 面归零，非 SERIES_DIR 缺陷所致——真目录叠加口径实测 true_classD_face=0，见下）。
- 判据面（执行器本体 `pillars_route`/`_CALIBRATION_JUDGED_KEYS` 实测，本班**考完 L9-A03 之后的活分母 109**）：
  route 取值面本族只有两种——`series` 102 张／`dual_arm` 7 张（**event 路由 0 张**）；机判词表外键 11 张
  （`car_t0_t20_min_bp`/`car_q5_q1_gap_min_bp`/`car_t_stat_min`/`ic_peak_lag_min_days`/`effective_independent_obs_min` 等，执行器无该柱机器面）；
  缺 `oos_window_ref` **0 张** ⇒ **判据面通过 91/109**。
  自洽校验：本班开考前的同一普查=92/109，本班烧掉 1 张通过卡（L9-A03）后=91 ⇒ 两班次读数差恰为 1，非尺漂。
  91 张按（卡形, 绑定级）=（series,U)28、(panel,C)22、(series,C)20、(panel,B)12、(series,A?)4、(panel,U)3、(series,A)2。
  ⇒ **结构性结论：entry 族的卡塞在"装载面"而不是"判据面"**（B/C/U 全是绑定层自立的取数拒因），与 ⑧B 席 10-15 班报的 G1/G2/G3 判据面缺口是两类问题。
- **本席自纠一条（不进结论，只留档）**：解锁账脚本首版把"未知键"谓词写成 `k not in _CALIBRATION_JUDGED_KEYS and route == "calibration"`，
  而 `pillars_route` 本族根本不返回字面量 `calibration`（只返回 `series`/`dual_arm`）⇒ 该谓词恒 False，一度得出"判据面通过 102、外键 0 张"的虚高读数。
  上节数字为**同分母重跑的第二版**（11 张外键、91 通过）。教训与在册"0 命中须正对照"同型：**满命中/零命中都要拿执行器真实取值面当标尺**，
  复跑命令=`python .runtime/tmp/p07/unlock_ledger_1015_02.py`（已改）＋上节同段对账脚本。
- 解锁账（同普查按拒因聚合，`.runtime/tmp/p07/unlock_ledger_1015_02.py` → `...unlock_ledger_1015_02.json`；
  分母=本班考完 L9-A03 后的活分母 109，23 个桶合计恰=109 不重不漏，本班逐桶相加核过）：
  **判据面未过 18**（双臂 7＋机判词表外键 11，两集不交）／
  **`target_face_not_index_next_day` 41**（单一最大堵点：绑定层只认"指数次日"目标面，其余 5 日前向/个股 t+1/NAV 全拒）／
  **panel 装载待装配 12**（B 级，去重与撮合口径须逐表面核）／**`no_data_binding_section` 12**（U 级卡面压根没绑定段）／
  **`multi_table_needs_composite_recipe` 16**／**`signal_column_not_a_single_identifier` 3**／
  **绑定册缺项 4**（`normalization_recipe_undecided` 1、`table_not_in_recipe_book` 3＝research_report/macro_data/hl_funding_history）／
  **class A 名义可绑实为 anyLast 砍面板 2**（本班判假分红线，不开）／`needs_replay_engine` 1。
  注：分母在动——40 分钟内 ⑥ 席有新预注册（B 17→16 因本班烧 1、C 51→52 因新增 1），下一班**禁照抄本数**，须先跑同一普查。
- 本地序列面实测：迁移后真目录 `docs/04_research_records/mining/ledgers/nightmine_20261010/series/` 有 36 枚 csv（16 枚属 _CSV_HINTS 形制、20 枚 `ti_ew_*`）；
  `ti_ew_*` 被 entry 卡全文提及者 20 张，状态**全部 examined**（他班已烧）；preregistered 卡里 `csv_declared_but_not_hint_face=0`、`true_classD_face=0` ⇒ 本地序列面对本席已耗尽。
- 断供避让：`src/zephyr/data/config/known_data_gaps.yaml` 中与本班依赖表相交的在册条目仅 `kline_sector_880_history_structural`
  （覆盖 2024-12-07..2026-05-31，status=completed）与 `sector_constituent_8803_8804_missing`；本班考试的 880 面在 2020-03-17..2025-09-09 窗内不触碰前者缺口段。
- 通道选定：panel 走 `run_card` API（SOP §3⑦ 明令 CLI `--target-csv` 砍单列缺陷未修前禁走），数据面全部走 CH 实读＋向量化宽表，零逐日 `.loc` 循环。

### 二、出分明细（1/1，run_id 前缀 p07a-880rs-20261015）
| 卡 | 形 | verdict | ic_mean | ic_ir | oos_ic | n 日 | bear | bull | 判据命中 |
|---|---|---|---|---|---|---|---|---|---|
| TDM-E-L9-A03/calibration/02_880板块相对强弱持续性 | panel | **fail** | 0.0111 | 0.0374 | +0.0210 | 976 | +0.0119 | 无日（0） | ic_floor 双柱败；regime 同号不可判；mono 无面 |

- 装载凭据（.runtime/tmp/p07/shift_1015_02_evidence.yaml 同件在册）：源=卡面冻结 `c1_market.v_kline_sector_880_named`，
  `period='1d'` 硬过滤，拉数窗 2020-01-01..2025-09-30，出分面窗 2020-04-01..2025-09-09（=卡面 IS 起＋OOS 止）；
  CH 回 577,619 行、(日,板块) 重复键=0（视图无多版本行，实测而非假设）、宽表 1348×722、首根 2020-03-17、拉数 1.4 秒。
- 口径锚点（照抄卡面，零自创）：`signal = close/close.shift(20) − 1 减当日全板块中位`；
  `target 喂"已实现日收益" close/close.shift(1) − 1`——**因为 `_panel_metrics:250` 内部 `ret = target.shift(-1)` 做 PIT 位移**，
  若在此预先做前向收益＝二次位移（错一天）。此点为本席自读执行器源码定死，非引用文档叙述。
- 单卡耗时：CH 拉数实测 1.4 秒＋判分面同命令内完成；距 15 分钟 kill 线极远（精确秒数未留，因证据脚本首跑即崩，见堵点⑥）。

### 三、分数册落地面与"两阶段写账"声明（透明留痕）
- 本班出分时 `exam_scores_v1.yaml` 被前班 claim 持有 ⇒ 本班**不硬闯主册**，把整册副本喂给 run_card 落到工位暂存面
  `.runtime/sessions/st-qoder-p07-1015-02/staging/exam_scores_v1.yaml`（84 行=83 旧＋1 新），锁到期后原样搬入主册。
- 因暂存基线=主册同字节副本，行号天然对齐：卡面 `lineage.score_row=exam_scores_v1.yaml#rows[83]`，主册搬入前恰 83 行 ⇒ 指针无需回填。
- 搬入前置断言（本班实测通过）：主册 sha256 `24ef736d…c55758` 与出分前基线逐字节相同、前 83 行 JSON 深比对与暂存册前 83 行全等。
- **GW 旗债=1 项 `--allow-non-worktree`**（与上班同因留痕备周审计）：出分装置 `run_card` 的分数册路径与卡路径均为绝对锚主区，指令书亦点名主区路径，
  车道内跑同一装置会把分数写进车道副本（在册死因"worktree 队列根/影子面"同族）；本班按"先注册会话→再 claim 卡片→才动盘"次序执行
  （`SessionRegistry.open_session` 回 pid=0 懒注册、logical 被 W-29 机械降级为 False，与上班同形；随后 `lock_files.py list` 实测该卡持有者=本席 sid、已锁定 7s）。

### 四、堵点与移交（不改判据、不挪门柱，只登记）
- **堵点①（转⑩线长席·结构性自锁）**：本席 60 分钟一班，而上一班入队续租的锁 ttl=90 分钟且袋在飞不放；
  实测 08:28 `lock_files.py list` 前班仍持 11 件（含本席 ledger.md/checkpoint.md/分数册），剩余 63.3 分钟；
  `tasklist //FI "PID eq 47612"` 实测前班心跳守护 python.exe 存活 ⇒ 按裁定#252 会话判活口径**不属于"死会话 stale claim"**，
  本班不代释放（§2.7 只授权对死会话精准释放）。叠加队列面实测：pending 102／dead 122，头袋 `st-chfinalw2-20261015-0005` 已等 26,147 秒（7.3 小时），
  上班两袋排位 89/91 ⇒ **同席位"上一班锁 + 深队列"会把 A 席连续多班挡在分数册外**。请 ⑩ 定策（建议口径：交班即释放台账两件、分数册随袋续租改由队列侧持有；属指令面，不涉判据）。
- **堵点②（转绑定层属主＋⑥制卡·假分红线）**：class A 2 张（L2-01-2 板块成交额占比活跃度、L2-01-3 多周期动量主导度）经 `build_signal` 会执行
  `SQL_FACE_DAILY = SELECT toDate(d), anyLast(col) … GROUP BY d`，而两卡 signal_table=`c1_market.kline_sector_880`（日×板块多码表）——
  `anyLast` 取的是任意一块板块的当日值，**不是卡面冻结的"占比/主导度"复合面** ⇒ 照 class A 正门跑＝灌错面出假分。
  本班判"名义可绑、实质错面"，**不开考**，登记不代修。修法属"改指向"（按卡面 signal_derivation 走面板装配），非改判据。
- **堵点③（复证上班）**：`card_binding.py:74 SERIES_DIR` 仍指迁移前旧路 `docs/_working/nightmine_campaign/series`（本班实测该目录 ABSENT），HEAD 上未修；
  对本班影响=零（本族 preregistered 卡申报 _CSV_HINTS 者实测 0 张），但它让 class D 普查恒为 0，属"尺失真"形态，请 ⑩ 派单一行路径更正。
- **堵点④（转①②数据席＋⑨成绩官·已定量）**：880 板块 RS 卡 bull 段（卡面 2020-04-01..2021-06-30）实测**可判日 0 个**：
  信号需 20 日预热 × `fast_rank_ic` 30 只/日地板 ⇒ 宇宙首个 ≥30 只有效板块的信号日=**2021-08-30**（与卡面 self-disclosure
  "牛段可用起点受限已声明"及 data_window_evidence 记 industry_l1(61)/industry_ths(128)=2021-08-02 起相容）。
  按族定量（.runtime/tmp/p07/sector_depth_and_regime_audit_1015_02.json，同窗 2020-01-01..2025-09-30 实跑）：
  `industry_l1 61 码`/`industry_l2 71`/`industry_ths 127` 首根 2021-08-02、首个 ≥30 信号日 **2021-08-30**、可判日各 992；
  `concept_or_style 421 码` 首根 2020-03-17 但首个 ≥30 信号日 **2022-08-29**（可判 751 日）；`region 32 码` 同 2022-08-29（751 日）；
  `mkt_index 10 码` 全窗**从未达 30**（⇒ 该族 panel 卡在现尺下结构性无机判面，与 ⑧B 席 G1 同型）。
  ⇒ 结论口径供 ⑨ 使用：**凡 bull/IS 段落在 2021-08-30 之前的 880 族 panel 卡，`regime_same_sign` 柱一律判"尺量不到"，不得记作信号无效**；
  `known_data_gaps.yaml` 现有 `kline_sector_880_history_structural` 只覆盖 2024-12-07..2026-05-31 且 status=completed，
  **未在册记这条"2021-08 前板块宇宙不足 30 只/日"**＝本班新观察，请 ①② 核 880 宇宙起点真实下限后决定是否开缺数单。
- **堵点⑤（转⑩追认·袋序风险）**：`exam_scores_v1.yaml` 在 git index 状态=**A（从未提交，HEAD 无此件）**，本班搬入后其落地完全依赖在飞袋；
  本班袋=上班两袋的**严格超集**（同 83 行前缀＋1 新行），若队列倒序（我袋先落、上班 83 行袋后落）会按整档快照回退本班新增行。
  在册死因"袋=整档快照"同型，请 ⑩ 按本条追认或让上班袋判弹。
- **堵点⑥（工具形态复证）**：`run_card` 翻卡走 `yaml.safe_dump`，卡内行内注释与分节注释在 examined 卡上丢失（本班卡注释行数=0），
  与上班观察②同款既有形态，非本班新造；键值面零丢失（第四节自检）。本班自犯一条留档：证据脚本首跑用 `yaml.safe_dump(default=str)`（该参数属 json，yaml 不接）
  与 `git show :<Windows 反斜杠路径>` 回空面两处崩点，导致 elapsed 秒数未留——记为"读数完整、耗时缺项"，不补估。
- **堵点⑦（转⑩／全体恒定指令班·锁语义对偶性实测）**：本班 08:38 对卡片 `TDM-E-L9-A03__calibration__02` claim 成就
  （`lock_files.py list` 实测持有者=本席 sid、"已锁定 7s"），08:52 复查**该 claim 已不在册**（全册 25 件锁中查无本席任何条目）。
  归因=本班只做 `SessionRegistry.open_session` 懒注册（pid=0）**未起心跳守护**，按裁定#252 会话判活口径本班会话在约 90 秒后即判死
  ⇒ 他班 `lock_files.py cleanup` 按语义收走本席锁（不是误杀）。
  ⇒ 与堵点①合成一条完整对偶，交给 ⑩：**每班必须自起心跳守护才持得住锁；而"每班自起守护＋入队续租 90 分钟＋队列 7.3 小时积压"＝同席位结构性自锁**。
  本班搬账改走"起守护→批量 claim→写→入队"一条链。**注意这里没有"交班即放锁"这条自由**：
  在册死因写死"袋在飞时禁放锁／禁停心跳，此刻 release-all＋停 keeper＝在飞袋集体死信"（10-10 Owner 认可条目），
  故本班与上班一样只能带锁交班。请 ⑩ 定策的合法方向只有两类：
  ①把"本席台账/游标"从每袋必含件里拆出（每班分件，避免同件跨班争锁＝指令面＋四件套改动）；
  ②把班次间隔与队列排空速度对齐（真解在提交链吞吐，Owner 已定性=全项目开发速度）。本班两案都不自执。
- **堵点⑧（转绑定层属主＋⑩排修复次序·已做 ROI 分层）**：最大单桶 `target_face_not_index_next_day` 全量 **51 张**（其中判据面通过 41 张）按目标面形状分层
  （`.runtime/tmp/p07/target_face_triage_1015_02.py`，谓词先验写死、末层不设通配）：
  `NAV_sharpe（组合净值/Sharpe/回撤）21`／`stock_fwd（个股前向 t+1 close 与 t+1o→t+2c）17`／`unclear 8`／`event_CAR 4`／`sector_fwd 1`，合计=51 不重不漏；
  与绑定层自带 `_target_face_kind` 读数对拍=`engine_replay 21／panel_stock 22／other 4／sector_series 3／probability_hit 1`（两套尺独立同序，属交叉印证非同一集合）。
  ⇒ **单条腿最高 ROI＝绑定层补"个股前向收益面板"目标面（17–22 张）**；`engine_replay` 那 21 张属 T3 重放执行器（⑤席实现面，非绑定层可解）；
  `unclear 8` 张＝卡面目标面措辞机械不可判，须 ⑥ 逐卡改写为可绑形（不改判据，只改指向）。

### 五、本批不做（自带承重证据）
- **不开 class A 2 张**：见堵点②（跑=假分，违"只有考试口径算数"）。
- **不开 L2-01-3**：卡面 `signal_derivation` 给了板块级三周期 rank 与主导度定义，但**面板→series 的收口聚合未声明**（卡面 series 面只对 L2-01-2 写明"占比前 10% 板块等权组合的次日超额与全样本差"）
  ⇒ 开考即由考工替卡面拍聚合口径＝碰判据，转 ⑥ 补声明。
- **不开 L2-07-1/02 回踩四因子合成分**：①"强度分=两路合成分/100（共用 L2-01 重算）"跨卡依赖未物化；②主面对象是 **5 日超额**而 `_panel_metrics` 无 horizon 参数（内部固定 `shift(-1)`）＝执行器面未实现（⑧B 席 G2 同族）；
  ③卡面自带 `conflict_note`（在码 grade_pullback 三维取最弱档 vs 节点文字四维）＝口径未闭合。
- **不开 hfq 全市场对照卡 L3-07-3/03·/04、L9-A01/04·/05**：①卡面 `universe_rule` 写死五件（60/00/30/68 前缀重建＋北交所显式排除＋`stk_limit.st_flag` 判 ST＋上市满 60 交易日＋停牌代理＋退市判定），本班未在算力窗内物化齐这套宇宙＝不裸扩（在册红线"裸扩即造回归"）；
  ②/03 /04 /05 的 `target_source` 文本自相矛盾：既写 `close_t→close_{t+1}/close_{t+2}` 又写"按 T+1 可成交口径取 open_{t+1}→close_{t+2}"，由考工择一＝拍口径，转 ⑥ 更正卡面后开考；
  ③次级理由：本机 08:10 reaper 读数 commit_pct=92.64%／ram_avail 19.28G，5.5M 行面板物化不宜在此余量下强推。
- **不预跑"补口径后即可考"的卡并把读数留在对话里**：同 ⑧B 席纪律，未入册读数一旦被引用＝第二个 03 旧册事故。

### 六、观测面（非分数、不入库，供 ⑥ 词表立法／⑨ 归因）
- 多周期 RankIC（同 RS 面，`fast_rank_ic` 直算，977 日）：t+1 0.01106／t+2 0.01223／t+3 0.01244／t+5 0.01000；
  icir：t+1 0.03714／t+2 0.04277／t+3 0.04483／t+5 0.03672 ⇒ 卡面 prose 柱 `lag_profile`（"t+1..t+3 至少一档达峰值且半衰期≥1"）实测**峰值在 t+3、量级极低**（0.0124）。
- 十分位前后价差（Top10%−Bot10%，日频均值）：t+1 −121.6bp／t+2 −167.7bp／t+3 −204.1bp／t+5 −292.6bp；底率重算（977 日、全样本 5 日均值 +50.4bp）：Top10 +20.9bp、Bot10 +313.6bp。
- 与分数面关系：RankIC 弱正 + 极端段深度反转并存＝族级结构观察；**判读权在 ⑨ 成绩官**，本班不下"信号无效/有效"结论。
- 口径差异如实挂旗：观测面 977 日 vs 分数面 976 日，差一日在边界 2025-09-09（分数路 `target.shift(-1)` 把末日变 NaN 丢掉，观测路直接算前向收益保留）——非同一集合，禁把两组数当同一分母对拍。
- 在册分数册未判柱普查（只读，同一审计件）：现 83 行中 `verdict=pass` 仅 2 行，**2/2 都带未判柱**
  （`TDM-E-L1-S2/calibration/41_agg_lu_count_z20_fwd10`、`/43_agg_lu_ratio_z20_fwd10`，缺面键=`ic_ir_min` series 路无机器面）
  ⇒ 复证上班第二轮红旗：今日 entry 族**没有任何一行是"五柱全判"的 pass**，⑨ 引用 pass 行时禁写"门柱全过"。
  板块族（L2-06/L2-07/L2-08/L9-A03）在册分数行实测 **0 行**（本班 1 张尚未落地）⇒ 该族"regime 柱缺失"此前无对拍面，本班为首例。
- **12 张 class B（panel 待装配）逐表面核（只读，`.runtime/tmp/p07/panel_face_review_1015_02.py`→同名 .json）**：
  按"卡面是否自证"四件筛，读数=去重口径未自证 11／依赖表不在绑定册 9／宇宙口径未写死 8／目标面非 1 日 8／带 arms 双臂面 2；`ready_now=[]`（0 张四格全绿）。
- **正面对照把本班这把尺证伪了一半（自报旗，旧读数保留不涂）**：本班**已成功出分**的 L9-A03/02 用同一把尺量也是两格不合格
  （`dedup_declared=False`、`universe_declared=False`），而它照样能考——因为本班是**用实测代替自证**：
  实跑 `(日,板块)` 重复键=**0 行**、日截面有效码数中位=**661**、目标面 horizon=**1**（`h1=True/multi=False`）。
  ⇒ 正确尺＝**逐表面三件实测**（①重复行数 ②有效码数≥30 ③目标面是否 1 日），"卡面没写"绝不等于"跑不了"，也绝不等于"可以瞎跑"；
  上表四件读数只当**装配前的提问清单**用，不作可考性判据（若当判据就会把 L9-A03 这类可考卡误锁回队列＝另一种假无源）。
- **单点最高 ROI（转绑定层属主，属"改指向"非"改判据"）**：`_REGISTERED_TABLES` 在册只有 5 张表，
  **`c1_market.kline_daily_hfq` 不在配方册** ⇒ 本族 12 张 B 卡里 9 张卡在"依赖表不在绑定册"。
  装载装置其实齐备（`ch_data.T_KLINE_DAILY_HFQ`/`load_close`/`forward_returns` 均已在册有测试），
  缺的只是配方册一条登记（三要素抄 DDL 真源：ReplacingMergeTree(ingest_ts)＋ORDER BY＋where 字面值），与本席上班报的 SERIES_DIR 一行路径更正同量级。
- 本席自纠一次：底率首跑把"信号/收益"两个变量接反（`sig,f=fwd5[cols],sig[cols]` 形参互换）导致读数失真，本节数字为纠正后的第二次实跑；
  另一条自纠=审计脚本首跑 `INNER JOIN ... ON s.sector_code = m.code` 引用了子查询里不存在的列名（CH 回 HTTPError），改 `m.sc` 后才是上列读数。

### 七、自检两轮
- **第一轮（only-add 未动旧行＋反挪门柱自闸）**：搬账脚本的写序=先分数册、后台账、后游标，且分数册搬入断言不过即整班停手不写本段，
  故本段所引"主册 83→84 行、前 83 行 JSON 深比对全等、sha256=`24ef736d…c55758`"均为**写本段之前已实测成立**的事实（终值与全部断言读数落
  `.runtime/tmp/p07/promote_1015_02_report.yaml`，本段不自我计数）；卡面对 `JUDGMENT_KEYS`（11 键）逐键对 base 面差分 ⇒ `判据改动=[]`，
  其他改动集合恰=`['lineage','status']`；本席 ledger.md 由脚本前缀断言（原字节=新字节前缀）通过后才落笔；
  checkpoint 采超集式写法＝本班游标在上＋前班游标逐字留档（脚本断言前班原文在本班字节内才写）。
- **第二轮（分数与门柱一致）**：按卡面冻结 `pillars_numeric` 逐键复算——`ic_mean_min 0.02`：读数 0.0111 败（如实记败）；
  `ic_ir_min 0.3`：读数 0.0374 败（panel 路本键有机判面，与上班 series 路"ic_ir 无面"不同形）；`oos_same_sign`：oos_ic +0.0210 与 IS 同号 ⇒ 过（`oos_ok=true`）；
  `regime_same_sign`：bull 段 0 日 ⇒ 有效段 1<2 **不可判**，由工具 `unjudged.numeric_keys_no_machine_face` 如实挂旗；
  `mono_spearman_min`：panel 路恒 None ⇒ 无面，同样挂旗。⇒ **引用本行只能说"ic_mean/ic_ir 双柱败、OOS 同号"，禁叙述成"五柱全判"**。
- 交付面 self-check 实测输出（正文原样可复跑）：`.runtime/tmp/p07/shift_1015_02_evidence.yaml` 的 `self_check` 节。

### 八、袋内机读自证（10-15 09:41 实测追加，本段与班次 02 同一班，走第二袋）
- 第一袋 `q-20261015-st-qoder-p07-1015-02-0001`（files=4，09:3x 建袋）逐件比对 `blob_sha256 == 工作区字节` ⇒ **4/4 全等**；
  分数册袋内 sha256=`4f986ec7143a…`＝搬账脚本写后回读值，两者同值＝"写的"与"入袋的"是同一份字节（非事后重算）。
- 合并器要面对的基线（实测读数，供 ⑩ 判袋序）：
  ①分数册 `base_blob=None` 且 `HEAD:件` **不存在**（inHEAD=False），但 **index 面存在**且=班前 75 行版
    （index blob `c7e5b1f8bfb9…`＝上班台账所记"班前 sha"同值 ⇒ 三处口径各是一份：HEAD 无／index 75 行／工作区与袋 84 行）；
  ②卡片/本席 ledger/checkpoint 三件 `inHEAD=True`，但 `base_blob` 既≠HEAD blob 也≠index blob（实测三对全不等）
    ⇒ 袋序与合并基线的取舍不由本席判，本班只把读数摊开；
  ③本班第二袋对第一袋逐件做 difflib 超集自证（见下条），第一袋对上班两袋的册面=严格超集（4256→4289 行 minus=0 plus=33）。
- 超集自证（在册要求"后袋⊇前袋才另投"）：`python -c` 逐件 `difflib.ndiff(前袋blob字节, 现工作区字节)`，
  实测 ledger=minus 0 / plus 14（纯追加，本段自身即 plus 面），其余三件 minus 0 / plus 0（同字节）⇒ 后袋不吞前袋任何行。
- 续租实测：`ENQUEUE-RENEW: claim 续租 1/4 件（ttl=7200s）`＝四件里只有本班自持的卡片被续租，
  另三件仍在前班 claim 名下（本班未抢、未放）⇒ 落地执法依据部分系于前班心跳守护，这正是堵点①⑦的具体形态。

---


# ⑦考工A 班次 03（2026-10-15 09:46 起手，10-15 10:31 交班，本班实测耗时 45 分钟）


## 一、领卡面与通道判定（先实测后动手，只读普查=.runtime/tmp/p07/face_census_1015_03.py）

- 分母实测（entry_flow 全树 yaml 按 status 分层）：preregistered 109 / empty 133 / blocked_on_data 69 / blocked_on_impl 23 / examined 62。
- **本班自造尺第一跑判 0 命中＝测量失真不是事实**：谓词写成 `route=='calibration'`，而 `pillars_route()` 实测回值只有 `series 102`／`dual_arm 7` 两种；改正后过三道机器闸（词表内键＋有 oos_window_ref＋非双臂）= **判据面通过 91/109**，缺 oos_window_ref 0 张。
- **本班尺的第二处失真自纠（词表按路由取，禁一把尺量两种路由）**：首跑把 109 张全按 5 键 `_CALIBRATION_JUDGED_KEYS` 度量，得 off-vocab 18 张；改按 `pillars_route()` 分词表复测＝双臂 7 张在 `_UNION_PILLAR_KEYS` 下**全 clean**、series 面真 off-vocab **11** 张 ⇒ 上班"机判词表外键 11"读数被复证，本班的 18 是粗口径产物（已弃用，旧案卷不涂）。
- 烧后活分母复测（同串程序取值）：preregistered 109−6=103、判据面通过 91−6=85 ⇒ 与本班逐张翻卡事实逐值自洽。
- 交叉验证（尺不同源读数对拍）：上班班次 02 独立普查在开考=92、烧 1 张后=91；本班实测 91 ⇒ 三时点读数自洽，非尺漂。
- 本班加第四道闸（本席上岗至今第一条"卡面自证"闸）：**series 卡的"面板→series 收口"必须写在卡面**，否则开考＝由考工替卡面拍聚合口径＝碰判据。机械筛法=在 signal_derivation 全文找显式收口句（`series=`／`series 面`／市场级标量定义），命中面仅 91 张中的 7 张；其余要么写臂（ablation "arm 变量=…"，主臂未指定）、要么指向未落地的在码件。
- 通道：`run_card` 双注入（绑定层实测 `_REGISTERED_TABLES` 仍只 5 张表 ⇒ 本批依赖的 kline_daily_hfq/earnings_forecast/hl_funding_history/news_sentiment_window 中后三者不在配方册，本班走注入绕过，**未改配方册**）。
- 断供避让：`known_data_gaps.yaml` 逐条扫，本批 6 张卡依赖表零命中（tick_data/edb_data/share_change/kline_index_399106 诸条与本批不同源）。
- 底座物化实测：基准 000300 2275 行（2017-06-01..2026-10-14，(日) 重复键 0）；行业族宇宙 189 码（=code_family IN (industry_l1,industry_ths)，非自拟名单）；板块面板 1258×189，重复键 5481，日均在数 188.1 码、最少 188 码；三次 CH 合计 1.2 秒。
- 位移口径照抄执行器本体：`_series_metrics` 对非 precomputed 卡做 `target.shift(-1)` ⇒ 本班喂**已实现日收益** close/close.shift(1)-1，禁在此预做前向（二次位移＝错一天）。本批 6 卡 `target_forward_face` 实测全空。

## 二、出分明细（6/6 出分，run_id 前缀 p07a-sector6-20261015）

| 卡（卡面尾名） | 卡形 | verdict | ic_mean | mono | n | oos_ic | regime 各段 | ic_ir | 判据命中 | 未判柱 |
|---|---|---|---|---|---|---|---|---|---|---|
| 02_四档风险轴前向收益单调 | series | fail | 0.0069 | 0.4000 | 1621 | 0.0682 | -0.0208/-0.0250 | 无面 | mono_spearman 0.400 < 0.6；ic_mean 0.0069 < 0.02 | ic_ir_min |
| 03_market_scope_sentiment_series | series | fail | -0.0234 | -0.2242 | 1621 | 0.0670 | -0.0295/-0.0278 | 无面 | mono_spearman -0.224 < 0.6；ic_mean -0.0234 < 0.02；oos_sign_flip oos=0.0670 is=-0.0234 | ic_ir_min |
| 02b_RRG象限迁移_在册10_26双EMA口径版 | series | fail | -0.0165 | -0.1030 | 996 | 0.0186 | 0.0135/-0.0768 | 无面 | mono_spearman -0.103 < 0.6；ic_mean -0.0165 < 0.02；regime_sign_flip {'bear': 0.013516335137379144, 'rebound': -0.07678648787654536}；oos_sign_flip oos=0.0186 is=-0.0165 | ic_ir_min |
| 02_板块候选池整体边际 | series | fail | -0.0605 | -0.7576 | 976 | -0.0740 | -0.0466/-0.0489 | 无面 | mono_spearman -0.758 < 0.6；ic_mean -0.0605 < 0.02 | ic_ir_min |
| 04_业绩预增催化剂腿 | series | fail | -0.0277 | -0.1000 | 1393 | -0.0031 | -0.0403/-0.0252 | 无面 | mono_spearman -0.100 < 0.6；ic_mean -0.0277 < 0.02 | ic_ir_min |
| 03_derived_signal_shock_panel | series | fail | 0.0166 | 0.3091 | 1621 | 0.0576 | 0.0129/0.0163 | 无面 | mono_spearman 0.309 < 0.6；ic_mean 0.0166 < 0.02 | ic_ir_min |
- 单卡计时（**stdout 打印实测值**，首两次跑）：L1-AGG/02 2.53s、L1-S0-1/03 0.55s、L2-02-1/02b 0.97s、L2/ablation-02 0.60s、L2-09/04 0.56s、L1-S5/03 1.3s；全部远低于 15 分钟 kill 线。自挂旗：机读证据 YAML 走第三跑时六张全走 RESUMED 回读路径，其 elapsed_s=0.0 **不是耗时**（回读不重算），勿据此判"零成本面"。
- 分数册：主册现 84 行 → 搬入后 90 行（本班净增 6 行）；主册搬入前 sha 逐字对回上班袋内记录 4f986ec7143a690f…。
- 卡面翻 examined：6/6；**反挪门柱自闸（对本班逐张实测，非引工具体自报）**＝以 `git show HEAD:<卡>` 为基线对 JUDGMENT_KEYS 逐键差分：6 张逐张判据键改动=[]（JUDGMENT_KEYS 11 键全等）；基线外面改动集合实测并集=['lineage', 'status']（应恰为 {'lineage','status'}）。

## 三、堵点与移交（不改判据、不挪门柱，只登记）

- **堵点①（转⑤执行器席·新缺陷形）**：本班 1 张卡被 `_series_metrics` 的 regime 段解析打断（实跑 traceback 落 .runtime/tmp/p07/shift_1015_03_evidence.yaml.blockers[0]），崩点=`calibration_exam.py:220` → `_in_spans` → `pd.Timestamp(叙述句)`。该卡机判柱 regime_same_sign 本已置 false，崩的不是判据而是装载。本班处置=try/except 隔离并如实登记（否则一卡崩带走整批），**未动执行器、未动卡面 regimes**（越写域）。
- **堵点②（转⑥制卡席·卡面口径未闭合逐张清单）**：
  - `L9-A15/calibration/03_币圈镜像资金费率对BTC`——执行器装载崩（非判据不过）：`calibration_exam.py:220` 对 `window.regimes` 每段调 `_in_spans` 解析日期，本卡 regimes 值是叙述句（`unavailable: 币圈行情实测仅 2025-08-08 起…`）⇒ DateParseError；本班未改执行器未改卡面，采 try/except 隔离整批 ⇒ ⑤执行器席（`_in_spans` 对不可解析段置 NaN/跳过＝不改判据语义，本卡 regime_same_sign 本就 false）
  - `L2-02-1/calibration/02_RRG象限迁移`——卡面口径两处未闭合：锚句『RS=100·exp(4 日累计 ln(板块收盘/基准收盘)) **平移**口径』——平移量无定义；且象限按 (RRI,RS) 四分但四标签↔两轴映射未写死（在码 classify_quadrant 只给 (RS-Ratio,RS-Momentum) 版） ⇒ ⑥制卡席（补平移定义与轴↔标签映射；本班不代拍）
  - `L2-02-2/calibration/02_板块见顶预警三信号`——题名三信号、卡面只给两信号且 RSI 无命中阈值：锚句『RSI14(Wilder) 按 sector_code 计算；放量滞涨=…；series=当日命中 >=1 信号的板块占比』——①无阈值（>几算命中）②第三信号全卡无源 ⇒ 命中集合不可定 ⇒ ⑥制卡席
  - `L2-04-1/calibration/02_轮动五态调节分`——卡面二维轴与其指向的在码真源不同构：卡面轴=(截面方差分位, Top2成交额占比分位)；其点名的 `sector_rotation_state.classify_rotation_state` 实测轴=(top_n_hhi, up_ratio, lead_streak)。『规则与在码一致但重算』无法机械落地 ⇒ 需考工造映射 ⇒ ⑥制卡席；旁证=上班 A? 独立读数 normalization_recipe_undecided 同向（不重裁）
  - `L2-05-1/calibration/02_水温档读数与月级封顶`——月级→上限映射表无源：锚句『最终档=min(日级档, 月级允许上限)』——7 个态各对应什么上限档卡面未给；grep `sector_gate.py` 无 cap 表命中 ⇒ ⑥制卡席
  - `L1-AGG/calibration/03_子信号族到状态轴传导保真度`——primary 与 note 互斥：`target.primary`=next_day_index_return，而 note『传导面卡，终点=状态档序；收益面只作增量旁证，不替代主柱』⇒ 五根机判柱落在哪一面由考工择一 ⇒ ⑥制卡席
  - `L2-09/calibration/03_评级上调聚集`——聚合权重未定义＋表不在配方册：锚句『series=行业加权均值』——按什么加权未写；且 `c3_fundamental.research_report` 不在 `_REGISTERED_TABLES`（实测仅 5 表） ⇒ ⑥制卡席＋绑定层属主
  - `L2-06/L2-07/L2-08 板块 panel 八张`——卡形=panel 而 primary 面=市场级 series：primary 写 next_day_index_return（组合层/series 面），机判柱是截面 RankIC 柱；辅轴多为 5 日超额而 `_panel_metrics` 无 horizon 参数（内部固定 shift(-1）＝执行器面未实现 ⇒ ⑥（卡形或 primary 面须对齐）＋⑤（horizon 参数）；上班 G2 同判不重裁
  - `L3/L9 个股 hfq panel 十五张`——本班算力窗内不强推物化：目标面=stock_fwd_ret_t1o_to_t2c/next_day_stock_return 需个股全面板（`kline_daily_hfq` 实测 10,098,785 行/5,916 票），reaper 本班实测 commit_pct=95.51%／ram_avail≈14G；另部分卡 target_source 自相矛盾（上班已逐张列明并转⑥） ⇒ 待算力窗（commit_pct<80%）再开；口径歧义件先由⑥更正
- **堵点③（在册复证·恒定席锁面）**：本班 pid=0 会话在值守内被外来回收——守护 10:04 起（首次 spawn 静默失败）→ 90s 无心跳判死 → 他席 cleanup 按 R-10 语义**连 11 件 claim 一起收走**（末行 `{"status":"exited","reason":"session not in registry"}` 见 .runtime/sessions/st-qoder-p07-1015-03/heartbeat.jsonl）。正解复跑=同一条命令串内 open_session→_spawn_heartbeat_daemon→acquire→立刻提交；另 `logical=True` 对非 chief 形 sid 被降级 False（fail-open），勿指望免 idle。
- **移交①（热册归属，复证上班）**：`trial_ledger_registry.yaml` 工作树面除本班 6 条 `recorded_by=st-qoder-p07-1015-03` 外仍挂上班 p07-1015-01 等未落地条目 （`git diff` 实测逐条列名）⇒ 本班**不随袋提交该册**（袋=整档快照，随袋=归属篡改），请 ⑩ 线长席串行落地。

## 四、本批不做（自带承重证据）

- 不跑上述九类卡：见堵点②逐张锚点句——**跑＝替卡面拍口径出假分**，违"只有考试口径算数"。
- 不搬个股 hfq 全面板（15 张卡）：本班 reaper 实测 commit_pct 95.51%/cpu 91%/degraded=True，上班同条读数 92.64% 已判"不宜强推"，本班未变好；且该族部分卡 target_source 文本自相矛盾已在册。⇒ 留给算力窗（commit_pct<80%）班，领卡清单见游标。
- 不用 `--mode run` 通道跑任何卡：绑定层零消费 `target_series` 且无条件灌 `index_next_day_return()`（上班堵点②在册），本批 6 卡目标面各异，走该通道＝喂错面。
- 不预跑"补口径后即可考"的卡并把读数留在对话里：同⑧B 席纪律，未入册读数一旦被引用＝第二个 03 旧册事故。

## 五、观测面（非分数、不入库，供⑥词表立法／⑨归因／⑩定策）

- **本班唯一带正对照的装载面**（L1-S5/03 的①②项）：卡面 data_window_evidence 年均涨停锚=卡面年均涨停 65.4/81.9/87.9/77.0/44.1/89.2/77.0（2019..2025）；本班同口径实跑读数={"2019": 64.5, "2020": 80.9, "2021": 87.3, "2022": 76.8, "2023": 43.9, "2024": 89.1, "2025": 78.1} ⇒ 逐年差 |Δ|≤1.1 家/日，导生式复现成功（这条是判"我算的面对不对"的正对照，非分数）。
- **口径歧义敏感性对拍**（⑥创新高家数比含当日窗 vs 排除当日窗，同卡同基准）：ic_mean 0.0166（含，入账读法）vs 0.0188（排除）；mono 0.3091 vs 0.4788；oos 0.0576 vs 0.0587 ⇒ **两种读法 verdict 同为 fail、fails 同键** ⇒ 该卡面歧义不影响本案结论，本班按卡面字面（含当日窗）入账并留此对拍面。
- **宇宙断崖读数（不删点，只挂旗）**：kline_daily_hfq 日均在数 2018 段 231.9 只 vs 2019 段 3647.6 只（=在册"预 2019 仅 ~237 只票"断桩事实）⇒ ④⑥⑦ 的 60 日滚动 z 在 2019-01 边界被放大；本班未截窗（截窗＝改分母），如实披露供⑨判读。
- **未判柱面（引用本班分数禁说"门柱全过"）**：6/6 行 `unjudged.numeric_keys_no_machine_face` 均点名 `ic_ir_min`（series 路恒 None）；panel 路 `mono_spearman` 恒 None 是上班在册形态，本批无 panel 行故未复现。
- 全册 pass 面复测（同一审计件，程序取值）：暂存面 90 行中 verdict=pass **2 行**=['TDM-E-L1-S2/calibration/41_agg_lu_count_z20_fwd10', 'TDM-E-L1-S2/calibration/43_agg_lu_ratio_z20_fwd10']；本班 6 行全 fail ⇒ entry 族今日仍无"五柱全判"的 pass。
- 上一班与本班的"活分母"差：blocked_on_impl 23（上班读数 20）⇒ 本班值守内上游把 3 张卡推进了 blocked_on_impl，非本班动作；派单计数须按两时点记（在册"面值在本班值守内被推进"同型）。

## 六、自检两轮

- **第一轮（only-add 未动旧行＋反挪门柱自闸）**：搬账写序=先分数册、后台账、后游标；分数册差分 difflib **minus=0** 才准搬（plus/行差终值落 .runtime/tmp/p07/promote_1015_03_report.yaml，本段不自我计数），搬入后旧行逐行字节全等＋前 84 行 JSON 深比对全等；卡面 JUDGMENT_KEYS 逐键差分⇒判据改动=[]，其他改动集合恰=['lineage','status']；台账由"原字节=新字节前缀"断言通过后才落笔；游标采超集式（本班在上＋上班原文逐字留档且在班新字节内）。
- **第二轮（分数与门柱一致＝不信工具体，从册面读数＋卡面冻结门柱独立复算）**：本班 6 行逐行重判（mono≥卡面值／ic_mean≥卡面值／oos 与 IS 同号／regime 各段同号且有效段≥2；ic_ir 无面者不计入判过）⇒ **独立复算与册面 verdict 一致 6/6**，逐行败柱与未判柱落 .runtime/tmp/p07/shift_1015_03_recheck.yaml：
  - `02_四档风险轴前向收益单调`：册面 fail／复算 fail／败柱 ['mono', 'ic_mean']／未判柱 ['ic_ir_min']
  - `03_market_scope_sentiment_series`：册面 fail／复算 fail／败柱 ['mono', 'ic_mean', 'oos_sign']／未判柱 ['ic_ir_min']
  - `02b_RRG象限迁移_在册10_26双EMA口径版`：册面 fail／复算 fail／败柱 ['mono', 'ic_mean', 'oos_sign', 'regime_sign']／未判柱 ['ic_ir_min']
  - `02_板块候选池整体边际`：册面 fail／复算 fail／败柱 ['mono', 'ic_mean']／未判柱 ['ic_ir_min']
  - `04_业绩预增催化剂腿`：册面 fail／复算 fail／败柱 ['mono', 'ic_mean']／未判柱 ['ic_ir_min']
  - `03_derived_signal_shock_panel`：册面 fail／复算 fail／败柱 ['mono', 'ic_mean']／未判柱 ['ic_ir_min']
- 引用口径（据上两条）：本班 6 行只能叙述为"部分柱败＋ic_ir 一柱未判"，**禁叙述成"五柱全判"**；本班 pass 行数=0。

### 八、旗债与袋内字节自证（10-15 10:43 实测追加，走本班第二袋）
- **旗债①（--allow-non-worktree 使用一次）**：首投预检判 `[WORKTREE-REQUIRED]`（活跃他会话实测 41 个、预检耗时 53.8s 未落袋），
  依 2026-08-13 裁定"AI 可默认"加旗重投；袋 JSON 的 `meta` 面**不记录旗标**（实测 keys=priority/depends_on/supersedes/registration_gate/preflight_face/interactive/lane），
  故旗债只在本台账留痕，审计侧若按袋面找旗会查无——此形已在册（班次 01 同法留痕）。
- **旗债②（--allow-overlap 使用一次）**：分数册/本席 ledger/checkpoint 三件由上班 sid `st-qoder-p07-1015-01` claim 持有且其 claim TTL 已过期挂册、其袋仍在 pending（在飞禁放锁）⇒
  本班不抢锁不放锁，前置证据=difflib 主册 vs 暂存面 **minus=0**（纯新增才判叠加型，见 promote 报告 overlap_evidence_scores），复证在册"锁对偶"正解。
- **袋内字节自证（第一袋 9 件）**：逐件 `blob_sha256 == 工作区字节` ⇒ **9/9 全等**；
  分数册袋内 sha=009c7bbcf8…＝promote 报告写后回读值 009c7bbcf8…（同值＝"写的"与"入袋的"是同一份字节，非事后重算）。
- 队列读数（提交时刻实测）：{"pending": 134, "processing": 2, "done": 793, "dead": 129}；本席在队项=[{"qid": "q-20261015-st-qoder-p07-1015-03-0001", "session_id": "st-qoder-p07-1015-03", "state": "pending", "created_at": "2026-10-15T10:40:14+08:00", "position_ahead": 132}]。
- 本班净零面自查：未改执行器（calibration_exam.py 装载崩只登记）、未改卡面判据/门柱（HEAD 基线逐键差分=[]）、未改配方册 `_REGISTERED_TABLES`、未新增 .py 资产（四件工位脚本落 .runtime/tmp/p07 随 TTL 退役）。


# ⑦考工A 班次 04（2026-10-15 15:15 起手核查、15:34 注册开工、16:09 交班；本班实测耗时 87 分钟，其中接手前置核查 ≈19 分钟）

## 一、防重入：本班不是"开新班"而是接手同号失压班（三证实测）

- checkpoint 读数：上一**交班**＝班次 03（10:31，last_batch p07a-sector6）；台账无班次 04 段 ⇒ 前任未交班。
- 但 .runtime/tmp/p07 存在 12:56–14:53 的 shift04_* 只读件 ⇒ 先判死活，三证齐：
  ① 队列：find .runtime 命中 q-20261015-st-qoder-p07-1015-01/02/03 诸袋，**1015-04 号袋零命中**（pending/done/.stale 三面皆无）；
  ② 会话：SessionInfo(st-qoder-p07-1015-04) `held_files=[]`，心跳末行自证 `{"status":"exited","reason":"idle timeout","idle_seconds":1813.8}`（本地 13:27）；
  ③ 进程表：Get-CimInstance 全量 python/pythonw 仅命中 p07-1015-03 的 heartbeat_daemon，无任何 shift04 脚本在跑。
- 分数册归属反查：本班开工前 2 分钟主册 mtime=15:13、93 行，末 3 行 card_id=TDM-X-R1-01（run_id=examcard-/mineloop-od1-capexam-）＝⑧B 席在写，**非本席**；TDM-E 行止于班次 03 的 90 行 ⇒ 前任 12:57–14:53 只做到只读普查，零分数行、零翻卡。
- 判定＝失压非未完 ⇒ 可开工；班号按台账"已交班数+1"取 04（与前任同号，本班在其只读件之上续做）。

## 二、领面普查（活分母本班实测；自造尺两处失真当场自纠，旧案卷不涂）

- 分母（entry_flow 全树 400 yaml 按 status 分层，本班实测）：preregistered **103**／empty 133／blocked_on_data 69／blocked_on_impl **27**／examined **68**。
  与上班烧后读数（103）逐值一致 ⇒ 值守内无人烧本族；examined 62→68＝上班 6 张；blocked_on_impl 23→27＝上游在**本班值守外**推进 4 张（非本席动作，派单计数须按两时点记）。
- **上游 ⑥ 未补口径（实测）**：entry_flow 全树 10:31 之后被改的卡＝**1 张**（L9/TDM-E-L9-A01/08，12:49 转入 blocked_on_impl），上班堵点②七张卡的卡面一字未动 ⇒ "等⑥收口"面未回收，本班不得复用上班移交清单当作已就绪。
- 尺自纠①（本班第一跑即假阴）：收口宽筛（`series=`／`series面`／市场级／差值／当日X占比）在 48 张 g_pass series 卡上仅 6 张命中——**而上班烧掉的 6 张本身多为天然市场级标量、根本无需收口句** ⇒ "命中数"≠"可考性"，本班改按"信号是否天然日度标量"逐张人读 46 张（含双臂 7 张路由），尺只分组摘录、不代判可考性。
- 尺自纠②（上班谓词失真复证）：上班那道闸的字面谓词是带空格的 `series 面`，机械上必漏 `series面`（L2-01-2 卡面原文正是"series面取…"）⇒ 上班"91 张中仅 7 张有收口"含**假阴面**；该卡改正后确有收口句，但另有两类缺陷（见堵点③第二条），不因尺误而可考。
- 真分母拆分：有 data_binding 的 series 卡 **39** 张（48 − 9 张无绑定位＝U 面，不在考工写域）；panel 面 g_pass **37** 张；dual_arm **7** 张；三者之外＝判据面外键/缺 oos_window_ref。

## 三、开考结果：0 张入册（唯一跑通者实测判"门槛不可达"，撤分并复原卡面）

- dual_arm 面＝本席上岗至今**唯一从未试投**的面（上班只按路由 G1 排除，理由记"非本席产出面"）。本班按 run_card 真实签名（在码 `signal/signal_b/target/arm_context` 实测）逐张定论：
  - **L2-04/comparison/02_主线合取与单腿双臂**（series 双臂，卡面构造式全闭合）：实跑 1.8s 出 verdict=fail，fails=[`maxdd_improvement 0.00pp < 2.0`, `oos_sign_flip ic_delta nan（配对 IC 面样本不足）`]。
    **本班判该分不入册**（理由=堵点①）：双臂 NAV 逐值全等（maxdd 0.20463246175900662 双侧同值、sharpe −0.0623761321252248 双侧同值、turnover_delta_annual_x 0.0、ic_delta nan），根因＝卡面门槛 `conc>=0.30` 在**卡面自述分母**（"前 2 板块成交额 / 该族当日成交额总和"）下考窗 **997 日一次未成就**：mean 0.0885／p50 0.0854／p90 0.1109／p95 0.1206／p99 0.1379／**max 0.1789**／`days_ge_0.30 = 0` ⇒ 两臂暴露恒 0.5＝常数序列。这是"未触发"不是"不成立"，入册＝把一个无法归因于信号质量的读数钉进 only-add 册（在册铁律：静默降级与"未触发"同形⇒假绿）。
    处置＝零搬账（主册 sha 起 8903ef9e9c731fdcc… 止同值，实测 main_sha_still_before=true）＋ run_card 已翻的 examined/lineage 以 **HEAD blob 原字节**写回复原（该路径 git status 空；disk sha == HEAD blob sha == 896548cbc734d04ddd33bbf8347a0efae33e7b35debefe809005c7e0eb032a98；status 复测=preregistered、lineage.run_id=None）。
  - L2-01/comparison/02、L2-01/comparison/03（series 双臂，构造式闭合但双臂组合面=**池等权次日收益**）：执行器配对面是 `_arm_nav_metrics(exposure, target)`（ret=e×r.shift(-1)）且**两臂共用同一 target**（paired_arm_protocol 原文"仅信号处理异，零行循环差异"）⇒ 卡面要各臂自己的池收益，与共用目标序列不同构 ⇒ ⑤（臂级 target 面）或 ⑥（改暴露面），本班不代拍。
  - L2-07-1/ablation/03、L2-07/ablation/03、L2-07/comparison/03、L2-09/comparison/02（panel 双臂）：双臂支路对 signal/signal_b 一律走 `_series_metrics`（在码实测 936–960 行），**无 panel 路径**；本班以合成权重矩阵 399×5 直调 `_series_metrics` **实测抛** `ValueError: Data must be 1-dimensional, got ndarray of shape (399, 5)` ⇒ 四张卡无机判装载面，转 ⑤（执行器面缺陷，非判据问题，禁改门柱救它）。
  - L9-A15/03（上班堵点①）：`git log --since 2026-10-15 00:00 -- scripts/backtest/fexam/calibration_exam.py` **零提交** ⇒ `_in_spans` 未修，仍不可考（上班读数在效）。
- series 单臂 39 张逐张人读：0 张可考（口径未闭合／断供／算力窗三类，逐张见堵点②③）；panel 37 张：本班无一张具备"轻底座＋卡面闭合＋算力窗成就"三条件。

## 四、堵点与移交（不改判据、不挪门柱，只登记）

- **堵点①（转⑥＋费率参数面属主·新发现"门柱不可达"形）**：L2-04/comparison/02 集中度阈值 0.30 与卡面自述分母量纲不匹配（实测 max 0.1789／997 日 0 次成就）。卡面另自注"在产接线 MOD-SIG-144 注入的是 Top2 主力净流入/全池主力净流入，与本卡不同口径，该错配另在本卡 note 登记"⇒ 分母口径与阈值二者必有一处须由 ⑥ 重定；**本班只报分布事实，不提改档数值**（改档＝代裁）。同卡第二处：卡面"暴露变动日扣单边 10bp" vs 参数面 net_fee.round_trip_cost_bp **实测 25.0**（执行器禁硬编码、读 config 真源；且 config/exam_scale_cost_gate.yaml 此刻在他席工作树脏面）；本班 10bp/25bp 对拍在两臂全等条件下差值恒 0，故该分歧未被本班读数放大，如实登记待属主一致化。
- **堵点②（断供闸逐卡命中，本班对册实跑 82 条 gaps 逐条扫）**：macro_data（source_stale 2026-09-18 起，status **open**）→ L9-A10/02；research_report（empty_column hot_value/rating_change，**open**）→ L2-09/03；kline_sector_intraday（source_discontinued 2026-09-11 起，expected_daily_avg 308000）→ L2-02-2/02、L2-07-1/03；sector_constituent（成分快照仅 2026-07-22 起）→ L2-01/ablation-02、L2-07/comparison/03 涨停剔除腿；edb_data（empty_table 2026-01-01 起，accepted）→ L9-A10 辅腿；alt_shipping_index／alt_typhoon_track → L9-A08/02、L9-A12/02（这两张同时判据键在词表外＝双重不可考）；technical_indicator（duplicate_rows，monitoring）→ L3/L9 多张辅腿。按"避开断供域"条款一律不开考。
- **堵点③（转⑥·卡面口径未闭合逐张精确锚点，本班新增，超上班七张清单）**：
  - L2-01-3/calibration/02 多周期动量主导度：卡面给 主导度=argmax_i(rank_i) 与 连续面=0.2·rank_q3+0.3·rank_q5+0.5·rank_q20，**两面皆为截面 per-sector 读数**，"折成哪一条日度标量"全卡无一句；它有 data_binding（非 U 面）⇒ 属"绑定面未闭合"新类，转 ⑥ 补 series 收口。
  - L2-01-2/calibration/02 板块成交额占比活跃度：收口句在（"series面取'占比前10%板块等权组合的次日超额'与全样本差"，上班带空格谓词漏判），但**该收口在 t 日读数里含 t+1 收益**＝信号自带前向，而执行器 target 面又 shift(-1) 一次 ⇒ 一条序列两处前向；另"与全样本差"未定全样本=基准指数 or 族均值。本班未跑（跑＝出泄漏式假分），需 ⑥ 先钉"前向归谁做"。
  - L2-04-1/02、L2-01-5/ablation-02、L2-05-2/ablation-02、L2-05-2/ablation-02b、L2-05/ablation-02：五张共卡"两路合成分"底座与"按档查表"，**查表值与入账主臂在卡面无一定数** ⇒ ablation 主臂未指定（上班在册形态，本班逐张复证，不重裁）。
  - L2-02-1/ablation-03 与 03b_quadrant_confirm_leg：RRG 重算闭合（03b 逐字承 sector_rrg.py:19-22，short=10/long=26 与 02b 同器），但采信三臂 raw／confirm_k（**k 无数值**）／confirm2+rare_guard 未指定入账臂 ⇒ ⑥。
  - L9-A10/calibration/02：signal="日变化率**或** z-score(60 日)" 二选一未钉，且五指标行转列后取哪一列（或合成）未写 ⇒ ⑥（另命中断供，见堵点②）。
  - L2-02-2/02（复证上班）：series=当日命中 ≥1 信号的板块占比 已在卡面，但 **RSI14 无命中阈值**且"三信号"题名在卡面只落地两信号 ⇒ 命中集合不可定；同卡另命中 kline_sector_intraday 断供。
  - L4-10/comparison-02、L4-13/comparison-02：卡面 derivation **自述**"实测只有成交终态 84 行／无 PendingNew-Accepted-Partial 中间态""两份账缺失" ⇒ 卡面自证 blocked，非本班判据，建议 ⑥ 依卡面自述转 blocked_on_impl/data 以免逐班重考。
- **堵点④（热册与副作用，转 ⑩ 线长席）**：本班实跑使 `trial_ledger_registry.yaml` 工作树面 **+126 行**（其中 recorded_by=st-qoder-p07-1015-04 命中 1 条），该册同时挂他席未落地条目 ⇒ 本班**不随袋提交**（袋=整档快照，随袋=归属篡改）。分数册主册工作树面已被 ⑧B 席推至 **95 行**（本班开工时 93 行）且 git 面 `AM`（index 与 worktree 不同版）＝他会话在途 ⇒ 本班零行未搬、字节未碰。
- **算力窗（转下一班的门槛条件）**：本班 reaper 两次实测——15:16 commit_pct **83.5%**/cpu 91.0/degraded False；15:5x commit_pct **92.73%**/cpu 86.4/**degraded True**/breached=['ALERT-SYS-001','ALERT-SYS-003'] ⇒ 游标 ROI① 的个股 hfq panel 面（15 张）不开。前任 14:53 只读探针读数在册可复用：窗口 2019-01-04..2025-09-09 hfq **7,590,928 行／5,642 票／版本重复单元 0**，列集含 open/close/high/low/volume/amount；本班未重跑该探针（同签名事实不复测）。

## 五、本批不做（自带承重证据）

- 不入册 L2-04/02 的 fail 行：见堵点①（997 日 0 次成就＋两臂常数＝未触发）。
- 不跑 series 39 张与 panel 37 张：逐张见堵点②③＋算力窗实测；跑＝替卡面拍口径出假分，违"只有考试口径算数"。
- 不搬个股 hfq 全面板：两次 commit_pct 读数 83.5%→92.73%（门槛 <80%），且 degraded True；内存红线在册（高 commit_pct 起并发崩在 git add）。
- 不修执行器、不改门柱：`_in_spans`／`_series_metrics` 无 panel 双臂路／双臂共用 target 三处皆属 ⑤ 写域；本班只交实测凭据（含合成矩阵直调 ValueError 一条）。
- 不代拍 0.30 应改成多少：只报分布（p50 0.0854／p99 0.1379／max 0.1789）。
- 不重跑前任 hfq 探针：同签名事实，前班读数已在册且本班无新增判据需求。

## 六、自检两轮

- 第一轮（only-add 未动旧行）：本班**零搬账** ⇒ 分数册主册 sha 起=止（8903ef9e9c731fdcce93243569edba4e8c267f236942227743b6b9b8d064caa5，实测 main_sha_still_before=true）；卡面复原＝disk sha 与 HEAD blob sha **逐字节等**（896548cbc734d04d…）＋ git status 该路径空＋ status 复测 preregistered／lineage.run_id=None；台账与游标走 safe_write_text（CAS＋回读＋审计），台账断言"原字节=新字节前缀"（纯追加），游标采超集式（本班在上、班次 03/02/01 原文逐字在新字节内）。
- 第二轮（分数与门柱一致）：本班无入册行 ⇒ 对该轮做**反向自证**——从证据面重取 conc 分布与两臂 NAV，逐值确认"门柱 maxdd_improvement_min=2.0 之所以违，是因为臂集恒空（days_ge_0.30=0）"而非"臂集非空但改善不足"；据此如实记 **0 出分**，不记 1 张 fail 出分。
- 引用口径（禁句清单）：本班**禁**叙述为"entry 族 series 面已尽/该族无信号"；准确说法＝"本班四闸（判据面／装载面／卡面口径／算力窗）下 0 张可考，原因分属上游三类未闭合＋一类待窗"。dual_arm 面须叙述为"已逐张实测判死（4 张装载面 ValueError／2 张共用 target 不同构／1 张门槛不可达）"，禁再当未探面派单。
- 全册 pass 面实测（本班独立读数，非引上班）：主册现 95 行，verdict=pass **2 行**；本班未新增行；TDM-E 族行数 81（TDM-X 行属⑧B 席在写）。

### 七、本班内更正（另起留旧案，不改上文字节）

- 上文字节内"本班实测耗时 87 分钟"＝**体感钟错值**（在册自犯形态：体感钟快约一倍）。按 date 两点实测重算：起手 15:15:31 → 交班 16:10 ＝ **实测 54 分钟**；其中接手三证核查 ≈19 分钟（15:15–15:34），注册开工 15:34 起算的实际作业 ≈35 分钟。上文那行按"原字节前缀保全"原则不涂改，以本行为准。
- 同因复核：本班"前任 14:53 探针"与"主册 15:13 mtime"两处读数是 `ls`/`find` 的文件 mtime 实测（非体感），不受本条更正影响。
- 保底条款如实呈报：本班 **0 张入册**（未达"每班 ≥8 张出分"），也未跑满 4 小时——原因不是省力，是四闸下 0 张可考（判据面/装载面/卡面口径/算力窗），逐张凭据见 §三 §四。请 ⑩/总筹按 §四堵点①②③派单上游，下一班仍无面时可考虑把本席位改派或并席。

### 八、旗债与袋面自证（本班实测，落袋前写定）

- **旗债①（--allow-non-worktree 使用一次）**：本班首投预检判 `[WORKTREE-REQUIRED]`（活跃他会话实测 ≥6：st-maint9b-20261015／p03-1015-06／p04-1015-06／p05-gpu-1015-01／p06-1015-09 等，锁外预检耗时 11.7s 未落袋），依门自列逃生通道加旗重投；
  袋 JSON 的 `meta` 面不记旗标（班次 03 实测 keys=priority/depends_on/supersedes/registration_gate/preflight_face/interactive/lane），故旗债只在本台账留痕，审计侧按袋面找旗会查无——此形已在册（班次 01/03 同法）。
- **一值守一袋**：本班只投**一袋**（两件：ledger.md＋checkpoint.md），旗债行在入袋**前**写入，避免"袋=快照／盘=后改"双侧皆改死袋（今日 ⑧B 席在册自撞根因）。
- **argparse 前败如实报**：首投用 `-m` 被拒（rc=2 unrecognized arguments，本 CLI 只认 `--message`），提交未发生、无 staged 残留风险；据 AGENTS §2 第 3 条重投带 `--adopt-prior-work`（ledger 工作树面 git 状态 `MM`＝index 与他席自动 add 的旧版不同）。
- **零分数行**：本班 bag 不含分数册/卡面/热册——主册 sha 起=止（8903ef9e9c731fdc…），卡面已复原（896548cbc734d04d…），trial_ledger_registry.yaml +126 行**不随袋**（他席未落地条目同档＝归属篡改风险，在册移交⑩）。

### 九、终态实测补记（16:25:35 date 实取；§七 那行"54 分钟"写于 16:09，彼时本班尚未交班＝在册"落笔即假计数"形态，以本行为准）

- 本班实测耗时＝**70 分钟**（15:15:31 起手核查 → 16:25 收班即清完成）。分段账：接手三证核查 ≈19 分／普查与逐张人读 ≈22 分／实跑与对拍 ≈8 分／交班写册 ≈3 分／提交返工 ≈15 分（其中 argparse 前败一次、预检 WORKTREE-REQUIRED 一次、被后台化误判"提交未发生"而多投一袋——该袋 0002 已由传送带判 `noop@c7890e531c7e` 销账，未成死信）。
- 终态机读凭据（本行落袋后自证，非叙述）：HEAD=c7890e531c（本班 0001 袋，只含 ledger.md＋checkpoint.md 两件）；队列本席 pending=0；claim released=2 denied=0；本席暂存面 staging 已删（被否决的那一行不留给他班误当主册）；分数册主册本班零字节改动（落地 commit 的 --stat 面可复核）。
- 保底终报：本班 **0 张入册**（未达 ≥8），耗时 70 分钟（未跑满 4 小时）；四闸下 0 张可考的逐张凭据在 §三 §四，dual_arm 面试投已判死，勿重复派单。


# ⑦考工A 班次 05（起手 2026-10-15 17:13:12 之前，实测锚：首条命令 date=10-15 16:32:46；写册时点 date 实测 10-15 17:1x）

## 一、防重入（两址同读＋三实测，在册处方）

- 旧址 `docs/_working/automation_campaign/p07_examiner_a/checkpoint.md`：cursor last_run 16:09＝班次 04 已交班；
  其两件袋 c7890e531c（16:18）＋终态补记袋 4f4ac32914（16:36:07）均已落 HEAD；本班开工前（16:37:51 实测钟）
  该班心跳仍 fresh＝在册"带守护交班"形态，非在途施工。
- 新址 `docs/04_research_records/cross_domain/automation_campaign/p07_examiner_a/checkpoint.md`：
  frontmatter 已是 permanent（st-docconsol-20261014 搬迁件），游标正文＝"未开始/last_run —"＝滞后镜像；
  本班取较新旧址（旧址）为活游标，与 ⑥席 1015-09 班同法。
- 取号：台账已交班段＝班次 01/02/03/04 四节（grep "^# ⑦考工A 班次" 实数）⇒ 本班取 **05**。

## 二、冷启动三步与分母（两时点实测，活分母勿照抄）

1. RULE-ENV：python 3.12.8 实测通过。
2. `lock_files.py cleanup`：CLEANED 3 枚死锁（分数册主册＋②席 ledger/checkpoint 两件）；
   SALVAGED 死会话 st-qoder-p04-1015-06 遗物（merge=skipped，释放 claim=0）。
   同串判活旁证：st-qoder-p05-gpu-1015-01 PID 亡而心跳＋在途袋俱在 ⇒ 判活（三证立法）。
3. `process_reaper --status`：source=live・scanned=38・killed=0・reported=3・whitelist_hits=25・
   worktree_changes=5454>50（并行漂移告警在册）。
- 分母（16:41 实测 entry_flow 全树 400 件按 status 分层）：preregistered **103**／empty 133／
  blocked_on_data 69／blocked_on_impl 27／examined 68。16:5x 复测**同值**，但成员已变＝禁当同面：
  本班值守内改名两件——L9-A17/02（⑥席 p06-1015-09，卡面 mtime 16:09:43）blocked_on_data→preregistered；
  L9-A01/02（run_id `st-autoplan-verify-20261015`，mtime 16:28:53，**非本席**）preregistered→examined
  并向分数册追加 1 行（95→**96**，本班 16:5x 实测 sha256 前缀 d77773545f5b4cc7c8c6，git 面 `AM`＝在途）。

## 三、开考结果：0 张入册（三把尺同框互证，含正/负对照）

- **尺一（执行器路由真源 `pillars_route`，非本班自造）**：103 张 prereg 路由面＝series 判官 55／panel 判官 41／
  dual_arm 7（series 3＋panel 4）／event 0；data_binding 段有 91／无 12。
- **尺二（本班轻-重底座尺，首版即自犯并当场自纠）**：本班第一版把"重底座"谓词写成只认全限定名
  `c\d_...\.kline_daily_hfq`，而 52 张 L3/L9 系卡的 target_source 面写的是裸名 `kline_daily_hfq` ⇒
  正则漏前缀，**16 张 panel 被误判"轻底座"**，与前任"panel 面无轻底座"结论相抵。逐张人读证伪本班尺后自纠：
  panel 面真轻底座＝L2-07 族 5 张＋L9-V3 1 张（合计 6），且全部另有闸（见下）。在册"谓词过宽即假扩"复证。
- **尺三（真源普查件 `card_binding.py --mode classify`，零 CH 零写分数册）**：A **2**／A? **7**／B **16**／
  C **52**／D **0**／U **26**，加总=103（互斥分母自证）。两张 class A＝L2-01-2/02 与 L2-01-3/02，
  逐张即前任堵点③第一、二条（series 折标量无一句／t 日读数含 t+1 收益而执行器 target 面再 shift(-1)＝双重前视）；
  D=0＝class D 本地序列面已被班次 01 烧尽（SERIES_DIR 在册 12 件本班复用其一做正对照）。
  另：classify 首跑崩 `ValueError: ... is not in the subpath of D:\\ZephyrAlpha`（件内 `p.relative_to(RUN_ROOT)`
  直吃 `--cards-dir` 原样串，传**绝对路径**才通）＝⑤席写域一枚小缺陷，本班只登记不代修。
- **本班开考面＝0**：dual_arm 7 张不重试（前任逐张判死：4 张 `_series_metrics` 拒权重矩阵／2 张双臂共用 target／
  1 张门槛 997 日 0 次成就，凭据在册）；尺二/尺三正向筛出的 12 张"次日线干净"series 卡逐张人读全部撞在册口径闸
  （查表值与入账主臂无数／"或"字二选一未钉／RSI 命中阈值缺／需重放引擎）；panel 轻底座 6 张中 L9-V3 撞散文 regime
  （`bull_note` 串内无成对日期 ⇒ `_span_pairs` 退回整串单点 ⇒ `pd.Timestamp` 抛，与前任 L9-A15/03 同因属 ⑤），
  其余 5 张＝L2-07/07-1 族撞双臂面或缺路处置律未钉。
- **正/负对照（防"0 是尺瞎"）**：本班零 CH 零写盘，直调执行器 `_series_metrics`＋`judge` 喂已烧的 class D 卡
  L1-S2/40（三件齐申报：`target_forward_face: precomputed`＋`target_horizon_days: 10`＋primary 内 mkt_fwd10）
  ＋本地序列 lu_count×mkt_fwd10（n=1860/1850）⇒ **verdict=fail**，读数 ic_mean **0.096118**／mono_spearman
  **0.818182**／n **1850**／oos_ic **−0.110150**／regime_ic bull 0.002357・bear 0.163279，
  fails=['oos_sign_flip oos=-0.1102 is=0.0961']。负对照＝信号取反 ⇒ fails 变 3 条
  （mono −0.794<0.6／ic_mean −0.0961<0.02／oos 翻正）＝**尺有判别力，能红也能绿**。
  卡面 sha256 前缀起=止（7d522cfc23ea764c）＝真面未动（在册"判官重写卡面"坑靠喂副本规避）。
  ⇒ 本班结论"entry 族现器可考面=0"是**面结论**，非管道失明。

## 四、堵点与移交（不改判据、不挪门柱，只登记；本班三枚新查明的结构性事实）

- **堵点①（纠尺，转⑩与后续各班）＝断供闸谓词口径错配**：前任把"绑定文本出现某表名"直接等同断供。本班按在册
  status 词表实测（83 条：open 27／accepted 19／resolved 13／completed 7／no_source 7／monitoring 5／
  mitigated 4／retired_quarantine 1）＝103 张 prereg 中表名级命中 **61** 张，而其中真落 open|no_source 两态的
  **38** 张 ⇒ **23 张被 accepted/completed/mitigated/monitoring 这类非断供态多挡**。
  本班**不据此开考任何一张**（这 23 张逐张另有尺三的 B/C/U 闸，翻案不产出可考卡），只纠口径：
  断供闸应当＝表绑定 ∩ status∈{open,no_source} ∩ 卡窗 ∩ 该卡所需列；照现行走法派单分母长期虚高约六成。
  实例：L9-A08/02 的 alt_shipping_index 两条 accepted 逐条写的是"国际集装箱租船指数止于 2011-08-23／
  灵便型船运价指数全史 1 行"，与本卡过滤 `index_code='BDI'` 无交集＝该卡真闸在下条（多日面无申报位），不在断供。
- **堵点②（翻案实测，转①席）**＝断供册 `c3_fundamental.research_report` 行已过期：册内 id=research_report_hot_value_rating_change_empty・
  gap_type=empty_column・status=**open**・last_updated=2026-09-21・文字仍写"rating_change 列仍在且维持空列"。
  本班 CH 直读实测＝表存在（system.tables 命中）、全表 **294,066** 行、`countIf(rating_change!='')`=**267,835**（91.08%）、
  取值面 维持 184,383／上调 39,480／下调 39,056／首次 4,916、非空面 publish_date 跨 2017-01-02..2026-10-14；
  负对照＝`countIf(rating_change='')`=**26,231**（空串谓词能命中真空值，非尺瞎）；
  反向自证＝本班首版探针把 `hot_value` 写进 SQL 直接 HTTP 404＝该列确实不存在，与册 verification_20260921 逐字吻合。
  ⇒ ⑥席 16:09 据②席回填证据把 A17/02 翻 preregistered 一事本班独立复算支持；**但册为真源且仍 open**，
  本班按工序"避开断供域"照旧不开考挂它的三张（L9-A17/02・L9-A17/03・L2-09/03），请①席当班复测后改该行。
- **堵点③（新面 6 张，转⑥；前任移交清单未覆盖）**＝**多日前向标的缺 `_forward_face` 三件齐申报位**：
  执行器只认 `target_forward_face: precomputed`＋`target_horizon_days`（2..252 整数）＋`target.primary` 内
  `mkt_fwd{h}` 同值记号，缺一即拒且禁半申报退化；实测全库申报者仅 **8** 张＝班次 01 烧的 class D 八张（现全 examined）。
  preregistered 面 target.primary 逐字命名多日标的而三件不齐＝**6** 张（尺＝`.runtime/tmp/p07/shift05_findings.yaml` M1 节）：
  L9-A08/02（next_20day_sector_return）・L9-A11/02（next_5day）・L9-A12/02（car_0_to_5_elec_sector）・
  L9-A13/02（car_0_to_20）・L9-A17/02（car_0_to_5_stock）・L9-A17/03（next_20day_return）。
  这 6 张在尺三里被归 C（target_face_not_index_next_day），故前任"等⑥补 series 收口句"那条工单读不到它们＝新面。
  两条修法均不属本席写域：⑥按在册申报形态补三件齐（须同时把 target.primary 记号改成 mkt_fwd{h}＝动到冻结目标面
  命名＝呈批面，本席不代拍）；或⑤给 sector/panel 面接 h 日前向聚合。
- 堵点④（承接在册未闭）＝散文 regime 串使装载崩：本班实测 entry prereg 内该形态 **5** 张
  （L9-A06/02・L9-A11/02・L9-A15/02・L9-A15/03・L9-V3/ablation/02，键名 bull_note/unavailable），属⑤。
- 堵点⑤（算力窗，门槛条件）＝本班三次 date 配对实测 commit_pct：**89.13**（16:33:23，cpu 61.3，degraded False）／
  **94.98**（16:34:52）／**89.52**（16:59:06，cpu 71.8，degraded False）⇒ 门槛 <80% 全程未成就，
  个股 hfq panel 面 15 张不开（前任探针读数 7,590,928 行／5,642 票／重复单元 0 在册，本班未重跑同签名事实）。
- 堵点⑥（副作用面复测，转⑩/⑨）＝`docs/01_policies_and_standards/_registry/catalogs/trial_ledger_registry.yaml`
  工作树面仍 ` M`（末次提交 eb02e513f6 10-13 23:35；本班实测含班次 04 的 1 条＋班次 03 的 6 条命中）
  ＝前任"不随袋"的副作用面至今未落地也未复位；本班**零 run_card 实跑**，未新增行。

## 五、本批不做（自带承重证据）

- 不重投 dual_arm 7 张（前任三类凭据在册）；不开 23 张"非断供态"卡（逐张另有 classify B/C/U 闸，本班已量）。
- 不改断供册（①席写域）、不补卡面申报位（⑥席写域且动冻结目标面命名须呈批）、不修 classify 相对路径崩与
  `_in_spans` 散文崩（⑤席写域）＝只交实测凭据与精确锚点。
- 不搬个股 hfq panel 面（三次 commit_pct 89.13/94.98/89.52 均≥80%，且高 commit_pct 起长批在册崩面为 git add 0xC0000142）。
- 不做 run_card 实跑（实跑＝翻牌＋写分数册＋记试次台账三件同起），正对照改走判官直调，零写盘。
- 不代拍 6 张多日面该走"改记号"还是"执行器扩面"＝两路代价不同（前者动冻结命名，后者动 ⑤ 码面），摊给⑥/⑩。

## 六、自检两轮

- 第一轮（only-add 未动旧行）：分数册主册本班**零字节**（起 16:5x 与止 17:1x 同 sha256 前缀 d77773545f5b4cc7c8c6，
  96 行／pass 2 行／TDM-E 面 82 行，末行 card_id=TDM-E-L9-A01/calibration/02・run_id=st-autoplan-verify-20261015
  ＝他席本班值守内追加，非本席）；卡面零翻牌（正对照喂的卡面 sha 起=止 7d522cfc23ea764c）；
  台账走 safe_write_text 且断言 `new.startswith(old)`（删除集=空）；游标超集式＝前言＋班次 04 整块＋班次 03/02/01
  留档段三块逐字在新字节内（脚本内断言，非叙述）。
- 第二轮（分数与门柱一致）：本班无入册行 ⇒ 做反向自证——正对照读数逐条对门柱：卡面冻 `ic_mean_min=0.02`・
  `mono_spearman_min=0.6`・`oos_same_sign=true`，读数 ic 0.096118 与 mono 0.818182 皆过线而 oos −0.110150 对
  is +0.096118 反号 ⇒ 唯一触发柱即 `oos_sign_flip`，与在册行号 rows[75] 同一形态＝尺确实受门柱约束；
  负对照取反后柱集换人（mono/ic 转违、oos 转符）＝判据随数值动而非随卡片动。
  断供翻案读数亦同法自证：空串谓词负对照命中 26,231・`hot_value` 列 404 反证。

## 七、保底条款如实呈报

- 本班 **0 张入册**（未达每班 ≥8 张），未跑满 4 小时（起手 16:32:46 至写册 17:1x＝实测约 45 分钟，按 date 两点对账）。
- 与班次 04 的差别（禁再复制"四闸下 0 张"当交付）：本班产出的是**三把尺同框互证**（含执行器路由真源与
  真源 classify 普查件首次同场）＋**两把断供尺的量化差 23 张**＋**1 枚 CH 实测翻案（research_report 列面）**＋
  **6 张新面精确锚点（多日标的缺申报位）**＋**正/负对照证"0 非尺瞎"**＋**本班自犯一枚假轻底座尺当场自纠留痕**。
- 请 ⑩/总筹定夺：本席连续三班（03/04/05）四闸下 0 出分，而真源尺已给出 103 张的完整归宿
  （A2／A?7／B16／C52／D0／U26＝现器可考面为 0 且非本班一把尺的说法）。建议按在册停手口径把本席节拍降档或并席，
  把上下文与算力让给可出分分片；exit/portfolio/position_flow 族属 ⑧B 席，本席不代裁、不越片。

### 八、旗债与袋面（入袋前写定，禁袋后再改盘面）

- 旗债①＝`--allow-non-worktree` 使用一次：本班首投锁外预检判 `[WORKTREE-REQUIRED]`（活跃他会话实测 4 枚
  st-qoder-p01-1015-12／p02-1015-07／p03-1015-06／p06-1015-10，预检耗时 12.8s 未落袋），依门自列逃生通道加旗重投；
  袋 JSON 的 meta 面不记旗标（班次 03/04 实测），故旗债只在本台账留痕，审计侧按袋面找旗会查无＝在册形态。
- 一值守一袋＝本班只投一袋（两件：ledger.md＋checkpoint.md），本班零分数册行、零卡面、零热册随袋；
  分数册主册现 `AM`（他席在途）＝绝不随袋（袋=整档快照＝归属篡改）。
- 会话活性锚＝本班值守内两次被外来回收（16:58:02 与 17:05:08 心跳末行自证 `session not in registry`），
  两次同串重注册＋独立后台重启守护；第二次重注册携 `logical=True` 被门降级为 False（chief-form verification failed，
  fail-open 照常注册）＝恒定班想要逻辑长会话锚的通道对本席不可用，如实登记待 ⑩ 定性。
- 主区 `.git/index.lock` 检疫读数＝mtime 15:27:38・长度 0・存活 git 进程StartTime 全在 17:05/17:19＝无主陈旧锁；
  本班**不删**（共享态且属 ⑩/运行班处置面），改走队列正门（在册：主区 index.lock 不挡入袋只挡直连落地）。
