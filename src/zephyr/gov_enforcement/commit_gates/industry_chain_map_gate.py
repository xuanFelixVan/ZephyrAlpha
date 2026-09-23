# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §industry_chain_map_gate
# [MODULE] zephyr.gov_enforcement.commit_gates.industry_chain_map_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] yaml（外部）；zephyr.gov_enforcement.registry_alignment（产业链字典四边核查）
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__（经 in_process_gate_registry.yaml 自动注册）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 硬阻断（确定性校验）——产业链全景图（图 8）git 侧工件触发：①industry_graph_field_dictionary.yaml 结构四边（表集=DDL ig_* 表集/每表字段=DDL 列/validated_by 引擎存在性/enum vocab 引用）error>0→阻断 ②chainmap_cluster_names.yaml 键格式 C\\d+ 与族名≤6 字违规→阻断；DDL/引擎解析失败降 warning 不阻断（环境异常 fail-open）；数据层（PG 产业链表）质量归 graph_quality_check.py（align_all 第七节），本 gate 只管 git 侧工件同 commit 原子性
# [MODIFY-GUARD] gate_id="INDUSTRY-CHAIN-MAP"；触发文件清单 _TRIGGER_FILES 变更须同步 alignment_checklist §3 图 8 行
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 校验函数异常=warning 放行（fail-open，对标 BUSINESS-REGISTRY depgraph 子检查）；字典 YAML 损坏=阻断（fail-closed，库损坏须先修）
# [TESTS] tests/governance/test_registry_alignment_layer2.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-ALIGN-NAMING-001
# [CREATION-TOKEN] industry-chain-map-gate-20260911
"""industry_chain_map_gate.py — 产业链全景图 git 侧工件门禁（INDUSTRY-CHAIN-MAP，priority=147）

    # [ALGO_FLOW]
    # 层: 输入
    # - id: I1
    #   name: 模块内部数据
    #   fields: 无公共形参/无再导出（AST 事实）
    #   code: industry_chain_map_gate.py
    # 层: 算法
    # - id: A1
    #   name_zh: ① make_industry_chain_map_gate
    #   name_en: make_industry_chain_map_gate
    #   intro: 构造聚合门禁 GateSpec（st-gslim-20260923 P4 并入 MAP-ALIGNMENT）。
    #   desc: 构造 GateSpec。 Returns: GateSpec(gate_id="MAP-ALIGNMENT", priority=141)。
    #   inputs: 无参数
    #   outputs: GateSpec
    # 层: 输出
    # - id: O1
    #   name_zh: GateSpec
    #   name_en: GateSpec
    #   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
    #   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
    #
    # 边:
    # I1 --> A1
    # A1 --> O1
    # [/ALGO_FLOW]

病根（第一性原理）
-----------------
产业链图谱（图 8）此前在七图对齐体系之外：数据层有 graph_quality_check.py（S1-S21
合格线引擎）但只按需手跑；git 侧工件（域字段字典/簇族名词表/DDL 真源）变更时
**无任何 commit 门禁**强制字典↔DDL↔引擎三方一致——字典漏列/DDL 加列不同步/
validated_by 引用不存在的检查项均可静默入库。本 gate 把图 8 的 git 侧工件纳入
commit 阻断（对齐 checklist §3 图 8 行），数据层质量由 align_all 第七节恒跑
graph_quality_check 覆盖——两层正交，共同闭环图 8 对齐。

触发文件（git 侧工件，数据层 PG 表不在 git 内不触发）：
- docs/01_policies_and_standards/_registry/catalogs/industry_graph_field_dictionary.yaml
- config/chainmap_cluster_names.yaml
- scripts/industry_graph/apply_industry_graph_ddl.py（DDL-as-Code 真源）

Usage::

    from zephyr.gov_enforcement.commit_gates.industry_chain_map_gate import make_industry_chain_map_gate
    registry.register(make_industry_chain_map_gate())
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Final

import yaml

from zephyr.gov_enforcement.commit_gates._diff_helpers import _norm_rel
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__: Final = ["make_industry_chain_map_gate"]

_REPO_ROOT = Path(__file__).resolve().parents[4]

_TRIGGER_FILES: Final[frozenset[str]] = frozenset(
    {
        "docs/01_policies_and_standards/_registry/catalogs/industry_graph_field_dictionary.yaml",
        "config/chainmap_cluster_names.yaml",
        "scripts/industry_graph/apply_industry_graph_ddl.py",
    }
)

_CLUSTER_KEY_PAT = re.compile(r"^C\d+$")

# 触发面 normcase 归一（commit() 传入绝对路径——git_commit_gateway abspath；朴素
# 反斜杠替换对绝对路径恒 miss=本 gate 注册以来生产链路零触发实证，2026-09-13
# FACTORY-MAP 实弹暴露同款缺陷连带修复；与 _norm_rel 输出同域可比，
# 学 DECISION-MAP _MAP_INPUT_YAML 先例）
_TRIGGER_FILES_NORMCASE: Final[frozenset[str]] = frozenset(
    os.path.normcase(p) for p in _TRIGGER_FILES
)


def _check_cluster_names() -> list[str]:
    """chainmap_cluster_names.yaml 词表 sanity（键格式/族名长度）。"""
    path = _REPO_ROOT / "config" / "chainmap_cluster_names.yaml"
    if not path.exists():
        return []
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    fails: list[str] = []
    for k, v in raw.items():
        if not _CLUSTER_KEY_PAT.match(str(k)):
            fails.append(f"chainmap_cluster_names 键非 C<N> 格式: {k}")
        if len(str(v)) > 6:
            fails.append(f"chainmap_cluster_names {k} 族名超 6 字: {v}")
    return fails


def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
    """合并前原 _check 闭包体（st-gslim-20260923 P4 闭包提级，行为逐字节保留）。"""
    if not files:
        return True, ""
    # 生产形态=绝对路径（gateway abspath），_norm_rel 归一到 normcase 相对路径
    norm = {_norm_rel(gateway, f) for f in files}
    triggered = sorted(_TRIGGER_FILES_NORMCASE & norm)
    if not triggered:
        return True, ""

    from zephyr.gov_enforcement.registry_alignment import check_industry_graph_field_dictionary

    all_fails: list[str] = []
    try:
        errors, warnings = check_industry_graph_field_dictionary()
        all_fails.extend(errors)
        for w in warnings:
            logger.warning("INDUSTRY-CHAIN-MAP gate warn: %s", w)
    except Exception as e:  # noqa: BLE001 — 共享核查异常=环境异常放行
        logger.warning("INDUSTRY-CHAIN-MAP gate: 字典核查异常（fail-open）: %s", e)

    if any(f.endswith("chainmap_cluster_names.yaml") for f in triggered):
        try:
            all_fails.extend(_check_cluster_names())
        except Exception as e:  # noqa: BLE001
            logger.warning("INDUSTRY-CHAIN-MAP gate: 簇名词表核查异常（fail-open）: %s", e)

    if not all_fails:
        return True, ""

    detail_lines = "\n".join(f"  - {x}" for x in all_fails)
    detail = (
        f"INDUSTRY-CHAIN-MAP：产业链全景图 git 侧工件对齐 {len(all_fails)} 项违规（触发: {', '.join(triggered)}）\n"
        f"{detail_lines}\n"
        "-> 字典↔DDL↔引擎三方必须同 commit 同步（alignment_checklist §3 图 8 行）"
    )
    logger.error("INDUSTRY-CHAIN-MAP gate block:\n%s", detail)
    return False, detail


def make_industry_chain_map_gate() -> GateSpec:
    """旧单门工厂（st-gslim-20260923 P4 已并入新台 MAP-ALIGNMENT，不再注册；保留供历史测试/引用兼容）。"""
    return GateSpec(gate_id="INDUSTRY-CHAIN-MAP", check=_check, priority=147)
