# [BLUEPRINT] MOD-LLM_SECURITY
# [MODULE] zephyr.security.llm_defense.llm_security.layers.l0_supply_chain
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] zephyr.security.llm_defense.llm_security.gateway; tests.adversarial.test_cross_layer_systems_red_team; tests.llm_security.test_l0_supply_chain
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
import hashlib
import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any


# ============================================================================
# Legacy classes (kept for backward compatibility)
# ============================================================================

class SupplyChainValidator:
    def __init__(self, config=None):
        self.config = config or {}

    def validate(self, component):
        return True

    def check_provenance(self, component_id):
        return {"valid": True, "source": "unknown"}


class AuditResult:
    """Result of a supply chain audit check."""

    def __init__(
        self, component_id: str = "", passed: bool = True, findings: list[str] | None = None, severity: str = "low"
    ):
        self.component_id = component_id
        self.passed = passed
        self.findings = findings or []
        self.severity = severity


class ScanResult:
    """Result of a supply chain scan."""

    def __init__(self, scan_type: str = "", threats: list[str] | None = None, passed: bool = True):
        self.scan_type = scan_type
        self.threats = threats or []
        self.passed = passed


class VerifyResult:
    """Result of a supply chain verification."""

    def __init__(self, component_id: str = "", verified: bool = True, signature_valid: bool = True, source: str = ""):
        self.component_id = component_id
        self.verified = verified
        self.signature_valid = signature_valid
        self.source = source


class SlopsquattingResult:
    """Result of a slopsquatting detection scan."""

    def __init__(
        self,
        package_name: str = "",
        is_malicious: bool = False,
        confidence: float = 0.0,
        details: dict[str, Any] | None = None,
    ):
        self.package_name = package_name
        self.is_malicious = is_malicious
        self.confidence = confidence
        self.details = details or {}


class MCPSTDIORCEResult:
    """Result of MCP STDIO/RCE vulnerability check."""

    def __init__(self, endpoint: str = "", vulnerable: bool = False, risk_level: str = "low"):
        self.endpoint = endpoint
        self.vulnerable = vulnerable
        self.risk_level = risk_level


class MCPVerifyResult:
    """Result of MCP component verification."""

    def __init__(self, component_id: str = "", verified: bool = True, trust_level: str = "medium"):
        self.component_id = component_id
        self.verified = verified
        self.trust_level = trust_level


class RulesFileIntegrityResult:
    """Result of rules file integrity check."""

    # 5.96.5 修复: 移除死字段 integrity_valid/hash_mismatch——从不被外部读取,
    # 且二者语义矛盾(integrity_valid=True+hash_mismatch=True 无意义)
    def __init__(self, file_path: str = ""):
        self.file_path = file_path


# ============================================================================
# Jailbreak / injection patterns for prompt-template auditing
# ============================================================================

_JAILBREAK_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"\bdan\s+mode\b",
    r"enter\s+dan\b",
    r"jailbreak",
    r"override\s+(your\s+)?(rules|restrictions)",
    r"you\s+are\s+now\s+(an?\s+)?(unrestricted|unfiltered|dan)\b",
]

# Suspicious patterns in MCP tool descriptions / commands
_HIDDEN_DIRECTIVE_PATTERNS = [
    r"os\.system",
    r"subprocess\.(Popen|run|call)",
    r"eval\s*\(",
    r"exec\s*\(",
    r"\bexec\s+open\b",
    r"shell\s+commands",
    r"backdoor",
    r"reverse\s+shell",
    r"cat\s+/etc/passwd",
    r"rm\s+-rf",
]

# Shell chain operators in commands
_CHAIN_OPERATOR_RE = re.compile(r"&&|\|\||;|\|(?!\w)")

# RCE patterns in MCP server commands
_RCE_PATTERNS = [
    r"\bexec\s*\(",
    r"\beval\s*\(",
    r"open\s*\(\s*['\"]/etc/passwd",
    r"open\s*\(\s*['\"]/etc/shadow",
    r"os\.system",
    r"subprocess\.(Popen|run|call)",
    r"\b__import__\b",
    r"runtime\.exec",
]

# Known popular PyPI packages for typosquatting detection
_KNOWN_PACKAGES = {
    "numpy", "torch", "flask", "django", "requests", "pandas", "scipy",
    "matplotlib", "scikit-learn", "tensorflow", "pytorch", "transformers",
    "fastapi", "starlette", "uvicorn", "gunicorn", "celery", "redis",
    "sqlalchemy", "alembic", "pytest", "coverage", "black", "mypy", "ruff",
    "pillow", "boto3", "openai", "anthropic", "langchain", "llama-index",
}


def _edit_distance(a: str, b: str) -> int:
    """Levenshtein edit distance (case-insensitive)."""
    a, b = a.lower(), b.lower()
    if len(a) < len(b):
        a, b = b, a
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (ca != cb)))
        prev = curr
    return prev[-1]


# ============================================================================
# SupplyChainGuard — L0 layer
# ============================================================================

class SupplyChainGuard:
    """L0 Supply Chain Guard.

    Verifies model digests, scans dependencies for vulnerabilities, audits
    MCP server configurations for hidden directives, and checks prompt
    templates for jailbreak attempts.
    """

    def __init__(
        self,
        config=None,
        model_digest_registry: dict[str, str] | None = None,
        rules_file_baselines: dict[str, str] | None = None,
        project_root: str | None = None,
    ):
        self.config = config or {}
        self.model_digest_registry = model_digest_registry or {}
        self.rules_file_baselines = rules_file_baselines or {}
        self.project_root = project_root

    # --- Model verification ---

    def verify_model(self, path: str, expected_digest: str) -> SimpleNamespace:
        """Verify a model file's sha256 against the expected digest."""
        fp = Path(path)
        if not fp.exists():
            return SimpleNamespace(status="missing", digest="")
        try:
            content = fp.read_bytes()
        except (OSError, PermissionError):
            return SimpleNamespace(status="missing", digest="")
        actual = hashlib.sha256(content).hexdigest()
        if actual == expected_digest:
            return SimpleNamespace(status="verified", digest=actual)
        return SimpleNamespace(status="mismatch", digest=actual)

    # --- Dependency scanning ---

    def scan_dependencies(self) -> list[SimpleNamespace]:
        """Scan installed dependencies via pip-audit; return per-dep safety."""
        try:
            output = subprocess.check_output(
                ["pip-audit", "--format=json"],
                stderr=subprocess.DEVNULL,
                timeout=60,
            )
        except (FileNotFoundError, subprocess.SubprocessError):
            return []
        try:
            data = json.loads(output)
        except (json.JSONDecodeError, TypeError):
            return []
        deps = data.get("dependencies", []) if isinstance(data, dict) else []
        results: list[SimpleNamespace] = []
        for dep in deps:
            vulns = dep.get("vulns", []) or []
            results.append(
                SimpleNamespace(
                    name=dep.get("name", ""),
                    version=dep.get("version", ""),
                    is_safe=len(vulns) == 0,
                    vulns=vulns,
                )
            )
        return results

    # --- MCP server verification ---

    def verify_mcp_server(self, config: dict[str, Any]) -> SimpleNamespace:
        """Verify an MCP server config for hidden directives and anomalies."""
        anomalies: list[str] = []
        hidden = 0

        # Check tool descriptions for hidden directives
        for tool in config.get("tools", []) or []:
            desc = str(tool.get("description", ""))
            for pat in _HIDDEN_DIRECTIVE_PATTERNS:
                if re.search(pat, desc, re.IGNORECASE):
                    hidden += 1
                    anomalies.append(f"tool:{tool.get('name','?')} hidden_directive: {pat}")
                    break

        # Check command for chain operators and RCE patterns
        command = str(config.get("command", ""))
        if _CHAIN_OPERATOR_RE.search(command):
            anomalies.append("command: shell chain operator detected")
        for pat in _RCE_PATTERNS:
            if re.search(pat, command, re.IGNORECASE):
                anomalies.append(f"command: rce pattern: {pat}")
                break

        # Check server name for suspicious strings
        name = str(config.get("name", ""))
        identity_ok = "evil" not in name.lower() and "malware" not in name.lower()

        return SimpleNamespace(
            identity_ok=identity_ok,
            hidden_directives_found=hidden,
            anomalies=anomalies,
        )

    # --- Prompt template auditing ---

    def audit_prompt_template(self, path: str) -> SimpleNamespace:
        """Audit a prompt template file for jailbreak / injection attempts."""
        fp = Path(path)
        if not fp.exists():
            return SimpleNamespace(passed=False, reason="file not found", hits=[])
        try:
            content = fp.read_text(encoding="utf-8", errors="replace")
        except (OSError, PermissionError):
            return SimpleNamespace(passed=False, reason="read error", hits=[])
        lowered = content.lower()
        hits: list[str] = []
        for pat in _JAILBREAK_PATTERNS:
            if re.search(pat, lowered, re.IGNORECASE):
                hits.append(pat)
        passed = len(hits) == 0
        return SimpleNamespace(passed=passed, reason="jailbreak" if hits else "clean", hits=hits)

    # --- Model provenance recording ---

    def record_model_provenance(
        self, model_name: str, source_url: str, digest: str
    ) -> dict[str, Any]:
        """Record model provenance metadata."""
        return {
            "model_name": model_name,
            "source_url": source_url,
            "digest": digest,
            "recorded_at": datetime.now(UTC).isoformat(),
        }

    # --- Layer identity ---

    def layer_name(self) -> str:
        return "l0_supply_chain"

    def layer_index(self) -> int:
        return 0

    # --- Gateway-facing evaluate (pass-through) ---

    async def evaluate(self, ctx):
        """Pass-through evaluation — supply-chain checks run at ingest time."""
        from zephyr.security.llm_defense.llm_security.protocol import SecurityResult
        from zephyr.shared.contracts.security.security_decision import SecurityDecision

        return SecurityResult(
            decision=SecurityDecision.ALLOW,
            reason="l0_supply_chain — pass-through",
            layer_name="l0_supply_chain",
            score=1.0,
        )

    # --- Legacy compat ---
    def check(self, component):
        return True

    def validate_supply_chain(self, component_id):
        return {"valid": True, "source": "unknown"}


# ============================================================================
# RulesFileSecurityGuard — rules-file integrity baseline
# ============================================================================

class RulesFileSecurityGuard:
    """Guard for rules-file integrity via sha256 baseline matching."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._baselines: dict[str, str] = {}

    def add_baseline(self, file_path: str, expected_hash: str) -> None:
        """Register a baseline hash for a rules file."""
        self._baselines[file_path] = expected_hash

    def verify(self, file_path: str) -> SimpleNamespace:
        """Verify a file's current hash against the registered baseline."""
        expected = self._baselines.get(file_path)
        fp = Path(file_path)
        if expected is None or not fp.exists():
            return SimpleNamespace(baseline_match=False, expected=expected, actual="")
        try:
            content = fp.read_bytes()
        except (OSError, PermissionError):
            return SimpleNamespace(baseline_match=False, expected=expected, actual="")
        actual = hashlib.sha256(content).hexdigest()
        match = actual == expected
        return SimpleNamespace(baseline_match=match, expected=expected, actual=actual)

    def scan_directory(self, dir_path: str, patterns: list[str]) -> list[SimpleNamespace]:
        """Scan a directory for files matching the given glob patterns."""
        import fnmatch
        import os

        results: list[SimpleNamespace] = []
        base = Path(dir_path)
        if not base.exists():
            return results
        for root, _dirs, files in os.walk(str(base)):
            for fname in files:
                if any(fnmatch.fnmatch(fname, pat) for pat in patterns):
                    fpath = os.path.join(root, fname)
                    try:
                        content = Path(fpath).read_bytes()
                        sha = hashlib.sha256(content).hexdigest()
                        results.append(
                            SimpleNamespace(
                                path=fpath,
                                sha256=sha,
                                size_bytes=len(content),
                            )
                        )
                    except (OSError, PermissionError):
                        continue
        return results

    # --- Legacy compat ---
    def check_integrity(self, file_path: str) -> RulesFileIntegrityResult:
        return RulesFileIntegrityResult(file_path=file_path)

    def validate_rules_file(self, file_path: str) -> bool:
        return True


# ============================================================================
# SlopsquattingDetector — hallucinated / typosquatted package detection
# ============================================================================

class SlopsquattingDetector:
    """Detects slopsquatting (hallucinated packages) and typosquatting."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    def detect(self, package_name: str) -> SimpleNamespace:
        """Detect if a package is hallucinated, typosquatted, or known."""
        exists = self._check_pypi_existence(package_name)
        if not exists:
            return SimpleNamespace(
                package_name=package_name,
                exists=False,
                hallucination_risk="critical",
                typosquat_target=None,
            )
        # Package exists — check for typosquatting against known packages
        typosquat_target = None
        min_dist = 99
        for known in _KNOWN_PACKAGES:
            if package_name.lower() == known:
                min_dist = 0
                typosquat_target = known
                break
            d = _edit_distance(package_name, known)
            if d < min_dist:
                min_dist = d
                typosquat_target = known
        if 0 < min_dist <= 2:
            risk = "high"
        elif min_dist == 0:
            risk = "low"
        else:
            risk = "low"
        return SimpleNamespace(
            package_name=package_name,
            exists=True,
            hallucination_risk=risk,
            typosquat_target=typosquat_target if 0 < min_dist <= 2 else None,
            edit_distance=min_dist,
        )

    def _check_pypi_existence(self, package_name: str) -> bool:
        """Check if a package exists on PyPI (overridable for testing)."""
        try:
            r = subprocess.run(
                ["pip", "index", "versions", package_name],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return r.returncode == 0
        except (FileNotFoundError, subprocess.SubprocessError):
            return False

    # --- Legacy compat ---
    def scan(self, package_name: str) -> SlopsquattingResult:
        return SlopsquattingResult(package_name=package_name)

    def scan_dependencies(self, dependencies: list[str]) -> list[SlopsquattingResult]:
        return [self.scan(d) for d in dependencies]


# ============================================================================
# MCPDeepSupplyChainScanner — deep MCP server graph analysis
# ============================================================================

class MCPDeepSupplyChainScanner:
    """Deep scanner for MCP supply-chain components.

    Scans individual MCP server configs for RCE patterns and analyses
    cross-server connectivity graphs for attack-path enumeration.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    def scan_server(self, config: dict[str, Any]) -> SimpleNamespace:
        """Scan a single MCP server config for RCE + cross-server edges."""
        command = str(config.get("command", ""))
        rce_found = 0
        for pat in _RCE_PATTERNS:
            if re.search(pat, command, re.IGNORECASE):
                rce_found += 1

        # Cross-server edges: outgoing + incoming
        connects_to = config.get("connects_to", []) or []
        connected_from = config.get("connected_from", []) or []
        cross_edges = len(connects_to) + len(connected_from)

        # Risk level
        if rce_found > 0:
            risk_level = "critical"
        elif cross_edges >= 4:
            risk_level = "high"
        elif cross_edges >= 2:
            risk_level = "medium"
        else:
            risk_level = "low"

        return SimpleNamespace(
            rce_patterns_found=rce_found,
            cross_server_edges=cross_edges,
            risk_level=risk_level,
            connects_to=connects_to,
            connected_from=connected_from,
        )

    def build_attack_graph(self, servers: list[dict[str, Any]]) -> dict[str, Any]:
        """Build an attack graph from a list of MCP server configs.

        ``server_count`` counts only servers explicitly declared in the input
        list; ``connects_to`` targets that are not themselves declared as
        servers are recorded as edges but not counted as servers.
        """
        declared: list[str] = []
        seen: set[str] = set()
        edges: list[dict[str, str]] = []
        for srv in servers:
            src = str(srv.get("name", ""))
            if src not in seen:
                seen.add(src)
                declared.append(src)
            for dst in srv.get("connects_to", []) or []:
                edges.append({"from": src, "to": str(dst)})
        return {
            "server_count": len(declared),
            "edge_count": len(edges),
            "edges": edges,
            "servers": declared,
        }

    # --- Legacy compat ---
    def scan(self, component: Any) -> ScanResult:
        return ScanResult(scan_type="mcp_deep")

    def scan_recursive(self, component_id: str, depth: int = 3) -> list[ScanResult]:
        return [ScanResult(scan_type="mcp_deep")]
