# [BLUEPRINT] MOD-INF-043 | docs/_working/cold_backup_automation/00_master_plan.md | §9 表行3
# [MODULE] scripts.ch.waste_table_scanner
# [DOMAIN] D_INFRASTRUCTURE
# [DEPENDENCIES] zephyr.infrastructure.database_service(经HTTP); PyYAML
# [CONSUMERS] 人工巡检; 备份成功事件链(可与 rolling_archive_reconciler 同窗运行)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只登记+报警永不自动删(裁定#380①/#382逐表批制) | 新备份表/污染表必落登记册 | 登记册条目只增不删(退役须Owner批)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH不可达→报错退出码1; 登记册损坏→备份后重建空册
# [TESTS] tests/scripts/ch/test_waste_table_scanner.py
# [A_module] module_id=MOD-INF-043-WT | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""waste_table_scanner.py — CH 备份表/污染表扫描登记器（裁定#380① 手动盘点机制）。

大白话：机器定期扫一遍库里有没有"备份表/污染表"（名字带 bak/tzbak/corrupt/pre_tz 的），
发现新面孔就登记造册+报警"待人工盘点"——**永远不自己动手删**，删不删由 Owner
逐表批（裁定#382：不存在 100% 机械可判的废表）。

用法：
    python scripts/ch/waste_table_scanner.py            # 扫描+登记+报警
    python scripts/ch/waste_table_scanner.py --json     # 机读输出
"""

from __future__ import annotations

import argparse
import http.client
import json
import re
import sys
from datetime import date
from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "src"))
from zephyr.shared.io.paths import PROJECT_ROOT  # canonical SSoT（禁本地重定义）

REGISTRY_FILE = PROJECT_ROOT / "docs" / "_working" / "disk_reorg_campaign" / "waste_table_registry.yaml"
# 备份表/污染表名字族（正则，大小写不敏感）
WASTE_PATTERNS = [
    re.compile(r".*_bak_\d+.*", re.IGNORECASE),  # _bak_日期/_bak_256/_bak_1970clean 等
    re.compile(r".*_tzbak_\d+", re.IGNORECASE),
    re.compile(r".*corrupt.*", re.IGNORECASE),
    re.compile(r".*_pre_tz.*", re.IGNORECASE),
]
# 已知合法例外（备份表命名但不属废表治理域的，如注解表），空=无
EXEMPT: set[str] = set()

__all__ = ["scan_waste_tables", "update_registry", "main"]


def _ch_query(sql: str) -> str:
    from zephyr.data.ch_config import ensure_ch_env_loaded
    from zephyr.shared.security.secrets import get_secret_or_default

    ensure_ch_env_loaded()
    host = get_secret_or_default("CLICKHOUSE_HOST", "")
    port = int(get_secret_or_default("CLICKHOUSE_HTTP_PORT", "8123"))
    user = get_secret_or_default("CLICKHOUSE_USER", "default")
    pwd = get_secret_or_default("CLICKHOUSE_PASSWORD", "")
    conn = http.client.HTTPConnection(host, port, timeout=60)
    conn.request("POST", "/", body=sql, headers={"X-ClickHouse-User": user, "X-ClickHouse-Key": pwd})
    r = conn.getresponse()
    data = r.read().decode("utf-8", "replace")
    conn.close()
    if r.status != 200:
        raise RuntimeError(f"CH {r.status}: {data[:200]}")
    return data


def scan_waste_tables() -> list[dict]:
    """扫 system.tables 命中废表名字族的表（只读）。"""
    out = []
    for line in _ch_query(
        "SELECT database, name, total_rows FROM system.tables "
        "WHERE database NOT IN ('system','INFORMATION_SCHEMA','information_schema') FORMAT TSV"
    ).splitlines():
        parts_ = line.split("\t")
        if len(parts_) != 3:
            continue
        db, name, rows = parts_
        if name in EXEMPT:
            continue
        if any(p.match(name) for p in WASTE_PATTERNS):
            out.append({"table": f"{db}.{name}", "total_rows": int(rows) if rows else 0})
    return sorted(out, key=lambda x: x["table"])


def _load_registry() -> dict:
    if REGISTRY_FILE.exists():
        with open(REGISTRY_FILE, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {"entries": []}


def update_registry(found: list[dict], discovered_by: str = "manual") -> dict:
    """登记册对账：新表登记+报警；已知表刷 last_seen。永不删除条目。"""
    reg = _load_registry()
    reg.setdefault("entries", [])
    known = {e["table"]: e for e in reg["entries"]}
    new_items: list[dict] = []
    today = date.today().isoformat()
    for item in found:
        t = item["table"]
        if t in known:
            known[t]["last_seen"] = today
            continue
        entry = {
            "table": t,
            "discovered": today,
            "discovered_by": discovered_by,
            "total_rows_at_discovery": item["total_rows"],
            "status": "待人工盘点",  # 只登记+报警，处置动作一律等 Owner
            "last_seen": today,
        }
        reg["entries"].append(entry)
        new_items.append(entry)
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(reg, f, allow_unicode=True, sort_keys=False)
    return {"new": new_items, "total_known": len(reg["entries"])}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="废表扫描登记器（只登记+报警，永不自动删）")
    parser.add_argument("--json", action="store_true", help="机读 JSON 输出")
    parser.add_argument("--discovered-by", default="manual")
    args = parser.parse_args(argv)

    found = scan_waste_tables()
    res = update_registry(found, discovered_by=args.discovered_by)
    report = {
        "scanned_at": date.today().isoformat(),
        "found": found,
        "new_registrations": [e["table"] for e in res["new"]],
        "total_known": res["total_known"],
        "alerts": [f"[WASTE-TABLE][待人工盘点] {e['table']} ({e['total_rows_at_discovery']} 行)" for e in res["new"]],
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=1))
    else:
        for a in report["alerts"]:
            print(f"⚠ {a}")
        print(f"扫描完成：命中 {len(found)} 张，新登记 {len(res['new'])} 张，册内共 {res['total_known']} 张")
    return 0


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  巡检型工具按裁定#380①由人工/备份事件链触发（backup.ps1 4b 同窗可挂），永不自动删
    raise SystemExit(main())
