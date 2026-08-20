# [BLUEPRINT] MOD-GOV_RULE_EXECUTION_PAIRING_GATE | docs/03_modules/_domain_governance/blueprint.md | §rule-execution-pairing-gate
# [MODULE] zephyr.gov_enforcement.commit_gates.rule_execution_pairing_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged trae_*.yaml 无 enforcement.paired_gate_id 时阻断；null 允许（文档型）；字符串须在 gate_registry 注册；[no-pairing:reason] 逃生通道；gate_registry 不可达 fail-open；YAML 解析失败 fail-closed
# [MODIFY-GUARD] gate_id="RULE-EXECUTION-PAIRING"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——YAML 解析异常 fail-closed；gate_registry 不可达 fail-open
# [TESTS] tests/governance/commit_gates/test_rule_execution_pairing_gate.py
# [A_module] module_id=MOD-GOV_RULE_EXECUTION_PAIRING_GATE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable  # noqa: blueprint-amodule-cross-check [BLUEPRINT]==[A_module] same module
# [TTL] permanent
r"""

rule_execution_pairing_gate.py — 规则-执行配对门禁（RULE-EXECUTION-PAIRING，Phase 3.5）

替代 RULE-DOC-FREEZE：规则 CAN 被编写，但 MUST 配对执行机制（gate_id）。
检测 A+B：A=staged trae_*.yaml 自动检测，B=commit message [rule-mod] 标记。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 提交上下文入参
#   fields: staged 文件列表 files + commit message（kwargs）
#   code: _check(gateway, files, **kwargs) L138-139
# - id: I2
#   name: staged 版 trae 规则文件内容
#   fields: docs/01_policies_and_standards/rules/trae_*.yaml 的 staged 文本（git show :<rel>）
#   code: gateway.run_git(["git", "show", f":{rel}"]) L113
# - id: I3
#   name: gate_registry.yaml 已注册 gate_id
#   fields: gates[].gate_id 集合
#   code: docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml L44-48
# 层: 算法
# - id: A1
#   name_zh: ① 触发与逃生判定
#   name_en: _check（前置段）
#   intro: 先看 commit message 有没有逃生通道或规则修改标记，决定要不要深入校验
#   desc: [no-pairing:<reason>] 直接放行 L141-142；无 trae 文件且无 [rule-mod] 标记放行 L147-148；否则进入校验
#   inputs: I1
#   outputs: 放行 / 继续校验
# - id: A2
#   name_zh: ② trae 规则文件筛查
#   name_en: _find_trae_files
#   intro: 从 staged 文件列表里筛出 trae_*.yaml 规则文件的相对路径
#   desc: os.path.relpath 归一化为正斜杠相对路径 → ^docs/01_policies_and_standards/rules/trae_.*\.yaml$ 正则匹配 L98-108
#   inputs: I1
#   outputs: trae_files 列表
# - id: A3
#   name_zh: ③ 单规则 enforcement 校验
#   name_en: _validate_single_rule
#   intro: 逐个读规则文件 staged 版本，检查 enforcement.paired_gate_id 字段存在且结构合法
#   desc: git show 读 staged 内容 → yaml.safe_load（语法错误 fail-closed）→ 顶层须 dict → enforcement 段须存在 → paired_gate_id 字段须存在 L110-136
#   inputs: A2 I2
#   outputs: violation 字符串或 None
#   invariant: YAML 解析失败 fail-closed；git show 失败跳过不误判
# - id: A4
#   name_zh: ④ paired_gate_id 合法性校验
#   name_en: _check_paired_gate_id
#   intro: 校验配对 gate_id 取值：null 放行，字符串/列表必须在 gate_registry 里注册过
#   desc: None→放行（文档型规则）；非 str/list→违规；registry 不可达→fail-open 放行；元素不在 known_gate_ids→违规 L66-92
#   inputs: A3 I3
#   outputs: (ok, detail)
#   invariant: gate_registry 不可达 fail-open
# - id: A5
#   name_zh: ⑤ GateSpec 组装
#   name_en: make_rule_execution_pairing_gate
#   intro: 把 _check 闭包打包成 RULE-EXECUTION-PAIRING 门禁规格，挂进提交门禁注册表
#   desc: GateSpec(gate_id="RULE-EXECUTION-PAIRING", check=_check, priority=61) L168；violations 聚合成阻断消息 L159-166
#   inputs: A1 A4
#   outputs: GateSpec
# 层: 输出
# - id: O1
#   name_zh: 配对门禁 GateSpec
#   name_en: GateSpec
#   intro: gate_id=RULE-EXECUTION-PAIRING、priority=61 的门禁规格，注册进 GitCommitGateway
#   downstream: git_commit_gateway.GitCommitGateway.__init__ MOD-INF-035（# [CONSUMERS] 头）
# - id: O2
#   name_zh: 门禁判定结果
#   name_en: tuple[bool, str]
#   intro: True=放行；False=硬阻断并附修复指引（加 paired_gate_id 或用 [no-pairing] 逃生通道）
#   invariant: check 永不抛异常
#   downstream: git_commit_gateway 提交阻断链路 MOD-INF-035
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# A2 --> A3
# I2 --> A3
# A3 --> A4
# I3 --> A4
# A1 --> A5
# A4 --> A5
# A5 --> O1
# A1 --> O2
# A4 --> O2
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
        gateway.project_root / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "gate_registry.yaml"
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
        return False, (f"paired_gate_id 类型无效({type(paired_gate_id).__name__})，须为 string | list[str] | null")
    if known_gate_ids is None:
        return True, ""
    invalid = [gid for gid in gate_ids_to_check if not isinstance(gid, str) or gid not in known_gate_ids]
    if invalid:
        return False, (f"paired_gate_id 含无效 gate_id: {invalid}. gate_id MUST 在 gate_registry.yaml 中注册。")
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
            result = gateway.run_git(["git", "show", f":{rel}"])
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
            return f"{rel}: enforcement 缺 paired_gate_id 字段。MUST 添加 paired_gate_id: <gate_id | null>。"
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
            v for v in (_validate_single_rule(gateway, rel, known_gate_ids) for rel in trae_files) if v is not None
        ]

        if violations:
            return False, (
                f"RULE-EXECUTION-PAIRING: {len(violations)} 条规则未配对执行机制"
                f"（Phase 3.5）: " + "; ".join(violations) + ". 修复：在 enforcement 段添加 paired_gate_id"
                "（gate_id 或 null），或用 [no-pairing:<reason>] 逃生通道。"
            )
        return True, ""

    return GateSpec(gate_id="RULE-EXECUTION-PAIRING", check=_check, priority=61)
