---
ttl: task_bound
title: 深度审查报告——盈亏与费用计算（R05）
owner: st-deeprev-20260918
created: 2026-09-18
reviewer: GLM-5.3-Flash/st-deeprev-20260918
baseline_commit: 2fa92002c3
---

# 深度审查报告：盈亏与费用计算（R05）

- 状态: **已审**
- 级别: P0｜类型: 算法
- 基线 commit: 2fa92002c3
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/trading/pnl_calculator.py:206`（PnlCalculator）/ `:176`（AShareFeeCalculator）/ `:64`（FeeConfig）
- 生产调用方（实核，**更正作业簿预填**）: 预填"recon_runner._compute_l3_pnl:285"不实——recon_runner 用 daily_auditor.PnLReconciliation，不经本件。实核消费方=`src/zephyr/reporting/attribution.py:51,106`（费率唯一真源约定）、`realtime_pnl_dashboard.py:209,267`（逐笔已实现+浮盈）、`report_watermark_tracker.py`
- 测试文件: tests/trading/test_pnl_calculator.py（426 行，全绿 2026-09-18 实录，含于 94 passed 批次）
- 备注: 费率错一分 PnL 全错——本簿含全费用手算复算（§4.0）

## 1 对象快照

- **范围**：PnlCalculator 全文（已实现/未实现/组合汇总）+ AShareFeeCalculator/FeeConfig（A股三项费用）+ 成本口径上游 PositionTracker.apply_fill/rebuild_from_broker（avg_cost 唯一来源）。
- **排除项**：attribution.py 的 Shapley/FIFO 归因内核（另一独立大件，本簿只核其对本件费率的复用声明）；daily_auditor L3 口径归 R04 簿。
- **测试覆盖概况**：min-5/印花单边/过户双边/负值 fail-fast/零持仓均有用例；券种差异与 per-order 最低佣金语义无覆盖（结构上不可表达，见缺陷 3/4）。
- **材料包缺项声明**：同 R01；Owner 实单费用单（佣金是否含规费）未取得——经手费/证管费口径问题只能挂起。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | 恒等式结构成立：net=毛−费（RealizedPnl.net_pnl:111-114）；BUY 毛盈亏=0 费用仍计（98-99,271-274）；组合 total=已实现净额+未实现毛额（149-152）——自洽 | pnl_calculator.py:98-99,111-114,149-152,271-276 | （正面） | §4.0 手算对照 |
| A | 三项费率与现行法定一致：印花税 0.05% 仅卖出（193）、过户费 0.001% 双边（195）、最低佣金不免五（191）；佣金万0.854=Owner 协议费率（tracker#233/ARCH-134 在册） | pnl_calculator.py:64-77,188-200 | （正面，轴F 实证） | 对照 §3 来源 |
| A | 边界完备：价格/数量/均价负值 fail-fast（252-266,326-335）；qty=0 未实现=0（337-338）；空头分支数学正确但 A 股不适用（344） | pnl_calculator.py:252-266,326-344 | （正面） | 跑测试 |
| A | avg_cost 来源=移动加权**不含费**（tracker cost 项不含 commission）——与"费用单列 net_pnl"分工一致，总口径正确 | tracker.py:152-156 | （正面） | 手算对照 |
| A/B | **avg_cost 缺失置 0**：recover_from_broker 重建时成本底档缺失置 0（"持仓数量优先于成本精度"）→ 重启后浮盈=(现价−0)×qty=全市值记为浮盈 | risk_layer_orchestrator.py:655-663 + tracker.py:209-211 | **P1** | 新 tracker+券商有持仓 → recover → dashboard 浮盈=市值 |
| B | **券商 avg_cost 口径未契约化**（eod ④ 路径）：rebuild_from_broker 的 avg_cost 入参语义（券商摊薄含费 vs 移动加权不含费）无文档——T+1 对齐后成本口径静默切换 | eod_reconciliation.py:146-147,208 + tracker.py:205-211 | P2（接线/日终启用时） | 对照券商字段实测 |
| B | fill.commission（券商原值）与 FeeCalculator 输出无对账——"阶段2可增加"自认未做；两套费用真源并存无互核 | pnl_calculator.py:244-245 | P3 | 构造两者差 10% 观察无人告警 |
| C | 消费方=reporting 三件（attribution/realtime_dashboard/watermark）；attribution 头注声明"费率唯一真源=pnl_calculator 不重复实现"（D 轴去重正面） | attribution.py:8,51,106 | （正面） | grep |
| C | 爆炸半径：avg_cost 错 → 浮盈错（dashboard）+ 已实现错（avg_cost 是卖出毛盈亏输入）+ attribution 全链错——单账户全策略级 | pnl_calculator.py:229,272 | （结构性） | — |
| D | 三套费用模型并存：FeeConfig（万0.854+min5+印花+过户）/ SimulationBroker（quantity×price×rate，**无 min5 无印花无过户**）/ 券商实单——ARCH-134 只统一了费率值 | pnl_calculator.py:64-77 vs simulation_broker.py:189 + architecture_issue_registry.yaml:17880-17912 | P2 | 并排读三处 |
| D | "#233 裁定"编号歧义：真源=tracker#233（ARCH-134 费率统一）在册✓；但"裁定#233"=蜡烛图退役（ruling_registry.yaml:1769-1775）——码内"#233 裁定"写法极易误引（checklist #15 邻型） | pnl_calculator.py:68,74 | P3 | 读两处注册表 |
| E | 现金链不含印花税/过户费：tracker 现金只加减 commission（158,167）→ 模拟盘闭环内自洽（ARCH-134 裁定"模拟盘以模拟盘费率为准"背书），但接真实券商资金核对时 eod 恒 DIFF=Σ(印花+过户)（R03 簿已预警） | tracker.py:158,167 | P2（接线预警） | 卖出对照券商资金差 |
| E | 最低佣金按**笔(fill)** 收（191）而券商实收按**委托(order)**：同委托拆 3 笔 partial fill 时系统费用高估 2×5 元 | pnl_calculator.py:188-191 | P2 | 一委托三笔回放对照费用 |
| F | 费率口径核验（两项检索实证）：印花税 0.05% 卖出单边=现行（2023-08 减半）；过户费 0.001% 双边=现行（2022-04 下调）；北交所过户费 0.007‰、ETF 免印花——费率无券种/市场参数（见缺陷 3） | 见 §3 | 见 §3 | — |

## 3 SOTA 对照

- **印花税**：0.05% 卖出单边，2023-08-28 起减半征收=现行——雪球《2025最新印花税规定》（xueqiu.com/1785441490/321962595，2025）；上海证券交易所收费一览表（sse.com.cn/services/tradingservice/charge/ssecharge/，官方）。**对等已有**（代码正确）。
- **过户费**：成交金额 0.01‰（0.001%）双边，2022-04-29 起下调 50%=现行；北交所 0.007‰——浙商证券《证券交易收费标准》（stocke.com.cn/main/a/20230627/7025309.shtml，2023 页面/检索 2026-09-18）。**对等已有**；北交所差异未建模（并入缺陷 3）。
- **规费**：经手费 0.0341‰+证管费 0.02‰ 通常含于佣金——知乎专栏 2025 佣金构成（zhuanlan.zhihu.com/p/19989319449）。FeeConfig 未建模：若 Owner 协议佣金为"全包"则无影响，若不含则低估——**挂起待实单核对（checklist #13 同型：外部契约未实测）**。
- 结论：三项法定费率=对等已有（现行正确）；券种/市场差异化费率=立卡候选（ETF/转债/北交所，见缺陷 3）。

## 4 缺陷清单

### 4.0 手算复算（本簿核心验证：买入+卖出全费用 PnL）

场景：买入 1000 股 @10.00 元，次日卖出 1000 股 @11.00 元（avg_cost=10.00）。

| 项 | 买入 | 卖出 | 代码路径核对 |
|---|---|---|---|
| turnover | 10000.00 | 11000.00 | `turnover=fill_price×qty` :268 ✓ |
| 佣金 | max(10000×0.0000854=0.854, **5**)=5.00 | max(11000×0.0000854=0.9394, **5**)=5.00 | `max(turnover×rate, min)` :191 ✓（两笔均触底） |
| 印花税 | 0（仅卖出） | 11000×0.0005=**5.50** | `if side==SELL` :193 ✓ |
| 过户费 | 10000×0.00001=**0.10** | 11000×0.00001=**0.11** | 双向 :195 ✓ |
| 费用合计 | **5.10** | **10.61** | FeeBreakdown.total :88-91 ✓ |
| 毛盈亏 | 0（买入不计） | (11−10)×1000=**1000.00** | :271-274 ✓ |
| 净盈亏 | −5.10 | 1000−10.61=989.39 | net=毛−费 :111-114 ✓ |
| **全程净 PnL** | **984.29**（=−5.10+989.39） | | PortfolioPnl.total_realized :140-142 ✓ |

复算结论：**逐项与代码一致，公式正确**。全程费用 15.71 元=卖出额的 0.1428%。盈亏平衡点验证：卖价需 ≥10 元×(1+费用率)≈10.0163 元才保本（佣金双向触底 5 元主导）——与 191 行行为一致。
另核现金链（tracker.apply_fill）：买后 cash−10005（=价+佣金），卖后 cash+10995（=价−佣金）——印花税+过户费 6.61 元**不入现金账**（tracker.py:158,167），见缺陷 5。

1. **P1 重启后 avg_cost 置 0 → 浮盈=全市值**
   现状→recover_from_broker 契约适配"avg_cost 保留 tracker 既有底档（缺失置 0）"；新 tracker（进程重启、新 session 目录）+券商有持仓 ⇒ avg_cost=0 ⇒ calculate_unrealized 返回 (price−0)×qty=整仓市值当浮盈。
   证据→risk_layer_orchestrator.py:655-663（"成本底档缺失不阻断重建"）+ pnl_calculator.py:341 + realtime_pnl_dashboard.py:267（直接消费）。
   影响与爆炸半径→dashboard/attribution 静默错报浮盈（不报错只亏口径）；"不阻断重建"是 P0-2 事故链的正确取舍，但下游无"成本未知"标记——错值当真值传播。实时盈亏全链。
   建议修法→avg_cost=0 且 qty≠0 的持仓在 RealizedPnl/UnrealizedPnl 加 `cost_basis_unknown` 标记（或抛错/置 None），消费方显式降级为"N/A"而非当 0 成本。
   验证法→新 PositionTracker + rebuild 持仓 qty=100/avg_cost=0 → calculate_unrealized 断言返回标记或异常而非 gross=市值。
2. **P2 三套费用模型并存（min5/印花/过户口径互相不一致）**
   现状→FeeConfig 全套 vs SimulationBroker 仅 commission 无 min5（simulation_broker.py:189）vs 券商实单。ARCH-134 只统一了回测费率值（万0.854），费项集合与 min5 语义未统一。
   证据→pnl_calculator.py:64-77 vs simulation_broker.py:189；architecture_issue_registry.yaml:17880-17912。
   影响与爆炸半径→回测-模拟盘费用系统性偏离（L1 COMMISSION_MISMATCH 参考列噪音的根因之一）；回测成本偏乐观（模拟盘无印花税→费用低估）。
   建议修法→SimulationBroker 装配 AShareFeeCalculator（费率可配），或在 56 号文对账侧把费用差归类规则显式化。
   验证法→同一笔卖出在两模型下断言费用差=印花+过户。
3. **P2 费率无券种/市场参数（ETF/转债/北交所）**
   现状→FeeConfig 全市场一套：ETF 交易免印花税、可转债无印花无过户、北交所过户费 0.007‰——现行费率均按券种/板块差异化，代码无法表达（FeeCalculator Protocol 头注自认"未来注入 ETF 费率"）。
   证据→pnl_calculator.py:64-77,163-173 + §3 费率来源。
   影响与爆炸半径→universe 含 ETF/转债时费用系统性高估（回测收益偏保守）；无报错，方向性偏差。当前 universe 若纯股票则无实害（需收口方核 universe 构成）。
   建议修法→FeeConfig 加 instrument_class 维度或按 symbol 后缀分发计算器。
   验证法→对 510300（ETF）卖出断言 stamp=0。
4. **P2 最低佣金按 fill 而非 order 收取**
   现状→calculate_realized 逐笔调 FeeCalculator（191）：一委托拆 N 笔 partial fill ⇒ 高估 (N−1)×min5；券商实收按委托金额一次计。
   证据→pnl_calculator.py:188-191,229-233（签名即逐笔）。
   影响与爆炸半径→高频小单+拆单场景回测费用显著高估（保守向）；与券商结算单费用对账时产生可预期的差异噪音。
   建议修法→min5 判定上移到订单级聚合（或提供 order-level 计算入口）。
   验证法→同 order 三笔 partial fill 对照券商费用单。
5. **P2 现金链缺印花税/过户费（模拟盘裁定背书，接线实盘前必炸）**
   现状→tracker 现金只加减 commission（tracker.py:158,167）；ARCH-134 裁定"模拟盘以模拟盘费率为准"（在册，非缺陷），但 eod 资金核对容差 0.01 元——接真实券商资金后每日恒 DIFF=Σ(印花+过户)。
   证据→tracker.py:158,167 + eod_reconciliation.py:181-183 + architecture_issue_registry.yaml:17912。
   建议修法→接线实盘前：tracker 现金链接入 FeeBreakdown 全量，或 eod 核对声明模拟口径白名单。
   验证法→见 R03 簿缺陷 5。
6. **P3 引用编号歧义+费用双真源无互核**
   现状→码内"#233 裁定"实为 tracker#233/ARCH-134（在册✓），但字面易误引为裁定#233（蜡烛图退役，ruling_registry.yaml:1769）；fill.commission vs FeeCalculator 对账自认"阶段2"未做（244-245）。
   证据→pnl_calculator.py:68,74,244-245。
   建议修法→注释改为"tracker#233（ARCH-134）"消歧；费用互核随 R04 缺陷 5 落库参考列一并消费。
   验证法→读两处注册表对照。

## 5 挂起疑问

- **Owner 协议佣金（万0.854）是否含规费（经手费 0.0341‰+证管费 0.02‰）？** 需实单费用单核对——决定回测成本是否低估双边 0.0541‰（checklist #13：外部契约未实测，代码层无法判定）。
- 当前生产 universe 是否含 ETF/可转债/北交所标的？（决定缺陷 3 是实害还是潜伏。）
- 券商端 avg_cost 字段语义（摊薄/买入均价、含费与否）未实测——eod ④ 启用前必须核（同 R03 挂起疑问 2）。

## 6 完备性自评

- 六轴全查：A/B/C/D/E/F 均有结论；核心复算（§4.0）逐项对照通过——**费用公式与盈亏恒等式本身无错**；问题集中在成本底档生命周期（缺陷 1）、费项集合跨模型不一致（缺陷 2/5）与费率差异化表达缺失（缺陷 3/4）。
- 长尾清单：①attribution.py 归因内核未审（独立大件，其"费率唯一真源"复用声明已核）；②实时 dashboard 的 avg_cost 消费频率/刷新链未追；③实单费用单未取得（挂起疑问 1）；④滑点/价格笼子等执行成本不在本件范围。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
