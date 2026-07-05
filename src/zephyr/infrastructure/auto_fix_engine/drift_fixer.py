# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] zephyr.infrastructure.auto_fix_engine.drift_fixer
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] engine.py;MOD-INF-023(drift-detector);MOD-INF-021(rollback)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 漂移修复MUST通过DriftBudgetLink;修复后MUST验证
# [MODIFY-GUARD] blueprint.md §3;_fixer-registry.yaml drift_fixer段
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftFixError
# [TESTS] tests/auto-fix-engine/test_drift_fixer.py
# [A_module] module_id=MOD-INF_drift_fixer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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


class DriftFixer(BaseFixer):

    def __init__(self) -> None:
        super().__init__(
            fixer_id="drift_fixer",
            action_type="drift_fix",
            level=FixLevel.L1_RULE,
            dimension="DIM-DRIFT-001",
            description="修复配置/结构漂移",
        )

    def scan(self) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        repo_root = REPO_ROOT  # 5.12.5 修复：改用 REPO_ROOT 真源（原 os.getcwd() 硬假设cwd是项目根）
        for config_file in repo_root.rglob("*.yaml"):
            if ".ailocks" in str(config_file) or "node_modules" in str(config_file):
                continue
            try:
                content = config_file.read_text(encoding="utf-8")
                version_matches = re.findall(r"version:\s*[\"']?(\d+\.\d+\.\d+)[\"']?", content)
                if not version_matches:
                    continue
                for v in version_matches:
                    if v.startswith("0."):
                        findings.append(
                            {
                                "file": str(config_file),
                                "version": v,
                                "type": "pre_release_version",
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
            fixes_applied: list[str] = []
            content = self._fix_stale_timestamps(content, fixes_applied)
            content = self._fix_inconsistent_keys(content, fixes_applied)
            if content != original:
                action.before = original
                action.after = content
                action.metadata["fixes"] = fixes_applied
                if not dry_run:
                    tmp_path = f"{target}.{os.getpid()}.tmp"
                    try:
                        with open(tmp_path, "w", encoding="utf-8") as f:
                            f.write(content)
                        os.replace(tmp_path, target)
                    except PermissionError:
                        try:
                            os.remove(tmp_path)
                        except OSError:
                            pass
                        action.status = FixStatus.FAILED
                        return action
                action.status = FixStatus.COMPLETED
            else:
                action.status = FixStatus.COMPLETED
                action.metadata["note"] = "No drift detected"
        except Exception as exc:
            action.status = FixStatus.FAILED
            action.metadata["error"] = str(exc)
        return action

    def _fix_stale_timestamps(self, content: str, fixes: list[str]) -> str:
        from datetime import UTC, datetime

        now_str = datetime.now(UTC).strftime("%Y-%m-%d")
        pattern = r'last_updated:\s*["\']?\d{4}-\d{2}-\d{2}["\']?'
        matches = list(re.finditer(pattern, content))
        if len(matches) > 1:
            first_date = re.search(r"(\d{4}-\d{2}-\d{2})", matches[0].group())
            if first_date:
                for m in matches[1:]:
                    old_date = re.search(r"(\d{4}-\d{2}-\d{2})", m.group())
                    if old_date and old_date.group(1) != first_date.group(1):
                        content = content.replace(m.group(), f'last_updated: "{first_date.group(1)}"')
                        fixes.append(f"Unified last_updated to {first_date.group(1)}")
        return content

    def _fix_inconsistent_keys(self, content: str, fixes: list[str]) -> str:
        lines = content.split("\n")
        fixed_lines: list[str] = []
        for line in lines:
            stripped = line.lstrip()
            if stripped.startswith("- ") and ":" in stripped:
                key = stripped.split(":")[0].strip().lstrip("- ").strip()
                if key and key != key.lower() and not key[0].isupper():
                    new_line = line.replace(key, key.lower())
                    if new_line != line:
                        fixes.append(f"Normalized key: {key} -> {key.lower()}")
                        line = new_line
            fixed_lines.append(line)
        return "\n".join(fixed_lines)

    def validate(self, target: str) -> ValidationResult:
        target_path = Path(target)
        if not target_path.exists():
            return ValidationResult(valid=False, check_name="drift_fix", evidence="", error="Target not found")
        try:
            content = target_path.read_text(encoding="utf-8")
            import yaml

            yaml.safe_load(content)
            return ValidationResult(valid=True, check_name="drift_fix", evidence="YAML parseable")
        except yaml.YAMLError as exc:
            return ValidationResult(valid=False, check_name="drift_fix", evidence="", error=f"YAML error: {exc}")
        except Exception as exc:
            return ValidationResult(valid=False, check_name="drift_fix", evidence="", error=str(exc))

    def rollback(self, target: str) -> bool:
        return False
