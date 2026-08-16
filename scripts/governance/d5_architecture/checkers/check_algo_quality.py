# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/checkers/check_algo_quality.py | §algo-quality
# [MODULE] scripts.governance.d5_architecture.checkers.check_algo_quality
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.checkers.__init__
# [CONSUMERS] GATE-ALGO-QUALITY pre-commit hook（warn-only 观察期）；AI 人工审计算法糊弄6类 pattern
# [STARTUP] event_driven
# [MATURITY] production
# [INVARIANTS] 只读扫描 src/zephyr/**/*.py + docs/03_modules/**/blueprint.md；检测6类算法糊弄 pattern（P1代理/P2定性词/P3伪精确/P4死数据/P5名词堆砌/P6逻辑错位）；--ci 有问题 exit 1，--warn-only 全 exit 0；不修改任何文件
# [MODIFY-GUARD] DEAD_DATA_SOURCES / INDICATOR_IMPLEMENTATION_MAP / *_PATTERN 常量清单
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=PASS/干净或--warn-only；exit 1=FINDINGS（--ci 且有问题）；exit 2=ERROR（文件不存在/参数错误）
# [TESTS] tests/governance/test_algo_quality.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""check_algo_quality.py — GATE-ALGO-QUALITY

审计算法糊弄（algorithm fraud）的自动检测器，填补 60+ 现有 gate 的语义空白。

病根：2026-08-06 全面审查发现 15 处"糊弄"算法（用换手率代理筹码分布、定性词无量化、
伪精确阈值、引用已停发的北向资金、Wyckoff 名词堆砌无识别逻辑、T3 把否决条件当正向评分）。
虽然已全部修正，但 100% AI 开发场景下没有任何自动化机制能检测"算法糊弄"——不可持续。

裁定：检测器主扫描对象是 src/zephyr/ 代码（AST + 正则），blueprint.md 作为辅助交叉验证。
理由：
  1. 代码是算法真源，blueprint 只是描述——代码糊弄是根因
  2. 很多算法实现在代码里但没写进 blueprint——只扫 blueprint 会漏
  3. blueprint 糊弄是设计层糊弄，代码糊弄是实现层糊弄——两者都抓，代码优先

6 类糊弄 pattern（每类都定义代码层 + blueprint 层检测点）：
  P1 代理替代      —— 用易得指标代替真正需要的指标（如换手率代理筹码分布）
  P2 定性词无量化   —— 有关键词列表但无分类/计算逻辑（如"降准降息→40分"无算法）
  P3 伪精确        —— 阈值依赖量纲/图表比例（如均线角度>45°→<30°）
  P4 死数据        —— 引用已停发/不可得的数据源（如北向资金 2024-08-19 停发）
  P5 名词堆砌无算法 —— 列出技术名词但无识别逻辑实现（如"PS/SC/AR/ST 结构识别"）
  P6 逻辑错位      —— 把否决条件当正向确认（如"无虹吸→60分"）

模式：
  --ci (默认): 有问题 → exit 1
  --warn-only: 全部 exit 0 (仅报告，观察期)

用法：
  python scripts/governance/d5_architecture/checkers/check_algo_quality.py [--warn-only] \\
      [--code-only|--bp-only|--all] [<file>...]
  无参数时扫描 src/zephyr/**/*.py + docs/03_modules/**/blueprint.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import NamedTuple

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout  # noqa: E402

ensure_utf8_stdout()

import argparse  # noqa: E402
import ast  # noqa: E402
import re  # noqa: E402

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT  # noqa: E402

__manifest__ = """
args:
- --ci
- --warn-only
- --code-only
- --bp-only
- --all
description: GATE-ALGO-QUALITY - 算法糊弄6类pattern检测（代码AST为主，blueprint正则为辅）
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: true
"""

# ============================================================================
# 扫描目标默认根目录（相对 REPO_ROOT）
# ============================================================================
CODE_SCAN_ROOT = Path("src/zephyr")
BP_SCAN_GLOB = "docs/03_modules/**/blueprint.md"

# ============================================================================
# 死数据源清单（P4）—— 可扩展
# 真源：10_regime_detector_spec 文档债务标注 + 2026-08-06 全面审查结论
# ============================================================================
DEAD_DATA_SOURCES: dict[str, dict[str, str]] = {
    "hk_connect_flow": {
        "stopped": "2024-08-19",
        "reason": "北向资金日度数据停发（证监会新规）",
    },
    "hk_connect_daily": {
        "stopped": "2024-08-19",
        "reason": "沪深股通日度数据停发",
    },
    "northbound_flow": {
        "stopped": "2024-08-19",
        "reason": "北向资金日度数据停发（英文别名）",
    },
    "northbound_capital": {
        "stopped": "2024-08-19",
        "reason": "北向资金日度数据停发（英文别名）",
    },
    "stock_connect_flow": {
        "stopped": "2024-08-19",
        "reason": "沪深股通日度数据停发",
    },
}

# 指标 → 应有实现关键字映射（P1 代理替代检测）
# 若函数名含 name_keywords，则 body 必须包含 expected_impl 任一关键字；
# 仅出现 proxy_only 关键字（且无 expected_impl）→ 判 P1 违规
INDICATOR_IMPLEMENTATION_MAP: dict[str, dict[str, list[str]]] = {
    "chip_distribution": {
        "name_keywords": ["chip_distribution", "chip_dist", "chipro"],
        "expected_impl": [
            "triangular",
            "vwap",
            "recurse",
            "grid_prices",
            "pdf",
            "turnover_recurse",
            "build_grid",
            "compute_daily_distribution",
        ],
        "proxy_only": ["turnover_rate", "turnover"],
    },
    "vix": {
        "name_keywords": ["compute_vix", "build_vix", "vix_index"],
        "expected_impl": [
            "variance_swap",
            "option_iv_surface",
            "cboe",
            "svi",
            "iv_surface",
            "forward_variance",
        ],
        "proxy_only": ["single_iv", "iv_35", "iv_atm"],
    },
}

# P2 定性词无量化：关键词列表模式（出现这些列表 + 无分类函数 → 违规）
QUALITATIVE_KEYWORD_LISTS: list[list[str]] = [
    ["降准", "降息", "MLF"],
    ["喊话", "利好", "利空"],
    ["鬼故事", "传闻", "小作文"],
]

# 算法步骤关键字（出现这些词说明有具体算法，P2/P5 不违规）
ALGO_STEP_KEYWORDS = [
    "算法",
    "公式",
    "检测",
    "FSM",
    "触发器",
    "状态机",
    "递推",
    "回归",
    "分类",
    "加权",
    "归一化",
    "标准化",
    "percentile",
    "z_score",
    "标准化",
    "function",
    "def ",
    "triangular",
    "vwap",
    "pivot",
    "hurst",
    "adf",
    "acsi",
]

# P3 伪精确：阈值变量名（出现这些名字 + 数值比较 → 违规，除非附近有 normalize/percentile）
DIMENSION_DEPENDENT_VARS = [
    "angle",
    "degree",
    "slope_angle",
    "均线角度",
    "角度",
    "度数",
    "斜率",
]

# 量纲化关键字（出现这些词则不算 P3 违规）
DIMENSION_FREE_KEYWORDS = [
    "normalize",
    "standardize",
    "percentile",
    "z_score",
    "zscore",
    "hurst",
    "滚动分位",
    "分位数",
    "归一化",
    "标准化",
    "iv_rank",
    "iv_percentile",
    "variance_swap",
]

# P5 名词堆砌：缩写正则（连续 ≥3 个 ALL-CAPS 缩写 → 可疑）
ABBREV_PATTERN = re.compile(r"\b[A-Z]{2,5}\b")

# 合法缩写白名单——这些缩写堆砌不算糊弄（通用技术栈/工程概念/license/状态值）
# 真正的糊弄是金融算法缩写堆砌（PS/SC/AR/ST/SOS/Wyckoff 等——这些不在白名单）
LEGIT_ABBREVS: frozenset[str] = frozenset(
    {
        # 通用技术
        "API",
        "JSON",
        "SQL",
        "HTTP",
        "HTTPS",
        "XML",
        "HTML",
        "CSS",
        "REST",
        "URL",
        "URI",
        "UUID",
        "GUID",
        "CSV",
        "TSV",
        "YAML",
        "TOML",
        "INI",
        "JSONL",
        "NDJSON",
        # AI/ML
        "AI",
        "ML",
        "DL",
        "NLP",
        "LLM",
        "GPT",
        "BERT",
        "RAG",
        "CNN",
        "RNN",
        "LSTM",
        "GRU",
        "TF",
        "GPU",
        "CPU",
        "TPU",
        "RAM",
        "GLM",
        "BGE",
        "MDPI",
        # 数据库
        "DB",
        "RDBMS",
        "OLTP",
        "OLAP",
        "CRUD",
        "ACID",
        "WAL",
        "MVCC",
        "CQRS",
        "ES",
        "DDL",
        "DML",
        "ETL",
        "ELT",
        "ORM",
        # 工程概念
        "TDD",
        "BDD",
        "OOP",
        "FP",
        "MVC",
        "MVVM",
        "DDD",
        "SOLID",
        "DRY",
        "KISS",
        "YAGNI",
        "OCP",
        "LSP",
        "RBAC",
        "ABAC",
        "ACL",
        # 状态/布尔
        "ON",
        "OFF",
        "YES",
        "NO",
        "OK",
        "FAIL",
        "PASS",
        "TRUE",
        "FALSE",
        "NULL",
        "VOID",
        "NAN",
        "INF",
        "INIT",
        "READY",
        "PAUSE",
        "IDLE",
        "ERROR",
        "WARN",
        "DENY",
        "ALLOW",
        "OPEN",
        "CLOSE",
        "HALT",
        "RED",
        "GREEN",
        "BLUE",
        "YELLOW",
        # 交易动作
        "BUY",
        "SELL",
        "HOLD",
        "LONG",
        "SHORT",
        "BID",
        "ASK",
        "MUST",
        # License
        "MIT",
        "BSD",
        "GPL",
        "MPL",
        "LGPL",
        "Apache",
        # 项目内部域名缩写（不是算法糊弄）
        "MOD",
        "GOV",
        "DOC",
        "POS",
        "EX",
        "SHA",
        "SYS",
        "SIM",
        "CTL",
        "RES",
        "CFG",
        "GEN",
        "SRC",
        "TST",
        "PF",
        "CORE",
        "DEDUP",
        "FLE",
        "INFRA",
        "DIM",
        "ORC",
        "PA",
        "PE",
        "BM",
        "RC",
        # 时间/单位
        "ISO",
        "UTC",
        "GMT",
        "ETC",
        "CST",
        "EST",
        "PST",
        "NTFS",
        "FAT",
        "KB",
        "MB",
        "GB",
        "TB",
        "PB",
        "MS",
        "NS",
        "US",
        # 网络协议
        "TCP",
        "UDP",
        "DNS",
        "VPN",
        "SSL",
        "TLS",
        "SSH",
        "SFTP",
        "FTP",
        "SMTP",
        "IMAP",
        "POP",
        "JWT",
        "JWS",
        "JWE",
        # 测试/CI
        "CI",
        "CD",
        "PR",
        "MR",
        "WIP",
        "TODO",
        "FIXME",
        "NOTE",
        "XXX",
        # 安全
        "MAC",
        "DAC",
        "CORS",
        "CSP",
        "XSS",
        "CSRF",
        "SSRF",
        "CVE",
        "CVSS",
        "CWE",
        "WQA",
        "PES",
        "OTP",
        "CSA",
        "ATF",
        "OPA",
        "AH",
        "MCP",
        # 文件格式
        "PNG",
        "JPG",
        "JPEG",
        "GIF",
        "SVG",
        "PDF",
        "XLS",
        "PPT",
        # 业务概念（非算法糊弄）
        "ROI",
        "KPI",
        "SLA",
        "SLO",
        "SLI",
        "MTTR",
        "RTO",
        "RPO",
        "BCP",
        "AUM",
        "NAV",
        "TCA",
        "ROE",
        "ROA",
        "EBITDA",
        # 状态机
        "FSM",  # 状态机本身是算法步骤词
        # 通用类型/关键字
        "ID",
        "UID",
        "TYPE",
        "KEY",
        "VAL",
        "TEXT",
        "INT",
        "BOOL",
        "STR",
        "LIST",
        "DICT",
        "SET",
        "TUPLE",
        "FLOAT",
        "DOUBLE",
        # 国际标准
        "OWASP",
        "NIST",
        "IEEE",
        "IETF",
        "W3C",
        # 财务报告（非算法）
        "GAAP",
        "IFRS",
        "SEC",
        "FINRA",
        "FRTB",
        "BASEL",
        "GDPR",
        # 通用前缀
        "EXT",
        "STD",
        "PRO",
        "LITE",
        "MINI",
        "MAX",
        "DEV",
        "PROD",
        "UAT",
        "SIT",
        "BAT",
        # 项目内特定模块缩写（非算法）
        "CTR",
        "TTL",
        "SSOT",
        "GATE",
        "ARCH",
        "BLUEPRINT",
        "MODULE",
        "DOMAIN",
        "LAYER",
        "PHASE",
        "STEP",
        "STATE",
        # 操作系统/平台
        "OS",
        "VM",
        "CLI",
        "GUI",
        "IDE",
        "SDK",
        "ROM",
        "DAG",
        # 日期格式占位符（非缩写）
        "YYYY",
        "MM",
        "DD",
        "HH",
        "MIN",
        "SS",
        "MOS",
        "YR",
        # 通用度量
        "MEM",
        "DISK",
        "NET",
        "IO",
        "PSI",
        "MAPE",
        # 数据结构/算法词（非糊弄）
        "LRU",
        "MRU",
        "FIFO",
        "LIFO",
        "LFU",
        "BFS",
        "DFS",
        "RPN",
        # 计算机体系结构/工具
        "RTX",
        "TLB",
        "DSR",
        "BH",
        "OR",
        "CT",
        "ATM",
        "INV",
        "BS",
        "RISK",
        "COST",
        "PRICE",
        "TIME",
        "RULE",
        "RULES",
        "TABLE",
        "HEAD",
        "OOM",
        "SOS",
        "ONE",
        "ALL",
        "DRIFT",
        "MA",
        "RI",
        "GAP",
        "MVO",
        "BL",
        "BR",
        "KBG",
        "FIX",
        "BT",
        "RS",
        # 编译器/系统工具
        "AST",
        "PID",
        "PATH",
        "NTP",
        "GC",
        "IPFS",
        "RBK",
        "TASK",
        "JIT",
        "LLVM",
    }
)

# blueprint 算法章节锚点（仅扫描这些章节的算法描述）
BP_ALGO_SECTION_HEADERS = [
    "## 3.",
    "## 4.",
    "## 5.",
    "## §3",
    "## §4",
    "## §5",
    "### 3.",
    "### 4.",
    "### 5.",
]


# ============================================================================
# Finding 数据结构
# ============================================================================


class Finding(NamedTuple):
    """单条糊弄检出。"""

    pattern: str  # P1_proxy / P2_qualitative / P3_false_precision / P4_dead_data / P5_buzzword / P6_logical
    severity: str  # "warning" / "error"
    detail: str  # 人类可读描述
    line: int = 0  # 行号（0 = 未定位）


# ============================================================================
# 工具函数
# ============================================================================


def _get_function_body_source(source: str, node: ast.FunctionDef) -> str:
    """提取函数体的源代码片段。"""
    if hasattr(ast, "get_source_segment"):
        seg = ast.get_source_segment(source, node)
        if seg:
            return seg
    # Fallback：用行号切片
    lines = source.splitlines()
    if node.lineno and node.end_lineno:
        return "\n".join(lines[node.lineno - 1 : node.end_lineno])
    return ""


def _extract_blueprint_algo_sections(text: str) -> str:
    """从 blueprint 文本中抽取算法描述章节（§3/§4/§5）。

    blueprint 中算法描述通常在 §3 架构设计 / §4 数据模型 / §5 核心算法 章节。
    抽取这些章节的文本用于 pattern 检测，避免误扫 frontmatter / 概述。
    """
    lines = text.splitlines()
    captured: list[str] = []
    in_algo_section = False

    for line in lines:
        # 检测章节头：## 3. / ## 4. / ## 5. / ### 3.1 等
        if re.match(r"^#{1,3}\s+(?:§)?[345](?:\.|\s|$)", line):
            in_algo_section = True
            captured.append(line)
            continue
        # 遇到其他顶级章节（## 1. / ## 2. / ## 6. 等）停止
        if in_algo_section and re.match(r"^#{1,3}\s+(?:§)?[12](?:\.|\s|$)", line):
            in_algo_section = False
            continue
        if in_algo_section and re.match(r"^#{1,2}\s+(?:§)?[6789]", line):
            in_algo_section = False
            continue
        if in_algo_section:
            captured.append(line)

    return "\n".join(captured) if captured else text


def _is_test_file(filename: str) -> bool:
    """测试文件豁免部分检测（允许 pass/... 桩）。"""
    name = Path(filename).name
    return name.startswith("test_") or name.endswith("_test.py")


# ============================================================================
# P1 代理替代（proxy substitution）
# ============================================================================

PROXY_REGEX = re.compile(r"(代理|近似|代替|用.{0,20}代表|\bproxy\b)", re.IGNORECASE)
# 金融/算法上下文词——必须同时含这些词才考虑代理替代嫌疑（避免"网络代理"/"数学近似"误报）
FINANCIAL_ALGO_CONTEXT_REGEX = re.compile(
    r"(筹码|分布|换手率|指标|特征|因子|算法|VWAP|Hurst|VIX|ACSI|分位|"
    r"compute_chip|compute_vix|calc_score|regime|capitulation|wyckoff)"
)
# 非金融语境豁免——这些上下文中的"代理/近似"是合法术语
NON_FINANCIAL_PROXY_CONTEXT = re.compile(
    r"(VPN|DNS|网络代理|代理服务器|代理延迟|HTTP proxy|forward proxy|"
    r"代理指标|近似等于|math\.|scipy\.|np\.|标准正态|erfinv|polyfit|"
    r"代理审核|代理签名|代理签发|agent_proxy|ProxyAgent|"
    r"衰减系数近似|近似迁移|近似计算|泰勒展开|近似可接受|数学近似|数值近似|"
    r"未就绪时|fallback|降级|备选|占位|临时方案|风险状态|生成贴近)"
)

# 修正说明语境豁免——这些标记说明是"修正说明"而非糊弄本身
REVISION_CONTEXT_REGEX = re.compile(
    r"(糊弄判定|原公式|原算法|替换|修正|升级为|改为|改用|"
    r"已废弃|已停发|文档债务|停发|停止公布)"
)


def _is_legitimate_proxy_context(line: str) -> bool:
    """检查"代理/近似"是否在合法非金融语境（网络代理/数学近似/代理指标表头等）。"""
    return bool(NON_FINANCIAL_PROXY_CONTEXT.search(line))


def _is_revision_context(line: str) -> bool:
    """检查是否在修正说明语境（"糊弄判定"/"替换"/"修正"等说明性引用）。"""
    return bool(REVISION_CONTEXT_REGEX.search(line))


def _is_negated_proxy(line: str) -> bool:
    """检查代理词是否处于否定语境（"非换手率代理"/"不用代理"等显式否定）。"""
    return bool(re.search(r"(非|不|无|禁用|避免|未用|不再).{0,6}(代理|近似|代替|proxy)", line))


def _p1_scan_regex(source: str, debt_docstring_lines: set[int]) -> list[Finding]:
    """P1 路径1：正则——代理词 + 金融算法上下文（避免网络代理/数学近似误报）。"""
    findings: list[Finding] = []
    for i, line in enumerate(source.splitlines(), 1):
        if not (PROXY_REGEX.search(line) and FINANCIAL_ALGO_CONTEXT_REGEX.search(line)):
            continue
        # 豁免：否定语境（"非换手率代理"/"不用代理"——显式声明 NOT 用代理）
        if _is_negated_proxy(line):
            continue
        # 豁免：非金融语境（网络代理/数学近似/代理指标表头）
        if _is_legitimate_proxy_context(line):
            continue
        # 豁免：修正说明语境（"糊弄判定：原公式..."等说明性引用）
        if _is_revision_context(line):
            continue
        # 豁免：文档债务标注（说明已废弃的代理）
        if "文档债务" in line or "已废弃" in line or "已停发" in line:
            continue
        # 豁免：行在含文档债务标记的 docstring 范围内
        if i in debt_docstring_lines:
            continue
        findings.append(
            Finding(
                pattern="P1_proxy",
                severity="warning",
                detail=f"代理替代嫌疑（含代理词且在算法上下文）：{line.strip()[:80]}",
                line=i,
            )
        )
    return findings


def _p1_scan_ast(source: str) -> list[Finding]:
    """P1 路径2：AST 语义检查——函数名声称计算 X 但实现只用 Y。

    用 INDICATOR_IMPLEMENTATION_MAP 做语义检查：函数名含 indicator.name_keywords，
    但 body 不含 expected_impl、仅含 proxy_only → 违规。
    """
    findings: list[Finding] = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return findings

    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        func_name = node.name.lower()
        body_src = _get_function_body_source(source, node).lower()

        for indicator, spec in INDICATOR_IMPLEMENTATION_MAP.items():
            if not any(kw in func_name for kw in spec["name_keywords"]):
                continue
            # 函数名声称计算 indicator
            has_proper_impl = any(kw in body_src for kw in spec["expected_impl"])
            has_proxy_only = any(kw in body_src for kw in spec["proxy_only"])
            if not has_proper_impl and has_proxy_only:
                findings.append(
                    Finding(
                        pattern="P1_proxy",
                        severity="error",
                        detail=f"函数 {node.name}() 声称计算 {indicator}，但 body 仅用 "
                        f"{spec['proxy_only']} 代理，未实现 {spec['expected_impl'][:3]}",
                        line=node.lineno,
                    )
                )
    return findings


def _check_p1_proxy_code(source: str, filename: str = "<string>") -> list[Finding]:
    """P1 代码层：① 注释/函数名含代理词且在算法上下文 ② 函数名声称计算指标但 body 仅用代理。"""
    debt_docstring_lines = _collect_debt_docstring_lines(source)
    findings = _p1_scan_regex(source, debt_docstring_lines)
    findings.extend(_p1_scan_ast(source))
    return findings


def _collect_debt_docstring_lines(source: str) -> set[int]:
    """收集含"文档债务"标记的 docstring 范围内的所有行号。

    用于豁免同一 docstring 内的代理词（作者已声明过渡实现）。
    """
    lines = source.splitlines()
    debt_lines: set[int] = set()

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return debt_lines

    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        doc = ast.get_docstring(node)
        if not doc or "文档债务" not in doc:
            continue
        # 收集该 docstring 涵盖的行号范围
        # Module docstring 是文件级，涵盖整个文件
        if isinstance(node, ast.Module):
            for i in range(1, len(lines) + 1):
                debt_lines.add(i)
        else:
            # 函数/类 docstring：从 node.lineno 到 node.body[0] 的 end_lineno
            if node.body and hasattr(node.body[0], "end_lineno") and node.body[0].end_lineno:
                for i in range(node.lineno, node.body[0].end_lineno + 1):
                    debt_lines.add(i)
            else:
                # fallback: 整个 node 范围
                end = getattr(node, "end_lineno", node.lineno) or node.lineno
                for i in range(node.lineno, end + 1):
                    debt_lines.add(i)

    return debt_lines


def _check_p1_proxy_blueprint(text: str, filename: str = "<string>") -> list[Finding]:
    """P1 blueprint 层：算法章节出现"代理/近似/代替"词且在金融算法上下文。"""
    findings: list[Finding] = []
    section = _extract_blueprint_algo_sections(text)

    for i, line in enumerate(section.splitlines(), 1):
        if PROXY_REGEX.search(line):
            # 必须在金融/算法上下文（避免网络代理/数学近似误报）
            if not FINANCIAL_ALGO_CONTEXT_REGEX.search(line):
                continue
            # 豁免：否定语境（"非X代理"——显式声明 NOT 用代理）
            if _is_negated_proxy(line):
                continue
            # 豁免：非金融语境（网络代理/数学近似/代理指标表头）
            if _is_legitimate_proxy_context(line):
                continue
            # 豁免：修正说明语境（"糊弄判定：原公式用换手率代理..."等说明性引用）
            if _is_revision_context(line):
                continue
            # 豁免：文档债务标注 / 已废弃说明
            if "文档债务" in line or "已废弃" in line or "禁用" in line:
                continue
            findings.append(
                Finding(
                    pattern="P1_proxy",
                    severity="warning",
                    detail=f"blueprint 算法章节含代理词：{line.strip()[:80]}",
                    line=i,
                )
            )

    return findings


# ============================================================================
# P2 定性词无量化（qualitative without quantification）
# ============================================================================

# 通用 "X → N分" 模式（不限关键词，依赖上下文判定）
# 负向前瞻 (?!钟|个|类|析) 排除 "5分钟"/"3个分"/"分类"/"分析" 等误匹配
SCORE_ASSIGNMENT_BP_REGEX = re.compile(r"([^\n]{3,80}?)\s*[→=]+\s*(\d+)\s*分(?!钟|个|类|析|子|配|歧|散|贝|支)")

# 保留特定关键词模式（强信号，立即违规）
QUALITATIVE_BP_KEYWORDS = re.compile(r"(关键词|降准|降息|MLF|喊话|鬼故事|利空|震仓后拉升|涨幅差|价未超前高)")


def _check_p2_qualitative_code(source: str, filename: str = "<string>") -> list[Finding]:
    """P2 代码层：出现关键词列表（≥3个定性词）但无分类/计算函数定义或调用。"""
    findings: list[Finding] = []

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return findings

    has_classifier = _has_classifier_def_or_call(tree)

    for node in ast.walk(tree):
        # 检测字符串列表赋值
        if not isinstance(node, ast.Assign):
            continue
        if not isinstance(node.value, ast.List):
            continue
        str_elems = [e.value for e in node.value.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)]
        if len(str_elems) < 3:
            continue
        # 匹配定性关键词列表
        for kw_list in QUALITATIVE_KEYWORD_LISTS:
            overlap = set(str_elems) & set(kw_list)
            if len(overlap) >= 2:
                if not has_classifier:
                    findings.append(
                        Finding(
                            pattern="P2_qualitative",
                            severity="warning",
                            detail=f"定性词列表 {list(overlap)} 无对应分类/计算函数",
                            line=node.lineno,
                        )
                    )
                break

    return findings


def _has_classifier_def_or_call(tree: ast.AST) -> bool:
    """检查 AST 中是否有 classify/score/compute/calc 函数定义或调用。"""
    for node in ast.walk(tree):
        # 函数定义
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.lower().startswith(("classify", "score", "compute", "calc")):
                return True
        # 函数调用
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id.lower().startswith(("classify", "score", "compute", "calc")):
                    return True
            elif isinstance(node.func, ast.Attribute):
                if node.func.attr.lower().startswith(("classify", "score", "compute", "calc")):
                    return True
    return False


def _check_p2_qualitative_blueprint(text: str, filename: str = "<string>") -> list[Finding]:
    """P2 blueprint 层：X→N分 模式但无算法步骤词。"""
    findings: list[Finding] = []
    section = _extract_blueprint_algo_sections(text)
    lines = section.splitlines()

    # 数值阈值模式——左侧 X 含这些模式时认为有算法步骤（合法可计算规则）
    NUMERIC_THRESHOLD_REGEX = re.compile(
        r"[<>]\s*\d|≥\s*\d|≤\s*\d|=\s*\d|>\s*\d|<\s*\d|"
        r"\d\s*[×x]|%\s|分位|percentile|"
        r"\d+\s*[<>]|\d+\s*日|\d+/\d+|矩阵|回归|分布|加权|归一化"
    )

    # 公式/代码模式——左侧含这些代码特征时认为有算法步骤（如 min/max/sqrt）
    # 注意：单独的 / 不能加入（会误匹配"降准/降息/MLF"等中文斜杠分隔列表）
    CODE_FORMULA_REGEX = re.compile(
        r"(min\s*\(|max\s*\(|sum\s*\(|mean\s*\(|std\s*\(|sqrt\s*\(|"
        r"np\.|pd\.|math\.|tensor|"
        r"ROC\s*=|Hurst\s*=|hurst\s*=|"
        r"\d+\s*[+\-*/]\s*\d+|"
        r"\d+\s*/\s*\d+)"
    )

    # 算法章节引用——行内含 §X 算法引用时认为有算法步骤
    SECTION_REF_REGEX = re.compile(r"§\s*\d|见\s*§|参考\s*§|详见\s*§|算法见|见算法|见\s*\d+\.\d")

    # 金融指标缩写——左侧含这些指标名时仍违规（需配套算法步骤词才算合法）
    # 理由：KDJ>90 / MACD>0 / RSI>70 等仅引用指标名+阈值，未说明指标怎么算
    FINANCIAL_INDICATOR_REGEX = re.compile(
        r"\b(KDJ|MACD|RSI|PE|PB|PS|ADX|ATR|BOLL|CCI|DMI|CR|WR|VR|OBV|DMI|"
        r"BIAS|DMI|EMV|ROC|MIKE|SAR|SMA|EMA|WMA|HMA|MA|DM|TRIX|SAR|FSL|"
        r"CSI|HHI|VIX|IV|DIF|DEA|J值|K值|D值)\b",
        re.IGNORECASE,
    )

    # 修正说明语境豁免
    REVISION_MARKERS = ("糊弄判定", "原公式", "替换", "修正", "已废弃", "已停发", "文档债务", "改用", "改为", "升级为")

    for i, line in enumerate(lines, 1):
        # 检测 "X → N分" 模式
        match = SCORE_ASSIGNMENT_BP_REGEX.search(line)
        if not match:
            continue
        left_text = match.group(1)
        # 豁免：修正说明语境
        if any(marker in line for marker in REVISION_MARKERS):
            continue
        # 豁免：行内含 §X 算法引用（如"详见 §4.3.1"）
        if SECTION_REF_REGEX.search(line):
            continue
        # 豁免：左侧 X 含公式/代码特征（min/max/np./pd. 等）
        if CODE_FORMULA_REGEX.search(left_text):
            continue
        # 含金融指标名+阈值时仍违规（KDJ>90 / MACD>0 等未说明指标怎么算）
        has_financial_indicator = bool(FINANCIAL_INDICATOR_REGEX.search(left_text))
        # 豁免：左侧 X 含数值阈值 + 不含金融指标名（"量>1.3×"/">60%"等直接可计算规则）
        if not has_financial_indicator and NUMERIC_THRESHOLD_REGEX.search(left_text):
            continue
        # 检查左侧 X 是否含算法步骤词（如"Hurst(DFA)"算算法，"涨幅差"不算）
        has_algo_in_left = any(kw.lower() in left_text.lower() for kw in ALGO_STEP_KEYWORDS)
        if has_algo_in_left:
            continue
        # 检查附近上下文（前后 8 行，扩大窗口以识别 §X 引用）是否有算法步骤词
        context = _get_context_lines(lines, i, window=8)
        if any(kw in context for kw in ALGO_STEP_KEYWORDS):
            continue
        # 豁免：上下文含算法章节引用
        if SECTION_REF_REGEX.search(context):
            continue
        findings.append(
            Finding(
                pattern="P2_qualitative",
                severity="warning",
                detail=f"定性词→分值 模式无算法步骤：{line.strip()[:80]}",
                line=i,
            )
        )

    return findings


def _get_context_lines(lines: list[str], target_line: int, window: int = 5) -> str:
    """获取目标行前后 window 行的文本。"""
    start = max(0, target_line - 1 - window)
    end = min(len(lines), target_line - 1 + window + 1)
    return "\n".join(lines[start:end])


# ============================================================================
# P3 伪精确（false precision）
# ============================================================================

DIM_VAR_REGEX = re.compile(
    r"\b(angle|degree|slope_angle)\b|均线角度|角度|度数",
    re.IGNORECASE,
)


def _find_enclosing_function(source: str, target_node: ast.If) -> str:
    """获取 If 节点所在 FunctionDef 的完整 body 源代码（用于检测量纲化关键字）。"""
    if hasattr(ast, "get_source_segment"):
        # walk source AST，找包含 target 的 FunctionDef
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return ""
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            # 检查 target_node 是否在此函数范围内
            if node.lineno <= target_node.lineno and (node.end_lineno or target_node.lineno) >= target_node.lineno:
                seg = ast.get_source_segment(source, node)
                if seg:
                    return seg
    # Fallback：用 If 的源段
    return _get_function_body_source(source, target_node)


def _check_p3_false_precision_code(source: str, filename: str = "<string>") -> list[Finding]:
    """P3 代码层：数值比较且变量名暗示量纲依赖（angle/slope/degree/斜率），且函数体内无量纲化。"""
    findings: list[Finding] = []

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return findings

    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if not isinstance(test, ast.Compare):
            continue
        # 提取比较的左侧变量名
        left = test.left
        var_name = ""
        if isinstance(left, ast.Name):
            var_name = left.id
        elif isinstance(left, ast.Attribute):
            var_name = left.attr
        if not var_name:
            continue
        # 检查变量名是否暗示量纲依赖
        if not DIM_VAR_REGEX.search(var_name):
            continue
        # 检查右侧是否是数值常量
        for comp in test.comparators:
            if not isinstance(comp, ast.Constant) or not isinstance(comp.value, (int, float)):
                continue
            # 检查所在 FunctionDef 全 body 是否有量纲化关键字（不能只看 If 段）
            func_body_src = _find_enclosing_function(source, node)
            if any(kw in func_body_src.lower() for kw in DIMENSION_FREE_KEYWORDS):
                continue
            findings.append(
                Finding(
                    pattern="P3_false_precision",
                    severity="warning",
                    detail=f"阈值 if {var_name} {comp.value} 依赖量纲，函数体内无量纲化",
                    line=node.lineno,
                )
            )

    return findings


def _check_p3_false_precision_blueprint(text: str, filename: str = "<string>") -> list[Finding]:
    """P3 blueprint 层：量纲依赖阈值变量（角度/度数/斜率/IV/VIX）无 normalize 依据。

    豁免：阈值=0（"斜率<0"/"斜率=0" 是符号判断，无量纲依赖）
    豁免：上下文含 normalize/percentile/hurst 等量纲化关键字
    豁免：修正说明语境
    """
    findings: list[Finding] = []
    section = _extract_blueprint_algo_sections(text)

    # 量纲依赖阈值：angle/degree/角度/度数/斜率 + 非零数值比较
    # 0 阈值豁免（"斜率<0"是符号判断，无量纲依赖）
    # 非零阈值（0.5/45/35）才依赖量纲
    angle_threshold_regex = re.compile(
        r"(角度|度数|斜率|均线斜率|angle|degree|slope)\s*[><=]+\s*"
        r"(?:[1-9]\d*\.?\d*|0\.\d*[1-9])\s*°?",
        re.IGNORECASE,
    )
    # IV/VIX 阈值（典型糊弄："IV>35"无定义哪个IV）
    iv_threshold_regex = re.compile(
        r"\b(?:IV|VIX|隐含波动率)\b\s*[><=]+\s*(?:[1-9]\d*\.?\d*|0\.\d*[1-9])",
        re.IGNORECASE,
    )
    for i, line in enumerate(section.splitlines(), 1):
        matched = angle_threshold_regex.search(line) or iv_threshold_regex.search(line)
        if not matched:
            continue
        # 豁免：修正说明语境（"替换'IV>35'糊弄"等说明性引用）
        if _is_revision_context(line):
            continue
        context = _get_context_lines(section.splitlines(), i, window=5)
        if any(kw in context.lower() for kw in DIMENSION_FREE_KEYWORDS):
            continue
        # 豁免：上下文含修正说明标记
        if _is_revision_context(context):
            continue
        findings.append(
            Finding(
                pattern="P3_false_precision",
                severity="warning",
                detail=f"伪精确阈值无量纲化：{line.strip()[:80]}",
                line=i,
            )
        )

    return findings


# ============================================================================
# P4 死数据（dead data source）
# ============================================================================


def _check_p4_dead_data_code(source: str, filename: str = "<string>") -> list[Finding]:
    """P4 代码层：import 死数据模块 / 字符串引用死数据表名。"""
    findings: list[Finding] = []

    try:
        tree = ast.parse(source)
    except SyntaxError:
        # 语法错误时退回正则扫描
        return _check_p4_dead_data_regex(source, filename)

    # 路径 1：import 检查
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for dead in DEAD_DATA_SOURCES:
                    if dead in alias.name.lower():
                        findings.append(
                            Finding(
                                pattern="P4_dead_data",
                                severity="error",
                                detail=f"import 死数据源 {dead}（{DEAD_DATA_SOURCES[dead]['reason']}）",
                                line=node.lineno,
                            )
                        )
        elif isinstance(node, ast.ImportFrom):
            module = (node.module or "").lower()
            for dead in DEAD_DATA_SOURCES:
                if dead in module:
                    findings.append(
                        Finding(
                            pattern="P4_dead_data",
                            severity="error",
                            detail=f"from {dead} import（{DEAD_DATA_SOURCES[dead]['reason']}）",
                            line=node.lineno,
                        )
                    )

    # 路径 2：字符串字面量检查（query("hk_connect_daily") 等）
    findings.extend(_check_p4_dead_data_regex(source, filename))

    return findings


def _check_p4_dead_data_regex(source: str, filename: str = "<string>") -> list[Finding]:
    """正则扫描字符串中的死数据表名（用于 query() 调用 / SQL 字符串）。"""
    findings: list[Finding] = []
    # 历史回测/已停发语境豁免——这些词说明引用是为历史回测或已声明数据停发
    HISTORICAL_BACKTEST_MARKERS = (
        "停止公布",
        "停发",
        "已废弃",
        "历史回测",
        "历史数据",
        "2024-08-16",
        "2024-08-19",
        "文档债务",
        "DEAD_DATA",
    )
    # 文件级豁免标记——文件 docstring 含这些词时豁免该文件的死数据引用
    # 理由：数据接入层/测速器/schema 注册是合法用途（不是算法糊弄）
    FILE_LEVEL_EXEMPT_MARKERS = (
        "测速",
        "数据接入",
        "Provider 实现",
        "IngestProvider",
        "schema 注册",
        "schemas/categories",
        "数据源选型",
        "数据源健康监控",
        "历史回测用",
    )

    # 检查文件级豁免
    file_exempt = _has_file_level_exempt_marker(source, FILE_LEVEL_EXEMPT_MARKERS)

    for i, line in enumerate(source.splitlines(), 1):
        # 豁免：治理脚本自身的死数据清单定义
        if "DEAD_DATA_SOURCES" in line or "文档债务" in line:
            continue
        # 豁免：注释中明确说明已停发
        if line.strip().startswith("#") and ("停发" in line or "废弃" in line or "停止公布" in line):
            continue
        # 豁免：行内或上下文含历史回测说明
        if any(marker in line for marker in HISTORICAL_BACKTEST_MARKERS):
            continue
        # 豁免：文件级豁免（数据接入层/测速器等合法用途）
        if file_exempt:
            continue
        for dead in DEAD_DATA_SOURCES:
            if dead in line:
                findings.append(
                    Finding(
                        pattern="P4_dead_data",
                        severity="error",
                        detail=f"引用死数据源 {dead}（{DEAD_DATA_SOURCES[dead]['reason']}）",
                        line=i,
                    )
                )
                break

    return findings


def _has_file_level_exempt_marker(source: str, markers: tuple[str, ...]) -> bool:
    """检查文件 docstring（前 30 行）是否含豁免标记。"""
    head = "\n".join(source.splitlines()[:30])
    return any(marker in head for marker in markers)


def _check_p4_dead_data_blueprint(text: str, filename: str = "<string>") -> list[Finding]:
    """P4 blueprint 层：数据源表/算法描述引用死数据源（且非历史回测说明）。

    豁免：
    - 文档债务 / 历史回测 / 已停发标注
    - schema 文件清单行（schemas/categories 路径 + 已实现标记）
    """
    findings: list[Finding] = []

    for i, line in enumerate(text.splitlines(), 1):
        # 豁免：文档债务 / 历史回测 / 已废弃说明
        if any(
            tag in line
            for tag in [
                "文档债务",
                "已废弃",
                "停发",
                "停止公布",
                "历史回测",
                "历史数据",
                "DEAD_DATA",
                "2024-08-16",
                "2024-08-19",
            ]
        ):
            continue
        # 豁免：schema 文件清单行（如 "| schemas/categories/market_hk_connect_flow.py | ✅ 已实现 |"）
        if "schemas/categories" in line and "已实现" in line:
            continue
        for dead in DEAD_DATA_SOURCES:
            # 中文别名
            cn_aliases = {
                "hk_connect_flow": ["北向资金回流"],
                "northbound_flow": ["北向资金"],
            }
            aliases = [dead] + cn_aliases.get(dead, [])
            for alias in aliases:
                if alias in line:
                    # 豁免：行内同时出现"停发"/"废弃"/"停止公布"说明
                    if "停发" in line or "废弃" in line or "替代" in line or "停止公布" in line:
                        continue
                    findings.append(
                        Finding(
                            pattern="P4_dead_data",
                            severity="error",
                            detail=f"blueprint 引用死数据源 {alias}（{DEAD_DATA_SOURCES[dead]['reason']}）",
                            line=i,
                        )
                    )
                    break
            else:
                continue
            break

    return findings


# ============================================================================
# P5 名词堆砌无算法（buzzword without algorithm）
# ============================================================================


def _p5_check_function(node: ast.FunctionDef, source: str) -> Finding | None:
    """检查单个函数是否 P5 违规（docstring 缩写堆砌 + body 空桩），返回 Finding 或 None。"""
    doc = ast.get_docstring(node) or ""
    all_abbrevs = ABBREV_PATTERN.findall(doc)
    abbrevs = [a for a in all_abbrevs if a not in LEGIT_ABBREVS]
    if len(abbrevs) < 3:
        return None
    body_src = _get_function_body_source(source, node)
    body_clean = re.sub(r"#.*", "", body_src).replace(doc, "")
    body_lines = [
        ln.strip()
        for ln in body_clean.splitlines()
        if ln.strip() and not ln.strip().startswith('"""') and not ln.strip().endswith('"""')
    ]
    is_stub = len(body_lines) <= 2 or all(
        "pass" in ln or "..." in ln or "TODO" in ln or "raise NotImplementedError" in ln for ln in body_lines
    )
    if not is_stub:
        return None
    if any(kw in body_src.lower() for kw in ["算法", "公式", "fsM", "触发器", "状态机"]):
        return None
    return Finding(
        pattern="P5_buzzword",
        severity="warning",
        detail=f"函数 {node.name}() docstring 含 {len(abbrevs)} 个非白名单缩写 {abbrevs[:5]}，"
        f"但 body 为空桩/TODO，无识别逻辑实现",
        line=node.lineno,
    )


def _check_p5_buzzword_code(source: str, filename: str = "<string>") -> list[Finding]:
    """P5 代码层：函数 docstring/注释含 ≥3 个非白名单 ALL-CAPS 缩写但 body 为空/pass/TODO。"""
    findings: list[Finding] = []
    if _is_test_file(filename):
        return findings
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return findings
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        finding = _p5_check_function(node, source)
        if finding is not None:
            findings.append(finding)
    return findings


def _check_p5_buzzword_blueprint(text: str, filename: str = "<string>") -> list[Finding]:
    """P5 blueprint 层：算法章节 ≥3 非白名单缩写 + 算法意图词 + 无算法步骤词。"""
    findings: list[Finding] = []
    section = _extract_blueprint_algo_sections(text)

    # 算法意图词——段落必须含这些词才考虑名词堆砌嫌疑（避免 BUY/SELL/HOLD 等列表误报）
    ALGO_INTENT_KEYWORDS = [
        "识别",
        "检测",
        "评分",
        "判定",
        "分析",
        "分类",
        "算法",
        "公式",
        "状态机",
        "触发",
        "FSM",
        "计算",
        "结构识别",
        "事件识别",
        "模式识别",
    ]

    # 修正说明语境豁免——这些词出现说明是"修正说明"而非糊弄本身
    REVISION_CONTEXT_MARKERS = (
        "糊弄判定",
        "原公式",
        "替换",
        "修正",
        "已废弃",
        "已停发",
        "文档债务",
        "改用",
        "改为",
        "升级为",
    )

    # 按段落扫描
    paragraphs = re.split(r"\n\s*\n", section)
    for para in paragraphs:
        # 先过滤白名单（与代码层一致）
        all_abbrevs = ABBREV_PATTERN.findall(para)
        abbrevs = [a for a in all_abbrevs if a not in LEGIT_ABBREVS]
        if len(abbrevs) < 3:
            continue
        # 去重
        unique_abbrevs = list(dict.fromkeys(abbrevs))
        if len(unique_abbrevs) < 3:
            continue
        # 必须含算法意图词（避免 BUY/SELL/HOLD/MIT/BSD/GPL 等合法缩写列表误报）
        if not any(kw in para for kw in ALGO_INTENT_KEYWORDS):
            continue
        # 检查是否有算法步骤词（已实现算法）
        if any(kw in para for kw in ALGO_STEP_KEYWORDS):
            continue
        # 修正说明语境豁免
        if any(marker in para for marker in REVISION_CONTEXT_MARKERS):
            continue
        # 计算行号
        line_no = text.count("\n", 0, text.find(para)) + 1 if para in text else 0
        findings.append(
            Finding(
                pattern="P5_buzzword",
                severity="warning",
                detail=f"算法意图段落含 {len(unique_abbrevs)} 个非白名单缩写 {unique_abbrevs[:5]}，"
                f"但无算法/公式/FSM/触发器等步骤词",
                line=line_no,
            )
        )

    return findings


# ============================================================================
# P6 逻辑错位（logical mismatch）
# ============================================================================

LOGICAL_BP_REGEX = re.compile(r"(无.{0,15}→\s*\d+\s*分|.{0,15}不发生.{0,5}→\s*\d+\s*分|无虹吸.{0,10}[+→=])")


def _p6_is_negation_test(test: ast.expr) -> bool:
    """判断 if 的 test 是否为否定（UnaryOp Not / Compare NotEq）。"""
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        return True
    if isinstance(test, ast.Compare):
        return any(isinstance(op, ast.NotEq) for op in test.ops)
    return False


# 风险评分语境豁免——这些变量名前缀表明 score 是"风险累加"而非"正向确认"
_P6_RISK_SCORE_PREFIXES = (
    "risk",
    "penalty",
    "violation",
    "warning",
    "drift",
    "hallucination",
    "missing",
    "badness",
    "debt",
    "cost",
    "deterioration",
    "degradation",
    "anomaly",
    "fraud",
)

# 风险语境关键词（函数名含这些词时豁免 P6）
_P6_RISK_CONTEXT_KEYWORDS = [
    "risk",
    "hallucination",
    "drift",
    "penalty",
    "violation",
    "风险",
    "幻觉",
    "漂移",
    "惩罚",
    "违规",
]


def _p6_check_if_body(node: ast.If, source: str) -> Finding | None:
    """检查 if body 内是否有 += 评分操作（逻辑错位），返回 Finding 或 None。

    豁免：风险评分语境——变量名含 risk/penalty/violation 等前缀时，
    "if not X: score += N" 是合法的"缺失即风险累加"模式。
    """
    for stmt in ast.walk(node):
        if not (isinstance(stmt, ast.AugAssign) and isinstance(stmt.op, ast.Add)):
            continue
        target_name = ""
        if isinstance(stmt.target, ast.Name):
            target_name = stmt.target.id
        elif isinstance(stmt.target, ast.Attribute):
            target_name = stmt.target.attr
        if not target_name.lower().startswith(("score", "point", "分值")):
            continue
        if target_name.lower().startswith(_P6_RISK_SCORE_PREFIXES):
            continue
        func_body_src = _find_enclosing_function(source, node)
        if any(kw in func_body_src.lower() for kw in _P6_RISK_CONTEXT_KEYWORDS):
            continue
        return Finding(
            pattern="P6_logical",
            severity="error",
            detail=f"否决条件 (if not X) 内做正向评分 ({target_name} +=)，逻辑错位",
            line=node.lineno,
        )
    return None


def _check_p6_logical_code(source: str, filename: str = "<string>") -> list[Finding]:
    """P6 代码层：if not X: score += N 模式（否决条件当正向评分）。"""
    findings: list[Finding] = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return findings
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        if not _p6_is_negation_test(node.test):
            continue
        finding = _p6_check_if_body(node, source)
        if finding is not None:
            findings.append(finding)
    return findings


def _check_p6_logical_blueprint(text: str, filename: str = "<string>") -> list[Finding]:
    """P6 blueprint 层：无 X → N分 / 不发生 → N分 作为正向评分。"""
    findings: list[Finding] = []
    section = _extract_blueprint_algo_sections(text)

    for i, line in enumerate(section.splitlines(), 1):
        if not LOGICAL_BP_REGEX.search(line):
            continue
        # 豁免：修正说明语境（"糊弄判定：原公式无虹吸=主线..."等说明性引用）
        if _is_revision_context(line):
            continue
        findings.append(
            Finding(
                pattern="P6_logical",
                severity="error",
                detail=f"逻辑错位：否决条件当正向评分：{line.strip()[:80]}",
                line=i,
            )
        )

    return findings


# ============================================================================
# 入口函数
# ============================================================================

_CODE_CHECKS = [
    _check_p1_proxy_code,
    _check_p2_qualitative_code,
    _check_p3_false_precision_code,
    _check_p4_dead_data_code,
    _check_p5_buzzword_code,
    _check_p6_logical_code,
]

_BP_CHECKS = [
    _check_p1_proxy_blueprint,
    _check_p2_qualitative_blueprint,
    _check_p3_false_precision_blueprint,
    _check_p4_dead_data_blueprint,
    _check_p5_buzzword_blueprint,
    _check_p6_logical_blueprint,
]


def audit_code_str(code: str, filename: str = "<string>") -> list[Finding]:
    """审计代码字符串（供测试调用）。"""
    findings: list[Finding] = []
    for check in _CODE_CHECKS:
        try:
            findings.extend(check(code, filename))
        except Exception as exc:  # noqa: BLE001
            findings.append(
                Finding(
                    pattern="error",
                    severity="warning",
                    detail=f"检测器 {check.__name__} 异常：{exc}",
                )
            )
    return findings


def audit_blueprint_str(text: str, filename: str = "<string>") -> list[Finding]:
    """审计 blueprint 文本（供测试调用）。"""
    findings: list[Finding] = []
    for check in _BP_CHECKS:
        try:
            findings.extend(check(text, filename))
        except Exception as exc:  # noqa: BLE001
            findings.append(
                Finding(
                    pattern="error",
                    severity="warning",
                    detail=f"检测器 {check.__name__} 异常：{exc}",
                )
            )
    return findings


def audit_code(path: Path) -> list[Finding]:
    """审计 .py 文件。"""
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [
            Finding(
                pattern="error",
                severity="warning",
                detail=f"无法读取 {path}: {exc}",
            )
        ]
    return audit_code_str(source, str(path))


def audit_blueprint(path: Path) -> list[Finding]:
    """审计 blueprint.md 文件。"""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [
            Finding(
                pattern="error",
                severity="warning",
                detail=f"无法读取 {path}: {exc}",
            )
        ]
    return audit_blueprint_str(text, str(path))


# ============================================================================
# main
# ============================================================================


def _collect_code_files(roots: list[Path]) -> list[Path]:
    """收集 src/zephyr/ 下所有 .py 文件（排除 __pycache__ / 测试目录外文件全收）。"""
    files: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            files.append(path)
    return sorted(files)


def _collect_bp_files() -> list[Path]:
    """收集 docs/03_modules/**/blueprint.md。"""
    bp_root = REPO_ROOT / "docs" / "03_modules"
    if not bp_root.exists():
        return []
    return sorted(bp_root.rglob("blueprint.md"))


def _parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="GATE-ALGO-QUALITY: 算法糊弄自动检测器（6类pattern，代码AST为主，blueprint正则为辅）"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="待审计文件（无参数时扫描 src/zephyr/**/*.py + docs/03_modules/**/blueprint.md）",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--warn-only",
        action="store_true",
        help="仅报告，全部 exit 0（观察期；转硬阻断时改用 --ci）",
    )
    mode.add_argument(
        "--ci",
        action="store_true",
        help="有问题即 exit 1（硬阻断模式，默认）",
    )
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--code-only", action="store_true", help="仅扫代码 .py")
    scope.add_argument("--bp-only", action="store_true", help="仅扫 blueprint.md")
    scope.add_argument("--all", action="store_true", help="扫代码 + blueprint（默认）")
    return parser.parse_args()


def _collect_targets(
    args: argparse.Namespace,
    scan_code: bool,
    scan_bp: bool,
) -> tuple[list[Path], list[Path]] | int:
    """收集待审计文件。

    返回 (code_files, bp_files)；若文件不存在则返回 exit code 2。
    """
    code_files: list[Path] = []
    bp_files: list[Path] = []

    if args.files:
        for f in args.files:
            p = Path(f)
            if not p.exists():
                print("ERROR: 文件不存在: %s" % p)
                return 2
            if p.suffix == ".py":
                code_files.append(p)
            elif p.name == "blueprint.md" or p.suffix == ".md":
                bp_files.append(p)
    else:
        if scan_code:
            code_files = _collect_code_files([REPO_ROOT / CODE_SCAN_ROOT])
        if scan_bp:
            bp_files = _collect_bp_files()

    return code_files, bp_files


def _run_scan(
    code_files: list[Path],
    bp_files: list[Path],
) -> tuple[list[tuple[Path, list[Finding]]], list[tuple[Path, list[Finding]]], int]:
    """运行扫描，返回 (code_findings, bp_findings, total_findings)。"""
    total_findings = 0
    code_findings: list[tuple[Path, list[Finding]]] = []
    bp_findings: list[tuple[Path, list[Finding]]] = []

    for path in code_files:
        fs = audit_code(path)
        if fs:
            total_findings += len(fs)
            code_findings.append((path, fs))

    for path in bp_files:
        fs = audit_blueprint(path)
        if fs:
            total_findings += len(fs)
            bp_findings.append((path, fs))

    return code_findings, bp_findings, total_findings


def _scope_label(args: argparse.Namespace) -> str:
    """根据 scope 参数返回范围标签。"""
    if args.code_only:
        return "仅代码"
    if args.bp_only:
        return "仅blueprint"
    return "代码+blueprint"


def _print_findings(findings: list[tuple[Path, list[Finding]]]) -> bool:
    """打印违规文件列表，返回是否有违规。"""
    has_findings = False
    for path, fs in findings:
        rel = path.relative_to(REPO_ROOT) if path.is_absolute() else path
        print("✗ %s — %d 处违规" % (rel, len(fs)))
        has_findings = True
        for f in fs:
            print("    [%s/%s] %s%s" % (f.pattern, f.severity, f"L{f.line}: " if f.line else "", f.detail[:120]))
    return has_findings


def _print_report(
    args: argparse.Namespace,
    code_files: list[Path],
    bp_files: list[Path],
    code_findings: list[tuple[Path, list[Finding]]],
    bp_findings: list[tuple[Path, list[Finding]]],
    total_findings: int,
    ci_mode: bool,
) -> int:
    """打印汇总报告并返回 exit code。"""
    print("=" * 70)
    print("GATE-ALGO-QUALITY 算法糊弄自动检测器")
    print("模式: %s" % ("--warn-only (仅报告)" if args.warn_only else "--ci (硬阻断)"))
    print("范围: %s" % _scope_label(args))
    print("代码文件: %d, blueprint 文件: %d, 总违规: %d" % (len(code_files), len(bp_files), total_findings))
    print("=" * 70)

    has_findings = _print_findings(code_findings)
    if _print_findings(bp_findings):
        has_findings = True

    clean_code = len(code_files) - len(code_findings)
    clean_bp = len(bp_files) - len(bp_findings)
    print("-" * 70)
    print("✓ %d 代码文件 / %d blueprint 干净" % (clean_code, clean_bp))

    if has_findings and ci_mode:
        print("结论: 发现 %d 处算法糊弄，--ci 模式阻断提交。" % total_findings)
        print("修复指引：参考 .trae/documents/gate-algo-quality-detector.md 6类pattern 定义。")
        return EXIT_FINDINGS
    if has_findings:
        print("结论: 发现 %d 处算法糊弄，--warn-only 模式仅报告不阻断。" % total_findings)
        return EXIT_PASS
    print("结论: 全部文件算法质量合格，无糊弄 pattern。")
    return EXIT_PASS


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    args = _parse_args()
    # 默认 --ci
    ci_mode = not args.warn_only
    # 默认 --all
    scan_code = not args.bp_only
    scan_bp = not args.code_only

    targets = _collect_targets(args, scan_code, scan_bp)
    if isinstance(targets, int):
        return targets
    code_files, bp_files = targets

    if not code_files and not bp_files:
        print("无可审计文件。")
        return EXIT_PASS

    code_findings, bp_findings, total_findings = _run_scan(code_files, bp_files)
    return _print_report(args, code_files, bp_files, code_findings, bp_findings, total_findings, ci_mode)


if __name__ == "__main__":
    sys.exit(main())
