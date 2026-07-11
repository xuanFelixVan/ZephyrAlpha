# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] zephyr.governance.kb.pipeline.batch_ingest
# [DOMAIN] D_GOV_KB
# [DEPENDENCIES] zephyr.governance.__init__; zephyr.shared.schema.schemas
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT_batch_ingest | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
批量入库 — scaffold P0/P1 知识候选批量入库（T-2-14）
=====================================================
依据：AGENTS.md §5.2-5.3、
     docs/19_development_workspace/archive/old-tree-migration-input/old-tree-asset-triage-matrix.md

功能
----
1. 读取知识候选列表（YAML 格式）
2. 逐条通过 G1 门禁入库
3. 入库成功率 ≥ 90%
4. 生成入库报告（成功/失败/跳过统计）

Safety : M
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from zephyr.governance.kb.ingest import IngestGate
from zephyr.shared.schema.schemas import Priority

__all__ = [
    "BatchIngestEntry",
    "BatchIngestReport",
    "BatchIngestor",
]

_UTC = UTC


@dataclass
class BatchIngestEntry:
    ke_id: str
    title: str
    category: str
    source_file: str
    priority: Priority = Priority.P2
    status: str = "pending"
    error: str | None = None


@dataclass
class BatchIngestReport:
    total: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0
    success_rate: float = 0.0
    entries: list[BatchIngestEntry] = field(default_factory=list)
    started_at: str = ""
    finished_at: str = ""

    def to_markdown(self) -> str:
        lines = [
            "# 批量入库报告\n",
            f"- 总数：{self.total}",
            f"- 成功：{self.succeeded}",
            f"- 失败：{self.failed}",
            f"- 跳过：{self.skipped}",
            f"- 成功率：{self.success_rate:.1%}",
            f"- 开始：{self.started_at}",
            f"- 结束：{self.finished_at}",
            "",
            "## 明细\n",
            "| KE ID | 标题 | 分类 | 优先级 | 状态 | 错误 |",
            "|-------|------|------|--------|------|------|",
        ]
        for e in self.entries:
            error = e.error or ""
            lines.append(f"| {e.ke_id} | {e.title} | {e.category} | {e.priority} | {e.status} | {error} |")
        return "\n".join(lines)


class BatchIngestor:
    # 5.44.4 修复：批次大小上限，防止单批 OOM
    MAX_BATCH_SIZE = 1000

    def __init__(
        self,
        ingest_gate: IngestGate,
        repo_root: Path | None = None,
    ) -> None:
        self._ingest_gate = ingest_gate
        self._repo_root = repo_root or Path.cwd()

    def ingest_from_yaml(self, yaml_path: Path) -> BatchIngestReport:
        if not yaml_path.exists():
            return BatchIngestReport(
                total=0,
                failed=1,
                entries=[
                    BatchIngestEntry(
                        ke_id="N/A",
                        title="YAML 文件不存在",
                        category="error",
                        source_file=str(yaml_path),
                        status="failed",
                        error=f"文件不存在：{yaml_path}",
                    )
                ],
            )

        try:
            raw = yaml_path.read_text(encoding="utf-8")
            data = yaml.safe_load(raw)
        except Exception as exc:
            return BatchIngestReport(
                total=0,
                failed=1,
                entries=[
                    BatchIngestEntry(
                        ke_id="N/A",
                        title="YAML 解析失败",
                        category="error",
                        source_file=str(yaml_path),
                        status="failed",
                        error=str(exc),
                    )
                ],
            )

        candidates = self._extract_candidates(data)
        return self._process_candidates(candidates)

    def ingest_from_list(self, candidates: list[dict[str, Any]]) -> BatchIngestReport:
        entries = [self._normalize_candidate(c) for c in candidates]
        return self._process_entries(entries)

    def _extract_candidates(self, data: Any) -> list[BatchIngestEntry]:
        if isinstance(data, list):
            return [self._normalize_candidate(item) for item in data if isinstance(item, dict)]

        if isinstance(data, dict):
            for key in ("candidates", "items", "entries", "knowledge_candidates"):
                if key in data and isinstance(data[key], list):
                    return [self._normalize_candidate(item) for item in data[key] if isinstance(item, dict)]

            p0_p1 = []
            for key, value in data.items():
                if isinstance(value, dict):
                    priority = value.get("priority", "")
                    if priority in (Priority.P0, Priority.P1):
                        entry = self._normalize_candidate(value)
                        entry.ke_id = entry.ke_id or key
                        p0_p1.append(entry)
            if p0_p1:
                return p0_p1

        return []

    def _normalize_candidate(self, item: dict[str, Any]) -> BatchIngestEntry:
        return BatchIngestEntry(
            ke_id=str(item.get("module_id", item.get("ke_id", ""))),
            title=str(item.get("title", "")),
            category=str(item.get("category", "general")),
            source_file=str(item.get("source_file", item.get("path", ""))),
            priority=Priority(item.get("priority", Priority.P2.value)),
        )

    def _process_candidates(self, candidates: list[BatchIngestEntry]) -> BatchIngestReport:
        p0_p1 = [c for c in candidates if c.priority in (Priority.P0, Priority.P1)]
        if not p0_p1:
            p0_p1 = candidates

        return self._process_entries(p0_p1)

    def _process_entries(self, entries: list[BatchIngestEntry]) -> BatchIngestReport:
        # 5.44.4 修复：批次大小校验，超过 MAX_BATCH_SIZE 抛 ValueError
        if len(entries) > self.MAX_BATCH_SIZE:
            raise ValueError(
                f"BatchIngestor 批次大小 {len(entries)} 超过上限 {self.MAX_BATCH_SIZE}，请分片处理"
            )

        report = BatchIngestReport(
            total=len(entries),
            started_at=datetime.now(_UTC).isoformat(),
        )

        for entry in entries:
            if not entry.ke_id or not entry.source_file:
                entry.status = "skipped"
                entry.error = "缺少 ke_id 或 source_file"
                report.skipped += 1
                report.entries.append(entry)
                continue

            source_path = self._resolve_source(entry.source_file)
            if source_path is None:
                entry.status = "skipped"
                entry.error = f"源文件不存在：{entry.source_file}"
                report.skipped += 1
                report.entries.append(entry)
                continue

            result = self._ingest_gate.ingest(source_path)

            if result.passed:
                entry.status = "succeeded"
                report.succeeded += 1
            else:
                entry.status = "failed"
                entry.error = "; ".join(result.violations[:3])
                report.failed += 1

            report.entries.append(entry)

        if report.total > 0:
            report.success_rate = report.succeeded / report.total

        report.finished_at = datetime.now(_UTC).isoformat()
        return report

    def _resolve_source(self, source_file: str) -> Path | None:
        if not source_file:
            return None

        candidates = [
            self._repo_root / source_file,
            Path(source_file),
        ]

        for p in candidates:
            if p.exists():
                return p

        return None
