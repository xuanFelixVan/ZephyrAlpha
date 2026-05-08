"""
对标：Problem — 12份 blueprint layer 声明 ≠ 物理目录（根因：缺外部一致性检查）
职责：读取 03_modules/**/blueprint.md 的 frontmatter layer 字段，
     与物理目录名交叉比对，检测不一致并报告。

检测逻辑：
- 物理路径包含 `l01_infrastructure/` → 期望 layer=L01
- 物理路径包含 `l00_data_source/`   → 期望 layer=L00
- 物理路径包含 `l02_alpha_factor/`  → 期望 layer=L02
- ...
- 物理路径包含 `_cross_layer/`      → 期望 layer=cross_layer
- 物理路径包含 `_master-blueprint/` → 期望 layer=cross_layer（Level 1 域总蓝图）
- 物理路径包含 `_domain-governance/`→ 期望 layer=cross_layer（Level 1 治理总蓝图）
- 物理路径包含 `_sys-master/`       → 期望 layer=cross_layer（Level 0 系统总蓝图）

三层防线定位：Layer 1 — 预防（AI/人创建蓝图后立即运行）；Layer 2 — 检测（pre-commit/CI）

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args:
- --warn-only
description: 蓝图 layer 声明 vs 物理目录一致性校验（预防 layer 不匹配 — 三层防线 Layer 1+2）
dimensions:
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""

import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT, EXIT_PASS, EXIT_FINDINGS, EXIT_ERROR
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter_from_file

ensure_utf8_stdout()
import argparse

LAYER_DIR_MAP = {
    "l00_data_source": "L00",
    "l01_infrastructure": "L01",
    "l02_alpha_factor": "L02",
    "l03_signal_generation": "L03",
    "l04_risk_management": "L04",
    "l05_portfolio_construction": "L05",
    "l06_trade_execution": "L06",
    "l07_post_trade_analytics": "L07",
    "l08_human_ai_interface": "L08",
    "l09_research_innovation": "L09",
    "l10_compliance": "L10",
    "l11_ml_platform": "L11",
    "l12_system_telemetry": "L12",
    "l13_experimentation": "L13",
    "_cross_layer": "cross_layer",
    "_master-blueprint": "cross_layer",
    "_domain-governance": "cross_layer",
    "_sys-master": "cross_layer",
}


def expected_layer_from_path(filepath: Path) -> str | None:
    """expected_layer_from_path implementation."""
    rel = filepath.relative_to(REPO_ROOT).as_posix()
    for dir_key, expected_layer in LAYER_DIR_MAP.items():
        if f"/{dir_key}/" in rel or rel.startswith(f"docs/03_modules/{dir_key}/"):
            return expected_layer
    return None


def scan_layer_consistency() -> tuple[list[dict], int]:
    """scan_layer_consistency implementation."""
    findings: list[dict] = []
    files_scanned = 0

    modules_dir = REPO_ROOT / "docs" / "03_modules"
    if not modules_dir.exists():
        return findings, files_scanned

    for filepath in sorted(modules_dir.rglob("blueprint.md")):
        files_scanned += 1
        fm = parse_frontmatter_from_file(filepath)
        if not fm:
            continue

        declared_layer = fm.get("layer", "")
        if not declared_layer:
            rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
            findings.append({
                "file": rel,
                "declared_layer": "",
                "expected_layer": "?",
                "detail": "缺少 layer 字段",
                "severity": "HIGH",
            })
            continue

        expected = expected_layer_from_path(filepath)
        if expected is None:
            continue

        if declared_layer != expected:
            rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
            findings.append({
                "file": rel,
                "declared_layer": declared_layer,
                "expected_layer": expected,
                "detail": f"layer 不一致: 声明={declared_layer}，物理目录要求={expected}",
                "severity": "HIGH",
            })

    return findings, files_scanned


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="蓝图 layer 声明 vs 物理目录一致性校验")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()

    findings, files_scanned = scan_layer_consistency()

    print(f"\n[LAYER-CONSISTENCY] 扫描 {files_scanned} 份 blueprint.md", file=sys.stderr)

    if findings:
        print(f"\n  {len(findings)} 个 layer 不一致:", file=sys.stderr)
        for f in findings:
            print(f"\n    [{f['severity']}] {f['file']}", file=sys.stderr)
            print(f"      {f['detail']}", file=sys.stderr)

        print(f"\n⚠ {len(findings)} 个 layer 声明与物理目录不一致！", file=sys.stderr)
        if not args.warn_only:
            sys.exit(EXIT_FINDINGS)
        sys.exit(EXIT_PASS)

    print("\n✅ 全部 blueprints layer 声明与物理目录一致", file=sys.stderr)
    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
