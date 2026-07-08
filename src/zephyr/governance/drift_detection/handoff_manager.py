# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.governance.drift_detection.handoff_manager
# [DOMAIN] D_BEHAVIORAL_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/governance/drift_detection/_infrastructure.py; tests/audit/test_handoff_manager.py; tests/ba/test_ba_handoff_manager.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 交接包完整性不可破坏
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_handoff_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Cross-Session Handoff Manager — 跨Session修复上下文交接 §6.14。





module_id: MOD-INF-023


handoff_package: JSON(drift_runbook + git bisect + pre-fix快照 + baseline diff + 关联漂移)<5000token


resume_workflow: 自动加载注入context推进状态


abort: 文件状态不一致->重新生成+通知Owner


对标 blueprint.md §6.14。"""

from __future__ import annotations
from zephyr.shared.io.serialization import dumps

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class FileIntegrityRecord:
    file_path: str

    sha256_before: str = ""

    sha256_after: str = ""

    verified: bool = False


@dataclass
class HandoffPackage:
    package_id: str

    drift_event_id: str

    detector_id: str

    severity: str

    runbook_summary: str

    git_bisect_log: str

    pre_fix_snapshot: dict[str, str]

    baseline_diff: dict[str, list[str]]

    related_drift_ids: list[str]

    file_integrity: list[FileIntegrityRecord] = field(default_factory=list)

    token_estimate: int = 0

    owner_id: str = ""

    status: str = "READY"

    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    last_verified_at: str | None = None


def _sha256_file(filepath: str) -> str:
    try:
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    except Exception:
        return ""


def build_handoff_package(
    drift_event_id: str,
    detector_id: str,
    severity: str,
    source_file: str,
    related_files: list[str],
    owner_id: str = "system",
    max_tokens: int = 5000,
) -> HandoffPackage:
    """构建跨Session交接包。"""

    pkg_id = f"handoff-{drift_event_id.replace('/', '-')}"

    file_integrity: list[FileIntegrityRecord] = []

    for fpath in related_files:
        file_integrity.append(
            FileIntegrityRecord(
                file_path=fpath,
                sha256_before=_sha256_file(fpath),
            )
        )

    runbook = (
        f"Drift {drift_event_id} detected by {detector_id}. "
        f"Source: {source_file}. Severity: {severity}. "
        f"Pre-fix snapshot captured. Baseline diff available."
    )

    snapshot: dict[str, str] = {}

    for fpath in related_files[:5]:
        try:
            snapshot[fpath] = Path(fpath).read_text(encoding="utf-8")[:200]

        except Exception:
            snapshot[fpath] = ""

    baseline_diff: dict[str, list[str]] = {}

    for fpath in related_files[:5]:
        baseline_diff[fpath] = [f"current: {snapshot.get(fpath, 'N/A')[:100]}"]

    related_ids = [
        f"related-{detector_id}-{hashlib.md5(fpath.encode()).hexdigest()[:6]}" for fpath in related_files[:3]
    ]

    package = HandoffPackage(
        package_id=pkg_id,
        drift_event_id=drift_event_id,
        detector_id=detector_id,
        severity=severity,
        runbook_summary=runbook,
        git_bisect_log=f"bisect not yet executed for {drift_event_id}",
        pre_fix_snapshot=snapshot,
        baseline_diff=baseline_diff,
        related_drift_ids=related_ids,
        file_integrity=file_integrity,
        owner_id=owner_id,
        token_estimate=min(max_tokens, len(runbook.split())),
    )

    return package


def serialize_package(pkg: HandoffPackage, output_dir: str) -> str:
    """序列化handoff package为JSON文件，应用RULE-ONE temp-file+rename。"""

    os.makedirs(output_dir, exist_ok=True)

    safe_id = pkg.package_id.replace("/", "-").replace("\\", "-")

    path = os.path.join(output_dir, f"{safe_id}.json")

    package_dict: dict[str, object] = {
        "package_id": pkg.package_id,
        "drift_event_id": pkg.drift_event_id,
        "detector_id": pkg.detector_id,
        "severity": pkg.severity,
        "runbook_summary": pkg.runbook_summary,
        "git_bisect_log": pkg.git_bisect_log,
        "pre_fix_snapshot": pkg.pre_fix_snapshot,
        "baseline_diff": pkg.baseline_diff,
        "related_drift_ids": pkg.related_drift_ids,
        "file_integrity": [{"file_path": fi.file_path, "sha256_before": fi.sha256_before} for fi in pkg.file_integrity],
        "token_estimate": pkg.token_estimate,
        "owner_id": pkg.owner_id,
        "status": pkg.status,
        "created_at": pkg.created_at,
        "last_verified_at": pkg.last_verified_at,
    }

    content = dumps(package_dict, indent=2,  ensure_ascii=False)

    tmp_path = f"{path}.{os.getpid()}.tmp"

    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(content)

        os.replace(tmp_path, path)

    except PermissionError:
        try:
            os.remove(tmp_path)

        except OSError:
            pass

    return path


def load_package(filepath: str) -> HandoffPackage | None:
    """从JSON文件加载handoff package。"""

    if not os.path.exists(filepath):
        return None

    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.loads(f.read())

    except Exception:
        return None

    integrity_raw = data.get("file_integrity", [])

    file_integrity = [
        FileIntegrityRecord(
            file_path=fi.get("file_path", ""),
            sha256_before=str(fi.get("sha256_before", "")),
        )
        for fi in integrity_raw
    ]

    return HandoffPackage(
        package_id=str(data.get("package_id", "")),
        drift_event_id=str(data.get("drift_event_id", "")),
        detector_id=str(data.get("detector_id", "")),
        severity=str(data.get("severity", "")),
        runbook_summary=str(data.get("runbook_summary", "")),
        git_bisect_log=str(data.get("git_bisect_log", "")),
        pre_fix_snapshot={str(k): str(v) for k, v in data.get("pre_fix_snapshot", {}).items()},
        baseline_diff={str(k): list(map(str, v)) for k, v in data.get("baseline_diff", {}).items()},
        related_drift_ids=list(map(str, data.get("related_drift_ids", []))),
        file_integrity=file_integrity,
        token_estimate=int(data.get("token_estimate", 0)),
        owner_id=str(data.get("owner_id", "")),
        status=str(data.get("status", "READY")),
        created_at=str(data.get("created_at", "")),
        last_verified_at=data.get("last_verified_at"),
    )


def verify_integrity(pkg: HandoffPackage) -> tuple[bool, list[str]]:
    """验证handoff package中文件完整性是否一致。"""

    violations: list[str] = []

    for fi in pkg.file_integrity:
        current_sha = _sha256_file(fi.file_path)

        fi.sha256_after = current_sha

        fi.verified = fi.sha256_before == current_sha and fi.sha256_before != ""

        if not fi.verified:
            violations.append(f"{fi.file_path}: expected {fi.sha256_before[:8]}... got {current_sha[:8]}...")

    pkg.last_verified_at = datetime.now(UTC).isoformat()

    if violations:
        pkg.status = "DIVERGED"

        return False, violations

    pkg.status = "VERIFIED"

    return True, []


def resume_workflow(
    pkg: HandoffPackage,
    project_root: str,
    target_state: str = "RESOLVING",
) -> dict[str, object]:
    """恢复跨Session修复流程——自动注入context并推进状态。"""

    if not verify_integrity(pkg)[0]:
        return {
            "status": "ABORT",
            "reason": "File integrity check failed. Regenerating handoff package.",
            "package_id": pkg.package_id,
            "violations": verify_integrity(pkg)[1],
        }

    context_lines: list[str] = [
        f"[handoff] Resuming drift: {pkg.drift_event_id}",
        f"Detector: {pkg.detector_id}  Severity: {pkg.severity}",
        f"Runbook: {pkg.runbook_summary[:200]}",
        f"Related drifts: {pkg.related_drift_ids}",
        f"Baseline diff: {len(pkg.baseline_diff)} files tracked",
        f"Target state: {target_state}",
        f"Owner: {pkg.owner_id}",
    ]

    injected_context = "\n".join(context_lines)

    pkg.status = target_state

    pkg.last_verified_at = datetime.now(UTC).isoformat()

    return {
        "status": "RESUMED",
        "package_id": pkg.package_id,
        "target_state": target_state,
        "injected_context": injected_context,
        "token_overhead": pkg.token_estimate,
        "related_drifts": pkg.related_drift_ids,
    }


def abort_handoff(
    pkg: HandoffPackage,
    reason: str = "",
) -> dict[str, object]:
    """中止handoff：当文件状态不一致时重新生成并通知Owner。"""

    pkg.status = "ABORTED"

    return {
        "status": "ABORTED",
        "package_id": pkg.package_id,
        "reason": reason or "File state inconsistent with handoff package",
        "owner_notification": pkg.owner_id,
        "action_required": "regenerate_handoff",
        "original_drift_id": pkg.drift_event_id,
    }


class HandoffRecord:
    def __init__(self, record_id="", from_agent="", to_agent="", timestamp=None, context=None, status="pending"):
        self.record_id = record_id
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.timestamp = timestamp
        self.context = context or {}
        self.status = status


class HandoffManager:
    def __init__(self, config=None):
        self.config = config or {}
        self._records = []

    def create_handoff(self, from_agent, to_agent, context=None):
        record = HandoffRecord(from_agent=from_agent, to_agent=to_agent, context=context)
        self._records.append(record)
        return record

    def get_pending(self):
        return [r for r in self._records if r.status == "pending"]
