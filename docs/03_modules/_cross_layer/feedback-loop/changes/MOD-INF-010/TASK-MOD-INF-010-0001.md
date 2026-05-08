---
task_id: TASK-MOD-INF-010-0001
module_id: MOD-INF-010
blueprint_ref: D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback-loop\blueprint.md
blueprint_sections: ["§1 概述与模块定位", "§2.0 三相流水线架构", "§10 已实现代码完整路径索引"]
status: pending
priority: P0
created_date: 2026-05-06
assigned_to: null
depends_on: []
blocked_by: []
blocks: ["TASK-MOD-INF-010-0002", "TASK-MOD-INF-010-0003"]
estimated_effort_hours: 4
actual_effort_hours: null
tags: [scaffold, foundation, directory-structure, module-identity]
upstream_files:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback-loop\blueprint.md
  - D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml
  - D:\ZephyrAlpha\docs\01_policies_and_standards\governance\document\directory-structure-standard.md
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\__init__.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\config.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\protocols.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\exceptions.py
acceptance_criteria:
  - AC-0001-01: feedback_loop/ 目录结构符合 directory-structure-standard.md 规范
  - AC-0001-02: __init__.py 导出 module_id MOD-INF-010 和版本号 v0.1.0
  - AC-0001-03: config.py 包含 FLEConfig 类，含 enable_autonomous_actions (default=False)、log_dir、otel_endpoint
  - AC-0001-04: protocols.py 定义 fire-and-forget Protocol 适配器接口 (FeedbackProtocolAdapter)，单向依赖调用其他系统
  - AC-0001-05: exceptions.py 定义 FLEBaseException，含 forensic_context 字段（stack_trace + causal_chain + decision_id）
  - AC-0001-06: blueprint-registry.yaml 中 MOD-INF-010 版本号更新为当前版本
  - AC-0001-07: §10 已实现代码路径索引 新增本任务创建的文件路径
rollback_instructions: |
  1. 删除 src/zephyr/feedback_loop/ 目录下本次创建的所有文件
  2. 回滚 blueprint-registry.yaml 中 MOD-INF-010 的版本号
  3. 如已注册到 _init__.py 的包导出，移除相应 import
context_assembly_manifest:
  required_contexts:
    - context_id: CTX-BLUEPRINT-§1
      source: D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback-loop\blueprint.md
      sections: ["§1.1 模块身份", "§1.2 核心职能", "§1.3 防循环依赖设计"]
      description: 模块身份定义——module_id/bounded_context/核心职责/Protocol单向依赖
    - context_id: CTX-BLUEPRINT-§10
      source: D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback-loop\blueprint.md
      sections: ["§10.1 源码文件", "§10.2 测试文件", "§10.5 路径索引使用指南"]
      description: 已实现代码路径索引——了解当前状态
    - context_id: CTX-DIRECTORY-STANDARD
      source: D:\ZephyrAlpha\docs\01_policies_and_standards\governance\document\directory-structure-standard.md
      description: 目录结构标准——文件存放路径规范
  assembly_notes: |
    这是 feedback_loop 模块的第一张任务卡。模块落位 src/zephyr/feedback_loop/，
    边界上下文 bounded_context=true。FLE 通过 Protocol 适配器 fire-and-forget 调用其他系统（单向依赖），
    避免循环依赖。core_responsibility: 系统自我调节——"发现问题→分析根因→调度修复"。
---

# TASK-MOD-INF-010-0001: feedback-loop 模块骨架搭建

## 1. 任务目标

搭建 MOD-INF-010 feedback_loop 模块的基础骨架，包括目录结构、配置文件、协议适配器接口、异常体系，确保模块具备最小可运行框架。

## 2. 模块身份

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-010 |
| 代码落位 | `src/zephyr/feedback_loop/` |
| 边界上下文 | bounded_context: true（独立领域模型） |
| 核心职责 | 系统自我调节——"发现问题 → 分析根因 → 调度修复" |
| 防循环依赖 | Protocol 适配器 fire-and-forget 单向依赖 |

## 3. 实现步骤

### Step 1: 创建 feedback_loop 目录结构
```
src/zephyr/feedback_loop/
├── __init__.py
├── config.py
├── protocols.py
├── exceptions.py
├── collectors/
│   └── __init__.py
├── detectors/
│   └── __init__.py
├── diagnosers/
│   └── __init__.py
├── actors/
│   └── __init__.py
├── verifiers/
│   └── __init__.py
└── gates/
    └── __init__.py
```

### Step 2: 实现 __init__.py
- 导出 `MODULE_ID = "MOD-INF-010"`、`VERSION = "0.1.0"`
- 延迟加载 FLE 核心组件

### Step 3: 实现 config.py
```python
@dataclass
class FLEConfig:
    enable_autonomous_actions: bool = False
    log_dir: str = "logs/fle/"
    otel_endpoint: str = "http://localhost:4317"
    max_concurrent_actions: int = 3
    autonomy_max_level: int = 0  # 0=OBSERVE_ONLY
    kb_path: str = "data/fle/kb/"
    worm_path: str = "data/fle/worm/"
```

### Step 4: 实现 protocols.py
- FeedbackProtocolAdapter: fire-and-forget 调用接口
- 定义 action_type 枚举：NOTIFY_OWNER、ADJUST_THRESHOLD、REPAIR、DEPLOY、SELF_UPGRADE、REBALANCE

### Step 5: 实现 exceptions.py
- FLEBaseException: 含 forensic_context（stack_trace + causal_chain + decision_id）
- 派生类：DiagnosisError、RepairError、GateBlockedError、AutonomyViolationError

### Step 6: 更新蓝图 §10 路径索引
- 新增本次创建的文件到 §10.1 源码文件表

## 4. 验证方式
1. `python -c "from zephyr.feedback_loop import MODULE_ID; assert MODULE_ID == 'MOD-INF-010'"`
2. `python -c "from zephyr.feedback_loop.config import FLEConfig; c = FLEConfig(); assert c.enable_autonomous_actions == False"`
3. `python scripts/governance/validate_blueprint_code_sync.py --module MOD-INF-010`
