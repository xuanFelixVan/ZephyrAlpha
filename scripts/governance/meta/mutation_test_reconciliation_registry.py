# [BLUEPRINT] MOD-INF-035 | .trae/documents/systemic_drift_root_cure_continuation_plan.md | §5.2 P3-T2
# [MODULE] scripts.governance.meta.mutation_test_reconciliation_registry
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] (none — stdlib only)
# [CONSUMERS] CI 门禁 / 手动回归（GATE-MUT 达标前手动，达标后事件驱动）
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 只读不修改真源 reconciliation_registry.py（变异写入临时副本）；mutation score < THRESHOLD 返回非 0 阻断；机械注入与 AI 盲区正交——打破"AI 写 Gate + AI 验 Gate"的自指悖论
# [MODIFY-GUARD] 新增变异必须对应 verify_reconciliation_registry.py 的一项不变量检查；find 字符串必须在真源中唯一
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无异常抛出——变异应用失败记为 SETUP_ERROR 并跳过；阈值不达标返回 1
# [TESTS] 自身即测试（oracle: scripts/governance/meta/verify_reconciliation_registry.py 6 项不变量）
# [A_module] module_id=MOD-GOV-mutation_test_rr | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""mutation_test_reconciliation_registry.py — ReconciliationRegistry SSoT 变异测试（P3-T2）

目的：机械注入源码变异到 ``reconciliation_registry.py`` 的副本，复用
``verify_reconciliation_registry.py``（P3-T1 产出的 6 项不变量 oracle）作 oracle，
统计 mutation score（被 oracle 杀死的变异 / 总变异）。打破自指悖论——AI 写的
Gate 与 AI 写的测试可能共享盲区，但机械注入的变异与 AI 盲区正交，能暴露 oracle 不足。

机制（per mutant）：
  1. 读真源 → 字符串替换注入变异 → 写临时副本
  2. 设环境变量 ``RR_UNDER_TEST=临时副本路径``（verify_reconciliation_registry.py 的 seam）
  3. 跑 ``python verify_reconciliation_registry.py``（**不带** --warn-only）
     - exit 0 = 全 PASS = oracle 未察觉变异 → 变异 SURVIVED（oracle 盲区暴露）
     - exit ≠ 0 = 有 FAIL = oracle 杀死变异 → KILLED
  4. 清理临时副本

阈值：mutation_score = killed / applicable >= 0.80 视为 PASS。
低于阈值返回 1，并打印 survived 变异清单供加固 oracle（按反馈环补场景，不删减变异凑分
——沿用 project_memory mutation testing 裁定）。

oracle 选择裁定：continuation plan §5.2 原述 oracle 为
``tests/test_reconciliation_registry.py``。经 P3-T1 落地，实际 oracle 为
``verify_reconciliation_registry.py``（P3-T1 产出的轻量不变量 audit，已 importlib
加载 SSoT + RR_UNDER_TEST seam）。二者等价——均为"加载 SSoT 副本跑不变量"，
verifier 无需单独 pytest，更轻量且复用 P3-T1。

用法::

    python scripts/governance/meta/mutation_test_reconciliation_registry.py
    python scripts/governance/meta/mutation_test_reconciliation_registry.py --threshold 0.80
    python scripts/governance/meta/mutation_test_reconciliation_registry.py --list

历史根因：自指悖论——AI 写 ReconciliationRegistry（Gate 补偿框架）+ AI 写其测试共享
同源盲区。机械注入变异（如反转 trigger、移除异常隔离、改 priority 排序）与 AI 认知
正交，是验证 oracle 是否真能拦截这类扰动的客观手段。
"""

from __future__ import annotations

__manifest__ = """
args: []
description: mutation_test_reconciliation_registry.py — ReconciliationRegistry SSoT
  变异测试（P3-T2）
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

_SSOT_PATH = _REPO_ROOT / "src" / "zephyr" / "governance" / "reconciliation_registry.py"
_ORACLE_PATH = _SCRIPT_DIR.parent / "verify_reconciliation_registry.py"
_SEAM_ENV = "RR_UNDER_TEST"  # 与 verify_reconciliation_registry.py 约定的 seam 名

DEFAULT_THRESHOLD = 0.80  # noqa: gate-vocab  治本(ARCH-036 P3-A5): 变异测试相似度判断阈值，测试工具专用非系统阈值


# ---- 变异目录 -----------------------------------------------------------
# 每个变异 = (mid, 描述, find, replace)。find 必须在真源中唯一出现一次。
# 变异锚定 ReconciliationRegistry 的关键校验分支（register 幂等/sort/reconcile_for
# trigger/exception/return/spec_count/ReconcilerSpec 字段）；
# 新增/删除 SSoT 分支时须同步维护本目录。
@dataclass
class Mutation:
    mid: str
    desc: str
    find: str
    replace: str


MUTATIONS: list[Mutation] = [
    Mutation(
        "M01",
        "register 幂等失效——不移除同 gate_id 旧 spec（重复注册产生重复 spec）",
        "        self._specs = [s for s in self._specs if s.gate_id != spec.gate_id]",
        "        self._specs = self._specs  # MUTATED: idempotency filter removed",
    ),
    Mutation(
        "M02",
        "sort reverse=True——priority 降序（manifest 补偿反在 ghost 之后）",
        "        self._specs.sort(key=lambda s: s.priority)",
        "        self._specs.sort(key=lambda s: s.priority, reverse=True)  # MUTATED: desc",
    ),
    Mutation(
        "M03",
        "sort 移除——reconcile_for 按 register 顺序执行（非 priority）",
        "        self._specs.sort(key=lambda s: s.priority)",
        "        pass  # MUTATED: sort removed",
    ),
    Mutation(
        "M04",
        "trigger 反转 not→is——命中 trigger 的 reconciler 被跳过，未命中的被执行",
        "                if not spec.trigger(committed_files):",
        "                if spec.trigger(committed_files):  # MUTATED: inverted",
    ),
    Mutation(
        "M05",
        "except re-raise——单 reconciler 异常中断后续（补偿链断裂）",
        "            except Exception as e:  # noqa: BLE001 — drift 对账非阻断",
        "            except Exception as e:  # MUTATED: re-raise\n                raise",
    ),
    Mutation(
        "M06",
        "return 单值——reconcile_for 返回 results[0] 而非 list（D3 退化）",
        "        return results",
        "        return results[0] if results else None  # MUTATED: single",
    ),
    Mutation(
        "M07",
        "append 移除——reconcile 结果不收集（CommitResult.reconcile 恒空）",
        "                results.append(result)",
        "                pass  # MUTATED: don't append result",
    ),
    Mutation(
        "M08",
        "ReconcilerSpec.priority 字段移除——构造 priority= kwarg 抛 TypeError",
        "    priority: int = 100",
        "    # priority: int = 100  # MUTATED: field removed",
    ),
    Mutation(
        "M09",
        "priority 默认值 100→999——未传 priority 的 spec 行为变化（oracle 盲区探针）",
        "    priority: int = 100",
        "    priority: int = 999  # MUTATED: default changed",
    ),
    Mutation(
        "M10",
        "spec_count 返回 +1——诊断/测试误判注册数",
        "        return len(self._specs)",
        "        return len(self._specs) + 1  # MUTATED: off-by-one",
    ),
    Mutation(
        "M11",
        "register 不 append——spec 注册后不入 _specs（注册静默失效）",
        "        self._specs.append(spec)",
        "        pass  # MUTATED: no append in register",
    ),
    Mutation(
        "M12",
        "continue→pass——不跳过未命中 trigger 的 reconciler（全部执行）",
        "                    continue",
        "                    pass  # MUTATED: don't skip",
    ),
    Mutation(
        "M13",
        "sort key priority→gate_id——按 gate_id 字典序（与 priority 排序的盲区探针）",
        "        self._specs.sort(key=lambda s: s.priority)",
        "        self._specs.sort(key=lambda s: s.gate_id)  # MUTATED: by gate_id",
    ),
    Mutation(
        "M14",
        "except 结果 action warn→clean——异常降级结果被误判为 clean（告警丢失）",
        '                        action="warn",\n                        detail=f"reconciler {spec.gate_id} raised: {e}",',
        '                        action="clean",  # MUTATED: warn→clean\n                        detail=f"reconciler {spec.gate_id} raised: {e}",',
    ),
    Mutation(
        "M15",
        "results 初始化为 None——reconcile_for 遍历 None 抛 TypeError（崩溃）",
        "        results: list[ReconcileResult] = []",
        "        results = None  # MUTATED: init None",
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
        return None, "find 未命中（变异锚点已漂移，需同步维护变异目录）"
    if count > 1:
        return None, f"find 命中 {count} 处（非唯一，需扩大上下文）"
    return source.replace(mut.find, mut.replace), "ok"


def _run_oracle(mutated_path: Path) -> tuple[bool, str]:
    """跑 verify_reconciliation_registry.py oracle 指向变异副本。

    返回 (killed, detail)。killed=True 表示 oracle 检出变异（有不变量 FAIL，exit≠0）。
    """
    env = os.environ.copy()
    env[_SEAM_ENV] = str(mutated_path)
    try:
        result = subprocess.run(
            [sys.executable, str(_ORACLE_PATH)],
            capture_output=True,
            text=True,
            cwd=str(_REPO_ROOT),
            env=env,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return True, "oracle 超时（视为 killed，避免误判 survived）"
    killed = result.returncode != 0
    # 取 stdout 末尾几行作 detail（verifier 打印 FN-RR-XXX: PASS/FAIL）
    tail = (result.stdout or "").strip().splitlines()[-3:]
    detail = " | ".join(tail) if tail else f"exit={result.returncode}"
    return killed, detail


def run_all(threshold: float = DEFAULT_THRESHOLD) -> tuple[RunReport, int]:
    """运行全部变异。返回 (报告, 退出码)。"""
    if not _SSOT_PATH.exists():
        print(f"[FATAL] SSoT 真源不存在: {_SSOT_PATH}", file=sys.stderr)
        return RunReport(), 2
    if not _ORACLE_PATH.exists():
        print(f"[FATAL] oracle 不存在: {_ORACLE_PATH}", file=sys.stderr)
        return RunReport(), 2

    source = _SSOT_PATH.read_text(encoding="utf-8")
    report = RunReport()
    tmp_files: list[Path] = []

    print(f"\n[MUTATION] SSoT={_SSOT_PATH.relative_to(_REPO_ROOT)}", file=sys.stderr)
    print(f"[MUTATION] oracle={_ORACLE_PATH.relative_to(_REPO_ROOT)}", file=sys.stderr)
    print(f"[MUTATION] 变异数={len(MUTATIONS)} 阈值={threshold:.0%}\n", file=sys.stderr)

    for mut in MUTATIONS:
        print(f"  [{mut.mid}] {mut.desc} ...", end=" ", flush=True, file=sys.stderr)
        mutated, msg = _apply_mutation(source, mut)
        if mutated is None:
            print(f"SETUP_ERROR ({msg})", file=sys.stderr)
            report.setup_errors.append(MutantResult(mut.mid, mut.desc, "SETUP_ERROR", msg))
            continue

        fd, tmp_path = tempfile.mkstemp(suffix=f"_{mut.mid}_mutant.py", prefix="_rr_mut_")
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
        print("\n  ⚠ SURVIVED 变异（oracle 盲区，建议补场景）：", file=sys.stderr)
        for r in report.survived:
            print(f"    [{r.mid}] {r.desc}", file=sys.stderr)
            print(f"          {r.detail}", file=sys.stderr)
    if report.setup_errors:
        print("\n  ⚠ SETUP_ERROR 变异（锚点漂移，需同步变异目录）：", file=sys.stderr)
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
        description="ReconciliationRegistry 变异测试（独立 oracle，打破自指悖论）"
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
