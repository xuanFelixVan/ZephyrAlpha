# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); zephyr.security.access_control.session_concurrency (SessionRegistry)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——commit message 含非本 session 的 [GW:标识符 标记 → 阻断（伪造/嫁祸，无论目标是否注册）；标记全部为本 session → 放行（自身冗余留痕既有惯例）；无 [GW:标识符 标记放行（non-GW commit 由 GATE-COMMIT-GW hook 兜底，"[GW: 空格"文档性提及放行）；commit msg 缺失放行（其他 gate 已检查）；无 session_id kwarg 时退回注册表校验（全部已注册放行/任一未注册阻断）；env 逃生废除（2026-09-14 P1-1 治本：gate 只见用户 message，网关标记在 gate 后追加，用户 message 中的外来标记无合法来源；os.environ 进程级全局可被并发污染不可作凭据）
# [MODIFY-GUARD] gate_id="FORGED-GW-MARKER"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]；session_id 提取正则 _SESSION_ID_RE（广义标识符口径，与 post_commit_guard.sh grep 对齐）
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
3. **env 逃生废除（P1-1 治本 2026-09-14）**：原设计用 ``ZEPHYR_COMMIT_GATEWAY=1`` env
   区分合法与伪造——但 os.environ 是进程级全局，并发 commit 线程间可互相污染（一线程
   commit 中设置的 env 在另一线程 gate 检查窗口可见），且 gate 只见用户 message（网关
   标记在 gate 之后追加），用户 message 中的外来标记没有任何合法来源需要 env 豁免。
   新语义：非本 session 标记一律阻断，与 env 无关。env 仍保留在 post_commit_guard.sh
   （那里校验的是含网关追加标记的 full message，env 用于区分网关路径与会话过期场景）
4. **merge commit 放行**：merge commit 由 session_worktree 生成，标记格式 ``[GW:sid:merge]``，
   session_id 已注册，自然通过本 gate

判定逻辑（P1-1 治本 2026-09-14 重设计，红蓝 v3 c224e15d63 实证）
----------------------------------------------------------------
- commit msg 不含 [GW:标识符 → 放行（non-GW commit 由 GATE-COMMIT-GW hook 兜底）
- 含标记 + 全部为本 session（session_id kwarg）→ 放行（自身冗余留痕既有惯例）
- 含标记 + 存在非本 session 标记 → **阻断**（伪造/嫁祸，无论目标 session 是否注册；
  env 逃生废除——gate 只见用户 message，网关标记在 gate 后追加，外来标记无合法来源）
- 无 session_id kwarg（隔离调用）→ 注册表校验兜底：全部已注册放行 / 任一未注册阻断

治本背景（红蓝 v3 S1.9，2026-09-14）：原 sess- 前缀提取正则对现行会话命名
（solo_agent/xt3-*/st-*/factory-* 等）全盲——提取恒 None 走"unparseable 保守放行"，
伪造标记 [GW:xt3-fake-session:multi-domain] 经网关零拦截落库（c224e15d63）；
即使提取成功还有 env 逃生通道可绕（os.environ 进程级全局，并发 commit 下可被污染）。
三层畅通 → 本 gate 语义整体重设计。

关联
----
- 裁定: #ARCH-PREVENTABILITY-LAYER-001 Phase 2（R6 治本，第 6 层可预防性 pre-commit gate 配对）
- 母规则: trae_068_preventability_layer.yaml（enforcement.paired_gate_id = "FORGED-GW-MARKER"）
- 现有 post-commit 检测: scripts/governance/git_hooks/post_commit_guard.sh L178-194
- 统计 reconciler: commit_gateway_abuse_monitor_reconciler.py L222-227（24h 长窗口，不可前移）
- GW 标记生成: git_commit_gateway.py L174 ``_GW_MARKER_FMT = "[GW:{session_id}]"``
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec
from zephyr.security.access_control.session_concurrency import SessionRegistry

# session_id 提取正则（P1-1 治本 2026-09-14，红蓝 v3 c224e15d63 实证）
# 病根：原 sess- 前缀口径对现行会话命名（solo_agent/xt3-*/st-*/factory-* 等）
# 全盲——提取恒 None → "unparseable 保守放行" → 伪造标记畅通入库
# （红蓝 v3 S1.9 实弹：[GW:xt3-fake-session:multi-domain] 经网关零拦截落库）。
# 新口径：[GW: 后紧跟标识符首字符（字母/数字/下划线），后接 [A-Za-z0-9_-]*
# （与 post_commit_guard.sh grep -o '\[GW:[A-Za-z0-9_][A-Za-z0-9_-]*' 对齐）。
# [GW: 后是空格/标点（文档性提及「[GW: 标记」）不匹配 → 放行。
# 匹配 [GW:solo_agent] / [GW:xt3-red:overlap] / [GW:sess-xxx:auto] / [GW:sid:merge] 等。
_SESSION_ID_RE = re.compile(r"\[GW:([A-Za-z0-9_][A-Za-z0-9_-]*)")


def _extract_session_id(commit_msg: str) -> str | None:
    """从 commit message 提取第一个 [GW:session_id] 标记中的 session_id。

    P1-1 治本（2026-09-14）：广义标识符口径（原 sess- 前缀对现行命名全盲，
    红蓝 v3 c224e15d63 实证伪造畅通）。文档性提及（``[GW: `` 后跟空格/标点）
    不匹配返回 None。

    Args:
        commit_msg: commit message 全文

    Returns:
        第一个标记的 session_id；无标记返回 None
    """
    if not commit_msg:
        return None
    match = _SESSION_ID_RE.search(commit_msg)
    if not match:
        return None
    return match.group(1)


def _extract_all_session_tokens(commit_msg: str) -> list[str]:
    """提取 commit message 中全部 [GW:session_id] 标记的 session_id（去重排序）。

    多标记全量校验用（防「首个合法+次个伪造」绕过——shell hook 原 head -1
    只查第一个，红蓝 v3 P1-1 治本配套）。
    """
    if not commit_msg:
        return []
    return sorted(set(_SESSION_ID_RE.findall(commit_msg)))


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
        """检测 commit message 中 [GW:*] 标记合法性（P1-1 治本 2026-09-14 语义重设计）。

        判定逻辑（红蓝 v3 c224e15d63 实证后治本——原 sess- 正则全盲 +
        unparseable 保守放行 + env 逃生 = 伪造标记三重畅通）：
        - commit_message 缺失 → 放行（其他 gate 已检查）
        - 无 [GW:标识符 标记（含「[GW: 空格」文档性提及）→ 放行
          （non-GW commit 由 GATE-COMMIT-GW hook 兜底）
        - 有 session_id kwarg（主网关/worktree 两条生产路径均透传）：
          * 全部标记 == 本 session → 放行（自身冗余留痕既有惯例——用户按
            网关指引手写 [GW:<sid>:multi-domain] 等旗标留痕，与网关自动
            追加的标记冗余但无害）
          * 存在非本 session 标记 → **阻断**（伪造或嫁祸已注册会话同为
            归因污染攻击向量；env 逃生废除——本 gate 只见用户 message，
            网关标记在 gate 之后追加，用户 message 中的非自身标记没有
            合法来源；os.environ 进程级全局可被并发 commit 污染，不可作凭据）
        - 无 session_id kwarg（隔离调用/测试）→ 退回注册表校验：
          全部已注册放行，任一未注册阻断（无 env 逃生）
        """
        # 1. 获取 commit message
        commit_msg: str | None = kwargs.get("commit_message") or kwargs.get("message")
        if not commit_msg:
            # commit msg 缺失——其他 gate（如 SESSION-REQUIRED）已检查，本 gate 放行
            return True, "commit_message missing, skip forged_gw_marker check"

        # 2. 提取全部 [GW:标识符 标记（广义标识符口径）
        tokens = _extract_all_session_tokens(commit_msg)
        if not tokens:
            # 无 [GW:标识符 标记（含文档性提及「[GW: 标记」）→ 放行
            # （non-GW commit 由 GATE-COMMIT-GW hook 兜底）
            return True, "no [GW: session marker in commit message"

        # 3. 生产路径判定（session_id kwarg 可用）：自身放行 / 外来阻断
        current_sid = kwargs.get("session_id") or ""
        if current_sid:
            foreign = [t for t in tokens if t != current_sid]
            if not foreign:
                # 全部为本 session 自身标记（冗余留痕既有惯例，无害）→ 放行
                return True, f"[GW:{current_sid}] self-marker(s) only, redundant but legitimate"
            return False, (
                f"FORGED-GW-MARKER: commit message 含非本 session 的 [GW: 标记 {foreign}"
                f"（本 session={current_sid}）。GW 标记由 GitCommitGateway/session_worktree "
                f"按旗标自动追加（allow_overlap/multi-domain/tracked-drift 等留痕），"
                f"用户 message 中出现非自身标记即伪造/嫁祸（红蓝 v3 c224e15d63 实证："
                f"伪造 [GW:xt3-fake-session:multi-domain] 经 sess- 前缀盲区畅通入库）。"
                f"修复：从 message 移除 [GW:...] 片段后重提；留痕标记由网关自动追加，"
                f"无需手写。"
            )

        # 4. 隔离调用兜底（无 session_id kwarg）→ 注册表校验
        project_root = getattr(gateway, "project_root", None)
        if project_root is None:
            # gateway 无 project_root——无法校验，保守放行
            return True, "gateway.project_root missing, cannot verify session registration"

        # 调公共 wrapper is_session_registered（非私有 _is_session_registered）——
        # Stage 4 公共化（commit c8b1b8e493）后公共 wrapper 是模块级名字，
        # 测试 patch "...forged_gw_marker_gate.is_session_registered" 才能命中。
        unregistered = [t for t in tokens if not is_session_registered(project_root, t)]
        if not unregistered:
            # 全部标记已注册 → 合法 GW commit
            return True, f"all [GW: markers registered: {tokens}, legitimate GW markers"

        # 5. 存在未注册标记 → 伪造（intentional fraud，无 env 逃生）
        return False, (
            f"FORGED-GW-MARKER: commit message contains unregistered [GW: markers "
            f"{unregistered}. This is intentional fraud (AI 手工伪造 GW 标记以绕过 "
            f"abuse monitor；红蓝 v3 c224e15d63 实证). "
            f"Fix: use GitCommitGateway.commit() instead of bare git commit, or remove "
            f"the [GW:*] marker from commit message."
        )

    return GateSpec(gate_id="FORGED-GW-MARKER", check=_check, priority=29)


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def is_session_registered(project_root, session_id) -> bool:
    """公共接口：is_session_registered（Stage 4 公共化）。"""
    return _is_session_registered(project_root, session_id)
