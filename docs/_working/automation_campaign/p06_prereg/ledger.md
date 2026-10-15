---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑥制卡席·findings台账
---

# findings 台账（追加式，禁删改他人行）

格式：`## <MM-DD HH:MM> · <一批摘要>` + 要点若干 + 自检结论（两轮）。
## 10-14 22:07 · st-e2e-test-p06 · ⑥制卡席真流程测试批（领 2 卡：2 填门柱 + 2 呈批草稿 + 0 翻转）

**领卡与处置**（均 status=empty、同族有在册冻结卡）：
1. `docs/03_modules/_domain_backtest/exam_cards/entry_flow/L1/TDM-E-L1-S0__calibration.yaml`（node=TDM-E-L1-S0/calibration，同族在册冻结 6 张）
   - 填门柱 pillars_numeric 五键逐字抄自同族 6/6 全一致值（源=`__02_货币卡.yaml:46-51`，另 5 张同值）：mono_spearman_min=0.6 / ic_mean_min=0.02 / ic_ir_min=0.3 / regime_same_sign=true / oos_same_sign=true。
   - 填窗口 in_sample 2019-01-04..2023-12-31 / oos 2024-01-01..2025-09-09（含 bull/bear regimes，逐字抄自 `__02_货币卡.yaml:8-17`；同族 6 张中 5 张同窗，`__07_margin_flow_shortwindow` 为另一短窗口径不适用，已写入卡内 frozen_note）。
2. `docs/03_modules/_domain_backtest/exam_cards/entry_flow/L0/TDM-E-L0-01__comparison.yaml`（node=TDM-E-L0-01/comparison，同族在册冻结 1 张）
   - 填门柱 pillars_numeric 五键逐字抄自 `__02_scenario_probability_stance_vs_fixed.yaml:48-53`（与 S0 族同一套在册冻结值）。
   - 填窗口逐字抄自同卡 `:8-17`。
- 两卡语义参数（hypothesis/buckets/pillars 文字门柱/target/data_binding）在册无可抄值 → **status 均维持 empty**（"填齐才翻"，未达 preregistered）。

**呈批草稿 2 件**（测试期禁改 05_owner_decisions.yaml 本体，草稿留此待呈批；一个数未编）：
- 草稿#1（S0 骨架卡）：五项语义参数全缺——/01 骨架卡无考试子题语义可抄（同族 6 张各考具体子题）；需 Owner 定"骨架卡考什么/退役/由具名卡代表"；另 target.primary 族内两种文案并存（4 张"（CSI300 次日收益，G0-4 主轴）" vs 2 张"（CSI300 000300 次日收益）"）需裁定唯一口径。
- 草稿#2（L0-01 骨架卡）：五项语义参数同缺（同族唯一在册卡考"九格概率定立场"，非骨架卡本体语义），需 Owner 定语义或退役。

**自检两轮**：
- R1：门柱非空且与冻结值逐字一致（字符串级比对零差异）；两卡 yaml.safe_load 通过；safe_write CAS 生效（改前 sha 前 8 位 3afd476c / 7687c225 与磁盘命中）；仅新增 window+pillars_numeric 与注释，tdm/lineage/原键零改动。
- R2：git status 确认 exam_cards 下本人修改仅本批 2 卡；他卡零触碰；冻结值未做任何算术或四舍五入（纯抄录）。

**findings（本批实测）**：
1. ⑥岗 SOP 输出口要求"pillars_numeric/window/buckets/data_binding 齐"，但 531 张在册卡中仅 3 张有 data_binding 字段，528 张用 lineage 承载绑定——SOP 字段面与卡面实际 schema 不一致（字段名对不上）。
2. 186 张 empty 卡全部是 /01 骨架卡（无具名子题）→ 按"语义缺→呈批、一个数不编"铁律，empty→preregistered 不可能仅靠抄值完成；"每班≥5 张"保底按字面只可能以呈批件计。
3. 同族冻结门柱双口径无裁决规则：TDM-E-L1-S2 族（分析时点 43 张冻结）=22 张标准五键+21 张事件研究五键（event_days_min=200 等）；TDM-E-L2-07 同族 sharpe_delta_min 0.1/0.2 并存——骨架卡抄哪套无据可依，只能呈批。
4. "各域判据册"不可寻址：仓内无具名判据册文件（find 仅 archive 命中），冻结值事实真源=冻结卡本体 pillars_numeric；呈批本体路径 `docs/_working/nightmine_campaign/05_owner_decisions.yaml` 全仓不存在。
5. 并发扰动：本席持有 ledger.md claim 期间，`docs/_working/automation_campaign/` p02..p10 被归档至 `docs/_archive/_working_20261014/`（归档方未检查 .ailocks claim）；本台账按原路径逐字重建模板后追加本条。另有 13 张 exam_cards 冻结卡（12 preregistered + 1 examined，含 S2 __40..__47 共 8 张）被他会话 staged 删除未提交，S2 族冻结参照面在收缩，本席未碰。
6. `scripts/backtest/` 残留 5 个 `factory_grid_executor.py.tmp.21772.*` 未跟踪临时文件（永久区临时文件，违 §9.4 精神）。
7. instruction/production_line_policy 引"裁定#518"为冻结口径来源：#518（ruling_registry.yaml:4735）主体=态层形态向职责裁准，其六条含判据二值/禁先用后批（语义可通），但不含任何卡面门柱数值，易误读为数值源。

## 10-15 02:53 · obi-probe-microchain · ③挖矿→⑤实现→⑥制卡微缩主链贯通冒烟（OBI 盘口因子，2 股×5 日）

**预注册草案（冻结件，先冻结后跑纪律；草案待⑥正式班过生成器通道，禁写真卡册）**：
- 因子定义：OBI=(bid_volume1-ask_volume1)/(bid_volume1+ask_volume1)，tick_depth_5 3 秒快照逐条计算后按 symbol×trade_date 日聚合均值。
- 参数冻结：档位=L1（买一/卖一）；质量过滤=quality_flag=1 且 bid_volume1/ask_volume1 非空且 (bid1量+ask1量)>0；聚合=等权日均值；快照粒度=表原生 3 秒。
- 冒烟窗口：000001.SZ、600519.SH 各自最近 5 个 distinct trade_date=2026-09-24/09-28/09-30/10-12/10-14（仅为贯通验证窗，非判据窗）。
- 建议判据草案（未冻结为正式判据，⑥班定）：日快照数下限质量门（本批实测 10-14 每股仅 1 快照，等权日均被单快照极端值支配）；候选方向=OBI 均值对次日收益的预测力门槛沿用族内在册五键（mono_spearman_min=0.6/ic_mean_min=0.02/ic_ir_min=0.3），是否适用盘口类待裁定。

**实测产物**：
- 表结构要点：tick_depth_5 列=bid_price1..5/ask_price1..5/bid_volume1..5/ask_volume1..5（Nullable(Decimal(18,4))/Nullable(UInt64)），trade_date Date，timestamp DateTime64(3,'Asia/Shanghai')，quality_flag UInt8，symbol 无交易所后缀（'000001'），market_type LowCardinality(String)，symbol_canonical 跨表 JOIN 键。
- 样本规模：000001.SZ 五日快照数 3094/3883/676/20/1；600519.SH 3033/3789/683/19/1（对应上列五日）。
- OBI 示例值（日均）：000001.SZ=+0.112011/+0.067727/-0.156009/-0.129929/+0.971028；600519.SH=+0.001604/-0.005178/+0.052796/+0.078059/-0.983914。
- 覆盖窗：600487 单股实测 2026-09-11..2026-10-14；两目标股冒烟窗见上；1970-01-01 存在空日期脏行（聚合时已排除）。

**findings（本批实测）**：
1. '000001' 同码双义：index（上证指数）与 stock（平安银行）各一份记录，盘口因子必须加 market_type='stock' 过滤，否则混入指数假盘口。
2. 各股覆盖窗不均且 LIMIT 采样有偏：全表 DISTINCT trade_date 采样（LIMIT 200000）只见 09-11..09-28，而 600487 单股实际到 10-14——覆盖窗结论必须按股内查询，禁全表采样外推。
3. 尾部快照稀疏：10-12（19-20 条/股）、10-14（1 条/股），n=1 快照产生 OBI=+0.97/-0.98 极端示例值，属数据稀疏非市场信号；正式判据必须含日快照数下限。
4. 数据起点 2026-09-11 晚于 2025-09-09 禁跑线：本批仅作管线贯通冒烟（任务指定 2 股×5 日真实读数），不构成 HOLDOUT/OOS 评估，判据窗冻结权在⑥正式班。
5. 候选落位 data/strategy_intake/lane_p0_obi_candidates.csv 为本批新建（此前不存在），正交闸因池信号未物化而缺席，已在候选行如实注明。

**自检两轮**：
- R1：全部读数走 ch_reader.query_rows()（失败必抛契约），每条 SQL 带 LIMIT；未用 query() 串 TSV、未用 count() 判空；candidate CSV 与 ledger 追加均走 safe_write_text CAS（ledger base_sha 前 8 位见上）。
- R2：写后进程外复核两文件在盘内容与本次写入一致；零 git commit；临时件全部落在 C:/Users/fanzi/Desktop/ZephyrAlpha_condaxis_tmp/obi_probe/。
## 10-15 05:54 · st-qoder-p06-1015-02 · ⑥制卡席正班（领 186 张→普查四态→填门柱 8 张 + 呈批草稿 4 件 + 0 翻转）

**领卡与普查**（本班实测分母：empty 卡 186 张，100% 为 /01 机生裸骨架——title_zh 含"骨架"、generated:true、hypothesis/buckets/pillars/target 全 null；具名子题的 empty 卡 0 张；对照申请 0 件——feedback/to_impl.md 实测仍是"空册待首班填写"模板）：
一致性判据=同族（node_id+family）在册冻结件（status∈{preregistered, examined}）的 `pillars_numeric` 与 `window` **全字段（含 regimes 牛熊段文字）**逐字一致。四态计数（71+11+3+101=186）：
- **可抄（全一致）71 张** → 本班填 8 张，余 63 张留后续班；
- **数值门柱多口径并存 11 张** → 呈批草稿#2（本席不擅挑）；
- **五键一致但 window 口径分歧 3 张**（TDM-E-L1-S0、TDM-E-L9-A01、TDM-X-R1-01__comparison——后者 3 张冻结件 3 套 window）→ 并入草稿#2；
- **同族零冻结参照 101 张**（连数值门柱都无源可抄）→ 呈批草稿#1。

**填门柱 8 张**（逐字抄同族在册冻结卡，零算术零改零舍；status 全维持 empty——语义参数缺，未达"填齐才翻"）：

| 骨架卡 | 抄源（同族在册冻结卡） | 同族冻结件数 |
|---|---|---|
| entry_flow/L4/TDM-E-L4-01__comparison.yaml | 同目录 TDM-E-L4-01__comparison__02_batching_all_vs_split.yaml | 1 |
| entry_flow/L1/TDM-E-L1-S4__calibration.yaml | 同目录同族冻结件 | 3 |
| entry_flow/L1/TDM-E-L1-S1__calibration.yaml | 同目录同族冻结件 | 2 |
| entry_flow/L9/TDM-E-L9-A03__calibration.yaml | 同目录 TDM-E-L9-A03__calibration__02_880板块相对强弱.yaml | 1 |
| exit_flow/S2/TDM-X-S2-01__comparison.yaml | 同目录 TDM-X-S2-01__comparison__02_执行方式路由与流动性三查对照.yaml | 1 |
| exit_flow/X1/TDM-X-R1-02__comparison.yaml | 同目录 TDM-X-R1-02__comparison__02_L3减仓顺序三臂对照.yaml | 1 |
| portfolio_flow/C3/TDM-F-C3-02__shadow.yaml | 同目录 TDM-F-C3-02__shadow__02_减半冻结线有效性.yaml（shadow 族自有 4 键，非 IC 五键） | 1 |
| position_flow/P3/TDM-P-P3-03__comparison.yaml | 同目录 TDM-P-P3-03__comparison__02_仓位定尺寸七档对照.yaml | 1 |

每张卡留两层溯源：`window.frozen_note`（抄源路径 + window/pillars_numeric 行号 + 同族一致件数）与文件尾 `# [st-qoder-p06-1015-02 2026-10-15]` 注释行。

**呈批草稿 4 件**（本体通道两头不可写，见 findings#4，故留本台账待注入；一个数未编）：
- **草稿#1 骨架卡转正语义缺口（186/186，含 101 张零同族参照）**：⑥席抄不到语义参数（hypothesis/buckets/文字门柱/target 在骨架卡层无同义在册值）。请 Owner 三选一——(a) 责成③④席当班产具名子题卡（语义由具名卡承载，骨架卡由具名卡代表）；(b) 授权本席以卡内 `tdm.decision_question` 逐字充当 hypothesis（在册面抄录、非编造），但 buckets/文字门柱/target 仍无源⇒只能"半转正"，须同时定义半转正态可否开考；(c) 骨架卡退役、卡册只留具名卡。不点的后果：empty→preregistered 零翻转，⑦⑧席只能吃现存 preregistered 187 张存量，主流水断料。
- **草稿#2 同族门柱多口径 12 件待裁唯一口径**：数值门柱多口径 11 族——TDM-E-L1-S2/calibration（43 张冻结件 2 套五键＝标准 vs 事件研究，与 10-14 班 finding#3 同值复证）、TDM-F-C2-02/shadow（3 张 3 套）、TDM-E-L1-S3、TDM-E-L2-01、TDM-E-L9-A15、TDM-X-S1-02、TDM-X-S1-03、TDM-F-C1-02、TDM-P-P1-05、TDM-P-P2-01、TDM-P-P3-01（各 2 套）；window 分歧 3 件见上。
- **草稿#3 IC 五键套到非 calibration 族的适用性**：在册冻结件键集实测分布——calibration 129 张（IC 五键 90／事件研究五键 23，键集共 18 种）；comparison 68 张（IC 五键 24／Sharpe+MaxDD 三键 7，键集 33 种，23 张自写 `numeric_face_mapping_note` 手工解释映射）；ablation 31 张（IC 五键 18，键集 13 种）；shadow 14 张（**IC 五键 0 张**，主键集=maxdd_delta_max/sharpe_vs_baseline_min/tracking_diff_max，映射注解 0 张）。即"考的是 Sharpe/MaxDD/换手面、机判读的是 IC/Spearman 列"的错位在 comparison+ablation 族是多数派，靠每卡手写注解兜。请裁：是否立法"非 calibration 族沿用 IC 五键必须同卡带 numeric_face_mapping_note，缺注解禁翻 preregistered"。（与 OD-1 对照/消融执行器立项不同面，非重复呈批。）
- **草稿#4 致⑤席修改单**：生成器会把数值门柱静默洗掉——`scripts/backtest/generate_exam_card_skeleton.py` 的 `_load_human_fields` 保留集实测只有 7 键（hypothesis/window/buckets/pillars/target/status/lineage），而 `render_card` 模板不含 `pillars_numeric`；同件跑 `_load_human_fields`+`render_card` 复现＝重渲染文本含 window: True、含 pillars_numeric: **False**。⇒ 凡 TDM 派生块漂移触发重渲染，抄到骨架卡上的数值门柱整块消失而 YAML 仍解析通过，直到考试侧以"卡缺 pillars_numeric"炸（`scripts/backtest/fexam/calibration_exam.py` 三处抛点）。请⑤席把 pillars_numeric 连同人填面（signal_kind/preregistered_by/discipline/numeric_face_mapping_note）纳入保留集。本席写域禁改代码。

**findings（本班实测）**：
1. **本班自犯并纠正**：首版填卡脚本把 window 子键写成 0 缩进，致 TDM-E-L4-01 解析后 `window=None`（子键漂到顶层＝静默语义丢失，文件照样 parse 绿）。已 `git checkout HEAD --` 复位该卡后重做，最终 8/8 逐值对表通过。教训＝改后必以解析值自证，文本在不在不算。
2. 口径收紧：把 regimes 纳入一致性判据后，可抄面 72→71，唯一被改判的是 TDM-X-R1-01（旧口径只比 in_sample/oos 会漏掉它 3 套 regimes 文字面并存）。请后续班沿用严口径。
3. shadow 族在册零张用 IC 五键（0/14）＝该族键集自成一套；本班 TDM-F-C3-02__shadow 抄的是族内自有 4 键，未把 IC 五键外推。
4. **呈批本体通道两头不可写（实测）**：新真源 `docs/04_research_records/mining/ledgers/nightmine_20261010/05_owner_decisions.yaml`（裁定#536 指定）在盘含 OD-1..OD-10，但 `git cat-file -e dev:<该路径>`=NO、`git status`=AM，且队列 pending/processing/dead 三态扫袋零命中＝他会话在途未落地新件；旧真源 dev 侧仍在（`git show dev:docs/_working/nightmine_campaign/05_owner_decisions.yaml` 有 OD-1..）而盘面已随 10-14 归档波不存在（find docs 只命中新路径一处）。两头都动＝与他班袋对撞或引用已删档，故本班按 10-14 班先例把 4 件呈批留台账，待新册落地后由下一班注入。
5. 上一班（10-14 22:07 st-e2e-test-p06）填的 2 张卡未落地：主区暂存面 `M ` 状态，载体袋 q-20261014-st-autoplan-20261014-0004 已 dead（死因＝SOP 册"非注册表族件双侧皆改真冲突"）。本班未触碰这两件以免成回退弹；其中 TDM-E-L1-S0 按本班严口径属 window 多口径（该呈批而非该抄），注入草稿#2 时一并补记——这不是撤上一班的门柱，是补一条"该族窗口有两套口径"。
6. 台账基线（防"我删了别人行"）：dev 版 ledger 仅 157 字节（模板头），主区盘面 4795 字节含两条未落地条目（10-14 22:07、10-15 02:53）；本班成袋字节＝盘面 4795 全等前缀 + 本条追加，startswith 双向实测为真，删除他人行数=0。
7. 能力反查留痕（宪法 §0 第 4 条）：query=考试卡／预注册／判据门柱／backtest exam card／exam skeleton／正交闸 命中 0/0/0/0/0/0，同尺正对照 registry=68、测试=19、数据库=5 证明尺未坏（零命中≠尺断）；审计落 `.runtime/lookup_audit/st-qoder-p06-1015-02.jsonl`。

**自检两轮**：
- R1（值面逐字对表）：8 张卡逐张解析比对 `pillars_numeric` == 抄源逐值、`window.{in_sample,oos,regimes}` 三键 == 抄源逐值、`status` 仍 empty、其余 12 键（schema_version/card_id/node_id/family/generated/title_zh/hypothesis/buckets/pillars/target/lineage/tdm）与写前 JSON 全等；yaml.safe_load 8/8 通过；全部经 safe_write_text CAS 写（带 base sha256）；门柱数值零算术零四舍五入。
- R2（归属·净零·保底）：车道 `git status -- docs/` 仅本班 8 卡 + 台账 + 游标，零他人件、零新增文件、零删除；对照卡对 0 对（前置=to_impl.md 零申请，实测非漏领）；净零=零新 gate/零新脚本/零新规则册（普查走一次性 stdin 脚本，产物落 `.runtime/tmp/p06_1015_02/` 不入册）；保底达成=填 8 + 呈批草稿 4（≥5），且领用面 186 张 100% 分类完毕、无一未定去向。
- 本班耗时：05:30 进场，至投递 05:54＝24 分钟（含普查、一次自犯回退重做）。
## 10-15 06:36 · st-qoder-p06-1015-01（自号，实测并发班 1015-02 在途）· ⑥制卡席 1015 班（领 186 张普查 + 2 在途件复位 + 呈批 3 件寄存 + 0 翻转）

**领卡与处置**：
- empty 卡池实测＝186 张，逐件字段级 walk 判定 100% 是 generated:true 的 node__family 裸骨架（具名 empty=0）；语义五面
  hypothesis／buckets／pillars／target／data_binding 非空命中 **0/186** ⇒ 本席「只抄在册冻结值、一个数不编」无一条门柱可独立成卷，
  本班翻转 0 张（保底走呈批件口径，SOP §3⑥「骨架卡时代呈批件计入保底」）。
- 领回上一班（10-14 st-e2e-test-p06 测试批）遗留在主区暂存区的 2 张骨架卡，处置＝**HEAD 复位 + 存证**（根宪法 §9.4 无主 staged 残留正解）：
  entry_flow/L0/TDM-E-L0-01__comparison.yaml、entry_flow/L1/TDM-E-L1-S0__calibration.yaml；复位前字节副本
  .runtime/tmp/p06_1015_01/staged_evidence_*.yaml（sha256 前 12 位 1687b734c10b／21821092cebf，对 HEAD blob 37dbdf62393／e3b75e64148）。
  复位不是嫌脏，是实测蒸发（见 findings 2）＋复位前两路径在队列 pending/processing 86 袋零命中（不伤任何在途袋）。
- [对照]申请＝**零**：feedback/to_impl.md 实测 11 行仍是空册（`（空册待首班填写）`）⇒ 本班无可配对 champion/challenger，对照卡零产出。

**呈批 3 件（OD-11/12/13）——正文已写好，落地未成，全文寄存本台账**（详见 findings 9）：
写入 docs/04_research_records/mining/ledgers/nightmine_20261010/05_owner_decisions.yaml 走 safe_write_text CAS 成功（written=True，
95→135 行，纯追加前缀断言过），但入袋预检 **CREATE-GUARD 拦**（该册在 HEAD 不存在＝整个 04 区只在 index）⇒ 本席把该册
`git checkout --` 复位到 index 字节（复位后 95 行、has_OD-11=False，本班写入内容存 .runtime/tmp/p06_1015_01/od_with_my_append.yaml），
**待 04 区落地后由下一班重投**（正文如下，抄此即可，勿再从零推）。三条全部只引在册冻结值与本进程实测，零自拟数值。

```yaml
- id: OD-11
  项: 186 张 /01 裸骨架卡的处置口径——⑥席零语义可抄，empty 恒不降，须择一（允许⑥自出命题／退役只登记不删／保留占位由具名卡代表）
  实测分母: 本进程对 exam_cards 全 531 张逐件 yaml.safe_load 字段级普查——status=empty 186 张，100% 为 generated:true 的
    node__family 裸骨架（具名 empty=0）；语义五面 hypothesis／buckets／pillars／target／data_binding 非空命中 0/186，
    window 2/186、pillars_numeric 2/186（＝本席 10-14 e2e 测试班遗留，本班已按根宪法 §9.4 HEAD 复位并存证）；
    同池其余状态 preregistered 187／examined 55／blocked_on_data 64／blocked_on_impl 39；上游 p03/p04/p05 三席台账实测仍是模板首 8 行（零具名子题产出）
  为何要点头: 判据语义（考什么、怎么分桶、目标列是谁）按生产线 SOP §3⑥ 输入口属③④席具名子题产出，本席受「只抄在册冻结值、一个数不编」约束，
    无权自拟命题；三条出路分别等于扩⑥席命题权（改岗位编制）、废卡登记（改资产处置面）、维持现状（继续零翻转），均属 Owner 保留面
  不点的后果: ⑥席每班只可能出呈批件（保底绩效条款空转），empty 恒 186 不动；⑦⑧开闸的 187 张 preregistered 考完后卡池无新增冻结面，
    生产线「③④挖矿→⑥制卡冻结」段实际断料，下游只能反复考同一批
  凭据: 普查与复位留痕 docs/_working/automation_campaign/p06_prereg/ledger.md（10-15 06:36 · st-qoder-p06-1015-01 班次）；
    脚本读数面 .runtime/tmp/p06_1015_01/；生产线 SOP §3⑥（输入口／保底绩效两行）
- id: OD-12
  项: 机生骨架卡面上填门柱会被生成器静默抹掉——立法「门柱只落具名卡」还是扩生成器保留面
  实测分母: scripts/backtest/generate_exam_card_skeleton.py:175-188 _load_human_fields 只回带 hypothesis／window／buckets／pillars／
    target／status／lineage 七键，pillars_numeric 不在保留面；对 10-14 遗留的 2 张骨架卡逐件渲染比对，磁盘与渲染的唯一键集合差＝['pillars_numeric']
    （⇒ 重跑即删该键，源注释同删）；--check 复位前 drift=8／identical=178，复位后 drift=6／identical=180
    （其余 6 件系 L9-A01/A02/A03/A05/A06/A09 的 tdm 块漂移，以 HEAD 版 TDM 为基重测仍漂移＝早于本班存在，非本席所造，本席未碰）
  为何要点头: 两条修法代价不同——改生成器保留面＝动机生件契约（须同改 --check 门与消费面，允许骨架卡冻结）；
    不改而立法「骨架卡禁填门柱」＝零代码改动，但 SOP §3⑥「只抄在册冻结值」的工序产出在骨架卡时代无处安放。属口径挪动，本席不自裁
  不点的后果: 后续任何班按字面往骨架卡抄数值，都会在下次生成器重跑时被静默抹除——账面「门柱已冻结」而盘面无值（静默降级/假绿形态），
    且每次抄写都新增 --check 漂移，连坐他人提交
  凭据: python scripts/backtest/generate_exam_card_skeleton.py --check 复位前后读数（drift 8→6）；生成器源码 175-188 行；
    复位前暂存面证据副本 .runtime/tmp/p06_1015_01/staged_evidence_TDM-E-L0-01__comparison.yaml（sha256 前 12 位 1687b734c10b）与
    staged_evidence_TDM-E-L1-S0__calibration.yaml（21821092cebf），对应 HEAD blob 37dbdf62393／e3b75e64148
- id: OD-13
  项: 同族门柱多口径并存无择一规则——请批唯一口径（S2 双套五键／L2-07 三套／S0 target.primary 双文案）
  实测分母: 本进程按 node_id 取族、只计 status 属于 preregistered/examined 的 pillars_numeric 键值集合去重——
    TDM-E-L1-S2 族 46 张（43 冻结）＝2 套并存（标准五键 22 张：mono_spearman_min=0.6／ic_mean_min=0.02／ic_ir_min=0.3／
    regime_same_sign／oos_same_sign；事件研究五键 21 张：event_days_min=200／event_gap_max_bp=0.0／event_t_stat_max=-2.0／
    event_regime_gap_same_sign／event_oos_gap_same_sign）；TDM-E-L2-07 族 4 张（3 冻结）＝3 套并存（标准五键 1 张／
    sharpe_delta_min=0.1 配 maxdd_improvement_min=5.0 一组 1 张／sharpe_delta_min=0.2 配 maxdd_improvement_min=5.0 一组 1 张）；
    TDM-E-L1-S0 族 6 张冻结门柱 6/6 同值，但 target.primary 双文案并存（「next_day_index_return（CSI300 次日收益，G0-4 主轴）」4 张／
    「next_day_index_return（CSI300 000300 次日收益）」2 张）
  为何要点头: 门柱取值与判定词都是判据的组成部分（裁定#518 六条③「判据二值，判定词不得事后增设」，ruling_registry.yaml:4735；
    G4-5 判据版本化禁追溯「事后挪门柱＝作废」，真源 docs/01_policies_and_standards/sop/governance_sop/adjudication_routing_policy.md:98）；
    择一即挪门柱，只能呈批——生产线 SOP §4 自我迭代回路同文（判据改动=挪门柱，只能呈批）
  不点的后果: ⑥席每逢多口径族只能停手（本班零翻转的第二主因）；两套口径继续并存，新具名子题卡抄错即与母卡分数不可并排解读，
    下游按「同族=同尺」误读
  凭据: 本席 10-15 班次 ledger 逐值记录；ruling_registry.yaml:4735 裁定#518；adjudication_routing_policy.md:98 G4-5
```

**并发与交接（本席两文件被同席他班在途袋占用）**：
- 实测 q-20261015-st-qoder-p06-1015-02-0001（建袋 05:55:57，10 件＝8 张骨架卡填门柱 + 本席 ledger.md + checkpoint.md）。
  本班不自称「首班」——自号 01 是按台账当日 p06 节计数所得（写本节前台账无 p06 条目），并发班已用 02 号，**号位终裁归⑩席**，本班不复号。
- ledger.md＝共享追加型，本班把袋内字节做成**两班并集严格超集**（10-14 测试批节＋02:53 obi 节＋02 班 05:54 节原文逐字在内＋本班节），
  自证法＝按「## 」切块，对彼袋 blob 与主区旧面逐块 verbatim 命中，删除集＝空。
- checkpoint.md＝游标态字段，无法并集，本班版为后到态并如实注明 02 班在途；若彼袋后落判 dead，其台账全文已在本册落地、其卡件字节仍在
  队列 blob（blobs/2df4cf85…）可取，内容不丢——**下班若见该袋 dead，先读 dead_reason 再按超集法重投，勿重写其普查结论**。

**findings（本批实测，非转述）**：
1. 卡池状态面＝preregistered 187／empty 186／blocked_on_data 64／examined 55／blocked_on_impl 39（合计 531，逐件 walk；与⑩席 05:47 读数逐项同值＝近一小时零流转）。
   ⚠本班首测把「status: empty」跑成非锚定 grep 得 187——多出的 1 张是 TDM-F-C1-02__shadow__03 卡内 hypothesis 散文写了「status: empty=未冻结禁考」字样；
   改锚定 `^status: empty$` 后 186 才是真面，留案自查（同一族坑：字面量尺必须先验命中面）。
2. **骨架卡上的门柱是易失面**：generate_exam_card_skeleton.py:175-188 `_load_human_fields` 只回带七键，`pillars_numeric` 不在其中；
   两张遗留卡逐件渲染比对唯一键集合差正是 ['pillars_numeric'] ⇒ 生成器重跑即删；`--check` 实测复位前 drift=8／identical=178，复位后 drift=6／identical=180
   （window 属保留面故可存活，数值门柱不能＝半冻结核，正是「账面已冻结、盘面无值」的形态）。
3. 残余 6 件 drift 系 L9-A01/A02/A03/A05/A06/A09 骨架卡 tdm 块——以 HEAD 版 TDM 为基重测仍漂移＝早于本班存在，非工作区在途 TDM 所造；
   本席无该面写权，未修，供⑤/⑩认领（机生件同步缺口又一形态）。
4. 呈批真源册在 HEAD 即**非法 YAML**：OD-3 的「实测分母: 2 张卡标 owner_gate_required: true」未加引号（safe_load_all ScannerError，HEAD 与盘面同态，
   且本席写前只得以「本批块独立解析＋纯追加断言」自证）。本席未代修（该件属 nightmine 战役面，根宪法 §3.4 owner 责任制）；
   修法一行＝给该标量加引号或改写为 owner_gate_required=true。
5. 上游断料实证＝p03_miner_lib／p04_scout_web／p05_impl 三席台账实测仍只有模板首 8 行（零产出）⇒「③④出具名子题」这条前提短期不成立，
   本席连续两班翻转 0 的根因在此，已折进 OD-11「不点的后果」。
6. ⑨席 10-15 两班在自席台账写了对 TDM-E-L3-07-3 与 TDM-E-L9-A01 的三条对照建议（close→close 口径复算／TopN 选股面／去 ST 敏感性），
   但按 SOP 应落的 feedback/to_impl.md [对照] 申请单零字 ⇒ ⑥席领不到，**对照卡做不了是交接面断线而非本席偷懒**；报⑩席巡单。
7. ⚠**04 研究记录区整体尚未落地**：git ls-tree HEAD docs/04_research_records/ 空、index 该路径 97 件（裁定#536 迁移只在暂存面，
   scorehome 三袋 pending）。后果＝⑥席呈批真源与⑦⑧成绩真源现都指向一个 HEAD 里不存在的目录，任何班往里写都会撞 CREATE-GUARD；
   各席 v1.5.1 指令面（含本席 instruction.md）本身也仍在 index staged 未落——全线「入册」动作在 04 区落地前都不可完成，非本班能力问题。
8. 本班把 HEAD 侧台账空洞一并补上：HEAD 的 p06 ledger.md 只有 9 行模板，10-14 e2e 批与 02:53 obi 批两节至今未落地（只活在主区工作区与各车道快照）；
   本袋同文件内三节齐落（同件追加，非跨件代投他人在途件）。
9. 并发班填的 8 张骨架卡门柱与本班 OD-12 同面（生成器重跑即蒸发）——本席不代改、不判其对错，留其自处或⑩席巡单。

**本班实际耗时**：date 实测 06:10:25 开班 → 06:36 落盘＝26 分钟（入袋与收尾另约 6 分，终值 32 分；SOP 3-B 估⑥席 20 分＝偏差 +60%，主因=并发撞车与 04 区未落地两条在册外障碍，如实记账不改估时基准）。

**自检两轮**：
- R1（写前/写中）：呈批册写入带 expected_base_sha256 的 safe_write_text CAS（written=True）＋纯追加断言＋本批块 yaml.safe_load 通过＋六键结构核对；
  OD-11..13 撞号先查（写前册面零命中）；复位前双件证据副本落盘并核 HEAD blob sha；`--check` 与逐件渲染比对均本进程实跑；门柱数值零自拟（只引在册五键与 window）。
- R2（写后进程外）：重读盘面——05 册已回到 index 字节（95 行、OD-11 不在盘面＝本班未越闸留半件）；exam_cards 本席两件在 git status 零命中、`--check` drift 恒 6；
  台账袋内字节逐块核对＝彼袋 3 节 + 本班节全在内且旧面两节 verbatim（删除集空）；游标改写用整行替换并断言仅 3 行变化、其余字节不变。
