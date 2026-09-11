# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §registry_alignment
# [MODULE] zephyr.gov_enforcement.registry_alignment
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] yaml（外部）；pathlab/re (stdlib)；zephyr.governance.depgraph_schema（PG 只读，fail-open）
# [CONSUMERS] zephyr.gov_enforcement.commit_gates.business_registry_gate, zephyr.gov_enforcement.commit_gates.industry_chain_map_gate, scripts/governance/d5_architecture/generators/align_all.py, tests/governance/test_registry_alignment_layer2.py, tests/industry_graph/test_field_dictionary_alignment.py
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 注册表对齐第二层唯一逻辑真源（gate/align_all/tests 三方同源，防双真源漂移）；depgraph 存在性 SQL 用 nodes.blueprint_id（2026-09-11 治本：原 nodes.module_id 列不存在致子检查恒 fail-open）；纯读函数零写入；PG 异常一律降级 skip（fail-open）不阻断
# [MODIFY-GUARD] REGISTRY_SPECS 段名/键名变更须同步对应注册表 schema；check_* 返回 (errors, warnings) 二元组约定
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check_*/run_* 永不抛（YAML 损坏→error 条目；PG/IO 异常→warning 条目）；validate_registry_file 保持原契约（YAML 异常向上抛=fail-closed，gate 依赖）
# [TESTS] tests/governance/test_registry_alignment_layer2.py；tests/industry_graph/test_field_dictionary_alignment.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-ALIGN-NAMING-001
# [CREATION-TOKEN] registry-alignment-core-20260911
"""registry_alignment.py — 注册表对齐第二层共享校验核心（全图全库对齐满贯施工 2026-09-11）

病根（第一性原理）
-----------------
alignment_checklist.md 第二层（注册表对齐）此前只有 6 库有 commit gate 强制、其余库
"既有门禁"多为文档口号；且 BUSINESS-REGISTRY gate 的 depgraph 存在性 SQL 查询
``nodes.module_id`` 列——该列在 depgraph schema 中**不存在**（真名为 blueprint_id），
子检查自 2026-09-05 上线起恒 fail-open，从未真正生效。本模块把第二层对齐的
全部校验逻辑收敛为唯一真源，供三方消费：

1. **commit gate**（business_registry_gate / industry_chain_map_gate）——入库硬阻断
2. **align_all.py**（第五节：注册表层）——统一入口恒跑报告
3. **pytest**（tests/governance/test_registry_alignment_layer2.py 等）——回归防线

四方对齐（规则数据）与全图全库对齐的关系：规则四方对齐（RULE-FOUR-WAY-ALIGN）
管 rules/ YAML↔Catalog↔Disk↔Code 纵向闭环；本模块管业务/治理/字典类注册表
↔depgraph↔FK 消费方的横向闭环。二者正交，共同构成全图全库对齐第二层。

Usage::

    from zephyr.gov_enforcement.registry_alignment import (
        REGISTRY_SPECS, validate_registry_file, run_all_registry_validations,
        check_field_dictionary_fk, check_candidate_promotion_chain,
        check_governance_bidirectional, check_industry_graph_field_dictionary,
    )
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import yaml

logger = logging.getLogger(__name__)

__all__: Final = [
    "CATALOGS_DIR",
    "RegistrySpec",
    "REGISTRY_SPECS",
    "validate_registry_file",
    "query_one",
    "module_exists_in_depgraph",
    "missing_depgraph_module_ids",
    "in_flight_module_ids",
    "run_all_registry_validations",
    "check_field_dictionary_fk",
    "check_candidate_promotion_chain",
    "check_governance_bidirectional",
    "check_industry_graph_field_dictionary",
]

_REPO_ROOT = Path(__file__).resolve().parents[3]
CATALOGS_DIR = _REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"


@dataclass(frozen=True)
class RegistrySpec:
    """单库（单段）校验规格（文件名/段名/id 键/显示名）。"""

    filename: str
    section: str
    id_key: str
    display: str


# 19 文件 / 21 段全量业务资产库（2026-09-11 满贯扩容，原 6 库 → 全量；
# 基线 1460 条目 module_id 填充率 100% + MOD-* 格式 100% 已实证后纳入）
REGISTRY_SPECS: tuple[RegistrySpec, ...] = (
    RegistrySpec("strategy_registry.yaml", "strategies", "strategy_id", "策略库"),
    RegistrySpec("factor_registry.yaml", "factors", "factor_id", "因子库"),
    RegistrySpec("technical_indicator_registry.yaml", "indicators", "indicator_id", "技术指标库"),
    RegistrySpec("chart_pattern_registry.yaml", "chart_patterns", "pattern_id", "图形形态库"),
    RegistrySpec("portfolio_model_registry.yaml", "portfolio_models", "model_id", "组合模型库"),
    RegistrySpec("risk_limit_registry.yaml", "risk_limits", "risk_limit_id", "风控限额库"),
    RegistrySpec("universe_registry.yaml", "universes", "universe_id", "股票池库"),
    RegistrySpec("benchmark_registry.yaml", "benchmarks", "benchmark_id", "基准库"),
    RegistrySpec("cost_model_registry.yaml", "cost_models", "cost_model_id", "成本模型库"),
    RegistrySpec("execution_algo_registry.yaml", "execution_algos", "execution_algo_id", "执行算法库"),
    RegistrySpec("data_asset_registry.yaml", "sources", "source_id", "数据资产库·源"),
    RegistrySpec("data_asset_registry.yaml", "datasets", "dataset_id", "数据资产库·数据集"),
    RegistrySpec("data_asset_registry.yaml", "jobs", "job_id", "数据资产库·作业"),
    RegistrySpec("seat_registry.yaml", "seats", "seat_id", "龙虎榜席位库"),
    RegistrySpec("regime_cycle_registry.yaml", "cycles", "cycle_id", "周期分析库"),
    RegistrySpec("event_calendar_registry.yaml", "event_types", "event_type_id", "事件日历库"),
    RegistrySpec("macro_indicator_registry.yaml", "indicators", "indicator_id", "宏观指标库"),
    RegistrySpec("model_registry.yaml", "models", "model_id", "ML 模型库"),
    RegistrySpec("alert_threshold_registry.yaml", "thresholds", "threshold_id", "告警阈值库"),
    RegistrySpec("field_dictionary.yaml", "fields", "field_id", "字段字典"),
    RegistrySpec("experiment_registry.yaml", "experiments", "experiment_id", "实验库"),
)


def validate_registry_file(path: Path, spec: RegistrySpec) -> list[str]:
    """整库确定性校验：id 唯一 + module_id 非空且 MOD-* 前缀。

    Returns:
        fails 列表（空=通过）。YAML 解析异常向上抛（gate fail-closed）。
    """
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    entries = raw.get(spec.section) or []
    fails: list[str] = []
    seen: dict[str, int] = {}
    for idx, e in enumerate(entries):
        if not isinstance(e, dict):
            fails.append(f"{spec.filename}[{idx}] 条目非映射")
            continue
        eid = str(e.get(spec.id_key) or "")
        if not eid:
            fails.append(f"{spec.filename}[{idx}] 缺 {spec.id_key}")
            continue
        if eid in seen:
            fails.append(f"{spec.filename} {spec.id_key} 重复: {eid}（首见 [{seen[eid]}]）")
        seen[eid] = idx
        mid = e.get("module_id")
        if not mid:
            fails.append(
                f"{spec.filename} {eid} 缺 module_id（业务库入库必须挂 depgraph 锚点，"
                "alignment_checklist §4.1——2026-09-05 起强制）"
            )
        elif not str(mid).startswith("MOD-"):
            fails.append(f"{spec.filename} {eid} module_id 非 MOD-* 格式: {mid}")
    return fails


# SQL 常量（NO-BARE-SQL 豁免命名约定 _SQL_*）。2026-09-11 治本：depgraph nodes 表
# 无 module_id 列（真名 blueprint_id，见 depgraph_schema.py CREATE TABLE nodes）——
# 原 SQL 恒报错致存在性子检查自上线起恒 fail-open，从未生效。
_SQL_CHECK_BLUEPRINT_ID = "SELECT 1 FROM nodes WHERE blueprint_id = %s LIMIT 1"
_SQL_GET_BUILD_STATUS = "SELECT build_status FROM nodes WHERE blueprint_id = %s LIMIT 1"
_SQL_CHECK_BM_ANCHOR = "SELECT 1 FROM battle_map_anchors WHERE target_graph = 'depgraph' AND target_id = %s LIMIT 1"


def query_one(query: str, param: str) -> tuple[bool, str | None]:
    """PG 单值查询。返回 (skip, value)；异常=(True, None)=fail-open 跳过子检查。"""
    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, (param,))
                row = cur.fetchone()
        finally:
            conn.close()
        return False, (row[0] if row else None)
    except Exception as e:  # noqa: BLE001 — DB 不可用=fail-open（对标 NEW-FILE-DEPGRAPH gate）
        logger.warning("registry_alignment: PG 查询失败，跳过子检查（fail-open）: %s", e)
        return True, None


def _norm_mid(module_id: str) -> str:
    """module_id 归一化：连字符≡下划线（depgraph 真源口径=下划线，如 MOD-SIGNAL_ASHARE；
    注册表/文件头两种变体并存，比较层归一，不动并行会话数据）。"""
    return module_id.replace("-", "_")


_SQL_CHECK_BLUEPRINT_NORM = "SELECT 1 FROM nodes WHERE REPLACE(blueprint_id, '-', '_') = %s LIMIT 1"


def module_exists_in_depgraph(module_id: str) -> bool:
    """depgraph 存在性查询（SQL 侧 REPLACE 归一——文件头存在混合风格
    MOD-INT_IMPACT_STREAM，纯原形/纯归一双查都会漏，必须 SQL 侧归一比对）。"""
    skip, row = query_one(_SQL_CHECK_BLUEPRINT_NORM, _norm_mid(module_id))
    if skip:
        return True
    return row is not None


def missing_depgraph_module_ids(mids: set[str]) -> tuple[set[str], bool]:
    """批量 depgraph 存在性检查（单查询替代逐 id 往返——满贯批性能治本：16 库数百
    唯一 id 逐条查询曾致 gate 单轮 5-11 分钟）。

    Returns:
        (missing 原值集合, db_ok)。db_ok=False=fail-open（异常，missing 恒空）。
        连字符≡下划线归一：查询用归一化键，缺失映射回原值。
    """
    if not mids:
        return set(), True
    # depgraph blueprint_id 存在三种风格并存（MOD-L02-001 连字符 / MOD-SIGNAL_ASHARE
    # 下划线 / MOD-INT_IMPACT_STREAM 混合）——SQL 侧 REPLACE 归一后比对，防风格漏配。
    norm_map = {_norm_mid(m): m for m in mids}
    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT DISTINCT REPLACE(blueprint_id, '-', '_') FROM nodes "  # noqa: bare-sql  depgraph PG 只读查询（registry_alignment 模块内聚使用，跨库无法集中化到单一 SQL 文件）
                    "WHERE REPLACE(blueprint_id, '-', '_') = ANY(%s)",
                    (sorted(norm_map.keys()),),
                )
                rows = {r[0] for r in cur.fetchall()}
        finally:
            conn.close()
    except Exception as e:  # noqa: BLE001 — DB 不可用=fail-open
        logger.warning("registry_alignment: PG 批量查询失败，跳过子检查（fail-open）: %s", e)
        return set(), False
    missing = {norm_map[n] for n in norm_map if n not in rows}
    return missing, True


_IN_FLIGHT_HEADER_PAT = re.compile(r"^#\s*\[A_module\]\s*module_id=([A-Z0-9_-]+)", re.M)


def in_flight_module_ids() -> frozenset[str]:
    """收集"在途"模块锚：git 工作区相对 HEAD 有变化（staged/unstaged/untracked）的
    .py 文件头部声明的 module_id 集合。

    用途：depgraph 存在性检查的在途豁免——他会话 staged 未提交的实现文件，其
    depgraph 节点要到 commit 后由 reconciler 自动登记（时序竞态，bbe49d0363 同族）；
    扫描器重扫也会剔除未提交文件的历史节点。对在途锚硬校验=误伤并行 WIP。
    """
    import subprocess

    try:
        changed = subprocess.run(  # noqa: bare-subprocess  依赖当前 cwd 的 git 状态扫描（depgraph 仓工作区审计），非可隐藏化场景
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        ).stdout.split()
        untracked = subprocess.run(  # noqa: bare-subprocess  同上：依赖 cwd 的 git 状态扫描
            ["git", "ls-files", "--others", "--exclude-standard"],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        ).stdout.split()
    except Exception:  # noqa: BLE001 — git 不可用=无法判定在途，返回空（保守）
        return frozenset()
    mods: set[str] = set()
    for f in changed + untracked:
        if not f.replace("\\", "/").endswith(".py"):
            continue
        p = _REPO_ROOT / f
        try:
            if not p.exists():
                continue
            head = p.read_text(encoding="utf-8", errors="ignore")[:3000]
        except OSError:  # noqa: BLE001
            continue
        m = _IN_FLIGHT_HEADER_PAT.search(head)
        if m:
            mods.add(m.group(1))
    return frozenset(mods)


def run_all_registry_validations(include_depgraph: bool = True) -> tuple[list[str], int]:
    """全量 21 段注册表校验（align_all 第五节消费）。

    Args:
        include_depgraph: 是否做 depgraph 存在性（PG fail-open）。

    Returns:
        (fails, entry_count)。YAML 损坏不抛——转 error 条目（align_all 场景永不中断）。
    """
    fails: list[str] = []
    total = 0
    for spec in REGISTRY_SPECS:
        path = CATALOGS_DIR / spec.filename
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception as e:  # noqa: BLE001 — 损坏转 error 条目
            fails.append(f"【{spec.display}】YAML 解析异常: {e}")
            continue
        entries = raw.get(spec.section) or []
        total += len(entries)
        try:
            fails.extend(f"【{spec.display}】{x}" for x in validate_registry_file(path, spec))
        except Exception as e:  # noqa: BLE001
            fails.append(f"【{spec.display}】校验异常: {e}")
            continue
        if include_depgraph:
            in_flight = {_norm_mid(x) for x in in_flight_module_ids()}
            mids = {
                str(e.get("module_id"))
                for e in entries
                if isinstance(e, dict) and e.get("module_id")
            }
            missing, _db_ok = missing_depgraph_module_ids(mids)
            for m in sorted(missing):
                if _norm_mid(m) in in_flight:
                    logger.info(
                        "registry_alignment: module_id 在途（实现文件未提交，commit 后 reconciler 自动登记）: %s",
                        m,
                    )
                else:
                    fails.append(f"【{spec.display}】module_id 在 depgraph 不存在: {m}")
    return fails, total


def _fd_build_indexes(fields: list) -> tuple[set[str], dict[str, int], list[str]]:
    """构建字段名集合/field_id 计数（循环抽离降复杂度）。"""
    names: set[str] = set()
    id_counts: dict[str, int] = {}
    dup_warns: list[str] = []
    for e in fields:
        if not isinstance(e, dict):
            continue
        fn = str(e.get("field_name") or "").strip()
        if fn:
            if fn in names:
                dup_warns.append(f"字段字典 field_name 重复: {fn}")
            names.add(fn)
        fid = str(e.get("field_id") or "")
        if fid:
            id_counts[fid] = id_counts.get(fid, 0) + 1
    return names, id_counts, dup_warns


_FD_CONSUMERS: Final = (
    ("factor_registry.yaml", "factors", "factor_id"),
    ("technical_indicator_registry.yaml", "indicators", "indicator_id"),
)


def _fd_scan_consumer(fname: str, sec: str, idk: str, field_names: set[str], referenced: set[str], errors: list[str]) -> None:
    """扫描单个 FK 消费方文件的 inputs 引用（循环抽离降复杂度）。"""
    try:
        raw = yaml.safe_load((CATALOGS_DIR / fname).read_text(encoding="utf-8")) or {}
    except Exception as e:  # noqa: BLE001
        errors.append(f"{fname} 读取失败: {e}")
        return
    for e in raw.get(sec) or []:
        if not isinstance(e, dict):
            continue
        for v in e.get("inputs") or []:
            v = str(v).strip()
            if not v:
                continue
            referenced.add(v)
            if v not in field_names:
                errors.append(f"{fname} {e.get(idk)} inputs 引用字典不存在的字段: {v}")


def check_field_dictionary_fk() -> tuple[list[str], list[str]]:
    """字段字典 FK 闭环（factor.inputs + technical_indicator.inputs ⊆ field_name）。

    Returns:
        (errors, warnings)。errors=悬空引用（引用了字典不存在的字段，硬）；
        warnings=孤儿字段聚合计数（字典按设计是 16 域超集，含契约消费方）。
    """
    errors: list[str] = []
    warnings: list[str] = []
    try:
        fd_raw = yaml.safe_load((CATALOGS_DIR / "field_dictionary.yaml").read_text(encoding="utf-8")) or {}
    except Exception as e:  # noqa: BLE001
        return [f"字段字典读取失败: {e}"], []
    field_names, id_counts, dup_warns = _fd_build_indexes(fd_raw.get("fields") or [])
    errors.extend(dup_warns)
    errors.extend(f"字段字典 field_id 重复: {k}" for k, v in id_counts.items() if v > 1)
    referenced: set[str] = set()
    for fname, sec, idk in _FD_CONSUMERS:
        _fd_scan_consumer(fname, sec, idk, field_names, referenced, errors)
    orphans = len(field_names - referenced)
    if orphans:
        warnings.append(f"字段字典孤儿字段 {orphans} 个（无 inputs 消费方；字典为 16 域超集含契约消费方，正常态——仅计数不列清单）")
    return errors, warnings


_CAND_PROMOTED_EMPTY_CAP = 50  # 空 promoted_to 基线债超过此数视作系统性回退（error）


def _cand_classify(promoted: list[dict]) -> tuple[list[dict], list[dict]]:
    """promoted 条目二分：promoted_to 为空 / 非空但无 MOD 锚（循环抽离）。"""
    empty_pt = [e for e in promoted if not str(e.get("promoted_to") or "").strip()]
    no_mod = [
        e
        for e in promoted
        if str(e.get("promoted_to") or "").strip() and not re.search(r"\bMOD-[A-Z0-9_-]+", str(e.get("promoted_to")))
    ]
    return empty_pt, no_mod


def _cand_anchor_errors(promoted: list[dict]) -> list[str]:
    """带 MOD 锚的转正条目逐个验 depgraph 存在性（循环抽离）。"""
    errors: list[str] = []
    for e in promoted:
        pt = str(e.get("promoted_to") or "")
        for m in sorted(set(re.findall(r"\bMOD-[A-Z0-9_-]+", pt))):
            if not module_exists_in_depgraph(m):
                errors.append(f"CAND 转正链: {e.get('id')} promoted_to 锚点在 depgraph 不存在: {m}")
    return errors


def check_candidate_promotion_chain() -> tuple[list[str], list[str]]:
    """CAND 转正链核查（alignment_checklist §4.2：转正必须迁移+登记 depgraph）。

    分档（2026-09-11 基线标定：promoted=460，promoted_to 空=38 历史债，非空但无
    MOD 锚=342 历史自由文本——均不可硬追溯，降 warn；硬检查=带 MOD 锚的必须在
    depgraph 存在，防未来转正写幽灵锚点）。
    """
    errors: list[str] = []
    warnings: list[str] = []
    try:
        raw = yaml.safe_load((CATALOGS_DIR / "candidate_module_registry.yaml").read_text(encoding="utf-8")) or {}
    except Exception as e:  # noqa: BLE001
        return [f"candidate_module_registry 读取失败: {e}"], []
    entries = raw.get("entries") or []
    promoted = [e for e in entries if isinstance(e, dict) and e.get("status") == "promoted"]
    empty_pt, no_mod = _cand_classify(promoted)
    if empty_pt:
        msg = f"CAND 转正链: promoted 且 promoted_to 为空 {len(empty_pt)} 条（历史基线债）"
        if len(empty_pt) > _CAND_PROMOTED_EMPTY_CAP:
            errors.append(msg + "——超基线容量，疑似系统性回退")
        else:
            warnings.append(msg)
    if no_mod:
        warnings.append(
            f"CAND 转正链: promoted_to 非空但无 MOD-* 锚 {len(no_mod)} 条（历史自由文本，"
            "新转正 MUST 带 MOD-* 锚——基线债不逐条列示）"
        )
    errors.extend(_cand_anchor_errors(promoted))
    return errors, warnings


_ARCH_NORM = re.compile(r"^#?")


def _normalize_issue_ref(ref: str) -> str:
    ref = str(ref).strip()
    return ref if ref.startswith("#") else f"#{ref}"


def _ruling_arch_errors(rulings: list[dict], issue_ids: set[str]) -> list[str]:
    """ruling.related_arch → issue registry 存在性（循环抽离）。"""
    errors: list[str] = []
    for r in rulings:
        for a in r.get("related_arch") or []:
            norm = _normalize_issue_ref(a)
            if norm and norm not in issue_ids:
                errors.append(f"治理双向: {r.get('ruling_id')} related_arch 悬空: {norm}")
    return errors


def _issue_ruling_errors(issues: list[dict], ruling_ids: set[str]) -> list[str]:
    """issue.adjudication 中 裁定#N 引用 → ruling registry 存在性（循环抽离）。"""
    errors: list[str] = []
    pat = re.compile(r"裁定#(\d+(?:-[A-Z])?)")
    for e in issues:
        text = str(e.get("adjudication") or "")
        for m in pat.finditer(text):
            rid = f"裁定#{m.group(1)}"
            if rid not in ruling_ids:
                errors.append(f"治理双向: {e.get('issue_id')} adjudication 引用未登记裁定: {rid}")
    return errors


def check_governance_bidirectional() -> tuple[list[str], list[str]]:
    """治理库双向关联核查（裁定#20 体系：议题↔裁定互指闭合）。

    - ruling.related_arch → issue registry 存在性：硬（结构化字段，基线 0）
    - issue.adjudication 中 裁定#N 引用 → ruling registry 存在性：硬
      （commit 时 RULING-REFERENCE gate 管增量；此处管存量全量对账）
    """
    try:
        ai_raw = yaml.safe_load((CATALOGS_DIR / "architecture_issue_registry.yaml").read_text(encoding="utf-8")) or {}
        ru_raw = yaml.safe_load((CATALOGS_DIR / "ruling_registry.yaml").read_text(encoding="utf-8")) or {}
    except Exception as e:  # noqa: BLE001
        return [f"治理库读取失败: {e}"], []
    issues = ai_raw.get("entries") or []
    rulings = ru_raw.get("entries") or []
    issue_ids = {str(e.get("issue_id")).strip() for e in issues if isinstance(e, dict) and e.get("issue_id")}
    ruling_ids = {str(e.get("ruling_id")).strip() for e in rulings if isinstance(e, dict) and e.get("ruling_id")}
    errors = _ruling_arch_errors(rulings, issue_ids) + _issue_ruling_errors(issues, ruling_ids)
    return errors, []


_IG_DDLPATH = Path(__file__).resolve().parents[3] / "scripts" / "industry_graph" / "apply_industry_graph_ddl.py"


def _ddl_columns() -> dict[str, set[str]]:
    """从 DDL-as-Code 真源解析每表物理列（CREATE TABLE + ALTER ADD COLUMN）。

    逻辑与 tests/industry_graph/test_field_dictionary_alignment.py 同源——该测试
    已改为委托本函数（唯一实现）。
    """
    import importlib.util
    import sys

    cols: dict[str, set[str]] = {}
    spec = importlib.util.spec_from_file_location("_ig_ddl_for_align", _IG_DDLPATH)
    if spec is None or spec.loader is None:
        return cols
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("_ig_ddl_for_align", mod)
    spec.loader.exec_module(mod)
    for stmt in mod.DDL_STATEMENTS:
        s = " ".join(stmt.split())
        m = re.search(r"CREATE TABLE (IF NOT EXISTS )?(\w+)\s*\((.*)\)\s*$", s)
        if m:
            table = m.group(2)
            body = m.group(3)
            body = re.sub(r"\b(UNIQUE|PRIMARY KEY|FOREIGN KEY|CONSTRAINT|CHECK)\s*\([^)]*\)", "", body, flags=re.I)
            for line in body.split(","):
                line = line.strip()
                if not line or re.match(r"(PRIMARY KEY|UNIQUE|FOREIGN|CONSTRAINT)", line, re.I):
                    continue
                cols.setdefault(table, set()).add(line.split()[0])
            continue
        m = re.search(r"ALTER TABLE (\w+) ADD COLUMN IF NOT EXISTS (\w+)", s)
        if m:
            cols.setdefault(m.group(1), set()).add(m.group(2))
    return cols


def _ig_load_engine_ids() -> tuple[set[str] | None, str | None]:
    """加载产业链引擎 CHECKS id 集合（失败返回 (None, 警告文本)）。"""
    import importlib.util
    import sys

    try:
        eng_path = _IG_DDLPATH.parent / "graph_quality_check.py"
        espec = importlib.util.spec_from_file_location("_ig_engine_for_align", eng_path)
        if espec is None or espec.loader is None:
            return None, None
        emod = importlib.util.module_from_spec(espec)
        sys.modules.setdefault("_ig_engine_for_align", emod)
        espec.loader.exec_module(emod)
        return {c["id"] for c in emod.CHECKS} | {"S11", "S19", "S21", "S24"}, None
    except Exception as e:  # noqa: BLE001
        return None, f"产业链引擎常量加载失败（validated_by 对账跳过）: {e}"


def _ig_table_errors(tables: dict, ddl_cols: dict[str, set[str]] | None) -> list[str]:
    """表集双向对账（YAML 表集 = DDL ig_* 表集）。"""
    errors: list[str] = []
    if ddl_cols is None:
        return errors
    ddl_tables = {t for t in ddl_cols if t.startswith("ig_")}
    yaml_tables = set(tables.keys())
    if yaml_tables != ddl_tables:
        errors.append(
            f"产业链字段字典表集与 DDL 不一致: 仅YAML={sorted(yaml_tables - ddl_tables)} "
            f"仅DDL={sorted(ddl_tables - yaml_tables)}"
        )
    return errors


def _ig_field_errors(tables: dict, ddl_cols: dict[str, set[str]] | None, engine_ids: set[str] | None, vocab: dict) -> list[str]:
    """逐字段对账：DDL 列集/validated_by/enum vocab（循环抽离）。"""
    errors: list[str] = []
    for table, spec in tables.items():
        if not isinstance(spec, dict):
            errors.append(f"产业链字段字典 {table} 段非映射")
            continue
        yaml_fields = set((spec.get("fields") or {}).keys())
        if ddl_cols is not None:
            ddl_set = ddl_cols.get(table, set())
            if yaml_fields != ddl_set:
                errors.append(
                    f"产业链字段字典 {table} 字段与 DDL 不一致: "
                    f"仅YAML={sorted(yaml_fields - ddl_set)} 仅DDL={sorted(ddl_set - yaml_fields)}"
                )
        for field, fdef in (spec.get("fields") or {}).items():
            if not isinstance(fdef, dict):
                continue
            refs = fdef.get("validated_by") or []
            if refs and engine_ids is not None:
                dangling = sorted(set(refs) - engine_ids)
                if dangling:
                    errors.append(f"产业链字段字典 {table}.{field} validated_by 引用不存在的检查项: {dangling}")
            t = str(fdef.get("type", ""))
            if t.startswith("enum(vocab:"):
                key = t[len("enum(vocab:") : -1]
                if key not in vocab:
                    errors.append(f"产业链字段字典 {table}.{field} 引用词表 vocab:{key} 不存在")
    return errors


def check_industry_graph_field_dictionary() -> tuple[list[str], list[str]]:  # noqa: gate-vocab  产业链字典=registry catalog，vocab 段是被交叉校验的数据而非加载词表
    """产业链域字段字典结构四边核查（图 8 挂总线配套；词表↔常量比对留 pytest）。

    - YAML 表集 = DDL ig_* 表集（双向）
    - 每表 YAML 字段集 = DDL 物理列集（双向）
    - validated_by 引用的 S 编号在引擎 CHECKS 真实存在
    - type=enum(vocab:xxx) 引用的词表键存在
    """
    errors: list[str] = []
    warnings: list[str] = []
    dict_path = CATALOGS_DIR / "industry_graph_field_dictionary.yaml"
    try:
        d = yaml.safe_load(dict_path.read_text(encoding="utf-8")) or {}
    except Exception as e:  # noqa: BLE001
        return [f"industry_graph_field_dictionary 读取失败: {e}"], []
    tables: dict = d.get("tables") or {}
    try:
        ddl_cols = _ddl_columns()
    except Exception as e:  # noqa: BLE001 — DDL 真源不可解析=环境异常，降 warning
        warnings.append(f"产业链 DDL 真源解析失败（降级跳过表/列对账）: {e}")
        ddl_cols = None
    errors.extend(_ig_table_errors(tables, ddl_cols))
    engine_ids, eng_warn = _ig_load_engine_ids()
    if eng_warn:
        warnings.append(eng_warn)
    errors.extend(_ig_field_errors(tables, ddl_cols, engine_ids, d.get("vocab") or {}))
    return errors, warnings
