# [BLUEPRINT] MOD-GOV_ALGO_EXTRACTOR | docs/03_modules/_cross_layer/gov_scripts/blueprint.md
# [MODULE] scripts.governance._shared.code_algorithm_extractor
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.frontmatter (parse_frontmatter_from_file, parse_py_header_from_file)
# [CONSUMERS] scripts/governance/d5_architecture/generators/generate_module_algorithm_overview.py; generate_domain_doc.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 降级不抛异常; 三档优先级(code>blueprint>empty); 截断长度上限; __init__.py回退扫描子文件; blueprint章节鲁棒匹配; ALGO_FLOW标记块(含边段)整块剥离不泄漏进文字字段
# [MODIFY-GUARD] 修改需同步更新 tests/governance/test_code_algorithm_extractor.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 解析失败->source_type='empty'; 文件不存在->empty; AST损坏->empty
# [TESTS] tests/governance/test_code_algorithm_extractor.py
# [TTL] permanent
"""code_algorithm_extractor.py — 模块核心算法提取器（派生逻辑真源）。

从代码 .py docstring + header，或 blueprint.md 章节，提取模块的核心算法描述，
供 generate_module_algorithm_overview.py（全局纵览）和 generate_domain_doc.py（域文档算法章节）
两个生成器共享消费，保证同一模块算法描述一致。

[BLUEPRINT] MOD-GOV_ALGO_EXTRACTOR | gov_scripts/blueprint.md
[MODULE] scripts.governance._shared.code_algorithm_extractor
[INVARIANTS] 降级不抛异常; 三档优先级(code>blueprint>empty); 截断上限; __init__.py回退扫描子文件; blueprint章节鲁棒匹配; ALGO_FLOW标记块(含边段)整块剥离
[CONSUMERS] generate_module_algorithm_overview.py; generate_domain_doc.py
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] 解析失败/文件不存在/AST损坏 → source_type='empty' 不抛
[DOMAIN] D_GOV_SCRIPTS

三大修正点（v3 样本制作发现）：
  ① depgraph path 常指向 __init__.py，但算法 docstring 在子文件 → _find_richest_docstring_file 回退扫描
  ② 三档判定看"文件是否真实存在"而非 build_status（在生成器层判定，本模块只管提取）
  ③ blueprint 章节结构不统一（非都是 §3/§4）→ _find_section 鲁棒关键词匹配 + 概述兜底

使用方式：
    from code_algorithm_extractor import (
        AlgorithmSummary, extract_algorithm_from_code,
        extract_algorithm_from_blueprint, build_blueprint_index,
    )
    summary = extract_algorithm_from_code(Path("src/zephyr/regime/core/regime_detector.py"))
"""

from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_SHARED_DIR = str(_THIS_FILE.parent)
if _SHARED_DIR not in sys.path:
    sys.path.insert(0, _SHARED_DIR)

from frontmatter import parse_frontmatter_from_file, parse_py_header_from_file  # noqa: E402

# 仓库根：含 scripts/ 和 src/ 的目录
REPO_ROOT = next(p for p in _THIS_FILE.parents if (p / "scripts").is_dir() and (p / "src").is_dir())

# 截断上限（防止纵览爆炸；域文档可放宽）
MAX_SUMMARY = 300
MAX_ALGO_STEPS = 500
MAX_INVARIANTS = 200

# 性能护栏（_find_richest_docstring_file 回退扫描）
_MAX_SCAN_CANDIDATES = 60  # 大包最多扫描 60 个候选 .py（如 MOD-BT-001 有 289 子文件）
_RICH_DOC_LEN = 200  # docstring ≥200 字视为富（算法真源），立即早停


@dataclass
class AlgorithmSummary:
    """模块核心算法摘要（三档来源统一结构）。"""

    source_type: str  # 'code' | 'blueprint' | 'empty'
    module_id: str = ""
    module_name: str = ""  # module docstring 首行 或 blueprint frontmatter title
    summary: str = ""  # 概述（≤300字）
    algo_steps: str = ""  # 算法步骤（≤500字）
    invariants: str = ""  # 不变量（≤200字）
    source_path: str = ""  # 真源文件相对仓库根路径
    source_line_range: str = ""  # "L18-L55" 行号锚点
    blueprint_ref: str = ""  # blueprint.md 相对路径（运营态也显示作对照）
    quality_issue: str = ""  # 质量评估（✅完整/⚠低质量/❌缺失 + 原因）
    algo_flow: AlgoFlowData | None = None  # ALGO_FLOW 结构化推导流程（§4.16，仅运营态代码有标记时）


# ── ALGO_FLOW 结构化数据（§4.16，算法全景图推导流程）──────────


@dataclass
class AlgoFlowNode:
    """ALGO_FLOW 推导流程节点（§4.14 五类节点统一结构）。

    layer 取值：输入/特征/指标/算法/输出。不同 layer 用不同字段子集渲染。
    """

    id: str
    layer: str = ""  # 输入/特征/指标/算法/输出
    name_zh: str = ""  # 输入层用 name 字段映射到此
    name_en: str = ""
    intro: str = ""  # 一句话简介
    formula: str = ""  # 公式（特征/指标/算法）
    code: str = ""  # 代码位置 file.py L行号 / 输入层代码标识
    registry: str = ""  # factor_registry 状态 / 指标表状态（断点判断）
    is_break: bool = False  # 是否断点节点（连入的边=断点边）
    inputs: str = ""  # 算法节点输入
    outputs: str = ""  # 算法节点输出
    invariant: str = ""  # 不变量
    downstream: str = ""  # 输出节点下游去向
    fields: str = ""  # 输入层节点字段说明
    desc: str = ""  # 算法节点算法描述


@dataclass
class AlgoFlowEdge:
    """ALGO_FLOW 推导流程边（§4.15 断点边规范）。"""

    src: str
    dst: str
    is_break: bool = False  # True=断点边（红色虚线+断点标签），False=正常边（黑色实线）


@dataclass
class AlgoFlowData:
    """ALGO_FLOW 解析结果：节点列表 + 边列表。"""

    nodes: list[AlgoFlowNode] = field(default_factory=list)
    edges: list[AlgoFlowEdge] = field(default_factory=list)


# ── 内部工具 ──────────────────────────────────────────────────


def _truncate(text: str, limit: int) -> str:
    """截断到 limit 字，超长加 …。"""
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "…"


def _empty(module_id: str = "", blueprint_ref: str = "", quality_issue: str = "") -> AlgorithmSummary:
    """构造空摘要（档③缺失/降级）。"""
    return AlgorithmSummary(
        source_type="empty",
        module_id=module_id,
        quality_issue=quality_issue or "无 docstring 无蓝图，需补",
    )


# 修正点①：__init__.py 回退扫描子文件
def _find_richest_docstring_file(py_path: Path) -> tuple[Path, str, int, int]:
    """找到 docstring 最丰富的 .py 文件。

    若 py_path 本身有非空 module docstring（≥30字），直接用它；
    否则（常见于 __init__.py 包入口）扫描同目录及一级子目录的 .py，
    返回 docstring 最长者的 (路径, docstring, 起行, 止行)。

    Returns:
        (actual_path, docstring, start_line, end_line)；py_path 不存在或全部失败 → (py_path, "", 0, 0)
    """
    if not py_path.exists():
        return py_path, "", 0, 0

    best = _parse_module_docstring(py_path)
    # 修正点①加强：__init__.py 通常是包入口说明（非算法真源），即使有 docstring 也扫描子文件找更丰富的；
    # 非 __init__.py 且 docstring 充分（≥30字）则直接用
    if best[1] and len(best[1]) >= 30 and py_path.name != "__init__.py":
        return best

    # 回退扫描：同目录 + 一级子目录
    # 性能护栏（505 模块纵览）：大包（如 MOD-BT-001 有 289 子文件）rglob 全扫会极慢，
    # 限制最多扫描 _MAX_SCAN_CANDIDATES 个候选；中途遇到富 docstring（≥_RICH_DOC_LEN）
    # 即早停——已足够找到算法真源，无需遍历全部。
    candidates: list[tuple[Path, str, int, int]] = []
    if best[1]:
        candidates.append(best)
        if len(best[1]) >= _RICH_DOC_LEN:
            return best
    search_root = py_path.parent
    scanned = 0
    try:
        for sub in sorted(search_root.rglob("*.py")):
            # 限制深度：不深入超过 3 层，跳过 __pycache__/tests/_archive
            rel = sub.relative_to(search_root)
            if len(rel.parts) > 3:
                continue
            if any(p in {"__pycache__", "tests", "_archive"} for p in rel.parts):
                continue
            if sub == py_path:
                continue
            scanned += 1
            if scanned > _MAX_SCAN_CANDIDATES:
                break
            r = _parse_module_docstring(sub)
            if r[1]:
                candidates.append(r)
                # 富 docstring 早停：算法真源已找到，无需继续
                if len(r[1]) >= _RICH_DOC_LEN:
                    return r
    except (OSError, PermissionError):
        pass

    if not candidates:
        return py_path, "", 0, 0
    # 选 docstring 最长的（__init__.py 的包说明通常短于子文件的算法 docstring）
    candidates.sort(key=lambda x: len(x[1]), reverse=True)
    return candidates[0]


def _parse_module_docstring(py_path: Path) -> tuple[Path, str, int, int]:
    """ast.parse 提取 module docstring，返回 (path, docstring, start_line, end_line)。

    失败返回 (path, "", 0, 0)。
    """
    try:
        src = py_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src, filename=str(py_path))
        ds = ast.get_docstring(tree)
        if not ds:
            return py_path, "", 0, 0
        # 估算行范围：找第一个 Expr(Constant) 的行号
        start_line = 1
        end_line = 1
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                start_line = node.lineno
                end_line = node.end_lineno or node.lineno
                break
        return py_path, ds, start_line, end_line
    except (SyntaxError, OSError, ValueError):
        return py_path, "", 0, 0


# 从 module docstring 提取算法步骤段
_ALGO_KEYWORDS = ("算法步骤", "算法", "五子模块", "子模块", "职责", "处理流程", "工作流程", "流程", "步骤")
_INVARIANTS_KEYWORDS = ("不变量", "INVARIANTS", "约束", "硬约束", "不变式")


def _extract_section_from_docstring(docstring: str, keywords: tuple[str, ...]) -> str:
    """从 docstring 里按关键词找段落（如「算法步骤」「不变量」）。

    匹配模式：行首含关键词的行 → 收集到下一个空行或下一个关键词行前。
    找不到返回空串。
    """
    lines = docstring.splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if any(k in stripped for k in keywords) and len(stripped) < 40:
            # 收集后续行直到空行或下一个关键词
            collected: list[str] = []
            for j in range(i + 1, len(lines)):
                nxt = lines[j].strip()
                if not nxt:
                    if collected:
                        break
                    continue
                # 遇到下一个关键词段停止
                if any(k in nxt for k in _ALGO_KEYWORDS + _INVARIANTS_KEYWORDS) and len(nxt) < 40 and nxt != stripped:
                    break
                collected.append(lines[j])
            if collected:
                return "\n".join(collected).strip()
    return ""


def _summary_from_docstring(docstring: str) -> str:
    """module docstring 首段作为概述。"""
    lines = docstring.splitlines()
    # 跳过开头的标题行（如「RegimeDetector — 7态...」）取下一段，或直接取首段
    first_para: list[str] = []
    started = False
    for line in lines:
        if line.strip():
            started = True
            first_para.append(line.strip())
        elif started:
            break
    return " ".join(first_para) if first_para else ""


def _strip_algo_flow_block(docstring: str) -> str:
    """剥离 docstring 里的 ALGO_FLOW 标记块，返回剩余人类可读文字。

    剥离范围：``# [ALGO_FLOW]`` 起 → ``# [/ALGO_FLOW]`` 止的整块，以及紧随其后的
    ``# 边:`` 边定义段（连续的空行或 ``#`` 开头注释行，直到首个非 # 内容行）。
    无结束标记时剥到 docstring 末尾（与 parse_algo_flow 的块界定一致）。

    这些 # 注释行是机器解析标记（§4.16 已由 parse_algo_flow 解析成推导流程图），
    概述/算法步骤等文字字段不应含——整块剥离在截断之前，不会留下 ``# 边…``
    这种截断残行（残行在 Markdown blockquote 里会被渲染成 H1 大字）。
    """
    if not docstring or _ALGO_FLOW_START not in docstring:
        return docstring
    out: list[str] = []
    in_block = False
    block_done = False  # [/ALGO_FLOW] 已过，正处于其后的边定义段
    for line in docstring.splitlines():
        stripped = line.strip()
        if in_block:
            if _ALGO_FLOW_END in stripped:
                in_block = False
                block_done = True
            continue
        if not block_done:
            if _ALGO_FLOW_START in stripped:
                in_block = True
                continue
            out.append(line)
            continue
        # 边定义段（# 边: / # X --> Y）：跳过空行和 # 注释行，首个真实内容行起恢复保留
        if not stripped or stripped.startswith("#"):
            continue
        block_done = False
        out.append(line)
    return "\n".join(out)


# ── 公开 API ──────────────────────────────────────────────────


def extract_algorithm_from_code(
    py_path: Path | str,
    module_id: str = "",
    blueprint_ref: str = "",
    truncate: bool = True,
) -> AlgorithmSummary:
    """从 .py 代码提取算法摘要（档①运营态，以代码为准）。

    修正点①：py_path 指向 __init__.py 时回退扫描子文件找最丰富 docstring。
    降级：解析失败/文件不存在 → source_type='empty'，不抛异常。

    Args:
        py_path: .py 文件路径（绝对或相对仓库根）
        module_id: 模块 ID（由调用方从 depgraph 传入）
        blueprint_ref: blueprint 相对路径（作对照显示）
        truncate: True=按 MAX_* 上限截断（纵览用，501 模块防爆）；
                  False=不截断返回完整文本（域文档用，域内检修完整视角）。
                  不截断时仍走 _find_richest_docstring_file 找算法真源。
    """
    py_path = Path(py_path)
    if not py_path.is_absolute():
        py_path = REPO_ROOT / py_path
    if not py_path.exists():
        return _empty(module_id, blueprint_ref, f"代码文件不存在: {py_path}")

    try:
        actual_path, docstring, start_line, end_line = _find_richest_docstring_file(py_path)
        if not docstring:
            return _empty(module_id, blueprint_ref, f"无 module docstring: {py_path.name}")

        # ALGO_FLOW 标记块（含 # 边: 段）是机器解析标记（§4.16 由 parse_algo_flow 解析成
        # 推导图承载），概述/算法步骤/不变量等文字字段先整块剥离——否则标记行会泄漏进
        # 概述（整段 YAML 挤一行）或截断残留「# 边…」半行（blockquote 里渲染成 H1 大字）。
        text_doc = _strip_algo_flow_block(docstring)
        had_algo_flow = text_doc != docstring

        # header [INVARIANTS] / [BLUEPRINT] / [MODULE]
        header = parse_py_header_from_file(actual_path) or {}
        invariants = header.get("invariants", "") or _extract_section_from_docstring(text_doc, _INVARIANTS_KEYWORDS)

        # module_name：docstring 首行（剥离标记后）或 header module
        text_lines = [ln for ln in text_doc.splitlines() if ln.strip()]
        first_line = text_lines[0].strip() if text_lines else ""
        module_name = first_line or header.get("module", "")

        summary = _summary_from_docstring(text_doc)
        algo_steps = _extract_section_from_docstring(text_doc, _ALGO_KEYWORDS)
        # 若没找到算法步骤段，用整个 docstring（截断）——docstring 本身即算法描述；
        # 但 docstring 含 ALGO_FLOW 块时算法细节已由推导图承载，剥离后的残文本
        # （多为包入口元信息行）不拿来凑数——留空，生成器会提示「见下方推导流程图」。
        if not algo_steps and not had_algo_flow:
            algo_steps = text_doc

        rel_path = str(actual_path.relative_to(REPO_ROOT)).replace("\\", "/")
        line_range = f"L{start_line}-L{end_line}" if start_line else ""

        # ALGO_FLOW 结构化推导流程（§4.16，运营态代码有标记时解析；无标记返回 None）
        algo_flow_data = parse_algo_flow(docstring)

        # 有 ALGO_FLOW 推导图的模块算法信息完整（由图承载），不因文字字段为空误报 ⚠
        quality = "✅ 完整" if ((summary and algo_steps) or algo_flow_data is not None) else "⚠ docstring 结构不完整"

        # 截断策略：纵览 truncate=True 按 MAX_* 截断（防爆）；域文档 truncate=False 保留完整
        if truncate:
            _name, _sum, _algo, _inv = (
                _truncate(module_name, 120),
                _truncate(summary, MAX_SUMMARY),
                _truncate(algo_steps, MAX_ALGO_STEPS),
                _truncate(invariants, MAX_INVARIANTS),
            )
        else:
            _name, _sum, _algo, _inv = module_name, summary, algo_steps, invariants

        return AlgorithmSummary(
            source_type="code",
            module_id=module_id,
            module_name=_name,
            summary=_sum,
            algo_steps=_algo,
            invariants=_inv,
            source_path=rel_path,
            source_line_range=line_range,
            blueprint_ref=blueprint_ref,
            quality_issue=quality,
            algo_flow=algo_flow_data,
        )
    except Exception as e:  # noqa: BLE001 — 降级不抛
        return _empty(module_id, blueprint_ref, f"提取异常: {type(e).__name__}: {e}")


# 修正点③：blueprint 章节鲁棒匹配
_SECTION_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


def _find_section(md_body: str, keywords: tuple[str, ...]) -> str:
    """从 markdown body 按关键词找章节内容。

    修正点③：blueprint 章节结构不统一，按关键词（如「核心规则」「算法」「不变量」）
    模糊匹配标题，收集该标题下到下一个同级或更高级标题前的内容。找不到返回空串。
    """
    matches = list(_SECTION_RE.finditer(md_body))
    for i, m in enumerate(matches):
        title = m.group(2).strip()
        if any(k in title for k in keywords):
            start = m.end()
            # 找下一个同级或更高级标题
            this_level = len(m.group(1))
            end = len(md_body)
            for j in range(i + 1, len(matches)):
                if len(matches[j].group(1)) <= this_level:
                    end = matches[j].start()
                    break
            section = md_body[start:end].strip()
            # 去掉子标题行，保留正文
            lines = [ln for ln in section.splitlines() if not ln.strip().startswith("#")]
            return "\n".join(ln for ln in lines if ln.strip()).strip()
    return ""


def extract_algorithm_from_blueprint(
    blueprint_md_path: Path | str,
    module_id: str = "",
    truncate: bool = True,
) -> AlgorithmSummary:
    """从 blueprint.md 提取算法摘要（档②设计态，以蓝图为准）。

    修正点③：blueprint 章节结构不统一，优先找含「核心规则/算法」关键词的章节，
    找不到用「概述」段 + frontmatter summary 兜底。

    Args:
        blueprint_md_path: blueprint.md 路径
        module_id: 模块 ID
        truncate: True=按 MAX_* 截断；False=不截断（域文档完整视角）
    """
    blueprint_md_path = Path(blueprint_md_path)
    if not blueprint_md_path.is_absolute():
        blueprint_md_path = REPO_ROOT / blueprint_md_path
    if not blueprint_md_path.exists():
        return _empty(module_id, "", f"蓝图文件不存在: {blueprint_md_path}")

    try:
        from frontmatter import parse_frontmatter_with_body_from_file

        fm, body = parse_frontmatter_with_body_from_file(blueprint_md_path)
        fm = fm or {}

        mid = module_id or fm.get("module_id", "") or fm.get("id", "")
        title = fm.get("title", "") or mid

        # 修正点③：鲁棒找算法/规则章节
        algo_steps = _find_section(body, ("核心规则", "核心算法", "算法步骤", "算法", "处理逻辑", "工作原理"))
        invariants = _find_section(body, ("关键不变量", "不变量", "INVARIANTS", "硬约束", "约束", "不变式"))
        summary = _find_section(body, ("概述", "简介", "功能简介", "Overview"))

        # 兜底：找不到算法章节，用概述或 frontmatter description
        if not algo_steps:
            algo_steps = summary or fm.get("description", "") or fm.get("summary", "")
        if not summary:
            summary = fm.get("description", "") or title

        if not (algo_steps or summary):
            return _empty(mid, str(blueprint_md_path.relative_to(REPO_ROOT)).replace("\\", "/"), "蓝图无算法/概述章节")

        rel = str(blueprint_md_path.relative_to(REPO_ROOT)).replace("\\", "/")
        quality = "✅ 完整" if algo_steps else "⚠ 蓝图结构非标准，靠概述兜底"

        if truncate:
            _title, _sum, _algo, _inv = (
                _truncate(title, 120),
                _truncate(summary, MAX_SUMMARY),
                _truncate(algo_steps, MAX_ALGO_STEPS),
                _truncate(invariants, MAX_INVARIANTS),
            )
        else:
            _title, _sum, _algo, _inv = title, summary, algo_steps, invariants

        return AlgorithmSummary(
            source_type="blueprint",
            module_id=mid,
            module_name=_title,
            summary=_sum,
            algo_steps=_algo,
            invariants=_inv,
            source_path=rel,
            source_line_range="",
            blueprint_ref=rel,
            quality_issue=quality,
        )
    except Exception as e:  # noqa: BLE001 — 降级不抛
        return _empty(module_id, "", f"蓝图提取异常: {type(e).__name__}: {e}")


# ── blueprint 索引 ────────────────────────────────────────────

_BLUEPRINT_CACHE: dict[str, Path] | None = None


def build_blueprint_index(blueprints_root: Path | str | None = None) -> dict[str, Path]:
    """扫描所有 blueprint.md，返回 {module_id: path}。

    优先用 frontmatter module_id；缺失则从目录名（MOD-xxx）推导。
    模块级缓存（首次扫描后复用）。
    """
    global _BLUEPRINT_CACHE
    if _BLUEPRINT_CACHE is not None:
        return _BLUEPRINT_CACHE

    root = Path(blueprints_root) if blueprints_root else REPO_ROOT / "docs" / "03_modules"
    index: dict[str, Path] = {}
    try:
        for bp in root.rglob("blueprint.md"):
            fm = parse_frontmatter_from_file(bp) or {}
            mid = fm.get("module_id", "") or fm.get("id", "")
            if not mid:
                # 从路径推导：MOD-xxx 目录名
                parts = bp.parts
                for p in parts:
                    if p.startswith("MOD-"):
                        mid = p
                        break
            if mid:
                index[mid] = bp
    except (OSError, PermissionError):
        pass
    _BLUEPRINT_CACHE = index
    return index


def clear_blueprint_cache() -> None:
    """清缓存（测试用）。"""
    global _BLUEPRINT_CACHE
    _BLUEPRINT_CACHE = None


# ── ALGO_FLOW 解析（§4.16，算法全景图推导流程标记）──────────────

_ALGO_FLOW_START = "# [ALGO_FLOW]"
_ALGO_FLOW_END = "# [/ALGO_FLOW]"

# 节点字段名 → AlgoFlowNode 属性（§4.16.2 YAML 风格标记）
_ALGO_NODE_FIELD_MAP = {
    "name": "name_zh",  # 输入层用 name（中文名+数据类型）
    "fields": "fields",
    "name_zh": "name_zh",
    "name_en": "name_en",
    "intro": "intro",
    "formula": "formula",
    "code": "code",
    "registry": "registry",
    "inputs": "inputs",
    "outputs": "outputs",
    "invariant": "invariant",
    "downstream": "downstream",
    "desc": "desc",
    "is_break": "is_break",
}

# 边定义正则：# SRC -.->|断点| DST  或  # SRC --> DST  或  # SRC -->|label| DST
_ALGO_EDGE_RE = re.compile(r"^#\s*([A-Za-z0-9_]+)\s+(-\.->|-->)(\|[^|]*\|)?\s+([A-Za-z0-9_]+)")

# 节点字段行：key: value（key 含字母数字下划线）
_ALGO_FIELD_RE = re.compile(r"^(\w+)\s*:\s*(.*)$")


def parse_algo_flow(docstring: str) -> AlgoFlowData | None:
    """解析 module docstring 里的 ``# [ALGO_FLOW]`` 块（§4.16）。

    扫描 ``# [ALGO_FLOW]`` 到 ``# [/ALGO_FLOW]`` 块解析节点（按"层:"分组），
    再从该块及后续 ``边:`` 段解析边定义。无 ALGO_FLOW 标记返回 None
    （生成器回退文字卡片）。

    解析规则（§4.16.3）：
      1. 扫描 [ALGO_FLOW] 块 → 解析节点（按"层:"分组，YAML 风格字段）
      2. 解析"边:"部分（src -.->|断点| dst 或 src --> dst）
      3. 无标记返回 None

    :param docstring: module docstring 文本
    :return: AlgoFlowData 或 None（无标记/无节点）
    """
    if not docstring or _ALGO_FLOW_START not in docstring:
        return None

    start_idx = docstring.index(_ALGO_FLOW_START)
    block_start = start_idx + len(_ALGO_FLOW_START)
    if _ALGO_FLOW_END in docstring[block_start:]:
        block_end = docstring.index(_ALGO_FLOW_END, block_start)
    else:
        block_end = len(docstring)
    node_block = docstring[block_start:block_end]

    nodes = _parse_algo_flow_nodes(node_block)
    if not nodes:
        return None

    # 边可定义在 ALGO_FLOW 块内或块后的"边:"段——从 [ALGO_FLOW] 起扫描到 docstring 末尾
    scan_region = docstring[start_idx:]
    edges = _parse_algo_flow_edges(scan_region)

    return AlgoFlowData(nodes=nodes, edges=edges)


def _parse_algo_flow_nodes(block: str) -> list[AlgoFlowNode]:
    """解析 ALGO_FLOW 块内的节点定义（按"层:"分组，YAML 风格）。

    每行去掉 ``# `` 前缀后按 ``层: <name>`` 切换当前层、``- id: <id>`` 起新节点、
    ``key: value`` 填字段。
    """
    nodes: list[AlgoFlowNode] = []
    current_layer = ""
    current: AlgoFlowNode | None = None

    for raw in block.splitlines():
        line = raw.strip()
        if not line:
            continue
        # 去掉 "# " 前缀（块内每行以 # 开头）
        content = line[1:].lstrip() if line.startswith("#") else line

        # 层切换：层: <name>
        m_layer = re.match(r"^层\s*:\s*(.+)$", content)
        if m_layer:
            if current is not None:
                nodes.append(current)
            current_layer = m_layer.group(1).strip()
            current = None
            continue

        # 节点起点：- id: <id>
        m_id = re.match(r"^-\s+id\s*:\s*(.+)$", content)
        if m_id:
            if current is not None:
                nodes.append(current)
            current = AlgoFlowNode(id=m_id.group(1).strip(), layer=current_layer)
            continue

        # 字段：key: value
        m_field = _ALGO_FIELD_RE.match(content)
        if m_field and current is not None:
            key = m_field.group(1)
            value = m_field.group(2).strip()
            attr = _ALGO_NODE_FIELD_MAP.get(key)
            if attr is None:
                continue
            if attr == "is_break":
                setattr(current, attr, value.lower() in ("true", "yes", "1"))
            else:
                setattr(current, attr, value)
            continue

    if current is not None:
        nodes.append(current)
    return nodes


def _parse_algo_flow_edges(scan_region: str) -> list[AlgoFlowEdge]:
    """解析边定义行（``# SRC -.->|断点| DST`` 或 ``# SRC --> DST``）。

    断点边判定：箭头为 ``-.->`` 或边标签含"断点"。
    """
    edges: list[AlgoFlowEdge] = []
    for raw in scan_region.splitlines():
        m = _ALGO_EDGE_RE.match(raw.rstrip())
        if not m:
            continue
        src, arrow, label, dst = m.group(1), m.group(2), (m.group(3) or ""), m.group(4)
        is_break = arrow == "-.->" or "断点" in label
        edges.append(AlgoFlowEdge(src=src, dst=dst, is_break=is_break))
    return edges
