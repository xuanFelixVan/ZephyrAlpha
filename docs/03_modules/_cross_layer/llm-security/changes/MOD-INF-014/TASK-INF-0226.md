---
task_id: "TASK-INF-0226"
source_blueprint: "MOD-INF-014"
source_section: "§32 Embedding Inversion 攻击防御"
title: "Embedding向量反转攻击防御——模型训练数据逆向提取防护+向量异常检测+输出输出模糊化"
description: |
  实现 EmbeddingInversionDefender: 
  向量输出模糊化(gaussian_noise/dropout/quantization 三种噪声策略可选)、
  异常向量请求检测(突发的密集向量请求→频率异常+上下文不一致)、
  输出水印机制(输出向量→弱信号水印→事后追溯架构)、
  请求频率限制(与 L5 RateLimiter 联动)、
  邻居保护(输出邻居→真实邻居+噪音邻居混合)。
priority: "P2"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\layers\\embedding_inversion_defense.py"
    description: "EmbeddingInversionDefender——5项防御能力"
  - path: "D:\\ZephyrAlpha\\tests\\llm_security\\test_embedding_inversion_defense.py"
    description: "Embedding Inversion 防御测试——8条用例"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\layers\\embedding_inversion_defense.py"
  - "D:\\ZephyrAlpha\\tests\\llm_security\\test_embedding_inversion_defense.py"
forbidden_touch: []
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\_cross_layer\\llm-security\\blueprint.md"
    reason: "§32 Embedding Inversion 攻击定义+缓解策略"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1","M3"]
estimated_tokens: 8000
timeout_minutes: 45
acceptance_criteria:
  - "EmbeddingInversionDefender 含 obfuscate_vector/detect_abnormal_requests/watermark_output/check_rate_anomaly/protect_neighbors 5个方法"
  - "NoiseStrategy 枚举: GAUSSIAN_NOISE/DROPOUT/QUANTIZATION 可选+可组合"
  - "AbnormalRequestDetector: 突发密集向量请求→burst_window(60s)+threshold(100req/60s)"
  - "VectorWatermarker: 输出向量→弱信号水印→事后追溯"
  - "RateLimitIntegration: 复用 L5 ResourceProtection Layer RateLimiter"
  - "NeighborProtector: 输出邻居→真实k+噪音(r-1→k)邻居混合"
  - "Pydantic V2 ObfuscatedVector/AbnormalRequestAlert"
  - "8条测试全部通过"
rollback_instructions: |
  1. 删除 embedding_inversion_defense.py + test_embedding_inversion_defense.py
depends_on: ["TASK-INF-0201","TASK-INF-0208"]
blocked_by: []
status: "created"
tags_fn: ["security","embedding"]
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-014"]
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# 目标

实现 Embedding Inversion 攻击防御——防止攻击者通过模型向量输出反向提取训练数据。

## 执行步骤

### 做
1. 实现 EmbeddingInversionDefender——5个防御方法
2. 实现 NoiseStrategy 三种噪声策略
3. 编写 8 条测试
