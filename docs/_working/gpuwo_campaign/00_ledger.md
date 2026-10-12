---
ttl: task_bound
title: 四 GPU 工单施工班·班台账（st-gpuwo-20261011）
created: '2026-10-11T22:20:00+08:00'
sid: st-gpuwo-20261011
family_id: GPUWO-CAMPAIGN
---

# 四 GPU 工单施工班 班台账

令源：Owner《施工指令·四 GPU 工单调查与派工》2026-10-11 → 总指挥调查复核 §1 → 本单派工。
工单真源四张：`docs/_working/automation/20260917_wo_gpu01_night_mining_ollama.md`／
`..._wo_gpu02_kronos_batch_scoring.md`／`..._wo_gpu03_sft_gguf_ollama_chain.md`／`..._wo_gpu04_rl_execution_training.md`。

## 1. 角色与并发权限（按令自决）

- 本班=施工队总包：只读类（诊断/对账/考古）多车道全并行；写盘与入队按文件/域分区，同文件跨车道禁并发。
- 车道：`.worktrees/st-gpuwo-20261011`（分支 `ai/st-gpuwo-20261011/task-gpuwo-four-orders`，建车基线 a0e27b1ac3，
  心跳 daemon PID 39592）。提交唯一入口 `python scripts/git_commit.py --session st-gpuwo-20261011 --files <清单>`。
- 只呈批不代拍三类：B-007 消费/训练批复、软件安装（llama.cpp）、任何上实盘或消费接线。

## 2. 进场现场信号（已核，非本班引入）

1. **冷启动 cleanup 清了 7 枚死锁**，其中 4 枚落在本单禁碰面：
   `scripts/backtest/factory_grid_executor.py`／`src/zephyr/backtest/gpu_core.py`／
   `tests/research/backtest/test_factory_grid_executor.py`／`tests/research/backtest/test_l2_gpu_landing.py`，
   另 3 枚在 `docs/_working/mineloop_campaign/`（29、32 号件）与 `docs/_working/backfix_campaign/00_ledger.md`。
   清完后锁面=CLEAN（零 claim），而 GPU 化两车道
   `.worktrees/st-gpux-20261011`／`.worktrees/st-gpux2-20261011` 仍在册，
   reaper 现算仍报 PID 22656 心跳新鲜（cmdline 含 st-mineloop-20261010）。
   ⇒ **并发避让前提受损**：在册车道可能继续写盘但已无 claim 保护。本班不碰上述任何一件，
     并把它列入呈批面请统筹复核是否需令相关车道重新 claim。
2. **主区池面 657 条脏**（reaper 自报 worktree_changes=660>50），含本班要用的
   `config/resource_profile_registry.yaml`。按在册纪律：需要该册变更的施工**另起袋**，绝不随袋提交他人未落地条目。
3. **Ollama 现在可达**（v0.34.1，127.0.0.1:11434，8 模型在册）——但 10-08 那夜 LaneC 翻译腿全数
   `llm_error:ConnectionError`，见 `01_anchor_reverify_lanec.yaml` 新发现 N-1。

## 3. 四单进度（三态之一登记）

| 单 | completes_when 摘要 | 态 | 产物位 |
|----|--------------------|----|--------|
| §1 锚点重验+LaneC 体检 | 原令 §1①-④ + LaneC 产物完整性四态分诊 | 已完成（q-0003 落地 ccf6d852cc） | `01_anchor_reverify_lanec.yaml` |
| P1 GPU-03 | 情绪 SFT 模型回灌 Ollama 且夜窗情绪批切换自模型验证一轮 | **部分完成＋呈批**（步骤 1/2 完；步骤 3 三重实测拦路；现 adapter 实测 0.6290 vs 基线 0.7869） | `02_gpu03_dataset_and_f1_evidence.yaml`＋两件套 .ps1 |
| P2 GPU-01 | 夜窗挖矿批上线且档位 A/B 定版报备 | **受阻**（夜窗两件套＋lane_b 档位参已落码；A/B 未出数＝今夜起跑不进 23:00 窗） | `03_gpu01_gpu02_construction.yaml`＋`05_`(待) |
| P2' GPU-02 | 批量打分窗口上线且落表，或工单否决归档 | **受阻**（三缺件全落码＋10 支守卫测；表未建、任务未注册；令文 00:30 与 CH 让路窗算术冲突已呈） | `03_gpu01_gpu02_construction.yaml`＋`06_`(待) |
| P3 GPU-04 | RL trainer 施工完成并通过 B-007 后启动，或否决归档 | **只呈批**（premise 过期：TD3 trainer 早在位，缺的是影子对拍腿＋replay 数据腿＋窗登记） | `04_gpu04_b007_material.yaml` |

## 4. 施工分层口径校正（有据，随袋报备）

两张工单把注册脚本写作 `register_night_mining_task.ps1`／`register_kronos_scoring_task.ps1`（未给目录）。
实测本仓分层=**注册册 `scripts/tasks/register/`（在册 32 件）＋执行链 `scripts/tasks/run/`**，
`scripts/` 根只留 2 件历史注册册（`register_process_reaper_task.ps1`、`register_commit_perf_report_task.ps1`）。
样板=`scripts/tasks/register/register_factory_lane_c_task.ps1`（幂等 `Set-ScheduledTask` 就地更新，
禁 Unregister+Register；`-ExecutionTimeLimit`＋`-MultipleInstances IgnoreNew`）。
⇒ 本班新件按分层落 `scripts/tasks/register/`，执行链落 `scripts/tasks/run/`，
并同步 `scripts/script-manifest.yaml`（生成器单口 `generate_script_manifest.py`），不入 `scripts/` 根。


## 5. 本班撞开并对症修好的落地链死法（三条，都是"机制面"不是"我这单"）

1. **心跳守护自退 → 队列把活会话判幽灵**（q-0001 死）。建车 14 分钟后
   `.runtime/sessions/<sid>/heartbeat.jsonl` 末行写 `status=exited reason=session not in registry`，
   注册表条目同时消失；此后入队能过（它认 BRANCH-WRITE-TRACE 旁证），**落地侧存活闸不认**，袋直接进 dead/。
   修法＝按今日维护二班刚立的**保活正门**：`register_heartbeat_keepalive(root, sid, reason=..., requested_by=..., ttl_seconds=7200)`
   ＋ `SessionRegistry(root).register(sid, pid=0)` ＋ 重起 daemon。**且每投一袋前现注册现投，不沿用上轮**；
   注意 `logical=True` 会被"非 chief 形态"降级拒绝（MARK_LOGICAL_DENIED），长班唯一合法通道就是具名保活授权。
2. **新建件"先 commit 到车道再入队"必死**（q-0002 死）。enqueue 把 `base_head` 记成**车道自己的 HEAD**；
   新文件已在车道 HEAD 里 ⇒ 落地侧 `_merge_registry_file` 判"在本袋基底存在而 dev 已删＝陈旧快照复活"直接拒写
   （`scripts/governance/commit_queue_landing.py:2367` 那条 P0 红队补齐）。
   正解＝新文件**先入队、后落车道 commit**（工作树留原字节，车道 HEAD 不含它即可）。
3. **预检扫的是整个暂存区不是本袋清单**（03B 被 TABLE-NAME-REGISTRY 拦）。我把已属另一袋（03A）的
   DDL 件一直留在 index 里，`schemas/**/market_*.py` 的 DDL 常量按规则是豁免的，但它作为"别人袋"的件
   混在我的暂存面上仍被算进来。正解＝**一袋一暂存面**：投前 `git restore --staged .` 再只 add 本袋文件。
   同族另一条：`COMMIT-SCOPE` 正当拦跨域 ⇒ 按域切两袋＋后继袋 `--depends-on` 先行袋，别拿 `--allow-multi-domain` 糊。

另两条**测量口径**教训（不是门，是尺）：
- 资源册再生**只能在主区根跑**：从车道根跑 `generate_resource_profile_registry.py` 只产出 69/103 实体，
  丢的恰好是全部 `sch_*` 家族——从车道拿它当绿＝假绿。
- `--score-only` 的 help 文案里写全限定表名，被 TABLE-NAME-REGISTRY 正当拦下：表名连说明文字都不该埋，
  因为它会被复制成第二真源。

## 6. 通宵执行与晨间裁定包（03:0x 编制；04:00 后三项实测数见 6.1 末段回填）

> 三段式按通宵令第六节：执行了什么／自裁了什么／等什么裁定。
> 状态只认三种：`HEAD`（已落地，判据=git show dev:<件>）、`在队`（qid 在册未落地）、`车道`（未入队）。
> 03:0x 实测：pending=47、head 是别班件已等 146 分钟；本班 8 袋在队、0 件今夜落地面新内容 ⇒ 本节每条都标真态，不写"已交付"。

### 6.1 执行了什么（逐件三态＋红绿锚点）

| 件 | 三态 | 锚点（命令＋实测） |
|---|---|---|
| §1 锚点重验＋LaneC 10-09 产物完整性体检（1 册） | HEAD | `git log --oneline -1 -- docs/_working/gpuwo_campaign/00_ledger.md`＝ccf6d852cc |
| GPU-03 可复现性与 F1 实测证据（2 册） | HEAD | a2c46fddca（样本级重合 1178/3600＝jaccard 0.1956 那条） |
| GPU-02 新表三件（schema＋apply_market_tables_ddl＋表名册） | 在队 q-…-0012 | 前身 0005 死于 `git commit` 60s 超时（他班同签名连死 335 次），`requeue --from-bag --force` 重投 |
| GPU-01＋GPU-02 施工 9 件（score-only 腿／两套注册＋执行 ps1／lane_b 档位参） | 在队 q-…-0006 | 红证 5/5 打在 dev 未修码上判败，0/5 在本码 |
| ↑ 的 R-3 分片超集（同 10 件携新字节） | 在队 q-…-0013 | 新 9 条判据在 dev 码上 9/9 判败、本码 0 判败；19 passed＋lane_b 20＝39 passed |
| LaneC 假绿修（Ollama 依赖腿＋零步完成/4h 掐断显式失败） | 在队 q-…-0008 | 4 桩探测器 4/4 判败；ParseFile SYNTAX-OK；非 ASCII 0 字节 |
| 06 llama.cpp 安装册＋07 GPU-04 更正册 | 在队 q-…-0009 | 07 册 C-1 自纠：我上袋写的"Owner 门已在位"是假的（CLI 不存在、real_training 零读者） |
| GPU-03B P0 样本级可复现修复（build_sft_dataset＋6 测） | 在队 q-…-0011 | 红证：dev 码跑出 N00017 vs N00012＝判败；修后判绿 |
| GPU-04 影子对拍腿（trainer.py＋8 测＋10 册） | 在队 q-…-0014／0015 | 15 passed（原 7＋新 8）；env 侧同跑 30 passed 无回归；dev 码上 15 处 import 面查无＝红 |
| GPU-03B P1/P2 管线（build_distilled_sft_dataset.py 333 行＋9 测） | 车道（未入队） | 件本身 15 passed；被 TRANSLATION-COVERAGE 两次 DENIED，取证在 09 册 |
| llama.cpp 工具链（E 盘） | 已装 | convert_hf_to_gguf.py＋gguf/＋llama-quantize.exe；bin.zip 19,501,541B sha256 前缀 bcfca9c8；**缺 `conversion/` 包**（装完即停，未追） |

04:00 后回填的三项实测（今夜不跑＝让路窗内零跑批零 CH，字面执行）：

- ⚑ R-4 冒烟（5 只票／synthetic／**零写生产表**／逐进程显存尺／≤25 分钟自动停）：尺＝`.runtime/tmp/gpuwo_r4_smoke.py`。
  在册提醒已避：nvidia-smi 设备级合计＝假尺，本件只认 per-PID 行＋torch 进程内自计两路对拍。
- ⚑ W-1 前置量测（execution_report 的 decision_timestamp 覆盖率＋与 tick_depth_5 的可联比例，UTC↔Asia/Shanghai 换算与分区剪枝已写死）：尺＝`.runtime/tmp/gpuwo_w1_depth_join.py`。
- ⚑ GPU-03B P1 金标扩充草稿＋Owner 抽检包（`gold-pack --target 600 --spot 60`，教师腿＝qwen3:8b）：
  今夜 02:58 实测 Ollama 在册 8 模型，qwen3:8b／qwen3:14b／deepseek-r1:14b 齐（GPU-01 档位 A/B 的三档都在）。

### 6.2 自裁了什么（每条＝断言＋证据＋所依据的预签裁定或授权矩阵行）

1. **不投"重打投影袋"**。依据＝Owner 2026-10-10 明令（本班／本车道禁出）。实测加成：自热册单口写之后
   袋内该册字节整体退出物化，落地内容由 PG render 决定 ⇒ "重打"已不是手工挑行，而是整册代表（含他人 7 行）。
   代价＝GPU-03B P1/P2 今夜不入 HEAD，如实标车道。
2. **M-2（replay behavior-cloning）今夜不写**，改跑只读联接量测。依据＝通宵令授权矩阵"域可自选＋最保守"，
   判据＝07 册：obs 要五档盘口、execution_report 零档级字段——硬凑＝把不存在的数写进训练面，
   与我今夜在 GPU-03 抓到的"基底有值但口径错"同族。
3. **影子腿落在训练器、不改 MOD-XS-011 选择器**。依据＝令文"现产线行为零变更"＋选择器是
   MATURITY=production／SAFETY=H 实盘路径。证据＝10 册 why_here_not_in_the_selector。
4. **给测件补 `[DOMAIN] D_EX_SOR` 头并把源码与守卫投同一袋**。依据＝根宪法二节第 4 条
   "改动与自家守卫同批是合法的"＋COMMIT-SCOPE 自己的优先级（先读 .py 的 [DOMAIN] 头，再退路径推断）。
   这不是造豁免：该测件 [MODULE] 与 [A_test] module_id 本就写 ex_sor。演进留痕＝10 册 bag_shape_note。
5. **不建 Kronos 预测表**。表结构＝架构数据，必须等 DDL-as-Code 落地后再跑 apply_market_tables_ddl.py，
   否则 DB 先于 git＝真源方向倒挂；今夜队列 47 袋，落地时点不可控 ⇒ 留作"机械四步"随落地执行。
6. **冒烟零写表**（比 R-4 令文"只落 synthetic/临时面"更保守一档）。理由＝生产表今夜还不该存在（见 5），
   而临时 CH 表要么违规建表、要么留无人认领的残件。写路径本身由 0013 袋里的列序单点＋落表失败即停守看。
7. **死袋对症重投不重做**：0005 死因是 `git commit` 60s 超时（环境类瞬态，他班同签名连 335 次），
   内容无过 ⇒ `requeue --from-bag --force`，不重写不拆判据。
8. **0006 不撤、改投超集 0013**：同会话同件以后袋为准；0013 带齐 10 件终态字节，
   避免"旧字节先落一夜、runner 拿不到分片旗"的中间态。
9. **心跳保活按在册处方重注册**（pid=0 注册＋keepalive ttl 7200），每袋前重注；不做 `mark_logical`（非总包形态被拒）。
10. **两处 Auto 档拦截未绕行、如实上报**：①读 tests/trade/ex_sor/test_td3_trainer.py 被以"文件不存在"拦下
    （Glob 实测该文件存在，110 行 7 支旧测在内）；②把 dev 字节临时覆盖车道件做实跑红证被拦。
    我改用了弱一档的"结构＋import 面"红证并在 10 册 evidence_grade_disclosed 标注定级差。

### 6.3 等什么裁定（编号菜单＋证据＋我的默认推荐）

- **G-1 GPU-03B 卡点走哪条**（证据＝09 册）：①册主车道出一个净增 8 行的投影 render 袋（今夜可解，最便宜）
  ②给 TRANSLATION-COVERAGE 的查询面加 PG 账本第三源（治本，先例＝CREATE-GUARD 已于 10-10 打过同一剂；
  动的是判官件，须治理车道）③继续等。默认推荐＝**①今夜先走、②立成治理续单**。
  另附赠一条卫生发现待判：账本里 6 条形如测试夹具的条目（degraded/layered/lying/new_mod/orphan/with_extras.py）
  在投影重打时会被一起带进 HEAD——清或留不由我判。
- **G-2 金标冻结**：04:00 后我出抽检包（≥50 条）＋扩充草稿；**Owner 抽检点头＝冻结线**，点头前我不冻结、不训。默认＝不动。
- **G-3 GPU-03 真训练按钮**：R-2② 已归档为"链在位、窗在位、按钮在 Owner"；`sft_authorization.txt` 旗在位待 Owner 落字。默认＝不跑。
- **G-4 B-007（RL 真训练＋执行侧消费接线）**：影子腿已能出可比重数（分歧率/成本差/完成率），真训练与接线仍等 Owner。默认＝不训不接。
- **G-5 机械四步的执行者**：计划任务注册×3＋资源册再生（必须主区根跑，车道跑＝丢 sch_* 假绿）＋冲突闸零红证明。
  默认＝**袋一落地我继续跑**；若我那时已停摆，下一班照 03 册 review_commands 逐条跑。
- **G-6 W-1 开不开**：今夜给的是覆盖率与可联比例两个数；数出来之前"档级重建 obs"不拍。默认＝不开（W-3 态）。
- **G-7 GPU-01 档位 A/B 首夜**：等 0006/0013 落地＋23:00 自然触发；本班不改 FactoryLaneC 任务本体（授权扩面只覆盖那两件）。默认＝只观察。
- **G-8 提交链吞吐**：03:0x 实测 pending=47、队头他班件已等 146 分钟、本班 8 袋全未落地。
  今夜所有代码成果的"落地面"都卡在这一个数上。若 Owner 要"今夜必上"，需给提速或加急通道——我不自裁动队列机制。
- **G-9 LaneC 时限**：批复要求 10-12（周一）20:00 前落地。修件在队 q-…-0008。
  若届时仍未落地，默认＝按 G-8 走加急；否则 20:00 那一夜仍会跑旧口径（可再产一夜假绿）。

### 6.4 编制后 45 分钟内的状态变动与四条新实测（03:20-03:50，仍在让路窗内＝零 CH 零跑批）

真态更新（6.1 的表不覆写，按留旧案卷另记）：

- q-…-**0006 已死**（02:53:52，死因 `GATE-PRECOMMIT-RUN`：落地前 ruff 在 staged 面判违规）。
  这不是内容错，是我先投了未 ruff-format 的旧字节；它的 10 件超集＝q-…-0013 已携终态字节在队，
  所以**不重投 0006**（重投只会让旧字节再落一次）。教训入 5 节同族：投前要跑的三门里，
  落地侧才生效的那一门（pre-commit run）以前只能靠死信学——今夜起我用
  `python -m pre_commit run --files <本袋 .py>` 在投前代跑（0013/0014/0015 涉及件已跑，exit 0）。
- q-…-0016 被 C1 同会话短窗自动合批并进 q-…-0014（回执 `C1-MERGED`），所以 0014 现在是 3 件（源码＋10 册＋班台账）。
- 新入队：0017（两册 register＋11 册）、0018（SFT register 单件，域不同另袋）。

队列算术（这是本班所有"代码在队不在 HEAD"的唯一原因，给 Owner 一把可核的尺）：

- 落地速率实测（done/ 里 landed_at 聚合）：30 分钟 2 袋、3 小时 13 袋＝**4.33 袋/小时**、6 小时 4.83、24 小时 3.38。
- backlog：pending=55（03:26），最老 172 分钟，中位 94.6 分钟；83 分钟内从 40 涨到 55（他班入队速率≈净 +11/小时）。
- 按 FIFO×15 分钟/袋估我的 9 袋落地时刻：0008≈06:15、0009≈09:45、0011≈11:45、0012≈12:15、0013≈12:30、
  0014≈14:00、0015≈14:15、0017≈17:00、0018≈17:15。
  两条前提写明：①新袋进队尾不推挤我的位次；②带 `--priority` 的会插队 ⇒ 上表是无插队口径。
- 结论对两条时限的意义：**LaneC 修件赶得上周一 20:00**（估 06:15）；
  而"机械四步"依赖的 0012/0013 要中午才落 ⇒ 我醒来时点建不了表、注册不了任务，这不是我没做，是链速决定的。

四条新实测/校正（细节与尺在 11、12 两册）：

1. **我自己说过一句假话**：03 册那句"实体挂 gpu_default/llm_local 互斥组"落不了地——生成器对 `sch_*`
   计划任务没有资源类别申报通道，实测册面 `sch_sft_train_window`＝light/default/无组/est=300。
   ⇒ 修法不是改生成器（越权），是三件 register 脚本改"缺省停用＋`-Enable` 才上膛"，11 册留痕。
2. **VRAM 预算册与令文不同轴**：`config/gguf_vram_budget.yaml`（MOD-INF-060）夜窗 15:30-08:30 配额＝**4.0GB**，
   而同册标 `qwen3:8b`＝5.4GB、14b 档＝9.2GB ⇒ 现产线本就长期超夜窗配额；R-4 的"≤8G"与这本册的"4G"
   我两把尺都报，不自行择一当合格线。
3. **GPU-01 令文的"单点换档"是假前提**：`MODEL_DEFAULT="qwen3:8b"` 硬写在 4 个脚本
   （lane_c2_agentic_miner.py:57／hypothesis_translator.py:59／graph_enrich_staging.py:54／irm_extract_batch.py:57），
   且四处都是 `OllamaChat(model=...)` 显式传模 ⇒ 环境变量 `OLLAMA_INFERENCE_MODEL` 对这四处不生效。
   定版真面目＝改 4 处常量或先做单点收口（后者属基建改造，不在本班授权面）。
4. **分片轮转我做了对照再定**：runner 用 `DayOfYear % 4`，而任务只 Sun-Thu 触发（跨周末跳 3 天）。
   40 夜实测：doy%4 四片占比 32.5/35/35/37.5%；"按星期映射"那版 27.5/27.5/27.5/**55%**（0 片被双日重复取）
   ⇒ 保留 doy%4，不是拍脑袋。另记一条固有近似：宇宙是当晚成交额 top-N，跨夜成员会变，
   "四夜一轮"覆盖的是 4×当晚宇宙，不是固定全集的稳定划分。

### 6.5 04:00 后三项实测回填（04:00-04:13，全部真跑，尺与失败通道都留在 12 册）

1. **R-4 冒烟（5 只票／零写表／≤25 分钟）**：rc=0，5/5 成功，分位五档逐票单调，热态 **0.43 秒/标的**
   （首票 3.22 秒含 CUDA 冷启）。显存：torch 进程内自计 peak allocated **126 MiB**／reserved **142 MiB** ⇒ 对
   "≤8G"是过，且差两个数量级。诚实定级：R-4 要的"逐进程真尺"里 NVML 两条通道本机判**不可归因**
   （A 路 usedGpuMemory 返回 WDDM 哨兵；B 路驱动侧行宽非公开头所写，解出的 pid 过不了正对照），
   pynvml/py3nvml 本机都没装（find_spec 双 False）⇒ 这个"过"只有 torch 一条真尺撑着。设备级 17966/24576 MiB
   只当旁证不当尺（在册教训：设备级被桌面污染）。
   副产品＝**R-3 首夜标定数提前拿到**：25 分钟约能装 3400 只票，而我按批复配的 top_n=300÷4 片＝每夜 75 只≈32 秒
   ⇒ 窗口是严重过配。要不要把 top_n 提到 1000-2000 级是扩产决策，我不自行放大覆盖面，列进菜单（新 G-11）。
   另注：本次是"主区 dev 码＋逐字内联车道 5 行尾窗切片"跑的——`vendor\Kronos` 与 `vendor\kronos_weights`
   只存在于主区工作树，车道里 `load_predictor` 必 RuntimeError（实测报的就是车道路径）。数值路径同一条，口径级别标清。
2. **W-1 前置量测＋正对照**：**execution_report 全库只有 1 行**（FINAL 与非 FINAL 都是 1），
   那 1 行 decision_timestamp=NULL、slippage_bps=**-10000.0**；`tick_depth_5` 有行的月份只有
   202607=48 行、202608=4 行、202609=1.30 亿行，**max trade_date=2026-09-30，10 月整月 0 行**，
   9-29 只有 1 行、9-21 只有 1.46 万行（窟窿日）。
   ⇒ 真实 replay 腿（M-2）的拦路石比 07 册写的更深一层：不是"obs 缺档口"，是**上游双重空集**——
   成交语料近乎为零，档级采集自 09-30 起断。"joinable_share=0.0"我不当结论用（语料 1 行＋时区语义未定，
   那 0 是我的算法和一行数据互相喂出来的）。
   两条后果：①B-007 材料包若要"真实流水"，前置是先把 execution_report 的写者与档级采集修回来；
   ②否则只能走合成盘口（现 env 的 book_provider 形态），且必须如实标合成。
   断采与无写者属数据/采集车道的账，本班只报数不代修——这条已进菜单（新 G-12）。
3. **GPU-03B P1 金标扩题草稿＋Owner 抽检包（真跑，rc=0）**：`gold-pack --target 40 --spot 60`，
   池 360 条（9 层×40，层内先按 stable_key 排序再截＝承 P0 可复现口径），教师 qwen3:8b 预标 **360/360，错误 0**，
   分布 positive 117／negative 55／neutral 188；产物两件套已随本袋入册：
   `data/eval/gold_expansion_draft_v1.jsonl`（360 条，human_label 全空）与
   `docs/_working/gpuwo_campaign/gold_expansion_spotcheck_pack.md`（60 行表，≥50 满足令文）。
   **没冻结、没训练、没跑 distill-train**——教师草稿只到"可抽检"，P1 的线在您判过之后。
   顺手一条环境观察（只报不改）：跑程中 LSG 打
   "AgentSecurityLayer：未传 hmac_key 且 ZEPHYR_L4_HMAC_SECRET 未设置，明确降级"＝L4 安全层此刻降级态。

菜单续编号（接 6.3）：

- **G-11 R-3 覆盖面**：实测热态 0.43 秒/标的 ⇒ 25 分钟可装约 3400 只票，现配 top_n=300 过配一个数量级。
  默认＝维持 300（不自行扩产）；若您要提覆盖，改 runner 的 `KRONOS_TOP_N` 与 `KRONOS_SHARD_COUNT` 两个环境变量即可，不动代码。
- **G-12 真实 replay 的上游前置**：execution_report 1 行＋档级行情 09-30 后断采。
  默认＝M-2 继续停线，B-007 材料包里"真实流水"一条改标"待上游补数据"；要不要立案修采集，归您与数据车道。
- **G-13 P1 抽检**：60 行抽检包在本袋的 `gold_expansion_spotcheck_pack.md`（也可读 data/eval 草稿全量 360 条）。
  默认＝不冻结不训练；您回填 human_label 并点头，才走"扩题升为冻结金标"那一步。

### 6.6 04:19-04:21 追加：单写者队列疑似楔死 ⇒ 6.4 那张 ETA 表作废，我上面那句"赶得上"收回

复测三数（同一分钟内取齐，尺=`commit_queue.py status` 与文件 mtime）：

- `processing/` 里 `q-20261012-st-deadcure3b-chief-20261011-0017`（**别班件**）袋 mtime 龄＝**215 分钟**；
  队头 `q-…-0018`（同班）已等 **12747 秒＝212 分钟**（00:46 创建）。
- `pending` 03:26 的 55 → 04:19 的 **62**；`done` 03:0x 的 746 → 04:21 的 **750**，
  即 03:2x 之后约 45 分钟里**落地 0 笔**（此前 3 小时窗均速 4.33 笔/小时）。
- 排空器活着不是熄火：`lease` state=drain-active、holder_pid=15100、alive=True、16 秒前刚续期，
  `belt_daemon.heartbeat` 龄 6 秒 ⇒ 形态＝**有节奏地卡在一袋的落地中段**（单写者被占住）。

顺带量到四枚陈旧 `.git/*.lock`（只报不删：清别人持的锁属锁主会话＋Owner 门位）：
`next-index-64212.lock` 2,542,018 字节、龄 **12945 分钟≈9 天**，而 `tasklist /FI "PID eq 64212"`
回"没有运行的程序匹配"；另三枚 0 字节 `tmpidx_precommit_{mq5pl6kd,w0zr79d0,w5nm0ulh}.lock`
龄 15648/26028/30903 分钟。**我不把"锁导致楔死"写成结论**——因果未证；只把龄期与体积入册，
醒来的第一只手若要清，按在册规矩先坐实持锁人已死（活性尺要与执行工具守卫同源），再动。

收回与改口（原文不覆写，按留旧案卷另记）：

- 6.4 那句"LaneC 修件按估 06:15 落地，赶得上周一 20:00"**作废**：它是按 4.33 笔/小时外推的健康态估计，
  而实测 03:2x 后 45 分钟落地 0 笔。楔死未解前，"赶得上"不成立，我先前据此给您的那条时限判断是错的。
- 6.5 三项实测不受影响（数字与产物都在盘上：冒烟 5/5、0.43 秒/标的、142MiB；
  execution_report 1 行＋档级 10 月 0 行；金标草稿 360 条＋抽检包 60 行）。
- 本班在队 10 袋：0008 0009 0011 0012 0013 0014 0015 0017 0018 0019（另有已死 0001 0002 0005 0006 按死因处置，0006 不重投）。
- 新增一条待裁 **G-14**：若楔死持续，"机械四步＋建表"应改为**下一班接手**而非本班收尾——
  这四步的前置是"件已在 HEAD"而不是"件已在队"。默认＝我不自行改令，等您或统筹一句话。

### 6.7 04:25-04:30 自挖自修一条：抽检包取样偏层（4/9），已改成按层轮转并重出

发现路径很偶然：我给抽检包做结构 QC（数行数、数空 human_label）时顺手数了一下"这 60 行来自几层"，
结果只有 **4/9 层**（crisis_2024 / normal_2017 / normal_2019 / recovery_2024）。
根因＝取样写的是"全量按 stable_key 排完再取前 spot 条"——排完序后前 60 名自然被少数几层占满。
这件事的分量：GPU-03B P1 的**唯一产出就是您那一句"冻不冻结"**，取样偏层就等于
"用三层的表现给九层的质量背书"，正是我在 GPU-03 那边反复抓的同一类错（口径不覆盖结论）。

修法（车道内，随件带守卫）：

- `build_distilled_sft_dataset.py` 新增 `pick_spot_sample(rows, spot)`＝层名定序 + 层内沿用 stable_key 序 + 轮转取，
  `render_spot_pack` 改用它，并把"实覆盖 N/M 层∶层名清单"直接写进表头（覆盖不足时包自己会喊）。
- 守卫 4 支（`tests/meta/scripts/test_distilled_sft_pipeline.py`）：每层都出现、轮转后各层 ≥15 条（偏样判败）、
  渲染逐字节可复现、spot 大于池时返回全池。实测 19 passed（本文件 13 ＋ P0 定序 6）。
- 重出＝**从已生成的 360 条草稿直接重渲染**（零教师调用、零 CH、零 GPU）：
  `python .runtime/tmp/gpuwo_regen_spotpack.py` 实测 pack 60 行、覆盖 9/9 层、human_label 60 行全空。
- 本袋带的是重出后的抽检包（同件后袋为准；q-…-0019 那袋带的是偏样版本，两袋按 FIFO 落，终态是本袋）。
- 一句自我更正的账：6.5 里我写"抽检包 60 行（≥50 满足令文）"——数量达标但**取样当时不达标**，
  那句在 04:25 之前是不充分的；现在这条才算完整。

### 6.8 裁定①（金标抽检有条件通过）执行实录——五步序全走完，冻结版已 hash 入册

Owner 10-12 终局裁定①给了执行序①→⑤，本班按序落，逐步留证据：

| 步 | 要求 | 实做 | 证据锚 |
|----|------|------|--------|
| ① | 按 7 行更正回填 | 7 条全部回填（方向 2：#24→中性、#47→利空；档位 4：#11/#12/#51→中性、#35→利空；置信 1：#15 0.85→0.60），`label_source=owner_correction`，教师草稿值留 `draft_*` 列不覆写 | 13 册（含行号↔包版本对齐证明：先取回 q-0019 的队列 blob 才敢认 Owner 数的行是抽检包 v2 的行） |
| ② | 360 道回填前先对"无方向目录/口号类标题"跑专项复核 | 复核跑在**冻结之前**：命中 9 道（本批 3/5 错同型＝教师系统性偏差），处置＝**只标不入金标**（隔离册），启发式只负责"标记"，永不负责"给标签" | 14 册 `quarantined_9_detail` |
| ③ | 360 道同规则回填→冻结为金标集 v1，hash 入册 | 守恒 351＋9＝360；来源 7 owner＋344 teacher；hash 见下"LF 口径" | `data/eval/gold_expansion_v1.jsonl` / `_quarantine.jsonl` / 14 册 `file_hashes_in_register` |
| ④ | #24/#47 改正前禁冻结；训练只认冻结版 | 改正已先于冻结（①→③ 的序守住了）；训练线读冻结版，禁边训边改卷写进 14 册口径 | 同上 |
| ⑤ | 冻结后开 GPU-03B 训练线 | `run_sft_train.py` 的三路径参数化（金标/训练/验证）在作，及格线 0.767 不动 | 6.9 末段 |

**hash 口径更正（我自己的错，留案）**：首次登记时三个 hash 是按**工作区 CRLF 字节**算的，而 git 落地会把
CRLF 归一成 LF ⇒ 在册值与真实仓内字节对不上，验收时必然"假红"。处置＝把两本 .jsonl 与 manifest 归一成 LF、
重算、把 14 册 hash 段改成 LF 口径（并保留归一前值只作连续性、明确标注"不作验收判据"）。
归一后（LF 字节）：金标 351 行＝`81c4f6ad…`，隔离 9 行＝`f41445fa…`，manifest＝`73886db6…`（未入仓，见 6.9）。
教训一句：**在册 hash 必须先问"落地后是什么字节"，不是"我现在盘上看到什么字节"**。

### 6.9 死机复位第二轮：三只死袋真因＝袋基底落在旧 HEAD，不是内容冲突（对在册一条加前置条件）

本机两次死机后复班，队列里出现三只死袋（0023/0025/0027），报的都是同一句
`[landing] 非注册表族件双侧皆改真冲突（整文件三方）`，点名件分别是
`register_sft_train_window_task.ps1`、`00_ledger.md`。按字面读会以为"别人也改了这两个文件、和我冲突"，
实测**不是**——是我自己的袋基底错了：

- 死机前这些件已由我的早先袋落到 dev（ledger 在 a8a19e2f63、ps1 在 a2c46fddca 之前那笔），
  但**车道工作树里它们是未跟踪件**（`??`），车道 HEAD 还是建道时刻的 a0e27b1ac；
- 入队时 base_head 取的是 `git rev-parse HEAD`（＝车道 HEAD）⇒ 基底树里**根本没有这两个文件**，
  而 dev 有、我的袋也有 ⇒ 落地器判"基底→dev 改了 ＋ 基底→袋也改了"＝三方真冲突。
- 判别尺（一条命令即可，零写入）：对每个点名件跑 `git cat-file -e <base_head>:<path>`，
  本例全部 N，而 `dev:<path>` 全部 Y ⇒ 是"基底缺文件"不是"内容打架"。

这与终清波三收班袋在册的那条同源（该册给"新建件先入队后落码／同会话后袋补救＝严格超集"两条加了前置条件：
仅在 base_head 与 dev 同源时成立）。本班补一个**更常见的触发形态**：*车道长期不推进 HEAD，但件已被自己的袋
落到 dev*——此时"未跟踪"叠加"旧基底"必撞三方冲突，且**内容做成 dev 严格超集也救不了**。
正解＝入队时显式 `--base-head $(git rev-parse dev)`（主区脚本、车道 cwd，配方见下），
基底树里有该件、base→dev 差为空 ⇒ 变单侧改动，快进落地。

超集性在重投前逐件实测（Counter 逐行差，禁肉眼）：ledger dev 81 行在车道 282 行里**零缺失**；
ps1 dev 73 行在车道 93 行里**零缺失**（多出的正是 -Enable 双闸那段）；
`run_sft_train_task.ps1` 车道与 dev **逐行全等**⇒ 不入袋（零变更不占提交）。

**LF 更正袋（0029）**：6.8 说的 hash 归一发生在 0028 入队之后，所以 0028 带的是归一前的字节；
本班不撤他不改他账，只做一件事＝以现字节（LF）重投一袋，后袋胜。manifest 仍**不入袋**：
CREATE-GUARD 要新建 .yaml 的 token，而 `batch_creation_tokens.py --prefix data/eval` 实测会把
他会话的 3 件一起扫进（宽前缀拒批），文件名级前缀零命中，`register_asset.py` 对不存在的路径报
"OK 五道手续完成"而 PG 查为零行（在册假成功形态）⇒ 改为把 manifest 内容整段内联进 14 册，
盘上留件、册上留 hash，等 G-1（维护三班 C4 投影/render 路）落地后再正式入册。

### 6.10 裁定①⑤（训练线开跑）执行态：线已接通并逐项实测，**最后一道闸本班不代签**

Owner 裁定①⑤ 要的是"冻结后训练线开跑，训练窗/互斥组/reaper keep 照在册，及格线 0.767 不变"。
本班把"能跑"做完了并逐条实测，但**没有**自己去按那个按钮，理由写在下面第三段。

已接通（三件，q-…-0029 一袋，D_ML_TRAIN）：

1. `scripts/ml/run_sft_train.py` 加四面旗 `--train-path/--eval-path/--gold-path(多本)/--pass-line`，
   **默认值逐条指回原常量**（含 pass_line=0.75 这个 Phase 8 现产线口径）——
   实测绿 A：单册默认 `rows_kept=200 == 文件行数 200`，册内那对逐字重复题
   （`c8b90cf1fcb0cc9650dae06b65dc6b40`）原样保留、只登记进 report 的 `intra_file_duplicate_ids`。
   为什么不敢顺手折叠：折叠＝把现产线 Macro-F1 的分母从 200 悄悄改成 199，
   那就是"以修 bug 之名行改判据之实"，与本_campaign 反复抓的那类错同源。
2. 新增 `merge_gold_rows` + `assert_no_gold_leakage`：金标扩充册字段是 `human_label`、
   原 200 集是 `sentiment`（词表相同），只改键名不改值；跨册同题标签打架 / 缺标 / 词表外 /
   无 news_id / 空册 / 训练面含金标 ＝ exit 2 且**训练不启动**（金标校验排在训练之前）。
   实测绿 B：两册 551 行进 → 551 条评估面，蒸馏训练池 3240 条 ∩ 金标 551 条 = **0 条**；
   实测红 D：七条各起一个子进程，七次 rc=2 全中（脚本 `.runtime/tmp/gpuwo_sft_entry_probe.py`）。
3. 包装器 `run_sft_train_task.ps1` 段1 改走蒸馏线并加两道前置：蒸馏池不在盘＝SKIPPED exit 0、
   **冻结金标不在盘＝DENIED exit 1**（不许拿未冻结集算分）；三道旧闸（01:00-04:00 让路／
   授权文件一次性消费／GPU 占用门槛）一字未动。
   实测绿 C（引号真穿透）：按包装器同款 `cmd.exe /c "python ... ""path"" ..."` 形式跑红路，
   rc=1 且日志回显我的绝对路径＋`eval=360` ⇒ 五面新旗真的进了 argparse，
   顺带证明 torch/transformers/datasets 在本机可导入（周日真跑的依赖面不是空的）。
   另修一处**会把 Owner 引错的注释**：闸门真读的授权文件叫
   `data/runtime/sft_train_authorization.txt`，旧注释写成 `sft_authorization.txt`——
   照注释建文件＝窗 armed 但永远 no-op。零逻辑改动，只把指针改对。

照在册的两处配套：

- 蒸馏训练池按 `data/sft/` 既有惯例＝**盘上派生物不入 git**（.gitignore:412，
  `data/sft/train.jsonl` 今天也在盘上而不在仓里）。字节已落主区并在册（LF 口径）：
  `distill_train.jsonl` 3240 行 3,168,831 B = `071680b0a4e5b640c813514b4216d63c2516def5847c26ad42000cffc948cbe8`；
  `distill_eval.jsonl` 360 行 443,273 B = `a1e434cacccf144d36c0b65587b7fe13f2bd2a2333493a08ae88757b7657552d`。
  金标 v1 相反＝**入 git**（裁定①③ 要的是"hash 入册"的可复核集），两件事分开记不混。
- reaper keep：给"今晚会真跑"的那批登记，没跑的不登记（在册"防误杀"是给在途批的，
  提前写＝给一条不存在的批发免死牌）。本班只追加一行
  `kronos_adapter.py --score-only`（附名目与时刻），写的是主区 `data/runtime/process_reaper_keep.txt`
  ——该文件未入 git（`git ls-files` 查无），追加＝本机运行态动作，不占袋。

窗口三件的真实现场（20:5x 实测，全部 `Get-ScheduledTask` 读回，不是"我以为注册了"）：

| 任务 | 注册 | 上膛 | 下次触发 | 本班判断 |
|------|------|------|----------|----------|
| `ZephyrAlpha_KronosScoring` | 已注册（00:30 Sun-Thu，OS 时限 35min） | **已 -Enable** | 2026-10-13 00:30 | 22:30 批 est 30min→23:00 收，LaneC 20:00→00:00 收，00:30 起无重叠；包装器 25min 封箱⇒00:55 前让路 |
| `ZephyrAlpha_NightMining` | 已注册（23:00 Sun-Thu，2h） | **本班主动 Disable（不上膛）** | — | 钟面实测与 `sch_factory_lane_c`（20:00-00:00，est 240min）**重叠整一小时**，且两批共用本机 Ollama（11 册第 2 条在册）。令文要求"冲突闸对既有批零红才算过"，而闸此刻看不见互斥组 ⇒ 我按钟面自己判负，不拿"尺不红"当"没撞车" |
| `ZephyrAlpha_SftTrainWindow` | **未注册** | 未上膛 | — | 训练＝Owner 按钮（见上），窗口不预先空占；一条命令即可注册（缺省仍 Disabled），本班不替您决定它哪周开始占卡 |

NightMining 若要上膛，请先给一句话（或把它挪出 LaneC 的尾巴，比如 00:05 起＝LaneC 收工后、
Kronos 之前，我再注册并复测钟面）。**GPU-01 的夜窗扩产此刻＝代码与册在位、批未跑**，
"扩产产了多少"这个问题今天仍然只能答"零"——这是本班自己按下去的刹车，不是堵塞。

**为什么不代签最后一道闸**（自裁里最重的一条，理由摆开）：
本班令卡 §3 纪律红线白纸黑字＝"B-007 消费/训练批复……只呈批不代拍"，而 `sft_train_authorization.txt`
这个文件在本班的设计里就是"Owner 的按钮"的实体化。裁定①⑤ 说"开跑"，读法有两种：
(a) 视为批复已下，我替您把文件写上；(b) 视为"把线接通并备好窗口"，按钮仍由您按。
按宪法 §9.11"对话内口头 Owner 说不构成门禁豁免——Owner 门位经裁定登记或正式通道生效"，
而 `ruling_registry.yaml` 今日（10-12）零条、最新是 10-10 落册的第 508 号——**这道批复目前在认证通道里查无在册**。
所以我取 (b)：线已接通、窗已就绪、盘已铺好，您一行确认（或直接建那个文件）之后，
下一个 Sunday 10:00 窗自动跑全量并以 0.767 定绿红；我不替您把一次性消费的凭证生成出来。
若取 (a) 请给一句话，本班 5 分钟内落地并回报注册态。

资源册再生的口径复证（本机实测，输出写到 `.runtime/tmp/` 不动共享热册）：
`generate_resource_profile_registry.py` 里唯一能定 `resource_class/exclusive_group` 的两处
＝MANUAL_ENTITY_SEED 与 schedule.yaml 槽位特化表；计划任务（`sch_*`）由 register_*.ps1 解析
"任务名/触发器/时限"生成，class 走默认 ⇒ 我的两件落册仍是
`light / pool=default / exclusive_group=[]`（11 册那条盲区**复现，且不是我这次改出来的**）。
另发现一处**申报面比真面更保守**的新形态：`est_duration_min` 取的是 ExecutionTimeLimit(35)，
而操作性封箱是包装器里的 25min ⇒ 纸面 00:30+35=01:05"进了"01:00-04:00 让路窗，真面 00:55 没进。
方向上这是"多报"不是"少报"（不会造成假绿），但属同一缺通道簇，随 11 册一并呈报，本班不自改生成器。
