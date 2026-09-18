---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——冲击标的生成
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：冲击标的生成（P30）（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件零漂移已核）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/intelligence/chain_impact_resolver.py`
- TDM 节点: TDM-E-L2-09-2（stage）
- 备注: 阶段0对账补册对象（T08 缺口清册）
- 生产调用方: **有真实消费链：`intelligence/chain_impact_stream.py:87,252,390,437`（W5 流 resolve(:390) 真实调用 + from_pg(:437) 生产加载）→ `frontend/dashboard/api_server.py:4139` 端点——非孤儿**
- 测试文件: `tests/intelligence/test_chain_impact_resolver.py`（23 用例，本班次实跑 23/23 绿）

## 1 对象快照

378 行规则法 MVP（MOD-INT-CHAIN-IMPACT，接线 W4）：图谱节点冲击→受影响标的清单。无向 BFS N 跳扩散（默认 2 跳、hop_decay=0.6）、活节点白名单（墓碑剔除）、公司映射只取 PIT 有效行（valid_to IS NULL）、同 symbol 去重取 (hop, -conf) 最优+sources 共振计数、置信度=种子 conf×decay^hop×company_conf 截断 [0,1]、polarity 死区 ±0.15。ERROR_CONTRACT 三类畸形 raise（ZA-IT-0030）+PG 不可达显式抛（W5 catch 降级）。已知简化声明诚实（全跳同向/无事件类型细分）。测试覆盖：畸形注入/BFS 路径/去重/死区/降级。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 数学①：BFS 层序+visited 入队标记=最短跳路径正确（:317-326）；置信度连乘 `conf×decay^hop×company_conf` 有界 [0,1]（:338）；去重元组比较 `(hop, -conf, symbol)` 字典序=先跳数后置信度（:355-360）正确 | chain_impact_resolver.py:317-326,338,355-360 | 通过 | 手推两跳路径置信度 0.9×0.36 |
| A 深度 | 边界②：max_hops<0/hop_decay∉(0,1] raise（:233-236）；polarity NaN→_sign 落死区→0→空输出（:117-123,301 fail-safe）；空图/空命中 fail-open 空元组；节点/边/公司行空字段全 raise（:168,185,202）；company confidence NULL→1.0（:203） | :117-123,168,185,202-203,233-236,301 | 通过 | 传 NaN polarity 观察 () |
| A 深度 | 建模③：**无向扩散+全跳同向**为声明式 MVP 简化（:8 INVARIANTS"成本反号传导留事件类型细分后迭代 known simplification"）——供应链上游涨价对下游=成本利空，现模型一律同向传播=结构性口径误差，但已文档化非隐藏缺陷；A 股口径：不含涨跌停/停牌过滤（输出为候选清单非交易指令，边界可接受） | :8,24-26 | P3(文档化简化) | 阅 INVARIANTS 对照 ALGO_FLOW A1 |
| B 上游 | checklist #6 断供：PG 断供 from_pg 显式抛（:258 契约 W5 catch 降级）——fail-closed 有痕；ig_edge 全量边无 active 链过滤，但 `_build_adjacency` 端点限活节点表白名单（:186-187）双保险成立 | :186-187,258 | 通过 | 注入墓碑端点边观察不入表 |
| B 上游 | checklist #9 幽灵引用：node_id/symbol 存在性由来源表主键保证+注入空值校验；ig_node_company PIT 有效行（valid_to IS NULL:377）与 api_server cm_* 通道同口径（:371 注释互认） | :376-378 | 通过 | — |
| C 下游 | 消费方=chain_impact_stream.resolve(:390) 真实调用→api_server:4139 仪表盘；错值传导=伪利好/利空标的清单上屏（人工决策参考，爆炸半径=前端展示+潜在人工跟单）；direction 全跳同向错误在 W5 无二次校验（信任链直通） | chain_impact_stream.py:390 | P3 | 上屏数据回溯 path 字段核对 |
| D 旁系 | checklist #4 双承载：与 W3（P29）共享墓碑口径/SQL 常量约定/ERROR_CONTRACT 风格但无重复实现（词表 vs 扩散职责分离）；`_sign` 死区映射全仓唯一；与 event_driven_screener（P28）direction 整数口径（±1/0）语义一致（:104-109 vs P28:104）=跨族口径对齐已查无漂移 | :104-109 | 通过 | 对照 P28 EventImpactRecord.direction |
| E 对抗 | 五问：①静默失败=连接关闭静默 pass（:276-277 只读无害）②假阳性=多种子共享 visited，节点先被低置信种子占位时 path 归属随种子迭代顺序（seeds dict 注入序）漂移——**hop 相同时归属哪个种子取决于遍历顺序，置信度取的是占位种子的**（:331 seed_hit=seeds[path[0]]）；影响限于展示置信度轻微漂移③断供=PG 断供显式抛④重触发幂等（纯函数）⑤时序=N/A | :310-326,331 | P3 | 双种子图注入换序对拍 path 归属 |
| F 新鲜度 | 图谱扩散传导（BFS N 跳+衰减）与供应链风险传播文献的传导效应方向一致（ScienceDirect 2025 disruption propagation；CUHK 供应链风险沿链传导实证）；业界同类多走加权图+方向边，本件无向+同向为声明简化=**对等已有（MVP 子集）** | https://www.sciencedirect.com/science/article/pii/S0921344924005391 ；https://cbk.bschool.cuhk.edu.hk/research-whitepapers/how-does-risk-propagate-along-supply-chains/ | 通过 | WebSearch 2026-09-18 |

## 3 SOTA 对照

- 对等已有：BFS 衰减扩散为知识图谱事件传导的标准 MVP 手法；供应链传导效应实证文献支撑该功能域有效性。
- 立卡候选：方向边（supply 类型成本反号）+事件类型细分（涨价/断供/扩产分型传导）——源码已自declared为后续迭代，与学界供应链传导方向性研究一致，建议排期。
- 驳回：无。

## 4 缺陷清单

1. P3（文档化简化，接线期关注）：无向+全跳同向传导对"上游利好=下游成本利空"场景产生方向性误报——已声明 known simplification；建议=方向边细分期前，前端展示层对 hop≥1 标的加"传导方向=MVP 同向假设"标注；验证法=构造 supply 边+正向 polarity 观察下游标 direction=+1。
2. P3：多种子 visited 占位顺序影响 path 归属与置信度（:310-331）；影响轻微（同 hop 才可能）；建议=占位时保留高置信种子或文档声明；验证法=换序对拍。
3. P3：ig_edge 无 active 链过滤，依赖节点白名单间接防御——若未来引入"边级失效"（停用链但节点保留）会漏防；建议=加 chain 状态 JOIN 或留注释声明假设；验证法=§2 B 轴。

## 5 挂起疑问

- ig_node_company.confidence 的取值分布/来源未做数据画像（0.9 还是 0.3 差异直接乘进输出置信度）——建议接线统计。

## 6 完备性自评

六轴全查（F 带 URL）。长尾：①W5 流层（chain_impact_stream）自身深审不在本批，其 polarity 来源（L1-S0-1 情绪 vs event_score）融合质量未验②ig_edge 1.3k 行小表全量加载的规模假设未对账增长③两跳=默认值的经验依据未记录。

## 7 收口裁定（收口方填）
