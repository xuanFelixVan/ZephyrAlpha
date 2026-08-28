---
ttl: permanent
doc_type: architecture_view
title: 合规与交易纪律体系
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.2.0"
date: 2026-08-28
topic: compliance_discipline
scope: 07_trading_decision_architecture
---

> ## 结案报告（2026-08-16 补记）
>
> **实际开发**：两波——①2026-08-15 第 4 批（会话 AI-COMP-001）落码 7 模块（MOD-CMP-001/002/005/007/008/009/010）+78 测试；②同日装配批（AI-ASM-001）完成运行时接线：C-004 四道合规闸嵌入 trading_session、C-002 双硬闸（先报告后交易 + 日申报笔数读数检查）嵌入 order_manager、MOD-PA-006 分批建仓纪律闸、CancelRateGuard v1.1.0 日申报硬计数器（5000 预警/1 万阻断）。
>
> **最终成果**：213 测试两轮全绿；红队三向量真实触发实证（9999 笔放行→1 万笔阻断/清单缺项整批拒/报复命中熔断落盘）；#ARCH-COMPLIANCE-001 按方案 A 闭环（不独立建模块）。
>
> **未做事项及原因**：
> - 47 项功能裁定清单全量迁移未做——源文档不在仓内，待用户补供（遗留 #77）。
> - 对敲/拉抬/洗售（Spoofing/Layering/WashTrade）盘中实时检测~~未做~~——需盘中实时流驱动，属后续批次。**已闭环**（2026-08-28 AI-WAVE3C-001 A8 批，MOD-CMP-018 盘中实时流驱动监测器+C-002 第三道冻结闸，含拉抬打压实时口径，见 §10 盘中实时流驱动记录）。

# 合规与交易纪律体系

> 本备忘是 D_COMPLIANCE 域设计真源，承载作战地图全覆盖审计中裁定"新建统一载体"的 5 个合规环节（BM-BUY-08-A/08-B/09/12/15）。
> 性质：永久态设计记录，可随项目演进而修订，不是不可推翻的裁定。
> 管理规范见 [01_design_memo_management_spec.md](01_design_memo_management_spec.md)。

## 1. 文档定位

### 1.1 本篇管什么

- **交易纪律**（BM-BUY-08-A 四项必做 / BM-BUY-08-B 四项严禁）：操作合规层的"必做清单完成度检测"与"严禁行为拦截"，即 D-COMPLIANCE-23 A-Share Trading Discipline Checker 的完整设计
- **信息合规**（BM-BUY-09）：数据源授权条款合规——登记、使用审计、违规处置
- **硬边界裁定**（BM-BUY-12）：功能二元裁定（能建/禁建）清单与上线门禁流程
- **交易合规检测补强**（BM-BUY-15）：市场操纵 4 类检测规则、程序化交易报告 6 项义务、50μs 订单停留时间锁的适用性裁定

### 1.2 本篇不管什么（与既有备忘的边界）

| 边界对象 | 归谁管 | 本篇只做什么 |
|---|---|---|
| 撤单率 ≤15%、价格笼子、资金预校验 | [40_execution_broker](40_execution_broker.md)（CancelRateGuard / price_cage 已 production） | 引用其产出作合规检测结果，不重复定义 |
| 2026 程序化新规限频（≤15 笔/秒内部安全垫）与令牌桶 | [24_daban_strategy_detail](24_daban_strategy_detail.md) §3.7（ProgramTradingComplianceGuard） | 引用其限频基线，本篇补操纵检测与报告义务 |
| 四项严禁的"命名 + Hard Block/Warning 定位"、限价锚定与追高拦截协同 | [41_buy_flow](41_buy_flow.md) §2.3/§3.1/§3.4/§3.5 | 本篇补检测阈值、算法与 Kill Switch 轻量版联动 |
| 数据资产登记（data_asset_registry） | [62_business_registry_construction](62_business_registry_construction.md)（REG-DATAFLOW-001） | 本篇的授权条款登记表作为其 compliance 字段的展开真源 |
| charter 红线治理（56 条硬边界砍到 10 条真红线） | [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §5 | 那是**系统生存红线**（Fail-Closed 风控阈值）；本篇 BM-BUY-12 是**功能建设权裁定**（能不能建），两者不同物，§6 消歧 |
| 内幕交易隔离墙 / AML / KYC | BM-BUY-11 已 deprecated | 本篇不建设（个人自有资金，无客户资产与多团队隔离场景） |

### 1.3 约束条件

- **个人 + 100% AI 开发、自有资金、miniQMT 单通道**：合规设计对标"个人程序化交易者"义务线，不照搬机构合规体系（无通信监控、无信息隔离墙、无 AML）
- **Fail-Closed 铁律**：合规检测失效时的降级方向一律是"更保守"（拒单/暂缓），绝不 fail-open
- **纪律辅助非阻断**（仅 BM-BUY-08-A 的必做清单）：必做清单是纪律辅助，超时只 Warning 不阻交易，盘中执行合规检查除外（Hard Block）

## 2. 环节映射总表

| BM 环节 | 名称 | 设计态 | 本篇章节 | 裁定状态 |
|---|---|---|---|---|
| BM-BUY-08-A | 四项必做清单自动化检测 | design | §3 | **建设**（MVP 轻量检查器，4 时点 cron + 完成度信号） |
| BM-BUY-08-B | 四项严禁自动化检测 | design | §4 | **建设**（补阈值+检测算法+Kill Switch 轻量版联动，41 号基座之上） |
| BM-BUY-09 | 信息合规 | production 态但 why 空白 | §5 | **建设**（重定义为数据源授权条款合规；内幕隔离墙不建设） |
| BM-BUY-12 | 硬边界裁定 | design | §6 | **建设**（47 项功能裁定清单结构 + 上线门禁流程） |
| BM-BUY-15 | 交易合规检测 | design（补强） | §7 | **建设**（补操纵 4 类检测 + 报告 6 项义务；50μs 时间锁裁定**不适用于个人低频**，降为记录性参数） |

## 3. BM-BUY-08-A 四项必做清单自动化检测

### 3.1 定位

交易日 4 个关键时点（盘前/盘中/盘后/晚间）自动检测四项必做清单完成度，是操作合规的"自律层"——防"AI 全自动跑、人不复盘"的纪律衰减。源定义：`合规架构.md §12.2.1`。

### 3.2 裁定

**建设（MVP 轻量检查器）**。理由：4 时点清单是纯工作流信号检测，无复杂算法，一次性建成即可长期运行；steps JSON 明确"必做是纪律辅助非阻断（盘中执行除外）"，建设成本与风险都低。不建设单独的"合规数据库"——检测结果落 `compliance_log`（结构化 JSONL）即可，达 3-5 个同类 artifact 再议生成器（01 号规范 §6）。

### 3.3 契约 / 参数 / 接口

**四时点清单定义**（默认值取 steps JSON indicators，deadline 为本篇裁定值）：

| 时点 | 必做内容 | 截止/检测时机 | 未完成动作 |
|---|---|---|---|
| 盘前复核 | 前日复盘摘要 + 今日计划 + 风险检查清单 | 08:00 前完成；08:00 检测 | 超时 → Warning 推送 |
| 盘中执行 | 策略信号合规检查 + 风控参数确认 + 仓位限额验证 | 实时（C-004 嵌入，订单提交前） | 违规 → **Hard Block**（四时点中唯一阻断项） |
| 盘后复盘 | 当日决策回顾 + 偏差分析 + 纪律自评 | 收盘后至次日开盘前 | 未完成 → 次日开盘前 Warning |
| 晚间分析 | 收盘数据归档 + 明日策略 + 风险预判 | 当晚至次日盘前 | 未完成 → 次日盘前 Warning |

**接口**：

```python
class ChecklistCompletionChecker:  # D-COMPLIANCE-23 组件 A
    def check_checkpoint(self, checkpoint: str, now: datetime) -> ChecklistVerdict:
        """checkpoint ∈ {PRE_MARKET, INTRADAY, POST_MARKET, EVENING}
        返回 ChecklistVerdict(checkpoint, complete: bool, missing_items: list[str],
                              action: WARNING | HARD_BLOCK, checked_at)
        完成度信号来源：复盘报告生成状态 / 分析任务提交状态 / C-004 风控参数确认位"""
```

- `WARNING`：推送 + 落 compliance_log，不影响交易执行
- `HARD_BLOCK`（仅盘中执行）：联动 C-004 拒绝订单，与 BM-BUY-08-B 共用阻断通道
- **降级**：检测失效 → 降级人工 checklist（paper 模式），不阻断交易（盘中执行项除外，失效时按 Fail-Closed 拒单）

**参数默认值**：`pre_market_deadline="08:00"`；`post_market_deadline="次日09:15"`；`evening_deadline="次日08:00"`；复盘/分析完成信号 = 对应工作流 artifact 存在且日期 = 当日。

### 3.4 与既有模块关系

- 盘中执行项嵌入 C-004 实时风控参数确认，与 [40 号](40_execution_broker.md) 决策⑭资金预校验同通道（Pre-Trade 拦截链一环）
- 复盘/晚间分析完成信号消费工作流 artifact 存在性，不侵入复盘/分析模块内部逻辑

## 4. BM-BUY-08-B 四项严禁自动化检测

### 4.1 定位

订单提交前 + 盘中实时检测四类严禁交易行为——踏空追高 / 被套补仓 / 盈利骄傲 / 亏损报复，触发即按等级处置。源定义：`合规架构.md §12.2.2`。[41 号](41_buy_flow.md) §2.3/§3.1 已定"四类命名 + Hard Block 拦截 / Warning 推送"定位，§3.4/§3.5 已有限价锚定与追高拦截协同；本篇补：检测阈值 + 检测算法 + Kill Switch 轻量版联动。

### 4.2 裁定

**建设**。理由：四类行为是个人交易者亏损的主要行为来源，41 号已立"买入下单前必过纪律闸、不得绕过"的硬约束，阈值与算法不补全则纪律闸是空壳。检测引擎失效 → 保守 Hard Block 拒绝订单（Fail-Closed，安全失败）。

### 4.3 契约 / 参数 / 接口

**检测阈值**（默认值：steps JSON 有建议值的取建议值，无建议值的给 MVP 初始值并标注待校准）：

| 行为 | 检测条件 | 阈值默认值 | 处置 |
|---|---|---|---|
| 踏空追高 | 买入价相对信号参考价（信号生成时价格）追涨幅度超阈值，且发生在急剧拉升后（近 30 分钟涨幅 > 5%） | `chase_max_deviation=+2%`（MVP 初始值，待 C1 实盘校准）；`surge_window=30min`、`surge_threshold=+5%` | **Hard Block** 拒绝追高 |
| 被套补仓 | 持仓亏损 > X% 后继续加仓同一标的 | `add_on_loss_threshold=-5%`（steps JSON 建议值） | **Hard Block** 拒绝补仓 |
| 盈利骄傲 | 连续盈利 N 笔后，单笔风险敞口超常规倍数 | `win_streak_n=5`（MVP 初始值，待校准）；`risk_exposure_multiplier=1.5` | **Warning** 推送提醒（不阻断） |
| 亏损报复 | 当日亏损 > Y% 后，交易频率或单笔规模异常增加 | `revenge_loss_threshold=-2%`（steps JSON 建议值）；`freq_multiplier=2.0`（相对 20 日均值）、`size_multiplier=1.5` | **Hard Block** + **Kill Switch 轻量版**（仅停该策略，非全局） |

**检测算法**（施工伪代码）：

```python
class DisciplineGuard:  # D-COMPLIANCE-23 组件 B，嵌入 C-004 风控引擎
    def check(self, order, ctx: DisciplineContext) -> DisciplineVerdict:
        """订单提交前调用；返回 DisciplineVerdict(behavior, action, detail)
        ctx 携带：信号参考价 / 3秒Tick价 / 持仓盈亏 / 同标的加仓记录 /
                  连续盈亏笔数 / 当日盈亏 / 20日交易频率与单笔规模基线"""
        # 1) 追高：deviation = order.price / ctx.signal_ref_price - 1
        #    deviation > 2% and ctx.surge_30min > 5% → HARD_BLOCK("CHASING")
        # 2) 补仓：ctx.position_pnl_pct < -5% and order 加仓同标的
        #    → HARD_BLOCK("ADDING_TO_LOSER")
        # 3) 骄傲：ctx.win_streak >= 5 and order.risk_exposure > 1.5 * ctx.normal_exposure
        #    → WARNING("OVERCONFIDENCE")（推送，不阻断）
        # 4) 报复：ctx.daily_pnl_pct < -2% and (freq > 2x 基线 or size > 1.5x 基线)
        #    → HARD_BLOCK("REVENGE_TRADING") + KillSwitchLite.trigger(strategy_id)
```

**Kill Switch 轻量版（KillSwitchLite）**：

- 作用域：**仅触发策略**（strategy_id 级），当日禁止该策略新开仓，不影响其他策略与已有持仓
- 接口：`KillSwitchLite.trigger(strategy_id, reason, expiry="当日收盘")`；状态存 compliance_log
- 与全局 Kill Switch 关系：轻量版是策略级降级手段；**轻量版失效 → 升级全局 Kill Switch**（RC-03，[35 号](35_drawdown_protocol_impl.md) 四级梯子），不与之冲突
- 解除：次日自动复位 + 人工确认当日违规已复盘

**降级**：检测引擎失效 → 保守 Hard Block 拒绝订单（宁可不交易）；Kill Switch 轻量版失效 → 升级全局 Kill Switch（RC-03）。

### 4.4 与既有模块关系

- 41 号 §3.5 限价锚定是"事前预防"（挂略低于压力位防追高），本篇追高检测是"事后拦截"（限价仍超阈值则拒单），两层互补
- 与 41 号 §3.3 降级表衔接：纪律闸拦截（追高/补仓）→ 取消后续批次 + 记录违规
- 检测结果统一落 compliance_log，供 §3 盘后复盘的"纪律自评"消费

## 5. BM-BUY-09 信息合规

### 5.1 定位

作战地图 panorama 定义：**管数据源使用条款合规**——确保行情/另类数据来源与使用符合供应商授权条款。注意与 steps JSON 原始 params（"内幕交易深度防护、通信监控、信息隔离墙"）的偏差：那是机构合规模板，BM-BUY-11（AML/KYC/隔离墙族）已 deprecated，本篇按 panorama 定义落地为**数据源授权合规**。

### 5.2 裁定

- **建设**：数据源授权条款登记表 + 使用审计 + 违规处置。理由：系统已接入多路行情/另类数据（Level-2、龙虎榜、新闻舆情等），授权条款（仅个人使用/禁止再分发/衍生数据政策/商用限制）是真实法律义务，登记成本极低、违规代价高
- **不建设**：内幕交易隔离墙、通信监控。理由：个人自有资金、单人决策，无多团队信息隔离场景；重评条件——引入外部资金或多人协作时重评

### 5.3 契约 / 参数 / 接口

**① 数据源授权条款登记表**（作为 [62 号](62_business_registry_construction.md) `catalogs/data_asset_registry.yaml`（REG-DATAFLOW-001）compliance 字段的展开真源，每个数据源 entry 必填）：

```yaml
# data_asset_registry.yaml 每个 source entry 的 compliance 段
compliance:
  vendor: str                 # 供应商（如 迅投/同花顺/Tushare/交易所）
  license_type: enum          # personal / professional / redistribution / trial
  permitted_use: list[str]    # 允许用途（backtest / live_trading / display / ml_training）
  redistribution: bool        # 是否允许再分发（默认 false）
  derived_data_policy: str    # 衍生数据政策（如"因子可自用不可发布"）
  expiry: date | null         # 授权到期日（订阅制必填）
  terms_ref: str              # 条款原文存档路径/URL
  registered_at: date         # 登记日期
  review_cycle_days: int      # 复核周期，默认 90
```

**② 使用审计**：`LicenseUsageAuditor.audit(source_id) -> AuditReport`——核对实际使用方式（消费该源的模块清单，由 depgraph path 反查）是否 ∈ permitted_use；每 `review_cycle_days` 天定期跑 + 新增数据消费模块时触发。输出落 compliance_log。

**③ 违规处置流程**：

| 违规级别 | 例子 | 处置 |
|---|---|---|
| L1 超范围使用 | trial 源用于 live_trading | 切断该用途数据流 + Warning + 限期整改（升级授权或下线用途） |
| L2 授权过期 | expiry 已过仍消费 | 立即切断数据流（Fail-Closed）+ 告警 |
| L3 再分发违规 | 衍生因子对外发布 | 人工处置 + 条款复核 + 功能下线评估（联动 §6 门禁） |

**降级**：登记表缺失某源 compliance 段 → 该源默认**仅 backtest 用途**（最保守假设），直至补登。

### 5.4 与既有模块关系

- 62 号 REG-DATAFLOW-001 是登记容器与治理流程真源；本篇定 compliance 段的**字段语义与处置动作**，62 号施工时按此展开
- BM-BUY-15 的报告义务（§7.4）若涉及数据源信息（交易软件信息项），从本登记表取数

## 6. BM-BUY-12 硬边界裁定

### 6.1 定位与消歧

47 项功能二元裁定（能建/禁建）+ 上线门禁流程。源定义：`合规架构.md §10`。

**消歧**：[30 号](30_multi_strategy_concurrency.md) §5"56 条硬边界砍到 10 条真红线"是 **charter 系统生存红线治理**（Fail-Closed 风控阈值，运行时强制）；本篇 BM-BUY-12 是**功能建设权裁定**（某功能能不能建、能不能上线，设计/上线时门禁）。两者对象不同、时机不同、强制层不同，互不替代。

### 6.2 裁定

**建设**。理由：47 项功能裁定是 steps JSON 已锁定的既有裁定资产，当前无登记载体，散落则必然漂移；门禁流程是纯登记+校验，成本低。裁定清单用 YAML 登记表承载（D_COMPLIANCE 域），不建独立数据库。

### 6.3 契约 / 参数 / 接口

**① 功能裁定清单结构**（`catalogs/feature_adjudication_registry.yaml`，47 项初始由 steps JSON/合规架构.md §10 迁移录入）：

```yaml
- feature: str              # 功能名（如 "裸期权卖方"/"T+0 变相回转"/"跨账户对倒工具"）
  verdict: enum             # BUILDABLE / FORBIDDEN
  reason: str               # 裁定理由（法规条款/风险论证）
  adjudicated_at: date      # 裁定日期
  re_review_condition: str  # 重评条件（如 "T+0 试点放开" / "AUM > 500万"）
  related_bm: str | null    # 关联作战地图环节（如有）
```

裁定原则（登记时必须逐条过）：①法律法规明令禁止 → FORBIDDEN 无例外；②通道/资金属性不支持（T+1、不能做空、无两融）→ FORBIDDEN，重评条件 = 通道变更；③个人系统复杂度不承受 → FORBIDDEN 或降级，重评条件 = 团队/AUM 变化。

**② 新功能上线门禁流程**（提案 → 裁定 → 登记 → 门禁校验）：

1. **提案**：新功能设计规格（功能名/数据源/订单行为/合规触点）随设计备忘提交
2. **裁定**：对照裁定原则逐项过，输出 verdict + reason + re_review_condition
3. **登记**：写入 feature_adjudication_registry.yaml
4. **门禁校验**：`FeatureGate.check(feature_name) -> PASS | BLOCK`——apply_depgraph.py 登记设计态模块时调用；未登记 → `PENDING` 视同 BLOCK（裁定未决 → 暂缓上线，安全优先，与 steps JSON degradation 一致）；FORBIDDEN → BLOCK 并提示重评条件

**降级**：裁定未决 → 暂缓功能上线（安全优先）；登记表不可读 → Fail-Closed，一切新功能门禁 BLOCK。

### 6.4 与既有模块关系

- 门禁校验挂 depgraph 登记环节（01 号规范 §2.2 第 2 步），不新增独立审批流程——单人+AI 顺序执行，与 01 号"自然工作流非审批流程"一致
- 30 号 §5 的 10 条真红线运行时在 C-004 强制；本篇 FORBIDDEN 功能在登记时拦截，两道闸互为补充

## 7. BM-BUY-15 交易合规检测（补强）

### 7.1 定位

合规检测层：异常交易行为 + 市场操纵 + 速率约束 + 程序化交易报告。区别于 BM-BUY-08-B（行为纪律，管"人"），本环节管"法"——监管规则符合性。已有基座：[24 号](24_daban_strategy_detail.md) §3.7（高频认定 300 笔/秒或 2 万笔/日、内部限频 ≤15 笔/秒 + 撤单率 ≤15%、ProgramTradingComplianceGuard 令牌桶）+ [40 号](40_execution_broker.md) 已闭合撤单率/价格笼子。本篇补：市场操纵 4 类检测规则、程序化交易报告 6 项义务、50μs 订单停留时间锁适用性裁定。

### 7.2 裁定总览

| 子项 | 裁定 | 一句话理由 |
|---|---|---|
| 4 类异常交易行为阈值（瞬时申报速率/撤单率/拉抬打压/大额成交） | **建设**，嵌入 C-004 | steps JSON 已给阈值，40 号已闭合撤单率与速率，补拉抬打压与大额成交两条检测即可 |
| 市场操纵 4 类检测（Spoofing/Layering/Wash Trade/尾盘操纵） | **建设**（检测+自证清白导向，非高频对冲导向） | 个人低频系统天然低触发，但需检测器自证"未实施操纵"+ 防误伤（撤单模式被误认定） |
| 程序化交易报告 6 项义务 | **建设**（登记+报送日历，人工报送） | 先报告后交易是铁律，未报告 C-002 拒绝订单 |
| 50μs 订单停留时间锁 | **不适用**（个人低频），降为记录性参数 | 见 §7.5 适用性裁定 |

### 7.3 市场操纵 4 类检测规则

检测目标：**自我监控 + 证据留存**（监管问询时可自证），检测器嵌入 C-004，输出落 compliance_log 并 T+1 归档。

| 类型 | 检测规则 | 阈值默认值 | 处置 |
|---|---|---|---|
| Spoofing 幌骗 | 大额挂单（> 该标的分钟均量 20%）后 10 秒内撤单，且挂单价远离成交 intent（同 pattern 30 分钟内 ≥3 次） | `spoof_size_ratio=0.2`、`spoof_cancel_window=10s`、`spoof_repeat=3` | Hard Block 撤单指令 + 告警 |
| Layering 分层 | 同侧连续挂 ≥3 档价格梯度单且总撤单率 > 80%（该序列内） | `layer_min_levels=3`、`layer_cancel_ratio=0.8` | Hard Block + 告警 |
| Wash Trade 对倒 | 同一实控人关联账户间成交（含自买自卖）；本系统单账户 → 检测自成交撮合结果与关联账户标记 | `wash_self_trade=零容忍` | Hard Block + 立即人工复核 |
| 尾盘操纵 | 14:57-15:00 收盘集合竞价段大额拉抬/打压（申报价偏离收盘前 VWAP > 2% 且量占比 > 30%） | `close_deviation=2%`、`close_volume_share=30%` | Hard Block + 告警（与 41 号尾盘执行窗口错峰约束联动） |

> **为何个人低频也要建**：2026 穿透监管按实控人合并计算，且撤单模式（正常改单）可能被交易所监控误认定——检测器同时是"自证清白"的证据链生成器。本项目内部撤单率 ≤15% 远低于官方 50% 监控线（40 号 §2.13，中基协 2026-07 确认），误认定概率低，但证据链必须有。

### 7.4 程序化交易报告 6 项义务

**铁律：先报告后交易**——报告未完成确认前，C-002 执行域拒绝发送任何订单（steps JSON degradation 原样承继）。

| # | 报告项 | 内容真源 | 报送时机 |
|---|---|---|---|
| 1 | 账户基本信息 | 券商账户档案 | 首次交易前 |
| 2 | 交易软件信息 | miniQMT 客户端标识 + 自研系统说明 | 首次交易前 / 变更时 |
| 3 | 策略类型（6 大类） | 策略登记（打板/多因子/事件驱动等归类） | 首次交易前 / 新增策略时 |
| 4 | 最高申报速率 | miniQMT 通道上限 10 笔/秒（steps JSON）；内部限频 ≤15 笔/秒（24 号 §3.7）取通道值 10 笔/秒填报 | 首次交易前 / 变更时 |
| 5 | 单日最高申报笔数 | 按容量测算填报（MVP 初始值 2000 笔/日，待实盘校准） | 首次交易前 / 变更时 |
| 6 | 重大变更 | 上述任一项变化 | **T+1 报送** |

**接口**：`ComplianceReportRegistry`（YAML 登记 6 项内容 + `reported_at` + `broker_ack` 确认位）+ `ReportGate.check() -> PASS | BLOCK`：任一必报项 `broker_ack` 缺失 → C-002 拒单。报送动作本身为人工（券商渠道），系统管"登记、确认位、门禁"。

### 7.5 50μs 订单停留时间锁适用性裁定

**裁定：不适用（个人低频交易），降为记录性参数**。

- **理由**：①50μs 停留锁针对高频做市/幌骗场景（限制挂单后瞬时撤单）；本项目内部限频 ≤15 笔/秒、撤单率 ≤15%、主动撤单按场景触发且挂单默认等待 30s（40 号决策⑫/⑬），订单实际停留时间是毫秒级锁的 6 个数量级以上；②miniQMT 个人通道物理延迟（广域网 1.2-2ms，62 号 latency_profile）使 50μs 级控制在本架构无实现意义
- **处置**：C-002 不实现 50μs 时间锁；在 ComplianceReportRegistry 登记 `order_min_dwell_us: 50`（标注"监管参考值，本系统天然满足"）
- **重评条件**：策略演进至秒级以内高频（报单速率 > 50 笔/秒）或监管将停留锁明确适用于全部程序化账户时，重评为"建设"

### 7.6 降级与既有模块关系

- 检测引擎失效 → Hard Block 拒绝发送任何订单（Fail-Closed，宁可不交易不可违规）
- 速率约束真源在 24 号 §3.7（令牌桶 + 限频），撤单率/价格笼子真源在 40 号；本篇检测器消费其计数器，不重复实现
- 数据流末端：合规数据库（compliance_log MVP）→ T+1 监管报送 → 审计证据链

## 8. 开放问题

| 问题 | 现状 | 决策状态 |
|---|---|---|
| 追高检测 `chase_max_deviation=+2%`、骄傲检测 `win_streak_n=5` 等 MVP 初始阈值 | 本篇给初始值，未经实盘校准 | 待 C1 实盘阶段按误拦截率校准 |
| 47 项功能裁定清单的迁移录入 | 登记表结构本篇已定；源清单（合规架构.md §10 / 17-D-COMPLIANCE-合规监管域.md）不在仓内不可用 | **部分落地**（v1.0.0）：19 条有据种子已登记（harvest 档案 15 条 ✅/❌ + 本篇明示 4 条）；全量 47 项迁移待源文档恢复后补录 |
| #ARCH-COMPLIANCE-001（5000 笔预警/1 万笔阻断/撤单率 80%/存档 20 年，program_trading_regulation.py） | **已裁定吸收（2026-08-15 用户拍板方案 A）**：不独立建模块——撤单率 80% 被 40 号内部 ≤15% 覆盖；存档维持 JSONL MVP 裁定；唯一缺口=日申报笔数硬计数器（5000 预警/1 万阻断） | **已闭环**：计数器已施工（2026-08-15 AI-ASM-001，CancelRateGuard v1.1.0 日申报硬计数器，报单+撤单双计+自然日滚动，C-002 order_manager 读数检查）；ARCH 条目转 decided |
| compliance_log 载体 | MVP 用 JSONL 文件；达 3-5 个同类 artifact 后是否建生成器/数据库 | 按 01 号规范 §6 暂缓，不预设 |
| 单日最高申报笔数填报值 2000 笔/日 | 按打板+多因子容量粗估 | 待实盘首月统计校准 |
| 报告义务券商侧确认流程（broker_ack 获取方式） | miniQMT/券商程序化报备通道细则未在库 | 待开通实盘时人工核实后补录 |

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-12 | 0.1.0 | 新建——作战地图全覆盖补丁，承载 BM-BUY-08-A/08-B/09/12/15 五环节设计真源（08-A 四时点必做清单检查器 / 08-B 四项严禁阈值+算法+KillSwitchLite / 09 数据源授权合规三级 / 12 功能裁定清单+上线门禁（与 30 号 charter 红线消歧）/ 15 操纵 4 类检测+报告 6 项义务+50μs 不适用裁定） | 作战地图 339 环节全覆盖审计发现合规域 5 环节无设计载体，经用户裁定新建本篇统一承载，作 D_COMPLIANCE 域设计真源 |
| 2026-08-15 | 0.1.1 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-05） | 首轮未压缩篇目：§9 新建条目改动单元格去正文重复（五环节细节以正文 §3-§7 为准）；全篇扫描无其他可压缩点——追高 +2%/30min+5%、补仓 -5%、骄傲 5 笔×1.5、报复 -2%/2.0/1.5、Spoofing 0.2/10s/3、Layering 3 档/0.8、尾盘 2%/30%、50μs、限频 ≤15 笔/秒+通道 10 笔/秒+2000 笔/日、撤单率 12%/15%、47 项裁定清单、BM-BUY 锚点/开放问题/链接逐项零丢失 |
| 2026-08-15 | 1.0.0 | **已施工**（AI-COMP-001，第 4 批）：五环节全落地，draft→active | §3-§7 全模块落码（7 模块+2 登记表+78 测试全绿），详见 §10 施工落地记录；depgraph 4 预登记设计态节点落码+3 新登记+10 设计态边 |
| 2026-08-15 | 1.0.1 | #ARCH-COMPLIANCE-001 裁定吸收（用户拍板方案 A） | §8 开放问题闭环：不独立建 program_trading_regulation.py；日申报笔数硬计数器（5000 预警/1 万阻断）并入 tracker #74 装配批 |
| 2026-08-15 | 1.1.0 | **运行时装配完工**（AI-ASM-001，tracker #78） | §10 新增装配记录：C-004 四道合规闸（清单/熔断/纪律/操纵检测）+C-002 双硬闸（ReportGate/日申报笔数）+MOD-PA-006 gate_batch_order+CancelRateGuard v1.1.0 硬计数器；§8 #ARCH-COMPLIANCE-001 转已闭环；红队三向量实证 |
| 2026-08-28 | 1.2.0 | **盘中实时流驱动完工**（AI-WAVE3C-001，A8 批） | §10 新增盘中实时流驱动记录：MOD-CMP-018 manipulation_realtime_monitor（委托/成交事件流挂接+tick 流分钟均量/短窗供给+4 类检测+告警冻结分发）+C-002 第三道闸（操纵冻结抛转）；结案报告"盘中实时检测未做"残余闭环；31 新用例+1503 两轮全绿 |

## 10. 施工落地记录

**已施工**（2026-08-15，AI-COMP-001，#ARCH-COMP-001）：

| 环节 | 模块 | 路径 | 测试 |
|---|---|---|---|
| §3 必做清单 | MOD-CMP-001 ChecklistCompletionChecker | [src/zephyr/compliance/discipline_must_do_checker.py](../../../../src/zephyr/compliance/discipline_must_do_checker.py) | 11 |
| §4 四项严禁+熔断 | MOD-CMP-002 DisciplineGuard + KillSwitchLite | [src/zephyr/compliance/discipline_prohibition_checker.py](../../../../src/zephyr/compliance/discipline_prohibition_checker.py) | 18 |
| §5 授权审计 | MOD-CMP-008 LicenseUsageAuditor | [src/zephyr/compliance/license_usage_auditor.py](../../../../src/zephyr/compliance/license_usage_auditor.py) | 11 |
| §6 功能门禁 | MOD-CMP-005 FeatureGate + [feature_adjudication_registry.yaml](../../../01_policies_and_standards/_registry/catalogs/feature_adjudication_registry.yaml)（REG-FEATURE-ADJ-001，19 条种子） | [src/zephyr/compliance/hard_boundary_adjudicator.py](../../../../src/zephyr/compliance/hard_boundary_adjudicator.py) | 8 |
| §7 交易合规检测 | MOD-CMP-007 TradingComplianceDetector（异常 2 + 操纵 4） | [src/zephyr/compliance/trading_compliance_detector.py](../../../../src/zephyr/compliance/trading_compliance_detector.py) | 17 |
| §7.4 报告门禁 | MOD-CMP-009 ReportGate + [compliance_report_registry.yaml](../../../01_policies_and_standards/_registry/catalogs/compliance_report_registry.yaml)（REG-CMP-REPORT-001，6 项义务+50μs 记录性参数） | [src/zephyr/compliance/compliance_report_registry.py](../../../../src/zephyr/compliance/compliance_report_registry.py) | 7 |
| 落库载体 | MOD-CMP-010 ComplianceLogger（JSONL append-only） | [src/zephyr/compliance/compliance_log.py](../../../../src/zephyr/compliance/compliance_log.py) | 6 |

- 蓝图：`docs/03_modules/_domain_compliance/{模块名}/blueprint.md` ×7
- 工程修正（对伪代码）：①严禁检测加 ε=1e-9 浮点尾差容差（恰达阈值不判违规，与"超阈值"语义一致）；②必做清单盘后/晚间截止按"次日+trade_date 显式入参"实现跨日语义
- 整合点（设计态边已登记，dep_maturity=design）：C-004 风控引擎→MOD-CMP-002/007；MOD-PA-006 分批建仓→MOD-CMP-002；C-002 执行域（order_manager）→MOD-CMP-009。运行时装配（实际调用点嵌入）留后续装配批
- merge 后 depgraph 经 #ARCH-70 同身份 UPDATE 通道自动转 production

**运行时装配**（2026-08-15，AI-ASM-001，tracker #78 + #ARCH-COMPLIANCE-001 方案 A 计数器）：

| 嵌入点 | 接线内容 | 落点 | 语义 |
|---|---|---|---|
| C-004 风控引擎（40 号 Pre-Trade 拦截链） | MOD-CMP-001 INTRADAY 必做清单（整批 Hard Block）+ KillSwitchLite 熔断 + MOD-CMP-002 四项严禁 + MOD-CMP-007 逐单检测（大额成交/拉抬打压/尾盘操纵，ctx 缺省跳过） | [trading_session.py](../../../../src/zephyr/ex_core/trading_session.py) `_validate_and_submit`（风控检查后、撤单率检查前） | 可选注入、检测失效 Fail-Closed 拒单、成对注入装配期 fail-fast |
| C-002 执行域 | MOD-CMP-009 ReportGate 先报告后交易 + 日申报笔数读数检查（5000 预警/1 万阻断） | [order_manager.py](../../../../src/zephyr/ex_core/order_manager.py) `submit_order` 前置 `_check_compliance_gates`（状态机+broker 发送前） | BLOCK → ComplianceGateBlockError（ZA-EX-0011） |
| MOD-PA-006 分批建仓 | MOD-CMP-002 每批下单前过闸（41 §2.3 不得绕过） | [batched_position_builder.py](../../../../src/zephyr/pf_alloc/batched_position_builder.py) `gate_batch_order` | 闸未注入 → DisciplineGuardError（Fail-Closed） |
| 日申报笔数硬计数器 | 报单+撤单双计、自然日滚动、5000 预警/1 万阻断、阈值穿越单次告警 | [cancel_rate_guard.py](../../../../src/zephyr/ex_core/cancel_rate_guard.py) v1.1.0（复用 40 号决策⑫既有事件流，不重复实现） | C-002 读数检查消费 |

- 红队实证（tests/compliance/test_runtime_wiring.py）：①9999 笔放行→1 万整 C-002 拒发+broker_ack 缺失拒发；②清单缺项整批 Hard Block、补全恢复；③报复命中 HARD_BLOCK+熔断落盘，C-004 与 MOD-PA-006 跨链同策略均拦，合规日志留痕
- 测试：213 项（ex_core 3 文件+pf_alloc+compliance 含红队 4 项）连续 2 轮全绿
- 边界：Spoofing/Layering/WashTrade 需订单/成交历史，由盘中实时流以同一 detector 实例驱动，不在 Pre-Trade 链范围；MOD-CMP-005/008 为治理/审计面不参与运行时拦截

**盘中实时流驱动**（2026-08-28，AI-WAVE3C-001，A8 批——结案报告"盘中实时检测未做"残余闭环）：

| 嵌入点 | 接线内容 | 落点 | 语义 |
|---|---|---|---|
| 委托/成交事件流（C-002 执行域） | MOD-CMP-018 ManipulationRealtimeMonitor attach 挂接：订单事件回调（报单 SUBMITTED/撤单 CANCELLED 发射）+ 既有 fill 回调链 | [order_manager.py](../../../../src/zephyr/ex_core/order_manager.py) `register_order_event_callback`/`_emit_order_event`（submit 券商确认后/cancel 终态后发射，回调异常隔离） | 被动观察，不接任何下单/撤单执行路径 |
| tick 行情流（tick_subscriber CP-01 通道） | RedisTickMarketProvider 懒读 Redis tick 缓存：分钟均量=累计量/已交易分钟（Spoofing 前提）+ 5min 滚动观测窗价变/量差（拉抬打压前提） | [manipulation_realtime_monitor.py](../../../../src/zephyr/compliance/manipulation_realtime_monitor.py)（事件时刻拉取，零定时器；缺数据降级跳过防误伤） | tick key/符号归一走 SSoT（tick_latest_key/normalize_symbol） |
| 检出→告警/阻断 | 命中一律 logging 告警 + compliance_log（MANIPULATION_REALTIME_ALERT；逐命中 MANIPULATION_VERDICT 归 detector 唯一真源）+ 冻结标的判定 | C-002 `_check_compliance_gates` 第三道闸：is_frozen 命中 → ComplianceGateBlockError 拒发新申报（既有闸抛转，不新建执行通道）；监测失效 Fail-Closed（§7.6） | 冻结须人工复核 release_freeze 释放（MANIPULATION_FREEZE_RELEASE 留痕） |

- 4 类检测口径：Spoofing/Layering/WashTrade（§7.3 经 ManipulationStreamDriver 同一 detector 实例）+ 拉抬打压（§7.2 短窗价变+我方成交占比，事件驱动懒评估）；尾盘操纵/大额成交维持 C-004 Pre-Trade 链覆盖不重复
- 测试：31 新用例（4 类检测正常/边界/异常 + 实时流接入隔离 + 集成冒烟模拟流）；compliance+ex_core 1503 项连续 2 轮全绿零回归
- 治理：MOD-CMP-018 depgraph 节点登记（只登记不流转）+ capability creation_tokens + module_translation 中文名
- 边界重述：本批=检测/告警/阻断判定逻辑；执行动作走既有合规闸抛转（ComplianceGateBlockError），未新建执行通道

---

**关联文档指针**：[41_buy_flow](41_buy_flow.md)（四项严禁命名与拦截定位、限价锚定协同）｜[40_execution_broker](40_execution_broker.md)（撤单率/价格笼子/Pre-Trade 拦截链）｜[24_daban_strategy_detail](24_daban_strategy_detail.md) §3.7（程序化新规限频与令牌桶）｜[62_business_registry_construction](62_business_registry_construction.md)（data_asset_registry 登记容器）｜[30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §5（charter 红线治理，与本篇 §6 消歧）
