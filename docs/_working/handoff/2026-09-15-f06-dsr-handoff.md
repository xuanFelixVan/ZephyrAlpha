---
ttl: task_bound
---

# F-06/DSR 交接包——总闸班（DSR 修口径）施工指令

> 交接方：st-f06combo-20260915（通宵班，批次 A 已完成）
> 接收方：下一班会话（Owner 令：新对话一键复刻执行）
> 日期：2026-09-15

## 一、项目背景简介（30 秒版）

ZephyrAlpha 是 A 股个人量化系统，100% AI 多会话并行开发。本线执行「全链路自动化工厂方案」的 P0 件 **F-06 组合层穷尽网格工厂**：用条件参数空间（活性谓词）把"因子→合成→选股→仓位→调仓"的配方空间（名义 362,880 格点）编译、抽样、批量回测，产出结构知识（维度重要性）+ 阴性库 + 幸存者候选。

**当前状态**：批次 A 普查已完成（2000 条实跑、结构知识三件套产出、执行器/ANOVA/编译器全部落库 dev）。**批次 B 的总闸 = DSR 修口径（本交接的下一班任务）**——145 条台账 DSR 因"N 未落账+数据漂移+solo 零折减"冻结中，修完口径才能解冻并供批次 B 消费。

## 二、必读文件（按序，完整路径）

1. `D:\ZephyrAlpha\AGENTS.md` —— 宪法 L0（冷启动序列 §0 + 十二硬规则 §1 + 并发提交 §2，唯一必读）
2. `D:\ZephyrAlpha\docs\_working\2026-09-14-combination-layer-exhaustive-charter.md` —— F-06 立项稿（§十 v2 维度 schema / §十二 两批次 / 文末裁定记录+施工排产总览）
3. `D:\ZephyrAlpha\docs\_working\2026-09-14-dsr-enable-impact-assessment.md` —— DSR 冲击评估（头部第 0 步重算定案新块 + §六 三步走 + 文末裁定记录）← **本班任务真源**
4. `D:\ZephyrAlpha\docs\_working\2026-09-14-full-chain-factory-blueprint.md` —— 全链路蓝图（§十活性谓词机制 / 附录 A 挖矿+A.6 验证核销+A.7 挖矿第二批）
5. `D:\ZephyrAlpha\docs\_working\2026-09-15-neff-estimator-preregistration.md` —— N_eff 估计器预注册（effective_rank 已锁定，本班 A1 实现时遵照）

## 三、工作产物文件（已全部落库 dev）

**代码（本线已建）**：
- `D:\ZephyrAlpha\src\zephyr\position\core\position_recipe_compiler.py` —— MOD-POS-029 编译器（active_if 折叠/内容寻址出生证）
- `D:\ZephyrAlpha\config\position_recipe_grid_schema.yaml` —— v2 十三维 schema 真源（含 industry_anchor 锚点）
- `D:\ZephyrAlpha\scripts\backtest\factory_grid_executor.py` —— MOD-BT-196 批次 A 执行器（抽样/求值/回测/阴性库）
- `D:\ZephyrAlpha\scripts\backtest\factory_grid_anova.py` —— MOD-BT-197 结构知识方差分解
- `D:\ZephyrAlpha\scripts\backtest\factory_intake_pipeline.py` —— E2 四车道+F 车道挂接
- `D:\ZephyrAlpha\tests\backtest\test_factory_grid_executor.py`（20 测试）/ `test_factory_grid_anova.py`（6）/ `D:\ZephyrAlpha\tests\position\test_position_recipe_compiler.py`（12）

**数据产物（批次 A）**：
- `D:\ZephyrAlpha\data\strategy_intake\grid_20260915-052749\` —— manifest.csv（2000 条）+ negatives.csv（1 条带死因）+ summary.json + structure_knowledge.json/md（结构知识三件套）

**DSR 相关（本班要动的）**：
- `D:\ZephyrAlpha\src\zephyr\simulation\deflated_sharpe_calculator.py` —— **官方件 SSOT（单位一致，勿动数学）**
- `D:\ZephyrAlpha\src\zephyr\backtest\core\metrics.py` —— 坏口径 calculate_dsr（年化 SR 配日频 T，实测 DSR=1.0000），A4 退役对象
- `D:\ZephyrAlpha\scripts\backtest\translated\_c4_engine.py` —— batch_deflated_sharpe（num_trials=批内行数口径，A1 改造对象）
- `D:\ZephyrAlpha\src\zephyr\backtest\regime_validation\c4_deflated_sharpe_runner.py` —— DSR 跑批封装
- `D:\ZephyrAlpha\scripts\backtest\c4_batch_screen.py` —— 台账写入链路（A2 N 字段落点）
- `D:\ZephyrAlpha\src\zephyr\simulation\sharpe_calculator_fixer.py` —— A5 阈值统一对象（dsr_threshold=0.95）
- `D:\ZephyrAlpha\src\zephyr\backtest\core\decision_gate.py` —— A5 另一半（DecisionGateConfig，tests 用 0.5）
- 台账：CH 表 `c1_backtest.strategy_screen`（145 条有 DSR / 51 条 is-only；走 `DatabaseService().get_clickhouse_conn().execute()`）

## 四、下一班任务：DSR 修口径（五件，总闸）

- **A1 N 账本累计计数器**：全局累计试验数，真源入注册表；计数边界=裁定锁定"只算可审计的机器回测次数（台账+run 档案）"，人工历史登记为已知下界。
- **A2 台账 N 字段**：strategy_screen 加 `num_trials_used` 字段并回填可考证值。考证方法已验证（第 0 步）：单策略 run=1、多策略 run=批内净收益非空行数（`SCR-C4-20260913-232609`=1、`SCR-C4-20260913-232100`=4、translated 批≈33-48）。schema 变更走生成器禁手改。
- **A3 存量重算**：145 条按可考证 N 重算回填+51 条缺口补齐+重算报告（对已归档结论影响逐条声明；**0.9809 那条恐慌反弹按 N=1 重算后无折减虚高、按累计 N 将跌破 0.5——显式翻案**）。完成后解除 145 条冻结。
- **A4 metrics.py 坏路径退役**：Grep calculate_dsr 全部消费方→迁移官方件或删除；DSR 数学勿重写（官方件 SSOT）。
- **A5 阈值统一**：0.95 放行/0.5 拒/中间存疑 三线 SSOT 化（#14 裁定），sharpe_calculator_fixer 与 DecisionGateConfig 归一。

**裁定已锁勿再议**：计数边界=可审计机器回测；阈值 0.95 不放水到 0.90；三步走=先修口径→再定阈值→后开开关只对新批次（未注入记 `not_tested` 不记 `rejected`）；重算产出是"当日口径新值"须逐条声明与历史值不可逐位比（09-14 行情修复致数据层漂移，同窗口 Sharpe 0.983→1.15 实证）。

## 五、已验证的关键事实与坑（新会话不知道会死）

1. **CH 访问**：`DatabaseService().get_clickhouse_conn().execute(sql)`（无 cursor）；uniqExact/DISTINCT 在 `c1_market.industry_class` 表稳定崩 server（count/DESCRIBE 正常）——该表聚合禁用，观察项已挂数据线。
2. **提交门禁穿行配方**（全部正门）：docs/_working 新文档必须带 `ttl: task_bound` frontmatter；测试同批=--allow-multi-domain；新 .py/.md/.yaml 先在 `capability_canonical_file_registry.yaml` 顶层 `creation_tokens:` 段插 token（safe_write_text+yaml 预检）；错误码先登记 `architecture_model/contracts/error_code_registry.yaml` 的 error_codes 段；该注册表受保护→commit message 加 `[ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001]`；新模块先 claim（GitCommitGateway.claim_files）再 commit；新 .py 跑 add_module_translation.py 登记；[TTL] permanent+argparse 加 `# noqa: m11-perm-manual-legitimate  <理由>`；SQL 常量+TableRegistry.table(category_id)；会话活跃时主区直提交=--allow-non-worktree；锁忙=--wait 或 --enqueue 队列。
3. **Python 3.12 PATH**（Git Bash）：`export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"`；pytest 加 `-o cache_dir=.runtime/tmp/pc_cache`。
4. **执行器降级边界**：86.6% 格点带降级标记（v1 精确实现只覆盖部分取值），结构知识只基于精确子集（246 条）；补齐排 F-02 后续批。
5. **多会话环境**：dev 上他会话高活跃（一小时数个大提交），提交窗口全靠 --wait/--enqueue+重试，禁硬闯；他会话在途 WIP 不代修；后台长任务用 run_in_background（Git Bash `ps aux` 看不到原生进程，核实进程用 `Get-CimInstance Win32_Process`）；长任务先登记 `data/runtime/process_reaper_keep.txt`。
6. **记忆库**：`C:\Users\fanzi\.zcode\cli\memories\projects\zephyralpha-88c39a4848e315f8\memory\f06-compiler-dsr-recalc-20260915.md` ——本线全程细节（含全部坑）。

## 六、执行协议（Owner 常设令）

睡前完全自主执行：遇问题自裁（架构师第一性原理+量化社区实践+开源对照，给出分析过程和裁定结果）；无法裁定的登记+跳过；全部完成后循环检查连续两次测试=0 → 红蓝对抗直接修 → GitCommitGateway 落地 → 临时文件清理 → 全部结束才汇报。提交一律 `python scripts/git_commit.py --session <新sid> --files <清单>`。

> 合规声明：研究方法与工程讨论，不构成投资建议。
