---
module_id: KE-1264
status: active
title: Ke Module Blu     004
ttl: permanent
doc_type: knowledge_entry
---

--004
title: ---
category: module_blueprint
---

# ---

---
task_id: "TASK-GOV-0022"
source_blueprint: "MOD-GOVERNANCE"
source_section: "治理脚本去重与优化"

title: "d5_architecture 根目录重复脚本清理 + test_all_scripts 分层改造"
description: |
  清理 d5_architecture 下 49 对同名异版本文件（根目录 vs 子目录），保留子目录 canonical 版本；
  重构 test_all_scripts.py 使用 run_all.py 标签体系实现分层测试（Quick/Critical/Full）；
  更新 script-manifest.yaml 移除已删除条目。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\scripts\\governance\\run_all.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_all_scripts.py"
  - "D:\\ZephyrAlpha\\scripts\\script-manifest.yaml"
  - "D:\\ZephyrAlpha\\tests\\governance\\conftest.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\scripts\\script-manifest.yaml"
    description: "移除已删除的根目录重复条目"
  - path: "D:\\ZephyrAlpha\\tests\\governance\\test_all_scripts.py"
    description: "重构为按标签分层测试 Python 脚本"
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\d5_architecture\\*.py"
    description: "删除 ~50 个根目录重复脚本"

allowed_touch:
  - "D:\\ZephyrAlpha\\scripts\\governance\\d5_architecture\\*.py"
  - "D:\\ZephyrAlpha\\scripts\\script-manifest.yaml"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_all_scripts.py"
  - "D:\\ZephyrAlpha\\scripts\\generate_manifest.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\scripts\\governance\\d5_architecture\\analyzers\\**"
  - "D:\\ZephyrAlpha\\scripts\\governance\\d5_architecture\\checkers\\**"
  - "D:\\ZephyrAlpha\\scripts\\governance\\d5_architecture\\detectors\\**"
  - "D:\\ZephyrAlpha\\scripts\\governance\\d5_architecture\\generators\\**"
  - "D:\\ZephyrAlpha\\scripts\\governance\\d5_architecture\\syncers\\**"
  - "D:\\ZephyrAlpha\\scripts\\governance\\d5_architecture\\validators\\**"
  - "D:\\ZephyrAlpha\\src\\**"

applicable_rules:
  - RULE-ZERO: "删除前走锁协议"
  - RULE-THREE: "删除前置三步审判"
  - RULE-SEVEN: "ThreadPoolExecutor 并行"
  - RULE-FIVE: "临时文件零残留"

acceptance_criteria:
  - "d5_architecture 根目录重复脚本已删除，子目录 canonical 版本保留"
  - "script-manifest.yaml 不再引用已删除路径"
  - "test_all_scripts.py 按标签分层（Quick/Critical/Full）"
  - "python -m pytest tests/governance/test_all_scripts.py --collect-only -q 通过"
  - "无孤儿脚本（audit_registration.py 通过）"
  - "generate_manifest.py 重新生成后 manifest 一致"

rollback_instructions: |
  1. git checkout -- scripts/governance/d5_architecture/*.py
  2. git checkout -- scripts/script-manifest.yaml
  3. git checkout -- tests/governance/test_all_scripts.py

status: "done"
tags_fn: ["governance"]
tags_ly: "cross_layer"
tags_st: "active"
tags_mo: ["MOD-GOVERNANCE"]
