---
module_id: KE-2195
title: 4. Key Design Decisions
category: module_blueprint
---

# 4. Key Design Decisions

4. Key Design Decisions

| ID | 决策 | 理由 |
|----|------|------|
| DD1 | 4 阶段流水线 | Build/Compress/Validate/Inject 各有独立失败域和降级 |
| DD2 | Token 预算三级 80%/90%/95% | 区分预警和紧急 |
| DD3 | DocCompressor Pydantic frozen | 不变量不可运行时修改 |
| DD5 | DocCompressor 三级降级 | Phase1 规则基, beta 本地 LLM, Phase3 截断 |
| DD6 | token_budget=8000 默认 | 主流模型 context window 的 10-15% |
