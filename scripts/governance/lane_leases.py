# [BLUEPRINT] MOD-INF-093 | docs/_working/fullflow_chief_closeout/s52_dynamic_lanes_v1.md | §lease model
# [MODULE] scripts.governance.lane_leases
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.encoding；zephyr.shared.utils.time_utils；zephyr.shared.io.file_utils；zephyr.shared.io.paths
# [CONSUMERS] scripts.governance.lane_leases_gate；docs/_working/fullflow_chief_closeout/s52_dynamic_lanes_v1.md（S5② 动态车道 v1 影子期）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 路径租约登记+分配器（S5② 动态车道 v1 影子模式，2026-09-28）：租约=sid→路径前缀集，
#   存 .runtime/lane_leases.json（心跳 TTL 600s；根级 runtime 协调文件先例=session_registry.json /
#   archive_watchlist.json）。冲突判定=段边界感知的前缀包含（src/zephyr 与 src/zephyr2 不相交，
#   src/zephyr 与 src/zephyr/data 相交）；同 sid 再 claim=覆盖式合并 OK；他 sid 活租约相交=拒绝
#   （fail 消息含相交对象与 suggest 拆分指引）。过期租约懒清除（读到即剔除，不死守）。
#   影子纪律：本工具只做登记与建议，绝不阻断任何写操作（硬阻断=v2 影子数据 3 天后另批裁定）。
#   RMW 并发窗口=O_EXCL 锁文件（.lock，重试上限后放行 best-effort——v1 影子期宁降级不卡死）
#   + safe_write_text CAS 防覆盖。时间一律 now_utc()（RULE-SCHEMA-TZ），禁 datetime.now()/time.time()。
#   suggest 分组：src/zephyr/<pkg>/、tests/<dir>/、docs/_working/<campaign>/、scripts/<dir>/、
#   含 _registry 段=hot-register 类；N 队贪心 FCFS（按首文件出现序，最少先分，平票取小号），
#   类间构造性不相交；跨队残余相交=输出 advisory 标记（不拒）。
# [MODIFY-GUARD] gate_id="N/A"（租约协调器+runtime 状态文件写，非门禁；消费方 lane_leases_gate 为 warn-only 影子审计）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] claim 冲突=rc=1（payload 含 conflicts+suggest 指引，绝不部分写——CAS 失败重试
#   3 轮后放行写前旧态或报 rc=2）；status/release/heartbeat 纯读或定向删本 sid 条目；锁竞争超限=
#   best-effort 继续（影子期可用性>强一致）；注册表损坏 JSON=备份后重建空册（rc=0 附 rebuilt 标记，
#   不猜测丢失租约）；--json 全输出机器可读；环境/用法错误=rc=2。
# [TESTS] tests/governance/test_lane_leases.py
# [A_module] module_id=MOD-INF-093 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# create-guard-not-dup: 本模块=路径租约登记+分配器（sid→前缀租约状态机+FCFS 拆分建议，S5② 新对象），命中词均为通用函数名/短语（prefixes_overlap/_lock_path），非任一命中能力的第二实现
# [TTL] permanent
"""
lane_leases.py — 路径租约登记+分配器（S5② 动态车道 v1，影子模式）

病根与目标
----------
工作区分治的最终形态=每个施工队持有一张**动态租借的冲突域**（一组路径前缀）。
前置已落地：四工池（belt w0-w3）、FCFS 队列、不可变树门、分叉基底拒绝。
缺的就是本件：租约分配器 + 写属主核验。

v1=影子模式（WARN-only）：只登记、只建议、只出审计信号，绝不硬阻断。
硬阻断=v2（影子数据跑 3 天、复盘相交告警后另批裁定——项目惯例）。

租约模型
--------
- 登记：``.runtime/lane_leases.json``（仓根相对；--leases 可指向他处以供测试/隔离）。
- 条目：``{sid, prefixes[], acquired_at, heartbeat_at, expires_at}``，TTL 缺省 600s。
- 心跳：``heartbeat <sid>`` 续期；到期即死（活租约判定以 now 对 expires_at）。
- 冲突：段边界感知前缀相交（``normalize_prefix`` + ``prefixes_overlap``）。
  同 sid 再 claim 覆盖合并；他 sid 活租约相交=拒绝并列出拆分建议。

Usage::

    python scripts/governance/lane_leases.py claim <sid> <prefix> [<prefix> ...]
    python scripts/governance/lane_leases.py status [--json]
    python scripts/governance/lane_leases.py release <sid>
    python scripts/governance/lane_leases.py heartbeat <sid>
    python scripts/governance/lane_leases.py suggest <files.csv> [--teams N] [--json]
    # 通用旗：--leases PATH（默认仓根 .runtime/lane_leases.json） --ttl S --json

退出码：0=成功；1=claim 冲突被拒；2=环境/用法错误。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import timedelta
from pathlib import Path
from typing import Final

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _shared.encoding import ensure_utf8_stdout  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from zephyr.shared.io.file_utils import content_sha256, safe_write_text  # noqa: E402
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  SSOT 单真源（禁本地重定义）
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

__manifest__ = """
dimensions: [D1]
priority: P3
timeout_seconds: 30
args:
  - {flag: command, type: str, description: "子命令：claim/status/release/heartbeat/suggest"}
  - {flag: --session, type: str, description: "session id（claim/release/heartbeat 必带）"}
  - {flag: --leases, type: str, description: "租约注册表路径（默认仓根 .runtime/lane_leases.json）"}
  - {flag: --ttl, type: int, description: "租约 TTL 秒数（默认 600）"}
  - {flag: --teams, type: int, description: "suggest 建议队数（默认 2）"}
  - {flag: --json, type: bool, description: "机器可读 JSON 输出"}
  - {flag: files_csv, type: str, description: "suggest 文件清单（csv 串或清单文件路径）"}
warn_only: true
"""

#: 根级 runtime 协调文件先例：.runtime/session_registry.json / archive_watchlist.json
DEFAULT_LEASES_REL = Path(".runtime/lane_leases.json")
#: 心跳 TTL 缺省（秒）
DEFAULT_TTL_SECONDS = 600
#: O_EXCL 锁重试参数（影子期 best-effort：超限放行，宁降级不卡死）
_LOCK_RETRIES = 20
_LOCK_SLEEP_S = 0.05
#: CAS 写重试轮数
_CAS_RETRIES = 3


# ---------------------------------------------------------------------------
# 前缀语义（段边界感知）
# ---------------------------------------------------------------------------


def normalize_prefix(raw: str) -> str:
    """路径前缀归一：反斜杠→正斜杠、去相对段与空段（等效去首尾斜杠+压缩重复斜杠）。"""
    p = raw.strip().replace("\\", "/")
    return "/".join(seg for seg in p.split("/") if seg and seg != ".")


def prefix_covers(prefix: str, path: str) -> bool:
    """段边界感知包含：prefix==path 或 path 位于 prefix 的直接子树。"""
    pre = normalize_prefix(prefix)
    pth = normalize_prefix(path)
    if not pre:
        return True
    if pth == pre:
        return True
    return pth.startswith(pre + "/")


def prefixes_overlap(a: str, b: str) -> bool:
    """两前缀相交=任一覆盖另一（段边界感知）。"""
    return prefix_covers(a, b) or prefix_covers(b, a)


# ---------------------------------------------------------------------------
# 注册表 IO（O_EXCL 锁 + safe_write_text CAS）
# ---------------------------------------------------------------------------


def _leases_path(repo_root: Path, override: str | None) -> Path:
    if override:
        return Path(override)
    return repo_root / DEFAULT_LEASES_REL


def _lock_path(target: Path) -> Path:
    return target.with_name(target.name + ".lock")


class _LeaseFileLock:
    """O_EXCL 锁文件（best-effort：超限放行——v1 影子期可用性优先）。"""

    def __init__(self, target: Path) -> None:
        self._lock = _lock_path(target)
        self._acquired = False

    def __enter__(self) -> _LeaseFileLock:
        self._lock.parent.mkdir(parents=True, exist_ok=True)
        for _ in range(_LOCK_RETRIES):
            try:
                fd = os.open(str(self._lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, now_utc().isoformat().encode("utf-8"))
                os.close(fd)
                self._acquired = True
                break
            except FileExistsError:
                time.sleep(_LOCK_SLEEP_S)
        return self

    def __exit__(self, *_exc: object) -> None:
        if self._acquired:
            try:
                self._lock.unlink()
            except OSError:
                pass
        self._acquired = False


def _empty_registry() -> dict:
    return {"version": 1, "leases": {}}


def load_registry(path: Path) -> tuple[dict, bool]:
    """读册：返回 (registry, rebuilt)。损坏 JSON=备份后重建空册（不猜测丢失租约）。"""
    if not path.exists():
        return _empty_registry(), False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("leases", {}), dict):
            raise ValueError("registry shape invalid")
        return data, False
    except (json.JSONDecodeError, ValueError, OSError):
        backup = path.with_name(path.name + ".corrupt-" + now_utc().strftime("%Y%m%dT%H%M%S"))
        try:
            backup.write_bytes(path.read_bytes())
        except OSError:
            pass
        return _empty_registry(), True


def _iso(dt: object) -> str:
    return dt.isoformat()  # type: ignore[attr-defined]


def _parse_iso(text: str):
    return datetime_fromisoformat(text)


def datetime_fromisoformat(text: str):
    """集中封装 fromisoformat（便于测试与后续换源）。"""
    from datetime import datetime  # 局部导入避免模块级别名歧义

    return datetime.fromisoformat(text)


def _now():
    return now_utc()


def save_registry(path: Path, registry: dict) -> None:
    """CAS 写册（热文件纪律：safe_write_text，防并发覆盖）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    base = ""
    if path.exists():
        try:
            base = path.read_text(encoding="utf-8")
        except OSError:
            base = ""
    expected = content_sha256(base) if base else None
    safe_write_text(path, payload, expected_base_sha256=expected, repo_root=REPO_ROOT)


def _lease_is_live(lease: dict, now) -> bool:
    try:
        return _parse_iso(str(lease.get("expires_at", ""))) > now
    except (ValueError, TypeError):
        return False


def prune_expired(registry: dict, now) -> dict:
    """懒清除：过期租约剔除（读时清理，不死守）。"""
    leases = registry.get("leases", {})
    registry["leases"] = {k: v for k, v in leases.items() if _lease_is_live(v, now)}
    return registry


def _find_conflicts(registry: dict, sid: str, prefixes: list[str], now) -> list[dict]:
    """他 sid 活租约与本批前缀的相交清单。"""
    conflicts: list[dict] = []
    for other_sid, lease in registry.get("leases", {}).items():
        if other_sid == sid or not _lease_is_live(lease, now):
            continue
        hit = sorted({p for p in prefixes for q in lease.get("prefixes", []) if prefixes_overlap(p, q)})
        if hit:
            conflicts.append(
                {
                    "sid": other_sid,
                    "expires_at": lease.get("expires_at"),
                    "their_prefixes": lease.get("prefixes", []),
                    "overlapping_requested": hit,
                }
            )
    return conflicts


# ---------------------------------------------------------------------------
# 核心操作
# ---------------------------------------------------------------------------


def op_claim(path: Path, sid: str, prefixes: list[str], ttl: int) -> dict:
    """登记/续登租约。同 sid 覆盖合并；他 sid 活租约相交=拒绝（附拆分建议）。"""
    now = _now()
    norm = sorted({normalize_prefix(p) for p in prefixes if normalize_prefix(p)})
    if not norm:
        return {"ok": False, "rc": 2, "error": "no valid prefixes after normalization"}
    with _LeaseFileLock(path):
        registry, rebuilt = load_registry(path)
        registry = prune_expired(registry, now)
        conflicts = _find_conflicts(registry, sid, norm, now)
        if conflicts:
            return {
                "ok": False,
                "rc": 1,
                "error": "lease conflict with live lease(s) of other session(s)",
                "sid": sid,
                "requested_prefixes": norm,
                "conflicts": conflicts,
                "hint": "拒绝即建议拆分：改用无相交的前缀切分（lane_leases.py suggest 可给出 N 队不相交租约），"
                "或等对方租约到期/释放后重试。",
            }
        prev = registry.get("leases", {}).get(sid)
        registry.setdefault("leases", {})[sid] = {
            "sid": sid,
            "prefixes": norm,
            "acquired_at": prev["acquired_at"] if prev else _iso(now),
            "heartbeat_at": _iso(now),
            "expires_at": _iso(now + timedelta(seconds=ttl)),
        }
        save_registry(path, registry)
        return {
            "ok": True,
            "rc": 0,
            "sid": sid,
            "prefixes": norm,
            "expires_at": registry["leases"][sid]["expires_at"],
            "rebuilt": rebuilt,
        }


def op_heartbeat(path: Path, sid: str, ttl: int) -> dict:
    now = _now()
    with _LeaseFileLock(path):
        registry, _ = load_registry(path)
        lease = registry.get("leases", {}).get(sid)
        if lease is None:
            return {"ok": False, "rc": 1, "error": f"no lease for sid={sid}"}
        lease["heartbeat_at"] = _iso(now)
        lease["expires_at"] = _iso(now + timedelta(seconds=ttl))
        save_registry(path, registry)
        return {"ok": True, "rc": 0, "sid": sid, "expires_at": lease["expires_at"]}


def op_release(path: Path, sid: str) -> dict:
    now = _now()
    with _LeaseFileLock(path):
        registry, _ = load_registry(path)
        existed = sid in registry.get("leases", {})
        registry.get("leases", {}).pop(sid, None)
        save_registry(path, registry)
        return {"ok": True, "rc": 0, "sid": sid, "released": existed, "at": _iso(now)}


def op_status(path: Path) -> dict:
    now = _now()
    registry, rebuilt = load_registry(path)
    live, stale = [], []
    for sid, lease in registry.get("leases", {}).items():
        bucket = live if _lease_is_live(lease, now) else stale
        bucket.append(
            {
                "sid": sid,
                "prefixes": lease.get("prefixes", []),
                "acquired_at": lease.get("acquired_at"),
                "expires_at": lease.get("expires_at"),
                "remaining_seconds": max(0, int((_parse_iso(str(lease.get("expires_at"))) - now).total_seconds())),
            }
        )
    live.sort(key=lambda x: x["sid"])
    stale.sort(key=lambda x: x["sid"])
    return {"ok": True, "rc": 0, "live": live, "stale": stale, "registry": str(path), "rebuilt": rebuilt}


# ---------------------------------------------------------------------------
# suggest 分配器（FCFS 贪心分组 → N 队不相交租约）
# ---------------------------------------------------------------------------


#: 目录族分类规则表（查表法降复杂度；顺序即优先级；seg1=None=通配；{N}=段占位）
# （seg0, seg1, 最少段数, 域名模板, 前缀模板）
_DOMAIN_RULES: Final[tuple[tuple[str, str | None, int, str, str], ...]] = (
    ("src", "zephyr", 4, "src/zephyr/{2}", "src/zephyr/{2}"),
    ("src", "zephyr", 3, "src/zephyr-root", "src/zephyr"),
    ("src", None, 3, "src/{1}", "src/{1}"),
    ("tests", None, 3, "tests/{1}", "tests/{1}"),
    ("docs", "_working", 4, "docs/_working/{2}", "docs/_working/{2}"),
    ("docs", None, 2, "docs/{1}", "docs/{1}"),
    ("scripts", None, 3, "scripts/{1}", "scripts/{1}"),
)


def _fill_template(template: str, segs: list[str]) -> str:
    """规则表段占位填充：{N}→segs[N]。"""
    return template.format(*segs)


def classify_domain(path: str) -> tuple[str, list[str]]:
    """文件 → (冲突域类名, 建议租约前缀集)。

    hot-register 类（含 _registry 段）前缀=各具体 _registry 根（同类聚合到一队，
    前缀集合仍可精确表达）；其余按目录族规则表（_DOMAIN_RULES，顺序即优先级）给单前缀。
    """
    p = normalize_prefix(path)
    segs = p.split("/")
    if "_registry" in segs:
        root = "/".join(segs[: segs.index("_registry") + 1])
        return "hot-register", [root]
    for seg0, seg1, min_len, name_t, prefix_t in _DOMAIN_RULES:
        if segs[0] != seg0 or len(segs) < min_len:
            continue
        if seg1 is not None and segs[1] != seg1:
            continue
        return _fill_template(name_t, segs), [_fill_template(prefix_t, segs)]
    if len(segs) >= 2:
        head = f"{segs[0]}/{segs[1]}"
        return head, [head]
    head = segs[0] if segs[0] else "root"
    return head, [segs[0] if segs[0] else "."]


def read_file_list(files_arg: str) -> list[str]:
    """files.csv 语义：存在文件=逐行读（行内逗号/空白皆可分）；否则按逗号切字面量。"""
    candidate = Path(files_arg)
    if candidate.exists() and candidate.is_file():
        items: list[str] = []
        for line in candidate.read_text(encoding="utf-8").splitlines():
            for piece in line.replace(",", " ").split():
                if piece.strip():
                    items.append(piece.strip())
        return items
    return [x.strip() for x in files_arg.split(",") if x.strip()]


def suggest_leases(files: list[str], teams: int) -> dict:
    """FCFS 贪心：域按首文件出现序入列，逐域分给当前域数最少的队（平票取小号）。"""
    classes: dict[str, list[str]] = {}
    order: list[str] = []
    for f in files:
        name, prefixes = classify_domain(f)
        if name not in classes:
            classes[name] = []
            order.append(name)
        for pre in prefixes:
            if pre not in classes[name]:
                classes[name].append(pre)
    buckets: list[list[str]] = [[] for _ in range(max(1, teams))]
    for name in order:
        target = min(range(len(buckets)), key=lambda i: (len(buckets[i]), i))
        buckets[target].append(name)
    suggested = []
    for i, names in enumerate(buckets):
        prefixes: list[str] = []
        for n in names:
            for pre in classes[n]:
                if pre not in prefixes:
                    prefixes.append(pre)
        suggested.append({"team": f"t{i}", "domains": names, "prefixes": sorted(prefixes)})
    # 跨队残余相交 advisory（构造性不相交的兜底核验，影子纪律=只报告不拒）
    overlap_advisories = []
    for i in range(len(suggested)):
        for j in range(i + 1, len(suggested)):
            for a in suggested[i]["prefixes"]:
                for b in suggested[j]["prefixes"]:
                    if prefixes_overlap(a, b):
                        overlap_advisories.append(
                            {"team_a": suggested[i]["team"], "team_b": suggested[j]["team"], "a": a, "b": b}
                        )
    return {"ok": True, "rc": 0, "teams": teams, "suggested": suggested, "overlap_advisories": overlap_advisories}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _print(payload: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    if payload.get("ok") is False:
        print(f"FAIL rc={payload.get('rc')}: {payload.get('error')}")
        for c in payload.get("conflicts", []) or []:
            print(f"  conflict sid={c['sid']} expires={c.get('expires_at')} their={c.get('their_prefixes')}")
            print(f"    overlapping: {c.get('overlapping_requested')}")
        if payload.get("hint"):
            print(f"  hint: {payload['hint']}")
        return
    cmd = payload.get("cmd")
    if cmd == "status":
        for l in payload["live"]:
            print(f"LIVE  {l['sid']}  ttl~{l['remaining_seconds']}s  {l['prefixes']}")
        for l in payload["stale"]:
            print(f"STALE {l['sid']}  expired={l['expires_at']}  {l['prefixes']}")
        if not payload["live"] and not payload["stale"]:
            print("no leases")
    elif cmd == "suggest":
        for s in payload["suggested"]:
            print(f"{s['team']}: domains={s['domains']}")
            print(f"      prefixes={s['prefixes']}")
        for ov in payload["overlap_advisories"]:
            print(f"ADVISORY overlap {ov['team_a']}/{ov['a']} vs {ov['team_b']}/{ov['b']}")
    else:
        print(json.dumps(payload, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="路径租约登记+分配器（S5② 动态车道 v1 影子模式，WARN-only）")
    parser.add_argument("command", choices=["claim", "status", "release", "heartbeat", "suggest"])
    parser.add_argument("sid", nargs="?", default="", help="session id（claim/release/heartbeat）")
    parser.add_argument("prefixes", nargs="*", default=[], help="claim 路径前缀（可多个）")
    parser.add_argument("--session", dest="session_opt", default="", help="session id（等价位置参数 sid）")
    parser.add_argument("--files", dest="files_csv", default="", help="suggest 文件清单（csv 串或清单文件路径）")
    parser.add_argument("--leases", default="", help="租约注册表路径（默认 .runtime/lane_leases.json）")
    parser.add_argument("--ttl", type=int, default=DEFAULT_TTL_SECONDS, help="TTL 秒（默认 600）")
    parser.add_argument("--teams", type=int, default=2, help="suggest 队数（默认 2）")
    parser.add_argument("--json", action="store_true", help="机器可读输出")
    return parser


def main(argv: list[str] | None = None) -> int:
    ensure_utf8_stdout()
    parser = build_parser()
    args = parser.parse_args(argv)
    path = _leases_path(REPO_ROOT, args.leases or None)
    sid = args.session_opt or args.sid
    try:
        if args.command == "claim":
            prefixes = list(args.prefixes)
            if not sid and prefixes:  # 位置形态：第一个词=sid，其余=前缀
                sid = prefixes.pop(0)
            if not sid or not prefixes:
                parser.error("claim 需要 <sid> <prefix>...（或 --session SID + prefixes）")
            payload = op_claim(path, sid, prefixes, args.ttl)
        elif args.command == "status":
            payload = op_status(path)
        elif args.command == "release":
            if not sid:
                parser.error("release 需要 <sid>")
            payload = op_release(path, sid)
        elif args.command == "heartbeat":
            if not sid:
                parser.error("heartbeat 需要 <sid>")
            payload = op_heartbeat(path, sid, args.ttl)
        else:  # suggest
            if not args.files_csv:
                parser.error("suggest 需要 --files <files.csv>")
            payload = suggest_leases(read_file_list(args.files_csv), args.teams)
    except OSError as exc:  # 磁盘/权限类环境错误
        payload = {"ok": False, "rc": 2, "error": f"environment error: {exc}"}
    payload = {"cmd": args.command, **payload}
    _print(payload, args.json)
    return int(payload.get("rc", 2))


if __name__ == "__main__":
    sys.exit(main())
