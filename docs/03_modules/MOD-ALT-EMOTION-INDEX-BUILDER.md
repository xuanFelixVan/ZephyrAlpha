---
ttl: permanent
title: MOD-ALT-EMOTION-INDEX-BUILDER 情绪指数日批构建器蓝图
doc_type: blueprint
module_id: MOD-ALT-EMOTION-INDEX-BUILDER
responsibility_domain: 
---

# [BLUEPRINT] MOD-ALT-EMOTION-INDEX-BUILDER
<!-- [MODULE] zephyr.alt_data.emotion_index_builder -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# MOD-ALT-EMOTION-INDEX-BUILDER — 情绪指数日批构建器

- 设计真源：[docs/_working/emotion_line/emotion_index_skeleton_v0.md](../_working/emotion_line/emotion_index_skeleton_v0.md)（骨架 v0.2）
- 契约真源：总包接口契约 v0.1（Max 定稿，2026-09-22）
- 代码：`src/zephyr/alt_data/emotion_index_builder.py`（纯计算零写库）
- 落表：`c1_market.emotion_index`（DDL 真源 `schemas/categories/market/market_emotion_index.py`）
- 调度：`emotion_index_close_final`（daily_kline）/ `emotion_index_pre_open`（pre_market），
  路由分支 `internal_compute_provider._fetch_emotion_index`，行交调度器写通道
- 测试：`tests/alt_data/test_emotion_index_builder.py`
- 内收判定：裁定#400（与 sentiment_cycle 并存分层，温度计≠档位计，内核单源化方向）

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-ALT-EMOTION-INDEX-BUILDER`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-ALT-EMOTION-INDEX-BUILDER` 的 1 个 file 节点 | design | `extract_depgraph.py --modules MOD-ALT-EMOTION-INDEX-BUILDER` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Draft | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-ALT-EMOTION-INDEX-BUILDER | MOD-ALT-EMOTION-INDEX-BUILDER | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
