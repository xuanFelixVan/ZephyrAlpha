---
ttl: task_bound
title: 深度审查报告——三流对账+日终对账（R03）
owner: st-deeprev-20260918
created: 2026-09-18
reviewer: GLM-5.3-Flash/st-deeprev-20260918
baseline_commit: 2fa92002c3
---

# 深度审查报告：三流对账+日终对账（R03）

- 状态: **已审**
- 级别: P0｜类型: 管线
- 基线 commit: 2fa92002c3
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/trading/three_way_reconciliation.py:175` + `src/zephyr/ex_core/eod_reconciliation.py:95`
- 生产调用方: **两者均零生产接线**（grep 实录，详见 C 轴）——作业簿预填"EodReconciler 消费 ThreeWay/PostSettlement 链"与事实不符：EodReconciler 与 ThreeWayReconEngine 互不调用，也无第三方装配
- 测试文件: tests/trading/test_three_way_reconciliation.py（25 用例）+ tests/ex_core/test_eod_reconciliation.py（9 用例，315 行）——全绿（2026-09-18 实录）

## 1 对象快照

- **范围**：ThreeWayReconEngine 全文（交易/持仓/资金三方流水收口+异常台账状态机）+ EodReconciler 全文（账户级日终对账：持仓委托/资金/订单归档/T+1 对齐）。
- **查重分工核对**：两文件头部互声明分工（three_way=流水级含费用逐笔，eod=账户级；settlement=逐笔 Fill）——声明本身自洽，且 eod 确实委托 ex_core PositionReconciler 不重复实现（eod_reconciliation.py:47,173，正面）。但与 settlement_reconciliation 的费用口径交叠见 R04 簿。
- **测试覆盖概况**：three_way 25 用例覆盖校验/配对/台账状态机/幂等；eod 9 用例覆盖 fail-closed 分支/资金核对/对齐开关。均通过。
- **材料包缺项声明**：同 R01；两模块均无生产运行时证据（因零接线，也无从取）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | three_way 配对确定性（sorted by flow_id）+ 异常 ID=recon_id+序号 + 同输入同输出——不变量兑现 | three_way_reconciliation.py:282-299,308 | （正面） | 同输入跑两次 diff 报告（除时钟） |
| A | three_way 输入校验 Fail-Closed：空流水/重复流水/重复引用/负值全拦 | three_way_reconciliation.py:204-246 | （正面） | 跑测试 |
| A | **费用 trade_ref=None 静默逃逸**：佣金/印花税流水 trade_ref=None 时既不参与匹配（303 行要求 is not None）也不列孤儿（371-372 行同条件）——适配层漏填 trade_ref 时费用差异无声消失 | three_way_reconciliation.py:301-304,371-379 | **P1** | 构造 COMMISSION、trade_ref=None、金额错 10 倍 → 断言无 FEE anomaly 且无 MISSING |
| A | 利息"仅计数不参与匹配"（头注 92-98），但 totals 无 interest 细分计数——"仅计数"承诺未兑现 | three_way_reconciliation.py:390-396 | P3 | 查 ReconReport.totals 键 |
| A | eod matched 定义 `positions_matched and cash_matched is not False`（219）——现金未核对（None）不影响"总体一致" | eod_reconciliation.py:219 | P2（见缺陷1） | 不带 broker_cash 跑，matched=True |
| A | eod 资金核对数学：cash_diff=system−broker、`abs(diff)<=0.01` 容差 | eod_reconciliation.py:181-183 | （正面） | 跑测试 |
| B | eod 资金核对上游=tracker.cash；SimulationBroker 现金模型只扣佣金（无印花税/过户费，见 R05 簿）→ 接真实券商后 EOD 资金核对将出现每日 =印花税+过户费 的恒定 DIFF | eod_reconciliation.py:181 + simulation_broker.py:226,235 + tracker.py:158,167 | P2（接线时预警） | 模拟一笔卖出对照 cash 差 |
| B | three_way 上游契约：PositionFlow.trade_ref 必填（222）但 CashFlow.trade_ref 可 None（245-246）——同一"券商侧"两流水引用键约束不对称=隐式契约无文档 | three_way_reconciliation.py:221-222 vs 245-246 | P2 | 读校验段 |
| C | **ThreeWayReconEngine 生产调用方=0**（全仓 grep 仅注释/文档引用）；[CONSUMERS] 写"运行时装配批（盘后三向对账调度/告警路由/台账工作台）"未见施工 | three_way_reconciliation.py:5 + grep `ThreeWayReconEngine(` | **P1**（孤儿） | grep 实录零命中 |
| C | **EodReconciler 生产调用方=0**（全仓 grep 仅自身文件+测试）；[CONSUMERS]"盘后 15:30 任务链/日终调度接线"未兑现 | eod_reconciliation.py:5 + grep `EodReconciler(` | **P1**（孤儿） | grep 实录零命中 |
| C | 台账 _ledger/_recon_ids 纯内存：进程重启后 OPEN 异常跟进状态全丢（若未来接线，将无声丢台账） | three_way_reconciliation.py:199-200,382-383 | P1（接线前置条件） | 重启后 ledger() 为空 |
| D | three_way 重复 recon_id 抛错=同进程幂等闸；但 _recon_ids 内存态——重启后同 recon_id 可重放（与上一条同根） | three_way_reconciliation.py:262-263 | P2 | 重启后同 recon_id 重跑不抛 |
| D | eod 与 R04 链的职责边界声明清晰（头注 20-28 查重分工），未发现第三处日终资金对账实现 | eod_reconciliation.py:20-28 | （正面） | — |
| E | three_way 对"结算单缺一整天"不设防：引擎只核对喂入窗口，窗口完备性全靠（不存在的）调用方 | three_way_reconciliation.py:250-269 无窗口校验 | P2 | 只喂 1 笔而当日实有 50 笔 → 无 anomaly 报 matched 按喂入集判定 |
| E | eod alert_sink 仅在 `not matched` 时触发（235-246）；broker_cash 缺失（断供）路径 cash_checked=False 但无任何告警——**结算单缺失日=绿灯**（checklist #6 直接命中） | eod_reconciliation.py:176,219,235 | **P1** | run_eod 不带 broker_cash：matched=True、无 alert |
| E | ④ rebuild_from_broker 在① reconcile 冻结之后执行，对齐后冻结集不重算→旧 drift 冻结残留到下一轮 | eod_reconciliation.py:173,206-212 | P3 | 带 drift+align_to_broker 跑，观察 frozen 未清 |
| F | 三向对账=Juspay（2025）三向收口（账本↔结算↔资金）同构；台账跟进状态机（OPEN→INVESTIGATING→RESOLVED 终态不可逆）对齐"immutable audit ledger+例外工作流"惯例 | three_way_reconciliation.py:100-107 | （对等已有） | 对照 juspay.io/blog 同名文 |

## 3 SOTA 对照

- 三向对账架构：Juspay《Payment Reconciliation Across Multiple PSPs》（juspay.io/blog，2025）——merchant ledger↔PSP settlement↔bank cash 三方收口+例外工作流。**对等已有**（three_way 的三方模型+异常台账同构）。
- 断供检测：业界（Oceanobe 事件驱动对账文，oceanobe.com，2025 前后）把"对账输入缺失本身=告警事件"当第一公民。**本项目两模块均缺此腿**（E 轴两条 P1）→ 立卡候选：窗口完备性守卫（当日系统成交笔数 vs 结算单笔数为 0/缺失比率→告警）。

## 4 缺陷清单

1. **P1 结算单缺失日=绿灯（eod 资金核对可静默跳过）**
   现状→broker_cash=None ⇒ cash_checked=False，`matched` 仍可 True（219），告警仅挂 `not matched`（235）——结算单断供不产生任何告警。
   证据→eod_reconciliation.py:176,219,235-246；test_eod_reconciliation 有"未核对"分支用例但断言的是字段值而非告警缺失。
   影响与爆炸半径→对账的意义在抓差异；上游断供时最该响的铃不响（checklist #6：399106 断更两月恒 0 同型）。一旦接线生产，券商通道故障期账户级资金核对无声消失。全账户级。
   建议修法→`cash_checked=False` 时也触发 alert_sink（事件类型区分"缺数据"与"有差异"）；或调用方强制要求 broker_cash 必填、缺失改由显式 skip 参数表达。
   验证法→run_eod 不带 broker_cash + alert_sink spy：断言收到"资金核对未执行"事件。
2. **P1 两引擎双孤儿：流水级与账户级日终对账均零生产接线**
   现状→ThreeWayReconEngine 与 EodReconciler 无任何生产装配点；各自 [CONSUMERS] 宣称的"运行时装配批/15:30 任务链"未施工；three_way 台账纯内存无持久化。
   证据→grep `ThreeWayReconEngine(`/`EodReconciler(` 全仓仅定义与测试；three_way_reconciliation.py:199-200。
   影响与爆炸半径→P0 钱路径的"三方收口+日终账户核对"两道闸当前**只存在于测试里**；台账丢失误=差异跟进无声蒸发（接线后）。
   建议修法→接线裁决收口方定优先级：最小闭环=挂入 scripts/run_post_settlement.py（其已串 SettlementReconciler，增量=补三方与账户级两步）；台账持久化复用 JsonStateStore。
   验证法→接线后 grep 出生产装配点；重启后 ledger() 可恢复。
3. **P1 费用流水 trade_ref=None 静默逃逸**
   现状→佣金/印花税 CashFlow 若 trade_ref=None：跳过费用归集（303）且不列孤儿（371-372 条件含 `is not None`）。
   证据→three_way_reconciliation.py:301-304,371-379；校验层仅拦"空串"不拦"佣金类费用无引用"（241-246）。
   影响与爆炸半径→券商数据适配层一个字段映射 bug 就能让全部费用差异脱离对账视线，报告仍 matched=True。资金级。
   建议修法→校验层加约束：fee_type∈{COMMISSION,STAMP_TAX} ⇒ trade_ref 必填（Fail-Closed 对齐 222 行 PositionFlow 先例）。
   验证法→构造 COMMISSION/trade_ref=None → 断言抛 ThreeWayReconError。
4. **P2 窗口完备性无守卫**
   现状→引擎对"喂入即全部"无怀疑：结算单只到 1 笔而系统有 50 笔时，49 笔 MISSING 会响（好）；但两边同源少一整天（喂空集+空集）→ matched=True。
   证据→three_way_reconciliation.py:250-269（无总数守卫）；eod 同理见缺陷1。
   建议修法→告警阈值：当日系统成交>0 且券商流水=0 → 强制 MISSING 告警；eod 侧同缺陷1修法。
   验证法→两侧空集断言 matched=False 或 alert。
5. **P2 SimulationBroker 现金模型与真实券商费用结构不符（接线预警）**
   现状→eod 资金核对上游 tracker.cash 只扣 commission（tracker.py:158,167）；真实券商另扣印花税/过户费 → 接实盘后 eod 资金核对每日恒 DIFF=Σ(印花+过户)，把真差异淹没在恒定噪音里。
   证据→simulation_broker.py:226,235（只 commission）+ R05 簿现金链发现。
   建议修法→tracker 现金链接入 FeeBreakdown 全量（或 eod 核对侧声明"模拟口径"白名单差异）。
   验证法→模拟买入卖出各一笔，对照 broker 端资金与系统 cash 差=费用合计。
6. **P3 杂项**：clock 默认 naive `datetime.datetime.now`（three_way:197）与全仓 UTC 惯例不一致；interest 未按承诺计数（390-396）；eod 对齐后冻结残留（206-212）。

## 5 挂起疑问

- 两孤儿模块的接线是否属于裁定/tracker 中已登记的待办？本簿未检索全部 backlog（backtest_backlog.yaml 有变更在途，未读）。若从未立项，P0 钱路径"两道闸只在测试里"应升 Owner 门位裁决。
- eod 步骤④ `rebuild_from_broker(broker_settled_holdings, cash=broker_cash)` 中 broker_settled_holdings 的 avg_cost 口径（券商摊薄含费 vs 系统移动加权不含费）无契约文档——交接后 PnL 口径漂移（详见 R05 簿缺陷2），需与券商字段语义实测对齐。

## 6 完备性自评

- 六轴全查：A/B/C/D/E/F 均有结论；正面项 4 条（确定性配对/Fail-Closed 校验/委托不重复实现/分工声明自洽）。
- 长尾清单：①两模块均无生产运行时证据可取（零接线的直接后果）；②three_way 测试未覆盖"佣金 trade_ref=None"路径（缺陷3 的覆盖洞）；③eod 测试未断言"未核对"场景的告警行为（缺陷1 的覆盖洞）；④backlog 全量核对未做（挂起疑问1）。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
