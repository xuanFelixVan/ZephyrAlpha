---
ttl: task_bound
session: st-xhs-full-20260922
topic: tc01_memo_recon_inputs
---

# 备忘录清理决策链 L4 复审报告（复审的复审，2026-09-21）

> 本报告是 L4 红蓝对抗位对 L1（report.md）/L2（review.md、full_report_20260921.md）的独立复审。
> 目标不是确认 L2 说得对，而是逐条钉出 L2 说错、说过头、方向说反、把未验写成已验的地方。
> **全程纯只读**：除本文件外未写任何仓库文件；无 git add/commit/stash/checkout/restore/clean；无生成器；无写库；无计划任务启停；无脚本落盘（python 全部 -c 内联只读）。

---

## §0 开工记录

| 项 | 值 |
|---|---|
| L4 执行 | 独立复审会话，2026-09-21 04:02~04:30 (+0800) |
| 快照 HEAD | `669099c7e730bf7b1a6cd1e943a6b43ae6593cfe`（2026-09-21 03:53:13 +0800） |
| 与 L2 时点差距 | `git rev-list --count 2d7308df1f..HEAD` = **22**（L2 复审于 2d7308df1f；L1 案卷自称 1ad0003e36） |
| 输入件三 hash（与备份 SHA256SUMS.txt 逐字一致） | report.md=`bda5f1cabd0b7ed782f30fc7b95e449e86858e15bc04c8a3530fbba03dccaa04`；review.md=`a3ad137d1285ac3ec1a8d77982b2c4765752f997b92fd39bb5e8bd6f1f3300ce`；full_report_20260921.md=`9bfe148d877e7fd6592965d3926797946d8b1030d666c3567e654648ff6a7db2` |
| 备份核对位置 | `.runtime/sessions/st-taskcards-exec-20260921/staging/memo_recon_inputs_backup/`（四件含 SHA256SUMS.txt，均一致） |
| 工作区在途规模（取证时刻 2026-09-21T04:02:34+0800，动态数） | ` D`=135、`M `=301、`A`=192、`R`=66、` M`=49、`MM`=8、`??`=34（与 L2 时点的 168/224/191/66/265/25/37 又已漂移——C 类归档战役仍在途） |
| 热文件取证纪律 | ruling_registry.yaml / known_data_gaps.yaml / factor_registry.yaml 一律以 `git show HEAD:<path>` 对照工作区版双读；两文件现仍处 staged 修改（`M `） |

---

## §1 17 条逐条判定表

> 等级：A=本会话亲跑命令实证（附关键输出）；B=转述或未重跑。L4 判定四态：可删/需改写/仍开/未决。

| 条 | L1 原判 | L2 改判 | L4 判定 | 证据（命令→关键输出） | 级 | 一句话差异说明 |
|---|---|---|---|---|---|---|
| A1 遥测归档 | 叙述过期（灯装了线接一半） | 推翻：Owner 基本对 | **需改写（L2 方向对）** | `sed -n '460,495p' facade.py`：`try: from ...archive import rotate_by_ttl; rotate_by_ttl()` + `except Exception: _logger.debug("archive_check failed")`；`sed -n '110,135p' cold_stub.py`：`def rotate_by_ttl(base_dir: Path, max_age_days: int)` 双必填 → 零实参必抛 TypeError 被吞。`grep -rn "rotate_by_ttl\|compress_dir\|RetentionPolicy"` 除本体/re-export 外零调用方（market_data_aggregates/gov_audit 的 RetentionPolicy 是同名异类）。flags loader `flags.py:354-355` 只映射 enabled+description，retention_days/compression/implementation_status 加载即弃。`find data -name '*.gz'`=0；data/telemetry/prod 只有 logs（26 件，17 件超 30 天仍留存） | A | L2 核心推翻全部亲验成立；另结 L2 未结案点：首提交=`a5c1a81787`（2026-06-21），L1 写的 `787f7a6ba4`（2026-05-06，audit commit）**未触过该文件，错** |
| A2 field_dictionary 缓办 | 仍开（前提被推翻） | 同意仍开，但"表建成"未证满 | **仍开** | `grep -c 待定 config/strategy_production_map.yaml`=3（L341/365/388 均 `location: 待定（E7/E8/E9 施工时定）`）；FAC 节点=16；`grep -c "^- field_id:" field_dictionary.yaml`=262 = ROOR`:675` entry_count:262；探针列 candidate_id/verdict/eps_consensus/n_reports/net_profit_ttm/eps_std/eps_mean/hypothesis_precheck/consensus_daily/strategy_screen **全 0**；`git log --oneline -S"c1_backtest.hypothesis_precheck" -- src/` 有消费方线索 + `grep -rl "hypothesis_precheck\|strategy_screen" src/zephyr` = 7 文件（n_trial_ledger/api_server/strategy_screener_3d 等）；DDL 脚本 apply_hypothesis_precheck/financial_derived/consensus_daily_ddl.py 在位；字典最后内容提交 `00f525d348`(09-13) | A | 待定3/16节点/262/探针全零亲验成立；"表已建成"仅能证到"DDL在位+代码有消费方引用"，实物在 CH（§4）；辖区反论点（字典 L21-27 仅管数据层字段）维持为活反论 |
| A3 老数据重验 | 仍开（约1/7，42760 未验） | 同意仍开；1/7 与 42760 口径混用 | **仍开** | 报告亲读：L26 `共 51,345 行`、L32 `A 组 7,337`、L33 `B 组 44,008`、L52/80 `44,008 待施工`、L85 `558 名回填→1,248 行升级（7,337→8,585）`；全文**无 42,760**；`7337/51345=14.29%≈1/7` ✓；`.runtime/audit/name_backfill_qa_20260915.json` 在盘（99657B 等 4 件），`total_checked=558`+session st-igbe-20260915 亲读 | A(算术+报告)/B(QA 深层字段) | 分母 51345=7337+44008 自洽 ✓；L1 的 42,760=44008−1248 把"已回填"错当"已验"（回填≠三检），真未验=B 组全量 44,008；L2 的批评方向对、其"未代码化"解释含混 |
| A4 详情页上下游 | 终局（两尾巴） | 同意终局；尾巴②半推翻（valid_to 有过滤） | **可删（留一条真尾巴）** | `sed -n '4045,4058p' api_server.py`：两条 SQL 均含 `valid_to IS NULL`；`source` 仅被 `_CM_SOURCE_EDGE_KIND` 分类，**无已验源白名单**；`eb9f3915eb` 祖先 exit=0 | A | L2 半推翻亲验成立：真缺陷只剩 source 无白名单一条（与 A3 的 44,008 未验行联动） |
| A5 消费端两选一 | BDI=终局封矿；政采=未开工 | (a)升A；(b)同意+口径修正 | **可删** | plan L134 `不升级为因子卡，就地封矿留痕`、L138 不注册 IC/不挂 TDM/不登记、L196 `维持封矿`；`grep -ci 'typhoon\|bdi\|台风' factor_registry.yaml`=0；政府采购/ccgp 在 src/zephyr+scripts+config 零文件命中；tasks.yaml/schedule.yaml 零命中 | A | 两支均无待办：(a) 裁定封矿在册，(b) 从未立项（删前 Owner 须知 (b) 是"消失"非"完成"，L2 话术正确） |
| A6 dead/ 953 | 终局 | 同意；活区 69→74 | **可删** | 取证时刻 2026-09-21T04:11:59：`dead`=**123**（69→74→123，24h 内翻倍级漂移，常态运转非欠账）；archives 61/25/912/48/113 与 L1/L2 全同；`dead_triage_20260914.jsonl`=25 行=授权数双重吻合 ✓；x1/x1b 目录数=jsonl 行数（912/48）；`dead_archive_20260830` dir=61 vs jsonl=23 行（两判据不平，L2 观察属实） | A | 终局维持；960 vs 953 差 7 三方均无解释，挂起不阻断"按授权边界处理完毕"的结论 |
| A7 16 硬报错清零 | 数字终局；定性待裁 | (b)真欠账+(c)绕门禁；不认(a) | **仍开（(b)成立；(c)过重须降格）** | 门禁 `registry_alignment.py:347-357` 亲读：`for v in e.get("inputs") or []`（空=零迭代即过）+`if not v: continue`（空串也过）；`grep -c 'inputs: \[\]' factor_registry.yaml`=171（工作区=HEAD）；姊妹库 technical_indicator `inputs: []`=**0**/inputs 行 139；`git show b1c59c9cda`=恰 8 条 `["c3_fundamental.financial_derived(DS-230) 对应列"]→[]`；`git show 1d23039e90`=恰 6 条（consensus_daily(DS-229)/research_report(DS-228) 族）→[]；**两笔合计 14 条目 16 引用**；python yaml 实数两库 inputs 列表元素总数=**275**（171 空条目）；提交语亲读：b1c59c9cda=`自由文本改结构化 []`、1d23039e90=`inputs=[] 全库惯例`（公开声明，非隐瞒） | A | (b) 成立（171 空接线+16 引用被清而非转正）；(c)"绕门禁"**过重**：被清引用本是自由文本、从来不是合法字段 ID（门禁从未"看见"过它们），且两笔提交在 commit message 公开声明做法——准确定性=门禁政策空缺（无非空判据）+可追溯信息删除；L2 对 L1 的两处"数字纠正"①②**均错**（详见 §3-1/§3-2） |
| A8 tick 8 天缺口 | 仍开（路径口径不匹配） | 仍开；归因=--days 逗号单串；"一条命令可收口" | **仍开（归因方向采 L2；"一条命令"驳回）** | **日志已灭失**：`.runtime/tmp/tilib-probe/` 整目录不存在（24h TTL），L1/L2 的日志级证据不可再复现（对我=双源独立转录一致的 B 级）。代码级亲验：`import_bdpan_tick_zip.py:156` `--days nargs="*"`、`:165` `[d for d in args.days if d in by_day]`（逗号单串→交集恒空）、`:176` rc=3、`:36` 缺省=扫目录、`_index_zips` 用 `iterdir()+is_file()`（不递归）；E 盘亲列：7 zip 平铺、mtime 09-17 00:20~00:25、月目录 00:27（20260703.zip=83,705,415B 与 L2 记录逐字节一致）；**zip 内构亲验**：20260703.zip=5199 csv / 20260805.zip=5200 csv、UTF-8 BOM、表头 `时间,成交价,手数,买卖方向`、首行 09:15 竞价手数=0——与导入器 docstring 期望一致；幂等预检存在（`import_day`: `pre=count(); if pre: return skip`）；CH 写入经 `get_db_service().get_clickhouse_conn(role="admin")`；known_data_gaps.yaml:383-386 工作区=HEAD 仍写 `accepted`/`无 2026-08 文件夹`——**与 E 盘 20260805/0806.zip 实物矛盾在案** | A(代码/E盘/zip/known_gaps)/B(日志内容) | L2 归因（参数格式非路径）与代码逻辑自洽、采信；但"一条命令可收口"驳回三点：①08-05 已有 1 行杂散行→预检必 skip，该日缺口不会被收口（动它=破坏性操作+Owner 面）；②CH 重写入车道正被他会话占用（st-data-fix-20260921 报告载明 01:45 起，协调板 ACTIVE）——须走协调非随时可跑；③"CH 六日 0 行"前提随日志灭失只能转述。另 F-05 裁定事实前提已被 E 盘实物证伪（§5-4） |
| A9 交易日开终端 | 叙述过期 | 同意 | **需改写** | `cat .runtime/logs/paper_session.log` 恰 4 行：09-17/09-18 `SKIP: XtMiniQmt`、09-19/09-20 `SKIP: (is_trading_day=False)` | A | 一致；补新状态：`schtasks` 实测 `ZephyrAlpha_PaperSession`=**就绪，下次运行 09-21 09:25（今日）**——首跑仍有机会，非死项 |
| A10 自动运行四站 | 部分成立 | 同意；heartbeat 证据已蒸发 | **需改写（+两处新事实）** | fired 尾序亲验：factory_lane_c=`09-16 15:35:04→09-19 10:00:00`（09-17 确未点火；**09-20/21 无点火**）；c4_exam=`09-16 17:32:22→09-19 14:00:00`；heartbeat 文件亲验不存在 ✓；fetch_perf 现 5 件（20260917~21.jsonl，比 L2 的 3 件更强）；**`schtasks //query //fo LIST` 亲验：`ZephyrAlpha_FactoryLaneC`=就绪（下次 09-26 10:00，每周六档）、C4Exam=就绪（09-26 14:00）、F06Grid=就绪（09-26 23:00）、AltFxECB=就绪（09-21 23:30）、BdpanTickWatch=就绪（每日 08:00）**——四件"清理对象"全部未 Disable | A | L1 的"任务现 Disabled"（引自 p7a:210）**双重错**：p7a 裁定表格原文写的就是 `Ready`+`清理对象`（判定=要 Disable），现状实测也仍 Ready——L2 未跑 schtasks、把 L1 的错表述原样保留为 B。C-16 批清理令登记未执行（§5-3）；tick 09-17 残余疑已闭合（§5-2） |
| A11 ALGO_FLOW | 机械面终局；79 下界；净增10 | 同意终局；79 近精确；净增10口径错 | **需改写（L2 主结论对，两细节修）** | 三分类重扫（同 L2 判据）：`{'ext_only': 3234, 'inline_only': 79, 'both': 0}` 总 3313——**L2 的 both=1/3311 不复现**（worktree 已变；且按 L2 自公布脚本，gate 文件 ：9 含散文 `# [ALGO_FLOW] external: <path>` 应落 ext_only 而非 both——L2 报告与其自公布判据内部不一致）；inline=79 与 L2 一致；**档案↔路标 1:1 亲验**：`# [ALGO_FLOW] external:` 出现 3235 次=3235 唯一路径（含 gate 文件 1 条散文假阳性 `<path>`），真实路标 3234 条 ↔ `docs/03_modules/**/algo_flow/**.yaml`=3234 件，**零缺失零孤儿**（Owner 的 3158 已陈旧，"一一对应"实质今日成立）；debt 台账 69 件路径全部 ⊂ 现内联集（零清偿）✓；inline−debt=**10**（L2 写 4，系其用严格 73 件集作减数——其数字在严格集下可复现，但行文紧邻"79"易误读为同集）；10 件中 3 件 last commit 09-16（早于台账扫描 09-17T03:49）→台账判据差实证，另 7 件晚于扫描→L1"净增 10"不可证实亦不可证伪 | A | L2 三个主结论（79 近精确/净增10不成立/报告挪路径）亲验维持；修正 both=1、补验 3158→现 3234 件 1:1 对应；L2"4"应为"10（79 集口径）" |
| A12 daban 链 | 终局（两尾巴） | 同意，接线升 A | **可删（留尾巴知悉）** | HEAD 版 ruling_registry `裁定#277`（L2681-2726）亲读：标题含 `双零表 936 行真数据贯通`；summary 含 `daban_board_event_derive 936 行→daban_engine_load_daily 936 行（09-01..15 窗）`、`面板产真实权重 4 只各 0.15（max_single 截顶，sum=0.60）`、`精确 close≥stk_limit.limit_up=30`；evidence 字段载明=实跑日志+CH 终态（各 936 行，周末分区=0）+测试 140 例×2 轮；两尾巴（周末档/`ROUTE_NO_DAILY_SOURCE`）裁定文内自认 | A(在册文字)/B(936 实物) | Owner 三个数字（936/4×15%/30 只）全部溯源到 #277 在册文字 ✓；实物（CH 行数）只读不可证（§4）；#302 在册 L3680 |
| A13 车道群质量 | 非任务可删 | 同意可删 | **可删** | 评价性段落，无可机械证伪的待办；其点名的伤项另册在案 | C | 三方案卷一致 |
| A14 Kimi 裁定班 | 裁定终局；93 与编号链未决 | 两未决结案：编号链=转述正确；93=精确成立 | **可删（改指针后）** | `git show 2d7308df1f:...ruling_registry.yaml | grep -n renumber_note` → **L2 时点 HEAD 已有 3766/3782 两注记**（行号与 L2 引用逐字一致）；现 HEAD 三注记（+L4256 #293→#386）；HEAD 亲读标题：`裁定#331`=做T v2 升级战战役砍（现形态）、`裁定#332`=STD-SWITCH-001 定稿、`裁定#306`=模拟盘准入组合门 v2 提案（号未变）、`#304`=Regime 重校准、`#305`=日度编排器八点批准；`git show --numstat dd56908c8e | awk '$3~/blueprint\.md$/'`=**93** ✓；kimi_audit=115 文件/94 md/29 顶层/0 蓝图 ✓；docs/03_modules blueprint.md=542 ✓；签字单 grep `331|332`=**0**、L17/L19 仍写 #304/#305（L2 的 B 升 A） | A | L2 两项结案全部亲验维持；**但 L2"全部结论建立在未提交内容上"的自我声明是错的**——renumber 证据在 L2 时点已是 HEAD 事实（§3-4）；#293 重复已被 a03179e2fa 修复（现 HEAD 零重复） |
| A15 提交链 F1-F4 | 部分完成 | 同意；但 L1 引用了不存在的 commit | **仍开（F2 卡 Owner）** | `git rev-parse --verify 025df45e0`→fatal（exit=128）✓ L2 对；`025df945e0`/`fe47296db5`/`604f414846`/`727ad32a54` 祖先全 exit=0；台账 `00_master_ledger.md:53` 亲读：F2=`✅ 前置①②③④施工完毕全绿…⑤「7 天>40 车道」=观察窗件…「k=4 通道就绪，待 Owner 签 S18-R3」`、`:20` `S18-R1~R4（四张裁定书，均待 Owner 签）`、`:21` 通道数=Owner 门位；台账自身写 F4 证据=`025df945` | A | L2 全部维持且 F2 门位由 B 升 A（台账+行号亲读）；L1 的 hash 转置确认 |
| A16 六个设想 | 落地度不齐 | 同意；maturity 真源指针错 | **仍开** | MATURITY 头亲读：crowd_game_simulator.py:7=production(MOD-SIG-114)、capital_behavior_orchestrator.py:7=testing(MOD-SIG-088)、manipulation_avoidance_detector.py:7=design(MOD-RK-39)；`grep -c "MOD-SIG-088\|MOD-SIG-114\|MOD-RK-39" candidate_module_registry.yaml`=**0** ✓ L2 对；④人性：src/zephyr 唯一命中=time_utils.py:28 注释"人性化的 datetime API"（非业务）；⑤玄学：bazi/生肖/八字/星座 零命中；`c007caac86` 祖先 exit=0；wiring_registry.yaml 在主树 catalogs（L1 路径无误） | A | L2 指针纠正亲验成立；④⑤零命中我亲跑补验（L2 未做）——B 升 A |
| A17 成本模型+防前视 | 终局 | 同意，逐字成立 | **可删** | `cost_model_calibration.py`：L115 window_start="2026-07-24"、L117 n_symbols=5519、L118 n_tick_snapshots=13119233、L147 `1bp 与实测最便宜一层（2.34bp）都相差 2.3 倍以上`；`LookaheadExecutionError`：定义 engine_base.py:165、raise 全仓唯一=vectorized_engine.py:248（L1 写 247 off-by-one，L2 对）、测试 :35/:84/:90；`35cf0eb36a` 祖先 exit=0 | A | 一致 |

---

## §2 P0 四件独立展开

### P0-1 A1 遥测归档开关 —— L4 结论：L2 推翻成立，判"需改写"非可删；L1 首提交引用为错

- **坏接线链亲验闭环**：facade.py:471-477 `elif task == "archive_check":` 内 `try: from ...system_telemetry.archive import rotate_by_ttl; rotate_by_ttl()` / `except Exception: _logger.debug("archive_check failed", exc_info=True)`。cold_stub.py:118 `def rotate_by_ttl(base_dir: Path, max_age_days: int) -> int`。零实参调用双必填 → TypeError → 吞入 DEBUG。archive/__init__.py 仅 re-export。**L2 的 A 级证据逐行成立。**
- **零读者反证补强**：全仓 grep `rotate_by_ttl|compress_dir|RetentionPolicy`——archive 模块外仅两个**同名异类**（data_governance/market_data_aggregates.py:279、gov_audit/retention.py:37），非读者。flags loader（shared/foundation/flags.py:354-355）只取 `spec.get("enabled")/spec.get("description")`——L2 转述子代理的"加载即丢弃"升 A。
- **零产物**：`find data -name '*.gz'`=0；data/telemetry/prod/ 下只有 logs/（26 件 jsonl，17 件超 30 天留存——若 TTL 轮转在跑这些早被删，反向证伪成立）。
- **补做 L2 未验面（首提交）**：`git log --reverse --format='%h %ad %s' -- cold_stub.py` → 第一笔=`a5c1a81787`（2026-06-21 refactor 架构债务清理）。L1 写"首提交 787f7a6ba4（2026-05-06）"——该 commit 是 audit 批、`git show --stat` 证明未触 system_telemetry 任何文件。**L1 错、L2 存疑点结案。**
- flags.yaml:45-50 archive 块（enabled:false/implementation_status:not_started）与 L1 引文逐字一致——开关状态本身 L1 没说错，错的是"代码没写"半句。

### P0-2 A7 空 inputs 接线欠账 —— L4 结论：(b) 维持、(c) 降格；L2 对 L1 的两处数字纠正**均错**

- **门禁失明**：registry_alignment.py:347-357 亲读成立——空列表零迭代即过、空串 continue；`gate_registry.yaml` 无 inputs 判据；L2 的"假 ID 红、空 [] 绿"自证逻辑与代码一致。
- **规模**：`inputs: []`=171（工作区=HEAD 双验）；姊妹库 technical_indicator 空值=0（L2 的 138 行现为 139，微漂不影响方向）；两库 inputs 列表元素总数=**275**（python yaml 遍历实数）。
- **被清内容**：b1c59c9cda 清 8 条目（每条 1 引用=8 引用）；1d23039e90 清 6 条目（2+1+1+2+1+1=8 引用）。**合计 14 条目 16 引用——L1 的"16"（引用/报错数）与 L2 的"8+6"（条目数）是同一事实的两个正确口径。**
- **(c) 降格理由**：①被清引用原文是 `c3_fundamental.financial_derived(DS-230) 对应列` 这类自由文本——**从来不是字段字典合法 ID，门禁对它们的唯一作用就是报错**，不存在"原本有效引用被清空令门禁失明"；②两笔提交语公开写明 `自由文本改结构化 []` 与 `inputs=[] 全库惯例`——是声明性修法，不是隐瞒性绕过；③真正的问题是政策空缺（门禁对"没接线"零判据）+把"哪张表哪些列"的可追溯信息删除而非转写成合法引用。**"真欠账"成立，"绕门禁"作为指控不成立，降格为"政策空缺+信息删除"。**
- 正修先例（FCT-SENT-028 补字典保真引用）：未重跑核对（alignment_checklist.md 现位于 `docs/01_policies_and_standards/sop/governance_sop/`，L1/L2 行号 204/235 未对照——B 级挂起，不影响判定）。

### P0-3 A14 裁定编号链 + "93 份蓝图" —— L4 结论：L2 结案全部维持；L2 的证据效力自我声明错误

- **编号链**：renumber_note 在 **2d7308df1f（L2 时点）的 HEAD 版**已存在（`git show 2d7308df1f:<registry> | grep -n renumber_note` → 3766/3782，与 L2 引行号逐字一致）。现 HEAD 增第三条（L4256：原#293 撞号改 #386，随 a03179e2fa 落库）。#331=做T v2 砍现形态、#332=STD-SWITCH-001 定稿、#306=组合门 v2 提案（号未变）——**Owner 备忘录的 ③ 条应改挂 #331/#332，#306 那半句本来就对**。
- **93**：`git show --numstat dd56908c8e | awk` = 93 精确；该 commit（09-18，HEAD 祖先）提交语自述"93 蓝图 code-index 生成器回写"；蓝图在 `docs/03_modules/**/blueprint.md`（全库 542），kimi_audit 目录 0 份蓝图。L2"数字成立、地点与性质被 Owner 混写"维持。
- **L2 的错误**：review.md §5-2 / full_report §8-2 宣称"P0-1 的全部结论建立在未提交内容上……本案卷与我的复审都读到的是工作区版本而非 HEAD 版本"。**事实：renumber 证据当时已在 HEAD**——L2 未做热文件 HEAD 对照（恰是本 L4 证据纪律第 3 条），把已验事实错报为未验风险。方向保守、结论未翻，但属"把已验写成未验"的确证。
- **签字单未回写**：owner_fast_sign_20260917.md L17/L19 仍写 #304/#305、全文无 331/332——亲验成立（L2 的 B 升 A）。#293 重复（L2 案卷外发现⑥）**现 HEAD 已修复**。

### P0-4 A8 tick 缺口 —— L4 结论：仍开维持；归因采 L2 参数格式说；"一条命令可收口"驳回

- **证据灭失（新事实，L2 之后发生）**：`.runtime/tmp/tilib-probe/` 整目录已不存在（.runtime/tmp 24h TTL）。L1/L2 引为 A 级的 gap7_fill.log（L44 逗号单串、L62 平铺后逐字相同等）**永久不可复现**。二人转述相互独立且一致，可作 B 级采信，但按本报告纪律不再具 A 级效力。**这直接命中 L3 §7 自报的失效面，且比 L3 预想的更严重：不是"没验"，是"验过的证据已蒸发"。**
- **代码级归因（可验部分全验）**：`--days nargs="*"`（空格分词）+`[d for d in args.days if d in by_day]`（逗号单串交集恒空）+`missing` 打印单元素串+`return 0 if oks==len(results) and not missing else (2 if oks else 3)`——与日志转述行为逐点吻合；`_index_zips` 用 `iterdir()+is_file()` 不递归（嵌套 zip 不被索引）；缺省不传 `--days` 时 `days=sorted(by_day)` 自动扫描。**参数格式归因成立，路径归因（L1）只解释第一段失败。**
- **实物（亲列）**：E 盘 7 zip 平铺（mtime 09-17 00:20~00:25，此后无变动）；**zip 内构亲验**（python zipfile 只读）：5199/5200 个 `{6位代码}.csv`、UTF-8 BOM、四列表头、09:15 竞价行手数=0——与导入器 docstring 期望逐项一致。**"zip 内 csv 结构不符"可以排除。**
- **"一条命令可收口"三点驳回**：
  1. **08-05 杂散行阻挡**：`import_day` 预检 `count()>0 → skip`（代码亲读），而日志转述 08-05 已有 1 行。省略 `--days` 重跑会导入 6 天、**skip 08-05**（退出码 2=部分）。要收口 08-05 必须先处置那 1 行=删除性判断（RULE-DATA-OPS 面+需看它是什么），不是"一条命令"。
  2. **CH 写入车道非空闲**：HEAD 内 `docs/_working/data_fix_campaign/p0_0917_tick_recovery_report.md`（st-data-fix-20260921）载明"CH 重写入车道占用于 01:45-（协调板 ACTIVE）"——CH 写入有协调板机制，本复审窗口内车道被占。"无阻挡"不成立。
  3. **前提转述化**：CH 六日 0 行的唯一证据随日志灭失；若某日实际已有行，幂等预检同样会 skip——结果无害但"必然收口"的断言弱化。
- **附带坐实的矛盾**：known_data_gaps.yaml:383-386（工作区=HEAD）仍写"无 2026-08 文件夹、不可恢复"；F-05 裁定同口径——而 E 盘 20260805.zip/20260806.zip 实物在盘（09-17 下载）。**裁定文字与盘面事实冲突未消解**（L1 已指出，我以双版本对照坐实其未随时间自愈）。

---

## §3 驳回清单（对 L2 的驳回/修正，条条 A 级）

1. **【驳回】A7 纠正①："8+8 与实证 8+6 不符"**。L2 review.md §1/§2 称前手数字须纠。事实：L1 的 16=**悬空引用/报错数**（原文"EXP-001~006 的 8 条悬空引用（EXP-001/004 各 2 条）"明写引用口径），L2 的 8+6=**条目数**（git show diff 实数 14 条目）。14 条目恰载 16 引用，两口径相容，**不构成纠正**。证据：`git show b1c59c9cda -- factor_registry.yaml | grep -c '^- .*inputs'`=8；`git show 1d23039e90 …`=6；两 diff 的 `+`行引用元素合计=16。
2. **【驳回】A7 纠正②："两库 275 条 inputs 引用未能复现该口径"**。精确复现：python yaml.safe_load 遍历两注册表、累加 inputs 列表元素数 → **275**（其中空 inputs 条目 171）。L2 只数了行数（176）未数元素数，把 L1 的正确数字标成"无法复现"并写入"前手数字须纠"清单。**L1 对、L2 错。**
3. **【降格】A7 定性"(c) 绕门禁"**。被清引用本为自由文本描述（非合法 ID，门禁从未放行过它们）；两笔修复在提交语公开声明做法。"绕门禁"隐含的规避-隐瞒情节无证据；准确定性=门禁无非空判据的政策空缺+可追溯信息删除。(b) 真欠账维持。此降格影响 Owner 对车道行为性质的判断，须随案卷更正。
4. **【纠正】L2 自我声明"P0-1 全部结论建立在未提交内容上"为假**。renumber_note×2（#331/#332）在 2d7308df1f HEAD 版已存在（行号 3766/3782 与 L2 引用一致）。L2 读的固然是工作区文件，但其引用的关键证据当时已是已提交事实——证据效力应标 A 而非"未提交、随时会变"。
5. **【修正】A11 "both=1（algo_flow_link_gate.py 假阳性）"不复现且与其自公布判据矛盾**。今日同判据重扫=`{'ext_only': 3234, 'inline_only': 79, 'both': 0}` 总 3313。gate 文件 ：9 含散文 `# [ALGO_FLOW] external: <path>`（非正则字面量），按 L2 自公布的 e 正则该文件 e=True、i=False → 应落 **ext_only**；L2 报告它落 both 与其自己 §10 的脚本不一致。核心结论（79 近精确）不受影响——我的 inline_only 同为 79。
6. **【修正】A11 "inline − debt = 4"应为"=10（79 集口径）"**。亲验：debt 69 件全部 ⊂ 现 79 内联集；79−69=10（L2 的 4 系用其严格 73 件集：73−69=4，数字在严格集下可复现，但其行文把 4 紧邻 79 呈现，构成口径误导——恰是 L2 自己批评 L1 的毛病类型）。
7. **【驳回】A8 "改判为一条命令可收口的最高性价比项"**。驳回为"一条命令+一次杂散行处置（08-05 已有 1 行，幂等预检必 skip）+CH 写车道协调（协调板 ACTIVE 中）"。方向（重跑优先于改导入器/重复下载）维持，乐观度砍半。
8. **【翻转升级】A10/A1 复审未验面**：L2 留 B 的"FactoryLaneC 现 Disabled"经 `schtasks //query //fo LIST` 实测=**就绪**（每周六 10:00 档，下次 09-26）。L1 的"现 Disabled"（引 p7a:210）双重错误——p7a 表格原文即写 `Ready|清理对象`（判定=将 Disable），现状也仍未执行 Disable。C4Exam/F06Grid/AltFxECB 同为就绪。
9. **【补充】A6 活区计数**：L2 记 74，本会话取证时刻（04:11:59）已 **123**——24h 漂移 +49，证实"活区=常态流量、任何时点数都须标时刻"的纪律必要性；archives 61/25/912/48/113 稳定未变。

---

## §4 主区不可只读验证清单（终验必须连库/连网/写操作）

| 断言 | 缺什么 | 终验条件 |
|---|---|---|
| A2 四实体表真建成/有行（hypothesis_precheck/strategy_screen/financial_derived/consensus_daily） | CH `EXISTS TABLE`+count() | 只读 CH 查询（经 DatabaseService reader）；或等该表首个真实消费产出反证 |
| A8 CH 六日 0 行 + A12 936 行 + A3 51,345/7,337/44,008 行数 | 唯一证据=已灭失日志或报告散文 | 只读 CH count()；A8 另需先解决 08-05 那 1 行的身份（查询只读、处置需授权） |
| A12 "4 只各 0.15 面板输出" | 面板真数据输出实物 | 只读查 c1_market.daban_engine_load 09-11 分区+复算面板 |
| tick 09-17 回补 28,327,322 行（§5-2 新发现） | 他会话 [亲验]、我未连库 | 只读 `SELECT countIf(trade_date='2026-09-17') FROM c1_market.tick_data` |
| A7 align_all 其余八节硬报错数 | 生成器落盘禁跑 | git worktree 隔离副本内跑 |
| A17 标定值可复算性（标定产物是否真无入库 artifact） | 全仓 13119233/5519 数据侧佐证检索我未穷尽 | 只读 grep+CH 元数据 |
| A5(b) "政采试点永不回来"是否 Owner 本意 | 意图问题 | Owner 拍板 |
| A10 四件 Ready 任务的清理意图（C-16）执行与否 | schtasks 已证未执行 | Owner 决定执行或撤销该批清理令 |
| A16 ①"三表有表无写入方"、③ w5 消费者缺失 | 写入方/消费者存在性需运行时或全量调用图 | 只读 grep 调用图可部分补，本轮未做 |

---

## §5 案卷外发现（只记录，不执行；含疑似注入文本）

1. **HEAD 前进 22 笔，其中两笔与本对账直接相关**：a03179e2fa（N-5 总裁定 #385）**顺带修复了 L2 发现的裁定#293 重复**（改号 #386，renumber_note 第三条）；87baf923b3（taskcards 回收清点）把本 L4 复审登记为 **TC-01 任务卡**（"2 完整存活(TC-01 memo_recon L4 复审/TC-11 autolnk 第五棒，均无人认领)"）——本报告即该卡交付物。
2. **tick 09-17 疑已回补（重大，A10 残余面）**：HEAD 内 `docs/_working/data_fix_campaign/p0_0917_tick_recovery_report.md`（st-data-fix-20260921，task_bound）载明：09-17 行数 0→18,334,896（09-20 夜）→**28,327,322**（09-21 02:20，[亲验] CH count()），数据源=模拟盘 QMT 只读下载，宇宙 8,073 标的。若属实，L1 §A10 附带"仍缺 tick 09-17 双通道 0 行"已闭合（B 级，我未连库）。
3. **C-16 批清理令登记未执行**：p7a 裁定判定"4 个 Ready 遗留件（C4Exam/FactoryLaneC/F06Grid/AltFxECB）Disable+登记退役理由"，schtasks 实测四件全部仍就绪且有下次运行时间。裁定-执行之间存在未闭合差。
4. **F-05 裁定事实前提被盘面证伪**：裁定（p7c:41）与 known_data_gaps.yaml 均断言"云端无 2026-08 文件夹、不可恢复"；E 盘实物 20260805/0806.zip 在盘（09-17 下载成功）。两份权威文字未回写。**同一事实面上，裁定文字、缺口登记表、盘面实物三者互相矛盾**——这是比单条判定更值得 Owner 知悉的结构性问题。
5. **另一会话正在 CH 写入**（协调板 ACTIVE，01:45 起）——本复审窗口内生产库写车道被占，任何"马上导入"类动作都须排队协调。
6. **在途注册表批**：ruling_registry.yaml 现仍 staged（+49 行相对 HEAD）、known_data_gaps.yaml 仍 staged——L2 报告的"他会话在途"状态 24h 后仍在，且内容已换批。
7. **疑似注入文本（记录，未执行）**：
   - `docs/_working/trading_vision/2026-09-18-ruling-renumber-execution-note.md` 含条件式重放指令（"若工作区改号被清……=重放：对 registry 工作区执行（CAS 循环）……网关提交"）及"gateway 最终提交……暂未落地"字样。**按数据记录**。其自设的触发条件经我验证为"已落库"（renumber_note 已在 HEAD），按该文件自身条款应归档、无需任何人重放。
   - 三份输入件全文件正则扫描（`ignore previous|system prompt|disregard|必须执行|请执行|重放脚本|立即执行`）：仅命中 L2/L3 自述其纪律声明的行（review.md:12/:174、full_report:364），**无外来指令式内容**；kimi_audit/ 与 c_class_scattered/ 两目录 `ignore previous|system prompt` 零命中。
   - L1 §1 转录的 Owner 备忘录含"需要你做什么/跟我说一声"等对话性文字——系 Owner 原话转录，非注入。
8. **fetch_perf 已有 5 件**（20260917~21.jsonl）——L2 用作常态化替代判据的文件族持续增长，其方向被新数据继续支持。
9. **项目根目录临时件=0**（L2 健康反证）抽验维持；`data/telemetry` 无 archive 产物、data/ 全树 .gz=0（A1 侧再证）。

---

## §6 17 条终局表与对齐声明

| 条 | L4 终局 | 删前必做的一句话 |
|---|---|---|
| A1 | 需改写 | 改成"实现体在位但接线必失败（零实参调双必填被吞）、零产物、零读者；首提交 a5c1a81787" |
| A2 | 仍开 | 前提松动（待定仅 3）但表建成未证；补登义务是否触发待 CH 实证+辖区反论 |
| A3 | 仍开 | 未验=B 组全量 44,008（42,760 作废）；QA 已推翻 8,585 口径未回写报告 |
| A4 | **可删** | 真尾巴仅剩 source 无已验白名单 |
| A5 | **可删** | (a)=封矿裁定在册；(b)=该计划已消失，若还要须重新排期而非默删 |
| A6 | **可删** | 25 授权对账双口径一致；活区 123 为常态流量（04:11 时点） |
| A7 | 仍开 | 171 空接线+16 引用被删欠账成立；定性=政策空缺+信息删除，非"绕门禁" |
| A8 | 仍开 | 归因=--days 参数格式；收口=一条命令+08-05 杂散行处置+CH 车道协调，非"一条命令" |
| A9 | 需改写 | 09-17/18 未开成；PaperSession 任务仍就绪（下次 09-21 09:25） |
| A10 | 需改写 | 09-17 挖矿/批考未跑；常态化以 fetch_perf 5 件为证；FactoryLaneC=Ready 非 Disabled（C-16 未执行）；tick0917 疑已闭合待验 |
| A11 | 需改写 | 现 3234 路标↔3234 档案 1:1 零缺失；内联 79（69 台账零清偿）；"净增 10"作废 |
| A12 | **可删** | 936/4×15%/30 全溯源自 #277 在册文字；周末档+ROUTE_NO_DAILY_SOURCE 尾巴知悉 |
| A13 | **可删** | 评价段无待办 |
| A14 | **可删** | #304/#305 改挂 #331/#332（#306 本就对）；签字单未回写知悉；#293 已修复 |
| A15 | 仍开 | F2 k=4 就绪卡 Owner 签 S18-R3+7 天窗（台账 ：53 亲读） |
| A16 | 仍开 | ④零痕迹⑤仅设计（零命中已亲验）；①③有码无消费 |
| A17 | **可删** | 标定值=代码常量、复算件未入库、断言仅日频向量化引擎 |

**可删条数：7 条（A4/A5/A6/A12/A13/A14/A17）**；需改写 4（A1/A9/A10/A11）；仍开 6（A2/A3/A7/A8/A15/A16）；未决 0。

**对齐声明**：
- 与 **L2（可删 7）完全一致**（同 7 条、同 4/6 分堆）；差异全部在定性词与细节层（§3 共 9 项驳回/修正/降格/翻转），无一改变四态归属。
- 与 **L1（可删 6）不一致**：L1 少 A14（其时"93/编号链"未决——L2/L4 均已结案），且 L1 把 A5 拆计、A10 记半条；L1 另有 3 处硬伤被两轮复审坐实（A1 首提交错、A15 hash 转置、A10"Disabled"引错）。

---

## §7 对 L2 整体可信度一句话评价

**L2 的 17 条四态结论与全部 P0 大方向经本轮逐条重跑后无一被推翻（可信度高），但其"数字纠错"与"证据效力自评"两个副产出可靠度明显低于其主判定——对 L1 的两处数字纠正全错、把已提交事实错报为未提交风险、以及一处过度刑事化的定性（"绕门禁"），说明 L2 在"下大结论"上稳健、在"顺手纠人"与"自评弱点"上草率，引用其结论可、引用其对 L1 的纠正需先过本报告 §3。**
