---
task_id: "TASK-SYS-0031"
source_blueprint: "SYS-MASTER-001"
source_section: "§49 智能执行与微观结构 + §57 因子择时与跨资产配置 + §58 交易日历与合约管理 + §65 因子治理与策略生命周期深化"

title: "智能执行五算法(TWAP/VWAP/IS/POV/Adaptive)+Almgren-Chriss冲击+FIX Protocol 6消息 + 因子择时(HMM 3状态+战略战术60/40+6×6跨资产) + 交易日历(3交易所+期货换月+期权到期) + 因子治理四阶段(准入/去重正交化/监控/退役)四合一骨架"
description: |
  将 §49 智能执行 + §57 因子择时与跨资产 + §58 交易日历 + §65 因子治理四合一落地为端到端执行与因子管理管线。
  §49 定义：
  （1）五种执行算法——TWAP（1-15min ping）· VWAP（跟随成交量分布 hist vol profile）· IS（Implementation Shortfall——最优化冲击/风险 risk_aversion λ）· POV（PercentOfVolume x=10%市场量）· Adaptive（实时条件选择——动态算法选择）。
  （2）Almgren-Chriss 冲击模型——Market Impact(元) = η·σ·(X/V)^γ + ε（η=0.14/γ=0.6/ε=0.01/σ=20天）。
  （3）FIX Protocol 映射 6 消息——D（NewOrderSingle=下单）/8（ExecutionReport=成交拒绝）/F（OrderCancelRequest=撤单）/G（OrderReplaceRequest=改单）/4（OrderCancelReject=撤单拒绝）/3（Reject=订单拒绝）。
  §57 定义：
  （1）市场状态识别 HMM 3 状态——Bull S1（Trending低Vol→Momentum+Growth）· Sideways S2（Ranging→Mean Reversion+Quality）· Bear S3（High Vol→Low Vol+Value/Defense）。
  （2）战略-战术分配——战略长期 60%（LTerm Expected Return Strategic weights）· 战术短期 40%（基于 HMM状态 Rotate factor weights）。
  （3）6×6 跨资产相关——Equities/Fixed Inc/Commodities/FX/Crypto/Cash→每月重算 ρ。
  §58 定义：
  （1）交易日历 3交易所——NYSE（ET, 9 key假日）· CME期货（ET）· ICE商品（ET）。
  （2）期货换月——ES（close>5天）· CL（close>3天）· GC（close前1-3天）· ZN（Before First Delivery 15天）。
  （3）期权到期——Monthly SPX（第3个Fri）· Weekly（每个Fri roll→close）· Quarterly（季末Fri）。
  §65 定义：
  （1）四阶段因子生命周期——准入门（Admission：经济逻辑+WFO IS/OOS Sharpe≥0.3+DSR≤0.05+无泄漏→GATE_NEWFACTOR）· 去重正交化（所有因子对 ρ>0.7→horse race→保留好的→去重）· 监控（IC均值+std+IC半衰期+最近3月IC>0占比→周/月）· 退役（12月IC<0.01/σ>3σ/Sharpshooter/Owner主动标记→Cold Storage）。
  （2）文法正交化管线——原始50因子→cluster ρ>0.7→保留代表→非代表→Cold Storage→结果50→12代表预测能力不降。
  本卡搭建 algo_execution.py + factor_timing.py + trading_calendar.py + factor_governance.py。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\algo_execution.py"
    description: "§49 TWAP/VWAP/IS/POV/Adaptive 五算法 + Almgren-Chriss + FIX 6消息映射"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\factor_timing.py"
    description: "§57 HMM 3状态(Bull-Bear-Sideways) + 战略60/战术40分配 + 6×6跨资产ρ月度重算"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\trading_calendar.py"
    description: "§58 3交易所(NYSE/CME/ICE)日历 + 期货换月ES/CL/GC/ZN + 期权到期Monthly/Weekly/Quarterly"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\factor_governance.py"
    description: "§65 4阶段(准入Sharpe≥0.3DSR≤0.05/去重ρ>0.7horse race/监控IC+半衰期/退役IC<0.01→ColdStorage) +正交化50→12"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\algo_execution.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\factor_timing.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\trading_calendar.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\factor_governance.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§49 5算法+AC+FIX + §57 HMM+60/40+6×6ρ + §58 3交易所+换月+期权到期 + §65 4阶段+正交化"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 30000
timeout_minutes: 80

acceptance_criteria:
  - "algo_execution.py 实现 AlgoType 枚举（TWAP/VWAP/IS/POV/ADAPTIVE）——TWAP(child_orders 1-15min) · VWAP(child_orders weighted by hist vol profile) · IS(optimize impact vs risk, risk_aversion λ) · POV(participate x=10% of mkt vol) · Adaptive(dynamic select by condition)"
  - "algo_execution.py 实现 AlmgrenChriss——impact(η=0.14 * σ * (X/V)^γ, γ=0.6, ε=0.01, σ=20d)→estimate slippage via volume function· FIXMessage——6 MsgType(D 下单/8 ExecReport/F CancelReq/G ReplaceReq/4 CancelReject/3 Reject)→builder+parser"
  - "factor_timing.py 实现 HMMStateDetector——3 隐状态 Bull/Sideways/Bear→各自最优因子 mapping（Momentum+Growth/MR+Quality/LowVol+Value）· StrategicTacticalAllocation——strategic 60% LTermER· tactical 40% HMM rotate weights· CrossAsset 6×6 ρ matrix（Equities/FI/Comm/FX/Crypto/Cash）monthly recalc"
  - "trading_calendar.py 实现 TradingCalendar——3 exchange（NYSE ET/CME ET/ICE ET）holiday list· FuturesRoll protocol（ES close>5d start/CL close>3d/GC 1-3d before close/ZN 15d before FirstDelivery）· OptionExpiry（Monthly 第3Fri/Weekly 每个Fri roll→close/Quarterly 季末Fri）"
  - "factor_governance.py 实现 FactorLifecycle 枚举（ADMISSION/DEDUP_ORTH/MONITOR/RETIREMENT）——Admission（WFO IS/OOS Sharpe≥0.3 + DSR≤0.05 + NoLeak → GATE_NEWFACTOR）· Dedup（ρ>0.7→ horse race keep best→remove redundant→ColdStorage）· Monitor（IC mean+std + IC half-life + IC>0 ratio last3months → weekly/monthly report）· Retirement（12m IC<0.01 OR σ>3σ OR Sharpshooter OR Owner mark→ColdStorage archive）"
  - "factor_governance.py 实现 Orthogonalizer——raw factors[]→compute ρ matrix→cluster ρ>0.7→per cluster keep representative→rest→ColdStorage→output: N→representative_count with prediction_power preserved"

rollback_instructions: |
  1. 删除 algo_execution.py / factor_timing.py / trading_calendar.py / factor_governance.py
  2. 从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0027"
blocked_by: []
status: "created"
tags_fn:
  - "trading"
tags_ly: "cross_layer"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "SYS-MASTER-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
