# [BLUEPRINT] MOD-GOV-052 | docs/03_modules/_domain_governance/gov_policy_manager/blueprint.md
# [MODULE] zephyr.governance.gov_policy_manager
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] 无（策略核心纯内存；sqlite 连接/时钟全注入，未注入连接则仅内存运行）
# [CONSUMERS] 运行时装配批（GOV-* 策略装配：sqlite 连接 + 时钟统一注入）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 状态词表闭合(draft|active|suspended|retired); 合法迁移 draft→active→suspended→retired(含 suspended→active 恢复与各态→retired 终态); 版本严格递增且历史全量留存; 更新/迁移仅作用于最新版本; 删除仅允许 draft; 持久化写入失败 Fail-Closed 不回滚内存态先写库后写内存; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_governance/gov_policy_manager/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] GovPolicyError(占位 ZA-GOV-UNREGISTERED-GOV-POLICY)——空/非GOV-前缀policy_id/空content/重复创建/未知策略/未知版本/非法状态迁移/retired后更新/非draft删除/sqlite写入失败时抛
# [TESTS] tests/governance/test_gov_policy_manager.py
# [A_module] module_id=MOD-GOV-052 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""



GovPolicyManager — 治理策略管理器（MOD-GOV-052）。

B9-10877（AUD-DRAFT-001-DIGEST P2 波 P2-W12，CAND-WORKTREE-003，B9
D-GOVERNANCE-01）：GOV-* 策略 CRUD + 版本管理（版本递增 + 历史留存）
+ 持久化存储（注入 sqlite 连接）+ 策略状态机
（draft→active→suspended→retired）。OPA 策略生命周期单机版。

查重分工（蓝图 §0）：policy_sandbox=策略沙箱执行（本件=策略生命周期
存储与状态机，不执行策略）；escalation/budget_enforcer=策略消费方
（本件只产出策略记录，不挂运行时判定）；audit_trail=审计落证（本件
sqlite 注入仅作策略持久化镜像，零交集）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: gov_policy_manager.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: sqlite_conn 参数
#   fields: 参数 sqlite_conn（无注解）
#   code: gov_policy_manager.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① GovPolicyManager
#   name_en: GovPolicyManager
#   intro: GOV-* 策略生命周期管理器（CRUD + 版本递增 + sqlite 镜像持久化）。
#   desc: GOV-* 策略生命周期管理器（CRUD + 版本递增 + sqlite 镜像持久化）。；公共方法（定义序）: create_policy, get_policy, update_policy, delete_poli…
#   inputs: clock sqlite_conn
#   outputs: 返回值
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: GovPolicyManager
#   downstream: 运行时装配批（GOV-* 策略装配：sqlite 连接 + 时钟统一注入）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
import sqlite3
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "GovPolicyError",
    "GovPolicyManager",
    "PolicyRecord",
    "PolicyState",
]

#: policy_id 强制前缀（GOV-* 策略词表）
_POLICY_PREFIX: Final = "GOV-"

#: 状态机合法迁移表（词表闭合；retired 为终态）
_TRANSITIONS: Final[dict[PolicyState, frozenset[PolicyState]]] = {}


class GovPolicyError(Exception):
    """策略管理输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-GOV-UNREGISTERED-GOV-POLICY。
    """


class PolicyState(str, Enum):
    """策略状态机（词表闭合）。"""

    DRAFT = "draft"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    RETIRED = "retired"


_TRANSITIONS.update(
    {
        PolicyState.DRAFT: frozenset({PolicyState.ACTIVE, PolicyState.RETIRED}),
        PolicyState.ACTIVE: frozenset({PolicyState.SUSPENDED, PolicyState.RETIRED}),
        PolicyState.SUSPENDED: frozenset({PolicyState.ACTIVE, PolicyState.RETIRED}),
        PolicyState.RETIRED: frozenset(),
    }
)


@dataclass(frozen=True)
class PolicyRecord:
    """单版本策略记录（frozen；历史留存的最小单元）。"""

    policy_id: str
    version: int
    content: str
    state: PolicyState
    updated_at: datetime.datetime


class GovPolicyManager:
    """GOV-* 策略生命周期管理器（CRUD + 版本递增 + sqlite 镜像持久化）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        sqlite_conn: sqlite3.Connection | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._conn = sqlite_conn
        #: policy_id -> 版本递增的记录列表（历史全量留存）
        self._policies: dict[str, list[PolicyRecord]] = {}
        if self._conn is not None:
            try:
                self._conn.execute(
                    "CREATE TABLE IF NOT EXISTS gov_policies ("
                    "policy_id TEXT NOT NULL, "
                    "version INTEGER NOT NULL, "
                    "content TEXT NOT NULL, "
                    "state TEXT NOT NULL, "
                    "updated_at TEXT NOT NULL, "
                    "PRIMARY KEY (policy_id, version))"
                )
                self._conn.commit()
            except sqlite3.Error as exc:
                raise GovPolicyError(f"sqlite 建表失败: {exc}") from exc

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _validate_policy_id(policy_id: str) -> None:
        if not policy_id:
            raise GovPolicyError("policy_id 为空")
        if not policy_id.startswith(_POLICY_PREFIX):
            raise GovPolicyError(f"policy_id 须以 {_POLICY_PREFIX!r} 前缀: {policy_id!r}")

    @staticmethod
    def _validate_content(content: str) -> None:
        if not content:
            raise GovPolicyError("content 为空（策略内容禁止空白）")

    def _latest(self, policy_id: str) -> PolicyRecord:
        versions = self._policies.get(policy_id)
        if not versions:
            raise GovPolicyError(f"未知策略: {policy_id!r}")
        return versions[-1]

    def _persist(self, record: PolicyRecord) -> None:
        """sqlite 镜像写入（未注入连接则跳过；写库失败 Fail-Closed）。"""
        if self._conn is None:
            return
        try:
            self._conn.execute(
                "INSERT INTO gov_policies (policy_id, version, content, state, updated_at) VALUES (?, ?, ?, ?, ?)",
                (
                    record.policy_id,
                    record.version,
                    record.content,
                    record.state.value,
                    record.updated_at.isoformat(),
                ),
            )
            self._conn.commit()
        except sqlite3.Error as exc:
            raise GovPolicyError(f"sqlite 写入失败: {record.policy_id!r} v{record.version}: {exc}") from exc

    def _append(self, record: PolicyRecord) -> PolicyRecord:
        """先写库后写内存（库失败则内存不变，Fail-Closed 不产生半态）。"""
        self._persist(record)
        self._policies.setdefault(record.policy_id, []).append(record)
        _log.info(
            "策略版本登记: %s v%d (%s)",
            record.policy_id,
            record.version,
            record.state.value,
        )
        return record

    # ── CRUD ─────────────────────────────────────────────────────────────

    def create_policy(self, policy_id: str, content: str) -> PolicyRecord:
        """创建策略：v1 / draft；重复创建 Fail-Closed。"""
        self._validate_policy_id(policy_id)
        self._validate_content(content)
        if policy_id in self._policies:
            raise GovPolicyError(f"策略已存在: {policy_id!r}（禁止重复创建）")
        return self._append(
            PolicyRecord(
                policy_id=policy_id,
                version=1,
                content=content,
                state=PolicyState.DRAFT,
                updated_at=self._clock(),
            )
        )

    def get_policy(self, policy_id: str, version: int | None = None) -> PolicyRecord:
        """取策略记录：默认最新版本；指定版本须存在（历史留存可查）。"""
        self._validate_policy_id(policy_id)
        versions = self._policies.get(policy_id)
        if not versions:
            raise GovPolicyError(f"未知策略: {policy_id!r}")
        if version is None:
            return versions[-1]
        for record in versions:
            if record.version == version:
                return record
        raise GovPolicyError(f"未知版本: {policy_id!r} v{version}")

    def update_policy(self, policy_id: str, content: str) -> PolicyRecord:
        """更新策略：版本 +1（历史留存），继承当前状态；retired 拒绝。"""
        self._validate_policy_id(policy_id)
        self._validate_content(content)
        latest = self._latest(policy_id)
        if latest.state is PolicyState.RETIRED:
            raise GovPolicyError(f"非法状态迁移: {policy_id!r} 已 retired（终态禁止更新）")
        return self._append(
            PolicyRecord(
                policy_id=policy_id,
                version=latest.version + 1,
                content=content,
                state=latest.state,
                updated_at=self._clock(),
            )
        )

    def delete_policy(self, policy_id: str) -> None:
        """删除策略：仅 draft 允许硬删除；其余须走 retired 终态。"""
        self._validate_policy_id(policy_id)
        latest = self._latest(policy_id)
        if latest.state is not PolicyState.DRAFT:
            raise GovPolicyError(f"删除拒绝: {policy_id!r} 当前 {latest.state.value}，仅 draft 可删")
        if self._conn is not None:
            try:
                self._conn.execute("DELETE FROM gov_policies WHERE policy_id = ?", (policy_id,))
                self._conn.commit()
            except sqlite3.Error as exc:
                raise GovPolicyError(f"sqlite 删除失败: {policy_id!r}: {exc}") from exc
        del self._policies[policy_id]
        _log.info("策略删除: %s（draft 硬删除）", policy_id)

    # ── 状态机 ────────────────────────────────────────────────────────────

    def transition(self, policy_id: str, target: PolicyState) -> PolicyRecord:
        """状态迁移：作用于最新版本并留存为新版本记录；非法迁移 Fail-Closed。"""
        self._validate_policy_id(policy_id)
        if not isinstance(target, PolicyState):
            raise GovPolicyError(f"非法状态: {target!r}")
        latest = self._latest(policy_id)
        if target not in _TRANSITIONS[latest.state]:
            raise GovPolicyError(
                f"非法状态迁移: {policy_id!r} {latest.state.value} -> "
                f"{target.value}（合法仅 draft→active→suspended→retired 系）"
            )
        return self._append(
            PolicyRecord(
                policy_id=policy_id,
                version=latest.version + 1,
                content=latest.content,
                state=target,
                updated_at=self._clock(),
            )
        )

    # ── 查询 ─────────────────────────────────────────────────────────────

    def history(self, policy_id: str) -> tuple[PolicyRecord, ...]:
        """全版本历史（版本递增序；未知策略 Fail-Closed）。"""
        self._validate_policy_id(policy_id)
        versions = self._policies.get(policy_id)
        if not versions:
            raise GovPolicyError(f"未知策略: {policy_id!r}")
        return tuple(versions)

    def list_policies(self, state: PolicyState | None = None) -> tuple[PolicyRecord, ...]:
        """各策略最新版本视图（按 policy_id 确定性排序；可按状态过滤）。"""
        if state is not None and not isinstance(state, PolicyState):
            raise GovPolicyError(f"非法状态: {state!r}")
        out = [
            versions[-1]
            for _, versions in sorted(self._policies.items())
            if state is None or versions[-1].state is state
        ]
        return tuple(out)
