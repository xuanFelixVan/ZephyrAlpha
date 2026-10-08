---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/env_mining/env_18_sysops.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# ENV-18 系统运维七族 挖矿作业簿（B1 批次，2026-10-06）

## §0 环节档案
- 锚件：config/governance_operations_map.yaml（GOMAP-001，generated_at 2026-10-04，机生器=scripts/governance/generate_governance_map.py）。
- counts（map 自带✓）：total_modules 450＝wired 246＋wired_dynamic 15＋wired_by_header 95＋suspect_orphans 94＋untagged 0（核算 246+15+95+94=450✓）。
- 七族切片核数：L0_lifecycle 77／L1_monitor 141／L2_resource 66／L3_fuse 22／L4_reap 42／L5_selfheal 98／L6_audit 4，合计 450✓（族内计 22+66+98+42+141+77+4=450✓）。
- wiring 判据（generate_governance_map.py:28-31/287-428）：AST import 边四档——wired=静态 import 实锚／wired_dynamic=importlib 字符串解析／wired_by_header=仅 [CONSUMERS] 头声明非空（不辨语义）／suspect_orphan=无任何消费证据。

## §1 六向台账（向/内部反查发现带路径/外部/判定）
| 向 | 内部反查发现（带路径） | 外部 | 判定 |
|---|---|---|---|
| 94 orphans 按族分布 | L0=25(32%)／L1=21(15%)／L2=25(38%)／L3=3(14%)／L4=10(24%)／L5=10(10%)／L6=0(0%)——重灾=L2_resource 与 L0_lifecycle，L6_audit 零孤儿 | — | 分布已核✅ |
| 94 按路径簇 | src 60／scripts 34；src 内簇：zephyr/feedback_loop **21**、infrastructure 13、orchestrator 11、governance 5、autonomy_core 4；scripts 内簇：governance **30**、ops 2、arch_guard 1、根 1——三簇（FBL 工具族/repair 脚本族/orchestrator 族）占大头 | — | 集中可归口✅ |
| 假阳性类 | **__init__.py×8**（L0×5＋L1×1＋L2×2：governance/infrastructure/orchestrator/shared/lifecycle_governance 与 validators/lifecycle 等包标记文件——import 机制天然接线，AST 文件级边判不出来）；**元孤儿**：scripts/governance/check_wiring_orphan.py 自身入册（L4_reap，tag=orphan_claim——查孤儿者自己是孤儿）；scripts/fix_orphan_all.py 亦在册 | — | ≥10 件假阳性/自指🌑 |
| 脏值面 | domain="#"×1（scripts/governance/repair/concurrent_write_test.py）＋空 domain 8 件＋maturity 空 13 件（含 __init__ 与 repair/apply_verification_results.py 等）；94 件 consumers_count 全=0（判定构造使然，非独立信息） | — | 数据质量小疤🔨 |
| purpose_tag 构成 | resource_alert 25／birth_registry 25／alive_proof 21／self_heal 10／reaper_duty 10／orphan_claim 8／emergency_brake 3——L0 孤儿全为 birth_registry（出生登记器无人登记它）、L1 全为 alive_proof（存活证明器自身无存活证明），语义自反集中 | — | 自反工具族是主构成✅ |
| 判据边界与消费面 | wired_by_header 95 件仅凭头声明（不辨语义）入 wired；map facts_sources 七源（commit_queue_ledger/runtime_audit/gate_audit/lookup_audit/drift_watchdog/reconcile_reports/reaper_last_run）在册；GOMAP 消费方=dashboard api_server 与 align_all/generate_panorama_registry 等生成链 | — | 判据已知保守🔬 |

## §2 挖干自评
- 已挖干：94 件逐条全量切片（非抽样）出族/路径/maturity/domain/purpose_tag 五维分布；识别两类系统性假阳性（__init__.py 包标记×8、自指件×2）；定位重灾三簇（feedback_loop 21、scripts/governance 30、orchestrator 11）并给出语义解释（自反工具族：出生登记器/存活证明器/错误预算器无人消费）。
- 未挖透（点名留档）：FBL 21 件逐件归口判定（该杀该接该升 wired_dynamic）未做——须 B2 车道逐件三问；orchestrator 11 件是否属「事件入口未挂接」类（同 ENV-16 BRK-016 形态）未逐件验证；wired_by_header 95 件中否定式头的漏网率未抽测。

## §3 挖后自审闸三态裁定
- **裁定：施工**（范围限机生器小改，不触业务件）。
- 理由与范围：①generate_governance_map.py 加 __init__.py 处置（包级聚合或单列 wiring 档），消 8 件包标记假阳性；②脏值清洗（domain "#"→正域、空 domain/maturity 补齐或显式 unclassified）；③check_wiring_orphan.py/fix_orphan_all.py 自指标注（工具自身豁免或标 self_wired）。三项都是生成器内改，零 Owner 门、零注册表净删，工程量小时级；再生成即生效，后续 orphan 数字才可信（否则 94 永远虚高 ≥10）。
- 簇归口随行：FBL 21 件簇＋orchestrator 11 件簇的真孤儿判定**挂起排期**随 b0 AM-13（监控·衰减·退役）车道；L3_fuse 3 件（kill_switch 三件套：check_kill_switch_latency/manage_kill_switch/kill_switch_sim）建议优先人工核——熔断件零消费证据是七族里唯一安全敏感项。
- 解锁条件：施工件随下次 GOMAP 再生成窗口（align_all 批）落地即解锁；簇归口解锁=b2 AM-13 车道开工。

## §4 挖矿日志
- R1（全量切片）：python 解析 families 七族 450 件，按 wiring 四档核对 counts 六字段全符；94 件五维分布一次出（族/顶层目录/子簇/maturity/domain/purpose_tag），假阳性两类当场浮出。
- R2（判据反查）：读 generate_governance_map.py:28-31/287-428 wiring 四档判据与 654 行 orphans 导出函数；grep governance_operations_map 消费方（api_server/align_all 等）——确认 map 本体有消费、94 件是真「无消费证据」而非 map 无人在读；脏值清单（#/空 domain×8/空 maturity×13）逐件点名留档。
