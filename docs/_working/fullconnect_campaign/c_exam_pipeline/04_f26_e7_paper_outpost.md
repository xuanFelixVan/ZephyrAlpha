---
ttl: task_bound
title: F26 E7 模拟盘前哨——L03 接线矿道案卷（工作树施工件实证：missing→built 未落地）
session: zc-l03-20260927
---

# F26 · E7 模拟盘前哨

> 挖矿基册=01_strategy_factory/b2_f26_e7_paper_outpost.md（SF-B，09-25 判 missing）。**本卷 09-27 重大增量：工作树已出现施工件**（总册/今日清单 §1.4/L02 卷仍记 missing——三方均过时，见骨架勘误①）。

## 一、六向台账
| 向 | 实证锚点（09-27 实测） |
|----|------|
| 上游 | strategy_registry lifecycle∈(sim,paper) 名单——**现池 2 条**（MOD-BT-084 lane_e_quantile_baseline＋CAND-e3da6fa71af1 panic_rebound，实读）；list_survivors 经 promotion_advisory.REGISTRY 常量取数 |
| 下游 | 期末判定三件套 {ok,reason,source}+verdict=pass/fail/not_evaluable+建议 continue_sim/demote_shelved/extend_observation；demote 经 lifecycle_fsm sim→shelved 合法边校验（verify_demote_edge 只验边不流转）；落点=run 档案 SCR-OUTPOST-*+c1_backtest.sim_daily_report 汇总行（source=paper_outpost，复用判定台账禁平行账本） |
| 自动触发 | **无**：pipeline_events.py 无 e7_daily/outpost kind（grep 实证），本件仅 CLI 手动（`python -m zephyr.strategy_pipeline.paper_outpost`）；邻接 sim 日链（SIM_DAILY_KINDS FIFO 四件）绿至 09-26 |
| 真源注册表 | **config/strategy_production_map.yaml 工作树 diff（未提交）**：FAC-E7 `module_ref: null→MOD-BT-225`/`build_status: pending→built`/`store_refs 待定→data/backtest_artifacts/runs/`（git diff HEAD 3 行实证）；HEAD 版仍 null/pending=总册 missing 判定对 HEAD 成立 |
| 门禁质量尺 | 已实现：N 周窗（DEFAULT_WEEKS=4）+逐日对账（市场隐含盈亏 vs 判定台账账面盈亏，sim_pocket_daily+sim_trade_log+kline 收盘价口径）+三件套范式+fail-closed（落库未确认 RuntimeError 上抛/幸存者名单空）；**未实现：滑点/容量实测档（收盘价口径≠图上硬要求，B-E7 第 4 项两案仍待裁）** |
| 运行状态 | **工作树 built+测试绿+零生产运行**。paper_outpost.py 396 行（untracked）+test_paper_outpost.py **18 passed 本日实跑（10.2s）**；data/backtest_artifacts/runs/ 154 项中 **SCR-OUTPOST-* =0**（从未真跑） |

## 二、子模块三级枚举
1. **代码面**：src/zephyr/strategy_pipeline/paper_outpost.py（list_survivors:120/outpost_window:147/daily_deviation:175/summarize:221/verify_demote_edge:259/run_outpost:264/_land:322/main:378；--weeks/--end-day/--strategy-ids/--dry-run 四参）；tests/strategy_pipeline/test_paper_outpost.py 18 用例。**两文件均 untracked 未提交**；除自引用外全仓无消费者（grep 实证）。
2. **注册表/文档面**：FAC-E7 图节点（工作树已指向 MOD-BT-225）；**注册面三缺**：docs/03_modules/_domain_backtest/blueprint.md 无"模拟盘前哨"节（grep=0，而码内 BLUEPRINT 头注指向该节）；模块注册表 catalogs 无 MOD-BT-225 条目；未见 add_module_translation 登记——TRANSLATION-COVERAGE/CREATE-GUARD 等 commit 门均未过（与 untracked 态一致）。与 F72 边界：docstring 自述"E7=考核期/F72=转正汇总，共用 sim_pocket 账本面"（B-E7 第 8 项已落）。
3. **数据面**：runs/ 无 SCR-OUTPOST-*；判定台账无 source=paper_outpost 行；c1_backtest.sim_daily_report 表构在用（sim_daily_runner 写入方）——落点表真源在。

## 三、接线四态独立复核
- 总册/今日清单 §1.4/L02 卷：missing → **HEAD 态维持 missing；工作树态=built（未落地）**。
- **骨架勘误（本卷主项）**：①F26 非"零起步"——B-E7 八项前置中 1/2/3/5/6/8 已在工作树落地（名单器/逐日对账/参数窗/判定器/落点复用/F72 边界），第 4 项滑点实测档未做、第 7 项事件接线未做；②总册与今日清单的 missing 判定需注记"工作树在途施工件存在，落地四缺：提交/注册/接线/首跑"；③基册"registry sim 名单 1 条"→2 条。
- L02 P0"缺位"交叉：**P0 性质变更**——从"施工缺位"变"临门一脚"（差 commit+接线+首跑）。

## 四、缺口清单
| # | 现象 | 证据 | 处置 | 优先 |
|---|------|------|------|------|
| 1 | 施工件未提交未注册 | untracked+蓝图 0 命中+无 MOD-BT-225 注册 | Owner 派工走正门提交批（补蓝图节/注册表/add_module_translation/creation_token）；1 个提交批 | **P0** |
| 2 | 零事件接线（纯 CLI） | pipeline_events 无 kind | SIM_DAILY_KINDS 追加 e7_daily（照抄 attribution_daily 范式，B-E7 第 2/7 项）；S-M | P0 |
| 3 | 零生产运行 | runs/ 无 SCR-OUTPOST-* | 首跑 --dry-run→真跑 2 条 sim 池（N=4 周窗）验证落册 | P0 |
| 4 | 滑点/容量实测档缺（收盘价口径） | 码内对账=kline 收盘价 | B-E7 第 4 项两案（真单腿桥 vs 五档扫描）待裁后补档 | P1（待裁） |
| 5 | sim 池仅 2 条且非管道产物 | registry sim 2 | BP-5 首条自动入库后池自补 | P1 |

## 五、自审闸三态
**挖干（缺位定性升级为在途施工定性）**。missing→工作树 built 有完整证据链（diff 3 行+18 测试+码面结构）；四缺清单即落地路径；滑点档与落点两小案待裁随册呈总筹。

## 六、复跑命令
```bash
cd /d/ZephyrAlpha
git status --porcelain src/zephyr/strategy_pipeline/paper_outpost.py   # ?? 未跟踪
git diff HEAD -- config/strategy_production_map.yaml                   # FAC-E7 3 行 null→225
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
python -m pytest tests/strategy_pipeline/test_paper_outpost.py -q      # 18 passed
grep -rn "MOD-BT-225" docs/03_modules docs/01_policies_and_standards/_registry/catalogs | wc -l  # 0=注册缺
ls data/backtest_artifacts/runs/ | grep -c OUTPOST                     # 0=零运行
python -m zephyr.strategy_pipeline.paper_outpost --dry-run             # 只算不落册
```
