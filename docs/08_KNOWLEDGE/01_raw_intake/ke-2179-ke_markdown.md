---
module_id: KE-2087--------markdown-004
status: active
title: 3.2.2 KE 物理存储格式（Markdown）
category: module_blueprint
ttl: permanent
---

# 3.2.2 KE 物理存储格式（Markdown）

3.2.2 KE 物理存储格式（Markdown）

每条 KE 的 canonical 物理形态是一个独立的 `.md` 文件，存储在 `docs/08_knowledge/` 下。格式包含两个区：

1. **YAML frontmatter**（机器可消费元数据 + 人类随手可看）——从 §3.2 的 28 字段 Schema 中选取"文件级必读"字段
2. **Markdown body**（知识正文）——结构化段落模板

##### 两区字段分工

| 字段 | 落位 | 理由 |
|------|:---:|------|
| `ke_id` | frontmatter | 文件级标识——AI 扫一眼 frontmatter 就知道这是哪条 KE |
| `title` | frontmatter | 标题——人类/AI 快速判断"这条知识讲什么" |
| `body` | **body** | 知识正文——Markdown 正文区，结构化段落 |
| `category` | frontmatter | 15 类双轨分类（§3.8） |
| `domain` | frontmatter | 业务域（对齐 PS-STD-004 §5） |
| `layer` | frontmatter | 架构层（对齐 `triage.py` VALID_LAYERS） |
| `source_type` | frontmatter | 来源类型——可追溯 |
| `source_path` | frontmatter | 来源文件绝对路径——可审计 |
| `status` | frontmatter | 10 状态机当前状态（§3.3） |
| `quality_score` | frontmatter | G2 Triage 质量评分 |
| `priority` | frontmatter | P0~P3 优先级 |
| `tags` | frontmatter | 标签列表（YAML list） |
| `ttl` | frontmatter | 有效期 |
| `half_life_days` | frontmatter | 半衰期（天）——0=永不过期 |
| `created_at` | frontmatter | 创建时间（ISO 8601） |
| `updated_at` | frontmatter | 最后更新时间 |
| `last_verified_at` | frontmatter | 最后验证时间 |
| `depends_on_ke` | frontmatter | 依赖的其他 KE-ID |
| `supersedes_ke` | frontmatter | 取代的旧 KE-ID |
| `usage_count` | **SQLite only** | 运行时计数器——由 `recall()` 实时更新，不在文件中 |
| `adoption_count` | **SQLite only** | 运行时计数器——由 `learn()` 实时更新，不在文件中 |
| `helpfulness_score` | **SQLite only** | 运行时滑动窗口（最近 10 次）——不在文件中 |
| `last_used_at` | **SQLite only** | 运行时时间戳 |
| `_locked` | **SQLite only** | 内部锁标记——禁止暴露给文件层 |

> **设计原则（对标 §6.12 AI-First Audience Principle）**：frontmatter 选择的边界是"这条字段离开这个文件之后还有没有独立价值？"——有 → 放 frontmatter（如 category、source_path）；没有（如 usage_count 是运行时计数器）→ 放 SQLite only。禁止把运行时字段写进文件——下次 `parse_frontmatter` 会读到过期数据。

##### 完整文件模板

```yaml
---
