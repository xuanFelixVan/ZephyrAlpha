# [BLUEPRINT] MOD-ALT-007 | docs/03_modules/_domain_alt_data/alt_data_connector/blueprint.md
# [MODULE] zephyr.alt_data.alt_data_connector
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] 无（接入核心纯内存；fetcher/adapter/cipher/clock/health_sink 全注入；采集语义参照 zephyr.data.news_collector）
# [CONSUMERS] 运行时装配批（三类连接器声明 / 真实 fetcher 与 cipher 绑定 / source_health 接健康度路由）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 连接器词表闭合(news|announcement|social); 免费源优先排序(free 降序, connector_id 升序)确定性; API密钥仅落密文(注入cipher，明文绝不入库); 增量游标断点续传(checkpoint导出/恢复，下一游标须非空str); 原始层按external_id去重幂等; fetcher未注入同步Fail-Closed不旁路; 每次同步必登记source_health(回调异常不阻断); 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_alt_data/alt_data_connector/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AltDataConnectorError(占位 ZA-ALT-UNREGISTERED-ALT-CONNECTOR)——重复/未知连接器、非法kind、适配器缺失或不可调用、密钥空/cipher缺失、游标非法、fetcher未注入或抓取/适配异常时抛
# [TESTS] tests/alt_data/test_alt_data_connector.py
# [A_module] module_id=MOD-ALT-007 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""AltDataConnector — 另类数据统一接入器（MOD-ALT-007）。

B5-07081（AUD-DRAFT-001-DIGEST P2 波 P2-W04，CAND-TESTA-022，B5 D-ALT-DATA-01）：
统一另类数据接入层——新闻/公告/社交**三类连接器注册表**（免费源优先）+
**格式适配**（适配器协议：原始载荷 → (external_id, 规范化载荷)）+**增量同步
游标**（断点续传 checkpoint 导出/恢复）+**API 密钥加密存储**（注入 cipher，
仅落密文）+ 落原始层登记 **source_health**（健康登记回调）。AkShare/巨潮 RSS
语义，API 全注入不真发。

查重分工（蓝图 §0）：news_collector=新闻采集面实现（本件=跨类别接入注册表与
同步协议层，不实现具体源抓取）；social_sentiment_collector=社媒帖子级采集
（本件仅注册其连接器声明）；alt_source_health_manager=健康度评分/降级阶梯
（本件仅登记 source_health 原始事实，不做评分/切源）。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "AltDataConnector",
    "AltDataConnectorError",
    "AltDataRecord",
    "ConnectorKind",
    "ConnectorSpec",
    "SourceHealth",
    "SyncCheckpoint",
]


class AltDataConnectorError(Exception):
    """另类数据接入输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-ALT-UNREGISTERED-ALT-CONNECTOR。
    """


class ConnectorKind(str, Enum):
    """连接器类别（词表闭合）。"""

    NEWS = "news"
    ANNOUNCEMENT = "announcement"
    SOCIAL = "social"


@dataclass(frozen=True)
class ConnectorSpec:
    """连接器声明（注册表条目，frozen）。"""

    connector_id: str
    kind: ConnectorKind
    free: bool = True
    description: str = ""


@dataclass(frozen=True)
class AltDataRecord:
    """原始层记录（格式适配后的规范化载荷，frozen）。"""

    connector_id: str
    external_id: str
    payload: dict
    fetched_at: datetime.datetime


@dataclass(frozen=True)
class SyncCheckpoint:
    """增量同步游标（断点续传持久化载体，frozen）。"""

    connector_id: str
    cursor: str | None
    exported_at: datetime.datetime


@dataclass(frozen=True)
class SourceHealth:
    """源健康登记事实（每次同步一条，frozen）。"""

    connector_id: str
    success: bool
    new_records: int
    detail: str
    reported_at: datetime.datetime


class AltDataConnector:
    """另类数据统一接入器（注册表 + 格式适配 + 增量游标 + 密钥保管 + 健康登记）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        fetcher: Callable[[ConnectorSpec, "str | None"], "tuple[list[Mapping], str]"] | None = None,
        cipher_encrypt: Callable[[str], str] | None = None,
        cipher_decrypt: Callable[[str], str] | None = None,
        health_sink: Callable[[SourceHealth], None] | None = None,
    ) -> None:
        for name, fn in (
            ("clock", clock),
            ("fetcher", fetcher),
            ("cipher_encrypt", cipher_encrypt),
            ("cipher_decrypt", cipher_decrypt),
            ("health_sink", health_sink),
        ):
            if fn is not None and not callable(fn):
                raise AltDataConnectorError(f"{name} 非 callable")
        self._clock = clock or datetime.datetime.now
        self._fetcher = fetcher
        self._encrypt = cipher_encrypt
        self._decrypt = cipher_decrypt
        self._health_sink = health_sink
        self._connectors: dict[str, ConnectorSpec] = {}
        self._adapters: dict[str, Callable[[Mapping], "tuple[str, Mapping]"]] = {}
        self._cursors: dict[str, str] = {}
        self._records: dict[str, list[AltDataRecord]] = {}
        self._seen: dict[str, set[str]] = {}
        self._keys: dict[str, str] = {}
        self._health: dict[str, SourceHealth] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _spec_of(self, connector_id: str) -> ConnectorSpec:
        spec = self._connectors.get(connector_id)
        if spec is None:
            raise AltDataConnectorError(f"未知连接器: {connector_id!r}（未注册）")
        return spec

    def _report_health(self, connector_id: str, success: bool, new_records: int, detail: str) -> None:
        health = SourceHealth(
            connector_id=connector_id,
            success=success,
            new_records=new_records,
            detail=detail,
            reported_at=self._clock(),
        )
        self._health[connector_id] = health
        if not success:
            _log.warning("source_health 失败: %s (%s)", connector_id, detail)
        if self._health_sink is not None:
            try:
                self._health_sink(health)
            except Exception:  # noqa: BLE001 — 健康回调不阻断（蓝图 §1）
                _log.exception("health_sink 回调失败")

    # ── 连接器注册表 ──────────────────────────────────────────────────────

    def register(self, spec: ConnectorSpec) -> None:
        """登记连接器：connector_id 非空唯一、kind 词表闭合。"""
        if not isinstance(spec, ConnectorSpec):
            raise AltDataConnectorError(f"spec 类型非法: {type(spec)!r}")
        if not isinstance(spec.connector_id, str) or not spec.connector_id:
            raise AltDataConnectorError("connector_id 为空")
        if not isinstance(spec.kind, ConnectorKind):
            raise AltDataConnectorError(
                f"非法连接器类别: {spec.kind!r}（词表闭合 news|announcement|social）"
            )
        if not isinstance(spec.free, bool):
            raise AltDataConnectorError(f"free 必须为 bool: {spec.free!r}")
        if spec.connector_id in self._connectors:
            raise AltDataConnectorError(f"connector_id 重复: {spec.connector_id!r}")
        self._connectors[spec.connector_id] = spec
        self._records[spec.connector_id] = []
        self._seen[spec.connector_id] = set()

    def set_adapter(self, connector_id: str, adapter: Callable[[Mapping], "tuple[str, Mapping]"]) -> None:
        """绑定格式适配器（协议：原始载荷 → (external_id, 规范化载荷)）。"""
        self._spec_of(connector_id)
        if not callable(adapter):
            raise AltDataConnectorError("adapter 非 callable")
        self._adapters[connector_id] = adapter

    def list_connectors(self, kind: ConnectorKind | None = None) -> tuple[ConnectorSpec, ...]:
        """连接器清单：免费源优先，同档按 connector_id 升序（确定性）。"""
        if kind is not None and not isinstance(kind, ConnectorKind):
            raise AltDataConnectorError(f"非法连接器类别: {kind!r}")
        specs = [s for s in self._connectors.values() if kind is None or s.kind is kind]
        specs.sort(key=lambda s: (not s.free, s.connector_id))
        return tuple(specs)

    # ── API 密钥加密保管 ──────────────────────────────────────────────────

    def store_api_key(self, connector_id: str, plaintext_key: str) -> None:
        """加密保管 API 密钥：仅落密文（cipher 未注入 Fail-Closed）。"""
        self._spec_of(connector_id)
        if not isinstance(plaintext_key, str) or not plaintext_key:
            raise AltDataConnectorError("plaintext_key 为空")
        if self._encrypt is None:
            raise AltDataConnectorError("cipher_encrypt 未注入（密钥仅可密文保管，禁止明文落库）")
        self._keys[connector_id] = self._encrypt(plaintext_key)

    def has_api_key(self, connector_id: str) -> bool:
        """密钥存在性查询。"""
        self._spec_of(connector_id)
        return connector_id in self._keys

    def get_api_key(self, connector_id: str) -> str:
        """解密读取密钥（无密钥/无 decrypt cipher → Fail-Closed）。"""
        self._spec_of(connector_id)
        blob = self._keys.get(connector_id)
        if blob is None:
            raise AltDataConnectorError(f"连接器 {connector_id!r} 无已存密钥")
        if self._decrypt is None:
            raise AltDataConnectorError("cipher_decrypt 未注入（无法解密密钥）")
        return self._decrypt(blob)

    # ── 增量同步（断点续传） ──────────────────────────────────────────────

    def sync(self, connector_id: str) -> int:
        """增量同步：游标续传 → 注入 fetcher 抓取 → 适配落原始层 → 登记 source_health。

        返回本次新落库条数；external_id 去重幂等；任一环失败登记失败健康并
        Fail-Closed（游标不前移，重试安全）。
        """
        spec = self._spec_of(connector_id)
        adapter = self._adapters.get(connector_id)
        if adapter is None:
            raise AltDataConnectorError(f"连接器 {connector_id!r} 未绑定格式适配器")
        if self._fetcher is None:
            raise AltDataConnectorError("fetcher 未注入（API 全注入不真发，禁止旁路）")
        cursor = self._cursors.get(connector_id)
        try:
            raw_batch, next_cursor = self._fetcher(spec, cursor)
        except Exception as exc:
            self._report_health(connector_id, False, 0, f"fetcher 抓取异常: {exc!r}")
            raise AltDataConnectorError(f"fetcher 抓取异常: {connector_id!r}: {exc}") from exc
        if not isinstance(raw_batch, (list, tuple)):
            self._report_health(connector_id, False, 0, "raw_batch 类型非法")
            raise AltDataConnectorError(f"raw_batch 类型非法: {type(raw_batch)!r}（须 list/tuple）")
        if not isinstance(next_cursor, str) or not next_cursor:
            self._report_health(connector_id, False, 0, "next_cursor 非法")
            raise AltDataConnectorError(f"next_cursor 非法: {next_cursor!r}（须非空 str）")

        new_count = 0
        for raw in raw_batch:
            try:
                external_id, payload = adapter(raw)
            except Exception as exc:
                self._report_health(connector_id, False, new_count, f"adapter 适配异常: {exc!r}")
                raise AltDataConnectorError(f"adapter 适配异常: {connector_id!r}: {exc}") from exc
            if not isinstance(external_id, str) or not external_id:
                self._report_health(connector_id, False, new_count, "external_id 非法")
                raise AltDataConnectorError(f"external_id 非法: {external_id!r}（须非空 str）")
            if not isinstance(payload, Mapping):
                self._report_health(connector_id, False, new_count, "payload 类型非法")
                raise AltDataConnectorError(f"payload 类型非法: {type(payload)!r}（须 Mapping）")
            if external_id in self._seen[connector_id]:
                continue  # 幂等去重（断点重传安全）
            self._records[connector_id].append(AltDataRecord(
                connector_id=connector_id,
                external_id=external_id,
                payload=dict(payload),
                fetched_at=self._clock(),
            ))
            self._seen[connector_id].add(external_id)
            new_count += 1
        self._cursors[connector_id] = next_cursor
        self._report_health(connector_id, True, new_count, f"同步成功 next_cursor={next_cursor!r}")
        return new_count

    # ── checkpoint 导出/恢复 ──────────────────────────────────────────────

    def export_checkpoint(self, connector_id: str) -> SyncCheckpoint:
        """导出断点 checkpoint（未同步过 cursor=None）。"""
        self._spec_of(connector_id)
        return SyncCheckpoint(
            connector_id=connector_id,
            cursor=self._cursors.get(connector_id),
            exported_at=self._clock(),
        )

    def restore_checkpoint(self, checkpoint: SyncCheckpoint) -> None:
        """恢复断点 checkpoint（续传语义：下一次 sync 自该游标起抓）。"""
        if not isinstance(checkpoint, SyncCheckpoint):
            raise AltDataConnectorError(f"checkpoint 类型非法: {type(checkpoint)!r}")
        self._spec_of(checkpoint.connector_id)
        if not isinstance(checkpoint.cursor, str) or not checkpoint.cursor:
            raise AltDataConnectorError(f"checkpoint cursor 非法: {checkpoint.cursor!r}（须非空 str）")
        self._cursors[checkpoint.connector_id] = checkpoint.cursor

    # ── 查询 ─────────────────────────────────────────────────────────────

    def records(self, connector_id: str) -> tuple[AltDataRecord, ...]:
        """原始层记录（落库序，确定性）。"""
        self._spec_of(connector_id)
        return tuple(self._records[connector_id])

    def cursor_of(self, connector_id: str) -> "str | None":
        """当前增量游标（未同步过 → None）。"""
        self._spec_of(connector_id)
        return self._cursors.get(connector_id)

    def latest_health(self, connector_id: str) -> "SourceHealth | None":
        """最近一次 source_health（未同步过 → None）。"""
        self._spec_of(connector_id)
        return self._health.get(connector_id)
