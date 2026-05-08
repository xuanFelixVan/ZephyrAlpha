"""AssetDashboard — MOD-INF-026 资产健康仪表盘生成器

蓝图 §5 + §27：读取 unified_asset_index.yaml → 生成 dashboard.json
含健康评分、分类统计、趋势数据、告警。"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from zephyr.asset_inventory.models import DashboardData, UnifiedAssetIndex, HealthScore

logger = logging.getLogger(__name__)

REPORTS_DIR = Path(__file__).resolve().parents[3] / "data" / "reports"
DASHBOARD_PATH = REPORTS_DIR / "dashboard.json"


class Dashboard:
    """资产健康仪表盘生成器——Phase 1 实现（蓝图 §5）。"""

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or Path(__file__).resolve().parents[3]

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

    def save(self, dashboard: DashboardData, output_path: Optional[Path] = None) -> Path:
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
        print(f"\n{'='*50}")
        print(f"  ZephyrAlpha 资产仪表盘")
        print(f"{'='*50}")
        print(f"  健康评分: {dashboard.health_score}")
        print(f"  总资产:   {dashboard.total_assets}")
        print(f"  孤儿率:   {dashboard.orphan_rate_pct:.1f}%")
        print(f"  幽灵率:   {dashboard.ghost_rate_pct:.1f}%")
        print(f"  漂移率:   {dashboard.drift_rate_pct:.1f}%")
        if dashboard.alerts:
            print(f"  ⚠️  告警:")
            for a in dashboard.alerts:
                print(f"    - {a}")
        print(f"{'='*50}")

    def main(self) -> None:
        index_path = self.root / "data" / "asset_index" / "unified_asset_index.yaml"
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
    now = datetime.now(timezone.utc)
    seq = str(now.timestamp()).replace(".", "")[-3:]
    return f"DASH-{now.strftime('%Y%m%d')}-{seq}"


def main() -> None:
    Dashboard().main()


if __name__ == "__main__":
    main()
