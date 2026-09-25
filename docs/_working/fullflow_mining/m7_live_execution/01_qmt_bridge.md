---
ttl: task_bound
---

# M7-01 · 实盘 QMT 桥（T10）

> 挖矿班 st-commitspeed-tbl-20260924 ｜ 2026-09-25 ｜ 只读挖矿（禁启终端/禁下单/禁连真实账户，连模拟下单接口也不碰）
> 交叉引用：decision_map_campaign `13_trading_chain_audit.md` 环节④/⑧（业务流审计）；本文补代码级子模块清单与通道退役考古。

## 一、环节定义与边界
把本进程订单语义翻译成 QMT 终端可执行的通道（指令文件/HTTP/SDK），并把柜台状态/成交/持仓/资金镜像回本地。上游=OrderManager/Saga（供单），下游=柜台镜像（供仓位/资金/成交真源给 TradingSession、position_reconciler、execution_report）。

## 二、六向台账
| 向 | 内容与实证 |
|---|---|
| 上游输入 | OrderManager.register_broker（`qmt_file_bridge_integration.py:148`）；Saga/TradingSession 委托单；行情注入=QmtFileBridgeQuoteProvider（`trading_session.py` 经 price_provider） |
| 下游消费 | CounterStateMirror（持仓/资金/挂单/成交→`get_counter_*` 接口族 `qmt_file_bridge_broker.py:727-755`）；execution_report 生产端（断点 E4，`attach_execution_report_producer:427`）；broker 健康检查→前端监控（`check_broker_health:913`） |
| 自动化触发 | `ZephyrAlpha_QMTWatchdog` 计划任务 Daily 08:45+12:55（`scripts/qmt_watchdog.ps1`，无状态 one-shot，M5 01 册实测 09-24 两班 LastResult=0）；`ZephyrAlpha_SimBridgeExecute` 09:35+13:05（**见堵点 B1，执行腿已断**）；会话本体=manual（start_paper_session 09:25 任务拉起） |
| 真源与注册表 | 桥蓝图=docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md（MOD-L06-001）；迁移台账=docs/_working/2026-09-08-qmt-bridge-migration-ledger.md（结案判定=未结案保留）；通道退役冻结注记=`miniqmt_channel_manager.py:56-62` |
| 门禁与质量尺 | R-H5E-1 sim 进桥前风控 fail-closed（`:571-620`，real 显式不注入=裁定#338⑤ Owner 门）；双实例物理隔离 env=real/sim（`:336-351`）；整手/价格笼子预校验（`:524-545`）；幂等拦截 idempotency_key（`:514-517`）；health 三档 ok/degraded/down |
| 当前运行状态 | **黄**。终端活体=绿（watchdog log 09-24 12:55 OK pid=22860，`data/runtime/qmt_watchdog.log`）；桥代码=绿（tests/ex_core/adapters/test_qmt_file_bridge_broker.py 在册）；桥执行腿调度=**红**（SimBridgeExecute 调用不存在的 `bridge-execute` 子命令，见 04 册 B1）；miniQMT 通道=**已退役**（2026-09-18 券商清退 XtMiniQmt，替代=本文件桥） |

## 三、子模块清单（ls+grep 两源交叉验证，66 件 ex_core 中桥面 11 件）
| 子模块 | 是什么 | 入口 file:line | 状态 |
|---|---|---|---|
| QmtFileBridgeBroker | 主执行器：HTTP 18901 快路径（中位 32ms）fail-open 降级文件桥（中位 5.7s）；3s 轮询柜台镜像 | adapters/qmt_file_bridge_broker.py:321（HTTP `_http_post_order:771`） | draft/evolving，sim 实弹过（09-23 sysid=4820） |
| CounterStateMirror | 柜台全量镜像（含手动单），GBK CSV 四文件 Order/PositionStatics/Account/Deal | 同上：117（`sync_all:161`） | 同上；**读侧对 CSV 列位硬编码**（row[9]/row[15]…，`:175-217`） |
| sysid 回填（历史保险①） | 柜台 sysid→本地 broker_order_id 回填，双键配对（remark+order_id） | 同上：193-204（`_remark_to_order_id/_pairing_cache:399-401`） | **已落**，代码在 |
| 撤单终态保护（历史保险②） | 终态三态（FILLED/CANCELLED/REJECTED）不可被镜像/ack/#FAIL 覆写 | 同上：198-203、858-865、903-910 | **已落**；但撤单终态不产 execution_report 行（audit 移交③，待勘） |
| #SENDING→#DONE 文件状态机 | 指令文件状态标记扫描，#FAIL→REJECTED | 同上：837-865 | 在；HTTP 成功路径不介入 |
| QmtFileBridgeAssembly | 一键装配双实例+LocalOrderQueue+E4 生产端默认接线 | adapters/qmt_file_bridge_integration.py:48（E4 默认开 `:103`） | 在 |
| QmtFileBridgeQuoteProvider | 反向行情桥：quote.csv 尾读 64KB+残行回退+mtime 新鲜度 | adapters/qmt_file_bridge_quote.py:31 | 在；喂 BoardIndexRealtime/trading_session |
| QmtTradingSession | 策略层无感知会话（env 校验先行，start 才连接） | qmt_trading_session.py:61 | 在；**OrderManager() 裸构造（:115）=合规门零注入**（见 06 册） |
| BrokerLinkProbe | miniQMT 链路探针（连接/下单延迟/回报延迟三件，注入式只读） | broker_link_probe.py:82 | 在但**未接线**（生产接线点名"健康巡检批次"，仓内未见装配点） |
| MiniQmtChannelManager | 通道五态状态机（DISCONNECTED→…→DOWN，fail-closed） | miniqmt_channel_manager.py:121 | **退役保留**：RETIRED_DATE=2026-09-18（`:61`），接口在禁真连，作重连管理参照实现 |
| MiniQmtBroker / OKXBroker | xtquant SDK 实盘适配器 / OKX 加密适配器 | adapters/miniqmt_broker.py、okx_broker.py | miniqmt=**退役通道残留**（券商清退）；okx=在盘未接（95 号 Phase 2 挂起） |
| qmt_watchdog.ps1 | 终端活体看门（无状态 one-shot，禁凭证 UI 自动化=安全裁定边界） | scripts/qmt_watchdog.ps1:1-58 | production；终端路径 UTF-8 存 data/runtime/qmt_terminal_path.txt |

## 四、堵点与病灶
| # | 现象/根因/修法/工作量/归属 |
|---|---|
| B1 | **SimBridgeExecute 执行腿指向不存在的子命令（P0，本班新证）**：`run_sim_bridge_execute_daily.ps1:76` 调 `sim_daily_runner.py bridge-execute`，但该子命令在已提交历史中**从未存在**（`git log --all -S "bridge-execute" -- scripts/backtest/sim_daily_runner.py` 零命中；HEAD 与工作区均只有 plan-bridge/plan-execute/e4-replay/report/settle 五子命令）。09-23 首单实弹来自**未提交工作区状态**，随后丢失（与 audit 环节⑥-3"活写手回退"自洽）。修法=按 delivery_report_20260923 §3 全参数路径重建 bridge-execute 并入册提交+幂等预扫+quote 新鲜度闸回归；预估 0.5-1 天；归属 M7 施工（调度面归 M5） |
| B2 | **桥断联自愈半成品**：同步线程异常不杀线程下轮重试（`:806-808`）+health 导出新鲜度>60s 判 degraded（`:961-963`）——但 degraded 只进前端监控读数，**无自动动作**（不撤在飞单、不告警到人、不重拉终端；M5 S5/S3 同族"单点哑发射"）。修法=degraded 持续 N 轮→事件触发 cancel 在飞单+告警条目（对齐 alert_threshold_registry 流程）；预估 1 天；可施工 |
| B3 | BrokerLinkProbe 无装配点（探针建好无人插电）；check_broker_health 消费面=前端监控组件，盘中无人盯。修法=装配时把 probe 挂 sync loop 采样+deadman 新通道；0.5 天 |
| B4 | 柜台 CSV 列位硬编码+账号硬编码（ENV_CONFIG `:336-351` 含实盘账号 8887871993 明文）——RULE-SECRETS 边缘（账号≠密钥，但实盘账号明文进 git 面宜移 config/.env.qmt）。修法=ENV_CONFIG 读 env 文件；0.5 天；待裁（涉 real 配置） |
| B5 | 迁移台账三未结（audit C7 引用）：沙箱同等权限 Owner 验证 9/18 逾期、下单/取价/桥监控三勾选空、PositionStatics 13 天未更红旗无复核。Owner 门位催办项 |

## 五、提速与合并机会
- MiniQmtBroker+MiniQmtChannelManager 退役后仅测试消费：可按内收判据"零触发零消费→退役"立项退役评审（保留状态机语义作参照的说法已在头注自认，若 6 个月无接线即删）。**待裁**（净删=Owner 门）。
- okx_broker/crypto 链已被总筹裁"研究域不编入生产流通挖矿"——本册只登记存在（adapters/okx_broker.py 600 行，testing），不再挖。

## 六、自审闸三态
**挖干可施工**（桥面代码/调度/退役考古三向全实证；B1/B2 有根因+修法）。B4/B5 两小项挂待裁/Owner 催办，不动摇主体结论。

## 七、复核命令（10 分钟）
```bash
sed -n "17,36p" src/zephyr/ex_core/adapters/qmt_file_bridge_broker.py   # 职责/快路径契约
sed -n "56,62p" src/zephyr/ex_core/miniqmt_channel_manager.py           # 退役冻结注记
git log --all --oneline -S "bridge-execute" -- scripts/backtest/sim_daily_runner.py  # 零命中=B1 实证
tail -3 data/runtime/qmt_watchdog.log                                    # 终端活体
grep -n "bridge-execute" scripts/run_sim_bridge_execute_daily.ps1        # :76 断腿点
```
