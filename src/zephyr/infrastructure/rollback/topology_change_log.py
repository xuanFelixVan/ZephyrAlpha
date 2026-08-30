# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.topology_change_log
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
TopologyChangeLog — 分支拓扑变更日志。

依据: 蓝图 MOD-INF-021 §6.12 B63

记录分支操作 (merge/rebase/cherry-pick/branch delete):
    topology_change_log -> 回滚时可重建操作前分支拓扑。
    git reflog 恢复被删除的分支。
    zephyr rollback --branch-topology 回滚分支级操作。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: project_root 参数
#   fields: 参数 project_root（无注解）
#   code: topology_change_log.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① TopologyChangeLog
#   name_en: TopologyChangeLog
#   intro: class TopologyChangeLog 源码 L92-L215
#   desc: 公共方法（定义序）: log_path, project_root, record, restore_branch, get_history, get_last_change_for, snapshot_current…
#   inputs: project_root
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: TopologyChangeLog
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging

from zephyr.shared.infra.process_pool import run_subprocess_hidden

logger = logging.getLogger(__name__)

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any


class TopologyOp(str, Enum):
    MERGE = "merge"
    REBASE = "rebase"
    CHERRY_PICK = "cherry_pick"
    BRANCH_DELETE = "branch_delete"
    BRANCH_CREATE = "branch_create"
    RESET = "reset"


@dataclass
class TopologyChange:
    op: TopologyOp
    branch: str
    target: str
    before_sha: str
    after_sha: str
    timestamp_utc: str
    details: dict[str, Any] = field(default_factory=dict)


class TopologyChangeLog:
    LOG_FILE: str = ".zephyr/topology_change_log.jsonl"

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._log_path = self._project_root / self.LOG_FILE

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def log_path(self):
        """只读：log_path（Stage 4 公共化）。"""
        return self._log_path

    @log_path.setter
    def log_path(self, value):
        """写入：log_path（Stage 4 公共化）。"""
        self._log_path = value

    @property
    def project_root(self):
        """只读：project_root（Stage 4 公共化）。"""
        return self._project_root

    @project_root.setter
    def project_root(self, value):
        """写入：project_root（Stage 4 公共化）。"""
        self._project_root = value

    def record(self, change: TopologyChange) -> None:
        entry = {
            "op": change.op.value,
            "branch": change.branch,
            "target": change.target,
            "before_sha": change.before_sha,
            "after_sha": change.after_sha,
            "timestamp_utc": change.timestamp_utc,
            "details": change.details,
        }
        self._log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def restore_branch(self, branch_name: str) -> bool:
        try:
            result = run_subprocess_hidden(
                ["git", "reflog", f"{branch_name}", "--format=%H", "-1"],
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=5,
            )
            sha = result.stdout.strip()
            if sha:
                run_subprocess_hidden(
                    ["git", "branch", branch_name, sha],
                    cwd=str(self._project_root),
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                return True
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("suppressed error in topology_change_log", exc_info=True)
        return False

    def get_history(self, limit: int = 20) -> list[TopologyChange]:
        if not self._log_path.exists():
            return []

        changes: list[TopologyChange] = []
        with open(self._log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    changes.append(
                        TopologyChange(
                            op=TopologyOp(entry["op"]),
                            branch=entry["branch"],
                            target=entry["target"],
                            before_sha=entry["before_sha"],
                            after_sha=entry["after_sha"],
                            timestamp_utc=entry["timestamp_utc"],
                            details=entry.get("details", {}),
                        )
                    )
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue

        return changes[-limit:]

    def get_last_change_for(self, branch: str) -> TopologyChange | None:
        history = self.get_history()
        for change in reversed(history):
            if change.branch == branch:
                return change
        return None

    def snapshot_current_topology(self) -> dict[str, Any]:
        try:
            branches = run_subprocess_hidden(
                ["git", "branch", "--format=%(refname:short)"],
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=5,
            )
            current_branch = run_subprocess_hidden(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=5,
            )

            return {
                "branches": [b for b in branches.stdout.strip().split("\n") if b],
                "current": current_branch.stdout.strip(),
                "snapshot_at": datetime.now(UTC).isoformat(),
            }
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            return {}
