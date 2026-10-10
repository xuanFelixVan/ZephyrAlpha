---
ttl: task_bound
title: L11 复挖车道台账——TDM-E-L2-01 / TDM-E-L2-04（前役 L1 自报封矿复验）
created: "2026-10-10"
sid: st-mineloop-20261010
family_id: MENELOOP-CAMPAIGN
lane: L11-remine-entry_flow-L2-01-and-L2-04
---

# L11 复挖台账（2 节点，任务=推翻前役封矿）

工作根（工棚）=`D:/ZephyrAlpha/.aidrafts/st-mineloop-20261010`。
共用任务书=`.runtime/tmp/st-mineloop-20261010/MINING_BRIEF_R1.md`（唯一作业口径真源，已完整读取）。
前役凭据=`D:/ZephyrAlpha/docs/_working/nightmine_campaign/L1_ledger.md`（sid=st-nightmine-20261010，lane=L1-entry_flow-L2-sector）。
方法论=`mining_sop v1.8.0` §2/§3 六向 + 复挖硬门（自报封矿不自证成立）。

## 0. 复挖判定口径（本车道立法）

- 前役 §7 把 TDM-E-L2-01 与 TDM-E-L2-04 双双列入 mined_out 名单（22 个），各带"另挂 blocked"尾注。
- 本车道逐向重查，每向给**证据行**（文件:行或命令原文）；凡前役写"受阻/blocked"的向＝突破口，
  须验证 blocked 是否真的无路可走（在产件实际喂的是什么口径）。
- 判据面一经写死不回改（G4-5）；未达标/查无/受阻如实记录才算交付；禁为凑数摊薄。
- 禁一切 git 命令；21:00–22:30 禁 CH 重查询 ⇒ 取数证据全部引用任务书 §3 在册事实或前役 §3 P1–P18 实测（带条目号）；
  需新证据者写 `data_window_evidence: 待总包 22:30 后实测` 并置 `status: blocked_on_data`。
- 只新建文件：未触碰任何骨架件（`generated: true`）与前役卡件；未写注册表/分数册/creation_tokens。

## 1. 台账总表（逐节点一行，机读优先）

| node_id | ①上游 | ②下游 | ③算法 | ④后端 | ⑤呈现 | ⑥数据 | 新卡数 | 族分布 | mined_out? | blocked 原因 |
|---|---|---|---|---|---|---|---|---|---|---|
| TDM-E-L2-01 | 地图 algo_note 四条判据陈述：四路 0-100 等权 0.25 合成 / +市场调节 ±10 后 clamp [0,100] / 总分前 15% 进池 / UP-4 六指数分布叠加通道（trading_decision_map.yaml:754-759）；**另有一条 `fallback:` 字段（同文件 772 行）前役未成题** | 实读接线件 MOD-SIG-144 `[CONSUMERS] TDM-E-L2-01（板块强度综合生产接线）`（sector_strength_wiring.py:5，[MATURITY]=production）；其余消费方=scripts/backtest/sector_surface.py、scripts/backtest/generate_backtest_backlog.py、config/trading_day_cycle_map.yaml（Grep 反查，见 §3-Q2） | 前役 §1 本行自述"族 S1+S3 等权→IC 加权改权须先出分"——**"须先出分"本身即未挖长尾的自白**：等权 vs IC 加权的双臂对照卡不存在（已实读 ablation/02 臂集与 target.note 确认） | MOD-SIG-142 在岗：DEFAULT_WEIGHTS 第 39 行、weights 形参 92 行、clamp 125-127 行、Top-ratio 池 141-171 行、缺失 fail-closed raise 46-48/76-82/111-121 行；件 INVARIANTS 第 8 行明写"权重与阈值为 proposed 待 IC 数据重加权"⇒ 非 blocked_on_impl | 强度榜+候选池成员标记（MOD-SIG-144 输出 WiringResult），本向只登记一句 | 两路面（880 行业族 2021-08-02..2026-10-08）可算=在册 P3/P4；四路全量面 blocked=成分口径（P6/P7）——**本条复验成立，前役 ⑥向结论不翻** | 2 | comparison×2 | **封矿不成立（推翻）** | 四路全量 IC 加权面仍 blocked_on_data（缺 2019-01-04..2026-07-21 板块成分口径）；两路面新卡均 preregistered |
| TDM-E-L2-04 | 地图三条判据陈述：高潮分≥90=次日分歧警示 / 梯队连击≥2 且 Top2 集中度≥30%=主线清晰 / 其余混沌降仓；优先级 高潮>主线>混沌（trading_decision_map.yaml:1125-1127） | 实读消费方：sector_ecology_judge.py:5 `[CONSUMERS] TDM-E-L2-04；TDM-E-L3-06 环境开关（待接线）；TDM-E-L2 板块候选池排序（待接线）`+ 生产接线 MOD-SIG-144（wiring.py:5 同列本节点）+ config/trading_day_cycle_map.yaml、generate_trading_day_cycle_map.py、src/zephyr/signal_ashare/__init__.py（Grep 反查 §3-Q2） | **机构三件套（响应曲线/时滞/条件稳定性）在本节点从未出过 calibration 卡**：前役只有 ablation/02（臂集 no_state/full_three/drop_climax/drop_mainline/priority_swapped），既无档间响应曲线，也无"合取 vs 单腿"的判定形式题 | MOD-SIG-143 常量三处真源各异：LEAD_STREAK_MIN=2（38-39 行，指 MOD-SIG-064 反向）、TURNOVER_CONCENTRATION_MIN=0.30（40-41 行，指节点原文）、CLIMAX_SCORE_MIN=90（42-43 行，指 sector_rotation_state）；合取式在 122 行、高潮优先在 113 行；**在产喂值口径由 MOD-SIG-144 决定**（wiring.py:8、56-62） | 三态标签（SectorEcology.ecology + reason 文本），本向只登记一句 | 高潮/集中度面 880 底座可算（P4）；**前役"梯队连击真口径仅 2026-09-01 起⇒blocked"经④后端复验不成立**（在码 lead_streak=880 收益排名导出的连续领涨天数，2021-08-02 起可算，见 §3-Q3）；全市场涨停比分母面待一次实测（未跑，禁令） | 2 | comparison×1 + calibration×1 | **封矿不成立（推翻）** | 本卡 calibration/02=blocked_on_data：缺逐日分母（当日在市股票数→全市场涨停比）实测，解锁成本=一条 GROUP BY trade_date 聚合；净流入集中度臂=blocked_on_data（缺 ..2026-07-21 板块级净流入） |

## 2. 前役封矿声明逐条验证（凭据=L1_ledger.md 原文行 → 本车道复验）

| 前役声明（出处） | 复验动作 | 结论 |
|---|---|---|
| L2-01 行：六向结论 + "mined_out?=部分（两路面已入卡；四路全量面挂 blocked）"，但 §7 mined_out 名单第 2 位即 TDM-E-L2-01 | 逐向对地图原文与件原文重查（§1 表 ①③④向证据行） | **推翻**：①向 `fallback:` 条款未成题、③向"改权须先出分"是自白非结论——两处本节点级未挖长尾 ⇒ 枯竭判据（六向全部已查无/已入卡）未达成 |
| L2-04 行："梯队连击真口径仅 2026-09-01 起（limit_up_pool 1426 行、daban_engine_load 19 日）⇒ 价格面代理并声明"，§7 列入 mined_out | ④后端反查件 DEPENDENCIES 与生产实现（sector_ecology_judge.py:4；mainline_candidates.py:24/163/209；analysis_utils.py:57） | **翻案（blocked 判错）**：三态判定实际消费的 lead_streak=当日收益最高板块的连续领涨天数，底座 kline_sector_880（2021-08-02 起，P3/P4 在册）⇒ 该腿可考，前役把"涨停连板梯队"的采集面缺口误挂到本腿头上 |
| L2-04-1 行与 L2-04 卡 frozen_note："三态阈值（90/连击 2/Top2 30%）全取在码既有口径不改" | 读在产接线件（wiring.py:8、56-62；sector_breadth.py:35-38、83-91） | **漏矿（新题）**：在产高潮分是涨停比四档阶跃映射 {极强95/强70/中40/弱15}，门柱 ≥90 严格等价于"涨停比>10% 单档"；前役卡的连续 z 分位高潮分与在产阶跃口径是两个不同对象，其"全取在码既有口径"表述未经一手复核 ⇒ 已另立 calibration/02 并在该卡如实登记档界来源 |
| L2-04 卡 data_binding.signal_derivation："集中度=前 2 板块成交额/全板块成交额" | 读 wiring.py:8 与 29 行"集中度=Top2 主力净流入/全池主力净流入（0-1）" | **口径错配未登记（前役遗漏）**：件常量名为 TURNOVER_CONCENTRATION（成交额），在产注入值却是净流入占比；本车道 comparison/02 以成交额口径成题（与节点原文同名），并把净流入臂登记为 blocked_on_data 的补跑面 |
| L2-01-5 / L2-01 行：市场级调节 ±10 面"已入卡" | 复核是否考过"缺路时调节杠杆被放大"这一机制（ablation/02 臂集与 pillar 文本） | **推翻（局部）**：ablation/02 的 degraded_flag_honesty 只是要求"必须标 degraded"，从未把重归一 vs 剔除作为双臂对象 ⇒ 已立 comparison/03 |
| L1 §5 长尾第 8 条"念想引擎（LSG qwen）向：受阻=未尝试" | 本车道同样未调用 LSG（预算优先留给六向对码；禁跑生成器/禁新增 LLM 审计面） | **如实登记为未尝试**，不写作"查无"；留给复挖轮 |

## 3. 六向重查凭据日志（命令/实读行号原文）

- **Q1 节点真源实读**：`config/trading_decision_map.yaml` Grep `id: TDM-E-L2-01$|id: TDM-E-L2-04$` →
  L2-01=744-779 行（algo_note 754-759、module_ref=sector_strength_aggregator.py、module_id=MOD-SIG-142、
  fallback=772、module_mounts=[MOD-SIG-144]、data_refs=[DS-059, DS-170]、confidence=untested、
  battle_map_refs=[BM-SEL-08-A] 引 裁定#483+裁定#487）；L2-04=1115-1146 行（algo_note 1125-1127、
  module_ref=sector_ecology_judge.py、MOD-SIG-143、module_mounts=[MOD-SIG-061]、fallback 字段为空、
  confidence=untested）。两节点 confidence 均=untested ⇒ 尚无已出分考卷，与"已考 18 行"名单不冲突。
- **Q2 ②下游反查**（Grep 工具替代 `git grep`，任务书 §2 依令）：pattern
  `TDM-E-L2-04|TDM-E-L2-01|sector_ecology_judge|sector_strength_aggregator`，命中 126 文件；
  其中代码/配置侧消费方=`src/zephyr/signal_ashare/core/sector_strength_wiring.py`、
  `core/sector_strength_aggregator.py`、`core/sector_ecology_judge.py`、`src/zephyr/signal_ashare/__init__.py`、
  `scripts/backtest/sector_surface.py`、`scripts/backtest/generate_backtest_backlog.py`、
  `config/trading_day_cycle_map.yaml`、`scripts/governance/d5_architecture/generators/generate_trading_day_cycle_map.py`、
  `tests/research/research/signal_ashare/sector/test_sector_{ecology_judge,strength_wiring,strength_aggregator}.py`。
  ⇒ 前役 §4-A3 对 L2-01/L2-04 的下游结论方向正确，但**未把 MOD-SIG-144（production 级）作为口径真源纳入卡面**，
  本车道三处新题（缺失处置律、净流入/成交额错配、阶跃高潮分）全部来自该件，是②+④两向交叉的产物。
- **Q3 ④后端实读（本车道主要矿源）**：
  `sector_strength_aggregator.py`（193 行全读）=纯函数、权重可注入、缺失 fail-closed、Top-ceil(N×ratio) 池、
  `[INVARIANTS]` 第 8 行与 docstring 26-29 行明示"等权为最大熵先验、IC 积累后重校（night-gw-2300 架构师自裁，
  Owner 授权'自行裁定'令）"——**该自裁不构成 ruling_registry 编号，本车道未引用任何裁定号**；
  `sector_ecology_judge.py`（140 行全读）=三态封闭、合取式 122 行、门柱 113 行；
  `mainline_candidates.py` Grep=lead_streak 定义 24 行、输出字段 163 行、无主线混沌 209 行；
  `sector_strength_wiring.py` Grep=INVARIANTS 第 8 行、四维源字段 26-28 行、BREADTH_CLIMAX_MAP 56-62 行；
  `sector_breadth.py` Grep=档界常量 35-38 行、classify_limit_up_breadth 83-91 行、ratio 定义 78-80 行。
- **Q4 ⑥数据向**（未跑 CH，全部引用在册）：880 行业族 2021-08-02..2026-10-08/78263+163038 行（P3/P4）；
  sector_constituent 6 个刷新日/323175 行（P6）；sector_constituent_snapshot 19 日（P7）；
  sector_fund_flow 17 交易日（P7）；limit_up_pool 1426 行/28 日（P7）；sector_state codes 376→729 宇宙漂移（P9）；
  kline_index 000300 2005-01-04..2026-10-09/5284 行（P10）；
  广度 7 序列 2019-01-04..2025-09-09/1622 交易日零缺日（任务书 §3；本车道实读
  `docs/_working/nightmine_campaign/series/limit_up_count.csv` 表头与首末行=1623 行含表头，
  首行 2019-01-04=84、末行 2025-09-09=66；`streak_distribution.csv` 表头 `trade_date,bucket,value`、6489 行含表头，
  bucket 含 first_board/second_board）。涨停判定 MUST 不复权 kline_daily + stk_limit（任务书 §3，hfq 得 3882 荒谬值）。
- **Q5 ⑤呈现向**：两节点均为盘后榜单/标签（强度榜+池成员、三态标签），各只登记一句，未据此立卡。

## 4. 本车道新卡清单（4 张，全部新建文件，编号承同层既有卡序）

| card_id 全名 | 族 | status | 一句话对象 |
|---|---|---|---|
| `TDM-E-L2-01/comparison/02_等权与IC加权双臂` | comparison | preregistered | 权重律本身（等权 0.25×4 vs IS 估计 IC 加权），件内 weights 可注入 |
| `TDM-E-L2-01/comparison/03_缺路处置律重归一与剔除双臂` | comparison | preregistered | 地图 fallback 条款 vs 在产剔除语义（三套缺失口径并存） |
| `TDM-E-L2-04/comparison/02_主线合取与单腿双臂` | comparison | preregistered | "连击≥2 且 集中度≥30%" 的合取形式本身 + 连击腿按在码 lead_streak 长窗可算（翻案点） |
| `TDM-E-L2-04/calibration/02_在码高潮分四档阶跃响应` | calibration | blocked_on_data | 在产阶跃映射（95/70/40/15）与 ≥90 门柱等价关系、档间响应与门柱位置检验 |

- data_binding 段四张齐备（signal_table/signal_column/signal_derivation/target_source/data_window_evidence/impl_ref），
  双臂卡的 binding 面照 series 模板（`TDM-E-L2-01-1__calibration__02`）写法，**未照**
  `TDM-X-S1-02__comparison__02_dualwindow.yaml` 抄 binding（该件无 binding 段，只抄其 pillars_numeric 键名口径
  `maxdd_improvement_min`/`sharpe_delta_min`/`oos_same_sign`）；`buckets.min_obs_per_bucket` 四张均写 60（双臂卡模板缺该字段，本车道补齐）。
- 无 `generated: true`；`preregistered_by` 四张均为 `st-mineloop-20261010-L11`。
- 与同车道/同战役既有卡的分工已逐字对照：ablation/02（子分剔除边际）、ablation/03（RX-A：叠加通道+前 15% 分位剂量响应）、
  L2-01-5/02（调节注入存在性）、L2-04-1（五态调节分）、L2-04-2（前 3 板块虹吸集中度）——本车道 4 张对象均不与之重合；
  前 15% 分位在本车道卡内取固定值不扫（避免与 ablation/03 摊薄重复）。

## 5. 复挖结论（推翻/确认）

- **TDM-E-L2-01：封矿推翻**。证据句一=前役台账 §1 本节点行自述"等权→IC 加权改权须先出分"，而 exam_cards 目录实扫
  本节点真卡仅 ablation/02 与 ablation/03，其臂集无一为"等权 vs IC 加权"双臂（已全文读两卡核对 buckets.on 字段原文）；
  证据句二=地图 `fallback`（trading_decision_map.yaml:772）、件内 fail-closed（aggregator.py:46-48/111-121）、
  接线剔除（wiring.py:8）三套缺失处置语义并存且互斥，前役六向表无一覆盖。
- **TDM-E-L2-04：封矿推翻，且前役 blocked 判据被翻案**。证据句一=MOD-SIG-143 的高潮分在产值是四档阶跃映射
  （wiring.py:56-62）且门柱 ≥90 等价于"涨停比>10% 单档"，前役以"880 Top5 z 分位"另一构造出卡并声明"阈值全取在码既有口径"，
  属口径漂移未登记（新题为档间响应+门柱位置检验）；证据句二=三态判定的连击腿在码口径是 880 收益排名导出的连续领涨天数
  （judge.py:4 → mainline_candidates.py:24/163/209 → analysis_utils.py:57），
  自 2021-08-02 可算（在册 P3/P4），故前役"梯队连击真口径缺史 ⇒ 挂 blocked"不成立，本车道已出 preregistered 双臂卡。
- **确认（不翻）的部分**：四路全量面与净流入集中度臂的 blocked 根因（板块成分口径，P6/P7 复证）本车道未找到替代读取源，
  确认前役结论；880 行业族 2021-08-02 冻结上限亦确认（唯广度序列面不受该上限约束，见 §5 L2-04 证据句一/二）。

## 6. 未挖长尾清单（明列，不降格封矿；本车道结束时两节点仍非 mined_out）

1. **MOD-SIG-144 的四维源字段与 rank-based 归一**（wiring.py:8"四维跨截面百分位排名归一 0-100（rank-based 方案=Quantpedia/研究复核裁定，抗离群）"）
   未考：截面百分位归一 vs 原值直接合成，是第三张 L2-01 双臂题，本车道受单车道产出预算未开。
2. **clamp [0,100] 的截断毁损**：件内 125-127 行先加 ±10 调节再 clamp，尾部信息被削平；
   与 comparison/02 的权重律、ablation/02 的调节臂都是不同对象，可立"截断 vs 保序不截断"双臂。
3. **梯队连击的第二读法（涨停连板梯队）市场级面**：`streak_distribution.csv`（first_board/second_board 分桶，
   2019-01-04 起）+ `max_streak_height.csv` 是已在 HEAD 的 1622 日连板形态面，可做"≥2 连板家数占比"的市场级档间响应；
   唯"板块内条件化"那一层仍受成分口径阻塞——本车道未立卡（怕与 L1-S2 广度母卡矿脉 14 张同假设撞车，遵任务书 §3 末行禁重复）。
4. **前役卡自身的口径披露债**（不改件，只入册）：`TDM-E-L2-04__ablation__02` 与 `TDM-E-L2-01__ablation__02` 的
   高潮分/集中度/子分构造均为卡内重算，与在产 MOD-SIG-144 喂值口径不同名同考——出分后若判 pass/fail，
   判的是重算代理而非生产件，须由总包在分数册侧加注，否则=假绿风险（见 §8）。
5. **sector_state 的 stage 语义**（close_final=429432/pre_open=2656，P9）与 L2-04 盘后态的对应关系未理清（本车道未查）。
6. 念想引擎（LSG qwen）向=**受阻=未尝试**（与前役 §5 第 8 条同类，未伪装成查无）。
7. 本车道未跑任何 CH 查询（21:00–22:30 禁令）⇒ comparison/02(L2-04) 与 calibration/02 的分母/行数类证据全部待总包实测回填。

## 7. 交叉复挖建议（20% 名单，含你认为前役封矿不成立的节点+理由）

1. **TDM-E-L2-01 / TDM-E-L2-04**（本车道，封矿不成立，理由见 §5 两条证据句）；
2. **TDM-E-L2-01-5**（前役 mined_out；其"市场级调节 ±10"在件里是 `MARKET_ADJUSTMENT_MAX=10.0` 的**硬封顶**，
   调节幅度响应曲线从未考过，只在码注释与地图里写死 ±10 ⇒ 与前役 ablation/02 的"注入存在性"不同对象）；
3. **TDM-E-L2-04-1**（前役 mined_out；件注释称高潮 90 阈值"真源=sector_rotation_state 既有文档阈值"，
   但生产喂值走的是涨停比阶跃映射，两处"高潮分"是否同物从未做过对卡 ⇒ 与本车道 calibration/02 成对，建议同批复挖）；
4. **TDM-E-L2-06 / L2-06-3**（`sector_strength_wiring` 的池成员输出与 L2-06 传导的接线状态：
   前役说"待接线"，件 `[CONSUMERS]` 亦写"待接线"，但 wiring 本体 [MATURITY]=production ⇒ 谁在生产里消费强度分需一次正查）；
5. **TDM-E-L2-02 / 02-1 / 02-2**（前役 §4-A3 记"零命中⇒输出未接线"，本车道的 Grep 反查工具与口径与前役
   `git grep -- src scripts config` 不完全同构，建议换 Grep 工具重跑一次②向，防"工具性查无"）；
6. **TDM-E-L2-05 / 05-2**（前役记"red_reason=pending_gate/无 module_ref"，其"水温档→参数查表"与
   MOD-SIG-144 的 ±10 查表是否同表，值得一次跨节点对卡）。

## 8. 假绿风险与阻塞（本车道上报口径）

- **假绿风险一（结构性）**：板块层两节点的既有真卡都以"卡内重算口径"作答，而生产喂值在 MOD-SIG-144；
  若这批卡出分后被写回 `TDM.nodes.*.confidence`，会把"代理口径的结论"当成"生产件的结论"。
  建议总包在分数册侧对本层所有卡加"重算口径/在产口径"标签，本车道未改任何前役件与注册表。
- **假绿风险二（样本地板）**：涨停比>10% 的"极强"档历史上极稀（可能 <60 日），
  本车道 calibration/02 已写死"稀疏档判数据不足非通过、禁报通过也禁删档"；执行器若按缺桶静默跳档，将产出假通过。
- **阻塞**：两臂卡的 arm driver（各 ≤60 行）与 L2-04 分母聚合查询归总包（本车道禁跑生成器、禁写分数册、禁 git）；
  21:00–22:30 CH 禁令使本车道 ⑥向全部依赖在册事实，未做任何新实测。

## 9. 收尾汇总（本车道）

- **节点总数**：2（TDM-E-L2-01、TDM-E-L2-04，均为前役自报 mined_out 的复挖对象）。
- **新卡总数**：4。族分布：comparison 3、calibration 1、ablation 0（前役已各持 1 张 ablation/02，本车道不再加同族臂集）。
- **status 分布**：preregistered 3、blocked_on_data 1、blocked_on_impl 0（四张卡的被测件与取数件均在岗，
  缺的是考卷侧组装，已在各卡 `executor` 字段标注为接线工单而非 blocked_on_impl）。
- **mined_out 名单**：无（两节点均判"封矿不成立"，且 §6 仍列 7 条本节点级长尾）。
- **blocked 明列（缺哪张表哪一段，写死在各卡 data_binding.blocked_reason/blocked_scope）**：
  L2-04/calibration/02 缺全市场涨停比逐日分母（当日在市股票数，kline_daily 不复权 + stk_limit 可算，待 22:30 后一条聚合）；
  L2-01/comparison/02 的四路全量面缺 2019-01-04..2026-07-21 板块成分口径；
  L2-04/comparison/02 的净流入臂缺 2021-08-02..2026-07-21 板块级主力净流入。
- **红线自查**：未执行任何 git 命令；未跑 CH 重查询；未写注册表/分数册/creation_tokens/trial_ledger/CAP 册/AGENTS.md；
  未改任何已存在文件（本车道只新建 4 张卡 + 本台账）；判据面写死后未回改；未引用任何 ruling_registry 编号
  （件内"架构师自裁"文字未当作裁定号使用）。
