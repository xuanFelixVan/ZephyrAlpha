# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.schema_file_exists_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); zephyr.gov_enforcement.commit_gates._diff_helpers (_read_staged_file)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] block——当 business_data_categories.yaml 被 staged 时，校验所有非 null schema_file 引用的文件必须存在；命中返回 passed=False + detail（阻断 commit）；fail-open（YAML 解析失败/git show 不可达不阻断）；检出违规则 fail-closed（passed=False）
# [MODIFY-GUARD] gate_id="SCHEMA-FILE-EXISTS"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——YAML/git/文件系统异常降级为 fail-open（passed=True）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_schema_file_exists_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH] ARCH-SSOT-REFERENCE-INTEGRITY-001
"""schema_file_exists_gate.py — SCHEMA-FILE-EXISTS block 门禁

裁定 #ARCH-SSOT-REFERENCE-INTEGRITY-001 Phase 1：SSoT 存在性强制。

第一性原理根因（SSoT 三层模型断裂）
------------------------------------
SSoT 三层模型（声明层/存在层/消费层）缺少存在性强制：
  - 声明层（business_data_categories.yaml schema_file 字段）可引用任意路径
  - 存在层（磁盘文件）无对应文件时不报错
  - 消费层（代码 import）按声明层读取时才运行时崩溃

Phase 0 止血修复了 7/8 悬空引用（87.5% SSoT 破裂率），但无 gate 防止
未来回归。本 gate 建立"存在性强制"层——commit 时校验 YAML schema_file
引用的文件必须存在。

检测逻辑
--------
1. 仅当 business_data_categories.yaml 被 staged 时触发
2. 读取 staged 版本的 YAML 内容（git show :path，非 HEAD）
3. 遍历所有 category 条目
4. 对非 null 的 schema_file，校验文件在 project_root 下存在
5. 任一引用悬空 → 阻断 commit

设计权衡
--------
1. **block（非 warn）**：悬空引用是确定性 bug，不是风险——对标
   TABLE-NAME-REGISTRY block 设计。
2. **只检测 staged YAML**：只在该文件被修改时触发，不影响其他 commit 性能。
3. **fail-open on parse error**：YAML 解析失败/git show 不可达不阻断
   （环境异常非违规，对标 table_name_registry_gate）。
4. **schema_file=null 跳过**：null 表示"该品类无独立 schema 文件"
   （如元数据表），合法。
5. **priority=121**：在 TABLE-NAME-REGISTRY(120) 之后，作为最新的 block gate。
6. **复用 _diff_helpers._read_staged_file**：DRY，与 table_name_registry_gate
   的 tasks.yaml 检测模式一致。

Usage::

    from zephyr.gov_enforcement.commit_gates.schema_file_exists_gate import (
        make_schema_file_exists_gate,
    )
    registry.register(make_schema_file_exists_gate())
"""

from __future__ import annotations

import logging
import os

import yaml

from zephyr.gov_enforcement.commit_gates._diff_helpers import _read_staged_file
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_schema_file_exists_gate"]

# business_data_categories.yaml 真源路径（相对项目根）
_YAML_REL = "docs/03_modules/_cross_layer/database/business_data_categories.yaml"


def _check_schema_files_exist(
    gateway,
    project_root: str,
) -> list[str]:
    """校验 staged YAML 中所有非 null schema_file 引用的文件存在。

    Args:
        gateway: GitCommitGateway 实例。
        project_root: 项目根绝对路径。

    Returns:
        违规消息列表（空=通过）。
    """
    content = _read_staged_file(gateway, _YAML_REL)
    if not content:
        return []  # fail-open: YAML 未 staged 或 git show 失败

    try:
        data = yaml.safe_load(content)
    except Exception:  # noqa: BLE001 — fail-open
        logger.warning("SCHEMA-FILE-EXISTS fail-open: YAML parse error")
        return []

    if not isinstance(data, list):
        return []  # fail-open: 非预期结构

    violations: list[str] = []
    for cat in data:
        if not isinstance(cat, dict):
            continue
        sf = cat.get("schema_file")
        if not sf or sf == "null":
            continue  # 合法：无独立 schema 文件
        full_path = os.path.join(project_root, sf)
        if not os.path.exists(full_path):
            cid = cat.get("category_id", "?")
            violations.append(f"  {cid}: schema_file='{sf}' 文件不存在（声明层→存在层断裂）")

    return violations


def make_schema_file_exists_gate() -> GateSpec:
    """构造 SCHEMA-FILE-EXISTS pre-commit block 门禁（priority=121）。

    当 business_data_categories.yaml 被 staged 时，校验所有非 null
    schema_file 引用的文件必须存在。命中返回 (False, detail) 阻断 commit。

    裁定 #ARCH-SSOT-REFERENCE-INTEGRITY-001 Phase 1：SSoT 存在性强制。

    Returns:
        GateSpec(gate_id="SCHEMA-FILE-EXISTS", priority=121)。
        block：检出违规返回 (False, detail)，阻断 commit。
    """

    def _check(gateway, files: list[str], **_kwargs) -> tuple[bool, str]:
        # 仅当 YAML 被 staged 时触发
        normalized = [f.replace("\\", "/") for f in files]
        if _YAML_REL not in normalized:
            return True, ""

        project_root = str(gateway.project_root)
        violations = _check_schema_files_exist(gateway, project_root)

        if violations:
            detail = (
                "SCHEMA-FILE-EXISTS (block)：schema_file 引用悬空\n"
                "  违反 SSoT 三层一致性（声明层→存在层断裂）"
                "（#ARCH-SSOT-REFERENCE-INTEGRITY-001 Phase 1）\n"
                "  修复：创建缺失的 schema 文件或修正 schema_file 路径。\n"
                + "\n".join(violations[:30])
                + (f"\n  ...(+{len(violations) - 30} more)" if len(violations) > 30 else "")
            )
            logger.error("SCHEMA-FILE-EXISTS gate block:\n%s", detail)
            return False, detail
        return True, ""

    return GateSpec(
        gate_id="SCHEMA-FILE-EXISTS",
        check=_check,
        priority=121,
    )
