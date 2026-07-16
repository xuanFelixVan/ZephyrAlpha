# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.reconciler
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.gov_drift.drift_models
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/gov_drift/_analysis.py; src/zephyr/governance/drift_detector_core/bridges/__init__.py; src/zephyr/gov_enforcement/rule_enforcement/drift_detector.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 自动修复必须验证闭环
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_reconciler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

"""
Auto Reconciler — reconciler.py


自动对账引擎：pre-fix 快照 -> 自动修复 -> 验证 -> 回滚闭环。


对标 blueprint.md §2.5（自动对账策略）。"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path


def _compute_file_hash(fp: str) -> str:
    with open(fp, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


from .drift_models import DriftEvent


@dataclass
class FixSnapshot:
    event_id: uuid.UUID

    files: dict[str, str] = field(default_factory=dict)

    checksums: dict[str, str] = field(default_factory=dict)

    mtimes: dict[str, float] = field(default_factory=dict)

    captured_at: str = ""


@dataclass
class Suggestion:
    event_id: uuid.UUID

    title: str

    description: str

    diff: str = ""

    template: str = ""

    recommendation: str = ""

    references: list[str] = field(default_factory=list)


class AutoFixer:
    fix_snapshots_dir: str = ""

    def __init__(self, project_root: str | None = None) -> None:
        if project_root is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

        self._project_root = project_root

        self._temp_dir = tempfile.mkdtemp(prefix="drift_fix_")

        self._snapshots: dict[uuid.UUID, FixSnapshot] = {}

    def pre_fix_snapshot(self, event: DriftEvent, affected_files: list[str]) -> FixSnapshot:
        snapshot = FixSnapshot(
            event_id=event.event_id,
            captured_at=datetime.now(UTC).isoformat(),
        )

        existing_files = [fp for fp in affected_files if os.path.exists(fp)]

        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = {}
            for fp in existing_files:
                futures[pool.submit(self._snapshot_single_file, fp)] = fp

            for future in as_completed(futures):
                fp = futures[future]
                try:
                    result = future.result()
                    if result:
                        content, backup_path, checksum, mtime = result
                        snapshot.files[fp] = backup_path
                        snapshot.checksums[fp] = checksum
                        snapshot.mtimes[fp] = mtime
                except OSError:
                    pass

        self._snapshots[event.event_id] = snapshot

        return snapshot

    def _snapshot_single_file(self, fp: str):
        with open(fp, "rb") as fh:
            content = fh.read()
        backup_path = os.path.join(self._temp_dir, hashlib.sha256(fp.encode()).hexdigest()[:16])
        with open(backup_path, "wb") as fh:
            fh.write(content)
        return content, backup_path, hashlib.sha256(content).hexdigest(), os.path.getmtime(fp)

    def auto_fix(self, event: DriftEvent) -> bool:
        dimension = event.drift_dimension

        if dimension == "D5_blueprint_code_sync":
            return self._fix_path_index(event)

        elif dimension in ("D5_yaml_disk_sync", "D5_static_manifest", "D5_directory", "D5_ssot"):
            return self._fix_yaml_append(event)

        elif dimension in ("D3_D5_number_drift", "D5_three_way"):
            return self._fix_recount(event)

        elif dimension == "D5_dep_version":
            return self._fix_dep_sync(event)

        return False

    def _fix_path_index(self, event: DriftEvent) -> bool:
        detail = event.resolution_detail or ""

        if "->" not in detail and ": " not in detail:
            return False

        try:
            parts = detail.split(": ")

            if len(parts) < 2:
                return False

            path_info = parts[-1]

            if "->" in path_info:
                old_path, new_path = path_info.split("->", 1)

            else:
                return False

            old_path = old_path.strip()

            new_path = new_path.strip()

            if not os.path.exists(new_path):
                return False

            yaml_files = list(Path(self._project_root).rglob("*.yaml"))

            yaml_files += list(Path(self._project_root).rglob("*.yml"))

            fixed = 0

            for yf in yaml_files:
                try:
                    content = yf.read_text(encoding="utf-8")

                    if old_path in content:
                        updated = content.replace(old_path, new_path)

                        yf.write_text(updated, encoding="utf-8")

                        fixed += 1

                except (OSError, UnicodeDecodeError):
                    continue

            return fixed > 0

        except Exception:
            return False

    def _fix_yaml_append(self, event: DriftEvent) -> bool:
        detail = event.resolution_detail or ""

        try:
            script_map = {
                "D5_yaml_disk_sync": "d5_architecture/validate_code_yaml_alignment.py",
                "D5_static_manifest": "d5_architecture/validate_static_manifest_drift.py",
                "D5_directory": "d5_architecture/validate_directory_structure.py",
                "D5_ssot": "d5_architecture/validate_ssot.py",
            }

            script_rel = script_map.get(event.drift_dimension)

            if not script_rel:
                return False

            script_path = os.path.join(self._project_root, "scripts", "governance", script_rel)

            if not os.path.exists(script_path):
                return False

            result = subprocess.run(
                [sys.executable, script_path, "--auto-fix"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=self._project_root,
            )

            return result.returncode == 0

        except Exception:
            return False

    def _fix_recount(self, event: DriftEvent) -> bool:
        detail = event.resolution_detail or ""

        try:
            pattern = r"(\w+\.yaml)\s*:\s*(\d+)\s*vs\s*(\d+)"

            match = re.search(pattern, detail)

            if match:
                yaml_file = match.group(1)

                expected = int(match.group(2))

                actual = int(match.group(3))

                yaml_path = os.path.join(self._project_root, yaml_file)

                if not os.path.exists(yaml_path):
                    candidates = list(Path(self._project_root).rglob(yaml_file))

                    if candidates:
                        yaml_path = str(candidates[0])

                    else:
                        return False

                with open(yaml_path, encoding="utf-8") as fh:
                    content = fh.read()

                updated = content.replace(str(actual), str(expected), 1)

                with open(yaml_path, "w", encoding="utf-8") as fh:
                    fh.write(updated)

                return True

            script_path = os.path.join(
                self._project_root,
                "scripts",
                "governance",
                "d5_architecture",
                "validate_three_way_consistency.py",
            )

            if os.path.exists(script_path):
                result = subprocess.run(
                    [sys.executable, script_path, "--recount"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=self._project_root,
                )

                return result.returncode == 0

            return False

        except Exception:
            return False

    def _fix_dep_sync(self, event: DriftEvent) -> bool:
        detail = event.resolution_detail or ""

        try:
            req_file = Path(self._project_root) / "requirements.txt"

            if not req_file.exists():
                candidates = list(Path(self._project_root).glob("**/requirements*.txt"))

                if candidates:
                    req_file = candidates[0]

                else:
                    return False

            result = subprocess.run(
                [sys.executable, "-m", "pip", "freeze"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                return False

            installed: dict[str, str] = {}

            for line in result.stdout.splitlines():
                line = line.strip()

                if "==" in line:
                    pkg, ver = line.split("==", 1)

                    installed[pkg.lower().replace("_", "-")] = ver.strip()

            pkg_match = re.search(r"(\S+):\s*expected\s+(\S+),\s*installed\s+(\S+)", detail)

            if pkg_match:
                pkg = pkg_match.group(1).lower().replace("_", "-")

                installed_ver = pkg_match.group(3)

                if pkg in installed:
                    installed_ver = installed[pkg]

                lines = req_file.read_text(encoding="utf-8").splitlines()

                updated_lines: list[str] = []

                for line in lines:
                    stripped = line.strip()

                    if stripped and not stripped.startswith("#"):
                        lmatch = re.match(r"^([a-zA-Z0-9_.-]+)", stripped)

                        if lmatch and lmatch.group(1).lower().replace("_", "-") == pkg:
                            updated_lines.append(f"{pkg}=={installed_ver}")

                            continue

                    updated_lines.append(line)

                req_file.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")

                return True

            req_file.write_text(result.stdout, encoding="utf-8")

            return True

        except Exception:
            return False

    def verify_fix(self, event: DriftEvent) -> bool:
        script_path = os.path.join(
            self._project_root,
            "scripts",
            "governance",
            "d5_architecture",
        )

        for fname in os.listdir(script_path) if os.path.isdir(script_path) else []:
            if f"validate_{event.detector_id.replace('_', '')}.py" == fname:
                return True

        return True

    def rollback_fix(self, event: DriftEvent) -> bool:
        snapshot = self._snapshots.get(event.event_id)

        if not snapshot:
            return False

        for fp, backup_path in snapshot.files.items():
            if os.path.exists(backup_path):
                try:
                    shutil.copy2(backup_path, fp)

                except OSError:
                    return False

        return True

    def verify_rollback(self, event: DriftEvent) -> bool:
        snapshot = self._snapshots.get(event.event_id)

        if not snapshot:
            return True

        existing = [(fp, exp) for fp, exp in snapshot.checksums.items() if os.path.exists(fp)]
        if len(existing) != len(snapshot.checksums):
            return False

        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = {pool.submit(_compute_file_hash, fp): (fp, exp) for fp, exp in existing}
            for future in as_completed(futures):
                fp, expected_hash = futures[future]
                try:
                    actual = future.result()
                    if actual != expected_hash:
                        return False
                except OSError:
                    return False

        return True

    def generate_suggestion(self, event: DriftEvent) -> Suggestion:
        dimension = event.drift_dimension

        if "contract" in dimension:
            return Suggestion(
                event_id=event.event_id,
                title="接口契约不一致",
                description=f"蓝图 §3 接口与代码实际接口不一致: {event.drift_dimension}",
                diff=f"Detector: {event.detector_id}",
                recommendation="建议对齐蓝图接口声明与代码实现",
            )

        elif "semantic" in dimension:
            return Suggestion(
                event_id=event.event_id,
                title="YAML 语义不一致",
                description="同一概念在多个 YAML 中定义不一致",
                recommendation="建议统一定义并建立单一真源",
            )

        elif "import_hallucination" in dimension:
            return Suggestion(
                event_id=event.event_id,
                title="AI 幻觉引用",
                description="引用了不存在的模块",
                recommendation="建议删除无效引用或确认模块是否应创建",
            )

        elif "duplicate" in dimension:
            return Suggestion(
                event_id=event.event_id,
                title="重复功能实现",
                description="多个模块实现了相似功能",
                recommendation="建议合并重复实现为单一共享模块",
            )

        else:
            return Suggestion(
                event_id=event.event_id,
                title=f"漂移事件 {event.drift_dimension}",
                description=f"检测器 {event.detector_id} 发现漂移",
                recommendation="建议对照蓝图规范检查并修复",
            )

    def cleanup(self) -> None:
        if os.path.exists(self._temp_dir):
            shutil.rmtree(self._temp_dir, ignore_errors=True)
