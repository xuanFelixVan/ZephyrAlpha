# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/track_script_costs.py | §
# [MODULE] scripts.governance.meta.track_script_costs
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.meta.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
track_script_costs.py — 脚本执行 AI 费用追踪



对标 B54（Script 执行费用追踪）。

追踪 D12 等调用 LLM API 的治理脚本的执行费用：
- 每个模型的 API 调用次数
- 每次调用的 token 使用量（prompt + completion）
- 按模型定价计算费用合计
- 按月/季度导出费用报告

1人+AI 维护的核心问题："这次扫描花了多少钱？"

Usage:
    python scripts/governance/meta/track_script_costs.py --record --script d12_ai/validate_hallucination.py --model deepseek-v3 --tokens 15000 --cost 0.003
    python scripts/governance/meta/track_script_costs.py --report
    python scripts/governance/meta/track_script_costs.py --monthly
    python scripts/governance/meta/track_script_costs.py --json
"""

from __future__ import annotations

__manifest__ = """
args: []
description: ⚠ __manifest__ 缺失——请添加元数据块
dimensions: []
priority: P2
timeout_seconds: 60
warn_only: false
"""


import json as json_mod
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

# 治本(2026-06-30): REPO_ROOT 真源来自 _shared.constants, 消除 parents[N] 硬编码
# 原 parents[2] 实为 scripts 目录而非 repo root, 变量名误导且路径计算有 bug
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT as _REPO_ROOT  # noqa: E402
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT
_COST_DB = _REPO_ROOT / "scripts" / "governance" / "meta" / "script_cost_db.jsonl"
_COST_STATE = _REPO_ROOT / "scripts" / "governance" / "meta" / "cost_tracking_state.json"

# 模型定价（$/1K tokens）—— 2025 Q4 参考值
MODEL_PRICING: dict[str, dict[str, float]] = {
    "deepseek-v3": {"prompt": 0.001, "completion": 0.002},
    "deepseek-v4": {"prompt": 0.0015, "completion": 0.003},
    "claude-sonnet-4": {"prompt": 0.003, "completion": 0.015},
    "claude-opus-4": {"prompt": 0.015, "completion": 0.075},
    "glm-4-plus": {"prompt": 0.002, "completion": 0.004},
    "gpt-4o": {"prompt": 0.0025, "completion": 0.01},
    "cursor-small": {"prompt": 0.0, "completion": 0.0},
}

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def _load_state() -> dict:
    """_load_state implementation."""
    if not _COST_STATE.exists():
        return {"total_cost": 0.0, "total_tokens": 0, "total_calls": 0, "monthly": {}}
    with open(_COST_STATE, encoding="utf-8") as f:
        return json_mod.load(f)


def _save_state(data: dict) -> None:
    """_save_state implementation."""
    _COST_STATE.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = f"{_COST_STATE}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, encoding="utf-8") as f:
            json_mod.dump(data, f, ensure_ascii=False, indent=2)

        os.replace(tmp_path, _COST_STATE)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


def record_cost(script: str, model: str, tokens: int, cost: float, detail: str = "") -> dict:
    """record_cost implementation."""
    now = datetime.now(UTC)
    entry = {
        "timestamp": now.isoformat(),
        "script": script,
        "model": model,
        "tokens": tokens,
        "cost_usd": cost,
        "detail": detail,
    }
    _COST_DB.parent.mkdir(parents=True, exist_ok=True)
    with open(_COST_DB, "a", encoding="utf-8") as f:
        f.write(json_mod.dumps(entry, ensure_ascii=False) + "\n")

    state = _load_state()
    state["total_cost"] = round(state["total_cost"] + cost, 6)
    state["total_tokens"] += tokens
    state["total_calls"] += 1
    month_key = now.strftime("%Y-%m")
    state.setdefault("monthly", {}).setdefault(month_key, {"cost": 0.0, "tokens": 0, "calls": 0})
    state["monthly"][month_key]["cost"] = round(state["monthly"][month_key]["cost"] + cost, 6)
    state["monthly"][month_key]["tokens"] += tokens
    state["monthly"][month_key]["calls"] += 1
    _save_state(state)
    return entry


def report() -> dict:
    """report implementation."""
    state = _load_state()
    now = datetime.now(UTC)
    month_key = now.strftime("%Y-%m")
    monthly = state.get("monthly", {}).get(month_key, {"cost": 0.0, "tokens": 0, "calls": 0})
    return {
        "total_cost_usd": state["total_cost"],
        "total_tokens": state["total_tokens"],
        "total_api_calls": state["total_calls"],
        "current_month": {
            "cost_usd": monthly["cost"],
            "tokens": monthly["tokens"],
            "calls": monthly["calls"],
        },
    }


def monthly_breakdown() -> dict:
    """monthly_breakdown implementation."""
    state = _load_state()
    return dict(sorted(state.get("monthly", {}).items()))


def estimate_cost(prompt_tokens: int, completion_tokens: int, model: str) -> float:
    """estimate_cost implementation."""
    pricing = MODEL_PRICING.get(model, {"prompt": 0.002, "completion": 0.005})
    return round(prompt_tokens * pricing["prompt"] / 1000 + completion_tokens * pricing["completion"] / 1000, 6)


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    if "--record" in sys.argv:
        script = model = ""
        tokens = cost = 0
        detail = ""
        for i, a in enumerate(sys.argv):
            if a == "--script" and i + 1 < len(sys.argv):
                script = sys.argv[i + 1]
            elif a == "--model" and i + 1 < len(sys.argv):
                model = sys.argv[i + 1]
            elif a == "--tokens" and i + 1 < len(sys.argv):
                tokens = int(sys.argv[i + 1])
            elif a == "--cost" and i + 1 < len(sys.argv):
                cost = float(sys.argv[i + 1])
            elif a == "--detail" and i + 1 < len(sys.argv):
                detail = sys.argv[i + 1]
        if script and model:
            result = record_cost(script, model, tokens, cost, detail)
            print(
                f"[COST] ${result['cost_usd']:.4f} | {result['script']} @ {result['model']} ({result['tokens']} tokens)",
                file=sys.stderr,
            )
    elif "--report" in sys.argv:
        r = report()
        if "--json" in sys.argv:
            print(json_mod.dumps(r, ensure_ascii=False, indent=2))
        else:
            print("\n[COST] AI 执行费用追踪", file=sys.stderr)
            print(f"  累计花费: ${r['total_cost_usd']:.4f}", file=sys.stderr)
            print(f"  累计 tokens: {r['total_tokens']:,}", file=sys.stderr)
            print(f"  累计 API调用: {r['total_api_calls']}", file=sys.stderr)
            print(f"  本月花费: ${r['current_month']['cost_usd']:.4f}", file=sys.stderr)
    elif "--monthly" in sys.argv:
        mb = monthly_breakdown()
        for month, data in mb.items():
            print(f"  {month}: ${data['cost']:.4f} ({data['tokens']:,} tokens, {data['calls']} calls)")
    elif "--estimate" in sys.argv:
        print("模型定价:", file=sys.stderr)
        for model, pricing in MODEL_PRICING.items():
            est = estimate_cost(10000, 5000, model)
            print(
                f"  {model:20s}: ${pricing['prompt']:.4f}/1K prompt, ${pricing['completion']:.4f}/1K completion → ~${est:.4f}/15K tokens"
            )
    else:
        print("Usage: track_script_costs.py --record ... | --report | --monthly | --estimate", file=sys.stderr)


if __name__ == "__main__":
    main()
