# [BLUEPRINT] MOD-GOV-VOCAB-GATE | docs/_working/daily_loop_campaign/03_self_ruling_vocab_ssot.md | §state_vocab_registry
# [MODULE] zephyr.gov_enforcement.commit_gates.library.state_vocab_registry_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt); zephyr.gov_enforcement.commit_gates._diff_helpers (_get_staged_py_files, _build_own_scope, _norm_rel, _audit_foreign_staged, _make_noqa_pattern, _extract_noqa_lines)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.gate_auto_registrar（in_process_gate_registry.yaml 条目驱动）
# [STARTUP] imported by gate_auto_registrar
# [MATURITY] evolving
# [INVARIANTS] 观察期 warn-only（STATE_VOCAB_GATE_MODE="warn"，Owner 批"词表 SSOT 制度"W3 执行门；未来 config 翻转 "block" 硬阻断）——staged 新增/修改 .py 中"新定义的状态枚举类"未在 state_vocabulary_registry.yaml 登记则 WARN+审计留痕+return 放行，不阻断 commit；启发式（类名关键词+全大写成员计数）必有误报→白名单豁免制（类体任一行行注释 noqa 标记（STATE-VOCAB-REGISTRY） <原因> 豁免，或登记进注册表）；own-scope（宪法 §3.3）：扫描集=staged∩本 session 范围（_build_own_scope），外来 staged 剔除不阻断、warn+_audit_foreign_staged 审计；AST 解析失败/文件读取失败 fail-open（logger.warning）；注册表 yaml 缺失/损坏 fail-open 跳过（缺失=debug 日志，不报错——配套注册表由并行会话施工）；净零声明=替代人工维护"状态词表↔注册表"映射（#ARCH-310 R4）
# [MODIFY-GUARD] gate_id="STATE-VOCAB-REGISTRY"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——AST/IO/yaml 异常降级为 fail-open（passed=True，logger.warning/debug）；warn 模式检出违规返回 passed=True+detail（留痕不阻断）；"block" 模式检出违规才 fail-closed（passed=False）
# [TESTS] tests/gov_enforcement/test_state_vocab_registry_gate.py
# [A_module] module_id=MOD-GOV-VOCAB-GATE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
state_vocab_registry_gate.py — 状态词表 SSOT 登记观察门（STATE-VOCAB-REGISTRY）

扫描 staged 新增/修改 .py 中"新定义的状态枚举类"，类名未登记进
``docs/01_policies_and_standards/_registry/catalogs/state_vocabulary_registry.yaml``
则 WARN+审计留痕+放行（观察期 warn-only）。词表 SSOT 制度 W3 执行门
（真源：docs/_working/daily_loop_campaign/03_self_ruling_vocab_ssot.md）。

病根（第一性原理）
-----------------
状态词表（交易状态/阶段/市况/情绪/模式枚举）散落各模块自造自用：
  1. 同一语义多套拼写（OPENED/OPEN/FILLED）跨模块对不齐
  2. 新增状态无人知道要同步下游映射/仪表盘/对账
  3. 词表真源缺位，SSOT 制度无从谈起
制度要求：凡定义状态词表类必须在 state_vocabulary_registry.yaml 登记，
使"词表有什么"可机读、可对账、可检索。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册观察门，AST 分析
staged .py 文件：
  1. 识别状态词表类：类名含 state/phase/regime/emotion/mode（不区分大小写）
     且类体含 ≥3 个值为全大写字符串字面量的赋值
  2. 查登记：类名（或模块路径）出现在 state_vocabulary_registry.yaml
     （yaml.safe_load 后递归收集字符串）即视为已登记
  3. 未登记 → collect 告警；warn 模式=审计落盘+logger.warning+放行

设计权衡
--------
1. **warn-only 起步**：启发式必有误报，观察期收集误报率，STATE_VOCAB_GATE_MODE
   翻 "block" 一行升硬阻断（同 FRONTEND-TRUTH-SOURCE 的 _HARD_BLOCK 先例）。
2. **白名单豁免制**：误报类在类体任一行加 ``# noqa 标记（STATE-VOCAB-REGISTRY） <原因>``
   豁免；真状态词表类应登记进注册表（登记本身即白名单）。
3. **注册表缺失 fail-open**：配套注册表由并行会话施工，可能尚不存在——缺失时
   debug 日志跳过，绝不报错（观察门不得比制度先行阻断）。
4. **own-scope**：宪法 §3.3 内容扫描型 gate 默认 own-diff 作用域，外来 staged
   剔除不阻断、warn+审计。
5. **priority=135**：FRONTEND-TRUTH-SOURCE(136) 之前，132 之后唯一空档。

Usage::

    from zephyr.gov_enforcement.commit_gates.state_vocab_registry_gate import (
        make_state_vocab_registry_gate,
    )

    registry.register(make_state_vocab_registry_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/l/state_vocab_registry_gate.yaml
"""

from __future__ import annotations

import ast
import json
import logging
import os
from pathlib import Path
from typing import Any, Final

import yaml

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _audit_foreign_staged,
    _build_own_scope,
    _extract_noqa_lines,
    _get_staged_py_files,
    _make_noqa_pattern,
    _norm_rel,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__: Final[list[str]] = ["make_state_vocab_registry_gate", "STATE_VOCAB_GATE_MODE", "STATE_VOCAB_REGISTRY_REL_PATH"]

# 模式常量（模块级）：warn=观察期（审计留痕+放行）；block=硬阻断（未来 config 翻转）
STATE_VOCAB_GATE_MODE = "warn"

# 状态词表注册表相对路径（配套注册表由并行会话施工，可能暂缺——缺失 fail-open）
STATE_VOCAB_REGISTRY_REL_PATH = "docs/01_policies_and_standards/_registry/catalogs/state_vocabulary_registry.yaml"

# 状态词表类名关键词（case-insensitive 子串匹配）
_STATE_NAME_KEYWORDS = ("state", "phase", "regime", "emotion", "mode")

# 状态词表类判定门槛：类体 ≥3 个全大写字符串字面量赋值
_MIN_UPPER_ASSIGNMENTS = 3

_GATE_ID = "STATE-VOCAB-REGISTRY"


def _is_upper_string_literal(value: ast.expr) -> bool:
    """表达式是否是全大写字符串字面量（枚举成员值的典型形态）。"""
    if not isinstance(value, ast.Constant) or not isinstance(value.value, str):
        return False
    return bool(value.value) and value.value.isupper()


def _count_upper_assignments(cls: ast.ClassDef) -> int:
    """统计类体（直接 body，不含嵌套函数/内类）中全大写字符串赋值个数。"""
    count = 0
    for stmt in cls.body:
        if (isinstance(stmt, ast.Assign) and _is_upper_string_literal(stmt.value)) or (
            isinstance(stmt, ast.AnnAssign) and stmt.value is not None and _is_upper_string_literal(stmt.value)
        ):
            count += 1
    return count


def _is_state_vocab_class(cls: ast.ClassDef) -> bool:
    """判定是否为"状态词表类"：类名含关键词 且 类体 ≥3 个全大写字符串赋值。"""
    name_lower = cls.name.lower()
    if not any(kw in name_lower for kw in _STATE_NAME_KEYWORDS):
        return False
    return _count_upper_assignments(cls) >= _MIN_UPPER_ASSIGNMENTS


def _collect_registry_strings(node: object, out: set[str]) -> None:
    """递归收集 yaml 结构中的全部字符串（dict 键+值 / list 元素 / 标量）。"""
    if isinstance(node, str):
        out.add(node)
    elif isinstance(node, dict):
        for k, v in node.items():
            _collect_registry_strings(k, out)
            _collect_registry_strings(v, out)
    elif isinstance(node, (list, tuple, set)):
        for item in node:
            _collect_registry_strings(item, out)


def _load_registered_strings(project_root: str) -> set[str] | None:
    """加载注册表并递归收集全部字符串。

    Returns:
        字符串集合；注册表缺失（fail-open，debug 日志）或损坏（fail-open，
        warning 日志）时返回 None——调用方跳过登记检查，绝不报错。
    """
    registry_path = Path(project_root) / STATE_VOCAB_REGISTRY_REL_PATH
    if not registry_path.exists():
        logger.debug(
            "%s: 状态词表注册表不存在（%s）——配套注册表未落地，fail-open 跳过登记检查。",
            _GATE_ID,
            STATE_VOCAB_REGISTRY_REL_PATH,
        )
        return None
    try:
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001 — 注册表损坏 fail-open（观察门不阻断）
        logger.warning("%s: 注册表解析失败（%s: %s）——fail-open 跳过登记检查。", _GATE_ID, type(e).__name__, e)
        return None
    strings: set[str] = set()
    _collect_registry_strings(data, strings)
    return strings


def _module_identifiers(rel_path: str) -> list[str]:
    """派生模块路径标识（posix 相对路径 / 点分模块名 / src 剥壳路径）。"""
    posix = rel_path.replace("\\", "/")
    dotted = posix[:-3].replace("/", ".") if posix.endswith(".py") else posix.replace("/", ".")
    stripped = dotted[len("src.") :] if dotted.startswith("src.") else dotted
    return [posix, dotted, stripped]


def _is_registered(cls_name: str, rel_path: str, registered: set[str]) -> bool:
    """类名（或模块路径标识）是否出现在注册表字符串集合中。

    类名匹配含点分后缀形态：注册表以 ``target: <module>.<Class>``（canonical_mapping）
    登记官方词表类时，``zephyr.shared.vocab.market_state.MacroRegime`` 经后缀匹配
    判 MacroRegime 已登记。
    """
    if cls_name in registered or any(s.endswith("." + cls_name) for s in registered):
        return True
    return any(ident in registered for ident in _module_identifiers(rel_path))


def _class_has_noqa(cls: ast.ClassDef, noqa_lines: set[int]) -> bool:
    """类体行范围内任一行带 ``# noqa 标记（STATE-VOCAB-REGISTRY） <原因>`` 即豁免。"""
    end = getattr(cls, "end_lineno", cls.lineno)
    return any(cls.lineno <= ln <= end for ln in noqa_lines)


def _audit_findings(gateway, findings: dict[str, list[str]]) -> None:
    """审计落盘（non-blocking）：供 Owner 回评误报率与升硬决策。"""
    try:
        from zephyr.shared.utils.time_utils import now_utc  # noqa: PLC0415

        audit_dir = Path(gateway.project_root) / ".runtime" / "gate_audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        rec = {
            "timestamp": now_utc().isoformat(),
            "gate": _GATE_ID,
            "mode": STATE_VOCAB_GATE_MODE,
            "findings": findings,
        }
        with (audit_dir / "state_vocab_registry.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001 — 审计失败不阻断（ERROR_CONTRACT）
        logger.debug("%s audit write failed (non-blocking)", _GATE_ID, exc_info=True)


def _resolve_wt_root(gateway) -> str:
    """worktree 根解析（回退 project_root，fail-open）。"""
    try:
        toplevel = gateway.run_git(["git", "rev-parse", "--show-toplevel"])
        if toplevel.returncode == 0:
            return toplevel.stdout.strip()
    except Exception:  # noqa: BLE001  回退 project_root（fail-open）
        pass
    return project_root if (project_root := getattr(gateway, "project_root", None)) else "."


def _scan_py_files_for_findings(gateway, py_files: list[str], registered) -> dict[str, list[str]]:
    """逐文件 AST 扫描：未登记状态词表类 → findings（单文件失败降级跳过）。"""
    findings: dict[str, list[str]] = {}
    wt_root = _resolve_wt_root(gateway)
    noqa_pattern = _make_noqa_pattern(_GATE_ID)
    for rel_path in py_files:
        abs_path = rel_path if os.path.isabs(rel_path) else os.path.join(wt_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            continue
        try:
            with open(abs_path, encoding="utf-8", errors="replace") as fh:
                content = fh.read()
            tree = ast.parse(content, filename=abs_path)
        except (OSError, SyntaxError) as e:
            logger.warning("%s: 跳过文件 %s (%s: %s)", _GATE_ID, abs_path, type(e).__name__, e)
            continue
        noqa_lines = _extract_noqa_lines(content, noqa_pattern)
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef) or not _is_state_vocab_class(node):
                continue
            if _class_has_noqa(node, noqa_lines):
                continue  # 白名单豁免（启发式误报逃生）
            if _is_registered(node.name, rel_path, registered):
                continue
            findings.setdefault(rel_path, []).append(f"状态词表类 {node.name} 未登记 state_vocabulary_registry.yaml")
    return findings


def make_state_vocab_registry_gate() -> GateSpec:
    """构造状态词表 SSOT 登记观察门 GateSpec（观察期 warn 型）。

    Returns:
        GateSpec(gate_id="STATE-VOCAB-REGISTRY", priority=135)。
        priority=135——FRONTEND-TRUTH-SOURCE(136) 之前的空档位。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 注册表 fail-open 前置：缺失/损坏 → 跳过（不报错）
        project_root = str(getattr(gateway, "project_root", "."))
        registered = _load_registered_strings(project_root)
        if registered is None:
            return True, ""

        # 2. staged .py（AM 态，tests/ 豁免）
        py_files = [f for f in _get_staged_py_files(gateway, _GATE_ID) if not is_test_exempt(f)]
        if not py_files:
            return True, ""

        # 3. own-scope（宪法 §3.3）：外来 staged 剔除不阻断、warn+审计
        session_id = kwargs.get("session_id")
        own_scope = _build_own_scope(gateway, files, session_id)
        if own_scope is not None:
            own_files = [f for f in py_files if _norm_rel(gateway, f) in own_scope]
            foreign_staged = [f for f in py_files if _norm_rel(gateway, f) not in own_scope]
            if foreign_staged:
                _audit_foreign_staged(gateway, session_id, foreign_staged, gate_name=_GATE_ID)
                logger.warning(
                    "%s: %d 个外来 session staged 文件未检查（warn+审计，不阻断）: %s",
                    _GATE_ID,
                    len(foreign_staged),
                    ", ".join(foreign_staged[:5]) + ("..." if len(foreign_staged) > 5 else ""),
                )
            py_files = own_files
            if not py_files:
                return True, ""

        findings = _scan_py_files_for_findings(gateway, py_files, registered)
        if not findings:
            return True, ""

        # 5. 输出姿态照先例（FRONTEND-TRUTH-SOURCE）：审计留痕 + warn/branch by mode
        _audit_findings(gateway, findings)
        detail_lines = [f"  {fp}:\n" + "\n".join(f"    - {c}" for c in cs) for fp, cs in findings.items()]
        detail = (
            "STATE-VOCAB-REGISTRY warn：状态词表类未登记 state_vocabulary_registry.yaml"
            "（词表 SSOT 制度 W3 执行门，真源 docs/_working/daily_loop_campaign/03_self_ruling_vocab_ssot.md）\n"
            + "\n".join(detail_lines)
            + "\n-> 合法情形自查：①真状态词表类→登记进注册表（登记即白名单）②启发式误报（非词表类）"
            "→类体任一行加 `# noqa 标记（STATE-VOCAB-REGISTRY） <原因>`。误报请回评 Owner（warn 起步收期误报率，稳定后升硬阻断）"
        )
        if STATE_VOCAB_GATE_MODE == "block":
            logger.error("%s gate block:\n%s", _GATE_ID, detail)
            return False, detail
        logger.warning("%s gate warn-only:\n%s", _GATE_ID, detail)
        return True, detail

    return GateSpec(gate_id=_GATE_ID, check=_check, priority=135)
