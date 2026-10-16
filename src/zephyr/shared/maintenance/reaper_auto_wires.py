# [BLUEPRINT] SH-MAIN-001 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md
# [MODULE] zephyr.shared.maintenance.reaper_auto_wires
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.infra.process_pool (run_subprocess_hidden, TRAE-067 铁律2);
#                zephyr.shared.io.audit_jsonl_writer (append_audit_jsonl, 审计追加+轮转唯一通道);
#                zephyr.shared.utils.time_utils (now_utc, RULE-SCHEMA-TZ);
#                scripts.session_worktree (判活/锁TTL/排除表同源引用——spec_from_file_location
#                按路径加载[计划任务环境 sys.path 无仓根]，禁复制数值);
#                scripts.commit_queue (dead-archive CLI 语义真源，子进程调用零导入零改源)
# [CONSUMERS] zephyr.trading.process_reaper (_run_safety_wires 第四/五/六 wire=既有计划任务扫描循环
#             挂点，禁新常驻进程——root-cure-plan §7 重校准裁定①②+L3 补件，st-diskp0-20261015 接线队 A);
#             tests.shared.test_reaper_auto_wires
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 本模块=reaper 三条自动维护线函数库（无 daemon/无 loop/无自启——挂点在消费方
#              _run_safety_wires 既有周期面，宪法 §9.3）; 三线语义真源各自工具（dead-archive/archive/
#              git 本体），零判定逻辑复制（动作=子进程调工具 CLI，工具内侧 fail-closed 死判/落地校验/
#              租约拒绝为最后防线）; 裁定语义禁改面：死信 age=7 天（Kafka 168h 同频）、git gc 自带
#              2 周宽限（禁 --prune=now，深清=Owner）、死车道判型=仅 zero_loss 自动（needs_rescue 只告警;
#              其余只记账）; 三 flag 出厂 ON（flags.yaml dead_archive_auto/git_gc_auto/dead_lane_autoreap），
#              回滚=enabled:false 下一轮即停; flags 不可读=跳过不动作; dry_run 轮零副作用;
#              任何失败记入返回值不反噬收割主链（对齐 _run_safety_wires 永不抛口径）
# [MODIFY-GUARD] 无（纯新增函数面；消费方挂点=process_reaper._run_safety_wires）
# [STABILITY] new
# [SAFETY] M（动作面：死信 mv 归档可逆+gc --auto git 自带宽限+车道 archive 仅 zero_loss 判型，工具活车道硬拒无逃生）
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 三个 run_*_wire 永不抛；子进程非零退出/超时/不可解析记入返回值 status，真跑轮审计行照写
# [TESTS] tests/shared/test_reaper_auto_wires.py（tmp 仓根+mock runner：flag 三态/命令面冻结/判活与
#         mtime 双确认两侧/判型分诊/dry-run 零副作用/审计行落盘/永不抛/按路径加载）
# [TTL] permanent
"""reaper_auto_wires — reaper 扫描循环的三条自动化维护线（root-cure-plan §7 重校准，函数库非 daemon）。

病灶：三项 Owner 已裁定照准的自动化此前"已裁定未接线"——死信归档靠人工想起、git 对象
增长无人例行清、死车道靠夜巡目视。本模块把三线装进 process_reaper._run_safety_wires
既有计划任务扫描循环（每轮顺带，禁新 daemon/cron，宪法 §9.3）。

三线（各带审计行，flag 出厂 ON，回滚=flags.yaml 对应键 enabled:false）：
- dead_archive_auto（裁定②）：子进程调 ``commit_queue.py dead-archive --days 7
  --content-level --execute``（fail-closed 语义零改，age/内容级判据全在工具内侧）；
  审计=.runtime/audit/dead_archive_wire.jsonl。
- git_gc_auto（裁定①例行半）：``git gc --auto``（2 周宽限+gc.auto 阈值 git 内建，
  无事即退零成本）；禁 --prune=now（深清=Owner）；审计=.runtime/audit/git_gc_wire.jsonl。
- dead_lane_autoreap（L3 补件）：扫 .aidrafts/.worktrees 车道→判活同源
  （scripts.session_worktree._check_archive_target_dead=活跃注册表+新鲜锁+免疫标记）
  外加 mtime>48h 保守双确认→先 dry-run 判型（工具自身三查）→仅 zero_loss 追加
  --execute 自动收；needs_rescue 只写 .runtime/workspace_alerts/ 告警件留夜巡/人工；
  审计=.runtime/audit/dead_lane_wire.jsonl。

Usage（消费方挂点示意）::

    wires["dead_archive"] = run_dead_archive_wire(REPO_ROOT, dry_run=report.dry_run)
    wires["git_gc_auto"] = run_git_gc_auto_wire(REPO_ROOT, dry_run=report.dry_run)
    wires["dead_lane"] = run_dead_lane_wire(REPO_ROOT, dry_run=report.dry_run)

# [ALGO_FLOW] external: docs/03_modules/_domain_shared/algo_flow/maintenance/reaper_auto_wires.yaml
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Final

from zephyr.shared.infra.process_pool import run_subprocess_hidden
from zephyr.shared.io.audit_jsonl_writer import append_audit_jsonl
from zephyr.shared.utils.time_utils import now_utc

__all__: Final = [
    "DEAD_ARCHIVE_DAYS",
    "DEAD_LANE_MIN_AGE_HOURS",
    "GIT_GC_CMD",
    "run_dead_archive_wire",
    "run_dead_lane_wire",
    "run_git_gc_auto_wire",
]

#: 三线子进程统一超时（秒）——工单指定 600s（gc 线明确，三线同一上限防挂死收割循环）
_WIRE_SUBPROCESS_TIMEOUT_S: Final = 600.0

#: 审计文件名（.runtime/audit/ 下；工单指定名）
_DEAD_ARCHIVE_AUDIT: Final = "dead_archive_wire.jsonl"
_GIT_GC_AUDIT: Final = "git_gc_wire.jsonl"
_DEAD_LANE_AUDIT: Final = "dead_lane_wire.jsonl"

#: 死信归档年龄门槛（天）——裁定②语义（与 Kafka 默认保留 168h 精确同频），禁改
DEAD_ARCHIVE_DAYS: Final = 7.0

#: 死车道保守双确认 mtime 门槛（小时）——L3 补件语义，禁改
DEAD_LANE_MIN_AGE_HOURS: Final = 48.0

#: 死车道扫描根（相对 repo root；车道=目录名即 sid）
_LANE_ROOTS: Final[tuple[str, ...]] = (".aidrafts", ".worktrees")

#: git gc 例行维护命令面（冻结常量）——禁 --prune=now（深清=Owner 门位，裁定①）；
#: 2 周宽限（gc.pruneExpire 默认 two.weeks.ago）与 gc.auto 阈值判断均为 git 内建。
GIT_GC_CMD: Final[tuple[str, ...]] = ("git", "gc", "--auto")

#: 判型行提取（archive 工具 dry-run 输出 ``  判型: <verdict>``；本件不复制三查判据）
_VERDICT_RE: Final = re.compile(r"^\s*判型:\s*(\S+)", re.M)

#: 判型分诊（裁定语义，禁改）：仅 zero_loss 自动收；needs_rescue 只告警；
#: 其余（superseded_shell/ahead_only）只记账不动作（保守，宁留人工/夜巡）
_AUTO_REAP_VERDICTS: Final[frozenset[str]] = frozenset({"zero_loss"})
_ALERT_VERDICTS: Final[frozenset[str]] = frozenset({"needs_rescue"})

#: 告警件文件名 sid 白名单外的字符替换（防路径穿越；车道 sid 实际均落白名单内）
_ALERT_SID_RE: Final = re.compile(r"[^A-Za-z0-9._-]")

_STDERR_TAIL_CHARS: Final = 400

_WireRunner = Callable[..., subprocess.CompletedProcess]


def _read_flag(repo_root: Path | str, key: str) -> bool | None:
    """读 flags.yaml 的 ``flags.<key>.enabled``（直读 YAML，对齐 git_commit_gateway 同款读法）。

    返回：True/False=在册值（键缺省=True=出厂 ON）；None=flags.yaml 不可读（repo 异常态，
    wire 跳过不动作——比误动作安全）。
    """
    try:
        import yaml  # type: ignore[import-untyped]  # noqa: PLC0415

        data = yaml.safe_load((Path(repo_root) / "config" / "flags.yaml").read_text(encoding="utf-8")) or {}
        section = (data.get("flags") or {}).get(key) or {}
        return bool(section.get("enabled", True))
    except Exception:  # noqa: BLE001 — 配置不可读=不动作
        return None


def _audit(repo_root: Path | str, filename: str, record: dict) -> bool:
    """审计行落盘（.runtime/audit/<filename>；append_audit_jsonl 自带 50MB 轮转）。"""
    return append_audit_jsonl(Path(repo_root) / ".runtime" / "audit", filename, record)


def _stderr_tail(text: str | None) -> str:
    return (text or "")[-_STDERR_TAIL_CHARS:]


def _iso_now() -> str:
    return now_utc().isoformat(timespec="seconds")


@lru_cache(maxsize=4)
def _load_session_worktree(repo_root_str: str) -> ModuleType:
    """按文件路径加载 scripts/session_worktree.py（判活/排除表/注册表同源真源）。

    不走 ``import scripts.session_worktree``：计划任务环境只挂 <repo>/src（usercustomize），
    仓根不在 sys.path——2026-10-16 14:27 首轮真跑实测 ModuleNotFoundError，本 loader 为补丁
    （spec_from_file_location 零 sys.path 副作用；同 root 命中缓存零重复执行）。
    """
    import importlib.util

    p = Path(repo_root_str) / "scripts" / "session_worktree.py"
    spec = importlib.util.spec_from_file_location("_wire_session_worktree", p)
    if spec is None or spec.loader is None:
        raise ImportError(f"session_worktree.py 不可加载: {p}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_dead_archive_wire(
    repo_root: Path | str,
    *,
    dry_run: bool = False,
    days: float = DEAD_ARCHIVE_DAYS,
    timeout_s: float = _WIRE_SUBPROCESS_TIMEOUT_S,
    runner: _WireRunner | None = None,
) -> dict[str, Any]:
    """wire④ 死信自动归档（裁定②）：调 commit_queue.py dead-archive，仅动 age>7 天袋。

    命令面固定 ``dead-archive --days 7 --content-level [--execute] --json``：fail-closed
    语义（年龄/内容级/落地校验/租约拒绝）零改全在工具内侧；dry_run 轮不带 --execute
    （工具默认 dry-run 零写）。真跑轮结果写审计行；永不抛。
    """
    root = Path(repo_root)
    out: dict[str, Any] = {"wire": "dead_archive", "dry_run": dry_run, "days": days}
    flag = _read_flag(root, "dead_archive_auto")
    if flag is not True:
        out["status"] = "skipped_disabled" if flag is False else "skipped_flag_unreadable"
        return out
    cmd = [
        sys.executable,
        str(root / "scripts" / "commit_queue.py"),
        "dead-archive",
        "--days",
        f"{days:g}",
        "--content-level",
        "--json",
    ]
    if not dry_run:
        cmd.append("--execute")
    out["status"] = "ok"
    run = runner or run_subprocess_hidden
    try:
        proc = run(cmd, cwd=str(root), timeout=timeout_s, encoding="utf-8")
    except subprocess.TimeoutExpired:
        out["status"] = "error"
        out["error"] = f"timeout_after_{timeout_s:g}s"
    except Exception as exc:  # noqa: BLE001 — 永不抛契约（OSError/参数异常等全收敛）
        out["status"] = "error"
        out["error"] = f"{type(exc).__name__}: {exc}"
    else:
        out["rc"] = proc.returncode
        out["stderr_tail"] = _stderr_tail(proc.stderr)
        payload = _extract_json_obj(proc.stdout or "")
        if payload is not None:
            out["archived"] = payload.get("archived") or []
            out["kept"] = payload.get("kept") or {}
            out["bag"] = payload.get("bag")
            if proc.returncode != 0:
                out["status"] = "error"
        else:
            out["status"] = "error"
            out["error"] = "unparsable_output"
    if not dry_run:
        out["audit_written"] = _audit(root, _DEAD_ARCHIVE_AUDIT, {"ts": _iso_now(), **out})
    return out


def run_git_gc_auto_wire(
    repo_root: Path | str,
    *,
    dry_run: bool = False,
    timeout_s: float = _WIRE_SUBPROCESS_TIMEOUT_S,
    runner: _WireRunner | None = None,
) -> dict[str, Any]:
    """wire⑤ git gc --auto 例行维护（裁定①例行半）：git 自带 2 周宽限+阈值判断，无事即退零成本。

    命令面=GIT_GC_CMD 冻结常量（含 --prune 字样即拒绝执行——深清=Owner 门位）；
    dry_run 轮直接跳过（gc 无只读形态，零副作用语义对齐）；真跑轮结果写审计行；永不抛。
    """
    root = Path(repo_root)
    out: dict[str, Any] = {"wire": "git_gc_auto", "dry_run": dry_run}
    flag = _read_flag(root, "git_gc_auto")
    if flag is not True:
        out["status"] = "skipped_disabled" if flag is False else "skipped_flag_unreadable"
        return out
    if dry_run:
        out["status"] = "skipped_dry_run"
        return out
    if any("--prune" in part for part in GIT_GC_CMD):  # 双保险：命令面冻结断言（深清=Owner）
        out["status"] = "error"
        out["error"] = "cmd_guard_prune_forbidden"
        return out
    cmd = list(GIT_GC_CMD)
    out["status"] = "ok"
    run = runner or run_subprocess_hidden
    t0 = now_utc()
    try:
        proc = run(cmd, cwd=str(root), timeout=timeout_s, encoding="utf-8")
    except subprocess.TimeoutExpired:
        out["status"] = "error"
        out["error"] = f"timeout_after_{timeout_s:g}s"
    except Exception as exc:  # noqa: BLE001 — 永不抛契约（OSError/参数异常等全收敛）
        out["status"] = "error"
        out["error"] = f"{type(exc).__name__}: {exc}"
    else:
        out["rc"] = proc.returncode
        out["stderr_tail"] = _stderr_tail(proc.stderr)
        if proc.returncode != 0:
            out["status"] = "error"
    out["elapsed_s"] = round((now_utc() - t0).total_seconds(), 3)
    out["audit_written"] = _audit(root, _GIT_GC_AUDIT, {"ts": _iso_now(), **out})
    return out


def run_dead_lane_wire(
    repo_root: Path | str,
    *,
    dry_run: bool = False,
    timeout_s: float = _WIRE_SUBPROCESS_TIMEOUT_S,
    runner: _WireRunner | None = None,
    now_ts: float | None = None,
) -> dict[str, Any]:
    """wire⑥ 死车道自动收（L3 补件）：判死→判型→仅 zero_loss 自动 archive --execute。

    判活同源=scripts.session_worktree._check_archive_target_dead（活跃注册表+新鲜锁
    +commit_persisted 免疫标记），外加 mtime>48h 保守双确认（裁定语义，禁改）；
    判型=工具自身 dry-run 三查（本件零判定复制）；needs_rescue 只写告警件不自动动；
    执行轮工具内侧死判硬拒仍为最后防线（竞态窗活车道必被工具拒绝）。永不抛。
    """
    root = Path(repo_root)
    out: dict[str, Any] = {
        "wire": "dead_lane",
        "dry_run": dry_run,
        "scanned": 0,
        "dead_candidates": 0,
        "skipped_alive": 0,
        "skipped_young": 0,
        "skipped_excluded": 0,
        "skipped_not_registered": 0,
        "auto_archived": [],
        "auto_failed": [],
        "needs_rescue": [],
        "other_verdicts": [],
        "errors": [],
    }
    flag = _read_flag(root, "dead_lane_autoreap")
    if flag is not True:
        out["status"] = "skipped_disabled" if flag is False else "skipped_flag_unreadable"
        return out
    out["status"] = "ok"

    sw = _load_session_worktree(str(root))  # 判活/排除表/注册表同源真源（按路径加载，见 docstring）

    registry = sw._list_worktree_registry()
    reg_paths = {sw._normcase(e["path"]) for e in registry if not e.get("bare")}
    now = float(now_ts) if now_ts is not None else now_utc().timestamp()
    min_age_s = DEAD_LANE_MIN_AGE_HOURS * 3600.0
    run = runner or run_subprocess_hidden

    for lane_root in _LANE_ROOTS:
        lane_dir = root / lane_root
        if not lane_dir.is_dir():
            continue
        try:
            entries = sorted(lane_dir.iterdir())
        except OSError as exc:
            out["errors"].append(f"{lane_root}: scan_failed:{exc}")
            continue
        for entry in entries:
            if not entry.is_dir():
                continue
            out["scanned"] += 1
            sid = entry.name
            path_norm = sw._normcase(entry)
            if any(m in path_norm for m in sw._ARCHIVE_ALL_EXCLUDED_MARKERS):
                out["skipped_excluded"] += 1
                continue
            if path_norm not in reg_paths:
                out["skipped_not_registered"] += 1
                continue
            try:
                dead, reason = sw._check_archive_target_dead(sid)
            except Exception as exc:  # noqa: BLE001 — 单车道判活失败不中断扫描
                out["errors"].append(f"{sid}: liveness_check_failed:{type(exc).__name__}:{exc}")
                continue
            if not dead:
                out["skipped_alive"] += 1
                continue
            try:
                age_s = now - entry.stat().st_mtime
            except OSError as exc:
                out["errors"].append(f"{sid}: stat_failed:{exc}")
                continue
            if age_s <= min_age_s:
                out["skipped_young"] += 1  # mtime>48h 保守双确认未过
                continue
            out["dead_candidates"] += 1
            _reap_one_lane(
                root,
                sid,
                out,
                dry_run=dry_run,
                reason=reason,
                runner=run,
                timeout_s=timeout_s,
            )

    if not dry_run:
        out["audit_written"] = _audit(root, _DEAD_LANE_AUDIT, {"ts": _iso_now(), **out})
    if out["errors"]:
        out["status"] = "completed_with_errors"
    return out


def _reap_one_lane(
    root: Path,
    sid: str,
    out: dict[str, Any],
    *,
    dry_run: bool,
    reason: str,
    runner: _WireRunner,
    timeout_s: float,
) -> None:
    """单车道分诊：dry-run 判型（工具自身三查）→ 按裁定语义分流（zero_loss 自动/告警/记账）。"""
    rc, stdout, stderr = _run_archive_cli(root, sid, execute=False, runner=runner, timeout_s=timeout_s)
    if rc != 0:
        # 工具内侧死判硬拒（竞态窗活车道）或注册表未命中——保守跳过不重试
        out["errors"].append(f"{sid}: plan_rc={rc} {_stderr_tail(stderr).strip()[:120]}")
        return
    m = _VERDICT_RE.search(stdout or "")
    if not m:
        out["errors"].append(f"{sid}: verdict_unparsable")
        return
    verdict = m.group(1)
    if verdict in _AUTO_REAP_VERDICTS:
        if dry_run:
            out.setdefault("planned", []).append({"sid": sid, "verdict": verdict})
            return
        xrc, _xout, xerr = _run_archive_cli(root, sid, execute=True, runner=runner, timeout_s=timeout_s)
        if xrc == 0:
            out["auto_archived"].append(sid)
        else:
            out["auto_failed"].append(sid)
            out["errors"].append(f"{sid}: execute_rc={xrc} {_stderr_tail(xerr).strip()[:120]}")
    elif verdict in _ALERT_VERDICTS:
        out["needs_rescue"].append({"sid": sid, "verdict": verdict})
        if not dry_run:
            _write_rescue_alert(root, sid, verdict, reason)
    else:
        out["other_verdicts"].append({"sid": sid, "verdict": verdict})  # superseded_shell/ahead_only 只记账


def _run_archive_cli(
    root: Path, sid: str, *, execute: bool, runner: _WireRunner, timeout_s: float
) -> tuple[int, str, str]:
    """调 session_worktree.py archive <sid> [--execute]（工具内侧死判/存证/rescue 全保留）。"""
    cmd = [sys.executable, str(root / "scripts" / "session_worktree.py"), "archive", sid]
    if execute:
        cmd.append("--execute")
    try:
        proc = runner(cmd, cwd=str(root), timeout=timeout_s, encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 — 永不抛契约（超时/OS 错误全收敛为 rc=1）
        return 1, "", f"{type(exc).__name__}: {exc}"
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def _write_rescue_alert(root: Path, sid: str, verdict: str, reason: str) -> None:
    """needs_rescue 告警件（.runtime/workspace_alerts/，同名覆盖=每轮刷新不堆积；留夜巡/人工）。"""
    safe_sid = _ALERT_SID_RE.sub("_", sid)
    alert_dir = root / ".runtime" / "workspace_alerts"
    try:
        alert_dir.mkdir(parents=True, exist_ok=True)
        (alert_dir / f"dead_lane_needs_rescue_{safe_sid}.json").write_text(
            json.dumps(
                {
                    "alert": "dead_lane_needs_rescue",
                    "session_id": sid,
                    "verdict": verdict,
                    "dead_evidence": reason,
                    "detected_at": _iso_now(),
                    "wire": "dead_lane_autoreap",
                    "next_step": (
                        "夜巡/人工核后跑 python scripts/session_worktree.py archive <sid> --execute"
                        "（工具 fail-closed：patch 存证+？？rescue 后才清）"
                    ),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
    except OSError:
        pass  # 告警件失败不反噬扫描（审计行仍带 needs_rescue 清单）


def _extract_json_obj(text: str) -> dict[str, Any] | None:
    """从 CLI 混合输出（人读行+--json 尾块）提取首个 JSON 对象；不可解析返回 None。"""
    start = text.find("{")
    if start < 0:
        return None
    try:
        payload = json.loads(text[start:])
    except ValueError:
        return None
    return payload if isinstance(payload, dict) else None
