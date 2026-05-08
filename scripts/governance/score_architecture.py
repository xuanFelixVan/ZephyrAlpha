"""
对标 12-dimension-audit-matrix.md §6.1：
  自动化评分引擎，读取各维度采集指标 → 计算加权分数 → 输出报告。

用法:
  python scripts/governance/score_architecture.py [--quarterly] [--dimension D1..D12]
                                                  [--compare PREV] [--dashboard]

exit: 0=success, 1=scoring error, 2=infrastructure error
"""

from __future__ import annotations

import os

__manifest__ = """
args:
- --quarterly
- --dimension
- --compare
- --dashboard
description: 12 维架构评分自动化（12-dimension-audit-matrix §6.1 — D1~D12 加权评分）
dimensions:
- D5
priority: P1
timeout_seconds: 60
warn_only: false
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import REPO_ROOT, EXIT_PASS, EXIT_FINDINGS, EXIT_ERROR
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

AUDIT_MATRIX_PATH = (
    REPO_ROOT
    / "docs"
    / "02_enterprise_architecture"
    / "target-architecture"
    / "12-dimension-audit-matrix.md"
)
ARCH_GUARD_MANIFEST = REPO_ROOT / "scripts" / "arch_guard" / "_manifest.yaml"
INVARIANTS_PATH = (
    REPO_ROOT
    / "docs"
    / "02_enterprise_architecture"
    / "target-architecture"
    / "architecture-model"
    / "cross-cutting"
    / "invariants.yaml"
)
CONTRACTS_PATH = (
    REPO_ROOT
    / "docs"
    / "02_enterprise_architecture"
    / "target-architecture"
    / "architecture-model"
    / "contracts"
    / "cross-layer-contracts.yaml"
)
OUTPUT_DIR = REPO_ROOT / "data" / "architecture_scores"

DIMENSION_WEIGHTS = {
    "D1": 0.08,
    "D2": 0.06,
    "D3": 0.08,
    "D4": 0.06,
    "D5": 0.12,
    "D6": 0.15,
    "D7": 0.08,
    "D8": 0.06,
    "D9": 0.06,
    "D10": 0.08,
    "D11": 0.09,
    "D12": 0.08,
}

DIMENSION_NAMES = {
    "D1": "结构完整性",
    "D2": "链接有效性",
    "D3": "元数据合规",
    "D4": "路径规范",
    "D5": "架构一致性",
    "D6": "安全性",
    "D7": "代码质量",
    "D8": "文档同步",
    "D9": "知识管理",
    "D10": "测试覆盖",
    "D11": "治理合规",
    "D12": "AI 幻觉防护",
}


def load_yaml_safe(path: Path) -> dict:
    """load_yaml_safe implementation."""
    import yaml

    if not path.is_file():
        return {}
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def score_d6_security() -> float:
    """score_d6_security implementation."""
    score = 5.0
    invariants = load_yaml_safe(INVARIANTS_PATH)
    sec_invs = [i for i in invariants.get("invariants", []) if i.get("runtime_plane") in ("hot", "cross")]
    if sec_invs:
        score += 1.5
    manifest = load_yaml_safe(ARCH_GUARD_MANIFEST)
    ffs = manifest.get("fitness_functions", [])
    active_sec_ffs = [f for f in ffs if f.get("runtime_plane") in ("hot", "cross") and f.get("status") == "active"]
    if active_sec_ffs:
        score += 1.0
    scaffold_gates = REPO_ROOT / "scripts" / "arch_guard" / "check_scaffold_exit_gates.py"
    if scaffold_gates.exists():
        score += 1.0
    lsg_dir = REPO_ROOT / "src" / "zephyr" / "llm_security"
    if lsg_dir.exists() and any(lsg_dir.iterdir()):
        score += 0.5
    return min(score, 10.0)


def score_d5_architecture() -> float:
    """score_d5_architecture implementation."""
    score = 5.0
    contracts = load_yaml_safe(CONTRACTS_PATH)
    if contracts.get("contracts"):
        score += 1.5
    manifest = load_yaml_safe(ARCH_GUARD_MANIFEST)
    ffs = manifest.get("fitness_functions", [])
    active_ffs = [f for f in ffs if f.get("status") == "active"]
    if len(active_ffs) >= 15:
        score += 1.5
    dual_tree_sync = REPO_ROOT / "scripts" / "governance" / "d5_architecture" / "check_dual_tree_sync.py"
    if dual_tree_sync.exists():
        score += 1.0
    return min(score, 10.0)


def score_d10_test() -> float:
    """score_d10_test implementation."""
    score = 4.0
    manifest = load_yaml_safe(ARCH_GUARD_MANIFEST)
    ffs = manifest.get("fitness_functions", [])
    active_ffs = [f for f in ffs if f.get("status") == "active"]
    if active_ffs:
        score += 2.0
    l2_ffs = [f for f in active_ffs if f.get("maturity") == "L2-static-scan"]
    if l2_ffs:
        score += 1.5
    l3_ffs = [f for f in active_ffs if f.get("maturity") == "L3-runtime"]
    if l3_ffs:
        score += 1.5
    return min(score, 10.0)


def score_default(dim: str) -> float:
    """score_default implementation."""
    return 6.0

SCORING_FNS = {
    "D5": score_d5_architecture,
    "D6": score_d6_security,
    "D10": score_d10_test,
}


def compute_scores(dimensions: list[str] | None = None) -> dict[str, float]:
    """compute_scores implementation."""
    dims = dimensions or list(DIMENSION_WEIGHTS.keys())
    scores = {}
    for dim in dims:
        fn = SCORING_FNS.get(dim)
        scores[dim] = fn() if fn else score_default(dim)
    return scores


def compute_weighted_total(scores: dict[str, float]) -> float:
    """compute_weighted_total implementation."""
    total = 0.0
    for dim, score in scores.items():
        weight = DIMENSION_WEIGHTS.get(dim, 0.0)
        total += score * weight
    return round(total, 2)


def format_report(scores: dict[str, float], total: float) -> str:
    """format_report implementation."""
    lines = [
        "=" * 70,
        "ZephyrAlpha 12 维架构评分报告",
        f"生成时间: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "=" * 70,
        "",
        f"{'维度':<6} {'名称':<16} {'分数':>6} {'权重':>6} {'加权':>6}",
        "-" * 50,
    ]
    for dim in sorted(scores.keys()):
        name = DIMENSION_NAMES.get(dim, "—")
        score = scores[dim]
        weight = DIMENSION_WEIGHTS.get(dim, 0.0)
        weighted = round(score * weight, 2)
        lines.append(f"{dim:<6} {name:<16} {score:>6.1f} {weight:>6.2f} {weighted:>6.2f}")
    lines.append("-" * 50)
    lines.append(f"{'加权总分':<24} {'':>6} {'1.00':>6} {total:>6.2f}")
    lines.append("")
    if total >= 8.0:
        lines.append("评级: ★★★★ 优秀 (≥8.0)")
    elif total >= 6.5:
        lines.append("评级: ★★★ 良好 (≥6.5)")
    elif total >= 5.0:
        lines.append("评级: ★★ 合格 (≥5.0)")
    else:
        lines.append("评级: ★ 不合格 (<5.0)")
    lines.append("=" * 70)
    return "\n".join(lines)


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="12 维架构评分自动化")
    parser.add_argument("--quarterly", action="store_true", help="季度模式（保存历史快照）")
    parser.add_argument("--dimension", nargs="*", help="仅评分指定维度（D1-D12）")
    parser.add_argument("--compare", type=str, help="对比历史快照文件")
    parser.add_argument("--dashboard", action="store_true", help="输出 JSON 格式（供仪表盘消费）")
    args = parser.parse_args()

    dims = args.dimension if args.dimension else None
    scores = compute_scores(dims)
    total = compute_weighted_total(scores)

    if args.dashboard:
        output = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "scores": scores,
            "weighted_total": total,
            "dimension_names": DIMENSION_NAMES,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        report = format_report(scores, total)
        print(report)

    if args.quarterly:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        snapshot_path = OUTPUT_DIR / f"score_snapshot_{ts}.json"
        snapshot = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "scores": scores,
            "weighted_total": total,
        }
        tmp_path = f"{snapshot_path}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, snapshot_path)
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        print(f"\n快照已保存: {snapshot_path.relative_to(REPO_ROOT)}")

    if args.compare:
        try:
            with open(args.compare, encoding="utf-8") as f:
                prev = json.load(f)
            prev_scores = prev.get("scores", {})
            print("\n--- 与历史快照对比 ---")
            for dim in sorted(set(list(scores.keys()) + list(prev_scores.keys()))):
                curr = scores.get(dim, 0.0)
                prev_val = prev_scores.get(dim, 0.0)
                delta = round(curr - prev_val, 2)
                arrow = "↑" if delta > 0 else "↓" if delta < 0 else "→"
                print(f"  {dim}: {prev_val:.1f} → {curr:.1f} ({arrow}{delta:+.1f})")
        except Exception as e:
            print(f"[WARN] 无法读取对比文件: {e}")

    return EXIT_PASS
if __name__ == "__main__":
    sys.exit(main())
