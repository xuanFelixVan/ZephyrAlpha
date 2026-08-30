# [A_module] module_id=MOD-SHR-io | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [TTL] permanent
"""
shared.io — auto-generated package init.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: __init__.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 content_fingerprint, file_utils, frontmatter_utils, io_cache, paths, serial…
#   desc: __init__ import L0；__all__ 9 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（9 符号）
#   name_en: __all__
#   intro: content_fingerprint, file_utils, frontmatter_utils, io_cache, paths, serializat…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

# P3-1.1 治本（#ARCH-P3-FOLLOWUP-TODOS-001 裁定 A，2026-07-20）：
# 显式 import workspace_telemetry，使其可通过 `from zephyr.shared.io import workspace_telemetry` 访问。
# 提取自 session_worktree._log_workspace_op，作为跨域共享遥测 API。
from . import workspace_telemetry  # noqa: E402

__all__ = [
    "content_fingerprint",
    "file_utils",
    "frontmatter_utils",
    "io_cache",
    "paths",
    "serialization",
    "streaming_reader",
    "workspace_telemetry",
    "yaml_utils",
]
