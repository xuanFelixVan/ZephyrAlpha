# [BLUEPRINT] MOD-INF-042 | docs/03_modules/_domain_integration/blueprint.md | §3.1
# [MODULE] zephyr.integration.local_model.ollama_chat
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] auto_runtime_core.py; local_model_scheduler.py; vector_memory_server.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] _budget_preflight DENY 时抛 RuntimeError; _chat 网络失败时抛异常
# [TESTS]
# [A_module] module_id=MOD-INT_ollama_chat | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

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

from typing import Final
logger = logging.getLogger(__name__)

from http import HTTPStatus

import json
import logging
import os
import random
import re
import time
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zephyr.governance.ops_governance.budget_engine import BudgetEngineProtocol

_log = logging.getLogger(__name__)

DEFAULT_OLLAMA_URL: Final[str] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# 5.141.1 修复: 模型名通过环境变量外部化, 避免硬编码
INFERENCE_MODEL: Final[str] = os.getenv("OLLAMA_INFERENCE_MODEL", "qwen3:8b")
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
    "cross_file_analysis": (
        "You are a cross-file dependency analyzer. Given multiple source files and a proposed change, "
        "determine which files need to be modified. Consider imports, function calls, class usage, "
        "and variable references. List every affected file with the reason."
        '\nOutput JSON: {"affected_files": [{"file": "filename.py", "reason": "why it needs changes"}]}'
    ),
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
    "file_edit_precision": (
        "You are a file edit precision specialist. Given file content and a change request, "
        "output the EXACT old_str (text to find) and new_str (replacement). "
        "The old_str must match the source exactly character-by-character."
        '\nOutput JSON: {"edits": [{"old_str": "exact text", "new_str": "replacement"}]}'
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
    "context_freshness_awareness": (
        "You are a context freshness awareness expert. Analyze conversation history to "
        "determine if the context has degraded. Look for contradictions, forgotten "
        "information, and inconsistency."
        '\nOutput JSON: {"context_degraded": true/false, "reason": "brief", "recommendation": "brief"}'
    ),
    "context_window_management": (
        "You are a context window management expert. Given a conversation length and token count, "
        "determine if the context window is being managed efficiently. Recommend actions to "
        "optimize context usage."
        '\nOutput JSON: {"needs_new_session": true/false, "reason": "brief", "recommendation": "brief"}'
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
        budget_engine: BudgetEngineProtocol | None = None,
    ) -> None:
        self._model = model
        self._url = ollama_url.rstrip("/")
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._timeout = timeout_s
        self._verified = False
        # 5.133.2 DI: 注入 BudgetEngine，避免每次 LLM 调用都硬编码实例化
        self._budget_engine: BudgetEngineProtocol | None = budget_engine

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
        # 通用JSON解析逻辑（适用于B/C/D/E/F/G/H/I/J/K/L/M类等所有新增能力）
        raw = self._ask_with_retry(text, system, work_type, temperature=0.0)
        parsed = self._parse_json(raw)
        result: dict[str, Any] = {
            "work_type": work_type,
            "model": self._model,
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
        max_retries: int = 2,
    ) -> str:
        for attempt in range(max_retries):
            try:
                raw = self.ask(prompt, system=system, temperature=temperature)
                if raw and len(raw.strip()) > 0:
                    return raw
                if attempt < max_retries - 1:
                    _log.warning(
                        "OllamaChat: %s empty response attempt %d/%d, retrying...", work_type, attempt + 1, max_retries
                    )
            except Exception as exc:
                if attempt < max_retries - 1:
                    _log.warning(
                        "OllamaChat: %s error attempt %d/%d: %s, retrying...", work_type, attempt + 1, max_retries, exc
, exc_info=True)
                else:
                    raise
            # 5.72.2 修复：exponential backoff + jitter；添加 try/except 捕获异常
            if attempt < max_retries - 1:
                delay = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(delay)
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
            _log.error("OllamaChat failed model=%s: %s", self._model, exc, exc_info=True)
            raise

        content = payload.get("message", {}).get("content", "")
        content = self._strip_think_block(content)
        return content

    def _budget_preflight(self, msg_count: int) -> None:
        try:
            engine = self._budget_engine
            if engine is None:
                from zephyr.governance.ops_governance.budget_engine import BudgetEngine

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
        except Exception as e:
            logger.warning("suppressed error in ollama_chat", exc_info=True)

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
                    text = text[text.index("{") if "{" in text else 0 :]
                    text = text[: text.rindex("}") + 1] if "}" in text else text
                else:
                    break
        _log.warning("OllamaChat JSON parse failed; raw=%s", raw[:200])
        return {}

    @staticmethod
    def quick_alive(url: str = DEFAULT_OLLAMA_URL, timeout_s: float = 2.0) -> bool:
        try:
            import requests

            resp = requests.get(f"{url.rstrip('/')}/api/tags", timeout=timeout_s)
            return resp.status_code == HTTPStatus.OK
        except Exception as e:  # 5.70.4 修复：异常路径添加日志，区分"真阴性"和"异常降级"
            _log.warning("quick_alive failed: %s", e, exc_info=True)
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
