---
module_id: KE-4025-------annotations-000
title: 2c. 事件标注（Annotations）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2c. 事件标注（Annotations）

2c. 事件标注（Annotations）

> 所有变更事件自动注入遥测时间线——回答"是不是上次变更引入的？"

| 事件类型 | 注入内容 | 触发时机 | 消费方 |
|---------|---------|---------|--------|
| **部署事件** | version_from / version_to / deployer / commit_sha | CI/CD 管线触发 | Dashboard 时间线标注 |
| **配置变更** | config_key / old_value / new_value / who | 配置文件写入检测 | FLE 关联异常 |
| **模型切换** | model_from / model_to / reason | AI Router 切换模型 | ai_behavior 追踪 |
| **蓝图变更** | blueprint_id / version_from / version_to / who | 蓝图文件写入 | 蓝图漂移检测 |
| **Feature Flag 变更** | flag_name / state_change / rollout_pct | 特性开关切换 | Experimentation 层 |

---
