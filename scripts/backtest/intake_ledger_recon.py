# [BLUEPRINT] MOD-BT-231 | docs/03_modules/_domain_backtest/blueprint.md | §E1 进货台账对账与蒸发重建
# [MODULE] scripts.backtest.intake_ledger_recon
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pandas; clickhouse-driver(经 zephyr.data.ch_writer 通道);
#   zephyr.shared.io.file_utils(safe_write_text/content_sha256);
#   scripts.backtest.lane_b_idea_generator(make_candidate_id)
# [CONSUMERS] 策略生产全景图 FAC-E1 进货→E2 前置对账（hypothesis_precheck.run 调 preflight）；
#   人工/夜批 CLI（check/rebuild）；tests/backtest/test_intake_ledger_recon.py
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 台账只追加不误删——rebuild 只 append CH 实证缺失行，绝不重写/删除既有行；
#   重建数据源唯一=c1_backtest.hypothesis_precheck（判定台账携带假说原文+出生证），
#   禁凭记忆手填；车道 B 重建前必过内容寻址校验（candidate_id 等于 E1B 前缀加假说全文的
#   md5_12），校验不过者拒绝入账并单独报出；台账追加写必经 safe_write_text（CAS 防并发覆盖，
#   根宪法 §1 条目13），本模块 append_ledger_rows 是 E1 卸货与重建的唯一写口；
#   CH 不可达=probe_failed 显式报红，禁静默归零判全绿
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(台账缺列/未知车道/台账不存在); StaleWriteRefused(CAS base 漂移拒写)
# [TESTS] tests/backtest/test_intake_ledger_recon.py
# [A_module] module_id=MOD-BT-231 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  手动 CLI 对账器非常驻服务：E2 预审前置内联调用 + 人工/夜批触发，无常驻循环
# create-guard-not-dup: 本模块是 FAC-E1 进货台账↔CH 判定台账的领域对账校验器（check/rebuild/preflight 与唯一 CAS 追加写口），非 gov_enforcement 门禁引擎参考检查器的第二实现——关键词命中仅因 id/校验类泛词撞车
"""FAC-E1 进货台账 ↔ CH 判定台账对账校验器与蒸发重建器（F16 治本，图9 FAC-E1/E2 断点）。

背景（09-26/27 事故实证，案卷 b_factory_inbound/04_f16 卷缺口1）：车道 B 09-16 班 11 条
候选卸货后蒸发——进货台账 lane_b_candidates.csv 只剩 4 行（mtime 停在 09-16 02:33），而 CH
判定台账 c1_backtest.hypothesis_precheck 的批 E2-20260916-021246 完整留存 11 行（含假说原文
与出生证）。台账蒸发零告警，直到下游 E3 取不到货才被发现。本模块补三刀：

1. **对账 check/preflight**：按车道表驱动比对 csv 唯一 id 集与 CH 唯一 id 集，报出
   missing_in_csv（蒸发=事故态）/missing_in_ch（未审=正常态）/dup_ids/内容寻址校验失败；
   有漂移即 status=drift（CLI 退出码 1，可挂夜批与编排前置）。
2. **重建 rebuild**：只从 CH 取实证行 append 回台账（默认预演，--apply 才写），车道 B 行
   先过 make_candidate_id 内容寻址校验；CH 侧不携带的列（theme/mechanism_hint/horizon/
   universe/birth_source）如实留空并在报告 unrecoverable_columns 中声明，不编造。
3. **写入通道**：append_ledger_rows 是本域台账唯一 CAS 追加口（E1 卸货与重建共用）。

E2 前置接线：hypothesis_precheck.run() 每次预审前调 preflight(source)，报告塞进
summary["ledger_recon"]——fail-open 不阻断主链，但 drift/probe_failed 必须显式出声。

用法:
  python scripts/backtest/intake_ledger_recon.py check
  python scripts/backtest/intake_ledger_recon.py check --ledger lane_b_candidates.csv
  python scripts/backtest/intake_ledger_recon.py rebuild --ledger lane_b_candidates.csv
  python scripts/backtest/intake_ledger_recon.py rebuild --ledger lane_b_candidates.csv --apply
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

from zephyr.shared.io.file_utils import DetailsCarryingError

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))  # CLI 直跑场景：schemas.* / scripts.* 在仓库根
_INTAKE_DIR = _ROOT / "data" / "strategy_intake"


class LedgerReconError(DetailsCarryingError):
    """台账对账/重建可预期失败（MSG-EXPOSURE 合规：路径/缺列明细入 details，消息文本零敏感面）。"""


# 进货台账 ↔ 出生车道（表驱动唯一真源，与 E1 各车道卸货路径一致；新增车道改本表）
LEDGER_CHANNELS: dict[str, str] = {
    "lane_b_candidates.csv": "B",
    "three_high_candidates.csv": "D",
    "lane_c_candidates.csv": "C",
    "lane_c2_candidates.csv": "C2",
    "lane_g_candidates.csv": "G",
    "lane_chain_candidates.csv": "I",
}

# 内容寻址可校验车道 → E1 前缀（candidate_id = CAND-md5_12("<前缀>:假说全文")）
CONTENT_ADDRESSED_PREFIX: dict[str, str] = {"B": "E1B"}

STATUS_OK = "ok"
STATUS_DRIFT = "drift"
STATUS_PROBE_FAILED = "probe_failed"
STATUS_UNKNOWN_LEDGER = "unknown_ledger"
STATUS_LEDGER_ABSENT = "ledger_absent"

SQL_CH_LEDGER = "SELECT DISTINCT candidate_id, birth_channel, birth_batch, hypothesis_zh FROM {table}"

# CH 判定行携带的列（重建只填这些；其余列如实留空并报告，禁编造出生证之外的字段）
REBUILD_SOURCE_COLS = ("candidate_id", "hypothesis_zh", "birth_channel", "birth_batch")


def _dir(intake_dir: Path | str | None) -> Path:
    """台账目录解析（注入=测试/离线预演用，缺省=生产 data/strategy_intake）。"""
    return Path(intake_dir) if intake_dir else _INTAKE_DIR


def _table() -> str:
    """判定台账全限定表名（SSOT=DDL-as-Code 常量，与 E2 同通道）。"""
    from schemas.categories.backtest.backtest_hypothesis_precheck import DATABASE, TABLE_NAME

    return f"{DATABASE}.{TABLE_NAME}"


def fetch_ch_index(channels: list[str] | None = None) -> list[dict]:
    """CH 判定台账唯一 (candidate_id, 车道, 出生批次, 假说) 索引（对账/重建唯一数据源）。

    Raises:
        Exception: CH 不可达原样上抛——由调用方显式记 probe_failed（禁静默归零）。
    """
    from zephyr.data.ch_writer import get_client_strict

    rows = get_client_strict().execute(SQL_CH_LEDGER.format(table=_table()))
    out = [
        {
            "candidate_id": str(r[0]),
            "birth_channel": str(r[1]),
            "birth_batch": str(r[2]),
            "hypothesis_zh": str(r[3]),
        }
        for r in rows
    ]
    if channels:
        want = set(channels)
        out = [r for r in out if r["birth_channel"] in want]
    return out


def load_ledger(path: Path) -> pd.DataFrame:
    """进货台账读取（缺列即报错——宁报错不猜列）。"""
    if not path.exists():
        raise LedgerReconError("进货台账不存在", details={"path": str(path)})
    df = pd.read_csv(path, encoding="utf-8-sig")
    missing = {"candidate_id", "hypothesis_zh"} - set(df.columns)
    if missing:
        raise LedgerReconError("进货台账缺必需列", details={"missing_columns": sorted(missing), "path": str(path)})
    return df


def make_id_checker(channel: str) -> Callable[[str], str] | None:
    """按车道取内容寻址校验函数（不可校验车道返回 None=该项校验跳过）。"""
    if channel not in CONTENT_ADDRESSED_PREFIX:
        return None
    from scripts.backtest.lane_b_idea_generator import make_candidate_id  # id 派生唯一真源

    return make_candidate_id


def id_integrity_failures(df: pd.DataFrame, channel: str) -> list[str]:
    """内容寻址校验：candidate_id 必须等于 md5(<E1 前缀>:假说全文)（仅可校验车道生效）。"""
    check = make_id_checker(channel)
    if check is None:
        return []
    bad = {
        str(cid)
        for cid, hyp in zip(df["candidate_id"], df["hypothesis_zh"], strict=False)
        if check(str(hyp)) != str(cid)
    }
    return sorted(bad)


def duplicate_ids(df: pd.DataFrame) -> list[str]:
    """台账内重复 id（跨批重复入账=E1 去重失效）。"""
    s = df["candidate_id"].astype(str)
    return sorted({x for x in s[s.duplicated(keep=False)].tolist()})


def render_csv_block(rows: list[dict], header: list[str], *, with_header: bool) -> str:
    """按台账表头渲染 CSV 文本块（LF 行尾、UTF-8 无 BOM——与既有台账同口径）。"""
    buf = io.StringIO()
    pd.DataFrame(rows, columns=header).to_csv(buf, index=False, header=with_header, lineterminator="\n")
    return buf.getvalue()


def append_ledger_rows(path: Path, rows: list[dict], header: list[str]) -> dict:
    """台账追加写唯一 CAS 通道（根宪法 §1 条目13：禁裸 mode="a" 直写）。

    只追加不重写：基文原样保留（含 BOM）+ 渲染块尾接；写盘走 safe_write_text
    （base 校验→原子写→回读校验→审计）。base 与磁盘不符即 StaleWriteRefused 上抛，
    由调用方决定重试——绝不静默覆盖他人/他会话刚写入的行。
    """
    from zephyr.shared.io.file_utils import content_sha256, safe_write_text

    base_text = path.read_text(encoding="utf-8") if path.exists() else ""
    block = render_csv_block(rows, header, with_header=not base_text)
    if base_text and not base_text.endswith("\n"):
        block = "\n" + block
    res = safe_write_text(path, base_text + block, expected_base_sha256=content_sha256(base_text), newline="")
    return {"rows": len(rows), "before_sha256": res.before_sha256, "after_sha256": res.after_sha256}


def reconcile_one(ledger_name: str, ch_index: list[dict], *, intake_dir: Path | str | None = None) -> dict:
    """单台账对账（纯计算：ch_index 由调用方供给，零网络，可喂样本做红样）。"""
    channel = LEDGER_CHANNELS[ledger_name]
    path = _dir(intake_dir) / ledger_name
    if not path.exists():
        return {
            "ledger": ledger_name,
            "channel": channel,
            "status": STATUS_DRIFT,
            "reason": "台账文件缺失",
            "missing_in_csv": [],
            "missing_in_ch": [],
            "dup_ids": [],
            "id_integrity_failures": [],
        }
    df = load_ledger(path)
    csv_ids = set(df["candidate_id"].astype(str))
    ch_ids = {str(r["candidate_id"]) for r in ch_index if r["birth_channel"] == channel}
    missing_in_csv = sorted(ch_ids - csv_ids)
    report = {
        "ledger": ledger_name,
        "channel": channel,
        "csv_rows": int(len(df)),
        "csv_unique_ids": int(len(csv_ids)),
        "ch_unique_ids": int(len(ch_ids)),
        "missing_in_csv": missing_in_csv,
        "missing_in_ch": sorted(csv_ids - ch_ids),
        "dup_ids": duplicate_ids(df),
        "id_integrity_failures": id_integrity_failures(df, channel),
    }
    report["status"] = (
        STATUS_OK if not (missing_in_csv or report["dup_ids"] or report["id_integrity_failures"]) else STATUS_DRIFT
    )
    return report


def check_all(
    ledgers: list[str] | None = None,
    *,
    ch_index: list[dict] | None = None,
    intake_dir: Path | str | None = None,
) -> dict:
    """全量/指定台账对账（ch_index/intake_dir 注入=测试与离线预演用）。"""
    names = ledgers or list(LEDGER_CHANNELS)
    unknown = [n for n in names if n not in LEDGER_CHANNELS]
    if unknown:
        raise LedgerReconError("未知台账（不在 LEDGER_CHANNELS 表内）", details={"unknown_ledgers": unknown})
    if ch_index is None:
        try:
            ch_index = fetch_ch_index()
        except Exception as exc:  # noqa: BLE001 — 探针失败必须报红，不得降级为"全绿"
            return {"status": STATUS_PROBE_FAILED, "error": f"{type(exc).__name__}: {exc}"[:200], "ledgers": []}
    reports = [reconcile_one(n, ch_index, intake_dir=intake_dir) for n in names]
    drifted = [r for r in reports if r["status"] != STATUS_OK]
    return {
        "status": STATUS_OK if not drifted else STATUS_DRIFT,
        "checked_at": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds"),
        "ledgers": reports,
        "drift_ledgers": [r["ledger"] for r in drifted],
    }


def preflight(source: str | Path, *, intake_dir: Path | str | None = None, ch_index: list[dict] | None = None) -> dict:
    """E2 前置对账入口（fail-open：不抛异常，只出声报告）。

    Args:
        source: E2 本次预审的进货台账（路径或文件名，按车道表判定）。
        intake_dir: 台账目录注入（测试/离线预演用）。
        ch_index: CH 判定索引注入（缺省=现查 CH）。

    Returns:
        {status, ...} — status ∈ ok/drift/probe_failed/unknown_ledger/ledger_absent。
    """
    name = Path(source).name
    if name not in LEDGER_CHANNELS:
        return {"status": STATUS_UNKNOWN_LEDGER, "ledger": str(source), "reason": "不在车道表内，跳过对账"}
    if not _dir(intake_dir).joinpath(name).exists():
        return {"status": STATUS_LEDGER_ABSENT, "ledger": name, "reason": "台账文件不存在"}
    report = check_all([name], ch_index=ch_index, intake_dir=intake_dir)
    if report["status"] == STATUS_PROBE_FAILED:
        return {"status": STATUS_PROBE_FAILED, "ledger": name, "error": report.get("error", "")}
    inner = report["ledgers"][0] if report["ledgers"] else {}
    return {
        "status": inner.get("status", report["status"]),
        "ledger": name,
        "missing_in_csv": len(inner.get("missing_in_csv", [])),
        "missing_in_ch": len(inner.get("missing_in_ch", [])),
        "id_integrity_failures": inner.get("id_integrity_failures", []),
        "detail": inner,
    }


def plan_rebuild(
    ledger_name: str,
    ch_index: list[dict],
    *,
    birth_batch: str | None = None,
    intake_dir: Path | str | None = None,
) -> dict:
    """重建计划（纯计算，零写盘）：CH 实证行 → 台账缺失行 + 拒绝入账行。"""
    if ledger_name not in LEDGER_CHANNELS:
        raise LedgerReconError("未知台账（不在 LEDGER_CHANNELS 表内）", details={"ledger": ledger_name})
    channel = LEDGER_CHANNELS[ledger_name]
    path = _dir(intake_dir) / ledger_name
    df = load_ledger(path)  # 不存在/缺列即 LedgerReconError（含 details.path），不在此重复判据
    header = list(df.columns)
    csv_ids = set(df["candidate_id"].astype(str))
    rows = [r for r in ch_index if str(r["birth_channel"]) == channel]
    if birth_batch:
        rows = [r for r in rows if str(r["birth_batch"]) == birth_batch]
    check = make_id_checker(channel)
    seen: set[str] = set()
    rebuilt: list[dict] = []
    refused: list[dict] = []
    for r in sorted(rows, key=lambda x: (str(x["birth_batch"]), str(x["candidate_id"]))):
        cid = str(r["candidate_id"])
        if cid in csv_ids or cid in seen:
            continue
        seen.add(cid)
        if check is not None and check(str(r["hypothesis_zh"])) != cid:
            refused.append({"candidate_id": cid, "reason": "内容寻址校验不过（CH 行 id 与假说原文不符）"})
            continue
        row = {c: "" for c in header}
        row.update({k: r[k] for k in REBUILD_SOURCE_COLS if k in r})
        rebuilt.append(row)
    return {
        "ledger": ledger_name,
        "channel": channel,
        "header": header,
        "rows": rebuilt,
        "refused": refused,
        "unrecoverable_columns": [c for c in header if c not in REBUILD_SOURCE_COLS],
    }


def rebuild_missing(
    ledger_name: str,
    birth_batch: str | None = None,
    apply: bool = False,
    *,
    ch_index: list[dict] | None = None,
    intake_dir: Path | str | None = None,
) -> dict:
    """从 CH 实证重建台账蒸发行（只 append；apply=False 即预演不落盘）。"""
    if ledger_name not in LEDGER_CHANNELS:
        raise RuntimeError(f"未知台账（不在 LEDGER_CHANNELS 表内）: {ledger_name}")
    if ch_index is None:
        ch_index = fetch_ch_index([LEDGER_CHANNELS[ledger_name]])
    plan = plan_rebuild(ledger_name, ch_index, birth_batch=birth_batch, intake_dir=intake_dir)
    result = {
        "ledger": ledger_name,
        "channel": plan["channel"],
        "rebuild_candidates": len(plan["rows"]),
        "rebuilt": [r["candidate_id"] for r in plan["rows"]],
        "refused": plan["refused"],
        "unrecoverable_columns": plan["unrecoverable_columns"],
        "applied": False,
    }
    if not apply or not plan["rows"]:
        return result
    written = append_ledger_rows(_dir(intake_dir) / ledger_name, plan["rows"], plan["header"])
    result.update({"applied": True, "written_rows": written["rows"], "cas": written})
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="FAC-E1 进货台账↔CH 对账校验器与蒸发重建器（只追加/CAS 写）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="台账↔CH 对账（漂移退出码 1）")
    c.add_argument("--ledger", default=None, help="仅查单个台账文件名（缺省=全部车道台账）")
    r = sub.add_parser("rebuild", help="从 CH 实证重建蒸发行（默认预演，--apply 才写盘）")
    r.add_argument("--ledger", required=True)
    r.add_argument("--birth-batch", default=None, help="限定出生批次（如 E1B-20260916-021130）")
    r.add_argument("--apply", action="store_true", help="真写盘（safe_write_text CAS 追加）")
    args = ap.parse_args()

    if args.cmd == "check":
        report = check_all([args.ledger] if args.ledger else None)
        print(json.dumps(report, ensure_ascii=False, indent=1))
        return 0 if report["status"] == STATUS_OK else 1
    result = rebuild_missing(args.ledger, args.birth_batch, apply=args.apply)
    print(json.dumps(result, ensure_ascii=False, indent=1))
    return 0 if not result["refused"] else 1


if __name__ == "__main__":
    sys.exit(main())
