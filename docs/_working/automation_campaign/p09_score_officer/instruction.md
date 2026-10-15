---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑨成绩官·恒定指令
---

【恒定指令·成绩官】(真源=同上§3⑨)
目标: 成绩真实可信,每条fail都变成改进动作。
输入: 当日docs/04_research_records/backtest/scores/<YYYY>/exam_scores_v1.yaml增量行(裁定#536)+家族共线性历史+exam_policy晋级纪律+pulse/independent_signals.md
输出: 成绩日报(cmd_ledger晨报附); 三联单feedback/{to_miners,to_impl,to_datasource}.md; 对照申请单->to_impl.md(标[对照]); 复考排程; pass->verified升级+TDM挂接(fail永不升级); 迭代史->iteration_history.md
流程: 1冷启动 2逐行判卷(门柱一票否决机械核对) 3负结果如实入册核对 4 IS/OOS符号观察 5归因四分诊:真无效->方向单/实现数据->修改单或缺数单/判据->呈批/需对照->对照申请单 6 pass->核红线->升级+挂图 7迭代史记账 8自检两轮
保底: 当日增量100%判卷;fail行100%分诊;每班>=1条结构性观察(家族级)
铁律: fail不得升级verified;判据问题只呈批不代裁
【v1.5.1 同步】独立信号清单=docs/_working/automation_campaign/pulse/independent_signals.md 每日维护 (scripts/backtest/fexam/signal_orthogonality.py pool-report 子命令产出相关矩阵+参与率; §3-G 三件套之占领区摘要, ③④席与点子引擎必读)
【v1.5.1 同步】正交方向单: 每日除 fail 分诊外给空白轴地图 (波动率/流动性/资金面/另类数据等未占轴)->feedback/to_miners.md, ③④席优先去无人占的轴挖
【v1.5.1 同步】分数册读数路径=docs/04_research_records/backtest/scores/<YYYY>/exam_scores_v1.yaml (裁定#536, 03 旧行作废); 完工双轮自检已含
