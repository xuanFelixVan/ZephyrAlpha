# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers (_build_own_scope, _norm_rel, _read_staged_file); zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.gate_auto_registrar（YAML 驱动自动注册）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] capability 注册表结构硬化门禁——staged 版本必须 yaml.safe_load 通过 且 di_seam_exemptions 存在且为末位顶层键 且 creation_tokens 为 list；解析失败/结构破坏 → fail-closed 阻断（2026-09-14 立：同名键嵌套 creation_tokens(L883) 与顶层(L4987) 共存+EOF 尾追悬挂条目致全库解析炸四连（9ca0f62b95 修/1edeea81b4 修/a5883d01 修/94aa4111 批内修），口头纪律不可靠故硬化；正确追加姿势=插 creation_tokens 列表尾（di_seam_exemptions 行之前）+提交前必验 parse；阻断与放行均落审计 .runtime/gate_audit/registry_yaml_parse.jsonl
# [MODIFY-GUARD] gate_id="REGISTRY-YAML-PARSE"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 失败/文件不可读 → fail-open 跳过（encoding 类 gate 覆盖）；staged 版本 YAML 解析失败或 di_seam_exemptions 非末位/缺失/creation_tokens 非 list → fail-closed 阻断（passed=False，报错附正确追加姿势教学）；审计写失败静默降级
# [TESTS] tests/governance/commit_gates/test_registry_yaml_parse_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L
# [TTL] permanent
"""registry_yaml_parse_gate.py — capability 注册表结构硬化门禁（防尾追悬挂第四道保险）

背景（2026-09-14，同病四连）：
    capability_canonical_file_registry.yaml 顶层键序=[schema_version…capabilities,
    creation_tokens, di_seam_exemptions]——di_seam_exemptions 在 creation_tokens 之后，
    EOF 追加 token 条目必落错段（悬挂在 exemptions 之后），全库 YAML 解析炸：
    capability_lookup 挂、所有读该表的会话挂。2026-09-13/14 四次同病
    （pattern 会话修一次/sim 会话修一次/st-sopreorg 修两次），口头纪律+"提交前验 parse"
    的约定反复失守 → 硬化为 commit gate。

检测逻辑（对 staged 版本，三断言全过才放行）：
    1. yaml.safe_load 通过（解析炸直接阻断）
    2. 顶层 di_seam_exemptions 键存在且为末位键（尾追悬挂的判别式——条目挂在
       exemptions 之后时 pyyaml 在映射内遇 '- ' 必炸； exemptions 被挪位也拦）
    3. creation_tokens 键存在且为 list（结构走样拦截）

触发范围：staged 命中 _WATCH_FILE（capability_canonical_file_registry.yaml，唯一
热追加目标）——紧范围不加宽（净删防护由 REGISTRY-MASS-DELETION 负责，编码由
ENCODING-SAFETY 负责）。

无逃生标记：解析炸的注册表没有"先合入再修"的合法场景——修复后在同一 commit 重新
staged 即可（gate 看的是 staged 终态）。

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

# 唯一热追加目标（紧范围；其余 catalogs YAML 的净删防护归 REGISTRY-MASS-DELETION）
_WATCH_FILE = "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml"

# 教学信息（阻断时给出正确姿势，治"每次重新发明修法"）
_TEACH = (
    "正确追加姿势：token/条目插在顶层 creation_tokens 列表尾"
    "（即 di_seam_exemptions: 行之前，注意 L883 有一个嵌套同名键勿错插），"
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


def _structural_issues(text: str) -> list[str]:
    """对 staged 文本做三断言 → 问题清单（空=通过）。永不抛异常。"""
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

    staged capability 注册表三断言（parse 通过/exemptions 末位/creation_tokens list）
    任一不满足 → fail-closed 阻断+教学信息；读失败/git 异常 → fail-open 跳过。
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

        if not any(f == _WATCH_FILE for f in staged_yaml):
            return True, ""

        staged_text = _read_staged_file(gateway, _WATCH_FILE)
        if staged_text is None:
            return True, ""  # fail-open：读失败（encoding 类 gate 覆盖）

        issues = _structural_issues(staged_text)
        _audit(
            gateway,
            {
                "timestamp": int(time.time()),
                "gate": "REGISTRY-YAML-PARSE",
                "action": "block" if issues else "pass",
                "session_id": session_id or "?",
                "file": _WATCH_FILE,
                "issues": issues,
            },
        )
        if not issues:
            return True, ""
        msg = f"REGISTRY-YAML-PARSE: {_WATCH_FILE} 结构校验未过:\n" + "\n".join(f"  - {i}" for i in issues) + f"\n  {_TEACH}"
        logger.error(msg)
        return False, msg

    return GateSpec(
        gate_id="REGISTRY-YAML-PARSE",
        check=_check,
        priority=54,
    )
