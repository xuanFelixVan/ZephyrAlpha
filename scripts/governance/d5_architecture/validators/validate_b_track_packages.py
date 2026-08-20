# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_b_track_packages.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_b_track_packages
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: CI 治理门禁（governance.yml B-Track Consistency 步骤 + run_all D5 编排）按需调用，非常驻服务
"""validate_b_track_packages.py — B 轨 b_track 一致性校验

治本重构（2026-07-30，#ARCH-INDEX-005）：
- 原实现：B_TRACK_DIRS 硬编码 kebab_case 集合（含幻影 "kb"），与 src/zephyr/
  snake_case 目录名永远不匹配 → 校验空转，抓不到 kb 幻影。
- 新实现：从 index.yaml 动态读 b_track modules 列表，与 layers/b_*.yaml 物理文件
  集合对比一致性。能抓两类漂移：
  - 幻影模块：index.yaml 列出但 layers/b_{id}.yaml 不存在（如原 kb）
  - 漏登模块：layers/b_*.yaml 物理存在但 index.yaml 未列（如原 execution_model）
- index.yaml 现由 dm200916_write_direct.py 从物理文件派生，本 validator 作为
  防御性校验：若 dm200916 损坏或有人手改 index.yaml，本校验能拦截。

校验维度：
- index.yaml b_track modules[].id ↔ layers/b_{id}.yaml 物理文件 双向对账

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: B 轨 b_track 一致性校验（index.yaml b_track ↔ layers/b_*.yaml 双向对账）
dimensions:
- D5
priority: P2
timeout_seconds: 30
warn_only: false
"""

import sys
from pathlib import Path

import yaml

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

ARCH_MODEL = REPO_ROOT / "architecture_model"
INDEX_YAML = ARCH_MODEL / "index.yaml"
LAYERS_DIR = ARCH_MODEL / "layers"


def _load_index_b_track() -> list[dict]:
    """从 index.yaml 读取 b_track modules 列表（真源：dm200916 派生产物）."""
    if not INDEX_YAML.exists():
        return []
    data = yaml.safe_load(INDEX_YAML.read_text(encoding="utf-8")) or {}
    # index.yaml partitions 列表中 id=b_track 的条目
    for part in data.get("partitions", []) or []:
        if part.get("id") == "b_track":
            return part.get("modules", []) or []
    return []


def _scan_physical_b_track() -> set[str]:
    """扫描 layers/b_*.yaml 物理文件，返回 b_track module id 集合.

    b_ 前缀 = b_track 成员资格（schema.yaml 约定 track 仅 b_track）。
    id 取文件名去 b_ 前缀（与 dm200916 派生逻辑一致）。
    """
    ids = set()
    if not LAYERS_DIR.exists():
        return ids
    for f in LAYERS_DIR.glob("b_*.yaml"):
        stem = f.stem
        mod_id = stem[2:] if stem.startswith("b_") else stem
        ids.add(mod_id)
    return ids


def scan_b_track_packages() -> list[dict]:
    """校验 index.yaml b_track ↔ layers/b_*.yaml 物理文件一致性."""
    findings: list[dict] = []

    index_modules = _load_index_b_track()
    index_ids = {m.get("id") for m in index_modules if m.get("id")}
    physical_ids = _scan_physical_b_track()

    # 幻影模块：index.yaml 列出但物理文件不存在
    phantom = index_ids - physical_ids
    for mod_id in sorted(phantom):
        findings.append(
            {
                "module": mod_id,
                "type": "PHANTOM_MODULE",
                "detail": f"index.yaml b_track 列出模块 '{mod_id}' 但 layers/b_{mod_id}.yaml 不存在（幻影模块）",
                "severity": "HIGH",
            }
        )

    # 漏登模块：物理文件存在但 index.yaml 未列
    missing = physical_ids - index_ids
    for mod_id in sorted(missing):
        findings.append(
            {
                "module": mod_id,
                "type": "MISSING_FROM_INDEX",
                "detail": f"layers/b_{mod_id}.yaml 物理存在但 index.yaml b_track 未登记（漏登）",
                "severity": "HIGH",
            }
        )

    return findings


def main() -> None:
    """入口函数."""
    import argparse

    parser = argparse.ArgumentParser(description="B 轨 b_track 一致性校验（index.yaml ↔ layers/b_*.yaml）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()

    findings = scan_b_track_packages()

    if findings:
        print(f"\n[B-TRACK] {len(findings)} 个 b_track 一致性问题:", file=sys.stderr)
        for f in findings:
            print(f"  [{f['severity']}] {f['module']} ({f['type']})", file=sys.stderr)
            print(f"    {f['detail']}", file=sys.stderr)
    else:
        print("[B-TRACK] b_track 一致性合规（index.yaml ↔ layers/b_*.yaml 对账通过）", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_FINDINGS if findings else EXIT_PASS)


if __name__ == "__main__":
    main()
