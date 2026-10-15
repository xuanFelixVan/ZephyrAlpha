---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑤实现席·findings台账
---

# findings 台账（追加式，禁删改他人行）

格式：`## <MM-DD HH:MM> · <一批摘要>` + 要点若干 + 自检结论（两轮）。

## 10-15 07:50 · 班次 01（st-qoder-p05-1015-01）首班固定施工单四件核账 + M5 接线卡解锁

实测耗时：约 85 分钟（超 75 分钟班窗，超出部分用于把自造 hang 的用例改对拍，记档）。

### 首班施工单四件：三件核销、一件改道

| 件 | 现状实测 | 处置 |
|---|---|---|
| ① signal_orthogonality.py gate rc=1→5 | 合成数据 CLI 实跑三态：reject `rc_A=5`、同 stem 自比 `rc_B=5`、独立候选 `rc_C=0`（`.runtime/tmp/st-qoder-p05-1015-01/smoke/`）；worktree 字节 sha `c5ca6d5ca68c70f5`，index 面 `09fbf878aa15cd37`（修复前） | **核销**——修复字节已在册他班袋 `q-20261015-st-ibtclose-20261015-0003`（04:27 建，blob=worktree 逐字节同），本席不代投、不重投（承在册处方：搁浅面让它死勿 requeue） |
| ② goal_readiness_aggregator.py 第 69 行老册指针 | 仍指 `docs/03_modules/_domain_backtest/exam_scores_v1.yaml`（该件在 HEAD 在册、磁盘已无=他班 staged 删除 `D `）；新册 `docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml` 磁盘现值 115036B 而 **不在 HEAD**；行 126 用 `yaml.safe_load` 单文档读（新册实为多文档，⑨席 04 班按 `safe_load_all[1]['rows']` 消费） | **改道呈批**——本件不在本席落地面：`?? untracked`＋无在途袋＋`dead/` 内 `st-infoaxis-20261013` 死袋 26 笔（死因一律 CREATE-GUARD「新建 src/zephyr .py 未申报挂图面 MAP-MOUNTS」）。单行改指针=把他人 26 次死亡原因整件接到自己袋上，且其测试件 `tests/data/test_goal_readiness_aggregator.py` 磁盘已无（只活于队列 blob）。判据与替代路径见下"呈批" |
| ③ 四闹钟 runner [ARTIFACTS] 注记 | NightMining/F06Grid/TTLRejudgeDaily/C4Exam 四件头部均已有 `[ARTIFACTS]` 具体产物路径，逐条对齐 SOP §8-A 表（含 C4Exam 增量分数行→`docs/04_research_records/backtest/scores/<YYYY>/`、TTL 禁旁路） | **核销**（四件均 `MM` 在途态，本席零动） |
| ④ p11_assembler pool 桥接 yaml | `scripts/tasks/run/run_assembler_nightly.ps1` 为 `?? untracked`（st-ibtclose 班产物，其 `q-…-0003/-0004` 在途袋含 fexam 件），桥 yaml 的消费端与 pool CSV 物化腿同源未落地（⑨席 04 班修⑤正解：闸只吃 `date,sig`，采集面产 `trade_date,value`，列名契约一行之差） | **挂起**——与①同件面（orthogonality/ibt 在途），本席不撞；移交见下"移交" |

### 本班真交付：领单 `TDM-P-P1-03/comparison/03`（39 张 blocked_on_impl 之一，missing=M5 维注册＋run 路径接线）

- 改动面三件：`scripts/backtest/factory_grid_executor.py`（evaluate_recipe 序钉末位接 `_apply_thesis_survival_overlay`，`thesis_mode` 字符串档→float）、`config/position_recipe_grid_schema.yaml`（加 `M5_thesis_survival` 维＋revisions 一行）、`tests/research/backtest/test_m5_thesis_survival_wiring.py`（新，10 用例）。
- 折叠闸选 `active_if: "False"` 而非卡面建议的 `phase >= 3`，两条实测红面为据：挂 phase>=3 ⇒ `test_charter_v2_schema_nominal_counts` 等钉死 phase2/3 名义数的在册用例转红；挂专用 context 键 ⇒ 自建 ctx 调用方集体撞 `[ZA-POS-0045] active_if 求值失败`（编译器 fail-closed，本席先犯后改）。真源处方=executor `_resolve_grid_schema` docstring「新档须走 --schema-path 探针册，共享册数字零动」。
- 顺带机械补一行在册用例的期望维度名集（`tests/trade/position/test_position_recipe_compiler.py`，照 10-08 X_sector 同款先例留注），非挪判据门柱。
- 实测读数（正文原样跑）：`PYTHONPATH=src python -m pytest tests/research/backtest/test_m5_thesis_survival_wiring.py tests/research/backtest/test_t3a_grid_s_wiring.py tests/research/backtest/test_sector_surface_wiring.py tests/trade/position/test_position_recipe_compiler.py -q` ⇒ **102 passed**（本席 10＋邻座 92 零回归）。
- 本席自犯并当场改正两处（留案勿再犯）：①三条语义用例期望值一度按脑估写（`combined` 与 `weights` 列面不一致还触发 pandas object dtype `~` TypeError）⇒ 改为先实测读数再落期望；②新用例在 phase=3 真源面上 `compile()` 整表铺 13M 格点自造 hang（>5 分钟）⇒ 改 `count_n_raw`＋`_evaluate_active` 零展开对拍＋HEAD 册字节对拍（他人套件 INVARIANTS 早钉过这条，本席没先读）。

### 移交

- →⑥制卡席：`TDM-P-P1-03/comparison/03` 已翻 `status: preregistered`（卡面注释留施工位与偏差依据），三臂开考需经探针册展开 `M5_thesis_survival` 值集或 recipe.values 注入——注入接口若要⑤席补（如卡面 arms→dim 的映射器），下班领单。
- →⑩线长席：本席判 ⑤席无权重写 `goal_readiness_aggregator.py`（他人 26 笔死袋的 MAP-MOUNTS 死因未清），建议归 infoaxis 车道或由 ⑩ 指定唯一纠正出口。
- →⑨成绩官：修⑤正解（`trade_date→date`/`value→sig` 列名映射＋池谓词逐对交集报错点名）落在 `signal_orthogonality.py`，该件本席见到在途袋 `st-ibtclose-0003`，等其落地后下一班接。

### 自检两轮

- 轮1：改动面 grep 复量——`grep -n "M5_thesis_survival" scripts/backtest/factory_grid_executor.py config/position_recipe_grid_schema.yaml` 命中接线位＋册维定义；`git status --porcelain` 本席件清单与袋内 files 一一对应，未含他人 `AM/ M/??` 在途件。
- 轮2：邻座回归 102 passed（同上文原样命令）；卡面判据/冻结窗/三臂定义字节未动（只加注释与 status 行）；折叠零漂移有 HEAD 册对拍用例钉住（非本席口头声明）。

## 10-15 10:10 · 班次 02（st-qoder-p05-1015-02）修⑨ 收口＝裁定#506 G1 净费参数面落地；附本席台账被外部重置的抢救留痕

实测耗时：截至本条落笔 09:05:32→10:10＝约 65 分钟。分账＝例行（冷启动/领单核实/施工/自证）约 40 分钟，返工与取证约 25 分钟（他班 7 红归因实验 ≈12 分钟、本席台账被抹的取证与抢救 ≈13 分钟）。

### 领单＝⑨席 04 班修改单 修⑨（series 路净/成本面未产，而毛面读数挂进"门柱"）

- 根因实测（非引用）：`config/exam_scale_cost_gate.yaml` 磁盘面顶层 11 键，**无 `net_fee`**；消费腿 `scripts/backtest/fexam/calibration_exam.py:102 _round_trip_cost_bp()` 读 `data["net_fee"]["round_trip_cost_bp"]`，异常分支返 `nan`（docstring 自陈"缺 net_fee 节属合法态"）⇒ 全册 `net_bucket_medians`/`round_trip_cost_bp` 恒 NaN，而 `mono_spearman` 照常有值＝**毛面读数过柱**（⑨席在册症状）。
- 授权面：裁定#506（`docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml:4505` 段，status=active，2026-10-10）明文"参数入 exam_scale_cost_gate.yaml net_fee 节唯一参数面，禁硬编码"，`affected_files/approved_paths` 均含该册 ⇒ 本席有写域。⚠ 该裁定自报 evidence 写"config/... net_fee 节"，与 10-15 实测盘面不符（节缺席 5 天）＝**自报证据未经内容核**，在册教训"存在性≠内容判据"复现。
- 撞车判定（开工前实测）：该册 `git status` 干净＋全 pending（103 袋）**零袋认领**；消费件 calibration_exam.py 有两只在途袋（autoplan-0005/scorehome-20261014-0003）⇒ 本席**只动参数面不动码**，且实测三个面（HEAD／主区 worktree／两只袋 blob）的读取键路径逐字符同为 `net_fee→round_trip_cost_bp`，无论哪版落地均兼容。

### 交付面（两件）

| 件 | 动作 | 自证读数 |
|---|---|---|
| `config/exam_scale_cost_gate.yaml` | 末尾**追加** `net_fee` 块（形制沿用裁定#435/#446 追加块先例） | `git --no-pager diff --numstat`＝**43 增 0 删**；键集合差＝新增 `['net_fee']`／删除 `[]`；既有 11 键逐一 deep-equal＝True |
| `tests/backtest/test_net_fee_param_face.py`（新，tests/ 依 CREATE-GUARD 豁免） | 7 用例：参数面存在／与引擎常量对拍／消费腿读真册／缺节→nan 负对照＋有节→12.5 正对照／合成面净桶逐桶==毛面−25bp／打桩 nan 反证净面真依赖参数面／judge() 有无净面同 verdict | `PYTHONPATH=src python -m pytest tests/backtest/test_net_fee_param_face.py` ⇒ collected **7 items**，**7 passed in 8.28s** |

- 数值零自创：`round_trip_cost_bp: 25.0` ＝引擎冻结土规常数的组合解。真源=`scripts/backtest/translated/_c4_engine.py:64-66`（`COMMISSION_BP=2.5/STAMP_BP=10.0/SLIPPAGE_BP=5.0`）与其 cost 式 `cost = turnover*(COMMISSION_BP*2 + STAMP_BP + slip*2)/1e4` ⇒ 2.5×2+10.0+5.0×2=25.0；测试件按 AST 读引擎常量重算并对拍册面值（禁双头硬编码，一侧漂移即红）。
- 两处**如实登记未修**（写进册内注释，非口头）：①口径差异＝消费腿"每桶固定减 25bp"不乘换手，引擎是 `turnover×标量`，二者何时统一属呈批面；②最低佣金 5 元/名义额 20 万两键今天＝登记面非计算面（`_round_trip_cost_bp()` 无名义额形参），接线须动在途件，设计稿见 `feedback/to_impl.md` 本席 02 班条。
- 判据零挪动：`net_bucket_medians` 在 calibration_exam 全文**只出现 1 次**（metrics 构造位），`judge()` 不消费；`05_owner_decisions.yaml` 在册注"不进 judge()"；并有第 7 号用例做行为级自证（有净面/无净面 verdict 全等）。

### 突变自证与归因实验（本席不采信"我以为无关"）

- 能红证明：`git checkout HEAD -- config/exam_scale_cost_gate.yaml`（撤本席块）⇒ 同命令 **4 failed, 3 passed**，失败正文含 `AssertionError: 净费读数非有限值：nan`＝**修⑨ 症状在测试面上复现**；恢复快照后 sha256 前缀 `89474f03b49c1940` 与改后记录值逐位同，再跑 **7 passed**。
- 邻座串跑：`PYTHONPATH=src python -m pytest tests/backtest/test_net_fee_param_face.py tests/backtest/test_calibration_exam.py tests/research/backtest/test_factory_grid_stage_cost_tiers.py tests/backtest/test_card_binding.py` ⇒ **7 failed, 200 passed in 85.31s**。
- 归因实验：再次撤本席改动后单独复跑他班两件 ⇒ **同样 6 failed**（`TestApplyPreregBudgetCompat`/`TestRunBatchStageCostWiring`，正文 `Failed: DID NOT RAISE <class 'SystemExit'>`，且 `scripts/backtest/factory_grid_executor.py` 为 `M ` 在途态）⇒ 六红与本席无关，属他班在途面。第 7 红 `test_card_binding::test_real_book_carries_07_and_07b_variant_vocabularies`（`docs/_working/mineloop_campaign/02_binding_book.yaml` 不存在）在归因复跑中**自行消失**＝他班正在写该件的瞬时态，非本席造成。

### ⚠ 事故留痕：本席台账与游标被外部重置回 HEAD（班次 01 未落地内容一度全失）

- 现象：09:26:21 `p05_impl/ledger.md` 6004B→**255B**、`checkpoint.md` 695B→**223B**，两面与 `git show HEAD:` 字节数一致且 `git status` **clean**＝工作树被重置（非本席改写、非队列回退）。班次 01 的交付记录只活于在途袋。
- 抢救（四步：快照→精确谓词→单口→读回）：谓词＝袋 `q-20261015-st-qoder-p05-1015-01-0001` 的 `files[].path` 精确等值；从 `.runtime/commit_queue/blobs/` 取件并核 `blob_sha256` ⇒ ledger `93ca3ad608d359b8`／checkpoint `b2f7221316616065` **MATCH**；`cp` 回工作树后逐文件独立哈希＝disk 与 recover **MATCH**（两件各自一条，禁"整批成功"叙述）。
- 纯增量自证：ledger 对 HEAD 非空行 **缺 0 行**；checkpoint 差 4 行＝游标字段（cursor/last_run/last_batch/notes 行）被班次 01 改写，游标本非追加面，预期内。
- 上报：本席不追他班重置来源（属 ⑩ 线长席串行/审计域），只登记事实与抢救路径；班次 01 台账随本席袋重新入册（本席袋＝其内容超集，即便其原袋四态全无，记录不再依赖单一存活处）。

### 移交与续挂（一律附实测依据）

- →⑩线长席：①本席两件四件套面被重置一次，建议把 `docs/_working/automation_campaign/p*/` 纳入重置白名单核查；②在册件 `src/zephyr/data/goal_readiness_aggregator.py`（首班施工单②）今日复测仍 `?? untracked`／NOT IN HEAD／**全 pending 零袋认领**，本席仍不接（他人 26 笔 MAP-MOUNTS 死因未清，宪法 §3.4 他会话在途不代修）。
- →⑨成绩官：修⑨ **参数面与净面产出已收口**；余下"口径统一（固定扣费 vs turnover 缩放）"与"最低佣金代码腿"两条本席按纪律不代裁、不自接线，随设计稿呈批。
- →⑤席下班：修⑤ 列名契约件 `signal_orthogonality.py` 今日复测仍被两只在途袋认领（`st-orthogate-0001`/`st-ibtclose-0003`）⇒ 续挂不撞；修⑥/修③ 申报腿与写分工具 `calibration_exam.py`（在途双袋）同件面，须待其落地；修⑦ 与呈批 P-3（`event_days_min` 作用窗未裁）纠缠 ⇒ 只可出设计稿，禁自行补腿。
- 净零：零新规则册、零新 gate、零新参数册（参数入**既有唯一参数面**）；新增测试件替代"裁定自报证据而无实面"这一虚账。

### 自检两轮

- 轮1（改动面 grep 复量＋归属核对）：`git status --porcelain` 本席五件＝config 册 ` M`、新测试件 `??`、ledger/checkpoint ` M`、`to_impl.md` ` M`；`grep -n "net_fee" config/exam_scale_cost_gate.yaml` 命中块头与消费键；`grep -n "net_bucket_medians" scripts/backtest/fexam/calibration_exam.py` 仍＝1 处（本席未碰码）。他班在途件（`M `/`??` 面 5390 漂移件）一律未入本席袋清单。
- 轮2（内容与判据面）：净费数值＝引擎常量 AST 对拍通过（用例 2）；judge 不消费净面（用例 7 行为级）；缺节→nan 负对照通过（用例 4）；配置纯增量有 numstat 与键集合差双证；台账恢复有 blob sha 与盘外哈希双证。

## 10-15 09:40 · 班次 02 自更正（留旧案卷不删，另起此节）

本节只更正本席自己的两类假账，不改任何判据与交付内容。

- **时间账（体感钟第 N 次快一倍）**：上节标题写"10:10"、耗时写"约 65 分钟"，均为落笔即假。实测锚：冷启动首命令 09:05:32（`process_reaper --status` 打印）、袋 `created_at=2026-10-15T09:39:51+08:00`（机生）、本更正落笔 `date` 实测 **09:40**。⇒ 班次 02 真实跨度＝**约 35 分钟**（不是 65）。分项不再自估，改列机时实测：`pytest` 五段 8.28s＋11.23s＋10.52s＋85.31s＋50.93s＝**166s**，`git_commit` 预检白烧一次 **191.2s**，其余为读档与判断。
- **重置根因线索（补上节"事故留痕"，非推翻其现象）**：`date` 复量发现 dev 在本席施工期间前进一笔 `14f18f6271`（提交/作者时间 **10-15 09:38**，"[docs-only][归档 st-docconsol-20261014] docs/_working/** 全量归档至 docs/_archive/（4,793 条目，零删除）"）。本席用 `git show --name-only 14f18f6271 -- docs/_working/automation_campaign/p05_impl/` 实测＝**该批未点本席四件套任一文件**（内容面未动），但本席 09:26:21 被抹与该归档批落地同窗。⇒ 上节结论（工作树未落地内容一度全失、已从袋 blob 抢救）不变，**新增归因线索**：嫌疑面=归档批落地过程对工作树做过复位类动作（`git stash`/checkout 家族，reaper 报 `stash_count=2`），归属 ⑩ 线长席审计域，本席不追。本席袋 `base_head` 已随该批前进＝`14f18f6271`（经 `merge-base` 双判＝与 dev 同点，非影子基底）。
- **预检死因与新知（写进卡才不再白烧）**：本班第一次 `git_commit.py --enqueue` 被 PREFLIGHT 双拦＝`[SESSION-REQUIRED]`＋`[WORKTREE-REQUIRED]`，白烧 191.2s。正解与在册一致：SESSION-REQUIRED 走**注册**（`session_worktree_start(sid, allow_workspace_drift=True, allow_concurrent=True, task_files=[...])`，注册后 `.runtime/session_registry/st-qoder-p05-1015-02.json` 与车道 `.aidrafts/st-qoder-p05-1015-02` 均实测在场），WORKTREE-REQUIRED 走 `--allow-non-worktree`（2026-08-13 裁定 AI 可自决）。⇒ **建议 ⑩ 把"冷启动第 0 步＝session_worktree_start 注册"写进 ⑤ 席指令卡**：本席指令卡三步只列 ENV/lock cleanup/reaper，两班连踩同一坑（班次 01 的袋讯息里同样自陈"降级登记原因＝冷启动三步未含 session_worktree_start"）。
- **本班残余（如实）**：①新建车道 `.aidrafts/st-qoder-p05-1015-02` 为空checkout（本席改动在主区，车道未用于施工），按"收班即清"本应归档，但 `session_worktree.py archive` 会对同 sid 做死判与分支删除，而同 sid 有在途袋 ⇒ 保守**留给 ⑩ 或下一班在袋落地后清**，此处登记不假装已清；②`lock_files.py` 五件 claim 未 release（TTL 7200s，袋已入队即由队列侧接管，收班补 release）。

## 10-15 09:45 · 班次 02 二次自更正：配置册也被同一波重生洗掉，两只袋吸到的都是模板面（差点假交付两次）

- 触发：入队 -0002 后本席按纪律复跑交付命令，`PYTHONPATH=src python -m pytest tests/backtest/test_net_fee_param_face.py` ⇒ **4 failed, 3 passed**（与突变态同签名）。⇒ 判"已交付"只能靠落地实测复跑，不能靠入队回执。
- 三面对拍定案（正文可复跑）：盘 `sha256sum` 与 python hashlib 同为 `1592ee74e0026fab`、`git show HEAD:config/exam_scale_cost_gate.yaml | sha256sum` 亦 `1592ee74e0026fab`、盘 `stat`＝6932B／mtime **09:27:39** ⇒ 配置册在 **09:27:39** 被洗回 HEAD 面，与本席四件套 09:26:21 被洗**同波**（外来重生波扫 `docs/_working`＋`config`，非仅台账面，上节"嫌疑面"据此扩面）。
- ⚠ **两只袋都不含本席交付**：`-0001`（09:39:51）与 `-0002`（09:44）内 `config/exam_scale_cost_gate.yaml` 的 blob sha 前缀均＝`1592ee74e002`＝被洗后的 HEAD 面 ⇒ 若照此落地，`net_fee` 节**不存在**，净费参数面等于没做；而 `-0001` 袋内讯息自陈"5 件 blob 与盘面对拍全 MATCH（1592ee74e002/…）"——**当时该断言为真，但盘面已是模板面**＝"存在性≠内容判据"的活案例，与在册新账 `p09-seat-files-external-regen-wipe-20261015`（⑨席同型）在 ⑤ 席复现。
- 唯一存活处与恢复（双源在册）：自留快照 `.runtime/tmp/st-qoder-p05-1015-02/net_fee_backup.yaml`（10353B、mtime 09:22、sha `89474f03b49c1940`、含 `net_fee`）⇒ `cp` 回位后盘 sha＝`89474f03b49c1940`、`net_fee` 在、顶层 12 键、`round_trip_cost_bp=25.0`；复跑交付命令 ⇒ **7 passed**（09:45 实测）。测试件盘面未受灾（7366B、mtime 09:21、`grep -c "def test_"`=7）。
- 另投 `-0003`（同 5 件，config 为含 net_fee 的正确面，ledger/checkpoint 为本节之后的超集面）；**留档防再洗**：快照＋两份袋讯息（msg.txt/msg2.txt）全留在 `.runtime/tmp/st-qoder-p05-1015-02/`，若 -0003 再被洗，下一班按在册处方"队列 blob ＋ 自留快照双源重放"。
- 时间账第三次落笔（每次都以 `date` 实测为准）：09:45；本班跨度 09:05:32→09:45 ≈ **40 分钟**。

## 10-15 10:47 · 班次 03（st-qoder-p05-1015-03）领单＝class D 装载口搬迁缺陷＋修⑪ 回落声明观测腿

实测耗时：冷启动首命令 `date`＝10:20:46，本条落笔 `date` 实测＝**10:47:22**，跨度≈**27 分钟**。（落笔即时更正：本节初稿标题写"11:15"、跨度写"≈54 分钟"，都是体感钟落笔即假——第 N 次同型，旧读数留此不删。机时分项实测＝pytest 四段 46.97s＋60.97s＋41.48s＋52.25s≈202s，`session_worktree_start` >120s 转后台，邻座回归 54.92s＋37.03s。）

### 领单依据（两条在册复证＋一条新单附问，均附本机实测）

- **缺陷面（⑦A 班 ledger:52-53/181 与 ⑧B 班 ledger:51 在册复证，HEAD 上未修）**：`card_binding.py:74 SERIES_DIR` 指 `docs/_working/nightmine_campaign/series`，而 10-15 研究资产搬迁已把该整目录搬至 `docs/04_research_records/mining/ledgers/nightmine_20261010/series`（登记位=`docs/04_research_records/_index/index.yaml:9864` 的 `dir: mining/ledgers/nightmine_20261010/series`）。本班进场实测＝**装载口整条死**：`SERIES_DIR.exists()=False`、`_CSV_HINTS` 去重 15 枚文件 **0/15 可解**、真卡 `09_limit_up_count_derived` 判 `U:series_csv_absent:limit_up_count.csv`、真卡 `41_agg_lu_count_z20_fwd10` 判 `U:series_csv_absent:lu_count_z20.csv`（两张 status 均 examined＝旧面曾跑通，现面不可复现）。
- **修⑪ 附问 (c)（⑨席 08 班新单）**：`*_derived` 名称回落在三面（卡面/册面/码面）零声明。本班实测该分支确实把平行卡绑到母序列（见下"内容级实证"），属**观测缺失**、非判据问题 ⇒ 本席只做申报面，不裁"算不算两次独立考试"（P-5 题面在 ⑨席，路由 ⑩＋Owner）。

### 撞车判定（开工前实测，一律附读数）

- `scripts/backtest/fexam/card_binding.py`：袋面 18 done／1 dead／**pending+processing=0**；三面同字节（disk=index=HEAD=`7b366fe297a3`）⇒ 本席可安全施工。
- `tests/backtest/test_card_binding.py`：17 done／1 dead／**live=0**，盘面 clean ⇒ 同袋追加。
- 不接件实测：`calibration_exam.py` 仍 2 只 pending（autoplan-0005／scorehome-0003）；`signal_orthogonality.py` 仍 2 只 pending（orthogate-0001／ibtclose-0003，盘面 `AM`）⇒ 修⑤/修⑥ 续挂不撞。
- 首班施工单复核：①signal_orthogonality rc（他班袋在途，核销续挂）②`goal_readiness_aggregator.py` 仍 `?? untracked`＋11 只 dead 袋零 live ⇒ 仍不接（他班 26 笔 MAP-MOUNTS 死因未清）③四闹钟 [ARTIFACTS] 上班已核销 ④p11 pool 桥接 yaml 与①同件面 ⇒ 挂起。

### 交付面（两件，均为在册件改动、零新建 ⇒ 无 creation_token）

| 件 | 动作 | 自证读数 |
|---|---|---|
| `scripts/backtest/fexam/card_binding.py` | ①`SERIES_DIR` 改指永久区真源（不留旧路候选位＝不给已废止临时区留活口，根宪法 §9.4）②`classify_card` class D 分支拆"精确申报／`*_derived` 名称回落"两形，回落时在机判输出挂 `caliber_fallback{declared_signal_column, resolved_file, series_root, statement}` ③`build_signal` 的 `local_series_csv` 凭据面并上 `series_root`＋`caliber_fallback` | 改后盘面 sha=`4e9fabc8694840ed`；**判据零改动**：`|corr|`／阈值／门柱键集 `JUDGMENT_KEYS` 未碰，`U:series_csv_absent:<file>` reason 字符串逐字符照旧（既有 1413 行用例钉过）；绑定结果面零变化（回落照旧绑母文件，只加声明） |
| `tests/backtest/test_card_binding.py` | 追加 7 用例（红蓝双证＋真卡字节内容级） | `PYTHONPATH=src python -m pytest tests/backtest/test_card_binding.py -o addopts="" -q -k "<本组六条谓词>"` ⇒ collected 114 中 **7 passed**；全文件 ⇒ **113 passed / 1 failed**（唯一红＝他班在途件，见下"如实登记"） |

### 内容与判据自证（正文可复跑，禁脑估）

- **改后真面读数**：`SERIES_DIR.exists()=True`、**15/15 hint 可解**、真卡 09 ⇒ `cls=D op=file=limit_up_count.csv` 且带 `caliber_fallback`，真卡 41 ⇒ `cls=D op=file=lu_count_z20.csv` 且**无**回落键（精确申报形）。
- **内容级实证（修⑪ 的"同一枚 CSV"从推断变实测）**：`cb.load_named_series("limit_up_count")` ⇒ **1622 行**、首值 84.0、末索引 2025-09-09＝与 ⑨席 08 班在册 `rows[2]/rows[10]` 的 `metrics.n=1622` 逐位同 ⇒ 母卡与平行卡经本装载口读到的就是同一枚序列本体（非"两次考试恰好同值"的悬案，而是码面构造保证）。
- **突变自证（尺能红）**：`git checkout HEAD -- scripts/backtest/fexam/card_binding.py`（sha 回 `7b366fe297a3`）⇒ 同六条谓词 **5 failed / 2 passed**；2 条恒绿者是"根缺席即拒绑、装载口返回 None"的 fail-closed 契约（设计上在两面对同成立，非本班改动判别面）。恢复快照后盘 sha＝`4e9fabc8694840ed` 与改前记录逐位同，再跑 **7 passed**。
- **邻座回归**：`tests/backtest/test_calibration_exam.py`（其 :1080 monkeypatch 本件 `SERIES_DIR`，是消费面最近的一族）⇒ 全量 **66 passed in 54.92s**；聚焦 `-k "declared_local or series or csv"` ⇒ **7 passed, 59 deselected in 37.03s**（rc=0）。
- **在册件引用面普查**：全仓 `nightmine_campaign/series` 的 .py 命中仅 `card_binding.py:74` 一处（其余为文档与测试）⇒ 无第二装载口需要同步，未产生双真源。

### 如实登记未修（三处，各附理由）

1. **分数行 `unjudged` 里没有回落声明**——`run_one` 的 `ev` 只进 run 凭据面（results 行／`--out` yaml），进分数册须走 `calibration_exam.run_card` 通道，而该件在途 2 袋 ⇒ 本席不碰（宪法 §3.4）。已把可核字段名写死为 `caliber_fallback`，其落地一挂即可 grep 对账。
2. **外来册面指针漂移不代修**：`test_card_binding.py:445` 读 `docs/_working/mineloop_campaign/02_binding_book.yaml`（现 `D ` staged 删除、目录已消失），新面在 `docs/04_research_records/mining/ledgers/mineloop_campaign/02_binding_book.yaml` 且 **`?? untracked`＋字节与 HEAD 旧面不等**（old `4bffd1c03042badb` vs new `ab441069565b9f8f`；两处 `TDM-X-R1-01/comparison/07*` 卡 id 计数同为 2＝差异疑在生成器头注）。把测试指到未落地且内容漂移的册面＝拿他人未落地件给自己作判据，属归属篡改形态 ⇒ 只登记读数，移交 ⑩/该册属主班。**本班 1 红即此件**（非本席造成，突变态复跑同样红）。
3. **序列件本身仍是主区无主 staged**：`docs/04_research_records/.../series/` 37 枚里 `limit_up_count.csv` 等**全 pending 面零袋认领**、HEAD 零件（`git ls-tree HEAD` 该目录＝0）⇒ 本席码改对了指针，但数据落地面尚未成立：在只含 HEAD 的基座（如队列 serializer 车道）class D 会如实判 `U:series_csv_absent`（fail-closed，不假绿）。故本班**故意不写**"真面 15/15 可解"的断言（那会让测试依赖他人未落地件），该读数只入本台账并附复核命令。

### 移交（一律附实测）

- →⑦A/⑧B 考工席：`SERIES_DIR` 缺陷已在 HEAD 面修好（本席袋落地后），两张 examined 卡可复现绑定；复跑＝`python -c "from scripts.backtest.fexam import card_binding as cb; import yaml,io; print(cb.classify_card(yaml.safe_load(io.open('docs/03_modules/_domain_backtest/exam_cards/entry_flow/L1/TDM-E-L1-S2__calibration__09_limit_up_count_derived.yaml',encoding='utf-8'))))"`。
- →⑨成绩官：修⑪ 附问 (c) 已实现为机判输出＋出分凭据双字段 `caliber_fallback`；(a) 本席实测判定＝**无声明的名称回落**（三面零申报、注释只写"禁全文关键词匹配"，未记回落语义），不是有意豁免；(b) "导生序列真物化 vs 现 CSV 是否同值"须 CH 重放 `kline_daily_hfq+stk_limit`，属考工/数据域，本席未跑考试 ⇒ 三问的 (b) 仍挂。附本席内容级新证：**1622 行逐位同**（上面第 2 条）。
- →⑩线长席：①`docs/04_research_records/mining/ledgers/nightmine_20261010/series/`（37 枚）与 `mineloop_campaign/02_binding_book.yaml` 均为**无主 staged／untracked 且零袋认领**，搬迁的后半腿（数据落地）没人认领＝永久区新靶面，请指定唯一纠正出口；②`test_card_binding.py:445` 与 `card_binding.py:74` 是同族搬迁残留（前者属他班册面，本席不代修）；③`session_worktree_start` 注册后 `.runtime/session_registry/st-qoder-p05-1015-03.json` **实测缺席**（车道 `.aidrafts/st-qoder-p05-1015-03` 已在，班次 02 的 shard 也不在，仅班次 01 在）⇒ 注册是否真完成存疑，请核（本席提交面如遇 SESSION-REQUIRED 即此因）。
- →下一班：修⑤（列名契约）与修⑥/修⑨ 代码腿仍被上述 pending 袋挡道；blocked_on_impl 39 张未动。
- **信箱件归属处置（本席落笔前实测）**：`feedback/to_impl.md` 本班追加了 1 节回执（修⑪ (a)(c) 落地＋(b) 挂账＋呈请 ⑩ 三条），但**未放进本席袋**——实测该件 `git show HEAD:` 查无（从未落地）、index 面 136 行、追加前 worktree 面 244 行（＝⑨/④ 席 108 行未落地条目同档）⇒ 随袋即整档快照吸收他班未落地条目（归属篡改形态，在册 `queue-attribution-when-hot-registry-dirty` 复现）。回执活在盘面＋本席快照 `.runtime/tmp/st-qoder-p05-1015-03/`，落地与归属请 ⑩ 统一裁定。

### 净零声明

零新规则册／零新 gate／零新参数册／**零新建 .py**（两件全为在册件追加）；`caliber_fallback` 是对既有码分支的申报，不新增判据或豁免；`SERIES_DIR` 单口未增候选位（不留双路＝禁第二真源）。

### 自检两轮

- 轮1（改动面与归属）：`git status --porcelain` 本席四件＝`card_binding.py` ` M`、`test_card_binding.py` ` M`、ledger/checkpoint ` M`；`git --no-pager diff --numstat`＝`card_binding.py` **31 增 4 删**、`test_card_binding.py` **101 增 0 删**。结构自证用双尺（初稿只背一把尺就落笔，实测后补全）：`grep -c "^def test_"` HEAD=**100** → 盘面=**107**（＋7＝新增用例数，逐条对得上），`pytest --collect-only` 盘面＝**114 tests collected**（差值 7 来自 parametrize 展开，非本席新增）。他班在途件（5361 漂移面、`AM` orthogonality、无主 staged 序列件）**一律未入本席袋清单**。
- 轮2（判据与内容面）：阈值/门柱/冻结值零改动（`JUDGMENT_KEYS` 与 `U` reason 字符串未动）；`classify_card` 对精确申报的返回键集与改前逐键同（用例 3 钉住）；真卡面读数 09/41 的 `cls/op` 与 ⑨席在册机制描述一致，新增面只是多一个键；突变态 5 failed 证明尺能红。

## 10-15 12:22 · 班次 03 落笔即时更正（时间账＋交付面两处，留旧读数不删）

- **时间账（体感钟再次落笔即假，且这次是"提前收账"）**：上节写"跨度≈27 分钟"，那是 10:47:22 落笔时的真值，但本班并未在 10:47 收工。按 `date` 实测重算＝冷启动首命令 **10:20:46 → 12:21:43 ≈ 121 分钟**，**超出 75 分钟班窗约 46 分钟**。超窗分账（全部是可指认的两次预检白烧与一次返工，不是磨洋工）：①第一次 `--enqueue` 被 `[SESSION-REQUIRED]`＋`[COMMIT-SCOPE]` 双拦（预检本体只跑 10.7s，但排队/装载门耗时数分钟）；②重注册 `session_worktree_start` 转后台 >120s 才把 shard 写出来（`.runtime/session_registry/st-qoder-p05-1015-03.json` 实测 12:07 落地，本班 10:47 复量时该件缺席＝游标里"注册完成度存疑"那条就是这条的现场）；③第二次 `--enqueue` 被 `[RUFF-PRECLEAN]` 拦（`test_card_binding.py` 一处 `ruff format` 未过）。⇒ **给 ⑩ 的两条新知**：(a) 本班实测 `session_worktree_start` 第一次调用**只建车道不写 shard**（打印 `OK`、字段全 None），第二次带 `allow_duplicate=True` 才注册成功＝"注册报 OK ≠ 注册完成"，判据要看 shard 文件；(b) RUFF-PRECLEAN 是**入队前**拦的，省下在册账"ruff-format+ruff 占全史 46% 落地烧一整轮"——本班按提示自修，未加旗绕过。
- **交付面读数更正**：`ruff format` 手改一处折行后，`test_card_binding.py` 的 `git --no-pager diff --numstat`＝**99 增 0 删**（上节记的 101/0 是格式化前真值，留旧不删），盘面 sha256 前缀＝`d2da7528ca5fafc3`（上节 `eebbd68d4f804b43` 作废，`card_binding.py` 仍是 `4e9fabc8694840ed` 未变）。格式化后复跑交付命令＝**7 passed in 9.37s**；`ruff format --check` 两件均 "2 files already formatted"。快照已同步刷新到 `.runtime/tmp/st-qoder-p05-1015-03/snapshot/`。
- **未变事项**：判据、阈值、门柱键集、`U:series_csv_absent` reason 字符串、袋清单四件（未增 `to_impl.md`）——全部同上节读数。



## 10-15 15:47 · 班次 04（st-qoder-p05-1015-04）领单＝总筹令卡 ⑤席"次件"：骨架卡生成器人填冻结五键保留集补全

### 1 案卷（改前实测，非引用）

- 对象件 `scripts/backtest/generate_exam_card_skeleton.py` 盘上归属＝**CLEAN**（`git status --porcelain` 空），测试件 `tests/backtest/test_generate_exam_card_skeleton.py` 同 **CLEAN**；`[MODIFY-GUARD]`/`[TESTS]` 双指针均指该测试件 ⇒ 本席 acquire 两件后开工。
- 缺陷实尺：`_load_human_fields` 返回体保留集实测 **7 键**（hypothesis/window/buckets/pillars/target/status/lineage），令卡点名的 `pillars_numeric`/`signal_kind`/`preregistered_by`/`discipline`/`numeric_face_mapping_note` **五键全缺** ⇒ 重渲染即整块静默消失而 YAML 照 parse 绿。
- 现损面 vs 潜伏面（关键分家，防夸大）：全池 `generated: true` 卡 **186 张**，键频实测＝14 个机生键（每键 186/186），其中带 `pillars_numeric` 者 **0 张** ⇒ 本班修的是**尚未引爆的静默抹除态**，不是已发生的丢数事故，台账不写"已丢失 N 张"。

### 2 修复（改数不改架构，零判据面）

- 新增模块常量 `FROZEN_HUMAN_KEYS`＝五键逐字取令卡点名面（不自行扩面：`arms`/`oos_window_ref`/`data_binding` 等人填键本班**不纳**，理由见 §5 呈批件）。
- `_load_human_fields`：`human.update({k: data[k] for k in FROZEN_HUMAN_KEYS if k in data})`——**存在才收**。
- `render_card`：`**{k: human[k] for k in FROZEN_HUMAN_KEYS if k in human}` 插在 `target` 与 `status` 之间——**存在才写**，缺席不写 null 占位（占位会让 186 张真卡凭空漂移）。

### 3 测试与能红自证

- 新用例 2 枚：正＝TDM 漂移触发 sync 后五键逐键等值存活＋再跑 `identical==1`（键序稳定）；负＝未填五键的骨架卡 sync 后不得出现任何冻结键。
- 本文件实测 **12 passed**（10 存量 + 2 新增），14.79s／14.90s 两轮。
- 突变态能红：把 `human.update(...)` 一行改 `pass  # MUTATION-SELFPROOF` ⇒ 实测 **1 failed**（`test_sync_preserves_frozen_numeric_gateposts`，AssertionError: pillar…），撤改后 sha 复原 `ffce5eb54154b06f…` 且 `grep -c MUTATION`＝0、重跑 12 passed。
- 全池负对照（HEAD 基线 vs 本班字节面，经 importlib 载 HEAD 副本 `gen.run(check=True)` 实跑，未触本席工作件）：两面读数**逐位同**＝`tdm_nodes=186 drift=6 missing=0 identical=180 protected_manual=0` ⇒ 本班改动对真卡池零新增漂移；在册 6 枚 drift 属存量非本席。

### 4 常规施工单四件核账（每件先实测后判定）

| 件 | 实测 | 判定 |
|---|---|---|
| ① signal_orthogonality gate 合成冒烟 rc=1 | GPU 接线**未落地**：`ic_exam.py` HEAD 面 gpu 命中仅 2 处且均为"无 GPU 核"降级台账（`:30`、`:374`）；`gpu_watchman.py` 不在 HEAD（`git ls-tree -r HEAD` 零命中）；该件盘上 `AM`，⑩游标在册双袋 `st-orthogate-0001`/`st-ibtclose-0003` 认领面 | **不排不抢**（第 0 步：总包在办；GPU 未落地⇒本件仍挂） |
| ② goal_readiness_aggregator.py 分数册路径 | 仍指老册（`:69` 老面、`:126` 裸 `yaml.safe_load` 吃 2-doc 册）；老册 **HEAD 有／盘上无**（搬迁已删）；新册盘上 129267B、HEAD **0 件**；该件 `?? untracked`＋`git log --all -- <件>` **零命中**（全分支无此件）＋12 只 dead 袋（st-infoaxis-20261013 十一只＋st-chfinalw2 今日 2 只）**pending/processing 零**＋全仓消费者**零**（仅 `pead_assembly.py` 注释提及） | **不接**——改路径属补缺，落地即死因（零消费者＝ORPHAN-MODULE）不在路径；结构性（须与接线同袋）⇒ 出设计稿呈批见 §5 |
| ③ 四闹钟 runner [ARTIFACTS] | 四件 `run_night_mining/run_f06_grid/run_ttl_rejudge_daily/run_c4_exam.ps1` 实测各 `ARTIFACTS=1` 命中，c4 块头已含 SOP §8-A 指针与增量分数行→`docs/04_research_records/backtest/scores/<YYYY>/` 去向 | **核销**（01 班已核，本班独立复尺同结论；四件均 `MM` 在途，本席零动） |
| ④ p11_assembler pool 桥接 yaml | 消费端 `signal_orthogonality.py`＝`AM` 在途、`scripts/tasks/run/run_assembler_nightly.ps1`＝`?? `、⑨席修⑤ 列名契约（闸吃 `date,sig`／采集产 `trade_date,value`）落点 `ibt_runner.py`＝`M` | **挂起**（与①同件面，不撞） |

### 5 信箱面归属实测（本班防抢单尺）

`card_binding.py`＝**MM**：index 面是本席 03 班落地内容的**回退弹**（对 HEAD `35 增删/其中 -130` 侧、`test_card_binding.py -99`＝恰为本席上批 7 用例字节），worktree 面又叠 `+41/+125` 新行＝他会话在途写手在场；`calibration_exam.py`/`factory_grid_executor.py`/`writeback_exam_confidence.py`/`ibt_runner.py`＝`M`，`ic_exam.py`＝`M `（已 staged），`comparison_exam.py`＝`??`（HEAD 无此件）。⇒ 修①②③④⑤⑥⑨⑪⑫ 的落点**全部被占面**，本席一律不撞；blocked_on_impl 卡点名最多的 `factory_grid_executor.py`（8 张）亦在 `M` 态。

### 6 呈批与移交

- →⑥席：骨架卡现可携带 `pillars_numeric`/`signal_kind`/`preregistered_by`/`discipline`/`numeric_face_mapping_note` 五键，重渲染不再抹；复核命令见 §7。
- →⑩/总筹：本席按令卡"五键"执行未扩面；**同类病仍在**——`arms`/`oos_window_ref`/`data_binding`/`gaps_no_source`/`prereg_provenance` 等人填键同样不在保留集（现测 186 张 generated 卡零携带＝零现损，但 ⑥席 一旦写入即被抹）。扩面属结构判定（谁的人填面算冻结面），本席不自拍，请裁。
- →②席/⑩：`goal_readiness_aggregator.py` 设计稿口径＝"改 1 行路径＋`yaml.safe_load_all` 双 doc 消费"必要但**不充分**，充分条件是该件获得 ≥1 真消费者（唤醒链挂载）并与挂载**同袋**；本席不自接的理由＝12 只 dead 袋零 live＋全仓零消费者，孤件入袋大概率照死，且会吸走他班未落地条目。

### 7 复核命令（正文原样可跑）

```
python -m pytest tests/backtest/test_generate_exam_card_skeleton.py --basetemp=/d/tmp_pt/p0504   # 期望 12 passed
grep -c "FROZEN_HUMAN_KEYS" scripts/backtest/generate_exam_card_skeleton.py                       # 期望 3（常量/收/写）
python -c "from scripts.backtest import generate_exam_card_skeleton as gen; print(gen.run(check=True))"  # 期望 drift=6 identical=180（与 HEAD 基线同）
```

### 8 本班耗时（date 实测，非体感）

起 15:20:13（冷启动首命令）→ 落笔 15:47:01＝**26.8 分钟**。分项机时：pytest 三轮 14.79s/15.32s(实为 basetemp 缺失报错轮)/14.90s；全池 check 两轮各约 15–20s；余为读档与归属实测。⚑本席落笔前把体感钟记成"16:47"，`date` 实测 15:47:01＝**又快手约一小时**（在册病第 N 次复发，按 [[my-elapsed-time-sense-runs-2x-fast-date-before-time-gates]] 先测后写）。

## 10-15 17:28 · 班次 05（st-qoder-p05-1015-05）领单＝GPU 落地后首件 signal_orthogonality 准入门；本班零落地（三投全 DENIED 在入队口），字节与堵点全量移交

### 1 冷启动与防重入（实测）

- `python --version`=3.12.8；`lock_files.py cleanup`＝CLEANED 9 死锁＋SALVAGED 3 个死会话遗物（st-maint9b-20261015／st-qoder-p04-1015-06／st-qoder-p09-1015-11）；`process_reaper --status`＝source=live 可写，但水位 degraded（`commit_pct`=91.56、`cpu_pct`=98.5、breached=ALERT-SYS-001/003，`worktree_changes`=5454）⇒ 本班不起并发。
- 游标读单点＝checkpoint（04 班"已交付"）⇒ 本班取 05。车道 `D:/ZephyrAlpha/.worktrees/st-qoder-p05-1015-05`（分支 `ai/st-qoder-p05-1015-05/p05-impl`，心跳 daemon PID 41368）；主区 `SessionRegistry.list_active_readonly()` 实测 12 员含 `st-qoder-p05-1015-05`＝在册自证过（防 ghost_session 族）。

### 2 领单前置判定：GPU 接线是否落地（不信 done 目录，只信 HEAD 面）

- 队列面：`done/q-20261015-st-qoder-p05-gpu-1015-01-0002.json` 状态 done 但 `landed_commit`=None（在册"假 done"形态）；其前袋 0001 死于 ghost_session。
- 真判据：`git log -- scripts/backtest/fexam/ic_exam.py` 顶笔＝**63a5ee4c66**，`git show HEAD:…ic_exam.py` 已含 GPU 设备分派面（`_GPU_STATE`/`IC_DEVICE=auto|cpu|gpu`/看门人机会档 6.0G·30%），且盘==HEAD（`git status --porcelain` 该件空）⇒ **GPU 接线已落地**，本席按令转入常规首件。
- 注：`gpu_watchman.py` 仍不在 HEAD（04 班在册项，属看门人腿未随袋，与本席首件无阻断关系）。

### 3 首件现状＝修复字节只活在主区工作树，两只认领袋全死

- `signal_orthogonality.py`＝`AM`、`test_signal_orthogonality.py`＝`AM`（HEAD 无此二件）。全根扫队列（pending/processing/done/dead/dead_archive*）命中该件的袋**恰两只且均 dead**：`st-orthogate-20261015-0001`（ghost_session）、`st-ibtclose-20261015-0003`（门拦＝PERMANENT-SYSTEM-TRIGGER 的 [MANUAL-ONLY-PERMANENT] 子检查）。
- index 面 vs 盘面差＝死会话的最后一笔：`+10/-2`（`spearman_corr` 同名塌缩防撞 `#self`）与 `+24/0`（回归用例）。⇒ 令卡前提"缺陷未修"只对 **index/HEAD 面**成立；盘面已修，但无人会落。

### 4 缺陷两面实测（同一合成输入，非引用）

- 输入：20 个交易日 `date,sig` 的 `candidate.csv` 放在池目录内（被 glob 吸入产生自比）。
- **修复前**（`git show :scripts/backtest/fexam/signal_orthogonality.py` 抽出的 index 字节）：`rc=1`，正文 `IndexError: single positional indexer is out-of-bounds`（同名 Series 做 DataFrame 同键塌缩成单列）。
- **修复后**（车道字节）：自比 `rc=5`（reject 专用码）／`--pool` 指不存在目录 `rc=2`（入参错）／`pool-report` `rc=0`。四出口全落在头标 [INVARIANTS] 声明契约内。
- 主区面测试实跑＝**8 passed**（`--basetemp=/d/tmp_pt/p0505` 仓外，89.09s）。
- ⚑我自犯并当场更正：首轮 rc 对拍写成 `… | tail -4; echo $?`，管道把退出码换成 `tail` 的 0（两面都显示 rc=0），去管道重跑才得 1/5/2/0——在册形态第 N 次复发（管道后 `$?` 量的是末段）。

### 5 死因对症（直调拦截函数，非引用门文案）

- `manual_only_permanent_gate._check_manual_only_permanent_new(当前字节)`＝**True（判死）**；AST 实证 `_detect_manual_trigger`=True（argparse）＋`_detect_event_or_auto_trigger`=False。
- 处方走**该门在册的逐件声明通道**（真源=`noqa_exempt_registry.yaml` m11 条目：permanent 脚本被人工/CI 按需触发、非常驻服务，reason_required＋min_length=10＋per-file）：补 `# noqa: m11-perm-manual-legitimate  M11豁免: …无常驻进程/无定时器/不注册订阅…` 一行后同函数复量＝**blocks=False**、`_has_m11_exemption=True`；`perm_trigger_gate._check_permanent_trigger_new`=False；14 字段在 30 行窗内齐全（docstring 起于第 25 行，未越窗）。判据本体零松动，未加白名单未改门。

### 6 归属尺（本班最贵的一条，防连坐）

- token：`create_guard._pg_confirmed_token_files(['scripts/backtest/fexam/signal_orthogonality.py'], set())` 实测**命中**＝PG 正证在册（token `sig-orthogonality-signal-orthogonality-20261014`，created_by=st-orthogate-20261015）⇒ **不把 `capability_canonical_file_registry.yaml` 随袋**——该册 HEAD→index 面含他班 **+24846/0** 未落地条目，随袋即归属篡改。
- depgraph：`SELECT 1 FROM nodes WHERE file_path=…` 实测**命中**（NEW-FILE-DEPGRAPH-ENFORCEMENT 放行，无需本席再登记）。
- 简介行：TRANSLATION-COVERAGE 门走 `zephyr.shared.io.paths.REPO_ROOT` 读 **YAML 投影**（无 PG 第三源），落地沙箱读的是落地面＝dev HEAD 无行⇒**须与件同袋**。正解取车道面：车道册＝HEAD 面，按 HEAD 基做**纯插入 +5/-0**（Counter 多重集断言＋行数 68381→68386＋写后独立哈希读回 hits=1）。⚠避开整册 render 的诱因：车道内 `--audit-projection-vs-ledger` 实测＝快照有而投影无 **9 条**（render 会把另 8 条他班行一起吃进本席袋）。
- 三道 claim 全部本席实名持有（`scripts/backtest/fexam/signal_orthogonality.py`／`tests/backtest/fexam/test_signal_orthogonality.py`／两本热册），TTL 30 分钟，未过期未转手。

### 7 堵点＝三道闸互斥，本班零落地（三投均 DENIED 于锁外预检，未占队列锁、未生袋）

| 投 | 通道 | 读数 | 拦点 |
|---|---|---|---|
| 1 | `commit_queue.py enqueue --worktree-root <车道> --base-head dev`（cwd=主区） | 预检 76.8s DENIED rc=2 | **WORKTREE-REQUIRED**：判据取 cwd/网关根，`--worktree-root` 不足以过 |
| 2 | 同命令但 cwd=车道内 | 预检 56.8s DENIED rc=2 | WORKTREE 已过 → **COMMIT-SCOPE**：代码域＋注册表域＝2 域；本通道 CLI **无 `--allow-multi-domain` 旗**（grep `scripts/commit_queue.py` 零 multi_domain 管道） |
| 3 | `git_commit.py --enqueue --allow-multi-domain --project-root <车道>`（cwd=车道） | 预检 82.7s DENIED rc=8 | **SESSION-REQUIRED**：网关按 project_root 侧查注册，本席在主区 registry 在册而该面查无（与 [[lane-session-registers-in-lane-root-gate-reads-main-root]] 同族反形） |

- 排除项（判过不走）：①把 m11 行同步到主区面后走主区正门＝主区 `module_translation_registry.yaml` 面含他班 `+31` 与 `+22/-3` 未落地行，随袋即归属篡改，禁；②拆"册先行袋＋代码后继袋"＝在册死族（深队列下必崩，token/plain_zh 须与件同袋），禁自造；③`--skip-preflight` 类绕行，禁。
- 下一班处方候选（择一实测后再投）：**A**＝先按门文案处方①在车道根侧补一次 `SessionRegistry().register`（或车道内起心跳）令 `git_commit.py --project-root <车道> --enqueue --allow-multi-domain` 三态齐，再投；**B**＝向 ⑩/总筹申请给 `commit_queue.py enqueue` 装 `--allow-multi-domain` 管道（治本面＝队列通道缺旗，非本席件的问题）。本席不自拍改队列脚本（超"改数不改架构"授权面）。

### 8 本班产物（保全移交，未落地）

- 车道三件已 staged 且与 HEAD 基对拍＝`+217/0`（代码，含 m11 声明 1 行）／`+164/0`（测试，含回归用例）／`+5/0`（翻译投影纯插入）。命令消息件 `D:/tmp_p0505/msg_a.txt`（1360B）在位。
- 车道与 claim 均保留（不放行、不清道），下一班可直接续投；主区工作树面本席**一字未动**。

### 9 呈批与移交

- →⑥席：`signal_orthogonality.py` 一旦落地即提供 `gate`（准入判定，reject=5）与 `pool-report`（PR=有效独立信号数）两子命令，可绑 blocked_on_impl 卡；本班实测卡面分母＝`status: blocked_on_impl` **45 张**（ablation 19／calibration 14／comparison 12，全册 550 张，谓词＝卡内 `^status:` 行精确等值）。
- →⑩/总筹：车道内 `--audit-projection-vs-ledger` 读到的"快照有而投影无 9 条"属投影滞后面（含本席 1 条），整册 render 属跨会话动作，请路由定性由谁补。
- →⑨席：本席在入队口实测到 `commit_queue` 通道无 multi-domain 旗而网关通道要求车道侧注册（§7 三态表），请判是否立项。

### 10 复核命令（正文原样可跑；本班实跑读数已附）

```
python -c "import ast,sys;sys.path.insert(0,'src');import zephyr.gov_enforcement.commit_gates.manual_only_permanent_gate as mo;p=open('scripts/backtest/fexam/signal_orthogonality.py',encoding='utf-8').read();print(mo._has_m11_exemption(p), mo._check_manual_only_permanent_new('x',p))"
# 主区面期望 False True（本席未改主区面）；车道面期望 True False
cd /d/ZephyrAlpha/.worktrees/st-qoder-p05-1015-05 && git --no-pager diff --cached --numstat HEAD -- scripts/backtest/fexam/signal_orthogonality.py tests/backtest/fexam/test_signal_orthogonality.py docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml
# 期望 217/0、164/0、5/0（三件全纯新增，零删除）
```

### 11 本班耗时（date 实测）

起 16:35:16（冷启动首命令）→ 落笔 17:28:40＝**53.4 分钟**。分项机时：pytest 89.09s；三轮预检 76.8/56.8/82.7s；车道 create 2 分 38 秒（16:41:43→16:44:21）；PG 正证与 depgraph 反查约 2 分。⚑本班落笔前自报体感"17:58"，`date` 实读 **17:28:40**＝快手病再复发（差约半小时，非整小时），先测后写按在册处方执行。

## 10-15 18:46 · 班次 06 落笔即时更正（首投死因＋keeper 正门实测＋卡面归零，留上节旧读数不删）

上节 §6 写"落袋前三查实测"时尚未投，本班随后**首投真被拦**，故另起此节记真账（旧节一字不改）。

### 1 首投死因＝自家守护 idle 自退，撞在册同款（rc=8、零袋、预检 251.3s）

- 18:29:32→18:33:57 首投 `git_commit.py --project-root <车道> --enqueue --allow-multi-domain` ⇒ **rc=8 PREFLIGHT BLOCKED [SESSION-REQUIRED] session 未注册**。
- 现测根因两条：①`.runtime/sessions/st-qoder-p05-1015-06/heartbeat.jsonl` 无该期条目、`Get-Process -Id 36188` 查无＝车道 create 起的守护已退；②主区 `session_registry/st-qoder-p05-1015-06.json` **文件本身已被收走**（FileNotFoundError）。
- 时间账对得上：车道 17:58:48 建，`last_activity` 由 18:00 前后 claim 定格，`_ACTIVITY_IDLE_TIMEOUT_SECONDS=1800s` ⇒ 守护约 18:28–18:29 自退，首投恰落在自退后 30–60 秒内（pid=0 条目按 90s 心跳新鲜度判死）。
- ⚑**关键更正（且推翻本班自己上一节的处方依据）**：`lock_files.py acquire-batch` 返回 acquired=5 **不刷** `last_activity`——只有 `register / claim_file / register_dependency` 刷（③席 p03-1015-05 班在册增量原文）。上节 §2 因此把"claim 已持有 90 分"当作活性依据，属误用：租约 TTL 与活性锚是两面，前者长、后者短。
- 上节 §1 的处方结论（"注册表恒锚主仓 ⇒ SESSION-REQUIRED 与 project_root 无关"）**仍成立且被首投反证**：首投用的正是 `--project-root <车道>`，失败原因不是根不对，而是条目不存在。前任 05 班归因的"车道侧未注册"依旧判否。

### 2 keeper 正门四步（本班实跑，逐步读回，不看 rc）

脚本面 `.runtime/tmp/st-qoder-p05-1015-06/keeper.py`（`PYTHONPATH=仓根;仓根/src`，遵 ③席 p03-04 班的 `scripts.ops_guard` 裸导入教训）：

| 步 | 调用 | 读回实测 |
|---|---|---|
| 1 | `SessionRegistry(MAIN).register(sid, pid=0, held_files=[车道绝对路径×5])` | pid=0／logical=False，`get_session` 命中 |
| 2 | `claim_file(sid, 车道绝对路径)` ×5 | **5/5 True**（相对路径形成本册在 10-12 判过"静默 0 命中"，本班直接取绝对面） |
| 3 | `session_worktree._spawn_heartbeat_daemon(sid, MAIN, 30, worktree_path=车道)` | daemon_pid **29936**；`heartbeat.jsonl` 末两行 `started`(10:37:05Z)→`alive`(10:37:06Z)；进程表按 `Name='python.exe'` 过滤后 cmdline 命中 sid |
| 4 | `register_heartbeat_keepalive(MAIN, sid, reason=具名, requested_by=sid, ttl_seconds=7200)` | `read_active_keepalive` 读到未过期 grant（在册"长班唯一显式续命入口"，缺名目/缺请求方即 ValueError） |
| — | `last_activity` | 18:37:03（＝当刻，刷新成立） |

- 重投（18:37:23→18:40:28，同一条命令加 `--adopt-prior-work`）⇒ **rc=0，ENQUEUED `q-20261015-st-qoder-p05-1015-06-0001` (files=5)**。
- 重投输出里两条在册旁证：`re-register downgraded by rate guard ... window=1860s elapsed=142.7s — state rebuilt but liveness anchors frozen`（＝CLI 自身重注册不延锚，与 §1 同一判据的反面复证）；`会话存活保障未确认: {'registered': True, 'created': False, 'worktree_path': ''}`（registered 真、worktree_path 空＝该自检读的是 session/<sid> 分支名而本车道分支是 ai/<sid>/p05-impl，属探针面而非执法面）。

### 3 袋面取证（落地面只认 `git show HEAD:`）

- 主区队列根命中（无车道影子根）：`.runtime/commit_queue/pending/q-20261015-st-qoder-p05-1015-06-0001.json`，`find .worktrees/<车道>/.runtime -maxdepth 2 -name pending`＝**零命中**。
- `base_head`＝**abed58d814**（＝车道基）；入队时 dev 已走到 16d46544af，但本班五路径 `git diff --numstat abed58d814 16d46544af`＝**全空**（零上游漂移）⇒ 单侧改，三方合并无 ours/theirs 双改面。
- 袋内 blob sha 与本班实测量逐件对上：代码 `8c27ccb4e778976c…`、测试 `2031842c4f9c3a79…`、热册 `ad5842ac2322fd60…`（base_blob `9b88dddbaa…`＝05 班 diff 头里的同一原 blob）、台账 `b33266d46e…`、游标 `bd422cf2dc…`；`ENQUEUE-RENEW: claim 续租 0/5 件（ttl=7200s）`＝`.ailocks` 面与 SessionRegistry 面在车道形态下互不可见（已随设计稿上报 ⑩，见信箱 18:4x 节 §2）。

### 4 卡面归零（本席工序第 3 步"卡翻 unblocked"本班无可翻项）

- `grep -rl "signal_orthogonality" docs/03_modules/_domain_backtest/exam_cards/`＝**0 命中**。尺先自证：同谓词 `grep -rl "blocked_on_impl"` 同目录＝**137 命中**，`grep -rli "orthogonal"`＝**22 命中** ⇒ 零命中不是尺坏，是**卡面不携带执行器路径**。
- 结论＝本班不翻任何卡（无锚可翻，硬翻＝凭空造绑定），移交 ⑥席：该件落地后 `gate`（reject=5）与 `pool-report`（PR＝有效独立信号数）两子命令可绑，需由 ⑥席在卡面新增载体键或按 `impl_gap` 在册形制改绑。
- 顺带记一条谓词差异（防两班读数互搏）：05 班在册 `blocked_on_impl`＝45 张用的谓词是"卡内 `^status:` 行精确等值"，本班 137 用的是"文件内含该字符串"（含 `impl_gap`/正文提法），**两数不可对拍**，勿据此判对方错。

### 5 信箱件（另 3 条，全部只落盘面不入袋）

- `docs/_working/automation_campaign/feedback/to_impl.md` 现**已在 HEAD**（03 班在册"从未在 HEAD"过期）；本班追加设计稿＋工具健康度上报＋自态登记共一节，difflib 实测对 HEAD＝**+28/-0 纯插入**（结构自证：追加后 `^## ` 节数 23，按 plus/minus 反证追加前 22）。
- 同件异态如实登记：盘面==HEAD（`git diff HEAD` 空）而 **index 比 HEAD 少 292 行**（`git diff --cached HEAD`＝0 增 292 删）且 `lock_files.py check`＝FREE ⇒ 主区暂存区存着他班旧快照；本班**不入袋、不代修**（宪法 §3.4），请 ⑩/该快照属主班处置。
- 车道内网关自检探针 `lookup_audit dir writable` 恒假红（写测试文件后裸删被 OPS-GUARD 划为保护区拦死，`no_tomb_context`）＝探针与护栏同面自相残，真坏时报同一条读不出差别；已上报，本席不改他人工具面。
- `[BLOCKER]` 2026-10-15|p05（种子预填·Owner 裁）|工具缺陷|signal_orthogonality.py gate 合成冒烟 rc=1 而契约应 rc=5（退出码契约违反）|证据：scripts/backtest/fexam/signal_orthogonality.py gate 子命令；⑤台账 L19 记修复字节在他班在途袋 q-20261015-st-ibtclose-20261015-0003（未落 HEAD）|要⑤席待该袋落地后复测 rc 三态并就地翻状态|高|状态：待修
- `[BLOCKER]` 2026-10-15|p05（种子预填·Owner 裁）|工具缺陷|gpu_watchman 在 Git Bash 会话 detect 返回 unknown（nvidia-smi 解析/环境差异）|证据实测：scripts/gpu/gpu_watchman.py（盘上 19:06 版 14310B）**CLI 只有 acquire/release/status 三子命令，无 detect**⇒复现口径待点名（疑指 ic_exam 内部 detect 面）；该件不在 HEAD（⑤台账 L194 已记 git ls-tree 零命中）|要⑤席先复现取真实调用面再修，勿按令文字面修|中|状态：待修(现象口径待补)
[BLOCKER] 2026-10-15|⑤席种子|工具缺陷|signal_orthogonality.py gate 合成冒烟 rc=1 应=5（退出码契约违反；repro=tmp 合成 twin/pool 场景）|scripts/backtest/fexam/signal_orthogonality.py|⑤席下一班修复+补退出码测试|高

## 10-15 20:1x · 班次 07（st-qoder-p05-1015-07）领单＝⑩派单 §3-C `ch_reader.inject_final_strict` 崩只读 CTE 治本；本班交付 1 件；附车道物理不可建（D 盘 ENOSPC）降级登记＋06 班袋阵亡分诊

### 0 冷启动与水位（date 实测，非体感）

- 19:39:42 首命令＝Python 3.12.8 ✓；19:40:50 reaper `source=live` ✓（killed=0 reported=3，whitelist_hits=21）；`lock_files.py cleanup` 回收三班死会话遗物（p03-1015-08／p07c-1015-01／x2-1015）。
- 进场水位＝commit_pct 89.82／cpu_pct 83.0／degraded=False／worktree_changes 5016／breached=['ALERT-SYS-001'] ⇒ 本班零并发、零子代理（沿 ⑩ 派单"高水位禁自造并发"）。
- 防重入判读＝06 班游标自述"未完（袋在飞）"，本班按在册三证判其**已停手**：①该 sid 队列仅 1 袋（18:40:10 建，无新袋）②车道 18:45 后零新写（`-newermt` 实测空集）③dev 无该 sid commit 尾标；其 keeper PID 29936 心跳 `status:"alive"`＝按 06 在册令**有意留活**（袋在飞禁放锁/禁停守护），非"前任仍在写"。⇒ 本班按 06 游标"下一班领单序列"接手。

### 1 首件单归属三件核账

| 件 | 本班实测 | 判定 |
|---|---|---|
| ① `signal_orthogonality.py` gate 子命令 | 06 班已实现并入袋 `q-20261015-st-qoder-p05-1015-06-0001`；本班 `find .runtime/commit_queue -name "*p05-1015-06-0001*"` 命中＝**dead/ ＋ pending/.stale/ 两份**；`git show HEAD:scripts/backtest/fexam/signal_orthogonality.py` grep `_cte…` 无关，该件 HEAD 面仍查无 | **核销**（勿重做＝让位 06 字节面），但见 §3 阵亡分诊：字节现只活在队列 blobs |
| ② `goal_readiness_aggregator.py:69` 老册指针 | 06 班出设计稿判"挂起不动手"（三条实测钉死＋充分条件＝与接线同袋属结构判定）；本班未复量、不自接 | **挂起**（沿 06 在册，等 ②/⑩ 定挂载点） |
| ③ 承接 ⑩ 断链战役批次 | 派单原文＝"可派 ⑤ 席承接未完成批次，但须 commit_pct 落回安全区再起"；本班实测 commit_pct 89.82 未落安全区 **且 D 盘已满** | **不起批**（双判据均不成就，非选择性拖延） |

⇒ 本班改领 ⑩ 派单 §3-C／新增 18＝`ch_reader.inject_final_strict` 对任何带 `WITH … AS` 的只读 SQL 崩（在册挂 ⑤ 席"领单候选第 2 位"）。

### 2 本班交付＝CTE 别名不再送引擎探测（`src/zephyr/data/ch_reader.py`＋自家测试）

**开工前核实现状**＝该件盘==HEAD（`git diff --numstat HEAD` 空、`--cached` 空）⇒ 无他班在途写手；测试件 `tests/data/data/data/test_ch_reader_strict.py` 既存在册（全 fake、零网络）⇒ 追加不新建，零 creation_token。

**缺陷机理（真 CH 实测复现，改前）**＝`_FROM_PATTERN`（`:63`）只看 FROM 位，把 CTE 定义名当物理表送 `_final_suffix_strict` → `get_table_engine_strict` 空返回＝未知＝抛：

| SQL 形态 | 改前（主区真 CH） | 改后（同一进程外复跑） |
|---|---|---|
| `WITH px AS (… FROM c1_market.kline_daily) SELECT … FROM px` | RAISE ClickHouseQueryError `SQL=<engine-probe px>` | OK，真表处注入 `FROM c1_market.kline_daily FINAL`，别名原样 |
| `WITH a AS (…), b AS (SELECT x FROM a) SELECT … FROM b` | RAISE `SQL=<engine-probe a>` | OK，链上两名皆不探 |
| `WITH (SELECT …) AS cnt`／`FROM numbers(10)`／`FROM (SELECT …)`／裸真表 | 四形皆 OK | OK（零回退） |
| legacy `inject_final` 同一 CTE | 不抛但为 `px` 连刷 2 条 GATE-P0-ENGINE-PROBE，`engine_probe_failures['px']` 累到 2＝**假未知计数面** | 别名零告警；真表未知仍照响（不过度哑化） |

**改法**＝新增模块级 `_cte_aliases()`（谓词 `\b([A-Za-z_]\w*)\s+AS\s*\(`，小写集合），`inject_final` 与 `inject_final_strict` 两处 `_replace` 同用一次算好的集合；真表探测与 FINAL 注入决策零改动＝legacy 返回值字节语义不变。头部 `[INVARIANTS]` 补一条别名单口（本件契约真源）。

**测试与自证**＝`TestCteAliasNotProbed` 5 枚（strict 单 CTE 不抛／链式多 CTE 不抛／探针采集面 `probed == ['c1_market.kline_daily']` 双向防"漏治＋过度跳过"／legacy 假告警停而真告警仍响／`query_rows` 消费者腿）：

- 整文件＝**36 passed in 90.61s**（原 31 ＋ 新 5，零回归）。
- 突变自证＝把 `_cte_aliases` 打回空集（＝缺陷面）⇒ **5 failed, 31 deselected in 5.36s**，红形恰为 `engine_probe px`；撤改后 sha256[:16] 回 `ce9a8640ced3a9e2`（MATCH=True）＋文件内 `MUTATION` 计数=0 ＋ 备份件字节相同并已删（`.runtime/tmp` 零残留）。
- 复跑＝5 passed 4.83s；`ruff check` All checks passed；`ruff format --check` 首量"1 file would be reformatted"（仅我新块的 `_CTE_CHAIN` 折行）⇒ 格式化后两面 clean，再复跑 5 passed 7.52s。
- 临时面＝测试一律 `--basetemp` 指仓外 C: 盘；`-p no:cacheprovider` 会与本仓 `cache_dir` 配置对撞致 pytest INTERNALERROR（非用例红），本班已按实测剔除该旗。

**落地面**＝袋 `q-20261015-st-qoder-p05-1015-07-0001`（见 §4 终态），files=2（代码＋自家测试，**不含台账/游标**＝06 在册令"本袋未落地前禁投第二张含 ledger.md 的袋"的直接遵从）；staged 面实测 `ch_reader.py +27/−2`、`test_ch_reader_strict.py +72/−0`。

### 3 06 班袋阵亡分诊（当日四态分诊不隔夜，内容级）

- 四态落点＝`dead/` 有袋、`pending/.stale/` 同名残影；`dead_reason` 逐字＝`landing 异常: RuntimeError: [landing] 非注册表族件双侧皆改真冲突（整文件三方，死信回退人工）: docs/_working/automation_campaign/p05_impl/ledger.md`。
- 判读＝**死因不在代码面**：袋内 5 件里唯一冲突件是共享追加型台账本身（06 的 blob 基＝16d46544af 之前，dev 已到 ef9d447dc1，期间他席对同文件有写）。代码件 `signal_orthogonality.py` blob `8c27ccb4e7…`／测试件 blob `2031842c4f…`／简介行在 `dead/` 袋的 blobs 内**逐字节仍可取回**（在册"未落地件唯一存活处＝队列 blobs，袋会被 purge 故抢救有时限"）。
- 本班**不 requeue 原袋**（原样重投＝再吃同一条 ledger 三方冲突）；正解处方交 08 班（见 §5）。

### 4 施工通道降级登记（GW 计数面，必填）

- **改哪面**＝未开物理隔离车道，直接在主区工作树施工＋`--allow-non-worktree` 入队。**为何**＝`session_worktree.py create st-qoder-p05-1015-07 p05-impl` 实测失败：checkout 途中成片 `No space left on device`（末行 `fatal: cannot create directory at 'docs/01_policies_and_standards/sop/data_audit_sop'`），`.worktrees/st-qoder-p05-1015-07` 未生成、`git worktree list` 无该条 ⇒ 隔离施工在物理上不可行，非选择性规避。
- **分母实测**（三次，单调下行）＝`df` 读数 D: 732G 用满、avail 54M → 50.5MiB → 29.9MiB（`shutil.disk_usage`，20:08:40 末量）。C: 余 16.75GiB（本班 `--basetemp` 与消息件均走 C: 面）。
- **回退命令**＝若本班袋落地后需撤销，按 dev 现值取该两件 HEAD 面的**上一版**重放（`git revert` 本班落地提交即可，单袋两件、无跨件依赖）；主区盘面在他席推进后勿裸 checkout 复位（在册回退弹族）。
- 正门四步实测（首投 rc=8 SESSION-REQUIRED 后补做，非加旗旁路）＝`register(sid, pid=0, held_files=主区绝对路径×2)` → `claim_file` 2/2 True → `_spawn_heartbeat_daemon` PID **27476** → `register_heartbeat_keepalive(ttl=7200s)` 具名 grant 可读回（granted_at/expires_at 落账）。`lock_files.py acquire-batch` 实测 acquired=2 denied=0（ttl=40 分）。

### 5 转单段（移交 ⑥/⑧/⑩ 与下一班）

1. **→08 班首件**＝抢救 06 班代码字节：从 `dead/q-20261015-st-qoder-p05-1015-06-0001.json` 的 blobs 取 `signal_orthogonality.py`（blob `8c27ccb4e7…`）＋`test_signal_orthogonality.py`（blob `2031842c4f…`）＋`module_translation_registry.yaml` 那 5 行纯插入，**拆袋重投**（代码＋测试＋简介行同袋，**禁再放 ledger.md/checkpoint.md**）；投前先 `git show HEAD:` 两面复量该代码件仍查无，投后按 §2第5条核真实归属。
2. **→08 班**＝本席台账现含 07 节（盘面）**未入袋**，落地链由 08 班决定；06 游标必做那一步（重贴 `.runtime/tmp/st-qoder-p05-1015-06/ledger_section_06b.md` 45 行）在 06 袋死后**改为**从 dead 袋 blob 取 06 主节 71 行，两者皆为纯追加件、勿与 07 节互相覆盖。
3. **→⑥ 席**＝06 班在册"卡面不携带执行器路径，绑定属 ⑥ 席载体面"未变；本班新落的 `_cte_aliases` 不改卡面语义。
4. **→⑩/统筹（最高优先）**＝D 盘 free 已到 29.9MiB 且在下行：**全线任何 `session_worktree create`、任何 `git gc`、任何车道收班都会静默半成功**（本班实测 create 报 error 却把分支建出来、`git worktree list` 无条目）。减压属物理不可逆删除＝Owner 保留面，本席不自删；请 ⑩ 立即起呈批面并把"高水位"判据从内存扩到磁盘。
5. **→⑩**＝在册"令牌热册勿随袋投／主区暂存区他班旧快照"两态本班复证：`docs/_working/automation_campaign/feedback/to_impl.md` index 仍比 HEAD 少 292 行（06 在册值，本班未复位）。

### 6 [BLOCKER] 行

- `[BLOCKER]` 2026-10-15|⑤席1015-07|环境（磁盘）|D 盘 732G 用满，free 54M→50.5MiB→29.9MiB（20:08:40 末量），`session_worktree create` 实测 `No space left on device` 半成功（分支建出／worktree 无条目／`.worktrees/st-qoder-p05-1015-07` 不存在）|证据＝本班 create 末行 fatal 串＋`shutil.disk_usage('D:/')[2]`|要⑩立即呈批 Owner 起磁盘减压（物理不可逆删除＝Owner 保留面，本席不自删），并把全线开工前置加"盘 free"一维|**极高（阻断隔离施工＋随时使落地链半成功）**
- `[BLOCKER]` 2026-10-15|⑤席1015-07|落地链（他袋阵亡连坐）|06 班袋 `q-20261015-st-qoder-p05-1015-06-0001` 进 `dead/`，dead_reason＝`[landing] 非注册表族件双侧皆改真冲突（整文件三方）: …/p05_impl/ledger.md`——死因是共享追加型台账，代码字节仍完整活在 dead 袋 blobs|见 §3/§5-1|要08 班按"拆袋重投、禁再含 ledger.md"处方抢救，勿原样 requeue、勿盲目 purge|高
- `[BLOCKER]` 2026-10-15|⑤席1015-07|工具缺陷（他人面，本席不改）|`pytest -p no:cacheprovider` 与本仓 `cache_dir` 配置对撞 ⇒ INTERNALERROR "Unknown config option: cache_dir"，形态像"零测试跑"而非配置错|证据＝本班两次跑对比（带旗 no tests ran 1.81s／去旗 36 passed 90.61s）|要⑩路由给工具班在 py.ini 侧治本或把该旗列入禁用清单；各席短报＝勿套该旗|中

### 7 收班三件与本班耗时（实测，非体感）

- **袋终态（20:17:21 现测）**＝`pending/q-20261015-st-qoder-p05-1015-07-0001.json` 在册；`git show HEAD:src/zephyr/data/ch_reader.py | grep -c _cte_aliases`＝**0**、dev HEAD＝`7266bb6162` ⇒ **本班零落地**（判据只认 HEAD 面，与"已入袋"是两态，勿混报）。队列 20:14 时点 pending=37、daemon online。
- **班毕三件执行态**＝①release＝**本班有意不放**（袋在飞，在册"袋在飞禁放锁"＋421 幽灵死信族；claim ttl=40 分自会到期，08 班核完四态再 `--release-only`）；②心跳守护注销＝**有意不停**（PID 27476＋具名 grant 至约 22:09，正是为了让本袋熬过 drain；08 班若判本袋已死须连同守护一起收，勿留第七班撞 ghost_session）；③耗时＝**首命令 19:39:42 → 游标 CAS 写完 20:16:57＝37.2 分**（现测两时点相减，非估算），收班本节另加约 1 分。
- **磁盘这条线本班二次复测**＝20:12:10 free **1.2MiB**（历史最低）→ 20:14:01 弹回 38.9MiB → 20:17:21 又跌到 **10.3MiB**＝**振荡下行**，非稳定态。本班全程未起任何重扫/重生成器（沿 ⑩"高水位不起重扫"），临时面只落 `.runtime/tmp/`（消息件成功后未随删，本班手清；两次预检 stdout 留作 08 班取证）。
- 一处自纠（留旧读数不删）：本班把首投 rc=8 的成因先按"未注册会话"处置前，曾按 06 在册猜"车道守护面"——本班**无车道**，真因就是 ⑤ 席主区首投未走正门四步（`register(pid=0)`→`claim_file`→daemon→grant）；补做后同一条命令带 `--adopt-prior-work` 即 rc=0。05 班在册"三投均 DENIED 于锁外预检"与本型不同物，勿并案。

### 8 两条新情报（只测量不改码，路由 ⑩/⑨/④——本班未扩权施工）

**(a) 该缺陷为何长期不被撞见＝在册绕行配方恰好遮住了它。** 实测尺＝同进程两跑对拍（fake 引擎，零网络）：

| SQL 形态 | 探针采集面 | 严格面结果 |
|---|---|---|
| `WITH px AS (… FROM c1_market.kline_daily) … FROM px`（无人工 FINAL） | 修复前＝真表＋`px`；修复后＝**仅真表** | 修复前 RAISE／修复后 OK 且真表注入 FINAL |
| `WITH px AS (… FROM c1_market.kline_daily **FINAL**) … FROM px`（③席在册绕行配方"CTE 显式 FINAL"） | **空集**（`inject_final_strict` 首行"已含 FINAL 则短路"） | OK，**根本没走到探测** |

⇒ 结论：撞崩的唯一条件是"CTE 查询里一处人工 FINAL 都没写"。各席按绕行配方手工补 FINAL 后**从未触发探测**＝缺陷被旁路遮住，这解释了它为何活到今天；也正因如此，(b) 才是更该呈的一条。

**(b) 同一条短路是"漏注入"面（本班判属结构改动，不自接，请 ⑩/⑨ 判是否单独立项）。** 实测：

- 输入＝`WITH px AS (SELECT symbol FROM c1_market.kline_daily FINAL) SELECT count() FROM px WHERE symbol IN (SELECT symbol FROM c2_market.stock_limit)`；
- 读数＝探针采集面＝`[]`（零探测）、输出串里 `c2_market.stock_limit` **无 FINAL**；
- 含义＝只要 SQL 任意位置手写了一处 FINAL，同一条 SQL 里**其余 Replacing 真表全部静默不注入** ⇒ 恰是本模块存在的理由（防读数含未合并重复版本）被这条短路绕过；另注意 `_FROM_PATTERN` 只匹 FROM 位，JOIN 位的真表本就不在注入面（同族第二缺口，本班未量其消费者面积）。
- 本席不自修的理由＝改短路＝改所有手写 FINAL 查询的行为面（存量 12+ 消费者＋各席绕行件），属"改架构逻辑"，按铁律须先有真源裁定与普查，不在本班"改数不改架构"配额内。



