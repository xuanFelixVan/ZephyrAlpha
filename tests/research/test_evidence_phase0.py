"""研究证据关联组件 Phase 0 测试（18号清单 §6 波4-11 / 11号文 §4.2 P0-1~P0-4）。

覆盖（设计真源：11号文 §4.2 验收标准逐条映射）：
- P0-1 假设注册表：CRUD + 状态机全路径（proposed→testing→supported/refuted→archived）；
  非法迁移被拒（proposed→supported 直飞 / archived→testing 复活 / supported→testing 倒退等）；
  状态迁移历史留痕；JSON 落盘后重载一致。
- P0-2 证据链：三态词表外取值被拒；外键约束（hypothesis 不存在拒挂）；
  SHA-256 固化——篡改落盘 jsonl 任一条目内容 → 完整性校验失败；append-only 重载一致。
- P0-3 迭代引导器：人工构造证据序列 → 继续/转向/放弃三态建议与规则推演一致；
  每条建议带命中规则 id + 证据计数（可追溯）；规则表 config 化（非法规则配置加载即拒）。
- P0-4 批量入口：全量假设批量评估 → 迭代建议清单落盘；盘中时段（工作日 09:30-15:00 CST）
  拒绝执行；盘后/周末允许；frequency 词表外取值被拒。
全部落盘走 tmp_path，不触网不触库不写仓内 data/。
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from zephyr.research.evidence.batch_entry import (
    IntradayExecutionForbiddenError,
    is_intraday,
    main,
    run_batch,
)
from zephyr.research.evidence.evidence_chain import (
    EvidenceChain,
    EvidenceIntegrityError,
    InvalidPolarityError,
    UnknownHypothesisError,
)
from zephyr.research.evidence.hypothesis_registry import (
    ALLOWED_TRANSITIONS,
    HypothesisNotFoundError,
    HypothesisRegistry,
    HypothesisRegistryError,
    HypothesisStatus,
    InvalidTransitionError,
)
from zephyr.research.evidence.iteration_guide import (
    GuideRule,
    IterationGuide,
    IterationGuideConfigError,
    Recommendation,
    load_rules,
)

CST = timezone(timedelta(hours=8))
# 2026-08-24 为周一；2026-08-22 为周六
MON = lambda h, m=0: datetime(2026, 8, 24, h, m, tzinfo=CST)  # noqa: E731
SAT = lambda h, m=0: datetime(2026, 8, 22, h, m, tzinfo=CST)  # noqa: E731

GUIDE_RULES = [
    GuideRule(
        rule_id="R-ABANDON-CONTRADICTED",
        recommendation=Recommendation.ABANDON,
        conditions={"contradict_gte": 2, "no_support_within_weeks": 4},
        rationale_zh="独立反驳证据≥2 条且近 4 周无新支持 → 建议放弃",
    ),
    GuideRule(
        rule_id="R-PIVOT-ALL-NEUTRAL",
        recommendation=Recommendation.PIVOT,
        conditions={"evidence_gte": 3, "support_eq": 0, "contradict_eq": 0},
        rationale_zh="证据≥3 条且全为中性 → 方向无判别力，建议转向",
    ),
    GuideRule(
        rule_id="R-PIVOT-CONTESTED",
        recommendation=Recommendation.PIVOT,
        conditions={"support_gte": 1, "contradict_gte": 1},
        rationale_zh="支持/反驳证据并存 → 建议转向细化适用边界",
    ),
    GuideRule(
        rule_id="R-CONTINUE-SUPPORTED",
        recommendation=Recommendation.CONTINUE,
        conditions={"support_gte": 2, "contradict_eq": 0},
        rationale_zh="支持证据≥2 且零反驳 → 建议继续投入",
    ),
    GuideRule(
        rule_id="R-CONTINUE-DEFAULT",
        recommendation=Recommendation.CONTINUE,
        conditions={},
        rationale_zh="兜底规则——证据不足，继续收集",
    ),
]


def _registry(tmp_path: Path) -> HypothesisRegistry:
    return HypothesisRegistry(store_dir=tmp_path / "store")


def _chain(tmp_path: Path, registry: HypothesisRegistry) -> EvidenceChain:
    return EvidenceChain(store_dir=tmp_path / "store", registry=registry)


# ============================================================================
# P0-1 假设注册表：状态机
# ============================================================================


class TestHypothesisStateMachine:
    """状态机全路径 + 非法迁移拒绝（11号文 P0-1 验收）。"""

    def test_legal_path_supported(self, tmp_path):
        reg = _registry(tmp_path)
        h = reg.create("因子 X 在 regime Y 下有效", at=MON(16))
        assert h.status is HypothesisStatus.PROPOSED
        h = reg.transition(h.hypothesis_id, HypothesisStatus.TESTING, reason="立项验证", at=MON(17))
        assert h.status is HypothesisStatus.TESTING
        h = reg.transition(h.hypothesis_id, HypothesisStatus.SUPPORTED, reason="2 条独立支持", at=MON(18))
        assert h.status is HypothesisStatus.SUPPORTED
        h = reg.transition(h.hypothesis_id, HypothesisStatus.ARCHIVED, reason="结论沉淀", at=MON(19))
        assert h.status is HypothesisStatus.ARCHIVED

    def test_legal_path_refuted(self, tmp_path):
        reg = _registry(tmp_path)
        h = reg.create("假设 B", at=MON(16))
        reg.transition(h.hypothesis_id, HypothesisStatus.TESTING, at=MON(17))
        h = reg.transition(h.hypothesis_id, HypothesisStatus.REFUTED, reason="反驳≥2", at=MON(18))
        assert h.status is HypothesisStatus.REFUTED
        h = reg.transition(h.hypothesis_id, HypothesisStatus.ARCHIVED, at=MON(19))
        assert h.status is HypothesisStatus.ARCHIVED

    def test_legal_abort_archive(self, tmp_path):
        """proposed/testing → archived 中止归档为合法路径。"""
        reg = _registry(tmp_path)
        h1 = reg.create("未验证即放弃", at=MON(16))
        h1 = reg.transition(h1.hypothesis_id, HypothesisStatus.ARCHIVED, reason="方向取消", at=MON(17))
        assert h1.status is HypothesisStatus.ARCHIVED
        h2 = reg.create("验证中中止", at=MON(16))
        reg.transition(h2.hypothesis_id, HypothesisStatus.TESTING, at=MON(17))
        h2 = reg.transition(h2.hypothesis_id, HypothesisStatus.ARCHIVED, reason="资源收回", at=MON(18))
        assert h2.status is HypothesisStatus.ARCHIVED

    def test_allowed_transitions_table_terminal(self):
        """迁移表本身：archived 为终态（无任何出边）。"""
        assert ALLOWED_TRANSITIONS[HypothesisStatus.ARCHIVED] == frozenset()
        assert HypothesisStatus.TESTING in ALLOWED_TRANSITIONS[HypothesisStatus.PROPOSED]
        assert ALLOWED_TRANSITIONS[HypothesisStatus.SUPPORTED] == frozenset({HypothesisStatus.ARCHIVED})
        assert ALLOWED_TRANSITIONS[HypothesisStatus.REFUTED] == frozenset({HypothesisStatus.ARCHIVED})

    @pytest.mark.parametrize(
        "path",
        [
            (HypothesisStatus.PROPOSED, HypothesisStatus.SUPPORTED),  # 直飞须过 testing
            (HypothesisStatus.PROPOSED, HypothesisStatus.REFUTED),
            (HypothesisStatus.TESTING, HypothesisStatus.PROPOSED),  # 倒退
            (HypothesisStatus.SUPPORTED, HypothesisStatus.TESTING),  # 翻案重开（Phase 0 不开）
            (HypothesisStatus.REFUTED, HypothesisStatus.TESTING),
            (HypothesisStatus.ARCHIVED, HypothesisStatus.TESTING),  # 归档复活（11号文点名非法）
            (HypothesisStatus.ARCHIVED, HypothesisStatus.PROPOSED),
            (HypothesisStatus.ARCHIVED, HypothesisStatus.SUPPORTED),
        ],
    )
    def test_illegal_transition_rejected(self, tmp_path, path):
        from_status, to_status = path
        reg = _registry(tmp_path)
        h = reg.create("假设", at=MON(16))
        # 把假设推进到 from_status（沿合法路径）
        for nxt in _legal_path_to(from_status):
            h = reg.transition(h.hypothesis_id, nxt, at=MON(17))
        assert h.status is from_status
        with pytest.raises(InvalidTransitionError):
            reg.transition(h.hypothesis_id, to_status, reason="非法迁移", at=MON(18))

    def test_transition_history_traced(self, tmp_path):
        """每次迁移留痕（from/to/at/reason）——可审计。"""
        reg = _registry(tmp_path)
        h = reg.create("假设", at=MON(16))
        reg.transition(h.hypothesis_id, HypothesisStatus.TESTING, reason="r1", at=MON(17))
        h = reg.transition(h.hypothesis_id, HypothesisStatus.SUPPORTED, reason="r2", at=MON(18))
        assert [e["to"] for e in h.status_history] == ["testing", "supported"]
        assert [e["from"] for e in h.status_history] == ["proposed", "testing"]
        assert [e["reason"] for e in h.status_history] == ["r1", "r2"]


def _legal_path_to(status: HypothesisStatus) -> list[HypothesisStatus]:
    """沿合法路径推进到目标状态的迁移序列。"""
    return {
        HypothesisStatus.PROPOSED: [],
        HypothesisStatus.TESTING: [HypothesisStatus.TESTING],
        HypothesisStatus.SUPPORTED: [HypothesisStatus.TESTING, HypothesisStatus.SUPPORTED],
        HypothesisStatus.REFUTED: [HypothesisStatus.TESTING, HypothesisStatus.REFUTED],
        HypothesisStatus.ARCHIVED: [HypothesisStatus.ARCHIVED],
    }[status]


# ============================================================================
# P0-1 假设注册表：CRUD + 持久化
# ============================================================================


class TestHypothesisRegistryCrud:
    def test_create_get_list(self, tmp_path):
        reg = _registry(tmp_path)
        h1 = reg.create("假设 1", tags=["factor", "regime"], at=MON(16))
        h2 = reg.create("假设 2", at=MON(17))
        assert h1.hypothesis_id != h2.hypothesis_id
        assert h1.statement == "假设 1"
        assert h1.tags == ["factor", "regime"]
        assert h1.proposed_at == MON(16).isoformat()
        assert reg.get(h1.hypothesis_id).statement == "假设 1"
        assert len(reg.list_all()) == 2
        reg.transition(h2.hypothesis_id, HypothesisStatus.TESTING, at=MON(18))
        assert [h.hypothesis_id for h in reg.list_all(status=HypothesisStatus.PROPOSED)] == [h1.hypothesis_id]
        assert [h.hypothesis_id for h in reg.list_all(status=HypothesisStatus.TESTING)] == [h2.hypothesis_id]

    def test_get_unknown_raises(self, tmp_path):
        reg = _registry(tmp_path)
        with pytest.raises(HypothesisNotFoundError):
            reg.get("HYP-9999")

    def test_create_empty_statement_rejected(self, tmp_path):
        reg = _registry(tmp_path)
        with pytest.raises(HypothesisRegistryError):
            reg.create("   ", at=MON(16))

    def test_update_metadata(self, tmp_path):
        reg = _registry(tmp_path)
        h = reg.create("原陈述", at=MON(16))
        h = reg.update(h.hypothesis_id, statement="修订陈述", tags=["a"], notes="备注", at=MON(17))
        assert h.statement == "修订陈述"
        assert h.tags == ["a"]
        assert h.notes == "备注"
        assert h.updated_at == MON(17).isoformat()

    def test_update_archived_rejected(self, tmp_path):
        """archived 终态不可变更（保审计）。"""
        reg = _registry(tmp_path)
        h = reg.create("假设", at=MON(16))
        reg.transition(h.hypothesis_id, HypothesisStatus.ARCHIVED, at=MON(17))
        with pytest.raises(HypothesisRegistryError):
            reg.update(h.hypothesis_id, statement="篡改归档", at=MON(18))

    def test_persistence_reload(self, tmp_path):
        """JSON 落盘后新实例重载一致（含状态历史）。"""
        reg = _registry(tmp_path)
        h = reg.create("假设", tags=["x"], at=MON(16))
        reg.transition(h.hypothesis_id, HypothesisStatus.TESTING, reason="r", at=MON(17))
        reg2 = _registry(tmp_path)
        h2 = reg2.get(h.hypothesis_id)
        assert h2.status is HypothesisStatus.TESTING
        assert h2.tags == ["x"]
        assert len(h2.status_history) == 1
        # 重载后 id 序列不重号
        h3 = reg2.create("假设 3", at=MON(18))
        assert h3.hypothesis_id != h.hypothesis_id

    def test_corrupt_store_fail_fast(self, tmp_path):
        """落盘损坏 fail-fast（不静默兜底为空注册表）。"""
        store = tmp_path / "store"
        store.mkdir(parents=True)
        (store / "hypotheses.json").write_text("{broken json", encoding="utf-8")
        with pytest.raises(HypothesisRegistryError):
            HypothesisRegistry(store_dir=store)


# ============================================================================
# P0-2 证据链：三态 + 外键 + hash 固化
# ============================================================================


class TestEvidenceChain:
    def test_append_three_polarities_and_reload(self, tmp_path):
        reg = _registry(tmp_path)
        h = reg.create("假设", at=MON(16))
        chain = _chain(tmp_path, reg)
        e1 = chain.append(h.hypothesis_id, "support", source="backtest-A", content="IC=0.08", at=MON(17))
        e2 = chain.append(h.hypothesis_id, "contradict", source="backtest-B", content="IC=-0.02", at=MON(18))
        e3 = chain.append(h.hypothesis_id, "neutral", source="note", content="样本不足", at=MON(19))
        assert len({e1.evidence_id, e2.evidence_id, e3.evidence_id}) == 3
        assert e1.polarity == "support"
        assert len(e1.content_hash) == 64  # SHA-256 hex

        chain2 = _chain(tmp_path, reg)
        entries = chain2.list_for(h.hypothesis_id)
        assert [e.evidence_id for e in entries] == [e1.evidence_id, e2.evidence_id, e3.evidence_id]
        assert entries[0].content_hash == e1.content_hash

    def test_invalid_polarity_rejected(self, tmp_path):
        """三态词表外取值被拒（11号文 P0-2 验收）。"""
        reg = _registry(tmp_path)
        h = reg.create("假设", at=MON(16))
        chain = _chain(tmp_path, reg)
        with pytest.raises(InvalidPolarityError):
            chain.append(h.hypothesis_id, "maybe", source="s", content="c", at=MON(17))

    def test_foreign_key_enforced(self, tmp_path):
        """hypothesis 不存在拒挂（外键约束）。"""
        reg = _registry(tmp_path)
        chain = _chain(tmp_path, reg)
        with pytest.raises(UnknownHypothesisError):
            chain.append("HYP-9999", "support", source="s", content="c", at=MON(17))

    def test_tamper_detected(self, tmp_path):
        """篡改落盘条目内容（不改 hash）→ 完整性校验失败（11号文 P0-2 验收）。"""
        reg = _registry(tmp_path)
        h = reg.create("假设", at=MON(16))
        chain = _chain(tmp_path, reg)
        chain.append(h.hypothesis_id, "support", source="bt", content="IC=0.08", at=MON(17))
        chain.append(h.hypothesis_id, "contradict", source="bt2", content="IC=-0.01", at=MON(18))

        jsonl = tmp_path / "store" / "evidence_chain.jsonl"
        lines = jsonl.read_text(encoding="utf-8").splitlines()
        tampered = json.loads(lines[0])
        tampered["content"] = "IC=0.99"  # 篡改内容，hash 不动
        lines[0] = json.dumps(tampered, ensure_ascii=False)
        jsonl.write_text("\n".join(lines) + "\n", encoding="utf-8")

        chain2 = _chain(tmp_path, reg)
        with pytest.raises(EvidenceIntegrityError):
            chain2.verify_integrity()

    def test_verify_integrity_clean_store_passes(self, tmp_path):
        reg = _registry(tmp_path)
        h = reg.create("假设", at=MON(16))
        chain = _chain(tmp_path, reg)
        chain.append(h.hypothesis_id, "support", source="bt", content="IC=0.08", at=MON(17))
        chain.verify_integrity()  # 不抛即通过

    def test_summary_aggregation(self, tmp_path):
        reg = _registry(tmp_path)
        h = reg.create("假设", at=MON(16))
        chain = _chain(tmp_path, reg)
        chain.append(h.hypothesis_id, "support", source="a", content="s1", at=MON(17))
        chain.append(h.hypothesis_id, "support", source="b", content="s2", at=MON(18))
        chain.append(h.hypothesis_id, "contradict", source="c", content="c1", at=MON(19))
        chain.append(h.hypothesis_id, "neutral", source="d", content="n1", at=MON(20))
        s = chain.summary_for(h.hypothesis_id)
        assert (s.support_count, s.contradict_count, s.neutral_count, s.total_count) == (2, 1, 1, 4)
        assert s.latest_support_at == MON(18).isoformat()
        assert s.latest_at == MON(20).isoformat()

    def test_corrupt_line_fail_fast(self, tmp_path):
        """jsonl 任一行不可解析 → fail-fast（篡改/损坏不静默跳过）。"""
        reg = _registry(tmp_path)
        h = reg.create("假设", at=MON(16))
        chain = _chain(tmp_path, reg)
        chain.append(h.hypothesis_id, "support", source="a", content="s1", at=MON(17))
        jsonl = tmp_path / "store" / "evidence_chain.jsonl"
        with jsonl.open("a", encoding="utf-8") as fh:
            fh.write("{not json\n")
        from zephyr.research.evidence.evidence_chain import EvidenceChainError

        with pytest.raises(EvidenceChainError):
            _chain(tmp_path, reg)


# ============================================================================
# P0-3 迭代引导器：三态建议 + 可追溯
# ============================================================================


def _summary(support=0, contradict=0, neutral=0, latest_support_at=None, latest_at=None):
    from zephyr.research.evidence.evidence_chain import EvidenceSummary

    return EvidenceSummary(
        hypothesis_id="HYP-T",
        support_count=support,
        contradict_count=contradict,
        neutral_count=neutral,
        total_count=support + contradict + neutral,
        latest_support_at=latest_support_at,
        latest_at=latest_at,
    )


class TestIterationGuide:
    """人工构造证据序列 → 引导输出与规则推演一致（11号文 P0-3 验收）。"""

    def test_abandon_when_contradicted_and_no_recent_support(self):
        guide = IterationGuide(rules=GUIDE_RULES)
        g = guide.evaluate(_summary(contradict=2, latest_at=MON(18).isoformat()), at=MON(19))
        assert g.recommendation is Recommendation.ABANDON
        assert g.rule_id == "R-ABANDON-CONTRADICTED"

    def test_abandon_when_support_stale(self):
        """支持证据存在但已超 4 周 → 仍命中放弃。"""
        guide = IterationGuide(rules=GUIDE_RULES)
        stale = (MON(19) - timedelta(weeks=5)).isoformat()
        g = guide.evaluate(
            _summary(support=1, contradict=2, latest_support_at=stale, latest_at=MON(18).isoformat()),
            at=MON(19),
        )
        assert g.recommendation is Recommendation.ABANDON

    def test_pivot_when_contested_with_recent_support(self):
        """反驳≥2 但近 4 周内有新支持 → 不放弃，落 contested 转向。"""
        guide = IterationGuide(rules=GUIDE_RULES)
        recent = (MON(19) - timedelta(weeks=1)).isoformat()
        g = guide.evaluate(
            _summary(support=1, contradict=2, latest_support_at=recent, latest_at=recent),
            at=MON(19),
        )
        assert g.recommendation is Recommendation.PIVOT
        assert g.rule_id == "R-PIVOT-CONTESTED"

    def test_pivot_when_all_neutral(self):
        guide = IterationGuide(rules=GUIDE_RULES)
        g = guide.evaluate(_summary(neutral=3, latest_at=MON(18).isoformat()), at=MON(19))
        assert g.recommendation is Recommendation.PIVOT
        assert g.rule_id == "R-PIVOT-ALL-NEUTRAL"

    def test_continue_when_supported_clean(self):
        guide = IterationGuide(rules=GUIDE_RULES)
        g = guide.evaluate(
            _summary(support=2, latest_support_at=MON(18).isoformat(), latest_at=MON(18).isoformat()),
            at=MON(19),
        )
        assert g.recommendation is Recommendation.CONTINUE
        assert g.rule_id == "R-CONTINUE-SUPPORTED"

    def test_continue_default_when_no_evidence(self):
        guide = IterationGuide(rules=GUIDE_RULES)
        g = guide.evaluate(_summary(), at=MON(19))
        assert g.recommendation is Recommendation.CONTINUE
        assert g.rule_id == "R-CONTINUE-DEFAULT"

    def test_suggestion_traceable(self):
        """每条建议带命中规则 id + 证据计数 + 规则中文理由（11号文 P0-3 验收）。"""
        guide = IterationGuide(rules=GUIDE_RULES)
        g = guide.evaluate(
            _summary(support=3, neutral=1, latest_support_at=MON(18).isoformat(), latest_at=MON(18).isoformat()),
            at=MON(19),
        )
        assert g.rule_id == "R-CONTINUE-SUPPORTED"
        assert g.evidence_counts == {"support": 3, "contradict": 0, "neutral": 1, "total": 4}
        assert g.rationale_zh
        d = g.to_dict()
        json.dumps(d, ensure_ascii=False)  # JSON 可序列化（落盘契约）

    def test_first_match_wins_order(self):
        """规则按配置顺序首命中生效——顺序敏感的实证。"""
        guide = IterationGuide(rules=GUIDE_RULES)
        # 同时满足 ABANDON(contradict≥2 且无近期支持) 与后续 DEFAULT → 首命中 ABANDON
        g = guide.evaluate(_summary(contradict=5, latest_at=MON(18).isoformat()), at=MON(19))
        assert g.rule_id == "R-ABANDON-CONTRADICTED"

    def test_no_rule_matched_raises(self):
        """无兜底规则且无命中 → 显式报错（不静默给建议）。"""
        guide = IterationGuide(rules=GUIDE_RULES[:1])  # 仅 ABANDON
        from zephyr.research.evidence.iteration_guide import IterationGuideError

        with pytest.raises(IterationGuideError):
            guide.evaluate(_summary(support=1), at=MON(19))

    def test_unknown_condition_key_rejected(self):
        bad = [GuideRule("R-X", Recommendation.CONTINUE, {"unknown_key": 1}, "坏规则")]
        with pytest.raises(IterationGuideConfigError):
            IterationGuide(rules=bad)

    def test_duplicate_rule_id_rejected(self):
        dup = [
            GuideRule("R-D", Recommendation.CONTINUE, {}, "a"),
            GuideRule("R-D", Recommendation.PIVOT, {}, "b"),
        ]
        with pytest.raises(IterationGuideConfigError):
            IterationGuide(rules=dup)

    def test_bad_recommendation_rejected(self):
        bad = [GuideRule("R-X", "hold", {}, "词表外建议")]  # type: ignore[arg-type]
        with pytest.raises(IterationGuideConfigError):
            IterationGuide(rules=bad)

    def test_default_config_loads(self):
        """规则表 config 化：仓内 config/iteration_guide_rules.yaml 可加载且校验通过。"""
        rules = load_rules()
        assert rules, "默认规则表为空"
        assert len({r.rule_id for r in rules}) == len(rules)
        assert all(isinstance(r.recommendation, Recommendation) for r in rules)
        # 默认规则表必须含兜底（空条件）规则，保证任意证据聚合都有建议输出
        assert any(not r.conditions for r in rules)

    def test_load_rules_rejects_bad_config(self, tmp_path):
        bad_yaml = tmp_path / "bad_rules.yaml"
        bad_yaml.write_text(
            "rules:\n  - rule_id: R-BAD\n    recommendation: continue\n"
            "    conditions: {bogus_key: 1}\n    rationale_zh: 坏\n",
            encoding="utf-8",
        )
        with pytest.raises(IterationGuideConfigError):
            load_rules(bad_yaml)


# ============================================================================
# P0-4 批量入口：全量评估落盘 + 盘中拒执行
# ============================================================================


class TestIntradayGuard:
    """盘中零调用守卫（18号工单：09:30-15:00 时段拒绝执行）。"""

    @pytest.mark.parametrize(
        "at,expected",
        [
            (MON(9, 29), False),
            (MON(9, 30), True),  # 开盘边界（含）
            (MON(10, 0), True),
            (MON(11, 30), True),  # 午间休市仍从严拒绝（09:30-15:00 全窗口）
            (MON(14, 59), True),
            (MON(15, 0), False),  # 收盘边界（不含）
            (MON(20, 0), False),
            (SAT(10, 0), False),  # 周末非盘中
        ],
    )
    def test_is_intraday_window(self, at, expected):
        assert is_intraday(at) is expected

    def test_run_batch_rejected_intraday(self, tmp_path):
        with pytest.raises(IntradayExecutionForbiddenError):
            run_batch(frequency="daily", store_dir=tmp_path / "store", at=MON(10, 0))

    def test_main_returns_3_intraday(self, tmp_path, capsys):
        rc = main(["--frequency", "daily", "--store-dir", str(tmp_path / "store")], at=MON(10, 0))
        assert rc == 3


class TestBatchRun:
    def _seed(self, tmp_path):
        reg = HypothesisRegistry(store_dir=tmp_path / "store")
        chain = EvidenceChain(store_dir=tmp_path / "store", registry=reg)
        h_ok = reg.create("有支持假设", at=MON(16))
        reg.transition(h_ok.hypothesis_id, HypothesisStatus.TESTING, at=MON(16, 30))
        chain.append(h_ok.hypothesis_id, "support", source="a", content="s1", at=MON(17))
        chain.append(h_ok.hypothesis_id, "support", source="b", content="s2", at=MON(18))
        h_bad = reg.create("被反驳假设", at=MON(16))
        reg.transition(h_bad.hypothesis_id, HypothesisStatus.TESTING, at=MON(16, 30))
        chain.append(h_bad.hypothesis_id, "contradict", source="c", content="c1", at=MON(17))
        chain.append(h_bad.hypothesis_id, "contradict", source="d", content="c2", at=MON(18))
        h_done = reg.create("已归档假设", at=MON(16))
        reg.transition(h_done.hypothesis_id, HypothesisStatus.ARCHIVED, at=MON(17))
        return reg, chain, (h_ok, h_bad, h_done)

    def test_run_batch_writes_guidance(self, tmp_path):
        """全量（未归档）假设批量评估 → 建议清单落盘（11号文 P0-4 验收）。"""
        self._seed(tmp_path)
        report = run_batch(frequency="daily", store_dir=tmp_path / "store", at=MON(16, 0))
        assert report.evaluated_count == 2  # archived 不评估
        out = Path(report.output_path)
        assert out.exists()
        payload = json.loads(out.read_text(encoding="utf-8"))
        assert payload["frequency"] == "daily"
        assert payload["evaluated_count"] == 2
        assert payload["skipped_archived_count"] == 1
        by_hyp = {i["hypothesis_id"]: i for i in payload["items"]}
        assert len(by_hyp) == 2
        for item in payload["items"]:
            assert item["rule_id"]
            assert set(item["evidence_counts"]) == {"support", "contradict", "neutral", "total"}
            assert item["recommendation"] in {"continue", "pivot", "abandon"}

    def test_run_batch_weekly_frequency(self, tmp_path):
        self._seed(tmp_path)
        report = run_batch(frequency="weekly", store_dir=tmp_path / "store", at=MON(16, 0))
        payload = json.loads(Path(report.output_path).read_text(encoding="utf-8"))
        assert payload["frequency"] == "weekly"
        assert "weekly" in Path(report.output_path).name

    def test_invalid_frequency_rejected(self, tmp_path):
        with pytest.raises(ValueError):
            run_batch(frequency="hourly", store_dir=tmp_path / "store", at=MON(16, 0))

    def test_run_batch_empty_store(self, tmp_path):
        """空注册表批量跑 → 空清单落盘不抛。"""
        report = run_batch(frequency="daily", store_dir=tmp_path / "store", at=MON(16, 0))
        assert report.evaluated_count == 0
        payload = json.loads(Path(report.output_path).read_text(encoding="utf-8"))
        assert payload["items"] == []

    def test_main_cli_success(self, tmp_path):
        self._seed(tmp_path)
        rc = main(
            ["--frequency", "daily", "--store-dir", str(tmp_path / "store"), "--output-dir", str(tmp_path / "out")],
            at=MON(16, 0),
        )
        assert rc == 0
        outputs = list((tmp_path / "out").glob("guidance_*.json"))
        assert len(outputs) == 1
