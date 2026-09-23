# [BLUEPRINT] MOD-LIB-004 | docs/03_modules/_domain_library/blueprint.md | §4
# [MODULE] zephyr.library.collectors.logs_collector
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.library.ledger_schema (derive_asset_id)
# [CONSUMERS] zephyr.library.collectors; scripts/governance/generators/check_library_coverage.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只读 registry_of_logs.yaml（REG-LOG-001，日志抽屉 SSOT）；一登记条目=一族抽屉资产（方案 A 族级入册，不逐件登记日志文件）；日志族不入 fs 扫描面（fs_collector 白名单不含 logs/），故 coverage 对账必须并入本采集器结果防 ghost 误报；SQL 零（纯 YAML 读取）；注册表缺失返回单条 error 记录（fail-soft）
# [MODIFY-GUARD] gate_id 不适用
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 任何异常折叠为 [{"error": ...}]（collect_all 兜底）
# [TESTS] tests/library/test_logs_collector.py
# [A_module] module_id=MOD-LIB-004 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""logs_collector — 图书馆采集器（MOD-LIB-004，只读）：日志抽屉族级入册（ulib3 T10）。

方案 A（Owner 定案）：日志不逐件入册——registry_of_logs.yaml 每条=一个抽屉族，
本采集器把 98 条抽屉登记为总账资产（home=载体路径），AI 查抽屉后进大盘自找文件。
Owner 目标：每个模块的回测日志都必须有抽屉且图书馆查得到（覆盖核验=T10 验收报告）。

# [ALGO_FLOW] external: docs/03_modules/_domain_library/algo_flow/collectors/logs_collector.yaml
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Final

import yaml

from zephyr.library.ledger_schema import derive_asset_id

__all__ = ["collect"]  # noqa: n114-final  n114-final豁免: __all__是Python导出约定，非可变常量，无需Final标注（先例=asyncio_run_in_context_gate.py L77）

LOG_REGISTRY_REL: Final[str] = "docs/01_policies_and_standards/_registry/catalogs/registry_of_logs.yaml"

# 登记状态→总账状态映射（legacy=仍在册但不再写入，挂 archived 防对账误报）
_STATUS_MAP: Final[dict[str, str]] = {"active": "active", "legacy": "archived"}


def collect(root: str = ".") -> list[dict[str, Any]]:
    """读日志总索引，产出抽屉族资产列表（fail-soft）。

    Args:
        root: 仓库根。

    Returns:
        资产列表；异常折叠为 [{"error": ...}]。
    """
    try:
        reg_path = Path(root) / LOG_REGISTRY_REL
        if not reg_path.exists():
            return [{"error": f"registry_of_logs.yaml 不存在: {LOG_REGISTRY_REL}"}]
        data = yaml.safe_load(reg_path.read_text(encoding="utf-8")) or {}
        assets: list[dict[str, Any]] = []
        for entry in data.get("logs") or []:
            path = str(entry.get("path") or "").strip()
            if not path:
                continue
            status = _STATUS_MAP.get(str(entry.get("status") or "active"), "active")
            writers = entry.get("writers") or []
            log_id = str(entry.get("log_id") or "").strip()
            # 占位/模板/仓外 path 不是可定位 home：旧口径一律按 path 派生索书号，
            # 两条抽屉共用同一占位串即塌缩成同一 asset_id（实测 registry_of_logs 98 条
            # 只出 97 唯一号）。此类改以登记册条目本身定位（不猜真实路径，禁猜配先例）。
            placeholder = bool(log_id) and any(ch in path for ch in "{}<>（:")
            home = f"{LOG_REGISTRY_REL}#{log_id}" if placeholder else path
            assets.append(
                {
                    "asset_id": derive_asset_id("file", home),
                    "kind": "file",
                    "home": home,
                    "status": status,
                    "title": entry.get("name_zh") or entry.get("log_id"),
                    "ai_contract": (
                        f"日志抽屉（{entry.get('kind', '')}，log_id={entry.get('log_id')}）："
                        f"{entry.get('schema_summary', '')} 写入方：{', '.join(writers) if writers else '未登记'}；"
                        f"保留期：{entry.get('retention', '未登记')}。抽屉族索引=registry_of_logs.yaml，"
                        "明细文件进大盘自查（方案 A 族级入册）。"
                    ),
                    "owner_domain": None,
                    "tags": ["日志"],
                    "retention_class": "long",
                }
            )
        return assets
    except Exception as e:  # noqa: BLE001 — fail-soft（collect_all 兜底口径）
        return [{"error": f"{type(e).__name__}: {e}"}]
