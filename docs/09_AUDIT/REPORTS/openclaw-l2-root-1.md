---
module_id: OPENCLAW_L2_ROOT_1
version: 1.0.0
status: Active
created_date: 2026-04-13
last_updated: 2026-04-13
owner: 首席文档架构师
layer: layer_09
responsibility: REPORTS
---









# OpenClaw L2 深度审计 — 批次: 仓库根目录 `.`



> **批次序号**: 1

> **目录**: `.`

> **文件数**: 18

> **审计时间**: 2026-04-08



---



## 审计汇总表



| 文件 | 核心职责(1句) | 职责问题 | 重叠文档 | 重复/版本 | YAML/链接 | 严重度 | 建议动作 |

|------|--------------|----------|----------|-----------|-----------|--------|----------|

| `README.md` | 仓库入口与快速开始指南 | 核心文档链接指向 03_TRADING_TACTICS 而非 docs/INDEX.md | `docs/INDEX.md` | 无 | 链接指向错误目录 | P1 | 更新链接指向 docs/INDEX.md |

| `CHANGELOG.md` | 系统更新日志 | 内容模板化，未实际记录变更 | 无 | 无 | YAML 正常 | P2 | 持续更新实际变更 |

| `temp_alerting_blueprint.md` | 告警蓝图临时稿 | 编码损坏（mojibake），不可读 | 可能在 01_FRAMEWORK 有正式版 | 版本未收敛 | 无有效 YAML | P0 | 编码修复后归档或删除 |

| `temp_alternative.md` | 替代数据临时稿 | 编码损坏 | `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/` | 版本未收敛 | 无有效 YAML | P0 | 同上 |

| `temp_alternative_data.md` | 替代数据临时稿(2) | 编码损坏 | `temp_alternative.md` | 重复 | 无有效 YAML | P0 | 同上 |

| `temp_analysis.md` | 分析临时稿 | 编码损坏 | 不明 | 版本未收敛 | 无有效 YAML | P0 | 同上 |

| `temp_blueprint.md` | 蓝图临时稿 | 编码损坏 | 可能在 01_FRAMEWORK | 版本未收敛 | 无有效 YAML | P0 | 同上 |

| `temp_deleted_blueprint.md` | 已删除蓝图临时稿 | 编码损坏 | 不明 | 已标记 deleted | 无有效 YAML | P0 | 确认已归档后删除 |

| `temp_deleted_nlp.md` | 已删除NLP临时稿 | 编码损坏 | 不明 | 已标记 deleted | 无有效 YAML | P0 | 同上 |

| `temp_gap.md` | 差距分析临时稿 | 编码损坏 | 不明 | 版本未收敛 | 无有效 YAML | P0 | 同上 |

| `temp_gap_analysis.md` | 差距分析临时稿(2) | 编码损坏 | `temp_gap.md` | 重复 | 无有效 YAML | P0 | 同上 |

| `temp_head_blueprint.md` | 蓝图头部临时稿 | 编码损坏 | `temp_blueprint.md` | 版本未收敛 | 无有效 YAML | P0 | 同上 |

| `temp_open_source.md` | 开源临时稿 | 编码损坏 | `docs/01_FRAMEWORK/` 可能存在正式版 | 版本未收敛 | 无有效 YAML | P0 | 同上 |

| `temp_opensource.md` | 开源临时稿(2) | 编码损坏 | `temp_open_source.md` | 重复 | 无有效 YAML | P0 | 同上 |

| `temp_risk_budget.md` | 风险预算临时稿 | 编码损坏 | `docs/11_STRATEGIC_DECISION/02_risk_budgeting/` | 版本未收敛 | 无有效 YAML | P0 | 同上 |

| `temp_risk_budget_v2.md` | 风险预算临时稿v2 | 编码损坏 | `temp_risk_budget.md` | 版本链未收敛 | 无有效 YAML | P0 | 同上 |

| `temp_risk_budget_v3.md` | 风险预算临时稿v3 | 编码损坏 | `temp_risk_budget_v2.md` | 版本链未收敛 | 无有效 YAML | P0 | 同上 |

| `temp_stress_test_spec.md` | 压力测试规格临时稿 | 编码损坏 | `docs/04_EXECUTION/` 可能存在正式版 | 版本未收敛 | 无有效 YAML | P0 | 同上 |



## 目录级职责地图



- **仓库根目录**应为：README + CHANGELOG + 配置文件

- **实际状态**：16 个 temp_*.md 文件散落根目录，全部编码损坏

- **必须归档组**：全部 16 个 temp_*.md → 归档至 `docs/06_ARCHIVE/temp_pending_encoding_fix/` 或删除（需先确认正式路径已有替代内容）

- **索引更新清单**：README.md 核心文档链接需修正



## 关键发现



1. **P0 编码灾难**：根目录 16 个 temp 文件全部为 mojibake（双重编码 UTF-8/GBK），完全不可读

2. **P1 导航错误**：README.md 链接指向 `docs/03_TRADING_TACTICS/INDEX.md` 而非 `docs/INDEX.md`

3. **版本链未收敛**：`temp_risk_budget` 有 v1/v2/v3 三版并存

4. **重复**：`temp_open_source.md` 与 `temp_opensource.md`、`temp_gap.md` 与 `temp_gap_analysis.md`、`temp_alternative.md` 与 `temp_alternative_data.md` 疑似重复

