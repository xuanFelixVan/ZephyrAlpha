# [BLUEPRINT] MOD-VOTE_REVIEW_SHELL | docs/03_modules/_domain_autonomy_core/vote_review_shell/blueprint.md | §
# [MODULE] zephyr.intelligence.reflexion.vote_review_shell
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_voting(A2AVoting/VoteAction); zephyr.shared.io.paths(MAIN_REPO_ROOT); zephyr.shared.utils.time_utils(now_utc_str)
# [CONSUMERS] 人手动触发 CLI(python -m zephyr.intelligence.reflexion.vote_review_shell)
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 壳体<100 行纯编排; 引擎复用零改动(MOD-INF-025 只消费); 无自动触发路径(唯一入口=人手动 CLI); 产出=评审报告 human_gated(不自动应用裁决)
# [MODIFY-GUARD] 变更须同步 12号文 §3.6
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] VoteReviewError — 输入目录缺失/选票文件非法/非法投票动作即抛, fail-closed 不产半成品报告
# [TESTS] tests/intelligence/test_vote_review_shell.py
# [A_module] module_id=MOD-VOTE_REVIEW_SHELL | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""投票评审壳（12号文 §3.6/§4.3 P1-2）——可选模式设施，人手动触发.

定位: 高价值评审场景（如因子入库终审）人多开 3-5 个 AI 会话并行产出候选后,
由人手动调用本壳完成计票裁决: 候选文件收集 → 调既有 A2AVoting 引擎(MOD-INF-025,
approve/reject/abstain + quorum + 权重, 只消费不改结构)逐候选计票 → 最优候选落盘
selected/ → 裁决报告 JSON 落盘. 全程文件交接, 默认根目录 .runtime/vote_review/.
主路径不变: solo 单 session + red_blue_validator(#ARCH-OE-011), 本壳默认不启用.

输入目录契约(候选目录, 默认 .runtime/vote_review/inbox/):
  candidates/<candidate_id>.<ext>  候选产出文件(候选 ID=文件名 stem)
  votes/<session>.json             每会话一份选票: {"agent_id", "weight"?=1.0,
                                   "votes": {candidate_id: "approve"|"reject"|"abstain"}}

输出: 裁决报告 JSON(默认 .runtime/vote_review/report.json); verdict ∈
selected/no_consensus/no_candidates/engine_error; human_gate_required 恒 true;
胜出候选复制到 <报告目录>/selected/.

裁决规则: 仅 quorum_met 且 passed(approve>reject, 引擎口径)候选可胜出; 多名通过
按 (净票 approve-reject, approve_weight) 取最优, 同分取 candidate_id 字典序最小
(max 稳定性+候选按字典序装载, 确定性 tiebreak); 无候选通过 → no_consensus 不选优.

行数口径(P1-2 验收"壳体<100 行"): 纯逻辑行=tokenize 剥离纯注释行+ast 剥离
docstring 后的非空物理行数(含 import/类与函数声明行), 实测值见当次施工报告.

不做什么: 不含调度器/定时器/钩子/导入副作用(人手动 CLI 为唯一触发路径); 不做
辩论制评审(Phase 2 P2-2); 不呼叫任何 LLM(会话产出由人搬运落盘); 不自动应用
胜出候选(产出仅供人终审).
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
from dataclasses import dataclass
from pathlib import Path

from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_voting import A2AVoting, VoteAction
from zephyr.shared.io.paths import MAIN_REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc_str

logger = logging.getLogger(__name__)

DEFAULT_ROOT: Path = MAIN_REPO_ROOT / ".runtime" / "vote_review"


class VoteReviewError(RuntimeError):
    """输入目录缺失、选票文件非法或投票动作非法（fail-closed，不产半成品报告）."""


@dataclass(frozen=True)
class SessionBallot:
    """单会话选票：agent_id + 权重 + 对各候选的 approve/reject/abstain 映射."""

    agent_id: str
    weight: float
    votes: dict[str, str]


def _load_inbox(candidates_dir: Path) -> tuple[dict[str, Path], list[SessionBallot]]:
    pool, votes_dir = candidates_dir / "candidates", candidates_dir / "votes"
    for directory in (pool, votes_dir):
        if not directory.is_dir():
            raise VoteReviewError(f"输入目录缺失: {directory}")
    candidates = {p.stem: p for p in sorted(pool.iterdir()) if p.is_file()}
    ballots: list[SessionBallot] = []
    for path in sorted(votes_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            ballots.append(SessionBallot(str(data["agent_id"]), float(data.get("weight", 1.0)),
                                         {str(k): str(v) for k, v in data["votes"].items()}))
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise VoteReviewError(f"选票文件非法: {path} ({exc})") from exc
    return candidates, ballots


def _cast_all(engine: A2AVoting, candidate_id: str, ballots: list[SessionBallot], warnings: list[str]) -> None:
    engine.open_proposal(candidate_id)
    for ballot in ballots:
        raw = ballot.votes.get(candidate_id)
        if raw is None:
            warnings.append(f"会话 {ballot.agent_id} 未对候选 {candidate_id} 投票")
            continue
        try:
            action = VoteAction(raw)
        except ValueError as exc:
            raise VoteReviewError(f"会话 {ballot.agent_id} 非法投票动作: {raw}") from exc
        engine.cast_vote(candidate_id, ballot.agent_id, action, ballot.weight)


def _pick_winner(results: list[dict]) -> dict | None:
    passed = [r for r in results if r["passed"]]
    return max(passed, key=lambda r: (r["approve_weight"] - r["reject_weight"], r["approve_weight"]), default=None)


def run_review(candidates_dir: Path, output_path: Path, *, quorum: float = 0.5, engine: A2AVoting | None = None) -> dict:
    """候选收集→A2AVoting 逐候选计票→最优落盘 selected/→裁决报告 JSON（人手动调用）."""
    candidates_dir, output_path = Path(candidates_dir), Path(output_path)
    candidates, ballots = _load_inbox(candidates_dir)
    engine = engine if engine is not None else A2AVoting(default_quorum=quorum)
    ghost = sorted({c for b in ballots for c in b.votes} - candidates.keys())
    warnings: list[str] = [f"选票指向缺失候选 {cid}, 已忽略" for cid in ghost]
    results, winner, error = [], None, None
    try:
        for cid, path in candidates.items():
            _cast_all(engine, cid, ballots, warnings)
            r = engine.tally(cid, len(ballots))
            results.append({"candidate_id": cid, "file": str(path), "passed": r.passed, "quorum_met": r.quorum_met,
                            "approve_weight": r.approve_weight, "reject_weight": r.reject_weight,
                            "abstain_weight": r.abstain_weight, "total_weight": r.total_weight, "votes": r.votes})
    except VoteReviewError:
        raise
    except Exception as exc:  # 引擎异常降级: 已计票明细+错误落盘交人, 不抛出
        logger.exception("A2AVoting 引擎异常, 降级 engine_error")
        verdict, error = "engine_error", f"{type(exc).__name__}: {exc}"
    else:
        winner = _pick_winner(results)
        verdict = "no_candidates" if not candidates else ("selected" if winner else "no_consensus")
    selected = None
    if winner is not None:
        selected = output_path.parent / "selected" / Path(winner["file"]).name
        selected.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(winner["file"], selected)
    report = {"verdict": verdict, "generated_at": now_utc_str(), "quorum": quorum,
              "participant_count": len(ballots), "candidates": results,
              "winner": winner["candidate_id"] if winner else None,
              "selected_file": str(selected) if selected else None,
              "warnings": warnings, "error": error, "human_gate_required": True}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    """人手动 CLI 入口（唯一触发路径；无调度器/定时器/导入副作用）."""
    parser = argparse.ArgumentParser(description="投票评审壳(可选模式设施, 人手动触发; 12号文 §3.6/§4.3 P1-2)")
    parser.add_argument("--candidates-dir", type=Path, default=DEFAULT_ROOT / "inbox")
    parser.add_argument("--output", type=Path, default=DEFAULT_ROOT / "report.json")
    parser.add_argument("--quorum", type=float, default=0.5)
    args = parser.parse_args(argv)
    try:
        report = run_review(args.candidates_dir, args.output, quorum=args.quorum)
    except VoteReviewError as exc:
        parser.error(str(exc))
    print(json.dumps({"verdict": report["verdict"], "winner": report["winner"],
                      "report": str(args.output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
