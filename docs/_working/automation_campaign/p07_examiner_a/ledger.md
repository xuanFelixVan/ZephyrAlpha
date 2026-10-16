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

# ⑦考工A 班次 06（起手 date 实测 10-15 18:10:12；写册时点 10-15 19:3x；本班实测耗时约 87 分钟至交班，超 60 分班期，超支全部记因见 §七）

## 一、防重入（在册三证＋一枚 phantom 班判定）

- 旧址游标：cursor last_run 17:13:12＝班次 05 已交班，其袋 5fb43bb823 于 17:22:39 落 HEAD（两件套 ledger+checkpoint）。
- 开工前盘面异象：`.runtime/tmp/p07/` 内 17:37–17:46 已存在三件自标 `CONSUMERS] ⑦考工A 班次06` 的探针
  （shift06_classify.yaml／shift06_bface_probe.{py,json}／shift06_panel_shape_probe.{py,json}），且 18:09 有人起
  06 号心跳守护失败（`heartbeat_1015_06.log`：Errno 13 读 + WinError 5 改名 `session_registry.json` 被占）。本班**不重跑同签名事实**，
  直接复用其 B 族 16 张逐表清单与 shape 实验结论（market-series 目标喂 panel 路 ⇒ `TypeError: '>=' not supported between ndarray and Timestamp`）。
- phantom 06 判死四证（在册三证补一枚注册表证）：①进程表（Get-CimInstance Win32_Process python.exe/pythonw.exe 全表）无 shift06/fexam/calibration 命令行，
  仅 p06-1015-11 与 x2-1015 两支心跳守护；②`.runtime/session_registry.json` 顶层键＝{st-qoder-p06-1015-11, st-qoder-x2-1015}，无 p07 任何条目；
  ③队列零 `p07-1015-06` 袋（grep -c＝0）；④17:46 后该目录零新写（40 分钟静默）。判定＝前任未交班且已停手 ⇒ 本班取 06 号续做。
- 冷启动三步：python 3.12.8 ✓／setup_dev_env --check installed ✓／lock_files cleanup「CLEAN — 无死锁需要清理」✓／
  process_reaper --status source=live・scanned=30・killed=0・reported=2・whitelist_hits=17・worktree_changes=5779>50（在册并行漂移告警）・
  watermark commit_pct=85.47（本班据此**只串行跑批、不自造并发**，见 §五）。
- 会话身份：`SessionRegistry().register('st-qoder-p07-1015-06', pid=0, logical=True)` ⇒ logical 被降为 False
  （回显 `chief-form verification failed … proceeds with logical=False`）＝在册"恒定班拿不到逻辑长会话锚"形态第三次复证；
  守护按在册处方独立后台起（`python -m zephyr.gov_enforcement.rule_bridge.heartbeat_daemon <sid> <repo> 30 ""`），
  心跳 `status:"alive"` 时点 date 实测 18:26:06。

## 二、本班主产出＝推翻前任"现器可考面=0"＋8 张出分（0 pass / 8 fail）

**三枚纠偏（都是尺的口径错，不是卡面新面出现）**

- 纠偏①（class B 语义误读）：`card_binding.classify_card` 里 B 的机判 reason 逐字＝
  `panel_deferred(去重/撮合口径须逐表面核)`（scripts/backtest/fexam/card_binding.py:355-362）＝**考工本席自己的逐表面工序**，
  前任把它与 C 一并归入"现器不可考"⇒ 16 张 B 面被错误后置。
- 纠偏②（C 词表族盲，面积更大）：C 的第一道触发是 `_INDEX_TARGET_RE` 只认**指数级**次日目标
  （scripts/backtest/fexam/card_binding.py:330-338，reason=`target_face_not_index_next_day`）。对 `signal_kind=panel` 的卡，
  "个股次日收益／同表 t+1 宽表"本就是正解目标形，却被这指数词表判死 ⇒ 本班全 103 张 prereg 里扫出
  **panel 且目标=个股次日** 的卡 24 张，其中 21 张被归 C、3 张归 B；按卡面绑定逐张人读后可考面 ≥8（本班烧尽 8 张）。
- 纠偏③（算力窗用错闸）：班次 03/04/05 以自设 `commit_pct<80%` 为开 panel 面前提（三测 89.13／94.98／89.52 皆不开）。
  在册机器闸实测＝`python scripts/backtest/compute_window_gate.py window` → `{"window":"heavy_ok","is_trading_day":true}`（18:18:04 date 配对），
  `check --purpose … --compute-class mixed` → `{"allowed":true,"reason_code":"gate_allow_off_hours"}`；
  SOP 侧：§3-D 研究态 24 小时不停＋§3-④"小考试（单卡 ic 类）白天空闲显存≥8GB 即放行"＋§3-B 白天禁算只在**实盘态**表（§3-E）；
  GPU 实测 `gpu_watchman.py status` → free_gb=21.29 util_pct=29.0（19:37 复测 free 21.13/util 7.0）。
  ⇒ 前任"15 张 hfq panel 不开"的门槛判据无在册来源，本班按真闸开工。

**物化通道与两把对照尺（先证尺再出分）**

- 通道同源化：本班自建 argMax-in-CH 分年块装载 vs 真源 `ch_data.load_panel`（scripts/backtest/fexam/ch_data.py:149）
  同月窗逐格对拍＝shape 同 (19×5371)／102,049 格／**max_abs_diff=0.0**／NaN 模式全等／非空 101,942；
  负对照＝换月（2024-07）两通道仍逐格等且与六月面板不同形（索引不同）⇒ 非"两查询都返空"。凭据 `.runtime/tmp/p07/shift06_channel_eq.json`。
- 卡面冻结实证当正对照：L3-03/ablation/02 卡面 `data_window_evidence` 写死封板 74（2023-06-05）／893（2024-10-08）、
  炸板 23／2,268、一字 41/5,355。本班 CH 直读复算＝**5/5 逐字同值**（`.runtime/tmp/p07/shift06_batch3_dry.json`）⇒ 涨停判定谓词与在册证据面同物。
- 宇宙掩码 V1（按 8 张卡中 6 张卡面 `universe_rule` 原文直译）：前缀留 5,365 票／剔 279；窗内留 7,152,422 格；
  ST 对 297,990 命中面板 233,200 格；"前缀留但 kline_daily 无首行情行"＝0 票。
- 底座实测：kline_daily_hfq 窗内唯一 (symbol,trade_date)＝7,590,928（与班次 04 探针同值，未重跑其事实）；
  卡面 evidence 的 5,583,635＝symbol∈stock_basic 子集（本班实测 stock_basic 5,787 符号／面板内命中 5,599）⇒ 两数不同物，勿混用。
- 数据源侧一枚澄清：窗内 hfq 的 tushare 源 1,622 行**全部**是 symbol=510050（ETF），与 recalc 源无同键重叠
  ⇒ "指数行撞个股键"这条假雷排除（曾按 stk_limit/000001 形态疑过，实测证伪）。

**8 行分数（rows[96..103]，run_id=st-qoder-p07-1015-06，全 fail）**

| rows | card_id | ic_mean | ic_ir | oos_ic | n | 触发柱 |
|---|---|---|---|---|---|---|
| 96 | L3-07-3/calibration/03_target_close_to_close_control | −0.041730851525535746 | −0.25500127905141573 | −0.052205256094141735 | 1621 | ic_mean, ic_ir |
| 97 | L9-A01/calibration/04_universe_st_and_age_control | −0.041730851525535746 | −0.25500127905141573 | −0.052205256094141735 | 1621 | ic_mean, ic_ir |
| 98 | L3-07-3/calibration/04_universe_no_filter_control | −0.026627857824190977 | −0.17433923952160182 | −0.03599276247605634 | 1620 | ic_mean, ic_ir |
| 99 | L9-A01/calibration/05_target_t1o_to_t2c_control | −0.026543146087269584 | −0.17403285244184388 | −0.03606360213682766 | 1620 | ic_mean, ic_ir |
| 100 | L3-07-1/ablation/02_烂板剔除步 | −0.02081657736952234 | −0.48213330858406755 | −0.023224275255530096 | 1620 | ic_mean, ic_ir |
| 101 | L3-10/calibration/02_一字板不可成交 | +0.009870424514809526 | +0.38502259649845294 | +0.011096301662463975 | 1524 | ic_mean（ic_ir 0.385>0.3 过线） |
| 102 | L3-03-1/calibration/02_涨停基因 | −0.023940958475789188 | −0.2300658844993045 | −0.023210717446075318 | 1605 | ic_mean, ic_ir |
| 103 | L3-01/calibration/02_成交额下限剔除 | −0.04326354947003124 | −0.2942658386595791 | −0.04440405934941715 | 1620 | ic_mean, ic_ir |

- rows[96] 与 rows[97] **逐位同值**＝两卡申报面同形（同 `ret_20` 式＋同"同表 t+1 close→close"目标＋同 universe_rule 原文），
  非复跑伪影；请 ⑨ 判卷按"两题同卷"合并叙述（同轴第二次读数不额外计独立试次）。
- 目标面两形并存是本批设计面：close→close（96/97）与 T+1 可成交 open_{t+1}→close_{t+2}（98-103）；
  后者 n=1620（右端多失一日＝h=2 面必然）、涨停基因 n=1605（60 日回看需宽窗预热，本班把 aux 面板拉到 2018-06-01 起）。
- 一字卡 n=1524：卡面明写"一字样本收益记 NaN（禁假设以涨停价成交）"，本班按 t 日标记掩 t 日收益（逐字直译），
  窗内按该规则剔除 12,955 格 ⇒ 96 个交易日的有效对跌破 30 地板被 fast_rank_ic 丢弃（scripts/backtest/fexam/ic_exam.py 内 `ic[valid<30]=nan`）。

## 三、本班自犯并当场推翻的一枚假绿尺（旧句留此不涂）

首版前置闸 `preflight` 里本班写 `fast_rank_ic(s, t)`＝**同日配对**，而判官 `_panel_metrics` 走 `ret = target.shift(-1)` 再算
（scripts/backtest/fexam/calibration_exam.py:249-252）⇒ 闸量的是另一面。症实在 L3-10/02：闸报 `ic_days=822 / ic_std=0.0`
而同题行内 n=1524。修尺（闸内同做 shift(-1)）后，本班以**已在册行做正对照**复测尺：闸 ic_days=1621==rows[96].n、
闸 ic_mean/oos_ic 与行**逐位同值** ⇒ 尺与判官同面后才放行第二、三批。凭据 `.runtime/tmp/p07/shift06_gate_control.json`。

附：为何必须自设此闸——`ic_exam.ic_stats` 对 `len<2` 返回 **0.0 而非 NaN**（首行 `{"ic_mean":0.0,"icir":0.0,"n_obs":0}`），
而 `fast_rank_ic` 把日有效对 <30 整天丢弃 ⇒ 退化面会往永久册写一条"ic_mean=0"的**测得零信息**假陈述；
判官 sample_gate 只兜 NaN 支（`_judge_calibration_face` 的 "无有效主指标"），兜不住 0.0 支。⑧B 席 1015-05 班钉的
29↔30 悬崖在本班个股 panel 面不咬（日均 4,285-4,311 名，最小 196 名/日），但 0.0 支对退化截面同样成立，故闸长住本班工序。

## 四、事故如实上报＝本班值守内两度被外部落地改写盘面（在册形态复证，非新故障）

- 19:00:53 他会话袋（④席"HEAD ABSENT 抢救"，其后 19:00:26 ⑨席 batch4 墓碑袋与 19:04:32 一列 examined 卡面复位）落地窗口内，
  本班 19:06 前完成的 4 次 run_card 产物被部分回滚：**分数册主册与 `docs/04_research_records/backtest/scores/2026/` 目录**
  一度盘面/index/HEAD 三面查无（19:01 实测 `ls` 报 No such file or directory，`git ls-files` 无、`git cat-file -e HEAD:` 报 does not exist），
  四张卡面 status 被复位回 `preregistered`；册被放回时停在**本班首枚追加后的中间态**（97 行／sha 70c71e7b1397＝本班第一行 sha_after），
  后 3 行被吞。
- 恢复链（可复跑）：本班唯一存活副本＝开工时自建的 pre-shift 备份 `.runtime/tmp/p07/shift06_register_preshift.bin`
  （96 行／132,248 B／sha12 d77773545f5b）。盘面回来后逐位前缀核验 `startswith=True` ⇒ 以 97 行为新基线补投 3 行，
  **sha 链与首投逐位同**（70c71e7b→f6d5cee1→8703e223→9c4582be）＝同码同参跨进程确定性自证（不是"重跑碰巧同值"，是字节级同）。
  rows[96] 存而卡面被复位 ⇒ 本班对该卡只做 3+/3− 四行手工对齐（status/lineage），其余 7 张由 run_card 自翻。
- 交班时终态（date 19:37:04 实测）：册 104 行／139,777 B／sha12 21ce93c0a55c／`cum_prefix(对 pre-shift 96 行)=True`／本班净增 7,529 B；
  entry 面 status＝preregistered 95・examined 76・blocked_on_impl 29・blocked_on_data 69・empty 133（总 402；
  18:10 首测为 103/68/28/69/133 总 401；差额对账＝19:14:09 盘面新增 1 张 `L9-A02/calibration/13_crossday_minutep*`
  （自宣 blocked_on_impl，卡面 status_reason 自述唯一缺腿在 ⑤ 算子与 csv 载体面，非本席）＋本班 −8）；
- **上报请求（属 ⑩/运行班写域，本班不代处置）**：`docs/04_research_records/` 全馆 HEAD 侧 0 件（`git ls-tree -r HEAD` 实数 0）、
  index 侧他会话 19:04 那波重新落回 `A`（现 `AM`＝他班 97 行快照＋本班 7 行在盘）。在分数册获得落地面之前，
  任何整树级操作都能再洗掉分数；建议 fexam 侧加一条"每批 run_card 后自证 sha＋把册副本落 `.runtime/sessions/<sid>/` 安全区"，
  本席不代拍实现。

## 五、本批不做（自带承重证据）

- 不烧 tick/重放面（L4-03/02、L4-11/02 及 L9-A02 全族）：需 MatchingLogic/逐笔重放核，属 ⑤ 写域；
  且 19:00:53 后 L9-A02/03-12 一族 status 已由他会话置 blocked_on_data/blocked_on_impl，非本席领卡面。
- 不烧 market-series 目标 × panel 信号混形面：phantom 06 的 shape 实验已给出 `TypeError` 凭据，本班未重跑同签名事实。
- 不烧三张"口径未钉"卡（详见 §六 转⑥）＝不开考、不代拍、不改卡面。
- 不动 17 张 `M `（他班在途卡面）与分数册落地面；本班袋只含自家四件（ledger/checkpoint＋本班 8 张卡面翻态）。
- 不自造并发批（commit_pct 85.47，在册崩面为 git add 0xC0000142）＝全程串行单批，面板缓存复用把装载次数减半。

## 六、堵点与移交（本班零改判据、零挪门柱、零自拟口径）

- **转⑥（三张卡口径未钉，任一钉死即回收 ≥1 张）**：
  ① `TDM-E-L3-03/ablation/02_双池代理合成`＝短线代理分第二项"当日涨幅截面分位"未钉源表口径
  （本卡自身 `data_window_evidence` 已证"limit_up 是不复权价须配 kline_daily，配 hfq 同日误判 3,882 家"，
  但**涨幅**未写 kd.pct_change 还是 hfq close/close_{t-1}，二者在本窗不同物）；
  ② `TDM-E-L3-03-2/calibration/02_均线多排`＝"趋势分位=计数与 (close/ma_20−1) 的截面**复合分位**"无合成式；
  ③ `TDM-E-L3-12-3/calibration/02_获利盘占比`＝"chips_winner 取值域 0-1 或 0-100 **需在首跑时以分布实证并写死换算**"
  ＝把冻结位让给考工看数后决定，与卡面自写 `frozen_note: 看数前冻结` 互斥，本席不代拍。
- **转⑤（用芯面凭证缺口＋散文 regime 崩续证）**：`IC_DEVICE=auto` 缺省档在本机现测 `_resolve_device()='gpu'`
  （free 21.13GB／util 7.0%，scripts/backtest/fexam/ic_exam.py:213）；但 `device_ledger` 只在 `run_exam` 返回体内
  （ic_exam.py:447），**run_card→_panel_metrics→fast_rank_ic 路径不落任何持久芯账** ⇒ 本班 8 张无法按行出具用芯凭证。
  如实申报＝本班既不断言"GPU 读数"，也不断言"回退 CPU"（无凭证即两面都不声明），请 ⑤ 把芯账接到行面。
  散文 regime 装载崩复测两枚（L9-A15/calibration/02 的 `bull_note` 与 /03 的 `unavailable` 键）＝
  `_span_pairs` 命中日期 <2 枚时退回整串单点 ⇒ `pd.Timestamp` 抛 `DateParseError`（与班次 05 在册同因，属 ⑤）。
- **转⑨（在册两枚 panel 行不可复现）**：rows[95]（L9-A01/02，run_id=st-autoplan-verify-20261015）与 rows[73]
  （L3-07-3/02，run_id=st-e2e-test-p09-*）用"卡面申报口径＋现库"**复现不上**：15 枚候选组合全不中
  （宇宙 none／prefix／age／st_excl／prefix+age／prefix+st／age+st／prefix+age+st／stock_basic × 信号 calendar/own_seq × 目标 shift/pad），
  最小绝对差 3.34e-4（st_excl 版 −0.0405968419728668 vs 行内 −0.04026245066618168），n 全为 1621＝窗与预热面对得上而截面成分对不上。
  库面时移已排除：窗内 `max(ingest_ts)=2026-09-24 07:27`，今日新灌 1,457 行全落窗外。
  另请 ⑨ 注意同 node 三卡宇宙不同物：L9-A01/**02** 卡面**无** `universe_rule`，而 /04・/05 有 ⇒ 三行不同截面，判卷须分面不得并比。
  凭据 `.runtime/tmp/p07/shift06_caliber_grid.json`＋`shift06_caliber_grid2.json`。
- **承接在册未闭（本班照旧避开）**：断供册 `research_report_hot_value_rating_change_empty` 行仍 `status: open`
  （src/zephyr/data/config/known_data_gaps.yaml:1345-1357，19:0x 复读未改；`git log --since=18:00 -- 该文件`＝零命中，
  即本班值守内 ① 席未动该行，其 B-23/B-24 两条是 17:45 的 P01-12 班落的地＝本班开班前事实）
  ⇒ 挂它的 L9-A17/02・L9-A17/03・L2-09/03 照旧不开考，待 ① 席复测改行。
- **转⑥/⑩（前任移交清单里那 6 张多日面未回收）**：本班值守内未见任何卡补 `_forward_face` 三件齐申报位
  （全库申报者仍＝班次 01 的 class D 8 张，现全 examined）⇒ L9-A08/02・A11/02・A12/02・A13/02・A17/02・A17/03 仍等 ⑥。

## 七、保底条款与耗时如实呈报

- 本班 **8 张入册**＝达"每班 ≥8 张"门槛（0 pass / 8 fail；pass 为零是读数事实，非工序未完）。
- 耗时：date 两点实测 18:10:12 起手 → 19:37:04 写册＝167 分钟跨度，扣 phantom 判定与事故等待，本班自估净工时约 87 分钟；
  超 60 分钟班期的三项归因：①phantom 06 三证判定＋复用其探针（约 15 分）②CH 面板装载（hfq close/open/volume/high＋kd 四价＋limit_up＋ti 均线族，分年块共 15 支，约 25 分）
  ③19:00-19:07 事故取证与 3 行补投（约 20 分）。
- 与班次 03 的"连续三班 0 出分"在册句**不符事实**（按更正另起、不涂旧句原则留此）：班次 03 自身 last_batch 记
  "6 张出分：0 pass / 6 fail；分数册 84→90 行"＝03 班是 0 **pass** 而非 0 **出分**；04/05 两班才是真 0 出分。

## 八、补记（写册后 14 分钟内两枚事实，另起一节，前文不涂）

- 袋①`q-20261015-st-qoder-p07-1015-06-0001`（ledger+checkpoint 两件）已判 **dead**，dead_reason 逐字首段＝
  `landing 异常: RuntimeError: git reset --hard refs/heads/dev -> rc=128: Updating files: 3% (799/21108) … 9% (1985/21108)` `[GATE-SELFDOC:GIT-DANGEROUS]`
  ＝落地器在对 21,108 文件做整树 `reset --hard` 的过程中失败。本班据此把 §四 的归因**收窄为机制级**：
  洗掉本班 3 行与四张卡面的那一次（19:00:53-19:04:32）与本次死袋同属"落地期整树 reset"这一类动作，
  不是针对本席文件的定向覆盖；本班自测 stash 面与"整馆被扫件数"的他席说法对不上（`git stash show --name-only stash@{0}`
  的未跟踪侧 `stash@{0}^3` 本班实数＝1 件，且在 `docs/_working/automation_campaign/p09_scorekeeper/ledger.md` 内 grep "5688" ＝0 命中），
  故本节**不引用该数字、不作机制定案**，只登记"落地期整树 reset 会在失败点上洗盘面"这一本班可复验事实，机制归口请 ⑩/维护班定性。
- 盘面完好性复核（reset 失败点后本班三件逐件复量）：ledger sha12=3f2770cde295＝袋① blob 逐位同；
  checkpoint sha12=84447488a7e1＝袋① blob 逐位同；分数册 sha12 仍 21ce93c0a55c（104 行，本班 8 行齐）；
  8 张卡面 status 仍 examined。⇒ 本次 landing 失败未洗掉本席交付。
- 因此本班交付终态＝**袋②（8 张卡面）pending ＋ 袋③（两件活文档，含本补记）重投**；分数册照旧不随袋（index 仍是他班 97 行快照）。

### 八·附更正（本班 §八 里一处假锚，另起留旧文，20:0x date 实测）

- 本班 §八 写的"在 `docs/_working/automation_campaign/p09_scorekeeper/ledger.md` 内 grep `5688` ＝ 0 命中"**是假锚**：
  真实目录名＝`docs/_working/automation_campaign/p09_score_officer/`（本班把席名写错⇒0 命中无判别力）。
  在册 [citation-must-be-greppable-before-writing] 形态**本班复犯一枚**，如实登记。
- 按真路径复核（p09_score_officer/ledger.md:923/940/970）＝⑨席 15 班已把本班 §四 的推测升为**机制级在册事实**：
  19:00:01 一次整树 `git stash`（身份 `lane <lane@local>`，reflog ts 1792062001）让分数馆 30 件在主区磁盘消失 6 分钟；
  该窗内 HEAD＝0 件、index 面虽在而工作树已被摘、载该册的 10 只袋**全部 dead** ⇒ 按在册"三面＋四态"尺会误判"成绩已丢"；
  该班并已建无损锚 `refs/recover/p09-scorehouse-20261015`。
- 由此给下一班加一条在册风险（同处 ⑨席 ledger:970）：**`stash@{0}` 未 drop ⇒ 若有人在主区 pop，分数册按回 97 行**
  ＝会吞掉本班 rows[96] 之后的 7 行。下一班开班第一步除"现测盘面册 sha＋与 `shift06_register_final.bin` 对拍"外，
  还须 `git stash list` 看那枚 stash 是否仍在；行数骤降**先查 stash 与 refs/recover，勿判成成绩已丢、勿急重跑考试**。
- 本班终态与 ⑨席 15 班终测锚逐位同：rows[103]／磁盘 sha12 21ce93c0a55c／104 行（⑨席 19:38 测，本班 19:58 复测同值）。


# ⑦考工A 班次 06·本席实例（同 sid 双跑，见 §三之二；起手 date 实测 10-15 17:28:59，写册 10-15 20:0x）

> 本节是**第二跑者视角**的收班段。台账第 585 行已有"班次 06"（同 sid `st-qoder-p07-1015-06`，
> 18:10:12 起手、19:37:04 交游标、8 张 hfq panel 出分）＝本席非重复开工，而是**同名单列**。
> 两班分工：它烧掉可考面，本席查"为什么前面三班判面=0 而面其实有"。判据零改动。

## 一、防重入与取号（两址同读实测）

- 旧址游标 last_run 17:13:12＝班次 05 已交班；新址 `docs/04_research_records/cross_domain/automation_campaign/p07_examiner_a/checkpoint.md`
  ＝`cursor: 未开始`・`last_run: —`（滞后镜像，在册两址形态）⇒ 取旧址为活游标。
- 17:3x `grep -c "^# ⑦考工A 班次"`＝5 ⇒ 本席取 06；20:0x 复量＝6（多出的那段是同 sid 第二跑者 19:3x 写的）。
  **同一秒算出同一号**＝本岗 sid 形态可被外部推算，见 §三之二。

## 二、冷启动三步（每步配 date）

1. RULE-ENV：python 3.12.8（17:28:59）。
2. `lock_files.py cleanup`（17:29）：零本席件被收。
3. `process_reaper --status`（last_run 17:29:26）：source=live・scanned=31・killed=0・worktree_changes=5504>50・
   watermark commit_pct 86.98／cpu 79.5／degraded False。CH 窗 01:00-04:00 全程窗外。
- 活性锚：`open_session` 注册 pid=0，`logical=True` 被门降级 False（chief-form failed，fail-open，在册同形）；
  守护以独立后台进程起。⚑ 后台任务通知报"completed exit 0"，而 19:51 实测 pid=38792 仍活・心跳 age 35.9s＝
  **通知≠进程死**，活性只认进程表＋心跳两证（在册复证）。守护自身 `session_registry.json` 两次权限拒绝（Errno 13/WinError 5）
  ＝旁路 legacy 写失败，非致命，如实登记。

## 三、开考结果：本席实例 0 张入册；本班三枚实测面

### 三之一 【P 级·归属】8 行分数（rows[96..103]）run_id＝本席 sid，而本席零 run_card 实跑

- 19:53:58 实测：分数册 104 行／pass 2／bytes-sha16 `21ce93c0a55c450e`；rows[96..103] run_id 全＝`st-qoder-p07-1015-06`，
  card＝L3-07-3/03・L9-A01/04・L3-07-3/04・L9-A01/05・L3-07-1/02・L3-10/02・L3-03/02・L3-01/02，8/8 fail。
- 本席自证：本班全部动作＝只读普查＋合成面正/负对照（零 CH・零分数册写・真卡喂副本且 sha 起=止 705dd9d43d42f619）＋两件活文档写。
- 后果（请 ⑩ 定策）：恒定班 sid `st-qoder-p07-<MMDD>-<NN>` 的 NN＝"当日台账班数＋1"＝确定性可推算 ⇒
  两个跑者共享同一 claim 命名空间（`lock_files.py` 按 sid 记持有者，同 sid 之间**零互斥**），
  心跳/claim/入袋归属全不可分。建议 sid 加跑者位，或自动器取号改读在册游标。
- 本席处置：不认领・不改判・不随袋（分数册 96→104 行是他班在途面，随袋＝整档快照归属篡改）。

### 三之二 本班主交付＝"entry 可考面=0"的第三枚尺错：**判据与执行器对 panel 目标形状的要求正好相反**

一句话：绑定册把"目标是全市场指数次日面"当作 panel 卡的**合格**条件，而执行器的 panel 判分面**吃不下**市场级一个数。
两头各说各话 ⇒ 这批卡被放进了一个叫 B 的"看似可考"桶，实际一喂就崩。

- 判据侧真源（本班直读）：`card_binding.py:330-338` ⇒ `_INDEX_TARGET_RE` 不命中才归 C（`target_face_not_index_next_day`）；
  命中后 `if kind == "panel"` 一律 `cls=B, reason=panel_deferred(去重/撮合口径须逐表面核)`（:355-362）＝**考工自家工序**，非他席堵点。
- 执行器侧真源：`calibration_exam.py:961` 指标函数**只按 signal_kind 选**；`:249-268` `_panel_metrics` 做逐日截面秩 IC，
  `:250` 无条件 `target.shift(-1)`，且源码切片实测 **`_forward_face` 只在 series 路被调（in_series=true／in_panel=false）**。
- 逐张形状账（尺＝`.runtime/tmp/p07/shift06_bface_probe.py`＋`.json`，`target.primary` 全串等值分桶，非子串放宽）：
  B 族 16 张＝**12** 张市场级 `next_day_index_return`（形状对不上）・**2** 张 `next_day_stock_return` 个股宽表（形状对得上：
  L3-07-3/03・L9-A01/04，恰是同 sid 那班实测跑通的两张＝尺的预测被自然实验证实）・**2** 张派生重放面
  （L4-03 `net_expected_gain_bps`・L4-11 `net_expected_cost_bps`，属重放引擎另闸）。
  ⚑ 更正留痕：本席 18:0x 口头初报"14 张形状对不上"，落笔前等值复算拆成 **12 形状＋2 重放**；
  退回名单的**集合不变**＝16 张除 L3-07-3/03・L9-A01/04 之外的 14 张，子因是两个，别当一类出题。
- 正对照（管形未瞎）：目标换成与信号同形的 189 列宽表 ⇒ `_panel_metrics` 正常出 ic_mean −0.00032466637911510843・
  ic_ir −0.004540490303771497・oos +0.0002993341601637285，`judge` 对随机面**正确判 fail**（ic_mean 柱触发）。
- 负对照（按卡面 primary 喂市场级序列）：`TypeError: '>=' not supported between instances of 'numpy.ndarray' and 'Timestamp'`，
  崩点 `calibration_exam.py:261`（`ic.index >= pd.Timestamp(oos[0])`）＝**装载崩，非判据红、非缺数**。
  按总包 20:0x 指令面处置：执行器形状预检施工中，上线前此类 TypeError＝已知形状不匹配 ⇒ 记 **blocked**，不硬啃、不改判据。
- 附带一枚（转⑨/⑤）：panel 路 `mono_spearman` 恒 None（:268），卡面冻 `mono_spearman_min=0.6` 却**从不被评估**；
  `_judge_calibration_face` 跳过并由分数行 `unjudged` 显形（非静默放行），但"门柱全过"的叙述对 panel 卡不成立。

### 三之三 两把尺被本班实测推翻（承接同 sid 那班的结论，本席独立复算）

- `commit_pct<80%` 算力窗＝**三班沿用而无在册源**。本席在真源闸实测：`scripts/backtest/compute_window_gate.py window`
  @20:01:32 ⇒ `{"now":"2026-10-15T20:01:32.586250+08:00","is_trading_day":true,"window":"heavy_ok"}`＝重活放行。
  本席 §五 因此**撤回**"本班不起 hfq 长批因算力窗未成就"这条拒绝理由（真因改为：归属面已脏＋本班定位在只读取证）。
- `check --compute-class mixed` 需 `--purpose`（本班实测 usage 报错 rc≠0）⇒ 同 sid 那班叙述的 `gate_allow_off_hours` 读数本席**未复算**，
  待下一班带 `--purpose` 复测后再入册。
- GPU＝**加速不扩面**（本席独立验）：`smoke_gpu.py --tier small` 实测放行（free 21497MiB・cupy 14.2.0・5 用例 worst|dIC|=2.220e-16・
  SMOKE-OK，两档制落 HEAD `f8e3c2b717`）；但 `calibration_exam.py` 对 GPU 零引用（grep 实测），内核只接在 `ic_exam.py`
  （IC_DEVICE=auto＋看门人）⇒ 预检放行不改变可考面，本席不据此开考。

## 四、堵点与移交（判据零改动）

- 堵点①（转⑤，施工中已领）＝panel 目标形制缺口，锚点 `card_binding.py:330-338`／`calibration_exam.py:249-268・:961`；
  对应面 12 张；本席只交锚点与崩点，不动码。
- 堵点②（转⑩，P 级）＝同 sid 双跑与 claim 零互斥（§三之一）。
- 堵点③（转⑥，按总包 20:0x 指令面执行）＝B 族 14 张 ill-formed 退回重新出题（具名清单见 §三之二，子因 12 形状／2 重放）。
- 堵点④（转⑨，复证非新证）＝`rows[96]≡rows[97]` 逐值同数（ic_mean −0.041730851525535746／n 1621）。
- 堵点⑤（承接在册未闭，本班 19:53 复测）＝①席 research_report 断供行／⑥席多日标的三件齐（6 张）／⑤席散文 regime（5 张）
  均未见闭合证据；blocked_on_impl 27→29 是⑥席在造新卡（17:27 L9-A02/12 自述缺物化算子），不是解锁。

## 五、本批不做（自带承重证据）

- 不起 hfq 长批：真闸 `heavy_ok` 已放行，但本席本班定位＝只读取证＋归属面已脏（同 sid 双跑），再起批只会把撞名事故放大。
- 不硬啃 12 张形状面：按总包指令记 blocked，等执行器形状预检上线。
- 不重投 dual_arm 7 张・不开挂 research_report 三张（凭据在班次 04/05 台账）。
- 不改判据／不补卡面申报位／不改断供册／不动 `compute_window_gate`＝分属⑤/⑥/①写域。
- 不认领同 sid 8 行、不随袋分数册。

## 六、自检两轮

- 第一轮（only-add）：本席唯一写面＝本台账＋游标两件（claim 持有者实测 `st-qoder-p07-1015-06`）；
  分数册零字节；卡面零翻牌（喂副本，L2-07-1/03 bytes-sha16 起=止 705dd9d43d42f619）；
  游标走"新游标＋同 sid 那班原文逐字留档"超集式，脚本内 Counter 断言旧行零缺失。
- 第二轮（结论↔读数对齐）：12/2/2 由全串等值分桶（谓词在脚本内可复跑）；崩点行号由源码表达式对号；
  "GPU 不扩面"由 grep 零引用＋run_card 无 device 参数双证；"算力窗无在册源"由 `compute_window_gate.py window` 现测读数支持。

## 七、保底条款如实呈报

- 本席实例 **0 张入册**；本岗 06 班（含同 sid 第二跑者）净出分 8 张＝分数册 96→104 行、examined 68→76。
- 实测耗时：17:28:59 起手 → 20:0x 写册，两时点 date 配对约 **150+ 分钟**（体感钟在册偏快，不采信自述）。
- 本班增量（勿读成"又一次四闸 0 张"）＝① 判据 vs 执行器对 panel 目标形状**互相矛盾**这枚第三尺错（含 12/2/2 具名账）；
  ② P 级同 sid 双跑归属事故；③ 推翻三班沿用的无源算力窗；④ GPU 加速不扩面的独立实测。

## 九、本班自犯并当场推翻＝"phantom 判死"是错的（同 sid 双跑，另起留旧文）

- 本班 §一 用四证（进程表无 shift06／注册表无 p07 条目／队列零袋／17:46 后盘面零新写 40 分钟）判 17:37-17:46 那批探针的主人为"已死 phantom"，
  据此取 06 号续做。**该判定错**：20:0x 盘面 ledger 由同实例追加 `# ⑦考工A 班次 06·本席实例（同 sid 双跑…）` 一节，
  自述起手 date 实测 **17:28:59**（早于本班 18:10:12），并把它自己的游标推到顶、把本班游标逐字留档为
  `## 前班游标逐字留档（班次 06 同 sid 第二跑者原文）` ⇒ 它是**可恢复的后台会话**，不是死班。
- 四证失效的机理（登记给 ⑩ 与本岗下一班）：①"进程表无我脚本"只证**当时**没有在跑的 python，恒定班的会话可在两次工具调用之间长睡后醒来；
  ②"注册表无条目"恰是本班自己也复现过的形态（本班条目 18:34 被外来摘除过，守护随之自退）＝**条目缺失不证会话已终**；
  ③"队列零袋"只证未交班；④"40 分钟零新写"在后台会话形态下不构成死亡证据。
  ⇒ 在册三证法（队列无新袋／worktree 无新写／无 commit 尾标）用于**判前任已交班**够用，用于**判前任已死**不够；
  本岗若要独占同 sid 续做，正解＝**改取新号（本班应取 07）或先向 ⑩ 报双跑**，而非自判死刑后共用 sid。
- 双跑的实际后果与本班处置：两实例都写过同一批文件——分数册本班 8 行（rows[96..103]，盘面 sha12 21ce93c0a55c／104 行 20:05 复测同值）
  与它 0 行＝册面无撞；ledger/checkpoint 两边都是纯追加或超集式改写（本班实测：袋④ checkpoint 的 140 行非空行在现盘面**全部还在**，
  ledger 现盘面以袋④字节为严格前缀）⇒ 零内容损失。但本班袋④（q-…-0004）若先落地会把它实例的顶游标与 §九 之后内容回退 ⇒
  本班立即另投**袋⑤（吃进现盘面全文＝两实例并集）**并在此登记，请 ⑩/维护班把袋④按"同 sid 后袋严格超集"处理（勿双落）。
- 交叉印证（不是本班结论的重复）：另一实例独立得出"第三尺错＝判据与执行器对 panel 目标形状的要求正好相反"，
  与本班 §二 纠偏②（C 词表只认指数目标）同一方向的两次独立观测 ⇒ "entry 族可考面=0" 已由两席实例各自推翻。


## 八、四族形状分布账（同班续做，date 实测 20:3x；尺＝.runtime/tmp/p07/shift06_shape_census4.py＋.json）

> 交 ⑩ 晨报用。一句话：**entry 族 95 张 prereg 里"考题形状对得上"的有 39 张，真"形状对不上"的只有 10 张，
> 前面三班把 45 张当成形状闸拦掉了——那是自动绑定层的边界，不是考工不能考。**

- 尺的定义（只量门柱目标面，不量信号供数）：形状只按 `target.primary` 判；`target_source` 只用来查自相矛盾；
  词表复用绑定册真源 `card_binding._INDEX_TARGET_RE`／`_HORIZON_RE`，不另起第四套私有口径。
- 正对照（在册"每处绿先证能红"）：拿**今日真出分的 8 张**喂尺 ⇒ v4 判 **8/8 SHAPE_OK** ✓。
  v3 同批只判 2/8（其余 6 张被 `_to_t\d|t1o|t2c` 误当"多日面"⇒ 尺过宽），**正对照当场把尺挡下**，v4 改判序：
  逐对象命名标的优先于多日字样。
- 分布（prereg=95）：**SHAPE_OK 39** ／ `GATE_nav_or_cost_face` 22（净值/成本面，需重放引擎）・
  **`CRASH_panel_x_market` 10**（真形状对不上）・`UNRESOLVED` 13（需人读）・`GATE_dualarm_event` 7・
  `GATE_state_prob_face` 3・`GATE_intraday_face` 1。
- class × 形状（条件表，禁只读边际）：A 2 全 SHAPE_OK；A? 7＝SHAPE_OK 5＋双臂 2；
  **B 14＝CRASH 8＋双臂 4＋净值 2**（B 里没有一张形状 OK，与前任"B=待逐表面核"一致，但真因是形状不是核对）；
  C 46＝净值 20＋未决 13＋SHAPE_OK 13＋…；U 26＝SHAPE_OK 19＋CRASH 2＋状态概率 3＋日内 1＋双臂 1。
- 他闸计数（与形状正交）：`classify_index_only_vocab` 45・`per_face_review` 14・`composite_recipe_missing` 13・
  `no_binding_section` 12・`route:dual_arm` 7・`table_unregistered` 4・`normalization_undecided` 3・
  `replay_engine` 1・`signal_col_composite` 1。
- **10 张崩面具名**（本席实测崩 `calibration_exam.py:261` TypeError，按总包指令面记 blocked 待执行器形状预检上线）：
  L1-S0/02 货币卡・L1-S0/05 政策事件卡・L2-06-1/ablation/02・L2-06-3/calibration/02・L2-06-3/calibration/03・
  L2-06/ablation/02・L2-07-1/calibration/02・L2-07-1/calibration/03・L2-07/ablation/02・L2-08/calibration/02。
  ⇒ 比本席 §三之二 的"12 张"少 2：L2-07-1/ablation/03・L2-07/ablation/03・L2-07/comparison/03・L2-09/comparison/02
  四张其实走双臂路由（先判路由），另 L1-S0 两张属 U 面同形冲突。旧数不涂，以更正的尺为准。
- **39 张形状 OK 里"扣掉自动绑定层边界后"净 15 张**（只欠考工自家逐表面工序，不欠绑定册）：
  L2-01-2/02・L2-01-3/02・L3-01/comparison/04・L3-03-2/02・L3-03-2/03・L3-03/ablation/02・L3-04/02・L3-05/02・
  L3-07-2/ablation/02・L3-12-3/02・L3-12-3/03・L4-05/comparison/02・L9-A01/03・L9-A05/02・L9-A06/02。
- 两处本尺**禁用面**（如实标注，防 ⑩ 误读）：①`supply_gap` 列 v4 命中 0，与班次 05 在册"真断供 38 张"矛盾＝
  本尺断供解析谓词失效，断供判定仍按班次 05 那把尺；②形状账**只量考题面形状，不量信号能否物化**——
  净 15 张里 L9-A01/03（分钟已实现波动）就卡在日内供数，故 15 是形状面上限，逐张还要过信号供数与卡面口径两关。
- 未决 13 张具名移交（含班次 05 在册"等⑥多日标的三件齐"六张 A08/11/12/13/17-02/17-03 全数落在本桶，独立复算相符）：
  L0-02/03・L4-13/02・L4-14/02・L9-A08/02・L9-A11/02・L9-A12/02・L9-A13/02・L9-A17/02・L9-A17/03・
  L9-D1/ablation/03・L9-V1/02・L9-V2/02・L9-V3/02。

## 八之一、本班两把尺自犯并被当场挡下（06 本席实例；另起留旧案卷，前文不涂）

- v2 把 `primary` 与 `target_source` 拼成一串量形状 ⇒ 4 张"主目标市场级／辅写个股宽表"的自相矛盾卡被判成形状 OK；
  v3 拆串只量 primary，同时暴露 v3 的 `_to_t\d` 多日谓词过宽（正对照 2/8 证伪）⇒ v4 定序修正后 8/8。
- 自犯计数：本班尺迭代 3 版，其中 2 版被自家正对照否证。教训复证＝"命中数≠可考性"与"谓词过宽即假扩"（在册两条同名坑）。

## 八之二、P0 环境事件＝D 盘写满（06 本席实例，转⑩/运行班；发现于 20:2x）

- **D 盘写满**：`df -h` ⇒ D: 732G/732G・Avail **11M**・Use **100%**；第二把尺 `shutil.disk_usage('D:\\')` ⇒ free_GB **0.012**；
  写探针 2MiB 勉强通过。C: 余 17.26G／F: 余 1477.8G／G: 余 2357.5G（对照面，均非项目盘）。
- 已见后果（实测非推断）：`.runtime/audit/feature_flags.jsonl` 写入报 `[Errno 28] No space left on device`（census v3 首跑两条同签名）；
  项目库/git 对象/队列 blobs/分数册全在 D 面 ⇒ 下一笔入袋与传送带落地都暴露在 ENOSPC 下。
- 本席不代删（物理不可逆删除属 Owner 保留面，宪法 §5），只呈报并附对照读数。

## 八之三、本班交班终态实测（date 20:2x；袋面与未落地面如实在册）

- 本班入袋一只＝`q-20261015-st-qoder-p07-1015-06-0006`（两件活文档，files=2）**已判 dead**，死因原文＝
  `landing 异常: RuntimeError: git reset --hard refs/heads/dev -> rc=128: Updating files: 1% (388/21107) ... error: unable to write file data/databases/governance_metadata/audit_governance_ai_dual_editor_collaboration_policy.json`＝磁盘满 checkout 失败。 `[GATE-SELFDOC:GIT-DANGEROUS]`
- 同 sid 六袋全 dead 且死因分两族：0001/0003/0006＝reset --hard 写文件失败；0002＝`git read-tree ... index.lock write error. Out of diskspace`；
  0004/0005＝GATE-PRECOMMIT-RUN 阻断（门禁族，非磁盘）。⇒ 落地链对**任何**会话均已在 ENOSPC 下停摆，非本席袋特有。
- ⚑⚑ **分数册从未落 HEAD**：`git cat-file -e HEAD:docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml` ⇒
  `exists on disk, but not in 'HEAD'`（rc=128）；工作树面 `AM`（他席在途）。104 行全部门试次与今日 8 行只活在盘上，
  而 19:00 已有"5688 件 stash 扫走整馆"案卷在册 ⇒ 这是全线最高优先风险，转 ⑩/运行班，本席不代删不代 commit 他席面。
- 本席交付存证（防 stash/ENOSPC 双险）：`.runtime/sessions/st-qoder-p07-1015-06/staging/p07a06_ledger.md`
  bytes=118956・sha16=a50691d50ead57a4；`p07a06_checkpoint.md` bytes=26400・sha16=f0c0a9fb3922b836（与盘上现值同哈希）。
- claim 不放（在册"袋在飞禁放锁"改判：袋已死但交付未落地＝本席持锁等 ⑩ 定磁盘策后重投；两把 claim 实测持有者仍为本席 sid）。
- 盘面复测三把尺同框：`df -h /d`＝732G/732G・Avail 8.0M・100%；`shutil.disk_usage('D:/')`＝1.81MB（20:20）；写探针 2MiB 勉强通过。


---

# ⑦考工A 班次 02（起手 date 实测 2026-10-16 22:10:15；写册时点 22:4x；本班实测耗时见 §六）

## 一、防重入与取号（三实测，在册三证）

- 前任 `st-qoder-p07-1016-01` 心跳末行自证 `{"ts":"2026-10-16T10:58:02+00:00","pid":33584,"status":"exited","reason":"idle timeout","idle_seconds":1802.5}`（=本地 18:58:02）；台账内 10-16 零班次记录；`lock_files.py cleanup` 当次收走其一张死卡锁（entry_flow/L3/TDM-E-L3-04__calibration__02_解禁否决）⇒ 三证齐，本班取 1016-02。
- 前任留给本班的不是空白而是**两张 status=examining 的遗卡**（L3-03-2/03 温和放量・L3-05/02 连板顺位），卡锁已随其阵亡自然过期（`lock_files.py list` 现值两面 p07 命中 0）。
- 冷启动四查带 date 配对：Python 3.12.8／reaper `source=live`（last_run 22:10:28，scanned=38 killed=0）／锁清理完成／D 盘 free 95.640GB（上班 P0 事件"D 盘写满"已由运行面解除，实测复证）。
- 环境压力实测入册：`commit_pct 89.57%`・`cpu_pct 98.1%`（reaper watermark 同框读数）⇒ 本班刻意走零 CH 拉数的纯缓存路，不抢宽表装载。
- 心跳守护：`.runtime/tmp/p07/shift02_keeper.py`（自注册活 PID 后同进程进环，在册配方）→ pid **42116**，`heartbeat.jsonl` 首两行 `started`/`alive`；防误杀登记行已追加 `data/runtime/process_reaper_keep.txt`。

## 二、领面与卡池分母（磁盘面实测，活分母勿照抄）

entry_flow 卡面 402 件按 `^status:` 逐件读磁盘面：`preregistered 89／empty 133／blocked_on_data 69／examined 80→81／blocked_on_impl 29／examining 2→1`（加总自证 402；末列系本班烧尽一张后的位移）。本班未与在席撞车：两张 examining 遗卡之外，`lock_files.py list` 现值中 p03-1016-02 持 10 张 entry 卡、p07c-1016-02 持 L9-A06/02 并在册续出 rows[106]・rows[107]（股东户数集中度／解禁否决）——本席一律避开。

## 三、开考结果：1 张出分（verdict=fail），且本班把前任的假读数挡在册外

| rows | card_id | ic_mean | ic_ir | oos_ic | regime bull/bear | n | 触发柱 |
|---|---|---|---|---|---|---|---|
| 108 | L3-05/calibration/02_连板顺位 | −0.021138514060901243 | −0.4685837944310852 | −0.023220204276208363 | −0.023301743589087143 / −0.01753632645004816 | 1620 | ic_mean, ic_ir |

- 读数定性：三段同号为负（IS／OOS／牛熊）⇒ **卡面冻结式在本宇宙上方向反了**，不是"弱正不过地板"，是"顺位越高次日溢价越低"的反向读数；假设面（妖>龙>中军…正向单调）被否证。
- 分数册 only-add 三 sha 全序自证：`before=d2…`（108 行）→ `after`（109 行），`prefix_only_add=true`・`bytes_added=941`・`rows 108→109`（新行末 `card_id: TDM-E-L3-05/calibration/02_连板顺位`，`run_id=st-qoder-p07-1016-02`）；卡面由执行器自翻 `status=examined`＋lineage `run_id/score_row=rows[108]`。卡锁 acquire rc=0／release rc=0 同件留痕 `.runtime/tmp/p07/shift02_run.json`。
- 前置闸 G1-G4（⑦A 1015-06 在册自设数据充分性面，非门柱、未动 `pillars_numeric`）全过：`ic_days 1620／mean_names_per_day 4320.8／min_names_per_day 0／ic_std 0.045111／n_cells_signal 7,152,422`。`min_names_per_day=0` 已定性＝窗末日 target `shift(-1)` 全 NaN 所致（非样本洞，日均 4320.8 名）。
- 算力芯如实申报：**本班零 GPU**（纯 pandas 宽面板路，未 acquire 看门人，未设 `IC_DEVICE`）⇒ 本行不得被读成 GPU 读数。

**两枚把前任 dry 读数挡在册外的实测（另起留旧案，前任原文不涂）**

1. **量纲陷阱**（卡面 `data_window_evidence` 自己写明，前任没照做）：前任 `shift01_exam.py:sig_lianban` 用 `shift06_close`（＝后复权面）比 `stk_limit.limit_up`（不复权价）。本班探针 `shift02_face_probe.py` 以卡面在册证据当正/负对照实测：`shift06_close@2023-06-05` 封板家数 **3,882**（＝卡面警示的陷阱值，逐字命中）／`@2024-10-08` **4,594**；`shift06_d_close` 同日 **74／893**（与卡面证据 74／893 逐字同值）⇒ 判 `shift06_close`＝hfq 面、`shift06_d_close`＝卡面指定的不复权底座。本班按卡面 `signal_table: stk_limit × kline_daily` 用 d_close 重建连板高度。
2. **窗外预热被当判分面**：前任定义了 `trim()` 却未调用，判分面覆盖 parquet 全幅 2018-11-01..2025-09-09（1,666 日），而卡面 `window` 冻 `in_sample 2019-01-04..2023-12-31／oos 2024-01-01..2025-09-09` 且 `frozen_note: 窗口禁改`。⇒ 前任 n=1664 含冻结窗外 45 个交易日。本班做法＝预热段（2018-11 起）只用于连续涨停计数与 MA/涨幅计算，判分面 `in_window` 裁到卡面窗（n=1620，与 ⑦A 1015-06・⑦c 1016-01 同窗同量级）。
   两枚偏差合并的后果：前任 dry 为 `ic_mean +0.0048／ic_ir 0.052／n 1664`（弱正噪声），本班真面为 `−0.0211／−0.469／n 1620`（反向且过线失败）——**若照搬其 dry 入永久册，写的是一条错陈述**。旧案留此：`.runtime/tmp/p07/dry01_scores_L3-05__02_连板顺位.yaml` 与 `shift01_dry.json` 请 ⑩ 标废勿搬（本席不自删他会话件）。

## 四、不开考与转单（按工序5：口径未冻→不开考，不自拟）

- **L3-03-2/03 温和放量（本班接手后又放回，未开考）**：带界在卡面 `hypothesis` 是冻死的（温和 1.2-2.5／爆量 >4／缩量 <0.8），但 `signal_derivation` 写"signal=温和带命中二值 **与** vol_ratio 截面分位（爆量惩罚取负构造）"——"与"是相加、相乘、还是二值为主分位为辅，卡面两种读法都能自洽；⑦c 1016-01 在册已写"其带界与合成序仍需⑥/⑤认定"。前任 dry 用的是**裸 vol_ratio**（既非二值也非带惩罚合成分）＝第三种面，不属本题。⇒ 请 ⑥ 补合成式申报位或 ⑤ 认定读法；本席不自拍。卡面仍 `examining`（僵卡翻回权属 ⑩，本席不自清）。
- **L9-A15/02 资金费率拥挤跨市场预警**：式子细（8h 结算／60 日横截面分位加权均值／UTC 日聚合／NULL 显式剔除），但宇宙写作"主要币（BTC/ETH/SOL/XRP **等**流动性前档）"且"加权"权重源未闭 ⇒ 取哪几档币种＝考工自拟宇宙（宪法级"禁裸扩"同形）。转 ⑥ 闭宇宙申报位。
- **需 fresh CH 宽表的面**（本席班限内不可达，如实登记不做）：L3-03/ablation/02（technical_indicator `prox_short_score/prox_swing_score`）、L3-07-2/ablation/02（同表复合式＋`atr_14`）——⑦c 1016-01 实测同类宽列首拉 45.7 分钟，单班拉两列即吃满班限；sector 系 series 卡另受在册"代码轴 2021-08 前不可回测（known_data_gaps kline_sector_880_history_structural verification_20261015）"约束，且 ⑦c 已具名转单（卡面 signal 写的是响应式非 t 日 PIT 式）。

## 五、领面普查复量（一把尺自纠一次，旧句不涂）

- v1 谓词把 `signal_table` 括注说明（"kline_daily_hfq（个股层整手折算）"）当表名，判出 3 张"CACHE_SERVABLE"＝其中 2 张（L1-S0/02・L1-S0/05）正是 ⑦A 1015-06 在册点名崩 `calibration_exam.py:261` 的两张，且属无 `data_binding` 段的 U 面 ⇒ v2 摘括注＋要求表名可解析后，**3 张全数落入"卡面空绑定"假阳性**（signal_table/col 均为空串）⇒ 结论修正：entry 91 张 prereg（含本班烧尽前）里"本席缓存面可直接物化"的真数 **=0**，唯一一张已出分者来自遗卡复用。
- 分母自证：91 张 = CACHE_SERVABLE 3（后判假阳性）＋ composite 2＋ series 9＋ NEED_FRESH_TABLE 77。分母在动勿照抄。

## 六、本班实测耗时与分段账（date 配对，禁落笔即假）

起手 22:10:15（冷启动首条 date）→ 开考器落地 22:26:09..22:26:44（**35 秒**，纯缓存路）→ 身份探针 5.3 秒 → 普查两版约 2 分钟 → 写册起于 22:3x（date 实测 22:32:54 与本节 numstat 读数同框配对）。班限 60 分；全班实耗终值与收班时刻记于 §九（以 date 实测，不预估）。

## 七、[BLOCKER] 登记（逐枚，行首形态与本台账约定一致）

[BLOCKER] 2026-10-16|⑦A席1016-02|工具缺陷|run_card 只接 status=preregistered（calibration_exam.py:979），与占卡三步"②先翻 examining 再开考"结构性互斥：按工序翻完卡就考不了，只能靠 force 松状态闸接遗卡；前任 1016-01 即死在这一跳（shift01_real.json 两枚 _ToolError 原文在册）|scripts/backtest/fexam/calibration_exam.py:979 + .runtime/tmp/p07/shift01_real.json|请 ⑤/⑩ 二选一改写（工序面补"翻 examining 与开考须同卡锁内以 force 衔接"，或执行器面接 examining 态）；本席未动判据未动工序，两案都在册上|中
[BLOCKER] 2026-10-16|⑦A席1016-02|流程问题|班被运行面掐死后留下的 dry 读数无任何作废机制：前任两张 dry 件（踩卡面自载量纲陷阱＋含冻结窗外 45 日）至今活在 .runtime/tmp/p07/，下一班照搬即往永久分数册写错陈述；本班以卡面证据正/负对照实测挡下|docs/03_modules/_domain_backtest/exam_cards/entry_flow/L3/TDM-E-L3-05__calibration__02_连板顺位.yaml:56 + .runtime/tmp/p07/dry01_scores_L3-05__02_连板顺位.yaml|请 ⑩ 定"阵亡班 dry 件"处置（标废或收编为不可搬），本席不自删他会话件|高
[BLOCKER] 2026-10-16|⑦A席1016-02|判据缺失|L3-03-2/03 温和放量卡合成序未冻：带界已冻（1.2-2.5/>4/<0.8）而"温和带命中二值 与 vol_ratio 截面分位"的"与"有两种自洽读法，裸 vol_ratio 是第三种；执行＝考工自批口径|docs/03_modules/_domain_backtest/exam_cards/entry_flow/L3/TDM-E-L3-03-2__calibration__03_温和放量.yaml:53|转 ⑥ 补 signal 侧合成式申报位（或 ⑤ 认定读法）后本席下即可考；卡现悬 examining，翻回权属 ⑩|中
[BLOCKER] 2026-10-16|⑦A席1016-02|数据问题|entry 族 prereg 91 张里"本席已有缓存面可直接物化"实测=0；可考的下一张须 fresh 拉 technical_indicator 宽列（在册同类首拉 45.7 分/两列）或 sector 系（代码轴 2021-08 前不可回测＋卡面 signal 响应式待 ⑥）|.runtime/tmp/p07/shift02_census.py 读数 + src/zephyr/data/config/known_data_gaps.yaml:654(verification_20261015)|请 ⑩/总筹按本分母定本席节拍（与 ⑦c 1016-01 需Owner 枚同题，本席只复证分母不重复开单）；宽列预拉若由 ①/⑥ 做，本席单班可从 1 张升到多张|中
[BLOCKER] 2026-10-16|⑦A席1016-02|流程问题|分数册无跨席串行闸：盘上 108 行含 ⑦c-1016-02 在途未落地 2 行（HEAD=106），本班落 109 行后入袋必携带他席字节（袋=整档快照），本席只能以"diff HEAD 全为加、零删"自证不伤其内容|docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml（`git diff --numstat HEAD` 实跑读数 102/0，date 22:32:54 配对）|请 ⑩ 定共写面次序（先落者吃后落者／或分数册走单口串行入袋），本席未摘他人行未改他人字节|中

## 八、自检两轮（写册后跑，读数原样贴）

- 轮1 only-add 未动旧行：分数册 `git diff --numstat HEAD` 实跑读数＝**102 加／0 删**（HEAD 106 行→盘 109 行＝⑦c-1016-02 在途 2 行＋本席 1 行，零删即未伤任何旧行与他席行）；本席行 `grep -c "run_id: st-qoder-p07-1016-02"`＝1。
- 轮2 分数与门柱一致：卡面 `pillars_numeric` 冻 `ic_mean_min 0.02／ic_ir_min 0.3／regime_same_sign／oos_same_sign`；读数 ic_mean −0.0211（违 ic_floor）、ic_ir −0.469（违 IR）、regime 两段同负（同号柱过）、oos −0.0232 与 IS 同号（过）⇒ `fails` 恰为 ic_mean/ic_ir 两柱，`verdict=fail` 与门柱逐柱对表无出入；门柱与冻结窗零改动（`frozen_note` 原文未动，卡面 status/lineage 由执行器写）。

## 九、收班八件与终态（本段落袋即终核；三件必然后置的动作写明留痕面，不预写未发生之数）

1. **claim release**＝本段落袋后执行 `git_commit.py --release-only`，留痕面＝`lock_files.py list` 现值 p07 命中 0。
   本班占过的锁：L3-05/02 卡锁（acquire rc=0→release rc=0 已在开考器内成对完成）＋四件套与分数册 claim 四面。
2. **心跳注销**＝按 pid **42116** 核活后终止（在册红线：绝不按镜像名批杀），留痕面＝`heartbeat.jsonl` 末行 `status:"exited"`＋`.runtime/locks/heartbeat_st-qoder-p07-1016-02.pid` 复位。
3. **实耗**＝起手 date 22:10:15 → 写本段 date **22:36:44** 实测＝**26 分 29 秒**（本班在册面已齐：1 张出分＋5 枚 BLOCKER＋游标推进）。
   后置三动作（release／终止守护／tmp 自清）为秒级且不带分数面，其终值不预写；下班若需全班终值，以 `heartbeat.jsonl` 末行时戳减 22:10:15 实测，本席不预估。
4. **[BLOCKER]**＝§七 5 枚行首（高1／中4），行首谓词 `grep -c "^\[BLOCKER\] 2026-10-16|⑦A席1016-02"`＝5。
5. **自清收口**＝本班 tmp 件分层处置：`shift02_exam.py`・`shift02_census.py`（含 [TTL] task_bound 24h 头）留在 `.runtime/tmp/p07/` 供下班复用＝在册"复用件"惯例，非散落；`shift02_face_probe.py`・`shift02_register_backup.bin`・`shift02_run.json`・`shift02_ledger_section.md`・`shift02_ledger_close.md`・`commit_msg_1016_02.txt` 在本段落袋后当场删除，读数已全部抄进本节与 §三/§七；四件套外零散落；项目根零临时件。
6. **GPU 还牌**＝本班未 acquire 看门人（纯 pandas 路）⇒免执行，且本班分数行不申报为 GPU 读数。
7. **后台子任务**＝零 spawn 子代理⇒零孤儿。
8. **零 worktree**＝未调用任何工棚/工作树启动入口（TRAE-079 Phase 2 遵令）；`.aidrafts`／`.worktrees` 面本班 sid 命中 0。历史遗留 `.worktrees/st-*` 本席不清理，报 ⑩ 交清理专班（在册指令面）。

**下一班（⑦A 1016-03）首查四件**：①本袋是否落地只认 `git log` 与 blob 内容级；②分数册 HEAD 行数是否追平盘 109（⑦c 在途 2 行＋本席 1 行）；③⑥ 是否补 L3-03-2/03 合成式申报位与 L9-A15/02 币种宇宙；④L3-03-2/03 需 ⑩ 翻回 preregistered 后才可再领，勿当可考面重复占卡。

## 十、交班补记（写于本段落袋前，date 实测 22:40:48；补 §九 未含的队列真态与卡面完整性自证，并把 §九 的 tmp 删除清单**扩全**——§九 漏列 `shift02_keeper.py` 与本补记件，原文不涂，以本段清单为准）

- **本班袋态实测（勿按"已提交"当"已落地"）**：`q-20261016-st-qoder-p07-1016-02-0001` `state=pending`・`position_ahead=14`（22:38 首测 18→本班写册时 14，传送带在吃）；HEAD 侧分数册 `git show HEAD:…| grep -c "^- card_id:"`＝**106 行**（盘 109 行）⇒ 本班 1 行与 ⑦c 2 行仍在队列暴露面内，未进 HEAD。22:40:48 队首＝`q-20261016-st-docconsol-20261014-0007`（files=40，waiting **1683.6 秒**）・serializer lease 活（pid 47508・drain-active）・`daemon.online=false`。本班不抢租约不代排（在册红线），只把交付做成严格超集二袋随行走。
- **执行器整档重写卡面的完整性自证**（`run_card` 用 `yaml.safe_dump` 覆写冻结考题面，本班以 HEAD blob 与盘做内容级对拍）：语义仅 `status`（preregistered→examined）与 `lineage`（run_id/score_row 写入）两键变；`window`／`pillars_numeric`／`data_binding`／`hypothesis`／`target`／`buckets`／`pillars` **逐项全等**；锚点 `&id001` 与 `*id001` 未失；行数 56→69 系长串折行（difflib ratio 0.512 属行级重排噪声，内容级判据取 yaml 相等）。⇒ 门柱与冻结窗未被执行器洗坏，本席亦未动其一。
- **本班未做面（自带承重证据，非省力）**：①需 fresh CH 宽列的 2 张（L3-03/ablation/02・L3-07-2/ablation/02，technical_indicator 宽列在册首拉 45.7 分/两列＞本班剩余班时（写本段 22:40:48，班限 60 分自 22:10:15 起）且单卡>15 分须终止）；②双臂 7／净值 22／日内 1／状态概率 3 面（⑦A 1015-06 四族形状账在册＝非现器可考）；③崩面 10 张（执行器形状预检上线前记 blocked，指令面）；④sector 系 series 卡（⑦c 在册：卡面 signal 为响应式非 t 日 PIT 式，待 ⑥ 补申报位）。
- **后置三件执行声明**（本段落袋后立即执行，留痕面下班可复量）：①`git_commit.py --release-only` 放本班四面 claim；②心跳守护按 pid **42116** 核活终止（绝不按镜像名批杀）；③`.runtime/tmp/p07/` 本班件删除清单＝`shift02_keeper.py`・`shift02_face_probe.py`・`shift02_register_backup.bin`・`shift02_run.json`・`shift02_ledger_section.md`・`shift02_ledger_close.md`・`commit_msg_1016_02.txt`（读数已全部入本节与 §三/§六/§七），保留复用件＝`shift02_exam.py`・`shift02_census.py`（[TTL] task_bound 24h）。
- **⚑ 交 ⑩ 两枚需人动作**：(a) L3-03-2/03 悬 `examining` 需 ⑩ 翻回（翻回权属 ⑩，本席不自清）；(b) 前任两枚 `dry01_scores_*.yaml` 建议标废（其面踩卡面自载量纲陷阱＋含冻结窗外 45 日，照搬即写错陈述）。

## 十一、二袋入队时撞出的一枚形态（当场登记并自纠初判，date 实测 22:42:37 提交・22:4x 读码）

- **stdout 原文两行**：`[compaction] docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml 合并前递失败: … ours 侧 yaml.compose 解析失败: expected a single document in the stream … line 8, column 1: --- ——拒绝压缩`・
  `[compaction] qid=q-20261016-st-qoder-p07-1016-02-0001 共享注册表路径不可信合并——拒绝压缩，两袋保留`。
- **本班初判与读码自纠（旧句留此不涂）**：本段首版把该形态写成"工具缺陷・中（compaction 用单文档谓词）"。
  读码后**推翻自己的定性**：`scripts/commit_queue.py:8` INVARIANTS 逐字在册＝"注册表族共享路径例外：顶替前身份集纯加法合并前递，
  **不可信合并拒绝压缩两袋保留**——W-CASE st-zcloseout-20260928 lost-update 治本"，且 `scripts/commit_queue.py:695` 调
  `three_way(...)`、`:746` 注释"两袋都保留交落地侧三向合并理顺" ⇒ **拒压保留是设计行为，不是故障**。初判作废，以本段为准。
- **仍然成立的一枚真风险（机制读数，未落地实证，勿当已发生事故报）**：条目级合并器与 compaction 用的是同一个解析口
  `scripts/governance/commit_queue_landing.py:486`（`yaml.compose` 解析失败即返 conflict）。分数册自 裁定#536 起是**双文档**
  （`doc_type: register` 头＋`---`＋含 rows 的本体），`run_card` 侧已按 `yaml.safe_load_all` 兼容（calibration_exam.py:1096-1099），
  合并器侧未兼容。落地快路径 `commit_queue_landing.py:1181` 注"base==ours 字节相等（dev 相对快照基底零漂移）→ 整文件取 theirs"可绕过 compose，
  但该快路径只在"dev 相对袋基底零漂移"时成立 ⇒ **同 sid 的后袋**（基底 106 行、落地时 dev 已含前袋 109 行）大概率走条目级合并
  ⇒ 在本册上有以"解析失败"判 dead 暴露。本班两袋（0001/0002）即此形态，如实登记不催授权、不预支结论。
- **本班自处**：不 requeue 不摘袋（在册红线）；二袋为一袋的严格超集（分数册与卡字节全等，仅 ledger.md 增长）；
  三袋（含本节）入队后**停手不再追加**，避免同件袋链线性增长。下班首查＝`commit_queue.py status --session st-qoder-p07-1016-02`
  与 `git show HEAD:docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml | grep -c "^- card_id:"`（应 106→109）；
  若后袋以 `dead_reason=…解析失败` 判死，按在册"先读 dead_reason 对症修因再投"处置，非盲重投。

[BLOCKER] 2026-10-16|⑦A席1016-02|工具缺陷|分数册自裁定#536 为双文档 register 形态，而队列条目级合并器解析口 yaml.compose 只认单文档（commit_queue_landing.py:486）；执行器 run_card 已按 safe_load_all 兼容（calibration_exam.py:1096-1099），合并器未同改 ⇒ 同件同册的后袋在 dev 已漂移时走条目级合并，有以"ours 侧 yaml.compose 解析失败"判 dead 的暴露（compaction 侧"拒绝压缩两袋保留"系在册设计非故障，本班初判已自纠）|scripts/governance/commit_queue_landing.py:486 ＋ scripts/commit_queue.py:8/695/746 ＋ 本班 22:42:37 stdout 两行原文|请 ⑤/队列班把合并器解析口改 safe_load_all 逐 doc（与 run_card 同源），修前考工各班只能靠严格超集袋自保；本席未落地实证，此为机制读数勿引成事故|中

- **对 §九 第 4 行的当场更正（旧行不涂）**：那里写的行首谓词读数 5 枚＝写该段时点（22:36:44）真值；本段 §十一 追加第 6 枚后现测＝`grep -c "^\[BLOCKER\] 2026-10-16|⑦A席1016-02"` 读数 **6**（严式实跑于本日 22:4x）。此即在册"追加型台账里的计数自述落笔即假"坑复证：计数只在写它的那一行有效，下班一律现测。

## 十二、对 §十 第 8 行的当场更正（旧行不涂；实测时点 date 22:48:40 配对）

- §十 写"`.aidrafts`／`.worktrees` 面本班 sid 命中 0"——**该句已错**。复量实测：
  `.aidrafts/st-qoder-p07-1016-02` **存在**＝397MB／22,763 个文件（`du -sh`＋`find -type f | wc -l`），
  `git worktree list` 全表 54 条（含各席 aidrafts 与 serializer 工棚 w3・`.worktrees/st-mtrain-1016`・`st-rulemap-20261014` 等）。
- **归属与成因**（不改判只定性）：该影子树非本席调用任何工棚/工作树入口所建——本席全程在主区作业，
  TRAE-079 Phase 2 禁建令面未破。它系**会话注册动作由工具自动派生**（在册已立案形态＝"会话一注册工具自动建
  `.aidrafts/<sid>` 整树 worktree＋30s 心跳守护；与禁建 worktree 令面冲突，勿自删"）。
  同因还有第二枚心跳写手：本班自起守护 pid **42116**（已于 22:47:4x 按 PID `taskkill //F` 终止并复证不活），
  而 `heartbeat.jsonl` 末行写手是 **pid 26828**（python.exe，工具侧守护，仍活）——本席不杀非自己名下的进程（在册红线：
  按镜像名批杀曾扫掉他班心跳守护与在途提交），其收尾形态按 1016-01 实例复证＝空闲 1800 秒后自写 `status:"exited"`。
- **本班收班第 8 项改判**：从"零 worktree 成立"改为**"本席零主动建树；工具自动影子树 1 枚在盘（397MB）待清理专班／⑩ 处置"**，
  并交 ⑩ 一枚需人动作：TRAE-079 Phase 2 的"禁建 worktree"与工具侧"注册即建整树"两条指令面互斥，
  需 ⑩/⑤ 定策（本席不自删，删属物理不可逆面且该树由工具生命周期持有）。
- **收班第 2 项补记**：`.runtime/locks/heartbeat_st-qoder-p07-1016-02.pid` 现存（5 字节・mtime 22:38・内容＝**26828**＝工具侧守护，
  现测仍活），本席自起的 42116 不在此文件面上且已终止 ⇒ 心跳末行现显 `alive`（写手＝26828）：
  下班对账勿把该 `alive` 读成"⑦A 1016-02 仍在值守"，本席班已于 22:4x 收完；该守护是否随会话终止而自写 `exited`，
  按 1016-01 实例（idle 1800 秒自写 exited）为最可能形态，本席不代杀非自己名下进程。
- ⚑ 本班"三袋后停手不再追加"自设线被本更正破例：更正不入册＝把已知的假陈述留在永久活文档里，代价高于多一袋。
  第四袋仍按在册配方做成三面严格超集，此后本席当班不再追加。

[BLOCKER] 2026-10-16|⑦A席1016-02|流程问题|TRAE-079 Phase 2"禁建 worktree"与工具侧"会话注册即自动建 .aidrafts/<sid> 整树"两指令面互斥：本席全程未调用任何工棚入口仍在盘上留下 397MB/22,763 件影子树，收班第 8 项无法按字面达成|.aidrafts/st-qoder-p07-1016-02（du -sh 397M・find -type f 计数 22,763・date 22:48 配对）＋git worktree list 全表 54 条|请 ⑩/⑤ 定策（收编为"注册面副作用不计入禁建令"或让工具侧改为按需建）；本席不自删（物理不可逆面且树由工具生命周期持有），历史遗留 .worktrees/st-* 同口径报 ⑩ 交清理专班|中

- **本班收尾读数（现测于 2026-10-16 22:50:15，勿沿用到下班）**：严式 `[BLOCKER] 2026-10-16|⑦A席1016-02` 行首计数＝**7**（§七 5＋§十一 1＋§十二 1）；台账行数＝1078；分数册盘 109 行／HEAD 仍 106 行（本班四袋全在队列，落地以 `git log` 与 blob 为准）。


---

# ⑦考工A 班次 03（起手 date 实测 2026-10-16 23:10:12；写册时点见 §六 现测；实耗见 §六）

## 一、冷启动与防重入（取号三证）

- 1c 禁建 worktree（TRAE-079 Phase 2）＝本班零工棚/工作树入口调用；历史遗留 `.worktrees/st-*` 未碰（按令报 ⑩ 交清理专班）。会话一注册工具自动建的 `.aidrafts/st-qoder-p07-1016-03` 影子树系工具生命周期持有，本席不自删（1016-02 §十二 同题在册，本班不重复立案）。
- 四步读数：python 3.12.8・`lock_files.py cleanup`＝收 6 把死锁（p08 ledger/checkpoint・p09 ledger/checkpoint・iteration_history・pulse/independent_signals）＋SALVAGED `st-infoaxis-20261013`（merge=skipped・stash=0件・释放claim=0+.ailocks/31.registry）・`process_reaper --status`＝`source=live`・scanned=28・killed=0・reported=21・`commit_pct=75.78`・degraded=False・stash_count=27・worktree_changes=1432・dead_archive rc=1（首段＝全量模式警告，次段＝serializer 租约 pid=47508 存活拒并行，均非本班动作）。
- 取号：游标末班＝1016-02（其 §九~§十二 有终核读数 date 22:50:15＝已收班）；台账 10-16 面上已有 01（阵亡未写册）与 02 两段 ⇒ 本班取 **1016-03**。会话身份＝`SessionRegistry.open_session('st-qoder-p07-1016-03')` 落盘 pid=0・`logical` 被降级 False（chief-form verification failed＝既有形态非本班事故）；守护按在册配方独立后台起（heartbeat_daemon 30 秒环），收班②按 PID 核活终止。

## 二、本班头号产出＝推翻在册"装载面是本席瓶颈"这枚节拍依据（承重）

在册原文两处＝`checkpoint.md:21-22`"下一张可考须 fresh 拉 technical_indicator 宽列（在册同类首拉 45.7 分/两列，单班即吃满）"＋`ledger.md:987`"⑦c 1016-01 实测同类宽列首拉 45.7 分钟，单班拉两列即吃满班限"。本班同口（`scripts/backtest/fexam/ch_data.load_panel`）逐列现测（date 23:2x 配对，窗 2021-01-04..2025-09-09，除注外）：

| 表.列 | 形状（日×票） | 秒 |
|---|---|---|
| c1_market.kline_daily_hfq.close（窗 2019-01-04..2025-09-09） | 1622×5642 | 16.2 |
| c1_market.money_flow.main_net_inflow_pct | 1137×5535 | 13.6 |
| c1_market.kline_daily_hfq.open | 1137×5616 | 12.2 |
| c1_market.technical_indicator.chips_winner | 1137×5614 | 62.4 |

⇒ 单列全市场宽面板＝**12–62 秒**，上表四列合计 104.4 秒。"45.7 分/两列"在现器现窗**不复现**（该读数系 ⑦c 1016-01 袋内自述，含首拉窗＋缓存写盘＋其班内重试，非纯 `load_panel` 计时；本席不据此翻案其研究结论，只翻"装载吃满单班"这一条被下游当承重用的依据）。
判语＝本班 0 出分的约束**不在装载面**，在卡面口径与执行器形状/解析面（§三、§四）。请 ⑩/总筹据此重估"宽列预拉须由 ①/⑥ 做"的呈批依据（本席不代裁节拍）。

## 三、开考实测＝本班唯一"表在位＋窗覆盖＋合成式冻死"的 panel 卡被执行器解析面挡在出分前

锚卡 `TDM-E-L9-A06/calibration/02_主力净流入截面`（signal_kind=panel・`oos_window_ref`=[2024-01-02, 2025-09-09] 在册・pillars_numeric 四柱＋两同号柱・universe_rule 顶键缺席）：

- 占卡三步：`lock_files.py acquire <卡> st-qoder-p07-1016-03` **rc=0**（同件 release **rc=0**，全程零撞车）；卡面**未手工翻 examining**（在册工具缺陷枚 1016-02 §七 枚1：`run_card` 只接 preregistered，`calibration_exam.py:979`），本班采"锁内直跑、由执行器自翻 examined"绕行，`force` 旗未用。
- 出分前崩点（原文）＝`DateParseError: Unknown datetime string format, unable to parse: 2019-2021H1 牛段 money_flow 无数据（起 2021-01-04）⇒ 本卡 regime 用熊/修复两段替代， 已如实声明不冒用统一牛熊串`。消费位＝`scripts/backtest/fexam/calibration_exam.py:255`（`_panel_metrics` 里 `for name, span in regimes.items(): ic[_in_spans(...)]`）→ `:87-93 _in_spans` → `_span_pairs` 把无日期散文条目整串当时点。
- 副作用三面查零（现测）＝`git status --porcelain <卡>` 空・卡面 status 复测 `preregistered`・分数册 `git diff --numstat HEAD` 该件空（本班零分数行）。
- 不开考理由＝执行器表示层解析面，**非判据非门柱**；改面权属 ⑤（执行器跳过不可解析条目并记"该 regime 柱未评估"）或 ⑥（卡件属主把声明位移出 `regimes` 字典）。本班未动判据、未动卡面字节、未动工序文本（在册铁律：改 regimes 表示层须卡件属主署名，接班不单方面动）。
- 同卡坐实在册数据面复证（本班现测谓词写明）＝`c1_market.money_flow` 窗内 5,509,521 行中 `pct_change!=0`＝**0**・`close!=0`＝**0**，而 `main_net_inflow_pct!=0`＝5,495,405（99.7% 活）⇒ 卡面 MUST 条款"残差化须剔当日涨幅"若按本表列构造即**空操作**（考的是原始资金流＝动量共线面）。本班据卡面 `target_source` 自载价格面（`kline_daily_hfq close`）构造涨幅腿与 20 日动量腿（未自创新口径），未落册。与 10-15 前席"恒 0"同签名＝**复证非新案**，处置在 ①（表为真源）。

## 四、领面分母与新死族面积（三把尺同框，谓词写明勿混用）

- 磁盘面分母（date 23:2x 现测）＝entry_flow `^status: preregistered` **91**（与 1016-02 收班读数同值＝本班值守内上游零翻卡）。
- 真源尺＝`card_binding.py --mode classify --cards-dir <绝对路径>`＝**A2／A?7／B14／C42／D0／U26**，加总 91 自证（件 `.runtime/tmp/p07/shift03_classify.yaml`）。按 1015-06 在册纠偏，C/B 是**自动绑定层边界**非"考工不能考"，故本班另起两把自家尺。
- 形状×regime 联合尺（谓词＝`signal_kind` 与 `window.regimes` 逐 value 调 `_in_spans`）＝panel 91 面里 regime 可解析 **29**／散文崩 **4**；series 面里崩 **3**。合＝**91 张里 7 张恒不可判**（panel 4／series 3），具名与坏键＝`.runtime/tmp/p07/shift03_regime_deadface.yaml`：L3-11-1/03`single_state`・L3-11-2/03`single_state`・L9-A06/02`bull_note`・L9-A11/02`bull_note`・L9-A15/02`bull_note`・L9-A15/03`unavailable`・L9-V3/02`bull_note`。
  ⚑ 与 ⑦c 1016-02 的"39/14"是**两把不同尺**（其尺＝全族含 str 型 regimes 的普查），本席尺只量 entry preregistered 且只对 dict 型条目逐键试解析；本席相对 05 班在册的 5 枚**新增两枚具名**（L3-11-1/03・L3-11-2/03，坏键 `single_state`，系 10-16 新翻出的同族形态）。
- 29 张 panel 可解析面逐族分账＝12 张标的为 CSI300 指数次日面（个股/板块截面信号 × 市场级目标，执行器 panel 路形状不配，按总包 10-15 指令面记 blocked 勿硬啃）；sector 系按在册"卡面 signal 写响应式非 t 日 PIT 式"待 ⑥（⑦c 1016-01/02 在册，本席复证不自新）；tick/1min 供数堵（L4-03・L4-11・L9-A01/03）；双臂/合成分支待 ⑤（L3-07-2/02・L2-01/02・L2-01/03，04 班逐张判死在册）。
- 事件路实测判废（本班读码，非推测）＝`calibration_exam.py:803-830 _event_metrics(signal: Series, target: Series, card)` 取的是**市场级日频事件开关面**（事件日 vs 非事件日次日收益 gap），而 L9-A05/02・L9-A13/02・L9-A17/02 三张事件卡冻结的 pillars 是**个股 CAR**（car_t0_t20_min_bp／car_q5_q1_gap_min_bp／car_t_stat_min，须逐票 [-210,-11] 市场模型 beta 回归）⇒ `judge_event:841-843` 对未知键 fail-closed 直写"未支持判据键"判 fail。本班**不产出该形态分数行**——把"执行器无该柱"写成永久册上的 fail＝1016-02 在册枚"往分数册写错陈述"同型，转 ⑤ 补柱。

## 五、本班 0 张入册与保底条款如实呈报

- 分数册本班零字节＝盘 110 行／HEAD 110 行／`git diff --numstat HEAD` 该件空・本班 run_id 零行。本班不搬 1016-02 的行（其行已随 ⑧B 袋落 HEAD，本班 §六之四实测）。
- 保底"每班≥8 张出分或跑满 4 小时"＝未达：本班可算窗 23:10→01:00（CH 窗禁跑，剩 108 分），且 entry 面真可考 0 张；同题 ⑦c 1016-01 已立"需Owner"枚，本班**只复证分母不重复开单**。

## 六、本班实测耗时与分段账（date 配对）

起手 23:10:12 → 首查四件＋冷启动 8 分 → 领面普查（classify＋形状×regime 联合尺＋panel/series 族账）20 分 → 装载纠偏四列现测 5 分 → 锚卡开考未遂（含占卡锁与三面副作用核查）12 分 → 事件路读码判废 6 分 → 写册＋推游标＋入袋＋收班＝以 §九 收班读数为准（勿在此预写终值）。

## 七、[BLOCKER] 登记（逐枚当场追加）

[BLOCKER] 2026-10-16|⑦A席1016-03|工具缺陷|执行器 panel/series/event 路把 window.regimes 每个条目无条件送 _in_spans，卡面含散文声明位即在出分前抛 DateParseError 使整卡恒不可判；本班具名 7 张（panel4/series3，含 05 班在册之外的 L3-11-1/03・L3-11-2/03 坏键 single_state）|scripts/backtest/fexam/calibration_exam.py:255＋:87-93＋.runtime/tmp/p07/shift03_regime_deadface.yaml＋本班实跑读数 .runtime/tmp/p07/shift03_run.json|请 ⑤ 把不可解析条目改为跳过并显式记"该 regime 柱未评估"（勿顺手放宽 regime_same_sign 判据），或请 ⑥ 把声明位移出 regimes 字典并署名；本席未动判据未动卡面|高
[BLOCKER] 2026-10-16|⑦A席1016-03|判据缺失|91 张 preregistered 卡的 regimes 形状不兼容在卡面冻结前无任何在册门暴露（classify 尺不读 regimes 形状、卡册计数不跑判官），唯一发现路径＝考工在出分前撞崩或做零 CH 预演|尺＝.runtime/tmp/p07/shift03_regime_deadface.yaml（谓词写明）＋10-13 案卷"22 张"同族先例|请 ⑥ 出题侧加"regimes 每条须可解析为日期段"自检位、⑤ 加机生门；修前本席每班须先跑该尺再领面（本班已跑，7 张不入领面）|中
[BLOCKER] 2026-10-16|⑦A席1016-03|数据问题|c1_market.money_flow 窗内 5,509,521 行中 pct_change!=0＝0 且 close!=0＝0（main_net_inflow_pct 非零 5,495,405）⇒卡面 L9-A06/02 MUST"剔当日涨幅残差化"按本表列构造即空操作|现测 SQL 读数见本段＋台账 §三；与 10-15 前席"恒 0"同签名（复证非新案）|请 ① 复测该表两列并改行（表为真源）；本席按卡面 target_source 自载 hfq close 面构造涨幅腿，未自创口径、未落册|中
[BLOCKER] 2026-10-16|⑦A席1016-03|流程问题|本席活文档在 HEAD 侧大面积未落地：ledger.md 盘 1080 行 vs HEAD 583 行（diff HEAD＝+497/−0）、checkpoint.md 盘 252 行 vs HEAD 107 行（+145/−0），班次 1015-06 与 1016-02 两班正文从未进 HEAD（`git show HEAD:<ledger> | grep -c "⑦A席1016-02"`＝0）；上一班四袋全死系分数册双侧皆改连带本席两件|`git diff --numstat HEAD -- <两件>` 现测读数＋队列四袋 dead_reason（"非注册表族件双侧皆改真冲突: exam_scores_v1.yaml"）|本班把两件按纯追加装进自家袋随行走（零删自证），分数册本班无新行故不入袋以免再次连坐；请 ⑩ 定"共写热册连坐挡住单写面交付"的收编序|高
[BLOCKER] 2026-10-16|⑦A席1016-03|工具缺陷|run_card 状态闸（只接 preregistered）与占卡三步"先翻 examining 再开考"仍互斥（1016-02 §七 枚1 在册复证，本班未见修面落地）|scripts/backtest/fexam/calibration_exam.py:979|请 ⑤/⑩ 在工序文本与执行器面二选一收敛；本班绕行＝锁内直跑、不预翻态、不用 force，未动工序文本|低
[BLOCKER] 2026-10-16|⑦A席1016-03|流程问题|本班推翻在册节拍依据＝"宽列首拉 45.7 分/两列⇒单班吃满"现测不复现（load_panel 逐列 12–62 秒）；据此前写的"下一班不可达须由 ①/⑥ 预拉"与 ⑩ 节拍呈批面失去承重|台账 §二 四行现测表＋checkpoint.md:21-22・ledger.md:987 原文锚|请 ⑩ 用新读数重估本席节拍与"保底≥8 张或 4 小时"条款（后者与 60 分班限＋CH 窗 01:00-04:00 禁跑互斥＝⑦c 1016-01 需Owner 枚同题，本班不重复开单）；本席不自改班限|中

## 八、收班段（date 实测 23:51:13 写入，正文内所有读数皆为本次现测）

- **耗时终值**＝起手 23:10:12 → 本段 23:51:13＝**41 分钟**；分账＝例行（冷启动＋首查＋领面三把尺＋装载现测＋锚卡开考未遂＋写册推游标）约 37 分，返工 4 分＝首投 23:41 被门拦一次（本段 §九 枚2），加 `[docs-only]` 申报后 23:45:34 重投成功。
- **对 §一 的当场更正（旧句不涂）**＝那里写的"收班②按 PID 核活终止守护"系开班时计划；本班实据＝袋 q-20261016-st-qoder-p07-1016-03-0001〔pending，ahead=4〕 在写入时点仍 pending，而在册条令"袋在飞禁放锁／禁停心跳（此刻 release-all＋停 keeper＝在飞袋集体死信）"优先⇒本班**不放写册两件 claim、不停守护**，改由下一班在袋落地后收。此对偶已另立 [BLOCKER]（本段枚1），本席不自造豁免。
- **袋态现测**＝q-20261016-st-qoder-p07-1016-03-0001〔pending，ahead=4〕；本段随同件链后袋投出（后袋＝前袋严格超集，纯追加零删），本班交付不系于单袋。
- **claim/卡锁现测**＝唯一卡锁（L9-A06/02）acquire rc=0→finally release rc=0（shift03_run.json 留痕）；`lock_files.py list` 命本班两件活文档＝(list 面本班零命中)。
- **心跳现测**＝pid 文件内容＝文件缺席；jsonl 末行＝{"ts": "2026-10-16T15:51:06.554984+00:00", "pid": 9520, "status": "alive"}（首起守护 23:23:53 自写 `exited/session not in registry`＝在册"pid=0 条目被外来摘除"形态复证；本班同串复注册 readback pid=0・held_files 被 register 语义整体重建为 0＋独立后台复起 30 秒环守护，日志 shift03_keeper.log）。
- **零 worktree（收班⑧）**＝本班未调用任何工棚/工作树入口；`git worktree list` 现测 70 条（本班零新增）；`.aidrafts/st-qoder-p07-1016-03` 存在性＝True＝会话注册的工具侧副作用，与前班在册"禁建令与工具自动建树互斥"同题，本班不重复开单、不自删。
- **主区根零临时件（收班⑤）**＝`git status --porcelain` 根级条目 2 条： M .gitignore／ M echo-guard.yml；本班 tmp 件全部在 `.runtime/tmp/p07/`（24h TTL）＝shift03_exam.py／shift03_classify.yaml／shift03_regime_deadface.yaml／shift03_run.json／shift03_append.py／shift03_closeout.py／shift03_cursor_body.md／shift03_msg.txt／shift03_keeper.log；本班零删除件（零分数册写入故无回退备份；上一班 `dry01_scores_*` 两件系他会话件面，本席不自删，已在 1016-02 §七 枚2 立案请 ⑩ 标废）。
- **GPU（收班⑥）**＝本班未 acquire 看门人（零 ic 类实跑）⇒免执行并如实申报；本班零分数行，不申报任何设备读数。
- **子代理（收班⑦）**＝零 spawn⇒零孤儿；本班自起后台仅心跳守护一支（状态见上条现测）。
- **分数册一致性（收班自检轮2）**＝本班零分数行：`git diff --numstat HEAD -- <分数册>` 现测＝(该件 diff HEAD 空)（盘 110 行＝HEAD 110 行）⇒"分数与门柱一致"无可比对象，如实记不适用；本班未搬 1016-02 的行（其行已随 ⑧B 袋落 HEAD，本班实测）。

## 九、[BLOCKER] 追加两枚（收班段现测；§七 六枚不涂）

[BLOCKER] 2026-10-16|⑦A席1016-03|流程问题|收班①②（release 全部 claim＋注销心跳）与在册"袋在飞禁放锁禁停心跳（此刻 release-all＋停 keeper＝在飞袋集体死信，10-10 认可条目）"互斥：本班袋 q-20261016-st-qoder-p07-1016-03-0001〔pending，ahead=4〕 写入时点仍 pending，本席按后者执行＝不放写册两件 claim、不停守护，留交下一班落地后收；恒定班每班都撞此对偶，非本班省力|本席 1015-04 台账 §堵点①⑦复证＋本班 §八 现测（daemon online=false）|请 ⑩ 定"在飞袋未落地即交班"的合法收班形态（或让队列 daemon 在线以即时落地）；本席不自造豁免|中
[BLOCKER] 2026-10-16|⑦A席1016-03|工具缺陷|纯文档袋（本席台账＋游标两件，袋内零代码件）在正门预检被 MESSAGE-CLAIMS-CODE-BAG-EMPTY 拦一次，原因＝消息按考工纪律引用 `.runtime/tmp/p07/shift03_*` 案卷证据指针即被当"声称代码件"；本席走门自己在册通道（加 [docs-only] 显式申报）而非弱化门|本班 23:41:02 与 23:45:41 两次 stdout 原文（拦信行 CLAIM-CHECK-BLOCKED: MESSAGE-CLAIMS-CODE-BAG-EMPTY）|请 ⑤ 把判据从"消息含 .yaml/.py 路径字串"改判"消息是否声称袋内含该件"（考工各班消息必引案卷件，此闸对纯文档袋＝恒拦面）；本席未动门|低

## 十、结构自证与写后核账

写册器＝`.runtime/tmp/p07/shift03_closeout.py`（单次 CAS 尾追加，禁整档覆写）；全部自证读数现算后落盘 `.runtime/tmp/p07/shift03_closeout_stats.json`（含 prefix_strict／行数／本班 [BLOCKER] 行首计数／他会话旧段是否仍在／worktree 条数／袋态）。本段正文不预写任何"共 N 枚／末袋 X／实耗 M 分"式终值之外的计数——凡写皆为同一脚本内现测。

## 十一、对 §八 两条的当场更正（旧句不涂；两时点并列现测，date 配对）

- **更正 §八"本班不放写册两件 claim"＝claim 已被外力摘除，本班随后复 claim**。两时点现测＝①23:51:13（§八 写入）与 23:53:20 复测＝`lock_files.py list` 命本席两件路径 **0** 条（当时 14 把锁全部系 st-qoder-p03-1016-04 名下 entry_flow comparison 卡），脱落旁证＝网关 23:45:34 自报 `ENQUEUE-RENEW: claim 续租 0/2 件（ttl=7200s）`（门侧已认不到本席 claim）＋本席首起守护 23:23:53 即被 `session not in registry` 摘除（§八 心跳条），形态归在册"新鲜窗外锁被判死清理"同族；②本班按"改前 claim"铁律于 23:54:46 重新 acquire 两件 rc=0，现测＝`17` 把锁、持有者集合=['st-qoder-p01-1016-04', 'st-qoder-p03-1016-04', 'st-qoder-p07-1016-03']、本席命中 **2** 条。⇒§八 那句"不放 claim"在写入时点属实、在 23:53 被外力改成"已脱落"，本席不假装自主 release，也不把复 claim 说成从未中断。
- **更正 §八 心跳条的 pid 依据＝三态不齐但归属已双证**：`.runtime/locks/heartbeat_st-qoder-p07-1016-03.pid` 现测存在性＝False（文件缺席），而 `heartbeat.jsonl` 末行现测＝`{"ts": "2026-10-16T15:56:06.868941+00:00", "pid": 9520, "status": "alive"}`；进程归属已按 PID 用 cmdline 验讫＝`...rule_bridge.heartbeat_daemon st-qoder-p07-1016-03 D:/ZephyrAlpha 30`（在册红线：判活须 cmdline 验证，禁按镜像名认人，亦禁把 pid 文件缺席读成守护亡）⇒本班继续不停该守护（袋在飞条令），下一班在袋 0001/0002 落地后按该 PID 核 cmdline 再终止。
- **本段自身的改写披露（不作旧案卷留存的理由）**＝本节初稿曾编号"## 十二、"，把"复 claim 后现测命中 2 条"误嵌进"claim 已脱落"的判语句、且 §十一 编号缺位；初稿从未进入任何袋（本班袋 0001 快照 23:45:34 止于 §七），盘面即唯一副本，故本席原地改写并把改写理由写在这里，而非另起一节留下可被下游误引的假陈述。前文 §一~§十 以逐字节相等自证（脚本断言 `head_prefix_equal`，读数落 `.runtime/tmp/p07/shift03_fix2_stats.json`）。

## 十二、对 §十一 心跳条的当场补记（旧句不涂；date 实测 00:02:26）

§十一 写"守护归属已按 PID cmdline 验讫＝pid 9520"——**不完整**。复测（谓词写明＝`Get-CimInstance Win32_Process -Filter "Name='python.exe'"` 再按 cmdline 含本席 sid 过滤，**必须带 Name 过滤**：不加时查询进程自身会被匹配进来，实测给出 9 支假数）＝本席名下现存活守护 **两支**＝`9520,36824`（9520＝本班 23:48 自起；36824＝23:57 由工具/网关侧派生）。心跳 jsonl 末三行现测＝`{"ts": "2026-10-16T16:03:37.255370+00:00", "pid": 9520, "status": "alive"}`／`{"ts": "2026-10-16T16:03:17.595934+00:00", "pid": 36824, "status": "alive"}`／`{"ts": "2026-10-16T16:03:07.240422+00:00", "pid": 9520, "status": "alive"}` ⇒ 写手在两支之间轮转（23:54 末行＝9520，00:00 末行＝36824）。

下班收守护的正解＝**按 cmdline 枚举本席 sid 的全部 PID 后逐个终止**（在册红线：禁按镜像名批杀，曾扫掉他班守护与在途提交；亦禁只杀账面那支＝留下一支继续写"说谎心跳"，与 ⑪席 1016 班"心跳双生待按 PID 双杀"同形态复证）。本班仍不停任何一支（两袋 pending 在飞，按在册"袋在飞禁停心跳"）。

## 十三、本班三袋判死与对症重投（date 实测 01:12:46，读数取自死袋原文）

- **四态实读**＝`pending 0／processing 0／done 0／dead 3`（0001・0002・0003），三袋同死因且**不是**在册最大的"双侧皆改"族：dead_reason 首行逐字＝`网关落盘失败（COMMIT_FAILED）: 门禁 GATE-PRECOMMIT-RUN 阻断: 落地前 pre-commit run 在 staged 面（own-scope 临时索引）发现本提交文件的违规（hook=['gate-detect-git-dangerous'])`，first_dead 依序 00:31:48／00:32:46／00:33:51（ serializer 逐袋复算，三袋同因＝非本班三次独立事故）。
- **违规点定位（门自己打印的坐标）**＝ledger.md:739・ledger.md:938・checkpoint.md:165 共 3 处"reset 全硬复位"字面串——**全部系上班未落地稿行逐字引用死信原文**（现算落地边界：HEAD 面 ledger 583 行／checkpoint 107 行，三处行号均在边界之外＝本班携带的 1015-06 与 1016-02 正文）。⇒⑩席 1016-01 立的结构性判据在本席复现＝**引用型案卷首次上正门必被同门拦，且只要它不落地就永久挡本席每一袋**（该门扫整档快照，own-scope 作用域救不了"这文件就是我的"情形）。
- **处置＝走 ⑩ 已在册的正解（改喂给闸的输入，禁弱化闸／禁白名单／禁新豁免）**：对上述三处自家未落地稿行加行级精确标记（门 id 逐字匹配、非通配、单文件 3 处 ≤ 上限 10），且**仅行内追加**。写后自证现测＝ledger 行数 1176→1176・checkpoint 295→295（零变）、变更行号集合＝ledger {739,938}／checkpoint {165}（`only_marked_lines_changed=true`・`marker_count_in_file` ledger 2／游标 1）、已落地行零触碰。随后**用门自己那把尺复跑**＝`scripts/governance/d6_security/detect_git_dangerous.py <两件>` 现测 rc=**0**・零命中（不是本席自尺）。
- **纪律自守两处**＝本节不逐字写那条危险命令串（形近中文写法代替），原因＝⑩席 §14 实测"归因段自己写的字面串"能把第二袋再拦死；以及本班不再为"记一个读数"另起袋（在册新证＝每投一袋网关代起一枚心跳守护，补袋＝递归无出口），故游标只补一行、账写在这一袋里。
- **交付面未受损**＝三袋 payloads 的全部字节仍活在盘面（本班工作树＝唯一完整副本），死袋 blob 系第四态存证；本班以现 HEAD 为基底重投第四袋（严格超集，纯追加）。销账（mv 通道＋机生台账行）属 ⑩/⑫，本席不手删死袋。

[BLOCKER] 2026-10-17|⑦A席1016-03|工具缺陷|引用型案卷与自家门互斥在本席第二次复现：GATE-PRECOMMIT-RUN 的 GIT-DANGEROUS 扫整档快照，凡台账逐字引用死信原文（含危险命令串）则该件首上正门必被拦、且未落地期间**每袋连坐**；本班三袋全死即此形（⑩席 1016-01 同题已立案并已给出加标正解，本席只补第二例与"永久挡本席每一袋"的强陈述）|证据：dead/q-20261016-st-qoder-p07-1016-03-0001..0003.json 的 dead_reason 原文（三处行号由门打印）・`.runtime/tmp/p07/shift03_selfdoc.py` 加标前后自证读数・门尺复跑 rc=0|请 ⑩/⑤ 与 Owner 定"谁有权给旧行加标记"（⑩ 已开此单：已落地旧行加标＝改旧行；不加＝门永拦）；本席只给自家**未落地**稿行加标（同 ⑩ 口径），已落地案卷零触碰|高
