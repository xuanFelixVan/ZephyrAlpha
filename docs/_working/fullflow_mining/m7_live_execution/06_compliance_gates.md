---
ttl: task_bound
---

# M7-06 · 合规门与程序化交易报告

> 挖矿班 st-commitspeed-tbl-20260924 ｜ 2026-09-25 ｜ 只读挖矿
> 边界：AI 行为合规（trae_044/LSG/redline 族）归 M3/M4；kill_switch 注册表限额面归 M3、交易五级熔断归 02 册；本册=执行链上的交易合规闸+程序化交易报告义务面。
> 交叉引用：01 册 B4（OrderManager 裸构造=合规门零注入）——本册给全量证据与处置序列。

## 一、环节定义与边界
把 2026-06-08/2025-07-07 程序化交易新规转译为订单路径上的机器闸：先报告后交易（C-002 三门）→会话级合规闸（C-004 三闸）→执行前四级闸（02 册）→报备/报告义务登记。上游=监管规则真源（供料），下游=order_manager.submit_order/trading_session（拦截执行）+Owner 人工报送动作（消费）。

## 二、六向台账
| 向 | 内容与实证 |
|---|---|
| 上游输入 | 监管真源：43_compliance_discipline.md（§7.4 先报告后交易/§8 日申报笔数/§7.3 盘中操纵/§4.3 纪律闸）；程序化新规两文（2025-07-07 实施细则→programmatic_trading_guard.py:12-14 引；2026-06-08 申报撤单口径→cancel_rate_guard.py:33 引）；规则 YAML 层=trae_044（合规治理审计，L1，human_gated） |
| 下游消费 | C-002 拦截点=order_manager._check_compliance_gates（`order_manager.py:356-418`，ComplianceGateBlockError ZA-EX-0011）；C-004 拦截点=trading_session._is_blocked_by_compliance_gates（`trading_session.py:979-1041`）；操纵冻结阻断=monitor.is_frozen→闸抛转（本层不接下单路径，`manipulation_realtime_monitor.py:8` INVARIANTS 自注）；compliance_log 落证据 |
| 自动化触发 | 盘中操纵流=事件驱动零定时器（on_order/on_cancel/on_trade 喂入，stream_driver:8）；批扫=intraday_manipulation_detector（MANIPULATION_BATCH_SCAN 自证清白落痕）；报送确认位=人工编辑 YAML 回填（registry:24-25"报送动作为人工（券商渠道）"）；纪律闸/熔断=逐单同步闸 |
| 真源与注册表 | 登记表=docs/01_policies_and_standards/_registry/catalogs/compliance_report_registry.yaml（REG-CMP-REPORT-001，6 项义务，tier_2，safety H）；代码门面=compliance/api/__init__.py（C-002 消费出口）；设计备忘=docs/_working/archive/2026-09/design_memos/43_compliance_discipline.md（**归档态真源**，见 B4） |
| 门禁与质量尺 | 全部闸 Fail-Closed：报告登记表不可读=BLOCK（registry INVARIANTS）；检测引擎失效=拒单（trading_session:995/1022/1070 三处 Fail-Closed 全捕获）；检测器与上下文必须成对注入否则 fail-fast（trading_session:326-329）；日申报计数同实例防护（cancel_rate_guard 双注入不同实例 raise，trading_session:342-346）；冻结须人工复解释放（release_freeze 留痕） |
| 当前运行状态 | **红**：闸代码全家族+56 测试绿（tests/compliance 21+ex_core 54 件含闸面）在库；**生产装配零注入**——6 处 OrderManager() 全裸构造、assemble_session 零 C-004 注入、programmatic_trading_guard 零实例化、操纵监测族零装配（详见三/四）；当前不构成在险违规的唯一原因是未实盘（S-1 锁着+未报备未交易），实盘准入 G5 前必闭 |

## 三、子模块清单（合规闸三层全景+程序化报告面；ls 27 件+grep 装配点三源交叉）
| 子模块 | 是什么 | 入口 file:line | 状态 |
|---|---|---|---|
| **C-002 订单级三门**（order_manager 内联闸，注入即生效/None 跳过） | | | |
| ReportGate（MOD-CMP-009） | 先报告后交易铁律：任一必报项 broker_ack 缺失→BLOCK 拒发 | compliance_report_registry.py:133（Decision :66/Result :87） | design 级模块+production 级闸逻辑；**零注入**（6 处裸构造实证见下） |
| 日申报笔数硬计数器 | CancelRateGuard.daily_declaration_status：≥5000 WARNING/≥10000 BLOCK；报单(:345)与撤单(:445)对称计数，成功失败均计（宁多勿漏） | cancel_rate_guard.py:98-108 阈值；order_manager.py:343-345 | 闸在；TradingSession 兜底自建实例只用于 can_place_order/can_submit_now（:829/:872）——**record_submit/record_cancel 在裸构造下永不触发**（仅在 order_manager 持 guard 时调用），即 1 万笔防线现役未激活 |
| 盘中操纵冻结闸（MOD-CMP-018） | monitor.is_frozen(symbol) 命中→拒新申报；监测失效→Fail-Closed 拒发（§7.6） | order_manager.py:401-418 | 闸在；**monitor 零装配→闸静默跳过**（None=不校验） |
| **C-004 会话级三闸**（trading_session，可选注入） | | | |
| KillSwitchLite（策略级熔断） | 触发策略当日禁新开仓，次日自动复位；状态存储失效→升级全局 Kill Switch（RC-03） | discipline_prohibition_checker.py:124-140（state 默认主仓 data/compliance_log/） | production；**assemble_session 零注入** |
| 四项严禁纪律闸（MOD-CMP-002） | 追高/补仓/报复=Hard Block，骄傲=WARNING；检测失效=保守 Hard Block | discipline_prohibition_checker.py:8 + trading_session.py:996-1019 | production；**零注入**（连同 ctx_provider 成对约束 :326） |
| 交易合规检测（MOD-CMP-007） | close_manipulation 等多类型检测，命中一律 Hard Block | trading_compliance_detector.py + trading_session.py:1025-1041 | production；**零注入** |
| **执行前四级闸**（细节归 02 册，此处列合规位） | 闸1 Kill Switch→闸1.5 blocks_live_trading（S-1 实盘门未解锁拒全单）→闸2 交易时段→闸3 快照→闸4 否决 | pre_execution_checker.py:23-25,233-316 | **已接线**（assemble_session attach_pre_execution_gate，start_paper_session:565） |
| **程序化报告/报备义务面** | | | |
| compliance_report_registry（REG-CMP-REPORT-001） | 6 项义务登记+确认位：①账户信息②软件信息③策略类型④最高申报速率⑤单日最高申报笔数⑥重大变更（T+1）；order_min_dwell_us=50 记录性参数（天然满足） | catalogs/compliance_report_registry.yaml:35-76 | **6 项全部 reported_at:null / broker_ack:false（实测）=报告从未报送**；门禁校验入口就绪 |
| programmatic_trading_guard（40 号 §决策⑱ gap18） | 实盘报备硬校验：策略/算法/服务器位置/风控 config hash/交易参数五项登记；启动(assert_can_start:514)+下单(assert_can_submit:551)双校验；PAPER/SIM 豁免、LIVE 必查；配置漂移检测(:584) | programmatic_trading_guard.py:273 | production 级；**零生产实例化**（grep 全仓唯一命中=自身 :278 示例） |
| **盘中操纵监测族**（检测规则唯一真源=TradingComplianceDetector，族内零重实现） | | | |
| trading_compliance_detector | 操纵类型判定核心（Wash/Spoofing 等，MOD-CMP-007） | trading_compliance_detector.py:36 | production；族内被三件复用 |
| manipulation_stream_driver | 30min 滚动窗口塑形+预筛，事件驱动零定时器 | manipulation_stream_driver.py:77 | 在；零外部装配 |
| intraday_manipulation_detector | 批扫层（首命中去重≤1 条/标的/日/类；零命中也落 MANIPULATION_BATCH_SCAN） | intraday_manipulation_detector.py:8,230 | 在；零外部装配 |
| manipulation_realtime_monitor | 流接线+告警+冻结分发（is_frozen 供 C-002 第三闸）；阻断走闸抛转不接执行 | manipulation_realtime_monitor.py:8,246 | 在；零装配（order_manager 仅 TYPE_CHECKING 预接线 :81） |
| info_asymmetry_manipulation_detector | 信息不对称操纵检测（304 行） | info_asymmetry_manipulation_detector.py | 在；零装配 |
| **合规域配套**（compliance/ 27 件其余） | | | |
| discipline_must_do_checker / compliance_policy_engine / compliance_rule_engine / hard_boundary_adjudicator / evidence_chain_generator / compliance_log | 必做清单/策略引擎/规则引擎/硬边界仲裁/证据链/合规日志底座 | compliance/ 各根文件 | compliance_log=production（6 件消费）；其余登记在案，执行链接线面同上待装配 |
| regulatory_change_tracker / compliance_drift_detector / compliance_continuous_ops / compliance_tech_enabler / async_intercept_queue / behavioral_auditor / license_usage_auditor / compliance_tech_enabler | 监管变化追踪/漂移检测/持续运营/技术使能/异步拦截队列/行为审计/许可审计 | compliance/ 各根文件 | 登记在案（治理面，多数归 M3 引用）；本册不判其接线 |

**装配点穷尽证据**（OrderManager 全仓 6 处构造，grep `OrderManager(`）：qmt_trading_session.py:115、qmt_file_bridge_integration.py:52、app_panel.py:524、start_paper_session.py:492、construction/demo_e2e_pipeline.py:326、construction/qmt_bridge_regression_smoke.py:230——**六处 report_gate/declaration_guard/manipulation_monitor 三参全默认 None**（grep 三参名于前四个生产文件零命中）。C-004 面：assemble_session 仅注入 risk_layer+pre_execution_gate（start_paper_session.py:563-565），checklist_checker/kill_switch/discipline_guard/compliance_detector 六可选参零注入。

## 四、堵点与病灶
| # | 现象/根因/修法/工作量/归属 |
|---|---|
| B1 | **P0：合规门全家族"码成闸空"**——C-002 三门+C-004 三闸+操纵监测族+报备 guard 共 12 件零生产装配，且 None=静默跳过（无告警无痕迹）。**接线顺序强约束**：ReportGate 接线即生效，而登记表 6 项 broker_ack=false→第一笔单即 BLOCK（fail-closed 正确行为，但意味着接线与人工报送必须同批编排：Owner 先走券商报送→人工回填 YAML 确认位→再接线，否则 paper 会话也全拒）。修法=①Owner 报送程序化交易报告（人工，外部周期）②assemble_session 注入三门三闸+monitor（同实例约束走 declaration_guard 复用）③programmatic_trading_guard 挂 live 档 assert_can_start。工程面 1-2 天+人工报送周期；**Owner 门位+G5 前置必做** |
| B2 | 1 万笔日申报防线现役未激活（B1 子症，单独列防漏读）：TradingSession 兜底自建 CancelRateGuard 只查不计数（record_submit 仅在 order_manager 持 guard 时触发），"防线存在"的假象来自测试（测试注入 guard 而生产不注入）。修法并入 B1② |
| B3 | 冻结闸依赖倒挂：monitor 不装配→is_frozen 闸静默跳过=操纵冻结保护 0；monitor 装配后若失效→Fail-Closed 全拒=可用性反噬。修法=装配+健康探针（monitor 心跳进 premarket_checker 清单）；并入 B1②，+0.5 天 |
| B4 | 真源归档张力：43_compliance_discipline.md 居 docs/_working/archive/2026-09/design_memos/（工作区归档目录）却是六模块 MODIFY-GUARD 指针真源。修法=升迁 docs/01_policies_and_standards/ 正式位或登记"设计态备忘"降级声明；0.5h+裁定；**待裁** |
| B5 | KillSwitchLite 默认 state_path 写主仓 data/compliance_log/（生产路径）——测试靠约定注入 tmp（宪法 §9.6 靠自觉）。修法=头注显式声明测试 MUST 注入+生产路径 env 化；0.5h；可施工 |

## 五、提速与合并机会
- 报告义务 6 项与 programmatic_trading_guard 报备 5 项有重叠字段（策略类型/申报速率/日笔数两处登记）——报送材料可一次组装双表回填（同真源可派生→必并方向，待 Owner 报送时实测合并）。
- 合规域 27 件单仓集中、api/__init__ 已是统一出口（C-002 消费面）——接线时从 api 层一次 import，勿散装根文件 import（保持出口唯一）。

## 六、自审闸三态
**挖干可施工**（闸家族 12 件+报告面 2 件+监测族 5 件全实证；装配点 6 处穷尽；B1 处置序列含人工报送编排明确）。B4 真源升迁挂待裁。**红→绿路径清晰但含 Owner 人工动作，非纯工程可闭**。

## 七、复核命令（10 分钟）
```bash
sed -n '356,418p' src/zephyr/ex_core/order_manager.py                 # C-002 三门全文
grep -rn "OrderManager(" src/zephyr scripts --include="*.py" | grep -v test  # 6 处裸构造穷尽
grep -c "broker_ack: false" docs/01_policies_and_standards/_registry/catalogs/compliance_report_registry.yaml  # =6
grep -rn "ProgrammaticTradingGuard(" src/zephyr scripts --include="*.py" | grep -v test  # 唯一命中=自身:278
sed -n '979,995p' src/zephyr/ex_core/trading_session.py               # C-004 闸序+Fail-Closed
sed -n '342,347p' src/zephyr/ex_core/trading_session.py               # 同实例防护+兜底自建（B2 实证）
```
