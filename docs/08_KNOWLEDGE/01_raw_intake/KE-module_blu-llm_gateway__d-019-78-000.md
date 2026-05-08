---
module_id: KE-module_blu-llm_gateway__d-019-78-000
title: LLM Gateway (D-019-78)
category: module_blueprint
---

# LLM Gateway (D-019-78)

LLM Gateway (D-019-78)
- Adaptive Complexity Classification (Kaman-inspired): lexical+syntactic+domain features → neural classifier → ComplexityTier (L1/L2/L3)
- Model Tier: L1(complexity<0.3→Haiku/GLM-4-Flash $0.25/M) → L2(0.3-0.7→Sonnet/DeepSeek-V4 $3/M) → L3(>0.7→Opus/GPT-5 $15/M)
- Failover chain: primary(DeepSeek-V4)→fallback1(Sonnet-4.5)→fallback2(GPT-5)→last_resort(GLM-4-Plus)
- Data-Zone: CN→CN models only, US→US models, EU→EU models (GDPR)
