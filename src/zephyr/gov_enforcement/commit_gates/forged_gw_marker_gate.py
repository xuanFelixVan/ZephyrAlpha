# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); zephyr.security.access_control.session_concurrency (SessionRegistry)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——commit message 含 [GW: 标记但 session_id 未在 SessionRegistry 注册且 ZEPHYR_COMMIT_GATEWAY env 未设置时阻断（passed=False，forged_gw_marker=intentional fraud）；无 [GW: 标记放行（non-GW commit 由 GATE-COMMIT-GW hook 兜底）；session_id 已注册放行（合法 GW commit）；ZEPHYR_COMMIT_GATEWAY=1 env 放行（GW 内部调用，逃生通道）；commit msg 缺失放行（其他 gate 已检查）；merge commit 放行（由 session_worktree 生成，标记合法）
# [MODIFY-GUARD] gate_id="FORGED-GW-MARKER"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]；GW 标记正则 _GW_MARKER_RE；session_id 提取正则 _SESSION_ID_RE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——SessionRegistry 读取异常降级为放行（避免 registry 损坏阻断所有 commit）；正则解析异常降级为放行（保守不阻断）
# [TESTS] tests/governance/commit_gates/test_forged_gw_marker_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: 无时间触发
"""forged_gw_marker_gate.py — Forged GW Marker 前置检测门禁（FORGED-GW-MARKER，#ARCH-PREVENTABILITY-LAYER-001 Phase 2）

检测 commit message 中的 ``[GW:*]`` 标记是否由 GitCommitGateway 合法写入。
未注册 session_id 且无 ``ZEPHYR_COMMIT_GATEWAY=1`` env 的标记 = 伪造（intentional fraud）→ 硬阻断。

第 6 层"可预防性"首批 pre-commit gate 落地（裁定 #ARCH-PREVENTABILITY-LAYER-001 Phase 2）
--------------------------------------------------------------------------------------
当前 forged_gw_marker 检测在 ``scripts/governance/git_hooks/post_commit_guard.sh`` L178-194，
post-commit 只能 ``git reset --soft HEAD~1``（commit 已入历史）。本 gate 前移到 pre-commit，
在 ``GitCommitGateway.commit()`` → ``_commit_locked()`` 之前执行，真正阻断伪造 commit 入历史。

设计权衡
--------
1. **硬阻断而非 warn-only**：forged_gw_marker 语义最严重（intentional fraud），不可 warn 放行
2. **只检测 GW 路径**：本 gate 在 GitCommitGateway 内部触发（in-process），无法防御裸 ``git commit``
   （那条路径由 GATE-COMMIT-GW hook 兜底）；本 gate 防御的是"AI 在 commit message 手工添加
   [GW:fake-session] 标记以绕过 abuse monitor"的攻击向量
3. **env 逃生通道**：``ZEPHYR_COMMIT_GATEWAY=1`` 是 GitCommitGateway 内部调用时注入的 env，
   合法 GW commit 一定带此 env；AI 手工伪造 commit 不会设置此 env → 区分合法与伪造
4. **merge commit 放行**：merge commit 由 session_worktree 生成，标记格式 ``[GW:sid:merge]``，
   session_id 已注册，自然通过本 gate

判定逻辑（与 post_commit_guard.sh L50-95 对齐）
------------------------------------------------
- commit msg 不含 ``[GW:`` → 放行（non-GW commit，由 GATE-COMMIT-GW 兜底）
- 含 ``[GW:`` + session_id 已注册 → 放行（合法 GW commit）
- 含 ``[GW:`` + session_id 未注册 + ``ZEPHYR_COMMIT_GATEWAY=1`` env → 放行（GW 内部逃生通道）
- 含 ``[GW:`` + session_id 未注册 + 无 env → **阻断**（forged_gw_marker）

关联
----
- 裁定: #ARCH-PREVENTABILITY-LAYER-001 Phase 2（R6 治本，第 6 层可预防性 pre-commit gate 配对）
- 母规则: trae_068_preventability_layer.yaml（enforcement.paired_gate_id = "FORGED-GW-MARKER"）
- 现有 post-commit 检测: scripts/governance/git_hooks/post_commit_guard.sh L178-194
- 统计 reconciler: commit_gateway_abuse_monitor_reconciler.py L222-227（24h 长窗口，不可前移）
- GW 标记生成: git_commit_gateway.py L174 ``_GW_MARKER_FMT = "[GW:{session_id}]"``
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec
from zephyr.security.access_control.session_concurrency import SessionRegistry

# [GW: 标记检测正则（与 post_commit_guard.sh L50 grep '\[GW:' 对齐）
_GW_MARKER_RE = re.compile(r"\[GW:")

# session_id 提取正则（与 post_commit_guard.sh L54 sed 's/.*\[GW:\(sess-[^]:}]*\).*/\1/p' 对齐）
# 匹配 [GW:sess-xxx] / [GW:sess-xxx:overlap] / [GW:sess-xxx:auto] / [GW:sess-xxx:merge] 等
_SESSION_ID_RE = re.compile(r"\[GW:(sess-[^\]:}]*)")

# 逃生通道 env（与 git_commit_gateway.py L174 _GATEWAY_ENV 对齐）
_GATEWAY_ENV = "ZEPHYR_COMMIT_GATEWAY"


def _extract_session_id(commit_msg: str) -> str | None:
    """从 commit message 提取 [GW:session_id] 标记中的 session_id。

    与 post_commit_guard.sh L54 sed 对齐：要求 sess- 前缀。
    多个标记时取第一个（与 shell head -1 对齐）。

    Args:
        commit_msg: commit message 全文

    Returns:
        session_id 字符串；无标记或解析失败返回 None
    """
    if not commit_msg:
        return None
    match = _SESSION_ID_RE.search(commit_msg)
    if not match:
        return None
    return match.group(1)


def _is_session_registered(project_root: str | Path, session_id: str) -> bool:
    """检查 session_id 是否在 SessionRegistry 中注册。

    与 post_commit_guard.sh L70 grep '"$session_id"' registry_file 对齐，
    但用 Python API 替代 shell grep（更可靠）。

    Args:
        project_root: 项目根路径
        session_id: 待校验的 session_id

    Returns:
        True=已注册（合法）；False=未注册（疑似伪造）；registry 异常降级为 False（保守阻断）
    """
    try:
        registry = SessionRegistry(project_root)
        # SessionRegistry 只有 get_session，没有 .get——原 registry.get(session_id)
        # 抛 AttributeError 被 except 吞掉→返回 False（保守阻断），导致任何 sess- 前缀
        # session 的合法 GW commit 被误判为 forged marker。修正为 get_session。
        info = registry.get_session(session_id)
        return info is not None
    except Exception:
        # registry 读取异常——降级为"未注册"（保守阻断，防 registry 损坏导致伪造放行）
        # 注：此降级可能导致合法 commit 在 registry 损坏时被阻断，但优于"伪造放行"
        return False


def make_forged_gw_marker_gate() -> GateSpec:
    """构造 Forged GW Marker 前置检测 GateSpec。

    Returns:
        GateSpec(gate_id="FORGED-GW-MARKER", priority=29)。
        priority=29 早于 DIRECTORY-CONTRACT=30 和 SESSION-REQUIRED=31，确保 GW 标记合法性最先检查。
    """

    def _check(gateway: object, files: list[str], **kwargs: Any) -> tuple[bool, str]:
        """检测 commit message 中 [GW:*] 标记合法性。

        判定逻辑：
        - 无 [GW: 标记 → 放行（non-GW commit 由 GATE-COMMIT-GW hook 兜底）
        - 含 [GW: + session_id 已注册 → 放行（合法 GW commit）
        - 含 [GW: + session_id 未注册 + ZEPHYR_COMMIT_GATEWAY=1 env → 放行（GW 内部逃生通道）
        - 含 [GW: + session_id 未注册 + 无 env → 阻断（forged_gw_marker）
        """
        # 1. 获取 commit message
        commit_msg: str | None = kwargs.get("commit_message") or kwargs.get("message")
        if not commit_msg:
            # commit msg 缺失——其他 gate（如 SESSION-REQUIRED）已检查，本 gate 放行
            return True, "commit_message missing, skip forged_gw_marker check"

        # 2. 无 [GW: 标记 → 放行（non-GW commit 由 GATE-COMMIT-GW hook 兜底）
        if not _GW_MARKER_RE.search(commit_msg):
            return True, "no [GW: marker in commit message"

        # 3. 提取 session_id
        session_id = _extract_session_id(commit_msg)
        if not session_id:
            # 含 [GW: 但无法解析 session_id——保守放行（可能是不规范但非伪造）
            # post_commit_guard.sh L58 同样保守放行
            return True, "[GW: marker present but session_id unparseable, conservatively pass"

        # 4. 检查 session_id 是否已注册
        project_root = getattr(gateway, "project_root", None)
        if project_root is None:
            # gateway 无 project_root——无法校验，保守放行
            return True, "gateway.project_root missing, cannot verify session registration"

        # 调公共 wrapper is_session_registered（非私有 _is_session_registered）——
        # Stage 4 公共化（commit c8b1b8e493）后公共 wrapper 是模块级名字，
        # 测试 patch "...forged_gw_marker_gate.is_session_registered" 才能命中。
        if is_session_registered(project_root, session_id):
            # session_id 已注册 → 合法 GW commit
            return True, f"[GW:{session_id}] session registered, legitimate GW marker"

        # 5. session_id 未注册——检查 ZEPHYR_COMMIT_GATEWAY env 逃生通道
        if os.environ.get(_GATEWAY_ENV) == "1":
            # env 设置 → GW 内部调用（合法逃生通道）
            return True, f"[GW:{session_id}] session unregistered but {_GATEWAY_ENV}=1 env set, emergency escape"

        # 6. session_id 未注册 + 无 env → 伪造（intentional fraud）
        return False, (
            f"FORGED-GW-MARKER: commit message contains [GW:{session_id}] but session_id "
            f"is not registered in SessionRegistry and {_GATEWAY_ENV}=1 env is not set. "
            f"This is intentional fraud (AI 手工伪造 GW 标记以绕过 abuse monitor). "
            f"Fix: use GitCommitGateway.commit() instead of bare git commit, or remove "
            f"the [GW:*] marker from commit message."
        )

    return GateSpec(gate_id="FORGED-GW-MARKER", check=_check, priority=29)


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def is_session_registered(project_root, session_id) -> bool:
    """公共接口：is_session_registered（Stage 4 公共化）。"""
    return _is_session_registered(project_root, session_id)
