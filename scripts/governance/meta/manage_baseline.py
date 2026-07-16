# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/manage_baseline.py | §
# [MODULE] scripts.governance.meta.manage_baseline
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.meta.__init__
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
# [TTL] permanent
"""
manage_baseline.py — Finding 基线快照管理

对标 B18（Baseline Snapshot 对比）+ OWASP ASVS v5 snapshot-based verification。
保存/加载/对比 Finding 基线快照，将当前扫描结果与上次 approved baseline 对比，
分类每个 Finding 为 NEW / RESOLVED / PERSISTENT。

Usage:
    python scripts/governance/meta/manage_baseline.py --save findings.jsonl
    python scripts/governance/meta/manage_baseline.py --compare findings.jsonl --baseline baseline.jsonl
    python scripts/governance/meta/manage_baseline.py --approve findings.jsonl
    python scripts/governance/meta/manage_baseline.py --status
"""

from __future__ import annotations
from _shared.constants import REPO_ROOT
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT

__manifest__ = """
args: []
description: >
  Finding 基线快照管理——保存/加载/对比 Finding 基线快照，
  分类每个 Finding 为 NEW / RESOLVED / PERSISTENT。
dimensions:
- D1
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

_REPO_ROOT = REPO_ROOT
_BASELINE_DIR = _REPO_ROOT / "scripts" / "governance" / "meta" / "baselines"
_CURRENT_BASELINE = _BASELINE_DIR / "current_baseline.jsonl"
_BASELINE_META = _BASELINE_DIR / "baseline_meta.json"

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def _load_findings(path: str | Path) -> list[dict]:
    """_load_findings implementation."""
    findings: list[dict] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                findings.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return findings


def _finding_key(f: dict) -> str:
    """_finding_key implementation."""
    raw = f"{f.get('dimension', '')}|{f.get('target', {}).get('file_path', '')}|{f.get('description', '')}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _build_index(findings: list[dict]) -> dict[str, dict]:
    """_build_index implementation."""
    return {_finding_key(f): f for f in findings}


def _atomic_write(path: Path, content: str) -> None:
    """原子写入：委托共享桥 atomic_write_safe（治本 ARCH-036 P1-1 收敛 tmp+replace 样板）。"""
    atomic_write_safe(path, content)


def _serialize_jsonl(findings: list[dict]) -> str:
    """将 findings 列表序列化为 JSONL 字符串（每行一个 JSON 对象）。"""
    return "".join(json.dumps(f, ensure_ascii=False) + "\n" for f in findings)


def write_jsonl_baseline(
    findings: list[dict],
    *,
    baseline_dir: Path,
    versioned_prefix: str,
    current_path: Path,
    meta_path: Path | None = None,
    source_label: str,
    label: str,
    ts_str: str | None = None,
) -> dict:
    """写入 JSONL 基线快照（SSoT helper，供 manage_baseline + audit_registration 复用）。

    统一原子写入逻辑，消除 save_baseline 三份重复。写入：
      1. 版本化备份 ``{baseline_dir}/{versioned_prefix}-{ts}.jsonl``
      2. 当前指针 ``current_path``（覆盖，内容与版本化备份一致）
      3.（可选）meta ``meta_path``（JSON 对象）；None 跳过

    Args:
        findings: Finding 列表（dict，至少含 dimension/target/description）。
        baseline_dir: 基线目录（自动 mkdir）。
        versioned_prefix: 版本化文件前缀（如 ``"baseline"`` / ``"audit_registration"``）。
        current_path: 当前指针文件完整路径。
        meta_path: 可选 meta 文件路径；None 表示不写 meta（audit_registration 不需要）。
        source_label: meta.source 字段值。
        label: meta.label 字段值。
        ts_str: 可选时间戳；None 则自动生成 ``%Y%m%dT%H%M%SZ``。

    Returns:
        meta dict（saved_at / finding_count / source / label / file）。
    """
    baseline_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC)
    ts_str = ts_str or timestamp.strftime("%Y%m%dT%H%M%SZ")

    output_path = baseline_dir / f"{versioned_prefix}-{ts_str}.jsonl"
    jsonl_content = _serialize_jsonl(findings)
    _atomic_write(output_path, jsonl_content)
    _atomic_write(current_path, jsonl_content)

    try:
        file_rel = str(output_path.relative_to(_REPO_ROOT))
    except ValueError:
        file_rel = str(output_path)
    meta = {
        "saved_at": timestamp.isoformat(),
        "finding_count": len(findings),
        "source": source_label,
        "label": label,
        "file": file_rel,
    }
    if meta_path is not None:
        _atomic_write(meta_path, json.dumps(meta, ensure_ascii=False, indent=2))
    return meta


def save_baseline(source: str | Path, label: str = "") -> dict:
    """从文件加载 findings 并保存为基线快照（版本化备份 + 当前指针 + meta）。"""
    findings = _load_findings(source)
    ts_str = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return write_jsonl_baseline(
        findings,
        baseline_dir=_BASELINE_DIR,
        versioned_prefix="baseline",
        current_path=_CURRENT_BASELINE,
        meta_path=_BASELINE_META,
        source_label=str(source),
        label=label or f"baseline-{ts_str}",
        ts_str=ts_str,
    )


def compare_with_baseline(
    current_path: str | Path,
    baseline_path: str | Path | None = None,
) -> dict:
    """compare_with_baseline implementation."""
    baseline_path = Path(baseline_path) if baseline_path else _CURRENT_BASELINE
    if not Path(baseline_path).exists():
        return {"error": "baseline_not_found", "path": str(baseline_path)}

    current_findings = _load_findings(current_path)
    baseline_findings = _load_findings(baseline_path)

    current_index = _build_index(current_findings)
    baseline_index = _build_index(baseline_findings)

    new_keys = set(current_index.keys()) - set(baseline_index.keys())
    resolved_keys = set(baseline_index.keys()) - set(current_index.keys())
    persistent_keys = set(current_index.keys()) & set(baseline_index.keys())

    classified: list[dict] = []
    for key in new_keys:
        f = dict(current_index[key])
        f["baseline_status"] = "NEW"
        classified.append(f)
    for key in resolved_keys:
        f = dict(baseline_index[key])
        f["baseline_status"] = "RESOLVED"
        classified.append(f)
    for key in persistent_keys:
        f = dict(current_index[key])
        f["baseline_status"] = "PERSISTENT"
        classified.append(f)

    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "current_total": len(current_findings),
        "baseline_total": len(baseline_findings),
        "new_count": len(new_keys),
        "resolved_count": len(resolved_keys),
        "persistent_count": len(persistent_keys),
        "classified": classified,
    }


def approve_baseline(source: str | Path) -> dict:
    """approve_baseline implementation."""
    return save_baseline(source, label="approved")


def baseline_status() -> dict:
    """baseline_status implementation."""
    if not _BASELINE_META.exists():
        return {"has_baseline": False}
    with open(_BASELINE_META, encoding="utf-8") as f:
        meta = json.load(f)
    return {"has_baseline": True, "meta": meta}


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Finding 基线快照管理")
    parser.add_argument("--save", type=str, help="保存当前 Findings 为基线")
    parser.add_argument("--compare", type=str, help="对比当前 Findings 与基线")
    parser.add_argument("--baseline", type=str, help="指定基线文件路径")
    parser.add_argument("--approve", type=str, help="批准当前 Findings 为正式基线")
    parser.add_argument("--status", action="store_true", help="查看当前基线状态")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    args = parser.parse_args()

    if args.status:
        result = baseline_status()
    elif args.approve:
        result = approve_baseline(args.approve)
    elif args.save:
        result = save_baseline(args.save)
    elif args.compare:
        result = compare_with_baseline(args.compare, args.baseline)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("\n[BASELINE] 对比完成", file=sys.stderr)
            print(f"  当前: {result['current_total']}, 基线: {result['baseline_total']}", file=sys.stderr)
            print(f"  🆕 NEW: {result['new_count']}", file=sys.stderr)
            print(f"  ✅ RESOLVED: {result['resolved_count']}", file=sys.stderr)
            print(f"  🔄 PERSISTENT: {result['persistent_count']}", file=sys.stderr)
            for f in result.get("classified", [])[:20]:
                status_tag = f["baseline_status"]
                sev = f.get("severity", "?")
                target = f.get("target", {}).get("file_path", "?")
                desc = f.get("description", "")[:100]
                print(f"    [{status_tag}] [{sev}] {target}: {desc}")
        return
    else:
        parser.print_help()
        return

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
