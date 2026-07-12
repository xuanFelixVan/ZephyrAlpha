# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.grandfather_manager
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/rule_enforcement/test_grandfather_manager.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/governance/code_dedup/test_grandfather_manager.py
# [A_module] module_id=MOD-GCQ_grandfather_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Grandfather 三定律 — 古老重复管理.

职责：
  - 第一定律：≥30天 -> auto_fix=false（永不自动修复，只能 manual review + --override-grandfather）
  - 第二定律：≥60天 -> severity=informational -> 不参与 Health Score -> fossilize()
  - 第三定律考古豁免：3项测试通过 -> --override-grandfather 可覆盖
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import yaml


@dataclass
class GrandfatherEntry:
    dup_group_id: str
    function_name: str
    file_path: str = ""
    first_detected_at: str = ""
    age_days: int = 0
    is_fossil: bool = False
    auto_fix: bool = True
    severity: str = "medium"
    archaeology_tests: dict[str, bool] = field(
        default_factory=lambda: {
            "git_log_found_original": False,
            "all_callers_have_tests": False,
            "revert_one_command": False,
        }
    )
    manual_override: bool = False


class GrandfatherManager:
    """Grandfather 三定律管理器."""

    _GRANDFATHER_AGE_DAYS: int = 30
    _FOSSIL_AGE_DAYS: int = 60

    def __init__(self, registry_path: str | Path | None = None) -> None:
        if registry_path is None:
            registry_path = Path("data/cache/grandfather-registry.yaml")
        self._registry_path = Path(registry_path)
        self._entries: dict[str, GrandfatherEntry] = {}
        self._load()

    def grandfather_check(self, dup_group_id: str, first_detected_at: str) -> tuple[bool, str]:
        """第一定律：≥30天 -> auto_fix=false."""
        try:
            detected = datetime.fromisoformat(first_detected_at.replace("Z", "+00:00"))
        except ValueError:
            return True, "invalid_date"

        age = (datetime.now(UTC) - detected.replace(tzinfo=UTC)).days
        if age >= self._GRANDFATHER_AGE_DAYS:
            return False, f"grandfather_protected: {age}days≥30days——禁止自动修复"
        return True, "auto_fix_allowed"

    def fossilize(
        self,
        dup_group_id: str,
        function_name: str,
        file_path: str = "",
        first_detected_at: str = "",
    ) -> GrandfatherEntry | None:
        """第二定律：≥60天 -> severity=informational -> fossil."""
        try:
            detected = datetime.fromisoformat(first_detected_at.replace("Z", "+00:00"))
        except ValueError:
            return None

        age = (datetime.now(UTC) - detected.replace(tzinfo=UTC)).days
        if age < self._FOSSIL_AGE_DAYS:
            return None

        entry = GrandfatherEntry(
            dup_group_id=dup_group_id,
            function_name=function_name,
            file_path=file_path,
            first_detected_at=first_detected_at,
            age_days=age,
            is_fossil=True,
            auto_fix=False,
            severity="informational",
        )
        self._entries[dup_group_id] = entry
        self._save()
        return entry

    def archaeology_check(
        self,
        *,
        git_log_ok: bool = False,
        all_tests_ok: bool = False,
        rollback_ok: bool = False,
    ) -> tuple[bool, str]:
        """第三定律考古豁免：3项全部通过 -> 可 override."""
        passed = sum([git_log_ok, all_tests_ok, rollback_ok])
        if passed < 3:
            missing = []
            if not git_log_ok:
                missing.append("git_log")
            if not all_tests_ok:
                missing.append("all_callers_tests")
            if not rollback_ok:
                missing.append("rollback_plan")
            return False, f"考古测试: {passed}/3 FAIL——缺失: {', '.join(missing)}"
        return True, "考古测试: 3/3 PASS——可用 --override-grandfather"

    def override(self, dup_group_id: str, force: bool = False) -> bool:
        """Owner --override-grandfather."""
        if not force:
            return False
        entry = self._entries.get(dup_group_id)
        if entry is None:
            entry = GrandfatherEntry(
                dup_group_id=dup_group_id,
                function_name=dup_group_id,
                manual_override=True,
            )
        entry.manual_override = True
        entry.auto_fix = True
        self._entries[dup_group_id] = entry
        self._save()
        return True

    def is_fossil(self, dup_group_id: str) -> bool:
        entry = self._entries.get(dup_group_id)
        return entry is not None and entry.is_fossil

    def get_all_entries(self) -> list[GrandfatherEntry]:
        return list(self._entries.values())

    # ── 内部 ──────────────────────────────────────────────────

    def _load(self) -> None:
        self._entries.clear()
        if not self._registry_path.exists():
            return
        try:
            data = yaml.safe_load(self._registry_path.read_text(encoding="utf-8")) or {}
            for entry_data in data.get("entries", []):
                tests = entry_data.pop("archaeology_tests", {})
                entry = GrandfatherEntry(**entry_data)
                entry.archaeology_tests = {
                    "git_log_found_original": tests.get("git_log_found_original", False),
                    "all_callers_have_tests": tests.get("all_callers_have_tests", False),
                    "revert_one_command": tests.get("revert_one_command", False),
                }
                self._entries[entry.dup_group_id] = entry
        except (yaml.YAMLError, OSError):
            pass

    def _save(self) -> None:
        self._registry_path.parent.mkdir(parents=True, exist_ok=True)
        entries_data = []
        for entry in self._entries.values():
            e = entry.__dict__.copy()
            entries_data.append(e)
        data = {
            "version": "1.0.0",
            "updated_at": datetime.now(UTC).isoformat(),
            "total_entries": len(entries_data),
            "entries": entries_data,
        }
        self._registry_path.write_text(
            yaml.dump(data, allow_unicode=True, default_flow_style=False),
            encoding="utf-8",
        )
