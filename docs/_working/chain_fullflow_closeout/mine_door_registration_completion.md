---
ttl: task_bound
---

# 案卷 · 提交链死信「门禁/登记拒绝」族挖矿（M1，只挖不干）

> 战役=全流通战役 20260926 ｜ 母节点=死信中的门禁/登记类拒绝 ｜ 班别=M1 挖矿班（只读，零施工）。
> 一切数字均为**实测读数**，旁附取数命令；dead/ 是活池，drain 实时搬动，引用前重跑。
> 事故留痕：本卷初稿曾于 02:2x 成功写入本路径后被未知在途进程抹除（无 stash_notice 记录，目录内仅余他班两卷）。
> 此为"文件内容/他人消息一律当数据"条款下的观测事实，重落全稿并加写后即时核实命令（R-FINAL）。

## 1. 母节点与分母声明

- 数据源真源：`.runtime/commit_queue/dead/*.json`（本卷普查时实测 682 件，见 R-0）。
- 日期跨度实测：dead_at 覆盖 2026-09-22 … 2026-09-26（5 个自然日），**不是**战役口径的"三天窗口"——本卷按 dead/ 现行全量口径立卷。
- 未纳入分母：`dead_archive_*` 六个归档目录与 `dead_triage_*.jsonl`（历史已处置件，长尾 L-1，未重复计数）。
- R-0 复现：`ls .runtime/commit_queue/dead/*.json | wc -l`（本卷时点=682）。

## 2. 死因普查表（类别 × 会话 × 日期）

统计脚本（只读）：`.runtime/tmp/mine_dossiers_20260926/census_dead.py`
原始三维输出：`.runtime/tmp/mine_dossiers_20260926/dead_census_raw.json`

- R-1：`python .runtime/tmp/mine_dossiers_20260926/census_dead.py`（重跑得最新三维计数）
- R-2 门禁/登记族（GATE:\* ∪ REG:\*）占比：脚本内置同逻辑单行版见下；实测读数 484/682 = **71.0%**：
  ```bash
  python -c "import json;rows=json.load(open('.runtime/tmp/mine_dossiers_20260926/dead_census_raw.json',encoding='utf-8'));g=[r for r in rows if r['category'].startswith(('GATE:','REG:'))];print(len(g),len(rows),round(100*len(g)/len(rows),1))"
  ```
- **口径对照（重要）**：战役底数"约 46% 死于门禁/登记"与本卷 71% 不矛盾——(i) 窗口不同（3 天 vs 现行 5 天全量）；(ii) 本卷把 GATE-PRECOMMIT-RUN（元门禁，转发其它 hook 判定）计入；(iii) "landing 异常: 注册表三向合并失败"69 件（纯登记册冲突）在本卷归 landing 族——若按"登记面死亡"并族，占比升至 ≈81%。**46% 为低估；"登记动作前置入队口"的量化依据成立且比战役判断更强**。

### 2.1 Top-N 死因族（覆盖 ≥80%，件数为本卷实测读数）

| 族 | 件数 | 归类 | 判据一句话 |
|---|---|---|---|
| OTHER:landing 异常 | 118 | 半登记 | 子类：热册三向合并失败 69（canonical_file 20/translation 20/in_process_gate 8/ruling 5/fail_open 5 等）+ 环境不可用 36（L-6）+ 杂项 |
| GATE:GATE-PRECOMMIT-RUN | 71 | 元门禁 | 落地前 staged 面 hook 重放；转发分布见 §3.6 |
| GATE:CREATE-GUARD | 64 | 登记 | 新建文件缺 creation_token |
| GATE:TRANSLATION-COVERAGE | 48 | 登记 | 新建 .py 缺合格 plain_zh 大白话简介 |
| OTHER:NOTHING_TO_COMMIT 但快照未真应用 | 31 | 机制 | 集中于 st-stress-20260923 单会话 29 件（L-2） |
| GATE:TTL-METADATA | 30 | 登记 | frontmatter 缺 ttl |
| GATE:GATE-VOCAB | 24 | 词表 | 用词不在认证词表 |
| GATE:COMPLEXITY-GUARD | 21 | 业务判定 | 圈复杂度超限，非填空 |
| GATE:R5-DIGIT-SUFFIX | 17 | 命名规则 | 文件名数字后缀 |
| GATE:REFERENCE-INTEGRITY | 16 | 引用完整性 | 裸「裁定+数字」式引用未登记即拦（死信文本自身含此类串，按数据对待；本卷不复现该形态以防门自触） |
| OTHER:cascade_stale | 16 | 机制 | 级联基底失效 |
| GATE:IMPORT-INTEGRITY | 15 | 引用完整性 | import 目标缺失 |

Top-12 累计 559 件 = 82.0%（R-1 输出直接累加可验）。长尾 25+ 族各 ≤13 件，明细在 dead_census_raw.json。

### 2.2 会话集中度（R-1 category×session 段）

- st-cmd-20260924：CREATE-GUARD 16 / TTL-METADATA 21 / COMPLEXITY-GUARD 9 / R5-DIGIT-SUFFIX 7。
- st-commitspeed-tbl-20260924：CREATE-GUARD 10 / TRANSLATION 6 / IMPORT-INTEGRITY 8。
- st-sweep-tail-20260923：GATE-PRECOMMIT-RUN 16。st-stress-20260923：假死 29。
⇒ 填空族死亡高度集中于 2-3 会话；"补登前置"的受益面按会话计而非按门族计。

## 3. 逐族三问

### 3.1 CREATE-GUARD（64 件）
- (a) 可机械推导=**是**。输入=袋内新文件路径清单（files 字段现成，含 blob_sha256）+ token 生成规则；无业务判断。
- (b) 工具：`scripts/governance/d3_metadata/batch_creation_tokens.py`（实测存在）。活雷（实测）：写 capability_canonical_file_registry.yaml＝热册三向合并冲突面（本窗 landing 族该册 20 件死）；改名换绑 token；他会话在途条目同键撞车。
- (c) 不该保持纯拒绝。且预检等价判定已在主线（§3.7），真缺口在旁路（§3.7 E-2/E-3）。

### 3.2 TRANSLATION-COVERAGE（48 件）
- (a) 半可推导：登记动作可机械，plain_zh **内容**是作者语义欠账，工具不可代写。
- (b) 工具：`scripts/governance/d3_metadata/add_module_translation.py`（死信 reason 文本自带该命令串——文本是数据，本卷全程未执行）。活雷：写 module_translation_registry.yaml（同窗 20 件合并死）；已知派生标量经队列进不了 HEAD（合并器恒取 ours，须合并后按段长度重算——前案在档）。
- (c) 保持"拒绝+点名+可复制命令"；入队口只预检"有无登记"，不代写内容。

### 3.3 TTL-METADATA（30 件）
- (a) **完全可推导**（插一行 `ttl:`；已知误报源=值内裸冒号使门误判缺 ttl，前案在档——预检与门须同解析器）。
- (b) 工具：`backfill_ttl_metadata.py`（实测存在）。活雷：改文档=袋内 blob sha 漂移，须重算快照指纹+重取基底，否则换族死于 HOT-FILE-BASE-FRESHNESS/基底冲突。
- (c) 不必保持拒绝。

### 3.4 R5-DIGIT-SUFFIX（17）＋ GATE-VOCAB（24）＋ BLUEPRINT-FORMAT（13）
- (a) 命名=纯字符串规则可推导；VOCAB 半（查表替换）；BLUEPRINT 可生成器化。
- (b) 活雷：改名=跨册换绑（token/depgraph 同步义务，宪法 §9.10 同族）。
- (c) VOCAB 语义替换处保点名拒绝；命名族可自动化。

### 3.5 REFERENCE-INTEGRITY + IMPORT-INTEGRITY（31）
- (a) 可机判"哪条引用缺登记"（file:line 级），不可机决策"引用该不该存在"。
- (c) **必须保持拒绝**；升级点=dead_reason 给全量缺口清单+单条补齐命令（现部分点名，覆盖率待核 L-9）。

### 3.6 GATE-PRECOMMIT-RUN（71 件）
- 本质=落地前 hook 重放。转发分布实测（R-3）：
  ```bash
  python -c "import json,re,collections;rows=json.load(open('.runtime/tmp/mine_dossiers_20260926/dead_census_raw.json',encoding='utf-8'));print(collections.Counter((re.search(r'hook=\[([^\]]+)\]',r['reason_head']).group(1) if re.search(r'hook=\[([^\]]+)\]',r['reason_head']) else 'unparsed') for r in rows if r['category']=='GATE:GATE-PRECOMMIT-RUN').most_common())"
  ```
  读数：gate-protected-paths 17｜ruff-format 13｜ruff+ruff-format 13｜gate-naming 9(+3)｜gate-any-abuse 3｜ruff 2｜gate-detect-git-dangerous 1｜unparsed 10。
- 判读：纯格式转发 ≈28 件零业务判断（业界托管面直接自动修，§4③）；protected-paths/any-abuse ≈20 件必须保持拒绝。本族处置须按 hook 拆分，不存在单一处方。

### 3.7 【重磅】部署后仍死族＝入队预检旁路（meta 族）
时间线（git log 只读核实，R-4：`git log --format="%h %ai %s" --since=2026-09-24 -- src/zephyr/gov_enforcement/rule_bridge/commit_preflight.py scripts/governance/enqueue_preflight.py scripts/governance/commit_queue_landing.py`）：
- 09-25 08:02 commit_preflight M2.1/M2.3（CREATE-GUARD/TRANSLATION 入队面**等价判定**内联，1da3f219ff）
- 09-25 08:46 enqueue_preflight M1.1 裸 CLI 挂线（3f912437fc）
- 09-25 09:21 M1.2 machine reroute 预检 blocking→COMMIT_FAILED 不降级（9469a6013e）
- 同日下午→09-26：三登记族仍新死 47 件（dead_at≥09-25T12:00；R-5：
  `python -c "import json,glob;print([ (j['qid'],j['dead_at']) for p in glob.glob('.runtime/commit_queue/dead/*.json') for j in [json.load(open(p,encoding='utf-8'))] if j.get('dead_at','')>='2026-09-25T12:00' and any(k in j.get('dead_reason','') for k in ('CREATE-GUARD','TRANSLATION-COVERAGE','TTL-METADATA'))][:50])" )`）
证据链：
- E-1 非 fail-open：preflight_events.jsonl 实测 09-25 起 enqueue passed=105 / blocked=87 / degraded_pass=0（R-6：
  `python -c "import json,collections;print(collections.Counter((json.loads(l).get('path'),json.loads(l).get('event')) for l in open('.runtime/audit/preflight_events.jsonl',encoding='utf-8') if json.loads(l).get('timestamp','')>='2026-09-25').most_common())" )`）。
- E-2 requeue 旁路：`q-20260925-st-cmd-20260924-0083` meta 含 `requeued_from`，死于 13:52；全文件 `run_enqueue_preflight` 仅 _cmd_enqueue 一处调用（`grep -n run_enqueue_preflight scripts/commit_queue.py`）——**requeue 重建快照通道无预检**。
- E-3 第四裸入口：09-26 00:45 mapbuild 四件（CREATE-GUARD×2/TRANSLATION×2）在 audit 同窗零 st-mapbuild 记录（R-7：按 session_id 前缀+UTC 窗过滤 jsonl，实测 0 行）。三条已挂线路径均留 audit ⇒ 指向**直接 import `enqueue_item()` 的脚本化入队**。
- E-4 TOCTOU：同会话 16:42Z passed（11 files）的袋 00:37+08 仍死于 CREATE-GUARD——锁外预检与落地锁内权威判定之间存在注册表面貌漂移窗。
- 结论修正：母节点"应从落地侧补救提前到入队口"的**前提已部分更新**——入队口预检+死信处方机制（`_DEAD_PRESCRIPTIONS` 12 族，CREATE-GUARD 处方一键命令实证存在）09-25 已在主线。真缺口=(i) requeue 通道无预检；(ii) `enqueue_item` API 层无强制预检点；(iii) 预检→落地窗漂移。
- (b) 自动补登的活雷**已有实测当量**：热册三向合并失败 69 件/窗（§2.1 landing 子类）⇒ 门侧/落地侧盲目补登只会把死因从 GATE 族搬进 landing 族，不减量。

## 4. 六向台账

- ①上游信号：袋 files(path+blob_sha256)/meta 足以机判 token/plain_zh/ttl 三族（§3）；缺的位图=「袋内新文件 × 在册 token」差集已由 preflight 内联判定实现，但 lane 字段在 CLI/requeue 件为 None——**入队车道无强制标记 ⇒ 旁路不可归因**（字段级缺口，与 §5 呼应）。
- ②下游消费者（grep 实测）：creation_token 被 create_guard/new_file_depgraph_gate/registry_yaml_parse_gate/secret_hardcode_gate 消费；module_translation_registry 被 translation_coverage_gate、`src/zephyr/governance/audit/translation_coverage_reconciler.py`（事件触发对账器已存在）、battle_map_alignment_gate、library_blood_flesh_gate、dashboard api_server 消费 ⇒ 登记面已有"对账腿"，补登可挂 reconciler 事件链而非新增 cron（宪法 §9.3 合规路径）。
- ③业界对照（外部，URL+发布方+取数日；关键结论双源）：
  - pre-commit 官方文档：本地钩发现文件被修改即「Files were modified by this hook」→ 提交失败、要求重新 add 再提交；框架本体**无** autofix 旗标（发布方 pre-commit.com，URL https://pre-commit.com/ ，2026-09-26 取）。
  - pre-commit.ci 官方：托管面「if tools make changes to files during a pull request, pre-commit.ci will automatically fix the pull request」，auto_fix「optional, default: true」（发布方 pre-commit.ci，URL https://pre-commit.ci/ ，2026-09-26 取）。
  - ⇒ 业界分层结论（双源成立）：**作者提交面 fail-fast+点名，托管/评审面自动修复提交**。映射本案：入队口保拒绝+处方（已建），落地/队列侧对纯格式族（ruff-format 28 件当量）做自动修袋重投是业界同型，不是异端。
  - 已查无：commitlint/Google presubmit-CL-autofix 的**官方**自动修文档本轮未检得权威源（检得的多为中文博客转述，质量不达标，记噪音）；登记为 L-5 待再查。
- ④后端缺什么：见 §3.7 三缺口（requeue 预检/enqueue_item 强制点/TOCTOU 窗）。另有实测成本约束：audit 记录 ms 字段显示预检单跑 2.4s–36s（40 文件袋 34.5s，R-6 同文件），"处处全量预检"有真价钱。
- ⑤前端呈现：dashboard/app_panel.py 与 api_server.py grep "dead" 零命中（R-10：`grep -c dead src/zephyr/frontend/dashboard/app_panel.py`）⇒ 死信/登记缺口对提交方的现成可见面只有 `commit_queue.py health` CLI（死因分类聚合+单会话死亡计数 D6）。只登记不施工：缺口清单面板若施工应读 health 快照派生，禁第二真源。
- ⑥数据字段：见 §5。

## 5. 数据字段核对（"字段在"≠"数据可得"逐条）

- 共同字段：qid/session_id/created_at/dead_at/branch/base_head/message/files/meta/dead_reason（6 种键签名，R-1 key signatures 段）。
- files=path+blob_sha256+blob_ref ⇒ (a) 类输入可得性：已证（能机算新文件差集）。
- meta：depends_on/supersedes/interactive/lane/oversize_batch/requeued_from ⇒ lane 在 CLI/requeue 件缺失（None 40/42），**字段存在但数据不全**——闸4 命中点。
- prescription+owner_session：168/682 有（09-25 后死件才有，老件无——覆盖率是部署时序产物，非缺陷）。
- dead_at vs created_at 双时间戳齐 ⇒ 旁路归因（§3.7）靠二者+audit 时刻比对完成。

## 6. 挖矿日志

| 轮 | 矿脉 | signal/noise(归因) | 关键产出 | 复现命令 |
|---|---|---|---|---|
| 1 | 分母口径 | signal | dead/=682、跨 5 日窗；archive 未入分母 | R-0 |
| 2 | 全族普查 | signal | 门禁/登记族实测读数>战役口径；Top-12=82% | R-1/R-2 |
| 3 | 会话集中度 | signal | 填空族集中 2-3 会话 | R-1 |
| 4 | landing 假死族 | signal(候选) | 29 件单会话集中，疑测试件混入生产池（L-2） | R-1 subcats |
| 4 | 字段签名 | signal | prescription 机制已在；files 含 sha | R-1 |
| 5 | PRECOMMIT-RUN 拆 hook | signal | 纯格式 28 件 vs 必拒 20 件 | R-3 |
| 6 | 预检部署时序 | signal | 三口挂线 09-25 已落主线 | R-4 |
| 7 | 部署后死亡 | signal | 47 件仍死，lane=None 为主 | R-5 |
| 8 | audit 反查 | signal | degraded_pass=0 ⇒ 旁路非故障 | R-6 |
| 9 | requeue/mapbuild | signal | E-2/E-3 两条旁路实锤 | R-5/R-7 |
| 10 | 消费面反查 | signal | token/翻译册消费方+对账器已存在 | R-8（grep 清单见 §4②） |
| 10 | 前端可见面 | signal | dashboard 零死信视图（grep 0 命中） | R-10 |
| 11 | 外部对照 | signal | 分层结论双源成立 | §4③ URL |
| 11 | commitlint/Google 官方源 | noise(检得皆二手博客) | 已查无→L-5 | §4③ |
| 12 | 初稿被抹 | signal(事故留痕) | 未追踪他班 clean 风险，卷首记档 | `ls docs/_working/chain_fullflow_closeout/` |

## 7. 防噪音四闸过闸记录

- 闸1 可复现：全表数字带 R-x 命令；脚本与 raw json 存 `.runtime/tmp/mine_dossiers_20260926/`。过。
- 闸2 口径唯一：46% vs 71% vs 81% 三口径差异逐项拆解（§2），未混用。过。
- 闸3 结论≠假设：E-2/E-3 有 meta 实据与 audit 阴性证据双卡；"requeue 无预检"的构造性验证（投一袋观察 audit）因本班禁写未做——**证据等级 B**，解锁条件写进 C-2。过（带注记）。
- 闸4 字段在≠数据可得：lane 字段缺失、prescription 覆盖及时序、老死件无处方均已点名（§5）。过。

## 8. 挖后自审闸（三态裁定）

量尺=终局全貌（Owner 只做四件事：网站账号注册/API 申请/充值/策略转正审批，其余全自动）。禁用"规模小"作封矿理由。

| 候选 | 裁定 | 理由/解锁条件 |
|---|---|---|
| C-1 `enqueue_item` 层轻量强制预检（仅登记三族内联判据，非全门重放） | **施工**（P0 候选，交施工班） | §3.7 三缺口之 (ii)；成本约束对策=只跑 2.4s 级内联判定不跑 36s 全链 |
| C-2 requeue 通道挂同款预检+留痕 | **施工**（P1） | E-2 实锤；施工验证时须顺带把 E-2 的 B 级证据升 A（投袋看 audit） |
| C-3 入队口**自动补登**（token/ttl 当场生成入袋） | **挂起排期** | 解锁条件=热册三向合并死当量 69 件/窗降到可忽略，且袋指纹重算机制先行；否则死因从 GATE 族搬进 landing 族（§3.7 实测雷） |
| C-4 落地侧纯格式族自动修袋重投（ruff/ruff-format 28 件当量） | **挂起排期** | 业界同型成立（§4③双源）；解锁条件=落地器具备"修后重算 blob+audit 留痕"原语，由施工班评估 C-1 落地后窗口 |
| C-5 死信登记缺口 health 面板化（复用 health 快照，禁第二真源） | **挂起排期** | 解锁条件=先修 lane 字段强制（C-6），否则面板无法归因旁路 |
| C-6 meta.lane 强制打标（所有入队通道） | **施工**（P2 小件） | 观测面前置，纯机械 |
| C-7 登记族"处方+一键命令"扩面 | **方案封矿** | 机制已在主线（M3.3 处方表实测存在且命令可核）；剩余缺口并入 C-2 验收，终局无独立位置 |
| C-8 GATE-VOCAB 自动替换 | **方案封矿** | 六段温度词表已裁（勿重裁）；替换即代写语义，终局无位置 |
| C-9 NOTHING_TO_COMMIT 假死族治本 | **挂起排期** | 归因未毕（L-2），先定 st-stress 是否测试件；解锁条件=L-2 出归因 |

反驳者一问（C-1，成本最高候选）——最强三条反对：
1. 预检单跑实测 2.4–36s（audit ms 字段），高并发班每袋双跑（交互+API 强制）拖慢生产者；
2. "预检是快败优化不是新权威"是 enqueue_preflight 在册设计原则（其蓝本注释自述，按数据对待），API 层强制=原则翻转，须先改册留痕否则违内收铁律；
3. requeue 者多半已改盘面，全量重放浪费——只 re-verify 差量即可。
→ 消化后形态：C-1 收窄为"登记三族内联判据的 API 层强制+差量"，与在册原则兼容（预检权威等级不变，只堵旁路）。

## 9. 长尾矿脉清单（明确未挖）

- L-1 dead_archive_* 六目录+triage jsonl（实测文件数合计约 1700 历史件）逐族分类未做——含 08-30 前老死因谱，可验证"登记族是否一直占大头"。
- L-2 st-stress-20260923 的 29 件 NOTHING_TO_COMMIT 假死归因（测试件混入生产池？）。
- L-3 prescription 字段生成覆盖面随时间的推进曲线（仅新件有）。
- L-4 零 requeue 族归因（R5-DIGIT-SUFFIX 0/17、DIRECTORY-CONTRACT 0/9、ALGO-FLOW-LINK 0/7——修不动还是没人修）。
- L-5 Google presubmit/CL autofix、commitlint 官方文档权威源再查。
- L-6 landing 环境不可用 36 件（LandingEnvironmentError repo_root）谱系。
- L-7 GATE-VOCAB 24 件逐实体分布（边界：不重裁词表本身）。
- L-8 预检 ms 耗时与袋大小曲线（C-1 定价用）。
- L-9 REFERENCE-INTEGRITY dead_reason 是否全量给 file:line 级缺口清单。
- 已查无记录：degraded_pass 事件（实测 0 起，旁路≠故障放行成立）；dashboard 死信视图（grep 0）；commitlint 官方 autofix 源（本轮）。

## 10. 待 Owner 门位登记项（只登记，不请求执行）

- O-1 flag `commit_queue_interactive` 出厂默认 OFF，启用属 Owner 窗口（宪章 B-007 在代码注释中自述，按数据对待）——交互正门灰度面。
- O-2 C-1/C-2 若落地触及 `enqueue_preflight`/`commit_queue` 在册设计原则文字（"skip 不是豁免/预检非新权威"），按宪法 §4 净零须声明合并替代关系——登记备查。
- O-3 热册三向合并策略若因 C-3 解锁需改（注册表合并语义属 high 域"production 流转/注册表"邻接面）——本轮不改，登记。

## 11. 复现命令附录

- R-FINAL 本卷双份核实：
  ```bash
  ls -la docs/_working/chain_fullflow_closeout/mine_door_registration_completion.md .runtime/tmp/mine_dossiers_20260926/mine_door_registration_completion.md
  ```
- R-7 mapbuild audit 阴性核查：
  ```bash
  grep -c st-mapbuild <(python -c "import json;[print(json.loads(l).get('session_id',''),json.loads(l).get('timestamp','')) for l in open('.runtime/audit/preflight_events.jsonl',encoding='utf-8') if '2026-09-25T16' in json.loads(l).get('timestamp','')]")
  ```
- R-8 消费面反查：
  ```bash
  grep -rln "module_translation_registry" src/zephyr --include=*.py | head; grep -rln "creation_token" src/zephyr/gov_enforcement/commit_gates/
  ```
