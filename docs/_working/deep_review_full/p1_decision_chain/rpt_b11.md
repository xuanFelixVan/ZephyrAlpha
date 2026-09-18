---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——成本归因
owner: st-deeprev-20260918
created: 2026-09-18
reviewed_by: GLM-5.3-Flash/st-deeprev-20260918
---

# 深度审查报告：成本归因（B11）

- 状态: **已审**
- 级别: P1｜类型: 引擎
- 基线 commit: 2fa92002c3（基线=HEAD=工作区一致，已验）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/backtest/core/cost_attribution.py:148`（CostAttribution）/:396（attribute_trade_costs）
- 生产调用方: result_repository.py:318-357（唯一生产注入点，落 artifact metrics["cost_attribution"]；fw_backtest 经 result_repository 间接消费）；脚本 eval_exp_expectations.py
- 测试文件: tests/backtest/test_cost_attribution.py（54 用例实跑全绿）
- 变更热力: 1 commit（新件）
- 备注: 台账 #23 H2-A 治本件；本轮产出 1×P1（ADV 缺失时冲击腿超标定域外推且生产路径必然触发）

## 1 对象快照

- 审查范围：全文件 718 行——佣金重构/地板判定、滑点/冲击双腿分档计费、反旁路 max(实测,标定)、as-run 双轨、告警生成器。
- 排除项：matching_logic 费率常量本体（B12 域）；ch 落盘链（P2 域）。
- 材料包缺项声明：真实 run 的 artifact 成本快照分布未拉（用合成单笔实测代替）；告警触发率的历史日志未取。
- 关键实测：`attribute_trade_costs` 不传 `adv_notional_by_symbol`（=生产唯一调用方式）时 calibrated_impact_w_bps=**199.70bp**；传 ADV 3.0e7 时=3.65bp（**55 倍差**）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **ADV 缺失回退路径冲击腿超标定域外推**：`adv = g_float`（自身名义当 ADV）→ `participation = g/max(g, ε) = 1.0` → `cost_bps_at(1.0)=η·σ` ≈ 199.7bp/边（tier0）。标定拟合域是五档走单的微小 p（1e-4~1e-2 量级），p=1.0 是纯外推。docstring 声称"参用率分母退化到该层代表 ADV"（=TIER_ADV_MEDIAN），代码分母实际是 `max(adv, TIER_ADV_MEDIAN×1e-12)`（仅防零，非代表 ADV）——**文档与代码矛盾** | cost_attribution.py:526,535-536; docstring :421-423 | **P1** | 实测复现：单笔 ¥2,200 交易不传 adv map → to_metrics_dict()["calibration_gap"]["calibrated_impact_w_bps"]=199.7041；传 {'000001':3.0e7} → 3.6454 |
| A | **生产唯一调用方不传 adv 映射与逐笔冲击**：result_repository.py:348-357 的 attribute_trade_costs 调用无 `adv_notional_by_symbol`、无 `impact_bps_by_trade` → 上述 P1 路径是**每个生产 artifact 的现实状态**，非边界 | result_repository.py:348-357 | P1 证据 | 读调用点；grep fw_backtest 亦无 adv 传参 |
| A | 未上报逐笔冲击时"不判旁路"（by design）→ 生产恒 None → `impact_leg_bypassed` 恒 False → **IMPACT-LEG-BYPASSED 反旁路对当前生产零效力**（检测器自身被旁路，docstring 有声明但告警语义形同虚设） | :425-427,584-588 | P2 | 生产调用点无 impact_bps_by_trade 实证 |
| A | 数学通过项：地板判定 max(比例,下限) 与 B12 同口径 ✓；exec cost 符号（buy 正=劣/sell 反号）✓；stdev n-1、n=1→0 ✓；分位数线性插值含空序列 Fail-Closed ✓；空 trades 显式抛错 ✓（不伪造零值） | :134-144,497-507,552-558,597-606,432-433 | 通过 | 单测覆盖+读码 |
| B | 上游 trade_log：side 大小写双词表（本件 _side_of 收 BUY/SELL/买/买入 宽词表——比 B13 稳健）；缺 commission 行按注入费率重构 ✓；decision_price 缺失跳过不猜 ✓ | :274-280,509-514 | 通过 | 对比 B13:262 窄匹配 |
| B | consumed_slippage_bps 缺省回退 LEGACY 1bp → 分层消费的 run 若调用方忘传，必触发 SLIPPAGE-UNDERCHARGED 误报（方向=噪声非沉默，可接受但污染告警信噪比） | :450-452,611 | P3 | consumed_bps 缺省值读码 |
| C | 输出消费方：artifact metrics（人审+脚本 eval_exp_expectations.py）；P0/P1 告警经 logger.warning 出声（result_repository.py:366-368）。P1 缺陷使 cost_total/冲击分量/成本占比系统性虚高 → **COST-DOMINATES-RESULT P0 告警可能由虚高触发**（假阳性引导归因讨论），as_run 轨不受污染（真实扣钱口径独立） | :571,594; result_repository.py:366 | 说明 | 对比 cost_total vs cost_total_as_run 双轨字段 |
| D | 兄弟件：B12（分档真源）复用而非复制 ✓；matching_engine 冲击腿（实测轨）与本件标定档（应计轨）双轨设计，两轨字段分离披露 ✓ 无同义两算 | :536-550 | 通过 | — |
| E | 重复触发/幂等：纯函数 ✓；异常路径全部 CostAttributionError 点名到笔 ✓；无 except 吞点（:486 noqa BLE001 是转抛非吞）✓ | 全文件 | 通过 | — |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| 佣金/滑点/冲击三分量 TCA 归因 | **对等已有**：机构 TCA 标准分解（explicit+slippage+impact），与 Talos/fe.training 的 TCA benchmark 框架同构 | Talos "Execution Insights Through TCA"（talos.com, ≈2023）；fe.training TCA 材料 |
| 冲击应计 = max(实测, 标定档) 反旁路 | **立卡候选**：业界 TCA 通常只披露实测，无"实测不得清零应计"的工程反旁路——本件做法偏保守工程化，立卡价值=防引擎静默旁路，但当前生产不喂实测使该机制空转（见 P2），立卡时应先补实测轨接线 | 本件 :34-37 设计注释；业界对照=Quantitative Brokers pre-trade cost model（quantitativebrokers.com, ≈2023） |
| 地板佣金→最小下单规模闭式 | **对等已有**：固定最低佣金下优化下单粒度是零碎资金实盘常识；本件给出闭式与容忍线（5bp）是干净落地 | 华创证券算法交易隐形成本专题（og.microbell.com, ≈2023-2024） |

## 4 缺陷清单

1. **P1｜ADV 缺失回退 → 冲击腿 200bp/边虚计，生产路径必然触发**
   - 现状：participation 回退实现为 `g/max(g, tier_median×1e-12)`≡1.0（:535-536），非 docstring 声明的"分母退化到该层代表 ADV"（:421-423）；p=1.0 落在标定拟合域外 2 个数量级。
   - 证据：实测单笔无 ADV → calibrated_impact_w_bps=199.7041、impact_total=43.93（名义 2,200 元计 2%）；生产唯一调用点 result_repository.py:348-357 两参皆缺。
   - 影响与爆炸半径：所有生产 artifact 的 cost_attribution 冲击分量、cost_total、cost_share_of_abs_result、calibrated_impact_w_bps 披露全部虚高 ~55×；COST-DOMINATES-RESULT（P0 级告警）可被虚高值触发，误导"一半亏损是佣金"类的归因叙事；as_run 轨与真实 PnL 不受影响（无直接资金损失，故 P1 非 P0）。
   - 建议修法：分母回退改 `TIER_ADV_MEDIAN_YUAN[tier]`（与 docstring 对齐），或调用方接入真实 ADV 表；并给 participation 加标定域 clamp+披露。
   - 验证法：`python -c` 单笔调用对比有无 adv_notional_by_symbol 的 to_metrics_dict()["calibration_gap"]（本轮已实测）。
2. **P2｜反旁路机制生产不可达**：impact_bps_by_trade 生产恒 None → bypassed 恒 False（:584-588）。旁路检测存在但从未参战。建议：result_repository 从 matching_engine 回填逐笔冲击，或将"未上报"单独披露为告警级事实。
3. **P3｜部分行缺 commission 时 reported_commission 部分和当全量**（:509-514,568-570），静默低估；建议记录 coverage 计数。
4. **P3｜adv_map 键 [:6] 截断静默**（:449,516）：跨市场同码异后缀会串层；A 股现状无碰撞，记录风险。
5. **P3｜consumed_bps 缺省 LEGACY 1bp** 误报 SLIPPAGE-UNDERCHARGED（:450-452）：建议缺省改 universal 3.79bp 或必填化。

## 5 挂起疑问

- "顶五成交占比 99.1%/佣金 51.7%"叙事（docstring）基于旧 run；标定滑点上线后新 run 的归因结构是否复核过，需收口方拉最新 artifact 验证。
- IMPACT-TERMS-UNIDENTIFIED 告警的 σ<0.05bp 阈值在 decision_price 大面积缺失（旧产物）时形同虚设（exec_n 不足直接跳过），历史批次是否漏告警待查。

## 6 完备性自评

- 六轴全查：A（含数值实测复现）✓ B（trade_log 词表/费率注入源）✓ C（唯一生产注入点+脚本消费方）✓ D（与 B12/引擎双轨）✓ E（五问：无静默面、幂等、无时序）✓ F ✓。
- 长尾：①真实 run artifact 成本快照全量分布画像；②告警历史触发率统计（运行时证据包未取）；③fw_backtest 侧对 cost_total 的下游断言强度未逐个审。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P1 ADV 缺失回退→冲击腿 55× 虚高（生产 artifact 全量污染，as_run 轨未污染故非 P0）: 确认→治本（participation 分母按 docstring 契约退化到层代表 ADV）。对拍：修复前 no-ADV=199.70bp → 修复后 3.63bp（与传 ADV 3.6454bp 比值 1.00×）。复检 177/177。
- 修复提交: q-0024（B11 冲击腿）。
