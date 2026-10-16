#!/usr/bin/env python
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md | §nine_face
# [MODULE] scripts.ops.nine_face_watch
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.io.audit_jsonl_writer (append_audit_jsonl 同款机制: 告警行统一写面);
#                zephyr.shared.utils.time_utils (now_utc, RULE-SCHEMA-TZ: 禁 datetime.now()/time.time() 生成时间戳);
#                zephyr.shared.infra.process_pool (run_subprocess_hidden, trae_067 CREATE_NO_WINDOW 统一 git 只读子命令入口)
# [CONSUMERS] 计划任务/人工手动触发（默认 one-shot）; 进程 reaper wire 挂载候选（root-cure-plan §3-L5 红线有警）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 只测量+告警，**零删停**（处置动作=告警 escalated 留 Owner——NL-6 物理删除=Owner 门位）;
#              九面测量全部只读（目录 glob/scandir 尺寸累计 + git 只读子命令 worktree list/status）,
#              任一测量失败记 errors 行内继续（单面失能不反噬整轮巡检）;
#              阈值单一真源=config/flags.yaml flags.nine_face_budget.*（禁复制字面量）;
#              告警双落点=.runtime/workspace_alerts/nine_face_<stamp>.json 告警件
#              + .runtime/audit/nine_face_alerts.jsonl 审计行（append_audit_jsonl, 自带 50MB 轮转）;
#              基线快照=.runtime/audit/nine_face_baseline.json（每轮真跑原子刷新，最新读数即基线）;
#              节流=巡检 60min（读基线自身 ts 判距，零额外状态文件）+告警冷却 60min（读告警审计末行 ts）;
#              enabled:false=出厂 OFF（只测+记基线，不告警——采样与告警两段解耦，与 disk_floor 同口径）;
#              部署形态=one-shot（OS 计划任务/reaper wire 事件驱动，进程秒级退出，无常驻循环面）
# [MODIFY-GUARD] config/flags.yaml flags.nine_face_budget（阈值真源，本件只读禁改）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] patrol_once 永不抛（OSError/git 失败收入 errors 列表）; exit 0=巡检完成无超限/节流跳过;
#                  exit 1=九面超限（budget_state=breach, 巡检本身成功）; exit 2=巡检设施故障（基线快照不可写）
# [TESTS] tests/scripts/test_nine_face_watch.py（假目录树实测九面计数/超限两侧/节流/OFF 降级/dry-run 零写）
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: 本件仅 one-shot 形态，由 OS 计划任务/reaper wire 人工事件驱动
#                         （与 vhdx_floor_watch 同部署形态），进程秒级退出；无 in-process cron/Timer/
#                         sleep-loop/常驻循环面（CAPABILITY-OVERLAP 裁定 2026-10-16：与 vhdx._run_watch
#                         同构常驻循环不重建，常驻需求复用 vhdx_floor_watch --watch）
# noqa: m11-perm-manual-legitimate  M11豁免: one-shot 形态由 OS 计划任务/人工按需触发（schtasks hourly，
#                         与 vhdx_floor_watch 同部署形态），CLI argparse 面为人工巡检入口，非常驻自启服务/非 daemon
#
# 【部署说明】one-shot 进程秒级退出，无需登记 reaper 白名单；常驻循环需求复用 vhdx_floor_watch --watch
# （本件刻意不建第二份同构 watch 循环——CAPABILITY-OVERLAP extract 级裁定 2026-10-16）。
# create-guard-not-dup: 本模块只 stat 目录条目计数/尺寸+git 只读列表并告警，不解析任何文件内容结构——
#                       命中词 parse 系 porcelain 文本行解析的散文碰撞，非 algo_flow_parse/file_header_parser 的第二实现
"""nine_face_watch — 九面遥测预算只读巡检 + 超限告警（st-diskp0-20261015 防复发 L5）。

病灶：2026-10-15 D 盘满盘事故复盘（docs/_working/2026-10-16-root-cure-plan.md §3-L5）——
东西从提交正门进来后，死车道/死信/审计/证据/tmp 五个出口只进不出，6 天 3 观测点零报警。
治本=出口闭环第五层"红线有警"：把 6 天 3 观测点变成每小时全-face 巡检+超限即喊。
本件补该观测：只测量+告警，**零删停**（自动处置属 Owner 门位，本件永不执行）。

九面（全部只读、廉价）：
    ① dead_bags      .runtime/commit_queue/dead/ 下 q-*.json 袋数
    ② tmp_gib        .runtime/tmp 递归体积 GiB
    ③ lanes          git worktree list 去主区/pool/serializer 后车道数
    ④ staged         主区 staged+untracked 数（git status --porcelain）
    ⑤ quarantine_gib .runtime/quarantine 递归体积 GiB
    ⑥ sessions       .runtime/sessions/ 一级子目录数
    ⑦ audit_gib      .runtime/gate_audit + .runtime/audit 合计递归体积 GiB
    ⑧ root_files     .runtime 根一级散件数（非目录文件）
    ⑨ queue_backlog  队列 pending+dead 袋数（q-*.json）

预算面（flags.nine_face_budget.*，判据=value < budget 为健康，读数>=阈值即超限）：
    任一超限且 enabled=true →
    ① .runtime/workspace_alerts/nine_face_<date>_<time>.json 告警件；
    ② .runtime/audit/nine_face_alerts.jsonl 告警审计行（append_audit_jsonl 同款机制）。
    告警级=escalated：只升级给 Owner，不自动处置。出厂 enabled:false=OFF（只测记基线），
    开闸属 Owner 门位。

基线面：每轮真跑（非 dry-run）原子刷新 .runtime/audit/nine_face_baseline.json——
    最新九面读数即基线（--once 首跑即产出首份基线快照）。

部署（任选其一，本件仅 one-shot、零常驻循环——常驻需求复用 vhdx_floor_watch --watch）：
    1. OS 计划任务小时级 one-shot（推荐，reaper wire 挂载候选）：
       schtasks /Create /SC HOURLY /TN "ZephyrNineFaceWatch" /TR
         "python D:\\ZephyrAlpha\\scripts\\ops\\nine_face_watch.py"
    2. 人工即时巡检：python scripts/ops/nine_face_watch.py --once

配置（环境变量，可选）：
    NFW_MIN_INTERVAL     巡检节流分钟（默认 60；--once 跳过）
    NFW_ALERT_COOLDOWN   告警冷却分钟（默认 60，防刷屏）

# [ALGO_FLOW] external: docs/03_modules/_domain_infrastructure_operations/algo_flow/nine_face_watch.yaml
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from zephyr.shared.io.audit_jsonl_writer import append_audit_jsonl  # noqa: E402
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

RUNTIME_REL = Path(".runtime")
QUEUE_REL = RUNTIME_REL / "commit_queue"
DEAD_DIR_REL = QUEUE_REL / "dead"
PENDING_DIR_REL = QUEUE_REL / "pending"
TMP_DIR_REL = RUNTIME_REL / "tmp"
QUARANTINE_DIR_REL = RUNTIME_REL / "quarantine"
SESSIONS_DIR_REL = RUNTIME_REL / "sessions"
GATE_AUDIT_DIR_REL = RUNTIME_REL / "gate_audit"
AUDIT_DIR_REL = RUNTIME_REL / "audit"
ALERT_DIR_REL = RUNTIME_REL / "workspace_alerts"
BASELINE_FILENAME = "nine_face_baseline.json"
ALERT_AUDIT_FILENAME = "nine_face_alerts.jsonl"
GIB = 1024**3
_Q_GLOB = "q-*.json"  # 队列袋命名（commit_queue._STATES 四态同款，状态文件不计数）

#: 九面键序（行字段与预算键一一对应；预算键即面键，禁另造第二套命名）
FACE_KEYS: tuple[str, ...] = (
    "dead_bags",
    "tmp_gib",
    "lanes",
    "staged",
    "quarantine_gib",
    "sessions",
    "audit_gib",
    "root_files",
    "queue_backlog",
)

#: 出厂保守预算（config/flags.yaml flags.nine_face_budget 缺席键的回退值；真源仍是 YAML）
FACTORY_BUDGETS: dict[str, float] = {
    "dead_bags": 80,
    "tmp_gib": 5.0,
    "lanes": 60,
    "staged": 600,
    "quarantine_gib": 1.5,
    "sessions": 120,
    "audit_gib": 2.5,
    "root_files": 40,
    "queue_backlog": 150,
}

#: GiB 面集合（其余面为件数整数面；阈值语义同型 value < budget 为健康）
_GIB_FACES = frozenset({"tmp_gib", "quarantine_gib", "audit_gib"})

_DEFAULT_MIN_INTERVAL_MIN = float(os.environ.get("NFW_MIN_INTERVAL", "60"))
_DEFAULT_ALERT_COOLDOWN_MIN = float(os.environ.get("NFW_ALERT_COOLDOWN", "60"))
_GIT_TIMEOUT_S = 60


def read_nine_face_budget_config(repo_root: Path | str | None = None) -> tuple[bool, dict[str, float | None]]:
    """flags.nine_face_budget 阈值读取唯一点（(enabled, budgets)；缺配置=出厂 (False, 出厂预算)）。

    单一真源=config/flags.yaml flags.nine_face_budget.*——本函数即那个共享读取面；
    缺席键回出厂保守值（禁复制字面量到消费方）；enabled 缺省 False（出厂 OFF）。
    """
    root = Path(repo_root) if repo_root else _REPO_ROOT
    budgets: dict[str, float | None] = dict(FACTORY_BUDGETS)
    try:
        import yaml

        doc = yaml.safe_load((root / "config" / "flags.yaml").read_text(encoding="utf-8")) or {}
        cfg = (doc.get("flags") or {}).get("nine_face_budget") or {}
        for key in FACE_KEYS:
            if cfg.get(key) is not None:
                budgets[key] = float(cfg[key])
        return bool(cfg.get("enabled", False)), budgets
    except Exception:  # noqa: BLE001 — 配置设施异常回出厂值（fail-closed：缺配置不豁免告警面）
        return False, budgets


def _dir_size_bytes(path: Path) -> int:
    """目录递归体积字节数（条目级 OSError 跳过不计——测量永不抛）。"""
    total = 0
    try:
        with os.scandir(path) as it:
            for entry in it:
                try:
                    if entry.is_file(follow_symlinks=False):
                        total += entry.stat(follow_symlinks=False).st_size
                    elif entry.is_dir(follow_symlinks=False):
                        total += _dir_size_bytes(Path(entry.path))
                except OSError:
                    continue
    except OSError:
        return total
    return total


def _count_q_bags(dir_path: Path) -> int:
    """队列袋计数（q-*.json；目录缺席/失败=0——空态与失能态经 errors 区分）。"""
    try:
        return sum(1 for _ in dir_path.glob(_Q_GLOB))
    except OSError:
        return 0


def _parse_worktree_lanes(porcelain_text: str, repo_root: Path | str) -> list[str]:
    """git worktree list --porcelain 文本 → 车道路径表（纯函数，去主区/pool/serializer）。

    去除规则：主区=与 repo_root 同一路径；pool=路径含 _pool/ 或 /pool 段；
    serializer=路径含 commit_queue/worktree（队列序列化车道 w0..wn）。
    """
    root_norm = str(Path(repo_root)).replace("\\", "/").rstrip("/").lower()
    lanes: list[str] = []
    for line in porcelain_text.splitlines():
        if not line.startswith("worktree "):
            continue
        raw = line[len("worktree ") :].strip()
        norm = raw.replace("\\", "/").rstrip("/").lower()
        if norm == root_norm:
            continue  # 主区
        if "_pool/" in norm or "/pool-" in norm:
            continue  # pool 车道
        if "commit_queue/worktree" in norm:
            continue  # serializer 车道
        lanes.append(raw)
    return lanes


def _parse_status_staged_untracked(porcelain_text: str) -> int:
    """git status --porcelain 文本 → staged+untracked 行数（纯函数）。

    staged=X 位非空格且非 ?；untracked=?? 行；MM 这类 X,Y 双脏行计 1 行（一次清账）。
    """
    count = 0
    for line in porcelain_text.splitlines():
        if not line:
            continue
        x = line[0]
        if x == "?" or x not in (" ", "?"):
            count += 1
    return count


def _git_read(repo_root: Path, args: list[str]) -> tuple[int, str, str]:
    """只读 git 子命令（-c core.quotepath=false 保中文路径原样；永不抛）。

    走 process_pool.run_subprocess_hidden 统一入口（trae_067 CREATE_NO_WINDOW 强制，
    Windows 下消除控制台闪窗）；行为与 subprocess.run 全等。
    """
    try:
        from zephyr.shared.infra.process_pool import run_subprocess_hidden  # noqa: PLC0415

        proc = run_subprocess_hidden(
            ["git", "-c", "core.quotepath=false", *args],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=_GIT_TIMEOUT_S,
        )
        return proc.returncode, proc.stdout or "", proc.stderr or ""
    except (OSError, subprocess.TimeoutExpired) as e:
        return 127, "", str(e)


def measure_faces(
    repo_root: Path,
    *,
    worktree_porcelain: str | None = None,
    status_porcelain: str | None = None,
) -> tuple[dict[str, float | None], list[str]]:
    """九面只读测量（返回 (faces, errors)；单面失能=None+error 行内继续，永不抛）。

    worktree_porcelain/status_porcelain 测试注入口（None=真跑只读 git 子命令）。
    """
    faces: dict[str, float | None] = {}
    errors: list[str] = []
    runtime = repo_root / RUNTIME_REL

    faces["dead_bags"] = _count_q_bags(repo_root / DEAD_DIR_REL)
    faces["tmp_gib"] = round(_dir_size_bytes(repo_root / TMP_DIR_REL) / GIB, 3)
    faces["quarantine_gib"] = round(_dir_size_bytes(repo_root / QUARANTINE_DIR_REL) / GIB, 3)
    faces["sessions"] = _count_subdirs(runtime / SESSIONS_DIR_REL.name)
    faces["audit_gib"] = round(
        (_dir_size_bytes(runtime / GATE_AUDIT_DIR_REL.name) + _dir_size_bytes(runtime / AUDIT_DIR_REL.name)) / GIB,
        3,
    )
    faces["root_files"] = _count_loose_files(runtime)
    faces["queue_backlog"] = _count_q_bags(repo_root / PENDING_DIR_REL) + _count_q_bags(repo_root / DEAD_DIR_REL)

    # ③ 车道面 + ④ 主区 staged+untracked 面（git 只读；git 失能=None+error）
    rc_wt, out_wt, err_wt = (
        (0, worktree_porcelain, "")
        if worktree_porcelain is not None
        else _git_read(repo_root, ["worktree", "list", "--porcelain"])
    )
    if rc_wt == 0:
        faces["lanes"] = len(_parse_worktree_lanes(out_wt, repo_root))
    else:
        faces["lanes"] = None
        errors.append(f"git_worktree_list_failed: {err_wt.strip()[:200]}")
    rc_st, out_st, err_st = (
        (0, status_porcelain, "") if status_porcelain is not None else _git_read(repo_root, ["status", "--porcelain"])
    )
    if rc_st == 0:
        faces["staged"] = _parse_status_staged_untracked(out_st)
    else:
        faces["staged"] = None
        errors.append(f"git_status_failed: {err_st.strip()[:200]}")
    return faces, errors


def _count_subdirs(path: Path) -> int:
    """一级子目录数（目录缺席/失败=0）。"""
    try:
        return sum(1 for e in os.scandir(path) if e.is_dir(follow_symlinks=False))
    except OSError:
        return 0


def _count_loose_files(path: Path) -> int:
    """一级非目录散件数（目录缺席/失败=0）。"""
    try:
        return sum(1 for e in os.scandir(path) if not e.is_dir(follow_symlinks=False))
    except OSError:
        return 0


def evaluate_budgets(
    faces: dict[str, float | None],
    budgets: dict[str, float | None],
) -> list[dict]:
    """九面预算判读（纯函数）：value >= budget 即超限；任一侧缺席该面跳过。"""
    breaches: list[dict] = []
    for key in FACE_KEYS:
        value = faces.get(key)
        budget = budgets.get(key)
        if value is None or budget is None:
            continue
        if value >= budget:
            breaches.append({"face": key, "value": value, "budget": budget})
    return breaches


def _last_alert_ts(audit_dir: Path) -> str | None:
    """上一条告警审计行的 ts（冷却判距；读不到=None）。"""
    try:
        path = audit_dir / ALERT_AUDIT_FILENAME
        if not path.exists():
            return None
        lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        if not lines:
            return None
        ts = json.loads(lines[-1]).get("ts")
        return str(ts) if ts else None
    except Exception:  # noqa: BLE001 — 审计读失败=无冷却依据（放行，宁多告不漏告）
        return None


def _parse_ts_minutes_ago(ts: str | None) -> float | None:
    """ISO ts → 距今分钟数（失败=None）。"""
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(str(ts))
        if dt.tzinfo is None:
            return None
        return (now_utc() - dt).total_seconds() / 60.0
    except (ValueError, TypeError):
        return None


def write_escalation(alert_dir: Path, audit_dir: Path, row: dict, breaches: list[dict]) -> dict:
    """超限升级告警：workspace_alerts 告警件 + audit jsonl 行（双落点，失败不抛）。"""
    record = {
        "ts": row["ts"],
        "by": "scripts.ops.nine_face_watch",
        "event": "nine_face_budget_breach",
        "severity": "escalated",
        "breaches": breaches,
        "faces": row["faces"],
        "budgets": row["budgets"],
        "note": "只读巡检+告警，零自动处置；处置=Owner 门位",
        "recover": (
            "死信: python scripts/commit_queue.py dead-archive --content-level（先 dry-run）; "
            "车道: python scripts/session_worktree.py archive（先 dry-run）; "
            "tmp: python scripts/ops/cleanup_runtime_tmp_residue.py --execute; "
            "队列积压: python scripts/commit_queue.py drain"
        ),
    }
    out: dict = {"alert_file": None, "audit_line": False}
    stamp = row["ts"][:19].replace(":", "").replace("-", "").replace("T", "_")
    try:
        alert_dir.mkdir(parents=True, exist_ok=True)
        path = alert_dir / f"nine_face_{stamp}.json"
        path.write_text(json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")
        out["alert_file"] = str(path)
    except OSError:
        pass
    try:
        out["audit_line"] = append_audit_jsonl(Path(audit_dir), ALERT_AUDIT_FILENAME, record)
    except Exception:  # noqa: BLE001 — 告警审计失败不抛（workspace_alerts 件已兜底）
        pass
    return out


def _write_baseline_atomic(baseline_path: Path, row: dict) -> None:
    """基线快照原子刷新（tmp+os.replace，防并发轮读到半行）。"""
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = baseline_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(row, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, baseline_path)


def patrol_once(
    *,
    repo_root: Path | str | None = None,
    alert_dir: Path | None = None,
    audit_dir: Path | None = None,
    min_interval_min: float = _DEFAULT_MIN_INTERVAL_MIN,
    alert_cooldown_min: float = _DEFAULT_ALERT_COOLDOWN_MIN,
    once: bool = False,
    dry_run: bool = False,
    note: str | None = None,
) -> dict:
    """一轮九面巡检（默认入口）：节流→测量→预算判读→落基线→超限告警。永不抛。

    Returns:
        {action: patrolled|throttled|error, faces, budgets, enabled, budget_state,
         breaches, row, alert, errors[]}
        action=error 时 exit 2（基线不可写）；budget_state=breach 时调用方 exit 1。
    """
    root = Path(repo_root) if repo_root else _REPO_ROOT
    alerts = Path(alert_dir) if alert_dir else root / ALERT_DIR_REL
    audits = Path(audit_dir) if audit_dir else root / AUDIT_DIR_REL
    out: dict = {
        "action": "patrolled",
        "faces": None,
        "budgets": None,
        "enabled": False,
        "budget_state": "ok",
        "breaches": [],
        "row": None,
        "alert": None,
        "errors": [],
    }
    baseline = audits / BASELINE_FILENAME

    # 节流：距基线 ts < min_interval 分钟 → 跳过（基线自身即状态，零额外状态文件；--once 跳过）
    if not once and not dry_run and baseline.exists():
        try:
            prev = json.loads(baseline.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 — 基线读损坏=无节流依据（放行）
            prev = None
        gap = _parse_ts_minutes_ago(prev.get("ts") if isinstance(prev, dict) else None)
        if gap is not None and gap < min_interval_min:
            out["action"] = "throttled"
            out["last_ts"] = prev.get("ts")
            return out

    enabled, budgets = read_nine_face_budget_config(root)
    faces, errors = measure_faces(root)
    breaches = evaluate_budgets(faces, budgets) if enabled else []
    state = "disabled" if not enabled else ("breach" if breaches else "ok")
    row: dict = {
        "ts": now_utc().isoformat(),
        "faces": faces,
        "budgets": budgets,
        "budget_enabled": enabled,
        "budget_state": state,
        "breaches": breaches,
        "errors": list(errors),
    }
    if note:
        row["note"] = note
    out.update(
        faces=faces, budgets=budgets, enabled=enabled, budget_state=state, breaches=breaches, errors=errors, row=row
    )

    if dry_run:
        out["dry_run"] = True
        return out
    try:
        _write_baseline_atomic(baseline, row)
    except OSError as e:
        out["action"] = "error"
        out["errors"] = out["errors"] + [f"baseline_write_failed: {e}"]
        return out

    if state == "breach":
        gap = _parse_ts_minutes_ago(_last_alert_ts(audits))
        cooled = gap is not None and gap < alert_cooldown_min
        if not cooled:
            out["alert"] = write_escalation(alerts, audits, row, breaches)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="九面遥测预算只读巡检 + 超限告警（只测量+告警，零删停）")
    parser.add_argument("--once", action="store_true", help="单轮即时巡检（跳过巡检节流；并刷新基线快照）")
    parser.add_argument("--dry-run", action="store_true", help="只测不写（零副作用，不落基线不告警）")
    parser.add_argument("--note", dest="note", default=None, help="本轮备注（写入基线行 note 字段）")
    args = parser.parse_args(argv)

    r = patrol_once(once=args.once, dry_run=args.dry_run, note=args.note)
    if r["action"] == "error":
        print(f"[NINE-FACE] 巡检失败: {r['errors']}", file=sys.stderr)
        return 2
    if r["action"] == "throttled":
        print(f"[NINE-FACE] 节流跳过（基线 {r.get('last_ts')}；--once 强制）")
        return 0
    faces = r.get("faces") or {}
    print(
        f"[NINE-FACE] 巡检: dead={faces.get('dead_bags')} tmp={faces.get('tmp_gib')}GiB "
        f"lanes={faces.get('lanes')} staged={faces.get('staged')} quarantine={faces.get('quarantine_gib')}GiB "
        f"sessions={faces.get('sessions')} audit={faces.get('audit_gib')}GiB "
        f"root_files={faces.get('root_files')} backlog={faces.get('queue_backlog')} state={r['budget_state']}"
    )
    if r.get("breaches"):
        print(f"[NINE-FACE] 超限: {r['breaches']}")
    if r.get("alert"):
        print(f"[NINE-FACE] 预算告警已升级: {r['alert'].get('alert_file')}")
    return 1 if r["budget_state"] == "breach" else 0


if __name__ == "__main__":
    sys.exit(main())
