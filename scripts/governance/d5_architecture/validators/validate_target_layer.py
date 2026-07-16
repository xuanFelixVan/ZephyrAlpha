# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_target_layer.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_target_layer
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.__init__
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
对标：target_layer_vocabulary.yaml v1.0.0——target_layer 字段值体系多真源不一致修复
职责：校验代码/测试中的 target_layer 赋值是否使用 target_layer_vocabulary.yaml 合法值
     检测废弃值（D_DATA/基础设施/D_COMPLIANCE 等）并提示替换

检测逻辑：
- 扫描 src/ 和 tests/ 下 .py 文件
- 正则匹配 target_layer\s*=\s*["'](D_[A-Z_]+|基础设施)["'] 模式
- 校验值是否在 target_layer_vocabulary.yaml 的 values 或 deprecated_values 中
- 废弃值 → warning + 建议替换
- 未知值（不在 values 也不在 deprecated_values）→ error

三层防线定位：Layer 2 — 检测（pre_commit/CI 手动运行）

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args:
- --warn-only
description: target_layer 值合法性校验（预防废弃值/非法值——三层防线 Layer 2）
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

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
import argparse

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML 未安装, 请运行 pip install pyyaml", file=sys.stderr)
    sys.exit(2)

# target_layer_vocabulary.yaml 真源路径
VOCAB_PATH = REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "vocabularies" / "target_layer_vocabulary.yaml"

# target_layer 赋值正则（匹配 target_layer="D_XXX" 或 target_layer='D_XXX' 或 target_layer="基础设施"）
_TARGET_LAYER_RE = re.compile(r'target_layer\s*=\s*["\']([^"\']+)["\']')


def load_vocabulary() -> tuple[set[str], dict[str, str]]:
    """加载 target_layer_vocabulary.yaml，返回 (合法值集合, 废弃值→替换值映射)。"""
    if not VOCAB_PATH.exists():
        print(f"ERROR: 词表文件不存在: {VOCAB_PATH}", file=sys.stderr)
        sys.exit(2)

    data = yaml.safe_load(VOCAB_PATH.read_text(encoding="utf-8"))
    valid_values = {v["value"] for v in data.get("values", [])}
    deprecated_map = {
        v["value"]: v.get("replacement", "")
        for v in data.get("deprecated_values", [])
    }
    return valid_values, deprecated_map


def scan_files(valid_values: set[str], deprecated_map: dict[str, str]) -> list[dict]:
    """扫描 src/ 和 tests/ 下 .py 文件，检测 target_layer 赋值。"""
    findings: list[dict] = []
    scan_dirs = [REPO_ROOT / "src", REPO_ROOT / "tests"]

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for py_file in scan_dir.rglob("*.py"):
            rel = str(py_file.relative_to(REPO_ROOT)).replace("\\", "/")
            # 跳过 .aidrafts/ worktree 副本
            if ".aidrafts/" in rel:
                continue
            try:
                text = py_file.read_text(encoding="utf-8")
            except Exception:
                continue
            for line_no, line in enumerate(text.split("\n"), 1):
                for m in _TARGET_LAYER_RE.finditer(line):
                    val = m.group(1)
                    if val in valid_values:
                        continue  # 合法值
                    if val in deprecated_map:
                        replacement = deprecated_map[val]
                        findings.append({
                            "file": rel,
                            "line": line_no,
                            "value": val,
                            "severity": "WARNING",
                            "detail": f"废弃值 '{val}'，建议替换为 '{replacement}'",
                        })
                    else:
                        findings.append({
                            "file": rel,
                            "line": line_no,
                            "value": val,
                            "severity": "ERROR",
                            "detail": f"未知值 '{val}'，不在 target_layer_vocabulary.yaml 合法值集合中",
                        })
    return findings


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="target_layer 值合法性校验")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()

    valid_values, deprecated_map = load_vocabulary()

    print(f"\n[TARGET-LAYER] 词表合法值: {len(valid_values)} 个，废弃值: {len(deprecated_map)} 个", file=sys.stderr)
    print(f"[TARGET-LAYER] 扫描 src/ 和 tests/ 下 .py 文件", file=sys.stderr)

    findings = scan_files(valid_values, deprecated_map)

    if findings:
        errors = [f for f in findings if f["severity"] == "ERROR"]
        warnings = [f for f in findings if f["severity"] == "WARNING"]

        print(f"\n  {len(findings)} 个问题 ({len(errors)} errors, {len(warnings)} warnings):", file=sys.stderr)
        for f in findings:
            print(f"\n    [{f['severity']}] {f['file']}:{f['line']}", file=sys.stderr)
            print(f"      {f['detail']}", file=sys.stderr)

        if errors:
            print(f"\n✗ {len(errors)} 个未知 target_layer 值！", file=sys.stderr)
            sys.exit(EXIT_FINDINGS)
        elif warnings and not args.warn_only:
            print(f"\n⚠ {len(warnings)} 个废弃 target_layer 值！", file=sys.stderr)
            sys.exit(EXIT_FINDINGS)

    print("\n✅ target_layer 值全部合法", file=sys.stderr)
    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
