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
                out.append(
                    {
                        "qid": data.get("qid", bag.stem),
                        "state": state,
                        "file_count": len(data.get("files") or []),
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
    reasons = [f"last_activity idle {evidence['last_activity_age_seconds']}s > {DEATH_IDLE_SECONDS}s"]
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
    dead.sort(key=lambda d: float(d["entry"].get("last_activity") or 0.0))
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
        e = write_takeover_entry(
            root, d["sid"], resources=d["resources"], death_evidence=d["death_evidence"], registry_entry=d["entry"]
        )
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
        print(f"sid={r.get('sid')} ts={r.get('ts')} reason={r.get('death_evidence', {}).get('reason', '-')}")
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


def _cmd_sweep_absorbed(root: Path, age_hours: int = 48) -> int:
    """第 16 类机制：死信及时清算（预防+处理闭环的"处理"腿）。

    三分流（零删除，全部档案化）：
    1. absorbed——死袋全部文件 blob 与 HEAD 逐字节一致（内容已被他路落地，指针死而无魂）
       → 移 commit_queue/dead_archive/absorbed/，销账。
    2. aged——创建超 age_hours 未吸收 → 升级清单（处方已在 dead_reason，供维护班/AI 优先处理）。
    3. fresh——其余保留 dead/ 原状（等属主/处方循环，不干扰）。

    仓库锚定设计：判定只依赖 git HEAD 与袋内 blob_sha256，任何平台任何 agent 跑同一命令同结果。
    """
    import hashlib
    import os
    import time

    dead_dir = root / ".runtime" / "commit_queue" / "dead"
    arch_dir = root / ".runtime" / "commit_queue" / "dead_archive" / "absorbed"
    sweep_log = root / ".runtime" / "takeover" / "sweep_log.jsonl"
    arch_dir.mkdir(parents=True, exist_ok=True)
    sweep_log.parent.mkdir(parents=True, exist_ok=True)

    def _head_hash(rel: str) -> str | None:
        from zephyr.shared.infra.process_pool import run_subprocess_hidden

        r = run_subprocess_hidden(
            ["git", "-C", str(root), "cat-file", "blob", f"HEAD:{rel}"],
            capture_output=True,
            text=False,  # 字节态：与袋内 blob_sha256（原始字节哈希）同口径
        )
        return hashlib.sha256(r.stdout).hexdigest() if r.returncode == 0 else None

    absorbed: list[str] = []
    aged: list[str] = []
    fresh = 0
    now = time.time()
    for qp in sorted(dead_dir.glob("*.json")):
        try:
            bag = json.loads(qp.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        files = bag.get("files") or []
        if not files:
            continue
        ok = True
        for f in files:
            if _head_hash(f["path"]) != f.get("blob_sha256"):
                ok = False
                break
        age_h = (now - qp.stat().st_mtime) / 3600.0
        if ok:
            os.replace(qp, arch_dir / qp.name)
            absorbed.append(qp.stem)
        elif age_h > age_hours:
            aged.append(f"{qp.stem} ({len(files)}件, {age_h:.0f}h)")
        else:
            fresh += 1
    rec = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "absorbed": absorbed,
        "aged": aged,
        "fresh": fresh,
    }
    with sweep_log.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"sweep: absorbed={len(absorbed)} 销账 | aged={len(aged)} 升级 | fresh={fresh} 保留")
    for q in absorbed[:10]:
        print(f"  absorbed: {q}")
    for q in aged[:10]:
        print(f"  aged: {q}")
    print(f"账: {sweep_log}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="接管台账：死亡会话资源显化 L1+L2（scan/list/resolve）")
    parser.add_argument("--scan", action="store_true", help="扫死亡会话生成/更新 open 条目（幂等）")
    parser.add_argument("--list", action="store_true", help="列 open 条目+处方")
    parser.add_argument("--resolve", metavar="SID", help="迁移该 sid 的 open 条目到 resolved/")
    parser.add_argument("--by", metavar="TAKER", default="", help="接管者标识（resolve 必填语义）")
    parser.add_argument("--note", default="", help="处置结论注记")
    parser.add_argument(
        "--sweep-absorbed", action="store_true", help="死信及时清算：HEAD 吸收的销账/超龄升级/新鲜保留（第 16 类机制）"
    )
    parser.add_argument("--age-hours", type=int, default=48, help="超龄阈值（小时，缺省 48）")
    parser.add_argument("--root", default=".", help="仓库根（缺省=.）")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if args.sweep_absorbed:
        return _cmd_sweep_absorbed(root, args.age_hours)
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
