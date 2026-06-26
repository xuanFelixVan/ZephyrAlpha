---
module_id: KE-2546------featureflag-002
status: active
title: AI 施工约定（FeatureFlag）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# AI 施工约定（FeatureFlag）

AI 施工约定（FeatureFlag）

```
1. AI 新增任何 Telemetry 功能时 MUST 同时创建对应的 FeatureFlag（初始 OFF）
2. AI 禁止自行修改 FlagState——修改 flag 是人工运维权限
3. 所有采集频率/采样率/阈值参数 SHOULD 通过 FeatureFlag 暴露，不做硬编码
4. 每次 AI session 启动时检查 FeatureFlag 状态（§14 AI session 冷启动工作流）
```
