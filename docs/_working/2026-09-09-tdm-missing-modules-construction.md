---
ttl: task_bound
---

# TDM 缺失模块全面施工总纲（2026-09-09 夜班 23:00 开工临时文档）

> **目的**：Owner 裁定 2026-09-09 23:00 起全面施工交易决策地图全部缺失模块。本文档是施工总清单+前置准备+SOP 速查的唯一工作底稿。
> **依据**：2026-09-09 全项目交易业务挂载核对（TDM 后端负责人会话 st-tdmbe-20260909 产出）+ `config/trading_decision_map.yaml` 当前 129 节点。
> **用法**：每完成一项在表内打勾并记 commit hash；全部完成或 Owner 叫停后本文档归档（ttl: task_bound）。
> **铁律预告**：清单里标"反查先行"的条目，动手前 MUST 跑创建前搜索——命中既有实现就降级为回填，**禁止把 A 类误当 C 类重建**（CLONE-GUARD L1 硬阻断无逃生）。

## 〇、分类总览（数字=节点数，含子节点）

| 类 | 语义 | 量级 | 今晚动作 |
|---|---|---|---|
| A | 代码已存在，回填 module_ref/module_id 即完成 | ~41（已回填 14 待提交） | 不施工，批量回填 |
| B | 实现部分存在，需核实成熟度/整合接线 | ~10 | 小规模施工 |
| C | 反查落空的真缺失，从零建 | ~12 | **今晚主战场** |
| D | 已裁定不建/不挂（防过度施工） | ~14 簇 | 不动 |

## 一、开工前置准备（P0 检查单，逐项打勾）

- [x] **环境对齐**：`$env:PATH` 前插 Python 3.12（Git Bash: `export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:$PATH"`），`python --version`=3.12.x；`python scripts/lock_files.py cleanup`；reaper 状态新鲜
- [x] **必读清单（六件，2026-09-09 SOP 扫描后定稿）**：①AGENTS.md RULE 区 ②`docs/_working/2026-09-09-node-backtest-governance.md` §七裁定+两条铁律 ③`sop/construction_workflow_sop.md` 15 步（主流程真源） ④`sop/trading_decision_map_layering_sop.md`（涉地图结构/血肉改动的四道前置检查闸） ⑤`sop/alignment_checklist.md`（七图+注册表对齐判据真源；新建注册表必挂轴 D38 铁律在此） ⑥`docs/_working/2026-09-09-tdm-night-greatwall-directive.md`（夜班执行指令：模型分工/微循环/双审协议/红蓝对抗/晨审交接）
- [x] **写码前四道闸**（每模块开工前逐个过）：①能力反查 `rule_discovery.discover_applicable_rules(operation='file_write')`（MCP）或 `CapabilityLookup().find(<关键词>)`；②clone_guard 查重 `check_before_write`；③Step 1.5 创建前三重搜索（Grep src/+scripts/+tests/ + 注册表）；④depgraph 设计态登记 `apply_depgraph.py --add-design-node <path> <BLUEPRINT_ID> <DOMAIN_ID> planned`（**写第一行业务代码前**，禁先施工后补登记）
- [x] **新建文件合规**：CREATE-GUARD creation_token 登记（本登记表 `capability_canonical_file_registry.yaml` 全局 `creation_tokens:` 段，四件套 file/token/created_by/capability，**禁 EOF 盲插错段**）；文件头 15 字段（trae_047）；目录归属（放进 62 个既有域包对应子目录，禁 governance/ 根平铺）；容量红线（目录 >150 必拆）；trae_070 放置 5 铁律（任务文档→docs/_working、运行时脚本→.runtime/tmp）
- [x] **提交纪律**：走网关 `python scripts/git_commit.py --session <各会话sid> --files "<逐一列出>" --message-file <msg文件> --allow-overlap`；改完 30 分钟内提交；禁裸 commit/禁 --no-verify。**今晚已知**：共享暂存区有 sess-26548 + worker-69d94 两活会话的 7 件在途 WIP（框架编排器特性），gate 会扫到它们的违规硬阻断——按 66 号备忘排队等窗口，**禁碰禁清别人 staged 文件**（判读器已定性 active_wip）
- [x] **地图改动配套**（凡动 config/trading_decision_map.yaml 或 decision_map.py）：validate error=0 + `tests/trading/test_decision_map.py`+`test_decision_map_adversarial.py` 双绿 + `align_all.py` exit 0 + 节点 module_ref 回填与代码**同 commit**（跨 commit 原子性）

## 二、施工 SOP 15 步速查（真源=construction_workflow_sop.md v1.5.5，此处只编排不重复）

| 步 | 动作 | 关键命令/判据 |
|---|---|---|
| 0 | 冷启动 | 环境对齐+守护进程+必读加载 |
| 1 | 文档审查 | AI_review 12 节，结论对话内给，禁建报告文件 |
| 1.5 | 创建前搜索 | 三重反查；覆盖率四档决策；**[REUSE-DECISION] 留痕** |
| 1.8 | 架构评审门控 | 新增模块/改接口才触发；纯内容修改豁免 |
| 2 | depgraph 设计态 | `apply_depgraph.py --add-design-node`（先于写码） |
| 3 | 七图对齐 | `sync_panorama_module.py --all` + `align_all.py` exit 0 |
| 3.5 | 后端盘点（涉前端才触发） | 三查+前端一查+三分支决策 |
| 4 | 施工编码 | 蓝图（新建模块）→scaffold→15 字段头→事件驱动启动→禁循环内 git subprocess |
| 5 | 单元测试+循环验收 | pytest 连续 2 轮 0 错误才算 COMPLETED |
| 6 | 长清单审查 | 附录 A 14 节；先改动分类（A-E）再逐节；遗留项登记 tracker |
| 7 | 更新施工文档 | 备忘 frontmatter 升版+设施盘点+00_index 同步+跨蓝图消费方 |
| 8 | 全景图状态流转 | worktree 会话只登记不流转；主工作区 `--transition-design-maturity <ID> production` |
| 9 | 文件完整性 | git status 无回退/无丢失+staged 清单核对 |
| 10 | 网关提交 | git_commit.py（禁裸 commit）；stash>40 阻断 |
| 11-12 | 清理+合并 | 只清自己会话临时文件；worktree merge 后暂不清理逃生通道 |

**已施工设施盘点基线**（Step 7 用）：地图真源 129 节点/180 边（TDM-E-L0 节点组 7c44295fcf 已入库）；门禁 R1-R37 全生效（R37=大白话算法说明必填）；登记表 DAL-*/五类方法学/param_origin 三档已建。

### 二.1 配套 SOP 使用边界（2026-09-09 对 sop/ 目录全量扫描裁定）

| 类 | SOP | 用在今晚哪里 |
|---|---|---|
| **必读** | construction_workflow_sop.md | 主流程 15 步（§二速查表的真源） |
| **必读** | alignment_checklist.md | 每波次收尾 align_all 的判据来源；新建注册表/图必须挂轴（D38）；R21 欠账清偿的规则依据 |
| **必读** | trading_decision_map_layering_sop.md | C 类新建节点=Blood 填充/结构调整，动地图前过四道前置检查（已有资产盘点/四路调研/上层完整性/枝干分级） |
| **必读** | merge_conflict_resolution_sop.md | 暂存区排队撞冲突时：三分法（叠加型合并/迭代型取新/互斥型升级 Owner）+7 步流程，禁盲选边 |
| **必读** | 夜班指令文档（姊妹篇） | 执行序/双审循环/红蓝对抗/晨审交接的操作真源 |
| 按需 | worktree_cleanup_sop.md | 仅当改走 session_worktree 路径时 |
| 按需 | document_review_and_optimization_sop.md | 写新模块 blueprint 时的文档质量关 |
| 按需 | 2026-08-22-emergency-runbook.md | 夜间事故应急（数据/服务类） |
| **不用** | frontend_component_split_sop.md | 今晚零前端施工（抽屉占位归前端会话） |
| **不用** | industry_chain_data_audit_sop.md | 异域（产业链图谱），无关 |
| **不用** | audit_prompts_20_ai.md | 审计专用提示词集，非施工 SOP |

## 三、C 类主战场：真缺失从零建（今晚核心，12 项）

> **每项开工第一动作=Step 1.5 三重反查**，命中既有实现→降级 B 类回填并在表内改标。拟建路径是默认方案，反查后可调整，但**必须落在这 62 个既有域包内**，禁新建顶层包。

| # | 节点 | 拟建模块（默认路径） | 域 | 大白话要求 | 反查关键词 | 优先波次 |
|---|---|---|---|---|---|---|
| C1 | TDM-L1-S5 日级市场条件传感器（11 信号聚合器） | src/zephyr/signal_ashare/daily_condition_sensor.py | D_ASHARE_SIGNAL | A组8信号+B组3信号聚合→5 档水温读数；月/周层封顶约束+三层对齐加成（D20 定稿） | daily_condition/水温/日级 | ✅已提交 065a2615（MOD-SIG-135，24 测试绿；迁 core/ 子目录避容量上限） |
| C2 | TDM-L1-S1 大盘指数传感器聚合 | src/zephyr/regime/features/index_sensor.py | D_REGIME | 均线排列+位置打分（-2~+2）；攻防板块特征入层（D109：券商/银行 5 日超额） | index_sensor/指数趋势 | ✅已提交 5c5b99f2（MOD-REGIME-016，14 测试绿） |
| C3 | TDM-L2-05-2 信号响应三件套 | ~~water_temp_response.py~~ **改判：降 B→命中 sector_gate.py** | D_ASHARE_SIGNAL | 水温档→响应动作三件套（加减档/对冲/观望清单） | water_temp/响应 | ✅波次0 命中：water_temp_response() 返回 signal_weight/gate_thresholds/rrg_filter 三件套，精确覆盖，module_ref 已正确 |
| C4 | TDM-L2-06-1 三级放行门槛 | ~~three_level_gate.py~~ **改判：降 B→命中 sector_gate.py** | D_ASHARE_SIGNAL | 板块→个股传导的三级放行判定（门槛不过不往下传） | sector_gate/放行 | ✅波次0 命中：admission_gate() 三级放行（CORE_HOT/SECONDARY/WILDCARD/BLOCKED）精确覆盖，module_ref 已正确 |
| C5 | TDM-L2-06-3 强度加权传导 | src/zephyr/signal_ashare/sector_conduction.py | D_ASHARE_SIGNAL | 板块强度加权传导到个股池（含 L2-10 同源补涨比价输入） | conduction/传导 | ✅已提交 065a2615（MOD-SIG-136，15 测试绿；迁 core/） |
| C6 | TDM-L2-03-1 扩散指标进度追踪 | adjustment_cycle_tracker.py 扩展（先反查） | D_ASHARE_SIGNAL | 调整周期扩散指标进度（40/60/80% 阈值） | diffusion/扩散 | ✅已提交 065a2615（tracker 扩展，12 测试绿） |
| C7 | TDM-L3-04 负面否决器 | src/zephyr/signal_fundamental/negative_veto.py | D_FUNDAMENTAL_SIGNAL | ST/退市/立案/减持/解禁/黑名单一票否决（已挂 STR-MULTIFACTOR-034~041 六条规则） | veto/否决/黑名单 | ✅已提交 48c913a8（MOD-SIG-137，18 测试绿；VetoVerdict 改名 NegativeVetoVerdict 避撞名） |
| C8 | TDM-P1-03 买入逻辑存活判定 | src/zephyr/plan_engine/thesis_survival.py（或扩展 plan_deviation_monitor） | D_PLAN | 买入理由还成立吗（题材退坡/逻辑证伪→触发 X 流信号） | thesis/survival/存活 | ✅已提交 994e96f9+ae9ccb83（MOD-PLAN-024，23 测试绿） |
| C9 | TDM-P3-01 加仓资格门 | src/zephyr/position/core/pyramiding_rules.py | D_POSITION | 加仓资格判定（浮盈保护/环境允许/计划内加仓点） | pyramiding/加仓资格 | ✅已提交 4105b58e（MOD-POS-027，CORE 标记；28 测试绿；CircuitLevel 复用白名单枚举） |
| C10 | TDM-P3-02 金字塔加仓规则 | 同上文件（与 C9 同模块两函数，节点分开） | D_POSITION | 金字塔递减加仓（1/2/4 档逐级减半，总加仓≤首仓） | pyramiding | ✅已提交 4105b58e（与 C9 同模块） |
| C11 | TDM-X-R1-03 护盘资产定向加仓白名单 | src/zephyr/position/core/defensive_asset_whitelist.py | D_POSITION | 熔断期允许定向加仓的护盘资产白名单（动作方向=买入，验证时单独核对） | whitelist/护盘 | ✅已提交 bc4c0770（MOD-POS-026，CORE 标记；D114 休眠铁律默认关） |
| C12 | TDM-X-S2-03 执行时段路由 | ~~核对 execution_scheduler.py~~ **核对结论：不覆盖，维持 C** → src/zephyr/ex_sor/core/sell_session_router.py | D_EX_SOR | 卖出单时段路由（开盘竞价/盘中/尾盘竞价/急单走市价） | execution_scheduler/时段 | ✅已提交 a9be7524（MOD-XS-016；50 测试绿；route_sell 拆 6 处理器） |
| C13 | TDM-E-L0-04 明日情绪盘中滚动预测（G1 增长批1 新增） | src/zephyr/plan_engine/intraday_tomorrow_forecast.py | D_PLAN | 盘中 10:00/11:00/13:30/14:30 四时点滚动合成 8 态先验+相似日 KNN+水温读数→明日情绪概率，悲观降档预警喂 L0-02（三零件全在，缺组合器；Brier 校准降权） | forecast/滚动/明日情绪 | ⏸挂起移交晨审（G1 节点已落图 c8f678d8 红节点；模块待下批） |

**波次0 定界结论（2026-09-10 夜班三重反查实跑）**：C3/C4 命中既有实现降级（sector_gate.py 两函数精确覆盖）；C12 核对 execution_scheduler.py=参与率切片调度≠时段通道路由，维持 C；C1 核对 market_state_sensor.py=9 网格 trend×vol≠11 信号→S0-S4 五档水温（D20），维持 C；C2 核对 index_regime_panel.py=HMM 概率面板≠均线排列+位置打分 -2~+2，维持 C；C5 核对 sector_attribute_rules.py=攻防属性标注≠强度传导系数，维持 C；C7 核对 risk_veto_engine(MOD-RK-24)=订单级风险否决、strategy_cross_vote_funnel=市场状态否决、均≠负面清单一票否决，维持 C；C8 核对 plan_deviation_monitor=收益偏差 z 监控≠买入理由存活三态，维持 C；C9/C10/C11 无 capability 无文件，维持 C。**C 类最终边界：C1/C2/C5/C6/C7/C8/C9/C10/C11/C12 十项真新建 + C6 为 tracker 扩展式。**

**C 类验收统一口径**：模块落码（15 字段头）+ `tests/<域>/test_<模块名>.py` 循环验收 2 轮 0 错误 + depgraph 设计态登记 + 节点 module_ref/module_id 同 commit 回填 + validate/双测试/align_all 三关。

## 四、B 类：部分实现待核实/整合（10 项，施工量小）

| # | 节点 | 已有线索 | 动作 |
|---|---|---|---|
| B1 | TDM-L1-S4 波动率传感器 | regime/features/synthetic_vix.py 存在但节点写"VIX 缺口用 ATR"（**矛盾①**） | 核实 synthetic_vix 成熟度：可用→回填+改节点注释；不可用→ATR 通道落码 |
| B2 | TDM-L2-04-1 轮动五分类 | sector_rotation_state.py | 核对五分类口径与节点定义一致→回填 |
| B3 | TDM-L3-03-1/2 双池评分 | fine_scoring_engine + quant_short_term_strength_engine + short_term_stock_selector | 三者关系厘清（谁是主评分器）→整合回填 |
| B4 | TDM-L3-05 顺位排序 | selection_confidence + stock_signal_strength | 排序键口径核对→回填 |
| B5 | TDM-L3-09 股票池分层维护 | 反查 pool/tier/分层（universe 管理可能已覆盖） | 反查命中→回填；落空→升 C |
| B6 | TDM-L2-01-5 市场级调节注入 | 可能内嵌 sector_ranking_engine | 反查后定 |
| B7 | TDM-L1-AGG overlay 补充 | overlay_signals_builder + market_forecast_fusion | 回填（detector 为主锚，两文件入 note） |
| B8 | TDM-L3-07-1 打板选股链 | limit_up_classifier(ml_train) + 打板 STR 链已有 | 推理件回填 |
| B9 | TDM-P2-01/P2-03 做T资格与闭环 | t1_sellable+t0_point_analyzer+day_trade_pnl_estimator+t0_trading_pipeline | 回填（batch3 范畴，若有缺口就地补） |
| B10 | 3 处 R21 交叉锚欠账 | t1_sellable/drawdown_state_machine/drawdown_liquidation_guard 无 MOD-ID | depgraph 注册后回填 module_id（`apply_depgraph.py` 或 generate 刷新缓存） |

## 五、A 类：纯回填（不施工，41 项=已完 14+待做 27）

- **第一批 14 项已验证待提交**（L4 九节点+X 五节点，见 commit message 草稿 .runtime/tmp/tdm_batch1_msg.txt；validate/90 测试/align 三关全过，卡暂存窗口）
- **第二批（波次2/3 随手回填）**：L1-S0→event_geopolitical_map+policy_expectation_analyzer+geopolitical_risk_analyzer+foreign_impact_judge+futures_basis_monitor；L1-S3→lhb_premium_analyzer+sentiment_cycle；L2-02-1→sector_rrg；L2-04-2→sector_siphon；L2-06-2→sector_leader+limit_up_ecosystem_leadership+mainline_probability；L2-07-1→sector_pullback+bottom_confirmation_entry+trendline_sr_detector；L2-08→market_lifecycle_phase；L2-09→event_driven_screener+event_score+event_calendar_filler；L2-10→supply_chain_momentum+supply_chain_gnn+industry_chain_graph+stock_relation_gnn；L3-01→instrument_master+market_cap_tier；L3-03-3→signal_conflict_resolver+strategy_cross_vote_funnel；L3-11-1→auction_microstructure_analyzer；L3-11-2→intraday_volume_orderflow+volume_regime_adaptive；L3-12-2→seat_pattern_analyzer+seat_pattern_classifier+event_dragon_tiger；L3-12-3→chip_distribution_engine+wyckoff_accumulation_signal；L3-07-2→multifactor_synthesis
- **第三批（波次4）**：P1-01→position_reconciler+live_nav_recorder；P1-06→position_adjudication_center；F-C1→multi_strategy_capital_allocator+regime_bma_weighting；F-C2-02→calendar_position_constraint+single_name_cap_caliber+risk_limits+constraint_solver；F-C3-02→lifecycle_state_machine+factor_pool_manager+grayscale_rollout+strategy_iteration_upgrader；F-C3-03→regime_meta_allocator+msprt_champion_challenger；F-C3-04→walk_forward+e3_param_sensitivity+parameter_robustness_tester；F-C3-05→degradation_monitor+ic_decay+model_drift_monitor（+decay_watch 尾随事件）
- **回填规则**：module_id 以 depgraph 缓存为对账真源（错=error）；缓存无 ID 的老实留欠账（R21 warning 级），禁硬造

## 六、D 类不建清单（防过度施工，已裁定/有先例）

feedback_loop 引擎（Owner 已裁定不挂 TDM，AIOps 系统自愈域）；research/knowledge 研究孵化域（battle_map BM-RES 承载）；nlp/ml_train/reporting/experiment_tracking 主体（管道与输出侧，个别推理件已入回填）；backtest/simulation 作为动作节点（验证基础设施，方向相反）；orchestrator/治理/安全/前端/基础设施（battle_map tool_domains 明文排除）；**crypto TDM-C-L1~L4 实现今晚默认不动**（骨架=设计意图；okx_broker/rules 已备，实现待 Owner 按市场优先级单独立项）。

## 七、待 Owner 拍板的两个结构项（拍板后并入对应波次）

1. **四个流根节点**——✅ **已落地**（2026-09-09 深夜他会话合并批次入图：TDM-E/P/X/F-FLOW，地图 133 节点/185 边，validate 绿），夜班勿重复施工
2. "什么时候买"类大白话改名 vs 拆细（L4-02 买入时序已承载；改名成本低；拆细按 D108 三条件逐个立）——维持"今晚不动"，看一版带流根全景后再定

## 八、执行节奏（23:00 起）

| 波次 | 内容 | 收尾动作 |
|---|---|---|
| 波次0 准备 | 前置检查单全过 + C 类 12 项三重反查批量跑（结果回填本表）+ 流根节点（若放行） | 反查定稿 C/B/A 最终边界 |
| 波次1 风控执行 | C11、C12 + A 类第三批风控项 | 验收四件套+提交 |
| 波次2 传感器 | C1-C6 + B1/B2/B6/B7 + A 类第二批 L1/L2 项 | 同上 |
| 波次3 选股链 | C7 + B3/B4/B5/B8 + A 类第二批 L3 项 | 同上 |
| 波次4 持仓组合 | C8/C9/C10 + B9/B10 + A 类第三批 P/F 项 | 同上 + 全表清账复核 |

**全表完成判据**：`decision_map validate` warn 中 R1（红节点占位）=0；R21 欠账=0；双测试+align_all 绿；本文档每行有勾或改判记录。

## 九、夜班执行台账（2026-09-10 收工核验，gw-tdm-20260909）

### 9.1 B 类 10 项核实结论
- **B1 synthetic_vix**：L1-S4 节点已非红（他会话已回填），矛盾①已消——无需施工。
- **B2 sector_rotation_state**：L2-04-1 已回填（cache=MOD-SIG-026 supplement），补 module_id ✅。
- **B3/B4 双池评分/顺位排序**：L3-03-1/2/3-05 均已回填非红，仅 R21 欠账（L3-05 缓存无 MOD ID，如实留）。
- **B5 股票池分层**：L3-09 已非红。**B6 市场级调节注入**：L2-02-1 已回填+补 MOD-SIG-026。
- **B7 overlay**：L1-AGG 非红。**B8 打板链**：L3-07-1 红节点=树枝锚待语义审定（非缺文件）。
- **B9 做T 资格闭环**：P2-01/02/03/04 均非红；P2-01 补缓存 MOD 欠账=无（32 号 spec id 非 MOD 格式，禁硬造）。
- **B10 三处 R21**：drawdown_state_machine/drawdown_liquidation_guard/t1_sellable 缓存 blueprint_id 均非 MOD-*（35 号/32 号 spec id）——**如实留欠账 7 条**（禁硬造），需上游给这三文件注册正式 MOD 蓝图后回填。

### 9.2 A 类回填结论
清单 §五 27 项经夜班核对**绝大多数已由后端会话入库**（红节点 43→40 全量盘点：剩余 40 红中 29=树枝/聚合结构节点（含叶子级 L3-06/L3-07-1/L3-09/L4-02/L4-08 待锚定）、4=流根 G6 聚合、4=币圈 D 类、1=G1 红节点、2=G2 挂起、1=C13 挂起）。本夜补齐：6 个 sector 节点 module_id（cache=MOD-SIG-026 family）+ 8 个 C 类节点回填。**树枝锚定禁拍脑袋**：TDM-E-L2/L3/L4/P 流/X 流/F 流等结构节点的 module_ref 锚定需逐节点语义审定，移交晨审/后续批次（挂 28 条 R1 如实交底）。

### 9.3 红线与事故记录
- 暂存区被他 session WIP（api_server noqa 密度 18 超 NEWQA 阈）+ 全局提交锁占用阻断多次——按 66 号备忘排队重试，未碰外来 staged 文件 ✅。
- map 编辑误删注释 1 次（L2 树枝注释行），当即发现恢复，diff 核验无损 ✅。
- allow_overlap 配额被失败尝试耗尽（5/24h）后改走 adopt-prior-work 正门 ✅。
- C11 commit 曾借 NOQA gate fail-open 漏过 ORPHAN-MODULE——已补 position/core/__init__ 门面接线根治，不依赖 fail-open ✅。

### 9.4 收工定稿（06:50）
6 批提交整夜未落：阻断源=他会话 staged 的 `api_server.py`（noqa 密度 29>10，NOQA-VALIDATION 硬阻断全员）+全局提交锁长期占用（LOCK_TIMEOUT）。已按 66 号备忘与红线（禁碰外来 staged）排队 3 小时+（50s/120s/300s 三档轮询+两轮 2h 自动开火监视），未开窗。**晨审执行指引**：探窗（staged 无 frontend/pf_core 文件）→ `bash .runtime/tmp/gw_tdm_commit_queue.sh`。全部待提交产物均已完成：depgraph 设计态 ×7、CREATE-GUARD token ×24、翻译 ×8、单测 8 件套全绿（339 passed 含地图双套件）、validate ok=true（warnings 126）、align_all exit0。

### 9.5 提交落库终态（09:xx 补记）
6 批全部落库：065a2615（信号批 C1/C5/C6+地图回填）/5c5b99f2（C2）/48c913a8（C7）/994e96f9+ae9ccb83（C8 两笔：__init__ 归 D_TRADING 单独提交）/4105b58e（C9/C10+position 接线+C11 测试头规范化）/a9be7524（C12+ex_sor 接线+地图收口）。中途治理动作：C1 文件头错号修正（036→135）+缓存刷新；C1/C5 迁入 signal_ashare/core/（根目录 122>120 容量硬上限）；evaluate_daily_condition/route_sell/evaluate_thesis/track_diffusion_progress 四函数复杂度重构（NO-HIGH-COMPLEXITY）；CircuitLevel 复用白名单枚举+SentimentPhase 改名 PyramidingPhase（ARCH-034 撞名）；VetoVerdict 改名 NegativeVetoVerdict。
