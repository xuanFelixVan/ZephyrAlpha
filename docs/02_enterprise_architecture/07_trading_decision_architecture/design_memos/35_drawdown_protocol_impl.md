---
ttl: permanent
doc_type: architecture_view
title: 回撤 Protocol 落地 spec
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.39.3"
date: 2026-08-15
topic: drawdown_protocol_impl
scope: 07_trading_decision_architecture
---

> ## 结案报告（2026-08-16 补记）
>
> **实际开发**：分两波——①2026-08-13 第一批（会话 AI-DRWD-001）落码 Kill Switch 链路 + detect_ghost_positions，81 测试通过；②2026-08-16 P0 风控接线批（RRESIL 原语层 dbc5d40e2b + RWIRE 消费层 2b3b68b5d2）把回撤熔断从"测试全绿但生产零实例化"接入真实链路：新建 state_store.py（JsonStateStore 原子写 + AppendOnlyDedupSet 崩溃残行容忍）、KillSwitch 状态落盘 Fail-Closed、LIQUIDATING 锁与单一仲裁点、启动时券商持仓全量重建 + fill_id 持久化去重 + Saga 超时终态查询。
>
> **最终成果**：红队双路实证（非 mock）——回撤 25% 触发 EMERGENCY、真实置位、MARKET SELL 清算全链；熔断重启存活；并发双触发只发一轮单；事件重放不重复；重建期禁单 Fail-Closed。风控层从"纸面熔断"转生产接线态。
>
> **未做事项及原因**：~~Redis 后端 state_store 未做——当前 JSON 文件后端已满足单机需求，登记后续批按同接口替换。~~ **✅ 已闭环（2026-08-17 AI-REDIS-001，merge e9d49313；2026-08-19 复核补正）**——RedisStateStore/RedisDedupSet 双后端 + 双工厂（`state_store_redis.py` 独立拆分防循环导入），与 JsonStateStore 同接口，65×2 测试全绿；db15 隔离登记已闭环。其余未做项（DrawdownStateMachine 持久化状态机/L2·L3 四层兜底/盘前-盘后持久化编排/回撤归因自动化）按本档 §6 优先级登记（P0-P4），属设计内延期非烂尾。

# 回撤 Protocol 落地 spec

> 本备忘记录回撤 Protocol 从 §2.5 框架到代码落地的选型推理、阈值裁决与上限定义。
> 性质：永久态设计记录，可随项目演进而修订，不是不可推翻的裁定。
> 管理规范见 [01_design_memo_management_spec](01_design_memo_management_spec.md)。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G16 回撤 Protocol 落地 |
| 所属 | 作战地图 09 + [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.5 |
| 依赖 | G12（仓位）—— 但框架已有，可并行 |
| 对标 | ARKA / LedgerMind / Sina 量化FOF / tradingwyckoff（§2.5 已引）；2026-08 行业补：TradeZella 三级协议 / algostrategyanalyzer Kill Switch / go-trader portfolio kill switch / BloFin 分阶段恢复 / JournalPlus 4 阶段恢复 / r1000-quant-engine hysteresis / dredyson 状态机 hysteresis；学术补：Nystrup/Boyd MPC / Noguer CVaR trend / RMATS / Uryasev CDaR / DLP-SMPC / MARCD / Man Numeric CVaR / Schmitt RWC / CVaR Risk-Aware Q-Learning / Conformal OCE；后续各轮登记见 §4.6-§4.28 / §6.8-§6.37 |
| 正交性 | ✅ 与 regime 正交（drawdown 是账户级，regime 是市场级） |
| 优先级 | P2（与 G12 并行） |
| 状态 | ✅ 已定稿（框架 §2.5 + 三层映射 + 阈值裁决 + 6 流程闭环 + 状态机 + Ghost 兜底 + A 股新规适配 + 回撤归因 + 盘后持久化 + Hysteresis + 毕业准则 + 远期登记 §4.6-§4.28/§6.8-§6.37 + 2026-08 实证/监管背书 + 通用规则 #11 盘点 + BM-RC-10/10-A/05-C/03-C 闭合）；v1.39.0 已施工 Kill Switch 平仓链路 + Ghost 检测（AI-DRWD-001，commit 1d814359，81 测试全绿，已 merge）；v1.39.1 压缩（AI-DOCS-001）；v1.39.2 第二轮循环压缩（AI-DC2-05） |

## 2. 背景

### 2.1 项目处境
- 个人 + 100% AI 开发，A 股个人账户（miniQMT 通道），非机构体量
- 回撤是账户生存风险的核心度量：20% 回撤需 25% 收益恢复，50% 回撤需 100%（[TradeZella 2026-04](https://www.tradezella.com/blog/drawdown-management) 恢复表）
- 30_multi_strategy_concurrency §2.5 已定四级框架（8/15/20/25%）+ 恢复机制 + Kill Switch，但**代码已先于框架落地了三套不同阈值的模块**，框架与代码存在口径分裂

### 2.2 核心问题：框架与代码的阈值分裂

§2.5.1 定义四级回撤阈值 8/15/20/25%（行业基准，LedgerMind/ARKA/Sina），但代码中存在**三套独立阈值体系**，且都比 §2.5.1 更紧：

| 体系 | 模块 | 阈值 | 性质 | 域 |
|---|---|---|---|---|
| A 监控告警 | `drawdown_tracker` (MOD-RK-011) | 5/10/15% 三级（WARNING/CRITICAL/EMERGENCY） | 实时报警，EMERGENCY 联动 Kill Switch | D_RISK |
| B 账户仓位节流 | `capital_curve_manager` (MOD-POS-007) | 5/10/15%+ 四级仓位上限 100/80/50/30% + 新高扩张 + 亏损收缩 | 仓位上限联动 | D_POSITION |
| C 综合响应 | `drawdown_controller` (MOD-POS-008) | VaR 驱动 5 级（GREEN/YELLOW/ORANGE/RED/BLACK）+ 策略 Soft/Hard 5/10% + 黑天鹅 7 模式 | 取最严综合裁决 | D_POSITION |

§2.5.1 的 8/15/20/25% 在代码中**无 1:1 对应模块**——代码用 5/10/15%（更紧）做早预警，用 VaR 驱动（不同维度）做综合响应。本备忘必须裁决：是改代码对齐 §2.5.1，还是改 §2.5.1 对齐代码，还是承认三层互补。

### 2.3 约束条件
- A 股 T+1，回撤发生后难以日内反转，早预警价值高于事后止损
- 个人系统无风控团队 7×24 盯盘，依赖自动触发 + 人工 reset
- Kill Switch 一旦触发需人工复位（`requires_manual_reset: True`，代码已实现），不可自动恢复（[ARKA 2026](https://completetradersedge.com/drawdown-protocol-traders/)：Recovery requires explicit re-authorization）
- drawdown 是沉没成本，不进入下次决策的 RiskSignal（[30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.5 用户裁定），只触发账户级风险节流

### 2.4 已施工设施盘点（2026-08-12 通用规则 #11 全面扫描）

> 通用规则 #11 要求的事实清单（扫描 `src/zephyr/{risk,position,ex_core,security,trading}` + `tests/` + `config/` + `schemas/` + `scripts/` + 三个注册表 YAML）。v1.39.0 起两项原"未施工"已落码（见 ④ 标注）。

**① 三层阈值模块（全部 production + 单测齐备，与 §2.2 三体系表一致）**

| 模块 | ID | 路径 | 阈值 | 测试 |
|---|---|---|---|---|
| DrawdownTracker | MOD-RK-011 | `src/zephyr/risk/core/drawdown_tracker.py` | 5/10/15% 三级告警（WARNING/CRITICAL/EMERGENCY），peak 单调非减 + 事件去抖 | `tests/risk/test_drawdown_tracker.py` 20 项 |
| CapitalCurveManager | MOD-POS-007 | `src/zephyr/position/core/capital_curve_manager.py` | 5/10/15% + 仓位上限 100/80/50/30% + 新高扩张 +5%（封顶 2x）+ 亏损收缩 10/20% | `tests/position/test_capital_curve_manager.py` 23 项 |
| DrawdownController | MOD-POS-008 | `src/zephyr/position/core/drawdown_controller.py` | VaR 5 级（2/4/6% + CVaR 10%）+ 策略 Soft/Hard 5/10% + 黑天鹅 7 模式 | `tests/position/test_drawdown_controller.py` 38 项 |

**② Kill Switch 三套实现（域分离，互不调用）**

| 实现 | ID | 域 | 语义 | 与本备忘的关系 |
|---|---|---|---|---|
| `stop_loss.py` + `DefaultRiskValidator` | MOD-L04-001 | D_RISK | 交易风控 Kill Switch：事件层（日志+返回 `requires_manual_reset: True` dict）+ 状态层（`_kill_switch_active` 布尔标志，`validate_order` 拒绝全部新订单）+ 执行层（`execute_kill_switch_liquidation` 平仓/撤单 15 笔/秒分片，v1.39.0 落码） | §3.5/§3.7 的主角 |
| `security/access_control/kill_switch.py` | MOD-INF-018 | D_SECURITY | AI 自治熔断器（VR-009 5 条件：Agent 越界/模型漂移 PSI/自治等级跳变/资源消耗/连续否决），NORMAL/TRIPPED/COOLDOWN 状态机，human_gated | battle_map BM-RC-03 锚点模块；与交易 Kill Switch 正交（管 AI agent 行为，不管账户回撤） |
| `trading/trading_contracts/risk/trading_kill_switch.py` | MOD-INF-016 | D_TRADING | 5 级熔断器数据模型注册表（POSITION_LIMIT / DAILY_LOSS `daily_pnl < -0.03*aum` / CIRCUIT_BREAKER / SECOND_LEVEL / API_TIMEOUT），含 cooldown + auto_reenable 标志 | §3.6 日度熔断的 DAILY_LOSS 类型承载——注意其阈值 **3%** 与 §3.6 裁决的组合层 4%、ashare 引擎 2% 是第三口径（见 §3.6 附注） |

**③ 支撑设施（已施工）**

| 设施 | 路径 | 与本备忘的关系 |
|---|---|---|
| DailyAuditor 日终清单 5 项 | `src/zephyr/risk/core/daily_auditor.py`（MOD-RK-20，46 项测试） | 第 4 项验证 Kill Switch 终态 == CLOSED（FAIL 判据 L803-820）；第 5 项数据完整性（§3.5.1 盘前持仓核对的扩展点）；`AttributionBias` 供 §3.16 因子归因 |
| AShareStopLossEngine | `src/zephyr/risk/core/ashare_stop_loss_engine.py` | 单标的止损默认 `daily_loss_limit=0.02`（2%，L137）——§3.6 已裁决其为单标的层级，与组合层 4% 不冲突 |
| daily_pnl_check 通用机制 | `risk_manager_base.py:108` 抽象 + `default_risk_manager_orchestrator.py:197` 实现 | §3.6 日度熔断承载者（阈值配置注入，不硬编码） |
| CancelRateGuard | `src/zephyr/ex_core/cancel_rate_guard.py`（production） | 撤单率 >12% 预警降级 / >15% 冻结 / 15 笔每秒限频——§3.5.1 A 股 2026 新规适配的撤单侧已落地 |
| ProgrammaticTradingGuard | `src/zephyr/ex_core/programmatic_trading_guard.py`（production） | 程序化报备（含日最大下单笔数/撤单率上限报备内容） |
| position_sizing_engine | `src/zephyr/position/core/position_sizing_engine.py` | 已消费 `capital_curve_discount` / `capital_curve_cap`（SizingInput L235-236，`total_cap=min(...)` L458）——§3.9 乘性叠加的工程落点 |
| AShareSystemicRiskDetector | `src/zephyr/risk/core/ashare_systemic_risk_detector.py` | 5 信号 3 级警报，LEVEL_3 联动 RK-17 Kill Switch——§3.5 黑天鹅 BS-007 的系统级产出方之一 |
| Task Scheduler watchdog | `scripts/deadman_switch.ps1` + `scripts/launch_hidden.vbs` | AtLogOn+PT5M 三服务看门狗（§3.5 ④ bare-metal recovery 佐证） |

**④ 未施工清单（标注"仅文档/未落码"；v1.39.0 已闭合两项）**

| 缺口 | 待裁定 | 现状 |
|---|---|---|
| RiskOrchestrator 统一编排器 | §6.5（P1） | ✅ 编排层已建（落地名 `RiskLayerOrchestrator`，MOD-L06-001，`src/zephyr/ex_core/risk_layer_orchestrator.py`，RWIRE-001 #ARCH-100）——三层喂入（drawdown/VaR/尾部/systemic→position_cap + Kill Switch 交战）已编排接线；§6.5 日度校准动作执行者语义仍=设计契约未接入；生产实例化经 `trading_session` risk_layer 注入缝（默认 None=未实例化），组合根装配待运行时装配批 |
| state_store 持久化层 + DrawdownStateMachine | §6.6 / §6.12（P1/P0） | 无代码；`capital_curve_manager.peak` / `drawdown_tracker` 窗口纯内存，重启即丢；architecture_issue_registry 已登记"Redis 状态外部化层"待办 |
| detect_ghost_positions | §6.11（P1） | ✅ 已施工（v1.39.0，commit 1d814359）：`stop_loss.detect_ghost_positions` + `DefaultRiskValidator.detect_ghost_positions` 双类型检测；盘前启动序列接入待 §6.12 |
| Kill Switch 平仓/撤单执行链路 | §6.11 / §6.14（P1/P0） | ✅ 已施工（v1.39.0）：`execute_kill_switch_liquidation` 15 笔/秒分片 ⌈N/15⌉ 批；L2 broker 端硬止损 + L3 看门狗进程仍缺（§6.11） |
| 独立 black_swan_detector 模块 | —（36 号契约） | 不存在；`BlackSwanSignal` 数据类定义于 drawdown_controller.py，`build_black_swan_signal` 无码，编排层抽象待 RiskOrchestrator |
| 前端回撤/Kill Switch 面板 | — | 未实现；`src/zephyr/frontend/`（MOD-L08-001）仅 stub + CTR-P1-008 RiskDashboardSnapshot 契约 |
| 回撤阈值 YAML 配置 | — | 无；阈值全部硬编码于各模块 dataclass 默认值；`config/risk_params.yaml` 的 `daily_loss_limit_nav_ratio: null`（未配置） |
| ClickHouse 净值曲线/回撤表 | §6.12 配对 | schemas/categories/ 下 100+ 表全为行情/基本面/宏观，无账户净值曲线表 |

**⑤ 注册表登记缺口（治理盘点发现）**

- `capability_canonical_file_registry.yaml`：drawdown_controller / daily_auditor / kill_switch（security）已登记；**drawdown_tracker / capital_curve_manager 无条目**（仅 blueprint_registry.yaml + module_translation_registry.yaml 有记录）——登记缺口，下次注册表维护批次补齐
- `module_translation_registry.yaml`：daily_auditor / ashare_stop_loss_engine 的 `name_zh` 系机器误抽取（取成了异常类名"日终审计输入数据非法"），引用时以 blueprint_registry 的 title 为准

**⑥ 盘点结论（对本文档既有论述的三点修正）**：

1. **§2.2"三套独立阈值体系"应精确化为"3+1"**——交易域还有第四套 `trading_kill_switch.py`（MOD-INF-016）5 级熔断器注册表，DAILY_LOSS 阈值 3% 是 §3.6 第三口径（框架 4% / 3% / ashare 2%；§3.6 裁决维持 4% 不变，production 33 项测试）
2. **§3.5 执行路径"平仓+撤单"已落码**（v1.39.0 `execute_kill_switch_liquidation`，commit 1d814359）——v1.38.0 缺口已闭合，见 §3.5 执行路径块
3. **15% EMERGENCY 是否触发 Kill Switch 存在跨真源口径分裂**（drawdown_tracker.py 注释 + BM-RC-03 支持 15%；30 号 §2.5.5 + §3.11 状态机支持 25%）——已登记 §7 ㉓ 开放问题，不擅自裁决

## 3. 决策：三层分离 + 代码优先 + §2.5.1 作为生存边界

### 3.1 核心裁决：承认三层互补，不改代码对齐 §2.5.1

**决策**：代码三套体系（A 监控 / B 节流 / C 综合响应）是**互补的三层防御**，不是矛盾。§2.5.1 的 8/15/20/25% 重新定位为**外层生存边界（regulatory-style floor）**，代码的 5/10/15% 是**内层早预警（tighter early warning）**。

理由：
1. **个人系统宁紧勿松**：5/10/15% 比 8/15/20/25% 早触发，符合用户"风险优先"偏好。行业基准 8% 是机构 AUM 体量下的容忍度，个人账户 5% 已该警觉。
2. **三层不同职责**：A 是"铃铛"（报警不行动）、B 是"节流阀"（降仓位上限）、C 是"总指挥"（综合多输入取最严）。强行统一阈值会破坏职责分离。
3. **改代码成本高且无收益**：三套模块均已 production + 有单测，改阈值引入回归风险，且 8/15/20/25% 比 5/10/15% 更松，是**降低**风控强度，与个人系统目标相悖。

### 3.2 三层映射表（§2.5.1 讨论要点 ① 的落地）

| §2.5.1 框架级 | 代码落地层 | 模块 | 阈值 | 动作 |
|---|---|---|---|---|
| Level 1 警告 8% | A+B 内层早预警 | drawdown_tracker + capital_curve_manager | 5% WARNING / 5% 仓位上限 80% | 报警 + 仓位上限降至 80% |
| Level 2 减仓 15% | A+B 中级 + C 策略 Hard Stop | drawdown_tracker CRITICAL + capital_curve CRITICAL + drawdown_controller Hard Stop | 10% CRITICAL / 10% 仓位上限 50% / 策略 Hard Stop 10% | 仓位上限降至 50% + 问题策略关闭 |
| Level 3 停仓 20% | A EMERGENCY + B EMERGENCY | drawdown_tracker EMERGENCY + capital_curve EMERGENCY | 15% EMERGENCY / 15% 仓位上限 30% + 仅防御 | 禁止新开仓 + 仓位上限降至 30% |
| Level 4 清仓 25% | C Kill Switch + 强制休息 | drawdown_controller Kill Switch advice → stop_loss | 25% 或 BS-007 系统性 | 全清 + Kill Switch + 强制休息 5 天 |

> **关键说明**：代码在 15% 已触发 EMERGENCY（最严告警 + 仓位上限 30%），比 §2.5.1 的 Level 3（20%）早 5 个百分点。§2.5.1 的 25% Level 4 = Kill Switch 全清，代码通过 `drawdown_controller` 的 BS-007（系统性风险，多模式同触发）或显式 25% 回撤阈值触发，委托 `stop_loss.trigger_kill_switch` 执行。

### 3.3 单策略 vs 组合分层（讨论要点 ②，§2.5.3 落地）

**决策**：分两层，由不同模块负责。

| 层面 | 模块 | 基准 | 触发动作 |
|---|---|---|---|
| 单策略层 | `drawdown_controller._evaluate_strategy_stops` | 各 StrategyBook 自身净值回撤 | Soft Stop（>5% 砍仓）/ Hard Stop（>10% 关闭策略），**不影响其他策略** |
| 组合层 | `capital_curve_manager` + `drawdown_controller` 系统性风险级 | firm 层总净值回撤 + VaR/CVaR | 所有策略同步收缩（仓位上限下调 + Shrinkage 额外下调） |

> 用户洞察（§2.5.3）："回撤深了是因为上一次交易没交易好，是策略的问题，不是市场的问题。"→ 单策略回撤 = 策略问题 → 该策略独立收缩；组合回撤 = 系统性问题 → 全局收缩。代码已实现此分离：`StrategyPnl.drawdown_pct` 喂入 `_evaluate_strategy_stops` 做单策略判定，`DrawdownInfo.drawdown_pct` 喂入系统性风险级做组合判定。

### 3.4 恢复机制（讨论要点 ③，§2.5.2 落地）

**决策**：恢复分两段，由 `capital_curve_manager` 和 `drawdown_controller` 分别实现。

| 阶段 | §2.5.2 框架 | 代码实现 | 模块 |
|---|---|---|---|
| 回撤企稳 | 回撤从峰值恢复 50% → 解除停仓，风险敞口仍降 50% | `recovered_pct >= 0.50` → `recovery_factor` 从 0.25 起，每步 +0.25（25%/50%/75%/100%） | drawdown_controller `_evaluate_recovery` |
| 完全恢复 | 创新高（回撤归零）→ 恢复正常 | 净值回到峰值 → `contraction` 自动解除，`expansion_factor` 保留累计扩张 | capital_curve_manager `record` |
| 强制休息 | Level 4 触发后强制休息 5 天 | **代码未实现**（Kill Switch `requires_manual_reset` 是人工复位，无自动 5 天计时） | 待裁定（见 §6.1） |

> 恢复是**逐步**而非跳变：`drawdown_controller` 的 `recovery_factor` 是乘性的（0.25→0.50→0.75→1.0），与风险级别 cap 相乘，避免"一恢复就满仓"的跳跃风险。与 [TradeZella 2026-04](https://www.tradezella.com/blog/drawdown-management) 三级恢复协议一致（25% size → 50% → 75% → full，需连续盈利日确认）。

> **分阶段恢复毕业准则**（真源 §3.20）：`recovery_factor` 阶梯升级前须满足 4 项毕业准则——① 连续 ≥3 个盈利日；② 近 10 笔交易平均期望 ≥ +0.3R；③ 规则合规率 ≥ 80%；④ 单笔最大亏损 ≤ 1.2R。数值达标但准则未达标则不升级（BloFin："Advance only when objective criteria are met"）。准则来源与理由详见 §3.20。

### 3.5 Kill Switch 触发与执行路径（讨论要点 ④，§2.5.5 落地）

**决策**：Kill Switch 是多源触发的单一执行通道，不可覆盖。

触发条件（多源 OR）：
| 来源 | 条件 | 模块 |
|---|---|---|
| 回撤 | 组合回撤 > 25%（§2.5.1 Level 4）或 drawdown_tracker EMERGENCY（15%，更紧）⚠️ 见下方口径矛盾标注 | drawdown_tracker / drawdown_controller |
| 单日亏损 | 单日亏损 > 6%（§2.5.5）或 daily_pnl_check 触发 DAILY_LOSS | stop_loss / default_risk_manager_orchestrator |
| 连续亏损 | 连续 5 天亏损 → 降仓至 50% | 待实现（见 §6.2） |
| 流动性危机 | 买卖价差 > 正常 5x | G18 流动性危机 Protocol（[37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md)） |
| 黑天鹅 | BS-007 系统性风险（多模式同触发） | drawdown_controller `_evaluate_black_swan` |
| 系统故障 | 连续拒单 ≥5 或价格偏离 >5%（CIRCUIT_BREAKER）/ 延迟 >1000ms 或成交率 <50%（SECOND_LEVEL）/ broker API 超时 >10s 或心跳丢失 ≥3（API_TIMEOUT） | `trading_kill_switch.py`（MOD-INF-016，D_TRADING 执行域熔断注册表，production，§2.4 ②）——系统故障维度由执行域 5 级熔断器承接，两域通过 RiskOrchestrator（§6.5）汇聚取最严；行业印证 [klawtrade 2026-04](https://klawtrade.com/blog/algorithmic-trading-risk-management-guide) 7 触发器含"3+ 系统错误/5 分钟" |

> **⚠️ 15% EMERGENCY 触发口径矛盾（登记 §7 ㉓ 开放问题，留业主裁决）**：本表"drawdown_tracker EMERGENCY（15%）触发 Kill Switch"与 §3.11 状态机（CRISIS=15%→仓位上限 30%，KILL 需 drawdown>25% 或 CVaR>10% 或 BS-007）+ 30 号 §2.5.5（回撤>25% 才清仓）三方口径分裂。**当前实际行为**：15% EMERGENCY 仅发射 E-RK-03 告警事件 + 仓位上限 30%（无 orchestrator 接线到 `trigger_kill_switch`，§6.5 未建），不会自动全清。本备忘倾向 15% 仅告警（25% 是 §2.5.1 生存边界）；证据三方/裁决候选 a)-c)/影响面全录见 §7 ㉓。

执行路径（v1.39.0 已全部落码）：
```
触发源 → drawdown_controller.kill_switch_advised=True          ✅ 已实现（BS-007 唯一自动建议路径）
       → stop_loss.trigger_kill_switch(reason, scope="all")    ✅ 已实现（事件记录层：日志+返回事件 dict）
       → DefaultRiskValidator.trigger_kill_switch() 置状态      ✅ 已实现（_kill_switch_active=True + CRITICAL 日志）
       → 平仓所有持仓 + 撤所有挂单                              ✅ 已落码（execute_kill_switch_liquidation，15 笔/秒分片）
       → 锁定新开仓                                            ✅ 已实现（validate_order 拒绝全部新订单）
       → requires_manual_reset: True（人工复位才能恢复）         ✅ 已实现（事件 dict 字段）
       → Ghost Position 检测                                   ✅ 已落码（detect_ghost_positions，双类型检测）
```

> ✅ 已施工（模块=drawdown_controller/kill_switch，commit 1d814359，81 测试，AI-DRWD-001）：v1.38.0 标注的"平仓/撤单执行链路未落码"缺口已闭合；reset 两层语义已统一——`DefaultRiskValidator.reset_kill_switch(confirmation)` 增 `holdings_verified_zero` 必填校验，对齐 stop_loss 事件层确认语义。`daily_auditor` 日终检查清单第 4 项验证 Kill Switch 终态 == CLOSED（FAIL 判据）。

> **COMPEL Framework Kill-Switch 四模式架构参考**（[COMPEL BoK AITL M9.3-Art02 v1.0, 2026-04-06](https://compelframework.org/articles/ai-agent-kill-switch-and-escalation-protocols)）——四种叠加停止模式（每模式 60 秒内可执行 + 自动升级 + 可逆状态保存 + 取证捕获）到本项目的映射：
> | COMPEL 模式 | 语义 | 本项目对应 | 现状 |
> |---|---|---|---|
> | Hard-stop | 立即终止进程，放弃在途工具调用 | §3.5 `trigger_kill_switch(scope="all")` 全平 + 撤单 + 锁新开仓 | ✅ 已实现 |
> | Graceful-halt | 完成当前原子动作后停止 | §3.4 recovery_factor 阶梯减仓（25%→50%→75%）+ §3.20 hysteresis min_hold | ✅ 已实现（恢复阶梯） |
> | Rollback | 回滚已执行的错误动作 | §3.5.1 Ghost Position 检测 + 异常订单撤销（待 §6.11） | ❌ 部分缺失（L2/L3 层） |
> | Scoped-disable | 禁用单一 agent 或能力 | 单策略 Soft/Hard Stop（§3.3）+ 策略级 circuit breaker（[37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md)） | ✅ 已实现 |
> 本项目已覆盖 Hard-stop/Graceful-halt/Scoped-disable 三模式，**Rollback** 是 §6.11 L2/L3 待施工部分。COMPEL 是语义分类框架非新模块。**VeritasChain Flight Recorder**（[2026-01-20](https://veritaschain.org/blog/posts/2026-01-20-five-incidents-algorithmic-trading-flight-recorder/)）append-only + prev_hash 哈希链 + Ed25519 签名 + RFC 8785 审计架构，§3.18 `daily_auditor.log_*` 远期向此标准演进（§6.31 待裁定）。

> **Unfireable Safety Kernel——架构级 kill switch（比 COMPEL 更根本）**（[arXiv:2606.26057](https://arxiv.org/abs/2606.26057)，Dobrin & Chmiel 2026-06-24 ARYA Labs）：kill switch 运行在 agent 地址空间之外。四属性：① 进程分离；② 唯一路径预执行强制；③ 请求级+系统级双重 fail-closed；④ Ed25519 签名证据日志。COMPEL 管"怎么停"，Unfireable 管"停不掉"，两者正交。§3.5.1 L3 看门狗是其思路的部分实现，登记 §6.31 远期——L3 施工时参考四属性。性能参考：Microsoft Agent Governance Toolkit 内核强制 0.103ms，对 A 股日频/T+1 无瓶颈。

> **Novotny Herding 相图触发**（[arXiv:2607.08907](https://arxiv.org/abs/2607.08907)，Novotny 2026-07-09）：单边订单簿事件比例 φ_∅≈0.34 处识别流动性压力交叉点（rule-robust 0.227 / horizon-robust 0.32-0.35），与 §3.5 ⑦ ORCA/Weng 收益分布层面 herding 检测正交——φ_∅ 是订单簿微观结构触发器。**登记 §6.31 远期候选**：L3 接入 Level 2 行情后作微观结构预警，需 A 股实证校准 φ_∅（涨跌停使单边事件更频繁）。

> **Li et al. Agent Swarm circuit breaker 实证参数**（[arXiv:2604.27150](https://arxiv.org/abs/2604.27150)，2026-04 Oxford + Vela Research）：900+ 交易、8960 配置全网格，最强配置 1.0×ATR 止损 + 2.0×ATR 止盈 + **连续 2 次亏损后 reduction factor 0.25**。与 §3.3 drawdown 阈值驱动正交可叠加。**登记 §3.3 增强 Phase 2 候选**（2 连亏→仓位×0.25，3 连亏→Soft Stop，需 A 股实证校准 ATR 倍数）。

### 3.5.1 Kill Switch 执行失败兜底（4 层架构 + Ghost Position）

**问题**：§3.5 假设 `trigger_kill_switch` 一定成功，但实际 broker 可能拒单（如 FOMC/政策行情 CME reserved state）、部分成交、连接中断，导致**幽灵持仓**（Ghost Position）——平仓指令发出但未成交，持仓无人管理。nexusfi 2026-06 实证 [@Breukelen 2022 案例](https://nexusfi.com/a/automation/automated-trading-emergency-protocols)：Kill Switch 触发后 CME 拒单，14 手 ES 无主暴露，仅靠 78 微秒的 bracket stop 残留单侥幸平仓。

**4 层防御架构**（[nexusfi 2026-06](https://nexusfi.com/a/automation/automated-trading-emergency-protocols) 四层独立设计，每层捕获上层遗漏）：

| 层 | 职责 | 触发 | 本项目现状 |
|---|---|---|---|
| L1 代码层 | `stop_loss.trigger_kill_switch` 发市价平仓 + 撤挂单 | drawdown_controller.kill_switch_advised | ✅ **已施工**（v1.39.0，commit 1d814359：`execute_kill_switch_liquidation` 15 笔/秒分片 ⌈N/15⌉ 批 + 逐笔异常汇总；事件记录 + 状态置位 + 新开仓拒绝此前已落码）；生产接线对账（v1.39.3，RWIRE-001 完工现实）：`risk_layer_orchestrator`（MOD-L06-001）生产代码已调用 `trigger_kill_switch`/`execute_kill_switch_liquidation`，经 `trading_session` risk_layer 可选注入装配（默认 None=未实例化） |
| L2 平台层 | broker 端硬止损单（bracket/OCO），不依赖策略连接 | 开仓时同步挂 broker 端 stop | ❌ **缺失**（miniQMT 通道需确认是否支持 broker-side bracket） |
| L3 看门狗层 | 独立进程监控"持仓 vs 策略状态"一致性，不一致即强平 | 定时轮询 broker 持仓 vs DefaultRiskValidator 状态 | ❌ **缺失** |
| L4 人工层 | 人工复位 + 持仓清零确认（§3.7 `requires_manual_reset`） | Kill Switch 触发后强制 | ✅ 已实现 |

**Ghost Position 检测**：✅ 已施工（模块=kill_switch，commit 1d814359，81 测试）——`stop_loss.detect_ghost_positions(broker_holdings, strategy_state, kill_switch_state)` + `DefaultRiskValidator.detect_ghost_positions(broker_holdings, strategy_state)`（复用 `_kill_switch_active` 状态）→ `ghosts` 列表；双类型 `strategy_closed_but_broker_holds` / `kill_switch_closed_but_position_remains`，同标的去重。盘前启动序列接入待 §6.12。

> **裁决**：L1 + L4 已实现（代码层 + 人工复位），L2/L3 暂缓为 §6.11。理由：① 个人系统 miniQMT 通道的 broker-side bracket 支持待确认（A 股 ETF/股票的 OCO 单支持情况需实测）；② L3 看门狗需独立进程，与当前单进程架构不一致，且 A 股 T+1 下"日内幽灵"窗口小（无法日内反转，最坏盘后清零）。但**盘前必须做一次持仓核对**（`daily_auditor` checklist 第 5 项数据完整性扩展），若 Kill Switch == CLOSED 但 broker 仍有持仓 → 拒绝开新仓 + 立即人工告警。

> **多维 Kill Switch 参考框架**（[Tidball 2026-05](https://fxmacrodata.com/articles/kill-switch-framework-for-ai-fx-bots)）：分层 kill switch 栈，每维度独立刹车、任一触发即暂停——与本项目 4 层架构互补（4 层按**执行路径**分层，Tidball 按**触发维度**分层）：
> | Tidball 维度 | 检测内容 | 本项目对应 | 状态 |
> |---|---|---|---|
> | ① 数据完整性 | 时间戳新鲜度/字段完整性/跨源一致性 | `daily_auditor` checklist 第 5 项 + 55_monitoring_review | ✅ 已实现 |
> | ② 模型行为 | schema 解析失败率/策略违规次数/无支撑高置信 | §3.12 行为性回撤诊断 + §3.16 归因 | 🟧 待施工 §6.7 |
> | ③ 执行异常 | 滑点/拒单率/延迟 | 40_execution_broker CancelRateGuard + 撤单率监控 | ✅ 已实现（v2.6.0） |
> | ④ 组合回撤 | session -1.25%/daily -2.0%/最大相关敞口 | §3.5 Kill Switch + §3.6 日度熔断 + §3.13 盘中循环 | ✅ 已实现 |
> | ⑤ 事件窗口 | 重大数据发布前暂停 | §3.14 黑天鹅事件监控（36号 §3.14）政策黑天鹅 | 🟧 待施工 |
> **核心原则印证**：① **"fail closed"**（监控不可用默认 halt）——§3.15 盘前 `RefuseStart` 即 fail closed；② **"安全状态必须在模型外计算"**——`stop_loss` 独立于 `drawdown_controller`（仅 `kill_switch_advised` 单向交接）。Tidball 框架作为 §6.11 4 层架构施工的**维度检查清单**。

**A 股 2026 程序化交易新规对 Kill Switch 执行的影响**（[csdn 2026-08-08](https://blog.csdn.net/syp1110/article/details/163276625)）：

2026-04-07 生效、7-07 全面执行的《程序化交易管理实施细则》对 Kill Switch 平仓执行链路施加新约束：

| 新规约束 | 数值 | 对 Kill Switch 的影响 |
|---|---|---|
| 每秒申报上限 | 15 笔（原 300 笔） | 全清多持仓时，若持仓标的 >15 只，**1 秒内无法全部平仓**——需分批拆单 |
| 每秒撤单上限 | 15 笔 | 撤所有挂单时同样受限，撤单风暴会触发异常交易监控 |
| 单日撤单率上限 | 15% | Kill Switch 触发后大量撤单可能撞日撤单率红线 |
| 每笔报单最小停留 | 50 微秒 | 市价平仓单的提交节奏受限，无法"瞬时全清" |

**对 §3.5 Kill Switch 执行路径的修正**：

1. **持仓 >15 只时需分批平仓**：全清 N 只持仓需 ⌈N/15⌉ 秒——窗口内持仓仍暴露于市场风险（Ghost Position 风险窗口扩大）
2. **撤单需计数**：撤挂单前检查"今日已撤单率"，若接近 15% 红线，优先撤关键挂单（如大额/远离市价的），放弃小额挂单让其自然到期
3. **拆单算法**：全清平仓应用 TWAP/VWAP 拆单（2026 新规下执行标配），而非裸市价单——但与 Kill Switch"尽快平仓"目标冲突，需权衡

> **裁决**：Kill Switch 平仓执行需适配 A 股 2026 新规，但**不改变"尽快全清"原则**——拆单是为合规，不是为追求好价格。最小实现：① `trigger_kill_switch` 内部按 15 笔/秒分片提交市价平仓单（非 TWAP 优化）——✅ 已施工（v1.39.0）；② 撤单前检查日撤单率，超 12% 预警（留 3% buffer）——待 §6.11/§6.14；③ 全清完成确认（polling 所有持仓归零，Ghost 检测）需考虑分片延迟，超时（如 30 秒未全清）即告警人工介入——待 §6.11/§6.14。

**2026 年全球监管趋势对 Kill Switch 独立性与审计的强化要求**（[BoE 2026-06-30 Sintra Forum](https://hotminute.co.uk/2026/07/05/kill-switches-for-the-stock-market-inside-the-bank-of-englands-ai-contingency-planning/) + [SEBI 2026-05](https://clearyourexam.com/current-affairs/sebi-new-framework-algorithmic-trading-enhanced-corporate-governance)）：

> - ① **多 agent herding 风险**——BoE 副行长 Breeden（Sintra 2026-06-30）：核心风险是多 agent 对相同触发相似反应导致 herding（"a thousand well-governed trading agents can still stampede together"）；BoE/BIS/Bundesbank 联合压力模拟探索市场级 kill switch。本项目 4 层防御（§3.5.1）+ 统计检测（§4.8/§4.18）正是对"AI 决策失效"的多层兜底。
> - ② **独立 Kill Switch 物理隔离**——SEBI 2026-05 强制 Kill Switch 与主交易逻辑物理隔离 + 算法报备 + 实时监控。`stop_loss` 独立于 `drawdown_controller`（仅 `kill_switch_advised` 单向交接）满足；§3.7 不可覆盖与 SEBI 人工复位要求一致。
> - ③ **事后审计不可绕过**——BoE 要求触发后提交失效原因诊断审计报告。`daily_auditor` 清单第 4 项（终态 == CLOSED）+ 第 5 项（数据完整性 + 持仓核对）覆盖。
> - ④ **circuit breaker vs kill switch 语义区分 + 监管时间线**（[BoE FPC 2026-07-07](https://integrated.social/blog/bank-of-england-ai-governance-circuit-breakers-financial-stability-2026/)）——circuit breaker = 临时可恢复暂停，kill switch = 永久/长期终止：§3.7 对应 kill switch 语义，37 号对应 circuit breaker 语义，分层正交。时间线：BoE DP Q3 2026 → FCA Dear CEO Q4 → PRA binding rules 2027 → 全面执行 2028。**deterministic output gating + bare-metal recovery**：output gating 须在 agent reasoning loop 之外 + 物理隔离恢复能力——`stop_loss` 独立 + Task Scheduler watchdog + `daily_auditor` 独立审计进程满足。
> - ⑤ **Herding 定量背书**——[GeomHerd arXiv:2605.11645](https://arxiv.org/abs/2605.11645)：价格相关性 herding 检测滞后 272 步（agent-interaction graph Ollivier-Ricci 曲率领先 40 步）；[arXiv:2604.03272](https://arxiv.org/abs/2604.03272)（SEC 13F 全样本）：AI 系统性风险尾部损失放大 **18-54%**，乘子 M=(1-r)^{-1} 在 AI 渗透率上超线性增长。Phase 2 候选：监控决策图层面策略相关性（GeomHerd 思路），而非仅价格相关性（HBI/CSAD 属价格维度，滞后 272 步）。
> - ⑥ **"证明而非声称" + 行业就绪度**——[Bailey 2026-07-23 开放信](https://resultssense.com/news/2026-08-05-bank-of-england-frontier-ai-testing/)要求以压力/渗透测试"证明"AI 韧性而非"声称"；[Wolters Kluwer 2026 调研](https://coresystempartners.com/core-insider/the-kill-switch-gap/)：72% 银行 AI 治理最薄弱环节是 kill-switch 协议（34%）或故障报送（38%）——"未测试的 kill switch 不是 kill switch"：§6.11 施工必须做 tabletop 测试与实盘断电演练；[FCA Mills Review 2026-07](https://investx.fr/en/crypto-news/fca-agentic-ai-tokenized-money-financial-disruption/) 要求算法决策可追溯 + 自动 circuit breaker + 强化报送。
> - ⑦ **Herding 检测可施工替代（GeomHerd 轻量化路径）**——[ORCA arXiv:2604.17251](https://arxiv.org/abs/2604.17251)（Kriuk 2026-04）：24 ETF 滚动相关矩阵 + **127 谱特征** + RF 8 折 walk-forward，BCD-AUC=0.741、谱特征对 crash 检测贡献 +10.3pp、Sharpe 1.13 / CAGR 15.6% / **MaxDD -7.5%**；[Weng arXiv:2607.27063](https://arxiv.org/abs/2607.27063)（2026-07-29）：A 股 CSAD/LSV + **Johnson S_U 变换滚动尾部 herding 指标**，专门针对 A 股。定位：⑤ GeomHerd 是决策图层面远期愿景，⑦ ORCA+Weng 是价格相关性层面可施工替代——Phase 2 候选（待 §6.7 施工后评估），与 31/32 号 HBI/CSAD 互补。
> - ⑧ **FSB AI 稳健实践咨询报告——全球监管顶层锚点**（[FSB 2026-06-10](https://www.fsb.org/2026/06/sound-practices-for-responsible-adoption-of-artificial-intelligence-ai-consultation-report/)，G20 框架 12 项 SP）——"AI monitoring AI"（人工监督不可扩展，用独立系统监控生产 agent）印证 §3.5.1 L3 看门狗 + §6.31 + Unfireable；**bounded authority**（AI agent 视为 synthetic employees）印证 §3.7 不可覆盖 + COMPEL Scoped-disable；agentic AI 放大风险（unauthorized actions / goal misalignment / reward hacking）印证 §3.21。**适用性**：咨询性质不具法律约束力（最终版 2026-10 提交 G20），SP3/SP9/SP10/SP11 对个人系统适用——本项目 Kill Switch + 审计 + Ghost 检测 + watchdog 已隐式覆盖核心要求。治理框架非施工算法，不新增独立模块。

### 3.5.2 风险否决权与否决执行引擎（作战地图 BM-RC-10 / BM-RC-10-A 闭合，design）

> 作战地图全覆盖补丁——BM-RC-10（风险否决权，L4 风控域，design）与 BM-RC-10-A（否决执行引擎，BM-RC-10 子环节，design）在本备忘落地。BM 环节定义真源：风险架构.md §3 风险否决权 / §3.2 否决执行机制。

**定位**：
- **BM-RC-10 风险否决权**：风控规则触发否决条件 / 交易请求拦截 → 否决/放行，数据流"交易请求→否决规则检查→否决/放行→隔离记录→BM-RC-03 Kill Switch"。code_mapping：待开发（planned，D_RISK 域）。
- **BM-RC-10-A 否决执行引擎**：策略信号到达订单执行入口前，否决规则引擎**同步拦截**判定放行/否决。code_mapping：待开发（planned，D_RISK 域；Kill Switch 需 miniQMT API 支持）。

**裁定**：否决执行引擎**登记为设计裁决、纳入 §6.11/§6.14 施工批次**，不提前落码。理由：
1. **与 Kill Switch 单一通道同源**：否决引擎是 §3.5"多源触发单一执行通道"在**订单入口侧**的延伸——Kill Switch 管存量（平仓/撤单/锁新开仓），否决引擎管增量（每笔下单前置拦截）；两者共用 `DefaultRiskValidator._kill_switch_active` 状态层与 `validate_order` 拦截点，构成"存量+增量"双闸门，不可绕过原则是同一原则的两个应用面（HC-RISK-03：所有下单必经引擎无旁路）。
2. **当前代码已覆盖否决的 MVP 子集**：`DefaultRiskValidator.validate_order` 在 kill_switch_active 时拒绝全部新订单（severity=HALT）即是"单规则否决"的已实现形态；BM-RC-10-A 完整否决规则集是 §6.5 RiskOrchestrator 施工时的扩展，MVP 阶段单独建引擎属过度工程。
3. **与 §3.5 既有施工缺口同批次衔接**：否决引擎（增量拦截）与 KS 平仓链路（存量出清）同属 D_RISK 执行层缺口，须在同一施工批次统一设计（共用 execution_broker 接口 + 审计通道），避免两套订单拦截点、旁路风险翻倍。

**重评条件**：① §6.5 RiskOrchestrator 统一编排器施工启动（P1）；② 实盘出现"非 Kill Switch 类的单规则否决需求"（单标的黑名单 / 单策略禁开仓 / 日历类否决）频次 ≥1 次/月；③ 40_execution_broker 下单入口封装层接口冻结后（否决引擎须挂在唯一入口上才满足 HC-RISK-03）。

**契约/参数/接口**（建设项必填，施工时冻结）：

| 项 | 裁决值 | 来源 |
|---|---|---|
| 同步拦截延迟预算 | **P99 < 50ms**——下单热路径同步拦截，超时即熔断（注意：BM-RC-11-A 的"每 Tick 3 秒"是指标计算节奏非拦截预算，拦截以 <50ms 为准） | BM-RC-10-A params |
| 不可绕过 | 所有下单必经引擎无旁路（HC-RISK-03）；防御性决策自动执行、不可人工否决（HC-RISK-02）；Kill Switch 在基础设施层实现（非 Agent 运行时内） | BM-RC-10-A params |
| 与策略逻辑隔离 | 否决规则集独立于策略代码部署（独立模块 + 独立配置），策略进程不可读改否决规则；规则变更走审计通道留痕 | BM-RC-10 params"否决与策略逻辑隔离" |
| 否决规则集结构 | 规则 = {rule_id, 条件表达式（限额/持仓/行情/Kill Switch 状态）, 动作（REJECT/HALT）, 严重级, 生效窗口}；规则集按域分组（限额规则/持仓规则/日历规则/Kill Switch 规则），求值取最严（任一 REJECT 即否决） | BM-RC-10 consumes"风控策略+持仓状态+交易请求+BM-RC-01 限额配置" |
| 熔断器模式 | 否决引擎自身 5 次失败/60 秒 → OPEN 全拒（fail-closed）→ 30 秒 HALF-OPEN 探针 → CLOSED；引擎不可用 → Kill Switch 激活（宁可停交易不可绕过风控） | BM-RC-10-A degradation |
| 多路径激活 | AI 自动 <1ms / 人工 <100ms / 定时熔断（5 秒无心跳）/ 外部信号 <1s | BM-RC-10-A params |
| 否决审计追踪 | 每条否决记录 {时间, 规则, 触发值, 被否决指令, 执行者}，append-only 日志（远期对齐 §6.31 VeritasChain 哈希链标准） | BM-RC-10-A params |
| 降级 | 否决机制失效 → 硬阻断交易（安全优先，fail-closed） | BM-RC-10 degradation |

> **与 §3.5.1 4 层架构的关系**：否决执行引擎是 L1 代码层"锁定新开仓"能力的**规则化扩展**——当前 `validate_order` 只有 kill_switch 单条规则，BM-RC-10-A 将其泛化为可配置规则集。L3 看门狗层施工时须同步校验"否决引擎未被绕过"（混沌工程验证：定期注入故障验证不可绕过性，BM-RC-10-A params 隔离策略三机制之一）。

### 3.6 日度熔断（讨论要点 ⑤）

**决策**：日度熔断由 `daily_pnl_check`（通用机制）+ Kill Switch `DAILY_LOSS` 类型承载，阈值可配置。

| 触发 | §2.5.1 框架 | 代码现状 | 裁决 |
|---|---|---|---|
| 组合单日亏损 | > 4% → 暂停开仓 1 天 | `daily_pnl_check(daily_pnl, loss_limit)` 通用，`ashare_stop_loss_engine` 默认 2% | 采用 §2.5.1 的 4%（比代码默认 2% 宽，但作为组合层熔断合理；单策略层仍可用 2%） |
| 单策略单日亏损 | > 5% → 该策略暂停 1 天 | 无独立模块，走 `StrategyPnl` + Soft Stop | 采用 5%，由 `drawdown_controller` 策略级止损承载（Soft Stop 5% 砍仓） |

> 日度熔断是"时间维度"的风控，与回撤（"幅度维度"）正交。`daily_pnl_check` 不绑定具体阈值、由配置注入，是正确抽象。`ashare_stop_loss_engine` 的 2% 默认值是**单标的止损**层级（更紧），与组合层 4% 不冲突。
> **日度熔断的第三口径**：`trading_kill_switch.py`（MOD-INF-016）`KillSwitchLevel.DAILY_LOSS` = `daily_pnl < -0.03 * aum`（**3%**），CANCEL_ALL + DISABLE_NEW、cooldown 86400s、auto_reenable=False（33 项测试）。三口径并存：框架裁决 4%（组合层，本备忘采用）/ trading_kill_switch 3%（交易域）/ ashare 引擎 2%（单标的层）——层级不同不构成矛盾，RiskOrchestrator（§6.5）施工时须明确"以哪一口径为组合层唯一生效值"；当前裁决维持 4%，3%/2% 作为更紧内层（先触发者先生效，取最严原则自动成立）。

> **周/月两级亏损限额与强制复盘链路（作战地图 BM-RC-05-C 闭合，design）**：
> **定位**：BM-RC-05-C 亏损限额强制停盘（L4 风控域，design，code_mapping：CAND-HARVEST-0135 候选 D-RISK-27 A-Share Stop-Loss）——日/周/月三级亏损限额判定 → 强制停盘 1-3 天 + 强制复盘，输入日/周/月累计盈亏（D-EX-CORE），输出停盘指令 → BM-POS 仓位调整。
> **裁定**：在既有"组合日亏 >4% 停开仓 1 天"基础上**补周/月两级组合层限额**：**周累计亏损 >5% → 停开仓 2 天；月累计亏损 >10% → 停开仓 3 天**。三级联动取最严（任一触发即生效，停盘天数取 max）。理由：① 日级管"单日急跌"，周/月级管"阴跌累积"（A 股 T+1 下阴跌不触发日级熔断）；② BM 阈值表"日 2%/周 5%/月 10%"中日 2% 是 CAND-HARVEST-0135 **单标的止损层级**（ashare 引擎默认 2% 已实现），组合层日级维持 §2.5.1 框架 4%，周 5%/月 10% 为组合层口径与 BM 一致；③ 停盘 1/2/3 天对齐 BM"强制停盘 1-3 天"递进，与 Kill Switch"强制休息 5 天"（§3.2 Level 4）保持梯度。**重评条件**：实盘 ≥6 月后若周/月级触发频次 >2 次/季度（过敏感）或同期组合回撤超 15% 而两级均未触发（过宽松），回测校准阈值。
> **契约/参数/接口**：周亏损 = 自然周（周一开盘 NAV → 当前 NAV）累计收益率；月亏损同理；数据源 = D-EX-CORE 累计盈亏；触发动作 = `DISABLE_NEW` + 天数冷却——承载机制复用 `trading_kill_switch.py`（MOD-INF-016）cooldown 模式扩展 `WEEKLY_LOSS` / `MONTHLY_LOSS` 两类型（对齐 `DAILY_LOSS` 语义，周/月级不 CANCEL_ALL 仅 DISABLE_NEW）；降级 = 限额引擎未就绪 → 人工监控停盘（BM-RC-05-C degradation 原值）。
> **强制复盘链路**：三级限额任一触发 → 除停盘外**强制复盘**，由 [55_monitoring_review](55_monitoring_review.md) §3.6 复盘编排器承载——日级触发并入当日自动复盘（四段模板：盈亏归因/偏离告警/参数变更/action items）；周级触发强制升档为**人工周复盘**（熔断触发的周复盘不可裁剪跳过）；月级触发除人工月复盘外，须经 §3.16 回撤归因流程产出归因报告后方可申请恢复开仓——月级停盘后的恢复视同一次"软 Kill Switch 复位"，走 §3.14 ResetConfirmation 确认链（owner 确认 + 根因分析留痕）。

### 3.7 Kill Switch 不可覆盖原则（讨论要点 ⑥）

**决策**：不可覆盖，代码已实现。

- `trigger_kill_switch` 返回 `requires_manual_reset: True`，无 `auto_reset` 通道
- `reset_kill_switch(confirmation)` 需 `confirmed_by` + `override_reason`，留审计日志
- 状态由 `DefaultRiskValidator` 集中管理，非调用方可绕过
- 行业印证：[Punch 2026](https://builderslab.punch.trade/help/articles/1440242-use-kill-switch-to-lock-trading-on-punch-desktop)："You cannot turn it off early. That's the point."；[go-trader 2026](https://github.com/richkuo/go-trader/issues/25)："Manual reset required to resume (no auto-restart)"
- Knight Capital 2012 年 45 分钟亏 $440M 是无 Kill Switch 的前车之鉴（[algotradingdesk 2026-03](https://algotradingdesk.com/kill-switch-mechanisms-hft-risk-control/)）

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-RC-03-A | 触发条件判定 | §3.5 多源触发条件表 | production 已建 |
| BM-RC-05 | A股特色止损 | §3.3 策略 Soft/Hard Stop + §3.6 日度熔断 | production 已建（与 42_sell_flow 分工：42 号承载个股层六种止损模式 BM-RC-05-A，本篇承载策略/组合层止损与日度熔断联动） |
| BM-RC-05-B | 通用止损引擎 | §3.5 / §3.7 Kill Switch 触发链 | production 已建（与 42_sell_flow §2.4 分工：42 号盘点个股止损 4 法，本篇承载组合层 Kill Switch 触发与不可覆盖原则） |

### 3.8 回撤基准净值口径（讨论要点 ⑦）

**决策**：peak NAV（高水位，high watermark），由 `capital_curve_manager` 维护。

- `peak` 单调非减（`capital_curve_manager` INVARIANTS：peak 单调非减；`drawdown_tracker` 同）
- `drawdown = (current_nav - peak_nav) / peak_nav`，≤ 0
- 净值口径：已实现盈亏驱动的本金（`capital_curve_manager` docstring："跟踪已实现盈亏驱动的净值曲线"），非市值浮动
- 盈利扩张：每次创新高 → `expansion_factor` +5%（封顶 2x 初始本金），复利累计
- 亏损收缩：回撤 > 5% 缩 10% / > 10% 缩 20%（瞬时乘子，净值回峰值自动解除）

> peak NAV 是行业标准（[algostrategyanalyzer 2026-01](https://algostrategyanalyzer.com/en/blog/drawdown-trading-guide/)：DD = (Peak - Trough) / Peak × 100）。`capital_curve_manager` 的扩张/收缩机制是本项目的增量——标准 peak NAV 只追踪，不主动扩张资金基础。

### 3.9 与 regime Shrinkage 协同（讨论要点 ⑧）

**决策**：正交分工，通过 budget 数字交接，不互相调用。

| 风险类型 | 归属 | 触发 | 动作 |
|---|---|---|---|
| 市场状态风险 | regime Shrinkage（[34_regime_meta_allocator](34_regime_meta_allocator.md)） | regime 置信度低 | 缩 `Shrinkage_i` → 缩各策略 budget 占比 |
| 账户生存风险 | 回撤 Protocol（本备忘） | 账户回撤 / VaR 突破 | 降仓位上限 / Kill Switch |

> 两者**乘性叠加**：`final_position_cap = regime_shrinkage × drawdown_protocol_cap`。regime 管"现在该多谨慎"（市场级，前馈），drawdown protocol 管"已经亏了多少该怎么办"（账户级，反馈）。[30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.5 定位：drawdown 是账户级，regime 是市场级——正交，可并行。regime 不读 drawdown，drawdown protocol 不读 regime；两者各自独立算出系数，在 `position_sizing_engine` 相乘。

**乘性叠加 vs 加性惩罚的选型理由**：[RMATS 2026](https://arxiv.org/abs/2605.25311) 的 Risk Agent 用 RL 目标函数 `R_t = r_t − λ₁σ_t − λ₂max(0, DD_t − θ)`（λ₁=0.8, λ₂=1.5），是**加性惩罚**。本项目选**乘性**，理由：① 乘性保证"任一因子为 0 则总仓位为 0"（Kill Switch 或 regime 极端时彻底停仓），加性做不到（收益高时惩罚被稀释）；② 乘性是仓位上限的天然语义（`cap = a × b`，两者都是 [0,1] 系数），加性是收益目标语义；③ 乘性各因子独立可解释可拆解归因，加性混合后难归因。RMATS 加性适合 RL 端到端目标，本项目乘性适合规则式风控模块化叠加。

### 3.10 施工流程算法（日度风控循环）

**现状**：代码无统一编排入口——三模块各自独立，由调用方手动编排（`drawdown_controller.evaluate()` 需依次喂入 `drawdown_info` / `var_cvar` / `black_swan` / `strategy_pnls`）。

**日度风控循环伪代码**（待施工编排器，参考 [nexusfi 2026-06](https://nexusfi.com/a/automation/automated-risk-controls) 三层防线编排）：

```python
def daily_risk_loop(trade_date, positions, nav, returns, strategy_pnls, realized_pnl,
                    state_machine, var_cvar, var_breach_state,
                    fills=None, limit_consumption=None):
    # 输入契约：state_machine 由 §3.15 InitializationResult 产出（evaluate 依赖当前态执行 §3.11 转换守卫）；
    #   var_cvar 由 36号 §3.1/§3.2 产出经 RiskOrchestrator 传入（产出方统一为 36号，本函数仅消费）；
    #   var_breach_state 由 36号 §3.15 VarBreachStateMachine 产出（对齐 36号 §3.17 衔接规则 2）；
    #   fills/limit_consumption 为盘中累积态，由 §3.13 IntradayResult 产出，盘后审计消费
    # 盘前：更新净值曲线 + 计算回撤（A 层监控 + B 层节流）
    curve = capital_curve_manager.record(nav, realized_pnl)
    dd_info = drawdown_tracker.update(nav)  # DrawdownInfo(drawdown_pct, peak, recovered_pct)
    # entry_var：当日盘前 var_cvar.var_95 存 state_store（§3.18 阶段 4b），供次日 §3.15 加载 + §3.16 归因对比
    # 盘前：综合裁决（C 层取最严，乘性叠加 var_breach 折扣 NORMAL=1.0/BREACHED=0.8/RECOVERY=0.9）
    response = drawdown_controller.evaluate(
        drawdown_info=dd_info, var_cvar=var_cvar, strategy_pnls=strategy_pnls,
        black_swan=black_swan_detector.scan(),
        var_breach_state=var_breach_state)  # 不传则 multiplier 恒 1.0，36号协同逻辑失效
    # response.position_cap 已含 var_breach 折扣（effective_cap = base_cap × multiplier）；
    # 双 RECOVERY 叠加：effective_cap = 阶梯值 × 0.9 + 下限 max(0.0)；双恢复 >20 交易日发 DUAL_RECOVERY_PROLONGED 告警
    # 盘前：Kill Switch 检查（最高优先级，不可覆盖）
    if response.kill_switch_advised:
        stop_loss.trigger_kill_switch(reason="drawdown_protocol", scope="all")
        return DailyRiskResult(var_cvar=var_cvar, response=response, plan=None, audit=None)
    # 仓位裁决（乘性叠加 regime × drawdown × VaR）
    plan = position_sizing_engine.size(PositionSizingInput(
        symbols=..., nav=nav,
        capital_curve_discount=curve.contraction_factor,  # B 层节流
        capital_curve_cap=curve.position_cap,              # B 层上限
        defensive_only=response.only_close,                 # C 层禁开仓
        var_95=var_cvar.var_95, cvar_95=var_cvar.cvar_95,   # C4/C5 约束
        market_regime=regime_shrinkage.regime))             # regime 层
    # 盘后：日终审计（checklist 第 4 项 Kill Switch 终态 == CLOSED；第 5 项数据完整性）
    audit = daily_auditor.audit(trade_date, positions, fills, limit_consumption)
    # 交接链：response → §3.13 盘中循环；var_cvar.var_95 → §3.16 归因 + §3.18 持久化；
    #   plan → RiskOrchestrator（§6.5）→ execution_broker（MVP 由调用方直传；Kill Switch 提前返回时 plan=None）；
    #   audit → §3.18 阶段 0 审计门控（audit.passed=False 不持久化；提前返回时 audit=None）
    return DailyRiskResult(var_cvar=var_cvar, response=response, plan=plan, audit=audit)
```

**编排责任归属**（待裁定 §6.5）：当前由上游 `default_risk_manager_orchestrator` 部分承载。第二阶段建 `RiskOrchestrator` 统一编排，避免调用方遗漏喂入某一层（如只喂 drawdown 忘喂 var_cvar，导致 C 层降级）。

### 3.11 恢复状态机形式化

**现状**：`DrawdownController` 用 `SystemicRiskLevel` 枚举（GREEN/YELLOW/ORANGE/RED/BLACK）表达级别，但**无持久化状态机**——每次 `evaluate()` 重新计算级别，不记忆上一态，无转换守卫（如"RED 必须经过 RECOVERY 才能回 GREEN"）。

**目标状态机**（参考 [nexusfi 2026-06](https://nexusfi.com/a/automation/automated-risk-controls) 5 态确定性转换 + [completetradersedge 2026-04](https://completetradersedge.com/drawdown-protocol-traders/) Red→Amber→Green 不可跳级）：

```
NORMAL(100%) → WARN(80%) → DANGER(50%) → CRISIS(30%) → KILL(0% 全清)   【回撤加深，单调升级】
    ↑                                                    │ 人工复位 + 持仓清零确认
    └── 创新高 ← RECOVERY（仓位阶梯 25→50→75%）←──────────┘
                 降级恢复须经 hysteresis 半阈值 + min_hold + 毕业准则（§3.20），不可跳级
```

**转换规则**：

| 当前态 | 触发（升级） | 下一态 | 恢复条件（降级，§3.20 hysteresis） | 约束 |
|---|---|---|---|---|
| NORMAL | drawdown > 5% 或 VaR > 2% | WARN | — | 单调升级 |
| WARN | drawdown > 10% 或 VaR > 4% | DANGER | drawdown < **2.5%** + VaR < 2% 持续 3 日 + min_hold 5 日 | 降级经 hysteresis 半阈值 |
| DANGER | drawdown > 15% 或 VaR > 6% | CRISIS | drawdown < **5%** + VaR < 4% 持续 3 日 + min_hold 10 日 | 降级经 hysteresis 半阈值 |
| CRISIS | drawdown > 25% 或 CVaR > 10% 或 BS-007 | KILL | drawdown < **7.5%** + VaR < 6% 持续 5 日 + min_hold 20 日 | Kill Switch 不可覆盖（§3.7） |
| KILL | 人工复位 + 持仓清零确认 | RECOVERY | —（仅人工复位） | `requires_manual_reset: True` |
| RECOVERY | recovered_pct ≥ 50% | RECOVERY（仓位 25→50→75% 阶梯）| — | recovery_factor 乘性递增 + 毕业准则（§3.20） |
| RECOVERY | 创新高（drawdown = 0）| NORMAL | — | 完全恢复，expansion_factor 保留 |
| RECOVERY | drawdown > 15%（恢复期二次回撤超 CRISIS 阈值）| KILL（仅阶梯耗尽 step<0）/ RECOVERY retreat（阶梯未耗尽 step≥0）| — | §3.14 代码为分级保护——先 retreat_recovery_step 回退一级，仅 recovery_step<0（阶梯 0 再回退→耗尽）才转 KILL；表码已对齐。行为差异：step=2 时需连续 3 日 dd>15% 才到 KILL（2→1→0→-1），非单次即 KILL |
| RECOVERY | drawdown > 10%（恢复期回撤加深超 DANGER 阈值）| RECOVERY（retreat_recovery_step，仅 step>0）/ 无动作（step=0 已到最低阶梯）| — | §3.14 代码有 `if recovery_step > 0` 守卫，step=0 时 10-15% 区间不回退（已到最低 25% 阶梯）也不 KILL（未到 15%）——此区间在 step=0 为保护矩阵空档，由 freeze(>5%) 兜底 |
| RECOVERY | drawdown > 5%（恢复期回撤加深超 WARN 阈值）| RECOVERY（freeze 5 日）| — | §3.14 恢复期轻度回撤冻结阶梯 5 日，不退级。此规则无 step 守卫，全阶梯生效（含 step=0），是 step=0 时 5-15% 区间的唯一保护 |
| 任意态 | 多源触发取最严 | 最高态 | — | [nexusfi](https://nexusfi.com/a/automation/automated-risk-controls)："the most severe state wins. Always." |

> **降级/恢复规则**（§3.20 形式化）：升级触发阈值与降级恢复阈值**不对称**（hysteresis 双阈值）——恢复阈值取触发阈值的 50%（半阈值）+ 持续时间门控（min_hold 5/10/20 交易日）+ 毕业准则（连续盈利日 + 10 笔期望 ≥ 0.3R + 合规率 ≥ 80%）。避免状态机在临界阈值附近 thrashing。详见 §3.20。

**代码差距**（待施工 §6.6）：① **无状态持久化**——级别每次重算，无"上一态"记忆，无法判断"是否经过 RECOVERY"；② **无转换守卫**——RECOVERY 可直接跳回 NORMAL（跳过阶梯），与 §3.4 `recovery_factor` 阶梯冲突；③ **无"不可跳级"约束**——CRISIS 回 NORMAL 无强制经过 RECOVERY，存在"刚 CRISIS 立即满仓"风险；④ **无 hysteresis 双阈值**（§3.20）——降级用与升级相同的阈值，临界态 thrashing 风险，需半阈值 + min_hold + 毕业准则三重守卫

> 当前代码的 `recovery_factor`（0.25→0.50→0.75→1.0）在数值上实现了阶梯，但无状态机守卫保证"必须经过 RECOVERY 态"，也无 hysteresis 双阈值防 thrashing。第二阶段建 `DrawdownStateMachine` 持久化状态 + 转换守卫 + §3.20 hysteresis 恢复算法。

### 3.12 统计性 vs 行为性回撤诊断

**决策**：回撤触发后先诊断类型，再决定响应。参考 [completetradersedge 2026-05](https://completetradersedge.com/advanced-drawdown-management/) 5 问诊断矩阵。

| 诊断问题 | 统计性回撤（方差） | 行为性回撤（执行失败） |
|---|---|---|
| 信号是否严格按策略规则生成？ | 是——与盈利期一致 | 否——规则被 AI 弯曲/遗漏 |
| 止损是否每次执行？ | 是——平均损失 ≈ 1R | 否——止损被放宽，平均损失 > 1.2R |
| 仓位是否按 Kelly 算法一致？ | 是 | 否——报复性加仓 |
| 交易频率是否在计划内？ | 是 | 否——过度交易 |
| 市场结构是否质变？ | 否——类似盈利期 | 可能——regime 转换策略未覆盖 |

**响应分流**：
- **统计性回撤**（多数）：策略正期望，方差产生亏损簇 → 按 §3.2 三层映射减仓，继续执行
- **行为性回撤**（少数）：AI 执行偏差导致 → **停止实盘 + daily_auditor 归因 + 修正执行逻辑**，不减仓继续

> 个人+100%AI 系统的特殊性：行为性回撤 = AI 执行偏差（信号生成正确但执行层偏差），而非人类情绪失控。`daily_auditor` 的 `AttributionBias` 检测（预测因子占比 vs 实际占比）是诊断行为性回撤的工具。当前代码无显式的"回撤类型诊断"步骤，待 §6.7 施工。

### 3.13 盘中实时风控循环

**问题**：§3.10 日度循环覆盖盘前/盘后，但 A 股盘中 4 小时（9:30-11:30, 13:00-15:00）的**单日亏损熔断**（§3.6 组合 -4%/单策略 -5%）需盘中检测，不能等盘后。当前 `daily_pnl_check` 是通用函数，但无明确的盘中调度循环。

**盘中循环伪代码**（参考 [nexusfi 2026-06](https://nexusfi.com/a/automation/automated-trading-emergency-protocols) polling loop 验证 + A 股 T+1 约束）：

```python
def intraday_risk_loop(trade_date, market_open, market_close, opening_nav, strategy_states, response=None):
    """盘中实时风控循环：每 N 秒轮询，检测单日亏损熔断 + Kill Switch 状态。
    trade_date: 交易日期；opening_nav: 当日开盘 NAV（§3.15 产出，单日亏损熔断基准）；
    strategy_states: {strat_id: StrategyState(opening_nav, ...)}；
    response: §3.10 DailyRiskResult.response（position_cap / kill_switch_advised 作盘中初始边界）。
    A 股 T+1 约束：盘中无法反转昨日买入，最坏只能"禁止新开仓 + 信号化减仓建议"（持仓次日可卖）。
    Returns: IntradayResult(fills, limit_consumption)——盘中累积成交 + 限额使用，供 §3.10 盘后审计消费"""
    # 盘中累积态初始化（§3.10 盘后审计的消费对象）
    fills = []                  # 当日成交列表，盘中逐笔累积
    limit_consumption = LimitConsumption()  # 限额使用情况（A 股 2026 新规：每秒15笔/撤单率15%）
    # 盘前裁决约束传入盘中（§3.10 DailyRiskResult.response → §3.13）
    if response and response.kill_switch_advised:
        risk_validator.enforce_kill_switch_closed()  # 盘前已触发 Kill Switch，盘中保持
    # 盘前 position_cap（如 0.8=减仓 20%）作盘中仓位约束初始边界；盘中重算触发更严约束则取最严覆盖
    if response and response.position_cap is not None:
        position_sizing_engine.apply_premarket_cap(response.position_cap)
    poll_interval = 30  # 秒，A 股 Level-1 行情 3 秒/笔，30 秒足够
    while market_open <= now < market_close:
        # ── 1. 拉取实时未实现 PnL + 累积当日成交 ──
        unrealized = broker.get_unrealized_pnl()
        realized_today = broker.get_realized_pnl(trade_date)
        daily_pnl = unrealized + realized_today
        new_fills = broker.get_fills_since(last_poll_time)  # 自上次轮询以来的 fill 事件
        fills.extend(new_fills)
        limit_consumption.update(new_fills)  # 更新笔数/撤单率/限额使用
        nav = capital_curve_manager.current_nav + daily_pnl
        # 2. 单日亏损熔断（§3.6 组合 -4% / 单策略 -5%）
        if daily_pnl_check(daily_pnl, loss_limit=-0.04 * opening_nav):
            # 组合单日 -4% → 暂停新开仓（A 股 T+1 无法强平昨日仓）
            risk_validator.set_daily_loss_halt(scope="all")
            alert("DAILY_LOSS 组合 -4%", severity=CRITICAL)
        strategy_pnls_today = broker.get_strategy_pnls_today()  # 按 strategy_id 分组的当日 PnL
        for strat_id, strat_state in strategy_states.items():
            pnl = strategy_pnls_today.get(strat_id, 0.0)
            if daily_pnl_check(pnl, loss_limit=-0.05 * strat_state.opening_nav):
                # 单策略单日 -5% → 该策略暂停
                risk_validator.set_daily_loss_halt(scope=strat_id)
                alert(f"DAILY_LOSS 策略 {strat_id} -5%", severity=WARNING)
        # 3. 盘中回撤重算（高频更新 drawdown_tracker）
        dd_info = drawdown_tracker.update(nav)  # 用含浮盈的 nav
        if dd_info.alert_level == EMERGENCY:  # 15% 回撤
            # A 股 T+1：无法强平昨日新买，但禁止新开仓
            risk_validator.set_emergency_halt(scope="all")
            # 收盘前 5 分钟强制检查：14:55 后检测到 EMERGENCY 则在 14:57 收盘集合竞价提交减仓单
            # （可卖既有持仓），非一味推迟 next_open
            from datetime import timedelta
            if now >= market_close - timedelta(minutes=5):  # 14:55 后（收盘前 5 分钟）
                position_sizing_engine.queue_auction_reduce("closing_auction")  # 14:57 集合竞价减仓
                alert("收盘前 EMERGENCY 回撤，14:57 收盘集合竞价减仓", CRITICAL)
            else:
                position_sizing_engine.queue_opening_reduce("next_open")  # 非收盘前→次日开盘减仓
        # 4. Kill Switch 状态轮询（防 Ghost Position，§3.5.1）
        if risk_validator.kill_switch == CLOSED:
            # 聚合各策略预期持仓与 broker 实际持仓对比（strategy_states 是 dict {strat_id: StrategyState}）
            expected_holdings = aggregate_expected_holdings(strategy_states)
            ghosts = detect_ghost_positions(broker.get_holdings(), expected_holdings)
            if ghosts:
                alert(f"Ghost Position 检测到: {ghosts}", severity=EMERGENCY)
                # 不自动强平（A 股 T+1 + 可能误判），人工介入
        # 5. 盘中 VaR/ES 重算触发（与 36号 §3.12 协同）
        # §3.17 总览规则 4：回撤循环检测到"日内突破盘前 VaR"时触发 VaR 重算。
        # 跨文档契约对齐 36号 §3.12："35号 §3.13 intraday_risk_loop 检测到触发条件后调用本函数"
        var_trigger = intraday_var_recalc_trigger(
            trade_date=trade_date, market_open=market_open, market_close=market_close,
            current_nav=nav, current_dd=dd_info.drawdown_pct,
            current_exposure=position_sizing_engine.current_exposure(),
            universe_size=len(positions),
        )
        if var_trigger is not None:
            # 触发条件命中 → 调用 36号 §3.12 重算 VaR/ES
            intraday_var_result = intraday_var_recalc(
                trade_date, current_nav=nav, current_returns=broker.get_intraday_returns(),
                trigger=var_trigger,
            )
            # 用新 var_cvar + breach_state 重新裁决（取最严覆盖盘前 response）
            new_response = drawdown_controller.evaluate(
                drawdown_info=dd_info,
                var_cvar=intraday_var_result.var_cvar,
                strategy_pnls=strategy_pnls_today,
                black_swan=black_swan_detector.scan(),
                var_breach_state=intraday_var_result.breach_state,  # 36号 §3.15 新 breach_state
            )
            # 取最严：新 position_cap 更低时覆盖盘前 response（对齐 §3.8 取最严原则）
            if new_response.position_cap < response.position_cap:
                response = new_response
                position_sizing_engine.apply_intraday_recalc(response)  # 应用更严约束
                alert(f"盘中 VaR 重算触发更严裁决: cap={response.position_cap}", WARNING)
            # intraday_var_result.significant_change → 记录供日终回测分析（36号 §3.12 已记录日志）
        last_poll_time = now  # 记录本次轮询时间，供下轮 get_fills_since
        sleep(poll_interval)
    # 收盘后：交出盘中累积态，由 §3.10 日度循环的盘后审计接管
    return IntradayResult(fills=fills, limit_consumption=limit_consumption)
```

**裁决**：盘中循环暂缓为 §6.5 编排器的一部分。理由：① 当前系统以日度决策为主（盘前选股+盘后审计），盘中仅执行已定计划；② A 股 T+1 下盘中熔断动作受限（无法强平昨日仓），价值低于期货市场；③ 但**单日 -4% 告警**必须盘中触发（不能等盘后），故最小实现是盘中每 30 秒拉一次未实现 PnL，超阈值即告警 + 禁新开仓。完整循环待 RiskOrchestrator（§6.5）施工时一并落地。**同 tick 调用方接入（37 号流动性危机 Protocol 的盘中联动）同为待做项**——37 号 circuit breaker 触发信号须在同 tick 传入本循环的取最严裁决（对齐 §3.5 触发条件表"流动性危机"行），随 §6.5 一并落地。

### 3.14 Kill Switch 复位 → RECOVERY → NORMAL 端到端流程

**问题**：§3.4 讲恢复机制（两段恢复 + recovery_factor 阶梯），§3.11 讲状态机（5 态转换），但缺乏"Kill Switch 触发后，从人工复位到完全恢复 NORMAL"的端到端施工流程。当前代码 `reset_kill_switch` 仅清状态，无 RECOVERY 阶梯守卫（§3.11 代码差距 2）。

**端到端流程伪代码**（对照 §3.11 状态机 KILL→RECOVERY→NORMAL 转换）：

```python
def kill_switch_recovery_flow():
    """人工复位 → RECOVERY 阶梯 → 创新高回 NORMAL。
    前置：Kill Switch 已触发（§3.5），持仓已清零（§3.5.1 Ghost 检测通过），requires_manual_reset == True。"""
    # 阶段 0 人工复位（KILL → RECOVERY 入口）：Kill Switch 执行 = 平仓 + 撤单 + 锁新开仓（§3.5 三项动作），
    # 复位确认须校验全部 3 项——仅校验持仓清零（1/3）可能残留未撤挂单复位后意外成交，或锁新开仓未生效即复位
    confirmation = ResetConfirmation(
        confirmed_by="owner", override_reason="root_cause_analyzed_and_fixed",
        holdings_verified_zero=True,       # ① §3.5.1 Ghost 检测：持仓已清零
        orders_cancelled_verified=True,    # ② 所有挂单已撤（防复位后意外成交）
        new_open_locked_verified=True)     # ③ 锁新开仓已生效（RECOVERY 25% 上限 ≠ 禁开仓）
    if not confirmation.holdings_verified_zero:
        raise RefuseReset("持仓未清零，存在 Ghost Position，拒绝复位")
    if not confirmation.orders_cancelled_verified:
        raise RefuseReset("存在未撤挂单，复位后可能意外成交，拒绝复位")
    if not confirmation.new_open_locked_verified:
        raise RefuseReset("锁新开仓状态未确认，拒绝复位")
    # KILL→RECOVERY→KILL 循环守卫：次数上限 + 冷却期 + 永久锁定（防根因未修复反复复位）
    # 设计依据：[Tidball 2026-05] 复位治理 + [Iyer 2026-01] BOCPD 调参经验
    reset_history = state_store.load_reset_history(window=20)  # 近 20 交易日复位记录
    total_resets = state_store.load_total_reset_count()        # 累计复位总次数
    MAX_RESETS_PER_WINDOW = 3       # 20 日内最多复位 3 次
    COOLDOWN_DAYS = 3               # 复位后强制冷却 3 交易日（期间保持 KILL）
    PERMANENT_LOCK_THRESHOLD = 5    # 累计 5 次复位→永久锁定，需外部根因验证解锁
    if total_resets >= PERMANENT_LOCK_THRESHOLD:
        daily_auditor.log_permanent_lock(trade_date, total_resets=total_resets)
        raise RefuseReset(f"累计复位 {total_resets} 次超阈值 {PERMANENT_LOCK_THRESHOLD}，永久锁定")
    if reset_history and (trade_date - reset_history[-1].date).days < COOLDOWN_DAYS:
        raise RefuseReset(f"距上次 KILL 不足 {COOLDOWN_DAYS} 交易日冷却期，拒绝复位")
    if len(reset_history) >= MAX_RESETS_PER_WINDOW:
        raise RefuseReset(f"近 20 日复位 {len(reset_history)} 次超上限 {MAX_RESETS_PER_WINDOW}，拒绝复位")
    state_store.record_reset(trade_date, reason=confirmation.override_reason)
    state_machine.transition(KILL, RECOVERY, confirmation)  # recovery_factor = 0.25（仓位上限 25%）
    # 阶段 1 RECOVERY 阶梯恢复（25% → 50% → 75% → 100%）：
    # 每级需满足 ① recovered_pct 达标 ② 连续 N 个盈利日（TradeZella 三级恢复协议）
    while state_machine.current == RECOVERY:
        dd_info = drawdown_tracker.update(current_nav)
        if dd_info.recovered_pct >= 0.50 and state_machine.recovery_step == 0:
            state_machine.advance_recovery_step()  # 0.25 → 0.50
            daily_auditor.log_recovery_step(1, dd_info)
        elif dd_info.recovered_pct >= 0.75 and state_machine.recovery_step == 1:
            state_machine.advance_recovery_step()  # 0.50 → 0.75
            daily_auditor.log_recovery_step(2, dd_info)
        elif dd_info.recovered_pct >= 1.0 - 1e-6 and state_machine.recovery_step == 2:
            # 创新高（epsilon 比较，不做 drawdown_pct == 0 浮点等值检查）→ §3.11 RECOVERY→NORMAL
            state_machine.transition(RECOVERY, NORMAL, reason="new_high_watermark")
            daily_auditor.log_full_recovery(dd_info)  # expansion_factor 保留（§3.8）
            break
        # 阶梯期回撤加深保护：三级分级响应（对齐 §3.11 WARN/DANGER/CRISIS 阈值；仅 >15% 回退会留 5-15% 空档）
        dd_abs = abs(dd_info.drawdown_pct)  # drawdown_pct ≤ 0，取绝对值
        if dd_abs > 0.15:        # CRISIS 阈值 → 回退一级；阶梯耗尽（step<0）→ 回 KILL
            state_machine.retreat_recovery_step()
            if state_machine.recovery_step < 0:
                state_machine.transition(RECOVERY, KILL, reason="relapse_during_recovery")
                alert("恢复期二次回撤 >15%，Kill Switch 重触发", CRITICAL)
                return  # 等待下一次人工复位
        elif dd_abs > 0.10:      # DANGER 阈值 → 回退一级（step=0 已到最低阶梯不回退）
            if state_machine.recovery_step > 0:
                state_machine.retreat_recovery_step()
                daily_auditor.log_recovery_retreat("drawdown_10pct_during_recovery", state_machine.recovery_step)
        elif dd_abs > 0.05:      # WARN 阈值 → 冻结升级 5 日（不退级；无 step 守卫，
            state_machine.freeze_recovery_progression(days=5)   # step=0 时 5-15% 区间唯一保护）
            daily_auditor.log_recovery_freeze(reason="drawdown_5pct_during_recovery")
        wait_next_trading_day()
    # 阶段 2 NORMAL 正常运行（recovery_factor = 1.0，expansion_factor 保留 §3.8）
    risk_validator.clear_recovery_mode()
```

**代码差距**（待施工 §6.6）：
1. **无 `state_machine` 对象**——当前 `DrawdownController` 无持久化状态，`reset_kill_switch` 仅清 Kill Switch 标志，不进入 RECOVERY 态
2. **无 `recovery_step` 阶梯计数器**——`recovery_factor`（0.25→0.50→0.75→1.0）虽在 `_evaluate_recovery` 中按 `recovered_pct` 计算，但无"阶梯不可跳级"守卫（§3.11 代码差距 2）
3. **无"恢复期回撤加深保护"**——RECOVERY 期间再次回撤应回退阶梯或回 KILL，当前代码无此逻辑
4. **无 `ResetConfirmation.holdings_verified_zero`**——`reset_kill_switch` 不强制验证持仓清零，存在 Ghost Position 复位风险（§3.5.1）

> **裁决**：端到端流程暂缓为 §6.6 DrawdownStateMachine 施工的输入规约。当前 MVP 用人工复位 + `recovery_factor` 阶梯（数值上实现，无状态机守卫）足够；完整流程待持久化状态机落地。最小补丁：`reset_kill_switch` 增加 `holdings_verified_zero` 必填校验（防 Ghost Position 复位）——✅ 已施工（v1.39.0）。
> **多域通知 Saga 裁定（作战地图 BM-RC-03-C 闭合，production 补强）**：BM-RC-03-C（Owner 确认重置与多域通知，L4，production，MOD-INF-018）定义 Owner 确认重置后的**多域通知 Saga**（D-AUTONOMY→D-EXECUTION→D-PORTFOLIO，无补偿），输出 KillSwitch=OPEN 恢复开仓 → BM-RC-02-E 盘前检查放行。**裁定**：MVP 阶段**不建独立 Saga 编排器，多域通知由现公告警通道承载**——复位确认通过本节阶段 0 校验后，`daily_auditor.log_*` 审计日志（D_AUTONOMY 侧留痕）+ `alert()` 告警推送（D_EXECUTION / D_PORTFOLIO 侧通知）+ `state_store.record_reset` 持久化三通道同步完成"通知"语义；显式 Saga 编排登记远期，归 §6.5 RiskOrchestrator 施工批次。理由：三域通知均为幂等动作，MVP 单进程架构下 Saga 编排价值不显著，Owner 人工确认本身是最强一致性闸门。**重评条件**：§6.5 RiskOrchestrator 落地或 L3 看门狗层独立进程化（§6.11）后，通知链路升级为显式 Saga 并补失败重放。

### 3.15 盘前初始化与跨重启状态恢复

**问题**：§3.10-§3.14 覆盖日度循环/盘中循环/复位流程，但缺**系统启动环节**——每交易日盘前如何加载持久化状态、与 broker 持仓核对、校准各模块基线。系统重启后若不恢复 DrawdownStateMachine 持久化状态，会丢失"上一态是 RECOVERY 还是 NORMAL"的记忆，导致 §3.11 转换守卫失效（nexusfi 2026-06 "Reconnection and State Recovery" 失败域）。

**盘前初始化伪代码**（对照 §3.11 状态机 + §3.5.1 Ghost 检测）：

```python
def premarket_initialization(trade_date):
    """盘前初始化：broker 持仓核对 → 加载状态机 → 基线校准 → Kill Switch 状态确认。
    顺序不可调换：先核对持仓（防 Ghost），再加载状态机（防基于错误持仓恢复），最后校准基线。"""
    # 阶段 1 broker 持仓核对（防 Ghost Position，§3.5.1）
    broker_holdings = broker.get_holdings()           # 实盘真实持仓
    strategy_state = state_store.load_strategy_state()  # 策略认为的持仓（None=冷启动/首次）
    # 冷启动守卫：None 时若 broker 有持仓则全部视为 Ghost（无策略记录却有持仓→来源不明），空仓正常通过
    ghosts = (list(broker_holdings.keys()) if broker_holdings else []) if strategy_state is None \
        else detect_ghost_positions(broker_holdings, strategy_state)
    if ghosts:
        alert(f"盘前 Ghost Position 检出: {ghosts}", severity=EMERGENCY)
        risk_validator.set_emergency_halt(scope="all")
        return RefuseStart("存在 Ghost Position，拒绝启动，需人工清零持仓")
    # 阶段 2 加载 DrawdownStateMachine 持久化状态（§3.11，恢复"上一态"记忆使转换守卫生效）
    persisted_state = state_store.load_drawdown_state(trade_date)
    if persisted_state is None:  # 首次启动或状态丢失 → 默认 NORMAL（保守：不假设上次在 RECOVERY）
        state_machine = DrawdownStateMachine(current=NORMAL, recovery_step=0)
        daily_auditor.log_state_recovery("cold_start_default_NORMAL")
    else:
        state_machine = DrawdownStateMachine(current=persisted_state.current,
            recovery_step=persisted_state.recovery_step, last_transition=persisted_state.last_transition)
        daily_auditor.log_state_recovery(f"restored_{persisted_state.current}")
    # Kill Switch 终态校验：上次收盘 == CLOSED → 盘前保持 CLOSED（人工复位才能解除）
    if persisted_state and persisted_state.kill_switch == CLOSED:
        risk_validator.enforce_kill_switch_closed()
        alert("Kill Switch 仍 CLOSED，盘前禁开仓，等待人工复位", WARNING)
    # 阶段 3 基线校准（peak NAV / 回撤窗口 / 入场 NAV / 入场 VaR）
    peak_nav = state_store.load_peak_nav()  # peak 单调非减（§3.8），从持久化加载，不可当日重算
    capital_curve_manager.restore_peak(peak_nav)
    nav_history = state_store.load_nav_history(window=252)  # 1 年窗口供 drawdown_tracker.restore
    MIN_HISTORY = 30  # 最小回撤计算窗口（对齐 36号 §2.3 var_calculator min_history=30）
    if len(nav_history) < MIN_HISTORY:
        # 历史不足 → 保守冷启动：① 强制 NORMAL ② position_cap 降至 50% ③ 审计标记 COLD_START_INSUFFICIENT_HISTORY
        daily_auditor.log_cold_start_insufficient_history(available=len(nav_history), required=MIN_HISTORY)
        alert(f"nav_history 不足 {MIN_HISTORY} 日（实际 {len(nav_history)}），保守冷启动（position_cap 50%）", WARNING)
        state_machine.force_conservative_mode(position_cap=0.50)
        drawdown_tracker.restore(nav_history) if nav_history else drawdown_tracker.reset(peak_nav)
    else:
        drawdown_tracker.restore(nav_history)
    opening_nav = capital_curve_manager.current_nav  # 入场 NAV（日度熔断 §3.6 基准）
    entry_var = state_store.load_entry_var()  # 前日盘前 VaR_95 快照（§3.18 阶段 4b 持久化），供 §3.16 归因对比；None=首次/未持久化→跳过
    daily_auditor.log_baseline(peak_nav=peak_nav, opening_nav=opening_nav, entry_var=entry_var)
    # 阶段 4 Kill Switch 执行通道健康检查（§3.5.1 L1 层，避免触发时才发现连接断）
    if not stop_loss.health_check():
        alert("Kill Switch 执行通道不健康（broker 连接异常），拒绝启动", CRITICAL)
        return RefuseStart("执行通道不健康")
    # prev_attribution（§3.18 save_attribution_result 配对 load）：① 编排器传入 §3.10 evaluate() context；
    # ② §3.16 当日归因趋势对比。None=正常降级
    prev_attribution = state_store.load_attribution_result(trade_date - 1)
    return InitializationResult(state_machine=state_machine, opening_nav=opening_nav,
                                entry_var=entry_var, prev_attribution=prev_attribution)
```

**代码差距**（待施工 §6.6/§6.11/§6.12）：
1. **无 `state_store` 持久化层**——当前 `DrawdownController` / `DrawdownStateMachine`（未建）/ `capital_curve_manager` 均内存态，重启即丢失 peak NAV / 状态机态 / recovery_step
2. **无 `detect_ghost_positions` 盘前调用**——函数已落码（v1.39.0，commit 1d814359），盘前启动序列未接入
3. **无 `stop_loss.health_check`**——执行通道健康检查缺失，存在"触发时才发现连接断"风险

> **裁决**：盘前初始化暂缓为 §6.6（状态机持久化）+ §6.12（Ghost 检测盘前接入）施工的输入规约。最小补丁（立即可做）：① `capital_curve_manager.peak` 与 `drawdown_tracker` 窗口持久化到 DB（已有 `daily_auditor` 持久化基础设施可复用）；② 盘前调用 `detect_ghost_positions`（函数已落码，只需在启动序列接入）。完整 `state_store` + `DrawdownStateMachine` 持久化待 §6.6。

### 3.16 回撤归因端到端流程

**问题**：§3.3 讲单策略 vs 组合分层，§3.12 讲统计性 vs 行为性诊断，但缺"组合回撤发生后，如何归因到各策略/各因子"的端到端流程。`daily_auditor` 的 `AttributionBias`（预测因子占比 vs 实际占比）是工具，但无归因触发条件与响应分流。orstac 2026-03 的 correlation-aware 视角提示：高相关性回撤 = 系统性（全局收缩），低相关性回撤 = 策略特定（单策略收缩）——这是归因的关键判别维度。

**回撤归因伪代码**（对照 §3.3 分层 + §3.12 诊断 + §3.9 regime 协同 + §3.15/§3.18 entry_var 跨文档契约）：

```python
def drawdown_attribution_flow(dd_info, strategy_pnls, factor_decomposition,
                               entry_var=None, current_var=None, strategy_pnls_history=None):
    """触发：drawdown_tracker WARNING（5%）及以上即归因（不只 CRISIS）。
    输出：AttributionResult(systemic_pct, per_strategy_contribution, root_cause, response_routing)
    数据源：dd_info=§3.10 drawdown_tracker.update()；strategy_pnls=§3.10 参数；
    factor_decomposition=RiskOrchestrator（§6.5）从 factor_registry 拉取当日因子暴露 vs 策略预期占比
    （MVP 未建传 None→跳过因子归因）；entry_var=§3.15 InitializationResult.entry_var（前日盘前 VaR_95，
    §3.18 阶段 4b 持久化，None=首次/未持久化）；current_var=§3.10 DailyRiskResult.var_cvar.var_95；
    strategy_pnls_history=RiskOrchestrator 从 PnL 库拉取过去 20 日各策略 PnL（None=历史不足→跳过相关性归因）"""
    # ── 0. 风险恶化型归因（前馈：VaR 恶化即减仓，不等 NAV 回撤；对齐 §3.19 前馈风控边界）──
    if entry_var is not None and current_var is not None and entry_var > 0:
        var_deterioration_ratio = current_var / entry_var
        if var_deterioration_ratio > 1.5:  # current_var 比 entry_var 高 50%+ → 风险显著恶化
            reduction_pct = min(var_deterioration_ratio - 1.0, 0.5)  # 乘性减仓，最高 50%
            daily_auditor.log_risk_deterioration(entry_var=entry_var, current_var=current_var,
                ratio=var_deterioration_ratio, reduction_pct=reduction_pct)
            return AttributionResult(
                systemic_pct=1.0,  # 风险恶化是组合级（VaR 是组合度量）
                root_cause="RISK_DETERIORATION_VAR_RATIO_{:.1f}".format(var_deterioration_ratio),
                response_routing="RISK_BASED_REDUCTION",
                risk_deterioration_ratio=var_deterioration_ratio, recommended_reduction=reduction_pct,
                per_strategy_contribution=None, attribution_bias=None)
    # ── 常规归因：drawdown 达 WARNING 才进入 ──
    if abs(dd_info.drawdown_pct) < 0.05:
        return None  # 未达 WARNING（5%），不归因
    # ── 1. 策略间相关性归因（orstac correlation-aware）──
    if len(strategy_pnls) <= 1 or strategy_pnls_history is None:
        # 单策略无相关性矩阵 / 历史不足 → 策略特定
        avg_corr, systemic_pct = 0.0, 0.0
        root_cause = ("STRATEGY_SPECIFIC_SINGLE_STRATEGY" if len(strategy_pnls) <= 1
                      else "STRATEGY_SPECIFIC_INSUFFICIENT_HISTORY")
        per_strategy_contribution = {strategy_pnls[0].id: 1.0} if strategy_pnls else {}
    else:
        corr_matrix = compute_correlation(strategy_pnls_history, window=20)
        avg_corr = mean(off_diagonal(corr_matrix))
        if avg_corr > 0.7:    # 高相关 → 系统性（市场级）→ 全局收缩（§3.3 组合层）
            systemic_pct, root_cause = 1.0, "SYSTEMIC_HIGH_CORRELATION"
        elif avg_corr < 0.4:  # 低相关 → 策略特定 → 单策略 Soft/Hard Stop（§3.3）
            systemic_pct, root_cause = 0.0, "STRATEGY_SPECIFIC_LOW_CORRELATION"
        else:                 # 混合：按各策略 |drawdown| 占比拆分（除零守卫）
            total_abs_dd = sum(abs(p.drawdown_pct) for p in strategy_pnls)
            per_strategy_contribution = (
                {sid: abs(pnl.drawdown_pct) / total_abs_dd for sid, pnl in strategy_pnls}
                if total_abs_dd > 1e-10 else {p.id: 0.0 for p in strategy_pnls})
            systemic_pct, root_cause = avg_corr, "MIXED_PARTIAL_SYSTEMIC"  # 近似
    # ── 2. 因子归因（daily_auditor AttributionBias：预测因子占比 vs 实际 PnL 因子占比）──
    attribution = daily_auditor.compute_attribution_bias(
        predicted_factor_pct=factor_decomposition.predicted, actual_factor_pct=factor_decomposition.actual)
    if attribution.status == BIASED:         # 行为性：AI 执行偏差 → 停实盘 + 修执行（§3.12）
        root_cause, response_routing = "BEHAVIOURAL_ATTRIBUTION_BIAS", "STOP_LIVE_AND_FIX_EXECUTION"
    elif root_cause.startswith("SYSTEMIC"):  # 统计性+系统性 → 全局收缩
        response_routing = "GLOBAL_CONTRACTION"
    else:                                    # 统计性+策略特定 → 单策略收缩
        response_routing = "PER_STRATEGY_CONTRACTION"
    # ── 3. regime 交叉验证（§3.9）：ACCEL_DECLINE/PANIC_CRASH/CRISIS → 预期内；
    # CALM_BULL 但组合亏 → 异常，策略失效信号 ──
    root_cause += ("_REGIME_ALIGNED" if regime_shrinkage.regime in (ACCEL_DECLINE, PANIC_CRASH, CRISIS)
                   else "_REGIME_MISALIGNED")
    return AttributionResult(systemic_pct=systemic_pct, per_strategy_contribution=per_strategy_contribution,
        root_cause=root_cause, response_routing=response_routing, attribution_bias=attribution)
```

**响应分流对照**（归因结果 → 响应动作）：

| 归因结果 | 响应动作 | 对应章节 |
|---|---|---|
| RISK_DETERIORATION（VaR 恶化 ratio > 1.5） | 按 var_deterioration_ratio 乘性减仓（最高 50%），不等 NAV 回撤触发 | §3.15/§3.18 entry_var 契约 + §3.19 前馈风控边界 |
| SYSTEMIC + REGIME_ALIGNED + 统计性 | 全局收缩（capital_curve_manager + drawdown_controller systemic），继续执行 | §3.3 组合层 + §3.9 regime 协同 |
| SYSTEMIC + REGIME_MISALIGNED | 异常告警——市场平稳但组合亏，可能数据/执行问题 | daily_auditor 异常检测 |
| STRATEGY_SPECIFIC + 统计性 | 单策略 Soft/Hard Stop（§3.3），其他策略不受影响 | §3.3 单策略层 |
| BEHAVIOURAL（AttributionBias） | 停实盘 + 修正执行逻辑（§3.12 行为性回撤） | §3.12 诊断 |

> **裁决**：归因流程暂缓为 §6.7（回撤类型诊断）施工的输入规约。当前 MVP 用 §3.3 分层（单策略 Soft/Hard + 组合 systemic）+ §3.12 诊断矩阵（人工判读）足够；自动化归因（相关性矩阵 + 因子偏差 + regime 交叉）待 §6.7。最小补丁：`daily_auditor` 已有 `AttributionBias`，回撤 WARNING 触发时自动调用并记入日志，供人工复盘。

**扩展归因维度：六类风险失败机制**（[López de Prado & Fabozzi, JAM 2026](https://quantresearch.org/Publications.htm) "Rethinking Portfolio Risk: A Taxonomy for Asset Management"）：

> 严重损失通常来自六类风险失败机制的**复合效应**（而非单一波动率）。当前 §3.16 归因只覆盖维度 ①+④，其余散布在其他文档——六类框架提供统一归因视图。

| # | 失败机制 | 内涵 | 当前覆盖 | 对应文档/模块 |
|---|---|---|---|---|
| ① | Statistical（统计性）| 样本偏差、过拟合、多重检验 | ✅ §3.12 统计性 vs 行为性诊断 | 本备忘 §3.12 |
| ② | Factor（因子）| 因子失效、拥挤、IC 衰减 | 🟧 25_multifactor IC 衰减监控 | G09 多因子策略 |
| ③ | Liquidity（流动性）| 滑点、冲击成本、流动性枯竭 | ✅ 37_liquidity_crisis_protocol | G18 流动性危机 |
| ④ | Model（模型）| 分布假设错误、regime 失配、参数漂移 | ✅ §3.16 regime 交叉验证 + 36号§3.9 回测 | 本备忘 + G17 |
| ⑤ | Governance（治理）| 权限错误、流程缺失、Kill Switch 失效 | ✅ §3.5 Kill Switch + daily_auditor | 本备忘 §3.5/§3.7 |
| ⑥ | Decision-infrastructure（决策基础设施）| 系统故障、数据错误、连接中断 | 🟧 55_monitoring_review 系统健康 | G26 监控告警 |

> **裁决**：六类框架作为 §3.16 归因的**扩展维度**暂缓（§6.16）。当前 MVP 用二分法足够；六类框架的价值在于实盘运行后做**复合归因**——逐类排查 ①-⑥ 形成"回撤根因六维报告"。重评条件：25_multifactor IC 衰减监控 + 55_monitoring_review 系统健康均 production 后，纳入 §6.7 归因流程。

### 3.17 施工流程总览（6 流程闭环）

> **阅读指引**：本总览引用 §3.18 盘后持久化（下一节详述）——总览先行建立整体认知，§3.18 随后补齐第 6 个流程环节细节。§3.20 Hysteresis（横切机制）+ §3.21 行业实证（案例背书）非独立流程环节，不影响本总览的 6 流程闭环完整性。

**问题**：§3.10-§3.18 共 8 个章节，其中 **6 个是独立流程环节**（§3.10/§3.13/§3.14/§3.15/§3.16/§3.18），**2 个是横切机制**（§3.11 状态机被 §3.14/§3.15/§3.18 引用、§3.12 诊断被 §3.16 引用，不独立调度），本节给出时序关系与触发衔接总览。

**6 流程闭环时序**（一个交易日的完整风控生命周期）：

```
T-1 收盘后：§3.10 日度循环·盘后段（净值+回撤+VaR）→ §3.16 回撤归因（若触发）
           → §3.10 盘后审计 daily_auditor（Kill Switch 终态 + 限额合规）
           → §3.18 盘后状态持久化（peak NAV → 状态机 → nav_history → 原子标记）
                ↓ 持久化状态
T 盘前：    §3.15 盘前初始化（broker 持仓核对 Ghost 检测 → 加载状态机 → 基线校准 → 通道健康）
           → §3.10 日度循环·盘前段（VaR/ES → drawdown_controller 综合裁决 → 仓位裁决）
                ↓
T 盘中（9:30-15:00）：§3.13 盘中实时风控循环（30 秒轮询：单日亏损熔断 + 回撤重算 + Ghost 轮询）
           ←→ §3.14 Kill Switch 复位流程（若 KILL 触发，人工复位后进入 RECOVERY 阶梯）
           ↓ 触发条件（日内突破盘前 VaR）→ 36号 §3.12 盘中 VaR/ES 重算（1 分钟轮询，协同）
```

**衔接规则**：
1. **§3.15 → §3.10**：盘前初始化成功（无 Ghost + 通道健康）才进入日度循环盘前段；失败则 `RefuseStart`，当日不交易
2. **§3.10 盘前 → §3.13 盘中**：盘前产出的 `response`（position_cap / kill_switch_advised）作为盘中循环的初始约束
3. **§3.13 → §3.14**：盘中循环检测到 Kill Switch 触发条件 → 进入 §3.14 复位流程（但 A 股 T+1 下当日无法强平，复位在次日盘前 §3.15 阶段 2 完成）
4. **§3.13 ↔ 36号 §3.12**：盘中回撤循环（30 秒）与盘中 VaR 重算（1 分钟）协同——回撤循环检测到"日内突破盘前 VaR"时，触发 VaR 重算
5. **§3.10 盘后 → §3.16**：盘后审计发现回撤 WARNING 及以上 → 触发归因流程；归因结果持久化供次日盘前 §3.15 加载
6. **§3.16/§3.10 盘后 → §3.18**：盘后审计 + 归因完成后，触发 §3.18 盘后状态持久化（peak NAV / 状态机 / nav_history 原子提交）→ §3.18 标记可加载 → 次日 §3.15 据此恢复而非冷启动

> **与 36 号文档的关系**：本备忘的 6 流程闭环与 [36_var_es_monitoring](36_var_es_monitoring.md) 的 VaR/ES 循环共享 `RiskOrchestrator`（§6.5 待裁定）。VaR/ES 是日度循环盘前段（§3.10）+ 盘中重算（36号 §3.12）的子步骤，不是独立流程。§3.18 盘后持久化与 36号 §3.11 回测 `backtest_store` 共享 `state_store` 持久化层。

### 3.18 盘后状态持久化流程

**问题**：§3.15 盘前初始化从 `state_store` 加载持久化状态（peak NAV / DrawdownStateMachine / nav_history / recovery_step），但缺**配对的盘后保存流程**——若无显式持久化，§3.15 的"加载"无源可载（nexusfi 2026-06：持久化与恢复是配对操作，缺一即状态机失效）。

**盘后持久化伪代码**（对照 §3.15 加载顺序的逆序——先保存被依赖项，再保存依赖者，确保一致性快照）：

```python
def postmarket_persist(trade_date, state_machine, capital_curve, dd_tracker, var_cvar,
                       attribution_result=None, audit=None):
    """审计门控→终态净值→peak NAV→状态机→nav_history→entry_var→归因→策略持仓→标记可加载。
    顺序=§3.15 加载逆序（先存被依赖项）；原子性：全部成功才标记可加载，部分失败则次日 §3.15 冷启动默认 NORMAL。
    var_cvar=§3.10 当日盘前 VarCvarMetrics；attribution_result=§3.16 归因结果（save/load 闭环）；
    audit=§3.10 daily_auditor.audit() 产出（None=MVP 未接门控，降级为无门控直接持久化，向后兼容）"""
    # 阶段 0 审计门控：未通过（Ghost 未清零/Kill Switch 终态异常/限额超限/数据完整性失败）→ 不持久化，
    # 次日冷启动默认 NORMAL（宁可丢状态不可存错误状态）
    if audit is not None and not audit.passed:
        daily_auditor.log_persist_skipped(trade_date, reason=audit.failure_reason)
        state_store.mark_persistable(trade_date, status="AUDIT_FAILED_SKIP")
        return
    closing_nav = capital_curve.current_nav  # 阶段 1 终态净值（含已实现；A 股 T+1 未实现 PnL 按收盘 Mark 归零）
    # 阶段 2 peak NAV（§3.8 单调非减由 max() 保证）
    old_peak = state_store.load_peak_nav()
    new_peak = max(old_peak, closing_nav)
    state_store.save_peak_nav(new_peak)
    daily_auditor.log_peak_update(old=old_peak, new=new_peak, is_new_high=(new_peak > old_peak))
    # 阶段 3 状态机（§3.11 5 态 + recovery_step 0/1/2 + kill_switch OPEN/CLOSED）
    state_store.save_drawdown_state(trade_date, DrawdownStateSnapshot(
        current=state_machine.current, recovery_step=state_machine.recovery_step,
        last_transition=state_machine.last_transition, kill_switch=risk_validator.kill_switch))
    # 阶段 4 nav_history 滚动窗口（追加当日 + trim 252 日，§3.15 restore 需完整窗口）
    state_store.append_nav_history(trade_date, closing_nav)
    state_store.trim_nav_history(window=252)
    # 阶段 4b entry VaR（当日盘前 var_95 快照，供次日 §3.15 加载 + §3.16 风险恶化判断）
    state_store.save_entry_var(trade_date, var_cvar.var_95)
    daily_auditor.log_entry_var(trade_date, entry_var=var_cvar.var_95)
    # 阶段 4c 归因结果持久化（§3.16 AttributionResult 的 save/load 闭环，供次日盘前加载）
    if attribution_result is not None:
        state_store.save_attribution_result(trade_date, attribution_result)
        daily_auditor.log_attribution_persist(trade_date, root_cause=attribution_result.root_cause)
    # 阶段 4d 策略持仓持久化（§3.15 load_strategy_state 配对 save）：
    # position_sizing_engine 当日 plan 目标持仓快照 = 次日 Ghost 检测基准（目标 vs broker 实际差异即 Ghost）
    state_store.save_strategy_state(trade_date, position_sizing_engine.get_target_holdings_snapshot())
    # 阶段 5 标记可加载（原子提交点）：两阶段标记——35号标 DRAWDOWN_COMPLETE，36号标 VAR_COMPLETE；
    # 两者都 COMPLETE 才完全可加载；仅 DRAWDOWN_COMPLETE → 回撤层恢复 + VaR 层冷启动默认 NORMAL
    state_store.mark_persistable(trade_date, status="DRAWDOWN_COMPLETE")
    daily_auditor.log_persist(trade_date, closing_nav=closing_nav, peak=new_peak,
                              state=state_machine.current, step=state_machine.recovery_step)
    # 盘后顺序（RiskOrchestrator §6.5 编排）：daily_auditor.audit() → 35号§3.18（本函数，含审计门控）
    # → 36号§3.18 postmarket_persist_var()；35号审计失败 → return → 36号不执行
```

**与 §3.15 的配对约束**：

| §3.15 加载顺序 | §3.18 保存顺序 | 配对约束 |
|---|---|---|
| 阶段 1 broker 持仓核对 | —（不持久化，实时拉取） | — |
| 阶段 2 加载状态机 | 阶段 3 保存状态机 | 状态机态 + recovery_step 必须一致（§3.11 转换守卫依赖） |
| 阶段 3 加载 peak NAV | 阶段 2 保存 peak NAV | peak 单调非减（§3.8 不变量） |
| 阶段 3 加载 nav_history | 阶段 4 追加 nav_history | 窗口 252 日滚动，drawdown_tracker 需完整窗口算 drawdown_pct |
| 阶段 3 加载 entry_var | 阶段 4b 保存 entry_var | entry_var = 前日盘前 VaR_95 快照，§3.16 回撤归因 current_var vs entry_var 判断风险恶化 |
| 阶段 4d 加载 prev_attribution | 阶段 4c 保存 attribution_result | §3.16 归因结果，供次日盘前决策参考 |
| —（首次启动无前置） | 阶段 5 标记可加载 | 原子提交点：§3.15 据此判断"恢复"vs"冷启动 NORMAL" |

**代码差距**（待施工 §6.12/§6.6）：
1. **无 `state_store.save_*` 接口**——当前 `capital_curve_manager` / `drawdown_tracker` 内存态，无盘后持久化调用
2. **无原子性提交**——若 peak 保存成功但状态机失败，会产生不一致快照（§3.15 加载到新 peak 但旧状态机态，转换守卫错乱）
3. **无 `mark_persistable` 标记**——§3.15 无法判断"上次正常持久化"vs"状态丢失"，只能盲目冷启动

> **裁决**：盘后持久化暂缓为 §6.12（盘前初始化）的配对施工项——两者必须同步落地，否则 §3.15 加载无源。最小补丁（与 §6.12 同步）：① `capital_curve_manager.peak` + `nav_history` 持久化到 DB（复用 daily_auditor 已有持久化基础设施）；② 状态机态持久化待 §6.6 DrawdownStateMachine 落地；③ 原子性用 DB 事务（全成功 commit，任一失败 rollback）。§3.17 总览"T-1 收盘后 → 持久化状态"箭头即本流程。

### 3.19 施工流程算法审查与远期演进方向声明

**审查结论**：对照 §3.10-§3.18 的 6 流程闭环（日度循环 / 盘中循环 / 复位 / 盘前初始化 / 归因 / 盘后持久化）+ 2 横切机制（状态机 / 诊断），一个交易日的完整风控生命周期已被覆盖——盘前（初始化+裁决）→ 盘中（轮询+熔断）→ 盘后（审计+归因+持久化）→ 跨日（复位+恢复）。**无缺失的独立流程环节**。可增强的是横切算法本身（回撤度量、风险厌恶调整、前馈防御），但这些是 §4 替代方案与 §6 待裁定的演进方向，不是流程环节缺失。§3.20 Hysteresis + §3.21 行业实证在本节之后追加，不影响本结论。

**2026 学术研究的远期演进方向登记**（不直接采纳，详见 §4.6-§4.28 评估 + §5.2 Stage 4 15 族分类表）：

| 演进方向 | 来源 | 核心思路 | 与当前方案的关系 | 评估结论 |
|---|---|---|---|---|
| MPC / 趋势跟踪防御层 / CDaR / 多 agent | 详见 §4.12-§4.15（来源链接与评估同） | 连续 risk aversion γ(dd) / 前馈趋势防御 / drawdown 序列 CVaR / 多 agent 协作 | §3.2 离散阶梯 vs 连续/前馈/协作式 | §4.12 暂缓（P4）/ §4.13 暂缓（P4）/ §4.14 暂缓（P2）/ §4.15 拒绝 |
| **Conformal Kelly drawdown dial** | [arXiv:2608.01494](https://arxiv.org/html/2608.01494v1)（2026-08-02） | conformal 预测区间下行连续 miss 超历史率→视为模型失效→缩减 leverage；开发窗口 MaxDD 27.7%→20.3%，rank-based p=1/41≈0.024。**OOS 诚实账本**（Lockbox 2022+）：校准保持（0.745 vs 0.750 目标）但**增长未保持**——两配置仅 8.5%/7.0%/年，低于被动基准 | 当前 §3.4 恢复是 `recovery_factor` 阶梯（0.25→0.50→0.75→1.0），Conformal Kelly dial 是**预测区间 miss 驱动**的自适应 leverage 缩减 | §6.21 暂缓（P2，远期——需 conformal 预测层就绪）|
| **Data-Driven Drawdown Restart** | [arXiv:2303.02613](https://arxiv.org/pdf/2303.02613v1)（Hsieh 2023） | drawdown modulation 接近预设限值时不应纯 stop-loss，而应带 **restart 机制**——数据驱动重置策略参数，有交易成本场景下仍优于无 restart | 当前 §3.11 RECOVERY 阶梯（0.25→0.50→0.75）是 restart 的工程化离散实现，但未实现"数据驱动参数重置" | §6.22 暂缓（P3，远期——需足够实盘样本做参数重置的 data-driven 校准）|
| **Non-Gaussian Drawdown Lookup Tables** | [arXiv:2608.00127](https://arxiv.org/abs/2608.00127)（Landolfi 2026-07-31） | 给定 Sharpe 与收益统计结构（skew/峰度/波动率聚集/Sharpe 不确定性），Monte-Carlo 生成 4 度量查表：MaxDD / 最大单期损失 / 末尾负时间 / 最长恢复时间。核心发现：① 单一 Gaussian 表会误警（四度量非正态下移动方向不同）；② 持续性下回撤"放大"几乎全是 self-similar dispersion scaling `T^(H-1/2)`，是 √T 校准失效而非路径几何本征危险 | 当前 §3.4 recovery_factor 阶梯 + §3.2 三层阈值（5/10/15%）是经验值，Landolfi 查表提供统计校准依据；同时警示 [36_var_es_monitoring](36_var_es_monitoring.md) §3.2 参数法 VaR 的 `√T` 时间缩放在持续性下失效 | §6.23 暂缓（P2，远期——需实盘 Sharpe 稳定估计 ≥6 月 + 收益分布矩估计）|
| **Schmitt RWC Conformal Risk Control** | [arXiv:2602.03903](https://arxiv.org/pdf/2602.03903)（Schmitt 2026-02, Oxford, **v3 2026-08-03**） | Regime-Weighted Conformal Risk Control：指数时间衰减 + regime 相似性权重校准 VaR 安全缓冲，weighted exchangeability 下有限样本覆盖保证。TWC 是 drift 下强默认，RWC 增 regime 加权改善 regime-conditional 稳定性。**v3 关键**：任意 data-driven 权重下推导覆盖界，与 Conformal Kelly"反自适应"结论一致（regime 做**校准加权**而非 conformal 宽度局部自适应） | 当前 [36_var_es_monitoring](36_var_es_monitoring.md) §3.2 参数法 VaR 假设正态+平稳，Schmitt RWC 提供"非平稳 + regime 结构"下 distribution-free VaR 校准——直接增强 §3.10 盘前 VaR 计算。**regime 特征稳定性依赖**：[arXiv:2604.14322](https://arxiv.org/abs/2604.14322) BR-iHMM（在线双重鲁棒无限 HMM，预测误差降 67%）可作 regime 特征在线更新方案，适配 A 股跳空/涨跌停异常点 | §6.25 暂缓（P2，远期——需 36 号 conformal 预测层就绪 + regime 特征工程稳定）|
| **CVaR Risk-Aware Q-Learning** | [arXiv:2608.04305](https://arxiv.org/abs/2608.04305)（Wu/Lei/Huang 2026-08-05, ICAIF '26 Milan） | 自适应有限预算训练 CVaR 风险感知 Q-learning（RaQL）：per-cell inner-step sizing + outer-rate-matched decay + coverage-first sample allocation，CVaR Bellman 残差降 85%，BTC 日度 Sharpe 0.93 / MaxDD 6.46% | 当前 §3.2 三层映射是规则式阈值，RaQL 是 RL 端到端 CVaR 优化——属 §4.15 多 agent 拒绝同类（RL 重模型），但 RaQL 是单 agent + CVaR 目标，比 RMATS/MARCD 轻量 | 不单独登记（归入 §4.15 多 agent 拒绝的"借鉴范围"——CVaR 目标函数思路已由 §3.9 乘性叠加承载）|

> **§4.16-§4.28 远期登记汇总**：详见各自 §4.x 节 + §5.2 Stage 4 15 族分类表（§4.16→§6.24 P3 ｜ §4.17→§6.25 P2 ｜ §4.18→§6.27 P3 ｜ §4.19 P5+ ｜ §4.20 P3 ｜ §4.21 P4 ｜ §4.22 P4 ｜ §4.23 P3 ｜ §4.24 P2-P3 ｜ §4.25→§6.35 P4 ｜ §4.26→§6.36 P3 ｜ §4.27→§6.37 P3 ｜ §4.28 P3）。

> **Conformal Kelly 的关键设计原则**（arXiv:2608.01494 核心发现）：**"slow, unweighted, per-asset rolling conformal quantiles" 优于 adaptive/fast 方法**——每次使区间更快适应当前市场状态的调整都损失 0.7-5.3 个百分点年增长。原因：区间用于**仓位规模**而非单点预测时，宽度的**稳定性**比**局部锐度**更重要。若远期集成，选用最简单的 per-asset rolling quantile，不追 locally adaptive 变体。
> **Conformal Kelly drawdown dial 施工骨架**（远期·接口冻结，待 conformal 预测层就绪激活，§6.21 P2）：
> ```python
> def conformal_kelly_drawdown_dial(realized_returns, conformal_intervals,
>                                    coverage_level=0.75, rolling_window=252,
>                                    floor_scale=0.5):
>     """预测区间下行 miss 驱动的 leverage 缩减。
>     设计原则：slow unweighted per-asset rolling quantile 优于 locally adaptive。
>     Returns: leverage_scale ∈ [floor_scale, 1.0]——1.0=不缩减，0.5=半仓杠杆"""
>     # 1. 下行 miss 序列：实际收益 < 区间下界 = 模型低估下行风险
>     downside_misses = [1 if r < lo else 0
>                        for r, (lo, _hi) in zip(realized_returns, conformal_intervals)]
>     # 2. slow unweighted rolling miss rate（固定窗口均值，非自适应核）
>     recent_miss_rate = sum(downside_misses[-rolling_window:]) / min(len(downside_misses), rolling_window)
>     baseline_miss_rate = 1.0 - coverage_level  # 75% 区间 → baseline 0.25
>     # 3. dial：miss 率超 baseline → 线性缩减 leverage（平滑过渡，不超调）
>     if recent_miss_rate <= baseline_miss_rate:
>         return 1.0
>     excess = (recent_miss_rate - baseline_miss_rate) / (1.0 - baseline_miss_rate)
>     return max(1.0 - excess, floor_scale)  # 最低半仓，不归零
> ```
> **与 §3.4 recovery_factor 的乘性叠加**（三层各管一件事，正交不覆盖）：
> `effective_position_cap = position_cap(state) × recovery_factor(state) × conformal_leverage_scale`
> | 乘子 | 驱动信号 | 作用层 | 来源 |
> |---|---|---|---|
> | `position_cap` | 状态机分级（NORMAL/WARN/DANGER/CRISIS） | 仓位硬上限 | §3.2 三层映射 |
> | `recovery_factor` | 已实现回撤恢复阶梯（0.25→0.50→0.75→1.0） | 回撤后恢复节流 | §3.4 + §3.20 hysteresis |
> | `conformal_leverage_scale` | 预测区间下行 miss 率 | 模型失效 dial | 本块（远期） |
> `recovery_factor` 是"已亏才减"的反馈式，`conformal_scale` 是"预测失准即减"的**前馈式**——正交互补。
> **接口冻结**：输入 `conformal_intervals`（由 [31_position_sizing](31_position_sizing.md) 或独立 conformal 模块产出）；输出 `conformal_leverage_scale ∈ [0.5, 1.0]` 喂入 `capital_curve_manager` 与 `recovery_factor` 乘性叠加；**不替换** §3.4 `recovery_factor`，`conformal_scale=1.0` 时退化为现状。**0.5 下限而非归零**：对齐 §4.5 拒绝 CPPI 的 cash-lock 教训——dial 是节流阀不是破产防护闸，Kill Switch（§3.5）才是归零通道；floor_scale=0.5 待实盘校准后调整（重评条件见 §6.21）。

> **0.5% Recovery Protocol**（[edgeflo 2026-03](https://www.edgeflo.com/blog/de-risk-after-drawdown)）：连续 2 笔亏损（或 2% 回撤）后，每笔风险从 1% 降至 0.5%——0.5% 风险下单笔 3R 盈利回补 +1.5%，覆盖 2 笔 0.5% 亏损还多 0.5%；2 笔 3R 盈利完全恢复 3% 回撤到 breakeven。**与本项目 §3.4 的关系**：25%→50%→75%→100% 阶梯是**仓位上限**层面恢复，0.5% protocol 是**单笔风险**层面恢复——正交可叠加（recovery_factor=0.5 + risk_per_trade=0.5% → 实际风险 0.25%，"双保险恢复"）。单笔风险由 [31_position_sizing](31_position_sizing.md) 的 risk_per_trade 参数承载（§6.20 待裁定）。

**过度工程红线**（个人 + 100% AI 项目的自约束）：

1. **不引入重模型**：MPC 需多变量 HMM，MARCD 需 regime-conditioned diffusion + CVaR epigraph QP，DLP-SMPC 需随机 MPC receding-horizon 求解——机构级 24 资产、561 交易日样本下有效，但本项目 3-5 个 A 股策略、实盘样本 <6 个月，参数估计不可靠。[arXiv:2605.16895 The Alpha Illusion 2026-05](https://arxiv.org/html/2605.16895v1) 警示：LLM/多 agent 报告的 alpha 在通过结构有效性测试前不应作部署证据——"借鉴思路不照搬架构"。
2. **A 股约束适配**：不能做空 + T+1 + 无期权，使趋势跟踪防御层（§4.13）只能"减仓/空仓"实现；MPC 的"杠杆提高收益不增 MaxDD"在 A 股个人账户融资融券受限下不适用。
3. **可解释性优先**：5/10/15% 阈值法每个数字都可向业主解释，MPC 的连续 `γ(dd)` 难解释——个人系统业主需理解每笔风控动作的依据，可解释性是硬约束。
4. **借鉴范围限定**：从 RMATS 借鉴"Risk Agent 独立于策略 agent"（已实现，§4.2）+ 回撤惩罚项思路（§3.9 选乘性）；从 Nystrup/Boyd 借鉴"风险厌恶随回撤调整"直觉（recovery_factor 阶梯是其离散近似）；从 Noguer 借鉴"持续回撤需递增防御"直觉（前馈层未实现）；从 Uryasev CDaR 借鉴"回撤序列尾部度量"思路。

**回撤预测 vs 前馈风控的边界**（澄清 §5.3 已论立场）：§5.3"独立回撤预测器是过度工程——预测回撤 = 预测收益，属 alpha 层"立场**不变**，但区分两种"前馈"：① **回撤预测**（拒绝）= 预测"下周会回撤多少"，属 alpha 层；② **基于收益预测的前馈风控**（MPC，远期）= 用 HMM 预测收益均值/协方差喂入风控约束。本项目当前无 alpha 层收益预测（regime 是市场状态分类非收益预测），MPC 前馈风控无数据基础，远期待 alpha 层成熟后再评估。

### 3.20 回撤状态滞后-恢复双阈值（Hysteresis）

> §3.11 状态机定义了 6 态及其**升级触发条件**，但**未定义降级/恢复条件**——若无恢复算法，状态机会在临界阈值附近 thrashing（触发→恢复→再触发），或锁死在高级态无法降级。本节补齐**降级恢复算法**，对齐 [37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md) §3.6 的滞后-恢复双阈值设计。

**核心原则**：触发阈值与恢复阈值**不对称**（hysteresis 双阈值），避免临界状态反复震荡（thrashing）——控制论迟滞回线标准应用（恒温器/施密特触发器同原理）。

**行业印证**：
- [r1000-quant-engine Phase 6a](https://github.com/wscha231/r1000-quant-engine/blob/master/PHASE_ROADMAP.md)（2026-04）：3 级 drawdown circuit breaker −8%/−15%/−25% → cash floors 15%/35%/60%，**equity-based recovery hysteresis** `dd_trigger_equity * (1 + 0.03)`——净值须从触发点回升 3% 才解除
- [dredyson 2026-05](https://dredyson.com/the-hidden-truth-about-state-machines-in-algorithmic-trading-systems-)：进入阈值 2.0 std、退出阈值 1.5 std，0.5 gap **减少 70% 假状态转换**；cooldown timer 是额外安全网
- [Actura 2026-04](https://github.com/othnielObasi/actura-gacr-agent/blob/main/WHITEPAPER.md)：drawdown > 6% 锁定 EXTREME_DEFENSIVE，profile 切换间至少 **8 cycles cooldown**
- **Triple Penance Rule（[Bailey & López de Prado 2014](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2201302)，[BacktestBase 2026-02](https://www.backtestbase.com/education/drawdown-risk-analysis) 实证引用）**：回撤恢复时间通常为形成时间的 **2-3 倍**——为 min_hold 门控（WARN 5 日 / DANGER 10 日 / CRISIS 20 日）提供经验倍数依据。**与 §2.1 恢复数学表的关系**：§2.1 的"20% 回撤需 25% 收益恢复"是**幅度非对称**（Loss/(1-Loss)），Triple Penance 是**时间非对称**（恢复用时 2-3x）——两者正交，构成"幅度×时间"双维约束。RECOVERY 阶梯 5 日/阶梯 min_hold 累计 15 日（三阶梯），对齐 2-3x 下限。

**恢复条件矩阵**（对称于 §3.11 升级触发条件，但阈值更宽松——恢复阈值 ≈ 触发阈值的 50%）：

| 状态转换 | 升级触发条件（§3.11） | **恢复条件（hysteresis）** | 恢复动作 | 最短持续时间 |
|---|---|---|---|---|
| WARN → NORMAL | drawdown > 5% | drawdown < **2.5%**（半阈值）持续 **N=3 个交易日** | position_cap 80% → 100%；recovery_factor 保持 1.0 | 触发后至少 **5 个交易日**才可降级 |
| DANGER → WARN | drawdown > 10% | drawdown < **5%**（半阈值）持续 N=3 日 | position_cap 50% → 80% | 至少 **10 个交易日**才可降级 |
| CRISIS → DANGER | drawdown > 15% | drawdown < **7.5%**（半阈值）持续 N=5 日 | position_cap 30% → 50%；解除 defensive_only | 至少 **20 个交易日**才可降级 |
| KILL → RECOVERY | drawdown > 25% 或 BS-007 | 人工复位 + 持仓清零确认（§3.14） | recovery_factor 0.0 → 0.25；position_cap 0% → 25% | 人工复位（无自动计时，§3.7） |
| RECOVERY 阶梯 0→1 | recovered_pct ≥ 50% | 持续 N=3 日 + **毕业准则**（见下） | recovery_factor 0.25 → 0.50 | 每阶梯至少 **5 个交易日** |
| RECOVERY 阶梯 1→2 | recovered_pct ≥ 75% | 持续 N=3 日 + 毕业准则 | recovery_factor 0.50 → 0.75 | 至少 5 日 |
| RECOVERY 阶梯 2→NORMAL | drawdown = 0（创新高） | 创新高确认 + 毕业准则 | recovery_factor 0.75 → 1.00；expansion_factor 保留 | — |

> **关键说明**：恢复阈值取触发阈值的 **50%**（半阈值）是经验初始值，对齐 [37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md) §3.6 的半阈值设计。r1000-quant-engine 用 3% 净值回升 buffer（绝对值），本项目用 50% 比例（相对值）——回撤阈值 5/10/15/25% 跨度大，固定 3% buffer 在浅回撤（5%）过粗、深回撤（25%）过细。50% 比例在各阈值下均产生合理 buffer：2.5% / 5% / 7.5% / 12.5%。

**恢复算法**（CUSUM 式，对齐 §3.11 状态机 + [37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md) §3.6 CUSUM 框架）：

```python
# 辅助函数
def next_state_level(current_state):
    """降级后的下一级状态（WARN→NORMAL / DANGER→WARN / CRISIS→DANGER）。"""
    return {"WARN": "NORMAL", "DANGER": "WARN", "CRISIS": "DANGER"}.get(current_state, current_state)

def var_trigger_threshold(target_state):
    """目标态对应的 VaR 触发阈值（§3.11 升级阈值逆查）：NORMAL→0.02 / WARN→0.04 / DANGER→0.06"""
    return {"NORMAL": 0.02, "WARN": 0.04, "DANGER": 0.06}.get(target_state, 0.02)

def sustained(history, threshold, window):
    """history 最近 window 个交易日是否全部 < threshold（CUSUM 式持续确认）。"""
    return len(history) >= window and all(abs(h) < threshold for h in history[-window:])

def has_consecutive_profit_days(strategy_pnls, n=3):
    """最近 n 笔交易是否全部盈利（TradeZella 三级恢复协议）。"""
    return len(strategy_pnls) >= n and all(t.pnl > 0 for t in strategy_pnls[-n:])

def compute_rule_compliance(recent_trades):
    """规则合规率——过去 10 笔交易中遵守预设规则的占比（BloFin 行为性检测）。"""
    if not recent_trades:
        return 0.0
    return sum(1 for t in recent_trades if t.rule_followed) / len(recent_trades)

def retreat_recovery_step(current_state, recovery_step):
    """RECOVERY 期间回撤加深 → 回退阶梯或回 KILL（对齐 §3.14 分级保护）。"""
    return f"RECOVERY_STEP_{recovery_step - 1}" if recovery_step > 0 else "KILL"  # 阶梯 0 回撤 >15% → KILL

# 主函数
def check_drawdown_recovery(current_state, dd_info, var_cvar, time_since_trigger, dd_history,
                            recovery_step=0, strategy_pnls=None, recovery_window=3):
    """回撤状态恢复判定——滞后双阈值 + 持续时间门控 + 毕业准则。
    current_state: NORMAL/WARN/DANGER/CRISIS/KILL/RECOVERY；dd_info: DrawdownInfo；
    var_cvar: VarCvarMetrics（交叉验证）；time_since_trigger: 距升级触发的交易日数；
    dd_history: 最近 N 日 drawdown_pct 序列；recovery_step: RECOVERY 阶梯计数器（0/1/2，§3.14）；
    strategy_pnls: 供毕业准则；recovery_window: 恢复条件持续窗口（默认 3 日）。
    Returns: 恢复后的目标态（None=不恢复）"""
    # 最短持续时间门控（防 thrashing，对齐 dredyson cooldown timer）
    min_hold = {"WARN": 5, "DANGER": 10, "CRISIS": 20,
                "RECOVERY_0": 5, "RECOVERY_1": 5, "RECOVERY_2": 5}  # RECOVERY 阶梯间 5 日
    hold_key = f"RECOVERY_{recovery_step}" if current_state == "RECOVERY" else current_state
    if time_since_trigger < min_hold.get(hold_key, 5):
        return None  # 持续时间不足，不恢复
    dd = abs(dd_info.drawdown_pct)  # drawdown_pct ≤ 0，取绝对值
    # VaR 也须同步回落到下一级触发阈值以下，避免"回撤降但 VaR 仍高"的假恢复
    var_ok = var_cvar.var_95 < var_trigger_threshold(next_state_level(current_state))
    # 降级条件检查（半阈值 + 持续时间 + VaR 交叉验证）
    if current_state == "WARN" and dd < 0.025 and var_ok:
        # WARN → NORMAL：drawdown < 2.5% + VaR < 2% 持续 3 日
        if sustained(dd_history, threshold=0.025, window=recovery_window):
            return "NORMAL"
    elif current_state == "DANGER" and dd < 0.05 and var_ok:
        # DANGER → WARN：drawdown < 5% + VaR < 4% 持续 3 日
        if sustained(dd_history, threshold=0.05, window=recovery_window):
            return "WARN"
    elif current_state == "CRISIS" and dd < 0.075 and var_ok:
        # CRISIS → DANGER：drawdown < 7.5% + VaR < 6% 持续 5 日
        if sustained(dd_history, threshold=0.075, window=recovery_window + 2):
            return "DANGER"
    # RECOVERY 阶梯升级（对齐 §3.14 kill_switch_recovery_flow）
    elif current_state == "RECOVERY":
        if dd_info.recovered_pct >= 0.50 and recovery_step == 0:
            if graduation_criteria_met(strategy_pnls, expected_phases=0):
                return "RECOVERY_STEP_1"  # recovery_factor 0.25 → 0.50
        elif dd_info.recovered_pct >= 0.75 and recovery_step == 1:
            if graduation_criteria_met(strategy_pnls, expected_phases=1):
                return "RECOVERY_STEP_2"  # 0.50 → 0.75
        elif dd_info.recovered_pct >= 1.0 - 1e-6 and recovery_step == 2:
            # 创新高 → 完全恢复（epsilon 比较替代 drawdown_pct == 0 浮点等值检查）
            if graduation_criteria_met(strategy_pnls, expected_phases=2):
                return "NORMAL"  # 0.75 → 1.00
    # 恢复期回撤加深保护（对齐 §3.14）：RECOVERY 期间再次回撤 > 15% → 回退阶梯或回 KILL
    if current_state == "RECOVERY" and dd > 0.15:
        return retreat_recovery_step(current_state, recovery_step)
    return None  # 不满足恢复条件

def graduation_criteria_met(strategy_pnls, expected_phases):
    """毕业准则——对齐 BloFin/JournalPlus 分阶段恢复：
    ① 连续 3 个盈利日（TradeZella）；② 近 10 笔平均期望 ≥ +0.3R（BloFin Phase 2）；
    ③ 规则合规率 ≥ 80%（BloFin 行为性检测，过去 10 笔）"""
    if strategy_pnls is None or len(strategy_pnls) < 3:
        return False  # 样本不足，不毕业
    if not has_consecutive_profit_days(strategy_pnls, n=3):
        return False
    recent_trades = strategy_pnls[-10:]
    if mean(t.r_multiple for t in recent_trades) < 0.3:
        return False
    if compute_rule_compliance(recent_trades) < 0.80:
        return False
    return True
```

**恢复执行动作**：

| 恢复路径 | 执行动作 |
|---|---|
| WARN → NORMAL | `position_cap` 80% → 100%；`recovery_factor` 保持 1.0；`halt_new_orders=False`；通知日志"回撤企稳，恢复正常开仓" |
| DANGER → WARN | `position_cap` 50% → 80%；通知日志"回撤缓解，仓位上限升至 80%" |
| CRISIS → DANGER | `position_cap` 30% → 50%；`defensive_only=False`（恢复开仓权限）；通知日志"危机降级，允许新开仓 50% 上限" |
| KILL → RECOVERY | 人工复位 + `holdings_verified_zero`（§3.14）；`recovery_factor` 0.0 → 0.25；`position_cap` 0% → 25% |
| RECOVERY 阶梯升级 | `recovery_factor` +0.25；`position_cap` 对应上调；`risk_per_trade` 联动（§6.20 0.5% Protocol：25%→0.5% / 50%→0.75% / 75%→1.0%） |

**为何用半阈值（hysteresis）而非原阈值**：恢复阈值 = 触发阈值（5%）时，drawdown 在 4.9%-5.1% 间波动会反复触发/恢复（thrashing）；半阈值（2.5%）制造"恢复缓冲带"（降到 2.5% 才恢复，升到 5% 才再触发，中间是稳定区）。[dredyson 2026-05](https://dredyson.com/the-hidden-truth-about-state-machines-in-algorithmic-trading-systems-) 实证 0.5 std gap **减少 70% 假状态转换**——本项目 2.5% gap 是 50% 比例（比 dredyson 25% 更宽），因回撤序列 serial correlation 更强。

**为何需要最短持续时间门控**：drawdown 短暂回到 2.5% 以下不代表回撤期已过，N=3 日窗口确保**持续满足**；WARN 5 / DANGER 10 / CRISIS 20 日递增 min_hold 是经验估计——[Rej-Seager-Bouchaud 2017](https://arxiv.org/abs/1707.01457)：回撤持续时间随 Sharpe **平方**反比。

**毕业准则（Graduation Criteria）——分阶段恢复的进阶约束**：

> 对齐 [BloFin 2026-05](https://blofin.com/en/academy/education/handling-drawdowns) 三阶段恢复 + [JournalPlus 2026-05](https://journalplus.co/learn/guides/trading-after-a-drawdown-guide/) 4 阶段框架 + [fazencapital 2026-05](https://fazencapital.com/learn/en/trading-drawdown-recovery-math-methods-guide) 30 天 reset protocol。

| 准则 | 阈值 | 来源 | 理由 |
|---|---|---|---|
| 连续盈利日 | ≥ 3 日 | TradeZella 三级恢复协议 | 确认回撤企稳而非单日反弹 |
| 10 笔交易平均期望 | ≥ +0.3R | BloFin Phase 2 graduation | 量化"策略正期望已恢复"——0.3R 是正期望下限确认 |
| 规则合规率 | ≥ 80% | BloFin 行为性检测 | 防 AI 执行偏差复发——合规率 < 80% 说明行为性回撤未修正 |
| 单笔最大亏损 | ≤ 1.2R | completetradersedge 诊断矩阵 | 止损未被放宽——平均损失 > 1.2R 说明执行偏差仍在 |

> **与 §3.4 recovery_factor 阶梯的关系**：§3.4 的 `recovery_factor`（0.25→0.50→0.75→1.0）是**仓位上限**层面的恢复数值，本节毕业准则是**状态转换**层面的进阶约束——`recovery_factor` 升级前毕业准则必须全部满足（BloFin："Advance only when objective criteria are met"）。

**与 §3.11 状态机的集成**：恢复判定由 `DrawdownStateMachine.check_recovery()` 在每次 `evaluate()` 时顺带执行，输出 `StateTransition(from, to, reason="hysteresis_recovery")` 或保持当前态；恢复动作由 `capital_curve_manager` + `drawdown_controller` 消费状态转换事件执行；**转换守卫**（§3.11 代码差距 2 修复）：降级须经 hysteresis 双阈值 + min_hold + 毕业准则三重守卫，CRISIS 不可直接跳回 NORMAL（须逐级降级），RECOVERY 不可跳过阶梯。

**与 §3.14 Kill Switch 复位流程的关系**：§3.14 定义 KILL → RECOVERY → NORMAL 的端到端流程（人工复位 + 阶梯恢复）；本节定义 NORMAL ↔ WARN ↔ DANGER ↔ CRISIS 的常规降级算法（非 Kill Switch 场景）。CRISIS/KILL 边界衔接：CRISIS 未触发 Kill Switch（drawdown 15-25%）用 §3.20 降级回 DANGER；触发 Kill Switch（>25% 或 BS-007）用 §3.14 人工复位 + RECOVERY 阶梯。

**与 37 号流动性危机恢复算法的对齐**：[37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md) §3.6（v1.0.3）定义流动性危机的滞后-恢复双阈值（spread 半阈值 0.25% + sell_pressure 0.50 + min_hold 10/15/30 分钟）；本节是回撤协议的对等设计——共享 hysteresis 半阈值 + min_hold + CUSUM 式检测模式，但阈值维度不同（37 号是 spread/sell_pressure 微结构信号，35 号是 drawdown_pct/VaR 账户级信号）；两个恢复算法独立运行不互相调用，可同时处于不同态。

> **待校准**（§6.26 新增）：恢复阈值（半阈值 50% 比例）和最短持续时间（5/10/20 交易日 + RECOVERY 阶梯 5 日）是经验初始值，需实盘观测校准。重评条件：实盘累积 3 个月恢复事件数据后评估 thrashing 率（恢复后 N 日内再次升级的比例）——若 > 20%，加大 hysteresis gap（50% → 60%）或延长 min_hold；若恢复滞后，缩小 gap（50% → 40%）。

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-POS-05 | 资金曲线回撤缩放 | §3.2 三层映射表 / §3.11 恢复状态机 / §3.20 Hysteresis（capital_curve_manager） | design 待施工 |

### 3.21 行业实证背书：2026-08 A 股量化私募集体回撤（风险优先原则的实盘检验）

> 2026-07 A 股科技成长与中小盘回调，量化私募集体回撤（[量化私募如何穿越波动](http://m.toutiao.com/group/7672055738499351080/) / [百亿量化稳博投资回撤](http://m.toutiao.com/group/7669983704357388819/)），为风险优先原则 + 四级回撤 Protocol + Kill Switch 不可覆盖提供**实盘级**背书。

| 产品类别 | 7 月平均跌幅 | 极端个案 |
|---|---|---|
| 中证 500 指增 | -18.72% | 进化论多只产品跌超 25% |
| 中证 1000 指增 | -19.96% | 稳博小盘激进择时指增 1 号 **-46.24%**（近一月） |
| 量化选股 | -13.04% | 多只产品跌逾 28% |
| 量化中性 | -3.33% | — |
| 幻方量化 | 9 只产品近一月均跌逾 20% | 仅 1 只年内正收益 |

**根因归因**（百亿量化私募复盘共识）：① **风格暴露集中是首要根因**——盈亏同源；② **分散失效**——原本低相关策略同向波动；③ **止损踩踏**——集中释放放大净值波动；④ **端到端 AI 逆向承接深套**——稳博投资（端到端 AI 策略）"逆向承接恐慌盘"=-46.24%。

**对本项目设计决策的实证映射**：

| 量化私募回撤教训 | 本项目对应设计 | 支撑强度 |
|---|---|---|
| 风格暴露集中→回撤源（根因①） | [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.5 firm 层硬上限裁剪 + [31_position_sizing](31_position_sizing.md) §2.4 单票 8%/行业上限/总仓位裁剪 | ★★★ 强——百亿量化因风格集中回撤 20%+，项目 firm 层硬上限是直接防御 |
| 低相关策略同向波动→分散失效（根因②） | §3.16 回撤归因（avg_corr>0.7=系统性）+ [23_strategy_correlation_validation](23_strategy_correlation_validation.md) 策略相关性监控 | ★★★ 强——"分散效果减弱"正是 §3.16 要检测的场景；[Aldridge & Krawciw crowding model](https://arxiv.org/abs/2608.02311) 两 agent 收敛相关暴露时 joint drawdown probability 从 **39.2% 升至 79.3%**（§4.28） |
| 止损集中释放→踩踏放大（根因③） | §3.20 hysteresis min_hold 5/10/20 交易日 + §3.5.1 Kill Switch 分批拆单（15 笔/秒）+ [42_sell_flow](42_sell_flow.md) §3.8 跌停板排队优先级 | ★★☆ 中——个人系统 min_hold + 分批拆单降低自身踩踏风险 |
| 端到端 AI 逆向承接深套（根因④） | §3.5 Kill Switch **不可覆盖**（`requires_manual_reset`）+ [30 §2.5.5](30_multi_strategy_concurrency.md) 回撤>25% 清仓+强制休息 5 天+人工 review | ★★★ 强——Kill Switch 不可覆盖正是防"模型自作主张深套" |
| 回撤 20%+ 成行业常态 | §2.5.1 四级阈值 8/15/20/25%（外层生存边界）+ 代码 5/10/15%（内层早预警） | ★★★ 强——百亿量化 7 月回撤 20%+ 是常态，Level 3（20%）停仓 / Level 4（25%）清仓是生存底线 |

> **关键启示**：2026-07 量化私募集体回撤**不是模型失效，而是风险约束不足**。直接印证项目风险优先原则（project_memory 硬约束：风险相关模块先于策略模块施工至 production）——先建风控红线再迭代 alpha。**与 [36_var_es_monitoring](36_var_es_monitoring.md) 联动**：回撤期间"流动性阶段性承压"→ VaR/ES 流动性调整因子（L-VaR）须在极端行情放大；§3.16 归因中"流动性归因"维度 + 37 号流动性危机 Protocol 是踩踏效应的对冲设计。

**国际平行案例：2026-08 韩国 KOSPI SideCar 连环熔断**（[新华财经/21世纪经济报道 2026-08-06](https://www.cnfin.com)）：

> KOSPI 2026-06-19 见顶后近 40% 回撤；年内 9 次全市场熔断（此前 25 年合计仅 6 次）；SideCar 触发逾 70 次；7 月跌 33.19%（1997 以来纪录）。根因：三层嵌套杠杆集中于三星/SK 海力士（~60% 权重），5-7 月强制平仓 2.3 万亿韩元，120 万账户追保，30 万账户清零。监管响应：暂停新上市杠杆 ETF、保证金 1000 万→3000 万韩元、最小交易单位 1→20 份。

| KOSPI 教训 | 本项目对应设计 | 适用性 |
|---|---|---|
| 杠杆 ETF 日内再平衡的顺周期放大 | §3.5 Kill Switch 不可覆盖 + §3.20 hysteresis min_hold 防 thrashing | ★★☆ 中——A 股无个股杠杆 ETF，但融资融券+两融集中度有类似脆弱性 |
| 三层嵌套杠杆→保证金追缴→流动性挤兑 | 37 号流动性危机 Protocol + §3.16 相关性崩溃归因（avg_corr>0.8） | ★★★ 强——流动性挤兑是 37 号要防御的核心场景 |
| 60% 权重集中于 2 只股票→集中度风险 | [31_position_sizing](31_position_sizing.md) §2.4 单票 8% 上限 + 行业上限 | ★★★ 强——A 股个人系统单票 8% 硬上限直接防御 |
| SideCar 70+ 次触发→circuit breaker 频繁暂停 | §3.7 Kill Switch 不可覆盖（非 circuit breaker）+ §3.20 hysteresis 防频繁触发 | ★★☆ 中——本项目 kill switch 是终止非暂停，但 hysteresis 防 thrashing 思路一致 |

> **裁决**：KOSPI 案例作为 Kill Switch 压力测试国际剧本纳入 §6.11 4 层架构施工验证——特别是"杠杆产品再平衡触发连环抛售"路径的模拟。Kill Switch 的"分批拆单 + 撤单率控制"（§3.5.1 A 股 2026 新规适配）在 KOSPI 式连环熔断场景下尤为重要。

## 4. 考虑过的替代方案（拒绝理由）

### 4.1 改代码对齐 §2.5.1 的 8/15/20/25% —— 拒绝
- 三套模块已 production + 有单测，改阈值引入回归风险
- 8/15/20/25% 比 5/10/15% 更松，是**降低**风控强度，与个人系统"宁紧勿松"目标相悖
- 强行统一阈值破坏三层职责分离（监控/节流/综合响应）

### 4.2 单一全局回撤控制器（合并 tracker + curve_manager + controller）—— 拒绝
- 违反单一职责：监控（只读报警）、节流（仓位上限）、综合裁决（多输入取最严）是三种不同语义
- 合并后耦合 VaR/黑天鹅/回撤三输入到同一模块，归因纠缠（亏钱时无法区分是回撤触发还是 VaR 触发）
- D_RISK（监控）与 D_POSITION（行动）跨域合并违反域边界

### 4.3 自动恢复（无人工复位）—— 拒绝
- [ARKA 2026](https://completetradersedge.com/drawdown-protocol-traders/) 行业共识：Recovery requires explicit re-authorization
- 自动恢复在情绪化市场中可能"刚清仓又满仓"，放大损失
- 个人系统无 7×24 盯盘，人工复位是必要的冷却期

### 4.4 回撤进入 RiskSignal 参与下次决策 —— 拒绝（§2.5 用户裁定）
- 回撤是沉没成本，不影响未来收益分布
- 进入 RiskSignal 会产生"亏多了该更激进回本"的赌博倾向（量化理论背书见 §6.33）
- 只触发账户级风险节流（减仓/停仓/清仓），不进入策略 alpha 信号

### 4.5 CPPI（Constant Proportion Portfolio Insurance）—— 拒绝

- **算法**：`E = m × (V − Floor)`，风险敞口 = 乘数 × cushion（净值超底线部分），[MetricGate 2026-06](https://metricgate.com/docs/constant-proportion-portfolio-insurance/) + [marketclutch 2026](https://marketclutch.com/buy-and-hold-vs-constant-mix-vs-cppi/)
- **优势**：cushion 随亏损自动缩小 → 仓位自动下降，天然"回撤越深仓位越轻"；连续函数比阶梯平滑
- **拒绝理由**：
  1. **cash-lock 风险**：cushion = 0 后全仓现金无法恢复——个人系统不能接受"一次触底永久退出"
  2. **A 股 gap risk**：T+1 + 涨跌停下隔夜跳空可能直接击穿 Floor，连续再平衡假设失效
  3. **无需硬底保**：CPPI 适合保本场景；个人系统无保本承诺，分层阈值 + Kill Switch 已足够
- **与当前方案对比**：§3.2 三层映射是分级阶梯（5/10/15%），可解释性强；CPPI 的 m 值选择主观且 gap risk 下失效
- **诚实账本——东方证券 A 股实证反证（v1.19.0 补）**：[东方证券 2026-04 "CPPI+风险预算"两阶段法](https://www.uufund.com/Report/Detail?id=AP202604121821139947) A 股 2006-2026 全样本年化 13.41%/Sharpe 1.53/MaxDD -10.91%，优于等权和纯 RP，**是对拒绝理由#2 的重要反证**。**仍不采纳**：① 定位正交（组合配置层 vs 本项目 sleeve 级节流）；② 无保本承诺；③ 架构耦合不可拆单层套用；④ 可解释性优先。**借鉴价值**：其"动态回撤控制"层与 §3.20 Hysteresis + §3.4 recovery_factor 同构。登记 §6.30 待裁定（组合配置层远期候选）。

### 4.6 Ulcer Index 替代回撤度量 —— 暂缓

- **算法**：`UI = sqrt((1/N) × Σ DD_t²)`，同时惩罚回撤**深度**和**持续时间**（`drawdown_pct` 单点值只看当前深度，UI 还考虑"在水下待了多久"），[IR-Tracker 2026-02](https://www.ir-tracker.com/en/columns/advanced-strategy/drawdown-management)
- **暂缓理由 + 重评条件**：① 单点值足够 MVP（触发分层响应）；② UI 需维护滚动窗口 DD_t 序列，增状态管理复杂度；③ 触发阈值无行业标准（不像 8/15/20/25% 有机构基准）。重评：实盘运行后若发现"浅回撤长时间"比"深回撤短时间"更危险（UI 高但 drawdown_pct 低），引入 UI 作补充触发条件（§6.8）

### 4.7 Time-in-Drawdown Kill Switch（时间维度 Kill Switch）—— 暂缓

- **算法**：`T_kill = MaxDDD_OOS × 1.5`，策略在水下的**连续时间**超 OOS 最大回撤期 1.5 倍时触发不可逆停机。[invistaja 2026-08-02](https://invistaja.app.br/time-in-drawdown-algotrading/)，理论支撑 [Rej, Seager & Bouchaud 2017](https://arxiv.org/abs/1707.01457)：drawdown 持续时间随 Sharpe **平方**下降——TiD 是比 depth 更敏感的"策略失效"信号
- **与 Ulcer Index（§4.6）的关系**：UI 度量"深度×时间"痛苦指数（连续值，触发减仓），TiD 是"纯时间"硬停机（离散值，不可逆退出）——UI 是节流阀，TiD 是断路器
- **暂缓理由 + 重评条件**：① **MaxDDD_OOS 依赖回测**——实盘样本 <6 个月估计不准，需 ≥1 年实盘或 walk-forward 回测；② **不可逆过激**——策略数少（3-5 个）误杀成本高，当前 Kill Switch（§3.5）可人工复位而 TiD 不可逆；③ **与 regime 转换冲突**——牛转熊所有策略同步回撤，TiD 会同时停掉多策略丧失恢复机会。重评：实盘 ≥1 年后，若某策略长期水下且 IC 衰减监控验证 alpha 衰减，引入 TiD 作该策略退役触发（§6.9）

### 4.8 CUSUM + Hawkes + Lee-Mykland 统计检测触发 —— 暂缓

- **算法**：用统计异常检测替代"阈值触发"的 Kill Switch / 回撤告警，[Tugbars/Finance-Kill-Switch 2025-11](https://github.com/Tugbars/Finance-Kill-Switch) 实现——**CUSUM** 检测收益均值漂移（比固定回撤阈值更早发现 alpha 衰减）；**Hawkes 过程** 检测亏损事件时序聚集；**Lee-Mykland 检验** 检测收益跳跃（区分漂移亏损=策略失效 vs 跳跃亏损=黑天鹅）
- **与当前阈值触发的对比**：
  | 维度 | 当前阈值触发 | 统计检测触发 |
  |---|---|---|
  | 回撤告警 | drawdown > 5/10/15% 固定阈值 | CUSUM 检测均值漂移，自适应策略 alpha 衰减 |
  | 连续亏损 | "连续 5 天"硬计数（§3.5，待实现 §6.2）| Hawkes 检测聚类强度，区分独立 vs 聚集亏损 |
  | 黑天鹅 | BS-007 多模式同触发（§3.5）| Lee-Mykland 检测跳跃显著性，区分漂移 vs 跳跃 |
- **暂缓理由 + 重评条件**：① 复杂度高（三套统计模型校准远超阈值法可解释性）；② 个人系统样本短（Hawkes λ 估计需足够亏损事件）；③ 当前阈值法已 production，统计检测更优但非必需。重评：实盘 ≥1 年后，若①阈值法误触发频繁 ②连续亏损判别力不足 ③黑天鹅误报多，引入统计检测升级 §6.7 诊断（§6.10）。**实践调参指南**（[Iyer 2026-01](https://mathandmarkets.com/p/detecting-decay-in-real-time-when) + [Iyer 2026-02](https://mathandmarkets.com/p/regime-detection-part-3-beyond-hmms)）：CUSUM 起始参数 k=0.5σ / h=4σ（Sharpe~1 策略真实变点后约 50 个交易日触发）；三信号框架 CUSUM + BOCPD + 滚动夏普集成；BOCPD 变点概率 p∈[0,1] 可驱动 `position_cap *= (1 - p * reduction_factor)` 实现"软 kill switch"（即 §4.18 工程化路径）

### 4.9 Pain Index（水下面积）—— 暂缓

- **算法**：`PI = (1/T) × Σ|DD_t|`，回撤深度的**时间平均**（"水下面积"），[tradingwyckoff 2026-01](https://www.tradingwyckoff.com/en/algorithmic-trading/drawdown-trading-guide/)——UI 是 `sqrt(mean(DD_t²))`（平方惩罚深谷），PI 是 `mean(|DD_t|)`（线性）
- **度量对比**：
  | 度量 | 公式 | 惩罚维度 | 直觉 |
  |---|---|---|---|
  | drawdown_pct（当前） | 单点 DD_t | 仅深度（瞬时） | "现在亏多少" |
  | Pain Index | mean(\|DD_t\|) | 深度 × 时间（线性） | "水下平均深度" |
  | Ulcer Index | sqrt(mean(DD_t²)) | 深度 × 时间（平方惩罚深谷） | "水下痛苦度（深谷加权）" |
- **暂缓理由 + 重评条件**：① 与 UI（§4.6）同类择一，UI 因平方惩罚更敏感而优先；② 单点值足够 MVP；③ 触发阈值无行业标准。重评：与 §4.6 同步；UI 作触发条件引入时，PI 作可解释性辅助度量（报告展示用，不参与触发）

### 4.10 TradeShield 静态+Trailing 双模式回撤 —— 部分采纳

- **算法**：[PropGuard TradeShield 2026-08-08](https://github.com/youcefbibo53/PropGuard-Trailing-Equity-Armor/) 双模式：① **静态模式** = 回撤相对**初始本金**的固定百分比；② **Trailing 模式** = 回撤相对**峰值净值**的百分比（"盈利保护"+"本金保护"两道线）
- **与当前方案对比**：
  | 模式 | 当前项目 | TradeShield 双模式 |
  |---|---|---|
  | Trailing（peak 基准） | ✅ 已实现（§3.8 capital_curve_manager peak NAV） | ✅ 同 |
  | Static（初始本金基准） | ❌ 无 | ✅ 第二道线 |
  - 当前只有 trailing 模式。trailing 的问题：账户大幅盈利后 trailing 5% 绝对金额很大，但相对初始本金可能仍盈利丰厚——无"无论如何不能亏初始本金 X%"的硬底线
- **部分采纳理由 + 裁决**：① trailing 已实现无需改动；② static 模式价值有限——个人系统无 prop firm"初始本金红线"考核；③ **但作为"破产底线"有保留价值**——账户 100 万涨到 500 万后，trailing 25%（Kill Switch）= 跌到 375 万（仍赚 275 万），极端崩盘可能跌破 initial 100 万，static 模式（initial × 0.85 = 85 万即 Kill Switch）是"绝对破产防护"。裁决：trailing 保留（已实现），static 模式作为"绝对破产底线"暂缓——§3.5 Kill Switch 触发条件表新增"组合净值 < 初始本金 × 0.85"作**第五类触发源**（与回撤 25% 并列），待 §6.11 施工时实现（§6.15 待裁定）

### 4.11 Hierarchical Risk Parity 聚类归因 —— 暂缓

- **算法**：[López de Prado 2016](https://quantresearch.org/Publications.htm) HRP 用相关性矩阵层次聚类树做风险分配；[marketmaker.cc 2026](https://marketmaker.cc/en/research/) 4800 次实验验证 HRP 在 T/N 低、结构化协方差下优于 min-variance 和 1/N。归因价值：聚类树识别"策略簇"——哪些策略在高相关簇内同步回撤
- **与 §3.16 归因的关系**：当前用平均相关系数（>0.7 系统性 / <0.4 策略特定），HRP 更精细——5 策略中 3 个高相关同步亏、2 个独立时 avg_corr 被拉低可能误判为策略特定，HRP 能识别"3 策略簇"为"部分系统性"
- **暂缓理由 + 重评条件**：① **策略数不足**——3-5 个策略聚类树太简单，HRP 需 ≥8 个策略才有聚类价值；② avg_corr 阈值法 MVP 判别力足够；③ HRP 权重分配属 G12（[31_position_sizing](31_position_sizing.md)）非本备忘，只借聚类树做归因。重评：策略数 ≥8 后，若 avg_corr 无法区分"部分系统性"（簇内高 + 簇间低），引入 HRP 聚类树作 §3.16 归因增强（§6.16 与六类框架同步评估）

### 4.12 MPC 连续风险厌恶调整 —— 暂缓（P4 远期）

- **算法**：[Nystrup, Boyd, Lindström & Madsen 2019](https://backend.orbit.dtu.dk/ws/files/149812772/Multi_Period_Portfolio_Selection_with_Drawdown_Control.pdf) 用 MPC 动态优化组合，核心创新**根据已实现回撤连续调整风险厌恶系数** γ(dd)（非离散阈值），多变量 HMM 预测多期收益均值/协方差，receding-horizon 每期重优化。[arXiv:2604.00415 DLP-SMPC 2026-04](https://arxiv.org/html/2604.00415v1) 同类：随机 MPC，TSLA MaxDD 12.17% vs Buy-and-Hold 73.63%
- **与当前方案的对比**：
  | 维度 | 当前 §3.2 三层映射 | MPC 连续风险厌恶 |
  |---|---|---|
  | 风险厌恶 | 离散阶梯（5/10/15% → 80/50/30%）| 连续函数 γ(dd) |
  | 时间维度 | 单期 | 多期（HMM 预测 N 期，receding-horizon）|
  | 前馈/反馈 | 纯反馈（已亏才减）| 前馈（HMM 预测）+ 反馈（回撤调整）|
  | 计算复杂度 | O(1) 阈值比较 | O(N³) 每期凸优化 + HMM 参数估计 |
  | 可解释性 | 高（阈值明确）| 低（γ 函数 + HMM 隐状态）|
- **暂缓理由 + 重评条件**：① **HMM 需长样本**（≥2 年稳定实盘，本项目 <6 个月，短样本过拟合则 MPC 退化为纯反馈）；② **alpha 层未成熟**——regime 是市场状态分类非收益预测，无 μ/Σ 输入源；③ **杠杆不适用**（A 股个人融资融券受限）；④ **可解释性硬约束**。重评：① 实盘 ≥2 年稳定样本；② alpha 层收益预测模块 production；③ 业主接受度验证后引入（§6.17，P4）。当前 recovery_factor 0.25→0.50→0.75 阶梯是其离散近似，MPC 落地后可平滑化

### 4.13 趋势跟踪回撤防御层 —— 暂缓（P4，A 股需裁定）

- **算法**：[Noguer i Alonso & Al-Fallouji 2026-07 (arXiv:2607.00883)](https://arxiv.org/html/2607.00883v1) 连续时间 CVaR 框架，OTM 看跌期权 + 系统化趋势跟踪放入连贯尾部风险 mandate。**时间分离核心洞察**：凸性保险（puts）跳跃冲击时立即 reprice；趋势跟踪首次冲击滞后（信号须穿零），但**持续回撤中越来越防御性**且无期权费。[AQR 实证](https://philippdubach.com/posts/long-volatility-premium/)：puts 赢 COVID 突然崩盘，trend-following 赢 dot-com 持续熊市——时间分离互补
- **A 股约束的适配问题**：
  | 原论文假设 | A 股约束 | 适配方案 |
  |---|---|---|
  | 可做空（趋势做空对冲）| 不能做空 | 只能"减仓/空仓"实现防御 |
  | OTM puts 可买 | 无期权 | 趋势跟踪是唯一防御层，无凸性保险 |
  | T+0 可日内调仓 | T+1 | 趋势信号须日度生成 |
  | 多资产分散 | A 股单一市场 | 趋势信号有效性降低 |
- **暂缓理由 + 重评条件**：① A 股趋势跟踪"持续回撤递增防御"有效性未实盘验证（牛短熊长、政策驱动、散户占比高）；② 与 §3.9 regime Shrinkage 职责边界需裁定（regime 状态分类 vs 趋势价格动量，是否冗余）；③ 趋势信号来源模块未定（需与 G09/G10 协调）。重评：① 实盘验证 A 股趋势信号防御有效性；② 与 [34_regime_meta_allocator](34_regime_meta_allocator.md) 裁定职责边界；③ 信号来源确定后作 §3.9 regime 之外**第二前馈防御层**（§6.18，P4）

### 4.14 CDaR 回撤深度连续度量 —— 暂缓（P2，与 UI/PI 同类但更优）

- **算法**：[Chekhlov, Uryasev & Zabarankin 2000/2005](https://uryasev.ams.stonybrook.edu/wp-content/uploads/2021/10/Drawdown_Portfolio_Optimization_Problems_and_Drawdown_Betas.pdf) CDaR = drawdown 序列的 CVaR（"最差 α% 回撤的平均值"）。[MetricGate 2026-06](https://metricgate.com/docs/conditional-drawdown-at-risk/) 论证 CDaR 是 coherent risk measure（单调/次可加/正齐次/平移不变），α→0 收敛 MaxDD，LP 可解；[Man Numeric CVaR 2025-07](https://www.man.com/man-numeric-cvar-insights) 论证 CVaR 优于方差——同样适用 CDaR 优于 MaxDD
- **度量对比**：
  | 度量 | 公式 | 捕获维度 | 当前状态 |
  |---|---|---|---|
  | drawdown_pct（当前 §3.8）| 单点 DD_t | 仅瞬时深度 | ✅ 已实现 |
  | Ulcer Index（§4.6 暂缓）| sqrt(mean(DD_t²)) | 深度×时间（平方惩罚深谷）| 暂缓 |
  | Pain Index（§4.9 暂缓）| mean(\|DD_t\|) | 深度×时间（线性）| 暂缓 |
  | **CDaR（本节）** | mean(worst α% of DD_t) | **尾部回撤均值（path-dependent）** | 暂缓（P2）|
  - CDaR 与 UI/PI 本质区别：UI/PI 是全样本平均，CDaR 是**尾部均值**——聚焦"真正痛苦的回撤"而非稀释于长期平静期
- **暂缓理由 + 重评条件**：① 与 UI/PI 同类择一，需先验证"单点 drawdown_pct 不足"的实盘证据；② α 选择（0.05 vs 0.10）无行业标准需自校准；③ 单点值足够 MVP，CDaR 价值在"组合优化目标"（属 G12）而非"触发阈值"。优势：coherent（次可加性，MaxDD 不满足）+ LP 可解（[PyPortfolioOpt EfficientCDaR](https://blog.csdn.net/gitblog_00739/article/details/148508135) 已有实现）+ 可作 [31_position_sizing](31_position_sizing.md) 仓位优化目标。重评：与 §4.6/§4.9 同步，优先级高于 UI/PI（coherent + LP 可解）；实盘发现"浅回撤长时间"后引入 CDaR 作 ① 回撤深度补充度量（报告）+ ② 31 号仓位优化回撤约束（§6.19，P2）

### 4.15 多 agent 协作回撤控制 —— 拒绝（过度工程，仅借鉴思路）

- **算法**：[RMATS 2026-05 (arXiv:2605.25311)](https://arxiv.org/abs/2605.25311) 4 agent（Sentiment/Report/Analysis/Risk）+ 递归 Manager，561 交易日 MaxDD 9.62%（vs MVO 15.49%）。Risk Agent 用 CVaR + EWMA + 多级 circuit breaker（DD/GRS/vol 三源 OR），RL 目标 `R_t = r_t − λ₁σ_t − λ₂max(0, DD_t − θ)`（λ₁=0.8, λ₂=1.5）。[MARCD 2026 (arXiv:2510.10807)](https://arxiv.org/html/2510.10807v3) 同类：Gaussian HMM regime + diffusion + CVaR QP，OOS MaxDD 9.3% vs BL 14.1%
- **拒绝理由（过度工程）**：① 个人项目不需要多 agent 协作——RMATS 是机构级 24 资产架构，本项目 3-5 策略单进程规则式风控已足够；② LLM agent 的 alpha 不可作部署证据（[arXiv:2605.16895 The Alpha Illusion 2026-05](https://arxiv.org/html/2605.16895v1)）；③ Risk Agent 独立性本项目已实现（§4.2 三模块职责分离）；④ RL 目标回撤惩罚项已评估（§3.9 选乘性替代加性）
- **借鉴范围**：
  | RMATS/MARCD 思路 | 本项目借鉴方式 | 对应章节 |
  |---|---|---|
  | Risk Agent 独立于策略 | 已实现（tracker/curve_manager/controller 三模块分离）| §3.1/§4.2 |
  | RL 目标回撤惩罚项 | 评估后选乘性叠加替代加性 | §3.9 |
  | CVaR + EWMA 动态协方差 | 已在 [36_var_es_monitoring](36_var_es_monitoring.md) 实现 | G17 |
  | 多级 circuit breaker（DD/GRS/vol 三源 OR）| 本项目 Kill Switch 多源 OR（§3.5）| §3.5 |
  | HMM regime 分类 | 本项目 regime 是分类（非 HMM），属 [34_regime_meta_allocator](34_regime_meta_allocator.md) | G15 |
- **不设重评条件**：多 agent 架构与个人项目定位根本不匹配；规模扩展到机构级（≥20 策略 + 多资产 + 团队运营）可重新评估

### 4.16 Conditional Expected Drawdown（CED）线性因子归因 —— 暂缓

- **算法**：[Goldberg & Mahmoud 2016 (DOI 10.1007/s11579-016-0181-9)](https://alexandria.unisg.ch/server/api/core/bitstreams/f53d98e4-3cfb-4517-8054-8287a2912bc8/content) CED = maximum drawdown 分布的尾部均值：CED_α(X) = E(μ(X) | μ(X) > DT_α)。**正齐次** → Euler 定理线性归因到因子；**convex** → 可优化。[arxiv 1404.7493v3](https://arxiv.org/pdf/1404.7493v3) LP 算法 + [internQuant/conditional-drawdown](https://github.com/internQuant/conditional-drawdown) Python 实现
- **与 §3.16 归因的关系**：avg_corr 启发式（>0.7/<0.4）只判"系统性 vs 策略特定"，CED 由 Euler 分解量化每个因子贡献：CED(P) = Σ w_i · MRC_i^CED(P)
- **与 §4.14 CDaR 的关系**：
  | 度量 | 定义 | 优化 | 归因 | 当前状态 |
  |---|---|---|---|---|
  | CDaR（§4.14）| drawdown 序列的 CVaR | LP 可解（组合优化）| 无显式归因 | 暂缓（P2）|
  | CED（本节）| maximum drawdown 分布的尾部均值 | LP 可解 | **Euler 线性归因** | 暂缓（P3）|
  - CED 对 serial correlation 敏感是独特优势（回撤本质是路径依赖，ES/volatility 不敏感）
- **暂缓理由 + 重评条件**：① 样本需求（CED 尾部估计需足够路径样本）；② 3-5 策略 avg_corr 足够 MVP；③ 优先级低于 CDaR；④ 策略数 <8 时 Euler 分解统计意义有限。重评：① 策略数 ≥8 且 avg_corr 无法区分"部分系统性"时引入；② 实盘 ≥1 年样本充足；③ 与 §4.14 CDaR / §4.11 HRP 同步评估（§6.24，P3）。**列入理由**：CED 的"正齐次 → Euler 线性归因 + serial correlation 敏感性"填补 §3.16"线性因子归因"空白，与 CDaR（优化）互补

### 4.17 Schmitt RWC Conformal Risk Control —— 暂缓（P2，与 Conformal Kelly 互补）

- **算法**：[Marc Schmitt 2026-02 (arXiv:2602.03903, Oxford)](https://arxiv.org/pdf/2602.03903) **Regime-Weighted Conformal Risk Control（RWC）**——指数时间衰减 + regime 相似性权重校准 VaR 安全缓冲，model-agnostic wrap 任意 quantile 预测器，weighted exchangeability 下有限样本覆盖保证。CRSP 实证：**TWC 是 drift 下强默认**，RWC 增 regime 加权改善 regime-conditional 稳定性
  **核心公式**：
  ```
  buffer_t = WeightedQuantile({s_i}, weights={w_i}, level=1-α)
  w_i = exp(-λ · (T - t_i)) · regime_similarity(regime_t, regime_{t_i})
  VaR_t = base_quantile_forecast(t) + buffer_t
  ```
- **与 §6.21 Conformal Kelly 的关系**：
  | 维度 | Conformal Kelly（§6.21） | Schmitt RWC（本节） |
  |---|---|---|
  | 目标 | position sizing（leverage 缩减） | VaR 校准（safety buffer） |
  | 触发 | 预测区间下行连续 miss | 预测误差 nonconformity score |
  | 输出 | leverage 系数 | VaR 安全缓冲 |
  | 与回撤的关系 | 间接（leverage ↓ → MaxDD ↓） | 直接（VaR 是 §3.10 C 层输入） |
  | 设计原则 | slow unweighted（稳定性优先） | TWC 强默认 + RWC regime 加权 |
  - Kelly 管"仓位多大"，RWC 管"VaR 多严"——正交可叠加；两者"简单时间加权足够"结论一致
- **与 [36_var_es_monitoring](36_var_es_monitoring.md) 的关系**：当前 §3.2 参数法 VaR 假设正态+平稳，RWC 提供"非平稳 + regime 结构"下 distribution-free 校准；regime 相似性权重与 [34_regime_meta_allocator](34_regime_meta_allocator.md) regime 标签天然对齐
- **暂缓理由 + 重评条件**：① 依赖 conformal 预测层（36 号当前参数法，无 conformal 基础设施）；② regime 相似性需定义"regime 距离"（离散分类→连续度量）；③ 与 Conformal Kelly 同类但 RWC 更直接作用于 VaR，优先级略高；④ 校准集需 ≥100 历史预测误差，实盘 <6 月不足。重评：① 36 号 conformal 预测层 production；② 34 号 regime 特征工程稳定；③ 实盘 ≥6 月校准集积累后引入（§6.25，P2）。**最小集成路径**：先 TWC（简单）验证稳定后再加 RWC

### 4.18 Bayesian Online Changepoint Detection（BOCD）概率 Kill Switch —— 暂缓

- **算法**：[Adams & MacKay 2007（arXiv:0710.3742）](https://arxiv.org/abs/0710.3742) 维护 **run-length** `r_t` 后验 `P(r_t | x_{1:t})`，输出 `P(changepoint at t) = P(r_t = 0 | x_{1:t})` **连续概率**而非二元判断。核心递推：growth 概率 `∝ P(x_t | r+1) · P(r_{t-1}) · (1-H)`；changepoint 概率 `∝ P(x_t | r=0) · Σ P(r_{t-1}) · H`（H = hazard，通常常数 1/λ）。[mathandmarkets 2026-02](https://mathandmarkets.com/p/detecting-decay-in-real-time-when) 策略衰减检测框架；[quantbeckman 2025-11](https://www.quantbeckman.com/p/with-code-switch-off-bayesian-online) **probabilistic kill switch**——N-IG 共轭先验 + Student-t 似然（重尾适配）+ 双触发系统
- **与 §4.8 CUSUM/Hawkes/Lee-Mykland 的关系**：
  | 维度 | CUSUM（§4.8）| BOCD（本节）|
  |---|---|---|
  | 检测目标 | 均值漂移（需指定 μ₀）| 任意参数变化（无需指定 μ₀）|
  | 输出形式 | 二元阈值告警 | 连续概率 P(r_t=0) |
  | 参数依赖 | μ₀ + k + h | H（hazard）+ 似然模型选择 |
  | 在线性 | O(1) | O(t)（需 pruning）|
  | 先验融合 | 无 | 可整合经验参数（期望 run-length）|
  - CUSUM 需指定 μ₀（选择困境）；BOCD 通过 run-length 后验自适应估计。概率输出允许分级响应（P>0.5 减 30% / P>0.7 减 60% / P>0.9 硬停机）。BOCD 是 §4.8 三检测器的"概率化统一演进"
- **quantbeckman 双触发系统**：硬触发 `P > 0.8` → 立即硬停机（对齐 §3.5 不可覆盖通道）；软触发 `P > 0.5` 持续 **5 个交易日** → 减仓 50%（对齐 §3.4 recovery_factor 阶梯）；N-IG 共轭先验 + Student-t（ν=3-7）适配 A 股重尾；log-space 数值稳定；run-length > T_max（100-200）pruning
- **与 §4.7 TiD 的关系**：TiD 检"长时间不恢复"（纯时间硬停机），BOCD 检"参数已变化"（概率变点）——互补：TiD 兜底 BOCD 未检测的缓慢衰减，BOCD 前瞻 TiD 无法预警的突发断点
- **暂缓理由 + 重评条件**：① 计算 O(t) 需工程化 pruning（日度决策可接受）；② 样本短（quantbeckman 实证需 ≥200 交易日）；③ 随 §4.8 同期暂缓；④ 似然模型选择额外复杂度；⑤ 与 §3.5 固定阈值 Kill Switch 职责重叠——MVP 先验证固定阈值法。重评：① 实盘 ≥1 年与 §6.10 同步；② 固定阈值误触发频繁或漏检结构断点时引入（§6.27，P3）；③ 似然 Student-t（ν=5 起步），hazard 常数 1/λ（λ=252，期望 1 年变点一次）；④ 最小路径：先单策略试运行（输出仅供参考不触发），验证后接双触发
- **Dm-BOCD 鲁棒性升级路径**（[arXiv:2302.04759](https://ar5iv.org/abs/2302.04759)）：**diffusion score matching** 广义贝叶斯替代精确似然，封闭形式共轭后验，比 β-BOCD 快 10x+ 且对离群点鲁棒——A 股厚尾/跳空下标准 BOCD（Student-t）若误报频繁，作 §6.27 同步重评的升级子项

### 4.19 Signature-based Path Portfolio（路径签名组合优化）—— 暂缓（P5+，理论远期）

- **算法**：[Noguer i Alonso 2026-08-03（arXiv:2608.02355）](https://arxiv.org/abs/2608.02355) Path Portfolio Optimization——以价格路径 **signature（签名）**作通用坐标，组合是 signature 的线性泛函，mean-variance 问题变成**张量上的线性系统**。**实证**：已知 expected signature 时 certainty equivalent 提升 **11 倍**（2 资产）/**60 倍**（20 资产）；estimated signature 需 **6 obs/param**，只拟合 driver generator 重建可降至 **1 obs/param**；增益集中在 symmetric block。**Lemahieu & Boudt（Ghent）**：signature **kernel trick** 线性近似 expected drawdowns + **VAE** 生成路径集成，实现 minimum drawdown 组合优化
- **path-dependent 风险三层递进**：
  | 层级 | 方法 | 数学基础 | 当前状态 |
  |---|---|---|---|
  | 具体度量 | CDaR（§4.14）/ CED（§4.16）| drawdown 序列 CVaR / MDD 分布尾部均值 | 暂缓（P2/P3）|
  | 签名近似 | Lemahieu & Boudt | signature kernel trick 线性近似 | 暂缓（P5+）|
  | 统一框架 | Noguer i Alonso Path Portfolio | signature 通用坐标，张量线性系统 | 暂缓（P5+）|
  - CDaR 是 signature 框架的特例（特定投影）。"sample-size floor 属 unstructured estimation"——直接估计需 6 obs/param 对本项目是关键约束
- **暂缓理由（P5+）+ 重评条件**：① 理论深度远超 MVP（rough paths 纯数学，需 sigkit/esig 专门库）；② 样本约束（即使 driver generator 重建也需 ≥1 年实盘）；③ VAE 生成路径引入 model risk；④ 优先级低于 CDaR/CED；⑤ 过度工程红线。重评：① 实盘 ≥2 年且 CDaR/CED 已验证实盘价值后评估增量；② 策略数 ≥10 需统一框架时；③ Python signature 库成熟且 A 股适配后。**不设近期施工计划**，仅作理论远期登记（与 [91_density_prediction](91_density_prediction.md) 密度预测正交，可远期交叉）

### 4.20 Continuous Cash-Overlay Filters（连续现金叠加回撤过滤器）—— 暂缓（P3，模块化回撤工具）

- **算法**：[Xiong arXiv:2606.09025](https://arxiv.org/abs/2606.09025) 2026-06-08——growth–defensive sleeve 上叠加两类连续过滤器：① **slow-tail compensation**（防防御资产持续跑输）；② **V-shape crash-brake**（V 型下跌急刹提现金、反弹快速恢复）；③ **max-cash 规则**（两过滤器取更保守者）
- **实证**（2017–2026 严格 walk-forward）：
  | 指标 | 100% R（无过滤器） | + Cash-Overlay | 改善 |
  |---|---|---|---|
  | CAGR | 16.62% | **20.45%** | +3.83% |
  | 最大回撤 | -33.59% | **-16.77%** | 改善 16.82% |
  即**同时提升收益和降低回撤**，walk-forward 验证非过拟合
- **与本项目的关系**：范式差异——本项目离散分档触发（5/10/15%），Xiong 连续比例调整；V-shape crash-brake 是**中速回撤软着陆**，§3.5 Kill Switch 是**极端回撤硬着陆**——互补，Kill Switch 是 crash-brake 止不住时的最终兜底
- **暂缓理由（P3）+ 重评条件**：① 本项目无 growth-defensive sleeve 架构（5 策略独立 sleeve）；② A 股 T+1 限制连续调整响应延迟；③ 34 号 regime Shrinkage 已是 9+3 态细粒度节流；④ max-cash 规则长期可能过度保守。重评：实盘 ≥1 年离散分档"阶梯跳变"问题显著 / sleeve 扩展含防御型策略 / 34 号证明不足时评估叠加连续微调（非替代）。**不设近期施工计划**

### 4.21 Transfer-Entropy + Hawkes + Von Neumann 图熵网络级系统性风险预警—— 暂缓（P4，网络级远期）

- **算法**：[An & Dai, MDPI Entropy 28(8), 887, 2026-08-06](https://www.mdpi.com/1099-4300/28/8/887)——转移熵 + 多元 Hawkes 互激矩阵 + 图拉普拉斯谱分解 + **Von Neumann 图熵 + 谱间隙比**作网络脆弱性度量。**关键发现**：图熵在主权债指数**峰值回撤前 7-12 个交易日**达历史极端值——kill switch 的**预触发信号**
- **关系与 A 股适配**：§4.8 是单资产级检测，本文是网络级系统性视角（比单资产变点更早，7-12 天提前量为"减仓但不平仓"黄色预警争取时间）；A 股迁移到申万一级 28 行业指数（行业间转移熵 + 行业级极端跌幅 Hawkes 互激 + 行业网络图熵极端值作预触发阈值）
- **暂缓理由（P4）+ 重评条件**：① 网络级基础设施需求（实时管道 + 转移熵估计 + Hawkes 拟合 + 谱分解）；② 个人系统单账户定位，行业传染信号到仓位调整映射路径长；③ 图熵极端值阈值需 A 股 3-5 年含牛熊数据校准；④ 与 §3.5 ⑦ ORCA 谱特征维度重叠（ORCA 更轻量且有 A 股实证）。重评：策略数 ≥8 / 实盘 ≥1 年发现 Kill Switch 滞后需 7-12 天预警 / 申万行业指数实时管道建成。**不设近期施工计划**

### 4.22 Xiao Jian et al. 2026-02 A 股 HFT 多层复杂网络 herding 渗流相变检测 —— 暂缓（P4，A 股网络级远期）

- **算法**：[Front. Phys. 2026-02-05](https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2025.1733200/full)（中南财经政法大学）多层复杂网络 ABM（regulatory/core institutional/market-maker/retail 四层）模拟 A 股 HFT 风险传导。**核心发现**：① 策略同质化系数 **ρ > 0.65** 时发生**渗流相变**，系统性风险概率 0.2 → 0.7+；② 通信延迟差 >50ms 时散户订单截获率非线性升至 82%。A 股特殊性：散户 80% 交易量 vs 0.3% 外资机构控制 43.6% 订单流
- **关系**：§4.21 是信息流+网络拓扑层，本文是策略同质化+渗流相变层（ρ>0.65 阈值是图熵极端值的补充）；§3.5 ⑦ ORCA 是价格相关性层（有 A 股实证先施工），本文作 ABM 模拟远期候选
- **暂缓理由 + 重评条件**：① ABM 模拟计算复杂度高；② 全市场策略同质化 ρ 实时监控样本不足；③ 个人系统是价格接受者非制定者。重评：策略数 ≥8 后 ρ 估计有意义 / A 股全市场实时数据管道建成 / 实盘发现 kill switch 滞后需渗流相变提前预警

### 4.23 Chen 2026-04 A 股 GWII 板块 herding CSAD/CSSD 实证 —— 暂缓（P3，A 股 herding 轻量检测）

- **算法**：[ICFIED 2026](https://docker.atlantis-press.com/proceedings/icfied-26/126023570) Chen 2026-04-29 CSAD + CSSD 检测 A 股 GWII 板块 herding。模型：`CSAD_t = (1/N) Σ |R_i,t − R_m,t|`，非线性回归 `CSAD_t = α + β·|R_m,t| + γ·R_m,t²`，**γ < 0 表示 herding**；`CSSD_t = sqrt((1/(N−1)) Σ (R_i,t − R_m,t)²)` 同理。**实证**：2025-06 GWII 板块 2951.33→5735.31，CSAD/CSSD 检出显著 herding
- **关系**：ORCA 是重模型（127 谱特征 + RF），CSAD/CSSD 是轻量截面离散度统计量——适合个人系统 MVP；Chen 实证验证 A 股 herding 存在性 + 可检测性
- **暂缓理由 + 重评条件**：① 需截面数据管道（全市场/板块个股收益离散度）；② 板块 herding → 仓位调整映射需 A 股历史校准；③ herding 检测是前馈预警，施工优先级低于 Kill Switch（风险优先原则）。重评：板块级实时数据管道建成 / 实盘 ≥1 年发现 Kill Switch 滞后需前馈预警 / §3.5 ⑦ ORCA 评估过重时作轻量替代

### 4.24 Lévy-stable Drawdown Scaling——封闭形式非高斯回撤传播（远期，2026-08-10 新增）

- **算法**：[arXiv:2511.07834](https://arxiv.org/abs/2511.07834) Vlasiuk 2025-11（Columbia）。Lévy 窗口 `[τ_UV, τ_IR]` 内收益服从 α-稳定分布（α∈(1,2)），尺度 τ^{1/α}；窗口外聚合 √τ 体制。以锚定 horizon τ₀ 为基准，**高斯假设的 drawdown 低估 = 显式偏差项 `(τ/τ₀)^{1/α} - (τ/τ₀)^{1/2}`**。drawdown 功能 `DD_{τ,p} := (E(D_τ)^p)^{1/p}`，Lévy 传播在窗口内跨 horizon 一致
- **与 §6.23 Non-Gaussian Lookup Tables（Landolfi）的关系**：
  | 维度 | Landolfi 2026-07（§6.23/§4.27） | Vlasiuk 2025-11（本节） |
  |---|---|---|
  | 方法 | Monte-Carlo 仿真查表 | 封闭形式解析公式 |
  | 分布假设 | 任意非高斯 | α-稳定（Lévy 窗口内） |
  | 优势 | 分布无关 | 解析 O(1) 无需仿真 |
  | 劣势 | 仿真成本高 | 窗口外失效 |
  两者互补：先用本节解析公式快速估计，Landolfi 仿真做精确验证
- **与 §3.8 的关系**：§3.8 用 close-to-close NAV 日度离散监测——[Li/Li/Yan 2026-02](https://doi.org/10.1017/apr.2026.10053) 推导 Poisson 观测时间下 drawdown 退出恒等式，为日度监测阈值提供 Lévy 理论支撑
- **暂缓理由 + 重评条件**：① α 估计需长样本（log-log 斜率多 horizon 覆盖）；② Lévy 窗口识别工程化成本高；③ 当前 8/15/20/25% 阈值已 §3.21 实证背书，理论校验非必要；④ 与 §6.23 同期暂缓。优势：封闭形式 O(1) + 偏差可量化（α 越小厚尾越重偏差越大）+ horizon 一致性（避免高斯 √T 跨持有期不一致）。重评：实盘 ≥2 年 α 稳定 / §6.23 查表落地后需解析快速估计 / 当前阈值需理论校验时
- **跨文档**：36号 §4.24 登记同论文 VaR/ES horizon 修正；González Cázares & Mijatović 2022 提供 Lévy 过程 drawdown MLMC 仿真算法可作 §6.23 查表算法基础

### 4.25 MFCCA 符号保留多重分形交叉相关组合分配——直接降低 drawdown 的组合配置层远期候选（2026-08-10 新增）

- **算法**：[arXiv:2608.04987](https://arxiv.org/abs/2608.04987) Kakinaka & Umeno 2026-08-05。风险泛函 = **带符号的多重分形交叉相关分析（MFCCA）波动函数**（尺度 s + 波动阶 q 索引）——**保留局部去趋势协方差符号**，同向/反向运动以**相反符号**贡献风险（MFDCCA 修正丢失符号）；q=2 退化为 MVO **严格泛化**。实证：每个要求收益水平上（in/out-of-sample）降 drawdown/VaR/ES **不损失收益**——"无代价降回撤"理论上限候选
- **与 35 号 Protocol 的关系**：
  | 维度 | 35 号回撤 Protocol（当前） | MFCCA（本节） |
  |---|---|---|
  | 层级 | sleeve 级 + firm 级风险节流 | 组合配置层 |
  | 机制 | 反馈式（回撤已发生→减仓） | 前馈式（分配时最小化带符号交叉相关风险） |
  | 度量 | drawdown_pct 单点 + VaR 5 级 | 多尺度带符号波动函数 F(s,q) |
  | 协方差 | [30号 §3.1](30_multi_strategy_concurrency.md) 拒绝 MVO + 协方差估计 | 需多尺度交叉相关估计（比 MVO 更重） |
  | 正交性 | ✅ 正交互补——Protocol 管"回撤后怎么减"，MFCCA 管"分配时怎么避免" |
- **与 30 号 §3.1 拒绝 MVO 的诚实账本**：30 号拒绝针对 MVO 权重对协方差极端敏感 + 样本不足；MFCCA 根本区别——① 符号保留（反向运动**降低**风险，对冲效果正确计入）；② 多尺度；③ q 阶泛化（q>2 强调尾部）。**但** MFCCA 仍需多尺度交叉相关估计，复杂度超 O(N) 与 30 号约束冲突，5 策略下样本不足比 MVO 更严重。与 §6.30 CPPI / §6.32 Put-Option Sleeve 同属组合配置层远期候选；已由 [90号](90_methodology_open_questions.md) v1.3.0 risk parity 五级递进第五级登记
- **暂缓理由（P4）+ 重评条件**：① 层级正交（当前两层架构不引入第三层）；② 计算复杂度超 O(N)；③ 5 策略样本不足；④ 30 号架构裁决约束。重评：项目演进到组合配置层独立模块（同 §6.30/§6.32）/ 策略数 ≥8 / 实盘 ≥2 年多尺度数据。**最小路径**：2 策略 × 3 尺度（日/周/月）offline backtest 验证 A 股符号保留增量价值（§6.35）

### 4.26 Robust Risk Parity (RRP) —— A 股实证的组合配置层远期候选（2026-08-10 新增）

- **算法**：[Li & Ye 2026（Finance Research Letters vol.92(C), DOI:10.1016/j.frl.2026.109586）](https://ideas.repec.org/a/eee/finlet/v92y2026ics1544612326001170.html)。TRP 框架内集成：① 自适应扰动机制；② 鲁棒协方差估计（抗异常点）；③ GARCH 波动率预测；④ 市场状态识别；⑤ 因子结构协方差。**A 股 2012-2024 全样本实证**对比 TRP/EW/GMV/MaxRet/ERP 五基线，收益/Sharpe/Calmar 均优、波动和 MaxDD 更低
- **与 §4.25 MFCCA 的关系**：
  | 维度 | §4.25 MFCCA | §4.26 RRP |
  |---|---|---|
  | 方法 | 多尺度带符号交叉相关（理论前沿） | 鲁棒风险平价（工程化集成） |
  | A 股实证 | 未明确 A 股 | **2012-2024 中国市场全样本** |
  | 创新点 | 符号保留 + 多尺度 | 自适应扰动 + GARCH + regime + 因子结构 |
  | 复杂度 | 高 | 中（标准 RP + 鲁棒增强） |
  | regime 维度 | 无 | 内置（与 [34号 RegimeMetaAllocator](34_regime_meta_allocator.md) 天然对接） |
  互补：MFCCA 是理论前沿，RRP 是工程化集成（A 股实证 + regime）
- **与当前架构的关系**：同 §4.25 层级正交；但 RRP 的 **regime 识别 + GARCH 波动率预测**两组件可独立提取，作 34 号增强候选（不引入完整组合配置层）
- **暂缓理由（P3）+ 重评条件**：① 层级正交；② 完整框架需协方差估计（30 号约束）；③ regime+GARCH 组件可独立评估。重评：34 号 regime 特征工程稳定后评估 GARCH 作 regime 输入增强（组件级集成）/ 演进到组合配置层时评估完整 RRP（§6.36）；**A 股实证优先级高于 MFCCA**（含牛熊周期全样本）

### 4.27 Drawdown Beyond Brownian Motion——回撤阈值非高斯校准与 keep-or-kill 决策表（2026-08-10 新增）

- **算法**：[arXiv:2608.00127](https://arxiv.org/abs/2608.00127) Landolfi 2026-07-31。RSB（Rej-Seager-Bouchaud）drifted Brownian drawdown 闭式框架的非高斯扩展，Monte-Carlo 生成 **4 决策测度查表**：
  1. **MaxDD**（最大回撤深度）
  2. **MaxLoss**（最大单期损失）
  3. **FinalNegTime**（水下时间占比）
  4. **LongestRecovery**（最长恢复交易日数）
- **核心贡献**：① 保持真实 Sharpe/波动率不变，变化偏度/厚尾/波动率聚集/Sharpe 不确定性，证明 **4 测度不同步移动** → 单一高斯表系统性误警（某些测度过松漏警 + 某些过紧误警）；② **fBm 长记忆**：持续性下回撤"放大"几乎全是自相似色散标度 `T^{H-1/2}`（H>1/2），是 **√-time 校准失效**而非路径几何本征危险——警示 [36_var_es_monitoring](36_var_es_monitoring.md) §3.2 参数法 VaR 的 √T 缩放在持续性下同样失效
- **与 35 号 Protocol 的关系**：
  | 维度 | 35 号回撤 Protocol（§3.x） | §4.27（本节） |
  |---|---|---|
  | 层级 | sleeve 级 + firm 级回撤判定与响应 | 回撤阈值校准层 |
  | 职责 | "触发后怎么做"（5/10/15% → 减仓/恢复/Kill） | "阈值怎么定"（给定 Sharpe+分布结构 → 4 测度期望分位） |
  | 输入 | 实时 drawdown_pct / VaR / 策略 PnL | 历史 Sharpe + skew/峰度/聚集参数 + Hurst |
  | 输出 | position_cap / recovery_factor / Kill | 4 测度阈值查表 |
  | 正交性 | ✅ 正交互补；§6.23 是本节早期待裁定登记（同一论文） |
- **实用校准配方**（strategy archetype 分类 → 参数 → 查表）：
  | strategy archetype | 偏度 | 厚尾（峰度） | 波动率聚集 | Hurst H | 查表侧重测度 |
  |---|---|---|---|---|---|
  | 趋势跟踪 | 左偏 | 中重尾 | 中 | >0.5（持续性） | MaxDD + LongestRecovery |
  | 均值回归 | 左偏 | 重尾 | 低 | <0.5（反持续性） | MaxLoss + FinalNegTime |
  | 套利 | 近对称 | 轻尾 | 低 | ≈0.5 | FinalNegTime（浅回撤长时间） |
  | 打板/T0 | 左偏 | 重尾 | 高 | ≈0.5 | MaxLoss（单日极端） |
  | 多因子 | 混合 | 中 | 中 | ≈0.5 | 4 测度均衡 |
  校准流程：① 估计策略 Sharpe + 4 矩参数；② archetype 分类；③ 查 4 测度表得 95%/99% 分位阈值；④ 与 §3.2 经验阈值（5/10/15%）对比——过松收紧，过紧放宽
- **参考参数预设**（ARCHETYPE_PARAMS，Phase 2 实盘估计后覆盖）：trend{skew -0.3, kurt 5.0, vol_clust 0.6, hurst 0.55} / mean_rev{-0.5, 7.0, 0.2, 0.45} / arbitrage{0.0, 3.5, 0.1, 0.50} / t0_snipe{-0.6, 8.0, 0.8, 0.50} / multi_fac{-0.2, 4.5, 0.4, 0.50}；MC 仿真 horizon=252、n_sims=50000、阈值判定 tight/loose 边界 = 查表 MaxDD 与经验阈值比值 >1.2 / <0.8
- **Phase 定位 + 互补性**：Phase 3 校准阶段（与 §6.21/§6.25 同期）——Phase 1 施工 §3.x 三层 + Kill Switch（当前），Phase 2 积累 Sharpe/矩参数样本，Phase 3 查表校准。MVP 不替换 §3.2 阈值，仅作校准参考。§4.24 Lévy-stable 解析（α-稳定窗口 O(1)）vs 本节仿真查表（任意分布）；§4.6/§4.9/§4.14 是事后度量（报告），本节是事前校准（阈值设定）；与 §6.28 vol-matched threshold 正交可叠加；§6.23 早期登记 → 本节施工形态 → §6.37 keep-or-kill 裁定
- **暂缓理由（P2-P3，Phase 3）+ 重评条件**：① 需实盘 Sharpe 稳定估计（≥6 月）；② 矩估计需 ≥1 年日频；③ 当前阈值已 §3.21 实证背书；④ 与 §6.23 同步。重评：实盘 ≥6 月 Sharpe 稳定 + 矩估计稳定后，查表校准 5/10/15% 与"给定 Sharpe 期望 MaxDD 分位"对比——过松收紧过紧放宽（§6.37）

### 4.28 Aldridge & Krawciw AI Governance——4 层治理框架+regret-covariance policy drift+crowding model 联合回撤定量背书（2026-08-10 新增）

**方案**：[arXiv:2608.02311](https://arxiv.org/abs/2608.02311) Aldridge & Krawciw（RiskAICenter）2026-08-03。**88% 受调金融从业者报告无 agentic AI 运营治理框架**（尽管 100% 知晓部署），75 家美国大型资管 Form ADV 披露中仅 24 家有正式治理政策。治理差距是**架构性而非文化性**——持续重训练的 agentic policy 在设计上违反静态治理假设。

**4 层治理框架**（Policy / Engineering / Composition / Systemic）：

1. **Policy 层**：reward function 视为 policy spec（allowed action set / risk budgets / market-state constraints / user-account constraints 四元组）。**Kill-switch 触发应基于 inner（pre-decoding）LLM confidence 而非 declared confidence**——Chen et al. 2026 实证 declared confidence 被 decoding 偏置
2. **Engineering 层**：**regret-covariance statistic** 检测 policy drift——仅从观测数据计算（不需白盒），对比 intended vs observed regret 协方差，漂移超阈值告警
3. **Composition 层**：**calibrated crowding model**——两 agent 收敛相关暴露时 joint drawdown probability 从 **39.2% 升至 79.3%**（可复现模拟）——"分散失效"（§3.21 根因②）的**定量模型背书**
4. **Systemic 层**：vendor embedding model 升级可 shift 策略收益分布而不触发单点告警——需跨组件监控（data feed / embedding model / portfolio construction 任一"未坏"但组合漂移）

**90-day 实施序列**：policy spec 声明 → regret-covariance 监控 → crowding 模型校准 → vendor 漂移跨组件监控。

**与本项目的关系**：

1. **与 §3.5 Kill Switch 治理**：Aldridge 4 层提供治理架构背书——Policy（§3.5 触发条件声明）+ Engineering（§3.5 执行路径）+ Composition（§3.16 相关性归因）+ Systemic（§3.15 Ghost 检测跨组件）。**inner LLM confidence kill-switch** 是新维度——本项目 Kill Switch 基于外部可观测量，inner confidence 是模型自身不确定性前馈触发器，与 §4.18 BOCD 正交（BOCD=分布变了，inner confidence=模型自己不确定）。当前无 LLM 决策层，登记为条件性候选
2. **与 §3.21/§3.16 的关系**：crowding model 将"分散失效"从定性引用升级为定量因子——Phase 2 可将 §3.16 avg_corr 单点阈值升级到 crowding-adjusted joint drawdown probability。与 §4.21 网络级前馈互补（Aldridge crowding 是组合配置级定量）
3. **与 §3.15 Ghost 检测的关系**：Systemic 层"vendor 升级 shift 分布"对应"策略代码/模型版本升级后跨重启状态恢复"——Ghost 检测是 regret-covariance 的物理对应（预期持仓 vs 实际持仓漂移）；可映射为"行情数据源 / 因子计算 / 仓位裁决"三组件跨组件一致性校验
4. **与 §4.18 BOCD / FSB（§3.5 ⑧）的关系**：regret-covariance 检 policy 行为 drift（"策略行为偏离 intended"），BOCD 检收益分布 changepoint（"环境变了"）——互补可叠加；FSB 是监管顶层锚点，Aldridge 是机构级实施框架（SP3↔Engineering / SP9↔Policy / SP10/SP11↔Composition/Systemic）

**远期登记理由 + 不过度工程审查**：① regret-covariance 填补"策略行为是否偏离 intended"检测空白（Ghost 检测是持仓级物理漂移，regret-covariance 是行为级逻辑漂移，正交）；② crowding model 量化"分散失效"（39.2%→79.3%）；③ inner confidence 前馈维度（引入 LLM 决策时激活）；④ 4 层框架是架构命名零增量成本（现有 §3.5/§3.15/§3.16/§3.18 已隐含 4 层）。Phase 3+ 远期（regret-covariance + crowding 可在 Phase 2 实盘 6 月+ 后评估）。成本审查：regret-covariance 计算成本低（协方差矩阵 + 阈值比较）；crowding model 是 §3.16 avg_corr 的量化升级增量成本低；inner confidence 需 LLM 决策层**远期不适用**除非引入 LLM

**与既有登记的关系小结**：

| 维度 | §4.18 BOCD | §4.21 Transfer-Entropy | §4.28 Aldridge（本节） |
|---|---|---|---|
| 检测层 | 收益分布 changepoint | 网络拓扑前馈 | policy 行为 drift + crowding |
| 信号源 | 收益序列 run-length 后验 | 跨资产 transfer entropy + Hawkes | intended vs observed regret 协方差 + crowding 模型 |
| 触发语义 | "环境变了" | "系统性风险网络激活" | "策略行为偏离 intended" + "crowding 放大联合回撤" |
| 与 §3.5 Kill Switch 关系 | 概率 kill-switch 触发器 | 前馈预警（非直接触发） | 治理框架背书 + crowding 量化归因 |
| Phase | P3 远期 | P4 远期 | P3 远期（regret-covariance + crowding）/ 条件性（inner confidence 需 LLM） |

## 5. 上限定义（Ceiling）

### 5.1 系统上限
三层防御 + 一个 Kill Switch 执行通道：
- 1× `drawdown_tracker`（MOD-RK-011，监控告警，5/10/15%）
- 1× `capital_curve_manager`（MOD-POS-007，仓位节流，5/10/15%+ 四级上限）
- 1× `drawdown_controller`（MOD-POS-008，综合响应，VaR 5 级 + 策略 Soft/Hard + 黑天鹅）
- 1× Kill Switch 执行通道（`stop_loss.trigger_kill_switch` → `DefaultRiskValidator`）

### 5.2 演进路径
- **第一阶段（当前）**：三层各独立运行，`drawdown_controller.evaluate()` 手动编排（调用方依次喂入 drawdown_info / var_cvar / black_swan / strategy_pnls）
- **第二阶段**：事件驱动串联——`drawdown_tracker` EMERGENCY 事件自动触发 `drawdown_controller.evaluate()`，无需手动编排
- **第三阶段（远期）**：`capital_curve_manager` 的 expansion/contraction 与 `drawdown_controller` 的 recovery_factor 统一为单一恢复状态机（当前两者独立计算恢复，可能冲突）
- **第四阶段（远期演进方向登记，非已定路径）**：§4.6-§4.28 评估的学术研究方向，均暂缓或拒绝（详见 §6.8-§6.37 待裁定）。按族全量对齐（15 族）：

  | 族 | §4.x 替代方案 | §6.x 待裁定 | 优先级 | 定位 |
  |---|---|---|---|---|
  | **回撤度量族** | §4.6 Ulcer Index / §4.9 Pain Index / §4.14 CDaR | §6.8 / §6.19 | P2 | 浅回撤长时间补充度量 |
  | **统计检测族** | §4.8 CUSUM+Hawkes+Lee-Mykland / §4.18 BOCD | §6.10 / §6.27 | P3 | 阈值法的概率化升级 |
  | **时间维度族** | §4.7 Time-in-Drawdown Kill Switch | §6.9 | P3 | 浅回撤长时间 alpha 衰减 |
  | **连续控制族** | §4.12 MPC / §4.13 趋势跟踪防御层 | §6.17 / §6.18 | P4 | 离散阈值→连续 risk aversion |
  | **归因族** | §4.11 HRP 聚类 / §4.16 CED 线性归因 | §6.16 / §6.24 | P3-P4 | 系统性 vs 策略特定精细归因 |
  | **conformal 族** | §4.17 Schmitt RWC | §6.25 | P2 | VaR buffer conformal 校准 |
  | **路径依赖族** | §4.19 Signature Path Portfolio | — | P5+ | path-dependent 风险数学基础 |
  | **回撤工具族** | §4.20 Continuous Cash-Overlay | — | P3 | 模块化回撤过滤器 |
  | **网络级风险族** | §4.21 Transfer-Entropy+Hawkes / §4.22 Xiao Jian HFT herding / §4.23 Chen GWII herding | — | P3-P4 | 截面错位/网络渗流前馈 |
  | **厚尾传播族** | §4.24 Lévy-stable Drawdown Scaling / §4.27 Drawdown Beyond Brownian Motion | §6.23 Non-Gaussian Lookup Tables / §6.37 4 测度 keep-or-kill | P2-P3 | 非高斯回撤传播 + 4 测度校准 |
  | **恢复机制族** | — | §6.20 0.5% Recovery / §6.22 Data-Driven Restart / §6.26 Hysteresis / §6.29 Fanous 非对称去风险 | P0-P3 | 恢复路径优化 |
  | **Kill Switch 族** | — | §6.11 4层架构 / §6.14 A股新规 / §6.15 static 破产底线 / §6.31 Shelby fallback+VeritasChain | P0-P3 | Kill Switch 执行增强 |
  | **组合配置层** | §4.5 CPPI(拒绝) / §4.10 TradeShield(部分采纳) / §4.25 MFCCA / §4.26 RRP A股实证 | §6.30 CPPI+RB / §6.32 Put-Option Sleeve / §6.35 MFCCA / §6.36 RRP | P3-P5+ | 组合层远期候选（MFCCA 符号保留泛函 / RRP A 股 regime+GARCH 可独立提取） |
  | **理论背书** | — | §6.33 Non-concave VaR 赌博回本 / §6.34 Liu Leakage-Safe Residual-Stress | P3 | 设计决策理论支撑 |
  | **治理层族** | §4.28 Aldridge AI Governance | — | P3 | regret-covariance policy drift + crowding model 联合回撤定量 + 4 层治理框架架构背书 |

  这些方向不纳入已定演进路径，仅在重评条件满足时重新讨论——个人项目的演进以"实盘验证驱动"而非"学术前沿驱动"

### 5.3 为何是上限而非妥协
- 三层是机构风控的标准分层（监控 → 节流 → 熔断），[ai-trading-system 2026-03](https://github.com/ballales1984-wq/ai-trading-system/blob/main/app/risk/hardened_risk_engine.py) 的 RiskLevel 5 级（GREEN/YELLOW/ORANGE/RED/BLACK）+ CircuitBreaker + KillSwitch 三件套与本项目三层同构
- 再加层（如独立的"回撤预测器"）是过度工程——回撤本质是已发生事实的度量，预测回撤 = 预测收益，属于 alpha 层不是风控层
- Kill Switch 单一通道是安全设计——多通道会产生"哪个 Kill Switch 说了算"的仲裁问题

## 6. 待裁定（暂缓）

> 以下项目暂不施工，**非永久禁止**。每项附"重评条件"——满足时可重新讨论。
> **优先级**：P0=最小补丁（立即可做，低依赖）｜P1=短期（实盘 1-3 月后）｜P2=中期（实盘 6 月+）｜P3=远期（实盘 1 年+）｜P4=超远期（实盘 2 年+ 或依赖架构演进，如组合配置层独立模块化）｜P5/P5+=理论远期（仅登记防重新调研，无施工计划）

| 优先级 | 暂缓项 | 暂缓理由 | 重评条件 |
|---|---|---|---|
| P0 | §6.1 强制休息 5 天自动计时 | §2.5.2 要求 Level 4 触发后强制休息 5 个交易日，代码只有 `requires_manual_reset`（人工复位），无自动 5 天计时器 | 实盘运行后若人工复位过快导致二次回撤，补 5 天冷却计时器；当前人工复位=天然冷却 |
| P1 | §6.2 连续 5 天亏损 → 降仓 50% | §2.5.5 Kill Switch 表第 3 行，代码无独立实现 | 实盘验证连续亏损的判别力后决定；可用 `daily_auditor` 的日终 PnL 序列扩展 |
| P2 | §6.3 drawdown_controller 由 VaR 驱动改为回撤驱动 | 当前 L3 综合响应用 VaR 5 级（2/4/6%/10% CVaR）而非回撤 8/15/20/25%，与 §2.5.1 框架维度不同 | VaR 与回撤的相关性验证后决定；若 VaR 预警早于回撤则保持 VaR 驱动（前馈优于反馈） |
| P2 | §6.4 三层恢复状态机统一 | `capital_curve_manager` 的 contraction 解除（净值回峰值）与 `drawdown_controller` 的 recovery_factor（回补 50% 起步）是两套恢复逻辑，可能冲突 | 第二阶段事件驱动串联时若发现恢复冲突，统一为单一状态机 |
| P1 | §6.5 RiskOrchestrator 统一编排器 | §3.10 日度风控循环当前由调用方手动编排，无 orchestrator 串联三层，易遗漏喂入导致 C 层降级 | 实盘验证手动编排的遗漏频率后决定；若遗漏导致响应降级则建 `RiskOrchestrator` |
| P1 | §6.6 DrawdownStateMachine 持久化状态机 | §3.11/§3.15 当前 `DrawdownController` 无状态持久化，RECOVERY 可跳过阶梯直接回 NORMAL，存在"刚 CRISIS 立即满仓"风险；跨重启丢失"上一态"记忆 | 实盘运行后若发现恢复跳级导致二次回撤，建持久化状态机 + 转换守卫 |
| P1 | §6.7 回撤类型诊断 + 归因（统计性 vs 行为性 + 系统性 vs 策略特定）| §3.12/§3.16 当前无显式诊断步骤与归因流程，回撤触发后不区分方差亏损簇 vs AI 执行偏差、系统性 vs 策略特定 | 实盘运行后若 `daily_auditor` 归因检测到执行偏差与回撤同步，引入诊断分流 + 相关性归因 |
| P2 | §6.8 Ulcer Index / Pain Index 补充度量 | §4.6/§4.9 `drawdown_pct` 单点值不反映持续时间，浅回撤长时间可能比深回撤短时间更危险 | 实盘运行后分析"UI 高但 drawdown_pct 低"的回撤是否导致更大损失 |
| P3 | §6.9 Time-in-Drawdown Kill Switch | §4.7 `T_kill = MaxDDD_OOS × 1.5` 时间维度不可逆停机，捕获"浅回撤长时间"的 alpha 衰减 | 实盘 ≥1 年后，若某策略长期水下且 IC 衰减监控验证 alpha 衰减，引入 TiD 作为退役触发 |
| P3 | §6.10 CUSUM/Hawkes/Lee-Mykland 统计检测 | §4.8 统计异常检测替代阈值触发：CUSUM 检测均值漂移 + Hawkes 检测亏损聚集 + Lee-Mykland 区分跳跃 vs 漂移 | 实盘 ≥1 年后，若阈值法误触发频繁 / 连续亏损判别力不足 / 黑天鹅误报多，引入统计检测升级 §6.7 诊断 |
| P1 | §6.11 Kill Switch 4 层架构（L2/L3）+ 盘前 Ghost 接入 | §3.5.1 L2 broker 端硬止损 + L3 看门狗进程缺失（L1 平仓链路 `execute_kill_switch_liquidation` + Ghost 检测函数已施工 v1.39.0，commit 1d814359；盘前持仓核对调用未接入启动序列） | 实盘验证 miniQMT broker-side bracket 支持 + 盘前持仓核对检出 Ghost 频率后决定；剩余最小补丁：盘前接入 `detect_ghost_positions` + L3 看门狗独立进程（参考 §3.5 Unfireable 四属性 + VeritasChain 审计） |
| P0 | §6.12 盘前初始化 + 盘后持久化（§3.15/§3.18 配对）| §3.15 盘前加载 + §3.18 盘后保存是配对操作，当前无 `state_store` 持久化层，peak NAV/状态机态/recovery_step 重启即丢失；盘后无原子提交（`detect_ghost_positions` 函数已落码 v1.39.0，盘前接入随本项施工） | 最小补丁立即可做：① `capital_curve_manager.peak` 与 `drawdown_tracker` 窗口持久化到 DB；② 盘前调用 `detect_ghost_positions`；③ §3.18 盘后 `mark_persistable` 原子提交（DB 事务）。完整 `state_store` + DrawdownStateMachine 待 §6.6 |
| P1 | §6.13 回撤归因端到端流程 | §3.16 当前无"组合回撤 → 归因到策略/因子 → 分流响应"的自动化流程，仅靠人工判读 §3.12 矩阵 | 最小补丁：`daily_auditor` 已有 `AttributionBias`，回撤 WARNING 触发时自动调用并记入日志；完整归因（相关性矩阵 + 因子偏差 + regime 交叉）待 §6.7 |
| P0 | §6.14 A 股 2026 新规 Kill Switch 平仓适配 | §3.5.1 新规下持仓 >15 只需分批平仓（15 笔/秒），撤单受 15% 日撤单率约束。15 笔/秒分片平仓已施工（v1.39.0 `execute_kill_switch_liquidation`）；剩余：撤单率预检（超 12% 预警留 3% buffer）+ 全清超时告警（30 秒未全清人工介入） | 与 §6.11 一并施工剩余两项 |
| P1 | §6.15 Static 模式破产底线 Kill Switch | §4.10 trailing 25% Kill Switch 在大幅盈利后仍远高于初始本金，缺"绝对破产防护"；static 模式（initial × 0.85）作为第五类 Kill Switch 触发源 | 与 §6.11 一并施工：§3.5 触发条件表新增"组合净值 < 初始本金 × 0.85" |
| P3 | §6.16 六类风险失败机制 + HRP 聚类归因 | §3.16 扩展维度 + §4.11 HRP 聚类归因。López de Prado 2026 JAM 六类失败机制（statistical/factor/liquidity/model/governance/decision-infrastructure）提供统一归因框架；HRP 聚类树识别"部分系统性"策略簇，比 avg_corr 二元阈值更精细 | 25_multifactor IC 衰减监控 + 55_monitoring_review 系统健康均 production + 策略数 ≥8 个后，将六类框架 + HRP 聚类纳入 §6.7 归因流程作为扩展维度 |
| P4 | §6.17 MPC 连续风险厌恶调整 | §4.12 Nystrup/Boyd 2019 + DLP-SMPC 2026 用 MPC 根据已实现回撤连续调整 risk aversion γ(dd)，替代当前 §3.2 离散阈值 5/10/15%→80/50/30%。当前 recovery_factor 0.25→0.50→0.75 阶梯是其离散近似 | ① 实盘 ≥2 年稳定样本（HMM 参数估计可靠）；② alpha 层收益预测模块（HMM 或等价物）production（MPC 前馈需 μ/Σ 输入）；③ 业主对连续风控接受度验证后，引入 MPC 平滑化 risk aversion |
| P4 | §6.18 趋势跟踪回撤防御层 | §4.13 Noguer i Alonso & Al-Fallouji 2026-07 CVaR 框架提出"趋势跟踪在持续回撤中递增防御"前馈层。当前 Protocol 纯反馈（已亏才减），无前馈防御；A 股不能做空+无期权，只能"减仓/空仓"实现 | ① 实盘验证 A 股趋势信号在持续回撤中的防御有效性；② 与 34_regime_meta_allocator 裁定 regime vs 趋势跟踪职责边界（是否冗余）；③ 趋势信号来源模块确定（G09/G10）后，作为 §3.9 regime 之外第二前馈防御层 |
| P2 | §6.19 CDaR 回撤深度连续度量 | §4.14 Chekhlov/Uryasev CDaR = drawdown 序列的 CVaR，path-dependent coherent measure，LP 可解。当前 §3.8 用 drawdown_pct 单点值，CDaR 是尾部回撤均值；Man Numeric 2025 论证 CVaR 优于方差同样适用 CDaR 优于 MaxDD | 与 §4.6 UI / §4.9 PI 同步重评。实盘发现"浅回撤长时间"或"单点 drawdown_pct 不足以反映回撤痛苦"后，引入 CDaR 作为 ① 回撤深度补充度量（报告）+ ② 31_position_sizing 仓位优化的回撤约束。优先级高于 UI/PI（coherent + LP 可解） |
| P1 | §6.20 0.5% Recovery Protocol（单笔风险层面恢复） | [edgeflo 2026-03](https://www.edgeflo.com/blog/de-risk-after-drawdown) 实证：连续 2 笔亏损（或 2% 回撤）后，risk_per_trade 从 1% 降至 0.5%，单笔 3R 盈利回补 +1.5% 覆盖 2 笔 0.5% 亏损。当前 §3.4 recovery_factor 阶梯是**仓位上限**恢复，0.5% protocol 是**单笔风险**恢复——两者正交可叠加（recovery_factor=0.5 × risk_per_trade=0.5% → 实际风险 0.25% = 双保险） | 实盘运行后，若 recovery 期间单笔风险未同步收缩导致二次回撤，引入 `risk_per_trade` 随 `recovery_step` 联动下调（25%→0.5% / 50%→0.75% / 75%→1.0% / 100%→1.0%）。最小补丁：`position_sizing_engine` 读取 `drawdown_controller.recovery_factor` 联动调整 risk_per_trade |
| P2 | §6.21 Conformal Kelly drawdown dial | [arXiv:2608.01494](https://arxiv.org/html/2608.01494v1)（2026-08-02）：conformal 预测区间下行连续 miss 超历史率→缩减 leverage，开发窗口 MaxDD 27.7%→20.3%，rank-based p=0.024。**关键设计原则**：slow unweighted per-asset rolling quantile 优于 adaptive 方法（宽度稳定性 > 局部锐度）。当前 §3.4 recovery_factor 是回撤驱动阶梯，Conformal Kelly 是预测区间 miss 驱动自适应 leverage。施工骨架接口已冻结（§3.19） | ① conformal 预测层（[31_position_sizing](31_position_sizing.md) 或独立模块）production；② 实盘积累足够 conformal interval miss 样本校准"连续 miss 超历史率"阈值；③ 业主对"预测区间驱动 leverage"接受度验证。远期集成时用最简 per-asset rolling quantile，不追 locally adaptive 变体 |
| P3 | §6.22 Data-Driven Drawdown Restart | [arXiv:2303.02613](https://arxiv.org/pdf/2303.02613v1)（Hsieh 2023）：drawdown modulation 接近限值时带 restart 机制（数据驱动重置策略参数），有交易成本场景下仍优于无 restart。当前 §3.11 RECOVERY 阶梯是 restart 的离散实现，但未实现"数据驱动参数重置" | 实盘 ≥1 年后，若 RECOVERY 阶梯恢复后策略参数（ATR 倍数/止损位/仓位权重）仍沿用 pre-drawdown 配置导致二次回撤，引入 data-driven 参数重置：restart 时用最近 N 日数据重估 ATR/相关性矩阵/regime 参数 |
| P2 | §6.23 Non-Gaussian Drawdown Lookup Tables | [arXiv:2608.00127](https://arxiv.org/abs/2608.00127)（Landolfi 2026-07-31）：给定 Sharpe + 收益统计结构（skew/峰度/波动率聚集）生成 4 度量查表（MaxDD/最大损失/末尾负时间/最长恢复时间）。核心发现：① Gaussian 表在非正态下误警（四度量移动方向不同）；② 持续性下回撤"放大"是 `T^(H-1/2)` dispersion scaling 即 √T 校准失效，非路径几何本征危险。当前 §3.2 阈值（5/10/15%）+ §3.4 recovery_factor 阶梯是经验值，查表提供统计校准依据；警示 [36_var_es_monitoring](36_var_es_monitoring.md) §3.2 参数法 VaR 的 √T 缩放在持续性下失效。施工算法形态见 §4.27 | ① 实盘 ≥6 月 Sharpe 稳定估计（Rej-Bouchaud 框架需 SR 输入）；② 收益分布矩估计（skew/kurt/波动率聚集参数）稳定；③ 用查表校准当前 5/10/15% 阈值是否与"给定 Sharpe 的期望 MaxDD 分位"一致——若经验阈值过松（查表 MaxDD 95% 分位 < 5%）则收紧，过紧则放宽。MVP 不替换阈值，仅作校准参考 |
| P3 | §6.24 CED 线性因子归因 | [Goldberg & Mahmoud 2016](https://alexandria.unisg.ch/server/api/core/bitstreams/f53d98e4-3cfb-4517-8054-8287a2912bc8/content)（UC Berkeley + St. Gallen）：CED = maximum drawdown 分布的尾部均值，positive homogenous → Euler 定理线性归因到因子，convex → 可优化，对 serial correlation 敏感（回撤路径依赖特性）。当前 §3.16 用 avg_corr 启发式（>0.7 系统性 / <0.4 策略特定）做二元归因，CED 提供量化每个因子贡献度的严谨框架。与 §4.14 CDaR（组合优化）互补：CDaR 用于优化（LP），CED 用于归因（Euler 分解） | ① 策略数扩展到 ≥8 个后，avg_corr 无法区分"部分系统性"（簇内高相关+簇间低相关）时引入；② 实盘 ≥1 年后样本充足，CED 尾部估计稳定；③ 与 §4.14 CDaR / §4.11 HRP 聚类归因同步评估优先级与组合方式 |
| P2 | §6.25 Schmitt RWC Conformal Risk Control | [arXiv:2602.03903](https://arxiv.org/pdf/2602.03903)（Schmitt 2026-02, Oxford）：Regime-Weighted Conformal Risk Control——用指数时间衰减 + regime 相似性权重校准 VaR 安全缓冲，model-agnostic wrap 任意 quantile 预测器，weighted exchangeability 下有限样本覆盖保证。TWC 是 drift 下强默认，RWC 增加 regime 加权改善 regime-conditional 稳定性。与 §6.21 Conformal Kelly 正交互补（Kelly 管 leverage，RWC 管 VaR buffer），RWC 更直接作用于 §3.10 drawdown_controller 的 C 层 VaR 输入 | ① [36_var_es_monitoring](36_var_es_monitoring.md) conformal 预测层（quantile forecaster + calibration pipeline）production；② [34_regime_meta_allocator](34_regime_meta_allocator.md) regime 特征工程稳定（regime embedding 或可用相似性度量）；③ 实盘 ≥6 月 conformal calibration set 积累。最小集成路径：先 TWC（time-weighted，简单），验证稳定后再加 RWC（regime-weighted） |
| P0 | §6.26 回撤状态滞后-恢复双阈值（Hysteresis）算法 | §3.20 形式化：§3.11 状态机有升级触发条件但无降级恢复条件，临界态 thrashing 风险。§3.20 补齐 hysteresis 双阈值（恢复阈值 = 触发阈值 × 50%）+ min_hold 持续时间门控（5/10/20 交易日）+ 毕业准则（连续盈利日 + 10 笔期望 ≥ 0.3R + 合规率 ≥ 80%）。对齐 [37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md) §3.6（v1.0.3）设计模式。当前代码无 hysteresis 实现——`DrawdownController` 降级用与升级相同阈值 | 最小补丁（立即可做）：① `DrawdownController._evaluate_recovery` 增加半阈值判定（drawdown < 触发阈值 × 0.5 才降级）；② 增加 `min_hold` 计时器（状态进入后至少 N 日才可降级）；③ 毕业准则先做"连续 3 盈利日"单项（最简），完整 4 项准则待 §6.7 回撤类型诊断施工。完整 hysteresis 算法 + 毕业准则待 §6.6 DrawdownStateMachine 落地 |
| P3 | §6.27 BOCD 概率 Kill Switch | §4.18 Adams & MacKay 2007 BOCD 维护 run-length 后验 `P(r_t \| x_{1:t})`，输出 `P(changepoint) = P(r_t=0)` 连续概率。mathandmarkets 2026-02 + quantbeckman 2025-11 工程化方案：N-IG 共轭先验 + Student-t 似然（重尾适配）+ 双触发（P>0.8 硬停机 / P>0.5 持续 5 日减仓 50%）+ log-space 数值稳定 + pruning。是 §4.8 CUSUM/Hawkes/Lee-Mykland 的概率化演进——CUSUM 需指定 μ₀（选择困境）+ 二元阈值，BOCD 无需 μ₀ + 概率输出可分级响应。Dm-BOCD（arXiv:2302.04759）为鲁棒性升级子项 | ① 实盘 ≥1 年后，与 §6.10 CUSUM/Hawkes/Lee-Mykland 同步重评；② 若 §3.5 固定阈值 Kill Switch 误触发频繁或漏检结构断点，引入 BOCD 作为 §6.10 统计检测的概率化升级；③ 似然模型用 Student-t（ν=5 起步），hazard 用常数 1/λ（λ=252，期望 1 年变点一次）；④ 最小集成路径：先单策略试运行 BOCD（输出 P(changepoint) 仅供参考不触发），验证检测有效性后再接入双触发系统 |
| P3 | §6.28 波动率匹配阈值 + 历史涨幅动态防御仓位 | [guorn 2026-04](https://guorn.com/forum/post/p.200941.361906578502334)（A 股回撤择时实证，1992-2006 历史数据）：① **倒 U 形最优区间**——回撤阈值过浅→临界态 thrashing，过深→触发滞后错过防御窗口，存在与策略波动率匹配的最优区间；② **vol-matched stop**——止损阈值应与策略自身波动率匹配（高波动策略需更宽阈值否则 whipsaw，低波动策略需更紧阈值否则太晚），而非统一固定数值；③ **历史涨幅动态防御仓位**——DEFENSIVE 态仓位应根据 pre-drawdown 涨幅动态调整（涨幅 >100%→0.3 / >50%→0.5 / 否则 0.6），涨幅大则同幅度回撤更值得防守。当前 §3.2 固定 5/10/15% 无 vol-matching + §3.4 recovery_factor 固定 0.25→0.50→0.75 阶梯无历史涨幅感知。**与 §6.23 Landolfi 的关系**：Landolfi 是统计严谨校准（给定 Sharpe 的 MaxDD 分位查表），guorn 是经验 vol-matching + 涨幅感知——两者正交互补可叠加 | ① 实盘 ≥6 月积累策略年化波动率估计；② 用策略 vol 标定阈值：`threshold = k × annualized_vol`（k 待校准，参考 guorn 倒 U 形实证找最优 k）；③ 历史涨幅维度：recovery_factor 阶梯乘以 gain_factor（pre-drawdown 涨幅 >100%→0.6 / >50%→0.8 / 否则 1.0），涨幅大则恢复更保守。MVP 不改固定阈值，仅作远期校准参考 |
| P3 | §6.29 Fanous Recovery-Efficiency Protocol（非对称去风险路径依赖框架） | [arXiv:2605.09123](https://arxiv.org/abs/2605.09123)（Fanous 2026-05，"The Engineering of Skew"）：① **Recovery-Efficiency Protocol**——将回撤深度、水下时间、恢复负担缩减、反弹参与度四维度链接为 allocator-facing 报告准则，是 path-dependent 风险管理框架而非单一阈值；② **非对称去风险**（skew engineering）——降低有害下行参与度 > 降低上行参与度，控制 submergence 同时保留足够反弹参与度维持复利，与 §4.5 CPPI 的对称去风险（cushion 缩即整体缩）形成对比；③ **恢复负担非线性**——R = 1/(1-D) - 1（D=20%→R=25%，D=50%→R=100%），对称去风险在深回撤时牺牲过多上行导致恢复负担无法缩减；④ **ML/AI 定位**——conditional estimation / regime mapping / robustness testing / model-risk governance 工具而非市场预测，对齐本项目 AI 开发定位。当前 §3.4 recovery_factor 阶梯是对称缩减（0.25→0.50→0.75 全仓同步恢复），缺非对称维度。**与 §6.21 Conformal Kelly 的关系**：Kelly 是预测区间 miss 驱动 leverage 缩减（前馈），Fanous 是回撤路径驱动非对称缩减（反馈）——两者正交 | ① 实盘 ≥1 年后，若发现 recovery_factor 对称恢复导致"反弹参与不足→恢复期过长"（Fanous 框架的 recovery burden reduction 缺失）；② 最小集成：recovery_factor 阶梯拆分为 downside_factor × upside_factor（下行缩减更激进 / 上行恢复更快），如 DEFENSIVE 态 downside_factor=0.2 / upside_factor=0.6（当前两者均为 0.5）；③ rebound participation 指标纳入 §3.18 盘后持久化（recovery 期间 upside capture ratio vs downside capture ratio）。MVP 不改对称恢复，仅作远期校准参考 |
| P4 | §6.30 CPPI+风险预算两阶段法（组合配置层远期候选） | [东方证券 2026-04 "CPPI+风险预算"两阶段法](https://www.uufund.com/Report/Detail?id=AP202604121821139947)：第一阶段 CPPI 优化单资产夏普比（`E = m × (V − Floor)`），第二阶段风险预算（RB）配置，A 股 2006-2026 全样本年化 13.41%/波动 8.45%/MaxDD -10.91%/Sharpe 1.53/Calmar 1.23，优于等权和纯 RP。三层风险控制：CPPI 保本期 max 损失约束 + 动态回撤控制 + 风险预算分散。**对 §4.5 拒绝 CPPI 的诚实账本反证**——东方证券用三层架构兜底 gap risk（动态回撤控制层），裸 CPPI 的 gap risk 在三层协同下可控。**与 §4.5 拒绝理由的关系**：#1（cash-lock）仍成立（东方证券未解决 cushion=0 永久退出）；#2（A股 gap risk）被反证（三层兜底可控）；#3（无保本承诺）仍成立。**为何记为远期候选而非采纳**：① 定位正交——东方证券 CPPI 是组合配置层，本项目回撤 Protocol 是 sleeve 级风险节流（[30号 §2.2](30_multi_strategy_concurrency.md)）；② 架构耦合——三层一体化不可拆单层套用；③ 可解释性优先——CPPI m 值主观，5/10/15% 阈值更明确。**借鉴价值**：东方证券"动态回撤控制"层与本项目 §3.20 Hysteresis + §3.4 recovery_factor 同构（回撤越深仓位越轻的反馈式） | ① 仅当项目演进到"组合配置层"独立模块时（当前 sleeve 级 + firm 级两层架构不引入第三层）重新评估；② 借鉴"动态回撤控制"连续函数思路校准 §3.2 阈值（与 §6.28 vol-matched threshold 互补）；③ MVP 不引入 CPPI，§4.5 拒绝维持，本条仅作诚实账本记录防止"A 股 gap risk 使 CPPI 失效"以偏概全 |
| P2 | §6.31 Shelby AI Resilience Gap fallback 教义 + VeritasChain Flight Recorder 审计层 | [arXiv:2607.07359](https://arxiv.org/abs/2607.07359)（Shelby 2026-07-08，"The AI Resilience Gap"）AI Resilience Framework 五要素：① **依赖映射**；② **关键性-可替代性分层**；③ **impact tolerance 扩展到 AI 失效模式**（不只"系统宕多久"，还"AI 决策错误多久能容忍"）；④ **显式 fallback 教义**（AI 失效时降级运行模式：仅平仓不开新仓 / 仅用规则引擎不用模型 / 完全人工接管）；⑤ **provider 集中度管理**。**与本项目的关系**：本项目 100% AI 开发，§3.5 Kill Switch 是"AI 失效→全停"的硬通道，但缺"AI 失效→降级运行"的中间态——Shelby 的 fallback 教义填补"kill switch 触发后下一步做什么"的空白。**[VeritasChain 2026-01-20](https://veritaschain.org/blog/posts/2026-01-20-five-incidents-algorithmic-trading-flight-recorder/) Flight Recorder**（Two Sigma 22 个月未检出参数操纵 + SEC 罚 9000 万美元）提出 append-only + prev_hash 哈希链 + Ed25519 签名 + RFC 8785 JSON 规范化三层加密审计架构——本项目 §3.18 盘后持久化的 `daily_auditor.log_*` 当前是普通日志，远期应向 flight recorder 标准演进（防参数操纵不可篡改审计）。§3.5 Unfireable Safety Kernel 四属性（agent 地址空间外 + 唯一路径预执行强制 + 双重 fail-closed + Ed25519 证据日志）与 Novotny φ_∅ 微观结构触发器同归本条远期参考 | ① **fallback 教义**：实盘运行后，若 §3.5 Kill Switch 触发频率高于预期（说明全停代价过大），定义降级运行模式——Mode 1 仅平仓不开新仓（AI 信号可信度低时）/ Mode 2 仅用规则引擎（AI 模型层失效时）/ Mode 3 完全人工（极端场景）；② **VeritasChain 审计层**：实盘 ≥1 年后，若 `daily_auditor` 日志出现参数篡改/回填争议，引入 append-only 哈希链日志（每条 `log_*` 追加 prev_hash + Ed25519 签名），与 §3.5 COMPEL 四模式的"取证捕获"要求对齐；③ MVP 不引入 fallback 教义与 flight recorder，保持 kill switch = 全停的简单语义，本条仅作远期登记 |
| P5 | §6.32 Put-Option Sleeve（convex insurance 腿）+ Four-Axis Hedge Diagnostic —— arXiv:2607.00883 双 sleeve 框架补全 | [arXiv:2607.00883](https://arxiv.org/abs/2607.00883)（Noguer i Alonso & Al-Fallouji 2026-07-01）把尾部风险管理建模为**两 sleeve 分配问题**：① **long OTM put options**（convex insurance，jump 即时 reprice，但 IV>RV 持续导致 premium drag）；② **systematic trend-following overlay**（首震滞后因信号须穿零，但持续回撤中递增防御且无 premium）。§6.18 仅采纳 trend-following 腿（A 股适配为减仓/空仓），本条补 put-option 腿。**时间分离核心洞察**：put 防突发崩盘（jump）、trend 防持续回撤（grind），混合比单一 sleeve 降 terminal CVaR。**四轴 hedge-quality 诊断**（可移植贡献）：conditional convexity / tail-event reliability / non-stress carry / drawdown persistence——可评估任意 hedge 含 §6.18 减仓/空仓作"synthetic put"。**§6.18 事实订正**：§6.18 称"A 股不能做空+无期权"**事实不准**——A 股有 50ETF 期权（2015）、300ETF 期权（2019）、中证1000 ETF 期权（2022）、沪深300/中证1000 股指期权，组合层 put 对冲**可行**；约束：无个股期权、深 OTM 流动性薄。**为何 P5+ 远期**：MVP sleeve 级用减仓/空仓（§6.18 trend 腿）已足；put-option sleeve 是**组合层**尾部对冲 mandate，需期权交易基础设施 + premium budget + 滚动管理，与 §6.30 组合配置层远期同层级 | ① 仅当项目演进到"组合配置层"独立模块（同 §6.30 触发条件）；② 期权交易基础设施就绪（miniQMT 期权行情/下单支持验证）；③ premium budget 框架（年化 premium drag 预算占 NAV 比例，参考 IV-RV spread 历史均值）；④ **四轴诊断可先于 put sleeve 落地**——用作 §6.18 减仓/空仓 hedge 质量评估工具。MVP 不引入 put-option sleeve，§6.18 trend 腿维持，本条补全论文双 sleeve 框架诚实账本 |
| P3 | §6.33 Non-concave VaR 约束下"赌博回本"行为理论警示——floor 设计理论背书 | [arXiv:2608.05623](https://arxiv.org/abs/2608.05623)（Li, Lyu & Wei 2026-08-06）研究 VaR 约束下非凹目标函数（固定薪酬+期权激励）的动态风险管理（concavification + 分位数方法显式解）。**核心发现**：① VaR 约束在**地板较低**时改善下行保护+降低破产概率（约束迫使亏损早期即去风险，"防御性"）；② VaR 约束在**地板过高**时反而**增加破产概率**并诱发**"赌博回本"（gambling for resurrection）**——非凹目标函数下接近地板时选极高方差项目"赌一把回本"。**对本项目的价值**：§4.4 已拒绝"回撤进入 RiskSignal 参与下次决策"（"亏多了该更激进回本"的赌博倾向）——本论文提供**量化理论背书**。**对 §3.2 阈值设计的启示**：三层映射采用**保守低地板**（5% WARNING 远低于 8% 外层边界），正是论文验证的"低地板=防御性"区域；若 WARNING 提到 7%+ 接近外层边界（高地板）则诱发赌博回本。**与 §6.28 的关系**：§6.28 主张阈值与波动率匹配（高波动需更宽），本论文补充**上限约束**（过宽=高地板诱发赌博）——两者共同界定阈值可行区间。**定位 P3 理论背书非新算法**——防未来审查时"阈值过保守"误判而放宽阈值 | 无重评条件——理论背书条目，§3.2 阈值调整时须引用本条检查"新阈值是否进入高地板赌博回本区" |
| P3 | §6.34 Leakage-Safe Residual-Stress Signal——截面 PCA 残差压力前馈预警（vol 低态补充信号） | [Liu 2026-06 "Beyond Volatility: A Leakage-Safe Residual-Stress Signal for Drawdown Risk Monitoring"](https://www.mdpi.com/2227-9091/14/7/143)（MDPI Risks, Northwestern）：**截面 PCA 重构误差**构造 residual-stress 信号——① SPY + 11 行业 ETF 行业超额收益 PCA 估计 common component；② residual stress = 截面 out-of-sample 重构残差 RMS；③ **leakage-safe**：PCA mapping 仅用 t-1 及之前信息，stress score 在 t 计算，阈值用 rolling train-only 分位数（前移 1 日）——彻底消除 look-ahead bias；④ **核心实证**：realized volatility 是更强**独立**基准，residual stress **不能替代** vol 但**互补**——**vol 低但 residual stress 高**时未来 H=21 交易日 drawdown onset 概率显著更高；⑤ 增量价值在**条件风险分层**而非系统性更早触发。**对本项目的价值**：① 填补**截面错位前馈**维度空白（§3.5 Kill Switch 反馈 + §6.18 trend 单标的趋势 + §6.27 BOCD 单标的变点均无截面维度）；② **vol 低态补充价值高**（当前 VaR 5 级 + drawdown 阈值在低 vol 态均不易触发）；③ A 股适配申万一级 28 行业（比 11 sector ETF 更细）；④ leakage-safe 与 [15_data_feature_layer_spec](15_data_feature_layer_spec.md) bitemporal PIT 纪律天然对齐。**梯度定位**：CSAD/CSSD（轻量统计量）/ Liu（中等 PCA 残差）/ ORCA（重模型 127 谱特征）截面错位检测轻-中-重三档，Liu 居中；与 §6.10 CUSUM 正交（时间维度 vs 截面维度）。**消费方与数据源**：消费方=§3.5 herding/截面错位预警维度（三档梯度中档）；数据源=申万一级 28 行业日频指数（项目现有 SWindex 接口可适配，需新建 industry_pca_pipeline 模块）；计算频率=日频盘后（与 §3.18 同批）；触发逻辑=stress_score > rolling_q90 时输出 high_residual_stress 标志到 RiskSignal，§3.5 评估是否升级 herding 级别。**暂缓理由**：① 需申万行业指数实时管道（同 §4.23）；② vol 低态增量价值需 A 股验证（Liu 用美股，A 股行业轮动更快 lead-time 可能不同）；③ 前馈预警施工优先级低于 Kill Switch（风险优先 + §6.11 先施工） | ① 申万一级 28 行业指数实时数据管道建成（同 §4.23 重评条件）；② 实盘 ≥1 年后发现 §3.5 Kill Switch 事后触发滞后且 vol 低态漏检 drawdown onset；③ ORCA 过重 + CSAD/CSSD 过轻时 Liu 作中等复杂度替代；④ 最小路径：先用申万行业指数 offline backtest 验证 A 股 vol 低态 lead-time，再决定是否接入 §3.5 前馈预警维度。MVP 不接入，仅作远期登记 |
| P4 | §6.35 MFCCA 符号保留多重分形交叉相关组合分配——直接降低 drawdown 的组合配置层远期候选 | [arXiv:2608.04987](https://arxiv.org/abs/2608.04987) Kakinaka & Umeno 2026-08-05。风险泛函 = 带符号 MFCCA 波动函数 F(s,q)，**保留局部去趋势协方差符号**使同向/反向运动以相反符号贡献风险（MFDCCA 修正符号丢失对冲效果）。q=2 退化为均值-方差（MVO 严格泛化）。实证：每个收益水平降低 drawdown/VaR/ES **无损收益**。**与 30 号 §3.1 拒绝 MVO 的关系**：30 号拒绝 MVO 的权重敏感+样本不足，MFCCA 虽符号保留创新但仍需多尺度交叉相关估计（比 MVO 更重，与 O(N) 保证冲突）。**定位组合配置层**（同 §6.30 CPPI/§6.32 Put-Option Sleeve），与 sleeve 级回撤 Protocol 正交——Protocol 管"回撤后怎么减"，MFCCA 管"分配时怎么避免"。已由 [90号](90_methodology_open_questions.md) v1.3.0 risk parity 五级递进第五级登记，本条补 35 号 drawdown 维度交叉引用 + 诚实账本 | ① 项目演进到"组合配置层"独立模块（同 §6.30/§6.32 触发条件）；② 策略数 ≥8 个后多尺度交叉相关估计有意义；③ 实盘 ≥2 年多尺度收益数据积累；④ 最小集成路径：2 策略 × 3 尺度（日/周/月）offline backtest 验证 A 股符号保留增量价值。MVP 不引入，仅作远期登记 |
| P3 | §6.36 Robust Risk Parity (RRP) —— A 股实证的组合配置层远期候选 | [Li & Ye 2026（Finance Research Letters, DOI:10.1016/j.frl.2026.109586）](https://ideas.repec.org/a/eee/finlet/v92y2026ics1544612326001170.html)。传统风险平价框架内集成：① 自适应扰动机制；② 鲁棒协方差估计；③ **GARCH 波动率预测**；④ **市场状态识别**（regime identification）；⑤ 因子结构协方差。**A 股 2012-2024 全样本实证**对比 TRP/EW/GMV/MaxRet/ERP 五基线，收益/Sharpe/Calmar 均优、波动和 MaxDD 更低。**独特价值**：少有的 A 股全样本实证组合配置方法（含牛熊周期），且 regime 识别维度与 [34号 RegimeMetaAllocator](34_regime_meta_allocator.md) 天然对接。**与 §6.35 MFCCA 互补**：MFCCA 是理论前沿（符号保留），RRP 是工程化集成（A 股实证+regime）。**组件可独立提取**：RRP 的 regime+GARCH 组件可不引入完整 RRP 框架，独立评估接入 34 号 regime 输入增强 | ① 34号 RegimeMetaAllocator regime 特征工程稳定后，评估 GARCH 波动率预测作为 regime 输入增强（组件级集成，不需组合配置层）；② 项目演进到组合配置层时评估完整 RRP 框架（同 §6.30/§6.32/§6.35 触发条件）；③ **A 股实证优先级高于 MFCCA**——RRP 有 A 股 2012-2024 实证，MFCCA 无 A 股实证。MVP 不引入完整 RRP，但 regime+GARCH 组件级集成可中期评估 |
| P2 | §6.37 Drawdown Beyond Brownian Motion 4 测度查表 keep-or-kill | §4.27 新增 Landolfi [arXiv:2608.00127](https://arxiv.org/abs/2608.00127) 2026-07-31 回撤阈值非高斯校准算法——4 测度（MaxDD/MaxLoss/FinalNegTime/LongestRecovery）查表证明单一高斯表系统性误警（4 测度不同步移动），fBm 持续性表观放大是 √-time 校准失效（T^{H-1/2} 自相似色散标度）而非路径几何本征风险。与 §6.23（同一论文 v1.8.0 早期登记）的关系：§6.23 是概念登记，§4.27 是施工算法形态，本条是 keep-or-kill 裁定——是否在 Phase 3 用 4 测度非高斯表替换当前 §3.2 单一高斯 √-time 校准的 5/10/15% 经验阈值。与 §6.21 Conformal Kelly / §6.25 Schmitt RWC 同期 Phase 3 校准 | 裁定时机：Phase 3 校准阶段启动前。重评条件：① 实盘 ≥6 月 Sharpe 稳定估计；② 收益分布矩（skew/kurt/聚集/Hurst）估计稳定；③ 用查表校准当前 5/10/15% 阈值——若经验阈值与查表 95% 分位偏差 >20% 则替换为 4 测度非高斯表，偏差 <20% 则维持经验阈值仅作校准参考 |

## 7. 待定问题（讨论要点对齐状态）

> 以下来自 00_index §3 G16 讨论要点，逐项对齐后落入 §3 决策。

- [x] ① 四级阈值落地 → §3.2 三层映射表（代码 5/10/15% 更紧，§2.5.1 作生存边界）｜② 单策略 vs 组合分层 → §3.3｜③ 恢复机制 → §3.4 + §6.1 强制休息暂缓｜④ Kill Switch 触发与执行 → §3.5｜⑤ 日度熔断 → §3.6（4%/5%）｜⑥ 不可覆盖 → §3.7｜⑦ 净值口径 → §3.8 peak NAV｜⑧ regime 协同 → §3.9 乘性叠加
- [x] ⑨ 盘前初始化与跨重启恢复 → §3.15 4 阶段流程，§6.12 待裁定（P0 最小补丁：peak/窗口持久化 + 盘前 Ghost 调用）｜⑩ 回撤归因 → §3.16（相关性 + 因子 + regime 交叉），§6.13 待裁定｜⑪ A 股 2026 新规 → §3.5.1（每秒15笔/撤单率15%/50微秒），§6.14 待裁定（P0；15 笔/秒分片平仓已施工 v1.39.0）｜⑫ Pain Index 暂缓（§4.9）+ TradeShield static 部分采纳（§4.10，initial × 0.85 破产底线触发源），§6.15 待裁定｜⑬ 盘后持久化 → §3.18 5 阶段配对保存，与 §6.12 同步施工｜⑭ 六类失败机制 + HRP 聚类 → §3.16 扩展 + §4.11，§6.16 待裁定（P3）
- [x] ⑮ MPC 连续风险厌恶 → §4.12 评估（HMM ≥2 年样本 + alpha 层未成熟 + 杠杆不适用 + 可解释性），§6.17 待裁定（P4）｜⑯ 趋势跟踪防御层 → §4.13 评估（A 股有效性未验证 + regime 职责待定 + 信号源未定），§6.18 待裁定（P4）｜⑰ CDaR → §4.14 评估（与 UI/PI 同类择一 + α 无行业标准），§6.19 待裁定（P2，优先级高于 UI/PI）｜⑱ 多 agent 协作 → §4.15 **拒绝**（过度工程，仅借鉴思路，不设重评条件）
- [x] ⑲ CED 线性因子归因 → §4.16 评估（样本不足 + avg_corr 足够 + 优先级低于 CDaR），§6.24 待裁定（P3）｜⑳ Schmitt RWC → §4.17 评估（依赖 conformal 层 + regime 特征 + 校准样本），§6.25 待裁定（P2，先 TWC 后 RWC）｜㉑ Hysteresis 算法 → §3.20 形式化（半阈值 + min_hold 5/10/20 日 + 毕业准则），§6.26 待裁定（P0 最小补丁：半阈值 + min_hold + 连续 3 盈利日单项；完整 4 项准则待 §6.6）｜㉒ BOCD 概率 Kill Switch → §4.18 评估（O(t) pruning + 样本 ≥200 日 + 与固定阈值职责重叠），§6.27 待裁定（P3，先单策略试运行不触发）
- [ ] ㉓ 15% EMERGENCY 是否触发 Kill Switch——跨真源口径分裂（v1.38.0 通用规则 #11 盘点新发现，**需业主裁决**）→ 证据分裂三方：① drawdown_tracker.py 模块头注释"EMERGENCY 级触发 RK-17 Kill Switch" + battle_map BM-RC-03 触发条件"回撤>EMERGENCY" → 支持 **15% 触发**；② 30 号 §2.5.5 Kill Switch 表"回撤 > 25% → 清仓+强制休息 5 天+人工 review" + 本备忘 §3.11 状态机（CRISIS=drawdown>15% → 仓位上限 30%；KILL 需 drawdown>25% 或 CVaR>10% 或 BS-007）+ §3.2 三层映射表（Level 3=15% 停仓 30% 上限，Level 4=25% 清仓）→ 支持 **25% 触发**；③ 当前代码实际行为：15% EMERGENCY 仅发射 E-RK-03 告警事件，无 orchestrator 接线到 `trigger_kill_switch`（RiskOrchestrator 未建，§6.5），故 15% 实际只告警+仓位上限 30%，**不会自动全清**。裁决候选：a) 15% EMERGENCY 仅告警（对齐 §3.11/30 号，需改 drawdown_tracker 模块头注释 + battle_map BM-RC-03 口径）；b) 15% EMERGENCY 触发 Kill Switch 全清（对齐代码注释/battle_map，需改 §3.2/§3.11 + 30 号 §2.5.5，但 Level 3"仓位上限 30%"动作被架空）；c) 15% 触发"软 Kill"（禁新开仓+仅平仓不全清，需新增中间语义层）。本备忘倾向 a)（25% 是 §2.5.1 生存边界，15% 全清过于激进且使 Level 3 动作失效；EMERGENCY 告警+30% 上限已是足够强的早预警），但因涉及阈值语义+跨文档（30 号/battle_map/代码注释）口径统一，**不擅自裁决，留业主决定**。裁决后需同步修改：drawdown_tracker.py 模块头注释 / battle_map_09 BM-RC-03 / 30 号 §2.5.5 / 本备忘 §3.5 触发条件表（四处真源统一）

## 8. 引用

### 8.1 内部文档
- [00_index_trading_decision](00_index_trading_decision.md) §3 G16
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.5（四级框架已定，必先读）
- [31_position_sizing](31_position_sizing.md)（仓位算法，C3/C4/C5 约束承载 VaR/CVaR/波动率下调）
- [34_regime_meta_allocator](34_regime_meta_allocator.md)（regime Shrinkage，与本协议乘性叠加）
- [36_var_es_monitoring](36_var_es_monitoring.md)（G17，VaR/ES 喂入 drawdown_controller）
- [37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md)（G18，流动性危机是 Kill Switch 触发源之一）
- [battle_map_09_risk_control](../battle_map/battle_map_09_risk_control.md)（当前状态快照；BM-RC-03 Kill Switch 熔断 + BM-RC-04-B 回撤实时追踪环节）

### 8.2 代码模块（SSoT）
> 本表仅列核心 6 模块；全量已施工/未施工设施（含 Kill Switch 三实现域分离、支撑设施、注册表缺口）见 §2.4 已施工设施盘点。

| 模块 | ID | 路径 | 职责 |
|---|---|---|---|
| DrawdownTracker | MOD-RK-011 | `src/zephyr/risk/core/drawdown_tracker.py` | L1 监控告警 5/10/15% |
| CapitalCurveManager | MOD-POS-007 | `src/zephyr/position/core/capital_curve_manager.py` | L2 仓位节流 5/10/15%+ 四级上限 |
| DrawdownController | MOD-POS-008 | `src/zephyr/position/core/drawdown_controller.py` | L3 综合响应（VaR+策略+黑天鹅） |
| stop_loss | MOD-L04-001 | `src/zephyr/risk/stop_loss.py` | Kill Switch 执行入口 |
| DefaultRiskValidator | — | `src/zephyr/risk/implementations/default_risk_validator.py` | Kill Switch 状态管理 |
| DailyAuditor | MOD-RK-20 | `src/zephyr/risk/core/daily_auditor.py` | 日终检查（含 Kill Switch 状态） |

### 8.3 行业参考（2026-08 搜索）

> 多数条目已在正文对应章节内联引用（URL 随正文保留），此处按主题归并汇总；正文未内联的条目单列。

- **恢复/诊断基准**：[TradeZella Drawdown Management](https://www.tradezella.com/blog/drawdown-management)（三级协议 25%→50%→75%→full）・[CompleteTradersEdge Drawdown Protocol](https://completetradersedge.com/drawdown-protocol-traders/)（Green/Amber/Red 三级 + re-authorization）・[completetradersedge Advanced Drawdown Management](https://completetradersedge.com/advanced-drawdown-management/)（统计性 vs 行为性 5 问诊断）・[BloFin Handling Drawdowns](https://blofin.com/en/academy/education/handling-drawdowns)（三阶段恢复 + 毕业准则，§3.20 依据）・[JournalPlus Trading After a Drawdown](https://journalplus.co/learn/guides/trading-after-a-drawdown-guide/)（4 阶段框架）・[fazencapital Recovery Math Guide](https://fazencapital.com/learn/en/trading-drawdown-recovery-math-methods-guide)（30 天 reset protocol）・[edgeflo De-Risk After Drawdown](https://www.edgeflo.com/blog/de-risk-after-drawdown)（0.5% Recovery Protocol，§6.20 依据）
- **Kill Switch 行业印证**：[algotradingdesk Kill Switch in HFT](https://algotradingdesk.com/kill-switch-mechanisms-hft-risk-control/)（Knight Capital 案例 + SEC Rule 15c3-5）・[Punch Kill Switch](https://builderslab.punch.trade/help/articles/1440242-use-kill-switch-to-lock-trading-on-punch-desktop)（"cannot turn it off early"）・[go-trader #25](https://github.com/richkuo/go-trader/issues/25)（manual reset + audit log）・[ai-trading-system hardened_risk_engine](https://github.com/ballales1984-wq/ai-trading-system/blob/main/app/risk/hardened_risk_engine.py)（RiskLevel 5 级三件套同构）・[nexusfi Automated Risk Controls](https://nexusfi.com/a/automation/automated-risk-controls)（5 态状态机 + 取最严）・[nexusfi Emergency Protocols](https://nexusfi.com/a/automation/automated-trading-emergency-protocols)（4 层架构 + Ghost Position + @Breukelen CME 拒单案例）
- **回撤度量/数学**：[algostrategyanalyzer Drawdown Guide](https://algostrategyanalyzer.com/en/blog/drawdown-trading-guide/)（DD=(Peak-Trough)/Peak）・[nexusfi Drawdown Recovery Mathematics](https://nexusfi.com/a/risk-management/drawdown-recovery-mathematics)（Loss/(1-Loss) 恢复表，§2.1 直接依据）・[tradingwyckoff Drawdown Guide](https://www.tradingwyckoff.com/en/algorithmic-trading/drawdown-trading-guide/)（UI/PI/Kill Switch，§4.9 依据）・[IR-Tracker Drawdown Management](https://www.ir-tracker.com/en/columns/advanced-strategy/drawdown-management)（Ulcer Index，§4.6 依据）・[Rej, Seager & Bouchaud 2017](https://arxiv.org/abs/1707.01457)（深度∝Sharpe 反比、持续∝Sharpe² 反比）
- **统计检测/前馈**：[Tugbars/Finance-Kill-Switch](https://github.com/Tugbars/Finance-Kill-Switch)（CUSUM+Hawkes+Lee-Mykland，§4.8 依据）・[Adams & MacKay BOCD 2007](https://arxiv.org/abs/0710.3742)（§4.18 原始论文）・[mathandmarkets CUSUM/Bayes](https://mathandmarkets.com/p/detecting-decay-in-real-time-when)（k=0.5σ/h=4σ 调参，§4.18 参考）・[quantbeckman Switch-Off](https://www.quantbeckman.com/p/with-code-switch-off-bayesian-online)（probabilistic kill switch 双触发，§4.18 依据）・[invistaja Time in Drawdown](https://invistaja.app.br/time-in-drawdown-algotrading/)（TiD `T_kill = MaxDDD_OOS × 1.5`，§4.7 依据）
- **CPPI/组合配置/归因**：[MetricGate CPPI](https://metricgate.com/docs/constant-proportion-portfolio-insurance/)（cash-lock 风险，§4.5 依据）・[López de Prado & Fabozzi JAM 2026](https://quantresearch.org/Publications.htm)（六类风险失败机制，§3.16 依据）・[marketmaker.cc HRP vs Markowitz](https://marketmaker.cc/en/research/)（4800 次实验，§4.11 依据）・[Uryasev & Ding Drawdown Beta](https://uryasev.ams.stonybrook.edu/wp-content/uploads/2021/10/Drawdown_Portfolio_Optimization_Problems_and_Drawdown_Betas.pdf)（ERoD=CDaR 优化等价，§4.14 依据）・[MetricGate CDaR](https://metricgate.com/docs/conditional-drawdown-at-risk/)（coherent 论证）・[Man Numeric CVaR 2025-07](https://www.man.com/man-numeric-cvar-insights)（CVaR 优于方差）・[Goldberg & Mahmoud CED 2016](https://alexandria.unisg.ch/server/api/core/bitstreams/f53d98e4-3cfb-4517-8054-8287a2912bc8/content)（Euler 线性归因，§4.16 依据）・[arxiv 1404.7493v3](https://arxiv.org/pdf/1404.7493v3)（CED LP 算法）・[internQuant/conditional-drawdown](https://github.com/internQuant/conditional-drawdown)（CED Python 实现）
- **MPC/趋势跟踪/多 agent**：[Nystrup/Boyd 2019 MPC Drawdown Control](https://backend.orbit.dtu.dk/ws/files/149812772/Multi_Period_Portfolio_Selection_with_Drawdown_Control.pdf)（γ(dd)，§4.12 依据）・[arXiv:2604.00415 DLP-SMPC](https://arxiv.org/html/2604.00415v1)（TSLA MaxDD 12.17% vs 73.63%）・[arXiv:2607.00883 Puts + Trend](https://arxiv.org/html/2607.00883v1)（时间分离 + 四轴诊断，§4.13/§6.18/§6.32 依据）・[philippdubach Long Volatility Premium](https://philippdubach.com/posts/long-volatility-premium/)（AQR 实证，§4.13 支撑）・[arXiv:2605.25311 RMATS](https://arxiv.org/abs/2605.25311)（§4.15 拒绝依据）・[arXiv:2510.10807 MARCD](https://arxiv.org/html/2510.10807v3)（§4.15 拒绝依据）・[arXiv:2605.16895 The Alpha Illusion](https://arxiv.org/html/2605.16895v1)（LLM alpha 不可作部署证据，§4.15 支撑）
- **conformal/非高斯/恢复远期**：[arXiv:2303.02613 Drawdown Restart](https://arxiv.org/abs/2303.02613)（Hsieh 2023，§3.11 RECOVERY 理论支撑）・[arXiv:2608.01494 Conformal Kelly](https://arxiv.org/html/2608.01494v1)（MaxDD 27.7%→20.3%，§6.21 依据）・[arXiv:2608.00127 Beyond Brownian Motion](https://arxiv.org/abs/2608.00127)（Landolfi 4 测度查表，§6.23/§4.27 依据）・[arXiv:2602.03903 Schmitt RWC](https://arxiv.org/pdf/2602.03903)（§4.17/§6.25 依据）・[arXiv:2608.04305 RaQL](https://arxiv.org/abs/2608.04305)（归 §4.15 借鉴范围）
- **Hysteresis/状态机印证**：[r1000-quant-engine Phase 6a](https://github.com/wscha231/r1000-quant-engine/blob/master/PHASE_ROADMAP.md)（−8/−15/−25% + 3% 回升 hysteresis）・[dredyson State Machines](https://dredyson.com/the-hidden-truth-about-state-machines-in-algorithmic-trading-systems-)（0.5 std gap 减 70% 假转换）・[Actura GACR Whitepaper](https://github.com/othnielObasi/actura-gacr-agent/blob/main/WHITEPAPER.md)（>6% 锁 EXTREME_DEFENSIVE + 8 cycles cooldown）——均 §3.20 印证
- **双模式/熔断/风控实战**：[PropGuard TradeShield](https://github.com/youcefbibo53/PropGuard-Trailing-Equity-Armor/)（static+trailing 双模式，§4.10 依据）・[orstac Avoid Over-Leveraging](https://orstac.com/ways-to-avoid-over-leveraging-in-trading-3/)（soft/hard circuit breaker + correlation-aware，§3.16 依据）・[csdn 2026 量化新规实盘重构](https://blog.csdn.net/syp1110/article/details/163276625)（每秒15笔/撤单率15%/50微秒，§3.5.1 依据）
- **监管**：[Bank of England AI Contingency Planning](https://hotminute.co.uk/2026/07/05/kill-switches-for-the-stock-market-inside-the-bank-of-englands-ai-contingency-planning/)（Breeden Sintra，§3.5 ①③ 依据）・[SEBI Algorithmic Trading Framework 2026](https://clearyourexam.com/current-affairs/sebi-new-framework-algorithmic-trading-enhanced-corporate-governance)（物理隔离强制，§3.5 ② 依据）・[guorn 回撤择时](https://guorn.com/forum/post/p.200941.361906578502334)（倒 U 形 + vol-matched stop，§6.28 依据）
- **正文未内联引用条目**：[systemtrade.blog Adaptive Drawdown Recovery](https://systemtrade.blog/posts/adaptive_drawdown_recovery)（3 段软止损状态机 + 阶梯 lot_multiplier）・[arxiv 2511.13251 Sharpe-Driven A-Share Portfolio](https://arxiv.org/pdf/2511.13251)（A 股实证：>2%→80% cap / 4-6%→40% cap / >6%→0+1 天冷却，比本项目更紧）・[csdn 期货量化风控实战](https://blog.csdn.net/lisiccwss/article/details/160660741)（三层联动 + 状态机防自动恢复）・[marketclutch Circuit Breakers](https://marketclutch.com/structural-safeguards-navigating-circuit-breakers-in-algorithmic-trading/)（LULD + MWCB 三级 7/13/20%）・[nadcab Trading Bot Risk Management](https://www.nadcab.com/blog/trading-bot-risk-management-stop-loss-position-sizing-drawdown-control)（Kill Switch 独立多层实现）・[signalbots AI Signals as Risk Safety Net](https://signalbots.ai/blog/forex-risk-management-with-ai-signals)（恢复非对称数学表，§2.1/§3.6 印证）・[Helios 9 Ways to Reduce Drawdowns](https://heliosdriven.com/helios-insights/reduce-drawdowns-portfolios)（系统化回撤控制框架，§3.16 归因印证）・[arXiv:2604.09060 AEGIS Volatility-Gated Momentum](https://trendsandbreakouts.com/volatility-gated-momentum-aegis-framework)（20 年 CAGR 15.41%/MaxDD 28.89%，§3.16 avg_corr 呼应）

---

## 9. 施工记录

### v1.39.0（2026-08-13，session AI-DRWD-001）

✅ 已施工（模块=drawdown_controller/kill_switch，commit 1d814359，81 测试全绿 0 失败连续 2 轮，新增 22 例；长清单审查 PASS，已 merge）——Kill Switch 平仓链路 `execute_kill_switch_liquidation`（scope 三态 + 15 笔/秒分片 ⌈N/15⌉ 批 + 逐笔异常汇总）+ Ghost 双类型检测（`strategy_closed_but_broker_holds` / `kill_switch_closed_but_position_remains`，同标的去重）+ `reset_kill_switch` 增 `holdings_verified_zero` 校验。接口级摘要见 §3.5 执行路径块 / §3.5.1 L1 层 / §2.4④；施工文件：`src/zephyr/risk/stop_loss.py` + `src/zephyr/risk/implementations/default_risk_validator.py` + `tests/risk/test_l04_risk_management.py`。

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | G16 讨论要点占位 |
| 2026-08-10 | 1.0.0–1.5.0 | 骨架→active 定稿：三层分离裁决（代码 5/10/15% 内层早预警 + §2.5.1 的 8/15/20/25% 外层生存边界）+ §3.10-§3.18 施工流程（日度循环/状态机/诊断/盘中循环/复位/盘前初始化/归因/盘后持久化，6 流程闭环）+ §3.5.1 4 层架构 + A 股新规拆单 + §4.1-§4.11 + §6.1-§6.16（优先级列） | 框架与代码阈值分裂裁决；持久化与恢复配对；系统启动与归因环节补齐（迭代细节已折叠，内容以对应章节为准） |
| 2026-08-10 | 1.6.0–1.11.0 | §3.19 审查结论 + 过度工程红线 4 条 + §3.9 乘性 vs 加性 + §4.12-§4.18 远期评估（MPC/趋势跟踪/CDaR/多 agent 拒绝/CED/RWC/BOCD）+ §3.20 Hysteresis 形式化（半阈值+min_hold+毕业准则）+ Conformal Kelly 施工骨架 + §6.17-§6.27 | 6 流程闭环无缺失独立环节，横切算法作远期登记；状态机缺降级恢复条件补齐（迭代细节已折叠） |
| 2026-08-10 | 1.12.0–1.18.0 | Triple Penance Rule（恢复时间 2-3x）+ §6.28 vol-matched 阈值（guorn）+ §4.19 Signature Path Portfolio + §3.21 A 股量化私募实证背书 + §3.10-§3.20 标题级别统一 + Conformal Kelly OOS 诚实账本/RWC v3/BR-iHMM + §6.29 Fanous 非对称去风险 | min_hold 经验倍数依据；风险优先原则实盘级验证（迭代细节已折叠） |
| 2026-08-10 | 1.19.0–1.27.0 | §4.5 CPPI 东方证券反证 + §6.30 + §3.5 全球监管背书（BoE Sintra/FPC + SEBI + Bailey/Wolters Kluwer/FCA + FSB 顶层锚点）+ COMPEL 四模式 + VeritasChain + ORCA/Weng herding 替代 + Unfireable Safety Kernel + Novotny 相图 + Li et al. circuit breaker + §4.20 Cash-Overlay + §6.31-§6.33 | 监管合规验证 + kill switch/herding 前沿登记（迭代细节已折叠） |
| 2026-08-10 | 1.28.0–1.30.6 | entry_var 持久化补全（§3.10/§3.15/§3.18）+ §3.16 风险恶化归因分支 + §3.14 三级分级保护 + 伪代码审计 9 项缺口修复 + 数据交接链 7 条 + 二次深化 8 条修复（复位三字段/集合竞价减仓/表码一致/复位循环守卫 20日3次·冷却3日·永久5次） | 伪代码审计→流程交接链级审查，跨函数数据传递断裂全部修复（迭代细节已折叠） |
| 2026-08-10 | 1.31.0–1.37.0 | 35号↔36号跨文档交接链 E1-E8 修复（var_cvar 产出方统一/var_breach_state 传入/双阶段标记/持久化顺序/双 RECOVERY ×0.9）+ §6.34 Liu Residual-Stress + §5.2 Stage 4 全量对齐（15 族）+ §4.25-§4.28 + §6.35-§6.37 | 跨文档协同闭合；组合配置层/治理层远期登记（迭代细节已折叠） |
| 2026-08-12 | 1.38.0 | 通用规则 #11 已施工设施盘点（§2.4：三层模块 + Kill Switch 三实现域分离"3+1" + 支撑设施 + 未施工清单 + 注册表缺口）+ §3.5 执行路径口径精确化 + §7 ㉓ 15% EMERGENCY 开放问题 + §3.6 第三口径附注 + §3.5 系统故障触发行 | 基础设施全量扫描；口径矛盾显式标注不擅自裁决 |
| 2026-08-12 | 1.38.1 | 作战地图全覆盖补丁：§3.5.2 否决执行引擎（BM-RC-10/10-A）+ §3.6 周 5%/月 10% 两级限额+强制复盘（BM-RC-05-C）+ §3.14 多域通知 Saga 裁定（BM-RC-03-C） | 作战地图 12 环节闭合施工（本篇 4 环节） |
| 2026-08-12 | 1.38.2 | 作战地图环节映射补强（BM-POS-05 / BM-RC-03-A / BM-RC-05 / BM-RC-05-B） | §3.7/§3.20 末尾补映射块，环节级可追溯 |
| 2026-08-13 | 1.39.0 | AI-DRWD-001 施工：§3.5 口径修正 + §6.11 两项落码——execute_kill_switch_liquidation（15 笔/秒分片）+ detect_ghost_positions 双类型 + reset_kill_switch 确认校验；81 测试全绿，commit 1d814359 | Kill Switch 平仓/撤单执行链路与 Ghost 检测从伪代码落码，§3.5 执行路径全 ✅ |
| 2026-08-14 | 1.39.1 | 压缩精简：已施工内容折叠，零信息丢失审查通过（AI-DOCS-001） | AI-DOCS-001 文档压缩：v1.39.0 已施工内容（Kill Switch 平仓链路 + Ghost 检测）折叠为 ✅ 已施工标记 + 接口级摘要；§9 施工记录折叠；过程性叙述/调试记录/迭代版本细节/对标散文删除（表格保留）；阈值表/Kill Switch 触发契约/36 号·37 号联动契约/§3.13 等待做项/开放问题 ㉓/全部数值参数逐项保留；章节标题与编号一字未动 |
| 2026-08-15 | 1.39.2 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-05） | §3.5 ⚠️15% EMERGENCY 矛盾块压缩（证据三方/裁决候选全录留 §7 ㉓，正文只留矛盾点+当前行为+倾向+指针）；§3.4 毕业准则块去来源重复（准则数值保留，来源/理由真源 §3.20）；§9 v1.39.0 施工记录折叠为 ✅ 一段（接口摘要已在 §3.5/§3.5.1/§2.4④）；§1 状态行瘦身。全篇扫描无其他可压缩点——8/15/20/25 与 5/10/15 阈值、VaR 2/4/6%+CVaR 10%、degraded 5 条件、撤单率 12%/15%、复位 20日3次/冷却3日/永久5次、BM-XXX/开放问题/跨文档链接逐项零丢失 |
| 2026-08-17 | 1.39.3 | D9 文档漂移对账（AI-GOVB-001 #105）：§2.4④ RiskOrchestrator「无代码」→已建（落地名 RiskLayerOrchestrator，MOD-L06-001，RWIRE-001 #ARCH-100）；§3.5.1 L1 行补生产接线对账（编排层已调用 stop_loss 两入口，trading_session 注入缝默认 None 未实例化）；stop_loss.py [CONSUMERS] 补 MOD-L06-001 | RWIRE-001 完工后文档措辞与代码现实对账；仅措辞同步，零语义变更 |

---

## 附录：数据资产消费登记（63 号审查批次 A，2026-08-20 登记）

> 来源：[63_data_utilization_audit](63_data_utilization_audit.md) §6.2 批次 A / §7.1 第一波——消费层文档覆盖缺口施工（风险/回撤模块优先）。登记口径：每表 3-5 行（表名/内容/潜在消费场景/当前状态）；按收缩方案合并为本节表格汇总。当前状态统一为**未消费登记**（unconsumed registration）：数据已落库、代码层或有引用，但本消费方文档尚未将其作为显式数据源描述；后续实际消费接线后，按 63 号 §7.0.1 六字段模板（业务含义/关键字段/消费频率/下游逻辑/依赖上游/实证支撑）改写为正文小节并更新状态。引用计数为 2026-08-20 工作区复扫（src/zephyr *.py，词边界匹配）；63 号 §6.2 表内"v0.2.0 估值"计数不可复现（63 号 §2.2 声明），以本登记与 `scripts/audit_data_utilization.ps1` 快照为准。

| 表名 | 内容 | 潜在消费场景 | 当前状态 |
|---|---|---|---|
| `restricted_shares`（限售解禁明细，[schemas/categories/](../../../../schemas/categories/) DDL 在册） | 限售股存量与解禁明细（股东/解禁数量/成本/解禁日期） | 解禁压力减仓硬规则输入：解禁量/流通股本分层（<50% 有限影响 / 50-200% 中等 / >200% 极端，Alphanume 2026-03 四指标口径）+ 吸收天数（解禁量/日均成交量，>50 天=结构性压力）触发减仓档；华泰 2026-06 港股实证 Q1 高压组风险规避胜率 72.5% | **未消费登记**（2026-08-20 实证：src/zephyr 引用 10 次，代码活跃；消费语义未落本文档） |
| `share_unlock`（解禁日历） | 个股未来解禁时间表（解禁日/规模/股东类型） | 解禁前 30 日减仓提示（63 号批次 A 既定硬规则，Time Criticality 高）：盘前扫描持仓股解禁日历，T-30 日起入观察名单、T-7 日起按分层降仓；与 §3.14 三级分级保护联动 | **未消费登记**（2026-08-20 实证：src/zephyr 引用 8 次，代码活跃；消费语义未落本文档） |