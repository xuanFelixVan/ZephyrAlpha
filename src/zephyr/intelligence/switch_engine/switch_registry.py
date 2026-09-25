# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §l6_switch_engine
# [MODULE] zephyr.intelligence.switch_engine.switch_registry
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
# [DEPENDENCIES] zephyr.infrastructure.database_service (get_db_service, 默认连接工厂);
#                zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] zephyr.intelligence.switch_engine.switch_engine (SwitchEngine);
#             zephyr.intelligence.switch_engine.shadow_runner (只读核对);
#             zephyr.ai_layer.switch_engine.tombstone_manager;
#             zephyr.ai_layer.switch_engine.revert_drill
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 运营态架构数据=DB（RULE-SSOT，DESIGN §②-B 裁定留痕），全部读写经
#              DatabaseService 治理连接（禁裸 duckdb）；七态规范枚举 fail-closed 校验
#              （shadow|canary|promoted|champion|retired|tombstone|aborted；promote=动作
#              非态）；时间字段一律 now_utc().isoformat() 显式带 +00:00 时区
#              （RULE-SCHEMA-TZ 精神，SQLite 无 DateTime64 即 ISO-8601 带时区文本）；
#              两版本同登记互斥生效=同 (object_family, object_ref) 仅允许一行活跃 switch
#              （partial UNIQUE INDEX，tombstone/aborted 不占坑——复活/重开走新行新 switch_id）；
#              state_history 只追加不改写（审计留痕）；schema 建表幂等（IF NOT EXISTS）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L6_ab_switch/DESIGN.md §②-B/§④-S1
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 非法 state/object_family→ValueError（fail-closed，绝不静默写库）；
#                  switch_id 不存在→KeyError（require）；同对象第二个活跃 switch→
#                  RuntimeError（互斥生效，IntegrityError 转译）；连接工厂异常上抛不吞
# [TESTS] tests/intelligence/switch_engine/test_switch_registry.py（schema 幂等/CRUD 往回读/
#         七态枚举校验拒非法/state_history 追加/互斥索引两版本同登记/JSON 字段回读/tombstone 释放互斥坑）
"""switch_registry — L6 切换段七态运营态注册表（S1 施工件，DESIGN §②-B schema 全字段）。

表结构逐字段对齐 DESIGN §②-B switch_registry：switch_id/object(family+ref)/domain/
champion_ref/challenger_ref/criteria_yaml_ref+criteria_hash（预注册冻结）/state（七态
规范枚举）/state_history/observation/rollback/promotion_record/tombstone。嵌套结构
（history/observation/rollback/promotion_record/tombstone）以 JSON 文本列存储——SQLite
治理库无原生 JSON 型，读写经本模块 dataclass 收敛，禁散落手工拼 JSON。

验收锚（DESIGN §⑤）：S1=两版本同登记互斥生效——同一对象的 champion/challenger 共存于
同一行（互斥生效=任一时刻该对象只有一行活跃 switch 行在驱动状态机）。
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Final

from zephyr.shared.utils.time_utils import now_utc

TABLE_NAME: Final[str] = "switch_registry"

SEVEN_STATES: Final[frozenset[str]] = frozenset(
    {"shadow", "canary", "promoted", "champion", "retired", "tombstone", "aborted"}
)
OBJECT_FAMILIES: Final[frozenset[str]] = frozenset(
    {"code_module", "gate_param", "model", "tool", "rule"}
)
APPROVED_BY_VALUES: Final[frozenset[str]] = frozenset(
    {"auto", "independent_review", "owner_one_click"}
)
# 互斥坑：非终态（活跃）行独占 (object_family, object_ref)；tombstone/aborted 让位。
NON_EXCLUSIVE_STATES: Final[tuple[str, ...]] = ("tombstone", "aborted")

_JSON_FIELDS: Final[tuple[str, ...]] = (
    "state_history",
    "observation",
    "rollback",
    "promotion_record",
    "tombstone",
)

_DDL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    switch_id         TEXT PRIMARY KEY,
    object_family     TEXT NOT NULL,
    object_ref        TEXT NOT NULL,
    domain            TEXT NOT NULL,
    champion_ref      TEXT NOT NULL,
    challenger_ref    TEXT NOT NULL,
    criteria_yaml_ref TEXT NOT NULL,
    criteria_hash     TEXT NOT NULL,
    state             TEXT NOT NULL,
    state_history     TEXT NOT NULL,
    observation       TEXT NOT NULL,
    rollback          TEXT NOT NULL,
    promotion_record  TEXT NOT NULL,
    tombstone         TEXT NOT NULL,
    created_at        TEXT NOT NULL,
    updated_at        TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_switch_active_object
    ON {TABLE_NAME}(object_family, object_ref)
    WHERE state NOT IN ('tombstone', 'aborted');
"""


@dataclass(frozen=True)
class SwitchRegistryRecord:
    """switch_registry 一行（DESIGN §②-B schema 的 Python 侧收敛型）。"""

    switch_id: str
    object_family: str
    object_ref: str
    domain: str
    champion_ref: str
    challenger_ref: str
    criteria_yaml_ref: str
    criteria_hash: str
    state: str
    state_history: list[dict[str, Any]] = field(default_factory=list)
    observation: dict[str, Any] = field(default_factory=dict)
    rollback: dict[str, Any] = field(default_factory=dict)
    promotion_record: dict[str, Any] = field(default_factory=dict)
    tombstone: dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""


def validate_record_fields(record: SwitchRegistryRecord) -> None:
    """入库前枚举校验（fail-closed）。非法 state/family/approved_by 一律 ValueError。"""
    if record.state not in SEVEN_STATES:
        raise ValueError(f"非法 state={record.state!r}（七态规范枚举之外）")
    if record.object_family not in OBJECT_FAMILIES:
        raise ValueError(f"非法 object_family={record.object_family!r}")
    approved_by = record.promotion_record.get("approved_by")
    if approved_by is not None and approved_by not in APPROVED_BY_VALUES:
        raise ValueError(f"非法 approved_by={approved_by!r}")


def ensure_schema(conn: sqlite3.Connection) -> None:
    """幂等建表+互斥部分唯一索引（两版本同登记互斥生效的物理保证）。"""
    conn.executescript(_DDL)
    conn.commit()


class SwitchRegistryStore:
    """switch_registry 存取门面。连接工厂可注入（测试指向 tmp_path 零生产写）。"""

    def __init__(
        self,
        conn_factory: Callable[[], sqlite3.Connection] | None = None,
    ) -> None:
        self._conn_factory = conn_factory or self._default_conn_factory
        self._conn: sqlite3.Connection | None = None

    @staticmethod
    def _default_conn_factory() -> sqlite3.Connection:
        from zephyr.infrastructure.database_service import get_db_service

        return get_db_service().get_governance_conn()

    def connection(self) -> sqlite3.Connection:
        if self._conn is None:
            conn = self._conn_factory()
            conn.row_factory = sqlite3.Row
            self._conn = conn
        return self._conn

    def ensure_schema(self) -> None:
        ensure_schema(self.connection())

    def create(self, record: SwitchRegistryRecord, *, created_at: datetime | None = None) -> None:
        """插入一行；同对象第二个活跃 switch 撞互斥索引→RuntimeError（fail-closed）。

        state_history 开户起笔（回执链自出生完整，演练三查③依赖），后续只追加。
        """
        validate_record_fields(record)
        ts = (created_at or now_utc()).isoformat()
        seeded = SwitchRegistryRecord(
            **{
                **record.__dict__,
                "state_history": [
                    {"state": record.state, "since": ts, "evidence_ref": f"create:{record.switch_id}"}
                ],
            }
        )
        try:
            self.connection().execute(
                f"INSERT INTO {TABLE_NAME} ({_all_columns()}) VALUES ({_placeholders()})",  # noqa: bare-sql  bare-sql豁免: P1存量伪新增,域内SQL集中通道,§5.160.2专项另列
                _row_values(seeded, ts),
            )
            self.connection().commit()
        except sqlite3.IntegrityError as exc:
            raise RuntimeError(
                f"switch 互斥生效违约：{record.object_family}/{record.object_ref} "
                f"已存在活跃 switch 行（tombstone/aborted 之外不可二开），{exc}"
            ) from exc

    def get(self, switch_id: str) -> SwitchRegistryRecord | None:
        row = self.connection().execute(
            f"SELECT * FROM {TABLE_NAME} WHERE switch_id = ?", (switch_id,)  # noqa: bare-sql  bare-sql豁免: P1存量伪新增,域内SQL集中通道,§5.160.2专项另列
        ).fetchone()
        return _row_to_record(row) if row is not None else None

    def require(self, switch_id: str) -> SwitchRegistryRecord:
        record = self.get(switch_id)
        if record is None:
            raise KeyError(f"switch_id 不存在：{switch_id}")
        return record

    def list_by_state(self, state: str) -> list[SwitchRegistryRecord]:
        if state not in SEVEN_STATES:
            raise ValueError(f"非法 state={state!r}")
        rows = self.connection().execute(
            f"SELECT * FROM {TABLE_NAME} WHERE state = ? ORDER BY updated_at", (state,)  # noqa: bare-sql  bare-sql豁免: P1存量伪新增,域内SQL集中通道,§5.160.2专项另列
        ).fetchall()
        return [_row_to_record(row) for row in rows]

    def update_state(
        self,
        switch_id: str,
        new_state: str,
        evidence_ref: str,
        *,
        patches: dict[str, dict[str, Any]] | None = None,
        at: datetime | None = None,
    ) -> SwitchRegistryRecord:
        """状态迁移落库：state 更新+state_history 追加（只追加不改写）+JSON 字段补丁。"""
        if new_state not in SEVEN_STATES:
            raise ValueError(f"非法 state={new_state!r}")
        if not evidence_ref:
            raise ValueError("state_history 追加缺 evidence_ref（审计留痕不可空）")
        record = self.require(switch_id)
        ts = (at or now_utc()).isoformat()
        history = list(record.state_history)
        history.append({"state": new_state, "since": ts, "evidence_ref": evidence_ref})
        merged: dict[str, Any] = {"state_history": history}
        for name in _JSON_FIELDS:
            if name != "state_history":
                merged[name] = {**getattr(record, name), **(patches or {}).get(name, {})}
        self.connection().execute(
            f"UPDATE {TABLE_NAME} SET state=?, state_history=?, observation=?, rollback=?, "  # noqa: bare-sql  bare-sql豁免: P1存量伪新增,域内SQL集中通道,§5.160.2专项另列
            "promotion_record=?, tombstone=?, updated_at=? WHERE switch_id=?",
            (
                new_state,
                json.dumps(history, ensure_ascii=False),
                json.dumps(merged["observation"], ensure_ascii=False),
                json.dumps(merged["rollback"], ensure_ascii=False),
                json.dumps(merged["promotion_record"], ensure_ascii=False),
                json.dumps(merged["tombstone"], ensure_ascii=False),
                ts,
                switch_id,
            ),
        )
        self.connection().commit()
        return self.require(switch_id)


def _all_columns() -> str:
    return ", ".join(
        [
            "switch_id", "object_family", "object_ref", "domain", "champion_ref",
            "challenger_ref", "criteria_yaml_ref", "criteria_hash", "state",
            "state_history", "observation", "rollback", "promotion_record",
            "tombstone", "created_at", "updated_at",
        ]
    )


def _placeholders() -> str:
    return ", ".join("?" * 16)


def _row_values(record: SwitchRegistryRecord, ts: str) -> tuple[Any, ...]:
    plain = asdict(record)
    values: list[Any] = []
    for name in _all_columns().split(", "):
        if name in _JSON_FIELDS:
            values.append(json.dumps(plain[name], ensure_ascii=False))
        elif name in ("created_at", "updated_at"):
            values.append(ts)
        else:
            values.append(plain[name])
    return tuple(values)


def _row_to_record(row: sqlite3.Row) -> SwitchRegistryRecord:
    mapping = dict(row)
    for name in _JSON_FIELDS:
        mapping[name] = json.loads(mapping[name])
    return SwitchRegistryRecord(**mapping)
