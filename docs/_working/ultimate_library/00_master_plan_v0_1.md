---
title: "终极图书馆总蓝图 v0.1 —— AI-first 全资产分层目录+防漂移机制"
ttl: task_bound
completes_when: 骨架矿封矿判定呈 Owner+P0 骨架搭建（schema/INDEX v0/library_lookup v0）施工令出单
date: "2026-09-21"
owner: "ZephyrAlpha-Owner"
session: "st-ulib-20260921"
status: "draft"
---

# 终极图书馆 · 总蓝图 v0.1

> **一句话**：全项目单入口、层级化、AI-first 的资产目录 + 防漂移防幻觉机制。给 AI 用，不是给人看。
> **姊妹件**：挖矿台账=[02_skeleton_mining_ledger_v0_1.md](02_skeleton_mining_ledger_v0_1.md)；业界调研=[01_external_research.md](01_external_research.md)。
> **上位法**：宪法 §4 净零 / §6 上下文预算 / §9 运维红线；[skeleton_mining_policy.md](../../01_policies_and_standards/sop/mining_sop/skeleton_mining_policy.md)（骨架挖矿 SOP）。

## §0 Owner 定调（2026-09-21，原文要点）

1. 图书馆**全套方便 AI**：最高效查询、最高效看到；彻底防幻觉、防漂移。
2. 全项目所有东西全部纳入（含备份系统/F 盘/G 盘等盘外资产）；临时文件与 working 除外。
3. **全自动化**更新 + 全自动化对齐（双向对齐、五角星对齐、各种对齐）。
4. 先骨架后血肉：骨架先挖矿，挖干判定通过才准开血肉矿。

## §1 定位铁律（四条，违反即方案作废）

1. **图书馆=生成视图，不是真源**。只存指针+摘要+指纹；真源永远留在资产本体（YAML/DB/CH/代码）。
2. **全部清单生成器产出**（宪法 §9.5）。馆页=构建产物（dbt manifest 同源模式）；机器可采的绝不手填（DataHub 铁律）；人填字段最小化并配覆盖率门禁。
3. **净零收编**（宪法 §4）：不建平行注册表、不新造对齐算法。每个新件必须声明收编对象（§4 收编地图）；骨架盘点证实原料约八成现成，缺的是"统一 schema+分层导航+指纹+唯一入口"。
4. **AI-first 读取契约**：分层渐进披露 L0 总目→L1 分馆→L2 域→L3 条目卡（复用 capability_cards 已验证的 L0-L3 范式）；每页头部必带 条目数/指纹/构建时戳/真源锚点；检索必经 library_lookup 留审计（与 capability_lookup 同构）。

## §2 馆藏结构 v1（七馆两区，Owner 2026-09-21 扩容令："制度、规则、git 路上一切设备全部入馆"）

纵轴=内容域（复用 functional_domain_registry 83 域），横轴=实物类型标签，交叉由生成器产出。单入口=INDEX 树。**类目总清=[05_master_inventory_v1.md](05_master_inventory_v1.md)（清单的清单：十维度 51 类有清单件+9 缺口全落总攻）。**

| 馆 | 收什么 | 既有真源（盘点实证） | 既有生成器/机制 |
|---|---|---|---|
| 制度馆 | 宪法/规则 86/裁定 384/议题 761/标准/政策/SOP 九族/门位/冻结契约 38/错误码 788/词汇三层 | rule_catalog、ruling_registry、architecture_issue_registry、risk_tier、freeze_manifest、error_code、术语三层+field_dictionary 257 | generate_rule_catalog |
| 闸门馆 | 门禁全家族（55 pre-commit+113 in-process+91 gate_engine+fail_open 1,635+noqa+allowlist）+**git 提交链全部设备**（网关/队列/serializer/锁 claim/会话心跳/worktree/stash 隔离/POST-COMMIT-GUARD/hooks/应急通道）+安全设备（LSG/kill_switch/secrets/红蓝 24+44） | in_process_gate_registry（SSoT）+GateSpec、gate_registry 聚合、git_commit.py/commit_queue/lock_files/session_worktree 源码与配置、REG-RB-001/002 | generate_gate_registry（reconciler 830 重生成） |
| 代码馆 | 源码/模块/脚本/蓝图/schema/迁移/测试 | depgraph PG 12,107 节点、script-manifest 991、module_id 74、blueprint 体系 | generate_project_depgraph.py |
| 数据馆 | CH 表/数据源/通道/字段+因子/策略/指标/形态/模型登记 | data_asset_registry、data_sources_registry、field_dictionary、哨兵、factor 175/strategy 161/indicator 138/pattern 254 | supply_sentinel.py；（缺）CH 采集器 |
| 管线馆 | 决策图/血缘/调度/排班/计划任务/守护/服务/MCP/模型路由 | TDM 138/194、decisiongraph 213、dataflow 1,757、tasks.yaml、resource_profile 74、MCP 契约 12/64 | reconcile_generators.py、generate_skeleton_health.py |
| 文档馆 | docs 手写文档/全景图十图/报告/任务卡/验收证据/能力卡 33 | rule_catalog、directory_registry 88、十图口径、capability_cards | d1 index 族、d8_doc_sync |
| 基建与备份馆 | 基础设施 9 组件/盘 D-E-F-G/冷储/网盘/数据库实例/备份链/恢复演练 | asset_inventory、infrastructure_registry、backup_config、backup.ps1 | backup.ps1；（缺）全盘盘点+checksum+restore 演练 |
| 运行时区（半开） | 活性台账入馆（6 lifecycle json/资源采样/审计流），堆积型只计指标 | data/runtime/、resource_samples、governance.db | — |
| 临时区（排除） | .runtime 堆积/tmp/docs/_working/根目录杂项 | 只入总账作 blind 域名点，不建馆页 | — |

## §3 入口三形态（一体三视图，同一生成器产出）

1. **文件形态**：ROOR 升级为分层 INDEX 树（AGENTS.md 格式做 L0 总目；L1 六馆；L2 域；L3 条目卡）。
2. **工具形态**：library_lookup（MCP）——"X 在哪/是什么/新鲜吗"一次调用；收编 capability_lookup（378 能力）+blueprint_search+rule_discovery 三既有 MCP 口为馆内检索后端。
3. **仪表盘形态**（殿后）：馆页照抄 TDM 页交互。

## §4 收编地图（净零声明 v0）

| 既有件 | 收编角色 |
|---|---|
| ROOR（75 REG-*，summary 机生） | 馆级总目录骨架；补指纹字段后=INDEX L1 |
| unified-asset-index（REG-INV-001，33,249 文件四维自动） | 实物横轴底座；图书馆在其上加层级导航，不从零建 |
| registry_master_index（REG-CATALOG-001，55 条自动） | 规则馆+文档馆目录层 |
| CAPCAN（REG-CAPCAN-001，378 能力+查询 API） | library_lookup 的前身——扩面而非新建 |
| capability_cards（REG-SKILL-001，33 卡） | 渐进披露范式真源（L0-L3） |
| align_all.py（十图口径）+align_panoramas+align_battle_map | 周对账执行器（原样收编） |
| reconcile_generators.py+generator_registry.yaml | 全自动更新的调度底座（原样收编） |
| supply_sentinel+data_supply_sentinel.yaml | 数据馆活性层 |
| generate_skeleton_health.py | 管线馆接电电表 |
| REG-DRIFT-001 漂移检测器注册表（17 existing+13 new，gov_drift） | 防漂移检测器的登记与调度真源 |
| MCP 簇 19 server（scripts/mcp/launcher.py） | 工具口承载 |
| greatwall 五角星拓扑（"任意两任务成果互相可达"） | 跨馆对齐语义：任意两馆条目互达 |

## §5 防漂移四件套（防幻觉机制）

1. **指纹**：每条目 sha256+mtime+HEAD+计数+构建时戳。补实证盲区：ROOR 自身无 generated_at/指纹（文件头 date 停在 2026-05-07，条目批注已到 09-18）；对齐清单头部计数 49 vs 实际 75 的漂移即此病。
2. **未登记即红**：CREATE-GUARD/depgraph/TRANSLATION-COVERAGE 既有 gate 家族扩面到馆藏条目——盘上有而馆中无=红，馆中有而盘上无=红（双向）。
3. **引用必经**：AI 取证走 library_lookup 留审计；一切报告必须带数据时戳+指纹（防 dataqa R4 型"报告当晚即腐化"复发）。
4. **周对账**：收编 align_all（十图）/哨兵/skeleton_health/活性审计为统一对账窗；双向对齐=馆↔资产本体互查；五角星对齐=跨馆互达性检查。

## §6 全自动更新与对齐

- **增量=事件驱动**：提交即触发派生馆页重建（经 reconcile_generators/post-commit 钩子），遵守永久系统四要素（自动触发/运行/维护/关闭；事件触发，禁 cron 睡眠循环——低频全量兜底走既有排班窗）。
- **对齐全收编**：图书馆不写新对齐算法，只做统一调度+结果展示；十图/哨兵/电表/五角星全部挂进统一对账窗。

## §7 分期与当前状态

- **P0 骨架期（当前）**：骨架挖矿（02 台账，判定=未封矿，九盲区）→ 骨架搭建（资产 schema 定稿 → INDEX 树 v0 → library_lookup v0 → 指纹器）。
- P1=代码馆+规则馆（真源最成熟）；P2=数据馆+管线馆；P3=备份馆+仪表盘+MCP 口转正。
- **封矿前禁开血肉矿**（逐馆逐条目录入=P1+ 的事）。
- 施工前义务清单：RULE-DEPGRAPH 登记（建 .py 时）、新 .py 大白话简介、CREATE-GUARD token（本批已办 3 枚）、RULE-CAPABILITY-LOOKUP 留审计。

## §8 拍板项状态

| # | 事项 | 状态 |
|---|---|---|
| 1 | 立项定性：大节点+骨架挖矿先行 | Owner 已令开工（2026-09-21） |
| 2 | 排除域=.runtime/_working 不入馆藏 | 初稿采纳，待 Owner 终批 |
| 3 | 入口优先级：文件树+library_lookup 先行，仪表盘殿后 | AI-first 定调下自洽，待确认 |
| 4 | 备份馆缺口授权（F→G 镜像/restore 演练自动化） | 未拍板 |
| 5 | 管线三断点（日循环接电/pf_alloc/模拟盘）归属 | 暂留统一施工方案 v1.0，未拍板 |
