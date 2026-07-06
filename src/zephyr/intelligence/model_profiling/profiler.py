# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] zephyr.intelligence.model_profiling.profiler
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.intelligence.model_profiling.benchmark_suite; zephyr.intelligence.model_profiling.model_discovery
# [CONSUMERS] MOD-INF-009;MOD-INF-036
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 模型能力评测;7维度benchmark;评分排名
# [MODIFY-GUARD] docs/03_modules/_cross_layer/model_profiler/blueprint.md;src/zephyr/intelligence/model_profiling/__init__.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ProfilerError;EvaluationError
# [TESTS] tests/test_model_profiler/
# [A_module] module_id=MOD-RSC_profiler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ModelProfiler — 核心性能分析引擎
===================================
对每个发现的模型运行全维度 benchmark 测试，收集：
  - 延迟 (P50/P95/P99, ms)
  - 吞吐 (tokens/s)
  - 正确率 (per category)
  - 幻觉率 (hallucination rate)
  - 质量评分 (format compliance, instruction following)
  - 综合评分 (weighted composite score)

用法
----
    profiler = ModelProfiler()
    results = profiler.profile_all()
    profiler.print_ranking(results)
"""

from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from zephyr.intelligence.model_profiling.benchmark_suite import (
    ALL_BENCHMARK_CASES,
    CATEGORY_MAP,
    BenchmarkCase,
)
from zephyr.intelligence.model_profiling.model_discovery import (
    DEFAULT_OLLAMA_URL,
    DiscoveredModel,
    ModelDiscovery,
)
from zephyr.shared.utils.time_utils import now_utc

_log = logging.getLogger(__name__)

MAX_OLLAMA_MODELS = 10

SKIP_MODEL_PATTERNS = [
    "bge",
    "embed",
    "nomic",
    "mxbai",
    "all-minilm",
    "multilingual-e5",
    "snowflake",
    "gte-",
    "e5-",
    "stella",
    "jina-embed",
]


@dataclass
class CaseResult:
    case_id: str
    category: str
    subcategory: str
    passed: bool
    score: float
    latency_ms: float
    tokens_generated: int
    tokens_per_second: float
    output_text: str
    expected_matches: int
    total_expected: int
    forbidden_hits: int
    error: str = ""


@dataclass
class ModelProfile:
    model_name: str
    source: str
    benchmark_date: str = ""
    total_tests: int = 0
    passed_tests: int = 0
    average_score: float = 0.0
    latency_p50_ms: float = 0.0
    latency_p95_ms: float = 0.0
    latency_p99_ms: float = 0.0
    throughput_tokens_per_sec: float = 0.0
    total_tokens: int = 0
    total_time_ms: float = 0.0

    category_scores: dict[str, float] = field(default_factory=dict)
    hallucination_rate: float = 0.0
    refusal_rate: float = 0.0
    json_validity_rate: float = 0.0
    code_validity_rate: float = 0.0

    case_results: list[CaseResult] = field(default_factory=list)
    recommendation: str = ""
    rank: int = 0
    available: bool = True
    error: str = ""


class ModelProfiler:
    """核心性能分析引擎——对每个模型运行全维度 benchmark。"""

    def __init__(
        self,
        ollama_url: str = DEFAULT_OLLAMA_URL,
        timeout_per_case_s: float = 60.0,
        max_ollama_models: int = MAX_OLLAMA_MODELS,
    ) -> None:
        self._url = ollama_url.rstrip("/")
        self._timeout = timeout_per_case_s
        self._max_models = max_ollama_models
        self._discovery = ModelDiscovery(ollama_url=ollama_url)

    def profile_all(self) -> list[ModelProfile]:
        """对所有可用模型运行全量 benchmark。"""
        models = self._discovery.discover_all()
        ollama_models = [m for m in models if m.source == "ollama"][: self._max_models]
        remote_models = [m for m in models if m.source == "remote_api"]

        all_profiles: list[ModelProfile] = []

        for model in ollama_models:
            if self._should_skip_model(model.name):
                _log.info("Skipping non-chat model: %s", model.name)
                continue
            _log.info("Profiling Ollama model: %s", model.name)
            profile = self._profile_ollama_model(model)
            if profile is not None:
                all_profiles.append(profile)

        for model in remote_models:
            _log.info("Remote model %s skipped (needs API key injection)", model.name)
            profile = ModelProfile(
                model_name=model.name,
                source="remote_api",
                available=True,
                recommendation="SKIPPED — remote model profiling requires API key injection",
            )
            all_profiles.append(profile)

        self._rank_profiles(all_profiles)
        return all_profiles

    def profile_ollama_only(self) -> list[ModelProfile]:
        """仅对 Ollama 本地模型进行 benchmark。"""
        models = self._discovery.discover_ollama()
        if not models:
            _log.warning("No Ollama models found — is Ollama running?")
            return []

        profiles: list[ModelProfile] = []
        for model in models[: self._max_models]:
            if self._should_skip_model(model.name):
                _log.info("Skipping non-chat model: %s", model.name)
                continue
            profile = self._profile_ollama_model(model)
            if profile is not None:
                profiles.append(profile)

        self._rank_profiles(profiles)
        return profiles

    def quick_profile(self, model_name: str) -> ModelProfile | None:
        """对单个模型跑快速 benchmark（仅 latency + semantic 维度）。"""

        quick_cases = CATEGORY_MAP.get("latency", [])[:3] + CATEGORY_MAP.get("semantic", [])[:2]

        profile = ModelProfile(
            model_name=model_name,
            source="ollama",
            benchmark_date=now_utc().isoformat(),
            available=True,
        )

        case_results: list[CaseResult] = []
        latencies: list[float] = []
        total_tokens = 0
        total_time = 0.0

        for case in quick_cases:
            try:
                start = time.perf_counter()
                content, token_count = self._call_ollama(model_name, case.prompt, case.max_tokens)
                elapsed_ms = (time.perf_counter() - start) * 1000
                latencies.append(elapsed_ms)
                total_tokens += token_count
                total_time += elapsed_ms

                score = self._score_output(case, content)
                expected_matches = sum(1 for p in case.expected_patterns if re.search(p, content, re.IGNORECASE))
                forbidden_hits = sum(1 for p in case.forbidden_patterns if re.search(p, content, re.IGNORECASE))
                passed = score >= 0.5 and forbidden_hits == 0

                tps = (token_count / elapsed_ms * 1000) if elapsed_ms > 0 else 0.0
                cr = CaseResult(
                    case_id=case.case_id,
                    category=case.category,
                    subcategory=case.subcategory,
                    passed=passed,
                    score=score,
                    latency_ms=elapsed_ms,
                    tokens_generated=token_count,
                    tokens_per_second=tps,
                    output_text=content[:500],
                    expected_matches=expected_matches,
                    total_expected=len(case.expected_patterns),
                    forbidden_hits=forbidden_hits,
                )
                case_results.append(cr)
            except Exception as exc:
                cr = CaseResult(
                    case_id=case.case_id,
                    category=case.category,
                    subcategory=case.subcategory,
                    passed=False,
                    score=0.0,
                    latency_ms=0.0,
                    tokens_generated=0,
                    tokens_per_second=0.0,
                    output_text="",
                    expected_matches=0,
                    total_expected=len(case.expected_patterns),
                    forbidden_hits=0,
                    error=str(exc),
                )
                case_results.append(cr)

        profile.case_results = case_results
        profile.total_tests = len(case_results)
        profile.passed_tests = sum(1 for r in case_results if r.passed)
        profile.average_score = sum(r.score for r in case_results) / len(case_results) if case_results else 0.0
        if latencies:
            profile.latency_p50_ms = self._percentile(latencies, 0.50)
            profile.latency_p95_ms = self._percentile(latencies, 0.95)
            profile.latency_p99_ms = self._percentile(latencies, 0.99)
        profile.total_tokens = total_tokens
        profile.total_time_ms = total_time
        profile.throughput_tokens_per_sec = (total_tokens / total_time * 1000) if total_time > 0 else 0.0
        profile.recommendation = "quick_profile_only"
        return profile

    def _should_skip_model(self, model_name: str) -> bool:
        """跳过非对话模型（embedding 模型等）。"""
        lower = model_name.lower()
        return any(p in lower for p in SKIP_MODEL_PATTERNS)

    def _profile_ollama_model(self, model: DiscoveredModel) -> ModelProfile | None:
        profile = ModelProfile(
            model_name=model.name,
            source=model.source,
            benchmark_date=now_utc().isoformat(),
            available=True,
        )
        if model.size_gb > 0:
            profile.category_scores["model_size_gb"] = round(model.size_gb, 2)

        case_results: list[CaseResult] = []
        all_latencies: list[float] = []
        total_tokens = 0
        total_time = 0.0

        for case in ALL_BENCHMARK_CASES:
            try:
                start = time.perf_counter()
                content, token_count = self._call_ollama(model.name, case.prompt, case.max_tokens)
                elapsed_ms = (time.perf_counter() - start) * 1000
                all_latencies.append(elapsed_ms)
                total_tokens += token_count
                total_time += elapsed_ms

                score = self._score_output(case, content)
                expected_matches = sum(1 for p in case.expected_patterns if re.search(p, content, re.IGNORECASE))
                forbidden_hits = sum(1 for p in case.forbidden_patterns if re.search(p, content, re.IGNORECASE))
                passed = score >= 0.5 and forbidden_hits == 0

                tps = (token_count / elapsed_ms * 1000) if elapsed_ms > 0 else 0.0
                cr = CaseResult(
                    case_id=case.case_id,
                    category=case.category,
                    subcategory=case.subcategory,
                    passed=passed,
                    score=score,
                    latency_ms=elapsed_ms,
                    tokens_generated=token_count,
                    tokens_per_second=tps,
                    output_text=content[:500],
                    expected_matches=expected_matches,
                    total_expected=max(len(case.expected_patterns), 1),
                    forbidden_hits=forbidden_hits,
                )
                case_results.append(cr)
            except Exception as exc:
                _log.warning("Case %s failed for %s: %s", case.case_id, model.name, exc, exc_info=True)
                cr = CaseResult(
                    case_id=case.case_id,
                    category=case.category,
                    subcategory=case.subcategory,
                    passed=False,
                    score=0.0,
                    latency_ms=0.0,
                    tokens_generated=0,
                    tokens_per_second=0.0,
                    output_text="",
                    expected_matches=0,
                    total_expected=max(len(case.expected_patterns), 1),
                    forbidden_hits=0,
                    error=str(exc),
                )
                case_results.append(cr)

        self._populate_profile_stats(profile, case_results, all_latencies, total_tokens, total_time)
        return profile

    def _populate_profile_stats(
        self,
        profile: ModelProfile,
        case_results: list[CaseResult],
        all_latencies: list[float],
        total_tokens: int,
        total_time: float,
    ) -> None:
        profile.case_results = case_results
        profile.total_tests = len(case_results)
        profile.passed_tests = sum(1 for r in case_results if r.passed)
        profile.total_tokens = total_tokens
        profile.total_time_ms = total_time

        scores = [r.score for r in case_results] if case_results else [0.0]
        profile.average_score = sum(scores) / len(scores)

        if all_latencies:
            sorted_lat = sorted(all_latencies)
            profile.latency_p50_ms = self._percentile(sorted_lat, 0.50)
            profile.latency_p95_ms = self._percentile(sorted_lat, 0.95)
            profile.latency_p99_ms = self._percentile(sorted_lat, 0.99)

        profile.throughput_tokens_per_sec = (total_tokens / total_time * 1000) if total_time > 0 else 0.0

        for cat, cat_cases in CATEGORY_MAP.items():
            cat_results = [r for r in case_results if r.category == cat]
            if cat_results:
                cat_score = sum(r.score for r in cat_results) / len(cat_results)
                profile.category_scores[cat] = round(cat_score, 3)

        hallu_results = [r for r in case_results if r.category == "hallucination"]
        if hallu_results:
            profile.hallucination_rate = round(1.0 - sum(r.score for r in hallu_results) / len(hallu_results), 3)

        profile.refusal_rate = round(
            sum(
                1
                for r in case_results
                if r.error
                or (
                    r.output_text
                    and "不存在" not in r.output_text
                    and "无法" not in r.output_text
                    and len(r.output_text) < 5
                )
            )
            / max(len(case_results), 1),
            3,
        )

        json_cases = [
            r
            for r in case_results
            if r.category in ("latency", "quality")
            and any(
                c.category == "quality" and c.subcategory == "json_format"
                for c in ALL_BENCHMARK_CASES
                if c.case_id == r.case_id
            )
        ]
        if json_cases:
            profile.json_validity_rate = round(
                sum(1 for r in json_cases if _is_valid_json(r.output_text)) / len(json_cases), 3
            )

        code_cases = [r for r in case_results if r.category in ("code_generation", "code_fix")]
        if code_cases:
            profile.code_validity_rate = round(sum(r.score for r in code_cases) / len(code_cases), 3)

    def _call_ollama(self, model: str, prompt: str, max_tokens: int = 512) -> tuple[str, int]:
        import requests

        body: dict[str, Any] = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {
                "temperature": 0.0,
                "num_predict": max(max_tokens, 256),
            },
        }

        resp = requests.post(
            f"{self._url}/api/chat",
            json=body,
            timeout=self._timeout,
        )
        resp.raise_for_status()
        payload: dict[str, Any] = resp.json()

        message: dict[str, Any] = payload.get("message", {}) or {}
        content = message.get("content", "") or ""
        if not content:
            content = message.get("thinking", "") or ""
        if not content:
            content = payload.get("response", "") or ""
        eval_count = payload.get("eval_count", 0)
        if not eval_count and content:
            eval_count = len(content.split())
        if not eval_count:
            eval_count = 1
        return content.strip(), eval_count

    def _call_ollama_with_messages(
        self, model: str, messages: list[dict[str, str]], max_tokens: int = 512
    ) -> tuple[str, int]:
        import requests

        body: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.0,
                "num_predict": max_tokens,
            },
        }

        resp = requests.post(
            f"{self._url}/api/chat",
            json=body,
            timeout=self._timeout,
        )
        resp.raise_for_status()
        payload = resp.json()

        content = payload.get("message", {}).get("content", "")
        eval_count = payload.get("eval_count", 0)
        return content.strip(), max(eval_count, 1) if eval_count else len(content.split())

    @staticmethod
    def _score_output(case: BenchmarkCase, output: str) -> float:
        if not output:
            return 0.0

        score = 0.0
        if case.expected_patterns:
            matched = sum(1 for p in case.expected_patterns if re.search(p, output, re.IGNORECASE))
            score = matched / len(case.expected_patterns) * 0.6

        if case.forbidden_patterns:
            violations = sum(1 for p in case.forbidden_patterns if re.search(p, output, re.IGNORECASE))
            penalty = violations / len(case.forbidden_patterns) * 0.5
            score = max(0.0, score - penalty)

        if case.expected_output_type == "json":
            if _is_valid_json(output):
                score = max(score, 0.7)
            else:
                score *= 0.3
        elif case.expected_output_type == "code":
            if output.count("\n") >= 2 and ("def " in output or "class " in output or "async " in output):
                score = max(score, 0.5)

        if case.reference_answer and output:
            ref_words = set(case.reference_answer.lower().split())
            out_words = set(output.lower().split())
            if ref_words:
                overlap = len(ref_words & out_words) / len(ref_words)
                score = 0.4 * score + 0.6 * overlap

        return round(min(1.0, max(0.0, score)), 4)

    def _rank_profiles(self, profiles: list[ModelProfile]) -> None:
        scored = [p for p in profiles if p.average_score > 0 and p.available]
        scored.sort(key=lambda p: p.average_score, reverse=True)
        for i, p in enumerate(scored):
            p.rank = i + 1

        if scored:
            best = scored[0]
            best.recommendation = (
                f"BEST_OVERALL — score={best.average_score:.2f}, "
                f"P50={best.latency_p50_ms:.0f}ms, "
                f"throughput={best.throughput_tokens_per_sec:.0f} tok/s"
            )
            for p in scored[1:]:
                gap = best.average_score - p.average_score
                speed_gap = best.latency_p50_ms - p.latency_p50_ms
                p.recommendation = f"RANK #{p.rank} — gap={gap:.2f}, latency_delta={speed_gap:.0f}ms vs best"

    @staticmethod
    def _percentile(sorted_data: list[float], p: float) -> float:
        if not sorted_data:
            return 0.0
        k = (len(sorted_data) - 1) * p
        f = int(k)
        c = min(f + 1, len(sorted_data) - 1)
        if f == c:
            return sorted_data[f]
        frac = k - f
        return sorted_data[f] * (1 - frac) + sorted_data[c] * frac

    def print_ranking(self, profiles: list[ModelProfile]) -> None:
        header = (
            f"{'Rank':>4} {'Model':<30} {'Score':>7} {'P50ms':>8} {'P95ms':>8} {'Tok/s':>8} {'Pass':>6} {'Hallu%':>8}"
        )
        print("\n" + "=" * len(header))
        print("  Model Performance Benchmark Results")
        print("=" * len(header))
        print(header)
        print("-" * len(header))

        for p in sorted(profiles, key=lambda x: x.rank or 999):
            if not p.available:
                continue
            print(
                f"{p.rank:>4} "
                f"{p.model_name:<30} "
                f"{p.average_score:>6.2f} "
                f"{p.latency_p50_ms:>7.0f} "
                f"{p.latency_p95_ms:>7.0f} "
                f"{p.throughput_tokens_per_sec:>7.0f} "
                f"{p.passed_tests}/{p.total_tests:<5} "
                f"{p.hallucination_rate:>7.1%}"
            )

        print("-" * len(header))
        self._print_category_breakdown(profiles)

    def _print_category_breakdown(self, profiles: list[ModelProfile]) -> None:
        categories = ["code_generation", "code_fix", "semantic", "hallucination", "quality", "reasoning"]
        labels = {
            "code_generation": "代码生成",
            "code_fix": "代码修复",
            "semantic": "语义理解",
            "hallucination": "幻觉检测",
            "quality": "输出质量",
            "reasoning": "逻辑推理",
        }

        print("\n  Category Breakdown:")
        print(f"  {'Model':<30}", end="")
        for cat in categories:
            print(f" {labels[cat]:>8}", end="")
        print()

        for p in sorted(profiles, key=lambda x: x.rank or 999):
            if not p.available or p.average_score == 0:
                continue
            print(f"  {p.model_name:<30}", end="")
            for cat in categories:
                val = p.category_scores.get(cat, "-")
                if isinstance(val, float):
                    print(f" {val:>8.2f}", end="")
                else:
                    print(f" {val!s:>8}", end="")
            print()

        if scored := [p for p in profiles if p.average_score > 0 and p.available]:
            print(
                f"\n  >>> Best model: {scored[0].model_name} "
                f"(score={scored[0].average_score:.2f}, "
                f"P50={scored[0].latency_p50_ms:.0f}ms, "
                f"throughput={scored[0].throughput_tokens_per_sec:.0f} tok/s)"
            )


def _is_valid_json(text: str) -> bool:
    candidates = [text]
    if text.startswith("```"):
        inner = text.split("\n", 1)
        if len(inner) > 1:
            candidates.append(inner[1].replace("```", "").strip())
    for c in candidates:
        try:
            json.loads(c)
            return True
        except (json.JSONDecodeError, ValueError):
            continue
    brace_start = text.find("{")
    brace_end = text.rfind("}")
    if brace_start >= 0 and brace_end > brace_start:
        try:
            json.loads(text[brace_start : brace_end + 1])
            return True
        except (json.JSONDecodeError, ValueError):
            pass
    return False
