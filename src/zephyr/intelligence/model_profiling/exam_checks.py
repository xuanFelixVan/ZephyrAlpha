# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] zephyr.intelligence.model_profiling.exam_checks
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.intelligence.model_profiling.exam_test_cases
# [CONSUMERS] zephyr.intelligence.model_profiling.exam_orchestrator; tests/model/test_exam_orchestrator.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 纯函数模块——所有函数无副作用，不依赖实例/类/模块级可变状态
# [MODIFY-GUARD] docs/03_modules/_cross_layer/model_profiler/blueprint.md
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无异常抛出——所有函数对非法输入返回 False/0.0/空值
# [TESTS] tests/model/test_exam_orchestrator.py
# [A_module] module_id=MOD-INF-034 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""exam_checks.py — 考试检测纯函数模块（Stage 4 试点：从 exam_orchestrator 提取）

治本（Stage 4 私有成员断言消除，2026-07-27）：
ExamOrchestrator 的 10 个 _check_* 静态方法 + 2 个模块级工具函数
（_normalized_edit_distance / _percentile）均为无副作用纯函数，却被标为私有，
导致测试必须通过 ExamOrchestrator._check_xxx(...) 访问——125 处私有成员访问
中 74 处由此产生。提取到本公共模块后，测试直接调用公共函数，消除私有访问。

设计原则
--------
1. **纯函数**：所有函数仅依赖参数，不读/写实例/类/模块级可变状态
2. **公共 API**：函数名无下划线前缀，供测试和 exam_orchestrator 共同调用
3. **向后兼容**：exam_orchestrator 中的 _check_* 私有方法保留为 thin wrapper，
   委托到本模块的公共函数，避免破坏内部调用链
4. **类型安全**：所有函数对非法输入（None/非 dict/空值）返回安全默认值
"""

from __future__ import annotations

import json
import re

from zephyr.intelligence.model_profiling.exam_test_cases import ExamTestCase

__all__ = [
    "check_static_assertions",
    "check_structure",
    "check_fabrication",
    "outputs_similar",
    "check_refusal",
    "check_overclaim",
    "check_source_confusion",
    "check_instruction_drift",
    "check_format_hallucination",
    "check_quantity_hallucination",
    "normalized_edit_distance",
    "percentile",
    "compute_olympiad_pass_rate",
    "compute_overall_score",
    "validate_result",
]


# ============================================================================
# 静态文本检测函数（原 ExamOrchestrator._check_* staticmethod）
# ============================================================================


def check_static_assertions(candidate: str, assertions: list[str]) -> float:
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


def check_structure(result: dict, expected_keys: list[str]) -> bool:
    """检查结果 dict 是否包含所有期望键且值非空。"""
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


def check_fabrication(case: ExamTestCase, result: dict) -> bool:
    """P2: 检查编造 — old_str 不在原始 prompt 中（编造了不存在的代码段）。"""
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


def outputs_similar(a: dict, b: dict) -> bool:
    """判断两个输出是否相似（过滤 _ 前缀内部字段后比较）。"""
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


def check_refusal(result: dict) -> bool:
    """P2: 检查拒绝 — 结果为空或 error 含拒绝关键词。"""
    if not result:
        return True
    error = str(result.get("error", "")).lower()
    refusal_keywords = ["cannot", "unable", "refuse", "i'm sorry", "i can't", "not able"]
    return any(kw in error for kw in refusal_keywords)


def check_overclaim(case: ExamTestCase, result: dict) -> bool:
    """P2: 检查过度声称 — 声称做了但实际未做。

    启发式: 输出含"已完成/已修复/已创建"等动词, 但对应字段为空。
    """
    if not isinstance(result, dict):
        return False
    claim_keywords = [
        "已完成",
        "已修复",
        "已创建",
        "已删除",
        "已重构",
        "已实现",
        "completed",
        "fixed",
        "created",
        "removed",
        "refactored",
        "implemented",
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


def check_source_confusion(case: ExamTestCase, result: dict) -> bool:
    """P2: 检查来源混淆 — 引用了 prompt/input_files 中不存在的文件名。

    启发式: result 中引用的 xxx.py 不在 case.prompt 或 input_files 中。
    """
    if not isinstance(result, dict):
        return False
    result_text = json.dumps(result, ensure_ascii=False)
    referenced = set(re.findall(r"[\w/\\]+\.py", result_text))
    if not referenced:
        return False
    prompt_files = set(re.findall(r"[\w/\\]+\.py", case.prompt))
    input_files = set(case.input_files.keys())
    legit = prompt_files | input_files
    # 通用文件名豁免 (常见但不视为混淆)
    generic = {"__init__.py", "setup.py", "conftest.py", "main.py", "test.py"}
    confused = referenced - legit - generic
    return len(confused) > 0


def check_instruction_drift(case: ExamTestCase, result: dict) -> bool:
    """P2: 检查指令偏离 — 输出结构不符合 expected_structure_keys。

    启发式: 复用 check_structure 判断输出是否包含指令要求的字段。
    若 case 无 expected_structure_keys 则跳过 (无法判定)。
    """
    if not isinstance(result, dict) or not case.expected_structure_keys:
        return False
    return not check_structure(result, case.expected_structure_keys)


def check_format_hallucination(case: ExamTestCase, result: dict) -> bool:
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


def check_quantity_hallucination(case: ExamTestCase, result: dict) -> bool:
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


# ============================================================================
# 数学工具函数（原 exam_orchestrator 模块级 _normalized_edit_distance / _percentile）
# ============================================================================


def normalized_edit_distance(a: str, b: str) -> float:
    """计算两个字符串的归一化编辑距离 (Levenshtein / max(len) )。

    Returns:
        0.0 (完全相同) ~ 1.0 (完全不同)
    """
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


def percentile(sorted_data: list[float], p: float) -> float:
    """计算已排序数据的百分位数（线性插值法，与 NumPy 默认一致）。

    Args:
        sorted_data: 已排序的数据列表（调用方负责排序）
        p: 百分位 (0~100)
    Returns:
        百分位值；空列表返回 0.0
    """
    if not sorted_data:
        return 0.0
    k = (len(sorted_data) - 1) * p / 100.0
    f = int(k)
    c = min(f + 1, len(sorted_data) - 1)
    return sorted_data[f] + (sorted_data[c] - sorted_data[f]) * (k - f)


# ============================================================================
# 奥赛题通过率（原 ExamOrchestrator._compute_olympiad_pass_rate 实例方法）
# ============================================================================


def compute_olympiad_pass_rate(case_results: list[bool]) -> float:
    """v3.0.5: 奥赛题通过率——用于奥赛封顶机制（纯函数版，Stage 4 公共化提取）。

    无奥赛题时返回 1.0（不封顶），保持向后兼容。

    Args:
        case_results: 各奥赛题的通过记录列表（True=通过, False=未通过）
    Returns:
        通过率 0.0~1.0；空列表返回 1.0
    """
    if not case_results:
        return 1.0
    return sum(case_results) / len(case_results)


def compute_overall_score(passport: object, case_results: list[bool]) -> float:
    """v3.0.5: 综合分 = 加权原始分，经奥赛封顶（纯函数版，Stage 4 公共化提取）。

    权重：breadth 0.35 + depth 0.50 + (1-halluc) 0.15
    奥赛封顶：通过率 <25%->B+(0.80)；<50%->A(0.85)；<75%->A-(0.88)；≥75%->A+(1.0)

    Args:
        passport: CapabilityPassport 对象（需有 breadth.score/depth.overall_score/
                  hallucination.overall_rate 三个属性）
        case_results: 奥赛题通过记录列表（用于封顶判定）
    Returns:
        综合分 0.0~1.0（已 round 到 3 位小数）
    """
    b = passport.breadth.score
    d = passport.depth.overall_score
    h = 1.0 - passport.hallucination.overall_rate
    raw = 0.35 * b + 0.50 * d + 0.15 * h

    pass_rate = compute_olympiad_pass_rate(case_results)
    if pass_rate < 0.25:
        cap = 0.80  # B+
    elif pass_rate < 0.50:
        cap = 0.85  # A
    elif pass_rate < 0.75:
        cap = 0.88  # A-
    else:
        cap = 1.0  # A+ 解锁

    return round(min(raw, cap), 3)


# ============================================================================
# 结果验证（原 ExamOrchestrator._validate_result staticmethod）
# ============================================================================


def validate_result(result: dict, case: ExamTestCase) -> bool:
    """验证模型返回结果是否有效（防作弊检测，纯函数版，Stage 4 公共化提取）。

    检测项:
    1. 泄露答案字段: result 中包含 expected_* 字段 -> 无效
    2. 数值越界: precision/recall 超出 [0,1] 范围 -> 无效

    Args:
        result: 模型返回的 dict
        case: 对应的 ExamTestCase（保留参数以兼容原签名，当前未使用）
    Returns:
        True=有效, False=无效
    """
    if not isinstance(result, dict):
        return False

    # 检测泄露答案字段
    suspicious_keys = {
        "expected_category",
        "expected_tags",
        "expected_old_str",
        "expected_contains",
        "expected_needs_human",
        "expected_structure_keys",
    }
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
