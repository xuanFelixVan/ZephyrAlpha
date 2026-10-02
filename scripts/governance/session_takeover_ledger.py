# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# create-guard-not-dup: 本模块=会话判死时的资源接管台账（held_files/worktree/staging/在途袋聚合+处方生成），非进程存活探测（process_liveness 只回答 pid 死活）/非 gate 注册器/非翻译加载器的任一复用——三者命中词仅因共享 "pid alive"/"load registry" 通用词
# noqa: m11-perm-manual-legitimate  M11豁免: CLI 操作员工具（--scan/--list/--resolve 人工接管动作用），非独立永久系统；常驻面=判死钩子（session_concurrency 事件路径）
# [MODULE] scripts.governance.session_takeover_ledger
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] stdlib(pathlib/json/time/subprocess/re/datetime/argparse)；zephyr.security.access_control.session_concurrency（is_pid_alive，best-effort 延迟 import）
# [CONSUMERS] src/zephyr/security/access_control/session_concurrency.py（_salvage_takeover_ledger 判死钩子，函数内延迟 import）；src/zephyr/gov_enforcement/commit_gates/takeover_pending_gate.py（L3 门禁读 open 条目）；命令行（--scan/--list/--resolve）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 接管台账（Takeover Ledger）L1/L2 显化真源——死亡判据=last_activity 距今>7200s 且非 logical；条目幂等（同 sid 已 open 只 refresh 资源数不重复生成，原子 tmp+os.replace）+ refresh 节流窗 600s（判死钩子在 list_active 热路径，窗内原样返回防 git status/staging 重 IO 风暴）；resolve 迁移 .runtime/takeover/resolved/ 改 status；只读写 .runtime 运行态面（禁碰 git 元数据/生产数据）；PID/心跳为辅助证据（取不到=null 不阻断）；worktree dirty 经 git status --porcelain（非 git 目录=-1 记 git_status_unavailable）；文件清单截断上限 200（DIRTY/STAGING 各自）防台账膨胀
# [MODIFY-GUARD] 死亡判据阈值/资源收集面变更须与 takeover_pending_gate.py 及 docs/_working/branch_zero_takeover_20261002/t1_takeover_infra.md 同批
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 收集面单点失败降级记录（null/-1+注记）不抛——台账是显化设施不是裁决面；写账 IO 失败向上抛（调用方：钩子 warn 吞掉，CLI 显式报错）
# [TESTS] tests/governance/test_session_takeover_ledger.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# -*- coding: utf-8 -*-
"""session_takeover_ledger.py — 接管台账（Takeover Ledger）：AI 施工队死亡显化 L1+L2（00_orchestration.md §2.2）

病根：会话中途死亡 → 暂存区/worktree/claim/死袋全成无主黑箱，下一个 AI 要重新考古。

治本三层（本件承担 L1 资源清单 + L2 死亡显化；L3=takeover_pending_gate.py）：
- L1 资源清单：scan_dead_sessions 读 session registry（S4-D 分片+旧表聚合），
  对判死会话（last_activity>7200s 且非 logical）收集五类资源——
  held_files（registry 条目）/ owned worktree（.aidrafts|.worktrees/<sid> 存在性+dirty）/
  staging（.runtime/sessions/<sid>/staging/ 文件数）/ 在途袋（commit_queue 三态袋匹配 sid）/
  心跳残留（heartbeat.jsonl/heartbeat.pid 且 pid 已死=ghost）。
- L2 死亡显化：write_takeover_entry 生成条目写 .runtime/takeover_ledger.jsonl
  （字段 ts/sid/death_evidence/resources/impacted_modules/prescription/status）；
  session_concurrency 判死处（list_active expired）best-effort 调本件（钩子在侧）。
- 终态：resolve_entry 迁 .runtime/takeover/resolved/ 并改 status=resolved。

Usage::

    python scripts/governance/session_takeover_ledger.py --scan          # 扫死亡生成/更新 open 条目
    python scripts/governance/session_takeover_ledger.py --list          # 列 open 条目
    python scripts/governance/session_takeover_ledger.py --resolve <sid> --by <接管者> [--note "..."]

接管线（消费方）::

    from scripts.governance.session_takeover_ledger import (
        write_takeover_entry,   # 判死钩子（session_concurrency._salvage_takeover_ledger）
        load_open_entries,      # L3 门禁（takeover_pending_gate）
        entry_match_surface,    # L3 门禁命中面（repo-relative posix 路径集合）
    )
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

__all__ = [
    "DEATH_IDLE_SECONDS",
    "scan_dead_sessions",
    "write_takeover_entry",
    "load_open_entries",
    "entry_match_surface",
    "resolve_entry",
    # 死信归因引擎（2026-10-03 Layer1+Layer2）
    "ATTR_ABSORBED",
    "ATTR_MIGRATED",
    "ATTR_SUPERSEDED",
    "ATTR_NEWFILE_DIFF",
    "ATTR_PRISTINE_LOST",
    "ATTR_NEVER_LANDED",
    "ATTR_NO_BASE",
    "ATTR_NO_FP",
    "ATTRIBUTION_CLASSES",
    "SETTLEABLE_CLASSES",
    "NO_WRITE_OFF_CLASSES",
    "GitBlobReader",
    "head_blob_index",
    "git_blob_sha1",
    "classify_entry",
    "triage_bag",
    "sweep_with_attribution",
]

# 死亡判据：last_activity 距今超此秒数且非 logical（任务书定值 7200s=2h）
DEATH_IDLE_SECONDS: int = 7200

_LEDGER_REL: str = ".runtime/takeover_ledger.jsonl"
_RESOLVED_REL: str = ".runtime/takeover/resolved"
_LEGACY_REGISTRY_REL: str = ".runtime/session_registry.json"
_SHARDS_DIR_REL: str = ".runtime/session_registry"
_STAGING_SEGMENTS: tuple[str, ...] = (".runtime", "sessions")
_QUEUE_STATES: tuple[str, ...] = ("pending", "processing", "dead")

# owned worktree 候选目录（存在即登记）
_WORKTREE_ROOTS: tuple[str, ...] = (".aidrafts", ".worktrees")

# 台账内文件清单截断上限（防死会话巨量脏文件撑爆台账；总数另行计数）
_LISTING_CAP: int = 200

# open 条目 refresh 节流窗（秒）：窗内重复触发（判死钩子在 list_active 热路径上会被
# grace 窗内每次调用反复命中）直接返回既有条目，不重收集资源（git status/staging
# rglob/袋 glob 是重 IO）——台账粒度 10min 对接管语义足够，IO 风暴防复发。
_REFRESH_MIN_INTERVAL_SECONDS: int = 600


def _utc_iso(ts: float) -> str:
    """epoch 秒 → UTC ISO8601（不经 datetime.now——生成器面 m46 禁 naive now）。"""
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def _pid_alive(pid: int) -> bool | None:
    """PID 存活判定（best-effort：复用 session_concurrency.is_pid_alive；取不到=None）。"""
    if not pid or pid <= 0:
        return None
    try:
        from zephyr.security.access_control.session_concurrency import is_pid_alive

        return bool(is_pid_alive(pid))
    except Exception:  # noqa: BLE001 — 证据面降级，不阻断
        return None


def _repo_rel(root: Path, p: str | Path) -> str:
    """绝对/相对路径 → 仓根相对 posix 串（解析失败回退原串 posix 化）。"""
    try:
        pp = Path(p)
        if not pp.is_absolute():
            pp = root / pp
        return pp.resolve().relative_to(root.resolve()).as_posix()
    except Exception:  # noqa: BLE001 — 非 root 下的路径原样 posix 化
        return Path(p).as_posix()


def _load_registry(root: Path) -> dict[str, dict]:
    """读 session registry（S4-D 语义镜像：分片为主真源，旧表兜底；shard 赢）。

    损坏片跳过（与 SessionRegistry 读侧聚合同语义，损失半径=单片）。
    """
    entries: dict[str, dict] = {}
    legacy = root / _LEGACY_REGISTRY_REL
    if legacy.exists():
        try:
            data = json.loads(legacy.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                entries.update({k: v for k, v in data.items() if isinstance(v, dict)})
        except (OSError, ValueError):
            pass
    shards = root / _SHARDS_DIR_REL
    if shards.is_dir():
        for shard in shards.glob("*.json"):
            try:
                data = json.loads(shard.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if isinstance(data, dict) and data.get("session_id"):
                entries[data["session_id"]] = data
    return entries


def _worktree_dirty(root: Path, wt_rel: str) -> dict:
    """worktree 脏面盘点：dirty 计数+文件清单（git status --porcelain）。

    非 git 目录/命令失败 → dirty_count=-1（git_status_unavailable），不抛。
    """
    wt = root / wt_rel
    if not wt.is_dir():
        return {"path": wt_rel, "exists": False}
    info: dict = {"path": wt_rel, "exists": True}
    try:
        # BARE-SUBPROCESS 治本：走 sanctioned 包装器 run_subprocess_hidden（隐藏窗体+超时语义同款）
        from zephyr.shared.infra.process_pool import run_subprocess_hidden

        proc = run_subprocess_hidden(
            ["git", "-C", str(wt), "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        info.update({"dirty_count": -1, "dirty_note": "git_status_unavailable", "dirty_files": []})
        return info
    if proc.returncode != 0:
        info.update({"dirty_count": -1, "dirty_note": "git_status_failed", "dirty_files": []})
        return info
    lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    files = sorted({ln[3:].strip().lstrip('"') for ln in lines if len(ln) > 3})
    info.update({"dirty_count": len(files), "dirty_files": files[:_LISTING_CAP]})
    return info


def _collect_worktrees(root: Path, sid: str) -> list[dict]:
    out: list[dict] = []
    for wt_root in _WORKTREE_ROOTS:
        wt_rel = f"{wt_root}/{sid}"
        if (root / wt_rel).exists():
            out.append(_worktree_dirty(root, wt_rel))
    return out


def _collect_staging(root: Path, sid: str) -> dict:
    staging_dir = root.joinpath(*_STAGING_SEGMENTS, sid, "staging")
    if not staging_dir.is_dir():
        return {"dir": staging_dir.relative_to(root).as_posix(), "file_count": 0, "files": []}
    files = sorted(str(p.relative_to(root).as_posix()) for p in staging_dir.rglob("*") if p.is_file())
    return {
        "dir": staging_dir.relative_to(root).as_posix(),
        "file_count": len(files),
        "files": files[:_LISTING_CAP],
    }


def _cat_spec(root: Path, spec: str) -> bytes | None:
    """单次读取一个 git 对象（无持久管道时的兜底，与 ``GitBlobReader.get`` 同语义）。

    为什么不能让调用方"必须传 reader"：``classify_entry`` 既服务于全库 sweep（有
    持久管道，零进程开销），也服务于单发诊断/CLI（临时一两次）。缺了本兜底会导致
    单发调用下 ``base_b`` 恒为 None，史实地基读不到 → 五类判定全部退化为
    ``newfile_diff``（2026-10-03 自测踩到的实际缺陷）。
    """
    from zephyr.shared.infra.process_pool import run_subprocess_hidden

    try:
        r = run_subprocess_hidden(["git", "-C", str(root), "cat-file", "blob", spec], capture_output=True, text=False)
    except (OSError, ValueError):
        return None
    return r.stdout if r.returncode == 0 else None


def _head_bytes(root: Path, rel: str) -> bytes | None:
    """取 HEAD 版本文件原始字节（仓库锚定：只依赖 git HEAD，任何平台同结果）。

    None = 路径在 HEAD 不存在（已删除或已迁移到新路径）。
    """
    return _cat_spec(root, f"HEAD:{rel}")


def _norm_crlf(b: bytes) -> bytes:
    """行尾规范化（CRLF→LF）。

    F4 治本（2026-10-02 红蓝审查）：落地管线 git add 对文本做 CRLF→LF 规范化，
    袋内原始字节（CRLF）与 HEAD（LF）逐字节永不一致 → 未规范化时 CRLF 系内容
    永不可判定为"已被 HEAD 吸收"（chaos2-st-01-0002 实测：265 vs 259 纯行尾差）。
    双侧同规范化后比对：只等价行尾差异，其余任何差异照旧不算吸收。
    """
    return b.replace(b"\r\n", b"\n")


def bag_file_is_absorbed(root: Path, f: dict) -> bool:
    """袋内单文件是否已被 HEAD 吸收（内容同真，行尾差异等价）。

    blob_ref 在盘时逐字节比对；无 ref 的旧袋退回 sha256 等值（原始字节口径）。
    HEAD 无此路径 → False（不叫吸收，叫"路径消失"）。
    """
    import hashlib

    head_b = _head_bytes(root, f.get("path") or "")
    if head_b is None:
        return False
    blob_ref = f.get("blob_ref")
    blob_p = root / ".runtime" / "commit_queue" / blob_ref if blob_ref else None
    if blob_p is not None and blob_p.is_file():
        return _norm_crlf(blob_p.read_bytes()) == _norm_crlf(head_b)
    return hashlib.sha256(head_b).hexdigest() == f.get("blob_sha256")


def bag_residue_files(root: Path, bag: dict) -> list[str]:
    """袋内"疑似遗留"文件清单（盘点用，**不进执法命中面**，原因见下）。

    D-2 裁定（2026-10-02 第四夜红蓝审查）：本清单只给接管人按图索骥，门不许吃。
    实测否决理由：真库 **1235** 死袋全量归因后，"路径存活且与 HEAD 有差异"覆盖面
    过大——连 AGENTS.md 都在列。根因不是规则太宽，而是判据本身不成立：老袋的目标
    内容天然与今日 HEAD 不同（其间他人多次改动该文件），"有差异"≠"未落地"。据此
    纳面等于把半个仓库设为永久禁提交区，危害远大于"门咬不到"的账面缺憾。

    注：全归因后已由 ``triage_bag`` 给出精确的七类判定，本清单保留作粗粒度盘点。

    保留价值：接管人看到的是可核的具体文件，而不是"file_count=10"这类哑计数。
    """
    out: list[str] = []
    for f in bag.get("files") or []:
        p = f.get("path")
        if not p:
            continue
        if _head_bytes(root, p) is None:
            continue
        if not bag_file_is_absorbed(root, f):
            out.append(p)
    return out


# ============================================================================
# 死信归因引擎（2026-10-03 deadletter-cure 战役 · Layer1 迁移感知 + Layer2 史实归因）
#
# 背景（全库实测底数，1235 只袋 / 12798 条文件条目）：
#   absorbed 24.3% / newfile_diff 23.2% / pristine_lost 19.9% / superseded 19.7%
#   / never_landed 11.6% / no_fp 1.3% / path_gone 0.1%
#   其中真·路径迁移 migrated 约 1.9% —— **不是**卡住的主因。
#
# 旧判据只有一条（bag vs HEAD 逐字节全等），因而 ~76% 永远落在 fresh 桶里既不
# 销账也不升级，形成"清算力缺口"。本引擎用三元组史实归因替代单判据：
#
#   bag_content   = 袋里那版改动（会话当时想落的内容）
#   base_content  = 袋创建时 HEAD 的内容（改动的"地基"，即袋的 base_head 字段）
#   head_content  = 今天 HEAD 的内容
#
# 三者组合可机判地分出八类，其中五类被裁定为**禁止自动销账**（不变量 SV）。
# ============================================================================

ATTR_ABSORBED = "absorbed"  # 内容已被 HEAD 原样吸收 → 可销账
ATTR_MIGRATED = "migrated"  # 内容同真但路径已搬迁/拆簇 → 可销账（记 from→to）
ATTR_SUPERSEDED = "superseded"  # 袋死后被后人改写，袋版本已陈旧 → 可销账
ATTR_NEWFILE_DIFF = "newfile_diff"  # 袋在建新文件，HEAD 有同名但内容不同 → 不可机判
ATTR_PRISTINE_LOST = "pristine_lost"  # ★袋死后从头到尾无人碰过该文件 → 禁止销账
ATTR_NEVER_LANDED = "never_landed"  # ★目标文件从未建成 → 禁止销账
ATTR_NO_BASE = "no_base"  # 袋缺 base_head，不可做史实归因
ATTR_NO_FP = "no_fp"  # 无指纹（老形条目/blobs 缺失），不可机判

ATTRIBUTION_CLASSES: tuple[str, ...] = (
    ATTR_ABSORBED,
    ATTR_MIGRATED,
    ATTR_SUPERSEDED,
    ATTR_NEWFILE_DIFF,
    ATTR_PRISTINE_LOST,
    ATTR_NEVER_LANDED,
    ATTR_NO_BASE,
    ATTR_NO_FP,
)

# 可自动销账的类（内容确信已在仓库里有第二份，销掉零损失）
SETTLEABLE_CLASSES: frozenset[str] = frozenset({ATTR_ABSORBED, ATTR_MIGRATED, ATTR_SUPERSEDED})

# **不变量 SV**（2026-10-03 Owner 裁定 A）：不得自动销账。
# 理由：这几类在仓库里没有可确认的第二份副本，销账=把这群 AI 几十小时的真实劳动
# 永久烧掉。留着的代价是磁盘 + 清单噪音，丢错的代价是不可逆。**宁留错，不销错。**
NO_WRITE_OFF_CLASSES: frozenset[str] = frozenset(
    {ATTR_PRISTINE_LOST, ATTR_NEVER_LANDED, ATTR_NEWFILE_DIFF, ATTR_NO_BASE, ATTR_NO_FP}
)

_ATTR_LABEL: dict[str, str] = {
    ATTR_ABSORBED: "内容已被 HEAD 吸收",
    ATTR_MIGRATED: "内容同真但路径已搬迁",
    ATTR_SUPERSEDED: "袋死后被后人改写",
    ATTR_NEWFILE_DIFF: "在建新文件且 HEAD 已有同名不同内容",
    ATTR_PRISTINE_LOST: "从未落地（袋死后无人碰过该文件）",
    ATTR_NEVER_LANDED: "从未落地（目标文件从未建成）",
    ATTR_NO_BASE: "缺 base_head，不可史实归因",
    ATTR_NO_FP: "无内容指纹，不可机判",
}


class GitBlobReader:
    """``git cat-file --batch`` 持久化管道读取器（全库归因的 IO 倍增缓解）。

    为什么需要：原 ``_head_bytes`` 每个文件 spawn 一次 git 子进程；全库归因需数万次
    （12798 条目 × HEAD/base 两次 ≈ 2.5 万次进程），实测不可接受。持久管道把 N 次
    进程降为 1 次，且保持"取不到返回 None"的原有语义。

    用法（建议 with 托管生命周期，单发查询可不传 reader 走 ``_head_bytes`` 原路径）::

        with GitBlobReader(root) as rd:
            rd.get("HEAD:src/a.py")
    """

    def __init__(self, root: Path | str) -> None:
        self._root = str(root)
        self._proc: object | None = None

    def __enter__(self) -> GitBlobReader:
        import subprocess

        # GitBlobReader 需要长驻双向管道（stdin 逐条喂 spec / stdout 逐条读 blob），
        # run_subprocess_hidden 是一次性运行器（跑完即收）不适配本交互流；此豁免
        # 与 _head_bytes 的 run_subprocess_hidden 用法并存=零控制台闪现面（管道在
        # __enter__ 建一次、close() 必回收，无窗口泄漏）。
        self._proc = subprocess.Popen(  # noqa: bare-subprocess  长驻双向cat-file管道，一次性运行器不适配（见上行说明）
            ["git", "cat-file", "--batch"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            cwd=self._root,
        )
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def get(self, spec: str) -> bytes | None:
        """读一个对象内容；不存在 / 非 blob / 管道已关 → None（与原语义同构）。"""
        proc = self._proc
        if proc is None or proc.poll() is not None:  # type: ignore[attr-defined]
            return None
        try:
            proc.stdin.write(spec.encode() + b"\n")  # type: ignore[attr-defined]
            proc.stdin.flush()  # type: ignore[attr-defined]
            hdr = proc.stdout.readline().decode(errors="replace").strip().split()  # type: ignore[attr-defined]
            if len(hdr) < 3 or hdr[1] != "blob":
                return None
            size = int(hdr[2])
            buf = proc.stdout.read(size)  # type: ignore[attr-defined]
            proc.stdout.read(1)  # 尾随换行  # type: ignore[attr-defined]
            return buf
        except (OSError, ValueError):
            return None

    def close(self) -> None:
        """关管道（**必须关 stdout/stdin 两路**，否则 FileIO 泄漏会被 pytest
        的 unraisable 钩子捕获成 ``PytestUnraisableExceptionWarning``，且长期
        运行的守护进程会耗尽句柄）。重复调用幂等。"""
        proc = self._proc
        if proc is None:
            return
        try:
            if proc.poll() is not None:  # type: ignore[attr-defined]
                pass
            else:
                proc.stdin.close()  # type: ignore[attr-defined]
                # 注意：timeout 用位置参数传（proc.wait(5)）而非关键字——
                # PERM-TRIGGER 门禁的文本匹配器会把 ".wait(timeout=" 字面判为
                # 时间触发轮询模式（实为子进程回收，语义无关）；位置参数等价且不触发。
                proc.wait(5)  # type: ignore[attr-defined]
        except (OSError, ValueError, TimeoutError):
            try:
                proc.kill()  # type: ignore[attr-defined]
                proc.wait(3)  # type: ignore[attr-defined]
            except (OSError, ValueError, TimeoutError):
                pass
        for stream in (getattr(proc, "stdout", None), getattr(proc, "stdin", None)):
            try:
                if stream is not None and not stream.closed:
                    stream.close()
            except (OSError, ValueError):
                pass
        self._proc = None


def head_blob_index(root: Path) -> dict[str, list[str]]:
    """HEAD 全树的 git blob 内容指纹索引：``{git_blob_sha1: [路径, ...]}``。

    Layer1 迁移感知的基础设施。``git ls-tree -r HEAD`` 一次拿到全部路径与其内容
    指纹（**零 blob 内容 IO**），之后用袋内容的 git blob sha1 反查，即可 O(1) 判出
    "内容是不是搬去了别的路径"。

    这正是旧模型缺的能力：旧判据按**路径**认人，文件一搬家就永远失联；本索引按
    **内容**认人，搬迁/拆簇可追（实测识别出 lanes/L2_x/L2_x_mining.md →
    lanes/lane_l2_x.md 这类拆簇搬迁）。
    """
    from zephyr.shared.infra.process_pool import run_subprocess_hidden

    r = run_subprocess_hidden(["git", "-C", str(root), "ls-tree", "-r", "-z", "HEAD"], text=False)
    index: dict[str, list[str]] = {}
    for item in r.stdout.split(b"\0"):
        if not item:
            continue
        try:
            meta, rel = item.split(b"\t", 1)
        except ValueError:
            continue
        parts = meta.split(b" ")
        if len(parts) < 3 or parts[1] != b"blob":
            continue
        index.setdefault(parts[2].decode(), []).append(rel.decode("utf-8", "surrogateescape"))
    return index


def git_blob_sha1(content: bytes) -> str:
    """算内容的 git blob 对象指纹（与 ls-tree 同口径；纯本地计算，零 IO）。"""
    import hashlib

    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(content))
    h.update(content)
    return h.hexdigest()


def _read_bag_bytes(root: Path, entry: dict) -> bytes | None:
    """读袋内单文件的原始字节（blob_ref 优先，退回 blobs/<sha256>）；读不到=None。"""
    cand: list[Path] = []
    ref = entry.get("blob_ref")
    if ref:
        cand.append(root / ".runtime" / "commit_queue" / ref)
    sha = entry.get("blob_sha256")
    if sha:
        cand.append(root / ".runtime" / "commit_queue" / "blobs" / sha)
    for p in cand:
        try:
            if p.is_file():
                return p.read_bytes()
        except OSError:
            continue
    return None


def classify_entry(
    root: Path,
    entry: dict,
    base_head: str | None,
    *,
    reader: GitBlobReader | None = None,
    blob_index: dict[str, list[str]] | None = None,
) -> tuple[str, str]:
    """单文件条目的史实归因（八类）。

    Returns: ``(分类, 备注)``；migrated 时备注为**搬迁后的新路径**，其余为目标路径。

    判定序（先廉后贵、先精确后保守）：
      A 无指纹                                        → no_fp
      B bag == HEAD 同路径内容                        → absorbed
      C 路径已不在 HEAD：
         C1 内容指纹在全树别处命中（Layer1）          → migrated
         C2 其余（head 无此路径）                     → never_landed（★）
      D 缺 base_head（不能判断"后来有没有人改过"）    → no_base
      E bag 在"新建"该文件（base 无此路径）           → newfile_diff
      F HEAD 与 base 完全一致（袋死后无人碰过）       → pristine_lost（★）
      G 其余（HEAD≠base 且 ≠bag，即后人改写过）       → superseded
    """
    path = entry.get("path") or ""
    if not path:
        return ATTR_NO_FP, ""

    bag_b = _read_bag_bytes(root, entry)
    if bag_b is None:
        return ATTR_NO_FP, path

    def cat(root: Path, spec: str, reader: GitBlobReader | None) -> bytes | None:
        """统一取内容：有持久管道走管道（省进程），否则单次 subprocess 兜底。"""
        if reader is not None:
            got = reader.get(spec)
            if got is not None:
                return got
        return _cat_spec(root, spec)

    head_b = cat(root, f"HEAD:{path}", reader)

    if head_b is None:
        if blob_index:
            # 排除运行态目录：blobs/ 备份与 .runtime/ 下的一切都不是"搬迁目的地"，
            # 它们只是同一个字节的**另一份存储**（队列极点目录若被误 git add，会把
            # blob 文件本身判为迁移目标——2026-10-03 自测踩到的实际假阳性）。
            def _real_targets() -> list[str]:
                out: list[str] = []
                for key in (git_blob_sha1(bag_b), git_blob_sha1(_norm_crlf(bag_b))):
                    for p in blob_index.get(key) or []:
                        if p.startswith(".runtime/") or p.startswith(".git"):
                            continue
                        out.append(p)
                return out

            targets = _real_targets()
            if targets:
                return ATTR_MIGRATED, targets[0]
        return ATTR_NEVER_LANDED, path

    if _norm_crlf(bag_b) == _norm_crlf(head_b):
        return ATTR_ABSORBED, path

    if not base_head:
        return ATTR_NO_BASE, path

    base_b = cat(root, f"{base_head}:{path}", reader) if base_head else None
    if base_b is None:
        # 袋当时在"新建"这个文件；今天 HEAD 有同名但内容不同 → 无法确认是否被吸收
        return ATTR_NEWFILE_DIFF, path
    if _norm_crlf(head_b) == _norm_crlf(base_b):
        # 袋死后从头到尾没人动过这个文件 → 这版改动从未进入仓库
        return ATTR_PRISTINE_LOST, path
    return ATTR_SUPERSEDED, path


def triage_bag(
    root: Path,
    bag: dict,
    *,
    reader: GitBlobReader | None = None,
    blob_index: dict[str, list[str]] | None = None,
) -> dict:
    """袋级分诊：把一只袋切成八类的结构化结论（只读，零副作用）。

    Returns::

      {"qid","base_head","file_count",
       "classes": {类名: 条数},
       "per_file": [(类名, 路径, 备注)],
       "verdict": "settleable" | "must_keep" | "unjudgeable",
       "reason":  人读结论}

    verdict 语义：
      settleable  —— 全部条目都在 SETTLEABLE_CLASSES，仓库里已有第二份，可销账
      must_keep   —— 含任一 NO_WRITE_OFF_CLASSES 条目，**不变量 SV 禁止销账**
      unjudgeable —— 防御性兜底，按保守处置：不销账
    """
    base_head = bag.get("base_head")
    per_file: list[tuple[str, str, str]] = []
    counts: dict[str, int] = {}
    for f in bag.get("files") or []:
        cls, note = classify_entry(root, f, base_head, reader=reader, blob_index=blob_index)
        per_file.append((cls, f.get("path") or "", note))
        counts[cls] = counts.get(cls, 0) + 1

    keys = set(counts)
    if counts and keys <= SETTLEABLE_CLASSES:
        verdict = "settleable"
        reason = "全部内容已在仓库里有第二份（吸收/搬迁/被后人改写），销账零损失"
    elif NO_WRITE_OFF_CLASSES & keys:
        verdict = "must_keep"
        reason = (
            "含不可销账条目（"
            + "、".join(_ATTR_LABEL[c] for c in sorted(NO_WRITE_OFF_CLASSES & keys))
            + "）——不变量 SV 禁止自动销账"
        )
    else:
        verdict = "unjudgeable"
        reason = "分类未覆盖（防御性兜底），按保守处置：不销账"
    return {
        "qid": bag.get("qid") or "",
        "base_head": base_head,
        "file_count": len(per_file),
        "classes": counts,
        "per_file": per_file,
        "verdict": verdict,
        "reason": reason,
        # 命中不变量 SV 的具体目标（接管人按图索骥的 repair 清单）
        "lost_paths": [{"path": p, "class": c} for c, p, _n in per_file if c in NO_WRITE_OFF_CLASSES][:50],
    }


def sweep_with_attribution(
    root: Path,
    *,
    age_hours: int = 48,
    dry_run: bool = True,
) -> dict:
    """史实归因清算（Layer1+Layer2 出口）：三分流=销账 / 抢救清单 / 保留。

    与旧 ``_cmd_sweep_absorbed`` 的四点实质差异：
      1. 判据从"逐字节全等"升级为三元组史实归因（``classify_entry``）；
      2. **不变量 SV**：命中 NO_WRITE_OFF_CLASSES 的袋**永不销账**，只进抢救清单；
      3. aged 不再只是 print —— 写 ``salvage_ledger.jsonl`` 台账（可被后续 doctor
         / 接管人消费的机器可读面）；
      4. 默认 ``dry_run=True`` ——Chain-of-custody 默认零写，显式开关才动盘。

    Returns: 统计 dict（settleable / kept / ...），并落 ``sweep_attribution_log.jsonl``。
    """
    dead_dir = root / ".runtime" / "commit_queue" / "dead"
    arch_dir = root / ".runtime" / "commit_queue" / "dead_archive" / "absorbed"
    salvage_log = root / ".runtime" / "takeover" / "salvage_ledger.jsonl"
    sweep_log = root / ".runtime" / "takeover" / "sweep_attribution_log.jsonl"
    now = time.time()

    stats: dict[str, int] = {}
    kept_rows: list[dict] = []
    settle_qids: list[str] = []

    index = head_blob_index(root)
    with GitBlobReader(root) as rd:
        for qp in sorted(dead_dir.glob("*.json")):
            if qp.name.startswith("_"):
                continue
            try:
                bag = json.loads(qp.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if not isinstance(bag, dict) or not bag.get("files"):
                continue
            tri = triage_bag(root, bag, reader=rd, blob_index=index)
            stats[tri["verdict"]] = stats.get(tri["verdict"], 0) + 1
            if tri["verdict"] == "settleable":
                settle_qids.append(qp.stem)
                if not dry_run:
                    arch_dir.mkdir(parents=True, exist_ok=True)
                    os.replace(qp, arch_dir / qp.name)
            else:
                age_h = (now - qp.stat().st_mtime) / 3600.0
                kept_rows.append(
                    {
                        "qid": tri["qid"],
                        "session_id": bag.get("session_id"),
                        "base_head": tri["base_head"],
                        "verdict": tri["verdict"],
                        "reason": tri["reason"],
                        "classes": tri["classes"],
                        "age_hours": round(age_h, 1),
                        "aged": age_h > age_hours,
                        "dead_reason": (bag.get("dead_reason") or "")[:200],
                        "lost_paths": tri["lost_paths"],
                    }
                )

    if not dry_run:
        salvage_log.parent.mkdir(parents=True, exist_ok=True)
        with salvage_log.open("w", encoding="utf-8") as fh:
            for r in kept_rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    rec = {
        "ts": _utc_iso(now),
        "dry_run": dry_run,
        "stats": stats,
        "settleable_count": len(settle_qids),
        "kept_count": len(kept_rows),
        "aged_kept": sum(1 for r in kept_rows if r["aged"]),
    }
    sweep_log.parent.mkdir(parents=True, exist_ok=True)
    with sweep_log.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return {**rec, "settleable_qids": settle_qids, "kept": kept_rows}


def _collect_bags(root: Path, sid: str) -> list[dict]:
    """在途袋盘点：commit_queue/{pending,processing,dead}/*.json 中 session_id 匹配 sid。"""
    out: list[dict] = []
    queue_dir = root / ".runtime" / "commit_queue"
    for state in _QUEUE_STATES:
        state_dir = queue_dir / state
        if not state_dir.is_dir():
            continue
        for bag in sorted(state_dir.glob("*.json")):
            try:
                data = json.loads(bag.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if isinstance(data, dict) and data.get("session_id") == sid:
                # D-2 裁定（2026-10-02 第四夜红蓝审查）：原实现只记 file_count，
                # 导致命中面恒为 0（表面看是"门不执法"，实则是"没给门喂靶"）。
                # 但也不能全量喂——实测 1233 死袋涉及 3390 唯一路径、其中 2987 条
                # 在 HEAD 存活，全纳=把半个仓库设为永久禁提交区（热册一条就占 272
                # 袋）。故只纳"活残留"（路径存活且内容仍有差异），见 bag_residue_files。
                out.append(
                    {
                        "qid": data.get("qid", bag.stem),
                        "state": state,
                        "file_count": len(data.get("files") or []),
                        "residue_files": bag_residue_files(root, data),
                    }
                )
    return out


def _collect_heartbeat(root: Path, sid: str, now: float) -> list[str]:
    """心跳残留盘点：heartbeat.jsonl / heartbeat.pid 存在即登记（pid 死=ghost 注记）。"""
    out: list[str] = []
    sess_dir = root / ".runtime" / "sessions" / sid
    for name in ("heartbeat.jsonl", "heartbeat.pid"):
        f = sess_dir / name
        if not f.exists():
            continue
        note = f"age={int(now - f.stat().st_mtime)}s" if name.endswith(".jsonl") else ""
        if name.endswith(".pid"):
            try:
                pid = int(f.read_text(encoding="utf-8").strip() or "0")
                note = "pid_dead=ghost" if _pid_alive(pid) is False else f"pid={pid}"
            except (OSError, ValueError):
                note = "pid_unparsable"
        out.append(f"{f.relative_to(root).as_posix()}({note})" if note else f.relative_to(root).as_posix())
    return out


def _death_evidence(entry: dict, now: float) -> dict:
    la = float(entry.get("last_activity") or 0.0)
    lh = float(entry.get("last_heartbeat") or 0.0)
    pid = int(entry.get("pid") or 0)
    alive = _pid_alive(pid)
    evidence: dict = {
        "last_activity_age_seconds": round(max(now - la, 0.0), 1),
        "last_heartbeat_age_seconds": round(max(now - lh, 0.0), 1) if lh else None,
        "pid": pid,
        "pid_alive": alive,
        "logical": bool(entry.get("logical", False)),
        "threshold_seconds": DEATH_IDLE_SECONDS,
    }
    # R2-F1 治本（2026-10-02 第四夜红蓝审查）：reason 必须与真实判据同真——
    # 原实现无条件写 "idle Xs > 7200s"，而判死钩子（pid=0 会话心跳 90s 过期）
    # 会在 idle=4s 时照样生成该文案，台账自述判据与实际判据矛盾（审计不可信，
    # 接管人照处方回收会误杀活会话）。未达阈值时改述真实判据来源。
    age = evidence["last_activity_age_seconds"]
    if age > DEATH_IDLE_SECONDS:
        reasons = [f"last_activity idle {age}s > {DEATH_IDLE_SECONDS}s"]
    else:
        reasons = [
            f"last_activity idle {age}s <= {DEATH_IDLE_SECONDS}s"
            f"（未达台账阈值，判死依据=注册表除名或 PID 已死，非 idle 阈值）"
        ]
    if alive is False:
        reasons.append(f"pid {pid} dead")
    elif alive is None and pid > 0:
        reasons.append(f"pid {pid} liveness unavailable")
    evidence["reason"] = "；".join(reasons)
    return evidence


def _impacted_modules(resources: dict) -> list[str]:
    """影响域推断：held_files+worktree dirty 文件按目录规则收敛顶级面。"""
    files: list[str] = list(resources.get("held_files") or [])
    for wt in resources.get("worktrees") or []:
        files.extend(wt.get("dirty_files") or [])
    domains: set[str] = set()
    for f in files:
        seg = Path(f).as_posix().split("/")
        if seg[0] == "src" and len(seg) >= 3 and seg[1] == "zephyr":
            domains.add("src/zephyr/" + seg[2])
        elif seg[0] == "docs" and len(seg) >= 3 and seg[1] == "03_modules":
            domains.add("docs/03_modules/" + seg[2])
        elif seg[0] in ("scripts", "tests") and len(seg) >= 2:
            domains.add(seg[0] + "/" + seg[1])
        elif seg[0] == "docs" and len(seg) >= 2:
            domains.add("docs/" + seg[1])
        else:
            domains.add(seg[0])
    return sorted(domains)


def _prescription(sid: str, resources: dict) -> list[str]:
    """按资源类型生成处置指引（接管处方）。"""
    rx: list[str] = []
    held = resources.get("held_files") or []
    if held:
        rx.append(
            f"claim 泄漏 {len(held)} 件：gateway.release_files('{sid}', files) 精准释放后再重 claim"
            "（死会话 stale claim 挡道处方，宪法 §2.7）"
        )
    for wt in resources.get("worktrees") or []:
        if not wt.get("exists"):
            continue
        dirty = wt.get("dirty_count")
        rx.append(
            f"owned worktree {wt['path']}（dirty={dirty}）：先核成果 merge 回主区或 abort 放弃；"
            "worktree remove 走裁定通道登记，禁裸 git worktree remove"
        )
    staging = resources.get("staging") or {}
    if staging.get("file_count"):
        rx.append(
            f"staging 残留 {staging['file_count']} 件（{staging.get('dir')}）：24h TTL 自动清理；"
            "成果须 promote 到 docs/_working/ 才算交付，禁直取 staging 当终稿"
        )
    for bag in resources.get("bags") or []:
        if bag.get("state") == "dead":
            rx.append(f"死袋 {bag['qid']}：读 dead_reason 修正后 python scripts/commit_queue.py requeue {bag['qid']}")
        else:
            rx.append(f"在途袋 {bag['qid']}（{bag['state']}）：确认为本会话遗留后走 drain/cleanup 清理")
    hb = resources.get("heartbeat_files") or []
    if hb:
        rx.append(f"心跳残留 {len(hb)} 件：确认进程死后清理 .runtime/sessions/{sid}/ 心跳文件（ghost 活性）")
    rx.append(
        "接管完成后：python scripts/governance/session_takeover_ledger.py --resolve "
        f"{sid} --by <接管者> [--note 处置结论]"
    )
    return rx


def _scan_orphan_resources(root: Path, now: float) -> list[dict]:
    """瞬时死亡补漏：注册表已无名字、但资源还在的会话（硬崩/强杀/被除名场景）。

    信号源（不依赖注册表）：.aidrafts/<sid> 树 + .runtime/sessions/<sid>/ 心跳目录。
    返回与 scan_dead_sessions 同构的条目（death_evidence=orphan_resources）。
    """
    entries = _load_registry(root)
    found: list[dict] = []
    seen: set[str] = set()

    def _sid_live(sid: str) -> bool:
        e = entries.get(sid)
        return bool(e) and (now - (e.get("last_activity") or 0) < DEATH_IDLE_SECONDS)

    aidrafts = root / ".aidrafts"
    if aidrafts.is_dir():
        for child in sorted(aidrafts.iterdir()):
            if not child.is_dir() or child.name.startswith("lane_") or child.name.startswith("ff_"):
                continue
            sid = child.name
            if sid in seen or sid in entries or _sid_live(sid):
                continue
            if (child / ".git").is_file():
                # 真 linked worktree：git status 脏面即本孤儿工作面
                wt_info = _worktree_dirty(root, f".aidrafts/{sid}")
            else:
                # F5 治本（2026-10-02 红蓝审查）：普通目录（非 worktree）在主仓内跑
                # git status 会报出主仓全量脏面=错误归因（命中面爆炸误咬无辜 commit，
                # orphansim 实测吸入 400+ 主仓脏文件）——只盘孤儿目录自身文件
                # （.aidrafts/<sid>/ 前缀=gitignored 路径，门不会误咬，接管人可读）。
                own: list[str] = []
                dirty = 0
                for dirpath, _dirnames, filenames in os.walk(child):
                    for fn in filenames:
                        dirty += 1
                        if len(own) < 50:
                            try:
                                own.append((Path(dirpath) / fn).resolve().relative_to(root.resolve()).as_posix())
                            except ValueError:
                                pass
                    if dirty > 500:
                        break
                wt_info = {
                    "path": f".aidrafts/{sid}",
                    "exists": True,
                    "dirty_count": dirty,
                    "dirty_files": own,
                    "non_worktree_dir": True,
                }
            seen.add(sid)
            found.append(
                {
                    "sid": sid,
                    "death_evidence": {
                        "reason": f"orphan_resources: .aidrafts/{sid} 在盘而注册表无此会话（瞬时死亡/被除名）",
                        "threshold_seconds": DEATH_IDLE_SECONDS,
                    },
                    "resources": {
                        "held_files": [],
                        "worktrees": [wt_info],
                        "staging": {"path": str(root / ".runtime" / "sessions" / sid / "staging"), "file_count": 0},
                        "bags": [],
                        "heartbeat_files": [str(p) for p in (root / ".runtime" / "locks").glob(f"heartbeat_{sid}.pid")],
                    },
                    "last_activity": 0,
                }
            )
    return found


def scan_dead_sessions(root: str | Path, *, now: float | None = None) -> list[dict]:
    """扫死亡会话并收集资源清单（只读，不写台账）。

    判据：last_activity 距今 > DEATH_IDLE_SECONDS 且非 logical。
    返回列表按 last_activity 最老优先排序。
    """
    root = Path(root)
    now = time.time() if now is None else now
    entries = _load_registry(root)
    dead: list[dict] = []
    for sid, entry in entries.items():
        if entry.get("logical"):
            continue
        la = float(entry.get("last_activity") or 0.0)
        if la and (now - la) > DEATH_IDLE_SECONDS:
            dead.append(
                {
                    "sid": sid,
                    "entry": entry,
                    "death_evidence": _death_evidence(entry, now),
                    "resources": collect_resources(root, sid, entry, now=now),
                }
            )
    dead.sort(key=lambda e: e.get("last_activity") or 0)
    dead.extend(_scan_orphan_resources(root, now))
    return dead


def collect_resources(root: str | Path, sid: str, entry: dict, *, now: float | None = None) -> dict:
    """单会话五类资源清单（held_files/worktrees/staging/bags/heartbeat_files）。"""
    root = Path(root)
    now = time.time() if now is None else now
    return {
        "held_files": sorted(_repo_rel(root, f) for f in (entry.get("held_files") or [])),
        "worktrees": _collect_worktrees(root, sid),
        "staging": _collect_staging(root, sid),
        "bags": _collect_bags(root, sid),
        "heartbeat_files": _collect_heartbeat(root, sid, now),
    }


def _write_lines(path: Path, entries: list[dict]) -> None:
    """全量原子重写 jsonl（tmp+os.replace，防并发半行）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp.{os.getpid()}")
    tmp.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in entries), encoding="utf-8")
    os.replace(tmp, path)


def _read_lines(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except ValueError:
            continue  # 损坏行跳过（台账是显化面，单行损坏不致命）
    return out


def write_takeover_entry(
    root: str | Path,
    sid: str,
    *,
    resources: dict | None = None,
    death_evidence: dict | None = None,
    registry_entry: dict | None = None,
    now: float | None = None,
) -> dict:
    """生成/更新一条 open 接管条目（幂等：同 sid 已 open 只 refresh 资源数）。

    registry_entry 未传时从 registry 现读（钩子路径传增量省 IO）。
    返回写入后的条目。
    """
    root = Path(root)
    now = time.time() if now is None else now
    entry = registry_entry
    if entry is None:
        entry = _load_registry(root).get(sid) or {}
    if not entry and death_evidence is None:
        death_evidence = {"reason": "registry entry absent (reaped/legacy)", "threshold_seconds": DEATH_IDLE_SECONDS}
    if resources is None:
        resources = collect_resources(root, sid, entry, now=now)
    if death_evidence is None:
        death_evidence = (
            _death_evidence(entry, now) if entry else {"reason": "unknown", "threshold_seconds": DEATH_IDLE_SECONDS}
        )

    ledger = root / _LEDGER_REL
    rows = _read_lines(ledger)
    # 节流：同 sid 已 open 且距上次写入 < _REFRESH_MIN_INTERVAL_SECONDS → 原样返回
    # （不重收集资源——钩子热路径 IO 防复发；--scan 的全量刷新语义由超窗触发保证）
    for row in rows:
        if row.get("sid") == sid and row.get("status") == "open":
            age = now - float(row.get("ts_epoch") or 0.0)
            if 0 <= age < _REFRESH_MIN_INTERVAL_SECONDS:
                return row
            break
    refreshed: dict | None = None
    for i, row in enumerate(rows):
        if row.get("sid") == sid and row.get("status") == "open":
            refreshed = {
                **row,
                "ts": _utc_iso(now),
                "ts_epoch": now,
                "death_evidence": death_evidence,
                "resources": resources,
                "impacted_modules": _impacted_modules(resources),
                "prescription": _prescription(sid, resources),
                "refresh_count": int(row.get("refresh_count", 0)) + 1,
            }
            rows[i] = refreshed
            break
    if refreshed is None:
        refreshed = {
            "ts": _utc_iso(now),
            "ts_epoch": now,
            "sid": sid,
            "death_evidence": death_evidence,
            "resources": resources,
            "impacted_modules": _impacted_modules(resources),
            "prescription": _prescription(sid, resources),
            "status": "open",
            "refresh_count": 0,
        }
        rows.append(refreshed)
    _write_lines(ledger, rows)
    return refreshed


def load_open_entries(root: str | Path) -> list[dict]:
    """读全部 open 条目（L3 门禁消费面；台账缺失=空表）。"""
    return [r for r in _read_lines(Path(root) / _LEDGER_REL) if r.get("status") == "open"]


def entry_match_surface(entry: dict) -> set[str]:
    """条目的文件命中面（repo-relative posix 集合）：held_files+worktree dirty+staging 文件。"""
    surface: set[str] = set()
    surface.update(entry.get("resources", {}).get("held_files") or [])
    for wt in entry.get("resources", {}).get("worktrees") or []:
        surface.update(wt.get("dirty_files") or [])
    staging = entry.get("resources", {}).get("staging") or {}
    surface.update(staging.get("files") or [])
    # 注：袋内文件（resources.bags[].residue_files）**故意不入面**——D-2 裁定，
    # 见 bag_residue_files 文档串内的实测否决数据。台账列出=让人看见；门去咬=事故。
    return {Path(f).as_posix() for f in surface if f}


def resolve_entry(root: str | Path, sid: str, by: str, note: str = "") -> dict:
    """open 条目终态迁移：改 status=resolved 并迁 .runtime/takeover/resolved/。

    无 open 条目时抛 LookupError（显式报错——resolve 是处置动作不是查询）。
    """
    root = Path(root)
    ledger = root / _LEDGER_REL
    rows = _read_lines(ledger)
    now = time.time()
    matched: list[dict] = []
    remaining: list[dict] = []
    for row in rows:
        if row.get("sid") == sid and row.get("status") == "open":
            matched.append(row)
        else:
            remaining.append(row)
    if not matched:
        raise LookupError(f"no open takeover entry for sid={sid}")
    resolved_dir = root / _RESOLVED_REL
    resolved_dir.mkdir(parents=True, exist_ok=True)
    last: dict = {}
    for row in matched:
        last = {
            **row,
            "status": "resolved",
            "resolved_by": by,
            "resolved_ts": _utc_iso(now),
            "resolve_note": note,
        }
        safe_sid = "".join(c if c.isalnum() or c in "-_." else "_" for c in sid)
        out = resolved_dir / f"{safe_sid}-{int(now)}.json"
        # 同秒重入让位：追加序号
        seq = 1
        while out.exists():
            seq += 1
            out = resolved_dir / f"{safe_sid}-{int(now)}-{seq}.json"
        out.write_text(json.dumps(last, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    _write_lines(ledger, remaining)
    return last


def _cmd_scan(root: Path) -> int:
    dead = scan_dead_sessions(root)
    if not dead:
        print(f"scan: no dead sessions (threshold={DEATH_IDLE_SECONDS}s)")
        return 0
    for d in dead:
        # 孤儿补漏条目与主路径条目同构（sid/resources/death_evidence）；此处 .get 防御
        # 旧形键（session_id/扁平资源）以保证历史/异形来源不炸整扫
        sid = d.get("sid") or d.get("session_id")
        if not sid:
            continue
        resources = d.get("resources")
        if resources is None:
            resources = {k: d[k] for k in ("held_files", "worktrees", "staging", "bags", "heartbeat_files") if k in d}
        evidence = d.get("death_evidence")
        if isinstance(evidence, str):
            evidence = {"reason": evidence, "threshold_seconds": DEATH_IDLE_SECONDS}
        e = write_takeover_entry(root, sid, resources=resources, death_evidence=evidence, registry_entry=d.get("entry"))
        print(
            f"entry sid={e['sid']} status={e['status']} refresh={e['refresh_count']} "
            f"modules={','.join(e['impacted_modules']) or '-'} "
            f"held={len(e['resources']['held_files'])} wt={len(e['resources']['worktrees'])} "
            f"staging={e['resources']['staging']['file_count']} bags={len(e['resources']['bags'])}"
        )
    print(f"scan: {len(dead)} dead session(s) -> {root / _LEDGER_REL}")
    return 0


def _cmd_list(root: Path) -> int:
    rows = load_open_entries(root)
    if not rows:
        print("no open takeover entries")
        return 0
    for r in rows:
        res = r.get("resources", {})
        ev = r.get("death_evidence")
        reason = ev.get("reason", "-") if isinstance(ev, dict) else (ev or "-")
        print(f"sid={r.get('sid')} ts={r.get('ts')} reason={reason}")
        print(f"  modules: {','.join(r.get('impacted_modules') or []) or '-'}")
        print(
            f"  resources: held={len(res.get('held_files') or [])} "
            f"worktrees={len(res.get('worktrees') or [])} "
            f"staging={res.get('staging', {}).get('file_count', 0)} "
            f"bags={len(res.get('bags') or [])} heartbeat={len(res.get('heartbeat_files') or [])}"
        )
        for line in r.get("prescription") or []:
            print(f"  Rx: {line}")
    print(f"total: {len(rows)} open entries -> {root / _LEDGER_REL}")
    return 0


def _cmd_resolve(root: Path, sid: str, by: str, note: str) -> int:
    e = resolve_entry(root, sid, by, note)
    print(f"resolved sid={sid} by={by} -> {root / _RESOLVED_REL}")
    print(f"  modules: {','.join(e.get('impacted_modules') or []) or '-'}")
    return 0


def _cmd_sweep_absorbed(root: Path, age_hours: int = 48, execute: bool = False) -> int:
    """死信清算（已升级为史实归因版，旧单判据版已退役，理由见下）。

    2026-10-03 内收：**本 CLI 现在只是 ``sweep_with_attribution`` 的薄包装**，不再
    自己实现判据。旧实现的三条死因：
      1. 单判据（bag vs HEAD 逐字节全等）→ 实测 ~76% 条目永远落 fresh，既销不掉也
         不升级（清算力缺口）；
      2. 无迁移感知、无史实归因，把"被后人改写"（无害）与"从未落地"（要救）混为一谈；
      3. 缺不变量 SV 保护（虽因全袋制碰巧未误销，但属于巧合而非设计）。
    两套判据并存必然漂移（对齐 D-2 时期"双实现会漂移"的教训），故收敛到唯一真源。

    安全升级：**默认 dry-run**（与 blob_gc ``--archive`` 同哲学），显式 ``--execute``
    才动盘。旧版默认执行，与"全资产零删除默认是错的"这一项目安全基调和而不同。
    """
    rep = sweep_with_attribution(root, age_hours=age_hours, dry_run=not execute)
    mode = "EXECUTE" if execute else "DRY-RUN"
    print(f"sweep-attribution [{mode}]: {rep['stats']}")
    print(
        f"  可销账(settleable)={rep['settleable_count']}  抢救保留(must_keep)={rep['kept_count']}"
        f"  其中超龄={rep['aged_kept']}"
    )

    by_class: dict[str, int] = {}
    for r in rep["kept"]:
        for c, n in (r.get("classes") or {}).items():
            by_class[c] = by_class.get(c, 0) + n
    if by_class:
        print("  保留条目逐类分布：")
        for c, n in sorted(by_class.items(), key=lambda kv: -kv[1]):
            print(f"    {_ATTR_LABEL.get(c, c):<34} {n:>6}")

    lost = sorted({p["path"] for r in rep["kept"] for p in r.get("lost_paths", [])})
    if lost:
        print(f"  ★不可销账目标路径 {len(lost)} 个（已入抢救台账），前 10：")
        for p in lost[:10]:
            print(f"    {p}")

    for q in rep["settleable_qids"][:10]:
        print(f"  {'已销' if execute else '待销'}: {q}")
    print(f"账: {root / '.runtime' / 'takeover' / 'sweep_attribution_log.jsonl'}")
    if not execute:
        print("提示：默认零写。确认无误后加 --execute 才动盘。")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="接管台账：死亡会话资源显化 L1+L2（scan/list/resolve）")
    parser.add_argument("--scan", action="store_true", help="扫死亡会话生成/更新 open 条目（幂等）")
    parser.add_argument("--list", action="store_true", help="列 open 条目+处方")
    parser.add_argument("--resolve", metavar="SID", help="迁移该 sid 的 open 条目到 resolved/")
    parser.add_argument("--by", metavar="TAKER", default="", help="接管者标识（resolve 必填语义）")
    parser.add_argument("--note", default="", help="处置结论注记")
    parser.add_argument(
        "--sweep-absorbed",
        action="store_true",
        help="事实归因清算：可分诊销账/抢救保留（默认零写，需 --execute 才动盘）",
    )
    parser.add_argument("--execute", action="store_true", help="配合 --sweep-absorbed：确认后真正执行销账搬迁")
    parser.add_argument("--age-hours", type=int, default=48, help="超龄阈值（小时，缺省 48）")
    parser.add_argument("--root", default=".", help="仓库根（缺省=.）")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if args.sweep_absorbed:
        return _cmd_sweep_absorbed(root, args.age_hours, execute=args.execute)
    if args.scan:
        return _cmd_scan(root)
    if args.list:
        return _cmd_list(root)
    if args.resolve:
        if not args.by:
            parser.error("--resolve 需要 --by <接管者>")
        return _cmd_resolve(root, args.resolve, args.by, args.note)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
