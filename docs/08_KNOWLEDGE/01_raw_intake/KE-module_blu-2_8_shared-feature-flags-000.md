---
module_id: KE-module_blu-2_8_shared-feature-flags-000
title: 2.8 shared-feature-flags（功能开关）
category: module_blueprint
---

# 2.8 shared-feature-flags（功能开关）

2.8 shared-feature-flags（功能开关）

> **盲点 B7/B10 修复**——100% AI 施工下的 AI 行为开关，配置驱动。

| 文件 | 职责 |
|------|------|
| `flags.py` | **FeatureFlag + FlagRegistry**——三态开关 ALWAYS_ON/CONDITIONAL/ALWAYS_OFF + 按 module_id/agent_id 灰度 |
