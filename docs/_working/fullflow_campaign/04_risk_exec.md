---
ttl: task_bound
completes_when: 全流通战役收官且最终交付报告落盘
---

# S4 风控与执行环节簿

> 战役: fullflow_20261008 ｜ 段: S4 风控与执行 ｜ 挖矿代理: R ｜ 日期: 2026-10-08
> 范围: risk-status/regime 投影 → 熔断/回撤/红线 → 仓位档 → ex_sor 执行域 → paper 模拟盘 → schedule_gate 调度闸
> 纪律: 只读调研+import 冒烟；未启动任何服务、未执行任何真实下单/资金操作。

## 一、输入面

| 输入物 | 真源路径 | 说明 |
|---|---|---|
| 熔断五级触发态 | `data/runtime/trading_kill_switch_state.json` | trading 进程 KILL_SWITCHES 内存态的磁盘影子（`zephyr.trading.trading_contracts.risk.kill_switch_state_store`，MOD-INF-016）；5 级=POSITION_LIMIT/DAILY_LOSS/CIRCUIT_BREAKER/SECOND_LEVEL/API_TIMEOUT；现值=2026-10-07T07:06Z 落盘、全 5 闸 active=true |
| 仓位参数表 | `config/position_parameters.yaml` | hard_cap=0.30（confirmed，裁定#429 Owner 签发 2026-09-29）；六段预算带（capitulation 0-10%/accumulation 20-30%/ignition 30-50%/expansion 50-70%/euphoria 只卖不买/distribution 空仓）；过渡带 0.5-0.7；未确认时 effective_hard_cap=0.0 fail-closed |
| 代码侧仓位常量 | `src/zephyr/strategy_pipeline/daily_decision_orchestrator.py` L98-110 | HARD_CAP=0.60/TRANSITION_THRESHOLD=0.60/TRANSITION_FACTOR=0.5/BUDGET_BANDS（注释值全 proposed，裁定#305 草案）；regime 六段映射消费 `framework_composer.REGIME_STATE_TO_ACTIVATION_PHASE` |
| 风控参数真源 | `config/risk_params.yaml`（MOD-INF-002） | INV-002 单票≤5% NAV、行业≤30%、总杠杆≤1.0、策略相关性≤0.85、ADV 参与≤5%；daily_loss_limit_nav_ratio=null（T0/T1 前待 Owner 配置） |
| 回撤控制器输入 | `src/zephyr/position/core/drawdown_controller.py`（MOD-POS-008） | 组合回撤 + VaR/CVaR 系统性分级（GREEN/YELLOW/ORANGE/RED/BLACK 五档，VaR 2%/4%/6%、CVaR 10% 阈）+ 黑天鹅 7 模式（BS-001~007）+ 策略级 Soft(>5%)/Hard(>10%) Stop |
| 红线引擎输入 | `src/zephyr/ex_sor/risk_redline.py`（MOD-AUTO-L6-001） | 组合日度序列 [{date,pnl_pct,market_crash}] + RedlineConfig（日黄 2%/日红 4%/周红 5%/月红 10%/回测最差日 2 倍/黑天鹅缓冲 2 日） |
| regime 词表 | `src/zephyr/regime/core/regime_detector.py`（MOD-REGIME-001） | 7 态 r1-r4（HMM family）+ r10-r12（overlay family）；REGIME_STATES 零硬编码投影 |
| 组合网格维度 | `config/position_recipe_grid_schema.yaml`（F-06 v2） | A1-I 九维活跃+F/J/K 条件折叠，compile(context) 求值；基线组合名义 N=362,880 |
| L5 排产闸常量 | `config/schedule_gate_policy.yaml`（MOD-INF-037） | 成熟度门 M1-M4（≥2 win/胜率≥0.60/样本≥3/90 天新鲜度/白名单[ai_eng,tooling]）、两问打分优先级、配额 Q1-Q4（会话≤2/subagent≤3/token 300 万日/提交队列深度≤10） |
| 执行域上游 | 信号/订单意图（S2 决策链）+ 券商 API（miniQMT） | ex_sor 消费订单特征与市场上下文（market_context_provider） |

## 二、输出面

| 输出物 | 形态 | 下游消费者 |
|---|---|---|
| `/api/risk-status` JSON | 只读投影：kill_switches/active_levels/saved_at/age_seconds；缺/坏=degraded+error（fail-visible 禁假数据）；回撤档如实标 drawdown.available=false | `src/zephyr/frontend/dashboard/web/features/warroom/wr-risk-cards.js`（作战室风险卡） |
| `/api/regime/current` JSON | 7 态词表投影；current=null+recent_series=[]+degraded:true（无日序真源，不造假） | `src/zephyr/frontend/dashboard/web/features/backtest/bt-live-tools.js` |
| 仓位上限 position_cap | min(预算带, HARD_CAP)，过渡带 ×TRANSITION_FACTOR | daily_decision_orchestrator 决策播报 → 执行链 |
| 红线动作列表 | YELLOW（减半仓+归因）/RED（清仓冻结）/GRACE（黑天鹅缓冲）/闩锁周月线 | 实盘监控执行器（施工待实盘开通）；rl_exec_boundary 语义对齐 |
| DrawdownController 响应 | 减仓比例/仓位上限/动作列表/Kill Switch 建议（BS-007 委托 stop_loss 执行，本模块不直接触发）；回撤回补 50%→每步 25% 恢复 | risk_layer_orchestrator（组合级风控层） |
| ex_sor 执行决策 | 最优券商路由（XS-001）、算法选择（XS-011）、TWAP/VWAP/ICEBERG 等引擎（XS-005）、卖出时段通道决策（XS-016）、拆单（sor_agent XS-015） | TradingSession/OrderManager（经 ex_core） |
| 执行质量反馈 | 滑点实际 vs 预估归因/预测（XS-017）、执行质量多维评分（XS-018）、总成本最小化（XS-019）、做T成本模型（CST-T0-001，价差≥0.3% 才正期望） | 策略评估与执行参数优化闭环 |
| TD3 checkpoint | 仅历史 replay 预热产物，只进模拟盘对拍 | 模拟盘对拍（真训练管线=H-04 Owner 门） |
| L5 排产决策 | 工单排序/门闸放行/配额降档 | `zephyr.ai_layer.scheduling.{maturity,router,order_daemon}`（AI 层排产，非交易调度） |

## 三、入口面（逐个：命令/路由 + 实测绿/黄/红）

| # | 入口 | 命令/路由 | 实测 | 证据 |
|---|---|---|---|---|
| 1 | ex_sor 域全模块 import 冒烟 | `PYTHONPATH=D:\ZephyrAlpha\src python -c "import zephyr.ex_sor…"`（Python 3.12.8） | **绿** | 24/24 模块 import OK 零失败（core 12+services 6+rl_trainer 2+api 2+包体 2） |
| 2 | 风控真源模块 import | kill_switch_state_store/trading_kill_switch/drawdown_controller/regime_detector/daily_decision_orchestrator/drawdown_state_machine/ai_layer.scheduling | **绿** | 8/8 import OK |
| 3 | 风控实况只读投影 | `GET /api/risk-status`（api_server.py L5168） | **黄** | 未起服务（纪律）；静态核验：真源文件在且 JSON 可解析，端点逻辑为纯只读投影+fail-visible=通道绿；但影子 saved_at=2026-10-07（陈旧>1 日）且全 5 闸 active=true，状态判读需 Owner |
| 4 | regime 只读投影 | `GET /api/regime/current`（api_server.py L5214） | **黄** | 词表 import 绿；端点设计性 degraded:true——7 态日序无持久化真源，current 恒 null（检测器离线回放另批立项） |
| 5 | 仓位双闸守卫（G1/G7） | `python scripts/governance/check_trd_a20_a21_dual_gates.py` | **红** | 实测 FAIL×2：G7 参数表与代码常量漂移 `hard_cap 0.3 != code 0.6`；G1 密钥轮换 Owner 催办未办〔G1 已结案 2026-10-09：#398/#399 维持不轮换+触发器制，R15 批转收口——G 车道登记〕 |
| 5b | **G7 修复就绪待落地（总包 st-entrance-gate-20261007 深挖后执行）** | 修复=代码 HARD_CAP 0.60→0.30（裁定#429 考古定谳 0.30 为 Owner 签发真值），守卫实测 G7 PASS，已入 st-poscap 分支+队列袋 | **受阻** | 该文件叠四层先存量债形成债务墙：①TABLE-NAME-REGISTRY（L182 表名硬编码，品类已在册只差 TableRegistry 引用——已同批修）②GATE-ALGO-FLOW（模块无 ALGO_FLOW 锚——校准块已起草入 docstring）③GATE-ANY-ABUSE（L279 _scalar1 裸 Any 返回）④6 处 lint。fail-closed 设计=漂移期间 effective_hard_cap=0.0 不建仓（无风险敞口）；处方=属主车道 ALGO_FLOW 校准遍按 ②③④⑤ 顺次清偿后，①随批落地（修复内容在其分支 st-poscap-fix-20261008 留档） |
| 6 | 模拟盘冒烟 | `python scripts/start_paper_session.py --dry-run`（只连 QMT 模拟账户不打单） | **黄** | 入口在、装配链齐（风控层必装配：回撤基线读不到=拒绝装配 exit 1 fail-closed）；未执行——需 QMT 环境+交易日+Owner 窗口 |
| 7 | 模拟盘下单会话 | `python scripts/start_paper_session.py [--strategy topn-momentum] [--service]` | **红-需授权** | 可向模拟账户真实下单；**需 Owner 授权才可运行**，本次只记录不执行 |
| 8 | 模拟盘计划任务 wrapper | `powershell -ExecutionPolicy Bypass -File scripts\start_paper_session_daily.ps1` | **黄** | 脚本存在（交易日判定+QMT 进程探活+拉起 --service+日志 .runtime/logs/paper_session.log）；登记的计划任务 DISABLED（启用=Owner 窗，92 D3） |
| 9 | 实盘交易进程 | `python -m zephyr.trading`（AutoRuntime Core，KILL_SWITCHES 真源宿主） | **红-需授权** | 真实资金链路总入口；**需 Owner 授权才可运行**，本次只记录不执行 |
| 10 | RL 真训练 | `python -m zephyr.ex_sor.services.rl_trainer.trainer --real-training` | **红-需授权** | 库层默认 real_training=False（只 replay 预热零梯度）；真训练触发+模型上实盘=H-04 Owner 门 |

## 四、模块面

### ex_sor 订单执行域（`src/zephyr/ex_sor/`，D_EX_SOR，24 模块 import 全绿）

| module_id | 模块 | 职责一行 |
|---|---|---|
| MOD-XS-001 | core/optimal_order_router.py | 延迟/成交率/费用三维加权最优券商选择 |
| MOD-XS-002 | core/broker_adapter_manager.py | 多券商统一适配+事务一致性+连接熔断+故障转移 |
| MOD-XS-004 | core/execution_scheduler.py | 时间切片+TWAP/VWAP 调度+优先级队列+进度监控 |
| MOD-XS-005 | core/algo_trading_engine.py | 算法注册表+TWAP/VWAP/ICEBERG/POV/IS/ALT 引擎+参数优化 |
| MOD-XS-006 | core/market_context_provider.py | 为算法引擎提供 MarketContext（治 G7 整笔直下占位病） |
| MOD-XS-008 | core/rl_exec_contract.py / rl_exec_env.py / rl_exec_boundary.py | RL 执行训练三件套：参数契约/环境骨架/硬边界包裹层（P-4 裁定组件） |
| MOD-XS-011 | core/algo_execution_selector.py | 订单特征→最优算法自动选择+推荐+效果评估 |
| MOD-XS-013 | api/broker_api_connector.py | REST/FIX 4.2+ 连接+心跳+重连+版本迁移 |
| MOD-XS-014 | api/api_rate_limiter.py | 四级限流（全局≤50QPS、miniQMT≤10TPS 等） |
| MOD-XS-015 | core/sor_agent.py | SOR 路由 Agent（Level 0 纯规则禁 LLM 写入）：通道选择+拆单+滑点回写 |
| MOD-XS-016 | core/sell_session_router.py | 卖出时段通道分裂路由（纯函数可回测：竞价/跳水窗/尾盘竞价） |
| MOD-XS-017 | services/slippage_analyzer.py | 实际 vs 预期滑点+归因+预测+基准比较 |
| MOD-XS-018 | services/execution_quality_scorer.py | 价格/时间/成本/市场影响多维执行质量评分 |
| MOD-XS-019 | services/transaction_cost_optimizer.py | 佣金+印花税+冲击+机会成本→总成本最小化 |
| CST-T0-001 | services/t0_cost_model.py | 做T成本模型（滑点×2+失败溢价；往返≈0.10-0.15%，价差≥0.3% 硬前置） |
| （90 号 Phase1③） | core/execution_route_policy.py | 默认单笔限价单+打板专用路径（封成比≥5% 过滤；删伪精确 ADV 条款） |
| MOD-AUTO-L6-001 | risk_redline.py | 实盘红线分级纯函数引擎（零 IO 零时钟，时间注入；2026-09-17 红队修复 5 项在案） |
| — | services/rl_trainer/{td3_agent,trainer}.py | TD3 双 Q+目标网+延迟更新；real_training=False 默认（H-04 Owner 门） |

### 风控真源与仓位档

| module_id / 标识 | 模块 | 职责一行 |
|---|---|---|
| MOD-INF-016 | `zephyr/trading/trading_contracts/risk/kill_switch_state_store.py` | 熔断触发态磁盘影子：save/rebuild_from_disk 纯加闸不加放；重启重臂在飞熔断 |
| （D_TRADING） | `zephyr/trading/trading_contracts/risk/trading_kill_switch.py` | 五级 KillSwitchLevel 内存态真源 |
| MOD-POS-008 | `zephyr/position/core/drawdown_controller.py` | 回撤五档分级响应+黑天鹅 7 模式+策略止损 |
| MOD-REGIME-001 | `zephyr/regime/core/regime_detector.py` | 7 态 HMM+overlay regime 检测（词表真源） |
| — | `zephyr/strategy_pipeline/daily_decision_orchestrator.py` | regime→六段预算带→position_cap（总仓位=min(带,硬顶)，过渡带折减） |
| MOD-INF-002 | `config/risk_params.yaml` | 集中度/杠杆/相关性风控参数唯一真源（三平面禁漂移） |
| MOD-INF-037 | `config/schedule_gate_policy.yaml` | L5 排产门闸与配额常量层（AI 提案→Owner 修标，禁运行时改值） |
| — | `scripts/governance/check_trd_a20_a21_dual_gates.py` | G7 参数表-代码常量漂移守卫+effective_hard_cap fail-closed |
| — | `zephyr/risk/core/drawdown_state_machine.py`、`zephyr/ex_core/risk_layer_orchestrator.py` | 回撤状态机与组合级风控层编排（paper 会话必装配） |

## 五、自动化面

- **已自动（进程内生/事件触发）**：kill_switch_state_store 在 trigger/reset 时自动落盘、启动 rebuild 重臂（事件触发，无 cron）；api_server 心跳 daemon 线程随服务进程；AsyncFillDispatcher 成交落账离回调线程；RiskValidationBridge+RiskLayerOrchestrator 在会话内自动拦截（EMERGENCY→熔断清算、盘中对账→冻结标的、启动恢复 Fail-Closed）。
- **计划任务（登记制）**：`scripts/tasks/register/register_paper_session_task.ps1`（模拟盘 Daily 09:25，**当前 DISABLED，启用=Owner 窗**）；`register_post_settlement_task.ps1` 在册；长批任务防误杀登记 `data/runtime/process_reaper_keep.txt`（RULE-GUARDIAN）。
- **手动（过渡形态，57 号文 §2）**：交易日 09:25 前人工拉起 `start_paper_session.py`（非 daemon 不挂调度；--service 常驻=LiveStrategyAdapter 监督+退避重启熔断+biz 心跳）；有界保活 15:05 自动 stop，stop 自动撤未成交单。
- **永久系统四要素核对**：模拟盘链=自动触发✗（DISABLED）/自动运行△（拉起后监督自动）/自动维护△/自动关闭✓（15:05 有界收场）——整体仍处手动过渡形态，挂调度是 Owner 门。
- **不属交易调度**：schedule_gate_policy+ai_layer.scheduling 是 AI 层排产闸（工单/配额/成熟度），与交易时钟无耦合，勿混淆。

## 六、缺口面（[绿|黄|红]）

- **[红→已闭合 10-08] 仓位硬顶双真源漂移**：`position_parameters.yaml` hard_cap=0.30（confirmed 裁定#429）vs `daily_decision_orchestrator.py` HARD_CAP=0.60（裁定#305 草案值），G7 守卫实测 FAIL。**已修（st-entrance-gate-20261007 落地，st-fullflow2 10-08 交叉验证）**：代码 HARD_CAP 0.60→0.30 已入 dev（裁定#429 考古定谳 0.30=Owner 2026-09-29 数字确认真值），守卫 scripts/governance/check_trd_a20_a21_dual_gates.py 实测 G7 PASS。
- **[红·催办刷新 10-08] G1 密钥轮换催办未办**：.env 曝光（2026-09-18）后 Owner 超期未轮换——截至 2026-10-08 已 20 天（双闸守卫输出"超 3 天"系挖矿时旧判读），连带风控面准入。**催办刷新（st-fullflow2-20261008 晨报随报提醒）**：本项=Owner 钥匙操作，AI 禁代旋转；请 Owner 执行 G1 密钥轮换（secrets.py 体系内换钥+受影响 token 重签）后回写轮换完成日期，本行随之转绿。**[结案 10-09]**：#398一（Owner 明示不轮换+触发器制=异常计费/异常调用即轮换）+#399四 全批准确认+Owner 2026-10-09 B 清单 R15 批转=登记面收口；本催办行转结案绿（安全语义=维持不轮换，非轮换完成）；.env mtime 澄清留 Owner 知会——st-chiefc-20261009 G 车道。
- **[红-需 Owner 授权才可运行]**：真实下单/资金类入口——`python -m zephyr.trading`（实盘进程）、`start_paper_session.py` 非 dry-run 模式（模拟账户下单）、ex_sor 券商连接器实连、rl_trainer `--real-training`（H-04）。本次全部只记录未执行。
- **[黄] regime 7 态无日序持久化真源**：`/api/regime/current` 永久 degraded（current=null），日序生产=检测器离线回放，另批立项未开工。
- **[黄] 回撤五档无落盘影子**：DrawdownController 为 trading 进程内存态，risk-status 如实标 unavailable——重启即丢档位观测（与熔断影子同病未治）。
- **[黄] 熔断影子状态判读缺 TTL**：现影子 saved_at=2026-10-07、全 5 闸 active=true；端点只报 age_seconds 不因超龄降级，陈旧影子与真实触发态无法机械区分，需 Owner 判读（演练态 or 在飞熔断）。
- **[黄] daily_loss_limit_nav_ratio=null**：risk_params.yaml 明示 T0/T1 前由 Owner 配置后不得静默变更——日损失限额尚未定值。
- **[黄] 模拟盘自动化 DISABLED**：日常模拟盘依赖人工拉起，计划任务登记制待 Owner 启用（挂调度=Owner 窗口）。
- **[黄] 实盘红线执行器缺位**：risk_redline 引擎（含 2026-09-17 红队修复）+测试在案，但 CONSUMERS 自述"实盘监控执行器（施工待实盘开通）"——纯引擎无消费者接线。
- **[绿] ex_sor 域健康**：24/24 import 绿；tests/trade/ex_sor 18 件测试在案；四级限流/红线引擎/卖出路由纯函数化可回测。
- **[绿] 风控真源链齐**：熔断影子+守卫脚本+fail-closed 语义（未确认=0 仓位）+fail-visible 投影（禁演示假数据）纪律成体系。

## 七、自审闸（三态总裁定）

**总裁定：黄（通道在、需授权/需修标，非断链）。**

- 绿证据：ex_sor 24 模块+风控真源 8 模块 import 全绿；风控真源链（熔断影子→只读投影→漂移守卫→fail-closed/fail-visible）体系完整；执行域测试 18 件在案。
- 黄证据：regime 日序缺真源、回撤档无影子、日损失限额未配置、模拟盘自动化 DISABLED、影子全开待判读——均为"通道在但缺数据或缺授权"。
- 红证据（不阻断本环节簿交付，但阻断带资运行）：~~G7 硬顶漂移~~（10-08 已修，守卫 PASS）+ ~~G1 密钥轮换催办（Owner 未办，10-08 晨报已再催）~~（10-09 已结案：#398/#399 维持不轮换+R15 批转收口——G 车道登记）+ 全部真实下单/资金入口未获 Owner 授权。**任何带资运行前：先清 G1，再走 Owner 授权门。**
