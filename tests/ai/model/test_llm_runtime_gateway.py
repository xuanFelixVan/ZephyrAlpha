# [BLUEPRINT] MOD-FEEDBACK_LOOP | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""
test_llm_runtime_gateway.py — llm_runtime_gateway MVP + GP1 预算门/LLMDeg/route 单测
=====================================================================================================
全 mock 通道（不真调 API；真跑在波5 由统筹执行）。覆盖：
- 三通道优先级链：DeepSeek 成功 / Qwen 备用降级 / Ollama 兜底 / 全失败 status=error / 显式 channel 钉死
- 登记落库三态断言：ok / error（降级留痕，每尝试一行）/ blocked（LSG 判决不发起调用）
- 成本计算：峰谷判定（高峰=北京 [9:00,12:00)∪[14:00,18:00)，DeepSeek 官网 2026-08-17 口径，谷=峰半价）、
  qwen 无峰谷平价/ollama 零价、未知模型通道兜底、无 tz 信息保守按峰时计价（防低估）
- reconcile_daily_calls 日终对账汇总（by_status/by_provider/重算 delta/防超额判定/非法日期 fail-closed）
- LSG：入口判决 BLOCK -> 不发起任何通道调用 + status=blocked 落库；LSG 异常 -> fail-closed 同径
- 预算硬门（10号文 §4 Phase 1.2）：DENY 阻断不发起调用+落库；引擎异常 fail-closed；token 消费回填闭环
- LLMDeg-0~4 降级注入（10号文 §3.6 降级表）：1=非关键本地优先 / 2=仅关键任务 API / 3|4=仅本地；
  显式 API 钉死在 2+非关键与 3+ 被拒
- route()（10号文 §4 Phase 1.4）：返回含 tier/reason/performance_score；LLMDeg tier 封顶与熔断标注
- L2 无旁路：源码无 bypass 配置项；Ollama 链与 API 链同过 LSG+预算闸门
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
budget_models = pytest.importorskip("zephyr.governance.ops_governance.budget_models")
budget_engine_mod = pytest.importorskip("zephyr.governance.ops_governance.budget_engine")

InferResult = gw_mod.InferResult
LLMRuntimeGateway = gw_mod.LLMRuntimeGateway
QwenChat = gw_mod.QwenChat
LSGBlockedError = gw_mod.LSGBlockedError
BudgetLevel = budget_models.BudgetLevel
GateDecision = budget_models.GateDecision
GateResult = budget_models.GateResult
ModelTier = budget_models.ModelTier
TaskComplexity = pytest.importorskip("zephyr.governance.intelligence_governance.model_router").TaskComplexity

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


class _FakeBudgetEngine:
    """假预算门（BudgetEngineProtocol 最小面）：可配 DENY/ALLOW×BudgetLevel；exc 非空时 pre_flight 即抛。"""

    def __init__(
        self,
        decision: GateDecision = GateDecision.ALLOW,
        level: BudgetLevel = BudgetLevel.L0_NORMAL,
        reason: str = "OK",
        exc: Exception | None = None,
    ):
        self._decision = decision
        self._level = level
        self._reason = reason
        self._exc = exc
        self.calls: list[dict] = []
        self.recorded: list[tuple] = []

    def pre_flight_check(self, request_id, estimated_tokens=0, estimated_cost=0.0, prompt=""):
        self.calls.append(
            {
                "request_id": request_id,
                "estimated_tokens": estimated_tokens,
                "estimated_cost": estimated_cost,
            }
        )
        if self._exc is not None:
            raise self._exc
        return GateResult(
            request_id=request_id,
            decision=self._decision,
            reason=self._reason,
            budget_level=self._level,
        )

    def get_model_router_recommendation(self):
        return (ModelTier.PREMIUM, 16000)

    def record_consumption(self, policy_id, tokens, cost, time_minutes):
        self.recorded.append((policy_id, tokens, cost, time_minutes))


def _make_gateway(tmp_path, clients, **kw):
    kw.setdefault("budget_engine", _FakeBudgetEngine())
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
            "text",
            "model_version",
            "provider",
            "tokens_in",
            "tokens_out",
            "cost_yuan",
            "latency_ms",
            "status",
            "error",
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
            "summary_extraction",
            "deepseek-v4-flash",
            "deepseek",
            "ok",
            None,
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
    # 官方口径（DeepSeek 官网 2026-08-17 调价，tracker #254 校准）：高峰=[9:00,12:00)∪[14:00,18:00)，
    # 其余为谷时（含午间 12:00-14:00），谷时价=高峰半价。
    @pytest.mark.parametrize(
        ("hour", "minute", "expected"),
        [
            (0, 0, True),  # 凌晨谷时
            (8, 59, True),  # 上午高峰前一刻仍谷时
            (9, 0, False),  # 上午高峰起点（含）
            (11, 59, False),  # 上午高峰内
            (12, 0, True),  # 上午高峰终点（不含）-> 午间谷时
            (13, 59, True),  # 午间 12:00-14:00 谷时
            (14, 0, False),  # 下午高峰起点（含）
            (17, 59, False),  # 下午高峰内
            (18, 0, True),  # 下午高峰终点（不含）-> 晚间谷时
            (20, 0, True),  # 晚间谷时
            (23, 0, True),  # 深夜谷时
        ],
    )
    def test_valley_window_boundaries(self, hour, minute, expected):
        ts = datetime(2026, 8, 22, hour, minute, tzinfo=_BEIJING)
        assert gw_mod.is_valley_period(ts) is expected

    @pytest.mark.parametrize(
        ("model", "peak_cost", "valley_cost"),
        [
            ("deepseek-chat", 12.0, 6.0),  # 高峰 3.0/9.0，空闲 1.5/4.5
            ("deepseek-v4-flash", 12.0, 6.0),  # 与 deepseek-chat 同一模型（别称）同价
            ("deepseek-reasoner", 12.0, 6.0),  # 名称已弃用=v4-flash 同价
            ("deepseek-v4-pro", 36.0, 18.0),  # 高峰 9.0/27.0，空闲 4.5/13.5
        ],
    )
    def test_pricing_table_official_values(self, model, peak_cost, valley_cost):
        peak_ts = datetime(2026, 8, 22, 10, 0, tzinfo=_BEIJING)  # 峰时
        valley_ts = datetime(2026, 8, 22, 20, 0, tzinfo=_BEIJING)  # 谷时
        assert gw_mod.compute_cost_yuan("deepseek", model, 10**6, 10**6, peak_ts) == peak_cost
        assert gw_mod.compute_cost_yuan("deepseek", model, 10**6, 10**6, valley_ts) == valley_cost

    def test_valley_is_half_of_peak(self):
        # 谷时折扣方向按官方校准：谷=峰半价（纠正旧口径谷>峰的方向错误）
        peak_ts = datetime(2026, 8, 22, 15, 0, tzinfo=_BEIJING)
        valley_ts = datetime(2026, 8, 22, 12, 30, tzinfo=_BEIJING)  # 午间谷时
        peak = gw_mod.compute_cost_yuan("deepseek", "deepseek-chat", 10**6, 10**6, peak_ts)
        valley = gw_mod.compute_cost_yuan("deepseek", "deepseek-chat", 10**6, 10**6, valley_ts)
        assert peak == 12.0 and valley == peak / 2

    def test_qwen_flat_price_and_ollama_free(self):
        peak_ts = datetime(2026, 8, 22, 10, 0, tzinfo=_BEIJING)
        valley_ts = datetime(2026, 8, 22, 20, 0, tzinfo=_BEIJING)
        # qwen-flash 无峰谷平价 0.15/1.5 元每百万（百炼 2026-07-31 页；真跑实证模型名=qwen-flash）
        assert gw_mod.compute_cost_yuan("qwen", "qwen-flash", 10**6, 10**6, peak_ts) == 1.65
        assert gw_mod.compute_cost_yuan("qwen", "qwen-flash", 10**6, 10**6, valley_ts) == 1.65
        assert gw_mod.compute_cost_yuan("ollama", "qwen3:8b", 10**6, 10**6, peak_ts) == 0.0

    def test_unknown_model_falls_back_to_provider_price(self):
        ts = datetime(2026, 8, 22, 10, 0, tzinfo=_BEIJING)
        cost = gw_mod.compute_cost_yuan("deepseek", "deepseek-v9-future", 10**6, 10**6, ts)
        assert cost == 12.0  # 通道兜底 deepseek-chat 峰时档
        assert gw_mod.compute_cost_yuan("qwen", "qwen-unknown", 10**6, 10**6, ts) == 1.65  # 兜底 qwen-flash 档
        assert gw_mod.compute_cost_yuan("unknown-provider", "m", 10**6, 10**6, ts) == 0.0

    def test_naive_timestamp_conservatively_peak(self):
        # 保守原则：无 tz 信息的不确定情形按峰时计价（防低估成本），即使钟点落在谷时窗口
        naive = datetime(2026, 8, 22, 20, 0)
        assert gw_mod.is_valley_period(naive) is False
        assert gw_mod.compute_cost_yuan("deepseek", "deepseek-chat", 10**6, 10**6, naive) == 12.0


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
        with patch.object(gw_mod, "enforce_input", side_effect=LSGBlockedError("LSG 不可用，fail-closed 拒绝输入")):
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


class TestBudgetGate:
    """预算硬门（10号文 §4 Phase 1.2）：门面入口统一 pre_flight_check，DENY 阻断。"""

    def test_deny_blocks_before_any_channel_and_logged(self, tmp_path):
        db = tmp_path / "test.db"
        ds = _FakeClient()
        engine = _FakeBudgetEngine(
            decision=GateDecision.DENY,
            level=BudgetLevel.L5_HARD_STOP,
            reason="COST hard stop: daily 120%",
        )
        gw = _make_gateway(tmp_path, {"deepseek": ds, "ollama": _FakeClient()}, budget_engine=engine)
        r = gw.infer("summary_extraction", "文本")
        assert r.status == "blocked"
        assert "budget_denied" in r.error and "hard stop" in r.error
        assert ds.calls == 0  # DENY -> 不发起任何通道调用
        assert engine.calls and engine.calls[0]["estimated_tokens"] > 0
        assert gw.last_llmdeg == 4  # L5_HARD_STOP -> LLMDeg-4 熔断
        rows = _rows(db)
        assert len(rows) == 1 and rows[0][6] == "blocked"
        assert engine.recorded == []  # 被拦调用不回填消费

    def test_engine_exception_fail_closed(self, tmp_path):
        db = tmp_path / "test.db"
        ds = _FakeClient()
        engine = _FakeBudgetEngine(exc=RuntimeError("budget store down"))
        gw = _make_gateway(tmp_path, {"deepseek": ds}, budget_engine=engine)
        r = gw.infer("summary_extraction", "文本")
        assert r.status == "blocked"
        assert "budget_gate_unavailable" in r.error
        assert ds.calls == 0
        assert _rows(db)[0][6] == "blocked"

    def test_llmdeg_level_refreshed_from_budget_level(self, tmp_path):
        engine = _FakeBudgetEngine(level=BudgetLevel.L2_THROTTLED)
        gw = _make_gateway(tmp_path, {"ollama": _FakeClient()}, budget_engine=engine)
        assert gw.last_llmdeg == 0
        gw.infer("tag_completion", "打标签")
        assert gw.last_llmdeg == 2

    def test_consumption_recorded_on_ok(self, tmp_path):
        engine = _FakeBudgetEngine()
        gw = _make_gateway(tmp_path, {"deepseek": _FakeClient()}, budget_engine=engine)
        r = gw.infer("summary_extraction", "文本")
        assert r.status == "ok"
        # ARCH-303：TOKEN（二级兜底）+ COST（主维度）双维回填，各一条
        assert len(engine.recorded) == 2
        by_policy = {policy_id: (tokens, cost) for policy_id, tokens, cost, _m in engine.recorded}
        assert by_policy["BP-TOKEN-001"][0] == r.tokens_in + r.tokens_out > 0
        assert by_policy["BP-COST-001"][1] == pytest.approx(r.cost_yuan)


class TestCostDimensionGate:
    """ARCH-303（2026-08-31 裁定）：预算硬门主维度=COST（元），TOKEN 降为二级兜底。

    - 预检 estimated_cost 由 est_tokens 按内置价表峰时保守价折算（元）传入 pre_flight_check
    - 真实 BudgetEngine：COST 维日耗超 hard_stop -> DENY 阻断（不发起通道调用）
    - TOKEN 维超限仍兜底 DENY（防跑飞二级保险丝）
    - 成功调用回填真实 result.cost_yuan，COST 维真实累加
    """

    def test_pre_flight_receives_estimated_cost_priced_from_est_tokens(self, tmp_path):
        """_budget_gate 预检成本 = est 输入按峰时输入价 + max_tokens 按峰时输出价合并估（元）。"""
        engine = _FakeBudgetEngine()
        gw = _make_gateway(tmp_path, {"deepseek": _FakeClient()}, budget_engine=engine)
        prompt = "压缩这段文本" * 10
        r = gw.infer("summary_extraction", prompt, max_tokens=4096)
        assert r.status == "ok"
        call = engine.calls[0]
        in_est = gw_mod._estimate_tokens(prompt)
        # 峰时保守价（deepseek-chat 档 3.0/9.0 元每百万）：输入 est + 输出 max_tokens 上限
        expected_cost = (in_est * 3.0 + 4096 * 9.0) / 1_000_000
        assert call["estimated_cost"] == pytest.approx(expected_cost)
        assert call["estimated_cost"] > 0.0
        assert call["estimated_tokens"] == in_est + 4096

    def test_cost_hard_stop_denies_with_real_engine(self, tmp_path):
        """真 BudgetEngine：COST 维日耗≥hard_stop（日限 10 元）-> blocked，不发起通道调用。"""
        engine = budget_engine_mod.BudgetEngine()
        engine.record_consumption("BP-COST-001", tokens=0, cost=9.9, time_minutes=0.0)  # 99% ≥ 98%
        ds = _FakeClient()
        gw = _make_gateway(tmp_path, {"deepseek": ds}, budget_engine=engine)
        r = gw.infer("summary_extraction", "文本")
        assert r.status == "blocked"
        assert "budget_denied" in r.error and "COST" in r.error
        assert ds.calls == 0

    def test_token_hard_stop_still_backstop_denies(self, tmp_path):
        """TOKEN 降为二级兜底但仍生效：token 日耗≥98% 且成本未超 -> DENY。"""
        engine = budget_engine_mod.BudgetEngine()
        engine.record_consumption("BP-TOKEN-001", tokens=990_000, cost=0.0, time_minutes=0.0)
        ds = _FakeClient()
        gw = _make_gateway(tmp_path, {"deepseek": ds}, budget_engine=engine)
        r = gw.infer("summary_extraction", "文本")
        assert r.status == "blocked"
        assert "budget_denied" in r.error and "TOKEN" in r.error
        assert ds.calls == 0

    def test_real_cost_yuan_backfilled_to_cost_dimension(self, tmp_path):
        """成功调用后真实 cost_yuan 回填：COST 维累加元成本、TOKEN 维累加 token。"""
        engine = budget_engine_mod.BudgetEngine()
        ds = _FakeClient(model="deepseek-v4-flash", reply="好" * 100)
        gw = _make_gateway(tmp_path, {"deepseek": ds}, budget_engine=engine)
        r = gw.infer("summary_extraction", "压缩这段文本")
        assert r.status == "ok" and r.cost_yuan > 0.0
        summary = engine.get_consumption_summary()
        assert summary["BP-COST-001"]["daily"] == pytest.approx(r.cost_yuan)
        assert summary["BP-TOKEN-001"]["daily"] == r.tokens_in + r.tokens_out


class TestLLMDegRouting:
    """LLMDeg-0~4 注入路由决策（10号文 §3.6 降级表走向逐条对应）。"""

    @staticmethod
    def _clients():
        return {
            "deepseek": _FakeClient(model="deepseek-v4-flash", reply="ok-deepseek"),
            "qwen": _FakeClient(model="qwen-flash", reply="ok-qwen"),
            "ollama": _FakeClient(model="qwen3:8b", reply="ok-ollama"),
        }

    def test_level0_default_chain_api_first(self, tmp_path):
        clients = self._clients()
        gw = _make_gateway(tmp_path, clients, budget_engine=_FakeBudgetEngine(level=BudgetLevel.L0_NORMAL))
        r = gw.infer("summary_extraction", "文本")
        assert r.provider == "deepseek"
        assert clients["deepseek"].calls == 1 and clients["ollama"].calls == 0

    def test_level1_noncritical_local_first(self, tmp_path):
        clients = self._clients()
        gw = _make_gateway(tmp_path, clients, budget_engine=_FakeBudgetEngine(level=BudgetLevel.L1_WARNING))
        r = gw.infer("summary_extraction", "文本")  # 非关键任务
        assert r.status == "ok" and r.provider == "ollama"  # LLMDeg-1：非关键 API->本地降级
        assert clients["ollama"].calls == 1 and clients["deepseek"].calls == 0

    def test_level1_critical_keeps_api_first(self, tmp_path):
        clients = self._clients()
        gw = _make_gateway(tmp_path, clients, budget_engine=_FakeBudgetEngine(level=BudgetLevel.L1_WARNING))
        r = gw.infer("summary_extraction", "文本", critical=True)
        assert r.provider == "deepseek"
        assert clients["deepseek"].calls == 1 and clients["ollama"].calls == 0

    def test_level2_noncritical_local_only(self, tmp_path):
        clients = self._clients()
        gw = _make_gateway(tmp_path, clients, budget_engine=_FakeBudgetEngine(level=BudgetLevel.L2_THROTTLED))
        r = gw.infer("tag_completion", "文本")
        assert r.provider == "ollama"
        assert clients["deepseek"].calls == 0 and clients["qwen"].calls == 0

    def test_level2_critical_api_allowed(self, tmp_path):
        clients = self._clients()
        gw = _make_gateway(tmp_path, clients, budget_engine=_FakeBudgetEngine(level=BudgetLevel.L2_THROTTLED))
        r = gw.infer("reflection_l3", "深度反思", critical=True)  # LLMDeg-2：仅战略层+反思 L2/L3 用 API
        assert r.provider == "deepseek"
        assert clients["deepseek"].calls == 1

    def test_level3_all_local_only_even_critical(self, tmp_path):
        clients = self._clients()
        gw = _make_gateway(tmp_path, clients, budget_engine=_FakeBudgetEngine(level=BudgetLevel.L3_DEGRADED))
        r = gw.infer("reflection_l3", "深度反思", critical=True)  # LLMDeg-3：全部 API->本地降级
        assert r.provider == "ollama"
        assert clients["deepseek"].calls == 0 and clients["qwen"].calls == 0

    def test_level4_local_only(self, tmp_path):
        clients = self._clients()
        gw = _make_gateway(tmp_path, clients, budget_engine=_FakeBudgetEngine(level=BudgetLevel.L4_EMERGENCY))
        r = gw.infer("summary_extraction", "文本")
        assert gw.last_llmdeg == 4
        assert r.provider == "ollama"
        assert clients["deepseek"].calls == 0

    def test_explicit_api_pin_blocked_at_level2_noncritical(self, tmp_path):
        db = tmp_path / "test.db"
        clients = self._clients()
        gw = _make_gateway(tmp_path, clients, budget_engine=_FakeBudgetEngine(level=BudgetLevel.L2_THROTTLED))
        r = gw.infer("summary_extraction", "文本", channel="deepseek")
        assert r.status == "blocked" and "llmdeg-2" in r.error
        assert clients["deepseek"].calls == 0
        assert _rows(db)[0][6] == "blocked"

    def test_explicit_api_pin_allowed_at_level0(self, tmp_path):
        clients = self._clients()
        gw = _make_gateway(tmp_path, clients, budget_engine=_FakeBudgetEngine(level=BudgetLevel.L0_NORMAL))
        r = gw.infer("summary_extraction", "文本", channel="qwen")
        assert r.status == "ok" and r.provider == "qwen"

    def test_explicit_local_pin_allowed_at_level3(self, tmp_path):
        clients = self._clients()
        gw = _make_gateway(tmp_path, clients, budget_engine=_FakeBudgetEngine(level=BudgetLevel.L3_DEGRADED))
        r = gw.infer("summary_extraction", "文本", channel="ollama")
        assert r.status == "ok" and r.provider == "ollama"


class TestRouteMethod:
    """route() 接 MOD-INF-024 perf-aware 决策（10号文 §4 Phase 1.4）。"""

    def test_route_returns_tier_reason_performance_score(self, tmp_path):
        gw = _make_gateway(tmp_path, {"deepseek": _FakeClient()})
        d = gw.route(complexity=TaskComplexity.COMPLEX)
        assert d.tier is ModelTier.STANDARD  # COMPLEX -> STANDARD（无 LLMDeg 封顶）
        assert isinstance(d.reason, str) and d.reason
        assert isinstance(d.performance_score, float)
        assert isinstance(d.model_key, str) and d.model_key

    def test_route_llmdeg2_caps_tier_for_noncritical(self, tmp_path):
        gw = _make_gateway(
            tmp_path,
            {"ollama": _FakeClient()},
            budget_engine=_FakeBudgetEngine(level=BudgetLevel.L2_THROTTLED),
        )
        gw.infer("tag_completion", "文本")  # 刷新 LLMDeg-2
        d = gw.route(complexity=TaskComplexity.COMPLEX)
        assert d.tier is ModelTier.ECONOMY  # STANDARD 被 LLMDeg-2 封顶到 ECONOMY
        assert "llmdeg-2-tier-cap" in d.reason

    def test_route_llmdeg2_critical_not_capped(self, tmp_path):
        gw = _make_gateway(
            tmp_path,
            {"deepseek": _FakeClient()},
            budget_engine=_FakeBudgetEngine(level=BudgetLevel.L2_THROTTLED),
        )
        gw.infer("reflection_l3", "深度反思", critical=True)
        d = gw.route(complexity=TaskComplexity.COMPLEX, critical=True)
        assert d.tier is ModelTier.STANDARD  # 关键任务在级别 <3 不封顶

    def test_route_llmdeg3_marks_api_suspended(self, tmp_path):
        gw = _make_gateway(
            tmp_path,
            {"ollama": _FakeClient()},
            budget_engine=_FakeBudgetEngine(level=BudgetLevel.L3_DEGRADED),
        )
        gw.infer("tag_completion", "文本")
        d = gw.route(complexity=TaskComplexity.MODERATE)
        assert "api-suspended-local-only" in d.reason


class TestNoL2Bypass:
    """L2 无旁路（10号文 §4 Phase 1.3 对齐验证）：代码中无 L2 旁路配置项；L2 与 L3 同一闸门。"""

    def test_source_has_no_bypass_config_token(self):
        import inspect

        src = inspect.getsource(gw_mod).lower()
        assert "bypass" not in src  # 源码零英文 bypass 配置项（中文“旁路”仅出现在否定性注释）

    def test_gateway_has_no_bypass_attribute(self, tmp_path):
        gw = _make_gateway(tmp_path, {"ollama": _FakeClient()})
        assert not any("bypass" in name.lower() for name in dir(gw))

    def test_ollama_chain_blocked_by_same_lsg_gate(self, tmp_path):
        db = tmp_path / "test.db"
        ol = _FakeClient()
        gw = _make_gateway(tmp_path, {"ollama": ol}, chain=("ollama",))
        with patch.object(gw_mod, "enforce_input", side_effect=LSGBlockedError("LSG 判决 block")):
            r = gw.infer("summary_extraction", "恶意 prompt")
        assert r.status == "blocked"
        assert ol.calls == 0  # L2 路径同过 LSG 入口闸门
        assert _rows(db)[0][6] == "blocked"

    def test_ollama_chain_blocked_by_same_budget_gate(self, tmp_path):
        db = tmp_path / "test.db"
        ol = _FakeClient()
        engine = _FakeBudgetEngine(decision=GateDecision.DENY, level=BudgetLevel.L5_HARD_STOP)
        gw = _make_gateway(tmp_path, {"ollama": ol}, chain=("ollama",), budget_engine=engine)
        r = gw.infer("summary_extraction", "文本")
        assert r.status == "blocked" and "budget_denied" in r.error
        assert ol.calls == 0  # L2 路径同过预算硬门，无本地豁免
        assert _rows(db)[0][6] == "blocked"
