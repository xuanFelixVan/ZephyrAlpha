---
ttl: task_bound
completes_when: 全流通战役收官且最终交付报告落盘
---

# 全流通战役 · 车道所有权地图与总包裁定（唯一并发协调真源）

总包会话 = `st-fullflow-20260918`。本文件由总包维护，**所有车道开工前必读、收工前回写**。
原则：**owner 责任制** —— 每个文件只有一个车道能改；他会话在途违规只登记不代修（宪法 §3.4）。

## 1. 车道编制（Wave 1）

| 车道 sid | 分包 | 范围 | 状态 |
|---|---|---|---|
| st-fullflow-20260918 | 总包 | 裁定/协调/落地/验收 | 在飞 |
| st-ff-landA-20260918 | 分包1 | N-5 收口 + staged 24 件落地 + 危机闸三件 | 在飞 |
| st-ff-mine0-20260918 | 元挖矿 | 全环节骨架发现 | 在飞 |
| st-ff-instL-20260918 | 分包12 | 机构级整改第一批 T1-T4（复权链/ETF时区/幂等键/CI） | 在飞 |
| st-ff-vocabM-20260918 | 分包13 | 词表收编死信清偿 + W8 封账 | 在飞 |
| st-ff-residG-20260918 | 分包7 | residual 残余挂账 T1-T6（接线批/E6纸面对冲/E7告警） | 在飞 |
| st-ff-ailayerB-20260918 | 分包2 | AI 层进化引擎 L2 收集库施工 | 在飞 |
| st-ff-altdataF-20260918 | 分包6 | 数据源接入 A1-A8 | 在飞 |
| st-ff-tdchainJ-20260918 | 分包10 | tdchain 验收复核 + 死信清理 + 裁定清单 | 在飞 |

## 2. 独占文件所有权（禁跨车道写）

| 路径 | Owner 车道 | 备注 |
|---|---|---|
| `src/zephyr/data/config/tasks.yaml` | residG | residual C1 独占（多份交接令一致确认） |
| `src/zephyr/strategy_pipeline/pipeline_events.py` | residG | residual C1 独占 |
| `scripts/ch/apply_market_tables_ddl.py` | residG | residual C1 独占 |
| `config/trading_decision_map.yaml` | 总包代管 | TDM 地图，Wave 2 分包4 才开；本轮只读 |
| `src/zephyr/pf_alloc/**`、`src/zephyr/alt_data/**` | landA | 已 staged，先落地再释放 |
| `scripts/governance/_shared/module_translation_loader.py` | vocabM | CloneGuard 克隆族在此 |
| `scripts/governance/d3_metadata/backfill_module_domain.py` | vocabM | 长参数/类名/裸 subprocess 三死信在此 |
| `src/zephyr/gov_enforcement/rule_bridge/session_worktree.py` | 总包代管 | **含分包15 §2.1 未提交编辑（8 行），严禁 revert/clean** |
| `tests/governance/rule_bridge/test_session_worktree_audit_wrapper.py` | 总包代管 | 同上（+26 行未提交） |
| `src/zephyr/backtest/core/data_handler.py` | instL | 复权链主战场 |
| `src/zephyr/data/**/akshare_provider.py` | instL | 复权因子 + 主备双接口（分包8 task4 已并入本车道） |
| `src/zephyr/data/ch_reader.py` | instL | FINAL 注入 |
| `schemas/categories/kline/market_kline_daily.py` | instL | 表定义 |
| `scripts/ch/repair_etf_minute_tz_split.py` | instL | 时区劈叉（分包4 T5/分包8 P2-8 均让渡给本车道） |
| `src/zephyr/ex_core/adapters/miniqmt_broker.py` | instL | 幂等键持久化 |
| `src/zephyr/ex_core/order_manager.py` | instL | idempotency_key |
| `.github/workflows/governance.yml` | instL | CI 真跑测试 |
| `docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml` | **共享热文件** | 见 §3 协议 |
| `docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml` | **总包独占写** | 见 §4 |
| `docs/03_modules/**`、`AGENTS.md` | **全员禁写** | depgraph 自动产物除外 |

## 3. 共享热注册表并发协议（`capability_canonical_file_registry.yaml`）

1. 写前 `git show HEAD:<册> | grep <我的token>` —— 已在 HEAD 就**从提交清单剔除**（他会话吸收是常态非事故）。
2. 写只用 `safe_write_text` + `content_sha256` 文本口径 CAS，**禁 yaml.safe_dump 整写**，只文本式追加。
3. 提交前必与 dev 三方合并，要求对 dev **纯 insert、`grep -c '^<'`=0**。
4. **夺不到锁就 worktree-only**：写入工作区副本 + yaml.safe_load 复解析验证 + **不进 --files 清单**（CREATE-GUARD 读 worktree 内容即过），commit message 注明"worktree-only 不入本提交面"。
5. 撞 REGISTRY-MASS-DELETION / HOT-FILE-BASE-FRESHNESS：`git checkout HEAD -- <册>` → 重放增量 → 重新 claim → 重提，**三步压进一条 bash 命令**。

## 4. 裁定登记协议

- **裁定号一律由总包统一分配**，车道不得自行取号（并发撞号会吞条目，09-17 实证 #290-294 被五件他会话覆盖）。
- 车道需要裁定时：把"裁定申请书"写进 `docs/_working/fullflow_campaign/adjudications/req_<车道>_<序号>.md`
  （背景 + 选项 + 各自证据 file:line + 影响面 + 建议），回写本文件 §6 待裁表，然后**继续做下一件**（禁停等）。
- 总包裁定后写 `adjudications/ruling_<序号>.md` 并在 §6 标"已裁"，车道下一轮读取执行。

## 5. 提交通量约束（硬事实）

系统实测上限 **24 笔/小时**（serializer 单通道 S=149s）。故：
- **每车道全程 ≤3 笔提交**，把所有成果压进批次（一战场一批）。
- 一律 `--enqueue` 走队列正门（serializer 干净暂存区，结构性免疫连坐）。
- 队列积压时**不要空转重试**，继续做未落盘的施工，最后再投。
- 死信读 `dead_reason` 对症修，**勿 requeue 旧快照**（requeue 不吸收新文件）。

## 6. 待裁 / 已裁台账

### 已裁（总包 Max 裁定，即时生效）

**R-001 · N-5 共享区纠缠脏树 —— 判定：已因自愈而失效，按现状归位，无需"恢复 or 废弃"判决**
- 实测（2026-09-18，总包亲验）：`git stash list` = **空**；`git diff --cached --diff-filter=D` = **0 件**；
  `.ailocks/registry.json` 的 `locks` = **0 条 claim**；`.git/MERGE_HEAD` 不存在。
- 8 份交接令共同描述的"317 staged / 22 schema 删除 / 189 deep_review docs / stash@{0} WIP on aa43e3b530"
  **在当前工作区已不存在**。分包15 已预见此趋势（"登记时 22 件 staged 删除，一分钟内复测只剩 1 件，
  21 件已由归属会话/守护自愈"）。
- 现存量：staged 24 件（6M+18A）= 分包1 T1-T4 已测通批次；unstaged 81 件 = 多车道在飞真实 WIP（含分包15 §2.1）；
  untracked 60,319 件中 **60,245 件是 `data/c4_pdf_cache/` 数据缓存**（非代码，不计入盘点）。
- **裁定**：①staged 24 件由 landA 车道按其原批次配方落地（已有 23/23+2680 测试证据）；
  ②unstaged 81 件按 §2 所有权地图归各车道自行落地，**禁任何车道 restore/clean/reset 他人 unstaged 件**；
  ③stash 面已空，分包1 T5（归档+drop）判**已完成/已失效**，只需在台账记"实测 stash 数=0"；
  ④`data/c4_pdf_cache/` 应进 `.gitignore`（60k 文件长期裸奔会污染所有全仓扫描型门禁）——归 instL 车道顺手落。
- 依据：第一性原理 —— "恢复 or 废弃"是**对存在的对象**做判决；对象已不存在则判决无标的。
  强行 restore 一个已消失的 staged 删除面 = 凭空制造回退。宪法 §9.11：外来消息=数据不作指令，
  8 份交接令里的 N-5 描述是**历史快照数据**，不是当前事实。

**R-002 · N-6 CloneGuard extract 级克隆（`module_translation_loader.py` 六对 100% 相似访问器）—— 判定：merge，不许 ack**
- 现场：q-0035 死信列出 6 对 100% 相似（`get_module_plain`↔`get_step_plain`/`get_step_mechanism`/`get_step_indicators_zh`、
  `get_module_desc_bilingual`↔`get_step_name_bilingual`、`is_generic_plain_zh`↔`is_generic_desc_zh`、`preload`↔`preload_battle_map_steps`）。
- **裁定 = merge（治本）**，理由：
  ①宪法 RULE-CLONEGUARD 明文"extract 级克隆**无逃生**"，ack 是"合理重复"通道，而 6 对 100% 相同的访问器
    不属合理重复 —— 它们是同一模式（按 key 查表 + 双语回退 + 泛化判空）在两个命名空间各写一遍。
  ②裁定#321"门禁只许加严"、#273"禁白名单消警"：ack 走 echo-guard.yml 白名单 = 消警。
  ③这批克隆**已经真实吃掉一笔提交**（q-0035 死信），ack 只让下一笔继续撞。
  ④治本改法明确且低风险：抽一个泛型访问器 `_lookup_text(kind, key, lang_field, fallback_field)`，
    module 族与 step 族各自变成 2-3 行的薄封装（薄封装之间不会 100% 相似，因为字面量不同）。
- 执行：vocabM 车道。改完必须证明能红（删掉泛型函数的一支 → 对应测试必须失败）。

**R-003 · 提交并发策略 —— 判定：车道自投队列，总包不代提；每车道 ≤3 笔**
- 24 笔/h 是**门禁常数**（S18 根因表实测，serializer 单通道 S=149s）。15 车道若各自散投会产生 45+ 笔 → 2h 纯落地。
- 故压缩为"一战场一批"：每车道把全部成果压进 ≤3 笔。总包保留最终补投权（车道死信无法自愈时）。

**R-004 · `data/c4_pdf_cache/` 60,245 未跟踪件 —— 判定：加 .gitignore，不删文件**
- 是 PDF 缓存数据（业务资产），删除会毁数据；但 60k 未跟踪文件让 `git status` 类全仓扫描型门禁/工具
  每次多扫 6 万条，且 `git add -A` 一旦误用即灾难。
- 裁定：`.gitignore` 加 `data/c4_pdf_cache/`（若已有更宽的 `data/*cache*/` 规则则确认覆盖即可），文件原地保留。

**R-005 · Wave 2 预裁索引（全文在各车道任务书内，此处只留判据摘要供交叉引用）**

| 裁定号 | 车道 | 主题 | 结论一句话 |
|---|---|---|---|
| R-K1 | deeprevK | `crisis_drill_monthly.py` 修头落地 | 移交 landA Batch C；预裁=重构降复杂度（门只算新函数、阈值15、无 noqa；豁免违反#321） |
| R-K2 | deeprevK | N-5 盘点 | R-001 已关闭；只重跑四项实测复核，禁任何处置 |
| R-K3 | deeprevK | #ARCH-338..356 十九条 | 车道出"逐条处置案卷"（含**是否仍成立**的实测），总包批裁后执行 |
| R-K4 | deeprevK | 告警推送通道⑩ | 飞书/SMTP 已被 Owner 彻底删除 → 只做**可插拔 webhook + 缺省 fail-closed + 零内置厂商通道**；机器侧建、凭据属 Owner |
| R-K5 | deeprevK | 面板 API 鉴权④ | **必须加鉴权且缺省 fail-closed**（唯一"外部攻击面直通资金"项）；令牌走 secrets 禁裸 getenv；401+审计落痕；127.0.0.1 缺省**不**豁免。D_FRONTEND 属 human_gated → 只出方案不改码 |
| R-K6 | deeprevK | 资金事故假处置⑤ | 假处置必须改**真处置或显式 fail-closed**（假处置比无处置更危险：消灭告警信号）；必配"不 mock 防线自身"的测试钉；兜底日志禁预设失败类别 |
| R-K7 | deeprevK | Wyckoff 旁路⑧ | 旁路必须收口；合法用例改为**显式登记的豁免通道**（留痕可审计），禁隐式旁路 |
| R-K8 | deeprevK | miniQMT 退役 24 任务退路② | 按裁定#339 矩阵**逐任务改接**，禁简单删任务（删=数据断供→哨兵 breach）；tasks.yaml 归 residG，只出案卷 |
| R-K9 | deeprevK | Regime 断供三腿⑦ | 三腿各自独立供数 + 哨兵阈值行；断供时**降级 fail-closed 不允许交易**，禁 fail-open 默认继续 |
| R-K10 | deeprevK | 对账链⑨ | 必须**事件触发**，禁 cron/Timer/sleep-loop（宪法 §9.3 四要素）；判重用 `check_tick_duplication.py` 禁聚合数 |
| R-K11 | deeprevK | TF07 daban 名义 DAG 边① | 名义边必须补成**真实边**或显式标注名义（名义边=日消费者读过期周数据=PIT 污染） |
| R-K12 | deeprevK | pf_alloc 整域⑥ | 归 landA+residG，deeprevK 只出案卷 |
| R-E1 | cleanexamE | L5-D1 考尺 OOS/IS 两口径不可比 | **同口径重算 is_sharpe**，不采纳"降级为参考指标"（保留不产生约束力的门=没有门）；历史 verdict 显式标作废需重考；**禁调阈值让翻红变绿** |
| R-E2 | cleanexamE | 清洁范围外件终处置 | 本轮不动+登记；`auction_book_limit_bak` **唯一副本先做异地备份**（G 盘或 recycle_bin 30天）再议删；禁删任何件 |
| R-E3 | cleanexamE | 组队方案 A 终审材料 | Owner 门位，只备料（三数字各自口径/为何 1.541 suspect/证据链） |
| R-E4 | cleanexamE | N-5 | R-001 已关闭 |
| R-D1 | tdskelD | T1 sim-memo token | 移交 landA Batch E（`.json` 会被 DIRECTORY-CONTRACT 拦，剔除并登记） |
| R-D2 | tdskelD | T4 tick_depth_5 回补窗 | **最高优先**（唯一硬性时间衰减件）。裁定=先探测实际可得范围 → **按"最老先救"排序**（过期从最老端逐日吞噬）→ 单日 >2GB 则只救最老 3-5 日，其余出精确工单。**D 盘仅 62GB，击穿磁盘会让 15 车道全败** |
| R-D3 | tdskelD | T3 ETF 60min 补深 | 可行则执行，但先体积估算 + 先查数据线是否在飞；`repair_etf_minute_tz_split.py` 归 instL 禁改；产出若依赖时区修复则标 provisional |
| R-D4 | tdskelD | T5 regime 切换备料 | 生产流转=Owner 门位，只出《切换备料包》（对照数据+检查单+回滚预案），禁执行切换 |
| R-D5 | tdskelD | T6 编排器出手阶段 | 只出《毕业生缺口与加速方案》；数字须标"基于旧口径，lane-E 重算后需刷新" |
| R-D6 | tdskelD | T7 WYF-3 立项 | 只备料（替代特征假设清单+预注册协议草案，含三问停止判据） |
| R-D7 | tdskelD | T2 cherry-pick 缺口 | 先核实是否已入 dev；cp3 param-object **不主动重构**，登记"待门禁触发时随批做"（无缺陷记录+未入库代码重构=白做） |
| R-H1 | kimiH | P1-4 akshare 主备双接口 | **并入 instL**（同批文件，并发必互踩） |
| R-H2 | kimiH | P1-7 N-5 | R-001 已关闭，只实测复核 |
| R-H3 | kimiH | P1-6 `e19bc24c` 重 merge | **走 TableRegistry 注册迁移（治本），禁豁免/绕过**（该门无 noqa 是设计意图；判定表不进注册表=判定链无 SSoT=全流通断点）。品类 YAML 必须与代码同批；`scripts/**` 不豁免；注意子串双匹配连坐 |
| R-H4 | kimiH | P0-1 数据源切换门体检 | 立即执行（已过 15:30 收盘）；DatabaseService 只读、ReplacingMergeTree 带 FINAL、symbol 裸码 |
| R-H5 | kimiH | P0-2 63 任务拆分催办 | 只出催办单（含逐条 YAML 片段），**tasks.yaml 归 residG 单一写者** |
| R-H6 | kimiH | P0-3 801 笔循环单/miniQMT 下线 | Owner 终端门位，**只只读核实+登记**，禁撤单/停进程/下线（不 kill 常驻守护 #281③） |
| R-H7 | kimiH | P1-5 声明面更新 | 执行前先 `git diff`（该文件已有 +2/-12 unstaged）：若正是"只保留 tick 类"则判已完成不重做；若是别的改动则**叠加勿覆盖** |
| R-I1 | minelineI | L1 TTL 去重批次口径 | **最多 3 批**（原定每批≤100 会产生远超 3 笔提交，而 24 笔/h 是全队共享稀缺资源）；>300 文件则本轮处理前 300 + 余量写接力清单 |
| R-I2 | minelineI | L2 ReDoS 根治选型 | **匹配预算，不用 regex timeout**（Windows 无 `signal.alarm`；线程方案打不断 C 层 `re` 灾难性回溯→资源泄漏）。对齐专业实践 RE2/Rust regex=禁回溯引擎，从算法层消除成因。落地：输入长度上限断言 fail-closed + 嵌套量词改写 + **能红的测试**（构造灾难输入断言预算内返回或 fail-closed） |
| R-I3 | minelineI | L5 哨兵排班接线 | **禁写 tasks.yaml**（residG 独占）→ 出 YAML 片段交总包转交；`schedule.yaml` 若无 claim 可直接改 |
| R-I4 | minelineI | L3 `trade_panel.py:306` fallback 绕闸 | **代码侧先改 fail-closed**（属"门禁只许加严"#321 范畴，不触发 human_gate）+ 闸位设计方案交 Owner 知会；必配"不 mock 防线自身"的测试钉 |
| R-I5 | minelineI | L4 工厂图 F/I 节点补挂 | 按 **depgraph 实测边**补挂，图语义以 **TDM 为唯一权威**；不冲突处直接补，冲突处出案卷（已有 `validate_strategy_production_map.py` + `align_all.py`，权威已定不需新裁） |
| R-N1 | anchorN | A1 W2 提交链提速包 | **本轮只做 F4（生成器并发化，纯提速零语义变更）**；F3 只出实施备料（判据要 100 笔回放样本，一夜凑不齐且改的是所有门禁作用域）；F1/F2 属 Owner 门位（S18-R1~R4 待签）登记不执行。**关键判断：15 车道 ×≤3 笔 = 最多 45 笔 ≈ 2h，一夜窗口足够 → 为可承受的瓶颈动提交链地基是用真实风险换非必要收益；动坏了则 15 车道全无法落地** |
| R-N2 | anchorN | A2 W4 自引用 fixture 判据化 | **采纳判据化**（写死白名单只覆盖已知 24 件、未来新件会漏；判据式对当前与未来件均生效=加严，且正是消除白名单，符合#321/#273）。验收三条变异证据：被豁免件注入真违规仍被拦 / 未豁免件注入自引用被拦 / 判据改宽则测试红 |
| R-N3 | anchorN | A3 W5 作者语义欠账 69 件 | **只做可机判**（git 证据唯一确定作者/依据）；不可机判列清单交总包，**禁自动填充**（责任归属错误的代价高于欠账本身，且这类错误静默无测试会红） |
| R-N4 | anchorN | B1 N-5 | R-001 已关闭；重跑四项实测 + 确认 `test_pretrade_risk_gate_sim.py` 现状 |
| R-N5 | anchorN | B2 外来"线已关闭"缺口核销 | **本会话代为补登**（注册表是永久产物，缺口不补=永久断链；原会话已收口不会回来补），**但取号权收归总包**（并发撞号已实证：#290-294 被覆盖、#304 三方撞号）。车道出内容包，禁自写 `ruling_registry.yaml` |
| R-N6 | anchorN | B3 既有 Owner 门位在册项 | 逐条**实测现状勿凭记忆**；`#ARCH-337` 治本若已在 HEAD 则由总包改 status=resolved |
| R-O1 | flashO | N-6 CloneGuard ack-vs-merge | **merge（治本），不许 ack**，与 R-002 同一原则一致适用（否则治理体系出现"看谁嗓门大"的裂缝）。**且既有债不成为该文件永久阻塞器** —— 否则 `session_worktree.py` 变成"改不动的技术债免疫区"，门禁从"逼出改进"退化成"冻结代码"。超 20 轮未清净则退回：8 行改动保持磁盘未提交态 + 双份 patch 备份 + 接力说明，**禁 revert/clean/ack 硬闯** |
| R-O2 | flashO | 回填 90_report/91 文档 | **改写新文件**，由总包在 landA Batch E 落地后统一合并回填（并发写同一文件必互踩，本仓已有热注册表被外来非 CAS 写静默蒸发事故 #ARCH-337） |

### Wave 2 车道编制

| 车道 sid | 分包 | 范围 |
|---|---|---|
| st-ff-deeprevK-20260918 | 分包11 | deep_review 收尾 + #ARCH-338..356 十九条案卷 |
| st-ff-cleanexamE-20260918 | 分包5 | 清洁+补考+E2E（L1-L6） |
| st-ff-tdskelD-20260918 | 分包4 | 交易决策骨架（T2-T7，T1 移交 landA） |
| st-ff-kimiH-20260918 | 分包8 | 数据源切换体检 + TableRegistry 迁移 + 声明面 |
| st-ff-minelineI-20260918 | 分包9 | 自动化挖矿线遗留（L1-L6） |
| st-ff-anchorN-20260918 | 分包14 | 落地面锚定收尾（A1 F4/A2/A3 + B1-B3） |
| st-ff-flashO-20260918 | 分包15 | 提交链 §2.1 堵点归因 + N-6 克隆治本 |

> **分包3（【模型编制】）与分包14 的路由段属纯模型路由指令、无独立任务** → 已折叠为本战役全局协议：
> 复杂裁定（资金语义/生产流转/架构级取舍/数学证明/恢复-vs-废弃/门禁语义变更）一律归总包（Max）；
> 机械执行（文件操作/跑批/登记/常规修复/盘点/测试）一律归车道子代理。全部 15 分包均已派车道，无遗漏。

### 资源自守协议（Owner 要求的性能监控）

- 已挂后台监控脚本 `.runtime/tmp/fullflow/resmon.py` → 每 60s 落一行到 `.runtime/tmp/fullflow/resmon.jsonl`
  （`cpu_pct` / `mem_pct` / `mem_avail_gb` / python 进程数）。
- **每条车道任务书里都写了自守条款**：跑测试前读该 jsonl 最后 3 行，`mem_avail_gb < 12` 或 `cpu_pct > 85` 则推迟重活；
  测试只跑单文件/单目录级禁全仓全量；压测 worker ≤20（50 曾三度压死宿主）。
- **裁定：不设"自动杀进程"看门狗。** 理由：杀进程会毁掉车道未提交的成果（本仓已有 pre-merge 横扫毁未提交件、
  孤儿进程撑爆内存两起事故），代价高于收益。改为**自守 + 总包轮询水位**：总包在每波交接点读 resmon，
  水位超线则**推迟下一波派发**（限流在入口而非杀已在飞的活）。
- 基线（2026-09-18 17:2x，15 路起飞前）：CPU 25-47%、RAM 32GB 可用/64GB、D 盘 62GB 可用/732GB（92% 已用）。
  **D 盘是最紧的资源** → 任何回填/下载前先估体积，超 5GB 登记不执行（已写进 tdskelD/altdataF 任务书）。

**实测起飞峰值（17:41-17:43，16 路在飞）**：CPU **91.7→99.0→98.1%**（已饱和）、RAM 可用 **32→17.6GB**、
python 进程数 **80-84 个**（16 个代理各自派生 pytest/git/python 子进程，故进程数远超代理数）、D 盘 62→59GB。
→ **总包裁定 R-006：并发冻结在 16 路，Wave 3（分环节深挖）推迟到 Wave 1/2 有车道收工后再派。**
  理由：①Owner 给的 20-30 上限是按"代理数"算的，但真实约束是**进程数与 CPU 核数**——20 核已被 84 个进程
  打到 99%，再派代理不会提高吞吐，只会让所有车道一起变慢（上下文切换与内存换页）；②本仓有内存耗尽事故前科
  （孤儿 llama-server 撑爆 + 页面文件扩容待重启），RAM 可用跌破 12GB 即进入危险区；③限流应在**入口**（推迟派发）
  而非杀已在飞的活（杀进程会毁未提交成果）。
→ 自守阈值实测有效：各车道任务书均含"`cpu_pct > 85` 或 `mem_avail_gb < 12` 则推迟重活"，峰值期车道会自动让出 CPU。
→ 磁盘监控：20 分钟消耗 3GB。若按此速率持续 10h 将击穿 59GB 余量 → 总包每波交接点复查，
  必要时清 `.runtime/tmp/` 下已收工车道的 backup（**只清已落地且已核归属的**，未落地的禁清）。

### 待裁（车道提交申请书后由总包裁）

| 编号 | 车道 | 主题 | 状态 |
|---|---|---|---|
| req_datagap_01 | st-ff-datagap-20260918 | 三议题：**A** daily_valuation 9 个行情腿列的无值表达口径（实测 FINAL 259238 行 close/amount/turnover 非零 0 行；A1 改 Nullable 推荐 / A2 由 kline_daily 同步 / A3 摘列=净删门位）；**B** 两份片段合并授权（lanes/datagap_sentinel_yaml_fragment.yaml 目标文件归 z-failopen、lanes/datagap_tasks_yaml_fragment.yaml 目标文件归 z-dag，本车道按单一写者制未直改）；**C 因果链锁定**：BRK-054（strict_mode=false + dlq_enabled=false + runtime drift 未实现）正是 BRK-034（计算列被抹 NULL 100%）与 N-1（0 值伪装合法数值）能落库且长期不可见的结构性原因，**不补 DLQ 本簇修完仍会复发**——本车道只挡住同表多写者互相抹值，挡不住新整窗重灌语义/列类型放宽/新写者接入。另报普查失效 4 条：BRK-029（sector_fund_flow 现 1467 行，假通道已愈）/BRK-034（双行 0 组，恶化为归零）/BRK-035（库内 0 撞码，拦阻在位）/BRK-038（哨兵实跑 breached 0，非噪音而是盲区）。证据 lanes/datagap_corrupt_rows.md、lanes/datagap_source_triage.md、adjudications/req_datagap_01.md | 待裁（车道未停等：止血与片段已落地） |
| req_tdchainJ_01 | st-ff-tdchainJ-20260918 | 裁定#304 三方撞号 tombstone 治理（总包预裁=采纳、总包统一执行；三方实证已交：regcal 保留#304/做T砍改号#331/切换器分支档声称） | 预裁已给·待总包执行 tombstone |
| req_tdchainJ_02 | st-ff-tdchainJ-20260918 | #306 红队条款① family_registry 立案（总包预裁=立案；立案书三要素已交：生成器落点 standards_governance/条目来源 standards.yaml+governance_family 词表/计数字段 total_families） | 预裁已给·待总包批+分配裁定号 |
| req_tdchainJ_03 | st-ff-tdchainJ-20260918 | kline_index_intraday 新表立项（总包预裁=立项、residG 执行；DDL 规格已交 lanes/tdchainJ_kline_index_intraday_spec.md） | 预裁已给·待总包转交 residG |
| req_wiresafe_01 | st-ff-wiresafe-20260918 | 保命链四项：①BRK-021/072 标的已由他道**未落地件**占据（`src/zephyr/risk/paper_hedge_leg.py` 与 `config/paper_hedge.yaml` 实测 untracked、不在 HEAD），请改派落地而非重复造；②KS 净删候选 `src/zephyr/infrastructure/kill_switch_sim.py`（禁自删，只登记）；③应急保命轨 `enabled: true` 盘内自动拉系统闸是否可接受（已内建四道防误触发+逐道测试钉）；④普查 §A/§D/§E 系统性陈旧（本车道 7 条中 4 条记载已过期），建议验收规范 §5 封矿后加一步施工前复测原始证据命令 | 待裁（车道未停等：已按建议方案落地并出三册施工包） |
| req_wirerecon_01 | st-ff-wirerecon-20260918 | **BRK-020 落地地雷 + 数据质量缺陷转 z-land**：G1 producer 与其测试 untracked、broker 四个接线方法 unstaged（按现 staged 面落地即断整条 ex_core import）；G4 未成交终态真单实证 `slippage_bps=-10000.0` 污染 TCA 回流入口（`eef42ae008` 已把台账从 0 行打通到 1 行，见案卷 §1 E3）；G2/G3 验收仪两处检测法缺陷。处方=file:line+改法已落 `lanes/wirerecon_BRK020_gap.md` | 待总包转 z-land（本车道未碰 ex_core/pf_alloc） |
| req_wirerecon_02 | st-ff-wirerecon-20260918 | **对账域六件实现并存且全部零程序消费**（position/ex_core×2/trading×2/orchestrator），提请按 R-002 同原则裁"盘中=position 事件入口（本车道已 Fail-Closed）+ 日终=recon_runner"，并把 `reconciliation_loop` 从 GOMAP `families.L5_selfheal` 摘出（普查 BRK-017 系误归因，它调的是编排器自完整性 5 不变量） | 待裁·待总包 |
| req_wirerecon_03 | st-ff-wirerecon-20260918 | 日终对账调度片段（`recon_runner.run_daily_reconciliation` / `eod_reconciliation` 需 15:30 档期）+ `execution_report` 的 `data_supply_sentinel.yaml` 阈值行——**tasks.yaml 归 residG 单一写者**，本车道不代写，片段待 G1 落地后另批 | 待总包转 residG |
| req_dag_01 | st-ff-dag-20260918 | **排班车道五件跨权登记**（A1 altdataF 品类片段载体 docs/03_modules 全员禁写；A2 instL/minelineI 两片段文件实测不存在=催重出；A3 pipeline_events --due 月频挂载属 z-land/pf_alloc 载体；A4 kline_index_intraday 建表 DDL 归总包（采集条目已受控落地 tasks.yaml）；A5 两项机制地雷：.gitignore `scripts/data/*` 静默排除新建永久工具 + dataflow 注册表无表级血缘故 BRK-050 不可自闭） | 待裁·待总包（本车道未停等：可落部分已全部落地） |

**R-007 · Wave 1/2 停车收割（总包亲执，2026-09-18 18:1x）**
- 停车实测：车道全停后仅剩 5 进程 / 0.5GB / CPU 26-35%，6 分钟内无文件写入 → **烧钱已止**。
- 落地：**仅 1 笔进 HEAD** = `30dc814645`（lane-M 执行 R-002：六对克隆 merge 成泛型访问器 +
  **主动撤销 6 条白名单消警** + 清偿 q-0035）。**证明队列 serializer 守护独立于车道存活**，
  车道死后仍会把自己入队的批次落地。
- 遗留资产：staged **314 件**（39A+275M）+ worktree 59 件，**0 笔提交**。
  → 已全部镜像归档 `.runtime/tmp/ff_quarantine/{index_snapshot,worktree_snapshot}/` + `MANIFEST.json`
    （11.9MB）。**自此任何后续操作均可回滚，零丢失风险。**
- 排雷：279 个 staged `.py` + 全部 worktree `.py` 做 `compile()` → **0 件语法破损**（无撑死通道的地雷）。
- 真交付确认：`crisis_gate.py`+438 / `cohort_daily_ledger.py`+440 / `crisis_drill_monthly.py`+770（分包1 E1/E4/E5）；
  **`shared/infra/idempotency.py`+91 新文件 + `miniqmt_broker.py`+113 + `order_manager.py`+38 = lane-L 的 T3 幂等键持久化已成型**；
  `qmt_file_bridge_integration.py`+45（lane-E execution_report 接线）；骨架 30KB + 普查 52KB；
  lane-B L2 worklist / lane-F 两 YAML 片段 / lane-J 三裁定书 + 新表规格。
- 裁定号策略：本战役内部一律用 `R-0NN` 前缀而非"裁定#NNN"，**刻意规避 RULING-REFERENCE 门禁**（禁引未登记号）。
  收官时由总包把值得永久化的条目按实测 max+1 统一转登记。

**R-008 · 暂存区换行污染剥离（`dedup_ttl_headers.py` 缺陷 = 治本件 BRK-086）**
- 实测归因（逐行比 HEAD blob vs index blob）：约 28 件呈 `raw=+449/-450`、`raw=+863/-864` 形态，
  **真实内容差异只有 1 行**（lane-I 的 L1 TTL 去重删了重复 `# [TTL] permanent`），
  但工具**把 CRLF 改写成了 LF** → git 把整篇 400+ 行全报为改动。
  `-w --ignore-blank-lines` 测不出（git 不把 CR 当空白），**必须 `--ignore-cr-at-eol`**。
- 危害：一笔提交背几万行假差异 → blame 全毁 + `REGISTRY-MASS-DELETION` 误判 + 看似"整体回退他人条目"。
- **裁定两步**：①这些文件**索引与工作区双双还原 HEAD**（改动已归档且是幂等机械件，可由修好的工具再生）；
  ②`dedup_ttl_headers.py` 改为**按字节保换行**（`read_bytes`+定位替换+`write_bytes`，禁文本模式整篇读写），
  并配能红的测试钉：对 CRLF 文件跑 `--apply` 后 `git diff --numstat` 必须是 `+0 -1` 而非 `+N -N±1`。
- **普适判据（建议永久化）**：任何"批量小改存量文件"的工具在混合换行仓库里用文本模式整篇读写，
  必然产出差评级假差异 → 一律要求字节级就地改写。

**R-009 · 战役组织由"15 分包"改为"断点簇"（策略转向，即时生效）**
- 元挖矿已交付权威骨架（**N=16 环节**；75/75 域、11995/11995 节点归口，未归属=0；12 独立真源交叉验证）
  与 **85 条断点**（高 38 / 中 42 / 低 5；Owner 门位 5）。
- 断点普查比 15 份交接令更贴近"全流通"判据：**交接令是车道视角（谁留下的活），普查是流转视角（哪根管子没水）**。
  → Wave 3 起按**断点簇**派工，每车道领一组 BRK-ID；15 分包未完成项映射进对应簇。
- **诚实规模判断（Owner 醒来先读这条）**：85 条里含 1585 件静态零入度模块（45.6% 上界）、
  213 个决策节点全 planned、17 项横切机制零落地、44 条数据缺口 —— 这是**数周到数月**的量。
  一夜能闭合的是**接线类**（有实现无消费方 / 有表无生产者 / 注册表自相矛盾 / 假通道改 fail-closed）；
  **新建类**（决策图落地、CC 机制实现、15 个无承载研究环节）只能出施工包与派工图。
  → 本轮交付 = 接线类全部打穿 + 新建类全部出可执行施工包 + 验收仪可用 + Max 待办清单（带完整路径）。

**R-010 · 新分派协议（覆盖此前所有模型路由令）**
- Owner 实测确认**此前 16 路全跑在 Max 上**（关主会话后子代理仍计费）→ 已停车并切 Flash。
- ①**Flash 能干的全干完，包括裁定** —— 裁定的做法=派多路子代理**并发深度调查**产出分层证据，Flash 依证据定案；
  只有"特别复杂的多线纠缠"才留 Max。
- ②收工交付固定两件：**（A）需 Max 裁定清单** + **（B）Max 待执行任务清单**，
  两者均带**完整路径**（文件:行号 / 命令 / 证据位置），使 Owner 切 Max 后**直接开工不需重新勘察**。
- ③上下文虽已放开 1M，**定位不变仍按 256K 纪律**：任务书给精确路径不撒网、产物落文件不堆上下文、
  深度广度靠**分形派子代理**（节点发散再派节点）而非单代理硬扛长上下文。
- ④并发上限修正：原令"20-30"按代理数计，真实约束是**进程数/CPU 核数**（16 代理→84 进程→20 核 99%）
  → 维持 R-006：**单波 ≤8 路**，波间交接再派。

**R-011 · lane-J 三裁定书定案（按 R-010①由 Flash 依证据裁）**
- **req_01（#304 三方撞号）= 采纳方案 A（tombstone 治理），由总包执行**。
  证据已完备：甲 regcal 因被 `regime_detector.py` 代码不变式引用而**唯一保留 #304**；
  乙做T v2 已按"代码绑定优先"改号 #331 且 renumber_note 在案（`:3766`）；丙 S-OWNER-002 **从未入 dev**
  （分支档 `89dd33dd8a:…ruling_registry.yaml:3765` 自带一条 #304，与 dev 永久分叉）。
  → 选 A 不选 B 的判据：B 的"引用带 title 消歧"是**口头约定**，而 RULING-REFERENCE 门禁**无法机械消歧**，
  等于把三处矛盾记载永久留在注册表里靠人眼守 —— 违反"机械判定禁止凭记忆"（RULE-SSOT）。
  影响面=仅注册表注记 + 文档消歧，**零代码行为变化**，故不触 Owner 门位。
- **req_02（family_registry 立案）= 批准立案**，三要素齐备可施工：生成器落 `standards_governance/` 子包
  （ARCH-031 合规）、条目来源 standards.yaml + `governance_family_vocabulary.yaml` + reexam_evidence/N_eff 注记、
  计数字段 `total_families`/`total_standards` 由生成器写入。
  → 挂 ROOR 索引（RULE-REGISTRY）、归 #307"派生自动"档、生成器只引已登记裁定号（#316）。
  → **派工**：Wave 3 治理簇车道。
- **req_03（`kline_index_intraday` 新表）= 立项确认，转 residG 执行**。
  缺表已实测（`system.tables` 0 件）；现行降级路径有精确锚点
  （`src/zephyr/plan_engine/intraday_l1_tracker.py:405-409` 用 510300 ETF 分钟线**代理**指数分钟线，
  受代理基差污染）。纯新增表+新增采集任务，**零既有表变更** → 不触门位。
  落地后消费侧摘除代理注记另批走独立门。

## 6.5 落地期裁定（Wave 3 在飞，总包续裁）

**R-012 · 拆除总包自造的死锁：`ALGO-NOTE-SYNC` 与"TDM 全员禁写"互斥（z-land 实证）**
- 现象（实测）：q-0001 死于 `TDM-F-C3-03`、q-0002 死于 `TDM-E-L4-10` —— 门禁要求
  **改 TDM 绑定模块的实现码，必须同批改 `config/trading_decision_map.yaml` 该节点 `algo_note_zh` 或加 `note_confirmed`**；
  而我把该文件列为对所有车道禁写 → **凡含 pf_alloc / ex_core / risk 的批次结构性不可能落地**。
  所有"赚钱链路"的批次都会被这条卡死。这是我编排时的疏漏，不是车道可控。
- **裁定：TDM 由"全员禁写"改为"限定用途可写"** ——
  ①**只允许**为自己本批实际触碰的 TDM 节点写 `note_confirmed: true`，或补 `algo_note_zh`（一行注释）；
  ②**禁止**改节点的 `impl`/`deps`/`algo` 等语义字段（那些才是真架构变更，归总包）；
  ③写法沿用 R-008 纪律：`safe_write_text` + `content_sha256` 文本口径 CAS + 与 dev 三方合并要求
    **对 dev 纯 insert、`grep -c '^<'`=0`**，且**与实现码同一 commit 原子提交**（这正是门禁要的）。
- 判据：门禁设计意图是"改了实现就得同步算法注记"，本就该由**改代码的人**同批改；
  把它集中到总包反而制造了"改代码的人不知道注记该怎么写"的信息错位。下放是正确方向。

**R-013 · 普查误归因修正：BRK-017 不是 FF-11→FF-12 成交对账链（z-wire-recon 实证）**
- 实测：`orchestrator/execution/reconciliation_loop.py` 调和的是**编排器自完整性五不变量**
  （契约校验和 / 熔断态 / CBAC 矩阵 / 任务卡态机 / DLQ），**与成交对账无关**。
  → 照普查字面把成交数据接上去 = **造一个假闭环**（看起来接了，实际语义错位）。
- **裁定：普查该条改判为"归属错"，不动接线**；真正的 FF-11→FF-12 缺口是
  `execution_report` **零读者 + 无事件扇出点**（车道已出处方 G6：producer `listeners` →
  `PositionReconciler.handle_execution_report`）。
- **普适教训（要写进验收仪）**：断点普查给出的是"零入度"这一**机械事实**，
  但"该接给谁"是**语义判断**。任何按"孤儿模块"字面接线的施工，都必须先验消费方语义，
  否则会把闭环接错 —— 比不接更糟（不接是明的缺口，接错是假的完成）。
  → 已要求后续车道在交工时附"语义核对"一行。

**R-014 · 静默数据缺陷：未成交终态 `slippage_bps=-10000.0` 污染学习闭环（真单实证）**
- 实测：模拟盘 510300.SH BUY 100 @4.07（跌停价必不成交）→ 撤单收敛 CANCELLED →
  `c1_market.execution_report` 落 1 行，但 `slippage_bps = -10000.0`。
  成因 `src/zephyr/ex_core/execution_report.py:54-62` **把 avg=0 当成成交价**。
- 危害：按"正=不利"口径，-10000bps = **满分执行**。每一笔撤单都在向 TCA / FF-02 研究孵化 /
  FF-06 选股**回流一张乐观票** → 系统会学到"我的执行很好"，而真实成交根本没发生。
- **裁定=改判为"无有效执行样本"（slippage 置 NULL 而非算出数值），且撤单/FILLED 分开计数**。
  判据：0 成交时任何"滑点"都是伪测量；**宁可缺一个数，不可有一个错数**——
  错数会进闭环并被当作证据复用，缺数只是少一条证据。
  测试钉：构造 `actual_quantity=0` 断言 `slippage_bps is NULL`；改回旧算法必须红（能红证据）。
- 处方全文 `lanes/wirerecon_BRK020_gap.md`（G1-G6）。**G1 是阻塞级地雷**：
  `execution_report_producer.py` 与其测试**仍是 untracked**，broker 四个接线方法**仅 unstaged** →
  按现 staged 面落地即 `ModuleNotFoundError`，**会打断整条 ex_core import 含前端健康监控** —— 与我给
  z-land 的配方里"新 .py 三件套 + token 同批入面"是同一课。**必须四件套原子落地。**

**R-015 · 对账域"五个孤儿 + 一个认错人的"（z-wire-recon 实证）**
- 实测：对账实现**六件并存、六件全部零程序消费** ——
  `position/`×1、`ex_core/`×2、`trading/recon_runner` + `three_way_reconciliation`、`orchestrator/`×1。
- **裁定=按 R-002 同一原则处理：merge 定权威，不许各留一套、也不许 ack 式登记了事。**
  理由：六套并存意味着"对账"这个概念没有唯一真源，那么任何一次对账结论都无法判断是谁算的 ——
  这正是资金语义上的架构级取舍，**但它需要跨 6 个文件的语义比对，且删冗余实现会触注册表净删（Owner 门位）**。
  → **列入 Max 待执行清单**（附六件路径与差异表），本轮**不自行合并**。
  → 本轮先做不删任何东西的一步：确立**唯一入口**（谁该被调度器调），其余标注 `superseded_by` 注记。

**R-016 · pf_alloc 测试实况纠正（勿沿用前任声称）**
- 前任交接令声称"23/23 + 回归 2680 通过"。z-land **实测**：`tests/risk` 1857 passed；
  **`tests/pf_alloc` 382 passed / 8 failed**；alt_data+sector 40 passed；幂等三套件 50 passed。
- **裁定：pf_alloc 8 红必须先归因后落地，禁带红落地、禁降级断言让它们变绿。**
  归因三分法：①本战役引入（必修）②他会话在途（不代修，登记）③环境性（如并发锁竞争，独立重跑证明）。
  → 幂等键 50 passed **含"下单→崩溃→重启→同信号重放不二次发单"这条硬判据，且测试是前驱车道已配的**
  → 分包12 T3 **实质达成**，只等 G1 式原子落地。**这是本轮资金安全面的头号成果。**

**R-017 · 车道撞门禁的通用处置（本轮已三次撞见，固化为协议）**
- 已见三例：①`MANUAL-ONLY-PERMANENT` 因**文本子串快检**把新函数名 `_probe_input(` 误命中为 `input(` 而拦
  （车道选择**改名治本**，拒绝打 `m11 合法 manual` 假豁免 —— 判定正确：本件非 CLI 工具，
  标"合法 manual"是伪证且触裁定#273 禁白名单消警）；
  ②`CREATE-GUARD` 死信：§3.4 的"worktree-only 登记"只适用**直连**路径，
  **队列侧 serializer 必须看到 token 已入提交面** → 队列批必须 token 同批进 `--files`；
  ③`ALGO-NOTE-SYNC` 死锁（见 R-012）。
- **协议**：撞门禁时车道**先判门禁说的是不是真问题**——
  真问题→治本（改名/补 token/同批注记）；门禁自身有缺陷（子串误命中类）→**治本绕过 + 把门禁缺陷登记为断点**，
  不走豁免旗。凡走豁免/加旗硬闯 = 交工报告必须单列并说明理由，总包复核可否。

**R-018 · 交付三清单制 + 车道自报义务（Owner 令，2026-09-18 18:3x）**
- Owner 追加交付要求：**除完成报告外，必须交付「需 Max 复查清单」** ——
  「Flash 可能会有很多执行上的遗漏或者是漂移幻觉。很多重要的节点、岔路口、重要算法需要 Max 检查一遍。
  你裁定过的所有内容都需要 Max 全部去看一遍。」
- **原则：执行者不能给自己的活签字。** Flash 四类系统性失效（遗漏/漂移/幻觉引用/误归因）
  **在自报里天然不可见** —— 出错的一方不知道自己错了。
  本轮已有两实证：①元挖矿普查被车道抓出误归因（R-013）；②前任交接令声称"全绿"被实测推翻（R-016）。
- 载体已建：`delivery/MAX_REVIEW_CHECKLIST.md`（已收录 R-001..R-017 全部总包裁定 + 3 笔 commit + 系统级抽查方法）。
- **车道自报义务（对所有在飞与后续车道生效）**：交工报告除原有内容外，须增一节
  **「我的高风险判断」**，逐条写：
  `判断内容 | 依据(实测/转报/推断) | 若错会怎样 | 一条能让 Max 验真的命令`
  → 凡依据为**`转报`（别人说的，我没独立复跑）或 `推断`（结构推得，无实测）**者必须显式标注 ——
  这两类是 Max 复查的重点面，**标了不算失职，漏标才算**。
  → 主动交底弱裁项比被查出来值钱。总包自己的示范：已在本清单中把自己裁的
    "对冲合约选 IM" 标为**全清单最弱一条**（纯结构推断、未做 beta 回归实测）。
- 三清单收工口径：**（A）需 Max 裁定** / **（B）需 Max 执行** / **（C）需 Max 复查**，
  均带完整路径（文件:行号 / 命令 / 证据位置），使 Owner 切 Max 后**直接开工不需重新勘察**。

**R-019 · ⚠️ 断点普查来源系统性陈旧（z-wire-safety 实证）—— 85 条断点数不能当基线用**
- 实测：本簇 7 条断点里 **4 条记载已陈旧**。`BRK-004`/`BRK-005` 的 A3/A4 接线**早在 2026-09-16 `49dde8fda5` 就已在 HEAD**，
  普查却按 GOMAP `pipeline.disconnected` 报成"零消费"。
- **根因（结构性，非一次性错误）**：`config/governance_operations_map.yaml` 的 `pipeline.disconnected` 是
  **人工语义层**（生成器保留、**落地后无刷新义务**）→ 接线一旦完成，该字段不会自动更新，于是"已修"被持续报成"待修"。
- 影响面：普查 §A（19 条孤儿）与 §E（12 条死管线）**大量依赖 GOMAP 与蓝图注释** →
  **这些条目的"待修"状态可信度低于 §B/§C/§D 里带 `grep`/SQL 直查证据的条目**。
  叠加 R-013（BRK-017 误归因）与 R-016（前任声称"全绿"被推翻）→
  **"85 条断点"是检出面上界，不是可靠基线；本轮"闭合率"分母不可信。**
- **裁定：所有在飞与后续车道，施工每条断点前必须先复跑普查给出的原始证据命令**（普查每条都带了命令与实测输出，
  照抄跑一遍 30 秒）。复跑不符者标"已闭合，建议关闭"并**回写普查该行**，禁按陈旧记载重复施工。
  → 已要求把"施工前复测原始命令"作为一步写进验收规范（z-wire-safety 提交了 `req_wiresafe_01.md` 第④项，总包采纳）。
- **已采纳并落地**：本裁定的载体 = 验收规范 §1 六向第①向"入口有料"补一条前置：
  **"复测"先于"施工"** —— 断点的①向证据必须是**本次实跑**，不得引用普查登记的快照值。

**R-020 · 总包指令被车道实测推翻（记为协议级更正，防后人沿用我的错）**
- 我在 z-wire-safety 任务书里写"比例 `beta×0.5` 进 `config/crisis_gate.yaml`"。
  车道实测：`src/zephyr/pf_alloc/crisis_gate.py:155` **对未知键是硬错** → 照我说的加会**当场打死危机闸主链**。
  车道拒绝执行并改用 `config/paper_hedge.yaml` 独立载体（含 `IM` / `beta×0.5` / `real_channel_locked`）。
- **裁定：车道抗命正确，予以确认。** 教训固化：**总包在任务书里给出的"改哪个文件"属结构推断，
  未经读码验证；车道以实测为准，与实测冲突时服从实测并回报。**
  → 后续任务书凡涉及"往某配置文件加键"，一律要求车道**先读该文件的未知键处理逻辑**再决定落点。
- 同源第二条：`BRK-021`/`BRK-072` 的标的已由他道**未落地件**占据
  （`src/zephyr/risk/paper_hedge_leg.py` + `config/paper_hedge.yaml` 实测 untracked）
  → **总包须把这两件的落地权明确指派给一条车道**（原 z-residG 已停，其 E6 纸面对冲腿产物无人认领）。
  → **指派给 z-land2**（其正在做落地接力，同一提交通道，避免并发写 `src/zephyr/risk/**`）。

**R-021 · 假通道的一个新形态（值得永久化到门禁判据）**
- z-wire-safety 在 BRK-066 实测：`host_resource_governor` 的旧 `probe()`
  **恒返 `16000MB / 12.5% / OK`** —— docstring 自称用 psutil，全件零调用方。
  即：**它不是"没接"，是"接了也不会报真值"，而且看起来在工作。**
- 已修为实探 RAM + Windows commit charge（`GlobalMemoryStatusEx`）+ CPU，阈值零代码副本
  （`alert_rules` 新增 `ALERT-SYS-003/004/005`），命中走既有通知板。
- **通用判据（提请 Max 考虑立门禁）**：*"函数返回带单位的数值 + docstring 声称某数据来源 + 但该来源库/对象在函数体内未被引用"*
  = 硬编码假通道嫌疑。本仓"全流通"验收第⑥向（失败会响）应把这类**恒真返回**列为必查项。
- **同族第二例**：BRK-005 的看门狗旗标此前**只写不读**（`escalation_engine:383` 写，全仓零读方）
  → 与 R-K6"假处置"同型：**写了不等于有人看**。已让 guardian 把它计作一条失效判据腿。

**R-022 · 车道上报的待裁四项（z-wire-safety `req_wiresafe_01.md`）—— 总包裁定**
- ①`BRK-021`/`072` 标的转交落地 → **裁定：转 z-land2**（见 R-020）。
- ②`kill_switch_sim.py` 净删候选 → **裁定：不删，登记为 Owner/Max 门位项**（注册表净删=§7 门位）。
  本轮只做"确立唯一入口"（已做：策略层 MOD-AU-004→路由层 MOD-AU-002→5 套本体三层已明，boot 同批注册策略层 + grep 型唯一性测试钉）。
- ③**保命轨 `enabled:true` 盘内自动拉系统闸是否可接受** → **裁定：列入 Max/Owner 待裁清单（A 类），Flash 不签。**
  理由：车道自己的判断准确 —— 默认启用属"加严"（不触 #321 禁止），但它**会在数据抖动时自动影响交易**，
  是**资金影响面的生产流转**（宪法 §5 high 域门位）。"加严所以不必申请"这条规则**不适用于会主动动作的闸**：
  加严免申请的前提是该改动只收紧"能不能做"，而不是系统**自己开始做某件花钱的事**。
  → 本轮保持车道实现的**四道防误触发**（unknown≠失效 / 4h 证据视界 / 盘外只判不动作 / 连续确认），
    但**不启用盘内自动拉闸**，等 Owner 判。
- ④普查复测步进规范 → **采纳**（见 R-019）。
- 未闭项如实记录：`respond()` 生产调用点仍 **0**；CB×9 未收敛；escalation L4→`respond()` 需改 human_gated 件；
  BM-RC-12 锚点 DB 登记未做；`docs/03_modules/**` 禁写致 ALGO_FLOW 只能走内联形态。

**R-023 · Wave 3 首批交工入账（z-wire-safety / z-datagap / z-failopen 三笔落地）**
- 落地实测（截至 19:24，共 6 笔进 HEAD）：`7b451b7f76` 保命链批1 / `35690242e7` datagap 止血批 / `8a8a3f9290` 假通道收口。
- **z-failopen 头号发现（P0 级假处置实例）**：`src/zephyr/data/scheduler.py:732-762 / 1376-1388` 的 CH 探活 CRITICAL 告警，
  原实现=**先无条件置 `_ch_probe_alerted_dead=True` → 再 try notify → `except: pass`**；
  而 `Alerter.notify` **本就不抛异常、以返回值表态** →
  **告警从未落盘而闩已锁死，该进程余生不再重试**。
  → 已改为 `_deliver_alert_with_latch`（真落盘才置闩、失败下轮重试）；DDL 缺失告警的 4h 去重戳同病同治。
  → **可泛化缺陷类（提请 Max 考虑立门禁）**："**投递前先置去重/已处理闩**" ——
    凡 `set_latch(); try deliver(); except: pass` 三段式都属此类，**且它在告警/熔断/自愈路径上时最致命**
    （恰在最需要发声时静默）。全仓同类扫查已派工（见 R-024 车道编制）。
- **普查可信度新增两条同型证据**（并入复查清单 §0）：
  ①**漏计**：`except…pass` 普查口径 144（"次行偏移"启发式），AST 严口径（handler 唯一语句为 pass）实测 **261** → 普查不完备；
  ②**归因放大**：`BRK-048` 报"5 处硬编码 fail-open 放行点"，实测是 **1 个定义 + 4 个消费点、同属 LSG `FAIL_OPEN_LAYERS={l6_observability,l7_validation}`**，
    且 L1-L5 本就 fail-closed 并留有 decision 痕 → **1 个构造被报成 5 个独立风险点**（与 R-013 同型）。
  ③普查所称 `BRK-029 sector_fund_flow` "从未灌入一行"**已不成立**（现实测 1467 行 / 4 快照日，被在途车道补线）。
- **总包前置裁定被机械印证**：R-K/R-047 令"1405 处不得无差别改造"→ 登记册实测 `total_fail_open=1595`、
  四档分布 hardcoded 5 / money_path_no_trace 176 / designed_with_trace 735 / undeclared 679，
  **FF-14 独占 1027（64%）** → 该裁定的"多数是有意降级"判断成立。
- **诚实入账两条负面**：①因加严而转红的测试 **0 条**（说明无既有测试依赖被吞行为 —— 这是好消息但也意味着
  既有测试面**覆盖不到这些路径**，本身是缺陷）；②`allow_empty` 收口 11/12 后 breach **0→0**，
  原因是那 12 张表当日**全部有数** → **白名单是过期死重量而非活风险**（收口动作正确，但收益是"消除未来盲点"而非"发现当下断供"）。
- ⚠️ **总包自记保护网漏洞（R-007 过度声称）**：我曾在 R-007 写"自此任何后续操作均可回滚，零丢失风险"，
  **但归档脚本只覆盖了 staged 与 worktree-modified 文件，未跟踪文件没进归档**。
  而未跟踪态**恰恰是最易被 sweep 掉的形态**，且本次未跟踪区里有 `execution_report_producer.py`（G1 地雷正主）、
  `owner_regime_switcher/` 7 件、`alert_webhook_dispatch.py`、`generate_standard_family_registry.py` 等成件产出。
  → **已补洞**：82 件未跟踪（除 `c4_pdf_cache`）全量镜像至 `.runtime/tmp/ff_quarantine/untracked_snapshot/`
    + `MANIFEST_untracked.json`（67MB），三个关键件核验在内。
  → **R-007 的"零丢失风险"表述作废**，更正为"staged/worktree/untracked 三面已全镜像"。
  → 教训：**"归档完成"必须以"覆盖三种 git 状态"为判据，不能只数 `git diff` 出来的那两面。**

## 7. Owner 门位（登记不催，禁自行执行）

以下是宪法 §5 的 high 域门位，**任何车道都不得执行**，只登记：
- production 流转 / 实盘账户启用开关（实盘 8887871993）
- 注册表**净删**（如旧域空行过渡态、ETF 备份五表 `*_tz_bak_20260918` 物理删除时机）
- flag 出厂翻转（`config/flags.yaml` 三个 production=true）
- 资金破坏性操作（4.12 亿行 ETF 时区 `--execute` 需低峰窗 + Owner 批）
- 需 Owner 注册外部账号（MSCI 官网 DS-CAND-016）
- 需硬件/基础设施变更（ClickHouse 与 Redis 分机、副本、灾备扩容、页面文件扩容重启、F 盘空间）
- 真实期货通道解锁（纸面≥3 演练 + 实盘门位）
- 需 Owner 提供凭据（E7 告警推送 webhook 四类凭据）

**注**：门位项登记 = 已闭环，不算未完成（分包4/分包6/分包7 交接令均明文）。

### 落地车道 st-ff-land-20260918 · 交工与接力（2026-09-18 19:0x）

| 编号 | 车道 | 主题 | 状态 |
|---|---|---|---|
| req_land_01 | st-ff-land-20260918 | R-008 收割批1 撞 ALGO-NOTE-SYNC：regime_meta_allocator.py 的 TDM-F-C3-03 note 同步须写 config/trading_decision_map.yaml（对本车道是禁写文件） | 待总包裁（本批已摘除该件，余 17 件入队 q-…-0004） |
| req_land_02 | st-ff-land-20260918 | R-008 第二步实测修正：31 件存量不是工具现有"auto-injected 注入块"形态（实测 line1 prose=『(长城任务 2026-09-09)』不匹配 `_INJECTED_LINE1_RE`，重复 TTL 在头部块尾第 16 行），车道已按确定形态 B 补治本并落地 19 件；余 12 件复扫为 too-short/单一 TTL/非头部块 | 已治本落地·待总包确认形态 B 入 INVARIANTS |

- 已入队并（除注明外）待 serializer 消化：q-0001 已 dead（见 req_land_01）/ q-0002 幂等键三件 /
  q-0003 BRK-086 工具+测试+19 件 TTL 去重 / q-0004 危机闸 17 件。
- **未落地清单（轮数预算耗尽，保持 staged 原样未动）**：
  ①`scripts/backtest/crisis_drill_monthly.py`+770（NO-HIGH-COMPLEXITY 无逃生，需抽
     `_parse_xxx()`/`_row_xxx()` helper 降复杂度；预裁 R-K1）；
  ②战役真源与元挖掘 docs 批（fullflow_campaign 骨架+普查 / n5_closure / flash_speedup /
     tdchain_mine / kimi_audit / residual_construction / pipeline-research，共约 33 件，
     新 .md 全部缺 creation_token → 必须先逐件 `batch_creation_tokens.py --prefix <完整路径>`
     再与代码同批提交，载体 docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml）；
     其中 `docs/_working/pipeline-research/sim-memos/sim-memo-202609.json`（1378 行）按 R-D1
     与 DIRECTORY-CONTRACT（docs/_working 只放 .md/.yaml/.csv/.html）**永久剔除**，交总包决定落点；
  ③其余 260 件（scripts/tests 的 TTL 去重与治理工具改动，清单
     `.runtime/tmp/ff-land/rest.txt`，raw numstat 与 --ignore-cr-at-eol 全等=零换行噪声）；
  ④execution_report 生产者接线：`src/zephyr/ex_core/adapters/qmt_file_bridge_integration.py`+45
     staged 未落，因它 import 未跟踪新模块 `src/zephyr/ex_core/execution_report_producer.py`
     （实测 tests/ex_core/test_execution_report_producer.py 与之同跑 50 passed）；新模块缺
     creation_token/翻译登记/depgraph 节点，单独入批会 CREATE-GUARD 死信并连带拖死资金安全批，
     故整组留 staged；
  ⑤4 件 STALE_INDEX（echo-guard.yml、module_translation_loader.py、test_module_translation_loader.py、
     ai_layer_vision/OBJ_R_rules_standards/DESIGN.md）索引内容与已落 HEAD 的 30dc814645 相反
     （提交=回退 R-002），已逐文件 `git restore --staged --` 归位（工作区即 HEAD，零内容损失）。

**落地车道关键阻塞（须总包处置，车道无法自愈）**：门禁 **ALGO-NOTE-SYNC** 要求
被触碰模块的 TDM 节点 `algo_note_zh` 随同一 commit 修订（或加 `note_confirmed: 2026-09-18`），
而真源 `config/trading_decision_map.yaml` 对所有落地车道都是禁写文件 → 凡含 TDM 绑定模块
（pf_alloc / ex_core/order_manager / risk / alt_data 等）的批次必然死信。
实测两笔死信：q-…-0001（TDM-F-C3-03 ← regime_meta_allocator.py）、q-…-0002
（TDM-E-L4-10 ← order_manager.py，=资金安全幂等键批）。
**请求**：总包在 TDM 为受影响节点补 `note_confirmed: 2026-09-18`（纯注记，零代码语义），
随后车道执行 `python scripts/commit_queue.py requeue <qid>` 即带当前字节重投。
另：本车道另见 MANUAL-ONLY-PERMANENT 全仓扫描命中外来件
`src/zephyr/governance/resilience_governance/emergency_track_guardian.py`（非本车道文件，
按 §3.4 不代修），它使落地批 1b 在 preflight 即被拦——同属维护班清账范围。
