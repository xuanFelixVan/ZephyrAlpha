# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.held_overlap_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] allow_overlap=True 时直接放行（逃生通道）；other_held_files 读取异常安全降级为空集（不阻断 commit，registry 故障不应卡死工作流）；目标文件用 Path.resolve() 归一化与 other_held 比较（与 _normalize_file_path 对齐）；.ailocks 双轨检查（红蓝 v4 F2 治本 2026-09-14）：held_files 与 .ailocks 双轨脱节（失败提交释放 held_files 但 .ailocks 存活 30min TTL），目标文件存在其他会话的活跃 .ailocks 锁同样阻断，锁系统异常降级空集对齐既有契约
# [MODIFY-GUARD] gate_id="HELD-OVERLAP"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——registry 读取异常降级为空集（other_held=set()）
# [TESTS] tests/governance/commit_gates/test_held_overlap_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
held_overlap_gate.py — 搭便车防护门禁（HELD-OVERLAP，2026-06-30 治本）

检测 commit 目标文件是否被其他**活跃** session 持有，命中则阻断
（``HELD_OVERLAP_VIOLATION``）。``allow_overlap=True`` 时放行（逃生通道），
由调用方在 commit message 追加 ``[GW:<sid>:overlap]`` 标记供审计追踪。

病根（L4 元问题）
-----------------
同文件多 session 修改是高风险反模式——GitCommitGateway 文件级隔离无法分离
同一文件内两个 session 的行级修改，后提交的 session 会把工作区内的全部修改
（含前一个 session 的 WIP）一并提交（"搭便车提交"/ghost commit）。

本 gate 在 **commit 时**（而非编辑时）阻断，不影响编辑自由。从源头避免优于
事后行级隔离（行级隔离前置依赖编辑器层行归属追踪，不可控）。

归一化一致性
-------------
``SessionRegistry.other_held_files`` 返回 ``_normalize_file_path`` 归一化的
绝对路径（``Path.resolve()``），本 gate 用 ``str(Path(f).resolve())`` 归一化
目标文件，与 ``_get_session_held_non_target`` 的比较方式一致。

Usage::

    from zephyr.gov_enforcement.commit_gates.held_overlap_gate import make_held_overlap_gate

    registry.register(make_held_overlap_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, allow_overlap=False)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: held_overlap_gate.py
# 层: 算法
# - id: A1
#   name_zh: ① make_held_overlap_gate
#   name_en: make_held_overlap_gate
#   intro: 构造搭便车防护门禁 GateSpec。
#   desc: 构造搭便车防护门禁 GateSpec。 Returns: GateSpec(gate_id="HELD-OVERLAP", priority=50)。 priority=50 优…；源码 L82-L124
#   inputs: 无参数
#   outputs: GateSpec
# 层: 输出
# - id: O1
#   name_zh: GateSpec
#   name_en: GateSpec
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import os
from pathlib import Path

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

__all__ = ["make_held_overlap_gate"]


def _ailocks_other_holders(gateway, files: list[str], session_id: str) -> tuple[list[str], list[str]]:
    """检查目标文件的 .ailocks 文件锁是否被其他会话持有（红蓝 v4 F2 治本）。

    背景：SessionRegistry.held_files 与 .ailocks（scripts/lock_files.py 的磁盘锁，
    TTL 30 分钟 / PID 死亡即 stale）是双轨制——失败提交会释放 held_files 但
    .ailocks 依然存活，搭便车会话在窗口期打包他 session 未提交改动可绕过
    HELD-OVERLAP（v4 F2 实弹击穿）。本函数补齐第二轨。

    算法：与 lock_files._sanitize_path/_lock_dir 同款——目标文件路径直接算出锁
    目录，读 owner.json 判定持有者。判活双格式（裁定#252，2026-09-14）：
    ① owner.json 含 session_id → 锁存活=会话存活（复用 SessionRegistry
    _is_session_alive 判活真源：pid>0 双判活 / pid=0 心跳 90s）；
    ② 无 session_id 的旧格式锁 → TTL-only（与 lock_files._is_stale 的 PID 僵尸
    语义有意分歧：lock 锁由瞬时 CLI 进程领取、PID 必死，按 PID 判废会让防护永不
    命中——v4/v4.5 实弹复验实证；误拦风险由 --allow-overlap 逃生口+TTL 上界双保险）。

    fail-open：锁目录结构缺失/读取异常降级为空清单（锁系统故障不卡死工作流，
    对齐 held_files 的降级契约）。
    """
    holders: list[str] = []
    hits: list[str] = []
    try:
        import json as _json
        import time

        lock_root = Path(str(gateway.project_root)) / ".ailocks"
        if not lock_root.is_dir():
            return holders, hits
        now = time.time()
        for f in files:
            try:
                lock_dir = _ailocks_lock_dir_for(f, lock_root)
                if not lock_dir.is_dir():
                    continue
                owner_file = lock_dir / "owner.json"
                if not owner_file.is_file():
                    continue
                owner = _json.loads(owner_file.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001 — 单文件锁读取异常跳过
                continue
            holder = str(owner.get("owner_id", ""))
            if not holder or holder == session_id:
                continue
            # 判活双格式（裁定#252）：带 session_id → 会话存活优先；旧格式 → TTL-only
            bound_session = str(owner.get("session_id", "") or "")
            if bound_session:
                try:
                    from zephyr.security.access_control.session_concurrency import (
                        SessionRegistry,
                        _is_session_alive,
                    )

                    info = SessionRegistry(str(gateway.project_root)).get_session(bound_session)
                    if info is None or not _is_session_alive(info, now):
                        continue  # 绑定会话已死 → 锁 stale（跳过，不阻断）
                    # 会话存活 → 锁有效（仍受 expires_at 兑底，见下）
                except Exception:  # noqa: BLE001 — registry 不可达退 TTL 兑底
                    pass
            expires_at = owner.get("expires_at")
            if expires_at is not None:
                if now > float(expires_at):
                    continue
            else:
                ts = float(owner.get("timestamp", 0.0) or 0.0)
                if now - ts > 1800.0:
                    continue
            if holder not in holders:
                holders.append(holder)
            if f not in hits:
                hits.append(f)
    except Exception:  # noqa: BLE001 — 锁系统故障降级（不阻断工作流）
        return [], []
    return holders, hits


def _ailocks_lock_dir_for(file_path: str, lock_root: Path) -> Path:
    """与 scripts/lock_files.py _sanitize_path/_lock_dir 同款算法（双轨一致性真源）。"""
    rel = Path(file_path)
    repo_root = Path(str(gateway_project_root_safe(lock_root)))
    if rel.is_absolute():
        try:
            rel = rel.relative_to(repo_root)
        except ValueError:
            pass
    sanitized = str(rel).replace("\\", ".").replace("/", ".").replace("..", "_dotdot_")
    sanitized = "".join(c for c in sanitized if c.isalnum() or c in "._-")
    return lock_root / (sanitized.lower()[:120] + ".lock")


def gateway_project_root_safe(lock_root: Path) -> str:
    """从 lock_root（<root>/.ailocks）反推项目根。"""
    return str(lock_root.parent)


def make_held_overlap_gate() -> GateSpec:
    """构造搭便车防护门禁 GateSpec。

    Returns:
        GateSpec(gate_id="HELD-OVERLAP", priority=50)。
        priority=50 优先于大部分校验执行（搭便车是根因级问题，早阻断早省事）。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        allow_overlap = kwargs.get("allow_overlap", False)
        if allow_overlap:
            # 逃生通道：显式声明放行，调用方负责追加 [GW:<sid>:overlap] 标记
            return True, ""

        session_id = kwargs.get("session_id", "")
        try:
            other_held = gateway._registry.other_held_files(session_id)
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            # registry 读取异常 -> 安全降级为空集（不阻断）
            # 理由：registry 故障不应卡死 commit 工作流；
            #       stash 隔离层（_get_session_held_non_target）同样降级为空集
            other_held = set()

        # 归一化目标文件（与 _normalize_file_path 的 Path.resolve() 对齐）
        target_abs = {str(Path(f).resolve()) for f in files}
        overlap = target_abs & other_held

        # .ailocks 第二轨检查（红蓝 v4 F2 治本 2026-09-14）：held_files 与 .ailocks
        # 双轨脱节——失败提交释放 held_files 但 .ailocks 存活，搭便车窗口期可打包
        # 他 session 未提交改动入库。目标文件存在他 session 的活跃锁 → 阻断。
        ailocks_holders, ailocks_hits = _ailocks_other_holders(gateway, files, session_id)

        if overlap or ailocks_holders:
            if overlap:
                overlap_rel = sorted(
                    # 显示相对路径更易读（调试用）
                    str(Path(f).relative_to(gateway.project_root))
                    if Path(f).resolve().is_relative_to(gateway.project_root)
                    else f
                    for f in files
                    if str(Path(f).resolve()) in overlap
                )
                holders_txt = "其他活跃 session"
            else:
                overlap_rel = sorted(ailocks_hits)
                holders_txt = "/".join(sorted(set(ailocks_holders)))
            track = "" if overlap else "（.ailocks 双轨命中）"
            return False, (
                f"目标文件被其他活跃 session 持有（搭便车防护 HELD_OVERLAP_VIOLATION{track}）: "
                f"{overlap_rel}. 持有者={holders_txt}。"
                f" 如确认需提交，等锁释放或用 commit(allow_overlap=True) / "
                f"CLI --allow-overlap 逃生通道。"
            )
        return True, ""

    return GateSpec(gate_id="HELD-OVERLAP", check=_check, priority=50)
