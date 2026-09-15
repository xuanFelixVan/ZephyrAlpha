# [BLUEPRINT] MOD-BT-171 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.auto_mount
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.translated._c4_engine(经翻译件注入); zephyr.data.ch_reader; zephyr.trading.decision_map; scripts.governance.d5_architecture.generators.check_decision_map; zephyr.shared.io.file_utils; zephyr.strategy_pipeline.fw_backtest(挂图落地后 fw_backtest_due 事件)
# [CONSUMERS] C6 入库线（strategy_registry 新条目→自动挂图）; decay_watch 月度挂图审计
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 全自动 only-add（diff 净删行=拒）；宁漏勿误（段<=0 或样本<30 天不激活）；
#   地图写入=文本级手术（node_id 分块+块内唯一锚+count==1）；写后 38 规则校验；挂载必 verified+evidence（R6）；
#   行数豁免（GOV-010 分层裁量 301-500 档）：本文件=五步管线单抽象族高内聚（映射/归因/配比/手术/报告
#   共享同一组常量与手术原语，拆分=跨文件耦合+常量漂移风险），变更隔离面=管线五步同批演化
# [MODIFY-GUARD] tests/backtest/test_auto_mount.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(锚点不唯一/only-add 断言失败/38 规则校验未过/claim 缺失)
# [TESTS] tests/backtest/test_auto_mount.py
# [A_module] module_id=MOD-BT-171 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] auto-mount-mod-bt-171-20260915
"""auto_mount 自动挂图器——策略转正后自动挂上决策地图（节点+状态格子+PP-001 配比）。

五步管线（立项真源 docs/_working/2026-09-14-auto-mount-research.md §4，验收五条同 §4）：
  ① 映射表 strategy_class→node_id（SOP-C §6.2 五行规则表硬编码）
  ② 分状态回测判 activation_state：c1_backtest.regime_snapshot_history.dominant 把 IS 窗切段逐段
     算 Sharpe；r→六段映射 R2SIX；段>0 且样本≥30 天才激活，且仅限类别候选态内（宁漏勿误）
  ③ PP-001 等权起步档：新 sleeve 0.05/条，老 sleeve 等比缩水保 sum=1.0
  ④ 文本级手术写入+only-add 断言+38 规则校验（run_checks）
  ⑤ 报告：挂了哪/为什么/证据指针

r→六段映射依据（2026-09-15 逐段 Sharpe 校准）：r10 CRISIS→capitulation；r4 熊市阴跌/r11 复苏→
accumulation；r3 牛市趋势→expansion；r12 BREAKOUT→ignition；r1 低波/r2 中波无六段对应→不路由。
校准一致率 5/6（STR-DABAN-023 expansion 漏挂=宁漏勿误方向，已知边界月度审计兜底）。

用法: --plan 预演只打印｜ --apply --strategy STR-A,STR-B 写入（先 claim+safe_write）｜
  --replay 幂等验收（已挂集合重放零 diff）｜ --audit 月度审计（只读）
判定缓存: .runtime/tmp/auto_mount_judge_cache.json（sid+code mtime+窗口键控，改规则/数据后可删）
"""

from __future__ import annotations

import argparse
import difflib
import importlib.util
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

REGISTRY = ROOT / "docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml"
MAP_YAML = ROOT / "config/trading_decision_map.yaml"
REPORT_DIR = ROOT / "docs/_working"
CACHE = ROOT / ".runtime/tmp/auto_mount_judge_cache.json"
IS_WIN = ("2020-01-01", "2023-12-31")
MIN_SEG_DAYS = 30
NEW_SLEEVE_WEIGHT = 0.05
CLASS_NODE_MAP = {  # ① SOP-C §6.2 映射表（规则真源）
    "value_reversal": "TDM-E-L1", "mean_reversion_timing": "TDM-E-L1", "trend_timing": "TDM-E-L1",
    "small_cap_quality": "TDM-E-L3-07-3", "value_quality": "TDM-E-L3-07-3", "intraday_gap": "TDM-P-P2",
}
CLASS_CANDIDATE_STATES: dict[str, set[str] | None] = {  # 语义先行候选态（数据只在态内裁决）
    "value_reversal": {"capitulation", "accumulation"}, "mean_reversion_timing": {"accumulation", "expansion"},
    "trend_timing": {"expansion", "ignition"}, "intraday_gap": {"accumulation", "expansion"},
    "small_cap_quality": None, "value_quality": None,  # 选股链无状态格
}
R2SIX = {"r10": "capitulation", "r4": "accumulation", "r11": "accumulation", "r3": "expansion", "r12": "ignition"}


def load_registry_entries() -> list[dict[str, Any]]:
    import yaml
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    return [{"sid": e["strategy_id"], "cls": e["strategy_class"], "code_path": e["code_path"],
             "lifecycle": e.get("lifecycle_status")} for e in data.get("strategies", [])
            if e.get("code_path") and e.get("strategy_class")]


def _load_translated_module(rel: str):
    path = Path(rel) if Path(rel).is_absolute() else ROOT / rel
    sys.path.insert(0, str(path.parent))
    sys.path.insert(0, str(ROOT / "scripts/backtest/translated"))  # _c4_engine 注入点（引擎与翻译件同目录）
    spec = importlib.util.spec_from_file_location(f"automount_{path.stem}", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _cached_judge(e: dict[str, Any], dom) -> dict[str, Any]:
    """② 分状态归因（带缓存：sid+code mtime+窗口+映射版本键控）。"""
    code = Path(e["code_path"]) if Path(e["code_path"]).is_absolute() else ROOT / e["code_path"]
    key = f"{e['sid']}|{int(code.stat().st_mtime)}|{IS_WIN}|{sorted(R2SIX)}|v2"
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    if cache.get(key):
        return cache[key]
    j = judge_activation_state(e["sid"], e["cls"], e["code_path"], dom)
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    cache[key] = j
    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    return j


def load_dominant():
    from zephyr.data import ch_reader
    tsv = ch_reader.query("SELECT trade_date, dominant FROM c1_backtest.regime_snapshot_history "
                          f"WHERE trade_date >= '{IS_WIN[0]}' AND trade_date <= '{IS_WIN[1]}' ORDER BY trade_date")
    import pandas as pd
    df = pd.DataFrame([l.split("\t") for l in tsv.strip().split("\n")], columns=["td", "dom"])
    df["td"] = pd.to_datetime(df["td"])
    return df.set_index("td")["dom"]


def judge_activation_state(sid: str, cls: str, code_path: str, dom) -> dict[str, Any]:
    """② 分状态归因；选股类 candidates=None→全段（activation_state=null）。"""
    import numpy as np
    import pandas as pd
    cands = CLASS_CANDIDATE_STATES.get(cls, set())
    if cands is None:
        return {"sid": sid, "activated": None, "segments": {}}
    mod = _load_translated_module(code_path)
    import _c4_engine  # noqa: PLC0415 经 translated 目录注入
    weights, closes = mod.build(*IS_WIN)
    net = _c4_engine.daily_net_returns(weights, closes)
    net.index = pd.to_datetime(net.index)
    joined = pd.concat([net.rename("net"), dom.rename("dom")], axis=1, join="inner").dropna()
    segs: dict[str, tuple[int, float]] = {}
    for r, six in R2SIX.items():
        if six not in cands:
            continue
        sub = joined[joined["dom"] == r]["net"]
        if len(sub) < MIN_SEG_DAYS:
            continue
        sr = float(sub.mean() / sub.std(ddof=1) * np.sqrt(252))
        n, prev = segs.get(six, (0, -np.inf))
        segs[six] = (n + int(len(sub)), max(prev, sr))
    activated = sorted(s for s, (n, sr) in segs.items() if sr > 0 and n >= MIN_SEG_DAYS)
    return {"sid": sid, "activated": activated, "segments": segs}


def sleeve_plan(new_refs: list[str], old: list[dict[str, Any]]) -> dict[str, float]:
    """③ 等权起步档：老 sleeve 等比缩水保 sum=1.0。"""
    keep = sum(float(x["weight"]) for x in old)
    scale = (1.0 - NEW_SLEEVE_WEIGHT * len(new_refs)) / keep if keep else 0.0
    out = {x["strategy_ref"]: round(float(x["weight"]) * scale, 6) for x in old}
    out.update({r: NEW_SLEEVE_WEIGHT for r in new_refs})
    return out


# ---------- ④ 文本级手术（node_id 分块+唯一锚+count==1） ----------
def _split_blocks(text: str) -> dict[str, tuple[int, int]]:
    starts = [(m.start(), m.group(1)) for m in re.finditer(r"(?m)^- node_id: (\S+)", text)]
    return {nid: (s, starts[i + 1][0] if i + 1 < len(starts) else len(text)) for i, (s, nid) in enumerate(starts)}


def _patch_block(text: str, node_id: str, new_block: str) -> str:
    s, e = _split_blocks(text)[node_id]
    out = text[:s] + new_block.rstrip("\n") + "\n" + text[e:]
    assert len(_split_blocks(out).get(node_id, ())) == 2, f"patch 后块不唯一: {node_id}"
    return out


def insert_node_mount(text: str, node_id: str, sid: str, evidence: str) -> str:
    block = text[_split_blocks(text)[node_id][0]:_split_blocks(text)[node_id][1]]
    assert f"strategy_ref: {sid}" not in block, f"{node_id} 已挂 {sid}"
    anchor = "  strategy_mounts:\n"
    assert block.count(anchor) == 1, f"strategy_mounts 锚不唯一: {node_id}"
    lines = block.splitlines(keepends=True)
    i = lines.index(anchor) + 1
    while i < len(lines) and lines[i].lstrip().startswith("- {strategy_ref"):
        i += 1
    lines.insert(i, f"  - {{strategy_ref: {sid}, confidence: verified, evidence: '{evidence}'}}\n")
    return _patch_block(text, node_id, "".join(lines))


def insert_cell(text: str, node_id: str, sid: str) -> str:
    """原位拼接：在该节点全部格子的 mounted [] 内追加 sid（多行折行格子安全）。"""
    pat = rf"(?m)^  - \{{node_id: {re.escape(node_id)}, state: (\w+), mounted: \["
    hits = list(re.finditer(pat, text))
    assert hits, f"state_matrix 无该节点格子: {node_id}"
    out = text
    for m in reversed(hits):
        # 括号配对找真闭括号（防多行折行格子把 ] 落在下一行）
        depth, i = 1, m.end()
        while depth:
            ch = out[i]
            depth += (ch == "[") - (ch == "]")
            i += 1
        close = i - 1
        inner = out[m.end():close]
        if sid in [x.strip() for x in inner.split(",")]:
            continue  # 幂等
        if not inner.strip():
            ins, pos = sid, close  # 空数组：] 前直插
        else:
            ins = f", {sid}"
            j = close  # 回退到最后一个非空白字符之后插入
            while j > m.end() and out[j - 1] in " \t\r\n":
                j -= 1
            pos = j
        out = out[:pos] + ins + out[pos:]
    return out


def insert_sleeve(text: str, sid: str, activation: list[str] | None) -> str:
    act = "null" if not activation else "[" + ", ".join(activation) + "]"
    line = f"  - {{strategy_ref: {sid}, weight: {NEW_SLEEVE_WEIGHT}, activation_state: {act}}}"
    anchor = "  sleeves:\n"
    assert text.count(anchor) == 1, "sleeves 锚不唯一"
    s = text.index(anchor) + len(anchor)
    seg_end = text.index("\n\n", s) if "\n\n" in text[s:] else len(text)
    hits = list(re.finditer(r"(?m)^  - \{strategy_ref: STR-", text[s:seg_end]))
    assert hits, "sleeves 无 STR- 行可锚"
    eol = text.index("\n", s + hits[-1].start()) + 1  # 最后一条 STR- sleeve 行尾=插入位（追加语义）
    return text[:eol] + line + "\n" + text[eol:]


def only_add_assert(before: str, after: str) -> None:
    """红蓝门（语义级）：挂载/格子/证据只增不减不改；sleeve 只增不减、老权重仅允许全局等比缩水
    （立项 §4③设计行为）、新 sleeve 必 0.05 起步。伪造删行/改证据/非等比改权重必被拒。"""
    import math
    import yaml
    b, a = yaml.safe_load(before), yaml.safe_load(after)

    def mounts(dm):
        return {n["node_id"]: {(m["strategy_ref"], m.get("confidence"), m.get("evidence"))
                                 for m in (n.get("strategy_mounts") or [])} for n in dm["nodes"]}

    bm, am_ = mounts(b), mounts(a)
    for nid, ms in bm.items():
        assert ms <= am_.get(nid, set()), f"only-add 违规：节点挂载被删/改 {nid}"

    def cells(dm):
        sm = dm.get("state_matrix") or {}
        return {(c["node_id"], c["state"]): (tuple(c.get("mounted") or []), c.get("confidence"))
                for c in (sm.get("cells") or [])}

    bc, ac = cells(b), cells(a)
    for k, (mounted, conf) in bc.items():
        ak = ac.get(k)
        assert ak, f"only-add 违规：格子被删 {k}"
        assert set(mounted) <= set(ak[0]), f"only-add 违规：格子挂载被删/改 {k}"
        assert conf == ak[1], f"only-add 违规：格子 confidence 被改 {k}"

    def sleeves(dm):
        return {s["strategy_ref"]: float(s["weight"]) for s in dm["portfolio_plan"]["sleeves"]}

    bs, as_ = sleeves(b), sleeves(a)
    for ref in bs:
        assert ref in as_, f"only-add 违规：sleeve 被删 {ref}"
    scales = [as_[ref] / w for ref, w in bs.items() if w > 0]
    assert scales, "only-add 异常：无老 sleeve 可比"
    s0 = scales[0]
    assert all(math.isclose(s, s0, rel_tol=2e-3) for s in scales), "only-add 违规：老 sleeve 权重非等比变动"
    for ref, w in as_.items():
        if ref not in bs:
            assert abs(w - NEW_SLEEVE_WEIGHT) < 1e-9, f"新 sleeve 起步档违规 {ref}={w}"


def validate_map() -> list[str]:
    gdir = str(ROOT / "scripts/governance/d5_architecture/generators")
    if gdir not in sys.path:
        sys.path.insert(0, gdir)
    from check_decision_map import run_checks
    fails, _warns, _total = run_checks(map_path=MAP_YAML, registry_dir=None)  # registry_dir 缺省=仓内 _registry 真源
    return fails


# ---------- 管线编排 ----------
def mounted_sids(text: str) -> set[str]:
    return set(re.findall(r"(?m)^  - \{strategy_ref: (STR-[\w-]+), confidence:", text))


def _plan_inserts(entries: list[dict[str, Any]], dom, only: set[str] | None) -> tuple[list[dict[str, Any]], str, str, list[str]]:
    text = MAP_YAML.read_text(encoding="utf-8")
    import yaml
    plan_data = yaml.safe_load(text)
    sleeves = plan_data["portfolio_plan"]["sleeves"]
    have_sleeve = {x["strategy_ref"] for x in sleeves}
    ops: list[dict[str, Any]] = []
    skipped: list[str] = []
    pipeline = [e for e in entries if "/translated/c4_" in e["code_path"].replace("\\", "/")]
    skipped += [f"{e['sid']}: code_path 非 C4 翻译件（无 build 契约）" for e in entries if e not in pipeline]
    if only is not None:
        pipeline = [e for e in pipeline if e["sid"] in only]
    for e in pipeline:
        j = _cached_judge(e, dom)
        node = CLASS_NODE_MAP.get(e["cls"])
        block = text[_split_blocks(text)[node][0]:_split_blocks(text)[node][1]] if node else ""
        if node and f"strategy_ref: {e['sid']}" not in block:
            seg_str = "; ".join(f"{s}={sr:+.2f}({n}d)" for s, (n, sr) in sorted(j["segments"].items()))
            evidence = (f"auto_mount IS {IS_WIN[0]}..{IS_WIN[1]} states={'+'.join(j['activated'] or [])}; "
                        f"{seg_str}; code={e['code_path']}").replace("'", "")  # YAML 单引号标量防注入
            ops.append({"kind": "node_mount", "node_id": node, "sid": e["sid"], "evidence": evidence[:150]})
        if j["activated"] and node:
            for st in j["activated"]:
                m = re.search(rf"(?m)^  - \{{node_id: {re.escape(node)}, state: {st}, mounted: \[([^\]]*)\]", text)
                if m and e["sid"] not in [x.strip() for x in m.group(1).split(",")]:
                    ops.append({"kind": "cell", "node_id": node, "state": st, "sid": e["sid"]})
        if e["sid"] not in have_sleeve:
            ops.append({"kind": "sleeve", "sid": e["sid"], "activation": j["activated"]})
    # 老 sleeve 等比缩水（立项 §4③ 设计行为；only_add 语义门放行全局等比）
    new_refs = [o["sid"] for o in ops if o["kind"] == "sleeve"]
    if new_refs:
        ops.append({"kind": "rescale", "plan": sleeve_plan(new_refs, sleeves)})
    return ops, text, json.dumps(sleeve_plan(new_refs, sleeves), ensure_ascii=False), skipped


def rescale_sleeves(text: str, plan: dict[str, float]) -> str:
    """老 sleeve 权重等比缩水（逐 sleeve 原位替换 weight 字段）。"""
    out = text
    for ref, w in plan.items():
        pat = rf"(?m)^(  - \{{strategy_ref: {re.escape(ref)}, weight: )(\d+(?:\.\d+)?)(,)"
        m = re.search(pat, out)
        assert m, f"rescale 找不到 sleeve 行: {ref}"
        out = out[:m.start(2)] + f"{w:g}" + out[m.end(2):]
    return out


def apply_ops(ops: list[dict[str, Any]], before: str) -> str:
    text = before
    for op in ops:
        if op["kind"] == "node_mount":
            text = insert_node_mount(text, op["node_id"], op["sid"], op["evidence"])
        elif op["kind"] == "cell":
            text = insert_cell(text, op["node_id"], op["sid"])
        elif op["kind"] == "sleeve":
            text = insert_sleeve(text, op["sid"], op["activation"])
        elif op["kind"] == "rescale":
            text = rescale_sleeves(text, op["plan"])
    return text


def mount_audit(scan_frequency: str | None = "monthly") -> dict[str, Any]:
    """月度挂图审计（钩子②）：只读三件套——地图 38 规则回执+衰减巡检同口径分档结果+挂载一致性盘点。

    挂接语义（对齐 decay_watch §调度挂载裁定）：审计函数无 IO 副作用，既可手动触发，
    也可被 decay_watch 同节奏调用方复用；不新建调度器（禁 cron/Timer，宪法 §9.3）。
    挂载一致性=格子 mounted 里的 STR-* 必须也在节点挂载区（防两边漂移）。
    """
    import yaml
    text = MAP_YAML.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    fails = validate_map()
    cells = data.get("state_matrix", {}).get("cells") or []
    node_mounted = {n["node_id"]: {m["strategy_ref"] for m in (n.get("strategy_mounts") or [])}
                    for n in data.get("nodes", [])}
    drift: list[str] = []
    for c in cells:
        nid = c.get("node_id", "")
        for sid in (c.get("mounted") or []):
            if str(sid).startswith("STR-") and sid not in node_mounted.get(nid, set()):
                drift.append(f"{nid}:{c.get('state')}:{sid} 格子挂载不在节点挂载区")
    mounted = sorted(mounted_sids(text))
    out: dict[str, Any] = {
        "audit": "ok" if not fails and not drift else "fails",
        "fails": fails,
        "mounted_count": len(mounted),
        "mounted": mounted,
        "drift": drift,
    }
    if scan_frequency:
        try:
            from zephyr.trading.validation.decay_watch import run_decay_check
            out["decay"] = run_decay_check(dry_run=True, scan_frequency=scan_frequency)
        except Exception as exc:  # noqa: BLE001 衰减档巡检是增强项，失败不阻断审计
            out["decay"] = {"error": str(exc)[:120]}
    return out


def write_report(payload: dict[str, Any], sid_label: str, out_dir: Path | None = None) -> Path:
    """报告落盘（钩子③，格式 Owner 已定稿）：Markdown 一页，专属子目录 docs/_working/auto-mount-reports/
    （平铺容量治理：不占 _working 根 120 硬上限；文件名带时间戳，标题内含对象清单）。
    内容=挂了哪/为什么（判定依据）/证据指针（run+code+段表）三节。"""
    stamp = datetime.now()
    out_dir = out_dir or (REPORT_DIR / "auto-mount-reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"auto-mount-report-{stamp.strftime('%Y%m%d-%H%M')}.md"
    ids = [x for x in sid_label.split(",") if x.strip()]
    if len(ids) > 8:
        shown = ", ".join(ids[:8]) + f" …等 {len(ids)} 条"
    else:
        shown = sid_label or "（重放）"
    lines = [
        f"# auto_mount 挂图报告——{shown}",
        "",
        f"> {stamp.strftime('%Y-%m-%d %H:%M')}｜管线=MOD-BT-171｜治理边界=only-add（本次 diff 无删改）",
        "",
        f"**对象清单**：{sid_label or '（重放：全部已挂 STR-* 幂等验证）'}",
        "",
        "## 挂了哪",
        "",
        "```yaml",
        payload.get("diff") or "（零 diff——幂等重放，地图无变化）",
        "```",
        "",
        "## 为什么",
        "",
    ]
    for j in payload.get("judgements", []):
        segs = "; ".join(f"{s}={sr:+.2f}({n}d)" for s, (n, sr) in sorted(j["segments"].items())) or "（选股类无状态格）"
        lines.append(f"- **{j['sid']}**（{j.get('cls', '')}）→ `{j.get('node') or '选股链'}`："
                     f"激活态={j['activated']}；分段证据 {segs}")
    lines += ["", "## 证据指针", "",
              f"- 判定窗口：IS {IS_WIN[0]}..{IS_WIN[1]}（C4 冻结口径）",
              f"- 状态真源：c1_backtest.regime_snapshot_history（dominant 列）",
              f"- 代码真源：注册表 code_path→翻译件 build()（见各条目）",
              f"- 地图回执：38 规则校验 {'通过' if not payload.get('fails') else payload.get('fails')}；"
              f"权重方案：{payload.get('weights', '{}')}", ""]
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description="auto_mount 自动挂图器（only-add）")
    ap.add_argument("--plan", action="store_true", help="预演：只算不写")
    ap.add_argument("--apply", action="store_true", help="写入地图（需显式 --strategy；先 claim+safe_write）")
    ap.add_argument("--replay", action="store_true", help="幂等验收：已挂集合重放断言零 diff")
    ap.add_argument("--audit", action="store_true", help="月度挂图审计（只读，含 decay 同口径分档）")
    ap.add_argument("--strategy", default=None, help="逗号分隔 strategy_id 列表")
    ap.add_argument("--report", action="store_true", help="报告落盘 docs/_working/（--plan/--apply/--replay 均可带）")
    ap.add_argument("--scan-frequency", default="monthly", choices=["monthly", "quarterly", "semiannual"],
                    help="审计档位（默认 monthly，对齐 decay_watch 分档）")
    args = ap.parse_args()
    only = {x.strip() for x in args.strategy.split(",") if x.strip()} if args.strategy else None
    entries = load_registry_entries()
    dom = load_dominant()
    if args.replay:
        text0 = MAP_YAML.read_text(encoding="utf-8")
        only = mounted_sids(text0)  # 重放范围=地图上已挂的 STR-*（幂等验收）
        assert only, "地图上无已挂 STR-* 可重放"
    ops, before, weights, skipped = _plan_inserts(entries, dom, only)
    report_payload: dict[str, Any] = {"judgements": [], "diff": None, "fails": None, "weights": weights}
    if args.audit:
        print(json.dumps(mount_audit(args.scan_frequency), ensure_ascii=False, indent=1))
        return
    # 判定摘要（报告/重放共用）：逐条判定依据+段证据
    for e in [x for x in entries if "/translated/c4_" in x["code_path"].replace("\\", "/")
              and (only is None or x["sid"] in only)]:
        j = _cached_judge(e, dom)
        report_payload["judgements"].append({"sid": e["sid"], "cls": e["cls"],
                                             "node": CLASS_NODE_MAP.get(e["cls"]),
                                             "activated": j["activated"], "segments": j["segments"]})
    if args.replay:
        assert not ops, f"重放非幂等：仍有 {len(ops)} 个待插操作 {ops[:3]}"
        report_payload["fails"] = validate_map()
        print(f"REPLAY OK: 已挂 {len(only)} 条零 diff（幂等）；38 规则 fails={len(report_payload['fails'])}")
        if args.report:
            rp = write_report(report_payload, ",".join(sorted(only))[:60])
            print(f"[REPORT] {rp}")
        return
    after = apply_ops(ops, before)
    only_add_assert(before, after)
    diff = "\n".join(difflib.unified_diff(before.splitlines(), after.splitlines(), "map.before", "map.after", lineterm="", n=1))
    report_payload["diff"] = diff
    print(diff or "(零 diff)")
    if skipped:
        print("[SKIPPED] " + "; ".join(skipped))
    if not args.apply:
        print(f"\n[PLAN] ops={len(ops)} weights={weights}")
        if args.report:
            rp = write_report(report_payload, args.strategy or "plan")
            print(f"[REPORT] {rp}")
        return
    assert only, "--apply 必须显式给 --strategy（挂谁=C6 线决策，工具只管怎么挂）"
    from zephyr.shared.io.file_utils import safe_write_text
    import hashlib
    r = safe_write_text(MAP_YAML, after, expected_base_sha256=hashlib.sha256(before.encode()).hexdigest(), newline="\n")
    if not getattr(r, "written", True):
        raise RuntimeError("safe_write_text 未确认写入")
    fails = validate_map()
    assert not fails, f"38 规则校验未过: {fails[:5]}"
    report_payload["fails"] = fails
    print(f"\n[APPLIED] ops={len(ops)} 校验全绿 written={getattr(r, 'written', True)}")
    # S11/C3 断桥③: 挂图落地成功 → fw_backtest_due（TDM sleeves→整装回测自动跑+证据包）；
    # 事件链任何故障不反噬挂图管线（journal 已留档，恢复=drain 重放）
    try:
        from zephyr.strategy_pipeline.fw_backtest import emit_fw_backtest_due

        fw = emit_fw_backtest_due(trigger="auto_mount", sids=sorted(only))
        tail = f" err={fw.get('error')}" if fw.get("error") else ""
        print(f"[FW-BACKTEST-DUE] event={fw.get('event')} drained={fw.get('drained')}{tail}")
    except Exception as exc:  # noqa: BLE001——事件链故障不回滚挂图
        print(f"[FW-BACKTEST-DUE] emit 失败（不影响挂图结果）: {type(exc).__name__}: {exc}")
    if args.report:
        rp = write_report(report_payload, args.strategy)
        print(f"[REPORT] {rp}")


if __name__ == "__main__":
    sys.exit(main())
