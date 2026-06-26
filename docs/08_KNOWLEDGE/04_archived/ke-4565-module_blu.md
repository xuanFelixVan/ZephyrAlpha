---
module_id: KE-4400
title: Phase 3：检索质量闭环
category: module_blueprint
ttl: permanent
---

# Phase 3：检索质量闭环

Phase 3：检索质量闭环

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §3.2 混合检索 + §8 FLE集成 |
| 产出位置 | `hybrid_retriever.py` / `retrieval_feedback.py` / `cross_collection_retriever.py` |
| 验收标准 | 混合检索 top-5 精度 > 纯向量 top-5；FLE 可记录检索反馈 |
| G7 检查项 | RRF 融合正确？RetrievalTrace 可解释？反馈信号写入 FLE pipeline？ |
