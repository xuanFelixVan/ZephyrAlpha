# [BLUEPRINT] MOD-INF-086 | docs/03_modules/_domain_infrastructure_operations/storage_cost_calculator/blueprint.md
# [MODULE] zephyr.infra_ops.storage_cost_calculator
# [DOMAIN] D_INFRA_OPS
# [DEPENDENCIES] 无（纯内存核算；usage_probe 层占用采集器/单价表/时钟全注入）
# [CONSUMERS] 运行时装配批（热温冷三层占用采集绑定 / 折旧单价表装配 / 成本报表消费）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 层词表闭合(hot|warm|cold); 单价非负且三层齐备; 占用字节非负; TB=1024**4 字节确定性换算; 报表键确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure_operations/storage_cost_calculator/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] StorageCostError(占位 ZA-INF-UNREGISTERED-STORAGE-COST)——单价表缺层/负单价/采集器缺失/占用负值/未知层时抛
# [TESTS] tests/infra_ops/test_storage_cost_calculator.py
# [A_module] module_id=MOD-INF-086 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
StorageCostCalculator — 存储成本量化核算器（MOD-INF-086）。

B13-04333（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-INFRAOPS-004，A3数据
架构）：按热（HOT）/温（WARM）/冷（COLD）三层统计占用字节，乘 TB 单价
（本地盘折旧折算参数注入，可经 derive_tb_price 由盘价/容量/摊销月数折
算）得各层月成本与总成本对比报表（纯字典结构）；并量化归档策略收益
（归档前后月成本差与节省比例）。层占用采集经注入 usage_probe 回调。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: disk_cost 参数
#   fields: 参数 disk_cost（无注解）
#   code: storage_cost_calculator.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: disk_tb 参数
#   fields: 参数 disk_tb（无注解）
#   code: storage_cost_calculator.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: amortize_months 参数
#   fields: 参数 amortize_months（无注解）
#   code: storage_cost_calculator.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① derive_tb_price
#   name_en: derive_tb_price
#   intro: 本地盘折旧折算 TB 月单价：disk_cost / disk_tb / amortize_months。
#   desc: 本地盘折旧折算 TB 月单价：disk_cost / disk_tb / amortize_months。；源码 L107-L115
#   inputs: disk_cost disk_tb amortize_months
#   outputs: float
# - id: A2
#   name_zh: ② StorageCostCalculator
#   name_en: StorageCostCalculator
#   intro: 三层存储成本核算件（占用采集 + 月成本报表 + 归档收益量化）。
#   desc: 三层存储成本核算件（占用采集 + 月成本报表 + 归档收益量化）。；公共方法（定义序）: collect_usage, cost_calculator, archive_benefit；源码 L118-L208
#   inputs: usage_probe price_per_tb_month
#   outputs: 返回值
#   （注：A2 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: float
#   name_en: float
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 运行时装配批（热温冷三层占用采集绑定 / 折旧单价表装配 / 成本报表消费）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "StorageCostCalculator",
    "StorageCostError",
    "StorageLayer",
    "TB_BYTES",
    "derive_tb_price",
]

#: 1 TiB 字节数（确定性换算基准）
TB_BYTES: Final[int] = 1024**4


class StorageCostError(Exception):
    """存储成本核算输入非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-INF-UNREGISTERED-STORAGE-COST。
    """


class StorageLayer(str, Enum):
    """存储分层（词表闭合）。"""

    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


def derive_tb_price(*, disk_cost: float, disk_tb: float, amortize_months: int) -> float:
    """本地盘折旧折算 TB 月单价：disk_cost / disk_tb / amortize_months。"""
    if disk_cost < 0:
        raise StorageCostError(f"disk_cost 不可为负: {disk_cost}")
    if disk_tb <= 0:
        raise StorageCostError(f"disk_tb 须为正: {disk_tb}")
    if amortize_months <= 0:
        raise StorageCostError(f"amortize_months 须为正: {amortize_months}")
    return disk_cost / disk_tb / amortize_months


class StorageCostCalculator:
    """三层存储成本核算件（占用采集 + 月成本报表 + 归档收益量化）。"""

    def __init__(
        self,
        *,
        usage_probe: Callable[[], Mapping[StorageLayer, int]] | None = None,
        price_per_tb_month: Mapping[StorageLayer, float],
    ) -> None:
        if not price_per_tb_month:
            raise StorageCostError("price_per_tb_month 为空（三层单价表须齐备）")
        for layer in StorageLayer:
            if layer not in price_per_tb_month:
                raise StorageCostError(f"单价表缺层: {layer.value!r}")
            if price_per_tb_month[layer] < 0:
                raise StorageCostError(f"单价不可为负: {layer.value}={price_per_tb_month[layer]}")
        self._price: dict[StorageLayer, float] = dict(price_per_tb_month)
        self._probe = usage_probe

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _validate_usage(self, usage: Mapping[StorageLayer, int]) -> None:
        for layer, nbytes in usage.items():
            if not isinstance(layer, StorageLayer):
                raise StorageCostError(f"未知存储层: {layer!r}")
            if nbytes < 0:
                raise StorageCostError(f"占用字节不可为负: {layer.value}={nbytes}")

    def _monthly_cost(self, layer: StorageLayer, nbytes: int) -> float:
        return nbytes / TB_BYTES * self._price[layer]

    def _total_cost(self, usage: Mapping[StorageLayer, int]) -> float:
        return sum(self._monthly_cost(layer, nbytes) for layer, nbytes in usage.items())

    # ── 采集与报表 ────────────────────────────────────────────────────────

    def collect_usage(self) -> dict[StorageLayer, int]:
        """采集各层占用字节（probe 未注入/负值/未知层 → Fail-Closed）。"""
        if self._probe is None:
            raise StorageCostError("usage_probe 未注入（禁止直采文件系统）")
        usage = dict(self._probe())
        self._validate_usage(usage)
        return usage

    def cost_calculator(self) -> dict:
        """成本对比报表：各层占用 TB/月成本 + 总成本（确定性键序）。"""
        usage = self.collect_usage()
        layers: dict[str, dict] = {}
        total_bytes = 0
        total_cost = 0.0
        for layer in StorageLayer:  # 枚举序即确定性键序
            nbytes = usage.get(layer, 0)
            cost = self._monthly_cost(layer, nbytes)
            layers[layer.value] = {
                "bytes": nbytes,
                "tb": nbytes / TB_BYTES,
                "unit_price_per_tb_month": self._price[layer],
                "monthly_cost": cost,
            }
            total_bytes += nbytes
            total_cost += cost
        return {
            "layers": layers,
            "total": {
                "bytes": total_bytes,
                "tb": total_bytes / TB_BYTES,
                "monthly_cost": total_cost,
            },
        }

    # ── 归档收益量化 ──────────────────────────────────────────────────────

    def archive_benefit(
        self,
        before: Mapping[StorageLayer, int],
        after: Mapping[StorageLayer, int],
    ) -> dict:
        """归档策略收益：归档前/后月成本差 + 节省比例（before 为 0 时比例为 0）。"""
        self._validate_usage(before)
        self._validate_usage(after)
        before_cost = self._total_cost(before)
        after_cost = self._total_cost(after)
        saving = before_cost - after_cost
        ratio = saving / before_cost if before_cost > 0 else 0.0
        _log.info("归档收益量化: before=%.4f after=%.4f saving=%.4f", before_cost, after_cost, saving)
        return {
            "before_monthly_cost": before_cost,
            "after_monthly_cost": after_cost,
            "saving_monthly_cost": saving,
            "saving_ratio": ratio,
        }
