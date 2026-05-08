---
task_id: "TASK-KB-0016"
source_blueprint: "MOD-KB-001"
source_section: "§5.12 四层防遗漏哨兵体系 + §5.13 全自动提取策略"

title: "四大哨兵实现——死知识检测 / 缺口检测 / 过期检测 / 专有词检测 + autoextract全自动模式"
description: |
  实现蓝图 §5.12 定义的四层防遗漏哨兵：(1)Sentinel 1 死知识检测（30d后）——adoption_count=0且freshness<50%→推Owner (a)保留/(b)进入沉睡池(retired)/(c)降级为KO；(2)Sentinel 2 缺口检测——session log中出现P0但KE中无对应category→缺哪补哪；同category下KE quality_score差距突出→提醒补全该domain；(3)Sentinel 3 过期检测（14d)→监控 b_kb.yaml ADR依赖记录 → 每次启动检测概念漂移→强制更新或降级；(4)Sentinel 4 专有词检测→KP词表(bp/s2s/prd/od/sop)→发现KP→检查是否有对应KE 5倍梯度惩罚。
  实现 §5.13 全自动提取：(1)优先级队列 PriorityQueue(capacity=27)；(2)auto_extract() 异步循环→_attempt_extract()→成功→notify；(3)quality_score≥0.80+adoption_count≥3→auto_promote_to_kb()（仅针对Track A）→90d冷却。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\_sentinels\\__init__.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\extract.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\_sentinels\\dead_knowledge.py"
    description: "新/增强——Sentinel 1 死知识检测"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\_sentinels\\gap_detector.py"
    description: "新/增强——Sentinel 2 缺口检测"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\_sentinels\\stale_detector.py"
    description: "新/增强——Sentinel 3 过期检测"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\_sentinels\\proprietary_term.py"
    description: "新/增强——Sentinel 4 专有词检测"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\auto_extract.py"
    description: "新建——PriorityQueue(27)+auto_extract()异步循环+auto_promote_to_kb()"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\_sentinels\\**\\*.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\auto_extract.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§5.12 定义四层哨兵 + §5.13 定义全自动提取策略"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 12000
timeout_minutes: 45

acceptance_criteria:
  - "Sentinel 1 检测 adoption_count=0且freshness<50% 的KE → 推送Owner 三选一"
  - "Sentinel 2 执行 category_covered 校验并补缺"
  - "Sentinel 3 执行 b_kb.yaml ADR依赖逐条新鲜度检查"
  - "Sentinel 4 KP词表匹配→5倍梯度惩罚缺失KE"
  - "PriorityQueue capacity=27——超出后拒绝入队"
  - "auto_extract() 单次提取最多3轮重试——失败后 SENTINEL_ALERT→回到队列底"
  - "auto_promote: quality_score≥0.80+adoption≥3→Track A类自动升格KB"

rollback_instructions: |
  1. git checkout -- src/zephyr/kb/_sentinels/
  2. 删除 src/zephyr/kb/auto_extract.py

depends_on: ["TASK-KB-0011"]
blocked_by: []
status: "created"
tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-KB-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
