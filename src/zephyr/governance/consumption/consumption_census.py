# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-GOV-CONSUMPTIONCENSUS
# [MODULE] zephyr.governance.consumption.consumption_census
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.io.file_utils(safe_write); yaml/pathlib/re/json(静态扫描)
# [CONSUMERS] consumption_census_reconciler(post-commit 事件触发); trading_lifecycle_weekly 能力分支;
#             scripts/governance/d3_metadata/generate_wiring_registry.py(孤岛入账);
#             tests/governance/test_consumption_census_redproof.py(红证)
# [STARTUP] imported(事件触发;禁 cron 自轮询——宪法 §9.3)
# [MATURITY] design
# [INVARIANTS] CONSUMER_SCAN_SCOPE 为 zephyr.governance.consumption.scan_scope_converged（§3.4 唯一真源，
#              壬道收敛）的薄别名——本文件禁再派生口径值/谓词；
#              .md/docs/ 永不计消费者(只记 doc_mentions 证据位)；
#              consumer_files 为文件清单(非计数)；stale 态已显式退役，产出侧不再写该键(理由=案卷 §一)；
#              只读源码/配置，除台账与缓存外零写副作用；同输入必同输出(缓存命中与冷跑结果全等)；
#              零 ClickHouse 读数(案卷 §四 记录 CH query() 返回 TSV 的在途缺陷与本道规避)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 登记册缺失/无条目->ValueError; 扫描根不存在->ValueError; 单文件不可读->跳过(不中断)
# [TESTS] tests/governance/test_consumption_census_redproof.py(tmp_path 合成仓库，红判据 R-5)
# [A_module] module_id=MOD-GOV-CONSUMPTIONCENSUS | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# create-guard-not-dup: 消费面普查引擎（扫描谁在消费资产）与死信所列 heatmap/dataflow/decisiongraph 生成器及对齐 checker 零功能交集——命中词「hit index」「registry doc」系 docstring「全词命中/登记册」措辞的探针碰撞（q-20260928-st-zcloseout-20260926-0001 死信处方）
"""consumption_census — "上架无客"九族消费面普查引擎（包 13.3，丁道）。

14 号文手工普查的机械化替代：登记册条目 → §3.4 单一 scope 全词命中 → 三层排除
（producer/display/infra）→ 消费态判定 → 孤岛按潜在价值排序。

本模块是 `indicator_usage_audit`（MOD-GOV-INDUSAGE，仅族①）的泛化超集：
族① 由本引擎承担，旧模块降为薄壳（保持原签名与原台账路径），避免两套口径并存
（内收判据 w5_1"同真源可派生→必并"）。

三处缺陷的修复对照（旧→新）：
  * `state` 永不出 `stale`  → 显式退役 `stale`（案卷 §一 三条理由），counts 不再广告该键
  * `consumer_files` 存计数  → 存真实文件清单，计数由 len() 派生
  * `.md` 算消费者（IND-REV-001 假绿）→ `.md`/`docs/` 移出消费面，另记 `doc_mentions`

# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/consumption_census.yaml
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable
from dataclasses import dataclass, field, fields, replace
from pathlib import Path
from typing import Any, Final

from zephyr.shared.foundation.errors import ValidationError
from zephyr.shared.io.file_utils import safe_write_text

__all__: Final = [
    "CensusInputError",
    "CensusRequest",
    "CONSUMER_SCAN_SCOPE",
    "FamilySpec",
    "FAMILY_SPECS",
    "get_family",
    "load_family_entities",
    "run_consumption_census",
    "scope_verdict",
]


class CensusInputError(ValidationError, ValueError):
    """普查输入不可用（登记册/真源锚/扫描根缺失，或提取器词表外）。

    房规 5.99.20（MSG-EXPOSURE）：异常消息只说"哪一类东西坏了"，路径与键名等
    可定位细节一律走 ``details`` 通道（日志/审计层落盘），二者不混装。
    同时继承 ``ValueError`` 以守住既有 ERROR_CONTRACT（登记册缺失/无条目→ValueError），
    调用方与测试的 ``except ValueError`` 面零变更。
    """

# ── 单一 scope 定档（§3.4 裁定）──壬道收敛：唯一真源在 zephyr.governance.consumption.scan_scope_converged，
# 本车道全部公开名改**薄别名 import**（禁再派生；收敛裁决=scope_convergence/CASE.md §二）。
# 扫描对象：src/ + scripts/ + config/ 的 .py/.yaml；排除 .md 与 docs/；排除 14 号文三层
# + 观察者层（本道独立发现的第四层，已并入真源）。
# 与 ORPHAN-MODULE 门（git grep src/**/*.py）的分歧不消除：该门判"创建期该不该存在"，
# 本 scope 判"运行期有没有人消费"——跨域不同对象→不并（§4 内收判据），理由见案卷 §二。
from zephyr.governance.consumption.scan_scope_converged import (  # noqa: E402
    CONSUMER_SCAN_SCOPE,
    DISPLAY_EXCLUDE_RE,
    DOC_EVIDENCE_SCOPE,
    EXCLUSION_LAYERS,
    INFRA_EXCLUDE_RE,
    OBSERVER_EXCLUDE_RE,
    PRODUCER_EXCLUDE_RE,
    ScanScope,
    exclusion_layer,
)


_CATALOGS = "docs/01_policies_and_standards/_registry/catalogs"
_DATA_ASSET_REGISTRY = f"{_CATALOGS}/data_asset_registry.yaml"

_TOKEN_SPLIT_RE = re.compile(r"[^0-9a-zA-Z_.\-]+")


# ── 族规格（九族＝14 号文 §一 ①-⑨；每族自带登记册输入与实体提取器）─────────────
@dataclass(frozen=True)
class FamilySpec:
    family_id: str
    label_zh: str
    source: str                 # 实体提取器 kind
    registry_path: str
    list_key: str = ""
    id_key: str = ""
    status_key: str = "status"
    status_filter: tuple[str, ...] = ()   # 空=不过滤
    prefix: str = ""                      # source='dataset_prefix'
    leaf_regex: str = ""                  # source='dataset_regex' / 'file_regex'
    producer_prefix: str = ""             # source='dataset_in_producer_dir'
    union_of: tuple["FamilySpec", ...] = ()   # source='union'
    file_path: str = ""                   # source='file_regex'
    demand_fields: tuple[str, ...] = ()   # 声明需求因子（价值公式第一维）
    alias_fields: tuple[str, ...] = ()    # 登记册别名列（仅"可能有列名消费者"建议位，不计客）
    wiring_target_hint: str = ""          # 建议接线目标（孤岛"往哪接"一栏）
    retired_ids: tuple[str, ...] = ()     # 退役件 token（族②：裁定#233 在册的退役面）
    self_surface: str = ""                # 族自证面：入选该族所依据的代码，不得再算消费者

    def key(self) -> str:
        return self.family_id


def _registry_doc(repo_root: Path, rel: str) -> dict[str, Any]:
    import yaml

    p = repo_root / rel
    if not p.exists():
        raise CensusInputError("族登记册缺失", details={"registry_path": rel})
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def _items_of(reg: dict[str, Any], list_key: str) -> list[dict[str, Any]]:
    """list_key 支持 "a|b" 备选键（旧登记册别名 technical_indicators 与 indicators 并存）。"""
    for k in list_key.split("|"):
        v = reg.get(k)
        if isinstance(v, list):
            return [x for x in v if isinstance(x, dict)]
    return []


def _entities_union(family: FamilySpec, repo_root: Path) -> dict[str, dict[str, Any]]:
    """source='union'＝并集族：逐子族递归装载（子族各自走分派表，禁在此加特例）。"""
    out: dict[str, dict[str, Any]] = {}
    for sub in family.union_of:
        out.update(load_family_entities(sub, repo_root))
    return out


def _entities_file_regex(family: FamilySpec, repo_root: Path) -> dict[str, dict[str, Any]]:
    """source='file_regex'＝从代码真源锚正则提取实体 ID（族④，无登记册）。"""
    p = repo_root / family.file_path
    if not p.exists():
        raise CensusInputError("族④ 真源锚缺失", details={"file_path": family.file_path})
    ids = sorted(set(re.findall(family.leaf_regex, p.read_text(encoding="utf-8", errors="replace"))))
    return {i: {"indicator_id": i, "entity_name": i, "source_anchor": family.file_path} for i in ids}


def _entities_producer_dir(family: FamilySpec, repo_root: Path) -> dict[str, dict[str, Any]]:
    """source='dataset_in_producer_dir'＝被生产者代码点名的登记表条目（族③）。"""
    # 机械定义、无手工清单（宪法 §9.5）
    pool = repo_root / family.producer_prefix
    if not pool.exists():
        raise CensusInputError("族③ 生产者面缺失", details={"producer_prefix": family.producer_prefix})
    toks: set[str] = set()
    for p in pool.rglob("*.py"):
        toks |= _file_tokens(p.read_text(encoding="utf-8", errors="replace"))
    out: dict[str, dict[str, Any]] = {}
    for it in _items_of(_registry_doc(repo_root, family.registry_path), family.list_key):
        eid = it.get("entity_name")
        if not eid:
            continue
        leaf = str(eid).split(".")[-1].lower().replace("-", "_")
        # 准入=多词表名（含下划线且 ≥8 字）——单泛词（composite/target/snapshot）会误纳成伪另类数据表
        if len(leaf) >= 8 and "_" in leaf and leaf in toks:
            out[str(eid)] = it
    return out


def _registry_item_keeps(family: FamilySpec, eid: Any, leaf: str, status: str) -> bool:
    """登记册型族的单条准入判据（registry_ids / dataset_prefix / dataset_regex 三形态共用）。"""
    if not eid:
        return False
    if family.status_filter and status not in family.status_filter:
        return False
    if family.source == "dataset_prefix" and not str(eid).startswith(family.prefix):
        return False
    if family.source == "dataset_regex" and not re.search(family.leaf_regex, leaf, re.I):
        return False
    return True


def _entities_registry_selector(family: FamilySpec, repo_root: Path) -> dict[str, dict[str, Any]]:
    """登记册 + 选择器型族（registry_ids / dataset_prefix / dataset_regex 共用提取器）。"""
    reg = _registry_doc(repo_root, family.registry_path)
    out: dict[str, dict[str, Any]] = {}
    for it in _items_of(reg, family.list_key):
        eid = it.get(family.id_key) or it.get("entity_name")
        leaf = str(eid).split(".")[-1] if eid else ""
        if not _registry_item_keeps(family, eid, leaf, str(it.get(family.status_key, ""))):
            continue
        out[str(eid)] = it
    for tok in family.retired_ids:
        out.setdefault(tok, {"entity_name": tok, "retired_by_declaration": True})
    return out


#: source → 提取器（查表分派替 if-else 阶梯：新增族形态只加一行，不再长函数体）
_FAMILY_EXTRACTORS: Final = {
    "union": _entities_union,
    "file_regex": _entities_file_regex,
    "dataset_in_producer_dir": _entities_producer_dir,
    "registry_ids": _entities_registry_selector,
    "dataset_prefix": _entities_registry_selector,
    "dataset_regex": _entities_registry_selector,
}


def load_family_entities(family: FamilySpec, repo_root: Path) -> dict[str, dict[str, Any]]:
    """族 → {entity_id: 登记册原始条目}（每族自带提取器，禁手工清单=宪法 §9.5）。"""
    extractor = _FAMILY_EXTRACTORS.get(family.source)
    if extractor is None:
        raise CensusInputError("未知实体提取器", details={"source": family.source})
    return extractor(family, repo_root)


def _residual_datasets(fam: FamilySpec, repo_root: Path,
                       entities: dict[str, dict[str, dict[str, Any]]]) -> dict[str, dict[str, Any]]:
    """族⑩＝"已在产登记但九族选择器没框住"的补集（禁手工清单：由九族成员集反推）。"""
    covered = {e for fid, d in entities.items() if fid in TABLE_FAMILIES for e in d}
    out: dict[str, dict[str, Any]] = {}
    for it in _items_of(_registry_doc(repo_root, fam.registry_path), fam.list_key):
        eid = it.get("entity_name")
        if not eid or str(eid) in covered:
            continue
        if it.get("scope") != "production" or not it.get("produced_by_job"):
            continue                      # 判"上架"：有生产作业把数据落进去才算，光有条目不算
        out[str(eid)] = it
    return out


def _token_forms(eid: str) -> set[str]:
    """实体 → 可在文件词元集里精确命中的形态集（全词边界＝14 号文 `\b` 口径的机械等价）。"""
    e = str(eid).lower()
    segs = e.split(".")
    forms = {e, e.replace("-", "_"), "_".join(s.replace("-", "_") for s in segs)}
    if len(segs) > 1:
        leaf = segs[-1].replace("-", "_")
        if len(leaf) >= 4 and not leaf.isdigit():
            forms.add(leaf)
    # 短形态（如 IND-A-001 的 leaf "001"）会全域误命中——一律按长度/纯数字过滤
    return {f for f in forms if len(f) >= 4 and not f.isdigit()}


def _file_tokens(text: str) -> set[str]:
    out: set[str] = set()
    for piece in _TOKEN_SPLIT_RE.split(text):
        if not piece:
            continue
        low = piece.lower()
        out.add(low)
        out.add(low.replace(".", "_"))
        out.add(low.replace("-", "_"))
        sub = re.split(r"[._-]+", low)
        if len(sub) > 1:
            out.add("_".join(sub))
            out.update(x for x in sub if x)
    return out


@dataclass
class _HitIndex:
    """entity → 命中文件（消费者候选面 / 文档证据面 / 别名建议面）。层级过滤在装配期按族做。"""

    all_hits: dict[str, set[str]] = field(default_factory=dict)
    doc_hits: dict[str, set[str]] = field(default_factory=dict)
    alias_hits: dict[str, set[str]] = field(default_factory=dict)


# ── 增量缓存 ─────────────────────────────────────────────────────────────────
def _load_cache(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8")) or {}
    except (OSError, ValueError):
        return {}


def _scan_file(abs_path: Path, token_map: dict[str, set[str]],
               alias_map: dict[str, set[str]] | None = None) -> tuple[str, list[str], list[str]] | None:
    """单文件指纹 + 命中实体列表 + 别名命中列表（仅建议位，不计消费者）。

    指纹=mtime_ns:size:sha1 前 12——mtime/size 相同而内容被替换的场景由 sha1 兜住。
    """
    try:
        st = abs_path.stat()
        raw = abs_path.read_bytes()
    except OSError:
        return None
    fingerprint = f"{st.st_mtime_ns}:{st.st_size}:{hashlib.sha1(raw).hexdigest()[:12]}"
    found = _file_tokens(raw.decode("utf-8", errors="replace"))
    hits = sorted(eid for eid, forms in token_map.items() if found & forms)
    alias = sorted(eid for eid, forms in (alias_map or {}).items() if found & forms)
    return fingerprint, hits, alias


# ── 价值公式（案卷 §四 逐字解释；禁拍脑袋）───────────────────────────────────
VALUE_FORMULA_VERSION: Final = "island_value/1"
VALUE_WEIGHTS: Final = {"declared_demand": 3.0, "build_maturity": 2.0, "registry_priority": 1.0}
_MATURITY_BANDS: Final = {"code_path_present": 1.0, "code_path_missing": 0.5, "doc_ref_only": 0.25, "bare_entry": 0.0}


def _maturity(item: dict[str, Any], repo_root: Path) -> tuple[float, str]:
    cp = item.get("code_path")
    if isinstance(cp, str) and cp.strip():
        return (1.0, "code_path_present") if (repo_root / cp).exists() else (0.5, "code_path_missing")
    if item.get("path") and isinstance(item["path"], str):
        return (1.0, "code_path_present") if (repo_root / item["path"]).exists() else (0.5, "code_path_missing")
    if item.get("doc_ref") or item.get("data_ref") or item.get("module_id"):
        return (0.25, "doc_ref_only")
    return (0.0, "bare_entry")


def _registry_tier(item: dict[str, Any], registry_tier: Any) -> float:
    raw = item.get("tier") or item.get("priority") or registry_tier or 0
    try:
        v = float(raw)
    except (TypeError, ValueError):
        v = {"high": 5.0, "critical": 5.0, "medium": 3.0, "low": 1.0}.get(str(raw).lower(), 0.0)
    return max(0.0, min(5.0, v)) / 5.0


def _declared_demand(item: dict[str, Any], family: FamilySpec) -> int:
    n = 0
    for f in family.demand_fields:
        v = item.get(f)
        if isinstance(v, list):
            n += len([x for x in v if str(x).strip()])
        elif isinstance(v, dict):
            n += len([x for x in v.values() if str(x).strip()])
        elif isinstance(v, str) and v.strip():
            n += 1
    return n


def _proof_cmd(eid: str, family: FamilySpec) -> str:
    pat = "|".join(sorted(_token_forms(eid))[:4])
    return (
        f"grep -rn --include=*.py --include=*.yaml -E '({pat})' src scripts config "
        "| grep -Ev 'src/zephyr/data/implementations/|(provider|collector|fetcher)\\.py$|"
        "src/zephyr/frontend/|scripts/ch|DDL|backfill|src/zephyr/data/config/tasks\\.yaml|"
        "known_data_gaps|data_supply_sentinel|speed_tester' "
        f"# family={family.family_id} 期望输出=空（零消费者）"
    )


# ── 九族规格（顺序＝14 号文矩阵 ①-⑨）───────────────────────────────────────
_F1 = FamilySpec(
    family_id="indicator", label_zh="①技术指标", source="registry_ids",
    registry_path=f"{_CATALOGS}/technical_indicator_registry.yaml", list_key="indicators",
    id_key="indicator_id",
    demand_fields=("used_by_factors", "used_by_strategies"),
    alias_fields=("name", "aliases"),
    wiring_target_hint="src/zephyr/factor/indicator_reader.py PIT 白名单 → factor/analysis/multifactor_synthesis.py（CNS-01）",
)
_F2 = FamilySpec(
    family_id="candle_pattern", label_zh="②图形指标（退役面）", source="registry_ids",
    registry_path=f"{_CATALOGS}/technical_indicator_registry.yaml", list_key="indicators",
    id_key="indicator_id", status_key="status", status_filter=("deprecated",),
    retired_ids=("candle_pattern",),
    demand_fields=("used_by_factors",),
    alias_fields=("name", "aliases"),
    wiring_target_hint="退役件不接线（裁定#233 后继=图形域 MOD-SIG-145 pattern_event_store）",
)
_F3 = FamilySpec(
    family_id="alt_data_table", label_zh="③另类数据表", source="dataset_in_producer_dir",
    registry_path=_DATA_ASSET_REGISTRY, list_key="datasets", id_key="entity_name",
    producer_prefix="src/zephyr/alt_data/",
    self_surface=r"^src/zephyr/alt_data/",
    demand_fields=("consumed_by_jobs",),
    wiring_target_hint="src/zephyr/alt_data/ 消费者或 signal_ashare/（CNS-03/CNS-11/CNS-12）",
)
_F4 = FamilySpec(
    family_id="emotion_component", label_zh="④情绪成分 C1-C6", source="file_regex",
    registry_path="", file_path="src/zephyr/alt_data/emotion_index_builder.py",
    leaf_regex=r"\b(C[1-6]_[a-z][a-z0-9_]*)\b",
    self_surface=r"emotion_index_builder\.py$",
    demand_fields=(),
    wiring_target_hint="data/sector_state_pipeline.py / signal_ashare/sector/sector_state_aggregator.py（D13 缺口）",
)
_F5 = FamilySpec(
    family_id="macro", label_zh="⑤宏观", source="union", registry_path=_DATA_ASSET_REGISTRY,
    union_of=(
        FamilySpec(family_id="macro__mac", label_zh="⑤a MAC-*", source="registry_ids",
                   registry_path=f"{_CATALOGS}/macro_indicator_registry.yaml", list_key="indicators",
                   id_key="indicator_id", demand_fields=("impact_assets", "used_by", "data_ref"),
                   alias_fields=("name", "aliases")),
        FamilySpec(family_id="macro__tables", label_zh="⑤b 宏观表", source="dataset_regex",
                   registry_path=_DATA_ASSET_REGISTRY, list_key="datasets", id_key="entity_name",
                   leaf_regex=r"^(cn_macro|sw_daily|us_index|macro_data|edb_data|us_futures_intraday|"
                              r"macro_[a-z_]+gauge)$",
                   demand_fields=("consumed_by_jobs",)),
    ),
    demand_fields=("impact_assets", "used_by", "data_ref", "consumed_by_jobs"),
    alias_fields=("name", "aliases"),
    wiring_target_hint="regime/regime_cycle_analyzer.py 或 plan_engine 隔夜链（CNS-04 宏观族总裁决）",
)
_F6 = FamilySpec(
    family_id="factor", label_zh="⑥因子", source="registry_ids",
    registry_path=f"{_CATALOGS}/factor_registry.yaml", list_key="factors", id_key="factor_id",
    demand_fields=("belongs_to_strategies",),
    alias_fields=("name", "aliases"),
    wiring_target_hint="src/zephyr/pf_core/strategies/ 挂载 + TDM factor_refs（CNS-09）",
)
_F7 = FamilySpec(
    family_id="strategy", label_zh="⑦策略", source="registry_ids",
    registry_path=f"{_CATALOGS}/strategy_registry.yaml", list_key="strategies", id_key="strategy_id",
    demand_fields=("alpha_sources",),
    alias_fields=("name", "aliases"),
    wiring_target_hint="TDM nodes[].strategy_mounts（族⑦→执行路径）",
)
_F8 = FamilySpec(
    family_id="fundamental_table", label_zh="⑧基本面表", source="dataset_prefix",
    registry_path=_DATA_ASSET_REGISTRY, list_key="datasets", id_key="entity_name",
    prefix="c3_fundamental.", demand_fields=("consumed_by_jobs",),
    wiring_target_hint="data/pit_query.py 白名单 + backtest/core/data_handler.py（CNS-05）",
)
_F9 = FamilySpec(
    family_id="calendar", label_zh="⑨另类日历", source="union", registry_path=_DATA_ASSET_REGISTRY,
    union_of=(
        FamilySpec(family_id="calendar__types", label_zh="⑨a 事件型", source="registry_ids",
                   registry_path=f"{_CATALOGS}/event_calendar_registry.yaml", list_key="event_types",
                   id_key="event_type_id", demand_fields=("used_by_strategies", "data_dataset_ref",
                                                           "data_source"),
                   alias_fields=("name", "aliases")),
        FamilySpec(family_id="calendar__tables", label_zh="⑨b 日历表", source="dataset_regex",
                   registry_path=_DATA_ASSET_REGISTRY, list_key="datasets", id_key="entity_name",
                   leaf_regex=r"^(trade_calendar|hk_trade_calendar|calendar_event|ipo_calendar|"
                              r"ipo_schedule|index_adjustment|disclosure_date|disclosure_plan|"
                              r"share_unlock)$",
                   demand_fields=("consumed_by_jobs",)),
    ),
    demand_fields=("used_by_strategies", "data_dataset_ref", "data_source", "consumed_by_jobs"),
    alias_fields=("name", "aliases"),
    wiring_target_hint="data/event_calendar_filler.py → universe 过滤器（CNS-10）",
)
#: 族⑩ 补集面（本道新增，理由见案卷 §三"覆盖安全网"）：九族选择器都没框住、但确已在产登记的表
#: ——净零对价＝替掉 14 号文 §三手工维护的"63 号 CSV zero_ref 老表"散文账，禁再手抄清单
_F10 = FamilySpec(
    family_id="table_residual", label_zh="⑩族外在产表（补集安全网）", source="dataset_residual",
    registry_path=_DATA_ASSET_REGISTRY, list_key="datasets", id_key="entity_name",
    demand_fields=("consumed_by_jobs",),
    wiring_target_hint="先归类到 ③/⑤/⑧/⑨ 或出死亡证明（CNS-13 零客老表评审）",
)

FAMILY_SPECS: Final = (_F1, _F2, _F3, _F4, _F5, _F6, _F7, _F8, _F9, _F10)

#: 九族（14 号文矩阵 ①-⑨）＋ 一族补集安全网＝⑩；族② 是退役面（零报警预期）
TABLE_FAMILIES: Final = ("alt_data_table", "macro", "fundamental_table", "calendar")

_BY_ID: Final = {f.family_id: f for f in FAMILY_SPECS}
for _f in FAMILY_SPECS:
    _BY_ID[_f.family_id] = _f
    if _f.source == "union":
        for _s in _f.union_of:
            _BY_ID[_s.family_id] = _s


def get_family(family_id: str) -> FamilySpec:
    if family_id not in _BY_ID:
        raise ValueError(f"未知普查族: {family_id}（在册={sorted(_BY_ID)}）")
    return _BY_ID[family_id]


def scope_verdict(rel_path: str) -> bool:
    """公开口径谓词：该文件是否可算消费者＝§3.4 单一 scope 唯一判据入口（含三层排除）。"""
    return CONSUMER_SCAN_SCOPE.counts_as_consumer(rel_path)


# ── 引擎主入口 ───────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class CensusRequest:
    """一次普查的完整入参（房规：入参数 >7 收进 dataclass，NO-LONG-PARAM-LIST 阈值=7）。

    ``force_full`` 由旧公开签名迁入本包：全仓无任何调用方传过它（默认 False=可用缓存），
    公开入口 ``run_consumption_census`` 经 ``CensusRequest`` 仍可注入。
    """

    families: Iterable[Any] | None = None
    repo_root: str | Path | None = None
    scan_root: str | Path | None = None
    output_path: str | Path | None = "data/runtime/consumption_census_ledger.json"
    cache_path: str | Path | None = "data/runtime/consumption_census_cache.json"
    today: str = "2026-09-27"
    include_doc_mentions: bool = True
    force_full: bool = False


@dataclass
class _RunState:
    """一次普查的可变中间态——替掉旧版嵌套闭包，状态显式传给各模块级助手。"""

    repo: Path
    scan: Path
    fam_list: list[FamilySpec]
    entities: dict[str, dict[str, dict[str, Any]]] = field(default_factory=dict)
    token_map: dict[str, set[str]] = field(default_factory=dict)
    alias_map: dict[str, set[str]] = field(default_factory=dict)
    idx: _HitIndex = field(default_factory=_HitIndex)
    files_cache: dict[str, Any] = field(default_factory=dict)
    new_cache: dict[str, Any] = field(default_factory=dict)
    prefix: str = ""
    rescanned: int = 0
    scanned: int = 0


def _token_signature(token_map: dict[str, set[str]]) -> str:
    """实体 token 面指纹——登记册增条目/族改选择器即刻作废旧缓存。

    缓存有效性＝(扫描根, token 签名) 双键：单键版本会把新增实体判成"零命中孤岛"
    （本道实测缺陷，案卷 §六）。
    """
    return hashlib.sha1(
        json.dumps({k: sorted(v) for k, v in sorted(token_map.items())},
                   ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _collect_entities(st: _RunState) -> None:
    """装载各族实体 + token 面 + 别名建议位（顺序敏感：补集族须排在其依赖族之后）。"""
    for fam in st.fam_list:
        if fam.source == "dataset_residual":
            ents = _residual_datasets(fam, st.repo, st.entities)
        else:
            ents = load_family_entities(fam, st.repo)
        st.entities[fam.family_id] = ents
        for eid, item in ents.items():
            st.token_map.setdefault(eid, set()).update(_token_forms(eid))
            for fld in fam.alias_fields:
                v = item.get(fld)
                vals = v if isinstance(v, list) else ([v] if isinstance(v, str) else [])
                for a in vals:
                    a = str(a).strip()
                    if len(a) >= 6 and not a.isdigit():
                        st.alias_map.setdefault(eid, set()).update(_token_forms(a))
    if not st.token_map:
        raise CensusInputError("普查族无实体（登记册全空？）", details={"families": ",".join(
            f.family_id for f in st.fam_list)})


def _prepare_cache(st: _RunState, req: CensusRequest, signature: str) -> None:
    """按 (扫描根, token 签名) 双键取回可用缓存；签名不符则整包作废冷跑。"""
    st.prefix = f"{st.scan.resolve().as_posix()}|"     # 缓存按扫描根分桶，沙盘与生产互不污染
    cache_root = Path(req.cache_path) if req.cache_path is not None else None
    cache: dict[str, Any] = {} if (req.force_full or cache_root is None) else _load_cache(cache_root)
    if cache and cache.get("signature") != signature:
        cache = {}
    files = cache.get("files")
    st.files_cache = files if isinstance(files, dict) else {}


def _record_bucket_hits(st: _RunState, rel: str, hits: list[str], alias: list[str], doc_side: bool) -> None:
    """单文件命中入账：文档侧只记证据，代码侧还须落在扫描面上才计客/记别名。"""
    if not doc_side and CONSUMER_SCAN_SCOPE.in_scan_surface(rel):
        for eid in alias:
            st.idx.alias_hits.setdefault(eid, set()).add(rel)
    for eid in hits:
        if doc_side:
            st.idx.doc_hits.setdefault(eid, set()).add(rel)
        elif CONSUMER_SCAN_SCOPE.in_scan_surface(rel):
            st.idx.all_hits.setdefault(eid, set()).add(rel)


def _scan_one_file(st: _RunState, p: Path, *, doc_side: bool) -> None:
    """扫描面内单文件：缓存命中直接复用，未命中真读并计入 rescanned。"""
    rel = p.relative_to(st.scan).as_posix()
    st.scanned += 1
    key = st.prefix + ("doc:" if doc_side else "src:") + rel
    try:
        s = p.stat()
        stat_key = f"{s.st_mtime_ns}:{s.st_size}"
    except OSError:
        return
    cached = st.files_cache.get(key)
    if cached is not None and cached.get("k") == stat_key:
        hits = list(cached.get("hits", []))
        alias = list(cached.get("alias", []))
        st.new_cache[key] = {"k": stat_key, "hits": hits, "alias": alias}
    else:
        scanned = _scan_file(p, st.token_map, st.alias_map)
        if scanned is None:
            return
        fp, hits, alias = scanned
        st.rescanned += 1
        st.new_cache[key] = {"k": stat_key, "fp": fp, "hits": hits, "alias": alias}
    _record_bucket_hits(st, rel, hits, alias, doc_side)


def _bucketed_scan(st: _RunState, scope: ScanScope, *, doc_side: bool) -> None:
    """按口径面逐文件取证（面/层两分：本函数只入账，判客谓词在 _record_bucket_hits）。"""
    for p in scope.iter_files(st.scan):
        _scan_one_file(st, p, doc_side=doc_side)


def _consumers_for(st: _RunState, eid: str, fam: FamilySpec) -> list[str]:
    """装配期分层过滤＝14 号文三层 + 观察者层 + 族自证面（同族定义所依据的代码不算客）。"""
    kept = []
    for rel in sorted(st.idx.all_hits.get(eid, set())):
        if exclusion_layer(rel) is not None:
            continue
        if fam.self_surface and re.search(fam.self_surface, rel):
            continue
        kept.append(rel)
    return kept


def _producer_only(st: _RunState, eid: str) -> list[str]:
    return [r for r in sorted(st.idx.all_hits.get(eid, set())) if exclusion_layer(r) == "producer"]


def _self_surface(st: _RunState, eid: str, fam: FamilySpec) -> list[str]:
    if not fam.self_surface:
        return []
    return [r for r in sorted(st.idx.all_hits.get(eid, set())) if re.search(fam.self_surface, r)]


def _family_registry_tier(fam: FamilySpec, repo: Path) -> Any:
    """登记册顶层 tier（union 族不取——子族各自有册，取顶层只会拿到 None 语义混淆）。"""
    if fam.source == "union" or not fam.registry_path:
        return None
    return _registry_doc(repo, fam.registry_path).get("tier")


def _entity_row(st: _RunState, fam: FamilySpec, eid: str, item: dict[str, Any],
                reg_tier: Any) -> tuple[dict[str, Any], str]:
    """单实体台账行 + 该实体消费态（value_score 三项加权＝案卷 §三 公式，禁在此改判据）。"""
    consumers = _consumers_for(st, eid, fam)
    prod = _producer_only(st, eid)
    selfs = _self_surface(st, eid, fam)
    docs = sorted(st.idx.doc_hits.get(eid, set()))
    state = _zero_state_of(item, consumers)
    maturity, maturity_band = _maturity(item, st.repo)
    demand = _declared_demand(item, fam)
    prio = _registry_tier(item, reg_tier)
    score = (
        VALUE_WEIGHTS["declared_demand"] * min(demand, 10) / 10
        + VALUE_WEIGHTS["build_maturity"] * maturity
        + VALUE_WEIGHTS["registry_priority"] * prio
    )
    row: dict[str, Any] = {
        "entity_id": eid,
        "family": fam.family_id,
        "state": state,
        "consumer_files": consumers,          # 修复②：清单非计数
        "consumer_count": len(consumers),
        "code_consumers": [c for c in consumers if Path(c).suffix == ".py"],
        "config_consumers": [c for c in consumers if Path(c).suffix in (".yaml", ".yml")],
        "producer_only_hits": prod,
        "self_surface_hits": selfs,           # 入选该族所依据的代码（自证面，不计客）
        "doc_mentions": docs,                 # 修复③：文档只作证据
        "advisory_alias_files": sorted(st.idx.alias_hits.get(eid, set()))[:12],
        "advisory_alias_count": len(st.idx.alias_hits.get(eid, set())),
        "declared_demand_refs": demand,
        "build_maturity": maturity_band,
        "registry_priority": round(prio, 3),
        "value_score": round(score, 4),
    }
    if fam.family_id == "indicator":
        row["recommendation"] = ("keep" if state == "active" else
                                 "retire_candidate(零消费，指标域会话核实后处置)")
    return row, state


def _zero_state_of(item: dict[str, Any], consumers: list[str]) -> str:
    """三态判定（stale 态已显式退役——单一 scope 下为空集，理由=案卷 §一）。"""
    if consumers:
        return "active"
    status = str(item.get("status", ""))
    return "retired" if status == "deprecated" or item.get("retired_by_declaration") else "zero"


def _island_reasons(row: dict[str, Any]) -> list[str]:
    """孤岛归因（为什么零消费）——顺序与文案＝案卷定档，禁静默改判据。"""
    why: list[str] = []
    prod, selfs, docs = row["producer_only_hits"], row["self_surface_hits"], row["doc_mentions"]
    if prod:
        why.append("producer_only(生产者命中已按 14 号文三层排除)")
    if selfs:
        why.append(f"self_surface_only({len(selfs)} 处＝本族入选依据代码，不计客)")
    if docs:
        why.append(f"doc_mention_only({len(docs)} 处 .md，按 §3.4 不计消费)")
    if not row["declared_demand_refs"]:
        why.append("no_declared_demand(登记册需求字段全空)")
    if not why:
        why.append("no_hit_in_scope(src/+scripts/+config/ 全词零命中)")
    return why


def _scan_faces(st: _RunState, *, include_doc_mentions: bool) -> None:
    """代码面 + （可选）文档证据面两轮取证。"""
    _bucketed_scan(st, CONSUMER_SCAN_SCOPE, doc_side=False)
    if include_doc_mentions:
        _bucketed_scan(st, DOC_EVIDENCE_SCOPE, doc_side=True)


def _family_block(fam: FamilySpec, rows: list[dict[str, Any]],
                  fam_islands: list[dict[str, Any]], counts: dict[str, int]) -> dict[str, Any]:
    rows.sort(key=lambda r: r["entity_id"])
    ordered = sorted(fam_islands, key=lambda i: (-i["value_score"], i["entity_id"]))
    return {
        "family_id": fam.family_id,
        "label_zh": fam.label_zh,
        "entity_source": f"{fam.source}:{fam.registry_path or fam.file_path}",
        "counts": counts,
        "island_count": len(fam_islands),
        "entries": rows,
        "islands_top": [i["entity_id"] for i in ordered[:10]],
    }


def _scan_root_of(req: CensusRequest) -> tuple[Path, Path]:
    repo = Path(req.repo_root) if req.repo_root is not None else Path(__file__).resolve().parents[3]
    scan = Path(req.scan_root) if req.scan_root is not None else repo
    if not scan.exists():
        raise CensusInputError("扫描根不存在", details={"scan_root": str(scan)})
    return repo, scan


def _fam_list(req: CensusRequest) -> list[FamilySpec]:
    wanted = req.families or tuple(f.family_id for f in FAMILY_SPECS)
    return [f if isinstance(f, FamilySpec) else get_family(f) for f in wanted]


def _census_doc(st: _RunState, signature: str, families_out: list[dict[str, Any]],
                islands: list[dict[str, Any]], grand_counts: dict[str, int], today: str) -> dict[str, Any]:
    islands.sort(key=lambda i: (-i["value_score"], i["family"], i["entity_id"]))
    return {
        "schema": "consumption_census/2",
        "scope_ruling": "three_piece_infra/00_plan_and_ownership.md §3.4（单一常量 CONSUMER_SCAN_SCOPE）",
        "value_formula": {
            "version": VALUE_FORMULA_VERSION,
            "weights": VALUE_WEIGHTS,
            "terms": {"declared_demand": "min(refs,10)/10", "build_maturity": _MATURITY_BANDS,
                      "registry_priority": "tier/5（缺省取登记册顶层 tier）"},
            "ch_row_count": "本尺零 ClickHouse 读数——见案卷 §四（在途缺陷：query() 返 TSV，下标取到首位数字）",
        },
        "stale_state": "retired(案卷 §一：单一 scope 下 stale 为空集，产出侧不再写该键)",
        "updated_at": today,
        "counts": grand_counts,
        "runtime": {"rescanned_files": st.rescanned, "cached_files": st.scanned - st.rescanned,
                    "files_scanned": st.scanned, "token_signature": signature[:12]},
        "families": families_out,
        "islands": islands,
    }


def _write_outputs(doc: dict[str, Any], output_path: str | Path | None,
                   cache_path: str | Path | None, signature: str,
                   new_cache: dict[str, Any]) -> None:
    """台账与缓存两本账各自落盘（None=该本不写；壳层零副作用走的就是这条开关）。"""
    if output_path is not None:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        safe_write_text(str(out), json.dumps(doc, ensure_ascii=False, indent=1) + "\n", newline="\n")
    if cache_path is not None:
        cp = Path(cache_path)
        cp.parent.mkdir(parents=True, exist_ok=True)
        safe_write_text(str(cp), json.dumps({"schema": "census_cache/2", "signature": signature,
                                             "files": new_cache},
                                            ensure_ascii=False, separators=(",", ":")), newline="\n")


_REQUEST_FIELDS: Final[frozenset[str]] = frozenset(f.name for f in fields(CensusRequest))


def run_consumption_census(*, request: CensusRequest | None = None,
                           **overrides: Any) -> dict[str, Any]:
    """九族消费普查：产台账 JSON + 孤岛清单（按 value_score 降序）。

    scan_root 注入供测试沙盘；repo_root 缺省=登记册上溯三级（生产仓库根）。
    缓存命中与冷跑必须同结果（红证 R-C 断言）。

    入参真源是 :class:`CensusRequest`（房规 >7 入参收进 dataclass）；``overrides``
    只是同一数据类的关键字便捷面——非法键名即刻点名报错，绝不静默吞参数。
    """
    if unknown := sorted(set(overrides) - _REQUEST_FIELDS):
        raise CensusInputError("普查入参含未知键", details={"unknown_keys": ",".join(unknown)})
    base = request or CensusRequest()
    req = replace(base, **overrides) if overrides else base

    repo, scan = _scan_root_of(req)
    st = _RunState(repo=repo, scan=scan, fam_list=_fam_list(req))
    _collect_entities(st)
    signature = _token_signature(st.token_map)
    _prepare_cache(st, req, signature)
    _scan_faces(st, include_doc_mentions=req.include_doc_mentions)

    grand_counts = {"active": 0, "zero": 0, "retired": 0}
    families_out: list[dict[str, Any]] = []
    islands: list[dict[str, Any]] = []
    for fam in st.fam_list:
        counts = {"active": 0, "zero": 0, "retired": 0}
        rows: list[dict[str, Any]] = []
        fam_islands: list[dict[str, Any]] = []
        reg_tier = _family_registry_tier(fam, repo)
        for eid, item in sorted(st.entities[fam.family_id].items()):
            row, state = _entity_row(st, fam, eid, item, reg_tier)
            counts[state] += 1
            grand_counts[state] += 1
            rows.append(row)
            if state == "zero":
                fam_islands.append({**row, "why_zero": _island_reasons(row),
                                    "proof_cmd": _proof_cmd(eid, fam),
                                    "suggested_wiring_target": fam.wiring_target_hint})
        islands.extend(fam_islands)
        families_out.append(_family_block(fam, rows, fam_islands, counts))

    doc = _census_doc(st, signature, families_out, islands, grand_counts, req.today)
    _write_outputs(doc, req.output_path, req.cache_path, signature, st.new_cache)
    return {
        "doc": doc,
        "total_entities": sum(len(f["entries"]) for f in families_out),
        "counts": grand_counts,
        "families": {f["family_id"]: f["counts"] for f in families_out},
        "islands": len(islands),
        "ledger": str(req.output_path) if req.output_path else None,
        "runtime": doc["runtime"],
    }
