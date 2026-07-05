# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md
# [MODULE] zephyr.intelligence.model_profiling.pipeline_routing.benchmark_suite
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RSC_benchmark_suite | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
BenchmarkSuite — 多维度模型性能测试用例集
==========================================
定义代码生成、代码修复、语义理解、幻觉检测、反应速度、
输出质量、逻辑推理 七大维度的标准化测试用例。

每个测试用例包含：
  - prompt: 输入 prompt
  - expected_patterns: 期望在输出中出现的关键模式（用于质量评分）
  - forbidden_patterns: 不应出现的模式（幻觉/错误标记）
  - max_tokens: 输出上限
  - expected_output_type: 输出类型 ("code" | "text" | "json" | "classification")
  - category: 测试分类
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ============================================================================
# 测试用例数据模型
# ============================================================================


@dataclass
class BenchmarkCase:
    case_id: str
    category: str
    subcategory: str
    prompt: str
    expected_patterns: list[str] = field(default_factory=list)
    forbidden_patterns: list[str] = field(default_factory=list)
    max_tokens: int = 512
    expected_output_type: str = "text"
    weight: float = 1.0
    reference_answer: str = ""

    @property
    def full_name(self) -> str:
        return f"{self.category}/{self.subcategory}/{self.case_id}"


# ============================================================================
# 维度 1: 代码生成能力 (Code Generation)
# ============================================================================

CODE_GEN_CASES: list[BenchmarkCase] = [
    BenchmarkCase(
        case_id="CG-001",
        category="code_generation",
        subcategory="function_impl",
        prompt="用 Python 写一个函数 is_prime(n: int) -> bool，判断一个整数是否为质数。"
        "要求：正确处理 n<=1 的情况，使用优化的试除法（只需试到 sqrt(n)）。"
        "只输出函数代码，不要解释。",
        expected_patterns=["def is_prime", "sqrt", "range", "return"],
        forbidden_patterns=["try:", "import math"],
        max_tokens=256,
        expected_output_type="code",
        weight=0.8,
        reference_answer="def is_prime(n: int) -> bool:\n    if n <= 1:\n        return False\n    if n <= 3:\n        return True\n    if n % 2 == 0 or n % 3 == 0:\n        return False\n    i = 5\n    while i * i <= n:\n        if n % i == 0 or n % (i + 2) == 0:\n            return False\n        i += 6\n    return True",
    ),
    BenchmarkCase(
        case_id="CG-002",
        category="code_generation",
        subcategory="data_structure",
        prompt="用 Python 实现一个 LRU Cache 类，使用 OrderedDict。"
        "需要实现 __init__(capacity), get(key), put(key, value) 三个方法。"
        "只输出类代码，不要解释。",
        expected_patterns=["class LRUCache", "OrderedDict", "def get", "def put", "move_to_end", "popitem"],
        forbidden_patterns=[],
        max_tokens=512,
        expected_output_type="code",
        weight=1.0,
        reference_answer="from collections import OrderedDict\n\nclass LRUCache:\n    def __init__(self, capacity: int):\n        self.capacity = capacity\n        self.cache = OrderedDict()\n\n    def get(self, key: int) -> int:\n        if key not in self.cache:\n            return -1\n        self.cache.move_to_end(key)\n        return self.cache[key]\n\n    def put(self, key: int, value: int) -> None:\n        if key in self.cache:\n            self.cache.move_to_end(key)\n        self.cache[key] = value\n        if len(self.cache) > self.capacity:\n            self.cache.popitem(last=False)",
    ),
    BenchmarkCase(
        case_id="CG-003",
        category="code_generation",
        subcategory="async_code",
        prompt="用 Python asyncio 写一个异步函数 fetch_all(urls: list[str]) -> list[dict]，"
        "并发请求所有 URL，设置 10 秒超时，返回 JSON 结果列表。"
        "使用 aiohttp 或 httpx。只输出代码。",
        expected_patterns=["async def", "asyncio", "aiohttp|httpx", "timeout"],
        forbidden_patterns=["requests.get", "requests.post"],
        max_tokens=512,
        expected_output_type="code",
        weight=1.0,
    ),
    BenchmarkCase(
        case_id="CG-004",
        category="code_generation",
        subcategory="error_handling",
        prompt="写一个 Python 函数 safe_divide(a: float, b: float) -> float，"
        "处理除零、类型错误、溢出三种异常情况，每种返回不同的错误值。"
        "只输出函数代码。",
        expected_patterns=["def safe_divide", "ZeroDivisionError|b == 0", "TypeError|isinstance", "OverflowError|abs"],
        forbidden_patterns=[],
        max_tokens=256,
        expected_output_type="code",
        weight=0.6,
    ),
    BenchmarkCase(
        case_id="CG-005",
        category="code_generation",
        subcategory="algorithm",
        prompt="用 Python 实现二分查找算法 binary_search(arr: list[int], target: int) -> int。"
        "返回目标索引，未找到返回 -1。要求 O(log n) 时间复杂度。只输出代码。",
        expected_patterns=["def binary_search", "while", "mid", "//"],
        forbidden_patterns=["for.*in.*arr", ".index("],
        max_tokens=256,
        expected_output_type="code",
        weight=0.8,
    ),
]

# ============================================================================
# 维度 2: 代码修复与编辑 (Code Editing / Fix)
# ============================================================================

CODE_FIX_CASES: list[BenchmarkCase] = [
    BenchmarkCase(
        case_id="CF-001",
        category="code_fix",
        subcategory="bug_fix",
        prompt="下面的 Python 代码有 bug，找出并修复它：\n\n"
        "```python\n"
        "def get_user(id):\n"
        "    users = {'1': 'Alice', '2': 'Bob'}\n"
        "    return users[id]\n"
        "print(get_user(3))\n"
        "```\n\n"
        "只输出修复后的代码，不要解释。",
        expected_patterns=[".get(", "None", "default"],
        forbidden_patterns=["except", "try"],
        max_tokens=128,
        expected_output_type="code",
        weight=0.6,
    ),
    BenchmarkCase(
        case_id="CF-002",
        category="code_fix",
        subcategory="refactor",
        prompt="下面的 Python 函数太长了，把它重构得简洁一点，保持功能不变：\n\n"
        "```python\n"
        "def process(data):\n"
        "    result = []\n"
        "    for item in data:\n"
        "        if item is not None:\n"
        "            if item > 0:\n"
        "                if item % 2 == 0:\n"
        "                    result.append(item * 2)\n"
        "                else:\n"
        "                    result.append(item * 3)\n"
        "    return result\n"
        "```\n\n只输出重构后的代码。",
        expected_patterns=["filter|generator|comprehension|list", "def process"],
        forbidden_patterns=[],
        max_tokens=256,
        expected_output_type="code",
        weight=0.8,
    ),
    BenchmarkCase(
        case_id="CF-003",
        category="code_fix",
        subcategory="add_feature",
        prompt="下面是一个简单的计数器类。请给它添加 reset() 方法和 max_count 上限功能：\n\n"
        "```python\n"
        "class Counter:\n"
        "    def __init__(self):\n"
        "        self.count = 0\n"
        "    def increment(self):\n"
        "        self.count += 1\n"
        "        return self.count\n"
        "```\n\n只输出修改后的完整类代码。",
        expected_patterns=["def reset", "max_count", "self.count = 0", "if"],
        forbidden_patterns=[],
        max_tokens=256,
        expected_output_type="code",
        weight=0.7,
    ),
]

# ============================================================================
# 维度 3: 语义理解 (Semantic Understanding)
# ============================================================================

SEMANTIC_CASES: list[BenchmarkCase] = [
    BenchmarkCase(
        case_id="SE-001",
        category="semantic",
        subcategory="sentiment",
        prompt="判断以下句子的情感倾向（positive/negative/neutral）：\n"
        "\u201c虽然过程充满挑战，但最终的成果超出了所有人的预期。\u201d\n"
        "只输出一个词。",
        expected_patterns=["positive"],
        forbidden_patterns=["negative", "neutral"],
        max_tokens=16,
        expected_output_type="classification",
        weight=0.5,
    ),
    BenchmarkCase(
        case_id="SE-002",
        category="semantic",
        subcategory="nli",
        prompt="前提：'小明每天早上 7 点起床跑步 5 公里。'\n"
        "假设：'小明有运动的习惯。'\n"
        "判断假设是否可以从前提推导出来。只回答 entailment / contradiction / neutral。",
        expected_patterns=["entailment"],
        forbidden_patterns=["contradiction"],
        max_tokens=16,
        expected_output_type="classification",
        weight=0.5,
    ),
    BenchmarkCase(
        case_id="SE-003",
        category="semantic",
        subcategory="summarization",
        prompt="用不超过 50 字概括以下段落的核心要点：\n\n"
        "分布式系统的 CAP 定理指出，在一个分布式数据存储系统中，"
        "最多只能同时满足一致性（Consistency）、可用性（Availability）和"
        "分区容错性（Partition Tolerance）这三项中的两项。"
        "由于网络分区在分布式系统中不可避免，因此实际架构选择"
        "通常是在 CP（一致性与分区容错）和 AP（可用性与分区容错）之间做权衡。",
        expected_patterns=["CAP", "一致性|consistency", "可用性|availability"],
        forbidden_patterns=[],
        max_tokens=128,
        expected_output_type="text",
        weight=0.7,
    ),
    BenchmarkCase(
        case_id="SE-004",
        category="semantic",
        subcategory="classification",
        prompt="将以下技术问题分类为：bug_report / feature_request / question / other：\n"
        "\u201c我在使用 pandas 读取 10GB CSV 文件时内存溢出，有什么优化方案吗？\u201d\n"
        "只输出分类标签。",
        expected_patterns=["question"],
        forbidden_patterns=["bug_report", "feature_request"],
        max_tokens=16,
        expected_output_type="classification",
        weight=0.4,
    ),
]

# ============================================================================
# 维度 4: 幻觉检测 (Hallucination Detection)
# ============================================================================

HALLUCINATION_CASES: list[BenchmarkCase] = [
    BenchmarkCase(
        case_id="HA-001",
        category="hallucination",
        subcategory="api_fabrication",
        prompt="Python 标准库中有一个叫 `datatools` 的模块吗？如果有，它的主要功能是什么？如果不存在，就回答'不存在'。",
        expected_patterns=["不存在|没有|无此模块"],
        forbidden_patterns=["datatools.*提供|datatools.*功能|datatools.*用法"],
        max_tokens=128,
        expected_output_type="text",
        weight=1.5,
    ),
    BenchmarkCase(
        case_id="HA-002",
        category="hallucination",
        subcategory="fact_check",
        prompt="Python 3.12 的 `itertools` 模块新增了一个叫 `batched()` 的函数吗？"
        "如果确实存在，描述它的作用；如果不存在，回答'不存在'。",
        expected_patterns=["batched|存在"],
        forbidden_patterns=["不存在"],
        max_tokens=128,
        expected_output_type="text",
        weight=1.0,
    ),
    BenchmarkCase(
        case_id="HA-003",
        category="hallucination",
        subcategory="parameter_fabrication",
        prompt="`json.dumps()` 有一个叫 `strict_mode` 的参数吗？如果有，说明它的作用；如果没有，回答'没有这个参数'。",
        expected_patterns=["没有|无此参数|不存在"],
        forbidden_patterns=["strict_mode.*控制|strict_mode.*设置|strict_mode.*True"],
        max_tokens=128,
        expected_output_type="text",
        weight=1.5,
    ),
    BenchmarkCase(
        case_id="HA-004",
        category="hallucination",
        subcategory="known_error",
        prompt="以下 Python 代码输出什么？\n"
        "```python\n"
        "x = [1, 2, 3]\n"
        "y = x\n"
        "y.append(4)\n"
        "print(x)\n"
        "```\n只输出结果，不解释。",
        expected_patterns=["[1, 2, 3, 4]"],
        forbidden_patterns=["[1, 2, 3]", "Error", "报错"],
        max_tokens=32,
        expected_output_type="text",
        weight=0.5,
    ),
    BenchmarkCase(
        case_id="HA-005",
        category="hallucination",
        subcategory="refusal_honesty",
        prompt="请问 Windows 11 build 99999 的发布时间是什么？（注意：这个 build 号是我编造的）\n"
        "如果不知道或者这个版本不存在，请诚实回答。",
        expected_patterns=["不知道|不存在|编造|没有|无法"],
        forbidden_patterns=["发布.*日期|发布.*时间|2025|2026"],
        max_tokens=128,
        expected_output_type="text",
        weight=1.2,
    ),
]

# ============================================================================
# 维度 5: 反应速度 (Latency / Speed) —— 用短 prompt 测试
# ============================================================================

LATENCY_CASES: list[BenchmarkCase] = [
    BenchmarkCase(
        case_id="LT-001",
        category="latency",
        subcategory="simple_response",
        prompt="回复 'OK' ，不要输出任何其他内容。",
        expected_patterns=["OK"],
        forbidden_patterns=[],
        max_tokens=8,
        expected_output_type="text",
        weight=0.3,
    ),
    BenchmarkCase(
        case_id="LT-002",
        category="latency",
        subcategory="json_output",
        prompt='输出 JSON: {"status":"ok","version":"1.0"} ，不要加任何额外文本。',
        expected_patterns=["status", "ok", "version"],
        forbidden_patterns=[],
        max_tokens=64,
        expected_output_type="json",
        weight=0.3,
    ),
    BenchmarkCase(
        case_id="LT-003",
        category="latency",
        subcategory="short_code",
        prompt="用 Python 写一个函数 add(a, b) 返回 a+b。只输出函数代码。",
        expected_patterns=["def add", "return"],
        forbidden_patterns=[],
        max_tokens=64,
        expected_output_type="code",
        weight=0.3,
    ),
]

# ============================================================================
# 维度 6: 输出质量 (Output Quality)
# ============================================================================

QUALITY_CASES: list[BenchmarkCase] = [
    BenchmarkCase(
        case_id="QL-001",
        category="quality",
        subcategory="json_format",
        prompt="生成一个 JSON 对象，包含以下字段：name(string), age(int), skills(list of strings)。"
        "只输出合法的 JSON，不要代码块标记。",
        expected_patterns=['"name"', '"age"', '"skills"', "[", "]"],
        forbidden_patterns=["```", "python", "javascript"],
        max_tokens=128,
        expected_output_type="json",
        weight=0.5,
    ),
    BenchmarkCase(
        case_id="QL-002",
        category="quality",
        subcategory="markdown_format",
        prompt="用 Markdown 格式写一段关于 Python 装饰器的简短介绍（100 字以内），包含一个代码示例和一个特点列表。",
        expected_patterns=["###|##|**", "```", "装饰|decorator"],
        forbidden_patterns=[],
        max_tokens=256,
        expected_output_type="text",
        weight=0.5,
    ),
    BenchmarkCase(
        case_id="QL-003",
        category="quality",
        subcategory="instruction_following",
        prompt="列出 3 种 Python 虚拟环境管理工具，用数字编号，每行不超过 20 个字符。不要加任何开头语或结尾语。",
        expected_patterns=["1\\.", "2\\.", "3\\."],
        forbidden_patterns=["以下是|下面是|Python 虚拟环境"],
        max_tokens=128,
        expected_output_type="text",
        weight=0.6,
    ),
]

# ============================================================================
# 维度 7: 逻辑推理 (Logical Reasoning)
# ============================================================================

REASONING_CASES: list[BenchmarkCase] = [
    BenchmarkCase(
        case_id="LR-001",
        category="reasoning",
        subcategory="deductive",
        prompt="所有 A 都是 B。C 是 A。那么 C 是 B 吗？只回答 YES 或 NO。",
        expected_patterns=["YES|Yes|是"],
        forbidden_patterns=["NO|No|不是|不"],
        max_tokens=8,
        expected_output_type="classification",
        weight=0.4,
    ),
    BenchmarkCase(
        case_id="LR-002",
        category="reasoning",
        subcategory="math",
        prompt="计算：如果一个文件大小是 10MB，网速是 2MB/s，下载需要多少秒？只输出数字。",
        expected_patterns=["5"],
        forbidden_patterns=[],
        max_tokens=16,
        expected_output_type="classification",
        weight=0.4,
    ),
    BenchmarkCase(
        case_id="LR-003",
        category="reasoning",
        subcategory="code_trace",
        prompt="以下 Python 代码输出什么？只输出数字。\n"
        "```python\n"
        "def f(n):\n"
        "    if n <= 1: return 1\n"
        "    return n * f(n-1)\n"
        "print(f(5))\n"
        "```",
        expected_patterns=["120"],
        forbidden_patterns=[],
        max_tokens=16,
        expected_output_type="classification",
        weight=0.4,
    ),
]

# ============================================================================
# 汇总
# ============================================================================

ALL_BENCHMARK_CASES: list[BenchmarkCase] = (
    CODE_GEN_CASES
    + CODE_FIX_CASES
    + SEMANTIC_CASES
    + HALLUCINATION_CASES
    + LATENCY_CASES
    + QUALITY_CASES
    + REASONING_CASES
)

CATEGORY_MAP: dict[str, list[BenchmarkCase]] = {
    "code_generation": CODE_GEN_CASES,
    "code_fix": CODE_FIX_CASES,
    "semantic": SEMANTIC_CASES,
    "hallucination": HALLUCINATION_CASES,
    "latency": LATENCY_CASES,
    "quality": QUALITY_CASES,
    "reasoning": REASONING_CASES,
}
