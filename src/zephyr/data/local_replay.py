# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.local_replay
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.shared.io.paths
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 本地落盘文件原子写入（先写.tmp再rename）; manifest追加模式（JSONL）; 回灌成功后删除文件+manifest条目; 回灌失败保留文件等下次重试
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] save_fallback永不抛异常（写入失败log+返回False）; replay_batch失败返回False不抛; has_backlog返回bool不抛
# [TESTS] tests/zephyr/data/test_local_replay.py
# [A_module] module_id=MOD-L00-004-local-replay | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""本地落盘兜底 + 自动回灌（裁定 #ARCH-CH-013 Phase 1）。

当 ClickHouse 二级降级链（TCP→HTTP）全部失败时（VM/CH 不可达），
ch_writer.write_tsv 将数据写入本地 TSV 文件而非丢弃。
scheduler 启动时 + 每 30 分钟检查并回灌积压文件到 CH。

文件布局：
    data/local_fallback/
        _manifest.jsonl          # 每行一条 JSON：{table, cols_clause, file, rows, ts}
        c1_market__kline_daily/
            20260715_103723_abc123.tsv
        c3_fundamental__news_data/
            20260715_103723_def456.tsv

回灌策略：
    1. 读取 _manifest.jsonl，按 table 分组
    2. 逐文件调用 ch_writer.write_tsv 回灌
    3. 成功则删除文件 + 从 manifest 移除条目
    4. 失败则保留，等下次重试
"""
from __future__ import annotations

import json
import logging
import os
import time
import uuid
from pathlib import Path
from threading import Lock

from zephyr.shared.io.paths import REPO_ROOT

log = logging.getLogger(__name__)

_FALLBACK_DIR = REPO_ROOT / "data" / "local_fallback"
_MANIFEST_PATH = _FALLBACK_DIR / "_manifest.jsonl"
_manifest_lock = Lock()


def _ensure_dir() -> Path:
    """确保落盘目录存在。"""
    _FALLBACK_DIR.mkdir(parents=True, exist_ok=True)
    return _FALLBACK_DIR


def _table_dir(table: str) -> Path:
    """表名转目录名（点号→双下划线）。"""
    safe_name = table.replace(".", "__")
    d = _FALLBACK_DIR / safe_name
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_fallback(table: str, cols_clause: str | None, tsv_bytes: bytes) -> bool:
    """将 TSV 数据落盘到本地文件（TCP+HTTP 均失败时的第三级降级）。

    原子写入：先写 .tmp 文件，再 rename 为 .tsv，避免半写文件。
    追加 manifest 条目（JSONL 格式，加锁防并发冲突）。

    Args:
        table: 完整表名（如 c1_market.kline_daily）
        cols_clause: 列子句（如 "(col1, col2)"），None 时 CH 自动推断
        tsv_bytes: TSV 格式字节数据

    Returns:
        True=落盘成功, False=落盘失败（磁盘满等）
    """
    if not tsv_bytes:
        return True
    try:
        _ensure_dir()
        ts_str = time.strftime("%Y%m%d_%H%M%S")
        uid = uuid.uuid4().hex[:8]
        filename = f"{ts_str}_{uid}.tsv"
        tsv_path = _table_dir(table) / filename
        tmp_path = tsv_path.with_suffix(".tmp")

        # 原子写入：先 .tmp 再 rename
        tmp_path.write_bytes(tsv_bytes)
        tmp_path.rename(tsv_path)

        rows = tsv_bytes.count(b"\n") + (0 if tsv_bytes.endswith(b"\n") else 1)

        # 追加 manifest 条目
        entry = {
            "table": table,
            "cols_clause": cols_clause,
            "file": str(tsv_path.relative_to(_FALLBACK_DIR)),
            "rows": rows,
            "ts": ts_str,
        }
        with _manifest_lock:
            with open(_MANIFEST_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        log.warning(
            "local_fallback: %s 落盘 %d 行到 %s（CH 不可用，数据保留待回灌）",
            table, rows, filename,
        )
        return True
    except Exception as e:
        log.error("local_fallback: 落盘失败 %s: %s", table, e)
        return False


def has_backlog() -> bool:
    """是否有积压的待回灌文件。"""
    try:
        if not _MANIFEST_PATH.exists():
            return False
        return _MANIFEST_PATH.stat().st_size > 0
    except Exception:
        return False


def get_backlog_summary() -> dict[str, int]:
    """获取积压摘要：{table: pending_rows}。"""
    summary: dict[str, int] = {}
    try:
        if not _MANIFEST_PATH.exists():
            return summary
        with _manifest_lock:
            with open(_MANIFEST_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    entry = json.loads(line)
                    table = entry["table"]
                    summary[table] = summary.get(table, 0) + entry.get("rows", 0)
    except Exception as e:
        log.warning("get_backlog_summary 读取 manifest 失败: %s", e)
    return summary


def _read_manifest() -> list[dict]:
    """读取 manifest 全部条目（线程安全）。"""
    entries: list[dict] = []
    if not _MANIFEST_PATH.exists():
        return entries
    with _manifest_lock:
        with open(_MANIFEST_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    log.warning("local_replay: manifest 行解析失败，跳过: %s", line[:100])
    return entries


def _write_manifest(entries: list[dict]) -> None:
    """重写 manifest（只保留未回灌的条目，线程安全）。"""
    with _manifest_lock:
        if entries:
            with open(_MANIFEST_PATH, "w", encoding="utf-8") as f:
                for entry in entries:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        else:
            _MANIFEST_PATH.unlink(missing_ok=True)


def _replay_one_file(entry: dict, ch_writer_mod) -> str:
    """回灌单个文件。返回 'replayed' / 'failed' / 'skipped'。"""
    file_path = _FALLBACK_DIR / entry["file"]
    if not file_path.exists():
        log.warning("local_replay: 文件不存在，跳过: %s", entry["file"])
        return "skipped"
    try:
        tsv_bytes = file_path.read_bytes()
        # 回灌时始终传 None 作为 cols_clause，强制 ch_writer 重新查询表列
        # 原因：落盘时 CH 可能不可用，cols_clause 可能为空/"*"/过期列清单，
        # 直接使用会导致 INSERT 语法错误或列不匹配（裁定 #ARCH-CH-013 Phase 1 根因修复）
        # 表名前缀修正：历史积压可能有不带 db. 前缀的表名，补全为 c1_market. 前缀
        replay_table = entry["table"]
        if "." not in replay_table:
            replay_table = f"c1_market.{replay_table}"
        ok = ch_writer_mod.write_tsv(
            replay_table,
            None,
            tsv_bytes,
            timeout=120,
        )
        if ok:
            file_path.unlink(missing_ok=True)
            log.info("local_replay: %s 回灌成功 (%d 行)", entry["file"], entry.get("rows", 0))
            return "replayed"
        log.warning("local_replay: %s 回灌失败，保留待重试", entry["file"])
        return "failed"
    except Exception as e:
        log.error("local_replay: %s 回灌异常: %s", entry["file"], e)
        return "failed"


def replay_batch(max_files: int = 100) -> dict[str, int]:
    """回灌积压文件到 ClickHouse。

    读取 manifest，逐文件调用 ch_writer.write_tsv 回灌。
    成功的文件删除 + 从 manifest 移除；失败的保留等下次重试。

    Args:
        max_files: 单次最大回灌文件数（避免长时间阻塞 scheduler）

    Returns:
        {"replayed": N, "failed": N, "remaining": N}
    """
    from . import ch_writer

    result = {"replayed": 0, "failed": 0, "remaining": 0}

    entries = _read_manifest()
    if not entries:
        return result

    log.info("local_replay: 开始回灌 %d 个文件（上限 %d）", len(entries), max_files)

    # 按 table 分组（同表的文件合并回灌，减少 INSERT 次数）
    by_table: dict[str, list[dict]] = {}
    for entry in entries:
        by_table.setdefault(entry["table"], []).append(entry)

    remaining_entries: list[dict] = []
    processed = 0

    for table_entries in by_table.values():
        if processed >= max_files:
            remaining_entries.extend(table_entries)
            continue
        for entry in table_entries:
            if processed >= max_files:
                remaining_entries.append(entry)
                continue
            status = _replay_one_file(entry, ch_writer)
            if status == "replayed":
                result["replayed"] += 1
            elif status == "failed":
                result["failed"] += 1
                remaining_entries.append(entry)
            processed += 1

    result["remaining"] = len(remaining_entries)
    _write_manifest(remaining_entries)

    if result["replayed"] > 0:
        log.info(
            "local_replay: 回灌完成 — 成功 %d, 失败 %d, 剩余 %d",
            result["replayed"], result["failed"], result["remaining"],
        )

    return result
