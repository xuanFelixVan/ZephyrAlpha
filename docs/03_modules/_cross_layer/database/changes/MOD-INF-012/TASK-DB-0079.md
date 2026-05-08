---
task_id: "DB-025-0079"
namespace: "OPS"
seq: 79
title: "SSoT 一致性自愈策略——§17.2 漂移预防+自愈双机制实现"
tags: ["fn:sost", "ly:cross_layer"]
depends_on: ["DB-025-0078"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md"]
acceptance_criteria:
  - "drift_prevention规则1: 每次修改db/目录下文件后→必须同步更新b_db.yaml"
  - "drift_prevention规则2: CI门禁——启动时对比b_db.yaml.files与src/zephyr/db/*.py glob结果"
  - "drift_prevention规则3: 不一致→阻断启动+提示修复SSoT"
  - "self_healing规则1: database_manager.health_check()自动检测schema_version与_MIGRATIONS注册表一致性"
  - "self_healing规则2: 不一致→HealthStatus.unhealthy+建议运行init_db()"
rollback_instructions: "自愈失败 → §20 R07"
---

# DB-025-0079：SSoT 一致性自愈策略——§17.2

§17.2: drift_prevention(3规则)+self_healing(2规则)双机制CI门禁。
