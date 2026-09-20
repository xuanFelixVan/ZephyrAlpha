---
ttl: task_bound
rule_form: data
verifiability: manual
title: P7-C 判定册——kimi_audit S3 E/F/G/H 四族 29 条 + 低置信 14 条逐条裁定（依裁定#371 代 Owner）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-20
status: final
session: st-maxexec-20260920
authorization: '裁定#371（final3 收尾全权执行令）'
---

# P7-C 判定册：E 族（9）+ F 族（12）+ G/H 族（8）+ 低置信 14 条

> 判定纪律：逐条复查证据后裁，禁照单全收。裁定形态四态：**a**=按草案/签字册建议通过；**改裁**=偏离草案建议（附依据）；**已执行追认**=事项已被在案裁定/施工落地，本册补认；执行指针=后续施工落点。证据等级：[亲验]=本班直查文件/git/注册表/进程；[转报]=引用草案与台账（未逐锚复验）。本册不写 ruling_registry（总包统一登记，见 §5）。
> 材料基线：签字册 `docs/_working/final3_campaign/w8_3_owner_signature_book.md` §主题一；源表 `docs/_working/kimi_audit/s3_pending_rulings_inventory.md`（2026-09-17）；草案 EF-族/G-01；复核基准 HEAD=23042a0497（2026-09-20）。

## 1. E 族：晋升·冻结区解锁（9 条）

| # | 裁定 | 依据 | 执行指针 |
|---|---|---|---|
| E-01 七份战役蓝图晋升 03_modules | **a 批准**（附红队修①） | [亲验] 7 蓝图仍全部在 `docs/_working/automation/campaign/blueprints/`（promotion_combo_gate/standards_lib/risk_redline/skeleton_health/intel_harvester/lane_g_stomach_intake/onboard_source），03_modules 无同名目录、grep 零命中——**未晋升**（07-15 后晋升批不含此批）；草案互证前提仍成立 | 晋升施工=git mv+depgraph --force；combo_gate 蓝图 [INVARIANTS] 头标注"尺子 STD-SIM-ACCESS-002 修订中，现数值以 standards.yaml 为准" |
| E-02 TableRegistry/表名入册 | **已执行追认** | [亲验] `business_data_categories.yaml` 现存 211 category_id、09-18 判定四表 TableRegistry 注册迁移已落（commit 37388478ae）；altdata D3/D6/D7 波次新表持续入册——入册通道活跃，机制已兑现 | 残余=nightbuild 后续新表随用随登（无专项）；e19bc24c 重 merge 的 TABLE-NAME-REGISTRY 硬拦随 CH-024 Phase 5 收口 |
| E-03 GPU-01/02 红线区+预测表 DDL+RL B-007 门 | **a 挂起维持** | [亲验] 前置 C-05（P-4 RL 选型）截至今日仍未落裁定号（registry #360-#376 无 C-05）；挂起理由（RL 执行链联动）未解除 | C-05 签发后自动回队；P-4 若裁不上则 B-007 门随之封存 |
| E-04 禁写区蓝图×2 晋升 | **a 批准** | [亲验] measure_calibration / resource_morning_report 两蓝图**尚不存在**（03_modules 无目录；验收证据原文"docs/03_modules/** 待建"）——是待建件非已建件 | 从 resource_schedule_v2 验收材料抽建蓝图入 03_modules（N-15 豁免留痕已有） |
| E-05 .trae/documents 181 份承源迁册 | **a 部分批准** | [亲验] `.trae/documents/` 现存 **181 份未迁移**（ls 实测）——迁移动作待执行；"可能已迁移"排除 | 承源迁移+归档；CloneGuard 蓝图（6 引擎表述）与架构图（mcrit L2 底座）同步勘误 |
| E-06 数据库 4 项"用户裁定"暂缓 | **a 不予解锁+补登裁定号** | [亲验] database/blueprint.md:109-120 四项仍标"2026-07-13 用户裁定"无裁定号（缺陷模式 #15 裸奔现状未变）；DuckDB 业务线已废，解锁=复活死路线 | 补登=总包 ruling_registry 一条追认号覆盖四项（Warm/Cold/Hot/Feature+Event），触发条件原文保留 |
| E-07 三条 akshare 采集链开窗 | **a 挂起维持** | [亲验] 三链仍 `enabled: false`（business_data_categories:874/890/906 现行 865-910 区段）；其 blueprint 指针指向已归档的 17 号文（design_memos 路径不存在、实体在 docs/_archive/）=悬空指针佐证可得性未证 | 数据窗申请须先补真源可达性证据+修 blueprint 指针 |
| E-08 REG-EXP-001 整表晋升真源 | **a 批准+顺带修计数** | [亲验] experiment_registry 实有 11 条目（EXP-REGIME-001..004/EXP-WALKFORD-001/EXP-FACTOR-EVAL-001..006）、表级 `status: draft`、master_index entry_count=0=计数滞后坐实 | registry 级 status draft→active；master_index 计数重生成 |
| E-09 裁定#1 因子 DSL 执行/废止 | **a 废止+触发复活条款** | [亲验] factor_registry 实测 **176** 条 factor_id < 500 触发线（头注"潘潘 546 条"为入库前计划口径非现状）；ruling#1 仍 status:draft | ruling#1 置 superseded/废止态+条款"因子数>500 达成时自动复活草案"（红队修③） |

## 2. F 族：数据可得性与外推授权（12 条）

| # | 裁定 | 依据 | 执行指针 |
|---|---|---|---|
| F-01 16 条 error 策略补考排期 | **改裁：解挂转"可排"** | [亲验] 挂起前提"market_commodity_futures_main 品类注册缺失"已修复——品类已注册 `enabled: true`（commit 9322ce6710，照生猪模式接入）；"等数据面修复"条件消失 | 并入 B-13 决赛前 backlog 排序面统排（不单独开跑，维持与 B 族分包的边界） |
| F-02 R-B 消融回放 §12 放行 | **a 批准（附条件）** | [亲验] triage :5——ablation.py 已施工（MATURITY=testing）但 sell_decision provider 零实现+回放受 §12 约束；放行令不即时生效 | 前置=sell provider 建成（PB-12 风控第二顺位）；届时按本批放行无需再签 |
| F-03 R-D 3 条 pending 行 superseded 机制 | **改裁：轻案** | [亲验] triage R-D 原案="保留不删+前端只按节点最新行渲染（工程 S）"；EF 草案"加 superseded 机制"重于原案且三行已被 09-14 风险口径行覆盖闭合（:39-41 已闭合） | 采渲染规避为正解；superseded 机制挂为升级路径（渲染规避不足再立）——最小 diff 纪律 |
| F-04 L3 快照源 A/B/C | **a 选 B 案确认** | [亲验] A 案依赖 MiniQmtBroker.get_positions()——miniQMT 9/18 退役（#339）后 A 死亡坐实；B 案施工清单仍有效；**WORK-ORDER-5 cohort_daily_ledger 不构成替代**（该账本=投资者行为五人群截面，非持仓快照源，正交关系） | recon_runner._compute_l3_pnl 实现成交反推+日志显式标注（B 案原清单） |
| F-05 bdpan 同步器重启 | **改裁：退役增量线** | [亲验] 重启前提已灭——云端归档源 7/3 16:24 停更后**无 2026-08 文件夹**（BaiduPCS-Go 实时列取在案），重启本地同步器无米下锅；6 日缺口已 accepted 终态；红队修②"并行重启"作废 | bdpan 增量线退役；import_bdpan_tick_zip.py 保留为幂等补货工具（源复活即用）；bdpan_tick_watch 看门狗转 monitoring |
| F-06 TradingWatchdog/RestartMiniQmt | **a 退役（已执行追认）** | [亲验] #339 miniQMT 9/18 退役+源切换三族裁决在册；resource_profile_registry `sch_trading_watchdog` status=**retired**（INT-03）；RestartMiniQmt 全仓零引用；S01 README 口径以退役向收口 | 残余=S01 README:54/66 欠账行回填"已裁退役"；ops_qmt_watchdog（QMT 桥线）保留 planned 不受影响 |
| F-07 TICK_SOURCE 桥降级纯后备 | **已执行追认（改向）** | [亲验] known_data_gaps:31——"9/18 起 TICK_SOURCE=bridge 桥模式"**已是主链**（#339 落地）；原问题"xtdata 主用后桥降后备"方向被 #339 反转 | 结案；防复发四件套之④的"待 Owner"回填"已随 #339 定为桥主线" |
| F-08 QUOTE_V17 并入 TICKDUMP3 v20 | **改裁：追认路径 B** | [亲验] 93 号 §14.9 Owner 09-07 已裁检查点机制，**默认=路径 B**（v17 过 9/18、合并推迟 10 月稳定期）；9/15 检查点已过且无 v20 施工实证（代码仍 v19+待并入注释）——EF 草案"批准并入"（=路径 A）与在案默认冲突，按禁照单全收原则不另开批文 | 10 月稳定期按 §14.9 原令执行 v20 对拍→退役 v17；期间 v17 继续服务 quote 族 |
| F-09 L1 必需传感器集定义 | **a 批准定义** | [转报+亲验] skeleton-coverage-audit Y3 现状仍"待 Owner 定必需传感器集"；草案定义与审计发现自洽 | 定义落 L1 DESIGN：日更必需=行情/指数/日历；可选=情绪/另类（消费方出现再升必需） |
| F-10 L4-#3 派考边契约对齐 | **a 批准** | [亲验] L4 DESIGN.md:140/190/211——同名冲突已拆分（回执改名 intake_exam_receipt），仅余派考边 `intake_exam_due`（L2→L4）跨稿确认挂"待 Owner-3" | L2 侧实施时事件表补列该边（payload={card_id, spec_ref, domain_id, mechanism_family, four_gates}） |
| F-11 L7 A/B 联赛 6 个月数据窗立项 | **改裁：立项维持+补迁移前置** | [亲验] **数据窗零积累实锤**：ZephyrAlpha_PaperSession 任务 09-17 已开闸（next run 9/21 就绪）但 paper_session.log 逐日 `SKIP: XtMiniQmt (57号 C1=Owner)`（09-17/09-18 连续，09-19/20 非交易日亦跳）——miniQMT 退役后无终端，模拟盘空转；EF 草案"现在立项越早越省"的隐含前提（数据在积累）不成立 | 补前置工单：模拟盘数据源 miniQMT→QMT 桥（sim 沙箱）迁移；**6 个月判定窗起点以迁移完成日记**，league 编排仍挂 L2/L1 落地后接 |
| F-12 模拟盘 A 阶段 2026-12-14 首评 | **a 维持原令** | [亲验] pending-owner-rulings.md 第 4 行原文"明令勿提前施工；sim_memo_monthly（MOD-BT-193）已按月产出建议书备料"现状未变 | 12 月首评以月度建议书为底稿，Owner 签字即评 |

## 3. G/H 族：方法论选型与机制澄清（8 条）

| # | 裁定 | 依据 | 执行指针 |
|---|---|---|---|
| G-01 _system_master 12 项待定 | **a=B 案（11 封挂+1 立案）** | [亲验] 蓝图 〇-B 12 项仍全部"设计决策待定"（:142-272 现状未翻）；堵点证据**更新且加重**：commit_block_events.jsonl 总 1487 行、09-16 以来 674 行（草案时点"295 次/24h"方向正确且持续）——#10/#11 例外项现实痛点更实 | 蓝图状态行改"挂起（触发：并发会话常态>20 或脚本>5000 再启）"；#10+#11 合并立案"现状并发（≤10）提交链锁/写瓶颈治本" |
| G-02 G07 判 COMBINATION_INVALID 后三件 | **a 按案通过** | [亲验] sentiment_cycle blueprint 仍"MATURITY=new 待 G07 验证、本注册不改变 L2-05 挂起状态"——三件处置现状未翻，无后裁覆盖 | ①TDM-E-L2-05 维持红节点 pending_gate；②G13 情绪暴露硬上限按 0.3-0.6 保守档；③定位器增"回放/打标模式"语义（28 号备忘录补条目） |
| G-03 belt daemon 治本 A/B（#ARCH-324） | **已执行追认（A 案）** | [亲验] **lock mtime 实测=2026-09-20 12:50:43**——按取证逻辑（re-exec 重取锁必刷 mtime、不动即未重启）旧码常驻进程（PID 28648/09-16 源码纪元）已被重拉，#ARCH-324"旧码盲区"前提消失；registry status 仍 open | 注册表收口：#ARCH-324 按本案实态 close（附 lock mtime 证据）；残余=头注 stop 模式清偿+B 案留下一版结构方案（不排期） |
| G-04 AI 资产盘点 7 问+Q10 快照 | **a 随草稿区清理（已执行大半）** | [亲验] Q10 依赖图快照两文件**已删**（.runtime/aidrafts/09_drafts_audit/依赖图/仅剩空目录）；7 开放问多数已被后续战役消解（Q4→D-01 三档、Q5→宪法 v2"计数用字段不背数"、Q9→D-11 联动） | 空目录顺手删；02_design_asset_inventory Q 表追加处置注记（不重开问） |
| G-05 #ARCH-314 dataflowgraph 分层排期 | **a 暂不排期** | [亲验] registry 仍 `status: proposed`、fix_phase=待 Owner 排期（依赖 CAND-CRYPTO-009 等 dataflow 车道窗）——无新消费方，维持 | 触发=dataflow 车道施工窗出现再立项 |
| H-01 取证期"冻结一切轮转"（26,909 HMAC） | **已执行追认+判解除** | [亲验] 冻结的技术前置 **C-2 已落地**：log_rotation.py:49-61 `_append_lock_for` 复用 `_cross_process_append_lock` 且 :156 接入 rotate（"解冻轮转前置"原文满足）；#266/#267 已把 26,909 判 known_loss 永久不可验证+era 钥部署；取证窗口 09-16/17 已闭 | 判：解除冻结、恢复常态轮转；C-3（长驻写方滚动重启）随 #267 的 14 天过渡窗自然消化 |
| H-02 撞号 #264 vs #266 合法性 | **已执行追认（改向）** | [亲验] 三条原文对读：**#264=WYF-3 wyckoff 阈值重校**（active、superseded_by=null）、**#265=空号 tombstone**（void、编号让位留痕）、**#266=审计链互踩治本**（active）——撞号已于 09-16 经改号机制机械消解，双条内容互异各归其位；签字册 a 案"认 #266 为准+回写引用面"的**排他前提不成立**（非同内容竞争，无需二选一） | 判：维持现状（#264/#266 均合法有效、#265 空号保留）；forensics §8.5"Owner 门位认定"以本裁定回填结案；无需回写引用面（无错引实据） |
| H-03 PGP 签名人工执行边界 | **a 保持人工 PGP+周期抽审** | [转报] 常设门位与待裁项边界澄清：~60 处"需 Owner 审批"登记为常设约束非待裁项；known_good_hashes PGP 签名保持人工（安全面单点），周期抽审作质量兜底 | 无施工件；D-01 三档若落地，此类 tier0 常设行不属"派生行全自动"射程 |

## 4. 低置信 14 条两态判定（清单 §10）

> 两态：**升格入册**=本册给出实体裁定（总包可据此登记）；**维持低置信不动**=不裁（附去向）。

| # | 条目 | 判定 | 依据与去向 |
|---|---|---|---|
| 1 | stash_notice 三次未留 notice | **维持不动** | [亲验] `.runtime/workspace_alerts/stash_notice.json` 现存且含 09-16/17 两条合规记录（skeletonaudit/auction-bridge 会话）——异常未复现，机制在案；运维派工排查撤销 |
| 2 | 面板 API 8890 旧实例 wedge | **维持不动** | [亲验+转报] 已被主题五方案 B 吸收（#374③：壳托管，ensureApi 含端口僵尸占口修复弹窗）；8890 当前无监听 |
| 3 | L1 外扫=日历节拍需 Owner 追认 | **升格入册** | [亲验] 判：**不构成宪法 §9.3 违规**——§9.3 射程=reconciler 写回/修复回路；L1 外扫=只读感知采集，与 tasks.yaml 日历采集同族不同物；E0 实闸保事件触发收敛。撤"Owner 追认"前置，限定 L1 施工项 7、禁外推；裁定登记随总包 |
| 4 | 组合层现金权重（疑已决 #270） | **升格入册** | [亲验] **#270 原文确认**："双轨披露制（默认满仓+opt-in 节流）……一律落现金禁再归一化回填（现金语义与 T1A-5 合并）"——允许现金且禁归一化回填；文档同步（decision_kernel_mining.md:134 一行注记）为施工小件 |
| 5 | alpha 增量车道立项排序 | **维持不动** | [转报] 并入 B-13 决赛前 15 条 backlog 排序面（B 族分包处理），不单独消耗决策点 |
| 6 | F06Grid/C4Exam 周六 14:00 双活 | **维持不动** | [转报] 并入 C-16 一次性/遗留计划任务清理批（C4Exam 遗留任务在 C-16 清单内），错窗方向随清理自然消解 |
| 7 | CH-OptimizeMerge ps1 化+任务名规范化 | **升格入册（已执行追认）** | [亲验] CAMPAIGN_LEDGER H-05 原文"Owner 已批待安全窗"——批文在案；执行挂值守安全窗（改活任务），不动 |
| 8 | WeeklyRest 周日休息窗点头 | **升格入册（已执行追认）** | [亲验] `ZephyrAlpha_WeeklyRest` 计划任务**在飞**（next run 2026-09-27 05:00 就绪）——Owner 点头已生效落地；首次周日窗执行后按 04:00 关机/09:00 开机口径复验一次 |
| 9 | 外网论文/策略搜索 agent 启用 | **维持不动** | [转报] 外呼边界涉安全面；内收判据：无急迫消费方，默认不启用；出现明确研究消费方再呈签 |
| 10 | kline_etf_60min 回补工单批否 | **维持不动** | [亲验] gap 条目 status=monitoring、工单在数据线在途（通道 C=CH 内 1min 合成零外呼+兜底 D=大 QMT 沙箱，~9 万 bar）——工单已有评估序，无需 Owner 再批 |
| 11 | sector_constituent 8803/8804 82% 覆盖 | **升格入册** | [亲验] 判：**接受 82% 现状**——881 体系已覆盖逆势榜行业决策面、8803/8804 无消费方（内收判据：无消费方不挖矿）；resolution_plan 改"出现消费方再启 TDX 成分源挖矿" |
| 12 | Embargo BDay 换真交易日历 | **升格入册** | [亲验] 随 **#376·ARCH-346"LdP 语义统一默认值（embargo 缺省≠0，按事件窗默认）"**方向连带：真源交易日历化（接 hk_trade_calendar 同族）作为其实现件落地，不单独立号 |
| 13 | legacy-clear 五件（门禁松紧族） | **升格入册** | [转报] 批：整族并入 **D-01 三档门位口径**一次批掉（对齐签字册 D-01 a 案设计：净删=Owner 常设/tier0 新增改=提案登记/派生行全自动）——五件（pytest_cache 根治/.openclaw ACL/R21 死批归一/allow-mass-deletion 中文阈值/CloneGuard ast_grep+SCHEMA-FILE-EXISTS）按档归位；总包若对 D-01 另裁，本条随改 |
| 14 | c1_market_clickhouse 蓝图内部矛盾 | **升格入册** | [亲验] 判：**以可执行为准**——实态=ReplacingMergeTree 无版本列、无 ingest_ts（§4.0/§4.2 勘误为注记，与 :363-365 HTML 注释一致）；§9.1/§10 两处"待对齐·人工核对"随依赖图重生成机械对齐，不逐项人工 |

## 5. 计数汇总与登记移交

**主 29 条裁定形态分布**：

| 形态 | 条数 | 条目 |
|---|---|---|
| a（按草案/建议通过） | 17 | E-01/03/04/05/06/07/08/09、F-02/04/09/10/12、G-01/02/05、H-03 |
| 改裁 | 5 | F-01（解挂转可排）、F-03（轻案）、F-05（退役增量线）、F-08（追认路径 B）、F-11（补迁移前置） |
| 已执行追认 | 7 | E-02（入册通道活跃）、F-06（退役向）、F-07（桥=主线）、G-03（A 案已发生）、G-04（快照已清）、H-01（冻结解除）、H-02（改号消解） |

**低置信 14 条两态分布**：升格入册 **8**（#3 现金外扫非违规/#4 现金权重已决 #270/#7 CH-OptimizeMerge 已批/#8 WeeklyRest 已落地/#11 接受 82%/#12 随 #376-346/#13 并入 D-01/#14 以可执行为准）；维持低置信不动 **6**（#1/#2/#5/#6/#9/#10，均附去向）。

**依据构成**：主 29 条中 [亲验] 26 条、[转报] 3 条（F-09 定义细节/H-03/其余引用草案行）；低置信 14 条中 [亲验] 9 条、[转报] 5 条。

**深复核红证（本册抽查样本，供总包验收）**：
1. **F-11 paper_session.log 逐行实读**——任务 09-17 开闸但 09-17/18 连续 `SKIP: XtMiniQmt (57号 C1=Owner)`，6 个月判定窗零积累；推翻 EF 草案"现在立项、数据积累越早越省"的隐含前提（其假定积累在进行中）。
2. **H-01 解冻前置 C-2 代码实读**——log_rotation.py:49-61 `_append_lock_for` 复用 writer `_cross_process_append_lock`、:156 接入 rotate 路径；era 部署报告 §5 原文标 C-2 为"解冻轮转前置"——前置已满足，冻结应解除。
3. **H-02 三条裁定原文对读**——#264（WYF-3 wyckoff 内容，active）/ #265（void 空号 tombstone）/ #266（审计链治本，active）：撞号已机械消解、内容互异；签字册 a 案"认 #266 为准+回写引用面"的排他前提不成立，改判维持现状。
4. **G-03 lock mtime 实测**——belt_daemon.lock mtime=2026-09-20 12:50:43，按 #ARCH-324 自身取证逻辑（mtime 移动=进程重取锁=新代码纪元）旧码常驻前提消失。
5. **E-09 触发线实测**——factor_registry 176 条 factor_id < 500；"潘潘 546 条"为头注计划口径非现状。
6. **F-05 重启前提实测**——云端 7/3 16:24 停更后无 2026-08 文件夹（known_data_gaps 云端取证原文），重启本地同步器无米下锅。

**登记移交（总包统一执行，本册不写 ruling_registry）**：
- 建议登记号覆盖：E-06 补登（四项数据库暂缓追认）、E-09 废止+复活条款、低置信 #3（§9.3 射程解释）、#4（#270 已决确认）、#11（82% 接受）、#13（并入 D-01 条款）、#14（以可执行为准）——共 7 个实体裁定点；其余为状态收口/追认（随各自执行指针落施工，不占号）。
- 需回写的在案状态：#ARCH-324 close（G-03）、#ARCH-314 维持 proposed（G-05）、s3_pending_rulings_inventory §13 处置列回填（E/F/G/H 29 条+低置信 14 条）。
- 与他包边界：F-01 归 B-13 排序面、低置信 #5 归 B 族、#6 归 C-16、#13 归 D-01、E-03 挂 C-05——总包归并时按此去重，勿双裁。

## 6. 未完成项与原因

无整项未完成。本册为判定册（裁定+轻量证据复核），不执行施工（按任务边界）；以下施工件留执行指针待总包排班：E-01/E-04 晋升 git mv、E-05 181 份迁移、E-08 计数重生成、F-04 B 案实现、F-11 模拟盘数据源迁移工单、G-01 蓝图状态行改挂、G-03 #ARCH-324 close、F-06/H-01/H-02 各回写注记。以上均已在各表"执行指针"列落锚。

---

汇编：st-maxexec-20260920 P7-C 分包｜2026-09-20｜授权=裁定#371｜复核基准 HEAD 23042a0497｜本册判定不写 ruling_registry（总包统一登记）。
