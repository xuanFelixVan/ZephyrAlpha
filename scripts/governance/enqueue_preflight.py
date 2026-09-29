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
# [TESTS] tests/governance/test_enqueue_preflight.py; tests/governance/test_ruff_preclean_enqueue.py
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
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

try:  # 统一无窗口 subprocess 入口（TRAE-067 铁律2）；孤立环境降级不破模块自足性
    from zephyr.shared.infra.process_pool import run_subprocess_hidden
except Exception:  # noqa: BLE001 — 降级仅剩属性引用无窗口语义缺失，设施故障由调用方 fail-open 兜底
    run_subprocess_hidden = subprocess.run  # noqa: bare-subprocess  zephyr 包不可用时的降级兜底，调用方 fail-open

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


# ---------------------------------------------------------------------------
# Rx-1 入队侧 ruff/format 预清（st-finaldel-crx-20260929，提交链治本 P0 首刀）
# ---------------------------------------------------------------------------

# env 开关（缺省 ON；"0"/"false"/"off"=一键回退现行为——B5/C1 同款零 yaml 依赖）
RUFF_PRECLEAN_ENV = "ZEPHYR_ENQUEUE_RUFF_PRECLEAN"
# 大批限流：批内 .py 超过即跳过并记原因（快检性能预算 <3s；落地侧权威兜底不缺席）
_RUFF_PRECLEAN_MAX_FILES = 200
# 单文件体积限流（红蓝对抗 st-finaldel-redblue-20260929 R1a 实证：限流原按数不按体积，
# 单个 10MB .py 即把 ruff format --check 顶到 >60s 超时——"秒级快败"被拖成 2×60s/次；
# 超限跳过=落地侧权威兜底不缺席，与 M2.2 max_bytes 同款保守判据）
_RUFF_PRECLEAN_MAX_FILE_BYTES = 1_000_000
# subprocess 硬杀兜底（ruff 实测秒级；超时=设施故障按 fail-open 放行）
_RUFF_PRECLEAN_TIMEOUT_S = 60.0
# 拒收处方输出截断（Owner 口径 800 字）
_RUFF_PRECLEAN_TRUNC = 800


def ruff_preclean_enabled() -> bool:
    """env 开关读取：ZEPHYR_ENQUEUE_RUFF_PRECLEAN 缺省 ON，"0"/"false"/"off"=回退现行为。"""
    return os.environ.get(RUFF_PRECLEAN_ENV, "").strip().lower() not in {"0", "false", "off"}


def _ruff_preclean_py_files(root: Path, files: list[str] | None) -> list[str]:
    """批内可用 .py 清单收集：相对路径锚 worktree 根；缺失/删除件/非 .py 不触发。

    红蓝对抗 R1a（st-finaldel-redblue-20260929）：单文件体积超限同款跳过——ruff
    format --check 实测 10MB 文件 >60s，不设体积帽则"秒级快败"可被单大文件拖死。
    """
    py_files: list[str] = []
    for f in files or []:
        p = Path(f)
        if not p.is_absolute():
            p = root / p
        if p.suffix == ".py" and p.is_file():
            try:
                oversized = p.stat().st_size > _RUFF_PRECLEAN_MAX_FILE_BYTES
            except OSError:
                continue  # stat 失败（竞态删除等）——同缺失件不触发
            if oversized:
                logger.warning(
                    "[ruff-preclean] skip：%s 体积超限 >%d 字节（单文件限流；落地侧权威兜底）",
                    p,
                    _RUFF_PRECLEAN_MAX_FILE_BYTES,
                )
                continue
            py_files.append(str(p))
    return py_files


def _ruff_exec_once(root: Path, argv: list[str], label: str, fix_hint: str) -> str | None:
    """跑单条 ruff 子命令：rc=0 放行；rc≠0 返回截断处方；设施故障 warn+None（fail-open）。"""
    try:
        r = run_subprocess_hidden(
            argv,
            cwd=str(root),
            encoding="utf-8",
            errors="replace",
            timeout=_RUFF_PRECLEAN_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired:
        logger.warning(
            "[ruff-preclean] skip：%s 超时 >%.0fs（设施故障 fail-open；落地侧权威兜底）",
            label,
            _RUFF_PRECLEAN_TIMEOUT_S,
        )
        return None
    except OSError as exc:
        logger.warning("[ruff-preclean] skip：%s 不可用（%s；设施故障 fail-open；落地侧权威兜底）", label, exc)
        return None
    if r.returncode == 0:
        return None
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    if len(out) > _RUFF_PRECLEAN_TRUNC:
        out = out[:_RUFF_PRECLEAN_TRUNC] + f"\n...（截断，完整输出共 {len(out)} 字符）"
    return f"[{label}] 命中（哪行哪规）：\n{out}\n  修复: {fix_hint}"


def _ruff_findings(root: Path, py_files: list[str]) -> list[str]:
    """ruff check + format --check 两连跑，聚合命中处方。

    ruff 可执行解析：优先 ruff.exe 直调（Rust 原生二进制，实测 spawn 31-89ms）；
    `python -m ruff` 走 Python 包装器启动实测 ~1.8-2.0s/次（两次=3.6-4s，超 <3s
    预算）——仅在 PATH 无 ruff exe 时兜底降级（慢但可用）。

    红蓝对抗 R1f（st-finaldel-redblue-20260929）实证：ruff 包缺失机器上
    `python -m ruff check` 以 rc=1 + "No module named ruff" 退出——旧逻辑把 rc≠0
    一律当违规命中=好文件假红硬拦，违反本模块"ruff 不可用 fail-open"不变量。
    故无 exe 时先探测 `-m ruff --version`，探测失败=设施故障 fail-open 放行。
    """
    which = shutil.which("ruff")
    if which:
        ruff_base: list[str] = [which]
    else:
        try:
            probe = run_subprocess_hidden(
                [sys.executable, "-m", "ruff", "--version"],
                cwd=str(root),
                encoding="utf-8",
                errors="replace",
                timeout=15.0,
            )
        except (subprocess.TimeoutExpired, OSError) as exc:
            logger.warning("[ruff-preclean] skip：ruff 不可用（%s；设施故障 fail-open；落地侧权威兜底）", exc)
            return []
        if probe.returncode != 0:
            logger.warning(
                "[ruff-preclean] skip：ruff 不可用（-m ruff rc=%s；设施故障 fail-open；落地侧权威兜底）",
                probe.returncode,
            )
            return []
        ruff_base = [sys.executable, "-m", "ruff"]
    findings: list[str] = []
    for argv, label, fix_hint in (
        (
            [*ruff_base, "check", "--no-cache", "--output-format", "concise", "--", *py_files],
            "ruff check",
            "ruff check --fix <file>",
        ),
        (
            [*ruff_base, "format", "--check", "--", *py_files],
            "ruff format --check",
            "ruff format <file>",
        ),
    ):
        rx = _ruff_exec_once(root, argv, label, fix_hint)
        if rx is not None:
            findings.append(rx)
    return findings


def ruff_preclean(worktree_root: Path | str, files: list[str]) -> str | None:
    """入队前 ruff check + ruff format --check 只读快检（绝不自动改写用户文件）。

    返回 None=放行（含 skip：非 .py 批零开销/缺失删除件/大批限流/设施故障，均记
    skip 原因）；返回 str=拒收处方（哪行哪规+修复命令）。判据真源=仓内
    pyproject.toml [tool.ruff]（与 .pre-commit-config.yaml 落地通道同一配置，
    ruff 按文件位置自 discovery）。任何设施故障（ruff 不可用/超时/异常）fail-open
    放行——本步是快败优化不是新权威，落地侧 pre-commit 通道照跑。
    """
    if not ruff_preclean_enabled():
        return None
    root = Path(worktree_root)
    py_files = _ruff_preclean_py_files(root, files)
    if not py_files:
        return None  # 非 .py 批零开销跳过（缺失/删除件不触发）
    if len(py_files) > _RUFF_PRECLEAN_MAX_FILES:
        logger.warning(
            "[ruff-preclean] skip：批内 .py %d 个 > 上限 %d（大批限流；落地侧权威兜底）",
            len(py_files),
            _RUFF_PRECLEAN_MAX_FILES,
        )
        return None
    findings = _ruff_findings(root, py_files)
    if not findings:
        return None
    return (
        "RUFF-PRECLEAN 拦截：入队批命中确定性 lint/format 违规——这些错误落到落地侧"
        "必然烧完一整轮 landing（通道阻断谱 ruff-format+ruff 占全史 46%）才第一次见红，"
        "先修再入队（本预检只读，绝不自动改写；auto-fix 请自行执行）：\n" + "\n".join(findings)
    )


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

    Rx-1（st-finaldel-crx-20260929）：gate 预检之前先跑 ruff/format 只读快检
    （ruff 族=通道阻断谱前两名，全史 46%）——同 fail-open 口径，env
    ZEPHYR_ENQUEUE_RUFF_PRECLEAN=0 一键回退现行为。
    """
    _ruff_rx = ruff_preclean(worktree_root, list(files))
    if _ruff_rx is not None:
        return _ruff_rx
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
