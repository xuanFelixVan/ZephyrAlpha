# [BLUEPRINT] MOD-GOV_ENFORCEMENT | docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml | §coordination_state_board
# [MODULE] zephyr.gov_enforcement.rule_bridge.coordination_state_board
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.worktree_drift_watchdog (_git/_dirty_tracked/_active_sessions_and_claims); zephyr.security.access_control.session_concurrency (SessionRegistry); zephyr.shared.utils.time_utils (now_utc); zephyr.governance.audit.reconciliation_registry (ReconcileResult, ReconcilerSpec); scripts/governance/classify_workspace_wip.py (classify)
# [CONSUMERS] AI 会话一次读全并发面（施工公告牌）; reconciliation_registry _EXTERNAL_SPEC_MODULES（post-commit 刷新）; CLI
# [STARTUP] manual / post-commit reconciler
# [MATURITY] candidate
# [INVARIANTS] 只读扫描（零 git 写/零文件删/零 DB）；候选车道目录必经 show-toplevel 自证（向上解析者永不计为车道，杜绝主区 dirt 按车道数放大）；两车道脏清单指纹逐字节相同=红色旗标；新鲜度必带（本地+UTC 双钟 + 一致性自校 + 读取时年龄）；预算耗尽必标 truncated 不假称全覆盖；身份无桥即记 UNKNOWN 禁臆造；云/他机不可观测面必列盲区不得报净单
# [MODIFY-GUARD] 车道验证判据（show-toplevel 规范化相等）与旗标词表 UPWARD_RESOLUTION*/EQUAL_COUNT_COINCIDENCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] git/registry/classifier 不可达→对应分节降级 {unavailable, reason} 并继续（公告牌永不抛）；异常消息禁插路径，细节走 details 面
# [TESTS] tests/governance/test_coordination_state_board.py
# [A_module] module_id=MOD-GOV_ENFORCEMENT | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""coordination_state_board.py — 施工公告牌（并发态单一快照，st-p11-board）。

一次调用回答五问：谁活着 / 谁 claim 了哪些文件 / 哪些文件**只改不提交**（主区+每条车道）/
队列在飞什么 / 这份快照有多旧。外加 B4 身份桥与 B5 自动化普查（含显式盲区）。

净零定位（AGENTS §4）：本件**不新增扫描器**——
  · 脏文件语义判读 = 复用 scripts/governance/classify_workspace_wip.classify()
  · porcelain/git 原语 = 复用 worktree_drift_watchdog._git/_dirty_tracked
  · 归属（活跃会话+claim） = 复用 worktree_drift_watchdog._active_sessions_and_claims
  · 活性判据 = 复用 SessionRegistry.list_active()（本件零重定义，B3 是他道）
它替代的是"人肉三段式"（git status + commit_queue status + 手抄 session_registry），
并把 AGENTS §9.5"静态清单禁手工维护"落到一个生成物上。

实测成本（见 docs/_working/three_piece_infra/visibility_board/CASE.md verified 11）：
102–105 个在册 worktree 全量 39.9–50.6 s（≈350–480 ms/车道；优化前 67.4 s——枚举面由
3 次子进程/车道降为 1 次，toplevel 自证那一次不可省），故新鲜度界由 --budget-seconds 强制，
超预算必 truncated=True，不报假全量。post-commit 形态另有更紧的界（20 车道/12 s）。

Usage::

    python -m zephyr.gov_enforcement.rule_bridge.coordination_state_board            # 生成+打印
    python -m zephyr.gov_enforcement.rule_bridge.coordination_state_board --fast     # 免判读快扫
    python -m zephyr.gov_enforcement.rule_bridge.coordination_state_board --print-md # 只打人读页
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import logging
import os
import subprocess  # noqa: S404 — 只读白名单命令（git 经 watchdog._git，schtasks 见 _run_readonly）
import sys
from datetime import datetime
from pathlib import Path
from typing import Final

import yaml

from zephyr.gov_enforcement.rule_bridge.worktree_drift_watchdog import (
    _active_sessions_and_claims,
    _dirty_tracked,
    _git,
)
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

__all__: Final[list[str]] = [
    "list_worktrees",
    "scan_lane",
    "collect_sessions",
    "collect_claims",
    "collect_queue",
    "collect_automation",
    "build_board",
    "render_markdown",
    "write_board",
    "load_board",
    "freshness_of",
    "session_ids_of",
    "main",
]

#: 公告牌机读产物规范路径（docs/_working 禁 .json ⇒ yaml）
BOARD_YAML_REL: Final[str] = "docs/_working/three_piece_infra/visibility_board/board.yaml"
BOARD_MD_REL: Final[str] = "docs/_working/three_piece_infra/visibility_board/BOARD.md"
#: 新鲜度界（秒）：超过即 stale——读数者必须重取或自行扫描
DEFAULT_STALE_AFTER_SECONDS: Final[int] = 600
#: 单次构建预算（秒）：实测全量 49.6 s，留判读余量
DEFAULT_BUDGET_SECONDS: Final[int] = 120
#: 判读（classify）车道上限——按脏量降序取用，其余只给计数
DEFAULT_CLASSIFY_TOP_N: Final[int] = 8
#: 每车道展示的脏文件上限（防产物膨胀；计数不受此限）
_FILE_DISPLAY_CAP: Final[int] = 20

_CLASSIFIER_REL: Final[str] = "scripts/governance/classify_workspace_wip.py"
_QUEUE_STATES: Final[tuple[str, ...]] = ("pending", "processing", "done", "dead")
_SCANNER_CMD: Final[str] = (
    "python -m zephyr.gov_enforcement.rule_bridge.coordination_state_board"
)
#: post-commit 刷新只盯施工面（防每 commit 全量重扫拖慢提交：实测全量 44-67 s）
_REFRESH_PREFIXES: Final[tuple[str, ...]] = (
    "src/", "scripts/", "docs/01_policies_and_standards/_registry/",
)
#: post-commit 形态的有界扫描预算（成本上限，超界即 truncated=True 如实报）
_RECONCILE_BUDGET_SECONDS: Final[int] = 12
_RECONCILE_MAX_WORKTREES: Final[int] = 20
#: 候选车道目录扫描面（在册 `git worktree list` 会漏注册的沙盒，故逐目录补扫并自证 toplevel）
_CANDIDATE_MARKERS: Final[tuple[str, ...]] = (".worktrees", ".aidrafts", ".qoder/worktrees")
#: 本地计划任务名前缀（B5 普查过滤键）
_TASK_PREFIXES: Final[tuple[str, ...]] = ("ZephyrAlpha", "ZEPHYR", "zephyr")
_UNOBSERVABLE: Final[list[dict]] = [
    {
        "kind": "cloud_side_agent_task",
        "observable": False,
        "why": "云端/调度平台侧任务在本地无任何落盘凭据——无 API 可读，只能由 Owner 侧导出",
        "consequence": "并发包工头数量只能给下界，不能给等号",
    },
    {
        "kind": "other_machine_runner",
        "observable": False,
        "why": "本仓 worktree 列表与 session registry 均为单机态，异机会话不出现",
        "consequence": "board.worktrees 是本机视图，非全宇宙视图",
    },
    {
        "kind": "windows_task_other_user",
        "observable": False,
        "why": "schtasks 以当前用户令牌查询，SYSTEM/他人上下文注册的任务不可见",
        "consequence": "automation.scheduled_tasks 是可见集非全集",
    },
    {
        "kind": "logical_session_without_heartbeat",
        "observable": "partial",
        "why": "pid=0 逻辑会话靠 heartbeat 新鲜度判活（判据真源=SessionRegistry，B3 面，本件只读）",
        "consequence": "心跳说谎则 live 集说谎——本件以 registry_dead_dirs 差值暴露异常量级",
    },
    {
        "kind": "unregistered_sandbox_outside_markers",
        "observable": "partial",
        "why": "车道枚举=git worktree list ∪ 候选目录 toplevel 自证（_CANDIDATE_MARKERS 三处）；"
               "放在 .runtime/tmp 等处的临时沙盒不在扫描面，异机盘更不可见",
        "consequence": "worktrees.lanes 是本机已登记面的并集，仍非全集 ⇒ 并发数只能取下界",
    },
]


def _now_pair() -> dict:
    """本地+UTC 双钟读数与自校（混合钟事故防线）。"""
    utc = now_utc()
    local = utc.astimezone()
    offset = int(local.utcoffset().total_seconds()) if local.utcoffset() else 0
    tzname = local.tzname() or "UNKNOWN"
    # 自校：两钟指向同一瞬间（timestamp() 已含时区，差值应为 0；秒级容差 2s）
    delta = abs(local.timestamp() - utc.timestamp())
    return {
        "generated_at_utc": utc.isoformat(),
        "generated_at_local": local.isoformat(),
        "utc_offset_seconds": offset,
        "tz_name_local": tzname,
        "epoch_seconds": round(utc.timestamp(), 3),
        "clock_consistency": "OK" if delta <= 2 else f"MISMATCH_{delta:.1f}s",
        "produced_by": "zephyr.shared.utils.time_utils.now_utc() + datetime.astimezone()",
    }


def _norm(p: str | Path) -> str:
    """比较用规范化键（大小写折叠 + 正斜杠 + 去尾斜杠 + 去 git stdout 换行）。"""
    s = os.path.normcase(str(p).strip())
    return s.replace("\\", "/").rstrip("/")


def _disp(p: str | Path) -> str:
    """展示用路径（保留原始大小写，统一正斜杠）。"""
    return str(p).strip().replace("\\", "/").rstrip("/")


def _fingerprint(paths: list[str]) -> str:
    return hashlib.sha256("\n".join(sorted(paths)).encode("utf-8")).hexdigest()[:12]


def _decode_console(raw: bytes) -> str:
    """控制台输出解码：中文 Windows 的 schtasks 是 GBK 码页，UTF-8 直读会撕裂。

    实测（本道）：`text=True` + UTF-8 读 schtasks → reader 线程 UnicodeDecodeError
    → stdout 静默为空 → 计划任务普查假报 0 条（"看着干净其实是没看见"）。
    """
    for enc in ("utf-8", "gbk", "cp936"):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("latin-1", errors="replace")


def _run_readonly(argv: list[str], timeout: int = 60) -> tuple[int, str]:
    """只读外部命令（fail-open：异常返回 (2, '')，消息不含路径）。"""
    try:
        r = subprocess.run(  # noqa: S603 — 固定 argv 白名单，无用户输入拼接
            argv, capture_output=True, timeout=timeout,
        )
        return r.returncode, _decode_console(r.stdout or b"")
    except (subprocess.TimeoutExpired, OSError):
        return 2, ""


_classifier_mod: object | None = None


def _classifier():
    """进程内装载既有判读器（不重写第二套分类法）。失败返回 None。"""
    global _classifier_mod
    if _classifier_mod is not None:
        return _classifier_mod
    try:
        root = Path(__file__).resolve()
        for up in root.parents:
            cand = up / "scripts" / "governance" / "classify_workspace_wip.py"
            if cand.is_file():
                # 该脚本以 CLI 形态运行（sys.path[0]=scripts/governance），进程内装载
                # 须补该路径，否则其 `from _shared.thresholds import ...` 断链
                gov_dir = str(cand.parent)
                if gov_dir not in sys.path:
                    sys.path.insert(0, gov_dir)
                spec = importlib.util.spec_from_file_location("_cwb_classifier", cand)
                mod = importlib.util.module_from_spec(spec)  # noqa: S603 — 仓内既有脚本
                sys.modules["_cwb_classifier"] = mod
                spec.loader.exec_module(mod)  # type: ignore[union-attr]
                _classifier_mod = mod
                return mod
    except Exception as exc:  # noqa: BLE001 — 判读器不可达降级快扫
        logger.warning("classifier 装载失败（降级快扫）: %s: %s",
                       type(exc).__name__, exc)
    return None


# ── 车道枚举（陷阱防线）────────────────────────────────────────────────────────


def _parse_worktree_list(out: str) -> dict[str, dict]:
    """`git worktree list --porcelain` → {path: {head, branch}}（省每车道 2 次子进程）。"""
    registered: dict[str, dict] = {}
    cur: str | None = None
    for line in out.splitlines():
        if line.startswith("worktree "):
            cur = line.split(" ", 1)[1].strip().strip('"')
            registered[cur] = {}
        elif not cur:
            continue
        elif line.startswith("HEAD "):
            registered[cur]["head"] = line.split(" ", 1)[1].strip()[:8]
        elif line.startswith("branch "):
            registered[cur]["branch"] = line.split(" ", 1)[1].strip().replace(
                "refs/heads/", "")
        elif line.startswith("detached"):
            registered[cur]["branch"] = "DETACHED"
    return registered


def list_worktrees(main_root: Path) -> tuple[list[dict], list[dict]]:
    """枚举真实 worktree，逐条以 show-toplevel 自证。

    返回 (lanes, rejected)。rejected 记录候选目录向上解析到主仓的情形——
    这正是"主区 dirt 被按车道数重复计数"的事故形态（实测 25/73 候选命中）。
    在册项的 branch/head 直接从 `worktree list --porcelain` 取，
    但 toplevel 自证一次不可省（它就是陷阱防线）。
    """
    _rc, out = _git(main_root, ["worktree", "list", "--porcelain"])
    registered = _parse_worktree_list(out or "")
    main_norm = _norm(main_root)
    lanes: list[dict] = []
    rejected: list[dict] = []

    def _probe(path: str, *, source: str, known: dict | None = None) -> None:
        disp = _disp(path)
        known = known or {}
        if not os.path.isdir(path):
            rejected.append({"path": disp, "reason": "DIR_MISSING", "source": source})
            return
        rc_t, top = _git(Path(path), ["rev-parse", "--show-toplevel"])
        top_norm = _norm(top or "")
        if rc_t != 0 or not top_norm:
            rejected.append({"path": disp, "reason": "NOT_A_GIT_WORKTREE", "source": source})
            return
        if top_norm != _norm(path):
            rejected.append({
                "path": disp, "reason": "UPWARD_RESOLUTION", "source": source,
                "resolves_to": top_norm,
                "meaning": "该目录不是独立 worktree——git 向上解析到父仓，"
                           "对它跑 status 会把父仓 dirt 当作本车道 dirt 重复计数",
            })
            return
        is_main = top_norm == main_norm
        lanes.append({
            "path": disp,
            "lane": "main" if is_main else Path(disp).name,
            "role": "main_worktree" if is_main else "lane",
            "branch": known.get("branch", "UNKNOWN"),
            "head": known.get("head", "UNKNOWN"),
            "registered_in_git_worktree_list": source == "worktree_list",
            "toplevel_verified": True,
        })

    for p, known in registered.items():
        _probe(p, source="worktree_list", known=known)
    reg_norm = {_norm(p) for p in registered}
    for marker in _CANDIDATE_MARKERS:
        base = main_root / marker
        if not base.is_dir():
            continue
        for cand in sorted(p for p in base.iterdir() if p.is_dir()):
            if _norm(cand) in reg_norm:
                continue
            _probe(str(cand), source=f"candidate_dir:{marker}")
    return lanes, rejected


def scan_lane(root: Path, lane: dict, *, classify_mod=None) -> dict:
    """单车道扫描：脏文件（未提交改动）计数 + 清单 + 可选语义判读。"""
    root = Path(root)
    rc, out = _git(root, ["status", "--porcelain=v1", "--untracked-files=all"])
    if rc != 0:
        return {**lane, "status": "GIT_UNAVAILABLE"}
    dirty: list[str] = []
    untracked: list[str] = []
    staged: list[str] = []
    for line in out.splitlines():
        if len(line) < 4:
            continue
        xy = line[:2]
        path = line[3:].split(" -> ", 1)[1] if " -> " in line[3:] else line[3:]
        path = path.strip().strip('"').replace("\\", "/")
        dirty.append(path)
        if xy == "??":
            untracked.append(path)
        elif xy[0] != " ":
            staged.append(path)
    tracked_mods = _dirty_tracked(root)
    entry = {
        **lane,
        "status": "ok",
        "dirty_total": len(dirty),
        "untracked": len(untracked),
        "tracked_or_index": len(dirty) - len(untracked),
        "staged_count": len(staged),
        "dirty_paths_sample": dirty[:_FILE_DISPLAY_CAP],
        "dirty_fingerprint": _fingerprint(dirty),
        "tracked_modifications_total": len(tracked_mods),
        "tracked_modifications_sample": tracked_mods[:_FILE_DISPLAY_CAP],
        "produced_by": "git -C <lane> status --porcelain=v1 --untracked-files=all"
                       " + worktree_drift_watchdog._dirty_tracked()",
    }
    if classify_mod is not None:
        entry["attribution"] = _attribute(classify_mod, root)
    return entry


def _attribute(classify_mod, root: Path) -> dict:
    """既有判读器的分类结果原样入册（零新分类法）。"""
    try:
        res = classify_mod.classify(root)  # type: ignore[attr-defined]
        cats = res.get("categories") or {}
        return {
            "available": True,
            "categories": {k: len(v) for k, v in cats.items()},
            "needs_attention": res.get("needs_attention"),
            "conclusion": res.get("conclusion"),
            "head": res.get("head"),
            "produced_by": "classify_workspace_wip.classify(<lane>)",
        }
    except Exception as exc:  # noqa: BLE001 — 判读降级不拖垮公告牌
        return {"available": False, "reason": f"CLASSIFIER_FAILED:{type(exc).__name__}"}


def _self_check(lanes: list[dict], rejected: list[dict]) -> dict:
    """红旗自检：两车道脏清单逐字节相同 ⇒ 向上解析 bug 发作；等数异集 ⇒ 仅记巧合。"""
    ok = [ln for ln in lanes if ln.get("status") == "ok"]
    by_key: dict[tuple[int, str], list[str]] = {}
    by_count: dict[int, list[dict]] = {}
    for ln in ok:
        n = int(ln.get("dirty_total") or 0)
        key = (n, str(ln.get("dirty_fingerprint")))
        by_key.setdefault(key, []).append(str(ln.get("path")))
        if n > 0:
            by_count.setdefault(n, []).append(ln)
    identical = [
        {
            "dirty_total": k[0], "dirty_fingerprint": k[1], "lanes": ps,
            "ancestor_geometry": _has_ancestor_pair(ps),
        }
        for k, ps in sorted(by_key.items(), key=lambda kv: -kv[0][0])
        if k[0] > 0 and len(ps) > 1
    ]
    coincidences = [
        {"dirty_total": n, "lanes": [str(x.get("path")) for x in rows]}
        for n, rows in sorted(by_count.items())
        if len(rows) > 1 and len({str(r.get("dirty_fingerprint")) for r in rows}) > 1
    ]
    geometry_hits = [g for g in identical if g["ancestor_geometry"]]
    return {
        "identical_dirty_groups": identical,
        "red_flag_upward_resolution": bool(geometry_hits),
        "upward_resolution_evidence": geometry_hits,
        "sibling_copy_suspects": [g for g in identical if not g["ancestor_geometry"]],
        "equal_count_different_content": coincidences[:10],
        "unverified_candidate_dirs_rejected": len(rejected),
        "rejected_reasons": _count_by(rejected, "reason"),
        "note": (
            "red_flag_upward_resolution 只在同脏清单两组车道呈父子目录几何（主区 dirt 被按车道"
            "重复计入的确证形态）时点亮；等计数但脏清单不同只记巧合；兄弟副本（同名不同目录、"
            "脏清单逐字相同但无父子关系）单列 sibling_copy_suspects 不报红"
        ),
        "produced_by": f"{_SCANNER_CMD} (internal _self_check)",
    }


def _has_ancestor_pair(paths: list[str]) -> bool:
    """同脏清单的目录里是否存在父子几何（向上解析事故的结构性证据）。"""
    normed = [_norm(p) for p in paths]
    return any(
        a != b and (b.startswith(a + "/") or a.startswith(b + "/"))
        for a in normed for b in normed
    )


def _count_by(rows: list[dict], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for r in rows:
        k = str(r.get(key, "UNKNOWN"))
        out[k] = out.get(k, 0) + 1
    return out


# ── 五个面 ────────────────────────────────────────────────────────────────────


def collect_sessions(main_root: Path) -> dict:
    """谁活着 + B4 身份桥（无桥即 UNKNOWN）。活性判据完全引用 SessionRegistry。"""
    live_ids: list[str] = []
    raw: dict[str, dict] = {}
    liveness_source = "UNAVAILABLE"
    try:
        from zephyr.security.access_control.session_concurrency import SessionRegistry

        reg = SessionRegistry(main_root)
        # 先取原始册再取活跃集：list_active() 自身会按 _REAP_GRACE_SECONDS 物理修剪，
        # 顺序反过来公告牌就永远看不见"刚死"的会话（实测宽限 900s / 判死 90s）
        raw = reg.load() or {}
        live_ids = [s.session_id for s in reg.list_active()]
        liveness_source = "SessionRegistry.list_active() (zephyr.security.access_control.session_concurrency)"
    except Exception as exc:  # noqa: BLE001 — registry 故障降级空集
        logger.warning("session registry 不可达: %s", type(exc).__name__)

    live = set(live_ids)
    sessions: list[dict] = []
    for sid, d in sorted(raw.items()):
        hb = _last_heartbeat(main_root / ".runtime" / "sessions" / sid / "heartbeat.jsonl")
        sessions.append({
            "session_id": sid,
            "live": sid in live,
            "pid_registry": d.get("pid"),
            "pid_heartbeat_file": hb.get("pid"),
            "heartbeat_age_seconds": hb.get("age_s"),
            "last_activity_age_seconds": _age_s(d.get("last_activity")),
            "held_files": len(d.get("held_files") or []),
            "task_files": len(d.get("task_files") or []),
            "depends_on_sessions": len(d.get("depends_on_sessions") or []),
            "lane_dir_exists": (main_root / ".worktrees" / str(sid)).is_dir(),
            "conversation_id": "UNKNOWN",
            "identity_bridge_source": "NONE_IN_REPOSITORY",
        })
    hb_dirs = _subdir_names(main_root / ".runtime" / "sessions")
    window = _dead_visible_window()
    return {
        "live_session_ids": sorted(live),
        "live_count": len(live_ids),
        "registered_count": len(raw),
        "registry_dead_count": len(set(raw) - live),
        "dead_visible_window_seconds": window,
        "dead_window_note": (
            "注册表按判死阈值+物理修剪宽限双窗自清：仅心跳年龄落在该窗内的死者仍在册，"
            "超窗即消失 ⇒ registry_dead_count 是下界，不是死讯全集"
        ),
        "sessions": sessions,
        "counters_floor": {
            "registry_sessions": len(raw),
            "heartbeat_dirs": len(hb_dirs),
            "live_sessions": len(live_ids),
            "note": "并发包工头数量只能取下界：三个数互不相等即说明在册态与活动态不同源",
        },
        "identity_mapping_note": (
            "Qoder 对话身份与 st-* 会话号之间无机器可读桥（SessionInfo 无对话字段、"
            "heartbeat.jsonl 仅 ts/pid/status）——conversation_id 恒 UNKNOWN，禁臆造映射"
        ),
        "produced_by": "python -c \"from zephyr.security.access_control.session_concurrency "
                       "import SessionRegistry as R; print([s.session_id for s in R('.').list_active()])\"",
        "liveness_judgement_source": liveness_source,
    }


def _dead_visible_window() -> dict:
    """引用 SessionRegistry 的判死/修剪常量（不硬编码他道真源数值）。"""
    out = {"judge_dead_after": None, "physically_reaped_after": None, "source": "UNAVAILABLE"}
    try:
        from zephyr.security.access_control import session_concurrency as sc

        out["judge_dead_after"] = getattr(sc, "_HEARTBEAT_TIMEOUT_SECONDS", None)
        out["physically_reaped_after"] = getattr(sc, "_REAP_GRACE_SECONDS", None)
        out["source"] = "zephyr.security.access_control.session_concurrency 常量（只读引用）"
    except Exception as exc:  # noqa: BLE001 — 常量面不可达只降级为 null
        logger.warning("registry 窗口常量不可读: %s", type(exc).__name__)
    return out


def _last_heartbeat(path: Path) -> dict:
    if not path.is_file():
        return {"pid": None, "age_s": None}
    try:
        lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        rec = json.loads(lines[-1])
        ts = datetime.fromisoformat(str(rec.get("ts")))
        age = (now_utc() - ts).total_seconds() if ts.tzinfo else None
        return {"pid": rec.get("pid"), "age_s": round(age, 1) if age is not None else None}
    except Exception:  # noqa: BLE001 — 心跳面异常只报告不可读
        return {"pid": None, "age_s": None}


def _age_s(epoch: object) -> float | None:
    try:
        return round(now_utc().timestamp() - float(epoch), 1)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def collect_claims(main_root: Path) -> dict:
    """谁 claim 了什么（三册并列：claim 快照 / 死会话残留快照 / .ailocks）。"""
    sessions, claimed = _active_sessions_and_claims(main_root)
    snap_dir = main_root / ".runtime" / "claim_snapshots"
    all_snaps: list[dict] = []
    if snap_dir.is_dir():
        live = set(sessions)
        for snap in sorted(snap_dir.glob("*.json")):
            sid = snap.stem
            try:
                data = json.loads(snap.read_text(encoding="utf-8"))
                n = len(data.get("files") or data.get("snapshots") or {})
            except Exception:  # noqa: BLE001
                n = -1
            all_snaps.append({
                "session_id": sid, "files": n, "live": sid in live,
                "age_seconds": _age_s(snap.stat().st_mtime),
            })
    locks = 0
    lock_path = main_root / ".ailocks" / "registry.json"
    if lock_path.is_file():
        try:
            locks = len(json.loads(lock_path.read_text(encoding="utf-8")).get("locks") or {})
        except Exception:  # noqa: BLE001
            locks = -1
    per_session: dict[str, int] = {}
    for sid in claimed.values():
        per_session[sid] = per_session.get(sid, 0) + 1
    return {
        "active_sessions": sessions,
        "claimed_files_total": len(claimed),
        "claimed_files_by_session": per_session,
        "claim_snapshot_files": all_snaps,
        "stale_claim_snapshots": [x for x in all_snaps if not x["live"]],
        "ailocks_registry_locks": locks,
        "note": (
            "claim 只在提交时被要求 ⇒ 只改文件不提交者在此三册零痕迹（B1）。"
            "本件以 dirty 清单补该空缺，不以 claim 册判存在性"
        ),
        "produced_by": "worktree_drift_watchdog._active_sessions_and_claims()"
                       " + .runtime/claim_snapshots/*.json + .ailocks/registry.json",
    }


def collect_queue(main_root: Path) -> dict:
    """队列在飞什么（四态 + 每袋 session_id + dead_reason 汇总）。"""
    qroot = main_root / ".runtime" / "commit_queue"
    states = {}
    inflight: list[dict] = []
    for state in _QUEUE_STATES:
        d = qroot / state
        files = sorted(d.rglob("*.json")) if d.is_dir() else []
        top = [f for f in files if f.parent != d]
        states[state] = {"items": len(files), "nested": len(top)}
        if state in ("pending", "processing"):
            for f in files[:60]:
                try:
                    item = json.loads(f.read_text(encoding="utf-8"))
                except Exception:  # noqa: BLE001
                    continue
                inflight.append({
                    "state": state,
                    "qid": item.get("qid", f.stem),
                    "session_id": item.get("session_id", "UNKNOWN"),
                    "created_at": item.get("created_at"),
                    "files": len(item.get("files") or []),
                    "base_head": str(item.get("base_head", ""))[:8],
                    "worktree_root": str((item.get("meta") or {}).get("worktree_root")),
                    "nested_stale": f.parent != d,
                })
    dead_reasons: dict[str, int] = {}
    for f in (qroot / "dead").glob("*.json") if (qroot / "dead").is_dir() else []:
        try:
            reason = str(json.loads(f.read_text(encoding="utf-8")).get("dead_reason", ""))[:60]
        except Exception:  # noqa: BLE001
            reason = "UNREADABLE"
        dead_reasons[reason] = dead_reasons.get(reason, 0) + 1
    return {
        "root": ".runtime/commit_queue",
        "states": states,
        "in_flight": inflight,
        "in_flight_by_session": _count_by(inflight, "session_id"),
        "dead_reason_top": dict(sorted(dead_reasons.items(), key=lambda kv: -kv[1])[:10]),
        "retired_dirs": [p.name for p in sorted(qroot.iterdir())
                         if p.is_dir() and p.name.startswith("dead_archive")][:20]
                         if qroot.is_dir() else [],
        "produced_by": "find .runtime/commit_queue/<state> -type f -name '*.json'（计数用 find，"
                       "禁 ls | wc -l）",
    }


def collect_automation(main_root: Path, *, skip_schtasks: bool = False) -> dict:
    """B5 自动化普查：本地计划任务 + 仓内登记者 + 不可观测面（显式盲区）。"""
    tasks: list[dict] = []
    total_tasks = 0
    query_status = "SKIPPED"
    if not skip_schtasks:
        rc, out = _run_readonly(["schtasks", "/query", "/fo", "CSV", "/nh"])
        query_status = "OK" if rc == 0 else "FAILED_OR_DENIED"
        for line in out.splitlines():
            if not line.strip():
                continue
            total_tasks += 1
            cols = [c.strip().strip('"') for c in line.split('","')]
            name = (cols[0] if cols else "").lstrip("\\/")
            if name.startswith(_TASK_PREFIXES):
                tasks.append({
                    "task_name": name,
                    "next_run_time": cols[1] if len(cols) > 1 else None,
                    "status": cols[2] if len(cols) > 2 else None,
                })
    registrars = sorted(p.name for p in (main_root / "scripts").glob("register_*task*.ps1"))
    keep_file = main_root / "data" / "runtime" / "process_reaper_keep.txt"
    keep = [ln.strip() for ln in keep_file.read_text(encoding="utf-8").splitlines()
            if ln.strip()] if keep_file.is_file() else []
    return {
        "local_scheduled_tasks": {
            "count": len(tasks),
            "total_tasks_in_window": total_tasks,
            "filter_prefixes": list(_TASK_PREFIXES),
            "query_status": query_status,
            "items": tasks[:80],
            "produced_by": "schtasks /query /fo CSV /nh | 前缀过滤",
        },
        "repo_registered_task_installers": {
            "count": len(registrars), "items": registrars,
            "produced_by": "ls scripts/register_*task*.ps1（脚本名=登记入口，非运行证据）",
        },
        "reaper_keep_allowlist": {
            "count": len(keep), "items": keep[:80],
            "produced_by": "find data/runtime -maxdepth 1 -name process_reaper_keep.txt",
        },
        "blind_spots": _UNOBSERVABLE,
        "honest_statement": (
            "本表可观测集=本机当前用户可见计划任务 + 仓内登记脚本；"
            "计数与可见清单均不构成全量——报'干净清单'即错"
        ),
    }


def _subdir_names(d: Path) -> list[str]:
    if not d.is_dir():
        return []
    return sorted(p.name for p in d.iterdir() if p.is_dir())


# ── 组装 ──────────────────────────────────────────────────────────────────────


def _scan_all(
    lanes: list[dict], started: float, budget_seconds: int, max_worktrees: int
) -> tuple[list[dict], bool]:
    """逐车道扫描，超预算或超上限即停并如实报未覆盖（绝不假称全量）。"""
    scanned: list[dict] = []
    stopped = False
    limit = max_worktrees or len(lanes)
    for lane in lanes[:limit]:
        if max_worktrees and len(scanned) >= limit:
            stopped = True
            break
        if scanned and now_utc().timestamp() - started > budget_seconds:
            stopped = True
            break
        scanned.append(scan_lane(Path(lane["path"]), lane))
    if len(lanes) > limit:
        stopped = True
    return scanned, stopped


def build_board(
    main_root: Path | str | None = None,
    *,
    budget_seconds: int = DEFAULT_BUDGET_SECONDS,
    classify_top_n: int = DEFAULT_CLASSIFY_TOP_N,
    stale_after_seconds: int = DEFAULT_STALE_AFTER_SECONDS,
    max_worktrees: int = 0,
    fast: bool = False,
    skip_schtasks: bool = False,
) -> dict:
    """一次调用产出全并发态快照（预算耗尽即 truncated，绝不假称全覆盖）。"""
    started = now_utc().timestamp()
    main = Path(main_root) if main_root else Path.cwd()
    lanes, rejected = list_worktrees(main)
    mod = None if fast else _classifier()
    scanned, scan_stopped = _scan_all(lanes, started, budget_seconds, max_worktrees)
    elapsed = now_utc().timestamp() - started
    scanned.sort(key=lambda x: -int(x.get("dirty_total") or 0))
    attributed = 0
    if mod is not None:
        for lane in scanned:
            if elapsed > budget_seconds or attributed >= classify_top_n:
                break
            lane["attribution"] = _attribute(mod, Path(lane["path"]))
            attributed += 1
            elapsed = now_utc().timestamp() - started
    truncated = scan_stopped or elapsed > budget_seconds
    main_head = next((l.get("head") for l in scanned if l.get("role") == "main_worktree"), "UNKNOWN")
    per_ms = round((now_utc().timestamp() - started) * 1000 / max(1, len(scanned)), 1)
    sessions = collect_sessions(main)
    claims = collect_claims(main)
    return {
        "schema": "coordination_state_board/1",
        **_now_pair(),
        "stale_after_seconds": stale_after_seconds,
        "scanner": {"module": __name__, "command": _SCANNER_CMD},
        "main_root": _norm(main),
        "measured": {
            "build_seconds": round(now_utc().timestamp() - started, 2),
            "worktrees_scanned": len(scanned),
            "worktrees_discovered": len(lanes),
            "worktrees_limit": max_worktrees or "unlimited",
            "per_worktree_ms": per_ms,
            "budget_seconds": budget_seconds,
            "truncated": truncated,
            "attribution_coverage": {"attributed_lanes": attributed, "total_lanes": len(scanned),
                                     "cap": classify_top_n,
                                     "partial": mod is not None and attributed < len(scanned)},
            "freshness_bound_note": "实测 39.9–50.6 s / 102–105 车道（fleet 在涨）⇒ 新鲜度界取 "
                                     "stale_after_seconds；读取时超界必须重扫，不得据旧板决策",
        },
        "worktrees": {
            "main_head": main_head,
            "lanes": scanned,
            "unverified_candidate_dirs": rejected,
            "self_check": _self_check(scanned, rejected),
            "produced_by": "git -C <root> worktree list --porcelain + 逐条 "
                           "git -C <dir> rev-parse --show-toplevel 自证",
        },
        "sessions": sessions,
        "claims": claims,
        "queue": collect_queue(main),
        "automation": collect_automation(main, skip_schtasks=skip_schtasks),
        "answers": _answers(scanned, rejected, sessions),
    }


def _answers(lanes: list[dict], rejected: list[dict], sessions: dict) -> dict:
    """公告牌存在的理由：五问的直接答案。"""
    ok = [l for l in lanes if l.get("status") == "ok"]
    edited_no_commit = [
        {
            "lane": l.get("lane"), "path": l.get("path"), "dirty_total": l.get("dirty_total"),
            "untracked": l.get("untracked"),
            "sample": l.get("dirty_paths_sample", [])[:12],
            "attribution": (l.get("attribution") or {}).get("categories"),
        }
        for l in ok if int(l.get("dirty_total") or 0) > 0
    ]
    dirty_lanes = [l for l in edited_no_commit if l.get("role") != "main"]
    return {
        "who_is_live": {
            "count": sessions.get("live_count"),
            "ids": sessions.get("live_session_ids"),
            "detail": "sessions.live_session_ids（活性判据真源=SessionRegistry）",
        },
        "uncommitted_edits_lanes": len(edited_no_commit),
        "uncommitted_edits_lane_count": len(dirty_lanes),
        "uncommitted_edits_total_files": sum(int(l.get("dirty_total") or 0) for l in ok),
        "uncommitted_edit_lanes": edited_no_commit[:60],
        "rejected_candidate_dirs": len(rejected),
        "produced_by": f"{_SCANNER_CMD} (internal _answers)",
    }


def session_ids_of(board: dict) -> set[str]:
    """公告牌 session 集（与注册表活跃集等值性判据的取数口）。"""
    return set((board.get("sessions") or {}).get("live_session_ids") or [])


def freshness_of(board: dict, *, now: datetime | None = None) -> dict:
    """读取时刻的新鲜度判定（年龄来自 UTC epoch，不看本地钟）。"""
    ref = now or now_utc()
    epoch = board.get("epoch_seconds")
    ts = board.get("generated_at_utc")
    try:
        base = float(epoch) if epoch is not None else datetime.fromisoformat(str(ts)).timestamp()
    except (TypeError, ValueError):
        return {"stale": True, "reason": "UNPARSEABLE_generated_at", "age_seconds": None}
    age = round(ref.timestamp() - base, 1)
    bound = int(board.get("stale_after_seconds") or DEFAULT_STALE_AFTER_SECONDS)
    return {
        "age_seconds": age,
        "stale_after_seconds": bound,
        "stale": age > bound,
        "verdict": "STALE_RESCAN_REQUIRED" if age > bound else "FRESH",
        "produced_by": f"{_SCANNER_CMD} --show-freshness",
    }


def load_board(path: Path | str) -> dict:
    """读板 + 新鲜度标注（机读产物是 YAML，PyYAML 为仓级既有依赖）。"""
    board = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    board["_freshness"] = freshness_of(board)
    return board


def _dump_yaml(obj: object) -> str:
    """确定性 YAML 序列化（键序=插入序，禁 sort_keys 以免产物抖动）。"""
    return yaml.safe_dump(obj, allow_unicode=True, sort_keys=False, default_flow_style=False)


def _md_header(board: dict) -> list[str]:
    m = board.get("measured") or {}
    return [
        "# 施工公告牌（coordination state board）",
        "",
        f"- 生成 UTC：`{board.get('generated_at_utc')}` / 本地：`{board.get('generated_at_local')}`"
        f"（偏移 {board.get('utc_offset_seconds')}s，钟一致性 {board.get('clock_consistency')}）",
        f"- 新鲜度界：{board.get('stale_after_seconds')}s；构建耗时 {m.get('build_seconds')}s"
        f"（{m.get('per_worktree_ms')} ms/车道）；truncated={m.get('truncated')}；"
        f"判读覆盖 {m.get('attribution_coverage')} ",
        f"- 取数命令：`{board.get('scanner', {}).get('command')}`",
    ]


def _md_people(board: dict) -> list[str]:
    s = board.get("sessions") or {}
    c = s.get("counters_floor") or {}
    claims = board.get("claims") or {}
    lines = [
        "",
        "## 一、谁活着",
        f"- 活跃会话 {s.get('live_count')}／注册表 {s.get('registered_count')}"
        f"／注册表判死 {s.get('registry_dead_count')}（宽限窗见 dead_visible_window_seconds）",
        f"- 活跃清单：{s.get('live_session_ids')}",
        f"- 下界三数：registry_sessions={c.get('registry_sessions')} heartbeat_dirs="
        f"{c.get('heartbeat_dirs')} live={c.get('live_sessions')} ——不等即不同源",
        "- 对话身份桥：`UNKNOWN`（无机器可读源，见 sessions.identity_mapping_note；禁臆造映射）",
        "",
        "## 二、谁 claim 了什么",
    ]
    for sid, n in sorted((claims.get("claimed_files_by_session") or {}).items()):
        lines.append(f"- `{sid}` claim {n} 个文件")
    lines.append(
        f"- claim 快照总数 {len(claims.get('claim_snapshot_files') or [])}"
        f"，其中死会话残留 {len(claims.get('stale_claim_snapshots') or [])}"
        f"；.ailocks 在册锁 {claims.get('ailocks_registry_locks')}",
    )
    return lines


def _md_uncommitted(board: dict) -> list[str]:
    a = board.get("answers") or {}
    w = board.get("worktrees") or {}
    sc = w.get("self_check") or {}
    lines = [
        "",
        "## 三、只改不提交（主区 + 每条车道，按脏量降序）",
    ]
    for lane in (a.get("uncommitted_edit_lanes") or [])[:25]:
        lines.append(
            f"- `{lane.get('lane')}` dirty={lane.get('dirty_total')} "
            f"untracked={lane.get('untracked')} 判读={lane.get('attribution')}"
        )
    lines += [
        f"- 未提交面合计 {a.get('uncommitted_edits_total_files')} 件，"
        f"散在 {a.get('uncommitted_edits_lanes')} 条 worktree（含主区）"
        f"／其中车道 {a.get('uncommitted_edits_lane_count')} 条",
        f"- 陷阱自检：red_flag_upward_resolution={sc.get('red_flag_upward_resolution')}"
        f"（同脏清单组 {len(sc.get('identical_dirty_groups') or [])}，"
        f"父子几何 {len(sc.get('upward_resolution_evidence') or [])}，"
        f"兄弟副本 {len(sc.get('sibling_copy_suspects') or [])}），"
        f"被剔除候选目录 {sc.get('unverified_candidate_dirs_rejected')} 个"
        f"（{sc.get('rejected_reasons')}）",
    ]
    return lines


def _md_queue_automation(board: dict) -> list[str]:
    q = board.get("queue") or {}
    auto = board.get("automation") or {}
    lts = auto.get("local_scheduled_tasks") or {}
    lines = ["", "## 四、队列在飞"]
    for st, info in sorted((q.get("states") or {}).items()):
        lines.append(f"- {st}: {info.get('items')} 件（嵌套 {info.get('nested')}）")
    lines.append(f"- 在飞袋按会话：{q.get('in_flight_by_session')}")
    lines.append(f"- dead 成因前列：{q.get('dead_reason_top')}")
    lines += [
        "",
        "## 五、自动化普查与盲区",
        f"- 本地可见计划任务：{lts.get('count')}（查询态 {lts.get('query_status')}，"
        f"窗口内总任务 {lts.get('total_tasks_in_window')}）",
        f"- 仓内登记脚本：{(auto.get('repo_registered_task_installers') or {}).get('count')}；"
        f"reaper 放行条目：{(auto.get('reaper_keep_allowlist') or {}).get('count')}",
        f"- 不可观测：{len(auto.get('blind_spots') or [])} 类——"
        + "；".join(b.get("kind", "?") for b in (auto.get("blind_spots") or [])),
        f"- {auto.get('honest_statement')}",
    ]
    return lines


def render_markdown(board: dict) -> str:
    """一页人读渲染（同源同数，禁第二套取数）。带 docs/_working 必需 frontmatter。"""
    lines = [
        "---",
        "ttl: task_bound",
        "completes_when: 公告牌生成物随下次刷新覆盖且新鲜度界内可读",
        "---",
        "",
    ] + _md_header(board) + _md_people(board) + _md_uncommitted(board) \
        + _md_queue_automation(board)
    return "\n".join(lines) + "\n"


def write_board(board: dict, out_dir: Path | str | None = None) -> dict:
    """落机读 yaml + 人读一页（幂等，原子替换）。"""
    base = Path(out_dir) if out_dir else Path(board["main_root"]) / "docs/_working" / \
        "three_piece_infra" / "visibility_board"
    base.mkdir(parents=True, exist_ok=True)
    ypath = base / Path(BOARD_YAML_REL).name
    mpath = base / Path(BOARD_MD_REL).name
    md = render_markdown(board)
    text = "# 生成物，勿手改；改判据请改 " + __name__ + "\n" + _dump_yaml(board)
    for p, content in ((ypath, text), (mpath, md)):
        tmp = p.with_suffix(p.suffix + ".tmp")
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, p)
    return {"yaml": str(ypath), "markdown": str(mpath), "yaml_bytes": ypath.stat().st_size}


# trae_060-reviewed: ①该存在——三总包并发实测互不可见（B1 只改不提交零痕迹 / B2 无总线读数即陈旧 /
# B4 对话↔st-* 无桥 / B5 云上面不可见），本件把四问收敛为一次读；②不能合并——worktree_drift_watchdog
# 是单主区写完整性看门狗（判"内容回退"），classify_workspace_wip 是单根判读器，二者均无跨 worktree
# 枚举与新鲜度语义，本件只做编排+渲染零新扫描器；③治标否——治的是"发现靠运气"根因（AGENTS §9.5
# 静态清单禁手工维护），warn/clean 语义零阻断零 git 写，fail-soft 永不拦提交。
def make_visibility_board_reconciler(gateway: object | None = None):
    """构造 post-commit 刷新 reconciler（事件触发，零 cron/Timer/sleep-loop）。"""
    from zephyr.governance.audit.reconciliation_registry import ReconcileResult, ReconcilerSpec

    root = Path(str(getattr(gateway, "project_root", None) or Path.cwd())).resolve()

    def _trigger(committed_files: list[str]) -> bool:
        rels = [os.path.relpath(str(f), str(root)).replace("\\", "/") for f in committed_files]
        return any(r.startswith(_REFRESH_PREFIXES) for r in rels)

    def _reconcile(committed_files: list[str], session_id: str):
        try:
            board = build_board(
                root, budget_seconds=_RECONCILE_BUDGET_SECONDS, classify_top_n=2,
                max_worktrees=_RECONCILE_MAX_WORKTREES, fast=True, skip_schtasks=True,
            )
            paths = write_board(board)
            det = (f"visibility-board post-commit（{session_id or 'unknown'}）："
                   f"{board['measured']['worktrees_scanned']}/"
                   f"{board['measured']['worktrees_discovered']} 车道，"
                   f"{board['measured']['build_seconds']}s，truncated="
                   f"{board['measured']['truncated']}，产物 {paths['yaml']}")
            return ReconcileResult(action="warn" if board["worktrees"]["self_check"][
                "red_flag_upward_resolution"] else "clean", detail=det)
        except Exception as exc:  # noqa: BLE001 — fail-soft，公告牌永不阻断提交
            logger.warning("visibility-board 刷新失败: %s", type(exc).__name__)
            return ReconcileResult(
                action="warn", detail=f"visibility-board 刷新失败: {type(exc).__name__}")

    return ReconcilerSpec(
        gate_id="VISIBILITY-BOARD",
        trigger=_trigger,
        reconcile=_reconcile,
        file_ops=frozenset({"read", "write"}),
        priority=210,
    )


def make_external_reconciler_spec(host: object | None = None):
    """ReconciliationRegistry 外部规格发现钩子入口（签名稳定）。"""
    return make_visibility_board_reconciler(host)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="施工公告牌（并发态单一快照）")
    parser.add_argument("project_root", nargs="?", default=".")
    parser.add_argument("--out-dir", default=None, help="产物目录（默认 docs/_working/.../visibility_board）")
    parser.add_argument("--fast", action="store_true", help="跳过 classify 判读（最快）")
    parser.add_argument("--skip-schtasks", action="store_true", help="跳过计划任务查询（离线/CI）")
    parser.add_argument("--budget-seconds", type=int, default=DEFAULT_BUDGET_SECONDS)
    parser.add_argument("--classify-top", type=int, default=DEFAULT_CLASSIFY_TOP_N)
    parser.add_argument("--max-worktrees", type=int, default=0, help="扫描车道上限（0=不限）")
    parser.add_argument("--print-md", action="store_true", help="只打印人读页不落盘")
    args = parser.parse_args(argv)

    board = build_board(
        Path(args.project_root).resolve(),
        budget_seconds=args.budget_seconds,
        classify_top_n=args.classify_top,
        max_worktrees=args.max_worktrees,
        fast=args.fast,
        skip_schtasks=args.skip_schtasks,
    )
    if args.print_md:
        print(render_markdown(board))
        return 0
    paths = write_board(board, args.out_dir)
    print(json.dumps({"written": paths, "build_seconds": board["measured"]["build_seconds"],
                      "lanes": board["measured"]["worktrees_scanned"],
                      "truncated": board["measured"]["truncated"],
                      "red_flag_upward_resolution": board["worktrees"]["self_check"][
                          "red_flag_upward_resolution"]},
                     ensure_ascii=False, indent=2))
    return 1 if board["worktrees"]["self_check"]["red_flag_upward_resolution"] else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
