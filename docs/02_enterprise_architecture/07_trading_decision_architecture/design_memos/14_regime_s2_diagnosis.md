---
ttl: permanent
doc_type: architecture_view
title: "S2 评分算法时点错配诊断与治本方案——capitulation 过程化 + valuation 基本面化 + V 反转通路"
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.5.4"
date: "2026-08-15"
last_updated: "2026-08-31"
topic: regime_s2_diagnosis
scope: 07_trading_decision_architecture
doc_id: 14_regime_s2_diagnosis
priority: P1
depends_on:
  - 10_regime_detector_spec.md
  - 11_regime_backtest_validation_plan.md
  - 12_regime_phase2_validation.md
  - 13_regime_phase3_engineering_plan.md
related_modules:
  - MOD-REGIME-001 (RegimeDetector)
  - MOD-REGIME-002 (RegimeFeatureBuilder / OverlaySignalsConstructor)
  - MOD-REGIME-VAL-002 (Phase 2 验证器 / B4TransitionAccuracy)
related_issues:
  - '#ARCH-REGIME-OVERLAY-001'
  - '#ARCH-REGIME-S2-ALGORITHM-001'
---

> ## 结案报告（AI-NIGHT-001 复核 2026-08-19）
>
> **实际开发**：P0 两层处置已落地（commit 93a25890）——① 两个治标 bug 修复：`s2_capitulation_score` vol_z 阈值 z>2→z>1、`s2_valuation_score` rolling(250).max() 加 min_periods=20；② `design_match` 设计域定级字段落码（b4_transition_accuracy.py:99/212 实证），3 个 S2 事件标 `design_match: false`（historical_events.yaml:82/91/100 实证，data_ready 维持 true），B4 回 PASS(3/3)，Phase 2 闭环；`#ARCH-REGIME-S2-ALGORITHM-001` 缺陷登记完成。诊断脚本 dump_s2_scores.py 沉淀可复用。
>
> **最终成果**：S2 算法时点错配完整诊断 + 架构裁定（路 3：design_match 排除 + P0 治标 + P1 治本，守住验证独立性）+ P1-E9 治本详设（§4 五子项 + Step 0 勘探门禁 + §4.5 防过拟合方法论栈）定稿。
>
> **未做事项及原因**：P1-E9 五子项全部未施工（grep 实证零命中）——E9a capitulation 衰减加权和 + 多过滤器（_capitulation_daily 不存在）、E9b valuation 路 A CAPE/PB 分位（s2_valuation_score_fundamental 不存在）+ 路 B 阈值放宽、E9c spring 复用 wyckoff_engine + 深度分级 + velocity、E9d breadth_thrust V 反转通路（s2_breadth_thrust_score / keys_or_gte 析取字段均不存在）、E9e three_yang 6 维分级（现仅 pct_change 单参数旧版）；属 P1 工程未排期，Step 0 勘探（daily_valuation 字段/wyckoff Spring 接口/涨跌家数/期权 put-call）未启动。演进方向 6 项（AH-HMM/LVI/滞回触发器/ProRealCode FSM/EVR/flush）为远期登记。

> ## 结案报告回填（2026-08-28 代码实证复核）
> 原"E9 五子项全部未施工（grep 零命中）"已严重过时：E9a-e 治本全部落码（overlay_features.py 五函数+regime_detector.py keys_or_gte，详见 13 号回填）；诊断脚本 scripts/tests/dump_s2_scores.py 已沉淀；P0 治标（b4 design_match 字段+historical_events.yaml 三事件标 false）在位。
> **仍真实未完工**：E9 落码后未重跑 B4 将 S2 三事件 design_match 翻回 true（收尾验证动作）；演进方向 6 项（AH-HMM/LVI 等）远期登记（既定）。

> ## B4 S2 重验注记（AI-WAVE1-001，2026-08-28）
> E9 落码后重验**未通过（0/3）**，historical_events.yaml 三事件 design_match 维持 false。方法：生产路径逐日实证（OverlaySignalsConstructor.build_for_date → RegimeDetector.record_transition，B4 ±5 交易日窗口），另做 ±25 交易日宽窗口峰值扫描；同日 run_phase2_validation --first-batch 权威对照 A1 PASS + B4 PASS(3/3 S1)，环境一致。逐事件差距（±25 窗口内各维度峰值）：
> - **EVT-2015-RECOVERY**：trigger 仅卡 capitulation——vix max=60(@09-18)/bad_news_flat max=80 在位，capitulation 全程 0.0；confirm 卡 fund=0（breadth_thrust max=60@08-11 / policy 80 / valuation 60@08-26 峰值在位，wyckoff max=10）。
> - **EVT-2020-RECOVERY**：trigger 卡 capitulation=0（vix 60@03-30 / bad_news_flat 80 在位）；confirm 卡 valuation=0（路 B pos≈0.86-0.90 不给分）+ fund 峰 50@03-05 与 breadth_thrust 60@03-06 不同日；spring max=3@03-23。
> - **EVT-2024-RECOVERY**：confirm 仅卡 valuation=0——E9d breadth_thrust 析取通路实证有效（09-27/09-30/10-08 breadth=80、policy 40-60、fund 50-70 同日在位）；trigger 三维（capitulation/vix/bad_news_flat）全 0。
> **差距结论**：①E9a capitulation 三过滤器（量能>2.0×均量 + 实体>40%ATR + 下影线>50%）联玩过严（A 股暴跌日 close≈low 致下影线比≈0），叠加衰减权重 w₀≈0.09（单日 90 分仅贡献 ~8 分），trigger≥60 实际不可达——三事件 ±25 交易日全程 0.0，含 2015-08-26/2020-03-23 真实底部；②E9b 路 A（s2_valuation_score_fundamental）未接线——builder 仍走路 B s2_valuation_score(close)（overlay_signals_builder.py:349-350 注明"路 A CAPE 待 daily_valuation 管道，Step 0 ①"），V 反转 pos 高→0；③E9e three_yang 三事件窗口全 0（strong_confirm 门槛 three_yang≥2 不可达）；④2015 fund=0（资金数据源覆盖不足）。后续方向：capitulation 过滤器/衰减参数需按 §4.5 walk-forward 校准（非简单降阈值凑分）；路 A CAPE 分位管道（daily_valuation）建设后接线。

> ## 结案报告回填（2026-08-31 复核：S2 校准已落产 + B4 重验闭环）
> 上述 2026-08-28 重验注记的"三过滤器需 walk-forward 校准"已闭环——**S2 校准专项已落产**：Owner 2026-08-29 裁定选项 1（commit c5c23036），capitulation 终选组合 `precrisis_z + close_pos + pct250 + decayed_max`（halflife=10 / lookback=20 / trigger≥60 未动）经 walk-forward 组合扫描（12 组预注册，IS 2010-2018 / OOS 2019-2026，三事件全程未参与选型）选型并接线生产（overlay_signals_builder.py:339-340）；three_yang 终选 `v2_index`（d5=-15%，删 d4 误抄维）同步落产；valuation 路 A（index_valuation_daily CAPE 分位主轴）已建成接线，2015/2020 的 0 分经勘探判定为正确信号（非深度低估）。六层验收：WFE=3.44 ✅ / fp@≥60=0.8% ✅ / 参数平移 ±10% 零变化 ✅ / MC 置换 p=0.87 ❌（诚实标注，DSR N=17 备案）/ MinTRL 低置信标注 ✅ / 预注册纪律 ✅（验证报告 2026-08-29 已归档 docs/_archive/）。B4 全量重跑（2026-08-30）A1/B4/A2/B1 全 PASS——EVT-2024 design_match 翻 true（confirm Δ=+3/+4/+5d 实证），2015/2020 维持 false 带边界注记（事件标注时点距真实底部超 halflife=10 衰减物理极限）。参数终值已回写 §4.1/§4.2/§4.4b（v0.5.3）。
> **仍真实未完工**：ERP 列全表 NULL（known_data_gaps 登记 accepted，路 A 加分项不可用但不改 confirm 判定）；2015/2020 两事件 design_match 维持 false（开放问题 3）；fund/vix 维度升级归 P1-E4/P1-E7 跨工程项（开放问题 7/10/11）；演进方向 6 项（AH-HMM/LVI 等）远期登记（既定）。

# S2 评分算法时点错配诊断与治本方案——capitulation 过程化 + valuation 基本面化 + V 反转通路

> **前置**：Phase 2 验证 B4 曾因 `data_ready=False`（S2 不计分母）以 PASS(3/3) 闭环
> （commit 0c5ea28bb1/83c94c4f，见 [#ARCH-REGIME-OVERLAY-001](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml)）。
> **本文档触发**：另一 session 将 S2 `data_ready` 误改为 `true` 后 B4 退回 FAIL(3/6)，
> 诊断确认为 **S2 评分算法时点错配缺陷**（非数据缺失），据此给出治本方案 P1-E9。
> **结论**：以 `design_match=false` 排除 S2 事件（数据已就绪但 Wyckoff 吸筹模板不匹配 A 股
> V/政策型复苏）+ 修复 capitulation/valuation 两个 P0 bug（commit 93a25890），让 Phase 2 闭环；
> S2 算法重设计独立为 P1-E9 工程项
> （见 [13_regime_phase3_engineering_plan §3.5](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md)）。
>
> **修订历程**：
> - **0.2.0**：同步 §1.2/§4 现状描述与源码；三维度算法吸收 2026 研究（ChartMath capitulation 四过滤器、
>   Wyckoff/ScienceRehashed Spring 四要素、A 股 PE 历史分位）；拆分 §3（P0 收尾）/§4（P1 治本）；新增 §4.0 范围边界。
> - **0.3.0**：① capitulation 从 rolling max → **衰减加权和**（防状态粘滞，参考 ArrowAlgo/Pomegra 2026 signal decay）；
>   ② valuation 路 A 从 PE_TTM 分位 → **CAPE/PB 分位优先**（防危机期盈利失真，参考雪球 2026 席勒 PE 报告）；
>   ③ 补施工流程：调用链改造、ATR 自实现（项目无现成）、TDD unit test stub、数据字段映射；
>   ④ 补 spring velocity 量化阈值、施工顺序、预期效果量化预估、开放问题优先级。
> - **0.3.1**：裁定落地后回写 §2.4/§2.5/§3.1/§3.2——原 v0.1.0/v0.2.0 拟"回退 `data_ready=false`"，
>   实施（commit 93a25890）升级为 `design_match=false` 排除（data_ready 维持 true，因数据确已就绪，
>   问题在算法设计域而非数据）。新增 §1.2.4 记录两个 P0 bug 修复（capitulation z>2→z>1 治标、
>   valuation min_periods=20 治本），§4.1 标注阈值调整治标性，§5 联动清单更新实际状态。
> - **0.4.0**（全网 2026-08-08 研究复审）：① 修 v0.3.1 回写遗漏——§2.1 增"路 3 design_match 排除"，
>   §2.5/§3/§5 彻底对齐已发布裁定（v0.3.1 仅改头未改正文，正文仍残留"回退 data_ready=false"）；
>   ② §1 诊断回写 commit 93a25890 的精确结论：capitulation 非"恒 0"而是"窗口外触发"（2015=08-24/25，
>   早于 09-15 事件日 3 周），wyckoff 非"诊断正常"而是"吸筹模板 vs V 反转设计域不匹配"；
>   ③ **扩 P1-E9 范围**：commit 明示"加政策/V 反转信号"，新增 §4.4 V 反转通路——confirm 改析取逻辑
>   `wyckoff≥60 ∨ (breadth_thrust ∧ policy)`，引入 Zweig Breadth Thrust 作 confirm 维度（V 反转时
>   wyckoff 不触发但 breadth thrust 触发，正好补盲区）；④ §4.1/§4.2/§4.3 并入 6 项研究背书的算法补强
>   （下影线过滤器 / 量能 2× / 实体用 open / Spring 深度分级 / CAPE 5 年 / stage 参数占位 + 数值边界）；
>   ⑤ §4.0 施工顺序补 TDD-first + Step 0 数据/接口勘探门禁。
> - **0.4.1**（全网 2026-08-08 研究复审增量补遗）：v0.4.0 已完成一致性修复 + 多数算法校准。本次补
>   v0.4.0 遗漏的 5 项（均 2026 研究背书）：① §4.2 路 A 补 ERP **绝对值**阈值（>5% 大底/>6% 熊末，
>   雪球炎黄投研 2026，原仅分位>0.95）+ 巴菲特指标 A 股本土化（<70% 深度低估，比美股下调 5-10%，
>   头条 2026-08）；② §4.3 补 Spring **0.5×ATR 失效边距**（FibAlgo 2026，收盘低于 Spring low 超
>   0.5×ATR→失效）+ 弱化"同日 low vs 跨日 close"过绝对定性（FibAlgo 2026 主流算法就用跨日 close，
>   非缺陷，真问题是缺 velocity/深度/失效边距）；③ §4.1 补 RSI<35 过滤器作可选第 4 维（ChartMath
>   2026 五因子）；④ 新增 §4.6 演进方向（AH-HMM 元体制门控/LVI 强平级联/滞回边沿触发器/ProRealCode
>   16 事件 FSM）；⑤ §6 开放问题补 ERP 绝对值/巴菲特字段勘探。
> - **0.4.2**（全网 2026-08-09 研究复审第三轮，补 v0.4.0/v0.4.1 未覆盖的 breadth thrust 实现/防过拟合/three_yang/fund/vix）：
>   ① **§4.4 breadth thrust 实现 bug 修正**——`was_washout=ema.shift(10)` 只看恰好−10 日违反 Zweig"10 日内"原意，改 `rolling().min().shift(1)`；
>   ② **§4.4 阈值本土化警告**——0.615 是美股 NYSE 值，A 股 924 上涨占比 96.97%，需 Step 0 校准（开放问题 9）；
>   ③ **§4.5 新增防过拟合方法论栈**——PBO/CSCV 在 N<10-12 不可用（archimedes #819 2026-06），改用事件研究法+预注册+DSR+CPCV；
>   ④ **§4.0 three_yang 改"需校准"+ 新增 §4.4b**——"连续 3 日上涨"过于宽松，2026 研究需实体/开盘/上影/量能/位置/失效 6 维量化；
>   ⑤ **§4.0 fund/vix 交叉工程项警告**——fund 成交量代理偏弱（2026：需融资余额+超大单）、vix≥40 偏美股标准（2026：A 股合成 VIX>25 即 8/8 胜率），跨 P1-E4/E7 处理（开放问题 10/11）。
> - **0.4.3**（全网 2026-08-09 研究复审第四轮，修 v0.4.2 名实不符 + 纳入 6 项新算法）：
>   ① **修 v0.4.2 名实不符**——v0.4.2 历程声称"新增 §4.4b/重写 §4.5/补 §6 开放问题 9-11"但正文未落地（第三次名实不符复发）。本次补全：新增 §4.4b three_yang 三源量化校准（6 维精确比例）、重写 §4.5 防过拟合方法论栈（事件研究法/预注册/DSR/CPCV/MinTRL/WFE + Neyt 开源引用）、补 §6 开放问题 9-11、补 §4.4 regime_detector 析取代码 diff + _TRANSITION_DIMS 注册步骤；
>   ② **§4.4b 红三兵精确比例**——2026 八源汇总（东方财富 2026-08-04/07-05、什么值得买 2026-06-17）给出比 v0.4.2"6 维定性"更可施工的量化比例：实体递增第三根≥第二根 1.5×、上影≤实体 5%、量能第三根≥前两根均量 2×、位置跌幅>30%+横盘>1 月、失效三根总涨幅>15%；
>   ③ **§4.5 防过拟合方法论栈**——PBO/CSCV 在 N<10-12 不可用（archimedes #819 2026-06），改用事件研究法 + 预注册 + DSR（Bailey & López de Prado 2014）+ CPCV（N=10,k=2→45 组合）+ MinTRL + WFE 验收标准（OOS/IS Sharpe≥0.6），参考 [Neyt/How-To-Backtest-Correctly](https://github.com/Neyt/How-To-Backtest-Correctly) 开源实现（2026-03）；
>   ④ **§4.6 演进方向补 EVR + flush**——EVR（量价背离/effort vs result，WyckoffTradingAgent 2026-05：量>1.6×+实体极小=主力暗中吸筹）+ flush（capitulation→spring 桥接信号，TradingSim 2026-05：末端暴跌+高量+收盘回区间+长下影）；
>   ⑤ **§4.3 ATR 止损过紧警告**——phuazz/breadth-thrust-etf 2026-08 实证 2×ATR 止损"actively destructive"，移除后 7 年回报 -1%→+110%，提示 spring 0.5×ATR 失效边距需 Step 0 敏感性测试。
> - **0.4.4**（2026-08-09 文档体系重排）：文件名 discussion_023_s2_algorithm_misalignment_diagnosis.md → 14_regime_s2_diagnosis.md（段位编号制）；doc_id 同步；depends_on/body 旧名引用全量更新为新名。新旧名对照见 00_index_trading_decision §10。

---

## 0. 背景：B4 S2 退回 FAIL(3/6) 触发的深挖

### 0.1 事件经过

| 时间 | 事件 |
|---|---|
| 2026-08-08（前序） | B4 修复门控跳过 + 验证器分母漏查 `data_ready` 后，S2 `data_ready=False` 不计分母，B4 PASS(3/3)，Phase 2 闭环 |
| 2026-08-08（后序） | 另一 session 以"数据管道已就绪（policy/bad_news_flat=NLP，wyckoff=engine，high/low 已加载）"为由，将 3 个 S2 事件 `data_ready` 从 `false` 改为 `true`（未提交） |
| 改动后 | S2 重新计入分母但 0/3 未命中，B4 退回 FAIL(3/6) |
| 本文档 | 运行诊断脚本 `scripts/tests/dump_s2_scores.py` dump 三事件日 ±10 交易日 S2 各维度评分，定位 0/3 根因 |

### 0.2 诊断方法

诊断脚本 [dump_s2_scores.py](file:///d:/ZephyrAlpha/scripts/tests/dump_s2_scores.py) 对三个 S2 复苏事件日（EVT-2015-RECOVERY=2015-09-15 / EVT-2020-RECOVERY=2020-04-10 / EVT-2024-RECOVERY=2024-09-24）±10 交易日，逐日 dump S2 的 12 个维度评分 + stage 判定，对比 [TRANSITION_CONFIG["S2"]](file:///d:/ZephyrAlpha/src/zephyr/regime/core/regime_detector.py#L195) 的阈值，判断是"分数不够"还是"维度恒缺"。

**核心发现**：3 个关键维度（capitulation / valuation / spring）在复苏事件日 ±10 窗口内**评分为 0 或近 0**，使 trigger/confirm/strong_confirm 三阶段全部无法满足。后续 commit 93a25890 的精确诊断进一步澄清（见 §1.2.1/§1.2.4）：capitulation 并非算法完全失效，而是**触发在窗口外**；wyckoff 是**设计域不匹配**而非"正常"。这不是阈值过高，而是**算法逻辑与时点/形态语义错配**。

### 0.3 已施工设施盘点（v0.5.0 新增，通用规则 #11）

> 盘点 S2 主题相关的全部已建设施（截至 2026-08-12 源码实证），明确"有什么"→"改什么"→"退役什么"。

**代码模块（src/zephyr/regime/）**：

| 设施 | 路径 | 状态 | 与 S2 的关系 |
|---|---|---|---|
| S2 四阶段阈值配置 | [regime_detector.py:195-207](file:///d:/ZephyrAlpha/src/zephyr/regime/core/regime_detector.py#L195) `TRANSITION_CONFIG["S2"]` | ✅ production | trigger/confirm/strong_confirm/fail 阈值真源，与 §1.1 设计表一致 |
| S2 维度注册表 | [overlay_signals_builder.py:89-102](file:///d:/ZephyrAlpha/src/zephyr/regime/overlay_signals_builder.py#L89) `_TRANSITION_DIMS["S2"]` | ✅ production | 12 个维度 key（无 breadth_thrust——P1-E9d 待施工） |
| S2 维度计算调用链 | [overlay_signals_builder.py:297-342](file:///d:/ZephyrAlpha/src/zephyr/regime/overlay_signals_builder.py#L297) | ✅ production | 12 维度评分调用 + `_compute_vix_pct` 合成 VIX 后备（commit eb3db21bd8） |
| 12 个 S2 维度评分函数 | [overlay_features.py](file:///d:/ZephyrAlpha/src/zephyr/regime/features/overlay_features.py)：s2_capitulation_score L192 / s2_vix_score L217 / s2_wyckoff_score L248 / s2_valuation_score L282 / s2_fund_score L306 / s2_spring_flag L328 / s2_three_yang_flag L346 / s2_break_sc_low_flag L358 / s2_vix_new_high_flag L369 / s2_fund_outflow_flag L380 / s2_policy_score L731 / s2_bad_news_flat_score L765 | ✅ production | capitulation/valuation/spring/three_yang 为当前实现（P1-E9 重设计对象）；policy/bad_news_flat 为 P1-E3 关键词 NLP（已激活非 stub） |
| 合成 VIX | [synthetic_vix.py](file:///d:/ZephyrAlpha/src/zephyr/regime/features/synthetic_vix.py) + `market_features.synthetic_vix_pct` | ✅ production（commit eb3db21bd8） | vix 维度数据前置，S1/S2 共用 |
| Wyckoff 6 阶段 FSM | [wyckoff_engine.py](file:///d:/ZephyrAlpha/src/zephyr/regime/features/wyckoff_engine.py) | ✅ production | s2_wyckoff_score 委托；Spring 事件接口达标度=P1-E9c Step 0 勘探项 |
| design_match 验证字段 | [b4_transition_accuracy.py](file:///d:/ZephyrAlpha/src/zephyr/regime/validation/phase2/b4_transition_accuracy.py) | ✅ production（commit 93a25890） | 区分"数据未就绪"（data_ready）与"设计域不符"（design_match） |

**诊断脚本 / 测试**：

| 设施 | 路径 | 状态 |
|---|---|---|
| S2 评分 dump 诊断 | [dump_s2_scores.py](file:///d:/ZephyrAlpha/scripts/tests/dump_s2_scores.py) | ✅ 已建（本文档诊断工具，P1-E9 验收复用） |
| S2 复苏诊断 | [diag_s2_recovery.py](file:///d:/ZephyrAlpha/scripts/tests/diag_s2_recovery.py) | ✅ 已建 |
| Overlay 构造器单测 | `tests/regime/test_overlay_signals_builder.py` | ✅ 29 测试全过（含合成 VIX 后备适配，commit 981d59d8cc） |
| 合成 VIX 单测 | `tests/regime/test_synthetic_vix.py` | ✅ 11 单测全过（commit eb3db21bd8） |
| P1-E9 TDD stub（5 个） | `tests/regime/features/test_s2_*.py` | ❌ 未建（§4.5 step 1，P1-E9 施工时先写 stub） |

**数据 / 治理登记**：

| 设施 | 路径 | 状态 |
|---|---|---|
| S2 事件定级 | [historical_events.yaml:59-100](file:///d:/ZephyrAlpha/src/zephyr/regime/validation/phase2/historical_events.yaml#L59) | ✅ data_ready=true + design_match=false（commit 93a25890） |
| ARCH 缺陷登记 | [architecture_issue_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) `#ARCH-REGIME-S2-ALGORITHM-001` | ✅ 已登记（status 三方不一致见 §6 开放问题 12） |
| P1-E9 工程项 | [13_regime_phase3_engineering_plan §3.5](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md) | ✅ 已登记（范围同步缺口见 §6 开放问题 13） |

**P1-E9 未施工清单**（grep 实证均不存在于代码，禁止误判为已建）：`s2_breadth_thrust_score` / `keys_or_gte` 析取字段 / `s2_valuation_score_fundamental`（CAPE 路 A）/ spring 深度分级与 velocity / three_yang 6 维分级 / capitulation 衰减加权与多过滤器 / `_atr` 辅助函数 / `c1_market.daily_valuation` 字段勘探。

---

## 1. 诊断报告：设计意图 vs 实现的语义错配

### 1.1 S2 设计源头（10_regime_detector_spec §4.12）

[10_regime_detector_spec §4.12](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/10_regime_detector_spec.md#L1525) 明确定义 S2 的语义与触发标准：

> **核心逻辑**：S2 是 CRISIS → RECOVERY 的转换，本质是"恐慌抛售**见底**→机构抄底→企稳复苏"。
> 与 T2（冰点→反核）同为"底部恢复"但起点不同——T2 从慢性阴跌的 Bear-Low 恢复，S2 从急性暴跌的 CRISIS 恢复。

[§4.12.8 触发标准汇总](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/10_regime_detector_spec.md#L1668)：

| 阶段 | 评分门槛 | P 更新 | Shrinkage |
|---|---|---|---|
| **S2 触发**（CRISIS→RECOVERY 预警） | Capitulation≥60 + VIX 回落≥40 + 利空钝化≥40 | P(RECOVERY)→40% | 0.3→0.4 |
| **S2 确认**（复苏确立） | Wyckoff 吸筹≥60 + 政策底≥40 + 估值极端≥40 + **资金承接≥50** | P(RECOVERY)→65% | 0.4→0.6 |
| **S2 强确认**（V 型反转） | 总分≥250（8 维度全达标）+ Spring Terminal Shakeout + 三根放量阳线 | P(RECOVERY)→80%+ | 0.6→0.7 |

设计意图的关键：**S2 衡量的是"危机见底→复苏"的转换时点**。在这个时点，恐慌抛售**已经过去**（属于 S1/CRISIS 阶段），企稳信号**正在出现**。因此各维度的评分逻辑应当衡量"近期曾出现 X"（过程信号）或"当前出现 Y"（企稳信号），而非"当日仍在 X"（危机信号）。

### 1.2 三维度错配详析

#### 1.2.1 capitulation（投降式抛售）——过程信号被实现为瞬时信号 ★ 核心缺陷

| 项 | 内容 |
|---|---|
| **设计意图**（[§4.12.1](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/10_regime_detector_spec.md#L1527)） | Capitulation 是"危机见底信号"，描述 **Phase 1-5 的过程**：慢性阴跌→杠杆清算级联→止损簇扫荡→长下影线→反弹与怀疑。底部在情绪恢复前形成（price leads narrative） |
| **实现**（[overlay_features.py:192-214](file:///d:/ZephyrAlpha/src/zephyr/regime/features/overlay_features.py#L192) `s2_capitulation_score`） | 当日 `z>1 ∧ pct_change<-1.5%` 分档给分（50/70/90），**瞬时信号无 rolling**。原 `z>2` 已于 2026-08-08 降至 `z>1`（持续高量期 z-score 被滚窗均值抬高、单日 z 被压低，z>2 经验性不可达）。仅 vol_z+pct_change 两维，无 ATR 实体/量能放大/下影线过滤 |
| **诊断实测** | 三事件日 ±10 交易日窗口内 capitulation **为 0**——但 commit 93a25890 精确诊断澄清：**并非算法完全失效，而是触发在窗口外**。2015 事件 capitulation 在 **08-24/25 底部触发，早于 09-15 事件日约 3 周**（见 [historical_events.yaml:82](file:///d:/ZephyrAlpha/src/zephyr/regime/validation/phase2/historical_events.yaml#L82) 注释），落在 B4 ±10 评估窗口外，故窗口内仍 0/3 |
| **错配本质** | 复苏事件日是企稳时点，当日不会出现"放量暴跌"。设计意图是"近期**曾**出现投降抛售"（过程），实现是"当日**正在**投降抛售"（瞬时）。S2 触发要求 capitulation≥60，但复苏时点 capitulation 必然为 0 → trigger 永不触发。**窗口外触发反而印证了 §4.1 衰减加权和的必要性**：把 08-25 的 capitulation 信号衰减带到 09-15 |

**结论**：capitulation 评分丢失了"过程"语义。正确的实现应衡量"近期曾出现投降抛售"且**信号随时间衰减**（非持续粘滞），而非当日值；且单日判定应从两维升级为多维度共振（见 §4.1）。

#### 1.2.2 valuation（估值极端）——基本面信号被实现为价格回撤信号

| 项 | 内容 |
|---|---|
| **设计意图**（[§4.12.5](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/10_regime_detector_spec.md#L1618)） | 估值和破净率是底部最硬的客观证据：沪深300 PE<15、全市场 PE<16、破净率>10%、风险溢价>95%分位、巴菲特指标<80% |
| **实现**（[overlay_features.py:282-303](file:///d:/ZephyrAlpha/src/zephyr/regime/features/overlay_features.py#L282) `s2_valuation_score`） | `close/rolling_max(250, min_periods=20)`，分档 `pos<0.60→20 / <0.50→40 / <0.40→60 / <0.30→80`——用价格回撤代理估值 |
| **诊断实测** | 三事件日 valuation **远未达 confirm 门槛 40**（实测见 dump_s2_scores.py；2020/2024 复苏 pos≈0.90 落 0 分档，2015 pos≈0.58 仅落 20 分档） |
| **错配本质** | 价格回撤 ≠ 估值。2020/2024 复苏距高点仅 -10%（pos≈0.90），但 PE 历史分位可能已在低估区——价格回撤捕捉不到"价格没跌但估值分位已低"。设计意图是基本面估值（PE/破净率历史分位），实现是价格回撤，且阈值偏严，不适用于非腰斩级复苏 |

**结论**：valuation 应用真正的基本面估值。**注意陷阱**（§4.2 路 A 详述）：S2 正是危机场景，危机期盈利 E 崩塌会令 PE_TTM"越跌越贵"失真，须用 CAPE（席勒 PE）或 PB 分位而非 PE_TTM 分位。13_regime_phase3_engineering_plan §6.2 已提及 `c1_market.daily_valuation`（日度估值表），数据源可获取。

#### 1.2.3 spring（弹簧信号）——close 跨日简化，时点错位

| 项 | 内容 |
|---|---|
| **设计意图**（[§4.12.2](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/10_regime_detector_spec.md#L1553)） | Wyckoff Spring 震仓——跌破支撑诱空+快速收回+清洗止损=最经典底部信号。需 high/low 判断 |
| **实现**（[overlay_features.py:328-343](file:///d:/ZephyrAlpha/src/zephyr/regime/features/overlay_features.py#L328) `s2_spring_flag`） | 用 close **跨日**简化判断（无 low）：`前日 close 跌破前低 ∧ 当日 close 收回`。这与真正 Spring"**同日** low 跌破支撑 + 当日 close 收回"语义**时点错位**（非"逻辑较严"）——它要求两日配合（前日破+当日收），而真 Spring 是单日完成（日内 low 破支撑+收盘收回） |
| **诊断实测** | 偶尔触发（1.0），如 2015-08-28、2024-09-06/11/19/23-30 |
| **错配本质** | spring 本身能触发，但 strong_confirm 要求 total≥250 ∧ spring≥1 ∧ three_yang≥1，总分不够（capitulation/valuation 恒 0 拖累 total）。Phase 2c 已激活 high/low，spring 应复用 wyckoff_engine 的 Spring 事件（已在 [s2_wyckoff_score](file:///d:/ZephyrAlpha/src/zephyr/regime/features/overlay_features.py#L248) 中识别），避免重复逻辑 |

#### 1.2.4 P0 bug 修复与 design_match 定级（commit 93a25890 落地记录）

诊断后落地两层处置（[commit 93a25890](file:///d:/ZephyrAlpha/src/zephyr/regime/features/overlay_features.py) "fix(regime): S2 复苏检测 bug 修复 + design_match 设计域定级"）：

1. **两个经验性 bug 修复（治标）**：
   - `s2_capitulation_score`：vol_z 阈值 `z>2 → z>1`（持续高量危机期 z-score 被滚窗均值抬高，实测 2015 股灾期 max=1.79 结构性不可达；修复后全局 cap≥60 仅 0.6%，选择性足够）。**治标**——降阈值让 capitulation 能触发，但未解决"过程语义缺失"（§4.1 治本）。
   - `s2_valuation_score`：`rolling(250).max()` 加 `min_periods=20`（000300 数据起点晚于 data_load_start，2015 年 rolling 不足 250 非 NaN → warmup 误零）。**治标**——修 warmup 误零，但未解决"价格回撤≠基本面估值"（§4.2 治本）。
2. **design_match 字段定级（设计域排除）**：[b4_transition_accuracy.py](file:///d:/ZephyrAlpha/src/zephyr/regime/validation/phase2/b4_transition_accuracy.py) 新增 `design_match` 字段——数据已就绪但事件类型超出当前模型设计域时排除出 B4 分母（区别于 `data_ready`）。3 个 S2 事件标 `design_match: false`，理由（[yaml:82/91/100](file:///d:/ZephyrAlpha/src/zephyr/regime/validation/phase2/historical_events.yaml#L82)）：
   - 2015：capitulation 在 08-24/25 底部触发，早于 09-15 事件日 3 周（窗口外）
   - 2020：V 型反转不走 Wyckoff 吸筹，valuation/wyckoff 合法不达标
   - 2024：政策驱动 V 反转不走 Wyckoff 吸筹，bad_news_flat/capitulation 不达标

**关键**：`data_ready` 维持 **true**（数据确已就绪），问题在设计域而非数据。B4 当前 = S1 3/3 = PASS，S2 被 design_match 排除不计分母。

### 1.3 trigger/confirm/strong_confirm 三阶段全堵死

[TRANSITION_CONFIG["S2"]](file:///d:/ZephyrAlpha/src/zephyr/regime/core/regime_detector.py#L195) 的阈值，叠加诊断实测：

| 阶段 | 阈值（AND 逻辑） | 实测瓶颈 | 结果 |
|---|---|---|---|
| **trigger** | capitulation≥60 ∧ vix≥40 ∧ bad_news_flat≥40 | capitulation 窗口外触发（vix 0-60 / bad_news_flat 80 均可满足） | **窗口内永不触发** |
| **confirm** | wyckoff≥60 ∧ policy≥40 ∧ valuation≥40 ∧ fund≥50 | valuation 远未达 40 + wyckoff 偏低(10-40) + **2020/2024 V 反转不走吸筹致 wyckoff 设计域不匹配**（policy 80 / fund 0-70 可满足） | **永不触发** |
| **strong_confirm** | total≥250 ∧ spring≥1 ∧ three_yang≥1 | total 不够（capitulation/valuation 恒 0 拖累） | **永不触发** |

> **关键洞察**：NLP 维度（bad_news_flat=80 / policy=80）评分正常，证明 P1-E3 NLP 管道 + P1-E6 bad_news_flat 已生效。S2 不触发的根因不在 NLP 数据，而在 capitulation/valuation 的算法逻辑 + **wyckoff 吸筹模板对 V/政策型复苏的设计域不匹配**。这意味着 13_regime_phase3_engineering_plan 现有 P1-E3/E6/E7（数据激活）即使全部完成，S2 仍会 0/3——因为算法缺陷不在这些工程项范围内。

### 1.4 "数据就绪"≠"算法正确"——data_ready 字段的语义陷阱

[HistoricalEvent.data_ready](file:///d:/ZephyrAlpha/src/zephyr/regime/validation/phase2/b4_transition_accuracy.py#L103) docstring：

> 触发条件所需**维度数据**是否就绪（S2 需 NLP+high/low，未就绪=False，不计 B4 分母）

另一 session 改 `data_ready=true` 的理由（"数据管道已就绪"）在**数据层面**成立，但诊断证明：**数据就绪后 S2 仍 0/3**，根因是算法逻辑错配 + 设计域不匹配。`data_ready` 语义无法表达"算法是否有缺陷"或"事件形态是否在设计域内"——commit 93a25890 新增 `design_match` 正补此缺口：承认"数据就绪 ∧ 设计域匹配 ⇒ 可验证"。

**100% AI 开发下的典型风险**（与 project_memory #ARCH-TEMP-FILE-PLACEMENT-001 教训同类）：AI 看到"NLP/high/low 已激活"就推断"数据已就绪 → S2 可验证"，未查证算法正确性与事件形态匹配度——"看似合理的推断替代应查证的惯例"，100% AI 开发下尤须警惕。

---

## 2. 架构裁定

### 2.1 三条路的取舍

面对 B4 FAIL(3/6)，有三条路：

| 路 | 内容 | 优点 | 缺点/风险 |
|---|---|---|---|
| **路 1** | 回退 `data_ready=false`，B4 回 PASS(3/3)，Phase 2 闭环；S2 算法重设计作为 P1 工程项后续做 | Phase 2 立即闭环；守住验证独立性 | `data_ready=false` 语义不准（数据已就绪，谎报未就绪）；掩盖"设计域不匹配" |
| **路 2** | 立即修复 S2 算法（capitulation 过程化 + valuation 放宽），重跑 B4 | 治本，S2 真正可验证 | 在 Phase 2 验证中"为过 B4 而改算法"，陷入调参过拟合历史事件 |
| **路 3**（**采纳**） | `design_match=false` 排除 S2 出 B4 分母（数据 ready 维持 true，诚实记录"设计域不匹配"）+ 修两个 P0 治标 bug + P1-E9 治本 | 语义诚实（区分数据/设计域）；Phase 2 立即闭环；守住验证独立性；缺陷登记不遗忘 | 需新增 design_match 字段（b4_transition_accuracy.py 改动） |

### 2.2 第一性原理：验证器不能驱动算法设计

B4 验证的目的是"客观验证检测器触发时点是否吻合历史"（[b4_transition_accuracy.py docstring](file:///d:/ZephyrAlpha/src/zephyr/regime/validation/phase2/b4_transition_accuracy.py#L17)）。为过 B4 而改算法 = **自我证明（circular validation）**——改算法让验证通过、验证通过证明算法正确，逻辑循环，验证失去独立性。

验证结果可以**暴露**缺陷（B4 FAIL 暴露了 S2 算法问题），但不能**驱动**算法设计（不能"调参直到 3/3 命中"）；算法重设计必须回归 §4.12 设计源头重新对齐语义，独立于验证结果进行。

### 2.3 长远战略：算法重设计是 P1 工程，不应在 P0 验证中草率完成

S2 算法重设计涉及评分逻辑的**语义重新定义**：
- capitulation：瞬时 → 过程（衰减加权和）+ 单日判定多维度化
- valuation：价格回撤 → 基本面估值（CAPE/PB 历史分位）或阈值校准
- spring：close 跨日简化 → 复用 wyckoff_engine（同日 low 判定）+ 深度分级
- **V 反转通路（v0.4.0 新增）**：confirm 的 wyckoff≥60 对 V/政策型复苏设计域不匹配，需开 breadth thrust 析取通路

这需要回归 §4.12.1/§4.12.5/§4.12.2 设计源头重新对齐，重设计后重跑 B4 验证，并防止"调参过拟合 3 个历史事件"——P1 级工程，应在 Phase 3 系统性完成，不在 Phase 2 P0 验证中"为了让 B4 过"而草率改算法。

### 2.4 100% AI 开发：隔离问题 → 登记缺陷 → 系统性修复

100% AI 开发下，"为过验证而改算法"的诱惑更强（AI 倾向于"让指标通过"）。正确做法三步走：

1. **隔离**：`design_match=false` 准确反映"S2 当前设计域不匹配"（数据已就绪，问题在算法/形态），B4 回 PASS(3/3)，Phase 2 闭环
2. **登记**：ARCH 条目记录缺陷（诊断证据 + 设计意图 vs 实现差异 + 设计域不匹配），防止 AI session 间遗忘
3. **系统性修复**：P1-E9 工程项，有设计审查和验证闭环，独立于 B4 结果进行

### 2.5 裁定结论

**采纳路 3**（design_match 排除 + P0 治标 + P1 治本，**非**路 1 的 data_ready 回退）：

- **已落地（commit 93a25890）**：3 个 S2 事件 `design_match: false`（data_ready 维持 true）；修 capitulation z>1 + valuation min_periods=20 两个 P0 治标 bug；B4 回 PASS(3/3)，Phase 2 闭环
- **已落地**：登记 `#ARCH-REGIME-S2-ALGORITHM-001`，记录 S2 算法时点错配 + 设计域不匹配缺陷
- **已落地**：13_regime_phase3_engineering_plan 新增 P1-E9 工程项（§3.5），引用本文档
- **P1 阶段**：P1-E9 算法重设计（capitulation 过程化 + valuation 基本面化 + spring 深度分级 + **V 反转通路**）→ 重跑验证 → S2 激活（design_match 改 true）
- **`design_match` 语义**：从"维度数据是否就绪"（data_ready）扩展出"事件形态是否在当前模型设计域内"（design_match），两字段正交。S2 注释更新为"评分算法有时点错配 + V 反转设计域不匹配缺陷，待 P1-E9 重设计后激活"

**核心理由**：不为过 B4 而改算法（守住验证独立性），但绝不掩盖缺陷（design_match 诚实标注 + ARCH 登记 + P1 工程项治本），且不谎报数据未就绪（data_ready 维持 true）。

---

## 3. P0 已落地记录（commit 93a25890）

> v0.3.1 裁定已实施，本节为落地记录（past tense），非待施工步骤。

### 3.1 步骤 1（已落地）：design_match 定级，Phase 2 闭环

**文件**：[historical_events.yaml:59-100](file:///d:/ZephyrAlpha/src/zephyr/regime/validation/phase2/historical_events.yaml#L59)

**改动**（commit 93a25890）：
- 3 个 S2 事件（EVT-2015/2020/2024-RECOVERY）`data_ready` 维持 **true**，新增 `design_match: false`
- 顶部注释更新：

```yaml
  # data_ready: true —— NLP(policy/bad_news_flat)+high/low(wyckoff) 数据管道 2026-08-08 已就绪
  # design_match: false —— S2 Wyckoff 吸筹模板与 A 股复苏模式不符，2026-08-08 实证 0/3：
  #   2015: capitulation 在 08-24/25 底部触发，早于 09-15 事件日 3 周（窗口外）
  #   2020: V 型反转不走 Wyckoff 吸筹，valuation/wyckoff 合法不达标
  #   2024: 政策驱动 V 反转不走 Wyckoff 吸筹，bad_news_flat/capitulation 不达标
  #   S2 待重设计（加政策/V 反转信号）后激活（见 14_regime_s2_diagnosis §4.4）
```

**效果**：S2 被 design_match 排除不计 B4 分母，B4 = S1 3/3 = PASS，Phase 2 闭环（A1/A2/B1/B4 全 PASS）。

### 3.2 步骤 2（已落地）：登记 #ARCH-REGIME-S2-ALGORITHM-001

**文件**：[architecture_issue_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml#L12464)

**条目** `#ARCH-REGIME-S2-ALGORITHM-001`：
- title: S2 评分算法时点错配 + V 反转设计域不匹配——capitulation 当日值 vs 过程 / valuation 价格回撤 vs 基本面 / wyckoff 吸筹 vs V 反转
- severity: P1中
- category: governance
- adjudication: 记录诊断证据（三事件 capitulation 窗口外触发/valuation 不达标/wyckoff 设计域不匹配）、设计意图 vs 实现差异、裁定结论（design_match=false 排除 + P0 治标 + P1-E9 治本）
- impact: overlay_features.py（s2_capitulation_score/s2_valuation_score/s2_spring_flag）、b4_transition_accuracy.py（design_match 字段）、historical_events.yaml（design_match 定级）、14_regime_s2_diagnosis（诊断详档）
- fix_phase: 待 P1-E9 算法重设计完成
- status: proposed（铁律#9：调参决策类 AI 提议，待用户确认）
- 修订 `#ARCH-REGIME-OVERLAY-001` 的 fix_phase：承认"B4 闭环"是基于 `design_match=false`，S2 算法缺陷未治本，见 `#ARCH-REGIME-S2-ALGORITHM-001`

### 3.3 步骤 3（已落地）：13_regime_phase3_engineering_plan 新增 P1-E9

**文件**：[13_regime_phase3_engineering_plan §3.5](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md)

新增 §3.5 P1-E9: S2 评分算法重设计（~120 行），引用本文档作为诊断详档。同时在 §1.1 工程清单加一行 P1-E9。

---

## 4. P1-E9 算法重设计详设

### 4.0 治本范围边界

P1-E9 覆盖诊断确认有"时点/形态错配"的四个维度（v0.4.0 扩入 V 反转通路），其余维度的归属明确如下，避免施工者误改全 12 维度：

| 维度 | 现状 | P1-E9 是否处理 | 归属 |
|---|---|---|---|
| capitulation | 瞬时信号，过程语义缺失（窗口外触发） | ✅ 是（§4.1） | P1-E9a |
| valuation | 价格回撤代理，基本面语义缺失 | ✅ 是（§4.2） | P1-E9b |
| spring | close 跨日简化，时点错位 | ✅ 是（§4.3） | P1-E9c |
| **confirm 通路（V 反转）** | wyckoff≥60 对 V/政策型复苏设计域不匹配 | ✅ 是（§4.4，**v0.4.0 新增**） | P1-E9d |
| fund | MVP（成交量代理资金），confirm 门槛 50 | ⚠️ 不处理但警告依赖项（见下注 + §6 开放问题 10） | P1-E4 资金/板块数据激活 |
| three_yang | "连续 3 日上涨"实现过于宽松（无实体/开盘/上影/量能/位置/失效要求） | ✅ 是（§4.4b，**v0.4.3 新增**） | P1-E9e |
| vix / bad_news_flat / policy | 诊断已确认正常（但 **vix≥40 门槛可能偏美股标准**，见下注） | ⚠️ 不处理但警告依赖项（vix 门槛校准跨 P1-E7，见 §6 开放问题 11） | P1-E3/E6/E7 |
| wyckoff（吸筹模板本身） | **设计域不匹配 V 反转**（非"诊断正常"，见 §1.2.4/§1.3） | ⚠️ 不改 wyckoff 本身，而是开 breadth thrust 析取通路绕过（§4.4） | §4.4 |

> **v0.4.2 跨工程项警告（fund/vix，2026 研究）**：
> - **fund（成交量代理偏弱）**：2026 研究（慧眼财经/华夏时报/东方财富）实证成交量不区分方向（散户接盘式上涨持续性差）、无法识别资金性质（配置型 vs 交易型北向）、缺乏"出清"语义（融资余额低点=出清，两融参与者占比 4% 见底）。924 是"主力净流入 209.85 亿 + 融资余额攀升 + 成交量量级跃升"三者共振，单看成交量无法复现。**P1-E4 应升级 fund 为"融资余额变化分位 + 超大单净流入分位 + 成交量分位"加权**（非 P1-E9 范围，但 confirm≥50 依赖此，见开放问题 10）。
> - **vix（≥40 门槛可能偏高）**：2026 研究（雪球淡定菌/浙商廖静池）实证 A 股合成 VIX>25 即触发 8/8 胜率信号（沪深300 期权 CBOE 方差互换法），vix≥40 是美股 3-sigma 标准（数年一遇）对沪深300 偏高。2026-07 大跌沪深300 期权隐波仅升至 23-28%。**P1-E7 应校准 vix 门槛**：若用沪深300 合成 VIX 降至 ≥25-30；或改"IV 近 89 日分位≥80% + 价格布林下轨"（浙商方案，胜率 75-86%）。实现波动率分位是后视镜，无法捕捉 924 这类政策脉冲拐点——需期权隐含 VIX 互补（非 P1-E9 范围，见开放问题 11）。

> **关键**：P1-E9 修好 capitulation/valuation 后，total 分提升，但 **confirm 仍卡 wyckoff≥60**——2020/2024 V 反转不走吸筹，wyckoff 合法不达标（[yaml:91/100](file:///d:/ZephyrAlpha/src/zephyr/regime/validation/phase2/historical_events.yaml#L91)）。这是 commit 93a25890 明示"S2 待重设计（加政策/V 反转信号）"的根因。**§4.4 V 反转通路是 P1-E9 能否让 confirm 触发的关键**，不解决则修完三维度 confirm 仍不触发。另：strong_confirm 仍需 spring≥1 ∧ three_yang≥1（**three_yang 需 §4.4b 校准**），confirm 仍需 fund≥50（**fund 需 P1-E4 升级**，见上注 + §6 开放问题 6/10）。

> **施工顺序**（关键路径，v0.4.0 补 TDD-first + Step 0 勘探门禁，v0.4.3 补勘探脚本）：
> 1. **Step 0（勘探门禁，禁止跳过）**：先勘探 ① `c1_market.daily_valuation` 是否含 CAPE/PB/破净率/ERP 字段（§4.2 路 A 前置）② wyckoff_engine 是否暴露 Spring 事件 flag + 是否满足 §4.3 四要素（§4.3 前置）③ A 股涨跌家数/创新低占比数据可得性（§4.4 breadth thrust 前置）④ 50ETF/300ETF 期权 put/call 数据可得性（§4.1 capitulation 第 5/6 维前置）。任一阻断则先建数据管道，**禁止带着假设平铺施工**。
>
> **勘探脚本（v0.4.3 补，复制即用）**：
> ```bash
> # ① daily_valuation 字段勘探（ClickHouse）
> python -c "
> from zephyr.data.clickhouse_client import query
> print(query('DESCRIBE TABLE c1_market.daily_valuation').to_string())
> print(query(\"SELECT toDate(min(trade_date)), toDate(max(trade_date)), count() FROM c1_market.daily_valuation\").to_string())
> # 关键字段: cape_5y_percentile / pb_percentile / broken_net_ratio / erp / erp_percentile / buffett_ratio / pe_ttm_percentile
> "
>
> # ② wyckoff_engine Spring 接口勘探（源码审查）
> python -c "
> import inspect
> from zephyr.regime.features import wyckoff_engine
> src = inspect.getsource(wyckoff_engine)
> # 查找: def wyckoff_score / Spring / spring / events / phase
> for kw in ['def ', 'spring', 'Spring', 'event', 'phase', 'SPRING']:
>     for i, line in enumerate(src.splitlines(), 1):
>         if kw in line: print(f'{i}: {line}')
> "
>
> # ③ 涨跌家数/创新低数据勘探（feature_builder 透传方法）
> python -c "
> from zephyr.regime.regime_feature_builder import RegimeFeatureBuilder
> fb = RegimeFeatureBuilder(backtest_start='2015-01-01', backtest_end='2026-06-30', data_load_start='2010-01-01')
> for m in ['get_advance_decline', 'get_new_high_low', 'get_market_breadth']:
>     fn = getattr(fb, m, None)
>     print(f'{m}: {\"存在\" if fn else \"缺失\"}')
>     if fn:
>         df = fn(); print(f'  shape={df.shape}, cols={list(df.columns)[:10]}, range={df.index.min()}~{df.index.max()}')
> "
>
> # ④ 期权 put/call 数据勘探
> python -c "
> from zephyr.regime.regime_feature_builder import RegimeFeatureBuilder
> fb = RegimeFeatureBuilder(backtest_start='2015-01-01', backtest_end='2026-06-30', data_load_start='2010-01-01')
> for m in ['get_option_iv_surface', 'get_option_put_call_ratio']:
>     fn = getattr(fb, m, None)
>     print(f'{m}: {\"存在\" if fn else \"缺失\"}')
> "
> ```
> 任一脚本输出"缺失"或字段不存在 → 该维度降级或先建管道，**禁止带着假设平铺施工**。
>
> 2. **TDD-first**（项目惯例：corrected algorithms 先写 unit test stub 再写主码，见 §4.5 step 1）——每个维度先写 stub 验证设计意图，再写实现。
> 3. **§4.3 spring 的 wyckoff_engine 达标审查**（依赖链最长，是前置依赖）→ 若不达标需先补 wyckoff_engine。
> 4. **§4.1 capitulation + §4.2 valuation + §4.4 breadth thrust + §4.4b three_yang**（可并行，均依赖 Step 0 勘探结果）。
> 5. **§4.5 验证闭环**（最后）。

### 4.1 P1-E9a: capitulation 过程化（衰减加权）+ 多维度升级

**现状**（[overlay_features.py:192-214](file:///d:/ZephyrAlpha/src/zephyr/regime/features/overlay_features.py#L192) `s2_capitulation_score`）：当日 `z>1 ∧ pct_change<-1.5%` 分档给分（50/70/90），瞬时信号无 rolling。仅 vol_z+pct_change 两维，无 ATR 实体/量能放大/下影线过滤。**调用方**（[overlay_signals_builder.py:300](file:///d:/ZephyrAlpha/src/zephyr/regime/overlay_signals_builder.py#L300)）当前仅 `s2_capitulation_score(vol_z, pct_change)` 传 2 参数，且在 `vol_z/pct_change` 检查块内调用（未含 close/high/low/volume 检查）。

**三层升级**：

1. **单日判定多维度化**（参考 ChartMath 2026 capitulation 四过滤器法 + JournalPlus 2026 四信号 confluence）：原仅 vol_z+pct_change 两维，单阈值易被噪声触发。叠加三道过滤器：
   - 量能放大：当日量 > **2.0×20 日均量**（确认 panic/forced liquidation）。**v0.4.0 校准**：原 1.3× 偏松，2026 多源（quantscanai 3×、JournalPlus 2–5×、Pomegra 2–3×）一致表明真 capitulation 量能 2–3× 均量，校准为 2.0×（取研究下限留 selective 余地）。
   - 实体力度：当日实体 `|close-open|` > 40% ATR(14)。**v0.4.0 修正**：项目 K 线**有 open 字段**，直接用真实体（非 close-to-close 近似）。
   - **下影线过滤器（v0.4.0 新增）**：§4.12.1 Phase 4 明列"长下影线"，JournalPlus 2026/Wyckoff Analytics 均列为 capitulation 核心标志。量化：`wick_ratio = (min(open,close)-low)/(high-low) > 0.5`（下影线占 K 线过半=卖盘被吸收）。
   仅当量价基础分 + 三道过滤器同时满足才给分（多维度共振区分"真投降"与"普通下跌"）。
   - **RSI<35 过滤器（v0.4.1 可选第 4 维，ChartMath 2026 五因子）**：RSI(14)<35 + 收盘低于布林下轨(20,2) 作**可选增强**——实测三过滤器噪声仍大时再启用。**默认不启用**，避免交集过严致 capitulation 永不触发（§4.5 数值边界：单日本就需簇集才达 60）。

2. **过程化 = 衰减加权和**（替代 rolling max，参考 ArrowAlgo Decay Block 2026 / Pomegra signal half-life 2026 / MathAndMarkets 2026）：
   - **为何不用 rolling max**：rolling(lookback).max() 一旦窗口内某日 capitulation=90，之后 lookback 日每天=90 → trigger 持续满足，**状态粘滞**；S2 是一次性转换事件，不应持续（dredyson 2026 regime 状态机"锁死"bug 同类）。
   - **衰减加权**：近期权重高，远期 e^(-i/τ) 衰减，τ=halflife/0.693。保留"过程"语义且信号自然消退（mean reversion 典型 half-life 5-20 天，取 halflife=10）。
   - **数值边界（v0.4.0 补，施工必读）**：halflife=10、lookback=20 时 w₀≈0.13 → 单日 90 分仅贡献 ~12 分，**单日不足以触发 trigger≥60**——设计意图是 trigger 要求**多日 capitulation 簇集**（2-3 日 70-90 分簇集可达 60+）。若簇集后仍不达 60，应扩 lookback 或放 halflife（§4.5 step 5 约束下），**禁止**直接降阈值凑分。

3. **ATR 自实现**（项目无现成）：`src/zephyr/regime` 下无 `def _atr`/`AverageTrueRange`，需自带。**v0.4.3 补放置位置**：`overlay_features.py` 顶部模块级私有函数（前缀 `_` 标内部），紧邻 `s2_capitulation_score` 上方。**理由**：① 仅 overlay_features 内 S2 维度用（spring 失效边距也用，§4.3）；② 未来 T1/T5 需 ATR 再提升到 `zephyr/regime/features/_indicators.py`（当前 YAGNI）；③ 私有前缀防外部误依赖。

```python
def _atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    """ATR(14)——项目无现成实现，P1-E9a 自带。

    True Range = max(high-low, |high-prev_close|, |low-prev_close|)，
    ATR = TR 的 Wilder 平滑（等价 EMA with alpha=1/window）。
    """
    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low).abs(),
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1.0 / window, adjust=False).mean()


def s2_capitulation_score(
    vol_z: pd.Series, pct_change: pd.Series,
    volume: pd.Series, high: pd.Series, low: pd.Series,
    open: pd.Series, close: pd.Series,          # v0.4.0: open 用于真实体 + 下影线
    put_call_ratio: pd.Series | None = None,    # v0.4.3: JournalPlus 第 5 维（期权 put/call）
    new_low_ratio: pd.Series | None = None,     # v0.4.3: JournalPlus 第 6 维（创新低占比）
    lookback: int = 20, halflife: int = 10, atr_window: int = 14,
    vol_mult: float = 2.0,                       # v0.4.0: 1.3→2.0（研究下限）
    enable_options_filter: bool = False,         # v0.4.3: 默认关，Step 0 ④ 得数据后开
) -> pd.Series:
    """S2 capitulation: 近 N 日 capitulation 的衰减加权和（过程信号，防粘滞）。

    设计意图（§4.12.1）：Capitulation 是危机见底的【过程】信号——
    Phase 1-5（慢性阴跌→杠杆清算→止损簇→长下影线→反弹）。
    复苏事件日是企稳时点，当日不会暴跌，故衡量"近期曾出现投降抛售"。
    诊断（commit 93a25890）：2015 capitulation 在 08-24/25 触发，早于 09-15 事件日 3 周
    （窗口外）→ 衰减加权和把窗口外信号带到事件日。

    三层升级：
    1. _capitulation_daily 多维度共振（ChartMath 2026 + JournalPlus 2026：量价+量2.0×+实体40%ATR+下影线>50%）
       v0.4.3 补 JournalPlus 四信号 confluence 第 5/6 维（可选）：put/call>1.4 + 新低占比>90%
    2. 衰减加权和替代 rolling max（ArrowAlgo/Pomegra/MathAndMarkets 2026 signal decay）：
       rolling max 致单日高分持续 lookback 日→状态粘滞（S2 是一次性转换不应持续）。
       衰减加权：近期权重高，远期 e^(-i/τ) 衰减，τ=halflife/0.693。
       数值边界：单日 90 分仅贡献 ~12 分（w₀≈0.13），trigger≥60 需多日簇集（设计意图）。
    """
    daily = _capitulation_daily(
        vol_z, pct_change, volume, high, low, open, close,
        atr_window, vol_mult,
        put_call_ratio, new_low_ratio, enable_options_filter,
    )
    weights = np.exp(-np.arange(lookback) / (halflife / 0.693))
    weights = weights / weights.sum()
    return daily.rolling(lookback).apply(lambda w: (w * weights).sum(), raw=True)


def _capitulation_daily(
    vol_z: pd.Series, pct_change: pd.Series,
    volume: pd.Series, high: pd.Series, low: pd.Series,
    open: pd.Series, close: pd.Series,
    atr_window: int = 14, vol_mult: float = 2.0,
    put_call_ratio: pd.Series | None = None,     # v0.4.3: JournalPlus 第 5 维
    new_low_ratio: pd.Series | None = None,      # v0.4.3: JournalPlus 第 6 维
    enable_options_filter: bool = False,
) -> pd.Series:
    """单日 capitulation 评分（多维度共振，原两维升级版）。

    原逻辑（overlay_features.py:192-214）：z>1 ∧ pct<-1.5% 分档 50/70/90。
    叠加 ChartMath 2026 + JournalPlus 2026 三道过滤器，仅共振时给分：
      - 量能放大：当日量 > vol_mult×20 日均量（v0.4.0: 1.3→2.0）
      - 实体力度：|close-open| > 40% ATR(14)（v0.4.0: 用 open 真实体，非 close-prev_close 近似）
      - 下影线（v0.4.0 新增）：下影线占 K 线 >50%（买盘吸收信号，§4.12.1 Phase 4）
    v0.4.3 JournalPlus 四信号 confluence（可选，enable_options_filter=True 且数据就绪时启用）：
      - put/call ratio > 1.4（期权市场恐慌对冲需求，JournalPlus 2026）
      - breadth collapse：新低占比 > 90%（>90% 股票创 52 周新低， indiscriminate selling）
    默认关闭——三过滤器已 selective 足够（§4.5 数值边界），四/六过滤器交集过严致 capitulation 永不触发。
    仅当 Step 0 ④ 期权 put/call + 新低数据可得 + 实测三过滤器噪声大时启用。
    """
    z = vol_z.fillna(0.0)
    pct = pct_change.fillna(0.0)
    base = pd.Series(0.0, index=vol_z.index)
    base[(z > 1) & (pct < -0.015)] = 50
    base[(z > 1) & (pct < -0.03)] = 70
    base[(z > 3) & (pct < -0.04)] = 90
    # 三道过滤器
    vol_surge = volume > volume.rolling(20).mean() * vol_mult
    atr = _atr(high, low, close, atr_window)
    body = (close - open).abs()                       # 真实体（v0.4.0）
    big_body = body > atr * 0.4
    lower_wick = np.minimum(open, close) - low        # 下影线（v0.4.0 新增）
    wick_ratio = lower_wick / (high - low + 1e-8)
    strong_wick = wick_ratio > 0.5
    mask = vol_surge & big_body & strong_wick
    # v0.4.3: JournalPlus 四信号 confluence（可选第 5/6 维）
    if enable_options_filter:
        if put_call_ratio is not None:
            mask = mask & (put_call_ratio.fillna(0.0) > 1.4)
        if new_low_ratio is not None:
            mask = mask & (new_low_ratio.fillna(0.0) > 0.90)
    return base.where(mask, 0.0)
```

**调用链改造**（[overlay_signals_builder.py:299-300](file:///d:/ZephyrAlpha/src/zephyr/regime/overlay_signals_builder.py#L299)）：签名从 2 参数扩到 7+ 参数（含 open），调用点须迁移。**v0.4.3 补 before/after 代码 diff**：

```python
# ── BEFORE（overlay_signals_builder.py:299-300，当前实现）──
        if vol_z is not None and pct_change is not None:
            cache["capitulation"] = overlay_features.s2_capitulation_score(vol_z, pct_change)
        else:
            _logger.warning("S2 capitulation 数据缺失，降级 0.0")

# ── AFTER（v0.4.3，迁移到 close 块，扩 7 参数）──
        # 移除原 vol_z/pct_change 块的 capitulation 调用
        if (
            vol_z is not None and pct_change is not None
            and close is not None and high is not None and low is not None
            and volume is not None
            and "open" in proxy  # open 需从 proxy 取（见下注）
        ):
            open_ = proxy["open"].astype(float).reindex(feat.index)
            # v0.4.3: 期权 put/call + 新低占比（Step 0 ④ 得数据后注入，默认 None）
            pc_ratio = self._fb_call("get_option_put_call_ratio")
            nl_ratio = self._fb_call("get_new_low_ratio")
            enable_opt = pc_ratio is not None and nl_ratio is not None
            cache["capitulation"] = overlay_features.s2_capitulation_score(
                vol_z, pct_change, volume, high, low, open_, close,
                put_call_ratio=pc_ratio.reindex(feat.index) if pc_ratio is not None else None,
                new_low_ratio=nl_ratio.reindex(feat.index) if nl_ratio is not None else None,
                enable_options_filter=enable_opt,
            )
        elif vol_z is not None and pct_change is not None:
            # 降级：缺 open/high/low/volume 时回退 2 参数（治标 z>1，与 commit 93a25890 一致）
            _logger.warning("S2 capitulation 缺 OHLCV，降级 2 参数（治标 z>1）")
            cache["capitulation"] = overlay_features.s2_capitulation_score(vol_z, pct_change)
        else:
            _logger.warning("S2 capitulation 数据缺失，降级 0.0")
```

> **open 字段加载（v0.4.3 补）**：当前 [overlay_signals_builder.py:244-254](file:///d:/ZephyrAlpha/src/zephyr/regime/overlay_signals_builder.py#L244) 仅取 `proxy["close"]/proxy["volume"]/proxy["high"]/proxy["low"]`，**未取 `proxy["open"]`**。施工时需在 L251 后补 `proxy_open = proxy["open"].astype(float)`，并在 L269 派生区补 `open = proxy_open.reindex(feat.index) if proxy_open is not None else None`。这是 capitulation 真实体 + 下影线过滤器的数据前置。

> **lookback / halflife 分阶段**（v0.4.0 给占位值，见 §6 开放问题 1）：trigger 阶段（近 1 月有 capitulation）`halflife=10, lookback=20`；confirm 阶段复苏确认可能在危机后数月（§4.12.4 政策底→市场底滞后 1.5-3 月），衰减应更慢 `halflife=30, lookback=40`（占位，待 §4.5 walk-forward 校准）。施工时按 stage 分参数化，不能全局一个值。

> **参数终值回写（v0.5.3，2026-08-30；Owner 2026-08-29 裁定选项 1 落产，commit c5c23036）**：walk-forward 组合扫描（12 组预注册，IS 2010-2018 / OOS 2019-2026，三事件全程未参与选型）终选 **`base_mode=precrisis_z + wick_mode=close_pos + vol_filter_mode=pct250 + agg_mode=decayed_max`**，`halflife=10 / lookback=20 / trigger≥60` 未动（生产接线实证：[overlay_signals_builder.py:339-340](file:///d:/ZephyrAlpha/src/zephyr/regime/overlay_signals_builder.py#L339)）。验收六层（[验证报告 2026-08-29](file:///d:/ZephyrAlpha/docs/_working/reports/2026-08-29-s2-walkforward-validation.md) §三）：WFE=3.44 ✅ / 负样本 fp@≥60=0.8% ✅ / 参数平移 ±10% 命中率零变化 ✅ / **MC 置换 p=0.87 ❌（诚实标注，DSR N=17 备案）** / MinTRL 低置信标注 ✅ / 预注册纪律 ✅。三事件窗口峰值：2015=0 / 2020=40.2 / 2024=90；2024 接线后窗口末日 73.1≥60，walk-forward 权威路径 confirm 于 Δ=+3/+4/+5d 触发（2026-08-30 实证）。
> **数值边界勘正**：本节"单日 90 分仅贡献 ~12 分（w₀≈0.13）"对应 `agg_mode=wavg`（归一化衰减加权和）；终选 `decayed_max`（衰减峰值）语义为 `max(daily_i × e^(-age_i·0.693/halflife))`——单日 90 分当日即 90，逐日 ×0.933 衰减（2024-10-10 峰值 90 → 10-15 衰减至 73.1 实证）。分阶段参数（trigger halflife=10/lookback=20）维持 trigger 档单档运行，confirm 档（30/40）未启用。

### 4.2 P1-E9b: valuation 基本面化（CAPE/PB 优先）或阈值校准

**现状**（[overlay_features.py:282-303](file:///d:/ZephyrAlpha/src/zephyr/regime/features/overlay_features.py#L282) `s2_valuation_score`）：`close/rolling_max(250, min_periods=20)`，分档 `pos<0.60→20 / <0.50→40 / <0.40→60 / <0.30→80`。用价格回撤代理估值。**调用方**（[overlay_signals_builder.py:310](file:///d:/ZephyrAlpha/src/zephyr/regime/overlay_signals_builder.py#L310)）仅 `s2_valuation_score(close)` 传 1 参数。

**两条子路**（推荐先 B 后 A）：

**路 B（MVP 改良，先做）**：放宽阈值，适配非腰斩级复苏

现状 <0.60→20 / <0.50→40 仍偏严（2020/2024 复苏 pos≈0.90 得 0）。整体右移+提分：

```python
def s2_valuation_score(close: pd.Series, window: int = 250) -> pd.Series:
    """路 B：价格回撤代理估值（MVP，待路 A 升级基本面）。

    阈值校准：原 <0.50 才给 40 过严，放宽为：
      pos<0.70 → 40（距高点-30% 即有估值吸引力，过 confirm 门槛）
      pos<0.60 → 60 / pos<0.50 → 80（腰斩级仍高分）
    """
    rolling_max = close.rolling(window, min_periods=20).max()
    pos = close / rolling_max
    score = pd.Series(0.0, index=close.index)
    score[pos < 0.70] = 40
    score[pos < 0.60] = 60
    score[pos < 0.50] = 80
    return score
```

**路 A（治本，P2 做）**：接入 `c1_market.daily_valuation`，用 **CAPE/PB 历史分位**评分，真正对齐 §4.12.5 基本面估值定义。

**关键陷阱（雪球 2026 席勒 PE 深度报告）**：S2 正是危机场景，危机期盈利 E 崩塌 → PE_TTM = P/E 分母变小 → PE 飙升 → **历史分位反而高（看似高估）→ 评分得 0 → 回到"恒 0"困境**。报告明确：*"PE_TTM 对经济周期极敏感，衰退期 EPS 急剧萎缩导致 PE 被动飙升，形成'越跌越贵'假象；2008/2013 历史大底恰恰是盈利低谷，单纯依赖 PE_TTM 会得出错误判断"*。

**因此路 A 优先用 CAPE（席勒 PE）或 PB 历史分位，PE_TTM 分位仅作辅助**。

> **CAPE 周期：5 年非 10 年（v0.4.0 修正）**：所引雪球 2026 报告实际用 **5 年席勒 PE（5-year CAPE）**——A 股历史数据不足 10 年且市场结构变化大（股权分置改革前数据失真），10 年 CAPE 会混入结构性失效的旧数据。原 §4.2 写"10 年通胀调整平均盈利"与引用源不符，A 股应**优先 5 年 CAPE**（10 年作辅助/回退）。A 股基准（2026-05，雪球）：沪深300 CAPE 12、上证50 CAPE 11、创业板指 CAPE 51.9（分位 52.2%）；银行 PB<1 破净。价格回撤 pos 根本捕捉不到"价格没跌但估值分位已低"。

> **v0.4.3 补 A 股五次底部共识（雪球假价值赛博 2026-06-13）**：A 股 15 年（2011-2026）五次历史大底共同规律 **PE 8-10.5× / 证券化率 37-63% / ERP > 6%**，五次无一例外伴随宏观冲击或流动性危机，且 PE 从未跌破 8×。这**验证了 §4.2 路 A 的 ERP 绝对值 >6% 熊末阈值 + 巴菲特指标（证券化率）<70% 深度低估阈值**。施工时可用此共识作路 A 评分映射的 A 股本土化校验基准——若 CAPE 分位 <10% 但 PE_TTM >15× 或证券化率 >80%，应触发"CAPE 与 PE_TTM 背离"警告（危机期盈利崩塌致 PE_TTM 失真，§4.2 关键陷阱）。

> **v0.4.3 补 A 股 CAPE 分位基准（雪球持股守息 2026-07-05）**：中证 500 简化 CAPE 历史区间——极度低估 <14（2018 底/2022.10）/ 合理中枢 17-19 / 偏高 22-26 / 泡沫 >28（2015 高点破 32）；沪深300 同期 CAPE 约 16.5。当前 §4.2 路 A 用 `<10%/<25%/<40%` 分位映射是美股标准，A 股本土化可参考：CAPE 分位 <10% ≈ 沪深300 CAPE <12 / 中证500 CAPE <14（极度低估，对应 80 分）；<25% ≈ 沪深300 CAPE <15 / 中证500 CAPE <17（低估，60 分）；<40% ≈ 沪深300 CAPE <17 / 中证500 CAPE <19（偏低，40 分）。**Step 0 ① 勘探 daily_valuation 表若已有 `cape_5y_percentile` 字段，直接用；否则需用 5 年 EPS + CPI 自算并分位化**。注意 A 股简化 CAPE 普遍未严格通胀调整（市场通用方式），不影响周期估值对比逻辑。

评分映射（CAPE 分位为主，对齐 §4.12.5 + confirm 门槛 40）：

```python
def s2_valuation_score_fundamental(
    cape_percentile: pd.Series,                    # 席勒 PE 历史分位 0-1（优先 5 年 CAPE，平滑盈利周期）
    pb_percentile: pd.Series | None = None,        # PB 历史分位 0-1（破净辅助）
    broken_net_ratio: pd.Series | None = None,     # 全市场破净率 0-1
    erp_percentile: pd.Series | None = None,       # 风险溢价历史分位 0-1
    erp_absolute: pd.Series | None = None,         # 风险溢价绝对值（v0.4.1，1/PE − 10Y 国债收益率）
    buffett_ratio: pd.Series | None = None,        # 巴菲特指标 总市值/GDP（v0.4.1，A 股本土化）
) -> pd.Series:
    """路 A：基本面估值评分（对齐 §4.12.5）。

    关键（雪球 2026 席勒 PE 报告）：危机期 PE_TTM 因盈利 E 崩塌而"越跌越贵"失真
    （2008/2013 大底是盈利低谷）。S2 正是危机场景，故优先用 CAPE（5 年通胀调整
    平均盈利平滑周期，A 股专用）或 PB 分位，PE_TTM 分位仅辅助。

    评分映射（CAPE 分位为主，对齐 confirm 门槛 40）：
      CAPE 分位 <10% → 80（极度低估）
      CAPE 分位 <25% → 60（低估）
      CAPE 分位 <40% → 40（偏低，刚达门槛）
      else         → 0
    叠加加分（最多 +25，封顶 100；base 80 + bonus 25）：
      PB 分位 <10% 或破净率 >10% → +10
      ERP：分位 >95% 或绝对值 >5% → +5；绝对值 >6%（熊市末期）→ +10（封顶 10）
        （v0.4.1 雪球炎黄投研 2026：ERP 20 年均值 4.1%，>5% 历史大底 / >6% 熊末，
         分位与绝对值双确认避免分位在长牛后失真）
      巴菲特指标（v0.4.1 头条 2026-08，A 股本土化）：<70% → +5
        （美股阈值 <80%，A 股因上市样本不完整+GDP 仅 15% 由上市公司创造+散户 60%+，下调 5-10%）
    """
    score = pd.Series(0.0, index=cape_percentile.index)
    cp = cape_percentile.fillna(1.0)
    score[cp < 0.40] = 40
    score[cp < 0.25] = 60
    score[cp < 0.10] = 80
    if pb_percentile is not None:
        score = score + (pb_percentile < 0.10).astype(float) * 10
    elif broken_net_ratio is not None:
        score = score + (broken_net_ratio > 0.10).astype(float) * 10
    # v0.4.1: ERP 分位 + 绝对值双确认（雪球炎黄投研 2026）
    if erp_percentile is not None:
        erp_bonus = (erp_percentile > 0.95).astype(float) * 5
    else:
        erp_bonus = pd.Series(0.0, index=cape_percentile.index)
    if erp_absolute is not None:
        ea = erp_absolute.fillna(0.0)
        erp_bonus = erp_bonus + (ea > 0.05).astype(float) * 5
        erp_bonus = erp_bonus.mask(ea > 0.06, 10.0)   # >6% 熊末直接满额
    score = score + erp_bonus.clip(upper=10.0)
    # v0.4.1: 巴菲特指标 A 股本土化（头条 2026-08：<70% 深度低估）
    if buffett_ratio is not None:
        score = score + (buffett_ratio.fillna(1.0) < 0.70).astype(float) * 5
    return score.clip(upper=100.0)
```

**数据字段映射**（待 Step 0 勘探确认 `c1_market.daily_valuation` 表结构，见 §6 开放问题 2）：
- `cape_percentile` ← `daily_valuation.cape_5y_percentile`（若无，需用 5 年 EPS + CPI 通胀调整自算）
- `pb_percentile` ← `daily_valuation.pb_percentile`
- `broken_net_ratio` ← `daily_valuation.broken_net_ratio`（全市场 PB<1 占比）
- `erp_percentile` ← `daily_valuation.erp_percentile`（风险溢价 = 1/PE − 10 年国债收益率，分位化）
- `erp_absolute` ← `daily_valuation.erp`（v0.4.1，风险溢价绝对值，>5% 大底 / >6% 熊末）
- `buffett_ratio` ← `daily_valuation.buffett_ratio`（v0.4.1，总市值/GDP，A 股本土化阈值 <70%）

> 若表未含 CAPE，需先建 CAPE 计算管道（5 年 EPS 通胀调整均值），工期可能超 P1，故先做路 B。
> ERP 绝对值/巴菲特指标字段若表未含，路 A 仍可降级运行（仅 CAPE+PB 分位，少 15 分加分）——
> 这两个 v0.4.1 补强项是"锦上添花"非阻断，Step 0 勘探无字段时不阻断路 A。

> **参数终值回写（v0.5.3，2026-08-30）**：**路 A 已建成并接线**（越过路 B 直做治本）——`c1_market.index_valuation_daily` 已回填（中证官网主源 + 内部真 CAPE/分位计算，000300/000905 双指数 2010-01~2026-08 年度连续无断点）；生产路径 [overlay_signals_builder.py:511-547](file:///d:/ZephyrAlpha/src/zephyr/regime/overlay_signals_builder.py#L511) 路 A 优先、路 B 降级告警留痕；评分映射即本节 CAPE 分位三档（<10%→80 / <25%→60 / <40%→40）。实证（2026-08-30 dump + ClickHouse 勘探）：2024 事件 valuation 0→80（09-13 cape_5y_pct=0.0003）→60（10-08 起分位回升）；**2015 事件日 cape_5y_pct=0.34、2020 事件日 0.448 → 0 分经勘探判定为正确信号**（泡沫顶急跌后/疫情底反弹两周后均非深度低估，非数据缺口——2020 底部 03-23 分位 0.298 已正确产出 40 分档）。字段就绪度：`cape_5y_pct` ✅ / `pe_pct` ✅ / `erp`、`erp_pct` ❌ 全表 NULL（ERP 管道未建，已登记 known_data_gaps accepted）/ `pb_pct`、`broken_net_ratio`、`buffett_ratio` ❌（一期暂缺/二期预留）——路 A 当前以 CAPE 分位主轴运行（少 ERP/PB/巴菲特最高 +25 加分，2024 confirm 实证不依赖加分项）。开放问题 2（路 A 数据就绪度）就此关闭。

### 4.3 P1-E9c: spring 复用 wyckoff_engine + 深度分级 + 验收 checklist

**现状**（[overlay_features.py:328-343](file:///d:/ZephyrAlpha/src/zephyr/regime/features/overlay_features.py#L328) `s2_spring_flag`）：close 跨日简化（诊断详见 §1.2.3）。**调用方**（[overlay_signals_builder.py:311](file:///d:/ZephyrAlpha/src/zephyr/regime/overlay_signals_builder.py#L311)）仅 `s2_spring_flag(close)` 传 1 参数。

**v0.4.1 校正（跨日 close 定性）**：上文"时点错位（非逻辑较严）"的定性过绝对。FibAlgo 2026 主流 Spring 算法**就用跨日 close**（"前一根 low 破支撑 + 当前根 close 回收至支撑上方"）——跨日 close 本身是合法实现，非缺陷。当前实现的**真问题**是缺 4 项验收要素：① velocity 量化 ② 穿透深度分级 ③ 0.5×ATR 失效边距 ④ 主尾巴判定，而非"跨日 vs 同日"的时点选择。施工时同日 low / 跨日 close 两种实现均可，关键是补齐 4 要素。

**重设计**：Phase 2c 已激活 high/low，[s2_wyckoff_score](file:///d:/ZephyrAlpha/src/zephyr/regime/features/overlay_features.py#L248) 已委托 wyckoff_engine 6 阶段 FSM（含 Spring 识别，Spring+40 累加进 score）。spring flag 应复用 wyckoff_engine 的 Spring 事件输出，避免与 wyckoff_score 重复逻辑。

**复用前验收 checklist**（参考 Wyckoff Analytics 2025-2026 / ScienceRehashed 2026-05 / ProRealCode 2026-06 / TradingWyckoff 2026）：

复用前必须确认 wyckoff_engine 的 Spring 实现达标以下 5 要素，否则复用即复用缺陷：

| # | 要素 | 标准（含量化阈值） | 来源 |
|---|---|---|---|
| 1 | 主尾巴（main tail） | Spring K 线必须有显著下影线（买盘从极端低点推回）；收盘在最低点的不算 | Wyckoff Analytics 2026 |
| 2 | 量能确认 | 刺破支撑时放量，但收盘不破支撑（刺破是暂时的）；Spring 期间量能应 < Phase A climax（卖压减弱） | Wyckoff Analytics / ScienceRehashed 2026 |
| 3 | 收回速度（velocity） | 快速尖锐下刺+立即反转=强制清算（真 Spring）；缓慢阴跌=假信号。**量化**：收盘跌破支撑不超过 3 根 K 线，同日或次日收盘回到支撑上方 | ScienceRehashed 2026 |
| 4 | 止损距离约束 | 连续低点间距 >10% 则无法设止损，Spring 不成立 | Wyckoff Analytics 2026 |
| 5 | **失效边距**（v0.4.1） | 收盘低于 Spring low 超出 **0.5×ATR(14)** → Spring 失效（防假突破持续跌破支撑，FibAlgo 2026 的 TR 支撑边距） | FibAlgo 2026 |

> **v0.4.3 补 velocity 量化判定（investing.com 2026-02 4-step bottom formula）**：上述要素 3 velocity "≤3 K 线"的**具体判定**可用 4-step 见底公式量化：
> - **第 1 步**：当日 low < rolling_min(low, 60).shift(1)（60 日新低，shake out weak hands，§4.12.1 Phase 3 止损簇扫荡）
> - **第 2 步**：**次日 close > 前日 high**（1 K 线反转，velocity=1，最强）或 **第 2 日 close > 第 1 日 high**（2 K 线反转，velocity=2，可接受）；第 3 日才收回则 velocity=3（边界，需配合量能放大）
> - **第 3 步**：反转日 volume > 1.5× 20 日均量（institutions stepping in，与 §4.1 capitulation 量能过滤器同源）
> - **第 4 步**：止损定义在 60 日新低 low 下方（risk defined，与要素 5 的 0.5×ATR 失效边距互补——0.5×ATR 是技术失效，60 日新低是结构失效）
>
> 施工时 `s2_spring_flag` 可增加 `velocity` 返回值（1/2/3 或 0=未收回），strong_confirm 优先要求 velocity≤2。这与要素 3 的"≤3 K 线"一致，但提供了**可计算的判定逻辑**而非仅定性描述。

**Spring 深度分级（v0.4.0 新增，参考 TradingWyckoff 2026）**：原详设 Spring 是二值（0/1），丢了穿透深度信息。TradingWyckoff 2026 按穿透深度分三类，量能特征不同，信号强度不同：

| 类型 | 穿透深度 | 量能（相对均量） | 信号强度 | 后续要求 |
|---|---|---|---|---|
| Spring #3（minor） | <1% | 低量 40-70% | 弱（弱手少，洗盘轻） | 无需强制 Test |
| Spring #2（moderate） | 1-3% | 中量 80-150% | 中（标准 Spring） | 建议有 Test 确认 |
| Spring #1（major） | >3% | 高量 150-300% | 强（强制清算级） | **必须**有低量 Test（量能较 Spring 降 40-60%）确认卖压耗尽 |

施工时 `s2_spring_flag` 升级为返回分级（0/1/2/3 或 0/0.5/1.0 强度权重），strong_confirm 优先要求 Spring #1/#2（major/moderate）。若 wyckoff_engine 不输出分级，则用 high/low 自算穿透深度兜底。

施工步骤：
1. 审查 wyckoff_engine Spring 实现，逐条对照上表 5 要素 + 深度分级
2. 若全达标 → 直接复用其 Spring flag 输出（抽取接口，确认输出形态：0/1 序列还是带时间戳事件序列 + 是否含深度分级）
3. 若有缺项 → 先补齐 wyckoff_engine 再复用，**禁止带着缺陷复用**
4. 用 high/low 重写 `s2_spring_flag` 为"跌破支撑（同日 low 或跨日 close 均可，FibAlgo 2026）+ 当日 close 收回 + velocity≤3 K 线 + 穿透深度分级 + **0.5×ATR 失效边距**（收盘低于 Spring low 超 0.5×ATR→失效）"作为兜底（wyckoff_engine 不可用时）

> **v0.4.3 补 ATR 止损/失效边距过紧警告（phuazz/breadth-thrust-etf 2026-08 实证）**：上述 0.5×ATR 失效边距是 FibAlgo 2026 的理论值，但 [phuazz/breadth-thrust-etf](https://github.com/phuazz/breadth-thrust-etf)（2026-08 活跃开发，418 commits）实证发现 **2×ATR 止损"actively destructive"**——移除后 7 年总回报从 -1% → +110-128%，中位持有期翻 3 倍。这提示 ATR 倍数对结果极敏感：过紧的失效边距会在正常波动中误判 Spring 失效、过早离场。**Step 0 须加 ATR 倍数敏感性测试**（测试 0.5×/1.0×/1.5×/2.0× 四档），不能直接用单一理论值。同理 §4.1 capitulation 的"实体>40%ATR"阈值也建议做敏感性扫描。

### 4.4 P1-E9d: V 反转通路（confirm 析取逻辑 + Breadth Thrust）★ v0.4.0 新增

**问题**（commit 93a25890 明示）：S2 confirm 门槛 `wyckoff≥60 ∧ policy≥40 ∧ valuation≥40 ∧ fund≥50`，但 2020/2024 是 **V 型反转/政策驱动，不走 Wyckoff 吸筹**（[yaml:91/100](file:///d:/ZephyrAlpha/src/zephyr/regime/validation/phase2/historical_events.yaml#L91)）→ wyckoff 合法偏低 → confirm 永不触发。修好 capitulation/valuation 也救不了 wyckoff。commit 原话："S2 待重设计（**加政策/V 反转信号**）后激活"。

**解法**：给 V 反转开一条 confirm 析取通路，不要求所有复苏都走 Wyckoff 吸筹。

**confirm 门槛改造**（析取逻辑）：

```
原：wyckoff≥60 ∧ policy≥40 ∧ valuation≥40 ∧ fund≥50
新：(wyckoff≥60 ∨ breadth_thrust≥60) ∧ policy≥40 ∧ valuation≥40 ∧ fund≥50
```

即：复苏确认走两条路之一——**Wyckoff 吸筹型**（慢复苏，wyckoff≥60）**或 V 反转/政策型**（breadth_thrust≥60）。policy/valuation/fund 仍为共同必要条件。这样 V 反转时 wyckoff 偏低不再卡死 confirm。

> **为何 breadth thrust 是 V 反转的合适代理**：Zweig Breadth Thrust 衡量"市场广度从恐慌到普涨的急剧反转"——10 日 EMA(adv/(adv+decl)) 从 <0.40 → >0.615 在 10 个交易日内。多个 2026 源（KenMacro 2026-05、AlphaStrategicGrowth 2026-06、TradingSim 2026-06、BuildersLens 2026）一致确认它是"最可靠的牛市启动信号"（历史 ~100% 命中、均值 +24%/12 月）。**关键互补性**：V 反转时 Wyckoff 吸筹不触发（无吸筹结构），但 breadth thrust 恰好在 V 反转的急速普涨中触发——正好补 wyckoff 盲区。A 股涨跌家数数据可得。

**Breadth Thrust 算法**：

```python
def s2_breadth_thrust_score(
    adv_issues: pd.Series,     # 当日上涨家数
    dec_issues: pd.Series,     # 当日下跌家数
    ema_window: int = 10,
) -> pd.Series:
    """S2 breadth_thrust: Zweig Breadth Thrust → 0-100（V 反转/政策型复苏确认）。

    定义（Zweig）：10 日 EMA(adv/(adv+dec)) 从 <0.40 升至 >0.615 在 10 交易日内。
    映射（对齐 confirm 析取门槛 breadth_thrust>=60）：
      触发完整 thrust（从<0.40→>0.615 在 10 日内） → 80
      10 日 EMA >0.615（已进入普涨区，不论起点）    → 60（刚达门槛，适配 V 反转无深洗盘）
      10 日 EMA >0.55（广度改善但未达 thrust）       → 30
      else                                          → 0
    """
    total = adv_issues + dec_issues + 1e-8
    breadth_ratio = adv_issues / total
    ema = breadth_ratio.ewm(span=ema_window, adjust=False).mean()
    # 完整 thrust：10 日窗口内任一时点 <0.40 且当前 >0.615（Zweig 原意，v0.4.2 修正）
    # v0.4.1 bug：ema.shift(ema_window) 只看恰好 −10 日，漏判 washout 低点落在窗口中段
    #   的情形（如 −5 日 <0.40 但 −10 日 >0.40）。改用 rolling().min().shift(1) 取过去
    #   ema_window 日内最低 EMA，匹配"10 日内曾 washout"语义。
    was_washout = ema.rolling(ema_window).min().shift(1) < 0.40
    now_thrust = ema > 0.615
    full_thrust = was_washout & now_thrust
    score = pd.Series(0.0, index=adv_issues.index)
    score[ema > 0.55] = 30
    score[ema > 0.615] = 60
    score[full_thrust] = 80
    return score
```

> **v0.4.3 阈值本土化警告**：0.615 是美股 NYSE 标准（Zweig 原始回测基于 NYSE 涨跌家数），A 股市场广度特征不同。2026-09-24 政策行情中全市场上涨家数占比达 96.97%，远超美股阈值。**Step 0 ③ 勘探时需用 A 股历史数据校准**（建议测试 0.58-0.65 区间），可参考沪深300 成分股上涨占比的 90%分位值。washout 阈值 0.40 同理需校准——A 股涨跌停板制度下极端普跌日占比可能更低。（见 §6 开放问题 9）

**调用链改造**（v0.4.3 补完整代码 diff，三处改动）：

**改动 1：`overlay_signals_builder.py` 新增 breadth_thrust 计算**（需 adv/dec 家数数据，Step 0 ③ 勘探可得性）：

```python
# ── AFTER（v0.4.3，overlay_signals_builder.py _precompute 内新增）──
# breadth_thrust 需涨跌家数数据（Step 0 ③ 勘探）
adv_issues = self._fb_call("get_advance_decline", field="advance")  # 上涨家数
dec_issues = self._fb_call("get_advance_decline", field="decline")  # 下跌家数
if adv_issues is not None and dec_issues is not None:
    adv = adv_issues.astype(float).reindex(feat.index)
    dec = dec_issues.astype(float).reindex(feat.index)
    cache["breadth_thrust"] = overlay_features.s2_breadth_thrust_score(adv, dec)
else:
    _logger.warning("S2 breadth_thrust 涨跌家数数据缺失，降级 0.0")
```

**改动 2：`overlay_signals_builder.py` `_TRANSITION_DIMS` 注册 breadth_thrust**：

```python
# ── AFTER（v0.4.3，_TRANSITION_DIMS["S2"] 新增 "breadth_thrust"）──
"S2": [
    "capitulation",
    "vix",
    "wyckoff",
    "valuation",
    "fund",
    "spring",
    "three_yang",
    "breadth_thrust",   # v0.4.3 新增：V 反转通路（confirm 析取）
    "break_sc_low",
    "vix_new_high",
    "fund_outflow",
    "policy",
    "bad_news_flat",
],
```

**改动 3：`regime_detector.py` TRANSITION_CONFIG["S2"] confirm 改析取逻辑**：

```python
# ── BEFORE（regime_detector.py:200，当前 AND 逻辑）──
"confirm": {
    "keys_gte": {"wyckoff": 60, "policy": 40, "valuation": 40, "fund": 50},
    "p_overlay": {"r11": 0.65}, "shrinkage": 0.6
},

# ── AFTER（v0.4.3，新增 keys_or_gte 析取字段）──
"confirm": {
    "keys_or_gte": {"wyckoff": 60, "breadth_thrust": 60},  # 析取：V 反转走 breadth_thrust，慢复苏走 wyckoff
    "keys_gte": {"policy": 40, "valuation": 40, "fund": 50},  # 合取：共同必要条件
    "p_overlay": {"r11": 0.65}, "shrinkage": 0.6
},
```

> **stage 判定逻辑改造**：当前 `_STAGE_ORDER` 判定仅检查 `keys_gte`（全 AND）。需在 stage 判定函数中新增 `keys_or_gte` 处理——该字段内任一 key 满足阈值即通过（析取），与 `keys_gte`（全满足才通过，合取）并列判定。两者同时存在时，**析取组 AND 合取组** 均须通过。施工时在 `RegimeDetector._evaluate_stage()` 中补 `keys_or_gte` 分支，并新增单元测试验证析取/合取组合逻辑。

**数据可得性（Step 0 勘探项）**：A 股全市场涨跌家数（万得/同花顺 iFinD/东财 API 均提供日度 adv/dec）。若历史数据不足，可先用"沪深300 成分股上涨占比"代理（精度略低但可得）。

> **范围边界**：本节只解决 confirm 的 V 反转通路，不改 strong_confirm（strong_confirm 仍要求 total≥250 ∧ spring≥1 ∧ three_yang≥1，V 反转靠 breadth_thrust 拉高 total + spring/三阳配合）。spring 在 V 反转中可能不触发（V 反转无支撑下破），strong_confirm 对 V 反转可能本就不适用——V 反转走 confirm 即可，strong_confirm 留给 Wyckoff 吸筹型慢复苏。此为预期行为，非缺陷。

### 4.4b P1-E9e: three_yang 三源量化校准（红三兵 6 维标准）★ v0.4.3 新增

**现状**：[overlay_features.py](file:///d:/ZephyrAlpha/src/zephyr/regime/features/overlay_features.py) `s2_three_yang_flag` 实现"连续 3 日阳线"——过于宽松，任何三根小红 K 线即触发，无实体/开盘/上影/量能/位置/失效约束。strong_confirm 要求 `three_yang≥1`，但当前实现无法区分"主力抢筹型红三兵"与"下跌中继三小阳假信号"。

**v0.4.3 校准依据**（2026 八源汇总）：[东方财富 2026-08-04](https://caifuhao.eastmoney.com/news/20260804183514697537220) / [东方财富 2026-07-05](https://caifuhao.eastmoney.com/news/20260705091813267539430) / [什么值得买 2026-06-17（8 源汇总）](https://post.m.smzdm.com/p/al3ddve0/) / 新浪财经 2026-07-07 一致给出 6 维量化标准：

| # | 维度 | 标准（含量化阈值） | 来源 |
|---|---|---|---|
| 1 | **实体递增** | 连续 3 根阳线（close>open），**第三根实体≥第二根 1.5 倍**，第二根实体>第一根（阶梯放大）；实体以中小阳为主（单日 0.5%-5%），**非连续涨停大阳** | 东方财富 2026-07-05 |
| 2 | **开盘位置** | 后一根阳线开盘**落在前一根实体内部**（非跳空高开），收盘价逐日创新高 | 东方财富 2026-08-04 |
| 3 | **上影线** | 上影线长度 **≤ 实体 5%**（光头最佳），严格上限 <实体 50%；收盘接近当日最高价 | 东方财富 2026-07-05 / 8 源汇总 |
| 4 | **量能配合** | **温和递增**：第二日量≥首日 1.1×，第三日量≥前两根均量 **2×**；**禁止巨量**（单根量>前 5 日均量 2× = 一日游风险） | 8 源汇总 / 东方财富 2026-07-05 |
| 5 | **位置要求** | 出现在**长期下跌后底部**（跌幅 >30% + 横盘 >1 月）或**上升中继回踩**（回踩 5/10 日线企稳）；**禁止高位**（短期涨幅 >20-50% = 诱多） | 8 源汇总 |
| 6 | **失效条件** | ① 三根总涨幅 **>15%** = 动能透支；② 后续跌破第三根开盘价 **2%** = 形态失败；③ 后续出现乌云盖顶/黄昏之星 = 见顶 | 东方财富 2026-07-05 / 8 源汇总 |

**三种假红三兵（施工须排除）**：
1. **高位红三兵**：已大幅上涨后三连阳，实体越来越小+缩量 = 诱多出货
2. **下跌中继三连阳**：大下降趋势中三根小阳，无量 = 短暂反弹后继续创新低
3. **缩量红三兵**：股价涨但成交量持续萎缩 = 买盘后继无力

**加强版——三个白武士**：第三根阳线实体显著放大 + 几乎光头（收盘≈最高价）= 多头进攻力度更强，strong_confirm 优先要求此变体。

**实现方案**（`s2_three_yang_flag` 升级为分级返回 0/1/2/3）：

```python
def s2_three_yang_flag(
    open: pd.Series, high: pd.Series, low: pd.Series, close: pd.Series,
    volume: pd.Series, window: int = 60,
) -> pd.Series:
    """S2 three_yang: 红三兵 6 维量化判定（v0.4.3，原"连续 3 日阳线"升级）。

    6 维标准（2026 八源汇总）：
      1. 实体递增：3 阳线 + 第三根实体≥第二根 1.5× + 第二根>第一根
      2. 开盘位置：后根开盘在前根实体内 + 收盘逐日新高
      3. 上影线：上影≤实体 5%（光头最佳）
      4. 量能配合：温和递增（1.1×/1.1×）+ 第三根≥前两根均量 2×，禁止巨量
      5. 位置：跌幅>30%（底部反转）或上升中继
      6. 失效：三根总涨幅>15%→降级，跌破第三根开盘 2%→失效

    返回分级：3=三个白武士（加强版）, 2=标准红三兵, 1=弱红三兵（缺量能确认）,
             0=不满足。strong_confirm 优先要求≥2。
    """
    body = (close - open).abs()
    body_pct = body / close
    upper_wick = high - close
    wick_ratio = upper_wick / (body + 1e-8)

    # 维度 1: 连续 3 阳线 + 实体递增
    is_yang = close > open
    three_yang = is_yang & is_yang.shift(1) & is_yang.shift(2)
    body_inc = (body > body.shift(1) * 1.5) & (body.shift(1) > body.shift(2))
    # 维度 2: 后根开盘在前根实体内
    open_in_body = (open > open.shift(1)) & (open < close.shift(1))
    close_new_high = (close > close.shift(1)) & (close.shift(1) > close.shift(2))
    # 维度 3: 上影≤实体 5%
    small_wick = wick_ratio < 0.05
    # 维度 4: 量能温和递增 + 第三根≥前两根均量 2×
    vol_inc = (volume > volume.shift(1) * 1.1) & (volume.shift(1) > volume.shift(2) * 1.1)
    vol_surge = volume > (volume.shift(1) + volume.shift(2)) / 2 * 2.0
    not_giant = volume < volume.rolling(5).mean() * 2.0  # 禁止巨量
    # 维度 5: 位置（底部反转：60 日跌幅>30%）
    rolling_max = close.rolling(window).max()
    drawdown = close / rolling_max - 1.0
    at_bottom = drawdown < -0.30
    # 维度 6: 失效（三根总涨幅>15%→降级）
    total_gain = close / close.shift(2) - 1.0
    not_overbought = total_gain < 0.15

    # 分级
    score = pd.Series(0, index=close.index)
    base_mask = three_yang & body_inc & open_in_body & close_new_high & at_bottom
    weak = base_mask & small_wick & not_overbought  # 缺量能确认
    standard = weak & vol_inc & vol_surge & not_giant
    # 三个白武士：第三根实体显著放大（≥第二根 2×）+ 光头（上影≈0）
    warrior = standard & (body > body.shift(1) * 2.0) & (wick_ratio < 0.01)

    score[weak] = 1
    score[standard] = 2
    score[warrior] = 3
    return score
```

> **调用链改造**：当前 `overlay_signals_builder.py` 仅 `s2_three_yang_flag(pct_change)` 传 1 参数（v0.5.0 校正：实参是 pct_change 非 close，见 [overlay_signals_builder.py:319](file:///d:/ZephyrAlpha/src/zephyr/regime/overlay_signals_builder.py#L319)），需扩为 5 参数（open/high/low/close/volume），迁移至含 OHLCV 的检查块（与 §4.1 capitulation 调用链改造同类）。

> **strong_confirm 门槛适配**：当前 `keys_gte: {"three_yang": 1}`，升级后建议改为 `{"three_yang": 2}`（标准红三兵及以上），三个白武士(3)作加分但非必要。

> **参数终值回写（v0.5.3，2026-08-30；Owner 2026-08-29 裁定落产，commit c5c23036）**：three_yang 终选 **`grading="v2_index"`**——d5 位置维度回撤门槛 **-30%→-15%**（指数单一口径，Owner 裁定）+ 删 d4 误抄维 + 核心维合取定级/辅助维分级（生产接线实证：[overlay_signals_builder.py:367-370](file:///d:/ZephyrAlpha/src/zephyr/regime/overlay_signals_builder.py#L367)，签名已扩 5 参数 OHLCV）；strong_confirm 门槛 `three_yang≥2` 已按本节建议落码（regime_detector.py S2 strong_confirm keys_gte）。walk-forward 验证（验证报告 §四）：legacy 基线 IS/OOS = 0%/0%，v2_index **IS 12.9%（4/31 簇）/ OOS 0%**——方向正确（IS 破零）但强度不足以单独承载 strong_confirm；OOS 簇（2019-05/2020-02~03/2022/2024-10/2025-04）以 V 反转型为主，红三兵本非该类底部必经形态，与本节"strong_confirm 辅助维"定位一致。三事件窗口 three_yang 仍全 0（2026-08-30 dump 实证），strong_confirm 阶段三事件均不可达（另卡 spring/total≥250）。

### 4.5 P1-E9 验证闭环与防过拟合方法论栈 ★ v0.4.3 重写

> **v0.4.3 重写说明**：v0.4.2 历程声称"§4.5 新增防过拟合方法论栈"但正文未落地（名实不符）。本次重写为完整方法论栈，核心问题：**N=3 历史事件样本极小**，传统 PBO/CSCV 需 N≥10-12 不可用（[archimedes #819 2026-06](https://github.com/)），须用事件研究法 + 预注册 + DSR + CPCV + MinTRL 替代。

重设计后按序验证：

1. **TDD 单元测试 stub**（项目惯例：corrected algorithms 先写 unit test stub 再写主码）：
   - 新建 `tests/regime/features/test_s2_capitulation_score.py`：stub 验证 ① 衰减加权不粘滞（构造单日 90 分后 lookback 日衰减曲线，确认非恒 90）② 多维度过滤器共振（缺量能/缺实体/缺下影线时不给分）③ **数值边界**（单日 90 分贡献 ~12 分，需多日簇集才达 60）
   - `test_s2_valuation_score.py`：stub 验证 ① CAPE 分位映射 ② 危机期 PE 失真不触发（构造 E 崩塌、PE 飙升场景，确认 CAPE 仍低估）③ **5 年 CAPE**（非 10 年）④ **ERP 绝对值**（>5% 大底/>6% 熊末双确认）+ **巴菲特指标 A 股本土化**（<70% 深度低估）
   - `test_s2_spring_flag.py`：stub 验证 ① 跌破支撑判定（同日 low 或跨日 close 均可，FibAlgo 2026）② velocity ≤3 K 线 ③ **深度分级**（<1%/1-3%/>3% 三类量能特征）④ **0.5×ATR 失效边距**（收盘低于 Spring low 超 0.5×ATR→失效）
   - `test_s2_breadth_thrust_score.py`（v0.4.0 新增）：stub 验证 ① 完整 thrust（<0.40→>0.615 在 10 日内→80）② V 反转场景（无 Wyckoff 吸筹但广度急升→≥60，confirm 析取可达）
   - `test_s2_three_yang_flag.py`（v0.4.3 新增）：stub 验证 ① 6 维量化标准（实体递增 1.5× / 开盘在前根实体内 / 上影≤5% / 量能递增+第三根≥2× / 位置跌幅>30% / 失效总涨幅>15%）② 分级返回（0/1/2/3）③ 三种假红三兵排除（高位/下跌中继/缩量）
2. **算法层验证**（独立于 B4）：重跑 `dump_s2_scores.py`，确认三事件日窗口内 capitulation/valuation/breadth_thrust/three_yang 不再恒 0，且 stage 判定合理（trigger/confirm 可达）。**验收标准（v0.4.0 补具体）**：trigger 在事件日 ±10 窗口内触发；confirm 在事件日 ±20 窗口内触发（析取逻辑下 V 反转走 breadth_thrust，慢复苏走 wyckoff）。
3. **B4 验证激活**：3 个 S2 事件 `design_match: false` → `true` 重新激活
4. **Phase 2 完整验证**：重跑 A1+B4+A2+B1，确认 B4 S2 命中
5. **防过拟合方法论栈**（v0.4.3 重写，N=3 小样本专用）：

   **核心挑战**：S2 仅 3 个历史事件（2015/2020/2024），传统 PBO/CSCV 需 N≥10-12 样本才统计有效（[archimedes #819 2026-06](https://github.com/)），**不可用**。以以下 6 层方法论栈替代：

   **① 事件研究法（Event Study）—— 主验证方法**：以事件日（2015-09-15/2020-04-10/2024-09-24）为 t=0，算 ±10/±20 交易日窗口内 S2 各维度评分的异常表现（vs 全历史基线）；不依赖大样本统计推断，逐事件验证"算法是否在正确时点产生正确信号"（[quant67 2026-05](https://quant67.com/post/quant/12-ml-alpha/12-ml-alpha.html)：事件研究法是小样本下最稳健的验证方式）。

   **② 预注册协议（Pre-registration）—— 防确认偏误**：看 3 个事件数据**之前**先锁定 §4.1-§4.4b 全部阈值/参数为预注册文档；实现后跑 B4 与预注册假设对比，**禁止看到结果后回头调参数**（[Neyt/How-To-Backtest-Correctly](https://github.com/Neyt/How-To-Backtest-Correctly) 2026-03 "The Second Law: Never run a backtest until your model is fully specified"）。预注册内容：capitulation 衰减参数（halflife=10/30）、valuation CAPE 分位阈值、breadth_thrust 0.615 阈值、spring velocity 4-step、three_yang 6 维标准、confirm 析取逻辑。

   **③ Deflated Sharpe Ratio（DSR）—— 多重检验校正**：传统 Sharpe 不惩罚多次试验→虚高；DSR 校正试验次数 N、偏度、峰度、Sharpe 方差（[Bailey & López de Prado 2014](https://research.mental-momentum.ai/r/backtest-overfitting-trading-strategy-ju55g3)）。**关键操作要求**：记录所有历史回试次数 N（每次调参/试阈值算一次）供 DSR 校正。

   **④ Combinatorial Purged Cross-Validation（CPCV）—— 替代 walk-forward**：walk-forward 只产 1 条 OOS 曲线（选择偏差）；CPCV 产 N 条性能分布。参数 N=10 组/k=2 测试组→C(10,2)=45 组合；Purging 移除标签窗口与测试集重叠的训练样本，Embargo 训练/测试间加缓冲（日线 2-5 日）（[noonbarbari 2026-07](https://noonbarbari.xyz/de/blog/cpcv-combinatorial-purged-cv) / [Neyt 开源实现](https://github.com/Neyt/How-To-Backtest-Correctly)）。

   **⑤ Minimum Track Record Length（MinTRL）—— 最小可信记录长度**：Lopez de Prado 公式算"给定 Sharpe 和置信度需多长跟踪记录才统计可信"。N=3 事件远不够——MinTRL 会诚实标注"S2 算法验证的统计置信度低"，不作通过门槛，防过度自信。

   **⑥ Walk-Forward Efficiency Ratio（WFE）+ 参数稳定性测试 —— 量化验收门槛**：**WFE = OOS/IS Sharpe ≥ 0.6**（[digitalninjasystems 2026-07](https://digitalninjasystems.wpcomstaging.com/2026/07/03/how-to-avoid-overfitting-when-backtesting/)），<0.5 = 红旗；**参数稳定性**：超参平移 ±10%（如 halflife 10→9/11）Sharpe 陡降=针尖峰过拟合、平滑高原=稳健；**Monte Carlo 置换检验**：随机打乱信号 1000 次，原始策略是否极端离群。

   **开源实现参考**：[Neyt/How-To-Backtest-Correctly](https://github.com/Neyt/How-To-Backtest-Correctly)（2026-03，MIT）实现 Triple-Barrier/Meta-Labeling/Purging & Embargoing/CPCV/DSR/PBO/MinTRL 全套，可 `pip install` 或 vendor 进 `src/zephyr/shared/backtest/`。

   **防过拟合铁律（保留 v0.4.0 原则）**：
   - 算法重设计独立于 B4 验证进行——先按设计意图改算法（过程化/基本面化/V 反转通路），再看 B4 结果。**禁止"调参直到 3/3 命中"**——若改后仍不命中，说明设计意图与历史事件时点有更深层偏差，应回到 §4.12 重新审视事件标注（expected_stage）而非继续调参
   - **超参扫描样本约束**：lookback / halflife / 阈值 / ATR 倍数 / vol_mult / breadth 阈值等超参的扫描须在**独立于 3 事件的样本**（全历史 walk-forward 或其他危机/复苏案例）上做，不能只在 3 个历史事件上调——否则就是"调参过拟合 3 事件"
6. **预期效果量化预估**（施工验收参考基准，**非调参依据**）：
   - capitulation（衰减加权）：2015 窗口外 08-24/25 capitulation 经 halflife=10 衰减到 09-15 约 ~30-50 分（需多日簇集才达 60，预估 trigger 可达但边界）；2020/2024 V 反转 capitulation 在底部触发，衰减后可达 trigger
   - valuation 路 B：2015 pos≈0.58→60 分；2020/2024 pos≈0.90→0 分（路 B 救不了非腰斩，须路 A）
   - valuation 路 A（5 年 CAPE）：三事件危机期 CAPE 分位预期 <25%→60 分，过 confirm 40 门槛
   - **breadth_thrust（v0.4.0）**：2020/2024 V 反转急速普涨，10 日 EMA 广度从 <0.40→>0.615→80 分，confirm 析取通路可达（不依赖 wyckoff）
   - **three_yang（v0.4.3）**：三事件危机后均有连续阳线反弹，6 维量化后预期 2/3 事件达标准红三兵(≥2)，strong_confirm spring≥1 ∧ three_yang≥2 可达
   - B4 预期：五维度修复后 trigger/confirm 可达，S2 预期 2-3/3（取决于 fund/wyckoff 配合）
   - 注：此为设计预估，实际以 `dump_s2_scores.py` 重跑为准，**不作为调参依据**（防过拟合）

### 4.6 演进方向（P2+，非 P1-E9 范围）

v0.4.1 记录 4 个 + v0.4.3 补 2 个 = 6 个 2026 研究发现的更优算法，P1-E9 效果不足时再按本节演进：

1. **AH-HMM 元体制门控**（Tampouris & Dritsaki, JRFM 2026-01）：转移概率依赖未观测元体制（meta-regime），每元体制有自己的转移矩阵。§4.4 析取通路是其具体实现；元体制门控更一般——政策型复苏元体制下 S2 阈值放宽（policy/breadth 权重高），市场型下从严（fund/wyckoff 权重高）。P1-E9 验证 §4.4 效果后若需更细体制自适应再演进。
2. **LVI 强平级联模型**（LiveVolatile 2026-02）：capitulation 建模为机械性强平级联（margin call→强平→价跌→更多强平），LVI=（多头强平总量/未平仓合约）×波动率乘子，>30 高风险/>50 级联中。比 §4.1 更接近 capitulation 本质（杠杆清洗）。A 股可用融资融券余额变化+质押爆仓 proxy；需衍生品/杠杆数据。
3. **滞回边沿触发器**（Modgil, arXiv:2606.19386, 2026-06）：衰减信号做阈值触发时带滞回（触发 60/解除 40）避免衰减曲线在阈值附近震荡反复触发。ArXiv 实证滞回触发每轨迹仅 0-3 次 vs 持续报警 20/20。P1-E9 验证若发现反复触发再加。
4. **ProRealCode 16 事件 FSM 相位引擎**（González 2026-06-09）：相位引擎自动分类 16 个 Wyckoff 事件（PSY/UT/BC/SOW/Spring/TSO...），从事件平衡推断主导相位（ACCUMULATION/DISTRIBUTION/NEUTRAL）——spring 只在 ACCUMULATION 相位下才有效，单 flag 不够。若 wyckoff_engine 不输出相位可参考此引擎补相位判定。
5. **EVR 量价背离信号**（v0.4.3，[YoungCan-Wang/WyckoffTradingAgent](https://github.com/YoungCan-Wang/WyckoffTradingAgent/wiki/01_Finance_Wyckoff_Method) 2026-05）：EVR（Effort vs Result）= 量 >1.6× 均量 + 实体极小（平盘）= 主力暗中吸筹（放巨量但价格没动）。与 capitulation（恐慌卖出）互补，可作 S2 confirm 辅助维度或 wyckoff_score 加分项；A 股用"成交量分位+日内振幅"自算无需新数据。**v0.5.1 补可计算代理**：ADL 反转三模式（FibAlgo 2026-02）——① 经典背离（价格新低但 ADL 更高低，跨度≥5 日+收盘位置由下 25% 区间改善至上 50%）② 吸筹脉冲（大跌日 ADL 暴增，2020-03-23 新冠底实例）③ 隐形吸筹（ADL 走平/微升而价格阴跌 7-10 日）。ADL = 前值 + 资金流乘子×成交量，资金流乘子 = [(close-low)-(high-close)]/(high-low)，纯 OHLCV 可算。
6. **Flush 桥接信号**（v0.4.3，[TradingSim 2026-05](https://www.tradingsim.com/blog/capitulate)）：flush = capitulation 末端最终暴跌（扫掉最后弱手，高量+收盘回前区间+长下影），是 §4.1 capitulation（过程）→ §4.3 spring（收回）的**时序桥接**。量化：当日 low 创 N 日新低 + 收盘回前日区间 + 下影线 >50% + 量 >2× 均量；可作 strong_confirm 时序前置条件。

---

## 5. 联动文档同步清单

| 文档 | 联动改动 | 状态 |
|---|---|---|
| [historical_events.yaml](file:///d:/ZephyrAlpha/src/zephyr/regime/validation/phase2/historical_events.yaml) | S2 `design_match: false` 定级（data_ready 维持 true）+ 注释更新 | ✅ 已落地（commit 93a25890） |
| [overlay_features.py](file:///d:/ZephyrAlpha/src/zephyr/regime/features/overlay_features.py) | capitulation z>1 + valuation min_periods=20（P0 治标） | ✅ 已落地（commit 93a25890）；P1-E9 治本待施工 |
| [b4_transition_accuracy.py](file:///d:/ZephyrAlpha/src/zephyr/regime/validation/phase2/b4_transition_accuracy.py) | design_match 字段 + 三处同步 | ✅ 已落地（commit 93a25890） |
| [architecture_issue_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) | 新建 #ARCH-REGIME-S2-ALGORITHM-001 + 修订 #ARCH-REGIME-OVERLAY-001 fix_phase | ✅ 已落地 |
| [13_regime_phase3_engineering_plan](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md) | §1.1 工程清单加 P1-E9 + §3.5 新增章节 + §0.1 结果摘要更新 | ✅ 已落地 |
| [20_first_batch_strategies §10.4](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/20_first_batch_strategies.md) | 裁定修订："S2 0/3 根因是算法错配 + V 反转设计域不匹配非数据缺失" → 引用本文档 | 待施工（P1 阶段） |
| [12_regime_phase2_validation](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/12_regime_phase2_validation.md) | Phase 2 结果：B4 PASS(3/3) 基于 design_match=false，S2 待 P1-E9 | 待施工（P1 阶段） |

---

## 6. 开放问题

> 优先级标记：[阻断]=不解决无法施工；[重要]=影响效果；[参考]=后续优化

1. **[重要] lookback / halflife 窗口 + 分阶段**：P1-E9a 衰减加权的 `lookback=20 / halflife=10`（trigger）与 `lookback=40 / halflife=30`（confirm，v0.4.0 占位）是否合适？需结合 A 股危机见底到企稳的典型时长校准（§4.12.4 政策底→市场底平均滞后 1.5-3 个月）。施工时按 stage 分参数化，超参扫描须在独立样本上做（§4.5 防过拟合）
2. **[阻断] valuation 路 A 数据就绪度 + 字段映射**：`c1_market.daily_valuation` 表是否已含 CAPE（5 年）/PB 分位/破净率/ERP？若无 5 年 CAPE，路 A 需先建 CAPE 计算管道（5 年 EPS 通胀调整均值），工期可能超 P1。**v0.4.1 补**：ERP 绝对值（`erp`，非仅分位）+ 巴菲特指标（`buffett_ratio`）字段若表未含，路 A 降级运行（少 15 分加分，非阻断，见 §4.2）。字段映射见 §4.2。**Step 0 勘探门禁项**
3. **[重要] 事件标注审视**：若 P1-E9 重设计后 S2 仍不命中 3/3，需回到 §4.12 审视事件日的 `expected_stage` 标注是否合理（复苏事件日应期望 trigger 还是 confirm？924 行情 2024-09-24 是政策启动日，可能 trigger 更合理而非 confirm）
4. **[阻断] wyckoff_engine Spring 接口 + 达标度 + V 反转适用性**：P1-E9c 需确认 wyckoff_engine 是否暴露 Spring 事件 flag + 是否满足 §4.3 验收 checklist 5 要素 + 深度分级。**v0.4.0 升级**：诊断已确认 wyckoff 吸筹模板对 V/政策型复苏设计域不匹配（§1.2.4/§1.3），故 P1-E9d 不改 wyckoff 本身，而是开 breadth thrust 析取通路绕过。但 Spring（strong_confirm 用）仍依赖 wyckoff——需确认 Spring 在 V 反转中的预期行为（可能不触发，strong_confirm 留给慢复苏）。**Step 0 勘探门禁项**
5. **[阻断] breadth thrust 数据可得性（v0.4.0 新增）**：A 股全市场涨跌家数日度数据是否可得？若历史不足，用沪深300 成分股上涨占比代理。**Step 0 勘探门禁项**
6. **[参考] 历史事件样本代表性**（反向防过拟合）：3 个 S2 事件（2015 股灾/2020 疫情/2024 924）都是政策驱动 V 型反转。A 股是否存在"慢复苏型" S2（无强力政策、缓慢筑底，走 Wyckoff 吸筹）未被标注？若只按 V 型反转调参，可能对慢复苏失效——需评估是否扩充历史事件样本。**v0.4.0 注**：confirm 析取逻辑（wyckoff ∨ breadth_thrust）正是为同时覆盖两类复苏而设计
7. **[重要] fund 与 P1-E9 协同**：confirm 需 fund≥50，但 fund 归 P1-E4。P1-E9 修好 capitulation/valuation/breadth_thrust 后若 P1-E4 未完成，confirm 仍卡 fund 门槛——两工程项的施工顺序需协调
8. **[参考] ML trough nowcasting 远期方向（v0.4.0 新增）**：Rao & Rojas 2025（arXiv:2509.05922）用 SVM + 200 特征（期权 RN 偏度/做市商持仓/put-call）实时识别 capitulation，ROC AUC 0.89。需期权数据（沪深300 ETF 期权可得）。非 MVP，记为 P2+ 方向，不进 P1-E9。（另见 §4.6 演进方向：AH-HMM/LVI/滞回触发器/ProRealCode FSM/EVR/flush）
9. **[重要] breadth_thrust 阈值本土化校准（v0.4.3 新增）**：§4.4 的 0.615（thrust）/0.40（washout）是美股 NYSE 标准，A 股广度特征不同（涨跌停板、散户 60%+、924 上涨占比 96.97%）。**Step 0 ③ 用 A 股历史数据校准**（测试 0.58-0.65，参考沪深300 成分股上涨占比 90% 分位）；校准须在独立 3 事件的样本上做（§4.5 防过拟合）。
10. **[阻断] fund 维度升级——成交量代理偏弱（v0.4.3 新增，跨 P1-E4）**：依据与量化方案见 §4.0 fund 警告。**confirm≥50 依赖 fund**——P1-E4 应升级 fund 为"融资余额变化分位 + 超大单净流入分位 + 成交量分位"加权；若 P1-E4 未完成 confirm 仍卡 fund 门槛，施工顺序需协调 P1-E4 与 P1-E9。
11. **[重要] vix 门槛校准——≥40 偏美股标准（v0.4.3 新增，跨 P1-E7）**：依据见 §4.0 vix 警告。**trigger≥40 依赖 vix**——P1-E7 应校准：沪深300 合成 VIX 降至 ≥25-30，或改"IV 近 89 日分位≥80% + 价格布林下轨"（浙商方案，胜率 75-86%）。非 P1-E9 范围，但 trigger 能否触发依赖此。
12. **[重要] ARCH 登记状态三方不一致（v0.5.0 新增，跨文档治理）**：`#ARCH-REGIME-S2-ALGORITHM-001` 的 status 在三处不一致——本文档 §3.2 写 `proposed`（铁律#9 待用户确认）、[10_regime_detector_spec §9.7.3](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/10_regime_detector_spec.md) 写 `confirmed`、[13_regime_phase3_engineering_plan §3.5](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md) 写"待登记"。真源 [architecture_issue_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) 条目为准，10/13 号引用需同步（不越界改，由负责 AI 回填）。
13. **[重要] 12/13 号闭环叙事未同步（v0.5.0 新增，跨文档治理）**：① [12_regime_phase2_validation](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/12_regime_phase2_validation.md) 仍停留在"B4 FAIL(3/6)、S2 0/3 归因数据缺失"的第二批结论，**未回填** commit 93a25890 的 design_match 闭环（B4=S1 3/3 PASS、Phase 2 闭环）——与 10 号 §9.7/本文档/13 号 §0.1 的闭环叙事直接矛盾，12 号作为 Phase 2 验证真源需回填终态（不越界改，由 AI-17 负责）。② 13 号 §3.5.2 仍写"回退 `data_ready` true→false"（路 1 旧表述），与本文档 §2.5 裁定（路 3：design_match 排除 + data_ready 维持 true）矛盾；13 号 §3.5 范围仅 3 维（capitulation/valuation/spring），未同步本文档 v0.4.0/v0.4.3 扩围的 P1-E9d（breadth_thrust V 反转通路）/P1-E9e（three_yang 6 维校准）；E7 编号 13 号写 `P2-E7`、本文档写 `P1-E7` 需统一（不越界改，由 AI-07 负责）。
14. **[参考] 10 号 §4.12.10 十二维体系演进对齐（v0.5.0 新增）**：10 号 §4.12.10 已将 S2 升级为 12 维体系——"触发：8 基础维度≥80 或 4 机构维度≥50；确认：8 基础≥140 且 4 机构≥80；强确认：12 维总分≥**260** + Spring Terminal Shakeout + 信用利差收紧"。本文档 §1.1/§1.3 的 strong_confirm（total≥250）对齐的是 §4.12.8 八维体系。P1-E9 施工前需裁定：TRANSITION_CONFIG["S2"] 的 total_gte=250 是否随 10 号 §4.12.10 升至 260、机构维度组（信用利差等）是否纳入（不越界改 10 号，裁定后回写本文档 §4 + regime_detector.py）。

---

> **本文档定位**：S2 算法缺陷的**完整诊断 + 架构裁定 + 治本详设**单一真源。
> P1-E9 施工时以本文档 §4 为详设依据，[13_regime_phase3_engineering_plan §3.5](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md) 为工程清单引用。
> 治理以 `#ARCH-REGIME-S2-ALGORITHM-001` 为登记真源。

---

## 7. 修订记录

> v0.2.0-v0.4.4 的修订历程记录在文首 blockquote（保留不动）；自 v0.4.5 起在本表登记。

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-31 | 0.5.4 | 头部结案报告区追加"2026-08-31 复核：S2 校准已落产 + B4 重验闭环"回填块 | 2026-08-28 B4 重验注记（0/3 未通过、三过滤器需校准）已过时：S2 capitulation 三过滤器校准已落产（Owner 2026-08-29 裁定选项 1，commit c5c23036，walk-forward 选型+接线生产），B4 全量重跑全 PASS（2026-08-30）；头部无此闭环记录，补登并标注残余项（ERP 全空/2015/2020 design_match 维持 false/演进方向远期） |
| 2026-08-30 | 0.5.3 | 参数终值回写（S2 校准专项收尾，roadmap A1 残余）：§4.1 回写 capitulation 终选组合（precrisis_z+close_pos+pct250+decayed_max，halflife=10/lookback=20/trigger≥60 未动）+ 六层验收结果 + wavg/decayed_max 数值边界勘正；§4.2 回写路 A 已建成接线（index_valuation_daily CAPE 分位主轴）+ 2015/2020 的 0 分经勘探判定为正确信号 + ERP 列全空登记 + 开放问题 2 关闭；§4.4b 回写 three_yang v2_index 终值（d5=-15%）+ IS 12.9%/OOS 0% 验证结论 | Owner 2026-08-29 裁定选项 1 落产（commit c5c23036）后参数终值须回写详设真源；B4 重跑（2026-08-30，A1/B4/A2/B1 全 PASS）+ EVT-2024 design_match 翻 true（confirm Δ=+3/+4/+5d 实证）后终值定稿 |
| 2026-08-15 | 0.5.2 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-02）——§1.4/§2.2-2.4 裁定散文紧凑化；§4.1 三层升级解释精简；§4.3 现状段改指针（诊断详见 §1.2.3）；§4.5 防过拟合 6 层方法论栈列表转段落；§4.6 演进方向 6 条精简；§6 开放问题 9/10/11 与 §4.0 警告去重（改指针+保留关键阈值） | 文档压缩治理（第一轮 ab3df58d9d 后续）；章节编号零改动，参数/裁定/锚点零丢失 |
| 2026-08-09 | 0.4.5 | 文档头统一：frontmatter 补 owner/language/topic/scope + 字段顺序统一（doc_id/priority/depends_on/related_modules/related_issues 扩展字段保留），H1 去文件名前缀与 title 对齐；文末补建本「修订记录」章节（§7）；章节编号与正文零变更 | 15 篇有内容文档结构统一（骨架体系收尾）；14 号此前无修订记录章节，补齐对齐 01_design_memo_management_spec §4.3 规范 |
| 2026-08-12 | 0.5.0 | 第十一轮审查（AI-15）：① §0.1 事件经过表回填 2026-08-07 两个 commit（eb3db21bd8 合成 VIX 后备 + 981d59d8cc S1 correlation 门槛校准）+ 新增因果链完整性注记（数据层根因 vs 算法层根因两层区分）；② 新增 §0.3 已施工设施盘点（通用规则 #11：12 维度函数/合成 VIX/wyckoff_engine/design_match 字段/诊断脚本/测试/治理登记 + P1-E9 未施工清单）；③ §4.4b 校正实参名（s2_three_yang_flag 传 pct_change 非 close）；④ §6 开放问题新增 12-14（ARCH 状态三方不一致 / 12+13 号闭环叙事未同步 / 10 号 §4.12.10 十二维体系演进对齐） | 因果时间线完整性（thresholds 过高/NLP stub=0/合成 VIX 缺失的第一层根因及修复方案此前未入本文档）；规则 #11 基础设施盘点合规；跨文档一致性缺口登记（不越界改 10/12/13 号） |
| 2026-08-12 | 0.5.1 | 第十二轮最新研究整合（AI-15，2026-08-12 全网搜索）：§4.6 演进方向#5 EVR 补 ADL 可计算代理（FibAlgo 2026-02 ADL 反转三模式：经典背离/吸筹脉冲/隐形吸筹，纯 OHLCV 可算无需新数据）；本轮搜索确认 capitulation 检测（Williams Vix Fix 价格合成恐慌指标=合成 VIX 思路同源）与 S2 多维度触发逻辑无新决策缺口 | 第十二轮搜索（crisis recovery/capitulation 2026）增量价值仅 ADL 一项，其余与既有研究库重合 |
