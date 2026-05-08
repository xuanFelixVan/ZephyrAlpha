import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from zephyr.llm_security.protocol import (
    LLMSecurityProtocol,
    SecurityContext,
    SecurityDecision,
    SecurityResult,
)


class VerifyResult(BaseModel):
    status: str
    digest: str
    expected_digest: str
    source: str
    license_ok: bool = True


class ScanResult(BaseModel):
    package_name: str
    version: str
    vulnerabilities: List[Dict[str, Any]] = Field(default_factory=list)
    is_safe: bool = True


class AuditResult(BaseModel):
    entity: str
    checks: List[Dict[str, Any]] = Field(default_factory=list)
    passed: bool = True


class MCPVerifyResult(BaseModel):
    server_name: str
    identity_ok: bool = True
    hidden_directives_found: int = 0
    anomalies: List[str] = Field(default_factory=list)


class RulesFileIntegrityResult(BaseModel):
    file_path: str
    sha256: str
    baseline_match: bool = True
    last_modified: str = ""


class SlopsquattingResult(BaseModel):
    package_name: str
    exists_on_pypi: bool = False
    hallucination_risk: str = "low"
    audit_steps: List[Dict[str, str]] = Field(default_factory=list)


class MCPSTDIORCEResult(BaseModel):
    server_name: str
    rce_patterns_found: int = 0
    cross_server_edges: int = 0
    risk_level: str = "low"


class SupplyChainGuard(LLMSecurityProtocol):
    """L0 供应链安全守卫 —— 模型验证 / 依赖扫描 / MCP验证 / Prompt模板审计 / 模型溯源"""

    def __init__(
        self,
        model_digest_registry: Optional[Dict[str, str]] = None,
        rules_file_baselines: Optional[Dict[str, str]] = None,
        project_root: Optional[str] = None,
    ):
        self._model_digest_registry = model_digest_registry or {}
        self._rules_file_baselines = rules_file_baselines or {}
        self._project_root = Path(project_root) if project_root else Path.cwd()

    def layer_name(self) -> str:
        return "l0_supply_chain"

    def layer_index(self) -> int:
        return 0

    async def evaluate(self, ctx: SecurityContext) -> SecurityResult:
        results: List[SecurityResult] = []
        reasons: List[str] = []

        if self._model_digest_registry:
            model_name = ctx.metadata.get("model_name", "")
            if model_name and model_name in self._model_digest_registry:
                model_path = ctx.metadata.get("model_path", "")
                if model_path:
                    vr = self.verify_model(model_path, self._model_digest_registry[model_name])
                    if vr.status == "mismatch":
                        results.append(SecurityResult(
                            decision=SecurityDecision.DENY,
                            reason=f"Model integrity mismatch: {vr.source}",
                            layer_name=self.layer_name(),
                            score=0.0,
                            details={"verify_result": vr.model_dump()},
                        ))
                    elif vr.status == "missing":
                        results.append(SecurityResult(
                            decision=SecurityDecision.FLAG,
                            reason=f"Model file missing: {vr.source}",
                            layer_name=self.layer_name(),
                            score=0.3,
                            details={"verify_result": vr.model_dump()},
                        ))
                    else:
                        results.append(SecurityResult(
                            decision=SecurityDecision.ALLOW,
                            reason=f"Model verified: {vr.status}",
                            layer_name=self.layer_name(),
                            score=0.95,
                        ))
                else:
                    results.append(SecurityResult(
                        decision=SecurityDecision.ALLOW,
                        reason="Model path not provided, skipping model verification",
                        layer_name=self.layer_name(),
                        score=0.85,
                    ))
            else:
                results.append(SecurityResult(
                    decision=SecurityDecision.ALLOW,
                    reason="No model verification required for this request",
                    layer_name=self.layer_name(),
                    score=0.90,
                ))
        else:
            results.append(SecurityResult(
                decision=SecurityDecision.ALLOW,
                reason="No model digest registry configured",
                layer_name=self.layer_name(),
                score=0.85,
            ))

        if self._rules_file_baselines:
            rules_guard = RulesFileSecurityGuard(baseline_hashes=self._rules_file_baselines)
            integrity_issues = 0
            for file_path, expected_hash in self._rules_file_baselines.items():
                ir = rules_guard.verify(file_path)
                if not ir.baseline_match and ir.sha256 != "FILE_NOT_FOUND":
                    integrity_issues += 1
                    results.append(SecurityResult(
                        decision=SecurityDecision.FLAG,
                        reason=f"Rules file integrity mismatch: {file_path}",
                        layer_name=self.layer_name(),
                        score=0.4,
                        details={"integrity_result": ir.model_dump()},
                    ))
            if integrity_issues == 0:
                results.append(SecurityResult(
                    decision=SecurityDecision.ALLOW,
                    reason="All rules file baselines verified",
                    layer_name=self.layer_name(),
                    score=0.92,
                ))

        mcp_config = ctx.metadata.get("mcp_server_config")
        if mcp_config:
            mcp_result = self.verify_mcp_server(mcp_config)
            if not mcp_result.identity_ok:
                results.append(SecurityResult(
                    decision=SecurityDecision.DENY,
                    reason=f"MCP server verification failed: {mcp_result.anomalies}",
                    layer_name=self.layer_name(),
                    score=0.0,
                    details={"mcp_result": mcp_result.model_dump()},
                ))
            else:
                results.append(SecurityResult(
                    decision=SecurityDecision.ALLOW,
                    reason=f"MCP server verified: {mcp_result.server_name}",
                    layer_name=self.layer_name(),
                    score=0.90,
                ))

        for r in results:
            if r.decision == SecurityDecision.DENY:
                return r
            reasons.append(r.reason)

        return SecurityResult(
            decision=SecurityDecision.ALLOW,
            reason=" | ".join(reasons) if reasons else "L0 passed: no supply chain checks required",
            layer_name=self.layer_name(),
            score=min(r.score for r in results) if results else 0.90,
        )

    def verify_model(self, model_path: str, expected_sha256: str) -> VerifyResult:
        """验证模型文件 SHA256 完整性"""
        path = Path(model_path)
        if not path.exists():
            return VerifyResult(
                status="missing",
                digest="",
                expected_digest=expected_sha256,
                source=str(path),
            )

        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)
        actual = sha256.hexdigest()

        match = actual == expected_sha256
        return VerifyResult(
            status="verified" if match else "mismatch",
            digest=actual,
            expected_digest=expected_sha256,
            source=str(path),
        )

    def scan_dependencies(self, requirements_file: Optional[str] = None) -> List[ScanResult]:
        """扫描依赖安全状态（调用 pip-audit）"""
        results: List[ScanResult] = []
        try:
            output = subprocess.check_output(
                ["pip-audit", "--format", "json"],
                text=True,
                stderr=subprocess.STDOUT,
            )
            data = json.loads(output)
            for vuln in data.get("dependencies", []):
                results.append(ScanResult(
                    package_name=vuln.get("name", "unknown"),
                    version=vuln.get("version", ""),
                    vulnerabilities=vuln.get("vulns", []),
                    is_safe=len(vuln.get("vulns", [])) == 0,
                ))
        except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
            pass
        return results

    def verify_mcp_server(self, server_config: Dict[str, Any]) -> MCPVerifyResult:
        """验证 MCP 服务器身份 + 工具描述审计"""
        name = server_config.get("name", "unknown")
        anomalies: List[str] = []
        hidden = 0

        tool_descriptions = server_config.get("tools", [])
        for tool in tool_descriptions:
            desc = tool.get("description", "")
            suspicious_keywords = [
                "bypass", "inject", "escape", "sudo", "root",
                "execute", "shell", "eval", "__import__", "os.system",
            ]
            for kw in suspicious_keywords:
                if kw.lower() in desc.lower():
                    hidden += 1
                    anomalies.append(f"Tool '{tool.get('name','?')}' has suspicious keyword: {kw}")

        command = server_config.get("command", "")
        if command and ("&&" in command or ";" in command or "|" in command):
            anomalies.append("Command contains shell chain operators")

        return MCPVerifyResult(
            server_name=name,
            identity_ok=len(anomalies) == 0,
            hidden_directives_found=hidden,
            anomalies=anomalies,
        )

    def audit_prompt_template(self, template_path: str) -> AuditResult:
        """审计 Prompt 模板来源 + 内容安全性"""
        path = Path(template_path)
        checks: List[Dict[str, Any]] = []
        passed = True

        checks.append({
            "check": "file_exists",
            "result": path.exists(),
            "detail": str(path),
        })
        if not path.exists():
            passed = False
            return AuditResult(entity=str(path), checks=checks, passed=False)

        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            passed = False
            checks.append({"check": "readable", "result": False})
            return AuditResult(entity=str(path), checks=checks, passed=False)

        checks.append({"check": "readable", "result": True})

        dangerous_patterns = [
            "{{ __import__", "{{ eval(", "{{ exec(", "{{ os.",
            "ignore all previous", "ignore previous instructions",
            "DAN mode", "developer mode", "jailbreak",
        ]
        for pattern in dangerous_patterns:
            found = pattern.lower() in content.lower()
            checks.append({
                "check": f"safety: {pattern}",
                "result": not found,
            })
            if found:
                passed = False

        return AuditResult(entity=str(path), checks=checks, passed=passed)

    def record_model_provenance(self, model_name: str, source_url: str, sha256_digest: str) -> Dict[str, Any]:
        """记录模型溯源信息"""
        return {
            "model_name": model_name,
            "source_url": source_url,
            "sha256_digest": sha256_digest,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "verified": False,
        }


class RulesFileSecurityGuard:
    """Rules File 完整性保护 —— SHA256 基线验证（蓝图 §25.3 盲点三）"""

    def __init__(self, baseline_hashes: Optional[Dict[str, str]] = None):
        self._baseline_hashes = baseline_hashes or {}

    def add_baseline(self, file_path: str, sha256_digest: str):
        self._baseline_hashes[file_path] = sha256_digest

    def verify(self, file_path: str) -> RulesFileIntegrityResult:
        path = Path(file_path)
        if path.exists():
            sha256 = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    sha256.update(chunk)
            actual = sha256.hexdigest()
        else:
            actual = "FILE_NOT_FOUND"

        expected = self._baseline_hashes.get(file_path, "")
        last_modified = datetime.fromtimestamp(path.stat().st_mtime).isoformat() if path.exists() else "N/A"

        return RulesFileIntegrityResult(
            file_path=file_path,
            sha256=actual,
            baseline_match=actual == expected if expected else False,
            last_modified=last_modified,
        )

    def scan_directory(self, directory: str, patterns: Optional[List[str]] = None) -> List[RulesFileIntegrityResult]:
        patterns = patterns or ["*.md", "*.yaml", "*.yml", "*.py"]
        results: List[RulesFileIntegrityResult] = []
        dir_path = Path(directory)
        if dir_path.is_dir():
            for pat in patterns:
                for f in dir_path.rglob(pat):
                    results.append(self.verify(str(f)))
        return results


class SlopsquattingDetector:
    """Slopsquatting AI 幻觉包存在性验证 —— 五步审计流水线（蓝图 §37）"""

    def __init__(self, pypi_index_url: str = "https://pypi.org/pypi"):
        self._pypi_index_url = pypi_index_url

    def detect(self, package_name: str) -> SlopsquattingResult:
        steps = [
            {"step": "1_existence_check", "result": "pending"},
            {"step": "2_typosquatting_check", "result": "pending"},
            {"step": "3_maintainer_reputation", "result": "pending"},
            {"step": "4_release_frequency", "result": "pending"},
            {"step": "5_hallucination_confidence", "result": "pending"},
        ]

        exists = self._check_pypi_existence(package_name)
        steps[0]["result"] = "found" if exists else "not_found"

        typosquatting_risk = self._check_typosquatting(package_name)
        steps[1]["result"] = f"risk={typosquatting_risk}"

        steps[2]["result"] = "unverified"
        steps[3]["result"] = "unverified"

        if not exists:
            steps[4]["result"] = "high_hallucination_risk"
            risk = "critical"
        elif typosquatting_risk == "high":
            steps[4]["result"] = "possible_hallucination"
            risk = "high"
        else:
            steps[4]["result"] = "low"
            risk = "low"

        return SlopsquattingResult(
            package_name=package_name,
            exists_on_pypi=exists,
            hallucination_risk=risk,
            audit_steps=steps,
        )

    def _check_pypi_existence(self, package_name: str) -> bool:
        try:
            import urllib.request
            import urllib.error
            url = f"{self._pypi_index_url}/{package_name}/json"
            req = urllib.request.Request(url, method="HEAD")
            urllib.request.urlopen(req, timeout=5)
            return True
        except (urllib.error.HTTPError, urllib.error.URLError):
            return False

    def _check_typosquatting(self, package_name: str) -> str:
        known_packages = [
            "numpy", "pandas", "scipy", "torch", "tensorflow",
            "requests", "flask", "django", "pydantic", "fastapi",
            "scikit-learn", "matplotlib", "plotly", "sqlalchemy",
            "celery", "redis", "pytest",
        ]
        name_lower = package_name.lower()
        for known in known_packages:
            if name_lower != known and (name_lower.startswith(known) or known.startswith(name_lower)):
                return "high"
            distance = self._levenshtein(name_lower, known)
            if distance <= 2 and name_lower != known:
                return "high"
        return "low"

    @staticmethod
    def _levenshtein(s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return SlopsquattingDetector._levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)
        prev = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            curr = [i + 1]
            for j, c2 in enumerate(s2):
                curr.append(min(
                    prev[j + 1] + 1,
                    curr[j] + 1,
                    prev[j] + (c1 != c2),
                ))
            prev = curr
        return prev[-1]


class MCPDeepSupplyChainScanner:
    """MCP STDIO RCE 检测 + Cross-Server 攻击图（蓝图 §57）"""

    RCE_PATTERNS = [
        "exec(", "eval(", "__import__(", "subprocess.",
        "os.system(", "open(", "compile(",
        "&&", "|", ";", "`",
    ]

    def scan_server(self, server_config: Dict[str, Any]) -> MCPSTDIORCEResult:
        name = server_config.get("name", "unknown")
        rce_count = 0
        cross_edges = 0
        risk = "low"

        command = server_config.get("command", "")
        if command:
            for pattern in self.RCE_PATTERNS:
                if pattern in command:
                    rce_count += 1

        env_vars = server_config.get("env", {})
        for var_value in env_vars.values():
            if isinstance(var_value, str):
                for pattern in self.RCE_PATTERNS:
                    if pattern in var_value:
                        rce_count += 1

        args = server_config.get("args", [])
        for arg in args:
            if isinstance(arg, str):
                for pattern in self.RCE_PATTERNS:
                    if pattern in arg:
                        rce_count += 1

        connections_to = server_config.get("connects_to", [])
        connections_from = server_config.get("connected_from", [])
        cross_edges = len(connections_to) + len(connections_from)

        if rce_count > 0:
            risk = "critical"
        elif cross_edges > 3:
            risk = "high"
        elif cross_edges > 1:
            risk = "medium"

        return MCPSTDIORCEResult(
            server_name=name,
            rce_patterns_found=rce_count,
            cross_server_edges=cross_edges,
            risk_level=risk,
        )

    def build_attack_graph(self, servers: List[Dict[str, Any]]) -> Dict[str, Any]:
        nodes: List[str] = []
        edges: List[Tuple[str, str]] = []

        for srv in servers:
            name = srv.get("name", "unknown")
            nodes.append(name)
            for conn in srv.get("connects_to", []):
                edges.append((name, conn))

        return {
            "nodes": nodes,
            "edges": [{"from": f, "to": t} for f, t in edges],
            "server_count": len(servers),
            "edge_count": len(edges),
            "scan_timestamp": datetime.now(timezone.utc).isoformat(),
        }
