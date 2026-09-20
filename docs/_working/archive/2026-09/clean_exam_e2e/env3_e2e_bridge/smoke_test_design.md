---
ttl: task_bound
title: 100 股模拟盘冒烟测试设计（QmtFileBridgeBroker 全链路，只设计未执行）
owner: ZephyrAlpha-Owner
session: st-cleanexam-20260918/C
date: 2026-09-18
status: design_ready
safety: |
  本文件=设计稿。执行留施工阶段。零实盘接触设计；委托仅发往券商模拟账户
  8886156677（E:\qmt_bridge_sim\ 文件桥），任何分支不得构造实盘路径参数。
---

# 100 股模拟盘冒烟测试设计（信号→下单→成交/废单终态→台账）

> **定位**：验证"委托→沙箱→柜台→回报→镜像"活体链路，为执行面通电（编排器 BT-P1-031 未来接入）提供前置证据。**不是**策略信号测试（信号侧 v1 只出声不出手，见 00_env_mining.md §1-B5）。
> **先例复用**：scripts/construction/test_qmt_file_bridge_e2e.py（装配/提交/轮询/撤单骨架，510300.SH 100 股）+ scripts/tests/smoke_test_qmt_broker.py（跌停价申报法：`prev_close×0.90`=笼子豁免+必不成交+随时可撤+**闭市时段同样合法**，2026-09-15 盘中实证）。
> **执行状态注记（2026-09-18）**：段一已按本设计 executed 2026-09-18 03:1x——结果 7 PASS + 1 FAIL（FAIL=P7 资金断言：夜间柜台镜像 Account.csv 零值，mtime 2026-09-17 20:50 官方导出夜间不刷新所致，证据在案）；留痕见 seg1_execution_log.md。段二脚本已按本设计写好，待 09:15 交易时段执行。

## 1. 标的与委托参数

| 项 | 取值 | 依据 |
|---|---|---|
| 标的 | `510300.SH`（沪深300ETF） | 先例同款；流动性顶级；ETF 最小申报=100 份整手（board_lot 真源） |
| 方向/数量 | BUY 100（买入侧零 T+1 锁定纠缠；卖出需先有持仓+可用量断言，多两层前置） | 最小可交易单位 |
| 委托类型 | LIMIT（pricetype=limit） | 文件桥 7 列指令仅 limit/latest 两态；限价可控 |
| 委托价 | `prev_close × 0.90`（跌停价，quantize 0.01） | 跌停价申报=价格笼子豁免（smoke_test_qmt_broker.py:191-195 实证注释）；ETF 涨跌幅 ±10%，跌停价合法；买在跌停=必不成交=零成交扰动；闭市时段申报合法 |
| idempotency_key | `smoke-e2e-<UTC 时间戳>` | broker 幂等闸（qmt_file_bridge_broker submit_order 首查） |
| strategy_id | `smoke_bridge_e2e` | 回报/镜像里可 grep 定位本单 |

prev_close 获取：xtdata 断供（miniQMT 退役），改读 CH `c1_market.kline_etf_daily` 最新收盘（DatabaseService 只读），或 quote.csv 首行昨收列（29 列契约）——施工时二选一并留痕。**禁止**用魔法常数。

## 2. 前置断言清单（全过才许进段二下单步）

| # | 断言 | 验证方法 | 预期 | 失败处置 |
|---|---|---|---|---|
| P1 | 模拟终端进程在跑且是 sim | `Get-Process XtItClient` 比对 Path 含 `国金QMT交易端模拟`；枚举确认**无**实盘目录进程 | 恰一进程、路径含"模拟" | 中止（EXIT_ENV）。出现实盘进程→按 qmt_environments.yaml 双终端协议改用 TCP 配对法（tick_subscriber.py:979 可复用）锁定行情对端后**仍中止下单**，转人工 |
| P2 | 账户=模拟账户 8886156677 | 读 config/.env.qmt QMT_SIM_ACCOUNT；断言 `!= QMT_REAL_ACCOUNT(8887871993)`；断言 broker.ENV_CONFIG["sim"].account==8886156677 | 三方一致 | 中止（EXIT_ENV） |
| P3 | 环境文件只读校验 | 读 config/qmt_environments.yaml：sim 槽 blocks_live_trading=false 且 live 槽 account 为空串（未启实盘） | 一致 | 中止（EXIT_ENV，live 槽非空=实盘已立项，需 Owner 重审本设计） |
| P4 | HTTP 桥活 | `Test-NetConnection 127.0.0.1 -Port 18901`（或 broker._http_post_order 探活语义只读版：对 /health 的 GET 不触发下单） | True | 不中止：自动走文件桥降级路径（93 §12.5 实证可补消费），降级事实留痕 |
| P5 | 交易侧熔断未触发 | 实例化 trading_kill_switch（trading_contracts/risk/trading_kill_switch.py:119 trigger 侧只读检查——查五级状态无一 active） | 无 active | 中止（EXIT_RISK）。注意：**不用** zephyr.security.access_control.kill_switch（agent 级、纯内存态，与资金无关——kill_switch.py 头注 P1-2 澄清） |
| P6 | 桥目录可写（broker.connect 的自有语义） | assembly.connect_all() 返回 dict["qmt_sim"]=True（内部含 .rw_test 读写探针+同步线程启动） | True | 中止（EXIT_CONNECT） |
| P7 | 资金充足 | broker.get_positions()（直读 Stock\Account.csv 镜像）cash > 委托金额×1.2 | True | 中止（EXIT_FUND） |
| P8 | 时段感知 | 本地时间判定：09:15-15:00 交易时段→段二全流程；否则→段一只跑（P1-P7+可选预埋单变体） | — | 非时段不下单（默认），或按 §4 变体 B 显式选择 |
| P9 | 无同标的历史残留单 | CounterStateMirror.pending_count("510300.SH", BUY)==0 | 0 | 先撤残留或中止（EXIT_DIRTY），防串单 |

## 3. 执行步骤（两段式）

### 段一（任何时段可跑，零委托）
```
S1 P1-P3 环境三断言（进程/账户/配置只读）
S2 P4 探活：GET http://127.0.0.1:18901/health（沙箱 EXEC 内建，只读）
S3 P5-P6 熔断检查 + assembly.assemble()/connect_all()（enable_real=False 显式传参）
S4 P7-P9 查资金持仓镜像（get_positions + pending_count）
S5 读 prev_close 并打印拟委托价（不下发）
S6 assembly.disconnect_all() 收尾，输出段一 PASS/FAIL 摘要
```

### 段二（交易时段，P8 判定通过后）
```
T1 段一 S1-S5 全重跑（断言有时效性）
T2 下单：order_manager.create_order(symbol="510300.SH", side=BUY, LIMIT,
      quantity=100, limit_price=跌停价, broker_id="qmt_sim")
   → order_manager.submit_order(order_id, broker_id="qmt_sim")
   验证1：返回本地 order_id；E:\qmt_bridge_sim\orders_sim.csv 或 ack_sim.csv
      在 10s 内出现本单行（HTTP 快路径 32ms/文件 5.7s；8s 无 ack=HTTP 丢请求，
      客户端须重写文件通道——93 §12.5 防御语义在 broker 内置，脚本只验证终局）
T3 轮询柜台同步（每 3s，上限 90s）：
   order_manager.get_order(order_id) 等 broker_order_id（柜台 sysid）回填
   验证2：status 从 SUBMITTED 推进（柜台镜像 _COUNTER_STATUS_MAP 全量六态可辨）
T4 终态等待（跌停价买单预期=永不成交，终态应经撤单产生；若 09:30 前柜台对
   非时段单返回"废单"，废单同样是合法终态——两态都算 PASS，如实记录命中哪态）
T5 撤单：order_manager.cancel_order(order_id) → 轮询 90s 等 CANCELLED
   验证3：终态 ∈ {CANCELLED, REJECTED}（若意外 FILLED：立即进入 §6 应急）
T6 台账验证（链路终点）：
   a. Stock\Order.csv 含本单 sysid 行、Stock\Deal.csv 无本单成交行（未成交预期）
   b. CH 侧执行报告表 c1_market.execution_report **预期无行**（E4 断点：生产者
      未接线——如实验证"断点仍在"并留痕，防误报链路已闭环）
   c. 若施工阶段同期接线了 execution_report 写入（断点 2 已修）：断言出现本单
      聚合行（order_id/actual_quantity=0/broker_id="qmt_sim"）
T7 清理：disconnect_all()；打印终态/回执/镜像三源对照摘要；EXIT_OK
```

## 4. 非交易时段行为与变体（诚实的不确定点）

- **已实证**：跌停价限价单"闭市时段同样合法"（旧 miniqmt 通道 2026-09 实证注释）；文件桥沙箱冻结期"HTTP 成功不响应→2s 超时降级写文件→沙箱复活补消费"（93 §12.5，12:04-13:00 实证 4 笔）。
- **未实证（本设计不假装知道）**：大QMT 柜台对**非时段**收到的文件桥单，是排队为预埋单（开盘转已报）还是直接废单——两者都是可接受终态，段二 T4 已把两态都纳入 PASS 集合。
- **变体 A（推荐，默认）**：tonight 只跑段一；09:15 后跑段二。零排队不确定性。
- **变体 B（tonight 激进版，需 Owner 点头）**：tonight 段二 T2-T3 跑到"柜台回执/文件指令受理"即止不撤单，留单过夜，09:15 后续 T4-T7——把"非时段柜台行为"变成活体实证。风险=单据过夜悬置（模拟资金，零真实风险）。

**段一 P7 补充（2026-09-18 03:1x 实测后新增认知，不改断言逻辑）**：夜间/非时段窗口 Account.csv 官方导出不刷新（本例 mtime=2026-09-17 20:50），镜像读出的资金值可能为零值/陈值——P7 在段一语义应视为"环境探测"而非"下单资格终审"；真正的资金资格判定由段二 T1 重跑断言承担（届时官方导出已随开盘刷新）。

## 5. 双重保险（绝不触碰实盘）

1. **保险一·账户前缀断言**（P2/P1）：脚本启动即断言 account_id==8886156677 且进程路径含"模拟"；构造参数硬编码 `env="sim"`、`broker_id="qmt_sim"`、assembly `enable_real=False, enable_sim=True`（与 e2e 先例逐字同款）。任何一路不符→EXIT_ENV，无逃生分支。
2. **保险二·配置只读校验**（P3）：独立读 config/qmt_environments.yaml（真源）交叉验证 live 槽未启用（account=''）；脚本内维护实盘危险清单（8887871993 / E:\qmt_bridge\ / E:\国金证券QMT交易端 / QMT_REAL_*）并对全部生效参数做"不在清单内"断言。
3. **结构兜底**：QmtFileBridgeAssembly enable_real 默认 False（代码级，qmt_file_bridge_integration.py:64）；LiveSimulationSwitcher 构造即 SIMULATION、sim→live 需 Owner 一次性令牌 Fail-Closed（本测试根本不实例化它）；Stock 官方导出目录 physical 隔离（sim=E:\qmt_bridge_sim\Stock\ vs real=E:\qmt_bridge\Stock\）。

## 6. 失败分支与应急

| 症状 | 定性 | 处置 |
|---|---|---|
| HTTP 无 ack 且文件通道也无 ack | 真丢单窗口（93 §12.5 PermissionError 案） | 查柜台镜像 pending；有挂单→撤单；无→单未进柜台，安全，记录 EXIT_NOACK |
| 单意外 FILLED（跌停价被打开且成交 100 份） | 链路超预期工作 | **不慌**：模拟资金。立即止步后续下单步骤，记录成交回报三源对照，反向平仓单**不在本测试授权内**→留持仓交 Owner 处置（100 份 510300 量级可忽略），测试仍判链路 PASS（成交回报验证更完整） |
| 撤单 90s 未确认 | 柜台延迟/冻结期 | 重发撤单一次；仍超时→查 Message.csv 与 ack RETRY 状态，人工兜底 |
| 台账步 c 断言失败（若断点 2 已修但无行） | 写入接线回归 | 按施工批回归处理，非本测试范畴 |
| 沙箱 handlebar 被人为停止（18901 死+orders 文件无消费） | 沙箱侧故障 | 只报障不代修（沙箱策略不在 repo 管辖），EXIT_SANDBOX |

## 7. 验证命令速查（施工时逐条落进脚本断言）

```powershell
# P1 进程辨识（单终端场景；双终端必须升级 TCP 配对法）
Get-Process XtItClient,XtMiniQmt -ErrorAction SilentlyContinue | Select-Object Id,ProcessName,Path
# P4 HTTP 桥探活
Test-NetConnection 127.0.0.1 -Port 18901 -InformationLevel Quiet
# T6a 柜台镜像三文件（GBK，人工核对辅助）
Get-Content E:\qmt_bridge_sim\Stock\Order.csv -Encoding Default | Select-String "510300"
Get-Content E:\qmt_bridge_sim\ack_sim.csv -Encoding Default | Select-String "smoke-e2e"
```

## 8. 设计自审（对齐挖矿 SOP §6）

- **消灭什么人工环节**：Owner"桥到底通不通、能不能安全下单"的口头问询与人工排查→一段脚本出 PASS/FAIL 证据链；同时是执行面通电（终局自动化的前门）的准入验证。
- **终局有位**：本脚本骨架=未来"策略转正审批（模拟→实盘，宪法 §5 high 门位）"前的标准验收件雏形，非一次性脚本（参数化 env 断言面后可复用为回归冒烟）。
- **时序**：断点 1/2 未修不阻塞本测试（T6b 如实验证断点仍在）；本测试反而是修断点 2 的前置（先证回报活，再接台账写）。
- **裁定：施工**（设计已毕，执行待施工阶段+Owner 择窗；段二须交易时段）。
