---
ttl: task_bound
title: 深度审查作业簿——目标聚合与净额轧平
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：目标聚合与净额轧平（P54）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（已核：本对象文件在基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/position/core/firm_risk_aggregator.py:173`（FirmRiskAggregator；两段接口 pre_kelly_aggregate:285 / post_kelly_clip:325）
- TDM 节点: TDM-F-C2-01（aggregation，config/trading_decision_map.yaml:3743；同模块还被 C2-02 组合约束栈锚定）
- 生产调用方: **零**——`FirmRiskAggregator(` 全仓无实例化；pre_kelly_aggregate/post_kelly_clip 零调用方（grep 命中的 .aggregate( 均为 clone_guard/semantic_audit/merkle 等无关聚合器）；引用仅存于 docstring（batched_position_builder.py:4、tomorrow_boundary_planner.py:106、budget_change_handler.py:5）。header [CONSUMERS] MOD-POS-001 的 position_sizing_engine 实际不调用
- 测试文件: tests/position/test_firm_risk_aggregator.py（1202 行，与 P55/P56 同批 151 passed 7.00s）

## 1 对象快照

- 范围：FirmRiskAggregator 全文件（804 行）——budget 口径归一求和（_sum_by_symbol）+ 冲突净额（_resolve_conflicts）+ 四层裁剪（单票 8%/流动性 ADV/行业偏离±10%±15%+绝对 30%/总仓位 regime_cap）+ 现金残差 + tail_risk 记录接口。
- 排除项：MOD-POS-001 Kelly 精裁决（本模块只留 kelly_fn 注入口）；C2-02 约束栈另 3 层（回撤限额/波动率目标/相关性）的缺失在轴 D 登记；tail_risk 的 var_calculator 归 risk 域。
- 测试覆盖概况：1202 行覆盖厚；但 **industry_map 缺省（全 UNKNOWN）路径与单策略纯减仓负权重穿透路径无测试**（两处恰为本次实证缺陷，测试造数总带 industry_map 且冲突成对出现）。
- 材料包缺项声明：运行时证据包未取（生产零调用）；数据画像不适用（纯内存聚合）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| C | **孤儿死码**（checklist #8）：零生产调用方，header [MATURITY] production 与现实矛盾；TDM-F-C2-01"intent netting 三步/净差单下发"节点按在网口径书写且未标红（对照 F-C3-03 对 MOD-PA-007 的孤儿如实声明，本节点缺同款声明） | firm_risk_aggregator.py:5,7；grep 证据见对象快照；config/trading_decision_map.yaml:3743-3790 | P2 | `grep -rn "FirmRiskAggregator(" src/ --include=*.py` 零生产命中 |
| A | **industry_map 缺省→全 UNKNOWN 伪行业→组合被静默砍到 30%**：aggregate(industry_map=None) 默认 {}，全部标的归 UNKNOWN 伪扇区；实测 30 只各 2%（合计 60%，单票均<8% 不触发单票档）被 absolute_cap 一次 scale=0.125 砍到合计 30%——**默认参数即触发组合腰斩级静默裁剪**，仅留一条 UNKNOWN cut 记录无显式告警；提供正常 industry_map 后同输入 total=95% | firm_risk_aggregator.py:689-692（UNKNOWN 归类）、729-744（绝对上限对 UNKNOWN 生效）、252（默认 {}）；探针实测 no-map total=0.30 vs with-map 0.95 | P2 | 本报告探针复跑（30×2% 无 map vs 有 map）；或 aggregate(targets, total_budget=1.0) 不传 industry_map 看 constraint_checks.sector.cuts |
| A | **净额截断口径双语义不对称**：冲突标的 net<0 → final=max(0, net+holdings)（target=存量+净变动，delta 语义）；非冲突单策略纯减仓 net<0 → 负权重**原样穿透**（实测 summed=-0.05），不做 max(0,·) 也不转 delta——同一"净卖出"两种表示，且负 target_weight 违反 long-only 不变量直达下游（Kelly 层/执行层若按 target 消费即出错）；若按 delta 消费则冲突分支的 +holdings 又重复计算存量 | firm_risk_aggregator.py:550-558（冲突分支）、565-567（非冲突直通）；探针实测 -0.05 穿透 | P2 | 探针三连（冲突 net<0/非冲突 net<0/net>0）对比 summed_weights 语义（本次已实测） |
| D | **C2-02 约束栈六层只承载四层**：同模块锚定的 TDM-F-C2-02 声明"总仓位→回撤限额→波动率目标→集中度→流动性→相关性"六层，本模块实现 单票/流动性/行业/总仓位 四层；回撤限额（资金曲线分级压缩 MOD-POS-007）、波动率目标、相关性（cluster 5%）三层零代码——图上节点有、码上约束无 | firm_risk_aggregator.py:339-346 vs config/trading_decision_map.yaml:3776-3800（C2-02 algo_note） | P2 | grep 回撤/wave/vol_target/cluster 于本模块零命中；对照 C2-02 声明 |
| A | TDM-F-C2-01 声明的 intent netting 运行时语义大面积无承载：批量窗口 1 分钟一拍、intent TTL、re-netting 循环（residual 进下一批次）、强平插队三语义、双车道、成交按贡献比例分摊回 sleeve 账本、"价格交叉闸门防跨策略自成交"——本模块是**目标权重聚合器**，非 intent 订单轧平器，上述全零实现（"净差单下发"语义由消费方承担但消费方不存在） | firm_risk_aggregator.py 全文 vs config/trading_decision_map.yaml:3747-3782（含 D85 五件套注释） | P2 | 逐条 grep TTL/批量/分摊/自成交 于模块零命中 |
| A | idempotency_key 时间戳生成（firm_agg_{unix秒}）不幂等：同秒碰撞/跨秒漂移，重试去重语义失效；created_at 用 naive datetime.now()（无时区，RULE-SCHEMA-TZ 口径冲突） | firm_risk_aggregator.py:447-448 | P3 | 两次相邻调用比对 idempotency_key 与语义预期 |
| A | risk_limits["total_exposure_cap"]=0.95 声明后从不消费（实际 cap=入参 regime_cap）——改配置无效果的死配置项 | firm_risk_aggregator.py:198-202,746-769 | P3 | 改 risk_limits 值重跑看结果不变 |
| B | total_budget<=0 → scale=0.0 全部权重静默清零（:508）而非报错；contributions 归因也归零——上游 budget 汇总错误被静默吞成空仓指令 | firm_risk_aggregator.py:508 | P3 | total_budget=0 探针看全零输出无异常 |
| A(亮点) | 裁剪级联单调性成立（每步只减不增、cut_ratio 乘法复合正确）；CASH 豁免与残差口径自洽；tail_risk ES/VaR 比值分档（1.25/1.50）与正态 95% ES/VaR≈1.13 理论锚吻合；degraded 五条件齐全 | firm_risk_aggregator.py:60-63,100-109,387-411,428-437 | — | — |

## 3 SOTA 对照

- 多策略 intent netting+成交按比例分摊回 sleeve：**对等已有（业界实线，细节属专有基础设施）**——multi-manager 平台（Millennium/Citadel 类 pod 结构）集中执行+内部轧平+成交分摊回 PM sleeve 是标准实践，公开记载见对冲基金 due-diligence 文献（Mercer Multi-Manager Platforms DD；The Hedge Fund Journal "A New Generation Pod Shop" 讨论内部化轧平与 netting-risk 归属，thehfj/hedgefundjournal.com，2025-2026；Syfe Best Execution & Order Placement Policy 给出经纪层 order netting 实例，syfe.com，2026）。本模块实现的是"目标聚合"半段，"成交分摊/净差下发"半段缺位（TDM 叙事整体超前于码）。
- 组合层单票/行业硬帽+总敞口帽：**对等已有**——multi-strategy 基金标准风险预算栈（CAIS《An Introduction to Multi-Strategy Hedge Funds》caisgroup.com，2025）；单票 8%/行业 30% 数值属项目自定（31 号参数域），结构同构。
- UNKNOWN 扇区兜底裁剪：**驳回（无业界先例支持把未分类资产聚成伪扇区做帽）**——业界对未分类敞口通常走"拒绝聚合/人工通道"而非静默归组裁剪；本报告按缺陷立卡。

## 4 缺陷清单

1. **[P2] industry_map 缺省→组合被 UNKNOWN 伪扇区静默砍到 30%**（默认参数即触发）。建议修法：industry_map 缺失时跳过行业绝对帽并标 benchmark_missing（与偏离帽退化路径同款）或直接 raise；UNKNOWN 永不参与 absolute_cap。验证法：本报告 30×2% 探针。
2. **[P2] 净额截断双语义不对称+负权重穿透**。建议修法：明确 tp 权重语义（target vs delta）写入 docstring 并统一两分支——若 target：所有 net<0 → max(0,net)（不留 holdings 复合）；若 delta：统一 final=max(0,holdings+net)；负值绝不穿透出 pre_kelly_aggregate。验证法：三连探针（本次已实测 -0.05 穿透）。
3. **[P2] 孤儿+C2-01 运行时语义（TTL/批量/分摊/防自成交）无承载、C2-02 三层约束无承载**。建议修法：接线批次立项或把 TDM 节点改红+把"净差单下发/分摊"语义迁往未来编排件节点；C2-02 缺层在约束栈施工批次补齐。验证法：grep（§2 轴 C/D）。
4. **[P3] idempotency_key 时间戳不幂等+naive datetime**。建议修法：key 由输入内容 hash 或调用方传入；datetime 带 tz。验证法：同输入两次调用 key 应相同。
5. **[P3] risk_limits["total_exposure_cap"] 死配置+total_budget<=0 静默清零**。建议修法：删除死配置或接通；total_budget<=0 raise BudgetChangeError 类异常。验证法：改配置重跑/零预算探针。

## 5 挂起疑问

- 净额语义（target vs delta）的裁定权在 Owner：两分支必有一错，修法方向取决于 30 号/32 号对 StrategyTarget 的原始定义（本报告不越权代裁）。
- UNKNOWN 扇区在真实 industry_map 部分缺失时（部分标的有映射部分没有）同样会把无映射标的聚进 UNKNOWN 做帽——是否属设计预期请裁定（当前实现一视同仁）。

## 6 完备性自评

六轴全查（A 数学四问：归一化 scale/裁剪级联单调性/ES-VaR 分档逐个过，两个实证缺陷已立；B 上游=StrategyTarget 三格式兼容+position_snapshot 两格式兼容逐字段查；C 下游=零调用方判孤儿；D=与 C2-02 共锚+与 cross_strategy_position_merger（MOD-POS-005 跨策略合并底座）分工在 TDM 声明但后者是否存在双承载未深挖（留长尾）；E 五问：静默失败=UNKNOWN 裁剪/负穿透、假阳性=degraded 标记齐全、断供=total_budget=0 静默、重复触发=幂等键缺陷、时序=created_at naive）。长尾：①MOD-POS-005 cross_strategy_position_merger 与本模块求和的关系（潜在双承载）未深挖；②1202 行测试的逐断言强度只抽查绕过区两处；③Kelly 层（MOD-POS-001）对负权重的容错归该对象。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
