# 判定书：VAL-P0-20260912-154118

对象/节点：BT-P0-001（TDM-E-L1-AGG 输入重建——印教材）｜ kind=VAL ｜ 窗口=2019-01-01~2026-09-12 ｜ 成本口径=rough（不适用）
结论：verdict=done（教材印制完成，非研究结论）｜ significance=ok ｜ verdict_reason=method_not_applicable（本 run 为数据准备，区分度检验在 P0-001 检验批）
判定链：SOP-B ③缺口取数完成即归档；本 run 不下策略/判定结论。

关键数字：
- 落库 1809 行 → c1_backtest.regime_snapshot_history（CH_COMMITTED 确认）
- 七态分布：r1 30.8% / r2 16.4% / r3 28.1% / r4 13.2% / r10 11.1% / r11 0.1% / r12 0.3%
- 最长连续同态 79 天（<250 锁死警戒线，G07 式路径依赖不存在）
- 概率行和=1 零违例，NaN=0；Shrinkage 均值 0.874（EMA α=0.15）

遗留问题：
- confidence_signal/risk_signal 分量列暂为 NULL（builder.schedule 接口不暴露分量；P0-002 需要时扩展）
- 本 run 为 dry-run 崩档两次重跑的第三次（153430/153707/153922 空档已清，失败原因=脚本字段 bug，非数据问题）

台账回执：verdict_ref=c1_backtest.regime_snapshot_history run_id=VAL-P0-20260912-154118
