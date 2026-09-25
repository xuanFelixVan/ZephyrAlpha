---
ttl: task_bound
title: ADJ 案卷·AI 层批落地与三条被暂禁 gate 的翻回前置
---

# ADJ · AI 层批文（12 项）+ 三条 gate 翻回

## ① 一句话问的是什么

三条安全类 gate 为解锁落地被临时关掉、名册里挂着"批落地同批翻回"的欠条——问的是：**AI 层大袋落地那一批里，必须同时翻回哪三条 gate、翻回的前置条件是否已满足，以及"12 项批文"到底指哪 12 项**。

## ② 现状实测

### 2.1 三条被暂禁 gate 的确切 gate_id（实测行号）

真源 `docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml`：

| gate_id | 行号 | priority | module_path / factory_function |
|---|---|---|---|
| `REAL-KEY-REFERENCE-SCAN` | :707-712 | 149 | `zephyr.ai_layer.redline.negative_list_gates` / `make_real_key_reference_scan_gate` |
| `TASK-ORDER-DOCS-LOCK` | :713-718 | 150 | 同上 / `make_task_order_docs_lock_gate` |
| `CONSTITUTION-LINE-LIMIT` | :719-724 | 151 | 同上 / `make_constitution_line_limit_gate` |

三条同挂一行同款注记（实测原文）："09-26 总指挥暂禁用（落地环境解封）：module 在 st-ailayer-final 245 件批内未落 HEAD，名册先行=同源断裂致全部 landing 死信；**AI 层批落地同批翻回 enabled: true**"。
各自职责（实测注记）：NL-2 判据② own-diff 中"实盘真键字样"引用拦截 / NL-5 同会话 own-diff 施工产物×任务书互斥 / NL-3 判据② `AGENTS.md ≤300 行`硬上限断言（宪法 §6）。

**注**：本册另有 4 条 `enabled: false`（`CAPABILITY-OVERLAP` :90、`GATE-VOCAB` :208、`ALGO-FLOW-LINK` :349 等，实测共 7 条 false），其注记是"Owner 批准 B 方案/187 件落地后恢复"，**不属"AI 层批落地同批翻回"三条**，勿混。

### 2.2 为什么"名册先行"会打死全部 landing（代码级实测）

- `src/zephyr/gov_enforcement/rule_bridge/gate_auto_registrar.py:8` [INVARIANTS]（实测原文）：**fail-closed（裁定#351）——任一 enabled gate 装载失败（YAML 损坏/import 失败/getattr 失败/…）→ 抛 `GateAutoRegistrationError` 阻断提交并逐台报 gate_id+错误**；同段末："**enabled=false 跳过**"。
- `:13` [ERROR_CONTRACT]：抛错阻断 `GitCommitGateway.__init__`（即阻断一切提交），"坏门静默免检比提交冻结危害更大；可用性代价已被裁定#351 接受"。
- 实测：三条 gate 的条目**已在 HEAD 名册中**（`git show HEAD:…in_process_gate_registry.yaml | grep -c` = 3），而其 module 在 HEAD **不存在**（`git cat-file -e HEAD:src/zephyr/ai_layer/redline/negative_list_gates.py` → NO）；同路径文件**在主区盘上存在且可 import**（实测 `importlib.import_module(...) → IMPORT OK`）。
- → **当前的 false 状态正是防止全站提交冻结的活锁**。任何"先把 enabled 翻成 true、等模块落地再对齐"的操作顺序，都会立即触发全仓提交不可用（fail-closed 无差别阻断），必须靠 `emergency_commit` 逃生。

### 2.3 AI 层袋的真实体量与当前死因链（实测）

| qid（dead） | dead_at | 件数 | 实测死因 |
|---|---|---|---|
| `q-20260925-st-ailayer-final-20260924-0010` | 09-25 20:35:40 | 187 | `GATE-VOCAB`：新增 .py 含词表硬编码（应自 `*_vocabulary.yaml` 动态加载） |
| `q-…-0011` | 09-25 20:55:57 | 187 | `ALGO-FLOW-LINK`：8 处 external 锚指向不存在的 `docs/03_modules/_domain_ai_layer/algo_flow/*.yaml` |
| `q-…-0012` | 09-25 21:06:47 | 187 | `GATE-PRECOMMIT-RUN`：hook `gate-algo-flow-marker` Failed——5 个 src/zephyr 模块缺 `# [ALGO_FLOW]` docstring 标记（列名见 dead_reason 原文） |

- 体量实测：`files=187`（**非 245**，亦非任务书所称"190+"）；构成：`src/zephyr/**` 70 件、`tests/ai_layer/**` 64 件、`tests/intelligence/**` 9 件、`scripts/ai_layer/**` 9 件、`docs/_working/**` 14 件、`config/*` 若干。`branch=dev`，`base_head=3cdafddf1d45…`（有记基线，优于 emoreplay 袋）。
- 死因链性质：**三死皆是"批次自洽性"而非功能缺陷**——0011 缺的是 0012 要补的 algo_flow yaml/标记（同一件事的两侧），说明该会话在逐轮自我修复中；当前 pending/processing 内已无 ailayer 袋（实测 pending=3：st-cmd 1 件 + st-qmine 两袋），ailayer 线在 21:06 后停摆。
- 名册一致性：`total_gates` 字段=102 且 =len(gates)=102（实测），翻转 `enabled` 不改条目数 → 不触计数对账；真正的计数战场在 `gate_registry.yaml`（`commit_queue_landing.py:1609` 记录了该册 total 被直提又被陈旧袋压回的历史）。

### 2.4 "12 项批文"到底是哪 12 项（实测枚举结果=只能枚举 11）

真源链：`docs/_working/ai_layer_vision/P1_final_report_20260924.md:114`"待 Owner 批文 12 项/受阻 3 项：全部登记（P1_full_construction_inventory.md），零代裁" → `P1_full_construction_inventory.md:92`"⏸ 待 Owner：12 项（全部登记在**夜报待批 11 项+R2 增项**，禁代裁）" → 夜报 `P1_night_report_20260923.md:41-56` §要素四。

夜报实列 **11 项**（逐条照抄编号，实测在盘）：
1. OBJ_M-#1 路由终批（批文对象已备好=`OBJ_M_models/C6_routing_diff_proposal.md`，api_providers 零增删）
2. OBJ_S-#2 `secret_registry` 增 `ai_exposure: forbidden` 字段（预审：S1 deny-list 已功能等价，可缓批）
3. L4-#3 `intake_exam_due` 契约对齐（需定向：不加该边 or 授权 L2 侧修订）
4. L5-#3 任务书 schema provenance 增补（附录级变更待定向）
5. L6-#2 墓碑 TTL 清理判据+净删门（清理提案生成器未建=等此项）
6. C4 打分口径常数一次确认（`model_scoring_policy.yaml` P 权重 0.5/0.3/0.2+αβ 0.6/0.4+档界 0.80/0.60，按夜批已原值生效在册，追认即可）
7. OBJ_M DESIGN §3.3 `external_missing_remedy` 自相矛盾定稿（0.5+0.2=0.7 回流 MCE vs 权重归 0.8，字面致 P 破 [0,1]）
8. C8 排班 `--force` 再生时机（一行命令 `generate_resource_profile_registry.py --force`，请排错峰窗）
9. L1 施工项 7（外扫节拍宿主）T3 双前置（追认+裁定登记）
10. L7 `DESIGN.md` 状态翻转 design_v1→定稿（即解锁 L1 项 9 先验消费接口）
11. 治理立案类保持既有节奏（OBJ_R-#5/#6、OBJ_T-#1/#2、L4-C7、L7-#2、L5-#2 六子项）

**第 12 项不可枚举**：`P1_full_construction_inventory.md` 与 `LEDGER_final.md:24` 均记"待 Owner 11 项在册"，而 `P1_final_report:114` 记 12 项；全 `ai_layer_vision/` 目录 grep "R2 项" 实测 8 处**全部是已完成接线项（R2 项1/2/4/5/7/8）而非待批项**。→ **"12" 这个数在三份真源之间自相矛盾，且第 12 项在真源里查无实体**。这正是本仓反复出事故的"文档计数漂移"形态，须按宪法 §4.3 处理：以可枚举清单为准，不以散文计数为准。

## ③ 可选路径

**路径 A：AI 层袋续投（该会话自修后重投），落地批内同批翻回三条 gate**
- 前置：①5 个模块补 `# [ALGO_FLOW]` 标记 + 8 个 algo_flow yaml 入袋（两死因同源，一次可解）；②词表硬编码改动态加载；③三条 `enabled: true` **写在同一 commit**。
- 代价：187 件单袋=连坐面大（本仓 §2.4"gate+自家测试同批是合法的"，但 `--allow-multi-domain` 须留痕）。
- 不可逆点：翻回即生效——三条 gate 从此对全仓提交有拦截力（尤其 `CONSTITUTION-LINE-LIMIT` 直接管 AGENTS.md ≤300 行，`REAL-KEY-REFERENCE-SCAN` 管真键字样）。

**路径 B：袋拆两批——功能件先落（保持 false），三条 gate 与其 module+测试单独一批同批翻回**
- 代价：多一次排队；需要精确圈出"module+测试+名册三件套"（实测该 module 与其测试均在 187 件内：`src/zephyr/ai_layer/redline/negative_list_gates.py`、`tests/ai_layer/redline/test_negative_list_gates.py`）。
- 不可逆点：与 A 同，但把"提交冻结"的风险窗口压到最小；**唯一禁忌顺序仍是 flip-before-module（2.2）**。

**路径 C：不翻回，改为把三条 gate 条目从名册摘除（退役）**
- 代价：负净零（宪法 §4 要求声明替代），且三条拦的是"实盘真键引用/任务书互斥/宪法行数"，均属资金与治理红线，摘除=三条防线永久免检。
- 不可逆点：高——摘除后需重新立法才能装回。

## ④ 专业对照（外部论据，URL+发布方+年份；链接均经本车道 2026-09-25 检索/抓取核验）

1. **"控制项临时不可用时须以补偿控制顶替、且例外要有边界"是安全控制的正规结构**：NIST SP 800-53 Rev.5《Security and Privacy Controls for Information Systems and Organizations》（NIST CSRC，2020-11 发布，页面经抓取核实存在，标题逐字核实）确立了"控制项+例外须留痕"的框架；业界对该框架的术语释义亦明确"compensating controls=在原始控制不可实施时采用的替代措施"。
   - https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final （NIST，2020）
   - https://www.fortinet.com/cn/resources/cyberglossary/compensating-controls （Fortinet 网络安全术语库，页面更新 2026-06）
2. **CIS Controls 把"控制项清单+实施顺序"作为可核查资产**（CIS Controls v8 生态），其第三方实施指南明确"控制项不得静默缺失，须以书面例外/补偿措施登记"。
   - https://www.manageengine.com/au/cis-critical-security-controls/ （ManageEngine/Digital Summit，页面更新 2026-08）
   （两条来源独立：美国联邦标准出版页 / 厂商术语库与实施指南。共同支持"暂禁可以，但必须有到期与替代留痕"，不支持"长期挂着 false"。）

## ⑤ 风险（做错的最坏情形）

- **资金安全：有真实暴露面**。`REAL-KEY-REFERENCE-SCAN`（NL-2）拦的是 own-diff 中**实盘真键字样**引用——它现在是关的；在 AI 层 70 个 `src/zephyr/**` 新件里，"裸 getenv/硬编码密钥"正属宪法 §1 RULE-SECRETS 的三道 gate 之一，目前这一道**无牙**。→ 不翻回的最坏情形=真键以字面量形式入 HEAD（密钥泄露，不可逆，须轮换）。
- 顺序错的最坏情形：先 flip 后落 module → `GateAutoRegistrationError` 无差别冻结全仓提交（实测 fail-closed 语义），所有在飞车道与死信循环同时停摆，只能 `emergency_commit`（手写标记会被判 forged，宪法 §9.8）。
- 计数风险：以"12 项"为准去要批文 → 只能拿到 11 项，第 12 项永远批不出来，形成永久悬置项。
- 连坐风险：187 件单袋若再撞前任三死因之一，整袋再死，`dead=609` 继续膨胀（实测当前 dead 规模，见本轮 LEDGER）。

## ⑥ 解锁依赖

1. 5 个模块的 `# [ALGO_FLOW] external:` 标记 + 8 个 `docs/03_modules/_domain_ai_layer/algo_flow/*.yaml` **必须同袋**（0011 与 0012 是同一件事的两面，实测列名齐全，可直接照补）。
2. 词表硬编码件改走 `*_vocabulary.yaml` 动态加载（0010 死因，未列具体文件名→需让 ailayer 会话自查或跑 `check_vocab_hardcode.py`）。
3. `tests/ai_layer/redline/test_negative_list_gates.py` 三 gate 的自家测试随批（宪法 §2.4"gate+自家测试同批是合法的"）。
4. 第 12 项批文的实体：要么由总筹给出条目，要么改口径为"11 项"并更正三处真源（计数用字段不写死散文）。
5. ailayer 会话是否还活着（21:06 后无新袋，实测）；若已死，需接手班按上四项重捕。

## ⑦ 一句话推荐（推荐待总筹拍）

推荐 **B（拆两批，"module+测试+名册三条 false→true"锁死在同一 commit）**，并把 §⑤ 的真键暴露列为本项唯一 P0 理由；同时把"12 项"改判为 **11 项可枚举 + 1 项口径错误待更正**（不得为凑数造批文）。
