# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §8.2 + §16 Phase 1
# [MODULE] zephyr.security.adversarial_validation.cleanup
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] validator.py; injection_engine.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] MUST achieve zero residue per RULE-FIVE; cleanup patterns: _attack_* | *.rb_backup | _temp*.py | _check*.py | data/red_blue/_temp_* | data/red_blue/checkpoint_*.yaml
# [MODIFY-GUARD] Adding cleanup patterns MUST update CLEANUP_PATTERNS; ensure_clean() MUST verify all patterns
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] CleanupVerificationError if residue remains after cleanup
# [TESTS] tests/red_blue/test_cleanup.py
# [A_module] module_id=MOD-SEC_cleanup | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

__all__: list[str] = ["Cleanup", "CleanupVerificationError"]

CLEANUP_PATTERNS: Final[list[str]] = [
    "_attack_*",
    "*.rb_backup",
    "_temp*.py",
    "_check*.py",
    "data/red_blue/_temp_*",
    "data/red_blue/checkpoint_*.yaml",
]

CLEANUP_DIRS: Final[list[Path]] = [
    Path("data/red_blue/backups"),
]


class CleanupVerificationError(RuntimeError):
    pass


class Cleanup:
    def __init__(self) -> None:
        self._backups: dict[Path, bytes] = {}

    def backup_file(self, file_path: Path) -> None:
        if file_path.exists():
            self._backups[file_path] = file_path.read_bytes()
            logger.info("backup_created file=%s", str(file_path))

    def backup_directory(self, dir_path: Path) -> None:
        if dir_path.exists():
            for f in dir_path.rglob("*"):
                if f.is_file():
                    self._backups[f] = f.read_bytes()
            logger.info("directory_backed_up dir=%s count=%d", str(dir_path), len(self._backups))

    def cleanup_artifact(self, artifact_path: Path) -> None:
        if artifact_path.exists():
            if artifact_path.is_file():
                artifact_path.unlink()
            elif artifact_path.is_dir():
                shutil.rmtree(artifact_path)
            logger.info("cleanup_artifact path=%s", str(artifact_path))

    def ensure_clean(self) -> bool:
        residue: list[str] = []
        for pattern in CLEANUP_PATTERNS:
            for p in Path().glob(pattern):
                residue.append(str(p))
        for d in CLEANUP_DIRS:
            if d.exists():
                for f in d.glob("_attack_*"):
                    residue.append(str(f))

        if residue:
            logger.warning("cleanup_residue_found residue=%s", residue)
            for p in residue:
                try:
                    path = Path(p)
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        shutil.rmtree(path)
                except OSError:
                    pass

        residue_after = []
        for pattern in CLEANUP_PATTERNS:
            for p in Path().glob(pattern):
                residue_after.append(str(p))
        for d in CLEANUP_DIRS:
            if d.exists():
                for f in d.glob("_attack_*"):
                    residue_after.append(str(f))

        if residue_after:
            raise CleanupVerificationError(f"Residue remains after cleanup: {residue_after}")

        return True

    def restore_backups(self) -> bool:
        for path, content in self._backups.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            logger.info("backup_restored file=%s", str(path))
        self._backups.clear()
        return True

    def verified(self) -> bool:
        try:
            self.ensure_clean()
            return True
        except CleanupVerificationError:
            return False
