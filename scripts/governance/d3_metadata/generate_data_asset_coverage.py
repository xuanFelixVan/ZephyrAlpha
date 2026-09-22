# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/generate_data_asset_coverage.py | §
# [MODULE] scripts.governance.d3_metadata.generate_data_asset_coverage
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.infrastructure.database_service; zephyr.shared.io.file_utils; zephyr.shared.utils.time_utils; schemas.categories; yaml
# [CONSUMERS] docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml（datasets 段增量唯一写者）; check_registry_consistency（entry_counts 对账）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 派生登记唯一产出者=本件（A14 裁定"生成器口径重建（禁手工）"）; 语义字段只从 DDL-as-Code 真源（schemas/categories/*.py 头部）机械派生，无真源模块者以占位描述在册留缺口（禁臆造语义）; entry_counts.datasets 随写入实测刷新; CH 只读（reader/verify），零写库; 时间戳走 time_utils.now_utc（RULE-SCHEMA-TZ）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH 不可达 -> exit 2（不写册）; --check 检出未登记 -> exit 1; 写盘 CAS 冲突 -> 异常上抛（禁静默覆盖）
# [TESTS] 手动: python scripts/governance/d3_metadata/generate_data_asset_coverage.py --check
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 资产册派生登记 CLI（--check 只读对账、写盘为 CAS 增量腿），manual 触发即设计语义；不内建 sleep/Timer（宪法 §9.3）
"""generate_data_asset_coverage.py — CH live 表 → data_asset_registry datasets 增量登记生成器。

治本对象 = dataqa R1×R4 交叉 P2-6 / 战役 A14：CH live 表中数十张未登记
data_asset_registry（REG-DATAFLOW-001）。裁定"生成器口径重建（禁手工）"——本件把
"枚举→对账→登记→计数刷新"变成可重复执行的生成器，禁止手改派生产物。

口径（与 dataqa cross_findings §6 判定一致）：
  1. live 表全集 = CH system.tables（c1_market/c1_backtest/c3_fundamental/c0_meta，
     排除备份/污染命名与 MergeTree 族/View 之外的引擎），reader/verify 只读；
  2. 已登记 = registry datasets[].entity_name 与 `库.表` 精确匹配；
  3. 新增条目 schema 与既有 clickhouse_table 条目同构（DS-271..275 先例），语义字段
     只从 DDL-as-Code 真源（schemas/categories 的 [DOMAIN]/module_id/docstring 定位行）
     机械派生；无真源模块者按库默认域 + 占位描述留缺口（禁臆造语义）；
  4. 写入 = 文本手术只在 datasets 段尾部追加 + 刷新 entry_counts 行（保留全文件注释，
     safe_write_text CAS）。

用法
----
    python .../generate_data_asset_coverage.py --check   # 只读对账：未登记清单，缺口 exit 1
    python .../generate_data_asset_coverage.py --write   # 登记增量并刷新计数（CH 不可达不写）
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "src"))
_GOV_DIR = next(p for p in Path(__file__).resolve().parents if (p / "_shared").exists())
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

import yaml  # noqa: E402
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS  # noqa: E402

from zephyr.shared.io.file_utils import content_sha256, safe_write_text  # noqa: E402
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402  RULE-SCHEMA-TZ

REG_PATH = Path("docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml")
SCAN_DBS = ("c1_market", "c1_backtest", "c3_fundamental", "c0_meta")
# 备份/污染/隔离类命名不计入 live 口径（dataqa R1 §7：备份/污染表已先行分类；
# bak 族=tzbak_2026xxxx/1970clean 修复副本（乙线 A11/A12 处置对象），quar=隔离，dup=重复副本）
_EXCLUDE_RE = re.compile(r"(bak|backup|polluted|^tmp_|_old$|_quar_|_dup$|_v2$)", re.IGNORECASE)
_BASE_ENGINES = {
    "MergeTree",
    "ReplacingMergeTree",
    "SummingMergeTree",
    "AggregatingMergeTree",
    "CollapsingMergeTree",
    "VersionedCollapsingMergeTree",
    "GraphiteMergeTree",
    "View",
}
# 无 DDL 真源模块时的库级默认域（占位登记，待数据线补 DDL-as-Code 后重跑本件刷新）
_DB_DEFAULT_DOMAIN = {
    "c1_market": "D_MKT_DATA",
    "c1_backtest": "D_BACKTEST",
    "c3_fundamental": "D_ASHARE_SIGNAL",
    "c0_meta": "D_DATA_ENG",
}
_TODAY = now_utc().strftime("%Y-%m-%d")


def _load_registry_text() -> str:
    return REG_PATH.read_text(encoding="utf-8")


def _registered_names() -> set[str]:
    data = yaml.safe_load(_load_registry_text()) or {}
    return {e.get("entity_name") for e in data.get("datasets", []) if isinstance(e, dict)}


def _live_ch_tables() -> dict[str, dict[str, Any]]:
    """CH system.tables 只读枚举（reader/verify）。返回 {'db.table': {engine, total_rows}}。"""
    from zephyr.infrastructure.database_service import get_db_service

    conn = get_db_service().get_clickhouse_conn(role="reader", slot="verify")
    dbs = ",".join(f"'{d}'" for d in SCAN_DBS)
    rows = conn.execute(f"SELECT database, name, engine, total_rows FROM system.tables WHERE database IN ({dbs})")  # noqa: bare-sql  system.tables 元数据只读枚举，IN 列表由 SCAN_DBS 动态构成，无法集中化为静态常量
    out: dict[str, dict[str, Any]] = {}
    for db, name, engine, total_rows in rows:
        key = f"{db}.{name}"
        if _EXCLUDE_RE.search(name):
            continue
        if engine.split()[0].strip() not in _BASE_ENGINES:
            continue  # 非基表/视图（内存表、字典等）不入资产册
        out[key] = {"engine": engine, "total_rows": int(total_rows or 0)}
    return out


_DDL_DOMAIN_RE = re.compile(r"^#\s*\[DOMAIN\]\s*(\S+)", re.MULTILINE)
_DDL_MODULE_RE = re.compile(r"^#\s*\[A_module\]\s*module_id=([^\s|]+)", re.MULTILINE)
# 锚点未入 depgraph/battle_map 的模块（2026-09-21 实测：MOD-BT-131/216 depgraph 缺登记；MOD-SIG-148 production 态缺 battle_map 锚）——补锚后从本名单移除并重跑
_UNREGISTERED_MODULE_SKIP = frozenset({"MOD-BT-131", "MOD-BT-216", "MOD-SIG-148"})
_DDL_BLUEPRINT_RE = re.compile(
    r"^#\s*\[BLUEPRINT\]\s*(MOD-[A-Za-z0-9_\-]+)", re.MULTILINE
)  # 旧约定回退：[A_module] 缺席时取 [BLUEPRINT] 头 MOD- 锚


def _doc_table_keys(doc: str, stem: str) -> list[str]:
    """表键判据：docstring 首个「<db>.<table> 表」/「<table> 表」提法；缺则回退文件名主干。"""
    m = re.search(r"((?:c\d_\w+)\.(\w+))\s*表", doc) or re.search(r"(\w+)\s*表", doc)
    keys: list[str] = []
    if m:
        keys.append(m.group(1) if "." in m.group(1) else m.group(1))
        if "." in m.group(1):
            keys.append(m.group(1).split(".", 1)[1])
    keys.append(stem)
    return keys


def _first_meaningful_line(doc: str) -> str:
    """取 docstring 首个非背景说明行作摘要。"""
    for line in doc.splitlines():
        s = line.strip()
        if s and not s.startswith(("本文件", "施工真源", "背景", "病根", "用法", "设计")):
            return s
    return ""


def _ddl_entry(text: str, doc: str, truth_path: str) -> dict[str, str]:
    """从单文件抽取 domain/module_id/summary/truth_path 四元组。"""
    dom = _DDL_DOMAIN_RE.search(text)
    mid = _DDL_MODULE_RE.search(text) or _DDL_BLUEPRINT_RE.search(text)
    return {
        "domain": dom.group(1) if dom else "",
        "module_id": mid.group(1) if mid else "",
        "summary": _first_meaningful_line(doc)[:200],
        "truth_path": truth_path,
    }


def _ddl_truth_index() -> dict[str, dict[str, str]]:
    """扫 schemas/categories/**/*.py，返回 {'库.表'|'表': {domain, module_id, summary, truth_path}}。"""
    out: dict[str, dict[str, str]] = {}
    for p in sorted(Path("schemas/categories").rglob("*.py")):
        if p.name == "__init__.py":
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        try:
            mod = ast.parse(text)
        except SyntaxError:
            continue
        doc = (ast.get_docstring(mod) or "").strip()
        info = _ddl_entry(text, doc, p.as_posix())
        for k in _doc_table_keys(doc, p.stem):
            out.setdefault(k, info)
    return out


def build_new_entries() -> tuple[list[dict[str, Any]], list[str]]:
    """返回（待登记条目, 摘要行清单）。纯内存，不写盘。"""
    live = _live_ch_tables()
    have = _registered_names()
    truth = _ddl_truth_index()
    missing = sorted(k for k in live if k not in have)
    entries: list[dict[str, Any]] = []
    lines: list[str] = []
    for key in missing:
        meta = live[key]
        t = truth.get(key) or truth.get(key.split(".", 1)[1]) or {}
        if not t.get("module_id") or t.get("module_id") in _UNREGISTERED_MODULE_SKIP:
            continue  # 无锚不登记：BUSINESS-REGISTRY 强制 module_id=depgraph 实存模块且已挂 battle_map；缺锚/锚未入册的表留待补锚后重跑本件（禁编造锚点）
        db = key.split(".", 1)[0]
        rows = meta["total_rows"]
        if t.get("summary"):
            summary = f"{t['summary']}；DDL 真源 {t['truth_path']}；{_TODAY} 实测 {rows} 行"
        else:
            summary = (
                f"A14 批量登记占位（无 DDL-as-Code 真源模块，语义字段待数据线补真源后"
                f"重跑本件刷新）；{_TODAY} 实测 {rows} 行"
            )
        entries.append(
            {
                "dataset_id": None,  # write 时按序列填充
                "entity_name": key,
                "entity_type": "dataset",
                "scope": "production",
                "contract_ref": None,
                "physical_type": "clickhouse_table",
                "produced_by_job": None,
                "consumed_by_jobs": [],
                "domain_id": t.get("domain") or _DB_DEFAULT_DOMAIN.get(db, "D_MKT_DATA"),
                "pit_policy": "strict",
                "format_summary": summary,
                "valid_since": _TODAY,
                "module_id": t.get("module_id") or None,
                "name": key,
                "name_zh": None,
                "status": "active",
                "version": "1.0.0",
                "created_at": _TODAY,
                "updated_at": _TODAY,
                "owner": t.get("module_id") or None,
                "produced_by_source": None,
                "survivorship_free": None,
                "pit_available": None,
                "earnings_lag_days": None,
                "llm_training_cutoff": "N/A",
                "lookahead_test_method": "N/A",
                "label_delay_days": None,
                "drift_detector": "none",
                "entry_role": "reference",
                "applies_to": [],
                "tags": [],
                "algorithm_status": "not_applicable",
                "evidence": "",
                "code_symbol": None,
                "code_fingerprint": None,
            }
        )
        lines.append(f"{key} rows={rows} engine={meta['engine']} ddl_truth={'Y' if t else 'N'}")
    return entries, lines


def _next_ds_id(text: str) -> int:
    return max((int(m) for m in re.findall(r"- dataset_id: DS-(\d+)", text)), default=0) + 1


def _dump_entry(entry: dict[str, Any]) -> str:
    body = yaml.dump(entry, allow_unicode=True, sort_keys=False, default_flow_style=False, width=120)
    lines = body.rstrip("\n").splitlines()
    return "\n".join([f"- {lines[0]}"] + [f"  {ln}" for ln in lines[1:]])


def write_increment() -> int:
    """把 build_new_entries() 结果追加进 datasets 段尾并刷新 entry_counts。返回写入条数。"""
    entries, _ = build_new_entries()
    if not entries:
        print("OK 无未登记 live 表，册已覆盖")
        return EXIT_PASS
    text = _load_registry_text()
    base = yaml.safe_load(text) or {}
    total_now = len(base.get("datasets", []))
    start_id = _next_ds_id(text)
    m_start = re.search(r"^datasets:\s*$", text, re.MULTILINE)
    assert m_start, "registry 缺 datasets 段"
    tail = text[m_start.end() :]
    m_next = re.search(r"^jobs:\s*$", tail, re.MULTILINE)
    insert_at = m_start.end() + (m_next.start() if m_next else len(tail))
    for i, e in enumerate(entries):
        e["dataset_id"] = f"DS-{start_id + i}"
    blob = (
        text[:insert_at].rstrip("\n")
        + "\n"
        + "\n".join(_dump_entry(e) for e in entries)
        + "\n\n"
        + text[insert_at:].lstrip("\n")
    )
    # 刷新 entry_counts（派生快照值，以 yaml 实测为准——注释链原样保留）
    blob = re.sub(
        r"^(entry_counts:\s*\{[^}]*datasets:\s*)\d+",
        lambda m: m.group(1) + str(total_now + len(entries)),
        blob,
        count=1,
        flags=re.MULTILINE,
    )
    res = safe_write_text(
        REG_PATH,
        blob,
        expected_base_sha256=content_sha256(text),
        newline="\n",
    )
    print(
        f"WROTE {REG_PATH} +{len(entries)} datasets（DS-{start_id}..DS-{start_id + len(entries) - 1}）"
        f" written={res.written}"
    )
    return len(entries)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CH live 表 → data_asset_registry 增量登记生成器（A14）")
    parser.add_argument("--check", action="store_true", help="只读对账：打印未登记清单，有缺口 exit 1")
    parser.add_argument("--write", action="store_true", help="登记增量并刷新 entry_counts（CAS；CH 不可达 exit 2）")
    args = parser.parse_args(argv)
    try:
        entries, lines = build_new_entries()
    except Exception as exc:  # noqa: BLE001 — CH/IO 不可达=基建故障，按 exit 2 分流
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_ERROR
    if args.write:
        n = write_increment()
        return EXIT_PASS
    for line in lines:
        print(f"MISSING {line}")
    print(f"total_missing={len(entries)}")
    return EXIT_FINDINGS if entries else EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
