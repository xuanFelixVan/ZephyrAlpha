---
title: "终极图书馆 · 骨架挖矿台账 v0.2"
ttl: task_bound
completes_when: Owner 批封顶声明；此后增枝须过停止判据并留理由
date: "2026-09-21"
owner: "ZephyrAlpha-Owner"
session: "st-ulib-20260921"
status: "active"
---

# 骨架挖矿台账 v0.2（依 skeleton_mining_policy 执行）

> **挖矿对象定义**：图书馆骨架 = 六馆 × 四支柱（真源映射/生成器/对账活性/入口工具）+ 防漂移件。骨架条目=**支柱件**，不是资产全集——资产全集（逐文件逐表逐指标录入）是血肉矿，封矿前禁开。
> **批次志**：批1=考古批（2026-09-20 全项目完成度调查+两路全网调研）；批2=三重扫描批第一轮（2026-09-21：ROOR 全量 75 / 生成器普查 30 / 对账机制 8 / 入口面 / 素材计数）；批3=盲区清偿+复扫（2026-09-21：两路只读盘点员+PG 实测+check_frontend_map 实跑，九盲区全清偿/转施工，见 §4.1）。

## §1 骨架矩阵（四支柱 × 六馆，SOP §5 状态纪律：✅=既有可收编 🔨=需改造 ⬜=缺口）

| 馆 | 真源映射 | 生成器 | 对账/活性 | 入口/工具 |
|---|---|---|---|---|
| 代码馆 | ✅ depgraph PG 9148 节点（REG-DEPGRAPH-001）+ module_id 74 + script-manifest 991 | ✅ generate_project_depgraph.py | ✅ align_panoramas 图1-4（module_id 轴） | ✅ blueprint_search MCP |
| 数据馆 | 🔨 data_asset_registry（对标 OpenLineage）+ data_sources_registry + field_dictionary 257；**CH 246 表清单未挂接** | ⬜ CH 元数据采集器缺 | ✅ supply_sentinel.py+哨兵 yaml | ⬜ 无 |
| 文档馆 | ✅ rule_catalog 256 + directory_registry 88 + sop 九族 + 十图口径 | ✅ d1 index 族（batch_create_index_md 等） | ✅ d8_doc_sync 六 reconciler | ✅ docs/index.md |
| 规则馆 | ✅ gate_registry 170 + rule_catalog + ruling_registry + CAPCAN 378 | ✅ generate_rule_catalog / generate_gate_registry | 🔨 gate 五表关系未理清（盲区4） | ✅ rule_discovery MCP + capability_lookup |
| 管线馆 | ✅ tasks.yaml + TDM 138/194 + strategy_production_map + generator_registry | ✅ reconcile_generators.py | ✅ generate_skeleton_health.py（接电电表） | 🔨 无统一查询口 |
| 备份馆 | 🔨 asset_inventory（E 盘）+ infrastructure_registry 9 组件 + backup_config；**F/G/网盘/计划任务外溢无台账** | ✅ backup.ps1 六阶段 | ⬜ restore 演练/F→G 镜像缺 | ⬜ 仓外计划任务 ~25 个 register_*.ps1 无台账 |

防漂移件：✅ CREATE-GUARD+creation_tokens｜✅ HOT-FILE-BASE-FRESHNESS gate｜✅ safe_write_text CAS｜✅ REG-DRIFT-001 漂移检测器注册表（17+13）｜🔨 指纹机制缺（ROOR 无 generated_at）｜⬜ 馆藏覆盖双向 gate 缺。

## §2 关键发现（五条，改变方案级）

1. **统一资产索引已存在**：REG-INV-001 `data/asset_index/unified-asset-index.yaml`（33,249 文件四维分类，generate_asset_index.py 自动）——实物横轴底座现成，图书馆=在其上加层级导航+指纹，**不是从零建**。
2. **血缘登记表已对标 OpenLineage**：REG-DATAFLOW-001（sources/datasets/jobs 三实体）——管线馆真源现成。
3. **能力反查 API 已存在**：REG-CAPCAN-001（378 能力+capability_lookup.py 查询 API）——library_lookup 的前身，扩面而非新建。
4. **生成器编排器已存在**：reconcile_generators.py+generator_registry.yaml——全自动更新的调度底座现成。
5. **MCP 工具簇已存在 19 server**（gateway/governance/rule_discovery/blueprint_search/vector_memory 等，scripts/mcp/launcher.py 统一启停）——工具口只差"馆"这一层。

## §3 漂移现行（挖矿中撞见，图书馆必要性的直接证据）

| # | 现行 | 证据 |
|---|---|---|
| 1 | ROOR 自身无指纹无 generated_at，文件头 date 停在 2026-05-07，条目批注已到 09-18 | registry_of_registries.yaml 头部 vs summary 块 |
| 2 | 对齐清单头部"注册表 49 个" vs ROOR 实际 75 | alignment_checklist v1.6.0 vs ROOR |
| 3 | depgraph 本地 db 0 字节空壳误导（真源已迁 PG） | data/depgraph.db |
| 4 | 前端 web/pages 实测 53 html vs 官方口径"41 页" | src/zephyr/frontend/dashboard/web/pages/ |
| 5 | gate 家族五表关系未理清（gate_registry 170 vs rule_enforcement/_registry 91 vs in_process/fail_open/noqa_exempt） | 各注册表 |
| 6 | ROOR 记 capability_cards=22，实际 33 | ROOR Tier0 vs data/capability_cards/ |

## §4 盲区清单（未挖干证明，九项，补完才准谈封矿）

| # | 盲区 | 补法 |
|---|---|---|
| 1 | PG 侧实测缺（depgraph 9148 行数实测、industry_graph、migrations） | 只读查 PG |
| 2 | .runtime 运行时态资产未清点（resource_samples、strategy_decay_ledger 等活性证据） | 只读盘点 |
| 3 | 根目录杂项工作区（_journals/session_logs/strategy_archive/tmp/30/st-* 残留）+ .aidrafts/.worktrees 重复计数风险 | 只读盘点+定性 |
| 4 | gate 家族五表关系 | 读表+画关系 |
| 5 | scripts/governance 深层未开（d9/d10/d12/observability/repair/vms/oneoff）；generator_registry.yaml 条目数未实测 | 第二轮三扫 |
| 6 | MCP 深层（tool_contracts.yaml、19 server tool 总数、Auth/ACL） | 读配置 |
| 7 | 前端口径对账（53 vs 41） | 跑 check_frontend_map |
| 8 | Windows 计划任务外溢资产（~25 个 register_*.ps1 注册的仓外资产无台账） | 读计划任务建台账 |
| 9 | ROOR 自身新鲜度机制缺（需 generated_at/指纹字段） | 随骨架搭建补 |

## §4.1 盲区清偿结果（批3，2026-09-21，全程只读）

| # | 盲区 | 清偿结论（关键数字） | 状态 |
|---|---|---|---|
| 1 | PG 侧实测 | depgraph 库实为 **73 表资产总线**：nodes 12,107（module 3,854/test 3,551/config 3,503/script 1,088/blueprint 101）+edges 23,686；dataflow_jobs 1,757/datasets 76/edges 90；decision_nodes 213/edges 211（与 TDM yaml 138/194 并存，口径待对齐）；ig_* 产业链 13 表（ig_fact 264,072/ig_node 5,560/ig_edge 1,726）；gates 289/rule_bindings 73/domain_mapping 184/battle_map 341 步 114 边 | ✅ 清偿（ROOR 旧数 9,148 陈旧→漂移现行 §7-7） |
| 2 | .runtime 活性资产 | 总 15G：commit_queue 3.7G/52,190 文件（堆积冠军）、tmp 30,266 文件、gate_cache 7,496；活性层台账候选=data/runtime/ 6 个 lifecycle/ledger json（strategy_registry_snapshot 9/21 仍在刷新）+logs/resource_samples 11 jsonl+session_registry.json；~60 空目录+pt_* 7 月残骸 | ✅ 清偿（堆积型与台账型分开入馆） |
| 3 | 根目录杂项 | .aidrafts 47,605/.worktrees 38,486/根 tmp 25,521/.aidrafts_pool 3,660 未跟踪——asset index 白名单制（仅扫 src/scripts/tests/docs/config/data）**天然排除，无重复计数**；但 tools 937/vendor 138/acceptance 9/根 logs 480 也在视野外需补录；session_logs 33/34 已跟踪；4 处会话残骸（30/st-stkind-20260916/st-ff-last-20260918/test_dir）可归档 | ✅ 清偿 |
| 4 | gate 五表关系 | 关系定案：SSoT=in_process_gate_registry(113)+commit_gates/*.py GateSpec → generate_gate_registry.py 三源生成 → gate_registry.yaml(170，聚合派生，reconciler priority=830 自动重生成)；rule_enforcement/_registry(91)=独立平行家族（会话/管线 gate，命名零重叠）；fail_open_register(1,635 点/272 文件)=纯派生；noqa **同名异构双胞胎**（catalogs 28 marker vs config/governance 92 file）；tracked_write_allowlist(11)=SSoT | ✅ 清偿（169≠170 微漂移→§7-9） |
| 5 | governance 深层 | d9_knowledge 2py/d10_performance 1py(自述待建设)/d12_ai_hallucination 4py/observability 1/repair 7/vms 10/_tasks 3/_sync 3/oneoff 7；**generators/ 16py=生成器集中地**；generator_registry.yaml=26 条 SSoT（reconcile_generators 只读此表，含禁注册清单） | ✅ 清偿 |
| 6 | MCP 深层 | tool_contracts.yaml=**12 server/64 tools**（契约 SSoT，frozen 禁 AI 改）；config/mcp.json=12 server 注册+auth+ACL 三角色(reader/operator/admin)+每 server rate_limit+熔断降级；vector_memory=**8 collections**（decisions/code_context/lessons/knowledge/rules/blueprints/session_snapshots/execution_traces，write 强制 provenance）；blueprint_search=19 蓝图路由 | ✅ 清偿（契约/注册双向漂移+2 未登记 server→§7-8） |
| 7 | 前端对账 | check_frontend_map 实跑：**359 功能点，fail=0 warn=10**（R2 module_id 不在 features/manifest，集中 sq-*/pat-* 页）；页面 52 html；"41 页"=裁定转正口径——三口径并存需统一 | ✅ 清偿（口径统一归骨架搭建） |
| 8 | 计划任务外溢 | 脚本侧 21 个 register_*.ps1→24 任务名**全部存活**（脚本侧 0 孤儿）；系统侧 44 个 ZephyrAlpha_*+独立命名空间 \tilib_indicator_backfill_nightly；3 个无注册脚本疑手工注册（IOCheck-Monthly/BoardIndexRealtime/tilib）；4 个 OneShot 残留任务未清；NightlySentiment 任务在而脚本已 .disabled.bak=**假活**；desktop_shell 走 Startup .lnk 单列；generate_resource_profile_registry.py=中央登记生成器候选 | ✅ 清偿（台账层随管线馆建） |
| 9 | ROOR 指纹 | 非挖矿项，转 **P0 骨架搭建施工项**（generated_at+sha256+计数指纹字段） | 🔁 转施工项 |

## §5 挖干判定 v0.2（批3 后更新，SOP §6 对照）

1. 三扫收敛：**达成**——生产者/形态/消费者三视角+复扫完成；批3 新发现全部为**条目级**（既有支柱下的补录与漂移），**支柱结构零新增**。
2. 增长曲线：批2 的 5 条改变方案级发现后，批3 降级为条目级微增，曲线收敛。
3. 🌑 清点：**达成**——盘外做不了/来源不明项已点名（3 个手工注册任务、Startup .lnk 自启、异地备份 Owner 自办、网盘通道停更）。
4. 封顶声明：**草案成立，呈 Owner 批**——此后骨架增长=叶→实现；增枝须过停止判据三问并留理由；**演化重开条件**=新真源类型出现/新馆立项/MCP server 族扩容/PG 资产总线新表族。
5. **判定：骨架矿可封矿（呈批）。血肉矿开工前置=Owner 批封顶+骨架搭建施工令（资产 schema 定稿→INDEX 树 v0→指纹器→library_lookup v0）。**

## §6 下一步

1. 封顶声明呈 Owner 批（本件 §5）。
2. 批准后出骨架搭建施工令（走 construction_workflow_policy）：资产 schema 定稿 → INDEX 树 v0 → 指纹器（含 ROOR generated_at，即盲区9 转正）→ library_lookup v0。
3. 血肉矿分期开矿按总蓝图 §7（P1 代码馆+规则馆先行）。
4. 批3 移交即办小件（呈 Owner/维护班）：4 个 OneShot 残留任务清理；catalogs 下 .tmp.* 残留与 *_warn_result.json 清理；4 处会话残骸归档；sq-*/pat-* 十条 R2 module_id 补 manifest。

## §7 漂移现行增补（批3 新增六条，续 §3 编号）

| # | 现行 | 证据 |
|---|---|---|
| 7 | ROOR 记 depgraph 9,148 节点，PG 实测 12,107+edges 23,686 | ROOR Tier1 vs PG 实测 |
| 8 | MCP 契约/注册双向漂移：contracts 有 resource_optimization+mcp_gateway 未注册；mcp.json 有 red_blue_validator+clone_guard 无契约；文件系统另有 doc_guard/sentinel 两 server 两边均未登记 | tool_contracts.yaml vs config/mcp.json vs src/zephyr/integration/mcp/ |
| 9 | gate 计数三口径：55+113+1=169≠自称 170；PG gates 表又=289 | gate_registry.yaml / PG gates |
| 10 | noqa_exempt 同名异构双胞胎（catalogs 28 marker vs config/governance 92 file），一表一位假设被破 | 两文件对照 |
| 11 | NightlySentiment 计划任务在而脚本已被 .disabled.bak 禁用=假活 | schtasks vs scripts/data/run_nightly_sentiment.py |
| 12 | decisiongraph PG 213 节点 vs TDM yaml 138 节点两图并存、口径未声明 | PG decision_nodes vs config/trading_decision_map.yaml |

## §8 骨架矩阵增补（批3 新支柱件，均收编不新建）

- **PG depgraph 库=73 表资产总线**：代码馆 nodes/edges、数据馆 dataflow_*、管线馆 decision_*/battle_map_*、规则馆 gates/rule_bindings、产业链 ig_* 13 表——多馆 PG 侧真源同库，指纹器可一针连全部。
- 管线馆任务台账候选=generate_resource_profile_registry.py（74 耗资源实体 SSoT，命中几乎所有 schtasks 任务名）+Startup .lnk 单列登录自启类。
- 入口/工具支柱增补=vector_memory 8 collections（馆藏语义检索后端现成）+blueprint_search（19 蓝图路由）。
- 文档馆验收证据候选=acceptance/（F-CHAINMAP 截图 9 件）。
- 血肉矿补录清单（asset index 白名单外）：tools 937/vendor 138/acceptance 9/根 logs 480。
