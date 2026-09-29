---
ttl: task_bound
---

# 叶簿 W-61 · T1 成绩单定稿（3698 有效 + 2 可审计阴性）→ T2 选优

> 族 6（考试与搜索链 GPU/T1/T2）· 骨架行锚=`00_master_skeleton.md` L121（态 🌑，出处「裁决归总令 裁2」，案卷 E）
> 编译：2026-09-28，会话 st-zcloseout-20260928（Agent-H），lane HEAD=`325b69a193`。
> 状态标记：🌑 Owner 门位（成绩单"定稿"=三项 blocking 的追认/改判，AI 不代裁）；哨兵与其测试**已落地**（本会话复读，见 M1）。
> **✅ Owner 定稿 2026-09-30**：Owner 2026-09-30 批复"终局交付战役 Owner 门位清单按总筹建议逐项执行"，其中 T1 定稿拍板按总筹建议（99_owner_gate #4"只差 Owner 签"，3700 格 manifest 全 pass、计数前置已消化）签付——本叶簿 🌑 定稿门位就此闭合，定稿登记=裁定#431 第⑦项（ruling_registry.yaml）。后续 T2 选优发车（前置 W-64/W-65）按工单推进，不在本批。
> 素材真源：`dossier_E_gpu_t1_t2.md` 主表 1a-1e、§B/§C/§D、追加批 2 条 5a-5e/6a-6c、收尾 1-6。

## 1. 六向台账（对象=`data/strategy_intake/grid_20260926-024947/` 成绩单的定稿面）

| 向 | 内容 | 锚 |
|---|---|---|
| 上游供数 | T1 全量粗扫产物 5 件：manifest.csv(2,239,062B)、net_returns.parquet(54,377,088B)、negatives.csv(971B)、summary.json、handover_verdict.yaml(9,881B) | dossier_E §一 1a |
| 下游消费 | T2 选优/发车（`build_t2_subspace()` 哨兵 L630；选层规则=`AUTO_t1_t2_handover.md` §四）；T2 认领位=`t2_handover_claim.yaml`（L216 幂等位） | dossier_E 追加批 3 条 10a/10b |
| 名册声明 | 判据真源=冻结件 `config/search_space_prereg.yaml`（tier1_points: 3700 :60 / tier2_points: 900 :61 / cost_gate_in_every_tier: true :62）+ `config/exam_scale_cost_gate.yaml`（tiers_bp [0,5,10,20,40] :11 / survival_floor 0.0 :13 / monotonic_tol 1e-09 :15）；17 号文 `17_quantified_acceptance.md` §一 L15-24 五判据 | dossier_E 追加批 2 条 9b/5b |
| 读声明的代码 | 哨兵 `scripts/backtest/t1_t2_handover.py`：verdict 逻辑+blocking_criteria 三件（manifest_points/dead_zero/cost_gate_spot）+阴格哨兵式 `insufficient_net` | dossier_E §B/追加批 2 条 6b（factory_grid_executor.py:793-795） |
| 覆盖测试 | `tests/backtest/test_t1_t2_handover.py`（史基线未跟踪 14,329B） | dossier_E 追加批 4 条 1f；本会话复读=**IN-HEAD**（M1） |
| 执法门禁 | verdict 自判 `all_green: false` 即发车阻断；成本门抽查由 blocking_criteria 闸死 | dossier_E §B（`all_green: false`，本会话复读 L93 同值） |

## 2. 现状实测（史基线 → 本会话 HEAD=`325b69a193`/盘面复读）

| # | 断言 | 史基线（锚=dossier_E） | 本会话复读 |
|---|---|---|---|
| M1 | 哨兵落地态 | 2a/2b：`scripts/backtest/t1_t2_handover.py` 在 index 不在 HEAD（`AM`）；测试件未跟踪（`??`） | ✅ **两者均已 IN-HEAD**（`git cat-file -e HEAD:scripts/backtest/t1_t2_handover.py` 与 `tests/backtest/test_t1_t2_handover.py` 均命中）——骨架 W-62（t1_t2_handover 哨兵落地）面已闭合，本叶簿只管 W-61 定稿面 |
| M2 | 成绩单规模 | 1b：manifest 3699 行=3698 数据格；summary evaluated=3698/eval_dead=0/backtest_dead=2；negatives 恰 2 行 | dossier_E §一 1b（产物只读，未复读数值面） |
| M3 | verdict 三 blocking | §B：`all_green: false`，blocking=[manifest_points, dead_zero, cost_gate_spot]；manifest_points false（3698 vs ==3700±0）；dead_zero false（backtest_dead=2）；cost_gate_spot false（sampled=50, ok=22 → 56% 坏，`source: replay`） | dossier_E §B + **本会话复读 `handover_verdict.yaml:93 all_green: false`**（产物未变） |
| M4 | 同文件分母自相矛盾 | §B 末：manifest_points 判 false 用「==3700」，negatives_discipline 判 true 用「manifest+negatives==3700」——两处不同分母 | dossier_E §B（定稿时必须二择一，AI 不代裁） |
| M5 | 成本门口径 vs 17 号文 | 5a/5b：17 号文 L20 原文「抽查 ≥50 格五档全真跑」**无**「幸存者分层抽」限定（该语在 LEDGER:72 自标"解释性澄清"）；verdict 抽查走 `source: replay` 重放腿≠「真跑」字面 | dossier_E 追加批 2 条 5a/5b + §D（40bp 档 top10 全负 sharpe） |
| M6 | 33%/56% 可复算 | 5c/5d：33%=grid_20260924-080309 manifest 66/200 sharpe≤0（min −4.7830 逐位吻合）；56%=verdict 28/50 | dossier_E 追加批 2 条 5c/5d |
| M7 | 两阴格 | §C/6a/6b：d6759a48a594/4bdf3555a27d，死因 `insufficient_net:1622`——哨兵把 dropna<60 与 std==0 两分支合并打印 len(net)（=全窗 1622 日），**零方差结论不可直读**；「同配方旧引擎同死」无同窗对拍件（6c 判「不」：旧窗现场评出 sharpe=−0.153 存活负） | dossier_E §C + 追加批 2 条 6a-6c |
| M8 | T2 面 | 10a/10b：无 T2 目录、无 subspace JSON、无 claim 件；晋级池构造产物面为空 | dossier_E 追加批 3 条 10a/10b（本会话未复读，IO 纪律；定稿前须复跑 §5 命令组） |

## 3. 缺口与根因（转述）

- 「完赛」≠「全绿」：3,698/3,700+2 阴性属实、垃圾三线绿，但三项 blocking 红（M3）——定稿=对三项各作追认/改判/复跑的 Owner 裁（骨架 🌑）。
- 抽查口径裂缝：17 号文要求「五档全真跑」，现役产物只有重放腿且**所有已跑产物无 manifest cost 列**（dossier_E 缺口 4/AUTO §七.3 prereg 缺 `cost_gate_t1_tiers_bp`）——56% 坏的档位归属只能靠重放件读。
- 复杂度门拦截史：哨兵曾因自身 cc=52（run_acceptance）被 COMPLEXITY-GUARD 拦（追加批 2 条 2c/2d：「52 层嵌套」口径错，实为圈复杂度；最大嵌套深仅 5）——现已入 HEAD（M1），说明该拦点已解，解法未在锚面（施工班如需同路径先例，读该件 git log）。

## 4. 施工项（带锚）

1. 三 blocking 逐项定稿呈裁包：manifest_points 分母二择一（M4）、dead_zero 两阴格定性（M7：insufficient_net 分支不可分辨→须补探针或改哨兵日志）、cost_gate_spot 真跑 vs 重放（M5）——出处=dossier_E §B/收尾 4-5。
2. 成本列补齐前置：prereg 补 `cost_gate_t1_tiers_bp` 后重跑才有 17 号文要求的 manifest cost 列（dossier_E 缺口 4）；prereg 改动=冻结件重签，联动 W-65（方案① prereg 重签，骨架 L125）。
3. 定稿后 T2 选优发车：tier2_points=900 现役（M8 无产物），W-64（晋级池基落主区，骨架 L124）为其前置。

## 5. 复验命令（可重跑）

```bash
cd /d/ZephyrAlpha/.worktrees/st-zcloseout-leaves
git cat-file -e HEAD:scripts/backtest/t1_t2_handover.py && echo sentinel-IN-HEAD
git cat-file -e HEAD:tests/backtest/test_t1_t2_handover.py && echo test-IN-HEAD
grep -n "all_green\|blocking_criteria" /d/ZephyrAlpha/data/strategy_intake/grid_20260926-024947/handover_verdict.yaml | head -4
# 期望（本会话读数）：两件 IN-HEAD；all_green: false。若 all_green 变 true 或产物被重写，M3 失效须按 dossier_E §B 重挖
```

## 6. 自审闸三态

- **挖干**：已干——产物面（M2）、判据面（§1 名册向+M5）、verdict 面（M3/M4）、阴格面（M7）、T2 面（M8）、落地态（M1 本会话复读）六向齐锚；「114 测试绿整体未验/等价对拍未复算」两条未挖项在 dossier_E 缺口 1-3 显式在册（属 W-62/W-38 相邻面，不在本叶簿扩）。
- **施工中**：哨兵+测试已落 HEAD（M1）；三项 blocking 的定稿材料备齐（M3-M7）。
- **未开工**：定稿裁定与 T2 发车——证据=handover_verdict.yaml `all_green: false` 本会话在读 + 🌑 门位（骨架 L121）。
