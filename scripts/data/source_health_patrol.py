# [BLUEPRINT] MOD-AUTO-L1-001 | docs/_working/automation/campaign/blueprints/onboard_source_blueprint.md | §巡检（WO-③-04）
# [PROVISIONAL] 暂编号：docs/03_modules 解冻后按注册表重编（挂单 H-01）
# [MODULE] scripts.data.source_health_patrol
# [DOMAIN] D_DATA
# [DEPENDENCIES] scripts.data.onboard_source; zephyr.data.alerter; zephyr.shared.utils.time_utils
# [CONSUMERS] Owner/AI 会话（晨间健康打卡）; 未来周期挂点（Windows 计划任务路线，先例=run_nightly_sentiment）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只读对账零落库（verify=count+max(trade_date)+schtasks /query）;
#   CH 断连→全卡 degraded 单条 WARN，不炸不刷屏;
#   卡级 FAIL 走 Alerter 正门（MOD-L00-004，ERROR 级写失败汇总文件）;
#   报告按日落 data/source_health_patrol/<YYYYMMDD>.json; 测试经参数注入 fake+tmp_path（宪法 §9.6）
# [MODIFY-GUARD] 源卡片驱动——巡检器零源特定分支；新源=新 config/source_cards/*.yaml 自动纳入
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单卡异常→该卡 FAIL 不炸批; 告警失败→log 吞掉（Alerter 不抛契约）; 报告写失败→exit 3 fail-visible
# [TESTS] tests/data/test_source_health_patrol.py
# [A_module] module_id=MOD-AUTO-L1-001 | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""source_health_patrol — 数据源健康度周期巡检器（WO-③-04）。

对 config/source_cards/*.yaml 全卡跑 onboard_source.verify 只读对账（行数+最新日+任务态），
汇总 PASS/FAIL/DEGRADED，报告落 data/source_health_patrol/<YYYYMMDD>.json；
卡级 FAIL 走 src/zephyr/data/alerter.py 正门告警（ERROR，写失败汇总文件），
CH 断连（全卡 error）→整体 degraded 单条 WARN，不炸、exit 0（基础设施故障非数据故障）。

零网安全：verify 本身只读对账，零落库零回补；巡检器自身零写 CH。

用法（仓库根，Python 3.12）：
    python scripts/data/source_health_patrol.py
    python scripts/data/source_health_patrol.py --cards-dir config/source_cards --report-dir data/source_health_patrol
    python scripts/data/source_health_patrol.py --no-alert   # 只出报告不告警
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  SSOT：仓库根常量唯一真源
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402  RULE-SCHEMA-TZ：禁 datetime.now()

import onboard_source as ob  # noqa: E402  可编程接口复用：load_card+verify（函数调用，非子进程）

DEFAULT_CARDS_DIR = REPO_ROOT / "config" / "source_cards"
DEFAULT_REPORT_DIR = REPO_ROOT / "data" / "source_health_patrol"

# noqa: m11-perm-manual-legitimate  M11豁免: 操作员/晨间打卡调用的只读巡检器，非高频自动触发常驻服务

TASK_ID = "source_health_patrol"
EXIT_OK = 0       # 全 PASS 或整体 degraded（CH 断连不炸）
EXIT_FAIL = 1     # 存在卡级 FAIL（数据故障）


def patrol(
    cards_dir: str | Path = DEFAULT_CARDS_DIR,
    *,
    verify_fn=None,
    alert_fn=None,
) -> dict:
    """对目录内全卡跑 verify 只读对账，返回报告 dict（不落盘不告警）。

    Args:
        cards_dir: 源卡片目录。
        verify_fn: 注入点（测试 fake）；默认 ob.verify。
        alert_fn: 注入点，签名 (task_id, error, level, source, extra)；测试收集断言。

    状态判定：verify 载荷带 error → 连接级故障（全卡皆 error=CH 断连→整体 degraded；
    个别卡 error=该卡 FAIL）；rows==0 → FAIL（空表）；否则 PASS。
    """
    verify_fn = verify_fn or ob.verify
    directory = Path(cards_dir)
    now = now_utc()
    cards: list[dict] = []
    for path in sorted(directory.glob("*.yaml")):
        entry: dict = {"card": path.name}
        try:
            card = ob.load_card(path)
            entry["source_id"] = str(card.get("source_id", ""))
        except Exception as exc:  # noqa: BLE001 — 单卡异常不炸批（卡片劣质=数据故障 FAIL）
            entry.update(status="fail", detail={"error": f"{type(exc).__name__}: {exc}"})
            cards.append(entry)
            continue
        try:
            result = verify_fn(card)
        except Exception as exc:  # noqa: BLE001 — verify 抛异常按卡级故障记，不炸批
            result = {"error": f"{type(exc).__name__}: {exc}"}
        if "error" in result:
            entry.update(status="error", detail=result)
        elif int(result.get("rows", 0)) == 0:
            entry.update(status="fail", detail={"reason": "空表（rows=0）", **result})
        else:
            entry.update(status="pass", detail=result)
        cards.append(entry)

    errored = [c for c in cards if c["status"] == "error"]
    if cards and len(errored) == len(cards):
        overall = "degraded"  # CH 断连签名：全卡 error
    elif any(c["status"] in ("fail", "error") for c in cards):
        overall = "fail"
    else:
        overall = "pass"
    return {
        "date": now.strftime("%Y-%m-%d"),
        "generated_at": now.isoformat(timespec="seconds"),
        "overall": overall,
        "total": len(cards),
        "pass": sum(1 for c in cards if c["status"] == "pass"),
        "fail": sum(1 for c in cards if c["status"] == "fail"),
        "degraded_cards": len(errored),
        "cards": cards,
    }


def alert(report: dict, alert_fn=None) -> None:
    """按报告结论走 Alerter 正门（MOD-L00-004）：FAIL 卡=ERROR 逐卡；degraded=单条 WARN。"""
    if alert_fn is None:
        from zephyr.data.alerter import Alerter

        alerter = Alerter()

        def alert_fn(task_id, error, level, source=None, extra=None):  # noqa: W7206 哨兵闭包
            alerter.notify(task_id, error, level=level, source=source, extra=extra)

    if report["overall"] == "degraded":
        # CH 断连：只发单条 WARN，不逐卡刷 ERROR（基础设施故障非数据故障）
        alert_fn(TASK_ID, f"源健康巡检 DEGRADED: 全卡 {report['total']} 卡 verify 失败（CH 断连嫌疑）",
                 "WARN", source="clickhouse", extra={"date": report["date"]})
        return
    for c in report["cards"]:
        if c["status"] in ("fail", "error"):
            alert_fn(TASK_ID, f"源健康巡检 FAIL: {c['card']} {c['detail']}",
                     "ERROR", source=c.get("source_id") or c["card"], extra=c["detail"])


def write_report(report: dict, report_dir: str | Path = DEFAULT_REPORT_DIR) -> Path:
    """报告按日落 <YYYYMMDD>.json（新文件无并发争用，非热注册表）。"""
    directory = Path(report_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{now_utc().strftime('%Y%m%d')}.json"
    import json

    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description="数据源健康度周期巡检器（verify 只读对账→报告→告警）")
    ap.add_argument("--cards-dir", default=str(DEFAULT_CARDS_DIR),
                    help="源卡片目录（默认 config/source_cards）")
    ap.add_argument("--report-dir", default=str(DEFAULT_REPORT_DIR),
                    help="报告输出目录（默认 data/source_health_patrol）")
    ap.add_argument("--no-alert", action="store_true", help="只出报告，不走 Alerter 告警")
    args = ap.parse_args()

    report = patrol(args.cards_dir)
    try:
        path = write_report(report, args.report_dir)
    except Exception as exc:  # noqa: BLE001 — fail-visible：报告落盘失败必须露出
        print(f"报告写盘失败: {exc}", file=sys.stderr)
        return 3
    print(f"[patrol] overall={report['overall']} pass={report['pass']}/{report['total']} "
          f"report={path}")
    for c in report["cards"]:
        mark = {"pass": "PASS", "fail": "FAIL", "error": "ERR "}[c["status"]]
        print(f"  [{mark}] {c['card']} {c['detail'].get('error') or c['detail'].get('reason') or ''}")
    if not args.no_alert:
        alert(report)
    return EXIT_OK if report["overall"] in ("pass", "degraded") else EXIT_FAIL


if __name__ == "__main__":
    raise SystemExit(main())
