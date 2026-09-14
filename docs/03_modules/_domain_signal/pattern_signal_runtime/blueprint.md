---
blueprint_id: MOD-SIG-147
module_name: pattern_signal_runtime
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-09-14
last_updated: 2026-09-14
owner: ZephyrAlpha-Owner
---

# MOD-SIG-147 pattern_signal_runtime 蓝图

> 设计真源：图形库消费端方案 v1.0（docs/_working/2026-09-14-pattern-consumer-plan.md
> §C1，dd4c754f06 落库）。消费班施工批 W-C1。

## 0. 文件清单

| 文件 | 说明 |
|------|------|
| src/zephyr/signal_ashare/strategy_signal/pattern_signal_runtime.py | 装配根本体 |
| tests/signal_ashare/strategy_signal/test_pattern_signal_runtime.py | 链路单测 |

## 0.1 定位

**纯装配根，零业务算法**。断点实证（2026-09-14 反查）：全仓仅回填脚本构造
UnifiedPatternEngine，mapper（MOD-SIG-115）/adjuster（MOD-SIG-131）建成零装配——
本模块把四个生产件拼成一台能开机的机器：

    PatternWinRateProvider(145) ──win_rate_fn──▶ UnifiedPatternEngine(091 注入契约)
    PatternEvent ──▶ PatternToSignalMapper(115) ──payload──▶ CTR-002 校验（MOD-CON-002）
                                                        │ Fail-Closed
                                                        ▼
                                            CTR-002 FactorSignal 兼容载荷（唯一出口）

## 1. 契约

- `PatternSignalRuntime(*, provider=None, win_rate_query=None, validator=None, clock=None,
  stop_buffer_pct=1.0, default_win_rate=0.5, timeframe="day", fwd_window=10, regime_tag="")`
  ——provider 与 win_rate_query 互斥（装配歧义禁止）；
- `build_engine(config=None, **kw)`：引擎工厂，win_rate_provider 已注入（091 契约）；
- `on_events(symbol, events, *, as_of=None)`：事件流→map_batch→emit_signal；
  空事件=空载荷不发信号（无形态不出网）。
- 默认校验器 `Ctr002PayloadValidator`：mapper 的 payload dict→FactorSignal→MOD-CON-002
  validate().ok；显式增查 symbol 非空/values 非空/as_of 不晚于时钟（PIT）；**任何异常
  一律 False（Fail-Closed 拒绝出网）**。

## 2. 不变式

1. 零业务算法——行为问题去各自 blueprint（091/115/145/MOD-CON-002）；
2. CTR-002 出口强制经校验器，validator 恒非 None（mapper 侧禁止旁路+本侧默认装配）；
3. 零新增错误码——映射错=PatternSignalMapError(ZA-SIG-0147)，库错=provider RuntimeError，
   全权委托既有契约（净零）；
4. 同输入必同输出（确定性 idempotency_key=blake2b(symbol+as_of+values)）。

## 3. 依赖

| 上游 | 契约 |
|------|------|
| MOD-SIG-091 unified_pattern_engine | PatternEvent/PatternScanResult/win_rate_provider 注入参数 |
| MOD-SIG-115 pattern_to_signal_mapper | map_batch/emit_signal/SignalValidator |
| MOD-SIG-145 pattern_win_rate_provider | get(pattern_id, timeframe, fwd_window, regime_tag) |
| MOD-CON-002 ctr002_producer_validator | Ctr002ProducerValidator.validate |

下游（W-C2 接入）：signal_factory 档投票总线；W-C3：MOD-SIG-131 adjuster。

## 4. 边界与 W-C2 落位记录（2026-09-14）

W-C2 已落位：①regime 门=runtime 构造参数 regime_filter（symbol,regime_tag）→bool，
拒准出空载荷（准入路由，不造检测器，复用胜率表 regime_tag 切片口径）；
②审计快照=metadata 增 win_rate_snapshot（逐事件 win_rate）+regime_tag+weight_version
（信号可溯源"当时为什么发"，VCP 思路个人化裁剪）；③总线接入=factory 参数
（SignalFactory 鸭子型），逐方向取最强分量注册 SignalDraft（signal_id=幂等键:方向，
NEUTRAL 跳过，重复幂等跳过留痕 notes）。

W-C3 已落位：①PatternWeightSync——物化完成→sync_from_provider：拉全行统计
（low_sample/查无跳过=不录样本不调权）→win_rate=Wilson LB、ic=ic_scale×(命中率−基准)
截断代理（方向优势代理非真实 IC，真实 IC 待逐笔 PnL 证据层；drawdown=0.0 不伪造，
装配建议 dd_coef=0）→131 record_metrics+adjust 限幅调权；②PatternWeightStore——
权重状态 JSON 持久化（data/runtime/pattern_signal_weights.json，safe_write CAS，
tmp_path 注入测试，重启恢复上次权重）；③main(--sync-weights) CLI=物化完成事件钩子
可挂载正身（JOB-108 日链 materialize 之后追加本步，禁 cron/Timer）。

仍不做：前端呈现（W-C4）；执行层（方案 C6）。

## 5. 测试

链路单测六景：引擎注入生效（recognize 事件带胜率）/on_events 全链路/空事件不发信号/
未来 as_of 拒绝/适配器 Fail-Closed 四态/装配歧义。
