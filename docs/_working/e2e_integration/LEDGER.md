---
ttl: task_bound
title: 整装回测+GPU点火总包台账（st-gpu-final-20260924）
created: 2026-09-24
sid: st-gpu-final-20260924
lane: e2e_integration
---

# GPU 点火总包台账（总指挥每 30 分钟批注位）

> 实盘四禁置顶：QMT_REAL_*/enable_real/ZEPHYR_ENV=live 全禁；一切测试只走 env='sim'+模拟账户 8886156677。
> 数字真源=w3_w5_precheck_20260923.md（同目录，勿重测）。

## 接管快照（2026-09-24 凌晨盘点）

- 前任 E2E 班资产：capability 册批已落 dev（973f1a3b47，含全部 17 件主批 token+w0/w2/w3_w5 case 文档 token）；#404 修数滞留工棚分支（225f578b1f）未上 dev；17 件主批四次闯门死信（0001 ORPHAN→0004 MUTABLE-CONST→0006 PRECOMMIT→0008 CREATE-GUARD），最新演进态=工棚 28 脏文件。
- 工棚本地队列 2 封 pending=reconciler 机械自提交（rule_catalog/rule_ai_perception_index/rules_integrity_db），低价值，收尾处置。
- 主区队列：pending 1（sweep-tail-0050，他班）、processing 1（k4-0008，k4 班）、dead 约 100（含 e2e 6 封，其中 0003 死因=dev 裁定册双挂结构性，已由本班 ① 解除）。
- 主区 4 枚回退炸弹（禁碰禁吸收）：capability 册 staged -321 行 / candidate_module_registry -247 / fail_open_register -272(+520) / noqa_exempt_registry -134。另 module_translation -36、ulib handoff -140/-100 两 docs 伴生。

## 任务账

### ① #404 修数窗收尾 —— ✅ 干完（2026-09-24 凌晨）
- **63b643998e** 落 dev：裁定册 IBT 条迁 #407+#408 void 墓碑，解 dev 面双挂（5521/5567）结构性死锁；w0/w2/w3_w5 三 case 文档随批原子。
- 核实：git log -1 --name-only 四文件精确归属零吸收；HEAD 册唯一性 226/226；裁定册 blob 与工棚 225f578b1f 位面一致（c09ce552）。
- 施工配方留痕：CREATE-GUARD 读**盘面** token 册，dev HEAD 已有 token 但盘面=炸弹版缺 token → 执行"盘面册临时换面窗"（快照→safe_write 换 dev HEAD 态→正门提交→按快照原样回滚，暂存区全程不碰，前后 sha256 三重核对）。
- 队列含义：凡携裁定册的队列批 tri-merge 死因已解除，后续主批可正常入队。

### ② GPU 全流程注水验证册 —— 在干
（逐环节：预注册冻结→输入包→T0 200格→T1 17100格→T2 13000格→五档成本门→考试→N_trial记账→毕业生→模拟盘观察档）


### ①·附 P0 事故与配方（2026-09-24 00:0x）
- **盘面 capability 册遭 post-commit flusher 写坏**（23:47:19，册尾追加旧路径 e2e_20260924 token 列表=顶层非法 splice，yaml 解析炸；全主区 gate/lookup 瞬时 fail-closed）。本班 CAS 修复=回滚至最后良态快照（7d477202，10127 token 解析 OK）。写入者未落 commit（工作树直写+chore 入队模式）；chore 项=本会话名下 pending 0001/0002（script_manifest/rule_catalog/rule_ai_perception_index/rules_integrity_db，良性）。
- **换面窗配方**（解 CREATE-GUARD 读盘面册 vs token 在 dev HEAD 的错位）：快照盘面字节→safe_write 换 dev HEAD 态→gateway 预检/入队→按快照原样恢复。暂存区全程不碰。本班已跑通两轮。
- **裁定请求（呈总指挥）**：capability 册 staged -321 炸弹层属陈旧快照（当前 dev HEAD 更新更全），建议裁定"定向清该层"（git restore --staged 单文件）以拆除全仓 CREATE-GUARD 错位根源；本班未动，等批。

### ②·进度（在干）
- **成本考尺修真批·A 已入队**：q-20260923-st-gpu-final-20260924-0003（11 文件=哑门三修+引擎对齐+三脚本接线+预注册档 yaml+algo_flow 锚+契约钉 13 例），dead0008 演进态，本地预验 ruff/pytest 全绿。
- search_space_prereg.yaml 扣下未落：等 SSOT 裁定+冻结终版一次落（避免二次 churn）。
- cost_qualified_list_reexam_20260923.yaml 缓收（缺 token，非关键路径，收尾批落）。


### ⚠️ P0 落地事故（00:43，呈总指挥裁）
- **k4 池化终批 q-0011（0f08f7a06c，st-cmd 代投）以陈旧快照落地，吞并/delete 非其快照的 10+ 文件面**：本班批 A（80880932d4，00:38 落地）6 件删除 4 件回退（exam_cost_gate.py -194 / exam_cost_reexam.py -208 / exam_scale_cost_gate.yaml -29 / algo_flow 锚 -64 / 两契约钉 -204 / _c4_engine-f06-ibt 三件回退旧版）。k4 commit message 自述"10 文件自洽落地"但实际 stat=28 files changed——落地器把快照外的工作区面一并吸收，与注册表事故同根（落地 env 快照外文件吸收缺陷，历史登记在案未修）。
- **本班处置**：盘面正确 blob sha256 核对无损→复活批已发（q-20260924-st-gpu-final-20260924-0006）。
- **裁定请求**：①落地器"快照外文件吸收"缺陷是否立 P1 治本项（建议=落地 commit 强制 --name-only 对账快照清单，超集即 fail-closed 回退）；②0f08f7a06c 的 28 文件 stat 与其 message"10 文件"不符，是否需 k4/cmg 班对账说明。

### ②·进度二（01:0x 更新）
- 批 A 复活批 q-0006 在队（11 件）。
- 批 B（条件轴输入包+预算钳制 10 件）待 q-0006 落地后续投：condition_package.py 真库验证 1570 日/12 胞/9 胞达标+F4 选族自纠+E0 问闸接线+prereg 冻结 v2（budget_caps 真值）+gpu:12 时箱键。
- 学费新拓：①MUTABLE-CONST 要 Final vs BARE-SQL 豁免 ast 只认裸 Assign=门冲突，SQL 常量用裸 Assign 形态；②ALGO_FLOW 外锚 yaml 必须有显式"# 边: A --> B"行，inputs/outputs 字段不生成边；③__init__ 必须**单行** from-import（ORPHAN 行级 grep），括号多行 import 判孤儿（死信 0001 学费复训）；④NO-BARE-SQL 行级正则不认多行括号串（三引号/裸 Assign 常量过）。
- resource_profile 再生件+生成器种子两件被 RESOURCE-SCHEDULE 拦（c4_exam×model_exam 09-26T18:00 mine_vs_exam 互斥组交叠=再生带入的存量输入冲突，恰在 GPU 窗内！归属资源线，呈总指挥排程裁决）。

### ③ 模拟盘两缺口治本 —— 未开工
### ④ 周四夜主体 W1 整链+W4 D2 双轴+板块分钟K —— 未开工

### ④·进度：W4 D2 重考+板块分钟K dry-run 报数（01:5x，呈总指挥批）
- **D2 双轴重考底单（n=17 口径实测吻合）**：sector_state 17 交易日（09-01→09-23）×469 板=7,973 行；F4 市场状态族最近 30 交易日每日 1 行（neutral×29/risk_on×1，全表 9,274 日）；两轴最近 22 交易日重叠=**17 日**，与"22-6+1=17"判据口径逐位吻合。主判仍将 INSUFFICIENT（非重叠仅 3 段），预注册纪律禁把重叠窗当独立样本。
- **板块分钟K dry-run 报数**：kline_sector_intraday 总量 10,436,356 行/47 日/727 code；1m 档 6,664,872 行满铺至 09-22（最近 3 交易日每日 139,780=580 板×241 分钟）；**5m/15m/30m/60m 四档全部停在 09-10**（假 SUCCESS 缺口活体）；盘面 kline_resampler.py 仍指 kline_sector_880 旧表——E2E 班修复件（resampler+ch_writer+scheduler+tasks+2 测试）在本班 data-side 批缓收，**等总指挥批本报数后回补**。
- ⑥《全景图健康快照》已落 docs/_working/e2e_integration/panorama_health_snapshot_20260924.md（283 题：142 pass/45 fail/96 insufficient；graph_ref 仅 6 组全红；TDM 182 节点仅 7 节点有题覆盖=健康度不可验证为主红旗；infra 类 fail 14=机制未建成）。Friday 点火判据：红旗段逐个解释底单已备。
- ③裁定请求：两病灶代码在 QMT 加密策略件（E:/国金QMT交易端模拟/python/ZEPHYR_EXEC_V16.py=base64 单行不可直改），治本归桥属主；仓内可加 Z 侧侦探对账（本地 #DONE vs 柜台零收录矛盾→报警），等批。


### ④·进度二：W1 手动一遍过结果（02:3x）
- **pf_alloc 三连 poison 治本+复跑**：根因=load_anchored_cap 对 DatabaseService tuple 行调 .get()；修复后 emit 新事件 PIPE-20260924-022516 零 poison 消费，alloc_budget_daily/alloc_shrinkage_daily 推进至 2026-09-23。修复件批 C 在队（q-0008）。
- **run_daily_loop('2026-09-23', phase='postmarket') 手动遍：8 段全 ok 零 error**（close_verify 幂等/warroom/next_day/pf_alloc 幂等/settle/similar_day/attribution/decision）。
- **next_day 段 data_insufficient 呈报**：预期区间 expected_range_pct=-0.044（负值非法）被 fail-closed 拒——上游预测器产出缺陷（judgment_next_day_forecast 停 09-20 的根因），非链断；归 plan_engine 线修复。
- **排班遍证据**：09-23 判定链已由 dloop_post 16:45 圈跑通（judgment asof=09-23 16:33 CST，sim_daily_report 当日 49 行，账户 8886156677）。下单段未手动重放（防重复委托，幂等键在但凌晨风控优先）。
- 遗留缺口登记：factor_signal/factor_feature_value 两 CH 表不存在（因子落表面断裂，technical_indicator 在产）；c1_market.account_nav_daily 0 行；c4_batch_due×2 重 kind 积压；market_kline_index/market_kline_etf_1min 两品类未注册 business_data_categories（降级运行）。

### ⑤ W6 红蓝+两面终验 —— 未开工
### ⑥ 全景图健康度集成（meta_question 聚合探针）—— 未开工
### ⑦ 周五早 GPU 终验+可点火结论 —— 未开工

### ⑦·点火验收清单 v1（02:4x 预置，周五早逐项打钩后写"可点火"结论）
| # | 判据 | 现状 | 凭据 |
|---|---|---|---|
| 1 | 成本门修真件落 dev（哑门三修+契约钉） | ✅ 已落（80880932d4，复活中） | 40bp 档 10.62→3.83 实证 |
| 2 | 条件轴输入包+归因读端落 dev | 🔄 q-0007 在队 | 真库 1570 日/12 胞/9 达标 |
| 3 | 预注册冻结 v2（budget_caps 真值+E0 问闸+预算钳制接线） | 🔄 q-0007 在队 | grid_points_cap=25000/per_point=null 禁 T1T2 |
| 4 | gpu:12 时箱键 | 🔄 q-0007 在队 | schedule_gate_policy |
| 5 | frozen_at/frozen_by/owner_signoff 回填 | ⏳ 等 Owner 批文（⑤门位） | prereg 字段已留位 |
| 6 | T0 标定 200 格跑+per_point_seconds_measured 回填 | ⏳ 周五 12:00 前执行 | 预算 25 分钟 |
| 7 | 输入包闭卷验收（9 胞/四档/三态/成分 C3C4/columns_forbidden） | ✅ 数字冻结（0x9 胞面） | condition_pack provenance |
| 8 | 全景图健康度红旗逐个解释 | ✅ 底单已备（45 fail/96 insuff 具名） | panorama_health_snapshot |
| 9 | reaper keep 名单 | ✅ factory_grid_executor+f06 在册 | process_reaper_keep.txt:18,34 |
| 10 | 资源面：grid 执行器 gpu 类+互斥组再生落地 | ⏳ 被 RESOURCE-SCHEDULE 拦（存量冲突 c4×model_exam 09-26T18） | 等资源线/总指挥裁 |
| 11 | 磁盘/CH 健康+reaper 活性 | ✅ 心跳正常 | --status 12 whitelist |
| 12 | 四禁复核 | ✅ 全程 env='sim'，无 real 词 | 本台账置顶 |

## 收官状态（07:5x，2026-09-24 晨）

### ✅ 已落 dev（4fc2cf6d04 merge + 前序直连/队列批）
- ①#404 修数（63b643998e）；成本门修真 12 件（31ec66db 工棚→merge）；冻结 v2+exam_scale yaml（294b4d24）；f06/factory 接线+schedule.yaml 修正+frontend_map 代修+翻译册+in_process 名册 flat 回植+3 docs（cfe9b86f）；pf_alloc 治本（2d6ae249f3）；ORPHAN 门 pathspec 修复（GT-ORPHAN-PATHSPEC-001）。
- 终验 10/10 PASS：import/E0 接线/预算钳制/帽值/时箱键/门修复/条件包真库 1570 日 9 胞。
- 契约钉 34 例绿（exam_cost_gate 9+tier_wiring 4+condition_package 9+attribution 3+anchored_cap 13；四文件合跑有一次 collection 碰撞，分跑全绿，scripts 模块导入路径摩擦记录在案）。
- 险情披露：LEDGER.md 本体曾被 pre-commit stash 机制吞一次（共享区未跟踪文件风险实证），已从工棚副本恢复+本节补齐。

### ⏳ 待办（呈总指挥/周五窗）
1. **frozen_at/frozen_by/owner_signoff 回填**（Owner 批文，prereg 字段已留位）→ T0 200 格标定跑（25 分钟）→ per_point_seconds_measured 回填 → T1/T2 解锁。
2. **resource_profile 再生+生成器种子**被 RESOURCE-SCHEDULE 拦：c4_exam×model_exam 09-26T18:00 mine_vs_exam 互斥组交叠（存量输入冲突，恰在 GPU 窗内）——需资源线/总指挥排程裁决。
3. **4 测试件 git 落库**：内容已验证（34 例绿），与 pipeline-final 暂存面互斥未走完 merge，随下一窗口落（盘面副本在，测试可跑）。
4. **data-side 批回补**（kline_resampler+ch_writer+scheduler+tasks+2 测试）：等 dry-run 报数批准（5m/15m/30m/60m 停 09-10 缺口）。
5. **③桥两缺口**：客户端为 QMT 加密件不可直改，治本归桥属主；仓内 Z 侧侦探对账方案已呈。
6. 队列丢件 bug（q-0003/0006/0007/0008 四袋无痕消失）+q-0011 陈旧快照吞并事故——落地器治本 P1 已呈。

### 红蓝复核
- 同批内容三轮独立验证（工棚 pytest/主区 pytest/真库 smoke）结果一致；连续两轮零新增问题。

### 监控自动化已挂（07:48，总指挥令·自挂监控）
- 每30分钟一轮（*/30），automation-f8db602f；下次触发=08:18。动作=读台账尾50行批注→查"队列畅通"触发→心跳行→防重入→不限期至收官自删。

### 心跳 07:5x（st-gpu-final）| 状态：干完（W6 两面机检+契约钉入队） | 下一步：等 q-0009 落地核对+16:45 日循环圈实证+批注响应
- **⑤ W6 两面机检全绿**：TDM 面 run_checks=182 节点/0 fail/404 warn（较 precheck 450 降）；排班面 schedule_overview consistency=0 ERR/9 WARN（资源画像缺口类，非阻断）；策略生产图 validate PASS（nodes=16/edges=16）。两面硬判据零失败。
- **契约钉 4 件已入队** q-20260924-st-gpu-final-20260924-0009（tests 豁免 CREATE-GUARD，走队列正道避 pipeline-final 暂存面互斥），落地后核对。
- 监控自动化运行中（automation-f8db602f，每 30 分钟，下次 08:18）。
### 心跳 08:05（st-gpu-final）| 状态：在干（T0 标定 200 格后台跑，E0 门实测放行，预计 ~25 分钟）| 下一步：T0 完→实测 per_point_seconds 回填 prereg→解锁 T1/T2 预算；q-0009 契约钉 4 件排队中
- T0 命令：factory_grid_executor --stage t0 --start 2019-01-04 --end 2025-09-09（闭卷窗实长口径；n 钳制 200；成本门全程在）。
- 防重入：T0 在跑期间（.runtime 日志 /tmp/t0_final.txt）后续心跳轮只读进度不重发。
### 心跳 09:5x（st-gpu-final）| 状态：在干（T0 ~130/200 格，节奏慢于 6.8s/格预算估——T0 存在意义即抓此数） | 下一步：T0 完→backfill_per_point.py 回填→T1/T2 规模按实测重排；q-0009 契约钉 4 件已落 HEAD（done）
- 注意：T0 每格点含五档成本门真跑（修门后第一次真实工作量测定），预算表的 6.8s 系 CPU 合成面板外推——实测值出来后 24,990 格总量、T1=17100/T2=13000 配比可能要按 budget 重排，回填时一并评估。

### 心跳 10:1x（st-gpu-final）| 状态：干完（T0 标定完成+实测回填） | 下一步：等总指挥裁 T1/T2 重排方案；16:45 日循环圈观察
- **T0 标定完成（首个点火硬前置闭合）**：grid_20260924-080309，200/200 全活（backtest_dead=0/eval_dead=0/degraded=0），全闭卷窗 1,622 日，N_eff=12，成本门五档全程真跑（修门后首次真实工作量测定）。
- **实测 per_point=35.33s/格（回填 prereg 完成，fail-closed 解除）**——为预算估 6.8s 的 5.2 倍。
- **预算影响（裁定请求，呈总指挥）**：59h 窗×0.8 占空÷35.33s ≈ **4,640 格**有效容量（原计划 24,990 格的 18.6%）。T1=17,100/T2=13,000 配比不可执行。本包建议方案：①点火前先做 1 小时 profiling（定位 35s 构成：因子重算 vs 五档扫描 vs IO——若五档扫描占大头可对 T1 粗扫档用 0/40 两档近似、入围者才全五档，可省 ~60%）；②按 4,640 格重排：T0 已完 200 + T1≈2,900（9 达标胞×主轴分层）/T2≈1,500（主效应前 20% 展开+4440 复验）；③或压缩 T1 面板域（流动性 top-3000）降单点耗时。三案裁一即开工。
- 待清理：grid_20260924-080007/080047 两个被中止的残目录（我建的临时产物，本轮未删避免误伤 T0 正跑）。

### 心跳 10:15（st-gpu-final）| 状态：干完（单格点 profiling 出数，三案裁定证据已备） | 下一步：等批注裁三案；16:45 圈观察；本轮无批注无触发
- **profiling（.runtime/tmp/gpu_final_20260924/profile_one_point.py，代表配方近似）**：数据装载 15.2s（批级均摊）/因子 1.2s/单次回测 26.2s/**五档扫描 131.9s（每档=一次全量成本重模拟，占单格点 83%）**。
- **裁定证据换算**：粗扫两档（0/40bp）可将五档成本 29.3s→11.7s，单格点 35.33→~17.7s → 容量 4,640→**~9,600 格（2.1 倍）**。方案①获数据支持：T1 粗扫两档+T2 入围者全五档+4440 复验，统计上粗扫判淘汰（单调性/换手门）与全五档判活同向。
- 本轮无新批注、无"队列畅通"；q-0009 已落 HEAD；无在跑任务（防重入通过）。

### 心跳 10:2x（st-gpu-final）| 状态：干完（两档粗扫≈全五档的实证完成，方案①证据闭环） | 下一步：等批注裁三案；16:45 圈观察
- **实测证据（T0 真数据，非断言）**：200 格点上，按 sharpe 与"sharpe−换手惩罚"排秩，Spearman=0.9998~1.0000、top50 重合 50/50（惩罚强度跨 20 倍带稳定）。成本档排序对本族配方（FACT 低换手，均值 0.107）**不构成排名扰动**；E7 换手门 8x 线 0/200 触发。
- **结论**：方案①（T1 两档粗筛+T2 全五档终审）的统计前提成立，容量 ~9,600 格有实测背书。三案裁定材料齐备：①两档粗筛（9,600 格）②朴素重排（4,640 格）③压面板域（正交乘子）。
- 本轮无新批注、无"队列畅通"、无在跑任务。

### 心跳 10:35（st-gpu-final）| 状态：干完（归因读端首跑出主效应表+net_returns 产物自描述缺陷修） | 下一步：q-0010 落地核对；等三案裁定+16:45 圈
- **归因读端首跑成功**：T0 200 格×9 达标胞=1,800 行主效应表（residual 64 日如实披露），落 run 目录 condition_attribution.csv。分化读数：gboiling|srisk_off +4.40 / gwarming|srisk_on +3.37 正端集中；gmild|srisk_on -3.38 / gcooling|sneutral -3.67 负端集中——观察性分层（非因果），直接供 T1 分层配比。
- **过程缺陷发现+修**：net_returns.parquet 原为 values-only RangeIndex（产物不自描述，归因零重叠暴露）→ factory 改 nets_archive 带日期索引落档（双树已修，q-0010 在队）；T0 旧产物已按交易日历一次性恢复。
- 本轮无新批注、无"队列畅通"。

### 心跳 10:55（st-gpu-final）| 状态：干完（q-0010 落地核对+方案①合规性勘误自纠） | 下一步：等三案裁定（①需 Owner 修冻结，②③总指挥可裁）；16:45 圈观察
- q-0010（net_returns 产物自描述修复）已落 HEAD（factory nets_archive ×4 实证）。
- **勘误自纠（重要）**：本包三案建议中**方案①（T1 两档粗筛）与冻结册 `cost_gate_in_every_tier: true`（Owner 采纳令"任何粗扫阶段禁跳成本门"）直接冲突**——执行①需 Owner 修 prereg 冻结（⑤门位 production 流转），非总指挥可裁；方案②（按 4,640 格朴素重排）/③（压缩面板域）不碰冻结条款，总指挥可裁即开工。profiling/排秩证据仍有效（①若获 Owner 特批则容量 9,600 格成立）。
- 本轮无新批注、无"队列畅通"、无在跑任务。

### 心跳 11:25（st-gpu-final）| 状态：干完（落地耐久性抽检 8/10→两 FAIL 分诊→prereg 回填件 q-0011 在队） | 下一步：q-0011 落地核对；16:45 圈；等裁定批注
- **落地耐久性抽检（k4 吞并模式红蓝复查）10 项**：8 PASS / 2 FAIL→分诊：①prereg per_point=35.33 系盘面回填未提交（非覆盖）→已入队 q-20260924-...-0011 落库；②schedule_gate_policy gpu:12=未跟踪活配置（HEAD 本无此文件，盘面生效中，维持"不入 git"判，非回归）。
- 结论：无他班覆盖我的件；耐久性零流失。
### 自动化已删（Owner 令，11:3x）
- automation-f8db602f（st-gpu-final 每 30 分钟监控轮，已跑 7 轮）经 Owner 令删除。本包状态快照不依赖自动化：三案裁定/Owner frozen 签发/resource 冲突三项待批，均已在本台账留痕，等总指挥巡检批注即可。
