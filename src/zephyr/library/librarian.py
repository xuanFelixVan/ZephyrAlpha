# [BLUEPRINT] MOD-LIB-002 | docs/03_modules/_domain_library/blueprint.md | §2
# [MODULE] zephyr.library.librarian
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.library.schema; zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] zephyr.library.collectors; scripts/governance/generators/generate_library_index.py; scripts/governance/generators/check_library_coverage.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 馆员=总账唯一写路径；event 与 state 同事务（不登记不变更）；delete 必须携带处置预授权；全部 SQL 模块级常量（NO-BARE-SQL）
# [MODIFY-GUARD] gate_id 不适用；写路径 W+1 由 app 角色仅 EXECUTE 馆员函数收口（08 §3.3 权限收口）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] act 校验失败抛 ValueError；DB 异常原样上抛（调用方决定重试）
# [TESTS] tests/library/test_library_smoke.py
# [A_module] module_id=MOD-LIB-002 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""librarian.py — 馆员（Librarian）：总账唯一写路径（MOD-LIB-002）。

六权落地：登记/借阅/变更/迁移/注销/盘点统一走 :meth:`Librarian.act`，
事件与状态同事务（不登记不变更）；delete 强制处置预授权（死亡证明，08 §3.1）。
并发语义：PG MVCC 行级锁+事件只追加（08 §3.3 全局登记并发制）。
# [ALGO_FLOW] external: docs/03_modules/_domain_library/algo_flow/librarian.yaml
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Protocol


class PgCursor(Protocol):
    """总账游标最小结构协议（容器型 Any 豁免口径，5.145）。"""

    description: Sequence[tuple[Any, ...]]

    def execute(self, sql: str, params: object = None) -> None:
        """执行 SQL（参数化）。"""
        ...

    def fetchone(self) -> tuple[Any, ...] | None:
        """取单行。"""
        ...

    def fetchall(self) -> list[tuple[Any, ...]]:
        """取全部行。"""
        ...

    def close(self) -> None:
        """关闭游标。"""
        ...

    def __enter__(self) -> PgCursor:
        """上下文入口。"""
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        """上下文出口（关闭游标由驱动语义决定）。"""
        self.close()


class PgConnection(Protocol):
    """总账 PG 连接最小结构协议（duck-typing：psycopg2 连接天然满足）。"""

    def cursor(self) -> PgCursor:
        """返回游标。"""
        ...

    def commit(self) -> None:
        """提交当前事务。"""
        ...

    def close(self) -> None:
        """关闭连接。"""
        ...


import json
from typing import Any, Final, Protocol

from zephyr.library.ledger_schema import (
    _SQL_ENSURE_ASSETS,
    _SQL_ENSURE_EVENTS,
    _SQL_INSERT_EVENT,
    _SQL_LOOKUP,
    _SQL_MARK_DECEASED,
    _SQL_UPSERT_ASSET,
    validate_action,
)

__all__ = ["Librarian", "PgConnection"]  # noqa: n114-final  n114-final豁免: __all__是Python导出约定，非可变常量，无需Final标注（先例=asyncio_run_in_context_gate.py L77）


class Librarian:
    """总账馆员：登记/借阅/变更/迁移/注销/盘点唯一读写路径。"""

    def __init__(self, conn: PgConnection) -> None:
        """注入 PG 连接（depgraph 资产总线）。

        Args:
            conn: psycopg2 连接对象（结构满足 :class:`PgConnection` 协议）。
        """
        self._conn = conn

    def ensure_schema(self) -> None:
        """确保总账两表存在（幂等 DDL）。"""
        with self._conn.cursor() as cur:
            cur.execute(_SQL_ENSURE_ASSETS)
            cur.execute(_SQL_ENSURE_EVENTS)
        self._conn.commit()

    def act(
        self,
        action: str,
        asset_id: str,
        *,
        actor: str = "",
        fields: dict[str, Any] | None = None,
        authority: str | None = None,
        detail: dict[str, Any] | None = None,
    ) -> int:
        """馆员唯一写动作：先记事件、再更新状态，同事务提交。

        采用字段字典参数（Builder 思路，规避 Long Parameter List 反模式）。

        Args:
            action: register/read/update/move/delete/audit 之一。
            asset_id: 资产身份证号。
            actor: 执行会话标识。
            fields: 户籍字段字典（kind/home/fingerprint_sha256/fingerprint_aux/
                title/ai_contract/owner_domain/retention_class/status/tags）。
            authority: 处置预授权（delete 必填，死亡证明）。
            detail: 事件 detail 附加信息。

        Returns:
            事件 ID。

        Raises:
            ValueError: 动作非法或 delete 无授权。
        """
        validate_action(action, authority)
        f = fields or {}
        kind = f.get("kind", "")
        home = f.get("home", "")
        fingerprint_sha256 = f.get("fingerprint_sha256")
        fingerprint_aux = f.get("fingerprint_aux")
        title = f.get("title")
        ai_contract = f.get("ai_contract")
        owner_domain = f.get("owner_domain")
        retention_class = f.get("retention_class", "long")
        status = f.get("status")
        tags_list = f.get("tags") or []
        detail_json = json.dumps(detail or {}, ensure_ascii=False)
        aux_json = json.dumps(fingerprint_aux or {}, ensure_ascii=False)
        with self._conn.cursor() as cur:
            cur.execute(_SQL_INSERT_EVENT, (asset_id, action, actor, True, detail_json))
            cur.execute("SELECT lastval()")
            event_id = int(cur.fetchone()[0])
            if action in ("register", "update", "move"):
                cur.execute(
                    _SQL_UPSERT_ASSET,
                    (
                        asset_id,
                        kind,
                        home,
                        fingerprint_sha256,
                        aux_json,
                        status,
                        owner_domain,
                        retention_class,
                        title,
                        ai_contract,
                        tags_list,
                        actor,
                    ),
                )
            if action == "delete":
                cur.execute(_SQL_MARK_DECEASED, (authority, asset_id))
        self._conn.commit()
        return event_id

    def register_batch(self, assets: list[dict[str, Any]], actor: str) -> int:
        """批量登记（采集器全量入账专用：单事务，避免逐条 commit 风暴）。

        Args:
            assets: 采集器资产列表（error 项与无 asset_id 项自动跳过）。
            actor: 登记会话标识。

        Returns:
            实际登记条数。
        """
        count = 0
        with self._conn.cursor() as cur:
            for asset in assets:
                if "error" in asset or not asset.get("asset_id"):
                    continue
                aux_json = json.dumps(asset.get("fingerprint_aux") or {}, ensure_ascii=False)
                detail_json = json.dumps({"source": "collector"}, ensure_ascii=False)
                cur.execute(
                    _SQL_INSERT_EVENT,
                    (asset["asset_id"], "register", actor, True, detail_json),
                )
                cur.execute(
                    _SQL_UPSERT_ASSET,
                    (
                        asset["asset_id"],
                        asset.get("kind", "file"),
                        asset.get("home", ""),
                        asset.get("fingerprint_sha256"),
                        aux_json,
                        None,
                        asset.get("owner_domain"),
                        "long",
                        asset.get("title"),
                        asset.get("ai_contract"),
                        asset.get("tags") or [],
                        actor,
                    ),
                )
                count += 1
        self._conn.commit()
        return count

    def lookup(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        """借阅：按 ID/home/标题模糊定位资产。

        Args:
            query: 查询串。
            limit: 返回上限。

        Returns:
            资产行字典列表。

        """
        escaped = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        pattern = f"%{escaped}%"
        with self._conn.cursor() as cur:
            cur.execute(_SQL_LOOKUP, (pattern, pattern, pattern, limit))
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row, strict=True)) for row in cur.fetchall()]
