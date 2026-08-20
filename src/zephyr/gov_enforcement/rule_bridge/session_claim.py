# [BLUEPRINT] MOD-GOV_SESSION_CLAIM | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §FP-ISO.4B
# [MODULE] zephyr.gov_enforcement.rule_bridge.session_claim
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.security.access_control.session_concurrency (SessionRegistry)
# [CONSUMERS] 已废弃（superseded by session_worktree_start，FP-ISO.4C，2026-07-04）；generate_session_id 仍被 zephyr.gov_enforcement.rule_bridge.session_worktree 调用
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 已废弃（superseded by session_worktree_start + HELD-OVERLAP gate，FP-ISO.4C，2026-07-04）：session_claim_start/add/check/heartbeat/end 零实际调用方（死代码），claim 语义已被 session_worktree_commit 的 HELD-OVERLAP 硬阻断完全替代且更强（编辑前软预警 -> commit 时硬阻断）；generate_session_id 保留（纯函数，被 session_worktree.py 调用）；session_claim_start 原子注册+claim（register 后逐个 claim_file，冲突文件跳过并记录）；session_claim_add 返回 conflict=True 时 AI MUST 等待或换文件（软约束）；session_claim_end 释放所有 held_files 并 unregister；session_id 格式 sess-{PID}-{yyyyMMddHHmmss}（Trae 对话无内置 session_id，由 AI 自生成）；所有函数 project_root 默认 REPO_ROOT
# [MODIFY-GUARD] session_id 生成规则；claim 冲突语义（conflict=True 不抛异常）；TTL 续期策略
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 所有函数返回 dict（不抛异常）；registry 异常时 conflict=True + error 字段；session 不存在时返回 not_found=True
# [TESTS] —（已废弃，无测试；generate_session_id 由 tests/governance/rule_bridge/test_session_worktree.py 间接覆盖）
# [A_module] module_id=MOD-GOV_SESSION_CLAIM | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

session_claim.py — AI 对话并发声明 helper（FP-ISO.4B 件2改，2026-07-01 治本）

.. deprecated:: 2026-07-04
    ``session_claim_start``/``add``/``check``/``heartbeat``/``end`` 已废弃，
    被 ``session_worktree_start``（FP-ISO.4C worktree 物理隔离）+ ``HELD-OVERLAP`` gate
    完全替代且更强（编辑前软预警 -> commit 时硬阻断）。零实际调用方（死代码）。
    AI 对话启动请改用 ``zephyr.gov_enforcement.rule_bridge.session_worktree.session_worktree_start``。
    ``generate_session_id`` 保留（纯函数，被 ``session_worktree.py`` 调用）。

提供 AI 对话启动时的 session 注册 + 文件 claim + 冲突检测 + 心跳续期 + 结束
释放一体化接口。适配 Trae IDE「共享工作目录 + 多 AI 对话并发」模式——编辑期
靠 AI 自觉 claim（软约束），提交期 GitCommitGateway 硬校验（SessionRequiredGate
+ ClaimRequiredGate + HeldOverlapGate）。

核心工作流（AI 对话生命周期）::

    1. 对话启动 -> session_claim_start(session_id, files=[...])
       -> 注册 session + claim 将修改的文件
       -> 冲突文件返回 conflict=True，AI 等待或换文件
    2. 改新文件前 -> session_claim_add(session_id, file)
       -> 追加声明，冲突时 conflict=True
    3. 长对话续期 -> session_claim_heartbeat(session_id)
       -> 防 TTL 过期（默认 3600s）
    4. 对话结束 -> session_claim_end(session_id)
       -> 释放所有 claim + 注销 session

session_id 生成（Trae 对话无内置 session_id）::

    sess-{PID}-{yyyyMMddHHmmss}
    例：sess-12345-20260701143025

Usage（AI 通过 RunCommand 调用）::

    python -c "
    from zephyr.gov_enforcement.rule_bridge.session_claim import session_claim_start, session_claim_add, session_claim_end
    sid = 'sess-12345-20260701143025'
    r = session_claim_start(sid, files=['src/foo.py', 'docs/bar.md'])
    print(r)  # {'session_id': ..., 'claimed': [...], 'conflicts': [...]}
    "

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: claim 请求入参
#   fields: session_id + files 列表 / 单个 file
#   code: session_claim_start(session_id, files) L96-100 / session_claim_add(session_id, file) L150-153
# - id: I2
#   name: SessionRegistry 注册表
#   fields: 各 session 的 held_files / pid / 时间戳（共享 JSON 注册表）
#   code: SessionRegistry(REPO_ROOT) L81-84
# 层: 算法
# - id: A1
#   name_zh: ① session_id 生成
#   name_en: generate_session_id
#   intro: Trae 对话没有内置 session_id，用进程号+时间戳拼一个全局唯一的
#   desc: f"sess-{os.getpid()}-{time.strftime('%Y%m%d%H%M%S')}" L87-93（纯函数，仍在被 session_worktree 使用）
#   inputs: I1
#   outputs: sess-{PID}-{yyyyMMddHHmmss}
#   invariant: 格式 sess-{PID}-{14位时间戳}
# - id: A2
#   name_zh: ② 注册并批量 claim（已废弃）
#   name_en: session_claim_start
#   intro: 对话启动时原子注册 session 再逐个 claim 文件，冲突的记下来告诉 AI 换文件
#   desc: registry.register(pid, held_files=[]) L119 → 逐个 claim_file，失败查 owner 记 conflicts L131-141；零实际调用方（死代码，FP-ISO.4C 已取代）
#   inputs: I1 I2
#   outputs: {claimed, conflicts}
# - id: A3
#   name_zh: ③ 追加 claim 与写前检测（已废弃）
#   name_en: session_claim_add / session_claim_check
#   intro: 改新文件前先 claim 或只查不占，冲突时返回 conflict=True 让 AI 等待（软约束）
#   desc: add: session 不存在返回 not_found → claim_file 失败查 owner 返回 conflict=True L168-196；check: other_held_files 命中则报 owner，仅查询不占用 L207-230
#   inputs: I1 I2
#   outputs: {claimed/conflict/owner} 或 {clear/owner}
# - id: A4
#   name_zh: ④ 续期与结束释放（已废弃）
#   name_en: session_claim_heartbeat / session_claim_end
#   intro: 长对话定期续期防 TTL 过期；对话结束释放所有 claim 并注销 session
#   desc: heartbeat → registry.heartbeat(sid) L233-249；end → 遍历 held_files 逐个 release_file → unregister L252-286；全程不抛异常
#   inputs: I1 I2
#   outputs: {renewed} / {released, unregistered}
# 层: 输出
# - id: O1
#   name_zh: claim 操作结果 dict
#   name_en: dict
#   intro: claimed/conflicts/owner 等字段，conflict=True 时 AI 须等待或换文件
#   invariant: 所有函数返回 dict 不抛异常
#   downstream: 无下游（session_claim_* 已废弃，零调用方）
# - id: O2
#   name_zh: 唯一 session_id 字符串
#   name_en: str
#   intro: sess-{PID}-{时间戳} 格式的会话标识，供 worktree 生命周期使用
#   downstream: session_worktree MOD-GOV_SESSION_WORKTREE（# [CONSUMERS] 头：generate_session_id 仍被调用）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O2
# I1 --> A2
# I2 --> A2
# I1 --> A3
# I2 --> A3
# I1 --> A4
# I2 --> A4
# A2 --> O1
# A3 --> O1
# A4 --> O1
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

__all__ = [
    "session_claim_start",
    "session_claim_add",
    "session_claim_check",
    "session_claim_heartbeat",
    "session_claim_end",
    "generate_session_id",
]

import os
import time
from pathlib import Path

from zephyr.security.access_control.session_concurrency import SessionRegistry
from zephyr.shared.io.paths import REPO_ROOT


def _get_registry(project_root: str | Path | None = None) -> SessionRegistry:
    """获取 SessionRegistry 实例。"""
    root = Path(project_root) if project_root else REPO_ROOT
    return SessionRegistry(root)


def generate_session_id() -> str:
    """生成全局唯一 session_id。

    格式：sess-{PID}-{yyyyMMddHHmmss}
    Trae 对话无内置 session_id，AI 启动时调用本函数生成。
    """
    return f"sess-{os.getpid()}-{time.strftime('%Y%m%d%H%M%S')}"


def session_claim_start(
    session_id: str,
    files: list[str] | None = None,
    project_root: str | Path | None = None,
) -> dict:
    """AI 对话启动第一步：注册 session + claim 文件。

    原子操作：先 register session，再逐个 claim_file。冲突文件跳过并记录到 conflicts。

    Args:
        session_id: session 标识（建议用 generate_session_id() 生成）
        files: 将修改的文件列表（绝对路径或相对 project_root 的路径）
        project_root: 项目根目录（默认 REPO_ROOT）

    Returns:
        {"session_id": str, "claimed": list[str], "conflicts": list[dict]}
        conflicts 元素：{"file": str, "owner": str}（owner 为持有该文件的其他 session_id）
    """
    registry = _get_registry(project_root)
    files = files or []

    # 注册 session（pid + 空 held_files，后续逐个 claim）
    try:
        registry.register(session_id, pid=os.getpid(), held_files=[])
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        return {
            "session_id": session_id,
            "claimed": [],
            "conflicts": [],
            "error": f"register failed: {e}",
        }

    claimed: list[str] = []
    conflicts: list[dict] = []

    for f in files:
        try:
            ok = registry.claim_file(session_id, f)
            if ok:
                claimed.append(f)
            else:
                # claim 失败 = 文件被其他 session 持有，查 owner
                owner = _find_file_owner(registry, f, exclude_session=session_id)
                conflicts.append({"file": f, "owner": owner or "unknown"})
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            conflicts.append({"file": f, "owner": "error", "error": str(e)})

    return {
        "session_id": session_id,
        "claimed": claimed,
        "conflicts": conflicts,
    }


def session_claim_add(
    session_id: str,
    file: str,
    project_root: str | Path | None = None,
) -> dict:
    """追加 claim 单个文件（AI 改新文件前调用）。

    Args:
        session_id: 已注册的 session_id
        file: 要 claim 的文件（绝对路径或相对 project_root）

    Returns:
        {"session_id": str, "file": str, "claimed": bool, "conflict": bool, "owner": str | None}
        conflict=True 时 AI MUST 等待或换文件（软约束，AGENTS.md 规定）
    """
    registry = _get_registry(project_root)

    # 检查 session 是否存在
    info = registry.get_session(session_id)
    if info is None:
        return {
            "session_id": session_id,
            "file": file,
            "claimed": False,
            "conflict": False,
            "not_found": True,
            "error": f"session '{session_id}' 未注册，先调 session_worktree_start（session_claim_start 已废弃）",
        }

    try:
        ok = registry.claim_file(session_id, file)
        if ok:
            return {
                "session_id": session_id,
                "file": file,
                "claimed": True,
                "conflict": False,
            }
        else:
            owner = _find_file_owner(registry, file, exclude_session=session_id)
            return {
                "session_id": session_id,
                "file": file,
                "claimed": False,
                "conflict": True,
                "owner": owner or "unknown",
            }
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        return {
            "session_id": session_id,
            "file": file,
            "claimed": False,
            "conflict": False,
            "error": str(e),
        }


def session_claim_check(
    file: str,
    session_id: str,
    project_root: str | Path | None = None,
) -> dict:
    """写前检测：文件是否被其他 session 持有（不 claim，仅查询）。

    AI 编辑文件前可调用本函数检测冲突（软约束，非强制）。

    Returns:
        {"file": str, "clear": bool, "owner": str | None}
        clear=True 表示文件无人持有或仅被当前 session 持有，可安全编辑
    """
    registry = _get_registry(project_root)
    try:
        other_held = registry.other_held_files(session_id)
        from pathlib import Path as _Path

        target = str(_Path(file).resolve())
        if target in other_held:
            owner = _find_file_owner(registry, file, exclude_session=session_id)
            return {"file": file, "clear": False, "owner": owner or "unknown"}
        return {"file": file, "clear": True, "owner": None}
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        return {"file": file, "clear": True, "owner": None, "error": str(e)}


def session_claim_heartbeat(
    session_id: str,
    project_root: str | Path | None = None,
) -> dict:
    """续期 session（防 TTL 过期，默认 3600s）。

    长对话（>1h）建议每 30min 调用一次。

    Returns:
        {"session_id": str, "renewed": bool}
    """
    registry = _get_registry(project_root)
    try:
        ok = registry.heartbeat(session_id)
        return {"session_id": session_id, "renewed": ok}
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        return {"session_id": session_id, "renewed": False, "error": str(e)}


def session_claim_end(
    session_id: str,
    project_root: str | Path | None = None,
) -> dict:
    """结束 session，释放所有 claim。

    AI 对话结束（任务完成）时调用。释放所有 held_files 并注销 session。

    Returns:
        {"session_id": str, "released": list[str], "unregistered": bool}
    """
    registry = _get_registry(project_root)

    # 获取当前 held_files
    info = registry.get_session(session_id)
    released: list[str] = []
    if info is not None:
        for f in info.held_files:
            try:
                registry.release_file(session_id, f)
                released.append(f)
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("suppressed error in session_claim", exc_info=True)

    # 注销 session
    try:
        unregistered = registry.unregister(session_id)
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        unregistered = False

    return {
        "session_id": session_id,
        "released": released,
        "unregistered": unregistered,
    }


def _find_file_owner(
    registry: SessionRegistry,
    file: str,
    exclude_session: str,
) -> str | None:
    """查找持有 file 的其他 session（排除 exclude_session）。

    遍历所有 session 的 held_files，返回第一个匹配的 session_id。
    """
    try:
        target = str(Path(file).resolve())
        # other_held_files 返回路径集合，不含 owner 信息
        # 需要遍历 sessions 查找 owner
        # SessionRegistry 没有 list_all_sessions 接口，用 other_held_files 确认冲突
        # 但要找 owner 需要访问内部数据
        data = registry._load()  # 读取 registry JSON
        for sid, sinfo in data.items():
            if sid == exclude_session:
                continue
            held = sinfo.get("held_files", [])
            for hf in held:
                if str(Path(hf).resolve()) == target:
                    return sid
        return None
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return None
