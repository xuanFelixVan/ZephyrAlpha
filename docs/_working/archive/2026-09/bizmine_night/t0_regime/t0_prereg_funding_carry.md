---
ttl: task_bound
rule_form: data
verifiability: manual
title: T0 预注册卡 T0-PRERG-02——币圈资金费率 delta 中性 carry（C1，设计冻结）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-19
status: 已封卡 SEALED（2026-09-19 真实费率重判一次后封卡，裁定#363；修订见 §7，禁静默改）
lane: T
family_id: T0-PRERG
n_eff: 1
parent_context: t0_subjective_methods.md §2.2 + t0_conversion_table.md §3-C1 + T4 币圈研究（t0_crypto_research.md）
---

# T0-PRERG-02：高资金费率币对的 delta 中性 carry 扣费后为正？

## 1. 假设（H1，唯一）

**在 Hyperliquid 永续高 funding 分位币对上构造"现货多+永续空"纸面 delta 中性配对，持有期 funding 结算净收入（年化）显著大于开平仓往返费用与再平衡成本，且收益衰减主因=funding 收敛速度。**

零假设 H0：扣费后年化 carry ≤ 0，或 funding 收敛快于建仓延迟使期望 carry ≤ 0。

机制自述（关③）：永续合约 funding 机制在多头拥挤时对空头持续付费；delta 中性持有空头腿即收租（Kraken/TradeSanta 综述，网络来源见 t0_subjective_methods.md §3）。

## 2. 数据与口径（冻结）

- 主料：`c1_market.hl_funding_history`（4,655,619 行，234 币，2023-05-12→2026-09-18；字段 coin/funding_time/funding_rate/premium/quality_flag）。
- 两腿行情：`c1_market.crypto_kline_daily`（70 币，2025-08-08→2026-09-17）——**局限明写**：日线粒度，funding 结算为 8h 级，两腿价格差（basis）只能日频近似；现货腿数据若与永续标的不一一对应（如现货币对 vs 永续 coin），以 symbol/base_asset 映射表为准，映射不上的币对剔除。
- IS/OOS：IS=2025-08-08→2026-02-28（定阈值），OOS=2026-03-01→2026-09-17（单次通过）。
- PIT：t 日决策只用 funding_time ≤ t 的 funding 行与 ≤t 的日线。

## 3. 策略规则（冻结）

- 信号：coin 的 funding_rate 3 期（3×8h）均值折年化 > +25% → 次日开"纸面配对"（现货多+永续空各 1 单位名义）。
- 平仓：funding 3 期均值年化 < +5% → 次日平仓。
- 容量：同时持有 ≤5 币对，等权。
- PnL：Σ(各 8h funding 结算 × 名义) − 开仓往返费 − 平仓往返费 − 再平衡费（delta 偏离 >5% 时再平衡，费按 1 次 taker 计）。
- 压力情景（披露不拦截）：永续腿单独 -10% 插针的保证金冲击情景表。

## 4. 及格/判红判据（冻结）

| 关 | 判据 | 门槛 |
|---|---|---|
| ① carry | OOS 净年化 carry（扣全费） | **> 5%** 年化 |
| ② 命中率 | 开仓后 30 日内 funding 维持 >0 的周期占比 | **> 70%** |
| ③ 机制 | 收益归因中 funding 项占比 | **> 80%**（排除 basis 误配贡献） |

费率占位披露（冻结时未核实 Owner 实际档）：taker 2bp/边、maker 0bp 占位（Binance VIP0 量级，模型知识未引证）；**考试执行前必须以 Owner 实际费率档+Hyperliquid 官方费率页重估，若与占位差 >1bp/边则本卡自动作废重开**。

## 5. 纪律

- 本卡为设计冻结，本役不跑数；执行前须：①两腿数据映射核查；②费率核实；③trial ledger 登记 N_eff=1。
- 结果无论红绿全量入册；负结果同样是"币圈=做T战略延伸"评估链的正式证据。

## 6. 勘误（2026-09-19，执行前数据事实修正）

- 原文"funding_rate 3 期（3×8h）均值/各 8h funding 结算"有误：T4 数据盘点实测 Hyperliquid funding 为**小时级**结算（28,833 行/币 ≈ 3.4 年 × 24/日，`t0_crypto_research.md` §1）。
- 修正：信号=过去 **24 期（24h）**均值年化（年化系数 ×24×365，非 ×3×365）；平仓线同步改为 24 期均值年化 < +5%；开平仓延迟语义不变（次日执行）。**判定门槛（§4 三关数值）不变**。
- 本勘误为数据颗粒度事实修正，发生于任何考试运行之前，随 T4 报告同批入册。

## 7. 修订附录（2026-09-19，裁定#363：按真实费率重判一次后封卡）

- **修订项（唯一）**：§4 费率占位披露中的"taker 2bp/边"按卡内作废条款与裁定#363 修订为 **Hyperliquid 公开档真实费率：现货 taker 7bp/边 + 永续 taker 4.5bp/边**（每事件=两腿各 1 边=11.5bp，每对往返=23bp）。其余 frozen 参数（§3 规则、§4 三关门槛、§6 勘误后信号定义）**零改动**。
- **重判结果**：OOS 净年化 carry +3.03%（占位口径 +4.09%），距 5% 门 1.97pp，**verdict=RED 变硬**；关② 88.73% 过、关③ 153.8% 退化通过（零鉴别力声明沿用）。判定与首考同向，证据变硬。全量数字与可复现性核验=同批 `crypto_probe/funding_carry_rejudge.md`。
- **封卡**：按裁定#363，本卡重判一次后**封存（SEALED）**，不再重开、不再改参重跑；机制遗产知识（动用率/费率双挤压读数、maker 腿等未来杠杆点）归档于重判报告 §5，任何未来重开=新卡新 N_eff，与本封卡无预授权关系。
