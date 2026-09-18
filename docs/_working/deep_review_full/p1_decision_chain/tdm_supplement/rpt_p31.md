---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——同源补涨比价
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：同源补涨比价（P31）（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件零漂移已核）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/supply_chain_momentum.py`
- TDM 节点: TDM-E-L2-10（stage）
- 备注: 阶段0对账补册对象（T08 缺口清册）
- 生产调用方: **0（全仓 grep 仅自命中；头注 [CONSUMERS]"运行时装配批（统一注入点装配）"=前向声明态；[MATURITY] production 虚标）**
- 测试文件: `tests/signal_ashare/test_supply_chain_momentum.py`（25 用例，本班次实跑 25/25 绿；**n=6 边界无 case=测试缺口实锤**）

## 1 对象快照

367 行纯内存 DI 模型（MOD-SIG-118，B10-01376，Cohen & Frazzini 供应链动量单机版）：邻接表注入（重复边/自环/边权∉(0,1] 拒绝）+ 上游动量因子（Σ边权×Σlead权重×上游领先 1-5 日收益）+ R²>5% 传导筛选（回归器注入，未注入 Fail-Closed）+ |z|>2σ 传导异常标记。同输入必同输出（邻居字典序+并列取小 lead 确定性）。测试覆盖：非法输入 Fail-Closed 全分支、回归器异常包装、确定性。排除项：蓝图 md 与 algo_flow yaml 未审（文档件）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 数学①：领先对齐 `xs=leader[:-lead], ys=follower[lead:]`（:263-264）t→t+lead 对齐正确；最优 lead 取 R² 最大、并列保序取小 lead（:285 注释与实现一致）；异常 z=(actual−predicted)/σ，predicted 用 leader[-(lead+1)] 与 follower[-1] 对齐（:327-329）正确 | supply_chain_momentum.py:263-264,285,327-329 | 通过 | 本班次实测脚本 n=7 通过 |
| A 深度 | **边界②实锤：config 允许 min_returns=6（:152-153 要求≥max(lead)+1），但 lead=5 需要 n≥7（xs=follower[5:] 长度 1<2 即 raise :265-266）——默认配置最小样本必然 ValueError，本班次实测 n=6 → `SupplyChainMomentumError: 领先对齐样本不足: lead=5 n=1`，n=7 通过**；fail-closed 方向（炸而非错值）故 P2 非 P1；测试 25 例全绿恰好因无 n=6 case（测试缺口与缺陷互证） | :152-153,265-266 | P2 | 本报告 §4 验证法脚本复跑 |
| A 深度 | 量纲③：lead_weights 默认 (1,0.8,0.6,0.4,0.2) 和=3.0 未归一——factor 上限=3.0×Σ边权，score 截断 [-1,1]（:358）后多上游标的易饱和贴边（信息压缩）；非错误但量纲任意，阈值语义依赖隐式标定 | :132,233-246,358 | P3 | 两上游边全 0.5 权重同向收益观察 factor>1 截断 |
| B 上游 | checklist #6 断供：收益序列缺失/不足/含 NaN 全 raise（:213-224）——断供 fail-closed 有痕非恒0；回归器未注入显式拒绝（:193-194"禁止旁路拟合"）+异常统一包装（:271-272） | :193-194,213-224,271-272 | 通过 | 缺序列调用观察 raise |
| C 下游 | **孤儿裁定：生产零调用方**（头注"运行时装配批"未落地）；接线后下游=供应链动量因子层/传导异常预警消费方；z 异常标记仅落 log.warning（:342）+dataclass 字段，无告警出口——接线时预警链须补 | grep 证据；:342 | P1(接线期) | `grep -rn "SupplyChainMomentumModel" src/ --include=*.py` |
| D 旁系 | checklist #4 双承载：与 P29/P30（intelligence 族传导器）同域不同实现——本件=统计回归传导（数值），W3/W4=规则图谱传导（文本→节点），职责正交非重复；无第二份 Cohen-Frazzini 因子实现（grep 唯一） | — | 通过 | grep `supply_chain\|chain_impact` 对照 |
| E 对抗 | 五问：①静默失败=无（全 Fail-Closed raise；z 异常有 log）②假阳性=最优 lead 按 R² 挑选存在多重比较（5 次回归选最大 R²，无惩罚）——小样本下 R² 虚高致 passed 偏宽松，5% 阈值在 n 小时近似不设防③断供=收益缺失 raise④重触发幂等（除 flagged_at 时间戳）⑤时序=series[-1]=最新日约定由调用方保证，倒序注入不报错（隐式契约：收益序列方向无校验——可用负收益对称性探测兜底，未做） | :255-299 | P3 | 注入倒序序列观察异常标记方位反转 |
| F 新鲜度 | Cohen & Frazzini "Economic Links and Predictable Returns"（Journal of Finance 2008，客户动量多空月均 2.03%、负面消息慢扩散不对称）——本件为该策略单机版实现声明诚实；领先 1-5 日+边权加权为合理 A 股化改造；**对等已有（文献正源）** | https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.2008.01379.x ；http://www.econ.yale.edu/~shiller/behfin/2006-04/cohen-frazzini.pdf | 通过 | WebSearch 2026-09-18 |

## 3 SOTA 对照

- 对等已有：核心=文献正源（Cohen & Frazzini 2008 JoF）的实现，方向与不对称性结论（负消息慢扩散）兼容本件异常标记用途。
- 立卡候选：①多重比较惩罚（lead 选择加 Bonferroni 式折扣或样本外验证）②lead_weights 归一化标定——接线校准期顺路。
- 驳回：无。

## 4 缺陷清单

1. P2：**min_returns=6 与 lead=5 样本需求矛盾（默认配置最小样本必炸）**——现状=Config:152 允许 6、算法:265 要求 lead=5 时 n≥7；影响=按文档最小样本装配的调用方 evaluate() 必然异常（fail-closed 无资损但断功能）；建议=min_returns 下限改 7（或 lead 循环按 n 自适应截短）；验证法=`SupplyChainMomentumModel(links=[SupplyChainLink('UP','DN',0.5)], regressor=...).evaluate('DN', {'UP':[0.01]*6,'DN':[0.01]*6})` 复现 raise。
2. P1（接线期）：零生产调用方孤儿+MATURITY=production 虚标（checklist #8/V06 同族）；验证法=§2 C 轴 grep。
3. P3：lead_weights 和=3.0 未归一+score [-1,1] 截断饱和；P3：收益序列方向（尾部=最新）无机械校验，倒序注入静默语义反转。

## 5 挂起疑问

- 边权 weight 语义（投入产出占比？等权？）来源未登记——影响因子经济含义，接线装配批需裁定数据源。

## 6 完备性自评

六轴全查（F 带文献 URL）。长尾：①回归器注入的生产实现（谁提供 OLS）未审——纯接口契约②真实产业链邻接表数据源未登记（TDM 图谱 vs 本件注入表关系未对账）③n=6 边界外的其他 n 值（如 7≤n<12 时 lead 组合子集行为）未穷举。

## 7 收口裁定（收口方填）
