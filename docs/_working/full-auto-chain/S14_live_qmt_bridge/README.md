---
ttl: task_bound
title: S14 实盘流转与 QMT 桥挖矿文档
session: st-fullauto-20260915
date: 2026-09-15
---
# S14 实盘流转与 QMT 桥（拍板后流转+QMT 模拟桥 100 股下单实测）

> 骨架定位：前端拍板（S13）→ 实盘/整装流转 + **QMT 模拟桥 100 股端到端实测**（施工 C6）。
> 当前=❌ 未实测（冒烟脚本与全套桥件已在，缺实弹记录）。本环节挖矿核心：①下单桥现状；
> ②模拟户 vs 实盘户代码级区分；③100 股单最小调用路径+安全护栏。

## 1 现状盘点（自动化状态+file:line 证据）

### 1.1 下单桥现状——xttrader 适配器全套已在（成熟度高）

- **MiniQmtBroker**（MOD-L06-001，`src/zephyr/ex_core/adapters/miniqmt_broker.py`，SAFETY=M）：
  - `submit_order` L410：七步流水=幂等拦截（INV-007，idempotency_key 必带）→A 股约束
    （T+1 锁定查 available_quantity/板块差异化整手 board_lot 真源/涨跌停）→价格笼子夹边
    不废单（price_cage 真源）→MatchingLogic 预成交校验（回测=实盘一致性）→xttrader.
    order_stock→错误码映射（0/-1/-2/-3/50/51/52/53/54/55）→订单缓存；
  - `cancel_order` L522 / `query_order` L563 / `get_positions` L601 /
    `query_trades_today` L645 / `pre_trade_simulate` L733 / `register_fill_callback` L724；
  - xtquant 版本契约：250807.1.2+（#ARCH-XTQUANT-API-COMPAT-001），session 必须 int
    （L288 hash 转换），下单/查询必须 StockAccount 对象（`_init_account` L876-896），
    start() 返回 None 坑已修（L898-905）；xttrader 非线程安全全链 `_lock`；
  - 断线重连四步（GAP-002）：行情重订阅+策略恢复+假死心跳（10s 心跳/30s 超时）。
- **MiniQmtChannelManager**（MOD-EX-058，`ex_core/miniqmt_channel_manager.py`，SAFETY=H）：
  通道生命周期状态机 DISCONNECTED→CONNECTING→CONNECTED→RECONNECTING→DOWN 单向留痕；
  Fail-Closed=非 CONNECTED 一切调用 MiniQmtChannelError；ChannelTransport 协议注入
  （本模块不 import xtquant）；约束三（下单 10 笔/秒、Tick=3 秒）的接口底座。
- **会话装配**：`start_paper_session.py`（MOD-SCRIPT，57 号文 GAP-2）=QMT_SIM_*→
  MiniQmtBroker→TradingSession（OrderManager+RiskValidationBridge+策略/信号/价格提供器）；
  `--dry-run` 只连不下单；`--service`=LiveStrategyAdapter 监督（异常隔离+退避重启熔断+
  biz 心跳）；有界保活至 15:05 自动 stop（stop 撤全部未成交单，trading_session L305/L942）。
  `register_paper_session_task.ps1`（任务 ZephyrAlpha_PaperSession）注册为 **DISABLED**，
  启用=Owner 窗口（Enable-ScheduledTask 后 09:25 拉起）。

### 1.2 模拟户 vs 实盘户的代码级区分（必答③前半，护栏真源）

- **连接参数层**：`config/.env.qmt` 四键——QMT_SIM_PATH（E:\国金QMT交易端模拟\userdata_mini）/
  QMT_SIM_ACCOUNT / QMT_REAL_PATH / QMT_REAL_ACCOUNT；start_paper_session 不变量明文=
  **"仅连 QMT 模拟账户（QMT_SIM_*，实盘 QMT_REAL_* 永不触碰）"**。
- **结构化辨识真源**：`config/qmt_environments.yaml`（#ARCH-QMT-ENV-DISAMBIG-001，
  "任何 QMT 操作前 MUST 先读该文件辨识环境"）：
  - sim：safety_level=L，账号 8886156677（模拟资金 1000 万），辨识特征=目录含"模拟"后缀；
  - live：safety_level=H，**account 留空（"实盘立项时填入"）**，blocks_live_trading=true，
    "任何下单操作需 ZEPHYR_ENV=live + 外部契约验证通过"；
  - **双终端在线的权威辨识=TCP 配对法**（LISTEN 58610 二义，靠 ESTABLISHED 连接配对锁定
    真实对端进程，`tick_subscriber._identify_qmt_peer_via_tcp` 已实现）；common_mistake
    明载"用户说开了模拟盘但实际是真盘"的事故形态——**Owner 已同时开启实盘+模拟终端，
    C6 实测 MUST 走 TCP 配对法而非肉眼/路径法单判**。
- **模式语义层**：LiveSimulationSwitcher（MOD-EX-035，SAFETY=H，human_gated）：构造即
  SIMULATION；sim→live 必须一次性确认令牌（token_verifier 注入，验签失败停门 Fail-Closed），
  live→sim 免令牌；全程 SwitchRecord 留痕（令牌只存 sha256 指纹）。
- **账户对象层**：MiniQmtBroker 构造时 account_id 决定 StockAccount——打哪个户在构造参数
  处一锤定音，后续无隐式切换。

### 1.3 100 股单最小调用路径（必答③后半，已存在的全链脚本）

`scripts/tests/smoke_test_qmt_broker.py`（manual，不入 CI）**就是 100 股实测的现成协议**：

```
STEP 0 环境辨识守卫 _verify_sim_terminal_running（psutil 扫 XtMiniQmt 进程路径，含"模拟"→过；
       含"证券"无"模拟"→FAIL 拒跑）      #ARCH-QMT-ENV-DISAMBIG-001
STEP 1 读 config/.env.qmt（QMT_SIM_PATH/QMT_SIM_ACCOUNT）→ MiniQmtBroker(path, session_id,
       account_id).connect()
STEP 2 get_positions() 查资金
STEP 3 xtdata 取 600000.SH prev_close → 限价=跌停价×1.01（远价挂单必不成交）→
       Order(idempotency_key="smoke-<ts>", order_type=LIMIT, quantity=Decimal("100"),
       side=BUY, strategy_id="smoke_test", symbol="600000.SH", limit_price=…)   ← 100 股本体
STEP 4 broker.submit_order(order) → broker_order_id
STEP 5 query_order → cancel_order → query 验证 CANCELLED
```

Order 契约=`zephyr.trading.trading_contracts.execution.order`（Order/OrderSide/OrderType）。
整链已设计为"远价+撤单"零成交零资金占用。

### 1.4 风控/杀开关在下单链路的位置

- **TradingSession C-004 合规闸**（`ex_core/trading_session.py` L55/L701-707）：
  `_validate_and_submit`（资金预占：串行扣减 available_cash+卖出预占释放+提交前拦截+拒单
  回滚）内序=INTRADAY 清单 HardBlock→**KillSwitchLite 策略级熔断**（43 号 §4.3：触发策略
  当日禁止新开仓）→四项严禁纪律闸→交易合规检测，失效 Fail-Closed。
- **PreExecutionChecker**（`ex_core/pre_execution_checker.py` L103/183/215-229）：
  kill_switch_probe 探针（生产接线=DefaultRiskValidator.kill_switch_active）；探针 None=
  未接线不臆造（DEBUG 留痕），探针 True=VETO kill_switch_gate。
- **治理级 KillSwitch**（`security/access_control/kill_switch.py` L171+）：默认 NORMAL，
  register_trigger/record_event/is_global_tripped/manual_trip_global；不变量 L8=
  **reset requires owner approval**；交易域另有 trading_kill_switch.py 契约件。
- 三层各管一段：治理级（agent/全局）→盘前（pre_execution）→单内（C-004/KillSwitchLite），
  C6 实测不新增开关，只确认三层在模拟链路上均可用。

## 2 六向挖矿日志表

| 轮 | 矿脉（方向） | 动作与证据 | 判定 |
|----|-------------|-----------|------|
| R1 | ④后端：下单桥解剖 | MiniQmtBroker submit_order 七步 L410+cancel/query/positions/fill 回调；xtquant 250807.1.2 契约坑全修 | **signal** |
| R2 | ④后端：通道与模式门 | MOD-EX-058 fail-closed 状态机；MOD-EX-035 默认 SIMULATION+一次性令牌+sha256 留痕 | **signal** |
| R3 | ⑥数据字段：环境辨识真源 | qmt_environments.yaml（sim 8886156677/L、live 空/H、TCP 配对权威法、smoke guard）；.env.qmt 四键 | **signal**（护栏核心） |
| R4 | ④后端：100 股最小路径 | smoke_test_qmt_broker.py STEP0-6 全链；Order 契约三件套；远价不成交+撤单设计 | **signal** |
| R5 | ④后端：会话/风控链位 | start_paper_session 不变量+--dry-run+--service；ps1 任务 DISABLED；C-004 闸 L701-707；pre_execution kill_switch_probe；治理 KillSwitch reset=Owner | **signal** |
| R6 | ③机制（外部）：QMT 官方口径 | XtTrade 官方文档（dict.thinktrader.net/nativeApi/xttrader.html，访问 2026-09）；miniqmt.com 模拟 vs 实盘差异（模拟不真实报单/实盘触发真实交易，访问 2026-09）；VeighNa 社区连接前提（vnpy.com/forum/topic/33667，访问 2026-09） | **signal** |
| R7 | ③机制（外部）：券商 API 惯例 | Futu unlock_trade 两层门——paper 免解锁/live 必解锁（openapi.futunn.com/futu-api-doc/en/trade/unlock.html，访问 2026-09）；IBKR 会话级 2FA（interactivebrokers.com/docs/tws-api，访问 2026-09） | **signal** |

轮次判定：7 signal / 0 noise。封批转施工。

## 3 业界与开源对照

- **券商 API 下单授权惯例**：Futu OpenAPI=两层门（登录→unlock_trade 后才能下单/撤单，模拟
  户免解锁，错误次数冷却，URL 见 R7）——本项目 LiveSimulationSwitcher（模拟免令牌/实盘
  一次性令牌）与之同构且更严（留痕指纹）；IBKR=会话层 2FA 一次、下单免密（URL 见 R7），
  适合有网关会话体系的场景。**结论：本项目分层设计与业界最佳一致，C6 无需新增授权层。**
- **QMT 生态**：XtQuant.XtTrade 官方能力面（报单/撤单/查询资产委托成交持仓+四类主推回调，
  URL 见 R6）与 MiniQmtBroker 已实现面一一对应；社区教程（知乎 zhuanlan.zhihu.com/p/
  13330916214，访问 2026-09）确认 order_stock/撤单/订阅的通用用法——适配器无欠账。
- **模拟/实盘防呆**：miniqmt.com 明示两模式差异（URL 见 R6）；本项目 qmt_environments.yaml
  的 TCP 配对辨识+smoke guard 属超出业界模板的本地化防呆（双终端同名 exe 是国金环境特有）。

## 4 堵点与欠账清单

| # | 堵点 | 证据 | 后果 |
|---|------|------|------|
| 1 | C6 实测未发生 | smoke 脚本在但无实弹记录/产物归档 | "QMT 模拟桥通"仍是纸面结论 |
| 2 | 双终端在线时路径法辨识不足 | qmt_environments.yaml common_mistake+tcp_pair_authority | smoke 的 psutil 单判在双终端场景有误打实盘的理论风险，须升级辨识 |
| 3 | 实盘账号未配置（设计如此） | qmt_environments.yaml live account='' | 实盘流转前有配置+验证前置 |
| 4 | 拍板→实盘无流转执行器 | FSM sim→production 无生产驱动（S12 §1.3）；整装 sleeve→目标持仓→订单清单翻译件不存在 | 拍板后"进整装/进实盘"仍是人肉动作 |
| 5 | 计划任务 DISABLED | register_paper_session_task.ps1 注释（92 号 D3 口径：DISABLED 等 Owner 启用） | 模拟盘每日自动拉起未开闸 |
| 6 | 三层风控开关无统一自检 | 治理 KillSwitch/PreExecutionChecker/C-004 三层各自独立 | 缺"下单前一键自检三层全绿"的 preflight |

## 5 施工项建议（C6 QMT 模拟桥 100 股端到端实测方案雏形）

1. **实测协议（C6 本体，先 --dry-run 后实弹）**：
   - 前置 A：`python scripts/start_paper_session.py --dry-run`（只连不下单，探活
     connect+get_positions）；
   - 前置 B（双终端辨识升级）：smoke 脚本环境守卫在检测到 ≥2 个 XtMiniQmt 进程时改走
     TCP 配对法（复用 `tick_subscriber._identify_qmt_peer_via_tcp`），判定非 sim 即拒跑；
   - 实弹：`python scripts/tests/smoke_test_qmt_broker.py`（100 股 600000.SH 远期限价→
     撤单，§1.3 协议）；
   - 收尾：产物归档 `docs/_working/pipeline-research/qmt-smoke/`（控制台输出+broker_order_id
     +撤单状态截图+日期+终端辨识结论），登记台账行。
   - 验收标准：STEP0-6 全绿+断言 final.status=CANCELLED+归档齐全；任何一步 FAIL 则 C6
     不通过且不重试超过 2 次（防风控锁）。
2. **安全护栏清单（写死在实测 SOP 里）**：①只读 .env.qmt 的 QMT_SIM_* 两键，QMT_REAL_*
   禁止出现在任何 C6 路径（start_paper_session 同款不变量）；②双终端在线 MUST TCP 配对
   判 sim；③单笔 100 股+远价（跌停×1.01）+当日必撤；④idempotency_key 带日期前缀防跨日
   重放；⑤治理 KillSwitch 状态前置检查 NORMAL。
3. **流转执行器（拍板后自动化的下一块板，本班只登记边界）**：approval approved→
   （整装语义）TDM sleeve 权重已挂→复用 `ex_core.rebalance.requested` 事件触发调仓
   （start_paper_session B4 治本已留事件口，--interval Timer 已删）；订单翻译件
   （目标权重→订单清单）登记为 S14 后续施工，解锁条件=C6 实测通过+C5 拍板链上线。
4. **计划任务开闸**：C6 通过后提请 Owner 启用 ZephyrAlpha_PaperSession（Enable-ScheduledTask），
   使交易日 09:25 自动拉起 --service——消灭"每天人肉拉起模拟盘"人工位。
5. **远期登记**：preflight 三层风控自检命令（治理 KillSwitch 状态+kill_switch_probe+
   C-004 闸干跑）；实盘立项时的 QMT_REAL_* 配置与外验契约（qmt_environments.yaml 已留
   blocks_live_trading 门）。

## 6 封矿结论

- 矿脉层面：7 signal/0 noise，下单桥、通道/模式门、环境辨识、最小路径、风控链位、外部
  惯例六向闭环，封批。
- 方案层面：**下单桥无欠账，欠的是实弹**——C6=现成 smoke 协议+TCP 配对辨识升级+产物归档，
  一天可落；流转执行器与订单翻译件**挂起排期**（解锁条件=C6 通过+C5 上线）；计划任务开闸
  归 Owner 门位。终局全貌（Owner 只管拍板）里模拟桥实测是必经件，**施工**。
- 一句话结论：**100 股最小路径=smoke_test_qmt_broker.py 现成协议（读 QMT_SIM_*→TCP 配对
  判 sim→connect→100 股远价 LIMIT 单→撤单验证 CANCELLED）；确保不打实盘的三重护栏=只读
  QMT_SIM_* 键+qmt_environments.yaml 辨识（双终端走 TCP 配对法）+live 账号本身未配置且
  blocks_live_trading=true。**
