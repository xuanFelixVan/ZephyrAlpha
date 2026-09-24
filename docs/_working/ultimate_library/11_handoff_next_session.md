---
title: "终极图书馆 · 下一班总攻交接书（新对话第一必读）"
ttl: task_bound
completes_when: 本书全部任务落地+验收通过+零遗留
date: "2026-09-21"
owner: "ZephyrAlpha-Owner"
session: "上一班=st-ulib-20260921；本班自起新 sid（建议 st-ulib2-20260921）"
status: "handoff_active"
---

# 下一班总攻交接书（新对话从这里开始）

> **本班唯一主任务**：把暂存区里已保全的 43 文件过门禁落进 HEAD，然后跑完闭环验收（对账两轮 0+冒烟 7 passed+lookup 实测+红蓝复测）。上一班已把系统全部建成并本地验证，只差最后落地一步。

## §0 项目背景 30 秒版

ZephyrAlpha = 100% AI 开发运维的 A 股量化交易项目（Owner=人类，睡梦中，多 AI 会话并行施工是常态）。本战役 = 建"**终极图书馆**"：全项目资产的单一入口分层目录（六馆+场外区）+ 防漂移防幻觉门禁 + AI 检索总口。Owner 已令通宵总攻、Plan B（降速并行）、堵塞可停、自裁授权、临时文件清零、GitCommitGateway 落地。

## §1 冷启动必读（按序，全路径）

1. `AGENTS.md` —— 宪法 L0（保护文件！改它=修宪，须 Owner 正式批准，AI 勿碰）
2. `docs/_working/ultimate_library/10_blockage_handoff.md` —— 上一班停机点+钩子墙明细
3. `docs/_working/ultimate_library/00_master_plan_v0_1.md` —— 总蓝图（四铁律/七馆/收编地图/分期）
4. `docs/_working/ultimate_library/11_handoff_next_session.md` —— 本书
5. `docs/_working/ultimate_library/08_field_dictionary_v0_1.md` —— schema 冻结 v1.0
6. `docs/_working/ultimate_library/04_night_ops_plan_v1_0.md` —— 派工单
7. `docs/_working/ultimate_library/02_skeleton_mining_ledger_v0_1.md` —— 骨架封顶台账
8. `docs/_working/ultimate_library/09_librarian_process_v1.md` —— 馆员六权六流程
9. 环境冷启动：`$env:PATH` 补 Python312（`/c/Users/fanzi/AppData/Local/Programs/Python/Python312`）+ `python scripts/lock_files.py cleanup` + reaper 存活检查（AGENTS.md §0）

## §2 系统现状（上一班已验证，可信）

- **PG 资产总线**：depgraph 库 `lib_assets`/`lib_events` 两表已建（超级用户建的，app 角色 depgraph_reader 已授 SELECT+DML）
- **总账 35,744 资产入账**：fs 33,903+pg 89+ch 249+schtasks 57+mcp 29；连续两轮 blind=0/ghost=0
- **总口可用**：`python -m zephyr.library.lookup <关键词>`（实测 kline_1min 有结果）
- **七馆页已生成**：`docs/library/` INDEX+code/data/doc/rule/gate/pipeline/backup
- **代码质量**：ruff 全清、ALGO_FLOW 锚+13 外置 yaml 齐、Final 齐、SQL 常量化、[STARTUP] manual、设计节点全部 production（14905529-32/34-43/14920531-32）
- **凭据**：capability 册含全部 ulib token（已入 HEAD）；翻译册含全部 13 条（已入 HEAD，5a13009bc1）

## §3 唯一主任务：43 文件落地（清单=git diff --cached）

暂存区已保全 43 文件（library 域 14 .py + gate + __init__ + 2 生成器 + tests + blueprint + 13 ALGO yaml + in_process/generator_registry/translation/gate_registry 四册 + 七馆页 8 + 09 流程）。**它们全在暂存区，零丢失，但 HEAD 没有**。

落地配方（照抄，已趟平全部坑）：

```
git add src/zephyr/library/ src/zephyr/gov_enforcement/commit_gates/__init__.py src/zephyr/gov_enforcement/commit_gates/library_coverage_gate.py scripts/governance/generators/generate_library_index.py scripts/governance/generators/check_library_coverage.py tests/library/ docs/03_modules/_domain_library/ docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/ docs/library/ docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml docs/01_policies_and_standards/_registry/catalogs/generator_registry.yaml
python scripts/git_commit.py --session st-ulib2-20260921 --files <上述清单逗号分隔> --message-file <msg文件> --enqueue --allow-non-worktree --allow-overlap --allow-multi-domain
```

前置检查（落地前必过）：`ruff check` + `ruff format --check` 对 src/zephyr/library/ 与两生成器+gate 文件全清；`python -m pytest tests/library/test_library_smoke.py -q` 7 passed；`python scripts/governance/d5_architecture/checkers/check_algo_flow.py <13个py>` exit 0。

**绝对不要带**：`capability_canonical_file_registry.yaml`（token 已全在 HEAD，带上会撞 RULING-REFERENCE/YAML 结构漂移）。

## §4 已知门禁墙闯关手册（上一班 8 次死信的全部教训）

| 死因 | 解法 |
|---|---|
| HOT-FILE capability 册基线过期 | 剔除该册不带（token 已在 HEAD）；或落地前重新 git add 刷新 |
| RULING-REFERENCE 悬空裁定号 | 查 `git show HEAD:...ruling_registry.yaml` 是否已登记该号；已登记=重发即过 |
| NEW-FILE-DEPGRAPH 新 .py 无节点 | `apply_depgraph.py --granularity file --add-design-node <path> <MOD> <D_*>` + 逐级转产 planned→generated→testing→stable→production |
| TRANSLATION-COVERAGE 缺 plain_zh | `add_module_translation.py --path <f> --domain D_GOVERNANCE --name-zh <中> --plain-zh <大白话≥8汉字>`；**翻译册必须与代码同批或先落地**（loader 有 mtime 缓存） |
| 同 plain_zh 两模块共用=generic | 文本改写到唯一；或删旧路径孤儿条目+`[allow-mass-deletion:…]` 留痕 |
| ORPHAN-MODULE 新 gate 无引用 | `commit_gates/__init__.py` 静态 import 区块加一行（本批已加，勿删） |
| NAMING N-16 重名 | `algo_flow/__init__.yaml` 撞名 → 改 `library_init.yaml` 并同步 src/zephyr/library/__init__.py 锚+token 路径 |
| DIRECTORY-CONTRACT | COVERAGE.md 已迁 docs/_working/（场外区）；docs/library/ 只放 8 个固定页 |
| MUTABLE-CONST 缺 Final | 模块级容器一律 `X: Final[...] =`；`__all__` 用 `# noqa: n114-final` 先例格式 |
| [STARTUP] 词表 | 合法值：auto_start/event_driven/imported/manual/scheduled_task（"cli"非法） |
| NO-BARE-SQL | SQL 全模块级常量（已做，勿回退） |
| NO-LONG-PARAM-LIST | act() 已改 fields 字典（已做，勿回退） |
| DEPGRAPH-WRITE-PATH | 代码禁 superuser=True（已做）；建表走一次性超 users 通道 |
| 死信读取 | `.runtime/commit_queue/dead/q-*.json` 的 dead_reason 字段=精确门禁+修法 |

## §5 落地后闭环验收（连续两轮零才算过）

1. `python scripts/governance/generators/generate_library_index.py`（重生成馆页）
2. `python scripts/governance/generators/check_library_coverage.py` ×2 → 两轮 blind=0/ghost=0
3. `python -m pytest tests/library/test_library_smoke.py -q` → 7 passed
4. `python -m zephyr.library.lookup kline_1min` → 有结果
5. 红蓝复测：红=fuzz/指纹抽查/规格自查（对照 asyncio gate 头 15 标签）；蓝=十资产跨馆抽查+生命周期演示（出生→盲册→死亡证明）
6. 连续两轮零缺陷 → 总攻过

## §6 遗留任务全量清单（按优先级）——【2026-09-22 st-ulib2-20260921 班更新：43 件套已全落 HEAD，验收+红蓝连续两轮零，P1 relations 已建成落地（1a71693a2e+本班增量 6e86bdda3a）；详见 12 交付报告】

**P1（落地后本班做）**：
- ~~**关系一键查询** `zephyr.library.relations <功能关键词>`~~ ✅ **本班已交付**：MOD-LIB-005，种子排序+BFS+四馆树，义务全套（design node 14920542/token/翻译册/测试 4 例），实测 kline_1min 出树
- AGENTS.md 修宪挂图书馆入口（PROTECTED-PATHS 拦过一次；须走正式修宪通道=Owner 批，勿直接改）——仍待 Owner

**P2（W+1，已立案勿忘）**：
- prompt 版本管理/轨迹数据集/DORA 四指标/数据质量度量（05 类目表 §K/§O）
- app 角色权限收口：depgraph_reader 收回直写，只留 librarian 函数（08 §3.3 权限收口）
- 12+6 条漂移现行修复长尾（已录盲册：ROOR 旧数/49vs75/depgraph 空壳/前端 53vs41/Nocturne 假活等）
- tools/vendor/acceptance/logs 编外补录（05 §I5）
- 临时区 TTL 自动清策略
- post-commit 指纹刷新钩子（现在靠手工 regen）
- library_lookup_server.py 挂 mcp.json（MCP 口转正）
- capability 册旧路径孤儿 token 2 条清理（registry.py/schema.py 旧路径）
- 【本班新增】预检层 CREATE-GUARD 路径形态假阳性修复（commit_preflight.py 绝对路径 vs create_guard.py:724 相对路径集合；落地权威链无此问题）
- 【本班新增】指纹口径统一：08 词典"LF 规范形" vs fs_collector 原始字节 sha256，CRLF 文件会漂移

**待 Owner 裁定（勿自裁）**：
- 修宪批准（图书馆入口入宪法细节检索序条目）
- 备份馆授权（F→G 镜像+恢复演练自动化）
- 盲册首 he-session 在途件（a5_delivery_report.md 等）催 respective 车道收编

## §7 环境与工具备忘

- Python 3.12：`/c/Users/fanzi/AppData/Local/Programs/Python/Python312`（PATH 前插）
- 队列状态：`python scripts/commit_queue.py status --session <sid>`；死信读 `.runtime/commit_queue/dead/q-*.json`
- claim：`python scripts/lock_files.py acquire <file> <sid>`（TTL 30min，落地前刷新）
- 直连会连坐 → 全部走 `--enqueue --allow-non-worktree --allow-overlap --allow-multi-domain`
- 队列拥挤时的原生通道：`from commit_queue import enqueue_item; enqueue_item(sid, msg, [(path, bytes)])`（跳 CLI 预检，落地门禁照跑）
- 多会话并行中：taskcards/workclean/tilib-b10/dloop-v2 等车道在飞——**勿碰他车道 staged 文件**，capability 册尽量不带（撞 HOT-FILE）

## §8 执行令

见对话指令（Owner 通宵总攻令全文）：连续两轮零缺陷+红蓝复测+GitCommitGateway 落地+临时文件清零+端到端交付，中途不问、自裁授权（架构师第一性原理+业界实践框架）、不可裁则登记跳过、堵塞可停。

## §9 终局交付报告（st-ulib2-20260921 班，2026-09-22）——总攻收官

**终态：43 件套全落 HEAD + 闭环验收连续两轮零 + 红蓝复测连续两轮零 + P1 relations 交付。零遗留阻断项。**

### 落地批记录

| qid | 内容 | 终态 |
|---|---|---|
| 0002 | 前置批①试发（serializer 快照竞态空转） | done（零实害） |
| 0003 | 前置批①：capability 册 token 路径 N-16 改名联动（1 行） | done=7bf6947563 |
| 0005 | 主批增量校准（librarian Protocol+checker；主内容经 gov-closeout 车道吸收先行落地 de2d8df066） | done=6e86bdda3a |
| 0006/0007 | 冗余前置批/relations 批（内容已在 HEAD；stale 快照被 REGISTRY-MASS-DELETION 门禁正确自拦） | dead（防覆盖自拦，零实害） |
| 0008 | 收官文档批（12 号新建件撞 CREATE-GUARD → 报告并入本 §9，文档集维持冻结 15 件） | dead→改道本节 |

- MOD-LIB-005 relations 五件（relations.py/relations.yaml/test_relations.py/blueprint 行/翻译册条目）与 HEAD 零差异实证。

### 闭环验收（两轮零）

馆页重生成（七馆 code 28299/data 339/doc 5376/rule 84/gate 295/pipeline 83/backup 0）→ coverage **blind=0/ghost=0 ×2**（盲 8 采集吸收；鬼 12 机械核验逐件确证盘删后注销=死亡证明制实战）→ pytest **11 passed** → lookup rc=0 → relations rc=0。第 2 轮重复全绿。

### 红蓝对抗（两轮零）

红 8 项：fuzz 六类恶意输入×lookup/relations、注入后 lib_assets/nodes 行数完好（42,979/12,163）、指纹抽查×3、15 字段规格自查（19 列全含）、无授权注销负例。蓝 2 项：十资产跨馆 lookup、生命周期演示（出生→借阅→无授权拒绝→死亡证明+事件链）。两轮 **8/8 零缺陷**。

### P1 交付：MOD-LIB-005 relations（Owner W+1 点名第一项）

`python -m zephyr.library.relations <功能关键词> [depth]`——种子定位（200 抓取+相关性排序，代码/表/注册表优先、failures 噪声沉底）→ depgraph nodes/edges 双向有界 BFS（depth≤5、visited≤400、种子≤8）→ 四馆归类树。义务全套：design node 14920542+token+翻译册+ALGO 锚+Protocol 零裸 Any+4 测试。

### 本班新增门禁配方 6 条（合并上 8 条=14 条）

①serializer 快照竞态：热文件编辑+入袋必须同链（他车道落地会回滚/吸收主区未提交编辑）→原生 enqueue_item 显式字节通道根治；②预检 CREATE-GUARD 路径形态假阳性（commit_preflight 绝对路径 vs create_guard.py:724 相对集合；落地权威链正常）；③NO-BARE-SQL 入队面预检=正则近似，落地 AST 权威放行；④gate-any-abuse 本地全仓 advisory 掩盖新文件增量债，落地 own-scope 硬拦→新代码零裸 Any；⑤CREATE-GUARD token 与新文件同批=死锁，registry 先行批解；⑥队列取单=qid 字典序+interactive 先落+machine 30min 防饿（'st-u' 恒排最后）；共享工作区他车道吸收未提交内容=内容零丢失但归属记他账。

### 上报偏差与待 Owner（不阻断）

- 语义偏差：08 词典"指纹=LF 规范形" vs fs_collector 实现=原始字节 sha256（CRLF 文件漂移），W+1 统一口径。
- 总账身份证实态：代码=MOD:src/斜杠路径、馆页=DOC: 前缀、blueprint 有 archived 旧行+active 新行双户籍、upsert 不覆盖存量 status/fingerprint。
- 修宪（图书馆入口入宪法细节检索序条目，节号以修宪为准）/备份馆授权（F→G 镜像）/he-session 在途件催收编。
- 临时文件已清零；claims 已释放；会话收尾注销。

---

# 终验班晨报六要素（st-ulib3c-20260923，2026-09-23 16:20→18:4x）

> 任务=0062 终极合并批核收 + T13 终验收 + 增枝执行/待令 + B 班放行信号核验。
> 复核命令全部附在①②③各行，自审不采信自述。

## ① 环节 × 状态 × commit / 袋

| 环节 | 状态 | 落点 | 复核命令 |
|---|---|---|---|
| 词库 turnover 双挂假红治修（含 182 词数） | ✅ 已落 | `a436eca546`（2 件：词库+红证测试） | `git show a436eca546 --stat`；`git grep -c turnover HEAD -- .../library_tag_vocabulary.yaml`（=1） |
| ulib3b 残件九件（藏书规程页/血肉SOP/logs_collector+外锚+3测试/yaml_utils helper/六采集器接线） | ⏳ 在队 | 袋 `q-20260923-st-ulib3c-20260923-0005` | `ls .runtime/commit_queue/pending/ \| grep ulib3c`；`git cat-file -e HEAD:docs/library/regulations.md` |
| 族级登记改造 + 抽屉按 log_id 出号（含测试） | ⏳ 在队 | 袋 -0007 | 同上；落地后 `git show HEAD:src/zephyr/library/collectors/fs_collector.py \| grep _FAMILY_DIRS` |
| coverage 账面收敛（1762 archived / 31+258 deceased / 123+14 入册 / 误签 59 纠正） | ✅ 已做（DB 非 git） | PG `lib_assets`+`lib_events` actor=st-ulib3c-20260923 | `psql`：`select action,count(*) from lib_events where actor='st-ulib3c-20260923' group by 1` |
| 增枝 potential_consumers | ⛔ 未批→登记待令 | 呈批件 §六（本班写入，随文档袋） | `tail -20 docs/_working/ultimate_library/ulib3b_potential_consumers_proposal.md` |

## ② 复跑轮次与测试证据

- coverage **两轮连零**：`blind=0 ghost=0` ×2（18:3x，`python scripts/governance/generators/check_library_coverage.py`）。
  收敛前实测=blind=7/ghost=259（上一班交 0/0 后由 10 路在途删改+轮转累积）。
- `pytest tests/library tests/gov_enforcement/test_tag_vocab_gate.py test_library_blood_flesh_gate.py` = **59 passed**
  （32+13+14；含本班 3 条新红证：真词库 strict 加载 / 族级目录不逐件入册 / 抽屉 98 唯一号）。
- 别名轴三词终态复测：融资融券→`TBL:ch:c1_market.margin_trading`、龙虎榜→dragon_tiger(+seat)、
  北向→northbound_hold_snapshot 全命中，`python -m zephyr.library.lookup <词> --kind table`。
- 日志抽屉：**98 登记 / 98 唯一 asset_id / 98 在账**（改造前 97/98）；32 条改 `registry_of_logs.yaml#LOG-*` 定位。
- 词库闸生产面复算：alert_threshold_registry 假红 38→0，真非枚举 60 distinct 浮出。

## ③ 端到端实测记录（含失败与重试，不粉饰）

1. 首三袋全死：-0001 死于 REGISTRY-MASS-DELETION（删 1 行也算净删，须 `[allow-mass-deletion:...]`）；
   -0002 死于 ORPHAN-MODULE（logs_collector 无静态 import 边）；-0003 死于 CAPABILITY-LOOKUP-REQUIRED
   （CLI `--find` 不落 session 审计，须 `CapabilityLookup().find(q, session_id=...)`）。三条均已对症重发。
2. **本班自伤一次并已纠正**：清零脚本用 `root+home` 朴素 exists 判"盘上缺失"，把 59 条占位/绝对/
   cwd 相对 home 的抽屉行误签 deceased（实测 blind 反涨 59）。已按"权威盘侧集合"口径逐件回写
   active（`Librarian.act('update')` 回读原字段，避免 tags/aux 被 upsert 抹平），复核=
   `select count(*) from lib_events where actor='st-ulib3c-20260923' and detail->>'restore'='true'`（59）。
3. 队列吞吐现实：39 件在排、单件 15-20 分钟，两袋至今未落；租约由活体 PID 35816 持有，
   按处方未抢（`status` 会刷一屏"不抢租约"，改用 `health`）。

## ④ 遗留问题清单（非零，逐条案由）

| # | 遗留 | 案由/证据 |
|---|---|---|
| L1 | HEAD 三处落地洞（悬空 helper / registry_family 名册指空 / 六采集器未接线） | 见①；registry_family=st-wm1-buildA 在飞件，按 §3.4 不代修 |
| L2 | 词数标量字段回写被吞 | 袋 -0004 的 vocab blob 实测含 `vocabulary: 182`，落地后 HEAD 仍是 181 而同批的条目行删改正常生效——**本班单件实测**：注册表三向合并对"非条目标量行"改动疑似不采（未跨件复现，立此存照待查） |
| L3 | 词表真缺口 1197 occurrences / 474 distinct | 集中在 candidate_module_registry(444)+rule_ai_perception_index(376)＝68%；内混两类：真概念缺词（超跌/多因子/波浪/江恩/市场级择时…）与 tags 字段滥用为状态倾倒（深圳/批2/待需求驱动/过度工程/rejected…，SOP §3 明禁） |
| L4 | 双语义务 3 词条 | 成交、大宗缺英文别名，每日基本面零别名（本班删 turnover 后 成交 由"有英文"退为"无英文"，属治修副产物，须馆员增补不可自造） |
| L5 | 两闸仍是 warn 观察期 | BLOOD-FLESH/TAG-VOCAB 出厂 warn，升硬需 Owner 门位（flag 翻转=high） |
| L6 | docs/_working 历史入账行 | `offsite_monthly_manual.md` 盘上在而扫描面永不复现，本班改 archived 退账（同类若再出现=按同方处置） |
| L7 | 退账类授权不可反查 | `lib_assets.disposition_authority` 只在 delete（死亡证明）路径写，archived/update 的授权文本仅落 `lib_events.detail`——户籍列查"谁准我退账"必空（ledger_schema 现状，建议 update 路径同写该列） |

## ⑤ 待裁定清单（每条附"这是什么/为何要您点头/不点会怎样"）

1. **tags 误用清道 vs 词表增补（L3）**：要删的是把 tags 当状态批注用的 4 册（444+376+120+111 次），
   要补的是 20 来个真概念词。不点→TAG-VOCAB 升硬无望、B 班填的卡仍会被噪音淹没。
   建议：先清误用（改册不改语义），词表增补走馆员名单次批。
2. **双语 3 词条（L4）**：建议 `成交→volume/amount`、`大宗→block_trade`、`每日基本面→daily_fundamental`
   （前两个有物理列名/既有 match_tokens 证据，第三个须您点头才算造词）。不点→双语义务留 3 个洞。
3. **registry_family 悬空装载（L1）**：要么催 wm1 车道A 落地，要么授权本战役代落其暂收件。
   不点→任何 clean worktree 会话（含新开的 B 班）依旧无法直连提交，只能走队列。
4. **词数标量被合并吞掉（L2）**：建议改由生成器机械回写（`counting_rule` 已有），别手改。不点→每次改词数都会静默丢。
5. **增枝 potential_consumers**：仍是"未批"，本班零施工（详见呈批件 §六）。

## ⑥ 临时文件清理确认

- 根目录零临时件；本班可复用工具留 `.runtime/tmp/`（7 天卫生窗内）：
  `ulib3c_coverage_cleanup.py`（盘点/干跑/签发三态）、`ulib3c_restore_missigned.py`（误签纠正）、
  `ulib3c_ledger_settle.py`（族级收敛），加三份 message 文件。
- claims：文档袋发出后全 release；会话 worktree 无未交回内容（改动已迁主区/入袋）。
- 复核：`python scripts/lock_files.py list | grep ulib3c`（应空）、`git worktree list | grep ulib3c`（注销后空）。

## B 班（千问苦力班）放行三条件核验

| 条件 | 判定 | 依据 |
|---|---|---|
| ① 两闸在 HEAD | **半**：文件与名册在 HEAD（9b0c31ab12），但 B 班在 clean worktree 开班时 gateway 自举仍炸（registry_family 悬空 + helper 悬空至 -0005 落地） | ①②③各表 |
| ② 词汇表定稿 | **达成（有尾巴）**：182 词 strict 加载 0 缺陷、双语义务缺 3 词条、真缺口 1197 次待清 | L3/L4 |
| ③ coverage 两轮零 | **达成** | ② |

**结论：暂不放行开班**。等 -0005/-0007 两袋落地（HEAD 有规程页+SOP+六采集器）且 L1 三条悬空面清零后，
①才成立；届时 B 班才拿得到"填卡前置件+能提交的环境"。若 Owner 决定先开班后补环境，需明授"代修 L1"。

---

# R4/R5 追记（同班 st-ulib3c-20260923，19:0x-19:2x）

## 裁定落地与执行数
- **R4 tags 清道已执行**：22 册+86 规则全仓外科逐行摘除 569 次（TRAE 172/候选态环节补登 49/
  acquisition导入 49/L1_foundation 44/深圳 37/rejected 25/批N/layer:X…），非枚举 1197→736。
  逐词理由与反证写在各袋 message + `.runtime/tmp/ulib3c_tag_sweep_yaml.py` 头注。
- **L2 复核后维持原案（本班一度误纠，此处为准）**：HEAD 现值 `vocabulary: 181 词` 而标准词实测 182
  ——a436eca546 落地时同批 blob 里的**条目行删改正常生效**（turnover 已不再双挂），
  但同行标量字段 `181→182` 的回写未进 HEAD＝注册表三向合并对"非条目标量行"改动疑似不采。
  复测安排：袋 -0010（含别名增补+该字段）落地后再核一次；两次同象即立案（禁按未复现推断定论）。
- **双语 3 词条（已批）落地**：成交+volume/amount、大宗+block_trade、每日基本面+stock_daily_basic
  （全取物理列名/表名，零造词）；复测 strict 加载 182 标准词/296 别名/0 缺陷，"缺英文别名"3→0、
  "零别名"1→0。
- **tier 轴未动并已立案**：残留 736 次里 61 次是 `L0/L1/L2`——#ARCH-024 指定"tier 真源=规则
  frontmatter tags 的 Lx"且 `generate_rule_catalog._extract_tier_from_tags` 实读该值；
  **回归自证 86/86 文件改前改后 tier 提取值一致**。二选一待裁（见 derive 册 §4.3）。
- **R5 两案确认结案**：族级登记（方案二）与抽屉按 log_id 出号即本班已实现路径，无追加动作。

## 新发现：退账被采集器静默复活（重要，跨战役）
`_SQL_UPSERT_ASSET` 的 ON CONFLICT 段 `status = EXCLUDED.status` 无条件覆盖，而采集器默认发
'active' → 只要文件还在盘上，任何 archived/deceased 处置都会被下一次全量入账（他会话 commit 触发
library_regen_reconciler）改回 active。实测：本班 18:3x 账面归零后，两轮转目录 214 行被复活
（其中 209 行 disposition_authority 仍在=注销证据留着而状态已 active），coverage 因此回到
blind/ghost 非零。**结论：账面收敛必须排在口径代码落地之后**——族级排除袋未进 HEAD 前反复签＝空转。
待 -0007（fs_collector 族级+跳判修 & logs_collector 出号）落地后重跑 `ulib3c_ledger_settle.py` 一次收敛即可。

## 在队未落（本班 8 袋，19:22 实况 FIFO 位序）
-0007(第1)/-0005(第3) ulib3b 残件与族级改造；-0008/-0010/-0011/-0012/-0013/-0014（清道四批+文档）。
队列共 45 件在排，串行落地；本班未抢租约（持有者 PID 35816 活体）。
主区误入 index 的 86+3 件已逐件 `restore --staged` 摘回（他人 313 件在飞面未受染）。

## 20:0x 总指挥五令对账（同班）

- **①tier 轴=保守保持（已裁，本班待裁第 4 条结案）**：规则 tags 的 `L0/L1/L2` 继续为 #ARCH-024
  真源，长期收敛走季度审计。本班 86/86 改前改后 tier 一致自证留档。
- **③0071 死信=核袋后判定不再 requeue（与令的前提有差，据实报）**：
  1. 该袋 37 件中仅 7 件不在 HEAD，而**这 7 件已全数在本班在飞袋 -0005 内**（-0005 另含
     0071 所缺的两件配套：`yaml_utils.load_vocabulary_alias_map` 本体 + `collectors/__init__`
     六采集器接线），requeue 净内容=0；
  2. `--from-bag` 取的是 13:10 快照，其词库 blob 实测仍是被治修前的坏态
     （`turnover 挂在 ['成交','换手']`，HEAD 现为 `['换手']`）→ requeue 会把 TAG-VOCAB
     假红风暴签回 HEAD；同袋还含 3 本热册的 13:10 陈旧版。
  解锁前提本班复核为真：HEAD 落地器复合身份键 `_merge_entry_identity` 在位；翻译册
  `algo_submodules` 968 条中"同 module_path 多条"194 族（新键下合法）、
  `battle_map_steps` 341 条同侧首标量键重复=0（66e6b31346 已清 BM-BUY-14/BM-SIM-08 两对真重复）
  ——0071 原死因确已消除，只是该袋本身已被 -0005 取代。0071 现身处
  `.runtime/commit_queue/dead_archive_ulib3_zombie_20260923/`（夜窗手术归档）。
- **④A 班增补 11-14 接手前置**：potential_consumers 增枝令既已批文覆盖，本班先索取
  **裁定登记号**（宪法 §5/§9.11：对话内口头不构成批文，须入 ruling_registry 才是机判门可查的
  授权链），登记后按呈批件 §四 五步执行；施工时序仍受"口径袋 -0007/-0010 落地→
  账面重收敛"约束（否则回填即写脏，理由见上"退账复活"机制）。
- **⑤热册蒸发=只报不修（已照令）**：本班 20:0x 实测 capability 册 HEAD=379 caps/10095 tokens、
  工作区=379/10127（+32 tokens 未落）、index 可析；本班作业期间未见自有件 token 消失，
  唯一"改动未落地"=词库 `vocabulary:` 标量行（L2 复测安排在 -0010 落地后）。
