# [BLUEPRINT] MOD-GOV_DRIFT_WATCHDOG | docs/_working/reports/2026-08-27-authz-writeaudit-adjudication.md | §裁定B3
# [MODULE] scripts.governance.collect_write_audit_4663
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.write_audit_daemon; zephyr.shared.io.audit_jsonl_writer
# [CONSUMERS] 计划任务/手工/守护随跑
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读 Security 日志不写；增量采集（RecordNumber 水位线去重）；只收热目录集路径；归因落盘 fail-open
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无 win32evtlog/无权限读 Security 日志 → exit 2 打印原因；单事件解析失败跳过不中断
# [TESTS] tests/governance/test_collect_write_audit_4663.py
# [A_module] module_id=MOD-GOV_DRIFT_WATCHDOG | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""collect_write_audit_4663.py — WriteAudit SACL 精确归因采集器（#ARCH-279 裁定B3）

前置（一次性，Owner 管理员）：scripts/governance/enable_write_audit_sacls.ps1
  ——auditpol 启用 File System 成功审计 + 热目录集 SACL（Everyone 写/删成功）。

本器读 Security 事件日志 4663（对象访问：文件写/删），过滤热目录集路径，
提取精确归因四要素（用户/进程 PID/进程名/访问掩码），经 session_registry
PID→session_id 会话映射后追加进 .runtime/audit/write_audit.jsonl
（exact_attribution=true，source=sacl_4663）——与 WriteAudit 守护的近似归因
记录同流共存，取证时精确记录优先。

增量语义：水位线存 .runtime/write_audit/sacl_collector_state.json
（last_record_number），重复运行零重复记录。

Usage::

    python scripts/governance/collect_write_audit_4663.py            # 增量采集
    python scripts/governance/collect_write_audit_4663.py --max 200  # 限本次最大事件数
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from zephyr.gov_enforcement.rule_bridge.write_audit_daemon import (  # noqa: E402
    _attribute_sessions,
    _load_session_map,
    _rel,
)

_AUDIT_DIR = ".runtime/audit"
_AUDIT_FILE = "write_audit.jsonl"
_STATE_FILE = ".runtime/write_audit/sacl_collector_state.json"

# 热目录集前缀（与 write_audit_daemon._WATCH_SPECS 对齐；相对仓根正斜杠）
_HOT_PREFIXES: tuple[str, ...] = (
    "docs/01_policies_and_standards/_registry/catalogs",
    "docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos",
    ".runtime/quarantine",
)

# 4663 Access Mask 位（写删语义判定）
_ACCESS_WRITE_BITS = (
    0x0002 | 0x0004 | 0x0008 | 0x0010 | 0x0020 | 0x0100
)  # WriteData/AddFile/AppendData/AddSubdir/WriteEA/WriteAttributes
_ACCESS_DELETE_BITS = 0x10000 | 0x100000  # DELETE | WRITE_DAC 族粗判（Delete 单独位 0x10000）


def _load_watermark(root: Path) -> int:
    try:
        return int(json.loads((root / _STATE_FILE).read_text(encoding="utf-8")).get("last_record_number", 0))
    except (OSError, json.JSONDecodeError, ValueError):
        return 0


def _save_watermark(root: Path, record_number: int) -> None:
    try:
        p = root / _STATE_FILE
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"last_record_number": record_number, "updated": time.time()}), encoding="utf-8")
    except OSError:
        pass


def parse_4663_inserts(inserts: list[str], root: Path) -> dict[str, Any] | None:
    """解析 4663 StringInserts → 标准化记录（纯函数，单测友好）。

    4663 布局（Windows 10/11 实测 13 槽位，2026-08-27 dump 实证）：
    0=SubjectSid 1=SubjectUser 2=SubjectDomain 3=LogonId 4=ObjectServer
    5=ObjectType 6=ObjectName 7=HandleId 8=Accesses 列表（%% 占位多行）
    9=AccessMask(hex) 10=ProcessId(hex) 11=ProcessName 12=ResourceAttributes(S:AI)。

    Returns:
        命中热目录集 → 记录 dict；非文件/非热目录/字段不全 → None。
    """
    if len(inserts) < 12:
        return None
    object_type = inserts[5]
    if object_type != "File":
        return None
    object_name = inserts[6]
    rel = _rel(object_name, root)
    if not any(rel.startswith(prefix + "/") or rel == prefix for prefix in _HOT_PREFIXES):
        return None
    try:
        access_mask = int(inserts[9], 16)
    except (ValueError, IndexError):
        access_mask = 0
    op = "delete" if (access_mask & 0x10000) else ("write" if (access_mask & _ACCESS_WRITE_BITS) else "access")
    try:
        proc_pid = int(inserts[10], 16)
    except (ValueError, IndexError):
        proc_pid = 0
    return {
        "path": rel,
        "op": op,
        "sacl": {
            "user": f"{inserts[2]}\\{inserts[1]}",
            "logon_id": inserts[3],
            "process_id": proc_pid,
            "process_name": inserts[11],
            "access_mask": hex(access_mask),
        },
    }


def collect(root: Path, max_events: int = 1000) -> dict[str, int]:
    """增量采集 Security 4663 → write_audit.jsonl。返回统计。"""
    try:
        import win32evtlog  # noqa: PLC0415
    except ImportError:
        print("[FAIL] pywin32 不可用（win32evtlog 缺失）")
        return {"error": 2}

    from zephyr.shared.io.audit_jsonl_writer import append_audit_jsonl  # noqa: PLC0415

    watermark = _load_watermark(root)
    session_map = _load_session_map(root)
    stats = {"read": 0, "matched": 0, "appended": 0, "skipped_old": 0}

    try:
        hand = win32evtlog.OpenEventLog(None, "Security")
    except Exception as e:  # noqa: BLE001 — 无权限等
        print(f"[FAIL] 无法打开 Security 日志（需管理员/审计权限）: {e}")
        return {"error": 2}

    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    newest_seen = watermark
    (root / _AUDIT_DIR).mkdir(parents=True, exist_ok=True)
    try:
        while stats["read"] < max_events:
            events = win32evtlog.ReadEventLog(hand, flags, 0)
            if not events:
                break
            for ev in events:
                stats["read"] += 1
                if ev.RecordNumber <= watermark:
                    stats["skipped_old"] += 1
                    continue
                newest_seen = max(newest_seen, ev.RecordNumber)
                if int(ev.EventID) != 4663:
                    continue
                inserts = list(ev.StringInserts or [])
                rec = parse_4663_inserts(inserts, root)
                if rec is None:
                    continue
                stats["matched"] += 1
                sessions = _attribute_sessions(
                    [{"pid": rec["sacl"]["process_id"], "name": rec["sacl"]["process_name"], "cmdline": ""}],
                    session_map,
                )
                record = {
                    "ts": ev.TimeGenerated.timestamp() if hasattr(ev.TimeGenerated, "timestamp") else time.time(),
                    "path": rec["path"],
                    "op": rec["op"],
                    "hash_before": None,
                    "hash_after": None,
                    "processes": [],
                    "sessions": sessions,
                    "exact_attribution": True,
                    "source": "sacl_4663",
                    "event_record_id": ev.RecordNumber,
                    "sacl": rec["sacl"],
                }
                if append_audit_jsonl(root / _AUDIT_DIR, _AUDIT_FILE, record):
                    stats["appended"] += 1
                if stats["read"] >= max_events:
                    break
    finally:
        win32evtlog.CloseEventLog(hand)
    if newest_seen > watermark:
        _save_watermark(root, newest_seen)
    return stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="WriteAudit SACL 4663 精确归因采集器（#ARCH-279 裁定B3）")
    parser.add_argument("--max", type=int, default=1000, dest="max_events", help="本次最大读取事件数")
    parser.add_argument("--root", default=str(_REPO_ROOT), help="仓库根路径")
    args = parser.parse_args(argv)

    stats = collect(Path(args.root).resolve(), max_events=args.max_events)
    if stats.get("error"):
        return 2
    print(
        f"collect_4663: read={stats['read']} matched={stats['matched']} "
        f"appended={stats['appended']} skipped_old={stats['skipped_old']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
