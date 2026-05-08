"""MOD-INF-026 §30 — 知识传递引擎。

KnowledgeTransferGate: Session 手交时的资产摘要注入。
下一个 AI session 从 unified_asset_index 快速定位。
"""

from __future__ import annotations

import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel


class KnowledgeTransferRecord(BaseModel):
    transferred_at: datetime
    health_score: str = "A"
    orphan_rate: float = 0.0
    total_assets: int = 0
    top_orphans: list[str] = []
    top_ghosts: list[str] = []
    top_depended_upon: list[str] = []
    recommendation: str = ""


class KnowledgeTransferGate:

    def __init__(self, project_root: Path) -> None:
        self._root = project_root

    def generate_summary(self) -> str:
        index_path = self._root / "data" / "asset_index" / "unified_asset_index.yaml"
        dep_path = self._root / "data" / "asset_index" / "dependency_graph.json"

        lines: list[str] = []
        lines.append("")
        lines.append("=" * 40)
        lines.append("  ZephyrAlpha 资产状态快照")
        lines.append(f"  生成时间: {datetime.now(timezone.utc).isoformat()}")
        lines.append("=" * 40)

        if index_path.exists():
            import yaml
            try:
                data = yaml.safe_load(index_path.read_text(encoding="utf-8"))
                if data:
                    lines.append(f"  总资产:    {data.get('total_assets', '?')}")
                    lines.append(f"  健康等级:  {data.get('health_score', '?')}")
                    lines.append(f"  孤儿率:    {data.get('orphan_rate_pct', 0):.1f}%")
                    lines.append(f"  幽灵率:    {data.get('ghost_rate_pct', 0):.1f}%")
                    lines.append(f"  漂移率:    {data.get('drift_rate_pct', 0):.1f}%")
            except Exception:
                lines.append("  (索引解析失败)")

        if dep_path.exists():
            import json
            try:
                dep = json.loads(dep_path.read_text(encoding="utf-8"))
                if dep:
                    top = dep.get("most_depended_upon", [])[:5]
                    if top:
                        lines.append(f"  最高依赖:  {', '.join(top)}")
                    cycles = dep.get("circular_dependencies", [])
                    if cycles:
                        lines.append(f"  环路警告:  {len(cycles)} 个循环依赖!")
            except Exception:
                pass

        lines.append("=" * 40)
        lines.append("")
        return "\n".join(lines)

    def write_handoff(self, output_path: Optional[Path] = None) -> Path:
        target = output_path or (self._root / "session-logs" / "_asset_handoff.txt")
        target.parent.mkdir(parents=True, exist_ok=True)

        tmp = f"{target}.{os.getpid()}.tmp"
        Path(tmp).write_text(self.generate_summary(), encoding="utf-8")
        os.replace(tmp, str(target))
        return target
