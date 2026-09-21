---
ttl: task_bound
title: 深度审查作业簿——相关性聚类与cluster上限
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：相关性聚类与 cluster 上限（P55）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（已核：本对象文件在基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/position/core/correlation_regime_monitor.py:109`（assess_correlation_regime）
- TDM 节点: TDM-F-C2-03（stage，config/trading_decision_map.yaml:3819）
- 生产调用方: **零**——`assess_correlation_regime`/`CorrelationRegimeReport` 全仓仅自身与包导出；header [CONSUMERS] MOD-POS-013（position_risk_budget_allocator）与 D_RISK 自适应风控⑤均 grep 零实际调用
- 测试文件: tests/position/test_correlation_regime_monitor.py（143 行，与 P54/P56 同批 151 passed 7.00s）

## 1 对象快照

- 范围：assess_correlation_regime 纯函数（182 行）——MOD-POS-011 Ledoit-Wolf 收缩协方差→相关矩阵标准化→平均成对相关（上三角不含对角）→三档 regime（LOW<0.3/NORMAL/HIGH≥0.6）+max_pair+分散失效预警。
- 排除项：covariance_estimator（MOD-POS-011）数学归其对象（本报告按消费口径抽查其输入校验：N≥2 类型化拒绝已核实，correlation_regime_monitor.py 的 n=1 边界由此上游兜住）。
- 测试覆盖概况：143 行覆盖三档判定/阈值校验/上三角均值；无多档危机形态（ρ→1）压测、无 A 股板块同涨跌形态画像（纯函数无数据依赖，可后补）。
- 材料包缺项声明：运行时证据包未取（生产零调用）；数据画像不适用。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| D | **节点声明语义与代码承载大面积错位**（checklist #4 同族）：TDM-F-C2-03 algo_note=「60 日滚动 PnL 相关矩阵→**层次聚类**→同 cluster 合并风控；ρ>0.70 持仓合并计算敞口；ρ>0.85 禁新仓；单 cluster 总权重≤5%；月度再聚类+危机期压测」——全仓 grep 无任何持仓层次聚类实现（命中均为 factor_similarity/gov_drift 等无关域）；本模块只承载"平均成对相关三档 regime"这一底座，**聚类/ρ0.70/ρ0.85/cluster≤5%/月度再聚类/危机压测六项全零代码**；阈值族也不同轴（模块 avg 0.3/0.6 vs TDM pair 0.70/0.85） | correlation_regime_monitor.py:55-57,159-171 vs config/trading_decision_map.yaml:3826-3840；grep 层次聚类/scipy.cluster/cluster_cap 全仓无持仓域命中 | P1 | `grep -rn "hierarchical\|层次聚类" src/zephyr/position src/zephyr/risk --include=*.py`；对照 TDM 节点逐项打勾 |
| C | **孤儿死码**（checklist #8）：零生产调用方；声明消费方 MOD-POS-013（position_risk_budget_allocator.py 存在但不 import 本模块）；[MATURITY] production 与现实矛盾；TDM 节点未标红 | correlation_regime_monitor.py:5,7；grep assess_correlation_regime src/ 零生产 | P2 | grep 三连（符号/类名/模块名） |
| A | 平均成对相关作为 regime 判定轴的口径局限（设计评审非 bug）：等权平均对"两两高相关但多数低相关"组合钝感——5 只同题材股 ρ=0.95 + 20 只独立股 ρ=0.05 → avg≈0.16 判 LOW，而真实扎堆风险恰在 max_pair/局部簇；模块已输出 max_pair 但 regime 判定与预警只看 avg | correlation_regime_monitor.py:144-171 | P3 | 构造 5×0.95+20×0.05 收益矩阵跑 assess 看 regime=LOW 且仅 max_pair_correlation 显危 |
| A | 数学主体正确性：corr=cov/√(var_i·var_j) 标准化+[-1,1] clamp+上三角均值排除对角——无误；阈值校验（[0,1] 有限值+low<high）完备；n=1/n=0 由上游 MOD-POS-011 类型化拒绝（InvalidCovarianceInputError），fail-closed 传导正确 | correlation_regime_monitor.py:99-106,134-157；covariance_estimator.py:107-108 | —（已核） | 单标的输入探针看类型化异常非 IndexError |
| B | 输入隐式契约：returns 序列长度/频率（60 日滚动窗语义由调用方保证）无窗口校验——喂 5 日窗口 vs 60 日窗口同样通过，avg 稳定性截然不同；"60 日滚动"语义零承载（连接线后也无从保证） | correlation_regime_monitor.py:110-118 | P3 | 短窗长窗同输入对比 avg 波动 |
| E | 危机期相关性趋于 1 的"压测"语义零实现（TDM 声明 ρ→0.9 压力情形）；HIGH 档仅出 warning 字符串，无任何下游动作钩子（diversification_effective=False 之后无人消费） | correlation_regime_monitor.py:166-171 vs TDM yaml:3838 | P3 | grep diversification_effective 消费方=0 |

## 3 SOTA 对照

- 相关性聚类用于组合风控/配置：**对等已有（成熟矿脉）**——层次聚类风险配置是近年主流：HRP（López de Prado；Hudson & Thames《The Hierarchical Risk Parity Algorithm》hudsonthames.org，2019-2026 持续维护）、Papenbrock 类 HCP（portfoliooptimizationbook.com §12.3，2024-2026）、Sass et al. 聚类风降（ScienceDirect S2452306221001416，2024，被引 16+）；**2026 新进展**：Trucíos et al. 指出层次风险聚类对协方差估计误差敏感（Springer s00181-026-02900-x，2026）——与本项目 Ledoit-Wolf 收缩前置的选择同向（收缩恰为缓解估计误差），节点选型合理但**实现缺位**。
- cluster 敞口上限（同簇合并风控/禁新仓）：**立卡候选**——公开学术文献对"cluster-level exposure cap"成文较少（多在 multi-strategy 基金实操域，TDM 引 Millennium pod 同构先例），属可辩护的项目自定纪律；建议接线时以 max_pair/簇内均值双轴而不仅 avg（对齐轴 A 局限发现）。
- 危机期 ρ→1 压测：**对等已有**——危机相关性收敛是 portfolio literature 共识（上述 ScienceDirect/Springer 论文的动机段均引），TDM 声明的"危机期压测 ρ→0.9"方向正确，缺的是实现而非依据。

## 4 缺陷清单

1. **[P1] 节点六项声明语义（层次聚类/ρ0.70 合并/ρ0.85 禁新仓/cluster≤5%/月度再聚类/危机压测）全仓无承载**，模块只交付 avg 三档底座且阈值不同轴。影响：F-C2-03 在图上表现为已建风控，实际组合扎堆保护为零；F-C2-02 约束栈的"相关性层"同样落空（联动 P54 轴 D）。建议修法：施工批次补聚类+簇帽（对齐 TDM D77 阈值），或节点改红并把声明收敛到"avg 三档底座已建、簇层未建"。验证法：§2 轴 D grep 打勾表。
2. **[P2] 孤儿死码**（header production 不实）。建议修法：接线（MOD-POS-013 真实消费或 F-C2-01 聚合链）前降 draft+节点补红。验证法：grep。
3. **[P3] avg 单轴判定的扎堆钝感**。建议修法：regime 判定引入 max_pair/簇均值第二轴（HIGH 触发条件加 max_pair≥0.85 旁路）。验证法：5×0.95+20×0.05 构造探针。
4. **[P3] 60 日滚动窗语义无校验承载**。建议修法：入口加窗口长度参数与最小样本校验（对齐 MOD-POS-011 风格）。验证法：短窗探针。

## 5 挂起疑问

- 阈值口径归一裁定：模块 avg 0.3/0.6 与 TDM pair 0.70/0.85 是"两轴并存"还是"漂移未对齐"——若并存需在 TDM/模块注释互相声明分工；请 Owner 裁定后回填。
- MOD-POS-013（position_risk_budget_allocator）是否本模块的正确消费方（header 声明 vs 实际零 import）——影响接线批次的编排设计。

## 6 完备性自评

六轴全查（A 数学四问：标准化公式/均值口径/阈值边界全过、n=1 边界实测上游兜住；B 上游=MOD-POS-011 契约抽查；C 下游=零调用方判孤儿；D=TDM 六项对账打勾+与 covariance_estimator 分工清晰；E 五问：静默失败=warning 无消费钩子、假阳性=avg 钝感、断供=上游类型化拒、重复触发=纯函数幂等、时序=无时钟依赖）。长尾：①Ledoit-Wolf 收缩数学详查归 MOD-POS-011 对象；②真实 A 股持仓相关性数据画像未做（无生产组合数据）；③143 行测试逐断言复核为抽查级。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
