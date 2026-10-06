---
ttl: task_bound
completes_when: W2 施工落地（节点/边进真源+门禁绿）后随战役归档
title: TDM 2.0 节点扩容清单（W1 挖矿产物，st-tdm20-20260923）
owner: st-tdm20-20260923
session: st-tdm20-20260923
date: 2026-09-23
---

# TDM 2.0 节点扩容清单（W1）

> 设计定案 D-1..D-8 见 00_tdm20_ledger.md §2；本清单=机械生成（build_tdm20.py），与真源同批落地。
> 前后对照：节点 138 → **182**（+44，目标区间 [150,250] ✓）；边 194 → **254**（+60 新边全带四元组，+194 条旧边机械回填 pit=legacy-unaudited）。

## §1 分组构成（44）

| 组 | 节点 | 数 | 依据 |
|---|---|---|---|
| 汇聚 | TDM-E-L9-AGG | 1 | 供给健康读数→建仓流根（数据就绪度输入） |
| L1 源线 | TDM-E-L9-A01..C03 | 29 | 源线谱 29 条三档（02_source_line_registry §1），U1-U6 上图 |
| L2 图谱 | TDM-E-L9-G1..G5 | 5 | 图谱谱系注册表 G1-G5（03_graph_registry） |
| L3 状态变量 | TDM-E-L9-V1..V3 | 3 | 宪章 L3 三件：大盘/情绪/板块快照；时间分层铁律显式层 |
| L4 决策 | TDM-E-L9-D1..D2 | 2 | 因子组合挖掘（E1C，纪要§4）+假设登记与考试方案 |
| L5 验证 | TDM-E-L9-E1..E2 | 2 | 一问一考考试链+结论回传修正（反馈边 lag=T-1） |
| L6 治理 | TDM-E-L9-Z1..Z2 | 2 | 问题治理与状态机+净零与资产对账 |

## §2 源线 29 节点明细（频率/时滞/PIT 摘自 U3/U4）

| node_id | 名称 | point | frequency | lag | 档 | 吸收PQ数 |
|---|---|---|---|---|---|---|
| TDM-E-L9-A01 | 源线·日线/分钟行情 | 盘前 | daily | hours | A档在产 | 11 |
| TDM-E-L9-A02 | 源线·Tick分笔 | 盘中 | realtime | 0d | A档在产 | 11 |
| TDM-E-L9-A03 | 源线·板块/概念指数 | 盘中 | realtime | 0d | A档在产 | 11 |
| TDM-E-L9-A04 | 源线·估值 | 盘前 | daily | hours | A档在产 | 11 |
| TDM-E-L9-A05 | 源线·财务 | 盘前 | quarterly | T-1 | A档在产 | 11 |
| TDM-E-L9-A06 | 源线·资金流 | 盘中 | daily | hours | A档在产 | 11 |
| TDM-E-L9-A07 | 源线·千股千评 | 盘前 | daily | hours | A档在产 | 6 |
| TDM-E-L9-A08 | 源线·航运运价BDI | 盘前 | daily | T-1 | A档在产 | 6 |
| TDM-E-L9-A09 | 源线·财经快讯情绪 | 盘中 | realtime | 0d | A档在产 | 8 |
| TDM-E-L9-A10 | 源线·国际宏观 | 盘前 | daily | T-1 | A档在产 | 6 |
| TDM-E-L9-A11 | 源线·能源库存 | 盘前 | weekly | T-1 | A档在产 | 6 |
| TDM-E-L9-A12 | 源线·天气 | 盘中 | realtime | 0d | A档在产 | 6 |
| TDM-E-L9-A13 | 源线·股东户数 | 盘前 | adhoc | T-1 | A档在产 | 8 |
| TDM-E-L9-A14 | 源线·互动易问答 | 盘中 | intraday | 0d | A档在产 | 6 |
| TDM-E-L9-A15 | 源线·加密永续/费率 | 盘中 | realtime | 0d | A档在产 | 8 |
| TDM-E-L9-A16 | 源线·投入产出 | 盘前 | static | static | A档在产 | 8 |
| TDM-E-L9-B01 | 源线·卫星影像 | 盘前 | adhoc | unknown | B档外采 | 6 |
| TDM-E-L9-B02 | 源线·美国官方天气/海洋 | 盘前 | adhoc | unknown | B档外采 | 6 |
| TDM-E-L9-B03 | 源线·招聘JD | 盘前 | adhoc | unknown | B档外采 | 6 |
| TDM-E-L9-B04 | 源线·电商价格 | 盘前 | adhoc | unknown | B档外采 | 6 |
| TDM-E-L9-B05 | 源线·招投标 | 盘前 | adhoc | unknown | B档外采 | 6 |
| TDM-E-L9-B06 | 源线·社媒舆情X/Reddit | 盘前 | adhoc | unknown | B档外采 | 6 |
| TDM-E-L9-B07 | 源线·雪球/股吧散户情绪 | 盘前 | adhoc | unknown | B档外采 | 6 |
| TDM-E-L9-B08 | 源线·APP榜单 | 盘前 | adhoc | unknown | B档外采 | 6 |
| TDM-E-L9-B09 | 源线·进出口贸易 | 盘前 | adhoc | unknown | B档外采 | 6 |
| TDM-E-L9-B10 | 源线·信用卡/支付消费 | 盘前 | adhoc | unknown | B档外采 | 6 |
| TDM-E-L9-C01 | 源线·实时门店客流 | 盘前 | adhoc | unknown | C档无渠道 | 0 |
| TDM-E-L9-C02 | 源线·银行网点/信贷活跃 | 盘前 | adhoc | unknown | C档无渠道 | 0 |
| TDM-E-L9-C03 | 源线·直播电商实时成交 | 盘前 | adhoc | unknown | C档无渠道 | 0 |

## §3 PQ 吸收计数（registry_latest.yaml row_count=283，机械统计）

- 源线轴（line_ref 非空）：**194 问** → 29 个 SL 节点（逐线计数见上表）
- 图谱轴（graph_ref 非空）：**18 问** → G1=4 G2=3 G3=4 G4=4 G5=3
- L0 元问题：4 问 → Z1/Z2 治理节点管辖面
- 分层其余（L3/L4/L5/L6 散问）：大盘/板块→V1/V3+D1；情绪→V2（独立对话未建）；决策→D1/D2；验证→E1/E2；治理→Z1/Z2
- 未计入（line_ref/graph_ref/layer 均空或 combo/ext 组）：随 D2 假设登记节点入表，不单设节点（净零：同域不重复设卡）

## §4 新边 60 条四元组（摘录关键 25 条，全量见真源 edges 段 TDM 2.0 批注下）

| 边 | 类型 | payload_type | frequency | lag | pit_proof |
|---|---|---|---|---|---|
| TDM-E-L9-A01 → TDM-E-L9-AGG | feed | data | daily | hours | K线落定不修订，复权因子禁进PIT窗 |
| TDM-E-L9-A02 → TDM-E-L9-AGG | feed | data | realtime | 0d | TDX分笔仅近交易日，历史依赖包断档不可补 |
| TDM-E-L9-A03 → TDM-E-L9-AGG | feed | data | realtime | 0d | 指数快照落定不修订，成分随披露更新 |
| TDM-E-L9-A04 → TDM-E-L9-AGG | feed | data | daily | hours | 估值按交易日落定，回补须按披露日对齐 |
| TDM-E-L9-A05 → TDM-E-L9-AGG | feed | data | quarterly | T-1 | 按公告日PIT，财报修订挂披露时戳 |
| TDM-E-L9-A06 → TDM-E-L9-AGG | feed | data | daily | hours | 日度聚合盘后落定不修订 |
| TDM-E-L9-A07 → TDM-E-L9-AGG | feed | data | daily | hours | 评级快照日更，历史不修订 |
| TDM-E-L9-A08 → TDM-E-L9-AGG | feed | data | daily | T-1 | 运价指数发布日锚定 |
| TDM-E-L9-A09 → TDM-E-L9-AGG | feed | data | realtime | 0d | 快讯时戳不可回填，聚合窗口须右闭 |
| TDM-E-L9-A10 → TDM-E-L9-AGG | feed | data | daily | T-1 | FRED发布日锚定，修订挂vintage |
| TDM-E-L9-A11 → TDM-E-L9-AGG | feed | data | weekly | T-1 | EIA周报发布时点锚定 |
| TDM-E-L9-A12 → TDM-E-L9-AGG | feed | data | realtime | 0d | 观测时戳即落定，预报分版本 |
| TDM-E-L9-A13 → TDM-E-L9-AGG | feed | data | adhoc | T-1 | 披露日锚定 |
| TDM-E-L9-A14 → TDM-E-L9-AGG | feed | data | intraday | 0d | 问答时戳不可回填 |
| TDM-E-L9-A15 → TDM-E-L9-AGG | feed | data | realtime | 0d | 交易所快照，资金费率8小时周期锚定 |
| TDM-E-L9-A16 → TDM-E-L9-AGG | feed | data | static | static | 统计口径年份锚定（2020版153部门） |
| TDM-E-L9-B01 → TDM-E-L9-AGG | feed | data | adhoc | unknown | 渠道未接，PIT未评估 |
| TDM-E-L9-B02 → TDM-E-L9-AGG | feed | data | adhoc | unknown | 渠道未接，PIT未评估 |
| TDM-E-L9-B03 → TDM-E-L9-AGG | feed | data | adhoc | unknown | 渠道未接，PIT未评估 |
| TDM-E-L9-B04 → TDM-E-L9-AGG | feed | data | adhoc | unknown | 渠道未接，PIT未评估 |
| TDM-E-L9-B05 → TDM-E-L9-AGG | feed | data | adhoc | unknown | 渠道未接，PIT未评估 |
| TDM-E-L9-B06 → TDM-E-L9-AGG | feed | data | adhoc | unknown | 渠道未接，PIT未评估 |

## §5 旧边机械回填规则（194 条，R43 欠账显式化）

- payload_type ← edge_type×from 节点型：feed+sensor=data｜feed+stage=signal｜feed+aggregation/gate=state｜sequence=decision｜feedback=feedback｜broadcast=governance
- frequency ← to_node.point：盘前/盘后=daily｜盘中=intraday｜持续=continuous
- lag ← feedback=T-1（时间分层铁律）否则 0d
- pit_proof ← `legacy-unaudited`（诚实欠账标记：未经逐边 PIT 审计，不冒充已证；探测器读数归 W4 对账报告）

## §6 净零声明

- 44 节点全部有独立决策职能（传感器/供给结构/快照/假设/考试/治理），与既有 138 节点零功能重复：漏斗 L0-L4 语义不变，L9=横切供给轴；V 组是"快照台账供给"非"状态判定"（判定仍在 L1-AGG/L2-04）。
- 60 新边不重画传导链（禁重画）：583 有效链经 chain_refs 轴引用（W4），不进 TDM 节点/边本体。
- schema_version 保持 1.2（D-2，payload_zh 先例：可选字段演进不触发 MODIFY-GUARD）。
