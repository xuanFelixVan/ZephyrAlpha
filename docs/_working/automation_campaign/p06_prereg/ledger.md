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

## 10-15 06:52 · st-qoder-p06-1015-01 · 更正块（自犯第 N 次同型：把"零文档"读成"能解析"）

- **作废句**（06:36 节 findings#4 原文照留不删）：「呈批真源册在 HEAD 即非法 YAML……HEAD 与盘面同态」。
- **实测更正**：`git show HEAD:docs/04_research_records/mining/ledgers/nightmine_20261010/05_owner_decisions.yaml` **rc=128、stdout 长度 0**＝该册从未落地（HEAD 无此件）。
  我当时用的后台探针把空串喂给 `yaml.safe_load_all` 得 0 个文档，打印成 "HEAD PARSE_OK docs= 0"，我照抄成「HEAD 同态非法」——
  **零文档≠可解析**，这是"零命中尺缺正对照"的老毛病第 N 次复发（在册老教训：零命中尺必须先配正对照），责任在本席读尺不读义。
- **真结论（只此一条成立）**：非法 YAML 存在于 **index/盘面字节**——当前 95 行版第 26 行「实测分母: 2 张卡标 owner_gate_required: true」未加引号，
  `list(yaml.safe_load_all(text))` 报 mapping values are not allowed here（line 26, column 34）。HEAD 侧不是"也坏"，是**根本没有这个件**，
  与本节 findings#7「04 区整区未落 HEAD」同源，且比原判更硬：呈批真源既不在 HEAD、字节又不可机读。
- **交付面影响**：本班袋 q-20261015-st-qoder-p06-1015-01-0001（ledger 451919102a44／checkpoint 96b202ddd19e）含旧句，本班按同会话后袋做严格超集法重投
  （本更正块追加在旧节之后，旧文逐字保留，删除集＝空）；下班读到 dead/duplication 信号时按超集版为准，勿重写 06:36 节。
- **自检两轮（本块）**：R1＝更正前先用 rc/长度/行号三点独立实测（非转述自家旧文）；R2＝写后读回，按「## 」切块 Counter 比对旧面 4 块全 verbatim 在内、新增 1 块、删除 0。

## 10-15 07:25 · st-qoder-p06-1015-03 · ⑥制卡席（领到首件 [对照] 申请三臂→新建对照卡 4 张全翻 preregistered＋呈批草稿 OD-14 寄存＋骨架卡面零填续判）

**领卡与实测分母**（写卡前本进程逐件 yaml.safe_load）：exam_cards 531 文件 531 解析零坏件；status=preregistered 187／empty 186／blocked_on_data 64／examined 55／blocked_on_impl 39。empty 面 186/186 仍是 generated 裸骨架，**具名 empty=0** ⇒ 本班无"抄门柱转正骨架卡"可做（与前两班同实测）。
本班真实领用＝**首件到料的 [对照] 申请**（`docs/_working/automation_campaign/feedback/to_impl.md` §2，2026-10-15 ⑨席 st-qoder-p09-1015-02；前两班实测该册仍是空册模板，本班实测已有三臂申请）。对象＝2 张具名在册冻结卡 TDM-E-L3-07-3/calibration/02_二十日动量排名、TDM-E-L9-A01/calibration/02_日线动量截面。champion 分数面本班逐行实测复核：rows[73] verdict=fail（ic_mean=-0.0277／ic_ir=-0.178／**mono_spearman=null**／n=1621）、rows[74] verdict=fail（ic_mean=-0.0406／ic_ir=-0.256／**mono_spearman=null**／n=1601）。

**产出 4 张对照卡（全部 status=preregistered）**：

| challenger 新卡（ASCII 名，card_id 与文件名逐字互推） | champion | 唯一变量 | 变量取值逐字抄源 |
|---|---|---|---|
| entry_flow/L3/TDM-E-L3-07-3__calibration__03_target_close_to_close_control.yaml | L3-07-3/calibration/02 | 目标收益可成交口径 | L9-A01/02 的 target.primary + data_binding.target_source |
| entry_flow/L3/TDM-E-L3-07-3__calibration__04_universe_no_filter_control.yaml | L3-07-3/calibration/02 | 宇宙预筛（去 universe_rule，改挂 exclusions） | L9-A01/02 的 data_binding.exclusions |
| entry_flow/L9/TDM-E-L9-A01__calibration__04_universe_st_and_age_control.yaml | L9-A01/calibration/02 | 宇宙预筛（加 universe_rule） | L3-07-3/02 的 data_binding.universe_rule |
| entry_flow/L9/TDM-E-L9-A01__calibration__05_target_t1o_to_t2c_control.yaml | L9-A01/calibration/02 | 目标收益可成交口径（臂 a 反向腿） | L3-07-3/02 的 target.primary + data_binding.target_source |

三臂去向：**臂 a**=2 张（正向腿＋反向腿，补反向腿才使两卡读数可同尺并排）；**臂 c**=2 张（⑨席原话"互为对照"，两向各一张）；**臂 b**=0 张→OD-14 呈批（实测理由见 findings 5，一个数未编）。

**制卡纪律（逐字节 clone＋定点替换，非重写）**：基线取 champion 的 `git show HEAD:` 面（该面 status=preregistered、lineage.run_id/score_row=null，正是"冻结未考"态；champion 本体在工作区/index 的 "M " 字节是⑨考工席在途翻转，本席零触碰、未代投）。每张新卡只改 identity 四件（card_id/title_zh/preregistered_by/preregistered_at）＋该臂唯一变量键，另加 arm_protocol/control_provenance 两个溯源块（非判据面）。抄源值由程序对 HEAD 版对照卡做 safe_load 后按字段直读注入，本席未手抄一个字。

**骨架卡门柱面本班零填（决定＋承重证据）**：本班复测 generate_exam_card_skeleton.py --check＝tdm_nodes 186／drift 6／identical 180／missing 0／protected_manual 0，与 1015-01 班复位后读数逐项同值；生成器 `_load_human_fields` 保留面七键不含 pillars_numeric（OD-12 在册实测）⇒ 往骨架卡抄数值门柱＝易失面，且每抄一次多一条 --check 漂移连坐他人提交。本班四件新卡全为具名卡、不在这 186 骨架面内，本班跑后 drift 仍 6＝**本班零新增漂移**。1015-02 班 8 张待落面本班未触碰。

**呈批通道复测（第三班连续受阻，本班实测）**：新真源 `docs/04_research_records/mining/ledgers/nightmine_20261010/05_owner_decisions.yaml` 经 `git cat-file -e HEAD:` 判＝查无、`git status`＝AM（整个 04 区只在 index）；旧真源 `docs/_working/nightmine_campaign/05_owner_decisions.yaml` HEAD 有件而盘面目录已不存在（ls: No such file or directory）。⇒ OD-11/12/13 继续寄存本台账（正文见 10-15 06:36 节，下班照抄即可，本班不重复抄写以免双份漂移），本班新增 OD-14 一件同样寄存：

```yaml
- id: OD-14
  项: ⑨席对照申请臂 b（选股面改 TopN 而非全截面 rank-IC）在"判据与阈值一律沿用卡面冻结值"约束下无可抄机判键——请批读数面口径
  实测分母: 本班对全 535 卡（含本班 4 新件）逐件 yaml.safe_load 的 buckets.type 值分布——有值卡 349 张、distinct type 87 种，
    最大档 quantile_decile 104／ablation_arm 32／event_flag_two_state_contrast 24／quantile_quintile 24／arm_comparison 21／
    arm_matrix 17……**零"TopN 选股面"专用 type**；全册 type 值含 champion_challenger 者仅 1 张
    （TDM-P-P1-05/shadow/05_组合体检帽影子对照，键集=maxdd_regression_max/sharpe_delta_min/turnover_or_cost_gate/
    oos_same_sign/evidence_min_days，属 shadow 族另一键集、非个股截面 IC 面）；numeric_face_mapping_note 非空 33 张
    （1015-02 班按 comparison 族计 23 张，本班按全册计 33 张，两个数各自口径在册）；champion 两卡机判读数 mono_spearman 全为 null
    （rows[73]/[74] 本班实测）⇒ 在册五键里连单调面都无机读源，再换读数面会同时失去两项机判
  为何要点头: 三条出路代价不同——(a) 立法"TopN 选股面读数仍以既有 ic_mean/ic_ir 五键为判据、只把截面读数限制在 Top10/20/30 档内"
    ⇒ 本席可即时出 challenger，但 buckets.on 需一句独立 TopN 口径串，而 champion 原文只有"20 日涨幅截面十分位（另按 Top10/20/30 三档）"
    的附属子句，拆写＝本席自拟口径（本席拒做）；(b) 新建 TopN 专属 numeric 键（如 topn_excess_vs_universe_min）＝全仓零阈值源，
    等于让 AI 编一个数，违 SOP §3⑥"一个数不编"；(c) 臂 b 挂到 OD-1 对照/消融执行器立项（已批、施工中）落地后再考。属判据口径挪动，本席不自裁
  不点的后果: ⑨席三臂只落两臂（a/c 已落 4 张），臂 b 每次到料都被停手；"选股面 vs 全截面"这条最常用的对照线在生产线上持续空转，
    且下游会把"已收到三臂申请"误读为"三臂都已冻结"
  凭据: 本班 07:25 节三臂去向表；to_impl.md 2026-10-15 ⑨席 [对照]申请单臂 b 原文；exam_scores_v1.yaml rows[73]/[74] metrics 面实测；
    全 535 卡 buckets.type 与 numeric_face_mapping_note 本班逐件解析计数
```

**findings（本批实测，非转述）**：
1. **lock_files 命名闸与 exam_card 同族命名口径互斥**：新建 `TDM-E-*__calibration__NN_*` 卡名必吃 N-01（连续大写）＋N-13（含连字符）——本班四张新件在 acquire 阶段 4/4 被拒（实测 BATCH-SUMMARY acquired=0 denied=4）。而提交侧 GATE-NAMING 的机器判据按 gate_registry.yaml 第 73-76 行原文＝"增量 N-16：只阻断本次 staged 文件引入的新重名"，N-01/N-13 风格面走 warn-only 的 GATE-NAMING-AUDIT。⇒ 本班走 lock 侧在册显式逃生口 --skip-naming-check（lock_files.py:589 注释原文"skip_naming_check 保留（显式逃生口，测试与特殊场景已在使用）"），理由＝新卡必须沿用同族存量命名才可被考试器与⑨席"card_id↔文件名精确互推"口径（to_impl.md 修改单 修②）消费。此为制度冲突面，正解＝⑤/⑩席给 exam_cards 目录立命名豁免登记，本席不自改闸。
2. creation_token 日期后缀取 **UTC**：本地 07:1x-07:2x 登记四条，token 尾全部 `-20261014`（非 20261015）。登记结果 4/4 OK（后三条实测 publish_snapshot v808→v809→v810 连续推进），投影面净 +4 条／删 0（before/after 逐 file 键集差分实测）。
3. **热册不随袋提交（归属篡改防线）**：capability_canonical_file_registry.yaml 工作区面比 HEAD 多 4911 条、index 面比 HEAD 多 81 条（均他会话在途），本班不把它放入 --files 清单（袋=整档快照）。CREATE-GUARD 有 T4 PG active 正证通道（create_guard.py:1394 注"投影三级面判缺者，再问一次 PG 账本"），token 已在 PG ⇒ 卡片可先落。若本班袋仍因 CREATE-GUARD 死，死因即"serializer 面读不到 PG 正证"，下班按 dead_reason 处置，禁改判据。
4. 能力反查时序自犯：本班 capability_lookup.find() 跑在首张卡落盘**之后**，违根宪法 §0 第 4 条"写第一行业务代码前"。留痕 `.runtime/lookup_audit/st-qoder-p06-1015-03.jsonl` 5 行：考试卡／对照卡／champion challenger 配对／pillars_numeric 命中 0/0/0/0，同尺正对照 creation_token=1（零命中≠尺断）。如实记档、不重做、不美化。
5. 臂 b 无可抄源的实测：见 OD-14 实测分母（535 卡 87 种 buckets.type 零 TopN 专用档；champion_challenger 型仅 1 张且属 shadow 族另一键集；numeric_face_mapping_note 全册 33 张）。
6. 并发流转实测（非本席所造）：本班写后复测卡池 535 文件＝preregistered 183／examined 63／empty 186／blocked_on_data 64／blocked_on_impl 39——本班 +4 新件（全在 preregistered），同时**另有 8 张 preregistered→examined 由考工/判卷班并发翻转**；工作区另有 8 张 `TDM-E-L1-S2__calibration__40..47` 处 " M" 在途、champion 两件在 index "M " 在途、本席 instruction.md 在 index "M " 在途（⑩线长改指令面）——本班清单零触碰这些件。
7. **本班再次自犯并当场纠正（同一坑二次踩，结构计数救场）**：修台账正文时用"下一行开头短语"作 Edit 锚点，把 findings 6 的正文从锚点后截断（该条一度只剩标题），且内联代码里的换行转义在 Python 普通字符串中被展开、凭空多出一个节标题行。两次都靠写后 `^## ` 与 `^6. ` 结构计数＋逐行读回抓到，本节为整节重建版（重建法＝按节标记截尾后重拼，前缀逐字节断言不变）。教训升级版：**追加与更正一律整节重建，禁以内联代码或行首短语作锚点；文本 grep 全绿救不了节级损坏**（在册坑 edit-append-anchor-consumes-heading 的反向形态）。

**自检两轮**：
- R1（门柱与冻结值逐字一致）：四张卡逐件与 champion 的 HEAD 面做 leaf 级 dict 差分，改动键集合实测＝identity 四件＋该臂唯一变量键（03/05＝target.primary+data_binding.target_source；L3-04＝data_binding.universe_rule→data_binding.exclusions；L9-04＝＋data_binding.universe_rule），unexpected 集合四件全空；pillars_numeric/window/buckets/hypothesis/signal_derivation 与 champion 全等（脚本逐件打印 True）；yaml.safe_load 4/4 通过；对照卡 diff 恰一个变量＝已机械自证（VERDICT CLEAN cards=4）。
- R2（归属·净零·保底·盘外核实）：本席清单＝4 新件＋本台账＋游标，逐件 git status 实测他人件零混入；净零＝零新 gate／零新脚本入册／零新规则册（普查与制卡脚本落 `.runtime/tmp/p06_1015_03/`）；投影删集为空；保底＝**4 张翻转 preregistered ＋ 1 件呈批（OD-14）＋领用面 100% 处置**（三臂 a/b/c 全有去向：2+2 卡、1 呈批；骨架 186 张按 OD-11/12 在册停手口径不重复领）。
- 写后进程外核实：safe_write_text 带 base sha256 CAS＋纯前缀断言（删除集=空），写后进程外读回逐字节相同；节标题结构计数与 findings 序号连续性逐行复核（1-7 无断号）。
- 本班耗时：07:03 进场（reaper 实测 07:04:23）→ 07:25 起投＝22 分钟（含两次自犯纠正与四件 token 登记）。
## 10-15 08:16 · st-qoder-p06-1015-04 · ⑥制卡席（首吃⑩席派单令→楼1盘口族具名子题卡 7 张全落 blocked_on_data（7/7 候选零遗漏）＋呈批 OD-15/16/17＋骨架卡面零填第四班复证）

**领用与实测分母**（写卡前本进程逐件 yaml.safe_load，540 文件 0 坏件）：卡池开工面 535 张＝preregistered 183／empty 186／blocked_on_data 64／examined 63／blocked_on_impl 39；**empty 面 186/186 仍是 generated:true 裸骨架、具名 empty=0、语义五面（hypothesis/buckets/pillars/target/data_binding）非空命中 0/186**＝与前四班同实测，本班无"抄门柱转正骨架卡"可做（OD-11/12 在册停手口径，不重复领、不重复呈批）。
本班真实领用三件（全部到料于本班值守内，非转述他班）：
1. **⑩席 2026-10-15 第三单 §6 派单行**＝本班首件实派单："③席 7 条候选按 §3 结论分档（WMP 纯新直转；OBI/SLOPE/CANCELL/CLOSEBAND 须写区分面；SPREAD/LARGEFLOW 须写残差化与降级条款门柱），每班 5 张"。上游 7 条候选在册真源=`data/strategy_intake/lane_p0_obi_candidates.csv`（③席 20261015-p03-01 批，8 行含 OBI-001 原行＋OBI-001R 补正行）。
2. **⑨席 st-qoder-p09-1015-04 新到 [对照] 申请 1 条**（对象 TDM-E-L1-S2/calibration/46、47，rows[81]/[82]）＝本班实测该册 07:38 由 07:0x 面新增第四确一节，本班为首个领到它的⑥班。
3. **④席 st-qoder-p04-1015-01 改良情报 3 条**（OBI 顺势挂单对照臂／成交父订单基底／"⑥冻结时须显式登记考的是哪个频率"）——其中对照臂一条实测无 champion 可配（见 findings 3）。

**产出 7 张具名子题卡（全部 status=blocked_on_data，非 preregistered；7/7 候选全覆盖）**：

| 新卡（card_id↔文件名精确互推已机检） | 候选真源行 | 判据面抄源 | sha256 前 12 |
|---|---|---|---|
| TDM-E-L9-A02/calibration/03_obi_l1_imbalance | CAND-P0-OBI-001 | 母卡 L9-A02/02 window＋pillars_numeric 整块逐字 | dd7daad9e80c |
| TDM-E-L9-A02/calibration/04_wmp_deviation_close_pair | CAND-P0-WMP-002（⑩判纯新直转） | 同上 | afe8759bffc9 |
| TDM-E-L9-A02/calibration/05_fivelevel_slope_asym | CAND-P0-SLOPE-003 | 同上 | 1e287b77717f |
| TDM-E-L9-A02/calibration/06_order_evap_proxy | CAND-P0-CANCELL-006 | 同上 | 89033bad1f35 |
| TDM-E-L9-A02/calibration/07_closeband_obi | CAND-P0-CLOSEBAND-007 | 同上 | 373ed8213480 |
| TDM-E-L9-A02/calibration/08_effective_relative_spread | CAND-P0-SPREAD-005 | 窗与 buckets 地板抄母卡 L9-A02/02；残差化三柱＋五键＋target 抄 **preregistered** 件 L9-A06/02 | d9927510c98d |
| TDM-E-L9-A06/calibration/04_tick_rule_largeflow | CAND-P0-LARGEFLOW-004 | window/pillars_numeric/残差三柱/target/buckets 全部逐字抄同节点 preregistered 件 L9-A06/02 | d741eec97ccf |

落位节点=同族真源逐字取：`TDM-E-L9-A02` 的骨架卡 tdm.decision_question 原文=「日内微观结构能否预测次日方向与冲击成本？」（`git show HEAD:…/TDM-E-L9-A02__calibration.yaml`），与 7 条候选对象同问；同族唯一在册冻结件=母卡 `TDM-E-L9-A02/calibration/02_竞价失衡与尾盘冲击`（本班实测该件在 HEAD、工作区零改动）。③席在册锚点亦同向：CAND-P0-CLOSEBAND-007 行自陈"与在册 L9-A02 竞价失衡卡不同窗…判非重复"。

**制卡纪律（程序直读注入，本席未手抄一个字）**：脚本 `.runtime/tmp/p06_1015_04/make_cards.py`＋`make_cards_b.py` 先 `git show HEAD:` 取母卡/同域 preregistered 件与骨架卡、`csv.DictReader` 取候选行，再把 `window` 整块／`pillars_numeric` 整块／`buckets.type+min_obs_per_bucket`／`signal_kind`／`discipline`／`oos_window_ref`／残差化三柱／`target` 的原对象写入七卡，候选 `definition_zh/sample_window/example_value/orthogonal_gate_note/birth_batch` 逐字段原文入卡；本席自写的只有 title_zh、buckets.on 的信号命名串（无数值）、区分面叙述与 gaps 键。**零自拟数值、零算术、零四舍五入**：03-07 号卡继承 L9-A02/02 的 6 个数值（mono_spearman_min 0.6／ic_mean_min 0.02／ic_ir_min 0.3／regime_same_sign false／oos_same_sign true／impact_curve_min_ratio 2.0），08/04 号卡继承 L9-A06/02 的 5 个数值（同前三键＋regime true／oos true），含一个本班发现越机判词表的键（impact_curve_min_ratio）也不删不改（删=挪门柱=loosening，在册原则"保守口径只紧不松"）。
**status 判 blocked_on_data 而非 preregistered 的承重证据（本班 CH 自测，非转述③席）**：`c1_market.tick_depth_5` min/max(toString(trade_date))=2026-07-24/2026-10-14、count()=130,283,635、uniqExact(trade_date)=24、uniqExact(symbol)=8,763；`WHERE trade_date<'2025-09-09'` count()=**0 行**；窗内 uniqExact(trade_date)=24 ⇒ 母卡 IS 2026-01-05..2026-06-30 在本表结构零行。与③席§一表读数逐项同值＝双证。七门槛⑤ 要求信号天数≥120 日，实测 24<120 ⇒ 不可达，此即③席判"配额前提不成立"的同一事实。

**呈批三件 OD-15/16/17**（04 册第四班不可写，正文寄存本台账；实测见各条分母，一个数未编）：

```yaml
- id: OD-15
  项: ⑨席 1015-04 班 [对照] 申请（L1-S2/calibration/46、47 的"OOS 切 IS 同号段/反号段两段"）在卡池无任何在册机读源——请批切段口径或另派⑤席扩执行器
  实测分母: 本班对 535 卡逐件 yaml.safe_load 的 window 顶层键集普查＝regimes 349／frozen_note 348／in_sample 347／oos 347／
    event_windows 7／warm_start 4／right_edge_note 3／stress 2／recent_oos 2／long_window_secondary 1／window_reality_note 1／
    window_lineage 1／multispan_reading_note 1，其中 oos 为"多段列表"形者 **0 张**；pillars_numeric 键集 Top30 无任一分段 OOS 键
    （oos_same_sign 324 为单一布尔，event_oos_gap_same_sign 24 属事件研究族）；46 号卡 window.regimes＝bull 2019-01-04..2021-06-30／
    bear 2021-07-01..2024-01-31，与 OOS 2026-04-03..2026-10-12 零重叠；OOS 窗内确有 36 种在册日期（最多 2026-09-30 见于 101 卡）
    但全部是他卡自身 IS/OOS 端点，非本族 holdout 的在册切段（借来即用＝本席自拟口径）
  为何要点头: 在册先例只到"双窗同验"（TDM-X-S1-02/03__comparison__02_dualwindow 的 stress＋recent_oos，裁定#505 B2 口径查证收口）
    与"长窗副面"（L2-01/ablation/03 的 long_window_secondary），两者都是**整段命名窗**，没有一张卡定义过"按 IS 段符号把 OOS 再切两段
    分别复量 oos_ic 符号"；机判面也无该形态的键。三条出路——(a) Owner/⑨席给一段在册切段规则（含日期或段名＋新 numeric 键名与阈值），
    本席即可照抄出 challenger；(b) 派⑤席扩执行器与词表（⑨席修⑦已在册：event_oos_gap_same_sign 腿在非 v2 路缺位，13 行方向否决不可见）；
    (c) 臂改判为"OOS 半段预演"另立呈批。择一即定判据形状，本席不自裁
  不点的后果: ⑨席这条对照线每班到料每班停手（本班已停一次）；"族时段失稳 vs OOS 窗构成"两种死因继续无法分离，
    L1-S2 族 8 行 agg8 负结果的归因卡在"判不了"，下游按"已收申请"误读为"已冻结对照"
  凭据: to_impl.md §2026-10-15 st-qoder-p09-1015-04 §3 申请单原文；本班 535 卡 window/pillars_numeric 键集普查
    （.runtime/tmp/p06_1015_04/scan_oos_split.py 与 census.json）；46/47 号卡本体 window 块
- id: OD-16
  项: SPREAD-005/LARGEFLOW-004 的残差化柱与列级分档已有源可抄（本班已据此成卡），仍缺两档数值——单笔额分档阈值与价差档位截面分位；另 LARGEFLOW 引用的 L7-A06 在卡池零卡（引用面属台账不属卡）
  实测分母: 本班首测曾误判"money_flow 族零残差柱"（见 findings 11 自犯纠案），复核实测＝**TDM-E-L9-A06/calibration/02（status=preregistered）带残差化三柱原文**：
    orthogonalization=『信号必须先对当日 pct_change 与 20 日动量做横截面回归取残差；主判据只在残差序列上算（否则与本车道 A01 动量卡重复计分）』、
    response_monotonicity=『残差分桶中位前向收益 Spearman 单调 rho>=0.6』、raw_vs_resid_gap=『原始信号 IC 与残差信号 IC 之差登记入台账』，
    pillars_numeric=标准五键（0.6/0.02/0.3/true/true），window=IS 2021-01-04..2023-12-29／OOS 2024-01-02..2025-09-09＋熊/修复两段替代（frozen_note 自陈 IS 因数据起点内缩），
    在册列级分档口径＝其 data_binding『备用列 super_large_net_inflow_pct / large_net_inflow_pct 各单跑一版』⇒ 本班两张卡的残差柱/五键/target 全部据此逐字抄成，零自拟；
    仍无源者两条＝①LARGEFLOW 主腿定义里的"单笔额≥分档阈值"（③席在册原文『分档阈值禁自拟 须沿用在册 money_flow 分档口径或解锁窗内实测分位』，而在册只有**列级**分档，无**单笔成交额**阈值；
    全池含"残差/residual"文本卡 22 张（本班完整 walk 计数，非截断打印），其中给单笔额阈值的＝0）；②SPREAD 有效相对价差的档位分位（同上禁自拟）。
    另 node_id=TDM-E-L7-A06 的卡全池 **0 张**（③席所引"L7-A06 门柱教训"活在 L7_ledger 台账面，且 04 区未落 HEAD）⇒ 等价卡面源只有 L9-A06/02
  为何要点头: 三条出路——(a) Owner/⑨席给单笔额分位阈值（如"当日成交额前 X 分位"）或批准以 money_flow 列级分档（super_large/large）替代主腿定义，本席即可把 04 号卡从 blocked_on_data 改判可考口径；
    (b) 派⑤席用 money_flow 替代腿（③席实测切点前 1,136 交易日/5,504,375 行可达）跑实测分位并落册，本席照抄；
    (c) 维持现档（两卡带 gaps_no_source 停 blocked_on_data）。择一＝判据形状，本席不自裁。另须同批裁一处**在册母卡自带的静默风险**：
    ⑨/⑤席在账面（memory 卡 money-flow-caliber-breaks）报过 money_flow 的 close/pct_change 全段恒 0 ⇒ A06 残差化门柱可能空操作；
    本席未复核该读数（本席只读卡面，未查库），若成立则本班两卡抄的 residualization 柱与母卡同受此险，属⑤/⑨实测面，本席不据此改判据也不据此免判
  不点的后果: 两条候选每班只能停在"具名但不可考"；LARGEFLOW 撞面（与 A06/02、L3-12-1 同假设）无单笔额级防线，一旦开考即与当日涨幅机械共线，IC 不可解读；
    ①②席补史也无处挂阈值
  凭据: 本班两卡 prereg_provenance.copied_verbatim_from 逐件列源；git show HEAD:…L9-A06__calibration__02 的 pillars/pillars_numeric/window/data_binding/target 整块实读；
    lane_p0_obi_candidates.csv CAND-P0-LARGEFLOW-004/SPREAD-005 两行原文；派单册第三单 §6 行原文；.runtime/tmp/p06_1015_04/verify_r1b.py 逐柱比对读数
- id: OD-17
  项: 盘口族具名卡三处语义面无源（五键适用性待裁／母卡第 6 柱越机判词表／两候选 target 未声明）——请批族级判据形状
  实测分母: ①本班 03-07 号 5 卡的 pillars_numeric 只能继承同族唯一冻结件＝母卡 L9-A02/02，而母卡 status=**blocked_on_data**（不在 1015-02 班自设"在册冻结件=status∈{preregistered,examined}"口径内，
    亦不在 OD-13 多口径清单内）；本班 08/04 号两卡改用同域 **preregistered** 件 L9-A06/02 为源，故同一楼内出现"blocked 源"与"preregistered 源"两制并存；②③席微缩链 10-15 02:53 节在册原文"候选方向=OBI 均值对次日收益的预测力门槛沿用族内在册五键
    （mono_spearman_min=0.6/ic_mean_min=0.02/ic_ir_min=0.3），**是否适用盘口类待裁定**"＝适用性至今未裁；③母卡 pillars_numeric 第 6 键
    impact_curve_min_ratio=2.0 属冲击成本曲线柱，本席逐字继承进 5 张不含冲击面 target 的新卡（保守只紧不松），但该键是否在机判词表内本班未读到代码级结论；
    ④CAND-P0-WMP-002 与 CAND-P0-CANCELL-006 两行未声明 target（definition_zh 只写主判据面），本班 target.primary 置 null 并如实写 gaps，禁自拟对象
  为何要点头: 三件都是族级判据形状，不是本席可拍的实现细节——盘口族若要进主线，须先裁"沿用 IC 五键还是另立键集"（与草稿#3 的
    comparison/ablation/shadow 族键集错位同题不同面：草稿#3 是已考族读数面错位，本条是未入族的前置立法）；
    target=null 的卡可否长期留在卡池、以及 blocked_on_data 卡的"冻结"称谓是否成立，关系⑩席"转正率"读数的口径
  不点的后果: 本班 7 卡会一直停在 blocked_on_data（不消耗开考配额，也不产出），⑩席按"5 张处置"计的转正率与⑦⑧席按 preregistered 计的供题面将长期背离；
    盘口深史补采（③席§六.2 新断供登记）无卡可挂，①②席收不到具名对象
  凭据: 母卡 TDM-E-L9-A02/calibration/02 与同域件 TDM-E-L9-A06/calibration/02 本体逐字段；③席 10-15 台账§一/§六；⑤席在册记忆卡 exam-shard 三道闸（待代码级复核，本席未采信为判据）；
    本班七卡 gaps_no_source 键原文
```

**findings（本批实测，非转述）**：
1. **⑩席派单前提被上游实测证伪，本班处置＝按实测落态而非按派单字面**：派单 §6 给⑥"每班 5 张"，隐含"候选可转成可考卡"；③席§一实测 tick_depth_5 仅 24 交易日且切点前 0 行（本班 CH 复测同值），门槛⑤(≥120) 结构性不可达，并 §六.4 请⑩席改派单口径。本班既不停手也不硬凑 preregistered：7 张具名卡全落 blocked_on_data，把"定义已具名、数据面堵"这一态如实入账（**配额 5 张已超额达成＝7 张成卡，可考面为零**——两面分列报，不合并报功）。
2. **本班是新口径首例：同族唯一在册冻结件本身是 blocked_on_data**。1015-02 班自设一致性判据把"在册冻结件"限定为 status∈{preregistered, examined}，按该尺本班 5 卡的窗/五键全无源；本席改用"同 node+同 family 唯一冻结面逐字继承＋继承声明入 prereg_provenance"。此口径差请⑩席对表（属计数口径，不属判据数值，本席不自改他班尺子）。
3. **④席改良情报 1 的对照臂实测无 champion 可配**：该条要求"把『顺势 OBI 挂单』作为对照臂提交⑥配对"。本班全池正则实测（含正对照）＝卡池零 OBI/一档失衡具名卡（OBI 图案命中 0，正对照 tick_depth 命中 10、竞价失衡命中 1），且该条自陈"落地权在⑤"⇒ 配对前置=⑤席先物化 OBI 信号面。本班 03 号卡把④席的两条构造约束（斜率与深度成反比⇒须除以深度；预测力随聚合频率衰减⇒须显式登记考的是 3 秒快照→日均这一频率）**逐字写进假设面**，即该情报的卡面登记义务已完成，对照臂本体待⑤。
4. **查重尺带正对照，零命中判得住**：OBI 一档失衡／WMP 中间价／有效相对价差 三族正则命中 0；正对照同批实测 tick_depth=10 件、竞价失衡=1 件（尺未坏）。五档压力梯度命中 1＝L9-G2__ablation__02（blocked_on_impl，对象为 CKG 静态事实层先验增益，非同对象）；"挂单/蒸发/撤单"命中 8＝全部属执行段/成本段策略卡，本班按⑩席 §3 更正行（"正确口径是零盘口**信号**卡"）在 06 号卡写明区分面，未自判重复也未自判非重复。
5. **CLONEGUARD L0 对本席无对象域，替代取证已做**：`check_before_write` 只活在 `zephyr.clone_guard.mcp_server`（该包 __init__ 自述"L0 MCP check_before_write 是 advisory 不阻断""MVP(Phase A) 仅调度 Echo-Guard"＝代码克隆/函数提取域），本班产物是 YAML 数据卡，非其判据对象；故本班以 findings 4 的查重尺＋正对照作等价取证，如实记此偏离而非谎称已过 CLONEGUARD。
6. **骨架卡面零填第四班复证，且上游"8 张已填"从未落地**：`generate_exam_card_skeleton.py --check` 本班写前写后同值＝{tdm_nodes:186, drift:6, missing:0, identical:180, protected_manual:0}（本班新增 5 张具名卡**零新增漂移**）；写后复测 empty 面 `EMPTY_WITH_ANY_SEMANTIC=0`⇒1015-02 班填的 8 张骨架卡门柱至今不在盘面（其袋 -02-0001 仍 pending，字节活在队列 blob），OD-12"骨架卡是易失面"再获一证。
7. **呈批真源两头第四班同堵（本班逐路实测）**：新真源 `docs/04_research_records/mining/ledgers/nightmine_20261010/05_owner_decisions.yaml`＝`git cat-file -e HEAD:` 查无、`git status`＝`A `（整 04 区 97 件只在 index）；旧真源 `docs/_working/nightmine_campaign/05_owner_decisions.yaml`＝`git cat-file -e HEAD:` 有件（OLD_IN_HEAD=YES）而 `ls docs/_working/nightmine_campaign/`＝No such file or directory（归档波已删盘面）。⇒ OD-11..17 共 7 件全部寄存本台账，注入面仍未开。
8. **本席队列卫生**：p06 四袋全 pending 零 dead（-01-0001 2 件／-01-0002 1 件／-02-0001 10 件／-03-0001 6 件，逐目录 walk 实测），无当日四态分诊欠账；全队列 pending 93／processing 2／done 774／dead 121（本班只读不动他袋）。
9. 锁与命名闸第 N 次复证：`lock_files.py acquire` 对本班 5 个新卡名 4/4→5/5 吃 N-01/N-13，走在册逃生口 `--skip-naming-check`（卡名必须沿用同族 `TDM-E-*__calibration__NN_*` 才能被考试器与⑨席"card_id↔文件名精确互推"消费，本班已把该互推写成机检项，见 R1）。
10. 热册与投影：`batch_creation_tokens.py` 逐件前缀登记 **7/7 OK**（token 尾日期取 UTC＝-20261014，非本地日）；投影 `capability_canonical_file_registry.yaml` 七件登完后实测键集＝HEAD 15,283／盘面 20,208，**deleted_vs_head=0**、added 4,925（含本班 7 件，`mine_in_disk=7` 逐件核名）；该 4,925 条绝大多数是他班在途条目，**本班不随袋**（袋=整档快照，随袋即归属篡改）。CREATE-GUARD 正证另走 T4 PG 通道。

11. **⚠本班自犯并当场纠正（在册老坑第 N 次复发＝拿截断打印当全集，导致一条假"无源"结论差点进呈批）**：本班第一次扫"残差×money_flow 交集"时，用 `print(... )[:12]` 截断输出便据此写下"money_flow 族零残差柱、SPREAD/LARGEFLOW 只能呈批"，并已把该写法写进 OD-16 初稿。复核契机＝读到在册记忆卡 money-flow-caliber-breaks 提到"A06 残差化门柱"，本班遂按 node/family 精确交集重跑（不截断）⇒ 实测 **TDM-E-L9-A06/calibration/02（preregistered）带残差化三柱原文**，判据形状有源。处置＝OD-16 全文改写为"两柱有源已抄成卡、仍缺两档阈值"，并据此**补制 2 张卡**（08/04 号），领用面由"5 成卡＋2 呈批"变"7 成卡＋0 呈批"。教训升级版：**跨集合判"零交集"必须先完整物化两个集合再取交，禁按打印面板前 N 行外推**（同族在册坑 observer-created-signal-grids-and-tail-counts、zero-hit-ruler-needs-known-positive-control 的第三种形态：这次不是尺坏，是我把尺的显示面当成了尺的读数面）。
12. 本班值守内上游到料两条（非账面引用）：to_impl.md 07:38 由 ⑨席 1015-04 追加第四确一节（新 [对照] 申请 1 条＋修⑨/修⑥/修⑧＋呈批 P-4），本班为首个领到它的⑥班；p03 台账 07:44 由 ③席 1015-01 收尾（7 候选在册面定稿），本班据此派单 §6 成卡——两席台账均只读未改。

**本班实际耗时**：date 实测 07:35:20 开班（reaper 首读时戳）→ 08:12:35 卡面终测完成＝37 分钟 → 08:16:28 台账落盘＝**41 分钟**（SOP 3-B 估⑥席 20 分＝偏差 +105%，主因＝①上游 07:38/07:44 新到料后重定领用面 ②CH 取证与 7 件 token 登记串行 ③本班一次自犯纠案重扫＋据此补制 2 卡；如实记账，不改估时基准）。

**自检两轮**：
- R1（门柱与冻结值逐字一致＋单变量核对）：`.runtime/tmp/p06_1015_04/verify_r1.py`（03-07 号，逐卡 11 项）＋`verify_r1b.py`（08/04 号，逐卡 10 项，含"残差化三柱逐柱原文相等"与"target 三面逐字相等"）＝**7/7 全 CLEAN**——window 整块与所抄源 HEAD 面 JSON 全等、pillars_numeric 整块全等、buckets.type+min_obs_per_bucket 全等、oos_window_ref==源卡 window.oos、discipline/signal_kind 全等、card_id 与文件名互推相等、status=blocked_on_data、无 generated 键（非骨架）、node_id 正确、假设含③席候选行原文标记；yaml.safe_load 7/7 通过。**对照卡 diff 项＝本班 N/A**：本班唯一领到的 [对照] 申请（⑨席 46/47）未成卡（OD-15 停手），故"diff 恰一个变量"无可核对象，此项如实记 N/A 而非记绿；本班 7 卡是新造具名卡（非 champion/challenger 配对），与源卡差异面=信号对象本身，已在各卡 prereg_provenance.single_variable_note 声明。
- R2（归属·净零·保底·进程外核实）：`git status -- …/entry_flow/L9` 实测＝本班 7 件全为 `??`（新件），他班在途件（L9-A01/02 处 `M `、A01 __04/__05 处 `??`）本班清单零触碰、零吸收；卡池写后 542 张＝blocked_on_data 64→71（恰本班 +7），preregistered 183／empty 186／examined 63／blocked_on_impl 39 四态零变＝本班未改他班卡面一字；骨架 --check 写前写后恒 {drift:6, identical:180, missing:0}＝**本班零新增漂移**；投影净删 0；台账追加走 safe_write_text CAS＋纯前缀断言（删除集=空，写后进程外读回）；净零＝零新 gate／零新脚本入册（普查与制卡脚本留 `.runtime/tmp/p06_1015_04/`）／零新规则册／零新注册表；保底＝**7 张成卡（配额 5 张，超额）＋3 件呈批（OD-15/16/17）＋领用面 100% 处置**（③席 7 条候选＝7 成卡，零遗漏；⑨席 1 条 [对照]＝呈批 OD-15；④席 3 条情报中频率登记与深度归一两条已写进 03/08 号卡假设面，对照臂一条实测无 champion 待⑤；186 骨架按 OD-11/12 在册停手口径不重复领）。

## 10-15 08:46 · st-qoder-p06-1015-05 · ⑥制卡席（③席 p03-02 批 5 新候选逐条处置→新卡 2 张＋不立卡裁定 2 条＋前置事实入卡 1 条／②席解锁面首翻 A17/02 blocked_on_data→preregistered／呈批 OD-18..21 四件）

**领用与实测分母**（本班写卡前逐件 `yaml.safe_load`，542 文件 **0 坏件**）：卡池面 542 张＝preregistered 184／empty 186／blocked_on_data 71／examined 63／blocked_on_impl 38。
**empty 面 186/186 仍是 `generated:true` 裸骨架、具名 empty=0**＝与前四班同实测（第五班复证），按 OD-11/12 在册停手口径不重复领、不重复呈批。
**与上班（st-qoder-p06-1015-04 08:16 写后读数 183/186/71/63/39）逐态对表**：preregistered +1／blocked_on_impl −1，其余三态零变。本班按 `git diff HEAD` 逐件定位该 ±1＝`TDM-P-P1-03/comparison/03_逻辑存活否决腿开闭对照` 一件由 blocked_on_impl 翻 preregistered（他会话在途面，本席未触碰、不代裁、不随袋）；另 10 件 preregistered→examined 的盘面差（L1-S2 40..47 八件＋L3-07-3/02＋L9-A01/02）在上班读数时已存在，故不构成上班计数误差——**账面差全部有主，零悬空**。
**[对照] 申请面零新条**：在册两笔（⑨席 1015-02 三臂＝p06-1015-03 已成 4 张对照卡；⑨席 1015-04 L1-S2/46・47 OOS 切段＝OD-15 停手在册）；本班无配对制卡对象⇒自检"diff 恰一个变量"项如实记 **N/A**（不记绿）。

**本班真实领用四件**（全部到料于本班值守内或上一班未领面，逐条实测非转述）：

1. **③席 20261015-p03-02 批新 5 条候选**：真源 `data/strategy_intake/lane_p0_obi_candidates.csv` 本班实测 **13 行**（上班成卡时台账自述 8 行/7 候选）。新 5 行＝CAND-P0-MFGAP-008／MFBRD-009／MFDSP-010／MFCAL-011／SEAL-012，`birth_batch` 逐行等值 20261015-p03-02；卡池全 542 件按 MFGAP/MFBRD/MFDSP/MFCAL/SEAL 五图案 name 面命中 **0**（本班完整 walk 计数，非截断打印）⇒ 五条本班为首个领到的⑥班，零遗漏处置：

| 候选 | 本班处置 | 承重判据（本班实测） |
|---|---|---|
| MFGAP-008 | **新卡** `TDM-E-L9-A06/calibration/05_mfgap_inst_retail_direction_gap`，status=**blocked_on_impl** | 对象＝个股横截面 panel（定义逐字『先按 trade_date 截面去均值再排序』），而正交闸在册只计量过其市场级折叠版（reject 0.4429）且横截面版③席自陈"未被计量＝呈批第 1 条"；信号物化腿属⑤（SOP ⑤出口"码面+测试绿→卡翻转 unblocked→移交⑥"）。money_flow 窗内 1,136 交易日可达⇒门槛⑤⑥不阻 |
| MFBRD-009 | **不立卡**＋OD-19 | 定义即市场级单列序列（『当日 countIf(main_net_inflow>0)/count() 的市场级占比』）＝正是闸已计量并判 reject 的对象（max\|corr\|=0.5085>0.3，most_similar=lu_ratio_z20）；SOP §3-G 第 1 条原文"不过闸记'重复'，喂 mined_out 判据"⇒ 准入判决在③/⑩面，本席不为其立可考卡，也不把 reject 读成豁免 |
| MFDSP-010 | **不立卡**＋OD-19 | 同上（市场级 `stddevPop` 二阶矩，闸 reject max\|corr\|=0.3651，most_similar=lu_count）；另③席在册自陈"量级随年份递减 23→13 ⇒ 须与波动率族做共线对拍后才可立项"＝立项前置未达 |
| MFCAL-011 | **不成卡**（③席自标"非信号行（判据面行）…不占正交计量"）＋整行逐字写入 05 号卡 `data_binding.nonzero_sum_correction`＋**OD-18** | 本班独立复测其 (a) 条：`money_flow WHERE trade_date<'2025-09-09'` count=5,504,375、countIf(pct_change=0)=**5,504,375**、countIf(close=0)=**5,504,375**（100%），uniq 日=1,136；正对照同表 countIf(main_net_inflow_pct!=0)=5,490,259／super_large!=0=4,124,403／small!=0=5,504,234 ⇒ 表非全局死、唯两列恒 0＝尺未坏且谓词成立 |
| SEAL-012 | **新卡** `TDM-E-L9-A02/calibration/09_seal_instant_orderflow`，status=**blocked_on_data** | 本班 CH 实测 `tick_depth_5` uniqExact(trade_date)=**24**、rows=130,309,431、覆盖 2026-07-24..2026-10-14、`trade_date<'2025-09-09'` count=**0** ⇒ 母卡 IS 2026-01-05..2026-06-30 结构零行，门槛⑤（≥120 信号日）不可达（24<120）；与上一班 08:1x 实测 rows=130,283,635 同形态（差值＝窗内新增行），uniq 日与零行两读数恒等＝双证 |

2. **②数据建设席 `feedback/unblocked.md` 两节（07:07 与 08:15 班）点名⑥的改判义务**——`TDM-E-L9-A17/calibration/02_研报评级调整事件研究` **blocked_on_data → preregistered（本班翻转，八面零改动）**：
   - 解锁条件是**卡内自己写的**（原文『rating_change 非空率 >=60%、看空类样本 >=300 条；齐备后把 status 改回 preregistered 重冻开考』），本班用**该卡 data_window_evidence 自带的命令形**（加 FINAL）实测：分布＝维持 92,173／上调 19,735／下调 19,522／空串 13,052／首次 2,458；count=146,940、非空 133,888＝**91.12% ≥60%** ✓；下调 **19,522** 条（publish_date>='2022-01-01' 仍 11,324）＝**看空类 ≥300** ✓；与②席在册四态读数逐值同（双证）。
   - 本班另补②席未量的**窗内可考性**（翻转前自证，不靠"列有值"推"卡可考"）：冻结 IS 2019-01-04..2023-12-31 内 下调 9,816 事件/1,766 符号/1,335 发布日、上调 10,218/1,919/1,398；冻结 OOS 2024-01-01..2025-09-09 内 下调 4,753/1,441、上调 4,559/1,391 ⇒ `buckets.min_obs_per_bucket=60` 与七门槛⑥（事件≥30）在**两窗×两组＝四面**全超线。
   - ②席 08:15 节"事件窗建议截到 publish_date<=2026-09-30"对本卡**空操作**：本卡 OOS 末端 2025-09-09 早于该缺口起点 2026-10-01 ⇒ 窗与柱一字未动（若据此改窗＝挪门柱，本席拒绝）。
   - 只动 `status` 一行＋追加 `unblocked_20261015` 块（含命令原文、逐值读数、八面未动声明）；blocked 时代的 `data_window_evidence` 与 `readiness: BLOCKED` **原文保留作旧案卷**（更正另起留旧案卷纪律）。写后自证＝`yaml.safe_load` 前后对比，window/buckets/pillars/pillars_numeric/target/oos_window_ref/discipline/signal_kind **八面 parsed 内容全等**。
   - 同节另三件：`A17/03 一致预期修正`（preregistered，窗与 02 卡同 IS/OOS 串）＝**并存不退役**，本席零动作（退役属 Owner 门位，且两卡对象异：评级变动事件 vs 一致预期修正）；其卡内 `data_window_evidence` 与盘上现值不一致（rows 6,829,376→6,856,034、max 2026-09-30→2026-10-15）＝本班实测窗末端 2025-09-09 不受影响，属证据块陈旧非门柱陈旧，**本班不改已注册卡面**，只登记；`L2-09/02 板块催化剂密度`（examined）②席问"是否依赖 rating_change 做主信号由⑥判"＝本班读卡面答：其 `data_binding.signal_column` 六列并列（industry, rating, rating_change, publish_date, org_name, symbol），未标主信号列，而该卡分数行产出时 rating_change 全表 100% 空 ⇒ **归因义务在⑨席**（旧分数可能吃空列），本席不重冻已考卡、不代⑨改判；`L2-09/03 评级上调聚集`（preregistered）卡内自述"rating_change 列若有值则以其为准并与自算口径对账（差异>5% 先查口径再开考）"⇒ 列已就位＝**对账腿义务已激活**，执行侧检查属⑦⑧（本班为指针登记，不代跑）。

3. **④全网战法矿工席 st-qoder-p04-1015-02 节（to_impl.md 07:45 追加，上一班未领面）改良情报 5 条中点名⑥的 3 件**⇒ 全部**呈批 OD-20/OD-21**，本班未制一张"看似齐了其实是自拟"的卡：该三件的卡面载体在卡池**零命中**（本班完整 walk：名称面 残差动量=0、residual_mom=0、门控反转=0、drift=0、holder_conc=0、smart_money=0、turnover_premium=0；"价差"1 件=TDM-P-P3-04/comparison/03 尾盘加仓执行价差对照、"spread"1 件=L9-A02/08 有效相对价差＝均非④席该族对象），且④席要求的正是**择一即换对象**的五处口径与刻度二选一——无在册冻结值可抄，本席一个数不编。④席 `data/strategy_intake/web_cards/` 九件中四件（holder_concentration 08:24／smart_money_ratio 08:22／turnover_premium 08:25／…）mtime 落在本班值守内＝**在途件，本班不抢读不据以制卡**。

4. **呈批真源两头第五班同堵（本班逐路实测）**：新址 `docs/04_research_records/mining/ledgers/nightmine_20261010/05_owner_decisions.yaml`＝盘面存在 7,062B（mtime 06:31）／`git status`＝`A `（只在 index）／`git cat-file -e HEAD:` **查无**；旧址 `docs/_working/nightmine_campaign/05_owner_decisions.yaml`＝`git cat-file -e HEAD:` **有件** 而 `ls docs/_working/nightmine_campaign/`＝No such file or directory。⇒ 注入面仍未开，**OD-11..21 共 11 件寄存本席台账**（本班新增 OD-18/19/20/21 四件全文见下），随袋该册＝把他人未落地条目一起吃进 commit＝归属篡改，故不为。

**呈批四件（正文寄存本台账，实测分母逐条自带）**：

```yaml
- id: OD-18
  项: 已注册卡 TDM-E-L9-A06/calibration/02（preregistered）的残差化柱 orthogonalization 在本库列面上是空操作——请裁"当日 pct_change"取数源（跨表 JOIN 还是表内列），并裁本班 05 号新卡是否可沿用该柱
  实测分母: 本班 CH 只读实跑 money_flow trade_date<'2025-09-09' ＝ count 5,504,375／countIf(pct_change=0) 5,504,375／countIf(close=0) 5,504,375／uniq 日 1,136（两列恒零覆盖 100%）；
    正对照 countIf(main_net_inflow_pct!=0)=5,490,259、super_large!=0=4,124,403、small!=0=5,504,234（尺未坏）；
    在册母卡 data_binding 原文=『resid = OLS(main_net_inflow_pct ~ pct_change + 20日动量) 的横截面残差，按 trade_date 分组回归；备用列 super_large_net_inflow_pct / large_net_inflow_pct 各单跑一版』，
    其 signal_table=c1_market.money_flow ⇒ 文字面把 pct_change 指向了恒 0 列；上游同向读数=③席 CAND-P0-MFCAL-011(a) 逐年 countIf 五年全段 100%（逐值已入本台账领用面表）
  为何要点头: 该柱是母卡五柱之一且母卡 status=preregistered——改"pct_change 从 kline_daily_hfq JOIN"＝改判据取数面＝挪门柱，只能呈批（本席禁自改、禁自加豁免）；
    而出路 (a) 表内列(空操作)／(b) 跨表 JOIN(改门柱文字)／(c) 该柱整根不判 三择一的判据形状不属本席。三条在册代价：选 (a) 则 A06 族与 05 号新卡的"残差化后才算主判据"防线全部形同虚设，LARGEFLOW/SPREAD/MFGAP 与当日涨幅机械共线的风险（OD-16 在册原文）无人守；
    选 (b) 须同批改 L9-A06/02 与上一班已抄该柱的 08/04 两卡＋本班 05 卡（四处），且母卡已 preregistered＝重冻＝OOS 消费面要另算；选 (c) 则该族主判据退化为裸横截面 IC，与 A01 动量卡重复计分（母卡柱文字自陈的陷阱）
  不点的后果: 卡池至少 4 张卡（A06/02・A06/04・A02/08・A06/05）的残差化防线是纸柱；⑦⑧一旦开考，读数会被当成"已残差化"引用，而实为恒 0 回归量＝静默假绿；
    ①②席收不到"要补哪一列"的具名对象（本表 close/pct_change 是否补派生 vs 改 JOIN，两条路成本差一个量级）
  凭据: 本班 CH 只读实测（命令与逐值见领用面表 1 MFCAL-011 行）；git show HEAD:…TDM-E-L9-A06__calibration__02…yaml 的 pillars.orthogonalization＋data_binding 整块；
    lane_p0_obi_candidates.csv CAND-P0-MFCAL-011 行 definition_zh/sample_window/example_value 原文；在册记忆卡 money-flow-caliber-breaks（⑨/⑤席账面读数，本班已用实测坐实）
- id: OD-19
  项: 个股横截面候选过正交准入闸的折叠口径全仓零源——请裁 MFBRD-009／MFDSP-010 的立项命运（本席判"不立卡"）与横截面族（含本班 05 号卡）的准入计量法
  实测分母: SOP §3-G 第 1 条在册原文『新候选入台账前对独立信号库做 spearman 预检，|corr|≤0.3 才收（工具=scripts/backtest/fexam/signal_orthogonality.py gate 子命令）；不过闸记"重复"，喂 mined_out 判据』；
    ③席三行在册读数逐字：MFGAP reject max|corr|=0.4429 most_similar=lu_ratio_z20、MFBRD reject 0.5085 同 most_similar、MFDSP reject 0.3651 most_similar=lu_count；
    计量对象＝"市场级折叠版"（三行同陈"系 3 个独立轴而非在册 15 员全池"），池真源＝⑨席 pool6 六序列/共同日 1855；
    MFGAP 行自陈『个股横截面版未被计量（闸契约只吃 date,sig 单列，横截面候选无在册折叠口径＝呈批第 1 条）』；
    ⑨席修⑤在册（同文件 20261015-04 节）＝闸侧列名契约不匹配：工具吃 date,sig 而采集面产 trade_date,value（报错原文在册），其建议正解=闸侧一行映射或采集面双写，判据 |corr|≤0.3 不动
  为何要点头: 本席能填门柱（05 号卡已填齐，抄母卡五键与残差三柱），但"能不能进供题面"取决于准入——(a) 认可横截面族暂以"物化＋口径"两缺停 blocked_on_impl（本班现档，零开考消耗）；
    (b) 授权⑤把 MFBRD/MFDSP 的市场级对象重述为个股横截面（＝换题面，须另立候选）；(c) 判两候选按 mined_out 退役（业务资产概念级退役＝Owner 门位）；
    (d) 扩闸契约使其能吃面板二维（属⑤施工＋词表）。本席不自裁：把 reject 读成"这卡不能做"是越权，读成"闸没测到点上所以照做"是越闸——两头都会洗掉可见性
  不点的后果: money_flow 替代腿三条候选每班到料每班停在同一处；⑨席空白轴地图拿不到"资金面轴是否已被占"的结论；
    ③席 p03-02 批的产出一半无法计量（正交性计量口径未定则挖矿产出按数量还是按正交性计=两本账）
  凭据: lane_p0_obi_candidates.csv 五行原文（本班 csv.DictReader 全 13 行读取）；SOP research_production_line_policy.md §3-G 第 276 行；
    to_impl.md 20261015-04 节 §2 修⑤（列名契约报错原文＋pool6 权威输出 n_members=6 n_common_dates=1855 effective_n_signals=2.1272）；
    本班 05 号卡 gaps_no_source.cross_sectional_orthogonality_caliber 原文
- id: OD-20
  项: ④席 p04-1015-02 三件"⑥须落字"的口径自由度——请逐条裁定取值，且其卡面载体尚不存在（须③席先转具名候选入台账）
  实测分母: to_impl.md 第 93 节三行点名⑥：①价差族（SIC-20261015-P04-04）『卡面可用面只两种：横截面 rank(S) 或横截面 rank(α>0 占比)。禁把 bps 裸值写进阈值』＋『β 与 γ 必须先做窗均值再解 α；逐日算 S 再平均…虚高 8 倍』＋两类退化日必剔（high=low 实测 228/116,749=0.20%、停牌日）；
    ②残差动量（P04-05）五处"择一即换对象"自由度＝因子集(CAPM/FF3/FF5/行业/PCA)・截距 α_i 是否计入(主刊排除)・回归窗长与跳过期数・分母是残差波动还是含 1/11 系数变体・是否加卖方"窗内日波动最高子期残差×−1"改进，④席令『改进臂可作对照，禁作主臂』；
    ③状态门控反转（P04-06）『不得用 circ_mv／turnover_rate／流动性列偷顶"价值"』＋『0 收益日在"正收益日占比"里的归属（含或不含）会变阈值读数，须⑥登记规则』。
    卡池载体实测零命中（完整 walk：残差动量/residual_mom/门控反转/drift/holder_concentration/smart_money_ratio/turnover_premium 名称面各 0 件；"价差"1 件与"spread"1 件经本班读卡面判为异对象）；
    ④席 web_cards 面 9 件中 4 件 mtime 在本班值守内（08:22/08:24/08:25）＝在途；数值面：④席给的 W=21、s_true 0/30/60/150bps 阶梯、底噪 5.2bps 皆为其**合成实测**，不是在册判据常数，本席不据以立阈值
  为何要点头: 三件的共同形状＝"先择一，后冻结"，而 SOP 只允许本席抄在册冻结值——在册既无该族五键适用性、也无因子集/窗长/α_i 归属/0 收益日归属的任何一条；
    (a) Owner 或⑨席按判据册给一份"残差动量五自由度＋价差刻度二选一＋0 收益日归属"的成文口径 ⇒ 本席一件成卡；
    (b) 派③席把三张网卡转成 lane 台账候选（带 definition/sample_window/正交面）⇒ 走楼1同款流程；
    (c) 维持现档＝④席情报有登记、卡面无载体（本台账即为登记面）。另须同批裁一处**已注册卡的防伪风险**：P04-06 的"价值腿不可达"若被 circ_mv 顶替，⑨席空白轴地图会把"估值"记成已出分（④席原文判=账面造假），而该顶替动作发生在⑤的物化腿，卡面无人守
  不点的后果: ④席每夜全网挖矿的产出一半落在"情报已送达、卡面无处落字"的悬空面；价差族若被⑤按裸 bps 阈值实现，则按④席实测是在给噪声定门柱（底噪 5.2bps vs 本库均值 7.9bps）；
    残差动量族五自由度不写死＝同一张卡名下一版与另一版不是同一对象，复制账失效
  凭据: to_impl.md 2026-10-15 st-qoder-p04-1015-02 节三行原文（本班逐行读）；data/strategy_intake/web_cards/ 九件目录实测（mtime 逐件）；
    本班卡池 542 件名称面与读卡面双重查重；SOP §⑥ 输入口『只抄在册冻结值…语义参数缺→呈批（一个数不编）』
- id: OD-21
  项: SEAL-012 的两个未赋值量（"维持阈值"与"其后 N 秒"）＋盘口族窗/柱继承源的 status 形态（第五处族级判据形状）
  实测分母: ③席 definition_zh 原文含两处无名量『首次买一量≥**维持阈值**时点为锚』『测**其后 N 秒**买一撤单率与新增挂单率』；卡池与判据册零命中该二值（本班查 L4-05/02 本体＝其 buckets.on『三臂 × 封单质量（seal_ratio 三分位）』、pillars.seal_quality_monotonicity 的 2% 是**封单比**阈值且建在 daban_board_event/limit_up_pool 表上，非 tick_depth_5 买一量维持阈值，不可移用）；
    窗继承面实测＝本班 09 号卡 window 整块抄同 node 唯一在册冻结面 L9-A02/02，而该件 status=**blocked_on_data**（其 window.frozen_note 自陈"短窗预演不作分布性结论，正式考试须待历史补齐后重冻"）；
    同 node 另一制＝L9-A06/02 是 preregistered（上一班 08/04 号卡用它为源）⇒ 同一楼内 blocked 源与 preregistered 源两制并存（OD-17 在册未裁，本班为第五例）
  为何要点头: 阈值与 N 是本卡唯一两个语义数值面，缺它们则卡面"具名而不可判"；本席禁编一个数（③席在册禁自拟纪律＋SOP 一个数不编）；
    出路 (a) Owner/⑨给 维持阈值（如"买一量≥封板时前 M 笔均量的 X 倍"）与 N（秒）的成文值；(b) 派⑤/③席用 tick_depth_5 24 日面实测分位并落册（本席照抄）；(c) 该卡长期停 blocked_on_data（本班现档，不消耗开考配额）
  不点的后果: 楼1 盘口族第 9 张具名卡停在"定义齐而常数缺"；①②席盘口深史补采（③席§六.2 在册新断供登记）到货时，该卡仍不能直接开考（须先补常数）；
    封板瞬间订单流与在册 L4-05/02 打板三式的对象区分只有叙述面防线、没有数值面防线
  凭据: lane_p0_obi_candidates.csv CAND-P0-SEAL-012 行 definition_zh/orthogonal_gate_note 原文；git show HEAD:…L9-A02__calibration__02…yaml 的 window/frozen_note/pillars 整块；
    TDM-E-L4-05__comparison__02 本体 buckets/pillars 实读；本班 09 号卡 gaps_no_source 两键原文
```

**findings（本批实测，非转述）**：
1. **保底两口径分列报**：本班成卡 **2 张**＋翻转 **1 张**＋裁定不立卡 **2 条**＋前置事实入卡 **1 条**＋呈批 **4 件**＝领用面（③席 5 候选＋②席 4 件＋④席 3 件＋[对照] 0 新条＋骨架 empty 186）100% 处置；**可考面新增 1 张**（A17/02），另 2 张新卡按实测停在 blocked_on_impl/blocked_on_data 不消耗配额。
2. **本班首见"卡自己写了解锁条件"的翻转样本**：A17/02 的 status 判据不依赖任何席的转述，而依赖卡内 `data_binding.data_window_evidence.unlock条件` 原文两档——本席据此把"翻转"从主观判断变成机械对表（两档＋窗内四面超线），并把 ②席的建议截窗判为空操作（窗末端 2025-09-09 < 缺口起点 2026-10-01）。**若 Owner 认为本席翻早了，回退命令＝把 `status: preregistered` 改回 `blocked_on_data` 一行**（本班未删任何字节，旧案卷原文俱在）。
3. **正交闸的"对象错配"是本生产线当前的静默面**：③席对三条 money_flow 候选报的 verdict 全部是**市场级折叠版**，而卡池的判据形状（五键＝横截面 RankIC 族）量的是**个股横截面**。闸与卡量的不是同一个对象时，reject 既不能当否决也不能当放行——本席两头都不做，落 OD-19。这与在册记忆卡 silent-degradation-looks-like-not-triggered 同族：**闸的读数面与卡的判据面不同根时，"跑过闸"是假绿**。
4. **④席情报送达面与卡池载体面之间没有桥**：④席已把三件写成"⑥须落字"，但卡池无该族具名卡（名称面 7 图案全 0），而⑥无权自造对象。这是 SOP ③④→⑤→⑥ 链上"④直送⑥"的一条空转路径（④席 web_cards 与③席 lane CSV 是两套面，本席只被授权消费后者）。
5. **骨架卡面零填第五班复证**：empty 186/186 仍 `generated:true`，具名 empty=0；本班不重复领、不重复呈批（OD-11/12 在册停手口径）。骨架面本班跑的是**只读** `--check`（实测见 R2，本班未调生成器写骨架，drift 恒 6＝本班零新增漂移）。
6. **在途件避让实测**：`data/strategy_intake/web_cards/` 九件中四件 mtime ∈ 本班值守（08:22/08:24/08:25）＝④席在写；卡池 `git diff HEAD` 11 件全部有主（10 件 preregistered→examined ＋ 1 件 blocked_on_impl→preregistered）＝⑦⑧/⑤在途；本班清单只含自家 7 件（2 新卡＋1 翻转卡＋1 台账＋1 游标），零吸收。
7. **环境警戒（在册事故形态）**：开班 `process_reaper --status` 实测 `commit_pct=97.6%`、`degraded=True`、breached=`ALERT-SYS-003`、`worktree_changes=5386`、`ram_used_pct=71.4%`——与 [[mem-commit-limit-incident-20260915]] 的"崩在 git add"前提同形。本班据此**主动降低并发与批量**（制卡与验证全串行、令牌登记逐件、CH 查询只读三批），如实上报：令牌登记首件即超 2 分钟被移入后台，属该内存压力形态而非工具缺陷。
8. **锁与命名闸第 N 次复证**：`lock_files.py acquire` 对本班 4 个新卡名（先按 5 件申请，其中 2 件后判不立卡）吃 N-01/N-13，走在册逃生口 `--skip-naming-check`（卡名必须沿用同族 `TDM-E-*__calibration__NN_*` 才能被考试器与⑨席 card_id↔文件名互推消费）。
9. **游标防重入实测**：开班 checkpoint 明书"本班已收尾"（08:18），`lock_files.py cleanup` 同时报 `SALVAGED — 死会话 st-qoder-p06-1015-04 遗物已回收（merge=skipped, stash=0件, 释放claim=0）`＝上一班账面已收尾、会话壳被回收，本班接手无内容丢失（释放 claim=0 与之自洽）。

**本班实际耗时**：date 实测 08:23:03 开班（冷启动首读）→ 08:46 台账落盘＝**23 分钟**（SOP 3-B 估⑥席 20 分＝偏差 +15%；主因＝①上游三席在上一班 08:16 收尾后集中到料（②席 08:15/07:07 两节点名⑥、③席 p03-02 批 5 候选、④席 07:45 节 5 情报）②翻转卡须自测窗内四面而非采信转述 ③呈批真源两头不可写须逐路实测 ④内存告警下降串行）。如实记账，不改估时基准。

**自检两轮**：
- R1（门柱与冻结值逐字一致＋单变量核对）：`.runtime/tmp/p06_1015_05/verify_r1.py`＝**2/2 CLEAN**——window 整块与所抄源 HEAD 面 JSON 全等、pillars_numeric 整块全等、buckets.type+min_obs_per_bucket 全等、oos_window_ref==源卡 window.oos、signal_kind/discipline 全等、node_id 正确、无 `generated` 键（非骨架）、status 在枚举内、③席 definition_zh/sample_window/orthogonal_gate_note 三面逐字在卡、MFGAP 另核"残差化三柱逐柱原文相等＋target 整块全等＋MFCAL-011 行原文在卡"。翻转卡 A17/02 的核对＝写前后 `yaml.safe_load` 八面 parsed 内容全等（window/buckets/pillars/pillars_numeric/target/oos_window_ref/discipline/signal_kind）＋`status` 单行差＋追加块 only-add。**对照卡 diff 项＝本班 N/A**：本班领用面 [对照] 申请零新条（在册两笔一已成卡一已停手 OD-15），故"diff 恰一个变量"无可核对象，此项如实记 N/A 而非记绿。
- R2（归属·净零·保底·进程外核实）：`verify_r2.py`＋命令面逐路实测：
- **归属**：`git status --porcelain` 本班清单＝7 件有界——`??` 2 新卡／` M` A17/02 翻转卡／` M` checkpoint／`MM` ledger（＋`M ` 的 instruction.md 与 ledger 头部 52 行是本席族 10-14 22:07 首批的未落地 staged 面，随册落地＝同岗自家件，非他班）；他会话在途件（L1-S2 40..47 八件、L3-07-3/02、L9-A01/02、TDM-P-P1-03/03、web_cards 四件、04 区 97 件 index=A）**本班清单零触碰、零吸收**。
- **写后池态**：544 张＝preregistered 184／empty 186／blocked_on_data 71／examined 64／blocked_on_impl 39。与本班预期对表：总数 542→544（＋本班 2 新卡）✓、blocked_on_impl 38→39（＋05 号卡）✓、blocked_on_data 71→71（−A17/02 翻转＋SEAL 新卡＝恒等）✓、preregistered 184→184（＋本班翻转 1、−他班 concurrent 开考 1）、examined 63→64（他班在本班值守内新出分 1 件，逐件对表＝`git diff HEAD` 面有主，本席未改其字节）。**本班净效果＝翻转 1＋新卡 2，其余一律有主**。
- **骨架零新增漂移**：`python scripts/backtest/generate_exam_card_skeleton.py --check` 本班写后实测 `{tdm_nodes:186, drift:6, missing:0, identical:180, protected_manual:0}`＝与上一班写前写后三读数逐键同值（findings 5 的"未跑"一句已被本段实测取代，脚本真源=`scripts/backtest/generate_exam_card_skeleton.py`，非 `scripts/` 根）。
- **投影 CAS 自证**：`capability_canonical_file_registry.yaml` 键集 HEAD 15,282／盘面 20,212 ⇒ **deleted_vs_head=0**、added 4,930（含本班 2 件逐件核名在盘面；另 4,928 条为他班在途，**本班不随袋**——袋=整档快照，随袋即归属篡改）；本班 2 件 token 逐件实测 `created_by: st-qoder-p06-1015-05`、token 尾日期 -20261015、capability=exam_card、merge_evaluation 随件在册。另登记一处**非本席面变化**：上一班报 HEAD 面 15,283 键，本班实测 15,282＝值守内有他班 commit 净删该册 1 键，本席不代查。
- **队列卫生**：`.runtime/commit_queue` 实测 pending 105／processing 4／done 774／dead 124；**p06 自家袋 pending=5、dead=0**（上一班报四袋全 pending，本班第 6 袋=本班自投）⇒ 本班无当日四态分诊欠账、未触碰他班袋。
- **净零**：零新 gate／零新规则册／零新注册表／零新脚本入册（制卡与核验脚本留 `.runtime/tmp/p06_1015_05/`，不入永久区）；保底＝2 新卡＋1 翻转＋2 不立卡裁定＋1 前置事实入卡＋4 呈批件＝**领用面 100% 处置**（③席 5/5、②席 4/4、④席 3/3、[对照] 0 新条、186 骨架按 OD-11/12 停手口径不重复领）。

**提交面堵点（本班实测，含三闸对症与拆袋决定）**：
- 首投 `git_commit.py --session … --enqueue` 被**锁外预检**双拦（耗时 82.2s，未吃锁未烧袋）：`[SESSION-REQUIRED]`＋`[WORKTREE-REQUIRED]`。
- SESSION-REQUIRED 正解＝**注册而非加旗**（在册口径）：`SessionRegistry().register(sid, pid=0, held_files=<本班会话 5 件>)` 实测 `get_session()` 转真；pid=0 走 90s 心跳窗由 daemon 续期（在册处方：短命进程注册必须 pid=0，否则心跳守护启动即退"session not in registry"）。本席指令卡冷启动三步未含 `session_worktree_start`，故本班**无车道**（该 API 会连带建 worktree，而本班成果已在主区）——此偏离如实入账，根宪法 §0 第 3 条的"降级直改主区=显式申请制"理由已写进 commit message 正文。
- WORKTREE-REQUIRED＝环境信号（他会话 12+ 活跃），走在册逃生口 `--allow-non-worktree`（2026-08-13 裁定 AI 可默认），不弱化闸、不加白名单。
- 入队前标准一步 `scripts/governance/meta/gate_prerun.py`（进程内门唯它能预跑）实测 **99 只门**：硬阻断 1＝`REFERENCE-INTEGRITY [RULING-REFERENCE] RULING_ATOMICITY_VIOLATION`，指认 `ledger.md: 裁定#536`。本班逐路定性：该引用**不在本班新写行**，而在本册 1015-02 班第 96 行与 1015-03 班第 190 行（本册追加式禁删改他人行）；`裁定#536` 在 `docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml` **工作区面存在、HEAD 面不存在**（实测 worktree 含 536/501、HEAD 只含 501）＝该册条目尚未落地，而全册在 pending 的 `q-20261015-st-maint9b-20261015-0008` 与 `q-20261015-st-scorehome-20261014-0003` 两枚他班袋里。⇒ 本席**不改他人行、不把他人未落地条目随自家袋代投**（袋=整档快照＝归属篡改）。
- **拆袋决定**：袋1＝卡面 3 件（2 新卡＋A17/02 翻转），预检对该清单零硬阻断（外来 staged 违规只 warn+审计）＝本班交付面先走；袋2＝台账＋游标，预期仍被同一门拦（因外来两行不动），按在册"队列项 dead＝当日四态分诊不隔夜、requeue 前先读 dead_reason 修因"处置＝死因已在册（等该册先落地），下一班若见其 dead 可直接 requeue，无需改内容。
- 全程至本段落盘＝08:23:03 开班 → 08:57（**34 分钟**；SOP 3-B 估⑥席 20 分＝偏差 +70%，主因另加一条＝本席首次遇到"注册会话＋预检双闸＋引用原子性"三连对症，全程按在册正解逐路实测未走旗子捷径）。


## 10-15 09:25 · st-qoder-p06-1015-06 · ⑥制卡席（③席 p03-03 批 11 条候选 100% 处置＝新卡 2 张（A02/10・A02/11，均 blocked_on_impl）＋不立卡裁定 7 条＋前置事实整行入卡 2 处＋非信号行呈批 1 件／⑨席 [对照] 追加面 4 行停手＝OD-15 追加／④席 p04-1015-03 点名⑥ 4 条→OD-24／新立 OD-22・OD-23）

**开班三实测**：①上一班游标（08:46）明书"本班已收尾"⇒ 防重入通过；②reaper `--status` 实测 source=live・last_run=09:03:46・scanned=57・killed=0；③环境 Python 3.12.8。**水位告警如实上报**：开班 reaper 读数 `commit_pct=97.05%`・`ram_used_pct=70.8`・`worktree_changes=5390>50`（并行漂移风险）⇒ 本班全程串行、零并发子代理、零长跑批。

**本班领用面（实测，非转述）**：
1. **③席 p03-03 批 11 条候选**（真源 `data/strategy_intake/lane_p0_obi_candidates.csv` 本班 DictReader 全读＝**24 行**，上班读 13 行；birth_batch 分布 obi-probe 1／p03-01 7／p03-02 5／**p03-03 11**）。卡池按 9 个候选图案名面（MITAILV/MIOPENV/MIKP/MIAMIHUD/MIVWAPDEV/MIRANGE/MIHHI/MIDOWNSK/MITAILMOM）完整 walk 命中 **0** ⇒ 十一条本班为首个领到的⑥班，零遗漏处置：

| 候选 | ③席在册闸读数（逐字取 orthogonal_gate_note） | 本班处置 | 判据 |
|---|---|---|---|
| CAND-P0-MITAILV-013 尾盘成交额时段占比 | pass max\|corr\|=0.2007（most_similar=lu_ratio）rc=0 | **成卡 TDM-E-L9-A02/calibration/10**，status=blocked_on_impl | 过闸＋kline_1min 可达（本班实测）＋门柱全抄得到位；缺⑤物化算子 |
| CAND-P0-MIOPENV-014 开盘30分钟成交额时段占比 | pass 0.1207（most_similar=avg_abs_ret_z20）rc=0 | **成卡 TDM-E-L9-A02/calibration/11**，status=blocked_on_impl | 同上 |
| CAND-P0-MIKP-015 分钟量价同向度 k_nb | 窗敏感：H1-2024 pass 0.2404／FY-2024 **reject 0.3612** rc=5（③席按宽窗判重复） | **不立卡** | SOP §3-G『不过闸记"重复"，喂 mined_out 判据』；本席不翻③席宽窗判据 |
| CAND-P0-MIAMIHUD-016 分钟 Amihud 非流动性 | H1 pass 0.1500／FY **reject 0.4836** rc=5 | **不立卡** | 同上（③席在册对象＝与 A02/08 blocked_on_data 卡的"可达替代"，但闸宽窗 reject） |
| CAND-P0-MIVWAPDEV-017 收盘相对 VWAP 偏离 | 两窗一致 **reject 0.5863**（lu_count_z20）／H1 0.7504 rc=5 | **不立卡** | 同上 |
| CAND-P0-MIRANGE-018 日内高低价振幅截面均值 | **reject 0.7619**（avg_abs_ret）rc=5 | **不立卡** | 同上；③席自陈"登记以证明本腿并非全族皆新（防自证偏向）"＝诚实面入册 |
| CAND-P0-MIHHI-019 日内成交额集中度 | **reject 0.6263**（avg_abs_ret）rc=5；③席请⑥对拍 L2-04-2/02 | **不立卡**＋对拍登记 | 对拍读面＝L2-04-2/02 系板块层 rank(amount) 前3占比（examined），本候选系个股日内层⇒**异对象**；但对象异不推翻宽窗 reject，二者不同层判据 |
| CAND-P0-MIDOWNSK-020 日内下行 RV 占比 | **reject 0.5398**（lu_ratio）rc=5；③席请⑥对拍 L9-A01/03 | **不立卡**＋对拍登记 | 对拍读面＝L9-A01/03（preregistered・panel・buckets.on『当日 RV（按 symbol 横截面）』・target=next_day_stock_return）vs 本候选比例型市场级序列⇒异形状同轴；**另记一条空白轴事实给⑨席**：闸池=pool6 六序列，不含 A01/03 的 RV 序列，故 most_similar 报 lu_ratio 而非该近邻＝二者从未同池对测，本席未跑闸无法补测 |
| CAND-P0-MITAILMOM-021 尾盘30分钟收益动量 | **reject 0.4153**（lu_ratio）rc=5；③席请⑥对拍 P3-04/02 | **不立卡** | 对拍读面＝P3-04/02（preregistered）含收益方向＋区间位置双维，本候选单维＝同族两形，按在册『同物两形禁各计一员』不另计 |
| CAND-P0-MINFPORTRAIT-022 kline_1min 口径画像行 | 非信号行（判据面行，无闸） | **整行入卡 2 处**＝本班 10/11 号卡 `data_binding.kline_1min_caliber_precedent`（definition_zh/example_value/downstream_meaning 三面逐字） | 六条画像正是本卡 data_binding 的写法门柱前置：(a) volume 单位=手（错 100 倍风险）、(b) 分区键 toYYYYMM(trade_time) 须用 trade_time 区间剪枝、(c) 无 market_type⇒前缀白名单宇宙守卫（本班卡面 universe_guard 键）、(d)(e)(f) |
| CAND-P0-MINLEG-023 楼1 主腿可达性扩测行 | 非信号行（12 表实测） | **呈批 OD-23**＋台账登记（本席不据此改任何在册卡面） | 其读数改变上班呈批第 2 条的断供清单（3 表→10 表）与一条限定令（『≥120 交易日结构性不可达』只适用订单簿类）——改他班呈批面不属本席裁量 |

2. **⑨席 st-qoder-p09-1015-06（to_impl.md 08:55 追加，上一班未领面）[对照] 追加面 1 条**＝请⑥按 04 班同一变量单换法（只切 OOS 窗为 IS 内同号段／反号段）把 4 行并入同一张对照卡批次。本班逐件读四张卡体实测＝`TDM-E-L9-A04/calibration/02`・`TDM-E-L1-S2/calibration/40・42・44` **四件 status 全=examined**・signal_kind 全=series・窗全=IS 2019-02-11..2026-04-02／OOS 2026-04-03..2026-10-12・五键全=0.6/0.02/0.3/true/true ⇒ **停手，出 OD-15 追加面**（在册『OOS 切 IS 同号段/反号段』口径本班实测仍零机读源：grep `同号段\|反号段\|oos_split\|sign_segment` 命中 5 件全部是本席 1015-04 班写进 A02/03..07 的 gaps 键＝申请面而非口径源）。
3. **④全网战法矿工席 st-qoder-p04-1015-03（to_impl.md 08:55 追加）改良情报 6 条中点名⑥的 4 条** ⇒ 全部**登记＋呈批 OD-24**，本班未制一张"看似齐了其实是自拟"的卡：卡07 归一分母择一（circ_mv vs 成交额）与在册 L9-A06/02・L3-12-1/02 的"占比列"口径冲突；卡07 双臂分考（顺势/反转符号相反＝两个对象，本席无权一卡两臂）；卡09 PIT 腿**已在册**（本班读 L9-A13/02 derivation 原文含『仅用 end_date 更晚且 announce_date 已发生的前一期（禁用到未来披露日）』），但其另三条剔样（次新／增发／解禁／转债转股）在卡面 grep **全 0 命中**⇒ 对 preregistered 卡加柱=挪门柱，只能呈批；共线预警 0.68 系④席未复现读数（自陈禁当已证），闸侧义务属⑨席、本席不跑闸。
4. **骨架 empty 面**：本班实测 empty=**186 且 186/186 全带 `generated` 键（具名 empty=0）**（完整 walk 计数）⇒ 按 OD-11/12 在册停手口径不重复领、不重复呈批。

**制卡纪律（程序直读注入，本席未手抄一个字）**：脚本 `.runtime/tmp/p06_1015_06/make_cards.py` 先 `git show HEAD:` 取三件在册冻结本体（`TDM-E-L9-A01/calibration/03`・`TDM-E-L9-A04/calibration/02`・`TDM-E-L9-A09/calibration/02`）与 CSV 候选行，再把 `window` 整块／`pillars_numeric` 整块／`buckets.type+min_obs_per_bucket`／`discipline`／`oos_window_ref` 锚／`signal_kind`／`target.primary+secondary+data_binding.target_source` 的原对象写入两卡，候选与画像行的 `definition_zh/sample_window/example_value/orthogonal_gate_note/data_source_table` 逐字段原文入卡；本席自写的只有 title_zh、buckets.on 的信号命名串（无数值）、hypothesis 的叙述句（不含任何阈值）、gaps 键与 status_reason/provenance。**零自拟数值、零算术、零四舍五入**：两卡五键＝0.6/0.02/0.3/true/true（整块抄 A01/03，且本班 parsed 对拍＝与 A04/02・A09/02 三面同值⇒数值面无择一）；窗整块抄 A01/03（择由见 OD-22）；`signal_kind: series` 抄 A09/02；target 三面抄 A04/02。母卡 A02/02 的 6 键面（含 `impact_curve_min_ratio: 2.0`・`regime_same_sign: false`）**本班未移用**——本班对象是市场级日频序列且五键在同层有 preregistered 源，移 blocked 源的 false 会放松判据，故走"同层同表 preregistered 源"；该择由本身仍是 OD-17（blocked 源 vs preregistered 源两制并存，本班为第六例）在册未裁面。

### 呈批四件（正文寄存本台账——05 区呈批真源第六班仍两头不可写：新址 `docs/04_research_records/mining/ledgers/nightmine_20261010/05_owner_decisions.yaml` 盘面 7,062B／`git status`=**A**（他班 staged）／HEAD **查无**（`git show HEAD:` 报 "exists on disk, but not in 'HEAD'"）；旧址 `docs/_working/nightmine_campaign/` 目录已删。⇒ 随袋他班未落地条目＝归属篡改，故仍寄存）

```yaml
- id: OD-15 追加面（06 班，题面不变、旧卷不删）
  项: ⑨席 1015-06 班把"OOS 切 IS 同号段／反号段"对照申请从 2 行扩到 6 行（新增 L9-A04/02・L1-S2/40・42・44）——请批切段口径或另派⑤席扩执行器
  实测分母: 四件卡体本班逐件读＝status 全 examined、signal_kind 全 series、窗全 IS 2019-02-11..2026-04-02／OOS 2026-04-03..2026-10-12、
    五键全 0.6/0.02/0.3/true/true；切段口径机读源 grep（同号段｜反号段｜oos_split｜sign_segment）在规则册＋卡池命中 5 件、
    全部＝本席 1015-04 班写入 A02/03..07 的 gaps_no_source.oos_subsegment_caliber（申请面，非口径源）
  为何要点头: 该单换法的"单变量"恰是 OOS 窗边界，而边界须由 IS 读数决定＝**看数后定窗**，与裁定#518『先冻结后跑』与在册 G4-5
    『事后挪门柱=作废』正面冲突；且四件已 examined＝重烧 OOS 消费面（迭代预算属⑩席）。出路 (a) Owner/⑨给成文切段规则（如"按 IS 日频 IC 符号
    连续段切、段长下限=在册 min_obs_per_bucket 60"）⇒ 本席一件成批四张对照卡；(b) 派⑤扩执行器支持 window.oos 多段形再裁口径；
    (c) 维持现档＝⑨席单在册、卡面无载体（本台账即为登记面，六行全部留痕）
  不点的后果: ⑨席"只栽 OOS 一根柱"的 6 个对象永远没有 A/B 面，负结果只能整体封存或重复再考（复跑消费 holdout）；
    本席若自挑一个切点＝给六张卡自拟门柱（在册禁自拟纪律）
  凭据: to_impl.md 2026-10-15 st-qoder-p09-1015-06 节 [对照] 追加面行原文；本班四件卡体实读；grep 谓词与 5 件命中清单
- id: OD-22（本班新立）
  项: 绑 c1_market.kline_1min 的在册卡窗并存 5 套＋本 node 唯一冻结面是 tick 短窗预演——请裁"分钟微结构族（市场级序列）预注册卡"的窗真源
  实测分母: 本班谓词＝data_binding.signal_table 含 kline_1min 的在册卡 11 张（含本班 2 张；全文提及该表 15 件），其 window 去重＝
    3×(IS 2022-01-04..2023-12-29／OOS 2024-01-02..2025-09-09)、1×(2021-09-01..2023-12-29／同 OOS)、1×(2021-09-01..2025-09-30／2025-10-09..2026-09-30)、
    4×(2026-06-01..2026-08-31／2026-09-01..2026-10-09)、2×(2021-09-01..2024-12-31／2025-01-01..2026-09-30)；
    本 node 唯一冻结面 A02/02 窗=IS 2026-01-05..2026-06-30／OOS 2026-07-01..2026-09-30 且其 frozen_note 自陈"短窗预演不作分布性结论"；
    本班可算性实测（CH 只读）＝system.parts active partition 62 个（202109..202610）、sum(rows)=1,496,671,246、
    单日 2024-06-03 探针 tail 带[14:30,15:01)=156,922／open 带[09:30,10:01)=156,922／全日=1,219,942／uniq symbol=5,062
  为何要点头: 本席两卡的窗只能整块抄某一张在册件（自拟日期=编数）；择"同 flow 同层同 family＋同表＋preregistered＋OOS 末端对齐③席在册切点 2025-09-09"
    得到 A01/03，但 (a) 若 Owner 判应取 IS 起点=数据起点 2021-09-01（X-S1-04/05 那一套）⇒ 本班两卡窗要换块，回退命令=改 window 两行＋frozen_note；
    (b) 若判按 node 一致性优先（本 node 只有 tick 窗）⇒ 两卡窗改抄 A02/02，但那是"不作分布性结论"的预演窗且 OOS 落在当季（烧 2026 HOLDOUT 面）；
    (c) 判"1min 族另立窗册"（一条成文常数）⇒ 最治本，本席照抄新册。三择一的判据形状不属本席
  不点的后果: 分钟微结构族每张新卡各挑一套窗＝同族读数不可比、OOS 面被不同时段反复消费；
    ⑦⑧按卡开考时同一信号在不同窗下得分不同，归因会把窗差读成信号差
  凭据: 本班 10/11 号卡 gaps_no_source.kline_1min_window_caliber 原文；11 件读面清单（尺件 .runtime/tmp/p06_1015_06/verify_r1r2.py 的 R2 段，正文可原样复跑）
- id: OD-23（本班新立）
  项: ③席 CAND-P0-MINLEG-023 把断供清单从 3 表扩到 10 表＋给"≥120 交易日结构性不可达"加限定令——请裁是否采纳为该族 blocked_on_data 的在册判据文字
  实测分母: ③席行 example_value 逐字＝前 10 表切点前行数全部=0（auction_book 覆盖 2026-07-21..09-30／auction_snapshot 2026-06-01..09-30／realtime_snapshot 2026-10-14 单日起／board_index_tick 2026-09-15..10-12／market_fund_flow_daily 2026-03-27..10-14／daban_board_event 2026-09-01..10-12／sector_fund_flow 2026-09-15..10-14／limit_up_pool 2026-09-01..／market_breadth_snapshot 2026-08-24..／dragon_tiger 2026-08-07..）；
    kline_1min 切点前=1,145,777,646 行／974 交易日、kline_60min=19,017,176 行；正对照同式 money_flow 切点前=5,504,375 行与 20261015-p03-02 在册读数逐位相同（尺有效）；
    本席独立复证（只读）＝partition 202109..202610・active rows 1,496,671,246・两时段带全覆盖；
    本班另读 A02/03..08 六件的 data_binding.signal_table＝**六件全绑 tick_depth_5（订单簿类）**⇒ 限定令若采纳，这六件 blocked_on_data 不变（本班零动作）
  为何要点头: 这既是③席对**上班自己结论**的样本面补正（原清单 3 表→10 表），也是一条会改变判据外延的限定（"结构性不可达"从盘口族收窄到订单簿类）；
    (a) 采纳⇒①②席的断供/补采单应按 10 表开、且分钟量价形态类不得再用该句挡（本班 10/11 号卡即走此路）；(b) 不采纳⇒本席两卡的"可达"论据须重述；
    (c) 判为③席内部修订不入判据面⇒本席只在台账留痕。改他班呈批面与改断供判据都不属⑥席写域
  不点的后果: 断供清单停在 3 表＝①②席按 3 表补采、另 7 表继续零行；"结构性不可达"若被误用于分钟族，
    会把 kline_1min 974 交易日的可达面对闸挡在门外（本生产线当前最活跃的一条新腿即被误封）
  凭据: lane_p0_obi_candidates.csv CAND-P0-MINLEG-023 行逐字（本班 DictReader 全 24 行读取）；本班 A02/03..08 六件 signal_table 实读；本班 CH 实测
- id: OD-24（本班新立）
  项: ④席 p04-1015-03 四条点名⑥的口径自由度（卡07 归一分母・卡07 双臂分考・卡09 剔样三腿・卡08 标度写死前置）——请逐条裁定取值
  实测分母: to_impl.md 第 112-117 行逐字：①『净流入腿禁直接除以成交额做跨市值比较，主构造应除以流通市值；成交额版只作对照臂』（④席实测
    stock_daily_basic.circ_mv 于 2026-10-14 为 5563/5563 行>0、中位 493741.644）；②『须同时挂"顺势臂"与"反转臂"，两臂读数禁合并报数』＋『应实现为分档过滤而非
    zscore 全域打分』；③卡09 PIT 与剔样义务（announce_date／次新／增发解禁转债）；④卡08 换手标度须 float_share×kline_daily.volume 反算互证后才写死。
    本班在册面对表＝(i) 卡池最接近载体 L9-A06/02（main_net_inflow_pct 水平截面，preregistered）与 L3-12-1/02（主力净额占比）用的都是**在册 pct 列**，
    卡池 grep『÷circ_mv』口径=0 源；(ii) 卡09 的 announce_date 腿**已在册**（L9-A13/02 derivation 原文含『仅用 end_date 更晚且 announce_date 已发生的前一期（禁用到未来披露日）』，
    本班 grep 该件 announce_date=True），但 次新／增发／解禁／转债 四词在该卡面 grep **全 False**；(iii) 卡08 的在册死列证据链已在案（kline_daily turnover>0=0/144576）
  为何要点头: 四条共同的形状＝"先择一/先补判据，后冻结"，而本席只准抄在册冻结值。分母择一若判 circ_mv⇒须另立候选（换对象）；
    双臂若判并存⇒③席各立一行各过一次闸，本席各成一卡（一卡两臂＝两对象混判，在册禁）；剔样三腿若采纳⇒是对 **preregistered 卡 L9-A13/02 加柱**＝挪门柱（Owner 面）；
    标度写死属⑤实现前置，本席不代跑反算
  不点的后果: ④席全网挖矿的产出继续落在"情报已送达、卡面无处落字"的悬空面（与 OD-20 同型，第六至第九例）；
    L9-A13/02 若被⑤按无剔样的版本物化，次新样本会把结论做反（④席引外部实证：次新 617 样本平均超额 +81 个百分点量级）——该风险卡面无人守
  凭据: to_impl.md 2026-10-15 st-qoder-p04-1015-03 节六行原文；本班 L9-A13/02 卡体实读（status=preregistered・kind=panel・signal_table=c3_fundamental.shareholder_count）；
    本班 L9-A06/02・L3-12-1/02 在册列面；SOP §⑥『只抄在册冻结值…语义参数缺→呈批（一个数不编）』
```

### findings（本批实测，非转述）

1. **本班是今天首个"新卡走 preregistered 源"的班，也是第一次不抄母卡**。③席 p03-03 两条过闸候选的对象与母卡 A02/02（tick・blocked_on_data・窗自陈"不作分布性结论"）不同形，本席改走同层同表的 A01/03（preregistered）＋市场级序列先例 A09/02・A04/02 三源合成。此法把 OD-17（blocked 源 vs preregistered 源两制）从"要不要用 blocked 源的数"推进到"同族该有窗真源册"，落 OD-22。
2. **"13 件提及该表"是本席自己写错的计数，已改**：初版卡面写"绑 kline_1min 的在册卡窗并存三套（13 件去重）"，本班尺实测＝signal_table 含该表 **11 张、窗并存 5 套**（全文提及面 15 件）。卡面文字与尺文已按实测改写（`.runtime/tmp/p06_1015_06/make_cards.py` 与 `verify_r1r2.py` 同一提交面），留此一句作自证与下一班反面教材（在册教训：计数谓词要写全路径/写字段，不写"提及"）。
3. **⑨席扩面对象已 examined 是新增风险**：四件 status=examined ⇒ 对照卡若成，champion 侧已消费过 OOS，切段再考＝同 holdout 二次消费（SOP §4 迭代预算属⑩席审计），本班把这句写进 OD-15 追加面"为何要点头"。
4. **本班未跑任何考试、未跑正交闸**（冻结与运行分离）：闸读数全部转抄③席在册行；可算性证据是本席自跑的 CH 只读探针（partition 元数据＋单日带计数），零写库、零分数册字节。
5. **正交闸"对象错配"在分钟族复现并加一例**：020 与 A01/03 系同轴近邻，但 pool6 不含 A01/03 序列，故闸从未把这对放在一起测（reject 报的是 lu_ratio）⇒ 本席对拍结论只到卡面形状层，数值层无源；已作为"空白轴事实"登记（供⑨席补池）。
6. **上游到料都在本班值守内到达（非账面引用）**：to_impl.md mtime 08:55（⑨席 06 班＋④席 03 班追加）与 CSV mtime 09:00（③席 p03-03 批）——本班为首个领到这两面的⑥班；两席台账/信箱文件本班**只读未改**。

### 自检两轮（两轮都核对，实跑读数如下）

- **R1（门柱与冻结值逐字一致＋单变量核对）**：`.runtime/tmp/p06_1015_06/verify_r1r2.py` 的 R1 段＝**2/2 全 CLEAN（每卡 22 项）**——window 整块与 HEAD 面 A01/03 parsed 全等、pillars_numeric 整块全等（并核与 A04/02・A09/02 三面同值）、buckets.type+min_obs_per_bucket 全等、discipline 全等、signal_kind==HEAD(A09/02)、target.primary/secondary 与 data_binding.target_source==HEAD(A04/02)、oos_window_ref==window.oos（锚）、card_id↔文件名互推相等、node_id 正确、status 在枚举内、无 generated 键（非骨架）、③席候选行五字段原文逐字在卡面、022 画像行三字段原文逐字在卡面。**对照卡 diff 项＝本班 N/A（如实记不记绿）**：本班唯一领到的 [对照] 面（⑨席 4 行扩面）停手在 OD-15，未成卡 ⇒ 无 champion/challenger 可 diff；本班两卡是新造具名卡，与源卡差异面=信号对象本身，已在各卡 prereg_provenance.single_variable_note 声明。
- **R2（归属·净零·保底·进程外核实）**：①卡池 546 件（非骨架 360＋empty 186），状态面 prereg 184／blocked_on_data 71／blocked_on_impl 41／examined 64／empty 186——与上班读数对表＝**仅 blocked_on_impl 39→41（恰本班 +2）**，其余四态零变⇒本班未改他班卡面一字；②empty 面 186/186 仍全 `generated`（完整 walk）＝骨架零填第六班复证，本班不重复领；③骨架 `--check` 只读实测＝{tdm_nodes:186, drift:6, missing:0, identical:180, protected_manual:0}，与上班写后同值＝**本班零新增漂移**（未调生成器写面）；④投影 `capability_canonical_file_registry.yaml` 键集 HEAD **15,282**／盘面 **20,216**／**净删 vs HEAD=0**／净增 4,934（本班 2 件逐件核名在盘面且 `created_by: st-qoder-p06-1015-06`，另 4,932 条他班在途**不随袋**）；⑤两张新卡 `git ls-files` 空＝本班尚未提交（写此段时的真实态，提交后由 git log 读回）；⑥台账追加走 safe_write_text CAS＋**纯前缀断言**（删除集=空集，写后进程外读回）；⑦净零＝零新 gate／零新规则册／零新注册表／零新脚本入册（制卡与核验脚本留 `.runtime/tmp/p06_1015_06/`）；⑧保底＝**2 新卡＋7 不立卡裁定＋2 处前置事实入卡＋4 呈批件＝领用面 100% 处置**（③席 11/11、⑨席 1/1（停手呈批）、④席 4/4（登记＋呈批）、骨架 186 按在册停手不领）；⑨本班实际耗时＝开班 09:04:01（reaper 时间戳实测）至本段落笔 **09:25**，开班→本段落笔 **21 分钟**（09:04→09:25），不足半窗，其中无返工轮、R1 谓词自纠一次（见 findings 2）与卡面计数改写一次同计入本窗。
## 10-15 10:09 · st-qoder-p06-1015-07 · ⑥制卡席（③席 p03-04 批 9 条 100% 处置＝新卡 3 张（L9-A01/06・07・L1-S2/48，全 blocked_on_impl）＋不立卡裁定 4 条＋前置事实整行入卡 3 处／⑧考工B 点名⑥解锁单 6 件＝补键 2 张（P2-04/06・07，值=本卡冻结 window.oos）＋4 件排产或呈批／②席点名 3 件／④席点名 2 件／新立 OD-25..28＋OD-22 追加面／本班另记 06 班游标未推案）

**开班三实测**：①防重入＝**两址同读**（在册处方 10-15 ⑦席入册）：旧址 `docs/_working/automation_campaign/p06_prereg/checkpoint.md` 盘面游标＝"本班已收尾"（last_batch 1015-05）、新址 `docs/04_research_records/cross_domain/automation_campaign/p06_prereg/checkpoint.md`＝"未开始"⇒ 取较新旧址；06 班台账 09:25 节自证收尾＋其袋 `q-20261015-st-qoder-p06-1015-06-0001` 已入 pending＋其 heartbeat 末行 `status:"exited"`＋PID 30504 `Get-Process` 查无＝三证齐，判定前任已停手，本班取号 07。②reaper `--status` 实测 source=live・last_run=09:36:40・scanned=56・killed=0。③Python 3.12.8。**水位如实上报**：开班 reaper 读数 `commit_pct=90.72%`・`ram_used_pct=75.3`・`degraded=True`・`breached=['ALERT-SYS-003']`・`worktree_changes=5395>50` ⇒ 本班全程串行、零并发子代理、零长跑批、零 CH 探针（可算性证据一律转抄③席在册读数并明标"本班未重扫"）。

**本班领用面（实测，非转述）**：

1. **③席 20261015-p03-04 批 9 条**（真源 `data/strategy_intake/lane_p0_obi_candidates.csv` 本班 DictReader 全读＝**33 行**，birth_batch 分布 obi-probe 1／p03-01 7／p03-02 5／p03-03 11／**p03-04 9**；CSV mtime 09:39:33＝③席 p03-04 到料在本班开班之后，本班为首个领到的⑥班）：

| 候选 | ③席在册闸读数（逐字取 orthogonal_gate_note） | 本班处置 | 判据 |
|---|---|---|---|
| CAND-P0-MIVOLSHAPE-024 日内波动率时段占比 U 型 | 两窗一致过：FY pass 0.1454（most_similar=lu_ratio）／H1 pass 0.1281，rc=0 | **成卡 TDM-E-L9-A01/calibration/06**，blocked_on_impl | 过闸＋门柱全抄得到位＋字段级查重 0 命中（正对照见 R1）；缺⑤物化算子（本班 grep 实测） |
| CAND-P0-MIJUMP-026 单分钟最大方差占比 | 两窗一致过：FY pass 0.1798（lu_count）／H1 pass 0.1969（lu_ratio_z20），rc=0 | **成卡 TDM-E-L9-A01/calibration/07**，blocked_on_impl | 同上；③席点名"与 020 分子不同（极值 vs 子集），闸读数可辨"＝对拍结论入卡面 single_variable_note |
| CAND-P0-SENTSKEW-029 截面收益偏度 | 两窗一致过：FY pass 0.1965（avg_abs_ret_z20）／H1 pass 0.1859（lu_ratio），rc=0 | **成卡 TDM-E-L1-S2/calibration/48**，blocked_on_impl | 同上；③席点名"须⑥席对拍勿各计一员"⇒ 本班对拍读面见 findings 3，对象差双登记（卡面 gaps.churn_vs_intraday_path_skew＋本节），成员计量属⑨席 |
| CAND-P0-MIGKEFF-025 区间-收益路径效率比 | 窗敏感翻转：H1 pass 0.2758／FY **reject 0.3138**（lu_count）rc=5（③席按不利侧定案记重复，第 3 例） | **不立卡** | SOP §3-G『不过闸记"重复"，喂 mined_out』；本席不翻③席不利侧判据 |
| CAND-P0-SENTADV-027 上涨家数占比 | 两窗一致 **reject 0.6291／0.7369**（lu_count）rc=5；③席查重"概念有主"（情绪温度计组件在册） | **不立卡** | 同上＋③席在册负面结论"广度计数型情绪在池内已被涨跌停轴占据"与⑨04 班 lu_count↔lu_ratio=0.9949 互证 |
| CAND-P0-SENTNHNL-028 252 日创新高减新低净占比 | 两窗一致 **reject 0.6481／0.5139** rc=5 | **不立卡**＋对拍登记 | ③席点名与 `TDM-E-L1-S5/calibration/03` 差异面三条（60 日单侧裸 close vs 252 净差复权重构）；本班读该件＝status=preregistered・series・target=next_day_index_return，差异面成立但**不推翻宽窗 reject**（同层不同形仍系重复轴）⇒ 记入 S48 卡的窗择由，不另立项 |
| CAND-P0-SENTQASYM-030 四分位不对称度 | 窗敏感翻转第 4 例：H1 pass 0.1860／FY **reject 0.4092**（lu_ratio）rc=5 | **不立卡** | 同 025 处置；③席在册结论"矩型比…本席只登记不裁"原文入台账，本班不代裁 |
| CAND-P0-MI60CONTRAST-031 60 分钟档对照行 | 非信号行无闸 | **整行入卡 2 处**＝本班 06・07 号卡 `data_binding.band_caliber_precedent_031`（definition_zh/example_value/downstream_meaning 三面逐字） | ③席三条结论正打本班两张分钟卡：改绑 kline_60min≠复算分钟腿（corr −0.0120/−0.1002/+0.2511）、60min 档三构造各自过闸（0.0962 pass／0.5103 reject／0.0818 pass）、跨档分母差 227 只 |
| CAND-P0-SENTPORTRAIT-032 日线族口径画像行 | 非信号行无闸 | **整行入卡 1 处**＝本班 S48 卡 `data_binding.kline_daily_caliber_precedent`（三面逐字） | 五处口径＋一处③席自证先验正证伪正是日线族卡的写法门柱前置：market_type 唯一值 'A_share'（矿规 'stock' 命中 0＝假无源）／adj_factor 恒 1／turnover 零值 93.68%／pct_change=对前收且截 2 位（⇒ 与分钟腿 r_i=log(C/O) 语义不同，跨表禁混）／volume=0 停牌行 405 |

2. **⑧考工B 席点名⑥的解锁单（`p08_examiner_b/ledger.md` §六，本班首领）** 6 件逐件处置：
   - `TDM-P-P2-04/calibration/06`・`/07`＝**本班补 `oos_window_ref` 两张**（值=本卡已冻结 `window.oos` 的同一锚 `*id001`，零新拍数）。改前/改后＝89→90 与 84→85 行、difflib **minus=0／plus=1**、parsed 其余键全等、新键值=['2024-01-01','2026-09-30'] 与本卡 window.oos 全等。判"该补"的在册依据＝⑧席三道闸第 2 条"执行器只读 oos_window_ref 不读 window.oos，补键=改指向不属改判据，写域在⑥制卡席"＋⑧席本班 OOS 逐日截面实测 min 5436／max 5569 只票（30 对/日地板与 ≥30 IC 日可达）＝补完出真分。
   - `TDM-P-P1-02/02`・`TDM-P-P1-04/04`・`TDM-P-P3-04/04`＝**本班不补键**并呈批 OD-25。理由带承重证据：在册申报形态唯一（本班读 `scripts/backtest/fexam/calibration_exam.py:173-195` 原文）＝`target_forward_face: precomputed`＋`target_horizon_days: h`＋**`target.primary` 内须写 `mkt_fwd<h>`**；三卡 target 冻结面分别= `worst_return_next_5d`／`excess_return_next_10d`／`excess_return_next_5d` 且 `signal_kind=panel`（个股面），两申报键实测全 None ⇒ 按在册形态申报＝把个股 5 日最差收益换成**市场级** 5 日前向面＝换对象；不申报只补 oos＝⑧席明言"出的分名实不符"。故本班把"缺 oos_window_ref"如实记为**保护态**并给⑦⑧留一句：这三件挡在门外是正解，勿只补 oos 键开考。
   - `TDM-X-S1-03/comparison/02_dualwindow`＝本班**不动**，呈批 OD-26：实测 `window.oos=null`・`oos_window_ref=null`・**无 data_binding 段**・kind=series、target.primary 文字面＝"双臂同装置 on/off 配对（exit_simulator 口径）"⇒ ⑧席令"⑥补 data_binding"无在册源可抄（卡池零 exit_simulator 双臂绑定的市场级先例被本班字段级扫过），补绑定＝新增对象级判据面而非改指向。
   - `TDM-X-R1-01/comparison/02`＝本班**不动**，呈批 OD-27：该件 `oos_window_ref` 实测**已有值**（['2025-10-09','2026-09-30']，⑧席读数复证），真缺＝五态名映射＋**已批册格**（册格在 `mineloop_campaign/02_binding_book.yaml` 的 approved 面，非卡面写域）；退役原卷＝业务资产概念级退役＝Owner 门位（根宪法 §5）。本班不半件解锁（只抄 07 五态块而册格无格＝造"卡面齐而绑定册无格"的第六态）。

3. **②数据建设席 `unblocked.md` 点名⑥三件**：
   - `TDM-E-L2-09/calibration/02_板块催化剂密度`"是否依赖 rating_change 做主信号由⑥席判"＝本班读卡体判定**依赖成立**（`status=examined`・`signal_kind=series`・`signal_table=c3_fundamental.research_report`・`signal_column` 六列含 `rating_change`・`signal_derivation` 主构造=板块研报条数密度截面 z 分＋上调聚集）；该件已 examined⇒ 本班零卡面动作，"对账腿可开"属⑦⑧开考面，②席的口径提示（东财研报中心派生序数与券商原文不同源、禁混）随本节登记给⑦⑧。
   - `TDM-E-L9-A17/calibration/03` 的 `data_window_evidence` 与盘上现值不一致（②席 08:15 段：卡内旧值 trade_date 至 2026-09-30／rows=6,829,376，盘上 FINAL 恒 6,856,034・max 2026-10-15）＝本班**不改卡面**并入 OD-28。承重理由：②席自证"本班补的是快照轴、没补信息轴（10 月全部行 last_report_date=2026-09-30、n_reports 逐日衰减 4,474→4,417）"且"10 月段**不可**用作 EPS 修正信号样本增量"⇒ 把 evidence 刷到 2026-10-15 反而把 readiness 说假；而该卡 preregistered，改数据窗证据块＝对冻结卡动面，按在册一律呈批。
   - A17 两卡并存/退役（②席 07:07 段第 4 条点名"属⑥席与 Owner 面"）＝呈批 OD-28 一并办。

4. **④全网战法矿工席 p04-1015-04 改良情报 5 条中点名⑥的 2 条**＝登记、不呈批：
   - 情报1（极差族 PR=1.0529，"⑥制卡须只保留一枚代表"）＝本班字段级实测**六枚极差估计量（parkinson/garman/rogers-satchell/yang-zhang/histvol/natr）在册载体 = 0 件**（谓词=title_zh+signal_column+signal_derivation 三字段拼接正则，正对照同尺"涨停家数"命中 18 件）⇒ 该令对本席是**前瞻约束**，卡池无并档对象、无重复计量可销，不立呈批。
   - 情报3（卡10 须"特质波动／系统波动·beta 两列分别喂闸、beta 作对照臂"）＝喂闸属③⑨席、双臂配对制卡须先有③席在册具名候选行；本班扫候选册全 33 行**零"特质波动/系统波动/beta 分列"行**⇒ 无载体可制卡，与 OD-20/24 同型（情报已送达、卡面无处落字），本班不编数、不代③席立候选。

5. **骨架 empty 面**：本班完整 walk 实测 empty=**186 且 186/186 带 `generated`（具名 empty=0，加总与 empty 总数相等）**＝第七班复证在册停手口径（OD-11/12），不重复领、不重复呈批。

**制卡纪律（程序直读注入，本席未手抄一个字）**：`.runtime/tmp/p06_1015_07/make_cards.py` 先 `git show HEAD:` 取四件在册冻结本体（`L9-A01/calibration/03`・`L9-A04/calibration/02`・`L9-A09/calibration/02`・`L1-S5/calibration/03`）与 CSV 行，再把 `window` 整块（**含 regimes 全字段，按在册口径三键比对不只比 IS/OOS**）／`pillars_numeric` 整块／`buckets.type+min_obs_per_bucket`／`discipline`／`target.primary+secondary+data_binding.target_source`／`signal_kind` 的原对象写入卡面，候选与画像行的 `definition_zh/sample_window/example_value/orthogonal_gate_note/data_source_table` 逐字段原文入卡；本席自写的只有 title_zh、buckets.on 命名串（尺内已机检"不含数值"）、hypothesis 叙述句（零阈值）、gaps 键、status_reason/provenance。**零自拟数值、零算术、零四舍五入**：三卡五键=0.6/0.02/0.3/true/true 整块来自源卡（且尺内加判 `pillars_numeric` 键集 ⊆ 机判五键词表）；两张分钟卡窗抄同 node 同表的 A01/03（与上班 A02/10・11 同块同值⇒同族新卡不另起窗），日线卡窗抄同 flow 同层 series 的 L1-S5/03。blocked 源与母卡 A02/02 的 6 键面本班**未移用**（承 OD-17 在册未裁面）。

### 呈批五件（正文寄存本台账——04 区呈批真源第七班仍两头不可写：新址 `docs/04_research_records/mining/ledgers/nightmine_20261010/05_owner_decisions.yaml` 盘面 7,062B／`git status`=**A**（他班 staged）／`git show HEAD:` 报 "exists on disk, but not in 'HEAD'"；旧址 `docs/_working/nightmine_campaign/` 目录已删。⇒ 随袋他班未落地条目＝归属篡改，故仍寄存）

```yaml
- id: OD-22 追加面（07 班，题面不变、旧卷不删）
  项: 上班立的"分钟微结构族（市场级序列）预注册卡窗真源"未裁——本班把它扩到**日线市场级序列族**（同一形状问题在第二张表复现）
  实测分母: 本班谓词=signal_kind=series 且 data_binding.signal_table 含日线族的 L1-S2 件，其 window 全字段（in_sample/oos/regimes 三键）去重=**2 套**：
    ①IS 2019-01-04..2023-12-31／OOS 2024-01-01..2025-09-09（examined 15 件＋preregistered 的 L1-S5/03 同块）；②IS 2019-02-11..2026-04-02／OOS 2026-04-03..2026-10-12（examined 聚合族 40..47 与 blocked 的 38）；
    另 L1-S2 内 blocked_on_data 件用五键之外的 ic_mean_min 0.25/ic_ir_min 0.5（该件非本班抄源，如实排除）。本班 S48 卡取①（唯一 preregistered 同层源）
  为何要点头: 与 OD-22 同型——本席的窗只能整块抄某一张在册件（自拟日期=编数）。若 Owner 判应取②（末端对齐当季 HOLDOUT）⇒ S48 窗要换块，回退命令=改 window 与 oos_window_ref 两处＋frozen_note；
    若判"市场级日频序列族另立一张窗册"（一条成文常数）⇒ 最治本，本席与⑦⑧照抄新册，OD-22 与本追加面一并销
  不点的后果: 同一测度层每张新卡各挑一套窗＝读数不可比、OOS 面被不同时段反复消费；⑦⑧按卡开考会把窗差读成信号差
  凭据: 本班 S48 卡 gaps_no_source.daily_market_series_window_caliber 原文；尺＝.runtime/tmp/p06_1015_07/probe_calibers.py（YAML 解析级三键比对，正文可原样复跑）
- id: OD-25（本班新立）
  项: ⑧席三张多日目标卡（P1-02/02・P1-04/04・P3-04/04）的成对申报形态与在册机判词表只覆盖市场级面——请裁三择一
  实测分母: `calibration_exam.py:173-195` 原文三句＝『target_forward_face 唯一允许值=precomputed』『h∈2..252』『target.primary 内须写 mkt_fwd<h>（h 与 target_horizon_days 同值）』；
    本班字段级实读三卡：status 全=preregistered、signal_kind 全=panel、window.oos 全=['2024-01-01','2026-09-30']、oos_window_ref 全=null、
    target.primary 分别=worst_return_next_5d／excess_return_next_10d／excess_return_next_5d、target_forward_face 与 target_horizon_days 全=None；
    ⑧席本班前测同值（`_forward_face` 三张均返回 (1,False)）
  为何要点头: (a) 派⑤扩 `_forward_face` 接受 panel 多日面（含个股 5/10 日最差·超额面真源）⇒ 本班下一班补两申报键＋oos 键；
    (b) 判"多日目标只做市场级"⇒ 三卡题面作废、须③席按个股面重立候选各过闸，本班再成卡；
    (c) 维持不可考⇒ 本班把缺键记为保护态（已写进本节 2，⑦⑧勿只补 oos 开考）。本班择一即等于改他班判据或换卡面对象，两不属⑥席写域
  不点的后果: 这三件挂在⑧席"最高杠杆 5 分钟"账面但实测一键出不了分——下一班若照字面补键开考，分数册多三行名实不符的假红／假绿，
    归因会把"执行器按次日面消费"读成"个股 5 日下行信号无效"
  凭据: calibration_exam.py:173-195 原文；本班三卡字段级实读（尺 .runtime/tmp/p06_1015_07/probe_targets.py A 段）；p08_examiner_b/ledger.md §六
- id: OD-26（本班新立）
  项: TDM-X-S1-03/comparison/02_dualwindow 要求⑥补 data_binding，但该件连 window.oos 都不存在且卡池零同名源——请裁去留
  实测分母: 本班字段级实读＝window.oos null・oos_window_ref null・无 data_binding 段・signal_kind=series・status=preregistered・
    target.primary=『双臂同装置 on/off 配对（exit_simulator 口径）：压力窗 MaxDD 改善 + 近样年 OOS Sharpe 非劣/MaxDD 改善』；
    同 node 另有 `TDM-X-S1-03/comparison/02_止盈族三式对照`（preregistered・panel・有 data_binding 与 oos_window_ref）＝**同 node 同 family 的 02 号位两件并存**（card_id 不撞，号位复用），
    两件事实在同一张卡上互相顶：02_止盈族三式对照的绑定面系 panel 三式，不是 dualwindow 的双臂市场级面
  为何要点头: 补 data_binding 与补 window 都是**新增对象级判据面**（非改指向），须先有在册源或 Owner 认可的新面定义；
    (a) 判"由⑤先产 exit_simulator 双臂市场级面"⇒ 本班待其落地再补；(b) 判"该件由 02_止盈族三式对照承接"⇒ 退役属 Owner；
    (c) 判"本班按某张在册件抄"⇒ 请点名件号，本班零自拟
  不点的后果: ⑧席的 class U 台账继续把该件列为"⑥ 补 data_binding"空转单，每班重领一次（与 OD-20/24 同型第五例）
  凭据: 本班 probe_targets.py A 段两行原文读数；p08_examiner_b/ledger.md §六第三条
- id: OD-27（本班新立）
  项: TDM-X-R1-01/comparison/02 的去留（补五态名映射可抄 07 先例，但另一半是绑定册 approved 格）——请裁去留或授权册格
  实测分母: 本班实读该件 `oos_window_ref=['2025-10-09','2026-09-30']`（**已有值，非缺键**，复证⑧席 07 班更正）；⑧席在册令＝『按 07 先例补五态名映射＋册格，或按 07/07b 承接关系退役原卷』；
    07 先例块位＝该族 07 卡面 `data_binding.level_to_cap_map.five_state_native`（⑧席给到 :99-113 行号，自证"五态表逐字值取自在册件 position_cap 的 return 行"）；
    绑定册真源=`docs/04_research_records/mining/ledgers/mineloop_campaign/02_binding_book.yaml`（⑤席在册件：该册现双文档形态且 entries 18 格／approved 17）
  为何要点头: 卡面那半腿在本席写域（逐字抄 07 在册块），册格那半腿在绑定册 approved 面＝Owner/⑩ 门位；只落半腿＝造"卡面齐而册无格"的第六态（在册死法：该件被反复领取却永远开不了考）。
    退役原卷系业务资产概念级退役＝Owner 门位（根宪法 §5），本席不定去留
  不点的后果: 02 与 07/07b 三件同族并挂，⑦⑧排考面看到三个候选臂而绑定册只认得其中两格；成员计量与试次账（n_trial_ledger）分母失真
  凭据: 本班该件 oos_window_ref 实读；p08_examiner_b/ledger.md §六第四条；⑤席在册 D2 段（02_binding_book.yaml 双文档形态与 entries 18/approved 17）
- id: OD-28（本班新立）
  项: A17 两卡并存/退役＋A17/03 数据窗证据块与盘上现值不一致而本班不改——请裁并给一条"证据块刷新"的写域口径
  实测分母: ②席 07:07 段实测 `research_report.rating_change` 非空率 91.12%／下调全史 19,522 条（限 publish_date>=2022-01-01 仍 11,324 条）⇒ A17/02 两档解锁条件均超线，本班 05 班已把该件翻 preregistered（盘面）；
    ②席 08:15 段实测 `consensus_daily` FINAL 恒 6,856,034・max(trade_date) 2026-10-15，而 A17/03 卡内 `data_window_evidence` 仍记 2026-09-30／6,829,376；同段②席自证"补的是快照轴没补信息轴"（10 月全部行 last_report_date=2026-09-30、n_reports 4,474→4,417）且"10 月段不可用作 EPS 修正样本增量"；
    ⑨席 07 班实测 A17/02 **三面分叉**＝HEAD/index=blocked_on_data／磁盘=preregistered（本班 05 班袋 pending 未落地所致，如实承报）
  为何要点头: (a) A17/02 与 A17/03 是否并存＝业务资产概念级退役门位在 Owner，本席只登记；(b) 证据块刷新口径须成文——若判"⑥席可按②席在册读数刷 data_window_evidence 而不算挪门柱"，
    本班下一班即按②席台账值逐字刷；若判"扩 evidence 到 10 月＝误导 readiness"，则应保持现值并等研报明细腿补跑（②席在册在途风险 1：研报明细自 2026-10-01 起 0 行入库）；
    (c) 三面分叉的解法在提交链吞吐（头袋本班实测 waiting 30,043s），不在本席
  不点的后果: 已解锁的 A17/02 在任何按 HEAD/index 消费卡状态的面（含队列物化）继续被判阻塞＝解锁情报与排考动作两头落空；
    A17/03 若被按"数据已齐"开考，10 月段修正值恒 0 会把结论做反（②席明确不背书）
  凭据: unblocked.md 07:07／08:15 两段原文；p08_examiner_b/ledger.md 07 班修⑧姊妹面；本班开班实测 pending 队列与自家六袋
```

### findings（本批实测，非转述）

1. **本班首件堵点是自己写的错路径，已纠并留案**：首版三卡被写进 `exam_cards/L9/` 与 `exam_cards/L1/`（漏 `entry_flow/` 段），根因＝制卡器用 `node_id` 反推目录时只剥到 `TDM-E-` 前缀。后果面＝`git ls-files`/`--others`/`status` 三面**全部查无此件**（不是"未跟踪"而是"不在册路径"），`batch_creation_tokens.py` 因此报"无待登记文件"而非报错——**静默形态**。纠正＝mv 入 `entry_flow/L9|L1`＋`rmdir` 本班自造空目录＋修 `make_cards.py` 路径谓词；随后 token 3/3 登记成功（PG 与投影双读回）。教训入册：新件落位后必须先跑 `git status --porcelain -- <全路径>` 证"git 看得见"，再谈登记与入袋（根宪法 §8 路径禁凭记忆）。
2. **本班两把坏尺自纠（留旧案卷不删原句）**：①极差族载体首测报 0 件的尺**当时不可信**——那句 `hay=" ".join(str(...))` 把单个拼接串当可迭代对象逐字符加空格，中文多字 token 永远不命中；改正拼接写法后重测＝六枚极差估计量在册载体确为 **0 件**（同尺正对照"涨停家数"18 件证尺通），结论未变但证据换了；②投影自证首版用 basename 谓词报"本班 3 件在投影盘面 0/3"（假阴），改全路径相等后＝3/3。两处均已把尺身改对并写进复跑尺，禁止下一班按首版读数立结论。
3. **029 对拍读面（③席点名义务）**：`偏度` 在卡池非骨架件的**字段级**唯一命中＝`TDM-E-L9-A01/calibration/03`（其 hypothesis 与 signal_derivation 的"日内偏度"系个股 240 根分钟收益路径矩・panel・个股横截面），本班 S48 系一股一收益的截面三阶矩・series・市场级＝**同词不同对象**；对象差已双登记（S48 卡面 gaps.churn_vs_intraday_path_skew＋本节），成员计量（勿各计一员）属⑨席对拍。
4. **本班未跑任何考试、未跑正交闸、未跑 CH 探针**（冻结与运行分离）：三张新卡的可算性证据**一律转抄③席在册行**（kline_1min 切点前 1,145,777,646 行／974 交易日；kline_daily 2024 段 2,200,391 行／逐日宇宙 4837-5384 只），卡面 readiness 键明写"本班未重扫"；缺算子证据是本席自跑的 `card_binding.py` 只读 grep（谓词与命中清单逐字入卡面 status_reason）。
5. **正交闸"对象错配"在日线族复现并加一例**（承上班 pool6 空白轴事实）：③席在册行 028 与 `L1-S5/03` 的差异面三条（回看窗／单侧 vs 净差／裸 close vs 复权重构）成立，但闸池=pool6 六序列不含该卡的合成 z 面，故 reject 报的是 lu_count 共线而非该近邻＝**差异面从未与闸同池对测**，本席对拍只到卡面形状层，数值层无源。
6. **06 班游标未推（本班开班实测）**：盘面 `checkpoint.md` 字节 sha256=`1cf16357e8da…`＝06 班**自己袋内**的 checkpoint blob＝05 版文字（三面对拍表：06 袋 ledger blob 与盘面 MATCH／checkpoint blob 与盘面 MATCH 而该字节属 05）；06 班 `.runtime/tmp/p06_1015_06/set_cursor.py` 在册存在但**未生效**（其 06 号游标文字在盘面 grep `p03-03 批 11`＝0 命中）。⇒ 本班把游标推到 07，06 班交付面以其台账 09:25 节为准（本席不代写他班文字，也不据此判 06 班交付缺失——卡与台账均在其袋内）。

### 自检两轮（两轮都核对，实跑读数见 `.runtime/tmp/p06_1015_07/verify_r1r2.py`，rc=0）

- **R1（门柱与冻结值逐字一致＋单变量核对）**：三张新卡各 **22 项全 CLEAN**——window 全字段（in_sample/oos/regimes/frozen_note）与 HEAD 源 parsed 全等、pillars_numeric 整块全等且**键集==机判五键词表**、buckets.type+min_obs_per_bucket 全等、discipline 全等、`oos_window_ref==本卡 window.oos`（在册三闸第 2 条的机检项）、signal_kind==HEAD 序列先例、target.primary/secondary 与 data_binding.target_source==HEAD 源、signal_table/signal_derivation/example_value/orthogonal_gate_verdict/data_window_evidence 五面与③席 CSV 行逐字等值、对照或画像前置行 definition_zh+example_value 逐字在卡面、card_id↔文件名互推、node_id 正确、status 在枚举内、无 generated 键、buckets.on 不含数值。**补键两张**＝新增键集恰为 `{oos_window_ref}`、其余键与 HEAD parsed **全等**、difflib minus=0/plus=1、值=['2024-01-01','2026-09-30']。**对照卡 diff 项＝本班 N/A（如实记不记绿）**：本班领用面零 [对照] 申请（⑨席 07 班当日增量 0 行、⑤席 02 班未提对照、④席情报 3 无在册候选行载体），故无 champion/challenger 可 diff；三张新卡系新造具名子题卡，与各自抄源卡的差异面=信号对象本身，已在各卡 `prereg_provenance.single_variable_note` 声明。
- **R2（归属·净零·保底·进程外核实）**：①卡池 **549 件**（上班读数 546＋本班 3，完整 walk 计数）；状态面 prereg **184**／blocked_on_data **71**／examined **64**／empty **186**（四态与上班逐值同）＋blocked_on_impl **41→44**（恰本班 +3）⇒ 本班未改他班卡面判据一字（两张补键件状态仍 preregistered，属改指向）；②empty 面 186/186 全 `generated`、具名 0，且**骨架+具名加总=empty 总数**（在册互斥分母自证）＝骨架零填第七班复证；③投影 `capability_canonical_file_registry.yaml` 键集 HEAD **15,282**／盘面 **20,219**／**净删 vs HEAD=0**／净增 4,937（本班 3 件全路径逐件在盘面且 `created_by: st-qoder-p06-1015-07`、token 尾日期 -20261015、capability=exam_card；其余系他班在途条目**不随袋**）；④本班 5 件卡面改动 git 面实测：3 新件 `??`（尚未 add，写此段时的真实态）、2 补键件 ` M`——提交后由 `git log -1 --name-only` 读回；⑤会话与锁：`SessionRegistry().register(st-qoder-p06-1015-07, pid=0, held_files=2)` 实测 get_session 转真，心跳守护 pid=34768 首行 `status:"started"`・interval=30，`acquire-batch --skip-naming-check` 实测 **acquired=7 denied=0**（新卡名沿用同族 `TDM-E-*__calibration__NN_*` 才被考试器与⑨席 card_id↔文件名互推消费，故走在册 lock 侧显式逃生口）；⑥台账追加走 `safe_write_text` CAS＋**纯前缀断言**（删除集=空集，写后进程外读回）；⑦净零＝零新 gate／零新规则册／零新注册表／零新脚本入册（制卡与核验尺留 `.runtime/tmp/p06_1015_07/`）；呈批 5 件里 4 件为**新立**、1 件为**在册 OD-22 追加面**（题面不变、旧卷不删，不新开同义号）；⑧保底＝**5 张卡面动作**（3 新卡＋2 补键）达标且领用面 **100% 处置**（③席 9/9、⑧席 6/6、②席 3/3、④席 2/2、骨架 186 按在册停手不领、当日 [对照] 面 0 条）。
- **本班实际耗时**：开班 reaper 首读 09:37:00 → 本段落笔 **10:09**（`date` 实测）＝**32 分钟**（SOP 3-B 估⑥席 20 分＝偏差 +60%，主因两条如实入账：本班多做了 ⑧席解锁单六件逐件字段级核账与三件"不补键"的承重定性，以及自犯路径错置的纠正轮）。

## 10-15 16:17 · st-qoder-p06-1015-09 · ⑥制卡席（死班 1015-08 三证判死＋其未落地产出整面承接＝19 张未跟踪卡＋23 张补键件＋2 张翻态件；⑩第七单三件全处置＝8 枚自家死信内容级分诊／缺键 2 张实测"一无源一挡道"零硬补／两枚非在册顶层键按在册体例撤出卡面；③席 20261015-p03-05 批 6 行 100% 处置＝033 卡门柱 12 项＋原文 10 项全 CLEAN 收编＋034/035/036 不立卡＋037/038 前置已在卡面；新立呈批 OD-29）

**开班三实测**：①防重入＝两址同读（在册处方）——旧址 `docs/_working/automation_campaign/p06_prereg/checkpoint.md` 盘面＝"本班已收尾"・last_batch `st-qoder-p06-1015-07`・last_run 10-15 10:09；新址 `docs/04_research_records/cross_domain/automation_campaign/p06_prereg/checkpoint.md`＝"未开始"⇒ 取较新旧址，07 班已收尾，本班可进。②reaper `--status` 实测 source=live・last_run=15:30:39・scanned=34・killed=0・reported=1・whitelist_hits=18。③Python 3.12.8。
**水位如实上报（在册事故形态同形）**：开班 reaper 读数 `commit_pct=90.86`・`ram_used_pct=70.1`・`cpu_pct=83.5`・`degraded=True`・`breached=['ALERT-SYS-001','ALERT-SYS-003']`・`worktree_changes=5444>50` ⇒ 本班全程串行、零并发子代理、零 CH 探针、零长跑批；可算性证据一律转抄③席在册读数并明标"本班未重扫"。

**本班取号纠偏（自犯一条当场纠）**：本班 scratch 先按"08 未存在"建在 `.runtime/tmp/p06_1015_08/`，随后实测该目录已有他班 10:22–13:33 的在册脚本 17 件 ⇒ 取号冲突暴露；本班改取 **09**（`st-qoder-p06-1015-09`）并把本班五件临时件 mv 至 `.runtime/tmp/p06_1015_09/`，死班目录一字未动。教训：数班号不能只数台账节标题，须同时数 `.runtime/tmp/` 与 `.runtime/sessions/` 两址（盘面游标 10:12 之后写盘的班次不会推游标＝游标滞后，非班次不存在）。

**死班 `st-qoder-p06-1015-08` 判死三证（在册处方：三证齐才可接手）**：①`.runtime/sessions/st-qoder-p06-1015-08/heartbeat.jsonl` 末行 `status:"exited"`・`reason:"idle timeout"`・`idle_seconds:1802.3`・ts=2026-10-15T03:07:31Z（＝本地 11:07，date 校时）；②`Get-Process -Id 47980` 查无；③队列面 `dead/pending/processing` 无该 sid 袋（p06 最新袋＝`q-20261015-st-qoder-p06-1015-07-0001`）且 `git log --all` 按 `p06-1015-08` 尾标命中 0。**残留产出面实测**：`edit_log.json` 23 件补键＋10:41 翻 `07b`＋12:49 新建 033 卡＋13:33 `newcard.txt`＝**全部未入袋**（其成果只活在主区盘面）。

### 本班领用面（实测，非转述）

1. **骨架 empty 面＝不领（第八班复证）**：完整 walk 550 件按「裸骨架 `^TDM-*__<kind>.yaml$`／具名子题」二分×状态普查＝empty **186 全部落在骨架面**、具名 empty＝**0**；骨架四态合计 282・具名合计 268・加总=550（互斥分母自证）。在册停手口径（骨架转正须③④席先产具名子题）延续，本班零张骨架卡自行填死。
2. **③席 20261015-p03-05 批 6 行**（真源 `data/strategy_intake/lane_p0_obi_candidates.csv` 本班 DictReader 全读＝**39 行**，mtime 10:29；birth_batch 分布 obi-probe 1／p03-01 7／p03-02 5／p03-03 11／p03-04 9／**p03-05 6**＝行号 33–38，本班为首个领到的⑥班）：

| 候选 | ③席在册闸读数（逐字取 orthogonal_gate_note） | 本班处置 | 判据 |
|---|---|---|---|
| CAND-P0-MIAUTOC-033 日内分钟收益一阶自相关 | pass max\|corr\|=0.1297 most_similar=avg_abs_ret_z20.csv rc=0；册内自查 vs034 0.0934／vs036 0.1129／vs026 0.1165／vs035 0.0177 全 ≤0.12 | **收编死班所造具名卡 `TDM-E-L9-A01/calibration/08_intraday_return_autocorr_lag1`**（blocked_on_impl） | 本班自家尺两轮：门柱 12 项对 `git show HEAD:A01/03` 全 CLEAN（window 全字段・pillars_numeric 整块与键集・buckets.type+min_obs_per_bucket・discipline・signal_kind・target.primary/secondary・oos_window_ref==本卡 window.oos・无 generated・buckets.on 不含数值）＋③席行逐字段 verbatim 10 项全等（definition_zh/sample_window/example_value/orthogonal_gate_note/data_source_table＋037 与 038 三面）⇒ 非采信死班自报，尺与清单见 R1 |
| CAND-P0-MIEXTPOS-034 日内极值时序位置差 | **reject** 0.4998 most_similar=lu_ratio.csv rc=5；60min 同名档 reject 0.3677＝最相似员换档即换；hpos×lpos 日频 +0.9941 | **不立卡** | ③席在册原文"判重复，不产卡"＝不利侧定案，本席不翻（SOP『不过闸记"重复"，喂 mined_out』） |
| CAND-P0-MICLOSEPOS-035 日内收位值（区间位置维） | **reject** 0.5966 most_similar=lu_ratio.csv rc=5；60min 档 reject 0.5969；档间 corr 0.9998＝档不变对象 | **不立卡** | 同上；③席该行另**更正上班派生判据**"形状/构成型（无量纲）在本池可过"⇒ 过闸分水岭是"时点/时序记忆维"而非无量纲与否，本班只转抄、不据此重判任何在册卡 |
| CAND-P0-MIKURT-036 日内分钟收益标准化峰度 | 闸面 **pass** 0.1968 most_similar=lu_count.csv rc=0，**但③席判重复**：与在册 CAND-P0-MIJUMP-026 同窗日频 \|corr\|=0.9893≫0.3＝同一对象两个名字 | **不立卡** | ③席在册结论"不作为新轴交付"优先于闸面 pass；该行同时登记"正交闸池外重复盲区"（闸只吃 `--pool` 目录、看不见候选册自家序列），呈批在③席 p03-05 台账，本席不代裁、不重复立号；本卡 08 面 `gaps_no_source.orthogonality_blindspot_036` 已承此事实 |
| CAND-P0-MI60CONTRAST2-037 60min 档第二批对照行 | 非信号行无闸 | **整行入卡 1 处**＝08 卡 `data_binding.band_caliber_precedent_037`（definition_zh/example_value/downstream_meaning 三面逐字，本班实测三面 verbatim 全等） | 该行的"60min 档 f_autocorr 不可产（每股每日仅 4 根、nb>=3 自由度不足＝该轴在 60min 档无源，禁写等价复算）"正打本卡唯一候选，载体正确；034/035/036 三构造未成卡，故不另设载体 |
| CAND-P0-MIPORTRAIT2-038 楼1 方言与成本口径画像行 | 非信号行无闸 | **整行入卡 1 处**＝08 卡 `data_binding.dialect_cost_precedent_038`（两面逐字＋downstream_meaning） | 其中 (c) ch_reader **自动注入 FINAL**・(a) corr 在本方言是聚合函数须手写 dotProduct・(d) 数组聚合单月 2.2s 与标量同量级＝本席与⑤⑦席的写法/成本前置，落在同批唯一成卡件面 |

3. **⑩线长席第七单 §6「⑥」行三件**（真源 `dispatch/daily_dispatch.md` 第七单，本班逐行读）：
   - **首件＝自家死信内容级分诊**：p06 名下 dead **8 枚**（本班开班实测，⑩点名 5 枚＝ledger 冲突＋ghost 口径，本班按 sid 全扫＝8）。逐件四态（袋字节→git blob sha1 对 HEAD 现值／全史／盘面三面对拍，尺 `.runtime/tmp/p06_1015_09/triage.py`，只读零写盘；`dead-archive --content-level` 正门本班实跑被拒＝"serializer 租约存活（pid=23976）拒绝并行维护操作"，本班未绕闸、改走只读分诊＋本袋承接）：
     * 死因族＝landing 双侧皆改真冲突 **3 枚**（01-0002／03-0001／07-0001）＋ ghost_session 属主已死 **5 枚**（02-0001／04-0001／05-0001／05-0002／06-0001），与⑩§1 的 93 枚三族同链。
     * 件级＝**A_LANDED 0／DISK=BAG 22／NOT_LANDED 20**（42 件次）；NOT_LANDED 再按内容级细分：台账件 **7 枚全部"按 `## ` 切块逐块 verbatim 命中盘面"、删除集=空**（01/02/03/04/05-0002/06/07 各袋 3–10 块全命中）⇒ 内容级已承接；游标件 6 枚 DIVERGED＝游标语义为最新者胜（盘面=07 版）非内容丢失；02 班 8 枚骨架卡回填 **DIVERGED 且盘面字节更小**（袋 2294–2679B／盘面 1107–1170B）＝外来重生波把骨架面打回，**本班不回吃**（裸骨架卡回填已被 v1.5.1 口径废弃，正解是等③席产具名）；07 班 P2-04/06・/07 两枚 DIVERGED＝盘面现值已被考工席改写，本班实测两件的 `oos_window_ref` 键**仍在盘面**（`grep -c "^oos_window_ref:"`＝1／1）⇒ 07 班那半腿未丢、由盘面承接；05 班 A17/02 一枚 DIVERGED＝本班当日撤键所致（键撤是⑩令，见下条），翻态与凭据整块搬入本节。
     * 本班处置＝**8 枚一律不 requeue**：其内容归宿全部由本班本袋盘面超集承接（22 件 DISK=BAG 直接入袋＋7 枚台账块＋6 枚游标＋2 枚 P2-04 键面已在盘面＋8 枚骨架面按新口径废弃）。销账动作本班**未执行**＝`dead-archive` 需 serializer 租约空闲，本班不抢维护窗；留本行判定与复跑尺，下班或⑩在排空后走 mv 通道。
   - **续补余下缺键 2 张**（⑩本班基线 25→2）＝本班实测这 2 张**一张无源、一张挡道，硬补数为 0**：`TDM-X-S1-03/comparison/02_dualwindow` 实测 `window.oos=null`・`oos_window_ref=null`・无 data_binding 段＝在册零可抄源，承 OD-26 呈批面不动（追加本班复测一行）；`TDM-P-P1-03/comparison/03` 实测 `window.oos=['2025-10-09','2026-09-30']` 可抄，**但盘面该件含⑤实现席 p05-1015-01 未落地改动**（`git diff --numstat`＝**+15/−1**，−1 行＝把 `blocked_on_impl` 翻成 `preregistered`，+15 行＝⑤席落地回执注释）⇒ 袋=整档快照，随袋即把他班判据面写进本班 commit（在册归属篡改形态），本班**不改该件**，新立 OD-30 呈请指定唯一纠正出口。
   - **两枚非在册顶层键归口＝本班已撤**：⑩§3 实测 `unblocked_20261015`（L9-A17/02，1015-05 班所加）与 `examined_face_20261015`（07b，死 08 班所加）是卡面非在册键，令"入卡面 schema 册或撤"。本班判**册不存在**（承重证据：`config/strategy_card_lifecycle_map.yaml` 头部 boundary 明列"不含卡内单张卡的全部字段（骨架 L-5：叶层不枚举）"，真源=`card_state_vocabulary.yaml` 只控状态词表，全库 `grep -rln oos_window_ref docs/01_policies_and_standards/ config/`＝卡面之外 0 命中）⇒ 立册＝新增治理册且无替代条目，违净零且越⑥写域；故走"撤"，**信息零丢失**：两块原文（26 行／15 行，sha256 前缀见下）整块搬入本节，卡面改按在册体例留 `# [st-qoder-p06-1015-09 2026-10-15]` 尾注一行指针。撤后两件本班实测＝YAML parse OK・difflib 对 HEAD **plus=3／minus=1**（唯一减行＝status 行）・九个冻结面（window/buckets/pillars/pillars_numeric/target/oos_window_ref/discipline/signal_kind/card_id+node_id+family）逐值不变・键面 `unblocked_20261015`/`examined_face_20261015` 计数 0。
4. **⑨成绩官 p09-09 节 §3 [对照] 申请单**＝**零新开**（6 行新判卷无一属"只栽 OOS 一根柱"形态）；该节另在册点名"未销的 [对照] 扩面 rows[8]/[75]/[77]/[79] 本席不重复派，仍等⑥席并批"＝与本班 06 班在册停手（OD-15 追加面）同条，**本班不重复领、不新开号**。该席呈批 **P-6**（有符号门柱把"反向稳定"与"零信息"洗成同一 fail）末句路由"若裁另立反向卡，请⑥席按 `TDM-E-L2/ablation/02` 反号命题 preregistered 新卡"＝**条件成就未成立**（Owner/⑩ 未表态），本班不 prereg 反号卡（先决条件是 Owner 裁，抢跑＝把噪声定门柱）。
5. **②数据建设席 unblocked.md 10:4x 段（p02-04）**：零新解锁，且把上一班"consensus 20 日修正窗从 10-12 起算"的建议**改判为 10-08 起算**（真因＝`_INCREMENTAL_OVERLAP_DAYS=3` 使 10-08/09 两日未进产出行集，非"无 EPS 不产行"；内容级读数 002594/10-08 eps 4.27→4.286・300750/10-09 eps 20.831875→20.8745）⇒ 本班**只登记**：该起算点对已 preregistered 的 A17/03 卡是窗末端事（该卡 OOS 末 2025-09-09，不触改判面），不动卡面一字；另记该段对⑥/⑨的告警"tick_data 近端 10-09 起逐日塌陷至 10-13=0、10-14 仅 14.6k"⇒ **任何吃"近 5 交易日分笔"的卡现都不具可考深度**（本班零张此类新卡投产，L9-A02 族 9 张 blocked_on_data 保持不动）。

### 本班成袋＝死班未落地产出整面承接（46 件）

19 张未跟踪具名卡（`git ls-files --others` 实测，全部 `made_by` 属⑥席：1015-03×4・1015-04×7・1015-05×2・1015-06×2・1015-07×3・1015-08×1）＋23 张补键件（死 08 班 `edit_log.json` 面，本班逐件对 HEAD 做 difflib＝**23/23 plus=1・minus=0・唯一加行 `+oos_window_ref:`**，DIRTY=0）＋2 张翻态件（A17/02・07b，撤键后 plus=3/minus=1）＋本台账＋游标＝46 件。**本班新造卡 0 张**（③席 p03-05 唯一过闸候选的卡已由死 08 班产出且本班尺验合格，重复造卡＝同 node 同号位双载体）。creation_token 面：19/19 在投影册 `capability_canonical_file_registry.yaml` 盘面有 token 与 created_by（含死 08 那张 `exam-card-tdm-e-l9-a01--calibration--08-intraday-return-autocorr-lag1-20261015`）⇒ 本班**未重复登记**；该热册含他班 4,9xx 条在途条目，照在册口径**不随袋**。

### 呈批两件（正文寄存本台账——04 区呈批真源本班复测仍两头不可写：`docs/04_research_records/mining/ledgers/nightmine_20261010/05_owner_decisions.yaml` 盘面 7,062B／`git status`＝**A**（他班 staged・从未落地）／`git show HEAD:` 报 "exists on disk, but not in 'HEAD'"；随袋＝整档快照吸收他班未落地条目＝归属篡改，故仍寄存）

```yaml
- id: OD-29（本班新立）
  项: 考试卡卡面的 provenance／审计注释应有何落点——⑩令"入卡面 schema 册或撤"两选项在本库不对称，请裁并给成文口径
  实测分母: 本班字段级实测＝卡池 550 件的顶层键频度梯度为 schema_version/card_id/node_id/family/title_zh/hypothesis/window/buckets/status 各 550・pillars/target 548・lineage 547・
    discipline/signal_kind/pillars_numeric 364・preregistered_by/at 348・data_binding 342・oos_window_ref 341・generated+tdm 186・origin 111，长尾 58 种键各 ≤58 且无一册枚举；
    图15 `strategy_card_lifecycle_map.yaml` boundary 明写"不含卡内单张卡的全部字段（骨架 L-5：叶层不枚举）"，`card_state_vocabulary.yaml` 只辖状态词表；
    被令撤面的两枚键＝卡面 26 行／15 行注释块（信息量＝翻态触发件・本席自测四态读数・"翻态非改判据"承重理由・未触九面声明・残余范围），本班已撤出卡面并整块搬入本节
  为何要点头: (a) 裁"另立卡面字段册"⇒ 属新增治理资产，净零须声明替代/合并对象（现无可并册，图15 已明确让位），本席不自立；
    (b) 裁"注释一律只准进台账"⇒ 本班体例即终态，代价＝⑦⑧排考面在卡上读不到"为什么这张已考 4 次的卡还写 preregistered"，须跨册检索；
    (c) 裁"卡面可留 YAML `#` 尾注"⇒ 本班今日所加两行尾注即最小形态，无需新册（本班现走的即此路的临时态）
  不点的后果: 每班各挑一种注释落点（顶层键／尾注／台账），⑩巡检的"变动键分布"继续出现无家键名，且卡面字节面不可逐字对拍（通令第十二条复述的序列化回写风险就来自这类加键）
  凭据: 本班顶层键频度尺（正则首列键计数，正文可原样复跑）・strategy_card_lifecycle_map.yaml 头注原文・撤键前后 difflib 读数（plus=3/minus=1 两件）・死班 edit_log.json 与 07b 卡面 git show HEAD 对比
- id: OD-30（本班新立）
  项: ⑥席补键单与⑤席／考工席在途件撞在同一张卡上——请指定唯一纠正出口（题面＝`TDM-P-P1-03/comparison/03` 的 `oos_window_ref` 谁来补）
  实测分母: 本班该件三面对拍＝HEAD `status: blocked_on_impl`・盘面 `status: preregistered` 且 **diff +15/−1**（−1 行即⑤实现席 p05-1015-01 的翻态行，+15 行＝其落地回执注释，含"折叠闸未取 phase>=3"的偏差记档与探针册处方）・
    `window.oos=['2025-10-09','2026-09-30']`・`oos_window_ref=null`；同族姊妹两件 `TDM-P-P2-04/calibration/06`・`/07` 盘面 diff **+32/−36**・**+27/−28**，加行内容含 `redline_gate`／`confound_gate`／`threshold_placement_gate`／
    `ballast_subgroup_gate`／`signal_definition_frozen`／`universe_note`／`extra_report` 等**柱级新面**且 status 直翻 examined（本班实测其 oos_window_ref 键仍在盘面＝07 班那半腿未丢）
  为何要点头: 本席写域＝"改指向"（把已有冻结窗抄进 `oos_window_ref`），**不含**把他班未落地的翻态与新增柱随袋落地（袋=整档快照）。三种出口请择一：
    (a) ⑤席／考工席自袋落地后，本班下一班补键；(b) Owner/⑩ 授权本班把该件整面当⑥席承接件落地（须由授权人署名承担他班判据面的归属）；
    (c) 判考工席在盘面对 preregistered 卡新增柱级面本身违"先冻结后跑"，先回退柱面再谈补键——**此择涉考工写域，本席只报事实不代指认**
  不点的后果: ⑩基线"缺键 2 张"每班复量同一张却每班都出不了手（与 OD-20/24/26 同型第五、六例），且考工在途柱面继续只活在主区工作树，一面按 HEAD 排考、一面按盘面判据，两侧读到的卡不同
  凭据: 本班三件 `git diff --numstat` 原样读数・死班 07-0001 袋与盘面 P2-04/06・/07 的 blob 分叉（同长度异字节）・unblocked/to_impl 两册中⑤席 p05-03 与考工 run_id `p08b-1015-04-card07` 在册行
```

### 撤键两块证据全文（原在卡面顶层键，本班 ⑩ 令撤出，此处为唯一存面）

```yaml
# 存面一：TDM-E-L9-A17/calibration/02_研报评级调整事件研究（原键 unblocked_20261015，26 行，sha256 前缀见 findings 2）
```

（全文见 `.runtime/tmp/p06_1015_09/A17_block.txt`；关键读数四句：①触发＝②席 p02-1015-01 建设单 B-3 派生回填，该节明言"卡状态改判不归本席"；②本卡 `data_window_evidence` 自带命令实测 `rating_change` 非空率 91.12%（146,940 中 133,888）≥60% 门槛、下调 19,522 条（限 publish_date≥2022-01-01 仍 11,324）≥300 门槛；③本班冻结窗内实测 IS 2019-01-04..2023-12-31 下调 9,816 事件/1,766 符号/1,335 发布日、OOS 2024-01-01..2025-09-09 下调 4,753/1,441 ⇒ `min_obs_per_bucket=60` 与事件≥30 两门槛两窗皆超线；④②席"10 月明细腿 0 行⇒事件窗建议截到 publish_date≤2026-09-30"对本卡是**空操作**（窗末端 2025-09-09 早于缺口起点），九个冻结面一字未动。）

```yaml
# 存面二：TDM-X-R1-01/comparison/07b_熔断五级梯度减仓对照_复位阶梯锚定版（原键 examined_face_20261015，15 行）
```

（全文见 `.runtime/tmp/p06_1015_09/07b_block.txt`；关键读数四句：①触发＝⑩第六单处置单 D-01 令"⑥席当班把两卡翻至在册终态或挂禁考标记"，姊妹件 07 三面实测已 examined＝零动作，本件是 D-01 剩余面；②分数册磁盘面实测 84 行・sha256 前缀 4f986ec7143a690f・册 mtime 09:38:34；③该卡 rows[68,69,70,71] 四行 card_id 全等且 verdict 全=fail；④4 行 > SOP §4 同 holdout ≤3 轮上限，超限后"换 fresh holdout or 封存"沿用⑩在册呈批第 4 项属 Owner，死班与本席均不代裁。）

### findings（本批实测，非转述）

1. **本班首件价值＝发现"⑥席产出从未落地"不是一班而是六班**：03–08 共 6 个班次（含死 08）的全部卡面动作只活在主区工作树＋已死袋 blob，`git ls-tree -r --name-only HEAD -- .../exam_cards/entry_flow/L9/` 对 19 件全查无；本班按"盘面超集承接"一次性把 46 件推正门。风险窗口如实上报：blob 会被 purge，抢救有时限（在册处方），故本班把"落地"排在分诊之后、写在同一袋。
2. **尺的自证与一次自犯**：本班所有存在性判定走进程外三面（`git ls-files --others`／`git rev-parse HEAD:<path>`／`git cat-file -e`），未以 Read 命中作正证；`triage.py` 首版把 `files` 当 dict 索引（实为 list of dict）⇒ `TypeError` 而非"零命中"，属**响亮的坏**，改形制后重跑；撤键两块证据全文落盘实测＝`.runtime/tmp/p06_1015_09/A17_block.txt` 26 行／2821B／sha256 前缀 `1a66c15cba19`、`07b_block.txt` 15 行／1597B／前缀 `874d58d62481`（落笔前逐文件独立哈希，非拼接面）。
3. **考工席在盘面对 preregistered 卡加柱**（最高优先移交面）：`TDM-P-P2-04/calibration/06`・`/07` 两件盘面含 4 枚新 `*_gate`＋`signal_definition_frozen`＋`universe_note`，且 status 直翻 examined，对 HEAD＝+32/−36・+27/−28。按"先冻结后跑"，加柱＝改判据面，写域不属考工；本班**不改、不随袋、不判死**，只在 OD-30 摊开事实并建议⑩定唯一纠正出口（本席不指认意图）。
4. **游标滞后不等于班次不存在**（取号纠偏见开班节）：旧址盘面游标 last_batch=07、`last_run 10:09`，而 08 班 10:22 起手、12:49 还在写卡。判"上一班已收尾"须加一尺＝`ls .runtime/tmp/p06_*`＋`.runtime/sessions/*`；只读游标会既漏号又漏产。
5. **本班未跑任何考试、未跑正交闸、未跑 CH 探针**（冻结与运行分离）：033 卡可算性与过闸证据全部转抄③席在册行并明标"本班未重扫"；034/035/036 的 reject/判重复结论逐字承③席不利侧定案，本班无一次重算。
6. **队列与租约面**：本班 `dead-archive --content-level` 正门实跑被 serializer 租约（pid=23976）拒绝，未加旗绕行；`commit_queue.py status` 实测 pending 2／processing 2／done 773／dead 289（total 1066），与⑩第七单 13:43 读数（94/4/801/175）相比 dead 由 175→289＝⑩§1 雪崩在继续，本班分诊只做自家 8 枚、不代拆他席袋。

### 自检两轮（两轮都核对）

- **R1（门柱与冻结值逐字一致＋单变量核对）**：①收编卡 08＝**12 项门柱尺全 CLEAN**（对 `git show HEAD:A01/03` 逐面 parsed 全等：window 含 regimes/frozen_note 全字段・pillars_numeric 整块且键集相等・buckets.type+min_obs_per_bucket・discipline・signal_kind・target.primary/secondary・data_binding.target_source；自判项：`oos_window_ref==本卡 window.oos`・无 `generated`・`buckets.on` 不含数值）＋**10 项 verbatim 尺全等**（③席 CSV 行 definition_zh/sample_window/example_value/orthogonal_gate_note/data_source_table＋037 三面＋038 两面）；尺＝`.runtime/tmp/p06_1015_09/`（正文两列读数可原样复跑）。②23 张补键件逐件 difflib＝plus=1・minus=0・加行前缀 `+oos_window_ref:`（DIRTY=0）。③2 张撤键件＝plus=3・minus=1・九冻结面 parsed 全等・两枚被令键计数 0。④**对照卡 diff 项＝本班 N/A（如实记不记绿）**：领用面零新 [对照] 申请（⑨p09-09 §3 明书零新开），在册未销扩面 4 行承 06 班 OD-15 追加面不重复领，故无 champion/challenger 可 diff。⑤**零张裸骨架卡被本席自行填死**＝骨架 empty 面 186 件本班零写入（R2 卡池状态面反证）。
- **R2（归属·净零·保底·进程外核实）**：①卡池件数 550→**550**（本班零新建文件，收编件由未跟踪转跟踪）；状态面 preregistered 177／empty 186／blocked_on_data 71／blocked_on_impl 45／examined 71（本班盘面读数，四态变动全为承接与翻态面：07b preregistered→examined 1・A17/02 blocked_on_data→preregistered 1，均为上班已写盘面、本班只落地）；②本班 commit 触及文件 46 件全部 `lock_files.py acquire-batch` 实测 **acquired=46 denied=0**（走 `--skip-naming-check` 在册逃生口，理由＝新卡名沿用同族 `TDM-E-*__calibration__NN_*` 体例供⑦⑧与⑨ card_id↔文件名互推消费）；③会话＝`SessionRegistry().register(st-qoder-p06-1015-09, pid=0, held_files=46)` 实测 `get_session` 转真，心跳守护 pid=49864（首跑 `_spawn_heartbeat_daemon` 传 str 报 `TypeError` ⇒ 按签名 `root: Path` 改传 Path 成）；④台账追加走 `safe_write_text` CAS＋**纯前缀断言**（删除集=空、写后进程外读回）；⑤热册照在册口径不随袋（投影册／生命周期图／ruling_registry 一字未动）；⑥净零＝零新 gate・零新规则册・零新注册表・零脚本入册（分诊与核验尺留 `.runtime/tmp/p06_1015_09/`）；呈批 2 件均为**新立**，OD-26/OD-15 只追加复测行不新开同义号；⑦保底＝领用面 **100% 处置**（③席 6/6・⑩三件三处置・⑨ [对照] 面 0 领＋P-6 未触条件不抢跑・②席 1 段登记・骨架 186 按在册停手・自家死信 8/8 内容级分诊），卡面动作 44 件（19 收编跟踪＋23 补键＋2 撤键翻态）。
- **本班实际耗时**：开班 reaper 首读 15:30:57 → 本段落笔 `date` 实测 **16:17:33** ＝**46.6 分钟**（超 SOP 3-B 估 20 分一倍以上；主因两条如实入账＝自家死信 8 枚逐件三面对拍＋非在册键归口需先证"册不存在"才敢撤）。

### 更正块（同班追加，旧案卷不删）· 16:41 · st-qoder-p06-1015-09

**本节改一处本册自报为假的句子，不动任何判据面。** 上文「本班成袋＝46 件」与游标里的"整面推正门"字样按实跑结果更正如下（落笔时按"一袋 46 件"写的，实测被正门拒）：

1. **拆袋实况（QueueReject 原文）**：首次 `--enqueue` 投 46 件，正门报 `单批 46 文件超上限 40（R2 大批硬顶）：请拆分为多个语义批次入队（失败早暴露不互相拖累）；确属原子大批用 --allow-oversize-batch`。本班**未加 `--allow-oversize-batch` 绕行**，按在册处方拆语义两袋、拆前实测件面零交集且 23+23=46 加总相等（尺 `.runtime/tmp/p06_1015_09/bagA.txt`／`bagB.txt`）：
   - `q-20261015-st-qoder-p06-1015-09-0001`＝23 件＝19 张未跟踪具名卡收编＋2 张撤非在册键翻态件＋本台账＋游标；
   - `q-20261015-st-qoder-p06-1015-09-0002`＝23 件＝补键件面。
   两袋各 `ENQUEUED` 成功，`--adopt-prior-work --allow-non-worktree` 全程带（认领死班工作区面并留审计）。
2. **同会话多袋的在册风险如实摊开**：本席指令卡与根宪法 §2第6条口径＝"一值守一袋"，本班成两袋的唯一因由是队列硬顶而非本班贪多；两袋件面零交集（脚本断言），故不触发"同件后袋吞前袋"形态，但**台账件在两袋中只属 0001**——本节即 0001 版的严格超集，由第三节袋 `0003` 承接（若下班见 0001/0003 撞面，按在册"后袋须为前袋严格超集"读，勿判本班自撞）。
3. **骨架卡退回单本班未开**（工序 2 的落 `feedback/to_miners.md` 动作）：理由＝停手口径已在册生效（③席 p03-05 游标自报"033 待⑤席物化＋⑥席成卡，本席无新骨可产"，且本班实测具名 empty=0），再投退回单＝给同一事实派第二张工；⑩第七单 §6「⑥」行末栏亦明书"empty 186 全 generated 不再领"。
4. **本班收尾前实测进程外面**：`python scripts/commit_queue.py status --session st-qoder-p06-1015-09` 实跑读数＝total 2・`-0001` **processing**（created_at 16:37:43）・`-0002` **pending**（created_at 16:38:39・position_ahead 0）・lease holder_pid=41936 alive=true；同分钟 `git ls-files --others` 复量＝19 张收编卡仍未跟踪（落地由传送带异步完成，本班不轮询等待、更不据此自宣落地）；锁面 46/46 已被 `ENQUEUE-RENEW` 续租 ttl=7200s；心跳守护 pid=49864 存活。

### 收班补记 · 16:50 · st-qoder-p06-1015-09（三条终验读数，全部本班进程外实测）

1. **本班实际耗时改终值**：开班 reaper 首读 15:30:57 → 收班 16:50（`date` 实测）＝**79 分钟**（上文 46.6 分只是首段落笔时刻，SOP 3-B 估 20 分＝偏差 +295%；三条增量如实入账＝自家 8 枚死信逐件三面对拍、非在册键归口须先证「册不存在」、46 件超硬顶后的拆袋与严格超集补投）。
2. **袋字节↔盘面逐件对拍终验**：本班三袋共 48 件次，blob 与盘面字节**相等 46 件・不等 2 件**，且不等两件恰是 -0001 内的台账与游标（＝预更正版，由 -0003 以严格超集承接，非丢失）；-0001・-0002 均 state=processing・-0003 pending。本班不自宣落地，判据只认此对拍表。
3. **骨架零填铁律的反证尺**：以 mtime>15:30 为谓词扫全卡池＝本班值守内被任何进程触及的卡 6 件，其 status 逐件实测为 preregistered/examined（**无一为 empty**），其中 2 件是本席撤键件（A17/02・07b），另 4 件（L2-04/02・L9-A01/02・P2-04/06・P2-04/07）属考工席值守内推进（与 OD-30 同链）⇒ 上文 R2「零张裸骨架卡被本席填死」由 mtime+status 双谓词独立成立，不靠本席自述。

### 终态补录 · 16:48 · st-qoder-p06-1015-09（上文收班补记第 2 条是值守中时点读数，本节改判终态、旧案留卷）

1. **本班五袋终态（`status --session` 16:48 实读）**：-0001 **done**・-0002 processing・-0003 **dead**・-0004・-0005 pending。上一节写「-0001・-0002 均 processing・-0003 pending」是 16:41 读数，-0003 于 16:45:13 判死＝**追加型台账里的时点计数自犯**，按在册另起留旧案不涂改。
2. **-0003 死因与处置（读回 dead_reason 后修因，禁盲 requeue）**：`landing 异常: [landing] 非注册表族件双侧皆改真冲突（整文件三方）: ledger.md`——点名的是 ledger 而非游标，且**严格超集不吃整文件三方规则**（-0003 袋面 174,111B 是 dev 现值 171,570B 的超集仍判死）。本班据此**不 requeue -0003**（会把已被 -0004 取代的旧面再推一遍＝回退弹形态），改为拆两件各自单投：-0004＝ledger（实测其 base_head 63a5ee4c66==当时 HEAD・袋面 175,418B・`git show HEAD:…ledger.md`＝171,570B 为严格前缀）・-0005＝checkpoint 单件。死袋留原位，销账须等排空后的 mv 通道（本班全程未 mv 他人袋、未动 dead 目录）。
3. **落地判据与一处盘面伪形**：-0001 落地正证＝`git show HEAD:` 对收编卡 `TDM-E-L9-A01__calibration__08_intraday_return_autocorr_lag1.yaml` 返回 13,776B（入 HEAD）；同刻 `git ls-files --others` 仍报 19 张未跟踪＝**主区 index 面滞后于分支 ref**（正门在 serializer 工作树推进 dev，主区暂存区未随之更新），「卡未落地」是误读；下班勿按该读数复投同件（判据只认 blob↔盘面对拍＋`git show HEAD:`）。


## 10-15 17:41 · st-qoder-p06-1015-10 · ⑥制卡席（③席 20261015-p03-06 批 7 行 100% 处置＝新卡 1 张（L9-A02/12 二阶自相关，blocked_on_impl）＋不立卡裁定 5 条＋非信号行整行入卡 1 处／⑨成绩官 p09-1015-10 班 [对照] 成卡 1 张（X-R1-01/07c 披露声明版，champion=07 判据 16 面逐字零改）／⑨席 p09-1015-11 班〔对照〕停手＝并入在册 OD-15 追加面（实测 552 卡面读数切段键 0 张）／OD-26・OD-30 各追加复测 1 行／骨架 empty 186 第九班复证停手）

**开班三实测**：①Python 3.12.8。②`python scripts/lock_files.py cleanup` 实跑＝**CLEANED 11 个死锁**（p08 台账＋游标、P2-04/06・07 两张卡面、p01 台账＋游标、to_builder.md、known_data_gaps.yaml、working_ref_sweep_20261015 三件）＋**SALVAGED 两会话遗物**（st-qoder-p02-1015-06・st-qoder-p05-gpu-1015-01，各 merge=skipped/stash=0 件/释放 claim=0）。③`python -m zephyr.trading.process_reaper --status` 实跑＝source=live・last_run=2026-10-15 16:52:02・scanned=42・whitelist_hits=28・killed=1・reported=4・ghosts 全 0。防重入＝游标盘面"本班已收尾"・last_batch=st-qoder-p06-1015-09・last_run 16:22；按在册"取号须数三址"本班另实测 `.runtime/tmp/` 与 `.runtime/sessions/` 均无 10 号先占⇒取 **10**。

**水位如实上报（在册事故形态同形，本班未据此降工）**：开班 reaper 读数 `commit_pct=91.08`・`ram_used_pct=67.4`・`cpu_pct=79.8`・`degraded=True`・`breached=['ALERT-SYS-003']`・`worktree_changes=5472>50` ⇒ 本班全程串行、零并发子代理、零 CH 探针、零长跑批；三条 python 冷启实测被拖过 2 分钟墙转后台（`find`／`batch_creation_tokens --help`／token 实投），故本班一律"只读快查在前＋重活转后台"，**未给提交套限时壳**（在册自犯形态：掐死预检而 rc=0 假成功）。

### 本班领用面（实测，非转述）

1. **骨架 empty 面＝不领（第九班复证）**：完整 walk **550 件**按「裸骨架 `^TDM-*__<kind>.yaml$`／具名子题」二分×状态普查＝具名 364（preregistered 175／examined 73／blocked_on_data 71／blocked_on_impl 45）＋骨架 empty **186**；**具名 empty=0**、骨架+具名加总=550（互斥分母自证）。本班零张裸骨架卡自行填死。骨架退回单**不重开**（停手口径在册生效），但本班新出一条**归口方向单**（见 findings 第 1 条），二者非同一件事。
2. **上班袋终态与 index 滞后伪形复证**：`python scripts/commit_queue.py status --session st-qoder-p06-1015-09` 实测＝`-0001`/`-0002`/`-0004`/`-0005` **done**、`-0003` **dead**（dead_reason＝`landing 异常: [landing] 非注册表族件双侧皆改真冲突（整文件三方）: ledger.md`），当前 HEAD `cd754ff8fd` 恰＝`-0005` 的 landed_id。`git status --porcelain -- .../exam_cards` 对 19 张收编卡同时报 `??` 与 `D ` 双行；本班逐件 `git cat-file -e HEAD:<path>` 实测 **19/19 在 HEAD**（尺 `.runtime/tmp/p06_1015_10/faces.py` 同批）＝主区 index 滞后于分支 ref 的在册伪形 ⇒ 本班**未复投同件、未对这批路径做暂存动作**（防把 `D ` 面带进袋）。-0003 死袋本班**不 requeue**（其内容已被 -0004/-0005 取代，复投＝回退弹形态），销账仍等排空后的 mv 通道。
3. **③席 20261015-p03-06 批 7 行**（真源 `data/strategy_intake/lane_p0_obi_candidates.csv` 本班 DictReader 全读＝**46 行**，mtime 16:10；birth_batch 分布 obi-probe 1／p03-01 7／p03-02 5／p03-03 11／p03-04 9／p03-05 6／**p03-06 7**＝行 39–45，本班为首个领到的⑥班）：

| 候选 | ③席在册闸读数（逐字取 orthogonal_gate_note） | 本班处置 | 判据 |
|---|---|---|---|
| CAND-P0-MIAC2-039 日内分钟收益二阶自相关（跨两步路径记忆维） | 过闸 verdict=**pass** max\|corr\|=0.2396 most_similar=avg_abs_ret_z20 rc=0；册内自查 vs 033=0.1197／vs 013=0.0482／vs 014=0.1281／vs 024=0.1067／vs 026=0.0571／vs 036=0.0910 全 ≤0.13；尺双对照＝池成员自投 reject 1.0000 rc=5（尺能红）＋随机高斯 ctrl pass 0.1414 rc=0（尺非恒拦）；**本班轴净增=1** | **成卡 `TDM-E-L9-A02/calibration/12_intraday_return_autocorr_lag2`**（blocked_on_impl） | 本班自家尺内建断言（尺 `.runtime/tmp/p06_1015_10/make_card1.py`）：门柱 12 项逐字对 `git show HEAD:A01/08`＋③席 039 行 5 面 verbatim＋045 行 3 面 verbatim；`oos_window_ref` 与本卡 `window.oos` 同锚；`buckets.on` 不含数值；无 `generated` 键 |
| CAND-P0-MIFLIP-040 日内方向切换频率 | **判重复**（不入过闸账）：池面 pass 0.1615 rc=0，**但册内自查 vs 033=0.6995≫0.3**＝同一"路径记忆"轴第二种写法 | **不立卡** | ③席在册原文"同轴两形禁各计一员"＝不利侧定案，本席不翻 |
| CAND-P0-MIIRREV-041 日内收益时间不可逆性（三阶时间箭头） | **判重复**：池面 pass 0.2839（贴线距 0.3 仅 0.0161），册内自查 vs 033=0.3543>0.3 | **不立卡** | 同上；本班另把该自查值写进 A02/12 面 `gaps_no_source.non_duplication_note_040_041` 供 ⑨ 席对拍 |
| CAND-P0-MIUDRUN-042 涨跌游程时长不对称 | 池面**真退码 reject** 0.6442 most_similar=lu_count_z20 rc=5（③席自陈首投曾把管道尾命令 rc 当闸 rc，已按台账§七自犯条更正）；册内自查 max=0.1947 | **不立卡** | 池拦即定案；"池拦而册内不撞"是闸的池面够用之反形，本班只转抄 |
| CAND-P0-MIDWELL-043 日内价格带停留熵 | **判重复**：池面 pass 0.1586，册内自查 vs 014=0.5166>0.3（日间变异主要由开盘段价格带偏移驱动） | **不立卡** | 同 040/041；③席该行另记"本班 v1 版漏除 nb 致读数≈240 倍已作废重写"，属③席自纠面 |
| CAND-P0-MIVOLCOM-044 日内方差时间重心偏移 | **判重复**：池面 pass 0.2118，册内自查 max=0.6791（vs 014）、另 0.6465（vs 024）≫0.3 | **不立卡** | ③席结论"把 024 的两端二值切成连续重心不产生新轴"优先；本席不重算 |
| CAND-P0-MI60CONTRAST3-045 60min 档第三批对照行（非信号） | 非信号行自身不入过闸账；60min 面闸实投 f_ac2=pass 0.0659／f_volcom=pass 0.0707／f_udrun=reject 0.5350 rc=5 | **整行入卡 1 处**＝A02/12 面 `data_binding.band_caliber_precedent_045`（definition_zh/example_value/downstream_meaning 三面逐字，本班断言全等） | 该结论①"时序差型构造 f_ac2 跨档 corr=−0.0422＝换档即换对象，且 sd 膨胀 13.5 倍（60min 面 0.292006 vs 1min 面 0.021656）把'该档自由度不足'从断言转为读数（4 根 bar 下 m=nb−2=2）"正打本卡唯一候选＝载体正确；结论③"014 在 60min 档构造无源（恒 0 是定义条件无 bar 命中，非读数为零），禁改绑"是 ⑤⑦ 席写法前置 |

4. **⑨成绩官 p09-1015-10 节 §4 [对照] 单＝本班首张配对卡**：对象 `TDM-X-R1-01/comparison/07`（OOS 配面无读数）。成卡 **`TDM-X-R1-01/comparison/07c`**（challenger，champion=07），唯一变量＝随册披露三件的卡面声明（OOS 段样本条数 len(m)／sig 与 tgt 两侧 std()／级别序列在 OOS 段是否整段驻留 0.0），**任何阈值与窗一律零动**。三件在册体例支撑本班不自造形制：①同族 07 面 `exam_scope_note_ruling_jia` 附加规则①原文"凭据须带 not_judged_pillars 列明该跑未判之柱"＝**卡面声明凭据须带何件**的在册先例；②同族 06 卡 `why_new_version_not_edit` 原文"补声明＝口径变更，禁原地改 02，只能另起 06"＝**声明版卡**体例；③号位授权逐字在 07 面括号内"（要拆也是 07c 新版本卡的事，等本版考完确有需要再说）"，而"本版考完"＝其 lineage.score_row=rows[45] 在册、"确有需要"＝⑨席该班实报三因未分账。status 保持 **blocked_on_impl**＝披露腿生产件在 ⑤ 席写域（该席在册单 修⑬ 形一），本班只读实测 HEAD 面无披露键，**不自宣可考**。
5. **⑨成绩官 p09-1015-11 节〔对照〕单＝本班停手**：对象 `TDM-P-P2-04/calibration/07`（＋姊妹 06），其"唯一改动"＝读数只取 `in_sample` 段重算 `ic_mean`/`ic_ir`。本班判**卡面无在册载体、不成卡**：谓词 `in_sample_only|is_only|read_scope|window_slice|disclosure_probe|probe_only` 在全卡池命中 **0 文件**，同尺正对照 `exam_scope_note`=3 文件／`^oos_window_ref:`=**343** 文件（＝上班读数 341＋本班 2 件新卡，加总自证）⇒ 尺未坏、零命中判得住。该"读数切段无卡面机读源"与在册 **OD-15**（⑨席 04 班 [对照] 单的"把 OOS 切成 IS 内同号段／反号段"）同真源，按内收判据"同真源可派生→必并"本班**不新开号**，只作 OD-15 追加面。另 ⑨席该班 修⑭ 请修句末"或显式在卡模板面禁止 panel 卡冻 mono 柱，属 ⑥ 席制卡面"＝**制卡规范变更**（禁一类卡冻一柱）不属本班写域，本班不自立，随本节登记待 ⑩/Owner 路由。
6. **在册未销 [对照] 扩面 rows[8]/[75]/[77]/[79]**（06 班点名、⑨席 09/10/11 三班连续声明"本席不重复派，仍等 ⑥ 席并批"）＝**停手不动**，与上条同一 OD-15 缺源题面，非本班可填的门柱。
7. **⑩线长席派单面**：`dispatch/daily_dispatch.md` 实测 mtime 13:58、`grep -n "^## "` 末节仍＝**第七单**（无第八单可领）；第七单 §6「⑥」行三件已由 09 班三处置完（8 枚自家死信内容级分诊／缺键 2 张／非在册键 2 枚），本班不重烧、不代拆他席袋。
8. **OD-26 追加复测**：`TDM-X-S1-02/comparison/02_dualwindow` 本班实测 HEAD 面 status=examined・`oos_window_ref` 与 `window.oos` 两面 **null**・HEAD 与盘面字节相等（1895B 两面同）⇒ 零可抄源面不变，本班未硬补；该件另被 ⑨席 10 班〔对照〕单用作"卡面未申报窗"的负对照对象（属 ⑦⑧ 跑法面，非制卡面，本班只登记指向）。
9. **OD-30 追加复测（两处读数变化，如实改判留旧案）**：①`TDM-P-P1-03/comparison/03` 本班实测＝HEAD `status: blocked_on_impl`（3415B）／盘面 `preregistered`（4454B）／`git diff --numstat` **+15/−1**（与 09 班读数逐值同）⇒ ⑤席 p05-1015-01 在途面**仍未落地**，本班仍不改该件、不随袋。②同单点名的考工加柱两件 `TDM-P-P2-04/calibration/06`・`/07` **本班复测已迁移**＝两面 HEAD==盘面（3815B／3680B）、status 均 examined、HEAD↔盘面 difflib **plus=0/minus=0** ⇒ 那半腿已由考工席自袋落地；据此 OD-30 出口 (c) 的对象（"盘面对 preregistered 卡新增柱级面"）现已是 HEAD 现值，本班**只登记状态迁移、不判死、不回退**（涉考工写域，且"已落地"不等于"已获裁"）。

### 本班成袋＝5 件（未超队列硬顶 40，一次投出）

2 张新卡（A02/12・X-R1-01/07c）＋本台账＋游标＋`feedback/to_miners.md` 方向单 1 条（同轴滞后阶归口）。

### 呈批与在册追加（正文寄存本台账——04 区呈批真源第十班仍两头不可写：`docs/04_research_records/mining/ledgers/nightmine_20261010/05_owner_decisions.yaml` 盘面 7,062B／`git status`＝**A**（他班 staged・从未落地）／`git show HEAD:` 报 "exists on disk, but not in 'HEAD'"；随袋＝整档快照吸收他班未落地条目＝归属篡改，故仍寄存）**

```yaml
# 本班新立＝0 件；在册追加＝3 面（题面一律不变、旧卷不删、不新开同义号）
- 追加面: OD-15（本班追加，非新号）
  本班复测: 全卡池 552 件里"读数切段/IS-only"类顶层键命中 0 文件（谓词逐字见领用面第 5 条；
    正对照 exam_scope_note=3／^oos_window_ref:=343 同尺同批）；上班读数面 550 件→本班 552 件，
    本班两张新卡均不新增该类键＝缺源结论未因本班产卡而松动。
  新增触发实例: ⑨成绩官 p09-1015-11 班〔对照〕单（对象 P2-04/07＋姊妹 06，唯一改动＝读数只取 in_sample 段）
    ＝同题面第二例，本班按"同真源可派生→必并"并入本单不另立号。
  本班不做的理由: 该单变量落在执行器读数面（写分件从不按 window.in_sample 切片，⑨席 修⑮ 已点名行号），
    卡面既无键可承载、本班又禁自造非在册顶层键（⑩第七单 §3 刚令撤两枚同型自造键，本班 09 班已执行并留证）。
- 追加面: OD-26（本班复测一行）
  本班实测: TDM-X-S1-02/comparison/02_dualwindow＝HEAD 与盘面同字节（1895B）、status=examined、
    oos_window_ref 与 window.oos 两面 null ⇒ 零可抄源面自 09 班至今未变，硬补数仍为 0。
- 追加面: OD-30（本班复测两行，其一改判）
  本班实测①: TDM-P-P1-03/comparison/03 仍 +15/−1（⑤席面未落地）⇒ 本班仍不随袋。
  本班实测②: TDM-P-P2-04/calibration/06・/07 现 HEAD==盘面且 status=examined ⇒ 考工加柱半腿已自袋落地；
    该单三种出口的 (c) 项对象由"盘面在途"变"HEAD 现值"，本班不据落地推定获裁，出口择一仍等 ⑩/Owner。
```

### findings（本批实测，非转述）

1. **同轴滞后阶两卡分属两节点，成因是③席归属声明才开始写**：本班对 46 行逐行正则实测＝001–038 行 definition_zh 内 `TDM归属＝` **零命中**（含 033 lag-1 那行），**039–044 六行**才明写 `TDM 归属＝TDM-E-L9-A02 源线·Tick分笔`（045 非信号行无）。后果＝lag-1 在 `TDM-E-L9-A01/08`（上班按载体落 A01）、lag-2（本卡）按③席明写落 `TDM-E-L9-A02/12`＝一条轴两个节点、两处 confidence 回写。本班处置＝**遵③席在册明写**（不自并、不改他卡、不代③席改判），并落 `feedback/to_miners.md` 方向单一条请 ③/⑩ 认一次归口；该卡面另把事实写进 `gaps_no_source.same_axis_two_nodes_lag1_lag2` 供读卡人自判。
2. **champion 面在本班值守外被他会话重写，本班一律取 HEAD**：`R1-01/comparison/07` 实测 HEAD 16,930 字符／盘面 16,032、行块 difflib **115/253**，而 parsed 顶层面**仅 lineage 一面变**（＝考试写回族）＋文本重排。本班 clone 全部以 `git show HEAD:` 为真源（在册判据只认 HEAD 面），**未取盘面字节做门柱**；该 115/253 面未进本班袋（本班不触该文件）。
3. **本班自犯第一条，当场纠＋留案**：首版建卡器用 `yaml.dump(裸标量).strip()` 取字面值，pyyaml 对裸标量会补 `...` 文档终止符 ⇒ 新卡混入 **4 行终止符**、`safe_load` 直接 ParserError（"expected '<document start>', but found '<block mapping start>'"）。该形态属"响亮的坏"（解析即崩，不会静默放行），修法＝标量一律走"映射切片"取字面＋加终止符负断言；两张卡的逐字断言在修后才跑通。教训：搬运冻结值时，**生成器选型本身是判据面风险**，与手打中文同罪等。
4. **本班自犯第二条，当场纠**：token 实投命令本班首跑带 `| tail -6`，把登记回执截掉只剩指路板 ⇒ "登记成没成"从本班证据面消失。改走权威面复量＝PG `registry_ledger.registry_entry` 反查两条 token 的 `payload->>'created_by'` **逐字＝st-qoder-p06-1015-10**、token 尾 `-20261015`（UTC）；投影册 `capability_canonical_file_registry.yaml` 同批复测对这两路径 **0 命中**＝主区投影滞后在册形态（非未登记），热册本班照旧不随袋、不手改。重申在册铁律：**取证命令禁滤详情**。
5. **本班未跑任何考试、未跑正交闸、未跑 CH 探针**（冻结与运行分离）：039 的过闸读数与册内自查全部逐字承③席在册行并明标"本班未重扫"；040–044 五条 reject/判重复逐字承③席不利侧定案，本班零重算；07c 的三因分账判据逐字承⑨席在册单，本班未自拟阈值。

### 自检两轮（两轮都核对）

- **R1（门柱与冻结值逐字一致＋单变量核对）**：尺＝`.runtime/tmp/p06_1015_10/make_card1.py`・`make_card2.py` 的**建卡即断言**（写盘后同进程内跑，非事后追述）。①A02/12＝门柱 **12 面**逐字对 `git show HEAD:TDM-E-L9-A01__calibration__08_...yaml`（window 全字段含 in_sample/oos/regimes/frozen_note 四子面・pillars_numeric 整块且键集相等・buckets.type+min_obs_per_bucket・discipline・signal_kind・target.primary/secondary・data_binding.target_source・oos_window_ref 与本卡 window.oos 及源卡值三面相等）＋自判 3 项（无 `generated` 键・`buckets.on` 不含数值・status 在枚举内）＋③席 039 行 **5 面** verbatim（definition_zh 同进 hypothesis 与 signal_derivation・example_value・orthogonal_gate_note・sample_window 进 universe_guard）＋045 行 **3 面** verbatim。②07c＝判据 **16 面**双尺（parsed 全等 **且** 源块原文整块为新卡文本子串），hypothesis 母文整段为新卡该面严格前缀；母卡的 node_id/family/schema_version 同值。③**对照卡 diff＝本班 1 对可核对**（champion 07／challenger 07c）：判据面 diff=0，唯一变量＝`exam_scope_note` 的披露声明一面；其余改动全部点名（身份 3 面 card_id/title_zh/version_of、状态 2 面 status/status_reason、溯源 3 面 lineage/prereg_provenance/drafted_*，另母卡审批史 5 键 approval_state/card_face_approved_by/card_face_approved_at/promotion_note/wiring_landed **不复制**并写明理由＝复制即伪称已获统筹签批与已接线，原文仍在 07 卡面故信息零丢）。④**零张裸骨架卡被本班填死**＝骨架 empty 面 186 件本班零写入（R2 状态面反证）。
- **R2（归属·净零·保底·进程外核实）**：①卡池 **550→552**（本班新建 2 件），状态面 blocked_on_impl **45→47**、preregistered 175／examined 73／blocked_on_data 71／empty 186 **四态零变**＝本班未改他班卡面判据一字；②`oos_window_ref` 命中文件数 **341→343**（恰本班 +2，加总自证）；③本班 5 件全部 `lock_files.py acquire-batch --skip-naming-check` 实测 **acquired=5 denied=0**（在册逃生口，理由＝新卡名沿用同族 `TDM-*__<family>__NN_*` 体例供 ⑦⑧⑨ 按 card_id↔文件名与卡内 card_id 消费）；④会话＝`SessionRegistry().register(st-qoder-p06-1015-10, pid=0, held_files=5)` 实测 get_session 转真（返回 SessionInfo 对象，本班首版按 dict 取 `.get` 报 AttributeError⇒属"响亮的坏"非静默），心跳守护 pid=49056；本班值守超 25 分钟续活窗（在册对偶处方）⇒ 入队前同串重注册＋重 claim，结果见收班补记；⑤台账/游标/方向单三件均走 `safe_write_text` CAS＋**纯前缀断言**（删除集=空集，写后进程外读回）；⑥本班实测盘面 ledger 177,148B > HEAD 175,418B＝上班**「终态补录 · 16:48」一节未落地尾块 1,730B**（本班实测 `HEAD 面为盘面严格前缀`=True，且尾块首 120 字逐字读回该节标题），属**同席承接面**（非他班条目），本班袋含"HEAD＋上班尾块＋本班节"，非归属篡改；⑦热册不随袋（投影册／生命周期图／ruling_registry 一字未动）；⑧净零＝零新 gate・零新规则册・零新注册表・零脚本入册（建卡器与核验尺留 `.runtime/tmp/p06_1015_10/`），呈批**新立 0 件**、在册 OD-15/26/30 只追加复测不新开同义号；⑨保底＝**领用面 100% 处置**（③席 7/7＝1 成卡＋5 不立卡＋1 整行入卡；⑨席两单 2/2＝1 成卡＋1 停手并入 OD-15；扩面 4 行停手承 OD-15；骨架 186 停手；⑩第七单无新面；OD-26/30 复测各 1 面），卡面动作 **2 件新卡**（不足 5 张，按"或领用卡 100% 处置完"这一出口达标，如实记不美化）。
- **本班实际耗时**：开班 reaper 首读 16:52:18 → 本段落笔 `date` 实测 **2026-10-15 17:41:34**＝**约 49 分钟**（超 SOP 40 分钟一班节奏；两条增量如实入账＝①python 冷启在 commit_pct 91% 水位下三次过 2 分钟墙、②建卡器两次自犯（`...` 终止符与回执截断）各要重跑与另走权威面）。


## 2026-10-15 18:16 · st-qoder-p06-1015-11 · ⑥制卡席（⑩第八单 §6 本席三件全处置＝自家 9 枚 dead 内容级分诊（44 件次真搁浅=0）＋缺键基线口径改判＝在册"2 张"系点名子集、全池同谓词实测 **21 张**、本班补 **20 张**（逐件 plus=1/minus=0、值取本卡 window.oos 同锚）余 1 张仍挡 ⑤席在途面＋两枚非在册键复测 HEAD=0／零新卡、零翻态、零判据改动／09 班撤键两块证据自 tmp 承接进本台账）

**开班三实测**：①Python 3.12.8（3.12 前置 PATH）。②`python scripts/lock_files.py cleanup` 首跑＝**SALVAGED 两会话遗物**（st-qoder-p02-1015-07・st-qoder-p10-1015-09，各 merge=skipped/stash=0 件/释放 claim=0）；本班 18:13 为取"CLEANED 全量回执"**二次跑**同令＝**CLEANED 126 个死锁**＋SALVAGED 2（p08-1015-05・worker-dbfc55e8-43332），副作用＝自家 claim 被摘（findings 3①）。③`python -m zephyr.trading.process_reaper --status`＝source=live・last_run=2026-10-15 17:48:35・scanned=31・whitelist_hits=19・killed=0・reported=4・ghosts 全 0・commit_pct=89.66・worktree_changes=5609>50・degraded=False。防重入＝游标盘面"本班已收尾"・last_batch=st-qoder-p06-1015-10・last_run 17:41；取号 11＝三址实测（本台账末节 10・`.runtime/tmp/` 末位 p06_1015_10・`.runtime/sessions/` 列至 10）。

**水位如实上报（未据此降工）**：commit 89.66%＋worktree 漂移 5609 与⑩第八单 §1 同形 ⇒ 本班全程串行、零并发子代理、零 CH 探针、零考试、零正交闸；⑩第八单 §0"全线停发新挖矿、各席首件一律＝D-05 自家 dead 分诊"本班照办（产新卡 0 张）。

### 本班领用面（实测，非转述）

1. **③席候选池＝零新批可领（非停手）**：`data/strategy_intake/lane_p0_obi_candidates.csv` DictReader 全读 **46 行**・mtime 16:10・birth_batch＝obi-probe 1／p03-01 7／p03-02 5／p03-03 11／p03-04 9／p03-05 6／p03-06 7 ⇒ **无 p03-07**（p03-06 已被上班 100% 处置）。
2. **`feedback/to_impl.md`＝零新 [对照] 申请**：mtime 16:41（末节＝⑨席 p09-1015-11，其〔对照〕单上班已判"卡面无载体"并入 OD-15）⇒ 本班不重烧。
3. **骨架 empty 面＝不领（第十班复证）**：全池完整 walk **552 件**状态普查＝preregistered 175／empty 186／blocked_on_impl 47／blocked_on_data 71／examined 73（加总 552，五态与上班逐值同＝本班零翻态）；empty 186 全为裸骨架 ⇒ **具名 empty=0**；本班零张裸骨架卡自行填死（⑩第八单 §3 在册链①"无新裸骨架回流"同读）。
4. **⑩第八单 §6「⑥」行三件＝本班全处置**：
   - **首件 自家 9 枚 dead 内容级分诊**：正门 `python scripts/commit_queue.py dead-archive --content-level --days 0 --session <本席 01–09 各 sid>` 实跑＝**被 serializer 租约拒**（原文 `ERROR: serializer 租约存活（pid=53820），拒绝并行维护操作——等排空结束再跑 dead-archive`；processing 现 1 袋＝`st-qoder-x2-1015`）＝09 班"正门被租约拒（pid=23976）"同型**第二证**，本班未加旗绕行、未 `--execute`。改走只读自家尺 `.runtime/tmp/p06_1015_11/d05.py`（袋 blob 字节→git blob sha1 对 HEAD／盘面／对象面三态＋difflib 行级超集判定），**44 件次逐件判＝真搁浅 0**。分族＝①台账中间态 8 枚全 `C_BAG_SUBSET_OF_HEAD`（袋行尽数在 HEAD，HEAD 领先 81–673 行）＝append-only 语义下已被承接；②游标 9 枚 uniq=3＝"最新者胜"原地改写（正对照＝上班 -10-0001 袋 checkpoint `A_LANDED_EXACT`，尺非恒判搁浅）；③02 班 8 枚**裸骨架回填**面 uniq 18–22＝v1.5.1 已废弃形态，承 09 班"不回吃"；④05 班 `A17/02` uniq 26＝本班 09 班按 ⑩ 令**主动撤出**的 `unblocked_20261015` 键（全文已承接进本台账）；⑤07 班 `P2-04/06・/07` uniq 36/28＝考工席后落地覆盖，本班复测两件 `oos_window_ref` 与 `window.oos` 在 HEAD 且等值 ⇒ 07 班补键腿未丢。⇒ 本班**零 requeue、零 mv**（判定腿当日交清，mv 腿受租约挡，等排空）。
   - **次件 缺键基线复量＝口径改判（2 → 21）**：在册"基线 2 张"按**全池同谓词**（`window.oos 有值 且 oos_window_ref 无值`）复量＝**21 张**。两把尺同值互证＝正则尺（`(?m)^oos_window_ref:` 命中 343，与上班在册 343 逐值同）＋YAML parsed 尺（552＝window.oos 无值 188＋有值且 ref 有值 343＋缺键 **21**，互斥分母加总自证，unparsed=0）。**本班补 20 张**，在册依据＝⑧席三道闸第 2 条"执行器只读 oos_window_ref 不读 window.oos，补键=改指向不属改判据，写域在⑥制卡席"（07 班已引并同形执行），值一律取**本卡已冻结 `window.oos` 同一锚**＝零新拍数；形制循同族盘面主流（343 枚里 284 枚为 `oos_window_ref: *id001` 别名）⇒ 有锚 18 枚走别名、无锚 2 枚走等值 flow 字面 `['2026-04-03', '2026-10-12']`。**余 1 张不动**＝`TDM-P-P1-03__comparison__03`（OD-30 对象，实测 head≠disk・`git diff HEAD --numstat` **+15/−1**・盘面 6241B／HEAD 4716B・status 盘 preregistered／head blocked_on_impl ⇒ ⑤席 p05-1015-01 在途面仍未落地，随袋＝归属篡改）。加总自证＝21＝20＋1；补后全池缺键 **21→1**、带 ref 面 **343→363**（恰 +20）、卡池 552 不变。
   - **三件 两枚非在册键归口沿用**：`TDM-E-L9-A17/calibration/02` HEAD 面 `unblocked_20261015`＝**0**（status=preregistered・HEAD==盘面）；`TDM-X-R1-01/comparison/07b` HEAD 面 `examined_face_20261015`＝**0**（status=examined・HEAD==盘面）⇒ 撤键仍归零，未被后班重写。
5. **上班与 09 班袋终态复量**：done 面 `-09-0001`(23)/`-09-0002`(23)/`-09-0004`/`-09-0005`/`-10-0001`(5) 全 done、`-09-0003` 仍 dead；本班对 -0001/-0002 的 **44 张卡面逐件对 HEAD 复量＝44/44 字节全等（漂移 0）**，对 -09-0002 的 23 张补键件 HEAD 面 `^oos_window_ref:` 计数＝**23/23 恰 1** ⇒ ⑩所要"归零"在上班面上成立。
6. **OD-26／OD-30 追加复测（题面不变）**：①`TDM-X-S1-02/comparison/02_dualwindow` HEAD==盘面（2508B）・examined・`window.oos=null`・`oos_window_ref=null`；姊妹 `TDM-X-S1-03/comparison/02_dualwindow` 同形（2475B・preregistered・两面 null）⇒ 零可抄源第三、四班同值，硬补数仍 0。②`P2-04/06・/07` HEAD==盘面（6011B／5566B）・examined・`oos_window_ref == window.oos == ['2024-01-01','2026-09-30']` ⇒ 07 班补键腿在 HEAD 存活（⚠如实标注：无参 `git diff --numstat` 对这两件报 32/36・27/28＝**工作树↔index** 读数（index 系他班旧快照形态，在册已录），`git diff HEAD` 面为零 ⇒ 勿把 index 滞后读成 HEAD 漂移）。

### 本班成袋＝22 件（≤40 硬顶；单一逻辑改动一袋；base 取最新 HEAD；等四态再投下一袋）

20 张补键卡面＋本台账＋游标。零新建文件、零删除、零脚本入册、零热册随袋。

### 呈批与在册追加（正文寄存本台账——04 区呈批真源仍 A 面未入库，第十一班复测口径不变；本班新立 0 件）

```yaml
# 本班新立＝0；在册追加＝2 面；归口呈请＝1 条（随 ⑩ 第八单 §6 本席行，不新开 OD 号）
- 追加面: OD-26（本班复测一行）
  本班实测: S1-02/02 与 S1-03/02 两枚 dualwindow 卡面 window.oos 与 oos_window_ref 皆 null、HEAD==盘面
    ⇒ 零可抄源结论第三、四班同值，本班未编值、未改窗。
- 追加面: OD-30（本班复测两行）
  本班实测①: TDM-P-P1-03/comparison/03 仍 +15/−1（⑤席面未落地）⇒ 本班仍不改该件、仍不随袋；
    该件＝本班全池缺键复量后唯一残余 1 张。
  本班实测②: P2-04/06・/07 补键腿在 HEAD 存活（ref==window.oos 逐值等），与 10 班"考工半腿已自袋落地"同读。
- 归口呈请（口径面，非新判据）: 在册"缺键基线 2 张"是按**点名件**计数、非按**全池谓词**计数。
  本班按全池同谓词实测＝21 张（＝20 可补＋1 挡道）。后果＝每班复量"2"都会归零，而池面始终留有执行器
  读不到 OOS 窗的卡。请 ⑩ 把该基线改为全池谓词口径（尺与谓词本班留 `.runtime/tmp/p06_1015_11/scan_oos.py`
  ・`verify1.py`，正文可原样复跑）；旧读数"2"不删（更正另起、留旧案卷）。本席不自改他席在册读数。
```

### 撤键两块承接（09 班在册称"唯一存面＝`.runtime/tmp/p06_1015_09/*.txt`"，属临时区有 TTL；本班逐字搬入本台账）

```yaml
# 承接一：TDM-E-L9-A17/calibration/02 原顶层键 unblocked_20261015（本班复量 26 行／2794B／sha256 前缀 1a66c15cba19）
unblocked_20261015:
  by: st-qoder-p06-1015-05
  at: '2026-10-15'
  trigger: ②数据建设席 st-qoder-p02-1015-01 建设单 B-3（c3_fundamental.research_report.rating_change 派生回填）
    登记于 docs/_working/automation_campaign/feedback/unblocked.md 10-15 07:07 节；该节明言"卡状态改判不归本席（⑥制卡/⑨成绩官面）"
  unlock_conditions_in_card_verbatim: 『解锁条件：research_report_collector 补 rating_change 解析（或从 pdf_forecast_extracted
    192365 行反推评级迁移），且回填后 rating_change 非空率 >=60%、看空类样本 >=300 条；齐备后把 status 改回 preregistered 重冻开考』
  own_measurement_not_secondhand:
    command: python -c "import sys; sys.path.insert(0,'scripts/backtest'); from fexam.ch_data import ch_query_df;
      print(ch_query_df(\"SELECT rating_change,count() FROM c3_fundamental.research_report FINAL GROUP BY rating_change
      ORDER BY 2 DESC LIMIT 8\").values)"（本卡 data_window_evidence 自带命令的 FINAL 形）
    rating_change_dist: 维持 92173 / 上调 19735 / 下调 19522 / 空串 13052 / 首次 2458（与②席在册四态读数逐值同）
    nonempty_rate: count=146940 countIf(rating_change!='')=133888 => 91.12% >= 60% 门槛 通过
    bearish_face: 下调 19522 条（全史）；publish_date>='2022-01-01' 仍 11324 条 => 看空类 >=300 门槛 通过
    inside_frozen_windows: IS 2019-01-04..2023-12-31 内 下调 9816 事件/1766 符号/1335 发布日，上调 10218/1919/1398；
      OOS 2024-01-01..2025-09-09 内 下调 4753/1441，上调 4559/1391 => buckets.min_obs_per_bucket=60 与七门槛⑥（事件>=30）
      在两窗两组皆超线（本班实测，非②席转述）
    publish_date_range: 2017-01-02..2026-09-30
  freshness_gap_does_not_move_pillars: ②席 10-15 08:15 节在册提示"研报明细增量腿自 2026-10-01 起 0 行入库…A17 事件窗建议截到
    publish_date<=2026-09-30"——本卡窗（IS 2019-01-04..2023-12-31／OOS 2024-01-01..2025-09-09）末端 2025-09-09 早于该缺口起点
    2026-10-01 ⇒ 建议对本卡为空操作，窗与柱一字未动
  untouched_frozen_faces: window／buckets／pillars／pillars_numeric／target／oos_window_ref／discipline／signal_kind 八面零改动；
    上方 blocked_on_data 时代的 data_window_evidence 与 readiness 原文保留作旧案卷（更正另起留旧案卷纪律），其"rating_change
    100% 空"谓词已被本班实测推翻
  residual_scope_note: 母卡 blocked 证据第 3 条"表内无目标价列"未随本次回补改变（A17 决策问题的"目标价变化"半问仍无字段），
    本卡只答"评级调整"半问（target.note 在册原文），故不阻本卡开考；目标价面另属①②席供数与节点级 GAP 挂起
```

```yaml
# 承接二：TDM-X-R1-01/comparison/07b 原顶层键 examined_face_20261015（本班复量 15 行／1581B／sha256 前缀 874d58d62481）
examined_face_20261015:
  by: st-qoder-p06-1015-08
  at: '2026-10-15'
  trigger: ⑩线长席第六单处置单 D-01（dispatch/daily_dispatch.md 2026-10-15 第六单 §3）令"⑥ 席当班把两卡翻至在册终态
    或挂禁考标记"；同 node 姊妹件 07 三面实测（HEAD/index/磁盘）已 examined＝零动作，本件是 D-01 的剩余面
  own_measurement_not_secondhand:
    score_book_face: docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml 磁盘面 sha256 前缀 4f986ec7143a690f
      ／116029B／rows=84（册 mtime 09:38:34；本班 date 实测 10:2x，非转述）
    rows_for_this_card: rows[68,69,70,71] 四行 card_id 全=TDM-X-R1-01/comparison/07b_熔断五级梯度减仓对照_复位阶梯锚定版・verdict 全=fail
    iter_budget_face: 4 行 > SOP §4 同 holdout ≤3 轮上限 ⇒ 超限后的"换 fresh holdout or 封存"沿用⑩席在册呈批第 4 项属 Owner，本席不代裁
  why_flip_is_not_a_judgment_change: status 是生命周期字段、非判据；该件实已被考 4 次而卡面仍 preregistered，
    按 HEAD/index 消费卡状态的排考面会继续把它当未考候选＝D-01 原句"队列与卡面都不挡第 5 轮考"
  untouched_frozen_faces: window／buckets／pillars／pillars_numeric／target／oos_window_ref／discipline／signal_kind／
    arm_definition／executor 十面零改动；lineage.run_id 与 lineage.score_row 维持 null——本卡四跑四条读数而单一 run_id
    无在册真源可择，择一属⑤写分工具腿（在册修①）与⑨成绩官面，本席不代拍
```

### findings（本批实测，非转述）

1. **"归零"在两处含义不同，成因是谓词不是数据**：在册写法"缺键基线 2 张待下一班复量归零"，照字面复量那 2 张＝OD-26 的 `X-S1-03/02`（无源）＋OD-30 的 `P1-03/03`（挡道），两张确实"归零或不动"；同一谓词铺到全池＝21 张。⇒ 本班按全池口径补 20 并把口径问题作归口呈请（见上节），旧读数不删。
2. **补键不等于翻态，本班用状态面反证**：五态 175/186/47/71/73 与上班逐值同，带 ref 面 +20 而 preregistered 面零增 ⇒ 20 张补完仍 blocked（补的是"将来能考"的指向，不是开考资格）。另本班把 09 班两块撤键证据全文从 tmp 搬进台账＝09 班那句"唯一存面"当时成立、现不成立（tmp 有 TTL），承接后存面＝本台账＋tmp 两处（本班复量两枚 tmp 件行数与字节与 09 班在册逐值同：26/2821・15/1597）。
3. **本班自犯三条，当场纠＋留案**：①**班中二次跑 `lock_files.py cleanup` 把自家 22 枚 claim 与心跳守护一并摘掉**（首跑只 SALVAGED 2；为取"CLEANED 全量回执"再跑，126 枚死锁被清），随后 `list --session` 读回"CLEAN — 持有者无任何文件锁"、心跳末行同批变 `status:"exited" reason:"session not in registry"`。教训＝**清道夫只在开班跑一次**，要回执用 `list`；在册"入队前重注册＋重 claim"由"超 25 分钟"扩为"任何一次自家清道之后"。修法实测＝同串重注册（pid=0）＋`acquire-batch <sid> --files-from` 重 claim（acquired=22 denied=0）＋重起守护（pid=61168）。②心跳首 spawn 连撞两形：传 str 触发在册已知 `TypeError: unsupported operand type(s) for /`；改 Path 后又因 `python <脚本>` 时 `sys.path[0]`＝脚本目录（非仓根）报 `No module named 'scripts.ops_guard'`，守护返回 None 并提示"session will expire in 90s"。正解＝仓根＋src 双入 sys.path、register 在先 spawn 在后（同进程）。③尺两处自犯：存在性尺首版把袋 `blob_ref` 当仓根相对路径（实为队列根相对）⇒ `FileNotFoundError`（响亮的坏）；`safe_write_text` 回执本班首版探 `.ok` 得 None＝**尺探不存在的字段**（真字段实测＝`path/written/before_sha256/after_sha256`），写面真伪改由 `git diff HEAD --numstat` 独立证实 ⇒ 报"某操作成功"前先看返回体真字段，勿凭命名猜。
4. **本班未跑任何考试／正交闸／CH 探针**（冻结与运行分离）：他席过闸与自查读数一律转抄在册原文并标"本班未重扫"；补键值零自拟（全部取本卡 `window.oos` 同锚）。

### 自检两轮（两轮都核对）

- **R1（门柱与冻结值逐字一致＋单变量核对）**：尺＝`.runtime/tmp/p06_1015_11/fill.py`（写即断言）＋`verify1.py`（进程外读回），两轮同判据。①逐件行级＝**plus=1・minus=0・唯一变行以 `oos_window_ref:` 起首**＝写内 20/20，`git diff HEAD --numstat` 面复量 20/20，异常件 0；②**冻结面零动**＝对 HEAD 逐件比 `pillars_numeric/pillars/window/status/card_id/buckets/target/discipline` 八面 parsed 全等＋键集差恰 `oos_window_ref` 一枚＋`oos_window_ref == window.oos`＋末三行无 `...` 文档终止符（承 10 班自犯条）＝不匹配 0；③**值来源零自拟**＝18 枚走本卡 `*id001` 别名、2 枚走等值 flow 字面；④**对照卡 diff＝本班 N/A（如实记不记绿）**＝领用面零 [对照] 申请（to_impl mtime 未动、⑨席新单未点名⑥），无 champion/challenger 可 diff；⑤**零张裸骨架卡被本班填死**＝本班 20 件 `skeleton=False` 逐件实测（谓词 `^TDM-.*__(calibration|comparison|shadow|ablation|robustness)\.yaml$`）＋empty 面 186 件本班零写入。
- **R2（归属·净零·保底·进程外核实）**：①卡池 552→**552**（零新建零删除）；带 ref 面 **343→363**（恰本班 +20）；全池缺键 **21→1**（残余＝P1-03/03 挡道件，非本班可动）；②五态 preregistered 175／empty 186／blocked_on_impl 47／blocked_on_data 71／examined 73 **零变**＝本班未翻他班一字；③claim＝`acquire-batch st-qoder-p06-1015-11 --files-from .runtime/tmp/p06_1015_11/files.txt --session <sid>` 实测 **acquired=22 denied=0**，持有者字段读回＝本席 sid（在册陷阱"参数序假成功"专门读回）；班中 claim 被自家 cleanup 摘除后已重注册＋重 claim；会话注册 `register(pid=0)` 实测 get_session 转真・held=22、心跳守护 pid=61168；④台账/游标均 `safe_write_text` CAS＋**纯前缀断言**（删除集=空集，写后进程外读回）；游标只改 `cursor`/`last_run`/`last_batch` 三行，frontmatter 与 `notes` 行零动（"最新者胜"＝上班游标正文按体例被取代，非本班删除）；⑤热册不随袋（投影册／生命周期图／ruling_registry 一字未动）；⑥净零＝零新 gate・零新规则册・零新注册表・零脚本入册（分诊尺与补键器留 `.runtime/tmp/p06_1015_11/`）、呈批**新立 0 件**、OD-26/OD-30 只追加复测；⑦归属＝袋只含本席写域 22 件，`P1-03/03`（⑤席在途）与 `P2-04/06・/07`（考工写域，且已落地）**不入袋**；⑧保底＝**卡面动作 20 件 ≥5**，领用面 100% 处置（③席 0＝无新批实测／[对照] 0＝实测／骨架 186 停手复证／⑩三件三处置／OD-26・OD-30 复测各成行）。
- **本班实际耗时**：开班 `date` 实测 17:48:28 → 本段落笔 **2026-10-15 18:16:02**＝约 **27 分钟**（超 SOP 40 分班期；两条增量如实入账＝①自家 cleanup 二次跑引发重注册/重 claim/重起守护的返工轮，②队列正门 `dead-archive` 受 serializer 租约拒（pid=53820）改走只读自家尺）。

## 10-15 19:30 · st-qoder-p06-1015-12 · ⑥制卡席（③席 20261015-p03-07 批 7 行 100% 处置＝新卡 1 张（L9-A02/13 跨日分钟路径形延续，blocked_on_impl）＋不立卡裁定 5 条＋方言画像行整行入卡 1 处／⑧考工B 点名⑥三件全处置＝并名件新立呈批 OD-31・三处臂参数件停手・implementation_gap 陈旧自述判"不原地改"／⑨席 13 班 P-9 选项 B 待裁登记＋10 班 [对照] 已成卡 07c 复测承接／全池新量＝13 张 preregistered 具名卡缺 data_binding（在册分类器 13/13 拒因 no_data_binding_section）按 P-5 未裁停手／骨架 empty 186 第十二班复证／上班 22 件袋落地复量 363/363 零漂移＝本班首件交清）

**开班三实测**：①防重入＝游标 last_batch=1015-11 且首句"本班已收尾"⇒ 前任已停手，本班取号 12；②reaper `--status` 实测 source=live・last_run=18:21:38・scanned=32・killed=0；③Python 3.12.8。**水位如实上报**：开班 reaper 读数 `commit_pct=85.73`・`ram_used_pct=72.5`・`cpu_pct=85.6`・`degraded=False`・`breached=['ALERT-SYS-001']`・`worktree_changes=5840>50` ⇒ 本班全程串行、零并发子代理、零 CH 探针、零长跑批；只读快查在前，重活一律带 timeout 外壳（但**未给提交套限时壳**，在册自犯形态）。

### 一、领用面与实测分母（写卡前本进程逐件 yaml.safe_load）

exam_cards **552 文件 552 解析零坏件**；状态面 empty 186／preregistered 175／examined 73／blocked_on_data 71／blocked_on_impl 47（加总 552，五态与 11 班逐值同＝本班开班面零变）。

1. **上班（11 班）交下的首件＝落地复量，本班实测达标**：11 班游标原文『本班不自宣落地，落地判据＝下班用 `git show HEAD:<件>` 复量』。本班实测其袋 `q-20261015-st-qoder-p06-1015-11-0001` 现＝**done**（pending/processing/dead 三面各 0），并对 HEAD 与盘面同谓词复量＝`^oos_window_ref:` **HEAD 363 文件／363 次・盘面 363 文件**（三面逐值同，与 11 班自报 343→363 的 +20 加总自证咬合）⇒ 20 张补键腿已在 HEAD 存活、零漂移。
2. **D-05 自家 dead 复证＝零新增**：`dead/` 面含 p06 件计数＝**9**（qids 与 11 班所量同一批，mtime 全落 13:22–13:27，本班值守内无新死袋）；11 班的 44 件次内容级分诊结论（真搁浅 0）在册未变，本班不重烧判定腿。
   **mv 腿＝正门第三证同型被挡**：`python scripts/commit_queue.py dead-archive --content-level --days 0 --session st-qoder-p06-1015-01 --session st-qoder-p06-1015-02` 实跑 **rc=1**，原文 `ERROR: serializer 租约存活（pid=46440），拒绝并行维护操作——等排空结束再跑 dead-archive`（09 班 pid=23976／11 班 pid=53820 ⇒ **第三证**）。本班未加旗绕行、未 `--execute`、零 requeue、零 mv。队列现值＝pending 10／processing 1／done 802／**dead 317**（⑩第八单记 305→本班实测 309→317＝雪崩仍在续扩，转 ⑩）。
3. **骨架 empty 面＝不领（第十二班复证）**：完整 walk 552 件按谓词 `^TDM-.*__(calibration|comparison|shadow|ablation|robustness)\.yaml$` 二分×状态普查＝**empty∩骨架 186・empty∩具名 0・非empty∩骨架 0・非empty∩具名 366**，四格加总＝552（互斥分母自证）。本班零张裸骨架卡自行填死。
4. **`feedback/to_impl.md`＝零新 [对照] 申请**：mtime 18:22（⑤席 06 班刚追加§3），本班逐节读＝⑤席该节三条（设计稿／工具健康度／信箱自态）**均不点名⑥席**；⑨席 14 班节零方向单／零缺数单／零对照单（其正文自述）⇒ 本班 [对照] 领用面＝0 张新单。⚠**本班不随袋该件**：⑤席 06 班在册读数＝该件盘面==HEAD 而 **index 比 HEAD 少 292 行**（他班旧快照形态），随袋＝吸收他人未落地删除面。

### 二、③席 20261015-p03-07 批 7 行＝100% 处置（本班为首个领到的⑥班）

真源 `data/strategy_intake/lane_p0_obi_candidates.csv` 本班 DictReader 全读＝**53 行**・mtime 18:20・birth_batch＝obi-probe 1／p03-01 7／p03-02 5／p03-03 11／p03-04 9／p03-05 6／p03-06 7（上班已处置）／**p03-07 7**（行 46–52）。

| 候选 | ③席在册闸读数（逐字取 orthogonal_gate_note，本班未重跑闸） | 本班处置 | 判据 |
|---|---|---|---|
| CAND-P0-MIDAYSHAPE-046 跨日分钟路径形延续（相邻两日十六档向量同位相关） | 池面过闸 verdict=**pass** max\|corr\|=0.1215 most_similar=lu_ratio_z20 rc=0；册内自查 vs 040 f_flip=0.2137／vs 041 f_irrev=0.1844／vs 043 f_dwellent=0.1479（其余 9 腿更低）⇒ max=0.2137≤0.3＝**池面与册内两面孔同判未撞**；尺双对照＝池成员自投 reject 1.0000 rc=5（尺能红）＋随机高斯 ctrl pass 0.1043 rc=0（尺非恒拦）；③席原文『本班唯一轴净增』 | **成卡 `TDM-E-L9-A02/calibration/13_crossday_minutepath_shape_corr`**（blocked_on_impl，10,297B） | 本班自家尺内建断言 31 项全过（尺 `.runtime/tmp/st-qoder-p06-1015-12/make_card13.py`）：冻结面逐字对 `git show HEAD:A02/12`・③席 046 行五面 verbatim・③席 052 行五面 verbatim・`oos_window_ref==本卡 window.oos==源卡值`・五键并与 A01/08・A02/10・A02/11 三面 parsed 逐值同值・`buckets.on` 不含数值・无 `generated` 键・card_id↔文件名互推成立・目标件此前不存在（不覆盖他件） |
| CAND-P0-MIAC2STAB-047 二阶路径记忆五日滚动稳定维 | 池面 pass 0.1863，**册内自查 vs 039 f_ac2=0.4168>0.3＝判重复**（③席自记"池外盲区第 6 例"） | **不立卡** | ③席在册不利侧定案，本席不翻、不重算 |
| CAND-P0-MIFOURIER1-048 日内方差谱一次谐波模 | 池面 pass 0.1468，册内 vs 024=0.8030／vs 044=0.7052／vs 014=0.6509 **判重复**（盲区第 7 例） | **不立卡** | 同上；③席结论"谐波改写不脱离时段方差族"优先 |
| CAND-P0-MIFOURIER2-049 二次谐波模 | 池面 pass 0.2836（贴线 0.0164），册内 vs 024=0.7784／vs 026=0.7094／vs 036=0.6962 **判重复**（盲区第 8 例）；048↔049 互共线=0.514 | **不立卡** | 同上；『换阶仍同族』是③席在册结论，本班不产同族第二卡 |
| CAND-P0-MIOPENTVD-050 开盘/尾盘成交强度形状距离 | 池面 pass 0.2932（**贴线距 0.0068，③席按保守口径不判过**），册内 vs 040=0.4489／vs 036=0.4202／vs 026=0.4014 **判重复**（盲区第 9 例）；与 046 互共线仅 0.045 | **不立卡** | ③席原文"两窗形状对比与跨日形状延续确是两个对象，但前者日频主成分被切换频率族吃掉"＝其不利侧自判，本班只转抄；046/050 共线 0.045 已写进本卡 `gaps_no_source.non_duplication_note_047_051` 供 ⑨ 席对拍 |
| CAND-P0-MIHURST-051 分钟收益多标度块和标度指数 | 池面 **reject** 0.3196 most_similar=avg_abs_ret_z20 rc=5（同批唯一池也拦的一条），册内 vs 040=0.6575／vs 039=0.5670／vs 033=0.5577 ⇒ **两面皆撞＝判重复** | **不立卡** | 池拦即定案（承 10 班 042 行同形口径）；尺能红由 ③席同批自投对照在册 |
| CAND-P0-MIPORTRAIT3-052 楼1 分钟腿方言与内存口径画像行（非信号） | 非信号行自身不入过闸账（该行原文『闸读数不适用』） | **整行入卡 1 处**＝A02/13 面 `data_binding.dialect_caliber_precedent_052`（definition_zh/data_source_table/sample_window/example_value/gate_note 五面逐字，本班断言全等） | 该行原文自述用途＝『对 ⑤⑥⑦ 席的用途＝data_binding 与查询写法门柱前置，尤其 (d) 条＝若制卡/考试器沿用 arraySplit 分档，会得到"看起来跑通、读数恒等"的假面』——正打本卡构造（046 定义里档界＝`intDiv(k·nb,16)`，而 (a)(b)(c)(d)(f)(g)(h) 七条都是本卡物化腿的写法前置） |

**成卡凭据（本班只读实测，面=`git show HEAD:scripts/backtest/fexam/card_binding.py`，HEAD 面 118,781B）**：负谓词 `middayshape|path_shape|shape_corr|跨日`＝0・`intDiv`＝0・`arraySplit`＝0・`autocorr`＝0；有效正对照 `kline`＝22・`corr`＝1・`limit_up_count`＝2（⇒尺有判别力，零命中判得住）；在册物化通道＝`card_binding.py:78 SERIES_DIR`＋`:195 _CSV_HINTS`＋`:202 load_named_series`，该目录 `ls` 实测 **35 枚 csv** 而 `shape|corr|day|ac` 类 **0 命中**（正对照 `avg_abs_ret.csv` 在册命中）；lag-1／lag-2 同缝未补 ⇒ 本卡按 SOP ⑤出口停手不自宣可考。

### 三、⑧考工B 点名⑥的三件＝全处置

1. **「词面分裂并名归⑥」＝本班不并名，新立呈批 OD-31**（三证齐，见§四）。
2. **「X-R1-01/ablation/03 缺⑥冻三处臂参数」＝停手**（在册尺面两证：①该卡面 `signal_derivation` 原文自陈『仓位带与预算面属 C1 流（**跨流禁代裁**）』，而本班全池检索 trend_down 绑数值 11 处命中**全部落在 F-C1/C2/C3 族的 `frozen_note` 散文面**（如『六段预算带数值真源=TDM-F-C1 节点注释』），把 C 流数值搬进 X 流卡面＝代裁；②在册尺 `arm_protocol_binding.py:631 _MAGNITUDE_HINTS` 是对**整张卡 JSON 文本**找关键词再判"相邻有无数值"，本班实测该卡面 5 处"预算"里 4 处是散文引用（C1 流预算面／same_family_precedent 引文），故"三处臂参数"含**尺把散文当参数**的假阳性面）。⇒ 本班既无在册可抄数，也不自造数；尺的假阳性另落本台账请 ⑤/⑩ 判（非本班写域）。
3. **「三张卡 implementation_gap 陈旧自述，呈⑥判是否补正卡面」＝本班判：不原地改、不自造新版**：本班实测 ⑧ 所引适配器凭据**在 HEAD 面即成立**（`git show HEAD:card_binding.py` 内 `DrawdownStateMachine`=5・`ResetConfirmation`=2・`RefuseResetError`=2・`DrawdownStateMachineConfig`=2，且 HEAD==盘面）⇒ ⑧ 的"卡面 10-10 冻结的陈旧自述没跟上"定性属实；但改它＝改卡面陈述，按在册体例（同族 06 卡 `why_new_version_not_edit` 原文『补声明＝口径变更，禁原地改 02，只能另起 06』）须**另起版本卡**，而另起需号位授权——本班逐字检查三张卡面未见"可拆新版"授权括号（07 面那句授权只覆盖 07c 一形）⇒ 本班不自造号位，登记待 ⑩/Owner 路由。

### 四、⑨席两单面

- **13 班 P-9 选项 B（"由 ⑥ 席 prereg 更长 OOS 窗或更密事件定义"）＝待裁不动作**：该选项的两个动作（改 OOS 窗长／改事件定义）都落在**判据面**，非本班写域；本班未动事件族 23 行任一窗与任一定义。P-9 选项 A/B/C 择一属 Owner＋⑩，本班只登记指向（若裁 B，本班按"抄在册冻结值"执行、不自拟窗）。
- **10 班 [对照] 单（X-R1-01/07 披露探针）＝已由 10 班成卡 07c 承接，本班复测**：`TDM-X-R1-01__comparison__07c_...yaml` **HEAD 与盘面同字节 18,007**，且本班按该单三件谓词逐件在 HEAD 面复量＝`len(m)`／样本条数 命中 **True**・`std()` 命中 **True**・"驻留" 命中 **True** ⇒ 披露声明三面已在 HEAD 卡体，**本班零重复制卡**。
- **11 班〔对照〕单（P2-04/07＋姊妹 06 的 IS-only 读数切段）＝承 10 班在册停手**（同题面已并入 OD-15，本班不新开号、不重烧）。

### 五、本班全池新量＝13 张 preregistered 具名卡缺 `data_binding`（在册分类器 13/13 实证），按 P-5 未裁停手

尺＝`.runtime/tmp/st-qoder-p06-1015-12/dbinding_gap.py`・`gap13_detail.py`（只读，零写）。谓词＝`status==preregistered 且 data_binding 为空`，全池 552 件命中 **13** 件，逐件调在册 `card_binding.classify_card`＝**13/13 回 `{"cls":"U","reason":"no_data_binding_section"}`**（＝可考性正堵在此面，非本班臆断）。分布＝E-L1-S0 4 张（货币／流动性／海外／政策事件卡）・E-L1-S1 1 张（黄白线交叉，同 node_id 有绑定面的先例数＝**0**）・E-L1-S2 1 张（连板家数分布）・E-L1-S3 3 张（昨日涨停溢价／晋级率／情绪先锋四态）・E-L1-S4 2 张（期权IV主路径／合成VIX后备）・E-L1-S5 1 张・另 1 张。

**本班为何不填（两证）**：①族内先例的绑定面**不是同一口径**——以 L1-S3 为例，具名先例是 `05_limit_up_premium_derived`・`06_promotion_rate_derived`（status=examined，卡内 title 自标『**日线导生截面均值口径**·结果面校准平行卡』），把导生口径抄回原卡＝在卡面上把"原始口径 vs 导生口径"择一，而该择一正是 ⑨席 **P-5 在册待裁**对象（原文：平行卡与母卡 `metrics`＋`fails`＋`verdict` 逐字节全等 6 对 12 行，"算不算两次独立考试"选项 A 合并记账／选项 B 先由 ⑤ 物化真导生序列再各排一次考）＝本班若填，等于在 P-5 裁定前**再造 13 对同读数卡**；②S0 族四张（LPR/MLF・DR007/逆回购・隔夜美股美债・政策事件清单）在本卡 node_id 族内**无可抄先例**（同节点有绑定的先例仅 m1m2 剪刀差与两融流量，属另两枚信号），而按工序3 指路的源线谱 `docs/04_research_records/data/chain_piling_campaign/02_source_line_registry.md` 实测是**链路册（U1–U6）不是表名字典**，全册对 LPR/MLF/DR007/期权/美债 四组关键词命中＝**0**（命中面只有第 72、139 行的散文提及）⇒ 语义与表源双缺，按"禁编一个数"停手。**归口呈请（随台账寄存）**：这 13 张＝"卡面无绑定⇒执行器 structurally 不可考"的存量面，请 ⑩ 与 P-5 一并判（先裁口径归属，再令 ⑥ 抄值）。

### 六、OD-26／OD-30 追加复测（题面不变）

- **OD-26**：两张 dualwindow 卡（`TDM-X-S1-02/comparison/02_dualwindow` examined・`/X-S1-03/...` preregistered）本班实测 `arms`=null・`window.oos`=null・`oos_window_ref`=null 三面同形；**本班新量一处结构**：其窗面并非真空，而是写成 `window.stress`＋`window.recent_oos` **两枚散文窗**（S1-03 卡面逐字：stress=2020-02-01..2020-03-31／recent_oos=2025-10-09..2026-09-30），且卡内 `pillars_dualwindow_frozen` 另有 5 键（crisis_maxdd_improve_pp_min 等）；母卡 `X-S1-03/comparison/02` 的 `window.oos`==['2025-10-09','2026-09-30'] 与其中一枚等值。⇒ 若把母卡 oos 抄成 `oos_window_ref`，执行器只会读**近样年单窗**，而该卡判据要"双窗同过方为真增益"（卡面 hypothesis 原文）＝**造出"单窗读数冒充双窗结论"的假可考**。本班因此仍不补、不改窗，把该结构写进本台账（第五班同值面已从"零可抄源"改判为"有散文双窗但不可单键指认"，更正另起、旧卷不删）。
- **OD-30**：`TDM-P-P1-03/comparison/03` 本班实测＝盘面 `preregistered` 4,454B／HEAD `3,415B`／`oos_window_ref`=null 而 `window.oos`=['2025-10-09','2026-09-30'] ⇒ ⑤席面仍未落地，本班仍不改该件、仍不随袋；该件＝全池缺键复量后**唯一残余 1 张**（本班按 11 班全池谓词复量＝缺键 1、带 ref 363，与 11 班收班值逐值同）。

### 七、本班成袋＝3 件（≤40 硬顶；单一逻辑改动一袋；base 取最新 HEAD；等四态再投下袋）

1 张新卡面（A02/13，未跟踪转跟踪）＋本台账＋游标。零新脚本入册（建卡器与全部尺留 `.runtime/tmp/st-qoder-p06-1015-12/`）、零删除、零热册随袋（令牌投影册 `capability_canonical_file_registry.yaml` 只登记不随袋，在册口径）、`feedback/to_impl.md` 不随袋（他班 index 少 292 行面，§一.4）。

### 八、呈批与在册追加（正文寄存本台账——04 区呈批真源仍 A 面未入库，第十二班复测口径不变）

```yaml
# 本班新立＝1 件（OD-31）；在册追加＝2 面（OD-26/OD-30 各 1 行）；归口呈请＝1 条（13 张缺绑定）
- 新立: OD-31「门柱词面 turnover_cost_gate vs turnover_or_cost_gate 并名」
  触发: ⑧考工B p08-1015-06 班 §④『词面分裂 turnover_cost_gate(11 卡) vs turnover_or_cost_gate(10 卡) 并名归⑥』
  本班实测（全池 552 件，谓词＝整卡 JSON 子串；尺 .runtime/tmp/st-qoder-p06-1015-12/pillar_name_split.py）:
    卡面命中＝turnover_cost_gate 33 张 / turnover_or_cost_gate 29 张 / 同卡兼有两面 0 张（互斥）
    落 pillars_numeric（机判键面）＝11 张 / 19 张
    状态构成＝前者 {preregistered 29, blocked_on_impl 2, examined 2}；后者 {preregistered 15, blocked_on_impl 13, blocked_on_data 1}
    ⑧席 11/10 面＝其本族 occurrence 计数（承 ⑦A/⑧首班在册"本族 60 个非在册键含 turnover_cost_gate 11 次"同读）；
      本班按"卡"与"全池"两谓词各量一遍，不复现 10，差异属计数单位与面不同——本班不改他席在册读数，只另起一行留证
  不利侧三证（为何本班不自助并名）:
    证1（机判后果为零且 fail-closed）＝直接 import 在册现值：`_CALIBRATION_JUDGED_KEYS ∪ _UNION_PILLAR_KEYS ∪ _EVENT_KNOWN_KEYS`
        对两枚词面命中 **0**（实测回值 True＝两者都不在词表）⇒ 两枚都是越表柱，judge() 对越表键 fail-closed 返"未支持判据键（机判面待扩）"，
        并名不改变任何一根柱的机判结果；⑧席自家在册口径亦记"词表须按路由取"（series/dual_arm 两值，无 calibration）
    证2（执行核明写禁改）＝`scripts/backtest/fexam/calibration_exam.py` `_unjudged_pillars` docstring 原文：
        『prose↔numeric 的对应关系无在册真源，本件不代拍（该映射是"门柱词表立法"工单的对象，**禁改键值**）』
        ＝权威名真源不存在于卡面侧，且改名被该件点名划给另一工单
    证3（事后改冻结面风险）＝两枚词面所涉卡含 examined 面（前者 2 张／后者 1 张为 examined 形态），
        ⑨席在册判卷轮一＝"回卡体门柱未走样"，改名会破分数行↔卡面对拍（分数行 pillars_prose_keys 原样存文字面）
  请裁（Owner／⑩线长，二选一即可，本席不自拍）:
    (a) 授权 ⑤ 在词表立法工单内先定权威名（改代码词表＝执行核写域），落地后本班按该名逐张搬运、并给 examined 卡另起披露行；
    (b) 判"并名属披露面统一、不属判据"⇒ 本班可对 **preregistered 且词面在 pillars 文字面（非 pillars_numeric）** 的子集先行统一，
        但须 ⑩ 书面认一次"文字柱改名＝非口径变更"，否则违在册体例（同族 06 卡"补声明＝口径变更禁原地改"）。
  不点的后果: 两枚词面继续并存，⑥/⑧/⑨ 每班各按自己谓词量一遍（本班已实测出 33/29 与 11/19 两组不同面），
    并名工单永远停在"归⑥"而本班永远停手；对机判零影响，但对人读与跨席对账持续耗轮。
- 追加面: OD-26（本班复测一行＋结构改判）
  本班实测: 两张 dualwindow 件 arms/window.oos/oos_window_ref 三面仍 null（与 09/10/11 班逐值同），
    但本班新量＝其窗面写成 window.stress＋window.recent_oos 两枚散文窗且卡另有 pillars_dualwindow_frozen 5 键；
    母卡 X-S1-03/02 的 window.oos 与其中 recent_oos 等值 ⇒ 旧结论由"零可抄源"改判为"有双窗散文但不可单键指认"，
    硬抄任一枚＝造单窗冒充双窗的假可考，本班仍未补、未改窗。
- 追加面: OD-30（本班复测一行）
  本班实测: TDM-P-P1-03/comparison/03 仍 盘面 4454B／HEAD 3415B／ref=null 而 window.oos 有值 ⇒ ⑤席面未落地，
    本班仍不随袋；该件＝全池缺键复量后唯一残余 1 张（缺键 1／带 ref 363，与 11 班收班值逐值同）。
- 归口呈请（口径面，非新判据）: 全池 preregistered 具名卡缺 data_binding＝13 张，
  在册分类器逐件实证 cls=U・reason=no_data_binding_section（13/13）。本班未填的两证见本台账§五。
  请 ⑩ 与 ⑨席 P-5 并判：先裁"原始口径 vs 日线导生口径"归属，再令 ⑥ 按裁定搬运在册值。
```

### findings（本批实测，非转述）

1. **③席 p03-07 批把 10 班的归口单答上了，但答案落在 ⑩ 的门**：046–051 六行 definition_zh 一律改记双标注『载体 kline_1min→TDM-E-L9-A01／信息本体＝日内路径形→TDM-E-L9-A02』并原文声明『归口待 ⑩ 认一次后由 ⑥ 席搬键，本席不改卡不自裁』。⇒ 本班遵**信息本体**落 A02（本卡 confidence_writeback 同节点），零搬键、零改 A01/08 与 A02/12 他卡；一轴两节点问题只剩 ⑩ 的一次确认，本班把它写进本卡 `gaps_no_source.attribution_dual_pending`。
2. **同批 7 行里 5 行被 ③席 自家册内自查判重复**，且 ③席 给出"池外盲区第 6/7/8/9 例"的连续编号＝正交闸的池面看不见册内已入库轴。本班据此把 046 的成卡判据写成"两面孔同判未撞"（池面 max=0.1215、册内 max=0.2137，两者都 ≤0.3），并把 047–051 的册内值整块转抄进本卡 `gaps_no_source.non_duplication_note_047_051` 供 ⑨ 席对拍——**本席零重算**。
3. **自犯第一条，当场纠＋留案**：本班首把"在册序列目录是否存在"的尺用 `os.path.isdir()` 量，回 **MISSING**；同一目录随后用 `ls` 实测**存在且 35 枚 csv**。⇒ 同谓词两把尺读数相反，本班一律以 `ls` 面入卷（正对照 `avg_abs_ret.csv` 在册命中），并把该分歧如实登记：在 python 侧判目录存在性不可单独作证据（本机会话内未定位到机制，禁据此断"目录不可读"）。
4. **自犯第二条，当场纠**：本班第一版正对照选了 `kline_1min` 整串，在 `card_binding.py` 的 HEAD 与盘面两面皆 **0 命中**＝该对照无法证明尺未坏（在册铁律：零命中须正对照，且对照须在同一被测面上有命中）。换 `kline`(22)／`corr`(1)／`limit_up_count`(2) 后判得住。旧句留案不改写。
5. **工具面新缺陷（转 ⑩/维护班，本班未动他人件）**：`session_worktree._spawn_heartbeat_daemon` 实跑报 `heartbeat daemon spawn failed (session will expire in 90s): No module named 'scripts.ops_guard'`＝spawn 子进程 sys.path 缺仓根。本班绕行＝从仓根直接起 `heartbeat_daemon.run_daemon(sid, root, interval=25)` 独立进程，实测 `heartbeat.jsonl` 连续 `status:"alive"`（pid=43508 与 54428 两行；本班另见 ⑤席 06 班在册"自续心跳 7 分救不了 ghost_session 袋"同族面）。
6. **值守内面值被上游推进（本班据 12 班在册处方＝两时点＋点名改动者）**：本班抄源件 `A02/12` 本身就在 19:00:53 那波 92 件批量触及里，**本班建卡一律取 `git show HEAD:<件>` 字节**（在册判据只认 HEAD 面）⇒ 该波对本卡零影响；本班未读盘面字节做门柱，也未随 28 件在途卡面入袋。后果面＝本班台账若沿用开班面会写出"其余四态零变"的假陈述，故 R2① 把两时点实测面并排列出并点名归属（承 ⑩ 第八单"派单计数须两时点"与在册"面值在你脚下变"形态）。
7. **本班未跑任何考试、未跑正交闸、未跑 CH 探针**（冻结与运行分离）：046 的过闸读数与册内自查逐字承③席在册行并明标"本班未重扫"；047–051 五条判重复/池拦逐字承③席不利侧定案；13 张缺绑定只出普查与拒因，未替任何一张拍口径。

### 自检两轮（两轮都核对）

- **R1（门柱与冻结值逐字一致＋单变量核对）**：尺＝`.runtime/tmp/st-qoder-p06-1015-12/make_card13.py` 的**建卡即断言**（写盘前同进程跑，非事后追述），**31 项全 CLEAN**：①对 `git show HEAD:A02/12` 逐面 parsed 全等＝window 整块（含 in_sample/oos/regimes/frozen_note 四子面与 `&id001` 锚）・pillars_numeric 整块＋键集相等・buckets.type 与 min_obs_per_bucket・discipline・signal_kind・target.primary/secondary・data_binding.target_source；②三面锚等＝`oos_window_ref == 本卡 window.oos == 源卡值`；③③席 046 行五面 verbatim（definition_zh 同进 hypothesis 严格后缀与 signal_derivation 整值・example_value・orthogonal_gate_note・sample_window 进 universe_guard・data_source_table 进 signal_table，且 signal_table 与源卡值**逐字同值**＝本班实测断言）；④③席 052 行五面 verbatim 整行入卡；⑤五键跨面同值＝并与 A01/08・A02/10・A02/11 三面 parsed 全等（消"多口径择一"）；⑥自判＝无 `generated` 键・`buckets.on` 不含 ASCII 数字（写"十六档"中文数词，承 10 班在册坑）・status 在五态枚举内・card_id↔文件名互推成立・**目标件写前不存在**（不覆盖他件）・全文无 `...` 文档终止符行。⑦**对照卡 diff＝本班 N/A（如实记不记绿）**：本班领用面零新 [对照] 申请（§一.4），无 champion/challenger 可 diff；新卡系新造具名子题卡，与各自抄源卡的差异面＝信号对象本身，已在 `prereg_provenance.single_variable_note` 声明。⑧**零张裸骨架卡被本席自行填死**＝本班写入面只 1 件新卡（骨架谓词 `skeleton=False`）＋骨架 empty 面 186 件本班零写入（R2 状态面反证）。
- **R2（归属·净零·保底·进程外核实）**：①卡池 **552→553**（本班新建 1 件）。**开班实测面**＝empty 186／preregistered 175／examined 73／blocked_on_data 71／blocked_on_impl 47（加总 552）；**收班实测面**＝empty 186／preregistered **167**／examined **81**／blocked_on_data 71／blocked_on_impl **48**（加总 553）。本班净贡献只有 **blocked_on_impl +1**（本班新建那张）；**其余 −8/+8 发生在本班值守内、由上游推进**＝`exam_cards` 全池按 mtime>18:21:19 谓词实测 **92 件在同一秒 19:00:53 被批量触及**（尺 `.runtime/tmp/st-qoder-p06-1015-12/bulkface.py`），其中 **28 件 HEAD≠盘面＝在途面**（本班一律不随袋）、`pillars_numeric` 被洗掉 **0 件**（10 班在册"骨架重渲染洗键"缺陷本波未触发，实测为证）。8 张 preregistered→examined 属考工席跑批，与在册"判官跑完重写卡面本身"同型⇒**本班零翻态**（反证＝本班 claim 面只 3 件＝新卡＋台账＋游标，且 28 件在途卡面本班逐件未写）。②`oos_window_ref` 命中文件数 **363→364**＝恰本班新建 1 件带该键（本班实测两时点读数，加总自证）。③本班 3 件全部 `lock_files.py acquire-batch --skip-naming-check` 实测 **acquired=3 denied=0**（在册逃生口，理由＝新卡名沿用同族 `TDM-*__<family>__NN_*` 体例供 ⑦⑧⑨ 按 card_id↔文件名与卡内 card_id 消费）；④会话＝`SessionRegistry().register(st-qoder-p06-1015-12, pid=0, held_files=3)` 实测 `get_session` 转真（返回 SessionInfo），官方守护 spawn 面缺陷见 findings 第 5 条，改由本班直起 `run_daemon(interval=25)` 心跳存活；**claim TTL=30 分 < 本班实际耗时**（承 ⑨席 14 班在册条）⇒ 本班入队前同串重 claim＋重注册（结果见收班补记）；⑤令牌＝`batch_creation_tokens.py --capability exam-card --created-by st-qoder-p06-1015-12` 逐件前缀登记，实跑回 **`OK: 已登记 1 条（意图 API 三步 register→publish→render）`**・`publish_snapshot v868 (noop=False)`，token 串＝`exam-card-tdm-e-l9-a02--calibration--13-crossday-minutepath-shape-corr-20261015`（尾日期取 UTC＝20261015，与本班 `date` 本地 19:2x 同日，在册口径）；投影册同件反查在册后**照在册不随袋**（该热册含他班在途条目，且本次 render 顺带补了 5 条"PG 有行而盘上无"的滞后行，样本含他席 p07c 两件＝本班不为其入袋）；⑥台账走 `safe_write_text` CAS＋**纯前缀断言**（删除集=空集，写后进程外读回）；⑦净零＝零新 gate・零新规则册・零新注册表・零脚本入册・零新卡除 1 张承接件；呈批**新立 1 件（OD-31）**，OD-26/OD-30 只追加复测不新开同义号，13 张缺绑定走"归口呈请"而非新号（同真源可派生→必并）；⑧保底＝**领用面 100% 处置**（③席 7/7＝1 成卡＋5 不立卡＋1 整行入卡；⑧点名 3/3＝并名呈批＋臂参数停手＋gap 判不改；⑨席 2/2＝P-9 待裁登记＋07c 复测已承接；[对照] 新单 0；骨架 186 按在册停手；13 张缺绑定停手＋归口；D-05 复证零新增＋mv 腿第三证），卡面动作 **1 件新卡**（不足 5 张，按"或领用卡 100% 处置完"这一出口达标，如实记不美化）。
- **本班实际耗时**：开班 `date` 实测 18:21:19（reaper 首读 18:21:53）→ 本段落笔 `date` 实测 **2026-10-15 19:30:23**＝**约 69 分钟**（超 SOP 40 分钟一班节奏；三条增量如实入账＝①在册臂三态机读器全池实跑一轮＋在册分类器逐件调用属重活，在 commit_pct 85% 水位下各占用数分钟；②心跳守护 spawn 缺陷逼出绕行取证；③建卡器两处自犯（正对照选错、目录存在性尺）各要重跑）。

## 2026-10-16 21:3x ｜ st-qoder-p06-1016-01（⑥制卡席·1016 首班）

### 一、冷启动与防重入
- 环境：`python --version`=3.12.8；`lock_files.py cleanup`＝CLEANED 3 枚死锁（known_data_gaps.yaml／p01 ledger／p01 checkpoint）＋SALVAGED st-diskp0-20261015（merge=skipped）；reaper `--status`＝source=live・last_run=21:30:20・scanned=16・killed=0⇒写操作前提成立。
- 防重入：游标行＝"本班已收尾（1015-11）"，台账末节＝1015-12 且含"本班实际耗时"收口行⇒11/12 两班皆终态，本班可开工。⚠新游标＝游标停 11 班而台账有 12 班＝12 班未推游标行（在册"游标由本岗每批推进"腿漏一棒），本班按台账实况接续，班号取 1016-01。
- 会话与心跳：`SessionRegistry().register(sid, pid=0, held_files=2, logical=True)`＝注册转真（get_session 返回 SessionInfo・held_files 两面），logical 被 chief-form 校验降级为 False（工具自陈 fail-open，非事故）；官方 spawn 面缺陷沿 1015-12 班在册，本班直起 `run_daemon(sid, root, interval=25)`＝heartbeat.jsonl 实测末行 `{"ts":"2026-10-16T13:36:55+00:00","pid":27260,"status":"alive"}`（UTC＝本地 21:36:55，三点对齐）。
- claim（工具缺陷已自犯一次并纠正）：`acquire-batch` 的位置参数形态会把**第一个文件当会话名**吞掉（本机实测 `acquire-batch <ledger> <checkpoint> --session X` 得 acquired=1 且"持有者: <ledger>"，checkpoint 被 ledger 名义锁定）；正解＝`acquire-batch <sid> --files-from <清单>`（--help 原文即此形）。本班按正解重跑＝**acquired=2 denied=0**（错锁经 RECLAIMED 过期回收，零外来 claim 受损）。
- 零 worktree：本班未调用任何工棚/工作树入口（TRAE-079 Phase 2）；在途发现的历史遗留面见 [BLOCKER] 流程问题行。

### 二、领用面 100% 处置（本班零张可领卡）
1. 领卡面（工序 1）＝**0 张**：全池完整 walk＝553 件（is_file 谓词，非 rglob('*') 计数），状态分账＝preregistered 163／empty 186／blocked_on_data 71／blocked_on_impl 48／examined 83／examining 2（加总 553 自洽）。**empty∩具名＝0**、empty∩骨架＝186（谓词＝`card_id` 末段=="01" 或 `title_zh` 含"骨架"之并集，逐件 yaml.safe_load 判定，两格互斥加总=553）。卡池 552→553＝上班 1 张新卡入池。⇒本班无可领具名卡，非本班怠工。
2. 骨架退回单＝沿在册停手口径不重开（186 件本班零写入，本班卡面动作面见§三～§五，全为只读量测）。
3. [对照] 申请面＝**0 张新单**：to_impl.md mtime 实测 2026-10-16 10:10:12，逐节 grep `⑥|制卡` 在 10-16 各节（⑩05/08/09/11/12 班）**零命中**；在册未销三条沿旧判不重烧＝X-R1-01/07 披露探针（10 班已成卡 07c）／扩面 rows[8]/[75]/[77]/[79]（承 OD-15 停手）／P2-04・/07 IS-only（已并 OD-15）。
4. 本席台账「接单」段＝`grep -n 接单` **零命中**⇒该段在本台账不存在（指令卡措辞与册面不符，登记以免下一班再找）。本班以 to_impl 逐节点名尺替代。
5. ⑨席点名⑥席两单＝修㉑（复核义务→§三）、修⑱（断链面积→§四），两单本班皆处置。
6. 保底判定＝本班卡面动作＝**0 件改写**（零冻结、零新卡、零补键），领用面 100% 处置达标＝①具名 empty 0（实测）②骨架 186 停手（实测）③[对照] 0（实测）④修㉑ 复核定性成文⑤修⑱ 面积复量成文⑥形状新法可机判性成文。如实记不美化。

### 三、修㉑ 复核定性＝**卡面零串位（单变量纪律成立），真病灶＝对照族 2×2 塌格**
尺＝六卡逐字段 `yaml.safe_load` 差集＋五字段绑定元组（signal_table/signal_column/signal_derivation/target_source/universe_rule）。母↔腿差集（逐卡实测，剔除身份/溯源键 card_id・title_zh・arm_protocol・control_provenance・lineage・preregistered_at/by）＝
- L3母→L3-target腿（rows[96]）＝仅 `target`＋`data_binding.target_source`；
- L3母→L3-universe腿（rows[98]）＝仅 `data_binding.universe_rule`＋`exclusions`；
- L9母→L9-universe腿（rows[97]）＝仅 `universe_rule`；
- L9母→L9-target腿（rows[99]）＝仅 `target`＋`target_source`。
⇒ 四张腿卡各只换声明的那一轴，**制卡侧不存在"母卡血统被复制错"形态**＝⑨席请本席判的"是否为绑定侧串位"＝**否**。
结构解释＝两枚母卡本身在 **(target 口径 × 宇宙过滤)** 两轴上**同时**不同（L3母＝t1o_to_t2c×有过滤；L9母＝close_to_close×无过滤），故四张单变量腿卡只落进 2×2 的两个格、每格被两卡重复度量：格(close_to_close×有过滤)＝rows[96]∪rows[97]；格(t1o_to_t2c×无过滤)＝rows[98]∪rows[99]；另两格＝两枚母卡自身（rows[73]、rows[95]）。⇒ ⑨席两观（"四卡塌成 2 面"＋"target 腿读到对侧量级"）皆由该格点重复派生，**无需引入串位假设**。
残留未解（本席不代裁机制）＝同为格内重复，rows[96]==rows[97] 逐位全等而 rows[98]/[99] 差 8.5e−5；两对的卡面差集形态相同（皆只差 signal_derivation/signal_column 散文，元组级零等值对＝本班实测 EQUAL 集为空），故"同格⇒同读数"不足以解释该不对称⇒请⑤席按序列解析口径判（`截面分位/Top-N 降序` 与 `rank_pct 归一` 两套窗下是否解析为同一对象）。
本席侧修法候选（不改任何冻结卡、不动判据）＝对照出卡前置加**格点查重**：新腿卡与在册同族卡按 (target_source, universe_rule) 二元组对表，落同格即判重复、禁冻结；两轴皆不同的母卡禁互为对照基线（须先拆单轴基线）。属本席工序纪律候选，非新 gate／非新注册表（全资产净零）。

### 四、修⑱ 复量＝面积世代漂移（在册 84→现测 33），差因已坐实非尺差
- 本班尺（谓词逐字）＝正则 `docs/_working/[^\s'"`，。；;）)、|]+`，取 `#` 前段、剥尾标点，`Path.exists()` 相对主区根判存，面＝553 件全文含注释行。尺自纠一次留痕＝首版误写 `docs/` 后再要 `/_working/`（多一个斜杠）⇒恒 0 命中，被"在册 84"与本机 grep 94 件当场证伪后修正；正对照＝`docs/_working/automation_campaign/p06_prereg/ledger.md` exists=True；负对照面＝同尺下现存无 False 样本（本班如实记：此面不构成"谓词恒真"证明，仅说明死面稀少）。
- 现测＝含 `docs/_working/` 引用卡 94 件；死引用 **33 件／36 次**；活引用 134 次。按字段分面＝死址落**机器字段**（lineage/data_binding/pillars*/window/oos_window_ref/target/*_spec）者 **5 件**，仅散文/证据字段 28 件。五件机器字段死址＝`TDM-E-L1-S2/calibration/16`（nightmine_campaign/series/max_streak_height.csv 全角括号截断处）、`TDM-P-P1-05/shadow/05`（matrix_campaign/90_execution_log.md）、`TDM-P-P2-01/comparison/02`（t0_matrix/six_phase_history_v1.csv）、`TDM-P-P2-04/ablation/04` 与 `TDM-P-P3-01/comparison/02`（皆 `docs/_working/2026-09-04-trading-decision-map-discussion.md`）。
- 与在册 84 件之差**归因**＝`docs/_working/fexam/`、`nightmine_campaign/series/`、`matrix_campaign/`、`t0_matrix/` 等于 **10-15 19:00 整批复现并入库**（mtime 齐 19:00・`git ls-files` 有面・`git cat-file -e HEAD:docs/_working/fexam/00_exam_campaign_summary_v1.md` 通过）⇒⑨席 18:1x 读数不假、本班读数亦不假，两数分属两个盘面世代。**跨班引用"84 件"这个数须带世代标签**（下班勿按 84 复烧）。
- 处置＝本席**不改写任何已冻结卡体的证据路径**（卡体＝冻结面，事后改指属挪门柱族）；五件清单随本节入册，归口请⑩定（属判卷可复验性腿，与修⑰ 写侧路径缺陷同族）。

### 五、形状匹配新法（SOP v1.6.2 工序 4／[⑥-新]）在卡面的可机判性＝当前无载体
- 卡面实测＝`target` 顶键全池仅 `note,primary,secondary`（291）／`primary,secondary`（43）／`primary`（26）／`note,primary`（5）／无 target（188），**带形状机读键（shape|form|granularity）的卡＝0/553**；`signal_kind` 面完整＝series 184／panel 183／None 186，且 None 集合与 empty 骨架集合**完全重合**（非empty∩缺 signal_kind＝0 件）＝缺键是骨架而非漏写，正/负对照自证。
- 执行器侧本班复量＝`git show HEAD:scripts/backtest/fexam/calibration_exam.py | grep -c _shape_preflight`＝**3**（函数 `:913`、调用 `:999`）⇒比在册 ⑩1016-12 班催办读数（HEAD=0）前进一格，该催办已可收口；而该函数**签名吃 card 却不读 card**，只按装载后的 pandas 对象形状判⇒制卡席在冻结前无法用同尺预检。
- 散文筛（**筛查非判定**）＝谓词 `signal_kind==panel 且 target.primary 含 next_day_index_return|CSI300|指数|市场级|全市场|基准指数`＝命中 **19 件**＝preregistered 14／blocked_on_data 4／examined 1。已证 1 件假阳＝`TDM-E-L9-A03/calibration/02_880板块相对强弱持续性`（target=880 板块指数次日收益，板块指数为多列面板，panel↔panel 合法）⇒其余 **18 件**（14 prereg＋4 blocked）为"panel 信号配市场级单序列"同号形态候选。
- 与在册"B 族 14 卡 ill-formed"关系＝**未对表**（B 族逐卡点名清单在③席面，本班未取到）⇒勿把两个"14"当同一物，本班只报现测。
- 处置＝18 件本班**一律不翻态、不撤卡、不自行填死**（撤卡与重出题不在本席写域；本班亦未跑装载腿＝那等价半次考试，本席恒定禁跑）。请③席按 TDM 节点重出或声明聚合路径；请⑤席若把形状申报落进卡面机读键，本席下班即可在冻结前用同尺预检。

### 六、[BLOCKER] 登记（§8-A-2，七字段）
[BLOCKER] 2026-10-16|⑥席1016-01|判据缺失|形状匹配新法在卡面无机读载体（target 零形状键 0/553），制卡席冻结前只能散文筛，且筛出 18 张 panel×市场级单序列同号形态卡仍在冻结面（14 张 preregistered）|docs/03_modules/_domain_backtest/exam_cards（谓词见§五）＋scripts/backtest/fexam/calibration_exam.py:913|请③席重出 18 张或声明聚合路径；请⑤席给 target 侧形状申报机读键|高
[BLOCKER] 2026-10-16|⑥席1016-01|判据缺失|修㉑ 对照族 2×2 塌格：两枚母卡在 target 与 universe 两轴同时不同，四张单变量腿卡只产 2 个面；格内重复一对逐位全等、另一对差 8.5e-5，卡面无法解释该不对称|exam_cards/entry_flow/L3/TDM-E-L3-07-3__calibration__03_target_close_to_close_control.yaml＋entry_flow/L9/TDM-E-L9-A01__calibration__04_universe_st_and_age_control.yaml|请⑤席按序列解析口径判不对称成因；本席"格点查重"工序纪律候选请⑩定是否入 SOP|中
[BLOCKER] 2026-10-16|⑥席1016-01|数据问题|修⑱ 面积世代漂移：在册 84 件→本班现测 33 件（死引用 36 次／机器字段 5 件），差因＝docs/_working/fexam 等于 10-15 19:00 整批复现并入库（跨班引用该数不带世代即造二次矛盾）|docs/_working/fexam/ mtime 19:00・git cat-file -e HEAD:docs/_working/fexam/00_exam_campaign_summary_v1.md 通过|请⑨席下班按世代重报修⑱ 分母；请⑩定五件机器字段死址归口（本席禁改冻结卡体）|中
[BLOCKER] 2026-10-16|⑥席1016-01|流程问题|指令卡措辞与册面不符两处＝①本席台账无「接单」段（grep 零命中）②游标停 1015-11 而台账已有 1015-12 收口行（游标推进腿漏一棒）|docs/_working/automation_campaign/p06_prereg/ledger.md（grep -n 接单 空）＋checkpoint.md cursor 行|请⑩线长定：接单面是否改指 to_impl 逐节点名尺；下班起游标是否由本班格式补正|低
[BLOCKER] 2026-10-16|⑥席1016-01|工具缺陷|lock_files.py acquire-batch 位置参数形态把第一个文件当会话名吞掉且仍报 ACQUIRED（实测 acquired=1・持有者=<另一个待锁文件>），无入参校验提示|scripts/lock_files.py（--help 正解＝acquire-batch <conv> --files-from <list>）|请⑤/工具班给"位置参数非会话名即报错"输入校验；本席已改 --files-from 正解并重锁 acquired=2|低
[BLOCKER] 2026-10-16|⑥席1016-01|需Owner|本班呈批零新立（OD 号止于 OD-31）；形状新法无载体属"判据缺失"而非新裁面，本席不据§五的 18 张候选请 Owner 撤卡或改判据|本节＋§五（在册停手口径：撤卡不在本席写域）|无（本班无呈批件待 Owner 点头；若 Owner 要一次性处置 18 张候选，请经⑩开单号）|低

### 七、本班未做与理由（防下班重烧）
- 零冻结、零新卡、零补键：领用面实测具名 empty=0、[对照] 新单 0；形状候选 18 张不在本席撤卡写域。
- 未跑考试／正交闸／CH 探针／装载腿（本席恒定与§五边界）。
- 未动判据门柱、未动任何卡体、未碰 `scripts/backtest/fexam/**`（⑤席写域）、未随袋 to_impl.md（⑩单写面）。
- 未清理他席在途面与历史遗留 worktree（TRAE-079 Phase 2 令只报不清）。

### 八、本班实际耗时
开班 date 实测 **21:30:12**（reaper 首读 21:30:25）→ 本段落笔 date 实测 **21:43:04**＝约 **12 分钟**（40 分班限内）。本班为只读量测班＝零卡面写动作（领用面实测无具名可领卡），耗时短属实情非美化。

### 九、收班补记（本班末段实测，追加不覆写§八）
- §八落笔＝21:43:04（写台账那一刻），**本班真收班＝21:58:24＝约 28 分钟**（超出 40 分班限，超支三处如实入账＝①正门 `git_commit.py` 前台跑满 2 分钟被工具转后台（袋 21:5x 入 done/、落地面 `f149929a90` 实测在册）；②本班自犯一次尺假零（`docs/` 后多要一斜杠⇒修⑱ 面积首版恒 0）与一次 `acquire-batch` 位置参数误用，两处各要重跑与取证；③他席在途面使 `grep -rl .runtime/commit_queue/` 全池扫描走满超时，已按 PID 精确终止自家 grep 进程，未伤任何他席进程）。
- 首袋落地三面自证（只认 git log＋blob，口径＝LF 归一文本 sha256）＝`git log -- ledger.md` 首条＝**f149929a90**；袋内件集＝`git show --name-only` 恰 2 件（ledger＋checkpoint，零他人件、零归属篡改）；`git show f149929a90:<件>` 与盘面对拍＝ledger 45839e39e882==45839e39e882・checkpoint 3ac6cd217ebd==3ac6cd217ebd（两值同时等于 safe_write_text 自报 after_sha＝写器/库面/盘面三面同源）。
- 工具缺陷追加一行留痕（不新开号）＝经 `timeout 900 python scripts/git_commit.py ...` 前台调用被 CLI 工具转后台后，正门 stdout 报告**整段丢失**（输出文件实测 0 字节而落地已证），故本席收工判据不能含"读到 CLI 回执"这一条；请⑤/工具班评估 gateway 报告是否改落 `.runtime/` 侧审计件而非仅 stdout。
- 收班八件终态＝①claim：本班两面（ledger／checkpoint）按 `release-batch --files-from` 正解释放（结果见下条下班复量面）；②心跳：守护 pid=**27260** 按 PID 精确终止（禁 /IM 全杀，在册教训），注销后核 heartbeat.jsonl 末行；③耗时＝本条实测 28 分；④[BLOCKER]＝本班 6 行七字段（本席在册历史 0 行⇒⑩强制收班提醒的两班连续零行已终结）；⑤自清＝`.runtime/tmp/st-qoder-p06-1016-01/` 本班临时件（claim_files.txt／ledger_block.md／commit_msg.txt 已由正门自删／heartbeat.out）当场删除，项目根零临时件；⑥GPU＝本班未 acquire 看门人牌，无牌可还（N/A 非漏做）；⑦后台子任务＝本班零子代理，两个后台 Bash 任务皆终态（一已完成、一由本席按 PID 终止）；⑧零 worktree＝本班未创建任何工作树，历史遗留 `.worktrees/st-mtrain-1016` 只报不清（已入 [BLOCKER] 流程问题行）。

### 十、收班补记二（更正§九第⑧条措辞，另起一节留旧案）＋正门自建车道新案
- ⚠**更正**＝§九⑧"本班未创建任何工作树"的措辞不完整，真相如下（本班首判只查"自己有没有调工棚入口"，漏查"落地链路会不会替我建"）：`.aidrafts/st-qoder-p06-1016-01` 确在位，且 `git worktree list` 有该行（HEAD 随落地推进）。
- 归属实测（三证，非推测）＝①目录 mtime＝21:45＝本班首袋 `git_commit.py` 起批时刻（本席该时刻无任何其它动作）；②分支 reflog 两跳＝`session/st-qoder-p06-1016-01@{1}: branch: Created from 788ab1add2`（①席 21:42 commit）→ `@{0}: reset: moving to a3c0370d3e`（⑤席 21:55 commit）＝**跟随 dev 移动的序列化车道**，不是人手工开的工作树；③`.aidrafts` 的写入方在 `scripts/commit_queue.py` 等落地链件内（`grep -rln aidrafts scripts src` 命中含 commit_queue.py）。⇒ 定性＝**创建者＝正门/队列落地链，不是本席**；本席依 TRAE-079 Phase 2 零调用工棚入口这一条仍成立，但"零 worktree 确认"这一检查项在现有实现下**不可能靠本席自律达成**。
- 危害面（本席只报不判）＝指令面与实现面冲突：TRAE-079 Phase 2 令各席"禁建 worktree、直改主区"，而落地链每袋替会话建一个 `.aidrafts/<sid>`；若下一班按 §八"发现历史遗留 .worktrees/st-*→禁自行清理、报⑩"的字面谓词去扫（只扫 `.worktrees/`），则 `.aidrafts/` 侧的在途车道**结构性漏扫**（实测 `.worktrees/` 面只有 `st-mtrain-1016` 一枚，而 `.aidrafts/` 面有全部会话车道）。
- 处置＝本席**不删**（删他人/他人链路创建的树属破坏性动作，在册禁）；请⑩线长向清理专班定性"落地链自建车道是否属 TRAE-079 令的豁免面"，并请⑤席给该车道一个会话结束后的自清钩子（或把它显式声明为豁免并从"零 worktree 确认"判据里剔除）。
- [BLOCKER] 追加一行（本节配套，七字段同规）＝见下一行。
[BLOCKER] 2026-10-16|⑥席1016-01|工具缺陷|正门落地链每袋替会话自建 .aidrafts/<sid> 序列化车道，与 TRAE-079 Phase 2"禁建 worktree"令面冲突且不在本席可控面（本席"零 worktree 确认"该检查项在现实现下无法自律达成；在册扫描谓词只写 .worktrees/ ⇒ .aidrafts/ 侧在途车道结构性漏扫）|.aidrafts/st-qoder-p06-1016-01・reflog "branch: Created from 788ab1add2"→"reset: moving to a3c0370d3e"・git worktree list 该行・grep -rln aidrafts scripts src 命中 scripts/commit_queue.py|请⑩向清理专班定豁免口径；请⑤给车道收尾自清钩子或把它从判据剔除；本席不删他链创建的树|中

- 本班终值（与§九同尺，覆盖其瞬时数）＝首班开班 date 实测 21:30:12 → 末袋起批此刻 date 实测 **22:03:02**＝本班总耗时约 **32 分钟**；三袋制＝袋1（正文§一～§八，21:45 起批／21:47 落地 f149929a90）＋袋2（§九收班补记，22:02 落地 d72e51936c）＋袋3（§十更正＋本行）；超 40 分班限的真因＝队列序列化每班各占 6～8 分且本班末段追加了一次自我更正轮，非量测怠工。

- **终值补记（本班末次网关袋；覆盖§九「28 分」与§十「32 分」两枚落笔瞬时数，两处旧案逐字不删）**＝开班 date 实测 21:30:12 → 末袋**落地面 git 提交时刻**实测 **2026-10-16 22:27:28**（尺＝`git log -1 --format=%ad 18c53be249`）＝**本班在飞总时长 57 分 16 秒**。分账（例行 vs 返工 vs 等待）＝①例行腿（冷启动三步＋全池 553 件普查＋修㉑／修⑱／形状新法三件量测＋§一～§八正文落袋）＝21:30→21:44＝约 14 分；②返工腿＝预检拦一袋（消息引代码路径撞 MESSAGE-CLAIMS-CODE-BAG-EMPTY，按门给的出口加 [docs-only] 重投＝**本席自犯，非门误杀**）＋尺自犯一次（`docs/` 后多要一斜杠致断链面积假零）＋`acquire-batch` 位置参数误用一次＋§九⑧ 措辞被自家复核推翻另起§十；③等待腿＝队列序列化（他席头袋 waiting 781 秒而 `commit_queue.py status` 报 daemon.online=false＝在册发车引擎停摆案复证），末袋 22:04 入池→22:27 落地＝23 分。补记落笔 date 实测 2026-10-17 05:31:58（距末袋落地 6 小时余，其间会话空闲、零在途写面）。
