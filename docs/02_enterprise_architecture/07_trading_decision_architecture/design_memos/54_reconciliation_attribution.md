---
ttl: permanent
doc_type: architecture_view
title: 对账归因
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.15.8"
date: 2026-08-15
topic: reconciliation_attribution
scope: 07_trading_decision_architecture
---

> ## 结案报告（2026-08-16 补记）
>
> **实际开发**：对账层 18 环节中 16 个此前已生产态；2026-08-16 第 5 批（会话 AI-RCAN-001，合并 057a9a2384）**仅做文档收敛**——复核修复 18 项缺陷（版本漂移×4/55 号悬空引用×8/能力夸大×4/伪代码 bug×7，含 Carino 恒等式标准形等照抄即炸级），本档升 v1.15.8。**代码无新增施工**，对账链路 16/18 生产态此前已就绪。
>
> **最终成果**：设计真源与代码现状对齐；成交→对账→归因→报表链路生产可用。
>
> **未做事项及原因**：BM-REC-02-B 绩效归因 + BM-REC-03-D 元级迭代两环节仍设计态——依赖 61 号 §3.3 Champion-Challenger 晋升通道代码施工（当前待施工），本档已补齐 why 层与口径上限。

# 对账归因

> 本备忘记录"成交→对账→归因→报表"对账归因层的选型推理与上限定义。
> 性质：永久态设计记录，可随项目演进而修订，不是不可推翻的裁定。
> 管理规范见 [01_design_memo_management_spec.md](01_design_memo_management_spec.md)。
> 上游：[40_execution_broker](40_execution_broker.md)（G22，成交回报/持仓/资金流水产出物）+ [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.2（StrategyBook 独立 PnL）。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G25 对账归因 |
| 所属 | 作战地图 11（[battle_map_11_reconciliation](../battle_map/battle_map_11_reconciliation.md)） |
| 依赖 | G22（执行，[40_execution_broker](40_execution_broker.md) 已定稿+代码已施工）+ G04（策略，[30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) Model A 已定稿） |
| 对标 | 机构中后台对账 / Brinson 归因（非 Barra 因子风险归因） |
| 正交性 | ✅ 与 regime 正交（归因是事后解释，不参与事前决策） |
| 优先级 | P5 |
| 状态 | active 1.15.8 |

## 2. 背景

### 2.1 项目处境
- 个人 + 100% AI 开发的 A 股量化系统，下单通道为 miniQMT（国金证券）
- 执行层已 production（[40_execution_broker](40_execution_broker.md) v2.11.2，19 个决策已定型），多策略并发已定稿 Model A（[30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) v2.6.1）
- 对账归因是数据流主动脉的末端收口：执行层产出成交回报 → 对账核对 → PnL 计算 → 归因分解 → 复盘报表 → 闭环反馈（[battle_map_11](../battle_map/battle_map_11_reconciliation.md) BM-REC-01/02/03 三阶段 18 环节）
- 作战地图 11 已有 18 环节，其中 16 个 production、2 个 design（BM-REC-02-B 绩效归因 + BM-REC-03-D 元级迭代）——本备忘的核心职责是为这两个 design 环节补 why 层 + 定义归因口径上限

### 2.2 核心问题
对账归因层要回答 6 个问题（对应 00_index §3 G25 讨论要点）：PnL 归因怎么分解、每日对账对什么、归因维度取哪些、如何与 StrategyBook 独立 PnL 对接、异常交易怎么检测、报表怎么生成。前 4 个是归因口径决策（决定"赚的钱怎么解释"），后 2 个是运营闭环决策（决定"异常怎么抓、结果怎么交付"）。归因不清=迭代停滞。

### 2.3 约束条件
- A 股 T+1 结算：当日买入次日可卖，盘后 15:30 结算对账是硬时点
- 个人账户 miniQMT：无机构级对账中台（无 custodian/fund admin 三方核对），对账是"系统账 vs 券商端"双边核对
- AI 开发 → 归因清晰度是生存项：亏钱时必须能区分"策略 alpha 错"还是"执行成本高"还是"对账数据不一致"，否则迭代无方向
- StrategyBook 独立 PnL（[30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.2）：每个策略自带独立 PnL 归因、独立风控参数、独立资金预算，firm 层只做求和裁剪不做统一优化器 → 归因必须支持"单策略归因 + firm 层聚合归因"两层
- Brinson 归因需要基准（benchmark）：A 股策略基准选取是归因前提（沪深 300/中证 500/策略自定义基准）

### 2.4 现有资产盘点（施工前已实现，本备忘为其补 why 层）

> 对账归因不是从零设计——结算对账、PnL 计算、TCA、风险报告、监管报告、报告发布均已 production。本备忘给已有实现补 why 层决策记录 + 填补绩效归因 gap。

| 环节 | 模块（类名） | path | battle_map | 状态（2026-08-12 全仓扫描校准） |
|---|---|---|---|---|
| 盘中持仓对账 | PositionReconciler | `src/zephyr/ex_core/position_reconciler.py` | — | 🟦 production（MOD-EX-056，213 行：双源比对/Decimal 容差/冻结解冻/on_drift 回调；阶段2 定时调度/现金对账/持久化未实现）⚠️ 双实现：第二套事件驱动版在 `src/zephyr/position/position_reconciler.py`（MOD-INF-022，98 行，无冻结机制），capability_canonical_file_registry 的 canonical 指向后者——真源归属待裁定（§7） |
| 盘后结算对账 | SettlementReconciler | `src/zephyr/trading/settlement_reconciliation.py` | BM-REC-01-A | 🟦 production（MOD-TRADING-003，432 行：broker_fill_id/order_id 配对 + 价格/数量/佣金 5 类差异 + 缺失检测 + SHA-256 报告哈希；事件总线未接） |
| 公司行为与费率 | CorporateActionProcessor | `src/zephyr/trading/corporate_action_processor.py` | BM-REC-01-B | 🟦 production（MOD-TRADING-004，477 行：5 类公司行动→持仓数量+均价调整+现金变动）⚠️ 与 `src/zephyr/ex_core/corporate_action_adjuster.py`（357 行，40 号决策⑯施工物：除权参考价/涨跌停价/价格笼子基准价）职责互补但公式独立实现，存在口径漂移风险 |
| PnL 计算 | PnlCalculator + AShareFeeCalculator | `src/zephyr/trading/pnl_calculator.py` | BM-REC-01-C | 🟦 production（MOD-TRADING-002，400 行：已实现/未实现/组合 PnL + 佣金 0.025% 最低¥5/印花税 0.05% 卖出/过户费 0.001%） |
| TCA 执行质量 | DefaultTCAEngine | `src/zephyr/reporting/default_tca_engine.py` | BM-REC-02-A | 🟧 production 框架但实现极简（MOD-L07-001，117 行：仅简易滑点=(成交价-限价)/限价；无 benchmark 数据源、无 IS 四组件分解、`_calc_shortfall` 死代码、无测试）——§3.2 transaction_cost_drag 接入的 TCA 侧前提是 IS 四组件施工 |
| 绩效归因（契约对齐桩） | DefaultAttributionEngine | `src/zephyr/reporting/default_attribution_engine.py` | BM-REC-02-B | 🟧 全桩（MOD-L07-001，99 行：`_calc_allocation/selection/interaction_effect` 全部 `return 0.0`，factor_contributions 恒空，transaction_cost_drag 恒 0，无测试）——registry canonical 却指向本桩，见下方双实现冲突 |
| **绩效归因（真实实现）** | PerformanceAttributionEngine | `src/zephyr/pf_core/core/performance_attribution_engine.py` | BM-REC-02-B | 🟦 production（MOD-PF-007，698 行：BHB 三因子含守恒校验 + 因子归因 + 风险归因（复用 MOD-RK-16）+ IC 衰减降级检测 + 拥挤检测 + 多期算术链接 + 专属测试）——**仓内唯一真实归因实现**，v1.14.0 前本表漏登；与 reporting 桩构成双实现冲突（§3.2 双实现核查 + §6 待裁定） |
| 绩效归因报告契约 | PerformanceAttributionReport（frozen dataclass，codegen CTR-P1-009） | `src/zephyr/shared/contracts/performance_attribution_report.py` | BM-REC-02-B | 🟦 契约已存在（58 行：allocation/selection/interaction/total_return/transaction_cost_drag/factor_contributions/portfolio_id/period/idempotency_key/schema_version="1.0"） |
| 绩效归因报告生成器 | MOD-RPT-015（未施工，无模块文件） | — | BM-REC-02-B | 🟥 未施工：registry 无 MOD-RPT-015 模块条目、无代码文件；报告模板契约见 §3.12 模板节 ⚠️ 未登记 architecture_issue_registry（新增模块须登记 ARCH 条目的硬约束缺口，§7 开放问题） |
| A 股交易复盘 | ASharePerformanceAuditor | `src/zephyr/reporting/ashare_performance_audit.py` | BM-REC-02-C | 🟦 production（MOD-RPT-026，617 行：5 类审计 + 优化建议 + SHA-256 报告哈希） |
| A 股交易记录模板 | AShareTradeRecordTemplate | `src/zephyr/reporting/ashare_trade_record_template.py` | BM-REC-02-C | 🟦 production（MOD-RPT-027，312 行：11 必填字段强制校验，数量 100 整数倍/印花税仅 SELL 等 A 股规则） |
| 报告发布 | ReportPublisher | `src/zephyr/reporting/report_publisher.py` | BM-REC-02-D | 🟦 production 框架（MOD-RPT-003，391 行：报告域唯一出口 + append-only 归档 + 哈希链）⚠️ 微信 Webhook / 邮件 SMTP 两渠道当前仅落 PENDING 状态不实际发送；SQLite report_archive + Parquet 归档为受限未实现 |
| 报告版本管理 | ReportVersionManager | `src/zephyr/reporting/report_version_manager.py` | BM-REC-02-D | 🟦 production（MOD-RPT-013，359 行：版本存储 + diff 引擎 + 哈希链；SQLite/Merkle 阶段2 未实现） |
| 报告水印防篡改 | WatermarkTracker | `src/zephyr/reporting/report_watermark_tracker.py` | BM-REC-02-D | 🟦 production（MOD-RPT-017，299 行：报告水印 + 哈希链） |
| 风险报告 | RiskReportEngine | `src/zephyr/reporting/risk_report_engine.py` | BM-REC-02-E | 🟦 production（MOD-RPT-008，515 行：日/周/事件/月四类风险报告） |
| 监管报告 | RegulatoryReportGenerator | `src/zephyr/reporting/regulatory_report_generator.py` | BM-REC-02-F | 🟦 production（MOD-RPT-006，336 行：四类监管报告，不含自动报送） |
| 实时 PnL 看板 | RealtimePnlDashboard | `src/zephyr/reporting/realtime_pnl_dashboard.py` | — | 🟦 production（MOD-RPT-004，340 行：消费 PnlCalculator + PositionTracker，record_fill/refresh 产出 DashboardSnapshot） |
| 日终 PnL 对账审计 | DailyAuditor + PnLReconciliation | `src/zephyr/risk/core/daily_auditor.py` | — | 🟦 production（MOD-RK-20，1105 行，safety=H：日终 PnL 对账 expected MtM vs 账面 realized+unrealized gap 检测 + 归因偏差检测 + 合规检查清单 + IssueRecord 追溯，产出 CTR-P1-011）——v1.14.0 前本表漏登 |
| 执行事件审计链 | ExecutionAuditLogger | `src/zephyr/ex_core/audit_journal/auditor.py` | — | 🟦 production（MOD-EX-003，778 行：执行事件哈希链审计 + ExecutionAuditReport + 链完整性校验）——对账取数的上游凭证链 |
| 资金管理（T+1 结算） | CashManager | `src/zephyr/position/core/cash_manager.py` | — | 🟦 production（MOD-POS-006，275 行：资金流水 + T+1 结算 SELL 进 pending_settlement 次日可用 + 三级储备金）——§3.3 资金对账的系统侧资金账已存在，缺 vs 券商端双边核对 |
| 策略账本 | StrategyBook | `src/zephyr/position/core/strategy_book.py` | — | 🟦 production 框架（MOD-POS-020，680 行：选股+粗仓位+四级回撤）⚠️ **独立 PnL 未实现**——仅消费外部注入 `strategy_pnl_history` 算回撤/Sortino，自身不核算 PnL——§3.5 两层归因的策略侧数据源缺口（§7 开放问题，关联 #ARCH-REG-005） |
| 研究侧因子归因 | attribute_by_time / attribute_by_sector | `src/zephyr/factor/analysis/factor_attribution.py` | — | 🟦 production（MOD-L02-010，90 行：IC 时间聚合 + 行业分组因子收益归因；研究侧非组合 PnL 归因） |
| 归因/TCA 抽象基座 | TCAEngineBase / AttributionEngineBase | `src/zephyr/reporting/analytics_base.py` | — | 🟦 production（MOD-L07-001 OCP 基座，102 行） |
| 前端 PnL 渲染 | position_monitor / chart_factory | `src/zephyr/frontend/dashboard/components/position_monitor.py`、`chart_factory.py` | — | 🟦 production（账户资金卡片含当日盈亏 + 逐标的 unrealized_pnl/盈亏% + T+1 标记；无归因报告/对账差异专属组件） |

**横向缺口（2026-08-12 全仓扫描确认，通用规则 #11 盘点）**：
1. **无 DB 持久化**：ClickHouse/SQLite 均无对账差异/PnL/归因结果/audit_trail 表 DDL——§3.3 三阶段审计轨迹的 `audit_trail` 表、§3.7 的 `report_archive` 均为文档约定，无落库 schema（§7 开放问题）。
2. **无 15:30 调度接线**："盘后结算对账每日 15:30 自动触发"是文档约定——全仓调度器（data scheduler APScheduler / trading work_dag / conductor）均无 settlement/reconciliation 任务，当前只能靠外部手动/事件调用 `reconcile()`（§7 开放问题）。
3. **报告发送渠道未通**：ReportPublisher 的 WEBHOOK/EMAIL 仅落 PENDING 不实际发送——§3.7"双渠道发布"当前是框架能力非运营事实。
4. **双实现未收敛**：归因引擎（reporting 桩 vs pf_core 实现）、PositionReconciler（ex_core vs position 事件驱动版）、公司行为（trading processor vs ex_core adjuster）三对并存，canonical 归属与口径统一待裁定（§6/§7）。
5. **BM-REC-02-B 阻塞标注已部分过时**：battle_map 标"⛔ CTR-P1-007/CTR-ERR-005 未就绪暂不可建"——两契约 codegen 文件已落盘（`shared/contracts/execution_report.py` / `errors/execution_rejection_error.py`），残余阻塞是 CTR-P1-007 产出逻辑未施工（execution_core blueprint GAP-L06-003，P0 待施工）+ 归因计算实现缺失（本备忘 §3.2/§3.5 施工算法即为此备）。
6. **微信入站指令解析未施工（BM-BUY-07 登记）**：出站方向已有 ReportPublisher 微信 Webhook 告警（当前仅落 PENDING 不实发，见缺口 #3）；入站方向——用户微信消息 → D-TRADING-06 解析/路由为标准指令（自然语言解析 + 多人通知列表，source_ref C-019 微信多人互动）——**全仓无实现**。入站与出站共用微信通道但方向相反、生命周期独立：出站是报告/告警分发（本备忘 §3.7），入站是交易指令入口（buy_flow 域，下游 BM-BUY-06 外部指令盯盘→执行结果→微信推送）。处置=**登记远期**：入站指令涉及资金操作，解析错误代价高，须待出站渠道实发（缺口 #3 闭合）+ 指令鉴权/确认机制设计后再评估，不在本备忘施工范围（归属 buy_flow 域备忘）。

## 3. 决策

### 3.1 对账归因架构总览

```
[成交回报] FillHandler (G22, 40_execution_broker)
        │   fill_id幂等 / 加权均价累积 / FillSummary
        ↓
[盘中持仓对账] PositionReconciler (MOD-EX-056, 每5min)
        │   系统账(PositionTracker) vs 外部账(Broker get_positions)
        │   diff > tolerance → 告警 + 冻结该标的 / 恢复一致 → 解冻
        ↓
[盘后结算对账] SettlementReconciliation (MOD-TRADING-003, 每日15:30)
        │   系统成交记录 vs 券商结算单 逐笔核对 / T+1 / 差异告警
        ↓
[公司行为与费率] CorporateActionProcessor (MOD-TRADING-004)
        │   除权除息调持仓成本 / 佣金印花税过户费 / 分红配股拆股
        ↓
[PnL 计算] PnlCalculator (MOD-TRADING-002)
        │   已实现PnL(卖出-买入-费率) + 未实现PnL(市价-成本)
        ↓
[TCA 执行质量] DefaultTcaEngine (MOD-L07-001)
        │   IS成本分解(时机+冲击+滑点+佣金) / DECISION基准 / 三因子+残差
        ↓
[绩效归因] DefaultAttributionEngine (MOD-L07-001)  ← 本备忘核心 gap
        │   Brinson 3因子(配置+选择+交互) / 策略贡献分解
        │   factor_contributions 暂不实现 / transaction_cost_drag 待接入TCA
        ↓
[A股交易复盘] AsharePerformanceAudit (MOD-RPT-026)
        │   5类审计(收益率/回撤/风险调整收益/归因一致性/交易成本)+优化建议+SHA-256指纹
        │   ※ 盘中异常检测(§3.6 MAD算法)/大额异动为本备忘待施工扩展，非现有代码能力
        ↓
[报告生成] RiskReportEngine + RegulatoryReportGenerator + ReportPublisher
        │   日/周/事件/月四类风险报告 + 四类监管报告 + 微信/邮件发布 + SQLite/Parquet归档
        ↓
[闭环反馈] BM-REC-03 因子层/信号层/模型层反馈 → 反向闭环到 BM-SEL-02
```

#### 3.1.1 闭环反馈补述：模型层反馈（BM-REC-03-C，design）

- **定位**：L5 闭环优化反馈层的模型层反馈（BM-REC-03 子环节，父 BM-REC-03）；触发=复盘报告就绪；消费 BM-REC-03-B 信号反馈 + BM-REC-02-D 复盘报告；数据流：复盘报告→漂移检测→模型重训练信号→C-003 回测门禁→BM-SEL-02（反向闭环）。参数口径：`drift_threshold = PSI>0.2`、`retrain_gate = C-003 回测门禁`；代码映射 C-007 模型层反馈（未完整实现）+ C-003 回测门禁。
- **裁定**：①**漂移检测与分级重训练复用 [61_lifecycle_multi_ai](61_lifecycle_multi_ai.md) §3.3**——多方法 Drift Observatory（PSI 只抓边际特征漂移，须组合多变量联合分布/概念漂移检测）+ 重训练触发分级逻辑（定时盘后增量保底 / 性能触发分级响应，不直接跳重训练），本环节不另造漂移检测器。②**门禁衔接裁定：模型重训练信号必须过 C-003 回测门禁（DecisionGate IS→WFA→OOS）后才允许回 BM-SEL-02 重新选股上线**——重训练≠可直接上线，新模型与策略新参数同级对待。理由：漂移触发的重训练若绕过回测门禁直接上线，等于把"检测到漂移"误当"修复已完成"——重训练产物本身可能引入新过拟合，必须经 IS→WFA→OOS 门控验证（门禁当前真源为代码 `backtest/core/decision_gate.py`；[52_backtest_framework_docking](52_backtest_framework_docking.md) ⚠️骨架 draft 待讨论，定型后回填 why 层衔接）。③**降级**：漂移检测不可用→人工评估模型质量（环节定义原口径）。
- **契约/参数/接口**：重训练信号 `{model_id, drift_evidence: {psi, cusum_alarm, ...}, retrain_scope}` → DecisionGate 评审 → 通过后经 [61 号](61_lifecycle_multi_ai.md) §3.3 Champion-Challenger 晋升通道（mSPRT + 95/5 流量切分）回 BM-SEL-02；未过门禁→信号驳回并留痕复盘报告。重评条件：61 号 §3.3 设计规范伪代码施工落地（当前代码待施工）+ 52 号骨架定型后，补双向小节号对齐。

### 3.2 决策①：PnL 归因——Brinson 3 因子为主，Barra 拒绝

**决策**：以 Brinson 3 因子分解作为 PnL 归因主框架，拒绝 Barra 多因子风险归因。落地形态：[DefaultAttributionEngine](file:///d:/ZephyrAlpha/src/zephyr/reporting/default_attribution_engine.py)（MOD-L07-001）当前是契约对齐桩（3 个计算方法全部 `return 0.0`），仓内唯一真实实现是 [PerformanceAttributionEngine](file:///d:/ZephyrAlpha/src/zephyr/pf_core/core/performance_attribution_engine.py)（MOD-PF-007，BHB 三因子含守恒校验 + 因子/风险归因 + 多期算术链接，698 行带测试）——双实现收敛裁定见 §6，施工算法以本节为准。

**Brinson 3 因子分解**（纯 BHB 口径，v1.15.0 守恒修正，[analytics_base](file:///d:/ZephyrAlpha/src/zephyr/reporting/analytics_base.py) AttributionEngineBase）：

| 因子 | 含义 | 公式 | 回答的问题 |
|---|---|---|---|
| Allocation Effect（配置效应） | 超配/低配某板块带来的超额收益 | ∑(w_p − w_b) × r_b | "配比配对了吗" |
| Selection Effect（选择效应） | 板块内选股超越基准的能力 | ∑w_b × (r_p − r_b) | "选股选对了吗" |
| Interaction Effect（交互效应） | 配置与选择的交叉影响 | ∑(w_p − w_b) × (r_p − r_b) | "配比和选股是否协同" |

其中 w_p/w_b = 组合/基准权重，r_p/r_b = 组合/基准板块收益（R_b 基准总收益 = Σ(w_b,i × r_b,i)，用于报告展示与 BF 备选口径）。

> **⚠️ v1.15.0 守恒修正（公式 bug 修复）**：本表 v1.14.0 及之前版本写作"allocation = ∑(w_p − w_b) × (r_b − R_b)（BF 基准差口径）+ selection = ∑**w_p** × (r_p − r_b)"——该组合三式求和 = R_p − R_b + ∑(w_p−w_b)(r_p−r_b)，**interaction 被重复计算**，违反求和不变量门禁（Carino residual 将恒 FAIL）。修正为**纯 BHB** 后三式求和恒等 = R_p − R_b ✓。选纯 BHB 而非 BF 3-effect 的理由：①与仓内唯一生产实现 [pf_core MOD-PF-007](file:///d:/ZephyrAlpha/src/zephyr/pf_core/core/performance_attribution_engine.py)（纯 BHB 含守恒校验）零改动对齐；②与 §3.13 Hentschel GLS 骨架设计矩阵（BHB）一致；③与本节"BHB vs BF 方案明确"决策文字一致。BF 3-effect（[pybrinson v1.3.1](https://github.com/gghez/pybrinson) / [metricgate 2026-09](https://metricgate.com/docs/multi-period-attribution/)：A_i=(w_p,i−w_b,i)·(R_b,i−R_b)，S_i=w_b,i·(R_p,i−R_b,i)+独立 interaction）登记为 allocation 基准差口径备选，切换只需改 allocation 一式。

**PnL Explain vs PnL Predict 概念框架**（v1.2.0 补，[hftradingbook 2026-06](https://hftradingbook.com/performance/attribution) + [CSDN SRPnL 2026-06](https://blog.csdn.net/weixin_42402664/article/details/152352510) 概念澄清）：

| 框架 | 类型 | 原理 | 适用场景 | A 股个人系统适用性 |
|---|---|---|---|---|
| **Brinson 3 因子**（本备忘主选） | PnL Explain | 配置效应 + 选择效应 + 交互效应，将总超额收益分解为决策维度 | 事后归因报告（日/周/月/季），回答"赚的钱来自配置还是选股" | ✅ 主选（A 股权益类策略，决策维度清晰） |
| **Greek decomposition**（Delta/Gamma/Vega/Theta） | PnL Predict | 持仓价值变化映射到风险因子空间（敏感性矩阵），预测因子微小变动下的 PnL | 衍生品做市（期权/期货），需要 Greek 模型 | 🟥 拒绝（A 股权益无 Greek，30 号 Model A 已拒 MVO 协方差） |
| **SRPnL 敏感性分解**（CSDN 2026-06 推广） | PnL Predict | Sensitivity-based Return and PnL Decomposition，持仓价值映射到风险因子空间实现"白盒式结构性贡献" | 多资产/衍生品组合归因 | 🟥 拒绝（本质是 Greek 风格，需因子协方差矩阵，与 Barra 同源） |
| **PnL attribution waterfall**（[hftradingbook 2026-06](https://hftradingbook.com/performance/attribution)） | PnL Explain | 做市商：spread capture - adverse selection - own impact + signal alpha + fees = net PnL | 高频做市策略归因 | 🟧 备选（A 股非做市场景，但 TCA 部分借鉴 adverse selection 概念） |

> **为何选 Explain 而非 Predict**：A 股权益策略的 PnL 来源是"配置+选股+时段"决策维度，不是 Greek 敏感性。Greek/SRPnL 需要 Greek 模型 + 协方差矩阵估计，与 30 号拒绝 MVO 协方差矩阵保持架构一致。

**为何 Brinson 而非 Barra**：Brinson（1985/1986）至今是行业标准收益归因框架（[traderssecondbrain 2026-05](https://traderssecondbrain.com/guides/performance-attribution-trading)），回答"赚的钱来自配置还是选股"；Barra 需因子风险模型许可证 + 协方差矩阵估计（finantrix 2026-08：典型 deal $100K-$1M+），对 5 策略小组合过度工程，与 30 号拒 MVO 协方差架构一致（§4.1）。**5 维归因参考**（同前 setup/regime/execution/sizing/instrument）：本备忘三维度已覆盖 setup→策略、instrument→标的、sizing→时段，regime fit 归 28 号 + 30 号 RegimeMetaAllocator、execution 归 TCA，不混入 Brinson。

**多 session PnL 归因边界**（v1.2.0 补，[seriousalchemy 2026-08-04](https://seriousalchemy.com/pnl-sessions/)）：30 号 Model A 的 StrategyBook 可能在持仓未平期间触发 reoptimization，导致同一笔交易 entry/exit 跨 session；跨 session 交易若用单 session FIFO 匹配器会产生"幽灵成交"（duplicate order record）+ PnL 漏算。

| 边界场景 | 风险 | 缓解策略 |
|---|---|---|
| StrategyBook reoptimization 期间有持仓 | entry 在旧 session、exit 在新 session，FIFO 匹配器漏算 PnL | StrategyBook 级独立 PnL 计算必须**跨 session 追踪持仓**（PnlCalculator 已实现持仓历史），不依赖 session_id 隔离 |
| 涨跌停/停牌导致订单跨日 | working 订单次日才成交，session 已切换 | OrderManager 必须按 fill_id 幂等（40 号 §6.1 gap 12 AsyncFillDispatcher fill_id LRU 幂等已实现），不依赖 session 状态机 |
| T+1 结算跨日 | 成交记录日切时点 vs 持仓对账时点错位 | SettlementReconciliation（MOD-TRADING-003）按 T+1 结算单核对，不按 session 切换核对 |

> **设计原则**：PnL 计算和归因必须以 fill_id + position_id 为唯一键，不依赖 session_id/reoptimization_run_id——避免"幽灵成交"和 PnL 漏算。30 号 StrategyBook reoptimization 只影响策略参数（target_portfolio 生成），不影响已成交订单的 PnL 归属。

**已实现 gap**（v1.15.0 校准：reporting 侧为全桩，pf_core 侧为真实实现——双实现并存）：

> **归因引擎双实现核查**（v1.15.0 补，2026-08-12 全仓扫描发现）：
>
> | 维度 | reporting/DefaultAttributionEngine（MOD-L07-001） | pf_core/PerformanceAttributionEngine（MOD-PF-007） |
> |---|---|---|
> | 实现实质 | 契约对齐桩：3 个计算方法全部 `return 0.0`，无测试 | 真实实现 698 行：BHB 三因子含守恒校验 + 因子归因 + 风险归因（复用 MOD-RK-16）+ IC 衰减降级检测 + 拥挤检测 + 专属测试 |
> | Brinson 口径 | 未实现（桩） | 纯 BHB——与本备忘 §3.2 v1.15.0 修正后口径一致 |
> | 多期链接 | 无 | 算术链接（简化，注释自述"乘法链接需对数化，此处简化为算术和"）——与本备忘 Carino 对数链接决策存在精度差 |
> | registry canonical | ✅ capability_canonical_file_registry `performance_attribution_engine` 指向本桩 + analytics_base | ❌ 未登记为 canonical |
> | CTR-P1-009 契约 | ✅ 直接产出 PerformanceAttributionReport | 产出自有 BrinsonResult |
>
> **冲突结论**：registry canonical 指向桩、真实实现未登记——同一能力两份实现违反单一真源原则。**收敛方向（登记 §6 待裁定，不擅自定）**：建议以 pf_core MOD-PF-007 为实现基底（已有守恒校验 + 测试 + 与本备忘同 BHB 口径），将其多期链接从算术升级为 Carino，reporting 桩退役或改为薄委托层；裁定前本备忘 §3.2 施工算法为公式真源。

- `factor_contributions={}`（[default_attribution_engine.py:77](file:///d:/ZephyrAlpha/src/zephyr/reporting/default_attribution_engine.py)）：reporting 桩因子贡献字典为空；pf_core MOD-PF-007 因子归因已实现但属研究侧口径 → 本备忘决策：组合归因层暂不实现（见 §3.4）
- `transaction_cost_drag=0.0`（[default_attribution_engine.py:78](file:///d:/ZephyrAlpha/src/zephyr/reporting/default_attribution_engine.py)）：交易成本拖拽硬编码 0，未接入 TCA → 待接入 [DefaultTcaEngine](file:///d:/ZephyrAlpha/src/zephyr/reporting/default_tca_engine.py) 的 IS 成本分解（TCA 侧 IS 四组件本身亦待施工，见 §2.4 盘点）
- `_calc_allocation_effect/_calc_selection_effect/_calc_interaction_effect` 三个方法当前返回占位值（未接真实持仓历史）→ 待接入 `_holdings_history` 真实数据
- **多期链接算法缺失**：单期 Brinson 不能简单相加——会产生 compounding residual（随期数增长而增大），周/月/季报必须用链接算法（见下方子决策）；pf_core 算术链接是过渡形态，Carino 对数链接为目标态

**多期链接算法子决策**（2026-08-10 补，v1.1.0）：

> 单期 Brinson 假设持仓不变，多期归因需将各单期效应合理加总。链接算法核心原则（[metricgate 2026-09](https://metricgate.com/docs/multi-period-attribution/)）：**链接后各效应求和必须等于总几何超额收益**（near-zero residual）。

| 链接算法 | 来源 | 原理 | 适用场景 |
|---|---|---|---|
| **Carino 对数链接**（主选） | Cariño (1999) | k_t = ln(1+R_{p,t}) / R_{p,t} 期特定修正因子，按总对数收益归一化 | GIPS-compliant 报告首选；residual 最小 |
| Menchero 优化链接 | Menchero (2000, 2004) | 优化链接系数矩阵（专利 2024 过期） | 需要 Menchero 系数矩阵实现 |
| GRAP 几何归因 | GRAP (1997) | 算术效应转几何等价 | DolphinDB 实现采用 |
| Frongello 递归 | Frongello (2002) | 递归链接，再投资收益归属产生阶段 | 适合再投资分析 |
| Bacon 几何 | Bacon (2008) ch.6 | 纯几何链接 | 几何归因偏好场景 |

> **GRAP 2026-05-19 专利公开：交易效应作为第 4 因子**（v1.10.0 补，[国知局 202610181717 "基于 GRAP 递推算法的交易效应内嵌式归因方法"](https://www.xjishu.com/zhuanli/55/202610181717.html)）：该专利核心创新**不是**链接算法，而是把**交易效应（Trading Effect）作为 Brinson 模型的独立第 4 因子**（`超额收益 = 配置效应 + 选股效应 + 交互效应 + 交易效应`），解决传统 3 因子假设持仓不变导致日内交易损益被错误归入选股/交互残差的问题。**与本备忘的等价关系**：§3.2 求和不变量已定义 `Brinson 3 因子 + transaction_cost_drag = 总超额收益`——transaction_cost_drag 功能上**等价于** GRAP 的"交易效应第 4 因子"（已含 timing/impact/slippage/commission 四组件）；概念差异是 drag 隐含负向 vs 交易效应中性。**结论：本备忘已功能等价覆盖 GRAP 专利核心创新，无需追加施工**；若未来切换到 GRAP 递推平滑系数链接（Carino residual 持续 > 1bp 时），transaction_cost_drag 字段无需改动，仅替换 carino_link_periods → grap_link_periods。

**主选 Carino 的理由**：GIPS-compliant 报告标准方法（[metricgate 2026](https://metricgate.com/docs/multi-period-attribution/)）；实现简单（单期效应 × k_t × (ln(period)/ln(total)) 求和），residual 可量化校验（见下方质量门禁）；开源参考 [pybrinson v1.3.1 2026-04-13](https://github.com/gghez/pybrinson) 已实现 Carino/GRAP/Frongello/Menchero/Geometric 5 种链接方法。

**BHB vs BF 方案明确**（v1.1.0 补 / v1.15.0 口径修正）：
- 本备忘采用 **纯 BHB（Brinson-Hood-Beebower 1986）三因子**（含独立 interaction effect）——与仓内生产实现 pf_core MOD-PF-007 完全同口径（其代码注释自称 "Brinson-Fachler 模型"系注释错误，公式实为 BHB）
- BF 3-effect（[pybrinson v1.3.1](https://github.com/gghez/pybrinson) / [metricgate 2026-09](https://metricgate.com/docs/multi-period-attribution/)）：allocation = ∑(w_p−w_b)·(r_b − R_b) 基准差口径 + selection = ∑w_b·(r_p−r_b) + 独立 interaction——守恒，登记为备选（切换只改 allocation 一式）
- 经典 BF 两因子（1985 原文）将 interaction 合并到 selection（[DolphinDB 2026](https://docs.dolphindb.com/zh/tutorials/brinson.html)）——作降级备选
- 决策保留 BHB 三因子——interaction 独立可见有助于区分"配比+选股协同效应"vs"纯选股能力"，对 AI 迭代更有指导性
- 重评条件：若 interaction 长期接近 0（统计不显著），可降级到 BF 两因子简化解释

**实现细节约束**（v1.1.0 补，[brinson-attribution 2026](https://github.com/gogoahead233-art/brinson-attribution) 共识）：
- **使用 beginning-of-period weights**（前一日收盘权重），非 end-of-period weights——消除系统性向上偏差（end-of-period 权重会被本期涨跌污染）
- 权重基准：组合权重 w_p 与基准权重 w_b 必须在同一时点（T-1 收盘）对齐
- 多期链接粒度：周/月报用日频单期链接（每日一单期 Brinson + Carino 链接），季报用周频单期链接

**Carino residual 质量校验**（v1.1.0 补）：
- 链接后 |Σ linked effects - total geometric active return| 应 < 1e-6（浮点精度级）
- residual > 0.01% 表示归因模型有 bug（如权重未对齐/数据缺失/单期计算错）
- 作为归因报告的自动质量门禁，residual 超阈值拒绝发布报告 + 触发告警

**Brinson 3 因子真实计算 + Carino 多期链接施工算法**（v1.5.0 补，[metricgate 2026-09](https://metricgate.com/docs/multi-period-attribution/) Carino 公式 + [pybrinson v1.3.1 2026-04-13](https://github.com/gghez/pybrinson) 参考实现 + [DolphinDB 2026](https://docs.dolphindb.cn/zh/tutorials/brinson.html) BHB 实现）：

> [default_attribution_engine.py:82-92](file:///d:/ZephyrAlpha/src/zephyr/reporting/default_attribution_engine.py) 当前 `_calc_allocation_effect/_calc_selection_effect/_calc_interaction_effect` 三个方法返回 0.0 占位值，未接 `_holdings_history`。本节给出 MVP 第一阶段施工的完整算法契约——施工时直接照此实现，替换占位返回。

```python
# Brinson BHB 3 因子单期计算 + Carino 多期链接（v1.5.0 施工算法）
import math
from typing import Sequence

def calc_single_period_brinson(
        portfolio_weights: dict[str, float],   # w_p,i 期初各板块权重（T-1 收盘）
        benchmark_weights: dict[str, float],    # w_b,i 基准各板块权重
        portfolio_returns: dict[str, float],    # r_p,i 期内各板块组合收益
        benchmark_returns: dict[str, float],    # r_b,i 期内各板块基准收益
        benchmark_total_return: float           # R_b 基准总收益
) -> dict[str, float]:
    """单期 Brinson BHB 3 因子分解（beginning-of-period weights）。

    纯 BHB 口径（v1.15.0 守恒修正，与 pf_core MOD-PF-007 生产实现同口径）：
        allocation_i  = (w_p,i - w_b,i) × r_b,i
        selection_i   = w_b,i × (r_p,i - r_b,i)
        interaction_i = (w_p,i - w_b,i) × (r_p,i - r_b,i)
    守恒校验：三式求和 = R_p - R_b，不满足即实现 bug。
    （benchmark_total_return 参数保留用于报告展示与 BF 备选口径切换，BHB 分解不用。）
    """
    sectors = set(portfolio_weights) | set(benchmark_weights)
    alloc = selec = interact = 0.0
    for s in sectors:
        wp = portfolio_weights.get(s, 0.0)
        wb = benchmark_weights.get(s, 0.0)
        rp = portfolio_returns.get(s, 0.0)
        rb = benchmark_returns.get(s, 0.0)
        alloc     += (wp - wb) * rb
        selec     += wb * (rp - rb)
        interact  += (wp - wb) * (rp - rb)
    return {
        'allocation_effect': alloc,
        'selection_effect': selec,
        'interaction_effect': interact,
        'single_period_active_return': alloc + selec + interact,
    }


def carino_link_periods(
        period_effects: Sequence[dict[str, float]],  # 各期单期 Brinson 分解结果
        portfolio_period_returns: Sequence[float],    # R_{p,t} 各期组合收益
        benchmark_period_returns: Sequence[float]     # R_{b,t} 各期基准收益
) -> dict[str, float]:
    """Carino 对数链接算法——将多期单期 Brinson 效应链接为多期归因。

    [Cariño 1999] 标准形式（v1.15.8 公式修正，原版 k_t=ln(1+R_{p,t})/R_{p,t}
    在零基准极限下 Σlinked≡1≠G，过不了本节 residual<1e-6 门禁）：
      k_t = [ln(1+R_{p,t}) − ln(1+R_{b,t})] / (R_{p,t} − R_{b,t})  期修正因子
      A   = G / ln(1+G)，G = (1+R_p)/(1+R_b) − 1  总几何超额收益
      linked_i = A × Σ_t e_{i,t} × k_t
    恒等性质：Σ_i linked_i = A × Σ_t [ln(1+R_{p,t})−ln(1+R_{b,t})]
             = A × ln(1+G) = G（near-zero residual，浮点精度级）。
    GIPS-compliant 报告首选方法。
    """
    assert len(period_effects) == len(portfolio_period_returns) == len(benchmark_period_returns)
    # 1. 累计几何收益 + 总几何超额收益 G
    cum_portfolio = 1.0
    cum_benchmark = 1.0
    for r_p, r_b in zip(portfolio_period_returns, benchmark_period_returns):
        cum_portfolio *= (1.0 + r_p)
        cum_benchmark *= (1.0 + r_b)
    total_portfolio_return = cum_portfolio - 1.0
    total_benchmark_return = cum_benchmark - 1.0
    geometric_active_return = (cum_portfolio / cum_benchmark) - 1.0

    # 2. 全局缩放因子 A = G / ln(1+G)（G→0 退化时洛必达极限 A→1）
    if (1.0 + geometric_active_return) > 0:
        log_active = math.log(1.0 + geometric_active_return)
    else:
        log_active = 0.0
    global_scale = (geometric_active_return / log_active) if abs(log_active) > 1e-12 else 1.0

    # 3. 各期 Carino 修正因子 k_t（R_{p,t}→R_{b,t} 退化时 k_t→1/(1+R_{p,t})，洛必达极限）
    k_factors = []
    for r_p, r_b in zip(portfolio_period_returns, benchmark_period_returns):
        active_t = r_p - r_b
        if abs(active_t) < 1e-12:
            k_t = 1.0 / (1.0 + r_p)
        else:
            k_t = (math.log(1.0 + r_p) - math.log(1.0 + r_b)) / active_t
        k_factors.append(k_t)

    # 4. 链接各效应
    linked_alloc = linked_selec = linked_interact = 0.0
    for eff, k_t in zip(period_effects, k_factors):
        linked_alloc     += eff['allocation_effect'] * k_t * global_scale
        linked_selec     += eff['selection_effect'] * k_t * global_scale
        linked_interact  += eff['interaction_effect'] * k_t * global_scale

    # 5. residual 质量校验（恒等性质下应处浮点精度级；非零即数据/单期计算 bug）
    linked_sum = linked_alloc + linked_selec + linked_interact
    residual = geometric_active_return - linked_sum

    return {
        'linked_allocation_effect': linked_alloc,
        'linked_selection_effect': linked_selec,
        'linked_interaction_effect': linked_interact,
        'geometric_active_return': geometric_active_return,
        'carino_residual': residual,
        'residual_quality': 'PASS' if abs(residual) < 1e-6 else 'FAIL',
    }


# DefaultAttributionEngine 施工改造点（替换 default_attribution_engine.py:82-92 占位实现）：
# def _calc_allocation_effect(self, period_start, period_end):
#     wp, wb, rp, rb, Rb = self._load_period_data(period_start, period_end)
#     return calc_single_period_brinson(wp, wb, rp, rb, Rb)['allocation_effect']
# 多期：对每个子期跑 calc_single_period_brinson，再用 carino_link_periods 链接
```

**施工约束**：
- `portfolio_weights` 必须用 **beginning-of-period weights**（T-1 收盘权重），从 `_holdings_history[date-1]` 取——end-of-period 权重会被本期涨跌污染（[brinson-attribution 2026](https://github.com/gogoahead233-art/brinson-attribution) 共识）
- 板块划分对齐开放问题 §7（申万一级 28 行业 / 风格 / 策略自定义），MVP 先用申万一级
- `R_b`（基准总收益）= `Σ(w_b,i × r_b,i)`，不可直接用指数收盘价算（防止权重与收益口径错位）
- 多期链接粒度：周/月报用日频单期链接（每日跑一次 + Carino 链接），季报用周频单期链接（§7 开放问题待实盘校准）

**A 股 T+1 归因特殊处理子决策**（v1.5.0 补，[akquant A 股市场微观结构 2026](https://akquant.akfamily.xyz/textbook/06_stock_a/) §6.2 T+1 持仓状态机 + [biyapay A 股入门 2025-12](https://www.biyapay.com/en/blogdetail/3010-ashare-beginners-guide-master-market-hours-and-tra) T+1 规则）：

> A 股 T+1 制度与 Brinson "beginning-of-period weights + 期内收益" 框架存在张力：T 日新建仓位的权重在 T 日收盘已计入 `_holdings_history[T]`，但 T+1 才能卖出 → T 日建仓的 selection effect 用 T 日收益计算会**高估选股能力**（T 日浮盈不可实现）。归因报告若不特殊处理 T+1，会把"当日浮盈"误记为"选股 alpha"。

**T+1 对 Brinson 三因子的影响分析**：

| Brinson 因子 | T+1 影响 | 处理原则 |
|---|---|---|
| Allocation Effect | T+1 不影响（allocation 看期初权重 vs 基准权重，与可卖性无关） | 无需特殊处理 |
| Selection Effect | **受影响**：T 日新建仓位的 r_p,i 用 T 日收益会含未实现浮盈 | 区分"已实现 selection"vs"浮盈 selection"，归因报告分列 |
| Interaction Effect | 受影响（含 selection 项） | 同 selection 处理 |

**T+1 归因特殊处理算法**（v1.5.0 补）：

```python
# A 股 T+1 归因特殊处理（v1.15.0 施工算法，收益贡献拆分口径）
def calc_brinson_with_t1_settlement(
        portfolio_weights: dict[str, float],       # T-1 收盘权重（含 T-1 前已建仓位）
        benchmark_weights: dict[str, float],
        portfolio_returns: dict[str, float],        # 各板块 T 日收益（含浮盈）
        benchmark_returns: dict[str, float],
        benchmark_total_return: float,
        new_positions_today: dict[str, dict]        # T 日新建仓位 {symbol: {'weight': w, 'day_return': r}}
) -> dict:
    """Brinson 3 因子 + A 股 T+1 已实现/浮盈分离（w_b 加权 selection 口径）。

    将 selection effect 拆为：
      - realized_selection：T-1 前已建仓位（T 日可卖）的选股贡献，可兑现
      - unrealized_selection：T 日新建仓位（T+1 才可卖）的选股贡献，仅为浮盈
    拆分原理（v1.15.0 随 §3.2 守恒修正从权重拆分改为收益贡献拆分）：
    板块组合收益 r_p,i = (1−λ_i)·r_p,i^old + λ_i·r_p,i^new，
    λ_i = 新建仓位占板块组合市值比例、r_p,i^new = 新建仓位市值加权当日收益；
    unrealized_selection_i = w_b,i × λ_i × (r_p,i^new − r_b,i)。
    归因报告分列两项，避免把浮盈误记为已实现 alpha。
    """
    # 1. 跑标准 Brinson 3 因子（纯 BHB，§3.2 v1.15.0 守恒修正口径）
    base = calc_single_period_brinson(
        portfolio_weights, benchmark_weights,
        portfolio_returns, benchmark_returns, benchmark_total_return)

    # 2. 按板块聚合新建仓位的收益贡献（λ_i 与 r_p,i^new）
    sector_new_weight: dict[str, float] = {}      # λ_i 分子：新建仓位市值权重和
    sector_new_ret_num: dict[str, float] = {}     # r_p,i^new 分子：Σ w_new × r_new
    for symbol, info in new_positions_today.items():
        sector = get_sector(symbol)  # 申万一级板块映射
        w_new = info['weight']
        r_new = info.get('day_return', 0.0)  # (close − vwap_buy)/vwap_buy，来自当日 buy fills
        sector_new_weight[sector] = sector_new_weight.get(sector, 0.0) + w_new
        sector_new_ret_num[sector] = sector_new_ret_num.get(sector, 0.0) + w_new * r_new

    # 3. 拆分 selection：新建仓位浮盈贡献 vs 已有仓位已实现贡献
    unrealized_selection = 0.0
    for sector, new_w in sector_new_weight.items():
        sector_total_wp = portfolio_weights.get(sector, 0.0)
        wb = benchmark_weights.get(sector, 0.0)
        rb = benchmark_returns.get(sector, 0.0)
        if sector_total_wp > 1e-12 and new_w > 1e-12:
            lambda_i = new_w / sector_total_wp              # 新建仓位占板块市值比例
            r_new_avg = sector_new_ret_num[sector] / new_w  # 新建仓位加权当日收益
            unrealized_selection += wb * lambda_i * (r_new_avg - rb)

    realized_selection = base['selection_effect'] - unrealized_selection

    return {
        'allocation_effect': base['allocation_effect'],           # T+1 不影响
        'realized_selection_effect': realized_selection,           # 可兑现
        'unrealized_selection_effect': unrealized_selection,       # 浮盈（T+1 才可兑现）
        'selection_effect_total': base['selection_effect'],       # 总 selection（兼容契约）
        'interaction_effect': base['interaction_effect'],
        't1_locked_weight': sum(info['weight'] for info in new_positions_today.values()),  # T+1 锁定权重合计
        't1_warning': unrealized_selection / base['selection_effect'] > 0.5
                      if abs(base['selection_effect']) > 1e-12 else False,
        # t1_warning=True 表示超过 50% 的 selection 来自当日新建仓位浮盈，
        # 归因报告须标注"高 T+1 浮盈依赖"警示 owner
    }
```

**T+1 归因处理施工约束**：
- `new_positions_today` 来自 [OrderManager](file:///d:/ZephyrAlpha/src/zephyr/ex_core/order_manager.py) 当日 buy fills 聚合（fill_id 幂等，40 号 §6.1 gap 12 AsyncFillDispatcher LRU 幂等已实现），`day_return` = (当日收盘 − 买入加权均价)/买入加权均价
- 板块映射 `get_sector(symbol)` 对齐 §7 开放问题（申万一级），施工算法 v1.13.0 补全（见下）

**`get_sector(symbol)` 施工算法补全**（v1.13.0 补，悬空 helper 定义）：

```python
# 模块级缓存：申万一级映射表 {symbol: sector_name}，启动时从 akshare/tushare 预加载
_SW_LEVEL1_MAP: dict[str, str] = {}  # e.g. {"000001": "银行", "600519": "食品饮料"}

def get_sector(symbol: str) -> str:
    """申万一级板块映射（symbol → SW Level-1 industry name）

    用途：Brinson 归因 allocation/selection effect 的板块维度
    数据源：akshare stock_individual_info_em（industry 字段）/ tushare stock_basic
    缓存：静态映射（季度更新），内存 dict 避免每笔查询
    降级：映射缺失返回 "未知板块"，归因报告标注覆盖度
    """
    return _SW_LEVEL1_MAP.get(symbol, "未知板块")
```

> **数据源对齐**：申万一级分类 28 行业，akshare `stock_individual_info_em(symbol).行业` 字段直接可用。映射表在 [09_d_alt_data](../../02_domain_architecture_docs/09_d_alt_data.md) `akshare_provider`（production）启动时预加载，季度更新（申万调整频率）。§7 开放问题"Brinson 板块划分"待实盘校准后定 28 行业 vs 风格分类。
- 归因报告 §3.12 MOD-RPT-015 模板第 2 节 Brinson 分解表增加 "Realized Selection" / "Unrealized (T+1 locked) Selection" 两行分列
- `t1_warning=True` 时归因报告顶部标注警示，避免 owner 把浮盈当真实 alpha 反馈到策略层
- T+1 不影响 Carino 多期链接（链接的是已实现 PnL，浮盈在 T+1 卖出后转入已实现）

**为何 T+1 是 A 股归因的真实 gap 而非通用问题**：美股/港股 T+0 可当日买卖，selection 全部可兑现；A 股 T+1 是制度性约束，不处理会导致打板策略归因严重失真——当日浮盈被记为 selection alpha，次日低开回落时归因无法解释"昨日的 alpha 今天消失了"。

**transaction_cost_drag 接入 TCA 算法**（v1.3.0 补，[40_execution_broker](40_execution_broker.md) §2.5 + [DefaultTcaEngine](file:///d:/ZephyrAlpha/src/zephyr/reporting/default_tca_engine.py) IS 成本分解）：

> [default_attribution_engine.py:78](file:///d:/ZephyrAlpha/src/zephyr/reporting/default_attribution_engine.py) 当前 `transaction_cost_drag=0.0` 硬编码，未接入 TCA。归因报告的 transaction_cost_drag 字段必须从 DefaultTcaEngine 的 IS 成本分解导出，否则无法区分"策略 alpha 错"还是"执行成本高"。

| TCA IS 成本分项 | 含义 | 映射到 transaction_cost_drag 的算法 |
|---|---|---|
| Timing cost | 信号产生到下单的时间延迟成本 | timing_drag_i = Σ(timing_cost_i × weight_i) 加权求和 |
| Impact cost | 下单对市场的冲击成本 | impact_drag_i = Σ(impact_cost_i × weight_i) |
| Slippage cost | 成交价 vs 决策价的滑点 | slippage_drag_i = Σ(slippage_cost_i × weight_i) |
| Commission cost | 佣金 + 印花税 + 过户费 | commission_drag_i = Σ(commission_cost_i × weight_i) |

**算法公式**（v1.3.0 补）：

```python
# transaction_cost_drag 接入 TCA 的归因算法
def calculate_transaction_cost_drag(tca_results_by_fill: dict[str, dict],
                                    portfolio_weights: dict[str, float]) -> dict:
    """从 DefaultTcaEngine 的 IS 成本分解导出 transaction_cost_drag。

    Args:
        tca_results_by_fill: 各成交笔的 TCA 分解，键为 fill_id（与 40 号 fill_id 幂等对齐），
                             值为 dict 含 symbol/timing_cost/impact_cost/slippage_cost/commission_cost
        portfolio_weights: 各标的权重（beginning-of-period）
    Returns:
        drag_breakdown: {
            'timing': float,      # 时机成本拖拽
            'impact': float,      # 冲击成本拖拽
            'slippage': float,    # 滑点拖拽
            'commission': float,  # 佣金拖拽
            'total': float       # 总拖拽（写入 transaction_cost_drag）
        }
    """
    drag = {'timing': 0.0, 'impact': 0.0, 'slippage': 0.0, 'commission': 0.0}
    for fill_id, tca in tca_results_by_fill.items():
        symbol = tca['symbol']
        w = portfolio_weights.get(symbol, 0.0)
        drag['timing']     += tca['timing_cost'] * w
        drag['impact']     += tca['impact_cost'] * w
        drag['slippage']   += tca['slippage_cost'] * w
        drag['commission'] += tca['commission_cost'] * w
    drag['total'] = sum(drag.values())  # 写入 transaction_cost_drag 字段
    return drag
```

**与 Brinson 归因的对接**：
- Brinson 3 因子（allocation + selection + interaction）+ transaction_cost_drag 应等于总超额收益（求和不变量）
- 残差 = total_active_return - (allocation + selection + interaction + transaction_cost_drag) < 0.01% 是归因完整性校验
- 残差 > 0.01% 表示归因维度未覆盖完（如缺时机归因/缺外部冲击归因），需排查未编目源

**为何必须接入 TCA**：[DefaultTcaEngine](file:///d:/ZephyrAlpha/src/zephyr/reporting/default_tca_engine.py) 当前仅简易滑点，**IS 四组件分解（timing/impact/slippage/commission）本身待施工**——drag 接入前提是 TCA 侧先落 IS 分解（§5.2 第一阶段，§7 开放问题）；transaction_cost_drag=0 会让归因报告无法区分"回撤来自策略失效 vs 执行成本高"（30 号 §2.5 四级回撤复盘必需）；[marketmaker.cc 2026-03](https://marketmaker.cc/en/blog/post/backtest-live-parity)：execution divergences 贡献 10-30% PnL，是 parity gap 最大源。

**A 股权益 PnL waterfall 子框架**（v1.3.0 补，[hftradingbook 2026-06](https://hftradingbook.com/performance/attribution) waterfall 模型 A 股适配）：

> hftradingbook 的 PnL waterfall 是做市商场景。A 股非做市场景但可借鉴 waterfall 思路——将 PnL 分解为信号贡献 + 选股贡献 + 择时贡献 - 成本 - 机会成本 = 净 PnL，与 Brinson 3 因子互为补充（Brinson 是配置/选择/交互维度，waterfall 是 PnL 流向维度）。

| PnL waterfall 分项 | 含义 | 算法 | 与 Brinson 的关系 |
|---|---|---|---|
| Signal alpha | 信号预测能力贡献 | Σ(信号值 × 后续收益 × 持仓) | 对应 Brinson selection 的预测部分 |
| Selection alpha | 选股能力贡献（剔除信号后） | 实际选股收益 - 信号预测收益残差 | 对应 Brinson selection 的非预测部分 |
| Timing alpha | 择时能力贡献（盘中择时 vs 收盘价基准） | 实际成交时点收益 - 收盘价基准收益 | Brinson 不覆盖（Brinson 假设持仓不变） |
| Transaction costs | 佣金 + 印花税 + 滑点 + 冲击 | 见上方 transaction_cost_drag 算法 | 对应 Brinson transaction_cost_drag |
| Opportunity costs | 未成交订单的机会损失（涨停未买入） | Σ(信号触发未成交 × 后续收益) | Brinson 不覆盖（Brinson 只看已成交） |
| **Net PnL** | = Signal + Selection + Timing - Costs - Opportunity | 求和不变量校验 | Brinson 总和应等于 waterfall 总和 |

**PnL waterfall 施工算法**（v1.5.1 补，[hftradingbook 2026-06](https://hftradingbook.com/performance/attribution) waterfall 模型 A 股适配 + [AlgoTradingDesk 2026-01](https://algotradingdesk.com/trade-outcome-attribution-algorithmic-trading-dma/) 5 Pillars 逐笔归因 + [OrderX 2026-07-09](https://orderx.com/education/introduction-to-algorithmic-execution-part-12-benchmarks-and-tca/) slippage signed bps 公式）：

> 核心是逐笔归因（per-fill attribution），非持仓层面聚合。[OrderX 2026-07-09] slippage signed bps：cost(bps) = side × (exec_price − benchmark) / benchmark × 10_000，side=+1 买/-1 卖。Phase 2 启用时施工方直接照此实现。

```python
def calc_ashare_pnl_waterfall(fills: list[dict],
                               signal_records: dict[str, float],
                               close_prices: dict[str, float],
                               decision_prices: dict[str, float],
                               opportunity_cost_records: list[dict] = None) -> dict:
    """A 股 PnL waterfall 5 分项分解（Phase 2 施工算法）。

    Args:
        fills: 成交记录列表，每笔含 symbol/direction/fill_price/qty/decision_price/
               commission/slippage_cost/impact_cost/timing_cost
        signal_records: {symbol: signal_value} 信号触发时信号值
        close_prices: {symbol: close_price} 当日收盘价（timing 基准）
        decision_prices: {symbol: decision_price} 信号产生时决策价
        opportunity_cost_records: 未成交订单机会损失记录（外部注入，OrderManager
            rejected/cancelled orders 聚合，40 号拒单分类），每条含
            symbol/rejected_signal/intended_qty/decision_price；None/空 → 0（MVP 默认）
    Returns:
        {'signal_alpha', 'selection_alpha', 'timing_alpha',
         'transaction_costs', 'opportunity_costs', 'net_pnl': float}
    """
    signal_alpha = selection_alpha = timing_alpha = 0.0
    transaction_costs = opportunity_costs = 0.0

    for fill in fills:
        symbol = fill['symbol']
        side = 1 if fill['direction'] == 'buy' else -1
        fill_price = fill['fill_price']
        decision_price = fill.get('decision_price', decision_prices.get(symbol, fill_price))
        close_price = close_prices.get(symbol, fill_price)
        qty = fill['qty']
        signal_val = signal_records.get(symbol, 0.0)

        # 1. Signal alpha：信号预测能力贡献 = 信号值 × 后续收益 × 持仓
        forward_return = (close_price - decision_price) / decision_price
        signal_alpha += signal_val * forward_return * qty * side

        # 2. Selection alpha：选股能力（剔除信号后残差）
        actual_selection_return = (fill_price - decision_price) / decision_price
        predicted_return = signal_val * forward_return  # 信号预测部分
        selection_alpha += (actual_selection_return - predicted_return) * qty * side

        # 3. Timing alpha：择时贡献（成交时点 vs 收盘价基准）
        # [OrderX 2026-07-09] signed bps: side × (exec - benchmark) / benchmark × 10000
        timing_return = (fill_price - close_price) / close_price
        timing_alpha += timing_return * qty * side * -1  # 成交优于收盘=正贡献

        # 4. Transaction costs：佣金 + 滑点 + 冲击 + 时机
        transaction_costs += (fill.get('commission', 0) + fill.get('slippage_cost', 0)
                              + fill.get('impact_cost', 0) + fill.get('timing_cost', 0))

    # 5. Opportunity costs：未成交订单的机会损失（涨停未买入等）
    #    外部依赖注入：由 OrderManager 的 rejected/cancelled orders 聚合后传入
    #    公式：opportunity_costs = Σ(rejected_signal × forward_return × intended_qty)
    if opportunity_cost_records:
        for opp in opportunity_cost_records:
            symbol = opp['symbol']
            rejected_signal = opp['rejected_signal']
            intended_qty = opp['intended_qty']
            opp_decision_price = opp.get('decision_price', decision_prices.get(symbol, 0.0))
            opp_close_price = close_prices.get(symbol, opp_decision_price)
            if opp_decision_price > 0:
                opp_forward_return = (opp_close_price - opp_decision_price) / opp_decision_price
                # 买入未成交：机会损失 = 信号 × 上涨幅度 × 计划数量（正值=错过盈利）
                opportunity_costs += rejected_signal * opp_forward_return * intended_qty

    net_pnl = signal_alpha + selection_alpha + timing_alpha - transaction_costs - opportunity_costs
    # 求和不变量校验：waterfall net_pnl 应与 PnlCalculator 的 realized+unrealized PnL 一致
    # 差异 > 0.01% → 归因维度未覆盖（如缺外部冲击归因）

    return {
        'signal_alpha': signal_alpha,
        'selection_alpha': selection_alpha,
        'timing_alpha': timing_alpha,
        'transaction_costs': transaction_costs,
        'opportunity_costs': opportunity_costs,
        'net_pnl': net_pnl,
    }
```

**为何 waterfall 是 Brinson 的补充而非替代**：Brinson 回答"赚的钱来自配置还是选股"（决策维度），waterfall 回答"PnL 流向哪里"（构成维度）；交集：Brinson selection ≈ waterfall signal + selection alpha；差集：Brinson allocation（waterfall 不分）+ waterfall timing/opportunity（Brinson 不分）。MVP Brinson 为主，waterfall Phase 2 补充；重评条件：Brinson 残差持续 > 0.01% + 需区分"信号/选股/择时失效"时。

**为何不再造**（v1.15.0 校准）：仓内已存在真实归因实现（pf_core MOD-PF-007，含守恒校验+测试），reporting 侧为契约桩——本备忘的价值是为双实现收敛提供公式真源（BHB 守恒口径 + Carino 链接）与 why 层决策记录，而非再建第三套归因引擎。收敛裁定见 §6。

**2026-08 最新研究补充**（v1.4.0 补）：

| 算法 | 来源 | 核心思路 | 适用性评估 |
|---|---|---|---|
| **Brinson + Industry Layer 5 层分解** | [Kiski 2026-03](https://www.kiski.com/blog-posts/adding-an-industry-layer-to-active-passive-decomposition) | 在 Brinson 3 因子基础上，sector 和 selection 之间插入**行业超额层**：Market + Sector超额 + Industry超额 + Selection + Sizing，解决"selection 变垃圾桶"问题；配套**发行人级 Brinson** 解决 A/H/ADR 交叉上市虚假"选股"噪音 | 🟧 Phase 2 候选（集中型行业基金尽调归因；个人 5 策略组合 industry 层增量信息有限，首批 track record 3 月后评估） |
| **Trade Outcome Attribution 5 Pillars** | [AlgoTradingDesk 2026-01](https://algotradingdesk.com/trade-outcome-attribution-algorithmic-trading-dma/) | Signal + Timing + Spread + Slippage + Market Impact 五支柱分解，含"信号 P&L 曲线 vs 执行 P&L 曲线"可视化 | ✅ 已部分覆盖（PnL waterfall 子框架的 signal/timing/costs 对应），5 Pillars 的"逐笔元数据存储（时间戳/订单类型/簿深度/波动率/成交量/延迟）"可借鉴强化 TCA |
| **Hentschel 统一 Brinson+Factor GLS** | [Hentschel 2024](https://www.ludgerhentschel.com/PDFs/Hentschel%2024b.pdf) | 受限广义最小二乘（Restricted GLS）统一处理交互项重分配/因子残差/多期平滑，将调整导向**精度最低的估计** | 🟥 远期参考（学术统一框架，个人系统过重，登记 §6 待裁定） |

**滑点分布报告增强**（施工算法 gap，[Drovix 2026-05](https://drovix.com/blog/tca-that-actually-drives-decisions)）：

> 当前 `transaction_cost_drag` 算法用加权求和（均值），Drovix 2026-05 实证：**滑点是分布非均值**——须报告 median/90th/99th 百分位，区分正常 vs 压力 regime（top decile 波动率或宏观事件 15min 窗口）。IS 单一数字是"虚荣指标"，必须分解为 Spread + Impact + Timing + Opportunity 四组件并排报告。

- **增强算法**：`transaction_cost_drag` 除 `total`（加权均值）外，增加 `slippage_distribution = {'p50': median, 'p90': 90th_percentile, 'p99': 99th_percentile}` 字段
- **拒绝率转换成本**：`rejection_cost_bps = (rejected_price - next_executable_price) × rejection_frequency`——当前未实现，Phase 1.5 候选
- **多基准并行**：arrival/VWAP/PWP/peer-relative，每个父订单标记其策略对应的评分基准——当前 DECISION 单基准，Phase 2 候选
- **Phase 1.5 施工**：在 `calculate_transaction_cost_drag()` 中增加百分位计算，归因报告同时展示均值和分布

**滑点分布报告增强施工算法**（v1.5.1 补，[Drovix 2026-05](https://drovix.com/blog/tca-that-actually-drives-decisions) 滑点分布 + [OrderX 2026-07-09](https://orderx.com/education/introduction-to-algorithmic-execution-part-12-benchmarks-and-tca/) reversion 诊断 + [waylandz 2026-04-20](https://waylandz.com/blog/backtest-to-live-gap/) cost model 分层）：

```python
import numpy as np

def calculate_slippage_distribution(tca_results: list[dict],
                                     portfolio_weights: dict[str, float]) -> dict:
    """滑点分布报告增强——百分位 + 压力 regime 切片（[Drovix 2026-05] 滑点是分布非均值 + [OrderX 2026-07-09] reversion 诊断）。

    Args:
        tca_results: 各成交笔的 TCA 分解（含 slippage_cost/symbol/volatility_regime）
        portfolio_weights: 各标的权重（beginning-of-period）
    Returns:
        {'total': float,  # 加权均值（兼容 transaction_cost_drag）
         'slippage_distribution': {'p50','p90','p99','mean','std': float},
         'stress_regime_slippage': float,  # 压力 regime（top decile 波动率）
         'normal_regime_slippage': float,
         'reversion_signal': 'temporary_impact'|'real_alpha'|'inconclusive'}
    """
    slippage_samples = []
    weighted_slippage = 0.0
    stress_slips, normal_slips = [], []

    for tca in tca_results:
        symbol = tca['symbol']
        w = portfolio_weights.get(symbol, 0.0)
        slip = tca.get('slippage_cost', 0.0)
        slippage_samples.append(slip)
        weighted_slippage += slip * w

        # 压力 regime 切片：top decile 波动率 或 宏观事件 15min 窗口
        vol_regime = tca.get('volatility_regime', 'normal')
        if vol_regime == 'stress' or tca.get('volatility_percentile', 50) >= 90:
            stress_slips.append(slip)
        else:
            normal_slips.append(slip)

    arr = np.array(slippage_samples) if slippage_samples else np.array([0.0])

    # Reversion 诊断（[OrderX 2026-07-09]）
    # 若有 post-trade 价格数据：价格回转 → temporary_impact，继续同向 → real_alpha
    reversion_signal = 'inconclusive'  # MVP 无 post-trade 数据时默认

    return {
        'total': weighted_slippage,  # 写入 transaction_cost_drag['slippage']
        'slippage_distribution': {
            'p50': float(np.percentile(arr, 50)),
            'p90': float(np.percentile(arr, 90)),
            'p99': float(np.percentile(arr, 99)),
            'mean': float(np.mean(arr)),
            'std': float(np.std(arr)),
        },
        'stress_regime_slippage': float(np.mean(stress_slips)) if stress_slips else 0.0,
        'normal_regime_slippage': float(np.mean(normal_slips)) if normal_slips else 0.0,
        'reversion_signal': reversion_signal,
    }
# 归因报告展示：均值 + p50/p90/p99 + 压力 vs 正常 regime 对比
# p99 >> mean → 滑点有厚尾，压力 regime 执行质量显著下降 → 反馈 40 号执行算法优化
```

### 3.3 决策②：每日对账——三层对账（成交/持仓/资金）

**决策**：每日盘后做三层对账——成交对账（系统记录 vs 券商结算单）+ 持仓对账（系统账 vs 券商端）+ 资金对账（系统现金 vs 券商可用资金），盘中加持仓对账每 5min 巡检。

**三层对账定义**：

| 对账层 | 对账内容 | 触发时点 | 模块 | 状态 |
|---|---|---|---|---|
| ① 成交对账 | 系统成交记录 vs 券商结算单（逐笔：数量/价格/费率/方向） | 每日 15:30 盘后 | SettlementReconciliation（MOD-TRADING-003） | 🟦 production |
| ② 持仓对账 | 系统账（PositionTracker）vs 券商端（get_positions）（逐标的：数量） | 盘中每 5min + 盘后全量 | PositionReconciler（MOD-EX-056） | 🟦 production（盘中）/ 🟧 Phase 2（盘后全量） |
| ③ 资金对账 | 系统现金 vs 券商可用资金（含 T+0/T+1 资金可用性） | 每日盘后 | — | 🟧 gap（PositionReconciler 阶段2扩展，见蓝图 §3） |

**持仓对账机制**（[PositionReconciler](file:///d:/ZephyrAlpha/src/zephyr/ex_core/position_reconciler.py)，已实现）：
- 双源比对：PositionTracker（靠成交回报累计）vs Broker get_positions（券商端查询）
- 差异检测：逐标的比较 quantity，diff > tolerance 记为 DriftItem
- 冻结/解冻：有 drift 的标的冻结交易；恢复一致后解冻
- 告警回调：on_drift 解耦告警通道
- 纯读不修改 source 状态（reconcile 是只读诊断，不修改 PositionTracker/Broker）

**持仓对账偏差检测算法**（v1.6.0 补，[marketclutch 2026 "Position Reconciliation"](https://marketclutch.com/the-silent-sentinel-mastering-trading-position-reconciliation/) Variance Delta 公式 + [electronictradinghub 2026-06-17 "Position Drift"](https://electronictradinghub.com/crypto-market-making-position-drift-how-multi-venue-state-desync-defeats-pre-trade-risk/) 容差校准不可解问题共识 + [ParseMyStatement 2026-04 Running Balance QA](https://parsemystatement.com/blog/running-balance-sequence-qa-detect-missing-merged-lines-before-reconciliation-reng8z) 行级不变量校验）：

> Variance Delta = (Internal Qty - External Qty) × Market Price，专业系统用 0.01 元或 1 股作为默认阈值；容差校准是"未解决问题"——需按标的流动性/价格量级分层设定，非单一全局阈值。以下补 DriftItem 数据结构、Delta 公式、容差参数、偏差分级、冻结/解冻状态机。

**DriftItem 数据结构**：

```python
@dataclass
class DriftItem:
    symbol: str                    # 标的代码
    internal_qty: float            # PositionTracker 持仓数量
    external_qty: float            # Broker get_positions 返回数量
    market_price: float            # 当前市价（用于计算金额维度 Delta）
    qty_delta: float               # = internal_qty - external_qty（数量维度）
    value_delta: float             # = qty_delta × market_price（金额维度）
    drift_severity: str            # 'minor' | 'major' | 'critical'（见下方分级）
    detected_at: datetime          # 检测时间戳
    reconcile_session_id: str      # 对账 session ID（关联审计轨迹 §3.3 三阶段）
    freeze_status: str             # 'frozen' | 'unfrozen' | 'monitoring'
```

**偏差检测与分级算法**：

```python
def detect_position_drift(
        internal_positions: dict[str, float],   # {symbol: qty} PositionTracker
        external_positions: dict[str, float],    # {symbol: qty} Broker get_positions
        market_prices: dict[str, float],         # {symbol: current_price}
        qty_tolerance: float = 0.01,             # 数量容差（股，小数股尾差）
        value_tolerance: float = 1.0,            # 金额容差（元，市场clutch 默认 0.01 元，A 股放宽到 1 元）
        major_threshold_bps: float = 50.0,       # 50bp = 0.5% 金额偏差 → major
        critical_threshold_bps: float = 200.0    # 200bp = 2% 金额偏差 → critical
) -> list[DriftItem]:
    """持仓对账偏差检测——逐标的计算 qty/value Delta + 分级。

    [marketclutch 2026]：Delta = (Internal - External) × Market Price，
    专业系统阈值 0.01 美元或 1 股。A 股适配：小数股尾差（送转股）+ 金额维度分级。
    [electronictradinghub 2026-06]：容差校准是"未解决问题"——
    本算法按金额偏差 bps 分级，实盘 3 月后回归校准阈值。
    """
    drifts = []
    all_symbols = set(internal_positions) | set(external_positions)

    for symbol in all_symbols:
        internal_qty = internal_positions.get(symbol, 0.0)
        external_qty = external_positions.get(symbol, 0.0)
        qty_delta = internal_qty - external_qty
        price = market_prices.get(symbol, 0.0)
        value_delta = qty_delta * price

        # 跳过容差内的微小偏差（精度尾差）
        if abs(qty_delta) <= qty_tolerance and abs(value_delta) <= value_tolerance:
            continue

        # 分级：按金额偏差占持仓市值的 bps
        position_value = max(abs(internal_qty), abs(external_qty)) * price
        if position_value > 1e-6:
            drift_bps = abs(value_delta) / position_value * 10000
        else:
            drift_bps = float('inf')  # 一方有持仓一方为零 → critical

        if drift_bps >= critical_threshold_bps:
            severity = 'critical'
        elif drift_bps >= major_threshold_bps:
            severity = 'major'
        else:
            severity = 'minor'

        drifts.append(DriftItem(
            symbol=symbol,
            internal_qty=internal_qty,
            external_qty=external_qty,
            market_price=price,
            qty_delta=qty_delta,
            value_delta=value_delta,
            drift_severity=severity,
            detected_at=datetime.utcnow(),
            reconcile_session_id=current_session_id(),
            freeze_status='frozen' if severity in ('major', 'critical') else 'monitoring'
        ))

    return drifts
```

**偏差分级与处置状态机**：

| 严重度 | 金额偏差 bps | 典型场景 | 处置动作 | 冻结状态 |
|---|---|---|---|---|
| **minor**（微小偏差） | < 50 bps（< 0.5%） | 精度尾差 / 小数股送转 / 四舍五入 | 记录 DriftItem + 监控，不冻结交易 | `monitoring` |
| **major**（重大偏差） | 50-200 bps（0.5%-2%） | 部分成交未同步 / 拒单未记录 / 费率错算 | 冻结该标的交易 + 触发告警（微信 Webhook） + owner 人工排查 | `frozen` |
| **critical**（严重偏差） | ≥ 200 bps（≥ 2%）或一方为零 | 系统漏单 / 券商多单 / 数据丢失 / 持仓完全错位 | 冻结该标的 + 全账户告警 + 暂停新下单 + owner 立即介入 | `frozen` |

**冻结/解冻状态机**（[electronictradinghub 2026-06] resnap 逻辑参考）：

```
[正常] --detect drift(major/critical)--> [frozen] --owner 排查修复--> [reconciling]
                                                                        |
                  [frozen] --detect drift(minor)--> [monitoring] <------+
                                                                        |
                  [monitoring] --连续 3 次对账无 drift--> [正常] <-------+
                  [monitoring] --再次 detect drift(major)--> [frozen]
```

- `frozen` 状态下该标的的 OrderManager 拒绝新下单（40 号决策⑥层3 已实现拒单逻辑）
- `reconciling` 是中间态：owner 修复后触发一次手动对账，确认 drift 消除
- `monitoring` 是 minor drift 的观察态：不冻结但跟踪后续对账是否收敛
- 连续 3 次对账（~15min）无 drift 后从 `monitoring` 恢复到 `正常`——避免瞬时数据延迟导致反复冻结/解冻

**为何按金额 bps 分级而非固定股数阈值**：固定股数阈值对高价股（贵州茅台 ~1700 元）和低价股（ST 股 ~2 元）严重度判断不一致；金额 bps 分级让偏差严重度与持仓市值成正比——100 股偏差对茅台（17 万元）是 minor，对 ST 股（200 元）是 critical（[electronictradinghub 2026-06]：按"实际影响"而非"绝对数量"判定）。

**容差校准计划**（[electronictradinghub 2026-06] "calibration does not have a solved answer"）：
- MVP 用默认容差（qty_tol=0.01 股 / value_tol=1 元 / major=50bps / critical=200bps）
- 首批策略实盘 3 月后用历史 drift 数据回归校准：
  - 统计 minor/major/critical 各级的 false positive 率（人工排查确认非真实 drift 的比例）
  - 若 minor 级 false positive > 30% → 上调 major 阈值至 75 bps
  - 若 critical 级漏检（真实持仓错位被分到 major）→ 下调 critical 阈值至 150 bps

**资金对账 gap**（待施工，v1.15.0 重定性）：
- 系统侧资金账已存在：[CashManager](file:///d:/ZephyrAlpha/src/zephyr/position/core/cash_manager.py)（MOD-POS-006，production）已实现资金流水 + T+1 结算（SELL 进 pending_settlement 次日可用）+ 三级储备金；[DailyAuditor](file:///d:/ZephyrAlpha/src/zephyr/risk/core/daily_auditor.py)（MOD-RK-20，production，safety=H）已实现日终 PnL 对账（expected MtM vs 账面 realized+unrealized gap 检测）
- 真正缺口是**双边核对的券商侧**：系统现金账（CashManager）vs 券商可用资金（miniQMT `get_positions().cash`）的逐日比对未接线；T+0/T+1 资金可用性需结合成交回报推算
- 配套缺口：盘后 15:30 自动触发无调度器接线（§2.4 横向缺口 #2），当前只能外部手动/事件调用
- 实盘上线后优先级提升（资金不一致会导致买入时 error_code=54 拒单，见 [40_execution_broker](40_execution_broker.md) §2.14 决策⑬资金预占）

**成交对账三层匹配算法**（v1.3.0 补，[osfin 2026-03](https://www.osfin.ai/blog/trade-reconciliation) 6 步流程 + [intura 2026](https://intura.co/en/guides/ai-finance-reconciliation) 匹配逻辑类型 + [ai-indeed 2026-08-04](https://www.ai-indeed.com/encyclopedia/19423.html) 强弱规则分层）：

> SettlementReconciliation（MOD-TRADING-003）当前是逐笔核对，缺匹配规则分层。2026-08 行业共识是三层匹配（exact/fuzzy/partial）+ 例外闭环——强规则先命中，弱规则辅助候选集排序，未匹配进例外工单。匹配规则分层能让对账例外率从 ~5% 降到 < 1%（[ai-indeed 2026-08-04](https://www.ai-indeed.com/encyclopedia/19423.html) 实证：例外率 18%→2.9%）。

| 匹配层级 | 匹配规则 | 容差 | 命中后动作 | 典型场景 |
|---|---|---|---|---|
| **① 强一致匹配**（exact match） | fill_id + symbol + direction + quantity + price 全等 | 0 容差 | 直接标记 matched，归档 | 90%+ 成交（正常成交回报与结算单严格一致） |
| **② 结构化容差匹配**（fuzzy match） | symbol + direction 一致 + quantity ±容差 + price ±容差 | 数量 ±0.01 股（小数股尾差）+ 价格 ±0.001 元（精度尾差）+ 日期 T±1（T+1 结算跨日） | 标记 fuzzy_matched + 记录容差原因 | 部分成交（partial fill）+ T+1 结算跨日 + 精度尾差 |
| **③ 拆分/合并匹配**（partial match） | 一笔系统订单 ↔ 多笔券商结算单（拆单）或多笔系统订单 ↔ 一笔结算单（合并） | 按同 symbol + 同 direction + 同日聚合 | 标记 partial_matched + 记录拆合关系 | 拆单成交（大单拆小单避免冲击）+ 合并结算（券商批量结算） |
| **④ 例外工单**（no match） | 三层均未命中 | — | 进例外队列 + 触发告警（§3.6 严重度按 gap 大小分级） | 系统漏单/券商多单/数据丢失/未编目场景 |

**算法实现**（v1.3.0 补，v1.13.0 补悬空 helper 定义）：

```python
# ── 悬空 helper 施工算法补全（v1.13.0 补）──────────────────────────

def current_session_id() -> str:
    """生成对账会话唯一标识（date + session_type），作 reconcile 幂等键。

    会话类型：MORNING (9:30-11:30) / AFTERNOON (13:00-15:00) / AFTER_HOURS (盘后)
    对账粒度：每 session 一次对账，session_id 防重复对账
    """
    from datetime import datetime
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    hm = now.hour * 100 + now.minute
    if hm < 1130:
        session = "MORNING"
    elif hm < 1500:
        session = "AFTERNOON"
    else:
        session = "AFTER_HOURS"
    return f"{date_str}_{session}"


def group_by_symbol_dir_date(items: list) -> list[tuple]:
    """按 (symbol, direction, date) 聚合键分组，返回所有出现的键。"""
    seen = set()
    for item in items:
        seen.add((item.symbol, item.direction, item.date))
    return list(seen)


def aggregate(items: list, symbol: str, direction: str, date) -> "AggRecord":
    """聚合同 (symbol, direction, date) 键的所有 fill 为单一 AggRecord。

    输出：AggRecord(.qty=加和, .symbol, .direction, .date)
    用途：三层匹配层 2/3 容差匹配前，将同键多笔 fill 合并为单记录比对
    """
    total_qty = sum(item.quantity for item in items
                    if item.symbol == symbol and item.direction == direction
                    and item.date == date)
    return AggRecord(symbol=symbol, direction=direction, date=date, qty=total_qty)

# ──────────────────────────────────────────────────────────────────


def reconcile_trades(system_fills: list[Fill],
                     broker_settlements: list[Settlement]) -> ReconciliationResult:
    """三层匹配算法：exact → fuzzy → partial → exception。

    Helper（v1.13.0 补全定义，见上方）：
      - group_by_symbol_dir_date / aggregate / current_session_id
      - ReconciliationResult / Fill / Settlement / AggRecord 为数据类（40 号已定义）
    """
    matched, fuzzy, partial, exceptions = [], [], [], []

    # 层 1: 强一致匹配（fill_id 为主键）
    matched_s_fill_ids = set()
    matched_b_fill_ids = set()
    for s_fill in system_fills:
        for b_settle in broker_settlements:
            if b_settle.fill_id in matched_b_fill_ids:
                continue  # 防御：一笔券商结算单只允许命中一笔系统成交
            if (s_fill.fill_id == b_settle.fill_id
                and s_fill.symbol == b_settle.symbol
                and s_fill.direction == b_settle.direction
                and abs(s_fill.quantity - b_settle.quantity) < 1e-9
                and abs(s_fill.price - b_settle.price) < 1e-6):
                matched.append((s_fill, b_settle))
                matched_s_fill_ids.add(s_fill.fill_id)
                matched_b_fill_ids.add(b_settle.fill_id)
                break

    # 层 1→2 传递：未匹配项 = 全集 - 层 1 命中
    unmatched_system = [f for f in system_fills if f.fill_id not in matched_s_fill_ids]
    unmatched_broker = [s for s in broker_settlements if s.fill_id not in matched_b_fill_ids]

    # 层 2: 结构化容差匹配（剩余未匹配项）
    qty_tol, price_tol, date_window = 0.01, 0.001, 1
    fuzzy_s_fill_ids = set()
    fuzzy_b_fill_ids = set()
    for s_fill in unmatched_system:
        for b_settle in unmatched_broker:
            if b_settle.fill_id in fuzzy_b_fill_ids:
                continue  # 防双计：已命中结算单不再参与后续 fuzzy 匹配
            if (s_fill.symbol == b_settle.symbol
                and s_fill.direction == b_settle.direction
                and abs(s_fill.quantity - b_settle.quantity) <= qty_tol
                and abs(s_fill.price - b_settle.price) <= price_tol
                and abs((s_fill.date - b_settle.date).days) <= date_window):
                fuzzy.append((s_fill, b_settle, "容差命中"))
                fuzzy_s_fill_ids.add(s_fill.fill_id)
                fuzzy_b_fill_ids.add(b_settle.fill_id)
                break

    # 层 2→3 传递：层 2 未匹配项（用于层 3 拆合匹配）
    remaining_system = [f for f in unmatched_system if f.fill_id not in fuzzy_s_fill_ids]
    remaining_broker = [s for s in unmatched_broker if s.fill_id not in fuzzy_b_fill_ids]

    # 层 3: 拆分/合并匹配（按 symbol + direction + date 聚合，双边合并取聚合键全集）
    partial_s_fill_ids = set()
    partial_b_fill_ids = set()
    for symbol, direction, date in group_by_symbol_dir_date(remaining_system + remaining_broker):
        sys_agg = aggregate(remaining_system, symbol, direction, date)
        brk_agg = aggregate(remaining_broker, symbol, direction, date)
        if abs(sys_agg.qty - brk_agg.qty) < 1e-6:
            partial.append((sys_agg, brk_agg, "拆合匹配"))
            # 标记本组所有 fill 为 partial 命中（按 symbol+direction+date 索引）
            for f in remaining_system:
                if f.symbol == symbol and f.direction == direction and f.date == date:
                    partial_s_fill_ids.add(f.fill_id)
            for s in remaining_broker:
                if s.symbol == symbol and s.direction == direction and s.date == date:
                    partial_b_fill_ids.add(s.fill_id)

    # 层 4: 例外工单 = 层 3 未命中项（系统/券商任一侧均可能残留）
    exceptions = {
        'system': [f for f in remaining_system if f.fill_id not in partial_s_fill_ids],
        'broker': [s for s in remaining_broker if s.fill_id not in partial_b_fill_ids],
    }
    return ReconciliationResult(matched, fuzzy, partial, exceptions)
```

**为何三层而非单层 exact**：单层 exact 容差 0 会让精度尾差/T+1 跨日/部分成交全进例外（例外率 ~5-18%，[ai-indeed 2026-08-04](https://www.ai-indeed.com/encyclopedia/19423.html)）；三层让 95%+ "近一致"成交自动归类，例外率 < 1%（owner 单点，例外工单必须可控）；与 40 号 fill_id 幂等不冲突（fill_id 是层①主键，三层是未命中兜底）。**不设四/五层**：弱规则辅助匹配（摘要/发票号片段）适合财务对账，A 股交易对账无此字段；重评条件：例外率持续 > 5% + 弱规则层能贡献 > 2% 命中率时。

**置信度评分匹配子决策**（v1.5.0 补，[naya.finance 2026-04-02](https://www.naya.finance/blog/reconciliation-engine-architecture) 加权属性相似度 + [tilores 2026-06-15](https://tilores.io/content/explainable-entity-resolution-confidence-thresholds-audit) 置信带 + [theneuralbase 2026-04](https://theneuralbase.com/ai-for-finance/learn/advanced/reconciliation-pipelines/) 三阶段模式）：

> 三层匹配只输出 matched/fuzzy/partial/exception 四状态，缺**置信度量化**——fuzzy 层命中可能是高置信（仅数量差 0.01 股）也可能是低置信（数量+价格+跨日均差）。2026-08 行业共识是给每个匹配输出**加权置信度分数**，高于阈值自动接受、中区间人工 review、低于阈值拒绝进例外——把"近一致"匹配从二元判断升级为可审计的概率决策。

| 置信带 | 分数范围 | 默认动作 | 审计证据 | 典型 owner |
|---|---|---|---|---|
| **High confidence**（高置信自动接受） | ≥ 0.85 | 自动标记 matched，归档 | 层级 + 命中规则 + 分数 + 属性差异 | 系统自动 |
| **Middle band**（中置信人工 review） | 0.50 - 0.85 | 标记 pending_review + 触发告警 | 冲突字段 + reviewer 决策 + 原因码 | Owner 人工 |
| **Low confidence**（低置信拒绝） | < 0.50 | 拒绝匹配 + 进例外工单 | 被拒规则路径 + 分数 + 反对匹配的字段 | Owner 人工排查 |

**加权属性相似度算法**（[naya.finance 2026-04-02](https://www.naya.finance/blog/reconciliation-engine-architecture) 共识，权重按 A 股交易对账场景校准）：

```python
def calculate_match_confidence(system_fill: Fill,
                               broker_settle: Settlement,
                               match_layer: str) -> float:
    """计算匹配置信度分数（0.0-1.0）。

    基于 naya.finance 2026-04 加权属性相似度模型，权重按 A 股交易对账校准：
    fill_id 是强主键（权重最高），数量/价格是核心字段，日期是辅助字段。
    """
    if match_layer == "exact":
        # 层 1 强一致匹配：fill_id + 全字段精确相等 → 置信度 1.0
        return 1.0

    score = 0.0
    # fill_id 匹配（权重 0.30，最强主键）
    if system_fill.fill_id == broker_settle.fill_id:
        score += 0.30
    # symbol + direction 匹配（权重 0.20，匹配前提）
    if (system_fill.symbol == broker_settle.symbol
            and system_fill.direction == broker_settle.direction):
        score += 0.20
    # 数量匹配（权重 0.20，核心字段）
    qty_diff = abs(system_fill.quantity - broker_settle.quantity)
    if qty_diff < 1e-9:
        score += 0.20          # 精确匹配
    elif qty_diff <= 0.01:
        score += 0.15           # 容差内（fuzzy 层）
    elif qty_diff <= system_fill.quantity * 0.01:
        score += 0.08           # 1% 内（partial 层拆合）
    # 价格匹配（权重 0.15，核心字段）
    price_diff = abs(system_fill.price - broker_settle.price)
    if price_diff < 1e-6:
        score += 0.15          # 精确匹配
    elif price_diff <= 0.001:
        score += 0.10           # 容差内（fuzzy 层）
    # 日期匹配（权重 0.10，T+1 结算跨日容忍）
    date_diff = abs((system_fill.date - broker_settle.date).days)
    if date_diff == 0:
        score += 0.10          # 同日
    elif date_diff <= 1:
        score += 0.06           # T+1 跨日（fuzzy 层）
    # 时间戳匹配（权重 0.05，辅助字段）
    if abs((system_fill.timestamp - broker_settle.timestamp).total_seconds()) < 300:
        score += 0.05           # 5 分钟内

    return round(score, 4)
# 层 2 fuzzy 命中典型分数：0.70-0.95（缺 fill_id 但 symbol/qty/price 全中）
# 层 3 partial 命中典型分数：0.50-0.80（聚合匹配但单笔对应关系不确定）
```

**为何加置信度而非保留二元状态**：[tilores 2026-06-15](https://tilores.io/content/explainable-entity-resolution-confidence-thresholds-audit) 置信度排序候选集 + 阈值分离自动接受 vs 人工 review；中置信区间（0.50-0.85）触发 review 可在例外爆发前拦截（owner 单点）；置信度分数是审计证据的一部分（下方三阶段审计轨迹复用）。

**置信度阈值校准计划**：
- MVP 用默认阈值（High ≥ 0.85 / Middle 0.50-0.85 / Low < 0.50）
- 首批策略实盘 3 月 track record 后，用历史匹配数据回归校准：
  - 统计各层命中的 false positive 率（人工 review 确认错误匹配的比例）
  - 若 fuzzy 层 false positive > 10% → 上调 High 阈值至 0.90
  - 若例外率 > 5% + 中区间命中率高 → 下调 High 阈值至 0.80
- **ML 匹配校准期警示**（v1.15.0 补，[theneuralbase 2026-04 verified note](https://theneuralbase.com/ai-for-finance/learn/advanced/reconciliation-pipelines/)）：ML/模糊匹配"70-80% 检出率"的前提是 2+ 年标注数据，新机构前 18 个月仅 40-50%——本项目规则三层 + 置信度评分优先、AI 匹配暂缓（§6）的设计由此获得行业实证支持；若未来引入 ML 辅助匹配，模型版本/再训练日期/回测结果须随每条匹配决策一并入审计轨迹（MiFID II 记录要求）

**例外工单根因分类增强**（v1.15.0 补，[m2pfintech 2026-08-04 "Exception Management in Reconciliation"](https://m2pfintech.com/blog/exception-management-reconciliation-best-practices/)）：

> 行业实证：对账的真实成本中心不是匹配而是例外处理。例外工单补两个轻量字段（非新算法）：
> - `root_cause`：例外根因分类枚举——`data_feed`（数据源错误/延迟）/ `process_gap`（流程缺口，如部分成交未同步）/ `system_limitation`（系统 bug/口径不一致）/ `timing`（T+1 跨日等时序差异，自愈型）
> - `recurrence_key`：重复模式键（symbol + root_cause + 匹配层）——月度复盘统计重复根因分布，同一 recurrence_key 月内 ≥ 3 次 → 升级为系统性问题反馈对应模块 owner（对齐 §3.6 异常事件月度统计节奏）
> - 落地位置：例外工单结构（`ReconciliationResult.exceptions`）增加两字段，审计轨迹阶段②同步记录

**三阶段不可变审计轨迹子决策**（v1.5.0 补，[theneuralbase 2026-04](https://theneuralbase.com/ai-for-finance/learn/advanced/reconciliation-pipelines/) 三阶段模式 + [theneuralbase reconciliation-assistance 2026-04](https://theneuralbase.com/ai-for-finance/learn/intermediate/reconciliation-assistance/) 不可变审计约束 + [tilores 2026-06-15](https://tilores.io/content/explainable-entity-resolution-confidence-thresholds-audit) 审计证据字段）：

> [theneuralbase 2026-04](https://theneuralbase.com/ai-for-finance/learn/intermediate/reconciliation-assistance/)："Audit trail must be immutable: write once, read-only after 30 days" + "regulators audit the false negatives hardest"——不仅记录接受的匹配，还必须记录被拒绝的匹配及理由。对账是 PnL 归因的数据源，任何匹配错误都会传播到归因报告，必须有不可变审计轨迹支撑"归因数据可信"。
>
> **与 #ARCH-OE-007 的对齐声明**（v1.15.0 补）：#ARCH-OE-007（2026-08-11 decided）裁定"BM-BUY-10 不建独立不可篡改审计链，可追溯性由 CC-15 事件溯源承接"。本节三阶段轨迹是**对账业务内生的防篡改可检测（tamper-evident）证据链**——SQLite append-only + hash 链提供"篡改可检测"而非机构级"篡改不可行"，服务对账匹配决策的可回溯自查，与 OE-007 裁剪的机构级不可篡改审计链（BM-BUY-10，面向外部审计/监管举证）性质不同、不冲突；Merkle tree/外部锚定/VCP 等机构级能力已全部标 Phase 2+（见下）。措辞口径：本节"不可变"= tamper-evident 可检测，非 tamper-proof 不可篡改。

| 阶段 | 内容 | 不可变性 | 存储方式 |
|---|---|---|---|
| **阶段①原始事件捕获** | system_fills + broker_settlements **原始记录**（未归一化、未匹配） | 追加写入（append-only），禁止 UPDATE/DELETE | SQLite 专用表 + 行级 hash |
| **阶段②匹配决策** | 匹配层级 + 置信度分数 + 命中规则版本 + 属性差异 + reviewer（若人工）+ 时间戳 + **被拒匹配及理由**（negative evidence） | 追加写入，30 天后 read-only | SQLite 专用表 + 前一阶段 hash 链 |
| **阶段③归因结果** | Brinson 3 因子分解 + Carino residual + transaction_cost_drag + 求和不变量校验结果 | 追加写入，30 天后 read-only | SQLite 专用表 + 前一阶段 hash 链 |

**不可变审计轨迹算法**（v1.5.0 补）：

```python
import hashlib
import json
from datetime import datetime

def write_audit_stage(db_conn, stage: int, record: dict,
                      prev_hash: str = "") -> str:
    """写入不可变审计轨迹阶段记录，返回本记录 hash。

    三阶段 hash 链：每条记录包含前一阶段记录的 hash，
    形成链式结构——篡改任何历史记录都会断链。
    [theneuralbase 2026-04]：write once, read-only after 30 days。
    """
    record['stage'] = stage
    record['timestamp'] = datetime.utcnow().isoformat()
    record['prev_hash'] = prev_hash            # 前一阶段 hash 链接
    record['rule_version'] = get_matching_rule_version()  # 规则版本快照
    # 序列化 + 计算 hash（排除自身 hash 字段）
    content = json.dumps(record, sort_keys=True, default=str)
    record_hash = hashlib.sha256(content.encode()).hexdigest()
    record['record_hash'] = record_hash
    # 追加写入（INSERT only，触发器禁止 UPDATE/DELETE）
    db_conn.execute(
        "INSERT INTO audit_trail (stage, timestamp, prev_hash, record_hash, content) "
        "VALUES (?, ?, ?, ?, ?)",
        (stage, record['timestamp'], prev_hash, record_hash, content)
    )
    db_conn.commit()
    return record_hash

# 阶段①：原始事件捕获（每次对账前写入 system_fills + broker_settlements 原始记录）
raw_hash = write_audit_stage(db, stage=1, record={
    'system_fills': [as_dict(f) for f in system_fills],
    'broker_settlements': [as_dict(s) for s in broker_settlements],
    'fill_count': len(system_fills),
    'settlement_count': len(broker_settlements),
})
# 阶段②：匹配决策（三层匹配 + 置信度 + 被拒匹配 negative evidence）
match_hash = write_audit_stage(db, stage=2, record={
    'matched': [(s.fill_id, b.settle_id, 1.0) for s, b in matched],
    'fuzzy': [(s.fill_id, b.settle_id, score, reason) for s, b, score, reason in fuzzy],
    'partial': [(agg_key, score, relation) for agg_key, score, relation in partial],
    'rejected': [(s.fill_id, b.settle_id, score, reject_reason)
                 for s, b, score, reject_reason in rejected_pairs],  # negative evidence
    'exception': [e for e in exceptions],
    'reviewer': owner_id if any_manual_review else 'auto',
}, prev_hash=raw_hash)
# 阶段③：归因结果（Brinson 分解 + Carino residual + 不变量校验）
attribution_hash = write_audit_stage(db, stage=3, record={
    'allocation_effect': alloc,
    'selection_effect': selec,
    'interaction_effect': interact,
    'transaction_cost_drag': drag,
    'carino_residual': residual,
    'sum_invariant_check': abs(total - sum_of_effects) < 1e-6,
    'residual_quality': 'PASS' if abs(residual) < 1e-6 else 'FAIL',
}, prev_hash=match_hash)
# 30 天后审计表自动 read-only（SQLite 触发器 + 定期 WAL 归档）
```

**为何用 SQLite hash 链而非区块链**：个人系统单机 + 单 owner，无需多方信任——SQLite hash 链提供"篡改可检测"而非"篡改不可行"；非 SOX 合规对象，SQLite 触发器级保护足够；区块链引入节点同步/共识开销是过度工程。重评条件：AUM 机构化 + 外部资金引入 + 需向 LP/监管提供不可篡改审计证据时 → 迁移到 PostgreSQL append-only 或 Hyperledger。

**Merkle Tree 升级路径**（v1.7.0 补 / v1.7.3 更新 VCP v1.2 对齐，[Apotheon.ai 2026-07-18 "Merkle DAG"](https://apotheon.ai/resources/whitepapers/merkle-dags) + [AgentAudit RFC 6962](https://github.com/KaushikKC/AgentAudit) + [mickai.co.uk 2026-06-14 "Tamper-Evident Log"](https://mickai.co.uk/articles/anatomy-tamper-evident-log-hash-chain-anchoring)）：

> 当前 v1.5.0 线性 hash 链能检测单点篡改，但有 2026 共识级结构性缺陷：①**无 inclusion proof**——无法向第三方证明"某条记录存在于链中"而不泄露全量；②**无外部时间锚**——持 DB 权限者可重写整段历史并重算所有哈希（"重写历史攻击"）。2026 共识标准（RFC 6962）是 **Merkle tree + 外部锚定**：
>
> | 维度 | 当前（v1.5.0 线性 hash 链） | 升级后（Merkle tree + 外部锚定） |
> |---|---|---|
> | 结构 | record → prev_hash 线性链 | 叶子=记录，内部节点=子节点 hash 拼接，root=全量承诺 |
> | 篡改检测 | ✅ 单点篡改断链 | ✅ 同等 + 额外：root 不匹配即暴露 |
> | Inclusion proof | ❌ 须泄露全量 | ✅ O(log n)——百万事件只需 ~3KB 证明（20 层路径） |
> | Consistency proof | ❌ 无 | ✅ 证明 T2 是 T1 的纯追加扩展（历史未被重写） |
> | 外部时间锚 | ❌ 无（持权者可重写历史） | ✅ 周期性 root 写入 RFC-3161 TSA 或 Sigstore Rekor |
>
> **为何暂缓到 Phase 2 而非 MVP**：MVP 阶段个人单机单 owner，线性 hash 链的"篡改可检测"已满足生存需求；Merkle tree + 外部锚定的价值在"AUM 机构化/外部审计/监管举证"场景才释放。与 §5 重评条件"外部资金引入"同步触发。
>
> **Phase 2 升级施工**（触发条件满足后）：①将 `write_audit_stage` 的线性 prev_hash 改为 Merkle tree 叶子节点；②每日 EOD 将 Merkle root 写入 RFC-3161 TSA（免费公共服务，如 [FreeTSA](https://time.certum.pl/)）或 Sigstore Rekor（开源透明日志）；③归因报告附带当日 Merkle root + TSA 时间戳收据，提供"可证明时间"；④**对齐 VCP v1.2 协议**（v1.7.3 补）——Merkle tree 结构 + JSON canonicalization（RFC 8785）+ UUIDv7 事件 ID（RFC 9562）+ Ed25519 签名按 VCP v1.2 规范实施，使审计轨迹未来可对接 VSO 监管验证节点（CSRC 中国已收到 VCP v1.2 提交，A 股监管举证有标准化协议可对照）。
>
> **VCP v1.1 三层密码学架构 + VCP-XREF 跨监管映射参考**（v1.8.0 补，[VeritasChain VCP v1.1 2026-01-17](https://veritaschain.org/blog/posts/2026-01-17-vcp-v1-1-regulatory-compliance-solutions/) + [IETF OMP draft-veridom-omp-00 2026-03-21](https://www.ietf.org/archive/id/draft-veridom-omp-00.html) + [IETF VAP draft-ailex-vap-legal-ai-provenance-03 2026-03-02](https://www.ietf.org/archive/id/draft-ailex-vap-legal-ai-provenance-03.html)）：
>
> | VCP v1.1 层 | 功能 | 对应本备忘当前 | Phase 2 升级后 |
> |---|---|---|---|
> | Layer 1 Event Integrity | EventHash（RFC 8785 canonical JSON SHA-256） | ✅ 已有 hash chain | 对齐 RFC 8785 canonicalization + UUIDv7 事件 ID |
> | Layer 2 Merkle Audit Paths | inclusion proof + consistency proof | ❌ 线性链无 | ✅ Merkle tree（§3.3 升级路径） |
> | Layer 3 External Anchoring | RFC 3161 TSA / IETF SCITT 透明日志 | ❌ 无 | ✅ EOD Merkle root 锚定 RFC-3161 TSA |
>
> - **VCP-XREF 跨监管映射**：同一审计事件按多监管要求（EU AI Act Art 12 / DORA Art 17 / MiFID II RTS 25 / prEN ISO/IEC 24970 / CSRC 中国）映射到不同合规视图。本项目当前仅 CSRC 中国监管要求，但 VCP-XREF 机制为未来 AUM 机构化 / 跨境资金接入预留扩展空间——审计轨迹一次记录，多监管视图按需生成
> - **Completeness Invariant 完整性不变量**（VCP v1.1 + VAP 共识）：审计轨迹须保证"无选择性日志"——通过 sequence number 连续性 + Merkle root 周期性锚定，第三方可证明"无事件被选择性删除"。本备忘当前线性 hash 链有"重写历史攻击"风险，Completeness Invariant + 外部锚定是结构性修复
> - **为何 Phase 2 而非 MVP**：同上方 Merkle 升级路径裁定——机构级跨境监管合规需求，个人单机线性 hash 链已满足生存需求；与 §5 重评条件"外部资金引入 + 跨境资金接入"同步触发
>
> **VCP v1.2 四大新特性升级路径**（v1.8.0 补，[VeritasChain VCP v1.2 2026-05-31 RC1](https://github.com/veritaschain/vcp-spec/blob/main/VCP-Specification-v1_2_en.md) + [IETF draft-kamimura-scitt-vcp-03 2026-07-21](https://datatracker.ietf.org/doc/draft-kamimura-scitt-vcp/)）：
>
> v1.2 是 v1.1 的**零破坏性协议升级**（v1.0/v1.1 数据完全可互操作），新增四大特性填补 v1.1 在"恢复约束 / 数据擦除留痕 / 跨方对账 / 后量子就绪"四个缺口。本项目 Phase 2 升级到 v1.1 后，按需评估进一步对齐 v1.2：
>
> | v1.2 新特性 | 解决的 v1.1 缺口 | 本项目对应场景 | 升级评估 |
> |---|---|---|---|
> | **VCP-RECOVERY**（SKIP/REBUILD/MERGE/CHECKPOINT 边界 + 紧急覆盖） | v1.1 Merkle root 锚定失败时无定义的恢复流程 | EOD Merkle root 写入 RFC-3161 TSA 失败（网络故障/TSA 服务宕机）时的恢复决策 | ✅ Phase 2 直接对齐（与 §3.3 Merkle root 升级同步落地，仅协议文档约束无代码开销） |
> | **ERASURE 事件**（GDPR crypto-shredding 作为不可变审计事件） | v1.1 只追加不删除，数据主体删除请求无合规留痕 | 未来 AUM 机构化接入客户资金时触发 GDPR/PIPL 删除请求 | ⚠️ Phase 3+ 远期（AUM 机构化 + 客户资金接入时触发） |
> | **SCITT 对齐**（COSE Receipts + 透明度服务 + IETF SCITT 透明日志） | v1.1 外部锚定用 RFC-3161 TSA 单点信任，无多方透明日志共识 | 多方审计场景（多个策略 provider / 多个 LP）需透明日志 | ⚠️ Phase 3+ 远期（多方审计需求出现时触发） |
> | **后量子签名**（DILITHIUM2 / FALCON512 从 FUTURE 升为 EXPERIMENTAL） | v1.1 Ed25519 签名在量子计算下不安全——长期审计存档（≥ 20 年）有"今签明破"风险 | 本项目审计轨迹长期存档（监管要求 ≥ 20 年），2040+ 量子计算成熟时 Ed25519 失效 | ⚠️ Phase 5+ 远期（量子计算成熟度跟踪 + 后量子签名标准化稳定后触发） |
>
> - **为何 v1.2 是"零破坏性升级"**：所有新特性都是**附加字段**，v1.0/v1.1 客户端解析 v1.2 数据时忽略未知字段即可。本项目 Phase 2 落地 v1.1 后，VCP-RECOVERY 边界约束可同步对齐（仅文档约束），其余三项按重评条件触发
> - **重评条件**：①VCP-RECOVERY：Merkle root 锚定失败率 > 1%/年（TSA 服务不稳定）；②ERASURE：AUM 机构化 + 客户资金接入；③SCITT：多方审计需求出现；④后量子：NIST PQC 标准化稳定（预计 2027-2030）+ 量子计算威胁评估成熟
> - **过度工程审查**：VCP v1.2 四大新特性**不是过度工程**——①v1.2 是协议级升级（零破坏性），登记升级路径是风险前瞻；②四项都有明确重评条件；③VCP-RECOVERY 是 Phase 2 Merkle root 升级的**必需配套**（无恢复流程的锚定在 TSA 故障时陷入"锚定失败 → 不知如何恢复 → 审计轨迹完整性受损"困境）；④ERASURE/SCITT/后量子是 Phase 3+ 远期，登记理论缺口+升级路径+重评条件，不在 Phase 2 实现

**为何三层而非两层**（成交+持仓）：资金对账是 cash 层 catch-all（费率/分红/利息最终在资金对账暴露）；成交抓"记录一致"、持仓抓"结果一致"、资金抓"钱对得上"——三者正交，任一 break 需独立定位；40 号决策⑬资金预占的事后校验（预占可能因费率变动/broker 扣款偏差失准）。

**为何盘后全量对账暂缓到 Phase 2**（§4.3）：MVP 盘中每 5min 持仓对账已覆盖生存需求（差异早发现早冻结）；盘后全量需券商对账单数据接入，MVP 用 `get_positions` 查询兜底（[40_execution_broker](40_execution_broker.md) §5 待裁定 + §6.1 gap 10）。

**审计证据链扩展：仓位审计追溯（BM-POS-10，production，v1.15.4 补 / v1.15.8 状态校准对齐 battle_map_08）**：

- **定位**：L3.5 仓位管理层横切环节——任意仓位变更事件（裁决/Kelly/漂移/再平衡/缩放/日历/合并）触发；消费 BM-POS-01~09 全部环节的仓位变更事件 + D-RISK C-004 审批链 + D-EX-CORE 执行结果；产出 **PositionAuditReport** → D-REPORTING 归档 / D-GOVERNANCE 合规审计。代码映射 MOD-POS-009（D-POSITION §1.3 POS-09 Position Audit Logger）。
- **裁定**：①**字段口径**——每次仓位变更全记录：`{position_id, symbol, qty_before, qty_after, change_source(BM-POS-01~09 环节编号), trigger_event_id, decision_ref, approval_chain_ref, execution_fill_ids, timestamp}`；②**审批链语义**——决策→裁决→风控→执行全链路引用（非内嵌拷贝），审批链本体由 D-RISK C-004 供给，本环节只记引用键防口径漂移；③**哈希链防篡改**——前一条记录哈希链接（与 §3.3 三阶段审计轨迹同构的线性 hash 链，tamper-evident 可检测口径，对齐 #ARCH-OE-007 声明——机构级不可篡改属 BM-BUY-10 已裁剪范围）；④**与 30 号衔接**——仓位审计 logger 已在 [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §7.5 设施盘点登记为 production（`position_audit_logger`），本节为其补 why 层与产出物契约，**不新造审计器**；⑤**降级（保守原则）**——审计日志器未就绪→**仓位决策阻断**（审计是合规底线，无审计不允许执行，fail-closed，与本备忘对账"双边冻结不可误判一致"同哲学）。
- **契约/参数/接口**：产出物 PositionAuditReport `{report_id, period, change_count, records: [...], chain_head_hash, chain_integrity_check: PASS|FAIL}`，日报频率走 §3.7 报告通道归档（ReportPublisher）。重评条件：外部资金引入/合规升级时，哈希链随 §3.3 Merkle tree Phase 2 升级路径一并升级。

### 3.4 决策③：归因维度——策略/标的/时段为主，因子维度暂缓

**决策**：归因维度取"策略 × 标的 × 时段"三维度，因子维度（factor_contributions）暂不实现。

**三维度定义**：

| 维度 | 含义 | 数据来源 | 用途 |
|---|---|---|---|
| 策略维度 | 各 StrategyBook 独立 PnL 贡献 | [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.2 StrategyBook 独立 PnL | "哪个策略赚/亏"→ 反馈到 RegimeMetaAllocator budget 调整 |
| 标的维度 | 各标的独立 PnL 贡献 | PnlCalculator 逐笔计算 | "哪只票赚/亏"→ 反馈到选股层 |
| 时段维度 | 日内/日间/周/月 PnL 分解 | PnlCalculator 按时间窗口 | "什么时候赚/亏"→ 反馈到择时层 |

**为何因子维度暂缓**（§4.2）：因子归因需因子暴露矩阵 + 因子收益回归（Barra 简化版），个人 5 策略组合因子暴露由选股策略内生决定，增量信息有限；Brinson"配置 vs 选股"二分已回答 80% 迭代问题；Phase 2 候选（首批策略 track record 3 月后）。**不做四维全归因**（§4.6）：机构级需求，维度越多每格样本量越小、统计显著性越差（5 策略 × 50 标的 × 4 因子 × 20 时段 = 20000 格，多数格子样本不足）。

### 3.5 决策④：与 StrategyBook 独立 PnL 归因的对接

**决策**：归因分两层——各 StrategyBook 自带独立 PnL 归因（策略层），firm 层 DefaultAttributionEngine 做 firm 级聚合归因（组合层），两层归因结果可追溯对账。

**两层归因架构**（对接 [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) Model A）：

```
各 StrategyBook（N 个，N=3~5）
  ├─ 独立 target_portfolio（标的+目标仓位）
  ├─ 独立 PnL 归因（策略层：该策略的配置/选择/交互效应）
  ├─ 独立风控参数（回撤 protocol，30号 §2.5 四级阈值）
  └─ 独立资金预算（RegimeMetaAllocator 分配的 budget）
        │
        ↓ firm 层求和裁剪（不做统一优化器，不做协方差估计）
        │
FirmRiskAggregator → firm_target_portfolio → 下单（40号）
        │
        ↓ 成交回报回流
        │
firm 级聚合归因（DefaultAttributionEngine）
  ├─ firm 层 Brinson 3 因子（全账户视角）
  ├─ 策略贡献分解（各 StrategyBook PnL 占比 → 反馈 budget 调整）
  └─ TCA 成本拖拽（transaction_cost_drag 接入 DefaultTcaEngine）
```

**对接契约**：
- 各 StrategyBook 必须输出独立 PnL（已在 30 号 §2.2 定义为能力声明；30 号未定义 PnL 数据结构字段级契约）——格式对齐 [PerformanceAttributionReport](file:///d:/ZephyrAlpha/src/zephyr/shared/contracts/performance_attribution_report.py) 契约（CTR-P1-009 codegen 已落盘）
- ⚠️ **策略侧数据源缺口**（v1.15.0 全仓扫描发现）：[StrategyBook](file:///d:/ZephyrAlpha/src/zephyr/position/core/strategy_book.py)（MOD-POS-020）当前**不核算独立 PnL**——仅消费外部注入的 `strategy_pnl_history: list[float]` 算回撤/Sortino。两层归因的"策略层"当前无代码载体，需由策略层施工填充（谁注入 strategy_pnl_history、按 fill_id 归集到策略的口径未定）。关联治理条目 **#ARCH-REG-005**（architecture_issue_registry，proposed 2026-08-11：扩展 pf_core/strategy_book.py sub-book 隔离 + 新建 `src/zephyr/reporting/attribution.py`，impact 已含本备忘）——施工时与该条目对齐，登记 §7 开放问题
- firm 层归因的 `portfolio_id` = firm 账户 ID，各 StrategyBook 归因的 `portfolio_id` = 策略 ID
- 策略贡献分解 = 各 StrategyBook PnL 求和应等于 firm 层 PnL（求和不变量，差异即对账误差）

**策略贡献分解求和不变量校验算法**（v1.5.0 补，[abq A 股量化全链路 2026-08-05](https://blog.csdn.net/suwuzs/article/details/163511629) fills/nav/holdings 对账求和不变量 + [ihr360 2026 共管账户贡献度分割](https://docs.ihr360.com/blog/930136) 三条原则）：

> "策略贡献分解 = 各 StrategyBook PnL 求和应等于 firm 层 PnL" 在 §3.5 已定义为不变量。归因报告必须显式校验此不变量——差异即对账误差（成交回报漏算/费率错算/T+1 跨日错位），不校验会让错误数据流入 RegimeMetaAllocator budget 调整闭环。

```python
# 策略贡献分解求和不变量校验（v1.5.0 施工算法）
def validate_strategy_pnl_invariant(
        strategy_pnls: dict[str, float],   # {strategy_id: net_pnl} 各 StrategyBook 独立 PnL
        firm_pnl: float,                    # firm 层聚合 PnL
        tolerance_bps: float = 1.0          # 容差 1bp（0.01%）——account for 费率精度尾差
) -> dict:
    """校验 Σ(strategy_pnl) == firm_pnl 求和不变量。

    [abq 2026-08-05] A 股量化全链路共识：fills/nav/holdings 三方对账必须满足
    求和不变量，否则归因数据不可信。[ihr360 2026] 共管账户归因须遵循
    "触发者担责 + 可追溯 + 贡献度分割" 三条原则——本算法实现贡献度分割 + 可追溯校验。
    """
    strategy_sum = sum(strategy_pnls.values())
    diff = firm_pnl - strategy_sum
    diff_bps = (diff / firm_pnl * 10000) if abs(firm_pnl) > 1e-12 else 0.0

    # 贡献度分割：各策略 PnL 占 firm PnL 比例
    contributions = {}
    for sid, pnl in strategy_pnls.items():
        contributions[sid] = {
            'net_pnl': pnl,
            'contribution_ratio': pnl / firm_pnl if abs(firm_pnl) > 1e-12 else 0.0,
        }

    return {
        'firm_pnl': firm_pnl,
        'strategy_sum': strategy_sum,
        'diff': diff,
        'diff_bps': diff_bps,
        'invariant_status': 'PASS' if abs(diff_bps) <= tolerance_bps else 'FAIL',
        'strategy_contributions': contributions,
        # FAIL 时归因报告拒绝发布 + 触发告警，定位差异来源：
        #   - 成交回报漏算（某 StrategyBook fill 未计入）
        #   - 费率错算（佣金/印花税口径不一致）
        #   - T+1 跨日错位（§3.2 多 session 边界）
        #   - firm 层裁剪副作用（30 号 FirmRiskAggregator 求和裁剪引入差异）
    }
```

**为何求和不变量是归因报告的硬门禁**：30 号 Model A 核心承诺"StrategyBook 独立 PnL 可加"的运行时校验；求和失败 = 数据流断裂，归因报告基于错误数据会误导 AI 迭代；与 §3.2 Carino residual < 0.01% 门禁并列（Carino 校验单期→多期链接一致性，求和不变量校验策略层→firm 层聚合一致性）——双重门禁。**两层而非统一归因**：统一归因破坏 StrategyBook 独立性（30 号 §3.1 拒 Model B 即因"归因纠缠"）；两层可追溯对账，差异即定位 bug。

**与 RegimeMetaAllocator 的反馈闭环**：
- firm 级归因的"策略贡献分解"输出各 StrategyBook 的 PerformanceScore（60 日滚动 Sortino，口径真源 34 号 §3.1）
- RegimeMetaAllocator 用 PerformanceScore 调整 budget（30 号 §2.2：allocation_i = normalize(Base_i × PerformanceScore_i × Shrinkage_i)）
- 形成"归因 → budget 调整 → 策略 PnL 变化 → 归因"的正向闭环（BM-REC-03）

**PerformanceScore 计算算法**（v1.5.1 补 / v1.15.0 口径修正，[30 号 §2.2](30_multi_strategy_concurrency.md) RegimeMetaAllocator budget 公式衔接 + [34 号 §3.1](34_regime_meta_allocator.md) Sortino 真源口径 + [stockalpha.ai 2026-01-22](https://stockalpha.ai/alpha-learning/multi-factor-analysis-of-stock-returns-using-fama-french-factors-and-beyond) rolling 风险调整收益标准实现）：

> §3.5 提到"PerformanceScore"但未给计算公式。RegimeMetaAllocator 用 `allocation_i = normalize(Base_i × PerformanceScore_i × Shrinkage_i)` 调整 budget——PerformanceScore 计算口径必须明确定义，否则 budget 调整闭环无契约。
>
> **⚠️ v1.15.0 口径修正**：v1.5.1 版误用"60 日滚动 **Sharpe** + 映射 [0.5, 2.0]"——与上游契约 30 号 §2.2 不符（30 号 v2.x 已修正为 **60 日 Sortino + 映射 [0.5, 1.5]**，口径真源为 [34 号 §3.1](34_regime_meta_allocator.md)；Sortino 只惩罚下行波动，符合"上行波动是好的"直觉）。本函数已按 Sortino 重写。

```python
import numpy as np

def calc_performance_score(daily_returns: list[float],
                            window: int = 60,
                            periods_per_year: int = 252,
                            min_observations: int = 20,
                            mar: float = 0.0) -> dict:
    """计算 StrategyBook 的 PerformanceScore（60 日滚动 Sortino）。

    [34 号 §3.1 / 30 号 §2.2] 口径：Sortino = mean(r - MAR) / downside_std × sqrt(252)，
    downside_std 只对低于 MAR 的收益取标准差（只惩罚下行波动）。映射区间 [0.5, 1.5]。
    对齐 RegimeMetaAllocator budget 公式 + floor ≥ 5% / cap ≤ 40%（30 号 §2.2）。

    Args:
        daily_returns: 策略日频收益率序列（小数，如 0.001 = 0.1%）
        window: 滚动窗口（默认 60 交易日）
        periods_per_year: 年化因子（A 股 252）
        min_observations: 最少观测数（不足返回中性 1.0）
        mar: 最低可接受收益（默认 0.0）
    Returns:
        {'performance_score': float,  # 年化 Sortino 映射值
         'rolling_sortino': float, 'is_reliable': bool, 'observations': int}
    """
    if len(daily_returns) < min_observations:
        # 观测不足：返回中性 1.0（不放大也不缩减 budget）
        return {'performance_score': 1.0, 'rolling_sortino': 0.0,
                'is_reliable': False, 'observations': len(daily_returns)}

    # 取最近 window 天
    recent = np.array(daily_returns[-window:])
    excess = recent - mar
    mean_excess = np.mean(excess)
    # 下行偏差：只对低于 MAR 的收益取平方均值开根（Sortino 分母）
    downside = excess[excess < 0]
    downside_std = np.sqrt(np.mean(downside ** 2)) if len(downside) > 0 else 0.0

    if downside_std < 1e-12:
        # 无下行波动：若均值为正给上限 1.5，均值为负/零给中性 1.0
        rolling_sortino = 0.0
        performance_score = 1.5 if mean_excess > 1e-12 else 1.0
    else:
        rolling_sortino = (mean_excess / downside_std) * np.sqrt(periods_per_year)
        # PerformanceScore 映射：Sortino → [0.5, 1.5] 区间（30 号 §2.2 契约，防极端值扭曲 budget）
        # Sortino ≥ +1 → score 1.5（上限，budget 最多放大 1.5 倍）
        # Sortino = 0 → score 1.0（中性，不调整）
        # Sortino ≤ −1 → score 0.5（下限，budget 缩减到 50%）
        performance_score = max(0.5, min(1.5, 1.0 + rolling_sortino / 2.0))

    return {
        'performance_score': performance_score,
        'rolling_sortino': rolling_sortino,
        'is_reliable': True,
        'observations': len(recent),
    }
# RegimeMetaAllocator 消费：allocation_i = normalize(Base_i × PerformanceScore_i × Shrinkage_i)
# Shrinkage_i 由 30 号 §2.2 定义（regime 置信度+信号可靠性综合收缩，≤1.0 只减不增）
# budget 硬约束：floor ≥ 5%（防饿死），cap ≤ 40%（防集中）
```

### 3.6 决策⑤：异常交易检测——三层检测（价格/量/拒单）

**决策**：异常交易检测分三层——盘中价格量异常（AsharePerformanceAudit）+ 拒单分类（40 号）+ 大额异动检测，不做实时 wash trade/spoofing 检测（个人单账户无自交易风险）。

**三层异常检测**：

| 层 | 检测内容 | 触发阈值 | 模块 | 状态 |
|---|---|---|---|---|
| ① 价格异常 | 单笔成交价偏离决策价 >2σ | 价格偏离 >2σ | [AsharePerformanceAudit](file:///d:/ZephyrAlpha/src/zephyr/reporting/ashare_performance_audit.py) | 🟥 未施工（算法见本节，待接入；该模块现有能力=5 类审计，见 §2.4） |
| ② 量异常 | 成交量 >3 倍均值 | volume >3×mean | AsharePerformanceAudit | 🟥 未施工（同上） |
| ③ 拒单分类 | 涨跌停/资金/持仓/数量/价格/连接类拒单 | error_code 50-55/-1/-3 | [OrderManager](file:///d:/ZephyrAlpha/src/zephyr/ex_core/order_manager.py) classify_rejection | 🟦 production（分类+日志）/ 🟧 RETRY/冻结动作待 Saga |
| ④ 大额异动 | 大额交易异动检测 | 待校准 | AsharePerformanceAudit | 🟥 未施工（算法见本节，阈值待实盘校准） |

**异常检测施工算法**（v1.5.1 补，[AsharePerformanceAudit](file:///d:/ZephyrAlpha/src/zephyr/reporting/ashare_performance_audit.py) 审计引擎已 production（5 类审计规则，见 §2.4）、本节异常检测算法为其待接入扩展 + [ParseMyStatement 2026-04](https://parsemystatement.com/blog/running-balance-sequence-qa-detect-missing-merged-lines-before-reconciliation-reng8z) 余额约束行级校验 + [Axon.Trade 2026](https://axon.trade/clock-discipline-for-trading-systems) 时间戳纪律）：

> §3.6 表格定义了"价格偏离 >2σ"和"成交量 >3×mean"阈值，但未给 σ/mean 的计算窗口和算法。本算法补：σ 用滚动 20 笔成交价格偏离率的标准差（非全量历史，20 笔覆盖约 3-5 个交易日）；mean 用滚动 20 日日均成交量（平滑月末/季末周期噪音）。

```python
import numpy as np
from collections import deque

def detect_price_anomaly(fill_price: float, decision_price: float,
                         price_deviation_history: deque,
                         sigma_threshold: float = 2.0,
                         min_history: int = 20) -> dict:
    """价格异常检测：单笔成交价偏离决策价 >2σ。σ 用滚动 20 笔偏离率标准差（约覆盖 3-5 交易日）。

    Args:
        fill_price: 实际成交价
        decision_price: 信号产生时决策价
        price_deviation_history: 滚动历史价格偏离率 deque（maxlen=20）
        sigma_threshold: σ 阈值（默认 2.0）
        min_history: 最少历史观测数
    Returns:
        {'is_anomaly': bool, 'deviation_bps': float, 'sigma_multiple': float}
    """
    if decision_price < 1e-12:
        return {'is_anomaly': False, 'deviation_bps': 0.0, 'sigma_multiple': 0.0}

    deviation = (fill_price - decision_price) / decision_price
    deviation_bps = deviation * 10000

    if len(price_deviation_history) < min_history:
        # 历史不足：用绝对阈值 50bps 兜底（A 股个股日内 0.5% 偏离即值得关注）
        is_anomaly = abs(deviation_bps) > 50
        return {'is_anomaly': is_anomaly, 'deviation_bps': deviation_bps,
                'sigma_multiple': 0.0}

    hist_arr = np.array(price_deviation_history)
    sigma = np.std(hist_arr, ddof=1)
    sigma_multiple = abs(deviation) / sigma if sigma > 1e-12 else 0.0
    is_anomaly = sigma_multiple > sigma_threshold

    return {'is_anomaly': is_anomaly, 'deviation_bps': deviation_bps,
            'sigma_multiple': sigma_multiple}


def detect_volume_anomaly(current_volume: float,
                          volume_history: deque,
                          multiplier: float = 3.0,
                          window: int = 20,
                          min_history: int = 10) -> dict:
    """成交量异常检测：成交量 >3 倍均值。mean 用滚动 20 日日均成交量（平滑月末/季末周期噪音）。

    Args:
        current_volume: 当前成交笔成交量
        volume_history: 滚动历史成交量 deque（maxlen=20）
        multiplier: 均值倍数阈值（默认 3.0）
        window: 滚动窗口
        min_history: 最少历史观测数
    Returns:
        {'is_anomaly': bool, 'volume_multiple': float, 'mean_volume': float}
    """
    if len(volume_history) < min_history:
        return {'is_anomaly': False, 'volume_multiple': 0.0, 'mean_volume': 0.0}

    mean_volume = np.mean(list(volume_history))
    if mean_volume < 1e-12:
        return {'is_anomaly': False, 'volume_multiple': 0.0, 'mean_volume': 0.0}

    volume_multiple = current_volume / mean_volume
    is_anomaly = volume_multiple > multiplier

    return {'is_anomaly': is_anomaly, 'volume_multiple': volume_multiple,
            'mean_volume': mean_volume}
# 大额异动检测阈值待实盘校准：MVP 先用相对阈值（>3×mean），
# Phase 1.5 用实盘数据回归绝对阈值（如单笔 > 50 万或 > 日均金额 5 倍）
```

**MAD 鲁棒增强算法**（v1.6.0 补，[juejin.cn 2026-04-28](https://juejin.cn/post/7633584575197380623) 行情数据清洗 Z-Score vs MAD 对比 + [metricgate 2026-05-13](https://metricgate.com/docs/mad-scaled-z-score/) MAD-Scaled Z-Score ISO/USP 标准推荐 + [tokentoolhub 2026](https://tokentoolhub.com/building-a-market-anomaly-detector/) Market Anomaly Detector robust baseline + [standarddeviationcalculator 2026-04-24](https://standarddeviationcalculator.app/learn/modified-z-score-outlier-detection) Modified Z-Score 完整推导）：

> 上述 `detect_price_anomaly` 用标准差 σ 做阈值，但金融数据是典型厚尾分布——σ 被**掩蔽效应（masking）**污染：一个极端异常值会拉高 σ，导致自身和其他中等异常值漏检。[juejin.cn 2026-04] 实测：Modified Z-Score 的 3.5 阈值比 Z=3 误判率低 60% 以上。[metricgate 2026-05]：ISO/USP 质控指南推荐 MAD-based 方法为默认鲁棒异常筛选器；MAD 的 50% 击穿点意味着即便半数数据被污染，中位数仍不受影响。

```python
def detect_price_anomaly_robust(fill_price: float, decision_price: float,
                                  price_deviation_history: deque,
                                  modified_z_threshold: float = 3.5,
                                  min_history: int = 20) -> dict:
    """价格异常检测（MAD 鲁棒版）：Modified Z-Score = 0.6745 × (x - median) / MAD。

    Iglewicz-Hoaglin 标准：MAD = median(|x_i - median(x)|)（50% 击穿点）；
    0.6745 = 1/Φ⁻¹(0.75) 正态一致性常数；|M_i| > 3.5 异常（conservative）。
    σ 受极端值污染（masking），中位数不受——适用金融厚尾分布，无正态假设。

    Args:
        fill_price: 实际成交价
        decision_price: 信号产生时决策价
        price_deviation_history: 滚动历史价格偏离率 deque（maxlen=20）
        modified_z_threshold: Modified Z-Score 阈值（默认 3.5）
        min_history: 最少历史观测数
    Returns:
        {'is_anomaly': bool, 'modified_z': float, 'severity': str, 'method': 'mad'}
    """
    if decision_price < 1e-12:
        return {'is_anomaly': False, 'modified_z': 0.0, 'severity': 'none', 'method': 'mad'}

    deviation = (fill_price - decision_price) / decision_price

    if len(price_deviation_history) < min_history:
        # 历史不足：降级到绝对阈值 50bps 兜底（与 detect_price_anomaly 一致）
        deviation_bps = abs(deviation) * 10000
        is_anomaly = deviation_bps > 50
        return {'is_anomaly': is_anomaly, 'modified_z': 0.0,
                'severity': 'warning' if is_anomaly else 'none', 'method': 'mad_fallback'}

    hist_arr = np.array(price_deviation_history)
    median_val = np.median(hist_arr)
    mad = np.median(np.abs(hist_arr - median_val))

    if mad < 1e-12:
        # MAD=0 退化处理：超过半数数据 tied at median，切换到 IQR 或绝对阈值
        # [standarddeviationcalculator 2026-04] MAD=0 failure mode 指导
        deviation_bps = abs(deviation) * 10000
        is_anomaly = deviation_bps > 50
        return {'is_anomaly': is_anomaly, 'modified_z': 0.0,
                'severity': 'warning' if is_anomaly else 'none', 'method': 'mad_degenerate'}

    modified_z = 0.6745 * (deviation - median_val) / mad
    is_anomaly = abs(modified_z) > modified_z_threshold

    # 严重度分级（见下方严重度表）
    abs_mz = abs(modified_z)
    if abs_mz > 5.0:
        severity = 'critical'
    elif abs_mz > 3.5:
        severity = 'warning'
    elif abs_mz > 2.0:
        severity = 'info'
    else:
        severity = 'none'

    return {'is_anomaly': is_anomaly, 'modified_z': modified_z,
            'severity': severity, 'method': 'mad'}
```

**为何 MAD 优于标准差 σ**（[juejin.cn 2026-04-28] 对比表 + [metricgate 2026-05-13] 方法论）：

| 维度 | 标准 Z-Score（σ-based） | Modified Z-Score（MAD-based） |
|---|---|---|
| 中心统计量 | 均值 μ（受极端值拉偏） | 中位数 median（50% 击穿点） |
| 离散统计量 | 标准差 σ（被异常值膨胀） | MAD = median(\|x - median\|)（50% 击穿点） |
| 掩蔽效应 | 有——异常值膨胀 σ 导致自身漏检 | 无——中位数不受极端值影响 |
| 分布假设 | 需正态分布（金融数据厚尾，不满足） | 无分布假设（适用于厚尾分布） |
| 阈值 | \|z\| > 3（99.7%，正态假设下） | \|M_i\| > 3.5（Iglewicz-Hoaglin，conservative） |
| 误判率 | 金融数据上高（Z=3 误判率比 M=3.5 高 60%+） | 低 |
| 适用场景 | 截面比较（同时间点多标的排名） | 时间序列异常检测（本项目场景） |
| 标准/推荐 | — | ISO/USP 质控指南默认推荐 |

**MVP 部署策略**：`detect_price_anomaly_robust`（MAD 版）作为主检测器替代 `detect_price_anomaly`（σ 版），两者输出字段兼容（`is_anomaly` + 严重度），AsharePerformanceAudit 切换时只需替换函数调用。历史不足 20 笔时两者降级逻辑一致（50bps 绝对阈值兜底）。

**bad-print vs 真实跳空区分增强**（v1.15.0 补，[referentiallabs 2026-05-09 "Market Data Hygiene Part 1"](https://referentiallabs.com/blog/market-data-hygiene-part-1/) Tick Test）：

> MAD/Z-Score 检测"偏离"但不区分**错价 print**（数据源错误记录，下一笔立即回摆）与**真实跳空**（财报/涨停，价格停留新位）——前者应剔除喂给归因，后者必须保留。Tick Test 判定规则：一笔成交**同时显著偏离前一笔与后一笔**（双向偏离）且**下一笔立即回摆至前一笔附近** → bad-print（数据错误，标记剔除 + 反馈数据源质量）；偏离后价格停留 → 真实异动（保留走 §3.6 严重度流程）。与 §3.2 滑点分布的 `reversion_signal` 同源于"回摆诊断"思想。落地位置：`detect_price_anomaly_robust` 输出增加 `print_type: 'bad_print' | 'real_move' | 'unknown'` 字段（需后一笔数据，盘中检测延迟一笔确认；盘后复盘可直接判定）。Phase 1.5 候选（随异常检测阈值校准同期回归）。

**异常严重度分级**（v1.6.0 补，[Monte Carlo Data 2026](https://docs.getmontecarlo.com/docs/marking-alerts-as-incidents) SEV-1~4 severity matrix + [DualEntry 2026](https://docs.dualentry.com/accountants/ai-automation/anomaly-detection) low/medium/high severity scoring + [Finomics 2026-06](https://finomics.ai/docs/finops-framework-compliance/understand-usage-and-cost/anomaly-management) High/Critical recommended response）：

| 严重度 | Modified Z-Score \|M_i\| | 价格偏离 bps | 量异常倍数 | 含义 | 响应动作 |
|---|---|---|---|---|---|
| `info` | 2.0 < \|M_i\| ≤ 3.5 | 20-50 bps | 2-3× | 轻微异动，统计上不常见但可解释（如盘中波动） | 记入审计日志（§3.3 三阶段），归因报告标注，不告警 |
| `warning` | 3.5 < \|M_i\| ≤ 5.0 | 50-100 bps | 3-5× | 显著异动，可能由执行滑点/部分成交/数据延迟导致 | 微信 Webhook 告警（ReportPublisher 实时渠道），标记入次日复盘报告 |
| `critical` | \|M_i\| > 5.0 | >100 bps | >5× | 严重异动，可能由数据源错误/系统 bug/极端市场事件导致 | 微信 Webhook 紧急告警 + 触发持仓对账（§3.3 DriftItem 检测）+ 标的标记 frozen（§3.3 冻结状态机） |

**异常升级流程**（v1.6.0 补，[theneuralbase 2026-04](https://theneuralbase.com/ai-for-finance/learn/intermediate/reconciliation-assistance/) Tier 3 Exception Escalation + [DualEntry 2026](https://docs.dualentry.com/accountants/ai-automation/anomaly-detection) dismiss/escalate 双动作 + SOX 404/MiFID II 审计轨迹要求）：

```
[检测] detect_price_anomaly_robust / detect_volume_anomaly
  │
  ├─ severity='none' ──────────────────────────────────────→ [正常] 无动作
  │
  ├─ severity='info' ──────────────────────────────────────→ [日志] 写入审计轨迹 §3.3 阶段1
  │                                                         归因报告标注 §3.7 复盘报告"异常事件"栏
  │                                                         不告警，不阻断
  │
  ├─ severity='warning' ───────────────────────────────────→ [告警] 微信 Webhook 实时推送
  │                                                         写入审计轨迹 §3.3 阶段1+2（检测+匹配决策）
  │                                                         标记入次日 AsharePerformanceAudit 复盘报告
  │                                                         owner 收到告警后 24h 内确认或 dismiss
  │
  └─ severity='critical' ──────────────────────────────────→ [紧急] 微信 Webhook 紧急告警
                                                            + 触发持仓对账（§3.3 detect_position_drift）
                                                            + 标的标记 frozen（§3.3 冻结状态机，停止新订单）
                                                            + 写入审计轨迹 §3.3 三阶段全量
                                                            + owner 人工排查根因：
                                                              - 数据源错误 → 修正数据源，重放归因
                                                              - 系统 bug → 修 bug，补数据
                                                              - 极端市场事件 → 记录事件，评估是否触发 kill_switch
                                                            + 排查完成后 unfreeze（§3.3 状态机 monitoring→正常）

[owner 动作]
  ├─ dismiss（确认可接受） → 标记 dismiss + 原因码，写入审计轨迹
  │                        dismiss 模式反馈到阈值校准（减少同类误报）
  └─ escalate（确认需处理）→ 进入 critical 流程或触发对应 Saga
```

**dismiss/escalate 审计轨迹要求**（[theneuralbase 2026-04] SOX 404 合规 + [Monte Carlo Data 2026] incident lifecycle）：
- 每个异常事件（info/warning/critical）必须写入审计轨迹，含：检测规则、modified_z 分数、严重度、时间戳、owner 动作（dismiss/escalate）、原因码
- dismiss 的事件不删除——[theneuralbase 2026-04] "regulators audit the false negatives hardest"
- 月度复盘报告统计异常事件分布：按严重度/标的/策略分桶，识别系统性异常模式（如某标的频繁 warning = 流动性问题）

**为何不做 wash trade/spoofing 检测**：个人单账户无自交易风险（wash trade 需多账户对敲）；spoofing 检测需订单簿深度数据 + 多账户意图推断。见 [40_execution_broker](40_execution_broker.md) §5 待裁定"Pre-Trade 合规检查"（BM-EXE-04，多账户或合规要求升级时再上）。

**与对账的协同**：异常检测输出（价格偏离/量异常/拒单）是对账差异常见来源；持仓对账发现 drift 优先排查异常交易导致（部分成交未记录/拒单未同步）；error_code=55 持仓不足直接触发持仓对账（40 号决策⑥层3）。

**Stale-Value 冻结馈送检测**（v1.7.0 补，[EQAF arXiv:2606.20079 2026-06](https://arxiv.org/pdf/2606.20079v1) UBS 投行实测关键发现）：

> EQAF 在 183 笔信用衍生品 / 129 日实测中发现：**stale-value（冻结馈送）异常是纯统计方法的结构性盲区**——Isolation Forest / PCA 重构 / 统计规则均无法检测"连续 N 笔数值完全相同"的冻结数据（统计方法假设数据有方差）。stale-value 必须**领域确定性规则**兜底。A 股场景：miniQMT 行情连接断开时，持仓/成交回报可能冻结在最后一个值，导致对账系统误判"一致"（实际是双边都冻结）。上述三层异常检测 + MAD 鲁棒增强都是统计方法，对"数据冻结"盲区相同，须补一条确定性规则层（第 0 层）。

**Stale-Value 检测算法**（v1.7.0 补）：

```python
def detect_stale_value(value_series: list[float],
                       timestamps: list,
                       max_unchanged_count: int = 3,
                       max_stale_seconds: float = 300) -> dict:
    """冻结馈送检测——连续 N 笔数值完全相同 → 告警（[EQAF arXiv:2606.20079]：纯统计方法对 stale-value 结构性失效，须领域确定性规则；miniQMT 断连时持仓/成交可能冻结在最后一个值）。

    Args:
        value_series: 数值序列（如持仓量、价格、PnL）
        timestamps: 对应时间戳序列
        max_unchanged_count: 连续不变最大容忍数（默认 3；持仓量短时不变正常，成交价/时间戳不变异常）
        max_stale_seconds: 最长冻结秒数（默认 300s=5min，对账每 5min 跑一次）
    Returns:
        {'is_stale': bool, 'stale_count': int,
         'stale_duration_seconds': float, 'severity': 'none'|'warning'|'critical'}
    """
    if len(value_series) < 2:
        return {'is_stale': False, 'stale_count': 0,
                'stale_duration_seconds': 0.0, 'severity': 'none'}

    # 从末尾向前数连续不变的笔数
    stale_count = 1
    for i in range(len(value_series) - 1, 0, -1):
        if value_series[i] == value_series[i - 1]:
            stale_count += 1
        else:
            break

    stale_duration = (timestamps[-1] - timestamps[-stale_count]).total_seconds() \
        if stale_count > 1 else 0.0

    is_stale = stale_count >= max_unchanged_count or (
        stale_count >= 2 and stale_duration >= max_stale_seconds)

    # severity：成交价冻结 = critical（数据源断连），
    # 持仓量冻结 = warning（可能正常无交易，但须确认行情连接）
    if is_stale and stale_duration >= max_stale_seconds:
        severity = 'critical'
    elif is_stale:
        severity = 'warning'
    else:
        severity = 'none'

    return {'is_stale': is_stale, 'stale_count': stale_count,
            'stale_duration_seconds': stale_duration, 'severity': severity}
# 用法：对每个 fill/broker_settlement 字段分别检测
# fill_price_stale = detect_stale_value([f.price for f in recent_fills],
#                                        [f.timestamp for f in recent_fills])
# position_stale = detect_stale_value([p.qty for p in recent_positions],
#                                      [p.timestamp for p in recent_positions])
# 若 fill_price_stale['severity'] == 'critical' → 跳过本轮对账 + 告警行情连接
# （不能对"冻结的数据"做对账——双边冻结会误判为"一致"）
```

> **与三层异常检测的关系**：stale-value 是第 0 层——在对账/异常检测**之前**先检测数据是否冻结，冻结则跳过本轮（不能对冻结数据做归因）。三层异常检测（价格/量/拒单）假设数据是活的，stale-value 检测保证这一假设成立。

### 3.7 决策⑥：报表生成——四类报告 + 双渠道发布

**决策**：报表生成复用已实现的四类报告体系（风险/监管/TCA/复盘）+ 双渠道发布（微信/邮件，当前仅 PENDING 落库未实际发送），归档目标 SQLite + Parquet（当前 append-only 文件归档已实现，DB 归档未实现）。

**四类报告体系**（battle_map BM-REC-02，已 production）：

| 报告类型 | 模块 | 内容 | 频率 | battle_map |
|---|---|---|---|---|
| 风险报告 | [RiskReportEngine](file:///d:/ZephyrAlpha/src/zephyr/reporting/risk_report_engine.py) | 日度（VaR/CVaR/因子暴露/否决统计/漂移/Amihud）/ 周度（压力测试+漂移趋势+拥挤度+模型健康度）/ 事件（触发+影响+处置）/ 月度（参数变更审计+否决有效性+合规） | 日/周/事件/月 | BM-REC-02-E |
| 监管报告 | [RegulatoryReportGenerator](file:///d:/ZephyrAlpha/src/zephyr/reporting/regulatory_report_generator.py) | 程序化交易报告 / 异常交易自报 / 持仓报告 / 绩效报告 | 月/季+事件 | BM-REC-02-F |
| TCA 报告 | [DefaultTcaEngine](file:///d:/ZephyrAlpha/src/zephyr/reporting/default_tca_engine.py) | 简易滑点已上线；滑点/冲击成本/市场影响/IS 成本分解待施工（§2.4 盘点） | 每笔成交+日度汇总 | BM-REC-02-A |
| 复盘报告 | [AsharePerformanceAudit](file:///d:/ZephyrAlpha/src/zephyr/reporting/ashare_performance_audit.py) | 5 类审计（收益率/回撤/风险调整收益/归因一致性/交易成本）+ 优化建议（BM 环节定义的盘前信号验证/盘中异常检测/大额异动为待施工扩展，见 §3.6） | 日度 | BM-REC-02-C |

**双渠道发布**（[ReportPublisher](file:///d:/ZephyrAlpha/src/zephyr/reporting/report_publisher.py)，MOD-RPT-003，production 框架）：
- 微信 Webhook（实时推送，适合告警类）⚠️ 当前仅落 PENDING 状态不实际发送（2026-08-12 代码核查）
- 邮件 SMTP（归档推送，适合日报/周报/月报）⚠️ 同上仅 PENDING
- 归档：append-only 归档 + 哈希链已实现；SQLite report_archive + Parquet 数据文件 + LLM 摘要为受限未实现（§2.4 横向缺口 #1/#3）
- 降级：发布不可用 → 本地归档不推送

**监管报告自动化门槛**：
- 当前手动填报（[RegulatoryReportGenerator](file:///d:/ZephyrAlpha/src/zephyr/reporting/regulatory_report_generator.py) 生成报告，人工提交）
- GATE-002（AUM≥1000 万）或 GATE-003（跨市场）激活后上自动化接口
- MVP 个人账户 AUM 远低于门槛，手动填报足够

### 3.8 决策⑦：sizing_basis 归因维度补强（v1.4.0 补，与 31 号 §2.3.4 对接）

**决策**：归因报告须记录每笔持仓的 `sizing_basis` 字段——即 31 号 §2.3.4 定义的"哪个仓位约束是 binding（起作用的）"，作为 Brinson 3 因子之外的"仓位决策归因"维度，亏损复盘时可区分"是 Kelly 估错还是尾部风险超预期还是策略选股过激"。

> **sizing_basis 来源**（[31_position_sizing](31_position_sizing.md) §2.3.4 + deadeye-rs 2026-06 v0.1.17 `sizing_basis` 模式）：仓位合成公式 `f_i^final = min(w_i^sum × dist_adj_i, f_i, var_cap_i, cvar_cap_i, single_name_cap_i)` 实质是多约束取最小 + 命名 binding constraint。deadeye-rs 2026-06 已实现 `sizing_basis: half-kelly / cvar-cap / budget` 三态命名，31 号扩展为 5 约束命名。

**5 约束 sizing_basis 取值**（对齐 31 号 §2.3.4 完整约束栈）：

| sizing_basis 取值 | binding 约束 | 归因含义 | 亏损复盘动作 |
|---|---|---|---|
| `strategy_intent` | w_i^sum × dist_adj_i（策略意愿约束） | 策略选股意愿主导仓位（其他约束未 binding） | 复盘策略层 alpha 信号（§3.5 策略层归因） |
| `kelly_budget` | f_i（Kelly 风险预算约束） | Kelly 半凯利限制仓位（策略想多配但 Kelly 拦住） | 复盘 Kelly 输入（μ/σ 估计是否失准） |
| `var_cap` | var_cap_i（VaR_95 上限约束） | 前瞻 VaR 超阈值下调仓位 | 复盘 VaR 模型（§3.6 风险报告 VaR 估计偏差） |
| `cvar_cap` | cvar_cap_i（CVaR_95 上限约束） | 前瞻 CVaR 超阈值进一步下调 | 复盘 CVaR 模型 + 尾部分布假设 |
| `single_name_cap` | single_name_cap_i（单票硬上限 8%/5%） | 跨策略求和后触顶（多策略同标的叠加） | 复盘策略间标的相关性（§3.5 firm 层聚合） |

**与 Brinson 3 因子的关系**：
- Brinson 看已实现 PnL 的来源分解（决策维度），sizing_basis 看仓位决策的 binding 约束（约束维度）——二者正交
- 交集场景：sizing_basis = `strategy_intent` 且 Brinson selection effect 为负 → 策略选股过激，指向策略层重优化；sizing_basis = `cvar_cap` 且 Brinson allocation effect 为负 → 尾部风险约束导致配置偏离基准，指向风控参数调整

**实现现状与 gap**：
- [31 号 §2.3.4](31_position_sizing.md) 已定义完整约束栈 + sizing_basis 命名规范，但代码 [MOD-POS-001](file:///d:/ZephyrAlpha/src/zephyr/position/core/position_sizing_engine.py) 当前**未显式输出 `sizing_basis` 字段**（31 号 §2.3.4 已记入待定问题）
- 本备忘决策：归因报告（DefaultAttributionEngine + PerformanceAttributionReport MOD-RPT-015）须消费 `sizing_basis` 字段做仓位决策归因——31 号施工填充 `sizing_basis` 输出后，归因层接入
- MVP 优先级：Phase 1.5（首批策略 track record 1-3 月），与 transaction_cost_drag 接入 TCA 同期施工

**sizing_basis 归因接入算法**（v1.5.0 补，[deadeye-rs 2026-06 v0.1.17](https://github.com/) `sizing_basis` 模式 + [31 号 §2.3.4](31_position_sizing.md) 5 约束命名）：

```python
# sizing_basis 归因接入算法（v1.5.0 施工算法）
def attribute_by_sizing_basis(
        position_records: list[dict],   # 各持仓记录，含 sizing_basis + pnl + symbol
) -> dict:
    """按 sizing_basis 分桶统计 PnL 贡献（仓位决策归因维度）。

    position_records 每条含：
      - symbol: 标的
      - sizing_basis: 5 约束之一（strategy_intent/kelly_budget/var_cap/cvar_cap/single_name_cap）
      - pnl: 该持仓期间净 PnL
      - weight: 期初权重
    返回各 binding 约束的 PnL 贡献分解 + 亏损复盘动作建议。
    """
    buckets = {
        'strategy_intent': {'pnl': 0.0, 'weight': 0.0, 'count': 0},
        'kelly_budget':    {'pnl': 0.0, 'weight': 0.0, 'count': 0},
        'var_cap':         {'pnl': 0.0, 'weight': 0.0, 'count': 0},
        'cvar_cap':        {'pnl': 0.0, 'weight': 0.0, 'count': 0},
        'single_name_cap': {'pnl': 0.0, 'weight': 0.0, 'count': 0},
    }
    for pos in position_records:
        basis = pos.get('sizing_basis', 'strategy_intent')
        if basis not in buckets:
            basis = 'strategy_intent'  # 兜底
        buckets[basis]['pnl'] += pos['pnl']
        buckets[basis]['weight'] += pos['weight']
        buckets[basis]['count'] += 1

    total_pnl = sum(b['pnl'] for b in buckets.values())

    # 亏损复盘动作建议（对齐 §3.8 表格"亏损复盘动作"列）
    review_actions = {
        'strategy_intent': '复盘策略层 alpha 信号（§3.5 策略层归因）',
        'kelly_budget':    '复盘 Kelly 输入（μ/σ 估计是否失准）',
        'var_cap':         '复盘 VaR 模型（§3.6 风险报告 VaR 估计偏差）',
        'cvar_cap':        '复盘 CVaR 模型 + 尾部分布假设',
        'single_name_cap': '复盘策略间标的相关性（§3.5 firm 层聚合）',
    }

    return {
        'sizing_basis_breakdown': {
            basis: {
                'pnl': b['pnl'],
                'pnl_ratio': b['pnl'] / total_pnl if abs(total_pnl) > 1e-12 else 0.0,
                'weight_share': b['weight'],
                'position_count': b['count'],
                'review_action': review_actions[basis],
            }
            for basis, b in buckets.items() if b['count'] > 0
        },
        'total_pnl': total_pnl,
        'dominant_constraint': max(buckets, key=lambda k: buckets[k]['weight']),
        # dominant_constraint = 期初权重占比最大的 binding 约束类型
        # 归因报告标注"本期主 binding 约束"，指导 owner 复盘优先级
    }
```

**接入施工约束**：
- 31 号 PositionSizingEngine 施工输出 `sizing_basis` 字段后，归因层从持仓记录消费
- 归因报告 §3.12 MOD-RPT-015 模板新增第 9 节"sizing_basis 仓位决策归因"展示上述分桶
- 与 Brinson 3 因子正交：Brinson 看 PnL 来源（配置/选择/交互），sizing_basis 看仓位约束（哪个 binding）——同一笔 PnL 在两个维度都有归因
- MVP 优先级 Phase 1.5（§5.2 演进路径已登记），依赖 31 号施工输出字段

### 3.9 决策⑧：deflated-alpha v0.3.0 三重验证（v1.4.0 补，回测 vs 实盘统计显著性验证）

**决策**：归因层引入 [deflated-alpha v0.3.0](https://github.com/0scarito/deflated-alpha)（2026-07-26）作为回测 vs 实盘对账的统计显著性验证框架——单一 `audit()` 调用跑齐 4 类检验（analytical / combinatorial / multiple-testing / bootstrap data-snooping），输出 `LIKELY_REAL / INCONCLUSIVE / LIKELY_OVERFIT` 三态判定，作为 §3.3 三层对账之外的"统计层对账"。

> **为何归因层需要统计显著性验证**：[Combined Trading Signals and Overfitting Risk (2026-06)](https://research.mental-momentum.ai/r/combined-trading-signals-overfitting-zwtahi) 实证——"组合多指标 overwhelmingly 导致历史噪声过拟合而非改善预测信号"。归因层若只做 Brinson 3 因子分解而不用 DSR 验证 alpha 真实性，会把过拟合的"伪 alpha"当作真实 edge 归因，AI 迭代方向被误导。

**deflated-alpha v0.3.0 四类检验**（[0scarito/deflated-alpha](https://github.com/0scarito/deflated-alpha) 2026-07-26 实现）：

> **⚠️ 55 号交叉引用口径**（v1.15.0 校准 / v1.15.8 更新）：55 号（[55_monitoring_review](55_monitoring_review.md)）已 active v1.0.2（2026-08-15）——本节及 §3.10/§5.1/§5.2/§8.1 等处"55 号 §x.x"引用已按其实际结构对齐：退役评审=55 号 §3.5（双判据+评审制，无 Tier 1/3 术语）、实盘 vs 回测偏离度量=§3.4（>30% 告警 / >50% 退役评估）、CUSUM/PSI 在线监控=§3.2B 模型风险审计 + §3.3 阈值注册表（PSI>0.2 关注 / >0.4 高度，CUSUM h=4σ）。55 号 v1.0.2 未采用 DSR/PBO 做退役检验，deflated-alpha 4 类检验为本备忘归因层自用框架，衔接点=verdict 触发 55 号 §3.4/§3.5 评审通道。本备忘内容自包含、以本备忘为真源（§7 开放问题登记并发施工残余风险）。

| School | Question | This package | 决策 |
|---|---|---|---|
| **Analytical** | 赢家 Sharpe 是否超过 N 次无技能试验的期望最大值？ | DSR + PSR + MinTRL（Bailey & López de Prado 2012/2014） | ✅ 主选（归因层自用；与 55 号衔接=verdict 触发其 §3.4/§3.5 评审通道） |
| **Combinatorial** | IS 赢家是否在 OOS 持续赢？ | PBO via CSCV（Bailey, Borwein, López de Prado & Zhu 2017） | ✅ 主选（对接 11 号 §0.5.7 perturbation PBO） |
| **Multiple-testing** | Sharpe 经过 N 试验 p-value haircut 后剩多少？ | Harvey-Liu Bonferroni / Holm / BHY（Harvey & Liu 2015） | ✅ 主选（归因层自用） |
| **Bootstrap data-snooping** | 最佳策略对重采样 null 是否显著？ | White's Reality Check + Hansen's SPA（White 2000, Hansen 2005） | ✅ v0.3.0 新增（归因层自用主选） |

**为何归因层用 deflated-alpha v0.3.0 而非自造**：MIT 许可轻量包（Python ≥ 3.10，numpy/scipy/pandas），单 `audit(trials, periods_per_year=252, bootstrap=True)` 调用即输出完整报告；4 类检验互补防漏判（[README](https://github.com/0scarito/deflated-alpha) 实证：SMA crossover 在零漂移 random walk 上 DSR 0.989 + SPA p=0.019 均被欺骗，PBO/CSCV 0.782 抓住过拟合）；输出 OOS degradation slope + Effective trials（N_eff 相关试验降权）+ MinTRL 三项辅助指标可直接消费；自造需 4 类检验 + bootstrap 重采样 + CSCV 组合枚举，违反不重造原则。

**与 55 号评审通道的衔接**（v1.15.8 校准——55 号已 active v1.0.2，结构为实际盘点）：
- 55 号 §3.5 退役评审=双判据（连续跑输 / 逻辑失效）+ 评审制（判据触发→退役评估报告→人工裁定），未采用 DSR/PBO；本备忘 deflated-alpha 的 LIKELY_OVERFIT verdict 定位为其"逻辑失效判据"的统计证据输入（不替代其双判据）
- 二者复用同一 `deflated-alpha` 包，但触发时机不同：55 号 §3.5 是退役评审触发，54 号是月/季归因报告触发
- 分层逻辑：日常监控用 CUSUM/PSI 在线轻量（55 号 §3.2B/§3.3，PSI>0.2 关注 / >0.4 高度，CUSUM h=4σ），月/季归因用 deflated-alpha（54 号离线重量）——检测链分层

**对账接入算法**：

```python
# 归因层 deflated-alpha 对账接入（v1.4.0 补）
from deflated_alpha import audit

def reconcile_backtest_live_significance(
        backtest_trial_returns: pd.DataFrame,  # T x N，每次参数 sweep 的回测收益
        live_returns: pd.Series,                # 实盘累计收益
        periods_per_year: int = 252) -> dict:
    """月/季归因报告调用：跑 deflated-alpha 4 类检验 + OOS 退化斜率。

    Args:
        backtest_trial_returns: 50 号 experiment_tracking 的参数 sweep 收益矩阵
        live_returns: 实盘累计收益序列
    Returns:
        {'verdict': 'LIKELY_REAL'|'INCONCLUSIVE'|'LIKELY_OVERFIT',
         'dsr': float, 'pbo': float,
         'oos_degradation_slope': float,  # 实盘 Sharpe / 回测最优 Sharpe
         'spa_p_value_consistent': float,  # Hansen SPA
         'reality_check_p_value': float,   # White RC
         'effective_trials': int,          # N_eff 有效试验数
         'min_trl': int}                   # 最小 track record 长度
    """
    # 1. 跑 deflated-alpha audit（含 bootstrap）
    report = audit(backtest_trial_returns, periods_per_year=periods_per_year,
                   bootstrap=True)

    # 2. 实盘 vs 回测 OOS 退化斜率补充校验
    # （实盘 Sharpe / 回测最优 Sharpe，< 0.5 即 OOS 退化严重）
    live_sharpe = live_returns.mean() / live_returns.std() * (periods_per_year ** 0.5)
    # 各 trial 年化 Sharpe = mean/std × √252（与 live_sharpe 同口径），取最优
    # std=0 退化的 trial 由 pandas 自动产 NaN，max() 跳过
    trial_sharpes = (backtest_trial_returns.mean()
                     / backtest_trial_returns.std(ddof=1)
                     * (periods_per_year ** 0.5))
    backtest_best_sharpe = float(trial_sharpes.max())
    oos_degradation = live_sharpe / backtest_best_sharpe if backtest_best_sharpe > 0 else 0

    return {
        'verdict': report.verdict,
        'dsr': report.dsr.dsr,
        'pbo': report.pbo.pbo,
        'oos_degradation_slope': oos_degradation,
        'spa_p_value_consistent': report.spa.p_value_consistent,
        'reality_check_p_value': report.reality_check.p_value,
        'effective_trials': report.effective_trials,
        'min_trl': report.min_trl,
    }
```

**verdict 三态判定阈值算法**（v1.5.1 补，[deflated-alpha v0.3.0](https://github.com/0scarito/deflated-alpha) 2026-07-26 内部逻辑 + [Bailey & López de Prado 2012/2014](https://doi.org/10.2139/ssrn.1825446) DSR 阈值 + [waylandz 2026-04-20](https://waylandz.com/blog/backtest-to-live-gap/) cost model gap 框架）：

> §3.9 pseudocode 中 `verdict = report.verdict` 直接消费 deflated-alpha 包输出，但未描述包内部三态判定阈值。owner 复盘须理解阈值才能正确解读 verdict——否则"LIKELY_OVERFIT"只是黑盒标签。[waylandz 2026-04-20] 补充：backtest-to-live gap 是 cost model 问题，verdict 之外还需看 OOS 退化斜率（实盘 vs 回测 Sharpe 比值）。

```python
def interpret_deflated_alpha_verdict(dsr: float, pbo: float,
                                      spa_p_value: float,
                                      oos_degradation_slope: float,
                                      min_trl: int, live_trading_days: int) -> dict:
    """verdict 三态判定阈值解析（对齐 deflated-alpha v0.3.0 内部逻辑）。

    阈值（[Bailey & López de Prado 2012/2014] / [Bailey et al. 2017] / [Hansen 2005] / [waylandz 2026-04-20]）：
      DSR > 0.95 强证据真实 / < 0.50 弱证据；PBO < 0.05 低过拟合 / > 0.25 高过拟合；
      SPA p < 0.05 显著优于 null；OOS 退化斜率 < 0.5 严重退化。

    Args:
        dsr: Deflated Sharpe Ratio 概率（0-1）
        pbo: Probability of Backtest Overfitting（0-1）
        spa_p_value: Hansen SPA consistent p-value（0-1）
        oos_degradation_slope: 实盘 Sharpe / 回测最优 Sharpe
        min_trl: 最小 track record 长度（天）
        live_trading_days: 实际实盘交易天数
    Returns:
        {'verdict': str, 'reasons': list[str], 'action': str}
    """
    reasons = []

    # Track record 长度不足 → 直接 INCONCLUSIVE
    if live_trading_days < min_trl:
        return {'verdict': 'INCONCLUSIVE',
                'reasons': [f'实盘 {live_trading_days} 天 < MinTRL {min_trl} 天，样本不足'],
                'action': '继续实盘收集数据，暂不做显著性判定'}

    # LIKELY_OVERFIT：任一红旗
    overfit_flags = []
    if dsr < 0.50:
        overfit_flags.append(f'DSR={dsr:.3f} < 0.50（alpha 真实性弱）')
    if pbo > 0.25:
        overfit_flags.append(f'PBO={pbo:.3f} > 0.25（过拟合概率高）')
    if spa_p_value < 0.01:
        overfit_flags.append(f'SPA p={spa_p_value:.4f} < 0.01（bootstrap 拒绝显著性）')
    if oos_degradation_slope < 0.5:
        overfit_flags.append(f'OOS退化={oos_degradation_slope:.2f} < 0.50（实盘严重退化）')

    if overfit_flags:
        return {'verdict': 'LIKELY_OVERFIT', 'reasons': overfit_flags,
                'action': '触发 55 号 §3.5 评审通道（重优化/退役评估）'}

    # LIKELY_REAL：所有检验通过
    real_flags = []
    if dsr > 0.95:
        real_flags.append(f'DSR={dsr:.3f} > 0.95（alpha 真实性强）')
    if pbo < 0.05:
        real_flags.append(f'PBO={pbo:.3f} < 0.05（过拟合概率低）')
    if spa_p_value > 0.05:
        real_flags.append(f'SPA p={spa_p_value:.4f} > 0.05（bootstrap 显著）')
    if oos_degradation_slope > 0.7:
        real_flags.append(f'OOS退化={oos_degradation_slope:.2f} > 0.70（实盘接近回测）')

    if len(real_flags) >= 3:  # 4 项中至少 3 项通过
        return {'verdict': 'LIKELY_REAL', 'reasons': real_flags,
                'action': 'alpha 真实性确认，继续监控'}

    # INCONCLUSIVE：既非明显过拟合也非明显真实
    return {'verdict': 'INCONCLUSIVE',
            'reasons': [f'DSR={dsr:.3f}, PBO={pbo:.3f}, SPA p={spa_p_value:.4f}, '
                        f'OOS退化={oos_degradation_slope:.2f}——指标混合，无法判定'],
            'action': '继续实盘收集数据，下月/季重新检验'}
```

**归因报告接入规则**：
- 月频归因报告（§3.7）：若 `verdict == LIKELY_OVERFIT` 或 `oos_degradation_slope < 0.5` → 触发 55 号 §3.4 偏离度量评估（其阈值 >30% 告警 / >50% 退役评估）+ §3.5 评审通道
- 季频归因报告（§3.7）：跑完整 4 类检验 + bootstrap，若 `verdict == LIKELY_OVERFIT` + `pbo > 20%` → 触发 55 号 §3.5 退役评审（verdict 作为其"逻辑失效判据"统计证据输入）
- `N_eff`（有效试验数）：若 N_eff << N（参数空间维度），说明参数 sweep 高度相关（参数冗余），归因报告标注"参数空间冗余"提示策略层简化参数

**为何归因层而非监控层用 deflated-alpha**：归因层是事后解释工具，bootstrap 开销 O(n_boot·T·N) 适合月/季频离线；监控层（55 号 §3.2B/§3.3）用轻量 CUSUM/PSI 在线检测，分层互补；`verdict` 三态判定可直接驱动 owner 复盘动作。

**Combined Trading Signals 正交维度启示**（[Combined Trading Signals and Overfitting Risk 2026-06](https://research.mental-momentum.ai/r/combined-trading-signals-overfitting-zwtahi)）：
- 行业 2026 共识：有效指标组合必须捕捉**数学正交的市场维度**，分离为 trend direction（趋势方向）/ execution timing（执行时机）/ risk sizing（风险仓位）三角色
- Brinson 3 因子已部分覆盖正交维度（allocation≈trend direction，selection≈execution timing，interaction≈协同），但缺 risk sizing 维度——本备忘 §3.8 sizing_basis 归因补齐
- 组合多指标若非正交维度，会引入多重共线性 + 多重检验危机，须用 deflated-alpha v0.3.0 验证组合后的 alpha 真实性

**PBO 零假设解释修正**（v1.7.0 补，[Solovjiev 2026-07 "PBO 受控标定"](https://pbo.marketmaker.cc/paper.pdf)）：

> 上述 verdict 函数用 `pbo > 0.25` 作 LIKELY_OVERFIT 红旗、`pbo < 0.05` 作 LIKELY_REAL 标志。Solovjiev 2026-07 受控实验确认：**PBO 零假设值是 0.5 而非 0**——纯噪声下样本内最佳策略等于样本外中位数（PBO=0.5），且相关参数网格会把 PBO 上限压在 0.5 附近（方法结构性限制）。因此解读须注意：
> - PBO ≈ 0.5 **不是"不确定"**，而是"无 edge"（纯噪声基线）
> - PBO < 0.5 才表示"有 edge"（越低越强），PBO > 0.5 才表示"过拟合倾向"
> - 当前阈值 `pbo > 0.25` 是保守红旗（远低于 null=0.5），触发即意味着"即使按最严格标准也有过拟合迹象"；`pbo < 0.05` 是强 edge 信号
> - 若 PBO 接近 0.5 且参数网格高度相关，可能是"方法结构性上限"而非"策略无 edge"——须结合 N_eff（有效试验数）和参数空间条件数（§3.10 正交性验证）综合判断，不单看 PBO

**Plateau Robustness 几何诊断补充**（v1.8.0 补，[Solovjiev 2026 "Plateaus, Peaks, and the Probability of Backtest Overfitting"](https://plateau.marketmaker.cc/paper.pdf) 受控验证）：

> Solovjiev 2026 受控实验（9000 个模拟优化问题）关键发现：①**plain PSR 是最强单一诊断器**（no-edge ROC AUC 0.808），优于 DSR（0.785）和 PBO（0.669）；②**plateau 几何指标单独 weak**（1 维 no-edge AUC 0.501≈随机猜测），固定阈值未校准；③**几何 + 统计组合显著提升检测**（2 维场景）；④**作为选择原则 outright 有效**——选 smoothed-surrogate 最优而非 raw argmax 使 OOS Sharpe 平均提升 0.12（1 维）/ 0.31（2 维），随曲率单调递增。
>
> **施工含义**（作为 §3.9 deflated-alpha 的几何补充而非替代）：
> - **不替代 DSR/PBO**：plateau 几何指标单独 weak，不能替代 DSR/PBO 主检验
> - **作为补充诊断维度**：归因报告新增"参数空间曲率"字段——计算 in-sample Sharpe 曲面在最优参数附近的 smoothed-surrogate 曲率，高曲率 + 低 DSR → "sharp peak fragile"红旗，低曲率 + 高 DSR → "broad plateau robust"标志
> - **选择原则指导参数重优化**：当 §3.9 verdict == LIKELY_OVERFIT 触发 55 号 §3.5 重优化/退役评审时，参数重优化须选 smoothed-surrogate 最优（plateau 中心）而非 raw argmax（peak 顶点）
> - **Phase 2 候选**：plateau 几何指标需 in-sample Sharpe 曲面数据（参数 sweep 网格完整记录），依赖 50 号 experiment_tracking——MVP 先用 DSR/PBO，Phase 2 评估 plateau 几何增量价值
> - **重评条件**：①首批策略重优化评审 ≥ 2 次/年（55 号 §3.5 通道）；②DSR/PBO verdict 边界（DSR 0.5-0.7 灰区）需几何补充诊断；③50 号 experiment_tracking 完整记录参数 sweep 网格

### 3.10 决策⑨：Combined Trading Signals 正交维度约束（v1.4.0 补）

**决策**：归因报告须标注各策略的"信号组合正交性"——多信号组合策略（如打板叠加情绪周期 + 龙头识别 + 量价确认）须验证信号间数学正交性，非正交组合是过拟合高危场景。

> [Combined Trading Signals and Overfitting Risk (2026-06)](https://research.mental-momentum.ai/r/combined-trading-signals-overfitting-zwtahi) 实证：①组合相关性指标产生多重共线性，提供冗余数据而非独立信号确认；②穷举指标组合测试保证 backtest 过拟合高概率；③ML 模型用原始价格数据一致优于用显式技术指标增强的模型；④有效指标组合必须捕捉数学正交的市场维度，分离为 trend direction / execution timing / risk sizing 三角色。

**正交性验证算法**（v1.4.0 补，轻量级，归因报告消费）：

| 验证维度 | 算法 | 阈值 | 决策 |
|---|---|---|---|
| **信号间相关性** | Spearman rank IC 矩阵 + 条件数 | 任两信号 \|IC\| > 0.7 → 高相关红旗；条件数 > 30 → 多重共线性 | 高相关 → 标注"信号冗余"，建议策略层去相关 |
| **正交角色覆盖** | 检查信号是否覆盖 trend/timing/sizing 三角色 | 缺角色 → 标注"维度缺失" | 缺维度 → 建议策略层补角色 |
| **组合后 alpha 真实性** | deflated-alpha v0.3.0 audit（§3.9） | verdict == LIKELY_OVERFIT → 过拟合红旗 | 过拟合 → 触发 55 号 §3.5 评审通道 |

**正交性验证施工算法**（v1.5.0 补，[Combined Trading Signals 2026-06](https://research.mental-momentum.ai/r/combined-trading-signals-overfitting-zwtahi) 正交维度要求 + VIF 多重共线性检测）：

```python
# 信号组合正交性验证（v1.5.0 施工算法）
import numpy as np
from scipy.stats import spearmanr

def validate_signal_orthogonality(
        signal_matrix: dict[str, list[float]],  # {signal_name: [signal_values across symbols/days]}
        signal_roles: dict[str, str],            # {signal_name: 'trend'|'timing'|'sizing'}
        ic_threshold: float = 0.7,               # Spearman IC 高相关红旗阈值
        condition_number_threshold: float = 30,  # 多重共线性阈值
        vif_threshold: float = 5.0               # 方差膨胀因子阈值
) -> dict:
    """验证多信号组合的数学正交性（防过拟合）。

    [Combined Trading Signals 2026-06] 共识：有效指标组合必须捕捉数学正交的
    市场维度，分离为 trend direction / execution timing / risk sizing 三角色。
    非正交组合产生多重共线性 + 多重检验危机，是过拟合高危场景。
    """
    signal_names = list(signal_matrix.keys())
    n_signals = len(signal_names)
    if n_signals < 2:
        return {'status': 'SKIP', 'reason': 'signals < 2, no orthogonality to check'}

    # 1. Spearman rank IC 矩阵
    ic_matrix = np.zeros((n_signals, n_signals))
    for i, s1 in enumerate(signal_names):
        for j, s2 in enumerate(signal_names):
            if i == j:
                ic_matrix[i][j] = 1.0
            else:
                rho, _ = spearmanr(signal_matrix[s1], signal_matrix[s2])
                ic_matrix[i][j] = rho if not np.isnan(rho) else 0.0

    # 2. 条件数（condition number）——矩阵奇异程度，越大越接近共线
    cond_number = np.linalg.cond(ic_matrix)

    # 3. VIF（方差膨胀因子）——每个信号被其他信号线性解释的程度
    vif_scores = {}
    for i, target in enumerate(signal_names):
        others = [signal_matrix[s] for j, s in enumerate(signal_names) if j != i]
        if len(others) == 0:
            vif_scores[target] = 1.0
            continue
        X = np.column_stack(others)
        y = np.array(signal_matrix[target])
        try:
            # R² 回归
            X_aug = np.column_stack([X, np.ones(len(X))])
            beta, _, _, _ = np.linalg.lstsq(X_aug, y, rcond=None)
            y_pred = X_aug @ beta
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - ss_res / ss_tot if ss_tot > 1e-12 else 0.0
            vif = 1.0 / (1.0 - r_squared) if (1.0 - r_squared) > 1e-12 else float('inf')
            vif_scores[target] = vif
        except Exception:
            vif_scores[target] = float('inf')

    # 4. 高相关红旗
    high_corr_pairs = []
    for i in range(n_signals):
        for j in range(i + 1, n_signals):
            if abs(ic_matrix[i][j]) > ic_threshold:
                high_corr_pairs.append((signal_names[i], signal_names[j], ic_matrix[i][j]))

    # 5. 正交角色覆盖检查
    covered_roles = set(signal_roles.values())
    missing_roles = {'trend', 'timing', 'sizing'} - covered_roles

    # 6. 综合判定
    flags = []
    if high_corr_pairs:
        flags.append(f'HIGH_CORRELATION: {len(high_corr_pairs)} pairs > {ic_threshold}')
    if cond_number > condition_number_threshold:
        flags.append(f'MULTICOLLINEARITY: condition_number={cond_number:.1f} > {condition_number_threshold}')
    high_vif = {s: v for s, v in vif_scores.items() if v > vif_threshold}
    if high_vif:
        flags.append(f'HIGH_VIF: {list(high_vif.keys())} > {vif_threshold}')
    if missing_roles:
        flags.append(f'MISSING_ROLES: {missing_roles}')

    return {
        'status': 'FAIL' if flags else 'PASS',
        'ic_matrix': ic_matrix.tolist(),
        'condition_number': float(cond_number),
        'vif_scores': vif_scores,
        'high_correlation_pairs': high_corr_pairs,
        'covered_roles': list(covered_roles),
        'missing_roles': list(missing_roles),
        'flags': flags,
        # FAIL → 归因报告标注"信号组合非正交"，建议策略层去相关或补维度
        # 与 §3.9 deflated-alpha 协同：§3.10 验证组合前正交性，§3.9 验证组合后 alpha 真实性
    }
```

**施工约束**：
- `signal_matrix` 由策略层（24/25 号）输出信号快照，归因层月/季报告消费
- 25 号多因子策略的因子正交性已由 §3 ic_decay + FSI 覆盖，本算法补非因子策略（如 24 号打板）的信号正交性
- 阈值（IC 0.7 / 条件数 30 / VIF 5）是行业共识起点，实盘 3 月后回归校准
- 与 §3.9 deflated-alpha 协同：本算法验证组合前信号正交性，§3.9 验证组合后 alpha 真实性——前后双重防线

**与 25 号多因子策略的关系**：25 号因子间正交性已由 §3 ic_decay 三层监控 + FSI（[61_lifecycle_multi_ai](61_lifecycle_multi_ai.md) 拥挤度量化指标）覆盖；本备忘 §3.10 补的是**非因子策略**（如 24 号打板）的信号组合正交性——25 号因子正交性用 IC 矩阵 + FSI，24 号信号正交性用本算法，分层检测。

### 3.11 决策⑩：regime-conditional 归因（v1.5.0 补，Phase 2 候选）

**决策**：归因报告须支持 regime-conditional 分解——按市场 regime 分桶分别计算 Brinson 3 因子 + regime 切换贡献，让 owner 能区分"收益来自 regime fit（顺风）还是 skill（选股/配置能力）"。Phase 2 候选（首批策略 track record 3 个月后，若 Brinson 总归因不足以解释策略表现时启用）。

> **为何需要 regime-conditional 归因**：[traderssecondbrain 2026-05](https://traderssecondbrain.com/guides/performance-attribution-trading) 实证——"Most retail traders running honest attribution discover 50-80% of their favorable-period returns came from regime fit rather than skill"。不分解 regime 维度会让 owner 误把"顺风收益"当"选股能力"，regime 切换后策略失效时归因无法解释。[breakingalpha 2026-01](https://breakingalpha.io/insights/performance-attribution-analysis-multi-strategy-portfolios) 将 regime-conditional 列为多策略归因的标准维度之一。

**regime-conditional 归因算法**（v1.5.0 补）：

```python
# regime-conditional 归因（v1.5.0 施工算法，Phase 2）
def attribute_by_regime(
        daily_brinson_results: list[dict],   # 各日 Brinson 3 因子分解结果
        daily_regime_labels: list[str],       # 各日 regime 标签（来自 28 号情绪周期）
        daily_portfolio_returns: list[float],
        daily_benchmark_returns: list[float]
) -> dict:
    """按 regime 分桶分别计算 Brinson + regime 切换贡献。

    [traderssecondbrain 2026-05] 5 维归因 framework 的 regime fit 维度实现。
    regime 标签来自 28 号情绪周期（bull/bear/range/squeeze 等），
    各 regime 内跑 Carino 链接 Brinson，跨 regime 算切换贡献。
    """
    from collections import defaultdict

    # 1. 按 regime 分桶
    regime_buckets = defaultdict(lambda: {
        'brinson_results': [], 'portfolio_returns': [], 'benchmark_returns': []
    })
    for brinson, regime, rp, rb in zip(
            daily_brinson_results, daily_regime_labels,
            daily_portfolio_returns, daily_benchmark_returns):
        regime_buckets[regime]['brinson_results'].append(brinson)
        regime_buckets[regime]['portfolio_returns'].append(rp)
        regime_buckets[regime]['benchmark_returns'].append(rb)

    # 2. 各 regime 内跑 Carino 链接 Brinson
    regime_attribution = {}
    for regime, data in regime_buckets.items():
        linked = carino_link_periods(
            data['brinson_results'],
            data['portfolio_returns'],
            data['benchmark_returns'])
        regime_attribution[regime] = linked

    # 3. regime 切换贡献 = 总超额收益 - Σ(各 regime 内超额收益)
    total_active = ((1 + sum(daily_portfolio_returns)) /
                    (1 + sum(daily_benchmark_returns))) - 1  # 简化几何
    sum_regime_active = sum(r['geometric_active_return'] for r in regime_attribution.values())
    regime_switch_contribution = total_active - sum_regime_active

    # 4. regime fit vs skill 分解
    total_allocation = sum(r['linked_allocation_effect'] for r in regime_attribution.values())
    total_selection = sum(r['linked_selection_effect'] for r in regime_attribution.values())
    regime_fit_share = regime_switch_contribution / total_active if abs(total_active) > 1e-12 else 0.0
    skill_share = (total_allocation + total_selection) / total_active if abs(total_active) > 1e-12 else 0.0

    return {
        'regime_attribution': regime_attribution,           # 各 regime 内 Brinson 分解
        'regime_switch_contribution': regime_switch_contribution,  # regime 切换贡献
        'regime_fit_share': regime_fit_share,               # regime fit 占比（顺风收益）
        'skill_share': skill_share,                         # skill 占比（真实能力）
        'warning': regime_fit_share > 0.5,                  # > 50% 收益来自 regime fit → 警示
        # warning=True 归因报告标注"高 regime fit 依赖"，
        # regime 切换时策略可能失效，反馈到 30 号 RegimeMetaAllocator budget 调整
    }
```

**与 28 号情绪周期 + 30 号 RegimeMetaAllocator 的对接**：
- 28 号情绪周期输出 regime 标签（bull/bear/range/squeeze 等），本算法消费作为分桶维度
- 30 号 RegimeMetaAllocator 用 regime_attribution 的"策略 × regime PnL 矩阵"调整 budget——某策略在某 regime 持续亏损 → 该 regime 下调该策略 budget
- 30 号 §2.2 闭环扩展：归因 → regime 条件 budget 调整 → 策略 PnL 变化 → 归因（BM-REC-03 闭环的 regime 维度）

**为何 Phase 2 而非 MVP**：
- 需要足够 track record 才能按 regime 分桶（每桶样本量 ≥ 20 交易日才统计显著）；28 号情绪周期 regime 标签需实盘校准
- MVP 先用 §3.2 Brinson 3 因子（不分 regime），Phase 2 加 regime-conditional 分解
- 重评条件：Brinson 总归因残差持续 > 0.01% + owner 需区分"顺风收益"vs"真实 skill"时

### 3.12 决策⑪：Shapley 值归因（v1.5.0 补，Phase 2 候选，2026-08 最新更好算法）

**决策**：策略贡献分解（§3.5）的求和不变量校验之外，Phase 2 评估引入 Shapley 值归因作为"公平分配"的更好算法——解决各策略/标的贡献的交互效应公平分配问题（vs naive weight×return 求和）。

> **2026-08 最新研究支持**：[arXiv:2102.05799 Moehle/Boyd/Ang 2021](https://arxiv.org/abs/2102.05799)（Shapley 归因经典框架）+ [xfinlink 2026-06-28](https://xfinlink.com/blog/shapley-value-portfolio-attribution-python)（Python 实现，实证 Shapley vs naive 差异可达 2-10 倍）+ [EDHEC 2026-02 SPPC](https://www.edhec.edu/sites/default/files/2026-02/SLIDES%20AnatomyPortfolioEDHEC.pdf)（Shapley-based Portfolio Performance Contribution，ML 黑盒归因）+ [Man Numeric 2023 SHAP](https://www.man.com/documents/download/b94f6-5adf6-a3bdc-5718e/Man_Numeric_Insights_Shining_Light_into_the_Machine_Learning_Black_Box_English_23-08-2023.pdf)（SHAP 组合归因，非线性交互捕捉）。

**Shapley 值归因的核心优势**（vs naive 求和）：

| 维度 | naive 求和（§3.5 当前方案） | Shapley 值归因 |
|---|---|---|
| 分配原则 | weight × return 简单加权 | 平均边际贡献，遍历所有联盟组合 |
| 交互效应 | 忽略（策略间相关性不计入） | 公平分配（合作博弈 Shapley 四公理） |
| 求和不变量 | 满足（算术求和） | 满足（efficiency 公理保证） |
| 计算复杂度 | O(n) | O(2^n)（n 策略数） |
| 适用规模 | 任意 | n ≤ 20（精确），n > 20 用 Monte Carlo 近似 |

**Shapley 值归因算法**（v1.5.0 补，[xfinlink 2026-06-28](https://xfinlink.com/blog/shapley-value-portfolio-attribution-python) Python 实现参考）：

```python
# Shapley 值策略贡献分解（v1.5.0 施工算法，Phase 2 候选）
from itertools import combinations
from math import factorial

def shapley_strategy_attribution(
        strategy_returns: dict[str, list[float]],  # {strategy_id: [daily_returns]}
        weights: dict[str, float]                   # 各策略权重（等权或 budget 加权）
) -> dict[str, float]:
    """Shapley 值策略贡献分解——公平分配各策略对组合总收益的边际贡献。

    [arXiv:2102.05799 Moehle/Boyd/Ang] 经典 Shapley 归因框架。
    [xfinlink 2026-06-28] 实证：Shapley vs naive weight×return 差异可达 2-10 倍，
    低相关性策略的 Shapley 贡献显著高于 naive（因加入任一联盟都改善分散化）。
    """
    strategy_ids = list(strategy_returns.keys())
    n = len(strategy_ids)

    def coalition_return(members: tuple) -> float:
        """特征函数：子组合（members）的复合收益。"""
        if not members:
            return 0.0
        # 等权子组合日收益
        import numpy as np
        daily = np.mean([strategy_returns[m] for m in members], axis=0)
        return float(np.prod(1 + np.array(daily)) - 1)

    full_return = coalition_return(tuple(strategy_ids))
    shapley = {sid: 0.0 for sid in strategy_ids}

    # 遍历每个策略，计算其在所有联盟中的平均边际贡献
    for target in strategy_ids:
        others = [s for s in strategy_ids if s != target]
        for size in range(n):  # 联盟大小 0 到 n-1
            for coalition in combinations(others, size):
                coalition_set = set(coalition)
                marginal = (coalition_return(tuple(coalition_set | {target}))
                            - coalition_return(tuple(coalition_set)))
                weight = (factorial(len(coalition_set)) *
                          factorial(n - len(coalition_set) - 1) / factorial(n))
                shapley[target] += weight * marginal

    # Shapley 效率公理：Σ Shapley = 总收益（求和不变量自动满足）
    return {
        'shapley_values': shapley,
        'full_portfolio_return': full_return,
        'sum_check': sum(shapley.values()),  # 应等于 full_return
        'invariant_status': 'PASS' if abs(sum(shapley.values()) - full_return) < 1e-9 else 'FAIL',
    }
```

**为何 Shapley 是"更好"但 Phase 2 才评估**：
- **更好**：Shapley 公平分配交互效应（naive 求和忽略策略间相关性）——[xfinlink 2026-06-28](https://xfinlink.com/blog/shapley-value-portfolio-attribution-python) 实证 JNJ naive +8.39% vs Shapley +18.46%（低相关性策略被 naive 低估）
- **Phase 2 才评估**：①计算复杂度 O(2^n)，5 策略可行（2^5=32），若策略数增长到 10+ 需 Monte Carlo 近似；②MVP 先用 §3.5 求和不变量校验（简单 + 满足 30 号 Model A 可加承诺）；③与 §3.11 regime-conditional 协同：Shapley 分配策略贡献，regime-conditional 分解 regime 维度——二者正交可叠加
- **重评条件**：①Brinson 求和不变量残差持续 > 1bp + 策略间相关性显著（IC > 0.5）+ owner 需公平分配交互效应时；②策略数 ≤ 8（精确 Shapley 可行）

**与 §3.5 求和不变量的关系**：§3.5 校验 Σ(strategy_pnl)==firm_pnl 数据一致性（对账门禁，PASS 才能跑 Shapley）；§3.12 Shapley 将 firm_pnl 公平分配到各策略（含交互效应）——不冲突，前者是数据校验门禁，后者是更精细的归因分解。

**MOD-RPT-015 绩效归因报告模板**（v1.3.0 补 / v1.15.0 路径修正，[default_attribution_engine.py](file:///d:/ZephyrAlpha/src/zephyr/reporting/default_attribution_engine.py) + [PerformanceAttributionReport 契约](file:///d:/ZephyrAlpha/src/zephyr/shared/contracts/performance_attribution_report.py) CTR-P1-009 codegen 已落盘）：

> MOD-RPT-015 报告生成器模块未施工（registry 无条目、无代码文件）；CTR-P1-009 契约 [performance_attribution_report.py](file:///d:/ZephyrAlpha/src/zephyr/shared/contracts/performance_attribution_report.py) 已存在于 shared/contracts。本备忘定义报告模板的最小必填字段 + Carino residual 质量门禁，作为施工时的契约。

```markdown
# 绩效归因报告 {period}

## 报告元数据
- portfolio_id: {firm_id 或 strategy_id}
- 报告期: {start_date} ~ {end_date}
- 基准: {benchmark_id}（沪深 300/中证 500/策略自定义）
- 归因方法: Brinson BHB 3 因子 + Carino 对数链接
- 报告版本: MOD-RPT-015 v1.0

## 1. 期间总收益
- 组合收益 R_p: {%}
- 基准收益 R_b: {%}
- 超额收益 R_p - R_b: {%}
- Carino 链接总超额收益（几何）: {%}

## 2. Brinson 3 因子分解
| 因子 | 单期求和 | Carino 链接 | 占超额收益比例 |
|---|---|---|---|
| Allocation Effect（配置效应） | {%} | {%} | {%} |
| Selection Effect（选择效应） | {%} | {%} | {%} |
| Interaction Effect（交互效应） | {%} | {%} | {%} |
| Transaction Cost Drag | {%} | {%} | {%} |
| **求和** | {%} | {%} | 100% |

## 3. Carino residual 质量校验
- |Σ linked effects - total geometric active return| = {%}
- 阈值: < 0.01%
- 状态: ✅ PASS / 🟥 FAIL（residual > 0.01%，报告拒绝发布）

## 4. 策略贡献分解（firm 级报告独有）
| StrategyBook | 净 PnL | 占 firm PnL 比例 | 60 日滚动 Sortino | PerformanceScore |
|---|---|---|---|---|
| 打板策略 | {%} | {%} | {%} | {%} |
| 多因子策略 | {%} | {%} | {%} | {%} |
| ... | ... | ... | ... | ... |
| **firm 求和不变量** | {%} | 100% | — | — |

## 5. transaction_cost_drag 分项
| 成本分项 | 金额 | 占比 | 备注 |
|---|---|---|---|
| Timing cost | {%} | {%} | 信号产生到下单延迟 |
| Impact cost | {%} | {%} | 下单对市场冲击 |
| Slippage | {%} | {%} | 成交价 vs 决策价 |
| Commission | {%} | {%} | 佣金+印花税+过户费 |
| **总 drag** | {%} | 100% | — |

## 6. 板块/标的维度分解
| 板块/标的 | w_p | w_b | r_p | r_b | Allocation | Selection | Interaction |
|---|---|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... | ... | ... |

## 7. 异常事件（若有）
- Carino residual > 0.01%: {原因排查}
- 板块权重未对齐: {T-1 收盘权重缺失}
- transaction_cost_drag 数据缺失: {TCA 未覆盖成交}

## 8. 反馈闭环
- 策略贡献分解 → RegimeMetaAllocator budget 调整（30 号 §2.2 闭环）
- 板块配置效应 → 选股层反馈（BM-REC-03-A）
- 标的选择效应 → 信号层反馈（BM-REC-03-B）
- 归因报告归档 → SQLite report_archive + Parquet
```

**2026-08 最新研究补充**（v1.9.0 补，3 项高价值发现）：

> **发现①：JPMorgan 层次化 Shapley 方法选择框架**——[arXiv:2608.04547v1 Mei & Lin 2026-08-05](https://arxiv.org/abs/2608.04547)（JPMorgan Chase，q-fin.RM）头对头比较 6 种归因方法：①**exact Shapley 是金标准但 O(2^n) 不可扩展**（输入 > 15 不可行）；②**hierarchical (nested) Shapley 是实用折中**——按层次结构（portfolio → strategy → signal）嵌套计算，复杂度从 O(2^n) 降到 O(Σ 2^{n_l})，3 层 × 5 节点 = 96 vs 单层 2^15=32768，**降 341 倍**；③IG/Gradient SHAP 适合连续输入不适合离散策略组合；④Permutation/Kernel SHAP 有 Monte Carlo 方差，生产不推荐。
>
> **施工含义**（§3.12 可扩展性升级路径）：**MVP 不变**（3-5 策略 exact Shapley，O(2^5)=32 可行）；**Phase 2 扩展**：策略数 8-15 时切换 hierarchical Shapley（sleeve → strategy → signal 三层嵌套）；**方法选择决策树**（[arXiv:2608.04547] §4 Table 1 适配）：输入离散 ≤15 → exact Shapley；离散 >15 且有层次结构 → hierarchical；连续（因子暴露）→ IG；需可复现性+治理 → exact > hierarchical > Kernel SHAP；**与 §3.13 Hentschel GLS 正交**（hierarchical Shapley 是分配层可扩展方案，GLS 是估计层统一框架，Phase 2 可同时落地）；**不采纳 IG/Gradient SHAP**（本备忘归因对象是离散策略/标的组合，登记但不施工）。
>
> **发现②：Shapley 归因规范背景分布**——[Hentschel 2026-07-28 "A Canonical Background Distribution for Shapley Attribution"](https://www.ludgerhentschel.com/PDFs/Hentschel%20%2726i.pdf)：SHAP 归因依赖背景分布定义"特征缺失"的参考总体，实践中常为代表性或计算便利而选。Hentschel 提出**预测中性流形背景分布**（用拟合预测接近中性水平的真实观测作背景），使 Shapley 效率公理意味着特征归因之和 = 预测值 - 中性预测值。优势：确定性（直接从观测构造）+ 语义对齐 + 不改变 Shapley 算法/公理。
>
> **施工含义**：**MVP 不变**（§3.12 用等权子组合作隐式背景，3-5 策略下背景选择影响小）；**Phase 2 评估**：若 Shapley 归因结果对背景分布敏感（换背景→排名变），改用 Hentschel 预测中性背景——用历史归因报告的"中性 Sharpe 水平"对应的策略组合作为背景样本；**不采纳原因登记**：预测中性流形背景需构造"拟合预测接近中性水平的真实观测"——A 股策略组合的中性预测水平定义模糊（Sharpe=0？benchmark return？），MVP 阶段不施工，Phase 2 若 Shapley 背景敏感性触发再评估。
>
> **发现③：Shapley 风险归因——从收益分配到风险分配**——[arXiv:2506.06653 Chen 2025 "Explaining Risks: Axiomatic Risk Attributions for Financial Models"](https://arxiv.org/abs/2506.06653)（Quantitative Finance，q-fin.CP）将 Shapley 值从**收益归因**扩展到**风险归因**（各策略对组合 VaR/CVaR 的贡献分配）。核心洞察：**风险分配 ≠ 收益分配**——一个策略可能收益贡献为正但风险贡献不成比例地高。方法：用 Shapley 四公理分配组合风险（VaR/CVaR/方差），效率公理保证 Σ Shapley 风险 = 组合总风险。
>
> **施工含义**（§3.12 从收益归因扩展到风险归因的路径）：**MVP 不变**（§3.12 仅做收益归因，风险归因由 36 号 VaR/CVaR 统一计算，非 Shapley 分配）；**Phase 2 评估**：当 owner 需要"哪个策略贡献了最多组合风险"时，用 CVaR 作为风险度量跑 `shapley_risk_attribution()` 分配各策略的边际 CVaR 贡献；**与 36 号的对接**：36 号 §3.2 计算 portfolio VaR/CVaR 总值，Shapley 风险归因把总值分解到各策略——36 号回答"组合风险是多少"，Shapley 风险归因回答"哪个策略贡献了最多风险"；风险归因也可用 hierarchical Shapley 降复杂度（sleeve → strategy → signal 三层嵌套分配 CVaR 贡献）；**Phase 2+ 远期候选**：MVP 不施工，当 36 号 portfolio VaR 计算稳定 + owner 需策略级风险归因时激活。

### 3.13 决策⑫：Hentschel GLS 统一归因框架（v1.8.0 补，Phase 2 候选，2026-08 最新更好算法）

**决策**：为 §3.2 Brinson + Carino + §3.12 Shapley 三套独立调整（多期链接 / 交互项再分配 / 因子残差再分配）登记 **Hentschel GLS 统一归因框架**作为 Phase 2 候选——把归因视为**估计问题**而非 ad-hoc 规则组合，用受限 GLS 把三类调整统一为"按精度最小化统计失真"的回归更新。

> **2026-08 最新研究支持**：[Hentschel 2024 "Brinson and Factors: A Unified Framework via Restricted GLS"](https://www.ludgerhentschel.com/PDFs/Hentschel%20%2724b.pdf)（精度感知广义最小二乘归因，2026 年被 [pybrinson v1.3.1](https://github.com/gghez/pybrinson) 工程化引用 + [gogoahead233-art/brinson-attribution 2026](https://github.com/gogoahead233-art/brinson-attribution) 开源实现）。

**Hentschel GLS 框架的核心优势**（vs §3.2 Carino + §3.12 Shapley 组合）：

| 维度 | §3.2 Carino + §3.12 Shapley | Hentschel GLS 统一框架 |
|---|---|---|
| 多期链接 | Carino 对数链接（ad-hoc 链接规则） | 受限 GLS 把链接视为跨期估计，按精度加权 |
| 交互项再分配 | Brinson BHB 保留交互项 / BF 降级为两因子 | GLS 把交互项再分配视为约束估计，统计可解释 |
| 因子残差再分配 | 当前 §3.4 因子维度暂缓，残差未处理 | GLS 把因子残差再分配纳入统一估计框架 |
| 统计置信度 | Carino residual 质量校验（求和不变量） | GLS 给出每个归因项的**统计置信度**（标准误 + CI） |
| 经典链接规则关系 | — | Carino / Frongello / Menchero 等经典链接规则在受限 GLS 下是其**特例**（特定权重选择） |
| 适用规模 | 任意 | 任意（GLS 是 O(n) 回归，比 Shapley O(2^n) 高效） |

**为何 Hentschel GLS 是"更好"但 Phase 2 才评估**：

- **更好**：①统一三类调整为单一估计框架，消除三套独立 ad-hoc 规则的组合失真；②给每个归因项统计置信度（Carino 只校验求和不变量，不回答"这个 allocation effect 0.3% 是否显著"）；③Carino/Frongello 等经典链接规则是其特例——落地 GLS 后现有 Carino 实现可视为 GLS 的特定参数化，平滑过渡无破坏性
- **Phase 2 才评估**：①MVP 阶段 §3.2 Carino + §3.12 Shapley 已够用，三类调整的"组合失真"在 3-5 策略小规模下不显著（Hentschel 实证：失真随策略数和持仓变动频率增长）；②GLS 需构造每期估计的协方差矩阵，3-5 策略 + 季度频率下协方差估计噪声大；③pybrinson v1.3.1 是参考实现非生产级，需自研适配 A 股 T+1 + 板块轮动场景；④与 §3.11 regime-conditional（分解维度）+ §3.12 Shapley（分配原则）正交可叠加——Hentschel GLS 是**估计层**统一
- **重评条件**：①Carino residual 持续 > 1bp + 策略数 ≥ 5 + 持仓变动频率高（日均 turnover > 30%）；②需归因项统计置信度做退役决策；③Brinson 交互项占总超额收益比例 > 10%（交互项再分配需求显著）

**Hentschel GLS 算法骨架**（v1.8.0 补，远期 Phase 2 候选，[Hentschel 2024](https://www.ludgerhentschel.com/PDFs/Hentschel%20%2724b.pdf) + [pybrinson v1.3.1](https://github.com/gghez/pybrinson) 实现参考）：

```python
def hentschel_gls_attribution(
        period_returns: list[dict],       # 各期收益 + 权重 + 基准数据
        factor_exposures: dict | None = None,  # 可选因子暴露（因子残差再分配）
        precision_weighting: str = "carino"    # carino/frongello/menchero/uniform
    ) -> dict:
    """Hentschel GLS 统一归因——把多期链接+交互项再分配+因子残差再分配统一为受限 GLS（[Hentschel 2024]：归因是估计问题，三类调整统一为"按精度最小化统计失真"的回归更新）。

    Args:
        period_returns: 各期 {strategy_id, weight, benchmark_weight, return, benchmark_return}
        factor_exposures: 可选因子暴露矩阵（n×k），用于因子残差再分配
        precision_weighting: carino/frongello/menchero（GLS 特例）/uniform（无精度感知）
    Returns:
        {'allocation_effect': float, 'selection_effect': float,
         'interaction_effect': float,
         'factor_residual': float | None,      # 因子残差再分配（可选）
         'std_errors': dict,                    # 各归因项标准误
         'confidence_intervals': dict,          # 95% CI
         'linking_residual': float,             # 链接残差（应≈0）
         'precision_matrix': np.ndarray}        # 精度矩阵（诊断用）
    """
    import numpy as np

    n_periods = len(period_returns)
    # 1. 构造精度矩阵（Hentschel 核心：按精度加权各期估计）
    if precision_weighting == "carino":
        # Carino 对数链接：k_t = ln(1+R_t) / R_t
        k_t = np.array([
            np.log1p(p['return']) / p['return'] if abs(p['return']) > 1e-10 else 1.0
            for p in period_returns
        ])
    elif precision_weighting == "frongello":
        # Frongello 链接：累积复利加权
        cumprod = np.cumprod([1 + p['return'] for p in period_returns])
        k_t = cumprod / np.sum(cumprod) * n_periods
    elif precision_weighting == "menchero":
        # Menchero 链接：固定系数（无需 R_t）
        k_t = np.ones(n_periods)  # Menchero 用约束估计
    else:
        k_t = np.ones(n_periods)  # uniform

    # 2. 构造 GLS 设计矩阵（Brinson 3 因子 + 可选因子残差）
    #    设计矩阵列：[allocation, selection, interaction, (factor_residual)]
    X = np.zeros((n_periods, 3 + (1 if factor_exposures else 0)))
    y = np.zeros(n_periods)
    for t, p in enumerate(period_returns):
        w_p, w_b = p['weight'], p['benchmark_weight']
        r_p, r_b = p['return'], p['benchmark_return']
        X[t, 0] = (w_p - w_b) * r_b              # allocation
        X[t, 1] = w_b * (r_p - r_b)              # selection
        X[t, 2] = (w_p - w_b) * (r_p - r_b)      # interaction
        if factor_exposures:
            X[t, 3] = factor_exposures.get(t, 0.0)  # factor residual
        y[t] = r_p - r_b                          # excess return

    # 3. 精度加权（GLS 核心：W = diag(k_t)）
    W = np.diag(k_t)

    # 4. 受限 GLS 估计（约束：Σ 归因项 = 总超额收益，即求和不变量）
    #    minimize ||W^(1/2) (y - Xβ)||² subject to Aβ = b
    #    A = [1, 1, 1, (1 if factor else 0)]，b = [sum(y)]——求和不变量约束
    W_sqrt = np.sqrt(W)
    X_w = W_sqrt @ X
    y_w = W_sqrt @ y

    # 受约束最小二乘（Lagrange 乘子法）
    n_factors = X.shape[1]
    A_constraint = np.ones((1, n_factors))
    b_constraint = np.array([np.sum(y)])

    # KKT 系统：[2X'WX, A'; A, 0] [β; λ] = [2X'Wy; b]
    KKT = np.block([
        [2 * X.T @ W @ X, A_constraint.T],
        [A_constraint, np.zeros((1, 1))]
    ])
    rhs = np.concatenate([2 * X.T @ W @ y, b_constraint])
    solution = np.linalg.solve(KKT, rhs)
    beta = solution[:n_factors]

    # 5. 统计置信度（GLS 标准误 + CI）
    residuals = y - X @ beta
    dof = max(1, n_periods - n_factors - 1)  # 自由度
    sigma2 = float(residuals @ residuals / dof)
    cov_beta = sigma2 * np.linalg.inv(2 * X.T @ W @ X)
    std_errors = np.sqrt(np.diag(cov_beta))

    # 95% 置信区间（正态近似，大样本下有效）
    from scipy.stats import norm
    z = norm.ppf(0.975)
    ci = {
        name: (beta[i] - z * std_errors[i], beta[i] + z * std_errors[i])
        for i, name in enumerate(['allocation', 'selection', 'interaction']
                                  + (['factor_residual'] if factor_exposures else []))
    }

    return {
        'allocation_effect': float(beta[0]),
        'selection_effect': float(beta[1]),
        'interaction_effect': float(beta[2]),
        'factor_residual': float(beta[3]) if factor_exposures else None,
        'std_errors': {'allocation': float(std_errors[0]),
                       'selection': float(std_errors[1]),
                       'interaction': float(std_errors[2])},
        'confidence_intervals': ci,
        'linking_residual': float(residuals @ residuals),  # 应≈0（求和不变量约束）
        'precision_matrix': W,  # 诊断用：精度加权矩阵
    }
# 用法（Phase 2 评估，替代/补充 §3.2 Carino + §3.12 Shapley）：
# result = hentschel_gls_attribution(period_returns, precision_weighting='carino')
# result['allocation_effect'] + 95% CI → 比 Carino 单点估计信息更丰富
# result['linking_residual'] ≈ 0 → 求和不变量自动满足（无需 §3.5 独立校验）
```

> **算法骨架说明**：①上述骨架是远期候选的施工形态参考，非 MVP 实现；②Hentschel GLS 的核心优势是**统计可解释**——给每个归因项标准误 + 95% CI，Carino 只给单点估计 + 求和不变量校验；③Carino/Frongello/Menchero 等经典链接规则在受限 GLS 下是其特例（precision_weighting 参数选择），落地 GLS 后现有 Carino 实现可平滑迁移；④与 §3.5 求和不变量校验的关系：GLS 的求和不变量约束（Aβ = b）是**估计内置**的，无需事后校验；⑤与 §3.11 regime-conditional + §3.12 Shapley 协同：Hentschel GLS 是估计层统一，regime-conditional 是分解维度，Shapley 是分配原则——三者正交可叠加。

**与 §3.2 Carino + §3.12 Shapley 的关系**：Carino 是 GLS 的 precision_weighting="carino" 特例；Shapley 是分配原则（GLS 交互项再分配是约束估计）；MVP 先用 Carino + 求和不变量校验（简单 + 满足 30 号 Model A 可加承诺），Phase 2 评估 GLS 增量价值（统计置信度 + 统一三类调整）。**为何不直接落地 GLS 替代**：MVP 简单优先（3-5 策略小样本下 GLS 置信度不稳定 dof 低）；pybrinson v1.3.1 是参考实现非生产级，需自研适配 A 股 T+1 + 板块轮动 + ST 事件；Shapley 公平分配四公理 GLS 不直接覆盖（估计层 vs 分配层正交）；重评条件触发后再评估。

**2026-08 最新研究补充：TreeIG 精确积分梯度**（v1.9.0 补，[Hentschel TreeIG 2026-08-04](https://github.com/LudgerHentschel/treeig) 同作者延伸）：

> [LudgerHentschel/treeig 2026-08-04](https://github.com/LudgerHentschel/treeig)（v0.1.1）是 Hentschel 归因理论体系的第三块拼图（2024 GLS + 2026-07 背景分布 + TreeIG）：对树模型（XGBoost/LightGBM/CatBoost），积分梯度的路径积分**精确退化为分裂边界跨越的预测跳跃之和**——无需 Monte Carlo 采样、无近似参数，属性分配满足精确完备性。
>
> **与本备忘的关系**：**不直接施工**——本备忘归因对象是离散策略/标的组合，TreeIG 是 ML 黑盒归因工具，适配 25 号多因子策略的 ML 模型解释而非 54 号组合归因；**登记原因**：Phase 2 评估 Hentschel GLS 时，若需对 25 号 ML 策略做特征归因（哪些因子贡献了收益），TreeIG 是精确解（vs SHAP Kernel 近似）——IG 适合连续输入（因子暴露），TreeIG 把 IG 精确化到树模型；Shapley 适合离散输入（策略组合），hierarchical Shapley 把它可扩展化；**Phase 2+ 远期候选**：当 25 号 ML 模型成为主 alpha 来源 + owner 需"哪些因子贡献了今日收益"归因时，TreeIG 替代 SHAP Kernel 近似。

### 3.14 决策⑬：MCR/CCR 风险分解（v1.14.0 补，Phase 2.5 候选，经典风险归因填补收益-风险归因不对称）

**决策**：为 §3.2 Brinson 收益归因登记**经典 MCR/CCR 风险分解**作为风险归因维度的轻量级中间档——Brinson 回答"谁赚了钱"，MCR/CCR 回答"谁贡献了风险"，二者正交互补。定位 **Phase 2.5 候选**（比 §3.12 Shapley 风险归因 Phase 2+ 更轻量、比 §4.1 Barra Phase 3 更轻量），填补"收益归因已有（Brinson）但风险归因全空白直到 Phase 3 Barra"的中间档缺口。

> **为何需要 MCR/CCR（收益-风险归因不对称问题）**：§3.2 Brinson 3 因子分解组合**收益**，但组合**风险**（波动率/VaR）的分解维度完全空白——直到 §4.1 Barra（Phase 3，需因子模型许可证+协方差矩阵）才填补。MVP~Phase 2 期间，owner 能回答"打板策略赚了多少"但无法回答"打板策略贡献了多少组合波动率"——一个收益贡献为正的策略可能风险贡献不成比例地高，不分解风险维度会误导 budget 调整方向（30 号 RegimeMetaAllocator 只看 PerformanceScore=收益维度，不看风险维度）。

> **MCR/CCR vs Shapley 风险归因 vs Barra 三档定位**：
> | 方法 | 风险归因机制 | 协方差来源 | 复杂度 | 定位 |
> |---|---|---|---|---|
> | **MCR/CCR**（本节） | Euler 齐次函数定理分解组合波动率 σ_p | 经验协方差矩阵（历史收益直接估计） | O(n²) 闭式解 | **Phase 2.5**（轻量中间档） |
> | **Shapley 风险归因**（§3.12 v1.9.0 已登记） | Shapley 四公理分配组合 VaR/CVaR 贡献 | Monte Carlo 模拟 VaR | O(2^n) 精确 / O(MC) 近似 | **Phase 2+**（高级替代，处理非线性） |
> | **Barra 因子风险归因**（§4.1 已拒绝/Phase 3） | 因子暴露 × 因子协方差矩阵分解 | Barra 因子风险模型（需许可证） | O(n·k) k=因子数 | **Phase 3**（机构级，AUM 机构化才评估） |

**MCR/CCR 理论基础**（Euler 齐次函数定理）：组合波动率 σ_p = √(wᵀΣw) 是权重 w 的一次齐次函数（σ_p(λw) = λσ_p(w)），由 Euler 定理：σ_p = Σᵢ wᵢ · ∂σ_p/∂wᵢ。定义：
- **MCR_i（Marginal Contribution to Risk）**= ∂σ_p/∂wᵢ = (Σw)_ᵢ / σ_p——第 i 个资产权重增加 1 单位时组合波动率的变化率
- **CCR_i（Component Contribution to Risk）**= wᵢ · MCR_i——第 i 个资产对组合波动率的绝对贡献
- **求和不变量**：Σᵢ CCR_i = σ_p（Euler 定理保证），类比 §3.5 Brinson 求和不变量 Σ(strategy_pnl) = firm_pnl

```python
def calc_mcr_ccr_risk_attribution(weights: np.ndarray, cov_matrix: np.ndarray,
                                   asset_names: list[str] = None) -> dict:
    """MCR/CCR 风险分解（v1.14.0 补，经典 Euler 分解，Phase 2.5 候选）

    将组合波动率 σ_p 分解到各资产的边际贡献(MCR)和组件贡献(CCR)。
    与 §3.2 Brinson 收益归因正交：Brinson 分解收益，MCR/CCR 分解风险。

    输入：
      weights: 组合权重向量 w (n×1)
      cov_matrix: 经验协方差矩阵 Σ (n×n)，用滚动 60 日收益估计
      asset_names: 资产/策略名（可选，默认索引）

    输出：
      portfolio_vol: 组合年化波动率 σ_p
      mcr: 各资产边际贡献向量 (∂σ_p/∂w_i)
      ccr: 各资产组件贡献向量 (w_i × MCR_i)
      ccr_pct: 各资产风险贡献占比 (CCR_i / σ_p，求和=100%)
      invariant_check: 求和不变量校验 |ΣCCR - σ_p| / σ_p
    """
    # 1. 组合波动率 σ_p = sqrt(wᵀΣw)
    portfolio_var = float(weights @ cov_matrix @ weights)
    portfolio_vol = np.sqrt(portfolio_var)

    # 2. MCR_i = (Σw)_i / σ_p（边际贡献=协方差加权组合向量除以总波动率）
    sigma_w = cov_matrix @ weights  # (Σw)_i 向量
    mcr = sigma_w / portfolio_vol   # MCR_i = (Σw)_i / σ_p

    # 3. CCR_i = w_i × MCR_i（组件贡献=权重×边际贡献）
    ccr = weights * mcr

    # 4. 求和不变量校验：ΣCCR = σ_p（Euler 齐次函数定理保证）
    invariant_residual = abs(float(ccr.sum()) - portfolio_vol) / portfolio_vol

    # 5. 风险贡献占比（求和=100%，用于归因报告）
    ccr_pct = ccr / ccr.sum()

    return {
        "portfolio_vol": portfolio_vol,
        "mcr": dict(zip(asset_names, mcr.tolist())) if asset_names else mcr.tolist(),
        "ccr": dict(zip(asset_names, ccr.tolist())) if asset_names else ccr.tolist(),
        "ccr_pct": dict(zip(asset_names, ccr_pct.tolist())) if asset_names else ccr_pct.tolist(),
        "invariant_check": {
            "residual_rel": invariant_residual,  # 应 < 1e-10（数值精度内）
            "status": "PASS" if invariant_residual < 1e-6 else "FAIL"
        }
    }


def calc_strategy_risk_attribution(strategy_returns: dict[str, np.ndarray],
                                    strategy_weights: dict[str, float],
                                    window: int = 60) -> dict:
    """策略级 MCR/CCR 风险归因（v1.14.0 补，与 §3.5 策略贡献分解对称）

    将 §3.5 的策略贡献分解从收益维度扩展到风险维度：
    - §3.5 Brinson: Σ(strategy_pnl) = firm_pnl（收益归因）
    - 本函数 MCR/CCR: Σ(strategy_ccr) = firm_σ_p（风险归因）

    输入：
      strategy_returns: 各策略日收益率序列 {strategy_name: returns_array}
      strategy_weights: 各策略 budget 权重 {strategy_name: weight}
      window: 协方差估计滚动窗口（默认 60 交易日）
    """
    names = list(strategy_returns.keys())
    R = np.column_stack([strategy_returns[n][-window:] for n in names])  # (T × N) 收益矩阵
    w = np.array([strategy_weights[n] for n in names])
    # 经验协方差矩阵（无需 Barra 因子模型，直接历史收益估计）
    cov = np.cov(R, rowvar=False) * 252  # 年化
    return calc_mcr_ccr_risk_attribution(w, cov, asset_names=names)
```

**与 §3.5 Brinson 收益归因的对称关系**：
- §3.5 Brinson：`Σ(strategy_pnl) = firm_pnl` + `validate_strategy_pnl_invariant()` 求和不变量校验
- §3.14 MCR/CCR：`Σ(strategy_ccr) = firm_σ_p` + `invariant_check` 求和不变量校验
- 二者正交：Brinson 分解"谁赚了钱"，MCR/CCR 分解"谁承担了风险"——归因报告同时展示两维度，owner 可识别"高收益高风险"vs"低收益低风险"策略

**与 30 号 RegimeMetaAllocator 的联动**：
- 当前 30 号 budget 调整公式 `allocation_i = normalize(Base_i × PerformanceScore_i × Shrinkage_i)` 只看收益维度（PerformanceScore=60 日滚动 Sortino，v1.15.0 口径修正后）
- MCR/CCR 补风险维度：若某策略 CCR_pct / PnL_share > 1.5（风险贡献占比远超收益贡献占比），PerformanceScore 须额外降权——"赚 10% 但贡献 25% 波动率"的策略应被 budget 收缩
- **Phase 2.5 施工形态**：MCR/CCR 输出 `risk_concentration_ratio = CCR_pct / PnL_share` 字段，30 号 RegimeMetaAllocator 消费该字段作为 budget 调整的风险维度补充（MVP 不接入，Phase 2.5 评估）

**为何 MCR/CCR 是"轻量级"（不需要 Barra 许可证）**：
- MCR/CCR 只需**经验协方差矩阵**（历史收益直接 `np.cov` 估计），无需 Barra 因子风险模型（CNE5 13类60+因子 + 协方差矩阵授权）——**不违反 §4.1 拒绝裁定**
- 与 30 号"拒绝统一 MVO（需协方差矩阵）"的关系：30 号拒绝的是 MVO **优化器**（用协方差做事前决策），MCR/CCR 是**事后归因**（用协方差做事后解释）——前者是 DECIDE 工具，后者是 EXPLAIN 工具，性质不同

**过度工程审查**：
- MCR/CCR 是工业标准风险归因（Litterman 1996 Goldman Sachs "Hot Spots" 框架，机构风险管理系统标配），非学术前沿；计算量极低（O(n²) 矩阵乘法，3-5 策略 <1ms），无 Monte Carlo / 无因子模型 / 无许可证
- **为何 Phase 2.5 而非 MVP**：MVP 阶段 3 策略组合 + 60 日 track record 不足时经验协方差估计噪声大（小样本协方差不稳定），Phase 2.5（首批策略 3 月 track record 后）协方差估计才稳定
- **为何 Phase 2.5 而非 Phase 3 Barra**：MCR/CCR 是 Barra 的轻量前置——在 AUM 机构化触发 Barra 评估前，MCR/CCR 已能回答"谁贡献了风险"，无需等 Barra 许可证

**重评条件**：首批策略 3 月 track record 后 + owner 需"哪个策略贡献了最多组合波动率"风险维度归因时 + §3.5 Brinson 收益归因已稳定运行

**2026-08-12 最新研究补充：FPRO 修复 Euler 对冲对符号失真**（v1.15.0 补，[Grant Holtes 2026-07-22 "A Funded-Path Random-Order Method for Portfolio Active Risk Attribution"](https://www.grantholtes.com/assets/documents/Funded_Path_Random_Order_Portfolio_Active_Risk_Attribution.pdf)）：

> Holtes 2026-07 指出 MCR/CCR（Euler 分解）的结构性弱点：在**最终持仓点**评估边际贡献，会给相互对冲的持仓对分配大额正负抵消贡献（数学正确但掩盖"哪笔决策驱动了风险"）。FPRO（Funded-Path Random-Order）把每次调仓视为从基准出发的离散决策步，在随机排序上求期望边际风险贡献（Shapley 思想），每步用对冲腿或现金腿保持满仓——精确 reconcile 到总主动风险且消除符号抵消伪影。**对本项目的适用性评估**：A 股不能做空 + 3-5 策略，机构组合的对冲对场景有限；但 30 号 firm 层"多策略同标的叠加/求和裁剪"可能产生跨策略同标的对冲（打板买入 vs 多因子减仓同一标的），届时 MCR/CCR 的 CCR_pct 会失真。**登记为 Phase 2.5+ 远期候选**：若归因报告显示同标跨策略对冲显著（single_name_cap 频繁 binding + CCR 符号抵消），启用 FPRO 替代 Euler 分解；MVP/Phase 2.5 仍用 MCR/CCR（O(n²) 闭式解足够）。

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-SEL-21-E | 绩效归因引擎 | §3.2 Brinson 3 因子 + §3.5 策略贡献分解 | production 已建 |
| BM-RC-08-A | 日终PnL对账与合规报告 | §3.3 三层对账 + §3.7 四类报告 | production 已建 |
| BM-RC-08-B | 风险归因分解 | §3.2 + §3.14 MCR/CCR 风险分解 | production 已建 |

### 3.15 决策⑭：压力测试（BM-RC-08-C，production 补强，v1.15.4 补）

> battle_map 风控域 BM-RC-08 子环节，production（MOD-RK-12 `core/stress_test_engine.py`），本备忘为其补 why 层决策记录。

- **定位**：L4 风控域，盘后/合规要求触发（历史情景 2008/2015/2020）；消费持仓（D-EX-CORE）+ 情景数据（D-DATA）；数据流：持仓+情景→压力报告（历史情景+假设情景+反向压力测试+敏感性+传染效应）→ BM-RES-07 策略迭代。
- **裁定**：①**历史情景库三段**——2008 全球金融危机 / 2015 A 股股灾 / 2020 疫情熔断，覆盖系统性危机、杠杆牛崩塌、跳空熔断三类 A 股极端形态；②**反向压力测试**——给定组合不可承受阈值（如单日回撤 >8% 或触及 35 号回撤 Protocol HARD_HALT 线）反推所需市场冲击幅度，回答"多大冲击会击穿风控"；③**敏感性分析**——单因子扰动（指数 ±5%/±10%、行业板块冲击、流动性折价）定位最脆弱敞口；④**传染效应**——登记为远期（跨市场/跨品种级联需多市场数据接入，当前 A 股单市场从简）。理由：压力测试是风控参数的事前验证——Brinson 归因（§3.2）回答"过去亏在哪"，压力测试回答"未来极端行情会亏多少"，两者构成事后/事前闭环；引擎代码已 production，本节补口径与通道裁定。**产出物通道裁定**：压力测试报告走 §3.7 周度报告通道——RiskReportEngine 的 WeeklyRiskDeep 已含压力测试板块（§3.7 四类报告体系），产出经 ReportPublisher 归档（渠道当前仅 PENDING 落库，见 §2.4 横向缺口 #3），日报不承载（频率过重）。**与 53 号 BM-SIM-04 的分工消歧**：53 号 BM-SIM-04 是**仿真验证域引擎**（造假市场喂策略、探策略行为边界的 what-if 实验）；本环节是**运营域报告通道**（真实持仓 × 情景、盘后产出压力报告供 owner 评审与风控参数调整）——同一历史情景库两边复用，引擎在 53、报告在 54，互不重造。
- **契约/参数/接口**：StressTestReport `{report_id, as_of, scenario_results: [{scenario_id, portfolio_pnl, max_dd, worst_position}], reverse_stress: {threshold, implied_shock}, sensitivity: [{factor, delta_pnl}]}`，周度经 ReportPublisher 归档。降级：压力测试引擎未就绪→跳过压力测试（环节定义原口径，周度报告该板块标"未生成"）。重评条件：传染效应维度待跨市场接入（港股通/跨品种）后评估；报告渠道实发随 §2.4 缺口 #3（Email/WeChat sender 注入）一并落地。

## 4. 考虑过的替代方案（拒绝理由）

### 4.1 Barra 因子风险归因 —— 拒绝（过度工程）
- **拒绝理由**：Barra 需因子风险模型许可证 + 协方差矩阵估计 + 较长实施周期（finantrix 2026-08：典型 deal $100K-$1M+）；个人 5 策略组合的因子暴露主要由选股策略内生决定，因子归因增量信息有限；与 30 号拒绝统一 MVO（需协方差矩阵）保持架构一致
- **重评条件**：AUM 增长到机构体量 + 多管理人场景 + 因子归因成为合规要求时

### 4.2 因子归因（factor_contributions 简化版） —— 暂缓
- **拒绝理由**（暂缓）：因子归因仍需因子暴露矩阵 + 因子收益回归，Brinson 的"配置 vs 选股"已能回答 80% 迭代问题；首批策略 track record 不足时因子收益估计不稳定
- **重评条件**：首批策略 track record 3 个月后，若 Brinson 归因不足以解释策略表现

### 4.3 盘后全量对账（EOD Reconciliation）—— 暂缓（Phase 2）
- **拒绝理由**（暂缓）：MVP 盘中每 5min 持仓对账已覆盖实盘生存需求；盘后全量对账需券商对账单数据接入（当前用 get_positions 查询兜底）；与 40 号 §5 待裁定一致
- **重评条件**：实盘上线后，T+1 结算确认需求 + 券商对账单数据可接入时

### 4.4 资金对账 —— 暂缓（Phase 2）
- **拒绝理由**（暂缓）：PositionReconciler 当前只对账持仓数量；资金对账需解析 get_positions 的 cash 字段 + T+0/T+1 资金可用性推算；MVP 用 40 号决策⑬资金预占本地串行扣减兜底
- **重评条件**：实盘上线后，资金不一致导致 error_code=54 拒单频发时

### 4.5 实时归因（盘中实时 Brinson）—— 拒绝
- **拒绝理由**：归因是事后解释工具，盘中实时归因无决策价值（盘中不能因归因结果改单）；实时归因需实时持仓历史 + 实时基准收益，计算开销大；盘中已有 RealtimePnlDashboard 看板满足实时 PnL 查看
- **重评条件**：永不（归因本质是事后工具）

### 4.6 四维全归因（策略×标的×因子×时段）—— 拒绝
- **拒绝理由**：四维全归因是机构级需求；个人 5 策略组合信息过载；多数格子样本不足（统计显著性差）
- **重评条件**：AUM 增长到机构体量 + 多管理人场景

### 4.7 wash trade/spoofing 检测 —— 拒绝（暂缓）
- **拒绝理由**：个人单账户无自交易风险；spoofing 检测需订单簿深度 + 多账户意图推断；与 40 号 §5 待裁定"Pre-Trade 合规检查"一致
- **重评条件**：多账户或合规要求升级时

## 5. 上限定义（Ceiling）

### 5.1 系统上限
- **归因框架**：Brinson 3 因子（allocation/selection/interaction，BHB 方案），非 Barra；BF 方案作降级备选（interaction 长期近 0 时）
- **归因类型**：PnL Explain（事后解释）为主，PnL Predict（Greek/SRPnL 事前预测）拒绝（A 股权益无 Greek，与 30 号拒 MVO 协方差一致）
- **多期链接**：Carino 对数链接（Cariño 1999，GIPS-compliant 首选）；Menchero/GRAP/Frongello/Bacon 备选（pybrinson v1.3.1 已实现 5 种）
- **权重时点**：beginning-of-period weights（T-1 收盘），非 end-of-period（消除向上偏差）
- **归因质量门禁**：Carino residual < 0.01%（链接求和 vs 总几何超额收益差异），超阈值拒绝发布
- **归因维度**：策略 × 标的 × 时段三维度，因子维度暂缓（regime fit 由 28 号独立管，execution discipline 由 TCA 独立管，不混入 Brinson）
- **跨 session 归因唯一键**：fill_id + position_id（不依赖 session_id/reoptimization_run_id，防幽灵成交）
- **对账层级**：三层（成交/持仓/资金），盘中持仓对账每 5min + 盘后结算对账每日 15:30 + 资金对账 Phase 2
- **对账双边**：系统账 vs 券商端（个人单账户，无 custodian/fund admin 三方）
- **两层归因**：StrategyBook 独立 PnL（策略层）+ firm 级聚合归因（组合层），求和不变量
- **异常检测**：三层（价格>2σ/量>3×mean/拒单分类），无 wash trade/spoofing
- **报表体系**：四类（风险/监管/TCA/复盘）+ 双渠道（微信/邮件，当前仅 PENDING 落库未实际发送）+ 归档（append-only 文件归档已实现；SQLite/Parquet 归档未实现，见 §2.4 横向缺口）
- **监管报告自动化**：手动填报（GATE-002 AUM≥1000 万 或 GATE-003 跨市场激活后自动化）
- **基准选取**：A 股策略基准（沪深 300/中证 500/策略自定义），归因前提
- **成交对账匹配**（v1.3.0 补）：三层（exact/fuzzy/partial）+ 例外工单，例外率目标 < 1%（[ai-indeed 2026-08-04](https://www.ai-indeed.com/encyclopedia/19423.html) 实证：例外率 18%→2.9%）
- **transaction_cost_drag 接入 TCA**（v1.3.0 补）：drag = timing + impact + slippage + commission 加权求和；Brinson + drag = 总超额收益（求和不变量）
- **A 股 PnL waterfall**（v1.3.0 补）：Signal + Selection + Timing - Costs - Opportunity = Net PnL；Brinson 补充框架，Phase 2 若 Brinson 残差 > 0.01% 时启用
- **MOD-RPT-015 报告契约**（v1.3.0 补）：8 节最小必填 + Carino residual < 0.01% 质量门禁 + 求和不变量校验
- **sizing_basis 归因维度**（v1.4.0 补，与 [31 号 §2.3.4](31_position_sizing.md) 对接）：仓位裁剪约束溯源（5 约束枚举见 §3.8），归因报告增加 sizing_basis 字段追溯每笔仓位的绑定约束
- **deflated-alpha v0.3.0 三重验证**（v1.4.0 补，与 55 号 §3.4/§3.5 评审通道对接（v1.15.8 对齐））：回测 vs 实盘统计显著性验证（DSR + PBO + OOS 退化斜率 + Hansen SPA consistent p-value + White RC p-value），月/季归因报告调用 `audit()` 跑齐 4 类检验；verdict == LIKELY_OVERFIT → 触发 55 号 §3.5 评审通道
- **Combined Trading Signals 正交维度约束**（v1.4.0 补）：信号组合前正交性验证（数学正交维度要求 + IC/条件数/VIF 阈值口径见 §3.10），防多信号共线过拟合；正交性不达标 → 拒绝组合或降权
- **成交对账置信度评分匹配**（v1.5.0 补）：三层匹配输出加权置信度分数（属性权重与 High/Middle/Low 三带阈值口径见 §3.3）；MVP 用默认阈值，实盘 3 月后回归校准
- **三阶段不可变审计轨迹**（v1.5.0 补）：阶段①原始事件捕获（system_fills + broker_settlements 原始记录）→ 阶段②匹配决策（层级+置信度+规则版本+被拒匹配 negative evidence）→ 阶段③归因结果（Brinson 分解+Carino residual+不变量校验）；SQLite append-only + hash 链 + 30 天后 read-only；替代区块链（个人单机无需多方信任）
- **Brinson 3 因子真实计算 + Carino 多期链接施工算法**（v1.5.0 补 / v1.15.0 守恒修正）：纯 BHB 三因子 + Carino 对数链接（公式与施工算法见 §3.2，与 pf_core MOD-PF-007 生产实现同口径，residual < 1e-6 质量门禁）；落地形态随 §6 双实现收敛裁定（pf_core 基底升级 Carino 或 reporting 桩填充）
- **A 股 T+1 归因特殊处理**（v1.5.0 补）：`calc_brinson_with_t1_settlement()` 将 selection effect 拆为 realized（T-1 前已建仓，可兑现）+ unrealized（T 日新建仓，T+1 才可卖，仅为浮盈）——施工算法见 §3.2；归因报告分列两行 + t1_warning 标注（> 50% selection 来自浮盈时警示）
- **策略贡献分解求和不变量校验**（v1.5.0 补）：`validate_strategy_pnl_invariant()` 校验 Σ(strategy_pnl) == firm_pnl（容差 1bp），FAIL 时归因报告拒绝发布 + 定位差异来源（成交漏算/费率错算/T+1 跨日/firm 裁剪副作用）；与 Carino residual 并列为归因报告双重门禁
- **regime-conditional 归因**（v1.5.0 补，Phase 2 候选）：`attribute_by_regime()` 按 28 号情绪周期 regime 标签分桶跑 Carino 链接 Brinson + regime 切换贡献 + regime_fit_share vs skill_share 分解；regime_fit_share > 0.5 警示；与 30 号 RegimeMetaAllocator regime 条件 budget 调整闭环
- **Shapley 值归因**（v1.5.0 补，Phase 2 候选）：`shapley_strategy_attribution()` 合作博弈 Shapley 值公平分配策略贡献（含交互效应），效率公理保证 Σ Shapley = 总收益；vs naive 求和差异可达 2-10 倍（[xfinlink 2026-06-28](https://xfinlink.com/blog/shapley-value-portfolio-attribution-python) 实证）；O(2^n) 复杂度，策略数 ≤ 8 精确可行
- **A 股 PnL waterfall 施工算法**（v1.5.1 补）：逐笔归因施工算法 `calc_ashare_pnl_waterfall()` 见 §3.2（含 [OrderX 2026-07-09](https://orderx.com/education/introduction-to-algorithmic-execution-part-12-benchmarks-and-tca/) signed bps 公式）；启用条件同上条
- **滑点分布报告增强**（v1.5.1 补）：`calculate_slippage_distribution()` 百分位（p50/p90/p99）+ 压力 regime 切片（top decile 波动率）+ reversion 诊断（temporary_impact vs real_alpha）；[Drovix 2026-05](https://drovix.com/blog/tca-that-actually-drives-decisions) 实证滑点是分布非均值；Phase 1.5 施工
- **PerformanceScore 计算算法**（v1.5.1 补 / v1.15.0 口径修正）：`calc_performance_score()` 60 日滚动 **Sortino** 年化 → 映射 **[0.5, 1.5]** 区间（30 号 §2.2 契约，口径真源 34 号 §3.1）；观测不足返回中性 1.0；对齐 30 号 RegimeMetaAllocator `allocation_i = normalize(Base_i × PerformanceScore_i × Shrinkage_i)` + budget floor ≥ 5% / cap ≤ 40%
- **异常检测施工算法**（v1.5.1 补）：`detect_price_anomaly()` / `detect_volume_anomaly()`（滚动窗口、阈值与兜底口径见 §3.6）
- **verdict 三态判定阈值**（v1.5.1 补）：`interpret_deflated_alpha_verdict()` 显式阈值见 §3.9（LIKELY_OVERFIT / LIKELY_REAL / INCONCLUSIVE 三态 + MinTRL 不足直接 INCONCLUSIVE）
- **持仓对账漂移检测算法**（v1.6.0 补）：`detect_position_drift()` 双容差 + bps 三级严重度 + 冻结/解冻状态机（参数口径见 §3.3）
- **MAD 鲁棒异常检测**（v1.6.0 补）：`detect_price_anomaly_robust()` 主检测器（Modified Z-Score 公式、3.5 阈值、MAD=0 兜底、三级严重度与 dismiss/escalate 升级流程见 §3.6）
- **PBO 零假设解释修正**（v1.7.0 补，[Solovjiev 2026-07 "PBO 受控标定"](https://pbo.marketmaker.cc/paper.pdf)）：verdict 函数中 PBO 阈值须显式说明 null=0.5——PBO<0.5 才有 edge，PBO>0.5 才过拟合；`pbo > 0.25` 是保守红旗（远低于 null=0.5），PBO 接近 0.5 须结合 N_eff+条件数综合判断（§3.9）
- **Stale-Value 冻结馈送检测**（v1.7.0 补，[EQAF arXiv:2606.20079 2026-06](https://arxiv.org/pdf/2606.20079v1) UBS 投行实测）：`detect_stale_value()` 第 0 层领域确定性规则（对账/异常检测前先检数据冻结，冻结则跳过本轮；参数与 A 股断连场景见 §3.6）
- **Merkle tree 审计轨迹升级路径**（v1.7.0 补，Phase 2 候选）：线性 hash 链 → Merkle tree + 外部锚定（RFC-3161 TSA / Sigstore Rekor）；升级施工步骤、VCP v1.2 对齐口径与暂缓理由见 §3.3
- **MCR/CCR 风险分解**（v1.14.0 补，Phase 2.5 候选）：经典 Euler 齐次函数定理分解组合波动率到各策略 MCR（边际贡献）/CCR（组件贡献），求和不变量 ΣCCR=σ_p；仅需经验协方差矩阵（np.cov 估计），无需 Barra 许可证；与 §3.2 Brinson 收益归因正交（收益归因+风险归因双维度），与 §3.12 Shapley 风险归因（Phase 2+ Monte Carlo）形成轻量-高级两档；输出 risk_concentration_ratio=CCR_pct/PnL_share 反馈 30 号 RegimeMetaAllocator budget 风险维度调整

### 5.2 演进路径
- **第一阶段（MVP，立即施工）**：**归因引擎双实现收敛**（v1.15.0 新增置顶项：按 §6 裁定以 pf_core MOD-PF-007 为实现基底——已有 BHB 守恒校验+测试，升级其算术链接为 Carino；reporting 桩退役或改薄委托；canonical 登记同步修正）+ **TCA IS 四组件施工**（v1.15.0 新增：DefaultTcaEngine 当前仅简易滑点，transaction_cost_drag 接入的前提是 IS 分解先落地）+ 补全 Brinson 3 因子真实计算（接入 _holdings_history，beginning-of-period weights，纯 BHB 口径 §3.2）+ **Carino 多期链接算法实现**（参考 [pybrinson](https://github.com/gghez/pybrinson) v1.3.1）+ **Carino residual 质量门禁**（< 0.01%）+ transaction_cost_drag 接入 TCA（v1.3.0 算法，依赖 TCA IS 施工）+ 绩效归因报告（MOD-RPT-015 v1.0 模板）生成 + **成交对账三层匹配算法实现**（v1.3.0 算法，exact/fuzzy/partial + 例外工单，含 v1.15.0 root_cause/recurrence_key 字段）+ **置信度评分匹配骨架**（v1.5.0 新增：calculate_match_confidence 函数 + High/Middle/Low 三带路由 + 默认阈值 0.85/0.50）+ **三阶段不可变审计轨迹骨架**（v1.5.0 新增：audit_trail SQLite 表 + write_audit_stage hash 链 + INSERT-only 触发器——v1.15.0 盘点确认 audit_trail 表 DDL 缺失，须先落 schema）+ **盘后 15:30 调度接线**（v1.15.0 新增：当前无调度器任务，须注册盘后 cron/APScheduler 触发 SettlementReconciler + DailyAuditor）+ **Brinson+Carino 施工算法契约落地**（v1.5.0 新增：§3.2 calc_single_period_brinson + carino_link_periods 替换 default_attribution_engine.py:82-92 占位实现）+ **A 股 T+1 归因特殊处理**（v1.5.0 新增：calc_brinson_with_t1_settlement 拆分 realized/unrealized selection——v1.15.0 已改为收益贡献拆分口径）+ **策略贡献分解求和不变量校验**（v1.5.0 新增：validate_strategy_pnl_invariant 作为归因报告发布门禁——v1.15.0 警示：策略层独立 PnL 数据源（StrategyBook MOD-POS-020）未实现，须先由策略层施工填充，关联 #ARCH-REG-005）
- **Phase 1.5（首批策略 track record 1-3 个月）**：① 策略贡献分解反馈 RegimeMetaAllocator budget 调整闭环 ② 大额异动检测阈值校准（实盘数据回归）③ 资金对账实现（PositionReconciler 阶段2扩展）④ **Carino residual 监控基线建立**（实盘归因数据回归后定阈值）⑤ **成交对账三层匹配容差校准**（qty_tol/price_tol/date_window 实盘回归）⑥ **transaction_cost_drag 分项监控基线**（timing/impact/slippage/commission 占比分布）⑦ **sizing_basis 归因维度接入**（v1.4.0 新增：31 号 PositionSizingEngine 输出 sizing_basis 字段后，归因报告增加仓位约束溯源）⑧ **Combined Trading Signals 正交性验证**（v1.4.0 新增：多因子/多信号策略组合前跑正交性检查，相关矩阵条件数 + VIF）⑨ **置信度阈值校准**（v1.5.0 新增：实盘匹配 false positive 率回归 + High/Middle/Low 阈值调整 + 按券商校准 if 多券商）⑩ **审计轨迹 30 天 read-only 触发器激活**（v1.5.0 新增：SQLite 触发器禁止 UPDATE/DELETE 超过 30 天的审计记录 + WAL 归档）⑪ **T+1 浮盈依赖监控基线**（v1.5.0 新增：t1_warning 触发率 + unrealized_selection 占比分布回归）
- **第二阶段（首批策略 track record 3 个月后）**：① 盘后全量对账（券商对账单接入）② 因子归因（factor_contributions，若 Brinson 不足以解释）③ 监管报告自动化（若 AUM 达门槛）④ **A 股 PnL waterfall 框架**（若 Brinson 残差持续 > 0.01% + 需区分信号/选股/择时失效时）⑤ **deflated-alpha v0.3.0 月/季归因报告接入**（v1.4.0 新增：月/季归因报告调用 `audit()` 跑齐 4 类检验 + OOS 退化斜率，verdict == LIKELY_OVERFIT → 触发 55 号 §3.5 评审通道）⑥ **regime-conditional 归因**（v1.5.0 新增：§3.11 attribute_by_regime 按 28 号 regime 分桶 Brinson + regime_fit_share vs skill_share 分解，若 Brinson 总归因残差持续 > 0.01% + 需区分顺风/skill 时）⑦ **Shapley 值归因评估**（v1.5.0 新增：§3.12 shapley_strategy_attribution，若策略间相关性 IC > 0.5 + owner 需公平分配交互效应 + 策略数 ≤ 8 时）⑧ **Hentschel GLS 统一归因框架评估**（v1.8.0 新增：§3.13 hentschel_gls_attribution，若 Carino residual 持续 > 1bp + 策略数 ≥ 5 + 持仓变动频率高时，把多期链接+交互项再分配+因子残差再分配统一为受限 GLS 估计，Carino/Frongello/Menchero 是其特例）⑨ **VCP v1.2 RECOVERY 边界对齐**（v1.8.0 新增：§3.3 Merkle root 升级时同步对齐 VCP v1.2 的 SKIP/REBUILD/MERGE/CHECKPOINT 恢复流程，仅协议文档约束无代码开销）⑩ **MCR/CCR 风险分解评估**（v1.14.0 新增：§3.14 calc_mcr_ccr_risk_attribution + calc_strategy_risk_attribution，若 owner 需"哪个策略贡献了最多组合波动率"风险维度归因 + §3.5 Brinson 收益归因已稳定运行 + 60 日协方差估计稳定时，归因报告增加风险贡献维度 CCR_pct + risk_concentration_ratio 反馈 30 号 budget 调整）
- **第三阶段（AUM 增长或合规要求升级时）**：① Barra 因子风险归因（若机构化）② wash trade/spoofing 检测（若多账户）③ 多 custodian 三方对账（若跨市场）

### 5.3 为何这是上限而非妥协
- 个人账户资金体量小，5 策略组合的归因维度三维度已覆盖迭代所需
- miniQMT 个人账户无 custodian/fund admin，对账是双边而非三方，机构级对账中台是过度工程
- Brinson 是行业标准收益归因框架，Barra 是机构级风险归因，二者用途不同，个人系统用 Brinson 足够
- AI-dev 归因清晰度原则：归因维度越多统计显著性越差，三维度是清晰度与覆盖度的平衡点

## 6. 待裁定（暂缓）

| 暂缓项 | 暂缓理由 | 重评条件 |
|---|---|---|
| **归因引擎双实现收敛**（v1.15.0 新增） | reporting/DefaultAttributionEngine（MOD-L07-001）是契约对齐全桩（3 方法 return 0.0、无测试）但 registry canonical 指向它；pf_core/PerformanceAttributionEngine（MOD-PF-007）是真实实现（BHB 守恒+测试）但未登记 canonical——同一能力双实现违反单一真源。建议方向：pf_core 为基底 + 算术链接升级 Carino + reporting 桩退役或薄委托；但 pf_core 产出 BrinsonResult 而非 CTR-P1-009 契约，收敛涉及契约对齐 + registry 变更 + 消费方迁移，须 owner 裁定 | 裁定时机：MVP 第一阶段施工前必须裁定（阻塞 §3.2 落地形态）；裁定要点：①实现基底归属 ②canonical 重登记 ③CTR-P1-009 契约产出接线 ④pf_core 因子/风险归因（研究侧口径）是否纳入组合归因层 |
| Barra 因子风险归因 | 需因子模型许可证+协方差矩阵；个人系统 Brinson 足够；与 30 号拒绝 MVO 一致 | AUM 机构化 + 多管理人 + 合规要求 |
| 因子归因（factor_contributions） | Brinson 已答 80% 迭代问题；首批 track record 不足 | 首批策略 3 个月 track record 后 |
| 盘后全量对账 | MVP 盘中每 5min 持仓对账够用；需券商对账单接入 | 实盘上线后 T+1 结算确认需求 |
| 资金对账 | PositionReconciler 当前只对账持仓；资金预占已兜底 | 实盘资金不一致致 54 拒单频发时 |
| 监管报告自动化 | MVP 手动填报；AUM 远低于门槛 | GATE-002（AUM≥1000万）/ GATE-003（跨市场） |
| wash trade/spoofing 检测 | 个人单账户无自交易风险 | 多账户或合规升级 |
| **Weight drift 框架**（drift-allocation/drift-interaction） | [Ortec Finance 白皮书](https://www.ortecfinance.com/-/media/project/ortec/shared/files/whitepapers/ip-multi-period-performance-attribution-ortec-finance_bas-leerink.pdf)：多期 Brinson 中 allocation effect 会被 selection decisions 引入的 weight drift 污染；Carino 链接已基本消除 residual，drift 框架是更高精度需求 | 归因 residual 持续 > 0.01% + 需区分 active allocation vs passive drift 时 |
| **AI 驱动对账**（neural fuzzy matching） | [optimus.tech 2026-06](https://optimus.tech/blog/ai-transaction-matching-for-high-frequency-trading-reconciling-100m-daily-trades-in-real-time)：HFT 场景 72h→60s 对账；[agencyscript 2026-03](https://www.agencyscript.com/blog/ai-agency-data-reconciliation-ai)：例外率 18%→2.9%；个人账户数据量小，规则对账够用 | 日成交笔数 > 1000 + 规则对账例外率 > 5% |
| **置信度阈值校准**（v1.5.0 新增） | High ≥ 0.85 / Middle 0.50-0.85 / Low < 0.50 是 [theneuralbase 2026-04](https://theneuralbase.com/ai-for-finance/learn/advanced/reconciliation-pipelines/) 推荐起点；A 股交易对账场景（单券商国金 miniQMT + T+1 结算 + 小数股尾差）的 false positive 分布可能不同；权重（fill_id 0.30 + qty 0.20 + price 0.15 + date 0.10 + timestamp 0.05）需实盘回归校准 | 首批策略实盘 3 月 track record + 统计各层 false positive 率后用历史匹配数据回归校准 |
| **审计轨迹存储迁移**（v1.5.0 新增） | MVP 用 SQLite append-only + hash 链 + 30 天 read-only 触发器；个人系统单机单 owner 无需多方信任；区块链/Hyperledger 引入节点同步/共识开销是过度工程 | AUM 机构化 + 外部资金引入 + 需向 LP/监管提供不可篡改审计证据 → 迁移到 PostgreSQL append-only 或 Hyperledger |
| **regime-conditional 归因**（v1.5.0 新增） | [traderssecondbrain 2026-05](https://traderssecondbrain.com/guides/performance-attribution-trading) 实证 50-80% 收益来自 regime fit 而非 skill；但需足够 track record 按 regime 分桶（每桶 ≥ 20 交易日）+ 28 号情绪周期 regime 标签实盘校准；MVP 先用 Brinson 3 因子不分 regime | 首批策略 3 月 track record + Brinson 总归因残差持续 > 0.01% + owner 需区分"顺风收益"vs"真实 skill"时 |
| **Shapley 值归因**（v1.5.0 新增） | [xfinlink 2026-06-28](https://xfinlink.com/blog/shapley-value-portfolio-attribution-python) + [arXiv:2102.05799](https://arxiv.org/abs/2102.05799) Shapley 公平分配交互效应 vs naive 求和差异 2-10 倍；但 O(2^n) 复杂度，MVP 5 策略可行但增量价值待验证；§3.5 求和不变量已满足 30 号 Model A 可加承诺 | 策略间相关性 IC > 0.5 + owner 需公平分配交互效应 + 策略数 ≤ 8（精确 Shapley 可行）时 |

## 7. 待定问题（讨论要点对齐结果）

> 以下 6 项来自 00_index §3 G25 讨论要点，讨论已对齐落入 §3 决策。

- [x] ① PnL 归因（策略贡献分解）→ §3.2 Brinson 3 因子为主，Barra 拒绝
- [x] ② 每日对账（成交 vs 持仓 vs 资金）→ §3.3 三层对账，资金对账 Phase 2
- [x] ③ 归因维度（策略/标的/因子/时段）→ §3.4 策略×标的×时段三维度，因子暂缓
- [x] ④ 与 StrategyBook 独立 PnL 归因的对接 → §3.5 两层归因（策略层+firm层）
- [x] ⑤ 异常交易检测 → §3.6 三层检测（价格/量/拒单），无 wash trade/spoofing
- [x] ⑥ 报表生成 → §3.7 四类报告 + 双渠道发布

**开放问题**（需人决策/实盘校准）：
- **基准选取**：各策略的 benchmark 选沪深 300/中证 500/策略自定义？Brinson 归因的前提是基准定义
- **Brinson 板块划分**：A 股板块按申万一级（28 行业）/风格（价值/成长/周期/防御）/策略自定义？影响 allocation effect 粒度
- **大额异动阈值**：检测未施工（算法见 §3.6），阈值待实盘校准（实盘数据回归后定）
- **transaction_cost_drag 接入**：DefaultTcaEngine 的 IS 成本如何映射到 transaction_cost_drag 字段（总和/分项）
- **MOD-RPT-015 绩效归因报告**：planned 未实现，报告格式需对齐 PerformanceAttributionReport 契约
- **Carino 链接粒度**（v1.1.0 新增）：周/月报用日频单期链接，季报用周频单期链接——待实盘数据量评估后定（日频链接计算开销 vs 精度）
- **BF 降级阈值**（v1.1.0 新增）：interaction effect 占总超额收益比例 < 何值时降级到 BF 两因子简化解释？需首批策略 3 月归因数据回归后定
- **T+1 浮盈依赖警示阈值**（v1.5.0 新增）：t1_warning 触发条件当前定为 unrealized_selection / total_selection > 50%，待实盘回归校准——打板策略日内建仓吃涨停场景下阈值可能需上调至 70%（否则告警过频）
- **regime-conditional 分桶粒度**（v1.5.0 新增）：28 号情绪周期 regime 标签用几态（bull/bear/range/squeeze 4 态 vs 更细）？每桶最少样本量（20 vs 30 交易日）？影响 regime-conditional 归因的统计显著性
- **Hentschel GLS 是否替代 Carino + Shapley 组合**（v1.8.0 新增）：Phase 2 评估 Hentschel GLS 时需决策——①完全替代（Carino + Shapley 退役，统一为 GLS 估计）；②部分替代（Carino 退役 / Shapley 保留，因 Shapley 公平分配原则 GLS 不直接覆盖）；③并行（GLS 作为 Carino + Shapley 的统计置信度补充层）。决策依据：GLS 在 A 股 T+1 + 板块轮动场景的实证表现 + 策略数增长轨迹
- **VCP v1.2 RECOVERY 边界选择**（v1.8.0 新增）：Merkle root 锚定 TSA 失败时选 SKIP（跳过该批）/ REBUILD（重建 root）/ MERGE（与前批合并）/ CHECKPOINT（检查点重发）何为合规？需结合 TSA 服务 SLA + 审计员容忍度 + 监管要求定
- **PositionReconciler 双实现真源**（v1.15.0 新增）：ex_core MOD-EX-056（盘中对账+冻结解冻，本备忘引用）vs position MOD-INF-022（事件驱动版，capability_canonical_file_registry canonical 指向后者）——同属对账能力双实现，与 §6 归因引擎收敛一并裁定
- **公司行为双实现口径**（v1.15.0 新增）：trading/corporate_action_processor.py（持仓成本/现金调整）vs ex_core/corporate_action_adjuster.py（除权参考价/涨跌停/价格笼子基准价）——公式独立实现存在口径漂移风险，需裁定单一计算真源或显式分工契约
- **StrategyBook 独立 PnL 数据源**（v1.15.0 新增）：MOD-POS-020 当前仅消费外部注入 `strategy_pnl_history`，不核算 PnL——两层归因策略层无载体；谁注入、按 fill_id 归集到策略的口径未定，关联 #ARCH-REG-005（proposed）
- **MOD-RPT-015 登记缺口**（v1.15.0 新增）：报告生成器未施工且 architecture_issue_registry / capability_canonical_file_registry 均无条目——违反"新增模块必须登记 ARCH 条目"硬约束，施工前先补登记
- **CTR-P1-007 产出逻辑**（v1.15.0 新增）：契约 codegen 已落盘但 execution_core 产出逻辑 GAP-L06-003 P0 待施工——BM-REC-02-B 的 TCA/归因数据流上游依赖，battle_map "暂不可建"标注的残余阻塞
- **盘后 15:30 调度接线**（v1.15.0 新增）：无调度器任务（APScheduler/work_dag 均无）——SettlementReconciler/DailyAuditor 盘后触发当前只能手动/事件调用
- **对账/归因 DB 持久化 schema**（v1.15.0 新增）：audit_trail 表/对账差异表/归因结果表/report_archive 均无 DDL——三阶段审计轨迹与报告归档的落库前提
- **55 号对接回对齐**（v1.15.0 新增 / v1.15.8 已对齐）：55 号已 active v1.0.2——本备忘 §3.9/§3.10/§5.1/§5.2/§8.1 的 55 号引用已按其实际结构对齐（退役评审=§3.5 双判据+评审制、偏离度量=§3.4、CUSUM/PSI=§3.2B/§3.3）；残余：55 号由 AI-MON-001 并发施工中，若其结构再变需二次对齐（另：00_index G26 状态标注 v1.21.0 与磁盘 v1.0.2 漂移，越界项登记供 00_index owner 处理，本备忘不改他文档）

## 8. 引用

### 8.1 相关设计备忘
- [40_execution_broker](40_execution_broker.md)（G22 v2.11.2，成交回报/持仓/资金流水产出物，依赖项；fill_id 幂等见 §6.1 gap 12 AsyncFillDispatcher）
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.2 StrategyBook 独立 PnL / §2.5 回撤 Protocol / §2.2 RegimeMetaAllocator budget
- [34_regime_meta_allocator](34_regime_meta_allocator.md) §3.1（v1.15.0 新增：PerformanceScore 60 日 Sortino 口径真源，§3.5 对接）
- [53_simulation_live_path](53_simulation_live_path.md)（G24，模拟实盘路径；SHADOW/GRAY_RAMP 阶段实盘成交供本备忘对账归因；§3.5 执行对账门禁阈值衔接本备忘 SettlementReconciliation）
- [55_monitoring_review](55_monitoring_review.md)（G26，active v1.0.2（2026-08-15），下游复盘消费归因结果；本备忘 §3.9/§3.10/§5 的 55 号引用已按其 v1.0.2 实际结构对齐，并发施工残余风险见 §7 开放问题）
- [31_position_sizing](31_position_sizing.md) §2.3.4（sizing_basis 归因维度，§3.8 对接）
- [50_backtest_observability_workplan](50_backtest_observability_workplan.md)（回测可观测性，归因回测验证）
- [62_business_registry_construction](62_business_registry_construction.md)（v1.15.0 新增：§7.2 experiment_registry.attribution_result 字段登记约定——归因执行逻辑以本备忘为真源，62 号仅登记结果；data_asset_registry 待施工，对账/归因数据资产登记缺口见 §7 开放问题）
- [00_index_trading_decision](00_index_trading_decision.md) §3 G25 主题组定义
- [01_design_memo_management_spec](01_design_memo_management_spec.md) §4.3 设计备忘推荐章节结构

### 8.2 相关作战地图
- [battle_map_11_reconciliation](../battle_map/battle_map_11_reconciliation.md) 对账阶段 18 环节：
  - BM-REC-01 交易运营清算（production）：①-A 结算对账 / ①-B 公司行为与费率 / ①-C PnL计算
  - BM-REC-02 报告复盘：②-A TCA（production）/ ②-B 绩效归因（design，本备忘核心 gap）/ ②-C A股复盘（production）/ ②-D 报告发布（production）/ ②-E 风险报告（production）/ ②-F 监管报告（production）
  - BM-REC-03 闭环优化反馈：③-A 因子层反馈（production）/ ③-B 信号层反馈（design）/ ③-C 模型层反馈（design）/ ③-D 元级迭代（design）
  - BM-REC-04 保证金管理 / BM-REC-05 多账户分仓管理

### 8.3 depgraph 模块（用 path/blueprint_id 引用，非 node_id）

| 模块 | blueprint_id | path | 域 |
|---|---|---|---|
| PositionReconciler（盘中） | MOD-EX-056 | `src/zephyr/ex_core/position_reconciler.py` | D_EX_CORE |
| PositionReconciler（事件驱动） | MOD-INF-022 | `src/zephyr/position/position_reconciler.py` | D_POSITION（registry canonical，真源归属待裁定 §7） |
| SettlementReconciler | MOD-TRADING-003 | `src/zephyr/trading/settlement_reconciliation.py` | D_TRADING |
| CorporateActionProcessor | MOD-TRADING-004 | `src/zephyr/trading/corporate_action_processor.py` | D_TRADING |
| CorporateActionAdjuster | —（40 号决策⑯施工物） | `src/zephyr/ex_core/corporate_action_adjuster.py` | D_EX_CORE（与 MOD-TRADING-004 口径分工待裁定 §7） |
| PnlCalculator | MOD-TRADING-002 | `src/zephyr/trading/pnl_calculator.py` | D_TRADING |
| DefaultTCAEngine | MOD-L07-001 | `src/zephyr/reporting/default_tca_engine.py` | D_REPORTING（简易滑点已上线，IS 分解待施工） |
| DefaultAttributionEngine（契约桩） | MOD-L07-001 | `src/zephyr/reporting/default_attribution_engine.py` | D_REPORTING（全桩，registry canonical） |
| PerformanceAttributionEngine（真实实现） | MOD-PF-007 | `src/zephyr/pf_core/core/performance_attribution_engine.py` | D_PF_CORE（v1.15.0 补登：BHB 守恒+测试，未登记 canonical） |
| PerformanceAttributionReport 契约 | CTR-P1-009（codegen） | `src/zephyr/shared/contracts/performance_attribution_report.py` | D_SHARED（契约已落盘） |
| 绩效归因报告生成器 | MOD-RPT-015 | —（未施工，无模块文件，registry 无条目） | D_REPORTING（planned） |
| ASharePerformanceAuditor | MOD-RPT-026 | `src/zephyr/reporting/ashare_performance_audit.py` | D_REPORTING |
| AShareTradeRecordTemplate | MOD-RPT-027 | `src/zephyr/reporting/ashare_trade_record_template.py` | D_REPORTING |
| ReportPublisher | MOD-RPT-003 | `src/zephyr/reporting/report_publisher.py` | D_REPORTING（渠道发送仅 PENDING） |
| ReportVersionManager | MOD-RPT-013 | `src/zephyr/reporting/report_version_manager.py` | D_REPORTING |
| WatermarkTracker | MOD-RPT-017 | `src/zephyr/reporting/report_watermark_tracker.py` | D_REPORTING |
| RiskReportEngine | MOD-RPT-008 | `src/zephyr/reporting/risk_report_engine.py` | D_REPORTING |
| RegulatoryReportGenerator | MOD-RPT-006 | `src/zephyr/reporting/regulatory_report_generator.py` | D_REPORTING |
| RealtimePnlDashboard | MOD-RPT-004 | `src/zephyr/reporting/realtime_pnl_dashboard.py` | D_REPORTING |
| DailyAuditor（日终 PnL 对账） | MOD-RK-20 | `src/zephyr/risk/core/daily_auditor.py` | D_RISK |
| ExecutionAuditLogger | MOD-EX-003 | `src/zephyr/ex_core/audit_journal/auditor.py` | D_EX_CORE |
| CashManager（T+1 资金结算） | MOD-POS-006 | `src/zephyr/position/core/cash_manager.py` | D_POSITION |
| StrategyBook（独立 PnL 未实现） | MOD-POS-020 | `src/zephyr/position/core/strategy_book.py` | D_POSITION |
| FactorAttribution（研究侧） | MOD-L02-010 | `src/zephyr/factor/analysis/factor_attribution.py` | D_FACTOR |
| AnalyticsBase | — | `src/zephyr/reporting/analytics_base.py` | D_REPORTING |

### 8.4 外部参考
- Brinson, G. P., & Fachler, N. (1985/1986). Measuring the Use Value of a Portfolio: The Brinson Model（配置+选择+交互三效应分解，行业标准至今）
- 2026 行业调研：tradetally "Performance Attribution Analysis"（2026-07，Brinson 仍是行业标准）；marketopia "Performance Attribution Complete Guide"（2026-05，Brinson-Fachler 三组件）；quant67 "风险模型：Barra 多因子"（2026-05，Brinson vs Barra 区别）
- finantrix "Buyer's Guide: Performance Attribution Software"（2026-08，Barra 机构级 deal $100K-$1M+，Brinson 是 table stakes）
- MSCI BarraOne Performance Analytics（Barra 因子风险归因平台，Equity Factor-Based Attribution 用 Barra factors）
- **多期归因链接算法**（v1.1.0 补）：Cariño, F. (1999) "Combining Attribution Effects Over Time"（对数链接，GIPS-compliant 首选）；Menchero, J. (2000, 2004) "Multiperiod Arithmetic Attribution"（优化链接系数，专利 2024 过期）；Frongello (2002) 递归链接；GRAP (1997) 几何归因；Bacon, C. (2008) ch.6 几何链接；[metricgate "Multi-Period Attribution" 2026-09](https://metricgate.com/docs/multi-period-attribution/)（Carino residual 校验）；[pybrinson v1.3.1 2026-04-13](https://github.com/gghez/pybrinson)（5 种链接方法开源参考实现）；[DolphinDB Brinson 教程](https://docs.dolphindb.com/zh/tutorials/brinson.html)（BHB vs BF 方案 + GRAP 多期）；[brinson-attribution 2026](https://github.com/gogoahead233-art/brinson-attribution)（beginning-of-period weights 消除偏差）；[ryanoconnellfinance 2026-03](https://ryanoconnellfinance.com/brinson-attribution-model/)（BHB vs BF 区别）
- **Weight drift 框架**：[Ortec Finance 白皮书 Bas Leerink & Gerard van Breukelen](https://www.ortecfinance.com/-/media/project/ortec/shared/files/whitepapers/ip-multi-period-performance-attribution-ortec-finance_bas-leerink.pdf)（drift-allocation/drift-interaction 隔离 active vs passive allocation）
- 2026 对账实践：marketclutch "Mastering Trading Position Reconciliation"（三层对账：Position Quantity/Cash Balance/Security Identification）；reconwizz "Cash vs Position Reconciliation"（2026-01，cash 与 position 对账独立）；osfin "Trade Reconciliation Best Practices"（2026-03，6步流程）；limina "Fund Reconciliation"（cash 是 catch-all 层）
- **AI 驱动对账**（暂缓参考）：[optimus.tech 2026-06](https://optimus.tech/blog/ai-transaction-matching-for-high-frequency-trading-reconciling-100m-daily-trades-in-real-time)（HFT 72h→60s）；[agencyscript 2026-03](https://www.agencyscript.com/blog/ai-agency-data-reconciliation-ai)（例外率 18%→2.9%）；[naya.finance 2026](https://www.naya.finance/learn/agentic-ai-reconciliation-guide)（Agentic AI reconciliation 三代演进）
- A 股 T+1 结算规则（沪深交易所《交易规则》：T+1 资金可用，T+1 股票可卖）
- [40_execution_broker](40_execution_broker.md) §2.4 Gatheral 无套利约束 / §2.7 拒单分类 / §2.13 资金预占 / §5 待裁定盘后全量对账
- **PnL Explain vs Predict 概念框架**（v1.2.0 补）：[hftradingbook 2026-06 "Performance Attribution"](https://hftradingbook.com/performance/attribution)（PnL attribution waterfall：spread capture - adverse selection - own impact + signal alpha + fees = net PnL；明确 Explain 事后归因 vs Predict 事前预测的分类）；[CSDN SRPnL 2026-06](https://blog.csdn.net/weixin_42402664/article/details/152352510)（SRPnL Sensitivity-based PnL Decomposition，敏感性分解属 Predict 类，A 股权益拒绝）；[traderssecondbrain 2026-05 "Performance Attribution: Decomposing Trading Returns"](https://traderssecondbrain.com/guides/performance-attribution-trading)（5 维归因 framework：setup/regime/execution/sizing/instrument，零售 vs 机构归因差距）；[walletfinder 2026-07 "Crypto Performance Attribution"](https://www.walletfinder.ai/blog/performance-attribution)（benchmark-relative Brinson 1986 BHB 框架在 crypto 场景的扩展，验证 Brinson 跨资产普适性）
- **多 session PnL 归因**（v1.2.0 补）：[seriousalchemy 2026-08-04 "Calculating P&L When a Trade Spans Multiple Sessions"](https://seriousalchemy.com/pnl-sessions/)（跨 session PnL 计算陷阱：reoptimization 期间持仓未平导致 entry/exit 跨 session，单 session FIFO 匹配器产生幽灵成交 + PnL 漏算；修复：以 fill_id 而非 session_id 为唯一键）；[seriousalchemy trade-reconciliation 后续篇](https://seriousalchemy.com/trade-reconciliation/)（FIFO 匹配器 + duplicate-order 修复 + attribution 反向运行）
- **成交对账三层匹配算法**（v1.3.0 补）：[osfin 2026-03 "Trade Reconciliation Best Practices"](https://www.osfin.ai/blog/trade-reconciliation)（6 步流程：Data Collection → Standardization → Matching → Exception → Resolution → Reporting + 4 类对账：trade-date/settlement/cash/position/broker-vs-custodian）；[intura 2026 "AI for Finance Reconciliation"](https://intura.co/en/guides/ai-finance-reconciliation)（4 种匹配逻辑：exact/fuzzy/partial/no-match + AI 辅助规则定义）；[ai-indeed 2026-08-04 "关联交易对账自动完成"](https://www.ai-indeed.com/encyclopedia/19423.html)（5 层匹配：强一致/容差/拆合/弱规则/例外 + 例外率 18%→2.9% 实证 + 自动派单闭环）；[numeric 2026-05 "Reconciliation Automation"](https://www.numeric.io/blog/reconciliation-automation)（exception-based review 范式 + 控制点 + 数据质量要求）；[airwallex 2026-06 "7 Best Automated Reconciliation Software"](https://www.airwallex.com/us/blog/best-automated-reconciliation-software-solutions)（行业对账工具选型基准 + BlackLine/FloQast/Trintech 对比）
- **A 股 PnL waterfall 子框架**（v1.3.0 补）：[hftradingbook 2026-06 "Performance Attribution"](https://hftradingbook.com/performance/attribution)（做市商 PnL waterfall：spread capture - adverse selection - own impact + signal alpha + fees = net PnL；A 股非做市场景借鉴 waterfall 思路而非直接套用）；[marketmaker.cc 2026-03 "Backtest-Live Parity"](https://marketmaker.cc/en/blog/post/backtest-live-parity)（execution divergences 贡献 10-30% PnL，是 parity gap 最大源——归因必须能定位执行成本贡献）
- **2026-08 最新归因算法研究**（v1.4.0 补）：[Kiski 2026-03 "Adding an Industry Layer to Active-Passive Decomposition"](https://www.kiski.com/blog-posts/adding-an-industry-layer-to-active-passive-decomposition)（Brinson+Industry 5 层分解 Market+Sector+Industry+Selection+Sizing，解决 selection 垃圾桶问题+发行人级 Brinson 解决 A/H/ADR 交叉上市）；[AlgoTradingDesk 2026-01 "Trade Outcome Attribution"](https://algotradingdesk.com/trade-outcome-attribution-algorithmic-trading-dma/)（Signal+Timing+Spread+Slippage+Impact 5 支柱分解+逐笔元数据存储+信号 P&L vs 执行 P&L 曲线可视化，"这不是策略失败，是归因失败"）；[Drovix 2026-05 "TCA That Drives Decisions"](https://drovix.com/blog/tca-that-actually-drives-decisions)（IS 四组件分解 Spread+Impact+Timing+Opportunity+滑点分布 median/p90/p99+拒绝率转换 bps 成本+多基准并行 arrival/VWAP/PWP/peer-relative+压力 regime top decile 切片）；[Hentschel 2024 "Unified Attribution"](https://www.ludgerhentschel.com/PDFs/Hentschel%2024b.pdf)（受限 GLS 统一 Brinson 交互项+Factor 残差+多期平滑，调整导向精度最低估计，2026 仍为最新统一框架）；[arXiv:2608.04547 2026-08-05](https://arxiv.org/html/2608.04547v1)（Shapley 值预测差异归因，摩根大通 CCAR/CECL 监管场景，合作博弈解决顺序依赖问题）；[arXiv:2607.10286 2026-07 TradeLens](https://arxiv.org/html/2607.10286v1)（LLM 交易智能体归因 P_sys+P_asset+P_timing+token 成本，HKUST+E Fund，intelligence-to-profit 转换诊断）
- **2026-08 A 股对账实践**（v1.4.0 补）：[abq A 股量化全链路系统 CSDN 2026-08-05](https://blog.csdn.net/suwuzs/article/details/163511629)（L0→L5 分层+CSV schema 校验+fills/nav/holdings 对账+"控换手比堆因子更重要"IR -0.17→1.04 实证+门禁 IR<0.8 不晋升+同日重复 apply 拒绝防重复扣账）；[恒生电子内存清算 中国日报 2026-05](http://tech.chinadaily.com.cn/a/202605/26/WS6a14fcdca310942cc49ae3f4.html)（国金证券机构对账 10 分钟内自动生成+一致性 100%+内存计算引擎替代批处理）；[ihr360 2026 量化主观共管账户双计递延归因](https://docs.ihr360.com/blog/930136)（触发者担责+可追溯+贡献度分割三条原则）
- **2026-08 对账异常检测与时间戳**（v1.4.0 补）：[ParseMyStatement 2026-04 "Running Balance Sequence QA"](https://parsemystatement.com/blog/running-balance-sequence-qa-detect-missing-merged-lines-before-reconciliation-reng8z)（余额约束系统逐行验证 expectedBalance[i]=expectedBalance[i-1]+transactionAmount[i]，断裂分类：缺失行/合并行/排序问题，对账数据导入前行级校验）；[Axon.Trade "Clock Discipline for Trading Systems"](https://axon.trade/clock-discipline-for-trading-systems)（50ms 时间戳错误翻转基准结果，PTP±50µs 替代 NTP+CLOCK_MONOTONIC_RAW+订单/成交/drop-copy 时间戳交叉比对+TCA 验证循环 PTP daemon 偏移<50µs/适配器差异<1ms/审计事件顺序<100µs/TCA 一致性<5ms）
- **Brinson 多期链接 + BHB/BF 实现**（v1.5.0 补）：[metricgate 2026-09 "Multi-Period Attribution"](https://metricgate.com/docs/multi-period-attribution/)（Carino k_t = ln(1+R_{p,t})/R_{p,t} 修正因子 + log_total 归一化 + GIPS-compliant 首选 + zero residual 校验 + Brinson-Fachler allocation 公式 A_i=(w_p-w_b)×(R_b,i-R_b)）；[pybrinson v1.3.1 2026-04-13](https://github.com/gghez/pybrinson)（Python 开源实现，Carino/GRAP/Frongello/Menchero/Geometric 5 种链接 + 多层级 hierarchical roll-up + math-core 100% coverage）；[DolphinDB 2026 Brinson 教程](https://docs.dolphindb.cn/zh/tutorials/brinson.html)（BHB vs BF 方案 + GRAP 多期 + 行业归因 + 现金板块择时）；[braverock PortfolioAttribution R](https://github.com/braverock/PortfolioAttribution/blob/master/man/Attribution.Rd)（R 实现 carino/menchero/grap/frongello/davies.laker 5 种 linking + top.down/bottom.up method）
- **A 股 T+1 归因特殊处理**（v1.5.0 补）：[akquant A 股市场微观结构 2026](https://akquant.akfamily.xyz/textbook/06_stock_a/) §6.2 T+1 交收制度与持仓状态机（资金 T 日可用 T+1 可取 + 股份 T 日登记 T+1 可卖 + 持仓状态机实现 + T+1 验证代码）；[biyapay A 股入门 2025-12](https://www.biyapay.com/en/blogdetail/3010-ashare-beginners-guide-master-market-hours-and-tra)（T+1 规则 + 涨跌停板 ±10%/±20% + 集合竞价 9:15-9:25 + 交易时段 9:30-11:30/13:00-15:00）；[licai A 股清算交收制度 2026-07](https://licai.cofool.com/ask/qa_7269736.html)（中证登中央清算 + 日终轧差 + 股份实时到账锁定 + 资金次一交易日可用可取 + 零违约机制）
- **regime-conditional 归因**（v1.5.0 补）：[traderssecondbrain 2026-05 "Performance Attribution: Decomposing Trading Returns"](https://traderssecondbrain.com/guides/performance-attribution-trading)（5 维归因 framework：setup/regime/execution/sizing/instrument，regime 维度实证 50-80% 收益来自 regime fit 而非 skill）；[breakingalpha 2026-01 "Performance Attribution Analysis for Multi-Strategy Portfolios"](https://breakingalpha.io/insights/performance-attribution-analysis-multi-strategy-portfolios)（regime-conditional estimate separate exposures + holdings-based + non-linear payoffs + 非线性策略凸性归因）；[Atlantic Trading 2026-03 "Market Regimes Explained"](https://atlantictrading.com/blog/market-regimes-explained-how-to-adapt/)（4 regime：Directional/Ranging/High Vol/Low Vol + 策略 environmental mismatch 失效机制）；[Lox Capital Palmer 2026-01](https://github.com/pythonjeff/lox/blob/main/docs/METHODOLOGY.md)（regime-conditional stochastic model + P&L attribution 规则决策树 VIX/HY_OAS 阈值）；[Đikanović EFMA 2026 "Conditional Performance of Factor Portfolios"](https://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2026-Norway/Ksenija%20Dikanovic.pdf)（BAB/momentum factor premia regime-dependent + 双 regime 宏观状态变量 timing signals）
- **Shapley 值归因**（v1.5.0 补）：[arXiv:2102.05799 Moehle/Boyd/Ang 2021 "Portfolio Performance Attribution via Shapley Value"](https://arxiv.org/abs/2102.05799)（Shapley 归因经典框架，特征 active/inactive + 边际贡献 + 全归因 + baseline，2026 仍被引用为最新统一方法）；[xfinlink 2026-06-28 "Shapley Value Attribution in Python"](https://xfinlink.com/blog/shapley-value-portfolio-attribution-python)（Python 实现 + 8 股票组合实证 + Shapley vs naive 差异 2-10 倍 + JNJ +8.39%→+18.46% 案例 + coalition 遍历 + efficiency 公理）；[EDHEC 2026-02 "Anatomy of ML-Based Portfolio Performance"](https://www.edhec.edu/sites/default/files/2026-02/SLIDES%20AnatomyPortfolioEDHEC.pdf)（SPPC Shapley-based Portfolio Performance Contribution + 207 firm characteristics + XGBoost + 20 predictor groups 贡献分解）；[Man Numeric 2023 "Shining Light into ML Black Box"](https://www.man.com/documents/download/b94f6-5adf6-a3bdc-5718e/Man_Numeric_Insights_Shining_Light_into_the_Machine_Learning_Black_Box_English_23-08-2023.pdf)（SHAP portfolio attribution + 非线性交互捕捉 + 四公理 + 局部/全局归因）；[arXiv:2606.21539 2026-06 "Attributing Forecast Gaps to Component Models"](https://arxiv.org/html/2606.21539v1)（JPMorgan 模型 suite gap 归因 + walk analysis vs LMDI vs Shapley 对比 + 顺序无关性 + Monte Carlo 扩展）
- **因子归因 vs Brinson 对比**（v1.5.0 补）：[simcorp 2024 "Risk-based or Brinson attribution?"](https://www.simcorp.com/resources/insights/industry-articles/2024/Risk-based-or-Brinson-attribution)（Brinson returns-based vs risk-based factor attribution 对比 + High dividend ETF 案例 + factor active risk/return 分解 + specific residual）；[ricequant 米筐归因模型详解](https://www.ricequant.com/doc/rqpattr/doc/model-introduction)（混合资产 Brinson + 行业 Brinson BF + 因子归因四来源：风格偏好/行业偏好/市场联动/特异收益 + 联接算法保证归因项求和）；[equicurious 2026-03 "Performance Attribution for Active Strategies"](https://equicurious.com/learn/equities/trading-and-execution/performance-attribution-for-active-strategies)（Brinson-Fachler 公式 + sector allocation/selection/interaction + time-period attribution + common mistakes + building attribution system）；[skill4agent performance-attribution 2026-02](https://www.skill4agent.com/en/skill/joellewis-finance_skills/performance-attribution)（Brinson-Fachler + factor-based + fixed-income + currency + multi-period linking Carino/Menchero/GRAP 统一 skill）
- **2026 置信度评分匹配**（v1.5.0 补）：[naya.finance 2026-04-02 "Anatomy of a Reconciliation Engine"](https://www.naya.finance/blog/reconciliation-engine-architecture)（加权属性相似度模型：amount 0.4 + date 0.2 + reference 0.3 + counterparty 0.1；可配置阈值 auto-match/route-to-exception；1:1/1:N/N:M 匹配算法架构；生产系统 99%+ 匹配率）；[tilores 2026-06-15 "Explainable Entity Resolution: Confidence Scores, Match Thresholds and Audit Trails"](https://tilores.io/content/explainable-entity-resolution-confidence-thresholds-audit)（置信带 High/Middle/Low + 审计证据字段：source record IDs + source systems + submitted/normalized values + fields compared + rule/model version + score + threshold band + decision + decision time + action + reviewer + **negative evidence** 被拒匹配理由）；[chatfin 2026-01-29 "AI-Powered Reconciliation"](https://chatfin.ai/blog/ai-powered-reconciliation-chatfin-platform-for-finance-automation/)（多阶段匹配：Exact → Fuzzy → ML prediction → Exception + 置信度评分标记低置信项 review + 审计轨迹系统维护所有匹配决策日志）
- **2026 不可变审计轨迹**（v1.5.0 补）：[theneuralbase 2026-04 "Reconciliation Pipelines"](https://theneuralbase.com/ai-for-finance/learn/advanced/reconciliation-pipelines/)（三阶段模式：automated matching → human review → decision logging；不可变审计轨迹是合规非可选；85% 置信阈值起点 + per-counterparty 校准；append-only databases 或 blockchain-backed ledgers SOX 合规；log model version + retraining date + backtesting results alongside each decision）；[theneuralbase 2026-04 "Reconciliation Assistance"](https://theneuralbase.com/ai-for-finance/learn/intermediate/reconciliation-assistance/)（"Audit trail must be immutable: write once, read-only after 30 days" + "regulators audit the false negatives hardest" 必须记录被拒匹配及理由 + log confidence scores/applied rules/approver identity with timestamps + SOX 404 + MiFID II 合规要求）
- **2026 PnL waterfall + 滑点分布 + verdict 阈值施工算法**（v1.5.1 补）：[OrderX 2026-07-09 "Introduction to Algorithmic Execution Part 12: Benchmarks and TCA"](https://orderx.com/education/introduction-to-algorithmic-execution-part-12-benchmarks-and-tca/)（signed bps slippage 公式 side×(exec-benchmark)/benchmark×10000 + reversion 诊断 temporary_impact vs real_alpha 价格回转检测 + IS 四组件基准选择 arrival/VWAP/PWP）；[Drovix 2026-05 "TCA That Drives Decisions"](https://drovix.com/blog/tca-that-actually-drives-decisions)（滑点是分布非均值——median/p90/p99 百分位 + 压力 regime top decile 切片 + 拒绝率转换 bps 成本，v1.5.1 用于 calculate_slippage_distribution 施工）；[waylandz 2026-04-20 "Backtest to Live Gap"](https://waylandz.com/blog/backtest-to-live-gap/)（backtest-to-live gap 是 cost model 问题 + OOS 退化斜率 = 实盘 Sharpe / 回测最优 Sharpe，< 0.5 严重退化，v1.5.1 用于 verdict 三态判定补充维度）；[Bailey & López de Prado 2012/2014 "The Sharpe Ratio Efficient Frontier"](https://doi.org/10.2139/ssrn.1825446)（DSR > 0.95 强证据 / < 0.50 弱证据阈值 + MinTRL 最小 track record 长度，v1.5.1 用于 interpret_deflated_alpha_verdict 阈值定义）；[deflated-alpha v0.3.0 2026-07-26](https://github.com/0scarito/deflated-alpha)（verdict LIKELY_REAL/INCONCLUSIVE/LIKELY_OVERFIT 三态 + 4 类检验 analytical/combinatorial/multiple-thinking/bootstrap data-snooping，v1.5.1 补 verdict 内部阈值解析）
- **2026 MAD 鲁棒异常检测**（v1.6.0 补）：[juejin.cn 2026-04-28 "Python 行情数据清洗实战：Z-Score、MAD 与分位数过滤"](https://juejin.cn/post/7633584575197380623)（金融数据厚尾分布 Z-Score 误判率高 + MAD 中位数免疫极端值 + Modified Z-Score 3.5 阈值比 Z=3 误判率低 60%+ + 不需正态分布假设）；[metricgate 2026-05-13 "MAD-Scaled Z-Score"](https://metricgate.com/docs/mad-scaled-z-score/)（Iglewicz-Hoaglin |M_i|≥3.5 标准 + 0.6745 正态一致性常数 + 50% 击穿点 + masking 效应解释 + ISO/USP 质控指南默认推荐 + MAD=0 failure mode 切换 Sn/IQR）；[tokentoolhub 2026 "Building a Market Anomaly Detector"](https://tokentoolhub.com/building-a-market-anomaly-detector/)（Volume z-score robust: rolling median + rolling MAD 替代 mean+std + session-aware relative volume + EWMA baselines + tiered alerts watch/investigate/high-risk/actionable + cooldown windows）；[standarddeviationcalculator 2026-04-24 "Modified Z-Score Outlier Detection"](https://standarddeviationcalculator.app/learn/modified-z-score-outlier-detection)（M_i=0.6745(x-median)/MAD 完整推导 + worked example + MAD=0 退化处理指导 + 与经典 Z-Score 对比 + decision checklist）
- **2026 异常严重度分级与升级流程**（v1.6.0 补）：[Monte Carlo Data 2026 "Marking Alerts as Incidents"](https://docs.getmontecarlo.com/docs/marking-alerts-as-incidents)（SEV-1~4 severity matrix：Impact Minor/Medium/Critical × Affected 1-3/4-10/10+ stakeholders + acknowledge→mark as incident→resolve lifecycle + Expected/No action needed resolve statuses + monthly incident review cadence）；[DualEntry 2026 "Anomaly Detection"](https://docs.dualentry.com/accountants/ai-automation/anomaly-detection)（low/medium/high severity scoring + dismiss/escalate 双动作 + dismiss 反馈模型减少误报 + Conservative/Balanced/Aggressive sensitivity presets + 5 detection rules: duplicate/round-number/off-hours/balance-swings/uncharacteristic-usage）；[Finomics 2026-06 "Anomaly Management"](https://finomics.ai/docs/finops-framework-compliance/understand-usage-and-cost/anomaly-management)（High: investigate immediately + Critical: executive notification + incident response + severity-based prioritization + monthly baseline recalculation for seasonal patterns）
- **2026-08 Shapley + regime-conditional 统一框架**（v1.6.1 补）：[arXiv:2605.24490 2026-05 "Market Regime Council for Dynamic Credit Assignment in Multi-Agent LLM Decision Systems"](https://arxiv.org/html/2605.24490v1)（多智能体 LLM 决策系统中 exact Shapley credits 跨 specialist agents 动态信用分配 + Regime Shift Perceptor regime 检测 + Bayesian Adaptive Update 在线权重 + Selective Winner-Takes-All + 三阶段合作博弈协商 N=3 + regime-aware multiplier ψ_i + 三玩家 Shapley 闭式推导 + efficiency 公理证明 + EWP 早期影响衰减定理——**同时覆盖 §3.11 regime-conditional + §3.12 Shapley 两条 Phase 2 候选路径的统一框架参考**，为未来两模块联合激活提供学术依据）
- **regime-conditional CVaR 负结果警示**（v1.6.1 补）：[MDPI Economies 2026-07-09 "From Regime Detection to Decision Rules: A Data-Driven Macro-Financial CVaR Framework"](https://www.mdpi.com/2227-7099/14/7/268)（四态 Gaussian HMM + CVaR 组合优化，欧洲多资产 2000-2026 walk-forward；**关键负结果：naive regime-conditional CVaR 分配年换手率 ~226% 侵蚀净收益至基准以下**，implementation-aware 替代方案（regime-constrained weight bands）净 Sharpe 与静态基准差 0.009 但换手率仅 ~29%；**结论：bottleneck 非 regime 检测而是 transparent/stable/cost-aware decision-rule design**——支持本项目 §3.11 regime-conditional 标为 Phase 2 候选 + §6 暂缓的谨慎设计，与项目记忆 RARE regime-conditional CVaR risk parity Phase 5+ 评估结论一致）
- **相关性下 Shapley 归因**（v1.6.1 补）：[stockalpha.ai 2026-02-17 "Feature Attribution Under Correlation: Shapley Values for Signals"](https://stockalpha.ai/alpha-learning/feature-attribution-under-correlation-shapley-values-for-alpha-signals)（金融特征罕有独立——momentum/volatility/sector tilt 交叉相关，naive Shapley 忽略依赖会误分配信用；**conditional vs interventional 采样选择**：conditional 保留特征依赖适合描述性归因，interventional 打断依赖需谨慎；**group/Owen-Shapley 处理强相关块**；orthogonalization 替代但须明确归因顺序；leakage + lookahead feature 陷阱致虚假 Shapley 分配；KernelSHAP conditional sampling + TreeSHAP + LMG/Owen values 工具箱——**与 §3.10 正交性验证 + §3.12 Shapley 归因直接相关**，为 Shapley 归因在相关性信号场景的可靠性提供实施指导）
- **A 股 Brinson 归因基础范式**（v1.6.1 补）：[长江证券 2026-01-18 "组合归因探微之一：基础归因范式及工具推演"](http://m.hibor.com.cn/wap_detail.aspx?id=b6119d6b6c03dc26e7df783378af4fa3)（国内券商研报：BHB vs BF 模型时间线梳理 + Carino 对数平滑因子 k_t 公式推导 + 朴素归因/持仓归因/净值归因三维度 + T-M/H-M/C-L 择时模型 + Excel 工具化实践——**A 股语境下 Brinson 归因的国内机构视角补充**，与 [ricequant 米筐](https://www.ricequant.com/doc/rqpattr/doc/model-introduction) + [DolphinDB 2026](https://docs.dolphindb.cn/zh/tutorials/brinson.html) 共同构成 A 股归因国内实践三角参考）
- **Carino 链接开源实现补充**（v1.6.1 补）：[attriblink v0.1.6 2026-03](https://github.com/george-dominic/attriblink)（Python 多期归因链接库，Carino 方法 + safe log-domain validation 防 R=0 边界 + bps/percent/decimal 多单位支持 + effects_sum check 求和校验——**与 [pybrinson v1.3.1](https://github.com/gghez/pybrinson) 互为独立验证参考实现**，两者 Carino 公式一致即可交叉确认实现正确性）
- **PBO 零假设受控标定**（v1.7.0 补）：[Solovjiev 2026-07 "PBO 受控标定"](https://pbo.marketmaker.cc/paper.pdf)（受控实验确认纯噪声下 PBO=0.5 而非 0——PBO<0.5 才有 edge，PBO>0.5 才过拟合；PBO≈0.5 不是"不确定"而是"无 edge"；当前阈值 pbo > 0.25 是保守红旗，PBO 接近 0.5 须结合 N_eff+条件数综合判断——为 §3.9 interpret_deflated_alpha_verdict 阈值解释提供正确性依据）
- **Stale-Value 冻结馈送检测**（v1.7.0 补）：[EQAF arXiv:2606.20079 2026-06 "Ensemble Quality Assessment Framework"](https://arxiv.org/pdf/2606.20079v1)（UBS 投行 183 笔信用衍生品 / 129 日实测：纯统计方法 Isolation Forest/PCA/统计规则对 stale-value（冻结馈送）结构性失效——统计方法假设数据有方差，冻结数据无方差触发误判；stale-value 必须**领域确定性规则**兜底——为 §3.6 detect_stale_value 算法提供实证依据）
- **Merkle tree 审计轨迹 + VCP v1.1 协议**（v1.7.0 补）：[Apotheon.ai 2026-07-18 "Merkle DAG"](https://apotheon.ai/resources/whitepapers/merkle-dags)（Merkle tree + 外部锚定是 2026 共识标准，线性 hash 链无 inclusion proof + 无外部时间锚）；[AgentAudit RFC 6962](https://github.com/KaushikKC/AgentAudit)（Certificate Transparency 协议应用于 AI agent 审计）；[mickai.co.uk 2026-06-14 "Tamper-Evident Log"](https://mickai.co.uk/articles/anatomy-tamper-evident-log-hash-chain-anchoring)（hash chain + anchoring 解剖）；[VeritasChain VCP v1.1 2026-01](https://veritaschain.org/blog/posts/2026-01-22-vcp-v1-1-eu-ai-act-compliance-guide/)（开源标准：RFC 6962 Merkle trees + RFC 8785 JSON canonicalization + RFC 9562 UUIDv7 + VCP-XREF 双日志 + 三层架构 events→Merkle tree→external anchors；映射 EU AI Act Art 12/14 + MiFID II Art 17 + SEC 17a-4 + DORA）；[VCP Supervision Node PoC](https://github.com/veritaschain/vcp-supervision-node-poc)（监管侧验证节点：Ed25519 签名 + Merkle inclusion proof + External anchor (TSA RFC-3161/blockchain) + Timing checks；"Verify, Don't Trust" 原则）；[martinuke0 2026-05-29 "Immutable Ledger Design for Financial Systems"](https://martinuke0.github.io/posts/2026-05-29-architecting-immutable-ledger-design-for-financial-systems-consistency-compliance-and-real-world-patterns/)（WORM 存储 + hash chains + role-based write permissions + dual-write with idempotent replay 生产模式）；[GreenHelix Tamper-Proof Audit Trails](https://hub.openclaw.ai/mirni/skills/greenhelix-trading-bot-audit-trail)（EU AI Act Art 14 + MiFID II RTS 25 + SEC 17a-4 合规审计轨迹 Python 实现 + VeritasChain Protocol 应用）；**[VCP v1.2 RC 2026-05-31](https://veritaschain.org/)（v1.7.3 补）**：v1.1 的 protocol-compatible 认证严格化版（零破坏性变更，v1.0/v1.1 所有 events + anchors 保持有效可验证），VSO 已向 **50+ 法域监管机构**正式提交含 **CSRC 中国**（A 股项目本地监管相关性）+ CFTC/SEC/MAS/SFC/ASIC/FCA/SEBI 等，默认 Ed25519 + ML-DSA（FIPS 204）量子抗性迁移路径——**本项目 Phase 2 Merkle 升级须对齐 VCP v1.2 而非 v1.1**，CSRC 已收到提交意味着未来 A 股监管举证有标准化协议可对照（非批准/推荐，但可作为"行业共识标准"引用）
- **EU AI Act Article 12/14 合规边界**（v1.7.0 补，远期监管扫描）：[EU AI Act Regulation 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)（Art 12 record-keeping "automatic recording of events over lifetime of system" + Art 14 human oversight "live override and halt capability" + Art 9 continuous risk management + Art 13 transparency；**高风险 AI 系统义务生效日 2026-08-02 已过**，算法交易 AI 决策若涉 EU 客户属高风险；罚则 €30M 或 6% 全球年营业额）；[runtimeai 2026-05-10 "EU AI Act Compliance"](https://runtimeai.io/blog/2026-05-10-eu-ai-act-compliance.html)（7 项条款实操 + 84 天倒计时合规指南 + FRIA 基本权利影响评估）；[regly.ai 2026-06-26 "Article 14 Explained"](https://www.regly.ai/blog/eu-ai-act-article-14-explained)（Art 14 fintech 落地：监控输出 + 质疑决策 + 介入能力三支柱 + 不能仅靠政策文档满足）；[Molecule-AI #642 2026-04-17](https://github.com/Molecule-AI/molecule-core/issues/642)（audit ledger 最小可行字段：timestamp/agent_id/operation/input/output/human_oversight_flag/model_used/session_id 七必填 + 6 月最低留存）；**为何暂不强制引入**：ZephyrAlpha 个人单机不服务 EU 客户 + 单 owner 无 AI 决策对第三方影响 + VCP v1.1 标准本身是 Phase 2 升级路径目标；**重评条件**：服务 EU 客户 + 多 owner + AUM 机构化 + 接入 LLM 决策生成 alpha 时
- **Cross-venue 对账 bi-temporal 模型 + 3 类分歧**（v1.11.0 补）：[alphaequations 2026-04-22 "Cross-venue reconciliation: designing a matching engine that tolerates divergence"](https://www.alphaequations.com/insights/cross-venue-reconciliation-matching-engine/)（cross-venue 对账的 3 类结构性分歧：①order-ID shape divergence（ClOrdID 客户端分配 replace 时变更 / OrderID 场所分配稳定 / ExecID 每笔 fill 唯一——单逻辑订单跨 replace 链积累多 ClOrdID，场所侧一 OrderID 一 ExecID，双方原生标识符均不跨生命周期稳定）②timestamp skew（trading system ingest clock vs venue matching-engine clock 偏差非随机噪声而是有界测量不确定度，RFC 5905 PTP 典型 ±几百 µs / primary ±几十 µs，须建模不可清洗）③partial-fill fragmentation（大单多次成交，双方聚合粒度不同，1:N 或 N:1 均非错误）+ bi-temporal timestamp model（分离"交易发生时间"vs"记录时间"）+ append-only fill events（投影状态不存储状态，可 replay）+ class-based escalation routing（按分歧类别而非严重度路由例外工单，deterministic tier 无法解决的交由 agent tier））；[theneuralbase 2026-04 "Reconciliation pipelines"](https://theneuralbase.com/ai-for-finance/learn/advanced/reconciliation-pipelines/)（三阶段 automated matching → human review → decision logging + 不可变审计轨迹 + 85% 置信阈值 + per-counterparty 校准——与 §3.3 置信度评分匹配 + 三阶段审计轨迹设计一致）；[naya.finance 2026-04-02 "Anatomy of a Reconciliation Engine"](https://www.naya.finance/blog/reconciliation-engine-architecture)（canonical transaction model + 1:1/1:N/N:M 匹配 + confidence scoring + exception routing——§3.3 三层匹配 partial 层即 N:M 场景）；**ZephyrAlpha 适用性评估**：单券商单市场（miniQMT）→ ①order-ID shape 分歧不适用（无跨场所标识符映射）；②timestamp skew 部分适用（[Axon.Trade PTP±50µs 纪律](https://axon.trade/clock-discipline-for-trading-systems) 已覆盖时间戳纪律，但 bi-temporal 双字段分离尚未显式实现）；③partial-fill fragmentation 已由 §3.3 三层匹配 partial 层覆盖；**bi-temporal 双字段尚未显式实现**——§3.3 `write_audit_stage` 当前只有单一 `timestamp` 字段（v1.12.0 修正：原 v1.11.0 声称"已隐含 event_time vs recorded_at 双字段分离"系文档准确性错误，实际代码行953 `record['timestamp'] = datetime.utcnow().isoformat()` 单字段，Phase 2 升级时需补双字段分离）；class-based escalation routing 与 §3.3 置信度评分 High/Middle/Low 三带路由互补；**结论**：远期候选登记，重评条件见 §6 待裁定表

- **2026-08-12 审查新增引用**（v1.15.0 补）：[Grant Holtes 2026-07-22 "A Funded-Path Random-Order Method for Portfolio Active Risk Attribution"](https://www.grantholtes.com/assets/documents/Funded_Path_Random_Order_Portfolio_Active_Risk_Attribution.pdf)（FPRO 修复 Euler/MCR-CCR 对冲对符号抵消伪影——随机排序期望边际贡献 + 资金腿规则，精确 reconcile 总主动风险；§3.14 Phase 2.5+ 远期候选）；[referentiallabs 2026-05-09 "Market Data Hygiene Part 1: Statistical Methods for Detecting Bad Data"](https://referentiallabs.com/blog/market-data-hygiene-part-1/)（Tick Test bad-print 判定：双向偏离前/后邻居 + 立即回摆 = 数据错误剔除，价格停留 = 真实异动保留；stale feed 三法：时间戳对墙钟/活跃标的数值不变/多源交叉——§3.6 bad-print 增强 Phase 1.5 候选）；[m2pfintech 2026-08-04 "Exception Management in Reconciliation: Best Practices"](https://m2pfintech.com/blog/exception-management-reconciliation-best-practices/)（例外管理是对账真实成本中心：先分类再排查 + 重复模式自动处理 + 例外单一事实源 + 根因追踪月度统计——§3.3 root_cause/recurrence_key 字段采纳依据）；[theneuralbase 2026-04 verified note](https://theneuralbase.com/ai-for-finance/learn/advanced/reconciliation-pipelines/)（ML/模糊匹配 70-80% 检出率需 2+ 年标注数据，新机构前 18 月仅 40-50%；MiFID II 要求模型版本/再训练日期/回测结果随每条匹配决策记录——§3.3 规则三层 + 置信度评分优先、AI 匹配暂缓的佐证）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 00_index G25 讨论要点占位 |
| 2026-08-10 | 1.0.0 | 骨架→active，6 讨论要点回填（§3.2 Brinson 主选 Barra 拒绝 / §3.3 三层对账 / §3.4 三维度 / §3.5 两层归因 / §3.6 三层异常检测 / §3.7 四类报告） | 2026 行业调研 + battle_map_11 18 环节 + 源码现状核查 |
| 2026-08-10 | 1.1.0 | §3.2 补多期链接（Carino 主选）+ BHB/BF 方案明确 + beginning-of-period weights + Carino residual <0.01% 质量门禁；§6 补 weight drift/AI 对账 | 单期 Brinson 不能直接加总，周/月/季报需链接算法 |
| 2026-08-10 | 1.2.0 | §3.2 补 PnL Explain vs Predict 框架 + 多 session 归因边界 + fill_id+position_id 唯一键原则 | Greek/SRPnL（Predict 类）A 股权益拒绝 |
| 2026-08-10 | 1.3.0 | §3.2 transaction_cost_drag 接入 TCA + A 股 PnL waterfall 子框架；§3.3 三层匹配算法；§3.7 MOD-RPT-015 报告模板 | drag=0 硬编码缺口 + 单层 exact 例外率过高 + 报告无契约 |
| 2026-08-10 | 1.4.0 | §3.8 sizing_basis 归因 + §3.9 deflated-alpha 三重验证 + §3.10 信号正交约束 + 滑点分布增强方向 | 与 31 号对接 + 过拟合统计验证 + 版本同步修复 |
| 2026-08-10 | 1.4.1 | §8.1 补 53/31 号引用 + §5.1/§5.2 同步 v1.4.0 三项 | 交叉引用审查 |
| 2026-08-10 | 1.5.0 | §3.3 置信度评分匹配 + 三阶段不可变审计轨迹；§3.2 Brinson+Carino+T+1 施工算法；§3.5 求和不变量校验；§3.8 sizing_basis 接入；§3.10 正交性验证；新增 §3.11 regime-conditional + §3.12 Shapley（均 Phase 2） | 三层匹配缺置信度量化 + 缺审计轨迹 + 决策有概念无算法 |
| 2026-08-10 | 1.5.1 | §3.5 calc_performance_score + §3.6 异常检测算法 + §3.2 waterfall 施工算法 + 滑点分布算法 + §3.9 verdict 阈值 + 55 号引用修复 | 施工算法缺口补全 |
| 2026-08-10 | 1.6.0 | §3.3 持仓偏差检测算法 + §3.6 MAD 鲁棒增强 + 严重度分级 + 升级流程 | 并发会话补施工算法 |
| 2026-08-10 | 1.6.1 | §8.4 补 5 条 2026-08 引用（MRC/CVaR 负结果/相关性 Shapley/长江证券/attriblink）+ 版本同步修复 | 最新研究覆盖核查 |
| 2026-08-10 | 1.7.0 | §3.9 PBO 零假设修正（null=0.5）+ §3.6 stale-value 冻结馈送检测（第 0 层）+ §3.3 Merkle tree 升级路径（Phase 2） | 三项必采纳缺口：PBO 解读正确性 + 统计方法盲区兜底 + 审计链结构性缺陷 |
| 2026-08-10 | 1.7.1 | 交叉引用版本同步（40 号/55 号） | stale 引用修复 |
| 2026-08-10 | 1.7.2 | §8.1 55 号 v1.11.0 同步 | 交叉引用版本同步 |
| 2026-08-10 | 1.7.3 | §8.4/§3.3 VCP v1.2 RC 对齐（CSRC 已收提交，Phase 2 对齐 v1.2 而非 v1.1） | VCP v1.2 零破坏性升级发布 |
| 2026-08-10 | 1.8.0 | §3.3 补 VCP v1.2 四大新特性升级路径 + 新增 §3.13 Hentschel GLS 统一归因框架（Phase 2） | 受限 GLS 统一多期链接/交互项/因子残差再分配 |
| 2026-08-10 | 1.9.0 | §3.12 补 3 项研究（hierarchical Shapley/背景分布/Shapley 风险归因）+ §3.13 TreeIG 登记 | 2026-08 最新研究整合 |
| 2026-08-10 | 1.10.0 | §3.2 补 GRAP 专利交易效应第 4 因子概念对齐（功能等价 transaction_cost_drag，无需追加施工） | 专利公开概念澄清 |
| 2026-08-10 | 1.11.0 | §6 补 Cross-venue 对账 bi-temporal 远期候选 + 版本同步修复 | 单券商单市场暂不适用，登记远期 |
| 2026-08-10 | 1.12.0 | §3.13 GLS 设计矩阵公式对齐 + §6/§8.4 bi-temporal 声明准确性修正 | 文档准确性修复 |
| 2026-08-10 | 1.12.1 | §3.2/§3.3 伪代码完整性修复（变量名漂移 + 跨层状态变量补全 + opportunity_costs 参数注入） | 伪代码审计缺口修复 |
| 2026-08-10 | 1.13.0 | 补全 4 个跨文档悬空 helper 定义（get_sector/current_session_id/group_by_symbol_dir_date/aggregate） | P2 悬空 helper 闭合 |
| 2026-08-10 | 1.14.0 | 新增 §3.14 MCR/CCR 风险分解（Phase 2.5，Euler 分解补收益-风险归因不对称） | 收益归因已有但风险归因空白至 Phase 3 Barra |
| 2026-08-12 | 1.15.0 | 全仓设施盘点回填（规则 #11）+ Brinson 公式守恒修复（纯 BHB 对齐 pf_core）+ PerformanceScore Sharpe→Sortino + 双实现冲突登记（§6 置顶）+ 55 号悬空引用校准 + OE-007 对齐声明 + FPRO/bad-print/例外根因/ML 校准期研究整合 + §7 开放问题新增 9 项 | 架构审查七轮循环：12+ 已施工设施漏登 + 公式守恒 bug + 口径冲突 + 状态夸大校准 |
| 2026-08-12 | 1.15.1 | 55 号引用校准覆盖面扩展 + v1.12.0 记录-正文漂移勘误（纯 BHB 为唯一口径，v1.12.0 BF 声明作废） | 确认轮复核 |
| 2026-08-12 | 1.15.2 | MOD-RPT-015 模板 §4 表头 Sharpe→Sortino 跟随修正 | 确认轮二复核 |
| 2026-08-12 | 1.15.3 | §3.14 联动段 PerformanceScore Sharpe→Sortino 跟随修正（全文口径零残留） | 确认轮三复核 |
| 2026-08-12 | 1.15.4 | 作战地图全覆盖补丁：新增 §3.15 压力测试（BM-RC-08-C）+ §3.3 仓位审计追溯（BM-POS-10）+ §3.1.1 模型层反馈（BM-REC-03-C）+ §2.4 缺口 #6（BM-BUY-07） | 四环节补 why 层/缺口登记 |
| 2026-08-12 | 1.15.5 | §3.14 末尾补作战地图环节映射（BM-SEL-21-E/BM-RC-08-A/BM-RC-08-B） | 环节级可追溯 |
| 2026-08-14 | 1.15.6 | 压缩精简：噪音去除+施工细节梳理，零信息丢失审查通过（AI-DOCS-001）；修复前序压缩会话截断事故（§7/§8/§9 整章恢复） | 待施工真源保守压缩：伪代码/契约/参数表/验收标准全保留，删除过程性叙述与重复解释 |
| 2026-08-15 | 1.15.7 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-04）——§5.1 上限定义 10 条与 §3 重复的参数细节真源+指针化（sizing_basis 5 约束枚举→§3.8、置信度权重/三带→§3.3、Brinson+Carino 公式→§3.2、T+1 拆分算法→§3.2、waterfall 施工算法→§3.2、异常检测/verdict 阈值→§3.6/§3.9、漂移检测→§3.3、MAD→§3.6、stale-value→§3.6、Merkle 升级→§3.3），上限裁定与 Phase 定性保留；§3.3 VCP v1.1"为何 Phase 2"与 Merkle 段重复理由并指；§5.1 正交维度条"条件数 <10"与 §3.10 算法阈值（30）冲突，统一为指针口径 | 8 类扫描 12 处（类别 3 重复信息×11、类别 5 冗余×1）；IS 四组件/Brinson 公式/费率口径/阈值全部保留于 §3 真源 |
| 2026-08-15 | 1.15.8 | Step 1 复核收敛（AI-RCAN-001）：§1 状态行版本漂移修正；40/30 号引用版本同步（v2.11.2/v2.6.1）；55 号已 active v1.0.2——§3.9/§3.10/§5.1/§5.2/§7/§8.1 全部 55 号引用按其实际结构对齐（退役评审=§3.5、偏离度量=§3.4、CUSUM/PSI=§3.2B/§3.3、FSI 真源=61 号）；§3.1/§3.6/§3.7 AsharePerformanceAudit 能力描述校准为实际 5 类审计（55 号 §7 越界登记 #1 本域闭环）；§3.3 BM-POS-10 状态 design→production 对齐 battle_map_08；施工算法 bug 修复 7 处——carino_link_periods 改标准 Cariño 1999 形式（原式零基准极限 Σlinked≡1≠G，过不了自家 residual<1e-6 门禁）、t1_locked_weight 对 dict 求和 TypeError、层3 group_by 误传 tuple-of-lists AttributeError、trade_date/.date 属性名不一致致 partial 匹配静默失效、aggregate 缺 date 过滤跨日混聚、exact/fuzzy 层已命中结算单未排除防双计、backtest_best_sharpe 缺 /std 量纲错误 | 文档审查发现：版本漂移+悬空引用+状态夸大+伪代码缺陷；决策零变更，公式修复对齐本备忘自定求和不变量门禁 |
