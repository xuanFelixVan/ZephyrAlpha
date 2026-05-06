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
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

# AGENTS.md §6.7: UTF-8 输出强制声明（防止 Windows GBK 编码 crash）

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

from _shared.constants import MANIFEST_PATH, REPO_ROOT, SCRIPTS_DIR

DEFAULT_OUTPUT = SCRIPTS_DIR / "reports" / "findings.jsonl"

sys.path.insert(0, str(REPO_ROOT / "src"))
try:
    from zephyr.l01_infrastructure.script_system.finding import (
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

if FINDING_AVAILABLE:
    _P_TO_SEVERITY = {
        "P0": Severity.CRITICAL,
        "P1": Severity.HIGH,
        "P2": Severity.MEDIUM,
        "P3": Severity.LOW,
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
        sys.exit(1)

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

def run_all_dimensions(
    dimensions_to_run: list[Dimension],
    output_path: str,
    verbose: bool = False,
    warn_only: bool = False,
) -> tuple[FindingCollection, dict]:
    """运行所有指定维度的审计扫描（每个脚本仅执行一次，去重）。

    按维度组织显示，但相同脚本只跑一次——多维度映射的脚本
    不重复执行，结果分发给各维度的 Finding 统计。

    Args:
        dimensions_to_run: 要扫描的维度列表
        output_path: JSONL 输出路径
        verbose: True 时打印详细输出
        warn_only: True 时传递 --warn-only 给所有子脚本

    Returns:
        tuple: (FindingCollection, 统计 dict)
    """
    registry = _get_registry()
    if FINDING_AVAILABLE:
        collection = FindingCollection()
    else:
        collection = None

    seen_scripts: set[str] = set()

    total_scripts = 0
    total_failed = 0

    for dim in dimensions_to_run:
        print(f"[{dim.value}] {dim.label} ...", end=" ", flush=True, file=sys.stderr)

        scripts_for_dim = {name: meta for name, meta in registry.items() if dim in meta["dimensions"]}

        dim_scripts_run = 0
        dim_scripts_failed = 0
        dim_findings = 0

        for script_name, meta in scripts_for_dim.items():
            if script_name in seen_scripts:
                continue
            seen_scripts.add(script_name)
            dim_scripts_run += 1
            total_scripts += 1

            exit_code, stdout, stderr = run_script(script_name, meta, warn_only=warn_only)

            if exit_code == 2:
                dim_scripts_failed += 1
                total_failed += 1

            if verbose and stdout:
                print(f"\n    [{script_name}]: {stdout[:200]}", file=sys.stderr)

            if FINDING_AVAILABLE and collection is not None:
                jl_result = _try_jsonl_run(script_name, meta, warn_only)
                if jl_result is not None:
                    collection.extend(jl_result)
                    dim_findings += len(jl_result)
                else:
                    parsed = parse_script_output_to_findings(
                        script_name,
                        meta["dimensions"],
                        stdout,
                        exit_code,
                        warn_only,
                    )
                    collection.extend(parsed)
                    dim_findings += len(parsed)
            else:
                if exit_code not in (0, 2):
                    dim_findings += 1

        failed_note = f" ({dim_scripts_failed} 异常)" if dim_scripts_failed else ""
        print(f"{dim_scripts_run} 脚本{failed_note}, {dim_findings} Finding", file=sys.stderr)

    overall = {
        "total_scripts": total_scripts,
        "total_failed": total_failed,
        "total_unique_scripts": len(seen_scripts),
    }
    return collection, overall


def _get_changed_files(diff_ref: str = "HEAD~1") -> frozenset[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", diff_ref],
        capture_output=True, text=True, timeout=30,
        cwd=str(REPO_ROOT), encoding="utf-8", errors="replace",
    )
    if result.returncode != 0:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--cached"],
            capture_output=True, text=True, timeout=30,
            cwd=str(REPO_ROOT), encoding="utf-8", errors="replace",
        )
    return frozenset(
        line.strip().replace("\\", "/")
        for line in result.stdout.split("\n") if line.strip()
    )


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
    ("src/zephyr/l01_infrastructure/", "D11"),
    ("src/zephyr/", "D6"),
    ("src/", "D7"),
    ("config/", "D4"),
    ("data/", "D4"),
)


def _map_files_to_dimensions(changed_files: frozenset[str]) -> frozenset[str]:
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
    args = parser.parse_args()

    if args.list:
        list_registered_scripts()
        return

    if not FINDING_AVAILABLE:
        print("⚠ Finding Schema 不可用（src/zephyr/script_system/finding.py 未找到或导入失败）", file=sys.stderr)
        print("  run_all.py 仍可执行脚本，但不会生成结构化 Finding 输出", file=sys.stderr)

    dimensions_to_run = [Dimension(d) for d in args.dimensions] if args.dimensions else list(Dimension)

    if args.diff_ref:
        changed = _get_changed_files(args.diff_ref)
        if not changed:
            print(f"\n[增量模式] git diff {args.diff_ref} 无变更，跳过扫描", file=sys.stderr)
            return
        relevant_dims = _map_files_to_dimensions(changed)
        dimensions_to_run = [d for d in dimensions_to_run if d.value in relevant_dims]
        print(f"\n[增量模式] {len(changed)} 变更文件 → {len(relevant_dims)} 相关维度: "
              f"{', '.join(sorted(relevant_dims))}", file=sys.stderr)

    if args.dry_run:
        registry = _get_registry()
        unique_scripts: set[str] = set()
        print(f"\n[DRY RUN] 将扫描 {len(dimensions_to_run)} 个维度：", file=sys.stderr)
        for dim in dimensions_to_run:
            scripts = [name for name, meta in registry.items() if dim in meta["dimensions"]]
            unique_scripts.update(scripts)
            print(f"  {dim.value} ({dim.label}): {len(scripts)} 个脚本 → {', '.join(scripts)}", file=sys.stderr)
        print(f"\n  去重后实际执行: {len(unique_scripts)} 个唯一脚本", file=sys.stderr)
        return

    print(f"\n{'=' * 60}", file=sys.stderr)
    print("  ZephyrAlpha 脚本系统 — 全维度扫描", file=sys.stderr)
    mode_tag = " [warn-only]" if args.warn_only else ""
    print(f"  时间: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}{mode_tag}", file=sys.stderr)
    print(f"  维度: {len(dimensions_to_run)} 个", file=sys.stderr)
    print(f"  输出: {args.output}", file=sys.stderr)
    print(f"{'=' * 60}\n", file=sys.stderr)

    start_time = time.time()
    collection, overall = run_all_dimensions(
        dimensions_to_run,
        args.output,
        verbose=args.verbose,
        warn_only=args.warn_only,
    )

    elapsed = time.time() - start_time
    total_findings = collection.total if (FINDING_AVAILABLE and collection is not None) else 0

    print(f"\n{'─' * 60}", file=sys.stderr)
    print(f"  总耗时: {elapsed:.1f}s", file=sys.stderr)
    print(f"  维度完成: {len(dimensions_to_run)}/{len(dimensions_to_run)}", file=sys.stderr)
    print(f"  唯一脚本: {overall['total_unique_scripts']}（{overall['total_failed']} 异常）", file=sys.stderr)
    print(f"  Finding 总计: {total_findings}", file=sys.stderr)
    print(f"{'─' * 60}", file=sys.stderr)

    if FINDING_AVAILABLE and collection is not None and total_findings > 0:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        collection.write_jsonl(str(output_path))
        print(f"\n  结构化输出已写入: {output_path}", file=sys.stderr)

        severity_summary = collection.summary()["by_severity"]
        if severity_summary:
            print(f"  严重度分布: {json.dumps(severity_summary, ensure_ascii=False)}", file=sys.stderr)

        criticals = collection.critical_only()
        if criticals.total > 0:
            print(f"\n  ⚠ {criticals.total} 个 CRITICAL Finding:", file=sys.stderr)
            for f in criticals:
                print(f"    [{f.finding_id}] {f.target_file}: {f.description[:120]}", file=sys.stderr)

    if overall["total_failed"] > 0:
        print(f"\n⚠ {overall['total_failed']} 个脚本执行异常，请检查上方输出", file=sys.stderr)

    if args.warn_only:
        sys.exit(0)
    sys.exit(1 if total_findings > 0 else 0)

if __name__ == "__main__":
    main()
