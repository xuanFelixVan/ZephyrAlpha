---
module_id: KE-1714-------output-quality-gate-003
status: active
title: 2.14 事中控制——Output Quality Gate
category: module_blueprint
ttl: permanent
---

# 2.14 事中控制——Output Quality Gate

2.14 事中控制——Output Quality Gate

> **决策 D-024-12（🆕 v0.4.0）**：Token ROI 只统计事后产出。但需要实时质量信号——如果 LLM 的前 200 token 输出明显是垃圾（格式错误/幻觉/不相关），应立即 abort + 切模型重试，而不是等到 4000 token 输出完了再判断。

```yaml
output_quality_gate:
  description: "输出前 N token 的快速质量校验——在浪费大量预算前发现问题"
  lifecycle_position: "in_flight"

  # 与 MOD-INF-023 Drift Detector 联动
  validator: "output_validator.early_quality_check()"

  early_signals:
    format_check:
      trigger: "first 200 output tokens"
      rules:
        - "JSON/XML 格式正确性"
        - "代码块完整性（``` 是否闭合）"
        - "markdown 语法正确性"
      fail_action: "ABORT + 追加 '你的输出格式有误，请重新生成' 到下一轮 prompt"

    relevance_check:
      trigger: "first 300 output tokens"
      method: "Fast embedding similarity(partial_output, task_prompt)"
      threshold: "similarity < 0.4"
      fail_action: "ABORT + L1_warning '输出与任务无关——可能上下文污染'"

    hallucination_check:
      trigger: "full response received"
      method: "引用验证——输出中声称的 file_path / module_id 是否真实存在"
      fail_action: "MARK_FAILED + 不计入 ROI + 写入 audit trail"

  auto_retry:
    max_retries: 2
    retry_model_escalation:
      attempt_1: "same model + extra 'be accurate' prompt"
      attempt_2: "升級到下一個 Tier 模型"
```
