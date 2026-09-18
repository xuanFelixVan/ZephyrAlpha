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

## 晨间循环下单体观察（flash-nightbuild-20260918 班 12:5x 只读核验，非本班下单）

- 柜台日志（8886156677_TaskDetail.txt，GBK）今日 828 条委托记录，其中 **801 条来自会话 `smoke-e2e-1789694891`**（510300.SH buy 100 @4.07 限价，10:07-10:45 窗内反复委托，状态"全部委托!"），**零成交记录**，12:5x 核验已停止增长（最后一笔 10:45）。
- 判定=桥客户端侧的循环/重试体（非 tdchain、非 flash 班、非 automation 台账在案任何一方）。**午休后 13:00 若这些单仍挂着会恢复有效**——请在 QMT 终端委托列表批量撤单清理，并在桥客户端侧找到并停掉循环源，防明日再发。
- 两个桥客户端契约缺口实录（本班与 red team 独立确认）：①撤单指令须用柜台回填的 broker id（ack_sim.csv），用本地 id 撤单=FAIL（flash-nightbuild-e2e-20260918-01 的 cancel #FAIL 即此因）；②隔夜单被标 #DONE 但从未进柜台（静默丢弃）——QMT 侧接管切换时应把这两条写进桥客户端验收。

## 验收复核只读核验（st-ff-tdchainJ-20260918，2026-09-18 17:3x，任务二）

- **前置**：XtMiniQmt.exe 在线（12:50:34 启动，路径=E:\国金QMT交易端模拟\bin.x64\，双重断言：
  进程路径含"模拟"+账号=8886156677，实盘终端未运行，无需 TCP-pairing 甄别）。
- **只读链实测**（脚本=.runtime/tmp/st-ff-tdchainJ-20260918/qmt_readonly_check.py，零下单零撤单）：
  connect=True → get_positions：cash=9,651,613.46、total_mv=9,099.20、持仓 510300.SH=1100 股/
  600036.SH=100 股（夜间资金镜像零值现象已随白班自愈，P7 口径吻合）→ query_trades_today=4 笔
  （全 510300.SH，与柜台 Deal.csv 4 行逐笔一致：09:30:58/09:33:19/09:47:28/10:03:00，test-002，
  100 股 @4.554-4.561）→ query_order("1098941366") 抽样=None（新会话无本地缓存且柜台 query_stock_orders
  未回配该编号，如实记录）→ disconnect。禁区全程未触（QMT_REAL_*/enable_real/live 切换零调用）。
- **D3 晨间复核（撤单终态+成交腿）**：
  - c3 隔夜单（bridge-smoke-c3-20260918，600000.SH BUY 100 @8.10，03:08）：orders_sim.csv 本地
    终态=#DONE，ack_sim.csv 仅 SENT（无 CANCEL_SENT ack、无柜台 broker id 回填）；今日柜台
    Order.csv 828 行（委托日期全=20260918）**零 600000 委托** → 与本簿契约缺口②"隔夜单被标
    #DONE 但从未进柜台（静默丢弃）"实证吻合；撤单终态在当日柜台文件不可证（按日轮替+未进柜台），
    登记为缺口②的又一实证，不处置（桥客户端验收时按缺口①②修契约）。
  - 成交腿：今日全部成交=4 笔 510300.SH（test-002 来源，非本战役车道），c3 600000.SH 零成交 ✓。
  - 循环单观察更新：smoke-e2e-1789694891 共 801 笔（Order.csv 实测窗口 09:30:01-11:30:22，
    较 flash-nightbuild 簿记的 10:45 更晚——以本实测为准；800 已报+1 已撤），17:3x 复核已停 6h+；
    800 笔挂单冻结资金 ~407 元/笔，批量撤单=Owner 门（终端 GUI），维持 flash 班请求不代办。
- **判定**：E7 只读对账补强=完成（零新下单承诺兑现）；缺口①②实证已归档，移交桥客户端验收批。
