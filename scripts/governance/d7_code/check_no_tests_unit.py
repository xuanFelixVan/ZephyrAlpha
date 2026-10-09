# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/check_no_tests_unit.py | §
# [MODULE] scripts.governance.d7_code.check_no_tests_unit
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d7_code.__init__
# [CONSUMERS] .pre-commit-config.yaml hook gate-no-tests-unit
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 纯 stdlib；检测 staged .py/.md/.yaml/.yml 文件中 tests/unit/ 旧路径；含豁免清单；exit 0=pass / 1=findings / 2=error
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 永不抛异常——git 失败/I/O 异常降级为 exit 2 + stderr 提示
# [TESTS] tests/governance/test_check_no_tests_unit.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""check_no_tests_unit.py — 禁止 tests/unit/ 旧路径重引入检测（local 替代 pygrep）

裁定 #ARCH-PRECOMMIT-OFFLINE-001 Phase 3 治本：
原 .pre-commit-config.yaml 的 gate-no-tests-unit hook 使用 language: pygrep，
pygrep 是 pre-commit 内置语言，需要 pre-commit 工具运行——破坏离线可运行原则。

本脚本用纯 stdlib 等价替代，检测 staged 文件中 tests/unit/ 旧路径引用。

权威依据：tests/ 目录组织规范（pyproject.toml testpaths）——tests/unit/ 已扁平化为 tests/
真源声明：ARCH-029 漂移种子清理——6 轮 87 文件修复后，添加自动化 guard 防止重引入

exit codes: 0=pass, 1=findings(发现 tests/unit/ 引用), 2=error
"""

from __future__ import annotations

# noqa: m11-perm-manual-legitimate  M11豁免: pre-commit/周期审计按需调用的静态检查器，非常驻服务（裁定#354 --full-tree 审计由计划任务事件拉起）

__manifest__ = """
args: []
description: >
  检测 staged .py/.md/.yaml/.yml 文件中 tests/unit/ 旧路径引用。
  纯 stdlib 替代 language: pygrep（裁定 #ARCH-PRECOMMIT-OFFLINE-001）。
dimensions:
- D7
priority: P1
timeout_seconds: 10
warn_only: false
"""

import re
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS  # noqa: E402

# tests/unit/ 旧路径检测正则
_TESTS_UNIT_RE = re.compile(r"tests/unit/")

# 扫描的文件扩展名（对标原 .pre-commit-config.yaml files 字段）
_SCANNABLE_EXTS: frozenset[str] = frozenset({".py", ".md", ".yaml", ".yml"})

# 豁免清单（对标原 .pre-commit-config.yaml exclude 字段）
# 这些路径含 tests/unit/ 字符串是合法的（历史归档/规则文档说明）
_EXEMPT_PATH_PATTERNS = [
    re.compile(r"^_archive/"),
    re.compile(r"^scripts/_archive/"),
    re.compile(r"^scripts/.*/_archive/"),
    re.compile(r"^session_logs/"),
    re.compile(r"^data/"),
    re.compile(r"^reports/"),
    re.compile(r"^docs/01_policies_and_standards/rules/trae_0(28|34)_"),
    re.compile(r"^\.pre-commit-config\.yaml$"),
    re.compile(r"^AGENTS\.md$"),
    # 派生清单逐字引用各 gate 自述（含本 gate 描述中的 tests/unit/ 字面量），
    # 非旧路径引用——不自引用误伤（2026-08-14 script_manifest 重生成被本 gate 自咬实证）
    re.compile(r"^scripts/governance/script_manifest\.yaml$"),
    # 同类自咬：gate_registry.yaml 由生成器逐字收录本 gate 的 name/description（含 tests/unit/ 字面量），
    # 非旧路径引用（2026-08-17 AI-00 merge 全文扫描实证）
    re.compile(r"^docs/01_policies_and_standards/_registry/catalogs/gate_registry\.yaml$"),
    # 同类自咬：FMS 死引用棘轮基线册逐字收录全仓 docs 扫描到的死引用 token
    # （含 `tests/unit`/`tests/unit/` E3 类存量条目=棘轮收缩库存，非旧路径重引入；
    # 2026-09-27 st-fms-chief-20260927 C2 批落地实测误报）
    re.compile(r"^docs/01_policies_and_standards/_registry/catalogs/fms_deadref_baseline\.yaml$"),
    # 检测器自身必须字面含检测模式（正则/docstring/报错文案），自豁免
    re.compile(r"^scripts/governance/d7_code/check_no_tests_unit\.py$"),
    # --- 案卷普查册/机生清单类豁免（2026-10-09 st-chiefc-20261009 SD 车道平权扩容批）---
    # 案卷普查册/机生清单把历史路径（含 tests/unit/ 存量 token）作为记录对象/交割键逐字
    # 收录，属清单数据非旧路径重引入（同 fms_deadref_baseline 机生册先例；死信专案
    # 01_ledger §三受阻件两案实证：02_reference_census.md 普查册正文照录 1 处
    # tests/unit/=其记录对象本身、05_tests_restore_manifest.yaml 交割清单逐字收录被删
    # 测试树原路径=交割索引键）。
    # [复审期限 2027-01-09] D8 格式类规则：本批为期限豁免（留痕+复审期限，禁常态化），
    # 季度合并审计同窗（宪法 §4 内收判据 w5_1）复查命中率；零触发零消费即退役。
    # 收窄设计：仅豁免清单/册数据面（.md/.yaml/.yml/.json/.csv），普查/清单同名的 .py
    # 代码面照常扫描（代码里的 tests/unit/ 是活引用不是清单条目）。
    re.compile(r"census[^/]*\.(md|ya?ml|json|csv)$"),  # 普查册 *census*.{md,yaml,yml,json,csv}
    re.compile(r"manifest[^/]*\.(ya?ml|json|csv)$"),  # 机生清单 *manifest*.{yaml,yml,json,csv}
    re.compile(r"_data/[^/]*\.csv$"),  # 机生数据清单目录 _data/*.csv（当前扫描面外，防御扫描面扩展回归）
]


def _get_staged_files_for_path_scan() -> list[str]:
    """获取 staged 文件列表（新增/修改/重命名后）。"""
    try:
        r = subprocess.run(  # noqa: bare-subprocess  静态检查器读 git 状态,process_pool 在此场景不适用
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        print(f"[ERR] git diff 失败: {type(e).__name__}: {e}", file=sys.stderr)
        return []
    if r.returncode != 0:
        print(f"[ERR] git diff rc={r.returncode}: {r.stderr}", file=sys.stderr)
        return []
    return [f for f in r.stdout.strip().split("\n") if f]


def _get_tracked_files_for_path_scan() -> list[str]:
    """获取全 tracked 树文件列表（--full-tree 审计模式，裁定#354）。

    审计语义：历史存量对 staged-only 检测面永久不可见（#354 亲验），
    本模式扫描 git ls-files 全跟踪树暴露存量违规。默认 staged 面行为零变化。
    """
    try:
        r = subprocess.run(  # noqa: bare-subprocess  审计模式读 tracked 树,process_pool 在此场景不适用
            ["git", "ls-files"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        print(f"[ERR] git ls-files 失败: {type(e).__name__}: {e}", file=sys.stderr)
        return []
    if r.returncode != 0:
        print(f"[ERR] git ls-files rc={r.returncode}: {r.stderr}", file=sys.stderr)
        return []
    return [f for f in r.stdout.strip().split("\n") if f]


def _is_exempt(rel: str) -> bool:
    """判断文件是否在豁免清单中（POSIX 路径归一化）。"""
    normalized = rel.replace("\\", "/")
    for pattern in _EXEMPT_PATH_PATTERNS:
        if pattern.search(normalized):
            return True
    return False


def _is_scannable(rel: str) -> bool:
    """判断文件是否在扫描范围内（按扩展名过滤）。"""
    return Path(rel).suffix.lower() in _SCANNABLE_EXTS


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    import argparse

    parser = argparse.ArgumentParser(description="GATE-NO-TESTS-UNIT: 禁止 tests/unit/ 旧路径重引入")
    parser.add_argument(
        "--full-tree",
        action="store_true",
        help="审计模式：扫描全 tracked 树而非 staged 面（裁定#354 周期审计，默认 staged 面行为零变化）",
    )
    args = parser.parse_args()

    files = _get_tracked_files_for_path_scan() if args.full_tree else _get_staged_files_for_path_scan()
    if not files:
        return EXIT_PASS

    findings: list[str] = []
    for rel in files:
        if _is_exempt(rel):
            continue
        if not _is_scannable(rel):
            continue
        path = Path(rel)
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            print(f"[WARN] 跳过不可读文件 {rel}: {type(e).__name__}: {e}", file=sys.stderr)
            continue
        matches = _TESTS_UNIT_RE.findall(content)
        if matches:
            findings.append(f"  {rel}: 发现 {len(matches)} 处 tests/unit/ 旧路径引用")

    if findings:
        print("[ERR] 发现 tests/unit/ 旧路径引用（ARCH-029 防漂移）:")
        for f in findings:
            print(f)
        print("")
        print("修复：tests/unit/ 已扁平化为 tests/（tests/ 目录组织规范），")
        print("     将 tests/unit/xxx 改为 tests/xxx，然后 git add <file> 重新提交。")
        return EXIT_FINDINGS

    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
