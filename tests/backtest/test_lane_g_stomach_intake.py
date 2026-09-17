# [BLUEPRINT] MOD-AUTO-E1G-001 | docs/_working/automation/campaign/blueprints/lane_g_stomach_intake_blueprint.md | §tests
# [PROVISIONAL] 暂编号：docs/03_modules 解冻后按注册表重编（挂单 H-01）
# [MODULE] tests.backtest.test_lane_g_stomach_intake
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.lane_g_stomach_intake
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 零网络零 LLM 零生产路径写入（全部落 tmp_path）；假 chat 注入=唯一喂料面
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=AssertionError（pytest 收集）
# [TESTS] 本文件
# [A_module] module_id=MOD-AUTO-E1G-001 | layer=test | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""车道G-全网搜索进货（MOD-AUTO-E1G-001）单测：解析/去重/出生证/seen 自愈/接线钉。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.backtest import lane_g_stomach_intake as lane_g  # noqa: E402

SAMPLE_INBOX = """# 情报收件箱 2026-09-16T21:52:26Z

## 1. Statistical Inference for Score Decompositions

- 链接: https://arxiv.org/abs/2603.04275  |  日期: Wed, 16 Sep 2026 00:00:0  |  命中词: `forecast`
- 摘要: 评分分解的统计推断方法，可评估模型偏差与区分能力。

## 2. Diffusion models for volatility surface

- 链接: https://arxiv.org/abs/2609.13402  |  日期: Wed, 16 Sep 2026 00:00:0  |  命中词: `volatil`、`hedg`
- 摘要: 动态波动率曲面生成与数据驱动对冲。

## 3. 无链接块

- 摘要: 畸形块应被跳过
"""


class FakeChat:
    """按 prompt 关键字回包的假 LLM（零网络零 LSG 实调）。"""

    def __init__(self, replies: dict[str, str], default: str = "[]"):
        self.replies = replies
        self.default = default
        self.prompts: list[str] = []

    def ask(self, prompt, *, system="", temperature=None, max_tokens=None):
        self.prompts.append(prompt)
        for kw, rep in self.replies.items():
            if kw in prompt:
                return rep
        return self.default


def _idea(text: str) -> str:
    return json.dumps([{
        "hypothesis_zh": text, "mechanism_hint": "机制", "horizon": "5日", "universe": "沪深300",
    }], ensure_ascii=False)


@pytest.fixture()
def sandbox(tmp_path, monkeypatch):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "intel-20260916.md").write_text(SAMPLE_INBOX, encoding="utf-8")
    monkeypatch.setattr(lane_g, "_INBOX_DIR", inbox)
    monkeypatch.setattr(lane_g, "_INTAKE_CSV", tmp_path / "lane_g_candidates.csv")
    monkeypatch.setattr(lane_g, "_SEEN_CSV", tmp_path / "lane_g_seen_urls.csv")
    return tmp_path


def test_parse_inbox_entries_fields():
    entries = lane_g.parse_inbox_entries(SAMPLE_INBOX)
    assert len(entries) == 2  # 无链接畸形块跳过
    e0, e1 = entries
    assert e0["url"] == "https://arxiv.org/abs/2603.04275"
    assert e0["keywords"] == ["forecast"]
    assert "统计推断" in e0["summary"]
    assert e1["keywords"] == ["volatil", "hedg"]


def test_candidate_id_content_addressed_and_domain_scoped():
    cid = lane_g.make_candidate_id("同一假说")
    assert cid == lane_g.make_candidate_id(" 同一假说 ")
    assert cid.startswith("CAND-")
    from scripts.backtest.lane_b_idea_generator import make_candidate_id as b_id
    assert cid != b_id("同一假说")  # E1G/E1B 域前缀隔离，同文不串台账


def test_run_intake_writes_birth_certificate(sandbox):
    chat = FakeChat({"Score Decompositions": _idea("评分分解动量假说")})
    rec = lane_g.run_intake(chat=chat)
    assert rec["generated"] == 1
    assert rec["processed_entries"] == 2
    import pandas as pd
    df = pd.read_csv(lane_g._INTAKE_CSV, encoding="utf-8-sig")
    row = df.iloc[0]
    assert row["birth_channel"] == "G"
    assert str(row["birth_batch"]).startswith("E1G-")
    assert "arxiv.org/abs/2603.04275" in row["birth_source"]
    seen = pd.read_csv(lane_g._SEEN_CSV, encoding="utf-8-sig")
    assert sorted(seen["n_candidates"].tolist()) == [0, 1]  # 空数组条目也记账、计数按条


def test_seen_log_blocks_reprocessing(sandbox):
    chat = FakeChat({"": _idea("复用假说")}, default=_idea("复用假说"))
    lane_g.run_intake(chat=chat)
    first_calls = len(chat.prompts)
    rec2 = lane_g.run_intake(chat=FakeChat({}, default="[]"))
    assert rec2["processed_entries"] == 0
    assert len(chat.prompts) == first_calls  # 已消化 url 不再提问


def test_llm_failure_not_marked_seen_retries_next_shift(sandbox):
    class Boom:
        def __init__(self):
            self.calls = 0

        def ask(self, prompt, **kw):
            self.calls += 1
            if "Score Decompositions" in prompt:
                raise RuntimeError("LSG 不可达")
            return "[]"

    boom = Boom()
    rec = lane_g.run_intake(chat=boom)
    assert rec["failed_urls"] == ["https://arxiv.org/abs/2603.04275"]
    rec2 = lane_g.run_intake(chat=FakeChat({"Score Decompositions": _idea("补挖假说")}))
    assert rec2["processed_entries"] == 1  # 失败条目下一班自愈
    assert rec2["generated"] == 1


def test_truncated_reply_without_json_treated_as_failure(sandbox):
    class Half:
        def ask(self, prompt, **kw):
            return "抱歉我需要更多上下文"

    rec = lane_g.run_intake(chat=Half(), dry_run=True)
    assert len(rec["failed_urls"]) == 2  # 全部按失败处理，不误标 seen


def test_dry_run_writes_nothing(sandbox):
    chat = FakeChat({"Score Decompositions": _idea("假说甲"),
                     "volatility surface": _idea("假说乙")})
    rec = lane_g.run_intake(chat=chat, dry_run=True)
    assert rec["generated"] == 2
    assert not lane_g._INTAKE_CSV.exists()
    assert not lane_g._SEEN_CSV.exists()


def test_limit_caps_entries_per_shift(sandbox):
    rec = lane_g.run_intake(limit=1, chat=FakeChat({}, default="[]"))
    assert rec["processed_entries"] == 1


def test_pipeline_lane_spec_registered():
    from scripts.backtest.factory_intake_pipeline import _LANE_SPECS
    spec = next(s for s in _LANE_SPECS if s["lane"] == "G")
    assert spec["compute_class"] == "local"
    assert "lane_g_candidates.csv" in spec["intake"]


def test_factory_map_has_lane_g_node():
    import yaml
    text = (_ROOT / "config" / "strategy_production_map.yaml").read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    node = next(n for n in data["nodes"] if n["node_id"] == "FAC-E1G")
    assert node["lane"] == "G"
    assert node["stage"] == "E1"
    assert node["node_type"] == "lane"
    assert node["build_status"] in {"built", "partial"}
