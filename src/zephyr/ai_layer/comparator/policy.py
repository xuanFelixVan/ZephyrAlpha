# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_comparator
# [MODULE] zephyr.ai_layer.comparator.policy
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT)
# [CONSUMERS] zephyr.ai_layer.comparator.executor (锦标赛 K/轮次);
#             zephyr.ai_layer.comparator.too_good (触发线 G1-G5/ε/归因词表);
#             zephyr.ai_layer.comparator.fairness (公平性词表/带星胜口径)
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 判据常量唯一读取入口：真源=config/comparison_policy.yaml（治理层资产，AI 层不持尺）；
#              只读加载（禁运行时改值，改动走 OBJ_R 四步流水线，DESIGN §2.3）；
#              fail-closed：文件缺失/节缺失/词表空→ComparePolicyError，绝不给静默默认值（尺子残缺=拒考依据，
#              宁可不考不可错考）
# [MODIFY-GUARD] config/comparison_policy.yaml（常量真源，头部治理锚定；改动走 OBJ_R）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] YAML 解析失败/顶层非映射→ComparePolicyError；REQUIRED_SECTIONS 任一缺失→ComparePolicyError
#                  （fail-closed，不猜默认值）；path 可注入（测试禁写生产路径）
# [TESTS] tests/ai_layer/comparator/test_comparison_policy.py（真源文件全节齐/缺节报错/词表与
#         experiment_store 枚举同源）
# [TTL] permanent
"""policy — L4 判据常量层加载器：config/comparison_policy.yaml 的唯一读取入口。

设计真源：``docs/_working/ai_layer_vision/L4_compare/DESIGN.md`` §2.3 常量层（D-L4-03）——
显著性 α、效应量门槛、锦标赛 K、too-good 触发线、公平性词表、阴性拒绝理由受控词表全部
收在治理层常量文件；本模块只做**只读加载+节完整性机检**，不解释语义（解释权在各消费器，
常量含义见 YAML 内逐值锚定注释）。

初值追认：Owner 夜批授权原值生效（vision README §3.5 L4-#1 已销项）；首轮实考数据后
按 OBJ_R 四步流水线提案修订。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Final, Mapping

import yaml

from zephyr.shared.io.paths import REPO_ROOT

__all__: Final = ["DEFAULT_POLICY_PATH", "ComparePolicyError", "load_comparison_policy"]

DEFAULT_POLICY_PATH: Final = REPO_ROOT / "config" / "comparison_policy.yaml"

REQUIRED_SECTIONS: Final[tuple[str, ...]] = (
    "policy_id",
    "significance",
    "too_good_triggers",
    "fairness",
    "verdict_values",
    "status_flow",
    "rejection_reasons",
    "too_good_attribution",
    "tie_reexam_conditions",
    "experiment",
)

TOO_GOOD_TRIGGER_IDS: Final = ("G1_algo", "G2_model", "G3_tool", "G4_replay", "G5_generic")


class ComparePolicyError(Exception):
    """判据常量层残缺/畸形（fail-closed：宁可拒考，不可错考）。

    :param details: 敏感上下文（路径等）走 details 不进消息文本（5.99.20）。
    """

    def __init__(self, msg: str, *, details: dict[str, str] | None = None) -> None:
        super().__init__(msg)
        self.details: dict[str, str] = details or {}


def load_comparison_policy(path: Path | str | None = None) -> dict[str, Any]:
    """加载判据常量层（只读）。缺文件/缺节/坏 YAML 一律 ComparePolicyError，不给静默默认。

    :param path: 常量文件路径（缺省=config/comparison_policy.yaml；测试注入 tmp_path）
    """
    target = Path(path) if path else DEFAULT_POLICY_PATH
    if not target.exists():
        raise ComparePolicyError("comparison_policy 缺文件", details={"path": str(target)})
    try:
        raw = yaml.safe_load(target.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ComparePolicyError(f"comparison_policy 坏 YAML:{exc}") from exc
    if not isinstance(raw, Mapping):
        raise ComparePolicyError(f"comparison_policy 顶层需映射，得:{type(raw).__name__}")
    missing = [section for section in REQUIRED_SECTIONS if section not in raw]
    if missing:
        raise ComparePolicyError(f"comparison_policy 缺节:{','.join(missing)}")
    triggers = raw["too_good_triggers"]
    if not isinstance(triggers, Mapping) or any(
        tid not in triggers for tid in TOO_GOOD_TRIGGER_IDS
    ):
        raise ComparePolicyError(f"too_good_triggers 需含 G1-G5 五组，得:{sorted(dict(triggers or {}))}")
    return dict(raw)
