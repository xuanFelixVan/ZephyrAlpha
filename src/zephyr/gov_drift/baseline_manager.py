# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.baseline_manager
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/governance/drift_detection/_infrastructure.py; tests/audit/test_baseline_manager.py; tests/drift/test_drift_core.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 基线更新必须经过投毒防护
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_baseline_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Baseline Manager — baseline_manager.py


基线快照的拍摄、存储、对比、版本化管理。


对标 blueprint.md §2.2（基线快照管理器）。"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import UTC, datetime

import yaml


@dataclass
class DiffReport:
    baseline_version: str

    module_id: str

    diff_type: str

    added: list[str] = field(default_factory=list)

    removed: list[str] = field(default_factory=list)

    modified: list[str] = field(default_factory=list)

    contract_changes: list[dict[str, str]] = field(default_factory=list)

    cumulative_creep_score: float = 0.0

    detail: dict[str, object] = field(default_factory=dict)


class BaselineManager:
    BASELINES_ROOT: str = ""

    BASELINES_DIR_NAME: str = "drift_baselines"

    MAX_VERSIONS: int = 10

    def __init__(self, project_root: str | None = None):
        if project_root is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

        self._project_root = project_root

        self._baselines_root = os.path.join(project_root, "data", self.BASELINES_DIR_NAME)

        os.makedirs(self._baselines_root, exist_ok=True)

    def module_baseline_dir(self, module_id: str) -> str:
        safe_id = module_id.replace("\\", "_").replace("/", "_")

        return os.path.join(self._baselines_root, safe_id)

    def snapshot_tree_hash(self, module_dir: str) -> dict[str, str]:
        hashes: dict[str, str] = {}

        if not os.path.isdir(module_dir):
            return hashes

        file_paths = []
        for root, _dirs, files in os.walk(module_dir):
            for fname in sorted(files):
                if fname.endswith(".pyc") or fname.startswith("__pycache__"):
                    continue
                file_paths.append(os.path.join(root, fname))

        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = {pool.submit(self._hash_file, fp): fp for fp in file_paths}
            for future in as_completed(futures):
                fp = futures[future]
                try:
                    sha = future.result()
                    if sha:
                        rel = os.path.relpath(fp, module_dir)
                        hashes[rel] = sha
                except OSError:
                    rel = os.path.relpath(fp, module_dir)
                    hashes[rel] = "ERROR"

        return hashes

    @staticmethod
    def _hash_file(fp: str) -> str:
        # 5.134.1 修复：函数实际始终返回 str（hashlib.hexdigest()），
        # 若文件打开失败会抛 OSError 而非返回 None。原注解 `-> str | None` 错误。
        with open(fp, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()


def _read_source_file(fp: str) -> tuple[str, str] | None:
    try:
        with open(fp, encoding="utf-8") as fh:
            return (fp, fh.read())
    except (UnicodeDecodeError, OSError):
        return None


def _read_config_file(fp: str):
    if fp.endswith(".json"):
        with open(fp, encoding="utf-8") as fh:
            return json.load(fh)
    else:
        with open(fp, encoding="utf-8") as fh:
            return yaml.safe_load(fh)

    def snapshot_interface(self, module_dir: str) -> dict[str, list[str]]:
        signatures: dict[str, list[str]] = {}

        if not os.path.isdir(module_dir):
            return signatures

        file_paths = []
        for root, _dirs, files in os.walk(module_dir):
            for fname in sorted(files):
                if not fname.endswith(".py") or fname.startswith("__pycache__"):
                    continue
                file_paths.append(os.path.join(root, fname))

        sources: dict[str, str] = {}
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = {pool.submit(_read_source_file, fp): fp for fp in file_paths}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    fp, source = result
                    sources[fp] = source

        for full, source in sources.items():
            try:
                tree = ast.parse(source, filename=os.path.basename(full))
            except SyntaxError:
                continue

            rel = os.path.relpath(full, module_dir)

            sigs: list[str] = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    args = [a.arg for a in node.args.args]

                    sigs.append(f"def {node.name}({', '.join(args)})")

                elif isinstance(node, ast.ClassDef):
                    bases = [b.id for b in node.bases if isinstance(b, ast.Name)]

                    sigs.append(f"class {node.name}({', '.join(bases)})" if bases else f"class {node.name}")

            signatures[rel] = sigs

        return signatures

    def snapshot_import_graph(self, module_dir: str) -> dict[str, list[str]]:
        graph: dict[str, list[str]] = {}

        if not os.path.isdir(module_dir):
            return graph

        file_paths = []
        for root, _dirs, files in os.walk(module_dir):
            for fname in sorted(files):
                if not fname.endswith(".py") or fname.startswith("__pycache__"):
                    continue
                file_paths.append(os.path.join(root, fname))

        sources: dict[str, str] = {}
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = {pool.submit(_read_source_file, fp): fp for fp in file_paths}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    fp, source = result
                    sources[fp] = source

        for full, source in sources.items():
            try:
                tree = ast.parse(source, filename=os.path.basename(full))
            except SyntaxError:
                continue

            rel = os.path.relpath(full, module_dir)

            imports: list[str] = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

            graph[rel] = sorted(set(imports))

        return graph

    def snapshot_config(self, module_dir: str) -> dict[str, object]:
        configs: dict[str, object] = {}

        if not os.path.isdir(module_dir):
            return configs

        for root, _dirs, files in os.walk(module_dir):
            file_paths = []
        for root, _dirs, files in os.walk(module_dir):
            for fname in files:
                if not (fname.endswith(".yaml") or fname.endswith(".yml") or fname.endswith(".json")):
                    continue
                file_paths.append(os.path.join(root, fname))

        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = {pool.submit(_read_config_file, fp): fp for fp in file_paths}
            for future in as_completed(futures):
                fp = futures[future]
                try:
                    result = future.result()
                    if result:
                        configs[os.path.relpath(fp, module_dir)] = result
                    else:
                        configs[os.path.relpath(fp, module_dir)] = "PARSE_ERROR"
                except (json.JSONDecodeError, yaml.YAMLError, UnicodeDecodeError, OSError):
                    configs[os.path.relpath(fp, module_dir)] = "PARSE_ERROR"

        return configs

    def capture(self, module_id: str, module_dir: str) -> dict[str, object]:
        tree = self.snapshot_tree_hash(module_dir)

        interfaces = self.snapshot_interface(module_dir)

        imports = self.snapshot_import_graph(module_dir)

        config = self.snapshot_config(module_dir)

        snapshot = {
            "module_id": module_id,
            "version": self._next_version(module_id),
            "captured_at": datetime.now(UTC).isoformat(),
            "tree_hash": tree,
            "interface_snapshot": interfaces,
            "import_graph": imports,
            "config_snapshot": config,
        }

        base_dir = self.module_baseline_dir(module_id)

        os.makedirs(base_dir, exist_ok=True)

        version_str = f"v{snapshot['version']:03d}"

        filepath = os.path.join(base_dir, f"{version_str}.json")

        with open(filepath, "w", encoding="utf-8") as fh:
            json.dump(snapshot, fh, indent=2, ensure_ascii=False, default=str)

        self._update_manifest(base_dir, version_str, snapshot)

        self._cleanup_old(base_dir)

        return snapshot

    def on_phase_complete(self, module_id: str, module_dir: str, phase: str) -> dict[str, object]:
        return self.capture(module_id, module_dir)

    def manual_capture(self, module_id: str, module_dir: str) -> dict[str, object]:
        return self.capture(module_id, module_dir)

    def load_baseline(self, module_id: str, version: str) -> dict[str, object] | None:
        base_dir = self.module_baseline_dir(module_id)

        filepath = os.path.join(base_dir, f"{version}.json")

        if not os.path.exists(filepath):
            return None

        try:
            with open(filepath, encoding="utf-8") as fh:
                return json.load(fh)

        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    def full_diff(self, module_id: str, module_dir: str, baseline_version: str | None = None) -> DiffReport:
        baseline = self._resolve_baseline(module_id, baseline_version)

        current = self.capture(module_id, module_dir)

        return self._compute_diff(module_id, baseline, current, "full_diff")

    def slow_creep_check(self, module_id: str, module_dir: str, threshold: float = 0.3) -> DiffReport:
        versions = self.list_versions(module_id)

        if len(versions) < 2:
            report = self.full_diff(module_id, module_dir, versions[0] if versions else None)

            report.diff_type = "slow_creep"

            return report

        oldest = self.load_baseline(module_id, versions[0])

        current = self.capture(module_id, module_dir)

        report = self._compute_diff(module_id, oldest, current, "slow_creep")

        total_sigs = len(current.get("interface_snapshot", {})) + len(oldest.get("interface_snapshot", {}))

        if total_sigs > 0:
            report.cumulative_creep_score = len(report.contract_changes) / (total_sigs / 2)

        return report

    def contract_diff(self, module_id: str, module_dir: str, baseline_version: str | None = None) -> DiffReport:
        baseline = self._resolve_baseline(module_id, baseline_version)

        current_iface = self.snapshot_interface(module_dir)

        return self._compute_contract_diff(module_id, baseline, current_iface)

    def list_versions(self, module_id: str) -> list[str]:
        base_dir = self.module_baseline_dir(module_id)

        if not os.path.isdir(base_dir):
            return []

        versions = []

        for entry in os.scandir(base_dir):
            if entry.is_file() and entry.name.endswith(".json") and not entry.name.startswith("manifest"):
                versions.append(entry.name.replace(".json", ""))

        return sorted(versions)

    def _next_version(self, module_id: str) -> int:
        existing = self.list_versions(module_id)

        if not existing:
            return 1

        nums = []

        for v in existing:
            try:
                nums.append(int(v.replace("v", "")))

            except ValueError:
                pass

        return max(nums, default=0) + 1

    def _update_manifest(self, base_dir: str, version_str: str, _snapshot: dict[str, object]) -> None:
        manifest_path = os.path.join(base_dir, "manifest.json")

        manifest: dict[str, object]

        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, encoding="utf-8") as fh:
                    manifest = json.load(fh)

            except (json.JSONDecodeError, UnicodeDecodeError):
                manifest = {"versions": []}

        else:
            manifest = {"versions": []}

        versions: list[str] = manifest.get("versions", []) or []

        if version_str not in versions:
            versions.append(version_str)

        manifest["versions"] = sorted(versions)

        tmp_path = f"{manifest_path}.{os.getpid()}.tmp"

        try:
            with open(tmp_path, "w", encoding="utf-8") as fh:
                json.dump(manifest, fh, indent=2, ensure_ascii=False)

            os.replace(tmp_path, manifest_path)

        except PermissionError:
            try:
                os.remove(tmp_path)

            except OSError:
                pass

    def _resolve_baseline(self, module_id: str, version: str | None) -> dict[str, object]:
        if version:
            bl = self.load_baseline(module_id, version)

            if bl is not None:
                return bl

        versions = self.list_versions(module_id)

        if versions:
            bl = self.load_baseline(module_id, versions[-1])

            if bl is not None:
                return bl

        return {"tree_hash": {}, "interface_snapshot": {}, "import_graph": {}, "config_snapshot": {}}

    def _compute_diff(
        self, module_id: str, baseline: dict[str, object], current: dict[str, object], diff_type: str
    ) -> DiffReport:
        report = DiffReport(
            baseline_version=str(baseline.get("version", "0")),
            module_id=module_id,
            diff_type=diff_type,
        )

        bl_tree = baseline.get("tree_hash", {}) or {}

        cur_tree = current.get("tree_hash", {}) or {}

        bl_keys = set(bl_tree.keys())

        cur_keys = set(cur_tree.keys())

        report.added = sorted(cur_keys - bl_keys)

        report.removed = sorted(bl_keys - cur_keys)

        report.modified = sorted(k for k in bl_keys & cur_keys if bl_tree.get(k) != cur_tree.get(k))

        bl_iface = baseline.get("interface_snapshot", {}) or {}

        cur_iface = current.get("interface_snapshot", {}) or {}

        for fname in set(list(bl_iface.keys()) + list(cur_iface.keys())):
            bl_sigs = set(bl_iface.get(fname, []))

            cur_sigs = set(cur_iface.get(fname, []))

            for added_sig in sorted(cur_sigs - bl_sigs):
                report.contract_changes.append({"file": fname, "change": "added", "signature": str(added_sig)})

            for removed_sig in sorted(bl_sigs - cur_sigs):
                report.contract_changes.append({"file": fname, "change": "removed", "signature": str(removed_sig)})

        return report

    def _compute_contract_diff(
        self, module_id: str, _baseline: dict[str, object], current_iface: dict[str, list[str]]
    ) -> DiffReport:
        bl_iface = _baseline.get("interface_snapshot", {}) or {}

        report = DiffReport(
            baseline_version=str(_baseline.get("version", "0")),
            module_id=module_id,
            diff_type="contract_only",
        )

        for fname in set(list(bl_iface.keys()) + list(current_iface.keys())):
            bl_sigs = set(bl_iface.get(fname, []))

            cur_sigs = set(current_iface.get(fname, []))

            for added_sig in sorted(cur_sigs - bl_sigs):
                report.contract_changes.append({"file": fname, "change": "added", "signature": str(added_sig)})

            for removed_sig in sorted(bl_sigs - cur_sigs):
                report.contract_changes.append({"file": fname, "change": "removed", "signature": str(removed_sig)})

        return report

    def _cleanup_old(self, base_dir: str) -> None:
        versions = []

        for entry in os.scandir(base_dir):
            if entry.is_file() and entry.name.endswith(".json") and not entry.name.startswith("manifest"):
                versions.append(entry.name)

        versions.sort()

        while len(versions) > self.MAX_VERSIONS:
            old = versions.pop(0)

            archive_dir = os.path.join(base_dir, "archive")

            os.makedirs(archive_dir, exist_ok=True)

            src = os.path.join(base_dir, old)

            dst = os.path.join(archive_dir, old)

            if os.path.exists(src):
                shutil.move(src, dst)
