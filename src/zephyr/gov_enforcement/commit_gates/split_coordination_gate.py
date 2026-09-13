# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §split_coordination_gate
# [MODULE] zephyr.gov_enforcement.commit_gates.split_coordination_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] yaml（外部）；zephyr.gov_enforcement.commit_gates._diff_helpers（_norm_rel）；声明真源=.runtime/coordination/active_splits.yaml（scripts/governance/split_coordination.py 写入）
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__（经 in_process_gate_registry.yaml 自动注册）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 硬阻断（协调协议执行点）——触发式：存在活跃拆分声明（mover≠本 session）且本 commit 清单命中声明 old_paths 时阻断（防旧平铺路径重建=双重存在事故）；mover 本人放行；声明拆除正门=mover finish（显式收尾），陈旧声明（>48h 弃单）降级 warn 放行防砖；不做"已落地自动失活"（落地=旧路径消失=重建风险开始，恰是保护最需存在的时点）；声明文件缺失/解析失败 fail-open（协调态运行时文件，非真源——损坏不砖死全库提交）
# [MODIFY-GUARD] gate_id="SPLIT-COORDINATION"；声明 schema（splits[].mover_session/old_paths/new_root/declared_at）变更须同步 split_coordination.py 工具与测试；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 声明 YAML 解析失败=fail-open 放行+warn（非真源）；declared_at 解析失败=视为不陈旧（保守，保护不静默消失）；命中活跃声明=硬阻断给出 re-base 指引
# [TESTS] tests/governance/commit_gates/test_split_coordination_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-SPLIT-COORDINATION-001
# [CREATION-TOKEN] split-coordination-gate-20260913
"""split_coordination_gate.py — 拆分×编辑双重存在协议门禁（SPLIT-COORDINATION，priority=143）

病根（第一性原理，2026-09-13 极限红蓝对抗 F5 100% 复现）
--------------------------------------------------------
拆分者把 N 个文件从平铺路径 ``dir/*.md`` 搬到子目录 ``dir/a/*.md`` 后，并发编辑者
（不知情）在**旧平铺路径重建**自己的文件——每笔提交单看全合法（token 有、门禁过），
组合起来 HEAD 里同名文件双重存在（历史"651 处失效路径引用"事故的根源形态）。
commit 时点门禁无法拦截**组合事故**，因为缺乏跨会话的"拆分进行中"信号。

协议根治（机器强制，替代纸面 SOP）
----------------------------------
1. 拆分者动盘**之前**声明：``scripts/governance/split_coordination.py begin`` 写入
   ``.runtime/coordination/active_splits.yaml``（mover_session + old_paths 清单 +
   new_root 新挂基点）。
2. 本 gate 在每个 commit 上执行协调校验：他会话提交清单命中活跃声明的 old_paths
   → 硬阻断，给出 re-base 指引（新路径/找 mover 协调）。
3. 声明拆除正门=``finish``（mover 确认消费方已 re-base 后显式收尾）；
   陈旧自愈=声明超 48h（mover 弃单）降级 warn 放行（防砖）。
   **刻意不做**"已落地自动失活"：搬移落地=旧路径从 HEAD 消失=重建风险开始的
   时点——恰是保护最需要存在的时刻（落地即失活会在风险窗口起点拆掉保护）。
4. ``sweep`` 清扫陈旧声明（>48h 弃单，防目录被永久锁死）。

设计权衡
--------
1. **触发式零基线开销**：无声明文件（绝大多数时间）= 一次 Path.exists，零 git 调用。
2. **fail-open（声明侧）**：声明文件是运行时协调态，非治理真源——解析失败放行+warn，
   不砖死全库提交（对比 FACTORY-MAP 真源损坏 fail-closed：那是数据真源，这是协调信号）。
3. **mover 放行**：mover 本人的搬移提交（旧路径删除+新路径新增）是协议的正主。
4. **陈旧降级**：mover 弃单后声明残留不永久锁目录——48h 后自动降级 warn（弃单自愈）。

Usage::

    from zephyr.gov_enforcement.commit_gates.split_coordination_gate import make_split_coordination_gate

    registry.register(make_split_coordination_gate())  # 经 in_process_gate_registry.yaml 自动注册
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Final

import yaml

from zephyr.gov_enforcement.commit_gates._diff_helpers import _norm_rel
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__: Final = ["make_split_coordination_gate"]

# 声明真源（运行时协调态，scripts/governance/split_coordination.py 单一写入方+本 gate 只读）
DECLARATION_REL: Final[str] = ".runtime/coordination/active_splits.yaml"

# 声明陈旧度上限（小时）：mover 弃单（begin 后消失）不会永久锁死目录——超过即降级
# warn 放行（协调信号自愈，防砖）。拆除保护的正门=mover finish（显式收尾）。
_STALE_AFTER_H: Final[float] = 48.0


def _declaration_stale(entry: dict) -> bool:
    """声明是否陈旧（declared_at 超过 _STALE_AFTER_H 小时）——弃单自愈。

    解析失败视为不陈旧（保守：解析不出就当新鲜，保护不静默消失）。
    """
    from datetime import datetime, timedelta, timezone  # noqa: PLC0415

    try:
        declared = datetime.fromisoformat(str(entry.get("declared_at") or ""))
    except ValueError:
        return False
    if declared.tzinfo is None:
        declared = declared.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - declared > timedelta(hours=_STALE_AFTER_H)


def _load_active_splits(gateway) -> tuple[list[dict], str]:
    """读声明文件，返回 (splits, skip_reason)——skip_reason 非空表示放行（零声明/损坏 fail-open）。"""
    decl_path = Path(str(getattr(gateway, "project_root", "."))) / DECLARATION_REL
    if not decl_path.exists():
        return [], "skip: 无拆分声明文件（协调窗口全关）"
    try:
        data = yaml.safe_load(decl_path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001 — 协调态文件损坏=fail-open（非真源）
        logger.warning("SPLIT-COORDINATION: 声明解析失败 fail-open: %s", e)
        return [], "skip: 拆分声明解析失败（fail-open，协调态非真源）"
    splits = (data or {}).get("splits") if isinstance(data, dict) else None
    if not splits:
        return [], "skip: 无活跃拆分声明"
    return [s for s in splits if isinstance(s, dict)], ""


def _find_foreign_hit(gateway, files: list[str], session_id: str, splits: list[dict]) -> tuple[dict, list[str]] | None:
    """扫描声明找首个需要阻断的 (entry, hits)——他会话提交清单 ∩ 活跃声明 old_paths。

    hits 返回**原始相对路径**（正斜杠，非 normcase——供展示与磁盘反查）。
    mover 本人放行；陈旧声明（>48h 弃单）降级放行（warn，防砖）。
    保护拆除正门=mover finish；**不做**"已落地自动失活"——搬移落地=旧路径消失
    =重建风险开始，恰是保护最需要存在的时点（设计教训：落地即失活会把保护
    在风险窗口起点拆掉）。
    """
    norm_files = {_norm_rel(gateway, f) for f in files}
    for entry in splits:
        mover = str(entry.get("mover_session") or "")
        old_paths = [str(p).replace("\\", "/") for p in entry.get("old_paths") or []]
        if not mover or not old_paths or mover == session_id:
            continue  # 声明残缺跳过 / mover 本人的搬移提交（协议正主）
        by_norm = {os.path.normcase(p): p for p in old_paths}
        hit_norms = sorted(norm_files & set(by_norm))
        if not hit_norms:
            continue
        if _declaration_stale(entry):
            logger.warning(
                "SPLIT-COORDINATION: 声明已陈旧（mover=%s 弃单自愈降级 warn 放行）", mover
            )
            continue
        return entry, [by_norm[n] for n in hit_norms]
    return None


def _locate_rebased(gateway, old_rel: str) -> str:
    """反查命中文件的**实际新位置**（P3-1 治本，2026-09-13 红蓝复测发现）。

    多簇拆分（a/b/c）时声明 new_root 只是单值指针（首簇），编辑者按它指引会
    re-base 到错误子目录。本函数在父目录下一层深找同名文件（拆分者已搬移/
    已提交时磁盘可寻）：``lab/seg_050.md`` → 找到 ``lab/b/seg_050.md`` 则返回
    实际新路径；找不到（搬移未发生/单簇场景）返回空串（消息回退 new_root 指引）。
    """
    if "/" not in old_rel:
        return ""
    parent, base = old_rel.rsplit("/", 1)
    pdir = Path(str(getattr(gateway, "project_root", "."))) / parent
    try:
        for child in sorted(pdir.iterdir()):
            if child.is_dir() and (child / base).is_file():
                return f"{parent}/{child.name}/{base}"
    except OSError:
        return ""
    return ""


def make_split_coordination_gate() -> GateSpec:
    """构造拆分协调门禁 GateSpec（#ARCH-SPLIT-COORDINATION-001）。

    Returns:
        GateSpec(gate_id="SPLIT-COORDINATION", priority=143)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        if not files:
            return True, ""
        splits, skip_reason = _load_active_splits(gateway)
        if skip_reason:
            return True, skip_reason

        session_id = str(kwargs.get("session_id") or "")
        hit = _find_foreign_hit(gateway, files, session_id, splits)
        if hit is None:
            return True, ""
        entry, hits = hit
        # P3-1 治本：逐命中文件反查实际新位置（多簇拆分精确指引；找不到回退 new_root）
        lines = []
        for h in hits[:10]:
            actual = _locate_rebased(gateway, h)
            lines.append(f"  - {h}" + (f"  → 实际新位置: {actual}" if actual else ""))
        new_root = str(entry.get("new_root") or "见声明")
        declared_at = str(entry.get("declared_at") or "?")
        mover = str(entry.get("mover_session") or "?")
        detail = (
            f"SPLIT-COORDINATION：{len(hits)} 个文件处于拆分搬移协调窗口，"
            f"禁止在旧平铺路径提交/重建（防双重存在事故）：\n"
            + "\n".join(lines)
            + f"\n拆分者={mover}（声明于 {declared_at}），新挂基点={new_root}"
            "（多簇拆分以逐文件『实际新位置』指引为准）。"
            "处置：①编辑请 re-base 到实际新位置（无指引时用新挂基点）；②或协调拆分者"
            "（拆分未完成时可 finish 解除、已完成时确认消费方全部 re-base 后 finish）；"
            "③查看声明：python scripts/governance/split_coordination.py status"
        )
        logger.warning("SPLIT-COORDINATION gate block (mover=%s, hits=%d)", mover, len(hits))
        return False, detail

    return GateSpec(gate_id="SPLIT-COORDINATION", check=_check, priority=143)
