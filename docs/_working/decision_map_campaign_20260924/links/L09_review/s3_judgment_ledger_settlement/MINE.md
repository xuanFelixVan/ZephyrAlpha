---
ttl: task_bound
doc_type: log
title: L09-S3 子模块挖矿簿 · 判定台账与结算
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-L09
status: MINE 完成（六向封口；全部行数为 09-26 CH 只读探针实测，禁裸 duckdb，reader 角色）
---

# L09 · S3 判定台账与结算

**① 职责一句话**：把"当时怎么判的"和"后来证明对不对"分成两栏长期记账，并让后者在无人干预下自动回填——它是全链唯一具备**自我校验能力**的地方。

**② 现状实测（2026-09-26 本机 CH 只读探针 `.runtime/tmp/l09_mine_probe{,2}.py`）**

**表真源与引擎归属（先纠一处易错口径）**：判定三表 + 验证表全在 **`c1_market`**，不在 `c1_backtest`。本册首轮探针误按 `c1_backtest` 前缀查结算列，得到全 "COLUMN ABSENT" ——**典型"库前缀错=假无数据"**，已换正确前缀复核，下表为复核值。

| 表（c1_market.） | 行数 | 日期列 | 说明 |
|---|---|---|---|
| `judgment_intraday_market_state` | **20** | 无 trade_date 列（用 `asof_ts`/`outcome_ts` 时间戳） | 盘中五态判定 |
| `judgment_next_day_forecast` | **4** | 同上 | 次日概率判定 |
| `judgment_daily_plan` | **9** | 同上 | 晨间预案判定 |
| `judgment_plan_verification` | **14** | `verified_at` | 计划↔验证联结（E2E 记的"0→6 行"现为 14 行） |

### 结算列回填率（本块最重要的实测，直接校准 D7 判语）

| 表 | 结算列回填（filled/rows） | 判读 |
|---|---|---|
| intraday_market_state | `outcome_ts` 20/20、`evaluated_at` 20/20、`eval_score` 20/20、`brier_contrib` 20/20 | **满回填**——真在自动结 |
| next_day_forecast | `evaluated_at` 4/4，但 `brier_score` **1/4**、`log_loss` **1/4**、`calibration_bucket` **1/4**、`eval_score` **1/4** | **仅 1/4 完成打分**，其余 3 行卡在 T+1 grace 未回 |
| daily_plan | `evaluated_at` 8/9、`eval_method` 8/9，但 `eval_score` **2/9**、`actual_scenario_id` **2/9** | **仅 2/9 真出分** |
| plan_verification | `plan_followed` 14/14、`deviations` 14/14、`verified_at` 14/14，但 `plan_quality_score` **6/14** | 质量分缺口 8/14 |

⇒ 对 SKEL/09 骨架「D7 大半已闭」的重勘裁定：**"链已通"成立，"账已结"不成立**。
Brier/log_loss 写入路径确凿存在且有非空值（不是死列），故结构面已闭；但分母侧同时受两件事压制：
(a) **判定样本本身极稀**——next_day_forecast 全史仅 4 条判定、daily_plan 全史仅 9 条，任何校准桶（calibration_bucket）在此体量下不可统计；
(b) **grace 回填有滞后的洞**——`evaluated_at` 已写而分数列为空，说明结算器"评估过但判不了分"（unresolvable 路径）与"待 T+1"两态**在列上不可区分**（无 unresolvable 标记列，仅靠"分数为 NULL"表达，NULL 语义重载）。

### 触发面实测（三态判定）

| 组件 | 实码 | 触发面 | 判定 |
|---|---|---|---|
| 判定产出 | `plan_engine/daily_plan.py::maybe_emit_daily_plan`、`scenario_classifier::maybe_classify_intraday_scenario`、`intraday_l1_tracker::maybe_track_intraday_state`、`next_day_forecaster::maybe_emit_next_day_forecast` | 事件链钩子 4/5/8/9（`pipeline_events.py:1054-1082`）+ dloop 段 | **已接电** |
| 收盘验证 | `plan_engine/close_verifier.py::maybe_verify_plan_close` | 事件链钩子 6 + dloop `close_verify`；钩子序契约=必须先于 settle（`:1050-1053` 注释明写"次序颠倒=当日宽限被误判 unresolvable"） | **已接电** |
| 结算 | `plan_engine/judgment_settler.py::settle_all`，钩子 7 `maybe_settle_judgment_ledger`（`pipeline_events.py:875-917`） | 事件链 + dloop `settle`；幂等键 `judgment_ledger_settle:<D>`，**记号先落再动手** | **已接电** |
| Brier 校准 | `plan_engine/brier_calibration.py`（MOD-PLAN-010 纯函数），被 judgment_settler import | 随结算链 | **已接电（被动）** |
| 结算聚合报告（按 module/model 聚合） | 判定台账标准 §四 Phase 5 数据源 | **未见生成件** | **缺失**（=L09-C06） |
| 相似日/8 态先验消费 | `similar_day_evaluator`，dloop `similar_day` 段（`:416`） | 段在跑=观察面；**先验喂给 L0-04 判定的消费点未接** | **覆盖未接电**（D7 残余，维持） |

新鲜度：三表无 date 列，"至今天数"须按 `asof_ts` 判；本册未取到逐日 asof 序列（探针按 trade_date 口径设计，未覆盖时间戳列），**登记为未测字段**，不做"新鲜/不新鲜"结论。

### 结算器合规性自证（宪法 §9.3 相关，本册只登记不改）
`maybe_settle_judgment_ledger` 头注明文自证："宪法 §9.3 合规（零新机制）：**不建 cron/Timer/sleep 循环，节拍由调度器 task_completed 唤醒给**"。⇒ 同一 `settle_all` 被 dloop `settle` 段的 **16:45 cron 二次驱动**，正是 L09-S1 册登记的偏差候选的实证落点（此处补证，裁定仍归 L09-C01，本册不施工）。

**③ 六向台账**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：dloop 各段（预案/盘中 60min bar/收盘）；判定台账标准三表 schema 真源=`docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md` §三（通用列 + 判定/结算分离铁律，本册实测列名与该契约一致：`judgment_id/module_id/model_version/horizon/confidence/asof_ts/input_cutoff_ts/inputs_ref/payload/subject/run_id/synthetic` + 结算组 `outcome_value/outcome_ts/eval_method/eval_score/evaluated_at/evaluated_by`）。外部：已查无（判定台账体裁=内部治理面） |
| ②下游 | 内部：S9-7 W0 归因（MOD-PLAN-009 消费 outcome 族）、次日 L0-01 计划生成、S9-4 拍板体的 `market_state`/`state_confidence`。外部：预测校准在业界是**概率预报校验**正典域（Brier 1950 / log score / reliability diagram / ECE），见 ⑤ |
| ③算法 | 内部：`brier_calibration.py` 纯函数 + `brier_score_multiclass`；多分类 Brier 与 reliability bucket。外部：Brier Score（W. G. Brier, 1950, *Weather Forecasting* 前身 NWFR）为概率预报标准尺；scikit-learn `brier_score_loss` / `calibration_curve`（BSD-3-Clause）为现成实现——**仓内已自建且为纯函数，不引外部依赖**，但**可靠性曲线（reliability diagram）与期望校准误差 ECE 是业界标准呈现，仓内有 `calibration_bucket` 列却无绘报件** → 与 L09-C06 同题 |
| ④后端 | 内部：①三表无 date 列 ⇒ 所有"日频幂等/日频查询"都要走时间戳函数或外部记号（记号文件即第二真源候选）；②NULL 语义重载（见 ②）；③记号先落再动手 ⇒ 当日失败**不再由事件链自愈**，靠次日累积扫描回捞，自愈滞后=1 交易日；④人工逃生口 `settle_all()` 直调，写在头注里但无脚本化入口。外部：已查无 |
| ⑤前端 | 内部：无校准呈现面（无 reliability 图、无分 module 的胜率表）。人工面靠翻 CH。外部：reliability diagram / calibration plot=概率校准标准呈现，属**必配而缺** |
| ⑥数据字段 | 内部：**"字段在"≠"数据可得"三重实证**——(1) `brier_score` 列在但只 1/4 有值；(2) `plan_quality_score` 在但 6/14；(3) `calibration_bucket` 有值仅 1 条 ⇒ **任何桶级统计当前分母=1，不可算**。另 `synthetic` 列 20/20、14/14 全填 ⇒ 真/合成判定的占比首次可机读（本册未取分布值，登记为下批可续） |

**④ 缺口清单**

| 编号 | 内容 | 状态 |
|---|---|---|
| L09-C06 | 结算聚合报告件（按 module_id/model_version/时间窗聚合，喂 MOD-PLAN-009 与 meta-回测） | 在册，本册补"为何必需"的实测理由（校准桶分母=1） |
| D7 残余 | 8 态转移先验 / 相似日推理消费点未接电（L0-04） | 在册，本册实测 `similar_day` 段在 dloop `:416` 有注册（观察面），消费未接 |
| L09-S3-G1（新） | **NULL 语义重载**：`evaluated_at` 非空 + 分数列 NULL 同时承载"待 T+1 宽限"与"永久 unresolvable"两态；标准 §三只说"unresolvable 留痕"，实测**无留痕列**（四表列名全集内无 `unresolvable`/`settle_state`） | 新增·高优先级（直接污染一切回填率统计） |
| L09-S3-G2（新） | **判定三表缺 date 型分区列**，一切日频闸（记号文件/`asof_ts` 函数）都是补偿机制；同域 `decision_daily` 反而有 `trade_date` ⇒ 同链两族表口径不齐 | 新增 |
| L09-S3-G3（新） | **样本密度本身是瓶颈**：next_day_forecast 全史 4 条 / daily_plan 全史 9 条；H1 未接电（见 S2 册）直接后果之一就是晨间判定不产 ⇒ 台账"接电但饿"。此条与 L09-C01/TRD-A04 联动，不另立施工 | 新增·联动 |
| L09-S3-G4（新） | 自愈滞后 1 交易日（记号先落 + 累积扫描）未被任何文档声明；Owner 若当日看"未结算"会误判为卡死 | 新增（文档级） |
| L09-S3-G5（新） | 探针库前缀坑（`c1_market` vs `c1_backtest`）已在本车道造成一次假无数据 ⇒ 建议判定四表的 db 归属进 ROOR/表册可查项 | 新增（卫生） |

**⑤ 自审闸三态裁定**

| 项 | 裁定 | 理由 / 解锁条件 |
|---|---|---|
| L09-C06 结算聚合+校准呈现 | **施工（P1）** | 缺的不是算法是"把已有列聚出来并画可靠性曲线"。终局全貌下"Owner 自己判断模型准不准"不可自动化 ⇒ 不许封。零新表（视图/日级物化即可），净零合格 |
| L09-S3-G1 unresolvable 显式化 | **施工（P0，本册最高优先）** | 一条枚举列即可消除 NULL 重载；不改它，一切回填率数字（含本册自己给的）都带歧义。属"判据口径"级，优先级高于新增功能 |
| L09-S3-G2 date 列 | 挂起排期 | 解锁=L09-S3-G1 同批改 schema 时顺带；不可逆点=CH 加列易、改分区键难（需 rebuild），故必须与 G1 合并成一次 DDL 变更，不许分两批 |
| D7 残余（先验消费） | 挂起排期 | 解锁=8 态转移先验有真实消费方（L0-04）落地；当前 `similar_day_evaluator` 已是观察面，先验属"从观察到决策"跨越，属策略车道非本车道 |
| L09-S3-G3 样本饿 | **不独立立项** | 处方在 S2/L09-C01；本册只负责把"饿"量化成 4/9/20 三个数字供裁定 |
| L09-S3-G4 / G5 | 施工（P3 文档/卫生） | 一次登记即销口 |
| 「判定/结算分离」铁律本身 | 施工（P1，实为**验收项**） | 实测已遵守（判定列与结算列分组清晰、结算走 mutation），但**无自动验收**——建议把"结算链不得改判定列"做成 own-scope gate 断言，防后续车道偷懒回填 |

**⑥ 挖矿日志**

| 轮 | 矿脉 | 判定 | 归因 |
|---|---|---|---|
| R1 | CH 表发现 + 行数（探针 v1/v2） | signal | 四表在 `c1_market`，非 `c1_backtest` |
| R2 | 结算列回填率逐列 `countIf(IS NOT NULL)` | signal | **本册主证据**：链通而账未满（1/4、2/9、6/14） |
| R3 | 全列名 dump 找 unresolvable 留痕列 | signal | 无此列 ⇒ G1 |
| R4 | 事件链钩子 4-9 实码 + 头注 §9.3 自证 | signal | 已接电判定成立；并取到 cron 二次驱动的实证落点 |
| R5 | 外部对表 | **部分** | 已就位候选=Brier(1950) / scikit-learn `brier_score_loss`+`calibration_curve`(BSD-3) / reliability diagram+ECE 标准呈现。**未做全网二次独立核验**，延至统一轮 |
| R6 | `asof_ts` 新鲜度序列 | **noise（未取得）** | 探针按 date 列设计，四表无 date 列 ⇒ 归因=**工具口径不匹配非无矿**，下批改 `max(asof_ts)` 即可取 |

**本册封矿判据**：六向封口；D7 判语从"大半已闭"细化为"链通/账未满 + 三组可复核分母"；三条新缺口（G1 为 P0）。⇒ **子模块封矿**。
