"""validate_false_negatives.py — 假阴性检测引擎 (Fitness Functions)

对标 B17（False Negative 检测）+ 《Building Evolutionary Architectures》Fitness Functions
+ OWASP ASVS v5 regression testing。

维护一个"已知有缺陷的测试用例库"（golden set），定期验证脚本系统
能否检测出这些已知缺陷。如果已知缺陷未被检出 → 假阴性 → Error Budget 消耗。

Usage:
    python scripts/governance/meta/validate_false_negatives.py
    python scripts/governance/meta/validate_false_negatives.py --list-cases
    python scripts/governance/meta/validate_false_negatives.py --add-case cases/bad_frontmatter.md
    python scripts/governance/meta/validate_false_negatives.py --dimension D3
    python scripts/governance/meta/validate_false_negatives.py --json
"""

from __future__ import annotations

__manifest__ = """
args: []
description: >
  假阴性检测引擎——维护已知缺陷测试用例库（golden set），定期验证脚本系统能否检出已知缺陷，
  已知缺陷未被检出 → 假阴性 → Error Budget 消耗。
dimensions:
- D1
- D7
priority: P1
timeout_seconds: 60
warn_only: false
"""


import os
import argparse
import json as json_mod
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CASES_DIR = _REPO_ROOT / "scripts" / "governance" / "meta" / "false_negative_cases"
_CASES_INDEX = _CASES_DIR / "cases_index.yaml"
_RESULTS_LOG = _CASES_DIR / "results.jsonl"
_SCRIPTS_DIR = _REPO_ROOT / "scripts" / "governance"

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


def _ensure_cases_dir() -> None:
    """_ensure_cases_dir implementation."""
    _CASES_DIR.mkdir(parents=True, exist_ok=True)
    if not _CASES_INDEX.exists():
        tmp_path = f"{_CASES_INDEX}.{os.getpid()}.tmp"
        try:
            Path(tmp_path).write_text(
            "# 已知缺陷测试用例索引\n# 格式：dimension / 预期检测出的脚本 / 预期 Finding 描述\n"
            "cases: {}\n",
            encoding="utf-8",
        )
            os.replace(tmp_path, _CASES_INDEX)
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass


def _load_cases() -> dict:
    """_load_cases implementation."""
    _ensure_cases_dir()
    with open(_CASES_INDEX, encoding="utf-8") as f:
        return yaml.safe_load(f) or {"cases": {}}


def list_cases() -> list[dict]:
    """list_cases implementation."""
    data = _load_cases()
    result = []
    for case_id, case in data.get("cases", {}).items():
        result.append({"case_id": case_id, **case})
    return result


def add_case(case_file: str, dimension: str, expected_script: str,
             expected_description: str, severity: str = "HIGH") -> dict:
    """add_case implementation."""
    data = _load_cases()
    case_id = f"FN-{len(data['cases']) + 1:03d}"

    dest = _CASES_DIR / f"case_{case_id}.md"
    if os.path.isabs(case_file):
        import shutil
        shutil.copy(case_file, dest)
    else:
        src = _REPO_ROOT / case_file
        if not src.exists():
            return {"error": f"源文件不存在: {src}"}
        tmp_path = f"{dest}.{os.getpid()}.tmp"
        try:
            Path(tmp_path).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            os.replace(tmp_path, dest)
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

    cases = data.setdefault("cases", {})
    cases[case_id] = {
        "dimension": dimension,
        "expected_script": expected_script,
        "expected_description": expected_description,
        "severity": severity,
        "case_file": str(dest.relative_to(_REPO_ROOT)),
        "added_at": datetime.now(UTC).isoformat(),
    }
    tmp_path = f"{_CASES_INDEX}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        os.replace(tmp_path, _CASES_INDEX)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
    return {"case_id": case_id, "status": "added"}


def run_validation(dimension_filter: str | None = None) -> dict:
    """run_validation implementation."""
    cases_data = _load_cases()
    cases = cases_data.get("cases", {})
    results: list[dict] = []
    passed = 0
    failed = 0

    for case_id, case in cases.items():
        if dimension_filter and case.get("dimension") != dimension_filter:
            continue

        script_name = case.get("expected_script", "")
        script_path = _REPO_ROOT / "scripts" / "governance" / script_name

        result = {
            "timestamp": datetime.now(UTC).isoformat(),
            "case_id": case_id,
            "dimension": case.get("dimension"),
            "expected_script": script_name,
            "expected_description": case.get("expected_description", ""),
            "severity": case.get("severity", "HIGH"),
            "detected": False,
            "detail": "",
        }

        if not script_path.exists():
            result["detail"] = f"脚本不存在: {script_name}"
            result["detected"] = False
            failed += 1
            results.append(result)
            continue

        case_file = _REPO_ROOT / case.get("case_file", "")
        if not case_file.exists():
            result["detail"] = f"测试用例文件不存在: {case.get('case_file')}"
            result["detected"] = False
            failed += 1
            results.append(result)
            continue

        proc = subprocess.run(
            [sys.executable, str(script_path), "--target", str(case_file)],
            capture_output=True, text=True, timeout=30,
            cwd=str(_REPO_ROOT), encoding="utf-8", errors="replace",
            env={**os.environ, "PYTHONPATH": str(_SCRIPTS_DIR)},
        )

        output = (proc.stdout + proc.stderr).lower()
        expected_lower = case.get("expected_description", "").lower()

        if proc.returncode != 0 and expected_lower in output:
            result["detected"] = True
            passed += 1
            result["detail"] = "检测成功"
        elif proc.returncode != 0:
            result["detected"] = True
            passed += 1
            result["detail"] = "检测到异常（描述未完全匹配）"
        else:
            result["detected"] = False
            failed += 1
            result["detail"] = "未检测到——假阴性"

        results.append(result)

    with open(_RESULTS_LOG, "a", encoding="utf-8") as f:
        for r in results:
            f.write(json_mod.dumps(r, ensure_ascii=False) + "\n")

    summary = {
        "timestamp": datetime.now(UTC).isoformat(),
        "total_cases": len(results),
        "detected": passed,
        "not_detected": failed,
        "detection_rate": round(passed / len(results) * 100, 1) if results else 0,
        "all_passed": failed == 0,
        "results": results,
    }

    return summary


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="假阴性检测引擎")
    parser.add_argument("--list-cases", action="store_true", help="列出所有测试用例")
    parser.add_argument("--add-case", type=str, help="添加测试用例文件")
    parser.add_argument("--dimension", "-d", type=str, help="指定维度过滤")
    parser.add_argument("--expected-script", type=str, help="预期检测脚本")
    parser.add_argument("--expected-desc", type=str, help="预期 Finding 描述")
    parser.add_argument("--severity", type=str, default="HIGH", help="严重度")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    args = parser.parse_args()

    if args.list_cases:
        cases = list_cases()
        for c in cases:
            print(f"  [{c['case_id']}] [{c.get('dimension', '?')}] {c.get('expected_description', '')}", file=sys.stderr)
    elif args.add_case and args.expected_script and args.expected_desc:
        result = add_case(args.add_case, args.dimension or "D1",
                          args.expected_script, args.expected_desc, args.severity)
        print(f"[FN-DETECT] {result}", file=sys.stderr)
    else:
        result = run_validation(args.dimension)
        if args.json:
            print(json_mod.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"\n[FN-DETECT] 假阴性检测完成", file=sys.stderr)
            print(f"  总用例: {result['total_cases']}", file=sys.stderr)
            print(f"  ✅ 检测成功: {result['detected']}", file=sys.stderr)
            print(f"  ❌ 假阴性: {result['not_detected']}", file=sys.stderr)
            print(f"  检测率: {result['detection_rate']}%", file=sys.stderr)
            for r in result["results"]:
                if not r["detected"]:
                    print(f"  ⚠ [{r['case_id']}] [{r['severity']}] {r['expected_description']}: {r['detail']}", file=sys.stderr)
        sys.exit(0 if result["all_passed"] else 1)


if __name__ == "__main__":
    main()
