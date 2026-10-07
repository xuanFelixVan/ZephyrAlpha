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
            R6 置信度违规/R7 矩阵格断链/R8 sequence 成环/R9 module_ref 断链/
            R12 battle_map_refs 死引用/R13 挂载指针形态+目的标签枚举与完备性）→ 硬阻断
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
import re
from pathlib import Path

__all__ = ["run_checks", "collect_strategy_ids_via_ast"]

_REPO_ROOT = Path(__file__).resolve().parents[4]
_MAP_PATH = _REPO_ROOT / "config" / "trading_decision_map.yaml"
_FACTORY_MAP_PATH = _REPO_ROOT / "config" / "strategy_production_map.yaml"
_REGISTRY_DIR = _REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
_PF_CORE_DIR = _REPO_ROOT / "src" / "zephyr" / "pf_core"

# R12（battle_map_refs 互挂引用，轴归一手术裁定#483/#487）常量
# 交易段流桶（裁定#483 段归属：这些段的 BM 环节叙事真源在 TDM；无回链=warn 君子协定）
_R12_TRADING_STAGES = frozenset(
    {"buy_flow", "sell_flow", "stock_selection", "position_management", "risk_control", "execution", "reconciliation"}
)
# 留空白名单（裁定#487 §四）：这些 TDM 节点族无 battle_map_refs=合法态，不告警
# ——TDM-E-L9 知识供给轴（横向支撑无生命周期格子）+TDM-C 币圈族（crypto-dev-paused 冻结令）
_R12_EMPTY_LEGAL_PREFIXES = ("TDM-E-L9", "TDM-C-")

# SQL 常量（NO-BARE-SQL 豁免命名约定 _SQL_*，先例=rename_depgraph_sync_gate）
# 审计 F-（AUDIT_REPORT 失明清单#5）修复：原查 nodes.module_id=不存在列→UndefinedColumn
# 被下方 except 吞掉→垃圾 module_ref 恒 True=R9 死检查。TDM module_ref 实值=文件路径
# （159 处），nodes 真列=file_path（111/111 实测命中）。
_SQL_CHECK_MODULE_FILE_EXISTS = "SELECT 1 FROM nodes WHERE file_path = %s LIMIT 1"
# 数据实存性（R11）：active parts 的最新写入日期与总行数（真源=system.parts）
# 2026-09-06 修复：CH 26.x 列名为 modification_time（原 modification_date 报 Code 47
# UNKNOWN_IDENTIFIER→HTTP 映射 404，TCP+HTTP 双失败被误判"CH 不可达"）；toDate() 统一
# TCP(datetime)/HTTP(TSV) 两路径返回格式为 YYYY-MM-DD（与 _classify_freshness 比较口径一致）
_SQL_DATA_FRESHNESS = (
    "SELECT max(toDate(modification_time)), sum(rows) FROM system.parts "
    "WHERE active AND database = '{db}' AND table = '{table}'"
)

# R13（挂载三字段形态+目的标签族，图12收官批 2026-10-07）常量
# MOD-* 指针形态（与 zephyr.trading.decision_map._MOD_ID_RE 同形：2026-09-16 复核班放宽，
# depgraph 库侧已下划线治理 MOD-INT_NEWS_CHAIN 类，连字符-only 正则会误红）
_R13_MOD_ID_RE = re.compile(r"MOD-[A-Z0-9]+(?:[_-][A-Z0-9]+)*")
# 路径指针形态：仓库相对路径（fullmatch 天然排除空白/CJK/散文标点——正文抄入=红）
_R13_PATH_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_./\\-]*")
# 图头标签 id 与节点 purpose_tag 值的骨架（PT-01..PT-12；值域真源=图头 purpose_tags 列表）
_R13_PT_ID_RE = re.compile(r"PT-\d{2}")
# 节点级 confidence（挂载三字段之三，v1.6 spec；与 R6 挂载级 confidence 同词表）
_R13_NODE_CONFIDENCES = frozenset({"verified", "proposed", "untested"})
# 满格四字段（按实图字段名，v1.7 节点规范）：四者皆非空=内容满格节点，
# 缺 purpose_tag=error（R13-3 标签完备性）。判据族无机械标记字段且实图全带标
# （机贴批 3ca6e997c9 起 186/186），规则按全节点从严不设豁免——防"新节点忘贴标"钻空子。
_R13_FULL_FIELDS = ("decision_question", "algo_note_zh", "module_ref", "module_mounts")


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

    # R12: battle_map_refs 互挂引用存在性（轴归一手术裁定#483/#487；PG 只读 fail-open）
    try:
        r12_fails, r12_warns = _check_battle_map_refs()
        fails.extend(r12_fails)
        warns.extend(r12_warns)
    except Exception as e:  # noqa: BLE001 — R12 是增强检查，异常不阻断主校验
        warns.append(f"R12 [map] battle_map_refs 检查异常（跳过）: {e}")

    # R13: 挂载三字段形态+目的标签枚举/落位+满格标签完备性（图12收官批；纯 YAML 只读，
    # 不裹 try——YAML 已被 load_decision_map 解析过，再炸=环境异常，按 ERROR_CONTRACT 上抛）
    fails.extend(_check_r13_mounts_and_purpose_tags(mp))

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


def _check_battle_map_refs() -> tuple[list[str], list[str]]:
    """R12：TDM/工厂节点 battle_map_refs → PG battle_map_steps 存在性（轴归一裁定#483/#487）。

    - 死引用=error（BM 三表冻结真源；引用指向不存在的环节=挂死词）。
    - 留空白名单：TDM-E-L9 知识供给轴/TDM-C 币圈族无 refs=合法态（裁定#487 §四），不告警。
    - 交易段 BM 环节无 TDM 回链=warn 君子协定（聚合计数单行，含 R4 自有；触发率实证后议 gate 化）。
    - 两图均无 battle_map_refs 字段=回滚态，本腿自动 skip。
    - PG 只读 fail-open 只限 DB 不可用类异常；其他异常向上抛（禁吞成死检查，AUDIT 清单#5 同训）。
    """
    import yaml

    from zephyr.governance.persistence.battle_map_reader import BattleMapReader

    fails: list[str] = []
    warns: list[str] = []
    raw_refs: dict[str, list[str]] = {}
    for label, path in (("TDM", _MAP_PATH), ("FACTORY", _FACTORY_MAP_PATH)):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except FileNotFoundError:
            continue
        for n in data.get("nodes") or []:
            refs = n.get("battle_map_refs") or []
            if refs:
                raw_refs[f"{label}:{n.get('node_id')}"] = [str(x) for x in refs]
    if not raw_refs:
        return [], []  # 回滚态 skip（对标 ghost_tdm 腿列缺失语义）

    with BattleMapReader() as reader:
        steps = reader.get_all_steps()
        step_ids = {s.get("step_id") for s in steps}
        all_refs: set[str] = set()
        for refs in raw_refs.values():
            all_refs.update(refs)
        dead = sorted({ref for refs in raw_refs.values() for ref in refs if ref not in step_ids})
        fails.extend(
            f"R12 [{nid}] battle_map_refs 死引用: {d}"
            for nid, refs in sorted(raw_refs.items())
            for d in refs
            if d in dead
        )
        # 交易段无回链君子协定计数：tdm_node_id 列不存在（回滚态）时跳过计数
        if any("tdm_node_id" in s for s in steps):
            n_unlinked = sum(
                1
                for s in steps
                if s.get("flow_stage") in _R12_TRADING_STAGES
                and not s.get("tdm_node_id")
                and s.get("step_id") not in all_refs
            )
            warns.append(
                f"R12 [map] 交易段 BM 无 TDM 回链 {n_unlinked} 条"
                "（君子协定计数，含 R4 自有——裁定#487 §六；触发率实证后再议 gate 化）"
            )
    return fails, warns


def _check_r13_mounts_and_purpose_tags(map_path: Path) -> list[str]:
    """R13 三族（图12收官批 2026-10-07）：挂载指针形态+目的标签枚举/落位+满格标签完备性。

    - R13-1 挂载三字段形态（INV-1 指针制）：module_mounts 成员必须是 MOD-* 模块指针或
      仓库相对路径指针——正文/散文抄进挂载字段=红；module_mounts_influence 键必须 MOD-*
      （值=影响说明散文，合法）；节点级 confidence ∈ R6 同款词表。
    - R13-2 目的标签：节点 purpose_tag ∈ 图头 purpose_tags 枚举（值域真源=图头，禁双真源）；
      自造不存在标签/枚举外值=红；purpose_tag 键必须落 node_id 块界内（nodes 段外出现=红，
      机贴批 3ca6e997c9 手术记录：末节点首插被 portfolio_plan 同缩进 confidence 行吞入的事故复发防线）。
    - R13-3 满格节点标签完备性：四字段（_R13_FULL_FIELDS，按实图字段名）皆非空的节点缺
      purpose_tag=error 级。

    X-R1 拆钉（tdm_mount/g_tag_mount_report §三.1 处方）：段头 TDM-X-R1 持 PT-12
    （kill switch 本体）、其子节点 R1-01/02/03 持 PT-07（熔断预案机制）是合法形态——
    本族不设"同段同标签"父子一致性检查，任何父子女标签组合只要各自合法即放行，
    禁一次性特判（通用规则天然覆盖，拆钉=不引入特例而非加白名单）。

    纯 YAML 只读（两字段不在 frozen dataclass schema，故在本层读 raw；异常向上抛，禁吞）。
    """
    import yaml

    raw = yaml.safe_load(map_path.read_text(encoding="utf-8")) or {}
    fails: list[str] = []

    # 图头枚举真源完整性（R13-2 前置：值域真源坏了枚举校验不可信）
    header = raw.get("purpose_tags")
    pt_ids: set[str] = set()
    if not isinstance(header, list) or not header:
        fails.append("R13 [map] 图头 purpose_tags 缺失或非列表（目的标签值域真源缺失）")
    else:
        for entry in header:
            if not isinstance(entry, dict):
                fails.append(f"R13 [map] 图头 purpose_tags 条目非映射: {entry!r}")
                continue
            pid = str(entry.get("id") or "")
            if not _R13_PT_ID_RE.fullmatch(pid):
                fails.append(f"R13 [map] 图头标签 id 非法（须 PT-NN）: {pid!r}")
            elif pid in pt_ids:
                fails.append(f"R13 [map] 图头标签 id 重复: {pid}")
            else:
                pt_ids.add(pid)
            if not str(entry.get("tag_zh") or "").strip() or not str(entry.get("meaning_zh") or "").strip():
                fails.append(f"R13 [map] 图头标签 {pid or entry!r} 缺 tag_zh/meaning_zh（大白话+意义双字段必填）")

    def _is_pointer(value: str) -> bool:
        """INV-1 指针制：MOD-* 模块指针 或 含 / 的仓库相对路径指针；其余（散文/单词）=非指针。"""
        return bool(_R13_MOD_ID_RE.fullmatch(value)) or ("/" in value and _R13_PATH_RE.fullmatch(value) is not None)

    def _filled(v) -> bool:
        """满格判定：标量非空白串/列表非空；None=空。"""
        if v is None:
            return False
        if isinstance(v, str):
            return bool(v.strip())
        return bool(v)

    for n in raw.get("nodes") or []:
        if not isinstance(n, dict):
            fails.append(f"R13 [map] nodes 条目非映射: {n!r}")
            continue
        nid = str(n.get("node_id") or "?")
        # ── R13-1 挂载三字段形态 ──────────────────────────────────────────
        mounts = n.get("module_mounts")
        if mounts is not None:
            if not isinstance(mounts, list):
                fails.append(f"R13 [{nid}] module_mounts 必须是列表（实态 {type(mounts).__name__}）")
            else:
                for m in mounts:
                    if not isinstance(m, str) or not _is_pointer(m):
                        fails.append(
                            f"R13 [{nid}] module_mounts 成员非指针（INV-1 指针制——"
                            f"禁把正文/散文抄进挂载字段，只收 MOD-* 或路径指针）: {m!r}"
                        )
        influence = n.get("module_mounts_influence")
        if influence is not None:
            if not isinstance(influence, dict):
                fails.append(f"R13 [{nid}] module_mounts_influence 必须是映射（MOD-*→影响说明）")
            else:
                for k in influence:
                    if not _R13_MOD_ID_RE.fullmatch(str(k)):
                        fails.append(f"R13 [{nid}] module_mounts_influence 键非 MOD-* 指针: {k!r}")
        conf = n.get("confidence")
        if conf is not None and str(conf) not in _R13_NODE_CONFIDENCES:
            fails.append(f"R13 [{nid}] 节点 confidence 非法: {conf!r}（词表 verified/proposed/untested）")
        # ── R13-2 purpose_tag 枚举+标量形态 ───────────────────────────────
        pt = n.get("purpose_tag")
        if pt is not None:
            if not isinstance(pt, str) or not _R13_PT_ID_RE.fullmatch(pt):
                fails.append(f"R13 [{nid}] purpose_tag 须为标量 PT-ID（枚举外形态）: {pt!r}")
            elif pt_ids and pt not in pt_ids:
                fails.append(f"R13 [{nid}] purpose_tag 自造/不存在于图头枚举: {pt}")
        # ── R13-3 满格节点标签完备性（error 级）───────────────────────────
        if pt is None and all(_filled(n.get(f)) for f in _R13_FULL_FIELDS):
            fails.append(
                f"R13 [{nid}] 满格节点缺 purpose_tag（{_R13_FULL_FIELDS} 四字段已满格，"
                f"标签缺失=error——目的标签机贴欠账）"
            )

    # R13-2 落位防线：purpose_tag 键禁出现在 nodes 段之外（手术记录复发防线）
    stray: list[str] = []

    def _scan(obj, path: str) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "purpose_tag" and not path.startswith("nodes"):
                    stray.append(path or "<root>")
                _scan(v, f"{path}.{k}" if path else str(k))
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                _scan(v, f"{path}[{i}]")

    _scan({k: v for k, v in raw.items() if k != "nodes"}, "")
    fails.extend(f"R13 [map] purpose_tag 键出现在 nodes 段之外（须落 node_id 块界内）: {p}" for p in stray)
    return fails


def _module_exists_in_depgraph(module_ref: str) -> bool:
    """depgraph 只读存在性查询。

    fail-open 只限 DB 不可用类异常（对标 BUSINESS-REGISTRY gate）；SQL 语法/列名错
    （psycopg2.ProgrammingError）必须抛出——审计教训：UndefinedColumn 被吞→
    R9 沦为垃圾 ID 恒 True 的死检查（AUDIT_REPORT 失明清单#5，处方 B3）。
    """
    try:
        from psycopg2 import ProgrammingError

        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(_SQL_CHECK_MODULE_FILE_EXISTS, (module_ref,))
                return cur.fetchone() is not None
        finally:
            conn.close()
    except ProgrammingError:
        raise
    except Exception:  # noqa: BLE001 — DB 不可用=fail-open（warn 交给调用方日志）
        return True
