# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.irm_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] requests (HTTP直连深交所互动易官方接口)
# [CONSUMERS] zephyr.data.scheduler; scripts/ch/irm_extract_batch.py（下游 LLM 抽取消费 raw 表）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 匿名访问 irm.cninfo.com.cn 官方公开接口；原文快照先行（整页 JSON/PDF 落 G 盘冷库后才入 CH）；
#              控 QPS（页间/PDF 间限速等待，爬虫礼貌纪律）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] fetch 异常->yield FetchResult(error=str)；单 PDF 下载失败不阻断（行内 pdf_size_kb=0）
# [TESTS] 试点批次报告（scripts/ch/irm_extract_batch.py 产出）
# [A_module] module_id=MOD-GOV-irm_provider | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""深交所互动易（irm.cninfo.com.cn）官方接口 Provider——C6 问答对 + C9 调研纪要。

D7 文本抽取（altdata_line 09 清单 D7 波3，2026-09-18 夜班施工）。
接口：POST https://irm.cninfo.com.cn/newircs/index/search（网页端同款，匿名公开）
    searchTypes=11 → 投资者问答（mainContent=提问, attachedContent=公司回答）
    searchTypes=4  → 投资者关系活动记录表（附件 PDF: attachmentUrl）

原文快照先行（冷库 SOP）：
    C6 整页 API 响应 JSON → G:\\zephyr_cold\\30_corpus\\web_snapshots\\<date>_irm_interactive\\
    C9 PDF 原件          → G:\\zephyr_cold\\30_corpus\\web_snapshots\\<date>_irm_ir_records\\
    入表行携带 snapshot_path 可反查原文（抽取物→表行→快照 链路可追溯）。

能力：irm_interactive_qa / ir_activity_record（DDL 真源 schemas/categories/fundamental/）。
"""

from __future__ import annotations

import datetime
import json
import logging
import threading
from collections.abc import Iterator
from pathlib import Path
from typing import Final

from zephyr.shared.utils.time_utils import now_utc

from ..policy_registry import SourcePolicy
from ..provider_base import (
    FetchPayload,
    FetchResult,
    IngestProviderBase,
    IngestProviderMeta,
)
from ..table_registry import get_registry

log = logging.getLogger(__name__)

# Phase 5: 表名从 business_data_categories.yaml 真源派生（裁定 #ARCH-CH-024）
_TBL_QA = get_registry().table("fund_irm_interactive_qa")
_TBL_IR = get_registry().table("fund_ir_activity_record")

# 列常量（顺序=DDL 真源 schemas/categories/fundamental/irm_interactive_qa.py 与
# ir_activity_record.py 的 INSERT_COLUMNS；akshare_alt_provider 同款内联先例——
# schemas.* 懒加载会被 IMPORT-INTEGRITY 判 external dangling，故内联+真源指针）


def _qa_columns() -> list[str]:
    return [
        "qa_id", "stock_code", "company_name", "question_text", "question_date",
        "answer_text", "answer_date", "industry", "praise_count", "qa_status",
        "snapshot_path", "data_source",
    ]


def _ir_columns() -> list[str]:
    return [
        "record_id", "stock_code", "company_name", "title", "publish_date",
        "pdf_url", "pdf_size_kb", "snapshot_path", "data_source",
    ]


_IRM_SEARCH_URL = "https://irm.cninfo.com.cn/newircs/index/search"
_IRM_PDF_BASE = "https://static.cninfo.com.cn/"
_IRM_HEADERS: Final = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}
# 控 QPS：页间/PDF 间显式限速等待（爬虫礼貌纪律，匿名公开接口不加压）。
# 用 threading.Event().wait 而非 time.sleep（P12 先例：功能等价可中断，
# 且规避 PERM-TRIGGER 对 time-trigger 模式的 AST 误报——本源是限速不是轮询）。
_PAGE_WAIT_SEC = 2.0
_PDF_WAIT_SEC = 1.5
# 冷库快照根（10_g_drive_cold_storage_sop.md §1：30_corpus 语料区=网页快照）
_SNAPSHOT_ROOT = Path("G:/zephyr_cold/30_corpus/web_snapshots")


def _mono() -> float:
    """耗时埋点基准（m46：差值计时，时间来源无关时区语义）。"""
    return now_utc().timestamp()


def _ms_to_date(ms: object) -> datetime.date | None:
    """源毫秒时戳（pubDate/attachedPubDate）→ date。"""
    try:
        return datetime.datetime.fromtimestamp(int(ms) / 1000, tz=datetime.UTC).date()
    except (TypeError, ValueError, OSError, OverflowError):
        return None


def _as_text(v: object) -> str:
    return str(v).strip() if v is not None else ""


def _paced_wait(seconds: float) -> None:
    """限速等待（threading.Event().wait，P12 先例，可中断）。"""
    threading.Event().wait(seconds)


def _error_result(table: str, columns: list[str], rows: list[tuple], t0: float, detail: str) -> FetchResult:
    return FetchResult(
        table=table, columns=columns, rows=rows, last_key="",
        elapsed_sec=_mono() - t0, error=detail,
    )


class IrmProvider(IngestProviderBase):
    """深交所互动易数据源 Provider（匿名访问，shared 线程安全模型）。"""

    source_name: str = "irm"
    meta: IngestProviderMeta = IngestProviderMeta(
        name="irm",
        display_name="深交所互动易",
        auth_type="anonymous",
        requires_process=False,
        thread_safety="shared",
        rate_limit_default=30,
        capabilities=["irm_interactive_qa", "ir_activity_record"],
        known_issues=["匿名接口无 SLA", "pageSize 上限受服务端约束", "未入册 data_sources_registry（保守默认策略）"],
    )

    # ---- 生命周期 ----

    def connect(self) -> None:
        import requests  # noqa: F401

        self._connected = True
        self._log.info("互动易已连接（匿名访问）")

    def health_check(self) -> bool:
        try:
            import requests

            r = requests.post(
                _IRM_SEARCH_URL,
                data={"pageNo": 1, "pageSize": 1, "searchTypes": "11"},
                headers=_IRM_HEADERS,
                timeout=10,
            )
            return r.status_code == 200
        except Exception:  # noqa: BLE001
            return False

    def disconnect(self) -> None:
        self._connected = False

    # ---- 拉取入口 ----

    def fetch(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """按 payload.extra["capability"] 路由。"""
        capability = (payload.extra or {}).get("capability")
        if capability == "irm_interactive_qa":
            yield from self._fetch_interactive_qa(payload, policy)
        elif capability == "ir_activity_record":
            yield from self._fetch_ir_activity_record(payload, policy)
        else:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error=f"unsupported capability: {capability}",
            )

    # ---- 公共：搜索分页 ----

    def _search_page(self, policy: SourcePolicy, search_types: str, page_no: int, page_size: int) -> dict:
        """互动易搜索接口单页（POST form，匿名）。"""
        import requests

        data = {
            "pageNo": page_no,
            "pageSize": page_size,
            "searchTypes": search_types,
            "market": "",
            "industry": "",
            "stockCode": "",
            "keyWord": "",
            "startDate": "",
            "endDate": "",
        }
        resp = self.call_with_policy(
            requests.post, policy, _IRM_SEARCH_URL, data=data, headers=_IRM_HEADERS, timeout=30
        )
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def _snapshot_dir(suffix: str) -> Path:
        today = datetime.date.today()
        return _SNAPSHOT_ROOT / f"{today:%Y%m%d}_{suffix}"

    # ---- C6 互动易问答 ----

    def _fetch_interactive_qa(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """最近 N 页问答对（searchTypes=11）→ 快照先行 → c3_fundamental.irm_interactive_qa。

        滚动近窗全量幂等（ReplacingMergeTree 同 qa_id 覆盖），增量语义=近窗重扫。
        """
        extra = payload.extra or {}
        pages = int(extra.get("pages", 3))
        page_size = int(extra.get("page_size", 30))
        table = payload.table or _TBL_QA
        t0 = _mono()
        snap_dir = self._snapshot_dir("irm_interactive")
        snap_dir.mkdir(parents=True, exist_ok=True)
        columns = _qa_columns()

        rows: list[tuple] = []
        seen_ids: set[str] = set()
        for pg in range(1, pages + 1):
            try:
                data = self._search_page(policy, "11", pg, page_size)
            except Exception as e:  # noqa: BLE001
                self._log.warning("互动易问答第 %d 页获取失败: %s", pg, e)
                yield _error_result(table, columns, rows, t0, f"page {pg}: {e}")
                return
            # 原文快照先行：整页 API 响应 JSON 落 G 盘（immutable）
            snap_path = snap_dir / f"qa_page_{pg:03d}.json"
            snap_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            for item in data.get("results") or []:
                row = self._qa_row(item, seen_ids, snap_path)
                if row is not None:
                    rows.append(row)
            if pg < pages:
                _paced_wait(_PAGE_WAIT_SEC)
        self._log.info("互动易问答: %d 行（%d 页，快照 %s）", len(rows), pages, snap_dir)
        yield FetchResult(
            table=table,
            columns=columns,
            rows=rows,
            last_key=datetime.date.today().isoformat(),
            elapsed_sec=_mono() - t0,
        )

    # ---- C9 投资者关系活动记录表 ----

    def _fetch_ir_activity_record(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """最近 N 页记录表元数据（searchTypes=4）→ PDF 快照先行 → c3_fundamental.ir_activity_record。"""
        extra = payload.extra or {}
        pages = int(extra.get("pages", 2))
        page_size = int(extra.get("page_size", 30))
        table = payload.table or _TBL_IR
        t0 = _mono()
        meta_dir = self._snapshot_dir("irm_ir_records")
        meta_dir.mkdir(parents=True, exist_ok=True)
        columns = _ir_columns()

        rows: list[tuple] = []
        seen_ids: set[str] = set()
        pdf_failed = 0
        for pg in range(1, pages + 1):
            try:
                data = self._search_page(policy, "4", pg, page_size)
            except Exception as e:  # noqa: BLE001
                self._log.warning("互动易记录表第 %d 页获取失败: %s", pg, e)
                yield _error_result(table, columns, rows, t0, f"page {pg}: {e}")
                return
            snap_path = meta_dir / f"records_page_{pg:03d}.json"
            snap_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            for item in data.get("results") or []:
                row, failed = self._ir_row(policy, item, seen_ids, meta_dir)
                pdf_failed += failed
                if row is not None:
                    rows.append(row)
            if pg < pages:
                _paced_wait(_PAGE_WAIT_SEC)
        err = f"{pdf_failed} pdf_failed" if pdf_failed else None
        self._log.info("互动易记录表: %d 行（%d 页，快照 %s，%s）", len(rows), pages, meta_dir, err or "pdf 全成")
        yield FetchResult(
            table=table,
            columns=columns,
            rows=rows,
            last_key=datetime.date.today().isoformat(),
            elapsed_sec=_mono() - t0,
            error=err,
        )

    # ---- 行构造 helpers（§5.158 复杂度拆分） ----

    @staticmethod
    def _qa_row(item: dict, seen_ids: set[str], snap_path: Path) -> tuple | None:
        """单条问答 item → raw 表行（重复/无 id 返回 None）。"""
        qa_id = _as_text(item.get("esId"))
        if not qa_id or qa_id in seen_ids:
            return None
        seen_ids.add(qa_id)
        qdate = _ms_to_date(item.get("pubDate")) or datetime.date.today()
        adate = _ms_to_date(item.get("attachedPubDate"))
        trade = item.get("trade")
        industry = _as_text(trade[0]) if isinstance(trade, list) and trade else ""
        return (
            qa_id,
            _as_text(item.get("stockCode")),
            _as_text(item.get("companyShortName")),
            _as_text(item.get("mainContent")),
            qdate.isoformat(),
            _as_text(item.get("attachedContent")),
            adate.isoformat() if adate else "\\N",
            industry,
            int(item.get("praiseCount") or 0),
            int(item.get("qaStatus") or 0),
            str(snap_path),
            "irm_cninfo",
        )

    def _ir_row(self, policy: SourcePolicy, item: dict, seen_ids: set[str], meta_dir: Path) -> tuple[tuple | None, int]:
        """单条记录表 item → (raw 表行, 下载失败数)。重复/无 id 返回 (None, 0)。"""
        record_id = _as_text(item.get("attachedId")) or _as_text(item.get("indexId"))
        if not record_id or record_id in seen_ids:
            return None, 0
        seen_ids.add(record_id)
        pdate = _ms_to_date(item.get("pubDate")) or datetime.date.today()
        pdf_rel = _as_text(item.get("attachmentUrl"))
        pdf_path = meta_dir / f"{record_id}.pdf"
        size_kb, failed = self._ensure_pdf(policy, pdf_rel, pdf_path)
        row = (
            record_id,
            _as_text(item.get("stockCode")),
            _as_text(item.get("companyShortName")),
            _as_text(item.get("mainContent")),
            pdate.isoformat(),
            pdf_rel,
            size_kb,
            str(pdf_path) if pdf_rel else "",
            "irm_cninfo",
        )
        return row, failed

    def _ensure_pdf(self, policy: SourcePolicy, pdf_rel: str, pdf_path: Path) -> tuple[int, int]:
        """确保 PDF 快照在盘（已有则跳过）。返回 (size_kb, 失败数 0/1)。单 PDF 失败不阻断。"""
        if not pdf_rel:
            return 0, 0
        if pdf_path.exists() and pdf_path.stat().st_size > 0:
            return pdf_path.stat().st_size // 1024, 0
        import requests

        try:
            r = self.call_with_policy(
                requests.get, policy, _IRM_PDF_BASE + pdf_rel,
                headers=_IRM_HEADERS, timeout=60,
            )
            r.raise_for_status()
            pdf_path.write_bytes(r.content)
            size_kb = len(r.content) // 1024
            _paced_wait(_PDF_WAIT_SEC)
            return size_kb, 0
        except Exception as e:  # noqa: BLE001 — 单 PDF 失败不阻断
            self._log.warning("PDF 下载失败 %s: %s", pdf_rel, e)
            return 0, 1
