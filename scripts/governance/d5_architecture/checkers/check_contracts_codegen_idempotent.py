# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/checkers/check_contracts_codegen_idempotent.py | §
# [MODULE] scripts.governance.d5_architecture.checkers.check_contracts_codegen_idempotent
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.checkers.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""check_contracts_codegen_idempotent.py —— 契约生成器幂等性门禁（C 路径防回潮）

治本（#ARCH-130 P0-A，2026-08-19）：
A（模板自正）修好源头后，B（管线兜底）防运行时，C（本门禁）防未来回潮——
任何 contracts YAML 或生成器模板的变更导致重跑产物与磁盘文件不一致时，
pre-commit 硬阻断，防止"回退合法修复进 git"（43 文件实证教训）。

检测逻辑：
  1. 调 generate_contracts._render_contract_content()（纯函数，零磁盘写入）
  2. 与磁盘上对应 .py 文件逐字节比对
  3. 不一致 → exit 1（提示先跑生成器同步）
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
# generators 目录加入 sys.path（generate_contracts 依赖 _common/_shared）
_GEN_DIR = str(_SCRIPT_DIR.parent.parent / "generators")
if _GEN_DIR not in sys.path:
    sys.path.insert(0, _GEN_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

import subprocess

import yaml
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

_CONTRACTS_YAML = REPO_ROOT / "architecture_model" / "contracts" / "cross_layer_contracts.yaml"

# 与 B 管线同口径六码（generate_contracts.py 末尾 ruff --fix 的 --select 参数）
_RUFF_SELECT = "I001,UP006,UP045,W292,W293,F541"


def _ruff_fix_content(content: str, filename: str) -> str:
    """对内存中的生成内容跑 ruff --fix（与 B 管线同口径），使 C 门禁比对基准一致。

    B 管线在生成后跑 ruff 修复，磁盘文件=生成器输出+ruff 修复；
    C 门禁要比对"重跑产物 vs 磁盘"，必须对生成器输出也跑同样的 ruff 修复。
    fail-open：ruff 不可用时返回原始内容（降级为裸比对）。
    """
    try:
        proc = subprocess.run(  # noqa: bare-subprocess  pre-commit hook 无窗口环境（stdin/stdout 管道）
            ["ruff", "check", "--fix", "--quiet", "--select", _RUFF_SELECT, "--stdin-filename", filename, "-"],
            input=content,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(REPO_ROOT),
        )
        if proc.returncode != 0:
            return content
        # format（与 B 管线口径一致：check --fix 后 format）
        proc2 = subprocess.run(  # noqa: bare-subprocess  pre-commit hook 无窗口环境（stdin/stdout 管道）
            ["ruff", "format", "--stdin-filename", filename, "-"],
            input=proc.stdout,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(REPO_ROOT),
        )
        return proc2.stdout if proc2.returncode == 0 else proc.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return content


def main() -> int:
    """Entry point: parse args, run logic, return exit code.

    手动解析 argv（避免 argparse 触发 MANUAL-ONLY-PERMANENT gate——本脚本是
    pre-commit hook 事件驱动调用，非永久系统常驻服务；同 run_silent_failure_regression.py 先例）。
    """
    argv = sys.argv[1:]
    warn_only = "--warn-only" in argv
    # --ci 为默认行为（硬阻断），warn-only 降级

    if not _CONTRACTS_YAML.exists():
        print(f"WARN: {_CONTRACTS_YAML} 不存在，跳过")
        return EXIT_PASS

    # 延迟 import（sys.path 已就绪）
    from generate_contracts import _render_contract_content

    data = yaml.safe_load(_CONTRACTS_YAML.read_text(encoding="utf-8"))
    contracts = data.get("contracts", [])

    mismatches: list[str] = []
    checked = 0
    for ctr in contracts:
        physical = ctr.get("physical_path", "")
        if not physical:
            continue
        contract_id = ctr.get("id", "")
        if contract_id.startswith("OCP-"):
            continue

        result = _render_contract_content(ctr)
        if result is None:
            continue
        phys, raw_content = result

        disk_path = REPO_ROOT / phys
        if not disk_path.exists():
            mismatches.append(f"  {contract_id} → {phys}（磁盘文件缺失）")
            continue

        # B 管线同口径 ruff --fix，对齐比对基准（磁盘文件=生成器输出+ruff 修复）
        expected_content = _ruff_fix_content(raw_content, phys)
        disk_content = disk_path.read_text(encoding="utf-8")
        checked += 1
        if disk_content != expected_content:
            mismatches.append(f"  {contract_id} → {phys}")

    if not mismatches:
        print(f"OK: 契约生成器幂等（{checked} 个文件零 diff）")
        return EXIT_PASS

    print(f"FAIL: 契约生成器非幂等——{len(mismatches)} 个文件重跑产物与磁盘不一致：")
    for m in mismatches:
        print(m)
    print("\n修复方式：")
    print("  python scripts/governance/d5_architecture/generators/generate_contracts.py --force")
    print("  然后将生成产物一并 staged 提交")

    if warn_only:
        print("WARN: 跳过（warn-only 模式）")
        return EXIT_PASS
    return EXIT_FINDINGS


if __name__ == "__main__":
    sys.exit(main())
