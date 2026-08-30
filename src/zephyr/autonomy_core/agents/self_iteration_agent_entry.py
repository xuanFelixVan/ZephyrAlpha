# [BLUEPRINT] MOD-EXE-ITER-001 | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/14_execution_layer.md | §3.4/§4-S0.5/§4-S1.1
# [MODULE] zephyr.autonomy_core.agents.self_iteration_agent_entry
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] stdlib ; zephyr.autonomy_core.agents._run_store ; zephyr.autonomy_core.agents._s11_wiring（§4-S1.1 反思接线薄委派，懒加载）
# [CONSUMERS] tests/autonomy/test_execution_layer_agent_entries.py ; tests/autonomy/test_execution_layer_s11_wiring.py ; 人手动触发（CLI）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只读形态：仅消费落盘证据（读白名单=.runtime/logs/docs 内文件），不写 src/ 不写注册表；零代码自改路径（不 import 执行/编辑链模块，测试断言此不变量）；建议工单 100% human_gated 标记（Phase 2 前一律人审）；S1.1 reflection_review=12号文频率闸门先行（拒则 denied 留痕不反思），放行才走三角色/L1 反思
# [MODIFY-GUARD] Owner approval required; 变更须同步 14号文 §4 S0.5/S1.1 验收口径
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 证据路径越白名单/不可读→跳过并如实记 skipped_evidence，不抛；reflection_review 非法 layer/level→ValueError fail-closed（先于落盘）
# [TESTS] tests/autonomy/test_execution_layer_agent_entries.py ; tests/autonomy/test_execution_layer_s11_wiring.py
# [A_module] module_id=MOD-EXE-ITER-001 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
自我迭代 Agent 薄入口（14号文 §3.4 评估/优化/反馈，§4 S0.5 只读形态 + S1.1 反思接线）.

kind=iteration_review（默认）：只读解析白名单证据（json/jsonl）→汇总 gate 判定与实验
通过情况→human_gated 优化建议工单（只复述缺口）。kind=reflection_review（S1.1）：
12号文频率闸门→三角色/L1 反思→ReflectionStore（薄委派 _s11_wiring）。
不做权重自更新/自进化搜索/自动改码；STOP 模式与 Meta-Harness 归 Phase 1+。
手动触发：python -m zephyr.autonomy_core.agents.self_iteration_agent_entry --ticket <path>

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: ticket 参数
#   fields: 参数 ticket，类型注解 dict[str, Any]
#   code: self_iteration_agent_entry.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: runtime_dir 参数
#   fields: 参数 runtime_dir（无注解）
#   code: self_iteration_agent_entry.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: repo_root 参数
#   fields: 参数 repo_root（无注解）
#   code: self_iteration_agent_entry.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: argv 参数
#   fields: 参数 argv，类型注解 list[str] | None
#   code: self_iteration_agent_entry.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① run_iteration_review
#   name_en: run_iteration_review
#   intro: 执行一张迭代评估工单（只读证据→human_gated 建议工单，端到端落盘）.
#   desc: 执行一张迭代评估工单（只读证据→human_gated 建议工单，端到端落盘）. ticket={"ticket_id", "evidence_paths": [仓内相对/绝对路…；源码 L208-L252
#   inputs: ticket runtime_dir repo_root
#   outputs: dict[str, Any]
# - id: A2
#   name_zh: ② run_reflection_review
#   name_en: run_reflection_review
#   intro: S1.1 reflection_review 工单（12号文闸门+三角色反思；
#   desc: S1.1 reflection_review 工单（12号文闸门+三角色反思；实现薄委派 _s11_wiring）.；源码 L255-L259
#   inputs: ticket
#   outputs: dict[str, Any]
# - id: A3
#   name_zh: ③ main
#   name_en: main
#   intro: CLI 手动触发入口：--ticket <工单 JSON 路径> [--runtime-dir DIR].
#   desc: CLI 手动触发入口：--ticket <工单 JSON 路径> [--runtime-dir DIR].；源码 L262-L277
#   inputs: argv
#   outputs: int
# 层: 输出
# - id: O1
#   name_zh: dict[str, Any]
#   name_en: dict[str, Any]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: tests/autonomy/test_execution_layer_agent_entries.py ; tests/autonomy/test_exec…
# - id: O2
#   name_zh: int
#   name_en: int
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: tests/autonomy/test_execution_layer_agent_entries.py ; tests/autonomy/test_exec…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Final

from zephyr.autonomy_core.agents._run_store import AgentRunStore

ROLE: Final[str] = "self_iteration"
_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[4]

AGENT_CARD: Final[dict[str, Any]] = {
    "role": ROLE,
    "capabilities": [
        {
            "id": "iteration_review",
            "name": "落盘证据评估→优化建议工单（只读）",
            "inputs": "证据指针（gate verdict/实验指标/审计记录落盘文件）",
            "outputs": "优化建议工单（human_gated，落盘）",
            "autonomyLevel": "L0_manual",
        },
    ],
    "autonomyBoundaries": {
        "ai_modifiable": [],
        "human_gated": ["全部优化建议（人审后方可进下一轮工单）"],
        "immutable": ["代码/架构本体（手动，00_index §1）", "自身目标函数与审核门槛"],
    },
    "healthCheck": {"heartbeat": "manual_trigger_only"},
}


def _read_evidence(path: Path) -> Any:
    """只读解析证据文件（.json→对象；.jsonl→行对象列表；其他→原文文本）."""
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    return json.loads(text) if path.suffix == ".json" else text


def _resolve_allowed(raw: str, roots: list[Path]) -> Path | None:
    """证据路径解析+白名单校验（仅 .runtime/logs/docs 内，越界返回 None）."""
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = _REPO_ROOT / candidate
    try:
        resolved = candidate.resolve()
    except OSError:
        return None
    for root in roots:
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            continue
        return resolved if resolved.is_file() else None
    return None


def _summarize(evidence: list[Any]) -> dict[str, Any]:
    """汇总证据：gate 判定分布 + 实验通过情况（只计数，不解释）."""
    gate_counts: dict[str, int] = {}
    experiments = {"total": 0, "passed": 0, "failed": 0}
    for item in evidence:
        for record in [r for r in (item if isinstance(item, list) else [item]) if isinstance(r, dict)]:
            verdicts = record.get("verdicts")
            decisions = (
                [v.get("decision") for v in verdicts if isinstance(v, dict)]
                if isinstance(verdicts, list)
                else [record.get("decision")]
            )
            for decision in [d for d in decisions if isinstance(d, str)]:
                gate_counts[decision] = gate_counts.get(decision, 0) + 1
            passed = record.get("passed")
            if record.get("kind") == "model_evaluation_report" or passed is not None:
                if passed is not None:
                    experiments["total"] += 1
                    experiments["passed" if passed else "failed"] += 1
    return {"gate_decision_counts": gate_counts, "experiments": experiments}


def _build_suggestions(summary: dict[str, Any]) -> list[dict[str, Any]]:
    """按证据汇总模板化出建议（全部 human_gated；只复述缺口，不下执行结论）."""
    gate_counts = summary["gate_decision_counts"]
    experiments = summary["experiments"]
    suggestions: list[dict[str, Any]] = []
    if gate_counts.get("block"):
        suggestions.append(
            {
                "topic": "immutable 拦截复盘",
                "suggestion_zh": f"证据含 {gate_counts['block']} 条 immutable_core "
                "物理拦截，建议人审复盘对应工单越界原因后再排施工。",
            }
        )
    if gate_counts.get("escalate"):
        suggestions.append(
            {
                "topic": "人审工单消化",
                "suggestion_zh": f"证据含 {gate_counts['escalate']} 条 human_gated "
                "升级记录，建议优先消化人审队列再扩自治面。",
            }
        )
    if experiments["failed"]:
        suggestions.append(
            {
                "topic": "失败实验复查",
                "suggestion_zh": f"{experiments['failed']}/{experiments['total']} "
                "条实验未通过，建议复查 PIT/成本口径与登记字段完整性"
                "（只读观察，非结论）。",
            }
        )
    if not suggestions:
        suggestions.append(
            {"topic": "常规巡检", "suggestion_zh": "证据未见拦截/失败信号，建议维持现行门禁与实验纪律。"}
        )
    for item in suggestions:
        item["human_gated"] = item["advice_only"] = True
    return suggestions


def run_iteration_review(
    ticket: dict[str, Any],
    *,
    runtime_dir: str | Path | None = None,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """执行一张迭代评估工单（只读证据→human_gated 建议工单，端到端落盘）.

    ticket={"ticket_id", "evidence_paths": [仓内相对/绝对路径...], "note"?}；
    runtime_dir 落盘根同时是证据白名单根之一。返回建议工单 dict（逐条 human_gated）。
    """
    ticket_id = str(ticket.get("ticket_id") or "").strip()
    if not ticket_id:
        raise ValueError("迭代评估工单缺 ticket_id")
    root = Path(repo_root) if repo_root else _REPO_ROOT
    runtime_base = Path(runtime_dir) if runtime_dir else root / ".runtime"
    store = AgentRunStore(ROLE, runtime_dir=runtime_base, repo_root=root)
    store.begin(ticket_id, ticket)

    allowed_roots = [runtime_base, root / "logs", root / "docs"]
    evidence: list[Any] = []
    skipped: list[str] = []
    for raw in ticket.get("evidence_paths") or []:
        resolved = _resolve_allowed(str(raw), allowed_roots)
        if resolved is None:
            skipped.append(str(raw))
            continue
        try:
            evidence.append(_read_evidence(resolved))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            skipped.append(str(raw))

    summary = _summarize(evidence)
    report = {
        "kind": "iteration_suggestion",
        "advice_only": True,
        "evidence_consumed": len(evidence),
        "skipped_evidence": skipped,
        "summary": summary,
        "suggestions": _build_suggestions(summary),
        "note": str(ticket.get("note") or ""),
    }
    store.write_output("iteration_suggestion.json", report, ticket_id)
    store.finish(ticket_id, "completed", {"evidence_consumed": len(evidence), "skipped": len(skipped)})
    return report


def run_reflection_review(ticket: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    """S1.1 reflection_review 工单（12号文闸门+三角色反思；实现薄委派 _s11_wiring）."""
    from zephyr.autonomy_core.agents import _s11_wiring

    return _s11_wiring.run_reflection_review(ticket, role=ROLE, **kwargs)


def main(argv: list[str] | None = None) -> int:
    """CLI 手动触发入口：--ticket <工单 JSON 路径> [--runtime-dir DIR]."""
    parser = argparse.ArgumentParser(description="自我迭代 Agent 薄入口：迭代评估工单手动触发")
    parser.add_argument("--ticket", required=True, help="迭代评估工单 JSON 路径")
    parser.add_argument("--runtime-dir", default=None, help="落盘根（默认仓根 .runtime/）")
    args = parser.parse_args(argv)
    ticket = json.loads(Path(args.ticket).read_text(encoding="utf-8"))
    kind = str(ticket.get("kind") or "iteration_review")
    if kind == "reflection_review":
        report = run_reflection_review(ticket, runtime_dir=args.runtime_dir)
    elif kind == "iteration_review":
        report = run_iteration_review(ticket, runtime_dir=args.runtime_dir)
    else:
        raise ValueError(f"未知迭代工单 kind: {ticket.get('kind')!r}")
    print(json.dumps({"kind": report["kind"], "status": report.get("status", "completed")}, ensure_ascii=False))
    return 0


__all__ = ["AGENT_CARD", "ROLE", "main", "run_iteration_review", "run_reflection_review"]


if __name__ == "__main__":
    raise SystemExit(main())
