# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.quarantine_manifest
# [DOMAIN] D_DATA
# [DEPENDENCIES] stdlib; zephyr.shared.io.file_utils.safe_write_text(热文件 CAS 写)
# [CONSUMERS] 死信处置方（隔离区自动分拣入口）+Owner 门审计面（TTL 报告只读）；生产接线=F04 C4
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只读扫描零改动（build/replay_candidates 不碰原文件）;manifest 唯一增量写（追加 jsonl 行，safe_write_text CAS）;本模块不提供删除/移动出隔离区的任何路径（破坏性操作=Owner 门，R-M1-02/03 同口径，dry_run 先行）;quarantined_at 缺证时取 mtime 并标 evidence=mtime（不臆造时间）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 目录不存在->QuarantineDirMissingError；manifest 行损坏->跳过并计入 corrupted_lines（不抛不吞账）
# [TESTS] tests/zephyr/data/test_quarantine_manifest.py
# [A_module] module_id=MOD-L00-004-R2 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# create-guard-not-dup: 数据清洁隔离区 manifest 桥+TTL 台账（F04 案卷 C4），与 governance_root_split 迁移脚本无同源关系，命中系"条目/清单"字面泛化
# [TTL] permanent

"""

Quarantine Manifest Bridge — 隔离区 manifest 桥 + TTL 台账 (MOD-L00-004-R2 / F04 夜战批)

背景（F04 案卷 C4）: 隔离区 data/local_fallback_quarantine 此前纯手工
（README.txt 记 2026-09-15 11 表死信，无代码桥、无 manifest、无 TTL 台账——
隔离了什么/何时到期/能否回放全凭人记忆）。本桥提供三件：

    1. build_quarantine_manifest(): 扫描隔离目录出结构化台账
       （条目/大小/隔离时间证据/条目数），只读零改动；
    2. append_quarantine_entry(): 死信→隔离的**自动分拣**入口——
       死信处置方把条目落进隔离目录时同步追加 manifest 行
       （jsonl，safe_write_text CAS 写），此后隔离事件不再靠 README 口口相传；
    3. replay_candidates(): TTL 台账——超期条目清单（report-only）。
       回放/清除本身=Owner 门（本模块不提供执行路径，dry_run 先行）。

SSoT: depgraph MOD-L00-004-R2
Version: 0.1.0

# [ALGO_FLOW] external: docs/03_modules/_domain_data/algo_flow/cleaning_rule_engine.yaml
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Final

from zephyr.shared.io.file_utils import safe_write_text

__all__: Final = [
    "DEFAULT_QUARANTINE_DIR",
    "MANIFEST_FILENAME",
    "QuarantineDirMissingError",
    "QuarantineEntry",
    "build_quarantine_manifest",
    "append_quarantine_entry",
    "load_manifest",
    "replay_candidates",
    "purge_expired",
    "PURGE_GATE_TOKEN",
    "REPLAYED_DIRNAME",
    "OwnerGateRequiredError",
]

#: C4 gated 执行路径字面闸（Owner 批文真源=2026-09-30 夜 F 组令卡 F6「C4 隔离区回放清除
#: 执行面（manifest report-only→加 gated 执行路径）」；裁定面=Owner 指令原文会话在案）
PURGE_GATE_TOKEN: Final = "F04-C4-OWNER-F6"

#: 清除动作落点（隔离区内 _replayed/<UTC 日期>/——mv 可逆非删除，R-M1-02/03 禁物理删除口径）
REPLAYED_DIRNAME: Final = "_replayed"

#: 生产隔离区（F04 案卷 C4 真源；测试一律传 tmp_path，禁写生产 data/）
DEFAULT_QUARANTINE_DIR: Final = Path("data/local_fallback_quarantine")

#: manifest jsonl 文件名（落在隔离目录内，随目录走）
MANIFEST_FILENAME: Final = "manifest.jsonl"

_README_MARK: Final = "隔离时间"


class QuarantineDirMissingError(Exception):
    """隔离目录不存在（扫描面 fail-loud，禁静默空账）。"""


class OwnerGateRequiredError(Exception):
    """C4 清除执行面 gate 字面值缺失/不符（Owner 批文确认位，防误触发）。"""


@dataclass(frozen=True)
class QuarantineEntry:
    """隔离条目台账行。

    Attributes:
        name: 条目名（目录/文件名）
        kind: dir / file / manifest / readme（manifest 与 readme 为账册自身）
        file_count: 条目内文件数（file=1，manifest/readme=1，dir=递归计数）
        total_bytes: 条目总字节数
        quarantined_at: 隔离时间（ISO8601 UTC；缺证=None）
        evidence: 时间证据来源（readme / mtime / manifest / none）
    """

    name: str
    kind: str
    file_count: int
    total_bytes: int
    quarantined_at: str | None
    evidence: str


def _entry_kind(p: Path) -> str:
    if p.name == MANIFEST_FILENAME:
        return "manifest"
    if p.suffix == ".txt":
        return "readme"
    return "dir" if p.is_dir() else "file"


def _stat_entry(p: Path) -> tuple[int, int]:
    """条目 (file_count, total_bytes)。"""
    if p.is_file():
        return 1, p.stat().st_size
    files = [f for f in p.rglob("*") if f.is_file()]
    return len(files), sum(f.stat().st_size for f in files)


def _parse_readme_time(p: Path) -> str | None:
    """从 _README.txt 首行解析隔离时间（"隔离时间 YYYY-MM-DD HH:MM:SS"）。"""
    try:
        head = p.read_text(encoding="utf-8", errors="replace")[:200]
    except OSError:
        return None
    for line in head.splitlines():
        if _README_MARK in line:
            raw = line.split(_README_MARK, 1)[1].strip("：: \t")
            raw = raw.split("：", 1)[0].strip()
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
                try:
                    dt = datetime.strptime(raw, fmt).replace(tzinfo=UTC)
                    return dt.isoformat()
                except ValueError:
                    continue
    return None


def build_quarantine_manifest(quarantine_dir: Path | str = DEFAULT_QUARANTINE_DIR) -> list[QuarantineEntry]:
    """扫描隔离目录出结构化台账（只读零改动）。

    目录不存在抛 QuarantineDirMissingError（fail-loud，禁静默空账）。
    """
    root = Path(quarantine_dir)
    if not root.is_dir():
        raise QuarantineDirMissingError(f"隔离目录不存在: {root}")
    entries: list[QuarantineEntry] = []
    readme_time: str | None = None
    readme = root / "_README.txt"
    if readme.is_file():
        readme_time = _parse_readme_time(readme)
    for p in sorted(root.iterdir(), key=lambda x: x.name):
        if p.name == MANIFEST_FILENAME:
            continue  # 账册自身不入账（防自引用递归）
        kind = _entry_kind(p)
        file_count, total_bytes = _stat_entry(p)
        if kind == "readme":
            entries.append(
                QuarantineEntry(
                    name=p.name,
                    kind=kind,
                    file_count=file_count,
                    total_bytes=total_bytes,
                    quarantined_at=readme_time,
                    evidence="readme" if readme_time else "none",
                )
            )
            continue
        # 目录/文件条目：README 全局时间优先，缺证回退 mtime（标 evidence=mtime）
        qtime = readme_time
        evidence = "readme" if readme_time else "none"
        if qtime is None:
            try:
                mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=UTC)
                qtime, evidence = mtime.isoformat(), "mtime"
            except OSError:
                pass
        entries.append(
            QuarantineEntry(
                name=p.name,
                kind=kind,
                file_count=file_count,
                total_bytes=total_bytes,
                quarantined_at=qtime,
                evidence=evidence,
            )
        )
    return entries


def append_quarantine_entry(
    entry: QuarantineEntry,
    quarantine_dir: Path | str = DEFAULT_QUARANTINE_DIR,
) -> Path:
    """死信→隔离自动分拣：追加一条 manifest 行（jsonl，CAS 写）。

    本函数只记账不搬文件——条目实体由处置方先落进隔离目录，随后调用本函数
    登账（搬+记账的原子性由处置方保证；账册先行会造成幽灵账）。
    """
    root = Path(quarantine_dir)
    if not root.is_dir():
        raise QuarantineDirMissingError(f"隔离目录不存在: {root}")
    manifest_path = root / MANIFEST_FILENAME
    line = json.dumps(asdict(entry), ensure_ascii=False, sort_keys=True)
    if manifest_path.exists():
        text = manifest_path.read_text(encoding="utf-8")
        return safe_write_text(manifest_path, text.rstrip("\n") + "\n" + line + "\n")
    return safe_write_text(manifest_path, line + "\n")


def load_manifest(
    quarantine_dir: Path | str = DEFAULT_QUARANTINE_DIR,
) -> tuple[list[QuarantineEntry], int]:
    """读回 manifest 账册。

    Returns:
        (entries, corrupted_lines)——损坏行跳过并计数（不抛不吞账）。
        账册不存在=([], 0)（空账合法：与 fail-loud 的扫描面区分）。
    """
    manifest_path = Path(quarantine_dir) / MANIFEST_FILENAME
    if not manifest_path.exists():
        return [], 0
    entries: list[QuarantineEntry] = []
    corrupted = 0
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            raw = json.loads(line)
            entries.append(
                QuarantineEntry(
                    name=str(raw["name"]),
                    kind=str(raw["kind"]),
                    file_count=int(raw["file_count"]),
                    total_bytes=int(raw["total_bytes"]),
                    quarantined_at=raw.get("quarantined_at"),
                    evidence=str(raw.get("evidence", "manifest")),
                )
            )
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            corrupted += 1
    return entries, corrupted


def replay_candidates(
    ttl_days: int,
    now: datetime | None = None,
    quarantine_dir: Path | str = DEFAULT_QUARANTINE_DIR,
) -> list[QuarantineEntry]:
    """TTL 台账：隔离超 ttl_days 天的条目清单（report-only，回放/清除=Owner 门）。

    数据来源=manifest 账册（先 append 后查）；无账册时回退扫描面时间证据。
    本函数不提供任何执行路径——回放/清除/R-M1-02/03 类破坏性操作必须走
    Owner 门位（裁定登记），此处只出清单。
    """
    if ttl_days <= 0:
        raise ValueError(f"ttl_days 须为正，got {ttl_days}")
    now = now or datetime.now(UTC)
    entries, _ = load_manifest(quarantine_dir)
    if not entries:
        try:
            entries = build_quarantine_manifest(quarantine_dir)
        except QuarantineDirMissingError:
            return []
    cutoff = now - timedelta(days=ttl_days)
    out: list[QuarantineEntry] = []
    for e in entries:
        if e.kind in ("manifest", "readme"):
            continue  # 账册与说明不入 TTL 台账
        if e.quarantined_at is None:
            continue  # 无时间证据不臆判超期
        try:
            qat = datetime.fromisoformat(e.quarantined_at)
        except ValueError:
            continue
        if qat <= cutoff:
            out.append(e)
    return out


def purge_expired(
    ttl_days: int,
    *,
    execute: bool = False,
    gate: str = "",
    now: datetime | None = None,
    quarantine_dir: Path | str = DEFAULT_QUARANTINE_DIR,
) -> dict:
    """TTL 超期条目清除执行面（F04 案卷 C4 gated 路径，2026-09-30 F 组夜班补装）。

    双闸（缺一即拒，宁停勿伤）：
    - execute=False（默认）=report-only（与 replay_candidates 同面，零改动）；
    - execute=True 时 gate 必须等于 PURGE_GATE_TOKEN 字面值——Owner 批文面
      （2026-09-30 夜 F 组令卡 F6），防误触发的显式确认位。

    动作语义：mv 入 <quarantine_dir>/_replayed/<UTC 日期>/（**可逆搬移非删除**，
    R-M1-02/03 禁物理删除口径——字节保全可回放），成功后 manifest 追加
    action=purged 台账行（append_quarantine_entry 同 CAS 通道，账随物走）。

    Returns:
        {"candidates": n, "purged": [...], "failed": {name: err}, "mode": "report"|"execute"}
    """
    if execute and gate != PURGE_GATE_TOKEN:
        raise OwnerGateRequiredError(
            "purge_expired execute=True 需显式 gate 字面值（Owner 批文确认位；批文真源=2026-09-30 夜 F 组令卡 F6）"
        )
    root = Path(quarantine_dir)
    expired = replay_candidates(ttl_days, now=now, quarantine_dir=root)
    if not execute:
        return {"candidates": len(expired), "purged": [], "failed": {}, "mode": "report"}
    if not root.is_dir():
        raise QuarantineDirMissingError(f"隔离目录不存在: {root}")
    day = (now or datetime.now(UTC)).strftime("%Y%m%d")
    replayed_dir = root / REPLAYED_DIRNAME / day
    purged: list[str] = []
    failed: dict[str, str] = {}
    for e in expired:
        src = root / e.name
        if not src.exists():
            failed[e.name] = "source missing (already moved?)"
            continue
        try:
            dst_parent = replayed_dir / e.name
            dst_parent.parent.mkdir(parents=True, exist_ok=True)
            src.rename(dst_parent)
        except OSError as exc:
            failed[e.name] = f"{type(exc).__name__}: {exc}"
            continue
        purged.append(e.name)
        try:
            append_quarantine_entry(
                QuarantineEntry(
                    name=e.name,
                    kind=e.kind,
                    file_count=e.file_count,
                    total_bytes=e.total_bytes,
                    quarantined_at=e.quarantined_at,
                    evidence=f"purged->{REPLAYED_DIRNAME}/{day}",
                ),
                quarantine_dir=root,
            )
        except OSError as exc:  # 账册失败不回滚搬移（物已安全落 _replayed，账面差异留审计）
            failed[e.name] = f"moved but manifest append failed: {exc}"
    return {
        "candidates": len(expired),
        "purged": purged,
        "failed": failed,
        "mode": "execute",
        "replayed_dir": str(replayed_dir),
    }


if __name__ == "__main__":  # ORPHAN-MODULE 入口豁免形态：默认隔离目录只读账面转储（Owner 门审计面，零参数零副作用）
    entries = build_quarantine_manifest(DEFAULT_QUARANTINE_DIR)
    print(f"quarantine_dir={DEFAULT_QUARANTINE_DIR} entries={len(entries)}")
    for e in entries:
        print(f"{e.name}	{e.kind}	{e.quarantined_at}")
