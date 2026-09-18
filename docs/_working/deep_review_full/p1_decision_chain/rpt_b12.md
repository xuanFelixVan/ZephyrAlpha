---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——成本模型校准
owner: st-deeprev-20260918
created: 2026-09-18
reviewed_by: GLM-5.3-Flash/st-deeprev-20260918
---

# 深度审查报告：成本模型校准（B12）

- 状态: **已审**
- 级别: P0｜类型: 引擎（生死线三件套之一，最深查）
- 基线 commit: 2fa92002c3（8 个对象文件基线=HEAD=工作区三方 hash 一致，已验）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/backtest/core/cost_model_calibration.py:77`（PROVENANCE）/:198（liquidity_tier）
- 生产调用方: matching_logic（滑点腿唯一解析）、matching_engine（冲击腿+开关）、result_repository、strategy_factory/owner_band_t/costs.py、owner_regime_switcher/costs.py
- 测试文件: tests/backtest/test_cost_model_calibration.py（41 用例，本轮实跑全绿，238s/8 文件合计）
- 变更热力: 1 commit（新件，2026-09 车道 M 落地）——年轻高危件，尚无返工史
- 备注: 本件零费率字面量，费率真源仍在 matching_logic（设计正确）

## 1 对象快照

- 审查范围：全文件 502 行——分层查表（ADV 五分位）、滑点腿常量+解析序、冲击腿 A-C 档（η/β/σ/γ）、地板佣金→最小名义闭式、PROVENANCE 证据件。
- 排除项：matching_engine 的 participation cap 实现（属 B 系另件，本轮只核其消费点 :791-866）；PROVENANCE 数值与原始 tick 数据的对拍（本地无 13,119,233 条快照复算环境，长尾登记）。
- 材料包缺项声明：数据画像（tick 快照分布）未取；运行时证据包未取（本件为纯函数无日志面）。
- 数学四问结论总览：分层查表/闭式推导/A-C 公式/边界 Fail-Closed **全部通过**；发现集中在**证据披露工件（PROVENANCE）与出厂常量的口径错位**。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | sqrt_law_Y 披露值与出厂常量口径错位：cross_checks 记 "Q1≈2.2、Q5≈0.7"，用出厂 γ=0 复算实为 1.693/0.539；披露值精确等于 γ=0.5η 口径（2.182/0.695，公共因子 1.2887）——证据是在另一套参数下算的 | cost_model_calibration.py:140-144 vs :307-316,332 | P2 | `python -c` 复算：`eta[0]*(1e-3)**(0.4205-0.5)`=1.693；乘 `(1+0.5*1e-3**(0.5-0.4205))`=2.182 |
| A | eff_vs_quoted 披露 "低 6%~5%"，实算 2.5%~7.5%（Q1=7.5%、Q3=2.5%），区间两端都不对 | :138 vs :228-234 | P3 | `(7.83-7.24)/7.83`=7.5%；`(4.79-4.67)/4.79`=2.5% |
| A | liquidity_tier 只自检 SLIPPAGE_TIER_BPS 长度，不检 IMPACT_TIER_ETA/IMPACT_TIER_SIGMA；后两者改短→裸 IndexError 而非 CostCalibrationError（Fail-Closed 有洞） | :214-215 vs :310,319,399-404 | P3 | 读代码+构造 4 元 eta 表调用 impact_level_for_tier(4) |
| A | 类型契约不一致：resolve_slippage_bps 声明收 Decimal 并 float() 转换，但直接调 slippage_bps_for_notional(Decimal) 会在 liquidity_tier:209 抛错 | :267-269 vs :209,298 | P3 | `slippage_bps_for_notional(Decimal("1e7"))` → CostCalibrationError |
| A | 数学四问通过项：五分位单调分层 ✓；floor_drag_bps 与 notional_for_floor_drag_bps 闭式互逆（代入验证 ✓）；A-C temp=η·p^β·σ 量纲=收益比例→bps ✓；γ=0 防 temp/perm 双计的论证成立（静态快照不可辨识时间轴）；NaN/负/bool/∞/p∈[0,1] 全部显式抛错 | :203-219,330-332,354-365,415-427 | 通过 | 互逆验证 `N=floor*1e4/(d+rate*1e4)` 反代回 floor_drag_bps→d |
| A | A 股口径：volume 手→股 ×100、五档量纲、min ¥5 地板结构、印花卖方单边——unit_gotchas 三条均有实证锚 | :156-163 | 通过 | 000001 amount/volume≈1182.9=100×11.82 复算 |
| B | 输入=日成交额（40 日 ADV 或当日额单调近似）。上游给错额（如手/股混淆）→ 落错层 → 成本差 2-3×；本件无法发现（无量纲校验），但 unit_gotchas 已把教训写死，matching_engine:861-866 有 [0,1] participation fail-closed 兜底 | :203-208; matching_engine.py:861-866 | P3 | 手/股混用使 participation 缩 100×，η 表现虚高——PROVENANCE 已自证 |
| B | `SLIPPAGE_TIERING_ENABLED` 导入期绑定陷阱已用 calibration_enabled() 访问器规避（A/B 取证可 monkeypatch）——防御到位 | :256-264 | 通过 | monkeypatch.setattr 测试已在测试文件内 |
| C | 消费方全列：matching_logic.py:525（逐笔滑点）、matching_engine.py:812/841（冲击腿，开关关→整腿回 legacy DEFAULT_PARAMS）、result_repository.py:317（归因补计）、owner_band_t/costs.py:56-67、owner_regime_switcher/costs.py（实盘成本核算）。参数错→**全部撮合回测 Sharpe 与策略工厂成本核算同时失真**（爆炸半径=全 sleeve） | 各文件行号 | 说明 | grep 锚点已核 |
| C | "策略侧下单规模硬约束尚无消费者"——头部自曝最小名义闭式零生产接线（诚实体） | :5 | P3 | grep notional_for_floor_drag_bps 消费方仅 cost_attribution 披露轨 |
| D | 兄弟实现：almgren_chriss_impact_model.DEFAULT_PARAMS（legacy 档，开关关时回退）；LEGACY_FLAT_SLIPPAGE_BPS=1（A/B 对照）。双承载是**有意开关语义**非漂移，且 resolve_slippage_bps 唯一解析序防复制 | :236-243,279-283 | 通过 | grep "SLIPPAGE_BPS =" 第二真源无 |
| D | 与 cost_attribution 的口径衔接：B11 未传 adv map 时退化路径产生 participation=1.0（详见 rpt_b11 P1）——本件 cost_ratio_at 域 [0,1] 合法但**标定拟合域是微小 p**，域内外推的防护不在本件（消费方责任未文档化到 B11 头部） | :354-361 | P2 | 见 rpt_b11 实测 199.70bp |
| E | 静默失败面：本件纯函数全 Fail-Closed，无 except 吞点；开关是全局 bool，无并发写面；幂等（同输入同输出）✓ | 全文件 | 通过 | — |
| E | 重跑幂等 ✓；但 PROVENANCE 是 frozen 常量，改档位必改 PROVENANCE 的 MODIFY-GUARD 只有约定无 gate 拦截（人肉纪律） | :9 | P3 | grep pre-commit/CI 是否校验（无） |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| 流动性分层 TCA 校准（滑点+冲击双腿、按流动性/规模分层取值） | **对等已有**：A 股卖方/业界通行做法即按流动性与规模分层校准隐性成本；ML 冲击成本专题（华创证券）与智能算法冲击成本模型（知乎专栏）同构 | 华创证券算法交易隐形成本专题（og.microbell.com, 年份未标注≈2023-2024）；知乎智能算法交易冲击成本模型（zhuanlan.zhihu.com/p/68100949, 2021） |
| 尺寸相关冲击腿平方根律 β | **对等已有（带偏差记录）**：经典平方根律 β=0.5（AQR/BSIC Transaction Costs 讲义；业界通用）；本件实证 β*=0.4205 略低但为五层中位数拟合值，属实证自由度内，非错误 | BSIC/AQR "Trading Costs - Modelling Transaction Costs and Market Impact"（PDF 讲义，≈2015-2020） |
| A-C 模型 temp/perm 拆分 γ=0.5 惯例 vs 本件 γ=0 | **对等已有且论证更强**：静态快照不可辨识时间衰减，强行取 0.5η 会双计；业界执行调度场景才需显式 perm 项（Almgren-Chriss 2000 原始框架需时间轴） | Almgren & Chriss (2000, Quantitative Finance)；本件 :327-332 裁定注释自洽 |
| A 股成本口径不可照搬美股 | **对等已有**：quant67 交易成本模型对照明确警示 A 股（T+1、涨跌停、印花单边）与美股口径差异——本件 unit_gotchas/A 股结构处理与该共识一致 | quant67.com 交易成本模型（冲击成本、滑点、TCA 对照，≈2023） |

## 4 缺陷清单

1. **P2｜PROVENANCE sqrt_law_Y 披露与出厂常量口径错位**
   - 现状：cross_checks 披露 "Q1 @p=1e-3 时 Y≈2.2、Q5≈0.7"（:140-144），并断言"落于业界 A 股中小票 1~3 区间"。
   - 证据：按出厂 γ=0（:332）复算 Y=[1.693, 1.263, 0.984, 0.830, 0.539]；披露值精确等于 γ=0.5η 口径（×1.2887）——证据是在"惯例 γ 拆分"参数化下产出，出厂件却取 γ=0，PROVENANCE 与常量不同源。
   - 影响与爆炸半径：PROVENANCE 随 artifact 披露（cost_attribution.to_metrics_dict 挂 provenance 全文），未来审计者按披露值复核会对不上账（差 ~30%）；且按披露区间判断，出厂 Q5（0.539）根本落在"1~3 区间"之外，交叉校验叙事自我矛盾。不改变撮合参数本身，不直接亏钱，故 P2 非 P1。
   - 建议修法：按 γ=0 口径重算并更新 cross_checks 文本（或注明披露值为 γ=0.5η 口径的历史对照）；同步修正 "1~3 区间" 的适用表述。
   - 验证法：`python -c "eta=(0.9776,0.3114);f=(1e-3)**(0.4205-0.5);print([round(e*f,3) for e in eta])"` → [1.693, 0.539]。
2. **P3｜eff_vs_quoted 百分比区间失真**：披露"低 6%~5%"实为 2.5%~7.5%（逐层复算）；描述性文字，不影响数值。
3. **P3｜冲击腿表长无自检**：liquidity_tier 自检只对 SLIPPAGE_TIER_BPS（:214），IMPACT_TIER_ETA/SIGMA 改短会在 impact_level_for_tier 抛裸 IndexError，违反自身 ERROR_CONTRACT（应 CostCalibrationError）。建议补齐两表长度断言。
4. **P3｜Decimal 入参契约不一致**：resolve_slippage_bps 声明收 Decimal（:267）但同参直传 slippage_bps_for_notional 抛错（:209）；统一类型闸门即可。
5. **P3｜docstring 硬编码金额**：commission_floor_nonbinding_notional 注释 "≈¥58,548"（:464）绑死特定费率，费率变更后注释变假真源。
6. **说明（不列缺陷）**：γ=0、双腿正交（eff<c1 证据）、手→股量纲、边界 Fail-Closed、A/B 开关位点——五项深查全部通过。

## 5 挂起疑问

- IMPACT_TIER_SIGMA 随流动性**递增**（Q1 2.04%→Q5 3.90%，:319-325）与 A 股横截面"小票高波动"常识相反——可能是分层中位数真实形态（低流动票含长期停牌/一字板拉低波动），也可能是上游 vol 计算口径问题。需对拍 c1_market.kline_daily 复算各层 σ 中位数（本轮无数据环境，登记长尾）。
- 单窗口 39 自然日、ADV 边界无陈化监测（known_limits 已披露前半，边界漂移监控缺位未披露）。
- 分层边界按成交额五分位而非市值分层（已披露）；Q1 内小市值占比未量化。

## 6 完备性自评

- 六轴全查：A（逐公式四问+复算）✓ B（ADV 上游+开关）✓ C（消费方 grep 全列）✓ D（legacy/标定双承载=有意开关）✓ E（五问过，纯函数无静默面）✓ F（2 次检索，TCA/平方根律/A-C 均有来源）✓。
- 长尾：①13.1M 条 tick 快照的 η/β/σ 原始对拍（缺数据环境）；②各层 σ 反常方向复算；③MODIFY-GUARD 无机械 gate 的人肉纪律面。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P2 PROVENANCE 证据工件与常量不同源: 挂起登记（工件再生）。TCA/平方根律对等确认。
- 修复提交: q-0024（B11 冲击腿）。
