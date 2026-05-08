"""validate_blueprint_registry.py — Blueprint registry self-check.

对标：PS-STD-003 D11（登记表与实际文件对账）
检测：file_path 存在性、total_blueprints、孤儿 blueprint.md、scope 目录。
exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: Blueprint registry self-check (declared rows vs files on disk)
dimensions:
- D3
- D11
priority: P1
timeout_seconds: 30
warn_only: false
"""

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_ERROR, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
BLUEPRINT_REGISTRY_PATH = REPO_ROOT / "docs" / "03_modules" / "blueprint-registry.yaml"
try:
    import yaml
except ImportError:
    print("ERROR: PyYAML 未安装，请运行 pip install pyyaml", file=sys.stderr)
    sys.exit(EXIT_ERROR)


def load_registry() -> dict | None:
    """加载注册表"""
    if not BLUEPRINT_REGISTRY_PATH.exists():
        return None
    try:
        with open(BLUEPRINT_REGISTRY_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except (OSError, yaml.YAMLError) as e:
        print(f"ERROR: 无法解析蓝图登记表: {e}", file=sys.stderr)
        return None


def check_registry(registry: dict) -> list[dict]:
    """检查注册表"""
    findings = []
    reg_meta = registry.get("registry", {})
    if not reg_meta:
        findings.append(
            {
                "file": str(BLUEPRINT_REGISTRY_PATH.relative_to(REPO_ROOT)),
                "line": 0,
                "pattern": "缺少 registry 元数据段",
                "matched": "registry key not found",
            }
        )
        return findings
    scope = reg_meta.get("scope", "")
    decl_total = reg_meta.get("total_blueprints", 0)
    declared_scope = reg_meta.get("scope", "")
    if declared_scope:
        scope_suffix = declared_scope.strip().strip("/").replace("\\", "/")
        scope_dir = REPO_ROOT / "docs" / scope_suffix if scope_suffix else REPO_ROOT / "docs" / "03_modules"
        if not scope_dir.exists():
            findings.append(
                {
                    "file": str(BLUEPRINT_REGISTRY_PATH.relative_to(REPO_ROOT)),
                    "line": 0,
                    "pattern": "registry.scope 目录不存在",
                    "matched": f"scope={declared_scope}",
                }
            )
    blueprints = registry.get("blueprints", [])
    if isinstance(blueprints, dict):
        blueprint_list = []
        for mod_id, bp in blueprints.items():
            bp["module_id"] = mod_id
            blueprint_list.append(bp)
        blueprints = blueprint_list
    actual_count = len(blueprints)
    if actual_count != decl_total:
        findings.append(
            {
                "file": str(BLUEPRINT_REGISTRY_PATH.relative_to(REPO_ROOT)),
                "line": 0,
                "pattern": "total_blueprints 计数不一致",
                "matched": f"declared={decl_total}, actual={actual_count}",
            }
        )
    for bp in blueprints:
        fp = bp.get("file_path") or bp.get("blueprint_file", "")
        if fp:
            full_path = REPO_ROOT / "docs" / fp if not str(fp).startswith("docs/") else REPO_ROOT / fp
            if not full_path.exists():
                findings.append(
                    {
                        "file": str(BLUEPRINT_REGISTRY_PATH.relative_to(REPO_ROOT)),
                        "line": 0,
                        "pattern": f'蓝图文件缺失: {bp.get('module_id', '?')}',
                        "matched": f"file_path={fp}",
                    }
                )
    module_ids_seen = set()
    for bp in blueprints:
        mid = bp.get("module_id", "")
        if mid in module_ids_seen:
            findings.append(
                {
                    "file": str(BLUEPRINT_REGISTRY_PATH.relative_to(REPO_ROOT)),
                    "line": 0,
                    "pattern": f"重复 module_id: {mid}",
                    "matched": f"module_id={mid}",
                }
            )
        module_ids_seen.add(mid)
    if scope:
        scope_suffix = scope.strip().strip("/").replace("\\", "/")
        scope_dir = REPO_ROOT / "docs" / scope_suffix
        if scope_dir.exists():
            registered_files = set()
            for bp in blueprints:
                fp = bp.get("file_path") or bp.get("blueprint_file", "")
                if fp:
                    rel = fp if str(fp).startswith("docs/") else f"docs/{fp}"
                    registered_files.add(rel.replace("\\", "/"))
            for md_file in scope_dir.rglob("blueprint.md"):
                rel = str(md_file.relative_to(REPO_ROOT)).replace("\\", "/")
                if rel not in registered_files:
                    findings.append(
                        {
                            "file": str(BLUEPRINT_REGISTRY_PATH.relative_to(REPO_ROOT)),
                            "line": 0,
                            "pattern": "未登记的蓝图文件",
                            "matched": f"file={rel}",
                        }
                    )
    return findings


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="蓝图登记表自校验")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    registry = load_registry()
    if registry is None:
        print("ERROR: 蓝图登记表不存在或无法解析", file=sys.stderr)
        if args.warn_only:
            sys.exit(EXIT_PASS)
        sys.exit(EXIT_ERROR)
    findings = check_registry(registry)
    if findings:
        print(f"\n[BLUEPRINT-REGISTRY] {len(findings)} 蓝图登记表问题:\n", file=sys.stderr)
        for f in findings:
            print(f'  [{f['pattern']}] {f['matched']}', file=sys.stderr)
        print(file=sys.stderr)
    total = len(findings)
    print(f"Scanned blueprint registry, {total} findings", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
