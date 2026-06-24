---
module_id: KE-2461
title: 8. 文件落位标准
category: module_blueprint
---

# 8. 文件落位标准

8. 文件落位标准

| 文件 | 路径 | 职责 |
|------|------|------|
| `scanner.py` | `src/zephyr/asset-inventory/scanner.py` | 全量文件系统扫描引擎（ThreadPoolExecutor） |
| `classifier.py` | `src/zephyr/asset-inventory/classifier.py` | 规则驱动四维分类器 |
| `reconciler.py` | `src/zephyr/asset-inventory/reconciler.py` | 发现清单 vs 24注册表 对账引擎 |
| `lifecycle.py` | `src/zephyr/asset-inventory/lifecycle.py` | 状态机 + MOD-INF-020 联动 |
| `dashboard.py` | `src/zephyr/asset-inventory/dashboard.py` | 健康评分 + Dashboard 生成 |
| `index_generator.py` | `scripts/governance/generators/generate_asset_index.py` | 统一资产索引生成脚本 |
| `schemas.py` | `src/zephyr/asset-inventory/schemas.py` | 本蓝图全部 Pydantic V2 模型定义 |
| `__init__.py` | `src/zephyr/asset-inventory/__init__.py` | 导出 AssetInventory / AssetScanner 等核心类 |
| `test_*.py` | `tests/asset-inventory/` | 对应测试文件 |
| `raw_asset_scan.json` | `data/scans/` | 原始扫描结果 |
| `unified_asset_index.yaml` | `data/asset_index/` | 统一资产索引 SSoT |
| `reconciliation_report.md` | `docs/09_audit/reports/` | 对账报告 |

---
