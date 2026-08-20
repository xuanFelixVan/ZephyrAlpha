#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""考试系统评分逻辑单元测试（合成数据，零成本，不调真实模型）。

验证 v3.0.5 三大改造的评分逻辑正确性：
  1. _time_weight 时间折扣边界值（exp(-t/260s)）
  2. _compute_olympiad_pass_rate 奥赛通过率边界
  3. _compute_overall 奥赛封顶机制（<25%→B+, <50%→A, <75%→A-, ≥75%→A+）
  4. 6 道奥赛题 expected 字段与 scorer 读取路径一致性（避免字段名错配导致全 0）

运行: python scripts/test_exam_scoring_unit.py
退出码: 0=全部通过, 1=有失败
"""

import json
import math
import sys
from pathlib import Path

# 注入 src 路径
_SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(_SRC))

from zephyr.intelligence.model_profiling.capability_passport import (  # noqa: E402
    BreadthResult,
    CapabilityPassport,
    DepthCapabilityResult,
    DepthResult,
    HallucinationResult,
    SpeedResult,
)
from zephyr.intelligence.model_profiling.exam_orchestrator import (  # noqa: E402
    _OLYMPIAD_CASE_PASS_THRESHOLD,
    ExamOrchestrator,
    _time_weight,
)
from zephyr.intelligence.model_profiling.exam_rubric import ExamRubric  # noqa: E402
from zephyr.intelligence.model_profiling.exam_test_cases import (  # noqa: E402
    ALL_EXAM_CASES,
    Difficulty,
)


# ── Mock Chat：返回预定 JSON，供 orchestrator 评分 ────────────
class _MockChat:
    """返回固定 JSON 的 mock chat，不调真实模型。"""

    def __init__(self, response: dict):
        self._response = response
        self._model = "mock"

    def inference(self, capability, prompt):
        # 返回副本，避免 _infer 注入 _elapsed_ms 污染
        return dict(self._response)


def _make_orch(response: dict) -> ExamOrchestrator:
    return ExamOrchestrator(_MockChat(response), model_id="mock")


# ═══════════════════════════════════════════════════════════════
# 1. _time_weight 边界值
# ═══════════════════════════════════════════════════════════════
def test_time_weight_boundaries():
    cases = [
        (0, 1.000),
        (9000, 0.966),  # 本地模型单题
        (60000, 0.794),  # thinking 模型单题
        (260000, 0.368),  # exp 衰减常数点
        (600000, 0.099),  # 防卡死上限，不归零
    ]
    for ms, expected in cases:
        got = round(_time_weight(ms), 3)
        assert abs(got - expected) < 0.005, f"_time_weight({ms}ms)={got} 期望~{expected}"
    # 负数容错
    assert _time_weight(-100) == 1.0, "负耗时应返回 1.0"
    # 单调递减
    assert _time_weight(1000) > _time_weight(60000) > _time_weight(600000)
    print("[PASS] _time_weight 边界值 (5 点 + 负数 + 单调性)")


# ═══════════════════════════════════════════════════════════════
# 2. _compute_olympiad_pass_rate 边界
# ═══════════════════════════════════════════════════════════════
def test_olympiad_pass_rate():
    orch = _make_orch({})

    # 无奥赛题 → 1.0（不封顶，向后兼容）
    orch._olympiad_case_results = []
    assert orch._compute_olympiad_pass_rate() == 1.0, "无奥赛题应返回 1.0"

    # 0/6 通过 → 0.0
    orch._olympiad_case_results = [False] * 6
    assert orch._compute_olympiad_pass_rate() == 0.0

    # 3/6 通过 → 0.5
    orch._olympiad_case_results = [True, False, True, False, True, False]
    assert abs(orch._compute_olympiad_pass_rate() - 0.5) < 1e-9

    # 6/6 通过 → 1.0
    orch._olympiad_case_results = [True] * 6
    assert orch._compute_olympiad_pass_rate() == 1.0

    print("[PASS] _compute_olympiad_pass_rate 边界 (空/0%/50%/100%)")


# ═══════════════════════════════════════════════════════════════
# 3. _compute_overall 奥赛封顶
# ═══════════════════════════════════════════════════════════════
def _make_passport(b=1.0, d=1.0, halluc_rate=0.0) -> CapabilityPassport:
    """合成满分 passport（breadth=1, depth=1, halluc=0）。"""
    p = CapabilityPassport(model_id="mock")
    p.breadth = BreadthResult(score=b, passed=1, total=1, failed_capabilities=[])
    p.depth = DepthResult(overall_score=d, capabilities={})
    p.hallucination = HallucinationResult(overall_rate=halluc_rate)
    p.speed = SpeedResult()  # SpeedResult 无 score 字段；_compute_overall 不读 speed
    return p


def test_overall_cap():
    orch = _make_orch({})

    # 满分 raw = 0.35*1 + 0.50*1 + 0.15*1 = 1.0
    passport = _make_passport()

    # pass_rate < 0.25 → 封顶 B+(0.80)
    orch._olympiad_case_results = [False] * 6
    assert orch._compute_overall(passport) == 0.80, "0% 通过应封顶 0.80(B+)"

    orch._olympiad_case_results = [True] + [False] * 5  # 1/6 ≈ 0.167 < 0.25
    assert orch._compute_overall(passport) == 0.80

    # pass_rate < 0.50 → 封顶 A(0.85)
    orch._olympiad_case_results = [True, True, False, False, False, False]  # 2/6 ≈ 0.33
    assert orch._compute_overall(passport) == 0.85, "33% 通过应封顶 0.85(A)"

    orch._olympiad_case_results = [True, True, True, False, False, False]  # 3/6 = 0.5 → 不<0.5
    assert orch._compute_overall(passport) == 0.88, "50% 通过应封顶 0.88(A-)"

    # pass_rate < 0.75 → 封顶 A-(0.88)
    orch._olympiad_case_results = [True, True, True, True, False, False]  # 4/6 ≈ 0.67
    assert orch._compute_overall(passport) == 0.88

    # pass_rate ≥ 0.75 → 解锁 A+(1.0)，不封顶
    orch._olympiad_case_results = [True, True, True, True, True, False]  # 5/6 ≈ 0.83
    assert orch._compute_overall(passport) == 1.0, "83% 通过应解锁 A+ (1.0)"

    # 无奥赛题 → 不封顶
    orch._olympiad_case_results = []
    assert orch._compute_overall(passport) == 1.0, "无奥赛题不封顶"

    # raw 低于 cap 时，取 raw（不虚高）
    low_passport = _make_passport(b=0.5, d=0.5, halluc_rate=0.5)
    orch._olympiad_case_results = [True] * 6  # cap=1.0
    raw = 0.35 * 0.5 + 0.50 * 0.5 + 0.15 * 0.5
    assert orch._compute_overall(low_passport) == round(raw, 3), "raw<cap 时应取 raw"

    print("[PASS] _compute_overall 奥赛封顶 (B+/A/A-/A+ 四档 + 无题不封 + raw<cap)")


# ═══════════════════════════════════════════════════════════════
# 4. 奥赛题 expected 字段与 scorer 一致性
#    构造"完美"合成结果，验证 scorer 能正确评分（非 0 即通过字段对齐）
# ═══════════════════════════════════════════════════════════════
def test_olympiad_field_consistency():
    oly_cases = [c for c in ALL_EXAM_CASES if c.difficulty in (Difficulty.OLYMPIAD, Difficulty.EXTREME)]
    assert len(oly_cases) == 9, f"期望 9 道奥赛题，实际 {len(oly_cases)}"

    # OLYMPIAD 题全部走 rubric/judge/executor 三轨评分（_score_olympiad_case），
    # 不走 _compute_metrics（后者仅用于非 OLYMPIAD 题）。
    # 本测试校验：每道奥赛题的「完美合成结果」已定义且字段结构对齐 expected_*，
    # 确保 rubric 读取 _expected_* 时不会因字段名错配而全 0。

    # 各题"完美"合成结果（严格对齐 Phase 1 核实的 scorer 读取字段）
    perfect_results = {
        "EX-OLY-001": {  # architecture_design: files/dependencies/expected_contains
            "files": [
                "user_service.py",
                "product_service.py",
                "order_service.py",
                "payment_service.py",
                "inventory_service.py",
                "shipping_service.py",
                "notification_service.py",
                "analytics_service.py",
                "tenant_isolator.py",
                "scale_shard.py",
                "consistency_saga.py",
                "idempotent_guard.py",
                "observability_trace.py",
                "gray_release.py",
                "api_gateway.py",
            ],
            "dependencies": [
                {"from": "api_gateway", "to": "order_service"},
                {"from": "order_service", "to": "inventory_service"},
                {"from": "order_service", "to": "payment_service"},
                {"from": "tenant_isolator", "to": "user_service"},
            ],
        },
        "EX-OLY-002": {  # hallucination_detect: hallucinations vs expected_hallucinations
            "hallucinations": [
                {"item": h, "reason": "fabricated"}
                for h in [
                    "fastjsonx 3.0",
                    "redis-py-cluster-plus",
                    "PyTTLCache",
                    "Ollama.function_call",
                    "SQLAlchemy.atomic_batch",
                    "kombu_rpc",
                    "psycopg3-async-pool",
                    "uvicorn.experimental_workers",
                    "Pydantic.serial_validator",
                    "httpx.retry_policy",
                    "aiohttp.thread_executor",
                    "FastAPI.dependency_scope",
                ]
            ],
        },
        "EX-OLY-003": {  # dependency_trace: call_chain vs expected_call_chain
            "call_chain": [
                {"function": f}
                for f in [
                    "handle_request",
                    "route_api",
                    "validate_input",
                    "process_order",
                    "query_inventory",
                    "map_record",
                    "fetch_cache",
                    "check_policy",
                ]
            ],
        },
        "EX-OLY-004": {  # code_generate: content + expected_test_cases（执行验证）
            "content": (
                "import threading\nimport time\nfrom functools import wraps\n\n"
                "def cached_decorator(ttl=60, maxsize=128):\n"
                "    def decorator(func):\n"
                "        cache = {}\n"
                "        order = []\n"
                "        lock = threading.Lock()\n"
                "        @wraps(func)\n"
                "        def wrapper(*args, **kwargs):\n"
                "            key = (args, tuple(sorted(kwargs.items())))\n"
                "            now = time.time()\n"
                "            with lock:\n"
                "                if key in cache:\n"
                "                    val, exp = cache[key]\n"
                "                    if now < exp:\n"
                "                        order.remove(key); order.append(key)\n"
                "                        return val\n"
                "                    else:\n"
                "                        del cache[key]; order.remove(key)\n"
                "                result = func(*args, **kwargs)\n"
                "                cache[key] = (result, now + ttl)\n"
                "                order.append(key)\n"
                "                if len(cache) > maxsize:\n"
                "                    old = order.pop(0)\n"
                "                    del cache[old]\n"
                "            return result\n"
                "        return wrapper\n"
                "    return decorator\n"
            ),
        },
        "EX-OLY-005": {  # parallel_planning: parallel_groups vs expected_parallel_groups
            "parallel_groups": [
                ["T1", "T2", "T3"],
                ["T4", "T5", "T6"],
                ["T7", "T8", "T9"],
                ["T10", "T11"],
                ["T12", "T13"],
                ["T14", "T15"],
            ],
        },
        "EX-OLY-006": {  # context_consistency: consistent/conflicts vs expected_contains
            "consistent": False,
            "conflicts": [
                "order_id 类型矛盾: API=string vs DB=integer",
                "缓存 redis ttl 矛盾: 900 vs 3600",
                "rate_limit 配额矛盾: 100 vs 500",
                "error_code 冲突: 4001 vs 40001",
                "log_level 矛盾: DEBUG vs INFO",
            ],
        },
        # ── Phase 3: 真实多文件注入题（rubric/judge 评分，不走 _compute_metrics）──
        "EX-OLY-007": {  # architecture_design: files/dependencies + broken/hallucinated
            "files": [
                "task_gate.py",
                "git_commit.py",
                "verify_schema_health.py",
                "diagnose_depgraph.py",
                "audit_registration.py",
                "ghost_router.py",
            ],
            "dependencies": [
                {"from": "git_commit", "to": "git_commit_gateway"},
                {"from": "task_gate", "to": "ghost_router"},
                {"from": "ghost_router", "to": "phantom_lock"},
            ],
            "broken_dependencies": [
                {"from": "task_gate", "to": "ghost_router", "reason": "ghost_router does not exist"},
            ],
            "hallucinated_items": [
                {"item": "route_ghost_request", "reason": "fabricated function"},
                {"item": "acquire_phantom_session", "reason": "fabricated import"},
            ],
        },
        "EX-OLY-008": {  # hallucination_detect: 3 处伪造 import
            "hallucinations": [
                {"item": "quantum_validator", "reason": "fabricated module"},
                {"item": "validate_quantum_coherence", "reason": "fabricated function"},
                {"item": "neural_lint", "reason": "fabricated module"},
                {"item": "neural_check", "reason": "fabricated function"},
                {"item": "phantom_router", "reason": "fabricated module"},
                {"item": "route_phantom", "reason": "fabricated function"},
            ],
        },
        "EX-OLY-009": {  # dependency_trace: call_chain + phantom_imports
            "call_chain": [
                {"function": f}
                for f in [
                    "main",
                    "GitCommitGateway",
                    "commit",
                    "_stash_other_files",
                    "_run_git",
                ]
            ],
            "phantom_imports": [
                "commit_orchestrator",
                "orchestrate_pipeline",
            ],
        },
    }

    # OLYMPIAD 题全部走 rubric/judge/executor 三轨评分（_score_olympiad_case），
    # 不走 _compute_metrics。本测试用 ExamRubric 直接验证字段对齐：
    # 注入 _expected_* 后 rubric 能正确读取并返回非零分（全 0 = 字段名错配）。
    rubric = ExamRubric()
    problems = []
    scores: list[tuple[str, str, float]] = []  # (case_id, capability, rubric_score)
    for case in oly_cases:
        result = perfect_results.get(case.case_id)
        assert result is not None, f"缺少 {case.case_id} 的合成结果"
        # 注入 _expected_* 供 rubric checker 读取（对齐 orchestrator _score_olympiad_case L312-321）
        rubric_input = dict(result)
        if case.expected_contains:
            rubric_input["_expected_contains"] = list(case.expected_contains)
        if case.expected_hallucinations:
            rubric_input["_expected_hallucinations"] = list(case.expected_hallucinations)
        if case.expected_call_chain:
            rubric_input["_expected_call_chain"] = list(case.expected_call_chain)
        if case.expected_parallel_groups:
            rubric_input["_expected_parallel_groups"] = [list(g) for g in case.expected_parallel_groups]
        try:
            rr = rubric.score(case.capability, rubric_input)
        except Exception as e:
            problems.append(f"{case.case_id} ({case.capability}): rubric 抛异常 {e}")
            continue
        scores.append((case.case_id, case.capability, rr.score))
        # 非零分 = 字段名对齐正确（全 0 才是字段错配；某些维度因内容不匹配得 0 属正常）
        if rr.score <= 0.0:
            problems.append(
                f"{case.case_id} ({case.capability}): 完美结果 rubric score=0.000，疑似字段名错配；维度明细: {rr.items}"
            )

    if problems:
        for prob in problems:
            print(f"  [FAIL] {prob}")
        raise AssertionError(f"字段一致性测试失败: {len(problems)} 项")

    for cid, cap, sc in scores:
        print(f"  {cid} ({cap}): rubric={sc:.3f}")
    print("[PASS] 9 道奥赛题字段一致性（rubric 非零分=字段对齐正确）")


# ═══════════════════════════════════════════════════════════════
# 5. 奥赛单题通过线常量
# ═══════════════════════════════════════════════════════════════
def test_pass_threshold():
    assert _OLYMPIAD_CASE_PASS_THRESHOLD == 0.6, "奥赛单题通过线应为 0.6"
    print("[PASS] _OLYMPIAD_CASE_PASS_THRESHOLD = 0.6")


# ═══════════════════════════════════════════════════════════════
# main
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    tests = [
        test_time_weight_boundaries,
        test_olympiad_pass_rate,
        test_overall_cap,
        test_olympiad_field_consistency,
        test_pass_threshold,
    ]
    failed = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            print(f"[FAIL] {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {t.__name__}: {type(e).__name__}: {e}")
            failed += 1
    print()
    if failed:
        print(f"结果: {failed}/{len(tests)} 失败")
        sys.exit(1)
    print(f"结果: {len(tests)}/{len(tests)} 全部通过")
    sys.exit(0)
