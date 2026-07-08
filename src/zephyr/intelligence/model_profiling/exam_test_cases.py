# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] zephyr.intelligence.model_profiling.exam_test_cases
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 96道v3.0.5扩展考试题;29能力×5难度
# [MODIFY-GUARD] docs/03_modules/_cross_layer/model_profiler/blueprint.md
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] TestCaseError
# [TESTS] tests/test_exam_test_cases.py
# [A_module] module_id=MOD-RSC_exam_test_cases | layer=module | stability=stable | safety=L | ai_autonomy=human_gated
# [TTL] permanent

"""
ExamTestCases --- v3.0.5 扩展考试题库（96 题 / 29 能力 / 5 难度）

5 难度: easy/medium/hard/extreme/olympiad
命名空间: EX-{capability_abbr}-{序号}

能力 -> 缩写映射:
    task_classification    -> CL
    tag_completion          -> TG
    summary_extraction      -> SE
    naming_suggest          -> NS
    anomaly_triage          -> AT
    code_fix                -> CF
    refactor                -> RF
    code_generate           -> CG
    dead_code_removal       -> DC
    + v3.0.5 扩展能力（20 项）见各题定义
"""

from __future__ import annotations

from typing import Final
from dataclasses import dataclass, field
from enum import Enum

# v3.0.5 Phase 3: 真实多文件注入装配器（极限深度 OLYMPIAD 题）
from .case_assembler import assemble_real_context


class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXTREME = "extreme"        # v3.0.5: 超纲但不封顶
    OLYMPIAD = "olympiad"      # v3.0.5: 奥赛级，参与奥赛封顶


@dataclass
class ExamTestCase:
    case_id: str
    capability: str
    difficulty: Difficulty
    prompt: str

    # 横轴: 只检查输出结构是否合法
    expected_structure_keys: list[str] = field(default_factory=list)

    # 纵轴: 期望答案 (根据能力类型不同含义不同)
    expected_tags: list[str] = field(default_factory=list)
    expected_category: str = ""
    expected_old_str: str = ""
    expected_new_str: str = ""
    expected_needs_human: bool = False
    expected_contains: list[str] = field(default_factory=list)

    # B类: 多文件联动能力
    input_files: dict[str, str] = field(default_factory=dict)
    expected_affected_files: list[str] = field(default_factory=list)
    expected_call_chain: list[str] = field(default_factory=list)

    # C类: 漂移检测能力
    expected_hallucinations: list[str] = field(default_factory=list)
    expected_answer: str = ""

    # D类: 规则理解能力
    expected_compliant: bool = False
    expected_modifiable: list[str] = field(default_factory=list)
    expected_blocked: list[str] = field(default_factory=list)

    # E类: 执行精度
    expected_edit_old: str = ""
    expected_edit_new: str = ""
    # F类: 自审自纠
    expected_has_bug: bool = False
    expected_bug_location: str = ""
    # G类: 增量执行
    expected_step_count: int = 0
    # H类: 错误恢复
    expected_root_cause: str = ""
    # I类: 歧义识别
    expected_ambiguous: bool = False
    # J类: 工具选择
    expected_tool: str = ""

    # K类: 影响分析能力
    expected_affected_files_k: list[str] = field(default_factory=list)  # impact_analysis预期受影响文件
    expected_has_cycle: bool = False  # circular_dependency_detect预期是否有循环
    expected_cycle_path: list[str] = field(default_factory=list)  # 预期循环路径
    expected_rollback_points: list[str] = field(default_factory=list)  # 预期回滚点
    # L类: 任务规划能力
    expected_tasks: list[str] = field(default_factory=list)  # 预期任务列表
    expected_parallel_groups: list[list[str]] = field(default_factory=list)  # 预期并行组
    expected_order: list[str] = field(default_factory=list)  # 预期排序
    # M类: 上下文管理能力
    expected_has_hallucination: bool = False  # 预期是否有幻觉
    expected_hallucinated_items: list[str] = field(default_factory=list)  # 预期幻觉项
    expected_context_degraded: bool = False  # 预期上下文是否退化
    expected_new_session: bool = False  # 预期是否需要新会话
    # N类: 执行式评测 — code_generate等能力用单元测试验证正确性（参考HumanEval pass@1）
    expected_test_cases: list[str] = field(default_factory=list)  # 可执行测试断言列表
    # O类: 静态文本断言 (P1-4) — OLY 题用关键文本包含率补充 executor 轨
    # 适用于非 code_generate 能力 (如 architecture_design/hallucination_detect 等)
    # _score_olympiad_case 当无 expected_test_cases 时, 用此字段走静态断言轨
    expected_static_assertions: list[str] = field(default_factory=list)

    # P类: 工具调用能力 (Tool 轴 ROADMAP-02)
    # function_calling: 期望调用的函数名 (复用 J 类 expected_tool) + 参数键值对
    expected_function_args: dict[str, str] = field(default_factory=dict)  # 预期参数 {key: value_substring}
    # tool_chaining: 预期工具调用顺序 (按序出现的工具名列表)
    expected_tool_sequence: list[str] = field(default_factory=list)


# ══════════════════════════════════════════════════════════
# task_classification (3 题)
# ══════════════════════════════════════════════════════════

EX_CL_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CL-001",
    capability="task_classification",
    difficulty=Difficulty.EASY,
    prompt="classify this module: hello\nprint('hello world')",
    expected_structure_keys=["category"],
    expected_category="other",
)

EX_CL_002: Final[ExamTestCase] = ExamTestCase(
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

EX_CL_003: Final[ExamTestCase] = ExamTestCase(
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

# ══════════════════════════════════════════════════════════
# tag_completion (3 题)
# ══════════════════════════════════════════════════════════

EX_TG_001: Final[ExamTestCase] = ExamTestCase(
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

EX_TG_002: Final[ExamTestCase] = ExamTestCase(
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

EX_TG_003: Final[ExamTestCase] = ExamTestCase(
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

# ══════════════════════════════════════════════════════════
# summary_extraction (3 题)
# ══════════════════════════════════════════════════════════

EX_SE_001: Final[ExamTestCase] = ExamTestCase(
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

EX_SE_002: Final[ExamTestCase] = ExamTestCase(
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

EX_SE_003: Final[ExamTestCase] = ExamTestCase(
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

# ══════════════════════════════════════════════════════════
# naming_suggest (3 题)
# ══════════════════════════════════════════════════════════

EX_NS_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-NS-001",
    capability="naming_suggest",
    difficulty=Difficulty.EASY,
    prompt=("suggest alternative names for module: calc\ndef f(x, y):\n    return x + y"),
    expected_structure_keys=["names"],
    expected_contains=["calculator", "math_utils", "arithmetic"],
)

EX_NS_002: Final[ExamTestCase] = ExamTestCase(
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

EX_NS_003: Final[ExamTestCase] = ExamTestCase(
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

# ══════════════════════════════════════════════════════════
# anomaly_triage (3 题)
# ══════════════════════════════════════════════════════════

EX_AT_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-AT-001",
    capability="anomaly_triage",
    difficulty=Difficulty.EASY,
    prompt="triage: WARNING: orphan module detected: old_script.py",
    expected_structure_keys=["needs_human", "reason"],
    expected_needs_human=False,
)

EX_AT_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-AT-002",
    capability="anomaly_triage",
    difficulty=Difficulty.MEDIUM,
    prompt="triage: CRITICAL: gateway authentication bypass detected in auth_middleware.py",
    expected_structure_keys=["needs_human", "reason"],
    expected_needs_human=True,
)

EX_AT_003: Final[ExamTestCase] = ExamTestCase(
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

# ══════════════════════════════════════════════════════════
# code_fix (3 题)
# ══════════════════════════════════════════════════════════

EX_CF_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CF-001",
    capability="code_edit_precision",
    difficulty=Difficulty.EASY,
    prompt=("fix bug: calc\ndef add(a, b):\n    return a - b  # BUG: should be a + b"),
    expected_structure_keys=["fixes"],
    expected_old_str="a - b",
    expected_new_str="a + b",
    expected_contains=["a + b", "return a + b"],
)

EX_CF_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CF-002",
    capability="code_edit_precision",
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
    expected_contains=["hash", "user_input"],
)

EX_CF_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CF-003",
    capability="code_edit_precision",
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

# ══════════════════════════════════════════════════════════
# refactor (3 题)
# ══════════════════════════════════════════════════════════

EX_RF_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-RF-001",
    capability="refactor",
    difficulty=Difficulty.EASY,
    prompt=("refactor: calc\nx = 10\ny = 20\nz = 30\nresult = x + y + z  # magic numbers everywhere"),
    expected_structure_keys=["changes"],
    expected_old_str="result = x + y + z",
    expected_new_str="TEN = 10\nTWENTY = 20\nTHIRTY = 30\nresult = TEN + TWENTY + THIRTY",
    expected_contains=["constant", "TEN", "MAGIC"],
)

EX_RF_002: Final[ExamTestCase] = ExamTestCase(
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
    expected_old_str="result = []\nfor i in range(len(data)):\n    result.append(data[i] * 2)",
    expected_new_str="result = [x * 2 for x in data]",
    expected_contains=["comprehension", "x * 2 for x in"],
)

EX_RF_003: Final[ExamTestCase] = ExamTestCase(
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
    expected_old_str="html += f'<li>{item}</li>'",
    expected_new_str="items = [f'<li>{item}</li>' for item in data]\nhtml = ''.join(items)",
    expected_contains=["join", "append", "concat"],
)

# ══════════════════════════════════════════════════════════
# code_generate (3 题)
# ══════════════════════════════════════════════════════════

EX_CG_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CG-001",
    capability="code_generate",
    difficulty=Difficulty.EASY,
    prompt=(
        "generate: a function called is_prime that takes an integer n and returns True if n is prime, False otherwise."
    ),
    expected_structure_keys=["content"],
    expected_contains=["def is_prime", "for n", "return True"],
    expected_test_cases=[
        "assert is_prime(2) == True",
        "assert is_prime(7) == True",
        "assert is_prime(1) == False",
        "assert is_prime(4) == False",
        "assert is_prime(0) == False",
        "assert is_prime(-3) == False",
    ],
)

EX_CG_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CG-002",
    capability="code_generate",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "generate: a function called fibonacci that takes an integer n "
        "and returns the first n Fibonacci numbers as a list. "
        "Include a docstring and type hints."
    ),
    expected_structure_keys=["content"],
    expected_contains=["def fibonacci", "docstring", "0, 1", "append"],
    expected_test_cases=[
        "assert fibonacci(0) == []",
        "assert fibonacci(1) == [0]",
        "assert fibonacci(2) == [0, 1]",
        "assert fibonacci(5) == [0, 1, 1, 2, 3]",
        "assert fibonacci(10) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]",
        "assert len(fibonacci(20)) == 20",
    ],
)

EX_CG_003: Final[ExamTestCase] = ExamTestCase(
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
    expected_contains=["class LRU", "OrderedDict", "get", "put", "capacity", "popitem"],
    expected_test_cases=[
        "c = LRU(2); c.put(1, 'a'); c.put(2, 'b'); assert c.get(1) == 'a'",
        "c = LRU(2); c.put(1, 'a'); c.put(2, 'b'); c.put(3, 'c'); assert c.get(1) == None",
        "c = LRU(2); c.put(1, 'a'); c.put(2, 'b'); c.get(1); c.put(3, 'c'); assert c.get(2) == None",
        "c = LRU(1); c.put(1, 'a'); c.put(2, 'b'); assert c.get(1) == None; assert c.get(2) == 'b'",
        "c = LRU(3); c.put(1, 'a'); c.put(2, 'b'); c.put(3, 'c'); c.get(1); c.put(4, 'd'); assert c.get(2) == None",
    ],
)

# ══════════════════════════════════════════════════════════
# dead_code_removal (3 题)
# ══════════════════════════════════════════════════════════

EX_DC_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-DC-001",
    capability="dead_code_removal",
    difficulty=Difficulty.EASY,
    prompt=("detect dead code: script\nimport os\nimport json\n\ndef main():\n    print(os.getcwd())\n    return 0"),
    expected_structure_keys=["dead_sections"],
    expected_old_str="import json",
    expected_new_str="",
    expected_contains=["json", "import json"],
)

EX_DC_002: Final[ExamTestCase] = ExamTestCase(
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
    expected_old_str="    print('done')  # unreachable code after return",
    expected_new_str="",
    expected_contains=["unreachable", "print('done')", "after return"],
)

EX_DC_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-DC-003",
    capability="dead_code_removal",
    difficulty=Difficulty.HARD,
    prompt=(
        "detect dead code: utils\n"
        "def used_func(x):\n"
        "    return x * 2\n"
        "\n"
        "def dead_func(x):\n"
        "    return x ** 3\n"
        "\n"
        "result = used_func(5)"
    ),
    expected_structure_keys=["dead_sections"],
    expected_old_str="def dead_func(x):\n    return x ** 3\n\n",
    expected_new_str="",
    expected_contains=["dead_func", "dead"],
)


# ══════════════════════════════════════════════════════════
# B类: 多文件联动能力 (12 题)
# ══════════════════════════════════════════════════════════

# cross_file_analysis (3 题) — 跨文件依赖分析
EX_CFA_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CFA-001",
    capability="impact_analysis",
    difficulty=Difficulty.EASY,
    prompt="如果将 calc.py 的 add 函数签名改为 add(a, b, c=0)，哪些文件需要修改？",
    expected_structure_keys=["affected_files"],
    input_files={
        "calc.py": "def add(a, b):\n    return a + b\n",
        "main.py": "from calc import add\nresult = add(1, 2)\nprint(result)\n",
        "test_calc.py": "from calc import add\ndef test_add():\n    assert add(1, 2) == 3\n",
    },
    expected_affected_files=["main.py", "test_calc.py"],
    expected_contains=["main.py", "test_calc.py"],
)

EX_CFA_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CFA-002",
    capability="impact_analysis",
    difficulty=Difficulty.MEDIUM,
    prompt="如果从 User 类中删除 email 字段，哪些文件需要修改？",
    expected_structure_keys=["affected_files"],
    input_files={
        "models.py": "class User:\n    def __init__(self, name, email):\n        self.name = name\n        self.email = email\n",
        "api.py": "from models import User\ndef create_user(name, email):\n    return User(name, email)\n",
        "serializer.py": "from models import User\ndef serialize(user):\n    return {'name': user.name, 'email': user.email}\n",
        "tests.py": "from models import User\ndef test_user():\n    u = User('test', 'test@test.com')\n    assert u.email == 'test@test.com'\n",
    },
    expected_affected_files=["api.py", "serializer.py", "tests.py"],
    expected_contains=["api.py", "serializer.py", "tests.py"],
)

EX_CFA_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CFA-003",
    capability="impact_analysis",
    difficulty=Difficulty.HARD,
    prompt="如果将 config.py 的 DATABASE_URL 改名为 DB_CONNECTION_STRING，哪些文件需要修改？",
    expected_structure_keys=["affected_files"],
    input_files={
        "config.py": "DATABASE_URL = 'localhost:5432'\nCACHE_URL = 'localhost:6379'\n",
        "db.py": "from config import DATABASE_URL\nclass Database:\n    def __init__(self):\n        self.url = DATABASE_URL\n",
        "cache.py": "from config import CACHE_URL\nclass Cache:\n    def __init__(self):\n        self.url = CACHE_URL\n",
        "api.py": "from db import Database\nfrom cache import Cache\ndb = Database()\ncache = Cache()\n",
        "utils.py": "from config import DATABASE_URL\ndef get_db_url():\n    return DATABASE_URL\n",
    },
    expected_affected_files=["db.py", "utils.py"],
    expected_contains=["db.py", "utils.py"],
)

# architecture_design (3 题) — 架构方案设计
EX_AD_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-AD-001",
    capability="architecture_design",
    difficulty=Difficulty.EASY,
    prompt="设计一个用户注册功能，需要：1.用户输入验证 2.密码加密 3.数据库存储 4.发送欢迎邮件 5.记录注册日志。请设计文件结构和依赖关系。",
    expected_structure_keys=["files", "dependencies"],
    expected_contains=["validate", "password", "database", "email", "logger"],
)

EX_AD_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-AD-002",
    capability="architecture_design",
    difficulty=Difficulty.MEDIUM,
    prompt="设计一个API网关，需要：1.路由转发 2.认证中间件 3.限流 4.日志记录 5.错误处理 6.请求缓存。请设计文件结构和依赖关系。",
    expected_structure_keys=["files", "dependencies"],
    expected_contains=["router", "auth", "rate_limit", "logger", "error", "cache"],
)

EX_AD_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-AD-003",
    capability="architecture_design",
    difficulty=Difficulty.HARD,
    prompt="设计一个事件驱动架构，需要：1.事件发布 2.事件订阅 3.事件存储 4.事件回放 5.事件版本管理 6.死信队列。请设计文件结构和依赖关系。",
    expected_structure_keys=["files", "dependencies"],
    expected_contains=["publisher", "subscriber", "event_store", "replay", "version", "dead_letter"],
)

# cross_file_refactor (3 题) — 跨文件重构
EX_CFR_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CFR-001",
    capability="cross_file_refactor",
    difficulty=Difficulty.EASY,
    prompt="将 calc.py 的 add 函数重命名为 sum_values，更新所有调用方。输出每个文件需要的修改。",
    expected_structure_keys=["changes"],
    input_files={
        "calc.py": "def add(a, b):\n    return a + b\n",
        "main.py": "from calc import add\nresult = add(1, 2)\n",
        "test.py": "from calc import add\nassert add(1, 2) == 3\n",
    },
    expected_contains=["sum_values", "calc.py", "main.py", "test.py"],
)

EX_CFR_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CFR-002",
    capability="cross_file_refactor",
    difficulty=Difficulty.MEDIUM,
    prompt="将 User 类重命名为 Account，更新所有文件。输出每个文件需要的修改。",
    expected_structure_keys=["changes"],
    input_files={
        "models.py": "class User:\n    def __init__(self, name):\n        self.name = name\n",
        "api.py": "from models import User\ndef create(name):\n    return User(name)\n",
        "serializer.py": "from models import User\ndef serialize(u):\n    return u.name\n",
    },
    expected_contains=["Account", "models.py", "api.py", "serializer.py"],
)

EX_CFR_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CFR-003",
    capability="cross_file_refactor",
    difficulty=Difficulty.HARD,
    prompt="将 Database.query 方法重命名为 execute，更新所有调用链。输出每个文件需要的修改。",
    expected_structure_keys=["changes"],
    input_files={
        "db.py": "class Database:\n    def query(self, sql):\n        pass\n",
        "repo.py": "from db import Database\nclass UserRepo:\n    def __init__(self):\n        self.db = Database()\n    def find(self, id):\n        return self.db.query(f'SELECT * FROM users WHERE id={id}')\n",
        "service.py": "from repo import UserRepo\nclass UserService:\n    def __init__(self):\n        self.repo = UserRepo()\n    def get_user(self, id):\n        return self.repo.find(id)\n",
        "api.py": "from service import UserService\nsvc = UserService()\nuser = svc.get_user(1)\n",
    },
    expected_contains=["execute", "db.py", "repo.py"],
)

# dependency_trace (3 题) — 依赖链追踪
EX_DT_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-DT-001",
    capability="dependency_trace",
    difficulty=Difficulty.EASY,
    prompt="追踪 func_a 的完整调用链，列出所有涉及的函数和文件。",
    expected_structure_keys=["call_chain"],
    input_files={
        "a.py": "from b import func_b\ndef func_a():\n    return func_b()\n",
        "b.py": "from c import func_c\ndef func_b():\n    return func_c()\n",
        "c.py": "def func_c():\n    return 'result'\n",
    },
    expected_call_chain=["func_a", "func_b", "func_c"],
    expected_contains=["func_a", "func_b", "func_c", "a.py", "b.py", "c.py"],
)

EX_DT_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-DT-002",
    capability="dependency_trace",
    difficulty=Difficulty.MEDIUM,
    prompt="追踪 handler() 的完整调用链，从API层到数据库层，列出所有涉及的函数和文件。",
    expected_structure_keys=["call_chain"],
    input_files={
        "api.py": "from service import UserService\ndef handler():\n    svc = UserService()\n    return svc.get_user(1)\n",
        "service.py": "from repo import UserRepo\nclass UserService:\n    def get_user(self, id):\n        return UserRepo().find(id)\n",
        "repo.py": "from db import Database\nclass UserRepo:\n    def find(self, id):\n        return Database().query(f'SELECT * FROM users WHERE id={id}')\n",
        "db.py": "class Database:\n    def query(self, sql):\n        return sql\n",
    },
    expected_call_chain=["handler", "get_user", "find", "query"],
    expected_contains=["handler", "get_user", "find", "query", "api.py", "service.py", "repo.py", "db.py"],
)

EX_DT_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-DT-003",
    capability="dependency_trace",
    difficulty=Difficulty.HARD,
    prompt="追踪 main() 的完整调用链，包括所有分支，列出所有涉及的函数和文件。",
    expected_structure_keys=["call_chain"],
    input_files={
        "main.py": "from controller import Controller\ndef main():\n    Controller().run()\n",
        "controller.py": "from service import ServiceA, ServiceB\nclass Controller:\n    def run(self):\n        a = ServiceA().process()\n        b = ServiceB().process()\n        return a + b\n",
        "service.py": "from repo import Repo\nclass ServiceA:\n    def process(self):\n        return Repo().fetch_a()\nclass ServiceB:\n    def process(self):\n        return Repo().fetch_b()\n",
        "repo.py": "from db import Database\nclass Repo:\n    def fetch_a(self):\n        return Database().query('SELECT a')\n    def fetch_b(self):\n        return Database().query('SELECT b')\n",
        "db.py": "class Database:\n    def query(self, sql):\n        return sql\n",
    },
    expected_call_chain=["main", "run", "process", "fetch_a", "fetch_b", "query"],
    expected_contains=["Controller", "ServiceA", "ServiceB", "fetch_a", "fetch_b", "query"],
)


# ══════════════════════════════════════════════════════════
# C类: 漂移检测能力 (9 题)
# ══════════════════════════════════════════════════════════

# context_consistency (3 题) — 上下文一致性检测
# FIX L3.5: 从字面矛盾改为语义矛盾（旧题int vs string、SQLite vs PostgreSQL太明显）
EX_CC_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CC-001",
    capability="context_consistency",
    difficulty=Difficulty.EASY,
    prompt=(
        "检查以下技术文档是否存在矛盾：\n"
        "系统设计为无状态服务，所有API请求相互独立。"
        "用户会话状态存储在服务器内存中，用于维持登录状态。"
        "请分析文档是否存在不一致。"
    ),
    expected_structure_keys=["consistent", "conflicts"],
    expected_contains=["stateless", "无状态", "session", "会话", "in-memory", "内存", "memory"],
)

EX_CC_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CC-002",
    capability="context_consistency",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "检查以下项目文档是否存在矛盾：\n"
        "本系统采用事件驱动架构，组件间通过消息队列异步通信。"
        "所有组件每5秒轮询一次数据库，检查是否有新任务需要处理。"
        "请分析文档是否存在不一致。"
    ),
    expected_structure_keys=["consistent", "conflicts"],
    expected_contains=["event-driven", "polling", "轮询", "asynchronous"],
)

EX_CC_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CC-003",
    capability="context_consistency",
    difficulty=Difficulty.HARD,
    prompt=(
        "检查以下架构文档是否存在矛盾：\n"
        "系统采用微服务架构，每个服务拥有独立的数据库实例，服务间通过API通信。"
        "订单服务和库存服务共享同一个MySQL数据库的orders和inventory表。"
        "所有服务必须独立部署和扩展。"
        "订单服务在部署时需要先启动库存服务，否则无法访问共享数据。"
        "请分析文档是否存在不一致。"
    ),
    expected_structure_keys=["consistent", "conflicts"],
    expected_contains=["microservice", "微服务", "shared", "共享", "database", "数据库", "independent", "独立"],
)

# hallucination_detect (3 题) — 幻觉检测
EX_HD_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-HD-001",
    capability="hallucination_detect",
    difficulty=Difficulty.EASY,
    prompt=(
        "项目文件列表：main.py, utils.py, config.py, os（标准库）\n"
        "代码分析报告：本项目使用了 utils.py 进行工具函数管理，"
        "使用了 phantom_module.py 进行数据处理，同时使用了标准的 os 模块。\n"
        "请对比文件列表，识别报告中哪些模块是编造的。"
    ),
    expected_structure_keys=["hallucinations"],
    expected_hallucinations=["phantom_module.py"],
    expected_contains=["phantom_module"],
)

EX_HD_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-HD-002",
    capability="hallucination_detect",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "项目API列表：get_user(id), create_user(data), update_user(id, data)\n"
        "API文档声称：本库提供了 fetch_all_users() 函数获取所有用户，"
        "同时封装了 requests.get() 进行 HTTP 请求。\n"
        "请对比API列表，识别文档中哪些函数是编造的。"
    ),
    expected_structure_keys=["hallucinations"],
    expected_hallucinations=["fetch_all_users"],
    expected_contains=["fetch_all_users"],
)

EX_HD_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-HD-003",
    capability="hallucination_detect",
    difficulty=Difficulty.HARD,
    prompt=(
        "项目模块列表：logging, json, auth_service.py, user_repo.py, api_controller.py\n"
        "架构分析声称：系统由 phantom_service、ghost_repository、mirage_controller 三个核心模块组成，"
        "同时依赖标准的 logging 和 json 模块。\n"
        "请对比模块列表，识别分析中哪些模块是编造的。"
    ),
    expected_structure_keys=["hallucinations"],
    expected_hallucinations=["phantom_service", "ghost_repository", "mirage_controller"],
    expected_contains=["phantom_service", "ghost_repository", "mirage_controller"],
)

# long_context_recall (3 题) — 长上下文召回
EX_LCR_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-LCR-001",
    capability="long_context_recall",
    difficulty=Difficulty.EASY,
    prompt=(
        "请仔细阅读以下流程说明：\n"
        "第一步：读取配置文件。\n"
        "第二步：初始化数据库连接。\n"
        "第三步：加载用户数据。\n"
        "第四步：执行业务逻辑。\n"
        "第五步：保存结果并关闭连接。\n"
        "问题：在执行业务逻辑之前，需要完成几个步骤？"
    ),
    expected_structure_keys=["answer"],
    expected_answer="3",
    expected_contains=["3", "three", "三"],
)

EX_LCR_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-LCR-002",
    capability="long_context_recall",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "请仔细阅读以下技术文档：\n"
        "系统配置参数说明：MAX_RETRIES=3 表示最大重试次数。"
        "TIMEOUT=30 表示请求超时秒数。BATCH_SIZE=100 表示批处理大小。"
        "CACHE_TTL=3600 表示缓存存活时间秒数。LOG_LEVEL=INFO 表示日志级别。"
        "问题：如果每次重试间隔为TIMEOUT秒，最坏情况下请求总耗时是多少秒？"
    ),
    expected_structure_keys=["answer"],
    expected_answer="120",
    expected_contains=["120", "4*30", "3*30", "four"],
)

EX_LCR_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-LCR-003",
    capability="long_context_recall",
    difficulty=Difficulty.HARD,
    prompt=(
        "请仔细阅读以下代码审查报告：\n"
        "审查范围：认证模块在 auth/middleware.py，负责用户身份验证。"
        "授权模块在 auth/permissions.py，负责权限检查。"
        "日志模块在 utils/logger.py，负责记录操作日志。"
        "缓存模块在 utils/cache.py，负责数据缓存。"
        "数据库模块在 db/connection.py，负责数据库连接管理。"
        "问题：认证模块在哪个文件？"
    ),
    expected_structure_keys=["answer"],
    expected_answer="auth/middleware.py",
    expected_contains=["auth/middleware.py", "middleware"],
)


# ══════════════════════════════════════════════════════════
# D类: 规则理解能力 (6 题)
# ══════════════════════════════════════════════════════════

# rule_comprehension (3 题) — 规则理解
# FIX L3.5: 精确化expected_contains（旧值包含修复建议而非违反点）
EX_RC_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-RC-001",
    capability="rule_comprehension",
    difficulty=Difficulty.EASY,
    prompt="规则集：1.所有Python文件必须使用UTF-8编码 2.禁止使用eval()函数 3.所有函数必须有类型注解。场景：代码中有 `def process(data):\n    result = eval(data)\n    with open('output.txt', 'w') as f:\n        f.write(result)`。这段代码违反了哪些规则？",
    expected_structure_keys=["compliant", "violations"],
    expected_compliant=False,
    expected_contains=["eval", "type", "encoding"],
)

EX_RC_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-RC-002",
    capability="rule_comprehension",
    difficulty=Difficulty.MEDIUM,
    prompt="规则集：1.禁止在for循环中使用subprocess.run() 2.所有HTTP请求必须设置timeout 3.异常必须记录日志。场景：代码中有 `for url in urls:\n    resp = subprocess.run(['curl', url])\n    print(resp)`。这段代码违反了哪些规则？",
    expected_structure_keys=["compliant", "violations"],
    expected_compliant=False,
    expected_contains=["subprocess", "timeout", "log"],
)

EX_RC_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-RC-003",
    capability="rule_comprehension",
    difficulty=Difficulty.HARD,
    prompt="规则集：1.文件名必须snake_case 2.禁止PowerShell语法 3.复杂逻辑必须落盘为.py脚本 4.禁止在代码中使用中文变量名 5.所有配置必须从YAML读取。场景：开发者编写了 `ValidateConfig.py` 文件（注意大小写），其中包含一个100行的数据校验函数，用Python标准库实现，配置硬编码在代码中。这段代码违反了哪些规则？",
    expected_structure_keys=["compliant", "violations"],
    expected_compliant=False,
    expected_contains=["snake_case", "yaml", "hardcoded", "config"],
)

# 审查2.2修复: rule_comprehension 正例对照组 (防止"总是报不合规"退化策略拿满分)
EX_RC_004: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-RC-004",
    capability="rule_comprehension",
    difficulty=Difficulty.MEDIUM,
    prompt="规则集：1.文件名必须snake_case 2.禁止PowerShell语法 3.复杂逻辑必须落盘为.py脚本 4.禁止在代码中使用中文变量名 5.所有配置必须从YAML读取。场景：开发者编写了 `validate_config.py` 文件（snake_case），用Python标准库实现了一个50行的配置校验函数，所有配置参数从 `config.yaml` 读取，变量名均为英文。这段代码违反了哪些规则？",
    expected_structure_keys=["compliant", "violations"],
    expected_compliant=True,
    expected_contains=["compliant", "no violation", "follows"],
)

# safety_judgment (3 题) — 安全判断
EX_SJ_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-SJ-001",
    capability="safety_judgment",
    difficulty=Difficulty.EASY,
    prompt="判断以下文件AI能否自主修改：1.config.py [AI_AUTONOMY=ai_modifiable] 2.core_rules.py [AI_AUTONOMY=immutable_core] 3/utils.py [AI_AUTONOMY=ai_modifiable]",
    expected_structure_keys=["modifiable", "blocked"],
    expected_modifiable=["config.py", "utils.py"],
    expected_blocked=["core_rules.py"],
    expected_contains=["config.py", "utils.py", "core_rules.py"],
)

EX_SJ_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-SJ-002",
    capability="safety_judgment",
    difficulty=Difficulty.MEDIUM,
    prompt="判断以下文件AI能否自主修改：1.database_schema.py [AI_AUTONOMY=human_gated] 2.helper.py [AI_AUTONOMY=ai_modifiable] 3/lock_files.py [AI_AUTONOMY=immutable_core] 4/test_utils.py [AI_AUTONOMY=ai_modifiable]",
    expected_structure_keys=["modifiable", "blocked"],
    expected_modifiable=["helper.py", "test_utils.py"],
    expected_blocked=["database_schema.py", "lock_files.py"],
    expected_contains=["helper.py", "test_utils.py", "database_schema.py", "lock_files.py"],
)

EX_SJ_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-SJ-003",
    capability="safety_judgment",
    difficulty=Difficulty.HARD,
    prompt="判断以下文件AI能否自主修改：1.pasport.py [AI_AUTONOMY=ai_modifiable] 2/blueprint.md [AI_AUTONOMY=human_gated] 3/governance_rules.yaml [AI_AUTONOMY=immutable_core] 4/README.md [AI_AUTONOMY=ai_modifiable] 5/security_gateway.py [AI_AUTONOMY=immutable_core]",
    expected_structure_keys=["modifiable", "blocked"],
    expected_modifiable=["pasport.py", "README.md"],
    expected_blocked=["blueprint.md", "governance_rules.yaml", "security_gateway.py"],
    expected_contains=["pasport.py", "README.md", "blueprint.md", "governance_rules.yaml", "security_gateway.py"],
)


# ══════════════════════════════════════════════════════════
# E类: 执行精度能力 (3 题)
# ══════════════════════════════════════════════════════════

# file_edit_precision (3 题) — 执行精度
EX_FEP_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-FEP-001",
    capability="code_edit_precision",
    difficulty=Difficulty.EASY,
    prompt="给定文件内容 `x = 10\ny = 20\nz = x + y`，要求把x的值从10改为100。输出精确的old_str和new_str。",
    expected_structure_keys=["edits"],
    expected_edit_old="x = 10",
    expected_edit_new="x = 100",
    expected_contains=["x = 100"],
)

EX_FEP_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-FEP-002",
    capability="code_edit_precision",
    difficulty=Difficulty.MEDIUM,
    prompt="给定文件内容 `def calc(a, b):\n    return a - b`，要求修复bug把减法改成加法。输出精确的old_str和new_str。",
    expected_structure_keys=["edits"],
    expected_edit_old="return a - b",
    expected_edit_new="return a + b",
    expected_contains=["a + b"],
)

EX_FEP_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-FEP-003",
    capability="code_edit_precision",
    difficulty=Difficulty.HARD,
    prompt="给定文件内容 `class User:\n    def __init__(self, name):\n        self.name = name\n    def get_info(self):\n        return self.name`，要求把get_info方法重命名为get_name。输出精确的old_str和new_str。",
    expected_structure_keys=["edits"],
    expected_edit_old="def get_info(self):",
    expected_edit_new="def get_name(self):",
    expected_contains=["get_name"],
)


# ══════════════════════════════════════════════════════════
# F类: 自审自纠能力 (3 题)
# ══════════════════════════════════════════════════════════

# self_review (3 题) — 自审自纠
# FIX L3.5: 把明显bug改为隐蔽的逻辑错误（旧题add返回减法、divide除零太明显）
EX_SR_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-SR-001",
    capability="self_review",
    difficulty=Difficulty.EASY,
    prompt="审查以下代码是否有bug：\ndef calculate_discount(price, discount):\n    return price * (1 + discount)\n\n请检查代码是否有问题。",
    expected_structure_keys=["has_bug", "bugs"],
    expected_has_bug=True,
    expected_bug_location="1 + discount",
    expected_contains=["1 + discount", "addition", "subtraction"],
)

EX_SR_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-SR-002",
    capability="self_review",
    difficulty=Difficulty.MEDIUM,
    prompt="审查以下代码是否有bug：\ndef get_last_item(lst):\n    return lst[len(lst)]\n\n请检查是否有潜在问题。",
    expected_structure_keys=["has_bug", "bugs"],
    expected_has_bug=True,
    expected_bug_location="len(lst)",
    expected_contains=["index", "out of range", "len(lst)", "off-by-one"],
)

EX_SR_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-SR-003",
    capability="self_review",
    difficulty=Difficulty.HARD,
    prompt="审查以下代码是否有bug：\ndef find_max(numbers):\n    max_val = 0\n    for n in numbers:\n        if n > max_val:\n            max_val = n\n    return max_val\n\n请检查代码是否有问题。",
    expected_structure_keys=["has_bug", "bugs"],
    expected_has_bug=True,
    expected_bug_location="max_val = 0",
    expected_contains=["negative", "zero", "initial", "max_val = 0"],
)


# ══════════════════════════════════════════════════════════
# G类: 增量执行能力 (3 题)
# ══════════════════════════════════════════════════════════

# incremental_execution (3 题) — 增量执行
EX_IE_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-IE-001",
    capability="incremental_execution",
    difficulty=Difficulty.EASY,
    prompt="任务：读取config.yaml文件，提取database_url字段的值并返回。\n请分解任务步骤并按顺序执行。",
    expected_structure_keys=["steps"],
    expected_step_count=3,
    expected_contains=["read", "读取", "parse", "解析", "extract", "提取", "return", "返回"],
)

EX_IE_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-IE-002",
    capability="incremental_execution",
    difficulty=Difficulty.MEDIUM,
    prompt="任务：搜索项目中所有.py文件，过滤出包含'import os'的文件，统计数量并生成报告。\n请分解任务步骤并按顺序执行。",
    expected_structure_keys=["steps"],
    expected_step_count=5,
    expected_contains=["search", "搜索", "filter", "过滤", "count", "计数", "report", "报告", "glob"],
)

EX_IE_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-IE-003",
    capability="incremental_execution",
    difficulty=Difficulty.HARD,
    prompt="任务：读取用户输入的SQL，检查是否有DROP/DELETE语句，如果有则要求确认，最后执行SQL并返回结果。\n请分解任务步骤并按顺序执行，注意条件分支。",
    expected_structure_keys=["steps"],
    expected_step_count=4,
    expected_contains=["read", "读取", "check", "检查", "confirm", "确认", "execute", "执行", "condition", "条件"],
)


# ══════════════════════════════════════════════════════════
# H类: 错误恢复能力 (3 题)
# ══════════════════════════════════════════════════════════

# error_recovery (3 题) — 错误恢复
EX_ER_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-ER-001",
    capability="error_recovery",
    difficulty=Difficulty.EASY,
    prompt="执行 `python script.py` 时报错：`ModuleNotFoundError: No module named 'requests'`。请诊断根因并提供修复方案。",
    expected_structure_keys=["diagnosis", "root_cause", "fix"],
    expected_root_cause="requests模块未安装",
    expected_contains=["pip install", "requests", "install"],
)

EX_ER_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-ER-002",
    capability="error_recovery",
    difficulty=Difficulty.MEDIUM,
    prompt="执行 `import json; json.loads('invalid')` 时报错：`json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)`。请诊断根因并提供修复方案。",
    expected_structure_keys=["diagnosis", "root_cause", "fix"],
    expected_root_cause="JSON格式无效",
    expected_contains=["JSON", "invalid", "parse", "JSONDecodeError"],
)

EX_ER_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-ER-003",
    capability="error_recovery",
    difficulty=Difficulty.HARD,
    prompt="执行 `for i in range(10): subprocess.run(['cmd'])` 时卡死40分钟无响应。请诊断根因并提供修复方案。",
    expected_structure_keys=["diagnosis", "root_cause", "fix"],
    expected_root_cause="for循环中串行调用subprocess",
    expected_contains=["ThreadPoolExecutor", "serial", "subprocess", "parallel"],
)


# ══════════════════════════════════════════════════════════
# I类: 歧义识别能力 (3 题)
# ══════════════════════════════════════════════════════════

# ambiguity_detect (3 题) — 歧义识别
# 注: 使用 EX_AMB 前缀避免与 architecture_design 的 EX_AD 冲突
EX_AMB_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-AMB-001",
    capability="ambiguity_detect",
    difficulty=Difficulty.EASY,
    prompt="指令：'优化这个函数'。这个指令是否有歧义？如果有，指出哪些方面不明确。",
    expected_structure_keys=["ambiguous", "ambiguities"],
    expected_ambiguous=True,
    expected_contains=["ambiguous", "optimize", "unclear"],
)

EX_AMB_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-AMB-002",
    capability="ambiguity_detect",
    difficulty=Difficulty.MEDIUM,
    prompt="指令：'修复bug'。这个指令是否有歧义？如果有，指出哪些方面不明确。",
    expected_structure_keys=["ambiguous", "ambiguities"],
    expected_ambiguous=True,
    expected_contains=["ambiguous", "bug", "which bug", "where is"],
)

EX_AMB_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-AMB-003",
    capability="ambiguity_detect",
    difficulty=Difficulty.HARD,
    prompt="指令：'将 utils.py 中第42行的 `result = a + b` 改为 `result = a * b`，并运行 tests/test_utils.py 验证'。这个指令是否有歧义？如果有，指出哪些方面不明确。",
    expected_structure_keys=["ambiguous", "ambiguities"],
    expected_ambiguous=False,
    expected_contains=["no ambiguity", "clear", "unambiguous"],
)


# ══════════════════════════════════════════════════════════
# J类: 工具选择能力 (3 题)
# ══════════════════════════════════════════════════════════

# tool_selection (3 题) — 工具选择
# FIX L3.5: 增加干扰选项，expected_contains改为理由关键词（旧题场景太简单）
EX_TS_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-TS-001",
    capability="tool_selection",
    difficulty=Difficulty.EASY,
    prompt="项目中有200个Python文件和50个配置文件，你需要定位所有包含'DEPRECATED'标记的代码行，以便进行技术债清理。应该用什么工具？",
    expected_structure_keys=["tool", "reason"],
    expected_tool="Grep",
    expected_contains=["search", "pattern", "content", "regex"],
)

EX_TS_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-TS-002",
    capability="tool_selection",
    difficulty=Difficulty.MEDIUM,
    prompt="部署前需要确认 docker-compose.yml 中数据库服务的端口映射是否正确，你需要查看该文件的完整内容以核对配置。应该用什么工具？",
    expected_structure_keys=["tool", "reason"],
    expected_tool="Read",
    expected_contains=["full", "content", "complete", "view"],
)

EX_TS_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-TS-003",
    capability="tool_selection",
    difficulty=Difficulty.HARD,
    prompt="CI流水线需要收集 src/ 目录下所有Python模块的文件路径列表，用于批量执行lint检查，但需要排除 __pycache__ 目录和测试文件。应该用什么工具？",
    expected_structure_keys=["tool", "reason"],
    expected_tool="Glob",
    expected_contains=["pattern", "file paths", "list", "match"],
)


# ══════════════════════════════════════════════════════════
# P类: 工具调用能力 (Tool 轴 ROADMAP-02)
# function_calling: 测试模型能否生成正确的工具调用 (函数名 + 参数)
# tool_chaining: 测试模型能否规划多工具调用顺序
# ══════════════════════════════════════════════════════════

# function_calling (3 题) — 生成结构化工具调用
EX_FC_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-FC-001",
    capability="function_calling",
    difficulty=Difficulty.EASY,
    prompt=(
        "你需要查看 docker-compose.yml 的完整内容来核对端口配置。"
        "请生成工具调用，输出 JSON 包含 function 和 arguments 字段。"
    ),
    expected_structure_keys=["function", "arguments"],
    expected_tool="Read",
    expected_function_args={"file_path": "docker-compose"},
    expected_contains=["file_path"],
)

EX_FC_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-FC-002",
    capability="function_calling",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "在 src/ 目录下搜索所有包含 'TODO' 或 'FIXME' 标记的代码行。"
        "请生成工具调用，输出 JSON 包含 function 和 arguments 字段，"
        "arguments 中需包含 pattern 和 path。"
    ),
    expected_structure_keys=["function", "arguments"],
    expected_tool="Grep",
    expected_function_args={"pattern": "TODO", "path": "src"},
    expected_contains=["pattern", "path"],
)

EX_FC_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-FC-003",
    capability="function_calling",
    difficulty=Difficulty.HARD,
    prompt=(
        "将 config.py 中的 DEBUG=True 改为 DEBUG=False。"
        "请生成工具调用，输出 JSON 包含 function 和 arguments 字段，"
        "arguments 中需包含 file_path、old_str、new_str 三个参数。"
    ),
    expected_structure_keys=["function", "arguments"],
    expected_tool="Edit",
    expected_function_args={
        "file_path": "config.py",
        "old_str": "DEBUG=True",
        "new_str": "DEBUG=False",
    },
    expected_contains=["file_path", "old_str", "new_str"],
)

# tool_chaining (3 题) — 规划多工具调用顺序
EX_TC_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-TC-001",
    capability="tool_chaining",
    difficulty=Difficulty.EASY,
    prompt=(
        "找到 src/ 下所有包含 'auth' 关键词的文件，然后读取其中一个匹配文件的完整内容。"
        "请规划工具调用顺序，输出 JSON 包含 steps 字段，steps 中每个元素含 tool 字段。"
    ),
    expected_structure_keys=["steps"],
    expected_tool_sequence=["Grep", "Read"],
    expected_contains=["Grep", "Read"],
)

EX_TC_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-TC-002",
    capability="tool_chaining",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "找到项目中所有 .yaml 配置文件，读取其中的 database 配置内容，"
        "然后将数据库端口从 3306 修改为 5432。"
        "请规划工具调用顺序，输出 JSON 包含 steps 字段。"
    ),
    expected_structure_keys=["steps"],
    expected_tool_sequence=["Glob", "Read", "Edit"],
    expected_contains=["Glob", "Read", "Edit"],
)

EX_TC_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-TC-003",
    capability="tool_chaining",
    difficulty=Difficulty.HARD,
    prompt=(
        "搜索代码中 deprecated 函数的所有调用点，读取调用上下文判断是否需要替换，"
        "如需替换则对调用点执行编辑。这是条件链路但整体顺序固定。"
        "请规划工具调用顺序，输出 JSON 包含 steps 字段。"
    ),
    expected_structure_keys=["steps"],
    expected_tool_sequence=["Grep", "Read", "Edit"],
    expected_contains=["Grep", "Read", "Edit"],
)


# ══════════════════════════════════════════════════════════
# K类: 影响分析能力 (15 题)
# ══════════════════════════════════════════════════════════

# impact_analysis (5 题) — 影响分析
EX_IA_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-IA-001",
    capability="impact_analysis",
    difficulty=Difficulty.EASY,
    prompt=(
        "impact analysis: If I modify the helper function in utils.py, which files will be affected?\n"
        "Project structure:\n"
        "  utils.py: def helper(): return 42\n"
        "  main.py: from utils import helper; print(helper())\n"
        "  test_utils.py: from utils import helper; assert helper() == 42\n"
        "List all affected files."
    ),
    expected_structure_keys=["affected_files"],
    expected_affected_files_k=["utils.py", "main.py", "test_utils.py"],
    expected_contains=["main.py", "test_utils"],
)

EX_IA_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-IA-002",
    capability="impact_analysis",
    difficulty=Difficulty.EASY,
    prompt=(
        "impact analysis: If I change the config value in config.py, which files will be affected?\n"
        "Project structure:\n"
        "  config.py: MAX_RETRIES = 3\n"
        "  retry.py: from config import MAX_RETRIES\n"
        "  handler.py: from config import MAX_RETRIES\n"
        "List all affected files."
    ),
    expected_structure_keys=["affected_files"],
    expected_affected_files_k=["config.py", "retry.py", "handler.py"],
    expected_contains=["retry", "handler"],
)

EX_IA_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-IA-003",
    capability="impact_analysis",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "impact analysis: If I modify the interface in interface.py, which files will be affected?\n"
        "Project structure (10 files):\n"
        "  interface.py: class IDataService: def get(self, id): pass\n"
        "  impl1.py: class Service1(IDataService): def get(self, id): return data1\n"
        "  impl2.py: class Service2(IDataService): def get(self, id): return data2\n"
        "  impl3.py: class Service3(IDataService): def get(self, id): return data3\n"
        "  factory.py: def create_service(name): return services[name]\n"
        "  client1.py: from factory import create_service; s = create_service('s1')\n"
        "  client2.py: from factory import create_service; s = create_service('s2')\n"
        "  client3.py: from factory import create_service; s = create_service('s3')\n"
        "  test_impl1.py: from impl1 import Service1\n"
        "  test_impl2.py: from impl2 import Service2\n"
        "List all affected files."
    ),
    expected_structure_keys=["affected_files"],
    expected_affected_files_k=[
        "interface.py",
        "impl1.py",
        "impl2.py",
        "impl3.py",
        "factory.py",
        "client1.py",
        "client2.py",
        "client3.py",
        "test_impl1.py",
        "test_impl2.py",
    ],
    expected_contains=["impl1", "impl2", "factory", "client"],
)

EX_IA_005: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-IA-005",
    capability="impact_analysis",
    difficulty=Difficulty.HARD,
    prompt=(
        "impact analysis: If I modify the core service in core_service.py, which files will be affected?\n"
        "Project structure (25 files):\n"
        "  core_service.py: class CoreService: def process(data): pass\n"
        "  adapter1.py, adapter2.py, adapter3.py, adapter4.py, adapter5.py: all import CoreService\n"
        "  handler1.py, handler2.py, handler3.py, handler4.py, handler5.py: all import adapters\n"
        "  controller1.py, controller2.py, controller3.py, controller4.py, controller5.py: all import handlers\n"
        "  view1.py, view2.py, view3.py, view4.py, view5.py: all import controllers\n"
        "  route1.py, route2.py, route3.py, route4.py, route5.py: all import views\n"
        "List all affected files."
    ),
    expected_structure_keys=["affected_files"],
    expected_affected_files_k=[
        "core_service.py",
        "adapter1.py",
        "adapter2.py",
        "adapter3.py",
        "adapter4.py",
        "adapter5.py",
        "handler1.py",
        "handler2.py",
        "handler3.py",
        "handler4.py",
        "handler5.py",
        "controller1.py",
        "controller2.py",
        "controller3.py",
        "controller4.py",
        "controller5.py",
        "view1.py",
        "view2.py",
        "view3.py",
        "view4.py",
        "view5.py",
        "route1.py",
        "route2.py",
        "route3.py",
        "route4.py",
        "route5.py",
    ],
    expected_contains=["adapter1", "handler1", "controller1", "view1", "route1"],
)

# circular_dependency_detect (5 题) — 循环依赖检测
EX_CDD_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CDD-001",
    capability="circular_dependency_detect",
    difficulty=Difficulty.EASY,
    prompt=(
        "circular dependency check: 分析以下模块是否存在循环依赖。\n"
        "  module_a.py: from module_b import func_b\n"
        "  module_b.py: from module_c import func_c\n"
        "  module_c.py: from module_a import func_a\n"
        "  module_d.py: from module_e import func_e\n"
        "  module_e.py: import os\n"
        "请分析并报告是否存在循环依赖。"
    ),
    expected_structure_keys=["has_cycle", "cycle_path"],
    expected_has_cycle=True,
    expected_cycle_path=["module_a", "module_b", "module_c"],
    expected_contains=["cycle", "module_a", "module_b", "module_c"],
)

EX_CDD_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CDD-002",
    capability="circular_dependency_detect",
    difficulty=Difficulty.EASY,
    prompt=(
        "circular dependency check: 分析以下10个模块是否存在循环依赖。\n"
        "  a.py: from b import b_func\n"
        "  b.py: from c import c_func\n"
        "  c.py: from a import a_func\n"
        "  d.py: from e import e_func\n"
        "  e.py: from f import f_func\n"
        "  f.py: import os\n"
        "  g.py: from h import h_func\n"
        "  h.py: import sys\n"
        "  i.py: from j import j_func\n"
        "  j.py: import json\n"
        "请分析并报告所有循环依赖。"
    ),
    expected_structure_keys=["has_cycle", "cycle_path"],
    expected_has_cycle=True,
    expected_cycle_path=["a", "b", "c"],
    expected_contains=["cycle", "a.py", "b.py", "c.py"],
)

EX_CDD_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CDD-003",
    capability="circular_dependency_detect",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "circular dependency check: Analyze these 10 modules for circular dependencies.\n"
        "  m1.py: from m2 import f2\n"
        "  m2.py: from m3 import f3\n"
        "  m3.py: from m4 import f4\n"
        "  m4.py: from m5 import f5\n"
        "  m5.py: from m1 import f1  # cycle here\n"
        "  m6.py: from m7 import f7\n"
        "  m7.py: from m8 import f8\n"
        "  m8.py: from m9 import f9\n"
        "  m9.py: from m10 import f10\n"
        "  m10.py: import os  # no cycle here\n"
        "Report all cycles found."
    ),
    expected_structure_keys=["has_cycle", "cycle_path"],
    expected_has_cycle=True,
    expected_cycle_path=["m1", "m2", "m3", "m4", "m5"],
    expected_contains=["cycle", "m1", "m5"],
)

EX_CDD_005: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CDD-005",
    capability="circular_dependency_detect",
    difficulty=Difficulty.HARD,
    prompt=(
        "circular dependency check: Analyze these 25 modules for circular dependencies.\n"
        "  core1.py: from core2 import f2\n"
        "  core2.py: from core3 import f3\n"
        "  core3.py: from core1 import f1  # cycle 1\n"
        "  data1.py: from data2 import f2\n"
        "  data2.py: from data3 import f3\n"
        "  data3.py: from data4 import f4\n"
        "  data4.py: from data1 import f1  # cycle 2\n"
        "  ui1.py: from ui2 import f2\n"
        "  ui2.py: from ui3 import f3\n"
        "  ui3.py: from ui1 import f1  # cycle 3\n"
        "  util1.py: from util2 import f2\n"
        "  util2.py: from util3 import f3\n"
        "  util3.py: import os  # no cycle\n"
        "  helper1.py: from helper2 import f2\n"
        "  helper2.py: from helper3 import f3\n"
        "  helper3.py: from helper4 import f4\n"
        "  helper4.py: from helper5 import f5\n"
        "  helper5.py: from helper1 import f1  # cycle 4\n"
        "  base1.py: from base2 import f2\n"
        "  base2.py: from base3 import f3\n"
        "  base3.py: from base4 import f4\n"
        "  base4.py: from base5 import f5\n"
        "  base5.py: import sys  # no cycle\n"
        "  main.py: from core1 import f1\n"
        "Report all cycles found."
    ),
    expected_structure_keys=["has_cycle", "cycle_path"],
    expected_has_cycle=True,
    expected_cycle_path=["core1", "core2", "core3"],
    expected_contains=["cycle", "core1", "data1", "ui1", "helper1"],
)

# rollback_boundary_design (5 题) — 回滚边界设计
EX_RBD_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-RBD-001",
    capability="rollback_boundary_design",
    difficulty=Difficulty.EASY,
    prompt=(
        "rollback design: We are modifying 3 files to add a new feature.\n"
        "  database.py: add new table schema\n"
        "  model.py: add new model class\n"
        "  api.py: add new endpoint\n"
        "Design safe rollback points and boundaries."
    ),
    expected_structure_keys=["rollback_points", "boundaries"],
    expected_rollback_points=["database", "model", "api"],
    expected_contains=["backup", "database.py", "model.py", "api.py"],
)

EX_RBD_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-RBD-002",
    capability="rollback_boundary_design",
    difficulty=Difficulty.EASY,
    prompt=(
        "rollback design: We are refactoring 3 files to change the authentication system.\n"
        "  auth.py: change token validation logic\n"
        "  middleware.py: update auth middleware\n"
        "  routes.py: add new auth routes\n"
        "Design safe rollback points and boundaries."
    ),
    expected_structure_keys=["rollback_points", "boundaries"],
    expected_rollback_points=["auth", "middleware", "routes"],
    expected_contains=["backup", "auth", "middleware"],
)

EX_RBD_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-RBD-003",
    capability="rollback_boundary_design",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "rollback design: We are migrating 10 files from REST to GraphQL.\n"
        "  schema.py, resolvers.py, types.py, models.py, db.py\n"
        "  api_v1.py, api_v2.py, middleware.py, auth.py, cache.py\n"
        "Design safe rollback points and boundaries for this migration."
    ),
    expected_structure_keys=["rollback_points", "boundaries"],
    expected_rollback_points=["schema", "resolvers", "types", "models", "db"],
    expected_contains=["backup", "schema", "resolvers", "migration"],
)

EX_RBD_004: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-RBD-004",
    capability="rollback_boundary_design",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "rollback design: We are splitting a monolithic 10-file module into microservices.\n"
        "  monolith.py, database.py, auth.py, users.py, orders.py\n"
        "  products.py, payments.py, notifications.py, logging.py, config.py\n"
        "Design safe rollback points and boundaries for this split."
    ),
    expected_structure_keys=["rollback_points", "boundaries"],
    expected_rollback_points=["monolith", "database", "auth", "users", "orders"],
    expected_contains=["backup", "monolith", "database", "split"],
)

EX_RBD_005: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-RBD-005",
    capability="rollback_boundary_design",
    difficulty=Difficulty.HARD,
    prompt=(
        "rollback design: We are doing a major architecture upgrade across 25 files.\n"
        "  core1-5.py: core logic changes\n"
        "  data1-5.py: data layer migration\n"
        "  ui1-5.py: UI framework upgrade\n"
        "  api1-5.py: API versioning\n"
        "  config1-5.py: configuration restructuring\n"
        "Design safe rollback points and boundaries for this major upgrade."
    ),
    expected_structure_keys=["rollback_points", "boundaries"],
    expected_rollback_points=["core", "data", "ui", "api", "config"],
    expected_contains=["backup", "core", "data", "upgrade", "boundary"],
)


# ══════════════════════════════════════════════════════════
# L类: 任务规划能力 (11 题)
# ══════════════════════════════════════════════════════════

# task_decomposition (5 题) — 任务分解
EX_TD_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-TD-001",
    capability="task_decomposition",
    difficulty=Difficulty.EASY,
    prompt=(
        "task decomposition: Break down this task into subtasks.\n"
        "Task: Add user registration feature\n"
        "Files to modify: models.py (add User model), views.py (add register view), urls.py (add route)\n"
        "Decompose into executable subtasks."
    ),
    expected_structure_keys=["tasks"],
    expected_tasks=["models", "views", "urls"],
    expected_contains=["models.py", "views.py", "urls.py", "register"],
)

EX_TD_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-TD-002",
    capability="task_decomposition",
    difficulty=Difficulty.EASY,
    prompt=(
        "task decomposition: Break down this task into subtasks.\n"
        "Task: Implement password reset\n"
        "Files: auth.py (reset logic), email.py (send email), templates.py (reset form)\n"
        "Decompose into executable subtasks."
    ),
    expected_structure_keys=["tasks"],
    expected_tasks=["auth", "email", "templates"],
    expected_contains=["auth", "email", "template", "reset"],
)

EX_TD_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-TD-003",
    capability="task_decomposition",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "task decomposition: Break down this complex task into subtasks.\n"
        "Task: Migrate from monolith to microservices\n"
        "Files: monolith.py, db.py, auth.py, users.py, orders.py, products.py, payments.py, notifications.py, api_gateway.py, config.py\n"
        "Decompose into executable subtasks."
    ),
    expected_structure_keys=["tasks"],
    expected_tasks=["monolith", "db", "auth", "users", "orders"],
    expected_contains=["monolith", "database", "auth", "users", "orders", "microservice"],
)

EX_TD_004: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-TD-004",
    capability="task_decomposition",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "task decomposition: Break down this complex task into subtasks.\n"
        "Task: Add real-time chat feature\n"
        "Files: websocket.py, chat_model.py, chat_service.py, chat_ui.py, notification.py, presence.py, history.py, file_upload.py, encryption.py, config.py\n"
        "Decompose into executable subtasks."
    ),
    expected_structure_keys=["tasks"],
    expected_tasks=["websocket", "chat_model", "chat_service", "chat_ui", "notification"],
    expected_contains=["websocket", "chat", "service", "notification", "presence"],
)

EX_TD_005: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-TD-005",
    capability="task_decomposition",
    difficulty=Difficulty.HARD,
    prompt=(
        "task decomposition: Break down this major task into subtasks.\n"
        "Task: Complete architecture upgrade\n"
        "Files: core1-5.py, data1-5.py, ui1-5.py, api1-5.py, config1-5.py (25 files total)\n"
        "Decompose into executable subtasks with clear dependencies."
    ),
    expected_structure_keys=["tasks"],
    expected_tasks=["core", "data", "ui", "api", "config"],
    expected_contains=["core1", "data1", "ui1", "api1", "config1", "upgrade"],
)

# parallel_planning (3 题) — 并行规划
EX_PP_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-PP-001",
    capability="parallel_planning",
    difficulty=Difficulty.EASY,
    prompt=(
        "parallel planning: Which of these tasks can run in parallel?\n"
        "Tasks:\n"
        "  A: Update models.py (no dependencies)\n"
        "  B: Update views.py (depends on A)\n"
        "  C: Update tests.py (depends on A and B)\n"
        "Identify parallel groups."
    ),
    expected_structure_keys=["parallel_groups"],
    expected_parallel_groups=[["A"], ["B"], ["C"]],
    expected_contains=["parallel", "sequential", "models.py", "views.py", "tests.py"],
)

EX_PP_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-PP-002",
    capability="parallel_planning",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "parallel planning: Which of these 10 tasks can run in parallel?\n"
        "Tasks:\n"
        "  T1: Update database schema (no deps)\n"
        "  T2: Update models (depends on T1)\n"
        "  T3: Update auth (no deps)\n"
        "  T4: Update users API (depends on T2, T3)\n"
        "  T5: Update orders API (depends on T2)\n"
        "  T6: Update products API (depends on T2)\n"
        "  T7: Update payments (depends on T4)\n"
        "  T8: Update notifications (depends on T3)\n"
        "  T9: Update logging (no deps)\n"
        "  T10: Update config (no deps)\n"
        "Identify parallel groups."
    ),
    expected_structure_keys=["parallel_groups"],
    expected_parallel_groups=[["T1", "T3", "T9", "T10"], ["T2", "T8"], ["T4", "T5", "T6"], ["T7"]],
    expected_contains=["parallel", "T1", "T3", "T9", "T10"],
)

EX_PP_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-PP-003",
    capability="parallel_planning",
    difficulty=Difficulty.HARD,
    prompt=(
        "parallel planning: Which of these 25 tasks can run in parallel?\n"
        "Tasks (25 total):\n"
        "  Core layer: C1-C5 (C1 no deps, C2 depends C1, C3 depends C2, C4 depends C3, C5 depends C4)\n"
        "  Data layer: D1-D5 (D1 no deps, D2-D5 depend on D1)\n"
        "  UI layer: U1-U5 (U1-U5 all depend on C5)\n"
        "  API layer: A1-A5 (A1-A5 all depend on C5 and D5)\n"
        "  Config layer: F1-F5 (F1-F5 no deps, can all run in parallel)\n"
        "Identify parallel groups."
    ),
    expected_structure_keys=["parallel_groups"],
    expected_parallel_groups=[["C1", "D1", "F1", "F2", "F3", "F4", "F5"]],
    expected_contains=["parallel", "C1", "D1", "F1", "F2"],
)

# dependency_ordering (3 题) — 依赖排序
EX_DO_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-DO-001",
    capability="dependency_ordering",
    difficulty=Difficulty.EASY,
    prompt=(
        "dependency ordering: Sort these tasks by dependency.\n"
        "Tasks:\n"
        "  A: Write tests (depends on B)\n"
        "  B: Implement feature\n"
        "  C: Deploy (depends on A)\n"
        "Provide the correct execution order."
    ),
    expected_structure_keys=["order"],
    expected_order=["B", "A", "C"],
    expected_contains=["B: Implement", "A: Write tests", "C: Deploy", "order"],
)

EX_DO_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-DO-002",
    capability="dependency_ordering",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "dependency ordering: Sort these 10 tasks by dependency.\n"
        "Tasks:\n"
        "  T1: Database migration (no deps)\n"
        "  T2: Update models (depends on T1)\n"
        "  T3: Update services (depends on T2)\n"
        "  T4: Update controllers (depends on T3)\n"
        "  T5: Update views (depends on T4)\n"
        "  T6: Update API routes (depends on T5)\n"
        "  T7: Write unit tests (depends on T3)\n"
        "  T8: Write integration tests (depends on T6)\n"
        "  T9: Update documentation (depends on T6)\n"
        "  T10: Deploy (depends on T8, T9)\n"
        "Provide the correct execution order."
    ),
    expected_structure_keys=["order"],
    expected_order=["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10"],
    expected_contains=["T1", "T2", "T3", "order"],
)

EX_DO_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-DO-003",
    capability="dependency_ordering",
    difficulty=Difficulty.HARD,
    prompt=(
        "dependency ordering: Sort these 25 tasks by dependency.\n"
        "Tasks:\n"
        "  Phase 1 (Foundation): F1-F5 (F1 no deps, F2 depends F1, F3 depends F2, F4 depends F3, F5 depends F4)\n"
        "  Phase 2 (Core): C1-C5 (C1 depends F5, C2 depends C1, C3 depends C2, C4 depends C3, C5 depends C4)\n"
        "  Phase 3 (Features): P1-P5 (P1 depends C5, P2 depends C5, P3 depends C5, P4 depends C5, P5 depends C5)\n"
        "  Phase 4 (Integration): I1-I5 (I1 depends P1, I2 depends P2, I3 depends P3, I4 depends P4, I5 depends P5)\n"
        "  Phase 5 (Deployment): D1-D5 (D1 depends I1, D2 depends I2, D3 depends I3, D4 depends I4, D5 depends I5)\n"
        "Provide the correct execution order."
    ),
    expected_structure_keys=["order"],
    expected_order=["F1", "F2", "F3", "F4", "F5", "C1", "C2", "C3", "C4", "C5"],
    expected_contains=["F1", "F2", "C1", "C2", "order"],
)


# ══════════════════════════════════════════════════════════
# M类: 上下文管理能力 (11 题)
# ══════════════════════════════════════════════════════════

# cross_file_hallucination_detect (5 题) — 跨文件幻觉检测
EX_CFHD_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CFHD-001",
    capability="hallucination_detect",
    difficulty=Difficulty.EASY,
    prompt=(
        "hallucination check: A developer claims these 3 files exist and were modified:\n"
        "  utils.py: contains helper() function\n"
        "  main.py: imports helper from utils\n"
        "  fake_module.py: imports nonexistent_func from utils  # THIS FILE DOES NOT EXIST\n"
        "Detect any hallucinated/nonexistent files or functions."
    ),
    expected_structure_keys=["has_hallucination", "hallucinated_items"],
    expected_has_hallucination=True,
    expected_hallucinated_items=["fake_module.py", "nonexistent_func"],
    expected_contains=["hallucination", "fake_module", "nonexistent"],
)

EX_CFHD_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CFHD-002",
    capability="hallucination_detect",
    difficulty=Difficulty.EASY,
    prompt=(
        "hallucination check: An AI assistant made these claims about 3 files:\n"
        "  config.py: has MAX_RETRIES = 3\n"
        "  retry.py: imports MAX_RETRIES from config\n"
        "  cache.py: imports REDIS_URL from config  # config.py does NOT contain REDIS_URL\n"
        "Detect any hallucinated/nonexistent imports or functions."
    ),
    expected_structure_keys=["has_hallucination", "hallucinated_items"],
    expected_has_hallucination=True,
    expected_hallucinated_items=["REDIS_URL"],
    expected_contains=["hallucination", "REDIS_URL", "cache"],
)

EX_CFHD_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CFHD-003",
    capability="hallucination_detect",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "hallucination check: An AI assistant analyzed 10 files and made these claims:\n"
        "  model.py: has User class\n"
        "  dao.py: has save_user() function\n"
        "  service.py: has process_user() function\n"
        "  api.py: has /users endpoint\n"
        "  auth.py: has authenticate() function\n"
        "  fake_service.py: has validate_user()  # DOES NOT EXIST\n"
        "  phantom.py: has send_email()  # DOES NOT EXIST\n"
        "  ghost.py: has log_event()  # DOES NOT EXIST\n"
        "  real_helper.py: has format_date()\n"
        "  utils.py: has helper()\n"
        "Detect all hallucinated/nonexistent files or functions."
    ),
    expected_structure_keys=["has_hallucination", "hallucinated_items"],
    expected_has_hallucination=True,
    expected_hallucinated_items=[
        "fake_service.py",
        "phantom.py",
        "ghost.py",
        "validate_user",
        "send_email",
        "log_event",
    ],
    expected_contains=["hallucination", "fake_service", "phantom", "ghost"],
)

EX_CFHD_004: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CFHD-004",
    capability="hallucination_detect",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "hallucination check: An AI assistant claimed to have read 10 files and found these imports:\n"
        "  main.py: from database import Database  # database.py exists\n"
        "  models.py: from database import User  # database.py does NOT have User class\n"
        "  views.py: from models import UserView  # models.py does NOT have UserView\n"
        "  controllers.py: from views import UserView  # views.py does NOT have UserView\n"
        "  services.py: from controllers import UserController  # controllers.py does NOT have UserController\n"
        "  auth.py: from services import AuthService  # services.py does NOT have AuthService\n"
        "  api.py: from auth import AuthMiddleware  # auth.py does NOT have AuthMiddleware\n"
        "  config.py: from api import APIClient  # api.py does NOT have APIClient\n"
        "  utils.py: from config import ConfigManager  # config.py does NOT have ConfigManager\n"
        "  helpers.py: from utils import format_date  # utils.py exists and has format_date\n"
        "Detect all hallucinated/nonexistent imports."
    ),
    expected_structure_keys=["has_hallucination", "hallucinated_items"],
    expected_has_hallucination=True,
    expected_hallucinated_items=[
        "User",
        "UserView",
        "UserController",
        "AuthService",
        "AuthMiddleware",
        "APIClient",
        "ConfigManager",
    ],
    expected_contains=["hallucination", "UserView", "AuthService", "ConfigManager"],
)

EX_CFHD_005: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CFHD-005",
    capability="hallucination_detect",
    difficulty=Difficulty.HARD,
    prompt=(
        "hallucination check: An AI assistant analyzed a 25-file project and made these claims:\n"
        "  core1-5.py: all exist and have correct functions\n"
        "  data1-5.py: all exist, but data3.py claims to import 'validate_schema' from data1.py which does NOT exist\n"
        "  ui1-5.py: all exist, but ui2.py claims to import 'render_component' from ui1.py which does NOT exist\n"
        "  api1-5.py: all exist, but api4.py claims to import 'authenticate_request' from api1.py which does NOT exist\n"
        "  config1-5.py: all exist, but config5.py claims to import 'load_env' from config1.py which does NOT exist\n"
        "  Also, the AI claimed there's a file 'phantom_module.py' that does NOT exist in the project\n"
        "Detect all hallucinated/nonexistent files and functions."
    ),
    expected_structure_keys=["has_hallucination", "hallucinated_items"],
    expected_has_hallucination=True,
    expected_hallucinated_items=[
        "validate_schema",
        "render_component",
        "authenticate_request",
        "load_env",
        "phantom_module.py",
    ],
    expected_contains=["hallucination", "validate_schema", "render_component", "phantom"],
)

# context_freshness_awareness (3 题) — 上下文新鲜度感知
# 注: 使用 EX_CFAW 前缀避免与 cross_file_analysis 的 EX_CFA 冲突
EX_CFAW_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CFAW-001",
    capability="context_management",
    difficulty=Difficulty.EASY,
    prompt=(
        "context freshness: Analyze this conversation for context degradation.\n"
        "Conversation (5 turns):\n"
        "  Turn 1: User asks about file A\n"
        "  Turn 2: AI reads file A and responds\n"
        "  Turn 3: User asks about file B\n"
        "  Turn 4: AI reads file B and responds\n"
        "  Turn 5: User asks 'what did we discuss in turn 1?'\n"
        "Is the context degraded? What's your recommendation?"
    ),
    expected_structure_keys=["context_degraded", "reason"],
    expected_context_degraded=False,
    expected_contains=["fresh", "not degraded", "no degradation"],
)

EX_CFAW_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CFAW-002",
    capability="context_management",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "context freshness: Analyze this conversation for context degradation.\n"
        "Conversation (20 turns):\n"
        "  Turns 1-5: Discussion about database schema\n"
        "  Turns 6-10: Discussion about API design\n"
        "  Turns 11-15: Discussion about UI components\n"
        "  Turns 16-20: User asks 'based on our earlier discussion, what should the schema look like?'\n"
        "The AI responds with a schema that contradicts what was discussed in turns 1-5.\n"
        "Is the context degraded? What's your recommendation?"
    ),
    expected_structure_keys=["context_degraded", "reason"],
    expected_context_degraded=True,
    expected_contains=["degraded", "new session", "contradiction"],
)

EX_CFAW_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CFAW-003",
    capability="context_management",
    difficulty=Difficulty.HARD,
    prompt=(
        "context freshness: Analyze this conversation for context degradation.\n"
        "Conversation (35 turns):\n"
        "  Turns 1-10: Initial architecture discussion\n"
        "  Turns 11-20: Implementation details\n"
        "  Turns 21-30: Bug fixing and testing\n"
        "  Turn 31: User asks 'what was our original architecture decision?'\n"
        "  Turn 32: AI gives an answer that partially contradicts turns 1-10\n"
        "  Turn 33: User asks 'are you sure?'\n"
        "  Turn 34: AI changes its answer\n"
        "  Turn 35: User asks 'what should we do next?'\n"
        "Is the context degraded? What's your recommendation?"
    ),
    expected_structure_keys=["context_degraded", "reason"],
    expected_context_degraded=True,
    expected_contains=["degraded", "new session", "contradiction", "inconsistency"],
)

# context_window_management (3 题) — 上下文窗口管理
EX_CWM_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CWM-001",
    capability="context_management",
    difficulty=Difficulty.EASY,
    prompt=(
        "context management: Should we start a new session?\n"
        "Current session: 45 turns, discussing 3 different unrelated topics\n"
        "  Topic 1: Database migration (turns 1-15)\n"
        "  Topic 2: UI redesign (turns 16-30)\n"
        "  Topic 3: API refactoring (turns 31-45)\n"
        "The AI has started giving generic answers and forgetting earlier context.\n"
        "Should we start a new session? What's your context strategy?"
    ),
    expected_structure_keys=["should_start_new_session", "reason"],
    expected_new_session=True,
    expected_contains=["new session", "yes, start", "degraded"],
)

EX_CWM_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CWM-002",
    capability="context_management",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "context management: Should we start a new session?\n"
        "Current session: 25 turns, all focused on the same feature implementation\n"
        "  Turns 1-10: Design discussion\n"
        "  Turns 11-20: Implementation\n"
        "  Turns 21-25: Testing and bug fixes\n"
        "The AI is still performing well and remembering all context.\n"
        "Should we start a new session? What's your context strategy?"
    ),
    expected_structure_keys=["should_start_new_session", "reason"],
    expected_new_session=False,
    expected_contains=["no, continue", "fresh", "performing well"],
)

EX_CWM_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CWM-003",
    capability="context_management",
    difficulty=Difficulty.HARD,
    prompt=(
        "context management: Should we start a new session?\n"
        "Current session: 30 turns\n"
        "  Turns 1-15: Complex architecture discussion with many decisions\n"
        "  Turns 16-25: Implementation that partially contradicts earlier decisions\n"
        "  Turns 26-30: User is confused about which decisions are final\n"
        "The AI is giving contradictory answers and seems confused.\n"
        "Should we start a new session? What's your context strategy?"
    ),
    expected_structure_keys=["should_start_new_session", "reason"],
    expected_new_session=True,
    expected_contains=["new session", "yes, start", "contradiction", "degraded"],
)


# ══════════════════════════════════════════════════════════
# 高区分度hard题 (3题, 8B模型基本做不对, 顶级模型能做对)
# ══════════════════════════════════════════════════════════

EX_CDD_004: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-CDD-004",
    capability="circular_dependency_detect",
    difficulty=Difficulty.HARD,
    prompt=(
        "detect circular dependency in these modules:\n"
        "auth.py imports session.py\n"
        "session.py imports user.py\n"
        "user.py imports permission.py\n"
        "permission.py imports role.py\n"
        "role.py imports auth.py"
    ),
    expected_structure_keys=["has_cycle", "cycle_path"],
    expected_has_cycle=True,
    expected_cycle_path=["auth", "session", "user", "permission", "role"],
    expected_contains=["auth", "session", "user", "permission", "role"],
)

EX_IA_004: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-IA-004",
    capability="impact_analysis",
    difficulty=Difficulty.HARD,
    prompt=(
        "analyze impact of changing utils.py:\n"
        "main.py imports utils.py\n"
        "api.py imports utils.py\n"
        "models.py imports utils.py\n"
        "views.py imports utils.py\n"
        "tests/test_main.py imports main.py\n"
        "tests/test_api.py imports api.py\n"
        "tests/test_models.py imports models.py\n"
        "config.py imports utils.py\n"
        "helpers.py imports utils.py\n"
        "services.py imports utils.py"
    ),
    expected_structure_keys=["affected_files"],
    expected_affected_files_k=["main.py", "api.py", "models.py", "views.py", "config.py", "helpers.py", "services.py"],
    expected_contains=["main", "api", "models", "views", "config", "helpers", "services"],
)

EX_SR_004: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-SR-004",
    capability="self_review",
    difficulty=Difficulty.HARD,
    prompt=(
        "review this code for bugs:\n"
        "def process_items(items):\n"
        "    result = []\n"
        "    for i in range(len(items)):\n"
        "        if items[i] > 0:\n"
        "            result.append(items[i] * 2)\n"
        "        if items[i] > 100:\n"
        "            result.append(items[i] * 3)\n"
        "    return result"
    ),
    expected_structure_keys=["has_bug", "bugs"],
    expected_has_bug=True,
    expected_bug_location="double append",
    expected_contains=["double", "append", "overlap"],
)

# 审查2.2修复: self_review 负例对照组 (防止"总是报bug"退化策略拿满分)
EX_SR_005: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-SR-005",
    capability="self_review",
    difficulty=Difficulty.MEDIUM,
    prompt=(
        "review this code for bugs:\n"
        "def calculate_average(numbers):\n"
        "    if not numbers:\n"
        "        return 0\n"
        "    total = sum(numbers)\n"
        "    return total / len(numbers)"
    ),
    expected_structure_keys=["has_bug", "bugs"],
    expected_has_bug=False,
    expected_bug_location="",
    expected_contains=["no bug", "correct", "clean"],
)


# ══════════════════════════════════════════════════════════
# v3.0.5 奥赛级附加题 (6 道) — 极限深度，参与奥赛封顶
# 设计目标: deepseek-v4-pro-thinking 通过率<50%, Opus级 50-75%, 无人满分
# ══════════════════════════════════════════════════════════

# EX_OLY_001: architecture_design OLYMPIAD — 多租户微服务电商订单系统 (20+文件)
EX_OLY_001: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-OLY-001",
    capability="architecture_design",
    difficulty=Difficulty.OLYMPIAD,
    prompt=(
        "设计一个支持多租户的微服务电商订单系统。要求拆分为 20 个以上独立微服务文件。\n\n"
        "【8 个业务领域，每个至少 1 个服务文件】\n"
        "1. 用户域(user): 账户/认证/画像\n"
        "2. 商品域(product): 目录/SKU/库存\n"
        "3. 订单域(order): 下单/履约/状态机\n"
        "4. 支付域(payment): 渠道/对账/退款\n"
        "5. 库存域(inventory): 占用/扣减/预占\n"
        "6. 物流域(shipping): 发货/追踪/签收\n"
        "7. 通知域(notification): 站内信/短信/推送\n"
        "8. 分析域(analytics): 埋点/报表/漏斗\n\n"
        "【6 个非功能需求，需有专门组件承载】\n"
        "A. 多租户隔离(tenant isolation): 数据与配额隔离\n"
        "B. 水平扩展(horizontal scale): 无状态+分片\n"
        "C. 最终一致性(eventual consistency): 事件驱动+Saga\n"
        "D. 幂等(idempotent): 重试安全\n"
        "E. 可观测(observability): 链路追踪trace+指标\n"
        "F. 灰度发布(gray release): 流量按比例切分\n\n"
        "输出 JSON: {\"files\": [...文件名...], \"dependencies\": [{\"from\":\"X\",\"to\":\"Y\"}, ...]}"
    ),
    expected_structure_keys=["files", "dependencies"],
    expected_contains=[
        "user_service", "product_service", "order_service", "payment_service",
        "inventory_service", "shipping_service", "notification_service", "analytics_service",
        "tenant", "scale", "consistency", "idempotent", "observability", "trace", "gray",
    ],
)

# EX_OLY_002: hallucination_detect OLYMPIAD — 30 条声称中 12 条幻觉
EX_OLY_002: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-OLY-002",
    capability="hallucination_detect",
    difficulty=Difficulty.OLYMPIAD,
    prompt=(
        "审阅以下技术方案文档，找出所有幻觉(编造/不存在/错误)的声称。\n"
        "输出 JSON: {\"hallucinations\": [{\"item\": \"幻觉内容\", \"reason\": \"为何是幻觉\"}, ...]}"
    ),
    expected_structure_keys=["hallucinations"],
    expected_hallucinations=[
        "fastjsonx 3.0", "redis-py-cluster-plus", "PyTTLCache",
        "Ollama.function_call", "SQLAlchemy.atomic_batch",
        "kombu_rpc", "psycopg3-async-pool", "uvicorn.experimental_workers",
        "Pydantic.serial_validator", "httpx.retry_policy",
        "aiohttp.thread_executor", "FastAPI.dependency_scope",
    ],
    input_files={
        "proposal.md": (
            "# 技术方案：异步订单处理服务\n\n"
            "## 选型声称（共 30 条，请核查真伪）\n\n"
            "1. 使用 fastjsonx 3.0 做高性能 JSON 序列化。\n"  # 幻觉：fastjsonx 不存在
            "2. 使用 redis-py-cluster-plus 管理分布式缓存集群。\n"  # 幻觉：库不存在
            "3. 使用 PyTTLCache 实现 TTL+LRU 内存缓存。\n"  # 幻觉：库不存在
            "4. 使用 Ollama.function_call 做结构化输出。\n"  # 幻觉：方法不存在
            "5. 使用 SQLAlchemy.atomic_batch 做原子批量提交。\n"  # 幻觉：方法不存在
            "6. 使用 kombu_rpc 做异步任务队列。\n"  # 幻觉：库不存在
            "7. 使用 psycopg3-async-pool 做异步连接池。\n"  # 幻觉：库不存在
            "8. 使用 uvicorn.experimental_workers 提升并发。\n"  # 幻觉：参数不存在
            "9. 使用 Pydantic.serial_validator 做字段校验。\n"  # 幻觉：方法不存在
            "10. 使用 httpx.retry_policy 配置重试。\n"  # 幻觉：参数不存在
            "11. 使用 aiohttp.thread_executor 做线程池。\n"  # 幻觉：参数不存在
            "12. 使用 FastAPI.dependency_scope 管理依赖生命周期。\n"  # 幻觉：方法不存在
            "13. 使用 Redis 做分布式锁（redlock 算法）。\n"  # 真实
            "14. 使用 PostgreSQL 14 的 LISTEN/NOTIFY。\n"  # 真实
            "15. 使用 RabbitMQ 做消息中间件（AMQP 协议）。\n"  # 真实
            "16. 使用 Celery 做定时任务调度（beat 组件）。\n"  # 真实
            "17. 使用 Kafka 做事件流（partition 机制）。\n"  # 真实
            "18. 使用 Elasticsearch 做全文检索（倒排索引）。\n"  # 真实
            "19. 使用 Prometheus + Grafana 做监控。\n"  # 真实
            "20. 使用 OpenTelemetry 做链路追踪（trace context）。\n"  # 真实
            "21. 使用 Docker 做容器化（cgroups 隔离）。\n"  # 真实
            "22. 使用 Kubernetes 做编排（namespace 隔离）。\n"  # 真实
            "23. 使用 Nginx 做反向代理（upstream 负载均衡）。\n"  # 真实
            "24. 使用 gunicorn 做 WSGI 服务器（pre-fork 模型）。\n"  # 真实
            "25. 使用 pytest 做单元测试（fixture 机制）。\n"  # 真实
            "26. 使用 mypy 做静态类型检查。\n"  # 真实
            "27. 使用 ruff 做代码 lint。\n"  # 真实
            "28. 使用 GitHub Actions 做 CI（workflow 机制）。\n"  # 真实
            "29. 使用 Vault 做密钥管理（secrets engine）。\n"  # 真实
            "30. 使用 Sentry 做错误采集（DSN 配置）。\n"  # 真实
        )
    },
)

# EX_OLY_003: dependency_trace OLYMPIAD — 8 文件深度调用链
EX_OLY_003: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-OLY-003",
    capability="dependency_trace",
    difficulty=Difficulty.OLYMPIAD,
    prompt=(
        "分析以下 8 个 Python 文件的调用关系，给出从入口到最深层的完整调用链。\n"
        "输出 JSON: {\"call_chain\": [\"func_a\", \"func_b\", ...]}"
    ),
    expected_structure_keys=["call_chain"],
    expected_call_chain=[
        "handle_request", "route_api", "validate_input", "process_order",
        "query_inventory", "map_record", "fetch_cache", "check_policy",
    ],
    input_files={
        "a_handler.py": (
            "from b_router import route_api\n"
            "def handle_request(req):\n"
            "    return route_api(req.path, req.body)\n"
        ),
        "b_router.py": (
            "from c_validator import validate_input\n"
            "def route_api(path, body):\n"
            "    data = validate_input(body)\n"
            "    return process_order(data)\n"
            "from d_service import process_order\n"
        ),
        "c_validator.py": (
            "def validate_input(body):\n"
            "    if not body.get('sku'):\n"
            "        raise ValueError('missing sku')\n"
            "    return body\n"
        ),
        "d_service.py": (
            "from e_repository import query_inventory\n"
            "def process_order(data):\n"
            "    stock = query_inventory(data['sku'])\n"
            "    return {'ok': stock > 0}\n"
        ),
        "e_repository.py": (
            "from f_mapper import map_record\n"
            "def query_inventory(sku):\n"
            "    row = db.fetch(sku)\n"
            "    return map_record(row)\n"
        ),
        "f_mapper.py": (
            "from g_cache import fetch_cache\n"
            "def map_record(row):\n"
            "    cached = fetch_cache(row.id)\n"
            "    return cached or row.qty\n"
        ),
        "g_cache.py": (
            "from h_policy import check_policy\n"
            "def fetch_cache(key):\n"
            "    if check_policy(key):\n"
            "        return redis.get(key)\n"
            "    return None\n"
        ),
        "h_policy.py": (
            "def check_policy(key):\n"
            "    return key.startswith('vip_')\n"
        ),
    },
)

# EX_OLY_004: code_generate OLYMPIAD — TTL+LRU+并发安全缓存装饰器
EX_OLY_004: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-OLY-004",
    capability="code_generate",
    difficulty=Difficulty.OLYMPIAD,
    prompt=(
        "实现一个缓存装饰器 cached_decorator，要求同时满足：\n"
        "1. TTL 过期：超过 ttl 秒的缓存自动失效\n"
        "2. LRU 淘汰：容量达到 maxsize 时淘汰最久未使用项\n"
        "3. 并发安全：多线程下无竞态（用 threading.Lock）\n"
        "4. 异步刷新：缓存命中但即将过期（剩余<TTL*0.2）时，后台线程刷新\n\n"
        "签名: def cached_decorator(ttl=60, maxsize=128)\n"
        "输出 JSON: {\"content\": \"<完整可执行Python代码>\"}"
    ),
    expected_structure_keys=["content"],
    expected_test_cases=[
        "import time, threading\nfrom functools import wraps\ncalls = []\n@cached_decorator(ttl=1, maxsize=2)\ndef f(x):\n    calls.append(x)\n    return x*2\nassert f(1)==2 and f(1)==2\nassert len(calls)==1",
        "import time\n@cached_decorator(ttl=1, maxsize=2)\ndef g(x):\n    return x+1\ng(1); g(2); g(3)\nassert g(1)==2",
        "import threading\n@cached_decorator(ttl=10, maxsize=100)\ndef h(x):\n    return x\nresults = []\ndef worker():\n    results.append(h(42))\nthreads = [threading.Thread(target=worker) for _ in range(10)]\n[t.start() for t in threads]; [t.join() for t in threads]\nassert all(r==42 for r in results)",
        "import time\n@cached_decorator(ttl=1, maxsize=10)\ndef k(x):\n    return x\nk(1); time.sleep(1.1); assert k(1)==1",
        "import threading\n@cached_decorator(ttl=10, maxsize=1)\ndef m(x):\n    return x\nm(1); m(2); assert m(1)==1",
        "dec = cached_decorator(ttl=60, maxsize=128)\nassert callable(dec)",
    ],
)

# EX_OLY_005: parallel_planning OLYMPIAD — 15 任务 DAG
EX_OLY_005: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-OLY-005",
    capability="parallel_planning",
    difficulty=Difficulty.OLYMPIAD,
    prompt=(
        "给定 15 个任务的依赖关系（DAG），按依赖拓扑分层，输出可并行执行的分组。\n"
        "约束: 同层任务可并行；每层≥1任务；单任务也是组；遵守依赖（被依赖任务先执行）。\n"
        "输出 JSON: {\"parallel_groups\": [[\"t1\",\"t2\"], [\"t3\"], ...]}"
    ),
    expected_structure_keys=["parallel_groups"],
    expected_parallel_groups=[
        ["T1", "T2", "T3"],
        ["T4", "T5", "T6"],
        ["T7", "T8", "T9"],
        ["T10", "T11"],
        ["T12", "T13"],
        ["T14", "T15"],
    ],
    input_files={
        "tasks.yaml": (
            "tasks:\n"
            "  T1: {deps: [], res: db}\n"
            "  T2: {deps: [], res: db}\n"
            "  T3: {deps: [], res: cache}\n"
            "  T4: {deps: [T1], res: db}\n"
            "  T5: {deps: [T2], res: mq}\n"
            "  T6: {deps: [T3], res: cache}\n"
            "  T7: {deps: [T4], res: db}\n"
            "  T8: {deps: [T5], res: mq}\n"
            "  T9: {deps: [T6], res: cache}\n"
            "  T10: {deps: [T7, T8], res: db}\n"
            "  T11: {deps: [T9], res: cache}\n"
            "  T12: {deps: [T10], res: db}\n"
            "  T13: {deps: [T11], res: cache}\n"
            "  T14: {deps: [T12, T13], res: db}\n"
            "  T15: {deps: [T14], res: db}\n"
        )
    },
)

# EX_OLY_006: context_consistency OLYMPIAD — 6 份矛盾文档
EX_OLY_006: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-OLY-006",
    capability="context_consistency",
    difficulty=Difficulty.OLYMPIAD,
    prompt=(
        "审阅以下 6 份设计文档，判断是否存在矛盾(consistent=false)，并列出所有冲突点。\n"
        "输出 JSON: {\"consistent\": false, \"conflicts\": [\"冲突描述1\", ...]}"
    ),
    expected_structure_keys=["consistent", "conflicts"],
    expected_contains=[
        "order_id", "string", "integer",   # API vs DB 类型矛盾
        "redis", "ttl", "3600", "900",       # 缓存策略矛盾
        "rate_limit", "100", "500",          # 限流矛盾
        "error_code", "4001", "40001",       # 错误码矛盾
        "log_level", "DEBUG", "INFO",       # 日志矛盾
    ],
    input_files={
        "api_spec.md": "订单接口 POST /orders\n字段: order_id (string), user_id (string), amount (float)\n返回: 201 Created",
        "db_schema.md": "表 orders\n列: order_id (INTEGER PK), user_id (VARCHAR), amount (DECIMAL)\n索引: idx_user",
        "cache_strategy.md": "缓存策略: 使用 Redis\norder 缓存 TTL = 900 秒\nkey 格式: order:{id}",
        "rate_limit_policy.md": "限流策略: /orders 接口\n配额: 500 次/分钟 per user\n超限返回 429",
        "logging_standard.md": "日志规范: 订单服务日志级别 = DEBUG\n格式: JSON structured\n输出: stdout",
        "error_code_table.md": "错误码表:\n4001 = 订单不存在\n4002 = 库存不足\n40001 = 参数错误\n40002 = 鉴权失败",
    },
)


# ══════════════════════════════════════════════════════════
# v3.0.5 Phase 3: 极限深度——真实多文件注入 OLYMPIAD 题
# 从项目 src/scripts 下读取真实治理文件 + 埋针/埋错，测大型工业能力。
# ══════════════════════════════════════════════════════════

# EX_OLY_007: architecture_design OLYMPIAD — 5 真实治理文件 + 1 埋错文件
_OLY_007_FILES = [
    "src/zephyr/trading/task_gate.py",
    "scripts/git_commit.py",
    "scripts/governance/verify_schema_health.py",
    "scripts/governance/diagnose_depgraph.py",
    "scripts/governance/d11_compliance/audit_registration.py",
]
_OLY_007_NEEDLES = [
    {  # 在 task_gate.py 注入一条不存在的跨文件依赖
        "file": "task_gate.py",
        "content": "from zephyr.governance.ghost_router import route_ghost_request  # cross-file dep",
        "after": "from zephyr.intelligence.model_profiling.capability_passport import CapabilityPassport",
    },
]
_OLY_007_GHOST_FILE = (  # 完全伪造的文件（埋错文件）
    "ghost_router.py",
    (
        '"""Ghost router module — fabricated for architecture review."""\n'
        "from zephyr.security.phantom_lock import acquire_phantom_session\n\n"
        "def route_ghost_request(task_id, capability):\n"
        '    """Route task to ghost executor (hallucinated function)."""\n'
        "    lock = acquire_phantom_session(task_id)\n"
        "    return lock.dispatch(capability)\n"
    ),
)
_OLY_007_CONTEXT = assemble_real_context(
    _OLY_007_FILES,
    _OLY_007_NEEDLES,
    max_chars_per_file=8000,
    extra_files={_OLY_007_GHOST_FILE[0]: _OLY_007_GHOST_FILE[1]},
)

EX_OLY_007: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-OLY-007",
    capability="architecture_design",
    difficulty=Difficulty.OLYMPIAD,
    prompt=(
        "审阅以下真实多文件架构（5 个治理文件 + 1 个埋错文件），完成架构审查：\n"
        "1. 还原文件清单与跨文件依赖关系（输出 files + dependencies）\n"
        "2. 找出依赖断裂（引用了不存在模块的 import）\n"
        "3. 找出幻觉函数（伪造/不存在的方法）\n\n"
        "输出 JSON: {\"files\": [...], \"dependencies\": [{\"from\":\"X\",\"to\":\"Y\"}], "
        "\"broken_dependencies\": [...], \"hallucinated_items\": [...]}\n\n"
        + _OLY_007_CONTEXT
    ),
    expected_structure_keys=["files", "dependencies"],
    expected_contains=["ghost_router", "route_ghost_request", "phantom_lock"],
    expected_hallucinations=["ghost_router", "route_ghost_request", "acquire_phantom_session"],
)

# EX_OLY_008: hallucination_detect OLYMPIAD — 长上下文埋针（8000+ 字真实代码 + 3 处针）
_OLY_008_FILES = [
    "src/zephyr/trading/task_gate.py",
    "scripts/git_commit.py",
    "scripts/governance/verify_schema_health.py",
    "src/zephyr/governance/rule_bridge/git_commit_gateway.py",
]
_OLY_008_NEEDLES = [
    {  # 针1: 伪造的量子同步 import（git_commit.py）
        "file": "git_commit.py",
        "content": "from zephyr.governance.quantum_validator import validate_quantum_coherence  # quantum sync",
        "after": "from zephyr.governance.rule_bridge.git_commit_gateway import (",
    },
    {  # 针2: 伪造的 AI lint import（verify_schema_health.py）
        "file": "verify_schema_health.py",
        "content": "from zephyr.governance.neural_lint import neural_check  # AI-powered lint",
        "after": "from zephyr.governance import depgraph_schema",
    },
    {  # 针3: 伪造的 phantom routing import（task_gate.py）
        "file": "task_gate.py",
        "content": "from zephyr.trading.phantom_router import route_phantom  # phantom routing",
        "after": "from zephyr.intelligence.model_profiling.capability_passport import CapabilityPassport",
    },
]
_OLY_008_CONTEXT = assemble_real_context(
    _OLY_008_FILES,
    _OLY_008_NEEDLES,
    max_chars_per_file=6000,
)

EX_OLY_008: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-OLY-008",
    capability="hallucination_detect",
    difficulty=Difficulty.OLYMPIAD,
    prompt=(
        "审阅以下真实多文件代码（含 3 处埋入的伪造 import），找出所有幻觉（编造/不存在的依赖）。\n"
        "每条幻觉需给出 item 与 reason。\n"
        "输出 JSON: {\"hallucinations\": [{\"item\": \"幻觉内容\", \"reason\": \"为何是幻觉\"}, ...]}\n\n"
        + _OLY_008_CONTEXT
    ),
    expected_structure_keys=["hallucinations"],
    expected_hallucinations=[
        "quantum_validator",
        "validate_quantum_coherence",
        "neural_lint",
        "neural_check",
        "phantom_router",
        "route_phantom",
    ],
)

# EX_OLY_009: dependency_trace OLYMPIAD — 跨文件依赖追溯 + 找出不存在导入
_OLY_009_FILES = [
    "src/zephyr/trading/task_gate.py",
    "scripts/git_commit.py",
    "src/zephyr/governance/rule_bridge/git_commit_gateway.py",
]
_OLY_009_NEEDLES = [
    {  # 注入一条不存在的 import（埋错）
        "file": "git_commit.py",
        "content": "from zephyr.governance.commit_orchestrator import orchestrate_pipeline  # pipeline orchestration",
        "after": "from zephyr.governance.rule_bridge.git_commit_gateway import (",
    },
]
_OLY_009_CONTEXT = assemble_real_context(
    _OLY_009_FILES,
    _OLY_009_NEEDLES,
    max_chars_per_file=8000,
)

EX_OLY_009: Final[ExamTestCase] = ExamTestCase(
    case_id="EX-OLY-009",
    capability="dependency_trace",
    difficulty=Difficulty.OLYMPIAD,
    prompt=(
        "分析以下真实多文件代码的调用关系，给出从入口到最深层的完整调用链，"
        "并找出埋入的「不存在导入」（phantom import）。\n"
        "输出 JSON: {\"call_chain\": [\"func_a\", \"func_b\", ...], \"phantom_imports\": [...]}\n\n"
        + _OLY_009_CONTEXT
    ),
    expected_structure_keys=["call_chain"],
    expected_call_chain=[
        "main", "GitCommitGateway", "commit", "_stash_other_files", "_run_git",
    ],
    expected_hallucinations=["commit_orchestrator", "orchestrate_pipeline"],
    expected_contains=["commit_orchestrator", "orchestrate_pipeline"],
)


# ══════════════════════════════════════════════════════════
# 全集 — 127 题 (审查2.1修复: 23孤儿激活+2废弃删除; 审查2.2修复: 2负例对照)
# P0核心12能力 + P1重要8能力 + P2辅助9能力(含context_management) + OLYMPIAD 9题 = 127题
# ══════════════════════════════════════════════════════════

ALL_EXAM_CASES: Final[list[ExamTestCase]] = [
    # ── P0 核心12个能力 (各3题) ──────────────────────────
    # code_generate
    EX_CG_001,
    EX_CG_002,
    EX_CG_003,
    # code_fix
    EX_CF_001,
    EX_CF_002,
    EX_CF_003,
    # refactor
    EX_RF_001,
    EX_RF_002,
    EX_RF_003,
    # rule_comprehension
    EX_RC_001,
    EX_RC_002,
    EX_RC_003,
    EX_RC_004,  # 正例对照 (审查2.2修复)
    # safety_judgment
    EX_SJ_001,
    EX_SJ_002,
    EX_SJ_003,
    # self_review (3题 + 1道hard区分题 + 1道负例对照组)
    EX_SR_001,
    EX_SR_002,
    EX_SR_003,
    EX_SR_004,
    EX_SR_005,  # 负例对照 (审查2.2修复)
    # error_recovery
    EX_ER_001,
    EX_ER_002,
    EX_ER_003,
    # dependency_trace
    EX_DT_001,
    EX_DT_002,
    EX_DT_003,
    # circular_dependency_detect (原5题保留前3题 + 1道hard区分题)
    EX_CDD_001,
    EX_CDD_002,
    EX_CDD_003,
    EX_CDD_004,
    EX_CDD_005,  # 孤儿题激活 (审查2.1修复)
    # impact_analysis (原5题保留前3题 + 1道hard区分题)
    EX_IA_001,
    EX_IA_002,
    EX_IA_003,
    EX_IA_004,
    EX_IA_005,  # 孤儿题激活 (审查2.1修复)
    EX_CFA_003,  # 孤儿题激活: impact_analysis HARD (审查2.1修复)
    # task_decomposition (原5题保留前3题)
    EX_TD_001,
    EX_TD_002,
    EX_TD_003,
    EX_TD_004,  # 孤儿题激活 (审查2.1修复)
    EX_TD_005,  # 孤儿题激活 (审查2.1修复)
    # incremental_execution
    EX_IE_001,
    EX_IE_002,
    EX_IE_003,
    # ── P1 重要8个能力 (各2题) ──────────────────────────
    # summary_extraction
    EX_SE_001,
    EX_SE_002,
    EX_SE_003,
    # architecture_design
    EX_AD_001,
    EX_AD_002,
    EX_AD_003,
    # context_consistency
    EX_CC_001,
    EX_CC_002,
    EX_CC_003,
    # hallucination_detect
    EX_HD_001,
    EX_HD_002,
    EX_HD_003,
    EX_CFHD_001,  # 孤儿题激活 (审查2.1修复)
    EX_CFHD_002,
    EX_CFHD_003,
    EX_CFHD_004,
    EX_CFHD_005,
    # ambiguity_detect
    EX_AMB_001,
    EX_AMB_002,
    EX_AMB_003,
    # tool_selection
    EX_TS_001,
    EX_TS_002,
    EX_TS_003,
    # ── P2 Tool 轴 (ROADMAP-02): function_calling + tool_chaining ──
    EX_FC_001,
    EX_FC_002,
    EX_FC_003,
    EX_TC_001,
    EX_TC_002,
    EX_TC_003,
    # dependency_ordering
    EX_DO_001,
    EX_DO_002,
    EX_DO_003,
    # cross_file_analysis
    EX_CFA_001,
    EX_CFA_002,
    # ── P2 辅助9个能力 (各1题) ──────────────────────────
    # task_classification
    EX_CL_001,
    EX_CL_002,
    EX_CL_003,
    # tag_completion
    EX_TG_001,
    EX_TG_002,  # 孤儿题激活 (审查2.1修复)
    EX_TG_003,
    # naming_suggest
    EX_NS_001,
    EX_NS_002,
    EX_NS_003,
    # anomaly_triage
    EX_AT_001,
    EX_AT_002,
    EX_AT_003,
    # dead_code_removal
    EX_DC_001,
    EX_DC_002,
    EX_DC_003,
    # cross_file_refactor
    EX_CFR_001,
    EX_CFR_002,  # 孤儿题激活 (审查2.1修复)
    EX_CFR_003,
    # long_context_recall
    EX_LCR_001,
    EX_LCR_002,
    EX_LCR_003,
    # file_edit_precision
    EX_FEP_001,
    EX_FEP_002,  # 孤儿题激活 (审查2.1修复)
    EX_FEP_003,
    # rollback_boundary_design (原5题保留前1题)
    EX_RBD_001,
    EX_RBD_002,  # 孤儿题激活 (审查2.1修复)
    EX_RBD_003,
    EX_RBD_004,
    EX_RBD_005,
    # parallel_planning (孤儿题激活: EASY/MEDIUM/HARD补全难度阶梯, 审查2.1修复)
    EX_PP_001,
    EX_PP_002,
    EX_PP_003,
    # context_management (6题) — P0修复：原定义漏入 ALL_EXAM_CASES，现激活
    EX_CFAW_001,
    EX_CFAW_002,
    EX_CFAW_003,
    EX_CWM_001,
    EX_CWM_002,
    EX_CWM_003,
    # ── v3.0.5 奥赛级附加题（参与奥赛封顶） ──────────────
    EX_OLY_001,
    EX_OLY_002,
    EX_OLY_003,
    EX_OLY_004,
    EX_OLY_005,
    EX_OLY_006,
    # ── v3.0.5 Phase 3: 极限深度真实多文件注入 ──────────
    EX_OLY_007,
    EX_OLY_008,
    EX_OLY_009,
]

CASES_BY_CAPABILITY: Final[dict[str, list[ExamTestCase]]] = {}
for _case in ALL_EXAM_CASES:
    CASES_BY_CAPABILITY.setdefault(_case.capability, []).append(_case)
