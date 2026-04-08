---
module_id: 09_AUDIT_STATE_ARCH_MODULE_GAP_REGISTER_20260408
version: 1.0.0
status: Active
created_date: 2026-04-08
last_updated: 2026-04-08
owner: 项目负责人
standard_type: 审计台账
applicable_scope: 架构与模块缺口登记
---

# 模块缺口与矛盾登记表

> **程序依据**：[`../PROCEDURES/ARCHITECTURE_MODULE_AUDIT_AND_GAP_PLAN_20260408.md`](../PROCEDURES/ARCHITECTURE_MODULE_AUDIT_AND_GAP_PLAN_20260408.md)  
> **本轮垂直切片**：Layer 0→1 数据 → Layer 2 因子 → Layer 5 回测 → 绩效可读结果  

## 登记表

| ID | 缺陷类 | 模块/能力名 | 发现位置（路径） | 与权威栈关系 | 简述 | P0/P1/P2 | 补缺动作（草案） | 状态 |
|----|--------|-------------|------------------|--------------|------|----------|------------------|------|
| G-001 | G3 | 策略引擎所属 Layer | `docs/01_FRAMEWORK/MODULE_RESPONSIBILITY_BOUNDARIES.md` | 须与 `ARCHITECTURE.md` Layer 3=舆情 一致 | 原文写「Layer 3 + Layer 5」与总架构矛盾 | P0 | 改为 Layer 5，并更新变更记录 | **已修正**（2026-04-08） |
| G-002 | G2 | 文首元数据 / `module_id` | `docs/01_FRAMEWORK/ARCHITECTURE.md` | 权威文档自身应可解析 | 文首多段 `---`、重复/断裂 YAML，不利于治理脚本与人工阅读 | P1 | 按 ADR-OC-001 合并为单一 front matter，并修编码 | 待处理 |
| G-003 | G2 | 文首元数据 / 表格 | `docs/01_FRAMEWORK/BLUEPRINT_ARCHITECTURE_MAPPING.md` | 映射表应对齐 `ARCHITECTURE.md` | 双 YAML、表格断行、乱码片段，映射不可机读 | P1 | 修复 Markdown 表格与 front matter，与 Layer 0-11 再对照 | 待处理 |
| G-004 | G1 | Layer 9～11 模块级职责 | `docs/01_FRAMEWORK/MODULE_RESPONSIBILITY_BOUNDARIES.md` | `ARCHITECTURE.md` 已展开 9～11 | 边界文档以回测链为主，未系统覆盖研究/治理/战略各子模块 | P1 | 增加「高层模块索引」节或链向各层主蓝图 | 待处理 |
| G-005 | G5 | 回测执行引擎（Backtrader） | `docs/01_FRAMEWORK/MODULE_RESPONSIBILITY_BOUNDARIES.md` | 边界已命名模块 | 未给出 canonical 实现/蓝图路径（读者找不到「唯一入口」） | P1 | 在边界表增加指向 `01_BLUEPRINTS` 或 `05_IMPLEMENTATION` 具体文档链接 | 待处理 |
| G-006 | G5 | L0→L1 数据接口 | `docs/01_FRAMEWORK/ARCHITECTURE.md` §4.2 | 数据流权威描述 | 有数据类型表，缺「单一契约入口」链（如 API_Contract） | P1 | 在 ARCHITECTURE 或边界文档显式链到 `docs/03_TRADING_TACTICS/API_Contract.md` 或替代权威 | 待处理 |
| G-007 | G3 | 业务视角 Layer 与流水线 Layer | `docs/01_FRAMEWORK/BLUEPRINT_ARCHITECTURE_MAPPING.md` | 须与 `ARCHITECTURE.md` 可逐条对照 | 映射节部分损坏，无法完成自动对照 | P2 | 待 G-003 修复后重跑对照审 | 待处理 |
| G-008 | G4 | 蓝图挂载 | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/*.md` | 总架构/映射应能指回 | 大量蓝图是否在总纲或 MAPPING 中有挂载点未做全量核对 | P2 | 维护 Blueprint 总索引或在 MAPPING 中分批登记 | 待处理 |
| G-009 | G1 | 风控「贯穿各层」 | `docs/01_FRAMEWORK/ARCHITECTURE.md` | 叙述要求融入各层 | `MODULE_RESPONSIBILITY_BOUNDARIES` 未给风控横切职责索引 | P2 | 增加横切小节或链到风险类主蓝图 | 待处理 |
| G-010 | G2 | `module_id` 唯一语义 | `docs/01_FRAMEWORK/ARCHITECTURE.md` | 与 Sentinel 首道 FM 口径一致 | 文首出现 `ARCHITECTURE` / `ARCHITECTURE_001` 等混用 | P1 | 统一为首道 `module_id` 与版本字段 | 待处理 |
| G-011 | G5 | 因子库模块 ID 与文件 | `MODULE_RESPONSIBILITY_BOUNDARIES.md`（FACTOR_BACKTEST_001） | 蓝图命名应对应真实文件 | 需核对是否对应具体 `*_BLUEPRINT.md` 文件名 | P2 | grep `FACTOR_BACKTEST` 与因子库蓝图互链 | 待处理 |
| G-012 | G1 | `module_designs` vs `01_FRAMEWORK` | `docs/module_designs/`、`docs/01_FRAMEWORK/` | 权威栈未写明双轨关系 | 个人仓库两套设计树并存时，冲突裁决未写入方案 | P2 | 在 `GOVERNANCE_DECISIONS` 或本方案权威栈中增加一条 | 待处理 |
| G-013 | G4 | Layer 11 子能力 | `docs/01_FRAMEWORK/ARCHITECTURE.md` §Layer 11 表 | 每项应对应蓝图或规格 | 表列极多，是否与 `STRATEGIC_DECISION_LAYER_BLUEPRINT` 等一一对应未核验 | P2 | 做一张「能力→文档」简表 | 待处理 |
| G-014 | G5 | Layer 3 舆情 vs Layer 5 策略 | 两文档并列 | 读者易混淆 | 已在职责地图分层，可增加互链说明「舆情信号如何进策略」 | P2 | 在边界文档加 1 段与数据流引用 | 待处理 |
| G-015 | G2 | 文档编码与显示 | `ARCHITECTURE.md`、`MODULE_RESPONSIBILITY_BOUNDARIES.md` 等 | 影响专业审阅 | 部分中文字符显示为 `?` 类乱码 | P1 | UTF-8 重存 + 抽查关键段落 | 待处理 |

## Deferred / 说明

- **本轮未开**：`01_BLUEPRINTS` 全量孤儿扫描、`module_designs` 全量对照（见方案第二节目录勾选）。  
- **已完成补缺**：G-001（策略引擎 Layer 与总架构对齐）。

## 质量门（本轮）

- [x] 登记行数 ≥ 15  
- [x] P0 条数 ≤ 7（本轮 P0 仅 G-001，且已关闭）  
- [ ] Q3：权威栈互链完善（待 G-006 等 P1 完成后复检）  
- [x] L1：本批修改后运行 `sentinel_l1_governance_scan.py`（见提交前检查）
