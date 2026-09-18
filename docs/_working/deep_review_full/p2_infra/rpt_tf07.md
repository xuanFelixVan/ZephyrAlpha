---
ttl: task_bound
doc_type: report
title: 深度审查报告——TF07 daily_kline盘后日K族(31任务)
object: TF07 daily_kline 盘后日K任务族（核心行情+复权+图形认证+打板装载）
target: "src/zephyr/data/config/tasks.yaml:22-3240（schedule: daily_kline 31条，主锚 22/37/52/67/79/261/274/408/498/513/632/871/1634/1662/1674/1831/2153/2207/2240/2278/3049/3081/3154-3212/3214-3290）；schedule.yaml:74-77"
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=b80084c0df；按工作区现状审）
date: 2026-09-18
status: 已审
---

# 深度审查报告：TF07 daily_kline盘后日K族（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 实测 **31 任务**（disabled 6：kline_weekly/kline_monthly/global_hsi/nikkei/kospi/usdcnh）。16:30 heavy(2线程)，交易日守卫（schedule.yaml:74-77；trading_calendar.py:155）。族内构成：核心行情 5（adj_factor/kline_daily_hfq/kline_daily/daily_valuation/kline_index，全部 miniqmt 主源+akshare/baostock fallback）、etf_daily+kline_cb（miniqmt **无fallback**）、周月hfq 2（miniqmt+akshare fb）、internal 派生 8（anchored_state/technical_indicator/kline_index_calc/kline_sector_880×2/pattern 链×3/4+daban_engine_load）、tqcenter 2、akshare 5、tushare 1（etf_nav）、图形认证链 pattern_event→win_rate→certify→weight_sync（DAG 同时段串联）。
- 防线：跑完自动触发日线标的数看门铃（±1% 容差 vs 近5日中位，scheduler.py:1385-1442,2068-2075——920 段静默降级 4 天事故治本）。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| E | **S-TF07【高】9/18 退役直接打击核心行情 5 任务主源**：adj_factor/kline_daily_hfq/kline_daily/kline_index 主源 miniqmt。fallback 配置合法（akshare meta 有 adj_factor:868/kline_daily_hfq:870/kline_index:869；baostock kline_daily）但注意：①fallback 长期全量接管后 miniqmt dr 行口径注释（akshare_provider.py:230——adj_factor 的 miniqmt dr 行仅覆盖 2026-07 起，此前 bdpan 累计口径被 SQL 修正）提示主备口径衔接有历史坑 ②**kline_etf_daily_incremental 与 kline_cb_incremental 无 fallback**（tasks.yaml:408-418,1662-1672），台账 §2.2-A 明列两者断流=真损失 | tasks.yaml:22-95,408-418,1662-1672；akshare_provider.py:230；migration-ledger §2.2-A | P1 | 停 QMT 跑 5 任务验证 fallback 生效；9/19 看 kline_etf_daily 表断更 |
| B | **kline_sector_incremental 依赖 industry_class_refresh（weekend_calibration）——跨时段名义边**：无强制（task_queue.py:150-164）；实际影响小（行业分类周更日更差可容忍），登记在案 | tasks.yaml:877；task_queue.py:150-164 | P3 | — |
| A | **daban_engine_load_daily（本族）←daban_board_event_derive（weekend_calibration 周一03:00）"日消费←周生产"错配（系统发现 S5）**：装载任务注释自述"trade_date=打板事件日=决策日 T 的 T-1，T 日盘前消费"（tasks.yaml:3282），但事件派生仅周窗重放（tasks.yaml:1581）——周二至周五的 T-1 事件在派生表中缺失，消费侧 `max(trade_date) < as_of` 只能取到上周事件（daban_load_producer.py:134-141）。跨时段依赖被 task_queue 自动视为满足，无任何告警 | tasks.yaml:3279-3290,1578-1589；daban_load_producer.py:134-141；task_queue.py:150-164 | **P1** | 周三查 daban_board_event 表 max(trade_date)（预期停在上周一）vs daban_engine_load 当日产出的事件日 |
| A | 图形认证链 DAG（pattern_event→win_rate_materialize→evidence_certify→weight_sync）同时段串联+禁 cron 自轮询（tasks.yaml:3220,3246,3271 注释）——与"reconciler 事件触发"宪法 §9.3 同构，链路设计核对通过；首环依赖 kline_daily_incremental 落库 | tasks.yaml:3214-3276 | 已查无 | 断首环看链尾 BLOCKED |
| B | internal 派生 8 任务无副源（显式置空）——上游 kline_daily 断供时全部静默产出空/旧窗（0 行交易日 WARN 兜底+看门铃）——传导链已声明依赖（dependencies 均挂 kline_daily_incremental），DAG 在同时段内强约束，兜底充分 | tasks.yaml:632-658,2153-2166,3081-3093 | P3 | 断 kline_daily 跑 technical_indicator 看 0 行 WARN |
| D | kline_weekly/kline_monthly 停用理由="100% 由 local_qfq 通道喂数"（tasks.yaml:272-286）——local_qfq 通道不在 tasks.yaml/scheduler 注册域，属"表有数据但任务清单外供给"的影子通道，审计可见性弱（checklist #8 邻接） | tasks.yaml:272-286 | P3 | grep local_qfq 生产调用方 |
| E | 停用任务（global_hsi/nikkei/kospi/usdcnh）disabled_reason 如实（capability 未入 provider/源死），首采数据留痕清晰——假完成状态风险低 | tasks.yaml:3165-3212 | 已查无 | — |
| F | 受阻（未检索）。复权因子增量+后复权聚合属 A 股标准做法；EQW_ALLA 等权指数基期 2019-01-03（tasks.yaml:3092）为项目自定 | tasks.yaml:3081-3093 | 受阻 | — |

## 3 SOTA 对照
- 受阻。日K/复权/估值管线为成熟范式；看门铃（当日标的数 vs 中位偏差）属项目原创防线，立卡候选（推广到 kline_index/technical_indicator 等表）。

## 4 缺陷清单
1. **P1 daban 日消费←周生产错配**：修法=①daban_board_event_derive 移入 daily_kline 时段（周窗重放幂等，日跑成本可承受）或②daban_engine_load_daily 明示接受周频事件并改注释（去掉"T-1 消费"承诺）→验证法=改后周三核对两表 max(trade_date) 同步推进。
2. P1 kline_etf_daily/kline_cb 无 fallback：桥 universe 含基金（台账 §8.5），评估 ETF 日K 走桥/akshare 基金 K 线兜底。
3. P3 local_qfq 影子通道登记（或纳管为 internal capability）。

## 5 挂起疑问
- adj_factor 主备口径（miniqmt dr 行 2026-07 起 vs akshare 全史）在 fallback 长期接管下的合并正确性——需要数据画像（2026-07 前后窗口 dr 值对拍），材料缺项未做。
- kline_sector_880_resample 的 DELETE+INSERT 幂等（tasks.yaml:2288）在 16:30 与 880 增量任务串行依赖已声明——并发竞争已由 dependencies 治理（tasks.yaml:877 注释 09-14/09-15 竞争实证），复检建议收口方跑一周验证。

## 6 完备性自评
六轴全查（F 受阻）。长尾：31 任务中 pattern 链四件与 internal 计算的数学正确性属 P1 决策链审查范围（本族只审调度/配置一致性，数学轴移交 p1_decision_chain 班次）；hfq 复权因子数学未复算。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
