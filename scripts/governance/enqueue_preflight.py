# [BLUEPRINT] MOD-GOV-046 | scripts/governance/enqueue_preflight.py | §QCure-M1-M2
# [MODULE] scripts.governance.enqueue_preflight
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] stdlib；zephyr.gov_enforcement.rule_bridge.commit_preflight.run_preflight 与 git_commit_gateway.GitCommitGateway（均函数内延迟 import，锁外只读零副作用）
# [CONSUMERS] scripts.commit_queue（_read_files_from_worktree 冲突字节预扫 M2.2 / _cmd_enqueue 预检挂线 M1.1）；scripts.git_commit._enqueue_mode（经 _read_files_from_worktree 同款受益）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 入队口快败不是豁免——权威执行仍在锁内/落地链，预检只拦注定死信的单子；v1 skip 集={SESSION-REQUIRED, CLAIM-REQUIRED}（三裸入口会话多未注册，入队面 top1 拦截 379 次实证，全量接=假红风暴；skip 后落地侧兜底）；冲突判据保守（行首 7 字符+空格，======= 仅伴随开始/结束标记才算——纯 markdown setext 标题不误报；二进制 NUL/超限与 blob 上限同源跳过）；预检设施任何故障 degraded fail-open 放行，绝不堵入队；max_bytes 由调用方传本模块不复制常量（防双真源漂移）
# [MODIFY-GUARD] QCure st-qcure-20260925 施工件 M2.2/M1.1；skip 集与冲突判据变更须同步 tests/governance/test_enqueue_preflight.py 红蓝例与 docs/_working/qcure_campaign/producer_enqueue/workbook.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] scan_conflict_markers 纯函数不上抛（异常输入按跳过返回 None）；run_enqueue_preflight 永不上抛——网关构造/preflight 异常一律 warn+放行（degraded fail-open，对齐 commit_preflight 整体异常口径 PF:477）；阻断经返回处方文本由调用方 QueueReject 收口（exit 2）
# [TESTS] tests/governance/test_enqueue_preflight.py
# [A_module] module_id=MOD-GOV-046 | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""enqueue_preflight.py — 入队口预检（QCure M2.2 冲突标记字节预扫 + M1.1 预检挂线）。

真源：docs/_working/qcure_campaign/producer_enqueue/workbook.md（矿#1/#2/#6）、
bag_storage/workbook.md；业界参照 pre-commit check-merge-conflict 的教训
（pre-commit-hooks#300）——字节预扫必须无条件扫描，不依赖 merge 状态触发。

M2.2 冲突标记字节预扫
--------------------
历史 50 笔死因=快照带未解决合并冲突标记，拖到落地口才死（blob 已落袋+白烧 serializer
一轮）。本模块在 ``_read_files_from_worktree`` 读到字节后、blob 落袋前逐文件扫描，
保守判据：

- 行首 ``<<<<<<< `` / ``>>>>>>> ``（7 字符+空格）即命中；
- 行首 ``=======``（恰 7 个等号）仅在该文件同时含开始/结束标记时才算——纯 markdown
  setext ``=======`` 标题不误报；
- 二进制（含 NUL 字节）与超限（>max_bytes，与 ``commit_queue._MAX_BLOB_BYTES`` 同源）
  跳过。

M1.1 入队预检挂线
----------------
裸 CLI enqueue 在冲突扫之后、``enqueue_item`` 落袋之前调
``commit_preflight.run_preflight``（audit_event="enqueue"，与交互正门 GC:847-855 同一套
gate 白名单）。v1 skip 集={SESSION-REQUIRED, CLAIM-REQUIRED}：preflight_events 实测
SESSION-REQUIRED 是入队面 top1 拦截（379 次）——三裸入口的调用会话多未注册，全量接=
假红风暴；CLAIM-REQUIRED 因快照语义=入袋即完成（落地时按队列项 session claim，
GC:852 先例同款）。skip 不是豁免：落地失败照旧死信。blocking→返回逐门禁处方（调用方
QueueReject→exit 2）；预检异常/网关构造失败→warn+放行（degraded fail-open，对齐 PF
既有口径），绝不因预检故障堵入队。
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# M2.2 冲突标记字节预扫（历史 50 笔死因在入队口快败——blob 落袋前，零垃圾 blob）
# ---------------------------------------------------------------------------

# 拒收处方（exit 2 文案，宪法口径：处方给到一键可执行）
CONFLICT_MARKER_REJECT_PRESCRIPTION = (
    "快照含未解决合并冲突标记（历史 50 笔死因）：回会话 worktree 解决合并后重新入队，勿重投本袋"
)

_CONFLICT_START = b"<<<<<<<"  # 裸 7 字符行首判（红队 P1-1：与落地权威判据同宽，无空格也命中）
_CONFLICT_END = b">>>>>>>"
_CONFLICT_SEP = b"======="  # 仅伴随开始/结束标记才算（markdown setext 标题防误报）

_CONFLICT_MARKER_LABELS = {_CONFLICT_START: "开始标记", _CONFLICT_END: "结束标记"}


def scan_conflict_markers(relpath: str, content: bytes, *, max_bytes: int) -> str | None:
    """单文件合并冲突标记扫描（判据对齐落地权威 check_merge_conflict）。

    max_bytes 必填由调用方传（与 blob 上限同源——本模块刻意不复制常量防漂移）；
    超限跳过（enqueue_item 轻检另行拒收，预扫不重复报）；二进制（NUL 字节探测）跳过。
    红队 P1-1 对齐：开始/结束标记按裸 7 字符行首判（落地权威 regex 连无空格裸标记
    也命中——预扫漏判=白烧 serializer，故此处必须同宽）；首行剥 UTF-8 BOM（红队 P2）。
    ======= 分隔线保守保留（markdown setext 标题/水平线常态，仅伴随开始/结束才算）。
    """
    if max_bytes <= 0 or len(content) > max_bytes:
        return None
    if b"\x00" in content:
        return None  # 二进制跳过（NUL 字节探测）
    if content.startswith(b"\xef\xbb\xbf"):
        content = content[3:]  # BOM 剥离（防首行标记被 BOM 遮挡漏扫）
    has_start = has_end = has_sep = False
    first_hit: tuple[int, bytes] | None = None
    for lineno, line in enumerate(content.split(b"\n"), start=1):
        # 行首锚定：转义样例/行内注释（非行首）不误报；\r 结尾（CRLF）兼容；
        # 裸标记（无尾随空格）同判（红队 P1-1，与落地权威判据同宽）
        if line.startswith(_CONFLICT_START):
            has_start = True
            if first_hit is None:
                first_hit = (lineno, _CONFLICT_START)
        elif line.startswith(_CONFLICT_END):
            has_end = True
            if first_hit is None:
                first_hit = (lineno, _CONFLICT_END)
        elif line.rstrip(b"\r") == _CONFLICT_SEP:
            has_sep = True
    if first_hit is None:
        # 纯 ======= 文件（markdown setext 标题常态）不误报：分隔线仅在文件同时含
        # 开始/结束标记时才算（66 号保守判据，防 markdown 文档假红）
        return None
    lineno, marker = first_hit
    detail = f"[{relpath}] 第 {lineno} 行命中合并冲突{_CONFLICT_MARKER_LABELS[marker]} '{marker.decode()}'"
    if has_start and has_end and has_sep:
        detail += "（含完整三段冲突体）"
    return detail


# ---------------------------------------------------------------------------
# M1.1 入队预检挂线（三裸入口零预检补口；唯一曾有预检的是交互正门 GC:847-855）
# ---------------------------------------------------------------------------

# v1 skip 集：SESSION-REQUIRED（入队面 top1 拦截 379 次实证——三裸入口会话多未注册，
# 全量接=假红风暴）+ CLAIM-REQUIRED（快照语义=入袋即完成，落地时按队列项 session
# claim，GC:852 先例同款）。skip 不是豁免：权威执行在锁内/落地链，落地失败照旧死信。
ENQUEUE_SKIP_GATES = frozenset({"SESSION-REQUIRED", "CLAIM-REQUIRED"})


def run_enqueue_preflight(
    worktree_root: Path | str,
    files: list[str],
    session_id: str,
    message: str = "",
    *,
    gateway_factory: Callable[..., Any] | None = None,
    preflight_fn: Callable[..., Any] | None = None,
) -> str | None:
    """入队口预检（锁外只读）：返回 None=放行（含 degraded）；返回 str=处方（调用方拒收）。

    预检全程不拿 _GlobalCommitLock、零写副作用（preflight 自身审计除外）；gateway/
    preflight_fn 注入位仅供测试，生产走缺省真源。任何设施故障（网关构造失败/
    preflight 异常）一律 warn+放行——预检是快败优化不是新权威，绝不因预检故障堵入队
    （degraded fail-open，PF:477 同口径）。
    """
    if gateway_factory is None:
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (  # noqa: PLC0415
            GitCommitGateway as gateway_factory,
        )
    if preflight_fn is None:
        from zephyr.gov_enforcement.rule_bridge.commit_preflight import (  # noqa: PLC0415
            run_preflight as preflight_fn,
        )
    try:
        gateway = gateway_factory(project_root=Path(worktree_root))
        result = preflight_fn(
            gateway,
            list(files),
            session_id,
            skip_gate_ids=ENQUEUE_SKIP_GATES,
            audit_event="enqueue",
            commit_message=message or "",
        )
    except Exception as exc:  # noqa: BLE001 — 预检设施故障 degraded 放行（绝不堵入队）
        logger.warning("[enqueue-preflight] 预检设施异常，degraded 放行（落地侧权威链兜底）: %s", exc)
        return None
    if result.blocking:
        return "入队预检拦截（注定死信的单子在入队口快败，锁内白烧已避免）——逐门禁处方：\n" + result.render_report(
            str(session_id)
        )
    if result.degraded:
        logger.info("[enqueue-preflight] degraded gate 不阻断（锁内权威链兜底）: %s", result.degraded)
    return None
