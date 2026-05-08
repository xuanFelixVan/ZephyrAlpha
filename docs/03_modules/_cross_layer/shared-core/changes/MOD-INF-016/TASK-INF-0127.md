---
task_id: "TASK-INF-0127"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §19 Shared Layer Testing Strategy"

title: "§19 测试策略——Shared层 42 文件单元测试全面补全"
description: |
  按蓝图 §19 的 Shared Layer Testing Strategy——当前 shared/ 42 文件缺专属测试文件。
  42 = Shared 46 总数 - 4 个已有测试模块（contracts 部分）。
  实现要求：
  1. 为 shared/ 下每个核心模块生成专门的 unit test。
  2. 测试覆盖率目标——按模块而言 contracts:95% infra:90% errors:100% resilience:95%。
  3. pytest conftest.py——shared/ fixtures 必须在 test init 后通用。
  4. 新增 test 文件必须放在 tests/unit/ 下，含 shared/ 源码路径追溯。
  5. param search——自动跑 4 种 threshold 以寻最佳退避策略。
  专业对标：pytest-cov + hypothesis + ZephyrAlpha Testing Pipeline。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\retry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\circuit_breaker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\fallback.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\contracts\\instrument.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\contracts\\money.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\contracts\\timestamp.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\errors.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\constants.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_retry.py"
    description: "RetryPolicy 退避策略测试——验证 backoff + jitter"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_circuit_breaker.py"
    description: "CircuitBreaker 打点检测——阈值 = 3/5/10 验证"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_fallback.py"
    description: "FallbackChain 测试——5 阶 fallback Level-of-Detail"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_errors.py"
    description: "ZephyrBaseError 12 子类 100% 覆盖"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_constants.py"
    description: "22 枚举 单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_observer.py"
    description: "Observer 事件订阅测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_capability.py"
    description: "Capability 模型测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\conftest.py"
    description: "Shared test fixtures——pytest conftest"

allowed_touch:
  - "D:\\ZephyrAlpha\\tests\\unit\\test_retry.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_circuit_breaker.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_fallback.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_errors.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_constants.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_observer.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_capability.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\conftest.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "GOV-TSK-004"
    section: "全篇"
    reason: "任务关闭标准——测试覆盖率为关闭必要条件"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §19——shared 层测试策略与覆盖率目标"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\errors.py"
    reason: "errors.py——12 子类全部需要测试覆盖"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\constants.py"
    reason: "constants.py——22 枚举全部需要测试"

assigned_model: "claude-sonnet-4.6"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 30000
timeout_minutes: 75

acceptance_criteria:
  - "Test Shared contracts:99% coverage——instrument / money / timestamp / runtime_plane_tag"
  - "Test errors:100% coverage——12 个 ZephyrError 子类均被 raise/import 测试覆盖"
  - "Test constants:100% coverage——22 枚举均被 import 测试覆盖"
  - "Test resilience:95% coverage——retry/circuit_breaker/fallback param search 验证"
  - "conftest.py fixtures 正确设置——pytest 运行无 contrived import error"
  - "全部 test 文件都在 tests/unit/ 下——符合目录结构"
  - "pytest tests/unit/ -v --cov=src/zephyr/shared --cov-report=term 目标覆盖率 >= 90%"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\tests\unit\test_retry.py
  2. 删除 D:\ZephyrAlpha\tests\unit\test_circuit_breaker.py
  3. 删除 D:\ZephyrAlpha\tests\unit\test_fallback.py
  4. 删除 D:\ZephyrAlpha\tests\unit\test_errors.py
  5. 删除 D:\ZephyrAlpha\tests\unit\test_constants.py
  6. 删除 D:\ZephyrAlpha\tests\unit\test_observer.py
  7. 删除 D:\ZephyrAlpha\tests\unit\test_capability.py
  8. 删除 D:\ZephyrAlpha\tests\unit\conftest.py

depends_on: ["TASK-INF-0101"]
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
