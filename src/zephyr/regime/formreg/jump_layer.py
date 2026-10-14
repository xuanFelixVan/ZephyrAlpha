# [BLUEPRINT] MOD-REGIME-017 | 待统筹登记（CONDAXIS-CAMPAIGN 两态线 formreg 包；挖矿真源 docs/_working/condaxis/formreg/2_state_machine.md）
# [MODULE] zephyr.regime.formreg.jump_layer
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas; scikit-learn; jumpmodels（Apache-2.0 外部依赖，研究册 §7 已核）
# [CONSUMERS] （隔离打靶：docs/_working/condaxis/formreg/8_prereg_targeting.md 冒烟；裁定#229 反转落地后接 [3] 灰度主轨——冻结面禁接线）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 两态槽位语义固定（slot0=down/slot1=up，锚定重排照裁定#304 先例：fit 后按
#              centers 锚列统计确定性重排，结构性消除 label switching）；态数守卫显式
#              （K≠2/锚列越界/死组件 NaN centers→ValueError，禁静默无锚定——挖矿簿坑 4）；
#              特征标准化 fit 于训练窗（walk-forward 场景由调用方切窗保 PIT）；
#              后验列=槽位语义且行和=1；跳变惩罚 λ 默认=文献常用对数网格中位（待标定呈批项）
# [MODIFY-GUARD] tests/regime/formreg/test_jump_layer.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 特征帧含 NaN/锚列越界/K≠2/死组件→ValueError（fail-closed）；jumpmodels 拟合异常原样上抛
# [TESTS] tests/regime/formreg/test_jump_layer.py
# [TTL] permanent
"""jump_layer — jumpmodels JumpModel 两态封装（持久态+各态后验）。

条件轴总包战役两态线环节[2]概率层施工产出（P2 车道 st-cdx-formreg-20261013）。
定位＝治 HMM 过频切换③病（挖矿簿 2_state_machine.md 台账行 7）：跳变惩罚 λ 显式
控制切换成本，输出持久态标签+各态后验（后验即 [3] 灰度主轨量源——冻结面禁接线）。

锚定重排（裁定#304 先例移植，regime_detector.anchored_component_order 同构）：
    JumpModel 组件编号跨 fit 无锚（本车道实测：penalty 1 与 10 两轮拟合组件序翻转），
    fit 后按 centers 锚列均值确定性重排到固定语义槽位：
        slot0 "down"（单边↓候选）= 锚列 centers 最低的组件
        slot1 "up"  （单边↑候选）= 锚列 centers 最高的组件
    锚列默认第 0 列（特征帧约定第 0 列=收益/动量向特征）；重排只换标签序不改拟合结果。

跳变惩罚 λ（jump_penalty）文档化（禁自拟冻结）：
    文献常用对数网格 = {0.1, 1, 10, 100}（Nystrup 系 jump model 系列论文及
    jumpmodels 官方示例的标准标定网格）；默认值取该网格对数中位 = √(1×10) ≈ 3.16。
    连续特征（cont=True）+ 标准化输入下量纲成立；A 股正式标定（网格搜索+λ* 报告）
    = P2 呈批项，见 docs/_working/condaxis/formreg/8_prereg_targeting.md。

PIT 纪律：标准化 scaler 与模型均 fit 于调用方给定的训练窗（walk-forward 场景
调用方切窗；detect 语义=对任意特征帧用冻结模型打分，不重拟合）。

# [ALGO_FLOW] external: docs/03_modules/_domain_regime/algo_flow/jump_layer.yaml
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

__all__: Final = [
    "TWO_STATE_SLOTS",
    "DEFAULT_JUMP_PENALTY",
    "JUMP_PENALTY_GRID",
    "anchored_two_state_order",
    "JumpLayerResult",
    "TwoStateJumpLayer",
]


# ---------------------------------------------------------------------------
# 结构常数区
# ---------------------------------------------------------------------------
TWO_STATE_SLOTS: tuple[str, str] = ("down", "up")
"""固定语义槽位（slot0=down 低锚列均值/slot1=up 高锚列均值；形态向语义非收益方向预测——裁定#230 边界措辞见挖矿簿 §3.6）。"""

JUMP_PENALTY_GRID: tuple[float, ...] = (0.1, 1.0, 10.0, 100.0)
"""文献常用 λ 标定网格（Nystrup 系+jumpmodels 官方示例；A 股正式标定=呈批项）。"""

DEFAULT_JUMP_PENALTY: float = 3.16
"""默认 λ=网格 {0.1,1,10,100} 的对数中位 √10≈3.16（文档化推导；待 A 股标定呈批）。"""


# ---------------------------------------------------------------------------
# 锚定重排（纯函数；裁定#304 先例同构）
# ---------------------------------------------------------------------------
def anchored_two_state_order(centers: np.ndarray, anchor_col: int = 0) -> list[int] | None:
    """按锚列 centers 均值算两态确定性槽位序（纯函数）。

    Args:
        centers: JumpModel.fit 后的 centers_（形状 (K, F)，标准化空间）。
        anchor_col: 锚定特征列号（默认 0=第 0 特征列）。

    Returns:
        order：order[槽位]=原组件索引（order[0]=down 最低锚列，order[1]=up 最高锚列）；
        不可锚定（K≠2 / 列数不足 / 锚列含 NaN=死组件）返回 None（禁静默无锚定）。
    """
    centers = np.asarray(centers, dtype=float)
    if centers.ndim != 2 or centers.shape[0] != 2:
        return None
    if centers.shape[1] <= anchor_col:
        return None
    anchor = centers[:, anchor_col]
    if not np.all(np.isfinite(anchor)):
        return None  # 死组件（高 λ 下组件未被占用）——显式不可锚定
    low = int(np.argmin(anchor))
    high = int(np.argmax(anchor))
    if low == high:
        return None
    return [low, high]


# ---------------------------------------------------------------------------
# 封装
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class JumpLayerResult:
    """两态 jump 层输出（全按槽位语义对齐）。

    Attributes:
        labels_online: 在线过滤持久态（predict_online，槽位语义标签）。
        labels_segment: 全样本分段标签（predict，槽位语义标签）。
        posterior: 各态后验 DataFrame（列=TWO_STATE_SLOTS，行和=1）。
        centers: 重排后槽位×特征 centers（标准化空间）。
        order: 锚定序 order[槽位]=原组件索引。
        jump_penalty: 本轮使用的 λ。
    """

    labels_online: pd.Series
    labels_segment: pd.Series
    posterior: pd.DataFrame
    centers: pd.DataFrame
    order: list[int]
    jump_penalty: float


class TwoStateJumpLayer:
    """jumpmodels JumpModel 两态封装（fit→锚定重排→槽位语义输出）。

    Args:
        jump_penalty: 跳变惩罚 λ（默认=文献网格对数中位 3.16；待标定）。
        anchor_col: 锚定特征列号（默认 0）。
        random_state: 随机种子（jumpmodels 多初始化；锚定后语义不受种子影响）。
        max_iter: jumpmodels 内层迭代上限。
    """

    def __init__(
        self,
        jump_penalty: float = DEFAULT_JUMP_PENALTY,
        anchor_col: int = 0,
        random_state: int = 0,
        max_iter: int = 1000,
    ) -> None:
        if jump_penalty < 0.0:
            raise ValueError("jump_penalty 必须 >=0（数值禁入消息文本）")
        self.jump_penalty = float(jump_penalty)
        self.anchor_col = int(anchor_col)
        self.random_state = int(random_state)
        self.max_iter = int(max_iter)
        self._scaler: StandardScaler | None = None
        self._model = None
        self._order: list[int] | None = None

    # -- 内部工具 -----------------------------------------------------------

    @staticmethod
    def _check_frame(features: pd.DataFrame) -> None:
        if features is None or features.empty:
            raise ValueError("特征帧为空（fail-closed）")
        if features.isna().to_numpy().any():
            raise ValueError("特征帧含 NaN（fail-closed：先丢热身期/缺数行再入层）")

    def _to_std(self, features: pd.DataFrame) -> np.ndarray:
        assert self._scaler is not None
        arr = self._scaler.transform(features.to_numpy(dtype=float))
        if not np.all(np.isfinite(arr)):
            raise ValueError("标准化后含非有限值（零方差特征列 fail-closed）")
        return arr

    # -- sklearn 风格主入口 --------------------------------------------------

    def fit(self, features: pd.DataFrame) -> TwoStateJumpLayer:
        """拟合两态 jump 模型＋锚定重排（scaler 与模型均只看本帧=训练窗，PIT 由切窗保证）。

        Args:
            features: 特征帧（行=日期升序，列=特征；第 anchor_col 列须为收益/动量向锚列）。

        Returns:
            self。

        Raises:
            ValueError: 空帧/NaN/锚定失败（K≠2、锚列越界、死组件）。
        """
        from jumpmodels.jump import JumpModel  # noqa: PLC0415 — 惰性导入（外部依赖隔离）

        self._check_frame(features)
        if features.shape[1] <= self.anchor_col:
            raise ValueError("锚列越界（数值禁入消息文本）")
        self._scaler = StandardScaler().fit(features.to_numpy(dtype=float))
        x_std = self._to_std(features)
        model = JumpModel(
            n_components=2,
            jump_penalty=self.jump_penalty,
            cont=True,  # 连续特征版（CJM）；离散 grid 版对收益尺度数据不适用（实测死组件）
            random_state=self.random_state,
            max_iter=self.max_iter,
        )
        model.fit(x_std)
        self._model = model
        order = anchored_two_state_order(model.centers_, self.anchor_col)
        if order is None:
            raise ValueError(
                "锚定重排失败（K≠2/锚列越界/死组件 NaN centers）——两态层禁静默无锚定"
                f"（centers={np.round(model.centers_, 4).tolist()}，λ={self.jump_penalty}）"
            )
        self._order = order
        return self

    def transform(self, features: pd.DataFrame) -> JumpLayerResult:
        """冻结模型对特征帧打分（持久态+各态后验，全按槽位语义）。

        Args:
            features: 特征帧（列序须与 fit 相同）。

        Returns:
            JumpLayerResult。

        Raises:
            RuntimeError: 未 fit。
            ValueError: 帧校验失败。
        """
        if self._model is None or self._order is None or self._scaler is None:
            raise RuntimeError("未 fit（先 fit 后 transform）")
        self._check_frame(features)
        x_std = self._to_std(features)
        raw_online = self._model.predict_online(x_std)
        raw_segment = self._model.predict(x_std)
        raw_proba = self._model.predict_proba(x_std)
        slot_of = np.empty(2, dtype=int)
        for slot, comp in enumerate(self._order):
            slot_of[comp] = slot
        labels_online = pd.Series(
            [TWO_STATE_SLOTS[slot_of[int(v)]] for v in raw_online], index=features.index, name="state"
        )
        labels_segment = pd.Series(
            [TWO_STATE_SLOTS[slot_of[int(v)]] for v in raw_segment], index=features.index, name="state"
        )
        proba_std = raw_proba[:, list(self._order)]  # 列重排到槽位语义
        row_sums = proba_std.sum(axis=1)
        if not np.allclose(row_sums, 1.0, atol=1e-6):
            raise ValueError("后验行和≠1（fail-closed；偏差值禁入消息文本）")
        posterior = pd.DataFrame(proba_std, index=features.index, columns=list(TWO_STATE_SLOTS))
        centers = pd.DataFrame(
            self._model.centers_[self._order, :],
            index=list(TWO_STATE_SLOTS),
            columns=list(features.columns),
        )
        return JumpLayerResult(
            labels_online=labels_online,
            labels_segment=labels_segment,
            posterior=posterior,
            centers=centers,
            order=list(self._order),
            jump_penalty=self.jump_penalty,
        )

    def fit_transform(self, features: pd.DataFrame) -> JumpLayerResult:
        """fit + transform 便捷入口（训练窗全史诊断用）。"""
        return self.fit(features).transform(features)
