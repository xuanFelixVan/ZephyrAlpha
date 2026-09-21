---
ttl: task_bound
title: 深度审查作业簿——轮动序列追踪（已审）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：轮动序列追踪（P15）— GLM-5.3-Flash / st-deeprev-20260918

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件基线后零漂移）
- 审查者: GLM-5.3-Flash/st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/sector/sector_divergence.py`
- TDM 节点: TDM-E-L2-02
- 生产调用方: boundary_revision_engine / llm_premarket_analysis / multi_indicator_divergence / sentiment_price_divergence（grep 实证，活件）；docstring :5 "（MVP 阶段无）"已过时（文档漂移 P3）
- 测试文件: tests/signal_ashare/sector/test_sector_divergence.py（合批 81 passed）

## 1 对象快照
MOD-SIG-060 全文件（1141 行）：四件套（5 状态消费接入/电风扇速度计/个股分歧度/SEC-03 概率标定）+ 族相对强度雷达。重降级纪律（各维独立降级 notes）。排除项：sector_rotation_state/sector_siphon（P19-P21 域，本件消费方）。测试实跑通过。

## 2 六轴审查日志表
| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 速度计 mean(\|rank_t−rank_{t-5}\|)/共同票数正确；_midrank_percentile 中秩分位（并列平均秩，bisect 实现正确）防大量并列低分误纳；分歧合成 0.4z+0.3+0.2+0.1 权重和=1 | :334-355,501-527,756 | 已查无 | 手算 4 值截面分位对拍 |
| A 深度 | `_disp_signal` 负收益语义洞：ret_today < ret_prev×0.5 在 ret_prev<0 时（前日跌）当日跌更深也计"放量滞涨"——领涨板块连续下跌场景误触发 | :446-450 | P3 | 造 ret_prev=-0.02/ret_today=-0.015 看 disp=1 |
| A 深度 | 标定器 n=max(len(r3),len(r5)) 混窗计数：3 日观测 25 样+5 日 30 样 → n=30 判 sufficient 但 freq3 仅 25 样 | :906-917 | P3 | 造两窗样本差 >5 观察 sufficient=True |
| A 边界 | 双池/宇宙守卫齐：可评分宇宙<30 不出清单；速度计分位窗<60 降级；虹吸历史<2 降级；当日成交额全 0 降级 | :514-526,600-601,741-742 | 已查无 | 各守卫边界造点 |
| A A股 | 炸板=触板(high≥limit_up−0.005 容差)未封(close<limit_up−容差)——**与 P09 炸板口径（无容差）同族两套**，边界票计数可差（两处均有文档声明但无双真源仲裁） | :738 vs rpt_p09 :76 | P3 | 边界价 high=lu−0.003 两模块对拍 |
| B 上游 | 成分 SCD-2 时点过滤（PIT）；money_flow 缺行→按 0（缺数据板块中性化，缺失率无透出）；kline_sector_880 仅 ~52 日历史（文档实证声明，250 日窗常态降级=设计内） | :131-135,46-61 | P3 | — |
| C 下游 | 四消费方实存（见头）；top_risk_flag 供 M2 降档触发——flag 误发直接降仓（爆炸半径=仓位档位）；watchlist=禁新开仓注解 | grep 实证 | 已查无 | grep 复跑 |
| D 旁系 | 消费接入而非重复实现（sector_rotation_state/sector_siphon import 复用——正例）；seat_registry 一线游资集合与 056/057 白名单三处承载（{龙头连板,首板} 字面量在本件 ：650 再现——三承载 checklist #4） | :77-96,650 | P3 | grep "龙头连板" 全仓计数 |
| E 对抗 | 五问：①各维异常独立降级 notes 全留痕（良好范式）②registry 空→对打全 False 静默（notes 有留痕）③无监控面 ④重跑幂等（纯读）⑤trade_date=None 取最新数据日（PIT 数据日口径正确） | :1066-1093,970-979 | 已查无 | — |
| F 新鲜度 | **已检索**（RRG/轮动族共享，见 rpt_p16 轴 F）：RRG 四象限方法学（StockCharts/Kempenaer）；电风扇速度计=国泰海通 2026-08 卖方口径（中文研报来源，符合政策"中文研报不算盲区"）；结论：对等已有（速度计为卖方定制口径的忠实实现，无独立 SOTA 对照） | https://chartschool.stockcharts.com/table-of-contents/chart-analysis/chart-types/relative-rotation-graphs-rrg-charts | — | — |

## 3 SOTA 对照
电风扇速度计：对等已有（国泰海通 2026-08 中文卖方口径）；RRG/5 状态消费侧对等已有（见 rpt_p16）。

## 4 缺陷清单
1. P3 disp 负收益语义洞。
2. P3 标定器混窗计数。
3. P3 炸板口径与 P09 双承载（容差差异）。
4. P3 一线游资白名单三处字面量承载。
5. P3 docstring 消费方声明过时。

## 5 挂起疑问
- kline_sector_880 仅 52 日历史：SEC-03 标定器 sufficient 短期恒 False——数据积累到 250 日前的过渡期消费策略需 Owner 确认（当前 state_conditional_stats 仅注解，未接门控，风险可控）。

## 6 完备性自评
六轴全查（超长文件逐段过，SQL/加载层全读）。长尾：_compute_siphon 聚合内 detect_siphon_state 内部数学归 P20 域复审；analysis_utils 辅助函数（daily_returns/lead_streaks）未逐行验算（多模块共用件，建议独立对象）。
