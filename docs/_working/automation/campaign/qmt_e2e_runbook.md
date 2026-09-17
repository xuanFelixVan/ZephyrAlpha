---
ttl: task_bound
completes_when: 模拟终端启动后 Owner/会话执行本手册并归档第三棒烟测证据
---

# QMT 模拟盘 100 股端到端测试执行手册（第三棒备妥版）

> 状态（2026-09-18 02:5x）：**阻塞于模拟终端未运行**（tasklist 零 QMT 进程；miniQMT 启动需 GUI 登录，密码不落盘属 Owner 四类事，AI 禁代做）。终端一开，照本手册 3 分钟完成。

## 背景

- 现成协议：`scripts/tests/smoke_test_qmt_broker.py`（2026-09-15 10:52 首次全通过，证据 docs/_working/full-auto-chain/evidence/qmt-smoke-result.yaml：600000.SH 100 股跌停价限价买→SUBMITTED→撤单→CANCELLED，零成交零资金风险）。
- 第三棒目标：复测（终端重启后环境可能变化）+ 归档第三棒证据。

## Owner 步骤（唯一人工动作）

启动模拟 miniQMT 终端并 GUI 登录：`E:\国金QMT交易端模拟\bin.x64\` 下启动（miniQMT 模式）。

## AI 执行序列（终端登录后逐条）

1. **环境辨识（双终端在线必做）**：
   `powershell -Command "Get-Process | ? {$_.Path -match '国金QMT交易端模拟'} | Select Id,Path"`
   ——确认模拟终端在跑；若实盘终端（国金证券QMT交易端）也在跑，须按 config/qmt_environments.yaml §TCP-pairing（tick_subscriber._identify_qmt_peer_via_tcp）确认实际 peer 是模拟端，否则 STOP。
2. **跑现成烟测协议**：`python scripts/tests/smoke_test_qmt_broker.py`（自载 QMT_SIM_*，跌停价限价买 600000.SH 100 股→SUBMITTED→撤单→CANCELLED→断开，exit 0=全通过）。
3. **归档证据**：产出 yaml 至 `docs/_working/full-auto-chain/evidence/qmt-smoke-result-20260918-c3.yaml`（照 09-15 格式，finished_at/结果/异常全录）。
4. **成交腿（可选，Owner 门）**：仅交易时段（09:30-11:30/13:00-15:00），限价改市价附近（prev_close）→status 52 FILLED→get_positions 增持 600000.SH 100 股→**当日不可卖（T+1）**，仓位留在模拟户为凭。

## 禁区（照抄侦察报告）

QMT_REAL_*/enable_real/ZEPHYR_ENV=live/LiveSimulationSwitcher.switch_to_live 全禁；双终端在线禁裸 psutil 判断；勿在 on_stock_trade 回调内调 query_trades_today（死锁）；勿无 touch_tick 接线开 heartbeat；kill_switch 触发属 Owner 复位项。
