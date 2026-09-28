# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.lifecycle.registry_state_vocab
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT，SSOT 引用不复制); PyYAML（只读 registry 真源）
# [CONSUMERS] zephyr.strategy_pipeline.promotion_advisory._update_registry_lifecycle（待接线一行，
#             92 波次 AI4 车道：注册表 lifecycle_status 写入边界；本窗 strategy_pipeline/** 为禁触
#             热件，接线由总筹落地——见 docs/_working/ai_layer_vision/closure_wave2/
#             AI4_ratification_secrets_vocab.md §三）
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 词表对齐层（F75 缺口 3.6）：FSM 五态词与注册表 lifecycle_status 词是**两套拼写**，
#              跨边界写入必经本模块映射+校验，禁止把 FSM 词直接写进注册表字段（04_lifecycle_fsm.md
#              §四硬伤 1/3：decide approve 曾把 "production" 写进只认注册表词表的字段）；
#              本模块只做**拼写对齐**，不新增边、不改映射语义（裁定 #398/#399 六段词表已正式裁定，
#              本窗不重开词表设计）；注册表允许值优先读 catalog 机读字段 `lifecycle_status_values`
#              （热册，由总筹落地 YAML 块），字段缺失时回退内置临时词表并在报告里标 source；
#              未登记的 FSM 词=抛错 fail-closed（绝不静默写入词表外值）；
#              **边界（防后来者顺手合并）**：本件对象=策略生命周期"FSM 词↔注册表 lifecycle_status 词"
#              拼写对齐；src/zephyr/shared/vocab/market_state.py（SH-VOCAB-001）对象=大盘状态/情绪
#              官方词表本体——跨域不同对象→不并（94 波2 裁定册 §四 边界）
# [MODIFY-GUARD] docs/_working/fullflow_mining/03_promotion_ab/04_lifecycle_fsm.md §四/§五 缺口 1
# [STABILITY] new
# [SAFETY] L（纯映射+只读校验，不写任何真源）
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未映射 FSM 词 → RegistryVocabError（fail-closed）；registry 文件缺失/坏 YAML/
#                  顶层非映射 → 允许值回退内置临时表并记 source="builtin_provisional"（不抛，
#                  因为读取侧与写入侧共用本件，缺文件不得升级为全链拒绝）；显式传入的
#                  allowed_values 为空 → RegistryVocabError（调用方失误面）
# [TESTS] tests/shared/lifecycle/test_registry_state_vocab.py（production→live 钉值/
#         五态全覆盖且无多余/未登记词抛错/词表外值校验拒绝/shelved 收编前后两态/
#         FSM 状态常量与映射定义域同源判别）
"""registry_state_vocab — 策略生命周期"FSM 词 ↔ 注册表词"对齐层（F75 词表对齐缺位治本件）。

大白话：状态机内部说的是"production"，策略注册表里生产态叫"live"。以前拍板转正时把
状态机的话直接抄进注册表，等于在只认八个词的字段里写了个第九种生词——下游（前端/日编 S4/
TDM）都不认得。本件就是抄表前先做翻译并核对拼写的那一层，只管拼写，不改任何流转规则。

真源：`docs/_working/fullflow_mining/03_promotion_ab/04_lifecycle_fsm.md` §四（三处硬伤）
      + §五 缺口 1（词表对齐层缺位）。裁定 #398/#399 已锁定六段词表，本件不重开设计。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Mapping

import yaml

from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

__all__: Final = [
    "DEFAULT_REGISTRY_PATH",
    "FSM_STATE_TO_REGISTRY_STATE",
    "REGISTRY_LIFECYCLE_STATES_PROVISIONAL",
    "RegistryVocabError",
    "LifecycleVocabReport",
    "registry_lifecycle_vocabulary",
    "to_registry_lifecycle_state",
    "assert_registry_lifecycle_state",
    "vocab_report",
]

#: 注册表条目册（热册——本件只读，字段 `lifecycle_status_values` 由总筹按 YAML 块落地）
DEFAULT_REGISTRY_PATH: Final[Path] = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "strategy_registry.yaml"
)
MACHINE_READABLE_FIELD: Final[str] = "lifecycle_status_values"

#: FSM 五态 → 注册表词（**纯拼写映射**，不改变任何边的可达性/守卫语义）
#: candidate/sim/retired 两表同词；production→live（§四硬伤 1）；shelved→shelved
#: （§四硬伤 3：注册表原无此值，须收编进词表——YAML 块待总筹落地）。
FSM_STATE_TO_REGISTRY_STATE: Final[Mapping[str, str]] = {
    "candidate": "candidate",
    "sim": "sim",
    "production": "live",
    "shelved": "shelved",
    "retired": "retired",
}

#: 注册表既有八态词表 + shelved（04_lifecycle_fsm.md §二 3.6 行：schema 注释八态；
#: shelved 收编=总筹 YAML 块内容，机读字段落地前本表=唯一回退真源）
REGISTRY_LIFECYCLE_STATES_PROVISIONAL: Final[frozenset[str]] = frozenset(
    {
        "candidate",
        "backtest",
        "sim",
        "paper",
        "live",
        "monitoring",
        "decayed",
        "retired",
        "shelved",
    }
)


class RegistryVocabError(RuntimeError):
    """词表对齐失败（未映射 FSM 词 / 词表外值 / 调用方传入空词表）。"""

    def __init__(self, msg: str, *, details: dict[str, str] | None = None) -> None:
        super().__init__(msg)
        self.details: dict[str, str] = details or {}


@dataclass(frozen=True)
class LifecycleVocabReport:
    """对齐层自述（审计面：词表来源与规模，不含条目明文）。"""

    source: str
    values: frozenset[str]
    mapped_fsm_states: tuple[str, ...]
    registry_only_values: frozenset[str]


def _read_machine_readable_values(path: Path) -> frozenset[str] | None:
    """读 catalog 的机读允许值字段；任何异常一律 None（=回退，不升级为全链拒绝）。"""
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        logger.info("strategy_registry 缺失，lifecycle 词表回退内置临时真源: %s", path)
        return None
    except (yaml.YAMLError, OSError):
        logger.warning("strategy_registry 读取/解析失败，lifecycle 词表回退内置临时真源: %s", path, exc_info=True)
        return None
    if not isinstance(raw, Mapping):
        return None
    values = raw.get(MACHINE_READABLE_FIELD)
    if not isinstance(values, list) or not values:
        return None
    return frozenset(str(v) for v in values)


def registry_lifecycle_vocabulary(path: Path | None = None) -> tuple[frozenset[str], str]:
    """注册表 lifecycle_status 允许值 + 来源标记（catalog 机读字段优先，回退内置临时表）。

    :param path: 可注入 catalog 路径（测试用 tmp_path 造副本；禁写生产路径）
    """
    target = path or DEFAULT_REGISTRY_PATH
    loaded = _read_machine_readable_values(target)
    if loaded is not None:
        return loaded, "catalog_machine_readable"
    return REGISTRY_LIFECYCLE_STATES_PROVISIONAL, "builtin_provisional"


def to_registry_lifecycle_state(fsm_state: str) -> str:
    """FSM 词 → 注册表词（未登记的 FSM 词=抛错，绝不静默透传词表外值）。"""
    key = str(fsm_state or "").strip()
    if key not in FSM_STATE_TO_REGISTRY_STATE:
        raise RegistryVocabError(
            f"未登记的 FSM 生命周期词:{key or '<empty>'}",
            details={"known": ",".join(sorted(FSM_STATE_TO_REGISTRY_STATE))},
        )
    return str(FSM_STATE_TO_REGISTRY_STATE[key])


def assert_registry_lifecycle_state(
    value: str,
    *,
    allowed_values: frozenset[str] | None = None,
    registry_path: Path | None = None,
) -> str:
    """校验注册表待写值在词表内（越界即抛，弥补 §四"无门禁拦截"）。"""
    if allowed_values is not None and not allowed_values:
        raise RegistryVocabError("allowed_values 不得为空集（调用方失误面）")
    vocab = allowed_values if allowed_values is not None else registry_lifecycle_vocabulary(registry_path)[0]
    candidate = str(value or "").strip()
    if candidate not in vocab:
        raise RegistryVocabError(
            f"lifecycle_status 词表外值:{candidate or '<empty>'}",
            details={"vocabulary": ",".join(sorted(vocab))},
        )
    return candidate


def aligned_lifecycle_state_for_write(
    fsm_state: str,
    *,
    registry_path: Path | None = None,
) -> str:
    """写入边界一步到位：翻译 + 校验（`_update_registry_lifecycle` 待接线行的语义本体）。"""
    translated = to_registry_lifecycle_state(fsm_state)
    vocab, _source = registry_lifecycle_vocabulary(registry_path)
    return assert_registry_lifecycle_state(translated, allowed_values=vocab)


def vocab_report(path: Path | None = None) -> LifecycleVocabReport:
    """对齐层自述快照（只读物化，供审计/看板消费，不产新真源）。"""
    values, source = registry_lifecycle_vocabulary(path)
    mapped = tuple(sorted(set(FSM_STATE_TO_REGISTRY_STATE.values())))
    return LifecycleVocabReport(
        source=source,
        values=values,
        mapped_fsm_states=mapped,
        registry_only_values=frozenset(v for v in values if v not in set(mapped)),
    )
