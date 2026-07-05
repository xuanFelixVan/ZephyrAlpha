# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §4
# [MODULE] zephyr.governance.audit_trail.pipeline_runner
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.integration.shared.schema.base_config; zephyr.governance.audit_trail.text_to_finding_adapter
# [CONSUMERS] audit-orchestrator.cli; audit_admission_controller
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] PipelineRunner executes scripts in dependency chain order; all findings collected as AuditFinding
# [MODIFY-GUARD] Dimension chain order changes require blueprint update
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] run() never raises; individual script failures are logged and skipped
# [TESTS] tests/test_audit_orchestrator_e2e.py
# [A_module] module_id=MOD-GOV_pipeline_runner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from pydantic import BaseModel, Field

# STUB: from zephyr.governance.audit_trail.text_to_finding_adapter import TextToFindingAdapter
# Reason: lazy import to break circular import with audit-orchestrator.__init__
from zephyr.governance.audit_trail.finding_model import (
    AuditFinding,
    BlastRadius,
    FindingDimension,
    FindingImpact,
    FindingLifecycle,
    FindingRemediation,
    FindingSeverity,
    FindingStatus,
    FindingTarget,
    FindingTraceability,
    RecommendationBlock,
    RemediationAction,
    RemediationPriority,
    generate_finding_id,
)
from zephyr.integration.shared.schema.base_config import BASE_CONFIG

logger = logging.getLogger(__name__)

DEPENDENCY_CHAINS: dict[str, tuple[str, ...]] = {
    "chain_a": ("D1", "D3", "D5", "D8"),
    "chain_b": ("D2", "D4", "D11", "D9", "D12"),
    "chain_c": ("D6", "D7", "D10"),
}

_SCRIPT_TIMEOUT = 120


class ScriptResult(BaseModel):
    model_config = BASE_CONFIG

    script_path: str
    exit_code: int = -1
    stdout: str = ""
    stderr: str = ""
    findings: list[AuditFinding] = Field(default_factory=list)
    timed_out: bool = False
    output_mode: str = "auto"


class DimensionResult(BaseModel):
    model_config = BASE_CONFIG

    dimension: str
    scripts_run: int = 0
    passed: int = 0
    failed: int = 0
    findings_count: int = 0


class PipelineResult(BaseModel):
    model_config = BASE_CONFIG

    total_scripts: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    findings: list[AuditFinding] = Field(default_factory=list)
    duration_seconds: float = 0.0
    dimension_results: dict[str, DimensionResult] = Field(default_factory=dict)


class PipelineRunner:
    _discovery_cache: dict[str, tuple[float, dict[str, list[str]]]] = {}
    _depgraph_cache: tuple[float, dict[str, object]] | None = None
    _manifest_cache: tuple[float, dict[str, object]] | None = None
    _gate_registry_cache: tuple[float, dict[str, object]] | None = None
    _scan_cache: dict[str, tuple[float, list[AuditFinding]]] = {}
    _depgraph_path: str = "data/asset_index/project-entity-depgraph.yaml"

    def __init__(self, scripts_dir: str = "scripts/governance", max_workers: int = 8) -> None:
        self.scripts_dir = scripts_dir
        self.max_workers = max_workers
        from zephyr.governance.audit_trail.text_to_finding_adapter import TextToFindingAdapter

        self._adapter = TextToFindingAdapter()
        self._script_output_mode: dict[str, str] = {}
        self._dimension_scripts: dict[str, list[str]] = self._discover_scripts()

    def run(self, dimensions: list[str] | None = None, dry_run: bool = False) -> PipelineResult:
        start = time.monotonic()
        all_findings: list[AuditFinding] = []
        dimension_results: dict[str, DimensionResult] = {}
        total_passed = 0
        total_failed = 0
        total_skipped = 0
        total_scripts = 0

        target_dimensions = self._resolve_dimensions(dimensions)
        ordered_dimensions = self._order_by_chains(target_dimensions)

        for dim in ordered_dimensions:
            scripts = self._dimension_scripts.get(dim, [])
            if not scripts:
                dimension_results[dim] = DimensionResult(dimension=dim)
                continue

            if dry_run:
                total_skipped += len(scripts)
                total_scripts += len(scripts)
                dimension_results[dim] = DimensionResult(
                    dimension=dim,
                    scripts_run=0,
                    passed=0,
                    failed=0,
                    findings_count=0,
                )
                continue

            dim_passed = 0
            dim_failed = 0
            dim_findings: list[AuditFinding] = []

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_path = {executor.submit(self._execute_script, sp, dim, dry_run): sp for sp in scripts}
                for future in as_completed(future_to_path):
                    try:
                        result = future.result()
                    except Exception:
                        total_scripts += 1
                        total_failed += 1
                        dim_failed += 1
                        continue

                    total_scripts += 1
                    if result.exit_code == 0:
                        total_passed += 1
                        dim_passed += 1
                    else:
                        total_failed += 1
                        dim_failed += 1

                    dim_findings.extend(result.findings)
                    all_findings.extend(result.findings)

            dimension_results[dim] = DimensionResult(
                dimension=dim,
                scripts_run=len(scripts),
                passed=dim_passed,
                failed=dim_failed,
                findings_count=len(dim_findings),
            )

        elapsed = time.monotonic() - start
        return PipelineResult(
            total_scripts=total_scripts,
            passed=total_passed,
            failed=total_failed,
            skipped=total_skipped,
            findings=all_findings,
            duration_seconds=round(elapsed, 3),
            dimension_results=dimension_results,
        )

    def _discover_scripts(self) -> dict[str, list[str]]:
        gov_path = Path(self.scripts_dir).resolve()
        cache_key = str(gov_path)
        try:
            current_mtime = gov_path.stat().st_mtime if gov_path.is_dir() else 0.0
        except OSError:
            current_mtime = 0.0
        cached = PipelineRunner._discovery_cache.get(cache_key)
        if cached is not None and cached[0] == current_mtime:
            return cached[1]

        if not gov_path.is_dir():
            PipelineRunner._discovery_cache[cache_key] = (current_mtime, {})
            return {}

        print(f"[START] Discovering scripts in {gov_path}...", file=sys.stderr)
        t_start = time.perf_counter()

        mapping: dict[str, list[str]] = {}

        py_files = list(gov_path.rglob("*.py"))
        total = len(py_files)
        for i, py_file in enumerate(py_files):
            if (i + 1) % 200 == 0 or i == total - 1:
                print(f"[PROGRESS] Filesystem scan {i + 1}/{total} files...", file=sys.stderr)
            name = py_file.name
            if name.startswith("_"):
                continue
            parent_dir = py_file.parent.name
            dim_key = self._dir_to_dimension(parent_dir)
            if dim_key is None:
                continue
            mapping.setdefault(dim_key, []).append(str(py_file))

        for py_file in gov_path.glob("*.py"):
            name = py_file.name
            if name.startswith("_"):
                continue
            if any(name in scripts for scripts in mapping.values()):
                continue
            dim_key = self._infer_dimension_from_name(name)
            if dim_key:
                mapping.setdefault(dim_key, []).append(str(py_file))

        for source in (
            self._discover_from_manifest(),
            self._discover_from_depgraph(),
            self._discover_from_gate_registry(),
        ):
            for dim, scripts in source.items():
                existing = set(mapping.get(dim, []))
                for sp in scripts:
                    if sp not in existing:
                        mapping.setdefault(dim, []).append(sp)
                        existing.add(sp)

        for dim in mapping:
            mapping[dim] = [sp for sp in mapping[dim] if not Path(sp).name.startswith("_")]

        for dim in mapping:
            mapping[dim].sort()

        elapsed = time.perf_counter() - t_start
        print(f"[DONE] Discovered {sum(len(v) for v in mapping.values())} scripts in {elapsed:.1f}s", file=sys.stderr)

        PipelineRunner._discovery_cache[cache_key] = (current_mtime, mapping)
        return mapping

    @staticmethod
    def _domain_to_dimension(domain: str) -> str | None:
        _DOMAIN_MAP: dict[str, str] = {
            "structure": "D1",
            "links": "D2",
            "metadata": "D3",
            "paths": "D4",
            "architecture": "D5",
            "security": "D6",
            "code": "D7",
            "doc_sync": "D8",
            "knowledge": "D9",
            "performance": "D10",
            "compliance": "D11",
            "ai_hallucination": "D12",
            "meta": "D12",
        }
        return _DOMAIN_MAP.get(domain)

    @staticmethod
    def _validate_script_exists(script_path: str, project_root: Path) -> bool:
        if Path(script_path).is_file():
            return True
        return (project_root / script_path).is_file()

    def _discover_from_manifest(self) -> dict[str, list[str]]:
        data = self._load_manifest()
        if not data or "scripts" not in data:
            return {}
        project_root = self._project_root()
        mapping: dict[str, list[str]] = {}
        for entry in data["scripts"]:
            domain = entry.get("domain", "")
            dim = self._domain_to_dimension(domain)
            if dim is None:
                continue
            rel_path = entry.get("path", "")
            if not rel_path:
                continue
            abs_path = project_root / "scripts" / rel_path
            if not abs_path.is_file():
                continue
            mapping.setdefault(dim, []).append(str(abs_path))
        for dim in mapping:
            mapping[dim] = [sp for sp in mapping[dim] if not Path(sp).name.startswith("_")]
        return mapping

    def _discover_from_depgraph(self) -> dict[str, list[str]]:
        data = self._load_depgraph()
        if not data or "nodes" not in data or "edges" not in data:
            return {}
        project_root = self._project_root()
        owned_by_map: dict[str, list[str]] = {}
        for edge in data.get("edges", []):
            if edge.get("dep_type") == "owned_by":
                from_id = edge.get("from", "")
                to_id = edge.get("to", "")
                if from_id and to_id:
                    owned_by_map.setdefault(from_id, []).append(to_id)
        mapping: dict[str, list[str]] = {}
        nodes = data.get("nodes", {})
        for node_id, node_data in nodes.items():
            if not isinstance(node_data, dict) or node_data.get("type") != "script":
                continue
            script_path = node_data.get("path", "")
            if not script_path:
                continue
            dim = None
            for owner_id in owned_by_map.get(node_id, []):
                for part in owner_id.split("__"):
                    dim = self._dir_to_dimension(part)
                    if dim:
                        break
                if dim:
                    break
            if dim is None:
                for part in Path(script_path).parts:
                    dim = self._dir_to_dimension(part)
                    if dim:
                        break
            if dim is None:
                continue
            abs_path = project_root / script_path
            if not abs_path.is_file():
                continue
            mapping.setdefault(dim, []).append(str(abs_path))
        for dim in mapping:
            mapping[dim] = [sp for sp in mapping[dim] if not Path(sp).name.startswith("_")]
        return mapping

    def _discover_from_gate_registry(self) -> dict[str, list[str]]:
        data = self._load_gate_registry()
        if not data or "gates" not in data:
            return {}
        import re

        project_root = self._project_root()
        gates_dir = project_root / "src" / "zephyr" / "gates"
        mapping: dict[str, list[str]] = {}
        for gate in data["gates"]:
            for field in ("script_path", "check_command", "file"):
                raw = gate.get(field, "")
                if not raw or not isinstance(raw, str):
                    continue
                if field == "check_command":
                    m = re.search(r"(\S+\.py)", raw)
                    if m:
                        raw = m.group(1)
                    else:
                        continue
                if not raw.endswith(".py"):
                    continue
                abs_path = (gates_dir / raw).resolve()
                if not abs_path.is_file():
                    abs_path = (project_root / raw).resolve()
                if not abs_path.is_file():
                    continue
                mapping.setdefault("D5", []).append(str(abs_path))
        for dim in mapping:
            mapping[dim] = [sp for sp in mapping[dim] if not Path(sp).name.startswith("_")]
        return mapping

    def _execute_script(self, script_path: str, dimension: str, dry_run: bool) -> ScriptResult:
        if dry_run:
            return ScriptResult(script_path=script_path)

        repo_root = str(Path(script_path).resolve().parents[2])
        script_name = Path(script_path).stem
        cached_mode = self._script_output_mode.get(script_path)

        if cached_mode == "jsonl":
            result = self._run_subprocess(script_path, repo_root, ["--jsonl", "--warn-only"])
            if result is not None:
                findings = self._parse_findings(
                    result.stdout,
                    dimension=dimension,
                    script_name=script_name,
                    output_mode="jsonl",
                )
                self._script_output_mode[script_path] = "jsonl"
                return ScriptResult(
                    script_path=script_path,
                    exit_code=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    findings=findings,
                    output_mode="jsonl",
                )

        if cached_mode == "text":
            result = self._run_subprocess(script_path, repo_root, ["--warn-only"])
            if result is not None:
                findings = self._parse_findings(
                    result.stdout,
                    dimension=dimension,
                    script_name=script_name,
                    output_mode="text",
                )
                self._script_output_mode[script_path] = "text"
                return ScriptResult(
                    script_path=script_path,
                    exit_code=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    findings=findings,
                    output_mode="text",
                )

        result = self._run_subprocess(script_path, repo_root, ["--jsonl", "--warn-only"])
        if result is None:
            return ScriptResult(script_path=script_path, exit_code=2, timed_out=True)

        if result.returncode in (0, 1):
            findings = self._parse_findings(
                result.stdout,
                dimension=dimension,
                script_name=script_name,
                output_mode="jsonl",
            )
            self._script_output_mode[script_path] = "jsonl"
            return ScriptResult(
                script_path=script_path,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                findings=findings,
                output_mode="jsonl",
            )

        stderr_lower = result.stderr.lower()
        if result.returncode == 2 and ("unrecognized arguments" in stderr_lower or "unknown option" in stderr_lower):
            fallback = self._run_subprocess(script_path, repo_root, ["--warn-only"])
            if fallback is None:
                return ScriptResult(script_path=script_path, exit_code=2, timed_out=True)

            findings = self._parse_findings(
                fallback.stdout,
                dimension=dimension,
                script_name=script_name,
                output_mode="auto",
            )
            detected_mode = (
                "jsonl"
                if any(line.strip() and self._try_parse_jsonl(line.strip()) for line in fallback.stdout.splitlines())
                else "text"
            )
            self._script_output_mode[script_path] = detected_mode
            return ScriptResult(
                script_path=script_path,
                exit_code=fallback.returncode,
                stdout=fallback.stdout,
                stderr=fallback.stderr,
                findings=findings,
                output_mode=detected_mode,
            )

        findings = self._parse_findings(
            result.stdout,
            dimension=dimension,
            script_name=script_name,
            output_mode="auto",
        )
        self._script_output_mode[script_path] = "auto"
        return ScriptResult(
            script_path=script_path,
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            findings=findings,
            output_mode="auto",
        )

    @staticmethod
    def _try_parse_jsonl(line: str) -> bool:
        try:
            AuditFinding.from_jsonl(line)
            return True
        except (ValueError, Exception):
            return False

    def _run_subprocess(
        self, script_path: str, repo_root: str, extra_args: list[str]
    ) -> subprocess.CompletedProcess | None:
        try:
            return subprocess.run(
                [sys.executable, script_path, *extra_args],
                capture_output=True,
                text=True,
                timeout=_SCRIPT_TIMEOUT,
                cwd=repo_root,
                encoding="utf-8",
                errors="replace",
            )
        except subprocess.TimeoutExpired:
            return None
        except Exception:
            return None

    def _parse_findings(
        self, stdout: str, dimension: str, script_name: str, output_mode: str = "auto"
    ) -> list[AuditFinding]:
        findings: list[AuditFinding] = []
        if output_mode == "jsonl":
            for line in stdout.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    findings.append(AuditFinding.from_jsonl(line))
                except (ValueError, Exception):
                    pass
            return findings

        if output_mode == "text":
            if stdout.strip():
                findings = self._adapter.parse(stdout, dimension=dimension, script_name=script_name)
            return findings

        for line in stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                findings.append(AuditFinding.from_jsonl(line))
                continue
            except (ValueError, Exception):
                pass
        if not findings and stdout.strip():
            findings = self._adapter.parse(stdout, dimension=dimension, script_name=script_name)
        return findings

    def _resolve_dimensions(self, dimensions: list[str] | None) -> list[str]:
        if dimensions is not None:
            return [d.upper() for d in dimensions]
        all_dims: list[str] = []
        for chain in DEPENDENCY_CHAINS.values():
            for dim in chain:
                if dim not in all_dims:
                    all_dims.append(dim)
        return all_dims

    def _order_by_chains(self, dimensions: list[str]) -> list[str]:
        dim_set = set(dimensions)
        ordered: list[str] = []
        for chain_name in ("chain_a", "chain_b", "chain_c"):
            for dim in DEPENDENCY_CHAINS[chain_name]:
                if dim in dim_set:
                    ordered.append(dim)
        remaining = sorted(dim_set - set(ordered))
        ordered.extend(remaining)
        return ordered

    @staticmethod
    def _dir_to_dimension(dir_name: str) -> str | None:
        _DIR_MAP: dict[str, str] = {
            "d1_structure": "D1",
            "d2_links": "D2",
            "d3_metadata": "D3",
            "d4_paths": "D4",
            "d5_architecture": "D5",
            "checkers": "D5",
            "validators": "D5",
            "detectors": "D5",
            "analyzers": "D5",
            "yaml_md": "D5",
            "d6_security": "D6",
            "d7_code": "D7",
            "d8_doc_sync": "D8",
            "d8_tests": "D8",
            "d9_knowledge": "D9",
            "d9_vcs": "D9",
            "d10_performance": "D10",
            "d10_ci_cd": "D10",
            "d11_compliance": "D11",
            "d11_infrastructure": "D11",
            "d12_ai_hallucination": "D12",
            "d12_feedback": "D12",
            "meta": "D12",
            "observability": "D10",
            "generators": "D5",
            "syncers": "D3",
            "blueprint": "D5",
        }
        return _DIR_MAP.get(dir_name)

    @staticmethod
    def _infer_dimension_from_name(name: str) -> str | None:
        _NAME_MAP: dict[str, str] = {
            "audit_": "D1",
            "check_": "D5",
            "validate_": "D5",
            "detect_": "D6",
            "scan_": "D6",
            "sync_": "D3",
            "generate_": "D5",
            "rebuild_": "D1",
            "verify_": "D1",
            "score_": "D5",
            "pre_write_gate": "D1",
            "pre_op_check": "D1",
            "construction_gate": "D5",
            "session_startup": "D1",
            "ci_self_check": "D1",
            "run_all": "D5",
        }
        for prefix, dim in _NAME_MAP.items():
            if name.startswith(prefix):
                return dim
        return None

    def _project_root(self) -> Path:
        return Path(self.scripts_dir).resolve().parents[1]

    def _load_depgraph(self) -> dict[str, object] | None:
        root = self._project_root()
        dep_path = root / PipelineRunner._depgraph_path
        if not dep_path.is_file():
            return None
        try:
            current_mtime = dep_path.stat().st_mtime
        except OSError:
            current_mtime = 0.0
        cached = PipelineRunner._depgraph_cache
        if cached is not None and cached[0] == current_mtime:
            return cached[1]
        print(f"[START] Loading depgraph {dep_path.name}...", file=sys.stderr)
        t_start = time.perf_counter()
        try:
            import yaml
        except ImportError:
            return None
        with open(str(dep_path), encoding="utf-8") as f:
            # 5.48.1 修复：FullLoader 可构造 Python 对象（!!python/object），
            # depgraph 文件被篡改时可实例化任意对象。统一改用 safe_load（与 L669 _load_manifest 一致）。
            data = yaml.safe_load(f)
        elapsed = time.perf_counter() - t_start
        print(f"[DONE] Loaded depgraph in {elapsed:.1f}s", file=sys.stderr)
        PipelineRunner._depgraph_cache = (current_mtime, data)
        return data

    def _load_manifest(self) -> dict[str, object] | None:
        root = self._project_root()
        mf_path = root / "scripts" / "script-manifest.yaml"
        if not mf_path.is_file():
            return None
        try:
            current_mtime = mf_path.stat().st_mtime
        except OSError:
            current_mtime = 0.0
        cached = PipelineRunner._manifest_cache
        if cached is not None and cached[0] == current_mtime:
            return cached[1]
        try:
            import yaml
        except ImportError:
            return None
        with open(str(mf_path), encoding="utf-8") as f:
            data = yaml.safe_load(f)
        PipelineRunner._manifest_cache = (current_mtime, data)
        return data

    def _load_gate_registry(self) -> dict[str, object] | None:
        root = self._project_root()
        reg_path = root / "src" / "zephyr" / "gates" / "_registry.yaml"
        if not reg_path.is_file():
            return None
        try:
            current_mtime = reg_path.stat().st_mtime
        except OSError:
            current_mtime = 0.0
        cached = PipelineRunner._gate_registry_cache
        if cached is not None and cached[0] == current_mtime:
            return cached[1]
        try:
            import yaml
        except ImportError:
            return None
        with open(str(reg_path), encoding="utf-8") as f:
            data = yaml.safe_load(f)
        PipelineRunner._gate_registry_cache = (current_mtime, data)
        return data

    def _get_cached_scan(self, cache_key: str, source_path: str) -> list[AuditFinding] | None:
        try:
            current_mtime = Path(source_path).stat().st_mtime
        except OSError:
            current_mtime = 0.0
        cached = PipelineRunner._scan_cache.get(cache_key)
        if cached is not None and cached[0] == current_mtime:
            return cached[1]
        return None

    def _set_cached_scan(self, cache_key: str, source_path: str, findings: list[AuditFinding]) -> None:
        try:
            current_mtime = Path(source_path).stat().st_mtime
        except OSError:
            current_mtime = 0.0
        PipelineRunner._scan_cache[cache_key] = (current_mtime, findings)

    def _make_finding(
        self,
        dimension: str,
        severity: FindingSeverity,
        category: str,
        file_path: str,
        description: str,
        evidence: str,
        remediation_action: RemediationAction = RemediationAction.FIX,
        remediation_priority: RemediationPriority = RemediationPriority.P2,
        blast_radius: BlastRadius = BlastRadius.file,
    ) -> AuditFinding:
        return AuditFinding(
            finding_id=generate_finding_id(dimension, description),
            dimension=FindingDimension(dimension),
            severity=severity,
            category=category,
            target=FindingTarget(file_path=file_path),
            description=description,
            evidence=evidence,
            impact=FindingImpact(blast_radius=blast_radius),
            remediation=FindingRemediation(action=remediation_action, priority=remediation_priority),
            lifecycle=FindingLifecycle(status=FindingStatus.OPEN),
            traceability=FindingTraceability(),
            recommendation_block=RecommendationBlock(),
        )

    def scan_registries(self) -> list[AuditFinding]:
        try:
            import yaml
        except ImportError:
            return []
        root = self._project_root()
        registry_path = root / "docs" / "registry_of_registries.yaml"
        str_path = str(registry_path)
        cached = self._get_cached_scan("scan_registries", str_path)
        if cached is not None:
            return cached
        findings: list[AuditFinding] = []
        if not registry_path.is_file():
            self._set_cached_scan("scan_registries", str_path, findings)
            return findings
        try:
            with open(str_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception:
            return findings
        if not data or "tiers" not in data:
            return findings
        for tier in data["tiers"]:
            for entry in tier.get("registries", []):
                rid = entry.get("registry_id", "UNKNOWN")
                phys = entry.get("physical_path", "")
                status = entry.get("status", "active")
                if status == "broken":
                    findings.append(
                        self._make_finding(
                            dimension="D3",
                            severity=FindingSeverity.CRITICAL,
                            category="注册表状态异常",
                            file_path=phys,
                            description=f"注册表 {rid} 状态为 broken",
                            evidence=f"status={status}",
                            remediation_priority=RemediationPriority.P0,
                            blast_radius=BlastRadius.system,
                        )
                    )
                if status == "pending_scan":
                    findings.append(
                        self._make_finding(
                            dimension="D3",
                            severity=FindingSeverity.MEDIUM,
                            category="注册表待扫描",
                            file_path=phys,
                            description=f"注册表 {rid} 状态为 pending_scan",
                            evidence=f"status={status}",
                        )
                    )
        self._set_cached_scan("scan_registries", str_path, findings)
        return findings

    def scan_manifest(self) -> list[AuditFinding]:
        root = self._project_root()
        manifest_path = root / "scripts" / "script-manifest.yaml"
        str_path = str(manifest_path)
        cached = self._get_cached_scan("scan_manifest", str_path)
        if cached is not None:
            return cached
        data = self._load_manifest()
        if not data or "scripts" not in data:
            return []
        findings: list[AuditFinding] = []
        valid_domains = {
            "structure",
            "links",
            "metadata",
            "paths",
            "architecture",
            "security",
            "code",
            "doc_sync",
            "knowledge",
            "performance",
            "compliance",
            "ai_hallucination",
            "meta",
            "a2a",
            "governance",
        }
        for entry in data["scripts"]:
            name = entry.get("name", "UNKNOWN")
            rel_path = entry.get("path", "")
            domain = entry.get("domain", "")
            abs_path = root / "scripts" / rel_path
            if rel_path and not abs_path.is_file():
                findings.append(
                    self._make_finding(
                        dimension="D1",
                        severity=FindingSeverity.HIGH,
                        category="脚本文件缺失",
                        file_path=str(abs_path),
                        description=f"脚本 {name} 的路径 {rel_path} 指向不存在的文件",
                        evidence=f"path={rel_path}",
                        remediation_action=RemediationAction.DELETE,
                        remediation_priority=RemediationPriority.P1,
                    )
                )
            if domain and domain not in valid_domains:
                findings.append(
                    self._make_finding(
                        dimension="D1",
                        severity=FindingSeverity.MEDIUM,
                        category="脚本域无效",
                        file_path=str(abs_path) if rel_path else "scripts/script-manifest.yaml",
                        description=f"脚本 {name} 的 domain '{domain}' 不在有效域列表中",
                        evidence=f"domain={domain}",
                        remediation_action=RemediationAction.UPDATE_REF,
                    )
                )
        self._set_cached_scan("scan_manifest", str_path, findings)
        return findings

    def scan_yaml_contracts(self) -> list[AuditFinding]:
        findings: list[AuditFinding] = []
        try:
            script_path = (
                self._project_root()
                / "scripts"
                / "governance"
                / "d5_architecture"
                / "checkers"
                / "check_contract_code_drift.py"
            )
            if not script_path.is_file():
                return findings
            try:
                result = subprocess.run(
                    [sys.executable, str(script_path), "--warn-only"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(self._project_root()),
                    encoding="utf-8",
                    errors="replace",
                )
            except Exception:
                return findings
            if result.returncode != 0:
                findings.append(
                    self._make_finding(
                        dimension="D5",
                        severity=FindingSeverity.HIGH,
                        category="契约-代码漂移",
                        file_path="src/zephyr/shared/contracts/",
                        description="YAML契约与生成代码之间存在漂移",
                        evidence=result.stdout[:500] if result.stdout else "exit_code=" + str(result.returncode),
                        remediation_action=RemediationAction.FIX,
                        remediation_priority=RemediationPriority.P0,
                        blast_radius=BlastRadius.layer,
                    )
                )
        except Exception as e:
            logger.warning("suppressed error in pipeline_runner", exc_info=True)
        return findings

    def scan_gate_registry(self) -> list[AuditFinding]:
        root = self._project_root()
        registry_path = root / "src" / "zephyr" / "gates" / "_registry.yaml"
        str_path = str(registry_path)
        cached = self._get_cached_scan("scan_gate_registry", str_path)
        if cached is not None:
            return cached
        data = self._load_gate_registry()
        if not data or "gates" not in data:
            return []
        findings: list[AuditFinding] = []
        gates_dir = root / "src" / "zephyr" / "gates"
        for gate in data["gates"]:
            gate_id = gate.get("gate_id", "UNKNOWN")
            gate_file = gate.get("file", "")
            gate_status = gate.get("status", "active")
            if gate_file:
                gate_path = gates_dir / gate_file
                if not gate_path.is_file():
                    findings.append(
                        self._make_finding(
                            dimension="D5",
                            severity=FindingSeverity.HIGH,
                            category="门禁文件缺失",
                            file_path=str(gate_path),
                            description=f"门禁 {gate_id} 的文件 {gate_file} 不存在",
                            evidence=f"file={gate_file}",
                            remediation_action=RemediationAction.CREATE,
                            remediation_priority=RemediationPriority.P1,
                        )
                    )
            if gate_status == "draft":
                findings.append(
                    self._make_finding(
                        dimension="D5",
                        severity=FindingSeverity.LOW,
                        category="门禁状态为草稿",
                        file_path=str(gates_dir / gate_file) if gate_file else str(registry_path),
                        description=f"门禁 {gate_id} 状态为 draft",
                        evidence=f"status={gate_status}",
                    )
                )
        self._set_cached_scan("scan_gate_registry", str_path, findings)
        return findings

    def scan_depgraph(self) -> list[AuditFinding]:
        root = self._project_root()
        dep_path = str(root / PipelineRunner._depgraph_path)
        cached = self._get_cached_scan("scan_depgraph", dep_path)
        if cached is not None:
            return cached
        data = self._load_depgraph()
        if not data or "nodes" not in data or "edges" not in data:
            return []
        findings: list[AuditFinding] = []
        nodes = data.get("nodes", {})
        edges = data.get("edges", [])
        import_adj: dict[str, set[str]] = {}
        owned_by_map: dict[str, list[str]] = {}
        for node_id in nodes:
            import_adj.setdefault(node_id, set())
        print(f"[START] Analyzing depgraph {len(edges)} edges...", file=sys.stderr)
        t_start = time.perf_counter()
        for i, edge in enumerate(edges):
            if (i + 1) % 3000 == 0:
                print(f"[PROGRESS] Edge analysis {i + 1}/{len(edges)}...", file=sys.stderr)
            dep_type = edge.get("dep_type", "")
            from_id = edge.get("from", "")
            to_id = edge.get("to", "")
            if dep_type == "imports" and from_id and to_id:
                import_adj.setdefault(from_id, set()).add(to_id)
            if dep_type == "owned_by" and from_id and to_id:
                owned_by_map.setdefault(from_id, []).append(to_id)
        node_list = list(import_adj.keys())[:1000]
        visited: set[str] = set()
        rec_stack: set[str] = set()
        cycle_nodes: set[str] = set()

        def _dfs(node: str) -> None:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in import_adj.get(node, set()):
                if neighbor not in node_list:
                    continue
                if neighbor not in visited:
                    _dfs(neighbor)
                elif neighbor in rec_stack:
                    cycle_nodes.add(node)
                    cycle_nodes.add(neighbor)
            rec_stack.discard(node)

        for n in node_list:
            if n not in visited:
                _dfs(n)
        if cycle_nodes:
            sample = sorted(cycle_nodes)[:5]
            findings.append(
                self._make_finding(
                    dimension="D5",
                    severity=FindingSeverity.CRITICAL,
                    category="循环依赖",
                    file_path=PipelineRunner._depgraph_path,
                    description=f"依赖图中检测到循环依赖，涉及 {len(cycle_nodes)} 个节点",
                    evidence=f"sample_nodes={sample}",
                    remediation_action=RemediationAction.FIX,
                    remediation_priority=RemediationPriority.P0,
                    blast_radius=BlastRadius.system,
                )
            )
        orphan_count = 0
        for node_id in node_list:
            node_data = nodes.get(node_id)
            if not isinstance(node_data, dict):
                continue
            node_type = node_data.get("type", "")
            if node_type in ("module", "script"):
                if node_id not in owned_by_map:
                    orphan_count += 1
        if orphan_count > 0:
            findings.append(
                self._make_finding(
                    dimension="D5",
                    severity=FindingSeverity.MEDIUM,
                    category="孤儿节点",
                    file_path=PipelineRunner._depgraph_path,
                    description=f"依赖图中检测到 {orphan_count} 个无 owned_by 边的模块/脚本节点",
                    evidence=f"orphan_count={orphan_count}",
                    remediation_action=RemediationAction.INVESTIGATE,
                    remediation_priority=RemediationPriority.P2,
                    blast_radius=BlastRadius.module,
                )
            )
        elapsed = time.perf_counter() - t_start
        print(f"[DONE] Depgraph analysis in {elapsed:.1f}s", file=sys.stderr)
        self._set_cached_scan("scan_depgraph", dep_path, findings)
        return findings

    def scan_phase_gates(self) -> list[AuditFinding]:
        findings: list[AuditFinding] = []
        try:
            from zephyr.governance.ops_governance.phase_check_registry import _CHECK_MAP, GateResult

            for check_name, check_fn in _CHECK_MAP.items():
                if not callable(check_fn):
                    findings.append(
                        self._make_finding(
                            dimension="D5",
                            severity=FindingSeverity.HIGH,
                            category="门禁检查不可调用",
                            file_path="src/zephyr/governance/rule_enforcement/phase_check_registry.py",
                            description=f"门禁检查 {check_name} 不是可调用对象",
                            evidence=f"type={type(check_fn).__name__}",
                            remediation_action=RemediationAction.FIX,
                            remediation_priority=RemediationPriority.P1,
                        )
                    )
                    continue
                try:
                    result = check_fn()
                    if not isinstance(result, GateResult):
                        findings.append(
                            self._make_finding(
                                dimension="D5",
                                severity=FindingSeverity.HIGH,
                                category="门禁检查返回类型错误",
                                file_path="src/zephyr/governance/rule_enforcement/phase_check_registry.py",
                                description=f"门禁检查 {check_name} 返回 {type(result).__name__}，期望 GateResult",
                                evidence=f"return_type={type(result).__name__}",
                                remediation_action=RemediationAction.FIX,
                                remediation_priority=RemediationPriority.P1,
                            )
                        )
                except Exception as exc:
                    findings.append(
                        self._make_finding(
                            dimension="D5",
                            severity=FindingSeverity.HIGH,
                            category="门禁检查执行失败",
                            file_path="src/zephyr/governance/rule_enforcement/phase_check_registry.py",
                            description=f"门禁检查 {check_name} 执行时抛出异常",
                            evidence=f"error={exc}",
                            remediation_action=RemediationAction.FIX,
                            remediation_priority=RemediationPriority.P1,
                        )
                    )
        except Exception as e:
            logger.warning("suppressed error in pipeline_runner", exc_info=True)
        return findings

    def run_full_scan(self, dimensions: list[str] | None = None, dry_run: bool = False) -> PipelineResult:
        start = time.monotonic()
        all_findings: list[AuditFinding] = []
        pipeline_result = self.run(dimensions=dimensions, dry_run=dry_run)
        all_findings.extend(pipeline_result.findings)
        scan_methods = [
            self.scan_registries,
            self.scan_manifest,
            self.scan_yaml_contracts,
            self.scan_gate_registry,
            self.scan_depgraph,
            self.scan_phase_gates,
        ]
        for method in scan_methods:
            try:
                all_findings.extend(method())
            except Exception as e:
                logger.warning("suppressed error in pipeline_runner", exc_info=True)
        elapsed = time.monotonic() - start
        return PipelineResult(
            total_scripts=pipeline_result.total_scripts,
            passed=pipeline_result.passed,
            failed=pipeline_result.failed,
            skipped=pipeline_result.skipped,
            findings=all_findings,
            duration_seconds=round(elapsed, 3),
            dimension_results=pipeline_result.dimension_results,
        )
