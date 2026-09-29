# [BLUEPRINT] MOD-GOV-CHIEFLEASE | docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml | 裁定#415 唯一在任总包
# [MODULE] scripts.governance.chief_lease
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib-only (argparse/json/os/sys/time/datetime/pathlib) — 零仓库内依赖，任何会话裸 Python 可执行
# [CONSUMERS] docs/_working/fullflow_chief_closeout/chief_lease_protocol.md | 各战役会话 bootstrap（startup 时 claim）| 未来 chief bootstrap 模板
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 裁定#415 机械化：租约唯一真源 .runtime/chief_lease.json（sid/claimed_at/last_heartbeat/ttl_seconds=600）；claim 仅当无活租约（last_heartbeat 距 now < TTL）时成功，否则拒绝并回报在任 holder sid；同 sid 重复 claim=幂等续期；heartbeat 仅 holder 可续（改写 last_heartbeat）；release 仅 holder 可释（过期租约 holder 仍可释=清尸）；TTL 过期=自动让位（先到先得，首个 claim 者胜）；损坏文件自愈（备份 .corrupt-<ts>.bak 后按空位处理）；全部写操作经 <path>.lock O_EXCL 互斥（stale 锁 >30s 自愈）+ os.replace 原子落盘；纯 stdlib
# [MODIFY-GUARD] gate_id="N/A"（运行时状态文件写，非门禁；自身不做门禁裁决，只做租约仲裁）
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] rc=0 成功；rc=1 仲裁失败（lease_held/not_holder/no_lease/lease_expired，--json 模式带 reason+holder 字段）；rc=2 用法/环境错误；损坏 JSON 不抛异常——自动备份+按空位续走（status 报 NONE）；锁竞争超时（>5s）rc=2 fail-closed 不猜测
# [TESTS] tests/governance/test_chief_lease.py
# [A_module] module_id=MOD-GOV-CHIEFLEASE | layer=module | stability=stable | safety=M | ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  合法 manual CLI 仲裁工具（裁定#415）：会话 bootstrap 按需 claim/heartbeat/release/status，非常驻自动运行器
# create-guard-not-dup: 本模块是裁定#415 唯一在任总包租约仲裁器（会话级领导权 claim/heartbeat/release 互斥语义+TTL 自动让位），非 depgraph module_id 修复器/进程存活探测/策略偏离监控的第二实现——CREATE-GUARD 命中词仅时间性措辞（atomic write json / is live）
"""chief_lease.py — 总指挥租约仲裁器（裁定#415 机械化，2026-09-28）

自动降格语义（裁定#415，册载 2026-09-28）::

    自称总指挥 = 职位申请，非任命；
    查册有活租约 = 自动为工序队；
    无租约 = 先 claim，claim 成功才升格总包。

根因：每份复制粘贴指令都写"你是总指挥"，导致每个会话都自认为是唯一总包。
本工具把"在任"从措辞断言变成可机判的租约状态：唯一真源
``.runtime/chief_lease.json``（sid / claimed_at / last_heartbeat / ttl_seconds=600）。

判定规则
--------
- LIVE 租约 = ``last_heartbeat`` 距 now < ``ttl_seconds``（默认 600s）。
- ``claim``：无 LIVE 租约才成功（过期租约=自动让位，先到先得）；已有 LIVE 租约
  则拒绝并回报在任 holder sid（拒绝≠冲突事故，=自动降格为工序队的机判信号）。
  同 sid 重复 claim = 幂等续期（崩溃重入安全）。
- ``heartbeat``：仅 holder 可续；续期=改写 last_heartbeat，TTL 不变。
  租约已过期时 heartbeat 失败（lease_expired）——须重新 claim。
- ``release``：仅 holder 可释；holder 释过期租约合法（清尸）；空位 release 失败。
- 损坏文件自愈：JSON 不可解析 → 备份为 ``chief_lease.json.corrupt-<UTC时间戳>.bak``
  后按空位处理（首个 claim 者胜），绝不因脏文件卡死领导权仲裁。
- 并发安全：所有变更经 ``<lease>.lock`` O_EXCL 独占锁（stale 锁 >30s 自愈）+
  ``os.replace`` 原子写；status 读路径同样过锁，保证所见即一致快照。

Usage::

    python scripts/governance/chief_lease.py claim <sid>     # 申请总指挥（无活租约才成功）
    python scripts/governance/chief_lease.py heartbeat <sid> # 在任心跳续期
    python scripts/governance/chief_lease.py release <sid>   # 交班组权（收尾必做）
    python scripts/governance/chief_lease.py status          # 打印在任总包或 NONE

全局旗标：``--json``（机读输出）；``--path``（租约文件重定向，测试专用）；
``--ttl``（claim 时自定义租约时长，默认 600s）。

退出码：0=成功；1=仲裁失败（含租约被他手持有）；2=用法/环境错误。

时间语义：全部 UTC 显式时区（RULE-SCHEMA-TZ）；库层 ``now`` 参数可注入冻结时钟
（测试零 sleep）。未来战役会话 bootstrap 时先 ``claim``：成功=总包，失败=按
holder sid 对齐工序队（三层治理地图见
docs/_working/fullflow_chief_closeout/chief_lease_protocol.md）。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

__manifest__ = """
module: scripts.governance.chief_lease
purpose: 总指挥租约仲裁器（裁定#415 唯一在任总包机械化）
ruling: 裁定#415
lease_file: .runtime/chief_lease.json
default_ttl_seconds: 600
commands: [claim, heartbeat, release, status]
"""

# ---------------------------------------------------------------------------
# 常量与路径
# ---------------------------------------------------------------------------

DEFAULT_TTL_SECONDS = 600
LOCK_STALE_SECONDS = 30
LOCK_POLL_INTERVAL = 0.05
LOCK_TIMEOUT_SECONDS = 5.0

_REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LEASE_PATH = _REPO_ROOT / ".runtime" / "chief_lease.json"


def _utcnow() -> datetime:
    """显式时区 UTC now（RULE-SCHEMA-TZ；测试经 now 参数注入冻结时钟，不走此处）。"""
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def _parse_iso(value: str) -> datetime:
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:  # 容错历史 naive 时间戳：按 UTC 解释
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


# ---------------------------------------------------------------------------
# 锁（O_EXCL 独占 + stale 自愈）
# ---------------------------------------------------------------------------


class _LeaseLock:
    """租约文件互斥锁：O_EXCL 独占创建，stale 锁自动清障。"""

    def __init__(self, lease_path: Path) -> None:
        self.lock_path = lease_path.with_name(lease_path.name + ".lock")

    def __enter__(self) -> "_LeaseLock":
        deadline = time.monotonic() + LOCK_TIMEOUT_SECONDS
        while True:
            try:
                fd = os.open(str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode("ascii"))
                os.close(fd)
                return self
            except FileExistsError:
                self._heal_stale_lock()
                if time.monotonic() > deadline:
                    raise TimeoutError(f"chief lease lock busy: {self.lock_path}")
                time.sleep(LOCK_POLL_INTERVAL)

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            self.lock_path.unlink()
        except FileNotFoundError:
            pass

    def _heal_stale_lock(self) -> None:
        try:
            age = time.time() - self.lock_path.stat().st_mtime
            if age > LOCK_STALE_SECONDS:
                self.lock_path.unlink()
        except FileNotFoundError:
            pass


# ---------------------------------------------------------------------------
# 租约读写（原子落盘 + 损坏自愈）
# ---------------------------------------------------------------------------


def _atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(path.name + f".tmp-{os.getpid()}")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(str(tmp_path), str(path))


def _heal_corrupt(path: Path) -> None:
    """损坏租约文件备份后移除（自愈=按空位处理，绝不卡死仲裁）。"""
    stamp = _iso(_utcnow()).replace(":", "").replace("+", "p")
    backup = path.with_name(path.name + f".corrupt-{stamp}.bak")
    try:
        os.replace(str(path), str(backup))
    except FileNotFoundError:
        pass


def _load_lease(path: Path) -> dict | None:
    """读租约；缺失/损坏返回 None（损坏先备份自愈）。"""
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    try:
        lease = json.loads(raw)
        if not isinstance(lease, dict) or not isinstance(lease.get("sid"), str):
            raise ValueError("lease schema invalid")
        _parse_iso(lease["last_heartbeat"])  # 可解析性预检
    except (ValueError, KeyError, TypeError):
        _heal_corrupt(path)
        return None
    lease.setdefault("ttl_seconds", DEFAULT_TTL_SECONDS)
    return lease


def _is_live(lease: dict, now: datetime) -> bool:
    age = now - _parse_iso(lease["last_heartbeat"])
    return timedelta(0) <= age < timedelta(seconds=int(lease["ttl_seconds"]))


def _result(ok: bool, action: str, **fields) -> dict:
    out: dict = {"ok": ok, "action": action}
    out.update(fields)
    return out


# ---------------------------------------------------------------------------
# 库层 API（now 参数可注入冻结时钟）
# ---------------------------------------------------------------------------


def claim(
    sid: str,
    path: str | Path | None = None,
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
    now: datetime | None = None,
) -> dict:
    """申请总指挥：无 LIVE 租约才成功；LIVE 被他手持有则拒绝并回报 holder。"""
    lease_path = Path(path) if path else DEFAULT_LEASE_PATH
    now = now or _utcnow()
    with _LeaseLock(lease_path):
        lease = _load_lease(lease_path)
        if lease is not None and _is_live(lease, now):
            if lease["sid"] == sid:  # 同 sid 幂等续期（崩溃重入安全）
                lease["last_heartbeat"] = _iso(now)
                _atomic_write_json(lease_path, lease)
                return _result(True, "claim", chief=sid, reclaimed=True, lease=lease)
            return _result(
                False,
                "claim",
                reason="lease_held",
                holder=lease["sid"],
                last_heartbeat=lease["last_heartbeat"],
                ttl_seconds=lease["ttl_seconds"],
            )
        fresh = {
            "sid": sid,
            "claimed_at": _iso(now),
            "last_heartbeat": _iso(now),
            "ttl_seconds": int(ttl_seconds),
        }
        _atomic_write_json(lease_path, fresh)
        return _result(True, "claim", chief=sid, lease=fresh)


def heartbeat(
    sid: str,
    path: str | Path | None = None,
    now: datetime | None = None,
) -> dict:
    """在任心跳：仅 holder 可续（改写 last_heartbeat，TTL 不变）。"""
    lease_path = Path(path) if path else DEFAULT_LEASE_PATH
    now = now or _utcnow()
    with _LeaseLock(lease_path):
        lease = _load_lease(lease_path)
        if lease is None:
            return _result(False, "heartbeat", reason="no_lease")
        if lease["sid"] != sid:
            return _result(False, "heartbeat", reason="not_holder", holder=lease["sid"])
        if not _is_live(lease, now):
            return _result(False, "heartbeat", reason="lease_expired")
        lease["last_heartbeat"] = _iso(now)
        _atomic_write_json(lease_path, lease)
        return _result(True, "heartbeat", chief=sid, last_heartbeat=lease["last_heartbeat"])


def release(
    sid: str,
    path: str | Path | None = None,
    now: datetime | None = None,
) -> dict:
    """交班组权：仅 holder 可释；过期租约 holder 仍可释（清尸）。"""
    lease_path = Path(path) if path else DEFAULT_LEASE_PATH
    now = now or _utcnow()
    with _LeaseLock(lease_path):
        lease = _load_lease(lease_path)
        if lease is None:
            return _result(False, "release", reason="no_lease")
        if lease["sid"] != sid:
            return _result(False, "release", reason="not_holder", holder=lease["sid"])
        expired = not _is_live(lease, now)
        try:
            lease_path.unlink()
        except FileNotFoundError:
            pass
        return _result(True, "release", chief=sid, expired=expired)


def status(path: str | Path | None = None, now: datetime | None = None) -> dict:
    """查册：回报在任总包（活租约 holder）或 NONE（空位/过期/损坏自愈后）。"""
    lease_path = Path(path) if path else DEFAULT_LEASE_PATH
    now = now or _utcnow()
    with _LeaseLock(lease_path):
        lease = _load_lease(lease_path)
    if lease is None:
        return _result(True, "status", chief=None, state="vacant")
    if _is_live(lease, now):
        age = (now - _parse_iso(lease["last_heartbeat"])).total_seconds()
        return _result(
            True,
            "status",
            chief=lease["sid"],
            state="held",
            last_heartbeat=lease["last_heartbeat"],
            ttl_seconds=lease["ttl_seconds"],
            age_seconds=round(age, 3),
        )
    return _result(
        True,
        "status",
        chief=None,
        state="expired",
        last_heartbeat=lease["last_heartbeat"],
        holder=lease["sid"],
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _ensure_utf8_stdout() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    except (AttributeError, ValueError):
        pass


def _print(result: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    action = result.get("action")
    if action == "status":
        chief = result.get("chief")
        if chief:
            print(f"CHIEF: {chief} (last_heartbeat={result.get('last_heartbeat')}, ttl={result.get('ttl_seconds')}s)")
        else:
            print(f"CHIEF: NONE ({result.get('state', 'vacant')})")
        return
    label = {"claim": "CLAIM", "heartbeat": "HEARTBEAT", "release": "RELEASE"}.get(action, action or "?")
    if result.get("ok"):
        print(f"{label} OK chief={result.get('chief')}")
    else:
        holder = result.get("holder")
        suffix = f" holder={holder}" if holder else ""
        print(f"{label} REJECTED reason={result.get('reason')}{suffix}")


def main(argv: list[str] | None = None) -> int:
    _ensure_utf8_stdout()
    # 全局旗标挂 parent parser（SUPPRESS 缺省）→ 子命令前后均可放置且互不覆盖。
    # 注意：勿用 set_defaults——它会改写与 subparser 共享的 action.default，
    # 击穿 SUPPRESS 导致子命名空间回填默认值、顶层旗标被清零；改用 getattr 取值。
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help="机读 JSON 输出")
    common.add_argument(
        "--path", default=argparse.SUPPRESS, help="租约文件路径重定向（默认 <repo>/.runtime/chief_lease.json）"
    )
    common.add_argument("--ttl", type=int, default=argparse.SUPPRESS, help="claim 租约时长秒数（默认 600）")
    parser = argparse.ArgumentParser(
        prog="chief_lease.py",
        description="总指挥租约仲裁器（裁定#415：唯一在任总包，claim 成功才升格）",
        parents=[common],
    )
    sub = parser.add_subparsers(dest="command", required=True)
    p_claim = sub.add_parser("claim", parents=[common], help="申请总指挥（无活租约才成功）")
    p_claim.add_argument("sid")
    p_heartbeat = sub.add_parser("heartbeat", parents=[common], help="在任心跳续期")
    p_heartbeat.add_argument("sid")
    p_release = sub.add_parser("release", parents=[common], help="交班组权")
    p_release.add_argument("sid")
    sub.add_parser("status", parents=[common], help="查册：在任总包或 NONE")
    args = parser.parse_args(argv)
    as_json = getattr(args, "json", False)
    lease_path_arg = getattr(args, "path", None)
    ttl_arg = getattr(args, "ttl", DEFAULT_TTL_SECONDS)

    try:
        if args.command == "claim":
            result = claim(args.sid, path=lease_path_arg, ttl_seconds=ttl_arg)
        elif args.command == "heartbeat":
            result = heartbeat(args.sid, path=lease_path_arg)
        elif args.command == "release":
            result = release(args.sid, path=lease_path_arg)
        else:
            result = status(path=lease_path_arg)
    except TimeoutError as exc:
        result = _result(False, args.command, reason="lock_timeout", detail=str(exc))
        _print(result, as_json)
        return 2
    _print(result, as_json)
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
