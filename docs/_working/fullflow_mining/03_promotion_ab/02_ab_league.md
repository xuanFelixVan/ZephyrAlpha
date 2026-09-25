---
ttl: task_bound
session: st-ailayer-fullflow-pr-a
creation_token: fullflow-pra-f73-ab-league-20260925
title: F73 A/B 联赛与分仓——六向台账（联赛五件已建+机制三缺位实证）
date: 2026-09-25
status: 待施工（基建 built/机制空场）
---

# F73 A/B 联赛与分仓（champion-challenger 守擂踢馆 + 等风险预算分仓 + ρ>0.7 相关性闸）

> 挖矿代理 PR-A。**M0 口径勘误先行**：总册 F73 状态标 `design（晋升判据执行器未写）`/分工册标"从未立册"——**已过时**。实测：09-21 TC-11 件1 施工批（裁定#392 D 批打包，ruling_registry.yaml:5267；st-taskcards-exec-20260921）已建联赛基建五件+测试，蓝本=HANDOFF_20260921_ab_league.md §2 件1（Owner 明令"现在就要跑起来"）。缺的是**机制三件**（晋升判据执行器/相关性闸执行器/分仓）与**任何一场实际比赛**。

## 一、环节定义与边界

- **一句话**：模拟盘四件产出的消费端竞技制度——A 组 champion 守擂/B 组 challenger 踢馆，6 个月终审一次性判胜负（判定器复用 promotion_combo_gate 本体零修改），月度只留档不判胜负；配套 1000 万模拟仓等风险预算分仓与 ρ>0.7 相关性合并闸（骨架 v1.1 §7）。
- **上游**：F72（sim_pocket_daily equity 序列=成绩原料）；标准库（STD-SWITCH-001/STD-SIM-ACCESS-002）。
- **下游**：F74 转正门（challenger 上位建议→Owner 拍板）；league_archive→终审证据链。
- **边界**：月度快照**只留档不判胜负**（league_monthly_snapshot.py INVARIANTS 明文）；任何冠亚军判定归 6 个月终审 Owner 门。

## 二、六向台账

| 向 | 内容（实证锚点） |
|----|------------------|
| 上游输入 | c1_backtest.sim_pocket_daily（267 行实测，equity 序列）；c1_backtest.strategy_screen（E4 成绩）；data/strategy_intake/promotion_advisories/*.json（promotion_combo_gate.py:11 声明消费——**目录不存在=零流入**）；config/standards.yaml 三尺 |
| 下游消费 | Owner 终审门（6 个月挂单=league_registry.yaml review_policy，A/B 组 due=2027-03-21）；league_restore.py（读 manifest 三指纹核对）；晨报/交接（月度对比引用） |
| 自动化触发 | **零排产**：config/schedule.yaml 无 league 条目（grep 实测）；无计划任务（schtasks Sim/Paper 过滤零命中 league）；全件 manual CLI（M11 manual 合法先例同 sim 家族）；月度快照纯靠人记得跑 |
| 真源与注册表 | config/league_registry.yaml（席位/参赛档案/判定窗**唯一登记真源**，阈值不复制防第二真源）；config/standards.yaml（尺真源：STD-SIM-ACCESS-001 frozen ⚠#306 suspect、**002 v2 frozen 09-18 裁定#337**、STD-SWITCH-001 draft）；exam_policy.md（考试语义前置，裁定#365）；裁定#392（批建授权） |
| 门禁与质量尺 | 判定器复用 promotion_combo_gate 本体零修改（league_registry.py INVARIANTS）；挂单回写唯一入口 schedule_review（CAS safe_write_text 写后回读校验）；先 freeze 后开考；档案三指纹缺 git hash 硬失败 fail-closed；复原判定三态 faithful/restorable/unverifiable 不硬判 |
| 当前运行状态 | **基建绿/空场红**：五件代码+测试 65 passed（实测 1.42s）；但 A/B 两组 members=[]（零参赛者）、archive_path=""（零档案）、review_scheduled=false（零挂单）、data/backtest_artifacts/league/ **目录不存在**（月度快照从未跑过）、promotion_advisories 目录不存在（上游零流入）——联赛建成至今未开过赛 |

## 三、子模块清单（ls + BLUEPRINT 头 + 测试实跑交叉验证）

| # | 件 | 是什么 / 入口 | 状态 |
|---|----|---------------|------|
| 1 | config/league_registry.yaml | 联赛注册表 v0（49 行）：组 A=champion/B=challenger 初始席位（09-21 入组）；review_policy.window_months=6+judge+judge_std_id=STD-SIM-ACCESS-001+snapshot_dir；members/archive_path/review_scheduled 回填位 | built **空场** |
| 2 | scripts/backtest/league_registry.py | MOD-AUTO-L11-REGISTRY（201 行）加载/校验/终审挂单 API（schedule_review CAS 回写） | built（测试在） |
| 3 | scripts/backtest/league_monthly_snapshot.py | MOD-AUTO-L11-SNAPSHOT（210 行）sim_pocket_daily 按组拉 equity→对比表→snapshot-YYYYMM.md；CH 断供降级记缺口不硬造成绩 | built **零运行**（产物目录缺） |
| 4 | scripts/backtest/league_archive.py | MOD-AUTO-L11-ARCHIVE（284 行）参赛档案打包：三指纹=代码 git hash+因子定义清单+数据截止日；manifest 含 restore_semantics 诚实边界；目录只新增不覆写 | built 未用 |
| 5 | scripts/backtest/league_restore.py | MOD-AUTO-L11-RESTORE（180 行）复原判定器：只核对不执行（禁自动 git checkout，切换须人） | built 未用 |
| 6 | scripts/backtest/promotion_combo_gate.py | 骨架 §7/§8 首件：模拟盘准入组合门打分器+转正建议书渲染；四条阈值硬编码 v1（OOS Sharpe≥1.5/MaxDD≤15%/成交≥30 笔/DSR>0），三态输出 promote_ready/reject/borderline，产出 docs/_working/pipeline-research/promotion-reports（**目录不存在=零评分**）；被 league review_policy 登记为终审判定器 | built，**尺漂移**（堵点 5） |
| 7 | tests/backtest/test_league_registry.py / test_league_archive.py / test_league_restore.py / test_promotion_combo_gate.py | 四件测试（快照测试类内嵌于 archive 测试） | **65 passed in 1.42s 实测** |

## 四、堵点与病灶

| # | 现象 | 根因 | 修法草案 | 工作量/归属 |
|---|------|------|----------|------------|
| 1 | **空场**：零策略参赛，联赛无从开赛 | 上游 F72/F74 链路零流量——promotion_advisories 目录不存在=intake sim 流转从未产出 advisory；注册表策略无一人进 sim 态 | 先让首位参赛者走通：E4 幸存者→intake sim 流转→advisory 产出→入 A 组 members+archive 打包 | 依赖 F74（PR-B 册）；1 策略试点半天 |
| 2 | **晋升判据执行器未写**（骨架 §4 P1 明示"新写"）：champion vs challenger 对比判定零代码——现有 judge 只做个体准入打分，无"A 显著优于 B"的成对判定（DSR 显著性+持续 6 月+容量滑点+降级标记 regime 复活四条件） | TC-11 件1 范围只到基建+挂单登记，对比赛制本体留待"新写" | 新写 league_judge：成对 DSR（msprt e-process 口径接 STD-SWITCH-001 pair_decision_engine）+族多重比较 BHY q=0.10（league_family_scope 已登记） | 2-3 天；前置 STD-SWITCH-001 draft→frozen |
| 3 | **相关性闸执行器未写**：ρ>0.7 合并算额度只在尺上（STD-SWITCH-001 correlation_gate_rho=0.7+STD-SIM-ACCESS-002 combo_corr_max=0.7 双登记），全仓零消费者（league_*/combo_gate grep 零命中）——尺在闸无 | 阈值登记先于机制施工（先 freeze 后开考的正确顺序），执行器属"新写"未动工 | 随堵点 2 同件实现（闸是判定前置步不是独立系统） | 并入堵点 2 |
| 4 | **分仓未写**：等风险预算制（champion 40%/挑战者各 15%/新入场 5-10%/现金机动 10-15%）零代码（全仓 grep 唯一命中 factory_grid_executor.py=策略工厂网格域，非本件）；1000 万模拟仓的跨组资金分配无承载 | 骨架 §7 v0 数字"靠模拟盘数据校准后冻结"——数据未至（空场），分配器自然未建 | league_allocator 最小件：读 members+equity→等风险预算权重表落 data/backtest_artifacts/league/；与 M2 07 册 pf_alloc SIM_DAILY 事件先对账防重复建设 | 1-2 天；前置堵点 1 |
| 5 | **尺-器漂移**：promotion_combo_gate THRESHOLDS 硬编码 v1 四条（含 dsr_min=0.0——已被裁定#306 实证"数学不可过"suspect），而 v2（dsr≥0.5+N_eff 封闭族+capacity_evidence+turnover≤12+combo_corr）09-18 已 frozen（裁定#337 双尺重考 81 覆盖/55 翻转零不可解释达标）；且 league_registry review_policy.judge_std_id 仍写死 001（头注自辩"终审以当日标准库状态为准"与字段写死并存=张力） | 判定器先于 v2 转正建成，未回升 | combo_gate 改读 standards.yaml 动态取尺（删硬编码=消第二真源），judge_std_id 跟升 002；重考义务=v2 change_rule 已载 | 半天-1 天；本车道可修 |
| 6 | **月度快照零排产**：manual 无槽位，"每月对比"靠人记 | M11 manual 豁免只豁免"无常驻"，未给月节拍安排入口 | 入 schedule.yaml 月槽（空场也可空跑出空表=链路保温）；与 F72 堵点 4 月度三件同批排产 | 1 小时；SC 调度 |
| 7 | **蓝图锚悬空**：四件 league_*.py [BLUEPRINT] 均指向 docs/_working/automation/campaign/mining/11_联赛/工段作业簿.md——该文件不存在（HANDOFF 件1 计划"先挖矿封矿"未落地；mining/ 下实存 01-09 无 11） | 施工先行、作业簿未建 | 补建 11_联赛 作业簿或四脚本改锚 08_模拟盘转正门册 | 半小时；AI 层车道协议 |
| 8 | **终审挂单无提醒**：review_scheduled=false，due=2027-03-21 无日历消费方/探活 | 挂单登记位建成，提醒机制不在件1 范围 | 随堵点 6 月槽顺带对账 due（快照表内联 due 倒计时列） | 并入堵点 6 |

## 五、提速与合并机会

**A/B 联赛最小可施工件清单**（分工册点名要答；按依赖序）：
1. 修尺（堵点 5，半天，无依赖，本车道即可施工）——性价比最高：不修尺，终审用的还是"数学不可过"的 v1。
2. 补锚（堵点 7，半小时）+排产（堵点 6/8，1 小时，与 F72 月度三件合并一张月槽工单）。
3. 首位参赛者试点（堵点 1，依赖 F74 链路，PR-B 册对接）——联赛从"建成"到"开赛"的唯一钥匙。
4. league_judge 成对判定执行器+相关性闸（堵点 2/3，2-3 天，前置 STD-SWITCH-001 frozen）。
5. league_allocator 分仓（堵点 4，1-2 天，前置 3；先对账 pf_alloc 防双建）。

**合并机会**：月度节拍一张工单（F72 月度三产出器+F73 月度快照+终审 due 对账，同槽同探活）；判定器修尺与 F74 汇总器（PR-B）打分口径同源（都吃 standards.yaml），宜同一施工批。

## 六、自审闸三态

- **六向实证完整性**：上游（CH 行数+消费方 file:line）/下游（review_policy+Owner 门）/触发（零排产 grep 三连证）/真源（注册表 YAML+standards+裁定#392/#337/#306）/门禁（INVARIANTS+CAS+fail-closed）/运行（65 passed+产物目录不存在双证）——每向≥2 源。
- **待裁项**：无 Owner 门位争议案；堵点 5 修尺属"改判定器读法"非修标（尺本体不动），本车道可修；若 Owner 认定 judge_std_id 跟升需裁定背书，则列晨报一行。
- **三态结论**：**待施工**（精确态=基建 built/机制空场：五件+判定器+测试绿实证在盘，但零参赛者/零快照/零挂单，晋升判据执行器+相关性闸+分仓三件新写未动工；既非 M0 所记"design 未建"，也够不上"挖干可施工"）。

## 七、复核命令（10 分钟口径）

```bash
# 1. 联赛五件与空场证据
ls -la scripts/backtest/league_*.py config/league_registry.yaml
grep -n "members:\|archive_path:\|review_scheduled:" config/league_registry.yaml   # 全空=空场
ls data/backtest_artifacts/league 2>&1          # 不存在=快照从未跑
ls data/strategy_intake/promotion_advisories 2>&1  # 不存在=上游零流入
# 2. 测试绿
python -m pytest tests/backtest/test_league_registry.py tests/backtest/test_league_archive.py tests/backtest/test_league_restore.py tests/backtest/test_promotion_combo_gate.py -q -o cache_dir=.runtime/tmp/pytest_cache_fullflow   # 65 passed
# 3. 尺-器漂移
grep -n "THRESHOLDS" -A 6 scripts/backtest/promotion_combo_gate.py   # v1 四条硬编码
grep -n "STD-SIM-ACCESS-002" -A 12 config/standards.yaml             # v2 frozen 实体
# 4. 授权链
grep -n "裁定#392" docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml | head -2
sed -n '1,40p' docs/_working/automation/campaign/HANDOFF_20260921_ab_league.md   # 件1 蓝本
# 5. 蓝图锚悬空
ls docs/_working/automation/campaign/mining/    # 无 11_联赛
```

## 附：矿脉增补（回填总筹）

1. M0 总册 F73 行状态列 `design（晋升判据执行器未写）` → 应改 `partial（基建五件 built 09-21 批+测试 65 绿；晋升判据执行器/相关性闸/分仓三缺位；零参赛空场）`——M0 挖矿（09-25 凌晨）漏检 09-21 已落地件，属"登记态→实件化"盲区实证。
2. league 件1 基建属 TC-11 任务卡体系（裁定#392 D 批打包裁定），非 automation 骨架工单队列——骨架 §4 P1"A/B 联赛编排"工单与 TC-11 件1 的关系（部分已消化）宜在骨架册对账一行。
