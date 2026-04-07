---
module_id: FACTOR_LIBRARY_05_BACKTEST_BACKTEST_REORGANIZATION
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理团队
responsibility:
  - 05_BACKTEST目录BACKTEST_REORGANIZATION文档
---

# BACKTEST_REORGANIZATION

---


responsibility:
  - 提供05 Backtest相关文档支持

module_id: 02_FACTOR_LIBRARY_05_BACKTEST_001
---|
| **对象** | 单个因子 | 完整策略 |
| **目的** | 验证因子预测能力 | 验证策略交易表现 |
| **指标** | IC值、相关?| 夏普比、最大回撤、胜?|
| **频率** | 因子更新时验证| 策略运行后验证|
| **位置** | `ic_reports/` | `strategy_reports/` |

## 迁移检查清单

- [ ] 创建 `ic_reports/` 目录
- [ ] 创建 `strategy_reports/` 目录
- [ ] 迁移 `PE_TTM_IC.md` ?`ic_reports/`
- [ ] 迁移 `CORRELATION_MATRIX.md` ?`ic_reports/`
- [ ] 创建 `ic_reports/README.md`
- [ ] 创建 `strategy_reports/README.md`
- [ ] 更新 `02_FACTOR_LIBRARY/00_INDEX/README.md`
- [ ] 更新 `System_Manifest.md`
- [ ] 更新 `CHANGELOG.md`

**版本**: 1.0 | **更新**: 2026-03-28
