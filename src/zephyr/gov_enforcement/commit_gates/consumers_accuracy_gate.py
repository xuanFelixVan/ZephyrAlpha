# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §ARCH-CONSUMERS-ACCURACY-001
# [MODULE] zephyr.gov_enforcement.commit_gates.consumers_accuracy_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers (_get_staged_py_files, _read_staged_file, _collect_function_names); zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] warn-only——检测 staged .py 文件的 [CONSUMERS] 字段准确性（#ARCH-CONSUMERS-ACCURACY-001 治本）；三类违规：orphan（括号内函数名在当前文件不存在，AST 精确检测）+ phantom（消费者模块路径在项目内不存在，文件系统查找）+ stale（消费者模块存在但不 import 当前模块，baseline-scan 专用 git grep，commit-time 不检测避免性能损耗）；命中返回 passed=True + warning detail（不阻断）；tests/ 豁免；抽象代号（MOD-XXX/SH-XXX）豁免（无法静态验证）；含中文括号内容跳过（描述性文字非函数名）；noqa: consumers-accuracy 行级逃生；git diff 不可达 fail-open
# [MODIFY-GUARD] gate_id="CONSUMERS-ACCURACY"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 异常降级为 fail-open（passed=True）；ast.parse 失败 fail-open；检出违规则 warn-only（passed=True + detail）
# [TESTS] tests/governance/commit_gates/test_consumers_accuracy_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""consumers_accuracy_gate.py — CONSUMERS 字段准确性 warn-only 门禁（CONSUMERS-ACCURACY）

#ARCH-CONSUMERS-ACCURACY-001 治本（2026-07-21 立项，P3低→P2中升级）：

病根（第一性原理）
-----------------
[CONSUMERS] 头部字段是"反向依赖索引"——记录"哪些模块依赖此文件"。它的真源是
"实际 import 关系"（depgraph 已有此数据），CONSUMERS 只是这个真源的人类可读
派生形式。

根本问题：派生数据被当作声明数据对待——让 AI 手工维护。AI 手工维护派生数据
= 漂移温床（抽样 40% 不一致率实证，推算全项目 150-200 个文件有错误）。

100% AI 开发的特殊致命性：
- AI 上下文有限 → CONSUMERS 是 AI 评估修改影响的关键入口
- AI 看到 CONSUMERS 就会信任它（即使不准）
- AI 修改文件后不会自动同步 CONSUMERS
- 247 个错误 CONSUMERS = 247 个 AI 决策污染源 = 系统性幻觉温床

规则真源已隐含承认：
- trae_009/012 §跨文件影响检查 设计为"读 CONSUMERS" + "Grep 所有引用"并列两步
- 规则制定者已预期 CONSUMERS 不可信，但用君子协定（AI 自觉 Grep 兜底）而非
  门禁强制弥补
- 40% 不一致率证明君子协定失败

治本方案
--------
在 GitCommitGateway pre-commit 阶段注册门禁（priority=116，紧接
RELATIVE-PATH-LITERAL=115 之后）：
  1. 对每个 staged .py 文件，读取 [CONSUMERS] 字段内容
  2. 解析消费者声明（支持 4 种格式：简单模块路径/模块+函数名/抽象代号/方法级）
  3. 三类违规检测：
     (a) orphan（轻）：括号内声明的函数名在当前文件中不存在（AST 精确检测）
     (b) phantom（重）：声明的消费者模块路径在项目内不存在（文件系统查找）
     (c) stale（中）：消费者模块存在但不 import 当前模块（baseline-scan 专用，
         commit-time 不检测避免性能损耗）
  4. warn-only（passed=True + detail 不阻断）

设计权衡
--------
1. **warn-only（P1）**：当前 warn-only 不阻断 commit，先建立检测能力 + 数据收集。
   历史漂移（247 个文件）一次性爆会瘫痪 commit 流程。P2 升级为 block（待历史
   漂移治理完成后）。
2. **commit-time 只检测 orphan + phantom**：stale 检测需要 git grep 反向查找，
   性能差（N × 500ms），commit-time 不检测。stale 留给 baseline-scan 脚本。
3. **抽象代号豁免**：MOD-XXX/SH-XXX 格式无法静态验证（需 capability registry
   映射），跳过避免假阳性。
4. **含中文括号内容跳过**：括号内含中文等非 ASCII 字符 → 视为描述性文字非
   函数名，跳过整个括号（宁可漏报不可误报）。
5. **fail-open 原则**：git 失败 / ast 解析失败时不阻断 commit（与其他 gate 一致）。
6. **priority=116**：原 113 被 DEPGRAPH-PRE-REGISTRATION 占用，后到者让位至 116
   （priority 冲突实证：109=RULING-COMMIT-VERIFIED, 110=CAPABILITY-LOOKUP-REQUIRED,
   111=GATE-PRECOMMIT-OFFLINE, 112=FOLDER-CAPACITY-HARD-LIMIT 已占用）。
7. **noqa 行级逃生**：`# noqa: consumers-accuracy  <reason>` 标记当前文件豁免
   （对标 bare-subprocess 模式）。

Usage::

    from zephyr.gov_enforcement.commit_gates.consumers_accuracy_gate import (
        make_consumers_accuracy_gate,
    )
    registry.register(make_consumers_accuracy_gate())
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _collect_function_names,
    _get_staged_py_files,
    _matches_any_prefix,
    _module_to_file_candidates,
    _read_staged_file,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = [
    "make_consumers_accuracy_gate",
    "parse_consumers_field",
    "check_consumers_accuracy",
    "scan_all_for_consumers_accuracy",
]

# 扫描范围：与 IMPORT-INTEGRITY / BARE-SUBPROCESS 对齐
_SCAN_PREFIXES: tuple[str, ...] = ("scripts/governance/", "src/")

# [CONSUMERS] 字段正则：匹配 `# [CONSUMERS] <content>` 行（允许前导空格）
_CONSUMERS_RE = re.compile(r"^\s*#\s*\[CONSUMERS\]\s*(.*)$")

# 抽象代号前缀（无法静态验证，豁免）
_ABSTRACT_CODE_PREFIXES: tuple[str, ...] = ("MOD-", "SH-", "CFG-", "REG-", "OPS-")

# 标识符正则（用于从括号内提取函数名）
_IDENTIFIER_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

# 中文字符检测（含中文则跳过括号内容）
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")

# noqa 行级逃生：`# noqa: consumers-accuracy  <reason>`（对标 bare-subprocess 模式）
_CONSUMERS_ACCURACY_NOQA_RE = re.compile(
    r"#\s*noqa:\s*consumers-accuracy",
)


# _is_abstract_code 已提取至 _diff_helpers._matches_any_prefix（#ARCH-FORCE-MERGE-DEDUP-001 消除克隆）
# 调用处使用 _matches_any_prefix(consumer, _ABSTRACT_CODE_PREFIXES)


def _has_cjk(text: str) -> bool:
    """检测文本是否含 CJK 字符（含中文则视为描述性文字，跳过括号内容）。"""
    return bool(_CJK_RE.search(text))


# === #ARCH-CONSUMERS-ACCURACY-004 治本（2026-07-22）===
# [CONSUMERS] 字段真源允许 4 种格式，phantom 检测 MUST 按格式分类处理：
#   - "dotted"      : dotted 模块路径（a.b.c）→ 候选文件 + 逐级缩短
#   - "filepath"    : slash 文件路径（scripts/git_commit.py）→ 直接存在性检查
#   - "glob"        : glob 模式（scripts/governance/*）→ 豁免（无法静态验证）
#   - "descriptive" : 描述性文字（含空格/CJK/括号开头）→ 豁免（非路径声明）
# 病根：原算法假设输入全是 dotted 格式，对 filepath/glob/descriptive 格式产生
# 系统性误报（如 scripts/git_commit.py 文件实际存在但被误报 phantom）。
_FILE_EXTENSIONS = (
    ".py",
    ".yaml",
    ".json",
    ".yml",
    ".ps1",
    ".sh",
    ".bat",
    ".cmd",
    ".toml",
    ".cfg",
    ".ini",
    ".md",
    ".txt",
    ".csv",
    ".sql",
)


def _classify_consumer_format(consumer: str) -> str:
    """识别 consumer 声明的格式类型（#ARCH-CONSUMERS-ACCURACY-004 治本）。

    Args:
        consumer: [CONSUMERS] 字段中单个消费者声明（括号前部分）

    Returns:
        "dotted" | "filepath" | "glob" | "descriptive"
    """
    # glob 模式（含 * 或 ?）
    if "*" in consumer or "?" in consumer:
        return "glob"
    # 描述性文字（含 CJK、含空格、以括号开头）
    if _has_cjk(consumer) or " " in consumer or consumer.startswith("("):
        return "descriptive"
    # 文件路径格式（含 / 或以文件扩展名结尾）
    if "/" in consumer or consumer.endswith(_FILE_EXTENSIONS):
        # 含 / 但最后一段无文件扩展名 → 描述性引用（如 CI/CD, mcp/server）
        if "/" in consumer and not consumer.endswith(_FILE_EXTENSIONS):
            last_seg = consumer.rstrip("/").rsplit("/", 1)[-1]
            if "." not in last_seg and not consumer.endswith("/"):
                return "descriptive"
        return "filepath"
    # 单词描述性标签（不含 . 的非抽象代号单词——不是模块路径）
    if "." not in consumer:
        return "descriptive"
    # Class.method 引用（首段大写开头——PEP 8 类名，非模块路径）
    if consumer[0].isupper():
        return "descriptive"
    # dotted 路径中有连字符段 → 描述性（Python 模块名不能含连字符）
    parts = consumer.split(".")
    if any("-" in p for p in parts):
        return "descriptive"
    # dotted 模块路径（含 .，首段小写，各段无连字符）
    return "dotted"


def _check_filepath_exists(filepath: str, project_root: Path) -> bool:
    """检查文件路径声明是否存在（phantom 检测——filepath 格式）。

    支持相对路径（scripts/git_commit.py）和 src/ 前缀路径。
    文件名-only 路径（无目录前缀）递归搜索项目内同名文件。
    """
    import glob as _glob

    filepath = filepath.strip()
    # 直接检查相对路径
    if (project_root / filepath).exists():
        return True
    # 尝试去除 src/ 前缀（如 src/zephyr/foo.py → zephyr/foo.py）
    if filepath.startswith("src/") and (project_root / filepath[4:]).exists():
        return True
    # 文件名-only 路径递归搜索（如 phase_manager.py 实际在 scripts/governance/d5_architecture/ 下）
    if "/" not in filepath:
        for prefix in ("scripts/governance/", "scripts/", "src/zephyr/", "src/"):
            if (project_root / prefix / filepath).exists():
                return True
        # 递归搜索作为兜底（短路径在深层子目录中）
        matches = _glob.glob(str(project_root / "scripts" / "**" / filepath), recursive=True)
        if not matches:
            matches = _glob.glob(str(project_root / "src" / "**" / filepath), recursive=True)
        if matches:
            return True
    return False


# _module_to_file_candidates 已提取至 _diff_helpers（#ARCH-FORCE-MERGE-DEDUP-001 消除克隆）
# 调用处直接使用 _module_to_file_candidates(module_path)


def _check_module_path_exists(module_path: str, project_root: Path) -> bool:
    """检查模块路径在项目内是否存在（phantom 检测）。

    Args:
        module_path: 模块路径（如 zephyr.gov_enforcement.commit_gates.create_guard）
        project_root: 项目根目录

    Returns:
        True 如果模块文件存在，False 不存在（phantom 违规）。
    """
    candidates = _module_to_file_candidates(module_path)
    for candidate in candidates:
        full_path = project_root / candidate
        if full_path.exists():
            return True
    return False


def _extract_function_names_from_parens(parens_content: str) -> list[str]:
    """从括号内容提取函数名（标识符）。

    策略：
    - 含 CJK 字符 → 跳过整个括号（描述性文字非函数名）
    - 按逗号/分号分割，每段必须是纯标识符——任何段含非标识符字符
      （空格、+、-等）→ 整个括号视为描述性文字，返回空列表

    Args:
        parens_content: 括号内内容（如 "find_breaking_change_session, register_dependency"）

    Returns:
        函数名列表（如 ["find_breaking_change_session", "register_dependency"]）。
        含 CJK 或描述性文字时返回空列表。
    """
    if _has_cjk(parens_content):
        return []  # 描述性文字，跳过
    # 按逗号/分号分割（不再按空格分割——描述性英文短语会被误提取）
    tokens = re.split(r"[,;]", parens_content.strip())
    result: list[str] = []
    for token in tokens:
        token = token.strip()
        if not token:
            continue
        # 每个 token 必须是纯标识符（无空格、无特殊字符）
        if not _IDENTIFIER_RE.match(token):
            return []  # 有非标识符 token → 描述性文字，跳过整个括号
        result.append(token)
    return result


def parse_consumers_field(file_content: str) -> list[tuple[str, str]]:
    """解析 [CONSUMERS] 字段内容，返回 (consumer_decl, parens_content) 列表。

    支持格式：
    1. `module1; module2` — 简单模块路径（parens_content=""）
    2. `module1 (func1, func2); module2 (func3)` — 模块+函数名
    3. `MOD-INF-027(audit-orchestrator)` — 抽象代号（parens_content="audit-orchestrator"）
    4. `module1.Class.method` — 方法级（取到模块级）

    Args:
        file_content: 文件内容

    Returns:
        [(consumer_decl, parens_content), ...] 列表。
        consumer_decl 是括号前的模块路径/代号，parens_content 是括号内内容（无括号则空）。
        未找到 [CONSUMERS] 字段时返回空列表。
    """
    # 只读前 30 行（与 CREATE-GUARD _check_field_header 对齐）
    for line in file_content.splitlines()[:30]:
        m = _CONSUMERS_RE.match(line)
        if m:
            content = m.group(1).strip()
            if not content:
                return []
            # 按 `;` 分割消费者声明
            declarations = [d.strip() for d in content.split(";") if d.strip()]
            result: list[tuple[str, str]] = []
            for decl in declarations:
                # 提取括号内容（如果有）
                paren_match = re.match(r"^([^(]+)\s*\(([^)]*)\)\s*$", decl)
                if paren_match:
                    consumer = paren_match.group(1).strip()
                    parens = paren_match.group(2).strip()
                    result.append((consumer, parens))
                else:
                    result.append((decl, ""))
            return result
    return []


def check_consumers_accuracy(
    py_file: str,
    file_content: str,
    project_root: Path,
    noqa_files: set[str] | None = None,
) -> list[str]:
    """检查单个文件的 [CONSUMERS] 字段准确性，返回违规消息列表（空=通过）。

    检测三类违规：
    - orphan（轻）：括号内声明的函数名在当前文件中不存在
    - phantom（重）：声明的消费者模块路径在项目内不存在

    stale 检测（消费者模块存在但不 import 当前模块）需要 git grep，commit-time
    不检测，留给 baseline-scan 脚本。

    Args:
        py_file: 文件相对路径（用于诊断消息）
        file_content: 文件内容
        project_root: 项目根目录
        noqa_files: noqa 豁免文件集合（可选）

    Returns:
        违规消息列表（空=通过）。
    """
    if noqa_files and py_file in noqa_files:
        return []

    declarations = parse_consumers_field(file_content)
    if not declarations:
        return []  # 无 [CONSUMERS] 字段或为空，由 CREATE-GUARD 检测存在性

    # 收集当前文件的所有函数名+类名（用于 orphan 检测）
    try:
        defined_functions = _collect_function_names(file_content)
        # 也收集类名（orphan 检测应识别 ClassDef）
        import ast

        tree = ast.parse(file_content)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                defined_functions.add(node.name)
    except Exception:  # noqa: BLE001 — fail-open
        defined_functions = set()

    violations: list[str] = []
    for consumer, parens in declarations:
        # 跳过抽象代号（MOD-XXX/SH-XXX 等，无法静态验证）
        if _matches_any_prefix(consumer, _ABSTRACT_CODE_PREFIXES):
            continue

        # #ARCH-CONSUMERS-ACCURACY-004 治本：按格式分类处理 phantom 检测
        fmt = _classify_consumer_format(consumer)

        # glob / 描述性文字：豁免（无法静态验证）
        if fmt in ("glob", "descriptive"):
            continue

        # 文件路径格式：直接存在性检查
        if fmt == "filepath":
            if not _check_filepath_exists(consumer, project_root):
                violations.append(f"  {py_file}: phantom consumer '{consumer}' (文件路径在项目内不存在)")
                continue  # phantom 违规，不再检测 orphan
            # 文件存在，继续 orphan 检测
        else:
            # dotted 模块路径：现有逻辑（候选文件 + 逐级缩短）
            # 处理方法级声明：module.Class.method → 取到模块级
            # 策略：从右往左尝试，去掉最后一段直到找到存在的文件
            module_path = consumer
            path_exists = _check_module_path_exists(module_path, project_root)
            if not path_exists and "-" in module_path:
                underscored = module_path.replace("-", "_")
                if _check_module_path_exists(underscored, project_root):
                    path_exists = True
            if not path_exists:
                # 逐级缩短尝试（处理 module.Class.method 格式）
                # 关键约束：至少保留 2 段——避免缩短到顶层包（如 zephyr）导致误判，
                # 因为顶层包 __init__.py 总是存在（src/zephyr/__init__.py），
                # 会使 zephyr.nonexistent.module 误判为"存在"。
                parts = module_path.split(".")
                found = False
                for i in range(len(parts) - 1, 1, -1):
                    shortened = ".".join(parts[:i])
                    if _check_module_path_exists(shortened, project_root):
                        found = True
                        break
                if not found:
                    violations.append(f"  {py_file}: phantom consumer '{consumer}' (模块路径在项目内不存在)")
                    continue  # phantom 违规，不再检测 orphan（模块都不存在）

        # orphan 检测：括号内声明的函数名在当前文件中不存在
        if parens:
            func_names = _extract_function_names_from_parens(parens)
            for func_name in func_names:
                if func_name not in defined_functions:
                    violations.append(
                        f"  {py_file}: orphan function '{func_name}' "
                        f"声明在 [CONSUMERS] 括号内但不在当前文件中定义 "
                        f"(consumer={consumer})"
                    )

    return violations


def _extract_noqa_files(gateway, py_files: list[str]) -> set[str]:
    """提取带 `# noqa: consumers-accuracy` 标记的文件集合（文件级豁免）。

    策略：读取每个 staged 文件内容，检查是否含 noqa 标记。
    """
    noqa_files: set[str] = set()
    for py_file in py_files:
        content = _read_staged_file(gateway, py_file)
        if content and _CONSUMERS_ACCURACY_NOQA_RE.search(content):
            noqa_files.add(py_file)
    return noqa_files


def make_consumers_accuracy_gate() -> GateSpec:
    """构造 CONSUMERS-ACCURACY pre-commit warn-only 门禁（priority=116）。

    检测 staged scripts/governance/** + src/**.py 的 [CONSUMERS] 字段准确性，
    warn-only（passed=True + detail 不阻断）。

    #ARCH-CONSUMERS-ACCURACY-001 治本（2026-07-21）：
    防止 AI 手工维护 [CONSUMERS] 字段时的漂移——函数名拼写错/已删除函数仍标注/
    消费者模块路径错。

    Returns:
        GateSpec(gate_id="CONSUMERS-ACCURACY", priority=116)。
        warn-only：检出违规返回 (True, warning_detail)，不阻断 commit。
    """

    def _check(gateway, _files: list[str], **_kwargs) -> tuple[bool, str]:
        py_files = [f for f in _get_staged_py_files(gateway, "CONSUMERS-ACCURACY") if not is_test_exempt(f)]
        if not py_files:
            return True, ""

        # 提取 noqa 文件级豁免
        try:
            noqa_files = _extract_noqa_files(gateway, py_files)
        except Exception:  # noqa: BLE001 — fail-open
            noqa_files = set()

        # 获取项目根目录
        project_root = getattr(gateway, "project_root", None)
        if project_root is None:
            logger.warning("CONSUMERS-ACCURACY: gateway.project_root 不可达，fail-open 放行")
            return True, ""
        project_root = Path(project_root)

        warnings: list[str] = []
        for py_file in py_files:
            if not py_file.startswith(_SCAN_PREFIXES):
                continue
            content = _read_staged_file(gateway, py_file)
            if not content:
                continue  # fail-open: 文件不可读

            try:
                file_warnings = check_consumers_accuracy(py_file, content, project_root, noqa_files)
                warnings.extend(file_warnings)
            except Exception as e:  # noqa: BLE001 — fail-open
                logger.debug(
                    "CONSUMERS-ACCURACY: check_consumers_accuracy fail-open %s: %s",
                    py_file,
                    e,
                )
                continue

        if warnings:
            detail = (
                "CONSUMERS-ACCURACY (warn-only)：[CONSUMERS] 字段准确性问题"
                "（#ARCH-CONSUMERS-ACCURACY-001 治本）\n"
                "  病根：[CONSUMERS] 是派生数据（真源=实际 import 关系），"
                "但被当作声明数据让 AI 手工维护——漂移温床（抽样 40% 不一致）。\n"
                "  影响：AI 修改文件前读 [CONSUMERS] 评估影响范围，不准的 CONSUMERS"
                " = AI 决策污染源 = 系统性幻觉温床。\n"
                "  修复：①核实声明的消费者模块路径是否正确；\n"
                "        ②核实括号内函数名是否在当前文件中定义；\n"
                "        ③若消费者模块不存在，删除该声明；\n"
                "        ④若为抽象代号（MOD-XXX），保留（豁免检测）。\n"
                + "\n".join(warnings[:50])
                + (f"\n  ...(+{len(warnings) - 50} more)" if len(warnings) > 50 else "")
                + "\n-> 逃生通道：文件内加 `# noqa: consumers-accuracy` 标记（整文件豁免）"
            )
            logger.warning("CONSUMERS-ACCURACY gate warn:\n%s", detail)
            return True, detail  # warn-only：passed=True 不阻断
        return True, ""

    return GateSpec(
        gate_id="CONSUMERS-ACCURACY",
        check=_check,
        priority=116,
    )


# ============================================================================
# scan_all_for_consumers_accuracy — 全仓 baseline 扫描（post-commit reconciler 用）
# 对标 undefined_name_gate.scan_all_for_undefined_names（DRY，零新真源）
# ============================================================================
def scan_all_for_consumers_accuracy(
    project_root: Path,
) -> tuple[list[str], str | None]:
    """全仓 baseline 扫描 scripts/governance/** + src/**.py 的 [CONSUMERS] 字段准确性。

    与 make_consumers_accuracy_gate（pre-commit warn-only）的区别：
    gate 扫 staged 文件；本函数扫全仓磁盘文件，供 post-commit reconciler
    baseline 全扫（warn 级）。与 gate 共享 check_consumers_accuracy（DRY）。

    不检测 stale（git grep 反向查找性能差 N×500ms，post-commit 不适合全扫）。
    stale 留给手动 scan_consumers_accuracy.py 脚本。

    Returns:
        (violations, error_msg)：error_msg 非 None 表示 fail-open（目录不存在），
        调用方应降级为 ReconcileResult(action="skip")。
    """
    import glob

    root = Path(str(project_root))
    gov_dir = root / "scripts" / "governance"
    src_dir = root / "src"
    if not gov_dir.exists() and not src_dir.exists():
        return [], "scripts/governance/ 与 src/ 均不存在"

    violations: list[str] = []
    for base, prefix in ((gov_dir, "scripts/governance/"), (src_dir, "src/")):
        if not base.exists():
            continue
        for py_file_path in glob.glob(str(base / "**" / "*.py"), recursive=True):
            # 排除 _archive 目录（归档代码不参与扫描）
            if "_archive" in py_file_path:
                continue
            rel = py_file_path.replace("\\", "/")
            idx = rel.find(prefix)
            if idx < 0:
                continue
            py_file = rel[idx:]
            # 排除 tests/ 文件（SSoT: is_test_exempt 路径段匹配，覆盖嵌套 tests/ 目录）
            if is_test_exempt(py_file):
                continue
            try:
                with open(py_file_path, encoding="utf-8", errors="replace") as fh:
                    content = fh.read()
            except OSError:
                continue  # fail-open: 文件不可读
            # noqa 豁免：baseline scan 也识别 consumers-accuracy 行级豁免标记
            if _CONSUMERS_ACCURACY_NOQA_RE.search(content):
                continue
            violations.extend(check_consumers_accuracy(py_file, content, root))

    return violations, None
