---
module_id: KE-2793
status: active
title: Model Evolution (D-019-23)
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# Model Evolution (D-019-23)

Model Evolution (D-019-23)
- Model Fingerprint 采集: provider/name/version/quantization/context_window
- Output Signature 对比: 旧模型 vs 新模型同一prompt输出 → Diff Score
- Compatibility Gate: Compatibility Score ≥ 0.95 → PASS, < 0.80 → BLOCK
- Safety Regression: injection resistance 基线 ≥ 旧模型的 90%
