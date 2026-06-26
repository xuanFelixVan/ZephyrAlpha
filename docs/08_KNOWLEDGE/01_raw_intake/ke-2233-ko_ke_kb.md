---
module_id: KE-2140
status: active
title: 3.6 KO→KE→KB 三级知识漏斗
category: module_blueprint
ttl: permanent
---

# 3.6 KO→KE→KB 三级知识漏斗

3.6 KO→KE→KB 三级知识漏斗

**问题**：Session Log 里 AI 说"我今天发现 ruff check 报 E501..."——这是一条原始观察（KO）。不该直接进入知识库——需要先结构化，再提炼，最终形成可复用的规则。

**对标 ITIL DIKW 金字塔的量化投射**：

```
DIKW 金字塔                ZephyrAlpha 三级漏斗           数量约束
──────────                ──────────────────           ────────
Wisdom  (智慧)           →  KB  (Knowledge Base)       ≤ 10 条
                            系统级规则——跨模块生效、
                            写入 JUSTFILE / AGENTS.md
                              "本项目永远用 ruff 不用 pylint，用 mypy 不用 pyright"

Knowledge (知识)         →  KE  (Knowledge Entry)      ≤ 30 条
                            结构化知识条目——标注了
                            分类/领域/层/标签/半衰期
                              "ruff 选型理由：比 pylint 快 10-100x + pyproject.toml 原生集成"

Information (信息)       →  KO  (Knowledge Observation) ≤ 50 条
                            从 Session Log / ADR 提取的
                            原始观察——未经结构化的第一手记录
                              "Session 2026-05-02：ruff E501 错误手动 fix 耗时 2 分钟"
```

**漏斗流转规则**：

```
KO (50条上限)                     KE (30条上限)                  KB (10条上限)
───────────                      ───────────                    ──────────
创建条件：G5 Extract              升格条件：≥3个 KO              升格条件：≥5个 KE
         从SessionLog/ADR/BP               指向同一主题的                或者Owner主动
         中自动识别知识块                    KO被人工/AI聚合              声明升格
         │                                │                           │
         │ 同类KO聚合                     │ 提炼为可复用规则            │
         ├────────────────→               ├──────────────→            │
         │   ≥3条 → 升格                  │    ≥5条 → 升格             │
         │                                │                           │
         ▼                                ▼                           ▼
    标记 KO-{NNN}                     标记 KE-{NNN}               标记 KB-{NNN}
    状态：DRAFT→REVIEWED              状态：INDEXED→VERIFIED      状态：ACTIVE
    存储：08_knowledge/drafts/         存储：08_knowledge/分类      存储：AGENTS.md /
    TTL：30d（过期自动清理）             + ChromaDB + SQLite            justfile /
                                        TTL：permanent                .cursor/rules/
                                                                      TTL：permanent
```

**升格阀值**：
- KO→KE：≥3 条 KO 指向同一主题（由向量聚类检测）→ 触发 D0 四轮知识管理流水线（011 GLM→022 Kimi→033 Qwen→044 Opus）自动聚合为 KE
- KE→KB：≥5 条 KE 在同一领域（`category` + `domain` + `layer` 交叉匹配）→ 触发 KB 升格评审（Owner 审批）

**淘汰规则**：
- KO：30 天内未升格为 KE → 自动清理（不是所有观察都值得保留）
- KE：升格为 KB 后 → SUPERSEDED（终态）
- KB：永不过期，但可被新版 KB 取代（SUPERSEDED）

> **对标**：ITIL Knowledge Management — DIKW 金字塔（Data→Information→Knowledge→Wisdom）要求每一层的升格有明确的阀值和流程。KO→KE→KB 是对 DIKW 的量化投射——从"模糊观察"到"可执行规则"的渐进化。
> 通俗解释：一条知识从"AI 随口说了一句"到"写入项目强制规则"要过三道门槛。第一道（KO）：记下来，"我在 Session #12 发现 ruff 很快"。第二道（KE）：整理好，"ruff 比 pylint 快 10-100 倍，所以选 ruff"。第三道（KB）：写入铁律，"本项目只用 ruff，不准用 pylint"。大多数 KO 熬不到 KE，大多数 KE 熬不到 KB——漏斗的作用就是筛掉噪音，只留下最有价值的东西。
