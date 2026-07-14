# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/checkers/check_contract_code_drift.py | §
# [MODULE] scripts.governance.d5_architecture.checkers.check_contract_code_drift
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.checkers.__init__
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
"""check_contract_code_drift.py —— 契约-代码双写漂移阻断（盲点 C2 修复）

对标：AGENTS.md §6.5 契约-代码同步铁律
      盲点 C2：AI 改 YAML 忘 codegen → 契约与代码漂移 → 硬阻断

检测逻辑：
  1. 计算 cross_layer_contracts.yaml 和所有生成 .py 文件的 SHA256
  2. 与作者签名的 _contract_sso.yml 中记录的上次 codegen 快照对比
  3. YAML 变更但 .py 未同步 → exit 1
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT

ensure_utf8_stdout()

import os

__manifest__ = """
args: []
description: 契约-代码双写漂移阻断——YAML修改后强制codegen一致，CI硬阻断
dimensions:
- D5
priority: P0
timeout_seconds: 30
warn_only: false
"""

import argparse
import hashlib
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

_CONTRACTS_YAML = (
    REPO_ROOT
    / "architecture_model"
    / "contracts"
    / "cross_layer_contracts.yaml"
)
_CONTRACT_OUT_DIR = REPO_ROOT / "src" / "zephyr" / "shared" / "contracts"
_SNAPSHOT_FILE = _CONTRACT_OUT_DIR / "_codegen_snapshot.txt"


def _sha256(path: Path) -> str:
    """_sha256 implementation."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _build_snapshot() -> str:
    """_build_snapshot implementation."""
    lines = [f"yaml {_sha256(_CONTRACTS_YAML)}"]
    if _CONTRACT_OUT_DIR.is_dir():
        for py_file in sorted(_CONTRACT_OUT_DIR.glob("*.py")):
            if py_file.name.startswith("_"):
                continue
            lines.append(f"{py_file.name} {_sha256(py_file)}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--ci", action="store_true")
    parser.add_argument("--warn-only", action="store_true")
    parser.add_argument("--freeze", action="store_true", help="冻结当前快照")
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args()

    if not _CONTRACTS_YAML.exists():
        print(f"WARN: {_CONTRACTS_YAML} 不存在，跳过")
        return EXIT_PASS
    current = _build_snapshot()

    if args.freeze:
        atomic_write_safe(_SNAPSHOT_FILE, current)
        print("OK: 契约快照已冻结")
        return EXIT_PASS
    if not _SNAPSHOT_FILE.exists():
        print("INFO: 无快照基线——运行 --freeze 建立基线后启用漂移检测")
        return EXIT_PASS
    baseline = _SNAPSHOT_FILE.read_text(encoding="utf-8")

    if current == baseline:
        print("OK: 契约-代码一致（无漂移）")
        return EXIT_PASS
    print("FAIL: 契约-代码漂移——以下文件与基线不一致：")
    cur_lines = current.strip().split("\n")
    base_lines = baseline.strip().split("\n")
    cur_map = {}
    for line in cur_lines:
        parts = line.split(" ", 1)
        if len(parts) == 2:
            cur_map[parts[0]] = parts[1]
    base_map = {}
    for line in base_lines:
        parts = line.split(" ", 1)
        if len(parts) == 2:
            base_map[parts[0]] = parts[1]

    for key in sorted(set(cur_map) | set(base_map)):
        cv = cur_map.get(key, "<缺失>")
        bv = base_map.get(key, "<缺失>")
        if cv != bv:
            print(f"  {key}: 基线={bv[:12]} 当前={cv[:12]}")

    print("\n修复方式：")
    print("  1. 运行 scripts/governance/d5_architecture/generate_contracts.py")
    print("  2. 运行本脚本 --freeze 冻结新快照")

    if args.warn_only:
        print("WARN: 跳过（warn-only 模式）")
        return EXIT_PASS
    return EXIT_FINDINGS


if __name__ == "__main__":
    sys.exit(main())
