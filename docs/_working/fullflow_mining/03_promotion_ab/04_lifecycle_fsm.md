---
ttl: task_bound
volume: 04_lifecycle_fsm
session: st-ailayer-fullflow-pr-b
creation_token: fullflow-prb-f75-fsm-20260925
---

# 04 · F75 策略生命周期状态机（lifecycle FSM）

## 一、环节定义与边界

总册口径：F75=策略生命周期状态机（lifecycle FSM/上架入库/晋升建议/事件流），真源=src/zephyr/strategy_pipeline/lifecycle_fsm.py、intake.py、registry_writer.py、screen_source.py，状态 **partial**，挂 REG-STR-001。本册实证后维持 **partial**，但缺口重新定位：状态机本体（五态七边+双 guard+fail-closed 测试）**已建成且合格**；partial 的真缺口在**词表对齐层与骨架 §6 生命周期轴的未覆盖段**（§四/§五）。上游 F23-F27（策略工厂）产出经 intake 进 candidate；转正/降档流转由 F74 拍板执行器驱动（姊妹册 03_promotion_gate.md）。

## 二、六向台账

| 向 | 内容（证据） |
|---|---|
| 上游输入 | intake.py（auto_intake 批处理：:319 `lifecycle = "sim" if sim_ok else "candidate"`——批内机器自动走 candidate→sim 或留 candidate；:165-171 fsm.transition(SIM, ctx) 带 SimPromotionContext）；PA-1 三条件实据（双窗/BH-FDR/衰减台账，评据=promotion_advisory.evaluate_sim_preauthorization :341）；Owner token（secrets 键 ZEPHYR_OWNER_APPROVAL_TOKEN） |
| 下游消费 | 注册表 strategy_registry.yaml lifecycle_status 字段（唯一持久真源；CAS 手术+术后复核 promotion_advisory.py:549/:531）；decision 台账（.decision.json）；promotion_advisory._transition_lifecycle :614（拍板驱动 sim→production/sim→shelved）；C6 管线状态治理；下游远处=daily_decision_orchestrator S4 已毕业包集（production 态策略的消费端，现包集空） |
| 自动化触发 | FSM 是库（无自触发、无常驻）；流转触发点两类：①intake 批内自动（candidate→sim，事件链 c4_batch_due/intake）②Owner 拍板 decide()（sim→production/sim→shelved）；shelved→candidate（家族替身回补）与 shelved→retired 为机器边、当前无自动发射方（intake 未来批次用） |
| 真源与注册表 | lifecycle_fsm.py MOD-BT-188（挖矿真源 §2.5 A 方案；复用 zephyr/shared/lifecycle/state_machine.py 泛型基类）；注册表八态词表=strategy_registry.yaml schema:58 注释 candidate/backtest/sim/paper/live/monitoring/decayed/retired；骨架 v1.1 §6 生命周期轴（研发→回测考试→模拟竞争 A/B→实盘生产→降级/退役/复活）；SOP-C（intake 治理动作留痕）；考试判据=sop/backtest_system_sop/exam_policy.md（预注册冻结/封闭族 N_eff/负结果台账——考试链 S-OWNER-001/002 FAIL 台账在案） |
| 门禁与质量尺 | SimPromotionGuard（candidate→sim 三条件∧，context 无 SimPromotionContext=False fail-closed）；OwnerTokenGuard（sim→production 与 production→retired 强制 owner_token 常量时间比对，未配置/空串=拒，"机器不带 token 天然停门"）；candidate→production 无直连边（A 方案治理边界）；非法转换抛 InvalidTransitionError；MODIFY-GUARD=tests/strategy_pipeline/test_lifecycle_fsm.py（在盘） |
| 当前运行状态 | **黄**：本体育证绿（测试在盘、流转点接线在）；注册表 163 条目全部 candidate/sim 两态（production 从未达成=转正从未发生）；词表对齐缺口见 §四——**decide approve 会把 FSM 词"production"写进只认八态词表的注册表字段，语义越界无门禁拦截** |

## 三、子模块清单（6 件）

| # | 子件 | 入口 file:line | 状态 |
|---|---|---|---|
| 3.1 | FSM 本体：candidate/sim/production/shelved/retired 五态七边（c→s、c→sh、sh→c、sh→r、s→p、s→sh、p→r），per-strategy 每台一实例（build_strategy_fsm(sid)），对齐因子版 8 态 10 边模式 | lifecycle_fsm.py:112-135（边表 :123-131；状态常量 :59-63） | 绿（测试在盘） |
| 3.2 | SimPromotionGuard 预授权：三条件（§8 双窗∧BH-FDR∧无未决衰减）收 SimPromotionContext 冻结数据类；PA-1 治本后实据评估迁 promotion_advisory 侧（禁硬编码 True 前科已闭），guard 独立复裁不自证 | lifecycle_fsm.py:66-84；promotion_advisory.py:341-375 | 绿 |
| 3.3 | OwnerTokenGuard：生产语义=sha256 常量时间比对+未配置 fail-closed+空串同罪（替代旧"非空即真"） | lifecycle_fsm.py:87-109 | 绿 |
| 3.4 | intake 自动流转消费方：auto_intake 批内 candidate→sim（sim_ok=预授权三条件全过）否则留 candidate；全自动化 only-add；差异化闸（differentiation_ok） | intake.py:128-/:165-171/:319；registry_writer.append_entries :170（CAS） | 绿 |
| 3.5 | 拍板流转执行：_transition_lifecycle——promote 时若 FSM 在 candidate 先以实据补走 candidate→sim 再 sim→production（lifecycle_now 落差留痕审计）；demote 走 c→sh 无守卫边（风险收敛动作不被预授权反向阻断） | promotion_advisory.py:614-652 | 绿（依赖 F74 堵点清零才首跑） |
| 3.6 | **词表对齐层（注册表八态↔FSM 五态映射）** | 无对应件——越界写入无拦截 | **缺位（本册核心发现）** |

## 四、核心发现：三套词表并存，production 越界写入

| 概念 | FSM 五态（lifecycle_fsm.py） | 注册表八态（strategy_registry.yaml:58） | 骨架 §6 生命周期轴 | 联赛词表（HANDOFF 件 1 league_registry 计划） |
|---|---|---|---|---|
| 候选 | candidate | candidate | 研发 | — |
| 回测/考试 | **无边**（考试前置到工段⑦，FSM 起步即 candidate） | backtest | 回测（考试） | — |
| 模拟观察 | sim（+兼容读 paper，_OBSERVING_LIFECYCLES） | sim/paper | 模拟竞争（A/B） | champion/challenger/retired（自带第三套） |
| 生产 | **production** | **live** | 实盘生产 | — |
| 留档/降档 | **shelved** | **无此值**（最接近 decayed/retired） | 降级 | — |
| 衰减 | **无边** | decayed | 降级 | — |
| 监控 | **无边** | monitoring | —（§9 持续监控语义） | — |
| 退役 | retired | retired | 退役 | retired |

三处硬伤（全部 file:line 实证）：
1. **production 越界**：decide approve → _update_registry_lifecycle 写 `"production"`（promotion_advisory.py:549+/:105 `_DECISION_TARGET`），而注册表 schema 词表生产态叫 `live`（:58）——首次真实转正日将诞生一个词表外状态值，下游任何按八态词表消费 lifecycle 的读者（含 TDM/前端）都不认得它。
2. **demote_decayed 语义分裂**：sim_governance 治理建议词=`demote_decayed`（目标语义=decayed 衰减态，sim_governance.py:127 判定书口径），经 _GOV_REC_MAP 归一 demote 后 FSM 落 **shelved**（promotion_advisory.py:105/:648）——衰减降档与策略留档两种不同业务语义在注册表里混成同一个词表外值；decayed 态在 FSM 中**无边可达**，成为只写不管的死态。
3. **shelved 越界**：同 production，注册表词表无 shelved；shelved→candidate 复活边（家族替身回补）与骨架 §7"冠军降级回挑战者池、regime 轮换时复活"的复活语义未区分（后者裁判=L1 regime 门，未挂任何 guard）。

## 五、堵点与缺口（partial 的真实差值）

| # | 缺口 | 证据 | 修法归属 |
|---|---|---|---|
| 1 | 词表对齐层缺位（§四 三处硬伤） | lifecycle_fsm.py:59-63 vs strategy_registry.yaml:58 | 治理裁定一次改齐（方向二选一：FSM 目标态映射注册表词 production→live+shelved 收编进八态注释；或注册表词表收编 FSM 词）+双侧测试钉值；**须在首个真实拍板日前落地，否则首例转正即写入脏态** |
| 2 | sim→decayed 衰减边缺位：治理 demote_decayed 应直达 decayed（机器边），而非混入 shelved | sim_governance.py 判定书口径 vs promotion_advisory.py:105 | 随堵点 1 同批（加一条机器边+decide demote 目标态分支） |
| 3 | 降级三档（§9 冻结/减仓/清仓）无 FSM 对应：production 只有→retired 一条边；下架分级语义无处落 | lifecycle_fsm.py:130 唯一出边；standards.yaml STD-LIVE-REDLINE-001 draft（#315 B-02 先校准） | 挂实盘域（红线 frozen 时同步），FSM 预留位即可，非本册施工窗 |
| 4 | 复活裁判未挂：shelved→candidate 现语义=家族替身回补；§7 regime 轮换复活（冠军降级标记"何种 regime 失效"）无 guard 无字段 | lifecycle_fsm.py:126 无 guard；§7 骨架原文 | 归 F73 联赛组（联赛建库时定 regime 失效标记字段与复活裁判） |
| 5 | backtest/monitoring 两注册表态在 FSM 无边：注册表既有值 FSM 不管理 | strategy_registry.yaml:58 | 按 w5_1 内收判据登记"跨域不同对象→不并"或补边，须治理立案（防静默死态） |
| 6 | FSM 状态无独立持久化（by design：注册表=状态真源、每台重建）——但重建起点恒 candidate，跨进程的"当前态"完全依赖注册表词表正确 → 堵点 1 是它的单点 | lifecycle_fsm.py:112-114（initial=CANDIDATE）+promotion_advisory.py:640-642（拍板时先补走 c→sim） | 随堵点 1 一并收口（词表对了重建语义即自洽） |

## 六、自审闸三态

**部分挖干可施工**（本体六件五绿一缺位全 file:line；三套词表逐值对照表核到 schema 注释行与 _DECISION_TARGET 常量；骨架 §6 轴五站逐站对账 FSM 覆盖面；六缺口三条本窗可施工、三条登记归属有主——实盘域/F73/治理立案）。PR 组内与 03 册（F74）交叉引用一致：F74 首例真实拍板日=堵点 1 的死线。

## 七、三态结论

**F75 = partial**（与总册判定一致，缺口重新定位：非"FSM 未建"，而是"词表对齐层缺位+骨架 §6 轴未覆盖段"）。
差什么才算 built：①词表对齐层落地（production→live 映射或词表收编，二选一经治理裁定，双侧测试同批）②sim→decayed 衰减边补齐（demote_decayed 语义归位）③backtest/monitoring/shelved 三值处置登记（补边或"不并"立案）④首例真实流转走通后注册表值经下游消费方（前端/日编 S4）实读无歧义。③④为收尾，①②是死线前置（早于首个 approve）。
**回写总册建议**：§一 F75 保持 partial，备注列补"真缺口=词表对齐（production/shelved 越界+decayed 死态），首例转正前必须清"；与 F74 回写项同批提交总筹。

## 八、复核命令

```bash
sed -n '23,36p;59,63p;112,135p' src/zephyr/strategy_pipeline/lifecycle_fsm.py   # 五态七边+语义
sed -n '56,60p' docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml  # 八态词表注释
grep -n "_DECISION_TARGET\|_OBSERVING_LIFECYCLES" src/zephyr/strategy_pipeline/promotion_advisory.py
grep -n "demote_decayed" scripts/backtest/sim_governance.py
python -m pytest tests/strategy_pipeline/test_lifecycle_fsm.py -q -o cache_dir=.runtime/tmp/pytest_cache_fullflow
```
