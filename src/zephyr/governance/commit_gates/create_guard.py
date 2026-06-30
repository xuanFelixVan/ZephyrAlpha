# [BLUEPRINT] MOD-GOV-create_guard | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §create-guard
# [MODULE] zephyr.governance.commit_gates.create_guard
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.commit_gate_registry (GateSpec), zephyr.governance.capability_lookup (REGISTRY_YAML)
# [CONSUMERS] zephyr.governance.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 硬阻断——staged 新增 .py 文件无 creation_token 时阻断 commit（passed=False）；tests/ 豁免（测试非能力真源，真源：commit_gate_registry.is_test_exempt）；YAML 不可达时 fail-closed 阻断（registry 故障是环境异常，禁止放行以防删 registry 绕过 token 检查）；git diff 失败亦 fail-closed；token 匹配按相对路径精确比对（路径归一化为正斜杠）；rules/ 新增(A)+rename(R) .yaml 两类命名违规硬阻断（ARCH-037 DIM-5 commit-time 强制：①非trae命名 ②单段name，--no-verify 绕不过）
# [MODIFY-GUARD] gate_id="CREATE-GUARD"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——YAML 读取/解析异常降级为 fail-closed 阻断（passed=False，detail 含修复指引：恢复 registry / 修正 YAML 语法）；git diff 异常降级为 fail-closed 阻断；对标 directory_contract_gate.py fail-closed 设计
# [TESTS] tests/test_create_guard.py
# [A_module] module_id=MOD-GOV-create_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""create_guard.py — 新建 .py 文件 creation_token 阻断门禁（CREATE-GUARD，2026-06-30 治本）

检测 staged 新增 .py 文件是否在 capability_canonical_file_registry.yaml 的
creation_tokens 字段登记。无 token 的 .py 文件 → 硬阻断，提示"无 creation_token，
禁止造第二真源（trae_060 §2）"。有 token 的 .py 文件 → 放行。

元问题3治本扩展（2026-06-30，AD-GOV-001 收敛约束技术强制）
------------------------------------------------------------
扩展检测范围：若 commit 包含 ``src/zephyr/governance/reconciliation_registry.py``，
用 AST 对比 staged 与 HEAD 版本的 ``make_*_reconciler`` 函数集，新增函数需在
def 前 5 行内添加 ``# trae_060-reviewed: <审查结论>`` 标记，否则硬阻断。

病根：AD-GOV-001 约束"新增 reconciler 前 MUST 过 trae_060 §4 元问题审查"是
君子协定，无技术强制，新 AI 可直接造新 reconciler 绕过审查。
递归陷阱：若新增门禁强制此审查，门禁本身也是"新增"，需过 §4 审查，无限递归。
治本：扩展已有 create_guard 检测范围（不新增门禁，规避自指递归）。

ARCH-037 治本扩展（2026-07-01，DIM-5 commit-time 强制）
-------------------------------------------------------
扩展检测范围：若 commit 含 ``docs/01_policies_and_standards/rules/`` 下新增(A)
或 rename(R) 的 ``.yaml`` 文件，检测两类命名违规 → 硬阻断：
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

creation_tokens 字段结构（capability_canonical_file_registry.yaml 顶层字段）::

    creation_tokens:
      - file: "src/zephyr/governance/commit_gates/create_guard.py"
        token: "auto-create-guard-20260630"
        created_by: "session-trae-redteam-deadly-5"
        capability: "create_guard"

Usage::

    from zephyr.governance.commit_gates.create_guard import make_create_guard

    registry.register(make_create_guard())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)
"""

from __future__ import annotations

import logging
import os

from zephyr.governance.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_create_guard"]


def make_create_guard() -> GateSpec:
    """构造新建 .py 文件 creation_token 阻断门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="CREATE-GUARD", priority=60)。
        priority=60——在 HELD-OVERLAP(50) 之后、CAPABILITY-OVERLAP(200) 之前执行。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 计算 commit_files_rel（reconciler 检测 + token 检测复用）
        commit_files_rel: set[str] = set()
        for f in files:
            try:
                rel = os.path.relpath(f, str(gateway.project_root)).replace("\\", "/")
                commit_files_rel.add(rel)
            except (ValueError, OSError):
                continue

        # === 元问题3治本（2026-06-30）：新增 make_*_reconciler 需 trae_060 §4 审查标记 ===
        # AD-GOV-001 约束技术强制：扩展已有 create_guard，不新增门禁（规避自指递归——
        # 若新增门禁强制此审查，门禁本身也是"新增"，需过 §4 审查，无限递归）。
        # 病根："新增 reconciler 前 MUST 过 §4 审查"是君子协定，新 AI 可直接造新 reconciler。
        # 治本：扩展已有 create_guard 检测范围——reconciliation_registry.py 新增 make_*_reconciler
        # 时，需在函数定义前 5 行内添加 '# trae_060-reviewed: <审查结论>' 标记。
        # 放在最前：reconciliation_registry.py 是已存在文件，不在 new_py_files 里，
        # 若等 new_py_files 过滤后检测，会被 "not new_py_files: return True" 提前返回跳过。
        _RECONCILER_REGISTRY_REL = "src/zephyr/governance/reconciliation_registry.py"
        _TRAEO60_MARKER = "trae_060-reviewed"

        if _RECONCILER_REGISTRY_REL in commit_files_rel:
            try:
                staged_res = gateway._run_git(["git", "show", f":{_RECONCILER_REGISTRY_REL}"])
                head_res = gateway._run_git(["git", "show", f"HEAD:{_RECONCILER_REGISTRY_REL}"])
            except Exception:
                staged_res = head_res = None  # fail-open：git 故障时不阻断（避免误伤正常 commit）

            if staged_res is not None and staged_res.returncode == 0:
                staged_src = staged_res.stdout
                head_src = head_res.stdout if (head_res is not None and head_res.returncode == 0) else ""
                import ast
                try:
                    staged_tree = ast.parse(staged_src)
                    head_tree = ast.parse(head_src) if head_src else None
                except SyntaxError:
                    staged_tree = head_tree = None  # 语法错误由其他 gate 检测，此处 fail-open

                if staged_tree is not None:
                    def _extract_makes(tree):
                        if tree is None:
                            return set()
                        return {
                            n.name for n in ast.walk(tree)
                            if isinstance(n, ast.FunctionDef)
                            and n.name.startswith("make_")
                            and n.name.endswith("_reconciler")
                        }

                    staged_makes = _extract_makes(staged_tree)
                    head_makes = _extract_makes(head_tree)
                    new_reconcilers = staged_makes - head_makes

                    if new_reconcilers:
                        staged_lines = staged_src.splitlines()
                        unmarked = []
                        for n in ast.walk(staged_tree):
                            if not (isinstance(n, ast.FunctionDef) and n.name in new_reconcilers):
                                continue
                            # 检查 def 行前 5 行（含 decorator/注释区）是否有标记
                            has_marker = False
                            for i in range(max(0, n.lineno - 6), n.lineno - 1):
                                if _TRAEO60_MARKER in staged_lines[i]:
                                    has_marker = True
                                    break
                            if not has_marker:
                                unmarked.append(n.name)

                        if unmarked:
                            return False, (
                                f"新增 reconciler 未过 trae_060 §4 元问题审查: {sorted(unmarked)}. "
                                f"AD-GOV-001 收敛约束：新增 make_*_reconciler 前 MUST 过 trae_060 §4 审查"
                                f"（该存在/能否合并进已有/治本），并在函数定义前添加 "
                                f"'# {_TRAEO60_MARKER}: <审查结论>' 标记。"
                                f"修复：在 reconciliation_registry.py 新增 make_*_reconciler 函数定义前"
                                f"添加注释 '# {_TRAEO60_MARKER}: <审查结论>'，或合并进已有 reconciler。"
                            )

        # 1. 仅关心 staged 新增 .py 文件（--diff-filter=A）
        # 治本1（2026-06-30）：git diff 失败改 fail-closed——无法确定新增文件=检测器失效，
        # fail-open 会漏放未登记 .py。对标 directory_contract_gate.py L123-125 subprocess 失败 fail-closed。
        try:
            diff_result = gateway._run_git(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=A"]
            )
            if diff_result.returncode != 0:
                return False, (
                    f"CREATE-GUARD fail-closed: git diff 失败(rc={diff_result.returncode})，"
                    f"无法确定 staged 新增文件。禁止放行——检测器失效时漏放未登记 .py。"
                    f"修复：检查 git 状态（git status）确认仓库可用后重试。"
                )
            staged_new = diff_result.stdout.strip().splitlines()
        except Exception as e:
            return False, (
                f"CREATE-GUARD fail-closed: git diff 异常({type(e).__name__}: {e})，"
                f"无法确定 staged 新增文件。禁止放行——检测器失效时漏放未登记 .py。"
                f"修复：检查 git 仓库状态后重试。"
            )

        # === ARCH-037 治本扩展（2026-07-01）：rules/ .yaml 命名格式硬阻断 ===
        # DIM-5 检测能力已就位（validate_rule_frontmatter.py pre-commit hook），但被
        # `git commit --no-verify` 绕过。治本：扩展已有 create_guard 检测范围（不新增门禁，
        # 规避自指递归——同 line 23-32 reconciler 审查标记检测先例）。
        # 病根：--no-verify 绕过所有 pre-commit hooks，DIM-5 君子协定无技术强制。
        # 检测：staged 新增(A)+rename(R) docs/.../rules/*.yaml，两类违规→硬阻断：
        #   ① 非 trae 命名（不匹配 trae_\d+_ 前缀，如 foo.yaml）——红蓝漏洞1修复
        #   ② 单段 name（匹配 trae_NNN_ 但 name 段无下划线，如 trae_999_test.yaml）
        # rename 检测（红蓝漏洞2修复）：--diff-filter=R 取新文件名检测，防 rename+--no-verify 绕过
        # 放在 new_py_files 过滤前：若 commit 只含 .yaml 无 .py，new_py_files 为空会提前
        # return True 跳过本检测，故须在 return 前完成 .yaml 命名检测。
        #
        # 真源一致性：_RULE_NAME_RE 与 validate_rule_frontmatter.py DIM-5 正则（line 209）保持一致
        # （修改此处 MUST 同步修改 validate_rule_frontmatter.py，两处共同构成 DIM-5 双层强制）。
        import re as _re
        _RULES_DIR_PREFIX = "docs/01_policies_and_standards/rules/"
        _RULE_NAME_RE = _re.compile(r"^trae_\d+_(.+)\.yaml$")
        # 收集 rules/ 下新增(A) 的 .yaml 文件
        new_rule_files: list[str] = []
        for f in staged_new:
            f_norm = f.replace("\\", "/")
            if (f_norm.startswith(_RULES_DIR_PREFIX)
                    and f_norm.endswith(".yaml")
                    and f_norm in commit_files_rel):
                new_rule_files.append(f_norm)
        # 收集 rules/ 下 rename(R) 的 .yaml 文件（检测 rename 后的新文件名）
        renamed_rule_files: list[str] = []
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
                            renamed_rule_files.append(new_path)
        except Exception:
            pass  # fail-open：rename 检测故障不阻断（新增检测已覆盖主要场景）
        all_rule_files = new_rule_files + renamed_rule_files
        bad_rule_names = []
        for f in all_rule_files:
            basename = f.rsplit("/", 1)[-1]
            m = _RULE_NAME_RE.match(basename)
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

        # 路径归一化为正斜杠 + 过滤 .py + 豁免 tests/（真源：commit_gate_registry.is_test_exempt）
        new_py_files = [
            f.replace("\\", "/") for f in staged_new
            if f.endswith(".py") and not is_test_exempt(f)
        ]
        if not new_py_files:
            return True, ""

        # 治本 2026-06-30：gateway 选择性提交（只提交 files_in_scope，其他 staged 文件 stash），
        # create_guard 应只检测 commit 文件中的新增 .py，不应检测其他 session 的 staged WIP。
        # commit_files_rel 已在函数开头计算（reconciler 检测 + token 检测复用），此处直接复用。
        new_py_files = [f for f in new_py_files if f in commit_files_rel]
        if not new_py_files:
            return True, ""

        # 2. 加载 capability registry YAML（真源：capability_lookup.REGISTRY_YAML）
        # 治本1（2026-06-30）：YAML 不可达改 fail-closed——registry 是 creation_token 真源，
        # 缺失/解析失败=检测器失效，fail-open 会漏放未登记 .py（红蓝：删 registry 绕过 token 检查）。
        # 对标 directory_contract_gate.py L105-107 fail-closed。配套治本1② registry 入 RULES_MANIFEST
        # 防"删 registry 绕过"在裸 commit 路径被 C 层检测。
        # import 放 try 外（代码级故障不捕获，由 check_all 的 try-except 兜底为 fail-closed）。
        from zephyr.governance.capability_lookup import REGISTRY_YAML

        if not REGISTRY_YAML.exists():
            return False, (
                f"CREATE-GUARD fail-closed: capability registry 不可达（文件缺失: {REGISTRY_YAML}）。"
                f"禁止放行——防删 registry 绕过 creation_token 检查。"
                f"修复：git checkout HEAD -- {REGISTRY_YAML} 恢复 registry 后重试。"
            )
        try:
            import yaml
            data = yaml.safe_load(REGISTRY_YAML.read_text(encoding="utf-8"))
        except Exception as e:
            return False, (
                f"CREATE-GUARD fail-closed: capability registry 解析失败"
                f"({type(e).__name__}: {e})。禁止放行——registry 是 creation_token 真源，"
                f"语法错误=检测器失效。修复：修正 {REGISTRY_YAML} 的 YAML 语法后重试。"
            )

        if not isinstance(data, dict):
            return False, (
                f"CREATE-GUARD fail-closed: registry YAML 顶层非 dict（结构异常）。"
                f"禁止放行——结构异常=检测器失效。修复：检查 {REGISTRY_YAML} 顶层结构后重试。"
            )

        # 3. 构建 creation_tokens 文件索引（相对路径 → token 条目）
        tokens = data.get("creation_tokens", []) or []
        registered_files: set[str] = set()
        if isinstance(tokens, list):
            for entry in tokens:
                if not isinstance(entry, dict):
                    continue
                token_file = entry.get("file", "")
                if isinstance(token_file, str) and token_file:
                    registered_files.add(token_file.replace("\\", "/"))

        # 4. 检测新增 .py 文件是否登记了 creation_token
        unregistered = [f for f in new_py_files if f not in registered_files]
        if unregistered:
            return False, (
                f"无 creation_token，禁止造第二真源（trae_060 §2）: {unregistered}. "
                f"commit 新建 .py 文件前 MUST 在 capability_canonical_file_registry.yaml "
                f"的 creation_tokens 字段登记 token（声明创建意图 + 关联 capability）。"
                f"格式: - file: \"<相对路径>\"  token: \"auto-xxx\"  "
                f"created_by: \"session-xxx\"  capability: \"xxx\""
            )
        return True, ""

    return GateSpec(gate_id="CREATE-GUARD", check=_check, priority=60)
