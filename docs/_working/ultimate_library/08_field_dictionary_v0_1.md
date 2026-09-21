---
title: "终极图书馆 · 字段词典 v1.0（总账 schema，总攻 A 包冻结）"
ttl: task_bound
completes_when: 冻结已生效（Owner 授权总攻自裁 2026-09-21）；转正时升 permanent 并迁 docs/；字段变更走 §6 增枝制
date: "2026-09-21"
owner: "ZephyrAlpha-Owner"
session: "st-ulib-20260921"
---

# 字段词典 v1.0 —— 总账 schema（资产身份证，A 包冻结版）

> **回答 Owner 之问**：需要，而且字段设计分五层——①总账核心户籍字段（资产身份证）②分类型扩展字段③事件流水字段④指纹规范⑤馆页呈现字段。核心 9 字段 v1 草案已在蓝图 03 §3，本件扩为五层全量设计稿，**冻结权在总攻 A 包（Max 评审签认）**。
> 设计五原则（07 挖矿背书）：**Dublin Core 最小完备**（字段宁少勿滥）/ **MARC 双区分离**（机器控制区 vs 人读描述区）/ **OCI 内容寻址**（指纹即身份的一半）/ **SR 11-7 状态机**（生命周期字段带流转）/ **索书号原则**（书脊只写索书号，卡片留在目录里——文件只带一行 asset_id，15 字段留在总账）。

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
| 8 | status | 枚举 | active/stale/orphan/archived/**deceased(注销，见 §3.1 死亡证明)**/**ghost(馆有盘无)**/**blind(盘有馆无)** |
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

`event_id / asset_id / action(register|read|update|move|delete|audit) / actor(session_id) / gate_passed / ts / detail`——lookup_audit 与 safe_write 审计的收编目标，追责与回滚的依据。`action=delete` 的 detail=死亡证明引用（§3.1）。

### §3.1 死亡证明（注销登记制，Owner 2026-09-21 令）

**原则：注销不是消失，是换一种在编状态。** 总账条目永不删除，死者留 tombstone（本仓先例：裁定撞号 tombstone 解法、死信 q-0040"留档作废"）；会计不擦账只冲账、crates.io yank 不删包——同一法系。死亡证明=不可变记录，字段：

| # | 字段 | 说明 |
|---|---|---|
| 1 | death_cert_id | `DC-YYYYMMDD-NNNN` 流水号 |
| 2 | asset_id | 死者身份证号（永不复用） |
| 3 | final_fingerprint | 死前最后指纹——证明"它原来是什么"，防删错无法举证 |
| 4 | disposition_action | destroyed / archived_to(X) / absorbed_into(asset_id) / ttl_expired |
| 5 | cause_of_death | 枚举：重复/退役/清缴未收编/TTL 到期/误建… |
| 6 | authority | 处置预授权批件号（=核心字段 11 的兑现；**无授权不得签发死亡证明**） |
| 7 | evidence_path | 盘点卡/呈批件/三证链接（机械判定门铁律） |
| 8 | executed_by/at | 执行会话+时戳 |
| 9 | resurrection | 可否复活+条件（封矿≠死亡，SOP 同款） |

保管级=**permanent**（审计链最不能丢的一类）；死亡证明本身不注销——元层级由登记流水兜底。

## §3.3 全局登记并发制（Owner 令：必须支持多 AI 同时改总账）

**原则：账本并发=数据库原生能力（MVCC/行级锁/唯一约束），不自研锁。** YAML 之疼（capability 册 CAS 五连竞态）的根因=文件当账本；总账在 PG 后此疼自愈，文件态注册表降级为生成视图。六道保障：

| # | 机制 | 实现 |
|---|---|---|
| 1 | **事务原子** | event INSERT 与状态 UPDATE 同事务提交——"不登记就没法改变状态"的机械形态 |
| 2 | **权限收口（绕不过的账本闸）** | app 数据库角色 REVOKE 表直写、只 GRANT EXECUTE 馆员函数 `librarian.act()`——写路径物理唯一，DB 层对应 L1 硬闸 |
| 3 | **行级锁+乐观指纹基线** | 同条目并发=行级自动串行；调用方带 expected_fingerprint，不匹配即拒（行级 CAS，语义同 git rebase：重读+重放） |
| 4 | **事件只追加** | 并发竞跑时两条事件全留（ts+actor 排序可回放真实交错）；只有 state 行是 last-writer-wins，历史永不丢 |
| 5 | **唯一约束幂等** | UNIQUE(asset_id)/UNIQUE(home,generation)——同文件重复登记，第二次冲突即"它已存在"，语义同 DUPLICATE_TASK_BLOCKED |
| 6 | **快慢分离** | 登记走 PG 并行吸收（不排队）；排队只给慢资源 git 落盘（serializer）——施工并发无上限、落盘串行、入账并行，三层各管一段 |

三层并发分工（与既有件对接）：**claim 系统管施工层**（文件级互斥，已有）→ **commit_queue 管落盘层**（串行化慢资源，已有）→ **PG MVCC 管账本层**（并行登记，B1 包建）。

### §3.2 盲册本身是资产

每轮盲册报告=一个 asset_id（retention_class=long），入馆归档——清缴的账本本身也在编。

## §4 馆页呈现字段（生成器产出的三视图各显示什么）

- **L1 馆页**：馆名/条目数/指纹/构建时戳/子目录锚点（≤100 行）
- **L2 域页**：域+计数+条目卡列表+blind/ghost 红标
- **L3 资产卡**：核心 15 字段全量+kind 扩展+最近事件 3 条

## §5 收编映射（净零：不重复造字段）

既有登记表已有的字段，总账**存指针不存副本**：CAPCAN 的 capability→ai_contract 源；gate_registry 的 own_scope→tags；dataqa 报告→table 扩展源；resource_profile→task 扩展源。总账=字段的家谱，不是字段的新家。

## §6 冻结与变更

总攻 A 包评审冻结 **v1.0** → 之后字段新增=增枝制（停止判据三问+Owner 批）；schema 演进只增不改语义（旧条目永不失效）。

## §7 索书号规范（文件表头：一行，越简单越好——Owner 2026-09-21 令）

**原则：书脊只写索书号，卡片留在目录里。** 15 字段是目录卡（在总账），文件只带**一行索书号**（约 60-80 字节）：

| 格式 | 表头形态 |
|---|---|
| .md/.yaml | frontmatter 新增必填键一行：`asset_id: FILE:docs/...` |
| .py 等代码 | 文件头注释一行：`# asset: MOD:src.zephyr.xxx` |
| csv/json 等受限文本 | 格式允许处一行；不允许（如 csv 表头前不能插行）→ 退化为哈希反查 |
| 二进制/密钥（.env 等） | **不嵌表头**——内容哈希反查（OCI digest：内容即身份，采集器算 sha256 查总账） |

**双向查找**：馆→文件=总账 home 字段；文件→馆=表头 asset_id（首选）或内容哈希反查（兜底）；两者皆无=**blind（编外）**。强制：出生时由 scaffold/CREATE-GUARD 注入模板；LIBRARY-COVERAGE 把"无索书号"并入 blind 红线。

## §8 编外名册与临时专区（"永久解决文件混乱"的机制判定——Owner 之问）

三件套闭合循环：

1. **无籍不生**（出生闸）：CREATE-GUARD 在出生点拦截，漏网率趋零；
2. **盲册清缴**（盘点权）：blind 名册=机械扫描自动产出（路径/名字/大小/首见时间全列出），专项三处置——**收编**（补登记）/ **归档**（移入专区）/ **注销**（签发死亡证明 §3.1，无授权不删）；总攻后首轮全量盲册=存量清缴的开工清单，且盲册报告本身入馆（§3.2）；
3. **编外有编**（临时专区）：临时文件/临时文档/归档/临时代码在图书馆有**专属临时区**，持二级身份证（`retention_class=temp`+TTL），到期自动处置——**编外不是无身份，是另一种身份**。

**判定：能永久解决"文件无编制/混乱"问题**——出生闸（漏网趋零）+盲册（兜底现形）+专区（编外有编）闭合了循环，且全程机械可证（符合机械判定门铁律）。两条诚实边界：①存量须一次性专项清缴（现 11.5 万未跟踪文件）；②临时区必须 TTL 自动清，否则编区变垃圾山。
