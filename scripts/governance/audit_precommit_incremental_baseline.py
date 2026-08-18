# [BLUEPRINT] MOD-INF-005 | scripts/governance/audit_precommit_incremental_baseline.py | §oneoff
# [MODULE] scripts.governance.audit_precommit_incremental_baseline
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d3_metadata.check_naming_convention
# [CONSUMERS] manual (oneoff 审计基线生成)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读审计——不修改任何文件，只生成基线报告
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=基线生成成功; exit 1=审计发现违规（正常，历史技术债）; exit 2=脚本错误
# [TESTS] oneoff 脚本，无单测（一次性审计工具）
# [A_module] module_id=MOD-INF-005 | layer=script | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""oneoff 审计基线生成器——#ARCH-PRECOMMIT-INCREMENTAL 历史违规快照。

用途（Task 6，2026-08-06）：
    增量/审计分离后，全仓历史 warn-only 违规归档为技术债。本脚本生成基线快照，
    记录"截至 2026-08-06 有多少历史违规"，作为后续 CI/manual 清零的参考点。

    验证 trae_084 铁律：
      - 增量守门（--check-new）只拦 staged 新增，不拦历史违规
      - 全仓审计（--warn-only --scan）能检出历史违规
      - 显示二元化（actual_blocking vs warn_only_count）正常工作

运行：
    python scripts/governance/audit_precommit_incremental_baseline.py

输出：
    控制台摘要 + .runtime/gate_audit/precommit_incremental_baseline.json
"""

from __future__ import annotations

__manifest__ = """
args: []
description: oneoff 审计基线生成器——#ARCH-PRECOMMIT-INCREMENTAL 历史违规快照。
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import json
import re
import subprocess
import sys
import time
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT  # noqa: E402

NAMING_GATE = REPO_ROOT / "scripts" / "governance" / "d3_metadata" / "check_naming_convention.py"
FRONTMATTER_GATE = REPO_ROOT / "scripts" / "governance" / "d3_metadata" / "check_frontmatter_metadata.py"
BASELINE_OUT = REPO_ROOT / ".runtime" / "gate_audit" / "precommit_incremental_baseline.json"


def _run(cmd: list[str], timeout: int = 300) -> tuple[int, str]:
    """运行命令，返回 (exit_code, stdout+stderr)。"""
    try:
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=timeout,
        )
        return r.returncode, (r.stdout + r.stderr)
    except subprocess.TimeoutExpired:
        return 2, f"TIMEOUT after {timeout}s"
    except Exception as e:  # noqa: BLE001
        return 2, str(e)


def _parse_naming_audit(output: str) -> dict:
    """解析命名审计输出，提取违规统计。"""
    result = {"actual_blocking": 0, "warn_only_count": 0, "n17_warnings": 0}
    m = re.search(r"总计 (\d+) 个阻断性命名违规", output)
    if m:
        result["actual_blocking"] = int(m.group(1))
    m = re.search(r"另有 (\d+) 个 warn-only", output)
    if m:
        result["warn_only_count"] = int(m.group(1))
    m = re.search(r"共 (\d+) 个 N-17 warning", output)
    if m:
        result["n17_warnings"] = int(m.group(1))
    return result


def _parse_frontmatter_audit(output: str) -> dict:
    """解析 frontmatter 审计输出，提取违规统计。"""
    result = {"files_checked": 0, "violations": 0, "passed": False}
    m = re.search(r"(\d+) files checked", output)
    if m:
        result["files_checked"] = int(m.group(1))
    if "PASS" in output:
        result["passed"] = True
    else:
        # 统计违规行数（[ERROR] / FAIL 等标记）
        result["violations"] = len(re.findall(r"\[ERROR\]|\bFAIL\b", output))
    return result


def main() -> int:
    """生成审计基线快照。"""
    print("=" * 70)
    print("#ARCH-PRECOMMIT-INCREMENTAL 审计基线生成器")
    print(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    baseline = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "arch_id": "#ARCH-PRECOMMIT-INCREMENTAL",
        "naming_audit": {},
        "frontmatter_audit": {},
        "ssot_validation": {},
    }

    # 1. 命名审计（--warn-only --scan）
    print("\n[1/3] 命名审计 (--warn-only --scan)...")
    code, out = _run([sys.executable, str(NAMING_GATE), "--warn-only", "--scan"], timeout=300)
    baseline["naming_audit"] = _parse_naming_audit(out)
    baseline["naming_audit"]["exit_code"] = code
    n = baseline["naming_audit"]
    print(f"  阻断性违规 (N-16): {n['actual_blocking']}")
    print(f"  warn-only 违规: {n['warn_only_count']}")
    print(f"  N-17 warnings: {n['n17_warnings']}")

    # 2. SSoT 一致性校验
    print("\n[2/3] SSoT 一致性校验 (--validate-ssot)...")
    code, out = _run([sys.executable, str(NAMING_GATE), "--validate-ssot"], timeout=60)
    baseline["ssot_validation"] = {
        "exit_code": code,
        "passed": code == 0,
        "output_tail": out.strip().split("\n")[-1] if out.strip() else "",
    }
    print(f"  {'✅ 通过' if code == 0 else '❌ 失败'}")

    # 3. Frontmatter 审计（--all-files）
    print("\n[3/3] Frontmatter 审计 (--all-files)...")
    code, out = _run([sys.executable, str(FRONTMATTER_GATE), "--all-files"], timeout=300)
    baseline["frontmatter_audit"] = _parse_frontmatter_audit(out)
    baseline["frontmatter_audit"]["exit_code"] = code
    f = baseline["frontmatter_audit"]
    print(f"  检查文件数: {f['files_checked']}")
    print(f"  违规数: {f['violations']}")
    print(f"  {'✅ 通过' if f['passed'] else '⚠️ 有违规'}")

    # 写入基线文件
    BASELINE_OUT.parent.mkdir(parents=True, exist_ok=True)
    with BASELINE_OUT.open("w", encoding="utf-8") as fh:
        json.dump(baseline, fh, ensure_ascii=False, indent=2)
    print(f"\n基线快照已写入: {BASELINE_OUT}")

    # 摘要
    print("\n" + "=" * 70)
    print("基线摘要（历史技术债，走 CI/manual 清零，不卡日常 commit）:")
    print(f"  命名: {n['actual_blocking']} 阻断 + {n['warn_only_count']} warn-only + {n['n17_warnings']} N-17")
    print(f"  SSoT: {'通过' if baseline['ssot_validation']['passed'] else '失败'}")
    print(f"  Frontmatter: {f['files_checked']} 文件, {f['violations']} 违规")
    print("=" * 70)

    # exit 1 表示有历史违规（正常，技术债），不是脚本错误
    return 0 if baseline["ssot_validation"]["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
