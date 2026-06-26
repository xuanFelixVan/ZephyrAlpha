---
module_id: KE-3265
title: 1.3 与其他视图的边界
category: documentation
ttl: permanent
---

# 1.3 与其他视图的边界

1.3 与其他视图的边界

| 其他视图 | 本视图与其关系 |
|---|---|
| `business_architecture.md` | 01-BA 定义"业务做什么"（能力边界 / Value Stream / RACI）；本视图给每项能力打成熟度分 |
| `architecture_model/cross-cutting/capability_heatmap.yaml` | YAML 是**机器可读能力清单**（canonical schema）；本视图是**人类可读热力图视觉化**（引用该文件作为数据源）|
| `application_architecture.md` | 03-AA 14 层 **业务本体**；本视图 14 层 × 7 能力域**叠加评分**，承载热力图的数据源 |
| `runtime_planes.md` | 04bis 是执行维度正交视图；本视图是成熟度维度正交视图。两视图**各切一把尺子**，协同刻画系统全貌 |
| `archive/reorg-2026-04-24/draft-abandoned/working-designs/ai-autonomy-architecture-design.md`（ARC-20260424-007）| AI 自治层的能力评分由本视图 §3 第 7 能力域承载 |
