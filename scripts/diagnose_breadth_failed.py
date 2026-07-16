# [MODULE] scripts.diagnose_breadth_failed
# [DOMAIN] D_GOVERNANCE
# [STARTUP] manual
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
"""
诊断 breadth_failed 能力的根因。

对指定能力列表, 各跑 breadth 第1题:
  1. inference() 返回的 result dict keys
  2. _check_structure 判定
  3. 缺失字段分析
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from zephyr.intelligence.model_profiling.deepseek_v4_chat import DeepSeekV4Chat
from zephyr.intelligence.model_profiling.exam_orchestrator import ExamOrchestrator
from zephyr.intelligence.model_profiling.exam_test_cases import (
    CASES_BY_CAPABILITY,
)
from zephyr.shared.security.secrets import get_required_secret, get_secret_or_default

# 通过 SSoT secret loader 读取（.env 由 zephyr/__init__.py 自动加载）；main() 校验非空
DEEPSEEK_API_KEY = get_secret_or_default("DEEPSEEK_API_KEY")


def diagnose_capability(cap_name: str) -> bool:
    """诊断单个能力, 返回 breadth 是否通过."""
    case = CASES_BY_CAPABILITY[cap_name][0]
    print("\n" + "=" * 70)
    print(f"能力: {cap_name} | 题目: {case.case_id}")
    print(f"expected_structure_keys: {case.expected_structure_keys}")
    print("=" * 70)

    chat = DeepSeekV4Chat(
        model="deepseek-v4-pro",
        api_key=DEEPSEEK_API_KEY,
        thinking=True,
        max_tokens=4096,
    )
    result = chat.inference(cap_name, case.prompt)

    print(f"\nresult keys: {list(result.keys())}")
    for k in case.expected_structure_keys:
        v = result.get(k)
        status = "✓存在" if v is not None else "✗缺失"
        empty = " (空)" if (isinstance(v, (list, str)) and len(v) == 0) else ""
        print(f"  {k}: {status}{empty} → {v!r:.100}")

    passed = ExamOrchestrator._check_structure(result, case.expected_structure_keys)
    print(f"\nbreadth 通过? {'✓ 是' if passed else '✗ 否'}")

    if not passed:
        for k in case.expected_structure_keys:
            v = result.get(k)
            if v is None:
                print(f"  → {k} 缺失: 检查 system prompt 是否要求输出此字段")
            elif isinstance(v, (list, str)) and len(v) == 0:
                print(f"  → {k} 为空: 检查 prompt 语义是否与模型理解一致")
    return passed


def main() -> int:
    try:
        get_required_secret("DEEPSEEK_API_KEY")
    except Exception as e:
        print(f"[FATAL] {e}", file=sys.stderr)
        return 2

    caps = sys.argv[1:] if len(sys.argv) > 1 else [
        "parallel_planning",
        "dependency_trace",
        "context_management",
    ]
    print(f"诊断 {len(caps)} 个能力: {caps}")

    results = {}
    for cap in caps:
        try:
            results[cap] = diagnose_capability(cap)
        except Exception as e:
            print(f"\n[ERROR] {cap}: {e}")
            results[cap] = False

    print("\n" + "=" * 70)
    print("汇总:")
    for cap, passed in results.items():
        print(f"  {cap:<25} {'✓ breadth 通过' if passed else '✗ breadth 失败'}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
