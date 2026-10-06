---
ttl: task_bound
title: "幽灵13项口径纠正落册报告"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-04
---

# 幽灵13项口径纠正落册报告（EXEC-D8）

> 依据=docs/_working/fullflow_mine/verify/D6_ghost13_mining.md（EXEC-D6 三段挖掘，裁定 13/13 口径纠正、0 建表 0 删码）。
> 目标册=docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml（非投影册，直改合规；v1.9.8→v1.9.9，last_updated=2026-10-04）。

## 一、落册处数（逐类）

| 类 | 条目 | 动作 | 处数 |
|----|------|------|------|
| 1 | DS-029~039（11 张 factor_analysis） | physical_type 模块路径→`in_memory_compute`（册内词表勘察：既有 clickhouse_table/postgres_table/代码锚路径，无内存计算枚举，按 D6 建议引入显式值）；degradation_note 逐条追加 D6 定案句（模块实体存活 src/zephyr/factor/analysis/ 27 文件+真消费 ic_ir_calc←multifactor_sleeve 等=内存计算工序非落库表，PG/CH 无表非数据丢失）；status 维持 candidate；updated_at→2026-10-04 | 11 条 ×（physical_type+note+日期）=33 字段 |
| 2 | DS-224 ig_industry_graph | status candidate→**active 复评回升**（满足其 degradation_note 自设回升条件）；physical_type postgres_table→`pg_depgraph_tables`；degradation_note 记回升依据（depgraph PG 四表族已扩 13 表实测增长：ig_node 3328→5560/ig_fact 264072/ig_product_revenue 165255/ig_company_metric 235392 等，api_server cm_* 通道 :3854 等活查；证据=D6 报告 §1.4）；updated_at→2026-10-04 | 1 条 ×4 字段 |
| 3 | DS-225 chain_impact_stream | status 维持 candidate；physical_type 多行类锚→`job_and_endpoint`（原类锚信息由 code_symbol=chain_impact_stream.py::ChainImpactStream 保留不丢失）；degradation_note 记端点实证（api_server.py:4786 /api/chain-impact-stream 存活，实现真源三件套在位，按自设路径改登 job/endpoint 资产）；updated_at→2026-10-04 | 1 条 ×3 字段 |
| 4 | JOB-028~038 | description 逐条追加"输出为内存计算工序产物，物理类型口径见对应 DS 条目（2026-10-04 口径纠正）"（job_schema 无 degradation_note 字段，按 description=notes 位落）；updated_at→2026-10-04 | 11 条 ×2 字段 |
| 5 | 册头机械字段 | version 1.9.8→1.9.9；last_updated 2026-10-01→2026-10-04；补 D8 口径纠正批 changelog 注记；entry_counts 无增删不变（datasets 334/jobs 122 实测复核一致） | 3 处 |

合计：24 条目、49 字段落册；全程锚行精确 Edit（禁全局 sed），改后 `yaml.safe_load` 进程外验证 **rc=0 全绿**（11 条 physical_type/status/note/date 逐条断言+DS-224/225 断言+JOB-028~038 断言+残留扫描：factor/analysis/ 路径残留仅 DS-040（deprecated，不在 13 项清单，不属本批））。

## 二、wiring_registry 联动核（无治愈事件，理由留痕）

对照 data/runtime/consumption_census_ledger.json（updated_at=2026-10-04）：islands 140 岛**全部 state=zero**（counts 头 active=2/retired=1 所指实体不在 islands 列表，families 段亦无 11 模块条目）；11 模块名与 5 处真消费锚（multifactor_sleeve/signal_dedup.py/model_risk_audit/_g04_ops_check/signal_providers.py/factor_lifecycle_runner）在**全账本零出现**。任务条件"已实证 state=active 的岛补 wired 事件（无则跳过）"→**无则跳过**，island_transitions 零新增（治愈语义无对象，防止无实证留痕）。

`generate_wiring_registry.py --repo-root . --check` 实测 **rc=1**：`DRIFT: 账面缺项 3 条: IND-MOM-002(期望 unwired, 账面 缺); IND-VOL-007; IND-VOL-015`。归属判定：wiring_registry.yaml 与 census ledger 均 git-clean（本批唯一脏文件=data_asset_registry.yaml）；EXEC-5（2b0513f3dd，10-01）记 rc=0 后账面未动，而 ledger 为 runtime 文件今日被他会话重扫加岛——**3 条 IND-* 缺项=他会话在途 drift，非本批引入**（本批 DS/JOB 条目与 IND-* 无交集），按宪法 §3.4 他会话在途工作不代修，留本节移交。

## 三、纪律留痕

- claim：lock_files.py acquire data_asset_registry.yaml @st-datasop-20260930（ACQUIRED，30min TTL）。
- 未碰：capability_canonical 投影册、A 队互斥清单、config/*map*.yaml。
- 提交：git_commit.py --session st-datasop-20260930 --adopt-prior-work --skip-preflight --no-auto-enqueue --allow-non-worktree（ZEPHYR_PRECOMMIT_DEBT_RATCHET=0 lever 留痕于 commit message）；**注册表单体已提交 hash=95f5cb840c**（git log -1 --name-only 核实归属纯净无连坐）；本报告因 CREATE-GUARD 无 token 未入库（batch_creation_tokens.py fail-safe 拒收：capability_canonical 基底缺他会话 2 条 token 判"陈旧快照压盘"，工具处方=增量补回他会话条目——属跨会话基底手术，按本任务"禁碰 capability_canonical 投影册+拒收则留盘移交"纪律不执行），留盘移交。
- 禁改区复核：capability_canonical_file_registry.yaml 等投影册零触及。
