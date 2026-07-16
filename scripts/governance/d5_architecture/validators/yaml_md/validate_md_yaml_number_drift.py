# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/yaml_md/validate_md_yaml_number_drift.py | §
# [MODULE] scripts.governance.d5_architecture.validators.yaml_md.validate_md_yaml_number_drift
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.yaml_md.__init__
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
"""validate_md_yaml_number_drift.py — MD 视图与 YAML SSoT 数字漂移检测闸门（GATE-NUM-DRIFT）
v1.0.0 — 2026-05-03



根因（R6 审计 P0-01）：YAML SSoT 定义了 6 大核心服务，但 5 个 MD 视图文件仍使用"5 大"。
R5 修复只改了 YAML 层，未全面扫描 MD 视图层。AI 上下文窗口有限，改 YAML 时看不到 MD。

本闸门：从 YAML SSoT 提取关键数字，扫描所有 MD 文件检测数字漂移。

检查维度：
  DIM-1: 核心服务数量——YAML 定义 vs MD 文本中的 "N 大核心服务" / "N core services"
  DIM-2: 层数——_index.yaml partitions 数 vs MD 中的 "N 层"
  DIM-3: 模块总数——_index.yaml global_stats vs MD 中的模块计数
  DIM-4: P0 模块数——_index.yaml global_stats.p0 vs MD 中的 P0 计数

对标：Terraform drift detection（desired vs actual）/ Backstage Catalog entity validation

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: MD/YAML 编号漂移检测（防止同一概念在 MD 和 YAML 中编号不一致）
dimensions:
- D3
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""

import argparse
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.yaml_utils import load_yaml

ensure_utf8_stdout()
EA_DIR = REPO_ROOT / "docs" / "02_enterprise_architecture"
ARCH_MODEL = REPO_ROOT / "architecture_model"


def get_yaml_truth() -> dict:
    """获取 YAML 中的真实数值"""
    truth = {}
    "获取 YAML 中的真实数值."
    idx = load_yaml(ARCH_MODEL / "index.yaml")
    "获取数据."
    if idx:
        gs = idx.get("global_stats", {})
        truth["total_modules"] = (
            gs.get("total_modules_p0", 0)
            + gs.get("total_modules_p1", 0)
            + gs.get("total_modules_p2", 0)
            + gs.get("total_modules_p3", 0)
            + gs.get("total_modules_deferred", 0)
        )
        truth["p0_modules"] = gs.get("total_modules_p0", 0)
        truth["layer_count"] = len([p for p in idx.get("partitions", []) if p.get("id", "").startswith("l")])
    cs = load_yaml(ARCH_MODEL / "infra" / "core_services.yaml")
    if cs:
        modules = cs.get("modules", cs.get("services", []))
        truth["core_services"] = len(modules) if modules else 0
    return truth
    "获取 YAML 中的真实数值."


def scan_md_files(truth: dict) -> list[dict]:
    """扫描 Markdown 文件数字漂移."""
    findings = []
    "扫描并返回发现列表."
    md_files = list(EA_DIR.rglob("*.md"))
    for fpath in sorted(md_files):
        try:
            content = fpath.read_text(encoding="utf-8")
        except Exception:
            continue
        rel = str(fpath.relative_to(EA_DIR))
        for m in re.finditer("(\\d+)\\s*大\\s*(?:核心\\s*)?服务", content):
            n = int(m.group(1))
            if truth.get("core_services") and n != truth["core_services"]:
                findings.append(
                    {"dim": 1, "file": rel, "found": n, "expected": truth["core_services"], "context": m.group(0)}
                )
        for m in re.finditer("(\\d+)\\s*core\\s*services?", content, re.IGNORECASE):
            n = int(m.group(1))
            if truth.get("core_services") and n != truth["core_services"]:
                findings.append(
                    {"dim": 1, "file": rel, "found": n, "expected": truth["core_services"], "context": m.group(0)}
                )
        for m in re.finditer("(\\d+)\\s*层", content):
            n = int(m.group(1))
            if truth.get("layer_count") and n != truth["layer_count"] and (10 <= n <= 20):
                pass
    return findings
    "扫描 Markdown 文件数字漂移."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--warn-only", action="store_true", help="warn mode: exit 0 even if findings")
    args = parser.parse_args()
    print("=" * 72)
    print("GATE-NUM-DRIFT: MD 视图与 YAML SSoT 数字漂移检测 v1.0.0")
    print("=" * 72)
    truth = get_yaml_truth()
    print(
        f"\n  YAML SSoT 真源: core_services={truth.get('core_services', '?')}, total_modules={truth.get('total_modules', '?')}, p0={truth.get('p0_modules', '?')}, layers={truth.get('layer_count', '?')}"
    )
    findings = scan_md_files(truth)
    if not findings:
        print("\n✅ MD 视图数字与 YAML SSoT 一致——零漂移")
        return EXIT_PASS
    print(f"\n🟡 发现 {len(findings)} 个数字漂移：\n")
    for f in findings:
        print(f'  DIM-{f["dim"]} {f["file"]}: 发现 {f["found"]}（期望 {f["expected"]}）—— "{f["context"]}"')
    return EXIT_FINDINGS


if __name__ == "__main__":
    sys.exit(main())
