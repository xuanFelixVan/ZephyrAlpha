---
module_id: KE-module_blu-3_10_ko_knowledge_observation-003
title: 3.10 KO（Knowledge Observation）存储格式
category: module_blueprint
---

# 3.10 KO（Knowledge Observation）存储格式

3.10 KO（Knowledge Observation）存储格式

**定位**：KO 是"知识碎片"——尚未通过完整 G1→G5 流水线的轻量级知识观察。对标 ITIL DIKW 金字塔的 Data→Information 层：KO = 原始观察（Data），KE = 结构化知识（Information），KB = 聚合规则（Knowledge）。

**KO 与 KE 的核心差异**：

| 维度 | KO | KE |
|------|:---:|:---:|
| 状态 | OBSERVED / PROMOTING / PROMOTED / DISCARDED（4 状态） | DRAFT→VERIFIED（10 状态机，§3.3） |
| 质量要求 | 低——仅需来源可追溯 | 高——需经过 G2 Triage 评分 ≥ 0.6 |
| 向量化 | ❌ 不入 ChromaDB | ✅ 入 ke_entries Collection |
| 被检索 | ❌ 不被 `recall()` 返回 | ✅ 语义检索+标签过滤+全文搜索 |
| 晋升条件 | 同 category 累计 3 条 + 人工确认 | — |
| 文件命名 | `KO-{NNN}-{slug}.md` | `KE-{NNN}-{slug}.md`（§3.2.1） |

**KO 4 状态机**：

```
OBSERVED → PROMOTING → PROMOTED（→ 转为 KE，原 KO 归档）
    │          │
    └──────────┴──→ DISCARDED（不晋升，直接丢弃）
```

| 状态 | 含义 | 条件 |
|------|------|------|
| OBSERVED | 系统自动生成，等待积累 | G2 Triage 将 LOW→MID 的知识放入 KO 等待队列 |
| PROMOTING | 满足晋升条件（同 category ≥ 3 条），等待 Owner 确认 | L2 哨兵触发："3 条同类 KO 待审批" |
| PROMOTED | Owner 确认晋升，已转为 KE | `batch_ingest.py` 将 KO 批量转为 KE |
| DISCARDED | Owner 拒绝晋升，或 90d 未达晋升条件 | 自动过期清理（APScheduler 月度 cron） |

**KO 文件模板**（`docs/08_knowledge/ko/KO-015-ruff-vs-pylint-speed-comparison.md`）：

```yaml
---
ko_id: "KO-015"
title: "ruff 比 pylint 快 50x 的实测数据"

category: "tool_configuration"
domain: "infra"
layer: "L01"

source_type: "session_log"
source_path: "docs/19_development_workspace/session-logs/session-047.md"

status: "OBSERVED"
priority: "MID"
quality_score: 0.45

created_at: "2026-05-02T14:35:00+08:00"
