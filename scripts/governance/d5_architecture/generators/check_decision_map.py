# [BLUEPRINT] MOD-D_GOV_SCRIPTS | docs/03_modules/_domain_governance/blueprint.md | §check_decision_map
# [MODULE] scripts.governance.d5_architecture.generators.check_decision_map
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.trading.decision_map (load_decision_map/validate_decision_map——校验逻辑单一真源); yaml; ast（stdlib）
# [CONSUMERS] scripts.governance.d5_architecture.generators.align_all (第七图检查项); zephyr.gov_enforcement.commit_gates.decision_map_gate (动态复用)
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只读（零写入）;校验规则单一真源=zephyr.trading.decision_map.validate_decision_map（本文件只做 AST 策略 id 收集+结果分级封装，禁复制 R1-R8）;known_strategy_ids=AST 扫描 src/zephyr/pf_core 全部 strategy_id 字面量（离线、免 import 重模块）
# [MODIFY-GUARD] gate_id="DECISION-MAP" 消费本文件 run_checks——签名 (fails, warns, total) 不得变更
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] run_checks 不吞异常——YAML 损坏/解析异常向上抛（gate 侧 fail-closed）
# [TESTS] tests/governance/test_alignment_gates_red_blue.py
# [A_module] module_id=MOD-D_GOV_SCRIPTS | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-DECISION-MAP-GATE-001
# [CREATION-TOKEN] auto-decision-map-aligner-20260905
"""check_decision_map.py — 第七图（交易决策地图）对齐校验器（#ARCH-DECISION-MAP-GATE-001）

七图对齐升级（2026-09-05，Owner 裁定"全部建造"）
------------------------------------------------
六图（ARCH-ALIGN-UNIFIED-001）之外，第 7 张地图=交易决策地图（config/trading_decision_map.yaml，
MOD-TRADING-015，node_id 轴 TDM-*）。本文件是其对齐校验入口：

  run_checks() -> (fails, warns, total)
    fails = error 级缺口（R1 枚举违规/R2 边断链/R3 策略引用断链/R4 因子断链/R5 数据断链/
            R6 置信度违规/R7 矩阵格断链/R8 sequence 成环）→ 硬阻断
    warns = warning 级（module_ref=null 红节点占位等）→ 不阻断
    total = 节点数

known_strategy_ids 收集：AST 静态扫描 src/zephyr/pf_core/**/*.py 中
strategy_id="..." / TickStrategyMeta 的字面量（8 实盘策略真源=代码 StrategyMeta），
免 import pf_core（避免拉起重依赖）。扫描失败=跳过代码侧集合（仅用 REG-STR-001），不抛异常。

用法::

    from check_decision_map import run_checks
    fails, warns, total = run_checks()

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 地图真源 + 三注册表
#   fields: config/trading_decision_map.yaml + catalogs/{strategy,factor,data_asset}_registry.yaml
#   code: load_decision_map + _load_registry_ids
# - id: I2
#   name: 代码策略 id 字面量
#   fields: src/zephyr/pf_core/**/*.py 的 strategy_id="..."
#   code: _collect_strategy_ids_via_ast
# 层: 算法
# - id: A1
#   name_zh: ① 校验执行
#   name_en: run_checks
#   intro: 调 validate_decision_map（R1-R8）+ AST 策略集合 → error/warning 分级
#   desc: error 级=fails（硬阻断）；warning 级=warns；不吞异常
#   inputs: I1 I2
#   outputs: (fails, warns, total)
# 层: 输出
# - id: O1
#   name_zh: 校验结果三元组
#   name_en: (fails, warns, total)
#   intro: align_all 第七项 + DECISION-MAP gate 共同消费
#   downstream: align_all.py; decision_map_gate.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import ast
from pathlib import Path

__all__ = ["run_checks", "collect_strategy_ids_via_ast"]

_REPO_ROOT = Path(__file__).resolve().parents[4]
_MAP_PATH = _REPO_ROOT / "config" / "trading_decision_map.yaml"
_REGISTRY_DIR = _REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
_PF_CORE_DIR = _REPO_ROOT / "src" / "zephyr" / "pf_core"

# SQL 常量（NO-BARE-SQL 豁免命名约定 _SQL_*，先例=rename_depgraph_sync_gate）
_SQL_CHECK_MODULE_EXISTS = "SELECT 1 FROM nodes WHERE module_id = %s LIMIT 1"
# 数据实存性（R11）：active parts 的最新写入日期与总行数（真源=system.parts，数据监管页同款）
_SQL_DATA_FRESHNESS = (
    "SELECT max(modification_date), sum(rows) FROM system.parts "
    "WHERE active AND database = '{db}' AND table = '{table}'"
)


def collect_strategy_ids_via_ast(pf_core_dir: Path = _PF_CORE_DIR) -> frozenset[str]:
    """AST 扫描 pf_core 下全部 strategy_id="..." 字面量（代码 StrategyMeta 真源）。

    扫描失败（目录缺失等）返回空集——校验器仍可用 REG-STR-001 兜底，不抛异常。
    """
    ids: set[str] = set()
    try:
        if not pf_core_dir.exists():
            return frozenset()
        for py in pf_core_dir.rglob("*.py"):
            try:
                tree = ast.parse(py.read_text(encoding="utf-8"))
            except (SyntaxError, UnicodeDecodeError, OSError):
                continue
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.keyword)
                    and node.arg == "strategy_id"
                    and isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, str)
                ):
                    ids.add(node.value.value)
    except OSError:
        return frozenset()
    return frozenset(ids)


def run_checks(
    map_path: Path | None = None,
    registry_dir: Path | None = None,
) -> tuple[list[str], list[str], int]:
    """第七图校验入口：error 级=fails（硬阻断），warning 级=warns。

    R9（module_ref→depgraph 存在性）在本层实现——PG 只读 fail-open：
    DB 不可达时跳过该子检查（决策地图纯离线校验 R1-R8/R10 已在 zephyr 层完成）。

    Returns:
        (fails, warns, total)——total=地图节点数。YAML 异常向上抛（gate fail-closed）。
    """
    from zephyr.trading.decision_map import load_decision_map, validate_decision_map

    mp = Path(map_path) if map_path else _MAP_PATH
    rd = Path(registry_dir) if registry_dir else _REGISTRY_DIR

    dm = load_decision_map(mp)
    known = collect_strategy_ids_via_ast()
    ok, issues = validate_decision_map(dm, rd, known)

    fails = [f"{i.code} [{i.node_id}] {i.detail}" for i in issues if i.level == "error"]
    warns = [f"{i.code} [{i.node_id}] {i.detail}" for i in issues if i.level == "warning"]

    # R9: 已填 module_ref 的节点必须真实存在于 depgraph（PG fail-open）
    module_refs = sorted({n.module_ref for n in dm.nodes if n.module_ref})
    if module_refs:
        missing = [m for m in module_refs if not _module_exists_in_depgraph(m)]
        fails.extend(f"R9 [map] module_ref 在 depgraph 不存在: {m}" for m in missing)

    # R11: data_refs → CH 表实存性+新鲜度四态（warn 级，N2 数据节点红绿灯）
    try:
        warns.extend(_check_data_existence(dm, rd))
    except Exception as e:  # noqa: BLE001 — R11 是增强检查，异常不阻断主校验
        warns.append(f"R11 [map] 数据实存性检查异常（跳过）: {e}")

    if not ok:
        pass  # ok 语义=fails 为空，已由分级表达
    return fails, warns, len(dm.nodes)


def _query_data_freshness(db: str, table: str) -> str:
    """查 system.parts 最新写入日期与行数（复用 ch_writer 单例与 TCP/HTTP 降级链；失败返回空串）。"""
    from zephyr.data.ch_writer import query as ch_query

    return ch_query(_SQL_DATA_FRESHNESS.format(db=db, table=table))


def _classify_freshness(fresh_date: str, total_rows: int) -> str:
    """四态分类（DS-12 语义：绿=正常/黄=延迟/红=断更/灰=未启动）。"""
    from datetime import date, timedelta

    today = date.today()
    if total_rows == 0:
        return "gray"
    if fresh_date >= today.isoformat():
        return "green"
    if fresh_date >= (today - timedelta(days=3)).isoformat():
        return "yellow"
    return "red"


def _evaluate_ref(ds: str, entity: str) -> tuple[str | None, bool]:
    """单条 DS 引用求值 → (warn|None, ch_down)。ch_down=True 表示 CH 不可达。"""
    if not entity or "." not in entity:
        return (f"R11 [{ds}] 无法解析 CH 表映射（entity_name={entity or '缺失'}）", False)
    db, table = entity.split(".", 1)
    raw = _query_data_freshness(db, table)
    if not raw or "\t" not in raw:
        return ("R11 [map] ClickHouse 不可达，数据实存性检查跳过（fail-open）", True)
    date_str, _, rows_str = raw.strip().partition("\t")
    try:
        rows = int(float(rows_str)) if rows_str not in ("", "\\N") else 0
    except ValueError:
        rows = 0
    state = _classify_freshness(date_str.strip(), rows)
    state_zh = {"green": "正常", "yellow": "延迟", "red": "疑似断更", "gray": "未启动"}[state]
    return (f"R11 [{ds}] {db}.{table} 四态={state_zh}（最新写入 {date_str}，{rows} 行）", False)


def _load_entity_map(registry_dir: Path) -> dict[str, str]:
    """DS-* → CH 表映射（data_asset_registry datasets[].entity_name）。"""
    import yaml as _yaml

    reg = _yaml.safe_load((registry_dir / "data_asset_registry.yaml").read_text(encoding="utf-8")) or {}
    return {
        str(e.get("dataset_id")): str(e.get("entity_name") or "")
        for e in (reg.get("datasets") or [])
        if isinstance(e, dict) and e.get("dataset_id")
    }


def _check_data_existence(dm, registry_dir: Path) -> list[str]:
    """R11：data_refs → DS-* → CH 表实存性+新鲜度 → 四态 warn（N2 需求数据节点红绿灯）。

    warn 级不阻断（数据是运行时状态，commit 时新鲜≠明天新鲜——行业标准=freshness SLI
    做运行时检查不做 CI 门禁）。CH 不可达=整体跳过（fail-open 单条 warn）。
    """
    refs: list[str] = []
    for n in dm.nodes:
        refs.extend(n.data_refs)
    if not refs:
        return []

    entity_by_id = _load_entity_map(registry_dir)
    warns: list[str] = []
    ch_down_notified = False
    for ds in dict.fromkeys(refs):  # 去重保序
        warn, ch_down = _evaluate_ref(ds, entity_by_id.get(ds, ""))
        if ch_down:
            if not ch_down_notified:
                warns.append(warn)
                ch_down_notified = True
            continue
        if warn:
            warns.append(warn)
    return warns


def _module_exists_in_depgraph(module_id: str) -> bool:
    """depgraph 只读存在性查询（fail-open：异常返回 True=跳过子检查，对标 BUSINESS-REGISTRY gate）。"""
    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(_SQL_CHECK_MODULE_EXISTS, (module_id,))
                return cur.fetchone() is not None
        finally:
            conn.close()
    except Exception:  # noqa: BLE001 — DB 不可用=fail-open（warn 交给调用方日志）
        return True
