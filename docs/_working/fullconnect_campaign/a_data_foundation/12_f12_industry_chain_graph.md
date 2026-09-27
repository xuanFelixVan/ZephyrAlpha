---
ttl: task_bound
title: "F12 产业链图谱——873 条 chain_registry 机生数据面复飞案卷"
session: zc-l01-20260927
---

# F12 产业链图谱（复飞案卷，首次独立成卷）

> 前序：M1 册 05_tdm_crossaxis.md D12 半面（真源锚定，内容质量归 M8/数据审计专项）；本卷按总册职责独立立卷+本日实测。

## 一、六向台账（本日实核）

| 向 | 内容与实证 |
|---|---|
| 上游 | PG depgraph ig_chain/ig_node/ig_edge（DDL=scripts/industry_graph/apply_industry_graph_ddl.py）；链生成判据=final3 W4-1 triage canonical（链内≥1 条链内传导边，禁重画） |
| 下游 | 车道 D/F18 产业链三高筛选（BOM 拆解）；decision_map chain_refs 轴 R45；F05 产业链数据审计修复循环；F32 图谱谱系 5 谱 |
| 自动触发 | generate_chain_registry.py 机生（chain_registry.yaml 头注 generated_at 2026-09-22T20:37:23Z；唯一合法再生成入口）；对齐链 align_all |
| 真源注册表 | docs/01_policies_and_standards/_registry/catalogs/chain_registry.yaml（**本日实数 873 条**，schema v1.0，module_id=MOD-GOV-CHAINREG，生成物禁手编）；值域消费=decision_map.py `_XREF_SPECS` CHN 轴 |
| 门禁质量尺 | R45 存在性校验（轴值域封闭）；机生禁手改=decision_map.py:115-117 注；审计修复循环=industry_chain_data_audit_policy.md（F05 同账）；覆盖判据防双口径 |
| 运行状态 | **绿**：873 条在册（与骨架一致）；registry 自带 covered 标志字段（抽查首条 covered:false/次条 true=分层覆盖在记）；industry_graph 修复件族 8+ 在盘（fix_s6_s7_nodes/execute_r1_chain_plans/build_chain_exposure_matrix 等） |

## 二、子模块三级枚举

1. 数据面：chain_registry.yaml（873 chain_id，含 node_count/edge_count/covered 字段）←PG ig_chain 族
2. 生成面：scripts/governance/generate_chain_registry.py（唯一合法入口）+apply_industry_graph_ddl.py
3. 消费/加工面（scripts/industry_graph/ 实列）：build_chain_exposure_matrix.py/calc_customer_concentration.py/backtest_supply_leadlag.py/build_node_bindings.py/execute_r1_chain_plans.py/concept_ingest.py/fix_s6_s7_nodes.py/backfill_futures_main.py
4. 审计面：industry_chain_data_audit_policy.md（审计修复循环）+F05 卷 D2/D3 账
5. 谱系面（下游 F32）：Zephyr/ChainKnowledgeGraph/股权穿透/概念题材/投入产出 5 谱（总册 F32 行，G3 有码余登记态——归 L04 带不重挖）

## 三、接线四态独立复核

- 总册：built/P2/D12。独立复核：**built 成立**（873 条实数+机生链在产+R45 校验在岗）。
- 勘误⑰：总册 F12 真源列写"chain_registry.yaml（generate_chain_registry.py 机生）"正确；但总册 F12 上游列"F05 审计"方向反了半格——审计循环（industry_chain_data_audit_policy）是图谱**质量治理**面，与其数据供给上游（PG ig_chain）并行的横切，非序列上游；DAG 语义建议总册侧加"审计横切"注（不改册，登记）。
- 抽样质量疑点（进待裁节）：registry 首条 CH-00607d464e8f node_count:1/edge_count:0/covered:false——单节点零边链占多少比例未测，可能稀释 R45 轴值域质量；归数据审计专项量化，不在本卷展开。

## 四、缺口清单

| # | 缺口 | 处置 | 级 |
|---|---|---|---|
| Y1 | 单节点零边链（covered:false）占比未量化 | 挂起+解锁=数据审计专项出分布报告；高于阈值触发 re-triage | P2 |
| Y2 | 审计修复循环手工驱动 | 施工：与 F05 D2 同批事件触发化 | P2 |
| Y3 | LLM 增补管线未建（总册 F18 注记，图谱增补需求侧） | 挂起+解锁=F18（L02 带上游）立项，本环节只供数 | P1 |
| Y4 | chain 值域与 data_asset_registry 双册镜像面 | 施工：05 册提速项 2（品类派生生成）同批评估 | P2 |

## 五、自审闸三态

挖干可施工（数据面 873 实数+生成/消费/审计三面 file 列实扫）；Y1 挂起待专项；Y2/Y4 可施工；Y3 挂起跨带。首次独立成卷，05 册沿用处已注明。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
grep -c "^- {chain_id" docs/01_policies_and_standards/_registry/catalogs/chain_registry.yaml   # 873
sed -n '1,12p' docs/01_policies_and_standards/_registry/catalogs/chain_registry.yaml          # 机生头注
grep -c "covered: false" docs/01_policies_and_standards/_registry/catalogs/chain_registry.yaml # 零边链分布初探
ls scripts/industry_graph/
sed -n '100,118p' src/zephyr/trading/decision_map.py | grep -n "chain"                        # R45 轴
```
