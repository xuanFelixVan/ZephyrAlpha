"""news_llm_scorer 单元测试（factory-off 契约+构造注入，零真实 LLM 调用）。"""

from __future__ import annotations

import zephyr.intelligence.news_llm_scorer as nls


class FakeBackend:
    def ask(self, prompt: str, *, system: str = "", temperature: float | None = None) -> str:
        return '{"sentiment": "positive", "score": 0.8, "scope": "market"}'


def test_flag_absent_returns_none(tmp_path):
    """出厂默认（旗标不存在）→ None = 规则法零变更。"""
    assert nls.make_llm_scorer(flag_path=tmp_path / "absent.flag") is None


def test_flag_present_builds_callable(tmp_path, monkeypatch):
    """旗标开启 → 返回可调用；注入 fake backend，验证走 infer_sentiment 解析出 polarity>0。"""
    flag = tmp_path / "nightly_sentiment_llm.enabled"
    flag.write_text("", encoding="utf-8")
    scorer = nls.make_llm_scorer(flag_path=flag, backend=FakeBackend())
    assert callable(scorer)
    result = scorer("重大利好：公司中标大额合同", "")
    assert getattr(result, "polarity", 0.0) > 0
    assert result.sentiment == "positive"


def test_construction_failure_degrades_to_none(tmp_path, monkeypatch):
    """构造异常（后端构造炸）→ 降级返回 None，不抛不阻断夜间批。"""
    flag = tmp_path / "nightly_sentiment_llm.enabled"
    flag.write_text("", encoding="utf-8")

    class Boom:
        def __init__(self):
            raise RuntimeError("boom")

    import zephyr.integration.local_model.ollama_chat as oc

    monkeypatch.setattr(oc, "OllamaChat", Boom, raising=False)
    scorer = nls.make_llm_scorer(flag_path=flag, backend=None)
    assert scorer is None
