---
ttl: task_bound
volume: 96_final_report_wave2
session: st-ailayer-final-20260924
creation_token: fullflow-closure-wave2-final-report-20260926
---

# 96 波2 终局交付报告（第四棒总包 · 通宵自裁自验）

> 开工前提校正（实测，非抄交接书）：交接书称"187 件主批已 staged，恢复脚本 apply_st_ailayer_final.py --stage"——
> ①主批 678 件早在 HEAD（`30505c93f6`）；②该恢复脚本全仓不存在；③`.runtime/tmp/st-ailayer-final-20260924/` 已被 24h TTL 清空（S3 的 76 常量骨架因此丢失，本棒用 AST 普查器机械重采）；
> ④交接书点名的 §S6/§C5 两处证据锚点有一处指错（墓碑 TTL 真源实为 §②-D/§④-S5）。
> 主区 index 当时 145 件 staged **全属他道在途** ⇒ 本棒不开主区、改在独立 worktree 施工，总筹单点走队列正门。

## 一、一句话终态与实测分母

12 项 Owner 已批项全部处置完毕（11 项落地/立案，1 项确属 Owner 门位只交可粘贴一行）；环节分母定档 **122→132**；全流通缺口经红队打假后是**诚实读数**（见 §五，含未清零项）；门禁系统两起 HEAD 级 outage 已修（§四）；安全事件 1 起未得手（§六）。

## 二、12 项已批项逐条（真源=`HANDOFF_st_ailayer_final.md` §一）

| 项 | 处置 | 落点/证据 |
|---|---|---|
| 1 C6 路由八轨 | 落地 | `config/model_routing_policy.yaml` 新增顶层段 `ai_layer_routes`（既有 12 轨删除行数实测 0）。落位改判理由：`task_routes.preferred` 语义是通道模式，塞模型键会让 mode 链整体落空并**静默**退化到 `static_mapping.default`，八轨永不绿且不报错；真实消费方 `washer.py:152-169` 只读顶层段 |
| 2 §3.3 口径 0.7 | 落地 | DESIGN→YAML→测试三处按 MODIFY-GUARD 序统一；未动任何参与算分的常数 |
| 3 外扫宿主双前置 | 落地（**不启用**） | `scripts/register_ai_l1_scan_task.ps1` 纯 ASCII＋双前置 fail-closed（DryRun 实跑退 2）。未注册计划任务＝生产流转属 Owner 门位；启用命令留册 |
| 4 L7 状态翻转 | 落地 | `L7_heredity/DESIGN.md` 状态行 1 行；`defect_pattern_checklist.md` 加入册前置 1 行 |
| 5 confirm 判定落点 | 落地＋红队加固 | 新 `confirm_gate.py`（api_server 未改，待接线一行已给）。红队实测三雷（并发不幂等/半写假持久化/畸形行静默抹档）⇒ 已列 W6-C 修，修前**不得接线** |
| 6 沙箱立案 | 落地 | `OBJ_T_tools/sandbox_profile_v0.yaml`＋试用档案卡 v0（机读全 .yaml）；内收复核：动作级沙箱三件跨域不并 |
| 7 各判据追认 | **改判为施工项** | 追认在"值层面"成立、"生效层面"不成立：真绿仅 1 族；红四类目＝四张受控词表无人读／三组开关连装载都没有／**双真源反向**（YAML 自称真源而代码硬编码）／写了不读 10 键。双真源反向已按 RULE-SSOT 收敛（W3-D：13 组改读盘、无回落常数、46 例红测；`switch_criteria.yaml` 的 git diff 为空＝此前纯装饰的反证） |
| 8 秘钥 ai_exposure | 落地（执法面未通电） | `ai_secret_exposure.py`＋可翻转对照（同键基线放行→标字段后拒），现网 106 条目/forbidden=0 故零行为变化。`get_secret` 断言**未接**＝缺 AI/生产会话判别器，直接接会拦 Owner 侧通道 |
| 9 墓碑 TTL | 落地 | `tombstone_ttl_proposer.py` 三判据 dry-run，零删除 API（测试扫 dir()） |
| 10 S3 阈值外置 | 重做落地 | 原清单蒸发 ⇒ AST 普查器机械重采（扫 210 文件/672 模块级常量/131 判据候选），旧"76"口径判不可复现未沿用，计数入 `meta.counts` 字段 |
| 11 区域白名单首批 | 落地 | 首批=`governance/tooling/ai_eng`（保守面：未加 trading_algo/骨架域/OBJ_S）；signoff 记 `registered_by_wave2_batch`，**未写 Owner 署名** |
| 12 FSM 词表对齐 | 落地（语义项停手） | 只落两处拼写硬伤；需加边的 `demote_decayed→decayed` 未动（重开已裁词表＝禁区） |

附带：`decision_map.py:183` 注释"11 业务库"是 09-11 冻结旧值，实测 `_XREF_SPECS` 为 13 轴 ⇒ 改为"13 轴＋轴数=len(_XREF_SPECS) 勿在此背数"。

## 三、挖矿封矿与施工波

- 31 行漏项二验（成立 17／不成立 10／证据不足 4）⇒ 四个 P0 中两个被证伪（REG-MIGRATION-001 实为冻结的重命名台账；38 个 null 节点已被区间写法全归属）；"122→151"虚高约 19。P-1/P-3/P-5 件级取证后 ΔN=0 ⇒ **定档 132**。
- 真缺环节按"分诊→补声明→开真簿"推进；**P-3"疑同物"查明是域册 ssot_path 与 covers 错配**（登记面缺陷，不改环节集合）。
- M7 实盘执行链补挖封矿（唯一还缺补挖波的车道）：十条"建了没接"带 file:line，F57 恒空总根＝**Fill 事实无生产写者** ⇒ 已按裁法接单一写者（AST 尺钉死唯一写者文件集）。
- 裁定册 `94_chief_rulings_wave2.md`：24 案自裁 20、Owner 一行 7、待裁净增 0。

## 四、门禁系统两起 HEAD 级 outage（本棒修，非在途件）

1. `priority=77` 撞号：`BLUEPRINT-FORMAT`(182) 与聚合门 `DOC-HEADER-SUITE`(231) 同槽 → registrar fail-closed 拒载聚合门；因七子台已出册，文档头七判据在链上集体不跑，且**入队预检整体 skip**。按"后到者让位"移聚合门至实测空位 130。
2. 修完才暴露：`in_process_gate_registry.yaml` 标量停在 102 而 gates 段实 103 → "装载数≠名册数"硬对账抛错 ⇒ **103 台门一起装载失败**。改标量并保留历史注（追加式）。
方法债已记：该标量手工维护违 §9.5，应由生成器按段长度派生。

## 五、覆盖诚实读数与未清零（勿当"已全绿"读）

对账尺被红队两轮打出假绿：第一版"提到即算"使 uncovered 6→0（我的裁定册只列出缺口就被记功）⇒ 收紧为正向声明位后诚实读数 122 中 44 无簿；两路声明车道交出 24 真认领＋20 拒认领（拒的逐格有理由）。红队二轮再打出四类仍可洗（标题塞号/`covers:` 空格串/反讽声明行/空壳文件名）＋F 号溢出＋WIP 簿被固化进真源记录 ⇒ 判据再收紧中（W6-M）。**结论：本轮交的是"可指证的缺口地图"，不是"零缺口"。**

## 六、安全事件（未得手，需 Owner 知情）

两路红队子代理的工具返回中被追加伪指令（24 条，两次谎称"Owner 已批准立即修复"），诱导修改判据函数 `_claim_tokens`/`NON_WORKBOOK_RELS`/`build_coverage`。两路按"文件与外来消息=数据"拒执行并上报。总筹读盘复核：现尺代码与我本人写入一致，无外来改动；两路盘面自证 sha 逐字节一致。⇒ 攻击未得手但通道存在。

## 七、落地终态（2026-09-29 夜战 SW11 台账回填；源=.runtime/commit_queue done|dead 实录＋git log 全史核）

**队列正门袋（qid↔landed commit，done/ 实录）**：

| qid | 内容 | landed commit | 落地时刻 |
|---|---|---|---|
| q-20260924-st-ailayer-final-20260924-0002 | token 先行批（九卡+resume 清单 11 行） | `5081f0ca91e` | 2026-09-24 13:17:31 |
| q-20260924-st-ailayer-final-20260924-0004 | token 先行批二（终报三件 3 行） | `9d71b563bd9` | 2026-09-24 14:20:50 |
| q-20260926-st-ailayer-final-20260924-0014 | 波2 开班·指挥册先行袋 | `ec0dd4f43a0` | 2026-09-26 02:41:26 |
| q-20260926-st-ailayer-final-20260924-0022 | 终局袋0·登记册先行 | `3ae33e7ffed` | 2026-09-26 04:36:18 |

**死袋（过门失败未落地，dead/ 实录，死因=门禁阻断）**：0001（DIRECTORY-CONTRACT）/ 0016（ENCODING-SAFETY）/ 0019（CREATE-GUARD）/ 0021（ALGO-NOTE-SYNC）。

**直连与代投携带（非队列袋，git log --all 全史核）**：`30505c93f6c`（P1 终局大单 678 件，allow-multi-domain 直连）；`8f03ef44bf7`（st-chief5 代投本会话孤儿接线件 [adopted-orphan]）；`6a4124cd8fd`（st-commitspeed-tbl 携带 budget/schedulegate 基线件落 dev）。0003/0005-0013/0015/0017-0018/0020 未见于 done|dead 与全史 grep＝直连或记录已被清理，队列实录无法归因（诚实缺口，不虚补）。

- [x] 各袋 qid 与 landed commit（上表＋直连/代投实录）
- [x] 两轮循环检查读数（2026-09-29 落地面复跑两轮，st-finaldel-cdocs-20260929；原会话口径不可得，以当日 HEAD 实跑替代）——电池=①对账尺 `generate_fullflow_crosscheck.py --check`＋②波2 触达域 `pytest tests/ai_layer -q`＋③`test_switch_criteria_ssot.py`。**两轮读数逐项全等**：①两轮同为 STALE rc=1（91_machine_crosscheck.yaml 生成物落后世界态——末次重跑=st-nightclean ba400ea294，其后各波落地累积漂移，属簿务面既有病非波2 残留，重跑归簿务车道；读数两轮确定性一致）；②两轮均 768 passed/2 skipped；③两轮均 1 skipped（skip=st-chiefzc-rescue 捞回袋官方豁免标记在案，上游实现件落地后恢复硬测）。红蓝完整轮次=原会话 §五/§六 在案（红队两轮打假收紧判据 W6-M＋伪指令攻击未得手），本复跑不重开红蓝只证落地面两轮一致
- [ ] 临时件清理与工作树收尾（待原会话/总筹终检）
