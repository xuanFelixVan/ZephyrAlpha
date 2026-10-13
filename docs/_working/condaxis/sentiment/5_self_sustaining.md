---
ttl: task_bound
title: 自维持回路环节册——日批/周批裁判/月批呈批的触发-动作-权限表落点
created: '2026-10-13'
session: st-condaxis-20261013
status: mining_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: 自维持回路环节施工完成且随 CONDAXIS-CAMPAIGN 归档
---

# 自维持回路环节册（合宪法永久系统四要素：自动触发/自动运行/自动维护/自动关闭）

> 契约定位（研究档 §14）：AI 自发回测→修正，每天给"诚实＋判据达标"的情绪。三节拍=日批（数据到达事件触发，**禁 cron/sleep-loop**）/周批裁判（三判据滚动重算→资格灯）/月批呈批（红灯触发的语义修正提案包）。
> 防过拟合铁律：修正由红灯触发，不由日历触发；**禁止每天看数每天调**。

## §1 逐项台账表

| 件名 | 仓内真源路径:行号 | 现状 | 消费方 | 缺口 | 六向定位 |
|---|---|---|---|---|---|
| 日批触发：数据到达事件门 | **已有在产事件链**：daily_kline SUCCESS → maybe_emit_sim_daily 追发 t0_condition_pack_due → run_optional_due 派发（t0_condition_pack.py:32-41，"与 emotion_index 同一事件门驱动"）；emotion_index 落表=调度器写通道单写（builder INVARIANTS :8-9）经 internal_compute_provider:766-767 capability 路由 | ✅（事件门在产） | emotion_index 日批、t0 三步串行（anchored_state→six_phase→condition_pack） | 三缺日告警面（09-25/29/30 类缺日的 detection 落 catchup_guard 同款）——复用 weekend_calibration 7 日无 SUCCESS→overdue 模式（gap_list:114"监控=既有 catchup_guard，零新增件"） | ①daily_kline ②日批执行体 ③事件驱动（非 cron） ④在产 ⑤— ⑥— |
| 日批动作：算温度→落表→诚实快照 | builder（纯计算）+调度器写通道+scripts/data/emotion_index_snapshot.py（append-only 全表镜像 gzip JSONL+manifest.jsonl；PIT 读径 pit_state_path；空表拒出快照） | ✅（快照器在册，"create-guard-not-dup"） | 未来 PIT 读径/考试审计 | 快照器 STARTUP=manual（头部"手工/日批 CLI"）——**从手工挂上事件门**是本环节主施工点（reaper 白名单登记由运维面负责，头部自记） | ①emotion_index 表 ②PIT 证据面 ③append-only 铁律 ④挂事件门 ⑤— ⑥8 列原样镜像 |
| 日批动作：当日诚实快照字段 | builder ERROR_CONTRACT（:17-18 单成分 insufficient/missing 降级不出行错；全成分不可产→None 禁拍假值）+components JSON 逐成分 status | ✅（机制在产） | 4_validation 判据分母、dashboard | 诚实快照汇总面（完整度/降级/判据分母剔除项的当日一行台账）——建议快照 manifest 扩列，禁新表 | ①六成分 status ②判据分母 ③insufficient 纪律 ④扩 manifest ⑤dashboard 候选 ⑥— |
| 周批裁判：三判据滚动重算 | 判据件=4_validation §1（Brier/单调性/命中率）；裁判节拍先例=weekend_calibration 系（catchup_guard/backfill_checker/integrity_checker/quality_sentinel/scheduler.py 监控族） | 🔨（判据件待 P2，节拍先例在） | 资格灯 | 判据规格未冻结（Q4 绑 P2）；周批事件的事件门挂位（建议=daily_kline 周末日 SUCCESS 后派生，禁 Timer） | ①判据输入 ②资格灯 ③滚动窗 ④待建 ⑤— ⑥— |
| 资格灯：写位+红灯动作 | 字面先例=gpu_core.py/gov_audit/models.py/frontend_truth_source_gate.py | ✅（先例族） | 消费面（预算带/条件轴/拐点确认器读数开关） | 写位未定（候选=独立判据台账表或 emotion_index status 扩展）；红灯=自动降权/停用 fail-closed（保守方向，medium/low 全自动合规——宪法 §5） | ①三判据输出 ②消费面开关 ③红=停用 ④待建 ⑤灯面 ⑥— |
| 月批呈批：语义修正提案包 | 预注册协议先例=regime_recal_protocol（预注册→跑数→验收→落版本；run_id 钉法 §2）+D 族冻结稿 :46（季度 walk-forward 同款） | ✅（协议先例在册） | Owner 裁决（人机门位） | 情绪线提案包模板（假设→判据→跑数结果→建议+契约红线：成分变更 minor/权重 major）未立——随 P2 同批钉死（Q13） | ①红灯触发记录 ②Owner 呈批 ③预注册协议 ④模板件 ⑤— ⑥— |
| 判死要素：连续 N 周红灯→降级 | 4_validation §3-6（灯位与消费开关同批）；先例=qual 资格灯族 | ⬜（规格待 P2） | 消费面 | "仅记录不消费"降级态的机械参数（N 周）未钉——Q13 权限表同批 | ①灯史 ②消费开关 ③自动关闭 ④待建 ⑤— ⑥— |

## §2 触发-动作-权限表（研究档 §14 落位版；Q13 草案，P2 冻结时钉死）

| 节拍 | 触发（事件门，禁 cron） | 动作 | 权限 |
|---|---|---|---|
| 日批 | daily_kline SUCCESS（既有门，t0_condition_pack.py:34 同源） | 算温度（builder）→落表（调度器写通道）→快照器自动跑（append-only）→诚实快照一行（完整度/降级/分母剔除） | 全自动（AI 自修面=机械参数） |
| 周批裁判 | 周末日 daily_kline SUCCESS 派生事件（或 catchup_guard 同款 overdue 反向触发） | 三判据滚动窗重算→绿/黄/红资格灯落台账→红=消费面自动降权/停用 | 全自动（含自动退出消费面；判据参数本身禁当日改） |
| 月批呈批 | **红灯触发**（非月历审视主动项；月历只做兜底巡检记录） | 语义参数修正预注册提案包（假设→判据→跑数→建议）→Owner 批后升版本（minor/major 契约红线） | AI 提案、Owner 裁（宪法 §5 人机门位） |
| 判死 | 连续 N 周红灯且无修正获批 | 自动降级"仅记录不消费" | 全自动（永久系统四要素之自动关闭） |

**修正权限分离表**（机械 vs 语义，防"AI 自己改判据"）：

| 类 | 项 | 权限 |
|---|---|---|
| 机械参数 | 分位窗宽（250 观测）/as-of 对齐偏移/数据源切换/断供补洞重放/缺日补齐/快照运维 | AI 自修留痕（git 台账+快照 manifest） |
| 语义参数 | 成分增删（minor）/权重方案（major）/事件阈值与触发条件/词表映射（含 A3 proposed 校准）/判据及格线与滚动窗规格 | Owner 门位（预注册提案包呈批） |

## §3 施工要点（实读代码的坑）

1. **事件门复用禁新开**：emotion_index 日批与 t0 三步**同一事件门**（daily_kline SUCCESS）已在案——施工禁为情绪线另开触发器（违"reconciler 事件触发，禁 cron/Timer/sleep-loop"红线；两门并存=双写竞速）。
2. **快照器挂门顺序**：必须在落表成功**之后**（快照的是落表后状态；空表拒出快照=证据污染防护在册）——挂门时 FIFO 顺序排在 t0 三步同队列或其后，禁抢跑。
3. **reaper 白名单**：快照器头部自记"日批在每日收盘数据 ingest 之后跑一次（reaper 白名单登记由运维面负责）"——长批任务先登记 `data/runtime/process_reaper_keep.txt`（宪法 §0 RULE-GUARDIAN）防误杀。
4. **诚实快照禁新表**：完整度/降级汇总沿 manifest.jsonl 扩列（append-only 同款），开新表面=违反净零（新表须声明替代件）。
5. **周批禁日频化**：三判据滚动重算只在周批事件跑——日批禁触发判据重算（防过拟合铁律的机械落实：判据计算频率本身是判据规格的一部分，P2 冻结项）。
6. **红灯动作方向=保守 fail-closed**：红→降权/停用（向"不消费"方向），禁红→改读数/换公式自救——与 R-055a"缺数落地板值禁把降级读作确无风险"同精神（TDM:400 在册表述）。
7. **月批提案包的 run_id 钉法**：沿 regime_recal_protocol §2 先例（run_id='VAL-P0-…'式），包内跑数结果引用闭卷窗纪律——提案包本身 append-only。

## §4 自审闸三态裁定

**裁定=施工（分两半）**：
- **日批半（挂门+诚实快照）=立即施工**：事件门/快照器/降级机制全部 ✅ 在产，施工量=快照器从 manual 挂上事件门+manifest 扩列——零新逻辑纯接线，直接消灭"手工跑快照"人工环节（终局全貌一票放行）。
- **周批/月批半=挂起排期（解锁条件=P2 判据冻结+Q13 权限表批准）**：判据件本身在 4_validation 挂起中，裁判节拍随之；但**周批事件门挂位与资格灯写位的工程设计先行**（本册 §1 已留位），P2 冻结后即插即用。
- 反驳者一问：①"日批已全自动，周批是否过度？"——否：三判据是契约存活条件（研究档 §13.4），无裁判=废物读数无退出机制，终局必需；②"月批呈批是否 Owner 负担？"——红灯触发制（非月历主动项）保证空窗期零打扰，Owner 只在被红灯召唤时出场——与终局全貌"Owner 只做四类事"兼容（语义修正=策略转正审批的同族门位）。
- 封矿面：无。
