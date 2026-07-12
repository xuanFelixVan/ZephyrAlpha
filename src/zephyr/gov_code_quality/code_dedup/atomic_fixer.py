# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.atomic_fixer
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/rule_enforcement/test_atomic_fixer.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/governance/code_dedup/test_atomic_fixer.py
# [A_module] module_id=MOD-GCQ_atomic_fixer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""原子性修复引擎 — WAL 式 PREFLIGHT -> CHECKPOINT -> APPLY -> RECOVER.

职责：
  - PREFLIGHT：生成 fix_plan.yaml + 所有 diff + plan_hash SHA256
  - CHECKPOINT：备份受影响文件到 fix_checkpoint_{plan_hash}.tar.gz
  - APPLY：按依赖顺序逐文件修改 + 每步 SHA256 验证（不匹配-> ABORT -> RECOVER）
  - RECOVER：引擎启动时扫描残留 tar.gz -> 自动恢复原始文件
"""

from __future__ import annotations

import hashlib
import json
import tarfile
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import yaml


class FixStepStatus:
    PENDING = "pending"
    SKIPPED = "skipped"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class FixStep:
    step: int = 0
    action: str = ""
    file: str = ""
    expected_sha256: str = ""
    depends_on: list[int] = field(default_factory=list)
    completed: bool = False
    diff: str = ""


@dataclass
class FixPlan:
    plan_hash: str = ""
    dup_id: str = ""
    status: str = FixStepStatus.PENDING
    steps: list[FixStep] = field(default_factory=list)
    completion_marker: str = ""
    created_at: str = ""


class AtomicFixer:
    """WAL 式原子性修复引擎."""

    _CHECKPOINT_DIR: Path = Path("data/cache")

    def __init__(self, project_root: str | Path | None = None) -> None:
        self._project_root = Path(project_root) if project_root else Path.cwd()
        self._checkpoint_dir = self._CHECKPOINT_DIR

    def preflight(self, dup_id: str, steps: list[FixStep]) -> FixPlan:
        """PREFLIGHT：生成 fix_plan.yaml + plan_hash SHA256."""
        plan_data = {
            "dup_id": dup_id,
            "status": FixStepStatus.PENDING,
            "steps": [s.__dict__ for s in steps],
            "completion_marker": "",
            "created_at": datetime.now(UTC).isoformat(),
        }

        payload = json.dumps(plan_data, ensure_ascii=False, sort_keys=True)
        plan_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]

        plan = FixPlan(
            plan_hash=plan_hash,
            dup_id=dup_id,
            steps=steps,
            created_at=plan_data["created_at"],
        )

        self._save_fix_plan(plan)
        return plan

    def checkpoint(self, plan: FixPlan) -> str:
        """CHECKPOINT：备份所有受影响文件到 tar.gz."""
        affected_files = self._collect_affected_files(plan)
        if not affected_files:
            return ""

        checkpoint_name = f"fix_checkpoint_{plan.plan_hash}.tar.gz"
        checkpoint_path = self._checkpoint_dir / checkpoint_name
        self._checkpoint_dir.mkdir(parents=True, exist_ok=True)

        manifest = {
            "plan_hash": plan.plan_hash,
            "dup_id": plan.dup_id,
            "created_at": datetime.now(UTC).isoformat(),
            "files": [],
        }

        with tarfile.open(str(checkpoint_path), "w:gz") as tar:
            for file_path in affected_files:
                abs_path = self._project_root / file_path
                if abs_path.exists():
                    tar.add(str(abs_path), arcname=file_path)
                    manifest["files"].append(
                        {
                            "file": file_path,
                            "sha256": self._file_sha256(abs_path),
                        }
                    )

        manifest_path = self._checkpoint_dir / f"manifest_{plan.plan_hash}.json"
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return str(checkpoint_path)

    def apply(self, plan: FixPlan) -> tuple[bool, str]:
        """APPLY：按依赖顺序逐文件修改 + SHA256 验证."""
        completed_steps: set[int] = set()

        for step in plan.steps:
            deps = set(step.depends_on)
            unsatisfied = deps - completed_steps
            if unsatisfied:
                step.completed = False
                continue

            abs_path = self._project_root / step.file
            if abs_path.exists():
                current_sha = self._file_sha256(abs_path)
                if current_sha != step.expected_sha256 and step.expected_sha256:
                    self._abort(plan, f"Step {step.step}: SHA256 mismatch for {step.file}")
                    self.recover(plan.plan_hash)
                    return False, f"Step {step.step}: SHA256 mismatch"

                abs_path.write_text(step.diff, encoding="utf-8")

            step.completed = True
            completed_steps.add(step.step)

        plan.status = FixStepStatus.COMPLETED
        plan.completion_marker = datetime.now(UTC).isoformat()
        self._save_fix_plan(plan)
        self._cleanup_checkpoint(plan.plan_hash)
        return True, "FIX_APPLIED"

    def recover(self, plan_hash: str) -> bool:
        """RECOVER：从 tar.gz 恢复原始文件."""
        checkpoint_name = f"fix_checkpoint_{plan_hash}.tar.gz"
        checkpoint_path = self._checkpoint_dir / checkpoint_name
        if not checkpoint_path.exists():
            return False

        try:
            with tarfile.open(str(checkpoint_path), "r:gz") as tar:
                for member in tar.getmembers():
                    dest = self._project_root / member.name
                    if member.isfile():
                        f = tar.extractfile(member)
                        if f:
                            data = f.read()
                            dest.write_bytes(data)
            return True
        except Exception:
            return False

    def scan_and_recover_all(self) -> list[str]:
        """引擎启动时扫描所有残留 tar.gz -> 自动恢复."""
        recovered: list[str] = []
        for checkpoint_file in sorted(self._checkpoint_dir.glob("fix_checkpoint_*.tar.gz")):
            plan_hash = checkpoint_file.stem.replace("fix_checkpoint_", "")
            if self.recover(plan_hash):
                recovered.append(plan_hash)
        return recovered

    # ── 内部 ──────────────────────────────────────────────────

    def _collect_affected_files(self, plan: FixPlan) -> list[str]:
        files: set[str] = set()
        for step in plan.steps:
            files.add(step.file)
        return sorted(files)

    def _save_fix_plan(self, plan: FixPlan) -> None:
        plan_path = self._checkpoint_dir / f"fix_plan_{plan.plan_hash}.yaml"
        data = {
            "plan_hash": plan.plan_hash,
            "dup_id": plan.dup_id,
            "status": plan.status,
            "used_at_generated_at": plan.created_at,
            "steps": [s.__dict__ for s in plan.steps],
            "completion_marker": plan.completion_marker,
        }
        plan_path.write_text(
            yaml.dump(data, allow_unicode=True, default_flow_style=False),
            encoding="utf-8",
        )

    def _abort(self, plan: FixPlan, reason: str) -> None:
        plan.status = f"ABORTED: {reason}"
        self._save_fix_plan(plan)

    def _cleanup_checkpoint(self, plan_hash: str) -> None:
        for f in self._checkpoint_dir.glob(f"*{plan_hash}*"):
            try:
                f.unlink()
            except OSError:
                pass

    @staticmethod
    def _file_sha256(path: Path) -> str:
        if not path.exists():
            return ""
        return hashlib.sha256(path.read_bytes()).hexdigest()
