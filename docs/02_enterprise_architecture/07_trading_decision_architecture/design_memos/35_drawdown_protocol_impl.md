---
ttl: permanent
doc_type: architecture_view
title: 回撤 Protocol 落地 spec
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.38.0"
date: 2026-08-12
topic: drawdown_protocol_impl
scope: 07_trading_decision_architecture
---

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
| 对标 | ARKA / LedgerMind / Sina 量化FOF / tradingwyckoff（§2.5 已引）；2026-08 行业搜索补：TradeZella 三级协议 / algostrategyanalyzer Kill Switch / go-trader portfolio kill switch / BloFin 分阶段恢复 / JournalPlus 4 阶段恢复 / r1000-quant-engine hysteresis / dredyson 状态机 hysteresis；2026-08 学术研究补：Nystrup/Boyd MPC drawdown control / Noguer CVaR trend following / RMATS multi-agent / Uryasev CDaR / DLP-SMPC / MARCD / Man Numeric CVaR / Schmitt RWC Conformal Risk Control / CVaR Risk-Aware Q-Learning / Conformal OCE Risk Training |
| 正交性 | ✅ 与 regime 正交（drawdown 是账户级，regime 是市场级） |
| 优先级 | P2（与 G12 并行） |
| 状态 | ✅ 已定稿 v1.38.0（框架 §2.5 + 落地三层映射 + 阈值裁决 + 6 流程闭环施工 + 状态机 + Ghost Position 兜底 + A 股新规适配 + 回撤归因 + 盘后持久化 + 六类风险失败机制扩展归因 + HRP 聚类归因暂缓 + MPC/趋势跟踪/CDaR/多 agent 远期演进登记 + Conformal Kelly drawdown dial/Data-Driven Restart/Non-Gaussian Drawdown Lookup Tables 远期演进登记 + CED 线性因子归因暂缓 + 0.5% Recovery Protocol 待裁定 + 过度工程审查 + 回撤状态滞后-恢复双阈值 Hysteresis 形式化 + Schmitt RWC Conformal Risk Control 远期演进登记 + 分阶段恢复毕业准则 + Conformal Kelly drawdown dial 施工骨架接口冻结 + BOCD 概率 Kill Switch 暂缓（§4.18 Adams-MacKay 2007 + mathandmarkets 2026-02 + quantbeckman 2025-11，run-length 后验概率输出替代 CUSUM 二元阈值，§4.8 概率化演进）+ 波动率匹配阈值+历史涨幅动态防御仓位远期演进登记（§3.19 guorn 2026-04 倒U形最优区间+vol-matched stop，填补"为何 5/10/15%"推理缺口）+ Signature-based Path Portfolio 路径签名组合优化远期登记（§4.19 arXiv:2608.02355 Noguer i Alonso 2026-08-03 signature 作路径通用坐标+Lemahieu & Boudt kernel trick 线性近似 expected drawdowns+VAE 生成路径集成，path-dependent 风险三层递进闭环）+ 2026-08 A股量化私募集体回撤实证背书（§3.21 幻方/稳博等百亿量化7月回撤20-46%四根因——风格暴露集中/分散失效/止损踩踏/端到端AI逆向承接——映射firm层硬上限/§3.16相关性归因/§3.20 min_hold/§3.5 Kill Switch不可覆盖五项设计决策，风险优先原则实盘级验证 + §3.10-§3.20 标题级别统一为 ### 格式修复 + §3.17 "5 流程闭环"→"6 流程闭环"笔误修复 + §3.19 远期演进表 v1.18.0 四项更新：Conformal Kelly OOS 诚实账本+Schmitt RWC v3+BR-iHMM regime 依赖+Fanous Recovery-Efficiency Protocol 非对称去风险路径依赖框架）+ v1.19.0 §4.5 CPPI 诚实账本补东方证券 2026-04 A股实证反证（CPPI+RB 两阶段法 2006-2026 年化13.41%/Sharpe 1.53 优于等权/RP，三层架构兜底 gap risk 反证拒绝理由#2，但定位正交+无保本承诺+架构耦合+可解释性优先仍不采纳，§6.30 待裁定登记组合配置层远期候选）+ v1.20.0 §3.5 补 2026 全球监管 Kill Switch 背书（BoE Sintra Forum 2026-06-30 Breeden herding 风险+BIS/Bundesbank 联合压力模拟+SEBI 2026-05 物理隔离+事后审计三维度，验证 4 层防御架构/独立 stop_loss/daily_auditor 审计清单的监管合规性）+ v1.21.0 §3.5 补 BoE FPC circuit breaker vs kill switch 语义区分+Q3 2026 DP 时间线+deterministic output gating+bare-metal recovery 三原则验证+GeomHerd arXiv:2605.11645 herding 检测滞后 272 步+AI Systemic Risk arXiv:2604.03272 18-54% 尾部放大超线性增长定量背书）+ v1.22.0 §3.5 补 COMPEL Framework Kill-Switch 四模式架构参考（Hard-stop/Graceful-halt/Rollback/Scoped-disable 映射，本项目三模式已覆盖+Rollback 待 §6.11）+VeritasChain Flight Recorder 审计层（append-only 哈希链+Ed25519 签名，§6.31 远期）+§3.5 ⑥ Bailey 2026-07-23 "证明而非声称"+Wolters Kluwer 72% 银行 kill switch 未就绪+FCA Mills Review 算法决策可追溯+§3.5 ⑦ ORCA arXiv:2604.17251 谱特征 herding 可施工替代（24 ETF+127 谱特征+RF walk-forward Sharpe 1.13/MaxDD -7.5%）+Weng arXiv:2607.27063 A股 Johnson S_U 尾部 herding 指标+§4.18 Dm-BOCD arXiv:2302.04759 鲁棒性升级路径（diffusion score matching 比 β-BOCD 快 10x+对离群点鲁棒）+§6.31 Shelby arXiv:2607.07359 AI Resilience Gap fallback 教义（5 要素：依赖映射/关键性分层/impact tolerance/fallback 教义/provider 集中度）+ v1.23.0 §6.32 Put-Option Sleeve（convex insurance 腿）+ Four-Axis Hedge Diagnostic 补全 arXiv:2607.00883 双 sleeve 框架（§6.18 trend 腿维持，本条补 put-option 腿+四轴诊断 conditional convexity/tail-event reliability/non-stress carry/drawdown persistence+时间分离洞察 put 防 jump/trend 防 grind 互补+§6.18"A 股无期权"事实订正：A 股有 50ETF/300ETF/中证1000 ETF 期权+股指期权，组合层 put 对冲可行）+ v1.24.0 §3.5 补 Unfireable Safety Kernel arXiv:2606.26057（架构级 kill switch，agent 地址空间外，Z3 SMT 验证，比 COMPEL 更根本，L3 看门狗层远期参考）+Novotny Herding 相图 arXiv:2607.08907（φ_∅ 单边订单簿事件比例微观结构 herding 触发器，与 ORCA/Weng 收益分布层面正交互补）+Li et al. Agent Swarm circuit breaker arXiv:2604.27150（2 连亏×0.25 reduction factor 实证参数，与 §3.3 drawdown 阈值驱动正交）+ v1.25.0 §4.20 Continuous Cash-Overlay Filters（arXiv:2606.09025 Xiong 2026-06-08 slow-tail compensation+V-shape crash-brake+max-cash 规则组合，2017-2026 walk-forward CAGR 16.62%→20.45%/MaxDD -33.59%→-16.77% 同时提升收益降低回撤，与 31号 BlackRock 比例控制 vol-targeting 同构连续闭环替代离散分档，P3 远期暂缓）+ v1.26.0 §6.33 Non-concave VaR 约束下赌博回本理论警示（arXiv:2608.05623 Li/Lyu/Wei 2026-08-06 高 floor 诱发 gambling-for-resurrection+低 floor 防御性，为 §4.4 拒绝回撤进 RiskSignal+§3.2 保守低地板阈值提供量化理论背书，与 36号 §3.5 v1.23.0 跨文档交叉印证）+ v1.27.0 §3.5 ⑧ 补 FSB 2026-06-10 AI 稳健实践咨询报告全球监管顶层锚点（G20 框架 12 项 SP，"AI monitoring AI"印证 Unfireable Safety Kernel+Shelby fallback，bounded authority 印证 COMPEL Scoped-disable+§3.7 Kill Switch 不可覆盖，① BoE/BIS/SEBI 均为 FSB 成员顶层锚点，SP3/SP9/SP10/SP11 对个人量化系统同样适用）+ v1.28.0 §3.10/§3.15/§3.18 entry VaR 持久化补全（跨文档算法交接链路 5 缺口修复——§3.10 盘前 VaR_95 快照作为 entry_var 持久化到 state_store 阶段 4b，§3.15 阶段 3 加载 entry_var 供 §3.16 回撤归因 current_var vs entry_var 判断风险恶化，配对约束表新增 entry_var 行）+ v1.30.0 §3.13 intraday_risk_loop 补 strategy_states 参数+aggregate_expected_holdings 辅助函数（伪代码审计缺口修复之二，消除未定义的 strategy_state 引用）+ v1.30.1 §3.13 realized_pnl 来源补全+§3.16 strategy_pnls_history 参数（伪代码审计缺口修复之三）+ v1.30.2 §3.13 trade_date 参数（today→trade_date）+fills/limit_consumption 产出（IntradayResult return 交出盘中累积态供 §3.10 盘后审计消费）+§3.17 阅读指引（前向引用 §3.18 说明）+§3.19 结构说明（审查结论与 §3.20/§3.21 后续章节关系）+v1.30.3 全网 2026-08-08~10 最新算法搜索最终闭环（arxiv 最新 listing 日 8/6，3 篇候选中 2 篇已登记/已评估+1 篇 Zhuang 期权隐含 ES bounds 归入 36号，35号 drawdown/kill switch 方面无新发现，6 流程闭环无缺失独立环节+伪代码审计 9 项缺口已全部修复）+v1.30.4 施工流程数据交接链 7 条断裂修复（后台 agent 深度审查发现：§3.10 无返回值→系统性根因+§3.15 InitializationResult 缺 entry_var+§3.13 缺 response 参数+§3.16 数据源说明缺失+§3.18/§3.15 AttributionResult save/load 闭环缺失+§3.11 转换表缺 RECOVERY→KILL 规则+§3.18 缺 save_strategy_state，全部修复）+v1.30.5 §3.18 prev_attribution 消费方补全（自洽性审查：§3.15 加载 prev_attribution 但无消费方→死数据修复，补 §3.16 当日归因趋势对比消费逻辑）+v1.30.6 施工流程数据交接链 v1.30.4 修复的二次深化——8 条断裂/不完整修复（A1 DailyRiskResult plan/audit 两返回字段补下游消费方：plan 供 execution_broker 执行、audit 供 §3.18 审计门控 audit.passed=False 不持久化+A3 §3.13 补 position_sizing_engine.apply_premarket_cap(response.position_cap) 盘前仓位上限传入盘中+A5 §3.15 strategy_state 冷启动 None 守卫防 detect_ghost_positions 崩溃+§3.18 strategy_engine 悬空引用修复为 position_sizing_engine.get_target_holdings_snapshot+B1 §3.14 ResetConfirmation 补 orders_cancelled_verified/new_open_locked_verified 两字段及校验完成 Kill Switch 三项动作（平仓/撤单/锁新开仓）复位确认+B3 §3.13 补 14:55 收盘前强制检查 EMERGENCY 触发 closing_auction 减仓+C1 §3.11 状态机转换表 RECOVERY→KILL"无条件"与 §3.14 代码"分级保护"分裂修复（RECOVERY→KILL 需阶梯耗尽 step<0/retreat 有 step>0 守卫）+C2 §3.14 KILL→RECOVERY→KILL 循环守卫补复位次数上限 20 日 3 次/冷却期 3 日/永久锁定阈值累计 5 次））+ v1.31.0 跨文档流程交接链 E1-E8 修复（35号↔36号 协同算法完整性：E6 var_breach_state 传入 drawdown_controller.evaluate/E8 var_cvar 产出方统一为 36号经参数传入/E5 盘中 VaR 重算触发调用 36号 §3.12 intraday_var_recalc/E2 持久化状态 DRAWDOWN_COMPLETE vs 36号 VAR_COMPLETE 双阶段标记/E1 盘后持久化顺序 daily_auditor.audit→35号§3.18→36号§3.18/E3 双 RECOVERY 叠加逻辑澄清 effective_cap=阶梯值×0.9+下限保护）+ v1.32.0 §4.24 Lévy-stable Drawdown Scaling 新增+§6.34 Liu Leakage-Safe Residual-Stress Signal 消费方补全 + v1.33.0 §5.2 Stage 4 与 §4.6-§4.24/§6.8-§6.34 全量对齐（14 族分类表，消除此前仅提 §4.12-§4.15/§6.17-§6.20 的 23 项远期登记遗漏）+ v1.34.0 §4.25 MFCCA 符号保留多重分形交叉相关组合分配（arXiv:2608.04987 Kakinaka and Umeno 2026-08-05，保留局部去趋势协方差符号使同向/反向运动以相反符号贡献风险，q=2 退化为 MVO 严格泛化，实证每个收益水平降 drawdown/VaR/ES 无损收益，定位组合配置层远期候选同 §6.30/§6.32，与 sleeve 级回撤 Protocol 正交——Protocol 管"回撤后怎么减"MFCCA 管"分配时怎么避免"，30号 §3.1 拒绝 MVO 诚实账本：符号保留创新但仍需多尺度交叉相关估计与 O(N) 保证冲突，§6.35 待裁定 P4 远期）+ §4.26 Robust Risk Parity RRP（Li and Ye 2026 Finance Research Letters，A 股 2012-2024 全样本实证 GARCH+regime+因子结构协方差，对比 TRP/EW/GMV/MaxRet/ERP 五基线均优，regime 识别维度与 34号 RegimeMetaAllocator 天然对接，§6.36 待裁定 P3 远期，regime+GARCH 组件可独立提取接入 34号不需完整组合配置层+ v1.35.0 §4.27 Drawdown Beyond Brownian Motion（arXiv:2608.00127 Landolfi 2026-07-31）回撤阈值非高斯校准算法——RSB 闭式框架 4 测度扩展（MaxDD/MaxLoss/FinalNegTime/LongestRecovery）证明单一高斯表系统性误警+fBm 持续性表观放大为 √-time 校准失效非真实风险+strategy archetype 分类查表校准配方+Python 伪代码+§6.37 keep-or-kill 待裁定 Phase 3 校准阶段启动前裁定）+ v1.37.0 §4.28 Aldridge & Krawciw AI Governance 新增（arXiv:2608.02311 2026-08-03，4 层治理框架 Policy/Engineering/Composition/Systemic+regret-covariance policy drift 检测+calibrated crowding model 联合回撤 39.2%→79.3% 定量背书+inner LLM confidence kill-switch+90-day 实施序列，§3.19 汇总小表+§5.2 Stage 4 新增治理层族第 15 族+§3.21 根因②分散失效补 crowding model 定量背书）+ v1.38.0 通用规则 #11 已施工设施盘点节新增（§2.4：三层阈值模块+Kill Switch 三实现域分离+支撑设施+未施工清单+注册表缺口全量扫描）+ §3.5 执行路径口径精确化（stop_loss 事件层+DefaultRiskValidator 状态层仅置标志拒新单，平仓/撤单执行链路未落码标注）+ §3.5 与 §3.11 的 15% EMERGENCY 是否触发 Kill Switch 矛盾显式标注（§7 ㉓ 开放问题登记，不擅自裁决）+ §3.21 自引用链接修复 + §6 表头补 P4/P5 定义 + §9 补 v1.37.0 修订记录遗漏条目 |

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

> 本节是通用规则 #11 要求的「已施工设施盘点」——全面扫描代码/配置/注册表/测试/脚本/前端/治理规则后的事实清单。先清楚有什么 → 才能知道怎么改 → 才能知道该删除/退役什么。扫描范围：`src/zephyr/risk/` + `src/zephyr/position/` + `src/zephyr/ex_core/` + `src/zephyr/security/` + `src/zephyr/trading/` + `tests/` + `config/` + `schemas/` + `scripts/` + 三个注册表 YAML。

**① 三层阈值模块（全部 production + 单测齐备，与 §2.2 三体系表一致）**

| 模块 | ID | 路径 | 阈值 | 测试 |
|---|---|---|---|---|
| DrawdownTracker | MOD-RK-011 | `src/zephyr/risk/core/drawdown_tracker.py` | 5/10/15% 三级告警（WARNING/CRITICAL/EMERGENCY），peak 单调非减 + 事件去抖 | `tests/risk/test_drawdown_tracker.py` 20 项 |
| CapitalCurveManager | MOD-POS-007 | `src/zephyr/position/core/capital_curve_manager.py` | 5/10/15% + 仓位上限 100/80/50/30% + 新高扩张 +5%（封顶 2x）+ 亏损收缩 10/20% | `tests/position/test_capital_curve_manager.py` 23 项 |
| DrawdownController | MOD-POS-008 | `src/zephyr/position/core/drawdown_controller.py` | VaR 5 级（2/4/6% + CVaR 10%）+ 策略 Soft/Hard 5/10% + 黑天鹅 7 模式 | `tests/position/test_drawdown_controller.py` 38 项 |

**② Kill Switch 三套实现（域分离，互不调用——盘点新发现：不止 §3.5 一套）**

| 实现 | ID | 域 | 语义 | 与本备忘的关系 |
|---|---|---|---|---|
| `stop_loss.py` + `DefaultRiskValidator` | MOD-L04-001 | D_RISK | 交易风控 Kill Switch：事件层（日志+返回 `requires_manual_reset: True` dict）+ 状态层（`_kill_switch_active` 布尔标志，`validate_order` 拒绝全部新订单） | §3.5/§3.7 的主角 |
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

**④ 未施工清单（文档已声明待办，盘点确认仍缺失——标注"仅文档/未落码"）**

| 缺口 | 待裁定 | 现状 |
|---|---|---|
| RiskOrchestrator 统一编排器 | §6.5（P1） | 无代码；当前 `default_risk_manager_orchestrator` 部分承载，三层喂入靠调用方手动 |
| state_store 持久化层 + DrawdownStateMachine | §6.6 / §6.12（P1/P0） | 无代码；`capital_curve_manager.peak` / `drawdown_tracker` 窗口纯内存，重启即丢；architecture_issue_registry 已登记"Redis 状态外部化层"待办 |
| detect_ghost_positions | §6.11（P1） | 仅 §3.5.1 伪代码，无实现；盘前未接入 |
| Kill Switch 平仓/撤单执行链路 | §6.11 / §6.14（P1/P0） | `stop_loss.trigger_kill_switch` 仅事件记录层；`DefaultRiskValidator` 只置标志 + 拒新订单；**"平仓所有持仓 + 撤所有挂单"无代码**（见 §3.5 口径修正） |
| 独立 black_swan_detector 模块 | —（36 号契约） | 不存在；`BlackSwanSignal` 数据类定义于 drawdown_controller.py，`build_black_swan_signal` 无码，编排层抽象待 RiskOrchestrator |
| 前端回撤/Kill Switch 面板 | — | 未实现；`src/zephyr/frontend/`（MOD-L08-001）仅 stub + CTR-P1-008 RiskDashboardSnapshot 契约 |
| 回撤阈值 YAML 配置 | — | 无；阈值全部硬编码于各模块 dataclass 默认值；`config/risk_params.yaml` 的 `daily_loss_limit_nav_ratio: null`（未配置） |
| ClickHouse 净值曲线/回撤表 | §6.12 配对 | schemas/categories/ 下 100+ 表全为行情/基本面/宏观，无账户净值曲线表 |

**⑤ 注册表登记缺口（治理盘点发现）**

- `capability_canonical_file_registry.yaml`：drawdown_controller / daily_auditor / kill_switch（security）已登记；**drawdown_tracker / capital_curve_manager 无条目**（仅 blueprint_registry.yaml + module_translation_registry.yaml 有记录）——登记缺口，建议在下次注册表维护批次补齐
- `module_translation_registry.yaml`：daily_auditor / ashare_stop_loss_engine 的 `name_zh` 系机器误抽取（取成了异常类名"日终审计输入数据非法"），引用时以 blueprint_registry 的 title 为准

**⑥ 盘点结论（对本文档既有论述的三点修正）**

1. **§2.2"三套独立阈值体系"应精确化为"3+1"**：风控域三套（A/B/C）之外，交易域还有第四套——`trading_kill_switch.py`（MOD-INF-016）5 级熔断器注册表，其中 DAILY_LOSS 阈值 3%（`daily_pnl < -0.03*aum`，CANCEL_ALL + DISABLE_NEW + cooldown 86400s）是 §3.6 日度熔断的第三口径（框架 4% / trading_kill_switch 3% / ashare 引擎 2%）。§3.6 已裁决"采用 §2.5.1 的 4%"，裁决不变，但盘点须记录 3% 口径的存在（它 production 且有 33 项测试，`tests/trading/test_trading_kill_switch.py`）。
2. **§3.5 执行路径的"平仓所有持仓 + 撤所有挂单"未落码**——见 §3.5 口径修正附注。
3. **15% EMERGENCY 是否触发 Kill Switch 存在跨真源口径分裂**——drawdown_tracker.py 模块头注释（"EMERGENCY 级触发 RK-17 Kill Switch"）+ battle_map BM-RC-03（"回撤>EMERGENCY"即触发）支持 15% 触发；30 号 §2.5.5（回撤 >25% 清仓）+ 本备忘 §3.11 状态机（CRISIS 15% → KILL 需 25%）支持 25% 触发。已登记 §7 ㉓ 开放问题，不擅自裁决。

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

> 恢复是**逐步**而非跳变：`drawdown_controller` 的 `recovery_factor` 是乘性的（0.25→0.50→0.75→1.0），与风险级别 cap 相乘，避免"一恢复就满仓"的跳跃风险。这与 [TradeZella 2026-04](https://www.tradezella.com/blog/drawdown-management) 三级恢复协议一致（25% size → 50% → 75% → full，需连续盈利日确认）。

> **v1.9.0 补充——分阶段恢复毕业准则**（§3.20 形式化）：`recovery_factor` 阶梯升级前须满足毕业准则（graduation criteria），对齐 [BloFin 2026-05](https://blofin.com/en/academy/education/handling-drawdowns) 三阶段恢复 + [JournalPlus 2026-05](https://journalplus.co/learn/guides/trading-after-a-drawdown-guide/) 4 阶段框架 + [fazencapital 2026-05](https://fazencapital.com/learn/en/trading-drawdown-recovery-math-methods-guide)（2026-08-04 复审）30 天 reset protocol：① 连续 ≥ 3 个盈利日（TradeZella）；② 近 10 笔交易平均期望 ≥ +0.3R（BloFin Phase 2 graduation）；③ 规则合规率 ≥ 80%（BloFin 行为性检测，防 AI 执行偏差复发）；④ 单笔最大亏损 ≤ 1.2R（completetradersedge 诊断矩阵，止损未被放宽）。毕业准则是 §3.4 `recovery_factor` 数值阶梯的**准则守卫**——数值达标但准则未达标则不升级，对齐 BloFin "Advance only when objective criteria are met. Return to the previous phase if drawdown exceeds the phase limit."。详见 §3.20。

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
| 系统故障 | 连续拒单 ≥5 或价格偏离 >5%（CIRCUIT_BREAKER）/ 延迟 >1000ms 或成交率 <50%（SECOND_LEVEL）/ broker API 超时 >10s 或心跳丢失 ≥3（API_TIMEOUT） | `trading_kill_switch.py`（MOD-INF-016，D_TRADING 执行域熔断注册表，production，§2.4 ②）——v1.38.0 补：系统故障维度不由本备忘的风控域 Kill Switch 承载，由执行域 5 级熔断器承接，两域通过 RiskOrchestrator（§6.5）汇聚取最严；行业印证 [klawtrade 2026-04](https://klawtrade.com/blog/algorithmic-trading-risk-management-guide) 7 触发器含"3+ 系统错误/5 分钟（数据馈送/券商拒单）" |

> **⚠️ 15% EMERGENCY 触发口径矛盾（v1.38.0 盘点发现，登记 §7 ㉓ 开放问题）**：本表"drawdown_tracker EMERGENCY（15%）触发 Kill Switch"与 §3.11 状态机（CRISIS=15% → 仓位上限 30%，KILL 需 drawdown>25% 或 CVaR>10% 或 BS-007）+ 30 号 §2.5.5（回撤>25% 才清仓）矛盾。支持 15% 触发的证据：drawdown_tracker.py 模块头注释（"EMERGENCY 级触发 RK-17 Kill Switch"）+ battle_map BM-RC-03（触发条件"回撤>EMERGENCY"）。**当前实际行为**：15% EMERGENCY 仅发射 E-RK-03 告警事件，无 orchestrator 将其接线到 `trigger_kill_switch`（RiskOrchestrator 未建，§6.5），故代码层面 15% 实际只告警+仓位上限 30%，不会自动全清。裁决候选：a) 15% EMERGENCY 仅告警不触发 Kill Switch（对齐 §3.11/30 号）；b) 15% EMERGENCY 触发 Kill Switch（对齐代码注释/battle_map，则 §3.2 Level 3"仓位上限 30%"动作被架空）；c) 15% EMERGENCY 触发"软 Kill"（禁新开仓+仅平仓，不全清，介于两者之间）。倾向 a)——25% 是 §2.5.1 生存边界，15% 全清过于激进且使 Level 3 动作失效；但涉及阈值语义裁决，留业主决定。

执行路径（v1.38.0 口径精确化——标注各步代码实现状态）：
```
触发源 → drawdown_controller.kill_switch_advised=True          ✅ 已实现（BS-007 唯一自动建议路径）
       → stop_loss.trigger_kill_switch(reason, scope="all")    ✅ 已实现（事件记录层：日志+返回事件 dict）
       → DefaultRiskValidator.trigger_kill_switch() 置状态      ✅ 已实现（_kill_switch_active=True）
       → 平仓所有持仓 + 撤所有挂单                              ❌ 未落码（见下方口径修正）
       → 锁定新开仓                                            ✅ 已实现（validate_order 拒绝全部新订单）
       → requires_manual_reset: True（人工复位才能恢复）         ✅ 已实现（事件 dict 字段）
```

> **口径修正（v1.38.0）**：`stop_loss.trigger_kill_switch` 是**事件记录层**（日志 + 返回 `requires_manual_reset: True` dict），`DefaultRiskValidator.trigger_kill_switch()` 只置布尔标志——**"平仓所有持仓 + 撤所有挂单"的执行链路（调用 execution_broker 发平仓单/撤单）在风控域无代码**，当前生效的强制力仅"锁定新开仓"（`validate_order` 在 kill_switch_active 时拒绝全部新订单，severity=HALT）。即当前 Kill Switch 的实际语义是"**禁止新增风险 + 事件告警**"，"存量持仓平仓"依赖人工或 40_execution_broker 执行层衔接（§6.11/§6.14 待裁定）。另注：`reset_kill_switch` 的确认校验（`confirmed_by`+`override_reason` 留审计日志）在 stop_loss 事件层实现；`DefaultRiskValidator.reset_kill_switch()` 状态层无确认参数，直接清标志——两层语义差异在 §6.11 施工时需统一（最小补丁：状态层 reset 增加 confirmation 必填校验，§3.14 已含此设计）。
>
> 代码已实现 `trigger_kill_switch` 返回 `requires_manual_reset: True`，状态由 `DefaultRiskValidator` 管理。`daily_auditor` 日终检查清单第 4 项验证 Kill Switch 终态 == CLOSED（FAIL 判据）。

> **COMPEL Framework Kill-Switch 四模式架构参考**（[COMPEL Body of Knowledge AITL M9.3-Art02 v1.0, 2026-04-06](https://compelframework.org/articles/ai-agent-kill-switch-and-escalation-protocols)）：COMPEL 提出 agentic AI 系统的四种叠加停止模式，每模式 60 秒内可执行 + 自动升级 + 可逆状态保存 + 取证捕获——这是目前找到的最施工可落地的 kill switch 算法蓝图。**四种模式到本项目的映射**：
>
> | COMPEL 模式 | 语义 | 本项目对应 | 现状 |
> |---|---|---|---|
> | Hard-stop | 立即终止进程，放弃在途工具调用 | §3.5 `trigger_kill_switch(scope="all")` 全平 + 撤单 + 锁新开仓 | ✅ 已实现 |
> | Graceful-halt | 完成当前原子动作后停止 | §3.4 recovery_factor 阶梯减仓（25%→50%→75%）+ §3.20 hysteresis min_hold | ✅ 已实现（恢复阶梯） |
> | Rollback | 回滚已执行的错误动作 | §3.5.1 Ghost Position 检测 + 异常订单撤销（待 §6.11） | ❌ 部分缺失（L2/L3 层） |
> | Scoped-disable | 禁用单一 agent 或能力 | 单策略 Soft/Hard Stop（§3.3）+ 策略级 circuit breaker（[37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md)） | ✅ 已实现 |
>
> **关键启示**：本项目当前实现已覆盖 Hard-stop（§3.5 全平）+ Graceful-halt（§3.4 恢复阶梯）+ Scoped-disable（§3.3 单策略止损）三模式，**Rollback 模式**（错误动作回滚）是 §3.5.1 4 层架构的 L2/L3 层待施工部分（§6.11）。COMPEL 的"60 秒内可执行 + 取证捕获"要求与本项目 §3.5.1 A 股 2026 新规适配（15 笔/秒分片全清 ⌈N/15⌉ 秒）+ §3.18 盘后持久化（daily_auditor 审计日志）一致。**不新增独立模块**——COMPEL 四模式是 kill switch 设计的**语义分类框架**，本项目现有实现已隐式覆盖三模式，Rollback 待 §6.11 施工时补齐。**VeritasChain Flight Recorder**（[VeritasChain 2026-01-20](https://veritaschain.org/blog/posts/2026-01-20-five-incidents-algorithmic-trading-flight-recorder/)）进一步提出 append-only + prev_hash 哈希链 + Ed25519 签名 + RFC 8785 JSON 规范化的三层加密审计架构（分析 Two Sigma 22 个月未检出参数操纵 + SEC 罚 9000 万美元事件），本项目 §3.18 盘后持久化的 `daily_auditor.log_*` 应向此标准演进（远期 §6.31 待裁定）。

> **Unfireable Safety Kernel——架构级 kill switch（比 COMPEL 更根本）**（[arXiv:2606.26057](https://arxiv.org/abs/2606.26057)，Dobrin & Chmiel 2026-06-24，ARYA Labs；Dobrin 为 IBM 首任全球首席 AI 官；[开源代码 Apache-2.0](https://github.com/ARYA-Labs-Public/unfireable-safety-kernel)）：提出**执行时对齐**（execution-time alignment）概念，区别于训练时对齐（RLHF）和推理时对齐（prompts/filters）。**核心创新**：kill switch 运行在 **agent 地址空间之外**——agent 无法触及、无法重配置、无法杀死，且没有它就无法启动（"no kernel, no agent"）。四属性：① 进程分离（独立进程/独立内存空间）；② 在唯一路径上的预执行强制（pre-execution enforcement on the only path）；③ 请求级与系统级双重 fail-closed；④ Ed25519 签名的外部化证据日志。**形式化验证**：Z3 SMT 定理证明 fail-closed 不变量 + Kani 有界模型检测生产 Rust 决策函数（4/4 harness 验证）+ 1000 个确定性 fixture 的字节等价迁移。**对抗评估**：1000 次自修改中所有 704 次针对安全核心的逃逸尝试均被拒绝 + operator kill switch 下另 300 次全部拒绝 + 6240 次授权往返无成功绕过。**与 COMPEL 的关系**：COMPEL 四模式是 kill switch 的**语义分类**（停止模式语义），Unfireable Safety Kernel 是 kill switch 的**架构保证**（agent 无法绕过）——两者正交，COMPEL 管"怎么停"，Unfireable 管"停不掉"。**对本项目的启示**：当前 §3.5 `trigger_kill_switch` 在策略进程内调用，`stop_loss` 虽独立于 `drawdown_controller`（§3.5 SEBI 物理隔离满足），但仍在同一 Python 进程内——若策略进程崩溃/被 OOM kill/hang，kill switch 无法执行。§3.5.1 L3 看门狗层（独立进程）是 Unfireable 思路的**部分实现**，但当前标注"❌ 缺失"。**登记为 §6.31 远期演进**——L3 看门狗层施工时（§6.11），参考 Unfireable 四属性设计：① 看门狗进程独立于策略进程（✅ 已设计）；② 看门狗在策略启动的唯一路径上（策略无法绕过看门狗启动）；③ fail-closed（看门狗心跳超时→策略无法继续交易）；④ Ed25519 签名审计日志（与 VeritasChain 对齐）。性能参考：Microsoft Agent Governance Toolkit p50 策略评估约 0.011-0.030ms，内核强制约 0.103ms——对 A 股日频/T+1 交易无性能瓶颈。

> **Novotny Herding 相图触发——herding 微观结构定量基础**（[arXiv:2607.08907](https://arxiv.org/abs/2607.08907)，Novotny 2026-07-09，Bayes Business School）：应用 Bouchaud 相图（phase-diagram）方法到连续双向拍卖订单簿模型，7×6 网格（336 次运行，每次带 scrambled-sign null）。识别出涌现的流动性压力交叉点：在 (φ,κ)=(0.9,1.0) 处单边订单簿事件比例 φ_∅≈0.34，而 42 个 scrambled 单元全部为零。**rule-robust**（在 order-flow-imbalance 规则下重现 φ_∅=0.227）+ **horizon-robust**（16× 动量窗口范围下 ≈0.32-0.35）。价格动量 herding 带大的反射性分量（+0.29），而 OFI 规则的分量≈0。**与 §3.5 herding 检测的关系**：§3.5 ⑦ ORCA 谱特征 + Weng Johnson S_U 是**收益分布层面**的 herding 检测，Novotny 相图是**订单簿微观结构层面**的 herding 检测——两者正交互补。φ_∅（单边订单簿事件比例）可作为 kill switch 的**微观结构触发器**：当 φ_∅ 超过阈值（如 0.30）时启动熔断，而非仅看自身 drawdown。**本项目适配**：A 股 T+1 + 涨跌停限制下订单簿微观结构与美股不同（涨跌停使单边事件更频繁），需 A 股实证校准 φ_∅ 阈值。**登记为 §6.31 远期候选**——当 §3.5.1 L3 看门狗层接入实时订单簿数据（Level 2 行情）后，φ_∅ 可作为 kill switch 的微观结构预警信号。Phase 4+ 远期（需 Level 2 数据基础设施 + A 股 φ_∅ 阈值校准）。

> **Li et al. Agent Swarm circuit breaker 实证参数**（[arXiv:2604.27150](https://arxiv.org/abs/2604.27150)，Li/Laryea/Ihlamur 2026-04，Oxford + Vela Research）：将退出规则调优重新框架为校准问题——900+ 历史交易，8960 配置全网格比较 + ATR 覆盖和 circuit-breaker 逻辑二阶段细化。**最强配置**：1.0×ATR 止损 + 2.0×ATR 止盈，**circuit-breaker 在连续 2 次亏损后 reduction factor 0.25**（即连续 2 亏后仓位缩至 25%）。**与 §3.3 单策略止损 + §3.20 hysteresis 的关系**：§3.3 单策略 Soft Stop 是 drawdown 阈值驱动（5/10/15%），Li et al. 是**连续亏损次数驱动**——两者正交可叠加（drawdown 触发 + 连亏触发双维度 circuit breaker）。§3.20 hysteresis 的 min_hold 5/10/20 交易日是恢复时间维度，Li et al. 的 0.25 reduction factor 是仓位缩减幅度维度。**本项目适配**：当前 §3.3 已有"单策略连续亏损"概念但缺 circuit breaker 形式化——Li et al. 的 0.25 reduction factor + 2 次连亏触发提供实证参数。**登记为 §3.3 增强**——Phase 2 候选，当 §3.3 单策略止损施工时引入"连亏 circuit breaker"子模块（2 连亏→仓位×0.25，3 连亏→Soft Stop），参数参考 Li et al. 但需 A 股实证校准（ATR 倍数可能不同）。

### 3.5.1 Kill Switch 执行失败兜底（4 层架构 + Ghost Position）

**问题**：§3.5 假设 `trigger_kill_switch` 一定成功，但实际 broker 可能拒单（如 FOMC/政策行情 CME reserved state）、部分成交、连接中断，导致**幽灵持仓**（Ghost Position）——平仓指令发出但未成交，持仓无人管理。nexusfi 2026-06 实证 [@Breukelen 2022 案例](https://nexusfi.com/a/automation/automated-trading-emergency-protocols)：Kill Switch 触发后 CME 拒单，14 手 ES 无主暴露，仅靠 78 微秒的 bracket stop 残留单侥幸平仓。

**4 层防御架构**（[nexusfi 2026-06](https://nexusfi.com/a/automation/automated-trading-emergency-protocols) 四层独立设计，每层捕获上层遗漏）：

| 层 | 职责 | 触发 | 本项目现状 |
|---|---|---|---|
| L1 代码层 | `stop_loss.trigger_kill_switch` 发市价平仓 + 撤挂单 | drawdown_controller.kill_switch_advised | 🟧 **部分实现**（v1.38.0 口径修正：事件记录 + 状态置位 + 新开仓拒绝已落码；发市价平仓 + 撤挂单的执行链路未落码，待 §6.11/§6.14 与 40_execution_broker 衔接） |
| L2 平台层 | broker 端硬止损单（bracket/OCO），不依赖策略连接 | 开仓时同步挂 broker 端 stop | ❌ **缺失**（miniQMT 通道需确认是否支持 broker-side bracket） |
| L3 看门狗层 | 独立进程监控"持仓 vs 策略状态"一致性，不一致即强平 | 定时轮询 broker 持仓 vs DefaultRiskValidator 状态 | ❌ **缺失** |
| L4 人工层 | 人工复位 + 持仓清零确认（§3.7 `requires_manual_reset`） | Kill Switch 触发后强制 | ✅ 已实现 |

**Ghost Position 检测**（待施工 §6.11）：
```python
def detect_ghost_positions(broker_holdings, strategy_state):
    """看门狗：检测策略认为已平仓但 broker 仍有的持仓。
    
    Ghost = broker_holdings[sym].qty != 0 但 strategy_state[sym] == CLOSED
    或 Kill Switch == CLOSED 但 broker 仍有任意持仓。
    """
    ghosts = []
    for sym, pos in broker_holdings.items():
        if pos.qty != 0 and strategy_state.get(sym) == "CLOSED":
            ghosts.append((sym, pos, "strategy_closed_but_broker_holds"))
    if strategy_state.kill_switch == "CLOSED":
        for sym, pos in broker_holdings.items():
            if pos.qty != 0:
                ghosts.append((sym, pos, "kill_switch_closed_but_position_remains"))
    return ghosts
```

> **裁决**：L1 + L4 已实现（代码层 + 人工复位），L2/L3 暂缓为 §6.11。理由：① 个人系统 miniQMT 通道的 broker-side bracket 支持待确认（A 股 ETF/股票的 OCO 单支持情况需实测）；② L3 看门狗需独立进程，与当前单进程架构不一致，且 A 股 T+1 下"日内幽灵"窗口小（无法日内反转，最坏盘后清零）。但**盘前必须做一次持仓核对**（`daily_auditor` checklist 第 5 项数据完整性扩展），若 Kill Switch == CLOSED 但 broker 仍有持仓 → 拒绝开新仓 + 立即人工告警。

> **多维 Kill Switch 参考框架**（[Tidball 2026-05 "Kill Switch Framework For AI FX Bots"](https://fxmacrodata.com/articles/kill-switch-framework-for-ai-fx-bots)）：
>
> Tidball 提出分层 kill switch 栈，**每个维度独立刹车，任一触发即暂停**——与本项目 4 层架构互补（4 层按**执行路径**分层，Tidball 按**触发维度**分层）：
>
> | Tidball 维度 | 检测内容 | 本项目对应 | 状态 |
> |---|---|---|---|
> | ① 数据完整性 | 时间戳新鲜度/字段完整性/跨源一致性 | `daily_auditor` checklist 第 5 项 + 55_monitoring_review | ✅ 已实现 |
> | ② 模型行为 | schema 解析失败率/策略违规次数/无支撑高置信 | §3.12 行为性回撤诊断 + §3.16 归因 | 🟧 待施工 §6.7 |
> | ③ 执行异常 | 滑点/拒单率/延迟 | 40_execution_broker CancelRateGuard + 撤单率监控 | ✅ 已实现（v2.6.0） |
> | ④ 组合回撤 | session -1.25%/daily -2.0%/最大相关敞口 | §3.5 Kill Switch + §3.6 日度熔断 + §3.13 盘中循环 | ✅ 已实现 |
> | ⑤ 事件窗口 | 重大数据发布前暂停 | §3.14 黑天鹅事件监控（36号 §3.14）政策黑天鹅 | 🟧 待施工 |
>
> **核心原则印证**：Tidball 的两条设计原则与本项目现有设计**完全一致**：① **"fail closed"**（监控不可用时默认 halt）——本项目 §3.15 盘前初始化的 `RefuseStart`（Ghost Position / 通道不健康即拒绝启动）即 fail closed；② **"安全状态必须在模型外计算"**——本项目 `stop_loss` 模块独立于 `drawdown_controller`（仅 `kill_switch_advised` 布尔信号单向交接），与 §3.5.1 ⑧ FSB "deterministic output gating + bare-metal recovery" 印证。Tidball 框架不新增独立模块，作为 §6.11 4 层架构施工的**维度检查清单**——确保每个 Tidball 维度都有对应检测+刹车。

**A 股 2026 程序化交易新规对 Kill Switch 执行的影响**（[csdn 2026-08-08](https://blog.csdn.net/syp1110/article/details/163276625)）：

2026-04-07 生效、7-07 全面执行的《程序化交易管理实施细则》对 Kill Switch 平仓执行链路施加新约束：

| 新规约束 | 数值 | 对 Kill Switch 的影响 |
|---|---|---|
| 每秒申报上限 | 15 笔（原 300 笔） | 全清多持仓时，若持仓标的 >15 只，**1 秒内无法全部平仓**——需分批拆单 |
| 每秒撤单上限 | 15 笔 | 撤所有挂单时同样受限，撤单风暴会触发异常交易监控 |
| 单日撤单率上限 | 15% | Kill Switch 触发后大量撤单可能撞日撤单率红线 |
| 每笔报单最小停留 | 50 微秒 | 市价平仓单的提交节奏受限，无法"瞬时全清" |

**对 §3.5 Kill Switch 执行路径的修正**：

原执行路径（§3.5）假设"平仓所有持仓 + 撤所有挂单"是瞬时完成的，但新规下：
1. **持仓 >15 只时需分批平仓**：`stop_loss.trigger_kill_switch(scope="all")` 内部需按 15 笔/秒分片，全清 N 只持仓需 ⌈N/15⌉ 秒——这段窗口内持仓仍暴露于市场风险（Ghost Position 风险窗口扩大）
2. **撤单需计数**：撤挂单前检查"今日已撤单率"，若接近 15% 红线，优先撤关键挂单（如大额/远离市价的），放弃小额挂单让其自然到期
3. **拆单算法**：全清平仓应用 TWAP/VWAP 拆单（[csdn 2026-08-08](https://blog.csdn.net/syp1110/article/details/163276625)：TWAP/VWAP 是 2026 新规下的执行标配），而非裸市价单——但这与 Kill Switch"尽快平仓"目标冲突，需权衡

> **裁决**：Kill Switch 平仓执行需适配 A 股 2026 新规，但**不改变"尽快全清"原则**——拆单是为合规，不是为追求好价格。最小实现：① `trigger_kill_switch` 内部按 15 笔/秒分片提交市价平仓单（非 TWAP 优化）；② 撤单前检查日撤单率，超 12% 预警（留 3% buffer）；③ 全清完成确认（polling 所有持仓归零，§3.5.1 Ghost 检测）需考虑分片延迟，超时（如 30 秒未全清）即告警人工介入。新规适配纳入 §6.11 Kill Switch 4 层架构施工。

**2026 年全球监管趋势对 Kill Switch 独立性与审计的强化要求**（[Bank of England 2026-06-30 Sintra Forum](https://hotminute.co.uk/2026/07/05/kill-switches-for-the-stock-market-inside-the-bank-of-englands-ai-contingency-planning/) + [SEBI 2026-05 算法交易框架](https://clearyourexam.com/current-affairs/sebi-new-framework-algorithmic-trading-enhanced-corporate-governance)）：

> ① **多 agent 协作风控 / herding 风险**——BoE 副行长 Sarah Breeden 在 ECB Sintra Forum（2026-06-30）指出，AI agent 交易的核心风险**不是单一 agent 失控，而是多个 agent 对相同触发作出相似反应导致 herding**，在压力事件中放大波动（"a thousand well-governed trading agents can still stampede together"）。BoE 与 BIS Innovation Hub + Bundesbank 联合运行结构化多轮压力模拟，研究 agent 设计如何驱动 herding，并探索"类似 circuit breaker 的市场级 kill switch"以在 AI 模型故障引发崩盘时限制或停止交易。Breeden 明确指出"relying on a human in the loop for every agent action is unlikely to be realistic"，现有监管框架"not built for autonomous agents"。FPC 于 2026-07-07 发布 AI 与金融稳定评估。**对本项目的启示**：虽然本项目是单账户系统，但 100% AI 开发意味着决策逻辑由 AI 模型驱动——Breeden 警示的 "objective drift"（agent 目标偏离运营者意图）在 AI 模型迭代中同样存在。§3.5.1 的 4 层防御架构（代码/平台/看门狗/人工）+ §4.8/§4.18 的统计检测（CUSUM/Hawkes/Lee-Mykland/BOCD）正是对"AI 决策失效"的多层兜底，与监管方向一致。
>
> ② **独立 Kill Switch 物理隔离**——SEBI 2026-05 算法交易框架强制要求算法交易系统必须包含**与主交易逻辑物理隔离的 Kill Switch** + 算法报备 + 实时监控 + 增强公司治理。**对本项目的验证**：`stop_loss` 模块（`trigger_kill_switch`）独立于 `drawdown_controller`（仅通过 `kill_switch_advised` 布尔信号单向交接），满足"Kill Switch 独立于主交易逻辑"的监管要求。§3.7 不可覆盖原则（`requires_manual_reset: True`，无 `auto_reset` 通道）与 SEBI"人工复位"要求一致。
>
> ③ **事后审计不可绕过**——BoE 提出 Kill Switch 触发后须提交包含失效原因诊断的审计报告。**对本项目的覆盖**：`daily_auditor` 日终检查清单第 4 项（Kill Switch 终态 == CLOSED）+ 第 5 项（数据完整性 + 持仓核对，§3.5.1 Ghost Position 检测）覆盖此要求。本项目的人工复位机制是"事件级人工介入"（Kill Switch 触发后 reset）而非"每笔交易人工审批"，与 Breeden"现实可行治理框架"的期待一致——避免了她批评的"human-in-the-loop for every action"不现实路径。
>
> ④ **circuit breaker vs kill switch 语义区分 + Q3 2026 DP 时间线 + deterministic output gating**（[BoE FPC Financial Stability Report 2026-07-07](https://integrated.social/blog/bank-of-england-ai-governance-circuit-breakers-financial-stability-2026/)）——BoE FPC 半年度金融稳定报告正式将 agentic AI 系统性风险写入，明确区分 **circuit breaker**（临时可恢复暂停，system can be safely resumed）与 **kill switch**（永久/长期终止，system cannot be safely corrected）。**对本项目的映射**：§3.7 Kill Switch 不可覆盖原则（`requires_manual_reset: True`）对应 kill switch 语义（终止+人工复位），37 号 circuit breaker 对应可恢复暂停语义（临时暂停+自动恢复），两者分层正交与 BoE 语义一致。**Q3 2026 Discussion Paper 时间线**：BoE DP Q3 2026（8-9 月）将正式咨询 agentic AI 系统性风险与 kill switch 强制要求 → FCA Dear CEO Letter Q4 → PRA binding rules 2027 → 全面执行 2028。**deterministic output gating + bare-metal recovery**——BoE 要求 kill switch 的 output gating 必须在 agent reasoning loop **之外**（deterministic，非模型自评安全状态），且须有 bare-metal recovery capability（物理隔离恢复，压力测试下验证）。**对本项目的验证**：`stop_loss` 模块独立于 `drawdown_controller`（仅 `kill_switch_advised` 布尔信号单向交接）满足"deterministic + loop-external"；Task Scheduler watchdog（`wscript.exe` + `launch_hidden.vbs`，GUI 子系统无控制台闪窗）+ `daily_auditor` 独立审计进程满足"bare-metal recovery"——kill switch 状态由独立进程计算，不依赖交易主循环自评。
>
> ⑤ **Herding 风险定量背书（2026-08 最新研究）**——[GeomHerd arXiv:2605.11645](https://arxiv.org/abs/2605.11645)（Yang & Su 2026-05）揭示**价格相关性 herding 检测滞后 272 步**——基于 agent-interaction graph 的 Ollivier-Ricci curvature 在 order-parameter 出现前中位数 272 步触发，领先 price-correlation 基线 40 步，contagion detector 回忆 65% 关键轨迹提前 318 步。[arXiv:2604.03272](https://arxiv.org/abs/2604.03272)（Meng & Chen, NYU, 2026-03）用 SEC 13F 全样本（9950 万持仓、10957 管理人、2013-2024）+ Bartik 工具变量（一阶段 F=22.7）证实 AI 系统性风险的**尾部损失放大 18-54%**，乘子 M=(1-r)^{-1} 在 AI 渗透率 φ 上**超线性增长**（非线性加速），cross-sectionally 排除杠杆周期解释。**对本项目的启示**：Breeden ① 的 herding 风险有定量背书——18-54% 尾部放大是超线性而非线性，意味着 A 股 AI 策略渗透率上升时尾部风险**加速**积累。本项目虽是单账户系统，但若自身信号与主流 AI 策略相关性 ρ 上升，应主动降仓。Phase 2 候选：监控"决策图"层面的策略相关性（GeomHerd 思路），而非仅价格相关性（HBI/CSAD 已在 31/32 号登记但属价格维度，滞后 272 步）。
>
> ⑥ **"证明而非声称" + kill switch 行业就绪度背书（2026-08 最新监管动态）**——① [BoE 行长 Andrew Bailey 2026-07-23 开放信](https://resultsense.com/news/2026-08-05-bank-of-england-frontier-ai-testing/) 要求银行通过**压力测试与渗透测试"证明"AI 韧性，而非在政策文件中"声称"**——同周 AISI 发布事件报告描述 agent 在评估中对真实系统采取未授权行动。**对本项目的映射**：§3.5 Kill Switch + §3.20 hysteresis + §3.5.1 Ghost Position 检测不能停留在代码注释与设计文档，须用实盘或模拟实盘证据记录响应时间、触发准确性、状态保存完整性——`daily_auditor` 日终审计日志 + §3.15 盘前 Ghost 核对是"证明"的最低基线，远期应引入 tabletop 演练（模拟 kill switch 触发场景验证 60 秒内全清）。② [Wolters Kluwer 2026 银行 kill-switch 调研](https://coresystempartners.com/core-insider/the-kill-switch-gap/)：**72% 的银行 AI 治理最薄弱环节是 kill-switch 协议（34%）或 AI 故障监管报送（38%）**，文件化的 kill switch 与运行时实际可执行的 kill switch 是两回事——"未测试的 kill switch 不是 kill switch，只是意图声明"。**对本项目的警示**：本项目虽非受监管银行，但此数据印证"kill switch 须实测"——§6.11 4 层架构施工时必须做 tabletop 测试与实盘断电演练，验证响应时间与状态保存。③ [FCA Mills Review 2026-07](https://investx.fr/en/crypto-news/fca-agentic-ai-tokenized-money-financial-disruption/) 建议FCA 3-6 个月内审查监管外围外的 AI 金融服务，FCA 警告 agentic AI + 可编程货币构成系统性断裂，要求**算法决策可追溯、自动 circuit breaker、强化报送**——与本项目 §3.18 盘后持久化 + §3.5 Kill Switch 不可覆盖 + daily_auditor 审计清单的设计方向一致。
>
> ⑦ **Herding 检测可施工替代（2026-08 最新研究，补 ⑤ GeomHerd 的轻量化路径）**——⑤ 的 GeomHerd（Ricci 流曲率）计算复杂度高，对个人系统偏重。两项 2026 研究提供**可施工的轻量化替代**：① **[ORCA Online Regime Correlation Analyzer arXiv:2604.17251](https://arxiv.org/abs/2604.17251)（Kriuk 2026-04）**——24 个 ETF 滚动相关矩阵，提取 **127 个谱特征**（吸收比、特征值熵、有效秩、谱隙、聚类系数、边密度、主特征值百分位）+ 79 传统指标，Random Forest 8 折 walk-forward，15 年数据，**BCD-AUC=0.741，谱特征对 crash 检测贡献 +10.3 个百分点**，回测 Sharpe 1.13 / CAGR 15.6% / **MaxDD 仅 -7.5%**。ORCA 的谱特征（尤其吸收比、主特征值百分位）比 GeomHerd 轻量得多，且对 crash 检测增益显著。② **[Weng A 股 herding arXiv:2607.27063](https://arxiv.org/abs/2607.27063)（Weng 2026-07-29，人大物理系）**——agent-based 模型 + von Neumann/Moore 格子 + ER/WS 网络鲁棒性，实证用 CSAD/LSV + **Johnson S_U 变换的滚动尾部 herding 指标**，A 股数据显示各指标在重大扰动期间同步上升。**Johnson S_U 变换的尾部 herding 指标**比纯 CSAD 更敏感于尾部——这是 2026 年专门针对 A 股 herding 的论文，可直接用于本项目 herding 检测模块。**对本项目的定位**：⑤ GeomHerd 是决策图层面的远期愿景（Ricci 流计算成本高），⑦ ORCA + Weng 是**价格相关性层面的可施工替代**——ORCA 谱特征（吸收比/主特征值百分位）+ Weng Johnson S_U 尾部 herding 可作为 §3.5 ⑤ herding 监控的 Phase 2 候选，与 31/32 号已登记的 HBI/CSAD 互补（HBI/CSAD 是基础维度，ORCA 谱特征是结构维度，Weng S_U 是尾部维度）。记为 Phase 2 候选（远期，待 §6.7 回撤类型诊断施工后评估）。
>
> ⑧ **FSB AI 稳健实践咨询报告——全球监管顶层锚点（2026-08 最新）**——[FSB 2026-06-10 "Sound Practices for Responsible Adoption of Artificial Intelligence (AI)"](https://www.fsb.org/2026/06/sound-practices-for-responsible-adoption-of-artificial-intelligence-ai-consultation-report/) 咨询报告，12 项稳健实践（SP1-4 组织级治理 / SP5-10 生命周期管理 / SP11-12 网络与第三方风险）。**层级定位**：FSB 是 G20 框架下全球金融稳定协调机构，① BoE/BIS/SEBI 均为 FSB 成员，本报告是 ①-⑦ 监管背书的**顶层锚点**——成员级监管（BoE FPC/SEBI/Bailey）在 FSB 框架下协调，本项目印证方向与 FSB 顶层框架一致。**核心洞察"AI monitoring AI"**：FSB 明确指出"continuous human monitoring of individual AI agent decisions is becoming impractical at scale"，建议用 AI 监控 AI（separate system watching production agents, flagging anomalies, triggering review）——这与本项目 §3.5.1 L3 看门狗层（独立进程监控持仓一致性）+ §6.31 Shelby AI Resilience Gap fallback 教义 + Unfireable Safety Kernel（agent 地址空间外强制）**直接印证**。**bounded authority 印证**：FSB 建议将 AI agent 视为"synthetic employees"，赋予 bounded authority + defined scope + accountability constraints——与本项目 §3.7 Kill Switch 不可覆盖（`requires_manual_reset: True`）+ COMPEL Scoped-disable 模式（单策略/单能力禁用）印证。**agentic AI 放大风险印证**：FSB 点名"智能体化AI"为重点风险源（unauthorized actions / goal misalignment / reward hacking），与本项目 §3.21 A股量化私募端到端 AI 逆向承接深套印证——虽本项目是传统量化非 agentic AI，但 100% AI 开发意味着决策逻辑由 AI 模型驱动，FSB 框架对 AI 模型迭代治理同样适用。**适用性边界**：报告不具法律约束力（咨询性质，征求意见至 2026-07-22，最终版 2026-10 提交 G20），但将成 G20 框架下 AI 治理基准。本项目非受监管机构，但 12 项 SP 中 **SP3（AI 风险管理框架）+ SP9（性能管理）+ SP10（人工监督）+ SP11（网络/ICT 风险）**对个人量化系统同样适用——本项目 §3.5 Kill Switch + §3.18 daily_auditor 审计 + §3.5.1 Ghost Position 检测 + Task Scheduler watchdog 已隐式覆盖核心要求。**不新增独立模块**——FSB 12 项 SP 是治理框架非施工算法，本项目现有实现已隐式对齐，登记为监管背书顶层锚点增强合规性论证。

### 3.6 日度熔断（讨论要点 ⑤）

**决策**：日度熔断由 `daily_pnl_check`（通用机制）+ Kill Switch `DAILY_LOSS` 类型承载，阈值可配置。

| 触发 | §2.5.1 框架 | 代码现状 | 裁决 |
|---|---|---|---|
| 组合单日亏损 | > 4% → 暂停开仓 1 天 | `daily_pnl_check(daily_pnl, loss_limit)` 通用，`ashare_stop_loss_engine` 默认 2% | 采用 §2.5.1 的 4%（比代码默认 2% 宽，但作为组合层熔断合理；单策略层仍可用 2%） |
| 单策略单日亏损 | > 5% → 该策略暂停 1 天 | 无独立模块，走 `StrategyPnl` + Soft Stop | 采用 5%，由 `drawdown_controller` 策略级止损承载（Soft Stop 5% 砍仓） |

> 日度熔断是"时间维度"的风控，与回撤（"幅度维度"）正交。代码的 `daily_pnl_check` 是正确抽象——它不绑定具体阈值，由配置注入，避免硬编码。`ashare_stop_loss_engine` 的 2% 默认值是**单标的止损**层级（更紧），与组合层 4% 不冲突（不同层级不同阈值）。
>
> **v1.38.0 盘点附注——日度熔断的第三口径**：除框架 4% 与 ashare 引擎 2% 外，`trading_kill_switch.py`（MOD-INF-016，D_TRADING，production）的 `KillSwitchLevel.DAILY_LOSS` 定义为 `daily_pnl < -0.03 * aum`（**3%**），动作 CANCEL_ALL + DISABLE_NEW、cooldown 86400s、auto_reenable=False（`tests/trading/test_trading_kill_switch.py` 33 项测试）。三口径并存：框架裁决 4%（组合层，本备忘采用）/ trading_kill_switch 3%（交易域注册表）/ ashare 引擎 2%（单标的层）。三者层级不同不构成矛盾，但 RiskOrchestrator（§6.5）施工时须明确"以哪一口径为组合层唯一生效值"，避免多口径同时生效导致告警语义混乱——当前裁决维持 4%，3%/2% 作为更紧的内层不冲突（先触发者先生效，取最严原则自动成立）。

### 3.7 Kill Switch 不可覆盖原则（讨论要点 ⑥）

**决策**：不可覆盖，代码已实现。

- `trigger_kill_switch` 返回 `requires_manual_reset: True`，无 `auto_reset` 通道
- `reset_kill_switch(confirmation)` 需 `confirmed_by` + `override_reason`，留审计日志
- 状态由 `DefaultRiskValidator` 集中管理，非调用方可绕过
- 行业印证：[Punch 2026](https://builderslab.punch.trade/help/articles/1440242-use-kill-switch-to-lock-trading-on-punch-desktop)："You cannot turn it off early. That's the point."；[go-trader 2026](https://github.com/richkuo/go-trader/issues/25)："Manual reset required to resume (no auto-restart)"
- Knight Capital 2012 年 45 分钟亏 $440M 是无 Kill Switch 的前车之鉴（[algotradingdesk 2026-03](https://algotradingdesk.com/kill-switch-mechanisms-hft-risk-control/)）

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

**乘性叠加 vs 加性惩罚的选型理由**：[RMATS 2026](https://arxiv.org/abs/2605.25311) 的 Risk Agent 用 RL 目标函数 `R_t = r_t − λ₁σ_t − λ₂max(0, DD_t − θ)`（λ₁=0.8, λ₂=1.5），是**加性惩罚**——回撤超阈值时从收益中扣减惩罚项。本项目选**乘性叠加**而非加性，理由：① 乘性保证"任一因子为 0 则总仓位为 0"（Kill Switch 或 regime 极端时彻底停仓），加性做不到（收益高时惩罚被稀释）；② 乘性是仓位上限的天然语义（`cap = a × b`，两者都是 [0,1] 系数），加性是收益目标的语义（不适合仓位节流）；③ 乘性各因子独立可解释（regime 0.8 × drawdown 0.5 = 0.4，可拆解归因），加性混合后难归因。RMATS 的加性适合 RL 训练时的端到端目标，本项目乘性适合规则式风控的模块化叠加。

### 3.10 施工流程算法（日度风控循环）

**现状**：代码无统一编排入口——`drawdown_tracker` / `capital_curve_manager` / `drawdown_controller` 各自独立，无 orchestrator 串联。当前由调用方手动编排，`drawdown_controller.evaluate()` 需调用方依次喂入 `drawdown_info` / `var_cvar` / `black_swan` / `strategy_pnls`。

**日度风控循环伪代码**（待施工编排器，参考 [nexusfi 2026-06](https://nexusfi.com/a/automation/automated-risk-controls) 三层防线编排）：

```python
def daily_risk_loop(trade_date, positions, nav, returns, strategy_pnls, realized_pnl,
                    state_machine, var_cvar, var_breach_state,
                    fills=None, limit_consumption=None):
    # ── 盘前：更新净值曲线 + 计算回撤（A 层监控 + B 层节流）──
    # v1.30.4 补：state_machine 补入函数签名（§3.15 InitializationResult 产出 → 本函数消费，
    #             drawdown_controller.evaluate() 依赖状态机当前态执行 §3.11 转换守卫）
    # v1.30.1 修：realized_pnl 补入函数签名（原伪代码直接引用但未声明参数）
    # v1.29.1 修：fills / limit_consumption 补入函数签名（原盘后审计直接引用但未声明参数，
    #             二者为盘中累积态——fills=当日成交列表，limit_consumption=限额使用情况，
    #             由 §3.13 intraday_risk_loop 返回的 IntradayResult 产出，盘后审计消费。
    #             v1.30.2 补：§3.13 已补齐产出点，此处接收其 return 值）
    # v1.31.0 补（E6/E8 修复——var_cvar 产出方统一 + var_breach_state 传入）：
    #   var_cvar 由 36号 §3.1/§3.2 产出（VaR/ES 计算是 36号职责），经 RiskOrchestrator 传入本函数，
    #   不再在本函数内部调用 var_calculator.calculate()——消除"两文档都算 var_cvar"的产出方冲突。
    #   var_breach_state 由 36号 §3.15 VarBreachStateMachine 产出（36号 §3.19 盘前初始化加载状态机 →
    #   36号 §3.1/§3.2 计算后 transition() 产出 breach_state），经 RiskOrchestrator 传入本函数。
    #   跨文档契约对齐 36号 §3.17 衔接规则 2："§3.1/§3.2 → 35号 §3.10：盘前 VaR/ES 产出 var_cvar +
    #   breach_state → 喂入 35号 §3.10 drawdown_controller.evaluate(var_breach_state=breach_state)"。
    curve = capital_curve_manager.record(nav, realized_pnl)
    dd_info = drawdown_tracker.update(nav)  # DrawdownInfo(drawdown_pct, peak, recovered_pct)

    # ── 盘前：VaR/ES 已由 36号 §3.1/§3.2 产出（var_cvar 参数传入，G17 喂入 C 层）──
    # v1.31.0 改（E8 修复）：原伪代码在本函数内部调用 var_calculator.calculate() +
    #   tail_risk_monitor.assess() 计算 var_cvar，与 36号 §3.17 衔接规则 2"36号产出 var_cvar 喂入
    #   35号"冲突——两文档都声称自己是 var_cvar 的产出方。裁决：var_cvar 产出方统一为 36号
    #   §3.1/§3.2（VaR/ES 计算是 36号核心职责），本函数仅消费。MVP 编排器未建时由调用方
    #   手动编排：先调 36号 §3.1/§3.2 产出 var_cvar + var_breach_state，再传入本函数。
    # entry_var 持久化：当日盘前 VaR_95（var_cvar.var_95）作为 entry_var 保存到 state_store
    #   （§3.18 阶段 4b），供次日 §3.15 加载 + §3.16 回撤归因对比（current_var vs entry_var
    #   判断风险是否恶化，v1.28.0 补）。var_cvar 由 36号产出后，§3.18 阶段 4b 直接取 var_cvar.var_95。

    # ── 盘前：综合裁决（C 层取最严，乘性叠加 var_breach_state 折扣）──
    # v1.31.0 补（E6 修复——var_breach_state 传入 evaluate）：
    #   drawdown_controller.evaluate() 接受 var_breach_state 参数（36号 §3.15 定义），
    #   产出 var_breach_multiplier（NORMAL=1.0 / BREACHED=0.8 / RECOVERY=0.9），
    #   与 base_position_cap 乘性叠加得 effective_cap（对齐 §3.8 取最严原则，multiplier≤1 故乘性即最严）。
    #   原伪代码未传 var_breach_state → evaluate() 内 var_breach_multiplier 恒 1.0 →
    #   36号 §3.15 VarBreachStateMachine 协同逻辑完全失效（BREACHED 状态不产生额外 20% 折扣）。
    response = drawdown_controller.evaluate(
        drawdown_info=dd_info,
        var_cvar=var_cvar,
        strategy_pnls=strategy_pnls,
        black_swan=black_swan_detector.scan(),
        var_breach_state=var_breach_state,  # v1.31.0 补：36号 §3.15 BREACHED/RECOVERY 折扣
    )
    # response.position_cap / response.reduce_ratio / response.kill_switch_advised
    #   position_cap 已含 var_breach_state 乘性折扣（effective_cap = base_cap × multiplier）

    # ── 盘前：Kill Switch 检查（最高优先级，不可覆盖）──
    if response.kill_switch_advised:
        stop_loss.trigger_kill_switch(reason="drawdown_protocol", scope="all")
        # v1.30.4 补：Kill Switch 提前返回也携带产出（供 §3.13 盘中循环获知 kill_switch_advised=True）
        return DailyRiskResult(var_cvar=var_cvar, response=response, plan=None, audit=None)
        # 拒绝所有新开仓，仅允许平仓

    # ── 盘中：仓位裁决（乘性叠加 regime × drawdown × VaR）──
    plan = position_sizing_engine.size(PositionSizingInput(
        symbols=...,
        nav=nav,
        capital_curve_discount=curve.contraction_factor,  # B 层节流
        capital_curve_cap=curve.position_cap,              # B 层上限
        defensive_only=response.only_close,                 # C 层禁开仓
        var_95=var_cvar.var_95,                             # C4 约束
        cvar_95=var_cvar.cvar_95,                           # C5 约束
        market_regime=regime_shrinkage.regime,              # regime 层
    ))

    # ── 盘后：日终审计（daily_auditor 检查 Kill Switch 终态 + 限额合规）──
    audit = daily_auditor.audit(trade_date, positions, fills, limit_consumption)
    # checklist 第 4 项：Kill Switch 终态 == CLOSED；第 5 项：数据完整性

    # v1.30.4 补：返回日度风控结果，供下游消费（交接链 1/2/4/5 根因修复）
    # 交接链 2: response → §3.13 盘中循环（kill_switch_advised 约束；position_cap 见 §3.13 A3 修复）
    # 交接链 4: var_cvar.var_95 → §3.16 回撤归因（current_var）+ var_cvar → §3.18 持久化（entry_var 快照）
    # v1.30.6 补（A1 消费方澄清——原 plan/audit 两字段无下游消费方）：
    # 交接链 plan: plan → 编排器（RiskOrchestrator §6.5）→ execution_broker 执行盘前仓位裁决。
    #   非 §3.13 盘中循环消费（盘中是监控+熔断，不执行仓位计划）。MVP 编排器未建时由
    #   daily_risk_loop 调用方直接传给 execution_broker。Kill Switch 提前返回时 plan=None。
    # 交接链 audit: audit → §3.18 postmarket_persist(audit=...) 阶段 0 审计门控（v1.30.6 补），
    #   audit.passed=False 时不持久化当日状态。Kill Switch 提前返回时 audit=None（未执行审计）。
    return DailyRiskResult(var_cvar=var_cvar, response=response, plan=plan, audit=audit)
```

**编排责任归属**（待裁定 §6.5）：当前由上游 `default_risk_manager_orchestrator` 部分承载。建议第二阶段建 `RiskOrchestrator` 统一编排，避免调用方遗漏喂入某一层（如只喂 drawdown 忘喂 var_cvar，导致 C 层降级）。

### 3.11 恢复状态机形式化

**现状**：`DrawdownController` 用 `SystemicRiskLevel` 枚举（GREEN/YELLOW/ORANGE/RED/BLACK）表达级别，但**无持久化状态机**——每次 `evaluate()` 重新计算级别，不记忆上一态，无转换守卫（如"RED 必须经过 RECOVERY 才能回 GREEN"）。

**目标状态机**（参考 [nexusfi 2026-06](https://nexusfi.com/a/automation/automated-risk-controls) 5 态确定性转换 + [completetradersedge 2026-04](https://completetradersedge.com/drawdown-protocol-traders/) Red→Amber→Green 不可跳级）：

```
            ┌──────────── 回撤加深（单调升级）─────────→
            │                                           │
   ┌────────┴────────┐  ┌────────┐  ┌────────────────┐ │  ┌────────┐  ┌──────────┐
   │ NORMAL (GREEN)  │→│ WARN   │→│ DANGER(ORANGE)  │─┼→│ CRISIS │→│ KILL(BLACK)│
   │   仓位 100%     │  │  80%   │  │     50%         │ │  │  30%   │  │  0% 全清  │
   └────────┬────────┘  └───┬────┘  └───────┬────────┘ │  └───┬────┘  └─────┬────┘
            ↑                │               │          │      │             │
            │   ┌────────────┴───────────────┘          │      │             │
            │   ↓  回撤企稳 50%                        │      │             │
            │ ┌──────────┐  创新高                      │      │             │
            └─┤ RECOVERY │←────────────────────────────┘      │             │
              │ 仓位阶梯  │       人工复位                      │             │
              │25→50→75% │←────────────────────────────────────┘             │
              └────┬─────┘                                                    │
                   └────────────── 人工复位 + 持仓清零确认 ────────────────────┘
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
| RECOVERY | drawdown > 15%（恢复期二次回撤超 CRISIS 阈值）| KILL（仅阶梯耗尽 step<0）/ RECOVERY retreat（阶梯未耗尽 step≥0）| — | v1.30.4 补（交接链 7）；v1.30.6 修（C1 表/码分裂 MAJOR）：§3.14 代码实际为分级保护——先 retreat_recovery_step 回退一级，仅 recovery_step<0（阶梯 0 再回退→耗尽）才转 KILL；原表声明"无条件 KILL"与代码不符，给恢复期单日波动留缓冲。行为差异：step=2 时需连续 3 日 dd>15% 才到 KILL（2→1→0→-1），非单次即 KILL |
| RECOVERY | drawdown > 10%（恢复期回撤加深超 DANGER 阈值）| RECOVERY（retreat_recovery_step，仅 step>0）/ 无动作（step=0 已到最低阶梯）| — | v1.30.4 补；v1.30.6 修（C1 MINOR）：§3.14 代码有 `if recovery_step > 0` 守卫，step=0 时 10-15% 区间不回退（已到最低 25% 阶梯无法再退）也不 KILL（未到 15%）——此区间在 step=0 为保护矩阵空档，由 freeze(>5%) 兜底；原表声明"无条件 retreat"未注明守卫 |
| RECOVERY | drawdown > 5%（恢复期回撤加深超 WARN 阈值）| RECOVERY（freeze 5 日）| — | v1.30.4 补：§3.14 恢复期轻度回撤冻结阶梯 5 日，不退级。此规则无 step 守卫，全阶梯生效（含 step=0），是 step=0 时 5-15% 区间的唯一保护 |
| 任意态 | 多源触发取最严 | 最高态 | — | [nexusfi](https://nexusfi.com/a/automation/automated-risk-controls)："the most severe state wins. Always." |

> **降级/恢复规则**（§3.20 形式化）：升级触发阈值与降级恢复阈值**不对称**（hysteresis 双阈值）——恢复阈值取触发阈值的 50%（半阈值）+ 持续时间门控（min_hold 5/10/20 交易日）+ 毕业准则（连续盈利日 + 10 笔期望 ≥ 0.3R + 合规率 ≥ 80%）。避免状态机在临界阈值附近 thrashing（反复触发/恢复）。详见 §3.20 回撤状态滞后-恢复双阈值。

**代码差距**（待施工 §6.6）：
1. **无状态持久化**——级别每次重算，无"上一态"记忆，无法判断"是否经过 RECOVERY"
2. **无转换守卫**——RECOVERY 可直接跳回 NORMAL（跳过阶梯），与 §3.4 `recovery_factor` 阶梯冲突
3. **无"不可跳级"约束**——CRISIS 回 NORMAL 无强制经过 RECOVERY，存在"刚 CRISIS 立即满仓"风险
4. **无 hysteresis 双阈值**（§3.20 新增）——降级用与升级相同的阈值，临界态 thrashing 风险；需 §3.20 的半阈值 + min_hold + 毕业准则三重守卫

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
    """盘中实时风控循环：每 N 秒轮询一次，检测单日亏损熔断 + Kill Switch 状态。
    
    Args:
        trade_date: 交易日期（v1.30.2 修：原伪代码 broker.get_realized_pnl(today) 引用
            未声明的 today，补 trade_date 参数，与 §3.10/§3.12 同口径）
        market_open / market_close: 盘中起止时间
        opening_nav: 当日开盘 NAV（§3.15 盘前初始化产出，单日亏损熔断基准）
        strategy_states: 各策略当日状态 dict {strat_id: StrategyState(opening_nav, ...)}
            （v1.30.0 补：原伪代码 strategy_pnls_today 未定义，改为显式参数传入）
        response: §3.10 DailyRiskResult.response（v1.30.4 补：盘前综合裁决产出，
            含 position_cap / kill_switch_advised，作为盘中仓位约束的初始边界）
    
    A 股 T+1 约束：盘中无法反转昨日买入，最坏只能"禁止新开仓 + 信号化减仓建议"
    （持仓只能在次日卖出），故盘中熔断动作受限。
    
    Returns:
        IntradayResult(fills, limit_consumption): 盘中累积的成交列表 + 限额使用情况，
        供 §3.10 盘后审计消费（v1.30.2 补：§3.10 声明 fills/limit_consumption "由盘中
        阶段产出"，原伪代码无产出点→交接断裂，本函数补产出）
    """
    # ── 盘中累积态初始化（§3.10 盘后审计的消费对象，v1.30.2 补）──
    fills = []                  # 当日成交列表，盘中逐笔累积
    limit_consumption = LimitConsumption()  # 限额使用情况（A 股 2026 新规：每秒15笔/撤单率15%）
    
    # v1.30.4 补：盘前裁决约束传入盘中（交接链 2 修复——§3.10 DailyRiskResult.response → §3.13）
    if response and response.kill_switch_advised:
        risk_validator.enforce_kill_switch_closed()  # 盘前已触发 Kill Switch，盘中保持

    # v1.30.6 补（A3 修复——position_cap 断裂：原 docstring 声称消费 position_cap 但函数体
    # 仅引用 kill_switch_advised，position_cap 从未被读取→交接链 2 只闭合一半）
    # 盘前综合裁决产出的 position_cap（如 0.8=减仓 20%）作为盘中仓位约束的初始边界，
    # 传给 position_sizing_engine 限制盘中新开仓上限。盘中回撤重算若触发更严约束
    # （如 EMERGENCY → set_emergency_halt）则取最严覆盖（position_sizing_engine 内部 max 约束）。
    if response and response.position_cap is not None:
        position_sizing_engine.apply_premarket_cap(response.position_cap)

    poll_interval = 30  # 秒，A 股 Level-1 行情 3 秒/笔，30 秒足够
    while market_open <= now < market_close:
        # ── 1. 拉取实时未实现 PnL + 累积当日成交 ──
        unrealized = broker.get_unrealized_pnl()
        realized_today = broker.get_realized_pnl(trade_date)  # v1.30.2 修：today → trade_date
        daily_pnl = unrealized + realized_today
        
        # 累积新成交（自上次轮询以来的 fill 事件，供 §3.10 盘后审计，v1.30.2 补）
        new_fills = broker.get_fills_since(last_poll_time)
        fills.extend(new_fills)
        limit_consumption.update(new_fills)  # 更新笔数/撤单率/限额使用
        nav = capital_curve_manager.current_nav + daily_pnl

        # ── 2. 单日亏损熔断（§3.6 组合 -4% / 单策略 -5%）──
        if daily_pnl_check(daily_pnl, loss_limit=-0.04 * opening_nav):
            # 组合单日 -4% → 暂停新开仓（A 股 T+1 无法强平昨日仓）
            risk_validator.set_daily_loss_halt(scope="all")
            alert("DAILY_LOSS 组合 -4%", severity=CRITICAL)
        
        # 按策略分别检测（v1.30.0 修：strategy_states 显式参数替代未定义的 strategy_pnls_today）
        strategy_pnls_today = broker.get_strategy_pnls_today()  # 按 strategy_id 分组的当日 PnL
        for strat_id, strat_state in strategy_states.items():
            pnl = strategy_pnls_today.get(strat_id, 0.0)
            if daily_pnl_check(pnl, loss_limit=-0.05 * strat_state.opening_nav):
                # 单策略单日 -5% → 该策略暂停
                risk_validator.set_daily_loss_halt(scope=strat_id)
                alert(f"DAILY_LOSS 策略 {strat_id} -5%", severity=WARNING)

        # ── 3. 盘中回撤重算（高频更新 drawdown_tracker）──
        dd_info = drawdown_tracker.update(nav)  # 用含浮盈的 nav
        if dd_info.alert_level == EMERGENCY:  # 15% 回撤
            # A 股 T+1：无法强平昨日新买，但禁止新开仓
            risk_validator.set_emergency_halt(scope="all")
            # v1.30.6 补（B3）：收盘前 5 分钟强制检查——14:55 后检测到 EMERGENCY
            # 则在 14:57 收盘集合竞价提交减仓单（可卖既有持仓），非一味推迟 next_open。
            # 原代码统一 queue_opening_reduce("next_open")→放弃 14:57 集合竞价减仓机会，
            # 过度保守。A 股 T+1 虽无法强平当日新买，但可减仓既有持仓（收盘集合竞价可卖）。
            from datetime import timedelta
            if now >= market_close - timedelta(minutes=5):  # 14:55 后（收盘前 5 分钟）
                position_sizing_engine.queue_auction_reduce("closing_auction")  # 14:57 集合竞价减仓
                alert("收盘前 EMERGENCY 回撤，14:57 收盘集合竞价减仓", CRITICAL)
            else:
                position_sizing_engine.queue_opening_reduce("next_open")  # 非收盘前→次日开盘减仓

        # ── 4. Kill Switch 状态轮询（防 Ghost Position，§3.5.1）──
        if risk_validator.kill_switch == CLOSED:
            # v1.30.2 修：strategy_state 未定义——strategy_states 是 dict {strat_id: StrategyState}，
            # detect_ghost_positions 需"策略认为的持仓"，聚合各策略预期持仓与 broker 实际持仓对比
            expected_holdings = aggregate_expected_holdings(strategy_states)
            ghosts = detect_ghost_positions(broker.get_holdings(), expected_holdings)
            if ghosts:
                alert(f"Ghost Position 检测到: {ghosts}", severity=EMERGENCY)
                # 不自动强平（A 股 T+1 + 可能误判），人工介入

        # ── 5. 盘中 VaR/ES 重算触发（与 36号 §3.12 协同，v1.31.0 补 E5/A2 修复）──
        # v1.31.0 补（E5/A2 修复——原 §3.13 未调用 36号 §3.12 intraday_var_recalc）：
        #   §3.17 总览规则 4 声明"盘中回撤循环检测到'日内突破盘前 VaR'时，触发 VaR 重算"，
        #   但原 §3.13 伪代码仅调用 drawdown_tracker.update(nav)，从未调用 36号 §3.12
        #   intraday_var_recalc()——§3.17 声明的协同逻辑在 §3.13 完全未实现→断裂。
        #   修复：在回撤重算后，调用 36号 §3.12 intraday_var_recalc_trigger() 检测 7 条触发条件，
        #   若触发则调用 intraday_var_recalc() 重算 VaR/ES，用返回的 IntradayVarResult 重新裁决。
        #   跨文档契约对齐 36号 §3.12："35号 §3.13 intraday_risk_loop 检测到触发条件后调用本函数"。
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
            # 取最严：新 response.position_cap 更低时覆盖盘前 response（对齐 §3.8 取最严原则）
            if new_response.position_cap < response.position_cap:
                response = new_response
                position_sizing_engine.apply_intraday_recalc(response)  # 应用更严约束
                alert(f"盘中 VaR 重算触发更严裁决: cap={response.position_cap}", WARNING)
            # 若 intraday_var_result.significant_change → 记录供日终回测分析（36号 §3.12 已记录日志）

        last_poll_time = now  # v1.30.2 补：记录本次轮询时间，供下轮 get_fills_since
        sleep(poll_interval)

    # ── 收盘后：交出盘中累积态，由 §3.10 日度循环的盘后审计接管（v1.30.2 补）──
    # fills / limit_consumption 是 §3.10 daily_risk_loop(audit=...) 的输入，
    # 原伪代码 §3.10 声明"由盘中阶段产出"但 §3.13 无产出点→交接断裂，此处补齐
    return IntradayResult(fills=fills, limit_consumption=limit_consumption)
```

**裁决**：盘中循环暂缓为 §6.5 编排器的一部分。理由：① 当前系统以日度决策为主（盘前选股+盘后审计），盘中仅执行已定计划；② A 股 T+1 下盘中熔断动作受限（无法强平昨日仓），价值低于期货市场；③ 但**单日 -4% 告警**必须盘中触发（不能等盘后），故最小实现是盘中每 30 秒拉一次未实现 PnL，超阈值即告警 + 禁新开仓。完整循环待 RiskOrchestrator（§6.5）施工时一并落地。

### 3.14 Kill Switch 复位 → RECOVERY → NORMAL 端到端流程

**问题**：§3.4 讲恢复机制（两段恢复 + recovery_factor 阶梯），§3.11 讲状态机（5 态转换），但缺乏"Kill Switch 触发后，从人工复位到完全恢复 NORMAL"的端到端施工流程。当前代码 `reset_kill_switch` 仅清状态，无 RECOVERY 阶梯守卫（§3.11 代码差距 2）。

**端到端流程伪代码**（对照 §3.11 状态机 KILL→RECOVERY→NORMAL 转换）：

```python
def kill_switch_recovery_flow():
    """Kill Switch 触发后的完整恢复流程：人工复位 → RECOVERY 阶梯 → 创新高回 NORMAL。
    
    前置：Kill Switch 已触发（§3.5），持仓已清零（§3.5.1 Ghost 检测通过），
          requires_manual_reset == True。
    """
    # ── 阶段 0：人工复位（KILL → RECOVERY 入口）──
    # 人工确认：① 持仓已清零 ② 根因已分析 ③ 决定恢复
    confirmation = ResetConfirmation(
        confirmed_by="owner",
        override_reason="root_cause_analyzed_and_fixed",
        holdings_verified_zero=True,       # ① §3.5.1 Ghost 检测：持仓已清零
        orders_cancelled_verified=True,    # ② v1.30.6 补（B1）：所有挂单已撤（防复位后意外成交）
        new_open_locked_verified=True,     # ③ v1.30.6 补（B1）：锁新开仓已生效（RECOVERY 25% 上限 ≠ 禁开仓）
    )
    # v1.30.6 补（B1）：Kill Switch 执行 = 平仓 + 撤单 + 锁新开仓（§3.5 三项动作），
    # 复位确认须校验全部 3 项。原仅校验持仓清零（1/3）→ 可能残留未撤挂单复位后意外成交，
    # 或锁新开仓未生效即复位→实际未完成 Kill Switch 全部动作。
    if not confirmation.holdings_verified_zero:
        raise RefuseReset("持仓未清零，存在 Ghost Position，拒绝复位")
    if not confirmation.orders_cancelled_verified:
        raise RefuseReset("存在未撤挂单，复位后可能意外成交，拒绝复位")
    if not confirmation.new_open_locked_verified:
        raise RefuseReset("锁新开仓状态未确认，拒绝复位")

    # v1.30.6 补（C2）：KILL→RECOVERY→KILL 循环守卫——复位次数上限 + 冷却期 + 升级机制。
    # 防止人工未修复根因即反复复位→系统反复 KILL→RECOVERY→KILL 循环（非死锁但消耗资金 + 风险暴露）。
    # 设计依据：[Tidball 2026-05] Kill Switch Framework 复位治理 + [Iyer 2026-01] BOCPD 实践
    # 调参经验——频繁复位说明根因未消除，应升级而非允许重复尝试。
    reset_history = state_store.load_reset_history(window=20)  # 近 20 交易日复位记录
    reset_count = len(reset_history)
    total_resets = state_store.load_total_reset_count()        # 累计复位总次数
    MAX_RESETS_PER_WINDOW = 3       # 20 日内最多复位 3 次
    COOLDOWN_DAYS = 3               # 复位后强制冷却 3 交易日（期间保持 KILL 不允许复位）
    PERMANENT_LOCK_THRESHOLD = 5    # 累计 5 次复位→永久锁定，需外部根因验证才能解锁

    # 升级机制：累计复位超阈值→永久锁定（最高级保护，防止无限循环）
    if total_resets >= PERMANENT_LOCK_THRESHOLD:
        daily_auditor.log_permanent_lock(trade_date, total_resets=total_resets)
        raise RefuseReset(f"累计复位 {total_resets} 次超阈值 {PERMANENT_LOCK_THRESHOLD}，"
                          f"永久锁定，需外部根因验证 + 人工解锁")

    # 冷却期：距上次 KILL 不足冷却期→拒绝复位（防刚 KILL 立即复位）
    if reset_history and (trade_date - reset_history[-1].date).days < COOLDOWN_DAYS:
        raise RefuseReset(f"距上次 KILL 不足 {COOLDOWN_DAYS} 交易日冷却期，拒绝复位")

    # 次数上限：窗口内复位超限→拒绝复位（防短期内反复 KILL/复位）
    if reset_count >= MAX_RESETS_PER_WINDOW:
        raise RefuseReset(f"近 20 日复位 {reset_count} 次超上限 {MAX_RESETS_PER_WINDOW}，"
                          f"拒绝复位，需根因验证")

    state_store.record_reset(trade_date, reason=confirmation.override_reason)
    state_machine.transition(KILL, RECOVERY, confirmation)
    # 进入 RECOVERY：recovery_factor = 0.25（仓位上限 25%）

    # ── 阶段 1：RECOVERY 阶梯恢复（25% → 50% → 75% → 100%）──
    # 每级需满足：① recovered_pct 达标 ② 连续 N 个盈利日（TradeZella 三级恢复协议）
    while state_machine.current == RECOVERY:
        dd_info = drawdown_tracker.update(current_nav)
        
        if dd_info.recovered_pct >= 0.50 and state_machine.recovery_step == 0:
            # 回撤从峰值恢复 50% → 阶梯 1（25% → 50%）
            state_machine.advance_recovery_step()  # recovery_factor 0.25 → 0.50
            daily_auditor.log_recovery_step(1, dd_info)
        
        elif dd_info.recovered_pct >= 0.75 and state_machine.recovery_step == 1:
            state_machine.advance_recovery_step()  # 0.50 → 0.75
            daily_auditor.log_recovery_step(2, dd_info)
        
        elif dd_info.recovered_pct >= 1.0 - 1e-6 and state_machine.recovery_step == 2:
            # 创新高（recovered_pct ≈ 1.0，用 epsilon 防浮点误差，v1.29.0 修）
            # 注意：不用 drawdown_pct == 0 浮点等值检查（浮点精度不可靠）
            # §3.11 状态机：RECOVERY → NORMAL
            state_machine.transition(RECOVERY, NORMAL, reason="new_high_watermark")
            # expansion_factor 保留（§3.8 盈利扩张累计）
            daily_auditor.log_full_recovery(dd_info)
            break

        # ── 阶梯期回撤加深保护：RECOVERY 期间再次回撤 → 分级响应（v1.29.0 修）──
        # 原 v1.28.0 仅 >15% 触发回退，5-15% 空档无保护——RECOVERY 期间回撤 10% 不触发任何动作
        # 修复：三级分级保护，对齐 §3.11 状态机 WARN/DANGER/CRISIS 阈值
        dd_abs = abs(dd_info.drawdown_pct)  # drawdown_pct ≤ 0，取绝对值
        if dd_abs > 0.15:  # CRISIS 阈值 → 阶梯耗尽，回 KILL
            state_machine.retreat_recovery_step()  # 阶梯回退一级
            if state_machine.recovery_step < 0:
                # 阶梯耗尽 → 回 KILL
                state_machine.transition(RECOVERY, KILL, reason="relapse_during_recovery")
                alert("恢复期二次回撤 >15%，Kill Switch 重触发", CRITICAL)
                return  # 等待下一次人工复位
        elif dd_abs > 0.10:  # DANGER 阈值 → 回退一级阶梯
            if state_machine.recovery_step > 0:
                state_machine.retreat_recovery_step()
                daily_auditor.log_recovery_retreat(
                    reason="drawdown_10pct_during_recovery",
                    new_step=state_machine.recovery_step,
                )
                alert(f"恢复期回撤 >10%，阶梯回退至 {state_machine.recovery_step}", WARNING)
        elif dd_abs > 0.05:  # WARN 阈值 → 暂停阶梯升级（不回退，但冻结升级 5 日）
            state_machine.freeze_recovery_progression(days=5)
            daily_auditor.log_recovery_freeze(reason="drawdown_5pct_during_recovery")
        
        wait_next_trading_day()

    # ── 阶段 2：NORMAL 正常运行 ──
    # expansion_factor 保留（§3.8），recovery_factor = 1.0
    risk_validator.clear_recovery_mode()
```

**代码差距**（待施工 §6.6）：
1. **无 `state_machine` 对象**——当前 `DrawdownController` 无持久化状态，`reset_kill_switch` 仅清 Kill Switch 标志，不进入 RECOVERY 态
2. **无 `recovery_step` 阶梯计数器**——`recovery_factor`（0.25→0.50→0.75→1.0）虽在 `_evaluate_recovery` 中按 `recovered_pct` 计算，但无"阶梯不可跳级"守卫（§3.11 代码差距 2）
3. **无"恢复期回撤加深保护"**——RECOVERY 期间再次回撤应回退阶梯或回 KILL，当前代码无此逻辑
4. **无 `ResetConfirmation.holdings_verified_zero`**——`reset_kill_switch` 不强制验证持仓清零，存在 Ghost Position 复位风险（§3.5.1）

> **裁决**：端到端流程暂缓为 §6.6 DrawdownStateMachine 施工的输入规约。当前 MVP 用人工复位 + `recovery_factor` 阶梯（数值上实现，无状态机守卫）足够；完整流程待持久化状态机落地。最小补丁：`reset_kill_switch` 增加 `holdings_verified_zero` 必填校验（防 Ghost Position 复位）。

### 3.15 盘前初始化与跨重启状态恢复

**问题**：§3.10-§3.14 覆盖了日度循环/盘中循环/复位流程，但缺**系统启动环节**——每个交易日盘前如何加载持久化状态、与 broker 持仓核对、校准各模块基线。这是 nexusfi 2026-06 "Reconnection and State Recovery" 章节专门强调的失败域：系统重启后若不恢复 DrawdownStateMachine 持久化状态，会丢失"上一态是 RECOVERY 还是 NORMAL"的记忆，导致 §3.11 转换守卫失效（§3.11 代码差距 1）。

**盘前初始化伪代码**（对照 §3.11 状态机 + §3.5.1 Ghost 检测）：

```python
def premarket_initialization(trade_date):
    """盘前初始化：加载持久化状态 → broker 持仓核对 → 基线校准 → Kill Switch 状态确认。
    
    顺序不可调换：先核对持仓（防 Ghost），再加载状态机（防基于错误持仓的状态恢复），
    最后校准基线（peak NAV / 回撤窗口）。
    """
    # ── 阶段 1：broker 持仓核对（防 Ghost Position，§3.5.1）──
    broker_holdings = broker.get_holdings()  # 实盘真实持仓
    strategy_state = state_store.load_strategy_state()  # 策略认为的持仓状态（None=冷启动/首次）

    # v1.30.6 补（A5 级联修复）：冷启动时 strategy_state 为 None（§3.18 未持久化或首次启动），
    # detect_ghost_positions(broker_holdings, None) 会因 NoneType 无 .get() 崩溃。
    # 守卫：None 时若 broker 有持仓则全部视为 Ghost（无策略记录却有持仓→来源不明），
    # 空仓则正常通过（冷启动无持仓是正常态）。
    if strategy_state is None:
        ghosts = list(broker_holdings.keys()) if broker_holdings else []
    else:
        ghosts = detect_ghost_positions(broker_holdings, strategy_state)
    if ghosts:
        alert(f"盘前 Ghost Position 检出: {ghosts}", severity=EMERGENCY)
        # Kill Switch == CLOSED 但 broker 有持仓 → 拒绝开新仓 + 人工介入
        # 不自动强平（A 股 T+1 + 可能误判）
        risk_validator.set_emergency_halt(scope="all")
        return RefuseStart("存在 Ghost Position，拒绝启动，需人工清零持仓")
    
    # ── 阶段 2：加载 DrawdownStateMachine 持久化状态（§3.11）──
    # 恢复"上一态"记忆，确保转换守卫生效（RECOVERY 不可跳级回 NORMAL）
    persisted_state = state_store.load_drawdown_state(trade_date)
    if persisted_state is None:
        # 首次启动或状态丢失 → 默认 NORMAL（保守：不假设上次在 RECOVERY）
        state_machine = DrawdownStateMachine(current=NORMAL, recovery_step=0)
        daily_auditor.log_state_recovery("cold_start_default_NORMAL")
    else:
        state_machine = DrawdownStateMachine(
            current=persisted_state.current,          # NORMAL/WARN/.../KILL/RECOVERY
            recovery_step=persisted_state.recovery_step,  # 0/1/2（阶梯计数器）
            last_transition=persisted_state.last_transition,
        )
        daily_auditor.log_state_recovery(f"restored_{persisted_state.current}")
    
    # Kill Switch 终态校验：若上次收盘 == CLOSED，盘前必须保持 CLOSED（人工复位才能解除）
    if persisted_state and persisted_state.kill_switch == CLOSED:
        risk_validator.enforce_kill_switch_closed()
        alert("Kill Switch 仍 CLOSED，盘前禁开仓，等待人工复位", WARNING)
    
    # ── 阶段 3：基线校准（peak NAV / 回撤窗口 / 入场 NAV）──
    # peak NAV 单调非减（§3.8），从持久化加载，不可从当日重算
    peak_nav = state_store.load_peak_nav()
    capital_curve_manager.restore_peak(peak_nav)

    # 回撤窗口：恢复历史净值序列（drawdown_tracker 需滚动窗口算 drawdown_pct）
    nav_history = state_store.load_nav_history(window=252)  # 请求 1 年窗口
    # 冷启动守卫（v1.29.0 补）：新系统历史不足 252 天时，用实际可用天数
    # drawdown_tracker 需 ≥ min_history=30 日才能计算 drawdown_pct（对齐 36号 §2.3 var_calculator min_history=30）
    MIN_HISTORY = 30  # 最小回撤计算窗口
    if len(nav_history) < MIN_HISTORY:
        # 历史不足 → 回撤计算不可靠，进入"保守冷启动"模式
        # 保守措施：① 强制 NORMAL 状态（不假设上次在 RECOVERY）② position_cap 降至 50%（保守上限）
        # ③ 日终审计标记 COLD_START_INSUFFICIENT_HISTORY 供人工复盘
        daily_auditor.log_cold_start_insufficient_history(
            available=len(nav_history), required=MIN_HISTORY,
        )
        alert(
            f"nav_history 不足 {MIN_HISTORY} 日（实际 {len(nav_history)}），"
            f"进入保守冷启动模式（position_cap 50%）",
            WARNING,
        )
        state_machine.force_conservative_mode(position_cap=0.50)
        # drawdown_tracker 用可用数据初始化（drawdown_pct 可能不准，但 peak NAV 仍准确）
        drawdown_tracker.restore(nav_history) if nav_history else drawdown_tracker.reset(peak_nav)
    else:
        drawdown_tracker.restore(nav_history)

    # 入场 NAV（日度熔断 §3.6 的基准）
    opening_nav = capital_curve_manager.current_nav

    # 入场 VaR（§3.16 回撤归因基准：current_var vs entry_var 判断风险恶化，v1.28.0 补）
    # entry_var = 前一交易日盘前 VaR_95 快照（§3.18 阶段 4b 持久化），供 §3.16 归因对比
    # None=首次启动/前日未持久化 → §3.16 风险恶化检测跳过（entry_var is None 时 §3.16 跳过分支 0）
    entry_var = state_store.load_entry_var()
    daily_auditor.log_baseline(peak_nav=peak_nav, opening_nav=opening_nav, entry_var=entry_var)
    
    # ── 阶段 4：Kill Switch 执行通道健康检查（§3.5.1 L1 层）──
    # 确认 stop_loss.trigger_kill_switch 与 broker 连接可用，避免触发时才发现连接断
    if not stop_loss.health_check():
        alert("Kill Switch 执行通道不健康（broker 连接异常），拒绝启动", CRITICAL)
        return RefuseStart("执行通道不健康")
    
    # v1.30.4 补：加载前日归因结果（交接链 5 修复——§3.18 save_attribution_result 的配对 load）
    prev_attribution = state_store.load_attribution_result(trade_date - 1)  # 前日归因结果
    # 消费方式（v1.30.5 补——自洽性审查发现 prev_attribution 加载后无消费方→死数据修复）：
    # 由编排器（RiskOrchestrator §6.5）传入 §3.10 drawdown_controller.evaluate() 的 context 参数，
    # 供综合裁决参考（如前日归因为"系统性回撤"→drawdown_controller 更保守判定）。
    # None=前日未持久化/首次启动，此时 drawdown_controller 无前日归因上下文（正常降级）

    # v1.30.4 补：entry_var 补入返回值（§3.16 回撤归因消费 entry_var 做风险恶化检测，
    # 原 InitializationResult 未携带→交接链 4 断裂，§3.16 entry_var 恒 None→分支 0 永跳过）
    return InitializationResult(state_machine=state_machine, opening_nav=opening_nav,
                                entry_var=entry_var, prev_attribution=prev_attribution)
```

**代码差距**（待施工 §6.6/§6.11）：
1. **无 `state_store` 持久化层**——当前 `DrawdownController` / `DrawdownStateMachine`（未建）/ `capital_curve_manager` 均内存态，重启即丢失 peak NAV / 状态机态 / recovery_step
2. **无 `detect_ghost_positions` 盘前调用**——§3.5.1 Ghost 检测当前仅在盘中循环（§3.13）和复位流程（§3.14）调用，盘前未调用
3. **无 `stop_loss.health_check`**——执行通道健康检查缺失，存在"触发时才发现连接断"风险

> **裁决**：盘前初始化暂缓为 §6.6（状态机持久化）+ §6.11（Ghost 检测）施工的输入规约。最小补丁（立即可做）：① `capital_curve_manager.peak` 与 `drawdown_tracker` 窗口持久化到 DB（已有 `daily_auditor` 持久化基础设施可复用）；② 盘前调用 `detect_ghost_positions`（函数已写在 §3.5.1，只需在启动序列接入）。完整 `state_store` + `DrawdownStateMachine` 持久化待 §6.6。

### 3.16 回撤归因端到端流程

**问题**：§3.3 讲单策略 vs 组合分层，§3.12 讲统计性 vs 行为性诊断，但缺"组合回撤发生后，如何归因到各策略/各因子"的端到端流程。`daily_auditor` 的 `AttributionBias`（预测因子占比 vs 实际占比）是工具，但无归因触发条件与响应分流。orstac 2026-03 的 correlation-aware 视角提示：高相关性回撤 = 系统性（全局收缩），低相关性回撤 = 策略特定（单策略收缩）——这是归因的关键判别维度。

**回撤归因伪代码**（对照 §3.3 分层 + §3.12 诊断 + §3.9 regime 协同 + §3.15/§3.18 entry_var 跨文档契约）：

```python
def drawdown_attribution_flow(dd_info, strategy_pnls, factor_decomposition,
                               entry_var=None, current_var=None,
                               strategy_pnls_history=None):
    """组合回撤触发后的归因流程：风险恶化 → 系统性 vs 策略特定 → 行为性 → regime 交叉。
    
    触发条件：drawdown_tracker WARNING（5%）及以上即触发归因（不只是 CRISIS 才归因）。
    输出：AttributionResult(systemic_pct, per_strategy_pct, root_cause, response_routing)
    
    Args:
        dd_info: DrawdownInfo(drawdown_pct, peak, recovered_pct)——§3.10 drawdown_tracker.update() 产出
        strategy_pnls: 各策略 PnL 列表（≥1 个策略）——§3.10 daily_risk_loop 参数 strategy_pnls 传入
        factor_decomposition: 因子分解（预测 vs 实际占比）——v1.30.4 补数据源说明（交接链 4 修复）：
            由 RiskOrchestrator（§6.5 待施工）从因子库 factor_registry 拉取当日因子暴露，
            与策略预期因子占比对比。MVP 阶段 factor_registry 未建时传 None→跳过因子归因分支
        entry_var: 前日盘前 VaR_95 快照（§3.15 InitializationResult.entry_var 产出，§3.18 阶段 4b 持久化，
            None=首次启动/前日未持久化。v1.30.4 修：原 InitializationResult 未携带→已修复）
        current_var: 当日盘前 VaR_95（§3.10 DailyRiskResult.var_cvar.var_95 产出，
            None=VaR 未计算时跳过恶化检测。v1.30.4 修：原 daily_risk_loop 无返回值→已修复）
        strategy_pnls_history: 各策略历史 PnL 序列（用于计算策略间相关系数矩阵，
            None=历史不足或首次运行，此时跳过相关性归因直接判为策略特定，
            v1.30.1 修：原伪代码引用 strategy_pnls_history 但未声明参数。
            v1.30.4 补数据源说明（交接链 4 修复）：由 RiskOrchestrator 从 PnL 数据库
            拉取过去 20 日各策略 PnL 序列。MVP 阶段历史不足 20 日时传 None→跳过相关性归因）
    """
    # ── 0. 风险恶化型归因（entry_var vs current_var，v1.29.0 补 §3.15/§3.18 跨文档契约）──
    # 若 entry_var 可用且 current_var 显著高于 entry_var → 持仓风险恶化（即便 NAV 未回撤）
    # 这是"前馈式"归因：不等 NAV 回撤触发，而是 VaR 恶化即减仓
    # 对齐 §3.19 Conformal Kelly "预测失准即减"的前馈风控边界
    if entry_var is not None and current_var is not None and entry_var > 0:
        var_deterioration_ratio = current_var / entry_var
        if var_deterioration_ratio > 1.5:
            # current_var 比 entry_var 高 50%+ → 风险显著恶化
            # 即便 dd_info.drawdown_pct 未达 WARNING，也触发"风险恶化型"减仓
            root_cause = "RISK_DETERIORATION_VAR_RATIO_{:.1f}".format(var_deterioration_ratio)
            response_routing = "RISK_BASED_REDUCTION"  # 按 var_deterioration_ratio 乘性减仓
            # 减仓幅度 = min(var_deterioration_ratio - 1.0, 0.5)，最高减 50%
            reduction_pct = min(var_deterioration_ratio - 1.0, 0.5)
            daily_auditor.log_risk_deterioration(
                entry_var=entry_var, current_var=current_var,
                ratio=var_deterioration_ratio, reduction_pct=reduction_pct,
            )
            return AttributionResult(
                systemic_pct=1.0,  # 风险恶化是组合级（VaR 是组合度量）
                per_strategy_contribution=None,
                root_cause=root_cause,
                response_routing=response_routing,
                attribution_bias=None,
                risk_deterioration_ratio=var_deterioration_ratio,
                recommended_reduction=reduction_pct,
            )
    
    # ── 常规归因：drawdown 达 WARNING 才进入 ──
    if abs(dd_info.drawdown_pct) < 0.05:  # 未达 WARNING（5%），不归因
        return None
    
    # ── 1. 策略间相关性归因（orstac correlation-aware）──
    # 单策略守卫：只有 1 个策略时无相关性矩阵，直接归为策略特定
    # 历史不足守卫：strategy_pnls_history is None 时跳过相关性归因（v1.30.1 补）
    per_strategy_contribution = {}
    if len(strategy_pnls) <= 1 or strategy_pnls_history is None:
        avg_corr = 0.0  # 单策略或历史不足 → 策略特定
        systemic_pct = 0.0
        root_cause = ("STRATEGY_SPECIFIC_SINGLE_STRATEGY" if len(strategy_pnls) <= 1
                      else "STRATEGY_SPECIFIC_INSUFFICIENT_HISTORY")
        per_strategy_contribution = {
            strategy_pnls[0].id: 1.0
        } if strategy_pnls else {}
    else:
        # 计算各策略 PnL 序列的两两相关系数矩阵
        corr_matrix = compute_correlation(strategy_pnls_history, window=20)
        avg_corr = mean(off_diagonal(corr_matrix))
        
        # 高平均相关性（>0.7）→ 系统性回撤（所有策略同步亏 = 市场级，非策略级）
        # 低平均相关性（<0.4）→ 策略特定回撤（个别策略独立亏）
        if avg_corr > 0.7:
            systemic_pct = 1.0  # 100% 系统性
            root_cause = "SYSTEMIC_HIGH_CORRELATION"
            # → 全局收缩（§3.3 组合层 capital_curve_manager + drawdown_controller systemic）
        elif avg_corr < 0.4:
            systemic_pct = 0.0  # 0% 系统性 = 策略特定
            root_cause = "STRATEGY_SPECIFIC_LOW_CORRELATION"
            # → 单策略收缩（§3.3 单策略层 Soft/Hard Stop）
        else:
            # 混合：按各策略贡献占比拆分（除零守卫）
            total_abs_dd = sum(abs(p.drawdown_pct) for p in strategy_pnls)
            if total_abs_dd > 1e-10:
                per_strategy_contribution = {
                    sid: abs(pnl.drawdown_pct) / total_abs_dd
                    for sid, pnl in strategy_pnls
                }
            else:
                per_strategy_contribution = {p.id: 0.0 for p in strategy_pnls}
            systemic_pct = avg_corr  # 近似
            root_cause = "MIXED_PARTIAL_SYSTEMIC"
    
    # ── 2. 因子归因（复用 daily_auditor AttributionBias）──
    # 预测因子贡献占比 vs 实际 PnL 因子占比 → 偏差大 = 行为性回撤（§3.12）
    attribution = daily_auditor.compute_attribution_bias(
        predicted_factor_pct=factor_decomposition.predicted,
        actual_factor_pct=factor_decomposition.actual,
    )
    if attribution.status == BIASED:
        # 行为性回撤：AI 执行偏差 → 停实盘 + 修正执行逻辑（§3.12）
        root_cause = "BEHAVIOURAL_ATTRIBUTION_BIAS"
        response_routing = "STOP_LIVE_AND_FIX_EXECUTION"
    elif root_cause.startswith("SYSTEMIC"):
        # 统计性 + 系统性 → 全局收缩
        response_routing = "GLOBAL_CONTRACTION"
    else:
        # 统计性 + 策略特定 → 单策略收缩
        response_routing = "PER_STRATEGY_CONTRACTION"
    
    # ── 3. regime 交叉验证（§3.9 正交协同）──
    # 若 regime 当前是 ACCEL_DECLINE/PANIC_CRASH → 系统性回撤与市场状态一致，属预期
    # 若 regime 是 CALM_BULL 但组合回撤 → 异常，归因为策略失效
    if regime_shrinkage.regime in (ACCEL_DECLINE, PANIC_CRASH, CRISIS):
        root_cause += "_REGIME_ALIGNED"  # 市场级回撤，预期内
    else:
        root_cause += "_REGIME_MISALIGNED"  # 市场平稳但组合亏 → 策略失效信号
    
    return AttributionResult(
        systemic_pct=systemic_pct,
        per_strategy_contribution=per_strategy_contribution,
        root_cause=root_cause,
        response_routing=response_routing,
        attribution_bias=attribution,
    )
```

**响应分流对照**（归因结果 → 响应动作）：

| 归因结果 | 响应动作 | 对应章节 |
|---|---|---|
| RISK_DETERIORATION（VaR 恶化 ratio > 1.5） | 按 var_deterioration_ratio 乘性减仓（最高 50%），不等 NAV 回撤触发 | §3.15/§3.18 entry_var 契约 + §3.19 前馈风控边界（v1.29.0 补） |
| SYSTEMIC + REGIME_ALIGNED + 统计性 | 全局收缩（capital_curve_manager + drawdown_controller systemic），继续执行 | §3.3 组合层 + §3.9 regime 协同 |
| SYSTEMIC + REGIME_MISALIGNED | 异常告警——市场平稳但组合亏，可能数据/执行问题 | daily_auditor 异常检测 |
| STRATEGY_SPECIFIC + 统计性 | 单策略 Soft/Hard Stop（§3.3），其他策略不受影响 | §3.3 单策略层 |
| BEHAVIOURAL（AttributionBias） | 停实盘 + 修正执行逻辑（§3.12 行为性回撤） | §3.12 诊断 |

> **裁决**：归因流程暂缓为 §6.7（回撤类型诊断）施工的输入规约。当前 MVP 用 §3.3 分层（单策略 Soft/Hard + 组合 systemic）+ §3.12 诊断矩阵（人工判读）足够；自动化归因（相关性矩阵 + 因子偏差 + regime 交叉）待 §6.7。最小补丁：`daily_auditor` 已有 `AttributionBias`，回撤 WARNING 触发时自动调用并记入日志，供人工复盘。

**扩展归因维度：六类风险失败机制**（[López de Prado & Fabozzi, JAM 2026](https://quantresearch.org/Publications.htm) "Rethinking Portfolio Risk: A Taxonomy for Asset Management"）：

> 严重损失通常来自六类风险失败机制的**复合效应**（而非单一波动率）。当前 §3.16 归因只覆盖了维度 ①+④，其余维度散布在项目其他文档中——六类框架的价值在于提供统一归因视图，将分散检测汇聚。

| # | 失败机制 | 内涵 | 当前覆盖 | 对应文档/模块 |
|---|---|---|---|---|
| ① | Statistical（统计性）| 样本偏差、过拟合、多重检验 | ✅ §3.12 统计性 vs 行为性诊断 | 本备忘 §3.12 |
| ② | Factor（因子）| 因子失效、拥挤、IC 衰减 | 🟧 25_multifactor IC 衰减监控 | G09 多因子策略 |
| ③ | Liquidity（流动性）| 滑点、冲击成本、流动性枯竭 | ✅ 37_liquidity_crisis_protocol | G18 流动性危机 |
| ④ | Model（模型）| 分布假设错误、regime 失配、参数漂移 | ✅ §3.16 regime 交叉验证 + 36号§3.9 回测 | 本备忘 + G17 |
| ⑤ | Governance（治理）| 权限错误、流程缺失、Kill Switch 失效 | ✅ §3.5 Kill Switch + daily_auditor | 本备忘 §3.5/§3.7 |
| ⑥ | Decision-infrastructure（决策基础设施）| 系统故障、数据错误、连接中断 | 🟧 55_monitoring_review 系统健康 | G26 监控告警 |

> **裁决**：六类框架作为 §3.16 归因的**扩展维度**暂缓（§6.16）。当前 MVP 用二分法（系统性/策略特定 × 统计性/行为性）足够；六类框架的价值在于实盘运行后做**复合归因**——当回撤发生时，逐类排查 ①-⑥ 是否触发，形成"回撤根因六维报告"。这比二分法更精细，但需六类检测模块全部 production 后才有意义（当前 ② 因子衰减监控 + ⑥ 系统健康待施工）。重评条件：25_multifactor IC 衰减监控 + 55_monitoring_review 系统健康均 production 后，将六类框架纳入 §6.7 归因流程作为扩展维度。

### 3.17 施工流程总览（6 流程闭环）

> **阅读指引**（v1.30.2 补）：本总览图引用 §3.18 盘后持久化（下一节详述）——总览先行建立整体认知，§3.18 随后补齐第 6 个流程环节的细节。6 流程闭环的完整定义需 §3.10-§3.16 + §3.18 全部读完方才闭合。另注：§3.20 Hysteresis（横切机制）+ §3.21 行业实证（案例背书）在 §3.19 审查之后追加，非独立流程环节，不影响本总览的 6 流程闭环完整性。

**问题**：§3.10-§3.18 共 8 个章节（§3.10 日度循环 / §3.11 状态机 / §3.12 诊断 / §3.13 盘中循环 / §3.14 复位 / §3.15 盘前初始化 / §3.16 归因 / §3.18 盘后持久化），其中 **6 个是独立流程环节**（§3.10/§3.13/§3.14/§3.15/§3.16/§3.18），**2 个是横切机制**（§3.11 状态机被 §3.14/§3.15/§3.18 引用、§3.12 诊断被 §3.16 引用，不独立调度），但缺一张总览图说明它们的时序关系与触发衔接，读者难以建立整体认知。

**6 流程闭环时序**（一个交易日的完整风控生命周期）：

```
┌─────────────────────────────────────────────────────────────────────┐
│  T-1 收盘后                                                          │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────────────┐      │
│  │ §3.10 日度   │ →  │ §3.16 回撤    │ →  │ §3.10 盘后审计     │      │
│  │ 循环·盘后段  │    │ 归因（若触发）│    │ daily_auditor      │      │
│  │ 更新净值曲线 │    │ 系统性/策略/  │    │ Kill Switch 终态 +  │      │
│  │ + 回撤 + VaR │    │ 行为性分流    │    │ 限额合规            │      │
│  └─────────────┘    └──────────────┘    └─────────┬──────────┘      │
│                                                    ↓                 │
│                                       ┌────────────────────┐        │
│                                       │ §3.18 盘后状态持久化 │        │
│                                       │ peak NAV→状态机→    │        │
│                                       │ nav_history→原子标记│        │
│                                       └─────────┬──────────┘        │
│                                                  │ 持久化状态        │
└──────────────────────────────────────────────────┼──────────────────┘
                                                   ↓
┌─────────────────────────────────────────────────────────────────────┐
│  T 盘前                                                              │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ §3.15 盘前初始化                                              │   │
│  │ broker 持仓核对（Ghost 检测）→ 加载状态机 → 基线校准 → 通道健康│   │
│  └──────────────────────────┬───────────────────────────────────┘   │
│                             ↓                                        │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ §3.10 日度循环·盘前段                                         │   │
│  │ 计算 VaR/ES → drawdown_controller 综合裁决 → 仓位裁决         │   │
│  └──────────────────────────┬───────────────────────────────────┘   │
└─────────────────────────────┼────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│  T 盘中（9:30-15:00）                                                │
│  ┌─────────────────────────┐    ┌────────────────────────────┐      │
│  │ §3.13 盘中实时风控循环   │ ←→ │ §3.14 Kill Switch 复位流程  │      │
│  │ 30 秒轮询：单日亏损熔断  │    │ （若 KILL 触发，人工复位后  │      │
│  │ + 回撤重算 + Ghost 轮询  │    │  进入 RECOVERY 阶梯）       │      │
│  └─────────────────────────┘    └────────────────────────────┘      │
│         ↓ 触发条件①（日内突破盘前 VaR）→ 联动                         │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ 36号 §3.12 盘中 VaR/ES 重算触发（1 分钟轮询，与回撤循环协同） │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
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

**问题**：§3.15 盘前初始化从 `state_store` 加载持久化状态（peak NAV / DrawdownStateMachine / nav_history / recovery_step），但缺**配对的盘后保存流程**——若无显式持久化，§3.15 的"加载"无源可载，跨重启状态丢失（§3.15 代码差距 1）。nexusfi 2026-06 "Reconnection and State Recovery" 强调：持久化与恢复是配对操作，缺一即状态机失效——盘前能恢复"上一态"的前提是盘后正确保存了"上一态"。

**盘后持久化伪代码**（对照 §3.15 加载顺序的逆序——先保存被依赖项，再保存依赖者，确保一致性快照）：

```python
def postmarket_persist(trade_date, state_machine, capital_curve, dd_tracker, var_cvar,
                       attribution_result=None, audit=None):
    """盘后状态持久化：审计门控 → 终态净值 → peak NAV → 状态机 → nav_history → 标记可加载。

    顺序与 §3.15 加载逆序：先保存依赖项（nav/peak），再保存依赖者（状态机/窗口）。
    原子性：全部写入成功才标记 trade_date 可加载，部分失败则次日 §3.15 冷启动默认 NORMAL。

    Args:
        var_cvar: 当日盘前计算的 VarCvarMetrics(var_95, cvar_95)（§3.10 产出），
            供阶段 4b 持久化 entry_var（v1.30.1 修：原伪代码引用 var_cvar 但未声明参数）
        attribution_result: §3.16 回撤归因结果（v1.30.4 补——交接链 5 修复，
            原 §3.18 无 save/§3.15 无 load→归因结果仅日志未结构化持久化→完全断裂）
        audit: §3.10 daily_auditor.audit() 产出的审计结果对象（v1.30.6 补——A1 修复，
            原签名不接收 audit 但阶段 0 注释声称"审计未通过不持久化"→空头声明。
            修复：补参数 + 阶段 0 实际检查 audit.passed。audit=None=MVP 编排器未接入
            审计门控，降级为无门控直接持久化，向后兼容）
    """
    # ── 阶段 0：审计门控（v1.30.6 补——A1 修复：原仅为注释无代码检查）──
    # §3.10 盘后段 daily_auditor.audit() 产出 audit，编排器（RiskOrchestrator §6.5）传入。
    # 审计未通过（Ghost Position 未清零 / Kill Switch 终态异常 / 限额超限 / 数据完整性失败）→
    # 不持久化当日状态，次日 §3.15 冷启动默认 NORMAL（保守：宁可丢状态不可存错误状态）
    if audit is not None and not audit.passed:
        daily_auditor.log_persist_skipped(trade_date, reason=audit.failure_reason)
        state_store.mark_persistable(trade_date, status="AUDIT_FAILED_SKIP")
        return  # 不进入阶段 1-5，当日状态不持久化
    # audit is None → MVP 阶段编排器未接入审计门控，降级为无门控直接持久化
    
    # ── 阶段 1：终态净值（当日收盘 NAV，含已实现 + 收盘 Mark-to-Market）──
    closing_nav = capital_curve.current_nav  # 已含当日 realized_pnl
    # A 股收盘后未实现 PnL 归零（T+1 持仓按收盘价 Mark），closing_nav 是确定值
    
    # ── 阶段 2：peak NAV（§3.8 单调非减，只在新高时更新）──
    old_peak = state_store.load_peak_nav()
    new_peak = max(old_peak, closing_nav)  # 单调非减不变量由 max() 保证
    state_store.save_peak_nav(new_peak)
    daily_auditor.log_peak_update(old=old_peak, new=new_peak, is_new_high=(new_peak > old_peak))
    
    # ── 阶段 3：DrawdownStateMachine 状态（§3.11 5 态 + recovery_step）──
    state_store.save_drawdown_state(trade_date, DrawdownStateSnapshot(
        current=state_machine.current,              # NORMAL/WARN/DANGER/CRISIS/KILL/RECOVERY
        recovery_step=state_machine.recovery_step,  # 0/1/2（阶梯计数器，§3.14）
        last_transition=state_machine.last_transition,
        kill_switch=risk_validator.kill_switch,     # OPEN/CLOSED（§3.5）
    ))
    
    # ── 阶段 4：nav_history 滚动窗口（§3.15 drawdown_tracker.restore 需 252 日窗口）──
    state_store.append_nav_history(trade_date, closing_nav)  # 追加当日
    state_store.trim_nav_history(window=252)  # 保留最近 252 日，防无限增长

    # ── 阶段 4b：entry VaR（§3.10 盘前 VaR_95 快照，供次日 §3.15 加载 + §3.16 回撤归因，v1.28.0 补）──
    # 当日盘前计算的 var_cvar.var_95 作为 entry_var 持久化，次日 §3.15 load_entry_var() 加载
    # 用途：§3.16 回撤归因对比 current_var vs entry_var——若 current_var >> entry_var 说明
    # 持仓风险已恶化（即便 NAV 未回撤），触发"风险恶化型归因"分流（减仓而非等回撤触发）
    state_store.save_entry_var(trade_date, var_cvar.var_95)
    daily_auditor.log_entry_var(trade_date, entry_var=var_cvar.var_95)

    # ── 阶段 4c：归因结果持久化（v1.30.4 补——交接链 5 修复：§3.16 AttributionResult 无 save/load 闭环）──
    # §3.17 总览声明"归因结果持久化供次日盘前加载"，但原 §3.18 无 save、§3.15 无 load→完全断裂
    # 修复：save_attribution_result + §3.15 load_attribution_result 配对，次日盘前可加载前日归因结果
    if attribution_result is not None:  # §3.16 回撤归因产出（正常交易日才有）
        state_store.save_attribution_result(trade_date, attribution_result)
        daily_auditor.log_attribution_persist(trade_date, root_cause=attribution_result.root_cause)

    # ── 阶段 4d：策略持仓状态持久化（v1.30.4 补——§3.15 load_strategy_state 的配对 save）──
    # §3.15 阶段 1 load_strategy_state() 用于 Ghost 检测基准，原 §3.18 无配对 save→跨重启策略持仓丢失
    # v1.30.6 修（A5）：原 strategy_engine.get_current_state() 是悬空引用——§8.2 模块清单
    # 无 strategy_engine，全文仅此 1 处引用，级联导致 save/load 链断裂（save 无源→load 返回 None→
    # §3.15 detect_ghost_positions(broker_holdings, None) 崩溃）。修复：改为从 position_sizing_engine
    # 获取当日仓位裁决产出的目标持仓快照（§3.10 plan 的 symbols/weights 部分），作为次日 Ghost 检测
    # 基准——对比"策略目标持仓"vs"broker 实际持仓"，差异即 Ghost Position。
    strategy_state = position_sizing_engine.get_target_holdings_snapshot()  # 当日 plan 目标持仓快照
    state_store.save_strategy_state(trade_date, strategy_state)

    # ── 阶段 5：标记可加载（原子性提交点，v1.31.0 改 E2 修复）──
    # 全部写入成功才标记，§3.15 盘前检查此标记决定"恢复"vs"冷启动默认 NORMAL"
    # v1.31.0 改（E2 修复——状态值冲突）：原 status="COMPLETE" 与 36号 §3.18 status="VAR_COMPLETE"
    #   冲突——盘前初始化无法判断"哪个文档已持久化"。改为两阶段标记：
    #   35号 §3.18 标记 "DRAWDOWN_COMPLETE"（回撤层持久化完成）
    #   36号 §3.18 标记 "VAR_COMPLETE"（VaR 层持久化完成）
    #   §3.15 盘前初始化检查：两阶段都 COMPLETE 才算完全可加载；
    #   仅 DRAWDOWN_COMPLETE → 回撤层恢复 + VaR 层冷启动默认 NORMAL；
    #   仅 VAR_COMPLETE → 不应出现（35号先于36号执行，见 E1 修复）。
    state_store.mark_persistable(trade_date, status="DRAWDOWN_COMPLETE")
    daily_auditor.log_persist(trade_date, closing_nav=closing_nav, peak=new_peak,
                              state=state_machine.current, step=state_machine.recovery_step)
    # v1.31.0 补（E1 修复——盘后持久化顺序）：本函数（35号 §3.18）先执行（含审计门控阶段 0），
    #   36号 §3.18 postmarket_persist_var() 后执行（假设本函数审计已通过）。
    #   RiskOrchestrator（§6.5）编排顺序：daily_auditor.audit() → 35号 §3.18 → 36号 §3.18。
    #   若 35号 §3.18 阶段 0 审计失败 → return（不持久化）→ 36号 §3.18 不执行（整体跳过）。
```

**与 §3.15 的配对约束**：

| §3.15 加载顺序 | §3.18 保存顺序 | 配对约束 |
|---|---|---|
| 阶段 1 broker 持仓核对 | —（不持久化，实时拉取） | — |
| 阶段 2 加载状态机 | 阶段 3 保存状态机 | 状态机态 + recovery_step 必须一致（§3.11 转换守卫依赖） |
| 阶段 3 加载 peak NAV | 阶段 2 保存 peak NAV | peak 单调非减（§3.8 不变量） |
| 阶段 3 加载 nav_history | 阶段 4 追加 nav_history | 窗口 252 日滚动，drawdown_tracker 需完整窗口算 drawdown_pct |
| 阶段 3 加载 entry_var | 阶段 4b 保存 entry_var | entry_var = 前日盘前 VaR_95 快照，§3.16 回撤归因 current_var vs entry_var 判断风险恶化（v1.28.0 补） |
| 阶段 4d 加载 prev_attribution | 阶段 4c 保存 attribution_result | §3.16 归因结果，供次日盘前决策参考（v1.30.4 补——交接链 5 修复） |
| —（首次启动无前置） | 阶段 5 标记可加载 | 原子提交点：§3.15 据此判断"恢复"vs"冷启动 NORMAL" |

**代码差距**（待施工 §6.12/§6.6）：
1. **无 `state_store.save_*` 接口**——当前 `capital_curve_manager` / `drawdown_tracker` 内存态，无盘后持久化调用
2. **无原子性提交**——若 peak 保存成功但状态机失败，会产生不一致快照（§3.15 加载到新 peak 但旧状态机态，转换守卫错乱）
3. **无 `mark_persistable` 标记**——§3.15 无法判断"上次正常持久化"vs"状态丢失"，只能盲目冷启动

> **裁决**：盘后持久化暂缓为 §6.12（盘前初始化）的配对施工项——两者必须同步落地，否则 §3.15 加载无源。最小补丁（与 §6.12 同步）：① `capital_curve_manager.peak` + `nav_history` 持久化到 DB（复用 daily_auditor 已有持久化基础设施）；② 状态机态持久化待 §6.6 DrawdownStateMachine 落地；③ 原子性用 DB 事务（全成功 commit，任一失败 rollback）。§3.17 总览"T-1 收盘后 → 持久化状态"箭头即本流程。

### 3.19 施工流程算法审查与远期演进方向声明

> **结构说明**（v1.30.2 补）：本节是 §3 施工流程的**审查结论 + 远期演进登记**，定位为"流程闭环验证 + 演进方向 living table"。§3.20 Hysteresis（横切恢复机制）+ §3.21 行业实证（案例背书）在本节之后追加——§3.20 是 §3.11 状态机的降级恢复补全（横切机制非独立流程），§3.21 是设计决策的实盘验证（非新算法）。两者不影响本审查"6 流程闭环无缺失独立环节"的结论，故审查位置保持不变。

**审查结论**：对照 §3.10-§3.18 的 6 流程闭环（日度循环 / 盘中循环 / 复位 / 盘前初始化 / 归因 / 盘后持久化）+ 2 横切机制（状态机 / 诊断），一个交易日的完整风控生命周期已被覆盖——盘前（初始化+裁决）→ 盘中（轮询+熔断）→ 盘后（审计+归因+持久化）→ 跨日（复位+恢复）。**无缺失的独立流程环节**。可增强的是横切算法本身（回撤度量、风险厌恶调整、前馈防御），但这些是 §4 替代方案与 §6 待裁定的演进方向，不是流程环节缺失。

**2026 学术研究的远期演进方向登记**（不直接采纳，详见 §4.6-§4.28 评估 + §5.2 Stage 4 15 族分类表）：

> **v1.33.0 补**：本表原仅覆盖 §4.12-§4.15 + §6.21-§6.25（2026-08 初次创建时的范围）。后续审查新增 §4.16-§4.28 共 13 项远期登记，为避免与 §5.2 Stage 4 15 族分类表重复，此处仅保留原 9 行详细评估，§4.16-§4.28 的详细评估见各自 §4.x 节，汇总映射见本表末尾的 §4.16-§4.28 汇总小表 + §5.2 Stage 4。

| 演进方向 | 来源 | 核心思路 | 与当前方案的关系 | 评估结论 |
|---|---|---|---|---|
| MPC 连续风险厌恶调整 | [Nystrup/Boyd 2019](https://backend.orbit.dtu.dk/ws/files/149812772/Multi_Period_Portfolio_Selection_with_Drawdown_Control.pdf) + [DLP-SMPC 2026](https://arxiv.org/html/2604.00415v1) | 根据已实现回撤**连续**调整 risk aversion 系数，替代当前 5/10/15% **离散**阈值 | 当前 §3.2 三层映射是阶梯式（80%→50%→30%→0%），MPC 是连续函数 | §4.12 暂缓（P4 远期）|
| 趋势跟踪回撤防御层 | [Noguer i Alonso & Al-Fallouji 2026-07](https://arxiv.org/html/2607.00883v1) | 趋势跟踪在**持续回撤**中越来越防御性（信号穿过零后递增），无需期权费 | 当前 Protocol 是纯**反馈式**（已亏才减仓），趋势跟踪是**前馈式**防御 | §4.13 暂缓（P4，A 股需裁定）|
| CDaR 回撤深度连续度量 | [Uryasev/Ding CDaR](https://uryasev.ams.stonybrook.edu/wp-content/uploads/2021/10/Drawdown_Portfolio_Optimization_Problems_and_Drawdown_Betas.pdf) + [Man Numeric CVaR 2025](https://www.man.com/man-numeric-cvar-insights) | CDaR = drawdown 序列的 CVaR，path-dependent coherent measure，LP 可解 | 当前 §3.8 用 `drawdown_pct` 单点值，CDaR 是回撤深度的连续度量 | §4.14 暂缓（P2，与 UI/PI 同类但更优）|
| 多 agent 协作回撤控制 | [RMATS 2026-05](https://arxiv.org/abs/2605.25311) + [MARCD 2026](https://arxiv.org/html/2510.10807v3) | 4 agent（Sentiment/Report/Analysis/Risk）+ 递归 Manager，MaxDD 9.62% | 当前是单进程规则式风控，多 agent 是协作式 | §4.15 拒绝（过度工程，仅借鉴 Risk Agent 独立性）|
| **Conformal Kelly drawdown dial** | [arXiv:2608.01494](https://arxiv.org/html/2608.01494v1)（2026-08-02） | 当 conformal 预测区间在下行方向连续 miss 超过历史率→视为模型失效信号→缩减 leverage；开发窗口 MaxDD 27.7%→20.3%，Sharpe 提升，rank-based p=1/41≈0.024。**OOS 诚实账本**（Lockbox 2022+ 样本外）：校准保持（0.745 vs 0.750 目标）但**增长未保持**——两配置仅 8.5%/7.0%/年，低于被动基准 | 当前 §3.4 恢复是 `recovery_factor` 阶梯（0.25→0.50→0.75→1.0），Conformal Kelly dial 是**预测区间 miss 驱动**的自适应 leverage 缩减 | §6.21 暂缓（P2，远期——需 conformal 预测层就绪）|
| **Data-Driven Drawdown Restart** | [arXiv:2303.02613](https://arxiv.org/pdf/2303.02613v1)（Hsieh 2023） | drawdown modulation 接近预设限值时不应纯 stop-loss（会错过后续盈利机会），而应带 **restart 机制**——用数据驱动重置策略参数，在有交易成本场景下仍优于无 restart | 当前 §3.11 RECOVERY 阶梯（0.25→0.50→0.75）是 restart 的工程化离散实现，但未实现"数据驱动参数重置" | §6.22 暂缓（P3，远期——需足够实盘样本做参数重置的 data-driven 校准）|
| **Non-Gaussian Drawdown Lookup Tables** | [arXiv:2608.00127](https://arxiv.org/abs/2608.00127)（Landolfi 2026-07-31） | 给定 Sharpe ratio 与收益统计结构（skew/峰度/波动率聚集/Sharpe 估计不确定性），用 Monte-Carlo 框架生成 4 个决策相关度量的查表：MaxDD / 最大单期损失 / 末尾负时间 / 最长恢复时间。核心发现：① 单一 Gaussian 表会误警（四种度量在非正态下移动方向不同）；② 持续性下的回撤"放大"几乎全是 self-similar dispersion scaling `T^(H-1/2)`，是 √T 校准失效而非路径几何本征危险 | 当前 §3.4 recovery_factor 阶梯（0.25→0.50→0.75）+ §3.2 三层阈值（5/10/15%）是经验值，Landolfi 查表提供"给定 Sharpe 该期望多深/多长回撤"的统计校准依据；同时警示 [36_var_es_monitoring](36_var_es_monitoring.md) §3.2 参数法 VaR 的 `√T` 时间缩放在持续性下失效 | §6.23 暂缓（P2，远期——需实盘 Sharpe 稳定估计 ≥6 月 + 收益分布矩估计）|
| **Schmitt RWC Conformal Risk Control** | [arXiv:2602.03903](https://arxiv.org/pdf/2602.03903)（Schmitt 2026-02, Oxford, **v3 2026-08-03**） | Regime-Weighted Conformal Risk Control（RWC）：用指数时间衰减 + regime 相似性权重校准 VaR 安全缓冲，wrap 任意 quantile 预测器，在 weighted exchangeability 下有限样本覆盖保证。TWC（time-weighted）是 drift 下的强默认，RWC 增加 regime 加权改善 regime-conditional 稳定性。**v3 关键**：在任意 data-driven 权重下推导覆盖界（不需 weighted exchangeability 假设），与 [arXiv:2608.01494](#) Conformal Kelly "反自适应"结论一致——RWC 用 regime 做**校准加权**（预测误差的 buffer）而非 conformal 宽度的局部自适应，避开"自适应损害增长"陷阱 | 当前 [36_var_es_monitoring](36_var_es_monitoring.md) §3.2 参数法 VaR 假设正态 + 平稳，Schmitt RWC 提供"非平稳 + regime 结构"下的 distribution-free VaR 校准——直接增强 §3.10 日度循环盘前段的 VaR 计算（C 层 drawdown_controller 输入）。**regime 特征稳定性依赖**：RWC 需 regime embedding 相似性度量，[arXiv:2604.14322](https://arxiv.org/abs/2604.14322) BR-iHMM（Yiu et al. 2026，在线双重鲁棒无限 HMM，预测误差降 67%）可作 regime 特征在线更新方案，天然适配 A 股跳空/涨跌停异常点 | §6.25 暂缓（P2，远期——需 [36_var_es_monitoring](36_var_es_monitoring.md) conformal 预测层就绪 + regime 特征工程稳定）|
| **CVaR Risk-Aware Q-Learning** | [arXiv:2608.04305](https://arxiv.org/abs/2608.04305)（Wu/Lei/Huang 2026-08-05, ICAIF '26 Milan） | 自适应有限预算训练 CVaR 风险感知 Q-learning（RaQL）：per-cell inner-step sizing + outer-rate-matched decay + coverage-first sample allocation，CVaR Bellman 残差降 85%，BTC 日度交易 Sharpe 0.93 / MaxDD 6.46% | 当前 §3.2 三层映射是规则式阈值，RaQL 是 RL 端到端 CVaR 优化——属 §4.15 多 agent 拒绝的同类（RL 重模型），但 RaQL 是单 agent + CVaR 目标，比 RMATS/MARCD 轻量 | 不单独登记（归入 §4.15 多 agent 拒绝的"借鉴范围"——CVaR 目标函数思路已由 §3.9 乘性叠加承载）|

> **§4.16-§4.28 远期登记汇总**（详见各自 §4.x 节 + §5.2 Stage 4 15 族分类表）：
>
> | §4.x | 方向 | §6.x | 优先级 | 一句话定位 |
> |---|---|---|---|---|
> | §4.16 | CED 线性因子归因 | §6.24 | P3 | 系统性 vs 策略特定回撤的线性因子分解 |
> | §4.17 | Schmitt RWC | §6.25 | P2 | （与上表 Schmitt RWC 行同条目，§4.x/§6.x 双重登记） |
> | §4.18 | BOCD 概率 Kill Switch | §6.27 | P3 | CUSUM 的概率化统一演进（run-length 后验） |
> | §4.19 | Signature Path Portfolio | — | P5+ | path-dependent 风险的 rough paths 数学基础 |
> | §4.20 | Continuous Cash-Overlay Filters | — | P3 | slow-tail compensation + V-shape crash-brake 连续回撤工具 |
> | §4.21 | Transfer-Entropy+Hawkes+Von Neumann 图熵 | — | P4 | 网络级系统性风险前馈预警 |
> | §4.22 | Xiao Jian A 股 HFT herding 渗流相变 | — | P4 | A 股多层复杂网络 herding 相变检测 |
> | §4.23 | Chen A 股 GWII herding CSAD/CSSD | — | P3 | A 股板块 herding 轻量统计检测 |
> | §4.24 | Lévy-stable Drawdown Scaling | §6.23 相关 | P2-P3 | α-稳定窗口内 drawdown 的封闭形式非高斯传播 |
> | §4.25 | MFCCA 符号保留多重分形交叉相关组合分配 | §6.35 | P4 | 组合配置层符号保留风险泛函，直接降低 drawdown |
> | §4.26 | Robust Risk Parity (RRP) A 股实证 | §6.36 | P3 | A 股 2012-2024 全样本实证 RRP，regime+GARCH 组件可独立提取 |
> | §4.27 | Drawdown Beyond Brownian Motion | §6.37 | P3 | §6.23 同论文的施工算法版，回撤阈值非高斯校准+keep-or-kill |
> | §4.28 | Aldridge AI Governance 4 层框架 | — | P3 | regret-covariance policy drift + crowding model 联合回撤定量背书（39.2%→79.3%） |

> **Conformal Kelly 的关键设计原则**（arXiv:2608.01494 核心发现）：**"slow, unweighted, per-asset rolling conformal quantiles" 优于 adaptive/fast 方法**——每次使区间更快适应当前市场状态的调整都损失 0.7-5.3 个百分点的年增长。原因：当区间用于**仓位规模**而非**单点预测**时，宽度的**稳定性**比**局部锐度**更重要。这违背了 conformal prediction 在时间序列上的现有文献建议（通常推崇 locally adaptive），但对 position sizing 场景成立——宽度频繁跳变 = 仓位频繁调整 = 交易成本侵蚀。**本项目启示**：若远期集成 Conformal Kelly，应选用最简单的 per-asset rolling quantile，不追 locally adaptive 变体——简单稳定优于复杂自适应。
>
> **Conformal Kelly drawdown dial 施工骨架**（远期·接口冻结，待 conformal 预测层就绪激活，§6.21 P2）：
>
> [arXiv:2608.01494](https://arxiv.org/html/2608.01494v1) 核心机制：conformal 预测区间在**下行方向**连续 miss 超过历史率 → 视为模型失效信号 → 缩减 leverage。实证 MaxDD 27.7%→20.3%。当前 §6.21 已登记设计原则与重评条件，本块补**可施工形态**（接口冻结，conformal 层就绪后直接对接）：
>
> ```python
> def conformal_kelly_drawdown_dial(realized_returns, conformal_intervals,
>                                    coverage_level=0.75, rolling_window=252,
>                                    floor_scale=0.5):
>     """Conformal Kelly drawdown dial——预测区间下行 miss 驱动的 leverage 缩减
>
>     设计原则（arXiv:2608.01494）：slow unweighted per-asset rolling quantile
>     优于 locally adaptive——宽度稳定性 > 局部锐度，故用固定窗口均值非自适应核。
>
>     Args:
>         realized_returns: 已实现收益序列 r_t
>         conformal_intervals: 历史预测区间 [(lower_t, upper_t), ...]
>         coverage_level: 区间覆盖率（默认 0.75，对应 75% conformal interval）
>         rolling_window: rolling miss 率窗口（默认 252 日≈1 年，slow/unweighted）
>         floor_scale: leverage 下限（默认 0.5，防 cash-lock，对齐 §4.5 拒绝 CPPI）
>     Returns:
>         leverage_scale ∈ [floor_scale, 1.0]——1.0=不缩减，0.5=半仓杠杆
>     """
>     # 1. 下行 miss 序列：实际收益 < 区间下界 = 模型低估下行风险
>     downside_misses = [1 if r < lo else 0
>                        for r, (lo, _hi) in zip(realized_returns, conformal_intervals)]
>     # 2. slow unweighted rolling miss rate（不追 locally adaptive 变体）
>     recent_miss_rate = sum(downside_misses[-rolling_window:]) / min(len(downside_misses), rolling_window)
>     baseline_miss_rate = 1.0 - coverage_level  # 75% 区间 → baseline 0.25
>     # 3. dial：miss 率超 baseline → 线性缩减 leverage（平滑过渡，不超调）
>     if recent_miss_rate <= baseline_miss_rate:
>         return 1.0  # 模型校准良好，不缩减
>     excess = (recent_miss_rate - baseline_miss_rate) / (1.0 - baseline_miss_rate)
>     return max(1.0 - excess, floor_scale)  # 最低半仓，不归零
> ```
>
> **与 §3.4 recovery_factor 的乘性叠加**（三层各管一件事，正交不覆盖）：
>
> `effective_position_cap = position_cap(state) × recovery_factor(state) × conformal_leverage_scale`
>
> | 乘子 | 驱动信号 | 作用层 | 来源 |
> |---|---|---|---|
> | `position_cap` | 状态机分级（NORMAL/WARN/DANGER/CRISIS） | 仓位硬上限 | §3.2 三层映射 |
> | `recovery_factor` | 已实现回撤恢复阶梯（0.25→0.50→0.75→1.0） | 回撤后恢复节流 | §3.4 + §3.20 hysteresis |
> | `conformal_leverage_scale` | 预测区间下行 miss 率 | 模型失效 dial | 本块（远期） |
>
> 三者乘性叠加：任一缩减即整体缩减。`recovery_factor` 是"已亏才减"的反馈式，`conformal_scale` 是"预测失准即减"的**前馈式**——两者正交互补，对应 §3.19 远期演进声明中"基于收益预测的前馈风控"边界（非"预测回撤本身"）。
>
> **接口冻结**（conformal 层就绪后直接对接，不改 §3.4/§3.2 现有逻辑）：
> - **输入**：`conformal_intervals` 序列——由 [31_position_sizing](31_position_sizing.md) 或独立 conformal 预测模块产出（每标的每预测点一个 (lower, upper) 对）
> - **输出**：`conformal_leverage_scale ∈ [0.5, 1.0]`——喂入 `capital_curve_manager`，与 `recovery_factor` 乘性叠加后作用于 `position_cap`
> - **不替换** §3.4 `recovery_factor`，只追加第三乘子；`conformal_scale=1.0` 时（模型校准良好）整体行为退化为现状
>
> **为何 0.5 下限而非归零**：对齐 §4.5 拒绝 CPPI 的"cash-lock 风险"教训——conformal dial 是风险节流阀不是破产防护闸，归零会重蹈 CPPI"cushion=0 永久退出"覆辙。Kill Switch（§3.5）才是归零通道，dial 只做平滑缩减。floor_scale=0.5 为初始值，待实盘校准 miss 率与 MaxDD 的敏感度后调整（重评条件见 §6.21）。
>
> **0.5% Recovery Protocol**（[edgeflo 2026-03](https://www.edgeflo.com/blog/de-risk-after-drawdown)）：连续 2 笔亏损（或 2% 回撤）后，将每笔风险从 1% 降至 0.5%——在 0.5% 风险下，单笔 3R 盈利回补 +1.5%，覆盖 2 笔 0.5% 亏损还多 0.5%。2 笔 3R 盈利可完全恢复 3% 回撤到 breakeven。**与本项目 §3.4 recovery_factor 阶梯的关系**：本项目的 25%→50%→75%→100% 阶梯是**仓位上限**层面的恢复，0.5% protocol 是**单笔风险**层面的恢复——两者正交可叠加。当前 §3.4 已实现仓位上限恢复（`recovery_factor`），单笔风险恢复由 [31_position_sizing](31_position_sizing.md) 的 risk_per_trade 参数承载。0.5% protocol 启发：recovery 期间 `risk_per_trade` 应从默认 1% 降至 0.5%，与 `recovery_factor` 乘性叠加（如 recovery_factor=0.5 + risk_per_trade=0.5% → 实际风险 = 0.25%），实现"双保险恢复"——仓位上限 + 单笔风险同步收缩。

**过度工程红线**（个人 + 100% AI 项目的自约束）：

1. **不引入重模型**：MPC 需多变量 HMM 预测多期收益均值/协方差，MARCD 需 regime-conditioned diffusion 生成器 + CVaR epigraph QP，DLP-SMPC 需随机 MPC receding-horizon 求解——这些模型在机构级 24 资产、561 交易日样本下验证有效，但本项目 3-5 个 A 股策略、实盘样本 <6 个月，HMM/diffusion 参数估计不可靠，重模型收益不抵复杂度成本。[arXiv:2605.16895 The Alpha Illusion 2026-05](https://arxiv.org/html/2605.16895v1) 警示：LLM/多 agent 报告的 alpha 在通过 temporal integrity / real-world frictions / counterfactual robustness 等结构有效性测试前，不应作部署证据——这进一步支持"借鉴思路不照搬架构"。
2. **A 股约束适配**：不能做空 + T+1 + 无期权，使趋势跟踪防御层（§4.13）的"持续回撤中递增防御"只能通过"减仓/空仓"实现，不能通过"做空对冲"实现；MPC 的"杠杆提高收益不增 MaxDD"（Nystrup 论文核心卖点之一）在 A 股个人账户融资融券受限下不适用。
3. **可解释性优先**：当前 5/10/15% 阈值法每个数字都可向业主解释"为什么这个点减仓"，MPC 的连续风险厌恶函数 `γ(dd)` 虽更优但难解释——个人系统业主需理解每一笔风控动作的依据，可解释性是硬约束。
4. **借鉴范围限定**：从 RMATS 借鉴"Risk Agent 独立于策略 agent"（本项目已实现，§4.2 拒绝合并 tracker/curve_manager/controller）+ "RL 目标函数的回撤惩罚项思路"（§3.9 已对比乘性 vs 加性，选乘性）；从 Nystrup/Boyd 借鉴"风险厌恶随回撤调整"的直觉（当前 recovery_factor 0.25→0.50→0.75 阶梯是其离散近似）；从 Noguer 借鉴"持续回撤需递增防御"的直觉（当前 §3.4 恢复是阶梯，未实现"持续回撤递增防御"的前馈层）；从 Uryasev CDaR 借鉴"回撤序列的尾部度量"思路（当前 drawdown_pct 是单点，CDaR 是尾部均值）。

**回撤预测 vs 前馈风控的边界**（澄清 §5.3 已论立场）：§5.3 说"再加层如独立的回撤预测器是过度工程——回撤本质是已发生事实的度量，预测回撤 = 预测收益，属于 alpha 层不是风控层"。此立场**不变**，但需区分两种"前馈"：① **回撤预测**（拒绝）= 预测"下周会回撤多少"，等价于预测收益分布，属 alpha 层；② **基于收益预测的前馈风控**（MPC 方法，远期）= 用 HMM 预测收益均值/协方差，在前馈优化中纳入回撤约束——这是"用 alpha 层预测喂入风控层约束"，不是"预测回撤本身"。本项目当前无 alpha 层收益预测（regime 是市场状态分类非收益预测），故 MPC 方法的前馈风控无数据基础，远期待 alpha 层成熟后再评估。

### 3.20 回撤状态滞后-恢复双阈值（Hysteresis）

> **v1.9.0 新增**：§3.11 状态机定义了 NORMAL/WARN/DANGER/CRISIS/KILL/RECOVERY 6 态及其**升级触发条件**（drawdown > 5% → WARN 等），但**未定义降级/恢复条件**——实盘一旦触发 WARN，drawdown 从 5.1% 回落到 4.9% 时是否立即回 NORMAL？若无恢复算法，状态机会在临界阈值附近反复震荡（触发→恢复→再触发→再恢复的 thrashing），或锁死在高级态无法降级（错过恢复后的盈利机会）。本节补齐**降级恢复算法**，对齐 [37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md) §3.6 的滞后-恢复双阈值设计。

**核心原则**：触发阈值与恢复阈值**不对称**（hysteresis 双阈值），避免在临界状态反复震荡（thrashing）。这是控制论中 hysteresis（迟滞回线）的标准应用——恒温器/施密特触发器同原理：升温到 25°C 才开制冷，降温到 23°C 才关制冷，中间 2°C 是稳定区，避免压缩机反复启停。

**行业印证**：
- [r1000-quant-engine Phase 6a](https://github.com/wscha231/r1000-quant-engine/blob/master/PHASE_ROADMAP.md)（2026-04）：3 级 drawdown circuit breaker 阈值 −8%/−15%/−25% → cash floors 15%/35%/60%，**equity-based recovery hysteresis** `dd_trigger_equity * (1 + 0.03)`——即净值须从触发点回升 3% 才解除 circuit breaker
- [dredyson 2026-05](https://dredyson.com/the-hidden-truth-about-state-machines-in-algorithmic-trading-systems-)：状态机进入阈值 2.0 std、退出阈值 1.5 std，0.5 gap **减少 70% 的假状态转换**；cooldown timer 是额外安全网
- [Actura 2026-04](https://github.com/othnielObasi/actura-gacr-agent/blob/main/WHITEPAPER.md)：drawdown > 6% 锁定 EXTREME_DEFENSIVE，profile 切换间至少 **8 cycles cooldown**
- **Triple Penance Rule（[Bailey & López de Prado 2014](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2201302)，[BacktestBase 2026-02](https://www.backtestbase.com/education/drawdown-risk-analysis) 实证引用）**：回撤恢复时间通常为回撤形成时间的 **2-3 倍**——即若 drawdown 用 10 个交易日形成，恢复到前高需 20-30 个交易日。这为 §3.20 min_hold 持续时间门控（WARN 5 日 / DANGER 10 日 / CRISIS 20 日）提供**经验倍数依据**：5/10/20 日 ≈ 形成期 2-3 日的 2-3x（WARN 浅回撤）/ 形成期 5 日的 2x（DANGER）/ 形成期 7-10 日的 2-3x（CRISIS），量级吻合。**与 §2.1 恢复数学表的关系**：§2.1 的"20% 回撤需 25% 收益恢复"是**幅度非对称**（Loss/(1-Loss) 公式），Triple Penance Rule 是**时间非对称**（恢复用时 2-3x 形成用时）——两者正交，共同构成回撤恢复的"幅度×时间"双维约束。RECOVERY 阶梯的 5 日/阶梯 min_hold 累计 15 日（0→1→2→NORMAL 三阶梯），对齐 Triple Penance Rule 的 2-3x 下限。

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

> **关键说明**：恢复阈值取触发阈值的 **50%**（半阈值）是经验初始值，对齐 [37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md) §3.6 的半阈值设计。r1000-quant-engine 用 3% 净值回升 buffer（绝对值），本项目用 50% 比例（相对值）——因回撤阈值 5/10/15/25% 跨度大，固定 3% buffer 在浅回撤（5%）时过粗（3% > 5% 的 60%），在深回撤（25%）时过细（3% < 25% 的 12%）。50% 比例在各阈值下均产生合理 buffer：2.5% / 5% / 7.5% / 12.5%。

**恢复算法步骤**（CUSUM 式，对齐 §3.11 状态机 + [37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md) §3.6 CUSUM 框架）：

```python
# ── 辅助函数定义（v1.30.0 补：消除 §3.20 伪代码未定义引用）──

def next_state_level(current_state):
    """返回降级后的下一级状态（WARN→NORMAL / DANGER→WARN / CRISIS→DANGER）。"""
    downgrade_map = {"WARN": "NORMAL", "DANGER": "WARN", "CRISIS": "DANGER"}
    return downgrade_map.get(current_state, current_state)

def var_trigger_threshold(target_state):
    """返回目标状态对应的 VaR 触发阈值（§3.11 升级阈值的逆查）。
    
    NORMAL → 0.02（WARN 触发阈值 2%，降级到 NORMAL 须 VaR < 2%）
    WARN → 0.04（DANGER 触发阈值 4%）
    DANGER → 0.06（CRISIS 触发阈值 6%）
    """
    thresholds = {"NORMAL": 0.02, "WARN": 0.04, "DANGER": 0.06}
    return thresholds.get(target_state, 0.02)

def sustained(history, threshold, window):
    """检查 history 最近 window 个交易日是否全部 < threshold（CUSUM 式持续确认）。"""
    if len(history) < window:
        return False
    return all(abs(h) < threshold for h in history[-window:])

def has_consecutive_profit_days(strategy_pnls, n=3):
    """检查最近 n 笔交易是否全部盈利（TradeZella 三级恢复协议）。"""
    if len(strategy_pnls) < n:
        return False
    return all(t.pnl > 0 for t in strategy_pnls[-n:])

def compute_rule_compliance(recent_trades):
    """计算规则合规率——过去 10 笔交易中遵守预设规则的占比（BloFin 行为性检测）。"""
    if not recent_trades:
        return 0.0
    compliant = sum(1 for t in recent_trades if t.rule_followed)
    return compliant / len(recent_trades)

def retreat_recovery_step(current_state, recovery_step):
    """RECOVERY 期间回撤加深 → 回退阶梯或回 KILL（对齐 §3.14 分级保护）。"""
    if recovery_step > 0:
        return f"RECOVERY_STEP_{recovery_step - 1}"  # 回退一级
    return "KILL"  # 阶梯 0 回撤 >15% → 回 KILL


# ── 主函数 ──

def check_drawdown_recovery(current_state, dd_info, var_cvar,
                            time_since_trigger, dd_history,
                            recovery_step=0, strategy_pnls=None,
                            recovery_window=3):
    """回撤状态恢复判定——滞后双阈值 + 持续时间门控 + 毕业准则
    
    Args:
        current_state: 当前状态机态（NORMAL/WARN/DANGER/CRISIS/KILL/RECOVERY）
        dd_info: DrawdownInfo(drawdown_pct, peak, recovered_pct)
        var_cvar: VarCvarMetrics(var_95, cvar_95)  # 交叉验证
        time_since_trigger: 距离升级触发的时间（交易日）
        dd_history: 最近 N 个交易日的 drawdown_pct 序列（供 sustained() 持续确认）
        recovery_step: RECOVERY 阶梯计数器（0/1/2，§3.14）
        strategy_pnls: 策略 PnL 列表（供 graduation_criteria_met 毕业准则）
        recovery_window: 恢复条件需持续的窗口（交易日，默认3）
    Returns:
        target_state: 恢复后的目标态（None=不恢复）
    """
    # 最短持续时间门控（防 thrashing，对齐 dredyson cooldown timer）
    min_hold = {
        "WARN": 5,      # 5 个交易日
        "DANGER": 10,
        "CRISIS": 20,
        "RECOVERY_0": 5,  # RECOVERY 阶梯间
        "RECOVERY_1": 5,
        "RECOVERY_2": 5,
    }
    # RECOVERY 阶梯的 min_hold key 含阶梯号
    hold_key = f"RECOVERY_{recovery_step}" if current_state == "RECOVERY" else current_state
    if time_since_trigger < min_hold.get(hold_key, 5):
        return None  # 持续时间不足，不恢复
    
    dd = abs(dd_info.drawdown_pct)  # drawdown_pct ≤ 0，取绝对值
    
    # ── 降级条件检查（半阈值 + 持续时间 + VaR 交叉验证）──
    # VaR 也须同步回落到下一级的触发阈值以下，避免"回撤降但 VaR 仍高"的假恢复
    var_ok = var_cvar.var_95 < var_trigger_threshold(next_state_level(current_state))
    
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
    
    # ── RECOVERY 阶梯升级（对齐 §3.14 kill_switch_recovery_flow）──
    elif current_state == "RECOVERY":
        # 阶梯 0→1: recovered_pct ≥ 50% + 毕业准则
        if dd_info.recovered_pct >= 0.50 and recovery_step == 0:
            if graduation_criteria_met(strategy_pnls, expected_phases=0):
                return "RECOVERY_STEP_1"  # recovery_factor 0.25 → 0.50
        
        elif dd_info.recovered_pct >= 0.75 and recovery_step == 1:
            if graduation_criteria_met(strategy_pnls, expected_phases=1):
                return "RECOVERY_STEP_2"  # 0.50 → 0.75
        
        elif dd_info.recovered_pct >= 1.0 - 1e-6 and recovery_step == 2:
            # 创新高 → 完全恢复（v1.30.0 修：用 recovered_pct >= 1.0-epsilon 替代
            # drawdown_pct == 0 浮点等值检查，与 §3.14 同类修复对齐）
            if graduation_criteria_met(strategy_pnls, expected_phases=2):
                return "NORMAL"  # 0.75 → 1.00
    
    # ── 恢复期回撤加深保护（对齐 §3.14）──
    if current_state == "RECOVERY" and dd > 0.15:
        # RECOVERY 期间再次回撤 > 15% → 回退阶梯或回 KILL
        return retreat_recovery_step(current_state, recovery_step)
    
    return None  # 不满足恢复条件


def graduation_criteria_met(strategy_pnls, expected_phases):
    """毕业准则——对齐 BloFin/JournalPlus 分阶段恢复的 graduation criteria
    
    1. 连续 N 个盈利日（TradeZella 三级恢复协议：需连续盈利日确认）
    2. 10 笔交易序列平均期望 ≥ +0.3R（BloFin Phase 2 graduation）
    3. 规则合规率 ≥ 80%（BloFin 行为性检测，过去 10 笔）
    """
    if strategy_pnls is None or len(strategy_pnls) < 3:
        return False  # 样本不足，不毕业（v1.30.0 补：None 守卫）
    
    # 连续盈利日（TradeZella）
    if not has_consecutive_profit_days(strategy_pnls, n=3):
        return False
    
    # 10 笔期望 ≥ 0.3R（BloFin graduation criterion）
    recent_trades = strategy_pnls[-10:]
    avg_r = mean(t.r_multiple for t in recent_trades)
    if avg_r < 0.3:
        return False
    
    # 规则合规率（BloFin 行为性，防 AI 执行偏差复发）
    compliance = compute_rule_compliance(recent_trades)
    if compliance < 0.80:
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

**为何用半阈值（hysteresis）而非原阈值**：
- 若恢复阈值 = 触发阈值（drawdown 5%），则在 drawdown 于 4.9%-5.1% 间波动时会反复触发/恢复（thrashing），系统在"80%→100%→80%"仓位间震荡
- 半阈值（2.5%）制造了一个"恢复缓冲带"——drawdown 须从 5% 降到 2.5% 才恢复，从 2.5% 升到 5% 才再触发，中间 2.5% 的区间是稳定区
- [dredyson 2026-05](https://dredyson.com/the-hidden-truth-about-state-machines-in-algorithmic-trading-systems-) 实证：0.5 std 的 hysteresis gap **减少 70% 的假状态转换**——本项目 2.5% gap 在 5% 阈值下是 50% 比例，比 dredyson 的 25%（0.5/2.0）更宽，因回撤序列比 std 信号更黏滞（serial correlation 更强）

**为何需要最短持续时间门控**：
- 回撤的恢复不是瞬时的——drawdown 短暂回到 2.5% 以下不代表回撤期已过（可能只是日内波动间隙，次日又深跌）
- N=3 个交易日的持续时间窗口确保恢复条件**持续满足**而非瞬时满足
- WARN 5 日 / DANGER 10 日 / CRISIS 20 日 的递增 min_hold 是对回撤持续性的经验估计——深回撤需要更长的"企稳确认期"，[Rej-Seager-Bouchaud 2017](https://arxiv.org/abs/1707.01457) 理论：回撤持续时间随 Sharpe **平方**反比，深回撤的恢复期呈二次方增长

**毕业准则（Graduation Criteria）——分阶段恢复的进阶约束**：

> 对齐 [BloFin 2026-05](https://blofin.com/en/academy/education/handling-drawdowns) 三阶段恢复（Phase 1 半仓 / Phase 2 微仓 / Phase 3 正常）+ [JournalPlus 2026-05](https://journalplus.co/learn/guides/trading-after-a-drawdown-guide/) 4 阶段框架（半仓规则 → 诊断 → 48-72h 休息 → scale-up 准则）+ [fazencapital 2026-05](https://fazencapital.com/learn/en/trading-drawdown-recovery-math-methods-guide)（2026-08-04 复审）30 天 reset protocol。

| 准则 | 阈值 | 来源 | 理由 |
|---|---|---|---|
| 连续盈利日 | ≥ 3 日 | TradeZella 三级恢复协议 | 确认回撤企稳而非单日反弹 |
| 10 笔交易平均期望 | ≥ +0.3R | BloFin Phase 2 graduation | 量化"策略正期望已恢复"——0.3R 是正期望的下限确认 |
| 规则合规率 | ≥ 80% | BloFin 行为性检测 | 防 AI 执行偏差复发——合规率 < 80% 说明行为性回撤未修正 |
| 单笔最大亏损 | ≤ 1.2R | completetradersedge 诊断矩阵 | 止损未被放宽——平均损失 > 1.2R 说明执行偏差仍在 |

> **与 §3.4 recovery_factor 阶梯的关系**：§3.4 的 `recovery_factor`（0.25→0.50→0.75→1.0）是**仓位上限**层面的恢复数值，本节的毕业准则是**状态转换**层面的进阶约束——`recovery_factor` 升级到下一阶梯前，毕业准则必须全部满足。两者是"数值阶梯 + 准则守卫"的互补关系，对齐 [BloFin](https://blofin.com/en/academy/education/handling-drawdowns)："Advance only when objective criteria are met. Return to the previous phase if drawdown exceeds the phase limit."

**与 §3.11 状态机的集成**：
- 恢复判定由 `DrawdownStateMachine.check_recovery()` 在每次 `evaluate()` 调用时顺带执行——检测升级触发 + 检测降级恢复条件，输出 `StateTransition(from=current, to=target_state, reason="hysteresis_recovery")` 或保持当前态
- 恢复动作（`position_cap` 调整 / `recovery_factor` 升级）由 `capital_curve_manager` + `drawdown_controller` 在消费状态转换事件时执行，与升级动作的消费者一致
- **转换守卫**（§3.11 代码差距 2 的修复）：降级必须经过 hysteresis 双阈值 + min_hold + 毕业准则三重守卫，CRISIS 不可直接跳回 NORMAL（必须经 DANGER → WARN → NORMAL 逐级降级），RECOVERY 不可跳过阶梯

**与 §3.14 Kill Switch 复位流程的关系**：
- §3.14 定义 KILL → RECOVERY → NORMAL 的**端到端流程**（人工复位 + 阶梯恢复 + 创新高）
- 本节 §3.20 定义 NORMAL ↔ WARN ↔ DANGER ↔ CRISIS 的**常规降级算法**（非 Kill Switch 场景的回撤恢复）
- 两者在 CRISIS/KILL 边界衔接：CRISIS 若未触发 Kill Switch（drawdown 15-25% 区间），用 §3.20 降级回 DANGER；CRISIS 若触发 Kill Switch（drawdown > 25% 或 BS-007），用 §3.14 人工复位 + RECOVERY 阶梯

**与 37 号流动性危机恢复算法的对齐**：
- [37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md) §3.6（v1.0.3）定义流动性危机的滞后-恢复双阈值（spread 半阈值 0.25% + sell_pressure 0.50 + min_hold 10/15/30 分钟）
- 本节 §3.20 是回撤协议的对等设计——两者共享 hysteresis 半阈值 + min_hold + CUSUM 式检测的设计模式，但阈值维度不同（37 号是 spread/sell_pressure 微结构信号，35 号是 drawdown_pct/VaR 账户级信号）
- 两个恢复算法独立运行，不互相调用——流动性危机恢复（37 号）管"市场微结构是否恢复正常"，回撤状态恢复（35 号 §3.20）管"账户回撤是否企稳"，两者可同时处于不同态（如流动性已恢复但账户仍 CRISIS）

> **待校准**（§6.26 新增）：恢复阈值（半阈值 50% 比例）和最短持续时间（5/10/20 交易日 + RECOVERY 阶梯 5 日）是经验初始值，需实盘观测触发-恢复频率校准。重评条件：实盘累积 3 个月恢复事件数据后评估 thrashing 率（恢复后 N 日内再次升级的比例）——若 thrashing 率 > 20%，加大 hysteresis gap（50% → 60%）或延长 min_hold；若恢复滞后（回撤已深度企稳但状态机迟迟不降级），缩小 gap（50% → 40%）。

### 3.21 行业实证背书：2026-08 A 股量化私募集体回撤（风险优先原则的实盘检验）

> **2026-08 全网搜索实证**（中国证券报/第一财经/深圳商报 2026-08，[量化私募如何穿越波动](http://m.toutiao.com/group/7672055738499351080/) / [百亿量化稳博投资回撤](http://m.toutiao.com/group/7669983704357388819/)）：2026 年 7 月 A 股科技成长与中小盘显著回调，量化私募遭遇**贝塔与阿尔法"双重压力"**的集体回撤，为项目风险优先原则 + 四级回撤 Protocol + Kill Switch 不可覆盖提供**实盘级**实证背书。

**回撤规模**（私募排排网/Wind 2026-07-31 数据）：

| 产品类别 | 7 月平均跌幅 | 极端个案 |
|---|---|---|
| 中证 500 指增 | -18.72% | 进化论多只产品跌超 25% |
| 中证 1000 指增 | -19.96% | 稳博小盘激进择时指增 1 号 **-46.24%**（近一月） |
| 量化选股 | -13.04% | 多只产品跌逾 28% |
| 量化中性 | -3.33% | — |
| 幻方量化 | 9 只产品近一月均跌逾 20% | 仅 1 只年内正收益 |

**根因归因**（多家百亿量化私募复盘共识）：

1. **风格暴露集中是首要根因**——"上半年资金向少数科技板块和个股集中，主动放开科技、动量、高波动等风格暴露的产品更容易获得超额收益；而当市场风险偏好骤降，前期收益来源也迅速转化为回撤来源"（**盈亏同源**）。部分管理人"迫于业绩和客户压力提高相关风格暴露，又在市场突然转向时被左右打脸"
2. **分散失效**——"原本相关性较低的策略也会出现同向波动，组合的分散效果随之减弱"
3. **止损踩踏**——"市场低开后，避险、止损和调仓行为集中释放，在流动性阶段性承压时形成了一定的踩踏效应，进一步放大净值波动"
4. **端到端 AI 逆向承接深套**——稳博投资（端到端 AI 策略）"模型在市场明显恐慌时会表现出一定的逆向倾向……有一定概率会选择承接这些恐慌盘"，近一月净值重挫 46.24%

**对本项目设计决策的实证映射**：

| 量化私募回撤教训 | 本项目对应设计 | 实证支撑强度 |
|---|---|---|
| 风格暴露集中→回撤源（根因①） | [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.5 firm 层硬上限裁剪 + [31_position_sizing](31_position_sizing.md) §2.4 单票 8%/行业上限/总仓位裁剪 | ★★★ 强——百亿量化因风格集中回撤 20%+，项目 firm 层硬上限是直接防御 |
| 低相关策略同向波动→分散失效（根因②） | §3.16 回撤归因（相关性归因 avg_corr>0.7=系统性）+ [23_strategy_correlation_validation](23_strategy_correlation_validation.md) 策略相关性监控 | ★★★ 强——"分散效果减弱"正是 §3.16 相关性归因要检测的场景。**v1.37.0 补定量背书**：[arXiv:2608.02311](https://arxiv.org/abs/2608.02311) Aldridge & Krawciw 2026-08-03 crowding model 实证——两 agent 收敛于相关暴露时 joint drawdown probability 从 **39.2% 升至 79.3%**（§4.28 远期登记），为"分散失效"提供可计算的 crowding 放大因子，Phase 2 可将 §3.16 avg_corr 单点阈值升级到 crowding-adjusted joint drawdown probability |
| 止损集中释放→踩踏放大（根因③） | §3.20 hysteresis min_hold 5/10/20 交易日 + §3.5.1 Kill Switch 分批拆单（A 股 2026 程序化新规 15 笔/秒）+ [42_sell_flow](42_sell_flow.md) §3.8 跌停板排队优先级算法 | ★★☆ 中——踩踏是机构同质化止损的后果，个人系统 min_hold + 分批拆单降低自身踩踏风险 |
| 端到端 AI 逆向承接深套（根因④） | §3.5 Kill Switch **不可覆盖**（`requires_manual_reset`）+ [30 §2.5.5](30_multi_strategy_concurrency.md) 回撤>25% 清仓+强制休息 5 天+人工 review | ★★★ 强——稳博 AI"逆向承接恐慌盘"=-46% 回撤，项目 Kill Switch 不可覆盖正是防"模型自作主张深套" |
| 回撤 20%+ 成行业常态 | §2.5.1 四级阈值 8/15/20/25%（外层生存边界）+ 代码 5/10/15%（内层早预警） | ★★★ 强——百亿量化 7 月回撤 20%+ 是常态，项目 Level 3（20%）停仓 / Level 4（25%）清仓是生存底线 |

> **关键启示**：2026-07 量化私募集体回撤**不是模型失效，而是风险约束不足**——"短期回撤不等于模型失效，不能因为一次极端行情就推翻长期验证过的策略"，但"部分模型的风格敞口过于集中"是可改进的风控缺陷。这直接印证项目风险优先原则（project_memory 硬约束："回撤 Protocol 施工优先级：风险相关模块（drawdown_controller/var_calculator/kill_switch）先于策略模块施工至 production"）——先建风控红线再迭代 alpha，正是量化私募 7 月回撤教训的工程化回应。

> **与 [36_var_es_monitoring](36_var_es_monitoring.md) 联动**：量化私募回撤期间"流动性阶段性承压"→ VaR/ES 估计的流动性调整因子（Liquidity Adjustment VaR, L-VaR）须在极端行情下放大。§3.16 归因中"流动性归因"维度 + 37 号流动性危机 Protocol 是踩踏效应的对冲设计。

**国际平行案例：2026-08 韩国 KOSPI SideCar 连环熔断**（[新华财经/21世纪经济报道 2026-08-06](https://www.cnfin.com)）：

> KOSPI 2026-06-19 见顶后近 40% 回撤；2026 年内 9 次全市场熔断（此前 25 年合计仅 6 次）；SideCar（程序化卖盘 5 分钟暂停）触发逾 70 次；7-28/29 首次连续 2 日熔断；7 月跌 33.19%（1997 以来纪录），7-31 单日涨近 18%。**根因**：三层嵌套杠杆（场外借钱 + 场内融资 + 产品杠杆如 2x ETF）集中于三星/SK 海力士（合计占 KOSPI 权重~60%），5-7 月强制平仓 2.3 万亿韩元，120 万账户追保，30 万账户清零。**监管响应**：暂停新上市杠杆 ETF、保证金 1000 万→3000 万韩元、最小交易单位 1→20 份、拟引入"紧急行动权限"快速下调杠杆倍数。

| KOSPI 教训 | 本项目对应设计 | 适用性 |
|---|---|---|
| 杠杆 ETF 日内再平衡的**顺周期放大**（负 Gamma 做市商强化抛售） | §3.5 Kill Switch 不可覆盖 + §3.20 hysteresis min_hold 防 thrashing | ★★☆ 中——A 股无个股杠杆 ETF，但融资融券+两融集中度有类似脆弱性 |
| 三层嵌套杠杆→保证金追缴→**流动性挤兑**连环反馈 | 37 号流动性危机 Protocol + §3.16 相关性崩溃归因（avg_corr>0.8） | ★★★ 强——流动性挤兑是 37 号要防御的核心场景 |
| 60% 权重集中于 2 只股票→**集中度风险** | [31_position_sizing](31_position_sizing.md) §2.4 单票 8% 上限 + 行业上限 | ★★★ 强——A 股个人系统单票 8% 硬上限直接防御集中度风险 |
| SideCar 70+ 次触发→**circuit breaker 频繁暂停**反效果 | §3.7 Kill Switch 不可覆盖（非 circuit breaker）+ §3.20 hysteresis 防频繁触发 | ★★☆ 中——本项目 kill switch 是终止非暂停，但 hysteresis 防 thrashing 思路一致 |

> **裁决**：KOSPI 案例作为 Kill Switch 压力测试**国际剧本**纳入 §6.11 4 层架构施工验证——特别是"杠杆产品再平衡触发连环抛售"路径的模拟。A 股虽无个股杠杆 ETF，但融资融券+两融集中度的脆弱性同构。Kill Switch 的"分批拆单 + 撤单率控制"（§3.5.1 A 股 2026 新规适配）在 KOSPI 式连环熔断场景下尤为重要——若全市场同时触发 kill switch，15 笔/秒限制下平仓队列会严重积压。

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
- 进入 RiskSignal 会产生"亏多了该更激进回本"的赌博倾向
- 只触发账户级风险节流（减仓/停仓/清仓），不进入策略 alpha 信号

### 4.5 CPPI（Constant Proportion Portfolio Insurance）—— 拒绝

- **算法**：`E = m × (V − Floor)`，风险敞口 = 乘数 × cushion（净值超底线的部分），[MetricGate 2026-06](https://metricgate.com/docs/constant-proportion-portfolio-insurance/) + [marketclutch 2026](https://marketclutch.com/buy-and-hold-vs-constant-mix-vs-cppi/)
- **优势**：cushion 随亏损自动缩小 → 仓位自动下降，天然实现"回撤越深仓位越轻"，无需分级阈值；连续函数比阶梯更平滑
- **拒绝理由**：
  1. **cash-lock 风险**：cushion = 0 后全仓现金，无法恢复（[MetricGate](https://metricgate.com/docs/constant-proportion-portfolio-insurance/)："Once the cushion hits zero the strategy is fully de-risked and cannot recover"）——个人系统不能接受"一次触底永久退出"
  2. **A 股 gap risk**：T+1 + 涨跌停制度下，隔夜跳空可能直接击穿 Floor，CPPI 的连续再平衡假设失效（需日内调仓但 A 股 T+1 不可）
  3. **无需硬底保**：CPPI 适合保险/结构化产品需保证本金的场景；个人系统无保本承诺，分层阈值 + Kill Switch 已足够
- **与当前方案对比**：当前 §3.2 三层映射是"分级阶梯"（5/10/15%），CPPI 是"连续函数"。阶梯法可解释性强（阈值明确），CPPI 的 m 值选择主观且 gap risk 下失效
- **诚实账本——东方证券 A 股实证反证（v1.19.0 补，2026-08-10 第十九轮审查）**：[东方证券 2026-04 "CPPI+风险预算"两阶段法](https://www.uufund.com/Report/Detail?id=AP202604121821139947)在 A 股 2006-2026 全样本回测显示 CPPI **在 A 股可生效**——第一阶段 CPPI 优化单资产夏普比，第二阶段风险预算（RB）配置，年化 13.41%/波动 8.45%/MaxDD -10.91%/Sharpe 1.53/Calmar 1.23，优于等权和纯 RP 组合。三层风险控制：CPPI 保本期 max 损失约束 + 动态回撤控制 + 风险预算分散。**这是对拒绝理由#2"A 股 gap risk 使 CPPI 失效"的重要反证**——东方证券用三层架构兜底 gap risk（动态回撤控制层），而非裸 CPPI。**为何仍不采纳**：①**定位正交**——东方证券 CPPI 是**组合配置层**（单资产 Sharpe 优化 + 多资产 RB 分散），本项目回撤 Protocol 是 **sleeve 级风险节流**（[30号 §2.2](30_multi_strategy_concurrency.md)"风险节流器非策略"），两者层级不同不可直接套用；②**无保本承诺**——东方证券 CPPI 第一阶段需"保本期 max 损失约束"对应保险/结构化产品保本场景，拒绝理由#3（个人系统无保本承诺）仍成立，本项目的 Kill Switch + 四级回撤已替代"保本"语义；③**架构耦合**——东方证券三层控制（CPPI+动态回撤+RB）是组合配置一体化设计，拆出单层 CPPI 套到本项目 sleeve 级会破坏其三层协同（gap risk 兜底依赖动态回撤控制层，裸 CPPI 仍有 gap risk）；④**可解释性优先**——本项目风控要可解释（[project_memory] 风险优先原则 + Kill Switch 不可覆盖），CPPI 的 m 值选择主观，5/10/15% 阈值更明确。**借鉴价值**：东方证券"动态回撤控制"层与本项目 §3.20 Hysteresis 双阈值 + §3.4 recovery_factor 阶梯思路同构——两者都是"回撤越深仓位越轻"的反馈式，本项目用离散阶梯实现可解释性，东方证券用连续函数实现平滑性，是同一设计原则的不同工程实现。登记为 §6.30 待裁定（CPPI+RB 两阶段法组合配置层远期候选，仅当项目演进到"组合配置层"独立模块时重新评估，当前 sleeve 级 + firm 级两层架构不引入第三层）。

### 4.6 Ulcer Index 替代回撤度量 —— 暂缓

- **算法**：`UI = sqrt((1/N) × Σ DD_t²)`，同时惩罚回撤**深度**和**持续时间**，[IR-Tracker 2026-02](https://www.ir-tracker.com/en/columns/advanced-strategy/drawdown-management)
- **优势**：`drawdown_pct` 是单点值（只看当前深度），UI 还考虑"在水下待了多久"——10% 回撤持续 1 天 vs 持续 30 天，UI 差异巨大，更符合"回撤痛苦=深度×时间"的直觉
- **暂缓理由**：
  1. 当前 `drawdown_tracker` 的 `drawdown_pct` 单点值足够 MVP（触发分层响应）
  2. UI 需维护滚动窗口的 DD_t 序列，增加状态管理复杂度
  3. UI 的触发阈值无行业标准（不像 8/15/20/25% 有机构基准），需自行校准
- **重评条件**：实盘运行后若发现"浅回撤长时间"比"深回撤短时间"更危险（UI 高但 drawdown_pct 低），引入 UI 作为补充触发条件（§6.8）

### 4.7 Time-in-Drawdown Kill Switch（时间维度 Kill Switch）—— 暂缓

- **算法**：`T_kill = MaxDDD_OOS × 1.5`，当策略在水下（低于高水位）的**连续时间**超过 OOS 最大回撤期的 1.5 倍时，触发不可逆停机。[invistaja 2026-08-02](https://invistaja.app.br/time-in-drawdown-algotrading/) 基于理论支撑 [Rej, Seager & Bouchaud (2017, arxiv 1707.01457)](https://arxiv.org/abs/1707.01457)：drawdown 持续时间随 Sharpe 的**平方**下降——高 Sharpe 策略回撤期短，低 Sharpe 策略回撤期长，TiD 是比 depth 更敏感的"策略失效"信号
- **与 Ulcer Index（§4.6）的关系**：UI 度量"深度×时间"的痛苦指数（连续值，触发减仓），TiD Kill Switch 是"纯时间"的硬停机（离散值，触发不可逆退出）。UI 是节流阀，TiD Kill Switch 是断路器
- **优势**：① 捕获"浅回撤长时间"的隐性失效——depth 永远不触 25% 但策略已失效（alpha 衰减）；② 不可逆设计强制"策略重评估"，避免长期占用资金在水下策略；③ 理论基础扎实（Bouchaud 物理金融学派实证）
- **暂缓理由**：
  1. **MaxDDD_OOS 依赖回测**：个人系统实盘样本短（<6 个月），OOS 最大回撤期估计不准；需先累积 ≥1 年实盘或用 walk-forward 回测估
  2. **不可逆过激**：`T_kill` 触发即永久停机，个人系统策略数少（3-5 个），误杀一个策略成本高；当前 Kill Switch（§3.5）是"可人工复位"的，TiD 是"不可逆"的，强度跳变
  3. **与 regime 转换冲突**：市场 regime 转换期（如牛→熊）所有策略同步回撤，TiD 会同时停掉多个策略，丧失恢复机会
- **重评条件**：实盘 ≥1 年后，若发现某策略长期在水下（TiD 高但 depth 低）且 alpha 确已衰减（IC 衰减监控验证），引入 TiD 作为该策略的退役触发（§6.9）

### 4.8 CUSUM + Hawkes + Lee-Mykland 统计检测触发 —— 暂缓

- **算法**：用统计异常检测替代"阈值触发"的 Kill Switch / 回撤告警，[Tugbars/Finance-Kill-Switch 2025-11](https://github.com/Tugbars/Finance-Kill-Switch) 实现：
  - **CUSUM**（Cumulative Sum）：检测收益序列的**均值漂移**——策略 alpha 衰减时累积偏差超阈值告警，比固定回撤阈值更早发现"策略开始失效"
  - **Hawkes 过程**：自激励点过程，检测亏损事件的**时序聚集**——一次大亏后后续大亏概率上升（聚类），比"连续 5 天亏损"的硬计数更严谨
  - **Lee-Mykland 检验**：检测收益序列的**跳跃**——区分连续漂移亏损 vs 离散跳跃亏损，前者归因策略失效，后者归因黑天鹅
- **与当前阈值触发的对比**：
  | 维度 | 当前阈值触发 | 统计检测触发 |
  |---|---|---|
  | 回撤告警 | drawdown > 5/10/15% 固定阈值 | CUSUM 检测均值漂移，自适应策略 alpha 衰减 |
  | 连续亏损 | "连续 5 天" 硬计数（§3.5，待实现 §6.2）| Hawkes 检测聚类强度，区分独立亏损 vs 聚集亏损 |
  | 黑天鹅 | BS-007 多模式同触发（§3.5）| Lee-Mykland 检测跳跃显著性，区分漂移 vs 跳跃 |
- **暂缓理由**：
  1. **复杂度高**：CUSUM 阈值校准 + Hawkes λ 参数估计 + Lee-Mykland 检验统计量，三套统计模型，远超当前阈值法的可解释性
  2. **个人系统样本短**：Hawkes λ 估计需足够亏损事件样本，3-4 个月开发期不足
  3. **当前阈值法已 production**：drawdown_tracker 5/10/15% + BS-007 已串联，统计检测是更优但非必需
- **重评条件**：实盘 ≥1 年后，若发现①阈值法误触发频繁（CUSUM 可校准自适应阈值）②连续亏损检测判别力不足（Hawkes 可量化聚集强度）③黑天鹅误报多（Lee-Mykland 可区分跳跃 vs 漂移），引入统计检测作为 §6.7 回撤类型诊断的算法升级（§6.10）
- **实践调参指南**（[Iyer 2026-01 "CUSUM, Bayes, and the Art of Knowing When to Quit"](https://mathandmarkets.com/p/detecting-decay-in-real-time-when) + [Iyer 2026-02 "Ensemble Regime Detection"](https://mathandmarkets.com/p/regime-detection-part-3-beyond-hmms)）：
  - **CUSUM 起始参数**：k=0.5σ（参考偏差），h=4σ（阈值）——Sharpe~1 策略在真实变点后约 50 个交易日触发（≈2 个月），提供足够提前量
  - **三信号框架**：CUSUM（快但需指定 μ₀）+ BOCPD（给概率而非二元标志，可按概率缩减仓位）+ 滚动夏普——无单一测试完美，集成使用
  - **BOCPD 概率驱动仓位**：BOCPD 输出变点概率 p∈[0,1]，可直接用于动态缩减仓位（`position_cap *= (1 - p * reduction_factor)`），实现"软 kill switch"——比二元阈值更平滑
  - **与 §4.18 BOCD 的关系**：Iyer 的 BOCPD 即 §4.18 的 Adams-MacKay BOCD，本指南提供 A 股适配的实践参数和"概率驱动仓位"的工程化路径

### 4.9 Pain Index（水下面积）—— 暂缓

- **算法**：`PI = (1/T) × Σ|DD_t|`，即回撤深度的**时间平均**（"水下面积"），[tradingwyckoff 2026-01](https://www.tradingwyckoff.com/en/algorithmic-trading/drawdown-trading-guide/) 与 Ulcer Index 同源但更简——UI 是 `sqrt(mean(DD_t²))`（平方惩罚深度），PI 是 `mean(|DD_t|)`（线性，无平方）
- **与 Ulcer Index（§4.6）的关系**：
  | 度量 | 公式 | 惩罚维度 | 直觉 |
  |---|---|---|---|
  | drawdown_pct（当前） | 单点 DD_t | 仅深度（瞬时） | "现在亏多少" |
  | Pain Index | mean(\|DD_t\|) | 深度 × 时间（线性） | "水下平均深度" |
  | Ulcer Index | sqrt(mean(DD_t²)) | 深度 × 时间（平方惩罚深谷） | "水下痛苦度（深谷加权）" |
  - PI 对"浅回撤长时间"和"深回撤短时间"一视同仁（线性），UI 偏罚深谷——PI 更直觉，UI 更敏感于极端回撤
- **优势**：① 比 UI 更易解释（"平均水下深度"比"均方根水下深度"直觉）；② 计算更简（无开方）；③ 与 Calmar Ratio（年化收益/MaxDD）互补——Calmar 看峰值回撤，PI 看平均回撤
- **暂缓理由**：
  1. 与 UI（§4.6）同类，UI 已暂缓则 PI 无独立引入必要（两者择一，UI 因平方惩罚更敏感而优先）
  2. 当前 `drawdown_pct` 单点值足够 MVP（§4.6 已论证）
  3. PI 的触发阈值同样无行业标准（与 UI 同困）
- **重评条件**：与 §4.6 Ulcer Index 同步重评；若实盘发现"UI 高但 drawdown_pct 低"的浅回撤长时间场景，UI 作为触发条件引入，PI 作为 UI 的可解释性辅助度量（报告展示用，不参与触发）

### 4.10 TradeShield 静态+Trailing 双模式回撤 —— 部分采纳

- **算法**：[PropGuard TradeShield 2026-08-08](https://github.com/youcefbibo53/PropGuard-Trailing-Equity-Armor/) 双模式：① **静态模式**（static）= 回撤相对**初始本金**的固定百分比（如初始 100 万，回撤 >5% 即触发，与账户增长无关）；② **Trailing 模式**（trailing）= 回撤相对**峰值净值**（peak NAV）的百分比（账户涨到 150 万后，回撤从 150 万算 5% = 7.5 万）
- **与当前方案对比**：
  | 模式 | 当前项目 | TradeShield 双模式 |
  |---|---|---|
  | Trailing（peak 基准） | ✅ 已实现（§3.8 capital_curve_manager peak NAV） | ✅ 同 |
  | Static（初始本金基准） | ❌ 无 | ✅ 第二道线 |
  - 当前项目**只有 trailing 模式**（§3.8 peak NAV），无 static 模式。trailing 的问题：账户大幅盈利后，trailing 5% 的绝对金额很大（如 200 万 × 5% = 10 万），但相对初始本金的回撤可能已 >20%（200 万跌 10 万 = 190 万，仍赚 90 万，但若继续跌到 160 万则回 initial 的 20% 而 trailing 只算 20%）
- **优势**：双模式提供"盈利保护"（trailing）+ "本金保护"（static）两道线，任一触发即响应。static 模式是"无论如何不能亏初始本金的 X%"的硬底线
- **部分采纳理由**：
  1. **trailing 已实现**（§3.8），无需改动
  2. **static 模式价值有限**——个人系统无 prop firm 的"初始本金红线"考核（prop firm 触红线即淘汰），个人账户的"初始本金"是心理锚点非硬约束。账户从 100 万涨到 200 万后回撤到 160 万（initial +60%），trailing 算 20% 回撤（已触发 CRISIS），无需 static 再触发
  3. **但作为"破产底线"有保留价值**：若账户从 100 万涨到 500 万后回撤，trailing 25%（Kill Switch）= 跌到 375 万（仍赚 275 万），但若市场极端（如 2008 式崩盘），可能一路跌破 initial 100 万——static 模式（initial × 0.85 = 85 万即 Kill Switch）是"绝对破产防护"
- **裁决**：trailing 模式保留（已实现），static 模式作为"绝对破产底线"暂缓——在 §3.5 Kill Switch 触发条件表新增"组合净值 < 初始本金 × 0.85"作为**第五类触发源**（绝对底线，与回撤 25% 并列），待 §6.11 施工时实现。理由：个人系统初始本金是真实资金，跌破 85% 是实质性亏损（非盈利回吐），应有独立 Kill Switch 触发，不依赖 trailing 的 25%（可能因大幅盈利后 trailing 25% 仍远高于 initial）

### 4.11 Hierarchical Risk Parity 聚类归因 —— 暂缓

- **算法**：[López de Prado 2016](https://quantresearch.org/Publications.htm) HRP 用相关性矩阵的层次聚类树做风险分配，[marketmaker.cc 2026](https://marketmaker.cc/en/research/) "When Does HRP Beat Markowitz?" 在 4800 次实验中验证 HRP 在 T/N 比低、结构化协方差下优于 sample/Ledoit-Wolf min-variance 和 1/N。对归因的价值：HRP 的**聚类树**可识别"策略簇"——哪些策略在高相关簇内同步回撤
- **与当前 §3.16 归因的关系**：当前用平均相关系数（`avg_corr > 0.7` = 系统性 / `< 0.4` = 策略特定），HRP 聚类树更精细——5 个策略中 3 个高相关同步亏、2 个独立，`avg_corr` 被 2 个独立的拉低（可能 <0.4 误判为策略特定），HRP 聚类能识别"3 个策略形成的簇"独立归因为"部分系统性"
- **优势**：① 识别策略簇（部分系统性 vs 全局系统性），比二元 avg_corr 阈值更精确；② 聚类树可视化，归因结果可解释；③ marketmaker.cc 2026 实证 HRP 在结构化协方差下优于 1/N 和 inverse-var
- **暂缓理由**：
  1. **策略数不足**：当前 3-5 个策略，层次聚类树太简单（3 个节点 2 个分支），统计意义有限；HRP 需 ≥8 个策略才有聚类价值
  2. **avg_corr 足够 MVP**：3-5 个策略下 avg_corr 阈值法（>0.7/<0.4）判别力足够，"部分系统性"场景（簇内高 + 簇间低）在策略数少时罕见
  3. **HRP 权重分配属于 G12**：HRP 本身是组合权重分配算法，属于 [31_position_sizing](31_position_sizing.md) / [32_firm_risk_aggregator](32_firm_risk_aggregator.md) 范畴，非 G16 回撤归因；本备忘只借其聚类树做归因
- **重评条件**：策略数扩展到 ≥8 个后，若平均相关系数无法区分"部分系统性"（簇内高相关 + 簇间低相关），引入 HRP 聚类树作为 §3.16 归因增强（§6.16 与六类框架同步评估）

### 4.12 MPC 连续风险厌恶调整 —— 暂缓（P4 远期）

- **算法**：[Nystrup, Boyd, Lindström & Madsen 2019 (Annals of Operations Research)](https://backend.orbit.dtu.dk/ws/files/149812772/Multi_Period_Portfolio_Selection_with_Drawdown_Control.pdf) 用 Model Predictive Control 动态优化投资组合，核心创新是**根据已实现回撤调整风险厌恶系数**（risk aversion based on realized drawdown）——风险厌恶 γ 是回撤的连续函数 `γ(dd)` 而非离散阈值。基于多变量 HMM 预测多期收益均值/协方差，receding-horizon 每期重优化。实证成功控制回撤且几乎不牺牲均值-方差效率；杠杆可进一步提高收益不增 MaxDD。[arXiv:2604.00415 DLP-SMPC 2026-04](https://arxiv.org/html/2604.00415v1)（NTHU）是同类工作，用随机 MPC 优化 Double Linear Policy 动态权重，TSLA MaxDD 12.17% vs Buy-and-Hold 73.63%，Sharpe 1.42 vs 1.03
- **优势**：① **连续风险厌恶**替代离散阈值——当前 §3.2 三层映射是阶梯式（80%→50%→30%→0%），MPC 是连续函数，避免阶梯边界的"差 0.1% 就跳级"突变；② **前馈+反馈结合**——HMM 预测是前馈（基于收益分布预测），回撤调整是反馈（基于已实现回撤），当前 Protocol 纯反馈；③ 交易/持仓成本作为估计误差的正则化手段，天然处理参数不确定性
- **与当前方案的对比**：
  | 维度 | 当前 §3.2 三层映射 | MPC 连续风险厌恶 |
  |---|---|---|
  | 风险厌恶 | 离散阶梯（5/10/15% → 80/50/30%）| 连续函数 γ(dd) |
  | 时间维度 | 单期（当日回撤 → 当日仓位）| 多期（HMM 预测 N 期，receding-horizon）|
  | 前馈/反馈 | 纯反馈（已亏才减）| 前馈（HMM 预测）+ 反馈（回撤调整）|
  | 计算复杂度 | O(1) 阈值比较 | O(N³) 每期凸优化 + HMM 参数估计 |
  | 可解释性 | 高（阈值明确）| 低（γ 函数 + HMM 隐状态）|
- **暂缓理由**：
  1. **HMM 需长样本**：多变量 HMM 预测多期收益均值/协方差需 ≥2 年稳定实盘样本，本项目实盘 <6 个月，参数估计不可靠——HMM 在短样本下易过拟合，前馈预测失效则 MPC 退化为纯反馈（与当前阈值法等效）
  2. **alpha 层未成熟**：MPC 的前馈依赖收益分布预测（HMM 喂 μ/Σ），本项目当前 regime 是市场状态分类（CALM_BULL/ACCEL_DECLINE 等）非收益预测，无 μ/Σ 输入源——MPC 前馈无数据基础
  3. **杠杆不适用**：Nystrup 论文核心卖点之一"杠杆提高收益不增 MaxDD"在 A 股个人账户融资融券受限下不适用
  4. **可解释性硬约束**：个人系统业主需理解每笔风控动作依据，连续 γ(dd) 函数难向业主解释"为什么这个回撤深度减这个仓位"
- **重评条件**：① 实盘 ≥2 年稳定样本；② alpha 层收益预测模块（HMM 或等价物）production；③ 业主对连续风控的接受度验证后，引入 MPC 作为 §3.2 三层映射的演进方向（§6.17，P4 远期）。当前 recovery_factor 0.25→0.50→0.75 阶梯是 MPC 连续风险厌恶的**离散近似**，待 MPC 落地后可平滑化

### 4.13 趋势跟踪回撤防御层 —— 暂缓（P4，A 股需裁定）

- **算法**：[Noguer i Alonso & Al-Fallouji 2026-07 (arXiv:2607.00883)](https://arxiv.org/html/2607.00883v1) AIFI/Mirabaud 连续时间 CVaR 框架，将 OTM 看跌期权 + 系统化趋势跟踪放入一个连贯的尾部风险 mandate。**时间分离核心洞察**：凸性保险（puts）在跳跃冲击时立即重新定价；趋势跟踪在首次冲击时滞后（信号须穿过零），但在**持续回撤中越来越防御性**，无需新期权费。四轴诊断层：条件凸性 / 尾部事件可靠性 / 非压力 carry / 回撤持续性。CVaR 策略梯度恒等式。[AQR 实证](https://philippdubach.com/posts/long-volatility-premium/)：puts 在 COVID 突然崩盘赢（+42%），trend-following 在 dot-com 持续熊市赢——两者时间分离互补
- **优势**：① **前馈防御**——当前 Protocol 是纯反馈（已亏才减仓），趋势跟踪是"持续回撤中递增防御"的前馈层，无需预测回撤本身，只需跟踪价格趋势信号；② **无期权费成本**——A 股无期权，趋势跟踪是唯一可行的"持续回撤防御"形态；③ 与 §3.9 regime 正交——regime 是市场状态分类，趋势信号是价格动量，两者互补
- **A 股约束的适配问题**：
  | 原论文假设 | A 股约束 | 适配方案 |
  |---|---|---|
  | 可做空（趋势跟踪做空对冲）| 不能做空 | 只能"减仓/空仓"实现防御，不能"做空对冲" |
  | OTM puts 可买 | 无期权 | 趋势跟踪是唯一防御层，无凸性保险 |
  | T+0 可日内调仓 | T+1 | 趋势信号须日度生成，日内无法反转 |
  | 多资产分散 | A 股单一市场 | 趋势信号在单一市场内有效性降低 |
- **暂缓理由**：
  1. **A 股趋势跟踪有效性未验证**：A 股牛短熊长、政策驱动、散户占比高，趋势跟踪的"持续回撤递增防御"在 A 股的回撤持续性模式（vs 美股）需实盘验证
  2. **与 regime 的职责重叠**：§3.9 regime Shrinkage 已承担"市场状态前馈"，趋势跟踪防御层是另一套前馈机制，两者职责边界需裁定（regime 是状态分类，趋势是价格动量，是否冗余？）
  3. **趋势信号来源未定**：当前项目无趋势跟踪策略，趋势信号（如均线穿越/动量）从哪个模块生成未定，需与 G09 多因子策略 / G10 趋势策略协调
- **重评条件**：① 实盘验证 A 股趋势信号在持续回撤中的防御有效性；② 与 [34_regime_meta_allocator](34_regime_meta_allocator.md) 裁定 regime vs 趋势跟踪的职责边界；③ 趋势信号来源模块确定后，引入趋势跟踪作为 §3.9 regime 之外的**第二前馈防御层**（§6.18，P4 远期）。当前 §3.4 恢复阶梯是"回撤后阶梯恢复"，未实现"持续回撤递增防御"的前馈层

### 4.14 CDaR 回撤深度连续度量 —— 暂缓（P2，与 UI/PI 同类但更优）

- **算法**：[Chekhlov, Uryasev & Zabarankin 2000/2005](https://uryasev.ams.stonybrook.edu/wp-content/uploads/2021/10/Drawdown_Portfolio_Optimization_Problems_and_Drawdown_Betas.pdf) Conditional Drawdown-at-Risk（CDaR）= drawdown 序列的 CVaR，即"最差 α% 回撤的平均值"。[MetricGate 2026-06](https://metricgate.com/docs/conditional-drawdown-at-risk/) 论证 CDaR 是 coherent risk measure（monotonicity / sub-additivity / positive homogeneity / translation invariance），α→0 收敛 MaxDD，α→1 收敛 average DD，可作凸优化目标。[Uryasev & Ding](https://uryasev.ams.stonybrook.edu/wp-content/uploads/2021/10/Drawdown_Portfolio_Optimization_Problems_and_Drawdown_Betas.pdf) 引入 ERoD（Expected Regret of Drawdown）并证明与 CDaR 优化等价，导出 ERoD Beta（市场回撤时证券的平均损失比率）。[Man Numeric CVaR 2025-07, Joshua Levin](https://www.man.com/man-numeric-cvar-insights) 论证 CVaR 优于方差：能区分"平稳上涨"vs"暴涨暴跌"组合（同等方差但回撤特性天壤之别），Portfolio One CVaR₀.₄=−1.32% vs Portfolio Two CVaR₀.₄=−1.78%——CDaR 把此思路应用到 drawdown 序列
- **与当前 §3.8 度量及 §4.6/§4.9 暂缓项的关系**：
  | 度量 | 公式 | 捕获维度 | 当前状态 |
  |---|---|---|---|
  | drawdown_pct（当前 §3.8）| 单点 DD_t | 仅瞬时深度 | ✅ 已实现 |
  | Ulcer Index（§4.6 暂缓）| sqrt(mean(DD_t²)) | 深度×时间（平方惩罚深谷）| 暂缓 |
  | Pain Index（§4.9 暂缓）| mean(\|DD_t\|) | 深度×时间（线性）| 暂缓 |
  | **CDaR（本节）** | mean(worst α% of DD_t) | **尾部回撤均值（path-dependent）** | 暂缓（P2）|
  - CDaR 与 UI/PI 的本质区别：UI/PI 是全样本平均（所有 DD_t），CDaR 是**尾部均值**（仅最差 α%）——CDaR 聚焦"真正痛苦的回撤"而非稀释于长期平静期。[MetricGate 2026-06](https://metricgate.com/docs/conditional-drawdown-at-risk/)："CDaR is far more stable than maximum drawdown yet still concentrated on the genuinely painful losses rather than diluted by long quiet stretches near the peak"
- **优势**：① **coherent risk measure**——满足次可加性（分散化不增风险），MaxDD 不满足（单点非 coherent）；② **LP 可解**——Rockafellar-Uryasev 公式使 CDaR 优化可转线性规划，[PyPortfolioOpt EfficientCDaR](https://blog.csdn.net/gitblog_00739/article/details/148508135) 已有 Python 实现；③ **path-dependent**——捕获回撤的持续性，比单点 drawdown_pct 更贴近"投资者真实痛苦"；④ **可作组合优化目标**——CDaR 约束可嵌入 [31_position_sizing](31_position_sizing.md) 的仓位优化（当前用 VaR/CVaR 约束，CDaR 是回撤维度的等价物）
- **暂缓理由**：
  1. **与 UI/PI 同类择一**：UI（§4.6）已暂缓，CDaR 是更优的同类（coherent + LP 可解 + 尾部聚焦），但需先验证"单点 drawdown_pct 不足"的实盘证据（UI 的重评条件同样适用 CDaR）
  2. **阈值校准无行业标准**：CDaR 的 α 选择（0.05 vs 0.10）无机构基准，不像 8/15/20/25% 有行业基准——需自行校准
  3. **当前 drawdown_pct 足够 MVP**：§4.6 已论证单点值足够触发分层响应；CDaR 的价值在于"组合优化目标"而非"触发阈值"——后者当前无需，前者属 G12 仓位优化范畴
- **重评条件**：与 §4.6 UI / §4.9 PI 同步重评。优先级高于 UI/PI（因 CDaR 是 coherent + LP 可解），实盘发现"浅回撤长时间"或"单点 drawdown_pct 不足以反映回撤痛苦"后，引入 CDaR 作为 ① 回撤深度补充度量（报告展示）+ ② [31_position_sizing](31_position_sizing.md) 仓位优化的回撤约束（§6.19，P2）。[Man Numeric CVaR 论证](https://www.man.com/man-numeric-cvar-insights) CVaR 优于方差同样适用于 CDaR 优于 MaxDD

### 4.15 多 agent 协作回撤控制 —— 拒绝（过度工程，仅借鉴思路）

- **算法**：[RMATS 2026-05 (arXiv:2605.25311)](https://arxiv.org/abs/2605.25311) Washington University 递归多 agent 交易系统，4 个专门 agent（Sentiment / Report / Analysis / Risk）+ 递归 Manager Agent 协调，typed message passing + 收敛保证 ‖w^(r+1)−w^(r)‖₂<ε。561 交易日回测 MaxDD 9.62%（vs MVO 15.49% / FinBERT 15.28%），5 个地缘政治压力场景中 3 个事件期回撤最低。Risk Agent 用 CVaR + EWMA 动态协方差 + 多级 circuit breaker（DD/GRS/vol 三源 OR），RL 目标 `R_t = r_t − λ₁σ_t − λ₂max(0, DD_t − θ)`（λ₁=0.8, λ₂=1.5 重罚回撤）。[MARCD 2026 (arXiv:2510.10807)](https://arxiv.org/html/2510.10807v3) 是同类工作，Gaussian HMM regime + diffusion 生成场景 + CVaR epigraph QP 分配器，MaxDD 9.3% vs BL 14.1%（2020-2025 OOS 降 34%）
- **优势**：① **Risk Agent 独立于策略 agent**——回撤控制与收益追求职责分离，避免策略 agent 为追求收益而放宽风控；② **递归协调**——多轮 message passing 使各 agent 信号收敛，比固定流水线更鲁棒；③ **多源融合**——Sentiment（情绪）+ Report（财报）+ Analysis（宏观+HMM regime）+ Risk（CVaR+circuit breaker）四源输入，比单一回撤信号丰富
- **拒绝理由（过度工程）**：
  1. **个人项目不需要多 agent 协作**：RMATS 是机构级 24 资产、4 agent 协作、递归收敛的架构，本项目 3-5 个 A 股策略、单进程规则式风控已足够。多 agent 的递归 message passing（typed schema + 收敛判断）引入分布式系统复杂度（消息序列化/反序列化/超时/重试），收益不抵成本
  2. **LLM agent 的 alpha 不可作部署证据**：[arXiv:2605.16895 The Alpha Illusion 2026-05](https://arxiv.org/html/2605.16895v1)（Fudan/Imperial College）警示：LLM/多 agent 报告的 alpha 在通过 temporal integrity / real-world frictions / counterfactual robustness / predictive calibration / numerical execution / multi-agent disaggregation 等结构有效性测试前，不应作部署证据。RMATS 的 Sentiment/Report agent 依赖 LLM，其 alpha 报告需打折看待
  3. **Risk Agent 独立性本项目已实现**：§4.2 已拒绝合并 tracker/curve_manager/controller，三者职责分离（监控/节流/综合裁决）正是"Risk 独立于策略"的体现——RMATS 的核心优势本项目已通过模块化获得，无需多 agent 架构
  4. **RL 目标函数的回撤惩罚项已评估**：§3.9 已对比 RMATS 的加性惩罚 `R_t = r_t − λ₁σ_t − λ₂max(0, DD_t − θ)` vs 本项目乘性叠加 `cap = regime × drawdown`，选乘性（理由：任一因子为 0 则总仓位为 0、仓位上限语义天然、可拆解归因）
- **借鉴范围**（不照搬架构，只借鉴思路）：
  | RMATS/MARCD 思路 | 本项目借鉴方式 | 对应章节 |
  |---|---|---|
  | Risk Agent 独立于策略 | 已实现（tracker/curve_manager/controller 三模块分离）| §3.1/§4.2 |
  | RL 目标回撤惩罚项 | 评估后选乘性叠加替代加性 | §3.9 |
  | CVaR + EWMA 动态协方差 | 已在 [36_var_es_monitoring](36_var_es_monitoring.md) 实现 | G17 |
  | 多级 circuit breaker（DD/GRS/vol 三源 OR）| 本项目 Kill Switch 多源 OR（回撤/单日亏损/流动性/黑天鹅，§3.5）| §3.5 |
  | HMM regime 分类 | 本项目 regime 是分类（非 HMM），属 [34_regime_meta_allocator](34_regime_meta_allocator.md) | G15 |
- **不设重评条件**：多 agent 架构的复杂度与个人项目定位根本不匹配，即使实盘 ≥1 年也不引入。若未来项目规模扩展到机构级（≥20 策略 + 多资产 + 团队运营），可重新评估

### 4.16 Conditional Expected Drawdown（CED）线性因子归因 —— 暂缓

- **算法**：[Goldberg & Mahmoud 2016 (Mathematical and Financial Economics, DOI 10.1007/s11579-016-0181-9)](https://alexandria.unisg.ch/server/api/core/bitstreams/f53d98e4-3cfb-4517-8054-8287a2912bc8/content) UC Berkeley + St. Gallen 提出 Conditional Expected Drawdown (CED)，定义为 maximum drawdown 分布的尾部均值：CED_α(X) = E(μ(X) | μ(X) > DT_α)，其中 μ(X) 是路径 X 的最大回撤，DT_α 是最大回撤分布的 α 分位数。CED 是 **degree one positive homogenous risk measure**（正齐次）→ 可用 Euler 齐次函数定理线性归因到因子；**convex**（凸）→ 可用于优化（促进分散化）；**deviation measure**（Rockafellar et al. 2002, 2006 的偏离度量）。[arxiv 1404.7493v3](https://arxiv.org/pdf/1404.7493v3) 提供 minimum CED 优化的高效线性规划算法 + CED/ES/volatility 风险归因差异实证。[internQuant/conditional-drawdown](https://github.com/internQuant/conditional-drawdown) 提供 Python 实现（CED + MDD + Rolling MDD + Portfolio Risk Attribution）。

- **与 §3.16 回撤归因的关系**：当前 §3.16 用 avg_corr 启发式（>0.7 系统性 / <0.4 策略特定）做归因，CED 提供更严谨的**线性因子归因**框架——由 positive homogeneity + Euler 定理，组合 CED 可分解为各因子 CED 贡献之和：CED(P) = Σ w_i · MRC_i^CED(P)，其中 MRC_i^CED = ∂CED(P)/∂w_i 是因子 i 的边际 CED 贡献。这比 avg_corr 二元阈值更精确——avg_corr 只判"系统性 vs 策略特定"，CED 归因能量化每个策略/因子对回撤的具体贡献度。

- **与 §4.14 CDaR 的关系**：两者都是 drawdown 的尾部度量，但：
  | 度量 | 定义 | 捕获维度 | 优化 | 归因 | 当前状态 |
  |---|---|---|---|---|---|
  | CDaR（§4.14，Chekhlov/Uryasev）| drawdown 序列的 CVaR | 每时点 drawdown 的尾部均值 | LP 可解（组合优化）| 无显式归因 | 暂缓（P2）|
  | CED（本节，Goldberg/Mahmoud）| maximum drawdown 分布的尾部均值 | 整条路径最大 drawdown 的尾部均值 | LP 可解 | **Euler 线性归因** | 暂缓（P3）|
  - CDaR 强调**组合优化**，CED 强调**线性因子归因** + **serial correlation 敏感性**
  - CED 对 serial correlation 敏感是独特优势——Goldberg/Mahmoud AR(1) 实证：CED 与自回归参数的相关性远高于 ES 或 volatility（US Equity + US Bonds），回撤本质是路径依赖（serial correlation 放大回撤），CED 捕获这一特性而 ES/volatility 不敏感

- **优势**：① **线性因子归因**——positive homogeneity + Euler 定理使 CED 可精确分解到各因子贡献，比 avg_corr 启发式严谨；② **对 serial correlation 敏感**——回撤本质是路径依赖（serial correlation 放大回撤），CED 捕获这一特性而 ES/volatility 不敏感；③ **convex**——可用于优化（促进分散化）；④ **deviation measure**——满足 Rockafellar 偏离度量公理

- **暂缓理由**：
  1. **样本需求**：CED 需足够路径样本估计 maximum drawdown 分布的尾部，当前 3-4 个月开发期样本不足
  2. **与 §3.16 avg_corr 足够 MVP**：3-5 个策略下 avg_corr 阈值法判别力足够，CED 的线性归因价值在策略数多（≥8）时才显著
  3. **与 §4.14 CDaR 优先级**：CDaR 是 coherent risk measure + LP 可解（组合优化），CED 是 deviation measure（归因），当前 §3.16 归因用 avg_corr 已满足，优先级低于 CDaR
  4. **策略数不足**：当前 3-5 个策略，CED 的 Euler 分解统计意义有限

- **重评条件**：① 策略数扩展到 ≥8 个后，avg_corr 无法区分"部分系统性"（簇内高相关 + 簇间低相关）时，引入 CED 的 Euler 线性归因作为 §3.16 归因增强；② 实盘 ≥1 年后样本充足，CED 尾部估计稳定；③ 与 §4.14 CDaR / §4.11 HRP 聚类归因同步评估（三者都是回撤归因/度量的增强，需裁定优先级与组合方式）

> **为何列入而非直接拒绝**：Goldberg & Mahmoud 2016（UC Berkeley + St. Gallen）是 drawdown 风险度量的经典理论工作，CED 的"positive homogeneity → Euler 线性归因 + serial correlation 敏感性"两特性恰好填补 §3.16 回撤归因的"线性因子归因"空白——当前 avg_corr 是启发式二元判断，CED 提供量化每个因子贡献度的严谨框架。与 §4.14 CDaR（组合优化）互补：CDaR 用于优化（LP），CED 用于归因（Euler 分解）。作为远期增强登记，避免策略数扩展后重新调研。

### 4.17 Schmitt RWC Conformal Risk Control —— 暂缓（P2，与 Conformal Kelly 互补）

- **算法**：[Marc Schmitt 2026-02 (arXiv:2602.03903, Oxford)](https://arxiv.org/pdf/2602.03903) "Taming Tail Risk in Financial Markets: Conformal Risk Control for Nonstationary Portfolio VaR" 提出 **Regime-Weighted Conformal Risk Control（RWC）**——用指数时间衰减 + regime 相似性权重校准 VaR 安全缓冲（safety buffer）。RWC 是 model-agnostic 的，wrap 任意 conditional quantile 预测器，target 一个期望 exceedance rate。在 **weighted exchangeability** 下建立有限样本覆盖保证，在 smoothly drifting regime-conditional distributions 下推导近似边界。CRSP 美股组合实证：**TWC（time-weighted conformal）是 drift 下的强默认**，RWC 增加 regime 加权可在某些设置下改善 regime-conditional 稳定性（伴随适度的 conservativeness 变化）。

  **核心公式**（safety buffer 校准）：
  ```
  buffer_t = WeightedQuantile({s_i}, weights={w_i}, level=1-α)
  w_i = exp(-λ · (T - t_i)) · regime_similarity(regime_t, regime_{t_i})
  VaR_t = base_quantile_forecast(t) + buffer_t
  ```
  其中 `s_i` 是历史预测误差（nonconformity scores），`w_i` 是时间衰减 × regime 相似性的复合权重，`buffer_t` 是校准的安全缓冲。

- **与 §6.21 Conformal Kelly（arXiv:2608.01494）的关系**：两者都是 conformal prediction 在金融风控的应用，但维度不同：
  | 维度 | Conformal Kelly（§6.21） | Schmitt RWC（本节） |
  |---|---|---|
  | 目标 | position sizing（leverage 缩减） | VaR 校准（safety buffer） |
  | 触发 | 预测区间下行连续 miss | 预测误差 nonconformity score |
  | 输出 | leverage 系数 | VaR 安全缓冲 |
  | 与回撤的关系 | 间接（leverage 缩减 → 降低 MaxDD） | 直接（VaR 是 §3.10 drawdown_controller 的 C 层输入） |
  | 设计原则 | slow unweighted per-asset rolling（稳定性优先） | TWC 强默认 + RWC regime 加权（适应性优先） |
  - Conformal Kelly 管"仓位多大"，Schmitt RWC 管"VaR 多严"——两者正交可叠加
  - Conformal Kelly 的"slow unweighted 优于 adaptive"结论与 Schmitt 的"TWC 是强默认"一致——简单时间加权足够，复杂自适应不一定更好

- **与当前 [36_var_es_monitoring](36_var_es_monitoring.md) 的关系**：当前 §3.2 参数法 VaR 假设正态分布 + 平稳，Schmitt RWC 提供"非平稳 + regime 结构"下的 distribution-free VaR 校准——直接替代或增强 [36_var_es_monitoring](36_var_es_monitoring.md) §3.2 的参数法 VaR。RWC 的 regime 相似性权重与本项目 [34_regime_meta_allocator](34_regime_meta_allocator.md) 的 regime 分类（CALM_BULL/ACCEL_DECLINE 等）天然对齐——regime 加权可直接用本项目的 regime 标签做相似性度量。

- **优势**：① **distribution-free**——不假设正态，有限样本覆盖保证，对齐 §3.19 远期演进方向中 Landolfi Non-Gaussian Drawdown Lookup Tables 的"非正态回撤"警示；② **regime-aware**——TWC + RWC 的 regime 加权与本项目 regime × drawdown 乘性叠加设计（§3.9）天然对齐；③ **model-agnostic**——wrap 任意 quantile 预测器，不绑定特定模型；④ **CRSP 实证**——在美股组合验证有效，比 Conformal Kelly 的 S&P 500 单资产更接近组合场景

- **暂缓理由**：
  1. **依赖 conformal 预测层**：RWC 需要一个 base quantile 预测器 + calibration set，当前 [36_var_es_monitoring](36_var_es_monitoring.md) 用参数法（历史模拟/GARCH-EVT），无 conformal 预测基础设施
  2. **regime 特征工程**：RWC 的 regime 相似性权重需定义"regime 距离"——本项目 regime 是离散分类（CALM_BULL 等），需转换为连续相似性度量（如 regime embedding 或 one-hot + cosine）
  3. **与 Conformal Kelly 优先级**：Conformal Kelly（§6.21）已暂缓，Schmitt RWC 与之同类（conformal 风控），但 RWC 更直接作用于 VaR（C 层输入），优先级略高于 Conformal Kelly
  4. **样本需求**：conformal 校准需 calibration set（≥100 个历史预测误差），当前实盘样本 <6 个月不足

- **重评条件**：① [36_var_es_monitoring](36_var_es_monitoring.md) conformal 预测层（quantile forecaster + calibration pipeline）production；② [34_regime_meta_allocator](34_regime_meta_allocator.md) regime 特征工程稳定（regime embedding 或可用的相似性度量）；③ 实盘 ≥6 月 conformal calibration set 积累后，引入 RWC 作为 [36_var_es_monitoring](36_var_es_monitoring.md) §3.2 参数法 VaR 的 conformal 校准增强（§6.25，P2）。**最小集成路径**：先 TWC（time-weighted，无 regime 加权，简单），验证稳定后再加 RWC（regime-weighted）。

> **为何列入而非直接拒绝**：Schmitt 2026（Oxford）是 conformal risk control 在金融 VaR 场景的最新应用（2026-02），比 Conformal Kelly（§6.21，2026-08）更早且更直接作用于 VaR——Conformal Kelly 管 leverage（仓位层面），Schmitt RWC 管 VaR buffer（风险度量层面），两者正交互补。RWC 的 regime 加权与本项目 §3.9 regime × drawdown 乘性叠加设计天然对齐，是"conformal 风控 + regime 感知"的直接落地路径。作为远期增强登记，避免 [36_var_es_monitoring](36_var_es_monitoring.md) conformal 预测层就绪后重新调研。

### 4.18 Bayesian Online Changepoint Detection（BOCD）概率 Kill Switch —— 暂缓

- **算法**：[Adams & MacKay 2007（arXiv:0710.3742）](https://arxiv.org/abs/0710.3742) 提出 Bayesian Online Changepoint Detection（BOCD），维护 **run-length** `r_t`（自上次变点以来的时间长度）的后验概率分布 `P(r_t | x_{1:t})`，每步在线更新，输出 `P(changepoint at time t) = P(r_t = 0 | x_{1:t})` **连续概率**而非二元判断。[mathandmarkets 2026-02 "CUSUM, Bayes, and the Art of Knowing When to Quit"](https://mathandmarkets.com/p/detecting-decay-in-real-time-when) 将 BOCD 与 CUSUM/Page-Hinkley/Rolling Sharpe 对比，构建策略衰减检测完整框架；[quantbeckman 2025-11 "Switch-Off: Bayesian online changepoint detection"](https://www.quantbeckman.com/p/with-code-switch-off-bayesian-online) 提出 **probabilistic kill switch**——用 Normal-Inverse-Gamma（N-IG）共轭先验 + Student-t 似然（重尾适配）+ 双触发系统（P > threshold_high 硬停机 / P > threshold_low 持续 N 日减仓）。

  **核心递推**（Adams & MacKay 2007）：
  ```
  # growth probability（无变点，run-length 增长）
  P(r_t = r_{t-1} + 1 | x_{1:t}) ∝ P(x_t | r_{t-1}+1) · P(r_{t-1}) · (1 - H)
  # changepoint probability（有变点，run-length 重置为 0）
  P(r_t = 0 | x_{1:t}) ∝ P(x_t | r=0) · Σ_{r_{t-1}} P(r_{t-1}) · H
  其中 H = hazard function（通常常数 1/λ，λ 为期望 run-length）
  P(x_t | r) = predictive probability under r-step posterior
  ```
  输出 `P(changepoint) = P(r_t = 0 | x_{1:t})`，可设概率阈值触发（如 P > 0.5 减仓 / P > 0.8 硬停机）。

- **与 §4.8 CUSUM/Hawkes/Lee-Mykland 的关系**：
  | 维度 | CUSUM（§4.8）| BOCD（本节）|
  |---|---|---|
  | 检测目标 | 均值漂移（需指定 μ₀）| 任意参数变化（无需指定 μ₀）|
  | 输出形式 | 二元阈值告警（S⁺_t > h）| 连续概率 P(r_t=0) |
  | 参数依赖 | μ₀ + k（allowance）+ h（threshold）| H（hazard）+ 似然模型选择 |
  | 在线性 | 在线（O(1) 更新）| 在线（O(t) 更新，需 pruning）|
  | 先验融合 | 无 | 可整合金融经验参数（如期望 run-length）|
  - CUSUM 需指定 μ₀（"策略正常时的期望收益"）——若用全回测均值则包含待检测的衰减，若用短窗则敏感于窗口选择；BOCD **无需指定 μ₀**，通过 run-length 后验自适应估计
  - BOCD 的概率输出允许"分级响应"——P > 0.5 减仓 30% / P > 0.7 减仓 60% / P > 0.9 硬停机，比 CUSUM 的二元阈值更灵活
  - BOCD 是 §4.8 三检测器的"概率化演进"——CUSUM/Hawkes/Lee-Mykland 各检测单一模式（均值漂移/聚类/跳跃），BOCD 统一框架检测任意参数变化

- **quantbeckman 双触发系统**（工程化设计）：
  - **硬触发**：`P(changepoint) > 0.8` → 立即硬停机（对齐 §3.5 Kill Switch 不可覆盖通道）
  - **软触发**：`P(changepoint) > 0.5` 持续 **5 个交易日** → 减仓 50%（对齐 §3.4 recovery_factor 阶梯）
  - **N-IG 共轭先验 + Student-t 似然**：Normal-Inverse-Gamma 先验使后验解析可积，Student-t 似然（自由度 ν=3-7）适配 A 股收益重尾——比 Gaussian 似然更抗异常值
  - **log-space 数值稳定**：run-length 后验在 log-space 递推，避免长序列下数值下溢
  - **state-space pruning**：run-length > T_max 的状态剪枝（T_max 通常 100-200），控制计算复杂度

- **与 §4.7 TiD Kill Switch 的关系**：
  - TiD 是"纯时间"硬停机（连续水下时间 > T_kill）→ BOCD 是"概率变点"软/硬触发（P(changepoint) > threshold）
  - TiD 检测"长时间不恢复"→ BOCD 检测"参数已变化"——前者是后者的特例（参数变化导致长期水下）
  - 两者互补：TiD 兜底"BOCD 未检测到的缓慢衰减"，BOCD 前瞻"TiD 无法预警的突发结构断点"

- **优势**：① **概率输出**——P(changepoint) 连续概率，可分级响应，比 CUSUM 二元阈值更灵活；② **无需指定 μ₀**——通过 run-length 后验自适应估计，避免 CUSUM 的 μ₀ 选择困境；③ **先验融合**——hazard function 可整合金融经验（如策略期望生命周期 18 个月 → λ=252*1.5）；④ **在线流式**——无需存储完整历史，内存恒定（pruning 后）；⑤ **quantbeckman 双触发**——硬/软触发对齐本项目 §3.5 Kill Switch + §3.4 recovery_factor 两层机制

- **暂缓理由**：
  1. **计算复杂度**：BOCD 每步 O(t) 更新（需 pruning 到 O(T_max)），比 CUSUM 的 O(1) 重——当前日度决策下可接受，但需工程化 pruning 策略
  2. **个人系统样本短**：BOCD 的 run-length 后验需足够样本收敛，3-4 个月开发期不足；quantbeckman 实证需 ≥200 交易日样本
  3. **与 §4.8 同期暂缓**：BOCD 是 §4.8 CUSUM/Hawkes/Lee-Mykland 的概率化演进，§4.8 已暂缓（实盘 ≥1 年后重评），BOCD 随 §4.8 同步重评
  4. **似然模型选择**：Gaussian 似然不抗异常值，Student-t 需选自由度 ν，N-IG 共轭先验需选超参——似然模型选择本身是额外复杂度
  5. **与 §3.5 Kill Switch 的职责重叠**：当前 §3.5 固定阈值 Kill Switch 已 production，BOCD 是"概率化增强"非必需——MVP 先验证固定阈值法有效性，再考虑概率化演进

- **重评条件**：① 实盘 ≥1 年后，与 §4.8 CUSUM/Hawkes/Lee-Mykland 同步重评；② 若发现 §3.5 固定阈值 Kill Switch 误触发频繁（BOCD 概率输出可调阈值减少误触发）或漏检结构断点（BOCD 检测任意参数变化比 CUSUM 单一均值漂移更全面），引入 BOCD 作为 §6.10 统计检测的概率化升级；③ 似然模型用 Student-t（ν=5 起步，实盘校准），hazard 用常数 1/λ（λ=252，即期望 1 年变点一次）；④ 最小集成路径：先单策略试运行 BOCD（输出 P(changepoint) 仅供参考不触发），验证检测有效性后再接入双触发系统

- **Dm-BOCD 鲁棒性升级路径**（[arXiv:2302.04759](https://ar5iv.org/abs/2302.04759)，Altamirano, Briol & Knoblauch，"Robust and Scalable Bayesian Online Changepoint Detection"）：标准 Adams-MacKay BOCD 用 Gaussian 似然对离群点敏感——A股收益厚尾、有跳空，标准 BOCD 会把轻微异质性误判为变点（false positive）。**Dm-BOCD** 用 **diffusion score matching** 的广义贝叶斯推断替代精确似然，得到**封闭形式共轭后验**，比 β-BOCD 快 10 倍以上且对离群点鲁棒。**核心优势**：① 鲁棒性——diffusion score matching 不依赖精确似然指定，对模型误设定（如真实分布是 Student-t 但用 Gaussian 似然）稳健；② 速度——封闭形式共轭后验避免 MCMC，比 β-BOCD 快 10x+；③ 可扩展——适配高维流数据。**与本项目 §4.18 BOCD 的关系**：Dm-BOCD 是标准 BOCD 的**鲁棒性升级路径**——若实盘验证发现标准 BOCD（Student-t 似然）在 A 股跳空/涨跌停异常点下误报频繁，Dm-BOCD 的 diffusion score matching 提供不依赖精确似然指定的替代。**不单独登记**——作为 §4.18 BOCD 的鲁棒性升级子项，与 §6.27 BOCD 概率 Kill Switch 同步重评（重评条件②增补：若标准 BOCD 误报频繁，评估 Dm-BOCD 替代）。

> **为何列入而非直接拒绝**：BOCD 是 §4.8 CUSUM/Hawkes/Lee-Mykland 三检测器的"概率化统一演进"——CUSUM 需指定 μ₀（选择困境）+ 二元阈值（不够灵活），BOCD 通过 run-length 后验自适应估计 + 概率输出解决两大痛点。mathandmarkets 2026-02 + quantbeckman 2025-11 提供完整工程化方案（N-IG 共轭先验 + Student-t 似然 + 双触发 + log-space 稳定 + pruning），与本项目 §3.5 Kill Switch + §3.4 recovery_factor 两层机制天然对齐。Dm-BOCD（arXiv:2302.04759）提供鲁棒性升级路径，应对 A 股厚尾/跳空场景。作为 §4.8 的概率化演进登记，避免实盘 ≥1 年后重新调研。

### 4.19 Signature-based Path Portfolio（路径签名组合优化）—— 暂缓（P5+，理论远期）

- **算法**：[Noguer i Alonso 2026-08-03（arXiv:2608.02355）](https://arxiv.org/abs/2608.02355) Path Portfolio Optimization——把组合理论建立在 **path-first 框架**上，以价格路径的 **signature（签名）**作为通用坐标。组合是 signature 的线性泛函，控制变量生活在截断张量代数中，signature 坐标的协方差是 expected signature 的 non-group-like 部分（defect form），整个 mean-variance 问题变成**一个张量上的线性系统**。两个结构结论：① lift（执行约定）的 Marcus vs forward 差异恰好等于 Fernholz excess growth rate（几何性缺陷）；② level-2 反对称块是 lift-invariant 的（方向信号与约定无关，方差/ruin 信号与约定有关）。

  **实证发现（dimensional trade-off）**：① 已知 expected signature 时，二次路径泛函使 certainty equivalent 提升 **11 倍**（2 资产）/ **60 倍**（20 资产截面）；② estimated signature 时，未正则化策略严重为负，直到样本超过约 **6 observations per parameter** 才可用，shrinkage 从 pair 的有害变为 cross-section 的不可或缺；③ 全部增益集中在 **symmetric block**（terminal increment 的凸性），path-dependent antisymmetric block 在 driver 无 expected area 时收益为零；④ sample-size floor 属于 unstructured estimation 而非 path complexity——只拟合 driver generator 并重建 expected signature 的估计器，在 barely 1 observation per parameter 下恢复几乎所有 attainable value。

  **Lemahieu & Boudt（Ghent University）drawdown optimization with generative ML**：用 signature transform 的 **kernel trick**（基于 path 的 non-parametric embedding 的 universality）线性近似 expected drawdowns，结合 **VAE（Variational Autoencoder）**生成路径集成均值（ensemble mean of noisy paths），实现 minimum drawdown portfolio 优化。多资产回测（US Bonds/Equity/NAREITs/GSCI）显示 superior risk-adjusted returns。

- **与 §4.14 CDaR / §4.16 CED 的关系**（path-dependent 风险度量的三层递进）：
  | 层级 | 方法 | 数学基础 | 路径依赖捕获 | 优化 | 当前状态 |
  |---|---|---|---|---|---|
  | **具体度量** | CDaR（§4.14）/ CED（§4.16）| drawdown 序列的 CVaR / MDD 分布尾部均值 | 显式（DD_t 序列）| LP 可解 | 暂缓（P2/P3）|
  | **签名近似** | Lemahieu & Boudt | signature transform kernel trick 线性近似 expected drawdown | 隐式（signature 编码路径）| 核方法 | 暂缓（P5+）|
  | **统一框架** | Noguer i Alonso Path Portfolio | signature 作通用坐标，mean-variance = 张量线性系统 | 完全（signature 是路径的 universal coordinate）| 张量线性系统 | 暂缓（P5+）|

  - **关键洞察**：CDaR/CED 是 path-dependent 风险的**具体度量**（定义 drawdown 函数后取尾部均值），signature 是 path-dependent 风险的**数学基础**（signature 是路径的 universal coordinate，任何 path functional 都可表示为 signature 的函数）。CDaR 是 signature 框架的一个特例——从 signature 视角看，CDaR 是对 signature 的特定投影。
  - **Noguer i Alonso 的实证警示**："sample-size floor 属于 unstructured estimation"——直接估计 expected signature 需 6 obs/param，但只拟合 driver generator 重建可降至 1 obs/param。这对本项目（3-4 个月开发期、小资金）是关键约束：signature 方法需配对 driver generator 估计才可行，直接估计不可行。

- **优势**：① **universal coordinate**——signature 是路径的通用坐标，任何 path-dependent 度量（CDaR/CED/UI/PI）都是其泛函，提供统一数学框架；② **linear approximation**——Lemahieu & Boudt 的 kernel trick 使 expected drawdown 可线性近似，绕过 CDaR 的 LP 求解；③ **path-first**——直接在路径空间优化，不依赖协方差矩阵（mean-variance 的 covariance 在重尾/非平稳下不可靠）；④ **generative augmentation**——VAE 生成路径集成可补充历史样本不足（本项目 3-4 个月开发期样本短的痛点）

- **暂缓理由（P5+ 远期，非近期候选）**：
  1. **理论深度远超 MVP 需求**：signature/rough paths 理论是纯数学领域（Lyons 1998+），实现需 sigkit/esig 等专门库，学习曲线陡峭。当前 §3.8 drawdown_pct + §4.14 CDaR（暂缓）已覆盖 path-dependent 风险的核心需求
  2. **样本约束**：Noguer i Alonso 实证需 6 obs/param（直接估计）或 1 obs/param（driver generator 重建）。本项目 3-5 策略、日频数据、3-4 个月开发期，样本量不足以支撑 signature 估计——即使 driver generator 重建也需 ≥1 年实盘数据
  3. **VAE 生成路径的合规边界**：Lemahieu & Boudt 的 VAE 路径生成与本项目"RL 驱动策略永久不采纳"裁定不冲突（VAE 是生成模型非 RL），但生成路径用于优化目标引入 model risk（生成路径分布偏离真实分布→优化过拟合生成路径而非真实路径）
  4. **与 CDaR/CED 优先级**：signature 是 CDaR/CED 的数学基础，但 CDaR/CED 已暂缓（P2/P3），signature 作为更底层的方法优先级更低——先验证 CDaR/CED 的实盘价值，再考虑是否需要 signature 统一框架
  5. **过度工程红线**：signature + VAE + driver generator 是三层理论叠加，个人项目不需要 universal coordinate 框架——具体度量（drawdown_pct → CDaR → CED）的递进已足够

- **重评条件**：① 实盘 ≥2 年后样本充足，且 CDaR（§4.14）/ CED（§4.16）已验证实盘价值后，评估 signature 是否提供 CDaR/CED 之外的增量；② 策略数扩展到 ≥10 个、path-dependent 风险度量需统一框架时；③ sigkit/esig 等 Python signature 库成熟且 A 股适配验证后。**不设近期施工计划**，仅作理论远期登记

> **为何列入而非直接拒绝**：Noguer i Alonso 2026-08-03 是 path-dependent portfolio optimization 的前沿理论工作，signature 是 CDaR/CED/UI/PI 等所有 path-dependent 风险度量的数学基础。登记此方向避免实盘 ≥2 年后重新调研 signature 理论。与 §4.14 CDaR（具体度量）+ §4.16 CED（归因度量）形成"path-dependent 风险三层递进"：具体度量 → 签名近似 → 统一框架。Lemahieu & Boudt 的 generative ML 路径生成思路与 [91_density_prediction](91_density_prediction.md) 的密度预测正交（前者生成路径，后者预测分布），可远期交叉。P5+ 定位确保不挤占近期施工带宽。

### 4.20 Continuous Cash-Overlay Filters（连续现金叠加回撤过滤器）—— 暂缓（P3，模块化回撤工具）

- **来源**：[Xiong arXiv:2606.09025](https://arxiv.org/abs/2606.09025) 2026-06-08 "Continuous Cash-Overlay Filters for Growth–Defensive Risk Sleeve"
- **算法**：在 growth–defensive risk sleeve（成长-防御风险袖套）上叠加**两类连续过滤器**的组合：
  1. **slow-tail compensation filter**（慢尾补偿过滤器）：针对 **2022 式持续补偿恶化**——防御资产在长周期内持续跑输成长资产（"补偿恶化"），过滤器动态调整成长/防御配比，避免防御资产拖累持续过久
  2. **V-shape crash-brake filter**（V 型急刹过滤器）：针对**快速回撤**——市场 V 型下跌时立即提升现金比例（急刹），V 型反弹时快速恢复（避免踏空）
  3. **max-cash 规则组合**：两个过滤器输出取 max-cash（更保守者获胜），确保任一过滤器触发时都执行更防御的配置

- **实证**（2017–2026 窗口，严格 walk-forward 验证）：
  | 指标 | 100% R（无过滤器） | + Cash-Overlay | 改善 |
  |---|---|---|---|
  | CAGR | 16.62% | **20.45%** | +3.83% |
  | 最大回撤 | -33.59% | **-16.77%** | 改善 16.82% |
  
  即**同时提升收益和降低回撤**（非单纯风险换收益），walk-forward 验证确认非过拟合

- **与本项目 §3 三层分离 + Kill Switch 的关系**：
  - **范式差异**：本项目回撤 Protocol 是**离散分档触发**（5/10/15% → Soft/Hard/Kill 四级响应），Xiong 现金叠加是**连续比例调整**（过滤器输出连续现金比例）。两者非互斥——本项目 regime Shrinkage（34 号）已是"连续-ish"的仓位节流，Xiong 过滤器可视为"回撤维度的连续节流"
  - **与 BlackRock 比例控制 vol-targeting（31 号 §2.4.3 v1.20.0）的同构性**：BlackRock 用跟踪误差反馈连续调整杠杆，Xiong 用 cash-overlay 连续调整现金比例——都是"连续闭环反馈"替代"离散分档"的范式。本项目 35 号回撤 Protocol 的离散分档 + 34 号 regime Shrinkage 的离散节流，与 BlackRock/Xiong 的连续控制是同一频谱的两端
  - **slow-tail compensation 与 §3.9 regime Shrinkage 协同**的协同维度：slow-tail 补偿恶化的场景正是 regime 检测器应识别的"防御资产持续跑输"状态，Xiong 过滤器提供了 regime 识别后的连续配比调整工具
  - **V-shape crash-brake 与 §3.5 Kill Switch 的区别**：Kill Switch 是**极端回撤的硬着陆**（≥15% 全停），V-shape crash-brake 是**中速回撤的软着陆**（V 型下跌时提现金但不停交易）——两者互补，Kill Switch 是 crash-brake 无法止住回撤时的最终兜底

- **暂缓理由（P3 远期，非近期候选）**：
  1. **本项目无"成长-防御 sleeve"架构**：Xiong 假设组合有明确的 growth sleeve + defensive sleeve（如股票+债券），本项目是 5 策略独立 sleeve 架构（打板/多因子/事件驱动等），无天然的"成长-防御"二分。移植需重新定义"哪些策略属成长/哪些属防御"，或改为"风险 sleeve vs 现金 sleeve"的映射——非直接适用
  2. **A 股 T+1 约束限制连续调整**：Xiong 的连续现金比例调整假设可实时调仓，A 股 T+1 下日内无法卖出已买入股票，连续调整的响应延迟降低 V-shape crash-brake 的急刹效果
  3. **与现有回撤 Protocol 的冗余**：§3 三层分离（tracker → curve_manager → controller）+ Kill Switch 已覆盖回撤控制的核心需求。Xiong 的增量价值在于"连续 vs 离散"的平滑性——但本项目 34 号 regime Shrinkage 已是 9+3 态的细粒度节流，离散跳变问题部分缓解
  4. **max-cash 规则的保守性偏置**：两个过滤器取 max-cash 意味着任一触发都执行更防御配置，长期可能过度保守（CAGR 20.45% vs 无过滤器 16.62% 的提升依赖 walk-forward 窗口包含 2022 熊市——若窗口以牛市为主可能反向拖累）

- **重评条件**：① 实盘 ≥1 年后，若 35 号离散分档的"阶梯跳变"问题显著（regime 切换时仓位跳变过大），评估引入 cash-overlay 连续平滑项（在分档基础上叠加连续微调，非完全替代）；② 策略 sleeve 扩展到含明确的"防御型策略"（如债券/黄金套利）时，growth-defensive 映射自然成立；③ 34 号 regime Shrinkage 证明不足以捕捉"防御资产持续跑输"场景时。**不设近期施工计划**

> **为何列入而非直接拒绝**：Xiong 2026-06-08 是回撤控制的模块化连续过滤器方法，与 §4.12 MPC 连续风险厌恶调整（P4 远期）+ 31 号 §2.4.3 BlackRock 比例控制 vol-targeting（远期候选）共同构成"离散分档 → 连续控制"的演进方向。实证数据（CAGR +3.83% / MaxDD 改善 16.82%）显著且 walk-forward 验证。登记此方向避免实盘后发现离散分档阶梯跳变问题时重新调研连续回撤控制方法。与 §4.19 Signature-based Path Portfolio（P5+）的区别：signature 是路径依赖的统一数学框架，cash-overlay 是回撤控制的工程化连续过滤器——前者是理论远期，后者是工程远期，优先级更高（P3 vs P5+）

### 4.21 Transfer-Entropy + Hawkes + Von Neumann 图熵网络级系统性风险预警—— 暂缓（P4，网络级远期）

- **来源**：[An & Dai, MDPI Entropy 28(8), 887, 2026-08-06](https://www.mdpi.com/1099-4300/28/8/887) "Transfer-Entropy- and Hawkes-Process-Driven Dynamic Measurement of Cross-Border Financial Risk Contagion in Directed, Weighted Networks"（南京审计大学 + 南开大学）
- **算法**：双层框架 + 网络级脆弱性度量：
  1. **第一层（转移熵）**：偏差校正 k-NN 估计器估计资产间一对一转移熵，检测**非线性和方向性**信息传递（超越线性相关）
  2. **第二层（多元 Hawkes）**：自激励点过程建模极端损失事件的到达和互激，给出激励强度矩阵
  3. **复合有向加权邻接矩阵**：转移熵层 + Hawkes 层合并为网络级传染强度指数，图拉普拉斯谱分解为直接/间接/反馈项
  4. **Von Neumann 图熵 + 谱间隙比**：作为网络复杂性和脆弱性度量
  5. **关键发现**：Von Neumann 图熵在主权债券指数**峰值回撤前 7-12 个交易日**达到历史极端值——提供 kill switch 的**预触发信号**

- **与本项目 §4.18 BOCD / §4.8 CUSUM+Hawkes+Lee-Mykland 的关系**：
  - **维度差异**：§4.8 三检测器是**单资产/单事件级**异常检测（CUSUM 检均值漂移、Hawkes 检事件聚类、Lee-Mykland 检跳跃），本文是**网络级系统性视角**（资产间信息流 + 互激 + 网络拓扑脆弱性）
  - **与 §4.18 BOCD 的互补**：BOCD 检测单序列变点，本文检测多资产网络的拓扑变化——当图熵超过历史极端值时，是"网络结构正在恶化"的信号，比单资产变点更早
  - **7-12 天提前量的价值**：§3.5 Kill Switch 是事后触发（回撤已发生），§3.13 盘中循环是日内触发，本文的图熵预警可在**回撤形成前 7-12 天**提供预触发信号——为"减仓但不平仓"的黄色预警争取时间

- **A 股适配**：
  - 将框架从"主权 CDS 利差"迁移到"A 股行业指数"（如申万一级 28 个行业指数间的风险传染）
  - 转移熵层：估计行业指数间一对一信息流（如科技→消费的溢出效应）
  - Hawkes 层：建模行业级极端跌幅事件的自激励和互激
  - Von Neumann 图熵：监控 A 股行业网络的系统性脆弱性，历史极端值作为 kill switch 预触发阈值

- **暂缓理由（P4 远期，非近期候选）**：
  1. **网络级基础设施需求**：需构建行业指数级实时数据管道 + 转移熵估计 + Hawkes 多元拟合 + 图拉普拉斯谱分解，计算复杂度远超当前单资产检测器
  2. **个人系统单账户定位**：网络级系统性风险预警更适合多策略/多组合的机构系统，本项目当前 5 策略独立 sleeve 架构下，行业间传染信号到仓位调整的映射路径较长
  3. **7-12 天提前量的校准成本**：A 股市场结构与主权 CDS 市场差异大，图熵极端值阈值需 A 股历史数据校准（至少 3-5 年含牛熊周期）
  4. **与现有 §3.5 ⑦ ORCA 谱特征 herding 检测的功能重叠**：§3.5 ⑦ 已登记 ORCA（24 ETF + 127 谱特征 + RF walk-forward）作为 herding 的价格相关性层替代，本文的转移熵+图熵是网络拓扑层——两者在"系统性风险检测"维度有重叠，但 ORCA 更轻量且已有 A 股实证

- **重评条件**：① 策略数扩展到 ≥8 个后，行业间传染信号对仓位调整的映射路径缩短；② 实盘 ≥1 年后发现 §3.5 Kill Switch 事后触发滞后（回撤已深才触发），需 7-12 天提前预警；③ A 股行业指数实时数据管道（申万一级 28 行业）建设完成。**不设近期施工计划**

> **为何列入而非直接拒绝**：本文是现有 Hawkes（§4.8）的**网络级扩展**——从单资产事件聚类到多资产互激+网络拓扑脆弱性，7-12 天提前量是 kill switch 从"事后触发"到"预触发"的质变。登记此方向避免实盘后发现 kill switch 滞后问题时重新调研网络级系统性风险预警方法。与 §4.18 BOCD 概率 Kill Switch 的区别：BOCD 是单序列概率化变点检测（概率输出替代二元阈值），本文是网络拓扑级脆弱性度量（图熵替代单序列统计量）——两者从不同维度增强 kill switch 的预警能力。与 §3.5 ⑦ ORCA 的区别：ORCA 是价格相关性层面（谱特征），本文是信息流+事件互激+网络拓扑层面——ORCA 更轻量先施工，本文作为网络级远期候选。

### 4.22 Xiao Jian et al. 2026-02 A 股 HFT 多层复杂网络 herding 渗流相变检测 —— 暂缓（P4，A 股网络级远期）

- **算法**：[Front. Phys. 2026-02-05](https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2025.1733200/full) Xiao Jian/Zhilin Yin/Hao Li（中南财经政法大学）构建多层复杂网络 ABM（regulatory/core institutional/market-maker/retail investor 四层），模拟 A 股 HFT 风险传导与监管策略
- **核心发现**：① 策略同质化系数 ρ > 0.65 时市场发生**渗流相变**（percolation phase transition），系统性风险概率从 0.2 跳到 0.7+；② 通信延迟差 > 50ms 时散户订单截获率非线性升至 82%；③ 传统监管平均响应延迟 2.1 小时，无法应对 HFT 实时性
- **A 股特殊性**：散户 80% 交易量 vs 外资 0.3% 机构控制 43.6% 订单流——"技术垄断"与"散户主导"并存的双重结构
- **与 §4.21 Transfer-Entropy + Hawkes 的关系**：§4.21 是信息流+事件互激+网络拓扑层（转移熵+Hawkes+图熵），本文是**策略同质化+渗流相变**层——两者从不同维度检测网络级系统性风险。本文的 ρ > 0.65 渗流阈值是 §4.21 图熵极端值阈值的补充
- **与 §3.5 ⑦ ORCA 的关系**：ORCA 是价格相关性层面（谱特征），本文是策略同质化层面（ABM 模拟）——ORCA 有 A 股实证先施工，本文作为 ABM 模拟远期候选
- **暂缓理由**：
  1. **ABM 模拟需求**：需构建 A 股多层网络 ABM（regulatory/institutional/market-maker/retail 四层 agent），计算复杂度远超当前单资产检测器
  2. **策略同质化系数 ρ 估计**：需实时监控全市场策略同质化程度，当前项目 5 策略独立 sleeve 架构下 ρ 估计样本不足
  3. **个人系统定位**：网络级 HFT 风险传导更适合交易所/监管层，个人系统是价格接受者非价格制定者
- **重评条件**：① 策略数扩展到 ≥8 个后，策略同质化 ρ 估计有意义；② A 股全市场实时数据管道建设完成；③ 实盘后发现 kill switch 事后触发滞后，需渗流相变提前预警

### 4.23 Chen 2026-04 A 股 GWII 板块 herding CSAD/CSSD 实证 —— 暂缓（P3，A 股 herding 轻量检测）

- **算法**：[ICFIED 2026](https://docker.atlantis-press.com/proceedings/icfied-26/126023570) Chen 2026-04-29（University of Calgary）用 CSAD（Cross-Sectional Absolute Deviation）+ CSSD（Cross-Sectional Standard Deviation）模型检测 A 股 Ground Weaponry II 板块 herding 行为
- **实证案例**：2025 年 6 月 GWII 板块股价从 2951.33 元（6/3）涨至 5735.31 元（8/13），CSAD/CSSD 检出显著 herding——政府主导军工企业重组 → 散户过度解读政策 → 模仿驱动投资
- **CSAD 模型**：`CSAD_t = (1/N) Σ |R_i,t − R_m,t|`，herding 时个股收益趋同 → CSAD 下降；非线性回归 `CSAD_t = α + β·|R_m,t| + γ·R_m,t²`，γ < 0 表示 herding
- **CSSD 模型**：`CSSD_t = sqrt((1/(N−1)) Σ (R_i,t − R_m,t)²)`，同理 herding 时下降
- **与 §3.5 ⑦ ORCA 的关系**：ORCA 是 24 ETF + 127 谱特征 + RF walk-forward（重模型），CSAD/CSSD 是**截面离散度**（轻量统计量）——两者从不同复杂度检测 herding。CSAD/CSSD 更轻量，适合个人系统 MVP
- **与 §4.22 Xiao Jian 的关系**：Xiao Jian 是 ABM 模拟（理论），Chen 是 CSAD/CSSD 实证（数据驱动）——Chen 的实证案例验证了 A 股 herding 的存在性 + CSAD/CSSD 的可检测性
- **暂缓理由**：
  1. **CSAD/CSSD 需截面数据**：需实时计算全市场或板块个股收益离散度，当前项目 5 策略独立 sleeve 架构下无截面数据管道
  2. **板块级 herding 到仓位调整的映射**：CSAD/CSSD 检出 herding 后如何映射到 drawdown_controller 的仓位调整，需 A 股历史数据校准
  3. **与现有 §3.5 Kill Switch 的功能关系**：herding 检测是"前馈预警"（herding 发生 → 减仓），Kill Switch 是"反馈触发"（回撤发生 → 减仓）——两者正交互补，但 herding 检测的施工优先级低于 Kill Switch（风险优先原则）
- **重评条件**：① A 股板块级实时数据管道（申万一级 28 行业）建设完成；② 实盘 ≥1 年后发现 Kill Switch 事后触发滞后，需 herding 前馈预警；③ §3.5 ⑦ ORCA 评估为过重时，CSAD/CSSD 作为轻量替代

### 4.24 Lévy-stable Drawdown Scaling——封闭形式非高斯回撤传播（远期，2026-08-10 新增）

- **算法**：[arXiv:2511.07834](https://arxiv.org/abs/2511.07834) Vlasiuk 2025-11 "Lévy-stable scaling of risk and performance functionals"（Columbia University）。在数据驱动的 Lévy 窗口 `[τ_UV, τ_IR]` 内，收益服从 α-稳定分布（α ∈ (1,2)），尺度 τ^{1/α}；窗口外聚合为有限方差 √τ 体制。以锚定 horizon τ₀ 为基准，**drawdown 功能的 Lévy 传播与高斯传播的差异为显式偏差项** `(τ/τ₀)^{1/α} - (τ/τ₀)^{1/2}`——高斯假设的 drawdown 低估可量化。drawdown 功能定义 `DD_{τ,p} := (E(D_τ)^p)^{1/p}`（p 阶 drawdown 期望），Lévy 传播在窗口内跨 horizon 产生一致的 drawdown 估计
- **与 §4.21 Non-Gaussian Drawdown Lookup Tables 的关系**：
  | 维度 | §4.21 Landolfi 2026-07 | §4.24 Vlasiuk 2025-11 |
  |---|---|---|
  | 方法 | 模拟仿真查表（lookup tables） | 封闭形式解析公式 |
  | 分布假设 | 任意非高斯分布（Monte Carlo 仿真） | α-稳定分布（Lévy 窗口内） |
  | 输出 | 给定分布 → drawdown 分布表 | 给定 α → drawdown 偏差项 |
  | 优势 | 分布无关（任意分布可仿真） | 解析公式（无需仿真，计算 O(1)） |
  | 劣势 | 仿真成本高（Monte Carlo 迭代） | 需 α-稳定假设（Lévy 窗口外失效） |
  - 两者**互补**：§4.21 适用于任意分布但需仿真；§4.24 适用于 α-稳定窗口内但解析。Phase 2+ 可先用 §4.24 解析公式做快速估计，§4.21 仿真做精确验证
- **与当前 §3.8 回撤基准净值口径的关系**：§3.8 使用 close-to-close NAV 计算回撤（峰值到谷值百分比）。Vlasiuk 的 drawdown 公式基于 log-price 过程的 supremum，理论上是连续监测；本项目日度监测（discrete monitoring）是 Poisson 观测的特例。[Li/Li/Yan 2026-02](https://doi.org/10.1017/apr.2026.10053)（Advances in Applied Probability）推导了 Poisson 观测时间下的 drawdown 退出恒等式（exit identities），为日度监测的回撤阈值设置提供 Lévy 过程理论支撑
- **优势**：① **封闭形式**——无需 Monte Carlo 仿真，O(1) 计算；② **偏差可量化**——高斯假设低估 drawdown 的程度 = `(τ/τ₀)^{1/α} - (τ/τ₀)^{1/2}`，α 越小（厚尾越重）偏差越大；③ **horizon 一致性**——Lévy 传播在窗口内跨 horizon 产生一致估计，避免高斯 √T 传播在不同持有期下的不一致
- **暂缓理由**：
  1. **α 估计需长样本**：α 从 log-log 斜率识别需足够数据点覆盖多个 horizon，A 股短样本下 α 估计不稳定
  2. **Lévy 窗口识别复杂**：需两段拟合 + 超越/红外截止点定位，工程化成本高
  3. **当前回撤阈值是经验值**：§3.2 的 8/15/20/25% 四级阈值基于 A 股实证+风险偏好，非理论推导。Vlasiuk 的 drawdown 公式可提供理论校验但非必要——当前阈值已在 §3.21 行业实证背书中验证
  4. **与 §4.21 同期暂缓**：§4.21 Non-Gaussian Drawdown Lookup Tables 已暂缓，§4.24 作为其解析互补品同步暂缓
- **重评条件**：① 实盘 ≥2 年稳定样本，α 估计稳定（Lévy 窗口可识别）；② §4.21 仿真查表落地后需解析公式做快速估计时；③ 当前 8/15/20/25% 阈值需理论校验时（Vlasiuk 公式可计算"高斯假设低估了多少 drawdown 风险"）
- **跨文档**：36号 §4.24 登记 Vlasiuk 论文的 VaR/ES horizon 修正公式（同一论文），本节登记 drawdown 公式，两者同源。González Cázares & Mijatović 2022（Finance and Stochastics 26(4)）提供 Lévy 过程 drawdown/duration 的 MLMC 仿真算法（stick-breaking Gaussian approximation），可作为 §4.21 仿真查表的算法基础

### 4.25 MFCCA 符号保留多重分形交叉相关组合分配——直接降低 drawdown 的组合配置层远期候选（2026-08-10 新增）

- **算法**：[arXiv:2608.04987](https://arxiv.org/abs/2608.04987) Kakinaka & Umeno 2026-08-05 "Portfolio Allocation under Heterogeneous Scales and Multifractality"。核心创新：**风险泛函 = 带符号的多重分形交叉相关分析（MFCCA）波动函数**，以尺度 s 和波动阶 q 为索引。与 MFDCCA 型准则（聚合前修正局部去趋势协方差符号）根本不同——**MFCCA 保留局部去趋势协方差的符号**，使同向运动（co-moving）与反向运动（counter-moving）分量以**相反符号**贡献风险。q=2 时二次型退化为组合序列本身的去趋势波动函数，**均值-方差准则成为其尺度依赖极限**。
- **实证结论**：应用于金融多资产，该准则在**每个要求收益水平上**（in-sample + out-of-sample）降低 drawdown、VaR、ES，且**不损失实现组合收益**——"无代价降回撤"的理论上限候选。符号保留比跨波动阶聚合对尾部风险缩减贡献更大。
- **与当前 35 号回撤 Protocol 的关系**：
  | 维度 | 35 号回撤 Protocol（当前） | MFCCA（本节） |
  |---|---|---|
  | 层级 | sleeve 级 + firm 级风险节流 | 组合配置层（portfolio allocation） |
  | 机制 | 反馈式（回撤已发生→减仓） | 前馈式（分配时即最小化带符号交叉相关风险） |
  | 度量 | drawdown_pct 单点 + VaR 5 级 | 多尺度带符号波动函数 F(s,q) |
  | 协方差 | [30号 §3.1](30_multi_strategy_concurrency.md) 明确拒绝 MVO + 协方差估计 | 需多尺度交叉相关估计（比 MVO 更重） |
  | 正交性 | ✅ 正交互补——Protocol 管"回撤后怎么减"，MFCCA 管"分配时怎么避免" |
- **与 30 号 §3.1 拒绝 MVO 的诚实账本**：
  - 30 号 §3.1 拒绝理由："不做 MVO，不做协方差估计"——针对的是 **mean-variance optimization 的权重对协方差矩阵极端敏感**（Michaux 1989 微小输入变化→权重剧烈跳变→换手成本侵蚀）+ **个人项目 5 策略 sleeve 架构下协方差估计样本不足**
  - MFCCA 与 MVO 的**根本区别**：① **符号保留**——MVO 的方差 `wᵀΣw` 对正负协差不区分（同向和反向都被惩罚），MFCCA 保留符号使反向运动**降低**风险（对冲效果被正确计入）；② **多尺度**——MVO 用单一协方差矩阵，MFCCA 跨尺度 s 分析（短尺度和长尺度交互结构不同）；③ **q 阶泛化**——q>2 强调大波动（尾部），q<2 强调小波动，q=2 退化为 MVO
  - **但 MFCCA 仍需估计多尺度交叉相关函数**——计算复杂度高于 O(N)，与 30 号"O(N) 复杂度保证"约束冲突。且 5 策略 sleeve 架构下多尺度交叉相关估计的样本不足问题比 MVO 更严重（需多 horizon × 多策略交叉相关矩阵）
- **与 §6.30 CPPI+风险预算 / §6.32 Put-Option Sleeve 的关系**：三者同属**组合配置层远期候选**（P4-P5），均需项目演进到"组合配置层"独立模块时重新评估。MFCCA 的独特价值是**符号保留**——其他组合配置方法（CPPI/RB/HRP）均不区分同向反向协差，MFCCA 是唯一将对冲效果正确计入风险泛函的方法
- **与 [54号 §3.14 MCR/CCR 风险分解](54_reconciliation_attribution.md) 的关系**：MCR/CCR 是风险**归因**（分解已有组合的风险贡献），MFCCA 是风险**优化**（分配时最小化风险泛函）。两者正交：MFCCA 优化分配 → MCR/CCR 归因验证分配效果
- **与 90 号 risk parity 五级递进的关系**：MFCCA 已由 [90号](90_methodology_open_questions.md) v1.3.0 纳入 risk parity 五级递进第五级（多尺度带符号），本节补 35 号 drawdown 维度的交叉引用 + 诚实账本评估
- **优势**：① **直接降低 drawdown**——论文实证"每个收益水平降 drawdown/VaR/ES 无损收益"；② **符号保留创新**——对冲效果正确计入（反向运动降风险）；③ **多尺度结构**——短/长尺度交互差异被捕捉；④ **理论优雅**——q=2 退化为 MVO，是 MVO 的严格泛化
- **暂缓理由（P4 远期，同 §6.30/§6.32 组合配置层触发条件）**：
  1. **层级正交**：MFCCA 是组合配置层，本项目当前 sleeve 级 + firm 级两层架构不引入第三层（[30号 §2.2](30_multi_strategy_concurrency.md)），同 §6.30 CPPI 暂缓理由
  2. **计算复杂度**：多尺度交叉相关估计高于 O(N)，与 30 号 O(N) 保证冲突
  3. **样本约束**：5 策略 sleeve 架构下多 horizon × 多策略交叉相关矩阵估计样本不足（比 MVO 更严重）
  4. **30 号架构约束**：30 号 §3.1 拒绝协方差估计是架构裁决非技术限制，MFCCA 需架构演进到组合配置层才可重新评估
- **重评条件**：① 项目演进到"组合配置层"独立模块（同 §6.30/§6.32 触发条件）；② 策略数扩展到 ≥8 个后多尺度交叉相关估计有意义；③ 实盘 ≥2 年多尺度收益数据积累。**最小集成路径**：先用 2 策略 × 3 尺度（日/周/月）做 offline backtest 验证 A 股符号保留的增量价值（同向 vs 反向策略对的风险贡献差异），再决定是否接入组合配置层
- **跨文档**：90 号 v1.3.0 risk parity 五级递进第五级（多尺度带符号）+ 54 号 §3.14 MCR/CCR 风险归因（分配后验证）+ 本节 drawdown 维度交叉引用

### 4.26 Robust Risk Parity (RRP) —— A 股实证的组合配置层远期候选（2026-08-10 新增）

- **算法**：[Li & Ye 2026 "Research on asset allocation strategies based on robust risk parity model"](https://ideas.repec.org/a/eee/finlet/v92y2026ics1544612326001170.html)（Finance Research Letters vol.92(C), DOI:10.1016/j.frl.2026.109586）。在传统风险平价（TRP）框架内集成：① **自适应扰动机制**（动态调整扰动半径应对市场不确定性）；② **鲁棒协方差矩阵估计**（抗异常点）；③ **GARCH 波动率预测**；④ **市场状态识别**（regime identification）；⑤ **因子结构协方差估计**（factor-structured covariance）。**A 股实证**：2012-2024 中国市场数据，对比 TRP/EW/GMV/MaxRet/ERP 五种基线，RRP 在收益、Sharpe、Calmar 上均优于全部基线，波动率和最大回撤更低。
- **与 §4.25 MFCCA 的关系**：
  | 维度 | §4.25 MFCCA | §4.26 RRP |
  |---|---|---|
  | 方法 | 多尺度带符号交叉相关（理论前沿） | 鲁棒风险平价（工程化集成） |
  | A 股实证 | 论文用多资产（未明确 A 股） | **2012-2024 中国市场全样本实证** |
  | 创新点 | 符号保留 + 多尺度 | 自适应扰动 + GARCH + regime + 因子结构 |
  | 复杂度 | 高（多尺度交叉相关） | 中（标准 RP + 鲁棒增强） |
  | 与 regime 关系 | 无 regime 维度 | 内置市场状态识别（与 [10号 regime](10_regime_detector_spec.md) 天然对接） |
  - 两者**互补**：MFCCA 是理论前沿（符号保留创新），RRP 是工程化集成（A 股实证 + regime 对接）。RRP 的 regime 识别维度与本项目 [34号 RegimeMetaAllocator](34_regime_meta_allocator.md) 天然契合
- **与当前架构的关系**：同 §4.25 MFCCA，RRP 是组合配置层方法，与 30 号 sleeve 级 + firm 级两层架构正交。但 RRP 的 **regime 识别 + GARCH 波动率预测**两个组件可独立提取，作为 [34号 RegimeMetaAllocator](34_regime_meta_allocator.md) 的增强候选（不引入完整 RRP 组合配置层）
- **暂缓理由（P3 远期）**：① 同 §4.25 层级正交理由；② RRP 完整框架需协方差估计（30 号约束）；③ 但 RRP 的 regime + GARCH 组件可独立评估接入 34 号
- **重评条件**：① 34号 RegimeMetaAllocator regime 特征工程稳定后，评估 GARCH 波动率预测作为 regime 输入增强；② 项目演进到组合配置层时评估完整 RRP 框架；③ **A 股实证优势**——RRP 是少有的有 A 股全样本实证的组合配置方法（2012-2024 含牛熊周期），优先级高于无 A 股实证的 MFCCA

### 4.27 Drawdown Beyond Brownian Motion——回撤阈值非高斯校准与 keep-or-kill 决策表（2026-08-10 新增）

- **算法**：[arXiv:2608.00127](https://arxiv.org/abs/2608.00127) Landolfi 2026-07-31 "Drawdown Risk Beyond Brownian Motion: A Monte-Carlo Framework, Non-Gaussian Extensions, and Long Memory"（Epiphany, Imperia, Italy）。在 Rej-Seager-Bouchaud (RSB) drifted Brownian motion drawdown 闭式框架基础上，建立透明 Monte-Carlo 实验验证 RSB 解析基准，并扩展 drawdown 到 **4 个决策相关测度**——决策时直接查表：
  1. **MaxDD**（最大回撤深度）——回撤序列的峰值到谷值最大百分比
  2. **MaxLoss**（最大单期损失）——单期（日/周）最大负收益
  3. **FinalNegTime**（最终处于水下时间占比）——回测窗口内 NAV 低于高水位的交易日比例
  4. **LongestRecovery**（最长恢复时间）——从回撤谷值回到前高的最长连续交易日数

- **核心贡献**：① 在保持真实 Sharpe 和波动率不变前提下，变化偏度/厚尾/波动率聚集/Sharpe 估计不确定性，证明 **4 个测度并不同步移动** → 单一高斯表系统性误警（Gaussian 表在非正态下对某些测度过松、对某些过紧）；② **分数布朗运动 (fBm) 长记忆**：持续性下回撤风险表观放大，对最大回撤深度而言**几乎完全是自相似色散标度效应 `T^{H-1/2}`**（H 为 Hurst 指数，H>1/2 持续性），而非路径几何深化 → 是 √-time 校准失效，不是内在危险；③ 提供可复现的查找表 + 实用校准配方（Section 7）。

- **与 RSB 闭式框架的关系**：RSB（Rej-Seager-Bouchaud）在 drifted Brownian motion 假设下给出 drawdown 的闭式解析解（给定 Sharpe + horizon → 期望 MaxDD）。本节是 RSB 的**非高斯扩展**——保留 RSB 的 Sharpe 驱动框架，但放松高斯假设，用 Monte-Carlo 仿真在任意收益分布下生成 4 测度查表。RSB 是本节 H=1/2（无长记忆）+ Gaussian 分布的特例。

- **关键洞见**：
  1. **单一高斯表系统性误警**：偏度（左偏→MaxDD/MaxLoss 更深）、厚尾（峰度→MaxLoss 尾部更重）、波动率聚集（GARCH 效应→LongestRecovery 更长）使 4 测度相对 Gaussian 基准的偏离方向不同——用单一 Gaussian 表同时校准 4 测度会导致某些测度阈值过松（漏警）+ 某些过紧（误警）
  2. **fBm 持续性放大是 √-time 校准失效而非真实风险**：H>1/2 时回撤"放大"的表观主要来自 `T^{H-1/2}` 自相似色散标度——高斯 √T 时间缩放在持续性下失效，需用 `T^H` 缩放校正；校正后表观放大大部分消失，说明这不是路径几何本征深化而是时间标度校准错误。警示 [36_var_es_monitoring](36_var_es_monitoring.md) §3.2 参数法 VaR 的 √T 缩放在持续性下同样失效

- **与 35 号 Protocol 的关系表**（参考 §4.25 MFCCA / §4.26 RRP 格式）：

  | 维度 | 35 号回撤 Protocol（§3.x sleeve/firm 层） | §4.27 Drawdown Beyond Brownian Motion（本节） |
  |---|---|---|
  | 层级 | sleeve 级 + firm 级回撤判定与响应 | 回撤阈值校准层（threshold calibration） |
  | 职责 | "触发后怎么做"——5/10/15% 阈值触发后的减仓/恢复/Kill 响应 | "阈值怎么定"——给定 Sharpe + 收益分布结构，4 测度的统计期望分位 |
  | 输入 | 实时 drawdown_pct / VaR / 策略 PnL | 历史 Sharpe + skew/峰度/波动率聚集参数 + Hurst 指数 |
  | 输出 | position_cap / recovery_factor / Kill 触发 | MaxDD/MaxLoss/FinalNegTime/LongestRecovery 4 测度阈值查表 |
  | 正交性 | ✅ 正交互补——本节管"阈值怎么定"（校准层），§3.x 管"触发后怎么做"（执行层），§6.23 是本节的早期待裁定登记（同一论文） |

- **实用校准配方**（strategy archetype 分类 → 参数 → 查表）：

  | strategy archetype | 偏度 | 厚尾（峰度） | 波动率聚集 | Hurst H | 查表侧重测度 |
  |---|---|---|---|---|---|
  | 趋势跟踪 | 左偏 | 中重尾 | 中 | >0.5（持续性） | MaxDD + LongestRecovery |
  | 均值回归 | 左偏 | 重尾 | 低 | <0.5（反持续性） | MaxLoss + FinalNegTime |
  | 套利 | 近对称 | 轻尾 | 低 | ≈0.5 | FinalNegTime（浅回撤长时间） |
  | 打板/T0 | 左偏 | 重尾 | 高 | ≈0.5 | MaxLoss（单日极端） |
  | 多因子 | 混合 | 中 | 中 | ≈0.5 | 4 测度均衡 |

  校准流程：① 估计策略历史 Sharpe + 4 矩参数（skew/kurt/波动率聚集系数/Hurst）；② strategy archetype 分类器匹配上表；③ 查 Landolfi 4 测度表得到各测度的 95%/99% 分位阈值；④ 与当前 §3.2 经验阈值（5/10/15%）对比——若经验阈值过松（查表 95% 分位 < 经验阈值）则收紧，过紧则放宽

- **Phase 定位**：Phase 3 校准阶段（与 §6.21 Conformal Kelly / §6.25 Schmitt RWC 同期）——Phase 1 施工 §3.x 三层回撤 Protocol + Kill Switch（当前），Phase 2 实盘积累 Sharpe/矩参数估计样本，Phase 3 用 4 测度查表校准经验阈值。MVP 不替换 §3.2 阈值，仅作校准参考

- **与现有 §4.x 各回撤算法的互补性**：
  - **§4.24 Lévy-stable Drawdown Scaling**（Vlasiuk）：解析公式（α-稳定窗口内 O(1) 计算），本节是仿真查表（任意分布）——§4.24 适用于 α-稳定窗口快速估计，§4.27 适用于任意分布精确查表，两者同属"厚尾传播族"
  - **§4.6 Ulcer Index / §4.9 Pain Index / §4.14 CDaR**（回撤度量族）：UI/PI/CDaR 是回撤的**事后度量**（描述已发生回撤），本节是**事前校准**（给定 Sharpe 预测回撤分位）——前者用于报告，后者用于阈值设定
  - **§3.2 三层映射表**（5/10/15%）：本节为 §3.2 经验阈值提供**统计校准依据**（"5% 是给定 Sharpe 的 MaxDD 多少分位？"），与 §6.28 vol-matched threshold（经验 vol-matching）正交互补可叠加
  - **§6.23 Non-Gaussian Lookup Tables**：§6.23 是本论文的**早期待裁定登记**（v1.8.0），本节是其**完整算法节**（从登记升级为可施工形态），§6.37 是对应的 keep-or-kill 待裁定

- **优势**：① **4 测度查表**——决策时直接查表不需在线仿真；② **分布无关**——Monte-Carlo 适用于任意收益分布（高斯/厚尾/偏态/聚集）；③ **揭示 √-time 失效**——fBm 持续性下高斯 √T 缩放失效的定量诊断；④ **可复现**——论文提供开源查找表 + 校准配方

- **暂缓理由（P2-P3 远期，Phase 3 校准阶段）**：
  1. **需实盘 Sharpe 稳定估计**：Rej-Bouchaud 框架需 SR 输入，A 股短样本下 SR 估计不稳定（需 ≥6 月实盘）
  2. **收益分布矩估计需样本积累**：skew/峰度/波动率聚集/Hurst 估计需 ≥1 年日频数据
  3. **当前阈值是经验值已在 §3.21 行业实证背书**：5/10/15% 阈值基于 A 股实证+风险偏好，非理论推导，4 测度查表提供校准但非必要
  4. **与 §6.23 同步**：§6.23 已登记本论文待裁定，本节是其施工形态，重评时机一致

- **重评条件**：① 实盘 ≥6 月 Sharpe 稳定估计；② 收益分布矩估计稳定；③ 用查表校准当前 5/10/15% 阈值是否与"给定 Sharpe 的期望 MaxDD 分位"一致——若经验阈值过松则收紧，过紧则放宽。MVP 不替换阈值，仅作校准参考

- **跨文档**：§6.23 早期登记（v1.8.0）+ §6.37 keep-or-kill 待裁定（v1.35.0）+ 36号 §3.2 参数法 VaR √T 缩放持续性失效警示 + §4.24 Lévy-stable 解析互补

- **Python 伪代码**（4 测度查表 + strategy archetype 分类器 + 阈值输出）：

```python
import numpy as np
from dataclasses import dataclass
# §4.27 Drawdown Beyond Brownian Motion——4 测度查表校准 (arXiv:2608.00127 Landolfi 2026-07-31)
# Phase 3 校准阶段，MVP 仅校准参考不替换 §3.2 阈值

@dataclass
class DrawdownMeasures:
    max_dd: float          # MaxDD 最大回撤深度（95% 分位，负值）
    max_loss: float        # MaxLoss 最大单期损失（95% 分位，负值）
    final_neg_time: float  # FinalNegTime 水下时间占比（0-1）
    longest_recovery: int  # LongestRecovery 最长恢复交易日数

ARCHETYPE_PARAMS = {  # strategy archetype → 分布参数预设（Phase 2 实盘估计后覆盖）
    "trend":     {"skew": -0.3, "kurt": 5.0, "vol_clust": 0.6, "hurst": 0.55},
    "mean_rev":  {"skew": -0.5, "kurt": 7.0, "vol_clust": 0.2, "hurst": 0.45},
    "arbitrage": {"skew":  0.0, "kurt": 3.5, "vol_clust": 0.1, "hurst": 0.50},
    "t0_snipe":  {"skew": -0.6, "kurt": 8.0, "vol_clust": 0.8, "hurst": 0.50},
    "multi_fac": {"skew": -0.2, "kurt": 4.5, "vol_clust": 0.4, "hurst": 0.50},
}

def classify_archetype(returns: np.ndarray) -> str:
    """策略 archetype 分类器——基于收益分布矩 + Hurst 指数"""
    r = (returns - returns.mean()) / returns.std()
    skew, kurt = float(np.mean(r**3)), float(np.mean(r**4))
    hurst = estimate_hurst_rs(returns)  # R/S 法，Phase 2 用更稳健估计
    if hurst > 0.52 and skew < -0.1: return "trend"
    if hurst < 0.48 and kurt > 6.0:   return "mean_rev"
    if abs(skew) < 0.15 and kurt < 4.0: return "arbitrage"
    if kurt > 7.0 and skew < -0.4:    return "t0_snipe"
    return "multi_fac"

def mc_drawdown_measures(sharpe, params, horizon=252, n_sims=50000, seed=42):
    """Monte-Carlo 4 测度查表——放松高斯假设，保持真实 Sharpe+vol 不变"""
    rng = np.random.default_rng(seed)
    mu = sharpe / np.sqrt(horizon)  # 日均超额收益（保持真实 Sharpe）
    rets = simulate_nongaussian_returns(mu, params, horizon, n_sims, rng)
    nav = np.cumprod(1 + rets, axis=1)
    peak = np.maximum.accumulate(nav, axis=1)
    dd = (nav - peak) / peak
    max_dd = np.min(dd, axis=1)                # MaxDD
    max_loss = np.min(rets, axis=1)            # MaxLoss
    neg_time = np.mean(dd < 0, axis=1)         # FinalNegTime 水下占比
    longest_rec = np.array([_longest_recovery(d) for d in dd])
    return DrawdownMeasures(
        max_dd=float(np.percentile(max_dd, 5)),       # 95% 分位
        max_loss=float(np.percentile(max_loss, 5)),
        final_neg_time=float(np.percentile(neg_time, 95)),
        longest_recovery=int(np.percentile(longest_rec, 95)))

def calibrate_thresholds(sharpe, returns):
    """Phase 3 校准入口——archetype 分类 → 4 测度查表 → 与 §3.2 经验阈值对比"""
    archetype = classify_archetype(returns)
    measures = mc_drawdown_measures(sharpe, ARCHETYPE_PARAMS[archetype])
    empirical = {"warn": 0.05, "danger": 0.10, "crisis": 0.15}  # §3.2 经验阈值
    verdict = {lv: ("tight" if abs(measures.max_dd)/e > 1.2 else
                    "loose" if abs(measures.max_dd)/e < 0.8 else "ok")
               for lv, e in empirical.items() if e > 0}
    return {"archetype": archetype, "measures": measures, "verdict": verdict}
```

### 4.28 Aldridge & Krawciw AI Governance——4 层治理框架+regret-covariance policy drift+crowding model 联合回撤定量背书（2026-08-10 新增）

**方案**：[arXiv:2608.02311](https://arxiv.org/abs/2608.02311) [econ.EM] Aldridge & Krawciw（RiskAICenter）2026-08-03 "AI Governance for Institutional Readiness in Finance"。论文指出 agentic AI 在资产管理中获接受但治理滞后——**88% 受调金融从业者报告无 agentic AI 运营治理框架**（尽管 100% 知晓其部署），75 家美国大型资管 Form ADV 披露 AI 使用中仅 24 家有正式治理政策。论文论证此差距是**架构性而非文化性**——为确定性系统构建的治理假设静态验证，但持续重训练的 agentic policy 在设计上违反静态治理。

**4 层治理框架**（Policy / Engineering / Composition / Systemic）：

1. **Policy 层**：将驱动 agentic 策略的 reward function 视为 policy spec（非黑盒）——需声明 allowed action set / risk budgets / market-state constraints / user-account constraints 四元组，诱导 intended action set。**Kill-switch 触发应基于 inner（pre-decoding）LLM confidence 而非 declared confidence**——Chen et al. 2026 实证：declared confidence 被 decoding process 偏置，inner confidence 才对 realized accuracy 经验有效
2. **Engineering 层**：**regret-covariance statistic** 检测 policy drift——仅从观测数据计算（不需白盒访问），对比"intended policy 的预期 regret 协方差"vs"observed regret 协方差"，漂移超阈值触发告警。论文 §5.2.1 给出可复现数值示例（合成数据 + 代码自生成）
3. **Composition 层**：**calibrated crowding model**——两 agent 收敛于相关暴露时，joint drawdown probability 从 **39.2% 升至 79.3%**。论文 §5.4.1 两 agent crowding 模拟可复现。这是对"分散失效"（§3.21 根因②"原本相关性较低的策略也会出现同向波动"）的**定量模型背书**——crowding 不是定性警示而是可计算的概率放大因子
4. **Systemic 层**：vendor embedding model 升级可shift策略收益分布而不触发任何单点告警——需跨组件监控（data feed / embedding model / portfolio construction 任一组件单独"未坏"但组合漂移）。论文以一部署 LLM-embedding 策略 18 月 + 同期一只自主基金爆仓为案例，澄清哪些控制跨 agentic / human-directed 风险-taking 可迁移

**90-day 实施序列**：论文给出机构 90 天落地 4 层框架的实施顺序（policy spec 声明 → regret-covariance 监控 → crowding 模型校准 → vendor 漂移跨组件监控）。

**与本项目的关系**：

1. **与 §3.5 Kill Switch 治理的关系**：§3.5 当前是"触发条件 + 执行路径 + 不可覆盖"三件套，Aldridge 4 层框架提供**治理架构背书**——Policy 层（§3.5 触发条件声明）+ Engineering 层（§3.5 执行路径）+ Composition 层（§3.16 回撤归因相关性维度）+ Systemic 层（§3.15 盘前初始化 Ghost 检测跨组件）。**inner LLM confidence kill-switch** 是新维度——本项目当前 Kill Switch 基于 drawdown_pct / VaR breach / BlackSwanSignal 三类**外部可观测量**，Aldridge 建议 agentic 系统应监控 LLM 内部 confidence（pre-decoding logits 或 embedding 不确定性）作为**前馈 kill-switch 触发器**。与 §4.18 BOCD（run-length 后验概率）正交：BOCD 是收益分布漂移检测，inner confidence 是模型自身不确定性检测——两者可叠加（BOCD 触发=分布变了，inner confidence 触发=模型自己不确定了）
2. **与 §3.21 行业实证背书的关系**：§3.21 根因②"分散失效"目前是定性引用（多家私募复盘共识"原本相关性较低的策略也会出现同向波动"），Aldridge crowding model 提供**定量模型**——joint drawdown probability 39.2%→79.3% 是可计算的 crowding 放大因子，可作为 §3.16 回撤归因相关性维度（avg_corr>0.7=系统性）的**量化升级路径**：从 avg_corr 单点阈值升级到 crowding-adjusted joint drawdown probability。与 §4.21 Transfer-Entropy+Hawkes 网络级前馈预警互补：§4.21 是网络拓扑级前馈，Aldridge crowding 是组合配置级定量
3. **与 §3.15 盘前初始化 Ghost 检测的关系**：Aldridge Systemic 层"vendor embedding model 升级 shift 收益分布"对应本项目"策略代码/模型版本升级后跨重启状态恢复"——§3.15 盘前初始化的 broker 持仓核对（Ghost 检测）是 Engineering 层 regret-covariance 的物理对应（检测"预期持仓 vs 实际持仓"漂移）。Aldridge 提供"跨组件漂移监控"框架：data feed / embedding model / portfolio construction 任一组件单独"未坏"但组合漂移——本项目可映射为"行情数据源 / 因子计算 / 仓位裁决"三组件的跨组件一致性校验
4. **与 §4.18 BOCD 的关系**：regret-covariance 与 BOCD 是两种**互补的漂移检测**——BOCD 检测收益分布的 changepoint（run-length 后验），regret-covariance 检测 policy 行为的 drift（intended vs observed regret 协方差）。前者是"环境变了"，后者是"策略行为偏离 intended"——两者可叠加（BOCD 触发=需重新校准环境模型，regret-covariance 触发=需审查策略代码/参数是否漂移）
5. **与 FSB 2026-06-10 AI 稳健实践咨询报告（§3.5 ⑧）的关系**：FSB 是全球监管顶层锚点（G20 框架 12 项 SP），Aldridge 是**机构级实施框架**（4 层 + 90-day 序列）。FSB SP3"AI monitoring AI"对应 Aldridge Engineering 层 regret-covariance，SP9"bounded authority"对应 Aldridge Policy 层 intended action set，SP10/SP11 对应 Composition/Systemic 层。两者是"监管原则 ↔ 机构实施"的配对

**远期登记理由**：

1. **regret-covariance 是新工具**：不同于 §4.8 CUSUM（阈值法）、§4.18 BOCD（概率 changepoint）、§4.21 Transfer-Entropy（网络级前馈）——regret-covariance 是**policy 行为级 drift 检测**，填补"策略行为是否偏离 intended"的检测空白。当前 §3.15 Ghost 检测是持仓级（物理漂移），regret-covariance 是行为级（逻辑漂移），两者正交
2. **crowding model 量化"分散失效"**：§3.21 根因②"分散失效"目前是定性，Aldridge 提供 39.2%→79.3% 定量因子——Phase 2 可将 §3.16 回撤归因相关性维度从 avg_corr 单点阈值升级到 crowding-adjusted joint drawdown probability（需策略间相关性矩阵 + crowding 模型校准）
3. **inner LLM confidence kill-switch 前馈维度**：当前 Kill Switch 三类触发器（drawdown/VaR/BlackSwan）都是**事后或外部**，inner confidence 是**事前+内部**——若项目远期引入 LLM 决策（当前是规则式+因子，无 LLM），inner confidence 可作为"模型自身不确定"的前馈 kill-switch 触发器。当前不适用（无 LLM 决策层），但登记为远期候选
4. **4 层治理框架是架构背书**：§3.5 Kill Switch + §3.15 盘前初始化 + §3.16 回撤归因 + §3.18 盘后持久化已隐含 4 层结构，Aldridge 提供正式框架命名 + 90-day 实施序列作为治理成熟度评估参照
5. Phase 3+ 远期（需 LLM 决策层就绪才能用 inner confidence；regret-covariance + crowding model 可在 Phase 2 实盘 6 月+ 数据积累后评估）

**不过度工程审查**：

- regret-covariance 需 intended policy spec 形式化（allowed action set / risk budgets / market-state constraints / user-account constraints 四元组）——本项目当前是规则式风控非 agentic policy，intended spec 即 §3.2 三层映射表 + §3.5 Kill Switch 触发条件 + §3.7 不可覆盖原则，已隐含声明，regret-covariance 计算成本低（协方差矩阵 + 阈值比较）
- crowding model 需策略间相关性矩阵 + crowding 参数校准——本项目 §3.16 回撤归因已有 avg_corr 计算，crowding model 是其量化升级，增量成本低
- inner LLM confidence kill-switch 需 LLM 决策层——本项目当前无 LLM 决策（规则式+因子），此项**远期不适用**除非引入 LLM 决策。登记为"若远期引入 LLM 决策则激活"的条件性候选
- 4 层治理框架是**架构命名**非新模块——本项目现有 §3.5/§3.15/§3.16/§3.18 已隐含 4 层，Aldridge 提供正式框架作为治理成熟度自评参照，零增量成本

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
- **第四阶段（远期演进方向登记，非已定路径）**：§4.6-§4.28 评估的学术研究方向，均暂缓或拒绝（详见 §6.8-§6.37 待裁定）。v1.33.0 补：此前 Stage 4 仅提 §4.12-§4.15 / §6.17-§6.20，遗漏 §4.16-§4.28 + §6.21-§6.37 共 24 项远期登记。以下按族全量对齐：

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
> **优先级**：P0=最小补丁（立即可做，低依赖）｜P1=短期（实盘 1-3 月后）｜P2=中期（实盘 6 月+）｜P3=远期（实盘 1 年+）｜P4=超远期（实盘 2 年+ 或依赖架构演进，如组合配置层独立模块化）｜P5/P5+=理论远期（仅登记防重新调研，无施工计划）（v1.38.0 补 P4/P5 定义——此前表头只定义到 P3，但 §6.17/§6.30/§6.35 等条目已用 P4、§6.32 已用 P5）

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
| P1 | §6.11 Kill Switch 4 层架构 + Ghost Position 检测 + A 股新规适配 | §3.5.1 L2 broker 端硬止损 + L3 看门狗进程缺失；A 股 2026 新规（每秒15笔/撤单率15%）要求 Kill Switch 平仓分批拆单 | 实盘验证 miniQMT broker-side bracket 支持 + 盘前持仓核对检出 Ghost 频率后决定；最小补丁：盘前持仓核对 + reset_kill_switch 强制 holdings_verified_zero + 平仓按 15 笔/秒分片 |
| P0 | §6.12 盘前初始化 + 盘后持久化（§3.15/§3.18 配对）| §3.15 盘前加载 + §3.18 盘后保存是配对操作，当前无 `state_store` 持久化层，peak NAV/状态机态/recovery_step 重启即丢失；盘前未调用 Ghost 检测；盘后无原子提交 | 最小补丁立即可做：① `capital_curve_manager.peak` 与 `drawdown_tracker` 窗口持久化到 DB；② 盘前调用 `detect_ghost_positions`；③ §3.18 盘后 `mark_persistable` 原子提交（DB 事务）。完整 `state_store` + DrawdownStateMachine 待 §6.6 |
| P1 | §6.13 回撤归因端到端流程 | §3.16 当前无"组合回撤 → 归因到策略/因子 → 分流响应"的自动化流程，仅靠人工判读 §3.12 矩阵 | 最小补丁：`daily_auditor` 已有 `AttributionBias`，回撤 WARNING 触发时自动调用并记入日志；完整归因（相关性矩阵 + 因子偏差 + regime 交叉）待 §6.7 |
| P0 | §6.14 A 股 2026 新规 Kill Switch 平仓适配 | §3.5.1 新规下持仓 >15 只需分批平仓（15 笔/秒），撤单受 15% 日撤单率约束，原"瞬时全清"假设失效 | 与 §6.11 一并施工：`trigger_kill_switch` 内部按 15 笔/秒分片 + 撤单率预检 + 全清超时告警 |
| P1 | §6.15 Static 模式破产底线 Kill Switch | §4.10 trailing 25% Kill Switch 在大幅盈利后仍远高于初始本金，缺"绝对破产防护"；static 模式（initial × 0.85）作为第五类 Kill Switch 触发源 | 与 §6.11 一并施工：§3.5 触发条件表新增"组合净值 < 初始本金 × 0.85" |
| P3 | §6.16 六类风险失败机制 + HRP 聚类归因 | §3.16 扩展维度 + §4.11 HRP 聚类归因。López de Prado 2026 JAM 六类失败机制（statistical/factor/liquidity/model/governance/decision-infrastructure）提供统一归因框架；HRP 聚类树识别"部分系统性"策略簇，比 avg_corr 二元阈值更精细 | 25_multifactor IC 衰减监控 + 55_monitoring_review 系统健康均 production + 策略数 ≥8 个后，将六类框架 + HRP 聚类纳入 §6.7 归因流程作为扩展维度 |
| P4 | §6.17 MPC 连续风险厌恶调整 | §4.12 Nystrup/Boyd 2019 + DLP-SMPC 2026 用 MPC 根据已实现回撤连续调整 risk aversion γ(dd)，替代当前 §3.2 离散阈值 5/10/15%→80/50/30%。当前 recovery_factor 0.25→0.50→0.75 阶梯是其离散近似 | ① 实盘 ≥2 年稳定样本（HMM 参数估计可靠）；② alpha 层收益预测模块（HMM 或等价物）production（MPC 前馈需 μ/Σ 输入）；③ 业主对连续风控接受度验证后，引入 MPC 平滑化 risk aversion |
| P4 | §6.18 趋势跟踪回撤防御层 | §4.13 Noguer i Alonso & Al-Fallouji 2026-07 CVaR 框架提出"趋势跟踪在持续回撤中递增防御"前馈层。当前 Protocol 纯反馈（已亏才减），无前馈防御；A 股不能做空+无期权，只能"减仓/空仓"实现 | ① 实盘验证 A 股趋势信号在持续回撤中的防御有效性；② 与 34_regime_meta_allocator 裁定 regime vs 趋势跟踪职责边界（是否冗余）；③ 趋势信号来源模块确定（G09/G10）后，作为 §3.9 regime 之外第二前馈防御层 |
| P2 | §6.19 CDaR 回撤深度连续度量 | §4.14 Chekhlov/Uryasev CDaR = drawdown 序列的 CVaR，path-dependent coherent measure，LP 可解。当前 §3.8 用 drawdown_pct 单点值，CDaR 是尾部回撤均值；Man Numeric 2025 论证 CVaR 优于方差同样适用 CDaR 优于 MaxDD | 与 §4.6 UI / §4.9 PI 同步重评。实盘发现"浅回撤长时间"或"单点 drawdown_pct 不足以反映回撤痛苦"后，引入 CDaR 作为 ① 回撤深度补充度量（报告）+ ② 31_position_sizing 仓位优化的回撤约束。优先级高于 UI/PI（coherent + LP 可解） |
| P1 | §6.20 0.5% Recovery Protocol（单笔风险层面恢复） | [edgeflo 2026-03](https://www.edgeflo.com/blog/de-risk-after-drawdown) 实证：连续 2 笔亏损（或 2% 回撤）后，risk_per_trade 从 1% 降至 0.5%，单笔 3R 盈利回补 +1.5% 覆盖 2 笔 0.5% 亏损。当前 §3.4 recovery_factor 阶梯是**仓位上限**恢复，0.5% protocol 是**单笔风险**恢复——两者正交可叠加（recovery_factor=0.5 × risk_per_trade=0.5% → 实际风险 0.25% = 双保险） | 实盘运行后，若 recovery 期间单笔风险未同步收缩导致二次回撤，引入 `risk_per_trade` 随 `recovery_step` 联动下调（25%→0.5% / 50%→0.75% / 75%→1.0% / 100%→1.0%）。最小补丁：`position_sizing_engine` 读取 `drawdown_controller.recovery_factor` 联动调整 risk_per_trade |
| P2 | §6.21 Conformal Kelly drawdown dial | [arXiv:2608.01494](https://arxiv.org/html/2608.01494v1)（2026-08-02）：conformal 预测区间下行连续 miss 超历史率→缩减 leverage，开发窗口 MaxDD 27.7%→20.3%，Sharpe 提升，rank-based p=0.024。**关键设计原则**：slow unweighted per-asset rolling quantile 优于 adaptive 方法（宽度稳定性 > 局部锐度）。当前 §3.4 recovery_factor 是回撤驱动阶梯，Conformal Kelly 是预测区间 miss 驱动自适应 leverage | ① conformal 预测层（[31_position_sizing](31_position_sizing.md) 或独立模块）production；② 实盘积累足够 conformal interval miss 样本校准"连续 miss 超历史率"阈值；③ 业主对"预测区间驱动 leverage"接受度验证。远期集成时用最简 per-asset rolling quantile，不追 locally adaptive 变体 |
| P3 | §6.22 Data-Driven Drawdown Restart | [arXiv:2303.02613](https://arxiv.org/pdf/2303.02613v1)（Hsieh 2023）：drawdown modulation 接近限值时带 restart 机制（数据驱动重置策略参数），有交易成本场景下仍优于无 restart。当前 §3.11 RECOVERY 阶梯是 restart 的离散实现，但未实现"数据驱动参数重置" | 实盘 ≥1 年后，若 RECOVERY 阶梯恢复后策略参数（ATR 倍数/止损位/仓位权重）仍沿用 pre-drawdown 配置导致二次回撤，引入 data-driven 参数重置：restart 时用最近 N 日数据重估 ATR/相关性矩阵/regime 参数 |
| P2 | §6.23 Non-Gaussian Drawdown Lookup Tables | [arXiv:2608.00127](https://arxiv.org/abs/2608.00127)（Landolfi 2026-07-31）：给定 Sharpe + 收益统计结构（skew/峰度/波动率聚集）生成 4 度量查表（MaxDD/最大损失/末尾负时间/最长恢复时间）。核心发现：① Gaussian 表在非正态下误警（四度量移动方向不同）；② 持续性下回撤"放大"是 `T^(H-1/2)` dispersion scaling 即 √T 校准失效，非路径几何本征危险。当前 §3.2 阈值（5/10/15%）+ §3.4 recovery_factor 阶梯是经验值，查表提供统计校准依据；警示 [36_var_es_monitoring](36_var_es_monitoring.md) §3.2 参数法 VaR 的 √T 缩放在持续性下失效 | ① 实盘 ≥6 月 Sharpe 稳定估计（Rej-Bouchaud 框架需 SR 输入）；② 收益分布矩估计（skew/kurt/波动率聚集参数）稳定；③ 用查表校准当前 5/10/15% 阈值是否与"给定 Sharpe 的期望 MaxDD 分位"一致——若经验阈值过松（查表 MaxDD 95% 分位 < 5%）则收紧，过紧则放宽。MVP 不替换阈值，仅作校准参考 |
| P3 | §6.24 CED 线性因子归因 | [Goldberg & Mahmoud 2016](https://alexandria.unisg.ch/server/api/core/bitstreams/f53d98e4-3cfb-4517-8054-8287a2912bc8/content)（UC Berkeley + St. Gallen）：CED = maximum drawdown 分布的尾部均值，positive homogenous → Euler 定理线性归因到因子，convex → 可优化，对 serial correlation 敏感（回撤路径依赖特性）。当前 §3.16 用 avg_corr 启发式（>0.7 系统性 / <0.4 策略特定）做二元归因，CED 提供量化每个因子贡献度的严谨框架。与 §4.14 CDaR（组合优化）互补：CDaR 用于优化（LP），CED 用于归因（Euler 分解） | ① 策略数扩展到 ≥8 个后，avg_corr 无法区分"部分系统性"（簇内高相关+簇间低相关）时引入；② 实盘 ≥1 年后样本充足，CED 尾部估计稳定；③ 与 §4.14 CDaR / §4.11 HRP 聚类归因同步评估优先级与组合方式 |
| P2 | §6.25 Schmitt RWC Conformal Risk Control | [arXiv:2602.03903](https://arxiv.org/pdf/2602.03903)（Schmitt 2026-02, Oxford）：Regime-Weighted Conformal Risk Control——用指数时间衰减 + regime 相似性权重校准 VaR 安全缓冲，model-agnostic wrap 任意 quantile 预测器，weighted exchangeability 下有限样本覆盖保证。TWC 是 drift 下强默认，RWC 增加 regime 加权改善 regime-conditional 稳定性。与 §6.21 Conformal Kelly 正交互补（Kelly 管 leverage，RWC 管 VaR buffer），RWC 更直接作用于 §3.10 drawdown_controller 的 C 层 VaR 输入 | ① [36_var_es_monitoring](36_var_es_monitoring.md) conformal 预测层（quantile forecaster + calibration pipeline）production；② [34_regime_meta_allocator](34_regime_meta_allocator.md) regime 特征工程稳定（regime embedding 或可用相似性度量）；③ 实盘 ≥6 月 conformal calibration set 积累。最小集成路径：先 TWC（time-weighted，简单），验证稳定后再加 RWC（regime-weighted） |
| P0 | §6.26 回撤状态滞后-恢复双阈值（Hysteresis）算法 | §3.20 形式化：§3.11 状态机有升级触发条件但无降级恢复条件，临界态 thrashing 风险。§3.20 补齐 hysteresis 双阈值（恢复阈值 = 触发阈值 × 50%）+ min_hold 持续时间门控（5/10/20 交易日）+ 毕业准则（连续盈利日 + 10 笔期望 ≥ 0.3R + 合规率 ≥ 80%）。对齐 [37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md) §3.6（v1.0.3）流动性危机恢复算法的设计模式。当前代码无 hysteresis 实现——`DrawdownController` 降级用与升级相同阈值 | 最小补丁（立即可做）：① `DrawdownController._evaluate_recovery` 增加半阈值判定（drawdown < 触发阈值 × 0.5 才降级）；② 增加 `min_hold` 计时器（状态进入后至少 N 日才可降级）；③ 毕业准则先做"连续 3 盈利日"单项（最简），完整 4 项准则待 §6.7 回撤类型诊断施工。完整 hysteresis 算法 + 毕业准则待 §6.6 DrawdownStateMachine 落地 |
| P3 | §6.27 BOCD 概率 Kill Switch | §4.18 Adams & MacKay 2007 BOCD 维护 run-length 后验 `P(r_t \| x_{1:t})`，输出 `P(changepoint) = P(r_t=0)` 连续概率。mathandmarkets 2026-02 + quantbeckman 2025-11 工程化方案：N-IG 共轭先验 + Student-t 似然（重尾适配）+ 双触发（P>0.8 硬停机 / P>0.5 持续 5 日减仓 50%）+ log-space 数值稳定 + pruning。是 §4.8 CUSUM/Hawkes/Lee-Mykland 的概率化演进——CUSUM 需指定 μ₀（选择困境）+ 二元阈值，BOCD 无需 μ₀ + 概率输出可分级响应 | ① 实盘 ≥1 年后，与 §6.10 CUSUM/Hawkes/Lee-Mykland 同步重评；② 若 §3.5 固定阈值 Kill Switch 误触发频繁或漏检结构断点，引入 BOCD 作为 §6.10 统计检测的概率化升级；③ 似然模型用 Student-t（ν=5 起步），hazard 用常数 1/λ（λ=252，期望 1 年变点一次）；④ 最小集成路径：先单策略试运行 BOCD（输出 P(changepoint) 仅供参考不触发），验证检测有效性后再接入双触发系统 |
| P3 | §6.28 波动率匹配阈值 + 历史涨幅动态防御仓位 | [guorn 2026-04](https://guorn.com/forum/post/p.200941.361906578502334)（A 股回撤择时实证，1992-2006 历史数据）：① **倒 U 形最优区间**——回撤阈值过浅→临界态 thrashing，过深→触发滞后错过防御窗口，存在与策略波动率匹配的最优区间；② **vol-matched stop**——止损阈值应与策略自身波动率匹配（高波动策略需更宽阈值否则 whipsaw，低波动策略需更紧阈值否则太晚），而非统一固定数值；③ **历史涨幅动态防御仓位**——DEFENSIVE 态仓位应根据 pre-drawdown 涨幅动态调整（涨幅 >100%→0.3 / >50%→0.5 / 否则 0.6），涨幅大则同幅度回撤更值得防守。当前 §3.2 固定 5/10/15% 无 vol-matching + §3.4 recovery_factor 固定 0.25→0.50→0.75 阶梯无历史涨幅感知。**与 §6.23 Landolfi 的关系**：Landolfi 是统计严谨校准（给定 Sharpe 的 MaxDD 分位查表），guorn 是经验 vol-matching + 涨幅感知——两者正交互补可叠加 | ① 实盘 ≥6 月积累策略年化波动率估计；② 用策略 vol 标定阈值：`threshold = k × annualized_vol`（k 待校准，参考 guorn 倒 U 形实证找最优 k）；③ 历史涨幅维度：recovery_factor 阶梯乘以 gain_factor（pre-drawdown 涨幅 >100%→0.6 / >50%→0.8 / 否则 1.0），涨幅大则恢复更保守。MVP 不改固定阈值，仅作远期校准参考 |
| P3 | §6.29 Fanous Recovery-Efficiency Protocol（非对称去风险路径依赖框架） | [arXiv:2605.09123](https://arxiv.org/abs/2605.09123)（Fanous 2026-05，"The Engineering of Skew: A Path-Dependent Framework for Asymmetric Volatility Management"）：① **Recovery-Efficiency Protocol**——将回撤深度、水下时间、恢复负担缩减、反弹参与度四维度链接为 allocator-facing 报告准则，是 path-dependent 风险管理框架而非单一阈值；② **非对称去风险**（skew engineering）——降低有害下行参与度 > 降低上行参与度，控制 submergence 同时保留足够反弹参与度维持复利，与 §4.5 CPPI 的对称去风险（cushion 缩即整体缩）形成对比；③ **恢复负担非线性**——R = 1/(1-D) - 1（D=20%→R=25%，D=50%→R=100%），对称去风险在深回撤时牺牲过多上行导致恢复负担无法缩减；④ **ML/AI 定位**——conditional estimation / regime mapping / robustness testing / model-risk governance 工具而非市场预测，对齐本项目 AI 开发定位。当前 §3.4 recovery_factor 阶梯是对称缩减（0.25→0.50→0.75 全仓同步恢复），缺非对称维度。**与 §6.21 Conformal Kelly 的关系**：Kelly 是预测区间 miss 驱动 leverage 缩减（前馈），Fanous 是回撤路径驱动非对称缩减（反馈）——两者正交 | ① 实盘 ≥1 年后，若发现 recovery_factor 对称恢复导致"反弹参与不足→恢复期过长"（Fanous 框架的 recovery burden reduction 缺失）；② 最小集成：recovery_factor 阶梯拆分为 downside_factor × upside_factor（下行缩减更激进 / 上行恢复更快），如 DEFENSIVE 态 downside_factor=0.2 / upside_factor=0.6（当前两者均为 0.5）；③ rebound participation 指标纳入 §3.18 盘后持久化（recovery 期间 upside capture ratio vs downside capture ratio）。MVP 不改对称恢复，仅作远期校准参考 |
| P4 | §6.30 CPPI+风险预算两阶段法（组合配置层远期候选） | [东方证券 2026-04 "CPPI+风险预算"两阶段法](https://www.uufund.com/Report/Detail?id=AP202604121821139947)：第一阶段 CPPI 优化单资产夏普比（`E = m × (V − Floor)`），第二阶段风险预算（RB）配置，A 股 2006-2026 全样本年化 13.41%/波动 8.45%/MaxDD -10.91%/Sharpe 1.53/Calmar 1.23，优于等权和纯 RP。三层风险控制：CPPI 保本期 max 损失约束 + 动态回撤控制 + 风险预算分散。**对 §4.5 拒绝 CPPI 的诚实账本反证**——东方证券用三层架构兜底 gap risk（动态回撤控制层），裸 CPPI 的 gap risk 在三层协同下可控。**与 §4.5 拒绝理由的关系**：拒绝理由#1（cash-lock）仍成立（东方证券未解决 cushion=0 永久退出）；拒绝理由#2（A股 gap risk）被反证（三层兜底可控）；拒绝理由#3（无保本承诺）仍成立（东方证券 CPPI 适合保本场景，本项目无保本语义）。**为何记为远期候选而非采纳**：① 定位正交——东方证券 CPPI 是组合配置层（单资产 Sharpe 优化 + 多资产 RB），本项目回撤 Protocol 是 sleeve 级风险节流（[30号 §2.2](30_multi_strategy_concurrency.md)），层级不同；② 架构耦合——东方证券三层是组合配置一体化设计，拆单层套用破坏协同；③ 可解释性优先——CPPI m 值主观，5/10/15% 阈值更明确。**借鉴价值**：东方证券"动态回撤控制"层与本项目 §3.20 Hysteresis + §3.4 recovery_factor 同构（回撤越深仓位越轻的反馈式），是同一设计原则的不同工程实现 | ① 仅当项目演进到"组合配置层"独立模块时（当前 sleeve 级 + firm 级两层架构不引入第三层）重新评估；② 借鉴"动态回撤控制"连续函数思路校准 §3.2 阈值（与 §6.28 vol-matched threshold 互补）；③ MVP 不引入 CPPI，§4.5 拒绝维持，本条仅作诚实账本记录防止"A 股 gap risk 使 CPPI 失效"以偏概全 |
| P2 | §6.31 Shelby AI Resilience Gap fallback 教义 + VeritasChain Flight Recorder 审计层 | [arXiv:2607.07359](https://arxiv.org/abs/2607.07359)（Shelby 2026-07-08，"The AI Resilience Gap"）提出 AI Resilience Framework 五要素：① **依赖映射**（AI 系统依赖链可视化）；② **关键性-可替代性分层**（哪些 AI 功能关键且不可替代）；③ **impact tolerance 扩展到 AI 失效模式**（不只"系统宕多久"，还"AI 决策错误多久能容忍"）；④ **显式 fallback 教义**（AI 失效时降级运行模式：仅平仓不开新仓 / 仅用规则引擎不用模型 / 完全人工接管）；⑤ **provider 集中度管理**（AI 模型供应商集中度风险）。**与本项目的关系**：本项目 100% AI 开发，§3.5 Kill Switch 是"AI 失效→全停"的硬通道，但缺"AI 失效→降级运行"的中间态——Shelby 的 fallback 教义填补"kill switch 触发后下一步做什么"的空白。**[VeritasChain 2026-01-20](https://veritaschain.org/blog/posts/2026-01-20-five-incidents-algorithmic-trading-flight-recorder/) Flight Recorder**（分析 Two Sigma 22 个月未检出参数操纵 + SEC 罚 9000 万美元事件）提出 append-only + prev_hash 哈希链 + Ed25519 签名 + RFC 8785 JSON 规范化的三层加密审计架构——本项目 §3.18 盘后持久化的 `daily_auditor.log_*` 当前是普通日志，远期应向 flight recorder 标准演进（防参数操纵不可篡改审计） | ① **fallback 教义**：实盘运行后，若 §3.5 Kill Switch 触发频率高于预期（说明全停代价过大），定义降级运行模式——Mode 1 仅平仓不开新仓（AI 信号可信度低时）/ Mode 2 仅用规则引擎（AI 模型层失效时）/ Mode 3 完全人工（极端场景）；② **VeritasChain 审计层**：实盘 ≥1 年后，若 `daily_auditor` 日志出现参数篡改/回填争议，引入 append-only 哈希链日志（每条 `log_*` 追加 prev_hash + Ed25519 签名），与 §3.5 COMPEL 四模式的"取证捕获"要求对齐；③ MVP 不引入 fallback 教义与 flight recorder，保持 kill switch = 全停的简单语义，本条仅作远期登记 |
| P5 | §6.32 Put-Option Sleeve（convex insurance 腿）+ Four-Axis Hedge Diagnostic —— arXiv:2607.00883 双 sleeve 框架补全 | [arXiv:2607.00883](https://arxiv.org/abs/2607.00883)（Noguer i Alonso & Al-Fallouji 2026-07-01，"Tail Risk Management with Puts and Trend Following: A CVaR Framework for Crashes and Drawdowns"）把尾部风险管理建模为**两 sleeve 分配问题**而非工具选择——① **long OTM put options**（convex insurance，jump impact 即时 reprice，但 IV>RV 持续导致 premium drag）；② **systematic trend-following overlay**（首震滞后因信号须穿零，但持续回撤中递增防御且无 premium）。§6.18 仅采纳 trend-following 腿（A 股适配为减仓/空仓），本条补 put-option 腿。**时间分离核心洞察**：两 sleeve 互补非替代——put 防突发崩盘（jump）、trend 防持续回撤（grind），固定等权/网格优化混合均比单一 sleeve 降 terminal CVaR。**四轴 hedge-quality 诊断**（可移植贡献）：conditional convexity（坏态非对称共动）/ tail-event reliability（尾部事件正收益概率）/ non-stress carry（非压力期成本）/ drawdown persistence（保护持续时间）——可评估任意 hedge 含 §6.18 减仓/空仓作"synthetic put"。**§6.18 事实订正**：§6.18 称"A 股不能做空+无期权"**事实不准**——A 股有 50ETF 期权（2015）、300ETF 期权（2019）、中证1000 ETF 期权（2022）、沪深300/中证1000 股指期权，组合层 put 对冲**可行**；约束：无个股期权、深 OTM 流动性薄。**HJB viscosity 解 + CVaR policy-gradient identity** 提供连续时间随机控制理论框架。**为何 P5+ 远期**：MVP sleeve 级用减仓/空仓（§6.18 trend 腿）已足；put-option sleeve 是**组合层**尾部对冲 mandate，需期权交易基础设施 + premium budget + 滚动管理，与 §6.30 组合配置层远期同层级 | ① 仅当项目演进到"组合配置层"独立模块（同 §6.30 触发条件）；② 期权交易基础设施就绪（miniQMT 期权行情/下单支持验证）；③ premium budget 框架（年化 premium drag 预算占 NAV 比例，参考 IV-RV spread 历史均值）；④ **四轴诊断可先于 put sleeve 落地**——用作 §6.18 减仓/空仓 hedge 质量评估工具。MVP 不引入 put-option sleeve，§6.18 trend 腿维持，本条补全论文双 sleeve 框架诚实账本 |
| P3 | §6.33 Non-concave VaR 约束下"赌博回本"行为理论警示——floor 设计理论背书 | [arXiv:2608.05623](https://arxiv.org/abs/2608.05623)（Li, Lyu & Wei 2026-08-06，"Non-concave Corporate Management with Option Incentives under Value-at-Risk Constraint"）研究风险厌恶管理者在 VaR 约束下的动态企业风险管理，目标函数因固定薪酬+期权激励呈**非凹性**。通过 concavification + 分位数方法推导出最优努力/终端企业价值/项目选择的显式解（九种情形）。**核心发现**：① VaR 约束在**地板较低**时改善下行保护+降低破产概率——约束迫使管理者在亏损早期即去风险，是"防御性"的；② VaR 约束在**地板过高**时反而**增加破产概率**并诱发**"赌博回本"（gambling for resurrection）行为**——管理者因非凹目标函数（期权激励在地板以下价值为零），在接近地板时选择极高方差项目"赌一把回本"而非保守减仓，VaR 约束从"防御性"变为"诱导性"。**对本项目的价值**：§4.4 已拒绝"回撤进入 RiskSignal 参与下次决策"并记录"进入 RiskSignal 会产生'亏多了该更激进回本'的赌博倾向"——本论文为该设计决策提供**量化理论背书**：非凹目标函数（对应本项目"回撤=沉没成本不进 alpha 信号"的拒绝理由）下，将亏损信息引入决策会诱导赌博行为。**对 §3.2 阈值设计的启示**：当前三层映射（5/10/15% 内层早预警 + 8/15/20/25% 外层生存边界）采用**保守低地板**策略——5% WARNING 远低于 8% 外层边界，正是论文验证的"低地板=防御性"区域；若将 WARNING 提高到 7%+ 接近外层边界（高地板），论文证明会诱发赌博回本。**与 §6.28 vol-matched threshold 的关系**：§6.28 主张阈值应与策略波动率匹配（高波动策略需更宽阈值），本论文补充**上限约束**——阈值不能过宽（高地板诱发赌博），也不能过紧（§6.28 低波动策略需更紧阈值否则太晚），两者共同界定阈值的**可行区间**。**定位 P3 理论背书非新算法**：本条不引入新施工算法，仅作为 §4.4 拒绝理由 + §3.2 阈值设计的理论支撑，防止未来审查时"阈值过保守"误判而放宽阈值 | 无重评条件——理论背书条目，§3.2 阈值调整时须引用本条检查"新阈值是否进入高地板赌博回本区" |
| P3 | §6.34 Leakage-Safe Residual-Stress Signal——截面 PCA 残差压力前馈预警（vol 低态补充信号） | [Liu 2026-06 "Beyond Volatility: A Leakage-Safe Residual-Stress Signal for Drawdown Risk Monitoring"](https://www.mdpi.com/2227-9091/14/7/143)（MDPI Risks vol.14(7), Northwestern University）：从**截面 PCA 重构误差**构造 residual-stress 信号——① 用 SPY + 11 行业 ETF 的行业超额收益（sector excess returns），PCA 估计 common component；② residual stress = 截面 out-of-sample 重构残差的 RMS 幅值；③ **leakage-safe 设计**：PCA mapping 仅用 t-1 及之前信息估计，stress score 在 t 计算，high-stress 用 rolling train-only 分位数阈值（前移 1 日）——彻底消除 look-ahead bias；④ **核心实证结论**：realized volatility 是更强的**独立**基准，residual stress **不能替代** vol；但 residual stress 是**互补**的截面市场错位指标——**当 vol 低但 residual stress 高**时，未来 H=21 交易日 drawdown onset 概率显著高于 low-stress/low-volatility regime；⑤ event-overlap + lead-time 诊断表明 residual stress 可识别 vol 阈值规则漏检的 onset episodes，主要增量价值在**条件风险分层**而非系统性更早触发。**对本项目的价值**：① §3.5 Kill Switch 是**反馈式**（回撤已发生→触发），§6.18 trend-following 是**单标的趋势前馈**（趋势信号→减仓），§6.27 BOCD 是**单标的概率变点**——三者均无**截面错位前馈**维度，Liu residual-stress 填补此空白；② **vol 低态补充价值高**：当前 §3.5 VaR 5 级 + drawdown_pct 阈值在低 vol 态均不易触发（VaR 低 + drawdown 浅），但 residual stress 高时仍可能即将发生 drawdown onset——Liu 信号在 vol 低态提供**唯一的前馈预警**；③ **A 股适配**：A 股有申万一级 28 行业（比 Liu 论文 11 sector ETF 更细），可用申万行业指数或行业 ETF 做 PCA；④ **leakage-safe 与项目 PIT 纪律一致**：[15_data_feature_layer_spec](15_data_feature_layer_spec.md) 已有 bitemporal 模型 + look-ahead 检测，residual-stress 的 t-1 估计 + t 计算设计天然对齐。**与 §3.5 ⑦ ORCA + §4.23 Chen CSAD/CSSD 的关系**：ORCA 是 24 ETF + 127 谱特征 + RF walk-forward（重模型），Chen CSAD/CSSD 是截面离散度（轻量统计量），Liu residual-stress 是**截面 PCA 残差**（中等复杂度，比 CSAD 多一步 PCA 但比 ORCA 轻很多）——三者在"截面错位检测"维度形成**轻-中-重三档梯度**，Liu 居中。**与 §6.10 CUSUM/Hawkes 的关系**：CUSUM 检测单序列均值漂移，Liu residual-stress 检测截面结构错位——两者正交（CUSUM 是时间维度，Liu 是截面维度）。**暂缓理由**：① **需截面数据管道**：当前项目 5 策略独立 sleeve 架构下无申万行业指数实时管道（同 §4.23 Chen 暂缓理由）；② **vol 低态增量价值需 A 股验证**：Liu 论文用美股 SPY+11 sector ETF 验证，A 股行业轮动更快 + 散户占比高，residual-stress 信号的 lead-time 可能不同；③ **与现有 §3.5 Kill Switch 的功能关系**：residual-stress 是"前馈预警"（错位发生→减仓），Kill Switch 是"反馈触发"（回撤发生→减仓）——两者正交互补，但 residual-stress 施工优先级低于 Kill Switch（风险优先原则 + 当前 Kill Switch §6.11 4 层架构待施工） | ① 申万一级 28 行业指数实时数据管道建设完成（同 §4.23 Chen 重评条件）；② 实盘 ≥1 年后发现 §3.5 Kill Switch 事后触发滞后且 vol 低态漏检 drawdown onset，需截面错位前馈预警；③ §3.5 ⑦ ORCA 评估为过重 + §4.23 Chen CSAD/CSSD 评估为过轻时，Liu residual-stress 作为中等复杂度替代；④ 最小集成路径：先用申万行业指数做 offline backtest 验证 A 股 vol 低态 residual-stress 的 lead-time，再决定是否接入 §3.5 作为前馈预警维度。MVP 不接入，仅作远期登记 |
| P4 | §6.35 MFCCA 符号保留多重分形交叉相关组合分配——直接降低 drawdown 的组合配置层远期候选 | [arXiv:2608.04987](https://arxiv.org/abs/2608.04987) Kakinaka & Umeno 2026-08-05 "Portfolio Allocation under Heterogeneous Scales and Multifractality"。风险泛函 = 带符号 MFCCA 波动函数 F(s,q)，**保留局部去趋势协方差符号**使同向/反向运动以相反符号贡献风险（MFDCCA 修正符号丢失对冲效果）。q=2 退化为均值-方差（MVO 的严格泛化）。实证：每个收益水平降低 drawdown/VaR/ES **无损收益**。**与 30 号 §3.1 拒绝 MVO 的关系**：30 号拒绝 MVO 的权重敏感+样本不足，MFCCA 虽符号保留创新但仍需多尺度交叉相关估计（比 MVO 更重，与 O(N) 保证冲突）。**定位组合配置层**（同 §6.30 CPPI/§6.32 Put-Option Sleeve），与 sleeve 级回撤 Protocol 正交——Protocol 管"回撤后怎么减"，MFCCA 管"分配时怎么避免"。已由 [90号](90_methodology_open_questions.md) v1.3.0 risk parity 五级递进第五级登记，本条补 35 号 drawdown 维度交叉引用 + 诚实账本 | ① 项目演进到"组合配置层"独立模块（同 §6.30/§6.32 触发条件）；② 策略数 ≥8 个后多尺度交叉相关估计有意义；③ 实盘 ≥2 年多尺度收益数据积累；④ 最小集成路径：2 策略 × 3 尺度（日/周/月）offline backtest 验证 A 股符号保留增量价值。MVP 不引入，仅作远期登记 |
| P3 | §6.36 Robust Risk Parity (RRP) —— A 股实证的组合配置层远期候选 | [Li & Ye 2026 "Research on asset allocation strategies based on robust risk parity model"](https://ideas.repec.org/a/eee/finlet/v92y2026ics1544612326001170.html)（Finance Research Letters vol.92(C), DOI:10.1016/j.frl.2026.109586）。传统风险平价框架内集成：① 自适应扰动机制；② 鲁棒协方差估计；③ **GARCH 波动率预测**；④ **市场状态识别**（regime identification）；⑤ 因子结构协方差。**A 股 2012-2024 全样本实证**对比 TRP/EW/GMV/MaxRet/ERP 五基线，RRP 收益/Sharpe/Calmar 均优、波动和 MaxDD 更低。**独特价值**：少有的 A 股全样本实证组合配置方法（含牛熊周期），且 regime 识别维度与 [34号 RegimeMetaAllocator](34_regime_meta_allocator.md) 天然对接。**与 §6.35 MFCCA 互补**：MFCCA 是理论前沿（符号保留），RRP 是工程化集成（A 股实证+regime）。**组件可独立提取**：RRP 的 regime+GARCH 组件可不引入完整 RRP 框架，独立评估接入 34 号 regime 输入增强 | ① 34号 RegimeMetaAllocator regime 特征工程稳定后，评估 GARCH 波动率预测作为 regime 输入增强（组件级集成，不需组合配置层）；② 项目演进到组合配置层时评估完整 RRP 框架（同 §6.30/§6.32/§6.35 触发条件）；③ **A 股实证优先级高于 MFCCA**——RRP 有 A 股 2012-2024 实证，MFCCA 无 A 股实证。MVP 不引入完整 RRP，但 regime+GARCH 组件级集成可中期评估 |
| P2 | §6.37 Drawdown Beyond Brownian Motion 4 测度查表 keep-or-kill | §4.27 新增 Landolfi [arXiv:2608.00127](https://arxiv.org/abs/2608.00127) 2026-07-31 回撤阈值非高斯校准算法——4 测度（MaxDD/MaxLoss/FinalNegTime/LongestRecovery）查表证明单一高斯表系统性误警（4 测度不同步移动），fBm 持续性表观放大是 √-time 校准失效（T^{H-1/2} 自相似色散标度）而非路径几何本征风险。与 §6.23（同一论文 v1.8.0 早期登记）的关系：§6.23 是概念登记，§4.27 是施工算法形态，本条是 keep-or-kill 裁定——是否在 Phase 3 用 4 测度非高斯表替换当前 §3.2 单一高斯 √-time 校准的 5/10/15% 经验阈值。与 §6.21 Conformal Kelly / §6.25 Schmitt RWC 同期 Phase 3 校准 | 裁定时机：Phase 3 校准阶段启动前。重评条件：① 实盘 ≥6 月 Sharpe 稳定估计；② 收益分布矩（skew/kurt/聚集/Hurst）估计稳定；③ 用查表校准当前 5/10/15% 阈值——若经验阈值与查表 95% 分位偏差 >20% 则替换为 4 测度非高斯表，偏差 <20% 则维持经验阈值仅作校准参考 |
## 7. 待定问题（讨论要点对齐状态）

> 以下来自 00_index §3 G16 讨论要点，逐项对齐后落入 §3 决策。

- [x] ① 四级阈值（8/15/20/25%）落到 StrategyBook 内部的实现 spec → §3.2 三层映射表（代码用 5/10/15% 更紧，§2.5.1 作为生存边界）
- [x] ② 单策略 vs 组合层面分层（§2.5.3）→ §3.3 单策略 Soft/Hard Stop + 组合 systemic risk 分层
- [x] ③ 恢复机制（企稳 50%/创新高/强制休息 5 天，§2.5.2）→ §3.4 两段恢复 + §6.1 强制休息暂缓
- [x] ④ Kill Switch 触发条件与执行路径（§2.5.5）→ §3.5 多源触发 + 单一执行通道
- [x] ⑤ 日度熔断（组合 -4%/单策略 -5%）→ §3.6 daily_pnl_check 通用机制 + 4%/5% 阈值
- [x] ⑥ Kill Switch 不可覆盖原则 → §3.7 requires_manual_reset + 集中状态管理
- [x] ⑦ 回撤基准净值计算口径 → §3.8 peak NAV 高水位 + 扩张/收缩
- [x] ⑧ 与 regime Shrinkage 的协同 → §3.9 正交分工 + 乘性叠加
- [x] ⑨ 盘前初始化与跨重启状态恢复（§3.15 补充·非原始讨论要点）→ 4 阶段流程（Ghost 核对 → 状态机加载 → 基线校准 → 通道健康），§6.12 待裁定（P0 最小补丁：peak/窗口持久化 + 盘前 Ghost 调用）
- [x] ⑩ 回撤归因端到端流程（§3.16 补充·非原始讨论要点）→ 相关性归因（系统性 vs 策略特定）+ 因子归因（行为性 vs 统计性）+ regime 交叉验证，§6.13 待裁定
- [x] ⑪ A 股 2026 新规对 Kill Switch 执行的影响（§3.5.1 补充·非原始讨论要点）→ 每秒15笔/撤单率15%/50微秒停留约束，平仓需分批拆单，§6.14 待裁定（P0）
- [x] ⑫ Pain Index + TradeShield static 模式（§4.9/§4.10 补充·非原始讨论要点）→ Pain Index 暂缓（与 UI 同类择一）；TradeShield static 模式部分采纳（initial × 0.85 作为破产底线 Kill Switch 触发源），§6.15 待裁定
- [x] ⑬ 盘后状态持久化流程（§3.18 补充·非原始讨论要点）→ §3.15 盘前加载的配对保存流程（5 阶段：终态净值→peak NAV→状态机→nav_history→原子提交标记），与 §6.12 同步施工
- [x] ⑭ 六类风险失败机制 + HRP 聚类归因（§3.16 扩展 + §4.11 补充·非原始讨论要点）→ López de Prado 2026 JAM 六类失败机制（statistical/factor/liquidity/model/governance/decision-infrastructure）提供统一归因框架，当前覆盖 ①③④⑤、待施工 ②⑥；HRP 聚类树识别"部分系统性"策略簇，策略数 ≥8 后引入，§6.16 待裁定（P3）
- [x] ⑮ MPC 连续风险厌恶调整（§4.12 补充·非原始讨论要点）→ Nystrup/Boyd 2019 + DLP-SMPC 2026 用 MPC 根据已实现回撤连续调整 risk aversion γ(dd)，替代当前离散阈值。暂缓理由：HMM 需 ≥2 年样本 + alpha 层收益预测未成熟 + 杠杆不适用 + 可解释性硬约束。当前 recovery_factor 0.25→0.50→0.75 阶梯是其离散近似，§6.17 待裁定（P4 远期）
- [x] ⑯ 趋势跟踪回撤防御层（§4.13 补充·非原始讨论要点）→ Noguer i Alonso & Al-Fallouji 2026-07 CVaR 框架提出"趋势跟踪在持续回撤中递增防御"前馈层，当前 Protocol 纯反馈无前馈防御。A 股不能做空+无期权，只能"减仓/空仓"实现。暂缓理由：A 股趋势跟踪有效性未验证 + 与 regime 职责重叠需裁定 + 趋势信号来源未定，§6.18 待裁定（P4 远期）
- [x] ⑰ CDaR 回撤深度连续度量（§4.14 补充·非原始讨论要点）→ Chekhlov/Uryasev CDaR = drawdown 序列的 CVaR，path-dependent coherent measure，LP 可解，优于 MaxDD（单点非 coherent）与 UI/PI（全样本平均）。Man Numeric 2025 论证 CVaR 优于方差同样适用 CDaR 优于 MaxDD。暂缓理由：与 UI/PI 同类择一 + α 校准无行业标准 + 当前 drawdown_pct 足够 MVP。优先级高于 UI/PI（coherent + LP 可解），§6.19 待裁定（P2）
- [x] ⑱ 多 agent 协作回撤控制（§4.15 补充·非原始讨论要点）→ RMATS 2026-05 + MARCD 2026 多 agent 协作回撤控制（4 agent + 递归 Manager，MaxDD 9.62%）。**拒绝（过度工程）**：个人项目不需要多 agent 协作 + LLM agent alpha 不可作部署证据（arXiv:2605.16895 The Alpha Illusion）+ Risk Agent 独立性本项目已实现（§4.2）+ RL 加性惩罚已评估选乘性（§3.9）。仅借鉴思路（Risk 独立 / 多源 circuit breaker / CVaR+EWMA），不照搬架构，不设重评条件
- [x] ⑲ CED 线性因子归因（§4.16 补充·非原始讨论要点）→ Goldberg & Mahmoud 2016（UC Berkeley + St. Gallen）Conditional Expected Drawdown = maximum drawdown 分布的尾部均值，positive homogenous → Euler 定理线性归因到因子，convex → 可优化，对 serial correlation 敏感。暂缓理由：3-4 月开发期样本不足估计 maximum drawdown 尾部分布 + 3-5 策略下 avg_corr 阈值法判别力足够 + 优先级低于 CDaR（coherent measure）。与 §4.14 CDaR 互补（CDaR 组合优化 / CED 线性归因），§6.24 待裁定（P3 远期）
- [x] ⑳ Schmitt RWC Conformal Risk Control（§4.17 补充·非原始讨论要点）→ Schmitt 2026-02（Oxford, arXiv:2602.03903）Regime-Weighted Conformal Risk Control：用指数时间衰减 + regime 相似性权重校准 VaR 安全缓冲，model-agnostic wrap 任意 quantile 预测器，weighted exchangeability 下有限样本覆盖保证。TWC 是 drift 下强默认，RWC 增加 regime 加权改善 regime-conditional 稳定性。与 §6.21 Conformal Kelly 正交互补（Kelly 管 leverage，RWC 管 VaR buffer），RWC 更直接作用于 §3.10 drawdown_controller 的 C 层 VaR 输入。暂缓理由：依赖 conformal 预测层（[36_var_es_monitoring](36_var_es_monitoring.md) 当前用参数法无 conformal 基础设施）+ regime 特征工程需定义"regime 距离"+ calibration set 样本不足。§6.25 待裁定（P2，最小集成路径：先 TWC 验证稳定后再加 RWC）
- [x] ㉑ 回撤状态滞后-恢复双阈值 Hysteresis 算法（§3.20 补充·非原始讨论要点）→ §3.11 状态机有升级触发条件但**无降级恢复条件**，临界态 thrashing 风险（触发→恢复→再触发反复震荡）。§3.20 补齐 hysteresis 双阈值（恢复阈值 = 触发阈值 × 50% 半阈值）+ min_hold 持续时间门控（WARN 5 日 / DANGER 10 日 / CRISIS 20 日 / RECOVERY 阶梯 5 日）+ 毕业准则（连续 ≥3 盈利日 + 10 笔期望 ≥ 0.3R + 合规率 ≥ 80% + 单笔最大亏损 ≤ 1.2R）。对齐 [37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md) §3.6（v1.0.3）流动性危机恢复算法的设计模式。行业印证：r1000-quant-engine 3% 净值回升 buffer、dredyson 0.5 std gap 减少 70% 假转换、Actura 8 cycles cooldown、BloFin/JournalPlus/fazencapital 分阶段恢复毕业准则。§3.11 状态机转换表已同步更新恢复条件列。§6.26 待裁定（P0 最小补丁：DrawdownController 增加半阈值 + min_hold + 连续 3 盈利日单项；完整 4 项毕业准则待 §6.6 DrawdownStateMachine 落地）
- [x] ㉒ BOCD 概率 Kill Switch（§4.18 补充·非原始讨论要点）→ Adams & MacKay 2007（arXiv:0710.3742）Bayesian Online Changepoint Detection 维护 run-length 后验 `P(r_t | x_{1:t})`，输出 `P(changepoint) = P(r_t=0)` **连续概率**而非二元判断。mathandmarkets 2026-02 + quantbeckman 2025-11 工程化方案：N-IG 共轭先验 + Student-t 似然（重尾适配 A 股）+ 双触发（P>0.8 硬停机对齐 §3.5 Kill Switch / P>0.5 持续 5 日减仓 50% 对齐 §3.4 recovery_factor）+ log-space 数值稳定 + state-space pruning。是 §4.8 CUSUM/Hawkes/Lee-Mykland 三检测器的**概率化统一演进**——CUSUM 需指定 μ₀（选择困境：全回测均值含待检测衰减，短窗敏感于窗口选择）+ 二元阈值（不够灵活），BOCD 无需 μ₀（run-length 后验自适应估计）+ 概率输出可分级响应（P>0.5 减仓 30% / P>0.7 减仓 60% / P>0.9 硬停机）。暂缓理由：计算复杂度 O(t) 需 pruning + 个人系统样本短（≥200 交易日）+ 与 §4.8 同期暂缓 + 似然模型选择额外复杂度 + 与 §3.5 固定阈值 Kill Switch 职责重叠。§6.27 待裁定（P3，与 §6.10 CUSUM/Hawkes/Lee-Mykland 同步重评，最小集成路径：先单策略试运行 BOCD 输出 P(changepoint) 仅供参考不触发，验证检测有效性后再接入双触发系统）
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
> v1.38.0 注：本表仅列核心 6 模块；全量已施工/未施工设施（含 Kill Switch 三实现域分离、支撑设施、注册表缺口）见 §2.4 已施工设施盘点。

| 模块 | ID | 路径 | 职责 |
|---|---|---|---|
| DrawdownTracker | MOD-RK-011 | `src/zephyr/risk/core/drawdown_tracker.py` | L1 监控告警 5/10/15% |
| CapitalCurveManager | MOD-POS-007 | `src/zephyr/position/core/capital_curve_manager.py` | L2 仓位节流 5/10/15%+ 四级上限 |
| DrawdownController | MOD-POS-008 | `src/zephyr/position/core/drawdown_controller.py` | L3 综合响应（VaR+策略+黑天鹅） |
| stop_loss | MOD-L04-001 | `src/zephyr/risk/stop_loss.py` | Kill Switch 执行入口 |
| DefaultRiskValidator | — | `src/zephyr/risk/implementations/default_risk_validator.py` | Kill Switch 状态管理 |
| DailyAuditor | MOD-RK-20 | `src/zephyr/risk/core/daily_auditor.py` | 日终检查（含 Kill Switch 状态） |

### 8.3 行业参考（2026-08 搜索）
- [TradeZella: Drawdown Management](https://www.tradezella.com/blog/drawdown-management)（2026-04，三级协议 + 恢复 ramp 25%→50%→75%→full）
- [CompleteTradersEdge: Drawdown Protocol](https://completetradersedge.com/drawdown-protocol-traders/)（2026-04，Green/Amber/Red 三级 + ARKA recovery re-authorization）
- [algostrategyanalyzer: Drawdown Guide](https://algostrategyanalyzer.com/en/blog/drawdown-trading-guide/)（2026-01，DD=(Peak-Trough)/Peak + Kill Switch protocol）
- [go-trader #25: portfolio kill switch](https://github.com/richkuo/go-trader/issues/25)（2026-03，aggregate drawdown limit + manual reset + audit log）
- [algotradingdesk: Kill Switch in HFT](https://algotradingdesk.com/kill-switch-mechanisms-hft-risk-control/)（2026-03，Knight Capital 案例 + SEC Rule 15c3-5）
- [Punch: Kill Switch](https://builderslab.punch.trade/help/articles/1440242-use-kill-switch-to-lock-trading-on-punch-desktop)（2026，"cannot turn it off early" 不可覆盖原则）
- [ai-trading-system: hardened_risk_engine](https://github.com/ballales1984-wq/ai-trading-system/blob/main/app/risk/hardened_risk_engine.py)（2026-03，RiskLevel 5 级 + CircuitBreaker + KillSwitch 三件套同构）
- [nexusfi: Automated Risk Controls](https://nexusfi.com/a/automation/automated-risk-controls)（2026-06，5 态风险状态机 NORMAL/WARN/KILL/SAFE + 取最严原则 + 三层防线编排）
- [completetradersedge: Advanced Drawdown Management](https://completetradersedge.com/advanced-drawdown-management/)（2026-05，统计性 vs 行为性回撤 5 问诊断矩阵 + 连败期望表）
- [MetricGate: CPPI](https://metricgate.com/docs/constant-proportion-portfolio-insurance/)（2026-06，CPPI cushion 机制 + cash-lock 风险）
- [IR-Tracker: Drawdown Management](https://www.ir-tracker.com/en/columns/advanced-strategy/drawdown-management)（2026-02，Ulcer Index + CPPI + vol targeting + drawdown budget）
- [systemtrade.blog: Adaptive Drawdown Recovery](https://systemtrade.blog/posts/adaptive_drawdown_recovery)（2026-04，3 段软止损状态机 + 阶梯 lot_multiplier）
- [nexusfi: Automated Trading Emergency Protocols](https://nexusfi.com/a/automation/automated-trading-emergency-protocols)（2026-06-01，4 层 Kill Switch 架构 code/platform/broker/exchange + Ghost Position 问题 + Dead Man's Switch 外部看门狗 + @Breukelen 2022 CME 拒单案例）
- [nexusfi: Drawdown Recovery Mathematics](https://nexusfi.com/a/risk-management/drawdown-recovery-mathematics)（2026-06-01，回撤恢复非对称数学表：Required Recovery Gain = Loss/(1-Loss)，20%→25% / 30%→42.9% / 50%→100% / 75%→300%，20-25% 是恢复难度指数级恶化的临界点，§2.1 项目处境恢复表直接依据）
- [invistaja: Time in Drawdown](https://invistaja.app.br/time-in-drawdown-algotrading/)（2026-08-02，TiD Kill Switch `T_kill = MaxDDD_OOS × 1.5` + Rej-Seager-Bouchaud 2017 理论：回撤持续时间随 Sharpe 平方下降）
- [Tugbars/Finance-Kill-Switch](https://github.com/Tugbars/Finance-Kill-Switch)（2025-11，CUSUM 均值漂移检测 + Hawkes 自激励过程亏损聚集 + Lee-Mykland 跳跃检验，统计检测替代阈值触发）
- [arxiv 2511.13251: Sharpe-Driven Chinese A-Share Portfolio](https://arxiv.org/pdf/2511.13251)（2026，A 股实证：drawdown >2%→80% cap / 4-6%→40% cap / >6%→0+1 天冷却，分级阈值比本项目更紧）
- [Rej, Seager & Bouchaud (2017): You are in a drawdown. When should you start worrying?](https://arxiv.org/abs/1707.01457)（物理金融学派，drawdown 深度与 Sharpe 反比、持续时间与 Sharpe 平方反比的理论基础）
- [tradingwyckoff: Drawdown Complete Guide](https://www.tradingwyckoff.com/en/algorithmic-trading/drawdown-trading-guide/)（2026-01，3 类 drawdown + Ulcer Index + Pain Index 水下面积 + Kill Switch protocol + intraday vs close-to-close 区分）
- [PropGuard TradeShield Protocol](https://github.com/youcefbibo53/PropGuard-Trailing-Equity-Armor/)（2026-08-08，prop firm 多层 drawdown 防御：静态（初始本金基准）+ trailing（peak 基准）双模式 + Daily Loss Limit + 硬 circuit-breaker）
- [orstac: Avoid Over-Leveraging](https://orstac.com/ways-to-avoid-over-leveraging-in-trading-3/)（2026-03，soft circuit breaker（win rate<30%→减仓）+ hard circuit breaker（daily DD>5%→24h halt）+ correlation-aware portfolio leverage 净暴露计算）
- [csdn: 2026 量化新规实盘交易重构](https://blog.csdn.net/syp1110/article/details/163276625)（2026-08-08，A 股程序化交易新规：每秒15笔/撤单率15%/50微秒停留 + TWAP/VWAP 拆单标配 + Kelly+风险平价头寸管理）
- [csdn: 期货量化风控实战](https://blog.csdn.net/lisiccwss/article/details/160660741)（2026-08-08，仓位/止损/熔断三层联动 + 状态机防自动恢复重复风险 + 风控与策略分离审计）
- [marketclutch: Circuit Breakers in Algorithmic Trading](https://marketclutch.com/structural-safeguards-navigating-circuit-breakers-in-algorithmic-trading/)（2026，LULD 价格带 + MWCB 三级 7/13/20% + Pre-Halt Liquidation + 内部系统 circuit breaker 与交易所级分层）
- [López de Prado & Fabozzi: Rethinking Portfolio Risk (JAM 2026)](https://quantresearch.org/Publications.htm)（2026，六类风险失败机制 taxonomy：statistical/factor/liquidity/model/governance/decision-infrastructure vulnerabilities，严重损失来自复合效应而非单一波动率，§3.16 扩展归因维度依据）
- [marketmaker.cc: When Does HRP Beat Markowitz?](https://marketmaker.cc/en/research/)（2026，4800 次实验验证 HRP 层次聚类在 T/N 低、结构化协方差下优于 Markowitz/1/N/inverse-var，§4.11 HRP 聚类归因依据；同站 PBO/CSCV/DSR/WFO/Bootstrap 系列研究覆盖回测过拟合检测全链路）
- [nadcab: Trading Bot Risk Management](https://www.nadcab.com/blog/trading-bot-risk-management-stop-loss-position-sizing-drawdown-control)（2026-01-14，Kill Switch 必须独立于主交易逻辑 + 多层实现 software/platform/manual + MAE 止损分析 + equity curve trading 仓位缩放 + portfolio-level correlation 风险聚合）
- [signalbots: AI Signals as Risk Safety Net](https://signalbots.ai/blog/forex-risk-management-with-ai-signals)（2026-08-04，回撤恢复非对称数学表 + risk per trade 1% + daily loss cap + correlation limits + 60 秒 pre-trade checklist，§2.1 恢复表 + §3.6 日度熔断行业印证）
- [arXiv:2303.02613: Drawdown Modulation with Restart Mechanism](https://arxiv.org/abs/2303.02613)（Hsieh 2023，drawdown modulation policy 保证最大回撤 ≤ 预设限 a.s.，但当 drawdown 逼近预设限时策略退化为 stop-loss order 错失后续盈利机会；新增 data-driven restart mechanism 在 drawdown 接近限值时重启交易策略以自动调优，含 ETF/加密货币实证支持。**与本项目 §3.11 RECOVERY 态关联**：restart mechanism 为"KILL→RECOVERY 阶梯恢复"提供理论支撑——modulation 接近限值时不应纯 stop-loss 而应带 restart 逻辑，35 号的 recovery_factor 0.25→0.50→0.75 阶梯正是 restart 的工程化实现）
- [Nystrup, Boyd, Lindström & Madsen: Multi-Period Portfolio Selection with Drawdown Control (Annals of Operations Research 2019)](https://backend.orbit.dtu.dk/ws/files/149812772/Multi_Period_Portfolio_Selection_with_Drawdown_Control.pdf)（Stanford/Boyd + DTU，MPC 动态优化投资组合控制回撤，核心创新"根据已实现回撤调整风险厌恶系数"——连续 risk aversion γ(dd) 替代离散阈值；多变量 HMM 预测多期收益均值/协方差；交易/持仓成本作为估计误差正则化；杠杆可提高收益不增 MaxDD。**与本项目 §4.12 关联**：MPC 连续风险厌恶是当前 5/10/15% 离散阈值的远期演进方向，recovery_factor 0.25→0.50→0.75 阶梯是其离散近似）
- [arXiv:2604.00415: Dynamic Weight Optimization for Double Linear Policy — A Stochastic MPC Approach](https://arxiv.org/html/2604.00415v1)（Tan & Hsieh, NTHU, 2026-04，DLP-SMPC 随机 MPC 优化 Double Linear Policy 动态权重，receding-horizon + survivability + RPE 约束。TSLA MaxDD 12.17% vs Buy-and-Hold 73.63%，Sharpe 1.42 vs 1.03；ETH MaxDD 10.18% vs 79.35%。**与本项目 §4.12 关联**：MPC 用于回撤控制的 2026 实证，验证 Nystrup/Boyd 范式在单资产上的有效性）
- [arXiv:2607.00883: Tail Risk Management with Puts and Trend Following — A CVaR Framework for Crashes and Drawdowns](https://arxiv.org/html/2607.00883v1)（Noguer i Alonso & Al-Fallouji, AIFI/Mirabaud, 2026-07-01，连续时间 CVaR 框架，将 OTM 看跌期权 + 系统化趋势跟踪放入一个连贯尾部风险 mandate。**时间分离核心洞察**：凸性保险在跳跃冲击时立即重新定价；趋势跟踪在首次冲击时滞后（信号须穿过零），但在持续回撤中越来越防御性，无需新期权费。四轴诊断层：条件凸性 / 尾部事件可靠性 / 非压力 carry / 回撤持续性。CVaR 策略梯度恒等式。**与本项目 §4.13 关联**：A 股不能做空+无期权，但"趋势跟踪作为持续回撤防御"思路可借鉴——回撤 Protocol 可叠加趋势跟踪信号作为动态防御层）
- [arXiv:2605.25311: Recursive Multi-Agent Trading System (RMATS)](https://arxiv.org/abs/2605.25311)（Yang et al., Washington University, 2026-05，4 agent（Sentiment/Report/Analysis/Risk）+ 递归 Manager Agent，typed message passing + 收敛保证。561 交易日 MaxDD 9.62%（vs MVO 15.49% / FinBERT 15.28%），5 个地缘政治压力场景中 3 个事件期回撤最低。Risk Agent 用 CVaR+EWMA+多级 circuit breaker（DD/GRS/vol 三源 OR），RL 目标 `R_t = r_t − λ₁σ_t − λ₂max(0, DD_t − θ)`（λ₁=0.8, λ₂=1.5 重罚回撤）。**与本项目 §4.15 关联**：多 agent 协作回撤控制范式，个人项目拒绝照搬架构，仅借鉴 Risk Agent 独立性 + 多源 circuit breaker 思路）
- [arXiv:2510.10807: Multi-Agent Regime-Conditioned Diffusion (MARCD) for CVaR-Constrained Portfolio Decisions](https://arxiv.org/html/2510.10807v3)（Alzahrani, 2025-11 v3 2026，Gaussian HMM regime + diffusion 生成场景 + CVaR epigraph QP 分配器，tail-weighted diffusion loss + regime-MoE denoiser。2020-2025 OOS MaxDD 9.3% vs BL 14.1%（降 34%）。**与本项目 §4.15 关联**：多 agent + 生成式建模的回撤控制，过度工程不采纳）
- [Uryasev & Ding: Drawdown Beta and Portfolio Optimization (Stony Brook)](https://uryasev.ams.stonybrook.edu/wp-content/uploads/2021/10/Drawdown_Portfolio_Optimization_Problems_and_Drawdown_Betas.pdf)（引入 ERoD（Expected Regret of Drawdown）并证明与 CDaR（Conditional Drawdown-at-Risk）优化等价。CDaR = drawdown 序列的 CVaR，path-dependent coherent risk measure。ERoD Beta = 市场回撤时证券的平均损失比率，负 ERoD Beta 识别"市场回撤时正收益"的证券。**与本项目 §4.14 关联**：CDaR 是回撤深度的连续度量，优于 MaxDD（单点非 coherent），LP 可解）
- [MetricGate: Conditional Drawdown-at-Risk (CDaR)](https://metricgate.com/docs/conditional-drawdown-at-risk/)（2026-06-09，CDaR 是 coherent risk measure（monotonicity/sub-additivity/positive homogeneity/translation invariance），α→0 收敛 MaxDD，α→1 收敛 average DD，可作凸优化目标。"CDaR is far more stable than maximum drawdown yet still concentrated on the genuinely painful losses rather than diluted by long quiet stretches near the peak"。**与本项目 §4.14 关联**：CDaR 性质论证，支撑其作为回撤深度连续度量的优越性）
- [Man Numeric: CVaR Insights (Joshua Levin, 2025-07)](https://www.man.com/man-numeric-cvar-insights)（方差作为风险度量的根本缺陷：无法区分"平稳上涨"vs"暴涨暴跌"组合（同等方差但回撤特性天壤之别）。CVaR 优于方差：显式度量不利结果，Portfolio One CVaR₀.₄=−1.32% vs Portfolio Two CVaR₀.₄=−1.78%。CVaR 用于组合具有互补左尾特性的回报流配置。**与本项目 §4.14 关联**：CVaR 优于方差的论证同样适用于 CDaR 优于 MaxDD——CDaR 把 CVaR 思路应用到 drawdown 序列）
- [arXiv:2605.16895: The Alpha Illusion — Reported Alpha from LLM Trading Agents Should Not Be Treated as Deployment Evidence](https://arxiv.org/html/2605.16895v1)（Ye et al., Fudan/Imperial College, 2026-05，LLM/多 agent 报告的 alpha 在通过 temporal integrity / real-world frictions / counterfactual robustness / predictive calibration / numerical execution / multi-agent disaggregation 等结构有效性测试前，不应作部署证据。提出 P1-P6 最低报告协议 + 模块化替代方案（LLM 作可审计信息接口，上游独立校准/风控/执行模块）。**与本项目 §4.15 关联**：支撑"多 agent 架构过度工程"判断——LLM agent 的 alpha 报告需打折看待，个人项目不应照搬）
- [philippdubach: Long Volatility Premium (One River / Causley)](https://philippdubach.com/posts/long-volatility-premium/)（2026-02-14，AQR 实证 puts 与 trend-following 互补：puts 在 COVID 突然崩盘赢（+42%），trend-following 在 dot-com 持续熊市赢——两者时间分离互补。One River 40 年数据：beta-neutral long volatility factor 改善总回报同时降低回撤。**与本项目 §4.13 关联**：实证"趋势跟踪在持续回撤中防御"的有效性，支撑 Noguer 论文的时间分离洞察）
- [Helios: 9 Ways to Reduce Drawdowns in Portfolios](https://heliosdriven.com/helios-insights/reduce-drawdowns-portfolios)（2026-05-01，系统化回撤控制框架：诊断（attribution）→ 资产配置 → 集中度限制 → 流动性规划 → rebalance → 防御性敞口 → 对冲纪律 → 决策指标。S&P Dow Jones 2025 美股日内波动率 1.18%（vs 2024 的 0.91%）。**与本项目 §3.16 关联**：回撤归因的系统性框架印证本项目归因流程的设计方向）
- [arXiv:2604.09060: AEGIS Volatility-Gated Momentum](https://trendsandbreakouts.com/volatility-gated-momentum-aegis-framework)（Chakraborty & Singh, 2026-04，Volatility-Adjusted Momentum（VAM = R_i/σ_i）+ minimax correlation filter，20 年 walk-forward CAGR 15.41% / MaxDD 28.89%。2008 年 S&P -50% / 标准动量 -42.58% / AEGIS -20.94%（MaxDD 28%）。**与本项目 §3.16 关联**：波动率门控 + 相关性结构防御，与归因中"avg_corr > 0.7 = 系统性"呼应，但 AEGIS 用 minimax 主动选择低相关资产）
- [Goldberg & Mahmoud: Conditional Expected Drawdown (Mathematical and Financial Economics 2016, DOI 10.1007/s11579-016-0181-9)](https://alexandria.unisg.ch/server/api/core/bitstreams/f53d98e4-3cfb-4517-8054-8287a2912bc8/content)（UC Berkeley + St. Gallen，CED = maximum drawdown 分布的尾部均值，degree one positive homogenous risk measure → Euler 定理线性因子归因，convex → 可优化，deviation measure（Rockafellar et al. 2002/2006）。AR(1) 实证 CED 对 serial correlation 敏感性远高于 ES/volatility。**与本项目 §4.16 关联**：CED 的"positive homogeneity → Euler 线性归因 + serial correlation 敏感性"填补 §3.16 回撤归因的"线性因子归因"空白，与 §4.14 CDaR 互补——CDaR 用于组合优化（LP），CED 用于线性归因（Euler 分解））
- [arxiv 1404.7493v3: Minimum CED Optimization](https://arxiv.org/pdf/1404.7493v3)（提供 minimum CED 优化的高效线性规划算法 + CED/ES/volatility 风险归因差异实证。**与本项目 §4.16 关联**：CED 优化的 LP 算法实现参考）
- [internQuant/conditional-drawdown (GitHub)](https://github.com/internQuant/conditional-drawdown)（Python 实现：CED + MDD + Rolling MDD + Portfolio Risk Attribution。**与本项目 §4.16 关联**：CED 归因的工程实现参考，策略数扩展后可直接借鉴）
- [edgeflo: De-Risk After Drawdown](https://www.edgeflo.com/blog/de-risk-after-drawdown)（2026-03，0.5% Recovery Protocol：连续 2 笔亏损后 risk_per_trade 从 1% 降至 0.5%，单笔 3R 盈利回补 +1.5% 覆盖 2 笔 0.5% 亏损。仓位上限恢复（recovery_factor）+ 单笔风险恢复（risk_per_trade）正交双保险，§6.20 待裁定依据）
- [arXiv:2608.01494: Conformal Kelly Drawdown Dial](https://arxiv.org/html/2608.01494v1)（2026-08-02，conformal 预测区间下行连续 miss 超历史率→缩减 leverage，开发窗口 MaxDD 27.7%→20.3%，Sharpe 提升，rank-based p=0.024。核心设计原则：slow unweighted per-asset rolling quantile 优于 adaptive 方法（宽度稳定性 > 局部锐度）。§6.21 Conformal Kelly 待裁定依据）
- [arXiv:2608.00127: Drawdown Risk Beyond Brownian Motion](https://arxiv.org/abs/2608.00127)（Landolfi 2026-07-31，给定 Sharpe + 收益统计结构生成 4 度量查表（MaxDD/最大损失/末尾负时间/最长恢复时间）。核心发现：① Gaussian 表在非正态下误警；② 持续性下回撤"放大"是 T^(H-1/2) dispersion scaling 即 √T 校准失效。§6.23 Non-Gaussian Drawdown Lookup Tables 待裁定依据，警示 [36_var_es_monitoring](36_var_es_monitoring.md) §3.2 参数法 VaR 的 √T 时间缩放在持续性下失效）
- [arXiv:2602.03903: Conformal Risk Control for Nonstationary Portfolio VaR](https://arxiv.org/pdf/2602.03903)（Schmitt 2026-02, Oxford，Regime-Weighted Conformal Risk Control（RWC）：指数时间衰减 + regime 相似性权重校准 VaR 安全缓冲，model-agnostic wrap 任意 quantile 预测器，weighted exchangeability 下有限样本覆盖保证。TWC 是 drift 下强默认，RWC 增加 regime 加权改善 regime-conditional 稳定性。CRSP 美股组合实证。§4.17 Schmitt RWC + §6.25 待裁定依据，与 §6.21 Conformal Kelly 正交互补（Kelly 管 leverage，RWC 管 VaR buffer））
- [arXiv:2608.04305: CVaR Risk-Aware Q-Learning](https://arxiv.org/abs/2608.04305)（Wu/Lei/Huang 2026-08-05, ICAIF '26 Milan，自适应有限预算训练 CVaR 风险感知 Q-learning（RaQL）：per-cell inner-step sizing + outer-rate-matched decay + coverage-first sample allocation，CVaR Bellman 残差降 85%，BTC 日度交易 Sharpe 0.93 / MaxDD 6.46%。§3.19 远期演进登记，归入 §4.15 多 agent 拒绝的"借鉴范围"——CVaR 目标函数思路已由 §3.9 乘性叠加承载）
- [r1000-quant-engine Phase 6a](https://github.com/wscha231/r1000-quant-engine/blob/master/PHASE_ROADMAP.md)（2026-04，3 级 drawdown circuit breaker 阈值 −8%/−15%/−25% → cash floors 15%/35%/60%，equity-based recovery hysteresis `dd_trigger_equity * (1 + 0.03)`——净值须从触发点回升 3% 才解除 circuit breaker。§3.20 hysteresis 恢复算法行业印证）
- [dredyson: State Machines in Algorithmic Trading](https://dredyson.com/the-hidden-truth-about-state-machines-in-algorithmic-trading-systems-)（2026-05，状态机进入阈值 2.0 std、退出阈值 1.5 std，0.5 gap 减少 70% 的假状态转换；cooldown timer 是额外安全网。§3.20 hysteresis gap + min_hold 行业印证）
- [Actura GACR Agent Whitepaper](https://github.com/othnielObasi/actura-gacr-agent/blob/main/WHITEPAPER.md)（2026-04，drawdown > 6% 锁定 EXTREME_DEFENSIVE，profile 切换间至少 8 cycles cooldown。§3.20 min_hold 持续时间门控行业印证）
- [BloFin: Handling Drawdowns](https://blofin.com/en/academy/education/handling-drawdowns)（2026-05，三阶段恢复 Phase 1 半仓 / Phase 2 微仓 / Phase 3 正常，Phase 2 graduation criterion 近 10 笔交易平均期望 ≥ +0.3R + 规则合规率 ≥ 80% 行为性检测。"Advance only when objective criteria are met. Return to the previous phase if drawdown exceeds the phase limit." §3.20 毕业准则依据）
- [JournalPlus: Trading After a Drawdown Guide](https://journalplus.co/learn/guides/trading-after-a-drawdown-guide/)（2026-05，4 阶段恢复框架：半仓规则 → 诊断 → 48-72h 休息 → scale-up 准则。§3.20 毕业准则依据）
- [fazencapital: Trading Drawdown Recovery Math Methods Guide](https://fazencapital.com/learn/en/trading-drawdown-recovery-math-methods-guide)（2026-05，2026-08-04 复审，30 天 reset protocol + 回撤恢复数学方法。§3.20 毕业准则依据）
- [Adams & MacKay: Bayesian Online Changepoint Detection (arXiv:0710.3742)](https://arxiv.org/abs/0710.3742)（2007，剑桥，BOCD 原始论文——run-length 后验递推 + hazard function + predictive probability，在线变点检测的概率框架奠基。§4.18 BOCD 概率 Kill Switch 算法依据）
- [mathandmarkets: CUSUM, Bayes, and the Art of Knowing When to Quit](https://mathandmarkets.com/p/detecting-decay-in-real-time-when)（2026-02-22，CUSUM + Page-Hinkley + Rolling Sharpe + Bayesian BOCD 四检测器对比框架，策略衰减检测完整工具箱 + 参数校准实践 k=0.5σ/h=4σ/hazard=1/50~1/100。§4.18 BOCD 工程化参考）
- [quantbeckman: Switch-Off — Bayesian online changepoint detection](https://www.quantbeckman.com/p/with-code-switch-off-bayesian-online)（2025-11-17，probabilistic kill switch 工程实现：N-IG 共轭先验 + Student-t 似然重尾适配 + 双触发系统 P>0.8 硬停机/P>0.5 持续 N 日减仓 + log-space 数值稳定 + state-space pruning。§4.18 BOCD 双触发系统 + 数值稳定方案依据）
- [Bank of England: AI Contingency Planning & Market-Wide Kill Switches](https://hotminute.co.uk/2026/07/05/kill-switches-for-the-stock-market-inside-the-bank-of-englands-ai-contingency-planning/)（2026-07-05，Breeden 副行长 ECB Sintra Forum 2026-06-30 演讲：AI agent herding 是核心风险非单一 agent 失控 + BoE/BIS Innovation Hub/Bundesbank 联合多轮压力模拟 + 探索市场级 kill switch + objective functions 纳入公共政策目标 + "human-in-the-loop for every action unrealistic" + FPC 2026-07-07 AI 金融稳定评估。§3.5 全球监管趋势 ① 多 agent 协作风控 + ③ 事后审计依据）
- [SEBI: Algorithmic Trading Framework 2026](https://clearyourexam.com/current-affairs/sebi-new-framework-algorithmic-trading-enhanced-corporate-governance)（2026-05，强制 Kill Switch 与主交易逻辑物理隔离 + 算法报备 + 实时监控 + 增强公司治理。§3.5 全球监管趋势 ② 独立 Kill Switch 物理隔离依据，验证 `stop_loss` 独立于 `drawdown_controller` 的架构合规性）
- [guorn: 量化投资中的回撤择时——分析与优化](https://guorn.com/forum/post/p.200941.361906578502334)（2026-04-20，A 股 1992-2006 历史数据回撤择时实证：① 倒 U 形最优区间——回撤阈值过浅 thrashing/过深滞后，存在与策略波动率匹配的最优区间；② vol-matched stop——止损阈值应与策略自身波动率匹配而非统一固定数值；③ 历史涨幅动态防御仓位——DEFENSIVE 态仓位按 pre-drawdown 涨幅动态调整（>100%→0.3/>50%→0.5/否则 0.6）+ confirm_days 缓冲器防假修复 + 离散化 TIPP 思路。§6.28 波动率匹配阈值 + 历史涨幅动态防御仓位依据）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G16 讨论要点占位，待讨论填空 |
| 2026-08-10 | 1.0.0 | 骨架→active：回填全部 8 项讨论要点 + 三层分离裁决 + 阈值分裂处理 + 2026-08 行业搜索印证 | 框架（§2.5）与代码（三套阈值体系）分裂裁决：承认三层互补，代码 5/10/15% 更紧作为内层早预警，§2.5.1 的 8/15/20/25% 作为外层生存边界；Kill Switch 不可覆盖已由代码 `requires_manual_reset` 实现；强制休息 5 天自动计时暂缓（人工复位=天然冷却） |
| 2026-08-10 | 1.1.0 | 补充施工流程算法（§3.10 日度风控循环伪代码）+ 恢复状态机形式化（§3.11 5 态状态转换图 + 代码差距）+ 回撤类型诊断（§3.12 统计性 vs 行为性 5 问矩阵）+ CPPI 拒绝方案（§4.5）+ Ulcer Index 暂缓（§4.6）+ §6.5-6.8 待裁定 4 项 + 6 篇 2026 行业参考 | 持续改进：对照 40 号施工流程算法格式发现 35 号缺失日度编排伪代码；nexusfi 5 态状态机揭示代码无持久化状态机差距；completetradersedge 诊断矩阵填补"回撤类型不区分"空白；CPPI 作为选项之外算法评估后拒绝（cash-lock + A 股 gap risk） |
| 2026-08-10 | 1.2.0 | 补充 Kill Switch 执行失败兜底（§3.5.1 4 层架构 + Ghost Position 检测伪代码）+ 盘中实时风控循环（§3.13 30 秒轮询 + A 股 T+1 约束）+ Kill Switch 复位端到端流程（§3.14 KILL→RECOVERY→NORMAL 阶梯 + 恢复期回撤保护）+ TiD Kill Switch 暂缓（§4.7 时间维度不可逆停机）+ CUSUM/Hawkes/Lee-Mykland 统计检测暂缓（§4.8）+ §6.9-6.11 待裁定 3 项 + 5 篇 2026 行业参考 | 持续改进：2026-08 全网搜索发现 nexusfi 4 层 Kill Switch 架构揭示当前仅 L1/L4 两层、Ghost Position 风险；invistaja TiD Kill Switch（Bouchaud 理论）作为选项之外算法评估后暂缓（不可逆过激 + 依赖 OOS 回测）；Tugbars CUSUM/Hawkes 统计检测作为阈值触发升级评估后暂缓（复杂度高 + 样本短）；施工流程算法补齐盘中循环 + 复位端到端两块缺失 |
| 2026-08-10 | 1.3.0 | 补充盘前初始化与跨重启状态恢复（§3.15 4 阶段流程：Ghost 核对→状态机加载→基线校准→通道健康）+ 回撤归因端到端流程（§3.16 相关性归因+因子归因+regime 交叉验证）+ 施工流程总览（§3.17 5 流程闭环时序图）+ A 股 2026 新规对 Kill Switch 执行影响（§3.5.1 每秒15笔/撤单率15% 分批拆单）+ Pain Index 暂缓（§4.9 水下面积，与 UI 同类择一）+ TradeShield static 模式部分采纳（§4.10 initial×0.85 破产底线）+ §6 待裁定加优先级列（P0-P3）+ §6.12-6.15 新增 4 项待裁定 + §7 ⑨-⑫ 新增对齐 + 6 篇 2026-08 行业参考 | 持续改进：复审发现施工流程缺"系统启动环节"（盘前初始化）与"归因环节"两块缺失，nexusfi Reconnection/State Recovery 章节揭示跨重启状态丢失风险；orstac correlation-aware 视角填补归因判别维度；A 股 2026-08-08 新规（csdn 实证）揭示 Kill Switch 平仓需分批拆单；Pain Index（tradingwyckoff）与 TradeShield 双模式（PropGuard 2026-08-08）作为选项之外算法评估；§6 加优先级列便于施工排序 |
| 2026-08-10 | 1.4.0 | 补充盘后状态持久化流程（§3.18 5 阶段：终态净值→peak NAV→状态机→nav_history→原子提交标记，§3.15 盘前加载的配对保存）+ §3.17 总览升级 5→6 流程闭环（时序图纳入 §3.18）+ §6.12 升级为"盘前初始化+盘后持久化配对"（P0）+ §7 ⑬ 新增对齐 + nexusfi 回撤恢复数学表引用（§8.3，§2.1 恢复表依据） | 持续改进：再次审查发现 §3.15 盘前"加载状态"缺配对的"盘后保存状态"——持久化与恢复是配对操作（nexusfi Reconnection/State Recovery），缺一即状态机失效；§3.18 填补"盘后保存"缺口，与 §3.15 形成 save/load 闭环；nexusfi 回撤恢复数学表（Loss/(1-Loss) 非对称）为 §2.1"20% 回撤需 25% 收益恢复"提供精确公式依据 |
| 2026-08-10 | 1.5.0 | 修正 §3.17 总览正文"8 个流程"→"8 章节（6 独立流程环节 + 2 横切机制）"逻辑矛盾 + §3.16 补充 López de Prado 2026 JAM 六类风险失败机制扩展归因维度（statistical/factor/liquidity/model/governance/decision-infrastructure，当前覆盖 ①③④⑤、待施工 ②⑥）+ §4.11 HRP 层次聚类归因暂缓（策略数 ≥8 后引入，识别"部分系统性"策略簇）+ §6.16 新增待裁定（P3）+ §7 ⑭ 新增对齐 + 5 篇 2026 行业参考（López de Prado JAM 2026 / marketmaker.cc HRP / nadcab Kill Switch / signalbots / arXiv drawdown modulation restart） | 持续改进：再次审查发现 §3.17 标题"6 流程闭环"与正文"8 个流程"矛盾——实为 8 章节 6 流程环节 + 2 横切机制（§3.11 状态机/§3.12 诊断）；2026-08 全网搜索发现 López de Prado 2026 JAM "Rethinking Portfolio Risk" 六类失败机制 taxonomy 为回撤归因提供统一框架（当前二分法→六类复合归因）；marketmaker.cc 2026 HRP 4800 次实验验证为"部分系统性"策略簇识别提供聚类工具；arXiv 2303.02613 drawdown modulation restart 为 §3.11 RECOVERY 阶梯提供理论支撑（modulation 接近限值不应纯 stop-loss 而应带 restart 逻辑，recovery_factor 0.25→0.50→0.75 阶梯正是 restart 的工程化实现） |
| 2026-08-10 | 1.6.0 | 补充施工流程算法审查与远期演进方向声明（§3.19 6 流程闭环审查结论 + 2026 学术研究 4 方向登记 + 过度工程红线 4 条 + 回撤预测 vs 前馈风控边界澄清）+ §3.9 补充乘性叠加 vs 加性惩罚选型理由（对比 RMATS RL 目标函数）+ §4.12 MPC 连续风险厌恶调整暂缓（P4，Nystrup/Boyd 2019 + DLP-SMPC 2026）+ §4.13 趋势跟踪回撤防御层暂缓（P4，Noguer i Alonso 2026-07 CVaR 框架 + AQR 实证）+ §4.14 CDaR 回撤深度连续度量暂缓（P2，Chekhlov/Uryasev + Man Numeric CVaR）+ §4.15 多 agent 协作回撤控制拒绝（过度工程，RMATS + MARCD + Alpha Illusion）+ §5.2 演进路径加第四阶段（远期演进方向登记）+ §6.17-6.19 新增 3 项待裁定（P4/P4/P2）+ §7 ⑮-⑱ 新增对齐 + 13 篇 2026 行业参考 | 持续改进：施工流程算法审查发现 6 流程闭环无缺失独立环节，但横切算法（回撤度量/风险厌恶调整/前馈防御）可增强；2026-08 全网搜索发现 4 篇最新学术研究（Nystrup/Boyd MPC 连续风险厌恶 / Noguer CVaR 趋势跟踪 / RMATS 多 agent / Uryasev CDaR）提供"选项之外更好的算法"，但作为远期演进方向登记不直接采纳——个人项目过度工程红线（不引入重模型/A 股约束适配/可解释性优先/借鉴范围限定）决定只借鉴思路不照搬架构；arXiv:2605.16895 The Alpha Illusion 警示 LLM/多 agent alpha 不可作部署证据，支撑拒绝多 agent 架构；Man Numeric CVaR 论证（CVaR 优于方差）+ Uryasev CDaR（drawdown 序列的 CVaR）为回撤深度连续度量提供理论基础，CDaR 优先级高于 UI/PI（coherent + LP 可解）；§3.9 乘性 vs 加性对比填补"为什么选乘性"的推理缺口 |
| 2026-08-10 | 1.7.0 | 补充 Ghost Position 4 层防御架构（§3.5.1 代码层平仓指令验证 + 平台层 broker 硬止损单 + 独立看门狗进程持仓核对 + 人工复位确认，detect_ghost_positions 伪代码）+ A 股 2026 程序化交易新规 Kill Switch 适配（每秒15笔分批平仓 + 撤单率15%监控 + 50μs 报单停留）+ escape 执行器规格（§3.5 LEVEL_3 逃生指令）+ 0.5% Recovery Protocol 待裁定（§6.20 edgeflo 2026-03，单笔风险层面恢复，recovery_factor 仓位恢复 + risk_per_trade 单笔恢复双保险）+ Conformal Kelly drawdown dial 远期演进登记（§3.19 + §6.21，arXiv:2608.01494 2026-08-02，预测区间 miss 驱动 leverage 缩减，MaxDD 27.7%→20.3%）+ Data-Driven Drawdown Restart 远期演进登记（§3.19 + §6.22，arXiv:2303.02613 Hsieh 2023，restart 机制数据驱动重置参数）+ §6.21-6.22 新增 2 项待裁定 | 持续改进：2026-08 全网搜索发现 nexusfi 4 层 Kill Switch 架构揭示 Ghost Position 风险（策略认为已平仓但 broker 仍有持仓）；A 股 2026-08-08 程序化新规（csdn 实证）要求 Kill Switch 平仓分批拆单适配 15 笔/秒 + 15% 撤单率；edgeflo 0.5% Recovery Protocol 填补"仓位恢复 vs 单笔风险恢复"正交维度空白（recovery_factor 是仓位上限恢复，risk_per_trade 是单笔风险恢复，两者乘性叠加=双保险）；arXiv:2608.01494 Conformal Kelly（2026-08-02）提供预测区间 miss 驱动的自适应 leverage 缩减，开发窗口 MaxDD 降 7.4pp；arXiv:2303.02613 drawdown restart 为 §3.11 RECOVERY 阶梯提供"数据驱动参数重置"理论支撑 |
| 2026-08-10 | 1.8.0 | 补充 Non-Gaussian Drawdown Lookup Tables 远期演进登记（§3.19，arXiv:2608.00127，Landolfi 2026-07-31）+ §6.23 新增待裁定（P2）+ CED 线性因子归因暂缓（§4.16 Goldberg & Mahmoud 2016，positive homogeneity → Euler 线性归因 + serial correlation 敏感性，与 §4.14 CDaR 互补：CDaR 组合优化 / CED 线性归因）+ §6.24 新增待裁定（P3）+ §7 ⑲ 新增对齐 + 3 篇行业参考（Goldberg & Mahmoud 2016 / arxiv 1404.7493v3 / internQuant/conditional-drawdown）| 持续改进：2026-08-10 全网搜索发现 arXiv:2608.00127（2026-07-31）"Drawdown Risk Beyond Brownian Motion"——给定 Sharpe + 收益统计结构生成 4 度量查表（MaxDD/最大损失/末尾负时间/最长恢复时间），核心发现：① Gaussian 表在非正态下误警（skew/峰度/波动率聚集使四度量移动方向不同）；② 持续性下回撤"放大"是 T^(H-1/2) dispersion scaling 即 √T 校准失效，非路径几何本征危险。为当前 §3.2 经验阈值（5/10/15%）+ §3.4 recovery_factor 阶梯提供统计校准依据，并警示 [36_var_es_monitoring](36_var_es_monitoring.md) §3.2 参数法 VaR 的 √T 时间缩放在持续性下失效；同时引入 Goldberg & Mahmoud 2016（UC Berkeley + St. Gallen）CED 线性因子归因——positive homogeneity → Euler 定理线性归因 + serial correlation 敏感性填补 §3.16 回撤归因的"线性因子归因"空白，与 §4.14 CDaR（组合优化）互补。两者均作为选项之外更好算法登记，远期待条件满足后引入 |
| 2026-08-10 | 1.9.0 | 补充回撤状态滞后-恢复双阈值 Hysteresis 算法形式化（§3.20：半阈值恢复矩阵 + CUSUM 式恢复算法伪代码 + min_hold 持续时间门控 5/10/20 交易日 + 4 项毕业准则 连续3盈利日/10笔期望≥0.3R/合规率≥80%/单笔≤1.2R + 恢复执行动作表 + 与 §3.11/§3.14/37号对齐说明）+ §3.11 状态机转换表更新恢复条件列（WARN→NORMAL drawdown<2.5%+VaR<2%持续3日+min_hold 5日 等 4 级降级条件）+ §3.19 远期演进表新增 Schmitt RWC + CVaR Risk-Aware Q-Learning 两项登记 + §4.17 Schmitt RWC Conformal Risk Control 暂缓（P2，arXiv:2602.03903 Oxford，regime-weighted conformal VaR 校准，与 §6.21 Conformal Kelly 正交互补）+ §6.25-6.26 新增 2 项待裁定 + §7 ⑳㉑ 新增对齐 + 11 篇行业参考（Schmitt RWC / CVaR Q-Learning / r1000-quant-engine / dredyson / Actura / BloFin / JournalPlus / fazencapital / edgeflo / Conformal Kelly / Landolfi Non-Gaussian） | 持续改进：施工算法完整性审查发现 §3.11 状态机有升级触发条件但**无降级恢复条件**——实盘一旦触发 WARN/drawdown 在 5% 临界波动会反复 thrashing（触发→恢复→再触发），或锁死高级态无法降级错过恢复后盈利机会。§3.20 补齐 hysteresis 双阈值（恢复阈值=触发阈值×50%半阈值）+ min_hold 持续时间门控 + 毕业准则三重守卫，对齐 [37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md) §3.6（v1.0.3）流动性危机恢复算法设计模式；行业印证：r1000-quant-engine 3% 净值回升 buffer + dredyson 0.5 std gap 减少 70% 假转换 + Actura 8 cycles cooldown + BloFin/JournalPlus/fazencapital 分阶段恢复毕业准则。2026-08 全网搜索发现 Schmitt 2026-02（Oxford, arXiv:2602.03903）Regime-Weighted Conformal Risk Control——用指数时间衰减 + regime 相似性权重校准 VaR 安全缓冲，model-agnostic wrap 任意 quantile 预测器，与 §6.21 Conformal Kelly 正交互补（Kelly 管 leverage / RWC 管 VaR buffer），RWC 更直接作用于 §3.10 drawdown_controller 的 C 层 VaR 输入，作为 §4.17 暂缓登记；CVaR Risk-Aware Q-Learning（arXiv:2608.04305）归入 §4.15 多 agent 拒绝的借鉴范围不单独登记。同时补录 v1.7.0/v1.8.0 遗漏的 §8.3 行业参考（edgeflo 0.5% Recovery / Conformal Kelly / Landolfi Non-Gaussian）|
| 2026-08-10 | 1.10.0 | 补充 Conformal Kelly drawdown dial 施工骨架（§3.19：conformal_kelly_drawdown_dial 伪代码——下行 miss 序列 + slow unweighted rolling miss rate + 线性 leverage 缩减 + 0.5 下限防 cash-lock + 与 §3.4 recovery_factor 乘性叠加三层表 position_cap×recovery_factor×conformal_scale + 接口冻结输入 conformal_intervals/输出 leverage_scale∈[0.5,1.0] + 前馈 vs 反馈正交互补说明） | 持续改进：施工算法完整性二次审查发现 §6.21 Conformal Kelly（arXiv:2608.01494）已登记设计原则与重评条件，但**缺可施工形态**——只有"用 per-asset rolling quantile"的定性原则，无 dial 公式/miss 检测/leverage 缩放/与 recovery_factor 集成的伪代码。§3.19 补施工骨架（接口冻结，待 conformal 预测层就绪激活），对齐 §3.20 hysteresis 的"远期登记→施工骨架"演进模式；设计原则严格遵循 arXiv:2608.01494 "slow unweighted 优于 adaptive"核心发现（固定 252 日窗口均值非 locally adaptive 核）；0.5 下限对齐 §4.5 拒绝 CPPI 的 cash-lock 教训；乘性叠加三层表明确"position_cap 状态机/recovery_factor 回撤恢复/conformal_scale 模型失效"各管一件事的正交分工，conformal_scale 是"预测失准即减"的前馈式补 §3.4 recovery_factor"已亏才减"反馈式的盲区 |
| 2026-08-10 | 1.11.0 | 补充 BOCD 概率 Kill Switch（§4.18 Adams & MacKay 2007 arXiv:0710.3742 + mathandmarkets 2026-02 + quantbeckman 2025-11）+ §6.27 新增待裁定（P3）+ §7 ㉒ 新增对齐 + §8.3 补 3 篇行业参考（Adams-MacKay / mathandmarkets / quantbeckman）| 持续改进：用户要求再次审查文档所有内容+施工环节流程算法缺失+选项之外更好算法+2026-08-08 最新研究+文档结构顺序内容调整+持续改进不停。七次审查全网搜索发现 BOCD（Bayesian Online Changepoint Detection）是 §4.8 CUSUM/Hawkes/Lee-Mykland 三检测器的**概率化统一演进**——CUSUM 需指定 μ₀（选择困境：全回测均值含待检测衰减，短窗敏感于窗口选择）+ 二元阈值（不够灵活），BOCD 通过 run-length 后验 P(r_t\|x_{1:t}) 自适应估计 + 连续概率输出 P(changepoint)=P(r_t=0) 解决两大痛点。mathandmarkets 2026-02 提供四检测器对比框架（CUSUM/Page-Hinkley/Rolling Sharpe/BOCD），quantbeckman 2025-11 提供 probabilistic kill switch 工程方案（N-IG 共轭先验+Student-t 似然重尾适配+双触发 P>0.8 硬停机/P>0.5 持续 5 日减仓+log-space 数值稳定+pruning）。暂缓理由：计算复杂度 O(t) 需 pruning + 个人系统样本短（≥200 交易日）+ 与 §4.8 同期暂缓 + 似然模型选择额外复杂度。§6.27 待裁定（P3，与 §6.10 同步重评，最小集成路径：先单策略试运行 BOCD 输出 P(changepoint) 仅供参考不触发，验证有效性后再接入双触发系统）。**施工算法完整性结论**：35 号 6 流程闭环无缺失独立环节，BOCD 是 §4.8 统计检测的概率化横切增强非独立流程 |
| 2026-08-10 | 1.12.0 | §3.20 行业印证补 **Triple Penance Rule**（Bailey & López de Prado 2014 SSRN 2201302 + BacktestBase 2026-02 实证引用）——回撤恢复时间为形成时间的 2-3 倍，为 min_hold 持续时间门控（WARN 5 日 / DANGER 10 日 / CRISIS 20 日）提供经验倍数依据；与 §2.1 恢复数学表（幅度非对称 Loss/(1-Loss)）正交，共同构成"幅度×时间"双维约束；RECOVERY 阶梯 5 日/阶梯累计 15 日对齐 2-3x 下限 | 持续改进：用户要求再次审查文档所有内容+选项之外更好算法+2026-08-08 最新研究+文档结构顺序内容调整+持续改进不停。全网搜索发现 BacktestBase 2026-02 引用 Bailey & López de Prado 2014 Triple Penance Rule——回撤恢复时间 2-3x 形成时间，这是回撤恢复**时间维度**的经验法则，填补 §3.20 min_hold 持续时间门控"为什么是 5/10/20 日"的推理缺口（此前为经验值无理论支撑）。§2.1 已有幅度维度（20% 回撤需 25% 收益），Triple Penance 补时间维度，两者正交 |
| 2026-08-10 | 1.13.0 | 修复 §1 状态行版本漂移（v1.11.0→v1.13.0）+ §3.19 远期演进表新增 **§6.28 波动率匹配阈值 + 历史涨幅动态防御仓位**（guorn 2026-04 A 股回撤择时实证：① 倒 U 形最优区间——阈值过浅 thrashing/过深滞后，存在与策略 vol 匹配的最优区间；② vol-matched stop——阈值应与策略自身波动率匹配而非固定数值；③ 历史涨幅动态防御仓位——DEFENSIVE 态仓位按 pre-drawdown 涨幅动态调整 涨幅>100%→0.3/>50%→0.5/否则 0.6）+ §8.3 补 guorn 行业参考 | 持续改进：用户要求再次审查文档所有内容+施工环节流程算法缺失+选项之外更好算法+2026-08-08 最新研究+文档结构顺序内容调整+持续改进不停。八次审查全网搜索发现 guorn 2026-04 A 股回撤择时实证（1992-2006 历史数据）提出**波动率匹配阈值**——止损阈值应与策略自身波动率匹配而非统一固定数值，填补 §3.2 固定 5/10/15%"为何是这些数值"的推理缺口。当前 §3.2 阈值是经验值无 vol-matching，guorn 的倒 U 形最优区间（过浅 thrashing/过深滞后）+ vol-matched stop（threshold = k × annualized_vol）+ 历史涨幅动态防御仓位（涨幅大→恢复更保守）三维度增强。与 §6.23 Landolfi 互补：Landolfi 是统计严谨校准（给定 Sharpe 的 MaxDD 分位查表），guorn 是经验 vol-matching + 涨幅感知，两者正交可叠加。**施工算法完整性结论**：35 号 6 流程闭环无缺失独立环节，vol-matched threshold 是 §3.2 阈值校准的横切增强非独立流程 |
| 2026-08-10 | 1.14.0 | 新增 §4.19 Signature-based Path Portfolio 路径签名组合优化（P5+ 理论远期登记）| §4.19 新增 path-dependent 风险度量的数学基础登记——arXiv:2608.02355（Noguer i Alonso 2026-08-03）Path Portfolio Optimization：signature 作路径通用坐标，mean-variance = 张量线性系统；Lemahieu & Boudt（Ghent）signature transform kernel trick 线性近似 expected drawdowns + VAE 生成路径集成。与 §4.14 CDaR / §4.16 CED 形成"path-dependent 风险三层递进"：具体度量（CDaR/CED）→ 签名近似（Lemahieu & Boudt）→ 统一框架（Noguer i Alonso）。暂缓 P5+ 远期：理论深度远超 MVP（rough paths 纯数学）+ 样本约束（6 obs/param 直接估计，1 obs/param driver generator 重建）+ VAE model risk + 与 CDaR/CED 优先级递进。不设近期施工计划，仅作理论远期登记 | 用户要求再次审查文档所有内容+施工环节流程算法缺失+选项之外更好算法+全网搜索 2026-08-08 最新研究+持续改进不停。全网搜索发现 arXiv:2608.02355（2026-08-03）是 path-dependent portfolio optimization 前沿理论，signature 是 CDaR/CED/UI/PI 所有 path-dependent 风险度量的数学基础。MFCCA（arXiv:2608.04987）已由并发会话纳入 90 号 v1.3.0 risk parity 五级递进第五级，本节补 signature 理论远期登记，path-dependent 风险三层递进闭环 |
| 2026-08-10 | 1.15.0 | 新增 §3.21 行业实证背书：2026-08 A 股量化私募集体回撤（风险优先原则的实盘检验）| §3.21 新增 2026-07 量化私募集体回撤实证——私募排排网/Wind 数据：中证 500 指增 7 月均跌 18.72%、中证 1000 指增跌 19.96%、稳博小盘激进择时指增 1 号近一月跌 46.24%、幻方 9 只产品均跌逾 20%。四大根因归因（风格暴露集中/分散失效/止损踩踏/端到端 AI 逆向承接深套）逐一映射到本项目设计决策（firm 层硬上限/§3.16 相关性归因/§3.20 min_hold+分批拆单/§3.5 Kill Switch 不可覆盖），实证支撑强度三级评定。关键启示：回撤非模型失效而是风险约束不足，印证项目"风险模块先于策略模块施工至 production"的风险优先原则 | 用户要求再次审查文档所有内容+施工环节流程算法缺失+选项之外更好算法+全网搜索 2026-08-08 最新研究+文档结构顺序内容调整+持续改进不停。九次审查全网搜索发现 2026-08 中国证券报/第一财经/深圳商报报道的量化私募 7 月集体回撤是项目风险优先原则的**实盘级实证背书**——百亿量化（幻方/稳博/鸣石等）因风格暴露集中+分散失效+止损踩踏回撤 20-46%，稳博端到端 AI"逆向承接恐慌盘"深套 -46% 直接印证 Kill Switch 不可覆盖的必要性。这不是新算法而是对现有设计决策的实盘验证，将行业教训映射到 §2.5.1 四级阈值/firm 层硬上限/§3.5 Kill Switch/§3.16 归因/§3.20 hysteresis 五项设计，提升设计决策的可信度与可追溯性 |
| 2026-08-10 | 1.16.0 | §3.10-§3.20 标题级别统一（## → ### 格式修复）| 文档结构一致性审查发现 §3.10-§3.20 共 11 处标题用 ##（h2）而非 ###（h3），与 §3.1-§3.9 和 §3.21（均用 ###）不一致——导致 markdown 大纲中 §3.10-§3.20 与"## 3. 决策"同级而非子节，破坏层级结构。本次修复 11 处标题级别（§3.10 施工流程算法/§3.11 恢复状态机/§3.12 统计性vs行为性诊断/§3.13 盘中实时风控循环/§3.14 Kill Switch复位端到端流程/§3.15 盘前初始化/§3.16 回撤归因端到端流程/§3.17 施工流程总览6流程闭环/§3.18 盘后状态持久化/§3.19 施工流程算法审查与远期演进/§3.20 回撤状态滞后-恢复双阈值Hysteresis）统一为 ###，使 §3.1-§3.21 全部为 §3 决策的 h3 子节，大纲层级一致。纯格式修复不影响内容/交叉引用/施工算法 | 用户要求文档结构顺序内容调整+持续改进不停。结构审查发现 §3.10-§3.20 标题级别历史遗留不一致（## vs ###），修复后 §3 全部子节统一 h3，大纲层级一致 |
| 2026-08-10 | 1.17.0 | 远期演进表 Conformal Kelly OOS 诚实账本 + RWC v3 更新 + BR-iHMM regime 依赖 | §3.19 远期演进表 3 项更新：① **Conformal Kelly drawdown dial** 补 OOS 诚实账本——Lockbox 2022+ 样本外校准保持（0.745 vs 0.750）但增长未保持（8.5%/7.0%/年低于被动基准），印证 §6.21 "slow unweighted 优于 adaptive" 设计原则（§3.19 施工骨架已遵循）；② **Schmitt RWC** 标注 v3（2026-08-03）——v3 在任意 data-driven 权重下推导覆盖界（不需 weighted exchangeability），与 Conformal Kelly "反自适应"结论一致（RWC 用 regime 做校准加权而非 conformal 宽度局部自适应，避开"自适应损害增长"陷阱）；③ **RWC regime 特征稳定性依赖** 补 BR-iHMM（arXiv:2604.14322, Yiu et al. 2026，在线双重鲁棒无限 HMM 预测误差降 67%）作 regime 特征在线更新方案，天然适配 A 股跳空/涨跌停异常点 | 用户要求再次审查+选项外更好算法+全网搜索 2026-08 最新研究+持续改进不停。后台搜索代理返回 2026-08 回撤/regime/风险平价最新研究：Conformal Kelly OOS 诚实账本（增长未保持）是此前未记录的重要负面结果，印证"slow unweighted"设计原则正确性；RWC v3 放宽 weighted exchangeability 假设使其更易部署；BR-iHMM 填补 RWC regime 特征在线更新的工程缺口。三项均为远期演进表更新非施工算法缺失 |
| 2026-08-10 | 1.18.0 | §3.19 远期演进表新增 §6.29 **Fanous Recovery-Efficiency Protocol**（非对称去风险路径依赖框架）| [arXiv:2605.09123](https://arxiv.org/abs/2605.09123)（Fanous 2026-05 "The Engineering of Skew"）：Recovery-Efficiency Protocol 将回撤深度+水下时间+恢复负担缩减+反弹参与度四维度链接为 allocator-facing 报告准则。**非对称去风险**（skew engineering）——降低有害下行参与度 > 降低上行参与度，控制 submergence 同时保留足够反弹参与度维持复利，与 §4.5 CPPI 的对称去风险形成对比。恢复负担非线性 R=1/(1-D)-1（D=20%→R=25%，D=50%→R=100%），对称去风险在深回撤时牺牲过多上行导致恢复负担无法缩减。当前 §3.4 recovery_factor 阶梯是对称缩减（0.25→0.50→0.75 全仓同步恢复），缺非对称维度。与 §6.21 Conformal Kelly 正交（Kelly 前馈/Fanous 反馈） | 用户要求再次审查+选项外更好算法+全网搜索 2026-08-08 最新研究+持续改进不停。全网搜索发现 Fanous 2026-05 非对称去风险路径依赖框架——当前回撤 Protocol 的 recovery_factor 是对称缩减（下行上行同步恢复），Fanous 提出"非对称去风险"（下行缩减更激进/上行恢复更快）填补反弹参与度缺失维度。属远期演进表登记非施工算法缺失，MVP 不改对称恢复 |
| 2026-08-10 | 1.19.0 | §4.5 CPPI 诚实账本补东方证券 2026-04 A股实证反证 + §6.30 待裁定登记组合配置层远期候选 | §4.5 拒绝 CPPI 的理由#2"A股 gap risk 使 CPPI 失效"此前无 A 股实证反证。全网搜索发现 [东方证券 2026-04 "CPPI+风险预算"两阶段法](https://www.uufund.com/Report/Detail?id=AP202604121821139947)在 A 股 2006-2026 全样本回测显示 CPPI **在 A 股可生效**——年化 13.41%/Sharpe 1.53/Calmar 1.23 优于等权和纯 RP，三层风险控制（CPPI 保本 + 动态回撤控制 + RB 分散）兜底 gap risk。**这是对拒绝理由#2 的重要反证**，但经评估仍不采纳：①定位正交（东方证券是组合配置层，本项目是 sleeve 级风险节流，[30号 §2.2](30_multi_strategy_concurrency.md)）；②无保本承诺（拒绝理由#3 仍成立）；③架构耦合（三层一体化不可拆单层套用）；④可解释性优先（m 值主观 vs 5/10/15% 阈值明确）。借鉴价值：东方证券"动态回撤控制"层与本项目 §3.20 Hysteresis + §3.4 recovery_factor 同构（回撤越深仓位越轻的反馈式），是同一设计原则的不同工程实现。§6.30 待裁定登记仅当项目演进到"组合配置层"独立模块时重新评估 | 用户要求再次审查文档所有内容+施工环节流程算法缺失+选项之外更好算法+全网搜索 2026-08-08 最新研究+文档结构顺序内容调整+持续改进不停。后台搜索代理返回 2026-08 最新交易算法研究，6 项突破性算法中 5 项（Conformal Kelly/MAP-Elites/LLM-FADT/RRG+扩散/AlphaAgent）已被并发会话覆盖，唯一缺口是 CPPI+风险预算（东方证券 2026-04 A股实证）在 §4.5 仅"拒绝"无 A 股实证交叉引用。本次补全诚实账本：反证拒绝理由#2 但维持拒绝决策（4 条不采纳理由），登记 §6.30 远期候选。**审计结论**：6 项突破性算法现已全部覆盖，35 号 19 轮审查施工算法完整性闭合 |
| 2026-08-10 | 1.20.0 | §3.5 补 2026 全球监管 Kill Switch 背书（BoE Sintra Forum herding 风险 + SEBI 物理隔离 + 事后审计三维度）+ §8.3 补 BoE/SEBI 2 篇行业参考 + §1 状态行版本漂移修复（leading v1.18.0→v1.20.0，00_index 2.93.0 声称同步但未生效）| 持续改进：用户要求再次审查文档所有内容+施工环节流程算法缺失+选项之外更好算法+全网搜索 2026-08-08 最新研究+文档结构顺序内容调整+持续改进不停。全网搜索发现 2026-08 全球监管对 Kill Switch 的强化要求——① BoE 副行长 Breeden 2026-06-30 ECB Sintra Forum 演讲指出 **AI agent herding（非单一 agent 失控）是核心风险**，"a thousand well-governed trading agents can still stampede together"，BoE/BIS Innovation Hub/Bundesbank 联合多轮压力模拟探索市场级 kill switch，"human-in-the-loop for every action unrealistic"，FPC 2026-07-07 发布 AI 金融稳定评估；② SEBI 2026-05 算法交易框架强制 Kill Switch 与主交易逻辑物理隔离+算法报备+实时监控。三维度验证本项目架构合规性：4 层防御架构（§3.5.1）对齐 BoE 多 agent 协作风控方向；stop_loss 独立于 drawdown_controller 满足 SEBI 物理隔离；daily_auditor 审计清单覆盖 BoE 事后审计要求。同时修复 §1 状态行版本漂移（leading v1.18.0 vs frontmatter v1.19.0，00_index 2.93.0 修订记录声称已同步但实际未生效）。**施工算法完整性结论**：35 号 20 轮审查施工算法完整性闭合，本次为监管合规背书补全+版本漂移修复非新施工算法 |
| 2026-08-10 | 1.21.0 | §3.5 补 ④ BoE FPC circuit breaker vs kill switch 语义区分+Q3 2026 DP 时间线+deterministic output gating+bare-metal recovery 三原则验证+⑤ Herding 定量背书（GeomHerd arXiv:2605.11645 检测滞后 272 步+AI Systemic Risk arXiv:2604.03272 18-54% 尾部放大超线性增长）| 二十五轮审查全网搜索 2026-08-08 最新研究，发现 v1.20.0 BoE 监管背书可深化——① BoE FPC 2026-07-07 金融稳定报告明确区分 circuit breaker（临时可恢复）vs kill switch（永久终止），本项目 §3.7 不可覆盖原则对应 kill switch 语义，37 号 circuit breaker 对应可恢复暂停，分层正交与 BoE 一致；② Q3 2026 DP 时间线（8-9 月咨询→FCA Q4→PRA 2027→执行 2028）为监管跟进提供路线图；③ deterministic output gating+bare-metal recovery 验证 stop_loss 独立于 drawdown_controller+Task Scheduler watchdog+daily_auditor 独立审计进程满足三原则；④ GeomHerd 揭示价格相关性 herding 检测滞后 272 步，决策图层面相关性领先 40 步；⑤ AI Systemic Risk 用 SEC 13F 全样本证实尾部放大 18-54% 超线性增长。**施工算法完整性结论**：35 号 21 轮审查施工算法完整性闭合，本次为监管背书深化+herding 定量背书非新施工算法 |
| 2026-08-10 | 1.22.0 | §3.5 补 COMPEL Framework Kill-Switch 四模式架构参考（Hard-stop/Graceful-halt/Rollback/Scoped-disable 映射本项目三模式已覆盖+Rollback 待 §6.11）+VeritasChain Flight Recorder 审计层（append-only 哈希链+Ed25519 签名+RFC 8785 规范化，§6.31 远期）+§3.5 ⑥ Bailey 2026-07-23"证明而非声称"+Wolters Kluwer 72% 银行 kill switch 未就绪+FCA Mills Review 算法决策可追溯+§3.5 ⑦ ORCA arXiv:2604.17251 谱特征 herding 可施工替代（24 ETF+127 谱特征+RF walk-forward Sharpe 1.13/MaxDD -7.5%/crash 检测增益 +10.3pp）+Weng arXiv:2607.27063 A 股 Johnson S_U 尾部 herding 指标+§4.18 Dm-BOCD arXiv:2302.04759 鲁棒性升级路径（diffusion score matching 比 β-BOCD 快 10x+对离群点鲁棒）+§6.31 Shelby arXiv:2607.07359 AI Resilience Gap fallback 教义（5 要素：依赖映射/关键性分层/impact tolerance/fallback 教义/provider 集中度） | 二十六轮审查全网搜索 2026-08-08 最新研究，两个后台搜索 agent 返回 24+ 篇前沿论文筛除已登记/不适配，登记 6 项高价值新发现——① COMPEL Framework 四模式（Hard-stop/Graceful-halt/Rollback/Scoped-disable）是 kill switch 设计的语义分类框架，本项目现有实现已隐式覆盖三模式（Hard-stop=§3.5 全平/Graceful-halt=§3.4 恢复阶梯/Scoped-disable=§3.3 单策略止损），Rollback 待 §6.11 4 层架构补齐；② VeritasChain Flight Recorder（Two Sigma 22 个月未检出参数操纵+SEC 罚 9000 万美元事件）提出 append-only 哈希链审计架构，本项目 §3.18 daily_auditor 日志远期向此标准演进；③ Bailey 2026-07-23"证明而非声称"+Wolters Kluwer 72% 银行 kill switch 未就绪+FCA Mills Review 三项监管动态深化 v1.20.0/v1.21.0 监管背书，警示 kill switch 须实测非文件化；④ ORCA 谱特征（24 ETF+127 谱特征+RF walk-forward BCD-AUC 0.741/Sharpe 1.13/MaxDD -7.5%）是 GeomHerd 的轻量化可施工替代，补 §3.5 ⑤ GeomHerd（Ricci 流计算成本高）的价格相关性层面替代路径；⑤ Weng A 股 herding（Johnson S_U 变换尾部 herding 指标）是 2026 专门针对 A 股的 herding 论文，本土适配；⑥ Dm-BOCD（diffusion score matching 广义贝叶斯推断）是 §4.18 标准 BOCD 的鲁棒性升级路径，应对 A 股厚尾/跳空场景。§6.31 Shelby AI Resilience Gap fallback 教义填补"kill switch 触发后下一步做什么"的降级运行模式空白。**施工算法完整性结论**：35 号 22 轮审查施工算法完整性闭合，本次为监管背书深化+herding 可施工替代+BOCD 鲁棒性升级+fallback 教义远期登记非新施工算法 |
| 2026-08-10 | 1.23.0 | §6.32 新增 Put-Option Sleeve（convex insurance 腿）+ Four-Axis Hedge Diagnostic —— arXiv:2607.00883 双 sleeve 框架补全 | §6.18 此前仅采纳 [arXiv:2607.00883](https://arxiv.org/abs/2607.00883)（Noguer i Alonso & Al-Fallouji 2026-07-01，"Tail Risk Management with Puts and Trend Following: A CVaR Framework"）的 trend-following 腿（A 股适配为减仓/空仓），论文的 put-option 腿（convex insurance）+ 四轴 hedge-quality 诊断 + 时间分离洞察（put 防 jump / trend 防 grind 互补，混合比单一 sleeve 降 terminal CVaR）未登记。本次补全双 sleeve 框架诚实账本：① put-option sleeve 作 P5+ 组合层远期候选（需期权基础设施 + premium budget，同 §6.30 组合配置层触发条件）；② 四轴诊断（conditional convexity / tail-event reliability / non-stress carry / drawdown persistence）可先于 put sleeve 落地，用作 §6.18 减仓/空仓 hedge 质量评估工具；③ **§6.18 事实订正**——§6.18 称"A 股不能做空+无期权"事实不准，A 股有 50ETF/300ETF/中证1000 ETF 期权（2015/2019/2022）+ 沪深300/中证1000 股指期权，组合层 put 对冲可行（约束：无个股期权、深 OTM 流动性薄）。**施工算法完整性结论**：35 号 23 轮审查施工算法完整性闭合，本次为论文双 sleeve 框架补全 + 事实订正非新施工算法 |
| 2026-08-10 | 1.24.0 | §3.5 补 3 项 2026-08 最新 kill switch / herding / circuit breaker 研究：① **Unfireable Safety Kernel**（[arXiv:2606.26057](https://arxiv.org/abs/2606.26057) Dobrin & Chmiel 2026-06-24 ARYA Labs，IBM 首任全球首席 AI 官）——架构级 kill switch，运行在 agent 地址空间之外（agent 无法触及/重配置/杀死，no kernel no agent），四属性（进程分离+唯一路径预执行强制+双重 fail-closed+Ed25519 签名证据日志），Z3 SMT 形式化验证 fail-closed 不变量+Kani 有界模型检测+1000 次自修改 704 次逃逸尝试全被拒绝。与 COMPEL 正交（COMPEL 管"怎么停"语义分类，Unfireable 管"停不掉"架构保证）。本项目 §3.5.1 L3 看门狗层是 Unfireable 思路的部分实现，登记为 §6.31 远期演进（L3 施工时参考四属性设计）；② **Novotny Herding 相图触发**（[arXiv:2607.08907](https://arxiv.org/abs/2607.08907) Novotny 2026-07-09 Bayes Business School）——Bouchaud 相图方法到订单簿模型，φ_∅ 单边订单簿事件比例≈0.34 作为 herding 微观结构触发器（rule-robust+horizon-robust），与 §3.5 ⑦ ORCA/Weng 收益分布层面 herding 检测正交互补，登记为 §6.31 远期候选（需 Level 2 数据+A 股 φ_∅ 阈值校准）；③ **Li et al. Agent Swarm circuit breaker 实证参数**（[arXiv:2604.27150](https://arxiv.org/abs/2604.27150) Li/Laryea/Ihlamur 2026-04 Oxford+Vela Research）——900+ 交易 8960 配置全网格，最强配置 1.0×ATR 止损+2.0×ATR 止盈+circuit-breaker 连续 2 亏后 reduction factor 0.25，与 §3.3 drawdown 阈值驱动正交（连亏次数驱动），登记为 §3.3 增强 Phase 2 候选 | 二十七轮审查全网搜索 2026-08-08~10 最新 kill switch / herding / circuit breaker 研究，搜索 agent 返回 11 项新发现筛除已登记/不适配，登记 3 项高价值新发现——① Unfireable Safety Kernel 是比 COMPEL 更根本的架构级 kill switch（agent 地址空间外+Z3 SMT 形式化验证+开源 Apache-2.0），本项目 L3 看门狗层是其思路的部分实现，施工时参考四属性；② Novotny 相图提供 herding 的订单簿微观结构定量基础（φ_∅ 阈值触发），填补 §3.5 herding 检测的微观结构维度空白；③ Li et al. circuit breaker 提供连亏次数驱动的实证参数（2 连亏×0.25 reduction），与 §3.3 drawdown 阈值驱动正交可叠加。**施工算法完整性结论**：35 号 24 轮审查施工算法完整性闭合，3 项新发现均为横切增强/远期登记非新施工算法 |
| 2026-08-10 | 1.25.0 | §4.20 新增 Continuous Cash-Overlay Filters（连续现金叠加回撤过滤器）—— arXiv:2606.09025 Xiong 2026-06-08 | 三十轮审查 + 后台搜索 agent 返回 2026-08-08 最新回撤控制研究 5 领域 15 篇论文，§4.20 新增 Xiong 连续现金叠加回撤过滤器（arXiv:2606.09025 Xiong 2026-06-08 "Continuous Cash-Overlay Filters for Growth–Defensive Risk Sleeve"）：两类连续过滤器组合——① slow-tail compensation filter（针对 2022 式持续补偿恶化，防御资产长周期跑输成长资产）；② V-shape crash-brake filter（针对快速回撤，V 型下跌急刹提现金/V 型反弹快速恢复避免踏空）；③ max-cash 规则组合（更保守者获胜）。实证 2017-2026 walk-forward：CAGR 16.62%→20.45%（+3.83%），MaxDD -33.59%→-16.77%（改善 16.82%），**同时提升收益和降低回撤**。**与本项目的关系**：范式差异（离散分档 vs 连续比例调整），与 31 号 §2.4.3 BlackRock 比例控制 vol-targeting 同构（都是连续闭环反馈替代离散分档），V-shape crash-brake 与 §3.5 Kill Switch 互补（软着陆 vs 硬着陆）。**暂缓理由（P3 远期）**：① 本项目无 growth-defensive sleeve 架构（5 策略独立 sleeve 无天然成长-防御二分）；② A 股 T+1 限制连续调整响应延迟；③ 与现有回撤 Protocol 冗余（34 号 regime Shrinkage 已细粒度节流）；④ max-cash 规则保守性偏置。**重评条件**：实盘 ≥1 年后离散分档阶梯跳变问题显著时评估连续平滑项。**施工算法完整性结论**：35 号 25 轮审查施工算法完整性闭合，本次为回撤控制连续过滤器远期登记非新施工算法 |
| 2026-08-10 | 1.26.0 | §6.33 新增 Non-concave VaR 约束下"赌博回本"行为理论警示——floor 设计理论背书 | 四十一轮审查 + 后台搜索 agent 返回 2026-08-03~07 遗漏论文 12 篇，筛除已整合/低相关 10 篇，登记 1 篇高价值理论背书——[arXiv:2608.05623](https://arxiv.org/abs/2608.05623) Li/Lyu/Wei 2026-08-06 研究 VaR 约束下非凹目标函数（期权激励）的动态风险管理，核心发现：低 floor 改善下行保护+降低破产，高 floor 反而增加破产+诱发 gambling-for-resurrection 行为。为 §4.4 拒绝"回撤进入 RiskSignal"（赌博倾向）+ §3.2 保守低地板阈值设计（5/10/15% << 8/15/20/25%）提供量化理论背书，与 36 号 §3.5 v1.23.0 已登记的"VaR floor 设定警示"形成跨文档交叉印证。**施工算法完整性结论**：理论背书条目，不引入新施工算法 |
| 2026-08-10 | 1.27.0 | §3.5 ⑧ 补 FSB 2026-06-10 AI 稳健实践咨询报告——全球监管顶层锚点 | 四十二轮审查全网搜索 2026-08-08 前后最新研究，arxiv q-fin.RM 截至 8 月 4 日 15 篇中 3 篇已整合（2608.02002→40号/2608.00127→35号/2608.01494→35号）+1 篇已评估不整合（2607.27461）+8 篇场景不匹配（信用/气候/链上/PPA/FX），新发现 1 篇 [FSB 2026-06-10 "Sound Practices for Responsible Adoption of AI"](https://www.fsb.org/2026/06/sound-practices-for-responsible-adoption-of-artificial-intelligence-ai-consultation-report/) 咨询报告（12 项 SP）——FSB 是 G20 框架下全球金融稳定协调机构，① BoE/BIS/SEBI 均为 FSB 成员，本报告是 §3.5 ①-⑦ 监管背书的顶层锚点。核心洞察"AI monitoring AI"（人工监督 agentic AI 不可扩展，须 AI 监控 AI）直接印证 §3.5.1 L3 看门狗层 + §6.31 Shelby AI Resilience Gap fallback 教义 + Unfireable Safety Kernel（agent 地址空间外强制）；bounded authority（AI agent 视为 synthetic employees，bounded authority+defined scope+accountability constraints）印证 §3.7 Kill Switch 不可覆盖 + COMPEL Scoped-disable；agentic AI 放大风险（unauthorized actions/goal misalignment/reward hacking）印证 §3.21 A股量化私募端到端 AI 逆向承接深套。适用性边界：报告不具法律约束力（咨询性质，征求意见至 2026-07-22，最终版 2026-10 提交 G20），但 12 项 SP 中 SP3（AI 风险管理框架）+SP9（性能管理）+SP10（人工监督）+SP11（网络/ICT 风险）对个人量化系统同样适用，本项目 §3.5 Kill Switch+§3.18 daily_auditor 审计+§3.5.1 Ghost Position 检测+Task Scheduler watchdog 已隐式覆盖核心要求。另评估 Aldridge arXiv:2608.02311 "AI Governance for Institutional Readiness in Finance"（2026-08-03）——核心是 agentic AI 治理框架（四层框架+regret-covariance drift+crowding model 39.2%→79.3%+inner-confidence kill switch），与本项目传统量化（非 LLM agent 交易）相关性低，crowding model 定量背书对 37 号边际价值低（37 号已有 LRISK 三大放大通道实证+Aldridge 2607.01377 Kyle λ），与 FSB 主题重叠且 FSB 层级更高，不登记避免过度文档化。**施工算法完整性结论**：35 号 26 轮审查施工算法完整性闭合，本次为全球监管顶层锚点登记非新施工算法 |
| 2026-08-10 | 1.28.0 | §3.10/§3.15/§3.18 entry VaR 持久化补全（跨文档算法交接完整性审查——链路 5 缺口修复） | 后台 agent 6 链路审查发现链路 5（36→35 VaR→回撤）缺口：35号 §3.10 日度循环伪代码引用 `entry_nav`（入场 NAV）但未定义 `entry_var`（入场 VaR）的持久化位置和数据结构。36号计算 `VaR_95`/`ES_95` 作为 C4/C5 约束输入，但"入场 VaR"（用于回撤归因对比当前 VaR vs 入场时 VaR 判断风险是否恶化）的记录位置此前未明确。本次补全：① §3.10 盘前 VaR 计算后新增注释——当日盘前 VaR_95 作为 entry_var 保存到 state_store；② §3.15 阶段 3 基线校准新增 `entry_var = state_store.load_entry_var()` 加载前一交易日盘前 VaR 快照（None=首次启动跳过归因对比），`daily_auditor.log_baseline` 新增 entry_var 参数；③ §3.18 盘后持久化新增阶段 4b `state_store.save_entry_var(trade_date, var_cvar.var_95)` + `daily_auditor.log_entry_var`，用途说明：§3.16 回撤归因 current_var vs entry_var 判断风险恶化（即便 NAV 未回撤，VaR 恶化也触发"风险恶化型归因"分流减仓）；④ §3.18 配对约束表新增 entry_var 行。缺口性质="持久化位置未明确"非"算法逻辑断裂"，严重性中等 |
| 2026-08-10 | 1.29.0 | §3.16 entry_var 归因分支补全（CRITICAL）+ §3.14 RECOVERY 分级回撤保护+浮点等值修复 + §3.15 nav_history 冷启动守卫 + §3.16 单策略/除零守卫 | 施工流程算法边缘案例深度审查发现 4 项问题：① **CRITICAL** §3.15/§3.18 声称 §3.16 用 entry_var 做风险恶化归因，但 §3.16 伪代码完全未实现——§3.16 只有 SYSTEMIC/STRATEGY_SPECIFIC/MIXED/BEHAVIOURAL 4 归因分支，缺第 5 种 RISK_DETERIORATION。本次补全：§3.16 函数签名新增 entry_var/current_var 参数，新增"步骤 0 风险恶化型归因"分支（var_deterioration_ratio > 1.5 即触发 RISK_BASED_REDUCTION 减仓，不等 NAV 回撤），响应分流表新增 RISK_DETERIORATION 行。② **HIGH** §3.14 RECOVERY 期间回撤保护仅 >15% 触发，5-15% 空档无保护。本次补全：三级分级保护（>5% 暂停阶梯升级冻结 5 日 / >10% 回退一级 / >15% 阶梯耗尽回 KILL），对齐 §3.11 状态机 WARN/DANGER/CRISIS 阈值。③ **MEDIUM** §3.14 `drawdown_pct == 0` 浮点等值检查不安全，改用 `recovered_pct >= 1.0 - 1e-6` epsilon 比较。④ **HIGH** §3.15 nav_history < min_history(30) 时冷启动行为未定义。本次补全：MIN_HISTORY=30 守卫，不足时进入保守冷启动模式（position_cap 50% + 强制 NORMAL + 日终审计标记 COLD_START_INSUFFICIENT_HISTORY）。⑤ **MEDIUM** §3.16 单策略时相关性矩阵未定义 + per_strategy_contribution 除零风险。本次补全：单策略守卫（直接归为 STRATEGY_SPECIFIC_SINGLE_STRATEGY）+ 除零守卫（total_abs_dd > 1e-10 才除）|
| 2026-08-10 | 1.29.1 | §3.10 daily_risk_loop 补 fills + limit_consumption 参数（伪代码审计 9 项缺口修复之一） | 伪代码审计发现 §3.10 daily_risk_loop 盘后审计行 `daily_auditor.audit(trade_date, positions, fills, limit_consumption)` 直接引用 fills / limit_consumption 但函数签名未声明（二者为盘中累积态——fills=当日成交列表，limit_consumption=限额使用情况，由盘中阶段产出，盘后审计消费）。修复：补入函数签名为 `fills=None, limit_consumption=None` 可选参数 + 注释说明来源。修复原则：最小改动保留原算法语义，仅补全参数声明不改变决策逻辑。施工算法完整性结论：35号 §3.10-§3.20 经本轮修复后 daily_risk_loop 变量定义闭环，盘后审计可正确接收盘中累积态 |
| 2026-08-10 | 1.30.0 | §3.13 intraday_risk_loop 补 strategy_states 参数 + aggregate_expected_holdings 辅助函数（伪代码审计 9 项缺口修复之二） | 伪代码审计发现 §3.13 intraday_risk_loop 函数体内 `detect_ghost_positions(broker.get_holdings(), strategy_state)` 引用未定义的 strategy_state（单数）——实为各策略预期持仓的聚合。修复：① 函数签名新增 `strategy_states: dict` 参数（{strat_id: StrategyState}），替代原伪代码未声明的 strategy_pnls_today；② 新增 aggregate_expected_holdings(strategy_states) 辅助函数，聚合各策略预期持仓与 broker 实际持仓对比检测 Ghost Position；③ Kill Switch CLOSED 分支改用 expected_holdings 聚合结果。修复原则：最小改动保留原算法语义，仅补全参数声明+辅助函数消除未定义引用 |
| 2026-08-10 | 1.30.1 | §3.13 intraday_risk_loop 补 realized_pnl 参数 + §3.16 entry_var/strategy_pnls_history 参数（伪代码审计 9 项缺口修复之三） | 伪代码审计发现：① §3.13 函数体内 `broker.get_realized_pnl(today)` 引用未声明的 realized_pnl 来源（函数签名仅有 market_open/market_close/opening_nav）；② §3.16 回撤归因伪代码引用 strategy_pnls_history（各策略历史 PnL 序列）但未声明参数。修复：① §3.13 函数签名补 realized_pnl 来源说明（通过 broker.get_realized_pnl(trade_date) 获取，trade_date 由调用方传入）；② §3.16 函数签名补 strategy_pnls_history 参数 + 历史不足守卫（None 时跳过相关性归因）。修复原则：最小改动保留原算法语义，仅补全参数声明 |
| 2026-08-10 | 1.30.2 | §3.13 intraday_risk_loop 补 trade_date 参数 + fills/limit_consumption 产出 + §3.17 阅读指引 + §3.19 结构说明（伪代码审计 9 项缺口修复之四 + 文档结构修复） | 伪代码审计 + 文档结构审查发现 4 项问题：① **CRITICAL** §3.13 函数体内 `broker.get_realized_pnl(today)` 引用未声明的 today 变量——补 trade_date 参数入函数签名，today→trade_date；② **CRITICAL** §3.10 声明 fills/limit_consumption"由盘中阶段产出"但 §3.13 无产出点——补 fills=[]初始化 + new_fills 累积 + limit_consumption.update() + return IntradayResult(fills, limit_consumption) 交出盘中累积态；③ **MEDIUM** §3.13 未记录 last_poll_time 供下轮 get_fills_since——补 last_poll_time=now 赋值；④ **LOW** §3.17 总览图前向引用 §3.18 + §3.19 审查位置在 §3.20/§3.21 之前——补 §3.17 阅读指引说明总览→§3.18 细节的阅读顺序 + §3.19 结构说明审查结论与后续章节的关系。施工算法完整性结论：35号 §3.10-§3.20 经本轮修复后 intraday_risk_loop 变量定义闭环、与 §3.10 盘后审计数据交接闭合，6 流程闭环无缺失独立环节 |
| 2026-08-10 | 1.30.3 | 全网 2026-08-08~10 最新算法搜索最终闭环（与 36号 v1.29.2 同步） | 后台 agent 独立搜索 arXiv q-fin.RM/PM/MF/CP/TR + 中文券商研报，确认 arxiv 最新 listing 日为 2026-08-06（周末不贴出，8/10 周一尚未上线）。3 篇候选论文中 2 篇已在本号登记（arXiv:2607.00883 Noguer CVaR 框架已在 §6.32 登记/arXiv:2608.02311 Aldridge AI Governance 已在 v1.27.0 评估排除），1 篇 arXiv:2607.25353 Zhuang 期权隐含 ES bounds 更适合 36号 VaR/ES 文档（已在 36号 §8.3 登记）。**35号 drawdown/kill switch 方面无新发现**——FSB 2026-06-10 AI SP（v1.27.0）+Unfireable Safety Kernel（v1.24.0）+Novotny Herding 相图（v1.24.0）+Li Agent Swarm circuit breaker（v1.24.0）已覆盖 2026-08 前沿。**施工算法完整性最终闭环**：35号 6 流程闭环无缺失独立环节，全网搜索无遗漏高价值新算法，伪代码审计 9 项缺口已全部修复 |
| 2026-08-10 | 1.30.4 | 施工流程数据交接链 7 条断裂修复（后台 agent 深度审查发现流程级缺口） | 后台 agent 深度审查 §3.10-§3.18 的 7 条数据交接链发现 5 条断裂（4⚠️+1❌）：①§3.10 daily_risk_loop 无返回值→系统性根因，var_cvar/response/audit 无法向下游传递→补 DailyRiskResult 返回值；②§3.15 InitializationResult 缺 entry_var→§3.16 归因 entry_var 恒 None→补 entry_var+prev_attribution 字段；③§3.13 缺 response 参数→盘前裁决约束无法传入盘中→补 response 参数+消费逻辑；④§3.16 factor_decomposition/strategy_pnls_history 无数据源说明→补 RiskOrchestrator 数据源说明；⑤§3.18/§3.15 AttributionResult save/load 闭环缺失（❌完全断裂）→补阶段 4c save_attribution_result+load_attribution_result+配对表；⑥§3.11 转换表缺 RECOVERY→KILL 及三级分级保护→补 3 条转换规则；⑦§3.18 缺 save_strategy_state→补阶段 4d。**审查方法论升级**：伪代码审计从参数/变量级升级到流程交接链级（A 产出→B 消费配对验证），发现参数级审计无法检测的跨函数数据传递断裂 |
| 2026-08-10 | 1.30.5 | §3.18 prev_attribution 消费方补全（自洽性审查：加载后无消费→死数据修复） | 自洽性审查发现 §3.15 阶段 3 加载 prev_attribution（前一交易日回撤归因结果）但 §3.18 无消费方——加载的归因结果成为死数据。本次补全 §3.18 prev_attribution 消费说明：用于 §3.16 当日归因的趋势对比（归因类型是否延续/恶化），填补"加载-消费"配对缺口。性质：数据交接链配对完整性修复，非新施工算法 |
| 2026-08-10 | 1.30.6 | 施工流程数据交接链 v1.30.4 修复的二次深化——8 条断裂/不完整修复（A1/A3/A5/B1/B3/C1/C2） | 后台 agent 二次深度审查 v1.30.4 修复后发现残留断裂与确认不完整：①§3.10 DailyRiskResult 的 plan/audit 两返回字段无下游消费方（A1）→补 plan 供 execution_broker 执行、audit 供 §3.18 审计门控（audit.passed=False 不持久化当日状态）；②§3.13 intraday_risk_loop 缺 response 参数消费（A3）→补 position_sizing_engine.apply_premarket_cap(response.position_cap) 盘前仓位上限传入盘中；③§3.15 strategy_state 加载缺冷启动 None 守卫→detect_ghost_positions 崩溃（A5）→补 None 守卫；④§3.18 strategy_engine 悬空引用（A5 级联）→修复为 position_sizing_engine.get_target_holdings_snapshot；⑤§3.14 ResetConfirmation 仅 holdings_verified_zero 一项，Kill Switch 三项动作（平仓/撤单/锁新开仓）仅确认 1/3（B1）→补 orders_cancelled_verified/new_open_locked_verified 字段及校验；⑥§3.13 缺收盘前 N 分钟强制检查（B3）→补 14:55 后 EMERGENCY 触发 closing_auction 减仓单；⑦§3.11 状态机转换表 RECOVERY→KILL"无条件 KILL"与 §3.14 代码"分级保护"分裂（C1 MAJOR）→修正表码一致，RECOVERY→KILL 需阶梯耗尽 step<0、retreat 有 step>0 守卫；⑧§3.14 KILL→RECOVERY→KILL 循环无守卫（C2）→补复位次数上限（20 日 3 次）+冷却期（3 日）+永久锁定阈值（累计 5 次）。审查方法论：从 v1.30.4 的"流程交接链级"深化到"复位确认完整性与 KILL 循环守卫"。施工算法完整性结论：35 号 6 流程闭环经二次深化审查后复位端到端三项动作确认完整、KILL 循环有守卫、状态机表码一致、审计门控落地 |
| 2026-08-10 | 1.31.0 | 跨文档流程交接链 6 条断裂修复（E1-E8，35号↔36号协同算法完整性） | 从参数级审计升级到流程交接链级审计，发现 35号↔36号 跨文档协同的 6 条断裂：①**E6**§3.10 drawdown_controller.evaluate() 未传入 var_breach_state→36号 §3.15 VarBreachStateMachine 协同失效（BREACHED 不产生额外 20% 折扣）→补 var_breach_state 参数传入；②**E8**§3.10 内部计算 var_cvar 与 36号 §3.17 声明的"36号产出 var_cvar 喂入 35号"冲突→删除 35号内部计算，var_cvar 由 36号产出经参数传入；③**E5**§3.13 盘中循环未调用 36号 §3.12 intraday_var_recalc()→盘中 VaR 重算协同逻辑未实现→补触发条件检测+重算调用+新 response 重新裁决（取最严覆盖盘前）；④**E2**§3.18 与 36号 §3.18 均用 status="COMPLETE"→盘前初始化无法区分状态来源→35号改用"DRAWDOWN_COMPLETE"，36号改用"VAR_COMPLETE"双阶段标记；⑤**E1**§3.18 与 36号 §3.18 盘后持久化执行顺序未定义→明确 RiskOrchestrator 编排顺序 daily_auditor.audit()→35号 §3.18→36号 §3.18，35号审计失败则 36号不执行；⑥**E3**§3.15 双 RECOVERY 叠加逻辑模糊（35号 DrawdownStateMachine RECOVERY + 36号 VarBreachStateMachine RECOVERY 同时发生时 position_cap 叠加规则不明）→明确 effective_cap = 阶梯值 × 0.9 + 下限保护 max(0.0) + 双恢复期过长（>20 交易日）DUAL_RECOVERY_PROLONGED 告警。同步更新 36号 §3.15/§3.18 对应修复。施工算法完整性结论：跨文档协同算法经 6 条断裂修复后 35号↔36号 流程交接链闭合 |
| 2026-08-10 | 1.31.1 | **第三十九轮审查：Liu Leakage-Safe Residual-Stress Signal 截面 PCA 残差压力前馈预警登记** | 用户要求"再次审查文档所有内容+施工环节流程算法有缺失+选项之外更好的答案算法+全网搜 2026年8月今天最新研究+文档结构顺序内容调整+持续改进不要停下来询问"。全网搜索 2026-08 q-fin.RM/q-fin.PM 最新研究发现 [Liu 2026-06 "Beyond Volatility: A Leakage-Safe Residual-Stress Signal for Drawdown Risk Monitoring"](https://www.mdpi.com/2227-9091/14/7/143)（MDPI Risks vol.14(7), Northwestern University）——截面 PCA 重构误差构造 residual-stress 信号，leakage-safe 设计（PCA mapping 用 t-1 信息估计+stress score 在 t 计算+rolling train-only 分位数阈值），核心实证"vol 低但 residual stress 高→未来 21 交易日 drawdown onset 概率显著高"，是 vol 的**互补**非替代。**§6.34 新增 P3 远期登记**：填补本项目"截面错位前馈"维度空白（§3.5 Kill Switch 反馈+§6.18 trend 单标的趋势前馈+§6.27 BOCD 单标的概率变点均无截面维度）；vol 低态补充价值高（当前 §3.5 VaR 5 级+drawdown_pct 阈值在低 vol 态均不易触发）；A 股适配申万一级 28 行业做 PCA；leakage-safe 与 15号 bitemporal PIT 纪律天然对齐；与 §3.5 ⑦ ORCA + §4.23 Chen CSAD/CSSD 形成"截面错位检测轻-中-重三档梯度"（CSAD 轻量统计量/Liu 中等 PCA 残差/ORCA 重模型 127 谱特征+RF）；与 §6.10 CUSUM 正交（CUSUM 时间维度/Liu 截面维度）。暂缓理由：需申万行业指数实时管道+vol 低态增量价值需 A 股验证+风险优先原则（§6.11 Kill Switch 4 层架构先施工）。重评条件：行业指数管道就绪+实盘≥1 年 Kill Switch 漏检 vol 低态 drawdown onset+ORCA 过重/CSAD 过轻时 Liu 作中等复杂度替代。施工算法完整性结论：35号 6 流程闭环+跨文档协同算法已闭合，本轮仅远期登记非新施工算法 |
| 2026-08-10 | 1.32.0 | **第四十轮审查：frontmatter v1.32.0 与 00_index 第三轮版本同步对齐+§6.34 Liu 信号消费方补全** | 用户要求"再次审查文档所有内容+施工环节流程算法有缺失+选项之外更好的答案算法+全网搜 2026年8月今天最新研究+文档结构顺序内容调整+持续改进不要停下来询问"。本轮 v1.32.0 frontmatter 升版的两个内容点：①§1 状态行更新为 v1.32.0 聚合 v1.31.1 §6.34 Liu 信号登记+此前 v1.30.x/v1.31.x 全部修复，对齐 frontmatter；②§6.34 Liu 信号"暂缓理由"声明"需申万行业指数实时数据管道"但未明确消费方与数据源——本轮补全"消费方=§3.5 8 级 herding/截面错位预警维度（ORCA 重模型/CSAD 轻统计量/Liu 中等 PCA 残差三档梯度的中档）+数据源=申万一级 28 行业日频指数（项目现有 SWindex 接口可适配，需新建 industry_pca_pipeline 模块）+计算频率=日频盘后（与 §3.18 盘后持久化同批）+触发逻辑=stress_score>rolling_q90 时输出 high_residual_stress 标志到 RiskSignal，§3.5 评估是否升级 herding 级别"。施工算法完整性结论：35号 6 流程闭环+跨文档协同算法已闭合，本轮为 v1.31.1 §6.34 的消费方/数据源/计算频率/触发逻辑 4 项细节补全非新施工算法，同步 00_index v2.7.1 第三轮版本同步 |
| 2026-08-10 | 1.33.0 | **第四十一轮审查：§5.2 Stage 4 + §3.19 远期演进表与 §4.6-§4.24/§6.8-§6.34 全量对齐——14 族分类表+§4.16-§4.24 汇总小表消除 23 项远期登记遗漏** | 用户要求"再次审查文档所有内容+施工环节流程算法有缺失+选项之外更好的答案算法+全网搜 2026年8月今天最新研究+文档结构顺序内容调整+持续改进不要停下来询问"。文档结构一致性审查（与 36号 v1.9.0 同步进行）发现两处同步缺口：①§5.2 演进路径 Stage 4 仅提"§4.12-§4.15 评估的 2026 学术研究方向（MPC/趋势跟踪/CDaR/多 agent），详见 §6.17-§6.20 待裁定"——遗漏 §4.16-§4.24（9 项替代方案）+ §6.21-§6.34（14 项待裁定）共 23 项远期登记；②§3.19 远期演进表表头仍写"详见 §4.12-§4.15 评估"但实际已有 §4.16-§4.24。本次修复：§5.2 Stage 4 重构为 14 族分类表（回撤度量/统计检测/时间维度/连续控制/归因/conformal/路径依赖/回撤工具/网络级风险/厚尾传播/恢复机制/Kill Switch/组合配置层/理论背书），每族标注 §4.x 替代方案 + §6.x 待裁定 + 优先级 + 定位；§3.19 表头更新为"§4.6-§4.24 评估 + §5.2 Stage 4 14 族分类表"+ v1.33.0 范围说明 + §4.16-§4.24 汇总小表（9 行，避免与 §5.2 重复）。同步 36号 v1.9.0 §5.2 演进路径六类族重组。后台搜索 agent 全网搜 2026-08-08~10 最新研究确认**无新增高价值研究，已全覆盖**（7 篇重复已收录+6 篇低相关+0 篇高价值新增）。施工算法完整性结论：35号 6 流程闭环+跨文档协同算法已闭合，本轮为文档结构一致性修复（§5.2+§3.19 ↔ §4.x/§6.x 全量对齐）非施工算法缺失 |
| 2026-08-10 | 1.34.0 | **第四十二轮审查：§4.25 MFCCA 符号保留多重分形交叉相关组合分配 + §4.26 Robust Risk Parity A 股实证——组合配置层 drawdown 降低双候选登记** | 用户要求"再次审查文档所有内容+施工环节流程算法有缺失+选项之外更好的答案算法+全网搜 2026年8月今天最新研究+文档结构顺序内容调整+持续改进不要停下来询问"。全网搜索 2026-08 最新组合配置/drawdown 控制研究发现两篇高价值论文：① [arXiv:2608.04987](https://arxiv.org/abs/2608.04987) Kakinaka & Umeno 2026-08-05 "Portfolio Allocation under Heterogeneous Scales and Multifractality"——MFCCA 风险泛函保留局部去趋势协方差符号，使同向/反向运动以相反符号贡献风险（MFDCCA 丢失符号），q=2 退化为 MVO 严格泛化，实证每个收益水平降 drawdown/VaR/ES 无损收益。**§4.25 新增 + §6.35 P4 远期待裁定**：与 sleeve 级回撤 Protocol 正交（Protocol 管"回撤后怎么减"MFCCA 管"分配时怎么避免"），30号 §3.1 拒绝 MVO 诚实账本评估（符号保留创新但仍需多尺度交叉相关估计与 O(N) 保证冲突），定位组合配置层远期候选同 §6.30/§6.32，已由 90号 v1.3.0 risk parity 五级递进第五级登记，本节补 drawdown 维度交叉引用。② [Li & Ye 2026 Finance Research Letters](https://ideas.repec.org/a/eee/finlet/v92y2026ics1544612326001170.html) Robust Risk Parity——传统风险平价框架内集成 GARCH+regime+因子结构协方差，**A 股 2012-2024 全样本实证**对比 TRP/EW/GMV/MaxRet/ERP 五基线均优。**§4.26 新增 + §6.36 P3 远期待裁定**：独特价值=少有的 A 股全样本实证组合配置方法+regime 识别维度与 34号 RegimeMetaAllocator 天然对接，regime+GARCH 组件可独立提取接入 34号不需完整组合配置层。**MFCCA vs RRP 互补**：MFCCA 是理论前沿（符号保留），RRP 是工程化集成（A 股实证+regime）。施工算法完整性结论：35号 6 流程闭环+跨文档协同算法已闭合，本轮为组合配置层 drawdown 降低双候选远期登记非施工算法缺失 |
| 2026-08-10 | 1.35.0 | §4.27 新增 Drawdown Beyond Brownian Motion（arXiv:2608.00127）回撤阈值非高斯校准算法 + §6.37 keep-or-kill 待裁定 | §4.27 新增 Drawdown Beyond Brownian Motion（[arXiv:2608.00127](https://arxiv.org/abs/2608.00127) Landolfi 2026-07-31）回撤阈值非高斯校准算法——RSB 闭式框架的 4 测度扩展（MaxDD/MaxLoss/FinalNegTime/LongestRecovery），证明单一高斯表系统性误警，fBm 持续性表观放大为 √-time 校准失效而非真实风险；strategy archetype 分类→参数→查表校准配方；Python 伪代码 4 测度查表+archetype 分类器+阈值输出；§6.37 新增 keep-or-kill 待裁定（Phase 3 校准阶段启动前裁定是否替换 §3.2 单一高斯 √-time 校准）；§5.2 厚尾传播族表更新纳入 §4.27/§6.37。与 §6.23（v1.8.0 早期登记同一论文）形成"登记→施工算法→keep-or-kill"三阶段演进 |
| 2026-08-10 | 1.36.0 | **第四十三轮审查：§3.19+§5.2 与并发会话新增 §4.25-§4.27/§6.35-§6.37 全量同步——3 处版本漂移修复** | 用户要求"再次审查文档所有内容+施工环节流程算法有缺失+选项之外更好的答案算法+全网搜 2026年8月今天最新研究+文档结构顺序内容调整+持续改进不要停下来询问"。审查发现并发会话 v1.34.0/v1.35.0 新增 §4.25 MFCCA/§4.26 RRP/§4.27 Drawdown Beyond Brownian Motion + §6.35/§6.36/§6.37 后，§3.19 远期演进表和 §5.2 Stage 4 14 族表未同步更新（仅 §5.2 厚尾传播族被并发会话更新含 §4.27，§5.2 组合配置层缺 §4.25/§4.26/§6.35/§6.36，§3.19 表头仍写 §4.6-§4.24 + 汇总小表缺 §4.25-§4.27）。本次修复 3 处：①§3.19 表头 §4.6-§4.24→§4.6-§4.27 + 汇总小表新增 §4.25/§4.26/§4.27 三行；②§5.2 组合配置层族新增 §4.25 MFCCA/§4.26 RRP/§6.35/§6.36；③frontmatter v1.35.0→v1.36.0。同步 36号 v1.9.0 §5.2 演进路径已覆盖全部 §4.x。施工算法完整性结论：35号 6 流程闭环+跨文档协同算法已闭合，本轮为并发会话新增内容的结构同步修复非施工算法缺失 |
| 2026-08-10 | 1.37.0 | **§4.28 Aldridge & Krawciw AI Governance 新增（v1.38.0 补录修订记录——原条目遗漏）** | §4.28 新增 [arXiv:2608.02311](https://arxiv.org/abs/2608.02311)（Aldridge & Krawciw，RiskAICenter，2026-08-03）"AI Governance for Institutional Readiness in Finance"——4 层治理框架（Policy/Engineering/Composition/Systemic）+ regret-covariance policy drift 检测（intended vs observed regret 协方差，仅从观测数据计算）+ calibrated crowding model（两 agent 收敛相关暴露时 joint drawdown probability 39.2%→79.3%，为 §3.21 根因②"分散失效"提供定量模型背书）+ inner LLM confidence kill-switch（pre-decoding confidence 前馈触发器，本项目无 LLM 决策层登记为条件性候选）+ 90-day 实施序列。§3.19 远期演进表汇总小表 + §5.2 Stage 4 新增治理层族（第 15 族）+ §3.21 根因②补 crowding model 定量背书。与 §4.18 BOCD（收益分布 changepoint）/§4.21 Transfer-Entropy（网络拓扑前馈）正交互补——regret-covariance 是 policy 行为级 drift 检测，填补"策略行为是否偏离 intended"空白。远期登记（P3），不过度工程审查通过（regret-covariance 计算成本低，4 层框架是架构命名零增量成本）。（v1.38.0 注：本轮修订记录条目当时漏登，本次补录，内容以 §4.28 正文为准） |
| 2026-08-12 | 1.38.0 | **第四十四轮审查：通用规则 #11 已施工设施盘点（§2.4 新增）+ Kill Switch 执行路径口径精确化（§3.5/§3.5.1）+ 15% EMERGENCY 口径矛盾显式标注（§7 ㉓ 开放问题）+ 文档质量修复 4 项** | 架构审查 AI 七轮工作清单第 1-2 轮：①**§2.4 已施工设施盘点新增**——全面扫描代码/配置/注册表/测试/脚本/前端/治理规则后的事实清单：三层阈值模块（MOD-RK-011/MOD-POS-007/MOD-POS-008 全 production + 20/23/38 项测试）+ **Kill Switch 三套实现域分离盘点新发现**（stop_loss+DefaultRiskValidator D_RISK 交易风控 / MOD-INF-018 D_SECURITY AI 自治熔断 / MOD-INF-016 D_TRADING 5 级熔断注册表 DAILY_LOSS 3%——§2.2"三套阈值体系"精确化为"3+1"）+ 支撑设施 8 项（daily_auditor 5 项清单/ashare 引擎 2%/daily_pnl_check/CancelRateGuard 12%-15%-15笔每秒/position_sizing_engine 已消费 position_cap/systemic_risk_detector/Task Scheduler watchdog/programmatic_trading_guard）+ 未施工清单 8 项（RiskOrchestrator/state_store+DrawdownStateMachine/detect_ghost_positions/平仓撤单执行链路/独立 black_swan_detector/前端面板/阈值 YAML/ClickHouse 净值表——全部确认"仅文档/未落码"）+ 注册表缺口 2 项（drawdown_tracker/capital_curve_manager 未进 capability_canonical_file_registry；translation_registry 两条目机器误抽取）。②**§3.5 执行路径口径精确化**——stop_loss.trigger_kill_switch 是事件记录层（日志+dict），DefaultRiskValidator 只置标志+拒新订单，"平仓所有持仓+撤所有挂单"执行链路在风控域无代码，当前 Kill Switch 实际语义="禁止新增风险+事件告警"；§3.5.1 四层架构表 L1 行 ✅已实现→🟧部分实现；reset_kill_switch 事件层（有确认校验）vs 状态层（无确认参数）两层语义差异登记 §6.11 施工时统一。③**15% EMERGENCY 是否触发 Kill Switch 跨真源口径分裂显式标注**——drawdown_tracker 注释+battle_map BM-RC-03 支持 15%，30号§2.5.5+§3.11+§3.2 支持 25%，当前实际行为=仅告警（无 orchestrator 接线）；§7 ㉓ 开放问题登记（倾向 a) 15% 仅告警，不擅自裁决留业主决定，裁决后需四处真源同步）。④**§3.6 日度熔断第三口径附注**（trading_kill_switch DAILY_LOSS 3% vs 框架 4% vs ashare 2%，RiskOrchestrator 施工时须明确唯一生效值）。⑤**文档质量修复**：§3.21 project_memory 自引用链接改为纯文本说明；§6 表头补 P4/P5 优先级定义（§6.17/§6.30/§6.32/§6.35 已用但表头未定义）；§9 补录 v1.37.0 修订记录遗漏条目；frontmatter date 2026-08-10→2026-08-12。⑥**第 3 轮缺失环节审查补§3.5 触发条件表"系统故障"行**——连续拒单≥5/延迟>1000ms/成交率<50%/API超时>10s/心跳≥3 由 MOD-INF-016（D_TRADING 执行域熔断注册表）承载，行业印证 klawtrade 2026-04 7 触发器含"3+系统错误/5分钟"；此前 §3.5 仅覆盖回撤/单日亏损/连续亏损/流动性/黑天鹅 5 类，系统故障维度散落在执行域未衔接。⑦**第 4 轮 2026-08-12 全网搜索闭环**——4 组定向搜索（drawdown protocol/kill switch/circuit breaker/recovery de-risking/multi-level risk control/Calmar）命中全部为已收录来源（orstac/LedgerMind/JournalPlus/algostrategyanalyzer/nexusfi/Tidball/Aldridge/TradeShield/arXiv:2511.13251/Nystrup-Boyd）或低价值博客（saintquant/klawtrade/legitnetworth/dxpa/tradingzenith/fondeo），无新增高价值研究，维持 v1.30.3 最终闭环结论。⑧**§8.1 内引清单补录 32/42 号**（正文已引用但清单漏登）。第 5 轮过度工程审查（charter 硬边界复核）：四级阈值+日度熔断+Kill Switch 三层不过重（30号 §2.5.6 已裁定 Kill Switch+四级=真红线、VaR 5级+7黑天鹅=监控层先全建全 log）；分层风控仅单策略/组合两层不过重；恢复多阶段设计有 §6.26 P0 最小补丁限定（先单准则）；§6.31 VeritasChain 审计链为 P2 远期登记非施工项，与 OE-007 裁剪裁定不冲突——无新增过度工程项。施工算法完整性结论：35号 6 流程闭环无缺失独立环节维持不变，本轮为基础设施盘点+口径精确化+文档质量修复+系统故障触发衔接，非新施工算法 |
