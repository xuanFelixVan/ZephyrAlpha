# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [MODULE] zephyr.frontend.dashboard.components.industry_graph
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); sentence_transformers
# [CONSUMERS] zephyr.frontend.dashboard.app_panel
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] PG 只读; RAG 模型后台预加载; 语料仅预览片段不提供下载（版权边界）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 索引缺失/PG不可达->空态提示不阻断其他 Tab
# [TTL] permanent
"""industry_graph · 图谱语料组件（视图四：文档浏览器 + RAG 问答 + 主题联动表）

数据源:
  - ig_document（PostgreSQL depgraph，只读）— 1,970 份源文档登记
  - RAG 检索层（E:\\数据下载\\产业链数据_P2语料\\chunks.sqlite + embeddings.npy,
    bge-small-zh 本地 CPU 推理，后台线程预加载）
  - 主题联动日报（.runtime/industry_graph/theme_linkage_daily.csv,
    scripts/industry_graph/theme_linkage_monitor.py 产出）

设计文档: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/2026-08-28-industry-graph-frontend.md §2.4
"""

from __future__ import annotations

import os

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"  # 必须先于 sentence_transformers 导入

import sqlite3
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import panel as pn
except ImportError:  # 测试环境无 panel
    pn = None

_CORPUS_DIR = Path(r"E:\数据下载\产业链数据_P2语料")
_LINKAGE_CSV = Path(__file__).resolve().parents[5] / ".runtime" / "industry_graph" / "theme_linkage_daily.csv"
_MODEL_NAME = "BAAI/bge-small-zh-v1.5"


# ============================================================
# 数据载荷
# ============================================================


@dataclass
class CorpusOverview:
    total_docs: int = 0
    by_type: dict[str, int] = field(default_factory=dict)
    by_status: dict[str, int] = field(default_factory=dict)


@dataclass
class IndustryGraphData:
    overview: CorpusOverview = field(default_factory=CorpusOverview)
    docs: list[dict] = field(default_factory=list)  # doc_id/title/type/year/org/status
    linkage: list[dict] = field(default_factory=list)  # 主题联动日报行
    linkage_date: str = ""
    rag_ready: bool = False
    error: str = ""


# ============================================================
# fetch（纯函数，可测试）
# ============================================================


def fetch_industry_graph() -> IndustryGraphData:
    data = IndustryGraphData(rag_ready=(_CORPUS_DIR / "chunks.sqlite").is_file()
                             and (_CORPUS_DIR / "embeddings.npy").is_file())
    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection(read_only=True, autocommit=True)
        with conn.cursor() as cur:
            cur.execute(
                "SELECT doc_type, count(*) FROM ig_document WHERE is_canonical AND NOT excluded GROUP BY 1"
            )
            data.overview.by_type = dict(cur.fetchall())
            cur.execute(
                "SELECT parse_status, count(*) FROM ig_document WHERE is_canonical AND NOT excluded GROUP BY 1"
            )
            data.overview.by_status = dict(cur.fetchall())
            data.overview.total_docs = sum(data.overview.by_type.values())
            cur.execute(
                """
                SELECT doc_id, title, doc_type, year, org, parse_status, extracted_text_path
                FROM ig_document
                WHERE is_canonical AND NOT excluded
                ORDER BY doc_type, year DESC NULLS LAST, title LIMIT 5000
                """
            )
            data.docs = [
                {"doc_id": r[0], "title": r[1], "doc_type": r[2], "year": r[3],
                 "org": r[4], "status": r[5], "text_path": r[6]}
                for r in cur.fetchall()
            ]
        conn.close()
    except Exception as exc:  # noqa: BLE001 — PG 不可达时降级为空态
        data.error = str(exc)[:200]

    if _LINKAGE_CSV.is_file():
        try:
            import csv

            with open(_LINKAGE_CSV, encoding="utf-8-sig") as f:
                rows = list(csv.DictReader(f))
            data.linkage = rows[:50]
            data.linkage_date = rows[0].get("trade_date", "") if rows else ""
        except Exception:  # noqa: BLE001
            pass
    return data


def fetch_doc_excerpt(text_path: str, limit: int = 3000) -> str:
    try:
        text = Path(text_path).read_text(encoding="utf-8", errors="replace")
        return text[:limit]
    except OSError:
        return "（语料文件不可读）"


# ============================================================
# RAG 检索器（惰性单例，后台线程预加载模型）
# ============================================================


class RagRetriever:
    """bge-small-zh 向量检索（本地 CPU）。模型加载约 10-30 秒，后台线程预热。"""

    _instance: "RagRetriever | None" = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self.ready = False
        self.failed = ""
        self._model = None
        self._emb = None

    @classmethod
    def instance(cls) -> "RagRetriever":
        with cls._lock:
            if cls._instance is None:
                cls._instance = RagRetriever()
            return cls._instance

    def ensure_loaded(self) -> None:
        """首次提问时同步加载（后台线程加载 torch/transformers 有导入死锁风险，禁用）。"""
        if not self.ready and not self.failed:
            self._load()

    def _load(self) -> None:
        try:
            import numpy as np
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(_MODEL_NAME)
            self._emb = np.load(_CORPUS_DIR / "embeddings.npy")
            self.ready = True
        except Exception as exc:  # noqa: BLE001
            self.failed = str(exc)[:200]

    def query(self, text: str, topk: int = 5) -> list[dict]:
        if not self.ready:
            return []
        import numpy as np

        q = self._model.encode([text], normalize_embeddings=True, convert_to_numpy=True)[0]
        scores = self._emb @ q
        top = np.argpartition(-scores, topk)[:topk]
        top = top[np.argsort(-scores[top])]
        db = sqlite3.connect(_CORPUS_DIR / "chunks.sqlite")
        out = []
        for idx in top:
            row = db.execute(
                "SELECT chunk_id, title, doc_type, year, chunk_text FROM chunks WHERE rowid=?",
                (int(idx) + 1,),
            ).fetchone()
            if row:
                out.append({"score": float(scores[idx]), "chunk_id": row[0],
                            "title": row[1], "doc_type": row[2], "year": row[3], "text": row[4]})
        db.close()
        return out


# ============================================================
# render
# ============================================================


def render_industry_graph(data: IndustryGraphData) -> dict[str, Any]:
    if pn is None:
        return {"overview": data.overview, "docs": len(data.docs), "rag_ready": data.rag_ready}

    # ---- 顶部 KPI ----
    kpis = [
        ("文档总数", f"{data.overview.total_docs}"),
        ("全景图 PDF", f"{data.overview.by_type.get('panorama_pdf', 0)}"),
        ("研究报告", f"{data.overview.by_type.get('research_report', 0)}"),
        ("图谱", f"{data.overview.by_type.get('atlas_image', 0)}"),
        ("已提取文本", f"{data.overview.by_status.get('extracted', 0) + data.overview.by_status.get('ocr_done', 0)}"),
    ]
    kpi_row = pn.Row(*[
        pn.pane.Markdown(
            f"**{k}**\n\n## {v}",
            styles={"padding": "8px", "border": "1px solid #444", "border-radius": "4px",
                    "text-align": "center", "min-width": "130px"},
        )
        for k, v in kpis
    ])

    # ---- 左栏：文档浏览器 ----
    import pandas as pd

    docs_df = pd.DataFrame(data.docs)[["doc_id", "title", "doc_type", "year", "org", "status"]] if data.docs \
        else pd.DataFrame(columns=["doc_id", "title", "doc_type", "year", "org", "status"])
    # 二分定位卡死: 先静态表（Tabulator 嫌疑未排除），稳定后再加回交互
    doc_table = pn.pane.DataFrame(docs_df.head(200), height=480, sizing_mode="stretch_width")

    path_by_id = {d["doc_id"]: d.get("text_path") for d in data.docs}
    status_by_id = {d["doc_id"]: d["status"] for d in data.docs}
    title_by_id = {d["doc_id"]: d["title"] for d in data.docs}

    doc_id_input = pn.widgets.TextInput(placeholder="输入文档 ID 预览文本（如 DOC-xxxx）", width=300)
    pv_btn = pn.widgets.Button(name="预览", width=60)
    preview = pn.pane.Markdown("", height=240, styles={"overflow-y": "auto"})

    def _on_preview(event) -> None:
        doc_id = doc_id_input.value.strip()
        if doc_id not in title_by_id:
            preview.object = "文档 ID 不存在"
            return
        path = path_by_id.get(doc_id)
        if path:
            preview.object = f"**{title_by_id[doc_id]}**\n\n```\n{fetch_doc_excerpt(path)}\n```"
        else:
            preview.object = f"**{title_by_id[doc_id]}**\n\n（无提取文本，状态：{status_by_id[doc_id]}）"

    pv_btn.on_click(_on_preview)

    # ---- 右栏：RAG 问答 ----
    rag_status = pn.pane.Markdown("")
    q_input = pn.widgets.TextInput(placeholder="例如：光伏硅料环节有哪些龙头公司？", width=420)
    q_btn = pn.widgets.Button(name="提问", button_type="primary", width=80)
    answers = pn.pane.Markdown("", sizing_mode="stretch_width")

    if data.rag_ready:
        retriever = RagRetriever.instance()
        rag_status.object = "首次提问需加载模型（约 10-30 秒），之后秒回"
    else:
        retriever = None
        rag_status.object = "RAG 索引未构建（先运行 scripts/industry_graph/rag_build_index.py）"
        q_btn.disabled = True

    def _on_query(event) -> None:
        q = q_input.value.strip()
        if not q or retriever is None:
            return
        if not retriever.ready:
            answers.object = "模型加载中（约 10-30 秒）…"
            retriever.ensure_loaded()
        if not retriever.ready:
            answers.object = f"模型加载失败：{retriever.failed}"
            return
        answers.object = "检索中 …"
        hits = retriever.query(q, topk=5)
        if not hits:
            answers.object = "无命中结果"
            return
        parts = [f"**问：{q}**\n"]
        for i, h in enumerate(hits, 1):
            snippet = h["text"][:280].replace("\n", " ")
            parts.append(
                f"**[{i}] {h['title']}**（{h['doc_type']} · {h['year']} · score={h['score']:.3f}）  \n"
                f"> {snippet} …"
            )
        answers.object = "\n\n".join(parts)

    q_btn.on_click(_on_query)

    # ---- 底部：主题联动日报 ----
    if data.linkage:
        link_df = pd.DataFrame(data.linkage)[
            ["chain", "n_companies", "up_ratio", "mean_pct", "corr20", "top_symbol", "top_pct"]
        ]
        link_title = f"主题联动日报（{data.linkage_date}，0.85 互证子集）"
    else:
        link_df = pd.DataFrame(columns=["chain", "n_companies", "up_ratio", "mean_pct", "corr20"])
        link_title = "主题联动日报（未生成，先运行 theme_linkage_monitor.py）"
    link_table = pn.pane.DataFrame(link_df.head(50), height=260, sizing_mode="stretch_width")

    layout = pn.Column(
        pn.pane.Markdown("### 图谱语料库（产业链/供应链 · 内部研究用）"),
        kpi_row,
        pn.layout.Divider(),
        pn.Row(
            pn.Column(pn.pane.Markdown("**文档浏览器**（前 200 条）"), doc_table, sizing_mode="stretch_width"),
            pn.Column(pn.pane.Markdown("**RAG 语料问答**"), rag_status,
                      pn.Row(q_input, q_btn), answers, sizing_mode="stretch_width"),
            sizing_mode="stretch_width",
        ),
        pn.Row(doc_id_input, pv_btn),
        preview,
        pn.layout.Divider(),
        pn.pane.Markdown(f"**{link_title}**"),
        link_table,
        sizing_mode="stretch_width",
    )
    return {"_layout": layout}
