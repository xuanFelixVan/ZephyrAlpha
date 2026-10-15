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

