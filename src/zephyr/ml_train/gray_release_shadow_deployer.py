# [BLUEPRINT] MOD-ML-004 | docs/03_modules/_domain_machine_learning_train/blueprint.md
# [MODULE] zephyr.ml_train.gray_release_shadow_deployer
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] numpy
# [CONSUMERS] MOD-ML-002 ai_operator（影子部署申请留痕）；MOD-ML-009 learning_effect_feedback（影子表现回喂）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 影子只记录不生效（effective 恒 False，B-009 红线）；同模型同时刻只允许一个活跃影子会话；shadow_ratio∈(0,1]
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ShadowDeployError(ZA-MLT-0007)——比例越界/重复部署/未部署记录/未知会话时抛
# [TESTS] tests/ml_train/test_gray_release_shadow_deployer.py
# [A_module] module_id=MOD-ML-004 | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] permanent

"""
D_ML_TRAIN — MOD-ML-004 灰度/影子部署器。

影子部署语义（红线 B-009）：模型预测只**记录**用于观测对比，**永不生效**——
``record_shadow_predictions`` 返回 ``effective=False``，本模块无任何把影子流量
接入真实决策面的接口。灰度比例 ``shadow_ratio`` 仅声明观测覆盖面（留痕用），
不代表真实流量切分。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: gray_release_shadow_deployer.py
# 层: 算法
# - id: A1
#   name_zh: ① GrayReleaseShadowDeployer
#   name_en: GrayReleaseShadowDeployer
#   intro: 灰度/影子部署器（MOD-ML-004）。
#   desc: 灰度/影子部署器（MOD-ML-004）。；公共方法（定义序）: deploy_shadow, retire_shadow, record_shadow_predictions, shadow_report；源码 L8…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: GrayReleaseShadowDeployer
#   downstream: MOD-ML-002 ai_operator（影子部署申请留痕）；MOD-ML-009 learning_effect_feedback（影子表现回喂）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import numpy as np

_log = logging.getLogger(__name__)


class ShadowDeployError(Exception):
    """ZA-MLT-0007: 影子部署操作失败。"""

    error_code = "ZA-MLT-0007"


@dataclass(frozen=True)
class ShadowSession:
    """影子部署会话。"""

    model_id: str
    shadow_ratio: float  # 观测覆盖面声明 ∈(0,1]，非真实流量
    active: bool
    deployed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    retired_at: datetime | None = None


class GrayReleaseShadowDeployer:
    """灰度/影子部署器（MOD-ML-004）。"""

    def __init__(self) -> None:
        self._sessions: dict[str, ShadowSession] = {}
        self._records: dict[str, list[np.ndarray]] = {}

    # ── 部署/退役 ────────────────────────────────────────────────────

    def deploy_shadow(self, model_id: str, shadow_ratio: float) -> ShadowSession:
        """开影子会话（只观测不生效）。"""
        if not 0.0 < shadow_ratio <= 1.0:
            raise ShadowDeployError(f"shadow_ratio 越界: {shadow_ratio}（需 ∈(0,1]）")
        existing = self._sessions.get(model_id)
        if existing is not None and existing.active:
            raise ShadowDeployError(f"模型 {model_id!r} 已在影子部署中（先 retire 再重部署）")
        sess = ShadowSession(model_id=model_id, shadow_ratio=float(shadow_ratio), active=True)
        self._sessions[model_id] = sess
        self._records[model_id] = []
        _log.info("影子部署: %s ratio=%.2f", model_id, shadow_ratio)
        return sess

    def retire_shadow(self, model_id: str) -> ShadowSession:
        """退役影子会话（保留记录供报告/回喂）。"""
        sess = self._active_or_raise(model_id)
        retired = ShadowSession(
            model_id=sess.model_id,
            shadow_ratio=sess.shadow_ratio,
            active=False,
            deployed_at=sess.deployed_at,
            retired_at=datetime.now(timezone.utc),
        )
        self._sessions[model_id] = retired
        _log.info("影子退役: %s", model_id)
        return retired

    # ── 影子记录（只记录不生效） ─────────────────────────────────────

    def record_shadow_predictions(self, model_id: str, predictions: Any) -> dict[str, Any]:
        """记录一批影子预测。返回 recorded/effective（恒 False）。"""
        self._active_or_raise(model_id)
        arr = np.asarray(predictions, dtype=float)
        self._records[model_id].append(arr)
        return {"recorded": int(arr.size), "effective": False}

    def shadow_report(self, model_id: str) -> dict[str, Any]:
        """影子观测聚合报告（record 数/批次/均值/标准差）。"""
        if model_id not in self._sessions:
            raise ShadowDeployError(f"模型 {model_id!r} 未影子部署（无会话）")
        batches = self._records.get(model_id, [])
        flat = np.concatenate(batches) if batches else np.zeros(0)
        return {
            "model_id": model_id,
            "total_records": int(flat.size),
            "batches": len(batches),
            "mean": float(np.mean(flat)) if flat.size else 0.0,
            "std": float(np.std(flat)) if flat.size else 0.0,
        }

    # ── 内部 ─────────────────────────────────────────────────────────

    def _active_or_raise(self, model_id: str) -> ShadowSession:
        sess = self._sessions.get(model_id)
        if sess is None or not sess.active:
            raise ShadowDeployError(f"模型 {model_id!r} 未影子部署（无活跃会话）")
        return sess


__all__ = [
    "GrayReleaseShadowDeployer",
    "ShadowDeployError",
    "ShadowSession",
]
