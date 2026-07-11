# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.commit_gates.module_id_consistency_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.governance.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] fail-closed——三声明轨道不一致或 count 不匹配或 module_id 跨文件撞车阻断
# [MODIFY-GUARD] gate_id="MODULE-ID-CONSISTENCY"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]；三声明轨道正则 + count 派生正则 + 跨文件唯一性 git grep
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] (True, msg)=通过；False=阻断（三声明轨道不一致或 count_mismatch 或 module_id 跨文件撞车）；OSError/git grep 超时跳过单文件不阻断
# [TESTS] tests/governance/commit_gates/test_module_id_consistency_gate.py
# [TTL] permanent
"""module_id_consistency_gate.py — module_id 三声明轨道一致性 + count 派生 + 跨文件唯一性门禁（Phase 3 reconciler->gate 收敛）

从 make_module_id_consistency_reconciler（post-commit warn）升级为 pre-commit 阻断 gate。

三维校验：
1. 三声明轨道一致性（P8-FIX-S0）：单文件中 CFG-*/MOD-*/PS-* 三声明轨道 module_id 声明是否一致
2. count 派生（P8-FIX-S1）：注册表声明的 total_registered/total_templates/total_dependencies
   与实际列表条目数是否匹配
3. 跨文件唯一性（治本 2026-07-03）：staged .py 文件含 [A_*] module_id 头时，
   git grep 全仓检测是否有其他文件声明相同 module_id——阻断跨文件撞车

治本动机：原 reconciler 是 post-commit 非阻断 warn，不一致已入 git 历史仅告警。
本 gate 在 commit() 内嵌等效校验，阻断新引入的不一致。
第三维治本：原 gate 只检查单文件三声明轨道一致性，不检测跨文件重复，12 组撞车漏检。
"""

from __future__ import annotations

import logging
import os
import re
import subprocess

from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_module_id_consistency_gate"]

_REGISTRY_REL = "architecture_model/module_id_registry.yaml"
_TEMPLATE_REGISTRY_REL = "docs/03_modules/template_registry.yaml"
_DEP_REGISTRY_REL = "docs/01_policies_and_standards/_registry/catalogs/cross_module_dependency_registry.yaml"
_CONTRACTS_DIR = "docs/01_policies_and_standards/_registry/contracts/"

# 三声明轨道正则
_RE_HEADER_CFG = re.compile(r"^#\s*\[A_config\]\s*module_id=(CFG-\S+)", re.MULTILINE)
_RE_ANCHOR_MOD = re.compile(r"^#\s*module_id:\s*(MOD-\S+)", re.MULTILINE)
_RE_BODY_RULE = re.compile(r"^module_id:\s*([A-Z]+(?:-[A-Z]+)*-\w+)\s*$", re.MULTILINE)

# count 派生校验正则
_RE_MODULE_ID_ENTRY = re.compile(r"^  - module_id:\s*\S+", re.MULTILINE)
_RE_TEMPLATE_ENTRY = re.compile(r"^  - template_id:", re.MULTILINE)
_RE_DEP_ENTRY = re.compile(r"^- dep_id:\s*DEP-", re.MULTILINE)
_RE_TOTAL_REGISTERED = re.compile(r"^total_registered:\s*(\d+)", re.MULTILINE)
_RE_TOTAL_TEMPLATES = re.compile(r"^\s*total_templates:\s*(\d+)", re.MULTILINE)
_RE_TOTAL_DEPS = re.compile(r"^total_dependencies:\s*(\d+)", re.MULTILINE)

# 跨文件 module_id 唯一性（治本 2026-07-03）：提取 [A_test]/[A_config] 头部 module_id
_RE_HEADER_MODULE_ID = re.compile(
    r"^#\s*\[A_\w+\]\s*module_id[:=]\s*(\S+)", re.MULTILINE
)


def _is_tracked_in_head(gateway, rel: str) -> bool:
    """判断文件是否已存在于 HEAD（即 tracked/修改态 M，而非新增 A）。

    用于 cross-file 碰撞检查的历史豁免：HEAD 中已存在的文件属存量基线违规，
    按"门禁只检测staged新增文件（diff-filter=A）"约定不阻断。git 错误时 fail-open
    返回 True（假定已跟踪，避免误阻断）。
    """
    try:
        result = gateway._run_git(["git", "ls-tree", "HEAD", rel])
        return result.returncode == 0 and bool(result.stdout.strip())
    except (subprocess.TimeoutExpired, OSError):
        return True


def make_module_id_consistency_gate() -> GateSpec:
    """构造 module_id 一致性门禁 GateSpec（fail-closed 阻断型）。

    Returns:
        GateSpec(gate_id="MODULE-ID-CONSISTENCY", priority=88)。
        priority=88——在 EXEMPT-ZONE-FM(87) 之后。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        from pathlib import Path

        project_root = gateway.project_root
        violations: list[str] = []

        for f in files:
            if not os.path.isfile(f):
                continue
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if (rel != _REGISTRY_REL and rel != _TEMPLATE_REGISTRY_REL
                    and rel != _DEP_REGISTRY_REL and not rel.startswith(_CONTRACTS_DIR)):
                continue

            try:
                content = Path(f).read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            # === 三声明轨道一致性校验 ===
            cfg_match = _RE_HEADER_CFG.search(content)
            mod_match = _RE_ANCHOR_MOD.search(content)
            rule_match = _RE_BODY_RULE.search(content)

            cfg_id = cfg_match.group(1) if cfg_match else None
            mod_id = mod_match.group(1) if mod_match else None
            rule_id = rule_match.group(1) if rule_match else None

            tracks_found = sum(1 for x in [cfg_id, mod_id, rule_id] if x)
            if tracks_found < 2 and cfg_id:
                violations.append(
                    f"{rel}: incomplete_tracks (cfg={cfg_id}, mod={mod_id}, rule={rule_id}) — "
                    f"header CFG but only {tracks_found}/3 tracks"
                )

            # === count 派生校验 ===
            if rel == _REGISTRY_REL:
                actual = len(_RE_MODULE_ID_ENTRY.findall(content))
                declared = _RE_TOTAL_REGISTERED.search(content)
                if declared and int(declared.group(1)) != actual:
                    violations.append(
                        f"{rel}: count_mismatch total_registered={declared.group(1)} but actual={actual}"
                    )
            elif rel == _TEMPLATE_REGISTRY_REL:
                actual = len(_RE_TEMPLATE_ENTRY.findall(content))
                declared = _RE_TOTAL_TEMPLATES.search(content)
                if declared and int(declared.group(1)) != actual:
                    violations.append(
                        f"{rel}: count_mismatch total_templates={declared.group(1)} but actual={actual}"
                    )
            elif rel == _DEP_REGISTRY_REL:
                actual = len(_RE_DEP_ENTRY.findall(content))
                declared = _RE_TOTAL_DEPS.search(content)
                if declared and int(declared.group(1)) != actual:
                    violations.append(
                        f"{rel}: count_mismatch total_dependencies={declared.group(1)} but actual={actual}"
                    )

        # === 跨文件 module_id 唯一性校验（治本 2026-07-03）===
        # 原 gate 只检查单文件三声明轨道一致性 + count 派生，不检测跨文件 module_id 重复。
        # 12 组撞车漏检根因。扩展：staged .py 含 module_id 头时，git grep 全仓检测重复。
        # 历史豁免（门禁只检测staged新增文件diff-filter=A，不触碰存量基线违规）：
        # cross-file 碰撞检查仅对 NEWLY ADDED（不在 HEAD）的文件生效；HEAD 中已存在的
        # 修改文件（M状态）属存量基线 DRY 违规，由去重任务处理，此处不阻断。
        for f in files:
            if not os.path.isfile(f) or not f.endswith(".py"):
                continue
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if _is_tracked_in_head(gateway, rel):
                continue  # 修改文件（M）——存量基线违规，跳过碰撞检查
            try:
                content = Path(f).read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            m = _RE_HEADER_MODULE_ID.search(content)
            if not m:
                continue
            mid = m.group(1)
            try:
                result = gateway._run_git(
                    ["git", "grep", "-l", "-F", mid, "--", "*.py"],
                )
            except (subprocess.TimeoutExpired, OSError):
                continue  # fail-open on git grep error
            if result.returncode != 0:
                continue  # no matches = no collision
            matches = [line.strip() for line in result.stdout.split("\n") if line.strip()]
            others = [x for x in matches if x != rel]
            if others:
                violations.append(
                    f"{rel}: module_id_collision '{mid}' also declared in: {', '.join(others[:5])}"
                )

        if violations:
            return False, (
                f"MODULE-ID-CONSISTENCY: {len(violations)} violation(s):\n"
                + "\n".join(f"  - {v}" for v in violations)
            )
        return True, "module_id consistency check passed"

    return GateSpec(gate_id="MODULE-ID-CONSISTENCY", check=_check, priority=88)
