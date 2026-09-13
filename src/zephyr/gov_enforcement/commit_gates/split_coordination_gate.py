# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §split_coordination_gate
# [MODULE] zephyr.gov_enforcement.commit_gates.split_coordination_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] yaml（外部）；zephyr.gov_enforcement.commit_gates._diff_helpers（_norm_rel）；声明真源=.runtime/coordination/active_splits.yaml（scripts/governance/split_coordination.py 写入）
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__（经 in_process_gate_registry.yaml 自动注册）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 硬阻断（协调协议执行点）——触发式：存在活跃拆分声明（mover≠本 session）且本 commit 清单命中声明 old_paths 时阻断（防旧平铺路径重建=双重存在事故）；mover 本人放行；声明全部落地（HEAD 无+盘无）自动失活；声明文件缺失/解析失败 fail-open（协调态运行时文件，非真源——损坏不砖死全库提交）
# [MODIFY-GUARD] gate_id="SPLIT-COORDINATION"；声明 schema（splits[].mover_session/old_paths/new_root/declared_at）变更须同步 split_coordination.py 工具与测试；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 声明 YAML 解析失败=fail-open 放行+warn（非真源）；git ls-tree 失败=保守视为未落地（声明保持活跃，fail-safe 方向）；命中活跃声明=硬阻断给出 re-base 指引
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
3. 声明自动失活：old_paths 全部不在 HEAD 且不在磁盘（搬移已落地且无人重建）
   → 协调窗口关闭，编辑者自由。
4. ``finish``（mover 主动收尾）或 ``sweep``（清扫已落地声明）移除条目。

设计权衡
--------
1. **触发式零基线开销**：无声明文件（绝大多数时间）= 一次 Path.exists，零 git 调用。
2. **fail-open（声明侧）**：声明文件是运行时协调态，非治理真源——解析失败放行+warn，
   不砖死全库提交（对比 FACTORY-MAP 真源损坏 fail-closed：那是数据真源，这是协调信号）。
3. **fail-safe（落地判定侧）**：git ls-tree 失败时保守视为"未落地"（声明保持活跃），
   宁可多拦一次（指引清晰）不可漏放双重存在。
4. **mover 放行**：mover 本人的搬移提交（旧路径删除+新路径新增）是协议的正主。

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


def _split_landed(gateway, entry: dict) -> bool:
    """声明是否已全部落地：old_paths 全部不在 HEAD 树且不在磁盘。

    fail-safe：git ls-tree 任一失败 → 返回 False（视为未落地，声明保持活跃——
    宁可多拦（指引清晰）不可漏放双重存在）。
    编辑者在旧路径重建未提交时：磁盘存在 → 未落地（继续拦，正确）。
    """
    root = Path(str(getattr(gateway, "project_root", ".")))
    old_paths = [str(p).replace("\\", "/") for p in entry.get("old_paths") or []]
    if not old_paths:
        return True
    dirs = sorted({p.rsplit("/", 1)[0] for p in old_paths if "/" in p})
    tracked: set[str] = set()
    for d in dirs:
        try:
            r = gateway.run_git(["git", "ls-tree", "-r", "--name-only", "HEAD", "--", d])
            if r.returncode != 0:
                return False  # fail-safe：HEAD 查询失败=未落地
            tracked |= {os.path.normcase(ln.strip()) for ln in r.stdout.splitlines() if ln.strip()}
        except Exception:  # noqa: BLE001 — git 设施异常=fail-safe 未落地
            return False
    for p in old_paths:
        if os.path.normcase(p) in tracked:
            return False  # 旧路径仍被 HEAD 跟踪=搬移未提交
        if (root / p).exists():
            return False  # 磁盘仍有旧路径文件（含编辑者重建）=窗口未关
    return True


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

    mover 本人放行；命中但已落地（HEAD 无+盘无）自动失活放行。
    """
    norm_files = {_norm_rel(gateway, f) for f in files}
    for entry in splits:
        mover = str(entry.get("mover_session") or "")
        old_paths = [str(p).replace("\\", "/") for p in entry.get("old_paths") or []]
        if not mover or not old_paths or mover == session_id:
            continue  # 声明残缺跳过 / mover 本人的搬移提交（协议正主）
        hits = sorted(norm_files & {os.path.normcase(p) for p in old_paths})
        if hits and not _split_landed(gateway, entry):
            return entry, hits
    return None


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
        # 生产形态=绝对路径（gateway abspath），_norm_rel 归一在 _find_foreign_hit 内完成
        new_root = str(entry.get("new_root") or "见声明")
        declared_at = str(entry.get("declared_at") or "?")
        mover = str(entry.get("mover_session") or "?")
        detail = (
            f"SPLIT-COORDINATION：{len(hits)} 个文件处于拆分搬移协调窗口，"
            f"禁止在旧平铺路径提交/重建（防双重存在事故）：\n"
            + "\n".join(f"  - {h}" for h in hits[:10])
            + f"\n拆分者={mover}（声明于 {declared_at}），新挂基点={new_root}。"
            "处置：①编辑请 re-base 到新挂基点路径；②或协调拆分者 finish 后再操作"
            "（拆分已落地时运维可 sweep 清扫残留声明）；"
            "③查看声明：python scripts/governance/split_coordination.py status"
        )
        logger.warning("SPLIT-COORDINATION gate block (mover=%s, hits=%d)", mover, len(hits))
        return False, detail

    return GateSpec(gate_id="SPLIT-COORDINATION", check=_check, priority=143)
