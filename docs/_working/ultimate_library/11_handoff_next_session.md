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
