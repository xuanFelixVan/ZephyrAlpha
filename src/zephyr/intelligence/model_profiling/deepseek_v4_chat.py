# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] zephyr.intelligence.model_profiling.deepseek_v4_chat
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES]
# [CONSUMERS] MOD-INF-034
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] DeepSeekV4API客户端;思考/非思考模式;费用追踪
# [MODIFY-GUARD] docs/03_modules/_cross_layer/model_profiler/blueprint.md;src/zephyr/intelligence/model_profiling/__init__.py
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] APIError;RateLimitError;CostLimitError
# [TESTS] tests/test_model_profiler/
# [A_module] module_id=MOD-RSC_deepseek_v4_chat | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

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
    chat = DeepSeekV4Chat(model="deepseek-v4-pro", api_key=os.environ["DEEPSEEK_API_KEY"], thinking=True)
    result = chat.inference("task_classification", "这段代码有什么问题?")
"""

from __future__ import annotations

import json
import logging
import os
import random as _random
import re
import sys
import time as _time
from typing import Any

from zephyr.shared.security.secrets import get_secret_or_default

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
    except Exception as exc:
        _log.debug("win32_ver patch failed: %s", exc, exc_info=True)
    _win32_ver_patched = True


DEFAULT_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

SYSTEM_PROMPTS: dict[str, str] = {
    "task_classification": (
        "You are a task classifier. Classify the input module/code into one of: "
        "web, config, data, logic, utility, test, other."
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
    "code_fix": (
        "You are a code fixer. Given source code and a problem description, "
        "output the exact old code (old_str) and its replacement (new_str). "
        "Only output changes that are necessary and minimal. "
        "Be precise: old_str must exactly match the source text including whitespace. "
        "Do NOT include reasoning or thinking. Output ONLY the JSON."
        '\nOutput JSON: {"fixes": [{"old_str": "exact source", "new_str": "replacement", "reason": "brief"}]}'
    ),
    "refactor": (
        "You are a code refactorer. Given source code, "
        "suggest improvements: simplify logic, extract functions, rename variables, "
        "improve readability. Output exact old_str → new_str replacements."
        '\nOutput JSON: {"changes": [{"old_str": "exact source", "new_str": "improved code", "reason": "brief"}]}'
    ),
    "code_generate": (
        "You are a code generator. Given a specification or requirement, "
        "generate complete, well-structured Python code. Include imports, docstrings, "
        "and proper typing. "
        "Do NOT include reasoning or thinking. Output ONLY the JSON."
        '\nOutput JSON: {"file_path": "suggested/filename.py", "content": "full code here", "description": "brief"}'
    ),
    "dead_code_removal": (
        "You are a dead code detector. Given source code, "
        "identify unused imports, unreachable code blocks, dead functions, "
        "or redundant logic. Output the exact lines that should be removed. "
        "Do NOT include reasoning or thinking. Output ONLY the JSON."
        '\nOutput JSON: {"dead_sections": [{"old_str": "exact dead code", "reason": "why it\'s dead"}]}'
    ),
    # ── v3.0.6: 补全 21 个缺失能力 prompt（对齐 OllamaChat） ──────
    "architecture_design": (
        "You are a software architect. Given a requirement, design the file structure and dependencies. "
        "List each file with its responsibility and which other files it depends on. "
        "Be specific about module separation and dependency direction."
        '\nOutput JSON: {"files": [{"name": "filename.py", "responsibility": "what it does", "depends_on": ["other.py"]}], "dependencies": [{"from": "a.py", "to": "b.py", "type": "import"}]}'
    ),
    "cross_file_refactor": (
        "You are a cross-file refactoring specialist. Given multiple source files and a rename operation, "
        "output the exact changes needed for EACH file. Include old_str and new_str for every modification. "
        "Do NOT miss any call site."
        '\nOutput JSON: {"changes": [{"file": "filename.py", "old_str": "exact source", "new_str": "replacement", "reason": "brief"}]}'
    ),
    "dependency_trace": (
        "You are a dependency chain tracer. Given multiple source files and a starting function, "
        "trace the complete call chain through all files. List every function call in order, "
        "including the file where each function is defined."
        '\nOutput JSON: {"call_chain": [{"step": 1, "function": "func_name", "file": "filename.py", "calls": "next_func"}]}'
    ),
    "context_consistency": (
        "You are a consistency checker. Given two or more statements from a technical document, "
        "determine if they are consistent with each other. Identify any contradictions."
        '\nOutput JSON: {"consistent": false, "conflicts": [{"statement1": "...", "statement2": "...", "reason": "why they conflict"}]}'
    ),
    "hallucination_detect": (
        "You are a hallucination detector for code analysis. Given a technical report that references "
        "files, functions, and modules, identify which references appear to be fabricated (hallucinated) "
        "vs which are likely real. Look for names that follow common patterns but don't match standard libraries."
        '\nOutput JSON: {"hallucinations": [{"item": "fabricated_name", "reason": "why it appears fabricated"}], "verified": [{"item": "real_name", "reason": "why it appears real"}]}'
    ),
    "long_context_recall": (
        "You are a long context recall tester. You will be given a long technical document. "
        "After reading it, answer the specific question about information from the BEGINNING of the document. "
        "Be precise and quote the exact value or name mentioned at the start."
        '\nOutput JSON: {"answer": "exact answer from the beginning of the document", "source_location": "beginning"}'
    ),
    "rule_comprehension": (
        "You are a rule compliance checker. Given a project rule and a code scenario, "
        "determine if the scenario complies with the rule. Identify specific violations."
        '\nOutput JSON: {"compliant": false, "violations": [{"rule": "rule name", "violation": "what is wrong"}]}'
    ),
    "safety_judgment": (
        "You are a file safety judge. Given a list of files with their AI_AUTONOMY tags "
        "(immutable_core=AI cannot modify, human_gated=needs approval, ai_modifiable=AI can modify), "
        "classify each file as modifiable or blocked."
        '\nOutput JSON: {"modifiable": ["file1.py"], "blocked": ["file2.py"], "reasons": [{"file": "file2.py", "reason": "immutable_core"}]}'
    ),
    "code_edit_precision": (
        "You are a code edit precision specialist. Given source code and a change request, "
        "output the EXACT old_str (text to find) and new_str (replacement). "
        "The old_str must match the source exactly character-by-character. "
        "Do NOT include reasoning or thinking. Output ONLY the JSON."
        '\nOutput JSON: {"fixes": [{"old_str": "exact text", "new_str": "replacement", "reason": "brief"}]}'
    ),
    "self_review": (
        "You are a code self-reviewer. Given code that may contain bugs, check if the code "
        "matches its documented behavior. Identify any bugs, their locations, and fixes."
        '\nOutput JSON: {"has_bug": true, "bugs": [{"location": "line or expression", "description": "what is wrong", "fix": "how to fix"}]}'
    ),
    "incremental_execution": (
        "You are an incremental task executor. Given a multi-step plan, execute each step "
        "in order. Output the result of each step. Do not skip steps."
        '\nOutput JSON: {"steps": [{"step": 1, "action": "what was done", "result": "outcome"}]}'
    ),
    "error_recovery": (
        "You are an error recovery specialist. Given an error message and context, "
        "diagnose the root cause and provide a fix. Be specific about the root cause."
        '\nOutput JSON: {"diagnosis": "what went wrong", "root_cause": "underlying reason", "fix": "how to fix"}'
    ),
    "ambiguity_detect": (
        "You are an ambiguity detector. Given an instruction, determine if it is ambiguous. "
        "If so, identify which aspects are unclear and what questions need to be asked."
        '\nOutput JSON: {"ambiguous": true, "ambiguities": [{"aspect": "what is unclear", "question": "what to ask"}]}'
    ),
    "tool_selection": (
        "You are a tool selection advisor. Given a task description, recommend the most "
        "appropriate tool. Common tools: Read (read file), Grep (search content), Glob (find files), "
        "Edit (modify file), Write (create file)."
        '\nOutput JSON: {"tool": "ToolName", "reason": "why this tool"}'
    ),
    "function_calling": (
        "You are a function calling expert. Given a task, generate the exact tool call "
        "with function name and arguments. Tools: Read(file_path), Grep(pattern, path), "
        "Glob(pattern, path), Edit(file_path, old_str, new_str), Write(file_path, content)."
        '\nOutput JSON: {"function": "ToolName", "arguments": {"key": "value"}}'
    ),
    "tool_chaining": (
        "You are a tool chaining planner. Given a multi-step task, plan the ordered sequence "
        "of tool calls. Each step has a tool name. Tools: Read, Grep, Glob, Edit, Write."
        '\nOutput JSON: {"steps": [{"tool": "ToolName", "purpose": "why"}]}'
    ),
    "impact_analysis": (
        "You are an impact analysis expert. Given a code change and project structure, "
        "identify ALL files that will be affected by the change. Consider direct imports, "
        "indirect dependencies, and test files."
        '\nOutput JSON: {"affected_files": ["file1.py", "file2.py"], "impact_summary": "brief"}'
    ),
    "circular_dependency_detect": (
        "You are a circular dependency detector. Analyze the given module imports and "
        "determine if any circular dependencies exist. Report the cycle path if found."
        '\nOutput JSON: {"has_cycle": true/false, "cycle_path": ["module1", "module2"], "explanation": "brief"}'
    ),
    "rollback_boundary_design": (
        "You are a rollback boundary designer. Given a set of file changes, design safe "
        "rollback points and boundaries. Consider data migrations, schema changes, and "
        "irreversible operations."
        '\nOutput JSON: {"rollback_points": ["point1", "point2"], "boundaries": ["file1.py"]}'
    ),
    "task_decomposition": (
        "You are a task decomposition expert. Break down complex tasks into smaller, "
        "executable subtasks. Each subtask should be independently verifiable and have "
        "clear file scope."
        '\nOutput JSON: {"tasks": [{"name": "task1", "files": ["file1.py"], "description": "brief"}]}'
    ),
    "parallel_planning": (
        "You are a parallel planning expert. Given a set of tasks with dependencies, "
        "identify which tasks can run in parallel and which must be sequential."
        '\nOutput JSON: {"parallel_groups": [["task1", "task2"], ["task3"]], "sequential": ["task4"]}'
    ),
    "dependency_ordering": (
        "You are a dependency ordering expert. Given tasks with dependencies, provide "
        "the correct execution order that respects all dependencies."
        '\nOutput JSON: {"order": ["task1", "task2", "task3"], "dependencies": [{"from": "task1", "to": "task2"}]}'
    ),
    "cross_file_hallucination_detect": (
        "You are a cross-file hallucination detector. Analyze claims about files and "
        "functions to identify any hallucinated (nonexistent) files, functions, or imports. "
        "Be thorough and check every claim."
        '\nOutput JSON: {"has_hallucination": true/false, "hallucinated_items": ["item1", "item2"], "explanation": "brief"}'
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
        self._api_key = api_key or get_secret_or_default("DEEPSEEK_API_KEY", "")
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

    # 5.110.2 修复: 显式 __repr__ 排除 _api_key, 防止调试/日志泄露
    def __repr__(self) -> str:
        return (
            f"DeepSeekV4Chat(model={self._model!r}, thinking={self._thinking!r}, "
            f"call_count={self.call_count!r}, cumulative_cost_rmb={self.cumulative_cost_rmb!r})"
        )

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
            self._model,
            self._thinking,
            input_tokens,
            output_tokens,
            cost,
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
        # v3.0.7: 通用 fallback——对所有有 SYSTEM_PROMPT 但无显式分支的 work_type，
        # 调用模型并解析 JSON，展开到顶层以通过 _check_structure 的结构检查。
        # 修复 breadth 暴跌：原 return error 导致 21 个能力 breadth 全失败。
        raw = self._ask_with_retry(text, system, work_type, temperature=0.1)
        parsed = self._parse_json(raw)
        result: dict[str, Any] = {
            "work_type": work_type,
            "model": self.model,
            "token_count": self.cumulative_output_tokens,
            "eval_count": self.cumulative_output_tokens,
        }
        result.update(parsed)
        return result

    def _ask_with_retry(
        self,
        prompt: str,
        system: str,
        work_type: str,
        *,
        temperature: float = 0.0,
        max_retries: int = 3,
    ) -> str:
        for attempt in range(max_retries):
            try:
                raw = self.ask(prompt, system=system, temperature=temperature)
                if raw and len(raw.strip()) > 0:
                    return raw
                if attempt < max_retries - 1:
                    _log.warning(
                        "DeepSeekV4Chat: %s empty response attempt %d/%d, retrying...",
                        work_type,
                        attempt + 1,
                        max_retries,
                    )
                    # 5.72.3 修复：exponential backoff + jitter 替代固定延迟
                    _delay = (2 ** attempt) + _random.uniform(0, 1)
                    _time.sleep(_delay)
            except Exception as exc:
                if attempt < max_retries - 1:
                    _log.warning(
                        "DeepSeekV4Chat: %s error attempt %d/%d: %s, retrying...",
                        work_type,
                        attempt + 1,
                        max_retries,
                        exc, exc_info=True
                    )
                    # 5.72.3 修复：exponential backoff + jitter 替代固定延迟
                    _delay = (2 ** attempt) + _random.uniform(0, 1)
                    _time.sleep(_delay)
                else:
                    _log.error(
                        "DeepSeekV4Chat: %s all %d attempts failed: %s",
                        work_type,
                        max_retries,
                        exc, exc_info=True
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
                _log.warning("JSON parse result is not a dict (type=%s), returning empty dict", type(result).__name__)
                return {}
            except json.JSONDecodeError:
                if attempt == 0:
                    text = text[text.index("{") if "{" in text else 0 :]
                    text = text[: text.rindex("}") + 1] if "}" in text else text
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
