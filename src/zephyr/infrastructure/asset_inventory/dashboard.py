# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain-infra_ops/asset-inventory/blueprint.md
# [MODULE] zephyr.infrastructure.asset_inventory.dashboard
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_dashboard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""AssetDashboard — MOD-INF-026 资产健康仪表盘生成器

蓝图 §5 + §27：读取 unified-asset-index.yaml → 生成 dashboard.json
含健康评分、分类统计、趋势数据、告警。"""

import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path

from zephyr.infrastructure.asset_inventory.models import DashboardData, UnifiedAssetIndex
from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

REPORTS_DIR = REPO_ROOT / "data" / "reports"
DASHBOARD_PATH = REPORTS_DIR / "dashboard.json"


class Dashboard:
    """资产健康仪表盘生成器——Phase 1 实现（蓝图 §5）。"""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or REPO_ROOT

    def generate(self, index: UnifiedAssetIndex) -> DashboardData:
        logger.info("生成仪表盘...")

        alerts: list[str] = []
        if index.orphan_rate_pct > 2.0:
            alerts.append(f"孤儿率 {index.orphan_rate_pct:.1f}% 超过 2% 阈值")
        if index.ghost_rate_pct > 1.0:
            alerts.append(f"幽灵率 {index.ghost_rate_pct:.1f}% 超过 1% 阈值")
        if index.drift_rate_pct > 5.0:
            alerts.append(f"漂移率 {index.drift_rate_pct:.1f}% 超过 5% 阈值")

        return DashboardData(
            dashboard_id=_generate_dashboard_id(),
            health_score=index.health_score,
            total_assets=index.total_assets,
            orphan_rate_pct=index.orphan_rate_pct,
            ghost_rate_pct=index.ghost_rate_pct,
            drift_rate_pct=index.drift_rate_pct,
            by_type=index.by_type,
            by_layer=index.by_layer,
            alerts=alerts,
            last_reconciliation=index.last_reconciliation_at.isoformat() if index.last_reconciliation_at else None,
        )

    def save(self, dashboard: DashboardData, output_path: Path | None = None) -> Path:
        target = output_path or DASHBOARD_PATH
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        payload = dashboard.model_dump(mode="json")
        content = json.dumps(payload, ensure_ascii=False, indent=2)

        tmp = f"{target}.{os.getpid()}.tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp, target)
        except PermissionError:
            try:
                os.remove(tmp)
            except OSError:
                pass
            raise

        logger.info("仪表盘已写入: %s", target)
        return Path(target)

    def print_summary(self, dashboard: DashboardData) -> None:
        print(f"\n{'=' * 50}")
        print("  ZephyrAlpha 资产仪表盘")
        print(f"{'=' * 50}")
        print(f"  健康评分: {dashboard.health_score}")
        print(f"  总资产:   {dashboard.total_assets}")
        print(f"  孤儿率:   {dashboard.orphan_rate_pct:.1f}%")
        print(f"  幽灵率:   {dashboard.ghost_rate_pct:.1f}%")
        print(f"  漂移率:   {dashboard.drift_rate_pct:.1f}%")
        if dashboard.alerts:
            print("  ⚠️  告警:")
            for a in dashboard.alerts:
                print(f"    - {a}")
        print(f"{'=' * 50}")

    def main(self) -> None:
        index_path = self.root / "data" / "asset_index" / "unified-asset-index.yaml"
        if not index_path.exists():
            print("警告: 索引文件不存在，先运行 index_generator")
            return

        import yaml

        raw = yaml.safe_load(index_path.read_text(encoding="utf-8"))
        index = UnifiedAssetIndex(**raw)

        dashboard = self.generate(index)
        out = self.save(dashboard)
        self.print_summary(dashboard)
        print(f"  OUTPUT {out}")


def _generate_dashboard_id() -> str:
    now = datetime.now(UTC)
    seq = str(now.timestamp()).replace(".", "")[-3:]
    return f"DASH-{now.strftime('%Y%m%d')}-{seq}"


def main() -> None:
    Dashboard().main()


if __name__ == "__main__":
    main()

# ============================================================================
# SRC-0040: 从 knowledge_transfer.py 合并 — KnowledgeTransferGate
# ============================================================================

from pydantic import BaseModel as _PydanticBaseModel


class KnowledgeTransferRecord(_PydanticBaseModel):
    transferred_at: datetime
    health_score: str = "A"
    orphan_rate: float = 0.0
    total_assets: int = 0
    top_orphans: list[str] = []
    top_ghosts: list[str] = []
    top_depended_upon: list[str] = []
    recommendation: str = ""


class KnowledgeTransferGate:
    """Session 手交时的资产摘要注入——下一个 AI session 从 unified-asset-index 快速定位。"""

    def __init__(self, project_root: Path) -> None:
        self._root = project_root

    def generate_summary(self) -> str:
        index_path = self._root / "data" / "asset_index" / "unified-asset-index.yaml"

        lines: list[str] = []
        lines.append("")
        lines.append("=" * 40)
        lines.append("  ZephyrAlpha 资产状态快照")
        lines.append(f"  生成时间: {datetime.now(UTC).isoformat()}")
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

        try:
            from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

            conn = get_depgraph_pg_connection(autocommit=True)
            with conn.cursor() as cur:
                cur.execute("SELECT node_id FROM nodes ORDER BY fan_in DESC LIMIT 5")
                top = [row["node_id"] for row in cur.fetchall()]
            conn.close()
            if top:
                lines.append(f"  最高依赖:  {', '.join(str(t) for t in top)}")
        except Exception as e:
            logger.debug("suppressed error in dashboard", exc_info=True)

        lines.append("=" * 40)
        lines.append("")
        return "\n".join(lines)

    def write_handoff(self, output_path: Path | None = None) -> Path:
        target = output_path or (self._root / "session_logs" / "_asset_handoff.txt")
        target.parent.mkdir(parents=True, exist_ok=True)

        tmp = f"{target}.{os.getpid()}.tmp"
        Path(tmp).write_text(self.generate_summary(), encoding="utf-8")
        os.replace(tmp, str(target))
        return target
