# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_heritage
# [MODULE] zephyr.ai_layer.heritage.policy
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT)
# [CONSUMERS] zephyr.ai_layer.heritage.store / priors / forget / closure_check; scripts/ai_layer/gen_heritage_human_digest.py
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] heritage_policy.yaml 的唯一读取口（三消费模块不再各自 yaml.safe_load，防口径分叉）;
#              规则=YAML、运行数据=DB（RULE-SSOT 分界，DESIGN §2.2 ⑥）; 数值初值=Owner 夜批追认
#              （README §3.5 L7-#1 已销项），修订走 OBJ_R 四步流水线，禁运行时改值;
#              fail-closed：配置文件缺失/畸形/缺键即抛 HeritagePolicyError，绝不静默回退默认值
# [MODIFY-GUARD] config/heritage_policy.yaml（改动走 OBJ_R 流水线）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 文件缺失/yaml 畸形/类型不符/缺键→HeritagePolicyError（fail-closed）
# [TESTS] tests/ai_layer/heritage/test_heritage_policies.py（真配置装载+缺键/坏类型拒收）
# [TTL] permanent
"""policy — config/heritage_policy.yaml 装载器（L7 规则参数唯一读取口）。

设计真源：``docs/_working/ai_layer_vision/L7_heredity/DESIGN.md`` §2.2 ⑥/§2.5/§2.6/§2.8/§2.9。
阈值/保留期=治理层资产（AI 层不持尺）：本模块只装载不裁决，判据消费方逐值引用。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

import yaml

from zephyr.shared.io.paths import REPO_ROOT

__all__: Final = [
    "AntiIncestPolicy",
    "ClosurePolicy",
    "ForgetFieldPolicy",
    "ForgetPolicy",
    "HeritagePolicy",
    "HeritagePolicyError",
    "RegistrationPolicy",
    "load_policy",
]

DEFAULT_POLICY_PATH: Final = REPO_ROOT / "config" / "heritage_policy.yaml"


class HeritagePolicyError(ValueError):
    """heritage_policy.yaml 缺失/畸形/缺键（fail-closed，绝不静默回退）。

    :param details: 敏感上下文（路径等）走 details 不进消息文本（5.99.20）。
    """

    def __init__(self, msg: str, *, details: dict[str, str] | None = None) -> None:
        super().__init__(msg)
        self.details: dict[str, str] = details or {}


@dataclass(frozen=True)
class RegistrationPolicy:
    """§2.5 登记闸参数。"""

    min_plain_zh_chars: int
    min_narrative_chars: int
    min_recipe_delta_chars: int
    simhash_hamming_max: int
    source_ref_prefixes: tuple[str, ...]
    defect_source_kinds: frozenset[str]
    pattern_slug_re: re.Pattern[str]


@dataclass(frozen=True)
class AntiIncestPolicy:
    """§2.6 防近亲繁殖四条配比约束参数。"""

    prior_factor_min: float
    prior_factor_max: float
    l7_prior_daily_share_max: float
    keyword_groups_min_keep: int
    coverage_freeze_line_pct: float
    coverage_decline_months: int
    total_cells: int
    prior_window_days: int


@dataclass(frozen=True)
class ForgetFieldPolicy:
    """单类条目遗忘参数（§2.8 三类差异化）。"""

    keep_per_cell: int
    compressed_zero_quarters: int
    tombstone_windows: int
    compressed_after_months: int
    keep_per_venue: int


@dataclass(frozen=True)
class ForgetPolicy:
    """§2.8 遗忘机制参数（缺陷/精英/判据三类）。"""

    defect: ForgetFieldPolicy
    elite: ForgetFieldPolicy
    criteria: ForgetFieldPolicy


@dataclass(frozen=True)
class ClosurePolicy:
    """§2.9 关单登记机检参数。"""

    kinds_requiring_heritage: frozenset[str]
    no_new_pattern_reasons: frozenset[str]


@dataclass(frozen=True)
class HeritagePolicy:
    """heritage_policy.yaml 全量只读快照（装载即冻结，进程内不突变）。"""

    policy_id: str
    registration: RegistrationPolicy
    anti_incest: AntiIncestPolicy
    forget: ForgetPolicy
    closure: ClosurePolicy


def _need(table: dict[str, Any], key: str, table_name: str) -> Any:
    if key not in table:
        raise HeritagePolicyError(f"policy_missing_key:{table_name}.{key}")
    return table[key]


def _need_int(table: dict[str, Any], key: str, table_name: str) -> int:
    value = _need(table, key, table_name)
    if not isinstance(value, int) or isinstance(value, bool):
        raise HeritagePolicyError(f"policy_bad_type:{table_name}.{key}(int)")
    return int(value)


def _need_float(table: dict[str, Any], key: str, table_name: str) -> float:
    value = _need(table, key, table_name)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise HeritagePolicyError(f"policy_bad_type:{table_name}.{key}(float)")
    return float(value)


def _need_str_list(table: dict[str, Any], key: str, table_name: str) -> tuple[str, ...]:
    value = _need(table, key, table_name)
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise HeritagePolicyError(f"policy_bad_type:{table_name}.{key}(list[str])")
    return tuple(str(v) for v in value)


def _opt_int(table: dict[str, Any], key: str, table_name: str, default: int = 0) -> int:
    """缺省键按类缺省（每类条目只读各自判据键，非本类键缺席属正常态）。"""
    if key not in table:
        return default
    value = table[key]
    if not isinstance(value, int) or isinstance(value, bool):
        raise HeritagePolicyError(f"policy_bad_type:{table_name}.{key}(int)")
    return int(value)


# 三类条目各自必填的判据键（DESIGN §2.8 表三行一一对应；非本类键缺席=缺省 0 不读）
_FORGET_REQUIRED: Final[dict[str, tuple[str, ...]]] = {
    "defect": ("compressed_zero_quarters",),
    "elite": ("keep_per_cell", "tombstone_windows", "compressed_after_months"),
    "criteria": ("keep_per_venue",),
}


def _parse_forget_field(table: Any, name: str) -> ForgetFieldPolicy:
    if not isinstance(table, dict):
        raise HeritagePolicyError(f"policy_bad_type:forget.{name}(table)")
    for key in _FORGET_REQUIRED.get(name, ()):
        _need(table, key, f"forget.{name}")
    return ForgetFieldPolicy(
        keep_per_cell=_opt_int(table, "keep_per_cell", f"forget.{name}"),
        compressed_zero_quarters=_opt_int(table, "compressed_zero_quarters", f"forget.{name}"),
        tombstone_windows=_opt_int(table, "tombstone_windows", f"forget.{name}"),
        compressed_after_months=_opt_int(table, "compressed_after_months", f"forget.{name}"),
        keep_per_venue=_opt_int(table, "keep_per_venue", f"forget.{name}"),
    )


def load_policy(path: Path | str | None = None) -> HeritagePolicy:
    """装载 heritage_policy.yaml → 冻结快照（fail-closed：缺文件/畸形/缺键一律抛错）。

    :param path: 可注入路径（测试用 tmp_path）；缺省=config/heritage_policy.yaml
    """
    policy_path = Path(path) if path else DEFAULT_POLICY_PATH
    if not policy_path.exists():
        raise HeritagePolicyError("policy_file_missing", details={"path": str(policy_path)})
    try:
        raw = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise HeritagePolicyError(f"policy_yaml_broken:{exc}") from exc
    if not isinstance(raw, dict):
        raise HeritagePolicyError("policy_bad_shape:root(table)")

    reg_raw = _need(raw, "registration", "root")
    if not isinstance(reg_raw, dict):
        raise HeritagePolicyError("policy_bad_shape:registration(table)")
    slug_re_raw = _need(reg_raw, "pattern_slug_re", "registration")
    try:
        slug_re = re.compile(str(slug_re_raw))
    except re.error as exc:
        raise HeritagePolicyError(f"policy_bad_regex:pattern_slug_re:{exc}") from exc
    registration = RegistrationPolicy(
        min_plain_zh_chars=_need_int(reg_raw, "min_plain_zh_chars", "registration"),
        min_narrative_chars=_need_int(reg_raw, "min_narrative_chars", "registration"),
        min_recipe_delta_chars=_need_int(reg_raw, "min_recipe_delta_chars", "registration"),
        simhash_hamming_max=_need_int(reg_raw, "simhash_hamming_max", "registration"),
        source_ref_prefixes=_need_str_list(reg_raw, "source_ref_prefixes", "registration"),
        defect_source_kinds=frozenset(_need_str_list(reg_raw, "defect_source_kinds", "registration")),
        pattern_slug_re=slug_re,
    )

    inc_raw = _need(raw, "anti_incest", "root")
    if not isinstance(inc_raw, dict):
        raise HeritagePolicyError("policy_bad_shape:anti_incest(table)")
    anti_incest = AntiIncestPolicy(
        prior_factor_min=_need_float(inc_raw, "prior_factor_min", "anti_incest"),
        prior_factor_max=_need_float(inc_raw, "prior_factor_max", "anti_incest"),
        l7_prior_daily_share_max=_need_float(inc_raw, "l7_prior_daily_share_max", "anti_incest"),
        keyword_groups_min_keep=_need_int(inc_raw, "keyword_groups_min_keep", "anti_incest"),
        coverage_freeze_line_pct=_need_float(inc_raw, "coverage_freeze_line_pct", "anti_incest"),
        coverage_decline_months=_need_int(inc_raw, "coverage_decline_months", "anti_incest"),
        total_cells=_need_int(inc_raw, "total_cells", "anti_incest"),
        prior_window_days=_need_int(inc_raw, "prior_window_days", "anti_incest"),
    )

    forget_raw = _need(raw, "forget", "root")
    if not isinstance(forget_raw, dict):
        raise HeritagePolicyError("policy_bad_shape:forget(table)")
    forget = ForgetPolicy(
        defect=_parse_forget_field(forget_raw.get("defect"), "defect"),
        elite=_parse_forget_field(forget_raw.get("elite"), "elite"),
        criteria=_parse_forget_field(forget_raw.get("criteria"), "criteria"),
    )

    clo_raw = _need(raw, "closure", "root")
    if not isinstance(clo_raw, dict):
        raise HeritagePolicyError("policy_bad_shape:closure(table)")
    closure = ClosurePolicy(
        kinds_requiring_heritage=frozenset(
            _need_str_list(clo_raw, "kinds_requiring_heritage", "closure")
        ),
        no_new_pattern_reasons=frozenset(
            _need_str_list(clo_raw, "no_new_pattern_reasons", "closure")
        ),
    )

    policy_id = _need(raw, "policy_id", "root")
    if not isinstance(policy_id, str) or not policy_id:
        raise HeritagePolicyError("policy_bad_type:policy_id(str)")
    return HeritagePolicy(
        policy_id=policy_id,
        registration=registration,
        anti_incest=anti_incest,
        forget=forget,
        closure=closure,
    )
