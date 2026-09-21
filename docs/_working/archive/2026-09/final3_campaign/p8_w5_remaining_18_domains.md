---
ttl: task_bound
completes_when: P14 终局报告落盘
title: W5-1 余 18 域三档清单册（P8 承接 W5-1 四簇后余域挖矿）
session: st-maxexec-20260920
date: 2026-09-20
---

# W5-1 余 18 域三档清单册 — final3 P8 / 任务 B

> 判据铁律（同 W5-1）：同真源可派生→必并｜零触发零消费→退役｜同域重复簇→收敛唯一｜跨域不同对象→不并。
> **本件只出清单不执行**（执行归 P11 消化循环）。证据等级：A=本会话机读实测；B=推断（声明性证据或松口径）。

## 0. 方法与口径

- **依据**：`w5_1_cluster_audit.md`（四簇已做）+ 裁定#371（余 18 域分包全权承接）+ `skeleton_mining_policy.md` 挖矿 SOP 精神（先挖干再判：机械探针先行，逐域四步）。
- **划分**：22 域 = W5-1 已做 4 簇（资源配置簇 / decisiongraph 簇 / scripts 动词簇 / module_id 锚城簇）+ 本册 18 域。18 域按 src/zephyr 56 个顶包聚合自定（见 §2 分组表）；`feedback_loop`、`shared` 两包与 `infra_runtime` 的资源配置面归四簇已覆盖域，不重复计。
- **探针**：`.runtime/tmp/p8_w5_domains_probe.py`（只读，24h TTL）→ `.runtime/tmp/p8_w5_domains_probe.json`；计划任务对账复用 W5-1 dump `.runtime/tmp/w5_1_tasks_dump.txt`（43 个 Zephyr 任务）。
- **逐域四步**：①资产盘点（py/LOC/唯一 module_id/蓝图数）②消费方实测（跨域 import 组数+域外文件数+计划任务）③判据应用 ④三档结论（合并/退役/保留）。
- **消费方口径警示（同 W5-1 簇3 B 级）**：import 图覆盖静态引用；动态/string import 与手工入口不能完全排除——退役结论一律标注证据等级，P11 执行前复核。

## 1. 汇总表（18 域三档总览）

| # | 域 | 包构成 | py | LOC | mids | 域外import组 | 计划任务 | 三档结论 |
|---|---|------|----|-----|------|------------|---------|---------|
| 1 | D_MKT_DATA | market_data+alt_data | 45 | 9,268 | 36 | 3 | 0 | 保留 |
| 2 | D_DATA_ENG | data+data_eng+integration | 232 | 93,039 | 110 | 15 | 1(data) | 保留 |
| 3 | D_DATA_GOV | data_governance+data_security | 31 | 4,175 | 25 | **0** | 0 | **退役候选** |
| 4 | D_KNOWLEDGE | knowledge+intelligence+nlp | 99 | 29,390 | 56 | 9 | 0 | 保留 |
| 5 | D_ML | ml_train+ml_serve+experiment_tracking | 67 | 10,232 | 36 | 5 | 0 | 保留（蓝图薄） |
| 6 | D_AI_AUTONOMY | ai_layer+autonomy_core+red_blue_validator | 153 | 29,741 | 23 | 5 | 0 | 保留 |
| 7 | D_FACTOR | factor | 87 | 18,253 | 41 | 8 | 1(factor) | 保留 |
| 8 | D_SIGNAL | signal_ashare+signal_fundamental+signal_quality+cross_asset | 209 | 52,691 | 137 | 6 | 0 | 保留（蓝图薄） |
| 9 | D_RISK_COMPLIANCE | risk+compliance | 108 | 31,362 | 60 | 5 | 0 | 保留 |
| 10 | D_PORTFOLIO | pf_alloc+pf_core+position+regime | 147 | 49,650 | 82 | 10 | 0 | 保留 |
| 11 | D_TRADING_CORE | trading+plan_engine+sell_decision+strategy_factory+strategy_pipeline | 190 | 53,204 | 95 | 13 | 1(trading) | 保留 |
| 12 | D_EXECUTION_SIM | ex_core+ex_sor+execution_simulation+simulation+digital_twin | 131 | 37,925 | 58 | 7 | 0 | 保留 |
| 13 | D_BACKTEST | backtest | 55 | 19,298 | 13 | 5 | 0 | 保留 |
| 14 | D_ORCH_RUNTIME | orchestrator+runtime | 75 | 13,149 | 9 | 3 | 1(runtime) | 保留 |
| 15 | D_GOV_CORE | governance+gov_audit+gov_code_quality | 439 | 96,842 | 77 | 11 | 1(governance) | 保留 |
| 16 | D_GOV_RULES | gov_rule+gov_drift+gov_enforcement | 286 | 88,028 | 41 | 8 | 1(gov_enforcement) | 保留 |
| 17 | D_INFRA_SEC | infrastructure+infra_ops+infra_runtime+security+clone_guard | 555 | 103,218 | 115 | 14 | 3 | 保留 |
| 18 | D_FRONT_REPORT | frontend+reporting+research | 96 | 31,403 | 51 | 5 | 0 | 保留 |

**三档分布：保留 17 / 退役候选 1（D_DATA_GOV）/ 合并候选 0**；另出 4 条待执行项（§4，归 P11）。

## 2. 逐域清单（四步记录）

### 2.1 D_MKT_DATA（market_data+alt_data）
①45 py / 9,268 LOC / 36 唯一 module_id / 16 蓝图。②域外 import 组=3，计划任务=0。③判据：多组消费+alt_data 为 W7 股权穿透在建线（00_master_directive W7-1..W7-4）。④**保留**。备注：W7 施工完成后建议复测消费面。

### 2.2 D_DATA_ENG（data+data_eng+integration）
①232 py / 93,039 LOC / 110 mids / 75 蓝图——18 域中体量第二。②域外 import 组=15（最高扇入之一），`data` 包=数据集成器 7 子命令（AGENTS §7）+ 计划任务在册。③判据：核心入数管线，多活消费。④**保留**。

### 2.3 D_DATA_GOV（data_governance+data_security）★退役候选
①31 py / 4,175 LOC / 25 mids / 14 蓝图文件；包根 blueprint 标 `(pending)`。②**消费方实测全零（A 级）**：跨域 import 组=0、域外文件 import=0、计划任务=0、pyproject/api_server/frontend 零引用、全仓字符串级引用（data_masking_engine/openlineage_exporter/column_lineage_tracker/ai_masking_pipeline/asset_auto_discovery）零外部命中；配套测试 15 件仍在（tests/data_governance 14 + tests/data_security 1）。③判据应用：零触发零消费→**退役成立**（唯一保留疑点=动态/手工入口不可机械排除，B 级口径警示）。**撞名危害（连带发现）**：`src/zephyr/governance/data_governance/`（数据源 provider 群，26 文件消费，活）与本域 `src/zephyr/data_governance/`（lineage/masking 群，零消费）同名不同物——跨域不同对象→不并，但同名撞车构成发现性危害（import 走错包风险）。④**退役候选**：整簇 31 件+15 测试件退役评估 → P11（退役须先 salvage 存档，比照 O-2 流程）。

### 2.4 D_KNOWLEDGE（knowledge+intelligence+nlp）
①99 py / 29,390 LOC / 56 mids / 34 蓝图。②域外 import 组=9。③判据：知识/情报层多组消费。④**保留**。

### 2.5 D_ML（ml_train+ml_serve+experiment_tracking）
①67 py / 10,232 LOC / 36 mids / 蓝图仅 4——**蓝图覆盖薄**（4/67）。②域外 import 组=5。③判据：模型训练/服务层，有消费。④**保留**；蓝图薄=对齐债，登记 P11。

### 2.6 D_AI_AUTONOMY（ai_layer+autonomy_core+red_blue_validator）
①153 py / 29,741 LOC / 23 mids（23 锚辖 153 文件=中粒度锚城，同簇4形态，非非法重复）。②域外 import 组=5。③判据：自治/红蓝验证线。④**保留**。

### 2.7 D_FACTOR（factor）
①87 py / 18,253 LOC / 41 mids / 18 蓝图。②域外 import 组=8+factor 计划任务在册。③判据：生产因子引擎（c4 策略资产消费方见 W5-1 簇3）。④**保留**。

### 2.8 D_SIGNAL（signal_ashare+signal_fundamental+signal_quality+cross_asset）
①209 py / 52,691 LOC / 137 mids（唯一 id 密度最高=锚粒度细）。②域外 import 组=6。③判据：信号族四包各管一类标的（裁定#204 域名史），跨域不同对象不并。④**保留**；蓝图 4/209 薄，登记 P11。

### 2.9 D_RISK_COMPLIANCE（risk+compliance）
①108 py / 31,362 LOC / 60 mids / 63 蓝图。②域外 import 组=5。③判据：风控/合规两域各自对象。④**保留**。

### 2.10 D_PORTFOLIO（pf_alloc+pf_core+position+regime）
①147 py / 49,650 LOC / 82 mids / 38 蓝图。②域外 import 组=10（高扇入）。③判据：组合/持仓/regime 现役。④**保留**。备注：`pf_alloc` 与 `portfolio_alloc` 蓝图目录并存（docs/03_modules 双目录），登记 P11 查目录收敛。

### 2.11 D_TRADING_CORE（trading+plan_engine+sell_decision+strategy_factory+strategy_pipeline）
①190 py / 53,204 LOC / 95 mids / 43 蓝图。②域外 import 组=13（最高）+trading 计划任务。③判据：交易核心。**W5-0 遗留线索复核**：`shared/contracts` vs `trading/trading_contracts` 契约双真源嫌疑——实测**已收敛**（顶层同名仅 `__init__.py`；trading_contracts 3 文件显式 `from zephyr.shared.contracts.*` 委托导入=声明式单真源形态，A 级）。④**保留**。

### 2.12 D_EXECUTION_SIM（ex_core+ex_sor+execution_simulation+simulation+digital_twin）
①131 py / 37,925 LOC / 58 mids。②域外 import 组=7。③判据：执行/仿真族，ex_core 与 simulation 对象不同不并。④**保留**。

### 2.13 D_BACKTEST（backtest）
①55 py / 19,298 LOC / 13 mids。②域外 import 组=5。③判据：回测域（O-2 已清零消费死件 decisiongraph_adapter；c4 资产库另见簇3）。④**保留**。

### 2.14 D_ORCH_RUNTIME（orchestrator+runtime）
①75 py / 13,149 LOC / 9 mids（9 锚辖 75 文件=粗粒度锚城，同簇4形态）。②域外 import 组=3+runtime 任务。③判据：编排/运行时（AutoRuntime Core 入口 `-m zephyr.trading` 属 D_TRADING_CORE 域，两域分工清晰）。④**保留**。

### 2.15 D_GOV_CORE（governance+gov_audit+gov_code_quality）
①439 py / 96,842 LOC / 77 mids——18 域中文件数第一。②域外 import 组=11+域外文件 9+governance 任务。③判据：治理核心（DatabaseService/capability_lookup/decisiongraph_schema 等宪法 §7 系统聚集地）。④**保留**。

### 2.16 D_GOV_RULES（gov_rule+gov_drift+gov_enforcement）
①286 py / 88,028 LOC / 41 mids。②域外 import 组=8+gov_enforcement 任务（GitCommitGateway 门禁引擎）。③判据：规则/漂移/执法三路现役。④**保留**。

### 2.17 D_INFRA_SEC（infrastructure+infra_ops+infra_runtime+security+clone_guard）
①555 py / 103,218 LOC / 115 mids——体量第一；config/ 册 34 件中 28 件锚 D_INFRA_RUNTIME（资源配置簇已由 W5-1/O-1 处置：capacity_params 退役、resource_optimization=活真源）。②域外 import 组=14（最高扇入）+3 计划任务。③判据：基础设施骨干。④**保留**。备注：config/ 另有 25 件无 [DOMAIN] 锚（anchor 债，登记 P11）。

### 2.18 D_FRONT_REPORT（frontend+reporting+research）
①96 py / 31,403 LOC / 51 mids / 38 蓝图。②域外 import 组=5。③判据：前端（8890 一体化已上线=master_directive S6）+报表+研究。④**保留**。

## 3. 跨域横切发现

1. **跨组同名文件 96 件**（探针 `_cross_group_same_names`）：top=__main__.py×4 组、cli.py×3、config.py×3、models.py×3、engine.py×3、circuit_breaker.py×3——逐对核验为跨域不同对象（入口/配置/模型同名惯例）→ 按铁律**不并**；同名漂移属命名惯例债，不立项。
2. **data_governance 撞名双包**（§2.3）：零消费 lineage/masking 包 vs 26 消费 provider 包——退役候选+撞名危害一并处置（P11）。
3. **蓝图覆盖薄域**：D_ML（4/67）、D_SIGNAL（4/209）——锚/蓝图对齐债，P11 批量补。
4. **config 无锚 25 件**（audit_key_eras/crypto_top50_usdt/intel_sources 等）——[DOMAIN] 锚补标债，P11。
5. **W5-0 契约双真源线索=已收敛**（§2.11，A 级实测）——线索销案。

## 4. 待执行项清单（P11 消化循环入口，本册零执行）

| # | 事项 | 证据 | 建议动作 | 门位 |
|---|------|------|---------|------|
| P11-1 | D_DATA_GOV 31 件+15 测试件退役评估（data_governance lineage 群+data_security masking 群） | A 级零消费（本册 §2.3） | 复核动态入口后 salvage+删除（比照 O-2 流程） | Max 自裁（#371） |
| P11-2 | data_governance 撞名消歧（若 P11-1 退役则自动销案；否则改名） | 同上 | 随 P11-1 | 同上 |
| P11-3 | D_ML/D_SIGNAL 蓝图薄覆盖对齐批 | A 级计数 | blueprint 补齐或锚收敛 | Max 自裁 |
| P11-4 | config/ 25 件无 [DOMAIN] 锚补标 | A 级计数 | 批量补锚（比照裁定#335 流程） | Max 自裁 |
| P11-5 | pf_alloc vs portfolio_alloc 双蓝图目录收敛查 | B 级（目录并存观察） | 查重后并目录 | Max 自裁 |

## 5. 回执（六要素）

1. **18 域三档结论**：保留 17 / 退役候选 1（D_DATA_GOV，A 级零消费）/ 合并候选 0；跨域横切 5 条（其中 W5-0 契约双真源线索实测已收敛销案）。
2. **证据等级**：盘点计数/消费图/计划任务对账=A 级（探针机读）；退役"无动态入口"判定=B 级（同 W5-1 簇3 口径警示）；P11-5=B 级。
3. **未完成+原因**：a) 18 域为聚合划分（56 顶包→18 组），未做包内逐模块级深挖——粒度对齐 W5-1 四簇的簇级口径，模块级深挖留给退役/合并执行批；b) D_DATA_GOV 动态入口复核未做（清单册零执行纪律）。
4. **红线遵守**：只读挖矿零合并零删除零执行；写入面=本文件+creation_token 1 条+探针/JSON 在 `.runtime/tmp/`（不入库）。
5. **防误杀**：探针只读（rglob+read_text+计数），无任何写路径调用；计划任务对账只读 dump。
6. **查询复用**：复用 W5-1 计划任务 dump 与 W5-0 十类台账基线计数（域包数按当日实测重跑，未转抄）。
