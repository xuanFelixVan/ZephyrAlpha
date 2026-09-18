---
ttl: task_bound
doc_type: report
title: 深度审查报告——市场预测融合（D04）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：市场预测融合（D04）

- 状态: **已审**
- 级别: P1｜类型: 算法（三层概率融合）
- 基线 commit: 2fa92002c3
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/regime/market_forecast_fusion.py:98(fuse:205)`（310 行全文通读，NaN 行为已实机复现）
- 生产调用方: **查无实际接线**——全仓 grep 命中：模块自身、`regime/__init__.py:33` 再导出、`signal_ashare/core/sector_strength_aggregator.py:4,59,100`（仅注释声明"市场级调节=market_forecast_fusion（L2-01-5）由调用方注入"）；[CONSUMERS] 栏"运行时装配批"未落地。注意头栏 `MATURITY=production` 与实际未接线不符（注册表漂移）
- 测试文件: `tests/regime/test_market_forecast_fusion.py`（25 个测试）

## 1 对象快照

- 审查范围：三层融合全文件（8 态分布校验/ExternalForecast 契约/RollingAccuracyTracker/fuse/settle/log payload）。排除项：MOD-SIG-037 NextDayForecast 引擎本体（信号域对象）；MOD-RPT-028 prediction_log_writer。
- 材料包缺项声明：NextDayState 词表 8 态语义未逐态审（引用其 value 真源）；内部模型实际准确率分布无数据画像。
- 测试覆盖概况：25 测试（校验/权重/融合/settle 时序/日志契约覆盖良好）；**NaN 无用例**。
- 变更热力：4 次。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | F-A1 **NaN 分布穿透 Fail-Closed 校验（已实机复现）**：`_validate_state_distribution` 只查键集/负值/Σ≤0；NaN 概率使 total=NaN，`total<=0.0` 为 False 放行，归一后**全部 8 态变 NaN**；下游 `max()` 对全 NaN 返回态序第一态——融合产出静默变成"GAP_UP_UP 概率 NaN"的畸形分布且不报错，违反头栏"畸形 Fail-Closed"不变量 | market_forecast_fusion.py:88-94,232-241 | P1 | `ExternalForecast(source_id='x', probabilities={8态含nan}, confidence=0.5)` 构造成功且 probabilities 全 NaN（本报告实机验证通过） |
| A | F-A2 线性意见池（linear opinion pool）融合数学正确：凸组合保 Σ=1，再归一防浮点；confidence=top_prob×众数态一致度 ∈[0,1] 自洽；并列取态序前者确定性成立 | :232-250,128 | 已查无 | 手算两源等权融合例 |
| A | F-A3 Beta 先验平滑准确率公式正确（hits+α·p0)/(n+α)，冷启动=1/8；min_weight=0.05 < 随机基线 0.125，下限实际不bind（防归零设计冗余但无害）；**先验强度 α=16 自注"初拟待实盘标定"**——16 次等效观测意味着单源需 ~50+ 条记录才能把权重与先验拉开，冷启动期外部源与内部源近乎等权 | :146-190 | P3 | accuracy 曲线仿真：60 条 50% 命中记录 vs 先验 0.125 |
| A | F-A4 自报置信度不参与权重（防虚高抬权）仅留痕——契约级好设计并文档化 | :104-105 | 已查无 | 读 dataclass docstring |
| B | F-B1 输入契约双 fail-closed：键集不全/负概率/Σ=0/source_id 空/保留字/confidence 越界全部抛错——外部主播信号畸形面覆盖良好，**唯独 NaN/Inf 缺防（F-A1）** | :79-94,112-119 | 见 F-A1 | — |
| C | F-C1 **孤儿模块（checklist#8）+成熟度漂移**：无生产调用方；下游约定面（sector_strength_aggregator 的 market_adjustment 注入位 :59）仍是注释声明；`MATURITY=production` 与现实不符——注册表/头栏漂移会让后续会话误信在产 | 头栏 [CONSUMERS]/[MATURITY] vs grep；sector_strength_aggregator.py:59 | P2 | grep 复核+读 sector_strength_aggregator 注入契约 |
| C | F-C2 爆炸半径预留评估：若按设计接线（预测日志→prediction_log；市场调节→sector 聚合），NaN 畸形分布（F-A1）会带病落库并污染 sector 调节——接线前必须修 F-A1 | :30-32 | P2(前瞻) | — |
| D | F-D1 与 MOD-SIG-037 的态词表唯一真源关系正确（_STATE_VALUES 取自 NextDayState.value，键集校验双向锁定 :82-87）；settle 的 actual 校验同源——无双词表副本 | :59-61,280-281 | 已查无 | 读 import 与 frozenset 构造 |
| E | F-E1 静默失败面：log_sink 异常→warning+log_signaled=False 如实记录（声明的 fail-open 仅日志面，产出不受影响）——规范；settle 时序 fail-closed（无 pending 即抛）防漏结算 | :259-263,282-283 | 已查无 | 先 settle 后 fuse 复现抛错 |
| E | F-E2 重跑语义：fuse 重跑覆盖 _pending_tops——若同日两次 fuse 后一次 settle，第一次的众数态记录静默丢失（in-memory tracker，重跑幂等性取决于装配批去重，本模块未防） | :251,285-289 | P3 | 两次 fuse 一次 settle 观察 report 只含第二次源集 |
| E | F-E3 tracker 为进程内状态，无持久化——重启后权重回冷启动 1/8 等权，融合退化为均匀信源平均（无告警）——装配批接线时需决定 tracker 生命周期与恢复策略 | :167,201 | P2(前瞻) | 重启场景演练 |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

| # | 对照项 | 结论 | 来源 |
|---|---|---|---|
| 1 | 概率预报线性融合 | **对等已有**——线性意见池（linear opinion pool，Σwᵢpᵢ）是概率预报组合最常用法，本项目为标准实现+动态权重 | [Genest & Zidek 1986, Combining Probability Distributions, Statistical Science](https://www.jstor.org/stable/2245510)（JSTOR，1986，引用 ~1580）；[Ranjan & Gneiting 2010, Combining Probability Forecasts, JRSS-B](https://academic.oup.com/jrsssb/article/72/1/71/7076442)（Oxford，2010，"linear pooling 最流行"） |
| 2 | 按滚动准确率定权重 | **对等已有**——权重随历史表现更新属 pool 权重分配经典路线（Genest & McConway 1987 同思路）；Beta 先验平滑是合理工程化，α=16 待标定已在注释自认 | [Ranjan & Gneiting 2010](https://academic.oup.com/jrsssb/article/72/1/71/7076442)（同上，权重层讨论） |
| 3 | 立卡候选：log-linear pool（对数线性池） | **立卡候选（低优先）**——对数池对极端概率更敏感、理论性质（外部 Bayesian）更优，但需处理零概率；当前 8 态外部源质量未知，线性池+准确率权重已够用，待实盘数据后可 A/B | [Rufo et al. 2012, Log-Linear Pool, Bayesian Analysis](https://projecteuclid.org/journals/bayesian-analysis/volume-7/issue-2/Log-Linear-Pool-to-Combine-Prior-Distributions--A-Suggestion/10.1214/12-BA714.pdf)（Project Euclid，2012） |

## 4 缺陷清单（按严重级）

- **F-A1（P1）NaN 分布穿透校验**：现状=NaN 概率使 Σ=NaN 绕过 `total<=0` 检查，归一后全态 NaN，max() 静默选首态 → 证据=实机复现（§2 F-A1）→ 影响=违反 Fail-Closed 不变量；接线后畸形预测会带病落库+污染 sector 市场调节 → 建议修法=`_validate_state_distribution` 加 `math.isfinite(v)` 检查（NaN/Inf→InvalidExternalForecastError），补 NaN 单测 → 验证法=本报告 §2 F-A1 复现脚本改用修后版本应抛错。
- **F-C1（P2）孤儿+成熟度漂移**：建议头栏 MATURITY 降 design 或登记装配批接线计划；接线前 F-A1 必修 → 验证法=grep 复核。
- **F-E3（P2）tracker 无持久化**：接线时定生命周期（重启=等权冷启动是否有意）并在装配批文档化 → 验证法=重启演练。
- **F-A3/E2（P3）**：α=16 标定挂账、fuse 重跑覆盖 pending——常规队列。

## 5 挂起疑问

1. sector_strength_aggregator 的 `market_adjustment`（-10..+10 delta）注入契约与 FusedForecast（8 态分布）之间缺转换层——谁把分布译成 delta 未定义（接线设计缺口，归装配批）。
2. 外部主播信号采集面（D_ALT_DATA）的 source_id 注册制与伪造防护（同名源重放）——采集面归 D_ALT_DATA 域，本审查范围外，接线时需接口背书。

## 6 完备性自评

- 六轴全查：A（池融合/Beta 平滑/置信度逐公式+NaN 复现）、B（输入契约逐条+缺 NaN）、C（消费方查无=孤儿+前瞻爆炸半径）、D（态词表同源锁定）、E（静默失败查无/时序 fail-closed/重跑覆盖/持久化缺口）、F（3 条带来源）。
- 长尾清单：①NextDayState 8 态语义与内部模型质量（MOD-SIG-037 本体）未审；②prediction_log_writer 契约未审（幂等/input_hash 归 MOD-RPT-028）；③8 态众数命中作为 accuracy 口径（ vs 概率口径 CRPS/Brier）的选型论证无文档——挂疑问待 Owner。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P1 NaN 分布穿透: 确认→治本（校验补 NaN/Inf 拒绝）。复检 78/78。
- 修复提交: q-0021（D03/D04 NaN 防御）。
