# [BLUEPRINT] MOD-AUTO-L3-002 | docs/_working/automation/campaign/blueprints/intel_harvester_blueprint.md | §
# [PROVISIONAL] 暂编号：docs/03_modules 解冻后按注册表重编（挂单 H-01）
# [MODULE] scripts.automation.source_card_drafter
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.backtest.lane_g_stomach_intake (parse_inbox_entries 委托复用);
#   zephyr.integration.local_model.ollama_chat（内嵌 LSG）; zephyr.shared.io.file_utils.safe_write_text; yaml
# [CONSUMERS] docs/_working/automation/inbox/intel-*.md（上游=本工段①收件箱）;
#   config/source_cards/drafts/<source_id>_draft.yaml（下游=工段③ onboard_source 流水线的人工确认料）;
#   docs/_working/automation/campaign/mining/01_数据源发现/工段作业簿.md §5-6 / §10 WO-①-05
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 草案红线：只产 draft 不生效——产出仅落 config/source_cards/drafts/（正式目录只读，
#   生效必须人工确认后移入正式目录并走 onboard_source 流水线，Owner 门=intel_harvester 红线的终点站）;
#   本件不提供任何"直接生效/promote/上架"CLI 路径;
#   收件箱解析委托 lane_g.parse_inbox_entries（格式真源=render_inbox，防双真源，CLONEGUARD=委托勿克隆）;
#   LLM 特征抽取必经 OllamaChat（内嵌 LSG，宪法 §9.2）；不可达/回包损坏→降级模板卡（TODO 注释留痕）不炸;
#   source_id=名称 slug 确定性派生（同输入同文件名→重跑幂等，内容不变不重写）;
#   非数据源条目诚实跳过（is_data_source=false 不硬凑卡片，同车道 G"冰淇淋式巧合宁可不产"）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单条目 LLM 失败/解析损坏→该条目降级模板卡继续（不抛）；写盘失败记 failed 继续；
#   全部条目非数据源→ok 报告零草案（非错误）
# [TESTS] tests/automation/test_source_card_drafter.py
# [A_module] module_id=MOD-AUTO-L3-002 | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 操作员/会话按需调用的草案转化工具（人工确认门前置件），非进程内常驻服务
"""source_card_drafter — 源发现→源卡片草案转化器（WO-①-05，打通工段①→③产线轴）。

收件箱（docs/_working/automation/inbox/intel-*.md，人读 markdown）→ 条目解析（委托车道 G
解析器）→ 本地 LLM 抽取候选数据源特征（名称/URL/频次/类别假设）→ 渲染源卡片【草案】YAML 到
config/source_cards/drafts/<source_id>_draft.yaml（schema 对齐真卡 config/source_cards/fx_ecb.yaml
的 11 字段结构）。草案文件头恒带红线注释：生效必须人工确认后移入正式目录并走 onboard_source
流水线——本件绝不直接生效（上架决策=Owner 门）。

用法（仓库根，Python 3.12）：
    python scripts/automation/source_card_drafter.py run                # 全收件箱→草案
    python scripts/automation/source_card_drafter.py run --dry-run      # 只回看不写盘
    python scripts/automation/source_card_drafter.py run --limit 5      # 本班最多消化条目数
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))  # CLI 直跑（__main__）时 scripts.* 惰性导入需仓库根在径
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))  # zephyr.* 走 src 布局

from zephyr.shared.io.file_utils import safe_write_text  # noqa: E402  CAS 防并发覆盖
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  SSOT
from zephyr.shared.utils.time_utils import now_utc, now_utc_str  # noqa: E402  RULE-SCHEMA-TZ：禁 datetime.now()

_INBOX_DIR = REPO_ROOT / "docs" / "_working" / "automation" / "inbox"
_CARDS_DIR = REPO_ROOT / "config" / "source_cards"
_DRAFTS_DIR = _CARDS_DIR / "drafts"  # 草案唯一出口；正式目录 _CARDS_DIR 本件只读

MODEL = "qwen3:8b"
DRAFT_SUFFIX = "_draft.yaml"
DRAFT_BANNER = (
    "draft=仅供参考，生效必须人工确认后移入正式目录并走 onboard_source 流水线"
)

EXTRACTION_SYSTEM = (
    "你是数据源候选特征抽取器。输入是一篇研究情报（标题/链接/命中词/摘要）。"
    "判断它是否指向一个可作行情/另类数据供给的在线数据服务（免费 API/RSS/公开下载源）；"
    "普通论文思路本身不是数据源，严禁硬凑（冰淇淋销量式巧合宁可不产）。"
    "始终输出单个合法 JSON 对象，不要输出额外文本。"
)

_FREQ_SCHEDULE = {
    "daily": {"type": "daily", "time": "23:30"},
    "weekly": {"type": "weekly", "days": ["MON", "TUE", "WED", "THU", "FRI"], "time": "23:30"},
}


def build_extraction_prompt(entry: dict) -> str:
    """确定性抽取 prompt（同条目必同 prompt——重跑幂等的前提）。"""
    return (
        f"研究标题：{entry['title']}\n"
        f"链接：{entry['url']}\n"
        f"命中词：{'、'.join(entry.get('keywords') or []) or '（无）'}\n"
        f"摘要：{entry.get('summary', '')}\n"
        "该条目是否指向一个可上架的免费数据源？\n"
        '输出 JSON 对象：{"is_data_source": 布尔, "source_name": "数据源名称", '
        '"source_url": "数据访问 URL（http/https）", "frequency": "daily|weekly|monthly|unknown", '
        '"category": "类别假设如 宏观汇率/新闻情绪/另类数据", "notes": "合规或接入备注（≤80字）"}；'
        "不是数据源则输出 {\"is_data_source\": false, 其余字段留空}。"
    )


def slugify_source_id(name: str) -> str:
    """名称 → 确定性 source_id slug（小写字母数字+下划线，空名回退 src 占位）。"""
    s = re.sub(r"[^a-z0-9]+", "_", (name or "").lower()).strip("_")
    s = re.sub(r"_+", "_", s)[:48].strip("_")
    return s or "src"


def derive_source_id(name: str, url: str = "", taken: set[str] | None = None) -> str:
    """slug 同名冲突时按 url 指纹确定性消歧（同输入同结果，跨班稳定）。"""
    taken = taken if taken is not None else set()
    base = slugify_source_id(name)
    if base not in taken:
        return base
    fp = hashlib.md5(url.encode("utf-8")).hexdigest()[:6]
    cand = f"{base}_{fp}"
    n = 1
    while cand in taken:
        cand = f"{base}_{fp}_{n}"
        n += 1
    return cand


def _parse_source_json(raw: str) -> dict | None:
    """LLM 回包 → 第一个平衡花括号 JSON 对象（宽松截取，损坏返回 None）。"""
    if not raw or "{" not in raw:
        return None
    start = raw.index("{")
    depth = 0
    for i in range(start, len(raw)):
        if raw[i] == "{":
            depth += 1
        elif raw[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    obj = json.loads(raw[start:i + 1])
                except json.JSONDecodeError:
                    return None
                return obj if isinstance(obj, dict) else None
    return None


def _card_header(features: dict, entry: dict, *, mode: str, model: str) -> tuple[list[str], str, str, str, str]:
    """红线横幅+身份段；返回 (行, sid, task_name, url, notes)。"""
    name = str(features.get("source_name") or "").strip() or entry["title"]
    url = str(features.get("source_url") or "").strip()
    if not url.startswith(("http://", "https://")):
        url = entry["url"]  # LLM 给不出合法 URL → 回退条目链接（有据可查）
    notes = str(features.get("notes") or "").strip()[:200]
    sid = features.get("_source_id") or slugify_source_id(name)
    task_name = "ZephyrAlpha_" + "".join(w[:1].upper() + w[1:] for w in sid.split("_")[:4])
    lines = [
        f"# {DRAFT_BANNER}",
        f"# draft=模式 {mode} | 模型 {model} | 生成器 scripts/automation/source_card_drafter.py（重跑幂等：卡体零时间戳）",
        f"# draft=来源条目: {entry['title']} ({entry['url']})",
        f"source_id: {sid}",
        f'title: "{name}"',
    ]
    return lines, sid, task_name, url, notes


def _render_schedule_block(freq: str, sched_plan: dict) -> list[str]:
    """频次假设 → schedule YAML 块（查表驱动，未知频次整块留 TODO）。"""
    if not sched_plan:
        return [
            "schedule:  # TODO(人工确认): 频次未知，须人工定 type/days/time（先例 fx_ecb.yaml:8-11）",
            '  type: ""',
            "  days: []",
            '  time: ""',
        ]
    lines = ["schedule:"]
    for k, v in sched_plan.items():
        if isinstance(v, list):
            rendered = "[" + ", ".join(str(x) for x in v) + "]"
        else:
            rendered = json.dumps(str(v))  # JSON 标量=合法 YAML（safe_dump 标量会拖 "..." 文档尾）
        lines.append(f"  {k}: {rendered}  # TODO(人工确认): 频次假设={freq}")
    return lines


def _render_llm_body(sid: str, task_name: str, url: str, notes: str,
                     freq: str, sched_plan: dict) -> list[str]:
    """LLM 特征卡正文（TODO=人工确认位显式留痕）。"""
    lines = [
        'schema_module: ""  # TODO(人工确认): 对齐 schemas/categories/market/ 下 DDL 模块真源',
        f'table: "c1_market.{sid}"  # TODO(人工确认): 表名假设（c1_market 族惯例），以 DDL 模块为准',
        'ingest_script: ""  # TODO(人工确认): 需新写 provider/ingest 壳（先例 scripts/data/fx_ecb_ingest.py）',
        'ingest_args: ""  # TODO(人工确认): 回补参数（先例 "--days 7"）',
        f"task_name: {task_name}  # TODO(人工确认): Windows 任务命名",
    ]
    lines += _render_schedule_block(freq, sched_plan)
    lines += [
        "probe_days: 2  # TODO(人工确认): 沿用 fx_ecb 先例默认",
        "backfill_days: 30  # TODO(人工确认): 沿用 fx_ecb 先例默认",
        "compliance:",
        f"  source_url: {url}",
        f'  tos_note: "{notes or "TODO(人工确认): 数据许可/限频/鉴权情况待核"}"',
    ]
    return lines


def _render_template_body(url: str, category: str, keywords: list, notes: str) -> list[str]:
    """降级模板卡正文：全部关键字段留 TODO 注释，人工补齐后方可走 onboard_source。"""
    kw = "、".join(keywords or [])
    return [
        'schema_module: ""  # TODO(人工确认): LLM 不可达未能抽取，全部字段人工补齐',
        'table: ""  # TODO(人工确认): c1_market.<source_id> 假设待定',
        'ingest_script: ""  # TODO(人工确认): provider/ingest 壳待新写',
        'ingest_args: ""  # TODO(人工确认)',
        'task_name: ""  # TODO(人工确认)',
        "schedule:  # TODO(人工确认): 频次假设缺失（LLM 降级）",
        '  type: ""',
        "  days: []",
        '  time: ""',
        "probe_days: 2  # TODO(人工确认)",
        "backfill_days: 30  # TODO(人工确认)",
        "compliance:",
        f"  source_url: {url}",
        f'  tos_note: "TODO(人工确认): 类别线索={category or kw or "无"}；{notes or "许可/限频待核"}"',
    ]


def render_draft_card(features: dict, entry: dict, *, mode: str, model: str) -> str:
    """特征 → 草案 YAML 文本（11 字段对齐真卡 fx_ecb.yaml；文件头红线注释恒在）。

    mode="llm"=LLM 抽取特征；mode="template"=LLM 不可达/回包损坏的降级模板卡（字段留 TODO 注释）。
    """
    freq = str(features.get("frequency") or "").strip().lower()
    category = str(features.get("category") or "").strip()
    header, sid, task_name, url, notes = _card_header(features, entry, mode=mode, model=model)
    if mode == "llm":
        body = _render_llm_body(sid, task_name, url, notes, freq,
                                dict(_FREQ_SCHEDULE.get(freq, {})))
    else:
        body = _render_template_body(url, category, entry.get("keywords") or [], notes)
    return "\n".join(header + body + [""])


def _draft_path(source_id: str, drafts_dir: Path | None = None) -> Path:
    """草案落点（白名单钳制：恒在 drafts/ 内，防任何路径拼装越界进正式目录）。"""
    base = Path(drafts_dir) if drafts_dir else _DRAFTS_DIR
    p = (base / f"{source_id}{DRAFT_SUFFIX}").resolve()
    if p.parent != base.resolve():
        raise ValueError(f"草案路径越界（仅限 {base}）: {p}")
    return p


def _build_chat(chat, model: str) -> tuple[object, bool]:
    """chat 注入位；缺省现场构造 OllamaChat（经 LSG）。返回 (chat, llm_ok)。"""
    if chat is not None:
        return chat, True
    try:
        from zephyr.integration.local_model.ollama_chat import OllamaChat
        return OllamaChat(model=model, timeout_s=120.0), True
    except Exception as exc:  # noqa: BLE001 — LLM 不可达降级（班不炸）
        print(f"WARN: Ollama 不可达，全部条目降级模板卡（{exc}）")
        return None, False


def _collect_entries(inbox: Path) -> list[dict]:
    """全部收件箱文件 → 条目列表（文件名排序+url 去重；解析委托车道 G，CLONEGUARD）。"""
    from scripts.backtest.lane_g_stomach_intake import parse_inbox_entries  # noqa: E402 委托复用

    entries: list[dict] = []
    seen_urls: set[str] = set()
    for f in sorted(inbox.glob("intel-*.md")):
        for e in parse_inbox_entries(f.read_text(encoding="utf-8")):
            if e["url"] in seen_urls:
                continue  # 同条目跨文件/同文件重复只出一张草案
            seen_urls.add(e["url"])
            entries.append(e)
    return entries


def _decide_features(entry: dict, chat) -> tuple[dict, str]:
    """单条目 LLM 抽取。返回 (features, mode)；mode∈{"llm","template","skip"}。

    ask 失败/回包损坏→template（降级留痕不硬凑）；is_data_source=false→skip（诚实无货）。
    """
    try:
        raw = chat.ask(build_extraction_prompt(entry), system=EXTRACTION_SYSTEM,
                       temperature=0.3)
        obj = _parse_source_json(raw)
    except Exception as exc:  # noqa: BLE001 — 单条目 LLM 失败→模板卡不炸
        print(f"WARN 特征抽取失败 {entry['url']}: {type(exc).__name__}: {exc}",
              file=sys.stderr)
        obj = None
    if obj is None:
        return {}, "template"
    if not obj.get("is_data_source"):
        return {}, "skip"
    return obj, "llm"


def _persist_draft(text: str, out: Path, item: dict, dry_run: bool) -> int:
    """落盘/幂等跳过判定。返回 unchanged 增量；成功把 item 记入 drafted（就地）。"""
    try:
        if out.exists() and out.read_text(encoding="utf-8") == text:
            return 1  # 幂等：内容不变不重写
        if not dry_run:
            out.parent.mkdir(parents=True, exist_ok=True)
            safe_write_text(out, text, encoding="utf-8")
        item["drafted"].append({"source_id": item["source_id"], "file": str(out),
                                "mode": item["mode"], "url": item["url"]})
    except Exception as exc:  # noqa: BLE001 — 写盘失败记档继续
        item["failed"].append(item["url"])
        print(f"WARN 草案写盘失败 {out}: {exc}", file=sys.stderr)
    return 0


def run_drafter(limit: int | None = None, dry_run: bool = False,
                chat=None, model: str | None = None,
                inbox_dir: Path | None = None, drafts_dir: Path | None = None) -> dict:
    """主流程：收件箱条目（url 去重）→ LLM 抽取 → 草案 YAML（幂等重跑）。

    chat 参数为测试注入位（缺省现场构造 OllamaChat，经 LSG）；
    inbox_dir/drafts_dir 为测试注入位（缺省=模块常量；drafts_dir 恒钳制在 drafts/）；
    OllamaChat 构造失败=不可达→后续全部条目降级模板卡（不炸）；
    单条目 ask 失败/回包无 JSON→该条目降级模板卡；
    is_data_source=false→诚实跳过不出卡。
    """
    inbox = Path(inbox_dir) if inbox_dir else _INBOX_DIR
    chat, llm_ok = _build_chat(chat, model or MODEL)
    entries = _collect_entries(inbox)

    drafted: list[dict] = []
    unchanged = 0
    no_source = 0
    failed: list[str] = []
    taken: set[str] = set()
    processed = 0
    for entry in entries:
        if limit is not None and processed >= limit:
            break
        processed += 1
        if not llm_ok:
            features, mode = {}, "template"
        else:
            features, mode = _decide_features(entry, chat)
        if mode == "skip":
            no_source += 1
            continue  # 诚实无货：非数据源条目不出卡
        features["_source_id"] = derive_source_id(
            features.get("source_name") or entry["title"], entry["url"], taken)
        taken.add(features["_source_id"])
        text = render_draft_card(features, entry, mode=mode,
                                 model=model or MODEL if mode == "llm" else "template(降级)")
        out = _draft_path(features["_source_id"], drafts_dir)
        item = {"source_id": features["_source_id"], "mode": mode,
                "url": entry["url"], "drafted": drafted, "failed": failed}
        unchanged += _persist_draft(text, out, item, dry_run)

    record = {
        "batch": f"W105-{now_utc().strftime('%Y%m%d-%H%M%S')}",
        "drafts_dir": str(drafts_dir if drafts_dir else _DRAFTS_DIR),
        "processed_entries": processed,
        "drafted": drafted,
        "unchanged": unchanged,
        "no_source": no_source,
        "failed_urls": failed,
    }
    return record


def main() -> int:
    ap = argparse.ArgumentParser(
        description="源发现→源卡片草案转化器（WO-①-05）：收件箱→source_cards 草案（只产草案不生效）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("run", help="消化收件箱条目并产出源卡片草案（仅 drafts/ 目录）")
    g.add_argument("--limit", type=int, default=None, help="本班最多消化条目数")
    g.add_argument("--dry-run", action="store_true", help="只回看不写盘")
    g.add_argument("--model", type=str, default=None, help="Ollama 模型（默认 qwen3:8b）")
    args = ap.parse_args()
    record = run_drafter(limit=args.limit, dry_run=args.dry_run, model=args.model)
    print(json.dumps(record, ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
