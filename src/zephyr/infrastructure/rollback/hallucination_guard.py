# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.hallucination_guard
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES] zephyr.infrastructure.rollback.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_hallucination_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
HallucinationGuard — AI 幻觉防护：回滚后强制状态验证。

依据: 蓝图 MOD-INF-021 §6.12 B57, §7 Phase 6.2, 决策 D-021-12

回滚后不直接放行——强制 AI 进入 state_verification_round:
    要求 AI 逐文件列出 MD5 / 行数 / 关键函数签名，
    Guard 验证 AI 输出与实际 git 状态是否一致。

连续 3 轮未通过 -> exit code 11 (HALLUCINATION_DETECTED) -> 暂停该 agent。
对标: Microsoft VeriTrail DAG 溯源验证风格
"""

from __future__ import annotations

import ast
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class FileState:
    path: str
    md5: str = ""
    sha256: str = ""
    line_count: int = 0
    function_signatures: list[str] = field(default_factory=list)
    class_names: list[str] = field(default_factory=list)


@dataclass
class VerificationRound:
    round_number: int
    ai_claimed_state: list[FileState] = field(default_factory=list)
    actual_state: list[FileState] = field(default_factory=list)
    mismatches: list[str] = field(default_factory=list)
    passed: bool = False


@dataclass
class HallucinationResult:
    detected: bool
    rounds_executed: int
    rounds_passed: int
    rounds_failed: int
    final_verdict: str
    exit_code: int
    suspended_agent: str = ""
    details: list[str] = field(default_factory=list)


class HallucinationGuard:
    MAX_ROUNDS: int = 3
    EXIT_CODE_HALLUCINATION: int = 11

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._rounds: list[VerificationRound] = []

    def compute_actual_state(self, files: list[str] | None = None) -> list[FileState]:
        target_files = files or list(self._project_root.glob("src/zephyr/**/*.py"))
        states: list[FileState] = []

        for f_path in target_files:
            p = Path(f_path)
            if not str(p).startswith(str(self._project_root)):
                p = self._project_root / p
            if not p.exists() or not p.is_file():
                continue

            content = p.read_text(encoding="utf-8")
            states.append(
                FileState(
                    path=str(p.relative_to(self._project_root)),
                    md5=hashlib.md5(content.encode()).hexdigest(),
                    sha256=hashlib.sha256(content.encode()).hexdigest(),
                    line_count=len(content.splitlines()),
                    function_signatures=self._extract_functions(content),
                    class_names=self._extract_classes(content),
                )
            )

        return states

    def verify_round(
        self,
        ai_claimed_state: list[dict[str, Any]],
        files: list[str] | None = None,
    ) -> VerificationRound:
        round_num = len(self._rounds) + 1
        actual = self.compute_actual_state(files)

        claimed: list[FileState] = []
        for item in ai_claimed_state:
            claimed.append(
                FileState(
                    path=item.get("path", ""),
                    md5=item.get("md5", ""),
                    sha256=item.get("sha256", ""),
                    line_count=item.get("line_count", 0),
                    function_signatures=item.get("function_signatures", []),
                    class_names=item.get("class_names", []),
                )
            )

        mismatches: list[str] = []
        actual_map = {s.path: s for s in actual}
        claimed_map = {s.path: s for s in claimed}

        all_paths = set(actual_map.keys()) | set(claimed_map.keys())
        for path in sorted(all_paths):
            a = actual_map.get(path)
            c = claimed_map.get(path)
            if not a:
                mismatches.append(f"{path}: file exists but AI claimed absent")
            elif not c:
                mismatches.append(f"{path}: AI claimed file but does not exist")
            else:
                if a.md5 != c.md5:
                    mismatches.append(f"{path}: MD5 mismatch")
                if a.line_count != c.line_count:
                    mismatches.append(f"{path}: line count {a.line_count} vs {c.line_count}")

        passed = len(mismatches) == 0
        vr = VerificationRound(
            round_number=round_num,
            ai_claimed_state=claimed,
            actual_state=actual,
            mismatches=mismatches,
            passed=passed,
        )
        self._rounds.append(vr)
        return vr

    def run_full_verification(
        self,
        ai_claimed_states: list[list[dict[str, Any]]],
        files: list[str] | None = None,
    ) -> HallucinationResult:
        self._rounds = []
        for i, claimed in enumerate(ai_claimed_states):
            if i >= self.MAX_ROUNDS:
                break
            self.verify_round(claimed, files)

        passed = [r for r in self._rounds if r.passed]
        failed = [r for r in self._rounds if not r.passed]
        detected = len(failed) >= self.MAX_ROUNDS

        if detected:
            verdict = "HALLUCINATION_DETECTED"
            exit_code = self.EXIT_CODE_HALLUCINATION
        elif len(passed) > 0:
            verdict = "STATE_VERIFIED"
            exit_code = 0
        else:
            verdict = "INCONCLUSIVE"
            exit_code = 0

        return HallucinationResult(
            detected=detected,
            rounds_executed=len(self._rounds),
            rounds_passed=len(passed),
            rounds_failed=len(failed),
            final_verdict=verdict,
            exit_code=exit_code,
            details=[m for r in self._rounds for m in r.mismatches],
        )

    @staticmethod
    def _extract_functions(source: str) -> list[str]:
        try:
            tree = ast.parse(source)
            funcs: list[str] = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    args = [a.arg for a in node.args.args]
                    funcs.append(f"{node.name}({', '.join(args)})")
            return funcs
        except SyntaxError:
            return []

    @staticmethod
    def _extract_classes(source: str) -> list[str]:
        try:
            tree = ast.parse(source)
            return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        except SyntaxError:
            return []

    @property
    def rounds(self) -> list[VerificationRound]:
        return self._rounds
