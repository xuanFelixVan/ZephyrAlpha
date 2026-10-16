---
created: "2026-10-07"
ttl: task_bound
title: "总包夜战 W1·业务块子册：数据供给（24 环节×子模块×上下游×本夜卡）"
session: st-mastertc-mine
---

# 0x_block：数据供给（A 段(F01-F12)+C 段 L9 知识供给(F30-F36)+定版新环 F123/F125/F126/F127/F131）

> 环节行/职责/上下游/模块锚点全部复用 `docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md`（F01-F122）与 `docs/_working/fullconnect_campaign/00_skeleton/00_skeleton_verified.md`（F123-F132 定版新增）；状态轴复用 `docs/_working/night_sweep_20260929/00_skeleton_nightsweep.md`。本册只做块视图组装+本夜卡挂接，不重挖、不改真源。

## 一、环节清单（24 环节）

| 环节 | 名称 | 段 | 状态轴 | 基态 | 上游（谁供料）| 下游（谁消费）| 核心模块锚点 | 本夜卡 |
|---|---|---|---|---|---|---|---|---|
| F001 | 多源采集调度 | A | 开口 | built | 外部数据源 | F04/F06/F10 | `python -m zephyr.data`；config/resource_profile_registry.yaml（96 实体） | C242(L5) |
| F002 | 数据源接入生命周期 | A | 开口 | partial | F31 胃情报 | F01 | docs/01.../sop/data_ops_sop/data_source_onboarding_sop.md | C226(L4)、C120(L5) |
| F003 | Provider 实现与源路由 | A | 已通 | built | F02 | F01 | src/zephyr/data/implementations/（miniqmt_provider.py 等） | C39(L8) |
| F004 | 清洗校验与坏数修复 | A | 等Owner | partial | F01 | F06 备用库 | src/zephyr/data/cross_source_validator.py、backfill_checker.py；data_ops_policy | — |
| F005 | 判重与数据审计 | A | 开口 | built | F01 | F12 | scripts/.../check_tick_duplication.py；data_audit_sop/industry_chain_data_audit_p | C324(L5) |
| F006 | CH 热库落库 | A | 开口 | built | F04 | 全部消费端 | src/zephyr/data/ch_config.py；scripts/ch/apply_*_ddl.py | C241(L5)、C121(L5)、C45(L10) |
| F007 | PG 架构库 | A | 已通 | built | 生成器 | 全部治理端 | postgresql://localhost:5432/depgraph；generate_project_depgraph.py | — |
| F008 | 冷库归档运维 | A | 已通 | built | F06 | 长周期回测 | scripts/ch/archiver.py | — |
| F009 | 备份 3-2-1 双链 | A | 已通 | built | 全库 | 灾备 | scripts/backup/backup.ps1、backup_ch_vm.ps1；INFRA-STORE-003 地图 | C325(L9)、C440(L9)、C109(L10) |
| F010 | 行情订阅分发 | A | 已通 | built | F01/券商 | 盘中决策链 | src/zephyr/data/scheduler.py；sch_tick_subscriber | — |
| F011 | TDM 交叉轴挂接 | A | 已通 | built | 各注册表 | TDM 全图 | src/zephyr/trading/decision_map.py:100（_XREF_SPECS 13 轴） | C75(L6) |
| F012 | 产业链图谱 | A | 已通 | built | F05 审计 | 车道 D/F18 | docs/01.../catalogs/chain_registry.yaml（generate_chain_registry.py 机生） | — |
| F030 | L9 源线·行情基本面族 | B | 开口 | missing | A 段 | F34 | TDM-E-L9-A01..A16（module_ref 大多 null=登记态） | — |
| F031 | L9 源线·另类数据族 | B | 开口 | missing | 外部 | F34/F96 | TDM-E-L9-B01..B10、C01..C03 | — |
| F032 | L9 图谱谱系 | B | 开口 | partial | F12 | F34/F18 | TDM-E-L9-G1..G5；scripts/entity_graph/equity_penetration.py | C122(L5) |
| F033 | L9 状态变量快照 | B | 开口 | partial | F38 | F34 | TDM-E-L9-V1..V3；src/zephyr/plan_engine/judgment_ledger.py | — |
| F034 | L9 知识供给汇聚 | B | 等Owner | missing | F30-F33 | F35/D 段 | TDM-E-L9-AGG（module_ref=null） | — |
| F035 | L9 决策假设与一问一考 | B | 开口 | partial | F34 | F23/回灌 | TDM-E-L9-D1/D2/E1/E2；scripts/backtest/mcts_expression_search.py；src/zephyr/tradi | — |
| F036 | L9 治理横切 | B | 开口 | partial | 全 L9 | 治理层 | TDM-E-L9-Z1/Z2；scripts/governance/reconcile_chain_refs.py | — |
| F123 | DB schema 迁移通道(REG-MIGRATION-001) | 新环 | 等Owner | new(定版新增) | — | — | 处方卷=13_f123_db_schema_migration_channel.md | C378(L5)、C383(L6) |
| F125 | data_governance 数据治理本体 | 新环 | 开口 | new(定版新增) | — | — | 处方卷=14_f125_data_governance_lineage.md | — |
| F126 | 字段字典(REG-FLD-001, 8280 行 v2.0) | 新环 | 开口 | new(定版新增) | — | — | 处方卷=15_f126_field_dictionary.md | — |
| F127 | data_eng 数据工程域(16 py) | 新环 | 开口 | new(定版新增) | — | — | 处方卷=16_f127_data_eng_engineering.md | — |
| F131 | nlp 文本情报处理线(7 py) | 新环 | 开口 | new(定版新增) | — | — | 处方卷=08_f131_nlp_text_intelligence.md | — |

## 二、块内数据流与上下游（谁喂谁、谁消费谁——真源 DAG 摘录）

### A 段·数据供给链（F001-F012）

- **F001 多源采集调度**：数据集成器按交易日历向 271 采集任务/252 CH 表灌水。上游=外部数据源；下游=F04/F06/F10。本夜卡：C242
- **F002 数据源接入生命周期**：源发现→报批→建表→接入→验收三查→路由→退役。上游=F31 胃情报；下游=F01。本夜卡：C226、C120
- **F003 Provider 实现与源路由**：miniQMT/AKShare/Tushare 等 10 源策略路由。上游=F02；下游=F01。本夜卡：C39
- **F004 清洗校验与坏数修复**：跨源校验/回补检查/AI 判净（API 大模型站）。上游=F01；下游=F06 备用库。本夜无卡
- **F005 判重与数据审计**：tick 判重禁聚合数+产业链数据审计修复循环。上游=F01；下游=F12。本夜卡：C324
- **F006 CH 热库落库**：ClickHouse 热层 DDL/分区监控/落库。上游=F04；下游=全部消费端。本夜卡：C241、C121、C45
- **F007 PG 架构库**：depgraph 9148 节点+元数据底座（架构数据=DB）。上游=生成器；下游=全部治理端。本夜无卡
- **F008 冷库归档运维**：F:/zephyr_cold Parquet 冷储 archive/restore 五重安全阀。上游=F06；下游=长周期回测。本夜无卡
- **F009 备份 3-2-1 双链**：六阶段备份+CH vhdx 双链（F 主/G 二）+离场月度。上游=全库；下游=灾备。本夜卡：C325、C440、C109
- **F010 行情订阅分发**：tick 订阅常驻+盘中实时/分钟槽位。上游=F01/券商；下游=盘中决策链。本夜无卡
- **F011 TDM 交叉轴挂接**：业务资产库挂 TDM 交叉轴（_XREF_SPECS 表驱动）。上游=各注册表；下游=TDM 全图。本夜卡：C75
- **F012 产业链图谱**：873 条产业链图谱数据面（ig_fact/chain_registry）。上游=F05 审计；下游=车道 D/F18。本夜无卡

### B 段·策略供给链＝策略工厂（F030-F036）

- **F030 L9 源线·行情基本面族**：日线分钟/Tick/板块/估值/财务/资金流/千股千评/股东户数/互动易 16 源线登记。上游=A 段；下游=F34。本夜无卡（开口，见总表 §五建议）
- **F031 L9 源线·另类数据族**：卫星/天气/招聘/电商/招投标/社媒/APP 榜/门店客流等 15 源线。上游=外部；下游=F34/F96。本夜无卡（开口，见总表 §五建议）
- **F032 L9 图谱谱系**：产业链 Zephyr/ChainKnowledgeGraph/股权穿透/概念题材/投入产出 5 谱。上游=F12；下游=F34/F18。本夜卡：C122
- **F033 L9 状态变量快照**：大盘/情绪/板块三快照（判断账本）。上游=F38；下游=F34。本夜无卡（开口，见总表 §五建议）
- **F034 L9 知识供给汇聚**：全源线→知识层汇聚点（PIT 生效日 effective_from 2026-09-08）。上游=F30-F33；下游=F35/D 段。本夜无卡
- **F035 L9 决策假设与一问一考**：因子组合挖掘→登记考试方案→验证回传修正。上游=F34；下游=F23/回灌。本夜无卡（开口，见总表 §五建议）
- **F036 L9 治理横切**：问题治理状态机+净零资产对账。上游=全 L9；下游=治理层。本夜无卡（开口，见总表 §五建议）

## 三、本夜涉及卡（15 张，去重按主挂接）

| 卡号 | 车道 | 自审闸预判 | 卡面摘要（canonical）| night_sweep 机判交叉 |
|---|---|---|---|---|
| C242 | L5 | **GREEN** | 波10 G-E.2分钟临时替代路径（不落库采样） | 18 |
| C226 | L4 | **GREEN** | 补丁D骨架W-117行尾终审改写注记 | 2 |
| C120 | L5 | **WAIT** | 空壳表逐表选型（建采集腿 vs known_data_gaps 登记 vs 退役——X-53 已撤销'请新批'改走 H-10 通道；#311/#328 在册未裁） | — |
| C39 | L8 | **GREEN** | miniQMT 退役口径文案修正（channel_manager/ch_tick_replay/br-page.js/bridge.html 等 4-7 件'全面清退'旧文案与 #339 裁定'仅实盘 | — |
| C324 | L5 | **GREEN** | L4 三把尺（禁缓存背书/供数守恒断言/反事实控制组） | — |
| C241 | L5 | **GREEN** | 波10 G-E.1个股分钟K持久化设计文档（DDL只呈批） | — |
| C121 | L5 | **WAIT** | hfq 表族血缘版本列 DDL（族内 11 张、8 张迁移残留，旧口径行可静默覆盖；⚑-5⑤/X-58） | — |
| C45 | L10 | **WAIT** | CH 复活后实弹批（etf_benchmark stub 重写#19/realtime 换腾讯源#20/intake_ledger_recon rebuild/apply_market_tables_ | — |
| C325 | L9 | **GREEN** | L5 备份链可恢复性（backup_state failed/DR 演练零实证） | — |
| C440 | L9 | **GREEN** | ⚑-3 灾备三合一（备份排除 .worktrees+时限按实测派生+免死名单 3 天影子账） | — |
| C109 | L10 | **WAIT** | 10-05 F 盘第一链摘除窗（F:\ch_backup_disk.vhdx 716G 回收，CH 单链归 G 已是 09-28 终裁定，物理摘除等 Owner 点停 VM；时间敏感） | — |
| C75 | L6 | **GREEN** | 消费面接线 CNS-01~14（114 零消费指标+139 零消费因子）——CNS 复算案卷判'生产可达=0、净减少=0'，cn_macro 全仓零引用 | — |
| C122 | L5 | **GREEN** | 股权穿透数据面：node_company/node_person 空（uscc 富化 P1①消歧桥）+股东名变体双实体（济川控股） | — |
| C378 | L5 | **GREEN** | F123 P0：DB schema 迁移登记册立项（33 件散装 apply_*_ddl.py 无版本册/回放/一致性尺） | 123 |
| C383 | L6 | **GREEN** | F123-F132 卷内四态缺口处置（F124 block 腿装饰/F129 ML 训练线 PROD 4/43/F131 三跳传递链/F126 262 字段无对账尺） | 123、124、125、126、127、128、129、130、131、132 |

## 四、处方指针（复用既有工单，不新开处方）

- 挖矿处方卷=docs/_working/fullconnect_campaign/ 各域 per-F 卷（总表夜战骨架处方指针列）；施工序列=docs/_working/fullconnect_campaign/00_workorders.md（S1-S5+§四下一战役）；分诊六态=docs/_working/final_delivery_campaign/workorders_{governance,commit_clean,data_exam_factory,docs_misc}.md。
- 本块开口环节中已有工单无卡者（如 F115'R1-R3 最薄一刀'）按总表 §五建议补卡挂接，工单不重写。
- Owner 门位卡（等Owner 状态轴/§五 保留）本夜只登记不施工；清单见总表 §四 WAIT 行。

## 五、复核命令

```bash
# 本块环节数与总表 §三 行一致；卡数与总表 §四 该块行数一致（主挂接口径）
grep -c '^| F' docs/_working/master_tc_20261006/01_skeleton/01_block_data_supply.md
```
