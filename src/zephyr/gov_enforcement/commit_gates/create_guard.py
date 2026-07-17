# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.create_guard
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec), zephyr.governance.capability_lookup (REGISTRY_YAML, CapabilityLookup)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 硬阻断——staged 新增 .py 文件无 creation_token 时阻断 commit（passed=False）；tests/ 豁免（测试非能力真源，真源：commit_gate_registry.is_test_exempt）；非 rules/ 新增 .yaml 无 creation_token 亦硬阻断（扩展 CREATE-GUARD 到 .yaml，防造第二配置真源，.yaml 是 YAML->DB 单向同步真源）；rules/ .yaml 不走 token 检查（已有命名检查 L232-278）；YAML 不可达时 fail-closed 阻断（registry 故障是环境异常，禁止放行以防删 registry 绕过 token 检查）；git diff 失败亦 fail-closed；token 匹配按相对路径精确比对（路径归一化为正斜杠）；rules/ 新增(A)+rename(R) .yaml 两类命名违规硬阻断（ARCH-037 DIM-5 commit-time 强制：①非trae命名 ②单段name，--no-verify 绕不过）；token 检测通过后追加 check_capability_duplicates 调用（ARCH-031 门禁缺口治本：L3 pre-commit hook 被 --no-verify 绕过->L2 create_guard 追加 basename 碰撞检测，含未注册 basename 碰撞 _check_unregistered_basename_collision，收窄 governance/ 前缀+排除 _archive/，CapabilityLookup 不可用时 fail-open 不阻断）；新建 .py 文件头部 30 行内 MUST 含 14 字段标注（ARCH-031 14字段治本：# [FIELD] value 格式，BLUEPRINT/MODULE/DOMAIN/DEPENDENCIES/CONSUMERS/STARTUP/MATURITY/INVARIANTS/MODIFY-GUARD/STABILITY/SAFETY/AI_AUTONOMY/ERROR_CONTRACT/TESTS，缺字段硬阻断）；codegen 文件豁免（含 BEGIN CODEGEN/BEGIN CODGEN 标记，字段由模板注入）；__init__.py 最低 3 字段（BLUEPRINT/MODULE/DOMAIN，包标记可省 CONSUMERS 等）；14字段规范真源在 AGENTS.md + governance/__init__.py docstring；governance/ 根禁止新增 .py 文件（ARCH-031 防复发2026-07-02：治本后仅保留 9 个高风险核心模块，新模块 MUST 放入子目录，path.count("/")==3 匹配 src/zephyr/governance/<name>.py 硬阻断）
# [MODIFY-GUARD] gate_id="CREATE-GUARD"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——YAML 读取/解析异常降级为 fail-closed 阻断（passed=False，detail 含修复指引：恢复 registry / 修正 YAML 语法）；git diff 异常降级为 fail-closed 阻断；对标 directory_contract_gate.py fail-closed 设计
# [TESTS] tests/governance/commit_gates/test_create_guard.py
# [A_module] module_id=MOD-GOV-create_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""create_guard.py — 新建 .py / 非 rules/ .yaml 文件 creation_token 阻断门禁（CREATE-GUARD，2026-06-30 治本）

检测 staged 新增 .py 文件与非 rules/ .yaml 文件是否在 capability_canonical_file_registry.yaml 的
creation_tokens 字段登记。无 token 的 .py / .yaml 文件 -> 硬阻断，提示"无 creation_token，
禁止造第二真源（trae_060 §2）"。有 token 的 .py / .yaml 文件 -> 放行。

.yaml token 扩展（2026-07-01，trae_060 §2 向内收治本）
-------------------------------------------------------
病根：.yaml 是配置真源（YAML->DB 单向同步硬约束），第二份 .yaml 配置真源
的危害比 .py 更隐蔽（同步漂移会污染 9 个 readonly DB 表）。rules/ 目录已有
命名检查（L232-278），但非 rules/ .yaml 无任何 commit-time 检测，--no-verify
绕过 pre-commit hooks 后可造第二配置真源。
治本：扩展现有 create_guard 检测范围到非 rules/ .yaml（不新增门禁，规避自指
递归——同 reconciler 审查标记检测先例）。新增 .yaml 文件无 creation_token
-> 硬阻断，复用 .py 的 token 索引（同一 registered_files 集合）。

元问题3治本扩展（2026-06-30，AD-GOV-001 收敛约束技术强制）
------------------------------------------------------------
扩展检测范围：若 commit 包含 ``src/zephyr/governance/audit/reconciliation_registry.py``，
用 AST 对比 staged 与 HEAD 版本的 ``make_*_reconciler`` 函数集，新增函数需在
def 前 5 行内添加 ``# trae_060-reviewed: <审查结论>`` 标记，否则硬阻断。

病根：AD-GOV-001 约束"新增 reconciler 前 MUST 过 trae_060 §4 元问题审查"是
君子协定，无技术强制，新 AI 可直接造新 reconciler 绕过审查。
递归陷阱：若新增门禁强制此审查，门禁本身也是"新增"，需过 §4 审查，无限递归。
治本：扩展已有 create_guard 检测范围（不新增门禁，规避自指递归）。

ARCH-037 治本扩展（2026-07-01，DIM-5 commit-time 强制）
-------------------------------------------------------
扩展检测范围：若 commit 含 ``docs/01_policies_and_standards/rules/`` 下新增(A)
或 rename(R) 的 ``.yaml`` 文件，检测两类命名违规 -> 硬阻断：
  ① 非 trae 命名（不匹配 trae_NNN_ 前缀，如 foo.yaml）——红蓝漏洞1修复
  ② 单段 name（匹配 trae_NNN_ 但 name 段无下划线，如 trae_999_test.yaml）

病根：DIM-5 检测能力已就位（validate_rule_frontmatter.py pre-commit hook），但
``git commit --no-verify`` 绕过所有 pre-commit hooks，DIM-5 沦为君子协定，无技术
强制。治本：扩展已有 create_guard（GitCommitGateway 注册 gate，``--no-verify``
绕不过），复用 DIM-5 正则逻辑（commit-time 强制层，DIM-5 真源仍在
validate_rule_frontmatter.py，两处正则保持一致）。

rename 检测（红蓝漏洞2修复）：--diff-filter=R 取新文件名检测，防 rename+--no-verify
绕过（rename 不是新增，--diff-filter=A 漏检）。

同 line 23-32 reconciler 审查标记检测先例：扩展现有 gate 检测范围（不新增门禁，
规避自指递归 + AD-GOV-001 收敛约束）。

病根（"造第二真源"根因）
-------------------------
AI 新建 .py 文件时可能复制已有实现（违反 trae_060 §2 唯一真源原则）。现有缓解
（GATE-SSOT module_path 冲突检测 + GATE-SSOT-SINGLESOURCE 文件名检测 +
capability_overlap_gate warn-only）均在 commit 时检测，此时文件已写完——
检测滞后于创建。本 gate 治本：强制 AI 在创建新 .py 文件前先在
creation_tokens 字段登记 token（声明创建意图 + 关联 capability），
未登记则 commit 硬阻断。token 登记是"创建前"动作（先登记再写文件），
把检测点从"commit 时"前移到"创建前"。

设计权衡
--------
1. **硬阻断而非 warn-only**：capability_overlap_gate 是 warn-only（文件名 token
   匹配是启发式，可能误报）；本 gate 用精确路径比对（creation_tokens[].file 与
   staged 新增文件路径精确匹配），无误报风险，故硬阻断。
2. **tests/ 豁免**：测试文件不是能力真源（不提供 canonical 实现），对标
   capability_overlap_gate 的 tests/ 豁免设计。真源已收敛到
   ``commit_gate_registry.is_test_exempt``（治本2，消除两 gate 实现不一致——
   create_guard 先归一再比对、capability_overlap_gate 未归一化导致 Windows latent bug）。
   包含 tests/ 会要求每个测试文件登记 token，过度 disruptive 且无 SSoT 收益。
3. **fail-closed（YAML 不可达，治本1 2026-06-30）**：YAML 缺失/解析失败/非 dict
   时阻断——registry 故障是环境异常，fail-open 会被"删 registry 绕过 token 检查"
   利用（红蓝攻击向量）。对标 directory_contract_gate.py fail-closed 设计。
   配套治本1②：registry 入 validate_rules_integrity.RULES_MANIFEST，防裸 commit 删 registry
   （C 层 MISSING+critical 阻断，防 DoS）。YAML 可达但文件无 token 时才走 token 硬阻断。
4. **priority=60**：在 HELD-OVERLAP(50) 之后、CAPABILITY-OVERLAP(200) 之前执行
   ——先过搭便车/claim 检查（session 级约束），再过 creation_token 检查（文件级
   约束），最后 warn-only 提示。

裁定#216 Tier1 P1 重构（2026-07-15，Extract Method）
----------------------------------------------------
原 _check 闭包 475 行 McCabe=101（11 个独立检测块串联，P1 gate-closure multi-check 模式）。
治本：Extract Method 提取为 9 个模块级 helper（均 McCabe≤15），_check 简化为
~30 行 pipeline（McCabe≈14）。行为等价契约：每个 helper 返回 (True, "")=放行/继续，
(False, msg)=硬阻断。关键行为保持：
  - governance/ 根检测用 UNFILTERED new_py_files（commit_files_rel 过滤前）
  - 两处 early return（过滤前/过滤后均空时 return True）
  - field_header 内部 `if not new_py_files: return True, ""`（无 .py 时跳过 trae_047 读取）

creation_tokens 字段结构（capability_canonical_file_registry.yaml 顶层字段）::

    creation_tokens:
      - file: "src/zephyr/gov_enforcement/commit_gates/create_guard.py"
        token: "auto-create-guard-20260630"
        created_by: "session-trae-redteam-deadly-5"
        capability: "create_guard"

Usage::

    from zephyr.gov_enforcement.commit_gates.create_guard import make_create_guard

    registry.register(make_create_guard())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)
"""

from __future__ import annotations

import ast
import logging
import os
import re

import yaml

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt
from zephyr.governance.rule_patterns import RULE_NAME_RE

logger = logging.getLogger(__name__)

__all__ = ["make_create_guard"]

# === 裁定#216 Tier1 P1 Extract Method 重构（2026-07-15） ===
# 模块级常量（原 _check 闭包内局部常量，提取为模块级以消除重复定义）
_RECONCILER_REGISTRY_REL = "src/zephyr/governance/audit/reconciliation_registry.py"
_TRAEO60_MARKER = "trae_060-reviewed"
_RULES_DIR_PREFIX = "docs/01_policies_and_standards/rules/"
_GOVERNANCE_ROOT_PREFIX = "src/zephyr/governance/"
_ALIAS_MARKER = "class-name-alias"
_OTHER_FORMAT_EXTENSIONS = (".md", ".sh", ".ps1", ".mmd", ".json")


def _compute_commit_files_rel(gateway, files: list[str]) -> set[str]:
    """计算 commit 文件相对路径集合（reconciler 检测 + token 检测复用）。"""
    commit_files_rel: set[str] = set()
    for f in files:
        try:
            rel = os.path.relpath(f, str(gateway.project_root)).replace("\\", "/")
            commit_files_rel.add(rel)
        except (ValueError, OSError):
            continue
    return commit_files_rel


def _extract_make_reconcilers(tree) -> set[str]:
    """从 AST 提取 make_*_reconciler 函数名集合。"""
    if tree is None:
        return set()
    return {
        n.name for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef)
        and n.name.startswith("make_")
        and n.name.endswith("_reconciler")
    }


def _find_unmarked_reconcilers(
    staged_tree, staged_src: str, new_reconcilers: set[str]
) -> list[str]:
    """在 staged AST 中查找未标记 trae_060 的新增 reconciler 函数名。

    检查 def 行前 5 行（含 decorator/注释区）是否有 '# trae_060-reviewed' 标记。
    """
    staged_lines = staged_src.splitlines()
    unmarked = []
    for n in ast.walk(staged_tree):
        if not (isinstance(n, ast.FunctionDef) and n.name in new_reconcilers):
            continue
        has_marker = False
        for i in range(max(0, n.lineno - 6), n.lineno - 1):
            if _TRAEO60_MARKER in staged_lines[i]:
                has_marker = True
                break
        if not has_marker:
            unmarked.append(n.name)
    return unmarked


def _check_reconciler_marker(gateway, commit_files_rel: set[str]) -> tuple[bool, str]:
    """元问题3治本：新增 make_*_reconciler 需 trae_060 §4 审查标记。

    放在最前：reconciliation_registry.py 是已存在文件，不在 new_py_files 里，
    若等 new_py_files 过滤后检测，会被 "not new_py_files: return True" 提前返回跳过。
    """
    if _RECONCILER_REGISTRY_REL not in commit_files_rel:
        return True, ""

    try:
        staged_res = gateway._run_git(["git", "show", f":{_RECONCILER_REGISTRY_REL}"])
        head_res = gateway._run_git(["git", "show", f"HEAD:{_RECONCILER_REGISTRY_REL}"])
    except Exception:
        staged_res = head_res = None  # fail-open：git 故障时不阻断（避免误伤正常 commit）

    if staged_res is None or staged_res.returncode != 0:
        return True, ""

    staged_src = staged_res.stdout
    head_src = head_res.stdout if (head_res is not None and head_res.returncode == 0) else ""
    try:
        staged_tree = ast.parse(staged_src)
        head_tree = ast.parse(head_src) if head_src else None
    except SyntaxError:
        return True, ""  # 语法错误由其他 gate 检测，此处 fail-open

    staged_makes = _extract_make_reconcilers(staged_tree)
    head_makes = _extract_make_reconcilers(head_tree)
    new_reconcilers = staged_makes - head_makes
    if not new_reconcilers:
        return True, ""

    unmarked = _find_unmarked_reconcilers(staged_tree, staged_src, new_reconcilers)

    if unmarked:
        return False, (
            f"新增 reconciler 未过 trae_060 §4 元问题审查: {sorted(unmarked)}. "
            f"AD-GOV-001 收敛约束：新增 make_*_reconciler 前 MUST 过 trae_060 §4 审查"
            f"（该存在/能否合并进已有/治本），并在函数定义前添加 "
            f"'# {_TRAEO60_MARKER}: <审查结论>' 标记。"
            f"修复：在 reconciliation_registry.py 新增 make_*_reconciler 函数定义前"
            f"添加注释 '# {_TRAEO60_MARKER}: <审查结论>'，或合并进已有 reconciler。"
        )
    return True, ""


def _get_staged_new_files(gateway) -> tuple[list[str] | None, str]:
    """获取 staged 新增文件列表（--diff-filter=A）。

    Returns:
        (staged_new, "") 成功； (None, detail) fail-closed 阻断。
    """
    try:
        diff_result = gateway._run_git(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=A"]
        )
        if diff_result.returncode != 0:
            return None, (
                f"CREATE-GUARD fail-closed: git diff 失败(rc={diff_result.returncode})，"
                f"无法确定 staged 新增文件。禁止放行——检测器失效时漏放未登记 .py。"
                f"修复：检查 git 状态（git status）确认仓库可用后重试。"
            )
        return diff_result.stdout.strip().splitlines(), ""
    except Exception as e:
        return None, (
            f"CREATE-GUARD fail-closed: git diff 异常({type(e).__name__}: {e})，"
            f"无法确定 staged 新增文件。禁止放行——检测器失效时漏放未登记 .py。"
            f"修复：检查 git 仓库状态后重试。"
        )


def _collect_renamed_rule_files(gateway, commit_files_rel: set[str]) -> list[str]:
    """收集 rules/ 下 rename(R) 的 .yaml 文件（检测 rename 后的新文件名）。

    fail-open：git diff 故障不阻断（新增检测已覆盖主要场景）。
    """
    renamed: list[str] = []
    try:
        rename_result = gateway._run_git(
            ["git", "diff", "--cached", "--name-status", "--diff-filter=R"]
        )
        if rename_result.returncode == 0:
            for line in rename_result.stdout.strip().splitlines():
                parts = line.split("\t")
                if len(parts) >= 3:
                    new_path = parts[-1].replace("\\", "/")
                    if (new_path.startswith(_RULES_DIR_PREFIX)
                            and new_path.endswith(".yaml")
                            and new_path in commit_files_rel):
                        renamed.append(new_path)
    except Exception:
        pass  # fail-open：rename 检测故障不阻断
    return renamed


def _check_rule_yaml_naming(
    gateway, staged_new: list[str], commit_files_rel: set[str]
) -> tuple[bool, str]:
    """ARCH-037 治本：rules/ .yaml 命名格式硬阻断（非 trae 命名 / 单段 name）。

    放在 new_py_files 过滤前：若 commit 只含 .yaml 无 .py，new_py_files 为空
    会提前 return True 跳过本检测，故须在 return 前完成 .yaml 命名检测。
    """
    new_rule_files: list[str] = []
    for f in staged_new:
        f_norm = f.replace("\\", "/")
        if (f_norm.startswith(_RULES_DIR_PREFIX)
                and f_norm.endswith(".yaml")
                and f_norm in commit_files_rel):
            new_rule_files.append(f_norm)

    renamed_rule_files = _collect_renamed_rule_files(gateway, commit_files_rel)

    bad_rule_names = []
    for f in new_rule_files + renamed_rule_files:
        basename = f.rsplit("/", 1)[-1]
        m = RULE_NAME_RE.match(basename)
        if not m:
            # ① 非 trae 命名（不匹配 trae_\d+_<xxx>.yaml）
            bad_rule_names.append((f, basename, "非trae命名"))
        elif "_" not in m.group(1):
            # ② 单段 name（匹配 trae_NNN_ 但缺主题前缀）
            bad_rule_names.append((f, m.group(1), "单段name缺主题前缀"))
    if bad_rule_names:
        detail = "; ".join(f"{f}（{reason}='{seg}'）" for f, seg, reason in bad_rule_names)
        return False, (
            f"rules/ .yaml 文件命名违规(ARCH-037 DIM-5硬阻断): {detail}. "
            f"命名约定: trae_NNN_<主题>_<描述>.yaml（见 trae_028 GOV-DOC-003）。"
            f"--no-verify 绕不过本检测（create_guard 是 GitCommitGateway 注册 gate，非 pre-commit hook）。"
            f"修复：用 `python scripts/scaffold.py rule <主题_描述>` 创建（RULE-TWO 强制入口），"
            f"或手工重命名为 trae_NNN_<主题>_<描述>.yaml。"
        )
    return True, ""


def _filter_new_py_and_yaml(staged_new: list[str]) -> tuple[list[str], list[str]]:
    """过滤 staged 新增文件为 (new_py_files, new_yaml_files)。

    - new_py_files: .py 文件，排除 tests/ 豁免（真源：commit_gate_registry.is_test_exempt）
    - new_yaml_files: .yaml 文件，排除 tests/ 豁免，排除 rules/ 目录（rules/ 已有命名检查）
    """
    new_py_files = [
        f.replace("\\", "/") for f in staged_new
        if f.endswith(".py") and not is_test_exempt(f)
    ]
    new_yaml_files = [
        f.replace("\\", "/") for f in staged_new
        if f.endswith(".yaml") and not is_test_exempt(f)
        and not f.replace("\\", "/").startswith(_RULES_DIR_PREFIX)
    ]
    return new_py_files, new_yaml_files


def _filter_new_other_formats(staged_new: list[str]) -> list[str]:
    """过滤 .md/.sh/.ps1/.mmd/.json 格式（阶段 2，ARCH-TTL-DOC-001 全 7 格式覆盖）。"""
    return [
        f.replace("\\", "/") for f in staged_new
        if any(f.endswith(ext) for ext in _OTHER_FORMAT_EXTENSIONS)
        and not is_test_exempt(f)
    ]


def _check_governance_root(gateway, new_py_files: list[str]) -> tuple[bool, str]:
    """ARCH-031 防复发：禁止 governance/ 根新增/rename .py 文件。

    NOTE: 使用 UNFILTERED new_py_files（commit_files_rel 过滤前），因为 rename
    检测 MUST 在 early return 前完成。
    """
    _gov_root_new = [
        f for f in new_py_files
        if f.startswith(_GOVERNANCE_ROOT_PREFIX) and f.count("/") == 3
    ]
    if _gov_root_new:
        return False, (
            f"ARCH-031 防复发: 禁止在 governance/ 根新增 .py 文件: {_gov_root_new}. "
            f"governance/ 根仅保留 9 个高风险核心模块（__init__/base/capability_lookup/"
            f"depgraph_schema/evidence_pack/integrity/merkle_hourly/"
            f"performance_attribution_report/rule_patterns）。"
            f"新模块 MUST 放入对应功能子目录（如 audit/ persistence/ commit_gates/ 等）。"
            f"修复：将文件移动到 src/zephyr/governance/<subdir>/ 下。"
        )
    # 检测②: rename(R) .py 到 governance/ 根（防 git mv 绕过 --diff-filter=A 漏检）
    try:
        _rename_result = gateway._run_git(
            ["git", "diff", "--cached", "--name-status", "--diff-filter=R"]
        )
        if _rename_result.returncode == 0:
            _gov_root_renamed = []
            for line in _rename_result.stdout.strip().splitlines():
                parts = line.split("\t")
                if len(parts) >= 3:
                    _new_path = parts[2].replace("\\", "/")
                    if (_new_path.startswith(_GOVERNANCE_ROOT_PREFIX)
                            and _new_path.count("/") == 3
                            and _new_path.endswith(".py")):
                        _gov_root_renamed.append(_new_path)
            if _gov_root_renamed:
                return False, (
                    f"ARCH-031 防复发: 禁止 rename 到 governance/ 根 .py 文件: "
                    f"{_gov_root_renamed}. 新模块 MUST 放入对应功能子目录。"
                    f"修复：将文件移动到 src/zephyr/governance/<subdir>/ 下。"
                )
    except Exception as e:
        logger.warning(
            "CREATE-GUARD: ARCH-031 rename 检测 git diff 失败: %s",
            e, exc_info=True,
        )
        # fail-open: git diff 失败不阻断 rename 检测（下游 gate 仍检测新增文件）
    return True, ""


def _check_class_uniqueness(gateway, new_py_files: list[str]) -> tuple[bool, str]:
    """ARCH-034 P3 遗留2治本：类名跨模块唯一性检测。

    豁免：class 定义前3行内有 '# class-name-alias: <理由>' 标记（合法 re-export 场景）。
    fail-closed：git grep 故障时阻断（防漏放同名 class）。
    """
    _class_violations = []
    for _py_file in new_py_files:
        _abs_path = str(gateway.project_root / _py_file)
        try:
            with open(_abs_path, encoding="utf-8") as _f:
                _src = _f.read()
            _tree = ast.parse(_src)
        except Exception:
            continue  # 语法错误由其他 gate 检测，此处 fail-open
        _lines = _src.splitlines()
        for _node in ast.walk(_tree):
            if not isinstance(_node, ast.ClassDef):
                continue
            # 检查豁免标记（def 行前3行内）
            _has_marker = False
            for _i in range(max(0, _node.lineno - 4), _node.lineno - 1):
                if _i < len(_lines) and _ALIAS_MARKER in _lines[_i]:
                    _has_marker = True
                    break
            if _has_marker:
                continue
            # git grep 搜索同名 class 在 src/zephyr/ 下（排除当前文件）
            #ARCH-034 遗留3治本：git grep 故障改 fail-closed
            try:
                _grep_res = gateway._run_git([
                    "git", "grep", "-l", f"^class {_node.name}\\b",
                    "--", "src/zephyr/"
                ])
                if _grep_res.returncode == 0:
                    _existing = [
                        f.replace("\\", "/") for f in _grep_res.stdout.strip().splitlines()
                        if f.replace("\\", "/") != _py_file
                    ]
                    if _existing:
                        _class_violations.append((_py_file, _node.name, _existing))
            except Exception as e:
                return False, (
                    f"CREATE-GUARD CLASS-UNIQUENESS fail-closed: git grep 异常"
                    f"({type(e).__name__}: {e})，无法检测 class '{_node.name}' 跨模块冲突。"
                    f"禁止放行——检测器失效时漏放同名 class（AI 开发幻觉温床）。"
                    f"修复：检查 git 状态（git status）确认仓库可用后重试。"
                )
    if _class_violations:
        _detail = "; ".join(
            f"{f} 定义 class {name} 与已有 {existing} 同名"
            for f, name, existing in _class_violations
        )
        return False, (
            f"类名跨模块冲突(ARCH-034 CLASS-UNIQUENESS): {_detail}. "
            f"同名不同义是 AI 开发幻觉温床（后导入覆盖前导入，不报错）。"
            f"修复：①改名区分（如 Managed* 前缀）②若是合法 re-export，"
            f"在 class 定义前加 '# class-name-alias: <理由>' 标记豁免。"
        )
    return True, ""


def _check_creation_token(
    gateway, new_py_files: list[str], new_yaml_files: list[str],
    new_other_files: list[str] | None = None,
) -> tuple[bool, str]:
    """检测新增 .py/.yaml 文件是否登记了 creation_token（trae_060 §2 唯一真源）。

    fail-closed：YAML 不可达时阻断（防删 registry 绕过 token 检查）。
    P-2 修复：registry 路径随 gateway.project_root 解析（支持 worktree 路径）。
    """
    from zephyr.governance.capability_lookup import REGISTRY_YAML

    _registry_yaml = (
        gateway.project_root
        / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
        / "capability_canonical_file_registry.yaml"
    )
    if not _registry_yaml.exists():
        _registry_yaml = REGISTRY_YAML  # 回退到全局真源

    if not _registry_yaml.exists():
        return False, (
            f"CREATE-GUARD fail-closed: capability registry 不可达（文件缺失: {_registry_yaml}）。"
            f"禁止放行——防删 registry 绕过 creation_token 检查。"
            f"修复：git checkout HEAD -- {_registry_yaml} 恢复 registry 后重试。"
        )
    try:
        data = yaml.safe_load(_registry_yaml.read_text(encoding="utf-8"))
    except Exception as e:
        return False, (
            f"CREATE-GUARD fail-closed: capability registry 解析失败"
            f"({type(e).__name__}: {e})。禁止放行——registry 是 creation_token 真源，"
            f"语法错误=检测器失效。修复：修正 {_registry_yaml} 的 YAML 语法后重试。"
        )

    if not isinstance(data, dict):
        return False, (
            f"CREATE-GUARD fail-closed: registry YAML 顶层非 dict（结构异常）。"
            f"禁止放行——结构异常=检测器失效。修复：检查 {_registry_yaml} 顶层结构后重试。"
        )

    # 构建 creation_tokens 文件索引（相对路径 -> token 条目）
    tokens = data.get("creation_tokens", []) or []
    registered_files: set[str] = set()
    if isinstance(tokens, list):
        for entry in tokens:
            if not isinstance(entry, dict):
                continue
            token_file = entry.get("file", "")
            if isinstance(token_file, str) and token_file:
                registered_files.add(token_file.replace("\\", "/"))

    # 检测新增 .py 文件是否登记了 creation_token
    unregistered = [f for f in new_py_files if f not in registered_files]
    if unregistered:
        return False, (
            f"无 creation_token，禁止造第二真源（trae_060 §2）: {unregistered}. "
            f"commit 新建 .py 文件前 MUST 在 capability_canonical_file_registry.yaml "
            f"的 creation_tokens 字段登记 token（声明创建意图 + 关联 capability）。"
            f"格式: - file: \"<相对路径>\"  token: \"auto-xxx\"  "
            f"created_by: \"session-xxx\"  capability: \"xxx\""
        )
    # 检测新增非 rules/ .yaml 文件是否登记了 creation_token
    unregistered_yaml = [f for f in new_yaml_files if f not in registered_files]
    if unregistered_yaml:
        return False, (
            f"无 creation_token，禁止造第二真源（trae_060 §2）: {unregistered_yaml}. "
            f"commit 新建 .yaml 文件前 MUST 在 capability_canonical_file_registry.yaml "
            f"的 creation_tokens 字段登记 token（声明创建意图 + 关联 capability）。"
            f"格式: - file: \"<相对路径>\"  token: \"auto-xxx\"  "
            f"created_by: \"session-xxx\"  capability: \"xxx\""
        )
    # 阶段 2 治本（ARCH-TTL-DOC-001）：检测新增 .md/.sh/.ps1/.mmd/.json 文件
    if new_other_files:
        unregistered_other = [f for f in new_other_files if f not in registered_files]
        if unregistered_other:
            return False, (
                f"无 creation_token，禁止造第二真源（trae_060 §2）: {unregistered_other}. "
                f"commit 新建 .md/.sh/.ps1/.mmd/.json 文件前 MUST 在 "
                f"capability_canonical_file_registry.yaml 的 creation_tokens 字段登记 token"
                f"（声明创建意图 + 关联 capability）。"
                f"格式: - file: \"<相对路径>\"  token: \"auto-xxx\"  "
                f"created_by: \"session-xxx\"  capability: \"xxx\""
            )
    return True, ""


def _check_field_header(gateway, new_py_files: list[str]) -> tuple[bool, str]:
    """ARCH-031 治本：字段头部完整性检测（14 字段 / __init__.py 最低 3 字段）。

    豁免：codegen 文件（BEGIN CODEGEN 标记）。真源：trae_047 field_specs。
    fail-closed：真源读取失败时阻断。无 new_py_files 时直接放行。
    """
    if not new_py_files:
        return True, ""

    _TRAE_047_YAML = gateway.project_root / "docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml"
    # F-5 修复续：trae_047 路径回退到全局 REPO_ROOT（对标 P-2 capability registry 回退模式）
    if not _TRAE_047_YAML.exists():
        from zephyr.shared.io.paths import REPO_ROOT
        _TRAE_047_YAML = REPO_ROOT / "docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml"
    try:
        _rule_data = yaml.safe_load(_TRAE_047_YAML.read_text(encoding="utf-8"))
        _field_specs = _rule_data["sections"]["gov_eng_002"]["field_specs"]
        _REQUIRED_FIELDS = _field_specs["a_full"]["required"]
        _INIT_MIN_FIELDS = _field_specs["init_min"]
    except Exception as _e:
        return False, (
            f"字段头部规范真源读取失败（trae_047.yaml field_specs）: {_e}. "
            f"修复：检查 {_TRAE_047_YAML} 是否存在且 field_specs 结构完整。"
        )

    for _py_file in new_py_files:
        _abs_path = gateway.project_root / _py_file
        if not _abs_path.exists():
            continue
        try:
            _head = "\n".join(
                _abs_path.read_text(encoding="utf-8", errors="replace").split("\n")[:30]
            )
        except Exception as e:
            logger.debug(
                "CREATE-GUARD: 读取文件头失败 file=%s: %s",
                _py_file, e, exc_info=True,
            )
            continue  # 读取失败由其他 gate 检测，此处 fail-open

        # codegen 文件豁免（自动生成，字段由模板注入，手写会被覆盖）
        if "BEGIN CODEGEN" in _head or "BEGIN CODGEN" in _head:
            continue

        # __init__.py 只要求 3 字段（包标记，CONSUMERS 等可省）
        _is_init = _py_file.endswith("__init__.py")
        _required = _INIT_MIN_FIELDS if _is_init else _REQUIRED_FIELDS

        _missing = [
            _field for _field in _required
            if not re.search(rf'#\s*\[{re.escape(_field)}\]', _head)
        ]

        if _missing:
            return False, (
                f"字段头部不完整（ARCH-031）: {_py_file} 缺失字段: {_missing}. "
                f"修复：在文件头部添加 '# [FIELD] value' 标注（共{len(_required)}字段: "
                f"{'/'.join(_required)}）。"
                + (f" __init__.py 最低要求: {'/'.join(_INIT_MIN_FIELDS)}" if _is_init else "")
            )
    return True, ""


def _check_basename_collision(gateway, new_py_files: list[str]) -> tuple[bool, str]:
    """ARCH-031 门禁缺口治本：磁盘 basename 碰撞检测（GATE-SSOT L2）。

    fail-open：CapabilityLookup 不可用时 warning 并跳过。
    """
    if not new_py_files:
        return True, ""
    try:
        from zephyr.governance.capability_lookup import (
            CapabilityLookup,
            CAPABILITY_DUPLICATE_FIX_HINT,
        )
        _lookup = CapabilityLookup()
        _new_py_tuples = [(str(gateway.project_root / f), f) for f in new_py_files]
        _dups = _lookup.check_capability_duplicates(_new_py_tuples)
        if _dups:
            _details = "; ".join(f"{d.rel_path}: {d.detail}" for d in _dups)
            return False, (
                f"能力重复/basename碰撞(GATE-SSOT L2): {_details}. "
                f"{CAPABILITY_DUPLICATE_FIX_HINT}"
            )
    except Exception as _e:
        logger.warning(
            "CREATE-GUARD: capability_lookup 不可用，跳过 basename 碰撞检测: %s",
            _e, exc_info=True
        )
    return True, ""


def make_create_guard() -> GateSpec:
    """构造新建 .py 文件 creation_token 阻断门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="CREATE-GUARD", priority=60)。
        priority=60——在 HELD-OVERLAP(50) 之后、CAPABILITY-OVERLAP(200) 之前执行。

    裁定#216 Tier1 P1 重构（2026-07-15）：原 _check 闭包 475 行 McCabe=101，
    Extract Method 提取为 9 个模块级 helper，_check 简化为 pipeline McCabe≈14。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        commit_files_rel = _compute_commit_files_rel(gateway, files)

        # 元问题3治本：新增 make_*_reconciler 需 trae_060 §4 审查标记
        passed, detail = _check_reconciler_marker(gateway, commit_files_rel)
        if not passed:
            return False, detail

        # 获取 staged 新增文件（fail-closed）
        staged_new, detail = _get_staged_new_files(gateway)
        if staged_new is None:
            return False, detail

        #ARCH-037：rules/ .yaml 命名格式硬阻断
        passed, detail = _check_rule_yaml_naming(gateway, staged_new, commit_files_rel)
        if not passed:
            return False, detail

        # 过滤 .py / .yaml + 豁免 tests/（真源：commit_gate_registry.is_test_exempt）
        new_py_files, new_yaml_files = _filter_new_py_and_yaml(staged_new)
        new_other_files = _filter_new_other_formats(staged_new)

        #ARCH-031 防复发：governance/ 根检测 MUST 用 UNFILTERED new_py_files
        passed, detail = _check_governance_root(gateway, new_py_files)
        if not passed:
            return False, detail

        if not new_py_files and not new_yaml_files and not new_other_files:
            return True, ""

        # 治本 2026-06-30：只检测 commit 文件中的新增 .py（gateway 选择性提交）
        new_py_files = [f for f in new_py_files if f in commit_files_rel]
        new_yaml_files = [f for f in new_yaml_files if f in commit_files_rel]
        new_other_files = [f for f in new_other_files if f in commit_files_rel]

        if not new_py_files and not new_yaml_files and not new_other_files:
            return True, ""

        #ARCH-034：类名跨模块唯一性检测
        passed, detail = _check_class_uniqueness(gateway, new_py_files)
        if not passed:
            return False, detail

        # creation_token 检测（trae_060 §2 唯一真源）——阶段 2：覆盖全 7 格式
        passed, detail = _check_creation_token(
            gateway, new_py_files, new_yaml_files, new_other_files
        )
        if not passed:
            return False, detail

        #ARCH-031：字段头部完整性检测
        passed, detail = _check_field_header(gateway, new_py_files)
        if not passed:
            return False, detail

        #ARCH-031：basename 碰撞检测
        passed, detail = _check_basename_collision(gateway, new_py_files)
        if not passed:
            return False, detail

        return True, ""

    return GateSpec(gate_id="CREATE-GUARD", check=_check, priority=60)
