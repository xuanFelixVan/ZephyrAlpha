---
module_id: KE-2122-----yaml----------wave-3---000
status: active
title: 3.5 策略树 YAML 设计（顶层设计——Wave 3 正式落地，参数在 config.py 中从 Wave 1 开始逐步配置）
category: module_blueprint
---

# 3.5 策略树 YAML 设计（顶层设计——Wave 3 正式落地，参数在 config.py 中从 Wave 1 开始逐步配置）

3.5 策略树 YAML 设计（顶层设计——Wave 3 正式落地，参数在 config.py 中从 Wave 1 开始逐步配置）

去重行为不应该硬编码在 Python 中——顶尖设计用**声明式策略树**替代硬编码阈值表。
Owner 或 AI 可以修改 YAML 调整行为，不需要读懂 Python 代码。
对标 1 人 + AI 维护的最优解。

```yaml
