---
ttl: task_bound
---

# 2026-09-17 今晚变更抽审报告（Sharpe2 决赛准备战·分包C①）

- 审计子代理: st-sharpe2c-20260917（审查者角色，只产报告不施工，符合 deep_review_policy §1"审查者只出报告"）
- 审查基线 commit: `fe8fce25b7`（2026-09-17 报告落盘时 HEAD）
- SOP 真源: [deep_review_policy.md](../../../01_policies_and_standards/sop/review_sop/deep_review_policy.md)（六轴/证据纪律/严重级四档）+ [defect_pattern_checklist.md](../../../01_policies_and_standards/sop/review_sop/defect_pattern_checklist.md)（14 条前置过一遍）
- 抽样口径说明: deep_review_policy 未规定抽样率（其方法论为"对象全查"），按任务书裁量抽 50 件、分新迁移/旧留/修复复发三层。

---

## 1 变更基线考证（"约 1.7 万文件变更"口径核实）

**结论：不成立。没有任何口径能数出 1.7 万个文件；最接近的数字是 172,092 行变更，疑为"行"被误记成"文件"。**

| 口径 | 数值 | 取证命令 |
|---|---|---|
| 提交数（2026-09-16 18:00 后） | **126 个**（首commit b9819fcbe9@18:05，末 08c696f0c5@00:48+） | `git log --since="2026-09-16 18:00" --oneline \| wc -l` |
| 提交链触碰文件（去重） | **3,959** | `--name-only` 去重计数 |
| 提交链触碰文件（含重复触碰） | 5,014 件次 | `--shortstat` 求和 files_sum |
| 提交链行变更 | **+108,994 / −63,098 = 172,092 行** | `--shortstat` 求和 |
| 工作区未提交变更（porcelain 行） | **444**（220 MM / 93 A / 83 M / 48 ??） | `git status --porcelain` |
| 两口径并集（真实"今晚动过的文件"上界） | **4,176** | 提交集∪工作区集去重 |
| 参考口径：整个 09-16 全天提交链去重 | 6,262 | `--since="2026-09-16 00:00"` |
| 参考口径：自 09-15 18:00（380 commits） | 去重 6,714 / 件次 8,657 | 同法 |

主要构成核实：确为 ALGO_FLOW 出仓波次（grp6 part1/2 480 件×6 小批 + part2/2 266 件×3 小批 + note-gated 18 件 + 死块复发清偿 17+1 件，提交链 6b44f342a1 / 074e79215c / d19747250c / adeb28bff0 / 008b99858e / 8bb5da3b95 / 622ee74103 / 5d5a58d23d / 8ec17e6887 / 56eea4d2de 等）+ docs/03_modules/*_domain_*/algo_flow yaml（全库 3,158 件）。触碰热区 top：`src/zephyr/gov_enforcement/commit_gates`(112)、`_domain_intelligence/algo_flow`(76)、`_domain_gov_drift/algo_flow`(73)、`src/zephyr/gov_drift`(65)。

**给任务书的更正口径**：今晚（18:00 后）真实变更 ≈ 4,176 个文件（并集）/ 172,092 行变更。"1.7 万文件"应为"17.2 万行"的量纲误记。

---

## 2 ALGO_FLOW round-trip 抽验

### 2.1 机制考证（锚的真身）

- `[BLUEPRINT] MOD-XXX | <blueprint路径> [| §N.N]` 锚在**源码 .py 头部**（src 下 3,475 件有锚），不在 yaml 头部（yaml 头仅 9 件提及且多为注释）。
- yaml ↔ py 双向由 `[ALGO_FLOW] external: <yaml路径>`（py 侧）与 `source_of_truth:`（yaml 侧）承载。
- blueprint.md §段落标题格式 `### §N.N 标题`；命名锚（如 `§kill_switch`）多数**无对应标题**。

### 2.2 全量普查（Phase A，非抽样，便宜检查全跑）

| 检查 | 结果 | 定性 |
|---|---|---|
| yaml → source_of_truth .py 存在 | 3,158/3,158 ✓ 0 缺失 | 健康 |
| py `[ALGO_FLOW] external:` → yaml 存在 | 0 缺失 | 健康 |
| 双向路径一致性（yaml.sot == 锚 py） | 0 错配 | 健康 |
| py → 回指 yaml（全文件复核后） | 0 缺失（首轮 91 件全为 60 行窗口假阳性，已逐件排除） | 健康 |
| `[BLUEPRINT]` 锚 → 蓝图文件存在 | **218/3,475 (6.3%) 指向不存在蓝图** = 94 件占位符（`(pending)` / `(auto-injected by S4 reconciler)`）+ **124 件真实路径死链** | 缺陷（详见 §3） |
| 锚带 § 段落 | 仅 622/3,475 (17.9%)；**2,853 (82.1%) 无 §** | 缺陷（trae_006 模板 `§{N}` 应填） |
| § 段落可解析（token 在蓝图文本出现） | 348/622 (55.9%)；**274 (44%) 不解析** | 缺陷 |

### 2.3 分层抽样 50 件深度检查（Phase B）

分层：修复复发 18（提交 622ee74103 的 17 件 + 074e79215c 的 akshare_provider，全取）、新迁移 20（今晚提交链内 1,743 件中随机）、旧留 12（1,397 件中随机）。种子 20260917。

**合格率（三档口径并报，禁只报好看的）：**

| 口径 | 合格 | 分层（复发/新/旧） |
|---|---|---|
| 严格（锚真实 ∧ 蓝图存在 ∧ § 存在且可解析） | **0/50 (0%)** | 0/18, 0/20, 0/12 |
| 宽口径（锚真实 ∧ 蓝图文件存在；§ 允许缺） | **26/50 (52%)** | **7/18 (39%)**, 13/20 (65%), 6/12 (50%) |
| 硬失败 | **24/50 (48%)** | 11/18, 7/20, 6/12 |

24 件失败经三轮甄别（60 行窗口→全文件→蓝图内文本/标题语义复核），**全部坐实为真失败，0 误报**（首判"宽松通过"5 件经精确复核也是假通过：genesis/kill_switch 的 §genesis/§kill_switch 在蓝图 §0.1 中明确标 `§ —`（段落未写），宽松命中只是 frontmatter tags 里的连字符词）。

失败明细分类（24 件）：

| 类别 | 件数 | 代表件（yaml） |
|---|---|---|
| 占位锚（蓝图路径=`(auto-injected by S4 reconciler)`/`(pending)`） | 9 | `_domain_execution_core/algo_flow/daban_exit_decision.yaml` 等 daban 系 6 件、`_domain_data_security/algo_flow/data_security__init__.yaml`、`_domain_factor/algo_flow/momentum.yaml`、`reversal.yaml` |
| 蓝图字段是散文占位（"待统筹登记…"）且文件不存在 | 1 | `_domain_research/algo_flow/evidence_chain.yaml` |
| 锚无 § 段落（`| §` 空段） | 3 | `_domain_shared/algo_flow/contracts/execution/execution_report.yaml`、`lifecycle/lazy_loader.yaml`、`resilience/fallback.yaml` |
| § 段落不存在（含蓝图 §0.1 明标 `§ —`、token 零命中、仅表格提一句） | 9 | 4×`_domain_infrastructure/algo_flow/adapters/*`（§M4 零命中）、`access_control/genesis_bootstrap.yaml`、`kill_switch.yaml`、`_domain_gov_enforcement/algo_flow/mcp_server.yaml`（§4.4 零命中）、`translation_coverage_reconciler.yaml`、`reference_extractor.yaml`（§4.1 仅表格引用非标题） |
| py 全文件无 `[BLUEPRINT]` 锚 | 2 | `_domain_signal_quality/algo_flow/infrastructure__init__.yaml`、`_domain_machine_learning_train/algo_flow/api__init__.yaml` |

**判读**：出仓波次把 yaml↔py 的算法承载链（external 锚）做干净了（全量 0 断链，这是今晚波次的主目标，达成）；但 **[BLUEPRINT]→蓝图→§ 这条"文档回环"链是系统性欠账**（严格口径 0/50），且**修复复发层失败率最高（11/18）**——"复发清偿"只治了 yaml/external 锚，没治 [BLUEPRINT] 锚，复发名符其实。机械校验脚本与逐件结果存 `.runtime/tmp/c_audit_algo_flow_results.json`。

---

## 3 缺陷挂单清单（只挂单不修，严重级按 deep_review_policy §4）

| # | 级 | 文件:行号 | 证据 | 修复建议（供主力会话） | 验证法 |
|---|---|---|---|---|---|
| D1 | **P1** | `scripts/backtest/f06_e4_wfa_exam.py:355-367,403`（对照 `:334-337`、`:487-488`） | OOS/IS 比率门控（0.70 硬线）分子=本考 WFA 拼接路径 OOS sharpe（2019-06 预热+折相位），分母=幸存者登记面 E4-v1 的 IS sharpe（2023-06 预热+周相位）。verdict.md 自己写明"预热起点与周频调仓相位不同，逐位不可比"（`:488`）。两个不可比口径之比被当硬否决线用——统计口径单点漂移（模式 #1） | 比率门控改用同引擎同预热重算 IS sharpe；或将 0.70 比率降级为"参考指标"并以同口径对照为主判定 | 用同一 `evaluate_recipe` 在 IS 窗重算 is_sharpe，对比登记值差异是否显著改变 ratio |
| D2 | **P2** | `src/zephyr/ex_core/daban_load_producer.py:458,586,692,702,735` | 打板决策链输入件 5 处 `except Exception → 降级空/default`（fail-open）。虽有 `_logger.warning` 留痕且 [INVARIANTS] 声明"上层 fetch_load 空→策略告警"，但本层断供时下游拿到的是中性默认值而非异常——数据源静默死亡模式（#6：断供时报错还是恒 0？） | 核实策略侧"fetch_load 空→告警"消费点真实存在并注册告警项；对 load 三腿（宽度/指数/成交额）分别加断供计数器 | 断开 events 表模拟空返回，确认策略侧是否产生可见告警 |
| D3 | **P2** | `data/backtest_artifacts/runs/E4-F06-38b453ca/summary.json` gate 块 vs overfitting 块（产自 `f06_e4_wfa_exam.py:170-215`） | 同一份数据两个"灾难"判定打架：overfitting.reasons 明写"Walk-Forward存在灾难fold(最低Sharpe=-1.00<-0.50)"，而 gate.wfa_stage.has_disaster=false、wfa_passed=true(7/8)。两个判定件对"灾难回撤"不同阈值/口径，verdict 映射只信 gate 侧 | 统一灾难 fold 定义（同一阈值常量、同一判定源），或把 overfitting 灾难理由升级为 verdict 输入 | 对照 `decision_gate` 与 `overfitting_detector` 各自的灾难阈值常量 |
| D4 | **P2** | 全仓 3,475 锚普查（§2.2）：94 占位锚 + 124 死蓝图链 + 2,853 锚无 §；今晚复发清偿件复发率 11/18 | [BLUEPRINT]→蓝图→§ 文档回环系统性欠账；trae_006 模板要求 `§{N}` 必填；现有 gate 未拦住占位符形态（`(auto-injected by S4 reconciler)`、`(pending)` 可过提交） | blueprint_format_gate 增加占位符黑名单判据与 § 必填判据（先 warn 后 hard）；94+124 件挂账分批清偿 | 对样例件跑该 gate 看能否拦住 |
| D5 | P3 | `scripts/backtest/f06_e4_wfa_exam.py:29` vs `:112` | 文档字符串"折 1-4 测试段(2022-01..2023-12)"与 0 基 fold 编号（`fold: len(folds)` 从 0 起）错位；verdict.md 模板 `:487` 按动态计算写"折 0-N" | 文档改 0 基或动态生成 | 读 summary.json folds[0].fold==0 |
| D6 | P3 | `scripts/backtest/f06_e4_wfa_exam.py:155` | `fold_metrics_from_net` 中 std==0 时 sharpe 硬置 0.0：恒正收益序列（std=0）会被记为 0 而非发散/异常标记，静默吞掉退化情形 | std==0 时记 NaN 并留痕，让门控走 fail-closed | 造常数收益序列单测 |
| D7 | P3 | `src/zephyr/backtest/core/cost_model_calibration.py:393-407` | `impact_level_for_tier` 直接下标 `IMPACT_TIER_ETA[tier]`/`IMPACT_TIER_SIGMA[tier]`，两表长度与 `n_tiers()` 不一致性无校验（滑点表 `:214` 有校验，冲击表没有）；表漂移时抛 IndexError 而非 CostCalibrationError，违 ERROR_CONTRACT"非法输入一律抛本错" | 加同款长度一致性断言抛 CostCalibrationError | 改短 IMPACT_TIER_ETA 后调用看异常类型 |
| D8 | P3 | `src/zephyr/backtest/core/decision_gate.py` check_oos_stage docstring（`dsr_threshold` 默认值定义在 `:445`） | docstring 仍写"DSR可选判定器(默认关闭)"，而 2026-09-16 车道 L 接线已把默认改为显式开启（`:420-425` 注释自述"默认由关闭改为显式安全默认"）——同文件内文档自相矛盾（文档矛盾=事故，宪法 §4.3） | 更新 docstring 与 `:445` 实况一致 | 读两处对比 |

（顺带发现、不计挂单：`c4425e60cb` screen_source 修复质量良好——SQL 注入面被 notes 解析正则约束、19 测试覆盖、存量行逐位不变；`run_f06_grid.ps1`/`register_f06_grid_task.ps1` 纯 ASCII 合规。）

## 4 完备性自评

- 六轴未全开（本审计为抽样复核非单对象深审）：轴 F（SOTA 对照）未做——新车道核心算法（DSR/WFA/成本标定）SOTA 对照需独立窗口；轴 C 消费方全列仅对 daban_load_producer 做了下游追查。
- 工作区 444 件未提交变更未逐件审（属在途施工，宪法 §3.4 他会话在途违规不代修）。
- 基线 `fe8fce25b7` 后并行施工会使个别行号过期，收口方按 §6 重验。
