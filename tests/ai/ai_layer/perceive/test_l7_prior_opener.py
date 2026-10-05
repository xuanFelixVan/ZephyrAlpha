# [MODULE] tests.ai_layer.perceive.test_l7_prior_opener
# [TTL] permanent
"""l7_prior_opener 单测：假 priors 注入（零 DB），journal 落 tmp_path（测试隔离铁律）。"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

from zephyr.ai_layer.perceive.l7_prior_opener import l7_prior_daily_share_state, open_l7_prior_order
from zephyr.ai_layer.perceive.search_orders import SearchOrderDraft, SearchOrderJournal
from zephyr.shared.utils.time_utils import now_utc


@dataclass
class _FakeAntiIncest:
    prior_factor_min: float = 1.0
    prior_factor_max: float = 2.0
    l7_prior_daily_share_max: float = 0.5


@dataclass
class _FakePolicy:
    anti_incest: _FakeAntiIncest = field(default_factory=_FakeAntiIncest)


class _FakePriors:
    """duck HeritagePriors：prior_for 可编程（零 DB）。"""

    def __init__(
        self,
        prior: dict[str, Any] | None = None,
        *,
        share_max: float = 0.5,
        total_cells: int = 100,
    ) -> None:
        self._prior = prior or {
            "prior_factor": 1.0,
            "rationale_refs": [],
            "exclusion_keywords": [],
            "frozen": False,
        }
        self.policy = _FakePolicy(_FakeAntiIncest(l7_prior_daily_share_max=share_max))
        self.total_cells = total_cells
        self.calls: list[tuple[str, str]] = []

    def prior_for(self, domain_id: str, mechanism_family: str) -> dict[str, Any]:
        self.calls.append((domain_id, mechanism_family))
        return dict(self._prior)


@pytest.fixture()
def journal(tmp_path: Path) -> SearchOrderJournal:
    return SearchOrderJournal(tmp_path / "orders")


MOMENT = now_utc().replace(hour=1, minute=0, second=0, microsecond=0)


def test_prior_factor_lands_on_priority_and_trigger(journal: SearchOrderJournal) -> None:
    priors = _FakePriors({"prior_factor": 1.8, "rationale_refs": ["L7:e1"], "exclusion_keywords": [], "frozen": False})
    out = open_l7_prior_order(
        journal,
        priors,
        domain_id="dom_a",
        mechanism_family="fam_x",
        vein_id="VEIN-1",
        trigger_ref="L7:prior:dom_a:fam_x",
        keyword_groups=[["alpha", "beta"], ["gamma"]],
        now=MOMENT,
    )
    assert out["ok"] is True
    order = out["order"]
    assert order.trigger == "l7_prior" and order.priority == 1.8
    assert order.vein_family == "fam_x"
    assert order.keyword_groups == ("alpha", "beta", "gamma")  # 组拍平为扁平词表
    assert priors.calls == [("dom_a", "fam_x")]
    assert out["dropped_groups"] == []


def test_exclusion_filters_group_but_keeps_one(journal: SearchOrderJournal) -> None:
    priors = _FakePriors({"prior_factor": 1.5, "rationale_refs": [], "exclusion_keywords": ["poison"], "frozen": False})
    out = open_l7_prior_order(
        journal,
        priors,
        domain_id="dom_a",
        mechanism_family="fam_x",
        vein_id="VEIN-1",
        trigger_ref="ref-1",
        keyword_groups=[["poison", "bad"], ["clean", "keep"]],
        now=MOMENT,
    )
    assert out["ok"] is True
    assert out["order"].keyword_groups == ("clean", "keep")
    assert out["dropped_groups"] == [["poison", "bad"]]


def test_exclusion_all_groups_filtered_keeps_first(journal: SearchOrderJournal) -> None:
    """只滤词不灭矿脉：全滤时保底保留第一组原样。"""
    priors = _FakePriors({"prior_factor": 1.2, "rationale_refs": [], "exclusion_keywords": ["a", "x"], "frozen": False})
    out = open_l7_prior_order(
        journal,
        priors,
        domain_id="d",
        mechanism_family="f",
        vein_id="V",
        trigger_ref="ref-2",
        keyword_groups=[["a"], ["x"]],
        now=MOMENT,
    )
    assert out["ok"] is True
    assert out["order"].keyword_groups == ("a",)


def test_missing_prior_row_empty_prior_opens(journal: SearchOrderJournal) -> None:
    priors = _FakePriors(None)
    out = open_l7_prior_order(
        journal,
        priors,
        domain_id="d",
        mechanism_family="f",
        vein_id="V",
        trigger_ref="r",
        keyword_groups=[["k"]],
        now=MOMENT,
    )
    assert out["ok"] is True
    assert out["order"].priority == 1.0
    assert out["prior"]["prior_factor"] == 1.0


def test_daily_share_exceeded_refuses_without_order(journal: SearchOrderJournal) -> None:
    priors = _FakePriors(share_max=0.5)
    # 当日已有 1 l7_prior 单 + 1 其他单 → 占比 50% 未超；再开将超（1/3 后 2/…）——
    # 造 3 单中 2 单 l7（占比 2/3>50%）后第三单必须拒。
    open_l7_prior_order(
        journal,
        priors,
        domain_id="d",
        mechanism_family="f",
        vein_id="V",
        trigger_ref="r1",
        keyword_groups=[["k"]],
        now=MOMENT,
    )
    journal.open_draft(
        SearchOrderDraft(
            vein_id="V2",
            vein_family="f",
            trigger="beat",
            trigger_ref="beat-1",
            keyword_groups=["b"],
            now=MOMENT,
        )
    )
    state = l7_prior_daily_share_state(journal, priors, now=MOMENT)
    assert state == (False, 1, 2)
    open_l7_prior_order(
        journal,
        priors,
        domain_id="d",
        mechanism_family="f",
        vein_id="V3",
        trigger_ref="r2",
        keyword_groups=[["k"]],
        now=MOMENT,
    )
    state2 = l7_prior_daily_share_state(journal, priors, now=MOMENT)
    assert state2 == (True, 2, 3)
    refused = open_l7_prior_order(
        journal,
        priors,
        domain_id="d",
        mechanism_family="f",
        vein_id="V4",
        trigger_ref="r3",
        keyword_groups=[["k"]],
        now=MOMENT,
    )
    assert refused["ok"] is False and refused["reason"] == "refused_l7_daily_share"
    assert refused["l7_n"] == 2 and refused["total_n"] == 3
    assert all(o.vein_id != "V4" for o in journal.list_orders())


def test_empty_keyword_groups_raises(journal: SearchOrderJournal) -> None:
    with pytest.raises(ValueError, match="keyword_groups 空"):
        open_l7_prior_order(
            journal,
            _FakePriors(),
            domain_id="d",
            mechanism_family="f",
            vein_id="V",
            trigger_ref="r",
            keyword_groups=[],
            now=MOMENT,
        )
