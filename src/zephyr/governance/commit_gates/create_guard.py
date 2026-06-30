# [BLUEPRINT] MOD-GOV-create_guard | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §create-guard
# [MODULE] zephyr.governance.commit_gates.create_guard
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.commit_gate_registry (GateSpec), zephyr.governance.capability_lookup (REGISTRY_YAML)
# [CONSUMERS] zephyr.governance.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 硬阻断——staged 新增 .py 文件无 creation_token 时阻断 commit（passed=False）；tests/ 豁免（测试非能力真源，对标 capability_overlap_gate 设计）；YAML 不可达时 fail-open 放行（registry 故障不应卡死 commit 工作流）；token 匹配按相对路径精确比对（路径归一化为正斜杠）
# [MODIFY-GUARD] gate_id="CREATE-GUARD"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——YAML 读取/解析异常降级为 fail-open 放行（不阻断 commit，registry 故障不应卡死工作流）；git diff 异常降级为 fail-open 放行
# [TESTS] tests/test_create_guard.py
# [A_module] module_id=MOD-GOV-create_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""create_guard.py — 新建 .py 文件 creation_token 阻断门禁（CREATE-GUARD，2026-06-30 治本）

检测 staged 新增 .py 文件是否在 capability_canonical_file_registry.yaml 的
creation_tokens 字段登记。无 token 的 .py 文件 → 硬阻断，提示"无 creation_token，
禁止造第二真源（trae_060 §2）"。有 token 的 .py 文件 → 放行。

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
   capability_overlap_gate 的 tests/ 豁免设计。包含 tests/ 会要求每个测试文件
   登记 token，过度 disruptive 且无 SSoT 收益。
3. **fail-open（YAML 不可达）**：YAML 缺失/解析失败时放行——registry 故障不应
   卡死 commit 工作流（对标 capability_overlap_gate 的 fail-open 设计）。
   YAML 可达但文件无 token 时才硬阻断。
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

from zephyr.governance.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_create_guard"]


def make_create_guard() -> GateSpec:
    """构造新建 .py 文件 creation_token 阻断门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="CREATE-GUARD", priority=60)。
        priority=60——在 HELD-OVERLAP(50) 之后、CAPABILITY-OVERLAP(200) 之前执行。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 仅关心 staged 新增 .py 文件（--diff-filter=A）
        try:
            diff_result = gateway._run_git(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=A"]
            )
            if diff_result.returncode != 0:
                return True, ""  # fail-open：git diff 失败不阻断
            staged_new = diff_result.stdout.strip().splitlines()
        except Exception:
            return True, ""  # fail-open

        # 路径归一化为正斜杠 + 过滤 .py + 豁免 tests/（测试非能力真源）
        new_py_files = [
            f.replace("\\", "/") for f in staged_new
            if f.endswith(".py") and not f.replace("\\", "/").startswith("tests/")
        ]
        if not new_py_files:
            return True, ""

        # 治本 2026-06-30：gateway 选择性提交（只提交 files_in_scope，其他 staged 文件 stash），
        # create_guard 应只检测 commit 文件中的新增 .py，不应检测其他 session 的 staged WIP
        commit_files_rel: set[str] = set()
        for f in files:
            try:
                rel = os.path.relpath(f, str(gateway.project_root)).replace("\\", "/")
                commit_files_rel.add(rel)
            except (ValueError, OSError):
                continue
        new_py_files = [f for f in new_py_files if f in commit_files_rel]
        if not new_py_files:
            return True, ""

        # 2. 加载 capability registry YAML（真源：capability_lookup.REGISTRY_YAML）
        try:
            from zephyr.governance.capability_lookup import REGISTRY_YAML
            if not REGISTRY_YAML.exists():
                return True, ""  # fail-open：registry 不存在不阻断
            import yaml
            data = yaml.safe_load(REGISTRY_YAML.read_text(encoding="utf-8"))
        except Exception:
            return True, ""  # fail-open：YAML 解析失败不阻断

        if not isinstance(data, dict):
            return True, ""

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
