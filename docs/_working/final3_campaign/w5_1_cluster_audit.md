---
ttl: task_bound
completes_when: W5-3 退役审计与 Owner 批阅消费本件后归档（最迟 2026-10-19）
title: W5-1 四簇内收审计（W5-0 df51a27a5f 移交）
owner_session: st-final3-20260919
date: 2026-09-19
---

# W5-1 四簇内收审计 — final3_campaign

> session=st-final3-20260919 | 判据铁律：同真源可派生→必并｜零触发零消费→退役｜同域重复簇→收敛唯一｜跨域不同对象→不并。
> 本件为只读审计，**零合并/零删除执行**。证据等级：A=本会话机读/活库直查实测；B=推断（声明性证据或松口径）。

## 簇1 resource_optimization vs capacity_params 两本资源参数册（Owner 点名合并评估候选）

### 现状
| | `config/resource_optimization.yaml` | `config/capacity_params.yaml` |
|---|---|---|
| 定位 | 资源优化引擎运行时配置（压力阈值/迟滞/降级/自愈） | 容量参数统一册（设计容量/硬件画像/worker/分片/SLO） |
| 体量 | 90 行 / 10 个顶层段 | 163 行 / 14 个顶层段 |
| 锚 | `module_id: MOD-INF-002`（头部另注明 SSoT=mod_inf_032 blueprint §18） | `module_id: MOD-INF-002` |
| 现役消费方 | **多活（A级实测）**：`src/zephyr/trading/resource_optimization.py`（引擎直接加载本 yaml）、`src/zephyr/shared/infra/process_incubator.py`（读 pressure_thresholds）、`src/zephyr/infrastructure/system_telemetry/alerts/ops_alert_feed.py`（读 ops_alerting.project_rss_alert_gb 作兜底线）、`global_state_aggregator.py`、`trading/health_monitor.py` | **零运行时消费**：全仓 grep 仅 `src/zephyr/infrastructure/config_validator.py:78` 结构性必填键检查、`generate_battle_map_diagram.py:1734` 展示性读 design_capacity、registry catalog 提及 2 处；其独有键（max_script_workers/shard_count/global_max_concurrent/lsg_concurrent_max 等）代码零命中 |
| 头部声明 | 热加载 ≤5s | "代码启动时从此文件加载"——**未找到任何加载器（死文字）** |

### 逐字段重叠比对
- **重叠段=资源压力阈值**：capacity_params `thresholds`（memory_warn 70 / crit 85；cpu_warn 75 / crit 90） vs resource_optimization `pressure_thresholds`（memory 70 / 80 / 90；cpu 75 / 85 / 95）。
- **同名概念数值冲突**：memory critical 85% vs 80%；cpu critical 90% vs 85%。后者对齐 AutoRuntime Core 蓝图 §3.3 四级降级链且有消费方=活真源；前者无消费方=死副本。
- **非重叠段互不覆盖**：容量册的 design_capacity/hardware_profile/sharding/budget/lsg/fle/mcp/timeouts/cache/observability vs 引擎册的 hysteresis/monitor/process_pool/circuit_breaker/self_healing/audit/eventbus/history/ops_alerting。
- **既有裁定边界**：resource_optimization.yaml 头部明文"压力口径五套不收编，统一口径=v2 挂起议题"（真源 v1 方案 §2.1 关键裁定-③）——阈值收编必须走 v2 裁定，本审计不越权单判。

### 判据应用
- 同真源可派生→必并：**不成立**（两册内容互不可派生）。
- 同域重复簇→收敛唯一：**阈值段成立**，收敛方向=resource_optimization.yaml（唯一有消费方+裁定真源）。
- 零触发零消费→退役：**capacity_params 主体成立**（独有键零代码命中+无加载器，仅结构性校验引用）。

### 三档结论
- **合并候选（部分）**：capacity_params.thresholds 段收敛至 resource_optimization.yaml（或改写为指向真源的指针注记）。
- **退役候选**：capacity_params.yaml 主体。联动点备料 4 处：config_validator.py:78 必填键表、generate_battle_map_diagram.py 展示读键、capability_canonical_file_registry 与 module_translation_registry 的提及行。
- **Owner 门位**：阈值收敛与"五套压力口径"v2 挂起议题绑定（裁定-③边界）；config 净删须 Owner 圈阅。本审计只备料。

## 簇2 decisiongraph 退役跟踪（季度退役审计观察名单项）

### 现状
- PG `decision_*` 四表全部非空（活库只读直查，A级）：decision_nodes=213 / decision_edges=211 / decision_layers=1763 / decision_tracks=5。
- 全景产物在盘且新鲜：`docs/02_enterprise_architecture/06_decision_architecture/` 22+ 文件于 2026-09-19 23:29（本审计约 2 小时前）刚由生成器重建；派生文档已整体移出 git 跟踪（`.gitignore:557-560`，commit 326952a276）——**decision_index.md 在 git ls-files 缺席=移出跟踪，不是死亡**。
- 生成器链全在且 production：`generate_decision_diagram.py`（全景）、`generate_decision_graph.py`（YAML→DB schema 同步）、`apply_decisiongraph.py`（nodes/edges 写入）、`extract_decisiongraph.py`，各有配套测试。

### 现役消费方（"零触发零消费"判据逐项核对）
1. **commit 门禁** `src/zephyr/gov_enforcement/commit_gates/panorama_alignment_gate.py`：三图（depgraph/dataflow/decision）内部不一致阻断 commit（ARCH-056），触发路径含 decisiongraph_schema.py / apply_decisiongraph.py——门禁级硬依赖。
2. `scripts/governance/align_battle_map.py`：battle_map 锚 target 合法值域校验读取 decisiongraph（`_valid_ids_decisiongraph`）。
3. `scripts/governance/sync_panorama_module.py` 单向派生（alignment_checklist §3 权威行：派生失败→阻断）。
4. YAML 真源 `architecture_model/domain/decision_graph_model.yaml` 在盘，规则 `trae_061_decisiongraph_access_protocol.yaml` 现行。
- **唯一零消费点**：`src/zephyr/backtest/io/decisiongraph_adapter.py`——头部声明消费方"回测管线（vectorized_engine / event_driven_engine 完成后调用）"，实测全仓零 import（仅自身测试引用）= 声明消费方未接线（B级）。

### 三档结论
- **保留理由（主体）**：零触发零消费判据不成立（门禁+对齐+派生三路现役消费）。建议将 decisiongraph 主体**移出退役观察名单**，定性"现役"。
- **退役候选（单件）**：decisiongraph_adapter.py（B级证据；手工入口不能完全排除，W5-3 复核运行痕迹后定）。
- **漂移线索**：panorama_alignment_gate.py:75 触发清单引用不存在的 `catalogs/decision_layers_registry.yaml`（全仓唯一引用点；邻位 decision_algo_registry.yaml 为决策算法登记表，非同一对象）——文档改漏项。
- **Owner 门位**：adapter 退役执行。

## 簇3 scripts 动词簇（validate×110 / check×94 / c4×88 + fix_n）

### 现状（本会话机扫，A级）
| 簇 | 总数 | _archive | 活跃 | 松口径零引用 |
|---|---|---|---|---|
| validate_* | 110 | 8 | 102 | 0 |
| check_* | 94 | 6 | 88 | 0 |
| c4_* | 88 | 0 | 88 | 0 |
| fix_n* | 8（W5-0 盘点日为 ×7） | 2 | 6 | 0 |

抽样=字母序前5+mtime 最新5（fix_n 全查），共 38 件；逐件全仓 git grep 引用计数 + script-manifest + 43 个 Zephyr 计划任务动作对账（dump 在 `.runtime/tmp/w5_1_tasks_dump.txt`）。

### 三问停止判据逐簇
- **validate×110**：抽样 10 件验证对象/口径互不相同——规则完整性（validate_rules_integrity，production，43 个引用文件）、交叉引用（validate_cross_references，门禁册引用）、策略生产全景（validate_strategy_production_map，in_process 门禁册成员）、intel 注册表（validate_intel_registry，被 intel_harvester 消费）等；抽样中 6 件为 _archive 残留（字母序偏差，全簇实为 8/110）。→ 验证口径变=拆；**跨域不同对象，不并**。
- **check×94**：抽样 10 件=目录契约（check_directory_contract，gate_registry.yaml:242 门禁入口+trae_047/070 规则引用）、保护路径（check_protected_paths，in_process 门禁册真源复用 import）、ssot gate（run_gate_chain 编排）、ACL 边界等。→ **跨域不同对象，不并**。
- **c4×88**：全部活跃，回测机翻策略资产库（`translated/c4_<hash>_<策略>.py` 一策略一文件：alpha022 / pairs_zscore / rsrs_60m / cgo_factor…），由 `tests/backtest/test_c4_pit_universal_gate.py` 通用 PIT 门禁+capability_canonical_file_registry 等登记体系消费。→ 只是标的/参数变=不拆；**策略资产 legitimately 多件，非冗余簇**。
- **fix_n×8**：一次性嫌疑**部分成立**——活跃 6 件（d7_code）头部消费方均为 OPS 工单（如 fix_n06_scope CONSUMERS=OPS-2026062106，STABILITY=volatile）；与 _archive 两件同名件（fix_n06/fix_n12）实测为改名后继关系（INVARIANTS/锚不同），非同内容重复。

### 零消费嫌疑清单
- 严格口径（全仓 grep 调用点=0 且无计划任务/manifest 引用）：抽样 38 件 **0 件命中**（全部在 manifest 在册）。
- 松口径（排除 _archive 与 script-manifest 后计引用文件数）：四簇 284 个活跃件全部 ≥1 个引用文件，**零消费嫌疑清单=空**。
- 口径警示（B级）：scripts 为手工触发入口惯例，grep 零≠未用；松口径将 docs/登记册提及计入引用。真"未用"需运行遥测佐证。

### 三档结论
- **保留理由**：top3 动词簇均为跨域不同对象/不同验证口径，合并制造聚合怪物，违反三问判据。
- **归档候选（非删除）**：fix_n 活跃 6 件一次性工单脚本，工单闭环核验后→W5-3 归档批素材。
- Owner 门位：本簇无（零净删）。

## 簇4 module_id 共享城（MOD-FEEDBACK_LOOP×287 / MOD-GATE_ENGINE×202 / MOD-INF-016×195）

### 判定：合法的"锚注模板复用"（多文件作为同一模块的成员文件共享章节锚），非重复模块定义

### 证据（MOD-INF-016 实测抽样 + 双城旁证）
1. **唯一规范蓝图存在**：`docs/03_modules/_cross_layer/shared_core/blueprint.md` frontmatter `module_id: MOD-INF-016`，范围=src/zephyr/shared/**（实测 280 py）+ core 并入（a5c1a81787）+ F20/F21——与锚载体分布（shared/utils×12、io×10、contracts×10、lifecycle×9、trading_contracts×7×2…）完全吻合，195 件全落在声明范围内。
2. **载体文件每件仅 1 条头部锚注行且为注释非定义**：实测 `en_process_lifecycle_gateway.py:15` `# [A_module] module_id=MOD-INF-016 | layer=module | …`——成员文件的归属自述，不重复声明模块。
3. **跨模块重叠走声明式委托**：gate_engine/blueprint.md circuit_breaker "基类 SSoT=MOD-INF-016 + §0.4 声明委托 + §10.5 登记重叠"；process_incubator blueprint `parent_module: MOD-INF-016`（子模块声明）。
4. **双城旁证**：MOD-FEEDBACK_LOOP×287 全部落 src/zephyr/feedback_loop/**（diagnosers×36/verifiers×24/collectors×21/evolution×20/forensic×19…）；MOD-GATE_ENGINE×202=commit_gates×113+feedback_loop/gates×49+rule_enforcement×24…（跨目录但同属门禁引擎对象）。
5. **W5-0"5 个文件 ≥2 锚"异常复核=正则误报**：capability_lookup.py 真锚仅 1 条（MOD-INF-037，其余 5 处为 docstring/regex 字符串）、api_server.py 真锚 1 条（MOD-L08-001）；blueprint_amodule_*_gate 高计数是门禁自检代码内的样例串。

### 三档结论
- **保留理由**：共享城=蓝图粗粒度锚机制的合法产物，零非法重复定义。
- **改进线索（仅登记）**：粗粒度锚（195-287 文件挂一 id）弱化模块定位力；若拆子 id（如 shared/io、shared/contracts 独立）→Owner 架构裁定+depgraph 重建，W5-3+ 议题。
- Owner 门位：无强制项（O-4 备选参考）。

## Owner 门位清单（本审计只备料，零执行）
| # | 事项 | 簇 | 备料 |
|---|---|---|---|
| O-1 | capacity_params.yaml 净删/归档 + thresholds 收敛唯一（与"五套压力口径"v2 挂起裁定-③绑定） | 1 | 零消费证据+联动点 4 处清单（§簇1） |
| O-2 | decisiongraph_adapter.py 退役 | 2 | B级零消费证据（声明消费方零 import） |
| O-3 | fix_n 活跃 6 件归档批（工单闭环核验后） | 3 | 工单消费方+后继关系实测（§簇3） |
| O-4 | （备选）MOD-INF-016 粗粒度锚拆分裁定 | 4 | 载体分布图谱（§簇4） |
| — | decisiongraph 主体建议移出退役观察名单 | 2 | 四表行数+三路消费方实测（无需圈阅，备案） |

## 回执（六要素）
1. **四簇三档结论**：簇1=合并候选（阈值段收敛 resource_optimization）+退役候选（capacity_params 主体，O-1 备料）；簇2=保留（建议移出退役观察名单；adapter 单件=退役候选 O-2）；簇3=保留（零消费嫌疑清单=空；fix_n×6=归档候选 O-3）；簇4=保留（合法锚注复用）。
2. **证据等级**：簇1 消费方/簇2 表行数与 mtime/簇4 抽样=A 级机读活库实测；簇3 计数=A 级、零消费判定=B 级（手工入口惯例+松口径含 docs 提及）；簇2 adapter 零消费=B 级。
3. **未完成+原因**：a) 手工触发脚本"确未用"无运行遥测不可机械证明→fix_n 归档留给 W5-3 复核运行痕迹；b) capacity_params 阈值收敛受裁定-③"v2 挂起"边界约束，不越权单判；c) decision_layers_registry.yaml 幽灵路径的成因（改名或删残）未溯源，仅列漂移线索。
4. **红线遵守**：只读审计零合并零删除；写入面=本文件+creation_token 登记一条+.runtime/tmp 探针（不入库）；禁碰清单零触碰；写前 reaper 存活已确认。
5. **防误杀**：探针与中间产物在 `.runtime/tmp/`（24h TTL）：w5_1_decision_db_probe.py、w5_1_scripts_probe.py、w5_1_scripts_full.py、w5_1_dump_tasks.ps1、w5_1_tasks_dump.txt、w5_1_scripts_probe.json、w5_1_scripts_full.json。
6. **查询复用**：W5-0 基线（df51a27a5f）计数未复核对表，仅对本审计四簇增量实测；簇3 的 fix_n 计数 8 与 W5-0 的 7 差异系"fix_n*"前缀口径（含 fix_naming_manual）。
