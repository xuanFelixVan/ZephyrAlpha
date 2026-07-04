# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] zephyr.intelligence.model_profiling.exam_rubric
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES]
# [CONSUMERS] zephyr.intelligence.model_profiling.exam_orchestrator
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RUB_exam_rubric | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""ExamRubric --- 奥赛题结构化多维清单评分（v3.0.5）。

对 OLYMPIAD/EXTREME 难度题做多维精确评分，超越单维关键词/结构匹配。
自包含纯 Python，不需要外部模型。

每个 capability 注册 4-6 个评分维度(RubricItem)，每维有：
  - criterion: 维度名（如"文件拆分完整性"）
  - weight: 权重（加权求和归一化）
  - checker: 检查函数 (dict) -> float 0.0~1.0

用法:
    rubric = ExamRubric()
    result = rubric.score("architecture_design", model_output_dict)
    print(result.score, result.items)
"""
from __future__ import annotations

import ast
import json
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RubricItem:
    """单维度评分项。"""
    criterion: str
    weight: float
    checker: Callable[[dict], float]


@dataclass
class RubricResult:
    """多维清单评分结果。"""
    score: float  # 加权总分 0.0~1.0
    items: list[tuple[str, float, float]] = field(default_factory=list)  # (维度, 得分, 权重)


# ── 通用 checker 辅助 ────────────────────────────────────────
def _safe_get(result: dict, *keys, default=None):
    """安全嵌套取值。"""
    cur = result
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k, default)
    return cur


def _keyword_coverage(text: str, keywords: list[str]) -> float:
    """关键词覆盖率（小写匹配）。"""
    if not keywords:
        return 0.0
    text_lower = text.lower()
    hits = sum(1 for kw in keywords if kw.lower() in text_lower)
    return hits / len(keywords)


# ═══════════════════════════════════════════════════════════════
# architecture_design 评分维度
# ═══════════════════════════════════════════════════════════════
_OLY_001_DOMAINS = ["user", "product", "order", "payment", "inventory", "shipping", "notification", "analytics"]
_OLY_001_NFRS = ["tenant", "scale", "consistency", "idempotent", "observability", "trace", "gray"]


def _ad_file_count(result: dict) -> float:
    """文件数完整性：目标 20+ 文件。"""
    files = result.get("files", [])
    return min(len(files) / 20.0, 1.0) if files else 0.0


def _ad_domain_coverage(result: dict) -> float:
    """8 业务领域覆盖度。"""
    text = json.dumps(result).lower()
    return sum(1 for d in _OLY_001_DOMAINS if d in text) / len(_OLY_001_DOMAINS)


def _ad_nfr_coverage(result: dict) -> float:
    """6 非功能需求覆盖度。"""
    text = json.dumps(result).lower()
    return _keyword_coverage(text, _OLY_001_NFRS)


def _ad_dependency_count(result: dict) -> float:
    """依赖关系数量：目标 5+。"""
    deps = result.get("dependencies", [])
    return min(len(deps) / 5.0, 1.0) if deps else 0.0


def _ad_naming_regularity(result: dict) -> float:
    """命名规范性：文件名是否含 service/模块标识。"""
    files = result.get("files", [])
    if not files:
        return 0.0
    regular = sum(1 for f in files if isinstance(f, str) and ("service" in f.lower() or "_" in f))
    return regular / len(files)


# ═══════════════════════════════════════════════════════════════
# hallucination_detect 评分维度
# ═══════════════════════════════════════════════════════════════
def _hd_recall(result: dict) -> float:
    """幻觉召回率（需 expected_hallucinations 注入到 result['_expected']）。"""
    expected = result.get("_expected_hallucinations", [])
    if not expected:
        return 0.0
    preds = _extract_hallucination_items(result)
    if not preds:
        return 0.0
    gold = set(h.lower() for h in expected)
    tp = len(preds & gold)
    return tp / len(gold) if gold else 0.0


def _hd_precision(result: dict) -> float:
    """幻觉精确率（报告中有多少是真幻觉）。"""
    expected = result.get("_expected_hallucinations", [])
    preds = _extract_hallucination_items(result)
    if not preds:
        return 0.0
    if not expected:
        return 0.5  # 无期望时给中性分
    gold = set(h.lower() for h in expected)
    tp = len(preds & gold)
    return tp / len(preds) if preds else 0.0


def _hd_reasoning_quality(result: dict) -> float:
    """理由质量：是否为每条幻觉提供 reason。"""
    hallucinations = result.get("hallucinations", [])
    if not hallucinations:
        return 0.0
    with_reason = sum(
        1 for h in hallucinations
        if isinstance(h, dict) and h.get("reason", "").strip()
    )
    return with_reason / len(hallucinations)


def _extract_hallucination_items(result: dict) -> set[str]:
    preds = set()
    for h in result.get("hallucinations", []):
        if isinstance(h, dict):
            preds.add(str(h.get("item", "")).lower())
        elif isinstance(h, str):
            preds.add(h.lower())
    preds.discard("")
    return preds


# ═══════════════════════════════════════════════════════════════
# dependency_trace 评分维度
# ═══════════════════════════════════════════════════════════════
def _dt_chain_depth(result: dict) -> float:
    """调用链深度：目标 8 层。"""
    chain = result.get("call_chain", [])
    return min(len(chain) / 8.0, 1.0) if chain else 0.0


def _dt_function_match(result: dict) -> float:
    """函数名匹配率（需 expected_call_chain 注入）。"""
    expected = result.get("_expected_call_chain", [])
    if not expected:
        return 0.0
    preds = _extract_call_chain_funcs(result)
    gold = set(f.lower() for f in expected)
    tp = len(preds & gold)
    return tp / len(gold) if gold else 0.0


def _dt_order_correctness(result: dict) -> float:
    """调用顺序正确性（需 expected_call_chain 注入）。"""
    expected = result.get("_expected_call_chain", [])
    if not expected:
        return 0.0
    preds = [str(f).lower() for f in _extract_call_chain_funcs(result, ordered=True)]
    gold = [f.lower() for f in expected]
    if len(preds) != len(gold):
        return 0.0
    correct = sum(1 for p, g in zip(preds, gold, strict=True) if p == g)
    return correct / len(gold)


def _extract_call_chain_funcs(result: dict, ordered: bool = False) -> list[str] | set[str]:
    chain = result.get("call_chain", [])
    funcs = []
    for step in chain:
        if isinstance(step, dict):
            funcs.append(str(step.get("function", "")))
        elif isinstance(step, str):
            funcs.append(step)
    return funcs if ordered else set(funcs)


# ═══════════════════════════════════════════════════════════════
# code_generate 评分维度（结构层；算法正确性由 executor 验证）
# ═══════════════════════════════════════════════════════════════
def _cg_syntax_valid(result: dict) -> float:
    """语法正确性：AST 解析通过。"""
    content = result.get("content", "")
    if not content:
        return 0.0
    try:
        ast.parse(content)
        return 1.0
    except (SyntaxError, ValueError):
        return 0.0


def _cg_decorator_present(result: dict) -> float:
    """目标函数定义存在。"""
    content = result.get("content", "")
    return 1.0 if "def cached_decorator" in content else 0.0


def _cg_concurrency_safety(result: dict) -> float:
    """并发安全标识：是否使用 Lock。"""
    content = result.get("content", "")
    score = 0.0
    if "Lock" in content or "lock" in content:
        score += 0.5
    if "threading" in content:
        score += 0.5
    return min(score, 1.0)


def _cg_ttl_logic(result: dict) -> float:
    """TTL 逻辑存在性。"""
    content = result.get("content", "").lower()
    score = 0.0
    if "ttl" in content or "expire" in content or "time.time" in content:
        score += 0.5
    if "lru" in content or "maxsize" in content or "evict" in content or "order" in content:
        score += 0.5
    return min(score, 1.0)


# ═══════════════════════════════════════════════════════════════
# parallel_planning 评分维度
# ═══════════════════════════════════════════════════════════════
def _pp_group_count(result: dict) -> float:
    """并行组数量：目标 6 组。"""
    groups = result.get("parallel_groups", [])
    return min(len(groups) / 6.0, 1.0) if groups else 0.0


def _pp_task_coverage(result: dict) -> float:
    """15 任务覆盖度。"""
    groups = result.get("parallel_groups", [])
    all_tasks = set()
    for g in groups:
        if isinstance(g, list):
            for t in g:
                if isinstance(t, str):
                    all_tasks.add(t.lower())
        elif isinstance(g, str):
            all_tasks.add(g.lower())
    return min(len(all_tasks) / 15.0, 1.0)


def _pp_dep_respect(result: dict) -> float:
    """依赖遵守度（需 expected_parallel_groups 注入，用其作为拓扑参考）。"""
    expected = result.get("_expected_parallel_groups", [])
    if not expected:
        return 0.5  # 无期望时给中性分
    # 检查模型输出的任务分层与期望分层的相似度
    pred_layers = _flatten_groups_to_layers(result.get("parallel_groups", []))
    gold_layers = [set(t.lower() for t in layer) for layer in expected]
    if len(pred_layers) != len(gold_layers):
        return 0.0
    matches = sum(
        1 for p, g in zip(pred_layers, gold_layers, strict=True)
        if p == g
    )
    return matches / len(gold_layers)


def _flatten_groups_to_layers(groups: list[Any]) -> list[set[str]]:
    layers = []
    for g in groups:
        layer = set()
        if isinstance(g, list):
            for t in g:
                if isinstance(t, str):
                    layer.add(t.lower())
        elif isinstance(g, str):
            layer.add(g.lower())
        layers.append(layer)
    return layers


# ═══════════════════════════════════════════════════════════════
# context_consistency 评分维度
# ═══════════════════════════════════════════════════════════════
def _cc_contradiction_detected(result: dict) -> float:
    """矛盾识别正确性：期望不一致时 consistent=false。"""
    consistent = result.get("consistent")
    if consistent is False:
        return 1.0
    return 0.0


def _cc_conflict_count(result: dict) -> float:
    """冲突点数量：目标 ≥5。"""
    conflicts = result.get("conflicts", [])
    return min(len(conflicts) / 5.0, 1.0) if conflicts else 0.0


def _cc_conflict_keyword_coverage(result: dict) -> float:
    """冲突内容关键词覆盖（需 expected_contains 注入）。"""
    expected = result.get("_expected_contains", [])
    if not expected:
        return 0.5
    text = json.dumps(result).lower()
    return _keyword_coverage(text, expected)


# ═══════════════════════════════════════════════════════════════
# Rubric 注册表
# ═══════════════════════════════════════════════════════════════
_OLYMPIC_RUBRICS: dict[str, list[RubricItem]] = {
    "architecture_design": [
        RubricItem("文件数完整性", 0.25, _ad_file_count),
        RubricItem("领域覆盖度", 0.25, _ad_domain_coverage),
        RubricItem("非功能覆盖", 0.20, _ad_nfr_coverage),
        RubricItem("依赖关系数", 0.15, _ad_dependency_count),
        RubricItem("命名规范性", 0.15, _ad_naming_regularity),
    ],
    "hallucination_detect": [
        RubricItem("幻觉召回率", 0.40, _hd_recall),
        RubricItem("幻觉精确率", 0.30, _hd_precision),
        RubricItem("理由质量", 0.30, _hd_reasoning_quality),
    ],
    "dependency_trace": [
        RubricItem("调用链深度", 0.30, _dt_chain_depth),
        RubricItem("函数匹配率", 0.40, _dt_function_match),
        RubricItem("顺序正确性", 0.30, _dt_order_correctness),
    ],
    "code_generate": [
        RubricItem("语法正确性", 0.30, _cg_syntax_valid),
        RubricItem("目标函数定义", 0.20, _cg_decorator_present),
        RubricItem("并发安全标识", 0.25, _cg_concurrency_safety),
        RubricItem("TTL/LRU逻辑", 0.25, _cg_ttl_logic),
    ],
    "parallel_planning": [
        RubricItem("并行组数量", 0.25, _pp_group_count),
        RubricItem("任务覆盖度", 0.35, _pp_task_coverage),
        RubricItem("依赖遵守度", 0.40, _pp_dep_respect),
    ],
    "context_consistency": [
        RubricItem("矛盾识别", 0.35, _cc_contradiction_detected),
        RubricItem("冲突点数量", 0.30, _cc_conflict_count),
        RubricItem("冲突关键词覆盖", 0.35, _cc_conflict_keyword_coverage),
    ],
}


class ExamRubric:
    """结构化清单评分——对奥赛题做多维精确评分。

    用法:
        rubric = ExamRubric()
        # 注入期望值供 checker 使用
        result_with_expected = {**model_output, "_expected_hallucinations": [...]}
        res = rubric.score("hallucination_detect", result_with_expected)
    """

    RUBRICS: dict[str, list[RubricItem]] = _OLYMPIC_RUBRICS

    def score(self, capability: str, result: dict) -> RubricResult:
        """对结果做多维评分。

        result 可包含 "_expected_*" 键注入期望值（由调用方从 ExamTestCase 填充）。
        """
        items = self.RUBRICS.get(capability, [])
        if not items:
            return RubricResult(score=0.0, items=[])

        scored: list[tuple[str, float, float]] = []
        total_w = sum(it.weight for it in items)
        if total_w <= 0:
            return RubricResult(score=0.0, items=[])

        weighted_sum = 0.0
        for it in items:
            try:
                s = max(0.0, min(1.0, float(it.checker(result))))
            except Exception:
                s = 0.0
            weighted_sum += s * it.weight
            scored.append((it.criterion, round(s, 3), it.weight))

        return RubricResult(score=round(weighted_sum / total_w, 3), items=scored)
