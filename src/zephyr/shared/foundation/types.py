# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.foundation.types
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_types | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
types.py —— 共享类型别名 & 语义化 NewType（Phase 3 新增 | 盲点 #5 修复）

痛点修复：AI 在多个文件中看到 `str` 类型的 task_id / module_id / file_path——
  1. 无法从类型签名区分 "普通字符串" 和 "语义化标识符"
  2. 交叉传递时容易传错（把 file_path 当 task_id 传）
  3. mypy/pyright 无法检测出此类错误

设计对标：
  - TypeScript branded types / `Nominal<T>`
  - Python typing.NewType / Annotated
  - Google //shared/types.h (C++)

设计原则：
  - 纯类型层——零运行时开销，仅用于静态检查 + AI 可读性
  - NewType 子类型不兼容——mypy 会拒绝 `TaskId` 赋值给 `FilePath`
  - 本项目使用 Pydantic V2，Annotated 支持 Field constraints

AI 施工约定：
  - 所有跨模块函数签名 MUST 使用语义化别名而非裸 str/int
  - 新增标识符类型时 MUST 在此登记
  - 本文件是类型维度的 SSoT——禁止在其他文件中重复定义同名 NewType

SSoT: MOD-INF-016 §2.9 shared-types
Version: 0.1.0
"""

from typing import NewType

__all__ = [
    "AbsPath",
    "AgentId",
    "BlueprintVersion",
    "ContractId",
    "DocumentId",
    "FilePath",
    "FingerprintHash",
    "MetricName",
    "ModuleId",
    "SSoT_Key",
    "SessionId",
    "TaskId",
    "TokenCount",
]

TaskId = NewType("TaskId", str)
"""任务唯一标识符——格式 T-N-MM 或 T-INF-NNN。"""

ModuleId = NewType("ModuleId", str)
"""模块标识符——格式 MOD-{DOMAIN}-{NNN} 如 MOD-INF-016。"""

FilePath = NewType("FilePath", str)
"""相对文件路径——相对于 REPO_ROOT。"""

AbsPath = NewType("AbsPath", str)
"""绝对文件路径——完整磁盘路径。"""

SessionId = NewType("SessionId", str)
"""AI 会话标识符——跨轮次追踪同一对话上下文。"""

AgentId = NewType("AgentId", str)
"""AI Agent 标识符——如 plan / build / review / search。"""

ContractId = NewType("ContractId", str)
"""数据契约标识符——格式 CTR-{CAT}-{NNN} 如 CTR-P1-001。"""

FingerprintHash = NewType("FingerprintHash", str)
"""内容指纹 SHA-256 哈希字符串。"""

TokenCount = NewType("TokenCount", int)
"""Token 数量——4 字符 ≈ 1 token 估算。"""

BlueprintVersion = NewType("BlueprintVersion", str)
"""蓝图 SemVer 版本号——格式 MAJOR.MINOR.PATCH 如 0.2.0。"""

DocumentId = NewType("DocumentId", str)
"""文档唯一标识符——用于知识库 KE 索引。"""

MetricName = NewType("MetricName", str)
"""指标名称——如 task_completion_rate / token_usage。"""

SSoT_Key = NewType("SSoT_Key", str)
"""SSoT 注册表中的唯一键——防命名冲突。"""
