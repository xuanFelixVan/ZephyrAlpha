---

module_id: 09_AUDIT_STATE_ARCH_MODULE_GAP_REGISTER_20260408

version: 1.6.0

status: Active

created_date: 2026-04-08

last_updated: '2026-04-08'

owner: 项目负责人

standard_type: 审计台账

applicable_scope: 架构与模块缺口登记

layer: layer_09
responsibility: "处理ARCH_MODULE_GAP_REGISTER_20260408相关业务"
---





# 模块缺口与矛盾登记表



> **程序依据**：`../PROCEDURES/ARCHITECTURE_MODULE_AUDIT_AND_GAP_PLAN_20260408.md`  

> **本轮垂直切片**：Layer 0→1 数据 → Layer 2 因子 → Layer 5 回测 → 绩效可读结果  



## 登记表



| ID | 缺陷类 | 模块/能力名 | 发现位置（路径） | 与权威栈关系 | 简述 | P0/P1/P2 | 补缺动作（草案） | 状态 |

|----|--------|-------------|------------------|--------------|------|----------|------------------|------|

| G-001 | G3 | 策略引擎所属 Layer | `MODULE_RESPONSIBILITY_BOUNDARIES.md` | 须与 `ARCHITECTURE.md` 一致 | 原「Layer 3 + Layer 5」矛盾 | P0 | 改为 Layer 5 | **已修正** |

| G-002 | G2 | 文首元数据 / YAML | `ARCHITECTURE.md` | 权威文档可解析 | 多段 `---` 与断裂 YAML | P1 | 合并为单一 front matter | **已修正**（2026-04-08） |

| G-003 | G2 | 映射表与文首 | `BLUEPRINT_ARCHITECTURE_MAPPING.md` | 对齐 ARCHITECTURE | 双 YAML、断表、乱码 | P1 | 重写为 v1.1 可读版 | **已修正**（2026-04-08） |

| G-004 | G1 | Layer 9～11 索引 | `MODULE_RESPONSIBILITY_BOUNDARIES.md` | ARCHITECTURE 已展开 | 边界文档缺系统索引 | P1 | 增加主蓝图表 | **已修正**（2026-04-08） |

| G-005 | G5 | 回测引擎入口 | `MODULE_RESPONSIBILITY_BOUNDARIES.md` | 需 canonical 蓝图 | 仅有模块名无路径 | P1 | 链到 FACTOR_BACKTEST_INTEGRATION | **已修正**（2026-04-08） |

| G-006 | G5 | L0→L1 契约入口 | `ARCHITECTURE.md` §4.2 | 数据流权威 | 缺单一契约链 | P1 | 指向 `docs/03_TRADING_TACTICS/API_Contract.md` | **已修正**（2026-04-08） |

| G-007 | G3 | 业务↔Layer 对照 | `BLUEPRINT_ARCHITECTURE_MAPPING.md` | 可逐条对照 | 旧版损坏 | P2 | 随 G-003 关闭 | **已修正**（2026-04-08） |

| G-008 | G4 | 蓝图全量挂载 | `01_BLUEPRINTS/*.md` | 总纲可指回 | 未全量核对 | P2 | `INDEX.md` 全量列表 + MAPPING/ARCHITECTURE 互链 | **已修正**（2026-04-08 批次 C） |

| G-009 | G1 | 风控横切索引 | `MODULE_RESPONSIBILITY_BOUNDARIES.md` | ARCHITECTURE 叙述 | 缺集中索引 | P2 | 增加风控索引段 + 蓝图链 | **已修正**（2026-04-08） |

| G-010 | G2 | `module_id` 唯一 | `ARCHITECTURE.md` | Sentinel 首道 FM | 混用 ARCHITECTURE / ARCHITECTURE_001 | P1 | 统一为 `ARCHITECTURE_001` | **已修正**（随 G-002） |

| G-011 | G5 | 因子库 ↔ 蓝图文件 | `MODULE_RESPONSIBILITY_BOUNDARIES.md` | FACTOR_BACKTEST_001 | ID 与文件未互链 | P2 | 链 ALPHA_FACTOR_FACTORY + 集成蓝图 | **已修正**（2026-04-08） |

| G-012 | G1 | 双轨裁决 | `module_designs` vs `01_FRAMEWORK` | 权威栈 | 未写明 | P2 | 边界文档「双轨说明」 | **已修正**（2026-04-08） |

| G-013 | G4 | Layer 11 子能力映射 | `ARCHITECTURE.md` §Layer 11 | 逐项↔蓝图 | 对照表 22/22；宏观因子主链见 MACRO 专篇 | P2 | 见 LAYER11_CAPABILITY_TO_BLUEPRINT_MAP_20260408.md v1.2 | **已修正**（批次 E+F） |

| G-014 | G5 | 舆情 vs 策略 | `MODULE_RESPONSIBILITY_BOUNDARIES.md` | 读者理解 | 易混淆 | P2 | Layer3→5 段 + API_Contract | **已修正**（2026-04-08） |

| G-015 | G2 | 正文乱码 | `ARCHITECTURE.md` 等 | 可读性 | §4.1 改为可读表、§5 P0 表与页脚、Layer 10 表等已清 `?` | P1 | 其他框架文档零星乱码随编辑顺带修 | **已修正**（`ARCHITECTURE.md` 本文件；2026-04-08 批次 F+） |



## 新增登记（全库持续）



| ID | 缺陷类 | 模块/能力名 | 发现位置 | 简述 | P | 状态 |

|----|--------|-------------|----------|------|---|------|

| G-016 | P2 | `01_BLUEPRINTS` 总索引 | `01_BLUEPRINTS/INDEX.md` | 需可复现更新 | 增加 `generate_01_blueprints_index.py` 与全量列表 | P2 | **已修正**（2026-04-08 批次 C） |



## Deferred / 说明



- **G-008 / G-013 / G-016**：接受「权威入口已具备、全量挂载分期」；下轮可脚本化蓝图文件名清单对账。  

- **G-015**：`ARCHITECTURE.md` 已收口；其余 `.md` 仍建议随小节编辑顺带清理乱码。



## 质量门（本轮执行后）



- [x] L1：**无效内链 = 0**（2026-04-08 扫描，批次 F 后复扫）  

- [x] 权威栈：`ARCHITECTURE` ↔ `MODULE_RESPONSIBILITY` ↔ `BLUEPRINT_ARCHITECTURE_MAPPING` ↔ `API_Contract` 可点击通达  

- [x] Q3 长期：Layer 11 子表与蓝图逐条核验（G-013；对照表 v1.2，22/22）

