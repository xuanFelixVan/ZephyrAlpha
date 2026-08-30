# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §workspace-telemetry
# [MODULE] zephyr.shared.io.workspace_telemetry
# [DOMAIN] D_SHARED
# [DEPENDENCIES] stdlib (json, hashlib, logging, datetime); zephyr.shared.io.paths (anchor_main_root)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.session_worktree (_log_workspace_op thin wrapper); zephyr.governance.semantic_audit.self_healer (_rollback telemetry)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 遥测降级不阻断主流程——所有 IO/路径异常仅 debug 日志；写入 worktree_ops_log.jsonl（主仓库 .runtime/ 下，非 worktree 内）
# [MODIFY-GUARD] log_workspace_op / compute_content_hash 公共 API 签名
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] log_workspace_op 永不抛异常（降级为 debug 日志）；compute_content_hash 文件不存在/读取失败返回空字符串
# [TESTS] tests/governance/test_workspace_telemetry_shared.py
# [A_module] module_id=MOD-INF-016 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
workspace_telemetry.py — 主工作区文件操作遥测公共 API（#ARCH-P3-FOLLOWUP-TODOS-001 裁定 A，2026-07-19）

病根
----
原 ``_log_workspace_op`` 定义在 ``zephyr.gov_enforcement.rule_bridge.session_worktree``（D_GOV_ENFORCEMENT），
是 private 函数。``self_healer._rollback``（在 ``zephyr.governance.semantic_audit``，D_GOV_AUDIT）需调用它
记录 ``git restore`` 遥测，但跨域 import 会违反架构边界（D_GOV_AUDIT → D_GOV_ENFORCEMENT 依赖方向错误）。

原"解法"是 ``audit_worktree_ops_telemetry.py`` 加 ``"rollback"`` 关键词豁免——掩盖症状，破坏了项目记忆
硬约束："主工作区文件级擦除（restore/unlink/quarantine）操作必须全量纳入 worktree_ops_log.jsonl 遥测"。

治本（裁定 A）
-------------
将 ``_log_workspace_op`` + ``_compute_content_hash`` 提取到 ``shared.io.workspace_telemetry``（D_SHARED，
跨域共享层），作为公共 API ``log_workspace_op()`` / ``compute_content_hash()``。

- D_GOV_ENFORCEMENT → D_SHARED：向下依赖，方向正确
- D_GOV_AUDIT → D_SHARED：向下依赖，方向正确
- 任何域都可调用 shared API 补遥测，不再需要跨域 import 或豁免

API
---
- ``log_workspace_op(op, session_id, source, root, file="", backup_path="", content_hash="") -> None``
- ``compute_content_hash(path: Path) -> str``

Usage::

    from zephyr.shared.io.workspace_telemetry import log_workspace_op, compute_content_hash
    from zephyr.shared.io.paths import find_repo_root
    from pathlib import Path

    # 计算文件内容 hash（移送/恢复前）
    ch = compute_content_hash(Path("src/foo.py"))

    # 记录遥测（root 走 paths 真源，禁止硬编码仓根路径）
    log_workspace_op(
        op="git_restore_rollback",
        session_id="sess-xxx",
        source="self_healer._rollback",
        root=find_repo_root(),
        file="src/foo.py",
        content_hash=ch,
    )

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: op 参数
#   fields: 参数 op，类型注解 str
#   code: workspace_telemetry.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: session_id 参数
#   fields: 参数 session_id，类型注解 str
#   code: workspace_telemetry.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: source 参数
#   fields: 参数 source，类型注解 str
#   code: workspace_telemetry.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: root 参数
#   fields: 参数 root，类型注解 Path
#   code: workspace_telemetry.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① log_workspace_op
#   name_en: log_workspace_op
#   intro: 主工作区文件操作遥测（ 扩展 content_hash； 裁定 A 提取到 shared）。
#   desc: 主工作区文件操作遥测（ 扩展 content_hash； 裁定 A 提取到 shared）。 记录文件级 stash/quarantine/restore/rollback 操作…；源码 L127-L172
#   inputs: op session_id source root file backup_path content_hash
#   outputs: 返回值
# - id: A2
#   name_zh: ② compute_content_hash
#   name_en: compute_content_hash
#   intro: 计算文件内容的 sha256 hex 前 16 字符（P2-6，2026-07-19； 裁定 A 提取到 shared…
#   desc: 计算文件内容的 sha256 hex 前 16 字符（P2-6，2026-07-19； 裁定 A 提取到 shared）。 用于 ``worktree_ops_log.jsonl…；源码 L175-L194
#   inputs: path
#   outputs: str
# 层: 输出
# - id: O1
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.rule_bridge.session_worktree (_log_workspace_op thin wra…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from zephyr.shared.io.paths import anchor_main_root

logger = logging.getLogger(__name__)

__all__ = ["log_workspace_op", "compute_content_hash"]


def log_workspace_op(
    op: str,
    session_id: str,
    source: str,
    root: Path,
    file: str = "",
    backup_path: str = "",
    content_hash: str = "",
) -> None:
    """主工作区文件操作遥测（裁定#C，2026-07-19；P2-6 扩展 content_hash；#ARCH-P3-FOLLOWUP-TODOS-001 裁定 A 提取到 shared）。

    记录文件级 stash/quarantine/restore/rollback 操作到 ``worktree_ops_log.jsonl``，
    支持事后审计与恢复。

    必填字段（项目记忆硬约束：session_id / source / file / content_hash / backup_path）：
      - ``content_hash``: 操作前文件内容的 sha256 hex（前 16 字符），用于校验隔离区/
        stash 恢复后的内容完整性。空字符串表示文件不存在或无法读取（如 stash 后文件已消失）。

    降级：遥测失败仅 debug 日志，绝不阻断主流程。

    Args:
        op: 操作类型（如 ``file_quarantine`` / ``git_restore_rollback`` / ``file_stash``）。
        session_id: AI session 标识。
        source: 调用源（如 ``self_healer._rollback`` / ``session_worktree_commit``）。
        root: 仓库根路径（自动 strip worktree 前缀，写入主仓库 .runtime/）。
        file: 被操作的文件相对路径（可选）。
        backup_path: 备份/隔离区路径（可选）。
        content_hash: 操作前文件内容 sha256 hex 前 16 字符（可选，空表示文件不存在）。
    """
    try:
        main_root = anchor_main_root(Path(root))
        log_dir = main_root / ".runtime"
        log_dir.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "op": op,
            "session_id": session_id,
            "source": source,
            "file": file,
            "content_hash": content_hash,
            "backup_path": backup_path,
        }
        with open(log_dir / "worktree_ops_log.jsonl", "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001 — 遥测降级不阻断主流程
        logger.debug("workspace op telemetry failed", exc_info=True)


def compute_content_hash(path: Path) -> str:
    """计算文件内容的 sha256 hex 前 16 字符（P2-6，2026-07-19；#ARCH-P3-FOLLOWUP-TODOS-001 裁定 A 提取到 shared）。

    用于 ``worktree_ops_log.jsonl`` 的 ``content_hash`` 字段，校验隔离区/stash 恢复后的
    内容完整性。文件不存在或读取失败返回空字符串（不抛异常）。

    Args:
        path: 文件绝对路径。

    Returns:
        sha256 hex 前 16 字符；文件不存在/读取失败返回 ``""``。
    """
    try:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()[:16]
    except OSError:
        return ""
