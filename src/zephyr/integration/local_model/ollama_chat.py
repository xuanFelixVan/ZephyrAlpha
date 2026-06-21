# [A_module] module_id=MOD-INT_ollama_chat | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-042 | docs/03_modules/_domain-integration/local-model/blueprint.md | §3.1

# [MODULE] zephyr.integration.local_model.ollama_chat

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] auto_runtime_core.py; local_model_scheduler.py; vector_memory_server.py

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] _budget_preflight DENY 时抛 RuntimeError; _chat 网络失败时抛异常

# [TESTS]

"""
OllamaChat — 通过 Ollama HTTP API 进行本地 LLM 推理
====================================================
替代外部 API 调用，使用本地 Ollama 的 qwen3:8b 等模型。
零费用，网络仅 localhost。

用法
----
    chat = OllamaChat(model="qwen3:8b")
    reply = chat.ask("这段代码有什么问题？", system="你是代码审查助手")
    structured = chat.ask_json("分类: {text}", fields=["category", "confidence"])
"""


from __future__ import annotations

import json
import logging
import re
from typing import Any

_log = logging.getLogger(__name__)

DEFAULT_OLLAMA_URL = "http://localhost:11434"

INFERENCE_MODEL = "qwen3:8b"
INFERENCE_TEMPERATURE = 0.1
INFERENCE_MAX_TOKENS = 1024
INFERENCE_TIMEOUT_S = 60.0

SYSTEM_PROMPTS: dict[str, str] = {
    "task_classification": (
        "You are a task classifier. Classify the input task into one of: "
        "audit, compliance, cleanup, repair, codegen, review, analysis, other."
        "\nOutput only the classification label, no explanation."
    ),
    "tag_completion": (
        "You are a tag generator. Given a task description, "
        "infer appropriate tag labels. Tags should be single English words."
        "\nOutput JSON: {\"tags\": [\"tag1\", \"tag2\"]}"
    ),
    "summary_extraction": (
        "You are a summary extractor. Compress the input text into 3 key points, "
        "each point under 50 characters."
        "\nOutput JSON: {\"points\": [\"point1\", \"point2\", \"point3\"]}"
    ),
    "anomaly_triage": (
        "You are an anomaly triager. Determine whether the input audit/log result is suspicious, "
        "and whether human intervention is needed."
        "\nOutput JSON: {\"needs_human\": true/false, \"reason\": \"one-line reason\"}"
    ),
    "query_rewrite": (
        "You are a search optimizer. Rewrite the user's natural language search query "
        "into more precise technical search terms, removing filler words and "
        "retaining core technical concepts."
        "\nOutput JSON: {\"rewritten\": \"optimized query\"}"
    ),
    "naming_suggest": (
        "You are a naming suggester. Given code context, "
        "suggest suitable variable/function/class names."
        "\nOutput JSON: {\"names\": [\"candidate1\", \"candidate2\"]}"
    ),
}


class OllamaChat:
    """Ollama 聊天客户端——封装 /api/chat，用于本地轻量推理。"""

    def __init__(
        self,
        model: str = INFERENCE_MODEL,
        ollama_url: str = DEFAULT_OLLAMA_URL,
        temperature: float = INFERENCE_TEMPERATURE,
        max_tokens: int = INFERENCE_MAX_TOKENS,
        timeout_s: float = INFERENCE_TIMEOUT_S,
    ) -> None:
        self._model = model
        self._url = ollama_url.rstrip("/")
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._timeout = timeout_s
        self._verified = False

    @property
    def model(self) -> str:
        return self._model

    @property
    def available(self) -> bool:
        try:
            self._verify()
            return self._verified
        except Exception:
            return False

    def ask(
        self,
        prompt: str,
        *,
        system: str = "",
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        _mt = max_tokens if max_tokens is not None else self._max_tokens
        return self._chat(messages, temperature=temperature, max_tokens=_mt)

    def ask_json(
        self,
        prompt: str,
        *,
        system: str = "",
        fields: list[str] | None = None,
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        raw = self.ask(
            prompt,
            system=(system or "始终输出合法的 JSON，不要输出额外文本。"),
            temperature=temperature,
        )
        return self._parse_json(raw, fields)

    def inference(
        self,
        work_type: str,
        text: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        system = SYSTEM_PROMPTS.get(work_type, "Always output valid JSON.")
        if work_type in ("summary_extraction", "anomaly_triage", "query_rewrite"):
            result = self.ask_json(text, system=system)
            return {"work_type": work_type, "model": self._model, "result": result}
        if work_type == "task_classification":
            raw = self._ask_with_retry(text, system, work_type, temperature=0.0)
            return {"work_type": work_type, "model": self._model, "category": raw.strip().lower()}
        if work_type == "tag_completion":
            raw = self._ask_with_retry(text, system, work_type, temperature=0.0)
            parsed = self._parse_json(raw)
            return {"work_type": work_type, "model": self._model, "tags": parsed.get("tags", [])}
        if work_type == "naming_suggest":
            raw = self._ask_with_retry(text, system, work_type, temperature=0.3)
            parsed = self._parse_json(raw)
            return {"work_type": work_type, "model": self._model, "names": parsed.get("names", [])}
        return {"work_type": work_type, "model": self._model, "error": f"unknown work_type: {work_type}"}

    def _ask_with_retry(
        self,
        prompt: str,
        system: str,
        work_type: str,
        *,
        temperature: float = 0.0,
        max_retries: int = 2,
    ) -> str:
        for attempt in range(max_retries):
            raw = self.ask(prompt, system=system, temperature=temperature)
            if raw and len(raw.strip()) > 0:
                return raw
            if attempt < max_retries - 1:
                _log.warning("OllamaChat: %s empty response attempt %d/%d, retrying...", work_type, attempt + 1, max_retries)
        _log.warning("OllamaChat: %s all %d attempts returned empty", work_type, max_retries)
        return "{}"

    @property
    def supported_work_types(self) -> frozenset[str]:
        return frozenset(SYSTEM_PROMPTS.keys())

    def _chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        import requests

        body: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "stream": False,
        }
        options: dict[str, Any] = {}
        t = temperature if temperature is not None else self._temperature
        if t >= 0:
            options["temperature"] = t
        mt = max_tokens if max_tokens is not None else 0
        if mt > 0:
            options["num_predict"] = mt
        if options:
            body["options"] = options

        try:
            self._budget_preflight(len(messages))
            resp = requests.post(
                f"{self._url}/api/chat",
                json=body,
                timeout=self._timeout,
            )
            resp.raise_for_status()
            payload = resp.json()
        except Exception as exc:
            _log.error("OllamaChat failed model=%s: %s", self._model, exc)
            raise

        content = payload.get("message", {}).get("content", "")
        content = self._strip_think_block(content)
        return content

    def _budget_preflight(self, msg_count: int) -> None:
        try:
            from zephyr.governance.budget_engine import BudgetEngine
            engine = BudgetEngine()
            est_tokens = msg_count * 500
            result = engine.pre_flight_check(
                request_id=f"ollama:{self._model}",
                estimated_tokens=est_tokens,
                estimated_cost=0.0,
            )
            if result.decision.name == "DENY":
                raise RuntimeError(f"BudgetEngine DENY: {result.reason}")
        except ImportError:
            pass
        except RuntimeError:
            raise
        except Exception:
            pass

    @staticmethod
    def _strip_think_block(text: str) -> str:
        """qwen3 思考块剥离——移除 response...response 标签对，只保留实际输出。"""
        if not text:
            return text
        stripped = re.sub(r"\x3cthink\x3e[\s\S]*?\x3c\x2fthink\x3e", "", text, flags=re.IGNORECASE)
        return stripped.strip()

    @staticmethod
    def _parse_json(raw: str, expected_keys: list[str] | None = None) -> dict[str, Any]:
        text = raw.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:])
            if text.endswith("```"):
                text = text[:-3]

        for attempt in range(3):
            try:
                result = json.loads(text)
                if isinstance(result, dict):
                    if expected_keys:
                        missing = [k for k in expected_keys if k not in result]
                        if missing:
                            _log.debug("JSON parse missing keys: %s", missing)
                    return result
                return {}
            except json.JSONDecodeError:
                if attempt == 0:
                    text = text[text.index("{") if "{" in text else 0:]
                    text = text[:text.rindex("}") + 1] if "}" in text else text
                else:
                    break
        _log.warning("OllamaChat JSON parse failed; raw=%s", raw[:200])
        return {}

    @staticmethod
    def quick_alive(url: str = DEFAULT_OLLAMA_URL, timeout_s: float = 2.0) -> bool:
        try:
            import requests
            resp = requests.get(f"{url.rstrip('/')}/api/tags", timeout=timeout_s)
            return resp.status_code == 200
        except Exception:
            return False

    def _verify(self) -> None:
        if self._verified:
            return
        if not self.quick_alive(self._url):
            raise RuntimeError(f"Ollama not reachable at {self._url}")
        result = self.ask("回复 pong")
        if result and len(result) > 0:
            self._verified = True
            _log.info("OllamaChat: %s verified", self._model)
        else:
            raise RuntimeError(f"OllamaChat verification failed for {self._model}, got: {result[:80]!r}")

    def shutdown(self) -> None:
        self._verified = False
