# [BLUEPRINT] MOD-ALT-EMOTION-INDEX-BUILDER | scripts/data/emotion_index_snapshot.py | emotion_index 表 append-only 每日快照器
# [MODULE] scripts.data.emotion_index_snapshot
# [DOMAIN] D_DATA
# [DEPENDENCIES] stdlib（argparse/hashlib/json/gzip/os/pathlib/datetime）; zephyr.data.ch_reader（严格读通道，失败必抛）;
#                zephyr.data.table_registry（表名真源）; zephyr.shared.utils.time_utils.now_utc
# [CONSUMERS] 手工/日批 CLI（python scripts/data/emotion_index_snapshot.py）; 未来 PIT 读径（pit_state_path）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] append-only 铁律：快照文件一经落盘禁改写禁删除（文件名含秒级时戳，同名已存在=fail-visible 拒写）;
#              manifest.jsonl 只追加; 全表镜像字节保真（components 保持 CH 原串不反序列化）; 零 DB 写
#              （CH 只读 SELECT 经 ch_reader 严格通道，表名经 TableRegistry 派生禁硬编码）; PIT 语义=
#              「created_at 日期 ≤ asof 的最新快照」即 asof 日收盘后可知的全表状态
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH 不可达/查询失败→ch_reader 严格通道异常原样上抛（fail-closed 禁伪造空快照）;
#                  输出目录不可写/同名冲突→RuntimeError; 空 table→拒绝出快照（空镜像是证据污染）
# [TESTS] tests/data/alt_data/test_emotion_index_snapshot.py
# [MODIFY-GUARD] none
# [TTL] permanent
# create-guard-not-dup: emotion_index 落盘快照器（append-only 文件证据面），与 builder/replay（CH 计算与落库面）无功能交集
"""emotion_index_snapshot — c1_market.emotion_index 全表 append-only 每日快照.

病根（fexam emotion_index_exam_v1 PIT-e 实证）：close_final 全史由 2026-09-23 单批 replay
建成，表级可事后改写历史行（pre_open 2026-10-02 双行异值=改写实证），无逐日快照留痕——
PIT 取证缺"当日表态"证据。本件每天对全表做一次全量镜像落盘（gzip JSONL），只增不改，
为未来任何考试/审计提供「asof 日可知状态」的可复算证据。

快照文件：``<out-dir>/emotion_index_<YYYYMMDDTHHMMSSZ>.jsonl.gz``，每行一个 JSON 对象
（全表 8 列原样：trade_date/stage/ts/emotion_index/components(原串)/version/ingest_ts/source）。
台账：``<out-dir>/manifest.jsonl`` 只追加，每行 {file,sha256,rows,...}。

PIT 读径：``pit_state_path(out_dir, asof)`` = created_at 日期 ≤ asof 的最新快照。
约定：日批在每日收盘数据 ingest 之后跑一次（reaper 白名单登记由运维面负责）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: c1_market.emotion_index 全表严格读（ch_reader.query_rows，FINAL 自动注入）
# 层: 算法
# - id: A1
#   name_zh: 行排序规范化（trade_date,stage,ingest_ts）+ 字节保真 JSONL + gzip
# 层: 输出
# - id: O1
#   name: 时戳命名的 append-only 快照文件 + manifest 台账追加行
"""

from __future__ import annotations

import argparse
import datetime
import gzip
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

RUN_ROOT = Path(__file__).resolve().parents[2]
_SRC = RUN_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from zephyr.data import ch_reader  # noqa: E402
from zephyr.data.table_registry import get_registry  # noqa: E402
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

#: 表名真源=TableRegistry（#ARCH-CH-024，禁硬编码）
_TBL_EMOTION_INDEX = get_registry().table("market_emotion_index")

#: 全表镜像 SQL 模板（NO-BARE-SQL：_SQL_* 常量唯一定义点；只读，FINAL 由 ch_reader 注入）
_SQL_SNAPSHOT = (
    "SELECT trade_date, stage, ts, emotion_index, components, version, ingest_ts, source"
    f" FROM {_TBL_EMOTION_INDEX} ORDER BY trade_date, stage, ingest_ts, source"
)

#: 快照行键序（字节保真：components 保持 CH 原串，不反序列化不重排）
_ROW_KEYS = ("trade_date", "stage", "ts", "emotion_index", "components", "version", "ingest_ts", "source")

DEFAULT_OUT_DIR = "data/emotion_index_snapshots"
_MANIFEST_NAME = "manifest.jsonl"


class SnapshotError(RuntimeError):
    """快照落盘失败（同名冲突/空表/目录不可写）。fail-closed，禁吞。"""


def stamp_token(now: Any = None) -> str:
    """快照文件名时戳（UTC，YYYYMMDDTHHMMSSZ）。now 可注入（测试/复算）。"""
    dt = now if now is not None else now_utc()
    return dt.strftime("%Y%m%dT%H%M%SZ")


def snapshot_filename(stamp: str) -> str:
    return f"emotion_index_{stamp}.jsonl.gz"


def _json_default(obj: Any) -> str:
    """Date/DateTime64 等 CH 驱动对象→ISO 字符串（components 原串不经此路径）。"""
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    raise TypeError(f"快照行含不可序列化对象: {type(obj).__name__}")


def rows_to_lines(rows: list[tuple]) -> list[str]:
    """行元组→规范化 JSONL 行（键序固定，components 原串保真）。"""
    out: list[str] = []
    for row in rows:
        if len(row) != len(_ROW_KEYS):
            raise SnapshotError(f"列宽不符：期望 {len(_ROW_KEYS)} 列，实得 {len(row)} 列")
        rec = dict(zip(_ROW_KEYS, row, strict=True))
        out.append(json.dumps(rec, ensure_ascii=False, sort_keys=True, default=_json_default))
    return out


def write_snapshot(
    out_dir: Path,
    rows: list[tuple],
    *,
    stamp: str,
) -> dict[str, Any]:
    """落一份全表快照（append-only）+manifest 追加。返回台账记录。

    - 同名快照已存在 → SnapshotError（绝不改写既有文件）
    - 先写 .tmp 同目录临时件再 os.replace 原子落位
    - manifest.jsonl 只追加（不存在则创建）
    """
    if not rows:
        raise SnapshotError("拒绝出快照：CH 返回 0 行（空镜像是证据污染，先查数据面）")
    out_dir.mkdir(parents=True, exist_ok=True)
    name = snapshot_filename(stamp)
    final = out_dir / name
    if final.exists():
        raise SnapshotError(f"同名快照已存在（append-only 禁改写）: {final}")
    lines = rows_to_lines(rows)
    payload = ("\n".join(lines) + "\n").encode("utf-8")
    sha256 = hashlib.sha256(payload).hexdigest()
    tmp = out_dir / f".tmp_{name}.{os.getpid()}"
    try:
        with open(tmp, "wb") as fh:
            fh.write(gzip.compress(payload, compresslevel=6))
        os.replace(tmp, final)
    finally:
        if tmp.exists():
            tmp.unlink()
    tds = sorted({str(r[0]) for r in rows})
    stages: dict[str, int] = {}
    for r in rows:
        key = str(r[1])
        stages[key] = stages.get(key, 0) + 1
    record = {
        "file": name,
        "sha256": sha256,
        "rows": len(rows),
        "min_trade_date": tds[0],
        "max_trade_date": tds[-1],
        "stage_counts": dict(sorted(stages.items())),
        "created_at_utc": stamp,
    }
    with open(out_dir / _MANIFEST_NAME, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return record


def read_manifest(out_dir: Path) -> list[dict[str, Any]]:
    """读台账（无台账=空列表）。"""
    path = out_dir / _MANIFEST_NAME
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def pit_state_path(out_dir: Path, asof: str) -> Path:
    """PIT 读径：created_at 日期 ≤ asof 的最新快照文件。无合格快照 → SnapshotError。"""
    asof_d = asof[:10].replace("-", "")  # 归一为 YYYYMMDD（与 stamp 同构，字典序=时序）
    best: tuple[str, Path] | None = None
    for rec in read_manifest(out_dir):
        created = str(rec.get("created_at_utc", ""))[:8]  # stamp 前8位=YYYYMMDD
        if created <= asof_d and (best is None or created >= best[0]):
            best = (created, out_dir / str(rec["file"]))
    if best is None:
        raise SnapshotError(f"PIT 无合格快照：asof={asof_d} 前没有任何快照落盘于 {out_dir}")
    if not best[1].exists():
        raise SnapshotError(f"PIT 快照文件缺失（被外部改动？append-only 被破坏）: {best[1]}")
    return best[1]


def main(argv: list[str] | None = None) -> int:
    """CLI 入口：拉全表→落快照→打印台账行。"""
    ap = argparse.ArgumentParser(prog="emotion_index_snapshot", description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir", default=DEFAULT_OUT_DIR, help="快照输出目录（默认 data/emotion_index_snapshots）")
    ap.add_argument("--stamp", default="", help="覆盖快照时戳（YYYYMMDDTHHMMSSZ，测试/复算注入用；缺省=now_utc）")
    args = ap.parse_args(argv)

    stamp = args.stamp if args.stamp else stamp_token()
    rows = ch_reader.query_rows(_SQL_SNAPSHOT)
    record = write_snapshot(Path(args.out_dir), rows, stamp=stamp)
    print(json.dumps(record, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
