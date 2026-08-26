# [BLUEPRINT] MOD-KNW-011 | docs/03_modules/_domain_knowledge/research_project_aggregate/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-KNW-011 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.knowledge.test_research_project_aggregate
# [TESTS] src/zephyr/knowledge/research_project_aggregate.py
"""MOD-KNW-011 单元测试：research_project_aggregate 研究项目聚合根。

蓝图验收（B6-08533/CAND-KNW-014，B6）：
draft→active→review→archived 四态闭合状态机 + 假设/证据/实验/因子四类
子实体挂载（版本不变量）+ SQLite 持久化（注入 :memory: 连接）+
hypothesis_registry 等联动接口注入。全内存替身，不触网。
"""

from __future__ import annotations

import datetime
import sqlite3

import pytest

pytest.importorskip(
    "zephyr.knowledge.research_project_aggregate",
    reason="research_project_aggregate not importable",
)

from zephyr.knowledge.research_project_aggregate import (  # noqa: E402
    ChildKind,
    ProjectStatus,
    ResearchProjectAggregate,
    ResearchProjectError,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)


def _agg(**linkage) -> ResearchProjectAggregate:
    return ResearchProjectAggregate(
        conn=sqlite3.connect(":memory:"), clock=lambda: _T0, **linkage
    )


# ──────────────────────────────────────────────────────────────────────────────
# 建项与状态机
# ──────────────────────────────────────────────────────────────────────────────


class TestLifecycle:
    def test_conn_not_injected_fail_closed(self) -> None:
        with pytest.raises(ResearchProjectError):
            ResearchProjectAggregate(conn=None, clock=lambda: _T0)

    def test_create_project_draft_v1(self) -> None:
        agg = _agg()
        view = agg.create_project("proj-1", "动量因子研究")
        assert view.status is ProjectStatus.DRAFT
        assert view.version == 1
        assert view.created_at == _T0

    def test_create_duplicate_raises(self) -> None:
        agg = _agg()
        agg.create_project("proj-1", "动量")
        with pytest.raises(ResearchProjectError):
            agg.create_project("proj-1", "重复")

    def test_create_empty_id_or_name_raises(self) -> None:
        agg = _agg()
        with pytest.raises(ResearchProjectError):
            agg.create_project("", "x")
        with pytest.raises(ResearchProjectError):
            agg.create_project("proj-1", "")

    def test_get_unknown_project_raises(self) -> None:
        agg = _agg()
        with pytest.raises(ResearchProjectError):
            agg.get_project("ghost")

    def test_transition_happy_path(self) -> None:
        agg = _agg()
        agg.create_project("proj-1", "动量")
        assert agg.transition("proj-1", ProjectStatus.ACTIVE).status is ProjectStatus.ACTIVE
        assert agg.transition("proj-1", ProjectStatus.REVIEW).status is ProjectStatus.REVIEW
        assert agg.transition("proj-1", ProjectStatus.ARCHIVED).status is ProjectStatus.ARCHIVED

    def test_transition_rework_review_to_active(self) -> None:
        agg = _agg()
        agg.create_project("proj-1", "动量")
        agg.transition("proj-1", ProjectStatus.ACTIVE)
        agg.transition("proj-1", ProjectStatus.REVIEW)
        assert agg.transition("proj-1", ProjectStatus.ACTIVE).status is ProjectStatus.ACTIVE

    def test_transition_skip_raises(self) -> None:
        agg = _agg()
        agg.create_project("proj-1", "动量")
        with pytest.raises(ResearchProjectError):
            agg.transition("proj-1", ProjectStatus.REVIEW)  # draft→review 越态

    def test_transition_archived_terminal(self) -> None:
        agg = _agg()
        agg.create_project("proj-1", "动量")
        agg.transition("proj-1", ProjectStatus.ACTIVE)
        agg.transition("proj-1", ProjectStatus.REVIEW)
        agg.transition("proj-1", ProjectStatus.ARCHIVED)
        with pytest.raises(ResearchProjectError):
            agg.transition("proj-1", ProjectStatus.ACTIVE)

    def test_transition_same_state_raises(self) -> None:
        agg = _agg()
        agg.create_project("proj-1", "动量")
        with pytest.raises(ResearchProjectError):
            agg.transition("proj-1", ProjectStatus.DRAFT)

    def test_transition_bumps_version(self) -> None:
        agg = _agg()
        agg.create_project("proj-1", "动量")
        view = agg.transition("proj-1", ProjectStatus.ACTIVE)
        assert view.version == 2

    def test_list_projects_deterministic(self) -> None:
        agg = _agg()
        agg.create_project("proj-b", "乙")
        agg.create_project("proj-a", "甲")
        agg.transition("proj-a", ProjectStatus.ACTIVE)
        assert [p.project_id for p in agg.list_projects()] == ["proj-a", "proj-b"]
        active = agg.list_projects(status=ProjectStatus.ACTIVE)
        assert [p.project_id for p in active] == ["proj-a"]


# ──────────────────────────────────────────────────────────────────────────────
# 子实体挂载（版本不变量 + 联动）
# ──────────────────────────────────────────────────────────────────────────────


class TestAttachChild:
    def test_attach_four_kinds(self) -> None:
        agg = _agg()
        agg.create_project("proj-1", "动量")
        for kind, ref in (
            (ChildKind.HYPOTHESIS, "hyp-1"),
            (ChildKind.EVIDENCE, "evi-1"),
            (ChildKind.EXPERIMENT, "exp-1"),
            (ChildKind.FACTOR, "fac-1"),
        ):
            child = agg.attach_child("proj-1", kind, ref)
            assert child.version == 1
        children = agg.children_of("proj-1")
        assert len(children) == 4
        assert [c.kind for c in children] == [
            ChildKind.EVIDENCE, ChildKind.EXPERIMENT, ChildKind.FACTOR, ChildKind.HYPOTHESIS,
        ]  # (kind, ref_id) 确定性排序

    def test_reattach_bumps_version(self) -> None:
        agg = _agg()
        agg.create_project("proj-1", "动量")
        agg.attach_child("proj-1", ChildKind.HYPOTHESIS, "hyp-1")
        child = agg.attach_child("proj-1", ChildKind.HYPOTHESIS, "hyp-1", note="修订")
        assert child.version == 2  # 版本不变量：重挂严格 +1
        assert agg.child_version("proj-1", ChildKind.HYPOTHESIS, "hyp-1") == 2

    def test_attach_bumps_project_version(self) -> None:
        agg = _agg()
        agg.create_project("proj-1", "动量")
        agg.attach_child("proj-1", ChildKind.FACTOR, "fac-1")
        assert agg.get_project("proj-1").version == 2

    def test_attach_to_archived_raises(self) -> None:
        agg = _agg()
        agg.create_project("proj-1", "动量")
        agg.transition("proj-1", ProjectStatus.ACTIVE)
        agg.transition("proj-1", ProjectStatus.REVIEW)
        agg.transition("proj-1", ProjectStatus.ARCHIVED)
        with pytest.raises(ResearchProjectError):
            agg.attach_child("proj-1", ChildKind.FACTOR, "fac-1")

    def test_attach_unknown_project_raises(self) -> None:
        agg = _agg()
        with pytest.raises(ResearchProjectError):
            agg.attach_child("ghost", ChildKind.FACTOR, "fac-1")

    def test_attach_invalid_kind_or_ref_raises(self) -> None:
        agg = _agg()
        agg.create_project("proj-1", "动量")
        with pytest.raises(ResearchProjectError):
            agg.attach_child("proj-1", "memo", "x")  # type: ignore[arg-type]
        with pytest.raises(ResearchProjectError):
            agg.attach_child("proj-1", ChildKind.FACTOR, "")

    def test_children_of_filter_by_kind(self) -> None:
        agg = _agg()
        agg.create_project("proj-1", "动量")
        agg.attach_child("proj-1", ChildKind.FACTOR, "fac-2")
        agg.attach_child("proj-1", ChildKind.FACTOR, "fac-1")
        agg.attach_child("proj-1", ChildKind.HYPOTHESIS, "hyp-1")
        factors = agg.children_of("proj-1", kind=ChildKind.FACTOR)
        assert [c.ref_id for c in factors] == ["fac-1", "fac-2"]  # 确定性排序

    def test_child_version_unattached_raises(self) -> None:
        agg = _agg()
        agg.create_project("proj-1", "动量")
        with pytest.raises(ResearchProjectError):
            agg.child_version("proj-1", ChildKind.EVIDENCE, "ghost")

    def test_linkage_adapters_called(self) -> None:
        seen: list[tuple[str, str, str]] = []

        def _mk(tag: str):
            return lambda pid, child: seen.append((tag, pid, child.ref_id))

        agg = _agg(
            hypothesis_registry=_mk("hypothesis_registry"),
            evidence_chain=_mk("evidence_chain"),
            experiment_tracker=_mk("experiment_tracker"),
            factor_sink=_mk("factor_sink"),
        )
        agg.create_project("proj-1", "动量")
        agg.attach_child("proj-1", ChildKind.HYPOTHESIS, "hyp-1")
        agg.attach_child("proj-1", ChildKind.FACTOR, "fac-1")
        assert seen == [
            ("hypothesis_registry", "proj-1", "hyp-1"),
            ("factor_sink", "proj-1", "fac-1"),
        ]

    def test_linkage_failure_not_blocking(self) -> None:
        def _boom(pid: str, child) -> None:
            raise RuntimeError("registry 不可用")

        agg = _agg(hypothesis_registry=_boom)
        agg.create_project("proj-1", "动量")
        child = agg.attach_child("proj-1", ChildKind.HYPOTHESIS, "hyp-1")
        assert child.version == 1  # 联动异常不阻断挂载

    def test_persistence_survives_reopen(self) -> None:
        conn = sqlite3.connect(":memory:")
        agg = ResearchProjectAggregate(conn=conn, clock=lambda: _T0)
        agg.create_project("proj-1", "动量")
        agg.attach_child("proj-1", ChildKind.EXPERIMENT, "exp-1")
        reopened = ResearchProjectAggregate(conn=conn, clock=lambda: _T0)
        assert reopened.get_project("proj-1").name == "动量"
        assert reopened.child_version("proj-1", ChildKind.EXPERIMENT, "exp-1") == 1
