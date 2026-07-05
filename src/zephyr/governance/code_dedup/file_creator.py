# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.file_creator
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/file/test_file_creator.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_file_creator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""文件创建清单执行器 — 验证所有源/测试/数据文件存在性."""

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class FileStatus:
    path: str = ""
    exists: bool = False


class FileCreator:
    """文件创建清单验证器."""

    _SOURCE_FILES: list[str] = [
        "__init__.py",
        "cache_manager.py",
        "diff_detector.py",
        "signature_matcher.py",
        "scanner.py",
        "degradation.py",
        "config.py",
        "report.py",
        "health-monitor.py",
        "ast_comparator.py",
        "extraction_safety.py",
        "auto_fixer.py",
        "doom_loop_guard.py",
        "shared_lifecycle_manager.py",
        "monoculture_guard.py",
        "grandfather_manager.py",
        "atomic_fixer.py",
        "debt_projector.py",
        "hotspot_tracker.py",
        "shadow_verifier.py",
        "shared_evolver.py",
        "false_negative_auditor.py",
        "policy_tree_validator.py",
        "simplicity_auditor.py",
        "fifteen_dimension_auditor.py",
        "risk_mitigator.py",
        "phase_executor.py",
    ]

    _TEST_FILES: list[str] = [
        "test_config.py",
        "test_scanner_raw.py",
        "test_scanner_cross.py",
        "test_micro_clone.py",
        "test_degradation_edge.py",
        "test_self_scan_integrity.py",
    ]

    _DATA_FILES: list[str] = [
        "function-cache.json",
        "doom-loop-freeze-list.json",
        "shared-lifecycle.yaml",
        "monoculture-risk.yaml",
        "grandfather-registry.yaml",
        "full-scan-report-baseline.yaml",
        "micro-clone-baseline.yaml",
    ]

    def __init__(
        self,
        package_dir: str | Path | None = None,
        test_dir: str | Path | None = None,
        data_dir: str | Path | None = None,
    ) -> None:
        if package_dir is None:
            package_dir = Path("src/zephyr/testing/code_dedup")
        if test_dir is None:
            test_dir = Path("tests/test_code_dedup_engine")
        if data_dir is None:
            data_dir = Path("data/cache")
        self._pkg = Path(package_dir)
        self._test = Path(test_dir)
        self._data = Path(data_dir)

    def verify_all(self) -> dict[str, Any]:
        """验证所有文件存在性."""
        source_status = [FileStatus(path=f, exists=(self._pkg / f).exists()) for f in self._SOURCE_FILES]
        test_status = [FileStatus(path=f, exists=(self._test / f).exists()) for f in self._TEST_FILES]
        data_status = [FileStatus(path=f, exists=(self._data / f).exists()) for f in self._DATA_FILES]

        src_ok = sum(1 for s in source_status if s.exists)
        test_ok = sum(1 for s in test_status if s.exists)
        data_ok = sum(1 for s in data_status if s.exists)

        return {
            "generated_at": datetime.now(UTC).isoformat(),
            "source_files": f"{src_ok}/{len(self._SOURCE_FILES)}",
            "test_files": f"{test_ok}/{len(self._TEST_FILES)}",
            "data_files": f"{data_ok}/{len(self._DATA_FILES)}",
            "missing": (
                [s.path for s in source_status if not s.exists]
                + [s.path for s in test_status if not s.exists]
                + [s.path for s in data_status if not s.exists]
            ),
        }
