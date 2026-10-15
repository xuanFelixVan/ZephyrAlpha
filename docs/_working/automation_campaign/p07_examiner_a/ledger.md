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
