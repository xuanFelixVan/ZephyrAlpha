# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] zephyr.infrastructure.auto_fix_engine.alignment_syncer
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] engine.py;MOD-INF-023(drift-detector)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 蓝图为SSoT;只同步代码->蓝图方向;不自动修改蓝图
# [MODIFY-GUARD] blueprint.md §3;_fixer-registry.yaml alignment_syncer段
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AlignmentSyncError
# [TESTS] tests/auto-fix-engine/test_alignment_syncer.py
# [A_module] module_id=MOD-INF_alignment_syncer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Any

from zephyr.infrastructure.auto_fix_engine.models import (
    BaseFixer,
    FixAction,
    FixConfidence,
    FixLevel,
    FixStatus,
    ValidationResult,
)

from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)


class AlignmentSyncer(BaseFixer):

    def __init__(self) -> None:
        super().__init__(
            fixer_id="alignment_syncer",
            action_type="alignment_sync",
            level=FixLevel.L1_RULE,
            dimension="DIM-ALIGNMENT-001",
            description="同步蓝图与代码差异",
        )

    def scan(self) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        repo_root = REPO_ROOT  # 5.12.5 修复：改用 REPO_ROOT 真源（原 os.getcwd() 硬假设cwd是项目根）
        for blueprint in (repo_root / "docs" / "03_modules").rglob("blueprint.md"):
            try:
                content = blueprint.read_text(encoding="utf-8")
                file_table_match = re.search(r"##\s*§0.*?(?=##|\Z)", content, re.DOTALL)
                if not file_table_match:
                    continue
                table_text = file_table_match.group(0)
                code_paths = re.findall(r"`(src/zephyr/[^\s`]+\.py)`", table_text)
                for code_path in code_paths:
                    full_path = repo_root / code_path
                    if not full_path.exists():
                        findings.append(
                            {
                                "blueprint": str(blueprint),
                                "declared_path": code_path,
                                "type": "code_missing_from_blueprint",
                            }
                        )
            except Exception:
                continue
        return findings

    def fix(self, target: str, dry_run: bool = False) -> FixAction:
        action = FixAction(
            action_type=self.action_type,
            level=self.level,
            target=target,
            confidence=FixConfidence.MEDIUM,
        )
        target_path = Path(target)
        if not target_path.exists():
            action.status = FixStatus.FAILED
            action.metadata["error"] = "Target not found"
            return action
        try:
            content = target_path.read_text(encoding="utf-8")
            original = content
            header_match = re.match(r"^#\s*\[BLUEPRINT\]\s+(.+?)(?:\n|$)", content, re.MULTILINE)
            if not header_match:
                action.status = FixStatus.COMPLETED
                action.metadata["note"] = "No [BLUEPRINT] header found - nothing to sync"
                return action
            blueprint_ref = header_match.group(1).strip()
            parts = blueprint_ref.split("|")
            if len(parts) >= 2:
                blueprint_path = parts[0].strip()
                section = parts[1].strip() if len(parts) > 1 else ""
                repo_root = REPO_ROOT  # 5.12.5 修复：改用 REPO_ROOT 真源（原 os.getcwd() 硬假设cwd是项目根）
                full_bp = repo_root / blueprint_path
                if full_bp.exists():
                    bp_content = full_bp.read_text(encoding="utf-8")
                    module_match = re.search(
                        rf"`{re.escape(str(target_path.relative_to(repo_root)).replace(chr(92), '/'))}`", bp_content
                    )
                    action.metadata["blueprint_exists"] = True
                    action.metadata["referenced_in_blueprint"] = module_match is not None
            action.status = FixStatus.COMPLETED
            action.metadata["sync_direction"] = "code_to_blueprint"
            action.metadata["auto_fix"] = False
            action.metadata["reason"] = "Alignment sync requires human review - only reporting discrepancies"
        except Exception as exc:
            action.status = FixStatus.FAILED
            action.metadata["error"] = str(exc)
        return action

    def validate(self, target: str) -> ValidationResult:
        target_path = Path(target)
        if not target_path.exists():
            return ValidationResult(valid=False, check_name="alignment_sync", evidence="", error="Target not found")
        try:
            content = target_path.read_text(encoding="utf-8")
            if "[BLUEPRINT]" not in content:
                return ValidationResult(
                    valid=False,
                    check_name="alignment_sync",
                    evidence="No [BLUEPRINT] header",
                    error="Missing blueprint reference",
                )
            return ValidationResult(valid=True, check_name="alignment_sync", evidence="[BLUEPRINT] header present")
        except Exception as exc:
            return ValidationResult(valid=False, check_name="alignment_sync", evidence="", error=str(exc))

    def rollback(self, target: str) -> bool:
        return False
