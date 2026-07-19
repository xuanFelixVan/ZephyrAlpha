# [BLUEPRINT] MOD-GOV_rule_execution_pairing_gate | docs/03_modules/_domain_governance/blueprint.md | §rule-execution-pairing-gate
# [MODULE] zephyr.gov_enforcement.commit_gates.rule_execution_pairing_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 硬阻断——staged trae_*.yaml 无 enforcement.paired_gate_id 时阻断；null 允许（文档型）；字符串须在 gate_registry 注册；[no-pairing:reason] 逃生通道；gate_registry 不可达 fail-open；YAML 解析失败 fail-closed
# [MODIFY-GUARD] gate_id="RULE-EXECUTION-PAIRING"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——YAML 解析异常 fail-closed；gate_registry 不可达 fail-open
# [TESTS] tests/governance/commit_gates/test_rule_execution_pairing_gate.py
# [A_module] module_id=MOD-GOV-rule_execution_pairing_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""rule_execution_pairing_gate.py — 规则-执行配对门禁（RULE-EXECUTION-PAIRING，Phase 3.5）

替代 RULE-DOC-FREEZE：规则 CAN 被编写，但 MUST 配对执行机制（gate_id）。
检测 A+B：A=staged trae_*.yaml 自动检测，B=commit message [rule-mod] 标记。
"""

from __future__ import annotations

import logging
import os
import re

import yaml

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_rule_execution_pairing_gate"]

_TRAE_RULE_RE = re.compile(r"^docs/01_policies_and_standards/rules/trae_.*\.yaml$")
_RULE_MOD_TAG_RE = re.compile(r"\[rule-mod\]")
_NO_PAIRING_RE = re.compile(r"\[no-pairing:[^\]]+\]")


def _load_known_gate_ids(gateway) -> "set[str] | None":
    """加载 gate_registry.yaml 中所有 gate_id（fail-open）。"""
    registry_path = (
        gateway.project_root
        / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
        / "gate_registry.yaml"
    )
    if not registry_path.exists():
        return None
    try:
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        logger.warning("RULE-EXECUTION-PAIRING: gate_registry 解析失败(%s)，fail-open", e)
        return None
    if not isinstance(data, dict):
        return None
    gates = data.get("gates", []) or []
    ids = set()
    for g in gates:
        if isinstance(g, dict) and g.get("gate_id"):
            ids.add(g["gate_id"])
    return ids if ids else None


def _check_paired_gate_id(paired_gate_id, known_gate_ids):
    """验证 paired_gate_id 值是否合法。返回 (ok, detail)。"""
    if paired_gate_id is None:
        return True, ""
    if isinstance(paired_gate_id, str):
        gate_ids_to_check = [paired_gate_id]
    elif isinstance(paired_gate_id, list):
        if not paired_gate_id:
            return True, ""
        gate_ids_to_check = paired_gate_id
    else:
        return False, (
            f"paired_gate_id 类型无效({type(paired_gate_id).__name__})，"
            f"须为 string | list[str] | null"
        )
    if known_gate_ids is None:
        return True, ""
    invalid = [
        gid for gid in gate_ids_to_check
        if not isinstance(gid, str) or gid not in known_gate_ids
    ]
    if invalid:
        return False, (
            f"paired_gate_id 含无效 gate_id: {invalid}. "
            f"gate_id MUST 在 gate_registry.yaml 中注册。"
        )
    return True, ""


def make_rule_execution_pairing_gate() -> GateSpec:
    """构造规则-执行配对门禁 GateSpec。"""

    def _find_trae_files(files, project_root):
        """从文件列表中筛选 trae_*.yaml 相对路径。"""
        trae_files = []
        for f in files:
            try:
                rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            except (ValueError, OSError):
                continue
            if _TRAE_RULE_RE.match(rel):
                trae_files.append(rel)
        return trae_files

    def _validate_single_rule(gateway, rel, known_gate_ids):
        """验证单个 trae 规则文件的 paired_gate_id。返回 violation 字符串或 None。"""
        try:
            result = gateway._run_git(["git", "show", f":{rel}"])
        except Exception as e:  # noqa: BLE001
            logger.warning("RULE-EXECUTION-PAIRING: git show :%s 失败(%s)，跳过", rel, e)
            return None
        if result.returncode != 0:
            return None
        try:
            data = yaml.safe_load(result.stdout)
        except yaml.YAMLError as e:
            return f"{rel}: YAML 语法错误({e})，规则文件无效"
        if not isinstance(data, dict):
            return f"{rel}: YAML 顶层非 dict，规则文件结构异常"
        enforcement = data.get("enforcement")
        if not isinstance(enforcement, dict):
            return f"{rel}: 缺 enforcement 段，MUST 添加 enforcement.paired_gate_id"
        if "paired_gate_id" not in enforcement:
            return (
                f"{rel}: enforcement 缺 paired_gate_id 字段。"
                f"MUST 添加 paired_gate_id: <gate_id | null>。"
            )
        ok, detail = _check_paired_gate_id(enforcement["paired_gate_id"], known_gate_ids)
        if not ok:
            return f"{rel}: {detail}"
        return None

    def _check(gateway, files, **kwargs):
        commit_message = kwargs.get("commit_message", "") or ""

        if _NO_PAIRING_RE.search(commit_message):
            return True, "no-pairing escape hatch active"

        trae_files = _find_trae_files(files, gateway.project_root)
        rule_mod_triggered = bool(_RULE_MOD_TAG_RE.search(commit_message))

        if not trae_files and not rule_mod_triggered:
            return True, ""

        known_gate_ids = _load_known_gate_ids(gateway)
        violations = [
            v for v in (
                _validate_single_rule(gateway, rel, known_gate_ids)
                for rel in trae_files
            )
            if v is not None
        ]

        if violations:
            return False, (
                f"RULE-EXECUTION-PAIRING: {len(violations)} 条规则未配对执行机制"
                f"（Phase 3.5）: " + "; ".join(violations)
                + ". 修复：在 enforcement 段添加 paired_gate_id"
                f"（gate_id 或 null），或用 [no-pairing:<reason>] 逃生通道。"
            )
        return True, ""

    return GateSpec(gate_id="RULE-EXECUTION-PAIRING", check=_check, priority=61)
