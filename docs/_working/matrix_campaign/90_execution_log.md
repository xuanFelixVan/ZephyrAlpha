---
campaign: matrix-20261006
session: st-matrix-20261006
owner_directive: 家底全接线·矩阵考试总包+批0-5全量考试（Owner 就寝授权：全程不问不停，自裁留痕，四门位只登记）
created: 2026-10-06
ttl: task_bound
---

# 90 — 矩阵战役执行台账（st-matrix-20261006）

> 总包=本会话。车道：S骨架挖矿｜M1另类源线挖矿｜M2离场板块挖矿｜E考试执行｜C施工登记｜R修路。
> 纪律：机生禁手填｜HOLDOUT选样窗与考试窗分离｜负结果如实入册｜他队面零触碰｜四门位只登记。

## 时间线

| 时点(UTC+8) | 事件 |
|---|---|
| 03:12 | 冷启动六步全绿（Python 3.12.8/usercustomize/reaper在岗/会话注册/心跳分离/reaper_keep登记fexam_run+run_fexam） |
| 03:15 | 战役目录建立 docs/_working/matrix_campaign/ + docs/_working/fexam/；claim=reaper_keep |
| 03:16 | **token先行**：18枚新文件token经意图API正道入账（register→publish_snapshot v58→render，capabilities 391零损） |
| 03:17 | S/M1/M2 三路挖矿代理并发发车 |
| 03:20-03:55 | E车道基建8件写成（scripts/backtest/fexam/）+selftest |
| 03:4x | S车道归队：22文件，TDM 182/182+SPM 341/341对平，新矛盾4项登记 |
| 03:5x | M1归队：30源线零遗漏（9可挖+21负结果）；M2归队：42节点零遗漏（S3/M28/L11） |
| 04:0x | 批0 roster机生：因子175/指标143/策略161/分配器5（施工单旧数175/139对平漂移如实记录） |
| 04:0x-04:3x | 批3五发迭代修障（CH代理劫持→period列误设→TSV无表头→三段式切分→judge指标判据分离→regime重复快照去重）+快路径秩IC（与内核逐位对拍<1e-6） |
| 04:3x | 批1因子考落册：175全部rework（册面量化欠账如实暴露）；批2策略考落册：161全部rework+DSR记账（n_trial cumulative 20632） |
| 04:4x | R车道：fac9_05修复计划册（两处名实错位处方+骨架新矛盾4项；地图族fig13-bone持锁→只开方不动刀） |
| 04:5x | 治理三件套：翻译册8条（claim持册）+depgraph设计节点×2（目录级+CLI文件级） |

## 车道交付清单

- **S骨架**：`mining/00_stage_skeleton.md`+st_*子册10+9族+`99_skeleton_selfcheck.md`（22文件）
- **M1另类**：`mining/m1_alt_sources/`00索引+9规格卡+99负结果（11文件）
- **M2离场板块**：`mining/m2_exit_sector/`00索引+13X卡+13L2卡+99负结果（28文件）
- **E考试**：`docs/_working/fexam/`bt_p0_roster_v1+factor/strategy/indicator三分数册+allocator影子报告+00总册（批3/4/5推进中）
- **R修路**：`fac9_05_drift_repair_plan.md`
- **总表**：`data/strategy_intake/matrix_inventory.yaml`+`matrix_gap_lists_v1.yaml`（机生）
- **原问题**：`metaq_matching_v1.yaml`（对照表模式，回填留Owner）

## 关键自裁记录（客观架构师口径，第一性原理）

1. **因子册175实测仅18条有outputs、2条quantized、列直连=0** → 批1全部rework是诚实结果（禁造凑数因子）。处置：31个code_symbol锚点属M级逐因子适配器工程，登记施工队列不夜战。
2. **策略册161实测alpha_sources非空仅2条**（且指向文本规则因子）、code_path=23 → 批2标准化harness无可实例化对象，全部rework。处置：23个code_backed策略逐策略适配器=M级登记；T1/T2冠军配方考试通道（factory_grid_executor）不受影响，那是配方域考试非册内策略考试。
3. **实测面收敛到指标册143列全量考+批4分配器五套影子**——指标列真源=c1_market.technical_indicator（4.03亿行，HOLDOUT窗覆盖✓）。
4. **批2引擎选型**：DefaultBacktestEngine(MOD-BT-001) CPU逐日（vectorized_engine无cupy核；0.53s/格口径属c4网格引擎T3a专用，单跑不适用）——degrade台账随册逐条可解释。
5. **修路车道只开方不动刀**：地图族正被st-fig13-bone在册演化（path_ownership_map实测持锁），按宪法§3.4他队在途不代修。
6. **regime快照同日多行**：drop_duplicates取末笔（最新检测态，PIT口径），已修+单测绿。
7. **mining代理产物的token**：代理只写文件不持账本，总包收割时统一补token后提交（CREATE-GUARD在commit时点校验）。

## 障碍与修复（跑批五发全记录）

| 发 | 症状 | 根因 | 修复 |
|---|------|------|------|
| 1 | HTTP 404 | Windows系统代理劫持urllib内网POST | ProxyHandler({})直连 |
| 2 | 404 Code:47 | kline_daily_hfq无period列却按period过滤 | table_columns探测按需加period条件 |
| 3 | KeyError trade_date | FORMAT TSV无表头被read_csv当表头吃掉 | header=None+位置列名协议 |
| 4 | judge KeyError abs_ic_min | 指标批与因子批判据语义不同却共用judge | judge_indicator独立（|IC_5d|+覆盖，负IC=反向可用） |
| 5 | duplicate labels reindex | regime_snapshot_history同日多run_id快照 | drop_duplicates(keep=last) |
| - | 快路径与内核IC偏差0.05 | NaN模式不一致时各自秩变换分母集不同 | 联合有效掩码先裁剪再秩变换+对拍单测锁定 |

## 提交与队列（终版）

- 直连通道三度受阻后切**队列正道**：共享暂存区躺着他队数千条 AD 幻影，gateway `_sweep_phantom_staged_adds` 全量 `git reset` 爆 WinError 206（环境性，非本役文件问题）→ serializer 队列免疫。
- 已入队：q-0001（代码+测试+capability册+translation册 14 件）、q-0002（**capability 册 token 先行批** 1 件，commitmap playbook 铁律）、前方 ~98 袋多队夜战排队，FIFO 自动消化。
- 排队中待入队：袋2a（战役文档 64 件）/袋2b（四册+总表+trial_ledger）——等 q-0002 落地（CREATE-GUARD 落地读 HEAD）后入队；袋3（批4 册+总册+终报+台账更新）随批4 收官。
- 落地时若 q-0001 先于 q-0002 死于 CREATE-GUARD → 走设计内死信 `commit_queue.py requeue` 自愈（FIFO 尾，落在 q-0002 之后）。
- 死会话处置实证：fig16 对翻译册的网关 claim（快照 6h 未动+心跳 1h 停摆）按宪法§2.7 `release_files` 精准释放后重 claim 成功。

## 循环检查与红蓝（05:4x）

- 红蓝对抗（新自动化六路攻击）：R1 NaN面板/R2 单票截面/R3 重复日期/R4 ckpt污染/R5 prereg篡改/R6 CH错误体注入——**6/6 BLUE-HOLD**（fail-closed 全防住；脚本 .runtime/tmp/st-matrix-20261006/redblue_fexam.py）。
- 循环检查#1：tests/backtest/fexam 19/19 绿 ×多轮；DSR/覆盖册域 59/60——唯一失败=**covledger 队的 backtest_coverage_ledger.yaml 三真源漂移**（02:23 生成后他队面继续演化，宪法§3.4 他队在途不代修，观察登记）。
- ruff 全清零；selftest 6/6 断言绿（含快路径与官方 IC 内核逐位对拍）。

## 热册并集战役（06:0x-07:0x，capability 册三宇宙合一）

- **病根**：capability 册真源分裂成两宇宙——PG 账本（意图API阵营：本役 83 token）vs git HEAD（直落阵营：capcov 等队三方合并只进 git 不进 PG）。双方渲染/合并互相覆盖对方条目。
- **死信三连**：q-0001 死于关键词判重（波13 泛词误判，官方逃生标记 `# create-guard-not-dup:` 八模块已打）；q-0002 死于 cascade_stale（122 袋深 FIFO 位次+热册每小时被推进=结构性死循环，capcov lap3 同款）；重投再死于 REGISTRY-MASS-DELETION（工作区落后 HEAD 14 条身份）。
- **治本手术**：字符串级外科追加（非整文件 re-dump——CAS 行级比对会拒语义纯追加）——HEAD 独有 14 条以原样式拼进 tokens 列表尾，条目身份归零消失，双侧归一（capcov=1 + fexam=1）。
- **在队**：q-0003（requeue 重建）+ q-0004（新鲜快照）双 capability 袋排队；任一落地即 token 进 HEAD → 解锁袋1 重投（not-dup 标记已修）与袋2a/2b 入队。死信→requeue 自愈链已演练全程。
- **capcov lap3 教科书**（他们的提交信息=最佳实践文档）：热册袋 `--base-head <真哈希> + --priority 5` 快速出队压缩漂移窗（commit_queue.py enqueue 原生支持；git_commit.py 包装器无 priority 透传）。

## 待Owner/后续批（登记不代裁）


- 及格线初拟全部待Owner校（prereg_v1内标注：IC>0.02/ICIR>0.3/retain>=0.5；策略OOS Sharpe>0+MDD<=30%）
- 31因子code_symbol适配器（M级）｜23策略code适配器（M级）｜T3a开闸考（与st-tclose-t3a车道握手后）｜T1冠军域复考5千格（晋升池36388958b3d8）
- R1/R2名实错位定谳（fac9_05处方）｜S1-S4骨架新矛盾（同册§二）
- 原问题回填（对照表模式；writeback API需认领链，留Owner过目批）
- metaq min_confidence=95 post_hoc_amendment（T-1待裁项，本战役未动）


## 收官补记（终版）

- 批4 五套全部实测（numpy 感知 Dumper 重跑版）：三层栈 OOS Sharpe +0.52 领跑，证据量 t=0.35~0.48 不足判终胜负（MOD-PF-008 纪律）；批1 因子 0 可考→批4 合成信号按 prereg 回退指标列（册内如实标注）。批4 首跑死于 np.float64 yaml 渲染（三小时计算蒸发教训）→ 根治补丁袋4 + 重跑通道临时包装双保险。
- 队列落袋全序列：q-0003 capability 册 HEAD 归一 → q-0006 翻译册 → q-0007 代码袋重投 → q-0008 np修复 → q-0009/0010 战役文档 → q-0011 册+总表 → 袋3 收口（本册+终报+批4/5 产物）。死信自愈链全程演练：CREATE-GUARD 关键词判重（not-dup 标记）/cascade_stale/TAKEOVER-PENDING（活体声明）/TTL 缺失（26+35 文件补 frontmatter，9 卡补闭合 ---，A15 裸 URL 引号）——每一门的处方都已留痕。
- 接管误判：心跳守护 01:25 停摆 → TAKEOVER-PENDING 咬住本会话 → 重拉守护 + session_takeover_ledger --resolve 活体声明，恢复。
- 质量终态：循环检查×2 连续零未决（fexam 19 测试+DSR 域 59/60 唯一红=covledger 他队在途面）+红蓝 6/6+ruff 零+selftest 6/6。
