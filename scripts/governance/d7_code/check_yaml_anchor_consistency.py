# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] scripts.governance.d7_code.check_yaml_anchor_consistency
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] stdlib(argparse/json/re/sys/pathlib)
# [CONSUMERS] CI governance.yml（Tier 3 锚定一致性门禁）; 人工审计
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 扫描 config/+architecture_model/ 所有 YAML 检测治理锚定一致性: P1 [A_config]遗留行/P2 锚定块↔body不一致/P3 缺锚定块/P4 锚定块缺blueprint字段; 豁免 grafana/prometheus/docker-compose 第三方配置
# [MODIFY-GUARD] trae_047_engineering_file_header.yaml（B_yaml 6字段格式真源: blueprint/module_id/stability/safety_level/ai_autonomy/ttl）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=无问题; exit 1=发现问题; exit 2=参数错误
# [TESTS] tests/governance/commit_gates/test_check_yaml_anchor_consistency.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""check_yaml_anchor_consistency.py — YAML 治理锚定一致性扫描.

检测 config/ 与 architecture_model/ 下所有 YAML 文件的 B_yaml 治理锚定块一致性，
防止 [A_config] 旧格式回退、锚定块↔body module_id 漂移、锚定块字段缺失。

B_yaml 格式真源（TRAE-047）: 6 字段注释块——
    # --- 治理锚定 ---
    # blueprint: <module_id> | <path> | <§section>
    # module_id: <id>
    # stability: <frozen|stable|evolving|volatile>
    # safety_level: <H|M|L>
    # ai_autonomy: <immutable_core|human_gated|ai_modifiable>
    # ttl: <permanent|task_bound|...>
    # --- 治理锚定结束 ---

用法:
  # 全量扫描（CI 用）
  python scripts/governance/d7_code/check_yaml_anchor_consistency.py

  # JSON 输出（供 CI 消费）
  python scripts/governance/d7_code/check_yaml_anchor_consistency.py --json

  # 指定项目根
  python scripts/governance/d7_code/check_yaml_anchor_consistency.py --root /path/to/repo

退出码:
  0 — 无问题
  1 — 发现问题
  2 — 参数错误

问题分类:
  P1_LEGACY_A_CONFIG      — 残留 [A_config] 旧格式行（B_yaml 锚定块已取代）
  P2_ANCHOR_BODY_MISMATCH — 锚定块 module_id 与 body module_id 不一致
  P3_MISSING_ANCHOR_BLOCK — 有 body module_id 但缺 B_yaml 锚定块
  P4_MISSING_BLUEPRINT    — 锚定块缺 blueprint 字段（B_yaml 要求 6 字段）
"""

from __future__ import annotations

__manifest__ = """
args: []
description: check_yaml_anchor_consistency.py — YAML 治理锚定一致性扫描.
dimensions:
- D7
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import json
import re
import sys
from pathlib import Path

# === 正则定义 ===

# [A_config] 旧格式遗留行（B_yaml 已取代）
RE_LEGACY_A_CONFIG = re.compile(r"^#\s*\[A_config\]\s*module_id[:=]\s*(\S+)", re.MULTILINE)

# B_yaml 治理锚定块
RE_ANCHOR_BLOCK = re.compile(
    r"# --- 治理锚定 ---\n(.*?)# --- 治理锚定结束 ---",
    re.DOTALL,
)

# 锚定块内字段
RE_ANCHOR_MODULE_ID = re.compile(r"^#\s*module_id:\s*(\S+)\s*$", re.MULTILINE)
RE_ANCHOR_BLUEPRINT = re.compile(r"^#\s*blueprint:\s*(.+?)\s*$", re.MULTILINE)

# body module_id：顶层非注释 module_id: 行
RE_BODY_MODULE_ID = re.compile(r"^module_id:\s*['\"]?(\S+?)['\"]?\s*$", re.MULTILINE)


# 第三方工具配置豁免（不需要治理锚定块）
EXEMPT_PATTERNS = [
    re.compile(r"grafana[/\\]"),
    re.compile(r"prometheus[/\\]prometheus\.yml$"),
    re.compile(r"docker-compose\.override\.example\.yml$"),
]


def _is_exempt(rel_path: str) -> bool:
    """_is_exempt implementation."""
    norm = rel_path.replace("\\", "/")
    return any(pat.search(norm) for pat in EXEMPT_PATTERNS)


def scan_file(path: Path) -> dict:
    """扫描单个 YAML 文件，返回检测结果."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return {"path": str(path), "error": str(e)}

    legacy_ids = [m.group(1).strip() for m in RE_LEGACY_A_CONFIG.finditer(content)]

    anchor_block = RE_ANCHOR_BLOCK.search(content)
    anchor_module_id = None
    anchor_blueprint = None
    if anchor_block:
        m = RE_ANCHOR_MODULE_ID.search(anchor_block.group(1))
        if m:
            anchor_module_id = m.group(1).strip()
        m = RE_ANCHOR_BLUEPRINT.search(anchor_block.group(1))
        if m:
            anchor_blueprint = m.group(1).strip()

    body_module_id = None
    m = RE_BODY_MODULE_ID.search(content)
    if m:
        body_module_id = m.group(1).strip().strip("'\"")

    return {
        "path": str(path),
        "legacy_a_config_ids": legacy_ids,
        "anchor_module_id": anchor_module_id,
        "anchor_blueprint": anchor_blueprint,
        "body_module_id": body_module_id,
        "has_anchor_block": anchor_block is not None,
    }


def classify(result: dict) -> list[str]:
    """返回问题标签列表."""
    if result.get("error"):
        return ["ERR"]
    problems = []
    if result["legacy_a_config_ids"]:
        problems.append("P1_LEGACY_A_CONFIG")
    if (
        result["anchor_module_id"]
        and result["body_module_id"]
        and result["anchor_module_id"] != result["body_module_id"]
    ):
        problems.append("P2_ANCHOR_BODY_MISMATCH")
    if result["body_module_id"] and not result["has_anchor_block"]:
        problems.append("P3_MISSING_ANCHOR_BLOCK")
    if result["has_anchor_block"] and not result["anchor_blueprint"]:
        problems.append("P4_MISSING_BLUEPRINT")
    return problems


def scan_all(root: Path) -> dict:
    """扫描 config/ 与 architecture_model/ 所有 YAML 文件."""
    scan_dirs = [root / "config", root / "architecture_model"]
    results = []
    for d in scan_dirs:
        if not d.exists():
            continue
        for p in d.rglob("*"):
            if p.suffix.lower() not in (".yaml", ".yml"):
                continue
            r = scan_file(p)
            rel = str(p.relative_to(root))
            r["rel_path"] = rel
            r["exempt"] = _is_exempt(rel)
            r["problems"] = classify(r)
            results.append(r)

    problem_files = [r for r in results if r["problems"] and not r["exempt"]]
    by_problem: dict[str, list] = {}
    for r in problem_files:
        for p in r["problems"]:
            by_problem.setdefault(p, []).append(r)

    return {
        "total": len(results),
        "problem_files": len(problem_files),
        "by_problem": {k: len(v) for k, v in by_problem.items()},
        "problem_details": by_problem,
        "results": results,
    }


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(
        description="YAML 治理锚定一致性扫描（B_yaml 锚定块 vs body vs [A_config] 遗留）"
    )
    parser.add_argument("--root", default=None, help="项目根目录（默认自动检测）")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出（供 CI 消费）")
    args = parser.parse_args()

    root = Path(args.root) if args.root else Path(__file__).resolve().parents[3]
    if not root.is_dir():
        print(f"ERROR: root not found: {root}", file=sys.stderr)
        return 2

    result = scan_all(root)

    if args.json:
        out = {
            "total": result["total"],
            "problem_files": result["problem_files"],
            "by_problem": result["by_problem"],
            "problems": [
                {
                    "file": r["rel_path"],
                    "problems": r["problems"],
                    "legacy_a_config_ids": r["legacy_a_config_ids"],
                    "anchor_module_id": r["anchor_module_id"],
                    "body_module_id": r["body_module_id"],
                    "anchor_blueprint": r["anchor_blueprint"],
                }
                for r in result["results"]
                if r["problems"] and not r["exempt"]
            ],
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(f"=== YAML 治理锚定一致性扫描 ===")
        print(f"项目根: {root}")
        print(f"总文件数: {result['total']}")
        print(f"问题文件数: {result['problem_files']}")
        print(f"问题分类: {result['by_problem']}")
        for p, files in sorted(result["problem_details"].items()):
            print(f"\n--- {p} ({len(files)} 文件) ---")
            for r in files:
                print(f"  {r['rel_path']}")
                print(f"      legacy={r['legacy_a_config_ids']} "
                      f"anchor={r['anchor_module_id']} body={r['body_module_id']}")
                if r.get("anchor_blueprint") is not None:
                    print(f"      blueprint={r['anchor_blueprint']}")

    return 1 if result["problem_files"] else 0


if __name__ == "__main__":
    sys.exit(main())
