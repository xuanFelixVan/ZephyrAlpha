---
title: "终极图书馆 · 骨架挖矿台账 v0.1"
ttl: task_bound
completes_when: 盲区九项清零+三重扫描第二轮零新增（封顶声明落盘呈 Owner）
date: "2026-09-21"
owner: "ZephyrAlpha-Owner"
session: "st-ulib-20260921"
status: "active"
---

# 骨架挖矿台账 v0.1（依 skeleton_mining_policy 执行）

> **挖矿对象定义**：图书馆骨架 = 六馆 × 四支柱（真源映射/生成器/对账活性/入口工具）+ 防漂移件。骨架条目=**支柱件**，不是资产全集——资产全集（逐文件逐表逐指标录入）是血肉矿，封矿前禁开。
> **批次志**：批1=考古批（2026-09-20 全项目完成度调查+两路全网调研）；批2=三重扫描批第一轮（2026-09-21：ROOR 全量 75 / 生成器普查 30 / 对账机制 8 / 入口面 / 素材计数）。

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

## §5 挖干判定（SOP §6 五判据对照）

1. 三扫收敛：**未达**（生产者扫=生成器普查第一轮已跑；形态扫=入口/图已跑；消费者扫=盲区 4/6/7 未跑）。
2. 增长曲线拉平：**未达**（批1→批2 撞出 5 条改变方案级发现，曲线陡升）。
3. 🌑 清点：**未达**（备份馆盘外资产 D/E/F/G 实盘未清点）。
4. 封顶声明：**未到时机**。
5. **判定：骨架矿不封矿。九盲区补完+三重扫描第二轮零新增 → 写封顶声明 → Owner 判定封矿。封矿前禁开血肉矿。**

## §6 下一步（按序，均为只读挖矿，零施工）

1. 补盲区 1/4/5/7（仓内可查）→ 2. 补盲区 8（计划任务台账）→ 3. 补盲区 2/3（.runtime+根目录定性）→ 4. 三重扫描第二轮，零新增则写封顶声明呈 Owner → 5. 封矿后骨架搭建：资产 schema 定稿 → INDEX 树 v0 → 指纹器 → library_lookup v0（施工令另立，走 construction_workflow_policy）。
