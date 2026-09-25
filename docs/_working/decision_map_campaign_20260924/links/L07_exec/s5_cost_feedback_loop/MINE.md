---
ttl: task_bound
doc_type: log
title: L07-EXE5 子块挖矿簿 · 成本反馈 L4-14（三零件 + 回写断链）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-L07
status: MINE 完成（六向封口）；新证=断链不止一条边，反馈环缺"数据平面"与"落库位点"
---

# L07 · EXE-5 成本反馈 L4-14

**① 职责一句话**：把"这一单实际执行得怎么样"量化成可比较的数（滑点归因 / 质量评分 / 全成本分解），并回灌给下一单的算法选型——是 L07 唯一的**学习闭环**，没有它执行层就是开环拍参。

**② 现状实测**（三零件 1,819 行正文级实读）

| 件 | 行 | MOD | 实测要点 | 触发面三态 |
|---|---|---|---|---|
| `ex_sor/services/slippage_analyzer.py` | 572 | XS-017 | 多基准（到达价/VWAP/TWAP/前收/决策价）；三因子归因=冲击/时机/价差+**残差项**（:533 `residual = total - attributed`，允许不归因余量）；冲击预测 `impact = coeff*sqrt(participation)*vol_bps`（:298，平方根律） | **覆盖未接电**：`analyze()` 无生产调用方（本册 grep 未见现役装配） |
| `ex_sor/services/execution_quality_scorer.py` | 532 | XS-018 | 四维阈值=最差线：price 50bps / time 300s / cost 30bps / impact 20bps（:84-87）；权重 price **.35** / time **.25** / cost **.25** / impact **.15**（:144-147，和=1.0 有 INVARIANT 自检）；verdict good≥.8 / acceptable≥.5 / poor（:90-91） | **覆盖未接电**：[CONSUMERS] 自注"XS-011 反馈环"，selector 侧零引用（SKEL 09-25 复核 + 本班 grep 复证） |
| `ex_sor/services/transaction_cost_optimizer.py` | 715 | XS-019 | 六项分解：佣金/印花税（**卖方单边 5bps=0.05%**，:138-145）/过户费（双边 0.1bps，件内自注 2022-04-29 由 0.002% 降）/监管费/冲击/机会；显性+隐性=总（INVARIANT :8） | **覆盖未接电** |
| `ex_core/execution_param_optimizer.py`（旁系收口件） | — | MOD-EX-064 | `tca_reader: Callable[[], list[TcaSnapshot]] \| None = None`（:115）；`run_cycle` 内 :203-207 **双重 Fail-Closed**：未注入 raise、读空亦 raise（"TCA 读数为空（无法计算目标函数）"）；白名单外参数硬拒（:135/:173，风控硬阈值禁自动优化）；`ai_autonomy=human_gated` + 提案需操作人（:252） | **覆盖未接电**：全仓 grep `ExecutionParamOptimizer(` 非自身文件=**0 命中**；[CONSUMERS]="运行时装配批"（:5）——与 `three_way_reconciliation`、MOD-PLAN-021 同一种"装配批"自注病 |

**数据新鲜度**：三零件历史=**纯内存**（`self._history: list[...]`，slippage :341 / TCO :342；均无 `maxlen`/`deque`，且有公开 `clear_history()` :570-572）→ 落库位点=**0**；进程重启后反馈环输入恒空。

**③ 六向台账**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：滑点分析要 `avg_fill_price` + 五类基准价 + adv + volatility + spread_bps；**其中 avg_fill_price 的真实生产者=EXE-3 `_sync_deals`，而该字段是"最后一笔价而非加权价"（EXE-3 G5）**→ 多笔部分成交时本件所有基准滑点全部继承失真，且失真方向不定。外部：待办。 |
| ②下游 | 内部：唯一定义中的下游 XS-011 断（复证）；旁系实际读者=`reporting/deviation_attribution_decomposer.py`、`simulation/divergence_attributor.py`、`ml_train/research_data_manager.py`（SKEL 已 grep 立证，本册不重复），三者语义=回测偏离归因，非"选型反馈"。`execution_param_optimizer` 是**理论上最合适的读者**（其 TcaSnapshot 正是为此设计），但它自己也没接电。外部：待办。 |
| ③算法/机制 | 内部：(a) 阈值是**线性"最差线"**（score=0 @50bps），不是标定曲线，且阈值/权重**全为默认常数、无来源标注**（本册未见 PROVENANCE 行，对比 EXE-7 `cost_model_calibration` 有 PROVENANCE 纪律）→ 评分不可审计"为什么 50bps 算差"。(b) 归因含残差项，允许"解释不了"的比例存在，但**残差占比无告警**（残差大=模型失效，静默）。(c) A 股适配闸：impact 20bps 阈与 sqrt 律参数来自英文文献口径，件内未做 A 股 T+1/无做市商/散户主导的重标定（对比同仓 `cost_model_calibration` 已用 1,311 万条五档实测标定）→ **两套冲击口径并存**。外部：待办。 |
| ④后端 | 内部：三件均纯 stdlib/Decimal，零 IO；本件族**唯一缺的就是持久化后端**，且 `slippage_analyzer` 的 `_history` 无上限=常驻服务内存单调增长（同仓 `qmt_file_bridge_broker` 对 `_deals` 有 100 条环形上限，证明该纪律存在但未贯彻到反馈环）。外部：待办。 |
| ⑤前端 | 内部：无人工面——无"执行质量"看板件（本册 grep 未覆 dashboard 侧，MINING 债具名）；`human_gated` 的优化提案确认通道（MOD-EX-064 [CONSUMERS] 自列"人工确认通道接线"）不存在。外部：待办。 |
| ⑥数据字段 | 内部：本件族需要的字段与 EXE-4 表**互不匹配**：scorer 要"下单到完成耗时"（time 维）→ execution_report 有 `execution_start/end`；TCO 要"印花税适用与否（买卖方向）"→ 表有 `direction`；但表**无 `parent_order_id`**（EXE-4 G6），按算法分桶统计在切片单下不可行。更根本：**表里现在只有 1 行且是 -10000bp 毒值**（EXE-4 实测）→ 反馈环的"数据可得"当前=0。外部：待办。 |

**④ 缺口清单**（本册新立；SKEL L07-C02 接线图纸、L07-C04 接读者、TRD-A08/LK-12 引用不重复）

| 编号 | 内容 | 级别 |
|---|---|---|
| **L07-S5-G1** | **反馈环缺数据平面，接线不足以成环**：三零件历史全内存无落库；即便按 L07-C02 把 selector 接上 scorer，selector 读到的是**本进程生命周期内**的评分，冷启动/每次重启=空历史 → 一条"接好但永不带载"的边=新型静默失败（比断链更坏：看着是通的）。**L07-C02 施工图纸必须扩为"落库位点 + selector 读库 + 冷启动最小样本数"**。 | **P0**（对 SKEL L07-C02 的直接增补） |
| **L07-S5-G2** | **MOD-EX-064 执行参数自优化器零装配且其硬前置不可满足**：`tca_reader` 未注入即 raise（:203），注入也无表可读（EXE-4 表 1 行毒值）。终局全貌下"执行参数自动寻优"是本环节的核心自动化件，现=production 标记下的死件。 | P1 |
| L07-S5-G3 | **评分阈值/权重无标定无 PROVENANCE**：50/300/30/20 与 .35/.25/.25/.15 皆为默认常数，无来源、无 A 股重标定；与同仓已建立的 PROVENANCE 纪律（EXE-7）不一致。 | P1 |
| L07-S5-G4 | **冲击口径双真源**：`SquareRootImpactPredictor`（coeff 注入，件内）∥ `cost_model_calibration` 的 AC η·p^β·σ 标定腿 ∥ `almgren_chriss_impact_model.estimate_params`（EXE-7 MINING 债自注"零生产者"）——三处冲击模型无相互认证。 | P1（内收 w5_1 候选） |
| L07-S5-G5 | **滑点输入受 EXE-3 G5 污染**：`avg_fill_price` 非加权 → 三零件输出全部失真，且失真在评分侧不可见（price 维只会偏低或偏高，无来源旗标）。 | P1（修在 EXE-3，记在 EXE-5） |
| L07-S5-G6 | **残差占比无告警**（归因失败=静默）；`clear_history()` 公开无护栏。 | P2 |
| L07-S5-G7 | **反馈环全链零成本口径校验**：TCO 印花税默认 5bps（卖方单边，2023-08-28 减半后的口径）与 `CST-ASTOCK-001`、`cost_model_calibration` 佣金腿是否同值，本册未对平（MINING 债具名，防"三处费率各写一遍"）。 | MINING 债 |

**⑤ 自审闸三态裁定**

| 项 | 裁定 | 理由（量尺=终局全貌） |
|---|---|---|
| G1 | **施工 P0**，且判为 **L07-C02 的验收前置**（不做落库=接了也不闭环，属"假绿施工"） | 终局全貌要求"每一单的评分成为下一单的输入"，跨进程持久是唯一实现路径；禁以"现在只有 sim 几单"封矿——样本少是冷启动问题，可用 `min_samples_before_feedback` 显式表达，不是不建的理由。 |
| G2 | **挂起排期**：解锁条件=(a) EXE-4 G1 毒值修 + (b) L07-C04 接读者落表 + (c) Owner 定"自优化白名单参数集"（该件 [CONSUMERS] 自列"风控硬阈值白名单声明"至今无声明件）。 | 顺序依赖 + Owner 门位双因。 |
| G3 | 施工 P2（可挂 `scripts/calibrate_cost_tier_redblue.py` 同族红蓝标定批，复用 PROVENANCE 纪律不新建） | 评分是"自动决策的输入"，其阈值必须有证据。 |
| G4 | **挂起排期**：解锁条件=L07-C03（算法层收口）+ L07-C08（成本参数双真源收敛）出裁定后统一归一，单独收冲击模型会撞车 | 跨块内收，需上位裁定。 |
| G5 | 移交 EXE-3 清单（不重复立项） | 修点不在本块。 |
| G6/G7 | G6 施工 P2（两行告警）；G7 记 MINING 债不裁定 | 零伪造纪律：未对平不立项。 |

**⑥ 挖矿日志**

| 轮 | 矿脉 | 判定 | 备注 |
|---|---|---|---|
| R1 | 三零件行数/头注/阈值/权重常量区实测 | signal | §② |
| R2 | 持久化面 grep（`_history/deque/maxlen/persist/json.dump/write_tsv`） | signal | **G1 主证**（三件全内存 + 有 clear_history） |
| R3 | `execution_param_optimizer` 注入协议 + 全仓装配反查 | signal | **G2 主证**：零实例化、双 Fail-Closed、human_gated |
| R4 | TCO 显性六项与 A 股费率口径核对 | partial | 5bps 印花税/0.1bps 过户费为件内自注口径，**未做外部对表**（推迟）→ 记 G7 MINING 债 |
| R5 | 旁系消费者（deviation_attribution_decomposer 等三件） | 沿用 SKEL 立证 | 本册不重复 grep（省预算），标"引用 SKEL §④" |
| R6 | 外部对表（execution quality scoring / slippage feedback loop 业界做法） | **未做** | 推迟 |

**本册封矿判据**：六向封口；三零件正文级已读关键区（阈值/权重/归因/历史面）；长尾=`transaction_cost_optimizer` 机会成本段正文、`slippage_analyzer` `_attribute` 全式、dashboard 执行质量看板有无（三项均具名 MINING 债）→ **判 MINING，主结论（断链不止一条边 + 缺数据平面）封口**。
