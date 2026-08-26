# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §audit-jsonl-writer
# [MODULE] zephyr.shared.io.audit_jsonl_writer
# [DOMAIN] D_SHARED
# [DEPENDENCIES] 无（纯 stdlib）
# [CONSUMERS] scripts.ops_guard; zephyr.gov_enforcement.rule_bridge.git_commit_gateway; zephyr.gov_enforcement.commit_gates.foreign_change_gate; zephyr.shared.io.file_utils
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 审计写入永不抛异常（失败返回 False 由调用方计数）；轮转保留 backup_count 份历史段不物理删除（B-016 合规：旧段改名保留而非清理）
# [MODIFY-GUARD] 轮转命名约定 <filename>.<N>（RotatingFileHandler 同型后缀）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 任何异常→返回 False（审计不阻断主链路）
# [TESTS] tests/shared/test_audit_jsonl_writer.py
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""audit_jsonl_writer.py — 审计 jsonl 统一写入助手（批5c，2026-08-26）。

治本动机
--------
.runtime/gate_audit/ 下 11 个 jsonl 全部裸 ``open(..., "a")`` 追加、零大小上限、
零轮转、零采样；GATE-RUNTIME-CLEANUP 显式豁免 *.jsonl（"append-only 审计日志"）
——实证 ops_guard_delete.jsonl 42 小时膨胀至 3.7GB（333 万条），
worktree_status_snapshots.jsonl 449 万行、post_claim_modifications.jsonl 175 万行
同型炸弹。月增 ~50GB/文件 不可持续。

设计（第一性）
--------------
审计日志的价值 = 异常取证 + 覆盖率证明。两者都不要求单文件无界——
写前大小检查 + 阈值轮转（旧段 ``.1/.2/...`` 移位保留，不物理删除）即可同时满足：
- 近期事件（取证主需求）始终在当前段；
- 历史事件在移位段内仍可检索（B-016"禁止 AI 自动清理未归档审计"合规——
  轮转是改名保留而非删除；超出 backup_count 的最老段才丢弃，与项目既有
  RotatingFileHandler 10MB×5 先例（scheduler/tick_subscriber/ch_health_probe）同型）；
- 写入失败永不抛异常（审计不阻断主链路，与 ops_guard audit_delete 语义一致）。

Usage
-----
::

    from zephyr.shared.io.audit_jsonl_writer import append_audit_jsonl

    ok = append_audit_jsonl(audit_dir, "ops_guard_delete.jsonl", record)
    if not ok:
        stats["audit_failed"] += 1
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Final

#: 单段大小上限（50MB——按 ops_guard 观测期 ~1.1KB/条 计约 4.5 万条/段，
#: 敏感区全量+异常事件密度下足够覆盖数周取证窗口）
DEFAULT_MAX_BYTES: Final = 50 * 1024 * 1024

#: 历史段保留份数（当前段 + 3 历史段 ≈ 200MB/文件 硬上限）
DEFAULT_BACKUP_COUNT: Final = 3


def _rotate(path: Path, backup_count: int) -> None:
    """移位轮转：最老段丢弃，其余段序号 +1，当前段变 .1。

    命名约定 ``<filename>.<N>``（RotatingFileHandler 同型）：N 越大越老。
    单步 rename 失败即中断（保现场优先于保轮转——残留的重复段不影响追加写）。
    """
    oldest = path.with_name(f"{path.name}.{backup_count}")
    if oldest.exists():
        oldest.unlink()  # 超出保留份数的最老段才物理丢弃
    for n in range(backup_count - 1, 0, -1):
        src = path.with_name(f"{path.name}.{n}")
        if src.exists():
            src.rename(path.with_name(f"{path.name}.{n + 1}"))
    path.rename(path.with_name(f"{path.name}.1"))


def append_audit_jsonl(
    audit_dir: Path,
    filename: str,
    record: dict,
    *,
    max_bytes: int = DEFAULT_MAX_BYTES,
    backup_count: int = DEFAULT_BACKUP_COUNT,
) -> bool:
    """审计记录追加落盘（jsonl 一行一条）+ 写前大小轮转。

    Args:
        audit_dir: 审计目录（不存在则创建；创建失败返回 False）。
        filename: 审计文件名（如 ops_guard_delete.jsonl）。
        record: 审计记录（json.dumps(ensure_ascii=False) 序列化）。
        max_bytes: 单段大小上限——当前段 ≥ 阈值时先轮转再写入。
        backup_count: 历史段保留份数（移位保留，最老段超出才丢弃）。

    Returns:
        True=落盘成功；False=任何环节失败（调用方计数 audit_failed，
        审计永不阻断主链路）。
    """
    try:
        audit_dir.mkdir(parents=True, exist_ok=True)
        path = audit_dir / filename
        try:
            if path.exists() and path.stat().st_size >= max_bytes:
                _rotate(path, backup_count)
        except OSError:
            pass  # 轮转失败不阻断写入（保追加优先）
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return True
    except Exception:  # noqa: BLE001 — 审计写入永不阻断主链路（调用方计数失败）
        return False
