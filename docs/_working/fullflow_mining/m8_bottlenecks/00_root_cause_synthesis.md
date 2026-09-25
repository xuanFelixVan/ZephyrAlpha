---
ttl: task_bound
---

# M8 堵点深挖 · 系统性根因综合册（00_root_cause_synthesis）

> 立册 2026-09-25 ｜ 车道 M8（会话 st-commitspeed-tbl-20260924）｜ 只读挖矿+本目录零 commit。
> 数据真源（全部实测，非记忆）：`.runtime/commit_queue/dead/`（398 封死信，统计窗内仍 +1/小时级缓涨）＋ `.runtime/audit/commit_block_events.jsonl`（2,034 事件）
> ＋ `.runtime/audit/bottleneck_ledger.jsonl`（17,494 行）＋ `git show HEAD` 逐探针落地核验
> ＋ 四波战役卷宗：`docs/_working/commit_speedup_campaign/`、`flash_speedup/`（含 `archive/2026-09/kimi_audit/lane_reports/F6_堵点总账.md`）、
> `commit_system_opt/`、`commit_chain_mining/`、`docs/_working/cmd_ledger/`。
> 复核命令（10 分钟口径）：见 §6。统计脚本=`.runtime/tmp/csx_m8/{dead_reason_stats,block_and_fixation_stats,bottleneck_ledger_stats}.py`。

## 一、矿源大盘（实测计数）

### 1.1 死信盘（dead/ 398 封，09-22→09-25）

| 死因族 | 封数 | 占比 | 主力会话 | 说明 |
|---|---|---|---|---|
| 网关落盘失败 COMMIT_FAILED（门禁拦截） | 253 | 63.6% | sweep-tail/chainpile/metaq/commitsys | 按门细分见 §1.2 |
| landing 异常（三向合并失败为主） | 85 | 21.5% | combine/library-final/align-dirty | 27 未解析+18 翻译册+12 capability 册+8 门册+5 裁定册+5 fail_open 册 |
| NOTHING_TO_COMMIT 但快照未真应用 | 31 | 7.8% | st-stress（29/31） | 假落地防线正确捕获派生写入竞态（F1 已治本根因） |
| cascade_stale 基底级联 | 8 | 2.0% | audit-fix/metaq-gc | stale_by 链 |
| 冲突/自撤（陈旧基底+CAS 竞态） | 16 | 4.0% | 各会话 1-2 封 | 高频争抢文件：rules_integrity_db.json×4、commit_queue_landing.py×3 |
| CLAIM_REQUIRED_VIOLATION | 4 | 1.0% | stress/align-dirty/mapbuild | claim 前移协议 |

requeue 标记：131 已重投 / 267 未重投。按日：09-22=2、09-23=116、09-24=275、09-25=5——**死信量随并发会话数超线性上涨**（09-24 五线并发夜为峰值）。

### 1.2 COMMIT_FAILED 253 封按门细分（top 12）

| 门 | 死信 | 拦截事件(commit_block_events) | 性质 |
|---|---|---|---|
| GATE-PRECOMMIT-RUN（ruff/format） | 49 | 198 | 入队预检不跑 ruff 钩=结构性死因（decisions_log 19:5x 已定性+纪律已补） |
| CREATE-GUARD（token/basename） | 36 | 98 | token 册读 HEAD 版=结构性死因（见 RC-6） |
| TRANSLATION-COVERAGE | 27 | 24 | 新建 .py 缺翻译条目，与 CREATE-GUARD 同属"登记先行"族 |
| GATE-VOCAB | 16 | — | 术语三层硬编码 |
| REFERENCE-INTEGRITY | 10 | — | 引用实存 |
| PROTECTED-PATHS | 9 | — | 稀有天价（P50 182.8 分/封，deadletter 成本表） |
| TTL-METADATA | 9 | 35 | frontmatter 头值非法（0026 死因） |
| MAP-ALIGNMENT | 9 | — | 全图对齐 |
| CAPABILITY-OVERLAP / ORPHAN-MODULE / COMPLEXITY-GUARD / SSOT-REDEFINITION | 6/6/6/6 | 31/—/20/48 | 内容扫描族 |

### 1.3 拦截面与堵点本

- `commit_block_events.jsonl` 2,034 事件：top 拦截面 GATE-PRECOMMIT-RUN 198 / CREATE-GUARD 98 / BLUEPRINT-FORMAT 95 / WORKTREE-REQUIRED 80 / HELD-OVERLAP 61 / CLAIM-REQUIRED 57 / ALGO-NOTE-SYNC 52 / MUTABLE-CONST 50 / SSOT-REDEFINITION 48；gate_id="－"（采样基线）324。按日峰值 09-16=332、09-13=241、09-23=244。
- `bottleneck_ledger.jsonl` 17,494 行：dead_letter 16,039（**同一 qid 每扫描重复登记，单 qid 最多 31 行**）、alert 1,132、slow_item 208（`commit_queue.py:1598` 写）、landing_staleness 93、registry_drift 21（**全部指向 capability_canonical_file_registry.yaml**）、derived_stuck 1（`reconcile_generators.py:310` 写）。真身=三写者：commit_belt_daemon.py（`_LEDGER:60`）、commit_queue.py、reconcile_generators.py。

### 1.4 治本落地核验（git show HEAD 逐探针；2026-09-25 01:2x 首测、01:4x 十二探针复测一致，HEAD=77129e94b1）

| 探针 | 结果 |
|---|---|
| D3 池波次+装表（landing_phase_stats/pool_wave） | **已落**（scripts/governance/commit_queue_landing.py） |
| B4 排队键 created_at FIFO | **已落**（scripts/commit_queue.py） |
| D4 幽灵 pending 双层修（回写收窄+认领终止性复查） | **已落**（commit_queue.py:2296 注释+landing:2296） |
| 批六 B0 出窗 regen_scope flag | **已落**（config/flags.yaml:48） |
| G1 还原审计闸+G2 热册还原 CAS | **已落**（e910cae9ac） |
| R-06 告警冷却状态机 | **已落**（commit_belt_daemon.py:515-527） |
| R-04 claim 失败 TTL 300s | **已落**（scripts/git_commit.py:663） |
| N-3 预检逃生旗映射 | **已落**（be934b079d） |
| §2.1 worktree 路径 gate_id 归因（_wt_block_gate_id） | **已落**（session_worktree.py） |
| #ARCH-HEARTBEAT-001/002 心跳治本 | **已落**（session_concurrency.py:8 不变式头） |
| W4 env 泄漏止血（prev_gateway_env） | **未落**（在队 q-0027） |
| p13 ms>=1.0 盲区过滤 | **未落**（commit_gate_registry.py ms>=1.0 仍在，q-0029 在队） |
| replay 仪器/_tree_view/derived_dirty_ledger（P3/包8 件） | **未落**（HEAD 无此文件，0028 在队+csx-p3b 待投） |
| D1 stats_lock 派生 offload、D2 删全局 env 写（包5） | **未落**（设计完，待 W4） |
| N-1 BLUEPRINT-FORMAT own-scope 化 | **未落**（gate_registry 仍 own_scope: false；全册 33 true/80 false/113 条） |

## 二、系统性根因 Top10

> 每条：病根机制 / 历史发作 / 治本状态 / 残余风险。发作数=本册 §1 实测+各战役卷宗实测引用。

### RC-1 全链共读共享可变暂存区（无不可变树）——延迟与判定的共同上游
- **机制**：102 台 in-proc 门+68 hook 全在锁内读共享 staged index；门禁读的是"别人的在途件"，你的等待随全场暂存量上涨（实测 543 个他人暂存文件）；MUTABLE-CONST verdict 随 index 噪声规模漂移（replay 实弹冒烟实证）。
- **发作**：FOREIGN-CHANGE 38 拦＋WORKTREE-REQUIRED 80 拦＋直连外来连坐死信（BLUEPRINT-FORMAT 挡全场直连）；单文件门禁链 64s 中 83% 是 5 台全仓扫描门；N-2 型外来 bulk-add 回退/删件事故 ≥8 波截获（flash_speedup 两轮核验+§3.1）。
- **治本**：**未落**。A1 冲突图/A2 目标架构/A3 改道矩阵/A4 阶梯已设计完；S1 不可变树（72 台咽喉一处改）是工程中心，replay 仪器（0028 在队）是其出厂判据的先决件。
- **残余风险**：**最高**。20+ 并发下暂存噪声与等待时间线性互涨；所有"共享判定"门（克隆检测、跨件断链）都会把他会话 WIP 当成自己的罪证。

### RC-2 派生热册"整册重写+无基底溯源"——并发登记互吞
- **机制**：token/翻译/门册等整册重写写入时无 base provenance（79/80 袋无基底），落地三向合并遇 ours 同侧身份键重复即死；一件 capability 册占全部文件碰撞权重 53.4%（138 项）。
- **发作**：landing 异常 85 封（18 翻译册+12 capability 册+8 门册）；registry_drift 21 条全在 capability 册；黑手案（盘面 31 条 token 蒸发→重置不落 stash）及 st-align-dirty 同病 epidemic 实证。
- **治本**：**部分落**。G2 热册还原 CAS 化+G1 还原审计闸已落（e910cae9ac）；F1 派生折叠已落（fe47296d，NOTHING_TO_COMMIT 族根因）；**条目级合并（S4"袋必填 base_tree_sha+declared_keys"）未落**。
- **残余风险**：高。每条车道登记 token/翻译都要过同一本册，20+ 并发=登记队列化的必然。

### RC-3 队列工单异常处理缺陷（熄火+幽灵双落地）——已断根
- **机制**：D3=一波等全部工返回，单工死 straggler 占波→新波永不开；D4=`_mark_cascade_stale` 回写复活幽灵 pending→`FileExistsError[WinError 183]`→工死；认领不查 done/→同件二次落地、done 膨胀。
- **发作**：排空 18→2-4 件/时、积压 83 件、并发实测 1.000；09-18 红蓝 done=120 vs total=60 计数翻倍旧账。
- **治本**：**已落**。D3+B4+装表（q-0005）、D4 双层修（q-0010），四路并发实证、四探针全 0；belt 纪元自检已自换血（21:46 re-exec）。
- **残余风险**：低。同类残余=**活进程不加载新码**（MQ-5 型换血饿死：积压使 lease 不释放、安全点不到）——已自解但机制上仍需"每 N 件强制安全点"方可根治（未落，小改）。

### RC-4 门禁链固定地板（81.2s+0.96×files，43 台 always-run 占 60%）
- **机制**：内容扫描门每链全跑；六台同读 2.68MB canonical 册各自 `yaml.safe_load`（单解析 3.6-4.2s）；union 台丢 files_trigger 无条件全跑；缓存白名单仅 14 台且命中率 8%。
- **发作**：14 天窗全门禁 CPU 111,852s；被拦尝试烧 2,386 分；提交者等待 p50 5.5 分/p99 3 小时；slow_item 均值 755s（n=173）。
- **治本**：**未落**（三簇合并/四台降档/diff 化方案已收卷=包8；p13 盲区修在队；P3 的 `_GATES_DIR` 17→136 复权在 csx-p3b 待投；缓存键=包7）。门禁退役三候选（PURE-SHIM/STASH-ACCUMULATION/RECONCILER-FILE-OPS）与 PANORAMA legacy 位挂起=Owner 净删门位。
- **残余风险**：高。多车道吞吐=门禁地板÷并发系数，地板不降则 60 件/h（G2）不可达。

### RC-5 "登记先行"族门禁的结构性时序死因（token/翻译册读 HEAD 版）
- **机制**：CREATE-GUARD/TRANSLATION-COVERAGE 落地侧读 HEAD 版册子；盘面已登记但册未落 HEAD 前，任何含新建文件的袋必拦——**先落册再落码是唯一正门序**，但无机制强制。
- **发作**：CREATE-GUARD 36 死信+98 拦截；R44 八阵亡中 q-0002/0008 即此；"今晚 token 依赖批按 FIFO 再死一轮"的预言性连锁（audit-fix 0022-0029）；flash_speedup 7 件交付件卡注册表 MM 一整夜。
- **治本**：**纪律已入册（token 册单批先行、q-0030 占位）**，机制性解法（enqueue 时同批携带册条目或落地侧读工作树）**未落**。
- **残余风险**：高。每条新车道新建 .py/.md 都过这道门；并发越高，"册先行"被插队的概率越大。

### RC-6 队列快照与 dev 尖漂移（陈旧基底/CAS 竞态/级联 stale）
- **机制**：enqueue 快照 base 与落地窗 dev 之间他人推进同路径→逐文件快进判定失败；快照含未修字节（0001 死于 stale B905/B009、0026 死于 TTL 头）；同文件多批在飞互相级联 stale。
- **发作**：冲突/自撤 16 封+cascade_stale 8 封；0007/0025 陈旧基底死信；23:1x 扰动期他会话 4 袋连死；"gateway 同文件串行纪律"是人工缓解。
- **治本**：**部分落**。基底重校验防线正确工作（0007 死=拒绝覆盖新 dev，非事故）；B4 FIFO 已落；ruff/format 入队前双跑纪律已立；`--from-bag` 重投+从当前 dev 重拉 scratch 处方已入交接卡。**结构解（按域分区/条目级合并/租约）未落**。
- **残余风险**：高。并发越高 dev 前进越快，快照陈旧率线性升；20+ 车道下"同文件串行纪律"将不可人工维持（冲突图实证：热册 top1 占 53.4% 碰撞）。

### RC-7 门禁判定正确但"使用摩擦"前置缺位——盲发循环
- **机制**：同一死因连死 2-3 次不修根因（贡献约 30% 死信）；报错文案不递送处方锚点；13 条分诊病灶中 12 条属 Complex。
- **发作**：(c) 使用摩擦 1,433 行（F6 总账 40.1%）；st-dloop 13 连败撞 13 个不同门禁；指南落地前 112 封死信全成本≈61 会话时/晚。
- **治本**：**大部分落**。指路指南 playbook v1.1+死因锚点双出口（3919c83d87）；F5 DC/目录容量前置提醒（1fb04f6e）；N-3 逃生旗映射修（be934b079d）。残余=报错文案精修、同 qid 同原因死信合并。
- **残余风险**：中。20+ 车道必然涌入新车道会话，无前置提醒则首死率高。

### RC-8 观测面：重复记账、口径漂移与盲区
- **机制**：堵点本每扫描重复登记同一死信（单 qid 31 行，16,039/17,494）；gate_execution_stats `ms>=1.0` 过滤致 42-44% 门禁时长不可见；名册四口径漂移（模块 115 / in-proc 102 / 统一册 180 / 链内计时名 124）；告警"记账不推送"（task_board 无主动推送）。
- **发作**：R-06 自激 1,095 行（曾占全场 31% 噪声）；daemon 死亡期 385→386 死信零记账（断流 09-18 起）；T14 名册快核查实 own_scope=None 67 条。
- **治本**：**大部分落**。R-06 冷却状态机（belt:515）、THD-ALERT-005/006/007、A1/A2 真实计费+八段计时+residual_ms、§2.1 worktree gate_id 归因、G-01/G-03 相位插桩均已落；**ms 盲区修（0029）与名册对账生成器+own_scope 机生补全（包13）在队未落**。
- **残余风险**：中。观测缺口不直接阻断，但会让下一次"并发 1.000"式病灶零证据潜伏。

### RC-9 会话生命周期与 claim/心跳跨进程竞态
- **机制**：pid=0 逻辑会话心跳窗（90s）竞态；死会话 stale claim 挡道；WIP 判读归因读快照陈旧（classify_workspace_wip 判 library 四件 claim=st-ailayer 而 lock_files 实判 CLEAN）；stash/清扫无 notice 即蒸发（registry_incident 台账目录整目录消失、msg 草稿被误删）。
- **发作**：CLAIM-REQUIRED 57+HELD-OVERLAP 61 拦；library-final 死会话残件需总指挥代投；T1 stash 定责实验 cwd 漂移致主区 staged 638→439（第三次踩同一陷阱）。
- **治本**：**大部分落**。#ARCH-HEARTBEAT-001/002（90s 心跳+idle 1800s 自动退出）、FAILED_CLAIM_TTL 300s、stash_notice.json、pwd 前置断言纪律。**N-4 心跳窗口参数化/预检前自动续心跳留 Owner**；classify_workspace_wip 归因陈旧未修。
- **残余风险**：中。并发×会话数越大，死会话遗物与 stale claim 频率越高。

### RC-10 治理债连坐：own_scope 缺口+潜伏克隆+解析连锁
- **机制**：own_scope=false 的门对外来 staged 连坐（违宪法 §3.1 own-diff 默认）；own_scope 覆盖 33 true/80 false/113 条；extract 级克隆债潜伏在"无人敢改"的热治理文件里，改一行即 CloneGuard 全文件重扫连坐（q-0010 死信实证）；共享注册表解析失败连锁硬拦（R-09）。
- **发作**：N-1 一个外来占位 .py 挡掉全场直连提交；CAPABILITY-OVERLAP 31 拦；session_worktree 三对 getter 克隆债堵住 2 行观察性修复的落地。
- **治本**：**部分落/在飞**。A2 解释位 CHANGING_IN_COMMIT own-scope（P3 在 csx-p3b）；own_scope 机生补全 53 条（包13 在队）；**N-1 own-scope 化未落（仍 false）**；R-09 隔离未落；克隆债 ack 未批量处置。
- **残余风险**：高。20+ 并发=外来 staged 常态化，连坐面全开；"改基建热文件的前置税"直接抑制治本速度。

## 三、根因×多车道目标关联度（20+ 并发下复发放大排序）

| 排序 | 根因 | 20+ 并发下的放大机制 | 状态 |
|---|---|---|---|
| 1 | RC-1 共享暂存区 | 等待与误判随全场暂存量线性涨；所有共享视野门全开 | 未落（S1 是总闸） |
| 2 | RC-6 快照漂移/陈旧基底 | dev 前进速率×在飞批数=死信率；同文件串行纪律人工不可维持 | 部分落 |
| 3 | RC-5 登记先行时序 | 每车道新文件必过 CREATE-GUARD；册先行被插队概率∝并发 | 纪律有、机制无 |
| 4 | RC-2 热册整册重写 | token/翻译/门册登记全收敛到 4 本册；碰撞权重 53.4% 单册 | CAS 落、合并未落 |
| 5 | RC-4 门禁地板 | 吞吐天花板；43 台 always-run 不随 files 缩 | 未落（包8/7） |
| 6 | RC-10 治理连坐 | 外来 staged 常态化→own_scope=false 门全连坐 | 部分在飞 |
| 7 | RC-7 使用摩擦 | 新车道会话首死率；盲发循环×30% 死信 | 大部落 |
| 8 | RC-9 会话竞态 | 死会话遗物/stale claim ∝ 会话数 | 大部落 |
| 9 | RC-8 观测盲区 | 病灶潜伏零证据；重复登记噪声 | 大部落/包13 在飞 |
| 10 | RC-3 工单熄火 | 已断根；残余=换血饿死机制化未落 | 已落 |

## 四、历史发作时间线（一页纵览）

- **09-10/11**：死信 952 项甄别、index.lock 4h 陈旧锁、watchdog 旧码整夜打死撞锁项、sys.modules 毒缓存——"根因已修"三次证伪（`2026-09-11-commit-queue-dead-zero-closure.md`，遗留 P1⑤/⑥ 未结案）。
- **09-13~17**：commit_block 241-332/天峰值；R-01~R-12 根因表成形；F6 总账 3,572 行四态归属零无主；S18 四张裁定书（#333 签署）。
- **09-18**：flash_speedup 战役 F1-F9（门禁常数→92/h 串行能力）；N-1~N-5 现场新证；纠缠脏树 N-5（裁定 #385 终审）。
- **09-22/23**：死信 112 封成本表（≈61 会话时/晚）；registry_incident 台账目录消失（R31 教训）；chainpile/ulib3 连死潮。
- **09-24/25**：五线并发夜——死信 275 封（历史峰值）；commitsys 指南+G1/G2 落地；commit_speedup 战役 D3/D4/B4/装表/批六落地、W4/P3/replay/包13 在飞。

## 五、三态自审

**挖干可施工**：本册六向证据齐（§1 实测计数+§1.4 HEAD 探针+卷宗锚点），Top10 每条有根因机制与修法归属；开放伤口册=`01_open_wounds.md`（55 条＝可机械施工 22／须Owner 24／已过期失效·已闭合 9，逐项有出处+修法+双态实证）。
**待挖**（不阻塞本册结论）：包8/9/7 落地后的实测回收数（链 64s→<15s 等 Owner 终止判据数值当前均未测得，须等落地后实测）；`landing 异常 27 封 (unparsed)` 的 reason 细分（需读死信全文逐封归因，量小可后补）。
**待裁**（归 Owner/总筹，本车道不裁）：见 `01_open_wounds.md` §三 Owner 门位清单（MQ-1/MQ-3/MQ-4/N-1/N-2/N-4/退役三候选/门禁退役§4.2）。

## 六、复核命令（10 分钟口径）

```bash
# 1) 死因族分布+会话/日期透视（396 封）
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"
python .runtime/tmp/csx_m8/dead_reason_stats.py | head -60
# 2) 死因细分(门级/真源级)+拦截面聚合+HEAD 治本探针
python .runtime/tmp/csx_m8/block_and_fixation_stats.py
# 3) 堵点本 kind 分布+pending 现状
python .runtime/tmp/csx_m8/bottleneck_ledger_stats.py | head -40
# 4) 落地真值抽查（凡"已落"以 HEAD 实测为准）
git show HEAD:scripts/governance/commit_queue_landing.py | grep -c landing_phase_stats   # >0=D3 装表
git show HEAD:config/flags.yaml | grep regen_scope                                       # =B0 出窗已落
git show HEAD:src/zephyr/gov_enforcement/rule_bridge/commit_gate_registry.py | grep -c "ms >= 1.0"  # =1 则 p13 盲区仍未落
git show HEAD:docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml | grep -c "own_scope: true"  # 33=包13 未落
# 5) 卷宗交叉验证
sed -n '30,50p' docs/_working/commit_speedup_campaign/90_verification/CAMPAIGN_STATE_SNAPSHOT.md
grep -c "RC-" docs/_working/fullflow_mining/m8_bottlenecks/00_root_cause_synthesis.md
```

## 七、与本战役其他车道的关系

- 提交链地基批次（P3/包5/包8/9/7/10/11/14/15）进度与依赖=CAMPAIGN_STATE_SNAPSHOT.md §四，本册不重复排程；本册 Top10 的"未落"列即其证据基线。
- M3 治理门禁链车道可直接引用 §1.2/§1.3 的门级计数；M5 调度常驻链可引用 RC-3 残余（换血安全点机制化）与 G-10 计划任务盲区；M0 骨架可引用 §四 时间线做交叉验证。
- 本册全部结论以 2026-09-25 01:2x 盘面为准；在飞批（0027/0028/0029+csx-p3b/包10/包13 子代理）落地后，§1.4 探针表需重跑刷新。
