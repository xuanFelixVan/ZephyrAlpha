# [BLUEPRINT] MOD-ML-017 | docs/03_modules/_domain_machine_learning_train/kan_density_head/blueprint.md
# [MODULE] zephyr.ml_train.implementations.kan_density_head
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] numpy（C-003 验证报告/时钟全注入；样条基函数 Cox-de Boor 递推纯 numpy）
# [CONSUMERS] 运行时装配批（QNN Stage1 替换语义统一注入点装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] B样条阶数≤4 护栏; 系数栅格初始化+岭回归闭式求解(确定性); 前向分位数输出单调不交叉(np.maximum.accumulate); 接口对齐 QNN Stage1(predict_quantiles(x)->dict[quantile,(n,)]); 须过 C-003 验证语义(报告未注入/未过 Fail-Closed 禁预测); 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_machine_learning_train/kan_density_head/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] KanHeadError(占位 ZA-MLT-UNREGISTERED-KAN-HEAD)——阶数>4/栅格非法/分位数越界/输入维度不符/未训练预测/验证报告缺失或未过时抛
# [TESTS] tests/ml_train/implementations/test_kan_density_head.py
# [A_module] module_id=MOD-ML-017 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
KanDensityHead — KAN 密度预测头（MOD-ML-017）。

B10-01878（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-MLT-024，A1 §29.33）：
**可学习 B 样条激活**（阶数≤4 护栏，系数栅格初始化 + 岭回归闭式求解）
+ **前向分位数输出**（纯 numpy，样条基函数 **Cox-de Boor 递推**）
+ **替换 QNN Stage1 MLP 语义**（接口对齐：``predict_quantiles(x) ->
dict[quantile, (n,)]``，Stage1 为跨标的共性基座故无 symbol 入参）
+ **须过 C-003 验证语义标注**（验证报告注入，未注入/未过 Fail-Closed
禁预测）。

查重分工（蓝图 §0）：qnn_two_stage=两阶段 HGB 分位数架构（本件=其 Stage1
MLP 的 KAN 替换头，不动 Stage2 仿射缩放）；density_quantile_trainer=单
标的 HGB 密度头（本件=样条激活新模型类，不同族）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: kan_density_head.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: validation_report 参数
#   fields: 参数 validation_report（无注解）
#   code: kan_density_head.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: kan_density_head.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① KanDensityHead
#   name_en: KanDensityHead
#   intro: KAN 密度预测头（可学习 B 样条激活 + 分位数前向，纯 numpy）。
#   desc: KAN 密度预测头（可学习 B 样条激活 + 分位数前向，纯 numpy）。；公共方法（定义序）: fit, predict_quantiles；源码 L109-L250
#   inputs: config validation_report clock
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: KanDensityHead
#   downstream: 运行时装配批（QNN Stage1 替换语义统一注入点装配）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from typing import Any, Callable, Final, Mapping

import numpy as np

_log = logging.getLogger(__name__)

__all__: Final = [
    "KanDensityConfig",
    "KanDensityHead",
    "KanHeadError",
    "MAX_SPLINE_ORDER",
]

#: B 样条阶数护栏（≤4 防组合爆炸）
MAX_SPLINE_ORDER: Final[int] = 4


class KanHeadError(Exception):
    """KAN 密度头输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-MLT-UNREGISTERED-KAN-HEAD。
    """


@dataclass(frozen=True)
class KanDensityConfig:
    """KAN 密度头配置（frozen）。"""

    quantiles: tuple[float, ...] = (0.1, 0.25, 0.5, 0.75, 0.9)
    spline_order: int = 3
    n_grid: int = 5
    ridge: float = 1e-6


class KanDensityHead:
    """KAN 密度预测头（可学习 B 样条激活 + 分位数前向，纯 numpy）。"""

    def __init__(
        self,
        config: KanDensityConfig | None = None,
        *,
        validation_report: Mapping[str, Any] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        self.config = config or KanDensityConfig()
        if not 1 <= self.config.spline_order <= MAX_SPLINE_ORDER:
            raise KanHeadError(f"样条阶数越界: {self.config.spline_order}（须 ∈[1,{MAX_SPLINE_ORDER}] 护栏）")
        if self.config.n_grid < 1:
            raise KanHeadError(f"n_grid 越界: {self.config.n_grid}（须 ≥1）")
        if not self.config.quantiles or any(not 0.0 < q < 1.0 for q in self.config.quantiles):
            raise KanHeadError(f"分位数越界: {self.config.quantiles}（须 ∈(0,1) 非空）")
        if tuple(sorted(self.config.quantiles)) != tuple(self.config.quantiles):
            raise KanHeadError("分位数须升序")
        self._validation_report = validation_report
        self._clock = clock or datetime.datetime.now
        self._knots: list[np.ndarray] = []  # 每特征节点向量
        self._n_basis: list[int] = []  # 每特征基函数数
        self._coef: np.ndarray | None = None  # 共性系数（栅格初始化后闭式求解）
        self._offsets: dict[float, float] = {}  # 逐分位残差偏移
        self._n_features: int = 0

    # ── B 样条基（Cox-de Boor 递推） ─────────────────────────────────────

    @staticmethod
    def _build_knots(x_min: float, x_max: float, n_grid: int, degree: int) -> np.ndarray:
        """夹紧节点向量（端点 degree+1 重）。"""
        internal = np.linspace(x_min, x_max, n_grid + 1)[1:-1]
        return np.concatenate(
            [
                np.full(degree + 1, x_min),
                internal,
                np.full(degree + 1, x_max),
            ]
        )

    @classmethod
    def _basis_matrix(cls, x: np.ndarray, knots: np.ndarray, degree: int, n_basis: int) -> np.ndarray:
        """Cox-de Boor 递推求基函数矩阵 (n_samples, n_basis)。"""
        span = knots[-1] - knots[0]
        if span == 0.0:
            return np.ones((len(x), 1))
        # 右端点归入末非退化区间（夹紧节点退化区间防护，保单位分解）
        x = np.clip(x, knots[0], np.nextafter(knots[-1], knots[0]))
        # 0 阶：区间指示（右端点归入末区间）
        basis = np.zeros((len(x), len(knots) - 1))
        for i in range(len(knots) - 1):
            left, right = knots[i], knots[i + 1]
            if i == len(knots) - 2:
                basis[:, i] = ((x >= left) & (x <= right)).astype(float)
            else:
                basis[:, i] = ((x >= left) & (x < right)).astype(float)
        # Cox-de Boor 递推升阶
        for p in range(1, degree + 1):
            next_basis = np.zeros((len(x), len(knots) - 1 - p))
            for i in range(len(knots) - 1 - p):
                denom_left = knots[i + p] - knots[i]
                denom_right = knots[i + p + 1] - knots[i + 1]
                term_left = (x - knots[i]) / denom_left * basis[:, i] if denom_left > 0 else 0.0
                term_right = (knots[i + p + 1] - x) / denom_right * basis[:, i + 1] if denom_right > 0 else 0.0
                next_basis[:, i] = term_left + term_right
            basis = next_basis
        return basis[:, :n_basis]

    def _design_matrix(self, x: np.ndarray) -> np.ndarray:
        """拼接逐特征样条基 + 截距列。"""
        blocks = [
            self._basis_matrix(x[:, j], self._knots[j], self.config.spline_order, self._n_basis[j])
            for j in range(self._n_features)
        ]
        blocks.append(np.ones((len(x), 1)))
        return np.column_stack(blocks)

    # ── 训练 ──────────────────────────────────────────────────────────────

    def fit(self, x: np.ndarray, y: np.ndarray) -> dict[str, Any]:
        """拟合：系数栅格（零）初始化 → 岭回归闭式求解 + 逐分位残差偏移。"""
        arr = np.asarray(x, dtype=float)
        target = np.asarray(y, dtype=float)
        if arr.ndim != 2:
            raise KanHeadError(f"x 需二维矩阵，实得 ndim={arr.ndim}")
        if len(arr) < 2:
            raise KanHeadError(f"样本不足: n={len(arr)} < 2")
        if len(arr) != len(target):
            raise KanHeadError("x/y 长度不齐")
        self._n_features = arr.shape[1]
        degree = self.config.spline_order
        self._knots = []
        self._n_basis = []
        for j in range(self._n_features):
            col = arr[:, j]
            x_min, x_max = float(np.min(col)), float(np.max(col))
            if x_max - x_min == 0.0:
                self._knots.append(np.array([x_min, x_max]))
                self._n_basis.append(1)
            else:
                self._knots.append(self._build_knots(x_min, x_max, self.config.n_grid, degree))
                self._n_basis.append(self.config.n_grid + degree)

        phi = self._design_matrix(arr)
        # 系数栅格初始化（零向量）→ 岭回归闭式一步求解（确定性）
        coef_init = np.zeros(phi.shape[1])
        reg = phi.T @ phi + self.config.ridge * np.eye(phi.shape[1])
        self._coef = coef_init + np.linalg.solve(reg, phi.T @ target)
        residuals = target - phi @ self._coef
        self._offsets = {q: float(np.quantile(residuals, q)) for q in self.config.quantiles}
        metrics: dict[str, Any] = {
            "n_train": len(arr),
            "n_features": self._n_features,
            "n_basis_total": int(sum(self._n_basis)),
            "spline_order": degree,
            "trained_at": self._clock().isoformat(),
        }
        _log.info("KAN 密度头拟合完成: %s", metrics)
        return metrics

    # ── 前向分位数输出（接口对齐 QNN Stage1） ─────────────────────────────

    def _check_c003(self) -> None:
        """C-003 验证语义：报告未注入/未过 Fail-Closed 禁预测。"""
        if self._validation_report is None:
            raise KanHeadError("C-003 验证报告未注入（须过 C-003 验证语义，禁预测）")
        if not bool(self._validation_report.get("c003_passed", False)):
            raise KanHeadError("C-003 验证未通过（禁预测）")

    def predict_quantiles(self, x: np.ndarray) -> dict[float, np.ndarray]:
        """分位数前向输出（单调不交叉修正；接口对齐 QNN Stage1）。"""
        if self._coef is None:
            raise KanHeadError("模型未拟合（先调 fit()）")
        self._check_c003()
        arr = np.asarray(x, dtype=float)
        if arr.ndim != 2 or arr.shape[1] != self._n_features:
            raise KanHeadError(f"x 维度不符: 期望 (n,{self._n_features})，实得 shape={arr.shape}")
        base = self._design_matrix(arr) @ self._coef
        raw = np.column_stack([base + self._offsets[q] for q in self.config.quantiles])
        monotone = np.maximum.accumulate(raw, axis=1)
        return {q: monotone[:, i] for i, q in enumerate(self.config.quantiles)}
