# [BLUEPRINT] MOD-EX-064 | docs/03_modules/_domain_execution_core/execution_param_optimizer/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-EX-064 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.ex_core.test_execution_param_optimizer
# [TESTS] src/zephyr/ex_core/execution_param_optimizer.py
"""MOD-EX-064 单元测试：execution_param_optimizer 执行运营自优化器。

蓝图验收（B1-00218/CAND-EX-010，C2 C-026）：
周期读 TCA（注入 tca_reader，未注入/为空 Fail-Closed）+ optuna 搜索注入
（study_runner，未装/异常降级网格搜索）+ 人工确认队列硬约束（未确认提案不
改变生效参数）+ 风控硬阈值白名单拦截（声明校验 + 搜索结果校验双闸）+
提案状态机 PENDING→CONFIRMED|REJECTED + 确定性（同输入必同输出）。
读取/搜索/时钟/审计全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime
from decimal import Decimal

import pytest

pytest.importorskip(
    "zephyr.ex_core.execution_param_optimizer",
    reason="execution_param_optimizer not importable",
)

from zephyr.ex_core.execution_param_optimizer import (  # noqa: E402
    ExecutionOptimizerError,
    ExecutionParamOptimizer,
    ParamSpec,
    ProposalStatus,
    TcaSnapshot,
)

_T0 = datetime.datetime(2026, 8, 25, 16, 0, 0)

_SPACE = {
    "participation_rate": ParamSpec(
        name="participation_rate",
        candidates=(Decimal("0.05"), Decimal("0.10"), Decimal("0.20")),
    ),
    "wait_seconds": ParamSpec(name="wait_seconds", candidates=(30, 60, 120)),
}
_WHITELIST = frozenset(_SPACE)


def _snapshots() -> list[TcaSnapshot]:
    return [
        TcaSnapshot(
            snapshot_id="snap-1",
            algo="twap",
            slippage_bps=Decimal("12.5"),
            fill_rate=Decimal("0.98"),
            observed_at=_T0,
        ),
        TcaSnapshot(
            snapshot_id="snap-2",
            algo="vwap",
            slippage_bps=Decimal("7.5"),
            fill_rate=Decimal("0.99"),
            observed_at=_T0,
        ),
    ]


def _objective(params, snaps) -> Decimal:
    # 目标：平均滑点 + 参与率偏离 0.10 的惩罚（越小越好；wait_seconds 不影响）
    mean_slip = sum((s.slippage_bps for s in snaps), Decimal("0")) / Decimal(len(snaps))
    return mean_slip + abs(params["participation_rate"] - Decimal("0.10")) * 100


def _optimizer(**kwargs) -> ExecutionParamOptimizer:
    base = {
        "param_space": _SPACE,
        "whitelist": _WHITELIST,
        "tca_reader": _snapshots,
        "objective_fn": _objective,
        "clock": lambda: _T0,
    }
    base.update(kwargs)
    return ExecutionParamOptimizer(**base)


# ──────────────────────────────────────────────────────────────────────────────
# 构造校验（白名单第一道闸）
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_init_ok_defaults(self) -> None:
        opt = _optimizer()
        # 生效参数初值=各参数首候选（确定性默认）
        assert opt.active_params() == {
            "participation_rate": Decimal("0.05"),
            "wait_seconds": 30,
        }
        assert opt.pending_proposals() == []

    def test_empty_space_raises(self) -> None:
        with pytest.raises(ExecutionOptimizerError):
            _optimizer(param_space={})

    def test_empty_whitelist_raises(self) -> None:
        with pytest.raises(ExecutionOptimizerError):
            _optimizer(whitelist=frozenset())

    def test_param_not_in_whitelist_raises(self) -> None:
        # 风控硬阈值拦截：声明了白名单外参数（如参与率未获授权）→ Fail-Closed
        with pytest.raises(ExecutionOptimizerError):
            _optimizer(whitelist=frozenset({"wait_seconds"}))

    def test_empty_candidates_raises(self) -> None:
        space = {"alpha": ParamSpec(name="alpha", candidates=())}
        with pytest.raises(ExecutionOptimizerError):
            _optimizer(param_space=space, whitelist=frozenset({"alpha"}))


# ──────────────────────────────────────────────────────────────────────────────
# 周期优化（TCA 读数 + 搜索 + 降级）
# ──────────────────────────────────────────────────────────────────────────────


class TestRunCycle:
    def test_grid_search_picks_best(self) -> None:
        opt = _optimizer()
        proposal = opt.run_cycle("20260825-eod")
        assert proposal.proposal_id == "PROP-20260825-eod"
        assert proposal.source == "grid"
        assert proposal.status is ProposalStatus.PENDING
        # 目标最小点：participation_rate=0.10（惩罚 0），wait_seconds 取首候选
        assert proposal.params == {
            "participation_rate": Decimal("0.10"),
            "wait_seconds": 30,
        }
        assert proposal.objective_value == Decimal("10")  # (12.5+7.5)/2 + 0
        assert proposal.created_at == _T0

    def test_study_runner_used(self) -> None:
        seen: list = []

        def runner(space, objective):
            seen.append(sorted(space))
            assert callable(objective)
            return {"participation_rate": Decimal("0.20")}

        opt = _optimizer(study_runner=runner)
        proposal = opt.run_cycle("c1")
        assert proposal.source == "optuna"
        assert seen == [["participation_rate", "wait_seconds"]]
        # 部分返回时合并默认：wait_seconds 仍为默认 30
        assert proposal.params == {
            "participation_rate": Decimal("0.20"),
            "wait_seconds": 30,
        }
        assert proposal.objective_value == Decimal("20")  # 10 + |0.20-0.10|*100

    def test_study_runner_exception_degrades_to_grid(self) -> None:
        def runner(space, objective):
            raise RuntimeError("optuna 未装/内部故障")

        opt = _optimizer(study_runner=runner)
        proposal = opt.run_cycle("c1")
        assert proposal.source == "grid"
        assert proposal.params["participation_rate"] == Decimal("0.10")
        assert proposal.status is ProposalStatus.PENDING

    def test_study_runner_out_of_whitelist_blocked(self) -> None:
        # 风控硬阈值拦截：搜索试图改 max_position（非白名单）→ Fail-Closed 不降级
        def runner(space, objective):
            return {"max_position": 100000}

        opt = _optimizer(study_runner=runner)
        with pytest.raises(ExecutionOptimizerError):
            opt.run_cycle("c1")

    def test_study_runner_value_outside_candidates_raises(self) -> None:
        def runner(space, objective):
            return {"participation_rate": Decimal("0.15")}  # 非候选取值

        opt = _optimizer(study_runner=runner)
        with pytest.raises(ExecutionOptimizerError):
            opt.run_cycle("c1")

    def test_tca_reader_missing_fail_closed(self) -> None:
        opt = _optimizer(tca_reader=None)
        with pytest.raises(ExecutionOptimizerError):
            opt.run_cycle("c1")

    def test_tca_empty_raises(self) -> None:
        opt = _optimizer(tca_reader=lambda: [])
        with pytest.raises(ExecutionOptimizerError):
            opt.run_cycle("c1")

    def test_duplicate_cycle_id_raises(self) -> None:
        opt = _optimizer()
        opt.run_cycle("c1")
        with pytest.raises(ExecutionOptimizerError):
            opt.run_cycle("c1")

    def test_empty_cycle_id_raises(self) -> None:
        opt = _optimizer()
        with pytest.raises(ExecutionOptimizerError):
            opt.run_cycle("")

    def test_default_objective_first_candidates(self) -> None:
        # 默认目标（平均滑点）与参数无关 → 网格确定性取首候选组合
        opt = _optimizer(objective_fn=None)
        proposal = opt.run_cycle("c1")
        assert proposal.params == {
            "participation_rate": Decimal("0.05"),
            "wait_seconds": 30,
        }
        assert proposal.objective_value == Decimal("10")


# ──────────────────────────────────────────────────────────────────────────────
# 人工确认队列（硬约束：未确认不生效）
# ──────────────────────────────────────────────────────────────────────────────


class TestConfirmQueue:
    def test_unconfirmed_proposal_not_effective(self) -> None:
        opt = _optimizer()
        opt.run_cycle("c1")
        # 硬约束：未人工确认，生效参数保持默认
        assert opt.active_params() == {
            "participation_rate": Decimal("0.05"),
            "wait_seconds": 30,
        }
        assert opt.proposal_status("PROP-c1") is ProposalStatus.PENDING

    def test_confirm_applies_params(self) -> None:
        opt = _optimizer()
        opt.run_cycle("c1")
        opt.confirm("PROP-c1", confirmed_by="ops_zhang")
        assert opt.active_params() == {
            "participation_rate": Decimal("0.10"),
            "wait_seconds": 30,
        }
        assert opt.proposal_status("PROP-c1") is ProposalStatus.CONFIRMED

    def test_confirm_unknown_raises(self) -> None:
        opt = _optimizer()
        with pytest.raises(ExecutionOptimizerError):
            opt.confirm("PROP-ghost", confirmed_by="ops_zhang")

    def test_confirm_twice_raises(self) -> None:
        opt = _optimizer()
        opt.run_cycle("c1")
        opt.confirm("PROP-c1", confirmed_by="ops_zhang")
        with pytest.raises(ExecutionOptimizerError):
            opt.confirm("PROP-c1", confirmed_by="ops_zhang")

    def test_confirm_empty_operator_raises(self) -> None:
        opt = _optimizer()
        opt.run_cycle("c1")
        with pytest.raises(ExecutionOptimizerError):
            opt.confirm("PROP-c1", confirmed_by="")

    def test_reject_keeps_params(self) -> None:
        opt = _optimizer()
        opt.run_cycle("c1")
        opt.reject("PROP-c1", rejected_by="ops_li")
        assert opt.active_params() == {
            "participation_rate": Decimal("0.05"),
            "wait_seconds": 30,
        }
        assert opt.proposal_status("PROP-c1") is ProposalStatus.REJECTED
        with pytest.raises(ExecutionOptimizerError):
            opt.confirm("PROP-c1", confirmed_by="ops_zhang")  # 已驳回不可再确认

    def test_pending_proposals_order(self) -> None:
        opt = _optimizer()
        opt.run_cycle("c2")
        opt.run_cycle("c1")
        pending = opt.pending_proposals()
        assert [p.proposal_id for p in pending] == ["PROP-c1", "PROP-c2"]  # 同刻按 id 排序
        opt.confirm("PROP-c1", confirmed_by="ops_zhang")
        assert [p.proposal_id for p in opt.pending_proposals()] == ["PROP-c2"]


# ──────────────────────────────────────────────────────────────────────────────
# 确定性与审计
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminismAndAudit:
    def test_deterministic_repeat(self) -> None:
        p1 = _optimizer().run_cycle("c1")
        p2 = _optimizer().run_cycle("c1")
        assert p1.params == p2.params
        assert p1.objective_value == p2.objective_value
        assert p1.source == p2.source

    def test_audit_events(self) -> None:
        events: list[dict] = []
        opt = _optimizer(audit_sink=lambda e: events.append(e))
        opt.run_cycle("c1")
        opt.run_cycle("c2")
        opt.confirm("PROP-c1", confirmed_by="ops_zhang")
        opt.reject("PROP-c2", rejected_by="ops_li")
        assert [e["event"] for e in events] == ["proposal_confirmed", "proposal_rejected"]
        assert events[0]["operator"] == "ops_zhang"
        assert events[0]["at"] == _T0

    def test_audit_sink_exception_swallowed(self) -> None:
        def bad_sink(event):
            raise RuntimeError("审计通道故障")

        opt = _optimizer(audit_sink=bad_sink)
        opt.run_cycle("c1")
        opt.confirm("PROP-c1", confirmed_by="ops_zhang")  # 审计异常不阻断确认
        assert opt.proposal_status("PROP-c1") is ProposalStatus.CONFIRMED
