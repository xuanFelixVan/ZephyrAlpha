---
task_id: "TASK-INF-0110"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §4 Phase 18 + §13 盲点 B46-B50"

title: "Phase 18 施工——AI 韧性可控：Backpressure(B46) + Quota配额(B47) + DegradationMatrix(B48) + KG接口(B49) + Drift检测(B50)"
description: |
  实现 AI 系统的全栈弹性——从 Backpressure 反压到 Data Drift 漂移检测。
  B46：Backpressure Protocol——当 AI agent 消费速率超过下游处理能力时，需要反压信号。
  需实现：BackpressureProtocol——subscribe(on_next/on_error/on_complete) + request(n) 拉取模式。
  对标 Reactive Streams / RxPY。
  B47：Quota Management——资源配额管理。每次 AI session 的资源消耗需有上限。
  需实现：QuotaManager——per-session token_quota / time_quota / api_call_quota + 配额耗尽时拒绝。
  对标 K8s ResourceQuota。
  B48：Graceful Degradation Matrix——优雅降级矩阵。当系统某组件不可用时的降级路径。
  需实现：DegradationMatrix——定义功能 → 降级行为映射（e.g., LLM 不可用 → fallback to cached response）。
  对标 Netflix Hystrix。
  B49：Knowledge Graph Interface——知识图谱接口。统一抽象以对接 Neo4j/Mem0 Graph Memory 等 KG 后端。
  需实现：KnowledgeGraphInterface Protocol——add_entity/add_relation/query_path/query_subgraph。
  对标 Mem0 Graph Memory / Neo4j。
  B50：Data Drift Detection——数据漂移检测。模型输入分布变化时自动告警。
  需实现：DriftDetector——compare_baseline(current_sample, reference_sample) → drift_score + alert。
  对标 Evidently AI / NannyML。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\limiter.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\metrics.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\backpressure.py"
    description: "BackpressureProtocol——Reactive Streams 风格 subscribe + request(n)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\quota_manager.py"
    description: "QuotaManager——per-session token/time/api_call 配额"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\degradation_matrix.py"
    description: "DegradationMatrix——功能→降级行为映射"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\kg_interface.py"
    description: "KnowledgeGraphInterface Protocol——add_entity/relation/query"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\drift_detector.py"
    description: "DriftDetector——compare_baseline + drift_score + alert"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_backpressure.py"
    description: "单元测试——验证反压信号传播"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_quota_manager.py"
    description: "单元测试——验证配额耗尽拒绝"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_degradation_matrix.py"
    description: "单元测试——验证降级路径正确性"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_kg_interface.py"
    description: "单元测试——验证 Protocol 签名、CRUD 操作"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_drift_detector.py"
    description: "单元测试——验证 drift score 计算、告警触发"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\backpressure.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\quota_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\degradation_matrix.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\kg_interface.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\drift_detector.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\__init__.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_backpressure.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_quota_manager.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_degradation_matrix.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_kg_interface.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_drift_detector.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\SHARED-QUICKREF.yml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\limiter.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.5"
    reason: "shared/ 准入规则——被 ≥2 个 L01 模块消费"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §4/§13——Phase 18 + B46-B50 盲点详情"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\limiter.py"
    reason: "limiter.py——B47 配额管理器需与此速率限制器互补"

assigned_model: "claude-sonnet-4.6"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 35000
timeout_minutes: 90

acceptance_criteria:
  - "backpressure.py: Publisher Protocol——subscribe(subscriber) → Subscription"
  - "backpressure.py: Subscriber Protocol——on_next/on_error/on_complete + request(n)"
  - "quota_manager.py: SessionQuota 模型——max_tokens / max_time_seconds / max_api_calls"
  - "quota_manager.py: QuotaManager.check_quota()——配额耗尽 → raise QuotaExceededError"
  - "degradation_matrix.py: DegradationMatrix——register_degradation(feature, level, fallback)"
  - "degradation_matrix.py: resolve_fallback(feature, error_type) → fallback_action"
  - "kg_interface.py: KnowledgeGraphInterface Protocol——add_entity/relation + query_path/subgraph"
  - "drift_detector.py: DriftDetector.compare_baseline(current, reference) → DriftReport"
  - "drift_detector.py: drift_score > threshold → alert"
  - "pytest tests/unit/test_backpressure.py -v 全部通过"
  - "pytest tests/unit/test_quota_manager.py -v 全部通过"
  - "pytest tests/unit/test_degradation_matrix.py -v 全部通过"
  - "pytest tests/unit/test_kg_interface.py -v 全部通过"
  - "pytest tests/unit/test_drift_detector.py -v 全部通过"
  - "SHARED-QUICKREF.yml 更新——新增 5 个模块入口"

rollback_instructions: |
  1. 删除 5 个 src/zephyr/shared/ 新文件
  2. 删除 5 个 tests/unit/ 对应测试文件
  3. 还原 __init__.py 对应导出
  4. 还原 SHARED-QUICKREF.yml 对应条目

depends_on: ["TASK-INF-0107", "TASK-INF-0105"]
blocked_by: []

status: "created"

tags_fn:
  - "infra"
tags_ly: "cross_layer"
tags_md: "claude-sonnet-4.6"
tags_st: "active"
tags_mo:
  - "MOD-INF-016"

completed_gates: []
blocked_gates: {}

artifact_paths: []

audit_findings: []

ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
