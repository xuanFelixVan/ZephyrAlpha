# [BLUEPRINT] MOD-INF-042 | docs/03_modules/_domain_integration/blueprint.md | §3.1
# [MODULE] zephyr.integration.local_model.deepseek_chat
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS] auto_runtime_core.py; local_model_scheduler.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 使用requests库绕过openai SSL问题;接口兼容OllamaChat
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] API失败时抛RuntimeError;JSON解析失败返回空dict
# [TESTS] tests/test_integration/test_deepseek_chat.py
# [A_module] module_id=MOD-INT_deepseek_chat | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
DeepSeekChat — 通过 DeepSeek API 进行 LLM 推理（requests 实现）
==============================================================
使用 requests 库直接调用 DeepSeek API，绕过 openai 库的 SSL 证书加载卡死问题。
接口与 OllamaChat 完全兼容，可作为 LocalModelScheduler 的推理后端直接替换。

模型:
    - deepseek-v4-flash: 快速模型（默认，低成本）
    - deepseek-v4-pro:   旗舰模型（深度推理，高成本）

用法
----
    chat = DeepSeekChat(model="deepseek-v4-flash")
    reply = chat.ask("这段代码有什么问题？", system="你是代码审查助手")
    result = chat.inference("task_classification", "修复登录bug")
"""

from __future__ import annotations

import logging
from typing import Final

import json
import os
import random
import re
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any
from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)
from zephyr.shared.security.secrets import get_secret_or_default

if TYPE_CHECKING:
    from zephyr.governance.ops_governance.budget_engine import BudgetEngineProtocol

_log = logging.getLogger(__name__)

DEFAULT_BASE_URL: Final[str] = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
# 5.141.1 修复: 模型名通过环境变量外部化, 避免硬编码
DEFAULT_MODEL: Final[str] = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
INFERENCE_TEMPERATURE: Final[float] = 0.1
INFERENCE_MAX_TOKENS: Final[int] = 1024
INFERENCE_TIMEOUT_S: Final[float] = 60.0

SYSTEM_PROMPTS: Final[dict[str, str]] = {
    "task_classification": (
        "You are a task classifier. Classify the input task into one of: "
        "audit, compliance, cleanup, repair, codegen, review, analysis, other."
        "\nOutput only the classification label, no explanation."
    ),
    "tag_completion": (
        "You are a tag generator. Given a task description, "
        "infer appropriate tag labels. Tags should be single English words."
        '\nOutput JSON: {"tags": ["tag1", "tag2"]}'
    ),
    "summary_extraction": (
        "You are a summary extractor. Compress the input text into 3 key points, "
        "each point under 50 characters."
        '\nOutput JSON: {"points": ["point1", "point2", "point3"]}'
    ),
    "anomaly_triage": (
        "You are an anomaly triager. Determine whether the input audit/log result is suspicious, "
        "and whether human intervention is needed."
        '\nOutput JSON: {"needs_human": true/false, "reason": "one-line reason"}'
    ),
    "query_rewrite": (
        "You are a search optimizer. Rewrite the user's natural language search query "
        "into more precise technical search terms, removing filler words and "
        "retaining core technical concepts."
        '\nOutput JSON: {"rewritten": "optimized query"}'
    ),
    "naming_suggest": (
        "You are a naming suggester. Given code context, "
        "suggest suitable variable/function/class names."
        '\nOutput JSON: {"names": ["candidate1", "candidate2"]}'
    ),
}

_env_loaded = False


def _load_env() -> None:
    """从项目根目录的 .env 文件加载环境变量（不依赖 python-dotenv）。"""
    global _env_loaded
    if _env_loaded:
        return
    _env_loaded = True
    env_path = REPO_ROOT / ".env"
    if not env_path.exists():
        return
    try:
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    except Exception as exc:
        _log.debug("DeepSeekChat: .env load skipped: %s", exc, exc_info=True)


class DeepSeekChat:
    """DeepSeek API 聊天客户端——使用 requests 库，接口兼容 OllamaChat。"""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        api_key: str | None = None,
        base_url: str | None = None,
        temperature: float = INFERENCE_TEMPERATURE,
        max_tokens: int = INFERENCE_MAX_TOKENS,
        timeout_s: float = INFERENCE_TIMEOUT_S,
        budget_engine: BudgetEngineProtocol | None = None,
    ) -> None:
        _load_env()
        self._model = model
        self._api_key = api_key or get_secret_or_default("DEEPSEEK_API_KEY", "")
        self._base_url = (base_url or os.getenv("DEEPSEEK_BASE_URL", DEFAULT_BASE_URL)).rstrip("/")
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._timeout = timeout_s
        self._verified = False
        # 5.133.2 DI: 注入 BudgetEngine，避免每次 LLM 调用都硬编码实例化
        self._budget_engine: BudgetEngineProtocol | None = budget_engine

    # 5.110.2 修复: 显式 __repr__ 排除 _api_key, 防止调试/日志泄露
    def __repr__(self) -> str:
        return (
            f"DeepSeekChat(model={self._model!r}, base_url={self._base_url!r}, "
            f"verified={self._verified!r})"
        )

    @property
    def model(self) -> str:
        return self._model

    @property
    def available(self) -> bool:
        """检查 API 是否可用（发送一个最小请求验证）。"""
        if not self._api_key:
            return False
        try:
            result = self.ask("ping", system="Reply with: pong")
            return bool(result and len(result) > 0)
        except Exception as exc:
            _log.debug("DeepSeekChat available check failed: %s", exc, exc_info=True)
            return False

    @property
    def supported_work_types(self) -> frozenset[str]:
        return frozenset(SYSTEM_PROMPTS.keys())

    def ask(
        self,
        prompt: str,
        *,
        system: str = "",
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """发送聊天请求，返回文本响应。"""
        if not self._api_key:
            raise RuntimeError("DEEPSEEK_API_KEY 未设置")

        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        return self._chat(
            messages,
            temperature=temperature if temperature is not None else self._temperature,
            max_tokens=max_tokens if max_tokens is not None else self._max_tokens,
        )

    def ask_json(
        self,
        prompt: str,
        *,
        system: str = "",
        fields: list[str] | None = None,
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        """发送聊天请求并解析 JSON 响应。"""
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
        """根据 work_type 路由推理任务——接口与 OllamaChat.inference 兼容。"""
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
            try:
                raw = self.ask(prompt, system=system, temperature=temperature)
                if raw and len(raw.strip()) > 0:
                    return raw
                if attempt < max_retries - 1:
                    _log.warning(
                        "DeepSeekChat: %s empty response attempt %d/%d, retrying...",
                        work_type, attempt + 1, max_retries,
                    )
            except Exception as exc:
                if attempt < max_retries - 1:
                    _log.warning(
                        "DeepSeekChat: %s error attempt %d/%d: %s, retrying...",
                        work_type, attempt + 1, max_retries, exc,
                        exc_info=True,
                    )
                else:
                    raise
            # 5.72.1 修复：exponential backoff + jitter 避免请求风暴
            if attempt < max_retries - 1:
                delay = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(delay)
        _log.warning("DeepSeekChat: %s all %d attempts returned empty", work_type, max_retries)
        return "{}"

    def _chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.1,
        max_tokens: int = 1024,
    ) -> str:
        """使用 requests 库直接调用 DeepSeek API。"""
        import requests

        body: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

        try:
            self._budget_preflight(len(messages))
            resp = requests.post(
                f"{self._base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json=body,
                timeout=self._timeout,
            )
            resp.raise_for_status()
            payload = resp.json()
        except requests.exceptions.HTTPError as exc:
            _log.error("DeepSeekChat HTTP error model=%s: %s", self._model, exc)
            raise RuntimeError(f"DeepSeek API HTTP error: {exc}") from exc
        except requests.exceptions.RequestException as exc:
            _log.error("DeepSeekChat request failed model=%s: %s", self._model, exc)
            raise RuntimeError(f"DeepSeek API request failed: {exc}") from exc

        choices = payload.get("choices", [])
        if not choices:
            _log.warning("DeepSeekChat: empty choices, payload=%s", str(payload)[:200])
            return ""

        content = choices[0].get("message", {}).get("content", "")
        content = self._strip_think_block(content)
        return content

    def _budget_preflight(self, msg_count: int) -> None:
        """预算预检——与 OllamaChat 保持一致。"""
        try:
            engine = self._budget_engine
            if engine is None:
                from zephyr.governance.ops_governance.budget_engine import BudgetEngine

                engine = BudgetEngine()
            est_tokens = msg_count * 500
            result = engine.pre_flight_check(
                request_id=f"deepseek:{self._model}",
                estimated_tokens=est_tokens,
                estimated_cost=0.0,
            )
            if result.decision.name == "DENY":
                raise RuntimeError(f"BudgetEngine DENY: {result.reason}")
        except ImportError:
            pass
        except RuntimeError:
            raise
        except Exception as e:
            logger.warning("suppressed error in deepseek_chat", exc_info=True)

    @staticmethod
    def _strip_think_block(text: str) -> str:
        """移除 <think>...</think> 思考块，只保留实际输出。"""
        if not text:
            return text
        stripped = re.sub(r"\x3cthink\x3e[\s\S]*?\x3c\x2fthink\x3e", "", text, flags=re.IGNORECASE)
        return stripped.strip()

    @staticmethod
    def _parse_json(raw: str, expected_keys: list[str] | None = None) -> dict[str, Any]:
        """解析 JSON 响应，容忍 markdown 代码块包裹。"""
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
        _log.warning("DeepSeekChat JSON parse failed; raw=%s", raw[:200])
        return {}

    def shutdown(self) -> None:
        """清理资源——兼容 OllamaChat 接口。"""
        self._verified = False
