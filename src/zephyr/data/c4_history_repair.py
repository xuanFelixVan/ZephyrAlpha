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
    """启发式 3a（表格视觉结构版）：fitz.find_tables → 表头年份 × EPS 行配对。

    返回 [{'forecast_year': int, 'eps': float, 'confidence': str, 'snippet': str}]。
    表路径置信度=high（值来自真实单元格网格）；零命中由调用方决定是否走文本兜底。
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
            header_years: list[int] | None = None
            header_idx = -1
            for i, row in enumerate(data[:6]):
                yrs = _parse_header_years([c for c in row if c])
                if len(yrs) >= 2:
                    header_years = yrs
                    header_idx = i
                    break
            if not header_years:
                continue
            for row in data[header_idx + 1:]:
                cells = [str(c) if c is not None else "" for c in row]
                label = "".join(cells[:2])
                if not _LABEL_RE.search(label):
                    continue
                vals: list[float] = []
                for c in cells[1:]:
                    m = _FLOAT_RE.search(c)
                    if m:
                        v = float(m.group())
                        if 0 < v < 5000:
                            vals.append(v)
                pairs = (list(zip(header_years, vals)) if len(vals) == len(header_years)
                         else list(zip(header_years[:len(vals)], vals)))
                for y, v in pairs:
                    if v > 0 and (y not in results or results[y]["confidence"] != "high"):
                        results[y] = {"forecast_year": y, "eps": v, "confidence": "high",
                                      "snippet": f"{label[:30]}|页{pg.number}|表头{header_years}"}
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


def extract_report(report_id: str, symbol: str, publish_date: str) -> dict:
    """单份端到端：下载→表格提取（兜底文本）→落表。返回摘要（不抛异常）。"""
    year = publish_date[:4]
    outcome, path = fetch_pdf(report_id, year)
    if path is None:
        return {"report_id": report_id, "outcome": outcome, "rows": 0}
    found = extract_forecasts_from_pdf(path)
    if not found:
        text, quality = pdf_text(path)
        if quality != "ok":
            return {"report_id": report_id, "outcome": outcome, "rows": 0, "quality": quality}
        found = [f for f in extract_forecasts(text) if f["confidence"] == "mid"]
    rows = []
    for f in found:
        rows.append((report_id, symbol, publish_date, f["forecast_year"], f["eps"],
                     None, f["confidence"], "heuristic", f["snippet"]))
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
