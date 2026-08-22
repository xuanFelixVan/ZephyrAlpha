"""
test_llm_runtime_gateway.py — llm_runtime_gateway MVP 单测（10号文 §4 + 18号清单 §5 E1，2026-08-22）
=====================================================================================================
全 mock 通道（不真调 API；真跑在波5 由统筹执行）。覆盖：
- 三通道优先级链：DeepSeek 成功 / Qwen 备用降级 / Ollama 兜底 / 全失败 status=error / 显式 channel 钉死
- 登记落库三态断言：ok / error（降级留痕，每尝试一行）/ blocked（LSG 判决不发起调用）
- 成本计算：谷时（北京 18:00-次日 9:00）/峰时判定与价差、qwen/ollama 零价、未知模型通道兜底
- reconcile_daily_calls 日终对账汇总（by_status/by_provider/重算 delta/防超额判定/非法日期 fail-closed）
- LSG：入口判决 BLOCK -> 不发起任何通道调用 + status=blocked 落库；LSG 异常 -> fail-closed 同径
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest

gw_mod = pytest.importorskip("zephyr.integration.llm_runtime_gateway")
secrets_mod = pytest.importorskip("zephyr.shared.security.secrets")

InferResult = gw_mod.InferResult
LLMRuntimeGateway = gw_mod.LLMRuntimeGateway
QwenChat = gw_mod.QwenChat
LSGBlockedError = gw_mod.LSGBlockedError

_BEIJING = ZoneInfo("Asia/Shanghai")


class _FakeClient:
    """假通道客户端（ask/model 协议；exc 非空时调用即抛）。"""

    def __init__(self, model: str = "fake-model", reply: str = "fake reply", exc: Exception | None = None):
        self.model = model
        self._reply = reply
        self._exc = exc
        self.calls = 0

    def ask(self, prompt: str, *, system: str = "", temperature=None, max_tokens=None) -> str:
        self.calls += 1
        if self._exc is not None:
            raise self._exc
        return self._reply


def _make_gateway(tmp_path, clients, **kw):
    return LLMRuntimeGateway(clients=clients, db_path=tmp_path / "test.db", lsg_enabled=False, **kw)


def _rows(db_path):
    conn = sqlite3.connect(str(db_path))
    try:
        return conn.execute(
            "SELECT task_type, model, provider, tokens_in, tokens_out, cost_yuan, status, error "
            "FROM llm_call_log ORDER BY id"
        ).fetchall()
    finally:
        conn.close()


class TestChannelChain:
    def test_deepseek_success(self, tmp_path):
        ds = _FakeClient(model="deepseek-v4-flash", reply="ok-deepseek")
        qw = _FakeClient()
        ol = _FakeClient()
        gw = _make_gateway(tmp_path, {"deepseek": ds, "qwen": qw, "ollama": ol})
        r = gw.infer("summary_extraction", "压缩这段文本")
        assert r.status == "ok"
        assert r.provider == "deepseek"
        assert r.model_version == "deepseek-v4-flash"
        assert r.text == "ok-deepseek"
        assert r.tokens_in > 0 and r.tokens_out > 0
        assert r.latency_ms >= 0 and r.error is None
        assert ds.calls == 1 and qw.calls == 0 and ol.calls == 0

    def test_qwen_fallback(self, tmp_path):
        ds = _FakeClient(exc=RuntimeError("DeepSeek API HTTP error: 500"))
        qw = _FakeClient(model="qwen-flash", reply="ok-qwen")
        ol = _FakeClient()
        gw = _make_gateway(tmp_path, {"deepseek": ds, "qwen": qw, "ollama": ol})
        r = gw.infer("task_classification", "修复登录bug")
        assert r.status == "ok"
        assert r.provider == "qwen"
        assert r.text == "ok-qwen"
        assert ds.calls == 1 and qw.calls == 1 and ol.calls == 0

    def test_ollama_last_resort(self, tmp_path):
        ds = _FakeClient(exc=RuntimeError("timeout"))
        qw = _FakeClient(exc=RuntimeError("Qwen API HTTP error: 401"))
        ol = _FakeClient(model="qwen3:8b", reply="ok-ollama")
        gw = _make_gateway(tmp_path, {"deepseek": ds, "qwen": qw, "ollama": ol})
        r = gw.infer("tag_completion", "打标签")
        assert r.status == "ok"
        assert r.provider == "ollama"
        assert r.cost_yuan == 0.0  # 本地通道零费用
        assert ds.calls == 1 and qw.calls == 1 and ol.calls == 1

    def test_all_channels_failed(self, tmp_path):
        clients = {ch: _FakeClient(exc=RuntimeError(f"{ch} down")) for ch in ("deepseek", "qwen", "ollama")}
        gw = _make_gateway(tmp_path, clients)
        r = gw.infer("anomaly_triage", "审计结果")
        assert r.status == "error"
        assert r.text == ""
        assert "all channels failed" in r.error
        assert "deepseek" in r.error and "qwen" in r.error and "ollama" in r.error

    def test_explicit_channel_pins_no_cascade(self, tmp_path):
        ds = _FakeClient()
        qw = _FakeClient(model="qwen-flash", reply="ok-qwen")
        ol = _FakeClient()
        gw = _make_gateway(tmp_path, {"deepseek": ds, "qwen": qw, "ollama": ol})
        r = gw.infer("query_rewrite", "改写", channel="qwen")
        assert r.status == "ok" and r.provider == "qwen"
        assert ds.calls == 0 and qw.calls == 1 and ol.calls == 0

    def test_explicit_channel_failure_no_cascade(self, tmp_path):
        ds = _FakeClient()
        qw = _FakeClient(exc=RuntimeError("qwen down"))
        gw = _make_gateway(tmp_path, {"deepseek": ds, "qwen": qw})
        r = gw.infer("naming_suggest", "命名", channel="qwen")
        assert r.status == "error"
        assert ds.calls == 0  # 显式指定不静默降级

    def test_unknown_channel_value_error(self, tmp_path):
        gw = _make_gateway(tmp_path, {})
        with pytest.raises(ValueError, match="未知通道"):
            gw.infer("task_classification", "x", channel="glm")

    def test_infer_result_json_serializable(self, tmp_path):
        gw = _make_gateway(tmp_path, {"deepseek": _FakeClient()})
        r = gw.infer("summary_extraction", "文本")
        payload = json.loads(json.dumps(r.to_dict(), ensure_ascii=False))
        assert payload["status"] == "ok"
        assert set(payload) == {
            "text", "model_version", "provider", "tokens_in", "tokens_out",
            "cost_yuan", "latency_ms", "status", "error",
        }


class TestCallLogPersistence:
    def test_ok_call_logged(self, tmp_path):
        db = tmp_path / "test.db"
        gw = _make_gateway(tmp_path, {"deepseek": _FakeClient(model="deepseek-v4-flash")})
        gw.infer("summary_extraction", "文本")
        rows = _rows(db)
        assert len(rows) == 1
        task_type, model, provider, _tin, _tout, _cost, status, error = rows[0]
        assert (task_type, model, provider, status, error) == (
            "summary_extraction", "deepseek-v4-flash", "deepseek", "ok", None,
        )

    def test_failure_cascade_logged_per_attempt(self, tmp_path):
        db = tmp_path / "test.db"
        gw = _make_gateway(
            tmp_path,
            {
                "deepseek": _FakeClient(exc=RuntimeError("boom")),
                "qwen": _FakeClient(model="qwen-flash"),
            },
        )
        r = gw.infer("task_classification", "任务")
        assert r.status == "ok" and r.provider == "qwen"
        rows = _rows(db)
        assert [row[6] for row in rows] == ["error", "ok"]  # 降级链留痕：失败行+成功行各一
        assert rows[0][2] == "deepseek" and "boom" in rows[0][7]
        assert rows[1][2] == "qwen"

    def test_all_failed_logs_three_error_rows(self, tmp_path):
        db = tmp_path / "test.db"
        clients = {ch: _FakeClient(exc=RuntimeError("down")) for ch in ("deepseek", "qwen", "ollama")}
        gw = _make_gateway(tmp_path, clients)
        gw.infer("anomaly_triage", "审计")
        rows = _rows(db)
        assert len(rows) == 3
        assert {row[6] for row in rows} == {"error"}
        assert [row[2] for row in rows] == ["deepseek", "qwen", "ollama"]


class TestCostCalculation:
    @pytest.mark.parametrize(
        ("hour", "expected"),
        [(18, True), (23, True), (0, True), (8, True), (9, False), (12, False), (17, False)],
    )
    def test_valley_window_boundaries(self, hour, expected):
        ts = datetime(2026, 8, 22, hour, 0, tzinfo=_BEIJING)
        assert gw_mod.is_valley_period(ts) is expected

    def test_peak_cost_uses_registry_price(self):
        ts = datetime(2026, 8, 22, 12, 0, tzinfo=_BEIJING)  # 峰时
        cost = gw_mod.compute_cost_yuan("deepseek", "deepseek-chat", 1_000_000, 1_000_000, ts)
        assert cost == 3.0  # 注册表实证价 1.0/2.0 元每百万

    def test_valley_cost_uses_order_price(self):
        ts = datetime(2026, 8, 22, 20, 0, tzinfo=_BEIJING)  # 谷时
        cost = gw_mod.compute_cost_yuan("deepseek", "deepseek-chat", 1_000_000, 1_000_000, ts)
        assert cost == 6.0  # 工单口径谷时价 1.5/4.5 元每百万（待 Owner 校准）

    def test_qwen_and_ollama_zero_pending_calibration(self):
        ts = datetime(2026, 8, 22, 12, 0, tzinfo=_BEIJING)
        assert gw_mod.compute_cost_yuan("qwen", "qwen-flash", 10**6, 10**6, ts) == 0.0
        assert gw_mod.compute_cost_yuan("ollama", "qwen3:8b", 10**6, 10**6, ts) == 0.0

    def test_unknown_model_falls_back_to_provider_price(self):
        ts = datetime(2026, 8, 22, 12, 0, tzinfo=_BEIJING)
        cost = gw_mod.compute_cost_yuan("deepseek", "deepseek-v9-future", 10**6, 10**6, ts)
        assert cost == 3.0  # 通道兜底 deepseek-chat 档
        assert gw_mod.compute_cost_yuan("unknown-provider", "m", 10**6, 10**6, ts) == 0.0


class TestReconcileDailyCalls:
    def _seed(self, tmp_path):
        db = tmp_path / "test.db"
        gw = _make_gateway(
            tmp_path,
            {
                "deepseek": _FakeClient(model="deepseek-v4-flash", reply="r" * 400),
                "qwen": _FakeClient(exc=RuntimeError("down")),
            },
        )
        gw.infer("task_classification", "任务一")  # ok deepseek（首通道成功）
        with patch.object(gw_mod, "enforce_input", side_effect=LSGBlockedError("blocked by L1")):
            gw.infer("task_classification", "恶意 prompt")  # blocked
        return db

    def test_summary_aggregation(self, tmp_path):
        db = self._seed(tmp_path)
        today = datetime.now(tz=_BEIJING).date().isoformat()
        rep = gw_mod.reconcile_daily_calls(today, db_path=db)
        assert rep["date"] == today
        assert rep["total_calls"] == 2
        assert rep["by_status"] == {"ok": 1, "blocked": 1}
        assert rep["by_provider"]["deepseek"]["calls"] == 1
        assert rep["by_provider"][""]["calls"] == 1  # 入口拦截行无通道
        assert rep["total_tokens_in"] > 0 and rep["total_tokens_out"] > 0
        # 登记成本与价表重算自洽（同源价表 -> delta=0）
        assert rep["cost_delta_yuan"] == 0.0
        assert rep["total_cost_yuan"] == rep["recomputed_cost_yuan"]

    def test_expected_cost_guardrail(self, tmp_path):
        db = self._seed(tmp_path)
        today = datetime.now(tz=_BEIJING).date().isoformat()
        rep = gw_mod.reconcile_daily_calls(today, db_path=db, expected_cost_yuan=-1.0)
        assert rep["over_expected"] is True  # 任意非负成本均超 -1（防超额口径判定路径）
        rep_none = gw_mod.reconcile_daily_calls(today, db_path=db)
        assert rep_none["over_expected"] is None  # MVP 无预算门，缺省不判定

    def test_empty_day(self, tmp_path):
        db = tmp_path / "test.db"
        gw_mod.ensure_llm_call_log_table(db)
        rep = gw_mod.reconcile_daily_calls("2026-08-22", db_path=db)
        assert rep["total_calls"] == 0 and rep["total_cost_yuan"] == 0.0

    def test_invalid_date_fail_closed(self, tmp_path):
        with pytest.raises(ValueError, match="非法日期格式"):
            gw_mod.reconcile_daily_calls("2026/08/22", db_path=tmp_path / "test.db")


class TestLSGGate:
    def test_entry_block_no_channel_call_and_logged(self, tmp_path):
        db = tmp_path / "test.db"
        ds = _FakeClient()
        gw = _make_gateway(tmp_path, {"deepseek": ds, "qwen": _FakeClient(), "ollama": _FakeClient()})
        with patch.object(gw_mod, "enforce_input", side_effect=LSGBlockedError("LSG 输入判决 block")):
            r = gw.infer("summary_extraction", "恶意 prompt")
        assert r.status == "blocked"
        assert r.text == "" and "LSG" in r.error
        assert ds.calls == 0  # 判决 BLOCK -> 不发起任何通道调用
        rows = _rows(db)
        assert len(rows) == 1 and rows[0][6] == "blocked"

    def test_lsg_exception_fail_closed(self, tmp_path):
        # LSG 自身异常 -> fail-closed 拒调用（lsg_gate 内部已包成 LSGBlockedError，此处直模拟判决点故障）
        db = tmp_path / "test.db"
        ds = _FakeClient()
        gw = _make_gateway(tmp_path, {"deepseek": ds})
        with patch.object(
            gw_mod, "enforce_input", side_effect=LSGBlockedError("LSG 不可用，fail-closed 拒绝输入")
        ):
            r = gw.infer("summary_extraction", "任意 prompt")
        assert r.status == "blocked"
        assert "fail-closed" in r.error
        assert ds.calls == 0
        assert _rows(db)[0][6] == "blocked"

    def test_client_self_gate_block_no_cascade(self, tmp_path):
        db = tmp_path / "test.db"
        ds = _FakeClient(exc=LSGBlockedError("LSG 输出判决 block"))
        qw = _FakeClient()
        gw = _make_gateway(tmp_path, {"deepseek": ds, "qwen": qw})
        r = gw.infer("summary_extraction", "文本")
        assert r.status == "blocked" and r.provider == "deepseek"
        assert qw.calls == 0  # LSG 判决不降级（同 prompt 换通道重发无意义）
        rows = _rows(db)
        assert len(rows) == 1 and rows[0][6] == "blocked" and rows[0][2] == "deepseek"


class _FakeResp:
    def __init__(self, payload, exc=None):
        self._payload = payload
        self._exc = exc

    def raise_for_status(self):
        if self._exc is not None:
            raise self._exc

    def json(self):
        return self._payload


class TestQwenChat:
    def test_ask_success_openai_compatible(self, monkeypatch):
        chat = QwenChat(api_key="sk-test", lsg_enabled=False)
        seen = {}

        def _post(url, headers=None, json=None, timeout=None):  # noqa: A002 - requests 参数名
            seen["url"] = url
            seen["auth"] = headers["Authorization"]
            seen["body"] = json
            return _FakeResp({"choices": [{"message": {"content": "pong"}}]})

        monkeypatch.setattr("requests.post", _post)
        assert chat.ask("ping", system="sys") == "pong"
        assert seen["url"].endswith("/chat/completions")
        assert seen["auth"] == "Bearer sk-test"
        assert seen["body"]["model"] == chat.model
        assert seen["body"]["stream"] is False

    def test_ask_http_error_wrapped(self, monkeypatch):
        import requests

        chat = QwenChat(api_key="sk-test", lsg_enabled=False)
        monkeypatch.setattr(
            "requests.post",
            lambda *a, **k: _FakeResp({}, exc=requests.exceptions.HTTPError("401")),
        )
        with pytest.raises(RuntimeError, match="Qwen API HTTP error"):
            chat.ask("ping")

    def test_ask_empty_choices(self, monkeypatch):
        chat = QwenChat(api_key="sk-test", lsg_enabled=False)
        monkeypatch.setattr("requests.post", lambda *a, **k: _FakeResp({"choices": []}))
        with pytest.raises(RuntimeError, match="empty choices"):
            chat.ask("ping")

    def test_missing_key_fail_fast(self, monkeypatch):
        chat = QwenChat(lsg_enabled=False)  # __init__ 内 .env 加载后强制删除，隔离环境差异
        monkeypatch.delenv("QWEN_API_KEY", raising=False)
        with pytest.raises(secrets_mod.SecretsError):
            chat.ask("ping")

    def test_repr_hides_api_key(self):
        chat = QwenChat(api_key="sk-secret-xxx", lsg_enabled=False)
        assert "sk-secret-xxx" not in repr(chat)
