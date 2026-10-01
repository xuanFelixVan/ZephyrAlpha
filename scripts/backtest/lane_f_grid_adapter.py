# [BLUEPRINT] MOD-BT-E1F-001 | docs/03_modules/_domain_backtest/blueprint.md | §FAC-E1 车道F（F-06 组合层网格）
# [PROVISIONAL] 暂编号：E11 环节施工件（st-lanech-20261001），模块注册表重编归总包统一登记
# [MODULE] scripts.backtest.lane_f_grid_adapter
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pandas; yaml(config/position_recipe_grid_schema.yaml 轴描述真源);
#   scripts.backtest.intake_ledger_recon (append_ledger_rows CAS 追加写口)
# [CONSUMERS] factory_intake_pipeline（E1 编排 F 车道函数级接续）；hypothesis_precheck（E2 幂等
#   消费 lane_f_candidates.csv）；上游=data/strategy_intake/grid_*/manifest.csv（F-06 执行器
#   MOD-BT-196 落盘，ZephyrAlpha_F06Grid 计划任务驱动）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 转换是确定性纯函数（同 manifest 行必产出同假说文本，零时钟零随机）；
#   机制字段缺失如实降级标注——grid recipe 是参数网格机械产物、不带机制叙事，本件禁编造机制，
#   假说文本只陈述 recipe 出处+参数轴取值+样本内指标并显式声明机制缺失（判定权在 E2/E4）；
#   轴描述只从 config/position_recipe_grid_schema.yaml desc 真源取（读不到=退回裸轴 id，不造词）；
#   candidate_id=F06-<recipe_id>（recipe_id 本身=sha1(全维取值规范 JSON)[:12] 内容寻址，
#   同参数组合跨批次同 id→幂等天然成立）；台账只追加，写必经 intake_ledger_recon.append_ledger_rows
#   （CAS 防并发覆盖，根宪法 §1 条目13）；出生证（birth_channel/birth_batch/birth_source）
#   由本模块代码机器写入，AI 禁手填；运动员不兼任裁判——manifest 指标是描述性证据不是本件评分
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(台账存在但不可读=fail-closed 防重复卸货); ValueError 不吃——
#   单行 values_json 损坏→skipped_malformed 留痕继续（不抛不冤枉同行）；无批次/空 manifest→诚实空报告
# [TESTS] tests/backtest/test_lane_f_grid_adapter.py
# [A_module] module_id=MOD-BT-E1F-001 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  手动 CLI 适配器非常驻服务：由 E1 进货编排/夜批事件调用，无常驻循环
"""FAC-E1 车道F 适配器——F-06 grid 配方批次 → E2 可审假说候选（销 2026-09-15 挂账欠账）。

背景：F 车道进货活（factory_grid_executor 由 ZephyrAlpha_F06Grid 计划任务驱动，落
data/strategy_intake/grid_*/manifest.csv），但 E2 预审消费断——manifest 行是参数网格
机械产物（recipe_id/prefix_key/values_json/metrics），不符合 E2 台账四列契约
（candidate_id/hypothesis_zh/birth_channel/birth_batch）。本适配器补消费侧最后一公里：

1. 解析最新（或指定）grid 批次 manifest；
2. 确定性转译：每 recipe → 一条假说候选（出处+参数轴+样本内指标+机制缺失如实声明）；
3. 幂等卸台账 lane_f_candidates.csv（同 recipe_id 跳过；E2 侧按 CH 终局集再幂等一层）。

用法:
  python scripts/backtest/lane_f_grid_adapter.py intake                # 最新批次→台账（幂等）
  python scripts/backtest/lane_f_grid_adapter.py intake --manifest data/strategy_intake/grid_20260925-232032/manifest.csv
  python scripts/backtest/lane_f_grid_adapter.py intake --dry-run
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

import pandas as pd

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))  # scripts.* 命名空间导入在 CLI 直跑场景

_INTAKE_CSV = _ROOT / "data" / "strategy_intake" / "lane_f_candidates.csv"
_GRID_BASE = _ROOT / "data" / "strategy_intake"
_AXIS_SCHEMA_YAML = _ROOT / "config" / "position_recipe_grid_schema.yaml"

BIRTH_CHANNEL = "F"
# E2 台账四列契约（hypothesis_precheck.load_candidates 硬校验）+ 溯源/指标留痕列
LEDGER_COLUMNS = (
    "candidate_id",
    "hypothesis_zh",
    "birth_channel",
    "birth_batch",
    "birth_source",
    "recipe_id",
    "prefix_key",
    "degraded_dimensions",
    "sharpe",
    "ann_return",
    "max_drawdown",
    "avg_turnover",
    "net_days",
    "values_json",
)
HONEST_NO_MECHANISM_NOTE = (
    "机制字段缺失如实声明：网格执行器产物不带机制叙事，本转换器不编造机制——"
    "请按参数结构与成本假设档审其可证伪性/成本/边界"
)


def latest_manifest(base: Path | None = None) -> Path | None:
    """最新 grid_<ts>/manifest.csv 解析（无批次=None 诚实缺；排序取尾=字典序即时间序）。"""
    b = base if base is not None else _GRID_BASE
    runs = sorted(b.glob("grid_*/manifest.csv"))
    return runs[-1] if runs else None


def make_candidate_id(recipe_id: str) -> str:
    """候选 id：F06-<recipe_id>。recipe_id=执行器侧 sha1 内容寻址（同参数组合跨批稳定）。"""
    return f"F06-{str(recipe_id).strip()}"


def load_axis_descs(schema_path: Path | None = None) -> dict[str, str]:
    """轴 id→中文描述（schema YAML desc 真源；读不到=空表→转换退回裸轴 id，不造词）。"""
    p = schema_path if schema_path is not None else _AXIS_SCHEMA_YAML
    try:
        import yaml

        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        return {str(d.get("id")): str(d.get("desc", "")).strip() for d in data.get("dimensions", []) if d.get("id")}
    except Exception:  # noqa: BLE001 — 描述缺位 fail-open（假说仍带裸轴 id 可审）
        return {}


def _fmt_metric(v: object) -> str:
    """指标格式化（NaN/None→无；6 位有效数字；布尔按字面）。"""
    if v is None:
        return "无"
    try:
        f = float(v)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return str(v)
    if f != f:  # NaN
        return "无"
    return f"{f:.6g}"


def _parse_degraded(raw: object) -> str:
    """degraded_dimensions 元组字串 → 中文清单（空→无；解析失败退回原文，不编造）。"""
    s = str(raw or "").strip()
    if not s or s == "()":
        return "无"
    try:
        parsed = ast.literal_eval(s)
        if isinstance(parsed, (tuple, list, set)):
            items = [str(x) for x in parsed if str(x).strip()]
            return "、".join(items) if items else "无"
    except (ValueError, SyntaxError):
        pass
    return s


def recipe_to_hypothesis(
    recipe_id: str,
    values: dict,
    prefix_key: str,
    degraded: str,
    metrics: dict,
    batch_tag: str,
    axis_descs: dict[str, str] | None = None,
) -> str:
    """确定性假说文本（同输入必同输出；机制缺失如实声明，禁编造）。

    语义设计（E11 挖矿结论）：grid recipe 是参数网格机械产物，翻译成"可审假说"必须
    带机制描述字段；manifest 无机制字段 → 最小可审假说=如实标注 recipe 出处（批次+id）
    +全参数轴取值（schema desc 真源翻译）+信号侧差异维+降级维+样本内指标观察，并显式
    声明机制缺失不编造——把"是不是数据挖掘巧合"（六问之5）诚实交给 E2 判。
    """
    desc = axis_descs or {}
    axes = "；".join(f"{k}[{desc[k]}]={v}" if desc.get(k) else f"{k}={v}" for k, v in sorted(values.items()))
    if not axes:
        axes = "无参数明细（values_json 缺损）"
    pk = prefix_key if prefix_key else "无"
    m = {
        "sharpe": _fmt_metric(metrics.get("sharpe")),
        "ann_return": _fmt_metric(metrics.get("ann_return")),
        "max_drawdown": _fmt_metric(metrics.get("max_drawdown")),
        "avg_turnover": _fmt_metric(metrics.get("avg_turnover")),
        "net_days": _fmt_metric(metrics.get("net_days")),
    }
    return (
        f"F06组合层参数网格配方（机械网格产物、非独立机制假说；批次 {batch_tag}，"
        f"recipe_id={recipe_id}）。参数轴全量取值：{axes}。"
        f"信号侧差异维(prefix_key)：{pk}。降级维：{_parse_degraded(degraded)}。"
        f"同批样本内回测观察（仅描述性证据，非机制主张）：sharpe={m['sharpe']}；"
        f"年化收益={m['ann_return']}；最大回撤={m['max_drawdown']}；"
        f"日均换手={m['avg_turnover']}；净值天数={m['net_days']}。{HONEST_NO_MECHANISM_NOTE}"
    )


def convert_manifest(manifest: Path | str, axis_descs: dict[str, str] | None = None) -> tuple[list[dict], dict]:
    """manifest → (候选行清单, 转换报告)。纯读函数（零写盘，测试/预演友好）。

    单行 values_json 损坏 → 记 skipped_malformed 继续同行（不抛不冤枉整批）；
    recipe_id 空行跳过；同 manifest 内重复 recipe_id 去重保首行。
    """
    path = Path(manifest)
    batch_tag = path.parent.name
    birth_batch = f"E1F-{batch_tag}"
    try:
        birth_source = str(path.resolve().relative_to(_ROOT)).replace("\\", "/")
    except ValueError:  # manifest 在仓库根外（测试 tmp_path 注入）——用绝对路径如实留痕
        birth_source = str(path)
    df = pd.read_csv(path, encoding="utf-8-sig")
    rows: list[dict] = []
    report: dict = {
        "manifest": str(path),
        "batch": birth_batch,
        "rows_in_manifest": int(len(df)),
        "converted": 0,
        "skipped_malformed": [],
    }
    seen: set[str] = set()
    descs = axis_descs if axis_descs is not None else load_axis_descs()
    for _, r in df.iterrows():
        rid = str(r.get("recipe_id", "") or "").strip()
        if not rid:
            continue
        if rid in seen:
            continue
        try:
            values = json.loads(str(r.get("values_json", "") or "{}"))
            if not isinstance(values, dict):
                raise ValueError("values_json 非对象")
            pk_raw = r.get("prefix_key", "")
            try:
                pk_obj = json.loads(str(pk_raw)) if str(pk_raw).strip() else {}
                pk = "；".join(f"{k}={v}" for k, v in sorted(pk_obj.items())) if pk_obj else "无"
            except (json.JSONDecodeError, ValueError):
                pk = str(pk_raw)
            cid = make_candidate_id(rid)
            hyp = recipe_to_hypothesis(
                rid,
                values,
                pk,
                r.get("degraded_dimensions", ""),
                {
                    "sharpe": r.get("sharpe"),
                    "ann_return": r.get("ann_return"),
                    "max_drawdown": r.get("max_drawdown"),
                    "avg_turnover": r.get("avg_turnover"),
                    "net_days": r.get("net_days"),
                },
                batch_tag,
                descs,
            )
        except (json.JSONDecodeError, ValueError) as exc:
            report["skipped_malformed"].append(f"{rid[:16]}:{type(exc).__name__}")
            continue
        seen.add(rid)
        rows.append(
            {
                "candidate_id": cid,
                "hypothesis_zh": hyp,
                "birth_channel": BIRTH_CHANNEL,
                "birth_batch": birth_batch,
                "birth_source": birth_source,
                "recipe_id": rid,
                "prefix_key": str(r.get("prefix_key", "")),
                "degraded_dimensions": str(r.get("degraded_dimensions", "")),
                "sharpe": r.get("sharpe"),
                "ann_return": r.get("ann_return"),
                "max_drawdown": r.get("max_drawdown"),
                "avg_turnover": r.get("avg_turnover"),
                "net_days": r.get("net_days"),
                "values_json": str(r.get("values_json", "")),
            }
        )
    report["converted"] = len(rows)
    return rows, report


def _existing_ids(intake_csv: Path) -> set[str]:
    """台账既有 candidate_id 集（台账存在但不可读→RuntimeError fail-closed 防重复卸货）。"""
    if not intake_csv.exists():
        return set()
    try:
        df = pd.read_csv(intake_csv, encoding="utf-8-sig")
        ids = set(df["candidate_id"].astype(str))
    except Exception as exc:  # noqa: BLE001 — 读不出就拒绝卸货，宁停不重（防幂等破口）
        raise RuntimeError(f"F 车道台账存在但不可读，拒绝重复卸货: {intake_csv} ({exc})") from exc
    return ids


def run_intake(
    manifest: Path | str | None = None,
    intake_csv: Path | None = None,
    dry_run: bool = False,
) -> dict:
    """主流程：解析批次→转换→幂等过滤→CAS 追加卸台账。返回报告 dict（编排层直接入 report）。"""
    out_csv = intake_csv if intake_csv is not None else _INTAKE_CSV
    src = Path(manifest) if manifest is not None else latest_manifest()
    if src is None or not src.exists():
        return {"lane": BIRTH_CHANNEL, "status": "no_batch", "manifest": None, "written": 0}
    rows, rep = convert_manifest(src)
    done = _existing_ids(out_csv)
    fresh = [r for r in rows if r["candidate_id"] not in done]
    record: dict = {
        "lane": BIRTH_CHANNEL,
        "status": "ok",
        "manifest": rep["manifest"],
        "batch": rep["batch"],
        "rows_in_manifest": rep["rows_in_manifest"],
        "converted": rep["converted"],
        "skipped_existing": len(rows) - len(fresh),
        "skipped_malformed": rep["skipped_malformed"],
        "written": 0,
        "dry_run": dry_run,
    }
    if not fresh:
        record["status"] = "no_new" if rows else "empty_manifest"
        return record
    if dry_run:
        return record
    from scripts.backtest.intake_ledger_recon import append_ledger_rows

    res = append_ledger_rows(out_csv, fresh, list(LEDGER_COLUMNS))
    record["written"] = res["rows"]
    record["written_to"] = str(out_csv)
    record["after_sha256"] = res.get("after_sha256")
    return record


def main() -> int:
    ap = argparse.ArgumentParser(description="FAC-E1F 车道F 适配器（grid manifest→E2 假说台账）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    it = sub.add_parser("intake", help="最新（或指定）grid 批次→lane_f_candidates.csv（幂等）")
    it.add_argument("--manifest", default=None, help="指定 manifest 路径（缺省=最新批次）")
    it.add_argument("--intake-csv", default=None, help="台账路径注入（测试/预演用）")
    it.add_argument("--dry-run", action="store_true", help="只转换不落盘")
    args = ap.parse_args()
    try:
        record = run_intake(
            manifest=args.manifest,
            intake_csv=Path(args.intake_csv) if args.intake_csv else None,
            dry_run=args.dry_run,
        )
    except RuntimeError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(record, ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
