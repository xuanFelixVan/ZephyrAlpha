# [BLUEPRINT] MOD-BT-150 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.lane_b_idea_generator
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pandas; zephyr.integration.local_model.ollama_chat
# [CONSUMERS] 策略生产全景图 FAC-E1B 车道B-AI生成；FAC-E2 假说预审（下游消费方）；
#   data/strategy_intake/lane_b_candidates.csv（进货台账）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 出生证（birth_channel/birth_batch/birth_source）由本模块代码机器写入，AI 禁手填；
#   运动员不兼任裁判——本车道只生成不打分，成绩与判定权在 E2 预审/E4 考试；
#   候选 id=CAND-md5_12('E1B:'+假说全文) 内容寻址稳定可去重；台账只追加；
#   LLM 调用必经 OllamaChat（内置 LSG fail-closed 闸门）；同一假说跨批不重复入账
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(生成解析连续失败); LSGBlockedError(prompt 被安全闸拒绝)
# [TESTS] tests/backtest/test_lane_b_idea_generator.py
# [A_module] module_id=MOD-BT-150 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  手动 CLI 生成器非常驻服务：由 E1 进货编排事件调用（接线前人工/会话触发），无常驻循环
"""FAC-E1B 车道B-AI生成——NL→策略想法量产 MVP（图9 FAC-E1B）。

原理（讨论稿 §五）：车道 B 货最便宜也最杂，靠 E2 预审把关；本车道只负责按主题种子
批量生成结构化假说（机制提示+持有期+适用域），带出生证卸到 data/strategy_intake/。
业界警示（QuantCode-Bench）：NL→可执行策略单轮通过率仅 70-76%——本车道产出是
"想法"而非"代码"，构造在 E3（带验收集+重试环），考试在 E4，本车道无权自我评分。

主题种子驱动（确定性）：内置 12 个策略族主题，每主题生成 N 条结构化假说；
生成结果经内容寻址去重（跨批同假说不重复入账）。

用法:
  python scripts/backtest/lane_b_idea_generator.py generate --n-per-theme 2 --dry-run
  python scripts/backtest/lane_b_idea_generator.py generate --themes 动量,反转 --n-per-theme 3
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

_ROOT = Path(__file__).resolve().parents[2]
_INTAKE_CSV = _ROOT / "data" / "strategy_intake" / "lane_b_candidates.csv"

MODEL = "qwen3:8b"
BIRTH_CHANNEL = "B"

# 内置主题种子（12 策略族，确定性清单；--themes 可选子集）
SEED_THEMES = (
    "价格动量", "价格反转", "横截面价值", "波动率变化", "成交量异动", "事件驱动",
    "趋势过滤", "均值回归", "季节性", "相对强弱", "流动性溢价", "风险规避切换",
)

GENERATION_SYSTEM = ("你是量化策略假说生成器。只生成假说，不写代码，不做回测。"
                     "每个假说必须说清：赚的是谁的钱（机制）、什么信号、持有多久、用在什么股票域。"
                     "始终输出合法 JSON，不要输出额外文本。")


def build_generation_prompt(theme: str, n: int) -> str:
    """确定性生成 prompt（同主题同 N 必同 prompt）。"""
    return (
        f"围绕主题「{theme}」生成 {n} 条 A 股日频策略假说。\n"
        "要求：机制具体到交易对手或风险来源；避免纯数据挖掘巧合（冰淇淋销量式）；"
        "信号必须是 T 日收盘可知的信息；不涉及做空（A 股个股限制）。\n"
        f"输出 JSON 数组，每条：{{\"hypothesis_zh\": \"一句话假说\", "
        f"\"mechanism_hint\": \"机制提示\", \"horizon\": \"持有期如5日/20日\", "
        f"\"universe\": \"适用域如沪深300/全A\"}}，恰好 {n} 条。"
    )


def parse_ideas(raw: str) -> list[dict]:
    """模型回复 → 假说 dict 列表（JSON 数组强解析；兜底逐对象提取；全败返回 []）。"""
    text = (raw or "").strip()
    start = text.find("[")
    end = text.rfind("]")
    if start >= 0 and end > start:
        try:
            arr = json.loads(text[start:end + 1])
            return [x for x in arr if isinstance(x, dict) and x.get("hypothesis_zh")]
        except json.JSONDecodeError:
            pass
    items: list[dict] = []
    for m in re.finditer(r"\{[^{}]*\}", text, re.DOTALL):
        try:
            x = json.loads(m.group(0))
            if isinstance(x, dict) and x.get("hypothesis_zh"):
                items.append(x)
        except json.JSONDecodeError:
            continue
    return items


def make_candidate_id(hypothesis_zh: str) -> str:
    """候选 id：CAND-<md5_12>，对假说全文内容寻址（跨批同假说不换 id）。"""
    digest = hashlib.md5(f"E1B:{hypothesis_zh.strip()}".encode("utf-8")).hexdigest()[:12]
    return f"CAND-{digest}"


def attach_birth_certificate(ideas: list[dict], batch_id: str, theme: str,
                             prompt: str) -> list[dict]:
    """出生证三件套机器写入（v9 防幻觉块：溯源由流水线代码生成）。"""
    prompt_fp = hashlib.md5(prompt.encode("utf-8")).hexdigest()[:12]
    out = []
    for x in ideas:
        row = dict(x)
        row["birth_channel"] = BIRTH_CHANNEL
        row["birth_batch"] = batch_id
        row["birth_source"] = f"llm:{MODEL} theme={theme} prompt_md5={prompt_fp}"
        out.append(row)
    return out


def load_existing_ids(path: Path) -> set[str]:
    """台账已有 id 集（跨批去重；文件不存在/损坏返回空集）。"""
    if not path.exists():
        return set()
    try:
        df = pd.read_csv(path, encoding="utf-8-sig")
        return set(df["candidate_id"].astype(str))
    except Exception:  # noqa: BLE001 — 台账损坏不阻断生成，宁可重写不误删
        return set()


def run_generation(themes: list[str], n_per_theme: int, dry_run: bool = False) -> dict:
    """主流程：主题×生成→解析→去重→出生证→卸货（dry-run 只回看不写）。"""
    from zephyr.integration.local_model.ollama_chat import OllamaChat

    chat = OllamaChat(model=MODEL)
    batch_id = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("E1B-%Y%m%d-%H%M%S")
    existing = load_existing_ids(_INTAKE_CSV)
    rows: list[dict] = []
    failed_themes: list[str] = []
    skipped_dup = 0
    for theme in themes:
        prompt = build_generation_prompt(theme, n_per_theme)
        ideas: list[dict] = []
        for _ in range(2):  # 解析失败一次重试
            try:
                raw = chat.ask(prompt, system=GENERATION_SYSTEM, temperature=0.4)
                ideas = parse_ideas(raw)
                if ideas:
                    break
            except Exception:  # noqa: BLE001 — LLM 不可达/被闸，该主题记失败继续
                break
        if not ideas:
            failed_themes.append(theme)
            continue
        certified = attach_birth_certificate(ideas, batch_id, theme, prompt)
        for x in certified:
            cid = make_candidate_id(str(x["hypothesis_zh"]))
            if cid in existing:
                skipped_dup += 1
                continue
            existing.add(cid)
            rows.append({
                "candidate_id": cid,
                "theme": theme,
                "hypothesis_zh": x["hypothesis_zh"],
                "mechanism_hint": x.get("mechanism_hint", ""),
                "horizon": x.get("horizon", ""),
                "universe": x.get("universe", ""),
                "birth_channel": x["birth_channel"],
                "birth_batch": x["birth_batch"],
                "birth_source": x["birth_source"],
            })
    record = {
        "batch": batch_id, "themes": list(themes), "generated": len(rows),
        "failed_themes": failed_themes, "skipped_dup": skipped_dup,
        "items": [{k: r[k] for k in ("candidate_id", "theme", "hypothesis_zh")} for r in rows],
    }
    if not dry_run and rows:
        header = not _INTAKE_CSV.exists()
        _INTAKE_CSV.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(rows).to_csv(_INTAKE_CSV, mode="a", header=header, index=False,
                                  encoding="utf-8-sig")
        record["written_to"] = str(_INTAKE_CSV.relative_to(_ROOT))
    return record


def main() -> int:
    ap = argparse.ArgumentParser(description="FAC-E1B 车道B-AI生成（NL→策略假说，经 LSG）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate", help="按主题种子批量生成假说")
    g.add_argument("--themes", default=None, help="逗号分隔主题子集（缺省=全部 12 主题）")
    g.add_argument("--n-per-theme", type=int, default=2, help="每主题生成条数")
    g.add_argument("--dry-run", action="store_true", help="只回看不写台账")
    args = ap.parse_args()
    themes = ([t.strip() for t in args.themes.split(",") if t.strip()]
              if args.themes else list(SEED_THEMES))
    try:
        record = run_generation(themes, args.n_per_theme, args.dry_run)
    except RuntimeError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(record, ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
