# [BLUEPRINT] MOD-AUTO-L1-001 | docs/_working/automation/campaign/blueprints/onboard_source_blueprint.md | §编排
# [PROVISIONAL] 暂编号：docs/03_modules 解冻后按注册表重编（挂单 H-01）
# [MODULE] scripts.data.onboard_source
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.data.ch_reader; zephyr.shared.infra.process_pool; yaml
# [CONSUMERS] Owner/AI 会话（一条命令上架新免费源）; docs/_working/automation/campaign/CAMPAIGN_LEDGER.md
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 源卡片驱动（config/source_cards/*.yaml）——新源=新卡片，编排器零改动;
#   probe 零落库；apply 幂等（DDL IF NOT EXISTS+ReplacingMergeTree 重放）;
#   排班走 Windows 任务路线（standalone 脚本正门先例=run_nightly_sentiment）;
#   provider 正门路由（tasks.yaml 绑定）=L1.1 块未挖干不硬做
# [MODIFY-GUARD] 源卡片驱动——新源=新 config/source_cards/*.yaml，禁在本编排器加源特定分支
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 卡片缺失/字段缺失=KeyError 上抛; CH 不可达→异常上抛（fail-visible）
# [TESTS] tests/data/test_onboard_source.py
# [A_module] module_id=MOD-AUTO-L1-001 | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""onboard_source — 数据源上架流水线编排器（骨架 §1 工段③ v0）。

一条命令上架一个免费数据源：probe（沙箱试拉零落库）→ apply（DDL 建表+首批回补+Windows 任务登记）
→ verify（行数+最新日期+任务状态）。源卡片=config/source_cards/*.yaml，新源=新卡片。

用法（仓库根，Python 3.12）：
    python scripts/data/onboard_source.py --card config/source_cards/fx_ecb.yaml --mode probe
    python scripts/data/onboard_source.py --card config/source_cards/fx_ecb.yaml --mode apply
    python scripts/data/onboard_source.py --card config/source_cards/fx_ecb.yaml --mode verify

批量模式（WO-③-03，--card/--cards-dir 二选一）：对目录内 *.yaml 逐卡跑同一 mode，
单卡失败不炸批，末尾打印汇总表（card/mode/result/reason）：
    python scripts/data/onboard_source.py --cards-dir config/source_cards --mode verify
"""
from __future__ import annotations

import argparse
import importlib
import json
from zephyr.shared.infra.process_pool import run_subprocess_hidden
import sys
from pathlib import Path

import yaml

# noqa: m11-perm-manual-legitimate  M11豁免: 操作员按需调用的上架编排器（每源一次性工单工具），非自动触发常驻服务

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  SSOT：仓库根常量唯一真源

REQUIRED_FIELDS = ("source_id", "schema_module", "table", "ingest_script", "task_name", "schedule")

# NO-BARE-SQL §5.160.2：SQL 集中化为模块级常量（表名为唯一变量位）
_LATEST_TRADE_DATE_SQL = "SELECT max(trade_date) FROM {table}"  # noqa: bare-sql  表名逐卡片动态代入，无法机械集中化为固定常量


def load_card(path: str | Path) -> dict:
    # MSG-EXPOSURE 铁律：消息文本只留人类可读摘要，路径走 details 结构化字段
    def _fail(exc_type: type, msg: str) -> Exception:
        exc = exc_type(msg)
        exc.details = {"path": str(path)}  # type: ignore[attr-defined]
        return exc

    card = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(card, dict):
        raise _fail(ValueError, "源卡片不是映射")
    missing = [f for f in REQUIRED_FIELDS if f not in card]
    if missing:
        raise _fail(KeyError, f"源卡片缺必备字段 {missing}")
    sched = card.get("schedule") or {}
    for k in ("type", "days", "time"):
        if k not in sched:
            raise _fail(KeyError, f"源卡片 schedule 缺 {k}")
    return card


def deploy_schema(schema_module: str) -> str:
    """导入 DDL 模块→ensure_database+建表（IF NOT EXISTS 幂等）。返回表名。"""
    from zephyr.data.ch_writer import ensure_database, query

    mod = importlib.import_module(schema_module)
    table = str(mod.TABLE_NAME)
    database = table.split(".")[0]
    ensure_database(database)
    ddl_key = next(k for k in dir(mod) if k.endswith("_DDL"))
    query(getattr(mod, ddl_key))
    return table


def build_task_cmd(card: dict) -> list[str]:
    """schtasks /tr 参数（纯函数，测试直喷）。"""
    ingest = str(REPO_ROOT / card["ingest_script"])
    args = card.get("ingest_args", "")
    return [
        "schtasks", "/create", "/tn", card["task_name"], "/f",
        "/tr", f'"{sys.executable}" "{ingest}" {args}'.strip(),
        "/sc", str(card["schedule"]["type"]),
        "/d", ",".join(str(d) for d in card["schedule"]["days"]),
        "/st", str(card["schedule"]["time"]),
    ]


def run_ingest(card: dict, extra_args: str = "") -> int:
    script = str(REPO_ROOT / card["ingest_script"])
    cmd = [sys.executable, script]
    if extra_args:
        cmd.extend(extra_args.split())
    else:
        cmd.extend(card.get("ingest_args", "").split())
    return run_subprocess_hidden(cmd, cwd=str(REPO_ROOT)).returncode


def verify(card: dict) -> dict:
    from zephyr.data.ch_reader import count, query

    table = card["table"]
    try:
        rows = int(count(table))
        latest = (query(_LATEST_TRADE_DATE_SQL.format(table=table)) or "").strip() or None
    except Exception as exc:  # noqa: BLE001 — fail-visible：CH 故障不得伪装成"空表"
        return {"table": table, "error": f"CH 查询失败: {exc}"}
    task_state = "unknown"
    try:
        out = run_subprocess_hidden(
            ["schtasks", "/query", "/tn", card["task_name"], "/fo", "LIST"],
            capture_output=True, timeout=30, encoding="gbk", errors="replace",
        )
        for line in (out.stdout or "").splitlines():
            if "Status" in line or "状态" in line:
                task_state = line.split(":", 1)[1].strip()
                break
    except Exception:  # noqa: BLE001 — 任务查询失败不阻断数据核验
        pass
    return {"table": table, "rows": int(rows), "latest_date": latest, "task_state": task_state}


def run_mode(card: dict, mode: str) -> tuple[int, dict]:
    """对已加载卡片执行单模式流水线。返回 (exit_code, 末段 JSON 载荷)。

    中间产物（DDL 确认/回补+任务登记结果）原样 print，保持单卡 stdout 契约不变。
    """
    if mode == "probe":
        rc = run_ingest(card, f"--probe --days {card.get('probe_days', 2)}")
        return rc, {"mode": "probe", "ingest_exit": rc}

    if mode == "apply":
        table = deploy_schema(card["schema_module"])
        print(json.dumps({"ddl_ok": True, "table": table}, ensure_ascii=False))
        rc = run_ingest(card, f"--days {card.get('backfill_days', 7)}")
        if rc != 0:
            # 回补失败不挂任务——避免留下"每晚注定失败"的僵尸班次
            return 2, {"backfill_exit": rc, "task_registered": False,
                       "reason": "backfill 失败，不登记定时任务"}
        cmd = build_task_cmd(card)
        task = run_subprocess_hidden(cmd, capture_output=True, text=True)
        task_ok = task.returncode == 0
        if not task_ok:
            return 2, {"backfill_exit": rc, "task_registered": False,
                       "task_err": (task.stderr or "")[-200:]}
        print(json.dumps({"backfill_exit": rc, "task_registered": True, "task_err": ""},
                         ensure_ascii=False))
        info = verify(card)
        return 0, {"mode": "apply", **info}

    return 0, {"mode": "verify", **verify(card)}


def run_batch(cards_dir: str | Path, mode: str) -> int:
    """批量模式：目录内 *.yaml 逐卡跑同一 mode（单卡失败不炸批）。

    返回汇总 exit code：全 ok=0；存在 fail=1；目录无卡片=2。
    末尾打印汇总表（card/mode/result/reason），verify 模式下 payload 带 error 键
    也判 fail（fail-visible：CH 故障不得伪装成成功）。
    """
    directory = Path(cards_dir)
    cards = sorted(directory.glob("*.yaml"))
    if not cards:
        print(json.dumps({"batch_error": f"目录无 *.yaml 卡片: {directory}"},
                         ensure_ascii=False))
        return 2
    rows: list[dict] = []
    for path in cards:
        rec: dict = {"card": path.name, "mode": mode}
        try:
            card = load_card(path)
            rc, payload = run_mode(card, mode)
            rec["result"] = "ok"
            rec["reason"] = ""
            if rc != 0 or "error" in payload:
                rec["result"] = "fail"
                rec["reason"] = str(payload.get("error") or payload.get("reason")
                                    or json.dumps(payload, ensure_ascii=False))
            elif mode == "verify":
                rec["reason"] = (f"rows={payload.get('rows')} "
                                 f"latest={payload.get('latest_date')} "
                                 f"task={payload.get('task_state')}")
        except Exception as exc:  # noqa: BLE001 — 批量模式单卡失败不炸批（工单 WO-③-03）
            rec["result"] = "fail"
            rec["reason"] = f"{type(exc).__name__}: {exc}"
        rows.append(rec)
    width = max((len(r["card"]) for r in rows), default=4)
    print("\n--- 批量汇总 ---")
    print(f"{'card'.ljust(width)}  mode    result  reason")
    for r in rows:
        print(f"{r['card'].ljust(width)}  {r['mode']:<6}  {r['result']:<6}  {r['reason']}")
    failed = sum(1 for r in rows if r["result"] == "fail")
    print(json.dumps({"batch_summary": {"total": len(rows), "ok": len(rows) - failed,
                                        "fail": failed, "mode": mode}},
                     ensure_ascii=False))
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="数据源上架流水线编排器（probe/apply/verify，单卡或批量）")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--card", help="源卡片路径 config/source_cards/*.yaml")
    group.add_argument("--cards-dir", help="批量模式：卡片目录，对其中 *.yaml 逐卡跑同一 --mode")
    ap.add_argument("--mode", choices=["probe", "apply", "verify"], required=True)
    args = ap.parse_args()

    if args.cards_dir:
        return run_batch(args.cards_dir, args.mode)

    card = load_card(args.card)
    rc, payload = run_mode(card, args.mode)
    print(json.dumps(payload, ensure_ascii=False))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
