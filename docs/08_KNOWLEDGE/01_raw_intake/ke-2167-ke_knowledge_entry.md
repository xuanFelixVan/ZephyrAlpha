---
module_id: KE-2075------ke---knowledge-entry--006
status: active
title: 3.2 知识条目（KE — Knowledge Entry）Schema
category: module_blueprint
ttl: permanent
---

# 3.2 知识条目（KE — Knowledge Entry）Schema

3.2 知识条目（KE — Knowledge Entry）Schema

每个知识条目对应一条可被语义检索的知识。核心字段：

| 字段 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| `ke_id` | str | ✅ | 全局唯一标识，格式 `KE-{NNN}`（3位递增编号），代码真源在 `kb_repo.py` |
| `title` | str (≤100) | ✅ | 知识标题 |
| `body` | str | ✅ | 知识正文（Markdown 格式） |
| `category` | enum | ✅ | 知识分类：15 类双轨体系（§3.8）。**beta 迁移**（KB-INF-0022）：当前仍沿用旧 10 类枚举→逐步迁移至 Track A（8类）+ Track B（7类） |
| `domain` | enum | ✅ | 业务域：10域枚举（对齐 PS-STD-004 §5） |
| `layer` | enum | ✅ | 架构层：14层枚举（对齐 `triage.py` VALID_LAYERS） |
| `source_type` | enum | ✅ | 来源类型：`adr` / `blueprint` / `session_log` / `candidate_pool` / `external_paper` / `github_repo` |
| `source_path` | str | ✅ | 来源文件绝对路径 |
| `status` | enum | ✅ | KE 状态：10状态机（§3.3） |
| `quality_score` | float [0.0-1.0] | ✅ | 质量评分（G2 Triage 产出） |
| `priority` | enum | ✅ | 优先级：`P0`~`P3` |
| `tags` | list[str] | ✅ | 标签列表（对齐 MOD-TASK_SYSTEM 5轴标签：fn/ly/md/st/mo） |
| `audit_chain` | list[str] | ✅ | 审计链：记录经过的审计模型和结论 |
| `ttl` | str | ✅ | 有效期：`permanent` / `30d` / `7d` / `session` |
| `half_life_days` | int | SHOULD | 知识半衰期（天），用于衰减计算。0=永不过期 |
| `created_at` | datetime | ✅ | 创建时间 |
| `updated_at` | datetime | ✅ | 最后更新时间 |
| `last_verified_at` | datetime | SHOULD | 最后验证时间 |
| `usage_count` | int | ✅ | 被 `recall()` 检索到的次数。默认 0 |
| `adoption_count` | int | ✅ | 被检索后 AI 实际采纳的次数。由 `learn(event_type="ke_adopted")` 递增。默认 0 |
| `helpfulness_score` | float [0.0-1.0] | ✅ | 采纳后任务成功率（滑动窗口最近 10 次）。默认 0.5 |
| `last_used_at` | datetime | SHOULD | AI 最后一次检索/使用此 KE 的时间 |
| `depends_on_ke` | list[str] | SHOULD | 依赖的其他 KE-ID |
| `supersedes_ke` | list[str] | SHOULD | 取代的旧 KE-ID |
| `_locked` | bool | ✅ | 锁定状态（true=不可修改，需走决策记录解锁） |
| `valid_from` | date | OPTIONAL | 知识生效起始日期（Track B 金融KE专用——如"Q1 财报季策略"仅在 01-01~03-31 有效） |
| `valid_until` | date | OPTIONAL | 知识失效日期（到期后自动 DEPRECATED，检索时过滤掉已过期的 KE） |
| `phase_context` | enum | SHOULD | **Phase 5 stubs (#25)**——知识阶段性有效标记：`bootstrap`/`development`/`stabilization`/`production`/`retirement`。检索时按当前项目阶段过滤。当前所有 KE 默认全局有效——Phase 5 启用阶段感知注入。 |
| `auto_refresh_trigger` | bool | SHOULD | **Phase 4 预留**——源文件变更时自动触发 KE 重审（§7.6.5）。默认 false。当前半衰期公式基于纯数学衰减，该字段启用后将叠加"源文档变更→KE 标记 NEEDS_REVIEW"的信号管线 |
| `git_branch` | str | OPTIONAL | **Phase 5 预留**——KE 所属 Git 分支。默认 `main`。跨分支开发时标记 KE 分支归属，`kb_repo.merge_knowledge(source_branch)` 合并分支时自动处理跨分支 KE |
| `cross_branch_status` | enum | OPTIONAL | **Phase 5 预留**——跨分支同步状态枚举桩：`branch_local` / `merged_to_main` / `conflict_on_merge`。分支本地 KE 先标记 `branch_local`，合并到 main 后变为 ACTIVE |

**字段稳定性分级**（对标 CTR-001~CTR-006 `stability: locked-5yr`）：

KE Schema 的 31 个字段同样需要稳定性承诺——beta/3 代码会依赖这些字段名和类型，随意变更会破坏下游消费者。

| 分级 | 字段 | 含义 | 变更规则 |
|:---:|------|------|---------|
| **frozen** | `ke_id` `category` `domain` `layer` `source_type` `status` `priority` `quality_score` `ttl` `created_at` `_locked` | 核心契约字段——代码强依赖其类型和枚举值 | 3年内不删不改类型。允许追加新枚举值但禁止删除旧值 |
| **extendable** | `title` `body` `source_path` `tags` `audit_chain` `depends_on_ke` `supersedes_ke` `updated_at` `last_verified_at` `auto_refresh_trigger` `git_
