# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_cleaning
# [MODULE] zephyr.ai_layer.cleaning.policy
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT)
# [CONSUMERS] zephyr.ai_layer.cleaning.washer; zephyr.ai_layer.cleaning.auditor;
#             zephyr.ai_layer.cleaning.local_prefill（占位枚举）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 常数真源=config/cleaning_policy.yaml（治理层考尺，改动必经 OBJ_R 流水线，
#              本模块零硬编码业务常数——只带加载期结构默认）；fail-closed：文件缺失/
#              必填节缺失/受控枚举类型错→CleaningPolicyError 拒载（绝不带病进产线）；
#              受控枚举装载为 frozenset（只读）；扩词=改 YAML 走 OBJ_R，不改代码；
#              DESIGN 数值追认记录：L3-#1 已销（Owner 2026-09-17 夜批授权原值生效）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L3_cleaning/DESIGN.md §2.2/§2.5（数值变更走 OBJ_R）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 文件缺失/ YAML 解析失败/必填键缺失/受控枚举非序列→CleaningPolicyError
#                  （消息含缺失键路径，机读可 grep）
# [TESTS] tests/ai_layer/cleaning/test_policy.py（缺文件拒载/缺节拒载/正常装载/词表只读化）
# [TTL] permanent
"""policy — L3 清洗考尺装载器：config/cleaning_policy.yaml → 冻结策略对象。

设计真源：``docs/_working/ai_layer_vision/L3_cleaning/DESIGN.md`` §2.2/§2.5；
考尺初值已经 Owner 夜批追认（README §3.5 已销项 L3-#1）。本模块只做"读+形校"，
不做任何业务判定——判定判据分属 washer/auditor；禁止把常数复制进消费模块
（SSOT=那份 YAML，R8-B 净零声明：吸收各稿分散清洗策略常数）。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

import yaml

from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

__all__: Final = ["CleaningPolicy", "CleaningPolicyError", "load_cleaning_policy"]

POLICY_FILENAME: Final = "cleaning_policy.yaml"
DEFAULT_POLICY_PATH: Final = REPO_ROOT / "config" / POLICY_FILENAME

_REQUIRED_SECTIONS: Final[tuple[str, ...]] = (
    "sampling",
    "rubric",
    "wash",
    "judge",
    "placeholder_words",
    "controlled_vocab",
    "task_types",
)
_VOCAB_KEYS: Final[tuple[str, ...]] = (
    "rejection_reasons",
    "risk_flags",
    "regime",
    "frequency",
    "precheck_overall",
    "spec_status",
    "review_verdict",
    "stages",
)


class CleaningPolicyError(RuntimeError):
    """清洗策略装载失败（fail-closed：缺文件/缺节/类型错一律拒载）。

    :param details: 敏感上下文（路径等）走 details 不进消息文本（5.99.20）。
    """

    def __init__(self, msg: str, *, details: dict[str, str] | None = None) -> None:
        super().__init__(msg)
        self.details: dict[str, str] = details or {}


@dataclass(frozen=True)
class CleaningPolicy:
    """清洗考尺只读快照（字段=DESIGN §2.2/§2.5 全部常数，词表已 frozenset 化）。"""

    raw: dict[str, Any]
    cold_start_days: int
    cold_start_cards: int
    periodic_rate: float
    high_impact_full_check: bool
    high_impact_gate_key: str
    high_impact_pass_values: frozenset[str]
    rubric_dimensions: tuple[str, ...]
    rubric_scale_max: int
    zero_score_fails: bool
    rewash_max: int
    cascade_upgrade_max_per_card: int
    per_card_token_budget: int
    default_entry_tier: str
    upgrade_tier: str
    forbid_same_vendor: bool
    forbid_same_tier: bool
    forbid_same_session: bool
    rework_rate_alert: float
    placeholder_words: frozenset[str]
    vocab: dict[str, frozenset[str]]
    task_types: dict[str, str]

    def vocab_of(self, name: str) -> frozenset[str]:
        """取受控词表（未知词表名=编程错误，直接 KeyError 暴露）。"""
        return self.vocab[name]


def _require(mapping: dict[str, Any], key: str, where: str) -> Any:
    if key not in mapping or mapping[key] is None:
        raise CleaningPolicyError(f"cleaning_policy 缺必填键:{where}.{key}")
    return mapping[key]


def _freeze_vocab(raw_vocab: dict[str, Any]) -> dict[str, frozenset[str]]:
    out: dict[str, frozenset[str]] = {}
    for key in _VOCAB_KEYS:
        values = _require(raw_vocab, key, "controlled_vocab")
        if not isinstance(values, (list, tuple)) or not values:
            raise CleaningPolicyError(f"cleaning_policy 受控枚举须非空序列:controlled_vocab.{key}")
        out[key] = frozenset(str(v) for v in values)
    return out


def load_cleaning_policy(path: Path | str | None = None) -> CleaningPolicy:  # noqa: gate-vocab  豁免: 本函数是 cleaning_policy 考尺装载器(policy 文件含 controlled_vocab 节故报错误消息含 vocab 字样),非词表复制——SSoT 不支持的批量分组模式
    """装载清洗考尺（fail-closed）。测试传 tmp_path 自备 YAML，禁触生产文件。"""
    policy_path = Path(path) if path else DEFAULT_POLICY_PATH
    if not policy_path.exists():
        raise CleaningPolicyError("cleaning_policy 文件缺失", details={"path": str(policy_path)})
    try:
        raw = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise CleaningPolicyError(f"cleaning_policy YAML 解析失败:{exc}") from exc
    if not isinstance(raw, dict):
        raise CleaningPolicyError("cleaning_policy 顶层须为映射")
    for section in _REQUIRED_SECTIONS:
        _require(raw, section, "root")

    sampling = raw["sampling"]
    rubric = raw["rubric"]
    wash = raw["wash"]
    judge = raw["judge"]
    dims = tuple(str(d) for d in _require(rubric, "dimensions", "rubric"))
    if len(dims) != 3:
        raise CleaningPolicyError("rubric.dimensions 须三维（DESIGN §2.5 预注册）")
    task_types_raw = _require(raw, "task_types", "root")
    if not isinstance(task_types_raw, dict) or not task_types_raw:
        raise CleaningPolicyError("task_types 须非空映射（工序 -> OBJ_M 轨）")
    return CleaningPolicy(
        raw=raw,
        cold_start_days=int(_require(sampling, "cold_start_days", "sampling")),
        cold_start_cards=int(_require(sampling, "cold_start_cards", "sampling")),
        periodic_rate=float(_require(sampling, "periodic_rate", "sampling")),
        high_impact_full_check=bool(sampling.get("high_impact_full_check", True)),
        high_impact_gate_key=str(sampling.get("high_impact_gate_key", "cross_validation")),
        high_impact_pass_values=frozenset(
            str(v) for v in sampling.get("high_impact_pass_values", ("pass", "已验证", "verified"))
        ),
        rubric_dimensions=dims,
        rubric_scale_max=int(rubric.get("scale_max", 2)),
        zero_score_fails=bool(rubric.get("zero_score_fails", True)),
        rewash_max=int(_require(wash, "rewash_max", "wash")),
        cascade_upgrade_max_per_card=int(
            _require(wash, "cascade_upgrade_max_per_card", "wash")
        ),
        per_card_token_budget=int(_require(wash, "per_card_token_budget", "wash")),
        default_entry_tier=str(wash.get("default_entry_tier", "standard")),
        upgrade_tier=str(wash.get("upgrade_tier", "premium")),
        forbid_same_vendor=bool(judge.get("forbid_same_vendor", True)),
        forbid_same_tier=bool(judge.get("forbid_same_tier", True)),
        forbid_same_session=bool(judge.get("forbid_same_session", True)),
        rework_rate_alert=float(judge.get("rework_rate_alert", 0.10)),
        placeholder_words=frozenset(str(w) for w in raw["placeholder_words"]),
        vocab=_freeze_vocab(raw["controlled_vocab"]),
        task_types={str(k): str(v) for k, v in task_types_raw.items()},
    )
