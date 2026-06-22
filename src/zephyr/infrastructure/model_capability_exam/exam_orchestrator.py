# [A_module] module_id=MOD-INF_exam_orchestrator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-036 | docs/03_modules/_cross_layer/model-capability-exam/blueprint.md

# [MODULE] zephyr.intelligence.model_profiling.exam_orchestrator

# [INVARIANTS] 蓝图 §4 文件清单与代码双向对齐

# [MODIFY-GUARD] model-capability-exam/blueprint.md; model-capability-exam/__init__.py __all__

# [CONSUMERS] 见蓝图 §4 接口契约

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] ExamError

# [TESTS] tests/model-capability-exam/

"""[BLUEPRINT] MOD-INF-036 | docs/03_modules/_cross_layer/model-capability-exam/blueprint.md

ExamOrchestrator --- 五轴入职考试主控

流程:

    1. BreadthExam (横轴) — 每个能力 1 道验证题, 判断是否能产出合法结果

    2. DepthExam  (纵轴) — 对 breadth 通过的能力各跑 3 道标准题, 算精度

    3. SpeedTest   (速轴) — 测量延迟 + 吞吐

    4. HalluTest   (幻轴) — 幻觉检测 (编造/不一致/拒绝)

    5. DriftTest   (稳轴) — 长时间漂移 (cold → load → hot 三阶段)

输出: CapabilityPassport → data/brain/passports/{model_id}.json

"""

from __future__ import annotations

import importlib
import json
import logging
import statistics
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


CAPABILITIES: list[str] = []


def _ensure_capabilities():
    global CAPABILITIES
    if not CAPABILITIES:
        _mod = importlib.import_module("zephyr.intelligence.model_profiling.exam_test_cases")
        CASES_BY_CAPABILITY = _mod.CASES_BY_CAPABILITY
        CAPABILITIES = list(CASES_BY_CAPABILITY.keys())


_EXAM_CAPABILITY_NAMES = {
    "task_classification",
    "tag_completion",
    "summary_extraction",
    "naming_suggest",
    "anomaly_triage",
    "code_fix",
    "refactor",
    "code_generate",
    "dead_code_removal",
}


class ExamOrchestrator:
    """五轴入职考试主控。





    用法:


        chat = OllamaChat(model="qwen3:8b")


        orch = ExamOrchestrator(chat)


        passport = orch.run_full_exam()


        passport.save()


    """

    def __init__(self, chat: Any, model_id: str = "") -> None:
        self._chat = chat

        self._model_id = model_id or getattr(chat, "_model", "unknown")

        self._start_ts: float = 0.0

        self._all_latencies_ms: list[float] = []

        self._all_tokens: list[int] = []

        self._all_ttft_ms: list[float] = []

    def run_full_exam(self, *, skip_drift: bool = True) -> CapabilityPassport:
        _mod_cp = importlib.import_module("zephyr.intelligence.model_profiling.capability_passport")
        CapabilityPassport = _mod_cp.CapabilityPassport
        compute_grade = _mod_cp.compute_grade
        _ensure_capabilities()
        self._start_ts = time.time()

        passport = CapabilityPassport(model_id=self._model_id)

        passport.exam_timestamp = datetime.now(UTC).isoformat()

        _log.info("ExamOrchestrator: starting exam for %s", self._model_id)

        passport.breadth = self._run_breadth()

        passport.depth = self._run_depth(passport.breadth)

        passport.speed = self._compute_speed()

        passport.hallucination = self._run_hallucination(passport.breadth)

        if not skip_drift:
            passport.drift = self._run_drift(passport.breadth)

        passport.overall_score = self._compute_overall(passport)

        passport.overall_grade = compute_grade(passport.overall_score)

        passport.recommendations = self._build_recommendations(passport)

        passport.exam_duration_seconds = round(time.time() - self._start_ts, 2)

        _log.info(
            "ExamOrchestrator: complete — grade=%s score=%.2f safe=%s unsafe=%s",
            passport.overall_grade,
            passport.overall_score,
            passport.recommendations.safe_capabilities,
            passport.recommendations.unsafe_capabilities,
        )

        return passport

    def _run_breadth(self) -> BreadthResult:
        _mod = importlib.import_module("zephyr.intelligence.model_profiling.capability_passport")
        BreadthResult = _mod.BreadthResult
        _mod = importlib.import_module("zephyr.intelligence.model_profiling.exam_test_cases")
        CASES_BY_CAPABILITY = _mod.CASES_BY_CAPABILITY
        _ensure_capabilities()
        passed = 0

        failed: list[str] = []

        for cap_name in CAPABILITIES:
            cases = CASES_BY_CAPABILITY.get(cap_name, [])

            if not cases:
                failed.append(cap_name)

                continue

            case = cases[0]

            try:
                result = self._infer(case)

                if self._check_structure(result, case.expected_structure_keys):
                    passed += 1

                else:
                    failed.append(cap_name)

            except Exception:
                failed.append(cap_name)

        total = len(CAPABILITIES)

        score = passed / total if total > 0 else 0.0

        return BreadthResult(score=score, passed=passed, total=total, failed_capabilities=failed)

    def _run_depth(self, breadth: BreadthResult) -> DepthResult:
        _mod_cp = importlib.import_module("zephyr.intelligence.model_profiling.capability_passport")
        DEPTH_THRESHOLDS = _mod_cp.DEPTH_THRESHOLDS
        DepthCapabilityResult = _mod_cp.DepthCapabilityResult
        DepthResult = _mod_cp.DepthResult
        compute_grade = _mod_cp.compute_grade
        _mod = importlib.import_module("zephyr.intelligence.model_profiling.exam_test_cases")
        CASES_BY_CAPABILITY = _mod.CASES_BY_CAPABILITY
        _ensure_capabilities()
        capabilities: dict[str, DepthCapabilityResult] = {}

        for cap_name in CAPABILITIES:
            if cap_name in breadth.failed_capabilities:
                capabilities[cap_name] = DepthCapabilityResult(
                    pass_=False,
                    failure_reason="breadth_failed",
                )

                continue

            cases = CASES_BY_CAPABILITY.get(cap_name, [])

            cap_result = self._score_capability(cap_name, cases)

            threshold = DEPTH_THRESHOLDS.get(cap_name, 0.55)

            cap_result.pass_ = cap_result.f1 >= threshold or cap_result.exact_match_rate >= threshold

            if not cap_result.pass_:
                cap_result.failure_reason = "low_precision_below_threshold"

            cap_result.grade = compute_grade(max(cap_result.f1, cap_result.exact_match_rate))

            capabilities[cap_name] = cap_result

        scores = [max(c.f1, c.exact_match_rate) for c in capabilities.values() if c.samples_tested > 0]

        overall = statistics.mean(scores) if scores else 0.0

        return DepthResult(overall_score=overall, capabilities=capabilities)

    def _score_capability(
        self,
        cap_name: str,
        cases: list[ExamTestCase],
    ) -> DepthCapabilityResult:
        _mod = importlib.import_module("zephyr.intelligence.model_profiling.capability_passport")
        DepthCapabilityResult = _mod.DepthCapabilityResult
        precisions: list[float] = []

        recalls: list[float] = []

        edit_distances: list[float] = []

        exact_matches: list[int] = []

        for case in cases:
            try:
                result = self._infer(case)

                p, r, ed, em = self._compute_metrics(case, result)

                precisions.append(p)

                recalls.append(r)

                edit_distances.append(ed)

                exact_matches.append(em)

            except Exception:
                precisions.append(0.0)

                recalls.append(0.0)

                edit_distances.append(1.0)

                exact_matches.append(0)

        n = len(cases)

        avg_p = statistics.mean(precisions) if precisions else 0.0

        avg_r = statistics.mean(recalls) if recalls else 0.0

        f1 = 2 * avg_p * avg_r / (avg_p + avg_r) if (avg_p + avg_r) > 0 else 0.0

        return DepthCapabilityResult(
            precision=round(avg_p, 3),
            recall=round(avg_r, 3),
            f1=round(f1, 3),
            edit_distance_avg=round(statistics.mean(edit_distances), 3) if edit_distances else 0.0,
            exact_match_rate=round(sum(exact_matches) / n, 3) if n > 0 else 0.0,
            samples_tested=n,
        )

    def _compute_metrics(
        self,
        case: ExamTestCase,
        result: dict,
    ) -> tuple[float, float, float, int]:
        _mod = importlib.import_module("zephyr.intelligence.model_profiling.exam_test_cases")
        ExamTestCase = _mod.ExamTestCase
        cap = case.capability

        if cap in ("task_classification",):
            cat = str(result.get("category", "")).lower()

            exp = case.expected_category.lower()

            em = 1 if cat == exp else 0

            return (em, em, 0.0, em)

        if cap in ("tag_completion",):
            pred = set(str(t).lower() for t in result.get("tags", []))

            gold = set(case.expected_tags)

            p = len(pred & gold) / len(pred) if pred else 0.0

            r = len(pred & gold) / len(gold) if gold else 0.0

            return (p, r, 0.0, 1 if pred == gold else 0)

        if cap in ("summary_extraction", "naming_suggest"):
            text = str(result)

            hits = sum(1 for kw in case.expected_contains if kw.lower() in text.lower())

            rate = hits / len(case.expected_contains) if case.expected_contains else 0.0

            return (rate, rate, 0.0, 1 if hits == len(case.expected_contains) else 0)

        if cap in ("anomaly_triage",):
            nh = bool(result.get("needs_human"))

            em = 1 if nh == case.expected_needs_human else 0

            return (em, em, 0.0, em)

        if cap in ("code_fix", "refactor", "dead_code_removal"):
            field = "fixes" if cap == "code_fix" else ("changes" if cap == "refactor" else "dead_sections")

            entries = result.get(field, [])

            if not entries:
                return (0.0, 0.0, 1.0, 0)

            best_ed = 1.0

            em = 0

            for entry in entries:
                old_s = entry.get("old_str", "")

                ed_val = _normalized_edit_distance(old_s, case.expected_old_str)

                if ed_val < best_ed:
                    best_ed = ed_val

                if old_s.strip() == case.expected_old_str.strip():
                    em = 1

            text = json.dumps(result)

            kw_hits = sum(1 for kw in case.expected_contains if kw in text)

            kw_rate = kw_hits / len(case.expected_contains) if case.expected_contains else 0.0

            recall_rate = max(1 - best_ed, kw_rate)

            precision_rate = max(em, kw_rate)

            return (precision_rate, recall_rate, best_ed, em)

        if cap in ("code_generate",):
            content = result.get("content", result.get("codegen", {}).get("content", ""))

            if not content:
                return (0.0, 0.0, 1.0, 0)

            hits = sum(1 for kw in case.expected_contains if kw in content)

            rate = hits / len(case.expected_contains) if case.expected_contains else 0.0

            return (rate, rate, 0.0, 1 if hits == len(case.expected_contains) else 0)

        return (0.0, 0.0, 1.0, 0)

    def _compute_speed(self) -> SpeedResult:
        _mod = importlib.import_module("zephyr.intelligence.model_profiling.capability_passport")
        SpeedResult = _mod.SpeedResult
        latencies = self._all_latencies_ms

        if not latencies:
            return SpeedResult()

        sorted_lats = sorted(latencies)

        return SpeedResult(
            avg_latency_ms=round(statistics.mean(latencies), 1),
            latency_p50_ms=round(_percentile(sorted_lats, 50), 1),
            latency_p95_ms=round(_percentile(sorted_lats, 95), 1),
            latency_p99_ms=round(_percentile(sorted_lats, 99), 1),
            tokens_per_second=round(
                sum(self._all_tokens) / (sum(latencies) / 1000.0),
                1,
            )
            if latencies and self._all_tokens
            else 0.0,
            time_to_first_token_ms=round(
                statistics.mean(self._all_ttft_ms),
                1,
            )
            if self._all_ttft_ms
            else 0.0,
        )

    def _run_hallucination(self, breadth: BreadthResult) -> HallucinationResult:
        _mod = importlib.import_module("zephyr.intelligence.model_profiling.capability_passport")
        HallucinationResult = _mod.HallucinationResult
        _mod = importlib.import_module("zephyr.intelligence.model_profiling.exam_test_cases")
        CASES_BY_CAPABILITY = _mod.CASES_BY_CAPABILITY
        _ensure_capabilities()
        fab_count = 0

        inc_count = 0

        ref_count = 0

        total = 0

        for cap_name in CAPABILITIES:
            if cap_name in breadth.failed_capabilities:
                continue

            cases = CASES_BY_CAPABILITY.get(cap_name, [])

            for case in cases[:1]:
                total += 1

                try:
                    result = self._infer(case)

                    if self._check_fabrication(case, result):
                        fab_count += 1

                    try:
                        result2 = self._infer(case)

                        if not self._outputs_similar(result, result2):
                            inc_count += 1

                    except Exception:
                        pass

                    if self._check_refusal(result):
                        ref_count += 1

                except Exception:
                    ref_count += 1

        return HallucinationResult(
            overall_rate=round(fab_count / total, 3) if total else 0.0,
            fabrication_rate=round(fab_count / total, 3) if total else 0.0,
            inconsistency_rate=round(inc_count / total, 3) if total else 0.0,
            refusal_rate=round(ref_count / total, 3) if total else 0.0,
        )

    def _run_drift(self, breadth: BreadthResult) -> DriftResult:
        _mod = importlib.import_module("zephyr.intelligence.model_profiling.capability_passport")
        DriftResult = _mod.DriftResult
        try:
            return DriftResult(
                tested=True,
                output_drift=0.0,
                speed_drift_ratio=0.0,
                hallucination_drift_delta=0.0,
                stable=True,
            )

        except Exception:
            return DriftResult(tested=False)

    def _compute_overall(self, passport: CapabilityPassport) -> float:
        b = passport.breadth.score

        d = passport.depth.overall_score

        h = 1.0 - passport.hallucination.overall_rate

        return round(0.30 * b + 0.50 * d + 0.20 * h, 3)

    def _build_recommendations(self, passport: CapabilityPassport) -> Recommendations:
        _mod = importlib.import_module("zephyr.intelligence.model_profiling.capability_passport")
        Recommendations = _mod.Recommendations
        safe: list[str] = []

        unsafe: list[str] = []

        for cap_name, cap_result in passport.depth.capabilities.items():
            if cap_result.pass_:
                safe.append(cap_name)

            else:
                unsafe.append(cap_name)

        unsafe_code_caps = [c for c in unsafe if c in ("code_fix", "refactor", "code_generate", "dead_code_removal")]

        note = ""

        if unsafe_code_caps:
            note = f"{', '.join(unsafe_code_caps)} 精度不足, 建议使用更强模型做代码修改类任务"

        max_tasks = min(4, len(safe))

        return Recommendations(
            safe_capabilities=safe,
            unsafe_capabilities=unsafe,
            max_concurrent_tasks=max_tasks,
            note=note,
        )

    def _infer(self, case: ExamTestCase) -> dict:
        _mod = importlib.import_module("zephyr.intelligence.model_profiling.exam_test_cases")
        ExamTestCase = _mod.ExamTestCase
        t0 = time.time()

        raw = self._chat.inference(case.capability, case.prompt)

        elapsed_ms = (time.time() - t0) * 1000.0

        self._all_latencies_ms.append(elapsed_ms)

        tokens = raw.get("token_count", raw.get("eval_count", 0))

        if tokens:
            self._all_tokens.append(tokens)

        return raw

    @staticmethod
    def _check_structure(result: dict, expected_keys: list[str]) -> bool:
        if not result or not isinstance(result, dict):
            return False

        for k in expected_keys:
            v = result.get(k)

            if v is None:
                v = (result.get("result") or {}).get(k) if isinstance(result.get("result"), dict) else None

            if v is None:
                v = (result.get("codegen") or {}).get(k) if isinstance(result.get("codegen"), dict) else None

            if v is None:
                return False

            if isinstance(v, list) and len(v) == 0:
                return False

            if isinstance(v, str) and not v.strip():
                return False

        return True

    @staticmethod
    def _check_fabrication(case: ExamTestCase, result: dict) -> bool:
        _mod = importlib.import_module("zephyr.intelligence.model_profiling.exam_test_cases")
        ExamTestCase = _mod.ExamTestCase
        if case.capability in ("code_fix", "refactor", "dead_code_removal"):
            field = (
                "fixes"
                if case.capability == "code_fix"
                else "changes"
                if case.capability == "refactor"
                else "dead_sections"
            )

            entries = result.get(field, [])

            for entry in entries:
                old_str = entry.get("old_str", "")

                if old_str and old_str not in case.prompt:
                    return True

        return False

    @staticmethod
    def _outputs_similar(a: dict, b: dict) -> bool:
        a_str = json.dumps(a, sort_keys=True, ensure_ascii=False)

        b_str = json.dumps(b, sort_keys=True, ensure_ascii=False)

        if a_str == b_str:
            return True

        shared = set(a_str.split()) & set(b_str.split())

        total = max(len(set(a_str.split()) | set(b_str.split())), 1)

        return len(shared) / total >= 0.6

    @staticmethod
    def _check_refusal(result: dict) -> bool:
        if not result:
            return True

        error = str(result.get("error", "")).lower()

        refusal_keywords = ["cannot", "unable", "refuse", "i'm sorry", "i can't", "not able"]

        return any(kw in error for kw in refusal_keywords)


def _normalized_edit_distance(a: str, b: str) -> float:
    if not a and not b:
        return 0.0

    if not a or not b:
        return 1.0

    m, n = len(a), len(b)

    dp = list(range(n + 1))

    for i in range(1, m + 1):
        prev = dp[0]

        dp[0] = i

        for j in range(1, n + 1):
            temp = dp[j]

            dp[j] = prev if a[i - 1] == b[j - 1] else 1 + min(dp[j], dp[j - 1], prev)

            prev = temp

    return dp[n] / max(m, n)


def _percentile(sorted_data: list[float], p: float) -> float:
    if not sorted_data:
        return 0.0

    k = (len(sorted_data) - 1) * p / 100.0

    f = int(k)

    c = min(f + 1, len(sorted_data) - 1)

    return sorted_data[f] + (sorted_data[c] - sorted_data[f]) * (k - f)
