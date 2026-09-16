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
"""
schema_file_exists_gate.py — SCHEMA-FILE-EXISTS block 门禁

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

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/s/schema_file_exists_gate.yaml
"""

from __future__ import annotations

import logging

import yaml

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _read_head_file,
    _read_staged_file,
    _repo_state_has_file,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_schema_file_exists_gate"]

# business_data_categories.yaml 真源路径（相对项目根）
_YAML_REL = "docs/03_modules/_cross_layer/database/business_data_categories.yaml"


def _schema_ref_pairs(content: str | None) -> list[tuple[str, str]]:
    """解析 YAML 内容中的非 null schema_file 引用，返回 (category_id, schema_file) 列表。

    解析失败/结构非 list → 空列表（fail-open，调用方语义=无引用可查）。
    """
    if not content:
        return []
    try:
        data = yaml.safe_load(content)
    except Exception:  # noqa: BLE001 — fail-open
        logger.warning("SCHEMA-FILE-EXISTS fail-open: YAML parse error")
        return []
    if not isinstance(data, list):
        return []  # fail-open: 非预期结构
    pairs: list[tuple[str, str]] = []
    for cat in data:
        if not isinstance(cat, dict):
            continue
        sf = cat.get("schema_file")
        if not sf or sf == "null":
            continue  # 合法：无独立 schema 文件
        pairs.append((str(cat.get("category_id", "?")), str(sf)))
    return pairs


def _dangling_refs(gateway, content: str | None, rev: str = "") -> set[tuple[str, str]]:
    """给定版本 YAML 内容中，仓库态（index 或 rev）不存在的 schema_file 引用集合。

    存在性观测面=git 仓库态（裁定#279 同盲区家族清偿，2026-09-17）：旧实现
    ``os.path.exists`` 判磁盘——序列化器落地 worktree 里"本批 staged 的新 schema
    文件未 checkout 到磁盘"会被误判悬空（假阳性），"他会话在途删除（磁盘没了但
    index/HEAD 还在）"会漏判。磁盘只作 git 不可达时的降级补充（helper 内置告警）。
    """
    return {
        (cid, sf)
        for cid, sf in _schema_ref_pairs(content)
        if not _repo_state_has_file(gateway, sf, rev=rev)
    }


def _check_schema_files_exist(
    gateway,
    project_root: str,
) -> list[str]:
    """校验 staged YAML 中所有非 null schema_file 引用的文件存在（兼容旧接口）。

    兼容保留：返回"staged(index) 版 YAML 的悬空引用"消息列表（观测面已升级为
    git 仓库态）。基线差分见闭包内 ``_dangling_refs`` 的 NOW−BASE 用法。

    Args:
        gateway: GitCommitGateway 实例。
        project_root: 项目根绝对路径（兼容旧签名；存在性判定已走仓库态）。

    Returns:
        违规消息列表（空=通过）。
    """
    del project_root  # 兼容旧签名；观测面=git 仓库态，不再直接用磁盘路径
    content = _read_staged_file(gateway, _YAML_REL)
    if not content:
        return []  # fail-open: YAML 未 staged 或 git show 失败

    return [
        f"  {cid}: schema_file='{sf}' 文件不在仓库态（声明层→存在层断裂）"
        for cid, sf in sorted(_dangling_refs(gateway, content))
    ]


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

        # 基线差分（裁定#279 同盲区家族清偿，2026-09-17）：悬空引用是 YAML 内容级违规，
        # 无基线时"HEAD 里早就悬空的引用"会挡住任何触碰该 YAML 的批次（他人欠账连坐）。
        # NOW(index)−BASE(HEAD) 只阻断本次新增；存量降级 warn 归属其责任人（宪法 §3.4）。
        now_missing = _dangling_refs(gateway, _read_staged_file(gateway, _YAML_REL))
        if not now_missing:
            return True, ""
        base_missing = _dangling_refs(gateway, _read_head_file(gateway, _YAML_REL), rev="HEAD")
        introduced = sorted(now_missing - base_missing)
        inherited = sorted(now_missing & base_missing)
        if inherited:
            logger.warning(
                "SCHEMA-FILE-EXISTS: %d 项存量悬空引用（HEAD 基线已在，非本次引入）不阻断，"
                "归属其责任人（宪法 §3.4）: %s",
                len(inherited),
                "; ".join(f"{cid}->{sf}" for cid, sf in inherited[:5]),
            )
        violations = [
            f"  {cid}: schema_file='{sf}' 文件不在仓库态（声明层→存在层断裂）"
            for cid, sf in introduced
        ]

        if violations:
            detail = (
                "SCHEMA-FILE-EXISTS (block)：schema_file 引用悬空（本次新增）\n"
                "  违反 SSoT 三层一致性（声明层→存在层断裂）"
                "（#ARCH-SSOT-REFERENCE-INTEGRITY-001 Phase 1；观测面=git 仓库态，"
                "基线=HEAD，存量悬空不在此列）\n"
                "  修复：创建缺失的 schema 文件（同批 git add）或修正 schema_file 路径。\n"
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
