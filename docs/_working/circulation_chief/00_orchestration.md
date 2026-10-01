---
ttl: task_bound
---

# 全流通清场总包作战书（st-ffchief-20261001）

> Owner 令（2026-10-01 13:00）：全部开工；最终目标=工作区全净（提交/分支 dev/worktree/暂存区/锁/注册表/脏数据/盲点）；先挖矿后施工、线间并行流水；六向台账+自审闸三态=挖干判据；内收原则施工；自裁不留问；连续两轮零+红蓝对抗收官；GitCommitGateway 落地+临时文件清理。Owner 睡眠期间全程自主，不中断不提问。

## 0. 总包会话与裁定授权

- 总包会话：`st-ffchief-20261001`（全部 claim/commit 用此 sid）。
- 裁定授权：Owner 明授自裁权（架构师第一性原理/长远战略/100% AI 开发前提/量化社区与开源实践对照）。重大裁定须同 commit 登记 ruling_registry（RULE-RULING）；无法裁定→登记跳过，终报留给 Owner。
- 施工红线：禁裸 git commit/reset --hard/clean/stash drop/plumbing；提交只走 `scripts/git_commit.py --session st-ffchief-20261001`；改前 claim、毕后 release；热册 safe_write_text CAS；新建 .py 先 `add_module_translation.py` + CREATE-GUARD token + capability_lookup；测试输出只进 tmp_path/.runtime/tmp；.ps1 纯 ASCII。

## 1. 友军共存在册（开车道前必查刷新）

| 友军 | 状态判据 | 禁区 |
|---|---|---|
| st-fullscore-20260930 | 心跳活跃，13:00 仍在 staged 化 | factory_intake_pipeline/cost_model/strategy_pipeline intake+promotion_advisory/ollama_chat 及其 tests、fullscore_night+integrated_backtest 文档 |
| st-chief7-20260928 | 收官自动机在册（约每2h，触发即终验+释放 claim+自删） | 其 claim 面；勿杀其心跳守护 |
| lanech merge 自动机 | 每 ~15min 一轮，busy=[factory_intake_pipeline, capability册, 翻译册]，成功自删 | 勿代并 lanech 分支；勿动其 busy 三件 |
| st-c10-* 四道 | 心跳 26s 级刷新 | 其 staging/产出面 |
| 队列 belt | 空闲=无人占道；有 processing=等它 | — |

每车道开工前重跑：`python -c "import json,time;reg=json.load(open('.runtime/session_registry.json'));[print(s,int(time.time()-v.get('last_activity',0))) for s,v in reg.items()]"` + `git diff --cached --name-only`。

## 2. 车道与顺序（线内先挖后干，线间并行流水）

- **S1 清场批**（总包亲理，最优先）：4 死袋（先 grep HEAD 查吸收：已吸收→弃袋销账；未吸收→修处方重投）；死 claim 释放（w3h/w3harvest/circ-integ 即放；fullscore 活着不动，收官时复核）；垃圾清理（.tmp.28828.* 三件 PID 已死→移 .runtime/tmp/campaign_trash；.bak 同）。
- **S2 骨架挖矿**：环节总数清点→`skeleton/00_skeleton.md`（段→环节→上下游/自动化态/入口/断链三态）。真源=TDM+night_totalflow_chief 先前骨架+total_circulation_night+alignment_checklist+GOMAP+ROOR。
- **S3 逐环节挖矿**：每环节一档（六向台账：上游/下游/消费/生产/自动化/运行态 + 自审闸三态：挖干/存疑/盲区）。产出 `skeleton/<seg>/<link>.md`。挖干即封矿。
- **S4 施工批**：封矿即开工（内收原则：同真源必并/零消费退役/同域收敛唯一/跨域不并）。断链接线、薄模块、死代码退役，全部走 claim+gateway。
- **S5 灌水批**：数据管道盘点→断供修复→烟测（国庆假期数据源静默，只验证可运行+登记缺口，不强行补历史）。
- **S6 脏面清零**：untracked 277 + unstaged 84 逐件三态裁决（落地/归档/废弃），落地走袋，归档移 .runtime/tmp/campaign_trash，废弃 blob 封存。
- **S7 循环检查**：全员施工完后统一验收，问题即修，连续两轮零才算过。
- **S8 红蓝对抗**：红蓝向量打全场（含门禁负样本、重放对拍、端到端烟测），发现即修。
- **S9 收尾**：claim 全释放→临时文件清理→作战书+挖矿册 promote→终报→记忆。

## 3. 验收判据（S7/S8 通过线）

1. `git status` 三桶：staged=0（除 belt 在飞）、unstaged 仅剩友军活面、untracked=0（或仅 .gitignore 政策件且有裁定）。
2. 队列：无 dead 新增（存量死袋全部处置销账）、pending/processing=0。
3. 锁=0、孤儿 claim=0（fullscore 例外复核）。
4. 骨架册：环节全部封矿（三态=挖干），P0 断链修复或登记待裁。
5. 测试：触达面 pytest 全绿两轮 + 红蓝对抗零未修。
6. 无临时文件残留于项目根/scripts；campaign 文档齐备可检索。

## 4. 台账纪律

- 总账 `LEDGER.md`：每动作一行（时间/车道/动作/证据锚）。
- 裁定簿 `rulings.md`：本战役自裁全部登记（终局并入 ruling_registry，取号先查册）。
- 交接保障：本文件+LEDGER 即断点续作真源，任何会话可从 §2 顺序接手。
