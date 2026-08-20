# [BLUEPRINT] MOD-CMP-005 | docs/03_modules/_domain_compliance/hard_boundary_adjudicator/blueprint.md
# [MODULE] zephyr.compliance.hard_boundary_adjudicator
# [DOMAIN] D_COMPLIANCE
# [DEPENDENCIES] stdlib + pyyaml + zephyr.compliance.compliance_log
# [CONSUMERS] apply_depgraph.py 设计态登记环节（新功能上线门禁校验，43 号 §6.3/§6.4）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 未登记=PENDING 视同 BLOCK（裁定未决暂缓上线）; FORBIDDEN=BLOCK 并提示重评条件; 登记表不可读=Fail-Closed 一切 BLOCK; 与 30 号 charter 红线消歧（本篇管功能建设权，不管运行时阈值）
# [MODIFY-GUARD] 43_compliance_discipline.md §6（BM-BUY-12）
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FeatureGateError(ZA-CMP-0004)
# [TESTS] tests/compliance/test_hard_boundary_adjudicator.py
# [TTL] permanent

"""硬边界功能裁定 + 上线门禁（43_compliance_discipline §6，BM-BUY-12）。

功能二元裁定（能建/禁建）清单 + 新功能上线门禁流程。
消歧（§6.1）：30 号 §5"10 条真红线"是 charter 系统生存红线（运行时 Fail-Closed
阈值）；本篇是功能建设权裁定（某功能能不能建/能不能上线，设计/上线时门禁），
两者对象不同、时机不同、强制层不同，互不替代。

裁定原则（§6.3，登记时逐条过）：
  ① 法律法规明令禁止 → FORBIDDEN 无例外
  ② 通道/资金属性不支持（T+1、不能做空、无两融）→ FORBIDDEN，重评=通道变更
  ③ 个人系统复杂度不承受 → FORBIDDEN 或降级，重评=团队/AUM 变化

门禁流程（§6.3）：提案 → 裁定 → 登记 → 门禁校验。FeatureGate.check 挂
apply_depgraph 登记设计态模块环节（§6.4，不新增独立审批流程）。

Version: 1.0.0
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

from zephyr.compliance.compliance_log import ComplianceLogger
from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.shared.io.paths import REPO_ROOT

DEFAULT_REGISTRY_PATH: Path = (
    REPO_ROOT  # git 版本化配置锚定当前检出（区别于治理观测库锚主仓）
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "catalogs"
    / "feature_adjudication_registry.yaml"
)


class FeatureGateError(ZephyrBaseError):
    """功能门禁错误。"""

    error_code = "ZA-CMP-0004"


class FeatureVerdict(enum.Enum):
    """裁定结论。"""

    BUILDABLE = "BUILDABLE"
    FORBIDDEN = "FORBIDDEN"


class FeatureGateDecision(enum.Enum):
    """门禁结论。"""

    PASS = "PASS"
    BLOCK = "BLOCK"


@dataclass(frozen=True)
class FeatureEntry:
    """一条功能裁定（§6.3 清单结构）。"""

    feature: str
    verdict: FeatureVerdict
    reason: str
    adjudicated_at: date | None
    re_review_condition: str
    related_bm: str | None = None


@dataclass(frozen=True)
class FeatureGateResult:
    """门禁校验结果（不可变）。"""

    feature: str
    decision: FeatureGateDecision
    entry: FeatureEntry | None
    detail: str


class FeatureGate:
    """新功能上线门禁。

    - 未登记 → PENDING 视同 BLOCK（裁定未决 → 暂缓上线，安全优先，§6.3）
    - FORBIDDEN → BLOCK 并提示重评条件
    - 登记表不可读 → Fail-Closed，一切新功能 BLOCK（§6.3 降级）
    """

    def __init__(
        self,
        registry_path: Path | None = None,
        logger: ComplianceLogger | None = None,
    ) -> None:
        self._registry_path = registry_path or DEFAULT_REGISTRY_PATH
        self._logger = logger or ComplianceLogger()

    def check(self, feature_name: str) -> FeatureGateResult:
        """校验功能是否可上线/可登记。"""
        try:
            entries = self._load()
        except FeatureGateError as exc:
            result = FeatureGateResult(
                feature=feature_name,
                decision=FeatureGateDecision.BLOCK,
                entry=None,
                detail=f"登记表不可读，Fail-Closed 阻断: {exc}",
            )
            self._log(result)
            return result
        entry = entries.get(feature_name)
        if entry is None:
            result = FeatureGateResult(
                feature=feature_name,
                decision=FeatureGateDecision.BLOCK,
                entry=None,
                detail="未登记（PENDING 视同 BLOCK）：裁定未决 → 暂缓上线，先走提案→裁定→登记流程",
            )
        elif entry.verdict is FeatureVerdict.FORBIDDEN:
            result = FeatureGateResult(
                feature=feature_name,
                decision=FeatureGateDecision.BLOCK,
                entry=entry,
                detail=f"禁建：{entry.reason}｜重评条件：{entry.re_review_condition}",
            )
        else:
            result = FeatureGateResult(
                feature=feature_name,
                decision=FeatureGateDecision.PASS,
                entry=entry,
                detail="能建（BUILDABLE）",
            )
        self._log(result)
        return result

    def list_entries(self) -> list[FeatureEntry]:
        """全量裁定清单（审计/复盘用）。"""
        return list(self._load().values())

    def _load(self) -> dict[str, FeatureEntry]:
        if not self._registry_path.exists():
            raise FeatureGateError(f"登记表不存在: {self._registry_path}")
        try:
            data = yaml.safe_load(self._registry_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise FeatureGateError(f"登记表解析失败: {exc}") from exc
        entries: dict[str, FeatureEntry] = {}
        for raw in data.get("features", []):
            adjudicated = raw.get("adjudicated_at")
            entry = FeatureEntry(
                feature=raw["feature"],
                verdict=FeatureVerdict(raw["verdict"]),
                reason=str(raw.get("reason", "")),
                adjudicated_at=(
                    adjudicated
                    if isinstance(adjudicated, date) or adjudicated is None
                    else date.fromisoformat(str(adjudicated))
                ),
                re_review_condition=str(raw.get("re_review_condition", "")),
                related_bm=raw.get("related_bm"),
            )
            entries[entry.feature] = entry
        return entries

    def _log(self, result: FeatureGateResult) -> None:
        self._logger.log(
            "FEATURE_GATE_CHECK",
            "hard_boundary_adjudicator",
            {
                "feature": result.feature,
                "decision": result.decision.value,
                "verdict": result.entry.verdict.value if result.entry else None,
                "detail": result.detail,
            },
        )
