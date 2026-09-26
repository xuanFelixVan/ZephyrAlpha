---
ttl: task_bound
session: st-ec2-p0
---

# 99_skipped_for_owner — Owner 门位登记（EC2 车道）

> 纪律：资金/净删/production 流转/flag 出厂翻转/人工报送=Owner 门位，车道只登记不代裁（宪章 §二.6）。

## SKIP-1 · F62 合规门接线（C-002 三门+C-004 三闸 12 件零注入）

- **判定**：Owner 门位，登记跳过（EC2 九项销账之 F62）。
- **现态证据（2026-09-27 复核）**：
  - `grep -rn "OrderManager(" src/zephyr scripts --include="*.py" | grep -v test` = 6 处裸构造全在
    （qmt_trading_session.py:115 / qmt_file_bridge_integration.py:52 / app_panel.py:524 /
    start_paper_session.py:492 / construction/demo_e2e_pipeline.py:326 / construction/qmt_bridge_regression_smoke.py:230）；
  - compliance_report_registry.yaml `broker_ack: false` ×6、`broker_ack: true` ×0——报告从未报送；
  - `ProgrammaticTradingGuard(` 非测试命中=仅自身 :278 示例。
- **为何 Owner 门**：接线顺序强约束（m7_live_execution/06_compliance_gates.md B1）——
  ReportGate 接线即生效，而 6 项义务 broker_ack 全 false→第一笔单即 BLOCK（fail-closed 正确）。
  正确序列=**Owner 先走券商人工报送程序化交易报告→人工回填 YAML 确认位→再接线**；
  人工报送=外部周期动作，工程侧不可代行。当前未实盘（S-1 锁），无在险违规。
- **移交**：Owner 报送完成后，工程侧接线（assemble_session 注入三门三闸+monitor 同实例、
  programmatic_trading_guard 挂 live 档）按 B1②③ 处方施工，1-2 天，G5 实盘准入前必闭。

## SKIP-2 · F74 堵点3（唯一人工门带外通知通道）

- **判定**：Owner 门位裁定项，登记跳过（03_promotion_gate.md §五堵点3）。
- **现态**：飞书/SMTP 09-15 裁撤后通知唯一出口=前端 #promotion 页横幅+data/failures/ 落文件；
  Owner 不开屏=建议无限期滞留（fail-safe 但无人知）。
- **为何 Owner 门**：补邮件/死件开关/晨报承接三选一=触达通道裁定（Owner 自身触达面）。
- **移交**：裁定后 F74 方可宣 built（本役已修堵点1/2，剩④处女链彩排随首自然班次）。
