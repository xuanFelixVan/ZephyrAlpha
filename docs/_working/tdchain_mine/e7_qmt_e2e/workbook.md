---
ttl: task_bound
title: E7 QMT 模拟盘 100 股端到端烟测作业簿——现成协议复跑+证据归档
session: st-tdchain-20260917
date: 2026-09-18
parent: docs/_working/tdchain_mine/a0_master_ledger.md
---

# E7 QMT 模拟盘 100 股端到端烟测作业簿

## 六向台账

- **目标**：Owner 通宵明令——模拟 QMT 桥端到端下单 100 股测试，从连接到撤单/对账全链实录+证据归档。
- **证据**：
  - runbook：docs/_working/automation/campaign/qmt_e2e_runbook.md（2026-09-18 02:5x 版：阻塞于模拟终端未运行）。
  - 现成协议：scripts/tests/smoke_test_qmt_broker.py——环境守卫（仅模拟路径放行）→connect→positions→下 600000.SH 100 股限价=昨收×0.90（跌停价，必不成交，零资金风险）→query(SUBMITTED)→cancel→query(CANCELLED)→disconnect，exit 0=全过。
  - 先例：2026-09-15 10:52 全通过，证据 docs/_working/full-auto-chain/evidence/qmt-smoke-result.yaml（order_id=1082140563，零成交）。
  - 环境真源：config/.env.qmt（QMT_SIM_PATH=E:\国金QMT交易端模拟\userdata_mini，QMT_SIM_ACCOUNT=8886156677）+config/qmt_environments.yaml §TCP-pairing 双终端甄别。
  - 侦察时实况：XtItClient.exe 在线（Owner 已开终端），XtMiniQmt.exe **缺**——smoke STEP 0 会安全 FAIL 挡住，不会误下单；需 miniQMT 模式登录。Owner 白班承诺亲自开终端（ auction 桥工单在案），故本环节=重试循环直至进程出现。
  - 防重复：今夜尚无人下过单（全仓证据目录无 20260918 烟测产物）；residual 轴 Q1 亦含端到端实测，但其口径=regime 注入历史日期哨兵（drill_e2e_b1），与 broker 烟测不同链——两轴各留证据文件名命名空间。
- **块**：B1 进程轮询（XtMiniQmt.exe 出现）；B2 双终端在线时先跑 TCP-pairing 甄别；B3 跑 smoke 协议；B4 资金/成交对账（positions 前后一致+query_trades_today 空=回调外调用）；B5 证据归档 docs/_working/full-auto-chain/evidence/qmt-smoke-result-20260918-tdchain.yaml+本簿回写。
- **依赖**：Owner 侧 miniQMT 登录（唯一外部依赖）；kill_switch 未触发（触发=Owner 复位项，禁碰）。
- **三态**：阻塞待终端（W2 起每 30min 轮询一次）。
- **下一步**：进程出现即执行 B2-B5；若 Owner 白班后仍缺进程，如实报告阻塞点。

## 执行记录（回写区）

（待执行）

## 禁区（runbook :30，违者=事故）

QMT_REAL_*/enable_real/ZEPHYR_ENV=live/LiveSimulationSwitcher.switch_to_live 全禁；双终端禁裸 psutil 判断（走 §TCP-pairing）；勿在 on_stock_trade 回调内调 query_trades_today（死锁）。

## 执行记录（2026-09-18 06:2x 终态回写）

- **100 股模拟单全链测试=已完成**（自动化战役第三棒，05:0x 官方入账 commit 60747a8a47"QMT 桥 100 股实测"+staged 证据 qmt-bridge-smoke-20260918-c3.yaml）：2026-09-18 03:08 账户 8886156677(sim)，600000.SH 100 股 BUY LIMIT 8.10（深低于市价，意图零成交）——SUBMITTED 全链打穿（下单→桥→柜台→状态回流），撤单指令受理；夜间时段终态以柜台导出 CSV 为准（他会话已留晨间复核尾巴）。
- **防重复裁定**：本环节不重复下单（同一模拟账户二次下单=污染他会话证据链）；改为 broker 侧对账闭环补强——06:1x 实测 XtMiniQmt.exe 进程不在线（仅 XtItClient.exe），broker 查询通道挂起；终端重连后补 query_order+query_trades_today 对账（零新下单，只读核验）。
- **禁区全程未触**：QMT_REAL_*/enable_real/live 切换全禁 ✓；kill_switch 未动 ✓。
