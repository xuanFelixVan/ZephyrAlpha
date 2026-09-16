---
ttl: task_bound
title: L2 收集段——原材料库（分库分表，生熟分离）
owner: ZephyrAlpha-Owner
session: st-ailayer-20260917
date: 2026-09-17
status: design_done
---

# L2 收集段骨架卡

## 职责一句话
把 L1 感知抓回的原材料结构化入库：按域分库分表（治理学/交易算法/AI 工程/数据工程/成本工程），
生熟分离——原材料库是生食库，与正式资产物理隔离，没过 L4 对比+门闸的永不直接进产线。

## 输入/输出
- 输入：L1 的搜索任务单产出（论文/开源仓库/机制描述/基准数据）
- 输出：结构化原材料条目（候选卡式 schema）→ L3 清洗；查重服务（simhash）→ 全循环

## 业界对应
AlphaEvolve evolutionary database（MAP-Elites 启发）；MAP-Elites 分格保优（Mouret & Clune 2015,
arXiv 1504.04909）= 多样性保底的具体算法蓝本——每个"行为格"留最优，防局部最优+防同质化。

## 已有件
negative_archive 阴性库（工厂五类产品之一）；ig_fact 知识库先例；候选卡 schema v0（主文档附录 B）。

## 待挖矿清单
1. 库表设计：分域 schema（每表字段/主键/查重键/simhash 指纹）
2. MAP-Elites 式分格机制：行为格怎么定义（按域？按机制族？按性能带？）
3. 生熟分离的物理边界：库放哪（duckdb 新表 vs docs vs .runtime）、与正式注册表的隔离墙
4. 入库闸：候选卡必答"进货费"两问的机检
5. 淘汰率 KPI：每百卡→入考数的健康区间与告警阈值

## 状态
壳已立。**建议本段第一个深挖**（它是七段的枢纽：L1 喂它、L3/L4/L7 都读它）。
**2026-09-17 深挖完成**：真源设计稿=[DESIGN.md](DESIGN.md)（design_v1：PG ai_intake 库表/simhash 查重/MAP-Elites 48 格（6 域×8 族）/进货费机检/淘汰率 KPI/六边接线图/9 施工项；自审闸=施工）。
