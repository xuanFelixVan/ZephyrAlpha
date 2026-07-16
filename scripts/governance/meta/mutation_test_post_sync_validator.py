# [BLUEPRINT] MOD-DATABASE | docs/03_modules/_cross_layer/database/blueprint.md | §task-system
# [MODULE] scripts.governance.meta.mutation_test_post_sync_validator
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] (none — stdlib only)
# [CONSUMERS] CI 门禁 / 手动回归
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 只读不修改真源 post_sync_validator.py（变异写入临时副本）；mutation score < THRESHOLD 返回非 0 阻断 CI；机械注入与 AI 盲区正交——打破"AI 写 Gate + AI 验 Gate"的自指悖论
# [MODIFY-GUARD] 新增变异必须对应一个真实校验分支；find 字符串必须在真源中唯一
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无异常抛出——变异应用失败记为 SETUP_ERROR 并跳过；阈值不达标返回 1
# [TESTS] 自身即测试（oracle: tests/governance/shared/test_post_sync_validation.py 36 场景）
# [TTL] permanent
"""
mutation_test_post_sync_validator.py — SSoT 变异测试（独立 oracle）

目的：机械注入源码变异到 post_sync_validator.py 的副本，复用
tests/governance/shared/test_post_sync_validation.py（36 场景）作 oracle，统计 mutation
score（被 oracle 杀死的变异 / 总变异）。打破自指悖论——AI 写的 Gate 与 AI 写的
测试可能共享盲区，但机械注入的变异与 AI 盲区正交，能暴露 oracle 不足。

机制（per mutant）：
  1. 读真源 → 字符串替换注入变异 → 写临时副本
  2. 设环境变量 PSV_UNDER_TEST=临时副本路径（test_post_sync_validation.py 的 seam）
  3. 跑 `python -m pytest tests/governance/shared/test_post_sync_validation.py -q`
     - exit 0 = 全 PASS = oracle 未察觉变异 → 变异 SURVIVED（假阴性暴露）
     - exit ≠ 0 = 有 FAIL = oracle 杀死变异 → KILLED
  4. 清理临时副本

阈值：mutation_score = killed / applicable >= 0.80 视为 PASS。
低于阈值返回 1（阻断 CI），并打印 survived 变异清单供加固 oracle。

用法:
    python scripts/governance/meta/mutation_test_post_sync_validator.py
    python scripts/governance/meta/mutation_test_post_sync_validator.py --threshold 0.80
    python scripts/governance/meta/mutation_test_post_sync_validator.py --list

历史根因：D-SIGNAL 改名 20 卡死锁事故——建卡 AI 臆造 apply_depgraph.py --diagnose，
而既有校验/测试未能拦截。变异测试验证当前 oracle 是否真能拦截这类机械扰动。
"""

from __future__ import annotations

__manifest__ = """
args: []
description: mutation_test_post_sync_validator.py — SSoT 变异测试（独立 oracle）
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

# ---- 路径 ---------------------------------------------------------------
# 治本(2026-06-30): REPO_ROOT 真源来自 _shared.constants, 消除 parents[N] 硬编码
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT as _REPO_ROOT  # noqa: E402

_SSoT_PATH = _REPO_ROOT / "src" / "zephyr" / "governance" / "post_sync_validator.py"
_TEST_PATH = _REPO_ROOT / "tests" / "unit" / "test_post_sync_validation.py"
_SEAM_ENV = "PSV_UNDER_TEST"  # 与 test_post_sync_validation.py 约定的 seam 名

DEFAULT_THRESHOLD = 0.80  # noqa: gate-vocab  治本(ARCH-036 P3-A5): 变异测试相似度判断阈值，测试工具专用非系统阈值


# ---- 变异目录 -----------------------------------------------------------
# 每个变异 = (mid, 描述, find, replace)。find 必须在真源中唯一出现一次。
# 变异锚定 SSoT 的关键校验分支；新增/删除 SSoT 分支时须同步维护本目录。
@dataclass
class Mutation:
    mid: str
    desc: str
    find: str
    replace: str


MUTATIONS: list[Mutation] = [
    Mutation(
        "M01",
        "flag 提取 split[0]→[-1]（破坏 --flag=value 解析）",
        "flags = [t.split(\"=\")[0] for t in parts if t.startswith(\"--\")]",
        "flags = [t.split(\"=\")[-1] for t in parts if t.startswith(\"--\")]",
    ),
    Mutation(
        "M02",
        "missing 判定 not in→in（反转：已注册 flag 误报缺失）",
        "    missing = [f for f in flags if f not in help_text]",
        "    missing = [f for f in flags if f in help_text]",
    ),
    Mutation(
        "M03",
        "脚本存在性 not p.exists()→p.exists()（反转：存在文件被拒）",
        "    if not p.exists():\n        return f\"脚本不存在: {script_path}（解析为 {p}）\"",
        "    if p.exists():\n        return f\"脚本不存在: {script_path}（解析为 {p}）\"",
    ),
    Mutation(
        "M04",
        "禁用 pytest/py_compile 跳过（return None→pass）",
        "            return None  # pytest/py_compile flag 由模块自身管理，跳过",
        "            pass  # MUTATED: pytest-skip disabled",
    ),
    Mutation(
        "M05",
        "超时分支 return None→return reason（误杀慢脚本）",
        "    except (subprocess.TimeoutExpired, Exception):\n        # --help 超时或异常无法校验，视为通过（不阻断）\n        return None",
        "    except (subprocess.TimeoutExpired, Exception):\n        # --help 超时或异常无法校验，视为通过（不阻断）\n        return \"MUTATED: 超时视为失败\"",
    ),
    Mutation(
        "M06",
        "if missing→if False（永不拒绝臆造 flag）",
        "    if missing:",
        "    if False:  # MUTATED: 永不拒绝",
    ),
    Mutation(
        "M07",
        "script_path is None→is not None（反转：有 .py 命令直接放行）",
        "    if script_path is None:\n        # 非 .py 命令（echo/git 等），无法内省，跳过\n        return None",
        "    if script_path is not None:\n        # 非 .py 命令（echo/git 等），无法内省，跳过\n        return None",
    ),
    Mutation(
        "M08",
        "链式拆分 re.split→[cmd]（不拆分 && / || / 换行）",
        "    sub_cmds = re.split(r\"\\s*(?:&&|\\|\\||\\n)\\s*\", cmd.strip())",
        "    sub_cmds = [cmd.strip()]  # MUTATED: 不拆分链式",
    ),
    Mutation(
        "M09",
        "if not flags→if flags（反转：有 flag 反而放行）",
        "    if not flags:\n        return None",
        "    if flags:\n        return None  # MUTATED: 有 flag 放行",
    ),
    Mutation(
        "M10",
        "flag 边界 startswith('--')→startswith('-')（单短横误判为 flag）",
        't.startswith("--")',
        't.startswith("-")',
    ),
    Mutation(
        "M11",
        "--help 超时阈值 15s→0.001s（强制超时→全部跳过 flag 校验）",
        "            timeout=15,",
        "            timeout=0.001,  # MUTATED: 强制超时",
    ),
    Mutation(
        "M12",
        "returncode != 0→== 0（反转：--help 成功反而跳过 flag 校验）",
        "    if result.returncode != 0:\n        # --help 自身失败（脚本可能有 import 错误等），跳过 flag 校验\n        return None",
        "    if result.returncode == 0:\n        # --help 自身失败（脚本可能有 import 错误等），跳过 flag 校验\n        return None",
    ),
    Mutation(
        "M13",
        "链式遍历 sub_cmds→sub_cmds[:1]（只校验首条子命令）",
        "    for sub in sub_cmds:",
        "    for sub in sub_cmds[:1]:  # MUTATED: 只校验首条",
    ),
    Mutation(
        "M14",
        "移除引号 strip（引号路径无法解析）",
        "        parts = [t.strip(\"'\\\"\") for t in shlex.split(cmd, posix=False)]",
        "        parts = shlex.split(cmd, posix=False)  # MUTATED: 不 strip 引号",
    ),
    # === W3 孪生字段扩展（M15-M17，杀灭由 R28-R36 守门）===
    Mutation(
        "M15",
        "rollback 长度阈值 <→>（过短反而通过，R32 杀灭）",
        "    if len(stripped) < _ROLLBACK_MIN_LENGTH:",
        "    if len(stripped) > _ROLLBACK_MIN_LENGTH:  # MUTATED: 反转阈值",
    ),
    Mutation(
        "M16",
        "禁用 rollback python 存在性检查（不存在的脚本通过，R35 杀灭）",
        "    for match in _PY_INVOCATION_RE.finditer(text):",
        "    for match in []:  # MUTATED: 跳过 py 校验",
    ),
    Mutation(
        "M17",
        "validate_post_sync_specific 不再委托（臆造 flag 通过，R29 杀灭）",
        "    return validate_post_sync_command(cmd, repo_root)",
        "    return None  # MUTATED: specific 不再委托",
    ),
]


# ---- 结果 ---------------------------------------------------------------
@dataclass
class MutantResult:
    mid: str
    desc: str
    outcome: str  # KILLED | SURVIVED | SETUP_ERROR
    detail: str = ""


@dataclass
class RunReport:
    killed: list[MutantResult] = field(default_factory=list)
    survived: list[MutantResult] = field(default_factory=list)
    setup_errors: list[MutantResult] = field(default_factory=list)

    @property
    def applicable(self) -> int:
        return len(self.killed) + len(self.survived)

    @property
    def score(self) -> float:
        denom = self.applicable
        return (len(self.killed) / denom) if denom else 0.0


# ---- 核心逻辑 -----------------------------------------------------------
def _apply_mutation(source: str, mut: Mutation) -> tuple[str | None, str]:
    """对源码应用变异。返回 (变异后源码 | None, 说明)。

    find 必须在源码中恰好出现一次；否则视为 SETUP_ERROR。
    """
    count = source.count(mut.find)
    if count == 0:
        return None, f"find 未命中（变异锚点已漂移，需同步维护变异目录）"
    if count > 1:
        return None, f"find 命中 {count} 处（非唯一，需扩大上下文）"
    return source.replace(mut.find, mut.replace), "ok"


def _run_oracle(mutated_path: Path) -> tuple[bool, str]:
    """跑 24 场景 oracle 指向变异副本。

    返回 (killed, detail)。killed=True 表示 oracle 检出变异（有测试 FAIL）。
    """
    env = os.environ.copy()
    env[_SEAM_ENV] = str(mutated_path)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(_TEST_PATH), "-q",
             "--no-header", "--tb=line"],
            capture_output=True,
            text=True,
            cwd=str(_REPO_ROOT),
            env=env,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return True, "oracle 超时（视为 killed，避免误判 survived）"
    killed = result.returncode != 0
    # 取末尾几行作 detail
    tail = (result.stdout or "").strip().splitlines()[-3:]
    detail = " | ".join(tail) if tail else f"exit={result.returncode}"
    return killed, detail


def run_all(threshold: float = DEFAULT_THRESHOLD) -> tuple[RunReport, int]:
    """运行全部变异。返回 (报告, 退出码)。"""
    if not _SSOt_PATH.exists():
        print(f"[FATAL] SSoT 真源不存在: {_SSOt_PATH}", file=sys.stderr)
        return RunReport(), 2
    if not _TEST_PATH.exists():
        print(f"[FATAL] oracle 测试不存在: {_TEST_PATH}", file=sys.stderr)
        return RunReport(), 2

    source = _SSOt_PATH.read_text(encoding="utf-8")
    report = RunReport()
    tmp_files: list[Path] = []

    print(f"\n[MUTATION] SSoT={_SSOt_PATH.relative_to(_REPO_ROOT)}", file=sys.stderr)
    print(f"[MUTATION] oracle={_TEST_PATH.relative_to(_REPO_ROOT)}", file=sys.stderr)
    print(f"[MUTATION] 变异数={len(MUTATIONS)} 阈值={threshold:.0%}\n", file=sys.stderr)

    for mut in MUTATIONS:
        print(f"  [{mut.mid}] {mut.desc} ...", end=" ", flush=True, file=sys.stderr)
        mutated, msg = _apply_mutation(source, mut)
        if mutated is None:
            print(f"SETUP_ERROR ({msg})", file=sys.stderr)
            report.setup_errors.append(MutantResult(mut.mid, mut.desc, "SETUP_ERROR", msg))
            continue

        fd, tmp_path = tempfile.mkstemp(suffix=f"_{mut.mid}_mutant.py", prefix="_psv_mut_")
        tmp = Path(tmp_path)
        tmp.write_text(mutated, encoding="utf-8")
        os.close(fd)
        tmp_files.append(tmp)

        killed, detail = _run_oracle(tmp)
        outcome = "KILLED" if killed else "SURVIVED"
        marker = "✅" if killed else "❌"
        print(f"{marker} {outcome} ({detail})", file=sys.stderr)
        result = MutantResult(mut.mid, mut.desc, outcome, detail)
        if killed:
            report.killed.append(result)
        else:
            report.survived.append(result)

    # 清理
    for t in tmp_files:
        try:
            t.unlink()
        except OSError:
            pass

    return report, _finalize(report, threshold)


def _finalize(report: RunReport, threshold: float) -> int:
    """打印汇总并返回退出码。"""
    print(file=sys.stderr)
    print(
        f"  killed={len(report.killed)} survived={len(report.survived)} "
        f"setup_errors={len(report.setup_errors)} applicable={report.applicable}",
        file=sys.stderr,
    )
    if report.survived:
        print(f"\n  ⚠ SURVIVED 变异（oracle 盲区，建议补场景）：", file=sys.stderr)
        for r in report.survived:
            print(f"    [{r.mid}] {r.desc}", file=sys.stderr)
            print(f"          {r.detail}", file=sys.stderr)
    if report.setup_errors:
        print(f"\n  ⚠ SETUP_ERROR 变异（锚点漂移，需同步变异目录）：", file=sys.stderr)
        for r in report.setup_errors:
            print(f"    [{r.mid}] {r.desc} — {r.detail}", file=sys.stderr)

    score = report.score
    verdict = "PASS" if score >= threshold else "FAIL"
    print(
        f"\n  mutation_score = {len(report.killed)}/{report.applicable} "
        f"= {score:.1%} (阈值 {threshold:.0%}) → {verdict}",
        file=sys.stderr,
    )
    return 0 if score >= threshold else 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="post_sync_validator 变异测试（独立 oracle，打破自指悖论）"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=f"mutation score 通过阈值（默认 {DEFAULT_THRESHOLD}）",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="列出变异目录后退出（不执行）",
    )
    args = parser.parse_args()

    if args.list:
        for mut in MUTATIONS:
            print(f"  [{mut.mid}] {mut.desc}")
        print(f"\n共 {len(MUTATIONS)} 个变异", file=sys.stderr)
        return

    _, exit_code = run_all(threshold=args.threshold)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
