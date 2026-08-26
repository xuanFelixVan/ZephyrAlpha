# [BLUEPRINT] MOD-RK-044 | docs/03_modules/_domain_risk/risk_policy_persister/blueprint.md
# [MODULE] zephyr.risk.risk_policy_persister
# [DOMAIN] D_RISK
# [DEPENDENCIES] sqlite3（连接注入）；无其他（时钟全注入）
# [CONSUMERS] 运行时装配批（风控策略持久化装配 / 与 risk_limits 运行时限额双向同步校验）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 三表DDL幂等(CREATE IF NOT EXISTS); 版本递增(每策略max+1)不可变(无更新/删除路径); 激活版本原子热加载(单事务切换+内存指针同步); 限额值Decimal文本落库; 漂移清单按limit_key确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_risk/risk_policy_persister/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] RiskPolicyError(占位 ZA-RK-UNREGISTERED-RISK-POLICY)——连接未注入/空policy_id/空限额集/未知策略或版本/激活事务失败时抛
# [TESTS] tests/risk/test_risk_policy_persister.py
# [A_module] module_id=MOD-RK-044 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""RiskPolicyPersister — 风控策略持久化器（MOD-RK-044）。

B13-04311（AUD-DRAFT-001-DIGEST P2 波 P2-W09，CAND-RSK-048，A3 D-RISK-49）：
风控策略 SQLite 持久化——risk_policy / risk_limit / risk_policy_version 三表
（连接注入）+ 版本递增不可变 + 激活版本热加载（切换原子）+ 与 risk_limits
契约双向同步校验（漂移清单）。

查重分工（蓝图 §0）：risk_limits=限额计算引擎接口（本件=限额的持久化与版本
治理，不做限额计算）；var_calculator=VaR 计算（本件仅持久化限额键值）；运行
时限额消费由运行时装配批注入同步校验，本件不直连组合优化器。
"""

from __future__ import annotations

import datetime
import logging
import sqlite3
from dataclasses import dataclass
from decimal import Decimal
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "PolicyDrift",
    "PolicyVersion",
    "RiskPolicy",
    "RiskPolicyError",
    "RiskPolicyPersister",
]

_DDL: Final = (
    """
    CREATE TABLE IF NOT EXISTS risk_policy (
        policy_id   TEXT PRIMARY KEY,
        name        TEXT NOT NULL,
        created_at  TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS risk_policy_version (
        policy_id   TEXT NOT NULL,
        version     INTEGER NOT NULL,
        created_at  TEXT NOT NULL,
        is_active   INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (policy_id, version)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS risk_limit (
        policy_id   TEXT NOT NULL,
        version     INTEGER NOT NULL,
        limit_key   TEXT NOT NULL,
        limit_value TEXT NOT NULL,
        PRIMARY KEY (policy_id, version, limit_key)
    )
    """,
)


class RiskPolicyError(Exception):
    """风控策略持久化输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-RK-UNREGISTERED-RISK-POLICY。
    """


@dataclass(frozen=True)
class RiskPolicy:
    """风控策略 Schema（限额键值集，frozen，金额/比率 Decimal）。"""

    policy_id: str
    name: str
    limits: Mapping[str, Decimal]


@dataclass(frozen=True)
class PolicyVersion:
    """策略版本快照（版本递增不可变，frozen）。"""

    policy_id: str
    version: int
    limits: Mapping[str, Decimal]
    created_at: datetime.datetime
    is_active: bool


@dataclass(frozen=True)
class PolicyDrift:
    """双向同步漂移条目（持久化侧 vs risk_limits 运行侧，frozen）。"""

    limit_key: str
    persisted: Decimal | None
    live: Decimal | None


class RiskPolicyPersister:
    """风控策略持久化器（三表 DDL + 版本不可变 + 原子热加载 + 同步校验）。"""

    def __init__(
        self,
        *,
        conn: sqlite3.Connection | None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if conn is None:
            raise RiskPolicyError("sqlite3 连接未注入（Fail-Closed 不旁路）")
        self._conn = conn
        self._clock = clock or datetime.datetime.now
        for ddl in _DDL:
            self._conn.execute(ddl)
        self._conn.commit()
        self._active: dict[str, PolicyVersion] = {}
        self._reload_active()

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _reload_active(self) -> None:
        """启动时从库内恢复激活指针（热加载语义）。"""
        rows = self._conn.execute(
            "SELECT policy_id, version FROM risk_policy_version WHERE is_active = 1 "
            "ORDER BY policy_id"
        ).fetchall()
        for policy_id, version in rows:
            self._active[policy_id] = self._load_version(policy_id, version)

    def _load_version(self, policy_id: str, version: int) -> PolicyVersion:
        row = self._conn.execute(
            "SELECT created_at, is_active FROM risk_policy_version "
            "WHERE policy_id = ? AND version = ?",
            (policy_id, version),
        ).fetchone()
        if row is None:
            raise RiskPolicyError(f"未知策略版本: {policy_id!r} v{version}")
        limits_rows = self._conn.execute(
            "SELECT limit_key, limit_value FROM risk_limit "
            "WHERE policy_id = ? AND version = ? ORDER BY limit_key",
            (policy_id, version),
        ).fetchall()
        return PolicyVersion(
            policy_id=policy_id,
            version=version,
            limits={k: Decimal(v) for k, v in limits_rows},
            created_at=datetime.datetime.fromisoformat(row[0]),
            is_active=bool(row[1]),
        )

    # ── 版本递增不可变 ────────────────────────────────────────────────────

    def save_policy(self, policy: RiskPolicy) -> int:
        """保存策略 → 新版本（max+1 递增，历史版本不可变，无更新/删除路径）。"""
        if not isinstance(policy, RiskPolicy):
            raise RiskPolicyError(f"非法策略: {policy!r}")
        if not policy.policy_id:
            raise RiskPolicyError("policy_id 为空")
        if not policy.limits:
            raise RiskPolicyError("限额集为空")
        for key, value in policy.limits.items():
            if not key:
                raise RiskPolicyError("limit_key 为空")
            if not isinstance(value, Decimal):
                raise RiskPolicyError(f"限额值非 Decimal: {key!r}")

        now = self._clock().isoformat()
        row = self._conn.execute(
            "SELECT MAX(version) FROM risk_policy_version WHERE policy_id = ?",
            (policy.policy_id,),
        ).fetchone()
        next_version = (row[0] or 0) + 1
        try:
            with self._conn:  # 单事务原子落库
                self._conn.execute(
                    "INSERT OR IGNORE INTO risk_policy(policy_id, name, created_at) "
                    "VALUES (?, ?, ?)",
                    (policy.policy_id, policy.name, now),
                )
                self._conn.execute(
                    "INSERT INTO risk_policy_version(policy_id, version, created_at, "
                    "is_active) VALUES (?, ?, ?, 0)",
                    (policy.policy_id, next_version, now),
                )
                for key in sorted(policy.limits):
                    self._conn.execute(
                        "INSERT INTO risk_limit(policy_id, version, limit_key, "
                        "limit_value) VALUES (?, ?, ?, ?)",
                        (policy.policy_id, next_version, key, str(policy.limits[key])),
                    )
        except sqlite3.Error as exc:
            raise RiskPolicyError(f"策略版本落库失败: {exc}") from exc
        return next_version

    # ── 激活版本原子热加载 ────────────────────────────────────────────────

    def activate(self, policy_id: str, version: int) -> PolicyVersion:
        """激活指定版本：单事务切换 is_active + 内存指针同步（原子热加载）。"""
        snapshot = self._load_version(policy_id, version)  # 未知 → Fail-Closed
        try:
            with self._conn:
                self._conn.execute(
                    "UPDATE risk_policy_version SET is_active = 0 WHERE policy_id = ?",
                    (policy_id,),
                )
                self._conn.execute(
                    "UPDATE risk_policy_version SET is_active = 1 "
                    "WHERE policy_id = ? AND version = ?",
                    (policy_id, version),
                )
        except sqlite3.Error as exc:
            raise RiskPolicyError(f"激活版本切换失败: {exc}") from exc
        active = PolicyVersion(
            policy_id=snapshot.policy_id,
            version=snapshot.version,
            limits=snapshot.limits,
            created_at=snapshot.created_at,
            is_active=True,
        )
        self._active[policy_id] = active
        _log.info("风控策略热加载: %s v%d", policy_id, version)
        return active

    # ── 查询 ─────────────────────────────────────────────────────────────

    def active_policy(self, policy_id: str) -> PolicyVersion | None:
        """当前激活版本（无激活 → None）。"""
        return self._active.get(policy_id)

    def get_version(self, policy_id: str, version: int) -> PolicyVersion:
        """指定版本快照（未知 → Fail-Closed）。"""
        return self._load_version(policy_id, version)

    def list_versions(self, policy_id: str) -> tuple[int, ...]:
        """版本清单（升序确定性）。"""
        rows = self._conn.execute(
            "SELECT version FROM risk_policy_version WHERE policy_id = ? "
            "ORDER BY version",
            (policy_id,),
        ).fetchall()
        return tuple(r[0] for r in rows)

    # ── 与 risk_limits 双向同步校验 ───────────────────────────────────────

    def sync_check(
        self, policy_id: str, live_limits: Mapping[str, Decimal]
    ) -> tuple[PolicyDrift, ...]:
        """激活版本 vs risk_limits 运行侧双向比对 → 漂移清单（按 key 排序）。

        双向：持久化侧有而运行侧缺失、运行侧有而持久化侧缺失、同键值不等，
        三类均计漂移。无激活版本 → Fail-Closed。
        """
        active = self._active.get(policy_id)
        if active is None:
            raise RiskPolicyError(f"策略无激活版本，无法同步校验: {policy_id!r}")
        drifts: list[PolicyDrift] = []
        for key in sorted(set(active.limits) | set(live_limits)):
            persisted = active.limits.get(key)
            live = live_limits.get(key)
            if persisted != live:
                drifts.append(
                    PolicyDrift(limit_key=key, persisted=persisted, live=live)
                )
        return tuple(drifts)
