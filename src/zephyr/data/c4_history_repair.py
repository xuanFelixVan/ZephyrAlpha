# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.c4_history_repair
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.ch_writer; zephyr.data.provider_base; PyMuPDF(fitz)
# [CONSUMERS] scripts/ch/c4_extract_batch.py（C4 历史修复批处理，下一班）；原型验证 CLI
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] PDF 原文=发布时点冻结件（时间机器，源污染修复唯一免费路径，§9 档案）；
#              URL 形态=http://pdf.dfcfw.com/pdf/H3_{infoCode}_1.pdf（https=反爬页禁用）；
#              缓存=data/c4_pdf_cache/{year}/{report_id}.pdf（gitignore 区，断点续传=缓存存在即跳过）；
#              文字层守卫=均值<200 字/页→low_text 标记跳过（扫描件不硬解）；
#              两级提取=fitz.find_tables 视觉表格结构优先（值来自真实单元格网格→high），
#              文本正则兜底（fitz 文字流与视觉列序可能错位→一律 mid 慎用）；
#              提取产物落 c3_fundamental.pdf_forecast_extracted（同键幂等覆盖）；
#              版权边界=仅内部研究提取，不留存分发 PDF 全文
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 下载失败→(outcome, None)；文字层薄→low_text 标记；提取零命中→空列表非错误
# [TESTS] 原型验证=缓存 PDF 实弹（茅台 2017 已知锚点 15.6 元）
# [TTL] permanent
"""c4_history_repair — C4 历史修复核心（下载/文本/表格提取三层，2026-09-14）。

使命：research_report 预测槽位=源站当前快照（历史无 PIT）；PDF 原文是发布时点冻结件，
从中提取**真历史预测值**重建 consensus 历史段。
方案真源=docs/_working/2026-09-14-c4-history-repair-plan.md（四层架构/验证三层/验收标准）。
LLM 兜底层（3b，走 LSG+intelligence 池化通道）=下一班接线；本模块=3a 规则提取。
"""

from __future__ import annotations

import logging
import re
import urllib.request
from pathlib import Path

log = logging.getLogger(__name__)

_URL_TMPL = "http://pdf.dfcfw.com/pdf/H3_{rid}_1.pdf"
_UA = "Mozilla/5.0"
_MIN_PDF_BYTES = 10_000
_LOW_TEXT_CHARS_PER_PAGE = 200

_REPO_ROOT = Path(__file__).resolve().parents[3]
_CACHE_ROOT = _REPO_ROOT / "data" / "c4_pdf_cache"

_YEAR_RE = re.compile(r"(20\d{2})\s*E?")
_FLOAT_RE = re.compile(r"-?\d+\.\d{1,2}(?![\d%])")
_TABLE_YEAR_RE = re.compile(r"(20\d{2})\s*E")
_LABEL_RE = re.compile(r"每股收益|EPS")
_FORECAST_ANCHOR_RE = re.compile(r"盈利预测|投资建议")


def fetch_pdf(report_id: str, year: str, timeout: int = 60, retries: int = 2) -> tuple[str, Path | None]:
    """下载（带缓存断点）：返回 (outcome, 缓存路径|None)。outcome=real_pdf/bot_page/http_err/cached。"""
    cache = _CACHE_ROOT / year / f"{report_id}.pdf"
    if cache.exists() and cache.stat().st_size >= _MIN_PDF_BYTES:
        return "cached", cache
    cache.parent.mkdir(parents=True, exist_ok=True)
    url = _URL_TMPL.format(rid=report_id)
    last_err = ""
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": _UA})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
            if data[:4] == b"%PDF" and len(data) >= _MIN_PDF_BYTES:
                cache.write_bytes(data)
                return "real_pdf", cache
            return "bot_page", None
        except Exception as exc:  # noqa: BLE001 — 下载失败重试
            last_err = repr(exc)[:120]
            if attempt < retries:
                import time as _t

                _t.sleep(2 ** attempt)
    log.warning("fetch_pdf %s 失败: %s", report_id, last_err)
    return "http_err", None


def pdf_text(path: Path) -> tuple[str, str]:
    """提取全文。返回 (text, quality)；quality=ok/low_text（均值<200 字/页=疑似扫描件）。"""
    import fitz

    doc = fitz.open(str(path))
    pages = len(doc)
    text = "".join(pg.get_text() for pg in doc)
    doc.close()
    ratio = len(text) / max(pages, 1)
    return text, ("ok" if ratio >= _LOW_TEXT_CHARS_PER_PAGE else "low_text")


def _parse_header_years(row: list) -> list[int]:
    years: list[int] = []
    for c in row:
        m = _TABLE_YEAR_RE.search(str(c))
        if m:
            y = int(m.group(1))
            if 2005 <= y <= 2035 and y not in years:
                years.append(y)
    return years


def extract_forecasts_from_pdf(path: Path) -> list[dict]:
    """启发式 3a（表格网格版）：fitz.find_tables → 表头年份列号 × EPS 行同列值配对。

    关键事实（茅台 2017 研报调试实证）：find_tables 会把左右并排的两张表合成
    一张带空隔列的大网格——EPS 标签可能在行中部，值必须按**列号**回对表头年份，
    不能假设"标签在前值在后"。
    表路径置信度=high（值来自真实单元格网格）。
    """
    import fitz

    results: dict[int, dict] = {}
    doc = fitz.open(str(path))
    for pg in doc:
        try:
            tabs = pg.find_tables()
        except Exception:  # noqa: BLE001 — 单页表格解析失败不阻断
            continue
        for t in tabs.tables:
            data = t.extract()
            if not data or len(data) < 2:
                continue
            # 表头行=年份单元格最多的前 6 行之一；收集 列号→年份
            best_cols: dict[int, int] = {}
            for row in data[:6]:
                cols: dict[int, int] = {}
                for ci, c in enumerate(row):
                    m = _TABLE_YEAR_RE.search(str(c))
                    if m:
                        y = int(m.group(1))
                        if 2005 <= y <= 2035:
                            cols[ci] = y
                if len(cols) > len(best_cols):
                    best_cols = cols
            if len(best_cols) < 2:
                continue
            # 数据行：任一单元格含 EPS 标签 → 按列号取同列值
            for row in data[1:]:
                label_at = -1
                for ci, c in enumerate(row):
                    if _LABEL_RE.search(str(c)):
                        label_at = ci
                        break
                if label_at < 0:
                    continue
                got: dict[int, float] = {}
                for year_ci, y in best_cols.items():
                    if year_ci < len(row):
                        m = _FLOAT_RE.search(str(row[year_ci]))
                        if m:
                            v = float(m.group())
                            if 0 < v < 5000:
                                got[y] = v
                if not got:
                    continue
                label = str(row[label_at])[:30]
                for y, v in got.items():
                    if y not in results or results[y]["confidence"] != "high":
                        results[y] = {"forecast_year": y, "eps": v, "confidence": "high",
                                      "snippet": f"{label}|页{pg.number}|列{sorted(best_cols.values())}"}
    doc.close()
    return list(results.values())


def extract_forecasts(text: str) -> list[dict]:
    """文本正则兜底（fitz 文字流与视觉列序可能错位——结果一律 mid 置信度慎用）。"""
    if not text:
        return []
    windows: list[str] = []
    for m in _FORECAST_ANCHOR_RE.finditer(text):
        windows.append(text[max(0, m.start() - 200): m.start() + 1500])
    best: dict[int, dict] = {}
    for win in windows:
        block_years: list[int] = []
        for m in _YEAR_RE.finditer(win):
            y = int(m.group(1))
            if 2005 <= y <= 2035 and y not in block_years:
                block_years.append(y)
        for em in _LABEL_RE.finditer(win):
            seg = win[em.start(): em.start() + 500]
            vals = [float(x) for x in _FLOAT_RE.findall(seg)]
            vals = [v for v in vals if 0 < v < 5000][: len(block_years)]
            if not vals or not block_years:
                continue
            for y, v in zip(block_years, vals):
                if v > 0 and y not in best:
                    best[y] = {"forecast_year": y, "eps": v,
                               "confidence": "mid",
                               "snippet": seg[:200].replace(chr(10), " ")}
            break   # 首个 EPS 行
    return list(best.values())


def extract_via_llm(text: str, symbol: str) -> list[dict]:
    """3b LLM 兜底（表格路径零命中时）：盈利预测段 → 结构化 (year, eps)。

    走 LLMGateway（内建 LSG 输入/输出双向扫描=法定通道）；输出一律 mid 置信
    （LLM 提取未经人工核对前不标 high——置信度语义见 schemas 真源）。
    调用失败/解析失败 → 空列表非错误（残差留给人工抽核）。
    """
    if not text or len(text) < 50:
        return []
    win = text[:4000]
    try:
        from zephyr.infrastructure.pipeline.llm_gateway import LLMGateway

        resp = LLMGateway.call(
            messages=[
                {"role": "system", "content": "你是财报数据提取器。只输出 JSON 数组，不要任何解释或代码块标记。"},
                {"role": "user", "content": (
                    "从下面的券商研报片段中提取盈利预测：找出'每股收益/EPS'按预测年份的数值。"
                    "只提取明确写成预测表的数值，不要从正文叙述里猜。"
                    '输出格式：[{"year": 2017, "eps": 17.10}]，年份为整数、eps 为数字。'
                    f"若片段中没有每股收益预测，输出 []。\n\n研报片段（{symbol}）：\n{win}")},
            ],
            provider="deepseek", temperature=0.0, max_tokens=4096,
        )
        if resp.simulated or not resp.content:
            log.warning("LLM 兜底未产出（%s）", resp.error)
            return []
        m = re.search(r"\[.*\]", resp.content, re.S)
        if not m:
            return []
        import json as _json

        items = _json.loads(m.group())
        out = []
        for it in items:
            try:
                y = int(it["year"])
                v = float(it["eps"])
                if 2005 <= y <= 2035 and 0 < v < 5000:
                    out.append({"forecast_year": y, "eps": v, "confidence": "mid",
                                "method": "llm",
                                "snippet": f"LLM提取|{symbol}"})
            except (KeyError, ValueError, TypeError):
                continue
        return out
    except Exception as exc:  # noqa: BLE001 — LLM 通道故障不阻断批处理
        log.warning("extract_via_llm 异常: %s", repr(exc)[:120])
        return []



def _page_word_rows(pg) -> list[list[tuple[float, float, str]]]:
    """页 → 坐标行重建：词按 y 聚类（4px）、行内按 x 排序、再按大间隙切栏段。

    双栏页面教训（立讯精密 002475 实证）：左右栏同高度的词会被 y 聚类拼成一行，
    年份来自左栏、数值来自右栏→跨栏错配。切栏段后表头/EPS 必须同段。
    返回 [(x_center, y, word)]（已切栏，段与段独立）。
    """
    words = pg.get_text("words")   # (x0, y0, x1, y1, word, ...)
    rows: dict[int, list] = {}
    for w in words:
        key = round(w[1] / 4)
        rows.setdefault(key, []).append(w)
    out = []
    for key in sorted(rows):
        ws = sorted(rows[key], key=lambda w: w[0])
        segs = [[ws[0]]]
        for w in ws[1:]:
            gap = w[0] - segs[-1][-1][0]   # 与段内末词的 x0 间距
            if gap > 80:                   # 大间隙=栏边界
                segs.append([w])
            else:
                segs[-1].append(w)
        for seg in segs:
            out.append([((w[0] + w[2]) / 2, w[1], w[4]) for w in seg])
    return out


def extract_forecasts_via_words(path: Path) -> list[dict]:
    """启发式 3a'（坐标几何版）：无边框表/隔列漂移的治本——词坐标 y 聚类成行，
    年份表头行与 EPS 行按 x 几何对齐（最近邻 ±半列宽）。有框无框通吃。
    置信度=high（几何对齐可信，且要求行内含>=2 个数值词）。
    仅在含"盈利预测"且"每股收益"的页上运行（叙事段落不误抓）。
    """
    import fitz

    results: dict[int, dict] = {}
    doc = fitz.open(str(path))
    for pg in doc:
        t = pg.get_text()
        if "每股收益" not in t or ("盈利预测" not in t and "投资建议" not in t):
            continue
        rows = _page_word_rows(pg)
        # 表头行=含 >=2 个年份词（同/异行相邻也算）
        year_cols: list[tuple[float, int]] = []
        for row in rows:
            yts = []
            for x, y, w in row:
                m = _TABLE_YEAR_RE.search(w)
                if m:
                    y = int(m.group(1))
                    if 2005 <= y <= 2035:
                        yts.append((x, y))
            if len(yts) >= 2:
                year_cols = yts
        if len(year_cols) < 2:
            continue
        # EPS 行=含每股收益/EPS 词的坐标行；值=同行最近年份 x 的数值词
        for row in rows:
            label_x = None
            for x, y, w in row:
                if _LABEL_RE.search(w):
                    label_x = x
                    break
            if label_x is None:
                continue
            nums = [(x, w) for x, y, w in row if re.fullmatch(r"-?\d+\.\d{1,2}", w)]
            got: dict[int, float] = {}
            for x_year, y_year in year_cols:
                cand = min(nums, key=lambda nw: abs(nw[0] - x_year), default=None)
                if cand is not None and abs(cand[0] - x_year) <= 30:
                    v = float(cand[1])
                    if 0 < v < 5000:
                        got[y_year] = v
            if len(got) < 2:
                continue
            label = next(w for x, y, w in row if _LABEL_RE.search(w))[:24]
            for y_year, v in got.items():
                if y_year not in results or results[y_year]["confidence"] != "high":
                    results[y_year] = {"forecast_year": y_year, "eps": v,
                                       "confidence": "high", "method": "heuristic",
                                       "snippet": f"{label}|页{pg.number}|坐标对齐{sorted(got)}"}
    doc.close()
    return list(results.values())


def extract_report(report_id: str, symbol: str, publish_date: str) -> dict:
    """单份端到端：下载→表格提取（兜底文本）→落表。返回摘要（不抛异常）。"""
    year = publish_date[:4]
    outcome, path = fetch_pdf(report_id, year)
    if path is None:
        return {"report_id": report_id, "outcome": outcome, "rows": 0}
    found = extract_forecasts_from_pdf(path)
    if not found:
        found = extract_forecasts_via_words(path)
    if not found:
        text, quality = pdf_text(path)
        if quality != "ok":
            return {"report_id": report_id, "outcome": outcome, "rows": 0, "quality": quality}
        found = [f for f in extract_forecasts(text) if f["confidence"] == "mid"]
        if not found:
            found = extract_via_llm(text, symbol)   # 3b LLM 兜底（残差）
    pub_year = int(publish_date[:4])
    rows = []
    for f in found:
        # 年份合理域守卫：预测目标年∈[发布年-1, 发布年+5]——下界含 -1：
        # 年报 4/30 前的年初研报预测"上一年度"（2016E）合法；上界防"2030愿景"误抓
        if not (pub_year - 1 <= f["forecast_year"] <= pub_year + 5):
            continue
        rows.append((report_id, symbol, publish_date, f["forecast_year"], f["eps"],
                     None, f["confidence"], f.get("method", "heuristic"), f["snippet"]))
    if rows:
        _persist(rows)
    return {"report_id": report_id, "outcome": outcome, "rows": len(rows),
            "years": [f["forecast_year"] for f in found]}


def _persist(rows: list[tuple]) -> None:
    from schemas.categories.fundamental.pdf_forecast_extracted import INSERT_COLUMNS, TABLE_NAME
    from zephyr.data import ch_writer
    from zephyr.data.provider_base import FetchResult

    cols = [c.strip() for c in INSERT_COLUMNS.strip("()").split(",")]
    fr = FetchResult(table=f"c3_fundamental.{TABLE_NAME}", columns=cols, rows=rows,
                     last_key="", elapsed_sec=0.0)
    if not ch_writer.write_result(fr):
        log.warning("提取结果落表失败（%d 行）", len(rows))
