# [BLUEPRINT] MOD-ML-014 | docs/03_modules/_domain_machine_learning_train/decision_annotation_dataset/blueprint.md
# [MODULE] zephyr.ml_train.decision_annotation_dataset
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] sqlite3/hashlib（连接与时钟全注入；纯内存 :memory: 连接亦可）
# [CONSUMERS] 运行时装配批（SFT 样本导出/复盘数据集导出统一注入点装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 七要素 schema 闭合(decision_id/标的/时点/理由/情绪标签/图表引用/结果回填); 情绪标签词表闭合; decision_id 唯一; 结果回填仅一次且须已录入; SFT 导出仅含已回填样本; 版本快照不可变且内容 hash 确定性; 查询按 (decision_time, decision_id) 确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_machine_learning_train/decision_annotation_dataset/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] DecisionAnnotationError(占位 ZA-MLT-UNREGISTERED-DECISION-ANNOTATION)——连接未注入/字段缺失/词表外情绪/重复 decision_id/未知决策/重复回填/版本冲突时抛
# [TESTS] tests/ml_train/test_decision_annotation_dataset.py
# [A_module] module_id=MOD-ML-014 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
DecisionAnnotationDataset — 交易决策标注数据集（MOD-ML-014）。

B1-00631（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-MLT-018，C2 71）：
**决策标注七要素 Schema**（decision_id/标的/时点/理由/情绪标签/图表引用/
结果回填）+ **SQLite 标注库**（连接注入，不自建文件句柄）+ **录入结构化
校验** + **结果回填**（事后收益，仅一次）+ **SFT 样本与复盘数据集导出**
+ **版本管理**（不可变快照 + 内容 hash）。

查重分工（蓝图 §0）：training_dataset_manager=训练样本集管理（本件=人工
决策标注库与导出，不管训练 batch）；sentiment_sft_trainer=SFT 训练执行
（本件仅产出 SFT 样本载荷，不训练）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: connection 参数
#   fields: 参数 connection（无注解）
#   code: decision_annotation_dataset.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: decision_annotation_dataset.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① DecisionAnnotationDataset
#   name_en: DecisionAnnotationDataset
#   intro: 交易决策标注数据集（SQLite 注入连接 + 版本管理）。
#   desc: 交易决策标注数据集（SQLite 注入连接 + 版本管理）。；公共方法（定义序）: add_annotation, fill_outcome, export_sft_samples, export_review_dat…
#   inputs: connection clock
#   outputs: 返回值
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: DecisionAnnotationDataset
#   downstream: 运行时装配批（SFT 样本导出/复盘数据集导出统一注入点装配）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import hashlib
import logging
import sqlite3
from dataclasses import dataclass
from typing import Any, Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "AnnotationInput",
    "DatasetVersion",
    "DecisionAnnotation",
    "DecisionAnnotationDataset",
    "DecisionAnnotationError",
    "EMOTION_TAGS",
    "SftSample",
]

#: 情绪标签词表（闭合）
EMOTION_TAGS: Final[frozenset[str]] = frozenset(
    {
        "calm",
        "confident",
        "anxious",
        "fearful",
        "greedy",
        "neutral",
    }
)


class DecisionAnnotationError(Exception):
    """决策标注输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-MLT-UNREGISTERED-DECISION-ANNOTATION。
    """


@dataclass(frozen=True)
class AnnotationInput:
    """标注录入载荷（结果回填前六要素，frozen）。"""

    decision_id: str
    symbol: str
    decision_time: datetime.datetime
    rationale: str
    emotion_tag: str
    chart_ref: str


@dataclass(frozen=True)
class DecisionAnnotation:
    """完整标注记录（七要素，frozen）。"""

    decision_id: str
    symbol: str
    decision_time: datetime.datetime
    rationale: str
    emotion_tag: str
    chart_ref: str
    outcome_return: float | None
    outcome_note: str | None
    created_at: datetime.datetime


@dataclass(frozen=True)
class SftSample:
    """SFT 导出样本（frozen）。"""

    decision_id: str
    prompt: str
    completion: str
    outcome_return: float


@dataclass(frozen=True)
class DatasetVersion:
    """数据集版本快照（不可变，frozen）。"""

    version_tag: str
    n_annotations: int
    n_filled: int
    content_hash: str
    created_at: datetime.datetime


class DecisionAnnotationDataset:
    """交易决策标注数据集（SQLite 注入连接 + 版本管理）。"""

    def __init__(
        self,
        *,
        connection: sqlite3.Connection | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if connection is None:
            raise DecisionAnnotationError("sqlite connection 未注入（Fail-Closed）")
        self._conn = connection
        self._clock = clock or datetime.datetime.now
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS decision_annotations (
                decision_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                decision_time TEXT NOT NULL,
                rationale TEXT NOT NULL,
                emotion_tag TEXT NOT NULL,
                chart_ref TEXT NOT NULL,
                outcome_return REAL,
                outcome_note TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS dataset_versions (
                version_tag TEXT PRIMARY KEY,
                n_annotations INTEGER NOT NULL,
                n_filled INTEGER NOT NULL,
                content_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _row_to_annotation(row: tuple) -> DecisionAnnotation:
        return DecisionAnnotation(
            decision_id=row[0],
            symbol=row[1],
            decision_time=datetime.datetime.fromisoformat(row[2]),
            rationale=row[3],
            emotion_tag=row[4],
            chart_ref=row[5],
            outcome_return=row[6],
            outcome_note=row[7],
            created_at=datetime.datetime.fromisoformat(row[8]),
        )

    def _content_hash(self) -> str:
        """全表内容确定性 hash（按主键序拼接）。"""
        rows = self._conn.execute("SELECT * FROM decision_annotations ORDER BY decision_id").fetchall()
        digest = hashlib.sha256()
        for row in rows:
            digest.update("|".join("" if c is None else str(c) for c in row).encode("utf-8"))
            digest.update(b"\n")
        return digest.hexdigest()

    # ── 录入 ──────────────────────────────────────────────────────────────

    def add_annotation(self, entry: AnnotationInput) -> DecisionAnnotation:
        """录入标注（结构化校验 + decision_id 唯一）。"""
        if not entry.decision_id:
            raise DecisionAnnotationError("decision_id 为空")
        if not entry.symbol:
            raise DecisionAnnotationError("标的 symbol 为空")
        if not entry.rationale:
            raise DecisionAnnotationError("理由 rationale 为空")
        if entry.emotion_tag not in EMOTION_TAGS:
            raise DecisionAnnotationError(f"情绪标签词表外: {entry.emotion_tag!r}（合法: {sorted(EMOTION_TAGS)}）")
        if not entry.chart_ref:
            raise DecisionAnnotationError("图表引用 chart_ref 为空")
        exists = self._conn.execute(
            "SELECT 1 FROM decision_annotations WHERE decision_id = ?",
            (entry.decision_id,),
        ).fetchone()
        if exists is not None:
            raise DecisionAnnotationError(f"decision_id 重复: {entry.decision_id!r}")
        created_at = self._clock()
        self._conn.execute(
            """
            INSERT INTO decision_annotations
            (decision_id, symbol, decision_time, rationale, emotion_tag, chart_ref,
             outcome_return, outcome_note, created_at)
            VALUES (?, ?, ?, ?, ?, ?, NULL, NULL, ?)
            """,
            (
                entry.decision_id,
                entry.symbol,
                entry.decision_time.isoformat(),
                entry.rationale,
                entry.emotion_tag,
                entry.chart_ref,
                created_at.isoformat(),
            ),
        )
        self._conn.commit()
        _log.info("标注录入: %s (%s)", entry.decision_id, entry.symbol)
        return self.get_annotation(entry.decision_id)

    # ── 结果回填 ──────────────────────────────────────────────────────────

    def fill_outcome(self, decision_id: str, outcome_return: float, note: str = "") -> DecisionAnnotation:
        """结果回填（事后收益；须已录入且仅回填一次）。"""
        annotation = self.get_annotation(decision_id)
        if annotation.outcome_return is not None:
            raise DecisionAnnotationError(f"重复回填拒绝: {decision_id!r} 已有结果")
        self._conn.execute(
            "UPDATE decision_annotations SET outcome_return = ?, outcome_note = ? WHERE decision_id = ?",
            (float(outcome_return), note, decision_id),
        )
        self._conn.commit()
        _log.info("结果回填: %s return=%.4f", decision_id, outcome_return)
        return self.get_annotation(decision_id)

    # ── 导出 ──────────────────────────────────────────────────────────────

    def export_sft_samples(self) -> list[SftSample]:
        """导出 SFT 样本（仅含已回填标注；按 (decision_time, decision_id) 排序）。"""
        rows = self._conn.execute(
            "SELECT * FROM decision_annotations WHERE outcome_return IS NOT NULL ORDER BY decision_time, decision_id"
        ).fetchall()
        samples = []
        for row in rows:
            ann = self._row_to_annotation(row)
            prompt = (
                f"标的: {ann.symbol}\n时点: {ann.decision_time.isoformat()}\n"
                f"情绪: {ann.emotion_tag}\n图表: {ann.chart_ref}"
            )
            completion = f"决策理由: {ann.rationale}\n事后收益: {ann.outcome_return:.6f}"
            samples.append(
                SftSample(
                    decision_id=ann.decision_id,
                    prompt=prompt,
                    completion=completion,
                    outcome_return=float(ann.outcome_return),
                )
            )
        return samples

    def export_review_dataset(self) -> list[DecisionAnnotation]:
        """导出复盘数据集（全量标注；按 (decision_time, decision_id) 排序）。"""
        rows = self._conn.execute("SELECT * FROM decision_annotations ORDER BY decision_time, decision_id").fetchall()
        return [self._row_to_annotation(row) for row in rows]

    # ── 版本管理 ──────────────────────────────────────────────────────────

    def create_version(self, version_tag: str) -> DatasetVersion:
        """创建版本快照（不可变；tag 冲突拒绝）。"""
        if not version_tag:
            raise DecisionAnnotationError("version_tag 为空")
        exists = self._conn.execute("SELECT 1 FROM dataset_versions WHERE version_tag = ?", (version_tag,)).fetchone()
        if exists is not None:
            raise DecisionAnnotationError(f"版本冲突: {version_tag!r} 已存在（快照不可变）")
        n_annotations = self._conn.execute("SELECT COUNT(*) FROM decision_annotations").fetchone()[0]
        n_filled = self._conn.execute(
            "SELECT COUNT(*) FROM decision_annotations WHERE outcome_return IS NOT NULL"
        ).fetchone()[0]
        created_at = self._clock()
        version = DatasetVersion(
            version_tag=version_tag,
            n_annotations=int(n_annotations),
            n_filled=int(n_filled),
            content_hash=self._content_hash(),
            created_at=created_at,
        )
        self._conn.execute(
            "INSERT INTO dataset_versions (version_tag, n_annotations, n_filled, "
            "content_hash, created_at) VALUES (?, ?, ?, ?, ?)",
            (
                version.version_tag,
                version.n_annotations,
                version.n_filled,
                version.content_hash,
                version.created_at.isoformat(),
            ),
        )
        self._conn.commit()
        _log.info("版本快照: %s n=%d", version_tag, version.n_annotations)
        return version

    def list_versions(self) -> list[DatasetVersion]:
        """版本清单（按 (created_at, version_tag) 确定性排序）。"""
        rows = self._conn.execute(
            "SELECT version_tag, n_annotations, n_filled, content_hash, created_at "
            "FROM dataset_versions ORDER BY created_at, version_tag"
        ).fetchall()
        return [
            DatasetVersion(
                version_tag=row[0],
                n_annotations=row[1],
                n_filled=row[2],
                content_hash=row[3],
                created_at=datetime.datetime.fromisoformat(row[4]),
            )
            for row in rows
        ]

    def get_version(self, version_tag: str) -> DatasetVersion:
        """单版本查询（未知 → Fail-Closed）。"""
        row = self._conn.execute(
            "SELECT version_tag, n_annotations, n_filled, content_hash, created_at "
            "FROM dataset_versions WHERE version_tag = ?",
            (version_tag,),
        ).fetchone()
        if row is None:
            raise DecisionAnnotationError(f"未知版本: {version_tag!r}")
        return DatasetVersion(
            version_tag=row[0],
            n_annotations=row[1],
            n_filled=row[2],
            content_hash=row[3],
            created_at=datetime.datetime.fromisoformat(row[4]),
        )

    # ── 查询 ─────────────────────────────────────────────────────────────

    def get_annotation(self, decision_id: str) -> DecisionAnnotation:
        """单标注查询（未知 → Fail-Closed）。"""
        row = self._conn.execute(
            "SELECT * FROM decision_annotations WHERE decision_id = ?",
            (decision_id,),
        ).fetchone()
        if row is None:
            raise DecisionAnnotationError(f"未知决策标注: {decision_id!r}")
        return self._row_to_annotation(row)

    def stats(self) -> Mapping[str, Any]:
        """数据集统计（确定性）。"""
        n = self._conn.execute("SELECT COUNT(*) FROM decision_annotations").fetchone()[0]
        filled = self._conn.execute(
            "SELECT COUNT(*) FROM decision_annotations WHERE outcome_return IS NOT NULL"
        ).fetchone()[0]
        return {"n_annotations": int(n), "n_filled": int(filled)}
