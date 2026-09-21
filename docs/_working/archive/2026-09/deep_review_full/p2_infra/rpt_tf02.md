---
ttl: task_bound
title: 深度审查报告——TF02 intraday_minute分钟K族(16任务)
object: TF02 intraday_minute 分钟K任务族
target: src/zephyr/data/config/tasks.yaml:287-495（kline_1min..60min×5 / kline_etf_*×5 / kline_lof_*×5 / market_breadth_snapshot_minute）；schedule.yaml:40-43
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=b80084c0df；按工作区现状审）
date: 2026-09-18
status: 已审
---

# 深度审查报告：TF02 intraday_minute分钟K族（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 实测 **16 任务，0 disabled**，全部 `source: miniqmt`、全部无可用 fallback（market_breadth 显式置空留痕 tasks.yaml:492）。时段 `*/5 9-15 * * 0-4` executor=intraday_minute(4线程)（schedule.yaml:40-42；scheduler.py:2199），时段在交易日守卫集（trading_calendar.py:154）。
- 本族即任务书点名的 **kline_etf_15min UTC误标CST前科** 所在族：修复于今日落地（commit 60ed3aa49c，2026-09-18：五表 4.12 亿误标行全部转正，备份 *_tz_bak_20260918 在库可逆，known_data_gaps 登记 etf_minute_tz_split_pre_202607）。
- 材料缺项：无运行时证据包/数据画像；轴 F 检索受阻如实记。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| A | **UTC误标前科复核**：根因修在 schema/物化层（CREATE AS 子句/确定性冻结台对账/MATERIALIZED 排除+显式回拷列，commit 60ed3aa49c），修复件 repair_etf_minute_tz_split.py 按 tick_depth_backfill 先例 gitignore 不入库（可复现性弱化——修复工具本身无回归测试载体）；另有 config/quality_sentinel_tables.yaml tz_shift 盘中小时分布哨兵（tz_suspect_hours 0-7 点=疑似 -8h）作为持续防线 | 60ed3aa49c；config/quality_sentinel_tables.yaml:8-25 | P3 | 对 2026-09-17 以后新行跑 tz 哨兵 SQL 看零误标 |
| E | **S-TF02【族级最高风险】16/16 任务主源=miniqmt 且 0 fallback**：9/18 miniQMT 退役后整族无退路。迁移台账 §2.2-A 自认"最大缺口：桥无 K 线 dump 通道"，三选一摸底推荐方案 b（tick 聚合合成）已落地为 qmt_bridge 的 kline_1min..60min capability（qmt_bridge_provider.py:174-180），但 **本族 15 个分钟K任务仍挂 source: miniqmt**（台账红线"主源切换统一走 9/17 收盘后窗口"未在现状留痕）；且 ETF/LOF 任务声明的 capability 是 kline_etf_1min/kline_lof_1min 等**独立 capability ID，桥 meta 只声明了 kline_1min..60min 六个通用 ID**——即便切 source 也过不了启动契约校验（CAP-NOT-FOUND ERROR，capability_validator.py:84-106） | tasks.yaml:287-478；qmt_bridge_provider.py:174-186；capability_validator.py:96-105；migration-ledger §2.2-A/§8.5 | **P1** | 9/19 起观察 integrity_check 23:00 对账 missing 列表应含本族16任务；或现在停 QMT 复演单任务 |
| B | market_breadth_snapshot_minute 挂 */5 槽位但语义=1 分钟级快照（配置注释自认"44号 §9.1 的 1 分钟级节拍需槽位提速或独立槽位——留痕为后续优化项"）——快照密度低于设计口径，属已知降级留痕非缺陷 | tasks.yaml:484-486 | P3 | 对照 44 号备忘 §9.1 |
| A | kline_5min_incremental 是族内唯一 `date_col: trade_time`（其余全 trade_date）——非缺陷：backfill/integrity 侧已用 `toDate({date_col})` 包裹修正 DateTime64 等值比较恒失真问题（backfill_checker.py:255-257 注释自认修复）；但该 outlier 无注释说明，易被后人"纠正"回 trade_date 造成断点续传游标错位 | tasks.yaml:304；backfill_checker.py:255-257 | P3 | git blame tasks.yaml:304 找原始裁定 |
| C | 整族爆炸半径=A股/ETF/LOF 全部分钟级下游（技术指标多周期重算 technical_indicator_full_refresh 9 周期、逆势榜、分钟宽度）——本族断供→technical_indicator 周末全量重算输入缺近期分钟段 | tasks.yaml:2168-2181 | P2 | 断供日后跑 full_refresh 看 1min 段缺口 |
| D | 桥方案 b 的合成口径（open=首tick/close=末tick/半根bar裁剪）与原生 get_market_data_ex bar 口径存在快照语义偏差（台账 §8.5 自认"偏差需对拍量化"），对拍计划未见落地留痕 | migration-ledger §8.5 方案 b | P2 | 切换后同窗对拍 akshare 分钟线 ±1 价位容差 |
| E | 0 行成功=WARN 通知仅限交易日（scheduler.py:1749 交易日 gate）+周 Schedule 级对账（integrity 23:00）兜底；无推送通道（alerter.py:28-29）复用系统发现 S1 | scheduler.py:1735-1756 | P2 | 同 TF01 §2 E 行验证法 |

## 3 SOTA 对照
- 受阻（未检索）。tick→bar 合成（方案 b）业界常见（快照聚合 vs 逐笔聚合的极值偏差为已知课题），台账已把偏差对拍列为后续——立卡候选：对拍偏差率阈值（价格±0.01 外偏差>2% 或 bar 缺口>1% 则立项沙箱 dump，台账 §8.5 建议已写）。

## 4 缺陷清单
1. **P1 整族断供风险**：现状=16 任务 miniqmt 零退路→影响=9/18 后全市场分钟K停更，且 ETF/LOF capability ID 与桥 meta 不对齐使"切 source"也不能直接生效→建议=①桥 meta 补 kline_etf_*/kline_lof_* CapabilityContract（或任务 capability 改挂通用 ID+symbols 路由）②9/17 窗口 source 切换落盘③对拍偏差监控立卡→验证法=切换日后对比 kline_1min 表 data_source 分布与行数连续性。
2. P3 修复工具不入库：repair_etf_minute_tz_split.py 九轮实跑不可复现——建议工具入库 tests/ 豁免通道或至少留 dry-run 快照。
3. P3 kline_5min date_col outlier 无注释（见上表 A 行）。

## 5 挂起疑问
- 桥 universe 是否真含 ETF/LOF 全集（台账 §8.5 称"桥 universe 含基金 2270 只"）未独立核验——若缺，方案 b 对 ETF/LOF 不成立。
- 4.12 亿行修复的抽样验证比例与边界日（2026-07 切换日）对拍结果未在 commit message 外的文档中找到。

## 6 完备性自评
六轴全查（F 受阻）。长尾：16 个 provider 路由（miniqmt _KLINE_CAPABILITIES）未逐一深查；ETF/LOF 表 DDL 与桥写通道列序一致性未核。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
