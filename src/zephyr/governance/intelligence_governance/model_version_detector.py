# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.intelligence_governance.model_version_detector
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 模型版本突变必须检测;KL divergence阈值不可手动覆盖
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Model Version Detector — v0.10.0 模型版本突变检测: model version change->degraded auto_guard。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: model_version_detector.py
# 层: 算法
# - id: A1
#   name_zh: ① ModelVersionDetector
#   name_en: ModelVersionDetector
#   intro: class ModelVersionDetector 源码 L51-L74
#   desc: 公共方法（定义序）: known_versions, record_version, detect_change, should_degrade；源码 L51-L74
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: ModelVersionDetector
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations


class ModelVersionDetector:
    def __init__(self):
        self._known_versions: dict[str, str] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def known_versions(self) -> dict[str, str]:
        """只读：known_versions（Stage 4 公共化）。"""
        return self._known_versions

    @known_versions.setter
    def known_versions(self, value):
        """写入：known_versions（Stage 4 公共化）。"""
        self._known_versions = value

    def record_version(self, model_id: str, version: str):
        self._known_versions[model_id] = version

    def detect_change(self, model_id: str, current_version: str) -> bool:
        known = self._known_versions.get(model_id)
        return known is not None and known != current_version

    def should_degrade(self, model_id: str, current_version: str) -> bool:
        return self.detect_change(model_id, current_version)
