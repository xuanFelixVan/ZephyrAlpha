---
task_id: "DB-025-0078"
namespace: "OPS"
seq: 78
title: "SSoT 漂移项 D1-D5 关闭——§17 五条漂移逐项验证+自动修复"
tags: ["fn:sost", "ly:cross_layer"]
depends_on: ["DB-025-0036", "DB-025-0046"]
upstream_files:
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_db.yaml"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\blueprint-registry.yaml"
acceptance_criteria:
  - "D1: 文件清单——b_db.yaml旧版4个.py→磁盘实际7个.py，T-DB-004增补3个缺失文件"
  - "D2: schema_version——b_db.yaml旧版1.1.0→蓝图实际2.1.0，T-DB-004同步"
  - "D3: db_file_path——b_db.yaml旧版data/zalpha_metadata.db→磁盘实际docs/09_audit/state/zalpha_metadata.db，T-DB-004同步"
  - "D4: interfaces.contracts——b_db.yaml旧版CT-FLE-DB-001+EXT-DB-ATM-001→蓝图§12定义了4个CT-DB-*，T-DB-004同步"
  - "D5: blueprint-registry.yaml——旧版v0.1.0/完整度72%/partial_80→蓝图实际v2.1.0/~95%/phase_1_complete，需同步更新注册表"
rollback_instructions: "SSoT漂移未关闭 → §20 R07"
---

# DB-025-0078：SSoT 漂移项 D1-D5 关闭——§17

§17: 5条 SSoT 漂移(D1-D5)全部关闭。
