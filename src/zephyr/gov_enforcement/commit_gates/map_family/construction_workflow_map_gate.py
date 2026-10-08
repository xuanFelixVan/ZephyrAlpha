# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §construction_workflow_map_gate
# [MODULE] zephyr.gov_enforcement.commit_gates.map_family.construction_workflow_map_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] yaml；validate_construction_steps（结构判据单一真源动态复用）+ zephyr.gov_enforcement.commit_gates._diff_helpers——详单见下方详情块
# [CONSUMERS] CONSTRUCTION-WORKFLOW-MAP 聚合台 subs 消费（panorama_alignment_gate）+ 对抗测试——详单见下方详情块
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 只暴露 _check；fail-closed 四通道；触发面 normcase 归一；禁复制校验器判据——详单见下方详情块
# [MODIFY-GUARD] gate_id/触发面变更须同步 90 spec gate 接法节与 alignment_checklist 图14 行——详单见下方详情块
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 校验器不可达/图 YAML 损坏=fail-closed 阻断；触发面外 skip 放行
# [TESTS] tests/governance/commit_gates/test_construction_workflow_map_gate.py
# [TTL] permanent
# [TESTS] tests/governance/commit_gates/test_construction_workflow_map_gate.py（原位详注见行 34+，2026-10-04 落库 30 行窗口适配）
# [TTL] permanent（原位详注见行 36+）
# [AI_AUTONOMY] ai_modifiable（原位详注见行 36+）
# [ERROR_CONTRACT] 校验器不可达/图 YAML 损坏=fail-closed 阻断；触发面外 skip（原位详注见行 36+）
# [DEPENDENCIES] yaml（外部）；scripts.governance.d5_architecture.validators.validate_construction_steps
#   （validate_structure / check_prose_counts，sys.path 动态加载——校验逻辑单一真源，禁复制判据）；
#   zephyr.gov_enforcement.commit_gates._diff_helpers._norm_rel（触发面路径归一）
# [CONSUMERS] zephyr.gov_enforcement.commit_gates.panorama_alignment_gate.make_map_alignment_gate()
#   的 subs 清单（MAP-ALIGNMENT 聚合台挂载行由总包统一落，本件不注册自己）；
#   tests/governance/commit_gates/test_construction_workflow_map_gate.py
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 硬阻断（确定性校验）——触发式：本 commit 触及图 14 真源四件（图 YAML/校验器/
#   生成器/91 号机读锚块提案件）时跑结构校验（17 环节契约全集+12 gap 显性化节点/三层字段 L0
#   统一名与废止别名禁令/segment 层位挂全/CV-BUS module_id 总线挂载/CV-DUAL 双轴与骨架状态列
#   同源/CV-STATE 声称值与骨架实扫列一致/CV-10 边闭合与未声明反馈环与主序无环/CV-13 计数只进
#   counts/CV-14 handoff 边界/CV-16 automated 必带 exec_source 与 built 必带实查证据/
#   INV-1 反复制长度面/越域挂载禁），error>0→阻断；
#   提交面走 live=False 口径（不做全仓磁盘实存与在册探活，判据真源见校验器 --skip-live 一条），
#   结构面一项不放宽；锚块装载点（proposal 态）不可装载=YAML 损坏级 fail-closed；
#   图 YAML 解析失败/校验器不可达/结构校验抛异常=fail-closed（真源损坏必须先修）；
#   触发面外=skip 放行；外部真源面（骨架两列/depgraph PG/门禁册/词表）不可达=对应子检查在校验器
#   内降 warn，随日志留痕而不升级为阻断（禁环境异常打死无辜提交）；触发文件清单变更须与生成器同步
# [MODIFY-GUARD] gate_id="CONSTRUCTION-WORKFLOW-MAP"；_TRIGGER_FILES 变更须同步
#   docs/_working/map_build/fig14_construction/90_step_anchor_validator_spec.md 的 gate 接法节与
#   alignment_checklist 图 14 行（挂轴由总包落）；check 闭包签名
#   (gateway, files, **kwargs) -> tuple[bool, str]；本件禁复制校验器判据（改判据只改校验器）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 校验器加载失败/图 YAML 解析失败/结构校验异常/锚块提案件不可装载=fail-closed
#   阻断（真源损坏须先修）；触发面外=skip 放行；不抛业务异常（内部异常一律收敛为 (False, detail)）；
#   与 DECISION-MAP/FACTORY-MAP/DEV-DELIVERY-MAP/TRADING-DAY-CYCLE-MAP 同族确定性硬门禁
#   （st-gslim 形态：只暴露 _check，注册与聚合台 subs 挂载由总包统一落）
# [TESTS] tests/governance/commit_gates/test_construction_workflow_map_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""construction_workflow_map_gate.py — AI 施工升级流图（图 14）结构门禁（CONSTRUCTION-WORKFLOW-MAP）

病根（第一性原理）
-----------------
图 14 的全部价值在于把"文档说有一个可跑锚、实则没有"这类静默腐坏变成可机检的显性事实：
17 个施工环节的机读锚块、9+3 条 gap 显性化、状态列与可机验列两列口径、handoff 段禁吞图 11 机制、
以及 production 数恒等骨架 ✅ 数（多了算谎、少了算欠）。这些一旦没有 commit 门禁，就会以
"手改图不回生成""伪造环节""🔨 环节宣 production 粉饰""有码环节不挂 module_id 冒充总线"
"旧字段名回潮""automated 凭散文主张"六种形态静默退化——而这张图描述的正是施工流程本身，
退化一次的代价是后续每次施工都照着假锚走。判据真源在
validate_construction_steps.validate_structure，本 gate 只做阻塞语义封装
（形态逐条照抄图 11 DEV-DELIVERY-MAP 与图 9 FACTORY-MAP 母版，勿造新概念）。

设计权衡
--------
1. **触发面四件**：图 YAML + 校验器 + 生成器 + 91 号机读锚块提案件。第四件是本图与其余五图的
   结构差异——政策尚未内嵌锚块期间（`anchor_source: proposal`），图的真源是那份提案件，
   它损坏=图无源，故既是触发面也是装载点。
2. **提交面 live=False**：磁盘实存/在册探活类腿（CV-05/06/07/08 与 depgraph PG、投影册核对）
   留给校验器 CLI 与 align_all，提交时不做全仓 stat（同 FACTORY-MAP 把仓储存在性排除在 gate
   外的口径）；结构面（枚举/闭合/双轴/计数/边/长度）一项不放宽。
3. **政策面不入 gate**：check_anchors 需扫政策 MD（CV-04 双向闭合/CV-11 矩阵/CV-GHOST），
   属全仓扫描语义，由 CLI 与 align_all 承担；本 gate 只调 validate_structure +
   check_prose_counts（后者纯文本判定，零 IO）。残余面如实记：anchor_source 被从 proposal
   翻成 policy 时本 gate 不再校装载点，"政策是否真嵌了块"由 CLI 的 CV-04 两条腿
   （policy 态 pending_anchors 必须清空 / proposal 态必须列全）兜，不在提交面复制一遍。
4. **真源可用性解耦**：骨架两列/门禁册/depgraph 投影/verifiability 词表四面的不可达降级
   全部发生在校验器内部（降 warn 入 warnings），本 gate 只随日志留痕，绝不升级为阻断。
5. **注册与聚合台挂载不属本件**：图门自 st-gslim P4 起并入 MAP-ALIGNMENT 聚合台，
   本模块只暴露 _check；gate 册登记与 subs 挂载行由总包统一落（净零增长纪律）。

Usage::

    # 总包挂载点（本车道不注册）：
    #   panorama_alignment_gate.make_map_alignment_gate() subs 增行：
    #   ("CONSTRUCTION-WORKFLOW-MAP", "construction_workflow_map_gate", "_check")

# [ALGO_FLOW]
# algo_flow: |
#     # [ALGO_FLOW]
#     # 层: 输入
#     # - id: I1
#     #   name: path 参数
#     #   fields: 待校准
#     #   code: path
#     # - id: I2
#     #   name: 数据 DataFrame
#     #   fields: 待校准
#     #   code: data
#     # - id: I3
#     #   name: warnings 参数
#     #   fields: 待校准
#     #   code: warnings
#     # - id: I4
#     #   name: gateway 参数
#     #   fields: 待校准
#     #   code: gateway
#     # 层: 特征
#     # - id: F1
#     #   name_zh: 待校准特征
#     #   name_en: feature_tbd
#     #   intro: 待校准（AI读代码确认）
#     #   formula: 待校准
#     #   code: 待校准
#     #   registry: factor_registry: 待查
#     #   is_break: true
#     # 层: 算法
#     # - id: A1
#     #   name_zh: 1. **触发面四件**：图 YAML + 校验器 + 生成器 + 91 号机读
#     #   name_en: tbd
#     #   intro: 1. **触发面四件**：图 YAML + 校验器 + 生成器 + 91 号机读锚块提案件。第四件是本图与其余五图的 结
#     #   inputs: 待校准
#     #   outputs: 待校准
#     # - id: A2
#     #   name_zh: 2. **提交面 live=False**：磁盘实存/在册探活类腿（CV-05/
#     #   name_en: tbd
#     #   intro: 2. **提交面 live=False**：磁盘实存/在册探活类腿（CV-05/06/07/08 与 depgraph
#     #   inputs: 待校准
#     #   outputs: 待校准
#     # - id: A3
#     #   name_zh: 3. **政策面不入 gate**：check_anchors 需扫政策 MD（
#     #   name_en: tbd
#     #   intro: 3. **政策面不入 gate**：check_anchors 需扫政策 MD（CV-04 双向闭合/CV-11 矩阵/
#     #   inputs: 待校准
#     #   outputs: 待校准
#     # - id: A4
#     #   name_zh: 4. **真源可用性解耦**：骨架两列/门禁册/depgraph 投影/veri
#     #   name_en: tbd
#     #   intro: 4. **真源可用性解耦**：骨架两列/门禁册/depgraph 投影/verifiability 词表四面的不可达降级
#     #   inputs: 待校准
#     #   outputs: 待校准
#     # - id: A5
#     #   name_zh: 5. **注册与聚合台挂载不属本件**：图门自 st-gslim P4 起并入
#     #   name_en: tbd
#     #   intro: 5. **注册与聚合台挂载不属本件**：图门自 st-gslim P4 起并入 MAP-ALIGNMENT 聚合台， 本
#     #   inputs: 待校准
#     #   outputs: 待校准
#     # 层: 输出
#     # - id: O1
#     #   name_zh: 待校准输出 list[str]
#     #   name_en: list[str]
#     #   intro: 待校准
#     #   downstream: 待校准
#     # - id: O2
#     #   name_zh: 待校准输出 str
#     #   name_en: str
#     #   intro: 待校准
#     #   downstream: 待校准
#     # [/ALGO_FLOW]
#     # 边:
#     # I1 -.->|断点| F1
#     # I2 -.->|断点| F1
#     # I3 -.->|断点| F1
#     # I4 -.->|断点| F1
#     # F1 --> A1
#     # A1 --> A2
#     # A2 --> A3
#     # A3 --> A4
#     # A4 --> A5
#     # A5 --> O1
# [/ALGO_FLOW]
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path, PurePosixPath
from typing import Final

import yaml

from zephyr.gov_enforcement.commit_gates._diff_helpers import _norm_rel

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[5]
_VALIDATORS_DIR = _REPO_ROOT / "scripts" / "governance" / "d5_architecture" / "validators"
_VALIDATOR_MOD = "validate_construction_steps"

_MAP_REL: Final[str] = "config/construction_workflow_map.yaml"
_VALIDATOR_REL: Final[str] = "scripts/governance/d5_architecture/validators/validate_construction_steps.py"
_GENERATOR_REL: Final[str] = "scripts/governance/d5_architecture/generators/generate_construction_workflow_map.py"
_ANCHORS_REL: Final[str] = "docs/_working/map_build/fig14_construction/91_step_anchor_block_proposal.yaml"
_POLICY_REL: Final[str] = "docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md"

# 触发面=图 14 真源五件：图 YAML + 校验器 + 生成器 + 机读锚块提案件 + 政策锚块承载位
# （2026-10-04 整编适配：锚块真源已整编入政策附录 D，政策变更强制重校；
#   校验器/生成器变更=判据与语义层规则变更，强制重校，学 DEV-DELIVERY-MAP 口径）
_TRIGGER_FILES: Final[frozenset[str]] = frozenset({_MAP_REL, _VALIDATOR_REL, _GENERATOR_REL, _ANCHORS_REL, _POLICY_REL})

# 触发面 normcase 归一（commit() 传入绝对路径——图 9 母版实弹教训：朴素反斜杠替换对绝对
# 路径恒 miss，本集合与 _norm_rel 输出同域可比）
_TRIGGER_FILES_NORMCASE: Final[frozenset[str]] = frozenset(os.path.normcase(p) for p in _TRIGGER_FILES)

# 图真源与锚块装载点路径（模块级常量=测试可替换挂点，红蓝 tmp 图直调 _check 先例=FACTORY-MAP）
_MAP_PATH: Final[Path] = _REPO_ROOT / _MAP_REL
_ANCHORS_PATH: Final[Path] = _REPO_ROOT / _ANCHORS_REL


def _rel_norm(path: str) -> str:
    """路径声明比对用的宽松归一（正斜杠 + 去前导 ./ + normcase）。

    前导/中段 ./ 由 PurePosixPath 归一（相对路径消除逻辑本身不得含 "./" 字面量，
    RELATIVE-PATH-LITERAL 门约束）；空串原样返回防 PurePosixPath("") 变 "."。
    """
    s = str(path or "").replace("\\", "/").strip()
    if s:
        s = str(PurePosixPath(s))
    return os.path.normcase(s)


def _check_anchor_block(data: dict, warnings: list[str]) -> list[str]:
    """锚块装载点完整性（fail-closed 通道之一）。

    只判"派生件声称的锚块来源现在是否可装载"这一件事：图里 `anchor_source=proposal` 即声明
    本轮 17 环节的机读锚来自 91 号提案件，该件读不出/非映射/`step_anchors` 空或形态坏 ⇒
    派生链断裂，与图 YAML 损坏同级（真源损坏必须先修）。政策已嵌块（anchor_source=policy）
    时提案件不再是真源，本腿整体跳过。
    **禁在此复制任何 CV-* 判据**——锚块字段对不对由校验器与生成器负责。
    """
    if str(data.get("anchor_source")) != "proposal":
        return []
    declared = str(data.get("anchor_block_origin") or "")
    if declared and _rel_norm(declared) != _rel_norm(_ANCHORS_REL):
        # 纯提示：装载点被搬走过图仍可校验通过，但"图声称的源"与"gate 读的源"已不是一件
        warnings.append(f"anchor_block_origin={declared} 与本 gate 装载点 {_ANCHORS_REL} 不一致（随结论留痕，不阻断）")
    problems: list[str] = []
    try:
        block = yaml.safe_load(_ANCHORS_PATH.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001 — 锚块真源损坏=fail-closed
        return [f"锚块提案件不可装载（{os.path.basename(str(_ANCHORS_PATH))}）: {e}"]
    if not isinstance(block, dict):
        return [f"锚块提案件顶层非对象: {type(block).__name__}"]
    steps = block.get("step_anchors")
    if not isinstance(steps, list) or not steps:
        problems.append("锚块提案件缺非空 step_anchors 清单")
    else:
        bad = [i for i, s in enumerate(steps) if not isinstance(s, dict) or not s.get("step_id")]
        if bad:
            problems.append(f"锚块提案件 step_anchors 有 {len(bad)} 条缺 step_id（下标 {bad[:5]}）")
    return problems


def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
    """触发式结构校验（签名与聚合台 subs 约定一致；阻塞语义封装，判据真源在校验器）。"""
    if not files:
        return True, ""
    # 生产形态=绝对路径（gateway abspath），_norm_rel 归一到 normcase 相对路径
    norm = {_norm_rel(gateway, f) for f in files}
    triggered = sorted(_TRIGGER_FILES_NORMCASE & norm)
    if not triggered:
        return True, "skip: 本 commit 未触及图 14 触发面（图 YAML/校验器/生成器/锚块提案件真源）"

    # 校验逻辑单一真源（validate_construction_steps），懒加载防 zephyr↔scripts 成环（先例=FACTORY-MAP）
    if str(_VALIDATORS_DIR) not in sys.path:
        sys.path.insert(0, str(_VALIDATORS_DIR))
    try:
        from validate_construction_steps import (  # noqa: import-integrity  sys.path 动态加载：判据单一真源，懒加载防 zephyr↔scripts 成环
            check_prose_counts,
            validate_structure,
        )
    except Exception as e:  # noqa: BLE001 — 校验器不可达=fail-closed
        logger.error("CONSTRUCTION-WORKFLOW-MAP gate: 校验器加载失败（fail-closed）: %s", e)
        return False, (f"CONSTRUCTION-WORKFLOW-MAP: 校验器 {_VALIDATOR_MOD} 加载失败（fail-closed）: {e}")

    try:
        raw = _MAP_PATH.read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
    except Exception as e:  # noqa: BLE001 — 真源损坏=fail-closed
        logger.error("CONSTRUCTION-WORKFLOW-MAP gate: 图真源解析失败（fail-closed）: %s", e)
        return False, (f"CONSTRUCTION-WORKFLOW-MAP: {_MAP_REL} 解析失败（fail-closed，真源损坏须先修）: {e}")
    if not isinstance(data, dict):
        return False, f"CONSTRUCTION-WORKFLOW-MAP: {_MAP_REL} 顶层非对象（真源损坏须先修）"

    warnings: list[str] = []
    try:
        errors = list(validate_structure(data, root=_REPO_ROOT, warnings=warnings, live=False))
        errors += check_prose_counts(raw)
        errors += _check_anchor_block(data, warnings)
    except Exception as e:  # noqa: BLE001 — 校验器抛异常=fail-closed
        logger.error("CONSTRUCTION-WORKFLOW-MAP gate: 结构校验异常（fail-closed）: %s", e)
        return False, f"CONSTRUCTION-WORKFLOW-MAP: 结构校验异常（fail-closed）: {e}"

    for w in warnings:  # 外部真源面不可达/口径提示=随结论留痕，绝不升级为阻断
        logger.warning("CONSTRUCTION-WORKFLOW-MAP gate（降级项）: %s", w)

    if errors:
        detail_lines = "\n".join(f"  - {x}" for x in errors)
        detail = (
            f"CONSTRUCTION-WORKFLOW-MAP：AI 施工升级流图结构校验 {len(errors)} 项 error"
            f"（nodes={len(data.get('nodes') or [])} "
            f"edges={len(data.get('edges') or [])} "
            f"anchor_source={data.get('anchor_source')}）\n{detail_lines}\n"
            f"-> 修复真源后重提：锚块改 {os.path.basename(_ANCHORS_REL)}"
            "（政策嵌块后改政策段尾块），图 YAML 一律重跑生成器（禁手改不回生成）"
            "（17 环节契约+12 gap/三层字段 L0 统一名/segment 层位/CV-BUS module_id/"
            "CV-DUAL 双轴×骨架状态列/CV-STATE 声称值回查/CV-10 边闭合与主序无环/"
            "CV-13 计数只进 counts/CV-14 handoff 边界/CV-16 automated 锚与 built 实查/"
            "INV-1 长度面/越域挂载禁/锚块装载点可装载）"
        )
        logger.error("CONSTRUCTION-WORKFLOW-MAP gate block:\n%s", detail)
        return False, detail
    logger.info("CONSTRUCTION-WORKFLOW-MAP gate: 结构校验通过（触发面=%s）", ",".join(triggered))
    return True, ""
