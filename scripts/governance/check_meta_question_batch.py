# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/03_modules/MOD-CHAINPILE-METAQ/blueprint.md | 批次机检口径
# [MODULE] scripts.governance.check_meta_question_batch
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] src/zephyr/governance/meta_question/meta_question_registry.py（A级必填/枚举/查重口径真源）; docs/_working/chain_piling_campaign/snapshots/question_batch_w6.yaml（只读校验对象）
# [CONSUMERS] 定桩战役 W6 批次验收（人工 CLI 调用）; 99 终报 §2 验收硬数字
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 纯读校验零写入零连库；违规=0 才 RC=0；判据改动必须先改 registry.py/纪要真源
# [MODIFY-GUARD] src/zephyr/governance/meta_question/meta_question_registry.py 校验段 + 00_piling_minutes.md §2/§6/§9
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RC=0 全通过；RC=1 存在违规（逐条打印清单）；输入文件缺失=异常上抛（fail-closed）
# [TESTS] none
# [TTL] task_bound
# noqa: m11-perm-manual-legitimate  M11豁免: 战役批次只读校验 CLI（按需调用零驻留），task_bound 随战役归档
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_w6_batch — W6 问题批次 JSON 纯读校验（统计+违规清单，rc 0/1）。

校验对象：docs/_working/chain_piling_campaign/snapshots/question_batch_w6.yaml
机检口径真源：
- src/zephyr/governance/meta_question/meta_question_registry.py（A 级必填/枚举/五要素降级口径/
  normalize_title 查重方法/event_driven 须 event_source_ref）
- 00_piling_minutes.md [纪要§2 五要素/§6 62 条骨架/§9 250-400]
- 02_source_line_registry.md §1-§5（data_sources 白名单来源）
- 03_graph_registry.md §6（GRF1-GRF18 槽位分布）
- 11_template_generator_design.md §6（space_hash 预注册/禁事后扩）

纯读：json.load+集合运算+打印；不写任何文件、不连任何库。
用法：python check_w6_batch.py [batch_json_path]（缺省按本脚本相对定位）
退出码：0=全部通过；1=存在违规（清单逐条打印）。
"""

import json  # noqa: F401  仅 dumps 序列化用
import sys
import unicodedata
from collections import Counter
from pathlib import Path

import yaml

from zephyr.shared.io.yaml_utils import load_vocabulary_values

BATCH_ID = "W6-st-chainpile-20260922"

VALID_LAYERS = tuple(sorted(load_vocabulary_values("meta_question_layers_vocabulary.yaml")))
VALID_FREQUENCIES = tuple(load_vocabulary_values("meta_question_frequencies_vocabulary.yaml"))
VALID_ORIGINS = tuple(load_vocabulary_values("meta_question_origins_vocabulary.yaml"))

# data_sources 白名单：仓内表名（W4/W5 文档出现）+ DS-* 键（W4 §1-§2）+ W4 B 档渠道名
ALLOWED_SOURCES = frozenset(
    {
        # DS 键
        "DS-MINIQMT",
        "DS-TUSHARE",
        "DS-BAOSTOCK",
        "DS-TDX",
        "DS-TICKFLOW",
        "DS-BAIDUYUN",
        "DS-TQCENTER",
        "DS-AKSHARE",
        "DS-AKSHARE-ALT",
        "DS-CLS",
        "DS-EASTMONEY_NEWS",
        "DS-RSS",
        "DS-FRED",
        "DS-EIA",
        "DS-QWEATHER",
        "DS-EASTMONEY_DATACENTER",
        "DS-IRM",
        "DS-HYPERLIQUID",
        "DS-IO_TABLE",
        # 仓内表名（行情/估值/资金流/tick）
        "kline_daily",
        "tick_data",
        "daily_valuation",
        "money_flow",
        "stock_daily_basic",
        # 仓内表名（图谱域 ig_* / entity / concept / CH 股东）
        "ig_chain",
        "ig_node",
        "ig_edge",
        "ig_company_edge",
        "ig_node_company",
        "ig_product_revenue",
        "ig_fact",
        "ig_unlisted_entity",
        "ig_equity_edge",
        "ig_io_edge",
        "ig_document",
        "ig_chunk",
        "ig_entity_code_map",
        "stock_concept",
        "edge_holding",
        "fund_top10_shareholders",
        "fund_top10_circulating_shareholders",
        "fund_shareholder_count",
        "industry_class",
        "suppl",
        # 基建四件套 PG 表（meta_question schema，registry.py 建表真源）
        "meta_question.meta_question",
        "meta_question.meta_question_audit",
        "meta_question.meta_question_exam_result",
        # W4 §3 B 档渠道名
        "Copernicus Data Space Ecosystem",
        "Planet",
        "NWS API",
        "NOAA",
        "智联招聘",
        "Keepa",
        "中国政府采购网",
        "全国公共资源交易平台",
        "Reddit API",
        "X API",
        "雪球",
        "东方财富股吧",
        "七麦数据",
        "Sensor Tower",
        "UN Comtrade",
        "海关总署",
        "Mastercard SpendingPulse",
        "国家统计局社零",
    }
)

# 期望分布（机械加总自检）
EXPECT_TOTAL_RANGE = (280, 320)
EXPECT_ORIGIN = {"base62": 62, "template": 174, "manual": 41, "combo": 6}
EXPECT_LAYER = {"L0": 4, "L1": 200, "L2": 18, "L3": 20, "L4": 18, "L5": 14, "L6": 9}
EXPECT_BASE62 = {"M": 4, "U": 6, "SP": 20, "S": 12, "D": 8, "E": 7, "G": 5}
EXPECT_GRF_GRAPH = {"G1": 4, "G2": 3, "G3": 4, "G4": 4, "G5": 3}
EXPECT_EXT_LAYER = {"L3": 8, "L4": 6, "L5": 5, "L6": 4}
U_LINES_26 = {"SL-A%02d" % i for i in range(1, 17)} | {"SL-B%02d" % i for i in range(1, 11)}
COMBO_LINES_6 = {"SL-A01", "SL-A02", "SL-A03", "SL-A04", "SL-A05", "SL-A06"}
SELECTED_10 = {"SL-A01", "SL-A03", "SL-A09", "SL-A16", "SL-A02", "SL-A05", "SL-A04", "SL-A06", "SL-A13", "SL-A15"}


def normalize_title(title):
    """对齐 registry.normalize_title：NFKC→小写→去空白→去标点。"""
    text = unicodedata.normalize("NFKC", str(title or ""))
    return "".join(ch for ch in text.lower() if not ch.isspace() and not unicodedata.category(ch).startswith("P"))


class _BatchStats:
    """逐条校验累计器（查重台账/分组计数/骨架计数；字段序对齐拆分前 main() 局部变量）。"""

    def __init__(self):
        """__init__ implementation."""
        self.seen_titles = {}
        self.base62_counter = Counter()
        self.origin_counter = Counter()
        self.layer_counter = Counter()
        self.freq_counter = Counter()
        self.u_exp_per_line = Counter()
        self.combo_per_line = Counter()
        self.grf_per_graph = Counter()
        self.ext_per_layer = Counter()
        self.base_id_seen = set()
        self.n_u_tpl = 0
        self.n_combo_space = 0
        self.n_grf = 0
        self.n_ext = 0
        self.n_combo = 0
        self.n_base62 = 0


def _load_batch(path):
    """载入批次 YAML（纯读零写入）；载入失败返回 fatal 文案（调用方打印后 RC=1）。"""
    try:
        with path.open("r", encoding="utf-8") as fh:
            return yaml.safe_load(fh), None
    except Exception as exc:  # noqa: BLE001
        return None, "FATAL: cannot load %s -> %s" % (path, exc)


def _validate_head(q, tag, seen_titles, bad):
    """头部校验：dict 类型 + title 存在/问句形/归一化非空/查重。

    返回 False=头部失败已记违规，该条后续校验跳过（对齐拆分前 continue 短路）。
    """
    if not isinstance(q, dict):
        bad("type", "%s not dict" % tag)
        return False
    title = q.get("title")
    if not isinstance(title, str) or not title.strip():
        bad("field_missing:title", tag)
        return False
    if not title.endswith("？"):
        bad("title_not_question", "%s %s" % (tag, title[:40]))
    norm = normalize_title(title)
    if not norm:
        bad("title_empty_norm", tag)
    if norm in seen_titles:
        bad("dup_title", "%s 与 %s 归一化重复：%s" % (tag, seen_titles[norm], title[:40]))
    else:
        seen_titles[norm] = tag
    return True


def _validate_enums(q, tag, bad):
    """枚举机检：layer / frequency（对齐 registry.py 枚举真源）。"""
    layer = q.get("layer")
    if layer not in VALID_LAYERS:
        bad("layer_invalid", "%s %r" % (tag, layer))
    freq = q.get("frequency")
    if freq not in VALID_FREQUENCIES:
        bad("frequency_not_in_enum", "%s %r" % (tag, freq))


def _validate_data_sources(q, tag, bad):
    """data_sources：非空数组逐项非空 + 白名单（仓内表名/DS 键/W4 B 档渠道，禁编造）。"""
    ds = q.get("data_sources")
    if not isinstance(ds, list) or not ds or not all(isinstance(s, str) and s.strip() for s in ds):
        bad("data_sources_empty", "%s %r" % (tag, ds))
        return
    for s in ds:
        if s not in ALLOWED_SOURCES:
            bad("data_source_unknown", "%s %r（白名单外，禁编造）" % (tag, s))


def _validate_exam_plan(q, freq, tag, bad):
    """exam_plan：dict 结构 + criterion/threshold 完备（threshold 0 合法，禁 truthy）+ 禁占位符。

    event_driven 须事件源引用非空（A 级机检，R-20；对齐 registry 口径）。
    """
    plan = q.get("exam_plan")
    if not isinstance(plan, dict):
        bad("exam_plan_invalid", "%s not dict" % tag)
    else:
        criterion = str(plan.get("criterion") or "").strip()
        threshold = plan.get("threshold")
        threshold_ok = threshold is not None and str(threshold).strip() != ""
        if not criterion or not threshold_ok:
            bad("exam_plan_no_threshold", "%s %r" % (tag, plan))
        if "待定" in json.dumps(plan, ensure_ascii=False) or "后续补充" in json.dumps(plan, ensure_ascii=False):
            bad("exam_plan_placeholder", "%s 含待定/后续补充" % tag)
    if freq == "event_driven":
        esr = str((plan or {}).get("event_source_ref") or "").strip()
        if not esr:
            bad("event_source_ref_missing", "%s frequency=event_driven 无事件源引用" % tag)


def _validate_required_notes(q, tag, bad):
    """消费方/PIT/净零必填 + 禁预写字段（status/q_id 由 API 管控，批次禁写入）。"""
    cons = q.get("consumers")
    if not isinstance(cons, list) or not cons or not all(isinstance(c, str) and c.strip() for c in cons):
        bad("consumer_unresolvable", "%s %r" % (tag, cons))
    if not str(q.get("pit_proof") or "").strip():
        bad("pit_proof_missing", tag)
    if not str(q.get("net_zero_note") or "").strip():
        bad("net_zero_note_missing", tag)
    if "status" in q:
        bad("status_forbidden", "%s status 不应写入（API 默认 draft）" % tag)
    if q.get("q_id"):
        bad("qid_forbidden", "%s q_id 由 API 分配" % tag)


def _validate_provenance(q, tag, origin_counter, bad):
    """provenance：dict 结构 + batch_id 归属 + origin 枚举（合法 origin 计数）+ combo 须 space_hash。"""
    prov = q.get("provenance")
    if not isinstance(prov, dict):
        bad("provenance_invalid", "%s not dict" % tag)
        return
    if prov.get("batch_id") != BATCH_ID:
        bad("provenance_batch", "%s %r" % (tag, prov.get("batch_id")))
    origin = prov.get("origin")
    if origin not in VALID_ORIGINS:
        bad("origin_invalid", "%s %r" % (tag, origin))
    else:
        origin_counter[origin] += 1
    if origin == "combo" and not str(prov.get("space_hash") or "").strip():
        bad("space_hash_required", "%s origin=combo 无 space_hash" % tag)


def _accumulate_layers(q, stats):
    """layer/frequency 分组计数（layer 非法不入 layer 计数；frequency 全量计数）。"""
    layer = q.get("layer")
    if layer in VALID_LAYERS:
        stats.layer_counter[layer] += 1
    stats.freq_counter[q.get("frequency")] += 1


def _classify_base_id(q, tag, stats, bad):
    """base62 骨架 ID：去重 + M/U/SP/S/D/E/G 分组计数（SP 线特定须属 §5 勾选十线）。"""
    base_id = q.get("base_id")
    if not base_id:
        return
    if base_id in stats.base_id_seen:
        bad("base_id_dup", "%s %s" % (tag, base_id))
    stats.base_id_seen.add(base_id)
    stats.n_base62 += 1
    is_line_specific = base_id.count("-") == 2 and base_id.endswith(("x1", "x2"))
    if base_id.startswith("M"):
        stats.base62_counter["M"] += 1
    elif base_id.startswith("U"):
        stats.base62_counter["U"] += 1
    elif is_line_specific:
        stats.base62_counter["SP"] += 1
        if base_id.rsplit("-", 1)[0] not in SELECTED_10:
            bad("base_id_format", "%s %s（须 SL-xx-x1/x2 且属 §5 勾选十线）" % (tag, base_id))
    elif base_id.startswith("S"):
        stats.base62_counter["S"] += 1
    elif base_id.startswith("D"):
        stats.base62_counter["D"] += 1
    elif base_id.startswith("E"):
        stats.base62_counter["E"] += 1
    elif base_id.startswith("G"):
        stats.base62_counter["G"] += 1
    else:
        bad("base_id_format", "%s %s（未知骨架 ID 格式）" % (tag, base_id))


def _accumulate_groups(q, stats):
    """骨架分组计数：U 族展开 / 线×窗组合 / 图谱问 / 扩展问 / 组合层新问。"""
    layer = q.get("layer")
    prov = q.get("provenance")
    line_ref = q.get("line_ref")
    graph_ref = q.get("graph_ref")
    tpl = (prov or {}).get("tpl") if isinstance(prov, dict) else None
    space_hash = (prov or {}).get("space_hash") if isinstance(prov, dict) else None
    origin = (prov or {}).get("origin") if isinstance(prov, dict) else None

    if origin == "template" and tpl == "TPL-U-001@1.0.0":
        stats.n_u_tpl += 1
        stats.u_exp_per_line[line_ref] += 1
    if space_hash == "lines6×wins3":
        stats.n_combo_space += 1
        stats.combo_per_line[line_ref] += 1
    if graph_ref:
        stats.n_grf += 1
        stats.grf_per_graph[graph_ref] += 1
    elif origin == "manual":
        stats.n_ext += 1
        stats.ext_per_layer[layer] += 1
    if origin == "combo":
        stats.n_combo += 1


def _validate_one(q, tag, stats, bad):
    """单条全项校验（阶段顺序=拆分前循环体，违规追加序逐字节稳定）。"""
    if not _validate_head(q, tag, stats.seen_titles, bad):
        return
    _validate_enums(q, tag, bad)
    _validate_data_sources(q, tag, bad)
    freq = q.get("frequency")
    _validate_exam_plan(q, freq, tag, bad)
    _validate_required_notes(q, tag, bad)
    _validate_provenance(q, tag, stats.origin_counter, bad)
    _accumulate_layers(q, stats)
    _classify_base_id(q, tag, stats, bad)
    _accumulate_groups(q, stats)


def _validate_questions(questions, stats, bad):
    """逐条校验循环。"""
    for idx, q in enumerate(questions):
        _validate_one(q, "q[%d]" % idx, stats, bad)


def _compare_distributions(questions, stats, bad):
    """总量区间 + origin/layer/base62 分布对账（机械加总自检）。"""
    total = len(questions)
    lo, hi = EXPECT_TOTAL_RANGE
    if not (lo <= total <= hi):
        bad("total_out_of_range", "total=%d 不在 [%d,%d]" % (total, lo, hi))
    for grp, exp in EXPECT_ORIGIN.items():
        if stats.origin_counter[grp] != exp:
            bad("origin_count", "%s=%d 期望 %d" % (grp, stats.origin_counter[grp], exp))
    for lay, exp in EXPECT_LAYER.items():
        if stats.layer_counter[lay] != exp:
            bad("layer_count", "%s=%d 期望 %d" % (lay, stats.layer_counter[lay], exp))
    for grp, exp in EXPECT_BASE62.items():
        if stats.base62_counter[grp] != exp:
            bad("base62_count", "%s 组=%d 期望 %d" % (grp, stats.base62_counter[grp], exp))


def _compare_skeleton(stats, bad):
    """骨架对账入口（COMPLEXITY 拆分：上半 U 族/组合窗，下半 图谱/扩展/组合；顺序即对账序）。"""
    _compare_expansion(stats, bad)
    _compare_graph_ext(stats, bad)


def _compare_expansion(stats, bad):
    """骨架对账上半：base62 总量 / U 族 26 线×6 / 组合窗 6 线×3。"""
    if stats.n_base62 != 62:
        bad("base62_total", "base_id 非空条目=%d 期望 62" % stats.n_base62)
    if stats.n_u_tpl != 156:
        bad("u_expansion_total", "TPL-U-001 展开件=%d 期望 156" % stats.n_u_tpl)
    for line in sorted(U_LINES_26):
        if stats.u_exp_per_line[line] != 6:
            bad("u_expansion_line", "%s U 族=%d 期望 6" % (line, stats.u_exp_per_line[line]))
    extra_u = set(stats.u_exp_per_line) - U_LINES_26
    if extra_u:
        bad("u_expansion_extra_lines", sorted(extra_u))
    if stats.n_combo_space != 18:
        bad("combo_window_total", "lines6×wins3 空间件=%d 期望 18（禁事后扩空间）" % stats.n_combo_space)
    for line in sorted(COMBO_LINES_6):
        if stats.combo_per_line[line] != 3:
            bad("combo_window_line", "%s 窗口件=%d 期望 3" % (line, stats.combo_per_line[line]))


def _compare_graph_ext(stats, bad):
    """骨架对账下半：图谱 18（含未知 graph_ref）/ 扩展 23 分层 / 组合层新问 6。"""
    if stats.n_grf != 18:
        bad("grf_total", "graph_ref 非空=%d 期望 18（GRF1-GRF18）" % stats.n_grf)
    for g, exp in EXPECT_GRF_GRAPH.items():
        if stats.grf_per_graph[g] != exp:
            bad("grf_graph_count", "%s=%d 期望 %d" % (g, stats.grf_per_graph[g], exp))
    if stats.n_ext != 23:
        bad("ext_total", "扩展问=%d 期望 23" % stats.n_ext)
    for lay, exp in EXPECT_EXT_LAYER.items():
        if stats.ext_per_layer[lay] != exp:
            bad("ext_layer_count", "扩展 %s=%d 期望 %d" % (lay, stats.ext_per_layer[lay], exp))
    if stats.n_combo != 6:
        bad("combo_total", "origin=combo=%d 期望 6" % stats.n_combo)
    unknown_graph = set(stats.grf_per_graph) - set(EXPECT_GRF_GRAPH)
    if unknown_graph:
        bad("graph_ref_unknown", sorted(unknown_graph))


def _report(path, questions, stats, violations):
    """统计报告 + 违规清单（违规=0 才 RC=0）。返回退出码。"""
    total = len(questions)
    lo, hi = EXPECT_TOTAL_RANGE
    print("=" * 72)
    print("check_w6_batch | %s" % path)
    print("=" * 72)
    print("总条数: %d（目标区间 [%d,%d]）" % (total, lo, hi))
    print("origin 分布: %s" % dict(sorted(stats.origin_counter.items())))
    print("layer 分布: %s" % dict(sorted(stats.layer_counter.items())))
    print("frequency 分布: %s" % dict(sorted(stats.freq_counter.items())))
    print("base62 分组: %s（合计 %d）" % (dict(sorted(stats.base62_counter.items())), stats.n_base62))
    print("U 族展开: %d 条 / %d 线（每线 6）" % (stats.n_u_tpl, len(stats.u_exp_per_line)))
    print("线×窗组合: %d 条（space_hash=lines6×wins3，6 线×3 窗）" % stats.n_combo_space)
    print("图谱问: %d 条 %s" % (stats.n_grf, dict(sorted(stats.grf_per_graph.items()))))
    print("扩展问: %d 条 %s" % (stats.n_ext, dict(sorted(stats.ext_per_layer.items()))))
    print("组合层新问: %d 条（space_hash=cmb-e1c-v1）" % stats.n_combo)
    print("-" * 72)
    if violations:
        print("违规 %d 条:" % len(violations))
        for v in violations:
            print("  " + v)
        return 1
    print("违规=0（字段完备/枚举合法/data_sources 白名单/查重零重复/分布全对账）")
    return 0


def main():
    """Entry point: parse args, run logic, return exit code."""
    here = Path(__file__).resolve()
    default_path = (
        here.parents[2] / "docs" / "_working" / "chain_piling_campaign" / "snapshots" / "question_batch_w6.yaml"
    )
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else default_path

    # ---- 载入 ----
    data, fatal = _load_batch(path)
    if fatal is not None:
        print(fatal)
        return 1
    questions = data.get("questions")
    if not isinstance(questions, list) or not questions:
        print("FATAL: no questions array")
        return 1

    violations = []

    def bad(code, detail):
        """bad implementation."""
        violations.append("[%s] %s" % (code, detail))

    if data.get("batch_id") != BATCH_ID:
        bad("batch_id", "top-level batch_id=%r != %s" % (data.get("batch_id"), BATCH_ID))

    # ---- 逐条校验 + 总量与分布自检 ----
    stats = _BatchStats()
    _validate_questions(questions, stats, bad)
    _compare_distributions(questions, stats, bad)
    _compare_skeleton(stats, bad)

    # ---- 报告 ----
    return _report(path, questions, stats, violations)


if __name__ == "__main__":
    sys.exit(main())
