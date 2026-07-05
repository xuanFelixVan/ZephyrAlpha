# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] zephyr.intelligence.model_profiling.exam_orchestrator
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.intelligence.model_profiling.capability_passport; zephyr.intelligence.model_profiling.exam_test_cases
# [CONSUMERS] MOD-INF-034
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 五轴入职考试;横纵速幻稳;CapabilityPassport产出
# [MODIFY-GUARD] docs/03_modules/_cross_layer/model_profiler/blueprint.md;src/zephyr/intelligence/model_profiling/__init__.py
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ExamError;InferenceError
# [TESTS] tests/test_model_profiler/
# [A_module] module_id=MOD-RSC_exam_orchestrator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
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

logger = logging.getLogger(__name__)

import json
import logging
import math
import os
import statistics
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from zephyr.intelligence.model_profiling.capability_passport import (
    DEPTH_THRESHOLDS,
    BreadthResult,
    CapabilityPassport,
    CostBreakdown,
    DepthCapabilityResult,
    DepthResult,
    DriftResult,
    HallucinationBreakdown,
    HallucinationResult,
    QuickProfile,
    Recommendations,
    SpeedResult,
    compute_grade,
    compute_grade_simple,
)
from zephyr.intelligence.model_profiling.exam_test_cases import (
    CASES_BY_CAPABILITY,
    Difficulty,
    ExamTestCase,
)
from zephyr.intelligence.model_profiling.exam_rubric import ExamRubric
from zephyr.intelligence.model_profiling.exam_executor import ExamExecutor
from zephyr.intelligence.model_profiling.exam_judge import DeterministicJudge, ExamJudge

_log = logging.getLogger(__name__)

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


# v3.0.5: 奥赛单题通过线（三轨综合分 ≥ 0.6 视为通过）
_OLYMPIAD_CASE_PASS_THRESHOLD: float = 0.6

# v3.0.5: 难度加权字典（加权平均替代简单平均）
_DIFFICULTY_WEIGHTS: dict[Difficulty, int] = {
    Difficulty.EASY: 1,
    Difficulty.MEDIUM: 2,
    Difficulty.HARD: 3,
    Difficulty.EXTREME: 4,
    Difficulty.OLYMPIAD: 5,
}


def _time_weight(elapsed_ms: float, decay_ms: float = 260_000.0) -> float:
    """v3.0.5: 时间权重折扣——慢答案被折扣但不归零。

    对齐 project_memory ``exp(-t/260s)``：参数 260s（exp 衰减常数，非半衰期）。
    - 0ms   → 1.000（即时满分）
    - 9s    → 0.966（本地模型单题，轻微折扣）
    - 60s   → 0.794（thinking 模型单题，明显折扣）
    - 260s  → 0.368
    - 600s  → 0.099（防卡死上限，不归零）

    用途：在 _score_capability 中对每 case 的 f1 折扣，
    替代已废除的 60s 硬熔断——慢但正确的答案仍得分，仅被折扣。
    """
    if elapsed_ms <= 0:
        return 1.0
    return math.exp(-elapsed_ms / decay_ms)


class ExamOrchestrator:
    """五轴入职考试主控。

    用法:
        chat = OllamaChat(model="qwen3:8b")
        orch = ExamOrchestrator(chat)
        passport = orch.run_full_exam()
        passport.save()
    """

    def __init__(
        self,
        chat: Any,
        model_id: str = "",
        randomize_order: bool = False,
        judge_chat: Any = None,
        depth_samples_per_case: int | None = None,
    ) -> None:
        self._chat = chat
        self._model_id = model_id or getattr(chat, "_model", "unknown")
        self._start_ts: float = 0.0
        self._all_latencies_ms: list[float] = []
        self._all_tokens: list[int] = []
        self._all_ttft_ms: list[float] = []
        self._randomize_order = randomize_order
        self._optimization_suspicions = 0
        # v3.0.5: 奥赛题逐题通过记录（供封顶）
        self._olympiad_case_results: list[bool] = []
        # v3.0.5: 三轨评分裁判模型（缺省回退纯 rubric 评分）
        self._judge_chat = judge_chat
        # v3.0.5: 三轨评分器实例（rubric/executor 自包含；judge 仅在有 chat 时创建）
        self._rubric_scorer = ExamRubric()
        self._executor = ExamExecutor()
        self._judge: ExamJudge | None = ExamJudge(judge_chat) if judge_chat is not None else None
        # P1-4: 确定性裁判 fallback — judge_chat=None 时避免 judge 轨缺失导致三轨退化为单轨
        self._det_judge: DeterministicJudge = DeterministicJudge()
        # P1-2: depth 每题采样次数（默认 1=单次保持向后兼容; 5=统计显著性校准）
        # 优先级: 显式参数 > 环境变量 ZEPHYR_DEPTH_SAMPLES > 默认 1
        if depth_samples_per_case is None:
            # 5.155.4 修复: 添加 try/except 防止非整数环境变量值导致 ValueError
            try:
                depth_samples_per_case = int(os.environ.get("ZEPHYR_DEPTH_SAMPLES", "1"))
            except (TypeError, ValueError):
                depth_samples_per_case = 1
        self._depth_samples_per_case = max(1, depth_samples_per_case)

    def run_full_exam(self, *, skip_drift: bool = False) -> CapabilityPassport:
        self._start_ts = time.time()
        self._olympiad_case_results = []  # v3.0.5: 重置奥赛题通过记录

        passport = CapabilityPassport(model_id=self._model_id)
        passport.exam_timestamp = datetime.now(UTC).isoformat()

        _log.info("ExamOrchestrator: starting exam for %s", self._model_id)

        passport.breadth = self._run_breadth()
        passport.depth = self._run_depth(passport.breadth)
        passport.speed = self._compute_speed()
        passport.cost = self._compute_cost()
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
        passed = 0
        failed: list[str] = []

        cap_order = list(CAPABILITIES)
        if self._randomize_order:
            import random
            random.shuffle(cap_order)

        for cap_name in cap_order:
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
        precisions: list[float] = []
        recalls: list[float] = []
        edit_distances: list[float] = []
        exact_matches: list[int] = []
        time_weights: list[float] = []  # v3.0.5: 每 case 时间折扣系数
        weights: list[int] = []       # v3.0.5: 难度加权

        # P1-2: 每题多次采样, 提升统计显著性 (n=1 时退化为原单次行为)
        n_samples = self._depth_samples_per_case

        for case in cases:
            # 多次采样收集 per-sample 指标
            sample_ps: list[float] = []
            sample_rs: list[float] = []
            sample_eds: list[float] = []
            sample_ems: list[int] = []
            sample_tws: list[float] = []
            oly_overalls: list[float] = []  # OLYMPIAD 题每次采样的 overall 分

            for _ in range(n_samples):
                p, r, ed, em, tw, oly_ov = self._score_case_once(case)
                sample_ps.append(p)
                sample_rs.append(r)
                sample_eds.append(ed)
                sample_ems.append(em)
                sample_tws.append(tw)
                if oly_ov is not None:
                    oly_overalls.append(oly_ov)

            # 聚合: p/r/ed/tw 取均值; em 用多数投票 (>=50% 视为 exact)
            precisions.append(statistics.mean(sample_ps) if sample_ps else 0.0)
            recalls.append(statistics.mean(sample_rs) if sample_rs else 0.0)
            edit_distances.append(statistics.mean(sample_eds) if sample_eds else 0.0)
            time_weights.append(statistics.mean(sample_tws) if sample_tws else 1.0)
            exact_matches.append(1 if (statistics.mean(sample_ems) >= 0.5) else 0)

            # OLYMPIAD: 用均值 overall 判定 pass, 仅 append 一次 (不按采样次数膨胀)
            if case.difficulty is Difficulty.OLYMPIAD:
                mean_oly = statistics.mean(oly_overalls) if oly_overalls else 0.0
                self._olympiad_case_results.append(mean_oly >= _OLYMPIAD_CASE_PASS_THRESHOLD)

            weights.append(_DIFFICULTY_WEIGHTS.get(case.difficulty, 1))

        n = len(cases)
        total_w = sum(weights) if weights else 1
        # v3.0.5: 加权平均替代简单平均（难度越高权重越大）
        avg_p = sum(p * w for p, w in zip(precisions, weights, strict=True)) / total_w if precisions else 0.0
        avg_r = sum(r * w for r, w in zip(recalls, weights, strict=True)) / total_w if recalls else 0.0
        f1_raw = 2 * avg_p * avg_r / (avg_p + avg_r) if (avg_p + avg_r) > 0 else 0.0
        # v3.0.5: 慢 case 被时间折扣——替代已废除的 60s 硬熔断，慢但不归零
        avg_tw = sum(tw * w for tw, w in zip(time_weights, weights, strict=True)) / total_w if time_weights else 1.0
        f1 = f1_raw * avg_tw

        return DepthCapabilityResult(
            precision=round(avg_p, 3),
            recall=round(avg_r, 3),
            f1=round(f1, 3),
            edit_distance_avg=round(statistics.mean(edit_distances), 3) if edit_distances else 0.0,
            exact_match_rate=round(sum(exact_matches) / n, 3) if n > 0 else 0.0,
            samples_tested=n,
            time_weight_avg=round(avg_tw, 3),
            samples_per_case=n_samples,
        )

    def _score_case_once(
        self,
        case: ExamTestCase,
    ) -> tuple[float, float, float, int, float, float | None]:
        """P1-2: 单次采样一个 case, 返回 (p, r, ed, em, tw, oly_overall_or_None)。

        oly_overall 为 None 表示非 OLYMPIAD 题; 否则为本次采样的三轨综合分。
        异常时返回全 0 指标 (oly_overall=0.0 for OLYMPIAD)。
        """
        elapsed_ms = 0.0
        oly_overall: float | None = None
        try:
            result = self._infer(case)
            # v3.0.5: 取出耗时计算时间折扣（_infer 注入；不干扰 _compute_metrics）
            if isinstance(result, dict):
                elapsed_ms = result.pop("_elapsed_ms", 0.0)

            if case.difficulty is Difficulty.OLYMPIAD:
                # P1.5: OLYMPIAD 题走三轨评分
                oly_overall = self._score_olympiad_case(case, result)
                p = r = oly_overall
                ed = round(1.0 - oly_overall, 3)
                em = 1 if oly_overall >= _OLYMPIAD_CASE_PASS_THRESHOLD else 0
            else:
                # 非 OLYMPIAD 题保持现有 _compute_metrics 路径不变
                p, r, ed, em = self._compute_metrics(case, result)
        except Exception:
            p, r, ed, em = 0.0, 0.0, 1.0, 0
            if case.difficulty is Difficulty.OLYMPIAD:
                oly_overall = 0.0

        tw = _time_weight(elapsed_ms)
        return p, r, ed, em, tw, oly_overall

    # ── P1.5: OLYMPIAD 三轨评分 ──────────────────────────

    def _score_olympiad_case(self, case: ExamTestCase, result: dict) -> float:
        """P1.5: OLYMPIAD 题三轨评分——judge*0.4 + executor*0.3 + rubric*0.3（归一化）。

        P1-4 升级: judge 轨始终存在 —
          - judge_chat 可用 → LLM judge (语义级评分)
          - judge_chat=None → DeterministicJudge (关键词+结构+长度, 零成本独立意见)

        executor 轨:
          - code_generate 类 + expected_test_cases → 可执行断言
          - 其他能力 + expected_static_assertions → 静态文本断言 (P1-4 新增)
          - 两者皆无 → executor 轨缺失, 权重回退到 rubric/judge (归一化)

        Returns:
            overall: float 0.0~1.0（三轨加权综合分）
        """
        candidate = self._extract_candidate_text(result)

        # 注入 _expected_* 供 rubric checker 使用
        rubric_input = dict(result) if isinstance(result, dict) else {"content": str(result)}
        if case.expected_contains:
            rubric_input["_expected_contains"] = list(case.expected_contains)
        if case.expected_hallucinations:
            rubric_input["_expected_hallucinations"] = list(case.expected_hallucinations)
        if case.expected_call_chain:
            rubric_input["_expected_call_chain"] = list(case.expected_call_chain)
        if case.expected_parallel_groups:
            rubric_input["_expected_parallel_groups"] = [list(g) for g in case.expected_parallel_groups]

        tracks: list[tuple[float, float]] = []  # (weight, score)

        # Track 1: Rubric（始终可用）
        rubric_result = self._rubric_scorer.score(case.capability, rubric_input)
        tracks.append((0.3, rubric_result.score))

        # Track 2: Executor
        # 优先用可执行断言 (code_generate); 否则用静态文本断言 (P1-4 新增, 适用于非 code 能力)
        if case.capability == "code_generate" and case.expected_test_cases:
            exec_result = self._executor.execute(candidate, list(case.expected_test_cases))
            tracks.append((0.3, exec_result.pass_rate))
        elif getattr(case, "expected_static_assertions", []):
            # P1-4: 静态文本断言 — 检查候选答案是否包含期望的关键文本
            static_pass_rate = self._check_static_assertions(
                candidate, case.expected_static_assertions
            )
            tracks.append((0.3, static_pass_rate))

        # Track 3: Judge (P1-4: 始终存在, LLM judge 优先, 缺省用 DeterministicJudge)
        if self._judge is not None:
            judge_result = self._judge.judge(case, candidate)
        else:
            judge_result = self._det_judge.judge(case, candidate)
        tracks.append((0.4, judge_result.overall))

        # 归一化加权（自动处理权重重分配）
        total_w = sum(w for w, _ in tracks)
        if total_w <= 0:
            return 0.0
        return sum(w * s for w, s in tracks) / total_w

    @staticmethod
    def _check_static_assertions(candidate: str, assertions: list[str]) -> float:
        """P1-4: 静态文本断言 — 检查候选答案是否包含期望的关键文本。

        Args:
            candidate: 被测模型的输出文本
            assertions: 期望包含的文本片段列表 (大小写不敏感)
        Returns:
            pass_rate: 0.0~1.0 (命中断言数 / 总断言数)
        """
        if not assertions:
            return 0.0
        text_lower = candidate.lower()
        hits = sum(1 for a in assertions if a.lower() in text_lower)
        return hits / len(assertions)

    @staticmethod
    def _extract_candidate_text(result: dict) -> str:
        """从推理结果中提取候选文本（供 judge/executor 使用）。"""
        if not isinstance(result, dict):
            return str(result) if result else ""
        content = result.get("content", "")
        if not content:
            content = result.get("response", "")
        if not content:
            nested = result.get("codegen", {})
            if isinstance(nested, dict):
                content = nested.get("content", "")
        if not content:
            content = json.dumps(result, ensure_ascii=False, indent=2)
        return content

    def _compute_metrics(
        self,
        case: ExamTestCase,
        result: dict,
    ) -> tuple[float, float, float, int]:
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

        if cap in ("code_fix", "code_edit_precision", "refactor", "dead_code_removal"):
            field = "fixes" if cap in ("code_fix", "code_edit_precision") else ("changes" if cap == "refactor" else "dead_sections")
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

        # v3.0.8: 通用 depth fallback——对未在硬编码分支处理的能力，
        # 按 expected_* 字段类型做语义匹配。修复 depth 暴跌：原兜底 return 零
        # 导致 21 个新增能力 depth 全零（与 inference() 硬编码链同类架构缺陷）。
        generic = self._compute_metrics_generic(case, result)
        if generic is not None:
            return generic
        return (0.0, 0.0, 1.0, 0)

    def _compute_metrics_generic(
        self,
        case: ExamTestCase,
        result: dict,
    ) -> tuple[float, float, float, int] | None:
        """v3.0.8: 通用 depth fallback——按 expected_* 字段类型做语义匹配。

        对未在 _compute_metrics 硬编码分支中处理的能力，穷举匹配 expected_* 字段：
        布尔/列表/字符串/int 四类 + expected_contains 关键词兜底。
        修复 depth 暴跌：原兜底 return (0,0,1,0) 导致 21 个新增能力 depth 全零
        （与 inference() 硬编码链同类架构缺陷——_compute_metrics 也只显式处理 9 能力）。

        Returns:
            (precision, recall, edit_distance, exact_match) 或 None（无可用字段时）。
        """
        text = json.dumps(result, ensure_ascii=False).lower()
        p_rates: list[float] = []
        r_rates: list[float] = []
        em_all = 1

        # 1. 布尔字段（用 expected_structure_keys 判断是否为考点，因 dataclass 默认 False）
        bool_fields = [
            ("expected_compliant", "compliant"),
            ("expected_has_bug", "has_bug"),
            ("expected_ambiguous", "ambiguous"),
            ("expected_has_cycle", "has_cycle"),
            ("expected_has_hallucination", "has_hallucination"),
        ]
        for attr, key in bool_fields:
            if key not in case.expected_structure_keys:
                continue
            exp = getattr(case, attr, False)
            got = result.get(key)
            if isinstance(got, bool):
                match = 1 if got == exp else 0
            elif got is None:
                match = 0
            else:
                match = 1 if str(got).lower() == str(exp).lower() else 0
            p_rates.append(match)
            r_rates.append(match)
            if not match:
                em_all = 0

        # 2. 列表字段（集合交集率）
        list_fields = [
            ("expected_affected_files", "affected_files"),
            ("expected_affected_files_k", "affected_files"),
            ("expected_call_chain", "call_chain"),
            ("expected_tasks", "tasks"),
            ("expected_order", "order"),
            ("expected_modifiable", "modifiable"),
            ("expected_blocked", "blocked"),
            ("expected_rollback_points", "rollback_points"),
            ("expected_cycle_path", "cycle_path"),
            ("expected_hallucinated_items", "hallucinated_items"),
        ]
        # dict 列表字段需提取子字段（模型常返回 [{"function":...}] 而非 ["func"]）
        dict_extractors = {
            "call_chain": "function",
            "tasks": "name",
            "files": "name",
            "changes": "file",
        }
        for attr, key in list_fields:
            exp_list = getattr(case, attr, [])
            if not exp_list:
                continue
            got_raw = result.get(key, [])
            extractor = dict_extractors.get(key)
            if (
                extractor
                and isinstance(got_raw, list)
                and got_raw
                and isinstance(got_raw[0], dict)
            ):
                got_list = [
                    str(item.get(extractor, "")) for item in got_raw if isinstance(item, dict)
                ]
            else:
                got_list = got_raw if isinstance(got_raw, list) else [str(got_raw)]
            exp_set = {str(x).lower() for x in exp_list}
            got_set = {str(x).lower() for x in got_list}
            inter = len(exp_set & got_set)
            p = inter / len(got_set) if got_set else 0.0
            r = inter / len(exp_set) if exp_set else 0.0
            p_rates.append(p)
            r_rates.append(r)
            if exp_set != got_set:
                em_all = 0

        # parallel_groups（列表的列表，按组集合匹配）
        if case.expected_parallel_groups:
            got_raw = result.get("parallel_groups", [])
            exp_set = {tuple(sorted(g)) for g in case.expected_parallel_groups}
            got_set = (
                {tuple(sorted(g)) for g in got_raw}
                if got_raw
                and isinstance(got_raw, list)
                and all(isinstance(g, list) for g in got_raw)
                else set()
            )
            inter = len(exp_set & got_set)
            p = inter / len(got_set) if got_set else 0.0
            r = inter / len(exp_set) if exp_set else 0.0
            p_rates.append(p)
            r_rates.append(r)
            if exp_set != got_set:
                em_all = 0

        # 3. 字符串字段（包含匹配）
        str_fields = [
            ("expected_tool", "tool"),
            ("expected_root_cause", "root_cause"),
            ("expected_answer", "answer"),
        ]
        for attr, key in str_fields:
            exp_str = getattr(case, attr, "")
            if not exp_str:
                continue
            # expected_tool 兼容 function_calling 输出的 "function" 键 (P类 Tool 轴)
            if attr == "expected_tool":
                got = str(result.get(key) or result.get("function") or "").lower()
            else:
                got = str(result.get(key, "")).lower()
            match = 1 if exp_str.lower() in got else 0
            p_rates.append(match)
            r_rates.append(match)
            if not match:
                em_all = 0

        # bug_location 在 bugs[].location 里
        if case.expected_bug_location:
            bugs = result.get("bugs", [])
            if isinstance(bugs, list):
                loc_text = " ".join(
                    str(b.get("location", "")) for b in bugs if isinstance(b, dict)
                ).lower()
            else:
                loc_text = ""
            match = 1 if case.expected_bug_location.lower() in loc_text else 0
            p_rates.append(match)
            r_rates.append(match)
            if not match:
                em_all = 0

        # 4. int 字段（expected_step_count → 检查 steps 长度）
        if case.expected_step_count and case.expected_step_count > 0:
            steps = result.get("steps", [])
            got_count = len(steps) if isinstance(steps, list) else 0
            match = 1 if got_count == case.expected_step_count else 0
            p_rates.append(match)
            r_rates.append(match)
            if not match:
                em_all = 0

        # 4b. P类 Tool 轴字段 (ROADMAP-02)
        # expected_function_args: function_calling 参数键值匹配
        if case.expected_function_args:
            args = result.get("arguments", {})
            if not isinstance(args, dict):
                args = {}
            arg_hits = 0.0
            for k, v in case.expected_function_args.items():
                got_v = args.get(k)
                if got_v is None:
                    continue
                if v and str(v).lower() in str(got_v).lower():
                    arg_hits += 1.0
                else:
                    arg_hits += 0.5  # key 存在但 value 不符
            arg_rate = arg_hits / len(case.expected_function_args)
            p_rates.append(arg_rate)
            r_rates.append(arg_rate)
            if arg_rate < 1.0:
                em_all = 0

        # expected_tool_sequence: tool_chaining 有序子序列匹配
        if case.expected_tool_sequence:
            steps = result.get("steps", [])
            got_tools: list[str] = []
            if isinstance(steps, list):
                for s in steps:
                    if isinstance(s, dict):
                        t = s.get("tool") or s.get("function") or ""
                        if t:
                            got_tools.append(str(t).lower())
                    elif isinstance(s, str):
                        got_tools.append(s.lower())
            # 检查 expected 是否为 got 的有序子序列
            seq_hits = 0
            gi = 0
            for et in case.expected_tool_sequence:
                etl = et.lower()
                while gi < len(got_tools) and got_tools[gi] != etl:
                    gi += 1
                if gi < len(got_tools):
                    seq_hits += 1
                    gi += 1
            seq_rate = seq_hits / len(case.expected_tool_sequence)
            p_rates.append(seq_rate)
            r_rates.append(seq_rate)
            if seq_rate < 1.0:
                em_all = 0

        # 5. expected_contains 关键词命中率（兜底，几乎所有 case 都有）
        kws = list(case.expected_contains or [])
        if kws:
            hits = sum(1 for kw in kws if kw.lower() in text)
            rate = hits / len(kws)
            p_rates.append(rate)
            r_rates.append(rate)
            if hits != len(kws):
                em_all = 0

        if not p_rates:
            return None

        p = sum(p_rates) / len(p_rates)
        r = sum(r_rates) / len(r_rates)
        ed = round(max(1.0 - (p + r) / 2, 0.0), 3)
        return (round(p, 3), round(r, 3), ed, em_all)

    def _compute_speed(self) -> SpeedResult:
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
            if latencies and self._all_tokens and sum(latencies) > 0
            else 0.0,
            time_to_first_token_ms=round(
                statistics.mean(self._all_ttft_ms),
                1,
            )
            if self._all_ttft_ms
            else 0.0,
        )

    # ── P2 Cost 轴 ───────────────────────────────────────
    # D-MCE-07: 成本是维度非硬门; claude 贵但必要时仍可用
    # 本地模型成本≈0; 云端按 provider_data.py 定价估算

    def _compute_cost(self) -> CostBreakdown:
        """P2 Cost 轴: 从 _all_tokens 派生考试成本。

        本地模型 (OllamaChat): 成本≈0, deployment_mode=local
        云端模型 (DeepSeekV4Chat 等): 按 provider_data.py 定价估算

        token 估算策略:
            - _all_tokens 记录每次推断的生成 token (output)
            - input_tokens 用 output 近似 (无法精确区分时的合理近似)
            - 本地模型无论多少 token, cost_usd=0
        """
        provider, mode = self._detect_deployment_mode()
        price_in, price_out = self._lookup_cost_per_1k(provider)

        output_tokens = sum(self._all_tokens) if self._all_tokens else 0
        # 近似: input ≈ output (OllamaChat 仅返回 eval_count, 无法精确区分)
        input_tokens = output_tokens
        total_tokens = input_tokens + output_tokens
        total_calls = len(self._all_tokens)

        cost_usd = (
            input_tokens / 1000.0 * price_in
            + output_tokens / 1000.0 * price_out
        )

        return CostBreakdown(
            deployment_mode=mode,
            provider=provider,
            total_calls=total_calls,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            price_per_1k_input=price_in,
            price_per_1k_output=price_out,
            estimated_cost_usd=round(cost_usd, 6),
        )

    def _detect_deployment_mode(self) -> tuple[str, str]:
        """检测部署模式 + 供应商标识。

        优先从 chat 对象类名判断, 其次从 model_id 关键字匹配。

        Returns:
            (provider, mode): provider ∈ {local, zhipu, deepseek, openai_azure, anthropic}
                              mode ∈ {local, api}
        """
        model_id = (self._model_id or "").lower()
        chat_cls = type(self._chat).__name__.lower()

        # 1. 优先从 chat 对象类名判断 (最可靠)
        if "ollama" in chat_cls:
            return ("local", "local")
        if "deepseek" in chat_cls:
            return ("deepseek", "api")
        if "anthropic" in chat_cls or "claude" in chat_cls:
            return ("anthropic", "api")
        if "openai" in chat_cls:
            return ("openai_azure", "api")
        if "zhipu" in chat_cls or "glm" in chat_cls:
            return ("zhipu", "api")

        # 2. 从 model_id 关键字匹配
        if "deepseek" in model_id:
            return ("deepseek", "api")
        if "claude" in model_id or "anthropic" in model_id:
            return ("anthropic", "api")
        if "gpt" in model_id or "openai" in model_id:
            return ("openai_azure", "api")
        if "glm" in model_id or "zhipu" in model_id:
            return ("zhipu", "api")

        # 3. 默认本地 (Ollama 等本地推理, 成本≈0)
        return ("local", "local")

    def _lookup_cost_per_1k(self, provider: str) -> tuple[float, float]:
        """从 provider_data.py 查询供应商定价。

        Returns:
            (price_per_1k_input, price_per_1k_output) in USD
            本地或未知供应商返回 (0.0, 0.0)
        """
        if provider == "local":
            return (0.0, 0.0)
        try:
            from zephyr.intelligence.model_profiling.provider_data import DEFAULT_PROVIDERS
            info = DEFAULT_PROVIDERS.get(provider, {})
            return (
                float(info.get("price_per_1k_input", 0.0)),
                float(info.get("price_per_1k_output", 0.0)),
            )
        except Exception:
            _log.warning("CostBreakdown: provider_data lookup failed for %s", provider)
            return (0.0, 0.0)

    def _run_hallucination(self, breadth: BreadthResult) -> HallucinationResult:
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
                    except Exception as e:
                        logger.warning("suppressed error in exam_orchestrator", exc_info=True)

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
        """稳轴: cold → load → hot 三阶段漂移测试（v3.0.5 真实实现）。

        cold:  单次冷启（首个 breadth 通过能力），记录基线输出 + 延迟 + 幻觉标志
        load:  连续 N 次压载（轮换 breadth 通过的能力），施加热负载
        hot:   复测冷启同题，对比输出漂移 + 速度漂移 + 幻觉漂移

        判稳阈值：output_drift < 0.3 且 speed_drift_ratio < 1.0 且幻觉无恶化。
        失败返回 DriftResult(tested=False) 不阻塞考试流程。
        """
        try:
            passed_caps = [c for c in CAPABILITIES if c not in breadth.failed_capabilities]
            if not passed_caps:
                return DriftResult(tested=False)

            probe_case = CASES_BY_CAPABILITY[passed_caps[0]][0]

            # Phase 1: cold — 单次冷启基线
            cold_result = self._infer(probe_case)
            cold_latency = self._all_latencies_ms[-1] if self._all_latencies_ms else 1.0
            cold_fab = 1 if self._check_fabrication(probe_case, cold_result) else 0

            # Phase 2: load — 连续 N 次压载
            load_n = 5
            for i in range(load_n):
                cap = passed_caps[i % len(passed_caps)]
                case = CASES_BY_CAPABILITY[cap][0]
                self._infer(case)

            # Phase 3: hot — 复测冷启同题
            hot_result = self._infer(probe_case)
            hot_latency = self._all_latencies_ms[-1] if self._all_latencies_ms else 1.0
            hot_fab = 1 if self._check_fabrication(probe_case, hot_result) else 0

            # 输出漂移（token 集合 Jaccard 距离）
            cold_str = json.dumps(cold_result, sort_keys=True, ensure_ascii=False)
            hot_str = json.dumps(hot_result, sort_keys=True, ensure_ascii=False)
            cold_tokens = set(cold_str.split())
            hot_tokens = set(hot_str.split())
            union = cold_tokens | hot_tokens
            output_drift = (
                1.0 - len(cold_tokens & hot_tokens) / max(len(union), 1)
                if union
                else 0.0
            )

            # 速度漂移比（hot 相对 cold 的延迟变化率）
            speed_drift_ratio = (hot_latency - cold_latency) / cold_latency if cold_latency > 0 else 0.0

            # 幻觉漂移增量（恶化为正）
            hallucination_drift_delta = float(hot_fab - cold_fab)

            stable = (
                output_drift < 0.3
                and speed_drift_ratio < 1.0
                and hallucination_drift_delta <= 0
            )

            return DriftResult(
                tested=True,
                output_drift=round(output_drift, 3),
                speed_drift_ratio=round(speed_drift_ratio, 3),
                hallucination_drift_delta=round(hallucination_drift_delta, 3),
                stable=stable,
            )
        except Exception as e:
            _log.warning("ExamOrchestrator: drift test failed: %s", e)
            return DriftResult(tested=False)

    def _compute_olympiad_pass_rate(self) -> float:
        """v3.0.5: 奥赛题通过率——用于奥赛封顶机制。

        无奥赛题时返回 1.0（不封顶），保持向后兼容。
        """
        if not self._olympiad_case_results:
            return 1.0
        return sum(self._olympiad_case_results) / len(self._olympiad_case_results)

    def _compute_overall(self, passport: CapabilityPassport) -> float:
        """v3.0.5: 综合分 = 加权原始分，经奥赛封顶。

        权重：breadth 0.35 + depth 0.50 + (1-halluc) 0.15
        奥赛封顶：通过率 <25%→B+(0.80)；<50%→A(0.85)；<75%→A-(0.88)；≥75%→A+(1.0)
        """
        b = passport.breadth.score
        d = passport.depth.overall_score
        h = 1.0 - passport.hallucination.overall_rate
        raw = 0.35 * b + 0.50 * d + 0.15 * h

        pass_rate = self._compute_olympiad_pass_rate()
        if pass_rate < 0.25:
            cap = 0.80  # B+
        elif pass_rate < 0.50:
            cap = 0.85  # A
        elif pass_rate < 0.75:
            cap = 0.88  # A-
        else:
            cap = 1.0   # A+ 解锁

        return round(min(raw, cap), 3)

    def _build_recommendations(self, passport: CapabilityPassport) -> Recommendations:
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
        t0 = time.time()
        raw = self._chat.inference(case.capability, case.prompt)
        elapsed_ms = (time.time() - t0) * 1000.0
        self._all_latencies_ms.append(elapsed_ms)

        tokens = raw.get("token_count", raw.get("eval_count", 0))
        if tokens:
            self._all_tokens.append(tokens)

        # v3.0.5: 注入耗时供 _score_capability 时间折扣（下划线前缀不干扰 _compute_metrics）
        if isinstance(raw, dict):
            raw["_elapsed_ms"] = elapsed_ms
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
        if case.capability in ("code_fix", "code_edit_precision", "refactor", "dead_code_removal"):
            field = (
                "fixes"
                if case.capability in ("code_fix", "code_edit_precision")
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
        # 过滤 _ 前缀的内部注入字段 (如 _elapsed_ms), 避免元数据干扰相似度判断
        a_clean = {k: v for k, v in a.items() if not k.startswith("_")} if isinstance(a, dict) else a
        b_clean = {k: v for k, v in b.items() if not k.startswith("_")} if isinstance(b, dict) else b
        a_str = json.dumps(a_clean, sort_keys=True, ensure_ascii=False)
        b_str = json.dumps(b_clean, sort_keys=True, ensure_ascii=False)
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

    @staticmethod
    def _validate_result(result: dict, case: ExamTestCase) -> bool:
        """验证模型返回结果是否有效（防作弊检测）。

        检测项:
        1. 泄露答案字段: result 中包含 expected_* 字段 → 无效
        2. 数值越界: precision/recall 超出 [0,1] 范围 → 无效
        """
        if not isinstance(result, dict):
            return False

        # 检测泄露答案字段
        suspicious_keys = {"expected_category", "expected_tags", "expected_old_str",
                          "expected_contains", "expected_needs_human",
                          "expected_structure_keys"}
        leaked = suspicious_keys & set(result.keys())
        if leaked:
            return False

        # 检测数值越界
        for field in ("precision", "recall", "f1"):
            val = result.get(field)
            if val is not None:
                try:
                    v = float(val)
                    if v < 0.0 or v > 1.0:
                        return False
                except (TypeError, ValueError):
                    return False

        return True

    def _detect_optimization(self, case: ExamTestCase, result: dict) -> bool:
        """检测模型是否针对 benchmark 优化（反作弊）。

        检测项:
        1. code_fix: old_str 与 expected_old_str 完全匹配（无推理过程）
        2. task_classification: category 精确匹配但无 reason 字段
        """
        suspicious = False

        if case.capability in ("code_fix", "code_edit_precision"):
            fixes = result.get("fixes", [])
            for entry in fixes:
                old_str = entry.get("old_str", "")
                if old_str and old_str.strip() == case.expected_old_str.strip():
                    suspicious = True
                    break

        if case.capability == "task_classification":
            category = result.get("category", "")
            if category == case.expected_category and "reason" not in result:
                suspicious = True

        if suspicious:
            self._optimization_suspicions += 1

        return suspicious

    # ══════════════════════════════════════════════════════════
    # P2: 三级考试模式 (Quick / Standard / Deep) + 六维幻觉
    # ══════════════════════════════════════════════════════════

    # Quick Mode 幻觉检测的关键能力 (5 项, 每项 2 次推断 = 10 次)
    _QUICK_HALLU_CAPS: tuple[str, ...] = (
        "hallucination_detect",
        "rule_comprehension",
        "safety_judgment",
        "summary_extraction",
        "code_generate",
    )

    @staticmethod
    def _check_overclaim(case: ExamTestCase, result: dict) -> bool:
        """P2: 检查过度声称 — 声称做了但实际未做。

        启发式: 输出含"已完成/已修复/已创建"等动词, 但对应字段为空。
        """
        if not isinstance(result, dict):
            return False
        claim_keywords = [
            "已完成", "已修复", "已创建", "已删除", "已重构", "已实现",
            "completed", "fixed", "created", "removed", "refactored", "implemented",
        ]
        text = json.dumps(result, ensure_ascii=False).lower()
        has_claim = any(kw in text for kw in claim_keywords)
        if not has_claim:
            return False
        # 检查对应字段是否为空
        field_kws = {
            "fixes": ["已修复", "fixed"],
            "changes": ["已重构", "refactored"],
            "dead_sections": ["已删除", "removed"],
            "tags": ["已完成", "completed"],
            "generated_code": ["已实现", "implemented"],
        }
        for field, kws in field_kws.items():
            if any(kw in text for kw in kws):
                val = result.get(field, None)
                if val is None:
                    return True
                if isinstance(val, (list, str)) and len(val) == 0:
                    return True
        return False

    @staticmethod
    def _check_source_confusion(case: ExamTestCase, result: dict) -> bool:
        """P2: 检查来源混淆 — 引用了 prompt/input_files 中不存在的文件名。

        启发式: result 中引用的 xxx.py 不在 case.prompt 或 input_files 中。
        """
        if not isinstance(result, dict):
            return False
        import re as _re
        result_text = json.dumps(result, ensure_ascii=False)
        referenced = set(_re.findall(r'[\w/\\]+\.py', result_text))
        if not referenced:
            return False
        prompt_files = set(_re.findall(r'[\w/\\]+\.py', case.prompt))
        input_files = set(case.input_files.keys())
        legit = prompt_files | input_files
        # 通用文件名豁免 (常见但不视为混淆)
        generic = {"__init__.py", "setup.py", "conftest.py", "main.py", "test.py"}
        confused = referenced - legit - generic
        return len(confused) > 0

    @staticmethod
    def _check_instruction_drift(case: ExamTestCase, result: dict) -> bool:
        """P2: 检查指令偏离 — 输出结构不符合 expected_structure_keys。

        启发式: 复用 _check_structure 判断输出是否包含指令要求的字段。
        若 case 无 expected_structure_keys 则跳过 (无法判定)。
        """
        if not isinstance(result, dict) or not case.expected_structure_keys:
            return False
        return not ExamOrchestrator._check_structure(
            result, case.expected_structure_keys
        )

    @staticmethod
    def _check_format_hallucination(case: ExamTestCase, result: dict) -> bool:
        """P2: 检查格式幻觉 — 字段值类型异常。

        启发式检测:
          1. list 字段被序列化为字符串 (如 "[\"a\",\"b\"]" 而非 ["a","b"])
          2. 字段值类型与常见预期严重不符 (如要求 str 但给了 dict)
        """
        if not isinstance(result, dict) or not case.expected_structure_keys:
            return False
        for key in case.expected_structure_keys:
            val = result.get(key)
            if val is None:
                continue  # instruction_drift 已处理缺失字段
            # 检测: list 字段被序列化为 JSON 字符串
            if isinstance(val, str) and val.strip().startswith("[") and val.strip().endswith("]"):
                try:
                    parsed = json.loads(val)
                    if isinstance(parsed, list):
                        return True  # 应该是 list 但给了 stringified JSON
                except (json.JSONDecodeError, ValueError):
                    pass
            # 检测: dict 字段被序列化为 JSON 字符串
            if isinstance(val, str) and val.strip().startswith("{") and val.strip().endswith("}"):
                try:
                    parsed = json.loads(val)
                    if isinstance(parsed, dict):
                        return True
                except (json.JSONDecodeError, ValueError):
                    pass
        return False

    @staticmethod
    def _check_quantity_hallucination(case: ExamTestCase, result: dict) -> bool:
        """P2: 检查数量幻觉 — 输出集合异常膨胀。

        启发式: list/dict 字段长度超过阈值 (默认 20) 视为异常膨胀。
        常见于模型"刷量"行为 (如编造大量虚假标签/文件)。
        """
        if not isinstance(result, dict):
            return False
        _QTY_THRESHOLD = 20
        for val in result.values():
            if isinstance(val, list) and len(val) > _QTY_THRESHOLD:
                return True
            if isinstance(val, dict) and len(val) > _QTY_THRESHOLD:
                return True
        return False

    def _run_hallucination_six_dim(
        self,
        breadth: BreadthResult,
        *,
        quick: bool = False,
    ) -> HallucinationBreakdown:
        """P2: 九维幻觉检测 (参考 ChatGPT 建议 + 业界实践)。

        九维:
            fabrication          _check_fabrication (事实编造)
            inconsistency        _outputs_similar (输出不一致, 2次推断值对比)
            refusal              _check_refusal (过度拒绝)
            overclaim            _check_overclaim (过度声称)
            context_drift        独立检测 (2次输出键集不同 = 忘记指令结构)
            source_confusion     _check_source_confusion (来源混淆)
            instruction_drift    _check_instruction_drift (指令偏离)
            format_hallucination _check_format_hallucination (格式幻觉)
            quantity_hallucination _check_quantity_hallucination (数量幻觉)

        Args:
            breadth: breadth 结果 (跳过 failed 能力)
            quick: True=只测 5 关键能力 (省时), False=测全部通过能力
        """
        from zephyr.intelligence.model_profiling.capability_passport import (
            HallucinationBreakdown,
        )

        if quick:
            caps_to_test = self._QUICK_HALLU_CAPS
        else:
            caps_to_test = tuple(CAPABILITIES)

        caps = [
            c for c in caps_to_test
            if c not in breadth.failed_capabilities and c in CASES_BY_CAPABILITY
        ]
        if not caps:
            return HallucinationBreakdown()

        fab = inc = ref = ovc = sc = cd = idr = fmh = qh = 0
        total = 0

        for cap_name in caps:
            cases = CASES_BY_CAPABILITY.get(cap_name, [])
            if not cases:
                continue
            case = cases[0]
            total += 1
            try:
                result = self._infer(case)
                if self._check_fabrication(case, result):
                    fab += 1
                if self._check_overclaim(case, result):
                    ovc += 1
                if self._check_source_confusion(case, result):
                    sc += 1
                if self._check_refusal(result):
                    ref += 1
                if self._check_instruction_drift(case, result):
                    idr += 1
                if self._check_format_hallucination(case, result):
                    fmh += 1
                if self._check_quantity_hallucination(case, result):
                    qh += 1
                # inconsistency + context_drift: 2次推断对比 (独立检测)
                try:
                    result2 = self._infer(case)
                    # context_drift: 两次输出键集不同 = 忘记指令结构
                    keys1 = set(k for k in (result.keys() if isinstance(result, dict) else [])
                                if not k.startswith("_"))
                    keys2 = set(k for k in (result2.keys() if isinstance(result2, dict) else [])
                                if not k.startswith("_"))
                    if keys1 != keys2:
                        cd += 1  # 键集漂移
                    elif not self._outputs_similar(result, result2):
                        inc += 1  # 键集相同但值差异大
                except Exception as e:
                    logger.warning("suppressed error in exam_orchestrator", exc_info=True)
            except Exception:
                ref += 1

        if total == 0:
            return HallucinationBreakdown()

        return HallucinationBreakdown(
            fabrication=round(fab / total, 3),
            inconsistency=round(inc / total, 3),
            refusal=round(ref / total, 3),
            overclaim=round(ovc / total, 3),
            context_drift=round(cd / total, 3),
            source_confusion=round(sc / total, 3),
            instruction_drift=round(idr / total, 3),
            format_hallucination=round(fmh / total, 3),
            quantity_hallucination=round(qh / total, 3),
        )

    def _pick_representative_case(self, cap_name: str) -> ExamTestCase | None:
        """P2 Quick Mode: 选代表题 (优先 medium, fallback easy)。"""
        cases = CASES_BY_CAPABILITY.get(cap_name, [])
        if not cases:
            return None
        for c in cases:
            if c.difficulty is Difficulty.MEDIUM:
                return c
        for c in cases:
            if c.difficulty is Difficulty.EASY:
                return c
        return cases[0]

    def run_quick_exam(self) -> QuickProfile:
        """P2 Quick Mode: 快速能力画像 (5-8 分钟)。

        策略:
            - 29 能力各跑 1 道 medium 代表题 (单次推断)
            - 幻觉检测: 5 个关键能力各 2 次推断 (六维细分)
            - 跳过 drift, olympiad
            - 输出 QuickProfile (能力分级 + 六维幻觉 + Top3 岗位推荐)

        总推断: 29 + 10 = 39 次 (本地模型 ~6 分钟)
        """
        from zephyr.intelligence.model_profiling.capability_passport import (
            BreadthResult,
            HallucinationBreakdown,
            QuickProfile,
            compute_grade_simple,
        )
        from zephyr.intelligence.model_profiling.job_matcher import JobMatcher

        self._start_ts = time.time()
        self._olympiad_case_results = []

        _log.info("ExamOrchestrator: starting QUICK exam for %s", self._model_id)

        # 1. 每能力 1 道代表题
        capability_scores: dict[str, float] = {}
        capability_grades: dict[str, str] = {}
        breadth_passed: list[str] = []
        breadth_failed: list[str] = []

        for cap_name in CAPABILITIES:
            case = self._pick_representative_case(cap_name)
            if case is None:
                breadth_failed.append(cap_name)
                capability_scores[cap_name] = 0.0
                capability_grades[cap_name] = "F"
                continue
            try:
                result = self._infer(case)
                if self._check_structure(result, case.expected_structure_keys):
                    breadth_passed.append(cap_name)
                    p, r, ed, em = self._compute_metrics(case, result)
                    score = max(p, r, float(em))
                else:
                    breadth_failed.append(cap_name)
                    score = 0.0
            except Exception:
                breadth_failed.append(cap_name)
                score = 0.0
            capability_scores[cap_name] = round(score, 3)
            capability_grades[cap_name] = compute_grade_simple(score)

        # 2. 六维幻觉检测 (5 关键能力)
        breadth = BreadthResult(
            score=len(breadth_passed) / len(CAPABILITIES) if CAPABILITIES else 0.0,
            passed=len(breadth_passed),
            total=len(CAPABILITIES),
            failed_capabilities=breadth_failed,
        )
        hallu = self._run_hallucination_six_dim(breadth, quick=True)

        # 3. 综合分 (五轴简化: breadth 0.35 + depth 0.50 + hallu 0.15)
        breadth_score = breadth.score
        nonzero = [s for s in capability_scores.values() if s > 0]
        depth_score = statistics.mean(nonzero) if nonzero else 0.0
        hallu_score = hallu.hallucination_score
        overall = 0.35 * breadth_score + 0.50 * depth_score + 0.15 * hallu_score

        # 4. 构建 QuickProfile
        profile = QuickProfile(
            model_id=self._model_id,
            exam_mode="quick",
            exam_timestamp=datetime.now(UTC).isoformat(),
            exam_duration_seconds=round(time.time() - self._start_ts, 2),
            capability_grades=capability_grades,
            capability_scores=capability_scores,
            hallucination=hallu,
            cost=self._compute_cost(),
            overall_score=round(overall, 3),
            overall_grade=compute_grade_simple(overall),
        )

        # 5. 岗位推荐 Top3
        try:
            matcher = JobMatcher()
            profile.recommendations = matcher.match_top(profile, n=3)
        except Exception as e:
            _log.warning("JobMatcher failed: %s", e)
            profile.notes.append(f"job_match_failed: {e}")

        _log.info(
            "ExamOrchestrator: QUICK complete — grade=%s score=%.2f hallu=%.3f (%.1fs)",
            profile.overall_grade, profile.overall_score,
            hallu.overall_rate, profile.exam_duration_seconds,
        )
        return profile

    def run_standard_exam(self, *, skip_drift: bool = True) -> CapabilityPassport:
        """P2 Standard Mode: 标准评测 (20-30 分钟)。

        = run_full_exam(skip_drift=True) 别名, n=1 单次采样。
        适合正式入职评估, 输出完整 CapabilityPassport。
        """
        if self._depth_samples_per_case != 1:
            _log.warning(
                "Standard mode expects n=1, got n=%d", self._depth_samples_per_case
            )
        return self.run_full_exam(skip_drift=skip_drift)

    def run_deep_exam(self, *, judge_chat: Any = None) -> CapabilityPassport:
        """P2 Deep Mode: 旗舰深评 (2-3 小时)。

        = run_full_exam(skip_drift=False) + 强制 n>=3 + 可选 LLM judge。
        适合旗舰候选模型深度校准, 区分度拉满。
        """
        if self._depth_samples_per_case < 3:
            _log.warning(
                "Deep mode forces n>=3, got n=%d, bumping to 3",
                self._depth_samples_per_case,
            )
            self._depth_samples_per_case = max(3, self._depth_samples_per_case)
        if judge_chat is not None:
            self._judge_chat = judge_chat
            self._judge = ExamJudge(judge_chat)
        return self.run_full_exam(skip_drift=False)

    def run_exam(
        self,
        mode: str = "standard",
        **kwargs: Any,
    ) -> QuickProfile | CapabilityPassport:
        """P2 统一考试入口。

        Args:
            mode: "quick" (5-8min) | "standard" (20-30min) | "deep" (2-3h)
            **kwargs: 传给对应模式的参数 (如 judge_chat for deep)

        Returns:
            QuickProfile (quick) 或 CapabilityPassport (standard/deep)
        """
        mode = mode.lower().strip()
        if mode == "quick":
            return self.run_quick_exam()
        elif mode == "standard":
            return self.run_standard_exam(**kwargs)
        elif mode == "deep":
            return self.run_deep_exam(**kwargs)
        else:
            raise ValueError(
                f"unknown exam mode: {mode!r} (expected: quick/standard/deep)"
            )


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
