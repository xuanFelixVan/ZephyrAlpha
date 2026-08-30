# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.test_residue_ssot_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); zephyr.gov_enforcement.commit_gates.doc_ref_broken_gate (_get_worktree_root 共享); zephyr.governance.audit.reconciliation_registry (_load_test_residue_config，前缀真源 SSoT 加载器，lazy import)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__ (via gate_auto_registrar YAML 驱动自动注册)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged .py 文件中存在硬编码测试残留目录前缀集合（≥2 个 trae_071 §test_residue_reclaim.covered_patterns.dir_prefixes 精确匹配）时阻断 commit；检测 staged 新增+修改的 .py（--diff-filter=AM）；前缀真源 = trae_071 YAML（通过 reconciliation_registry._load_test_residue_config lazy import 加载，禁止本 gate 硬编码前缀）；config 不可达/import 失败/AST 解析失败时 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [MODIFY-GUARD] gate_id="TEST-RESIDUE-SSOT"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——import/YAML/AST/IO 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_test_residue_ssot_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# M03豁免: AI趋同演化(与blueprint_node_id_hardcode_gate.py相似结构),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测
"""
test_residue_ssot_gate.py — 测试残留前缀硬编码阻断门禁（TEST-RESIDUE-SSOT）

检测 staged .py 文件中是否硬编码测试残留目录前缀集合（重复造轮子风险）。
in-process gate，注册到 CommitGateRegistry，在 GitCommitGateway 的 check_all() 阶段执行。
--no-verify 无法绕过 in-process gate。

病根（第一性原理）
-----------------
trae_071 §test_residue_reclaim.covered_patterns.dir_prefixes 是测试残留目录前缀的
唯一真源（YAML），reconciliation_registry._load_test_residue_config() 与
scripts/ops/cleanup_runtime_tmp_residue.py 动态加载。但项目 100% AI 开发，AI 新建
脚本时可能"重复造轮子"——硬编码 ``_PREFIXES = ("pytest_", "git_guard_test_", ...)``
而不从 YAML 加载，形成多真源漂移（trae_062 SSoT 违规）。#ARCH-TEST-RESIDUE-CLEANUP-001
修复时正是此模式（已治本收敛为动态加载）。本 gate 防止未来复发（治本 #5：无门禁阻断
硬编码——原仅靠文档约定，现升级为技术强制）。

检测逻辑（AST，纯 stdlib，无 subprocess）
------------------------------------------
1. 从 trae_071 YAML 加载 dir_prefixes（真源，lazy import _load_test_residue_config）
2. 对每个 staged .py 文件（--diff-filter=AM），ast.parse 解析
3. 找 Assign/AnnAssign 节点，其 value 是 Tuple/List/Set 且元素为 str Constant
4. 若该集合中 ≥2 个字符串**精确等于**某个 dir_prefix → 判定违规（硬编码前缀集合）
   - ≥2 阈值：消除单前缀巧合（"pytest_" 单独出现可能是合法 pytest 助手代码）
   - 精确匹配：避免 startswith 误伤 pytest hook 名（pytest_sessionfinish 等）
5. config 不可达 / import 失败 / AST 语法错误 → fail-open（不阻断 commit）

设计权衡
--------
1. **≥2 精确匹配阈值**：单前缀硬编码（如 ``("pytest_",)``）不触发——"pytest_" 半常见，
   单独出现可能是合法 pytest 助手。≥2 个项目特有前缀（pytest_+git_guard_test_ 等）
   几乎必为重复造轮子。dir_prefixes 中 git_guard_test_/conc_mv_/rb1_/p4-1b-test/
   probe_test/xhs_ocr 为项目独有，任意 2 个组合零误报（已全仓库扫描验证）。
2. **仅检测 dir_prefixes**：exact_names（b1/g1/fx1/rc1）与 tmp_prefix（tmp）过于
   通用，精确匹配易误报，故不纳入检测集。dir_prefixes 足以覆盖重复造轮子主模式。
3. **lazy import 加载器**：_load_test_residue_config 从 reconciliation_registry lazy
   import（函数内），避免模块级耦合 + 复用 SSoT 单一加载器（禁止本 gate 重写 YAML 解析
   形成双源）。reconciliation_registry 的 gov_enforcement import 均为函数级 lazy，
   无循环 import 风险。
4. **fail-open 三层**：config 不可达（YAML 缺失）/ import 失败 / AST 语法错误均不阻断
   commit（环境异常非违规，语法错误由其他 gate/lint 管）。检出违规则 fail-closed。
5. **priority=56**：在 DERIVED-FILE-DELETION-PROTECTION(46)/HELD-OVERLAP(50) 之后、
   BLUEPRINT-NODE-ID-HARDCODE(57) 之前——同属 hardcode 检测族。

Usage::

    from zephyr.gov_enforcement.commit_gates.test_residue_ssot_gate import make_test_residue_ssot_gate
    registry.register(make_test_residue_ssot_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: test_residue_ssot_gate.py
# 层: 算法
# - id: A1
#   name_zh: ① make_test_residue_ssot_gate
#   name_en: make_test_residue_ssot_gate
#   intro: 构造测试残留前缀硬编码阻断门禁 GateSpec（硬阻断型）。
#   desc: 构造测试残留前缀硬编码阻断门禁 GateSpec（硬阻断型）。 Returns: GateSpec(gate_id="TEST-RESIDUE-SSOT", priority=5…；源码 L238-L294
#   inputs: 无参数
#   outputs: GateSpec
# 层: 输出
# - id: O1
#   name_zh: GateSpec
#   name_en: GateSpec
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import ast
import logging
import os
from typing import Final

# 共享 _get_worktree_root（避免 FUNCTION-DUP 重复——与 doc_ref_broken_gate.py 共用）
from zephyr.gov_enforcement.commit_gates.doc_ref_broken_gate import _get_worktree_root
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__: Final = ["make_test_residue_ssot_gate"]

# 违规判定阈值：集合中 ≥2 个 dir_prefix 精确匹配才判定为硬编码前缀集合。
# 1 个可能是巧合（pytest_ 单独出现于 pytest 助手），≥2 个项目特有前缀几乎必为重复造轮子。
_MIN_PREFIX_MATCHES_FOR_VIOLATION: Final[int] = 2


def _load_dir_prefixes() -> frozenset[str] | None:
    """从 trae_071 YAML 加载 dir_prefixes（SSoT 真源，复用 reconciliation_registry 加载器）。

    lazy import _load_test_residue_config（避免模块级耦合 + 复用单一加载器，
    禁止本 gate 重写 YAML 解析形成双源）。

    Returns:
        dir_prefixes frozenset；加载器不可达/段缺失 → None（fail-open）。
    """
    try:
        from zephyr.governance.audit.reconciliation_registry import (  # noqa: PLC0415
            _load_test_residue_config,
        )
    except ImportError as exc:
        logger.warning(
            "TEST-RESIDUE-SSOT gate fail-open: _load_test_residue_config import 失败(%s)，检测器失效。",
            exc,
        )
        return None
    cfg = _load_test_residue_config()
    if cfg is None:
        logger.warning("TEST-RESIDUE-SSOT gate fail-open: trae_071 test_residue_reclaim config 不可达，检测器失效。")
        return None
    return frozenset(cfg.get("dir_prefixes") or ())


def _get_staged_py_files(gateway) -> list[str] | None:
    """获取 staged 新增+修改的 .py 文件列表（fail-open：出错返回 None）。

    Args:
        gateway: GitCommitGateway 实例（提供 ``run_git``）。

    Returns:
        .py 相对路径列表（正斜杠归一化）；git diff 失败/异常时返回 None。
    """
    try:
        diff_result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=AM"])
        if diff_result.returncode != 0:
            logger.warning(
                "TEST-RESIDUE-SSOT gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                diff_result.returncode,
            )
            return None
        staged = diff_result.stdout.strip().splitlines()
    except Exception as e:  # noqa: BLE001 — fail-open: broad exception catch
        logger.warning(
            "TEST-RESIDUE-SSOT gate fail-open: git diff 异常(%s: %s)，检测器失效。",
            type(e).__name__,
            e,
            exc_info=True,
        )
        return None
    return [f.replace("\\", "/") for f in staged if f.endswith(".py")]


def _collect_string_literals(value) -> list[str]:
    """从 Tuple/List/Set AST 节点收集 str Constant 元素（仅直接元素，不递归嵌套）。

    Args:
        value: AST 节点（期望 Tuple/List/Set）。

    Returns:
        字符串字面量列表；非容器或含任何非 str 字面量元素（数字/变量/嵌套容器/Starred）
        → 空列表（保守：含非 str 元素视为非纯前缀集合，放弃判定，降误报）。
    """
    if not isinstance(value, (ast.Tuple, ast.List, ast.Set)):
        return []
    out: list[str] = []
    for elt in value.elts:
        # Python 3.8+ Constant；仅收 str（排除 int/bytes/None 等混入的"伪前缀集合"）
        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
            out.append(elt.value)
        else:
            # 含非 str 字面量（数字/变量/Starred/嵌套容器）→ 不是纯字符串前缀集合，保守放弃
            return []
    return out


def _target_name(target) -> str:
    """推断赋值目标名（Name.id / Attribute.attr / Tuple-List 多目标摘要）。"""
    if isinstance(target, ast.Name):
        return target.id
    if isinstance(target, ast.Attribute):
        return target.attr
    if isinstance(target, (ast.Tuple, ast.List)):
        names = [_target_name(e) for e in target.elts]
        return "(" + ", ".join(names) + ")"
    return "<expr>"


def _find_hardcoded_prefix_collections(tree: ast.AST, dir_prefixes: frozenset[str]) -> list[tuple[int, str, list[str]]]:
    """遍历 AST，找硬编码 dir_prefix 集合的赋值节点。

    Args:
        tree: 模块 AST。
        dir_prefixes: 已知 dir_prefix 集合（SSoT 真源）。

    Returns:
        [(lineno, target_name, matched_prefixes)] 列表；matched_prefixes 为该集合中
        精确命中 dir_prefixes 的字符串列表。
    """
    violations: list[tuple[int, str, list[str]]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            value = node.value
            target = node.targets[0] if node.targets else None
        elif isinstance(node, ast.AnnAssign):
            value = node.value
            target = node.target
        else:
            continue
        if value is None:
            continue
        strs = _collect_string_literals(value)
        if len(strs) < _MIN_PREFIX_MATCHES_FOR_VIOLATION:
            continue
        matched = [s for s in strs if s in dir_prefixes]
        if len(matched) >= _MIN_PREFIX_MATCHES_FOR_VIOLATION:
            name = _target_name(target) if target is not None else "<expr>"
            violations.append((node.lineno, name, matched))
    return violations


def make_test_residue_ssot_gate() -> GateSpec:
    """构造测试残留前缀硬编码阻断门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="TEST-RESIDUE-SSOT", priority=56)。
        priority=56——DERIVED-FILE-DELETION-PROTECTION(46)/HELD-OVERLAP(50) 之后、
        BLUEPRINT-NODE-ID-HARDCODE(57) 之前（同 hardcode 检测族）。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 加载 dir_prefixes（falsy 表示 fail-open 检测器失效）
        dir_prefixes = _load_dir_prefixes()
        if not dir_prefixes:
            return True, ""

        # 2. 获取 staged .py 文件（None/空 → 放行）
        staged_py = _get_staged_py_files(gateway)
        if not staged_py:
            return True, ""

        # 3. 获取 worktree root（fail-open 回退 gateway.project_root）
        wt_root = _get_worktree_root(gateway)

        # 4. 逐文件 AST 检测
        all_violations: list[str] = []
        for rel in staged_py:
            abs_path = rel if os.path.isabs(rel) else os.path.join(wt_root, rel.replace("/", os.sep))
            if not os.path.isfile(abs_path):
                continue
            try:
                with open(abs_path, encoding="utf-8", errors="replace") as fh:
                    source = fh.read()
                tree = ast.parse(source, filename=rel)
            except (OSError, SyntaxError, ValueError) as exc:
                # 单文件读/语法错误 fail-open（不阻断 commit，语法错误由其他 gate/lint 管）
                logger.warning(
                    "TEST-RESIDUE-SSOT gate fail-open: %s 解析失败(%s: %s)，跳过该文件。",
                    rel,
                    type(exc).__name__,
                    exc,
                )
                continue
            for lineno, name, matched in _find_hardcoded_prefix_collections(tree, dir_prefixes):
                all_violations.append(f"  {rel}:{lineno} ({name}) 硬编码前缀 {sorted(set(matched))}")

        if not all_violations:
            return True, ""

        detail = "\n".join(all_violations[:20])
        return False, (
            "TEST_RESIDUE_SSOT_VIOLATION——检出硬编码测试残留目录前缀集合（重复造轮子风险）。\n"
            "前缀真源 = trae_071 §test_residue_reclaim.covered_patterns.dir_prefixes（YAML），\n"
            "MUST 通过 reconciliation_registry._load_test_residue_config() 动态加载，禁止硬编码\n"
            "（trae_062 SSoT：规则数据真源是 YAML 文件）。\n" + detail
        )

    return GateSpec(gate_id="TEST-RESIDUE-SSOT", check=_check, priority=56)
