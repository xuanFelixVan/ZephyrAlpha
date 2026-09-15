---
ttl: task_bound
title: T1-α 节点挖矿：wyckoff_engine + synthetic_vix（D-SIGNAL-68 Phase 2c 小节点扫）
session: st-qoder-t1a-20260915
date: 2026-09-15
parent: S11_assembled_backtest
---

# 挖矿节点 6：wyckoff_engine + synthetic_vix（D-SIGNAL-68 Phase 2c 小节点扫）

> 挖矿日期：2026-09-15 ｜ 会话：st-qoder-t1a-20260915 ｜ 唯源骨架：S11_assembled_backtest/nodes/
> 挖矿依据：overlay_dims_mining §5 遗留小节点——wyckoff_engine（6 阶段 FSM）+
> synthetic_vix（期权 IV 合成 VIX + 下行半偏差后备）
> 证据等级：全部结论经最小复现 + 11.5 年真实 000300 数据（2790 日）实证

## 1. 头号发现 WYF-1（P0）：wyckoff_engine 生产路径结构性死亡——6 阶段里 4 阶段数学上不可触发，S2 confirm 门槛永不可达

**实证（000300，2015-01-05~2026-06-30，2790 日，生产同款引擎参数）**：

| 阶段 | 权重 | 11.5 年触发次数 | 结论 |
|------|------|----------------|------|
| PS | 10 | 151 | 唯一活体 |
| SC | 30 | **2** | 畸形日才触发 |
| AR | 15 | **0** | 永不触发 |
| ST | 20 | **0** | 永不触发 |
| Spring | 40 | **0** | 永不触发（理论关键转折） |
| Test | 20 | **0** | 永不触发 |

wyckoff_score max=40，**>=60（S2 confirm 门槛）天数 = 0**。维度名义可算，
实际贡献恒 0/40 两档（cummax 粘滞 40 分是噪声不是信号）。

**两个独立 bug 叠加**：

1. **SC 条件数学不可达**（wyckoff_engine.py L106）：`c <= rolling_min + 1e-8`
   中 rolling_min 是 **low** 的 60 日滚动最低（含当日）。因 low ≤ close 恒成立
   （且实际数据 low < close），`min(low) ≤ 当日 low < 当日 close` → 条件要求
   **close == 当日最低价且为 60 日最低**（光脚收盘在 60 日最低，11.5 年仅 2 次）。
   应该是 close 对 close 的滚动最低（或 low 对 low）。最小复现：教科书式暴跌
   序列（单日 -7%/-8% 巨量）SC=0；仅当人为令 low==close 才点亮 1 次。
2. **ar_vol_avg 稀疏 rolling 恒 NaN**（L118）：`v.where(ar>0).rolling(10).mean()`
   在 AR 事件日（稀疏）之外全 NaN，pandas rolling(10) 默认 min_periods=10
   要求窗口内 10 个非 NaN——即 **10 日窗口内出现 10 个 AR 日**才非 NaN，永不成立。
   → ST 的缩量条件（v < NaN×0.7）与 Spring 的缩量条件（v < NaN×0.8）恒 False。
   最小复现：单 AR 日注入，稀疏 rolling 非 NaN 数 0/400。应 ffill() 后
   rolling(min_periods=1)（用"最近一次 AR 日的均量"作缩量基准）。

**连锁效应**：Spring 永不触发 → "Spring 是关键转折 +40 → 过 confirm 门槛 60"
的设计意图（spec §4.12.2）整体落空。s2_wyckoff 完整版（overlay_signals_builder
在 high/low 可用时优先走）比它替换掉的 MVP 回退版（range<2% & pos>0.6 → 70 可
过门槛）**更差**——升级即死亡。

**裁定建议**：两 bug 均为确定性缺陷（非校准债），修复合入前 S2 confirm 的
wyckoff 维度应视为不存在；修复后需 walk-forward 重校（AR 10 日窗/ST ±2% 带/
Test 20 日窗均为拍脑袋值，见 §3 校准债）。

## 2. WYF-2（P1）：wyckoff_engine 零测试 + 头部声明失真

- 头部 `[TESTS] none # 2026-09-05 AI-00：全仓无测试 import 本模块`——P0 级
  FSM 引擎（决定 S2 confirm 一 whole 维度）零测试，WYF-1 两个 bug 在生产里
  存活至今的直接原因。修 bug 必须同步补测试（6 阶段各一触发场景 + 边界）。
- docstring 声称"所有事件标记用 rolling + **shift**（严格历史）"，实际除
  not_new_low（L101）外无任何 .shift()（SC/AR/ST/Spring/Test 均含当日窗口）。
  兜底 PIT 由调用方 shift(1) 保证，未泄漏未来，但"文档声称≠代码行为"是
  本仓惯发事故模式。

## 3. WYF-3（P2）：wyckoff 校准债清单（修 bug 后才值得校）

- AR 的 `sc_recent` 窗 10 日、ST 的 sc_recent 同窗 10 日、Test 的 spring_recent
  窗 20 日——Wyckoff 理论里 AR 紧随 SC 数日，但 ST 可在数周后；10 日窗偏紧。
- `in_sc_zone` 固定 ±2% 带（L124）不随波动率自适应。
- `high_breakout = h >= h.rolling(10).max()` 含当日 → 当日即 10 日最高时恒真，
  条件实际退化为"当日是 10 日新高"（弱但可用）。
- MVP 回退版（overlay_features.s2_wyckoff_score）固定用 20 日窗，window 参数
  60 在回退路径被忽略——参数契约失真。

## 4. SVX-1（正面+P2）：synthetic_vix 下行半偏差后备路径健康，期权 IV 路径零测试

**正面**：
- synthetic_vix_pct（后备）有 10 个单测（test_synthetic_vix.py），覆盖值域/
  warmup NaN/危机飙升/与 vol_pct 互补性/恒价/窗口参数——P0 后备链路可信。
- 降级链完整：期权 IV 失败 → 合成 VIX → None → s1/s2 回退 vol_pct，每层有
  log，C1 不退化守住。

**P2 债**：
- `compute_synthetic_vix` + `vix_pct_from_vix`（期权 IV 优先路径，CBOE 简化式）
  **零测试**：_interp_vix_for_date 的近月/次月插值、单标的降级、双标的均值
  均无覆盖。期权表有数据的日子走的就是这条未测路径。
- _interp_vix_for_date 用**近月全部 DTE≤30 期权的 IV 均值**当作 t1 点参与
  30 天线性插值——均值的"DTE"不是 t1（t1 取近月最大 DTE），插值口径与
  均值口径错位（简化式可接受，但应注记）。
- vix_pct 需要 250 日 option_iv 历史 + overlay 侧 rolling rank 又 250 日——
  期权表历史深度决定 IV 路径实际覆盖起点，若表浅则大多数回测期实际走的
  是后备路径（与 t3_inputs 同理，建议在 print_regime_history 输出里加
  vix_pct 来源标记便于核查）。

## 5. 正面清单

- wyckoff cummax 传播（"已发生"语义）PIT 安全：只用历史事件，无未来泄漏。
- score cap 100 兑现 [0,100] INVARIANTS；无结构=0 守住 C1。
- synthetic_vix 降级链三层设计正确，接口同构（vix_pct∈[0,1] 与 vol_pct 可
  无缝互换）在 s1_vix_panic_score 的 per-element combine_first 落实到位。

## 6. 修复优先级裁定建议

| 项 | 级别 | 动作 |
|----|------|------|
| WYF-1 SC close-vs-low | P0 | bug 修复 + 最小复现测试（真数据 11.5 年实证 0 过门槛） |
| WYF-1 ar_vol_avg 稀疏 rolling | P0 | ffill+min_periods=1 修复 + 测试 |
| WYF-2 零测试 | P0 同批 | 6 阶段触发场景测试补齐 |
| SVX-1 IV 路径零测试 | P2 | _interp_vix_for_date 插值/降级测试 |
| WYF-3 校准债 | P2 | 修 bug 后 walk-forward 再校 |
