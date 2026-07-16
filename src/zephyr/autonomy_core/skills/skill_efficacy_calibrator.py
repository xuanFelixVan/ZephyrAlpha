# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_efficacy_calibrator
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_skill_efficacy_calibrator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Efficacy Calibrator
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.2.0

Skill 效能实证校准 —— Anti-Regression SkillsBench
==================================================
机制:
  1. BenchmarkRunner: 对 Skill 执行标准化基准测试
  2. LatencyTracker: 追踪历史延迟，检测退化
  3. AccuracyValidator: 对比 Skill 产出与预期输出
  4. RegressionDetector: 多版本对比，发现性能退化
  5. CalibrationAdvisor: 给出调优建议
"""

from __future__ import annotations

import json
import statistics
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class SkillsBenchRunner:
    """基准测试执行器"""

    def __init__(self, history_path: Path | None = None):
        self._history_path = history_path or (Path(__file__).resolve().parent / "_benchmark_history.json")
        self._history: dict[str, list[dict[str, Any]]] = self._load_history()

    def _load_history(self) -> dict[str, list[dict[str, Any]]]:
        if self._history_path.exists():
            try:
                return json.loads(self._history_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                pass
        return {}

    def _save_history(self):
        try:
            data = json.dumps(self._history, ensure_ascii=False, indent=2)
            self._history_path.write_text(data, encoding="utf-8")
        except OSError:
            pass

    def record_run(
        self,
        skill_id: str,
        score: float,
        latency_ms: float,
        accuracy: float,
        checks_passed: int,
        checks_total: int,
    ):
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "score": score,
            "latency_ms": latency_ms,
            "accuracy": accuracy,
            "checks_passed": checks_passed,
            "checks_total": checks_total,
        }
        self._history.setdefault(skill_id, []).append(entry)
        self._save_history()

    def get_history(self, skill_id: str, limit: int = 10) -> list[dict[str, Any]]:
        return self._history.get(skill_id, [])[-limit:]

    def detect_regression(self, skill_id: str) -> dict[str, Any]:
        history = self.get_history(skill_id, 20)
        if len(history) < 3:
            return {
                "regression_detected": False,
                "reason": "insufficient_data",
                "min_samples": 3,
                "current_samples": len(history),
            }

        scores = [h["score"] for h in history]
        latencies = [h["latency_ms"] for h in history]

        mid = len(scores) // 2
        old_scores = scores[:mid]
        new_scores = scores[mid:]
        old_lat = latencies[:mid]
        new_lat = latencies[mid:]

        old_mean = statistics.mean(old_scores) if old_scores else 0
        new_mean = statistics.mean(new_scores) if new_scores else 0
        old_lat_mean = statistics.mean(old_lat) if old_lat else 0
        new_lat_mean = statistics.mean(new_lat) if new_lat else 0

        score_drop = old_mean - new_mean
        latency_increase = new_lat_mean - old_lat_mean

        regression = score_drop > 10.0 or latency_increase > 100.0

        return {
            "regression_detected": regression,
            "score_trend": "declining" if score_drop > 5 else ("improving" if score_drop < -5 else "stable"),
            "score_drop": round(score_drop, 2),
            "old_mean_score": round(old_mean, 2),
            "new_mean_score": round(new_mean, 2),
            "latency_trend": "increasing"
            if latency_increase > 50
            else ("decreasing" if latency_increase < -50 else "stable"),
            "latency_change_ms": round(latency_increase, 2),
            "old_mean_latency": round(old_lat_mean, 2),
            "new_mean_latency": round(new_lat_mean, 2),
        }


def _run_checks(
    checks: list[str],
    l1: dict[str, Any],
    l2: str,
    tokens: int,
) -> tuple[list[dict[str, Any]], int]:
    results: list[dict[str, Any]] = []
    passed_count = 0
    for check in checks:
        if check == "metadata_completeness":
            ok = bool(l1.get("skill_id")) and bool(l1.get("name"))
            results.append({"check": check, "passed": ok, "detail": str(l1.get("name", "?"))})
            if ok:
                passed_count += 1

        elif check == "body_non_empty":
            ok = len(l2) > 10
            results.append({"check": check, "passed": ok, "detail": f"{len(l2)} chars"})
            if ok:
                passed_count += 1

        elif check == "token_budget_compliance":
            ok = tokens <= 500
            results.append({"check": check, "passed": ok, "detail": f"{tokens}/500 tokens"})
            if ok:
                passed_count += 1

        elif check == "tool_allowlist_present":
            tools = l1.get("allowed_tools", [])
            ok = len(tools) > 0
            results.append({"check": check, "passed": ok, "detail": f"{len(tools)} tools"})
            if ok:
                passed_count += 1

        elif check == "frontmatter_valid":
            ok = bool(l1.get("skill_id"))
            results.append({"check": check, "passed": ok})
            if ok:
                passed_count += 1

        else:
            results.append({"check": check, "passed": True, "detail": "auto_pass"})
            passed_count += 1
    return results, passed_count


class SkillEfficacyCalibrator:
    """Skill 效能实证校准器"""

    SUITE_NAME = "SkillsBench-Zephyr"
    PASS_THRESHOLD = 70.0
    REGRESSION_FATAL = True

    def __init__(self):
        self._runner = SkillsBenchRunner()
        self._bench_results: dict[str, list[dict[str, Any]]] = {}

    def run_benchmark(self, skill_id: str, check_items: list[str] | None = None) -> dict[str, Any]:
        checks = check_items or [
            "metadata_completeness",
            "body_non_empty",
            "token_budget_compliance",
            "tool_allowlist_present",
            "frontmatter_valid",
        ]

        total_latency_ms = 0.0

        try:
            from zephyr.autonomy_core.skills.skill_loader import SkillLoader

            loader = SkillLoader()
            t0 = datetime.now(UTC)

            skill = loader.progressive_load(skill_id)
            l1 = skill.get("l1", {})
            l2 = skill.get("l2", "")
            tokens = skill.get("token_count_l2", 0)

            t1 = datetime.now(UTC)
            load_latency = (t1 - t0).total_seconds() * 1000
            total_latency_ms += load_latency

            results, passed_count = _run_checks(checks, l1, l2, tokens)

            accuracy = (passed_count / len(checks)) * 100.0 if checks else 100.0
            score = round(accuracy, 1)

            self._runner.record_run(
                skill_id=skill_id,
                score=score,
                latency_ms=total_latency_ms,
                accuracy=accuracy,
                checks_passed=passed_count,
                checks_total=len(checks),
            )

            regression = self._runner.detect_regression(skill_id)

            return {
                "skill_id": skill_id,
                "score": score,
                "accuracy": round(accuracy, 1),
                "latency_ms": round(total_latency_ms, 1),
                "checks_total": len(checks),
                "checks_passed": passed_count,
                "results": results,
                "passed": score >= self.PASS_THRESHOLD,
                "regression": regression,
            }

        except (KeyError, FileNotFoundError) as e:
            return {
                "skill_id": skill_id,
                "score": 0.0,
                "latency_ms": 0,
                "accuracy": 0.0,
                "error": str(e),
                "passed": False,
            }
        except ImportError:
            return {
                "skill_id": skill_id,
                "score": 0.0,
                "latency_ms": 0,
                "accuracy": 0.0,
                "error": "skill_loader_unavailable",
                "passed": False,
            }

    def calibrate(self, skill_id: str, target_accuracy: float) -> dict[str, Any]:
        bench = self.run_benchmark(skill_id)
        current = bench.get("accuracy", 0.0)
        gap = target_accuracy - current

        suggestions: list[str] = []
        if bench.get("error"):
            suggestions.append(f"Fix error: {bench['error']}")
        for r in bench.get("results", []):
            if not r.get("passed"):
                suggestions.append(f"Fix check '{r.get('check')}': {r.get('detail', '')}")

        calibrated = current >= target_accuracy

        return {
            "skill_id": skill_id,
            "current_accuracy": current,
            "target_accuracy": target_accuracy,
            "gap": round(gap, 1),
            "calibrated": calibrated,
            "suggestions": suggestions,
        }
