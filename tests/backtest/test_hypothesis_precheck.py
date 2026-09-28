# [BLUEPRINT] MOD-BT-091 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_hypothesis_precheck
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest
# [CONSUMERS] MOD-BT-091 hypothesis_precheck 循环验收（tests 同批）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 纯函数测试零 IO 零 LLM 零真连（禁触生产数据路径与网络；CH 一律以迷你替身
#   注入，其 WHERE verdict 过滤做真实求值⇒幂等口径缺陷可直接测红）；
#   解析器对格式漂移的映射表穷举
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-091 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FAC-E2 假说预审单测——prompt 确定性/回复强解析/理由码闭合/幂等集口径/台账前置对账，零真连。"""

from __future__ import annotations

import json
import re

import pandas as pd
import pytest

from scripts.backtest.hypothesis_precheck import (
    DEFER_REASONS,
    LOW_CONFIDENCE,
    REASON_PASS,
    REJECT_REASONS,
    SQL_ALREADY,
    VERDICT_DEFER,
    VERDICT_PASS,
    VERDICT_REJECT,
    build_prompt,
    fetch_prechecked_ids,
    ledger_preflight,
    parse_reply,
)


class _MiniCH:
    """极简 CH 替身：对 SQL_ALREADY 文本里的 verdict 排除条件做真实求值（不写死返回集）。

    表语义=c1_backtest.hypothesis_precheck（行=候选 id+verdict）；DISTINCT 按 candidate_id
    保序去重。旧 SQL（全表 DISTINCT、无 WHERE）会把 deferred 一并判为"已审"⇒测红。
    """

    def __init__(self, rows: list[tuple[str, str]]):
        self.rows = list(rows)
        self.seen_sql = ""

    def execute(self, sql, params=None):  # noqa: ANN001 — 替身签名对齐 clickhouse-driver
        self.seen_sql = sql
        m = re.search(r"WHERE\s+verdict\s*!=\s*'([^']+)'", sql)
        picked = [r for r in self.rows if m is None or r[1] != m.group(1)]
        if "DISTINCT" in sql.upper():
            picked = list(dict.fromkeys(picked))
        return [(cid,) for cid, _verdict in picked]


class TestPrompt:
    def test_deterministic_and_contains_hypothesis(self):
        h = "做多黄金环节——三高共振"
        p1, p2 = build_prompt(h, "D"), build_prompt(h, "D")
        assert p1 == p2
        assert h in p1
        assert "D" in p1

    def test_six_questions_present(self):
        p = build_prompt("x")
        for token in ("机制", "前视", "成本", "可证伪", "同义反复", "边界"):
            assert token in p

    def test_reason_code_vocabulary_in_prompt(self):
        p = build_prompt("x")
        for rc in (REASON_PASS, *REJECT_REASONS, "defer_low_confidence"):
            assert rc in p, rc


class TestReasonCodeSystem:
    def test_vocabulary_disjoint_and_closed(self):
        assert REASON_PASS not in REJECT_REASONS
        assert not (set(REJECT_REASONS) & set(DEFER_REASONS))
        assert len(REJECT_REASONS) == 6 and len(DEFER_REASONS) == 3

    def test_low_confidence_threshold(self):
        assert 0 < LOW_CONFIDENCE < 1


class TestParseReply:
    def test_clean_json_pass(self):
        raw = json.dumps(
            {"verdict": "pass", "reason_code": REASON_PASS, "confidence": 0.8, "rationale": "风险溢价机制成立"}
        )
        v = parse_reply(raw)
        assert v["verdict"] == VERDICT_PASS and v["reason_code"] == REASON_PASS
        assert v["confidence"] == 0.8

    def test_clean_json_reject(self):
        raw = json.dumps(
            {"verdict": "reject", "reason_code": "reject_lookahead", "confidence": 0.9, "rationale": "用到未来数据"}
        )
        v = parse_reply(raw)
        assert v["verdict"] == VERDICT_REJECT and v["reason_code"] == "reject_lookahead"

    def test_json_wrapped_in_noise(self):
        raw = f"模型思考中……{json.dumps({'verdict': 'pass', 'reason_code': REASON_PASS, 'confidence': 0.7, 'rationale': 'ok'})}以上。"
        assert parse_reply(raw)["verdict"] == VERDICT_PASS

    def test_keyword_fallback_pass(self):
        v = parse_reply("我判断该假说 pass，机制是风险溢价")
        assert v["verdict"] == VERDICT_PASS and v["reason_code"] == REASON_PASS

    def test_keyword_fallback_reject_reason_code(self):
        v = parse_reply("该想法 reject：reject_cost_prohibitive 成本太高")
        assert v["verdict"] == VERDICT_REJECT and v["reason_code"] == "reject_cost_prohibitive"

    def test_garbage_becomes_defer_parse_fail(self):
        v = parse_reply("嗯……这个想法大概也许可能行吧")
        assert v["verdict"] == VERDICT_DEFER and v["reason_code"] == "defer_parse_fail"

    def test_empty_and_none_become_defer(self):
        for bad in ("", None):
            v = parse_reply(bad)
            assert v["verdict"] == VERDICT_DEFER

    def test_reject_with_unknown_reason_maps_to_defer_low_confidence(self):
        raw = json.dumps(
            {"verdict": "reject", "reason_code": "reject_我不认识", "confidence": 0.9, "rationale": "怪理由"}
        )
        v = parse_reply(raw)
        assert v["verdict"] == VERDICT_DEFER and v["reason_code"] == "defer_low_confidence"

    def test_defer_roundtrip(self):
        raw = json.dumps(
            {"verdict": "defer", "reason_code": "defer_low_confidence", "confidence": 0.3, "rationale": "说不准"}
        )
        v = parse_reply(raw)
        assert v["verdict"] == VERDICT_DEFER and v["confidence"] == 0.3

    def test_non_numeric_confidence_tolerated(self):
        raw = json.dumps({"verdict": "pass", "reason_code": REASON_PASS, "confidence": "高", "rationale": "x"})
        assert parse_reply(raw)["confidence"] is None

    def test_deterministic(self):
        raw = (
            '{"verdict": "reject", "reason_code": "reject_tautology", "confidence": 0.75, "rationale": "动量同义反复"}'
        )
        assert parse_reply(raw) == parse_reply(raw)


class TestIdempotencyScopeF21:
    """F21 治本：幂等集只认终局结论（passed/rejected），deferred 必须留在重审通道。

    旧 SQL 是 `SELECT DISTINCT candidate_id FROM {table}`——全表 DISTINCT 把 24 条
    defer_llm_unreachable 之类基础设施失败一并算作"已审"，Ollama 恢复后永不再审。
    """

    TABLE = [
        ("CAND-pass", VERDICT_PASS),
        ("CAND-rej", VERDICT_REJECT),
        ("CAND-defer", VERDICT_DEFER),
    ]

    def test_sql_declares_deferred_exclusion(self):
        assert "WHERE" in SQL_ALREADY and VERDICT_DEFER in SQL_ALREADY

    def test_deferred_candidate_is_not_skipped(self, monkeypatch):
        import zephyr.data.ch_writer as chw

        fake = _MiniCH(self.TABLE)
        monkeypatch.setattr(chw, "get_client_strict", lambda: fake)
        done = fetch_prechecked_ids()
        assert "CAND-defer" not in done, "deferred 被占坑=滞留死锁（F21 原缺陷）"
        assert done == {"CAND-pass", "CAND-rej"}

    def test_terminal_verdicts_still_skipped(self, monkeypatch):
        """修完不得反向漏审：终局结论仍进跳过集（否则同想法反复烧算力）。"""
        import zephyr.data.ch_writer as chw

        monkeypatch.setattr(chw, "get_client_strict", lambda: _MiniCH(self.TABLE))
        done = fetch_prechecked_ids()
        assert {"CAND-pass", "CAND-rej"} <= done

    def test_ch_outage_degrades_to_full_recheck(self, monkeypatch):
        import zephyr.data.ch_writer as chw

        def boom():
            raise RuntimeError("connection refused")

        monkeypatch.setattr(chw, "get_client_strict", boom)
        assert fetch_prechecked_ids() == set()


class TestLedgerPreflightF16:
    """F16 接线：E2 前置台账对账必须出声，且永不把异常抛进预审主链。"""

    def test_evaporated_ledger_reported_as_drift(self, tmp_path, monkeypatch):
        from scripts.backtest import intake_ledger_recon as recon
        from scripts.backtest.lane_b_idea_generator import make_candidate_id

        rows = [
            {
                "candidate_id": make_candidate_id("甲"),
                "hypothesis_zh": "甲",
                "birth_channel": "B",
                "birth_batch": "E1B-1",
            }
        ]
        pd.DataFrame(rows).to_csv(tmp_path / "lane_b_candidates.csv", index=False, lineterminator="\n")
        monkeypatch.setattr(recon, "_INTAKE_DIR", tmp_path)
        monkeypatch.setattr(
            recon,
            "fetch_ch_index",
            lambda channels=None: [
                {
                    "candidate_id": make_candidate_id("甲"),
                    "birth_channel": "B",
                    "birth_batch": "E1B-1",
                    "hypothesis_zh": "甲",
                },
                {
                    "candidate_id": make_candidate_id("乙"),
                    "birth_channel": "B",
                    "birth_batch": "E1B-2",
                    "hypothesis_zh": "乙",
                },
            ],
        )
        out = ledger_preflight("lane_b_candidates.csv")
        assert out["status"] == recon.STATUS_DRIFT
        assert out["missing_in_csv"] == 1

    def test_probe_failure_is_explicit_and_never_raises(self, tmp_path, monkeypatch):
        from scripts.backtest import intake_ledger_recon as recon

        pd.DataFrame(
            [{"candidate_id": "CAND-x", "hypothesis_zh": "x", "birth_channel": "B", "birth_batch": "E1B-1"}]
        ).to_csv(tmp_path / "lane_b_candidates.csv", index=False, lineterminator="\n")
        monkeypatch.setattr(recon, "_INTAKE_DIR", tmp_path)

        def boom(channels=None):
            raise RuntimeError("clickhouse unreachable")

        monkeypatch.setattr(recon, "fetch_ch_index", boom)
        out = ledger_preflight("lane_b_candidates.csv")
        assert out["status"] == "probe_failed"
        assert "clickhouse unreachable" in out["error"]

    def test_unknown_source_is_skipped_without_ch_call(self, monkeypatch):
        calls = []
        from scripts.backtest import intake_ledger_recon as recon

        monkeypatch.setattr(recon, "fetch_ch_index", lambda channels=None: calls.append(1) or [])
        out = ledger_preflight("some_random_file.csv")
        assert out["status"] == "unknown_ledger"
        assert calls == []


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-v"])
