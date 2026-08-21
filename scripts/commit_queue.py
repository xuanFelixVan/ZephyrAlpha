# [BLUEPRINT] MOD-GOV-046 | scripts/commit_queue.py | §
# [MODULE] scripts.commit_queue
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] stdlib；zephyr.shared.infra.process_pool.is_pid_alive（僵尸 PID 检测真源唯一）
# [CONSUMERS] 全部 AI session（提交入队唯一入口）；B 段 Serializer 落盘执行体（专用 worktree 真落盘）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 单写者（serializer.lease 唯一持有者排空）；纯 FIFO（qid 单调序，无优先级插队）；快照入袋即安全（blob 落盘即完成）；死信不卡队；同键 (session_id,path) pending 内仅留最新；永不改主工作区文件
# [MODIFY-GUARD] 66 号备忘 §6 协议/schema 真源；08 号文 §4.2 Phase 0；CLI 子命令面（enqueue/status/drain）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=成功（含 drain 拿不到 lease 跳过）; exit 1=参数/IO 错误; exit 2=入队轻检拒绝(DENIED)
# [TESTS] tests/governance/test_commit_queue.py
# [A_module] module_id=MOD-GOV-046 | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 本文件是 AI/CI 按需调用的 CLI 协调工具（入队自举排空，无常驻进程），与 lock_files.py/task_board.py 同类
"""commit_queue.py — 提交队列串行化 MVP（A 段：队列协议 + CLI + Serializer 自举排空 + 死信 + compaction）

真源
----
- 66 号备忘 §6（入队 schema / compaction / Serializer 主循环 / 冲突判定）、§8（入队自举
  排空形态 + lease 算法 + 幂等恢复）、§9（不做什么：单写者/纯 FIFO/死信回退给人/永不改
  主工作区）、§10（MVP 验收口径）、§11（红队测试清单）。
- 08 号文 §4.2 Phase 0 步骤 0/1/2/4（A 段范围）；步骤 3（专用 worktree 真落盘）与步骤 5
  （_commit_auto 改道）属 B 段，不在本文件。

核心语义（66 号 §4 裁定 1/2）
------------------------------
- 会话提交 = 快照入队即返回：文件**完整内容**（非 diff）按内容寻址落 blobs/（sha256 命名
  天然去重），队列项 JSON 落 pending/（O_EXCL 原子创建）——快照入袋即完成，工作区后续
  被 restore/清空不影响本项。
- 落盘由单写者 Serializer 按 FIFO（qid 单调序）完成；本 A 段落盘为**接口桩**
  （landing callable 注入点，默认实现仅标记 done 不真提交）——队列语义（零丢失/FIFO/
  死信/compaction）本段钉死，真 git 落盘 B 段接专用 worktree + GitCommitGateway 全门禁。

与 66 号 §6.1 schema 的刻意出入（回执报备）
------------------------------------------
1. 队列项用 JSON（{qid}.json）而非 YAML——stdlib 零依赖 + 原子写简单；字段集与 66 号
   §6.1 对齐（qid/session_id/created_at/branch/base_head/files[{path,blob_sha256,
   blob_ref,base_blob,action}]/message/meta{depends_on,supersedes}）。
2. message 内联于队列项 JSON（66 号为 message_file 指针）——A 段落盘为桩无消费方，
   B 段接通时可落 message_file；CLI 保留 --message-file 读入（PowerShell 中文编码教训，
   66 号 §6.3 修正 3）。
3. base_head/base_blob A 段不主动取 git（零 git 依赖，测试可全 tmp 隔离）——CLI 提供
   --base-head 显式传入；B 段落盘接通时由 enqueue 增强或 drain 端填充。
4. lease 文件落 .runtime/commit_queue/serializer.lease（任务指定，与队列同目录共命运）；
   66 号 §8 原文为 .ailocks/commit_serializer.lock——语义同款（O_EXCL+TTL+僵尸 PID）。

目录协议（运行时创建；.runtime/ 已整体 gitignore）
--------------------------------------------------
.runtime/commit_queue/
  pending/      待处理队列项（q-*.json，O_EXCL 原子创建）
  processing/   Serializer 取走处理中（原子 rename 进入；崩溃留孤儿，下次自举回收）
  done/         已落盘（含 landed_at/landed_id）
  dead/         死信（含 dead_reason/dead_at；永不自动清理，66 号 §8）
  blobs/        内容寻址快照（sha256 命名，tmp+os.replace 原子写）
  {session_id}.seq  会话内单调序号（qid 组成部分；唯一性最终由 O_EXCL 保证）
  serializer.lease  Serializer 租约（TTL=300s + 僵尸 PID 检测）

入队轻检（66 号 §6.5 + §11 #3 红队口径，全部 fail-closed 报错非静默）
--------------------------------------------------------------------
- 路径穿越：.. 段 / 绝对路径（盘符、UNC、/ 开头）/ ~ 开头 / 反斜杠 / NUL
- .git 路径：首段为 .git 一律拒绝
- 密钥路径：常见密钥文件名黑名单（.env*/*.pem/*.key/*.pfx/id_rsa* 等，66 号 §6.5 pathspec 白名单）
- 超大 blob：单文件 > 10MB 拒绝（66 号 §6.1 大小约束，§12 Q3 已闭环：超限走人工）
- 空 message：strip 后为空拒绝

故障与恢复（66 号 §8）
----------------------
- Serializer 无常驻进程：enqueue/status/drain 成功写队后尝试拿 lease 排空，拿不到就放弃
  等下次自举；崩溃则下一个入队者/任意 status 调用续排空。
- drain 中途崩溃 → processing/ 孤儿项：下次拿 lease 后先原子回收重入 pending 续跑——
  不得双落（done/ 按 qid 唯一）不得丢失（每项终有 pending/processing/done/dead 其一）。
  A 段默认 landing 桩无副作用天然幂等；B 段真落盘时幂等判定（git merge-base
  --is-ancestor / done/ 记录，66 号 §8）在 landing 实现内完成。
- landing 抛普通 Exception = 单项处理失败 → 死信（不卡队，后续项继续）；
  BaseException（KeyboardInterrupt/SystemExit 等，含测试崩溃注入）不捕获向上传播——
  当前项留 processing 等回收，模拟真实进程崩溃语义。

CLI
---
  python scripts/commit_queue.py enqueue --session S --files a.py,b.py --message "msg"
      [--message-file F] [--worktree-root DIR] [--base-head SHA] [--depends-on qid1,qid2]
      [--queue-root DIR] [--no-bootstrap]
  python scripts/commit_queue.py status [--session S] [--queue-root DIR] [--no-bootstrap]
  python scripts/commit_queue.py drain [--queue-root DIR] [--max-items N]

B 段接口预留点（2026-08-21 B 段已接通）
--------------------------------------
- landing callable：drain_queue(queue_root, landing=fn)，fn(item: dict, queue_root: Path)
  -> LandingResult(ok, reason, landed_id)。**B 段真落盘实现已落
  scripts/governance/commit_queue_landing.py（MOD-GOV-047）**：专用 worktree
  （<queue_root>/worktree）+ GitCommitGateway 全门禁零适配 + `[GW:{sid}:{qid}]` 标记
  （POST-COMMIT-GUARD / REFERENCE-TRANSACTION-GUARD `[GW:` 子串匹配兼容）+
  is-ancestor/标记 grep 幂等 + dev update-ref CAS 推进。
- flag 接入：config/flags.yaml `commit_queue_serializer`（默认 enabled:false=
  ALWAYS_OFF）；ON 时 _commit_auto 改道 enqueue（git_commit_gateway 内一处改动，
  66 号 §7），启用属 Owner 窗口（宪章 B-007）。
- task_board 联动点：死信时把 {qid, reason, session_id} 写入 task_board metadata_json
  （66 号 §6.4，无需改表）——A/B 段仅落 dead/ JSON，联动属 P1。
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 提交队列串行化 MVP（enqueue/status/drain + 入队自举排空 + 死信 + compaction）
dimensions:
- D1
priority: P0
timeout_seconds: 120
warn_only: false
"""

import argparse
import hashlib
import json
import logging
import os
import re
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# --- sys.path 引导（CLI 独立运行时 src 不在 sys.path；pytest 下已由项目配置提供）---
_REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# 僵尸 PID 检测真源唯一（红蓝对抗归一，禁止内联复制——process_pool.py docstring 原话）
from zephyr.shared.infra.process_pool import is_pid_alive  # noqa: E402

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 常量（真源逐条注释）
# ---------------------------------------------------------------------------
QUEUE_ENV_VAR = "ZEPHYR_COMMIT_QUEUE_DIR"  # 测试/多仓隔离覆盖位（先例：ZEPHYR_TASK_BOARD_DB）
_QUEUE_DIR_DEFAULT = ".runtime/commit_queue"  # 66 号 §2.4 #13 / 08 号文 §2.4 E
_STATES = ("pending", "processing", "done", "dead")  # 四态目录（66 号 §5 架构图）

_LEASE_FILE = "serializer.lease"  # 独立文件锁，不共用网关 _GlobalCommitLock（任务口径）
_LEASE_TTL_SECONDS = 300  # 66 号 §8：Serializer 排空一批通常 <30s，5 分钟足够
_LEASE_TIMEOUT_SECONDS = 5.0  # 66 号 §8：自举模式不等待——拿不到就放弃
_LEASE_POLL_INTERVAL = 0.1  # 与 _GlobalCommitLock._POLL_INTERVAL 同款

_MAX_BLOB_BYTES = 10 * 1024 * 1024  # 66 号 §6.1 大小约束（§12 Q3 已闭环：单 blob 上限 10MB，超限拒绝走人工）
_TARGET_BRANCH = "dev"  # 66 号 §9.5：v0.1 仅 dev 主干单目标（不支持跨分支队列）
_SEQ_PAD = 4  # 66 号 §6.1：seq:04d 零填充——qid 字典序 == 数值序，保 FIFO 排序机械性

_READ_RETRY_TIMES = 20  # drain 读 pending 项容忍写入窗口：重试次数（见 _read_item 注释）
_READ_RETRY_INTERVAL = 0.05  # 重试间隔 50ms × 20 = 1s 上限

# session_id 字符白名单：session_id 进入 qid 与 seq 文件名，必须防路径注入
_SESSION_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")

# 密钥文件名黑名单（66 号 §6.5 pathspec 白名单：禁止 .git/密钥路径入队）
_SECRET_NAME_RE = re.compile(
    r"^(\.env(\..*)?|.*\.(pem|key|pfx|p12|keystore|jks)|id_rsa.*|id_ed25519.*|credentials(\..*)?)$",
    re.IGNORECASE,
)


class QueueReject(ValueError):
    """入队轻检拒绝（fail-closed：报错非静默，CLI 映射 exit 2 DENIED）。"""


class LeaseUnavailable(RuntimeError):
    """Serializer lease 被活体持有（自举模式：放弃等下次，非错误）。"""


@dataclass
class LandingResult:
    """landing callable 返回协议（B 段真落盘实现的契约）。

    ok=False → 项进 dead/ 附 reason；landed_id 预留 B 段回填 commit hash。
    """

    ok: bool
    reason: str = ""
    landed_id: str = ""


# landing callable 类型：fn(队列项 dict, queue_root) -> LandingResult
# B 段接专用 worktree 真落盘（08 号文 §4.2 步骤 3，GitCommitGateway 全门禁零适配）。


def default_landing_stub(item: dict, queue_root: Path) -> LandingResult:
    """A 段默认落盘桩：仅标记 done 不真提交。

    队列语义（零丢失/FIFO/死信）本段钉死；真 git 落盘 B 段接专用 worktree
    （.aidrafts/serializer/）+ GitCommitGateway 全门禁链（66 号 §6.3 MVP 形态）。
    """
    logger.info("[landing-stub] qid=%s 仅标记 done（B 段接专用 worktree 真落盘）", item.get("qid"))
    return LandingResult(ok=True, landed_id=f"stub:{item.get('qid', '')}")


# ---------------------------------------------------------------------------
# 路径与基础工具
# ---------------------------------------------------------------------------


def resolve_queue_root(queue_root: str | os.PathLike | None = None) -> Path:
    """队列根解析序：显式参数 > 环境变量 > 仓库默认 .runtime/commit_queue。

    默认锚 __file__ 派生的仓库根（scripts/ 上一级）——与 task_board 锚主仓同理，
    本队列是跨 worktree 协调设施，MUST 全会话共享同一目录。
    """
    if queue_root is not None:
        return Path(queue_root)
    env = os.environ.get(QUEUE_ENV_VAR)
    if env:
        return Path(env)
    return _REPO_ROOT / _QUEUE_DIR_DEFAULT


def _ensure_dirs(queue_root: Path) -> None:
    """运行时创建队列目录协议（pending/processing/done/dead/blobs）。"""
    for d in (*_STATES, "blobs"):
        (queue_root / d).mkdir(parents=True, exist_ok=True)


def _atomic_write(path: Path, data: bytes) -> None:
    """tmp + flush/fsync + os.replace 原子写（RULE-ONE 同款模式，对标 lock_files.py）。"""
    tmp = path.with_name(path.name + f".tmp-{os.getpid()}-{threading.get_ident()}")
    with open(tmp, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _retry_transient(fn, times: int = 5, interval: float = 0.02):
    """Windows 瞬态文件占用（PermissionError）重试。

    竞态真源：enqueue 的 O_EXCL 创建后单 write 窗口内文件被持有句柄，并发 drain 的
    rename/compaction 的 replace 撞上即 WinError 32（PermissionError）。窗口极短
    （毫秒级），短暂重试即可收敛；FileNotFoundError 属语义性消失（对方已完成移动/
    删除），由调用方按语义处理，不在此重试。
    """
    for attempt in range(times):
        try:
            return fn()
        except PermissionError:
            if attempt == times - 1:
                raise
            threading.Event().wait(interval * (attempt + 1))
    return None  # pragma: no cover - 防御性（循环必 return 或 raise）


def _now_iso() -> str:
    """本地时区 ISO8601 秒级（66 号 §6.1 示例：2026-08-12T21:30:00+08:00）。"""
    return datetime.now().astimezone().isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# 入队轻检（66 号 §6.5 + §11 #3 红队口径——畸形项全拦，报错非静默）
# ---------------------------------------------------------------------------


def _validate_session_id(session_id: str) -> None:
    if not session_id or not _SESSION_ID_RE.match(session_id):
        raise QueueReject(
            f"非法 session_id: {session_id!r}（白名单 [A-Za-z0-9._-] 且 ≤64 字符；"
            f"session_id 进入 qid/seq 文件名，必须防路径注入）"
        )


def _validate_relpath(path: str) -> str:
    """仓内相对路径校验，返回归一化正斜杠形式。

    红队向量（66 号 §11 #3）：路径穿越（../、绝对路径、~）/.git 路径/密钥路径。
    """
    if not path or not path.strip():
        raise QueueReject("空路径拒绝入队")
    if "\x00" in path:
        raise QueueReject(f"路径含 NUL 字符: {path!r}")
    if "\\" in path:
        raise QueueReject(f"路径必须正斜杠（拒绝反斜杠）: {path!r}")
    if path.startswith("~"):
        raise QueueReject(f"路径穿越（~ 开头）: {path!r}")
    if path.startswith("/") or path.startswith("//"):
        raise QueueReject(f"绝对路径（/ 或 UNC 开头）拒绝: {path!r}")
    if re.match(r"^[A-Za-z]:", path):
        raise QueueReject(f"绝对路径（盘符）拒绝: {path!r}")
    parts = path.split("/")
    if any(p in ("", ".", "..") for p in parts):
        raise QueueReject(f"路径穿越（含空段/./..）拒绝: {path!r}")
    if parts[0] == ".git":
        raise QueueReject(f".git 路径禁止入队（66 号 §6.5 pathspec 白名单）: {path!r}")
    if _SECRET_NAME_RE.match(parts[-1]):
        raise QueueReject(f"密钥路径禁止入队（66 号 §6.5 pathspec 白名单）: {path!r}")
    return path


def _validate_message(message: str) -> str:
    msg = (message or "").strip()
    if not msg:
        raise QueueReject("空 message 拒绝入队（66 号 §11 #3 红队口径）")
    return msg


def _validate_blob_size(path: str, content: bytes) -> None:
    if len(content) > _MAX_BLOB_BYTES:
        raise QueueReject(
            f"超大 blob 拒绝入队: {path} = {len(content)} 字节 > 上限 {_MAX_BLOB_BYTES}"
            f"（66 号 §6.1：单 blob 10MB 上限，超限走人工）"
        )


# ---------------------------------------------------------------------------
# blob 内容寻址存储（66 号 §6.1 v0.4.0：tmp 写入 + os.replace；sha 命名天然去重）
# ---------------------------------------------------------------------------


def _store_blob(queue_root: Path, content: bytes) -> str:
    sha = hashlib.sha256(content).hexdigest()
    blob_path = queue_root / "blobs" / sha
    if not blob_path.exists():  # 内容寻址天然去重——同内容不重复存储
        _atomic_write(blob_path, content)
    return sha


# ---------------------------------------------------------------------------
# qid / seq（66 号 §6.1 v0.4.0：q-{date}-{session_id}-{seq:04d}，O_EXCL 原子创建，
# 碰撞重试 seq+1；seq 文件是 hint，唯一性最终由 O_EXCL 保证）
# ---------------------------------------------------------------------------

# 同进程内每会话 enqueue 串行点（66 号 §6.2：compaction 序列需在 session seq 锁内完成）；
# 跨进程同会话并发由 pending O_EXCL + 原子 rename 兜底（竞态分析见 enqueue_item docstring）。
_session_locks: dict[str, threading.Lock] = {}
_session_locks_guard = threading.Lock()


def _get_session_lock(session_id: str) -> threading.Lock:
    with _session_locks_guard:
        lock = _session_locks.get(session_id)
        if lock is None:
            lock = threading.Lock()
            _session_locks[session_id] = lock
        return lock


def _read_seq(queue_root: Path, session_id: str) -> int:
    seq_file = queue_root / f"{session_id}.seq"
    try:
        return int(seq_file.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return 0


def _write_seq(queue_root: Path, session_id: str, seq: int) -> None:
    _atomic_write(queue_root / f"{session_id}.seq", f"{seq}\n".encode("utf-8"))


def _make_qid(session_id: str, seq: int) -> str:
    date = datetime.now().strftime("%Y%m%d")
    return f"q-{date}-{session_id}-{seq:0{_SEQ_PAD}d}"


def _create_item_excl(path: Path, payload: bytes) -> None:
    """os.open(O_CREAT|O_EXCL) 原子创建队列项（66 号 §6.1 v0.4.0 文件创建原子性）。"""
    fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        os.write(fd, payload)
    finally:
        os.close(fd)


# ---------------------------------------------------------------------------
# compaction（66 号 §6.2：键=(session_id,path)，pending 内同键仅留最新，整体覆盖）
# ---------------------------------------------------------------------------


def _compact_pending(queue_root: Path, session_id: str, new_paths: set[str]) -> list[str]:
    """同键覆盖：移除 pending 中被新项覆盖的同会话旧项/旧条目，返回 supersedes 链。

    调用时机：新项落盘**之前**（会话锁内）——故无需排除新项自身。
    语义（66 号 §6.2 + §4 裁定 2）：快照是完整内容非增量补丁，替换=最终态正确；
    仅作用 pending（done/dead/processing 不参与）；跨会话同文件不覆盖（键不同）。
    supersedes 传递累积：被整体移除项自身的 supersedes 并入返回值——覆盖全链可追溯
    （如 v3 覆盖 v2、v2 曾覆盖 v1 → v3.supersedes=[q2,q1]），供死信回溯/审计。
    竞态安全：与 drain 并发时——drain 用原子 rename 取项，本函数对已不在 pending 的项
    收到 FileNotFoundError 即跳过（说明已被 drain 取走，不参与 pending compaction，
    语义正确）；部分覆盖写回走 tmp+os.replace 原子替换，读者（drain）只见完整旧版或
    完整新版；Windows 瞬态占用（enqueue 写入窗口）经 _retry_transient 收敛。
    """
    superseded: list[str] = []
    pending_dir = queue_root / "pending"
    for candidate in sorted(pending_dir.glob("q-*.json")):
        try:
            item = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue  # 写入窗口或损坏——跳过不碰（读者容错，见 _read_item）
        if item.get("session_id") != session_id:
            continue  # 跨会话同文件不产生覆盖（键不同，66 号 §6.2）
        files = item.get("files") or []
        overlapped = [f for f in files if f.get("path") in new_paths]
        if not overlapped:
            continue
        remaining = [f for f in files if f.get("path") not in new_paths]
        old_qid = item.get("qid", candidate.stem)
        if not remaining:
            # 整体覆盖：旧项所有 path 均被新项包含 → 移除旧项（其内容必然已被
            # 新快照包含，66 号 §4 裁定 2 审查论证）；supersedes 关系记在新项 meta。
            try:
                _retry_transient(lambda: os.remove(candidate))
                superseded.append(old_qid)
                # 传递累积：被移除项自身覆盖过的更旧项一并入链（审计可追溯）
                superseded.extend(item.get("meta", {}).get("supersedes") or [])
            except (FileNotFoundError, PermissionError):
                pass  # 已被 drain 并发取走/正在其操作窗口——正确语义，跳过
        else:
            # 部分覆盖：旧项缩减为未被覆盖的 path 集合，原子写回。
            # 不记 compacted_by=<新qid>——本函数在新项落盘前调用，新 qid 此时尚未分配；
            # 只留「被部分覆盖」事实与时间戳（整体覆盖链在新项 meta.supersedes 全量记录）。
            item["files"] = remaining
            item.setdefault("meta", {})["compacted_partial"] = True
            item["meta"]["compacted_at"] = _now_iso()
            try:
                _retry_transient(
                    lambda: _atomic_write(candidate, json.dumps(item, ensure_ascii=False, indent=2).encode("utf-8"))
                )
            except (FileNotFoundError, PermissionError):
                pass  # 同上：并发取走即跳过
    # 保序去重（直接前驱在前）
    seen: set[str] = set()
    out: list[str] = []
    for q in superseded:
        if q not in seen:
            seen.add(q)
            out.append(q)
    return out


# ---------------------------------------------------------------------------
# enqueue（快照入袋即返回——防内容丢失的核心语义，66 号 §6.1「快照即落袋」）
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EnqueueOptions:
    """enqueue 可选参数束（NO-LONG-PARAM-LIST 合规收口，§5.150：>7 参数反模式）。

    base_head : 入队时观察到的目标分支 HEAD（A 段不主动取 git，由调用方显式传入；
        B 段落盘接通后用于 §6.4 逐文件快进/冲突判定）。
    depends_on : meta.depends_on 预留字段（A 段只做 schema 预留，不实现级联逻辑）。
    deletes : 删除路径列表（B 段新增，66 号 §6.1 action=delete 语义细化）：已跟踪但
        盘上缺失的文件经此通道入袋，落盘时从 dev 树删除；与 files 共享同键 compaction。
    meta_extra : 附加 meta 键值（并入队列项 meta）。
    """

    base_head: str | None = None
    depends_on: list[str] | None = None
    deletes: list[str] | None = None
    meta_extra: dict | None = None


def enqueue_item(
    session_id: str,
    message: str,
    files: list[tuple[str, bytes]],
    *,
    queue_root: str | os.PathLike | None = None,
    options: EnqueueOptions | None = None,
) -> dict:
    """入队核心（API 层；CLI 层负责从 worktree 读文件内容后调本函数）。

    参数
    ----
    files : list[(仓内相对路径, 完整内容 bytes)]——完整快照非 diff（66 号 §4 裁定 2）。
    options : 可选参数束（base_head/depends_on/deletes/meta_extra），见 EnqueueOptions。

    返回：落袋的队列项 dict（含 qid）。
    异常：QueueReject（轻检拒绝，fail-closed 报错非静默）。

    并发安全（66 号 §6.1 v0.4.0 结论）：多会话同时 enqueue 各自 {qid}.json 独立文件，
    无共享写状态；同会话内经进程内 session 锁串行（seq 递增 + compaction 在同一
    关键段），跨进程同会话由 O_EXCL 碰撞重试兜底唯一性。
    """
    opts = options or EnqueueOptions()
    base_head = opts.base_head
    depends_on = opts.depends_on
    deletes = opts.deletes
    meta_extra = opts.meta_extra
    root = resolve_queue_root(queue_root)
    _ensure_dirs(root)
    _validate_session_id(session_id)
    msg = _validate_message(message)
    if not files and not deletes:
        raise QueueReject("空文件清单拒绝入队")

    # 1) 轻检 + blob 落袋（先于队列项创建——blob 入袋即内容不丢）
    blob_entries: list[dict] = []
    seen_paths: set[str] = set()
    for path, content in files:
        norm = _validate_relpath(path)
        if norm in seen_paths:
            raise QueueReject(f"同一入队项内路径重复: {norm}")
        seen_paths.add(norm)
        _validate_blob_size(norm, content)
        sha = _store_blob(root, content)
        blob_entries.append(
            {
                "path": norm,
                "blob_sha256": sha,
                "blob_ref": f"blobs/{sha}",
                "base_blob": None,  # A 段预留（B 段：git rev-parse HEAD:{path} 填充，66 号 §6.1 v0.4.0）
                "action": "modify",  # add/modify 统一 modify；delete 经 deletes 通道（B 段细化）
            }
        )
    # B 段 deletes 通道（66 号 §6.1 action=delete）：已跟踪但盘上缺失的删除项，
    # 无 blob 落袋；同键 compaction 与 files 共享 seen_paths（覆盖语义一致）。
    for path in deletes or []:
        norm = _validate_relpath(path)
        if norm in seen_paths:
            raise QueueReject(f"同一入队项内路径重复: {norm}")
        seen_paths.add(norm)
        blob_entries.append(
            {
                "path": norm,
                "blob_sha256": None,
                "blob_ref": None,
                "base_blob": None,
                "action": "delete",
            }
        )

    # 2) 会话内串行段：compaction → seq 分配 → O_EXCL 落 pending（同一会话锁内完成，
    #    66 号 §6.2「compaction 序列需在 session seq 锁内完成」）。
    #    顺序为何是「先 compact 后落新项」而非「先落后 compact+回填」：
    #    2026-08-21 竞态测试实证——先落后回填形态下，drain 把新项 rename 取走后，
    #    supersedes 回填的 os.replace 对不存在目标**静默重建** pending 文件，
    #    同快照同 qid 二次落盘（v17 双落实例）。改为 compact 收集 supersedes 链后
    #    随新项一次落盘，零回填零重建窗口。空窗代价：compact 删旧项与新项落盘间
    #    该键短暂无 pending——blob 已入袋不丢内容，drain 空窗仅视为队列空（无害）。
    lock = _get_session_lock(session_id)
    with lock:
        removed = _compact_pending(root, session_id, seen_paths)
        seq = _read_seq(root, session_id)
        payload_item: dict = {}
        qid = ""
        for _attempt in range(1000):  # O_EXCL 碰撞重试（66 号 §6.1：极端碰撞 seq+1 重试）
            seq += 1
            qid = _make_qid(session_id, seq)
            payload_item = {
                "qid": qid,
                "session_id": session_id,
                "created_at": _now_iso(),
                "branch": _TARGET_BRANCH,
                "base_head": base_head,
                "message": msg,
                "files": blob_entries,
                "meta": {
                    "depends_on": list(depends_on or []),  # schema 预留，A 段不实现级联
                    "supersedes": removed,  # compaction 覆盖全链（传递累积，审计可追溯）
                    **(meta_extra or {}),
                },
            }
            payload = json.dumps(payload_item, ensure_ascii=False, indent=2).encode("utf-8")
            try:
                _create_item_excl(root / "pending" / f"{qid}.json", payload)
                break
            except FileExistsError:
                continue  # qid 碰撞（并发同 seq hint）→ seq+1 重试
        else:  # pragma: no cover - 理论不可达（1000 次碰撞）
            # MSG-EXPOSURE 口径：session_id 属敏感标识不入错误消息文本
            raise RuntimeError("qid 分配失败（1000 次碰撞），请清理队列后重试")
        _write_seq(root, session_id, seq)

    logger.info("[enqueue] qid=%s session=%s files=%d supersedes=%s", qid, session_id, len(blob_entries), removed)
    return payload_item


# ---------------------------------------------------------------------------
# Serializer lease（复用 _GlobalCommitLock 同款语义：O_EXCL + TTL + 僵尸 PID 检测；
# 独立文件锁 .runtime/commit_queue/serializer.lease，不共用网关锁——任务口径）
# ---------------------------------------------------------------------------


class SerializerLease:
    """Serializer 租约（66 号 §8 v0.4.0 lease 算法）。

    - 获取：os.open(O_CREAT|O_EXCL) 原子创建；与 _GlobalCommitLock 同款。
    - TTL=300s：持有者崩溃后租约自动过期可回收。
    - 僵尸 PID 检测：持有进程 PID 已死亡立即清理（零窗口期，is_pid_alive 真源唯一）。
    - 超时 5s：自举模式不等待——拿不到抛 LeaseUnavailable，调用方放弃等下次自举。
    - 释放：os.remove。
    """

    def __init__(
        self,
        queue_root: Path,
        timeout: float = _LEASE_TIMEOUT_SECONDS,
        ttl: float = _LEASE_TTL_SECONDS,
        poll_interval: float = _LEASE_POLL_INTERVAL,
    ) -> None:
        self._lease_file = queue_root / _LEASE_FILE
        self._timeout = timeout
        self._ttl = ttl
        self._poll_interval = poll_interval
        self._acquired = False

    def __enter__(self) -> "SerializerLease":
        deadline = time.monotonic() + self._timeout
        # do-while 等价结构（expired 后置判定）——保证 timeout=0 也至少尝试一次获取，
        # 与 66 号 §8"拿不到就放弃"语义一致；不用 while True（PERM-TRIGGER 口径：
        # 本文件是事件触发自举，非时间轮询常驻，循环有界）。
        expired = False
        while not expired:
            try:
                fd = os.open(str(self._lease_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                try:
                    os.write(
                        fd,
                        json.dumps({"pid": os.getpid(), "acquired_at": time.time()}, ensure_ascii=False).encode("utf-8"),
                    )
                finally:
                    os.close(fd)
                self._acquired = True
                return self
            except FileExistsError:
                try:
                    data = json.loads(self._lease_file.read_text(encoding="utf-8"))
                    acquired_at = data.get("acquired_at", 0)
                    if not isinstance(acquired_at, (int, float)):
                        acquired_at = 0
                    holder_pid = data.get("pid")
                    if holder_pid is not None and not is_pid_alive(int(holder_pid)):
                        # 僵尸租约：持有者进程已死亡，立即清理（零窗口期）
                        logger.warning("SerializerLease: 持有进程 PID %s 已死亡，清理僵尸租约", holder_pid)
                        try:
                            os.remove(self._lease_file)
                        except OSError:
                            pass
                        continue
                    if time.time() - acquired_at > self._ttl:
                        # TTL 过期：持有者崩溃未释放，回收
                        logger.warning("SerializerLease: 租约超 TTL(%ss) 过期，回收", self._ttl)
                        try:
                            os.remove(self._lease_file)
                        except OSError:
                            pass
                        continue
                except (OSError, ValueError, TypeError):
                    logger.warning("SerializerLease: 租约文件损坏，清理后重试")
                    try:
                        os.remove(self._lease_file)
                    except OSError:
                        pass
                    continue
                expired = time.monotonic() >= deadline
                if not expired:
                    threading.Event().wait(self._poll_interval)
        raise LeaseUnavailable(
            f"Serializer lease 被活体持有（timeout {self._timeout}s）: {self._lease_file}"
        ) from None

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self._acquired:
            try:
                os.remove(self._lease_file)
            except OSError:
                pass
            self._acquired = False
        return False


# ---------------------------------------------------------------------------
# drain（Serializer 主循环，66 号 §6.3：FIFO 取项 → processing → 落盘 → done/dead）
# ---------------------------------------------------------------------------


def _read_item(path: Path) -> dict | None:
    """读队列项 JSON，容忍 enqueue 写入窗口（O_EXCL 创建后单 write 的极短半写窗口）。

    重试 _READ_RETRY_TIMES × 50ms ≈ 1s；仍失败返回 None（本轮跳过留 pending，永不因
    读取竞态进死信；真损坏项留待人工，66 号 §8 队列腐败口径：append-only + fsck 校验）。
    """
    for _ in range(_READ_RETRY_TIMES):
        try:
            if path.stat().st_size > 0:
                return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
        threading.Event().wait(_READ_RETRY_INTERVAL)
    logger.error("[drain] 队列项读取失败（疑似损坏，留待人工）: %s", path)
    return None


def _recover_orphans(queue_root: Path) -> list[str]:
    """processing/ 孤儿回收（66 号 §8：崩溃后下次自举从 processing 续跑——重入 pending）。

    仅 lease 持有者调用（单写者不变量）。原子 rename 回 pending/；done/dead 同名文件
    已存在则直接删除孤儿（幂等重放保护：已确认终态的不重跑，防双落）。
    """
    recovered: list[str] = []
    processing_dir = queue_root / "processing"
    for orphan in sorted(processing_dir.glob("q-*.json")):
        qid = orphan.stem
        if (queue_root / "done" / orphan.name).exists() or (queue_root / "dead" / orphan.name).exists():
            # 已有终态（崩溃发生在 rename 之后？防御性）→ 删孤儿防双落
            try:
                os.remove(orphan)
            except OSError:
                pass
            logger.warning("[drain] 孤儿项 %s 已有终态，删除防双落", qid)
            continue
        try:
            os.rename(orphan, queue_root / "pending" / orphan.name)
            recovered.append(qid)
        except OSError as exc:
            logger.error("[drain] 孤儿回收失败 %s: %s", qid, exc)
    if recovered:
        logger.info("[drain] 回收 processing 孤儿 %d 项重入 pending: %s", len(recovered), recovered)
    return recovered


def drain_queue(
    queue_root: str | os.PathLike | None = None,
    *,
    landing=None,
    max_items: int | None = None,
    lease_timeout: float = _LEASE_TIMEOUT_SECONDS,
) -> dict:
    """Serializer 排空（单写者主循环）。

    流程（66 号 §6.3 + §8）：拿 lease → 回收 processing 孤儿 → FIFO（qid 单调序）取
    pending 队首 → 原子 rename processing → landing → done/（附 landed_at/landed_id）
    或 dead/（附 dead_reason/dead_at，不卡队后续继续）→ 排空释放 lease。

    landing : callable(item: dict, queue_root: Path) -> LandingResult；None=默认桩
        （仅标记 done 不真提交，B 段接专用 worktree 真落盘）。
    异常语义：landing 抛 Exception → 单项失败死信；BaseException 不捕获向上传播
        （模拟进程崩溃，当前项留 processing 等孤儿回收）。
    """
    root = resolve_queue_root(queue_root)
    _ensure_dirs(root)
    landing_fn = landing if landing is not None else default_landing_stub
    stats = {"skipped": False, "recovered": 0, "done": 0, "dead": 0, "processed_qids": []}

    with SerializerLease(root, timeout=lease_timeout):
        stats["recovered"] = len(_recover_orphans(root))
        processed = 0
        # 排空即退出（66 号 §6.3）：heads 为空 break；循环上界=max_items——有界批处理，
        # 非 while True 时间轮询（PERM-TRIGGER 口径：事件触发自举，无常驻）。
        while max_items is None or processed < max_items:
            pending_dir = root / "pending"
            heads = sorted(pending_dir.glob("q-*.json"))  # qid 字典序 == FIFO 序（seq 零填充）
            if not heads:
                break  # 排空即退出（66 号 §6.3）
            head = heads[0]
            processing_path = root / "processing" / head.name
            try:
                # 原子取项：pending → processing；PermissionError=enqueue 写入窗口瞬态占用，
                # 重试收敛（保 FIFO 不跳项——取不到队首本轮结束，下轮自举再来）
                _retry_transient(lambda: os.rename(head, processing_path))
            except FileNotFoundError:
                continue  # 被并发 compaction 移除——取下一队首（竞态安全，66 号 §6.2）
            except PermissionError:
                logger.info("[drain] 队首 %s 持续被占用（写入者慢），本轮结束等下次自举", head.name)
                break
            item = _read_item(processing_path)
            if item is None:
                # 读取持续失败：放回 pending 下轮再试（不冤枉慢写入者，不见死信）
                try:
                    os.rename(processing_path, head)
                except OSError:
                    pass
                break
            qid = item.get("qid", head.stem)
            try:
                result = landing_fn(item, root)
            except Exception as exc:  # 单项失败 → 死信不卡队（66 号 §4 裁定 4）
                result = LandingResult(ok=False, reason=f"landing 异常: {type(exc).__name__}: {exc}")
            if result.ok:
                item["landed_at"] = _now_iso()
                item["landed_id"] = result.landed_id
                _atomic_write(processing_path, json.dumps(item, ensure_ascii=False, indent=2).encode("utf-8"))
                os.replace(processing_path, root / "done" / head.name)
                stats["done"] += 1
            else:
                # 死信：附原因移 dead/，队列继续前进（DLQ 语义不堵队，66 号 §6.4）
                item["dead_at"] = _now_iso()
                item["dead_reason"] = result.reason
                _atomic_write(processing_path, json.dumps(item, ensure_ascii=False, indent=2).encode("utf-8"))
                os.replace(processing_path, root / "dead" / head.name)
                stats["dead"] += 1
                logger.warning("[drain] qid=%s 进死信: %s", qid, result.reason)
                # B 段联动点：task_board metadata_json 打标签（{qid, reason, session_id}，
                # 66 号 §6.4，无需改表）；依赖级联标记（meta.depends_on）B 段实现。
            stats["processed_qids"].append(qid)
            processed += 1
    return stats


def try_bootstrap_drain(queue_root: str | os.PathLike | None = None, *, landing=None) -> dict:
    """入队自举排空（66 号 §8：无常驻进程——写队后尝试拿 lease，拿不到就放弃等下次）。"""
    try:
        return drain_queue(queue_root, landing=landing)
    except LeaseUnavailable as exc:
        logger.info("[bootstrap] %s —— 另一 Serializer 在跑，放弃等下次自举", exc)
        return {"skipped": True, "reason": "lease_unavailable", "done": 0, "dead": 0, "recovered": 0, "processed_qids": []}


# ---------------------------------------------------------------------------
# status（66 号 §6.6 落盘确认接口：会话 push/声明完成前 MUST 先确认队列项全部 done）
# ---------------------------------------------------------------------------


def queue_status(queue_root: str | os.PathLike | None = None, *, session_id: str | None = None) -> dict:
    """队列状态总览；--session 过滤该会话各 qid 的 pending/processing/done/dead 状态。"""
    root = resolve_queue_root(queue_root)
    _ensure_dirs(root)
    counts: dict[str, int] = {}
    items: list[dict] = []
    for state in _STATES:
        state_dir = root / state
        entries = sorted(state_dir.glob("q-*.json"))
        counts[state] = 0
        for entry in entries:
            try:
                item = json.loads(entry.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                item = {"qid": entry.stem, "session_id": None, "_corrupt": True}
            if session_id is not None and item.get("session_id") != session_id:
                continue
            counts[state] += 1
            record = {
                "qid": item.get("qid", entry.stem),
                "session_id": item.get("session_id"),
                "state": state,
                "created_at": item.get("created_at"),
            }
            if state == "dead":
                record["dead_reason"] = item.get("dead_reason")
            if state == "done":
                record["landed_id"] = item.get("landed_id")
            items.append(record)
    return {
        "queue_root": str(root),
        "counts": counts,
        "total": sum(counts.values()),
        "items": items,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _read_files_from_worktree(worktree_root: Path, relpaths: list[str]) -> list[tuple[str, bytes]]:
    """CLI 层：从工作区读文件完整内容（66 号 §6.1 v0.4.0：读工作区文件非 git index，
    因工作区是 AI 编辑的最终态）。

    B 段衔接点：读取前 MUST 先 lock_files.py acquire（66 号 §6.1 v0.4.0 编辑期锁协议
    衔接）——A 段未集成（严格限界），由会话纪律层保证；快照落袋本身保数据不丢。
    """
    out: list[tuple[str, bytes]] = []
    for rel in relpaths:
        norm = _validate_relpath(rel)  # 轻检前置：CLI 读盘前就拦穿越（不读越界文件）
        abs_path = worktree_root / norm
        try:
            content = abs_path.read_bytes()
        except OSError as exc:
            raise QueueReject(f"文件读取失败: {norm}（{exc}）") from exc
        out.append((norm, content))
    return out


def _cmd_enqueue(args: argparse.Namespace) -> int:
    worktree_root = Path(args.worktree_root) if args.worktree_root else Path.cwd()
    message = args.message
    if args.message_file:
        try:
            # --message-file：UTF-8 读入（PowerShell 管道传中文必毁编码教训，66 号 §6.3 修正 3）
            message = Path(args.message_file).read_text(encoding="utf-8")
        except OSError as exc:
            print(f"ERROR: message-file 读取失败: {exc}", file=sys.stderr)
            return 1
    files_arg = [f.strip() for f in (args.files or "").split(",") if f.strip()]
    if not files_arg:
        print("DENIED: 空文件清单拒绝入队（--files 必填）", file=sys.stderr)
        return 2
    try:
        files = _read_files_from_worktree(worktree_root, files_arg)
        depends_on = [d.strip() for d in (args.depends_on or "").split(",") if d.strip()]
        item = enqueue_item(
            args.session,
            message or "",
            files,
            queue_root=args.queue_root,
            options=EnqueueOptions(base_head=args.base_head, depends_on=depends_on or None),
        )
    except QueueReject as exc:
        # fail-closed：报错非静默（66 号 §11 #3：畸形项全拦且报错非静默）
        print(f"DENIED: {exc}", file=sys.stderr)
        return 2
    print(f"ENQUEUED: {item['qid']} (files={len(item['files'])}, supersedes={item['meta']['supersedes']})")
    if not args.no_bootstrap:
        result = try_bootstrap_drain(args.queue_root)  # 入队自举排空（66 号 §8）
        if not result.get("skipped"):
            print(f"DRAIN: done={result['done']} dead={result['dead']} recovered={result['recovered']}")
        else:
            print("DRAIN: skipped（另一 Serializer 持 lease，等下次自举）")
    return 0


def _cmd_status(args: argparse.Namespace) -> int:
    if not args.no_bootstrap:
        try_bootstrap_drain(args.queue_root)  # 66 号 §6.6：status 调用本身触发一次排空尝试
    report = queue_status(args.queue_root, session_id=args.session)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def _cmd_drain(args: argparse.Namespace) -> int:
    try:
        result = drain_queue(args.queue_root, max_items=args.max_items)
    except LeaseUnavailable as exc:
        # 显式 drain 拿不到 lease = 另一 Serializer 在排空——正常路径非错误（66 号 §8）
        print(f"SKIPPED: {exc}")
        return 0
    print(
        f"DRAIN: done={result['done']} dead={result['dead']} "
        f"recovered={result['recovered']} qids={result['processed_qids']}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="commit_queue.py",
        description="提交队列串行化 MVP（66 号 §6 协议）：enqueue/status/drain",
    )
    parser.add_argument("--queue-root", default=None, help=f"队列根（默认 {_QUEUE_DIR_DEFAULT}；环境变量 {QUEUE_ENV_VAR} 可覆盖）")
    sub = parser.add_subparsers(dest="command", required=True)

    p_enq = sub.add_parser("enqueue", help="快照入队即返回（入袋即完成）")
    p_enq.add_argument("--session", required=True, help="生产者会话 ID（[A-Za-z0-9._-] ≤64）")
    p_enq.add_argument("--files", required=True, help="仓内相对路径逗号分隔（正斜杠）")
    p_enq.add_argument("--message", default=None, help="commit message（内联）")
    p_enq.add_argument("--message-file", default=None, help="commit message 文件（UTF-8，中文推荐）")
    p_enq.add_argument("--worktree-root", default=None, help="工作区根（默认 cwd）")
    p_enq.add_argument("--base-head", default=None, help="入队时目标分支 HEAD（A 段显式传入，B 段自动取）")
    p_enq.add_argument("--depends-on", default=None, help="依赖的前置 qid 逗号分隔（schema 预留，A 段不实现级联）")
    p_enq.add_argument("--no-bootstrap", action="store_true", help="入队后不尝试自举排空")
    p_enq.set_defaults(func=_cmd_enqueue)

    p_st = sub.add_parser("status", help="队列状态（触发一次排空尝试）")
    p_st.add_argument("--session", default=None, help="按会话过滤")
    p_st.add_argument("--no-bootstrap", action="store_true", help="不触发排空尝试")
    p_st.set_defaults(func=_cmd_status)

    p_dr = sub.add_parser("drain", help="显式排空（拿不到 lease 则跳过 exit 0）")
    p_dr.add_argument("--max-items", type=int, default=None, help="本轮最多处理项数")
    p_dr.set_defaults(func=_cmd_drain)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
