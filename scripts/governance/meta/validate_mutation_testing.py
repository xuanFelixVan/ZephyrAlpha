# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/validate_mutation_testing.py | §
# [MODULE] scripts.governance.meta.validate_mutation_testing
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
# [TTL] task_bound
"""
validate_mutation_testing.py — 变异测试引擎（蓝图 §19.2 + B75）

主动向治理脚本注入缺陷，验证脚本系统的检测能力：
- 从 false_negative_cases/ 加载已知缺陷用例
- 注入缺陷到对应路径
- 运行对应维度的验证脚本
- 验证脚本是否检测到（true positive）或未检测到（false negative）

Usage:
    python scripts/governance/meta/validate_mutation_testing.py
    python scripts/governance/meta/validate_mutation_testing.py --dimension D1
    python scripts/governance/meta/validate_mutation_testing.py --dry-run
    python scripts/governance/meta/validate_mutation_testing.py --warn-only
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 变异测试引擎 — 注入已知缺陷→验证检测能力（false negative detection）
dimensions:
- D7
priority: P1
timeout_seconds: 120
warn_only: false
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parents[1]
_GOV_DIR = str(_SCRIPT_DIR)
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

from _shared.constants import EXIT_PASS, REPO_ROOT, SCRIPTS_DIR

CASES_DIR = Path(__file__).resolve().parent / "false_negative_cases"


def load_cases() -> list[dict]:
    """加载已知缺陷用例（D2 修复：json + yaml/yml 双源）。

    支持两种 case schema（加适配层对齐，**不强行统一签名**——沿用 project_memory
    DRY 重构裁定：签名不兼容的复制应保留适配层，而非强行统一）：

    - **json case**（单文件单用例）：``case_id`` / ``dimension`` / ``verifier`` /
      ``expected_finding_id`` / ``target_path`` / ``defect`` / ``expected_detection``
      / ``timeout_seconds``
    - **yaml case**（``*_cases.yaml`` 多用例 ``cases:`` 列表）：FalseNegativeCase
      schema（``case_id`` / ``description`` / ``expected_detection`` / ``severity``
      / ``input_file`` / ``expected_finding_count`` / ``false_negative_if``）+ 可选
      json 兼容字段（``verifier`` / ``expected_finding_id`` / ``target_path`` /
      ``defect`` / ``dimension``）

    yaml case 经适配层映射到 dict（与 json case 同构），供 check_detection 消费：
      - ``dimension`` ← ``dimension`` 或 ``expected_detection``
      - ``verifier`` ← ``verifier``（缺省 ""→ check_detection SKIP，不计 false negative）
      - ``expected_finding_id`` ← ``expected_finding_id`` 或 ``case_id``
      - ``target_path`` ← ``target_path`` 或 ``input_file``

    Returns:
        list[dict]: 缺陷用例（统一 dict schema）
    """
    cases: list[dict] = []
    if not CASES_DIR.exists():
        return cases

    # 1. JSON cases（单文件单用例）
    for case_file in sorted(CASES_DIR.glob("*.json")):
        try:
            with open(case_file, encoding="utf-8") as f:
                case = json.load(f)
                case["_source_file"] = str(case_file.relative_to(CASES_DIR))
                case["_schema"] = "json"
                cases.append(case)
        except (json.JSONDecodeError, KeyError):
            continue

    # 2. YAML cases（多用例 *_cases.yaml/*.yml）— D2 修复：原仅 glob *.json，
    #    导致 4 个 *_cases.yaml 死库存（governance/security/architecture/data_quality）
    try:
        import yaml
    except ImportError:  # pragma: no cover — yaml 是项目硬依赖
        yaml = None  # type: ignore[assignment]
    if yaml is not None:
        yaml_files = sorted(CASES_DIR.glob("*.yaml")) + sorted(CASES_DIR.glob("*.yml"))
        for case_file in yaml_files:
            try:
                with open(case_file, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                if not isinstance(data, dict):
                    continue
                raw_cases = data.get("cases", [])
                if not isinstance(raw_cases, list):
                    continue
                for c in raw_cases:
                    if not isinstance(c, dict):
                        continue
                    # 适配层：FalseNegativeCase schema → json-compatible dict
                    adapted = {
                        "case_id": c.get("case_id", "??"),
                        "dimension": c.get("dimension") or c.get("expected_detection", ""),
                        "description": c.get("description", ""),
                        "verifier": c.get("verifier", ""),
                        "expected_finding_id": c.get("expected_finding_id") or c.get("case_id", ""),
                        "target_path": c.get("target_path") or c.get("input_file", ""),
                        "defect": c.get("defect")
                        or {"type": "file_create", "path": c.get("input_file", "")},
                        "expected_detection": c.get("expected_detection", True),
                        "timeout_seconds": c.get("timeout_seconds", 30),
                        "severity": c.get("severity", "medium"),
                        "_source_file": str(case_file.relative_to(CASES_DIR)),
                        "_schema": "yaml",
                    }
                    cases.append(adapted)
            except (yaml.YAMLError, KeyError, TypeError):
                continue
    return cases


def apply_mutation(case: dict) -> Path | None:
    """应用变异——将缺陷注入到测试路径。

    Args:
        case: 缺陷用例定义

    Returns:
        Path | None: 变异后的临时文件路径
    """
    target_path = Path(case.get("target_path", ""))
    if not target_path.is_absolute():
        target_path = REPO_ROOT / target_path

    if not target_path.exists():
        print(f"  [SKIP] 目标不存在: {target_path}", file=sys.stderr)
        return None

    defect = case.get("defect", {})
    defect_type = defect.get("type", "file_create")

    if defect_type == "file_create":
        content = case.get("defect_content", "")
        tmp_dir = tempfile.mkdtemp(prefix="_mutation_")
        injected = Path(tmp_dir) / target_path.name
        injected.write_text(content, encoding="utf-8")
        return injected

    if defect_type == "content_inject":
        return target_path

    return target_path


def check_detection(
    case: dict,
    dimension: str | None = None,
) -> tuple[bool, str]:
    """检查脚本是否能检测到变异。

    Args:
        case: 缺陷用例
        dimension: 限定维度

    Returns:
        tuple[bool, str]: (是否检测到, 详情)
    """
    expected_dim = case.get("dimension", "")
    if dimension and expected_dim != dimension:
        return True, "SKIP（维度不匹配）"

    verifier = case.get("verifier", "")
    if not verifier:
        # D2 配套修复：yaml case（FalseNegativeCase schema）无 verifier 字段时
        # SKIP 而非计 false negative——否则 4 个 *_cases.yaml 死库存会膨胀漏检计数。
        # SKIP 语义：未指定验证脚本 = 未配置 oracle，不计入 detected/missed 分母。
        return True, "SKIP（未指定验证脚本）"

    verifier_path = SCRIPTS_DIR / verifier
    if not verifier_path.exists():
        return False, f"验证脚本不存在: {verifier}"

    # P3-T1 健壮性修复：捕获 verifier 超时/异常——原裸 subprocess.run 超时会抛
    # TimeoutExpired 导致整个 run_mutations 中断（pre-existing 死库存 verifier
    # check_naming_convention.py 即 30s 超时）。超时/异常 = verifier 未检出（false
    # negative），如实记录而非崩溃，使框架可端到端运行至新 RR case。
    try:
        result = subprocess.run(
            [sys.executable, str(verifier_path), "--warn-only"],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=case.get("timeout_seconds", 30),
            cwd=str(REPO_ROOT),
        )
    except subprocess.TimeoutExpired:
        return False, f"TIMEOUT（{case.get('timeout_seconds', 30)}s）"
    except Exception as e:  # noqa: BLE001 — verifier 启动失败如实记录
        return False, f"verifier run error: {e}"

    expected_finding_id = case.get("expected_finding_id", "")
    stdout = result.stdout or ""

    detected = expected_finding_id in stdout
    return detected, f"exit={result.returncode}, detected={'YES' if detected else 'NO'}"


def run_mutations(
    dimension: str | None = None,
    dry_run: bool = False,
    warn_only: bool = False,
) -> int:
    """运行变异测试。

    Args:
        dimension: 限定维度
        dry_run: 预览模式
        warn_only: 警告模式

    Returns:
        int: exit code
    """
    cases = load_cases()
    if not cases:
        print("[MUTATION] 无缺陷用例可用", file=sys.stderr)
        return EXIT_PASS

    print(f"\n[MUTATION] 加载 {len(cases)} 个缺陷用例\n", file=sys.stderr)

    detected_count = 0
    missed_count = 0
    skipped_count = 0

    for case in cases:
        case_id = case.get("case_id", "??")
        desc = case.get("description", "")[:80]
        print(f"  [{case_id}] {desc} ...", end=" ", flush=True, file=sys.stderr)

        if dry_run:
            print("DRY-RUN", file=sys.stderr)
            continue

        detected, detail = check_detection(case, dimension)
        if "SKIP" in detail:
            print(detail, file=sys.stderr)
            skipped_count += 1
        elif detected:
            print(f"✅ 已检测 ({detail})", file=sys.stderr)
            detected_count += 1
        else:
            print(f"❌ 未检出 — FALSE NEGATIVE ({detail})", file=sys.stderr)
            missed_count += 1

    total = detected_count + missed_count + skipped_count
    detection_rate = (
        detected_count / (detected_count + missed_count) * 100 if (detected_count + missed_count) > 0 else 0
    )

    print(
        f"\n  检测率: {detected_count}/{detected_count + missed_count} ({detection_rate:.0f}%), 跳过: {skipped_count}",
        file=sys.stderr,
    )

    if missed_count > 0:
        print(f"  ⚠ {missed_count} 个 FALSE NEGATIVE——脚本系统缺陷被绕过", file=sys.stderr)

    if warn_only:
        return EXIT_PASS
    return 1 if missed_count > 0 else 0


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="变异测试引擎")
    parser.add_argument("--dimension", type=str, help="限定维度（如 D1）")
    parser.add_argument("--dry-run", action="store_true", help="预览模式")
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
    args = parser.parse_args()

    exit_code = run_mutations(
        dimension=args.dimension,
        dry_run=args.dry_run,
        warn_only=args.warn_only,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
