---
ttl: task_bound
doc_type: log
title: L07-EXE7 子块挖矿簿 · 滑点/成本标定真源（cost_model_calibration）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-L07
status: MINE 完成（六向封口）；新证四条（执行侧冲击腿整体缺席 / 打板 7.2 倍低估 / 注册表域界错位 / 再标定无调度）
---

# L07 · EXE-7 滑点标定 cost_model_calibration

**① 职责一句话**：用真五档快照把"一笔单子花多少成本"标成**有出处的数**（滑点腿/冲击腿/佣金腿三分），并作为全仓成本参数的单一真源位点——它是执行层所有"预估 vs 实际"比较的**左半边**。

**② 现状实测**（`src/zephyr/backtest/core/cost_model_calibration.py` 501 行正文级实读）

| 项 | 实测值 | 出处 |
|---|---|---|
| 身份 | MOD-BT-001，MATURITY=**testing**，STARTUP=imported，[DEPENDENCIES]="无（纯常量+纯函数）"，SAFETY=M，ai_autonomy=ai_modifiable | 头注 :6-14 |
| PROVENANCE | 窗口 2026-07-24~2026-09-16、5,519 标的、五档快照 13,119,233 条；`:113` 起结构化记录 | 头注 :30 + :113 |
| 滑点腿（5 档，bps/单边） | `SLIPPAGE_TIER_BPS = (7.24, 5.69, 4.67, 4.00, 2.34)`，`TIER_NAMES=("Q1_illiquid"…"Q5_liquid")`，`SLIPPAGE_BPS_UNIVERSAL=3.79`，`LEGACY_FLAT_SLIPPAGE_BPS=1` | :183/:228-237/:240 |
| 分档阈值 | `ADV_QUINTILE_BOUNDS_YUAN` :175、`TIER_ADV_MEDIAN_YUAN` :186、`TIER_TICK_BPS=(8.783,9.170,7.915,6.940,4.140)`（**注意 Q2 的 tick_bps 高于 Q1，非单调**——件内 INVARIANT 只约束 `SLIPPAGE_TIER_BPS` 单调非增，tick 维未纳 INVARIANT） | :195 |
| 冲击腿 | `IMPACT_BETA=0.4205`、`IMPACT_GAMMA_RATIO=0.0`（永久项实证不可辨识）、`IMPACT_PERMANENT_EXPONENT=0.5`、`IMPACT_TIER_ETA/SIGMA` 分层表；对照常量 `DEFAULT_PARAMS_REF={"eta":0.1,"beta":1.0,"gamma":0.05,"sigma":0.02}` | :307-339 |
| 读法 | `resolve_slippage_bps`（开关→tier→universal→LEGACY 四段，:279-299）+ `calibration_enabled()` 调用期读全局（为 monkeypatch 留口，:257-264）；地板佣金闭式 `min_notional/…` :444-467 | — |
| 生产触发面 | **标定=一次性批产出，无再标定调度**；消费面见 §③④ | — |
| 数据新鲜度 | 窗口末 2026-09-16 → 本班日 2026-09-26 已 **10 个交易日+**无再标定，件内/仓内**无过期告警**（查法：grep `PROVENANCE` 无 expiry/stale 字样；`scripts/` 内无再标定计划任务包装器） | 实测 |

**③ 六向台账**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：证据来自 `tick_depth_5` 五档（EXE-8 供）+ 本地无泄漏复算脚本（TESTS 指向用例）；判重/治本对象=`full-auto-chain/S11…/slippage_impact_cost_mining.md` §1.2/1.3/1.5。外部：待办。 |
| ②下游 | 内部：全仓 `cost_model_calibration` 消费件实测 **11 个**：backtest 六件（`matching_logic/matching_engine/vectorized_engine/cost_attribution/result_repository`+自身）+ **`strategy_factory/owner_band_t/{costs.py,__init__.py}` 与 `owner_regime_switcher/{costs.py,__init__.py}`**（=策略工厂侧，SKEL §2 EXE-7④"执行域零消费"须精确化为"执行域(ex_core/ex_sor)零消费，但 strategy_factory 已吃标定"，band_t/regime 属别车道，本册不掘）+ `scripts/backtest/eval_exp_expectations.py`。`exam_cost_gate` 未在本轮 grep 命中（MINING 债：SKEL 列它为消费者，本册未复现，二者其一需更正）。外部：待办。 |
| ③算法/机制 | 内部：(a) **两腿互斥计费**是核心不变量（滑点=尺寸无关、冲击=尺寸相关），且件内实证 `eff < c1` → 滑点不含尺寸溢价（INVARIANT :8）。(b) γ=0 的理由（"把测得的瞬时位移拆一半给 γ 会双重计费"）是**可审计的方法论裁定**，写进注释=合标本仓 MODIFY-GUARD 纪律。(c) `TIER_TICK_BPS` 非单调（Q2>Q1）说明 tick 维与有效价差维不是同一因果链，件内只用后者做档位，前者只作披露——**这是"数据里有但语义未闭环"的正例**，与"字段在≠数据可得"互补。外部：待办（AC η·p^β·σ 的 β 经验值域 0.3-0.6 需外部二源对表，本册不断言）。 |
| ④后端 | 内部：纯常量+纯函数、Fail-Closed 抛 `CostCalibrationError(ZA-BT-0044)`（错误码改号留痕记录完整，:59-66）；NaN 陷阱有专注释（:418 "`Decimal('NaN') <= 0` 恒为 False"）——后端质量高，**本册零后端缺口**。外部：已查无（查法：本件无 IO/无并发/无存储可查）。 |
| ⑤前端 | 内部：标定结果的人工面=`cost_model_registry` 在 `api_server.py:1479/:1500` 有词表映射与条目读取函数（`_read_cost_model_registry_entries`），即仪表盘可展示，但**"标定档位 vs 注册表 active 值"的对比视图无**（L07-C08 的人工监督面缺位）。外部：待办。 |
| ⑥数据字段 | 内部：`cost_model_registry.yaml` CST-ASTOCK-001（active，v1.1.0，updated_at 2026-08-24）实测字段值：`slippage{model: fixed, params:{bps: 1}}`、**`market_impact{model: none, params: null}`**、`impact_model: none`、`propagator_config: null`、`used_by_strategies: [STR-DABAN-022, STR-MULTIFACTOR-096, STR-EVENT-001]`、`module_id: MOD-L06-001`、**`code_path: src/zephyr/backtest/core/engine_base.py`**、`owner: MOD-EX-CORE`。外部：待办。 |

**④ 缺口清单**（本册新立；SKEL L07-C08「双真源收敛」、L07-C07/D36、CST-T0-001 挂起（B-007）引用不重复）

| 编号 | 内容 | 级别 |
|---|---|---|
| **L07-S7-G1** | **执行侧成本模型不是"低估"而是"整腿缺席"**：SKEL/L07-C08 的口径是"CST-ASTOCK-001 fixed bps=1 与标定 3.79 冲突"（3.8 倍）。本册实测注册表原文发现**更严重的一面**：`market_impact.model=none` + `impact_model: none` → 执行侧（L4-09 发单前成本估算）**完全没有冲击腿**，而标定已给出 `IMPACT_TIER_ETA/SIGMA/BETA` 全套分层参数躺在回测侧。滑点低估 3.8-7.2 倍是"量"，冲击整腿归零是"质"。 | **P0**（并入 L07-C08 施工范围，本册提供实证字段） |
| **L07-S7-G2** | **打板票（低流动性档）成本被系统性低估至 1/7.2**：`used_by_strategies` 含 `STR-DABAN-022`，其成本口径=`fixed 1bp + impact none`；打板标的按标定属 Q1_illiquid（7.24bp）且冲击最大 → 打板执行的"预估成本 vs 实际"偏差在**全 L07 所有子块中方向最确定、量级最大**，直接支撑 EXE-9 的可行性判断（收益预期被成本假数撑高）。 | **P0**（与 EXE-9 交叉，见该册） |
| L07-S7-G3 | **注册表条目域界错位**：CST-ASTOCK-001 `module_id=MOD-L06-001`（执行域）+ `owner=MOD-EX-CORE`，但 `code_path` 指向 **backtest/core/engine_base.py**，且件自身 [CONSUMERS] 只列回测件。→ SSOT 上"这条成本规则归谁、改它要过谁的门"两处指向不同域；REFERENCE-INTEGRITY/锚点 gate 只看 code_path，执行域改它不会触发。 | P1（治理/门位） |
| L07-S7-G4 | **无再标定调度与过期告警**：PROVENANCE 有窗口无 TTL；证据窗结束后市场微观结构变化（价差/波动）静默侵蚀标定有效性，且 `MODIFY-GUARD` 只约束"改数须附证据"，不约束"数过期"。终局全貌=周期性重标定 + 窗口年龄闸（与既有 `*_staleness_audit.py` 同族）。 | P1 |
| L07-S7-G5 | **`exam_cost_gate` 消费者归属待勘**：SKEL §2 EXE-7④ 列它为消费者，本册全仓 grep `cost_model_calibration` 未命中该件 → 二者之一需更正（若 SKEL 误记，则"考试成本闸不吃标定"=闸与真源脱钩，性质更重）。 | P1（事实核查，零代码） |
| L07-S7-G6 | **`almgren_chriss_impact_model.DEFAULT_PARAMS` 恒被消费的旧症**（件内 :23-24 自陈"estimate_params 零生产者，实盘成交相对决策价恒 ±1.000bp 零方差"）：本册复核该症在 `estimate_params` 侧是否仍零生产者=未查（MINING 债，属 EXE-7 正文清单第 6 件）→ 不立项仅登记，防与 L07-C08 重复计。 | MINING 债 |

**⑤ 自审闸三态裁定**

| 项 | 裁定 | 理由（量尺=终局全貌） |
|---|---|---|
| G1 | **施工 P0**，作为 L07-C08 的**范围扩面**（原范围只到"回写滑点腿"）：执行侧成本模型须补 impact 腿（吃 `IMPACT_TIER_*`），并明确"无 ADV 输入时 fail-closed 取保守档"而非取 0。 | 执行层的自动化决策（下单规模/是否拆单）建立在成本预估上，冲击腿=0 等于告诉系统"大单免费"，会**结构性诱导超大规模单**；这是终局全貌下必须先修的正确性，不是优化。 |
| G2 | **施工 P0（同一批改）**，并把结论回写 13 号文/EXE-9 打板可行性口径 | 打板是 L07 中唯一"高成本+高冲击+低流动性"三叠加场景，用 1bp 假设做决策=纸面盈利假象的风险源。 |
| G3 | 施工 P1（登记口径修正：`code_path` 与 `owner` 对齐，或拆执行/回测两条条目并声明关系） | RULE-SSOT/锚点 gate 依赖字段正确性；错位的锚点=假绿 gate。 |
| G4 | 挂起排期：解锁条件=五档数据补齐（D36，EXE-8）后再定重标定周期——数据尾巴没齐之前排再标定必然拿旧窗凑数 | 顺序依赖，非不重视。 |
| G5 | 施工（纯核查，两分钟命令级） | 假绿/假红都算事故。 |
| G6 | MINING 债留档 | 未读正文不立项。 |

**⑥ 挖矿日志**

| 轮 | 矿脉 | 判定 | 备注 |
|---|---|---|---|
| R1 | 头注全文（501 行件，PROVENANCE/三段语义/治本对象） | signal | — |
| R2 | 常量区全量（tier 表/bounds/impact 参数/LEGACY） | signal | 3.8 倍口径复算=3.79/1 成立 |
| R3 | 全仓消费件 grep（11 件，含 strategy_factory 两件） | signal | 精确化 SKEL"执行域零消费"；G5 由此暴露 |
| R4 | `cost_model_registry.yaml` CST-ASTOCK-001 原文逐字段 | signal | **G1/G2/G3 主证**（impact none + 域界错位） |
| R5 | registry 加载方 grep（decision_map/api_server/commit gate） | signal | 说明注册表确实进执行链（decision_map.py），故 impact none 是真在产口径 |
| R6 | `calibrate_cost_tier_redblue.py` / `exam_cost_gate.py` / `almgren_chriss_impact_model.py` 正文 | **未做（预算内主动舍）** | 三件属 SKEL §3 已列 MINING 债，本册优先把"执行侧缺腿"这条 P0 挖实；G6 因此留债不立项 |
| R7 | 外部对表（A 股有效价差/冲击成本实证量级） | **未做** | 推迟；本册结论全部出自仓内实测字段，无外部论断依赖 |

**本册封矿判据**：六向封口（④后端向已给"已查无+查法"）；执行侧三条 P0 有字段级证据；长尾=R6 三件正文 + `TIER_ADV_MEDIAN_YUAN`/bounds 与 CH 五档实测对平 → **判 MINING（标定证据链本体未复核），参数消费侧封口**。
