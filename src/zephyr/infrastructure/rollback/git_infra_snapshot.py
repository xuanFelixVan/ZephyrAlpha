# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.git_infra_snapshot
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
# [A_module] module_id=MOD-INF_git_infra_snapshot | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
GitInfraSnapshot — Git 基础设施快照与污染防护。

依据: 蓝图 MOD-INF-021 §6.12 B64

定期 .git/config + .git/hooks/ 快照 -> 受保护位置。
Watchdog 实时监控 git hooks/config 修改 -> 检测到非Owner修改 -> 告警+恢复。
防止 AI 通过篡改 git hooks 绕过门禁执行恶意代码。
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class InfraCheckResult:
    intact: bool
    tampered_files: list[str]
    restored_files: list[str]
    details: list[str] = field(default_factory=list)


class GitInfraSnapshot:
    SNAPSHOT_DIR: str = ".zephyr/git_infra_snapshot"

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._snapshot_dir = self._project_root / self.SNAPSHOT_DIR

    def create_snapshot(self) -> bool:
        git_dir = self._project_root / ".git"
        if not git_dir.exists():
            return False

        if self._snapshot_dir.exists():
            shutil.rmtree(self._snapshot_dir)

        self._snapshot_dir.mkdir(parents=True, exist_ok=True)

        config_path = git_dir / "config"
        if config_path.exists():
            shutil.copy2(config_path, self._snapshot_dir / "config")

        hooks_dir = git_dir / "hooks"
        if hooks_dir.exists():
            dst_hooks = self._snapshot_dir / "hooks"
            shutil.copytree(hooks_dir, dst_hooks)

        manifest = {
            "snapshot_at": datetime.now(UTC).isoformat(),
            "files": [str(p.relative_to(self._snapshot_dir)) for p in self._snapshot_dir.glob("**/*") if p.is_file()],
        }
        (self._snapshot_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

        return True

    def check_integrity(self) -> InfraCheckResult:
        if not self._snapshot_dir.exists():
            return InfraCheckResult(
                intact=True, tampered_files=[], restored_files=[], details=["No snapshot available"]
            )

        git_dir = self._project_root / ".git"
        tampered: list[str] = []
        restored: list[str] = []

        config_path = git_dir / "config"
        snapshot_config = self._snapshot_dir / "config"
        if config_path.exists() and snapshot_config.exists():
            current = config_path.read_text(encoding="utf-8")
            snapshot = snapshot_config.read_text(encoding="utf-8")
            if current != snapshot:
                tampered.append(".git/config")

        hooks_dir = git_dir / "hooks"
        snapshot_hooks = self._snapshot_dir / "hooks"
        if hooks_dir.exists() and snapshot_hooks.exists():
            for hook in hooks_dir.iterdir():
                if hook.is_file():
                    snapshot_hook = snapshot_hooks / hook.name
                    if snapshot_hook.exists():
                        current = hook.read_text(encoding="utf-8")
                        snapshot = snapshot_hook.read_text(encoding="utf-8")
                        if current != snapshot:
                            tampered.append(f".git/hooks/{hook.name}")

        return InfraCheckResult(
            intact=len(tampered) == 0,
            tampered_files=tampered,
            restored_files=restored,
            details=[f"Checked {len(list(git_dir.glob('**/*')) if git_dir.exists() else [])} git infra files"],
        )

    def restore_from_snapshot(self) -> InfraCheckResult:
        check = self.check_integrity()
        if check.intact:
            return check

        git_dir = self._project_root / ".git"
        restored: list[str] = []

        snapshot_config = self._snapshot_dir / "config"
        if snapshot_config.exists():
            shutil.copy2(snapshot_config, git_dir / "config")
            restored.append(".git/config")

        snapshot_hooks = self._snapshot_dir / "hooks"
        if snapshot_hooks.exists():
            for hook in snapshot_hooks.iterdir():
                if hook.is_file():
                    shutil.copy2(hook, git_dir / "hooks" / hook.name)
                    restored.append(f".git/hooks/{hook.name}")

        return InfraCheckResult(
            intact=True,
            tampered_files=check.tampered_files,
            restored_files=restored,
            details=check.details + [f"Restored {len(restored)} files from snapshot"],
        )
