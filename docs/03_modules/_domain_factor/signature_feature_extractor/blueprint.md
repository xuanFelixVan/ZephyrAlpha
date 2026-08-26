---
blueprint_id: MOD-FAC-002
module_name: signature_feature_extractor
domain: D_FACTOR
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: human_gated
version: "0.1.0"
created: 2026-08-26
last_updated: 2026-08-26
owner: ZephyrAlpha-Owner
priority: P2
blueprint_level: module
domain_id: D_FACTOR
path: src/zephyr/factor/signature_feature_extractor.py
granularity: file
---

# MOD-FAC-002 signature_feature_extractor 蓝图（签名方法特征提取器）

> **module_id**: MOD-FAC-002 | **域**: D_FACTOR | **优先级**: P2
> **来源**: B10-01834（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-FAC-018，A1 §29.8）
> 代码：`src/zephyr/factor/signature_feature_extractor.py`

## 0. 定位

SignatureFeatureExtractor：路径截断2-4阶log-signature特征向量（对数变换+增量累积+张量积迭代截断，阶数护栏≤4防组合爆炸）+确定性输出（同序列必同向量）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/factor/test_signature_feature_extractor.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
