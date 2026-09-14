# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers (_build_own_scope, _norm_rel, _read_staged_file); zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.gate_auto_registrar（YAML 驱动自动注册）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 注册表结构硬化门禁——staged 版本必须 yaml.safe_load 通过 且 顶层根键唯一（yaml.compose
#   节点树判重，PyYAML 对重复根键静默取后者的盲区由本检查补上）；capability 注册表另有 di_seam_exemptions
#   末位+creation_tokens list 两断言。解析失败/结构破坏 → fail-closed 阻断（2026-09-14 立：同名键嵌套
#   creation_tokens(L883) 与顶层(L4987) 共存+EOF 尾追悬挂条目致全库解析炸四连（9ca0f62b95 修/1edeea81b4 修/
#   a5883d01 修/94aa4111 批内修）；2026-09-15 扩：data_asset_registry.yaml 双 datasets 根键（L752/755，
#   PyYAML 静默取后者，前段插条目被解析层忽略）随 st-patgov 合并批入库（件3），watch 面同步扩入+根键唯一
#   硬化；正确追加姿势=插既有根键的列表尾+提交前必验 parse；阻断与放行均落审计 .runtime/gate_audit/registry_yaml_parse.jsonl
# [MODIFY-GUARD] gate_id="REGISTRY-YAML-PARSE"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 失败/文件不可读 → fail-open 跳过（encoding 类 gate 覆盖）；staged 版本 YAML 解析失败/根键重复/capability 注册表结构破坏 → fail-closed 阻断（passed=False，报错附正确追加姿势教学）；审计写失败静默降级
# [TESTS] tests/governance/commit_gates/test_registry_yaml_parse_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L
# [TTL] permanent
"""registry_yaml_parse_gate.py — 注册表结构硬化门禁（防尾追悬挂/防重复根键）

背景（2026-09-14，同病四连）：
    capability_canonical_file_registry.yaml 顶层键序=[schema_version…capabilities,
    creation_tokens, di_seam_exemptions]——di_seam_exemptions 在 creation_tokens 之后，
    EOF 追加 token 条目必落错段（悬挂在 exemptions 之后），全库 YAML 解析炸：
    capability_lookup 挂、所有读该表的会话挂。2026-09-13/14 四次同病
    （pattern 会话修一次/sim 会话修一次/st-sopreorg 修两次），口头纪律+"提交前验 parse"
    的约定反复失守 → 硬化为 commit gate。

扩面（2026-09-15，图形库治理上报件3）：
    data_asset_registry.yaml 双 `datasets:` 根键（L752 空 null 键/L755 真块）——
    PyYAML 对重复根键静默取后者，人工/工具往前段插条目会被解析层无感忽略。
    合并批入库后，watch 面扩入该文件，并新增**顶层根键唯一**断言（yaml.compose
    节点树判重——safe_load 对重复键静默覆盖，节点树才同时保留两个），
    capability 注册表同享此检查。

检测逻辑（对 staged 文本，按档案分档）：
    capability_registry 档：
        1. yaml.safe_load 通过（解析炸直接阻断）
        2. 顶层根键唯一（yaml.compose 判重）
        3. 顶层 di_seam_exemptions 键存在且为末位键（尾追悬挂判别式）
        4. creation_tokens 键存在且为 list（结构走样拦截）
    data_asset_registry 档：
        1. yaml.safe_load 通过
        2. 顶层根键唯一

触发范围：staged 命中 _WATCH_FILES（capability_canonical_file_registry.yaml /
data_asset_registry.yaml，两个高频追加热注册表）——紧范围不加宽（净删防护由
REGISTRY-MASS-DELETION 负责，编码由 ENCODING-SAFETY 负责）。

无逃生标记：解析炸/根键重复的注册表没有"先合入再修"的合法场景——修复后在同一
commit 重新 staged 即可（gate 看的是 staged 终态）。

Usage::

    from zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate import (
        make_registry_yaml_parse_gate,
    )
    registry.register(make_registry_yaml_parse_gate())
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _build_own_scope,
    _norm_rel,
    _read_staged_file,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_registry_yaml_parse_gate"]

# 审计落点（.runtime/gate_audit/ 家族惯例）
_AUDIT_REL = ".runtime/gate_audit/registry_yaml_parse.jsonl"

# 热追加目标 watch 表 → 结构断言档案（紧范围不加宽；净删防护归 REGISTRY-MASS-DELETION，
# 编码归 ENCODING-SAFETY）。capability=全量断言；data_asset=parse+根键唯一。
_WATCH_FILES: dict[str, str] = {
    "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml": "capability_registry",
    "docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml": "data_asset_registry",
}

# 向后兼容别名（capability 注册表=首 watch 目标）
_WATCH_FILE = next(iter(_WATCH_FILES))

# 教学信息（阻断时给出正确姿势，治"每次重新发明修法"）
_TEACH = (
    "正确追加姿势：条目插在既有根键的列表尾（capability 注册表的 token 条目插 "
    "creation_tokens 列表尾=di_seam_exemptions: 行之前，注意 L883 有一个嵌套同名键勿错插），"
    "顶层根键禁止重复（PyYAML 静默取后者，前段插条目会被解析层无感忽略），"
    "插入后必须 yaml.safe_load 验证通过再提交"
)


def _audit(gateway, record: dict) -> None:
    """审计落盘（jsonl append；fail-open：写失败不阻断）。"""
    try:
        root = Path(getattr(gateway, "project_root", "."))
        audit_dir = root / ".runtime" / "gate_audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        with (audit_dir / "registry_yaml_parse.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001
        logger.debug("REGISTRY-YAML-PARSE audit write failed (non-blocking)", exc_info=True)


def _duplicate_root_keys(text: str) -> list[str]:
    """yaml.compose 节点树判重——safe_load 对重复根键静默取后者，节点树才同时保留两个。

    永不抛异常（compose 失败返回空=由 safe_load 断言兜底报解析失败）。
    """
    try:
        import yaml

        node = yaml.compose(text)
    except Exception:  # noqa: BLE001 — 解析失败由 _structural_issues 的 safe_load 断言报告
        return []
    if node is None or not hasattr(node, "value") or not isinstance(node.value, list):
        return []  # 非 MappingNode（Scalar/Sequence）→ 无根键可判重
    seen: set[str] = set()
    dups: list[str] = []
    for key_node, _ in node.value:
        k = str(getattr(key_node, "value", ""))
        if k in seen and k not in dups:
            dups.append(k)
        seen.add(k)
    return dups


def _structural_issues(text: str, profile: str) -> list[str]:
    """对 staged 文本做档案化断言 → 问题清单（空=通过）。永不抛异常。

    capability_registry 档：parse + 根键唯一 + exemptions 末位 + creation_tokens list。
    data_asset_registry 档：parse + 根键唯一。
    """
    issues: list[str] = []
    try:
        import yaml

        data = yaml.safe_load(text)
    except Exception as exc:  # noqa: BLE001 — 解析失败=阻断本体
        issues.append(f"yaml.safe_load 解析失败: {str(exc)[:160]}")
        return issues
    if not isinstance(data, dict):
        issues.append(f"顶层不是 mapping（实际 {type(data).__name__}）")
        return issues
    dups = _duplicate_root_keys(text)
    if dups:
        issues.append(f"顶层根键重复: {dups}（PyYAML 静默取后者——前段条目会被解析层无感忽略，必须合并为单键）")
    if profile == "capability_registry":
        keys = list(data.keys())
        if "di_seam_exemptions" not in keys:
            issues.append("顶层 di_seam_exemptions 键缺失")
        elif keys[-1] != "di_seam_exemptions":
            issues.append(f"di_seam_exemptions 不是末位顶层键（当前末位={keys[-1]!r}，键序={keys[-3:]}）")
        ct = data.get("creation_tokens")
        if not isinstance(ct, list):
            issues.append(f"creation_tokens 不是 list（实际 {type(ct).__name__}）")
    return issues


def make_registry_yaml_parse_gate() -> GateSpec:
    """构造 REGISTRY-YAML-PARSE pre-commit 门禁（priority=54）。

    staged 热注册表按档案断言（parse 通过/根键唯一/capability 注册表另查 exemptions
    末位+creation_tokens list）任一不满足 → fail-closed 阻断+教学信息；
    读失败/git 异常 → fail-open 跳过。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        try:
            result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=AM"])
            if result.returncode != 0:
                return True, ""  # fail-open：git 失败不阻断
            staged_yaml = [f.replace("\\", "/") for f in result.stdout.strip().splitlines() if f and f.endswith(".yaml")]
        except Exception:  # noqa: BLE001 — fail-open
            logger.warning("REGISTRY-YAML-PARSE fail-open: git diff 异常", exc_info=True)
            return True, ""

        session_id = kwargs.get("session_id")
        own_scope = _build_own_scope(gateway, files, session_id)
        if own_scope is not None:
            staged_yaml = [f for f in staged_yaml if _norm_rel(gateway, f) in own_scope]

        watched = [(f, profile) for f, profile in _WATCH_FILES.items() if f in staged_yaml]
        if not watched:
            return True, ""

        all_issues: list[tuple[str, list[str]]] = []
        for watch_file, profile in watched:
            staged_text = _read_staged_file(gateway, watch_file)
            if staged_text is None:
                continue  # fail-open：读失败（encoding 类 gate 覆盖）
            issues = _structural_issues(staged_text, profile)
            if issues:
                all_issues.append((watch_file, issues))

        _audit(
            gateway,
            {
                "timestamp": int(time.time()),
                "gate": "REGISTRY-YAML-PARSE",
                "action": "block" if all_issues else "pass",
                "session_id": session_id or "?",
                "files": {f: issues for f, issues in all_issues} if all_issues else [f for f, _ in watched],
            },
        )
        if not all_issues:
            return True, ""
        detail = "\n".join(
            line for f, issues in all_issues for line in (f"REGISTRY-YAML-PARSE: {f} 结构校验未过:", *(f"  - {i}" for i in issues))
        )
        msg = f"{detail}\n  {_TEACH}"
        logger.error(msg)
        return False, msg

    return GateSpec(
        gate_id="REGISTRY-YAML-PARSE",
        check=_check,
        priority=54,
    )
