# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] zephyr.intelligence.model_profiling.exam_test_cases
# [DOMAIN] D-INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.model_profiler.__init__
# [CONSUMERS] MOD-INF-034
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 27道标准入职考试题;9能力×3难度
# [MODIFY-GUARD] docs/03_modules/_cross_layer/model-profiler/blueprint.md;src/zephyr/model-profiler/__init__.py
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] TestCaseError
# [TESTS] tests/test_model_profiler/
# [A_module] module_id=MOD-INF_exam_test_cases | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""
ExamTestCases --- 入职考试 27 道标准题

每个能力类型 3 道题, 覆盖 easy/medium/hard 三种难度.
命名空间: EX-{capability_abbr}-{序号}

能力 → 缩写映射:
    task_classification → CL
    tag_completion      → TG
    summary_extraction  → SE
    naming_suggest      → NS
    anomaly_triage      → AT
    code_fix            → CF
    refactor            → RF
    code_generate       → CG
    dead_code_removal   → DC
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class ExamTestCase:
    case_id: str
    capability: str
    difficulty: Difficulty
    prompt: str

    expected_structure_keys: list[str] = field(default_factory=list)
    expected_tags: list[str] = field(default_factory=list)
    expected_category: str = ""
    expected_old_str: str = ""
    expected_new_str: str = ""
    expected_needs_human: bool = False
    expected_contains: list[str] = field(default_factory=list)


EX_CL_001 = ExamTestCase(
    case_id="EX-CL-001",
    capability="task_classification",
    difficulty=Difficulty.EASY,
    prompt="classify this module: hello\nprint('hello world')",
    expected_structure_keys=["category"],
    expected_category="other",
)

EX_CL_002 = ExamTestCase(
    case_id="EX-CL-002",
    capability="task_classification",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "classify this module: api_router\n"
        "from fastapi import APIRouter\n"
        "router = APIRouter()\n"
        "@router.get('/users')\n"
        "def get_users(): return []"
    ),
    expected_structure_keys=["category"],
    expected_category="web",
)

EX_CL_003 = ExamTestCase(
    case_id="EX-CL-003",
    capability="task_classification",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "classify this module: config_loader\n"
        "import os\n"
        "from pathlib import Path\n"
        "def load_config(path: Path) -> dict:\n"
        "    return json.loads(path.read_text())"
    ),
    expected_structure_keys=["category"],
    expected_category="config",
)

EX_TG_001 = ExamTestCase(
    case_id="EX-TG-001",
    capability="tag_completion",
    difficulty=Difficulty.EASY,
    prompt=(
        "generate tags for: ollama_chat\n"
        "class OllamaChat:\n"
        "    def inference(self, work_type, text): ...\n"
        "    def ask(self, message): ..."
    ),
    expected_structure_keys=["tags"],
    expected_tags=["inference", "chat", "llm", "ollama"],
)

EX_TG_002 = ExamTestCase(
    case_id="EX-TG-002",
    capability="tag_completion",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "generate tags for: embedding_router\n"
        "class EmbeddingRouter:\n"
        "    def route(self, query): ...\n"
        "    def warmup(self, model_name): ..."
    ),
    expected_structure_keys=["tags"],
    expected_tags=["embedding", "vector", "semantic", "routing"],
)

EX_TG_003 = ExamTestCase(
    case_id="EX-TG-003",
    capability="tag_completion",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "generate tags for: action_dispatcher\n"
        "class ActionDispatcher:\n"
        "    def dispatch(self, task): ...\n"
        "    def drain_results(self, scheduler): ..."
    ),
    expected_structure_keys=["tags"],
    expected_tags=["dispatch", "action", "runtime", "automation"],
)

EX_SE_001 = ExamTestCase(
    case_id="EX-SE-001",
    capability="summary_extraction",
    difficulty=Difficulty.EASY,
    prompt=(
        "summarize: The ZephyrAlpha project implements a multi-agent runtime "
        "for autonomous software development. It uses FastAPI for REST APIs, "
        "Pydantic for data validation, and Ollama for local LLM inference."
    ),
    expected_structure_keys=["points"],
    expected_contains=["multi-agent", "FastAPI", "Ollama"],
)

EX_SE_002 = ExamTestCase(
    case_id="EX-SE-002",
    capability="summary_extraction",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "summarize: The ActionDispatcher is the brain's hands. After inference "
        "completes, it directly modifies project source files: inserts BRAIN "
        "comment blocks, appends capability card tags, and performs "
        "SearchReplace code modifications with versioned backups."
    ),
    expected_structure_keys=["points"],
    expected_contains=["ActionDispatcher", "source files", "backup"],
)

EX_SE_003 = ExamTestCase(
    case_id="EX-SE-003",
    capability="summary_extraction",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "summarize: The LocalModelScheduler manages a FIFO task queue for "
        "Ollama inference. It supports 9 capability types including "
        "task_classification, tag_completion, code_fix, refactor, "
        "code_generate, and dead_code_removal. It has built-in retry "
        "logic for 500 errors and GPU utilization monitoring."
    ),
    expected_structure_keys=["points"],
    expected_contains=["LocalModelScheduler", "inference", "retry"],
)

EX_NS_001 = ExamTestCase(
    case_id="EX-NS-001",
    capability="naming_suggest",
    difficulty=Difficulty.EASY,
    prompt=("suggest alternative names for module: calc\ndef f(x, y):\n    return x + y"),
    expected_structure_keys=["names"],
    expected_contains=["calculator", "math_utils", "arithmetic"],
)

EX_NS_002 = ExamTestCase(
    case_id="EX-NS-002",
    capability="naming_suggest",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "suggest alternative names for module: proc\n"
        "def run(data: list[dict]) -> list[dict]:\n"
        "    result = []\n"
        "    for item in data:\n"
        "        if item['status'] == 'active':\n"
        "            result.append(item)\n"
        "    return result"
    ),
    expected_structure_keys=["names"],
    expected_contains=["filter", "processor", "active"],
)

EX_NS_003 = ExamTestCase(
    case_id="EX-NS-003",
    capability="naming_suggest",
    difficulty=Difficulty.HARD,
    prompt=(
        "suggest alternative names for module: cache\n"
        "class Cache:\n"
        "    def get(self, key): ...\n"
        "    def set(self, key, value, ttl=3600): ...\n"
        "    def invalidate(self, key): ..."
    ),
    expected_structure_keys=["names"],
    expected_contains=["ttl_cache", "memory_store", "key_value"],
)

EX_AT_001 = ExamTestCase(
    case_id="EX-AT-001",
    capability="anomaly_triage",
    difficulty=Difficulty.EASY,
    prompt="triage: WARNING: orphan module detected: old_script.py",
    expected_structure_keys=["needs_human", "reason"],
    expected_needs_human=False,
)

EX_AT_002 = ExamTestCase(
    case_id="EX-AT-002",
    capability="anomaly_triage",
    difficulty=Difficulty.MEDIUM,
    prompt="triage: CRITICAL: gateway authentication bypass detected in auth_middleware.py",
    expected_structure_keys=["needs_human", "reason"],
    expected_needs_human=True,
)

EX_AT_003 = ExamTestCase(
    case_id="EX-AT-003",
    capability="anomaly_triage",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "triage: ERROR: 500 Internal Server Error in /api/v1/users - "
        "recurring pattern: 15 failures in last 5 minutes. "
        "Traceback: KeyError in user_validator.py line 142."
    ),
    expected_structure_keys=["needs_human", "reason"],
    expected_needs_human=True,
)

EX_CF_001 = ExamTestCase(
    case_id="EX-CF-001",
    capability="code_fix",
    difficulty=Difficulty.EASY,
    prompt=("fix bug: calc\ndef add(a, b):\n    return a - b  # BUG: should be a + b"),
    expected_structure_keys=["fixes"],
    expected_old_str="a - b",
    expected_new_str="a + b",
)

EX_CF_002 = ExamTestCase(
    case_id="EX-CF-002",
    capability="code_fix",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "fix bug: login\n"
        "def check_password(user_input, stored_hash):\n"
        "    if user_input == stored_hash:  # BUG: should hash user_input first\n"
        "        return True\n"
        "    return False"
    ),
    expected_structure_keys=["fixes"],
    expected_old_str="if user_input == stored_hash",
    expected_new_str="if hash(user_input) == stored_hash",
)

EX_CF_003 = ExamTestCase(
    case_id="EX-CF-003",
    capability="code_fix",
    difficulty=Difficulty.HARD,
    prompt=(
        "fix bug: fetcher\n"
        "def fetch_data(url):\n"
        "    resp = requests.get(url)\n"
        "    return resp.json()  # BUG: no error handling, no timeout"
    ),
    expected_structure_keys=["fixes"],
    expected_contains=["try", "except", "timeout"],
)

EX_RF_001 = ExamTestCase(
    case_id="EX-RF-001",
    capability="refactor",
    difficulty=Difficulty.EASY,
    prompt=("refactor: calc\nx = 10\ny = 20\nz = 30\nresult = x + y + z  # magic numbers everywhere"),
    expected_structure_keys=["changes"],
    expected_contains=["constant", "TEN", "MAGIC"],
)

EX_RF_002 = ExamTestCase(
    case_id="EX-RF-002",
    capability="refactor",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "refactor: proc\n"
        "data = [1, 2, 3, 4, 5]\n"
        "result = []\n"
        "for i in range(len(data)):\n"
        "    result.append(data[i] * 2)  # use list comprehension"
    ),
    expected_structure_keys=["changes"],
    expected_contains=["comprehension", "x * 2 for x in"],
)

EX_RF_003 = ExamTestCase(
    case_id="EX-RF-003",
    capability="refactor",
    difficulty=Difficulty.HARD,
    prompt=(
        "refactor: report\n"
        "def gen_report(data):\n"
        "    html = '<html><body>'\n"
        "    for item in data:\n"
        "        html += f'<li>{item}</li>'  # inefficient string concatenation\n"
        "    html += '</body></html>'\n"
        "    return html"
    ),
    expected_structure_keys=["changes"],
    expected_contains=["join", "list", "append"],
)

EX_CG_001 = ExamTestCase(
    case_id="EX-CG-001",
    capability="code_generate",
    difficulty=Difficulty.EASY,
    prompt=(
        "generate: a function called is_prime that takes an integer n and returns True if n is prime, False otherwise."
    ),
    expected_structure_keys=["content"],
    expected_contains=["def is_prime", "for", "return"],
)

EX_CG_002 = ExamTestCase(
    case_id="EX-CG-002",
    capability="code_generate",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "generate: a function called fibonacci that takes an integer n "
        "and returns the first n Fibonacci numbers as a list. "
        "Include a docstring and type hints."
    ),
    expected_structure_keys=["content"],
    expected_contains=["def fibonacci", "list", "docstring", "0, 1", "append"],
)

EX_CG_003 = ExamTestCase(
    case_id="EX-CG-003",
    capability="code_generate",
    difficulty=Difficulty.HARD,
    prompt=(
        "generate: a LRU cache class with get(key) and put(key, value) methods, "
        "using an OrderedDict for O(1) operations. "
        "Include capacity limit, eviction of least recently used items, "
        "and type hints."
    ),
    expected_structure_keys=["content"],
    expected_contains=["class", "OrderedDict", "get", "put", "capacity", "popitem"],
)

EX_DC_001 = ExamTestCase(
    case_id="EX-DC-001",
    capability="dead_code_removal",
    difficulty=Difficulty.EASY,
    prompt=(
        "detect dead code: script\n"
        "import os\n"
        "import json  # never used\n"
        "\n"
        "def main():\n"
        "    print(os.getcwd())\n"
        "    return 0"
    ),
    expected_structure_keys=["dead_sections"],
    expected_contains=["import json"],
)

EX_DC_002 = ExamTestCase(
    case_id="EX-DC-002",
    capability="dead_code_removal",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "detect dead code: worker\n"
        "def process(data):\n"
        "    result = transform(data)\n"
        "    return result\n"
        "    print('done')  # unreachable code after return"
    ),
    expected_structure_keys=["dead_sections"],
    expected_contains=["unreachable", "print", "after return"],
)

EX_DC_003 = ExamTestCase(
    case_id="EX-DC-003",
    capability="dead_code_removal",
    difficulty=Difficulty.HARD,
    prompt=(
        "detect dead code: utils\n"
        "def used_func(x):\n"
        "    return x * 2\n"
        "\n"
        "def dead_func(x):  # never called anywhere\n"
        "    return x ** 3\n"
        "\n"
        "result = used_func(5)"
    ),
    expected_structure_keys=["dead_sections"],
    expected_contains=["dead_func", "never called"],
)


ALL_EXAM_CASES: list[ExamTestCase] = [
    EX_CL_001,
    EX_CL_002,
    EX_CL_003,
    EX_TG_001,
    EX_TG_002,
    EX_TG_003,
    EX_SE_001,
    EX_SE_002,
    EX_SE_003,
    EX_NS_001,
    EX_NS_002,
    EX_NS_003,
    EX_AT_001,
    EX_AT_002,
    EX_AT_003,
    EX_CF_001,
    EX_CF_002,
    EX_CF_003,
    EX_RF_001,
    EX_RF_002,
    EX_RF_003,
    EX_CG_001,
    EX_CG_002,
    EX_CG_003,
    EX_DC_001,
    EX_DC_002,
    EX_DC_003,
]

CASES_BY_CAPABILITY: dict[str, list[ExamTestCase]] = {}
for _case in ALL_EXAM_CASES:
    CASES_BY_CAPABILITY.setdefault(_case.capability, []).append(_case)
