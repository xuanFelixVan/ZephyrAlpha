# [BLUEPRINT] MOD-L02-018 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-08
# [MODULE] zephyr.factor.governance.factor_pool_manager
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.governance
# [CONSUMERS] zephyr.factor.governance.engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 活跃池不超active_capacity; 核心因子不参与末位淘汰; 全池不超n_max
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] IC不足->拒绝入池; 活跃池满且IC更低->拒绝替换; 全池满->触发批量裁剪
# [TESTS] tests/factor/test_factor_pool_manager.py
# [A_module] module_id=MOD-L02-018 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D-FACTOR-08 因子池容量管理——活跃池/休眠池 + IC末位淘汰 + 批量裁剪。

管理因子池的容量控制，防止因子膨胀失控。
核心规则（ADR-FAC-006）：
  - N_max ≈ 64（运行上限），活跃池 ≤ N_max-4 ≈ 60，休眠池 ≤ 4
  - 核心因子（is_core=True）不参与末位淘汰
  - IC-Based Replacement: 活跃池满时，新因子与池内IC最低者对比
  - Batch Pruning: 全池≥N_max时，按IC从休眠池裁撤

参数从 governance/_config.yaml 读取，不硬编码。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 新因子入池申请 tuple
#   fields: factor_id + ic_mean + is_core（add_factor/ic_based_replace 参数）
#   code: factor_pool_manager.py L112-113
# - id: I2
#   name: 因子池容量配置 dict
#   fields: factor_pool.n_max=64 / active_capacity=60 / dormant_capacity=4 / min_ic_to_enter=0.02
#   code: governance/_config.yaml L25-29
# 层: 算法
# - id: A1
#   name_zh: ① 入池门槛与容量检查
#   name_en: FactorPoolManager.add_factor
#   intro: 新因子先查重再验IC，活跃池未满直接进，全池满先触发批量裁剪
#   desc: 已在池→拒；|ic|<min_ic→拒；total≥n_max→batch_prune；active<cap→进活跃池；否则走IC替换（L125-144）
#   inputs: I1 I2
#   outputs: (success: bool, message: str)
#   invariant: 活跃池≤active_capacity；全池≤n_max
# - id: A2
#   name_zh: ② IC末位淘汰替换
#   name_en: FactorPoolManager._ic_based_replace
#   intro: 活跃池满时新因子跟池内IC最低的非核心因子比，更高才换得下
#   desc: 找活跃池|IC|最低非核心victim → |new_ic|≤|victim_ic|拒换 → victim降休眠池+新因子进活跃池（L207-229）
#   inputs: I1 A1
#   outputs: (success, message) 替换结果
#   invariant: 核心因子 is_core=True 不参与末位淘汰
# - id: A3
#   name_zh: ③ 批量裁剪
#   name_en: FactorPoolManager.batch_prune
#   intro: 全池到顶64个时，按IC从休眠池往死里裁，腾地方给新因子
#   desc: while total≥n_max：优先裁休眠池|IC|最低者；休眠空则把活跃池最低非核心降级休眠再裁（L167-180, L231-243）
#   inputs: I2 A1
#   outputs: 被裁撤 factor_id 列表
# - id: A4
#   name_zh: ④ 池状态摘要
#   name_en: FactorPoolManager.get_pool_status
#   intro: 数一数活跃池/休眠池各多少个，汇报容量水位
#   desc: 统计 active/dormant/total → FactorPoolStatus（含 is_full=total≥n_max）（L192-205）
#   inputs: I2
#   outputs: FactorPoolStatus
# 层: 输出
# - id: O1
#   name_zh: 入池/替换/裁剪操作结果 (bool, str)
#   name_en: pool operation result
#   intro: 成功失败加一句人话消息，说明进了哪个池或拒因
#   downstream: 治理引擎 engine MOD-L02-017
# - id: O2
#   name_zh: 因子池状态 FactorPoolStatus
#   name_en: pool status
#   intro: 活跃/休眠/全池计数与容量水位摘要
#   downstream: 治理引擎 engine MOD-L02-017
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I1 --> A2
# A1 --> A2
# I2 --> A3
# A1 --> A3
# I2 --> A4
# A2 --> O1
# A3 --> O1
# A4 --> O2
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from zephyr.factor.governance import load_governance_config

ACTIVE = "active"
DORMANT = "dormant"


def _now_utc() -> datetime:
    """返回当前 UTC 时间。"""
    return datetime.now(timezone.utc)


def _get_pool_config() -> tuple[int, int, int, float]:
    """从配置读取因子池参数 (n_max, active_capacity, dormant_capacity, min_ic)。"""
    cfg = load_governance_config()
    pool = cfg.get("factor_pool", {})
    return (
        int(pool.get("n_max", 64)),
        int(pool.get("active_capacity", 60)),
        int(pool.get("dormant_capacity", 4)),
        float(pool.get("min_ic_to_enter", 0.02)),
    )


@dataclass
class FactorPoolEntry:
    """因子池条目。

    Attributes:
        factor_id: 因子ID
        ic_mean: IC均值（用于末位淘汰排序）
        is_core: 是否核心因子（核心因子不参与末位淘汰）
        entered_at: 入池时间
        pool: 所在池 ("active" / "dormant")
    """

    factor_id: str
    ic_mean: float
    is_core: bool = False
    entered_at: datetime = field(default_factory=_now_utc)
    pool: str = ACTIVE


@dataclass
class FactorPoolStatus:
    """因子池状态摘要。"""

    active_count: int
    dormant_count: int
    total_count: int
    active_capacity: int
    dormant_capacity: int
    n_max: int
    is_full: bool


class FactorPoolManager:
    """因子池容量管理器。

    管理活跃池和休眠池的容量控制，提供IC末位淘汰和批量裁剪机制。
    """

    def __init__(self) -> None:
        self._n_max, self._active_cap, self._dormant_cap, self._min_ic = _get_pool_config()
        self._entries: dict[str, FactorPoolEntry] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def entries(self) -> dict[str, FactorPoolEntry]:
        """只读：entries（Stage 4 公共化）。"""
        return self._entries

    @entries.setter
    def entries(self, value):
        """写入：entries（Stage 4 公共化）。"""
        self._entries = value

    def add_factor(self, factor_id: str, ic_mean: float, is_core: bool = False) -> tuple[bool, str]:
        """添加因子到池中。

        - IC低于 min_ic_to_enter → 拒绝入池
        - 活跃池未满 → 直接加入活跃池
        - 活跃池已满 → 触发 IC-Based Replacement
        - 全池已满 → 先触发 Batch Pruning 再尝试加入

        Returns:
            (success, message)
        """
        if factor_id in self._entries:
            return False, f"因子 {factor_id} 已在池中"
        if abs(ic_mean) < self._min_ic:
            return False, f"IC均值 {ic_mean:.4f} < 最低门槛 {self._min_ic}"
        if self._total_count() >= self._n_max:
            pruned = self.batch_prune()
            if self._total_count() >= self._n_max:
                return False, "全池已满，批量裁剪后仍无空间"
            if pruned:
                _msg_prefix = f"批量裁剪 {len(pruned)} 个因子后；"
            else:
                _msg_prefix = ""
        else:
            _msg_prefix = ""
        if self._active_count() < self._active_cap:
            self._entries[factor_id] = FactorPoolEntry(factor_id, ic_mean, is_core, pool=ACTIVE)
            return True, f"{_msg_prefix}因子 {factor_id} 加入活跃池"
        return self._ic_based_replace(factor_id, ic_mean, is_core, _msg_prefix)

    def remove_factor(self, factor_id: str) -> bool:
        """从池中移除因子。"""
        if factor_id not in self._entries:
            return False
        del self._entries[factor_id]
        return True

    def ic_based_replace(self, new_factor_id: str, new_ic: float, is_core: bool = False) -> tuple[bool, str]:
        """IC末位淘汰：新因子与活跃池中IC最低的非核心因子对比。

        活跃池未满时直接加入。已满时新因子IC须高于池内最低IC才替换。
        """
        if self._active_count() < self._active_cap:
            self._entries[new_factor_id] = FactorPoolEntry(new_factor_id, new_ic, is_core, pool=ACTIVE)
            return True, f"活跃池未满，因子 {new_factor_id} 直接加入"
        return self._ic_based_replace(new_factor_id, new_ic, is_core, "")

    def batch_prune(self) -> list[str]:
        """批量裁剪：全池≥N_max时，按IC从休眠池裁撤。

        如果休眠池空，则从活跃池中IC最低的非核心因子移到休眠池再裁撤。
        Returns: 被裁撤的 factor_id 列表。
        """
        pruned: list[str] = []
        while self._total_count() >= self._n_max:
            target = self._find_prune_target()
            if target is None:
                break
            del self._entries[target]
            pruned.append(target)
        return pruned

    def get_active_pool(self) -> list[FactorPoolEntry]:
        """返回活跃池条目列表（按IC降序）。"""
        active = [e for e in self._entries.values() if e.pool == ACTIVE]
        return sorted(active, key=lambda e: abs(e.ic_mean), reverse=True)

    def get_dormant_pool(self) -> list[FactorPoolEntry]:
        """返回休眠池条目列表（按IC降序）。"""
        dormant = [e for e in self._entries.values() if e.pool == DORMANT]
        return sorted(dormant, key=lambda e: abs(e.ic_mean), reverse=True)

    def get_pool_status(self) -> FactorPoolStatus:
        """返回因子池状态摘要。"""
        active_n = self._active_count()
        dormant_n = self._dormant_count()
        total = active_n + dormant_n
        return FactorPoolStatus(
            active_count=active_n,
            dormant_count=dormant_n,
            total_count=total,
            active_capacity=self._active_cap,
            dormant_capacity=self._dormant_cap,
            n_max=self._n_max,
            is_full=total >= self._n_max,
        )

    def _ic_based_replace(self, new_id: str, new_ic: float, is_core: bool, msg_prefix: str) -> tuple[bool, str]:
        """活跃池满时，新因子与池内IC最低的非核心因子对比。"""
        victim = self._find_lowest_ic_active_non_core()
        if victim is None:
            return False, f"{msg_prefix}活跃池全为核心因子，无法替换"
        victim_ic = self._entries[victim].ic_mean
        if abs(new_ic) <= abs(victim_ic):
            return False, f"{msg_prefix}新因子IC {new_ic:.4f} 不高于池内最低IC {victim_ic:.4f}"
        self._demote_to_dormant(victim)
        self._entries[new_id] = FactorPoolEntry(new_id, new_ic, is_core, pool=ACTIVE)
        return True, f"{msg_prefix}因子 {new_id} 替换 {victim}（IC {new_ic:.4f} > {victim_ic:.4f}）"

    def _find_lowest_ic_active_non_core(self) -> str | None:
        """找活跃池中IC绝对值最低的非核心因子。"""
        candidates = [fid for fid, e in self._entries.items() if e.pool == ACTIVE and not e.is_core]
        if not candidates:
            return None
        return min(candidates, key=lambda fid: abs(self._entries[fid].ic_mean))

    def _find_prune_target(self) -> str | None:
        """找裁剪目标：优先休眠池中IC最低者。"""
        dormant = [fid for fid, e in self._entries.items() if e.pool == DORMANT]
        if dormant:
            return min(dormant, key=lambda fid: abs(self._entries[fid].ic_mean))
        # 休眠池空 → 从活跃池降级IC最低非核心因子到休眠池，再裁撤
        victim = self._find_lowest_ic_active_non_core()
        if victim is None:
            return None
        self._demote_to_dormant(victim)
        return victim

    def _demote_to_dormant(self, factor_id: str) -> None:
        """将因子从活跃池移到休眠池。"""
        if factor_id in self._entries:
            self._entries[factor_id].pool = DORMANT

    def _active_count(self) -> int:
        return sum(1 for e in self._entries.values() if e.pool == ACTIVE)

    def _dormant_count(self) -> int:
        return sum(1 for e in self._entries.values() if e.pool == DORMANT)

    def _total_count(self) -> int:
        return len(self._entries)
