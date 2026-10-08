---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/env_mining/env_20_dev_delivery.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# ENV-20 开发交付流水线挖矿作业簿（B1 批次，2026-10-06）

## §0 环节档案

- **覆盖坐标**：图11 交付流水线（`config/dev_delivery_map.yaml`，30 节点=28 stage+2 gap，wired 22）+图14 施工工作流（`config/construction_workflow_map.yaml`，28 节点=17 stage+11 gap，**unwired_no_caller 15**）+图15 策略卡生命周期（`config/strategy_card_lifecycle_map.yaml`，13 态/17 迁移/13 禁边）。
- **真源锚**：三图均机生（`scripts/governance/d5_architecture/generators/generate_dev_delivery_map.py` / `generate_construction_workflow_map.py` / `generate_strategy_card_lifecycle_map.py`），禁手改后不回生成；图11 骨架=`docs/_working/map_build/fig11_delivery/00_skeleton.md`，图15 骨架=`fig15_cardlife/00_skeleton.md`，图14 语义锚=`docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md`（07 域 15 步）。
- **职责一句话**：代码从会话诞生（图11 C/S/D 三车道）经施工合规 15 步（图14）到策略卡生死轮回（图15）的三段流水线；ROOR 挂 REG-MAP-DEVDELIVERY-001（:579）/REG-MAP-CWF-001（:639）/REG-MAP-SCLC-001（:651）。
- **状态总判**：图11 最健壮（production 26/30）；图14 一半 unwired 但其中 11 个是**设计态缺口显性化**非烂尾；图15 结构满配、消费方六族代码级实证（§1"下"向）。

## §1 六向台账

| 向 | 内部反查发现（带路径） | 外部 | 判定 |
|---|---|---|---|
| 上（触发面——三图各自的"上游"） | 图11：三车道 C15/S9/D6 十交接面实证（laws :24-28"无实证交接不许画边"）；图14：每节点带 policy_step+policy_anchor 挂 15 步（如 D14-02→construction_workflow_policy.md#step-1、D14-04→#step-18）；图15：anchor_source=registry（`docs/01_policies_and_standards/_registry/vocabularies/card_state_vocabulary.yaml`+宿主册 `catalogs/experiment_registry.yaml` CARD-* 契约条目），91 号提案件已降级施工档案（文件头 :2） | 图15 boundary :30 声明不含裁定产生流程（图16）/提交机制（图11）/数据供料（图12）——四图轴界在册 | wired（图11 图15）/signal（图14：4 个 stage 政策锚在而执行件不在） |
| 下（消费面——图15 真实消费方六族，代码 grep 实证） | ①门禁面：`src/zephyr/gov_enforcement/commit_gates/map_family/strategy_card_lifecycle_map_gate.py`+`registry_code_anchor_gate.py`+`registry_alignment.py`；②运行时面：`src/zephyr/reporting/attribution_registry_mapper.py`+`prediction_calibration_monitor.py`（吃 experiment_registry）；③回测面：`scripts/backtest/eval_exp_expectations.py`；④治理面：`scripts/governance/d5_architecture/checkers/check_registry_code_fingerprint.py`/`check_registry_code_anchor.py`+`scripts/governance/d8_doc_sync/agents_cheatsheet_drift_reconciler.py`；⑤总图挂轴：`align_all.py`+`generate_panorama_master_map.py`；⑥同构收编：图16 T9 复活边注"图15 D15-M17 同构"（`generate/validate_governance_legislation_map.py` 引用）。实例面读数：cards_total 89/registered 56/headless 29/needs_adjudication 2 | **56+29+2=87≠89**（若 needs_adjudication⊂headless 则 85），两读法均≠89 且 counts 段无口径注记——counts 校验器未覆盖四数互恰 | wired（六族实证）/signal（89 口径不自明） |
| 内（counts 自洽逐图验） | 图14：17 stage+11 gap=28 ✓；built 6+partial 7+pending 15=28 ✓；wiring 4+8+15+1=28 ✓；**gap 跳号 G10 有账不悬空**（:695-696 在册：D14-G10 词表模块缺失，2026-09-26 复活落仓 a2e820034bd 后闭合除名）。图11：production 26 与骨架 ✅ 26 双轴对齐（ssot_note"多了算谎少了算欠"）；wired22+partial4+unwired_no_caller2+slot_hollow2=30 ✓。图15：13 态+17 迁移+13 禁边=30 总边 ✓ | 图15 D15-M17（:1152）sealed→**新卡** S1，permitted/actor=human——复活唯一合法口与图16 T9 同构 | pass（图11/图14）/signal（图15 89） |
| 旁（三种"负空间"不同物） | 图11 D 车道死信 6 节点（落地异常分流）≠图14 gap 节点（政策承诺件缺口显性化，ssot_note :18 自陈"待总包回写骨架 §1"）≠图15 forbidden_edges 13 条（判据自相矛盾防线）——三语义不可并册；图14 D14-15 提交网关落地（wired）=图11 正门 git_commit.py 的 L2 投影，两图在正门交汇 | `config/strategy_production_map.yaml`（FAC-* 策略工厂，197KB，mtime 10-06 02:35）与图15 boundary 声明轴区分：build_status 是工序进度非契约地位（:34） | pass |
| 史 | 图11 2026-10-04 血肉批（挂图 SOP §4 四字段 purpose_tags/casebooks/trigger_facts/consumers，generated_at 2026-10-04T13:30，commit 28707ce7eb"图11回写血肉+上户口批"）；图14 gap 族源自 2026-09 审计批，G10 已闭合=缺口件可闭合的先例实证；图15 effective 2026-09-24→宿主册 2026-10-04 cutover 同批 | — | pass |
| 新（本簿 2026-10-06 三条） | ①图14 15 个 unwired_no_caller 全名单首录（§2）——此前只有计数无名单；②图15 消费方六族清单首录——"卡生命周期谁在用"此前只有散文断言；③图15 counts 四数互恰缺口（89/56/29/2）——生成器自检盲区 | — | signal |

## §2 挖干自评

- **图14 15 个 unwired_no_caller 全名单**（本簿主挖项）：
  - **stage 4 个**：D14-02 文档审查（red_reason broken_supply，fallback="无留痕面时以对话内 GAP 清单为准，图不代主张"）/D14-04 架构评审门控判定（Step 1.8，fallback="门位不可用时按高危域人工门位停等，不自动放行"，invalidation=评审记录落点待总包裁定）/D14-05 方案挖矿（Step 1.9，red_reason unwired，invalidation="结构 checker 落地（建议挂 d9_knowledge，零新目录）后可升 inspection"）/D14-11 长清单审查。
  - **gap 11 个**：D14-G01 政策指认的守护件不存在（幽灵脚本）/G02 幽灵脚本已进注册表（引用面）/G03 政策所指正门脚本不存在/G04 政策所指诊断件路径失效/G05 设计态先行铁律无执行面/G06 准入记录面不存在/G07 会话工作树 CLI 子命令不存在（四条）/G08 锁释放命令契约与实现不符/G09 前端真源图路径三份不一（双真源嫌疑）/G11 规则册符号锚不存在/G12 上游真源整体归档未跟进（十二处链接）。
- **性质判读**：4 个 stage unwired=政策步无代码执行件（门禁不可机判），但 fallback/invalidation 双列在册=人工兜底与升级路径已画；11 gap=骨架外显性化缺口件（设计态）——**"图14 一半 unwired"是缺件显性化的机械记账，不是流水线烂尾**；对照 G10 先例，缺口件可逐个闭合除名。
- **三扫收敛**：图14 28 节点逐点读 wiring/red_reason/fallback/invalidation✅；图15 消费方六族代码级反查（src/scripts 全树 grep）✅；三图互引核（图16 T9↔D15-M17、D14-15↔图11 正门、图15 boundary↔工厂图）✅。
- **长尾（如实登记）**：图15 counts 89 口径差未解（对拍 CLI 属写侧/运行侧，本簿只读约束未跑）；图11 machine_facts 层未逐节点复核（生成器重扫面，门禁守护非人工义务）。

## §3 挖后自审闸三态裁定

**挂起排期**（主体卡总包回写令；两件 low 小件可随批施工）。
- **挂起主体**：图14 gap 族处置（11 件）——图14 ssot_note 自陈"待总包回写骨架 §1"，处置权在总包不在挖矿层；D14-04 评审记录落点、D14-05 结构 checker 两件同理（invalidation 均写明"总包裁定后改写"）。
- **随批施工小件（low，不卡门位）**：①图15 counts 四数互恰——改 `generate_strategy_card_lifecycle_map.py` 加自检/注记后回生成（机生件修生成器不修图）；②图14-G09/G11 属路径/锚修正级，可按 RULE-WORKTREE 常规 claim 排期。
- **封矿**：无——三图均新生代资产，无退役对象；"gap 族一次清零"式大扫除判不必要（G10 先例证明逐件闭合即可）。
- **解锁条件**：总包回写批文（gap 族+D14-04/D14-05）；小件解锁=常规 claim+生成器门（CONSTRUCTION-WORKFLOW-MAP/STRATEGY-CARD-LIFECYCLE-MAP gate 判红即验证）。

## §4 挖矿日志

- **轮1（2026-10-06）**：三图 counts 段+wiring 分布全量提取——得图14 unwired 15 名单（4 stage+11 gap）与图11 wired22 分布；发现图14 gap 跳 G10。
- **轮2**：G10 跳号溯源（:695-696 复活闭合在账）→判跳号非悬空；图15 消费方全树 grep（src/scripts 七文件+六族归类）；counts 互恰验算发现 89≠87。
- **轮3**：图14 unwired 节点逐点读 fallback/invalidation/policy_anchor 三字段→性质判读从"烂尾"改判"缺件显性化"；三图互引与轴界 boundary 核对收口。
