# [BLUEPRINT] MOD-INF-034 | 03_modules/_cross_layer/model-profiler/blueprint.md | §

# [MODULE] zephyr.pipeline.model_profiler.deepseek_v4_chat

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
DeepSeekV4Chat --- DeepSeek V4 系列模型 API 客户端
================================================
通过 OpenAI SDK 调用 DeepSeek API，支持思考/非思考模式切换。

模型:
    - deepseek-v4-flash: 快速模型 (1元/M输入, 2元/M输出)
    - deepseek-v4-pro:   旗舰模型 (3元/M输入, 6元/M输出, 2.5折优惠)

思考模式:
    - thinking=True (默认): 模型先输出思维链，再输出最终答案
    - thinking=False: 直接输出答案，不输出思维链

用法:
    chat = DeepSeekV4Chat(model="deepseek-v4-pro", api_key="sk-...", thinking=True)
    result = chat.inference("task_classification", "这段代码有什么问题?")
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
import time
from typing import Any

_log = logging.getLogger(__name__)

_win32_ver_patched = False


def _patch_win32_ver() -> None:
    global _win32_ver_patched
    if _win32_ver_patched:
        return
    if sys.platform != "win32":
        _win32_ver_patched = True
        return
    try:
        import platform as _plat
        _orig = _plat.win32_ver
        if getattr(_orig, "_patched", False):
            _win32_ver_patched = True
            return

        def _safe_win32_ver():
            try:
                return ("10", "10.0.19045", "SP0", "Multiprocessor Free")
            except Exception:
                return ("10", "", "", "")

        _safe_win32_ver._patched = True  # type: ignore[attr-defined]
        _plat.win32_ver = _safe_win32_ver
    except Exception:
        pass
    _win32_ver_patched = True

DEFAULT_BASE_URL = "https://api.deepseek.com"

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
    "code_fix": (
        "You are a code fixer. Given source code and a problem description, "
        "output the exact old code (old_str) and its replacement (new_str). "
        "Only output changes that are necessary and minimal. "
        "Be precise: old_str must exactly match the source text including whitespace. "
        "Do NOT include reasoning or thinking. Output ONLY the JSON."
        "\nOutput JSON: {\"fixes\": [{\"old_str\": \"exact source\", \"new_str\": \"replacement\", \"reason\": \"brief\"}]}"
    ),
    "refactor": (
        "You are a code refactorer. Given source code, "
        "suggest improvements: simplify logic, extract functions, rename variables, "
        "improve readability. Output exact old_str → new_str replacements."
        "\nOutput JSON: {\"changes\": [{\"old_str\": \"exact source\", \"new_str\": \"improved code\", \"reason\": \"brief\"}]}"
    ),
    "code_generate": (
        "You are a code generator. Given a specification or requirement, "
        "generate complete, well-structured Python code. Include imports, docstrings, "
        "and proper typing. "
        "Do NOT include reasoning or thinking. Output ONLY the JSON."
        "\nOutput JSON: {\"file_path\": \"suggested/filename.py\", \"content\": \"full code here\", \"description\": \"brief\"}"
    ),
    "dead_code_removal": (
        "You are a dead code detector. Given source code, "
        "identify unused imports, unreachable code blocks, dead functions, "
        "or redundant logic. Output the exact lines that should be removed. "
        "Do NOT include reasoning or thinking. Output ONLY the JSON."
        "\nOutput JSON: {\"dead_sections\": [{\"old_str\": \"exact dead code\", \"reason\": \"why it's dead\"}]}"
    ),
}

PRICING_RMB: dict[str, dict[str, float]] = {
    "deepseek-v4-flash": {
        "input_per_1M": 1.0,
        "input_cache_hit_per_1M": 0.02,
        "output_per_1M": 2.0,
    },
    "deepseek-v4-pro": {
        "input_per_1M": 3.0,
        "input_cache_hit_per_1M": 0.025,
        "output_per_1M": 6.0,
    },
}


class DeepSeekV4Chat:
    """DeepSeek V4 系列模型客户端——兼容 ExamOrchestrator 的 inference 接口。

    Attributes:
        model_id: 模型标识（deepseek-v4-flash / deepseek-v4-pro）
        thinking: 是否启用思考模式
        cumulative_cost_rmb: 累计费用（人民币元）
        cumulative_input_tokens: 累计输入 token 数
        cumulative_output_tokens: 累计输出 token 数
    """

    def __init__(
        self,
        model: str = "deepseek-v4-pro",
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        thinking: bool = True,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        timeout_s: float = 120.0,
    ) -> None:
        self._model = model
        self._api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self._base_url = base_url.rstrip("/")
        self._thinking = thinking
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._timeout = timeout_s

        self.cumulative_cost_rmb: float = 0.0
        self.cumulative_input_tokens: int = 0
        self.cumulative_output_tokens: int = 0
        self.call_count: int = 0

        self._pricing = PRICING_RMB.get(model, PRICING_RMB["deepseek-v4-pro"])

    @property
    def model(self) -> str:
        return f"{self._model}{'-thinking' if self._thinking else '-non-thinking'}"

    @property
    def model_id(self) -> str:
        return self.model

    def _get_client(self):
        _patch_win32_ver()
        from openai import OpenAI
        return OpenAI(base_url=self._base_url, api_key=self._api_key)

    def _chat(self, messages: list[dict[str, str]]) -> str:
        client = self._get_client()

        extra_body = {"thinking": {"type": "enabled" if self._thinking else "disabled"}}
        kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "max_tokens": self._max_tokens,
            "extra_body": extra_body,
        }

        if not self._thinking:
            kwargs["temperature"] = self._temperature

        response = client.chat.completions.create(**kwargs)

        usage = response.usage
        input_tokens = getattr(usage, "prompt_tokens", 0) or 0
        output_tokens = getattr(usage, "completion_tokens", 0) or 0

        self.cumulative_input_tokens += input_tokens
        self.cumulative_output_tokens += output_tokens
        self.call_count += 1

        cost = (
            input_tokens / 1_000_000.0 * self._pricing["input_per_1M"]
            + output_tokens / 1_000_000.0 * self._pricing["output_per_1M"]
        )
        self.cumulative_cost_rmb += cost

        content = response.choices[0].message.content or ""

        _log.debug(
            "DeepSeekV4Chat %s thinking=%s: input=%d output=%d cost=%.6f元",
            self._model, self._thinking, input_tokens, output_tokens, cost,
        )

        return content

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
        saved_mt = self._max_tokens
        self._max_tokens = _mt
        try:
            return self._chat(messages)
        finally:
            self._max_tokens = saved_mt

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
            return {
                "work_type": work_type,
                "model": self.model,
                "result": result,
                "token_count": self.cumulative_output_tokens,
                "eval_count": self.cumulative_output_tokens,
            }
        if work_type == "task_classification":
            raw = self._ask_with_retry(text, system, work_type, temperature=0.0)
            return {
                "work_type": work_type,
                "model": self.model,
                "category": raw.strip().lower(),
                "token_count": self.cumulative_output_tokens,
                "eval_count": self.cumulative_output_tokens,
            }
        if work_type == "tag_completion":
            raw = self._ask_with_retry(text, system, work_type, temperature=0.0)
            parsed = self._parse_json(raw)
            return {
                "work_type": work_type,
                "model": self.model,
                "tags": parsed.get("tags", []),
                "token_count": self.cumulative_output_tokens,
                "eval_count": self.cumulative_output_tokens,
            }
        if work_type == "naming_suggest":
            raw = self._ask_with_retry(text, system, work_type, temperature=0.3)
            parsed = self._parse_json(raw)
            return {
                "work_type": work_type,
                "model": self.model,
                "names": parsed.get("names", []),
                "token_count": self.cumulative_output_tokens,
                "eval_count": self.cumulative_output_tokens,
            }
        if work_type == "code_fix":
            raw = self._ask_with_retry(text, system, work_type, temperature=0.0)
            parsed = self._parse_json(raw)
            return {
                "work_type": work_type,
                "model": self.model,
                "fixes": parsed.get("fixes", []),
                "token_count": self.cumulative_output_tokens,
                "eval_count": self.cumulative_output_tokens,
            }
        if work_type == "refactor":
            raw = self._ask_with_retry(text, system, work_type, temperature=0.2)
            parsed = self._parse_json(raw)
            return {
                "work_type": work_type,
                "model": self.model,
                "changes": parsed.get("changes", []),
                "token_count": self.cumulative_output_tokens,
                "eval_count": self.cumulative_output_tokens,
            }
        if work_type == "code_generate":
            raw = self._ask_with_retry(text, system, work_type, temperature=0.1)
            parsed = self._parse_json(raw)
            return {
                "work_type": work_type,
                "model": self.model,
                "codegen": parsed,
                "token_count": self.cumulative_output_tokens,
                "eval_count": self.cumulative_output_tokens,
            }
        if work_type == "dead_code_removal":
            raw = self._ask_with_retry(text, system, work_type, temperature=0.0)
            parsed = self._parse_json(raw)
            return {
                "work_type": work_type,
                "model": self.model,
                "dead_sections": parsed.get("dead_sections", []),
                "token_count": self.cumulative_output_tokens,
                "eval_count": self.cumulative_output_tokens,
            }
        return {
            "work_type": work_type,
            "model": self.model,
            "error": f"unknown work_type: {work_type}",
        }

    def _ask_with_retry(
        self,
        prompt: str,
        system: str,
        work_type: str,
        *,
        temperature: float = 0.0,
        max_retries: int = 3,
    ) -> str:
        import time as _time
        for attempt in range(max_retries):
            try:
                raw = self.ask(prompt, system=system, temperature=temperature)
                if raw and len(raw.strip()) > 0:
                    return raw
                if attempt < max_retries - 1:
                    _log.warning(
                        "DeepSeekV4Chat: %s empty response attempt %d/%d, retrying...",
                        work_type, attempt + 1, max_retries,
                    )
                    _time.sleep(1.0)
            except Exception as exc:
                if attempt < max_retries - 1:
                    _log.warning(
                        "DeepSeekV4Chat: %s error attempt %d/%d: %s, retrying...",
                        work_type, attempt + 1, max_retries, exc,
                    )
                    _time.sleep(2.0)
                else:
                    _log.error(
                        "DeepSeekV4Chat: %s all %d attempts failed: %s",
                        work_type, max_retries, exc,
                    )
        _log.warning("DeepSeekV4Chat: %s all %d attempts returned empty", work_type, max_retries)
        return "{}"

    @property
    def supported_work_types(self) -> frozenset[str]:
        return frozenset(SYSTEM_PROMPTS.keys())

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
        _log.warning("DeepSeekV4Chat JSON parse failed; raw=%s", raw[:200])
        return {}

    @staticmethod
    def _strip_think_block(text: str) -> str:
        if not text:
            return text
        stripped = re.sub(
            r"\x3cthink\x3e[\s\S]*?\x3c\x2fthink\x3e",
            "",
            text,
            flags=re.IGNORECASE,
        )
        return stripped.strip()

    def reset_cost_counters(self) -> None:
        self.cumulative_cost_rmb = 0.0
        self.cumulative_input_tokens = 0
        self.cumulative_output_tokens = 0
        self.call_count = 0