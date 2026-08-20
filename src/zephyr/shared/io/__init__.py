# [A_module] module_id=MOD-SHR-io | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [TTL] permanent
"""shared.io — auto-generated package init."""

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
