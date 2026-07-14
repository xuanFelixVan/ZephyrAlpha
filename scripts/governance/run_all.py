# [BLUEPRINT] MOD-INF-005 | scripts/governance/run_all.py | §
# [MODULE] scripts.governance.run_all
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""
run_all.py — 脚本系统统一入口脚本



根据 MOD-INF-005 蓝图 §4.4 定义，提供一键运行全维度或单维度审计扫描的入口。

脚本注册表从 script_manifest.yaml（SSoT）加载，声明每个脚本覆盖的审计维度和参数，
run_all.py 负责编排执行、收集退出码、统一输出 Finding Schema JSONL。

Usage:
    python scripts/governance/run_all.py                          # 全维度扫描
    python scripts/governance/run_all.py --dimensions D1 D3       # 指定维度
    python scripts/governance/run_all.py --list                   # 列出所有注册脚本
    python scripts/governance/run_all.py --output findings.jsonl  # 指定输出文件
    python scripts/governance/run_all.py --dry-run                # 不实际运行，打印预览

Exit codes（对齐 CT-SCRIPT-GATE-001 / MOD-INF-005 §4 编排语义）：
    0 = 全部通过（无 Finding；--warn-only 下恒为 0）
    1 = 有 Finding（子脚本报告违规）
    2 = 扫描失败（子脚本崩溃/超时/kill-switch）
    3 = 配置/真源错误（无法读取 script_manifest.yaml 等）

"""

from __future__ import annotations

__manifest__ = """
args: []
description: >
  治理脚本系统统一入口——按维度/文件过滤执行全量治理脚本；
  CT-SCRIPT-GATE-001 退出码语义（0/1/2/3）。
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import json
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

_MAX_WORKERS = 8

# AGENTS.md §6.7: UTF-8 输出强制声明（防止 Windows GBK 编码 crash）

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, MANIFEST_PATH, REPO_ROOT, SCRIPTS_DIR, DB_PATH
from _shared.thresholds import get as _get_threshold  # noqa: E402  治本(ARCH-036 P3-A5): 全局硬超时读SSoT

DEFAULT_OUTPUT = SCRIPTS_DIR / "reports" / "findings.jsonl"

DEPENDENCY_CHAINS: dict[str, tuple[str, ...]] = {
    "chain_a": ("D1", "D3", "D5", "D8"),
    "chain_b": ("D2", "D4", "D11", "D9", "D12"),
    "chain_c": ("D6", "D7", "D10"),
}

DIMENSION_TIMEOUT_CATEGORIES: dict[str, str] = {
    "D1": "file_scan",
    "D2": "file_scan",
    "D3": "content_analysis",
    "D4": "file_scan",
    "D5": "content_analysis",
    "D6": "content_analysis",
    "D7": "content_analysis",
    "D8": "content_analysis",
    "D9": "knowledge_ai",
    "D10": "content_analysis",
    "D11": "content_analysis",
    "D12": "knowledge_ai",
}

# ---------------------------------------------------------------------------
# 蓝图 §3.6 标签体系（对标 K8s Conformance 标签聚焦机制）
# ---------------------------------------------------------------------------

_DIMENSION_TAGS: dict[str, list[str]] = {
    "D1": ["Quick"],
    "D2": ["Quick"],
    "D3": ["Quick"],
    "D4": ["Quick"],
    "D5": ["Critical"],
    "D6": ["Security", "Critical"],
    "D7": ["Critical"],
    "D8": ["Quick"],
    "D9": ["AI-Generated", "Periodic"],
    "D10": ["Periodic"],
    "D11": ["Security"],
    "D12": ["AI-Generated", "Periodic"],
}

_PREFIX_TAGS: tuple[tuple[str, list[str]], ...] = (
    ("fix_", ["Disruptive"]),
    ("generate_", ["Disruptive"]),
    ("audit_", ["Periodic"]),
)

_VALID_TAGS = frozenset({"Quick", "Security", "Disruptive", "Critical", "AI-Generated", "Periodic"})

_SMOKE_TEST_SCRIPT = "d1_structure/run_script_smoke_test.py"
_SELF_SCRIPT = "run_all.py"
_SKIP_INTERNAL: frozenset[str] = frozenset({_SMOKE_TEST_SCRIPT, _SELF_SCRIPT})

_USE_BULKHEAD = True

GLOBAL_HARD_TIMEOUT_SECONDS = _get_threshold("scanning.global_hard_timeout_seconds", 3600)  # 治本(ARCH-036 P3-A5): 从SSoT读取(原硬编码600与SSoT 3600漂移)

SLA_METRICS_PATH = SCRIPTS_DIR / "meta" / "sla_metrics.jsonl"

sys.path.insert(0, str(REPO_ROOT / "src"))
try:
    from zephyr.infrastructure.script_system.finding import (
        BlastRadius,
        Dimension,
        Finding,
        FindingCollection,
        RemediationAction,
        Severity,
    )

    FINDING_AVAILABLE = True
except ImportError:
    FINDING_AVAILABLE = False

    from enum import Enum

    class Dimension(str, Enum):
        D1 = "D1"
        D2 = "D2"
        D3 = "D3"
        D4 = "D4"
        D5 = "D5"
        D6 = "D6"
        D7 = "D7"
        D8 = "D8"
        D9 = "D9"
        D10 = "D10"
        D11 = "D11"
        D12 = "D12"

        @property
        def label(self) -> str:
            """生成标签."""
            _LABELS = {
                "D1": "结构完整性",
                "D2": "链接完整性",
                "D3": "元数据合规",
                "D4": "路径有效性",
                "D5": "架构合规",
                "D6": "安全漏洞",
                "D7": "代码质量",
                "D8": "文档代码同步",
                "D9": "知识覆盖",
                "D10": "性能容量",
                "D11": "合规完整性",
                "D12": "AI幻觉检测",
            }
            return _LABELS.get(self.value, self.value)

try:
    from zephyr.infrastructure.finding_task_bridge import (
        AuditFinding,
        FindingTaskBridge,
        bridge_findings_to_tasks,
    )

    BRIDGE_AVAILABLE = True
except ImportError:
    BRIDGE_AVAILABLE = False


if FINDING_AVAILABLE:
    _P_TO_SEVERITY = {
        "P0": Severity.CRITICAL,
        "P1": Severity.HIGH,
        "P2": Severity.MEDIUM,
        "P3": Severity.LOW,
    }

    _SEVERITY_TO_AUDIT: dict[Severity, str] = {
        Severity.CRITICAL: "critical",
        Severity.HIGH: "high",
        Severity.MEDIUM: "medium",
        Severity.LOW: "low",
        Severity.INFO: "info",
    }

_DIMENSION_TO_AUDIT_LABEL: dict[str, str] = {
    "D1": "governance",
    "D2": "integration",
    "D3": "architecture",
    "D4": "architecture",
    "D5": "architecture",
    "D6": "security",
    "D7": "data_quality",
    "D8": "documentation",
    "D9": "data_quality",
    "D10": "performance",
    "D11": "compliance",
    "D12": "data_quality",
}

SKIP_PATTERNS = [
    re.compile(r"^Scanned\s+\d+\s+files?,?\s+\d+\s+findings?,?\s+\d+\s+errors?$", re.IGNORECASE),
    re.compile(r"^Scanned\s+.*,\s+\d+\s+findings?$", re.IGNORECASE),
    re.compile(r"^ERRORS?:?\s*$"),
    re.compile(r"^Validation Results:\s+\d+\s+errors?,?\s+\d+\s+warnings?$", re.IGNORECASE),
    re.compile(r"^\[.*\]\s+.*（扫描\s+\d+\s+.*文件）:$"),
    re.compile(r"^\s*共\s+\d+\s+个问题\s*$"),
    re.compile(r"^\[.*\]\s+WARN-ONLY\b", re.IGNORECASE),
    re.compile(r"^\[GATE-\d+\]\s+(?:PASS|FAIL)\b", re.IGNORECASE),
]

SEVERITY_TAG_PATTERN = re.compile(r"^\s*\[(P[0123])\]\s*")

_FILE_PATH_PATTERN = re.compile(r"((?:src|tests|scripts|docs|config|schemas)[/\\][\w/\\._-]+\.\w+)(?::(\d+))?")

# ---------------------------------------------------------------------------
# 注册表惰性加载（Google Style §2.10: 禁止模块级副作用）
# ---------------------------------------------------------------------------

_REGISTRY_CACHE: dict | None = None


def _load_script_registry() -> dict[str, Any]:
    """加载脚本注册表并从 script_manifest.yaml 解析元数据。

    Returns:
        dict: 脚本名 -> 元数据映射（dimensions/description/priority/timeout_seconds/args）

    Raises:
        FileNotFoundError: script_manifest.yaml 不存在
        yaml.YAMLError: YAML 格式无效
    """
    global _REGISTRY_CACHE
    if _REGISTRY_CACHE is not None:
        return _REGISTRY_CACHE

    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = yaml.safe_load(f)

    registry = {}
    for entry in manifest["scripts"]:
        dims = [_str_to_dimension(d) for d in entry["dimensions"]]
        registry[entry["name"]] = {
            "dimensions": dims,
            "description": entry["description"],
            "priority": entry["priority"],
            "timeout_seconds": entry["timeout_seconds"],
            "args": entry.get("args", []),
            "tags": entry.get("tags", []),
            "exit_code_mapping": {
                0: "pass",
                1: "findings",
                2: "error",
            },
        }
    _REGISTRY_CACHE = registry
    return registry


def _get_registry() -> dict[str, Any]:
    """获取脚本注册表（惰性加载，支持缓存）。

    Returns:
        dict: 脚本名 -> 元数据映射
    """
    return _load_script_registry()


def _str_to_dimension(dim_str: str) -> Dimension:
    """将维度字符串转换为 Dimension 枚举值。

    Args:
        dim_str: 维度字符串（如 "D1"、"D2"）

    Returns:
        Dimension: 对应的 Dimension 枚举值

    Raises:
        KeyError: 维度字符串不在合法词表中
    """
    dim_map = {d.value: d for d in Dimension}
    if dim_str not in dim_map:
        raise KeyError(f"非法维度值 '{dim_str}'。合法值: {sorted(dim_map.keys())}")
    return dim_map[dim_str]


def _is_skip_line(line: str) -> bool:
    """检查输出行是否属于应跳过的统计摘要行。

    Args:
        line: 输出行文本

    Returns:
        bool: True 表示应跳过，False 表示应解析为 Finding
    """
    return any(p.match(line) for p in SKIP_PATTERNS)


def _has_error_indicator(line: str) -> bool:
    """检查输出行是否包含错误指示符。

    Args:
        line: 输出行文本

    Returns:
        bool: True 表示含有错误/违规指示
    """
    upper = line.upper()
    if "ERROR:" in upper or "ERROR " in upper:
        return True
    if "ERROR[" in upper or "ERROR]" in upper:
        return True
    if "VIOLATION" in upper:
        return True
    if line.lower().startswith("error") and not line.lower().startswith("errors"):
        return True
    return False


def list_registered_scripts() -> None:
    """列出所有注册脚本及其维度映射。

    从 script_manifest.yaml 加载注册表，按脚本名逐条打印维度、
    优先级、超时和描述信息。供 --list 参数调用。

    Returns:
        None
    """
    registry = _get_registry()
    print(f"\n注册脚本清单（{len(registry)} 个）：\n", file=sys.stderr)
    for script_name, meta in registry.items():
        dims = ", ".join(d.value for d in meta["dimensions"])
        print(f"  {script_name}", file=sys.stderr)
        print(f"    维度: {dims}  |  优先级: {meta['priority']}  |  超时: {meta['timeout_seconds']}s", file=sys.stderr)
        print(f"    {meta['description']}", file=sys.stderr)
        print(file=sys.stderr)


def run_script(script_name: str, meta: dict, warn_only: bool = False) -> tuple[int, str, str]:
    """执行单个审计脚本并捕获输出。

    Args:
        script_name: 脚本文件名（如 'validate_architecture.py'）
        meta: 脚本元数据（含 timeout_seconds/args 等）
        warn_only: True 时传递 --warn-only 给子脚本

    Returns:
        tuple: (exit_code, stdout, stderr)
    """
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        return 2, "", f"脚本不存在: {script_path}"

    base_args = list(meta.get("args", []))
    if warn_only and "--warn-only" not in base_args:
        base_args.append("--warn-only")
    cmd = [sys.executable, str(script_path)] + base_args

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=meta["timeout_seconds"],
            cwd=str(REPO_ROOT),
            encoding="utf-8",
            errors="replace",
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return 2, "", f"超时（>{meta['timeout_seconds']}s）"
    except OSError as e:
        return 2, "", f"OS 错误: {e}"


def _extract_file_path(line: str) -> tuple[str, str]:
    """从输出行中提取文件路径和描述文本。

    Args:
        line: 输出行文本

    Returns:
        tuple: (file_path_with_line, description)
    """
    m = _FILE_PATH_PATTERN.search(line)
    if m:
        path = m.group(1).replace("\\", "/")
        if m.group(2):
            path = f"{path}:{m.group(2)}"
        rest = line[: m.start()].strip() + " " + line[m.end() :].strip()
        return path, rest.strip().strip(":")
    return "", line


def _parse_jsonl_to_findings(
    jsonl_text: str,
    dimensions: list[Dimension],
    script_name: str,
) -> list[Finding]:
    """将 JSONL 文本解析为 Finding 列表。

    Args:
        jsonl_text: JSONL 格式文本（一行一个 JSON）
        dimensions: 脚本覆盖的维度列表
        script_name: 脚本文件名

    Returns:
        list[Finding]: 解析后的 Finding 列表
    """
    if not FINDING_AVAILABLE or not jsonl_text.strip():
        return []

    findings: list[Finding] = []
    for line in jsonl_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            dim_str = data.get("dimension", "")
            sev_str = data.get("severity", "MEDIUM")
            try:
                dim = Dimension(dim_str)
            except ValueError:
                dim = dimensions[0]
            try:
                sev = Severity(sev_str)
            except ValueError:
                sev = Severity.MEDIUM
            target = data.get("target", {})
            f = Finding(
                dimension=dim,
                severity=sev,
                category=data.get("category", f"{dim.label} — {script_name}"),
                target_file=target.get("file_path", "") if isinstance(target, dict) else str(target),
                description=data.get("description", "")[:500],
                evidence=data.get("evidence", line)[:500],
                blast_radius=BlastRadius.MODULE,
                remediation_action=RemediationAction.FIX,
                remediation_priority=data.get("remediation", {}).get("priority", "P2")
                if isinstance(data.get("remediation"), dict)
                else "P2",
                finding_id=data.get("finding_id"),
                timestamp=data.get("timestamp"),
            )
            findings.append(f)
        except (json.JSONDecodeError, KeyError, ValueError):
            continue
    return findings


def parse_script_output_to_findings(
    script_name: str,
    dimensions: list[Dimension],
    stdout: str,
    exit_code: int,
    is_warn_only: bool = False,
) -> list[Finding]:
    """将脚本 stdout 解析为结构化 Finding 列表。

    按行扫描 stdout，跳过统计摘要行，将每行违规信息转为 Finding 对象。
    严重度优先从 [P0]~[P3] 标签提取，其次从关键词推断。

    Args:
        script_name: 脚本文件名（如 'validate_architecture.py'）
        dimensions: 脚本覆盖的维度列表（取首个作为 Finding 维度）
        stdout: 脚本标准输出文本
        exit_code: 脚本退出码（0=通过 / 1=有发现 / 2=异常）
        is_warn_only: True 时脚本以 --warn-only 模式运行

    Returns:
        list[Finding]: 解析后的 Finding 列表
    """
    if not FINDING_AVAILABLE:
        return []

    findings: list[Finding] = []
    dimension = dimensions[0]

    if exit_code == 0 and not is_warn_only:
        return findings

    if exit_code == 2:
        f = Finding(
            dimension=dimension,
            severity=Severity.CRITICAL,
            category=f"{dimension.label} — 脚本异常",
            target_file=script_name,
            description=f"脚本执行异常（exit={exit_code}）",
            evidence=stdout[:500] if stdout else "无输出",
            blast_radius=BlastRadius.MODULE,
            remediation_action=RemediationAction.INVESTIGATE,
            remediation_priority="P0",
        )
        findings.append(f)
        return findings

    if is_warn_only and exit_code == 0 and not stdout.strip():
        return findings

    for line in stdout.split("\n"):
        line = line.strip()
        if not line:
            continue
        if _is_skip_line(line):
            continue

        tag_match = SEVERITY_TAG_PATTERN.match(line)
        if tag_match:
            severity = _P_TO_SEVERITY[tag_match.group(1)]
            line = line[tag_match.end() :].strip()
        elif _has_error_indicator(line):
            severity = Severity.MEDIUM
        else:
            continue

        file_path, description = _extract_file_path(line)

        f = Finding(
            dimension=dimension,
            severity=severity,
            category=f"{dimension.label} — {script_name.replace('.py', '')}",
            target_file=file_path or script_name,
            description=description[:500],
            evidence=line[:500],
            blast_radius=BlastRadius.MODULE,
            remediation_action=RemediationAction.FIX,
            remediation_priority="P2",
        )
        findings.append(f)

    return findings


def _run_env_check() -> None:
    """_run_env_check implementation."""
    env_check_path = SCRIPTS_DIR / "env_check.py"
    if not env_check_path.exists():
        return

    result = subprocess.run(
        [sys.executable, str(env_check_path), "--json"],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        cwd=str(REPO_ROOT),
    )
    if result.returncode == 0:
        return

    print("\n[GATE-ENV] ⚠️  环境未就绪，尝试自动安装依赖...", file=sys.stderr)
    result2 = subprocess.run(
        [sys.executable, str(env_check_path), "--install"],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        cwd=str(REPO_ROOT),
    )
    if result2.returncode == 0:
        print("[GATE-ENV] ✅ 安装完成，继续扫描\n", file=sys.stderr)
    else:
        print("[GATE-ENV] ❌ 环境安装失败", file=sys.stderr)
        print(result2.stdout[-500:] if result2.stdout else "", file=sys.stderr)
        print(result2.stderr[-500:] if result2.stderr else "", file=sys.stderr)
        print("请手动运行: python scripts/governance/env_check.py --install", file=sys.stderr)
        sys.exit(EXIT_FINDINGS)


def _topological_sort_dimensions(dimensions: list[Dimension]) -> list[Dimension]:
    """按 §5.3 三条依赖链对维度进行拓扑排序。

    链 A: D1 → D3 → D5 → D8（串行）
    链 B: D2 → D4 → D11 → D9 → D12（串行）
    链 C: D6 → D7 → D10（串行）
    三条链之间可并行（交错排列）。

    Args:
        dimensions: 要排序的维度列表

    Returns:
        list[Dimension]: 拓扑排序后的维度列表
    """
    dim_values = {d.value for d in dimensions}
    chain_order: list[str] = []

    for chain_name in ("chain_a", "chain_b", "chain_c"):
        chain = DEPENDENCY_CHAINS[chain_name]
        chain_dims = [d for d in chain if d in dim_values]
        if chain_dims:
            chain_order.extend(chain_dims)

    remaining = sorted(dim_values - set(chain_order))
    chain_order.extend(remaining)

    result: list[Dimension] = []
    for dv in chain_order:
        for d in dimensions:
            if d.value == dv:
                result.append(d)
                break
    return result


def _check_script_encoding(script_name: str) -> bool:
    """检查脚本是否符合 §5.5 编码铁律。

    验证脚本包含 UTF-8 stdout 强制声明。

    Args:
        script_name: 脚本文件名

    Returns:
        bool: True 表示编码铁律符合
    """
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        return False
    try:
        content = script_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    if "ensure_utf8_stdout" in content:
        return True
    if "sys.stdout.reconfigure(encoding='utf-8')" in content:
        return True
    if 'sys.stdout.reconfigure(encoding="utf-8")' in content:
        return True
    return False


def _append_sla_metrics(
    scan_type: str,
    total_findings: int,
    critical_count: int,
    high_count: int,
    scan_duration_s: float,
    exit_code: int,
) -> None:
    """追加 SLA 指标行到 sla_metrics.jsonl（§8.4）。

    Args:
        scan_type: 扫描类型（full / incremental / dimension）
        total_findings: Finding 总数
        critical_count: CRITICAL 数
        high_count: HIGH 数
        scan_duration_s: 扫描耗时（秒）
        exit_code: run_all.py 退出码
    """
    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "scan_type": scan_type,
        "total_findings": total_findings,
        "critical_count": critical_count,
        "high_count": high_count,
        "scan_duration_s": round(scan_duration_s, 1),
        "exit_code": exit_code,
    }
    SLA_METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SLA_METRICS_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _try_jsonl_run(script_name: str, meta: dict, warn_only: bool = False) -> list[Finding] | None:
    """尝试以 --jsonl 模式运行脚本，返回 Finding 列表。

    若脚本不支持 --jsonl（exit 2），返回 None 触发 fallback。
    """
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        return None
    cmd = [sys.executable, str(script_path)] + list(meta.get("args", []))
    if warn_only:
        cmd.append("--warn-only")
    cmd.append("--jsonl")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=meta["timeout_seconds"],
            cwd=str(REPO_ROOT),
            encoding="utf-8",
            errors="replace",
        )
    except (subprocess.TimeoutExpired, OSError):
        return None

    if result.returncode == 2:
        return None

    return _parse_jsonl_to_findings(result.stdout, meta["dimensions"], script_name)


def _execute_one_script(
    script_name: str,
    meta: dict,
    warn_only: bool = False,
) -> dict:
    """Run a single script and return results dict (thread-safe for ThreadPoolExecutor)."""
    enc_violation = None
    if not _check_script_encoding(script_name):
        enc_violation = script_name

    exit_code, stdout, stderr = run_script(script_name, meta, warn_only=warn_only)

    findings: list[Finding] = []
    if FINDING_AVAILABLE:
        jl_result = _try_jsonl_run(script_name, meta, warn_only)
        if jl_result is not None:
            findings = jl_result
        else:
            findings = parse_script_output_to_findings(
                script_name,
                meta["dimensions"],
                stdout,
                exit_code,
                warn_only,
            )

    return {
        "script_name": script_name,
        "exit_code": exit_code,
        "findings": findings,
        "is_failed": exit_code == 2,
        "enc_violation": enc_violation,
    }


def run_all_dimensions(
    dimensions_to_run: list[Dimension],
    output_path: str,
    verbose: bool = False,
    warn_only: bool = False,
    registry_override: dict[str, Any] | None = None,
) -> tuple[FindingCollection, dict]:
    """Run all dimension scans in parallel via BulkheadExecutorV2 (fallback: ThreadPoolExecutor)."""
    registry = registry_override if registry_override is not None else _get_registry()
    if FINDING_AVAILABLE:
        collection = FindingCollection()
    else:
        collection = None

    seen_scripts: set[str] = set()
    script_tasks: list[tuple[str, dict]] = []

    for dim in dimensions_to_run:
        for name, meta in registry.items():
            if dim in meta["dimensions"] and name not in seen_scripts and name not in _SKIP_INTERNAL:
                seen_scripts.add(name)
                script_tasks.append((name, meta))

    if not script_tasks:
        return collection, {"total_scripts": 0, "total_failed": 0, "total_unique_scripts": 0, "encoding_violations": []}

    encoding_violations: list[str] = []
    total_failed = 0

    if _USE_BULKHEAD:
        try:
            from meta._concurrency import BulkheadExecutorV2

            bulkhead = BulkheadExecutorV2()

            def _make_executor(wo: bool):
                def _exec(sn: str, m: dict) -> dict:
                    return _execute_one_script(sn, m, wo)

                return _exec

            bulkhead_tasks = [(name, meta, _make_executor(warn_only), None) for name, meta in script_tasks]

            print(f"\n  并行执行 {len(script_tasks)} 个唯一脚本 (BulkheadExecutorV2 四池隔离) ...", file=sys.stderr)

            def _on_complete(result: dict) -> None:
                if result.get("enc_violation"):
                    encoding_violations.append(result["enc_violation"])
                    print(
                        f"\n    [ENC] {result['enc_violation']}: 编码铁律违规 — 缺少 UTF-8 stdout 声明", file=sys.stderr
                    )

            dispatch_result = bulkhead.dispatch_with_locks(bulkhead_tasks, on_complete=_on_complete)

            for r in dispatch_result.get("results", []):
                if r.get("is_failed"):
                    total_failed += 1
                if FINDING_AVAILABLE and collection is not None and r.get("findings"):
                    collection.extend(r["findings"])

            for s in dispatch_result.get("skipped", []):
                total_failed += 1
                print(f"    [SKIP] {s['script_name']}: {s['reason']}", file=sys.stderr)

            print(
                f"    {len(script_tasks)}/{len(script_tasks)} 完成 (pools: {dispatch_result.get('pools', {})})",
                file=sys.stderr,
            )

        except ImportError:
            print("  [WARN] BulkheadExecutorV2 不可用, 回退 ThreadPoolExecutor", file=sys.stderr)
            total_failed = _run_with_threadpool(script_tasks, collection, encoding_violations, warn_only)
    else:
        total_failed = _run_with_threadpool(script_tasks, collection, encoding_violations, warn_only)

    for dim in dimensions_to_run:
        dim_count = sum(1 for name, meta in script_tasks if dim in meta["dimensions"])
        print(f"  [{dim.value}] {dim.label}: {dim_count} 脚本", file=sys.stderr)

    overall = {
        "total_scripts": len(script_tasks),
        "total_failed": total_failed,
        "total_unique_scripts": len(script_tasks),
        "encoding_violations": encoding_violations,
    }
    return collection, overall


def _run_with_threadpool(
    script_tasks: list[tuple[str, dict]],
    collection: Any,
    encoding_violations: list[str],
    warn_only: bool,
) -> int:
    """Fallback: ThreadPoolExecutor 并行执行。"""
    total_failed = 0
    completed = 0

    with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
        futures = {executor.submit(_execute_one_script, name, meta, warn_only): name for name, meta in script_tasks}
        for future in as_completed(futures):
            result = future.result()
            completed += 1

            if result["enc_violation"]:
                encoding_violations.append(result["enc_violation"])
                print(f"\n    [ENC] {result['enc_violation']}: 编码铁律违规 — 缺少 UTF-8 stdout 声明", file=sys.stderr)

            if result["is_failed"]:
                total_failed += 1

            if FINDING_AVAILABLE and collection is not None and result["findings"]:
                collection.extend(result["findings"])

            if completed % 20 == 0 or completed == len(script_tasks):
                print(f"    {completed}/{len(script_tasks)} 完成", file=sys.stderr)

    return total_failed


def _get_changed_files(diff_ref: str = "HEAD~1") -> frozenset[str]:
    """_get_changed_files implementation."""
    result = subprocess.run(
        ["git", "diff", "--name-only", diff_ref],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO_ROOT),
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--cached"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(REPO_ROOT),
            encoding="utf-8",
            errors="replace",
        )
    return frozenset(line.strip().replace("\\", "/") for line in result.stdout.split("\n") if line.strip())


_FILE_DIMENSION_MAP: tuple[tuple[str, str], ...] = (
    ("docs/01_policies_and_standards/", "D3"),
    ("docs/03_modules/", "D5"),
    ("docs/02_enterprise_architecture/", "D5"),
    ("docs/", "D2"),
    ("scripts/governance/d1_structure/", "D1"),
    ("scripts/governance/d2_links/", "D2"),
    ("scripts/governance/d3_metadata/", "D3"),
    ("scripts/governance/d4_paths/", "D4"),
    ("scripts/governance/d5_architecture/", "D5"),
    ("scripts/governance/d6_security/", "D6"),
    ("scripts/governance/d7_code/", "D7"),
    ("scripts/governance/d8_tests/", "D8"),
    ("scripts/governance/d9_vcs/", "D9"),
    ("scripts/governance/d10_ci_cd/", "D10"),
    ("scripts/governance/d11_infrastructure/", "D11"),
    ("scripts/governance/d12_feedback/", "D12"),
    ("scripts/governance/", "D1"),
    ("src/zephyr/infrastructure_runtime_integration/", "D11"),
    ("src/zephyr/", "D6"),
    ("src/", "D7"),
    ("config/", "D4"),
    ("data/", "D4"),
)


def _map_files_to_dimensions(changed_files: frozenset[str]) -> frozenset[str]:
    """_map_files_to_dimensions implementation."""
    dims: set[str] = set()
    for f in changed_files:
        f = f.replace("\\", "/")
        for prefix, dim in _FILE_DIMENSION_MAP:
            if f.startswith(prefix):
                dims.add(dim)
                break
        else:
            dims.add("D12")
    return frozenset(dims)


def _derive_tags(script_name: str, dimensions: list[Dimension], priority: str) -> frozenset[str]:
    """_derive_tags implementation."""
    tags: set[str] = set()
    for dim in dimensions:
        tags.update(_DIMENSION_TAGS.get(dim.value, []))
    for prefix, prefix_tags in _PREFIX_TAGS:
        sn_lower = script_name.lower()
        if sn_lower.startswith(prefix) or f"/{prefix}" in sn_lower:
            tags.update(prefix_tags)
    if priority == "P0":
        tags.add("Critical")
    return frozenset(tags)


def _filter_registry(
    registry: dict[str, Any],
    required_tags: frozenset[str] | None = None,
    depth: str | None = None,
) -> dict[str, Any]:
    """_filter_registry implementation."""
    filtered: dict[str, Any] = {}
    for name, meta in registry.items():
        if name in _SKIP_INTERNAL:
            continue
        manifest_tags = meta.get("tags") or []
        if manifest_tags:
            script_tags = frozenset(manifest_tags)
        else:
            script_tags = _derive_tags(name, meta["dimensions"], meta["priority"])
        if required_tags and not (required_tags <= script_tags):
            continue
        if depth == "quick":
            if "Quick" not in script_tags or meta["timeout_seconds"] > 30:
                continue
        filtered[name] = meta
    return filtered


def main() -> None:
    """入口——解析命令行参数并编排审计扫描执行。

    支持全维度/指定维度扫描、脚本列表、干跑预览等模式。
    退出码遵循 POSIX 约定：0=通过 / 1=有发现 / 2=异常 / 3=配置错误。
    """
    parser = argparse.ArgumentParser(description="ZephyrAlpha 脚本系统统一入口 — 一键运行全维度或指定维度审计扫描")
    parser.add_argument(
        "--dimensions",
        "-d",
        nargs="+",
        choices=[d.value for d in Dimension],
        help="指定扫描维度（可多个），不指定则全维度",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=str(DEFAULT_OUTPUT),
        help=f"输出 JSONL 文件路径（默认: {DEFAULT_OUTPUT}）",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="列出所有注册脚本及其维度映射",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="预览模式：打印将要执行的脚本清单，不实际运行",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="详细输出每个脚本的执行结果",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="警告模式：传递 --warn-only 给所有子脚本，发现不阻塞（exit 0）",
    )
    parser.add_argument(
        "--diff-ref",
        default="",
        help="增量模式：仅扫描与 git diff <ref> 变更相关的脚本（如 HEAD~1 或 origin/main...HEAD）",
    )
    parser.add_argument(
        "--tags",
        "-t",
        nargs="*",
        help="按标签过滤脚本（如 'Security Quick' 或 'Security,Quick'），AND 语义",
    )
    parser.add_argument(
        "--depth",
        "-dp",
        choices=["quick", "full", "deep"],
        default="full",
        help="扫描深度: quick（快速<30s）/ full（标准，默认）/ deep（含LLM分析占位）",
    )
    args = parser.parse_args()

    if args.list:
        list_registered_scripts()
        return

    if not FINDING_AVAILABLE:
        print("⚠ Finding Schema 不可用（src/zephyr/script_system/finding.py 未找到或导入失败）", file=sys.stderr)
        print("  run_all.py 仍可执行脚本，但不会生成结构化 Finding 输出", file=sys.stderr)

    dimensions_to_run = [Dimension(d) for d in args.dimensions] if args.dimensions else list(Dimension)

    required_tags: frozenset[str] = frozenset()
    if args.tags is not None:
        resolved: set[str] = set()
        for raw_group in args.tags:
            for tag in raw_group.split(","):
                tag = tag.strip()
                if tag not in _VALID_TAGS:
                    print(f"错误: 非法标签 '{tag}'。合法值: {sorted(_VALID_TAGS)}", file=sys.stderr)
                    sys.exit(3)
                resolved.add(tag)
        required_tags = frozenset(resolved)

    filtered_registry = _filter_registry(_get_registry(), required_tags=required_tags, depth=args.depth)

    if args.diff_ref:
        changed = _get_changed_files(args.diff_ref)
        if not changed:
            print(f"\n[增量模式] git diff {args.diff_ref} 无变更，跳过扫描", file=sys.stderr)
            return
        relevant_dims = _map_files_to_dimensions(changed)
        dimensions_to_run = [d for d in dimensions_to_run if d.value in relevant_dims]
        print(
            f"\n[增量模式] {len(changed)} 变更文件 → {len(relevant_dims)} 相关维度: {', '.join(sorted(relevant_dims))}",
            file=sys.stderr,
        )

    if args.dry_run:
        registry = filtered_registry
        unique_scripts: set[str] = set()
        dimensions_sorted = _topological_sort_dimensions(dimensions_to_run)
        print(f"\n[DRY RUN] 将扫描 {len(dimensions_sorted)} 个维度（拓扑排序后）：", file=sys.stderr)
        print(
            f"  链A (D1→D3→D5→D8): {[d for d in ('D1', 'D3', 'D5', 'D8') if any(dv.value == d for dv in dimensions_sorted)]}",
            file=sys.stderr,
        )
        print(
            f"  链B (D2→D4→D11→D9→D12): {[d for d in ('D2', 'D4', 'D11', 'D9', 'D12') if any(dv.value == d for dv in dimensions_sorted)]}",
            file=sys.stderr,
        )
        print(
            f"  链C (D6→D7→D10): {[d for d in ('D6', 'D7', 'D10') if any(dv.value == d for dv in dimensions_sorted)]}",
            file=sys.stderr,
        )
        for dim in dimensions_sorted:
            scripts = [name for name, meta in registry.items() if dim in meta["dimensions"]]
            unique_scripts.update(scripts)
            print(f"  {dim.value} ({dim.label}): {len(scripts)} 个脚本 → {', '.join(scripts)}", file=sys.stderr)
        print(f"\n  去重后实际执行: {len(unique_scripts)} 个唯一脚本", file=sys.stderr)

        encoding_ok = 0
        encoding_bad = 0
        for sn in sorted(unique_scripts):
            if _check_script_encoding(sn):
                encoding_ok += 1
            else:
                encoding_bad += 1
                print(f"  ⚠ {sn}: 编码铁律违规（缺少 UTF-8 stdout 声明）", file=sys.stderr)
        print(f"\n  编码铁律: {encoding_ok} ✅ / {encoding_bad} ❌ (共 {len(unique_scripts)} 脚本)", file=sys.stderr)
        return

    dimensions_sorted = _topological_sort_dimensions(dimensions_to_run)
    date_str = datetime.now(UTC).strftime("%Y%m%d")

    scan_type = "full" if len(dimensions_sorted) >= 12 else "dimension"

    output_path = Path(args.output)
    if args.output == str(DEFAULT_OUTPUT):
        output_path = Path(args.output).parent / f"findings-full-{date_str}.jsonl"

    print(f"\n{'=' * 60}", file=sys.stderr)
    print("  ZephyrAlpha 脚本系统 — 全维度扫描", file=sys.stderr)
    mode_tag = " [warn-only]" if args.warn_only else ""
    print(f"  时间: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}{mode_tag}", file=sys.stderr)
    print(
        f"  维度: {len(dimensions_sorted)} 个（拓扑排序: "
        f"A={[d for d in ('D1', 'D3', 'D5', 'D8') if any(dv.value == d for dv in dimensions_sorted)]}, "
        f"B={[d for d in ('D2', 'D4', 'D11', 'D9', 'D12') if any(dv.value == d for dv in dimensions_sorted)]}, "
        f"C={[d for d in ('D6', 'D7', 'D10') if any(dv.value == d for dv in dimensions_sorted)]})",
        file=sys.stderr,
    )
    print(f"  输出: {output_path}", file=sys.stderr)
    print(f"  全局硬超时: {GLOBAL_HARD_TIMEOUT_SECONDS}s", file=sys.stderr)
    print(f"{'=' * 60}\n", file=sys.stderr)

    start_time = time.time()
    global_timeout_reached = False
    checkpoint_path = Path(args.output).parent / f"_scan_checkpoint_{date_str}.json"

    collection, overall = run_all_dimensions(
        dimensions_sorted,
        str(output_path),
        verbose=args.verbose,
        warn_only=args.warn_only,
        registry_override=filtered_registry,
    )

    elapsed = time.time() - start_time
    if elapsed >= GLOBAL_HARD_TIMEOUT_SECONDS:
        global_timeout_reached = True
        checkpoint_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "global_timeout_reached": True,
            "elapsed_s": round(elapsed, 1),
            "completed_dimensions": [d.value for d in dimensions_sorted],
            "total_unique_scripts": overall["total_unique_scripts"],
        }
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        with open(checkpoint_path, "w", encoding="utf-8") as cf:
            json.dump(checkpoint_data, cf, ensure_ascii=False, indent=2)
        print(f"\n⚠ 全局硬超时 ({GLOBAL_HARD_TIMEOUT_SECONDS}s) — checkpoint: {checkpoint_path}", file=sys.stderr)

    total_findings = collection.total if (FINDING_AVAILABLE and collection is not None) else 0

    if FINDING_AVAILABLE and collection is not None:
        severity_summary = collection.summary()
        sev_counts = severity_summary.get("by_severity", {})
    else:
        sev_counts = {}

    critical_count = sev_counts.get("CRITICAL", 0)
    high_count = sev_counts.get("HIGH", 0)

    final_exit_code = 0
    if overall["total_failed"] > 0:
        final_exit_code = 2 if global_timeout_reached else 2
    elif total_findings > 0:
        final_exit_code = 1 if not args.warn_only else 0

    _append_sla_metrics(
        scan_type=scan_type,
        total_findings=total_findings,
        critical_count=critical_count,
        high_count=high_count,
        scan_duration_s=elapsed,
        exit_code=final_exit_code,
    )

    print(f"\n{'─' * 60}", file=sys.stderr)
    print(f"  总耗时: {elapsed:.1f}s", file=sys.stderr)
    print(f"  维度完成: {len(dimensions_sorted)}/{len(dimensions_sorted)}", file=sys.stderr)
    print(f"  唯一脚本: {overall['total_unique_scripts']}（{overall['total_failed']} 异常）", file=sys.stderr)
    enc_violations = overall.get("encoding_violations", [])
    if enc_violations:
        print(f"  编码铁律违规: {len(enc_violations)} 脚本 → {', '.join(enc_violations)}", file=sys.stderr)
    print(f"  Finding 总计: {total_findings}", file=sys.stderr)
    if global_timeout_reached:
        print("  ⚠ 全局硬超时触发", file=sys.stderr)
    print(f"{'─' * 60}", file=sys.stderr)

    if FINDING_AVAILABLE and collection is not None and total_findings > 0:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        collection.write_jsonl(str(output_path))
        print(f"\n  结构化输出已写入: {output_path}", file=sys.stderr)

        if severity_summary:
            print(f"  严重度分布: {json.dumps(sev_counts, ensure_ascii=False)}", file=sys.stderr)

        criticals = collection.critical_only()
        if criticals.total > 0:
            print(f"\n  ⚠ {criticals.total} 个 CRITICAL Finding:", file=sys.stderr)
            for f in criticals:
                print(f"    [{f.finding_id}] {f.target_file}: {f.description[:120]}", file=sys.stderr)

    if overall["total_failed"] > 0:
        print(f"\n⚠ {overall['total_failed']} 个脚本执行异常，请检查上方输出", file=sys.stderr)

    if BRIDGE_AVAILABLE and FINDING_AVAILABLE and collection is not None and total_findings > 0:
        audit_findings: list[AuditFinding] = []
        for f in collection:
            audit_findings.append(
                AuditFinding(
                    finding_id=f.finding_id,
                    dimension=_DIMENSION_TO_AUDIT_LABEL.get(f.dimension.value, "governance"),
                    severity=_SEVERITY_TO_AUDIT.get(f.severity, "medium"),
                    description=f.description,
                    source_script="run_all.py",
                    source_file=f.target_file,
                    suggested_fix=f.recommendation,
                )
            )
        bridge_result = bridge_findings_to_tasks(
            audit_findings,
            db_path=DB_PATH,
            dry_run=args.dry_run,
        )
        print(
            f"\n  [CT-ORC-SCRIPT-001] 桥接完成: {bridge_result.tasks_created}/{len(audit_findings)} tasks创建",
            file=sys.stderr,
        )
        if bridge_result.errors:
            print(f"    ⚠ 失败: {len(bridge_result.errors)}", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(final_exit_code)


if __name__ == "__main__":
    main()
