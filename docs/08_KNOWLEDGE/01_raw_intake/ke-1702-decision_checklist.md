---
module_id: KE-1612
title: 2. Decision Checklist
category: module_blueprint
ttl: permanent
---

# 2. Decision Checklist

2. Decision Checklist

| ID | 决策 | 验证方式 |
|----|------|---------|
| DD1 | 4 阶段 vs 3 或 5 | 流水线编排代码中阶段数=4，每阶段独立 try/except |
| DD2 | Token 预算三级 80%/90%/95% | check_budget() 返回 L1/L2/L3 三种状态 |
| DD3 | DocCompressor Pydantic frozen | CompressionPolicy.model_config = {"frozen": True} |
| DD4 | intent_parser 10 分类 | len(IntentType) == 10 |
| DD5 | DocCompressor 三级降级 | compress() 含三个 fallback 分支 |
| DD6 | token_budget=8000 | DEFAULT_CONTEXT_TOKEN_BUDGET 常量 |
| DD7 | ContextRot 幂函数 n^{-k} | 数学函数在 context_rot_model.py |
| DD8 | Provenance 全覆盖 | InjectionResult.sources 含 provenance |
| DD9 | Eviction 三维排序 | sort key = priority * freshness * relevance |
| DD10 | Per-Turn 增量注入 | curation_loop 跟踪已注入 KE ID 集合 |
