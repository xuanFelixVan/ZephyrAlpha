---
ttl: task_bound
title: 深度审查报告——TF13 crypto+alt_fx币圈外汇族(3任务·daily_crypto错挂executor前科复核)
object: TF13 crypto+alt_fx 任务族（daily_crypto 错挂 executor 前科修复质量复核）
target: src/zephyr/data/config/tasks.yaml:845-869(crypto×2)、3341-3351(alt_fx_ecb)；schedule.yaml:70-73(daily_crypto)、185-191(daily_alt_fx)；scheduler.py:2195-2201(executors)
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=b80084c0df；按工作区现状审）
date: 2026-09-18
status: 已审
---

# 深度审查报告：TF13 crypto+alt_fx币圈外汇族（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 实测 **3 任务**：crypto_kline_daily_incremental（crypto_binance=binance.vision 免 key 公开镜像，Owner 2026-09-11 影子 MVP 裁定，只记账不进 TDM）、crypto_shadow_gate_daily（C-L1 影子判定，依赖前者）、alt_fx_ecb_daily_incremental（frankfurter.app，L1 上架流水线首源）。时段 daily_crypto `41 8 * * *`（全周含周末——7×24 市场 UTC 日界语义）+daily_alt_fx `35 23 * * 0-4`。
- **前科复核对象**：daily_crypto 曾错挂 executor=light（scheduler 执行器字典无此键），APScheduler 注册不校验、每日触发时 Executor lookup failed 并移除 job——该任务自上线从未自动跑成过（水位全靠手动），2026-09-16 治本（schedule.yaml:72 注释自述）。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|
| A | **前科修复质量=通过**：①schedule.yaml:72 executor 已改 default 且留完整病理注释②scheduler.py:2195-2201 执行器字典实有 default/heavy/realtime/intraday_minute/intraday_sector 五键，default 在列③全 23 槽位 executor 值逐一比对（本班全族审查顺带覆盖）无第二处未知执行器④"只增校验"加固可选：add_job 前对 executor 键存在性断言仍未做——同类错挂仍依赖 APScheduler 运行期才暴露（同型隐患=今后新增槽位拼错 executor 会重演"注册成功、每日触发失败、job 被移除"静默戏码，仅报错在调度器日志） | schedule.yaml:72；scheduler.py:2195-2201 | 已修/留加强项 | 加启动断言：executor not in executors → raise |
| A | 修复后任务实际跑通的证据未在配置留痕（如"09-17 起自动水位正常"一行）——修复质量复核建议补一行运行实绩锚 | tasks.yaml:845-856 | P3 | 查 crypto_kline_daily 表 max(trade_date) 是否连续含周末 |
| B | crypto_shadow_gate_daily dependencies=[crypto_kline_daily_incremental] 同槽位强约束（tasks.yaml:864）+lookback_days: 5（回看 5 根幂等重放，tasks.yaml:856）——**断供自愈=5 天窗**，>5 天缺口需手动；binance.vision 单源免 key、无 fallback（影子定位可接受） | tasks.yaml:845-869 | P3 | 停跑 6 天看缺口不自愈 |
| E | **daily_crypto 不在 catchup_guard 任何桶**（catchup_guard.py:43-47）——08:41 错过>1h（misfire 3600s）无补跑；not in TRADING_DAY_GUARDED（正确，7×24 市场不能被 A 股日历挡）也不进 integrity 对账排除集（_NON_DAILY 不含它→23:00 对账"应跑"含它——错过日会进 missing 告警，**告警兜底存在、补跑缺失**） | catchup_guard.py:43-47；integrity_checker.py:61-67 | P2 | 停调度器 08:00-10:00 复演错过→看 23:00 missing 但无补跑 |
| B | alt_fx_ecb：保守游标"各货币对最迟日取 min，任一对缺价下一班回查自愈"（tasks.yaml:3351）+known_issues 假日缺价自愈声明（fx_ecb_provider.py:118-119）+与 Windows 任务双轨并行（退役=挂单 H-06）——自愈语义与哨兵衔接：c1_market.alt_fx_rate_ecb **不在** supply_sentinel 16 表 | fx_ecb_provider.py:118-119；data_supply_sentinel.yaml:28-124 | P3 | 建议补哨兵条目 |
| D | crypto_provider meta 显式声明 crypto_kline_daily+crypto_shadow_gate 双 capability（crypto_provider.py 两处 CapabilityContract 实证）——配置-路由一致；crypto_binance/alt_fx_ecb 两 runtime 不在 data_sources_registry（系统发现 S4） | crypto_provider.py；data_sources_registry.yaml runtime_id 清单 | P3 | 补登记 DS-CRYPTO_BINANCE/DS-ALT_FX_ECB |
| F | 受阻（未检索）。UTC 日界（北京 08:30=UTC 00:30 拉上一完整 UTC 日）与 binance 1D K 线对齐口径正确（训练记忆）；cron 实际 08:41 与描述 08:30 措辞漂移 | schedule.yaml:70-73 | 受阻 | — |

## 3 SOTA 对照
- 受阻。

## 4 缺陷清单
1. P2 daily_crypto 入 catchup_guard daily 桶（或专用桶）+shadow gate 的 5 天自愈窗文档化。
2. P3 启动时 executor 键存在性断言（防"light 错挂"同型三犯）。
3. P3 两 runtime 补登记 data_sources_registry；crypto_kline_daily 补 supply_sentinel 条目（7×24 表阈值=日行数）。

## 5 挂起疑问
- crypto_shadow_gate 的 shadow_version=v0.1 逻辑变更须升版本的约定（tasks.yaml:868）无机器校验——挂起交治理侧。

## 6 完备性自评
六轴全查（F 受阻）。长尾：crypto_universe_selector（Top-50 快照宇宙）的宇宙漂移对 shadow gate 判定影响未查；ECB 假日历与 frankfurter 实际发布时间（北京 22:15-23:15）对 23:35 槽位的余量实证未做。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
