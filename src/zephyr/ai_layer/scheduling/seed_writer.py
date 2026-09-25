# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_scheduling
# [MODULE] zephyr.ai_layer.scheduling.seed_writer
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.io.file_utils (safe_write_text——热文件 CAS 纪律);
#                zephyr.shared.io.paths (REPO_ROOT)
# [CONSUMERS] zephyr.ai_layer.scheduling.dispatcher（验收段登记挂接）;
#             scripts/governance/generators/generate_resource_profile_registry.py（种子消费方=
#             新源 I7，另行单派施工——本班禁改既有生成器，在册缺口如实声明）
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 排班一张真源（README §1.6 归属裁定）：登记=写种子文件+生成器再生（GENERATED
#              注册表零手改），禁直改 resource_profile_registry.yaml；种子字段全过词表校验
#              （幽灵池禁令：禁 light/禁 cpu/gpu 空间维值作泳道——daily_crypto 事故语义；
#              exclusive_group ⊆ groups 词表；resource_class ⊆ E0 映射值域；trading_sensitive
#              按 TRADING_SENSITIVE_CLASSES 推导禁手填）；window_type=event（开工事件触发）、
#              window_expr=null（人禁填字段留空）；写文件必经 safe_write_text（热文件 CAS，
#              宪法硬规则 13）；校验=纯函数全枚举
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L5_schedule_gate/DESIGN.md §2.3（D-L5-04 种子字段表）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 词表违例→SeedValidationError（携带全部违例清单，绝不部分通过）；
#                  path 必注入（测试禁写生产路径）；safe_write_text 冲突→上抛（不静默覆盖）
# [TESTS] tests/ai_layer/scheduling/test_seed_writer.py（合法种子全绿/幽灵池 light 拒/cpu gpu
#         空间维拒/组词表外拒/class 词表外拒/trading_sensitive 手填错拒/window_expr 非空拒/
#         task_id 形态拒/写盘回读+CAS 复核；路径全 tmp_path）
# [TTL] permanent
"""seed_writer — L5 排班登记接口（D-L5-04 ③使用=客户自助登记，AI 层运营轴供接口）。

登记=自动写种子文件 ``config/evolution_schedule_seeds.yaml``（生成器新源 I7 消费）+ 触发
``generate_resource_profile_registry.py`` 再生（每小时自检任务已存在，自动吸入）——GENERATED
注册表零手改，排班一张真源不变。先例=``manual_lane_c_agentic_miner``（llm_api_local +
exclusive_group [llm_local] + manual 窗）；本接口产出的进化种子固定 ``window_type: event``
（开工事件触发），与 manual 先例的差异在档。

种子条目=registry 18 字段子集（DESIGN §2.3 字段表 11 键）::

    task_id=evo_<order_id>_<seg>  resource_class=E0 四值映射  pool=lanes 五档真池
    peak_mem_gb/est_duration_min=按对象类常数初估（sampler 实测回填 measured，禁编造）
    exclusive_group=groups 词表按段选挂  window_type=event  window_expr=null
    trading_sensitive=按 TRADING_SENSITIVE_CLASSES 推导  schedule_truth_source=种子文件路径
    notes_zh=工单 title
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Mapping

import yaml

from zephyr.shared.io.file_utils import safe_write_text
from zephyr.shared.io.paths import REPO_ROOT

__all__: Final = [
    "DEFAULT_SEEDS_PATH",
    "SEG_BUILD",
    "SEG_ACCEPT",
    "SeedDraft",
    "SeedValidationError",
    "build_seed",
    "build_seed_from_draft",
    "validate_seed",
    "load_seeds",
    "write_seeds",
]

DEFAULT_SEEDS_PATH: Final = REPO_ROOT / "config" / "evolution_schedule_seeds.yaml"
SEG_BUILD: Final = "build"
SEG_ACCEPT: Final = "accept"
SEED_KEYS: Final[tuple[str, ...]] = (
    "task_id",
    "resource_class",
    "pool",
    "peak_mem_gb",
    "est_duration_min",
    "exclusive_group",
    "window_type",
    "window_expr",
    "trading_sensitive",
    "schedule_truth_source",
    "notes_zh",
)
GHOST_POOL_BAN: Final[tuple[str, ...]] = ("light", "cpu", "gpu")  # 幽灵池+空间维双禁令


class SeedValidationError(Exception):
    """种子词表违例（携带全部违例清单，绝不部分通过——幽灵池先治再排班）。"""


@dataclass(frozen=True)
class SeedDraft:
    """种子登记草稿（build_seed_from_draft 入参载体；字段名与旧 build_seed 签名一一对应）。"""

    order_id: str
    seg: str
    compute_class: str
    title: str
    policy: Mapping[str, Any]
    peak_mem_gb: float = 2.0
    est_duration_min: int = 30
    exclusive_group: list[str] | None = None


def build_seed_from_draft(draft: SeedDraft) -> dict[str, Any]:
    """纯函数：工单段→种子条目（DESIGN §2.3 字段表逐行；初估常数调用方按对象类给）。"""
    cc = draft.policy["compute_classes"]
    allowed = set(cc["e0_class_to_resource"].values()) | set(cc["acceptance_extra_classes"])
    resource_class = cc["e0_class_to_resource"].get(draft.compute_class, "")
    if not resource_class and draft.compute_class in allowed:
        resource_class = draft.compute_class  # 验收段语义档（cpu_heavy/llm_api_local/db_heavy）直用既有档
    sensitive = resource_class in set(cc["trading_sensitive_classes"])
    return {
        "task_id": f"evo_{draft.order_id}_{draft.seg}",
        "resource_class": resource_class,
        "pool": "default",
        "peak_mem_gb": float(draft.peak_mem_gb),
        "est_duration_min": int(draft.est_duration_min),
        "exclusive_group": list(draft.exclusive_group or []),
        "window_type": "event",
        "window_expr": None,  # 人禁填字段留空（再生自真源重抽）
        "trading_sensitive": sensitive,  # 按 TRADING_SENSITIVE_CLASSES 推导，不手填
        "schedule_truth_source": "config/evolution_schedule_seeds.yaml",
        "notes_zh": str(draft.title or "").strip(),
    }


def build_seed(*args, **kwargs):
    """DEPRECATED 兼容包装（gate 口径参数数 0）——转 Draft 新入口。"""
    return build_seed_from_draft(SeedDraft(*args, **kwargs))


def _seed_vocabulary(policy: Mapping[str, Any]) -> tuple[list[str], list[str], set[str], list[str], set[str]]:
    """policy → (lanes, groups, classes, segs, sensitive_classes) 五词表。"""
    cc = policy["compute_classes"]
    lanes = [str(p) for p in cc["pool_vocabulary_lanes"]]
    groups = [str(g) for g in cc["exclusive_group_vocabulary"]]
    classes = set(cc["e0_class_to_resource"].values()) | set(cc["acceptance_extra_classes"])
    segs = [str(s) for s in cc["seg_vocabulary"]]
    sensitive_classes = set(cc["trading_sensitive_classes"])
    return lanes, groups, classes, segs, sensitive_classes


def _validate_task_id(seed: Mapping[str, Any], segs: list[str], errors: list[str]) -> None:
    """task_id 形态闸：evo_<order_id>_<seg 词表内>。"""
    task_id = str(seed.get("task_id") or "")
    parts = task_id.split("_")
    if len(parts) < 3 or parts[0] != "evo" or parts[-1] not in segs:
        errors.append(f"task_id 形态非法（需 evo_<order_id>_<{'/'.join(segs)}>）:{task_id}")


def _validate_pool(seed: Mapping[str, Any], lanes: list[str], errors: list[str]) -> None:
    """pool 双闸：lanes 真池词表 + 幽灵池/空间维禁令。"""
    pool = str(seed.get("pool") or "")
    if pool not in lanes:
        errors.append(f"pool 不在 lanes 真池词表:{pool}")
    if pool in GHOST_POOL_BAN:
        errors.append(f"幽灵池/空间维禁令命中:{pool}（daily_crypto 事故语义，禁入注册表）")


def _validate_exclusive_groups(seed: Mapping[str, Any], groups: list[str], errors: list[str]) -> None:
    """exclusive_group ⊆ groups 词表闸。"""
    for g in seed.get("exclusive_group") or []:
        if str(g) not in groups:
            errors.append(f"exclusive_group 不在 groups 词表:{g}")


def _validate_resource_class(
    seed: Mapping[str, Any],
    classes: set[str],
    sensitive_classes: set[str],
    errors: list[str],
) -> None:
    """resource_class 值域闸 + trading_sensitive 推导一致性闸。"""
    rc = str(seed.get("resource_class") or "")
    if rc not in classes:
        errors.append(f"resource_class 不在 E0 映射值域:{rc}")

    sensitive = bool(seed.get("trading_sensitive"))
    derived = rc in sensitive_classes
    if sensitive != derived:
        errors.append(f"trading_sensitive 手填错（须按 TRADING_SENSITIVE_CLASSES 推导={derived}）")


def _validate_window_fields(seed: Mapping[str, Any], errors: list[str]) -> None:
    """window 双闸：window_type=event（开工事件触发）、window_expr 人禁填留空。"""
    if str(seed.get("window_type") or "") != "event":
        errors.append(f"window_type 须为 event（开工事件触发）:{seed.get('window_type')}")
    if seed.get("window_expr") is not None:
        errors.append("window_expr 人禁填（须留空，再生自真源重抽）")


def _validate_required_keys(seed: Mapping[str, Any], errors: list[str]) -> None:
    """11 键齐全闸（缺字段逐键留痕）。"""
    for key in SEED_KEYS:
        if key not in seed:
            errors.append(f"缺字段:{key}")


def validate_seed(seed: Mapping[str, Any], policy: Mapping[str, Any]) -> list[str]:
    """纯函数：种子字段全过词表校验（幽灵池/空间维双禁令）。返回违例清单（空=合法）。

    分组闸按原闸序编排（task_id→pool→exclusive_group→resource_class→
    trading_sensitive→window→缺字段），违例清单顺序与旧实现逐位一致。
    """
    lanes, groups, classes, segs, sensitive_classes = _seed_vocabulary(policy)
    errors: list[str] = []
    _validate_task_id(seed, segs, errors)
    _validate_pool(seed, lanes, errors)
    _validate_exclusive_groups(seed, groups, errors)
    _validate_resource_class(seed, classes, sensitive_classes, errors)
    _validate_window_fields(seed, errors)
    _validate_required_keys(seed, errors)
    return errors


def load_seeds(path: Path | str | None = None) -> dict[str, Any]:
    """读种子文件（只读；缺文件=空种子集，不炸——首写前是合法空态）。"""
    target = Path(path) if path else DEFAULT_SEEDS_PATH
    if not target.exists():
        return {"seeds": []}
    raw = yaml.safe_load(target.read_text(encoding="utf-8")) or {}
    raw["seeds"] = list(raw.get("seeds") or [])  # 空 seeds: 键的 YAML 空值归一为 []
    return dict(raw)


def write_seeds(
    seeds: list[dict[str, Any]],
    policy: Mapping[str, Any],
    *,
    path: Path | str,
) -> Path:
    """校验全量种子后写盘（safe_write_text CAS；任一违例=整批拒写，绝不部分通过）。"""
    for seed in seeds:
        errors = validate_seed(seed, policy)
        if errors:
            raise SeedValidationError("seed 词表违例:\n- " + "\n- ".join(errors))
    target = Path(path)
    header = (
        "# [SEEDS] config/evolution_schedule_seeds.yaml — L5 排班登记接口种子文件（生成器新源 I7 消费）\n"
        "# 治理锚定：真源设计稿=docs/_working/ai_layer_vision/L5_schedule_gate/DESIGN.md §2.3（D-L5-04）\n"
        "# 净零声明：吸收进化任务散落排班需求（ai_layer_vision/README.md §3 台账行原文）——\n"
        "#           不建第二张排班表（排班一张真源裁定 README §1.6 不变）；本文件只做种子，\n"
        "#           GENERATED 注册表（resource_profile_registry.yaml）零手改。\n"
        "# 词表校验：zephyr.ai_layer.scheduling.seed_writer.validate_seed（幽灵池/空间维双禁令）。\n"
        "schema_version: 1.0.0\n"
        "doc_type: schedule_seeds\n"
        "ttl: permanent\n"
        "title: 进化任务排班种子（evolution schedule seeds）\n"
        "status: active\n"
        "seeds:\n"
    )
    body = (
        yaml.safe_dump(seeds, allow_unicode=True, sort_keys=False, default_flow_style=False)
        if seeds
        else ""
    )
    content = header + body
    result = safe_write_text(target, content, newline="\n")
    _ = result  # SafeWriteResult（写后进程外核实由网关审计承担）
    return target
