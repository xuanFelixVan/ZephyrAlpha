---
ttl: task_bound
session: st-dloop-20260921
issue: DLOOP-V2-OWNER-GATES
completes_when: Owner 逐项裁定后本清单归档（每项批了才动）
---

# Owner 门位清单（丁线申请单）——只出单不代批

## A. 日循环挂任务表批（缺口①收尾件）——✅ 已批（Owner 2026-09-21）已施工
- **原申请**：将日循环总扳手挂入 tasks.yaml/schedule.yaml（建议时点 16:45 盘后带，daily_kline 落地后；
  事件链已覆盖 9 棒，本扳手=补 warroom 棒+全链体检兜底）。MANUAL-ONLY-PERMANENT 门禁合规
  （不设 argparse，编程式入口，编排器同款先例），挂表形态建议=internal 任务行包装
  `run_daily_loop(None)`。
- **理由**：对账实证 warroom scenario_plan 族是唯一零接线棒（prediction_log 0 行）；其余棒已在
  事件链上。挂表=排期表动作，按裁定#388 口径归 Owner 门位。
- **不批的后果**：warroom W0 样本（20日窗）无法积累，Brier 校准闭环永远空转。

## B. regime 供需阈值错位治本批（对账 §4 头号病灶）——✅ 已批（Owner 2026-09-21）已施工
- **原申请**：`fw_backtest._REGIME_STALE_DAYS` 3→1（对齐编排器 D1 消费方口径）；
  或反向放宽 D1 至 3 日——二选一，必须闭合。涉及文件 `src/zephyr/strategy_pipeline/fw_backtest.py`
  （非丁线写域，故出申请单）。
- **实证**：调度器日志 09-17/18 三条"刷新体检 action=fresh 滞后=2/3日"零印制 vs 编排器
  同日 regime_missing no_trade——供给方说新鲜、消费方说缺失的死亡窗口。

## C. 路由表 config 落地批（缺口④）
- 六段↔五态映射口径（routing_table_v1_draft.md §1，含 ignition/euphoria 拆分阈值待拍板）；
- TDM-E-L1 三空格（ignition/euphoria/distribution）填格=资金分配门位（R41 词表）；
- 60% 硬顶/过渡带系数定稿（蓝图 proposed 项）。

## D. 策略卡 1、2 立卡批（Owner 愿景映射件）
- 卡1「300ETF 波段+底仓 T」、卡2「regime 切换器」按 2026-09-16 映射表待立卡；
- 立卡后走 S-OWNER 考试链毕业→喂入 GRADUATED_PACKAGES（禁手填，#305 第2点）——
  这是编排器从"今日不出手"安全态解除的唯一合法路径。

## E. 模拟盘部署批
- 整装回测 0 次未跑（#388 语境）；模拟盘三步进阶待批（币圈 7×24 捷径在案）。

## F. pf_alloc 生产接线批（如按 #257② 口径需确认）
- 对账实证：pf_alloc **已在事件链接线状态**（09-18 alloc-2026-09-18-82cb50 真实落地），
  缺口⑤的"接线"条件已满足，本项=确认无需再做，非新申请。

## G. 中毒行修复确认批（本班操作透明化）
- judgment_daily_plan 3 行 eval_method=unresolvable(verification_missing) 为**时序债疤**：
  row1=周五自动结算先于验证（非本班）、row2=本班手动结算跑在验证前（自伤，已认）、
  row3=本班修订行同因。修复=已按台账修订语义补发未结算修订行 01M30BBDM6KB14HZ4H5TKZNF08
  （今晚验证+结算落于其上）；中毒行保留作疤不 DELETE（零破坏）。
  若 Owner 判需物理修复（清 evaluated_at），属结算列写权限新授权，另行裁定。

## H. 周计划任务带观测移交
- pending_events.jsonl 存 2 条 09-16 c4_batch_due（85 件 C4 批）滞留未消费——非丁线写域，
  移交 C4/任务卡线核查消费端是否存活。
