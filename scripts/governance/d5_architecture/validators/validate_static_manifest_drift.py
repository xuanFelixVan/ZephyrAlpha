# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_static_manifest_drift.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_static_manifest_drift
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.__init__
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
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
validate_static_manifest_drift.py — GATE-21 静态清单漂移阻断

顺序运行所有静态清单生成器的 --check 模式。自动生成版与磁盘版任何不一致
均触发硬失败（exit 1）。

权威依据：AGENTS.md 运维红线「静态清单禁手工维护」——任何"条目列表 + 计数"清单
必须由生成器产出（Type A：从代码/配置派生）或以 schema 为输入（Type B），
禁止手工维护条目（手工维护必然与真源漂移）。

检查清单：
  1. script_manifest.yaml — via generate_script_manifest.py --check
  2. gate_registry.yaml   — via generate_gate_registry.py --check

治本（2026-07-17）：
  - 清理代码退化结构（双 docstring / 重复 import / 游离 shebang / __manifest__ 块）
  - CHECKS 补齐 gate_registry.yaml（原仅 script_manifest.yaml，漏检门禁登记表漂移）
  - 输出消息 GATE-19 → GATE-21（2026-06-30 簇3合并重命名后消息未同步）
  - §6.16 断头引用 → §6.2 → §6.3（AGENTS.md 原无 §6.16，2026-07-17 治本补建 §6.2，2026-07-20 因新增临时文件分类存放铁律顺延为 §6.3）
  - 自举 sys.path 含 src/ + 子进程注入 PYTHONPATH=src，消除对调用方环境的依赖
    （原 validator 在未设 PYTHONPATH=src 的环境下崩溃 ModuleNotFoundError: No module named 'zephyr'）

Usage:
    python validate_static_manifest_drift.py --check
"""

from __future__ import annotations

__manifest__ = """
args:
- {flag: --check, type: bool, description: "检测漂移，不一致时 exit 1"}
description: GATE-21 静态清单漂移阻断——顺序运行所有静态清单生成器的 --check 模式，自动生成版与磁盘版不一致即硬失败
dimensions:
- D1
- D5
priority: P1
timeout_seconds: 120
warn_only: false
"""

import os
import subprocess
import sys
from pathlib import Path

# 自举 sys.path（顺序敏感）：
#   1. scripts/governance/ —— import _shared.*
#   2. <repo_root>/src      —— _shared.constants 内部 import zephyr.*（治本：原缺此行）
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists())
_REPO_ROOT = _GOV_DIR.parent.parent  # scripts/governance -> scripts -> <repo_root>
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))
_SRC_DIR = _REPO_ROOT / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from _shared.constants import EXIT_FINDINGS, EXIT_PASS  # noqa: E402
from _shared.encoding import ensure_utf8_stdout  # noqa: E402

ensure_utf8_stdout()

# 子进程环境：生成器 import _shared.constants → import zephyr，需 src/ 在 PYTHONPATH。
# 治本：原 subprocess.run 未传 env，子进程在未设 PYTHONPATH=src 的环境下崩溃。
_pp_parts = [str(_SRC_DIR)]
if os.environ.get("PYTHONPATH"):
    _pp_parts.append(os.environ["PYTHONPATH"])
_SUBPROCESS_ENV = {**os.environ, "PYTHONPATH": os.pathsep.join(_pp_parts)}

GENERATORS_DIR = _GOV_DIR / "generators"
SYNCERS_DIR = _GOV_DIR / "d5_architecture" / "syncers"

CHECKS = [
    {
        "name": "script_manifest.yaml",
        "cmd": [sys.executable, str(GENERATORS_DIR / "generate_script_manifest.py"), "--check"],
        "fix": [sys.executable, str(GENERATORS_DIR / "generate_script_manifest.py")],
    },
    {
        "name": "gate_registry.yaml",
        "cmd": [sys.executable, str(GENERATORS_DIR / "generate_gate_registry.py"), "--check"],
        "fix": [sys.executable, str(GENERATORS_DIR / "generate_gate_registry.py")],
    },
    # 注（2026-08-19 退库终态跟进）：原 blueprint_registry.yaml 检查已摘除——
    # 该文件经 #ARCH-BP-REGISTRY-DELETION-001 后续裁定正式派生退库（commit 03df6215e8：
    # 100% 可由 frontmatter 重生成=派生物，盘文件删除+.gitignore 入列+
    # check_no_commit_derived 扩列防重新跟踪）。文件缺失从"事故"翻转为"决策终态"，
    # dry-run 缺文件即 exit 2 的防删检测已过时（防重新跟踪由 check_no_commit_derived 承接）；
    # triple_alignment 消费侧已改 frontmatter 现算回退（同批治本）。
    {
        "name": ".importlinter forbidden_modules",
        "cmd": [sys.executable, str(GENERATORS_DIR / "generate_importlinter.py"), "--check"],
        "fix": [sys.executable, str(GENERATORS_DIR / "generate_importlinter.py")],
    },
    # 册内自洽（2026-09-24 本包补，真源=docs/_working/audit_fix/lanes/L4_registry_counts/）：
    # 上面 gate_registry 的 --check 只比对"声明计数 vs 生成器算出的计数"，从不比对
    # "声明计数 vs 在册段实际长度"⇒ 队列落地把条目推进了、标量钉在旧值时检测器全盲
    # （实测 total_gates=174 而 gates 实 180 带病 2 天，GATE-21 在册却报不出）。
    # 现按 audit 尺Q 的口径把自洽检查立成常驻闸。作用域先只点两台（含尺Q 实测出的
    # 两台失真），扩到全 catalogs 扫是加文件名一行的事——本轮不扩面，避免在其他会话
    # 批次在飞时把无关提交打红（判读见 L4 挖矿簿 §3）。
    {
        "name": "gate_registry.yaml (declared total == section length)",
        "selfcheck": {
            "path": "docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml",
            "pairs": {"total_gates": "gates"},
        },
        "fix": [sys.executable, str(GENERATORS_DIR / "generate_gate_registry.py")],
    },
    {
        "name": "rule_catalog_registry.yaml (declared total == section length)",
        "selfcheck": {
            "path": "docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml",
            "pairs": {"total_files": "files"},
        },
        "fix": [
            sys.executable,
            str(_GOV_DIR / "d3_metadata" / "generate_rule_catalog.py"),
        ],
    },
]


def derived_total_pairs() -> dict[str, dict[str, str]]:
    """册名 → {声明标量: 集合段}——GATE-21 自洽台的配对对外读口。

    存在的唯一理由＝让"检测口径"与"落地侧自愈口径"可被一把尺直接比对
    （见 tests/governance/test_audit_fix_lanes_rulers.py 的配对一致性尺）。
    """
    out: dict[str, dict[str, str]] = {}
    for chk in CHECKS:
        sc = chk.get("selfcheck") or {}
        pairs = sc.get("pairs")
        if pairs:
            out[Path(str(sc.get("path", ""))).name] = dict(pairs)
    return out


def _run_selfcheck(item: dict) -> str | None:
    """声明计数 vs 同名段实际长度；不一致返回漂移描述，一致返回 None。

    刻意独立于生成器实现（生成器 --check 的口径是"磁盘 vs 生成"，本函数是
    "磁盘内部自洽"——两半合起来才是完整的静态清单失真定义）。
    """
    import yaml  # noqa: PLC0415

    p = _REPO_ROOT / item["selfcheck"]["path"]
    if not p.is_file():
        return f"{p.name} 不存在（自洽检查无从判定）"
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception as exc:  # noqa: BLE001 — 解析失败=失真，不得静默放行
        return f"{p.name} YAML 解析失败: {type(exc).__name__}: {exc}"
    for key, section in item["selfcheck"]["pairs"].items():
        declared = data.get(key)
        actual = data.get(section)
        if declared is None or not isinstance(actual, (list, dict)):
            return f"{p.name} 缺 {key} 或段 {section} 非集合（自洽键漂移）"
        if int(declared) != len(actual):
            return f"DRIFT: {p.name} 声明 {key}={declared} ≠ {section} 实际 {len(actual)}"
    return None


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    # --check=只判定（pre-commit 正门用）；--auto-fix=先跑各台的 fix 命令再复判定
    # （post-commit reconciler 的 D5_static_manifest 通道用，reconciler._fix_yaml_append
    #  一直按这个契约传旗，本脚本此前"忽略其他参数"＝映射到空操作，故漂移能带病两天）。
    auto_fix = "--auto-fix" in sys.argv
    failures = []
    for check in CHECKS:
        if auto_fix and check.get("fix"):
            fr = subprocess.run(
                check["fix"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=_SUBPROCESS_ENV,
                cwd=str(_REPO_ROOT),
            )
            tail = (fr.stdout + fr.stderr).strip().splitlines()
            print(f"AUTO-FIX [{check['name']}] rc={fr.returncode}: {(tail[-1] if tail else '')[:160]}")
        if "selfcheck" in check:
            drift = _run_selfcheck(check)
            if drift:
                failures.append(f"FAIL [{check['name']}]: {drift}")
            else:
                print(f"PASS [{check['name']}]")
            continue
        result = subprocess.run(
            check["cmd"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=_SUBPROCESS_ENV,
            cwd=str(_REPO_ROOT),
        )
        if result.returncode != 0:
            msg = (result.stdout + result.stderr).strip()
            failures.append(f"FAIL [{check['name']}]: {msg}")
        else:
            print(f"PASS [{check['name']}]: {result.stdout.strip()}")

    if not failures:
        print("\nGATE-21 PASS: all static manifests are consistent with their sources.")
        sys.exit(EXIT_PASS)

    print(f"\nGATE-21 FAIL: {len(failures)} static manifest(s) have drifted:\n")
    for f in failures:
        print(f"  - {f}")
    print("修复（本包补的通道）：python " + __file__.replace(chr(92), "/") + " --auto-fix")
    print("\nFix: 运行对应生成器（不带 --check）重新生成，例如：")
    print("  python scripts/governance/generators/generate_script_manifest.py")
    print("  python scripts/governance/generators/generate_gate_registry.py")
    print("  python scripts/governance/d5_architecture/syncers/sync_registry_from_blueprints.py --write")
    sys.exit(EXIT_FINDINGS)


if __name__ == "__main__":
    main()
