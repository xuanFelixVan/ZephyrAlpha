# [BLUEPRINT] MOD-FAC-002 | docs/03_modules/_domain_factor/signature_feature_extractor/blueprint.md
# [MODULE] zephyr.factor.signature_feature_extractor
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] 无（纯内存纯 Python 数值核；无任何外部副作用）
# [CONSUMERS] 运行时装配批（路径签名特征批量提取 / 因子库草稿治理串行合并）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 截断阶数护栏 2≤order≤4（越界 Fail-Closed 防组合爆炸）；管线固定：逐分量对数变换→增量→张量积迭代截断（分段线性路径签名 S⊗exp(Δ) 更新）；level-k 维数恰为 dim^k；特征名按 itertools.product 索引字典序确定性生成；输入路径须 ≥2 点、等维、逐分量严格为正且有限；同序列必同向量
# [MODIFY-GUARD] docs/03_modules/_domain_factor/signature_feature_extractor/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] SignatureError(占位 ZA-FAC-UNREGISTERED-SIGNATURE)——阶数越界/路径过短/维度不齐/空维/非正或非有限值（对数无定义）时抛
# [TESTS] tests/factor/test_signature_feature_extractor.py
# [A_module] module_id=MOD-FAC-002 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""


SignatureFeatureExtractor — 签名方法特征提取器（MOD-FAC-002）。

B10-01834（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-FAC-018，A1 §29.8）：路径
**截断 2-4 阶 log-signature** 特征向量——逐分量对数变换 + 增量累积 + 张量
积迭代截断（阶数护栏 ≤4 防组合爆炸）+ 确定性输出（同序列必同向量）。

查重分工（蓝图 §0）：casebook=形态案例库检索（语义图案匹配）；本件=路径签名
**代数不变量**数值特征（ rough path 理论截断签名，无形态库、无检索），二者
零交集。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: order 参数
#   fields: 参数 order（无注解）
#   code: signature_feature_extractor.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① SignatureFeatures
#   name_en: SignatureFeatures
#   intro: 截断 log-signature 特征向量（frozen；names 与 values 等长对齐）。
#   desc: 截断 log-signature 特征向量（frozen；names 与 values 等长对齐）。；公共方法（定义序）: as_dict；源码 L96-L106
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② SignatureFeatureExtractor
#   name_en: SignatureFeatureExtractor
#   intro: 截断 log-signature 提取器（2-4 阶护栏，纯内存确定性）。
#   desc: 截断 log-signature 提取器（2-4 阶护栏，纯内存确定性）。 Args: order: 截断阶数（∈ [2,4]，越界 Fail-Closed）。；公共方法（定义序）: order, feature_na…
#   inputs: order
#   outputs: 返回值
#   （注：A2 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: SignatureFeatures, SignatureFeatureExtractor
#   downstream: 运行时装配批（路径签名特征批量提取 / 因子库草稿治理串行合并）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from itertools import product
from typing import Final, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "MAX_ORDER",
    "MIN_ORDER",
    "SignatureError",
    "SignatureFeatureExtractor",
    "SignatureFeatures",
]

#: 截断阶数护栏（≤4 防组合爆炸：level-k 维数 dim^k）
MIN_ORDER: Final = 2
MAX_ORDER: Final = 4


class SignatureError(Exception):
    """签名特征输入/配置非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-FAC-UNREGISTERED-SIGNATURE。
    """


@dataclass(frozen=True)
class SignatureFeatures:
    """截断 log-signature 特征向量（frozen；names 与 values 等长对齐）。"""

    order: int
    dim: int
    names: tuple[str, ...]
    values: tuple[float, ...]

    def as_dict(self) -> dict[str, float]:
        """特征名 → 取值映射（按键序确定性）。"""
        return dict(zip(self.names, self.values, strict=False))


class SignatureFeatureExtractor:
    """截断 log-signature 提取器（2-4 阶护栏，纯内存确定性）。

    Args:
        order: 截断阶数（∈ [2,4]，越界 Fail-Closed）。
    """

    def __init__(self, *, order: int = 2) -> None:
        if isinstance(order, bool) or not isinstance(order, int):
            raise SignatureError(f"order 非法（须为 int）: {order!r}")
        if not (MIN_ORDER <= order <= MAX_ORDER):
            raise SignatureError(f"order 越界: {order}（护栏 {MIN_ORDER}≤order≤{MAX_ORDER} 防组合爆炸）")
        self._order = order

    @property
    def order(self) -> int:
        return self._order

    # ── 特征名（确定性索引字典序） ─────────────────────────────────────────

    def feature_names(self, dim: int) -> tuple[str, ...]:
        """level 1..order 特征名（level-k 维数 dim^k，product 索引字典序）。"""
        if isinstance(dim, bool) or not isinstance(dim, int) or dim < 1:
            raise SignatureError(f"dim 非法（须 ≥1 的 int）: {dim!r}")
        names: list[str] = []
        for k in range(1, self._order + 1):
            for idx in product(range(dim), repeat=k):
                names.append(f"s{k}_" + "_".join(str(i) for i in idx))
        return tuple(names)

    # ── 提取（对数变换 + 增量 + 张量积迭代截断） ───────────────────────────

    def extract(self, path: Sequence[Sequence[float]]) -> SignatureFeatures:
        """路径 → 截断 log-signature 特征向量（同序列必同向量）。"""
        rows = self._validate(path)
        dim = len(rows[0])
        log_rows = [tuple(math.log(v) for v in row) for row in rows]  # ① 对数变换
        increments = [  # ② 增量
            tuple(log_rows[t + 1][i] - log_rows[t][i] for i in range(dim)) for t in range(len(log_rows) - 1)
        ]
        # ③ 张量积迭代截断：分段线性路径签名 S ← S ⊗ exp(Δ)
        levels: list[list[float]] = [[0.0] * (dim**k) for k in range(1, self._order + 1)]
        for inc in increments:
            for k in range(self._order, 1, -1):  # 高阶先更新（用低阶旧值）
                prev = levels[k - 2]
                cur = levels[k - 1]
                bump = [x * y for x in prev for y in inc]  # prev ⊗ Δ
                for j in range(len(cur)):
                    cur[j] += bump[j]
            level1 = levels[0]
            for i in range(dim):
                level1[i] += inc[i]
        values: list[float] = []
        for level in levels:
            values.extend(level)
        names = self.feature_names(dim)
        _log.debug("log-signature 提取: dim=%d order=%d 特征数=%d", dim, self._order, len(values))
        return SignatureFeatures(order=self._order, dim=dim, names=names, values=tuple(values))

    # ── 输入校验（Fail-Closed） ────────────────────────────────────────────

    @staticmethod
    def _validate(path: Sequence[Sequence[float]]) -> list[tuple[float, ...]]:
        if not isinstance(path, Sequence) or isinstance(path, (str, bytes)):
            raise SignatureError(f"path 非法（须为点序列）: {type(path).__name__}")
        rows: list[tuple[float, ...]] = []
        for row in path:
            if not isinstance(row, Sequence) or isinstance(row, (str, bytes)):
                raise SignatureError(f"路径点非法（须为数值序列）: {row!r}")
            vals: list[float] = []
            for v in row:
                if isinstance(v, bool) or not isinstance(v, (int, float)):
                    raise SignatureError(f"路径分量非法（须为实数）: {v!r}")
                fv = float(v)
                if not math.isfinite(fv):
                    raise SignatureError(f"路径分量非有限: {v!r}")
                if fv <= 0.0:
                    raise SignatureError(f"路径分量非正（对数无定义）: {v!r}")
                vals.append(fv)
            rows.append(tuple(vals))
        if len(rows) < 2:
            raise SignatureError(f"路径过短（须 ≥2 点）: {len(rows)}")
        dim = len(rows[0])
        if dim < 1:
            raise SignatureError("路径维度为空（须 ≥1 维）")
        if any(len(r) != dim for r in rows):
            raise SignatureError("路径维度不齐（各点维数须一致）")
        return rows
