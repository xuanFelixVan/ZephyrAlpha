---
module_id: KE-module_blu-3_7_ke-003
title: 3.7 KE 运行时反馈字段
category: module_blueprint
---

# 3.7 KE 运行时反馈字段

3.7 KE 运行时反馈字段

**问题**：当前 `quality_score` 只在入库时计算一次（G2 Triage），之后永远不变。但实际上——一条 KE 被 AI 检索了 100 次但从未采纳 = 质量可能有问题；一条 KE 被检索 3 次但 3 次都采纳了 = 高质量。

**新增 Schema 字段**（追加到 §3.2 KE Schema）：

| 字段 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| `usage_count` | int | ✅ | 被 `recall()` 检索到的次数。默认 0 |
| `adoption_count` | int | ✅ | 被检索后 AI 实际采纳的次数。由 `learn(event_type="ke_used", adopted=True)` 递增。默认 0 |
| `helpfulness_score` | float [0.0-1.0] | ✅ | 采纳后任务成功率（滑动窗口最近 10 次）。由 `learn(event_type="task_outcome")` 更新。默认 0.5 |
| `last_used_at` | datetime | SHOULD | AI 最后一次检索/使用此 KE 的时间 |

**动态质量评分**（取代纯静态评分）：

```python
quality_score = (
    quality_score_static * 0.4    # 入库时 G2 Triage 评分
    + adoption_rate     * 0.3    # 采纳次数 / usage_count（usage_count=0 → 此项=0）
    + helpfulness_score * 0.2   # 任务成功率
    + freshness         * 0.1    # 半衰期的新鲜度
)
```

**反馈事件类型**（通过 `unified_memory_api.learn()` 记录）：

| event_type | 触发时机 | 记录内容 |
|-----------|---------|---------|
| `ke_retrieved` | `recall()` 返回 KE 列表时 | `ke_id` + `query` |
| `ke_adopted` | AI 明确说"根据 KE-042 的建议..." | `ke_id` + `adopted=True` |
| `ke_ignored` | KE 被检索到但 AI 未引用 | `ke_id` + `adopted=False` |
| `task_outcome` | 任务完成时 | `ke_id`（哪些 KE 被采纳） + `success`（bool） + `session_id` |
| `ke_contradiction` | 矛盾检测发现冲突 | `ke_id_a` + `ke_id_b` + `conflict_description` |

**KE Schema 新增字段**（追加到 §3.2）——**知识退化级联防护**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| `extraction_generation` | int | ✅ | **知识提取的代际数**。gen=0：直接来自 Owner 原话；gen=1：来自 AI 基于 gen=0 KE 产生的 session；gen≥3：高风险——已跨 3 次提取，语义偏移概率 > 15%。默认 0。每次 `batch_ingest` 新 KE 时：`max(源session中引用到的KE的generation) + 1` |

> **触发缺口（盲点#18）**："传话游戏"效应——Session 1 中 Owner 说"ruff E501 实际含义是行超过88字符"→G5 Extract→KE-042→Session 2 AI 注入此 KE 后输出"ruff E501严格限制88字符"→G5 Extract→KE-073→Session 3 AI 注入后输出"ruff E501：禁止超过88字符的行"。3 跳后，"含义是"变成了"禁止"——20% 语义偏移。gen=0 直接来自 Owner 的 KE 权重最高；gen≥3 的 KE 每次 G3 Analyze 时追加退化检测（§9.13 新增子规则）。

> **对标**：Horthy Harness Engineering——反馈闭环是四大支柱之一（"每次注入的知识必须追踪采纳率和效果"）+ Google Vertex AI——RAG 评估有 `answer_relevance` + `faithfulness` + `context_recall` 三维指标。
> 大白话：现在知识存进去后跟石沉大海一样——不知道 AI 到底用没用、用了有没有用。加了这四个字段，知识从"入库时猜质量"变成"运行时验证质量"。就像餐厅——不仅做出菜（G2），还要看客人吃没吃（`adoption_count`）、好不好吃（`helpfulness_score`）。`extraction_generation` 管的是另一个问题：知识被反复"蒸馏"时会不会变味——gen=0（Owner 原话）→真金；gen=3（AI 基于 AI 输出的再提取）→可能是镀金，需要重审原始来源。
