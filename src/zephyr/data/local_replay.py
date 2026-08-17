# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.local_replay
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.shared.io.paths
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 本地落盘文件原子写入（先写.tmp再rename）; manifest追加模式（JSONL）; 回灌成功后删除文件+manifest条目; 回灌失败保留文件等下次重试; 回灌使用manifest保存的cols_clause(不重新查询表列,防列数不匹配); 回灌传create_fallback=False防重复落盘
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] save_fallback永不抛异常（写入失败log+返回False）; replay_batch失败返回False不抛; has_backlog返回bool不抛
# [TESTS] tests/zephyr/data/test_local_replay.py
# [A_module] module_id=MOD-GOV-local_replay | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

# 默认库名（从环境变量读取，与 config/.env.clickhouse 的 CLICKHOUSE_DATABASE 一致）
# 用途：历史积压 manifest 可能有不带 db. 前缀的裸表名，回灌时补全为 <db>.<table>
# 治本：不再硬编码 "c1_market."，支持未来 c3_fundamental 等多库场景（裁定 #ARCH-CH-013 Phase 2）
# 注：模块级常量是测试钉住的 monkeypatch 扩展缝（test_local_replay），保持常量形态。
_DEFAULT_DB = os.environ.get("CLICKHOUSE_DATABASE", "c1_market")


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
        with _manifest_lock, open(_MANIFEST_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        log.warning(
            "local_fallback: %s 落盘 %d 行到 %s（CH 不可用，数据保留待回灌）",
            table,
            rows,
            filename,
        )
        return True
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        log.error("local_fallback: 落盘失败 %s: %s", table, e)
        return False


def has_backlog() -> bool:
    """是否有积压的待回灌文件。"""
    try:
        if not _MANIFEST_PATH.exists():
            return False
        return _MANIFEST_PATH.stat().st_size > 0
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return False


def get_backlog_summary() -> dict[str, int]:
    """获取积压摘要：{table: pending_rows}。"""
    summary: dict[str, int] = {}
    try:
        if not _MANIFEST_PATH.exists():
            return summary
        with _manifest_lock, open(_MANIFEST_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                table = entry["table"]
                summary[table] = summary.get(table, 0) + entry.get("rows", 0)
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        log.warning("get_backlog_summary 读取 manifest 失败: %s", e)
    return summary


def _read_manifest() -> list[dict]:
    """读取 manifest 全部条目（线程安全）。"""
    entries: list[dict] = []
    if not _MANIFEST_PATH.exists():
        return entries
    with _manifest_lock, open(_MANIFEST_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                log.warning("local_replay: manifest 行解析失败，跳过: %s", line[:100])
    return entries


def read_manifest() -> list[dict]:
    """读取 manifest 全部条目（公共接口，R5: 消除测试私有访问）。"""
    return _read_manifest()


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
        # 回灌时使用 manifest 中保存的 cols_clause（落盘时确定，与 TSV 字段数匹配）。
        # 仅在 cols_clause 为 None/""/"*"/缺失时才让 ch_writer 重新查询表列。
        # 原因：get_insert_columns 返回全部可插入列（含 DEFAULT），但 TSV 数据
        # 可能不含 DEFAULT 列的值，导致 INSERT 列数(7) > TSV 字段数(5) → Code 27。
        # 使用保存的 cols_clause 确保 INSERT 列数与 TSV 字段数一致。
        # 2026-08-09: "*" 已废弃（生成非法 SQL），"" 表示无列子句（CH 按全列插入），
        # 两者都意味着 TSV 列数可能与表列数不匹配，回灌时重新查询表列。
        # create_fallback=False：回灌失败时不创建新 fallback 文件，避免无限复制 duplicates。
        # 表名前缀修正：历史积压可能有不带 db. 前缀的裸表名，补全为默认库前缀
        # （裁定 #ARCH-CH-013 Phase 2：从 CLICKHOUSE_DATABASE 读取，不再硬编码 c1_market.）
        replay_table = entry["table"]
        if "." not in replay_table:
            replay_table = f"{_DEFAULT_DB}.{replay_table}"
        saved_cols = entry.get("cols_clause")
        replay_cols = saved_cols if saved_cols and saved_cols not in ("*", "") else None
        # 2026-08-09 修复：cols_clause=None 时 get_insert_columns 返回全部可插入列（含
        # DEFAULT），但 TSV 数据可能不含 DEFAULT 列值 → INSERT 列数 > TSV 字段数 → Code 27。
        # 按 TSV 首行字段数截取列清单前 N 列，确保 INSERT 列数 = TSV 字段数。
        if replay_cols is None:
            first_line = tsv_bytes.split(b"\n", 1)[0]
            tsv_ncol = first_line.count(b"\t") + 1
            all_cols_str = ch_writer_mod.get_insert_columns(replay_table)
            if all_cols_str and all_cols_str not in ("*", ""):
                col_names = [c.strip() for c in all_cols_str.strip("()").split(",")]
                if len(col_names) > tsv_ncol:
                    col_names = col_names[:tsv_ncol]
                    replay_cols = "(" + ", ".join(col_names) + ")"
                    log.info(
                        "local_replay: %s cols_clause=None, TSV %d fields, 截取前 %d 列",
                        entry["file"],
                        tsv_ncol,
                        tsv_ncol,
                    )
        ok = ch_writer_mod.write_tsv(
            replay_table,
            replay_cols,
            tsv_bytes,
            timeout=120,
            create_fallback=False,
        )
        if ok:
            file_path.unlink(missing_ok=True)
            log.info("local_replay: %s 回灌成功 (%d 行)", entry["file"], entry.get("rows", 0))
            return "replayed"
        log.warning("local_replay: %s 回灌失败，保留待重试", entry["file"])
        return "failed"
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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
    replayed_files: set[str] = set()
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
                replayed_files.add(entry.get("file"))
            elif status == "skipped":
                # 治本修复 #ARCH-LOCAL-REPLAY-SKIPPED-ORPHAN（2026-07-24）：
                # 文件不存在的 skipped 条目必须从 manifest 移除，否则既不在
                # remaining_entries 也不在 replayed_files，会在后续 manifest 合并
                # 步骤被重新加回，导致积压永不归零（孤儿 manifest 条目永久存在）。
                # skipped 与 replayed 一样从 manifest 移除，但不计入成功计数。
                result.setdefault("skipped", 0)
                result["skipped"] += 1
                replayed_files.add(entry.get("file"))
            elif status == "failed":
                result["failed"] += 1
                remaining_entries.append(entry)
            processed += 1

    # 修复 manifest 覆盖 bug（#ARCH-CH-023 Phase 3）：
    # _replay_one_file 失败时 ch_writer.write_tsv 内部调用 save_fallback
    # 追加新条目到 manifest。直接 _write_manifest(remaining_entries) 会用 "w" 模式
    # 覆盖，丢失循环中新增的 fallback 条目，导致孤儿文件堆积。
    # 修复：重新读取 manifest 合并去重后再写入。
    #
    # #ARCH-CH-023 Phase 3 末尾逻辑 bug 修正（2026-07-22）：
    # 原逻辑将 current_entries 中不在 existing_files 的 entry 全部加回 remaining，
    # 但 current_entries 仍含已成功回灌的条目（manifest 尚未覆盖），导致已回灌
    # entry 被误加回 remaining，remaining 计数错误且 manifest 保留孤儿条目。
    # 修正：用 replayed_files 集合排除已回灌条目，只合并新增的 fallback 条目。
    current_entries = _read_manifest()
    existing_files = {e.get("file") for e in remaining_entries}
    for entry in current_entries:
        f = entry.get("file")
        if f in replayed_files:
            continue
        if f not in existing_files:
            remaining_entries.append(entry)
            existing_files.add(f)
    result["remaining"] = len(remaining_entries)
    _write_manifest(remaining_entries)

    if result["replayed"] > 0:
        log.info(
            "local_replay: 回灌完成 — 成功 %d, 失败 %d, 剩余 %d",
            result["replayed"],
            result["failed"],
            result["remaining"],
        )

    return result
