#!/usr/bin/env python
# [BLUEPRINT] MOD-GOV_SCRIPTS
# [MODULE] scripts.governance.harvest_candidates_from_drafts
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.shared.infra.process_pool; zephyr.shared.io.file_utils; scripts.governance.extract_depgraph
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 双注册表幂等（existing_harvest_keys候选库+existing_translation_keys翻译真源+max_harvest_seq扫描双注册表防seq碰撞）; 追加写入走 safe_write_text CAS（base 陈旧拒写防吞并发追加）
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=成功; exit 1=参数错误/无新候选
# [TESTS]
# [A_module] module_id=MOD-GOV_SCRIPTS | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
从场外草稿 CSV 抓取候选模块入候选库（一次性 harvest 脚本，不进 generators/）。

输入:
  - d:\\临时工作区\\extracted_modules\\merged_all_modules_final.csv (能力+模块类)
  - depgraph (extract_depgraph 拉各域 path 做去重/域校准)

输出:
  - candidate_module_registry.yaml 追加候选条目 (status=candidate, design_admission=pending)
  - module_translation_registry.yaml 追加 plain_zh 条目 (key=候选ID)

策略: 分域批处理 + 启发式四态去重 (likely_new/likely_implemented/likely_planned/likely_misplaced) + 跨域校准

去重四态（区分运营态/设计态，2026-08-01 治本）:
  - likely_new         该域 depgraph 无 path 命中，疑真候选
  - likely_implemented 该域运营态(stable/generated)path 命中关键词，疑已实现
  - likely_planned     该域设计态(planned)path 命中关键词，已在 depgraph 设计管道，勿重复登记
  - likely_misplaced   含 infra 通用词且域错标，已校准到 D_INFRA_RUNTIME

用法:
  python scripts/governance/harvest_candidates_from_drafts.py --domain D-CROSS-ASSET   # 试点单域
  python scripts/governance/harvest_candidates_from_drafts.py --domain D-CROSS-ASSET --dry-run  # 只看不写
  python scripts/governance/harvest_candidates_from_drafts.py --all   # 全量 (试点确认后用)
"""

from __future__ import annotations

__manifest__ = """
args: [--domain, --all, --dry-run]
description: '从场外草稿CSV抓取候选模块入候选库+翻译真源（双注册表幂等去重）'
dimensions:
- D5
priority: P2
timeout_seconds: 300
warn_only: false
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path

from zephyr.shared.infra.process_pool import run_subprocess_hidden

REPO = Path(r"d:\ZephyrAlpha")
CSV_PATH = Path(r"d:\临时工作区\extracted_modules\merged_all_modules_final.csv")
CANDIDATE_YAML = REPO / "docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml"
TRANSLATION_YAML = REPO / "docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml"
EXTRACT = REPO / "scripts/governance/extract_depgraph.py"

TODAY = "2026-08-01"
NEXT_REVIEW = "2026-11-30"


def run_extract(args: list[str]) -> dict:
    """跑 extract_depgraph.py，返回解析后的 JSON。"""
    r = run_subprocess_hidden(
        [sys.executable, str(EXTRACT)] + args,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(r.stdout)


def load_csv(domain_filter: str | None) -> list[dict]:
    """读 CSV，过滤能力+模块类。domain_filter 为横杠域名（D-CROSS-ASSET）。"""
    items = []
    with open(CSV_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("功能类型") not in ("能力", "模块"):
                continue
            if domain_filter and row.get("所属域", "").strip() != domain_filter:
                continue
            items.append(row)
    return items


# build_status 三态分类（TRAE-062 架构数据真源=depgraph）
# 运营态：已落代码（stable=稳定运行 / generated=已生成骨架）
# 设计态：已登记 depgraph 设计态但未实现（planned）
# 弃用态：已退役（deprecated），命中也不算"已实现"
OPERATIONAL_STATUS = {"stable", "generated"}
DESIGN_STATUS = {"planned"}


def load_all_paths() -> tuple[dict[str, list[str]], dict[str, str], dict[str, str]]:
    """拉所有非空域 path + 每条 path 的 build_status。

    返回:
        domain_paths: {domain: [paths]}        —— 按域分组的 path 列表
        path_to_domain: {path: domain}          —— path → 所属域
        path_to_status: {path: build_status}    —— path → build_status(stable/generated/planned/deprecated)
    """
    summary = run_extract(["--summary"])
    domain_paths: dict[str, list[str]] = {}
    path_to_domain: dict[str, str] = {}
    path_to_status: dict[str, str] = {}
    for d in summary.get("domains", []):
        if d.get("module_count", 0) == 0:
            continue
        dom = d["domain"]
        data = run_extract(["--domains", dom])
        dom_data = data.get(dom, {})
        for it in dom_data.get("items", []):
            p = it.get("path", "")
            if p:
                domain_paths.setdefault(dom, []).append(p)
                path_to_domain[p] = dom
                path_to_status[p] = it.get("build_status", "unknown")
    return domain_paths, path_to_domain, path_to_status


def dash_to_under(d: str) -> str:
    """D-FACTOR → D_FACTOR"""
    return (d or "").replace("-", "_").strip()


def extract_keywords(name: str) -> list[str]:
    """'CurrencyHedger 货币对冲' → ['currency', 'hedger']（驼峰拆分）"""
    en = re.sub(r"[^\x00-\x7f]+", " ", name)
    tokens = re.split(r"[^a-zA-Z0-9]+", en)
    words = []
    for t in tokens:
        if not t:
            continue
        # 驼峰拆分 CurrencyHedger → Currency, Hedger；CrossMarket → Cross, Market
        parts = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)|\d+", t)
        words.extend(p.lower() for p in parts)
    return [w for w in words if len(w) >= 3]


def split_name(name: str) -> tuple[str, str, str]:
    """'Multi-Market Data Router 多市场数据路由' → (en, zh, name_en_slug)"""
    en = re.sub(r"[\u4e00-\u9fff\uff00-\uffef]+", " ", name).strip()
    en = re.sub(r"\s+", " ", en)
    zh = re.sub(r"[a-zA-Z0-9_\-/&.()]+", " ", name)
    zh = re.sub(r"\s+", "", zh).strip()
    slug = re.sub(r"[^a-z0-9]+", "_", en.lower()).strip("_")
    return en, zh, slug


INFRA_KEYWORDS = {
    "config",
    "health",
    "logger",
    "audit",
    "metric",
    "metrics",
    "scheduler",
    "retry",
    "circuit",
    "breaker",
    "task",
}
INFRA_DOMAINS = {"D_INFRA_RUNTIME", "D_INFRA_OPS", "D_OPS", "D_GOV_AUDIT"}  # noqa: gate-vocab — 基础设施域名单系治理域判定集合，属词表豁免合法场景


def heuristic_dedup(
    item: dict,
    domain_paths: dict,
    path_to_domain: dict,
    path_to_status: dict | None = None,
) -> tuple[str, str, str]:
    """返回 (likely_status, recommended_domain, matched_status_detail)。

    策略（区分运营态/设计态，2026-08-01 治本用户提出的"运营态和设计态已有"问题）:
    - 同域 path 命中关键词：
        * 命中 stable/generated → likely_implemented（运营态已有，已落代码）
        * 命中 planned         → likely_planned（设计态已有，已在 depgraph 设计管道，勿重复登记）
        * 多 path 命中取"更已实现"者优先（operational > planned）
    - 含 infra 通用词(config/health/logger/audit...)但不在 infra 域 → likely_misplaced(推荐 D_INFRA_RUNTIME)
    - 其余该域无命中 → likely_new
    跨域全搜索假阳率高(通用词组合必然命中),已弃用。域校准留人工。

    matched_status_detail: 命中 path 的 build_status 明细（如 "stable" / "planned" / ""未命中"），
    供 tech_notes 记录，便于人工复核。
    """
    dom = dash_to_under(item.get("所属域", ""))
    kws = extract_keywords(item.get("功能名称", ""))
    if not kws:
        return "uncertain", dom, ""
    own_paths = domain_paths.get(dom, [])
    # 同域命中只算非 __init__ 的真实模块 path（排除骨架目录名假阳）
    own_real_paths = [p for p in own_paths if "__init__" not in p]
    if own_real_paths:
        matched_statuses = []
        for kw in kws:
            for p in own_real_paths:
                if kw in p.lower():
                    matched_statuses.append((path_to_status or {}).get(p, "unknown"))
        if matched_statuses:
            # 优先级：运营态 > 设计态 > 其他。取"最已实现"的状态代表。
            if any(s in OPERATIONAL_STATUS for s in matched_statuses):
                return "likely_implemented", dom, "operational(" + ",".join(sorted(set(matched_statuses))) + ")"
            if any(s in DESIGN_STATUS for s in matched_statuses):
                return "likely_planned", dom, "planned(" + ",".join(sorted(set(matched_statuses))) + ")"
            # 命中但状态非运营/设计（如 deprecated/unknown）——记录但不算"已实现"
            return "likely_new", dom, "matched_but_" + ",".join(sorted(set(matched_statuses)))
    # 轻量错标识别：infra 通用词出现在非 infra 域
    if (set(kws) & INFRA_KEYWORDS) and dom not in INFRA_DOMAINS:
        return "likely_misplaced", "D_INFRA_RUNTIME", ""
    return "likely_new", dom, ""


def existing_harvest_keys() -> set[str]:
    """从候选库 YAML 提取已登记 harvest 候选的幂等键集合 (original_id@source_draft)。

    治本(2026-08-01): 原 existing_ids() 用正则提取裸 original_id，但 dedup_key
    是 "orig_id@src" 格式——两者永不匹配，导致幂等失效、重复登记。
    改为 yaml.safe_load 正规解析，提取每条 CAND-HARVEST* 条目的 original_id+source_draft。
    """
    import yaml

    if not CANDIDATE_YAML.exists():
        return set()
    with open(CANDIDATE_YAML, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    keys: set[str] = set()
    for e in data.get("entries", []) or []:
        if not str(e.get("id", "")).startswith("CAND-HARVEST"):
            continue
        oid = (e.get("original_id") or "").strip()
        src = (e.get("source_draft") or "").strip()
        if oid:
            keys.add(f"{oid}@{src}")
    return keys


def max_harvest_seq() -> int:
    """已存在的 CAND-HARVEST-XXXX 最大序号（YAML 解析，避免正则误匹配注释）。

    治本(2026-08-01 seq 碰撞): 同时扫描候选库 + 翻译真源两个 YAML，取两者最大值。
    原实现只扫候选库——若候选库因 stash/restore 丢失但翻译真源残留，seq 从 0
    重新分配会导致 CAND-HARVEST-0001 等序号与翻译真源残留条目碰撞，产生
    "同 key 不同内容"的脏重复（见 #ARCH-TRANSLATION-DUP-001）。
    """
    import yaml

    seqs: list[int] = []
    for ypath in (CANDIDATE_YAML, TRANSLATION_YAML):
        if not ypath.exists():
            continue
        with open(ypath, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        key = "id" if ypath == CANDIDATE_YAML else "module_path"
        for e in data.get("entries", []) or []:
            cid = str(e.get(key, ""))
            if cid.startswith("CAND-HARVEST-"):
                try:
                    seqs.append(int(cid.split("-")[-1]))
                except ValueError:
                    pass
    return max(seqs) if seqs else 0


def existing_translation_keys() -> set[str]:
    """翻译真源中已存在的 CAND-HARVEST module_path 集合（幂等去重）。

    治本(2026-08-01): 原脚本只对候选库做幂等检查（existing_harvest_keys），
    翻译真源无去重——重跑时若候选库丢失但翻译真源残留，会追加重复翻译条目。
    新增此函数使翻译真源也具备幂等能力：已存在的 CAND-HARVEST-xxxx 跳过追加。
    """
    import yaml

    if not TRANSLATION_YAML.exists():
        return set()
    with open(TRANSLATION_YAML, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    keys: set[str] = set()
    for e in data.get("entries", []) or []:
        mp = str(e.get("module_path", ""))
        if mp.startswith("CAND-HARVEST-"):
            keys.add(mp)
    return keys


def yaml_str(s: str) -> str:
    """YAML 字符串安全引用。"""
    s = (s or "").strip().replace('"', "'")
    return f'"{s}"'


# likely_status → tech_notes 后缀查表（拆出自 build_candidate_entry 降圈复杂度 16→12）
_LIKELY_TECH_SUFFIX: dict[str, str] = {
    "likely_implemented": " 该域运营态path命中关键词, 疑已实现;",
    "likely_planned": " 该域设计态path命中关键词, 已在depgraph设计管道, 勿重复登记;",
    "likely_new": " 该域无运营态/设计态path命中, 疑真候选;",
}


def _likely_tech_suffix(likely: str, orig_dom: str, rec_domain: str) -> str:
    """生成 likely_status 对应的 tech_notes 后缀文本。"""
    if likely == "likely_misplaced":
        return f" 疑似域错标(原{orig_dom}→校准{rec_domain}), 跨域path命中;"
    return _LIKELY_TECH_SUFFIX.get(likely, "")


def build_candidate_entry(
    item: dict,
    seq: int,
    likely: str,
    rec_domain: str,
    dom_paths: dict,
    matched_detail: str = "",
) -> tuple[str, str]:
    """生成候选 YAML 条目文本 + 翻译条目文本。返回 (candidate_block, translation_block)。"""
    cid = f"CAND-HARVEST-{seq:04d}"
    name = item.get("功能名称", "").strip()
    en, zh, slug = split_name(name)
    orig_dom = dash_to_under(item.get("所属域", ""))
    domain_for_entry = rec_domain if likely == "likely_misplaced" else orig_dom
    domain_status = "skeleton" if len(dom_paths.get(domain_for_entry, [])) < 10 else "active"
    domain_node_count = len(dom_paths.get(domain_for_entry, []))
    orig_id = item.get("原始ID", "").strip()
    src = item.get("源文件", "").strip()
    src_line = item.get("源行号", "").strip()
    ctx = item.get("上下文", "").strip()
    ftype = item.get("功能类型", "").strip()
    kws = extract_keywords(name)

    cap = orig_id if orig_id.upper().startswith("C-") or orig_id.upper().startswith("SKILL") else ""
    tech = f"harvest来源:{src}; 类型={ftype}; likely_status={likely}; depgraph该域节点数={domain_node_count};"
    if matched_detail:
        tech += f" 命中build_status={matched_detail};"
    tech += _likely_tech_suffix(likely, orig_dom, rec_domain)

    tags = ["harvest", likely, ftype]
    if likely == "likely_misplaced":
        tags.append("域错标存疑")

    # 候选条目
    cand = []
    cand.append(f"- id: {cid}")
    cand.append(f"  name: {yaml_str(name)}")
    cand.append(f"  aliases: [{yaml_str(orig_id)[1:-1] if orig_id else ''}]")
    cand.append(f"  domain: {domain_for_entry}")
    cand.append(f"  domain_status: {domain_status}")
    cand.append(f"  domain_node_count: {domain_node_count}")
    cand.append("  panorama_position:")
    cand.append("    depgraph:")
    cand.append("      has_position: false")
    cand.append(f"  description: {yaml_str(name + '（来源: ' + src + '）')}")
    cand.append(f"  capability: {yaml_str(cap)}")
    cand.append(f"  problem_it_solves: {yaml_str(ctx[:120] if ctx else 'harvest待评估')}")
    cand.append("  trigger_signals: []")
    cand.append(f"  keywords: {kws}")
    cand.append("  design_admission:")
    cand.append("    q1_implemented: pending")
    cand.append("    blocking_question: pending")
    cand.append("  status: candidate")
    cand.append("  priority: P2")
    cand.append(f"  created_at: '{TODAY}'")
    cand.append(f"  last_reviewed_at: '{TODAY}'")
    cand.append(f"  source_draft: {yaml_str(src)}")
    cand.append(f"  source_section: 'L{src_line}'")
    cand.append(f"  original_id: {yaml_str(orig_id)}")
    cand.append("  estimated_complexity: M")
    cand.append(f"  tech_notes: {yaml_str(tech)}")
    cand.append(f"  tags: {tags}")
    cand.append("  alternatives: ''")
    cand.append(f"  next_review_date: '{NEXT_REVIEW}'")
    cand.append("  review_frequency: quarterly")
    cand.append(f"  last_review_outcome: 'harvest待评估（{likely}）'")

    # 翻译条目（翻译真源列表项为顶格 - module_path:）
    trans = []
    trans.append(f"- module_path: {cid}")
    trans.append(f"  domain_id: {domain_for_entry}")
    trans.append(f"  name_zh: {yaml_str(zh or name)}")
    trans.append(f"  name_en: {yaml_str(slug or en)}")
    trans.append(f"  desc_zh: {yaml_str('harvest来源:' + src)}")
    trans.append("  desc_en: ''")
    trans.append(f"  plain_zh: {yaml_str(name + '（来源:' + src + ', ' + likely + '）')}")

    # 候选库 entries 项是2空格缩进（  - id:），给候选 block 每行加2空格前缀
    cand_block = "\n".join(("  " + ln) if ln else ln for ln in cand)
    return cand_block, "\n".join(trans)


def append_to_file(path: Path, block: str) -> None:
    """追加 YAML 块到文件末尾（保注释，不重写）。

    CAS 接入（2026-08-23 陈旧快照覆写事故治本）：base=追加前读到的原文，
    磁盘已被他人推进即 StaleWriteRefused 拒写不落盘，防吞并发追加；
    newline="\\n" 保 .gitattributes eol=lf 行尾约定（原 open("a") 文本模式
    在 Windows 写出 CRLF，随本写入一并归一到 LF）。
    """
    from zephyr.shared.io.file_utils import content_sha256, safe_write_text  # noqa: PLC0415

    base = path.read_text(encoding="utf-8")
    sep = "" if base.endswith("\n") else "\n"
    safe_write_text(
        path,
        base + sep + block + "\n",
        expected_base_sha256=content_sha256(base),
        repo_root=REPO,
        newline="\n",
    )


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", help="只处理指定域（横杠格式，如 D-CROSS-ASSET）")
    ap.add_argument("--all", action="store_true", help="全量处理所有域")
    ap.add_argument("--dry-run", action="store_true", help="只统计不写文件")
    args = ap.parse_args()

    if not args.domain and not args.all:
        print("[ERR] 必须指定 --domain 或 --all")
        return 1

    print("[1/4] 加载 depgraph 所有域 path + build_status（运营态/设计态去重基准）...")
    domain_paths, path_to_domain, path_to_status = load_all_paths()
    # 统计运营态/设计态 path 数量，给用户可见信号
    op_cnt = sum(1 for s in path_to_status.values() if s in OPERATIONAL_STATUS)
    des_cnt = sum(1 for s in path_to_status.values() if s in DESIGN_STATUS)
    print(
        f"      非空域 {len(domain_paths)} 个，总 path {len(path_to_domain)} 条（运营态 {op_cnt} / 设计态 {des_cnt}）"
    )

    print("[2/4] 加载 CSV 候选项...")
    items = load_csv(args.domain)
    print(f"      能力+模块类候选项 {len(items)} 条（domain={args.domain or 'ALL'}）")

    print("[3/4] 去重 + 域校准（区分运营态/设计态）...")
    existing = existing_harvest_keys()
    existing_trans = existing_translation_keys()  # 治本: 翻译真源幂等
    seq = max_harvest_seq()
    stats = {
        "likely_new": 0,
        "likely_implemented": 0,
        "likely_planned": 0,
        "likely_misplaced": 0,
        "uncertain": 0,
        "skipped": 0,
        "trans_skipped": 0,
    }
    cand_blocks = []
    trans_blocks = []
    for item in items:
        orig_id = item.get("原始ID", "").strip()
        src = item.get("源文件", "").strip()
        # 幂等：同 original_id + src 视为已登记
        dedup_key = f"{orig_id}@{src}"
        if dedup_key in existing:
            stats["skipped"] += 1
            continue
        likely, rec_dom, matched_detail = heuristic_dedup(item, domain_paths, path_to_domain, path_to_status)
        stats[likely] += 1
        seq += 1
        cb, tb = build_candidate_entry(item, seq, likely, rec_dom, domain_paths, matched_detail)
        cand_blocks.append(cb)
        # 翻译幂等：若 CAND-HARVEST-xxxx 已存在于翻译真源，跳过追加（防脏重复）
        cid = f"CAND-HARVEST-{seq:04d}"
        if cid in existing_trans:
            stats["trans_skipped"] += 1
        else:
            trans_blocks.append(tb)
            existing_trans.add(cid)
        existing.add(dedup_key)

    print(f"      去重统计: {stats}")
    print(f"      新增候选: {len(cand_blocks)} 条，新增翻译: {len(trans_blocks)} 条")

    if args.dry_run:
        print("[DRY-RUN] 不写文件。前3条候选预览:")
        for b in cand_blocks[:3]:
            print(b + "\n---")
        return 0

    if not cand_blocks:
        print("[4/4] 无新候选需登记。")
        return 0

    print(f"[4/4] 追加 {len(cand_blocks)} 条到候选库 + 翻译真源...")
    append_to_file(CANDIDATE_YAML, "\n".join(cand_blocks))
    if trans_blocks:
        append_to_file(TRANSLATION_YAML, "\n".join(trans_blocks))
    print(f"[OK] 完成。候选库+{len(cand_blocks)}，翻译真源+{len(trans_blocks)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
