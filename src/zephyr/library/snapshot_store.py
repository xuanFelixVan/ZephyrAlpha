# [BLUEPRINT] MOD-LIB-006 | docs/03_modules/_domain_library/blueprint.md | §6
# [MODULE] zephyr.library.snapshot_store
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.library.librarian (Librarian/PgConnection/PgCursor); zephyr.library.ledger_fingerprint (R1 世代指纹唯一真源，动态 import 禁复制 SQL); zephyr.infrastructure.database_service (唯一 PG 入口); zephyr.shared.io.paths (REPO_ROOT); zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] scripts/backup/library_ledger_backup.py（备份成功尾步刷新）; tests/library/test_snapshot_store.py
# [STARTUP] event_driven
# [MATURITY] production
# [INVARIANTS] 快照=可派生镜像**非真源**（PG lib_assets/lib_events 恒唯一真源）；磁盘恒 ≤KEEP_GENERATIONS 代；崩溃安全 7 步序（tmp→fsync→os.replace=提交点①→manifest 提交点②→才删上上代），删旧严格后置；读侧 PG 可达即以 PG 为准，PG 不可达才回落快照且必标 degraded/authoritative=False；缺 ledger_version 版本列/代际不符一律**拒读**（禁覆盖语义——本仓 ReplacingMergeTree 无版本列事故先例）；刷新零新增计划任务、零 cron/Timer/sleep-loop（根宪法 §9 第 3 条）；世代指纹只 import R1 件（禁本件复制指纹 SQL，S1 单写者公理）
# [MODIFY-GUARD] gate_id 不适用
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 快照缺失=SnapshotUnavailableError；截断/校验失配=SnapshotCorruptError；无版本列/代际不符=SnapshotVersionColumnError；双写者占用=SnapshotWriterBusyError；PG 不可达且快照不可用=SnapshotFallbackExhaustedError（禁静默返回空）；R1 世代指纹件未落地=LedgerStampUnavailable；refresh 不吞异常（fail-open 由调用方决定）
# [TESTS] tests/library/test_snapshot_store.py
# [A_module] module_id=MOD-LIB-006 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""snapshot_store.py — 图书馆账本本地快照层（MOD-LIB-006，内存缓存战役 R2 批）。

大白话：账本真源在 PostgreSQL，库一旦连不上就查无可查。本件把整张 ``lib_assets``
导出成磁盘上的一份"影子副本"（Parquet+gzip，文件名自带世代号），磁盘最多只留 2 份，
新副本**完整落盘成功**才删掉上上代——删旧严格排在两次原子改名之后，崩溃时磁盘状态
恒 ∈ {旧 pair, 新 pair+旧}，无第三态。库连着时一切以库为准；库断了才读影子副本，
并且每次都会显式标注"降级·来源=快照·非真源"，绝不当真源用。

本件按职责分四件（§5.150 拆职责不拆行为，对外 API 恒为 :class:`LedgerSnapshotStore`）：
:func:`default_snapshot_root` 定家 → :class:`SnapshotLayout` 命名/存在性薄层 →
:class:`LedgerSnapshotWriter` 写侧 7 步崩溃安全序（见 :meth:`LedgerSnapshotWriter.refresh`）→
:class:`LedgerSnapshotReader` 读侧校验链；回落总口见 :func:`query_ledger_with_fallback`。
刷新挂接点=``scripts/backup/library_ledger_backup.py``
备份成功尾步（既有 schtasks 链，零新增计划任务）。规格真源=
``docs/_working/lib_ram_campaign/S3_snapshot_layer/README.md``。

Usage::

    python -m zephyr.library.snapshot_store status
    python -m zephyr.library.snapshot_store refresh [--ledger-version N]
    python -m zephyr.library.snapshot_store query kline --limit 5

# [ALGO_FLOW] external: docs/03_modules/_domain_library/algo_flow/snapshot_store.yaml
"""

from __future__ import annotations

import hashlib
import importlib
import json
import logging
import os
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Final

import psycopg2
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

from zephyr.library.librarian import Librarian, PgConnection, PgCursor
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

SNAPSHOT_PREFIX: Final[str] = "lib_snapshot.v"
SNAPSHOT_SUFFIX: Final[str] = ".parquet"
TMP_SUFFIX: Final[str] = ".tmp"
MANIFEST_NAME: Final[str] = "lib_snapshot_latest.manifest.json"
WRITER_LOCK_NAME: Final[str] = "writer.lock"
VERSION_COLUMN: Final[str] = "ledger_version"
MANIFEST_FORMAT: Final[int] = 1
KEEP_GENERATIONS: Final[int] = 2
WRITER_LOCK_TTL_SECONDS: Final[int] = 1800
ROOT_ENV_VAR: Final[str] = "ZEPHYR_LIBRARY_SNAPSHOT_ROOT"
DEFAULT_ROOT_REL: Final[str] = "data/library_snapshots"
# 整表镜像：不裁行不裁列（S3 簿 §4.2）——列集动态取，禁硬编码（ledger_schema 投影列集正在被他队改）
# 纯 Assign 形态（NO-BARE-SQL 的 SQL 常量豁免走 ast.Assign，带 : Final 注解会被漏认）
_SQL_EXPORT_ASSETS = "SELECT * FROM lib_assets"
_QUERY_MATCH_COLUMNS: Final[tuple[str, ...]] = ("asset_id", "home", "title")
_ORDER_COLUMN: Final[str] = "asset_id"
_PG_UNREACHABLE: Final[tuple[type[BaseException], ...]] = (psycopg2.Error, ConnectionError, OSError)

#: 世代指纹（=max(event_id)）读出的唯一入口。真源实现=R1 批
#: ``zephyr.library.ledger_fingerprint.read_ledger_fingerprint``（S1 簿 §3.6 单写者公理：
#: 指纹判据只允许一处实现，本件**禁**复制指纹 SQL）。R1 件缺席/更名时本入口抛
#: :class:`LedgerStampUnavailable` 报红——禁伪造水位、禁退化成别处现算。
#: 测试/旁路注入位=:func:`set_ledger_version_provider`（单点接线，不改本件判据）。
_R1_STAMP_MODULE: Final[str] = "zephyr.library.ledger_fingerprint"
_R1_STAMP_FUNC: Final[str] = "read_ledger_fingerprint"
_version_provider_override: Callable[[Any], int] | None = None


class SnapshotStoreError(RuntimeError):
    """快照层异常基类（读侧一律显式报红，禁降级为静默空结果）。"""


class SnapshotUnavailableError(SnapshotStoreError):
    """磁盘上没有任何可用快照（缺 manifest 或缺文件）。"""


class SnapshotCorruptError(SnapshotStoreError):
    """快照截断/校验和失配/行数与 manifest 不符/manifest 指向半途态。"""


class SnapshotVersionColumnError(SnapshotStoreError):
    """快照缺 ``ledger_version`` 版本列或行内代际与 manifest 不符（禁覆盖语义）。"""


class SnapshotWriterBusyError(SnapshotStoreError):
    """目录级写者锁被活跃进程持有（禁双写者）。"""


class SnapshotFallbackExhaustedError(SnapshotStoreError):
    """PG 不可达**且**快照不可用——唯一出路是报红上抛。"""


class LedgerStampUnavailable(SnapshotStoreError):
    """世代指纹读出实现（R1 批）尚未落地。"""


@dataclass(frozen=True)
class LedgerSnapshotManifest:
    """代际记录（提交点②的内容）：文件名携版本 + 行内版本列 + 本记录=三重同代声明。"""

    ledger_version: int
    snapshot_file: str
    built_at_utc: str
    row_count: int
    sha256: str
    columns: tuple[str, ...]

    def to_json(self) -> dict[str, Any]:
        """序列化为 manifest 载荷（附 manifest_format 供后续代际演进）。"""
        payload: dict[str, Any] = asdict(self)
        payload["manifest_format"] = MANIFEST_FORMAT
        return payload

    @classmethod
    def from_json(cls, payload: Mapping[str, Any]) -> LedgerSnapshotManifest:
        """从 manifest 载荷还原；字段缺失/类型非法一律判损坏（fail-closed）。"""
        try:
            columns = tuple(str(c) for c in payload["columns"])
            return cls(
                ledger_version=int(payload["ledger_version"]),
                snapshot_file=str(payload["snapshot_file"]),
                built_at_utc=str(payload["built_at_utc"]),
                row_count=int(payload["row_count"]),
                sha256=str(payload["sha256"]),
                columns=columns,
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise SnapshotCorruptError(f"manifest 载荷非法: {exc}") from exc

    def file_name_for(self, version: int) -> str:
        """按版本生成快照文件名（文件名=可读的代际声明）。"""
        return f"{SNAPSHOT_PREFIX}{version}{SNAPSHOT_SUFFIX}"

    @property
    def is_self_consistent(self) -> bool:
        """机械自检：文件名版本必须等于 manifest.ledger_version。"""
        return self.snapshot_file == self.file_name_for(self.ledger_version)


@dataclass(frozen=True)
class LedgerQueryResult:
    """读侧结果：来源/降级/陈旧度全部显式携带，禁与正常命中同形。"""

    rows: list[dict[str, Any]]
    source: str
    ledger_version: int | None
    degraded: bool
    authoritative: bool
    degraded_reason: str | None = None
    snapshot_load_error: str | None = None


def default_snapshot_root() -> Path:
    """快照家目录（S3 判家=data/library_snapshots 中性区；env 可注入，测试禁写生产目录）。"""
    override = os.environ.get(ROOT_ENV_VAR)
    if override:
        return Path(override)
    return Path(str(REPO_ROOT)) / DEFAULT_ROOT_REL


def set_ledger_version_provider(provider: Callable[[Any], int] | None) -> None:
    """世代指纹读出的单点接线口（R1 落地后注入其实现；None=恢复默认解析）。"""
    global _version_provider_override  # noqa: PLW0603 — 单点 DI 缝，语义同 lookup.py 模块开关先例
    _version_provider_override = provider


def read_ledger_version(conn: PgConnection) -> int:
    """账本世代指纹（=max(event_id)）唯一读出口。

    Args:
        conn: 满足只读查询的 PG 连接（透传给 R1 实现）。

    Returns:
        当前世代号。

    Raises:
        LedgerStampUnavailable: R1 指纹件尚未落地（禁伪造水位、禁本件复制指纹 SQL）。
    """
    if _version_provider_override is not None:
        return int(_version_provider_override(conn))
    try:
        module = importlib.import_module(_R1_STAMP_MODULE)
        reader = getattr(module, _R1_STAMP_FUNC)
    except (ImportError, AttributeError) as exc:
        raise LedgerStampUnavailable(
            f"世代指纹真源件不可用（期望 {_R1_STAMP_MODULE}.{_R1_STAMP_FUNC}）: {exc}"
            "——快照写侧拒绝伪造水位，禁在本件另写一份指纹 SQL"
        ) from exc
    return int(reader(conn))


def _pg_conn() -> PgConnection:
    """默认 PG 入口：DatabaseService 唯一真源（禁裸 duckdb/裸 psycopg 连接，根宪法 §9 第 1 条）。"""
    from zephyr.infrastructure.database_service import get_db_service  # noqa: PLC0415 — 重依赖懒加载

    return get_db_service().get_depgraph_conn(read_only=True)


def _sha256_file(path: Path) -> str:
    """文件级 sha256（stdlib CPython 3.12 file_digest：零分块样板，禁与他件复制同一实现）。"""
    with path.open("rb") as fh:
        return hashlib.file_digest(fh, "sha256").hexdigest()


def _version_from_name(name: str) -> int | None:
    """从 ``lib_snapshot.v<ledger_version>.parquet`` 解析版本号；不合规命名返回 None。"""
    if not (name.startswith(SNAPSHOT_PREFIX) and name.endswith(SNAPSHOT_SUFFIX)):
        return None
    stem = name[len(SNAPSHOT_PREFIX) : -len(SNAPSHOT_SUFFIX)]
    return int(stem) if stem.isdigit() else None


def _fsync_write(path: Path, payload: bytes) -> None:
    """写 tmp + flush + fsync（"成功"定义=落盘语义，非写调用返回）。"""
    with path.open("wb") as fh:
        fh.write(payload)
        fh.flush()
        os.fsync(fh.fileno())


def _atomic_publish(tmp_path: Path, final_path: Path) -> None:
    """提交点原语：os.replace 同目录改名=文件级原子（唯一崩溃可见切换点）。

    单独成函数=红队夹具的故障注入缝（monkeypatch 本函数即模拟改名前抛异常）。
    """
    os.replace(tmp_path, final_path)


def _json_cells(row: Mapping[str, Any]) -> dict[str, Any]:
    """jsonb 单元格转 JSON 串（异构 struct 无法统一成 arrow 列，转文本零歧义）。"""
    return {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, Mapping) else v) for k, v in row.items()}


def _rows_from_cursor(cur: PgCursor) -> list[dict[str, Any]]:
    """游标结果转 list[dict]（兼容 RealDictCursor 与元组游标两种行形态）。"""
    cols = [d[0] for d in cur.description]
    return [dict(row) if isinstance(row, Mapping) else dict(zip(cols, row, strict=False)) for row in cur.fetchall()]


class SnapshotLayout:
    """快照目录布局薄层：命名/路径拼法 + 存在性探测（读写两侧的共用底座，零业务判定）。"""

    def __init__(self, root: Path) -> None:
        self._root = Path(root)

    @property
    def root(self) -> Path:
        """快照根目录（只读视图）。"""
        return self._root

    @property
    def manifest_path(self) -> Path:
        """稳定入口 manifest 路径。"""
        return self._root / MANIFEST_NAME

    @property
    def lock_path(self) -> Path:
        """目录级写者锁路径。"""
        return self._root / WRITER_LOCK_NAME

    def ensure_dir(self) -> None:
        """目录就位（幂等；仅写侧调用，读者只探测不创建）。"""
        self._root.mkdir(parents=True, exist_ok=True)

    def full_name(self, manifest: LedgerSnapshotManifest) -> Path:
        """manifest 指向的快照绝对路径（不校验存在性）。"""
        return self._root / manifest.snapshot_file

    def snapshot_files(self) -> list[tuple[int, Path]]:
        """目录内合规快照文件（版本升序）；不合规命名一律不认（含 ``.tmp`` 残渣）。"""
        found: list[tuple[int, Path]] = []
        if not self._root.is_dir():
            return found
        for path in self._root.glob(f"{SNAPSHOT_PREFIX}*{SNAPSHOT_SUFFIX}"):
            version = _version_from_name(path.name)
            if version is not None:
                found.append((version, path))
        return sorted(found, key=lambda item: item[0])

    def tmp_residues(self) -> list[Path]:
        """崩溃残渣候选（``.tmp`` 后缀，永不被读者引用）。"""
        if not self._root.is_dir():
            return []
        return list(self._root.glob(f"{SNAPSHOT_PREFIX}*{SNAPSHOT_SUFFIX}{TMP_SUFFIX}"))


class LedgerSnapshotReader:
    """快照读入职：manifest 点读 + 代际/校验和/行数/版本列全链核验 + 回落查询。

    判据铁律：任一校验失配即抛（禁静默返回空/部分行集）；缺 ``ledger_version`` 版本列
    或行内代际与 manifest 不符一律**拒读**（禁覆盖语义）。
    """

    def __init__(self, layout: SnapshotLayout) -> None:
        self._layout = layout

    def read_manifest(self) -> LedgerSnapshotManifest | None:
        """点读 manifest；不存在=None（缺件由调用方判定，禁静默造代）。"""
        path = self._layout.manifest_path
        if not path.exists():
            return None
        try:
            return LedgerSnapshotManifest.from_json(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, ValueError) as exc:
            raise SnapshotCorruptError(f"manifest 不可读: {exc}") from exc

    def load_manifest_quietly(self) -> LedgerSnapshotManifest | None:
        """幂等跳过判据专用：manifest 缺失/非法一律按"无可比代"处理（后续必然重建）。"""
        try:
            return self.read_manifest()
        except SnapshotCorruptError:
            return None

    def verify(self) -> tuple[LedgerSnapshotManifest | None, str | None]:
        """廉价自检（manifest+文件名+校验和+footer 行数+版本列），**永不抛**。

        Returns:
            (manifest, error)：error=None 表示可用；无快照=(None, None)。
        """
        try:
            manifest = self.read_manifest()
            if manifest is None:
                return None, None
            self._verified_table(manifest)
            return manifest, None
        except SnapshotStoreError as exc:
            return None, f"{type(exc).__name__}: {exc}"

    def load_rows(self) -> list[dict[str, Any]]:
        """全量读回当前快照（逐项校验，任一失配即抛——禁静默返回空/部分行集）。"""
        return self._verified_table(self._require_manifest()).to_pylist()

    def query(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        """回落查询：等价 ``_SQL_LOOKUP`` 的 asset_id/home/title 模糊 + asset_id 序。"""
        table = self._verified_table(self._require_manifest())
        needle = (query or "").strip()
        mask = None
        for column in _QUERY_MATCH_COLUMNS:
            if column not in table.column_names:
                raise SnapshotCorruptError(f"快照缺查询列 {column}（列集漂移=非本件镜像）")
            hit = pc.fill_null(pc.match_substring(table[column], needle, ignore_case=True), False)
            mask = hit if mask is None else pc.or_(mask, hit)
        if mask is None:
            raise SnapshotCorruptError("快照无匹配列可查")
        matched = table.filter(mask).sort_by(_ORDER_COLUMN)
        return matched.slice(0, max(1, int(limit))).to_pylist()

    def _require_manifest(self) -> LedgerSnapshotManifest:
        manifest = self.read_manifest()
        if manifest is None:
            raise SnapshotUnavailableError(f"无快照 manifest：{self._layout.manifest_path}")
        return manifest

    def _verified_table(self, manifest: LedgerSnapshotManifest) -> pa.Table:
        """校验链：自洽→文件在→sha256→footer 行数→版本列→行内代际（全过才交表）。"""
        if not manifest.is_self_consistent:
            raise SnapshotCorruptError(
                f"manifest 文件名代际与 ledger_version 不符（半途提交态）: {manifest.snapshot_file}"
            )
        path = self._layout.full_name(manifest)
        if not path.exists():
            raise SnapshotCorruptError(f"manifest 指向不存在的快照文件（崩溃窗口③）: {path.name}")
        if _sha256_file(path) != manifest.sha256:
            raise SnapshotCorruptError(f"快照校验和失配（截断/位翻转）: {path.name}")
        table = pq.read_table(path)
        if table.num_rows != manifest.row_count:
            raise SnapshotCorruptError(f"行数与 manifest 不符: {table.num_rows} != {manifest.row_count}")
        _assert_version_column(table, manifest)
        return table


class LedgerSnapshotWriter:
    """快照写出职：目录级写者锁 + S3 §4.3 七步崩溃安全落盘 + 留 2 份轮转。

    删旧严格后置于两个提交点（数据文件改名、manifest 改名）之后——崩溃窗口内磁盘状态
    恒 ∈ {旧 pair, 新 pair+旧}，无第三态。轮转与残渣清理见 :meth:`_prune_after_commit`。
    """

    def __init__(
        self,
        layout: SnapshotLayout,
        *,
        conn_factory: Callable[[], PgConnection] | None = None,
        version_provider: Callable[[Any], int] | None = None,
        keep: int = KEEP_GENERATIONS,
        clock: Callable[[], datetime] = now_utc,
        lock_ttl_seconds: int = WRITER_LOCK_TTL_SECONDS,
    ) -> None:
        """注入目录布局与全部外部依赖（测试零生产路径写）。

        Args:
            layout: 快照目录布局（路径/命名/存在性薄层）。
            conn_factory: PG 连接工厂（默认 DatabaseService 只读连接）。
            version_provider: 世代指纹读出口（默认 :func:`read_ledger_version` 单点入口）。
            keep: 磁盘保留代数上限（Owner 定版=2，代码常量封死）。
            clock: 时钟注入口（RULE-SCHEMA-TZ：默认 now_utc，测试注入固定时刻）。
            lock_ttl_seconds: 写者锁 TTL（超时视为残渣可自愈接管）。
        """
        self._layout = layout
        self._reader = LedgerSnapshotReader(layout)
        self._conn_factory = conn_factory
        self._version_provider = version_provider
        self._keep = max(1, int(keep))
        self._clock = clock
        self._lock_ttl = int(lock_ttl_seconds)

    def refresh(self, ledger_version: int | None = None) -> dict[str, Any]:
        """导出并落盘一份新快照（S3 §4.3 七步崩溃安全序）。

        Args:
            ledger_version: 显式世代号（默认由世代指纹单点入口现读）。

        Returns:
            状态字典：``written``（含 row_count/sha256/deleted）或 ``skipped_up_to_date``。

        Raises:
            LedgerStampUnavailable: 指纹源未落地且未显式传 version。
            SnapshotWriterBusyError: 双写者占用。
            SnapshotStoreError: 导出为空表等异常（禁落"看起来正常"的空快照）。
        """
        self._acquire_lock()
        try:
            return self._refresh_locked(ledger_version)
        finally:
            self._release_lock()

    def _refresh_locked(self, explicit_version: int | None) -> dict[str, Any]:
        """七步序主体（步骤号对应 S3 §4.3）。"""
        conn = self._connect()
        stamp = explicit_version if explicit_version is not None else self._stamp(conn)  # ①
        manifest = self._reader.load_manifest_quietly()
        if (
            manifest
            and manifest.is_self_consistent
            and stamp == manifest.ledger_version
            and self._layout.full_name(manifest).exists()
        ):
            return {"status": "skipped_up_to_date", "ledger_version": stamp, "row_count": manifest.row_count}  # ②
        rows = self._export_rows(conn)  # ③
        if not rows:
            raise SnapshotStoreError("lib_assets 导出零行——拒落空快照（空快照被回落读=静默假真源）")
        for row in rows:
            row[VERSION_COLUMN] = stamp
        table = pa.Table.from_pylist(rows)
        manifest = self._publish_data_file(table, stamp)  # ④ 提交点①：文件级原子
        manifest = self.publish_manifest(manifest)  # ⑤ 提交点②：代际记录生效
        deleted = self._prune_after_commit(stamp)  # ⑥ 严格后置
        return {
            "status": "written",
            "ledger_version": stamp,
            "row_count": manifest.row_count,
            "sha256": manifest.sha256,
            "snapshot_file": manifest.snapshot_file,
            "deleted": deleted,
        }

    def _publish_data_file(self, table: pa.Table, version: int) -> LedgerSnapshotManifest:
        """步骤③④：tmp 写 → fsync → os.replace（提交点①文件级原子）。"""
        self._layout.ensure_dir()
        name = f"{SNAPSHOT_PREFIX}{version}{SNAPSHOT_SUFFIX}"
        tmp_path = self._layout.root / (name + TMP_SUFFIX)
        with tmp_path.open("wb") as fh:
            pq.write_table(table, fh, compression="gzip")
            fh.flush()
            os.fsync(fh.fileno())
        manifest = LedgerSnapshotManifest(
            ledger_version=version,
            snapshot_file=name,
            built_at_utc=self._clock().isoformat(),
            row_count=table.num_rows,
            sha256=_sha256_file(tmp_path),
            columns=tuple(table.column_names),
        )
        _atomic_publish(tmp_path, self._layout.full_name(manifest))
        return manifest

    def publish_manifest(self, manifest: LedgerSnapshotManifest) -> LedgerSnapshotManifest:
        """步骤⑤：manifest tmp → fsync → os.replace（提交点②代际记录生效）。"""
        final_path = self._layout.manifest_path
        tmp_path = final_path.with_name(MANIFEST_NAME + TMP_SUFFIX)
        payload = json.dumps(manifest.to_json(), ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
        _fsync_write(tmp_path, payload)
        _atomic_publish(tmp_path, final_path)
        return manifest

    def _prune_after_commit(self, current: int) -> list[str]:
        """步骤⑥：仅在提交点②成功后执行——保留当代与其前一代，删上上代起。"""
        kept: set[int] = {current}
        files = self._layout.snapshot_files()
        prior = [version for version, _ in files if version not in kept]
        kept.update(prior[-(self._keep - 1) :] if self._keep > 1 else [])
        removed: list[str] = []
        for version, path in files:
            if version not in kept:
                path.unlink(missing_ok=True)
                removed.append(path.name)
        removed.extend(self._sweep_tmp_residue())
        return removed

    def _sweep_tmp_residue(self) -> list[str]:
        """步骤⑦残渣：崩溃遗留的 .tmp 幂等清理（禁被引用，超 TTL 才删以免误伤在途写者）。"""
        swept: list[str] = []
        cutoff = self._clock().timestamp() - self._lock_ttl
        for tmp in self._layout.tmp_residues():
            try:
                if tmp.stat().st_mtime < cutoff:
                    tmp.unlink(missing_ok=True)
                    swept.append(tmp.name)
            except OSError:
                continue
        return swept

    def _export_rows(self, conn: PgConnection) -> list[dict[str, Any]]:
        """全表 SELECT（整表镜像，列集动态取；禁裁行=第二裁判）。"""
        with conn.cursor() as cur:
            cur.execute(_SQL_EXPORT_ASSETS)
            return [_json_cells(row) for row in _rows_from_cursor(cur)]

    def _stamp(self, conn: PgConnection) -> int:
        provider = self._version_provider or read_ledger_version
        return int(provider(conn))

    def _connect(self) -> PgConnection:
        factory = self._conn_factory or _pg_conn
        return factory()

    # ---------------------------------------------------------------- 写者锁

    def _acquire_lock(self) -> None:
        """目录级写者锁（O_EXCL 创建 + TTL 自愈），禁双写者。"""
        self._layout.ensure_dir()
        lock = self._layout.lock_path
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            if self._lock_is_live(lock):
                raise SnapshotWriterBusyError(f"快照写者锁在握（TTL {self._lock_ttl}s 内）: {lock}") from exc
            lock.unlink(missing_ok=True)
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(fd, "wb") as fh:
            fh.write(f"{os.getpid()} {self._clock().isoformat()}".encode())

    def _lock_is_live(self, lock: Path) -> bool:
        """锁是否仍在握：mtime 早于 TTL 窗口=残渣可自愈接管；未来时戳=刚写入，判在握。"""
        try:
            age = self._clock().timestamp() - lock.stat().st_mtime
        except OSError:
            return False
        return age < self._lock_ttl

    def _release_lock(self) -> None:
        self._layout.lock_path.unlink(missing_ok=True)


class LedgerSnapshotStore:
    """账本本地快照层门面：写出职（:class:`LedgerSnapshotWriter`）与读入职
    （:class:`LedgerSnapshotReader`）接在同一 :class:`SnapshotLayout` 上，
    对外 API 与 R2 交付逐字同形（§5.150 拆职责不拆行为）。
    """

    def __init__(
        self,
        root: Path | None = None,
        *,
        conn_factory: Callable[[], PgConnection] | None = None,
        version_provider: Callable[[Any], int] | None = None,
        keep: int = KEEP_GENERATIONS,
        clock: Callable[[], datetime] = now_utc,
        lock_ttl_seconds: int = WRITER_LOCK_TTL_SECONDS,
    ) -> None:
        """注入快照根目录与全部外部依赖（测试零生产路径写；参数语义见写侧构造器）。"""
        self._layout = SnapshotLayout(Path(root) if root is not None else default_snapshot_root())
        self._reader = LedgerSnapshotReader(self._layout)
        self._writer = LedgerSnapshotWriter(
            self._layout,
            conn_factory=conn_factory,
            version_provider=version_provider,
            keep=keep,
            clock=clock,
            lock_ttl_seconds=lock_ttl_seconds,
        )

    @property
    def root(self) -> Path:
        """快照根目录（只读视图）。"""
        return self._layout.root

    @property
    def manifest_path(self) -> Path:
        """稳定入口 manifest 路径。"""
        return self._layout.manifest_path

    def refresh(self, ledger_version: int | None = None) -> dict[str, Any]:
        """导出并落盘一份新快照（七步崩溃安全序真源=:meth:`LedgerSnapshotWriter.refresh`）。"""
        return self._writer.refresh(ledger_version)

    def snapshot_files(self) -> list[tuple[int, Path]]:
        """目录内合规快照文件（版本升序）。"""
        return self._layout.snapshot_files()

    def read_manifest(self) -> LedgerSnapshotManifest | None:
        """点读 manifest；不存在=None（缺件由调用方判定，禁静默造代）。"""
        return self._reader.read_manifest()

    def verify(self) -> tuple[LedgerSnapshotManifest | None, str | None]:
        """廉价自检（manifest+文件名+校验和+footer 行数+版本列），**永不抛**。"""
        return self._reader.verify()

    def load_rows(self) -> list[dict[str, Any]]:
        """全量读回当前快照（逐项校验，任一失配即抛——禁静默返回空/部分行集）。"""
        return self._reader.load_rows()

    def query(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        """回落查询：等价 ``_SQL_LOOKUP`` 的 asset_id/home/title 模糊 + asset_id 序。"""
        return self._reader.query(query, limit)

    def _publish_manifest(self, manifest: LedgerSnapshotManifest) -> LedgerSnapshotManifest:
        """提交点②单步暴露位（损坏态夹具/运维补登记用；禁绕写者锁批量刷新）。"""
        return self._writer.publish_manifest(manifest)


def _assert_version_column(table: pa.Table, manifest: LedgerSnapshotManifest) -> None:
    """版本列铁律机器锁：缺列或行内代际与 manifest 不符一律拒读（禁覆盖语义）。"""
    if VERSION_COLUMN not in table.column_names:
        raise SnapshotVersionColumnError(f"快照缺 {VERSION_COLUMN} 版本列（旧代无版本快照）——拒读，禁覆盖语义")
    column = table[VERSION_COLUMN]
    distinct = pc.unique(column).to_pylist()
    if distinct != [manifest.ledger_version]:
        raise SnapshotVersionColumnError(f"快照行内代际与 manifest 不符: {distinct} != {manifest.ledger_version}")


def query_ledger_with_fallback(
    query: str,
    limit: int = 20,
    *,
    store: LedgerSnapshotStore | None = None,
    conn_factory: Callable[[], PgConnection] | None = None,
) -> LedgerQueryResult:
    """读侧总口：PG 可达以 PG 为准；PG 不可达回落快照并显式标降级/非真源。

    Args:
        query: 资产模糊查询串。
        limit: 返回上限。
        store: 快照层实例（默认按注入根目录构造）。
        conn_factory: PG 连接工厂（默认 DatabaseService 只读连接）。

    Returns:
        :class:`LedgerQueryResult`——``source`` ∈ {pg, snapshot}；快照态恒
        ``authoritative=False`` + ``degraded=True`` + 陈旧度；PG 态若快照损坏亦
        自报 ``snapshot_load_error``（不许吞异常）。

    Raises:
        SnapshotFallbackExhaustedError: PG 不可达且快照不可用（禁静默空结果）。
    """
    active_store = store or LedgerSnapshotStore(conn_factory=conn_factory)
    factory = conn_factory or _pg_conn
    _manifest, snapshot_error = active_store.verify()
    try:
        conn = factory()
        rows: list[dict[str, Any]] = Librarian(conn).lookup(query, limit=limit)
    except _PG_UNREACHABLE as exc:
        return _serve_from_snapshot(active_store, query, limit, exc)
    version = _manifest.ledger_version if _manifest else None
    return LedgerQueryResult(
        rows=rows,
        source="pg",
        ledger_version=version,
        degraded=snapshot_error is not None,
        authoritative=True,
        snapshot_load_error=snapshot_error,
    )


def _serve_from_snapshot(
    store: LedgerSnapshotStore,
    query: str,
    limit: int,
    pg_exc: BaseException,
) -> LedgerQueryResult:
    """回落通路：读快照成功=降级服务（自报非真源）；快照也不可用=报红上抛。"""
    try:
        manifest = store.read_manifest()
        rows = store.query(query, limit=limit)
    except SnapshotStoreError as snap_exc:
        raise SnapshotFallbackExhaustedError(
            f"PG 不可达（{type(pg_exc).__name__}）且快照不可用（{snap_exc}）——拒绝返回空结果"
        ) from snap_exc
    return LedgerQueryResult(
        rows=rows,
        source="snapshot",
        ledger_version=manifest.ledger_version if manifest else None,
        degraded=True,
        authoritative=False,
        degraded_reason=f"pg_unreachable:{type(pg_exc).__name__}:{pg_exc}",
    )


def refresh_snapshot(
    root: Path | None = None,
    *,
    conn_factory: Callable[[], PgConnection] | None = None,
    ledger_version: int | None = None,
) -> dict[str, Any]:
    """刷新挂接口（备份成功尾步调用；异常上抛由调用方决定 fail-open）。"""
    return LedgerSnapshotStore(root, conn_factory=conn_factory).refresh(ledger_version)


def _cli(args: Sequence[str]) -> int:
    store = LedgerSnapshotStore(Path(args.root) if getattr(args, "root", None) else None)
    if args.command == "status":
        manifest, error = store.verify()
        payload: dict[str, Any] = {
            "root": str(store.root),
            "generations": [version for version, _ in store.snapshot_files()],
            "manifest": manifest.to_json() if manifest else None,
            "error": error,
        }
        print(json.dumps(payload, ensure_ascii=False))
        return 0
    if args.command == "refresh":
        result = refresh_snapshot(store.root, ledger_version=args.ledger_version)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    result = store.query(args.query, limit=args.limit)
    for row in result:
        print(f"{row.get('asset_id')}\t{row.get('kind')}\t{row.get('status')}\t{row.get('home')}")
    return 0 if result else 1


def main(argv: Sequence[str] | None = None) -> int:
    """CLI 入口（status/refresh/query）；回落读用 :func:`query_ledger_with_fallback`。"""
    import argparse  # noqa: PLC0415

    parser = argparse.ArgumentParser(prog="zephyr.library.snapshot_store", description="图书馆账本本地快照层")
    parser.add_argument("command", choices=["status", "refresh", "query"])
    parser.add_argument("query", nargs="?", default="", help="[query] 模糊查询串")
    parser.add_argument("--root", default=None, help=f"快照根（默认 {DEFAULT_ROOT_REL} 或 env {ROOT_ENV_VAR}）")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--ledger-version", type=int, default=None, help="[refresh] 显式世代号（缺省走指纹单点入口）")
    args = parser.parse_args(list(argv) if argv is not None else None)
    return _cli(args)


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 快照层运维 CLI（status/refresh/query 人工按需巡检），事件触发主体在备份链尾步非本入口
    raise SystemExit(main())
