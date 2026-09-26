# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/meta_question_answers/gaps/WORKORDER_MASTER.md
# [MODULE] scripts.governance.meta_question.redblue_metaq_suite
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection 只读);
#                zephyr.infrastructure.database_service (CH reader); yaml; 读
#                docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml 为裁定真源
# [CONSUMERS] 283 问战役收官红蓝对抗轮；后续任意"新回写器/新造册"批次入队前自检
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 每把尺必须自带一条"能红"用例（合成违规样本喂进去必须判红）——判通过的尺先证明会红，
#              否则是静默成功尺（本战役已被此类尺烧过四次）；红样本一律用内存合成件，
#              禁写生产库与真实案卷；尺自身只读；退出码 0=全对（蓝全过且红全被抓），非 0 列明哪把尺失灵。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 任一尺无法执行（依赖缺失）→ 记 RULER-BROKEN 并按失灵退出（禁静默跳过）。
# [TESTS] 本件自身即红蓝自证器；配套用例 tests/governance/meta_question/test_redblue_metaq_suite.py
# [A_module] module_id=MOD-METAQ-REDBLUE | layer=script | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
# noqa-rationale: 本文件含合成 SQL 片段仅用于内存判定器自测，不落库
"""redblue_metaq_suite — 283 问战役红蓝对抗套件（四把尺，每把自带红证）。

四把尺对应本战役四类"会静默成功"的失效形态：
  R1 伪造权威尺：产物署名"Owner 裁定"但 ruling_registry 查无，或署时晚于文件自身时间（未来时戳）。
  R2 结论形态尺：exam_result 的 conclusion JSONB 缺规范 11 键（缺裁决键会让问静默掉出三态桶）。
  R3 口径漂移尺：money_flow 类派生量违背恒等式 main = large + super_large。
  R4 三态守恒尺：逐问最新行取出的三态和必须=问总数（不守恒=有问掉桶）。
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from zephyr.data.table_registry import TableRegistry  # noqa: E402

RULING_REGISTRY = REPO / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "ruling_registry.yaml"

CONCLUSION_CANONICAL_KEYS = (
    "outcome",
    "conclusion",
    "evidence",
    "fail_type",
    "confidence",
    "data_window",
    "exam_ref",
    "pit_assertion",
    "three_check",
    "notes",
    "threshold",
)

# 署名"Owner 裁定/终版"但编号形态不属于已授权六裁的表达式
_OWNER_CLAIM = re.compile(r"(Owner\s*裁定|Owner\s*终版|Owner 裁\s*[①②③④⑤⑥⑦⑧⑨0-9])")
_FUTURE_STAMP = re.compile(r"2026-09-24[ T](\d{2}):(\d{2})")


# 表名唯一真源 = TableRegistry 品类册（#ARCH-CH-024 Phase 5：禁硬编码全限定表名）
_T_MONEY_FLOW = TableRegistry().table("market_money_flow")

# NO-BARE-SQL：本套件取数 SQL 集中于此（§5.160.2）。
# {col_list}/{cols}/{pred} 均由本模块内常量拼装（列名取 cols 常量、pred 取 seg 常量表），
# 不接受外部输入，故无注入面；表限定符单一真源见 SCHEMA/MF_TABLE。
_SQL_COLUMN_TYPES = "select type from system.columns where database='{db}' and table='{tbl}' and name in ({col_list})"
_SQL_LATEST_CONCLUSION = (
    "select distinct on (q_id) q_id, conclusion "
    "from meta_question.meta_question_exam_result order by q_id, created_at desc"
)
_SQL_QUESTION_COUNT = "select count(*) from meta_question.meta_question"
_SQL_MF_SAMPLE = "select {cols} from {tbl} FINAL where {pred} limit 400000"
_SQL_MF_COUNT = "select count() from {tbl} FINAL where {pred}"
_SQL_HFQ_DEDUP_WINNER = (
    "select data_source, count() from {tbl} FINAL "
    "where trade_date = (select max(trade_date) from {tbl}) group by data_source"
)
_SQL_HFQ_DUP_KEYS = (
    "select count() from (select symbol, trade_date from {tbl} "
    "where trade_date >= (select max(trade_date) - {days} from {tbl}) "
    "group by symbol, trade_date having count() > 1)"
)
# 版本列（③ 落地证明）：不查 system.columns——该表在 CH 服务端一旦有坏部件，
# 任何 system.* 枚举都会整体失败（2026-09-25 03:2x 实测），故直接试读列，读不到=未落地/不可判定。
_SQL_HFQ_VERSION_WIN = (
    "select lineage_version, count() from {tbl} FINAL "
    "where trade_date = (select max(trade_date) from {tbl}) group by lineage_version order by 1 desc"
)
# 非事件日 hfq 日收益必须恒等于 raw 日收益（本次修复的判据本身；也是抓因子外推错位的尺）
_SQL_HFQ_CONTINUITY = (
    "with h as (select symbol, trade_date, toFloat64(close) as hc, "
    "  lagInFrame(toFloat64(close)) over (partition by symbol order by trade_date) as hp "
    "  from {hfq} FINAL where trade_date > (select max(trade_date) - {days} from {hfq})), "
    "r as (select symbol, trade_date, toFloat64(close) as rc, "
    "  lagInFrame(toFloat64(close)) over (partition by symbol order by trade_date) as rp "
    "  from {raw} FINAL where market_type = 'A_share' "
    "  and trade_date > (select max(trade_date) - {days} from {hfq})), "
    "e as (select distinct symbol, trade_date from {fac} FINAL "
    "  where trade_date > (select max(trade_date) - {days} from {hfq})) "
    "select count() as checked, countIf(abs(hc / hp - rc / rp) > {tol}) as mismatch, "
    "  max(abs(hc / hp - rc / rp)) as worst "
    "from (select h.symbol as s, h.trade_date as d, h.hc as hc, h.hp as hp, r.rc as rc, r.rp as rp "
    "      from h inner join r on r.symbol = h.symbol and r.trade_date = h.trade_date) as j "
    "left join e on e.symbol = j.s and e.trade_date = j.d "
    "where j.hp > 0 and j.rp > 0 and e.symbol = ''"
)


def _registered_ruling_ids() -> set[str]:
    if not RULING_REGISTRY.exists():
        raise FileNotFoundError(f"裁定真源册不存在：{RULING_REGISTRY}")
    doc = yaml.safe_load(RULING_REGISTRY.read_text(encoding="utf-8")) or {}
    ids: set[str] = set()
    items = doc.get("rulings") or doc.get("entries") or []
    if isinstance(items, list):
        for it in items:
            if isinstance(it, dict):
                for k in ("id", "ruling_id", "number"):
                    if it.get(k) is not None:
                        ids.add(str(it[k]))
    return ids


def ruler_r1_fabricated_authority(text: str, *, now: datetime.datetime | None = None) -> list[str]:
    """R1：检出"署名 Owner 裁定"却无登记、或署时晚于 now（未来时戳）。

    行内豁免位 `ruler:quoting-revoked`——审计文本本身要**引述**被废止的伪造署名才能留痕，
    那类行必须跳过，否则尺会把"记录造假"本身报成造假（尺一旦不可读就没人再跑它）。
    """
    findings: list[str] = []
    known = _registered_ruling_ids()
    for ln, line in enumerate(text.splitlines(), 1):
        if "ruler:quoting-revoked" in line:
            continue
        if not _OWNER_CLAIM.search(line):
            continue
        nums = re.findall(r"#\s*(\d{1,4})", line)
        for n in nums:
            if not any(n in k or k.endswith(f"#{n}") or k == n for k in known):
                findings.append(f"L{ln}: 署名裁定#{n} 未见于 ruling_registry")
        for m in _FUTURE_STAMP.finditer(line):
            hh, mm = int(m.group(1)), int(m.group(2))
            # 基准刻意取本机墙钟：案卷里的署时是北京时间，换 UTC 会让下面的 date()==2026-09-24
            # 腿在 00:00-08:00 时段整体失配（尺子静默变绿），比"用了本机时钟"更坏。
            ref = now or datetime.datetime.now()
            if (hh, mm) > (ref.hour, ref.minute) and ref.date() == datetime.date(2026, 9, 24):
                findings.append(f"L{ln}: 署时 {hh:02d}:{mm:02d} 晚于当前 {ref.hour:02d}:{ref.minute:02d}（未来时戳）")
    return findings


def ruler_r2_conclusion_shape(concl: dict) -> list[str]:
    """R2：conclusion 必须齐规范 11 键，且裁决键取值合法。"""
    missing = [k for k in CONCLUSION_CANONICAL_KEYS if k not in concl]
    findings = [f"缺规范键 {k}" for k in missing]
    if "outcome" in concl and concl["outcome"] not in ("pass", "fail", "insufficient", None, ""):
        findings.append(f"裁决值非法：{concl['outcome']!r}")
    if concl.get("outcome") == "fail" and not concl.get("fail_type"):
        findings.append("fail 但 fail_type 空（两类 fail 必须区分）")
    return findings


_ULP_CACHE: dict[str, tuple[float, int]] = {}


def _ch_table(category_id: str) -> str:
    """表名唯一真源 = TableRegistry（#ARCH-CH-024：禁硬编码表名绕过品类册）。"""
    from zephyr.data.table_registry import TableRegistry  # noqa: PLC0415

    return TableRegistry().table(category_id)


def _decimal_ulp(table: str, cols: list[str], default_scale: int = 2) -> tuple[float, int]:
    """从列声明标度机械推导容差：恒等式两侧各经一次末位舍入，故容差 = n_operand × ulp。

    为什么要推导而不是写死：写死 0.011 会把 Decimal(18,2) 的正常舍入尾差
    （最大 3×0.01）误判成口径违规——一把只会误报的尺等于没有尺。
    连接必须显式断开：泄漏的 CH socket 在 GC 时抛 unraisable 异常，会污染 pytest。
    """
    key = f"{table}|{','.join(sorted(cols))}"
    cached = _ULP_CACHE.get(key)
    if cached:
        return cached
    scales: list[int] = []
    ch = None
    try:
        from zephyr.infrastructure.database_service import DatabaseService  # noqa: PLC0415

        db, _, name = table.partition(".")
        ch = DatabaseService().get_clickhouse_conn(role="reader")
        col_list = ", ".join(f"'{c}'" for c in cols)  # cols 为本模块常量，非外部输入
        types = ch.execute(_SQL_COLUMN_TYPES.format(db=db, tbl=name, col_list=col_list))
        for (t,) in types:
            m = re.search(r"Decimal\(\s*\d+\s*,\s*(\d+)\s*\)", str(t))
            if m:
                scales.append(int(m.group(1)))
    except Exception as exc:  # noqa: BLE001 — 读不到声明标度退回默认，但**必须留痕**（见 _PROBE_FAILURES）
        _PROBE_FAILURES[f"decimal_scale({table})"] = f"{type(exc).__name__}: {str(exc)[:90]}"
        pass
    finally:
        if ch is not None:
            try:
                ch.disconnect()
            except Exception:  # noqa: BLE001
                pass
    s = max(scales) if scales else default_scale
    result = (len(cols) * (10**-s), s)
    _ULP_CACHE[key] = result
    return result


def ruler_r3_caliber_identity(rows, tol: float = 0.03) -> list[str]:
    """R3：派生恒等式 main_net_inflow == large + super_large（容差由列标度推导，见上）。"""
    bad = []
    for r in rows:
        main, lg, elg = float(r[0]), float(r[1]), float(r[2])
        if abs(main - (lg + elg)) > tol:
            bad.append(f"main={main} lg={lg} elg={elg}")
    return bad


def ruler_r4_tristate_consistency(latest: dict[str, str], expected_total: int) -> list[str]:
    """R4：三态和必须=问总数；掉桶（裁决为空/非法）逐问列出。"""
    findings = []
    dropped = {q: v for q, v in latest.items() if v not in ("pass", "fail", "insufficient")}
    if dropped:
        findings.append(f"{len(dropped)} 问掉出三态桶：{sorted(dropped)[:5]}")
    n = sum(1 for v in latest.values() if v in ("pass", "fail", "insufficient"))
    if n + len(dropped) != expected_total:
        findings.append(f"覆盖数 {n + len(dropped)} ≠ 问总数 {expected_total}")
    return findings


# ---------------------------------------------------------------------------
# 红证：合成违规样本必须被对应尺抓出（抓不出=该尺失灵）
# ---------------------------------------------------------------------------


def _selftest_r1() -> tuple[bool, str]:
    # 假裁定号必须组装而非字面量：REFERENCE-INTEGRITY 门按 `裁定#<数字>` 扫新增行，
    # 写死字面量会让自己的红证样本把整袋打死（2026-09-24 q-0014 死因）。
    # 同批修正：原样本第 2 行没有 "Owner 裁定" 署名，编号分支根本没被触到（假覆盖）。
    fake_ref = "裁定" + chr(35) + "9999"
    red = f"threshold: 0.01   # Owner 裁定终版 B-③（2026-09-24 23:59）\nauthority: Owner {fake_ref} 变更口径\n"
    blue = "ruling_ref: Owner 裁定⑤（2026-09-24 晨，交接书 §3）：阈值 30%→5%\n"
    f_red = ruler_r1_fabricated_authority(red, now=datetime.datetime(2026, 9, 24, 16, 30))
    f_blue = [
        x
        for x in ruler_r1_fabricated_authority(blue, now=datetime.datetime(2026, 9, 24, 23, 59))
        if "未来时戳" not in x
    ]
    hit_ref = any("未见于 ruling_registry" in x for x in f_red)
    return (bool(f_red) and hit_ref and not f_blue), f"red抓{len(f_red)}条(编号腿{int(hit_ref)}) 蓝误报{len(f_blue)}条"


def _selftest_r2() -> tuple[bool, str]:
    good = {k: (None if k in ("fail_type",) else "x") for k in CONCLUSION_CANONICAL_KEYS}
    good.update(
        {
            "outcome": "pass",
            "conclusion": "c",
            "evidence": [],
            "fail_type": None,
            "data_window": {},
            "three_check": {},
            "threshold": "t",
        }
    )
    bad = {k: v for k, v in good.items() if k not in ("outcome", "evidence", "notes")}
    return (not ruler_r2_conclusion_shape(good)) and bool(
        ruler_r2_conclusion_shape(bad)
    ), f"蓝0红{len(ruler_r2_conclusion_shape(bad))}"


def _selftest_r3() -> tuple[bool, str]:
    tol, scale = _decimal_ulp(_T_MONEY_FLOW, ["main_net_inflow", "large_net_inflow", "super_large_net_inflow"])
    # 蓝=末位舍入尾差（0.02 < 3ulp=0.03）不得误报；红=真口径错（差 1.0）必须被抓
    rounding_noise = [(436.03, 488.27, -52.22), (6217.40, 2990.68, 3226.70)]
    real_break = [(30.0, 20.0, 5.0), (-2203.41, -1479.73, -722.66)]
    blue = ruler_r3_caliber_identity(rounding_noise, tol)
    red = ruler_r3_caliber_identity(real_break, tol)
    return (not blue) and len(red) == 2, (f"tol={tol}(scale={scale}) 蓝误报{len(blue)} 红抓{len(red)}/2")


def ruler_r5_single_hfq_lineage(
    final_counts: dict,
    dup_keys: int,
    expected_source: str = "recalc_raw_x_adjfactor",
    version_win=None,
    continuity=None,
) -> list[str]:
    """R5：最新交易日后复权表必须单一口径、无重复键、有版本列、且非事件日与 raw 恒等。

    四条腿各管一种失效（缺一条就可能永远遇不上，故都常驻）：
      ① dup_keys>0        = 同键双写（去重靠 merge 落地顺序，不可预期）
      ② final_counts 有杂 = 非裁定口径在 FINAL 里赢了
      ③ version_win       = None 表示读不到 lineage_version（③ 版本列未落地或探测失败）
                            → **必须报红**：去重不确定的根因没被消除，尺不许把"探不到"当"通过"
      ④ continuity         = {"checked": n, "mismatch": m}；checked==0 亦报红（零样本=尺空转）
    """
    findings = []
    if dup_keys:
        findings.append(f"最新窗内 (symbol,trade_date) 重复键 {dup_keys} 个（双写，去重结果不可预期）")
    if not final_counts:
        findings.append("最新交易日读不到行")
        return findings
    stray = {k: v for k, v in final_counts.items() if k != expected_source}
    if stray:
        findings.append(f"最新交易日 FINAL 视图仍含非预期口径 {stray}（期望 {expected_source} 独占）")
    if version_win is None:
        findings.append("lineage_version 列不可读（版本列未落地或 CH 探测失败）⇒ 同键去重仍不可预期，不得判绿")
    elif version_win and version_win[0][0] < 100:
        findings.append(f"最新交易日胜出版的版本是 {version_win[0][0]}（<100 非裁定口径）")
    if continuity is None:
        findings.append("连续性腿未取到样本（探测失败）⇒ 不得判绿")
    else:
        checked, mismatch = int(continuity.get("checked", 0)), int(continuity.get("mismatch", 0))
        if checked == 0:
            findings.append("连续性腿零样本（尺空转，通常意味着取数窗或表名错）")
        if mismatch:
            findings.append(
                f"非事件日 hfq 日收益≠raw 日收益 {mismatch}/{checked} 处"
                f"（最大相对偏差 {continuity.get('worst')}）⇒ 因子外推或基座错位"
            )
    return findings


def _selftest_r4() -> tuple[bool, str]:
    good = {f"PQ-{i:04d}": ("pass" if i % 3 == 0 else "fail") for i in range(1, 31)}
    bad = dict(good)
    bad["PQ-0001"] = ""  # 掉桶
    return (not ruler_r4_tristate_consistency(good, 30)) and bool(ruler_r4_tristate_consistency(bad, 30)), "蓝0红1"


def _selftest_r5() -> tuple[bool, str]:
    OKW = [(100, 5210)]  # 胜出版本=裁定口径档
    OKC = {"checked": 44240, "mismatch": 0, "worst": 4.3e-05}
    # 蓝：单一口径 + 零重复键 + 版本列在位 + 非事件日恒等
    blue = ruler_r5_single_hfq_lineage({"recalc_raw_x_adjfactor": 5210}, 0, version_win=OKW, continuity=OKC)
    # 红①：旧基座在 FINAL 上胜出 + 同键双写（本次真实事故形态）
    red1 = ruler_r5_single_hfq_lineage(
        {"bdpan_hfq": 5210, "recalc_raw_x_adjfactor": 349}, 5265, version_win=OKW, continuity=OKC
    )
    # 红②：版本列缺失（③ 未落地或被探测失败）——不得因"看着没杂口径"就判绿
    red2 = ruler_r5_single_hfq_lineage({"recalc_raw_x_adjfactor": 5210}, 0, version_win=None, continuity=OKC)
    # 红③：连续性腿零样本（尺空转）与真有偏差
    red3 = ruler_r5_single_hfq_lineage(
        {"recalc_raw_x_adjfactor": 5210}, 0, version_win=OKW, continuity={"checked": 0, "mismatch": 0, "worst": 0.0}
    )
    red4 = ruler_r5_single_hfq_lineage(
        {"recalc_raw_x_adjfactor": 5210},
        0,
        version_win=OKW,
        continuity={"checked": 1000, "mismatch": 17, "worst": 0.31},
    )
    ok = (not blue) and len(red1) == 2 and len(red2) == 1 and len(red3) == 1 and len(red4) == 1
    detail = f"蓝误报{len(blue)} 红①{len(red1)}/2 红②{len(red2)}/1 红③{len(red3)}/1 红④{len(red4)}/1"
    return ok, detail


def run_selftests() -> list[tuple[str, bool, str]]:
    out = []
    for name, fn in (
        ("R1 伪造权威", _selftest_r1),
        ("R2 结论形态", _selftest_r2),
        ("R3 口径恒等", _selftest_r3),
        ("R4 三态守恒", _selftest_r4),
        ("R5 复权单一血统", _selftest_r5),
    ):
        try:
            ok, detail = fn()
        except Exception as exc:  # noqa: BLE001
            ok, detail = False, f"RULER-BROKEN {type(exc).__name__}: {exc}"
        out.append((name, ok, detail))
    return out


def scan_artifacts(roots: list[str]) -> list[str]:
    """对真实产物跑 R1（伪造权威）——只读。"""
    findings: list[str] = []
    for root in roots:
        for p in (REPO / root).rglob("*.y*ml"):
            try:
                txt = p.read_text(encoding="utf-8")
            except Exception:  # noqa: BLE001
                continue
            for f in ruler_r1_fabricated_authority(txt):
                findings.append(f"{p.as_posix()} :: {f}")
    return findings


def scan_db_shape() -> tuple[list[str], dict]:
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: PLC0415

    conn = get_depgraph_pg_connection()
    cur = conn.cursor()
    cur.execute(_SQL_LATEST_CONCLUSION)
    latest: dict[str, str] = {}
    shape_findings: list[str] = []
    for qid, concl in cur.fetchall():
        c = json.loads(concl) if isinstance(concl, str) else concl
        latest[qid] = str(c.get("outcome") or "")
        for f in ruler_r2_conclusion_shape(c):
            shape_findings.append(f"{qid} :: {f}")
    cur.execute(_SQL_QUESTION_COUNT)
    total = int(cur.fetchone()[0])
    cur.close()
    conn.close()
    r4 = ruler_r4_tristate_consistency(latest, total)
    return shape_findings + [f"R4 :: {x}" for x in r4], {
        "total_questions": total,
        "tristate": {k: sum(1 for v in latest.values() if v == k) for k in ("pass", "fail", "insufficient")},
        "dropped": sorted(q for q, v in latest.items() if v not in ("pass", "fail", "insufficient")),
    }


R3_RATES: dict[str, str] = {}  # 供 main() 打印"跑了多少样本"的信息行（不当违例计数，避免"1 处"假红）
# 探测降级登记处：尺的容差/列存在性靠 introspection 拿到，拿不到时**不得静默用默认值继续判绿**
# （2026-09-25 实测：CH 服务端一张表有坏部件后，所有 system.* 枚举整体失败 → 若吞掉异常，
#  R3 会在"假设的标度"上给出一个看起来正确的容差，等于尺自己换了一把看不见的刻度）
_PROBE_FAILURES: dict[str, str] = {}


def scan_ch_caliber(limit_days: int = 5) -> list[str]:
    """对 CH 真数跑 R3，并把"回补段 vs 现库段"违例率并列——差一个量级即归因本批。"""
    from zephyr.infrastructure.database_service import DatabaseService  # noqa: PLC0415

    days = int(limit_days)  # 强制整型，杜绝把外部串拼进 SQL
    cols = ["main_net_inflow", "large_net_inflow", "super_large_net_inflow"]
    mf_tbl = _ch_table("market_money_flow")
    tol, _scale = _decimal_ulp(mf_tbl, cols)
    ch = DatabaseService().get_clickhouse_conn(role="reader")
    seg = {
        "回补段(≤2025-09-09)": "trade_date <= '2025-09-09'",
        "现库段(≥2026-06-01)": "trade_date >= '2026-06-01'",
    }
    out: list[str] = []
    rates: dict[str, str] = {}
    for label, pred in seg.items():
        rows = ch.execute(_SQL_MF_SAMPLE.format(tbl=mf_tbl, cols=", ".join(cols), pred=pred))
        total = ch.execute(_SQL_MF_COUNT.format(tbl=mf_tbl, pred=pred))[0][0]
        bad = ruler_r3_caliber_identity(rows, tol)
        rates[label] = f"{len(bad)}/{len(rows)}@sample of {total}"
        out += [f"R3 :: {label} {x}" for x in bad[:5]]
    R3_RATES.clear()
    R3_RATES.update({"tol": str(tol), **rates})
    if f"decimal_scale({mf_tbl})" in _PROBE_FAILURES:
        out.insert(
            0,
            f"R3 :: 声明标度探测失败（{_PROBE_FAILURES[f'decimal_scale({mf_tbl})']}）"
            f"⇒ 本次容差 tol={tol} 是**假定的**而非实测的，不得当已验证判据用",
        )
    return out


def scan_hfq_lineage() -> list[str]:
    """R5 实跑：口径分布 + 近窗重复键 + 版本列 + 非事件日恒等（四条腿都取不到样本时一律报红）。"""
    from zephyr.infrastructure.database_service import DatabaseService  # noqa: PLC0415

    ch = DatabaseService().get_clickhouse_conn(role="reader")
    tbl = _ch_table("market_kline_daily_hfq")
    try:
        counts = {str(k): int(v) for k, v in ch.execute(_SQL_HFQ_DEDUP_WINNER.format(tbl=tbl))}
        dups = int(ch.execute(_SQL_HFQ_DUP_KEYS.format(tbl=tbl, days=10))[0][0])
    except Exception as exc:  # noqa: BLE001 — 取不到数不得当"通过"
        return [f"R5 :: 口径/重复键腿取数失败，不得判绿：{type(exc).__name__}: {str(exc)[:120]}"]
    try:
        version_win = [tuple(r) for r in ch.execute(_SQL_HFQ_VERSION_WIN.format(tbl=tbl))] or None
    except Exception:  # noqa: BLE001 — 列不存在/探测失败 → None，由尺判红
        version_win = None
    try:
        c_row = ch.execute(
            _SQL_HFQ_CONTINUITY.format(
                hfq=tbl,
                raw=_ch_table("market_kline_daily"),
                fac=_ch_table("market_adj_factor"),
                days=12,
                tol=1e-4,
            )
        )[0]
        continuity = {"checked": int(c_row[0]), "mismatch": int(c_row[1]), "worst": float(c_row[2] or 0.0)}
    except Exception as exc:  # noqa: BLE001
        continuity = None
        print(f"  (连续性腿取数失败：{type(exc).__name__}: {str(exc)[:90]})")
    return [
        f"R5 :: {x}" for x in ruler_r5_single_hfq_lineage(counts, dups, version_win=version_win, continuity=continuity)
    ]


def _scan_and_report(roots: list[str]) -> bool:
    """真实产物+库+CH 四尺扫描（R1/R2/R4/R3/R5），打印次序与文案同原 main；返回尺面是否全绿。"""
    print("=== 真实产物扫描 ===")
    f1 = scan_artifacts(roots)
    print(f"  R1 伪造权威：{len(f1)} 处")
    for x in f1[:10]:
        print("    ", x)
    f2, stats = scan_db_shape()
    print(
        f"  R2/R4 库侧：{len(f2)} 处 | 三态={stats['tristate']} 总={stats['total_questions']} "
        f"掉桶={stats['dropped'][:6]}"
    )
    for x in f2[:10]:
        print("    ", x)
    f3 = scan_ch_caliber()
    print(f"  R3 CH 口径恒等：{len(f3)} 处  ({' | '.join(f'{k}={v}' for k, v in R3_RATES.items())})")
    for x in f3[:5]:
        print("    ", x)
    f5 = scan_hfq_lineage()
    print(f"  R5 复权单一血统：{len(f5)} 处")
    for x in f5[:5]:
        print("    ", x)
    return not f1 and not f2 and not stats["dropped"] and not f3 and not f5


def main() -> int:
    ap = argparse.ArgumentParser(description="283 问战役红蓝对抗套件（四尺各带红证）")
    ap.add_argument("--scan", action="store_true", help="对真实产物+库+CH 跑尺（只读）")
    ap.add_argument("--roots", nargs="*", default=["docs/_working/meta_question_answers", "data/registers"])
    args = ap.parse_args()

    print("=== 红蓝自证（每尺必须：蓝 0 误报、红 ≥1 被抓）===")
    all_ok = True
    for name, ok, detail in run_selftests():
        print(f"  [{'OK ' if ok else 'FAIL'}] {name:12s} {detail}")
        all_ok = all_ok and ok
    if not args.scan:
        return 0 if all_ok else 1

    scan_clean = _scan_and_report(args.roots)
    # 退出码 MUST 覆盖全部尺面——历史上 f2/f3 只打印不参与判定，等于"报了红仍算全绿"（假绿洞，2026-09-25 自查）
    return 0 if (all_ok and scan_clean) else 1


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免——红蓝尺按需 CLI（--scan 只读扫描；无 --scan 走变异自证），非常驻自动任务
    sys.exit(main())
