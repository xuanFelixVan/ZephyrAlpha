---
module_id: KE-module_blu-3_2_1_taskcard_vibe_coding-008
title: 3.2.1 TaskCard（Vibe Coding 扩展任务模型）
category: module_blueprint
---

# 3.2.1 TaskCard（Vibe Coding 扩展任务模型）

3.2.1 TaskCard（Vibe Coding 扩展任务模型）

> **基座**：继承 [shared/schemas.py](file:///D:/ZephyrAlpha/src/zephyr/shared/schemas.py) `Task`（**31 字段**，真源 [metadata-registry.md](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/meta/metadata-registry.md) §7.1~§7.1.1）
>
> **扩展**：本蓝图追加 6 维防漂移 + 门禁 + 管线 + **v0.4.0 新增：父子层级/可执行回滚/Retry策略/AI自治五级** 等 Vibe Coding 执行层字段

```python
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from datetime import datetime
from typing import Optional
from zephyr.shared.schemas import Task, TaskStatus, Priority, SafetyLevel, Classification, EvolutionPolicy

class GateLevel(str, Enum):
    """全生命周期门禁——G0-G7"""
    G0 = "G0"  # 创建门禁——字段完整性校验（21必填） + v0.4.0: diff_plan_required/conflict_free/idempotent_check
    G7 = "G7"  # 完整度门禁——上游文件存在+下游路径完整+回滚可执行 + v0.4.0: checkpoint_path 可用
    G1 = "G1"  # 指派门禁——模型/管线/模块不冲突 + v0.4.0: WIP 限制检查 + 并发冲突检测
    G2 = "G2"  # 前置门禁——depends_on 全部 COMPLETED/VERIFIED + v0.4.0: 拓扑排序校验 + 循环依赖检测
    G3 = "G3"  # 执行门禁——context_assembly_manifest 全部可读 + v0.4.0: 上下文窗口溢出保护
    G4 = "G4"  # 产出门禁——downstream_outputs 文件存在+格式正确
    G5 = "G5"  # 审计门禁——audit_findings 零 Critical/High
    G6 = "G6"  # 关闭门禁——artifact_paths 残留物已处理

class TaskNamespace(str, Enum):
    """任务命名空间——裁定 #21 + metadata-registry.md §7.2"""
    ADR = "ADR"  # 架构决策记录
    CP = "CP"    # 施工计划
    KE = "KE"    # 知识条目
    STD = "STD"  # 标准/规范
    DW = "DW"    # 开发工作区
    SRC = "SRC"  # 源代码
    OPS = "OPS"  # 运维/其他

class AISelfGovernanceLevel(str, Enum):
    """AI 自治等级——v0.4.0 新增，五级枚举（GOV-TASK-004 §AI自治 真源）"""
    SUPERVISED = "supervised"          # Owner 在线时执行——所有操作需确认
    SEMI_AUTONOMOUS = "semi_autonomous"  # Owner 离线可执行低风险任务（P2-P4）——不可改规则/蓝图
    AUTONOMOUS = "autonomous"           # 完全自主——可自动 READY→IN_PROGRESS，自动低风险修复
    FULL_AUTO = "full_auto"            # 全自动——可改非规则代码 + 自动创建任务卡
    EMERGENCY_ONLY = "emergency_only"  # 仅紧急模式——P0/P1 + 断路器触发时自动介入

class TaskCard(Task):
    """
    Vibe Coding 任务模型——继承 shared/schemas.py Task（31字段）+ 追加执行层字段

    父类（Task，metadata-registry.md §7 真源）提供：
      task_id(namespace-seq), namespace, seq, title, status(10态), priority(P0-P3),
      phase, execution_model, model_rationale, fallback_model, safety_level,
      directive, idempotent, classification, evolution_policy, estimate_hours,
      actual_hours, files_in_scope, deliverables, acceptance, depends_on,
      tags(扁平[]), session_id, waiting_for, ready_at, completed_at, created_at, updated_at

    本类追加 Vibe Coding 执行层字段——防漂移六维 + 门禁 + 管线 + v0.4.0 新增扩展
    """
    model_config = ConfigDict(extra="allow")

    # ---- 防漂移：上游（Vibe Coding 关键——AI需要知道读什么）----
    upstream_files: list[str] = Field(
        default_factory=list,
        description="执行前必须读取的文件完整绝对路径列表——AI 零记忆，不知道看什么"
    )

    # ---- 防漂移：下游（结构化产出描述）----
    downstream_outputs: list[dict] = Field(
        default_factory=list,
        description="执行后必须产出的文件 [{path: 完整绝对路径, description: 说明}]"
    )

    # ---- 防漂移：范围白名单（对标 K8s PodSecurityPolicy allowedCapabilities）----
    allowed_tou
