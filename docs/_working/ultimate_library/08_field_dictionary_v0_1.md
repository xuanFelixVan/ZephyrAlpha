---
title: "终极图书馆 · 字段词典 v0.1（总账 schema 设计稿）"
ttl: task_bound
completes_when: 总攻 A 包评审冻结为 v1.0 后转正式；字段变更走增枝制
date: "2026-09-21"
owner: "ZephyrAlpha-Owner"
session: "st-ulib-20260921"
---

# 字段词典 v0.1 —— 总账 schema 设计（资产身份证）

> **回答 Owner 之问**：需要，而且字段设计分五层——①总账核心户籍字段（资产身份证）②分类型扩展字段③事件流水字段④指纹规范⑤馆页呈现字段。核心 9 字段 v1 草案已在蓝图 03 §3，本件扩为五层全量设计稿，**冻结权在总攻 A 包（Max 评审签认）**。
> 设计四原则（07 挖矿背书）：**Dublin Core 最小完备**（字段宁少勿滥）/ **MARC 双区分离**（机器控制区 vs 人读描述区）/ **OCI 内容寻址**（指纹即身份的一半）/ **SR 11-7 状态机**（生命周期字段带流转）。

## §1 核心户籍字段（assets 表，每个资产一条身份证）

**机器控制区**（程序读写，禁止手填）：

| # | 字段 | 类型/约束 | 说明 |
|---|---|---|---|
| 1 | asset_id | `KIND:稳定派生键` | 身份证号。**永不复用、永不改**（OCI digest 纪律）；改名/搬家只改 home |
| 2 | kind | 枚举 12 类 | module/file/table/registry/doc/task/mcp_tool/backup/pipeline_node/factor_strategy/prompt_agent/infra |
| 3 | home | 结构化定位 | `file:路径` / `pg:表` / `ch:库.表` / `schtasks:任务名` / `mcp:server.tool` / `startup:lnk` |
| 4 | family_id | 可空 | WEMI 族号：同一逻辑资产的多载体挂一族（策略 X 的代码/配置/回测/报告） |
| 5 | fingerprint_sha256 | hex | 内容规范形哈希（LF 规范形，CAS 同源） |
| 6 | fingerprint_aux | 结构 | size+mtime+HEAD+条目数 |
| 7 | built_at / generation | 时戳+整数 | 采集时戳+扫描代次（无指纹的记录=不可引用） |
| 8 | status | 枚举 | active/stale/orphan/archived/**ghost(馆有盘无)**/**blind(盘有馆无)** |
| 9 | owner_domain | 外键 | functional_domain 83 域（Backstage owner 必填纪律） |
| 10 | retention_class | 枚举 | permanent/long/task_bound/temp（ISO 15489 保管期限表） |
| 11 | disposition_authority | 可空引用 | 处置预授权：Owner 批件号或规则 ID（注销权的前提） |
| 12 | registered_at/by | 时戳+会话 | 登录簿流水（accession register：先领号后上架） |

**人读描述区**（可 AI 辅助填充，带新鲜度）：

| # | 字段 | 说明 |
|---|---|---|
| 13 | title / one_liner | 名称+一句话 |
| 14 | ai_contract | "这是什么+怎么读+读取成本"——AI 检索后第一眼看到的接地摘要 |
| 15 | tags | 实物类型标签（横轴），收编既有登记表的 own_scope 等字段 |

## §2 分类型扩展字段（每 kind 3-6 个，总账 JSON 字段或侧表）

| kind | 扩展字段 |
|---|---|
| table | row_count / max_date（业务新鲜度）/ last_write / sentinel_state / pit_policy |
| module | language / entry_points / test_refs / consumers_count |
| task | schedule / last_run / last_exit / next_run / orphan_flag（OneShot 残留检测用） |
| registry | entry_count / generator_id / regen_command / last_regen |
| mcp_tool | server / tool_count / auth_role（reader/operator/admin） |
| backup | volume_bytes / last_verified / restore_drill_date / mirror_state |
| factor_strategy | lifecycle：candidate→trial→production→retired（SR 11-7 状态机+BRAIN 式流转，补 L1/L2 缺口） |
| prompt_agent | version（不可变）/ label（production/staging，Langfuse 式）/ model / eval_set_ref |
| infra | instance_type / capacity / watermark_ts |

## §3 事件流水字段（events 表，六流程各记一行，不可变追加）

`event_id / asset_id / action(register|read|update|move|delete|audit) / actor(session_id) / gate_passed / ts / detail`——lookup_audit 与 safe_write 审计的收编目标，追责与回滚的依据。

## §4 馆页呈现字段（生成器产出的三视图各显示什么）

- **L1 馆页**：馆名/条目数/指纹/构建时戳/子目录锚点（≤100 行）
- **L2 域页**：域+计数+条目卡列表+blind/ghost 红标
- **L3 资产卡**：核心 15 字段全量+kind 扩展+最近事件 3 条

## §5 收编映射（净零：不重复造字段）

既有登记表已有的字段，总账**存指针不存副本**：CAPCAN 的 capability→ai_contract 源；gate_registry 的 own_scope→tags；dataqa 报告→table 扩展源；resource_profile→task 扩展源。总账=字段的家谱，不是字段的新家。

## §6 冻结与变更

总攻 A 包评审冻结 **v1.0** → 之后字段新增=增枝制（停止判据三问+Owner 批）；schema 演进只增不改语义（旧条目永不失效）。
