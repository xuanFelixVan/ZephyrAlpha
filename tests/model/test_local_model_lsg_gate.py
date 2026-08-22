# [A_test] module_id: MOD-GOV_local_model_lsg_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-042 | docs/03_modules/_domain_integration/blueprint.md | §test
# [MODULE] tests.model.test_local_model_lsg_gate
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_local_model_lsg_gate.py
# [TTL] task_bound

"""
test_local_model_lsg_gate.py — local_model LSG 注入单测（09号文 §4.2 P0-1，2026-08-22）
=====================================================================================

覆盖：开关解析（env/构造参数/默认开）、mock 网关判决 BLOCK -> 抛 LSGBlockedError 且
不发起 API 调用、ALLOW -> 正常调用、判决记录落 L6 审计断言、LSG 不可用 fail-closed。
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

lsg_gate = pytest.importorskip("zephyr.integration.local_model.lsg_gate")
ollama_chat = pytest.importorskip("zephyr.integration.local_model.ollama_chat")
deepseek_chat = pytest.importorskip("zephyr.integration.local_model.deepseek_chat")
embedding_router = pytest.importorskip("zephyr.integration.local_model.embedding_router")
local_model_scheduler = pytest.importorskip("zephyr.integration.local_model.local_model_scheduler")
security_decision = pytest.importorskip("zephyr.shared.contracts.security.security_decision")
gw_mod = pytest.importorskip("zephyr.security.llm_defense.llm_security.gateway")

LSGBlockedError = lsg_gate.LSGBlockedError
SecurityDecision = security_decision.SecurityDecision


def _scan_result(decision, mode):
    """构造 mock 网关判决结果（ScanResult 真实类型）."""
    denied = 1 if decision in (SecurityDecision.BLOCK, SecurityDecision.DENY) else 0
    return gw_mod.ScanResult(
        decision=decision,
        mode=mode,
        layers_evaluated=1,
        layers_passed=1 - denied,
        layers_denied=denied,
        layers_flagged=0,
        total_score=1.0 if not denied else 0.0,
        elapsed_ms=0.05,
        blocked_by="mock_layer" if denied else "",
    )


def _make_gw(input_decision=SecurityDecision.ALLOW, output_decision=SecurityDecision.ALLOW):
    """构造 mock 网关 + 附着的 L6 mock 层，返回 (gateway, l6_layer)."""
    gw = MagicMock()
    gw.scan_input = AsyncMock(return_value=_scan_result(input_decision, gw_mod.ScanMode.INPUT_ONLY))
    gw.scan_output = AsyncMock(return_value=_scan_result(output_decision, gw_mod.ScanMode.OUTPUT_ONLY))
    l6 = MagicMock()
    gw.get_layer = MagicMock(side_effect=lambda name: l6 if name == "l6_observability" else None)
    return gw, l6


def _mock_http_response(content: str, *, openai_style: bool = False) -> MagicMock:
    resp = MagicMock()
    resp.status_code = 200
    if openai_style:
        resp.json.return_value = {"choices": [{"message": {"content": content}}]}
    else:
        resp.json.return_value = {"message": {"content": content}}
    return resp


class TestSwitchResolution:
    """开关解析：构造参数 > 环境变量 > 默认开."""

    def test_default_on(self, monkeypatch):
        monkeypatch.delenv(lsg_gate.LSG_ENABLED_ENV, raising=False)
        assert lsg_gate.resolve_lsg_enabled(None) is True

    def test_env_off(self, monkeypatch):
        monkeypatch.setenv(lsg_gate.LSG_ENABLED_ENV, "0")
        assert lsg_gate.resolve_lsg_enabled(None) is False

    @pytest.mark.parametrize("value", ["0", "false", "off", "no", "FALSE", "Off"])
    def test_env_off_values(self, monkeypatch, value):
        monkeypatch.setenv(lsg_gate.LSG_ENABLED_ENV, value)
        assert lsg_gate.resolve_lsg_enabled(None) is False

    def test_override_beats_env(self, monkeypatch):
        monkeypatch.setenv(lsg_gate.LSG_ENABLED_ENV, "0")
        assert lsg_gate.resolve_lsg_enabled(True) is True
        monkeypatch.setenv(lsg_gate.LSG_ENABLED_ENV, "1")
        assert lsg_gate.resolve_lsg_enabled(False) is False

    def test_blocked_error_is_runtime_error(self):
        """错误契约：LSGBlockedError 必须是 RuntimeError 子类（客户端契约零破坏）."""
        assert issubclass(LSGBlockedError, RuntimeError)


class TestEnforceFailClosed:
    """LSG 不可用 -> fail-closed 抛 LSGBlockedError."""

    def test_enforce_input_gateway_unavailable(self, monkeypatch):
        monkeypatch.setattr(lsg_gate, "get_gateway", lambda: None)
        with pytest.raises(LSGBlockedError, match="fail-closed"):
            lsg_gate.enforce_input("hello", source="test")

    def test_enforce_output_gateway_unavailable(self, monkeypatch):
        monkeypatch.setattr(lsg_gate, "get_gateway", lambda: None)
        with pytest.raises(LSGBlockedError, match="fail-closed"):
            lsg_gate.enforce_output("answer", source="test")

    def test_enforce_skipped_when_disabled(self, monkeypatch):
        monkeypatch.setattr(lsg_gate, "get_gateway", lambda: None)
        lsg_gate.enforce_input("hello", source="test", enabled=False)  # 不抛
        lsg_gate.enforce_output("answer", source="test", enabled=False)  # 不抛


class TestOllamaChatInjection:
    def test_blocked_input_raises_and_no_api_call(self, monkeypatch):
        gw, l6 = _make_gw(input_decision=SecurityDecision.DENY)
        monkeypatch.setattr(lsg_gate, "_gateway", gw)
        chat = ollama_chat.OllamaChat()
        with patch("requests.post", return_value=_mock_http_response("reply")) as mock_post:
            with pytest.raises(LSGBlockedError, match="deny"):
                chat.ask("malicious prompt")
            assert mock_post.called is False, "BLOCK 判决后不得发起 API 调用"
        gw.scan_input.assert_awaited_once()
        assert l6.log_security_event.called, "判决必须落 L6 审计"

    def test_allow_calls_api_and_audit_written(self, monkeypatch):
        gw, l6 = _make_gw()
        monkeypatch.setattr(lsg_gate, "_gateway", gw)
        chat = ollama_chat.OllamaChat()
        with patch("requests.post", return_value=_mock_http_response("test reply")) as mock_post:
            assert chat.ask("hello") == "test reply"
            assert mock_post.called is True
        gw.scan_input.assert_awaited_once()
        gw.scan_output.assert_awaited_once()
        # 输入+输出各一条 L6 审计记录
        assert l6.log_security_event.call_count == 2
        messages = [str(c.kwargs.get("message", "")) for c in l6.log_security_event.call_args_list]
        assert any("decision=allow" in m and "input" in m for m in messages)
        assert any("decision=allow" in m and "output" in m for m in messages)

    def test_blocked_output_raises(self, monkeypatch):
        gw, l6 = _make_gw(output_decision=SecurityDecision.BLOCK)
        monkeypatch.setattr(lsg_gate, "_gateway", gw)
        chat = ollama_chat.OllamaChat()
        with patch("requests.post", return_value=_mock_http_response("leaked secret")):
            with pytest.raises(LSGBlockedError, match="block"):
                chat.ask("hello")

    def test_lsg_disabled_skips_scan(self, monkeypatch):
        gw, _ = _make_gw(input_decision=SecurityDecision.DENY)
        monkeypatch.setattr(lsg_gate, "_gateway", gw)
        chat = ollama_chat.OllamaChat(lsg_enabled=False)
        with patch("requests.post", return_value=_mock_http_response("reply")):
            assert chat.ask("anything") == "reply"
        gw.scan_input.assert_not_awaited()
        gw.scan_output.assert_not_awaited()


class TestDeepSeekChatInjection:
    def test_blocked_input_raises_and_no_api_call(self, monkeypatch):
        gw, _ = _make_gw(input_decision=SecurityDecision.BLOCK)
        monkeypatch.setattr(lsg_gate, "_gateway", gw)
        chat = deepseek_chat.DeepSeekChat(api_key="sk-test")
        with patch("requests.post", return_value=_mock_http_response("reply", openai_style=True)) as mock_post:
            with pytest.raises(LSGBlockedError, match="block"):
                chat.ask("malicious prompt")
            assert mock_post.called is False

    def test_allow_calls_api_and_audit_written(self, monkeypatch):
        gw, l6 = _make_gw()
        monkeypatch.setattr(lsg_gate, "_gateway", gw)
        chat = deepseek_chat.DeepSeekChat(api_key="sk-test")
        with patch("requests.post", return_value=_mock_http_response("ds reply", openai_style=True)) as mock_post:
            assert chat.ask("hello") == "ds reply"
            assert mock_post.called is True
        gw.scan_input.assert_awaited_once()
        gw.scan_output.assert_awaited_once()
        assert l6.log_security_event.call_count == 2


class TestEmbeddingRouterInjection:
    def _router_with_model(self):
        router = embedding_router.EmbeddingRouter()
        router.bge_m3_available = True
        mock_model = MagicMock()
        mock_model.encode.return_value = np.ones(1024, dtype=np.float32)
        router.bge_m3_model = mock_model
        return router, mock_model

    def test_blocked_input_raises_and_no_encode(self, monkeypatch):
        gw, _ = _make_gw(input_decision=SecurityDecision.DENY)
        monkeypatch.setattr(lsg_gate, "_gateway", gw)
        router, mock_model = self._router_with_model()
        with pytest.raises(LSGBlockedError):
            router.embed("malicious text", "knowledge")
        mock_model.encode.assert_not_called()

    def test_allow_embeds_and_audit_written(self, monkeypatch):
        gw, l6 = _make_gw()
        monkeypatch.setattr(lsg_gate, "_gateway", gw)
        router, mock_model = self._router_with_model()
        vec = router.embed("hello", "knowledge")
        assert vec.shape[0] == 1024
        mock_model.encode.assert_called_once()
        assert l6.log_security_event.call_count == 1

    def test_embed_batch_blocked_raises(self, monkeypatch):
        gw, _ = _make_gw(input_decision=SecurityDecision.BLOCK)
        monkeypatch.setattr(lsg_gate, "_gateway", gw)
        router, mock_model = self._router_with_model()
        with pytest.raises(LSGBlockedError):
            router.embed_batch(["t1", "t2"], "knowledge")
        mock_model.encode.assert_not_called()


class TestSchedulerInjection:
    def _task(self, capability, payload):
        return local_model_scheduler.LocalTask(task_id="t-1", capability=capability, payload=payload)

    def test_inference_blocked_raises_and_backend_untouched(self, monkeypatch):
        gw, _ = _make_gw(input_decision=SecurityDecision.DENY)
        monkeypatch.setattr(lsg_gate, "_gateway", gw)
        backend = MagicMock()
        sched = local_model_scheduler.LocalModelScheduler(ollama_chat=backend)
        with pytest.raises(LSGBlockedError):
            sched._handle_inference(self._task("task_classification", {"text": "malicious"}))
        backend.inference.assert_not_called()

    def test_inference_allow_dispatches(self, monkeypatch):
        gw, l6 = _make_gw()
        monkeypatch.setattr(lsg_gate, "_gateway", gw)
        backend = MagicMock()
        backend.inference.return_value = {"category": "audit"}
        sched = local_model_scheduler.LocalModelScheduler(ollama_chat=backend)
        result = sched._handle_inference(self._task("task_classification", {"text": "fix login bug"}))
        assert result["category"] == "audit"
        backend.inference.assert_called_once()
        assert l6.log_security_event.call_count == 1

    def test_embedding_blocked_raises(self, monkeypatch):
        gw, _ = _make_gw(input_decision=SecurityDecision.BLOCK)
        monkeypatch.setattr(lsg_gate, "_gateway", gw)
        router = MagicMock()
        sched = local_model_scheduler.LocalModelScheduler(embedding_router=router)
        with pytest.raises(LSGBlockedError):
            sched._handle_embedding(self._task("vector_embedding", {"text": "malicious"}))
        router.embed.assert_not_called()

    def test_lsg_disabled_skips_scan(self, monkeypatch):
        gw, _ = _make_gw(input_decision=SecurityDecision.DENY)
        monkeypatch.setattr(lsg_gate, "_gateway", gw)
        backend = MagicMock()
        backend.inference.return_value = {"category": "audit"}
        sched = local_model_scheduler.LocalModelScheduler(ollama_chat=backend, lsg_enabled=False)
        result = sched._handle_inference(self._task("task_classification", {"text": "anything"}))
        assert result["category"] == "audit"
        gw.scan_input.assert_not_awaited()
