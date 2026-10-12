# [BLUEPRINT] MOD-BT-150 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_lane_b_idea_generator
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest
# [CONSUMERS] MOD-BT-150 lane_b_idea_generator 循环验收（tests 同批）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 纯函数测试零 IO 零 LLM（tmp_path 外禁写；不触生产 intake 路径）；
#   卸货写盘段以 OllamaChat 替身+CAS 写口 spy 验收（F16 治本回归面）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-150 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FAC-E1B 车道B 单测——生成 prompt/假说解析/内容寻址 id/出生证/台账 CAS 卸货，零网络。"""

from __future__ import annotations

import json

import pandas as pd
import pytest

from scripts.backtest.lane_b_idea_generator import (
    SEED_THEMES,
    attach_birth_certificate,
    build_generation_prompt,
    make_candidate_id,
    parse_ideas,
)


class TestSeedThemes:
    def test_twelve_distinct_themes(self):
        assert len(SEED_THEMES) == 12
        assert len(set(SEED_THEMES)) == 12


class TestGenerationPrompt:
    def test_deterministic_with_theme_and_n(self):
        p1, p2 = build_generation_prompt("动量", 3), build_generation_prompt("动量", 3)
        assert p1 == p2
        assert "动量" in p1 and "3" in p1

    def test_guardrails_present(self):
        p = build_generation_prompt("反转", 1)
        for token in ("交易对手", "T 日收盘", "不涉及做空"):
            assert token in p


class TestParseIdeas:
    def _idea(self, h: str = "低波动股票长期跑赢") -> dict:
        return {"hypothesis_zh": h, "mechanism_hint": "风险溢价", "horizon": "20日", "universe": "沪深300"}

    def test_clean_array(self):
        raw = json.dumps([self._idea(), self._idea("放量突破买入")])
        out = parse_ideas(raw)
        assert len(out) == 2 and out[0]["hypothesis_zh"] == "低波动股票长期跑赢"

    def test_array_wrapped_in_noise(self):
        raw = f"好的，生成如下：\n{json.dumps([self._idea()])}\n请查收。"
        assert len(parse_ideas(raw)) == 1

    def test_object_extraction_fallback(self):
        raw = "前言 " + json.dumps(self._idea()) + " 中间 " + json.dumps(self._idea("另一条")) + " 结尾"
        assert len(parse_ideas(raw)) == 2

    def test_items_without_hypothesis_dropped(self):
        raw = json.dumps([{"mechanism_hint": "无假说字段"}, self._idea()])
        assert len(parse_ideas(raw)) == 1

    def test_garbage_returns_empty(self):
        assert parse_ideas("这个主题我想不出什么") == []
        assert parse_ideas("") == []
        assert parse_ideas(None) == []

    def test_deterministic(self):
        raw = json.dumps([self._idea()])
        assert parse_ideas(raw) == parse_ideas(raw)


class TestCandidateId:
    def test_content_addressed_stable(self):
        assert make_candidate_id("假说A") == make_candidate_id("假说A")
        assert make_candidate_id("假说A") != make_candidate_id("假说B")
        assert make_candidate_id("假说A ").startswith("CAND-")  # 空白已 strip 归一

    def test_md5_12_format(self):
        cid = make_candidate_id("x")
        assert len(cid) == len("CAND-") + 12


class TestBirthCertificate:
    def test_machine_written_and_stable_prompt_fp(self):
        ideas = [{"hypothesis_zh": "a"}, {"hypothesis_zh": "b"}]
        out = attach_birth_certificate(ideas, "E1B-20260914-000000", "动量", "PROMPT")
        assert all(x["birth_channel"] == "B" for x in out)
        assert all(x["birth_batch"] == "E1B-20260914-000000" for x in out)
        assert out[0]["birth_source"] == out[1]["birth_source"]
        assert "llm:" in out[0]["birth_source"] and "prompt_md5=" in out[0]["birth_source"]

    def test_no_mutation_of_input(self):
        ideas = [{"hypothesis_zh": "a"}]
        attach_birth_certificate(ideas, "E1B-x", "动量", "P")
        assert "birth_channel" not in ideas[0]


class _FakeChat:
    """OllamaChat 替身：固定回复同一批假说（零网络零 LSG 调用）。"""

    def __init__(self, model=None, **kwargs):
        self.model = model

    def ask(self, prompt, **kwargs):
        return json.dumps(_IDEAS)


_IDEAS = [
    {
        "hypothesis_zh": "低波动股票长期跑赢高波动股票",
        "mechanism_hint": "风险溢价",
        "horizon": "20日",
        "universe": "沪深300",
    },
    {"hypothesis_zh": "放量突破前高的股票次日续涨", "mechanism_hint": "行为偏差", "horizon": "5日", "universe": "全A"},
]


class TestLedgerAppendGoesThroughCasF16:
    """F16 治本第三刀：卸货写盘必经 CAS 通道，且既有行只追加不覆盖。"""

    def _prep(self, tmp_path, monkeypatch):
        import zephyr.integration.local_model.ollama_chat as oc
        from scripts.backtest import lane_b_idea_generator as lb

        ledger = tmp_path / "lane_b_candidates.csv"
        monkeypatch.setattr(lb, "_INTAKE_CSV", ledger)
        monkeypatch.setattr(oc, "OllamaChat", _FakeChat)
        return lb, ledger

    def test_append_uses_recon_cas_channel(self, tmp_path, monkeypatch):
        lb, ledger = self._prep(tmp_path, monkeypatch)
        from scripts.backtest import intake_ledger_recon as recon

        calls = []
        real = recon.append_ledger_rows

        def spy(path, rows, header):
            calls.append((str(path), len(rows), list(header)))
            return real(path, rows, header)

        monkeypatch.setattr(recon, "append_ledger_rows", spy)
        record = lb.run_generation(["波动率变化"], 1, dry_run=False)
        assert calls, '绕过 CAS 写口=裸 mode="a" 回归（F16 蒸发写手侧根因）'
        assert calls[0][1] == record["generated"] == 2
        assert record["cas"]["rows"] == 2
        assert ledger.exists()

    def test_second_batch_appends_without_touching_old_rows(self, tmp_path, monkeypatch):
        lb, ledger = self._prep(tmp_path, monkeypatch)
        lb.run_generation(["波动率变化"], 1, dry_run=False)
        before = ledger.read_text(encoding="utf-8")
        _IDEAS.append(
            {"hypothesis_zh": "第三条新假说", "mechanism_hint": "h", "horizon": "10日", "universe": "中证500"}
        )
        try:
            lb.run_generation(["相对强弱"], 1, dry_run=False)
        finally:
            _IDEAS.pop()
        after = ledger.read_text(encoding="utf-8")
        assert after.startswith(before)
        assert len(pd.read_csv(ledger, encoding="utf-8-sig")) == 3

    def test_same_hypothesis_across_batches_not_double_booked(self, tmp_path, monkeypatch):
        lb, ledger = self._prep(tmp_path, monkeypatch)
        first = lb.run_generation(["动量"], 1, dry_run=False)
        second = lb.run_generation(["反转"], 1, dry_run=False)
        assert first["generated"] == 2 and second["generated"] == 0
        assert second["skipped_dup"] == 2
        assert len(ledger.read_text(encoding="utf-8").splitlines()) == 3  # 表头+2 行

    def test_dry_run_writes_nothing(self, tmp_path, monkeypatch):
        lb, ledger = self._prep(tmp_path, monkeypatch)
        record = lb.run_generation(["动量"], 1, dry_run=True)
        assert record["generated"] == 2 and not ledger.exists()


class TestModelTierPlumbing:
    """工单 GPU-01 档位 A/B：模型档必须与出生证同源，缺省行为零变更。"""

    def _run(self, tmp_path, monkeypatch, model=None):
        import json

        import zephyr.integration.local_model.ollama_chat as oc
        from scripts.backtest import lane_b_idea_generator as lb

        seen = {}

        class _SpyChat:
            def __init__(self, model=None, **kwargs):
                seen["model"] = model

            def ask(self, prompt, **kwargs):
                return json.dumps(_IDEAS)

        ledger = tmp_path / "lane_b_candidates.csv"
        monkeypatch.setattr(lb, "_INTAKE_CSV", ledger)
        monkeypatch.setattr(oc, "OllamaChat", _SpyChat)
        kwargs = {} if model is None else {"model": model}
        record = lb.run_generation(["动量"], 1, True, **kwargs)
        return record, seen

    def test_explicit_tier_reaches_chat_and_birth_source(self, tmp_path, monkeypatch):
        record, seen = self._run(tmp_path, monkeypatch, model="qwen3:14b")
        assert seen["model"] == "qwen3:14b", "档位没传到 OllamaChat＝A/B 三档其实跑的是同一档"
        assert record["model"] == "qwen3:14b"
        srcs = {i["candidate_id"] for i in record["items"]}
        assert len(srcs) == record["generated"]
        # dry_run 不落台账，但出生证已在 rows 上生成：直接查 attach 侧
        from scripts.backtest.lane_b_idea_generator import attach_birth_certificate

        certified = attach_birth_certificate([{"hypothesis_zh": "x"}], "E1B-t", "动量", "P", model="qwen3:14b")
        assert "llm:qwen3:14b" in certified[0]["birth_source"]

    def test_default_keeps_legacy_constant(self, tmp_path, monkeypatch):
        from scripts.backtest import lane_b_idea_generator as lb

        record, seen = self._run(tmp_path, monkeypatch, model=None)
        assert seen["model"] == lb.MODEL, "缺省必须仍是 MODEL 常量（现产线行为零变更）"
        assert record["model"] == lb.MODEL

    def test_cli_flag_exists_on_generate_subparser(self):
        import subprocess
        import sys

        rc = subprocess.run(
            [sys.executable, "scripts/backtest/lane_b_idea_generator.py", "generate", "--help"],
            capture_output=True,
            text=True,
            cwd=str(lb_root()),
        )
        assert "--model" in rc.stdout, "CLI 没挂 --model 旗＝夜窗批无法换档"


def lb_root():
    from pathlib import Path

    return Path(__file__).resolve().parents[3]


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-v"])
