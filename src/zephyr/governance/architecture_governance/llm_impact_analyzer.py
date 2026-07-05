# [BLUEPRINT] (migrated from MOD-INF-021 by ARCH-039 P1, target domain=D_GOVERNANCE)
# [MODULE] zephyr.governance.architecture_governance.llm_impact_analyzer
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.architecture_governance.__init__
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
# [A_module] module_id=MOD-GOV_llm_impact_analyzer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
LLMImpactAnalyzer — LLM-based commit 语义影响分析器。

依据: 蓝图 MOD-INF-021 §7 Phase 5.14 + §6.10 B55

commit diff → LLM API → 语义级风险评估:
    输出: RISK score (0.0~1.0) + 类别 (P0/P1/P2/P3) + 受影响模块 + 推荐操作
    离线模式: 基于关键词规则回退（不含 LLM API 调用）

注意：与 src/zephyr/infrastructure/impact/llm_impact_analyzer.py 命名碰撞
（后者依据 MOD-TASK_SYSTEM 是 task impact analyzer，本文件是 commit impact analyzer）。
类名撞车是历史遗留问题，不在 ARCH-039 P1 范围内。
module_id 已重新分配为 MOD-GOV_llm_impact_analyzer 避免撞车。
"""

from __future__ import annotations

import importlib
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from zephyr.shared.utils.async_utils import run_sync  # 5.12.8 修复：统一 async/sync 边界


class RiskLevel(str, Enum):
    P0_CRITICAL = "P0"
    P1_HIGH = "P1"
    P2_MEDIUM = "P2"
    P3_LOW = "P3"


@dataclass
class ImpactAnalysis:
    commit_sha: str
    risk_score: float
    risk_level: RiskLevel
    impacted_modules: list[str]
    recommendation: str
    key_changes: list[str]
    analysis_source: str
    details: list[str] = field(default_factory=list)


HIGH_RISK_KEYWORDS: set[str] = {
    "drop table",
    "delete from",
    "truncate",
    "rm -rf",
    "force push",
    "DROP TABLE",
    "DELETE FROM",
    "TRUNCATE",
    "os.remove",
    "os.unlink",
    "shutil.rmtree",
    "eval(",
    "exec(",
    "subprocess.Popen",
    "password",
    "secret",
    "token",
    "api_key",
    "__import__",
    "importlib",
}

MEDIUM_RISK_KEYWORDS: set[str] = {
    "ALTER TABLE",
    "ALTER COLUMN",
    "modify",
    "git reset",
    "git checkout --",
    "pickle.loads",
    "pickle.dumps",
    "executemany",
    "execute(",
    "@dataclass",
    "class ",
    "def ",
}


class LLMImpactAnalyzer:
    def __init__(self, project_root: Path | None = None, use_llm: bool = False) -> None:
        self._project_root = project_root or Path.cwd()
        self._use_llm = use_llm

    def analyze(self, commit_sha: str) -> ImpactAnalysis:
        diff = self._get_diff(commit_sha)
        if self._use_llm:
            return self._llm_analyze(commit_sha, diff)

        return self._rule_based_analyze(commit_sha, diff)

    def _rule_based_analyze(self, commit_sha: str, diff: str) -> ImpactAnalysis:
        risk_score = 0.0
        key_changes: list[str] = []
        impacted_modules: set[str] = set()

        for keyword in HIGH_RISK_KEYWORDS:
            if keyword in diff:
                risk_score += 0.25
                key_changes.append(f"HIGH: {keyword}")

        for keyword in MEDIUM_RISK_KEYWORDS:
            if keyword in diff:
                risk_score += 0.10
                key_changes.append(f"MEDIUM: {keyword}")

        risk_score = min(risk_score, 1.0)

        if risk_score >= 0.75:
            risk_level = RiskLevel.P0_CRITICAL
        elif risk_score >= 0.40:
            risk_level = RiskLevel.P1_HIGH
        elif risk_score >= 0.15:
            risk_level = RiskLevel.P2_MEDIUM
        else:
            risk_level = RiskLevel.P3_LOW

        for line in diff.splitlines():
            if line.startswith("diff --git") or line.startswith("--- a/") or line.startswith("+++ b/"):
                path = line.split(" b/")[-1] if " b/" in line else line.replace("--- a/", "").replace("+++ b/", "")
                if "/" in path:
                    impacted_modules.add(path.split("/")[0])

        recommendation = "safe_to_proceed"
        if risk_level in (RiskLevel.P0_CRITICAL, RiskLevel.P1_HIGH):
            recommendation = "requires_manual_review"
        elif risk_level is RiskLevel.P2_MEDIUM:
            recommendation = "auto_rollback_if_flaky"

        return ImpactAnalysis(
            commit_sha=commit_sha,
            risk_score=risk_score,
            risk_level=risk_level,
            impacted_modules=sorted(impacted_modules),
            recommendation=recommendation,
            key_changes=key_changes,
            analysis_source="rule_based_keyword",
        )

    def _llm_analyze(self, commit_sha: str, diff: str) -> ImpactAnalysis:
        rule_result = self._rule_based_analyze(commit_sha, diff)
        self._lsg_scan_analysis(rule_result)
        return rule_result

    def _lsg_scan_analysis(self, analysis: ImpactAnalysis) -> None:
        try:
            _lsg_mod = importlib.import_module("zephyr.security.llm_defense.llm_security.gateway")
            LSGSecurityGateway = _lsg_mod.LSGSecurityGateway
            import asyncio

            gateway = LSGSecurityGateway()
            content = f"{analysis.recommendation} {' '.join(analysis.key_changes)}"
            result = run_sync(gateway.scan_output(content))
            if result.decision.value not in ("allow", "ALLOW"):
                analysis.recommendation = "requires_manual_review"
                analysis.details.append("LSG output scan flagged content")
        except ImportError:
            pass
        except Exception:
            pass

    def _get_diff(self, commit_sha: str) -> str:
        try:
            result = subprocess.run(
                ["git", "show", "--format=%B", "-p", commit_sha],
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=15,
            )
            return result.stdout or ""
        except Exception:
            return ""

    def batch_analyze(self, commit_shas: list[str]) -> list[ImpactAnalysis]:
        return [self.analyze(sha) for sha in commit_shas]
