---
created: "2026-10-07"
ttl: task_bound
title: "总包夜战 W1·业务块子册：治理门禁（21 环节×子模块×上下游×本夜卡）"
session: st-mastertc-mine
---

# 0x_block：治理门禁（K 段(F97-F110)+J 段治理件(F87 红线/F88 LSG/F91 能力反查)+F116/F117 方法论文档+F124 词表+F128 数据安全）

> 环节行/职责/上下游/模块锚点全部复用 `docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md`（F01-F122）与 `docs/_working/fullconnect_campaign/00_skeleton/00_skeleton_verified.md`（F123-F132 定版新增）；状态轴复用 `docs/_working/night_sweep_20260929/00_skeleton_nightsweep.md`。本册只做块视图组装+本夜卡挂接，不重挖、不改真源。

## 一、环节清单（21 环节）

| 环节 | 名称 | 段 | 状态轴 | 基态 | 上游（谁供料）| 下游（谁消费）| 核心模块锚点 | 本夜卡 |
|---|---|---|---|---|---|---|---|---|
| F087 | AI 红线 | J | 开口 | partial | 治理层 | F86 | src/zephyr/ai_layer/redline/ | — |
| F088 | LSG 安全网关 | J | 已通 | built | — | 全部 LLM 面 | src/zephyr/security/llm_defense/llm_security/gateway.py | — |
| F091 | 能力反查渐进披露 | J | 已通 | built | — | 施工前置 | src/zephyr/governance/capability_lookup.py；data/capability_cards/ | — |
| F097 | commit 侧门禁链 | K | 已通 | built | — | 提交链 | 提交链战役 00_skeleton | C97(L1)、X01(L1)、C338(L2)、C150(L2)、C02(L3)、C05(L3)、C147(L3)、C300(L3)、C330(L3)、C11(L5)、C441(L10)、C263(L11)、C56(L11)、C155(L11) |
| F098 | GateEngine 运行时门禁 | K | 已通 | built | 规则 | 全链 | src/zephyr/gov_enforcement/rule_enforcement/ | C157(L1) |
| F099 | 漂移检测 | K | 已通 | built | F98 | 告警 | src/zephyr/gov_drift/ | C245(L1) |
| F100 | 红蓝对抗 | K | 已通 | built | — | F98 | src/zephyr/security/adversarial_validation/ | C16(L11) |
| F101 | 规则与裁定体系 | K | 已通 | built | Owner 门 | 全链 | docs/01_policies_and_standards/rules/ | C244(L1)、C323(L1)、C266(L4)、C65(L10) |
| F102 | 审计体系 | K | 已通 | built | 全链 | 报告 | src/zephyr/gov_audit/ | C268(L2)、C342(L4)、C412(L8)、C62(L9) |
| F103 | 代码质量与克隆守卫 | K | 已通 | built | F98 | 施工 | src/zephyr/gov_code_quality/、clone_guard/ | C346(L2)、C304(L2) |
| F104 | 会话并发治理 | K | 已通 | built | — | 提交链 | src/zephyr/security/access_control/session_concurrency.py；scripts/git_commit.py | C461(L2)、C248(L3) |
| F105 | 密钥治理 | K | 已通 | built | — | 全链 | src/zephyr/shared/security/secrets.py；SECRETS.md | C19(L10) |
| F106 | 术语三层翻译体系 | K | 已通 | built | 模块册 | 生成器 | docs/01.../_registry/catalogs/module_translation_registry.yaml | — |
| F107 | 回滚恢复 | K | 已通 | built | F84 | 全链 | src/zephyr/infrastructure/rollback/ | — |
| F108 | 人机门位 | K | 已通 | built | REG-RISK-TIER-001 | 全链门位 | docs/01.../catalogs/risk_tier_registry.yaml | C320(L10) |
| F109 | 注册表族治理 | K | 已通 | built | 全注册表 | 全链 | docs/registry_of_registries.yaml | C443(L2)、C156(L5)、C24(L10) |
| F110 | 契约冻结与错误码 | K | 已通 | built | — | 全链 | src/zephyr/shared/contracts/freeze_manifest.yaml | C169(L8)、C475(L8) |
| F116 | SOP 方法论族 | M | 已通 | built | — | 全链方法论 | docs/01_policies_and_standards/sop/（12 目录实测：automation/backtest_system/construct | C430(L4)、C452(L7) |
| F117 | 文档资产体系 | M | 已通 | built | — | 治理面 | docs/01.../catalogs/directory_registry.yaml；data/asset_index/unified-asset-index | C128(L1)、C27(L1)、C30(L4)、C61(L4)、C129(L4)、C419(L4)、C453(L4)、C462(L8)、C161(L9)、C127(L9)、C473(L9) |
| F124 | 状态词表册生命周期(REG-STATE-VOCAB-001) | 新环 | 开口 | new(定版新增) | — | — | 处方卷=11_f124_state_vocab_lifecycle.md | — |
| F128 | data_security 数据安全域(10 py) | 新环 | 开口 | new(定版新增) | — | — | 处方卷=12_f128_data_security_masking.md | — |

## 二、块内数据流与上下游（谁喂谁、谁消费谁——真源 DAG 摘录）

### J 段·AI 层链（F087-F091）

- **F087 AI 红线**：negative_list/年审/会话环境守卫/严重度路由。上游=治理层；下游=F86。本夜无卡（开口，见总表 §五建议）
- **F088 LSG 安全网关**：全部 LLM 调用五层防御+注入检测+行为审计。上游=—；下游=全部 LLM 面。本夜无卡
- **F091 能力反查渐进披露**：capability 378 条 canonical+44 卡片+12 生成器别名。上游=—；下游=施工前置。本夜无卡

### K 段·治理门禁链（F097-F110）

- **F097 commit 侧门禁链**：23 环节/115 子环节（引用不重挖）。上游=—；下游=提交链。本夜卡：C97、X01、C338、C150、C02、C05、C147、C300、C330、C11、C441、C263、C56、C155
- **F098 GateEngine 运行时门禁**：91 门禁 canonical+GatePipeline+MAD 准入。上游=规则；下游=全链。本夜卡：C157
- **F099 漂移检测**：30 检测器+基线/级联/金丝雀+双 watchdog。上游=F98；下游=告警。本夜卡：C245
- **F100 红蓝对抗**：攻击场景 53+宪法条款 44。上游=—；下游=F98。本夜卡：C16
- **F101 规则与裁定体系**：86 trae_*.yaml+ruling_registry 同 commit 原子。上游=Owner 门；下游=全链。本夜卡：C244、C323、C266、C65
- **F102 审计体系**：gov_audit 编排+语义/供应链/隐私审计+Merkle 小时链。上游=全链；下游=报告。本夜卡：C268、C342、C412、C62
- **F103 代码质量与克隆守卫**：code_dedup+extract 级克隆无逃生。上游=F98；下游=施工。本夜卡：C346、C304
- **F104 会话并发治理**：session_concurrency+lock claim+worktree 四证。上游=—；下游=提交链。本夜卡：C461、C248
- **F105 密钥治理**：secrets.py 唯一通道三道 gate+生命周期。上游=—；下游=全链。本夜卡：C19
- **F106 术语三层翻译体系**：术语/域/模块三册 7686 条+i18n loader+覆盖 gate。上游=模块册；下游=生成器。本夜无卡
- **F107 回滚恢复**：双轨 checkpoint+四级回滚+G0 验证自愈。上游=F84；下游=全链。本夜无卡
- **F108 人机门位**：域风险分级 18 条→四类 Owner 门位。上游=REG-RISK-TIER-001；下游=全链门位。本夜卡：C320
- **F109 注册表族治理**：ROOR 76 册+master_index+一致性契约+净零审计。上游=全注册表；下游=全链。本夜卡：C443、C156、C24
- **F110 契约冻结与错误码**：freeze_manifest 38 契约+error_code 788 SSoT。上游=—；下游=全链。本夜卡：C169、C475

### M 段·全局横切段（F116-F117）

- **F116 SOP 方法论族**：九族真源（挖矿/施工/数据操作/回测/治理/图书馆/自动化/运维/审查+TDM 族）。上游=—；下游=全链方法论。本夜卡：C430、C452
- **F117 文档资产体系**：目录册 87+统一资产索引 33249+rule_catalog 256。上游=—；下游=治理面。本夜卡：C128、C27、C30、C61、C129、C419、C453、C462、C161、C127、C473

## 三、本夜涉及卡（49 张，去重按主挂接）

| 卡号 | 车道 | 自审闸预判 | 卡面摘要（canonical）| night_sweep 机判交叉 |
|---|---|---|---|---|
| C97 | L1 | **GREEN** | N-1：ALGO_FLOW external 指针悬空 9 枚（read_side 两件 gate 指向不存在的 read_side_fms_hygiene_gate.yaml） | — |
| X01 | L1 | **RED** | creation_token 预检/工具口径矛盾立案（预检索 .md token、工具回'已登记'、--wide-prefix 拒写三方矛盾无人回修） | — |
| C338 | L2 | **GREEN** | integ2三件：重取基底mergeable_pred+入队预检扩面+RECONCILER-FILE-OPS diff化 | — |
| C150 | L2 | **GREEN** | k=6 试轮结论（提交池工数 4→6，Owner 09-26 批准） | — |
| C02 | L3 | **GREEN** | 死信终局处置（内容驱动新规）整体未启动——dead 1079 封在册且持续增长，dead_archive_final 不存在 | — |
| C05 | L3 | **GREEN** | R2 复测（csx_deep_01..09 全集重跑对照 R1，无可回收>5min/天=达标） | — |
| C147 | L3 | **GREEN** | R3 复测第二轮确认（连续两轮达标=终止） | — |
| C300 | L3 | **GREEN** | R6 flag commit_queue_interactive 出厂翻转窗口 | — |
| C330 | L3 | **GREEN** | QMine 收尾①-⑥（candidate 撞号/api_server 心跳/snapself+EV 护栏/blob_gc 等） | — |
| C11 | L5 | **WAIT** | blob 归档两代方案均未执行（blob_gc --archive 从未实弹，blobs 已从 5803 块涨至 23217 块；phase2 8509 块归档件未动） | — |
| C441 | L10 | **GREEN** | ⚑-4 出厂开关三件（immutable_tree/词表门 block/AI 进化点火三缺） | — |
| C263 | L11 | **GREEN** | test_commit_preflight_registry_cache.py 孤儿测试收编（impl已在HEAD 026fd1fbea） | — |
| C56 | L11 | **GREEN** | stfinalbuild 66 件代码面落地——部分已被后续袋吸收，q-0213（40 件 RMCode 抢救袋）仍在 pending 队，约 62 件 HEAD 实测未落（清单在 .runtime/ | — |
| C155 | L11 | **GREEN** | N1 snapself 层+EV 护栏重放（铁尺 6红转绿+4红转绿） | — |
| C157 | L1 | **GREEN** | QMine二期矿·gate 链残差计时二期 | — |
| C245 | L1 | **GREEN** | W-171 align_all全量实跑复验/复裁 | — |
| C16 | L11 | **GREEN** | 红蓝场景⑦补跑（跨道连坐：两会话同域文件并发提交合并正确性） | — |
| C244 | L1 | **GREEN** | W-170 | — |
| C323 | L1 | **WAIT** | L3 | — |
| C266 | L4 | **GREEN** | 终局清单§4约60项裁定批量落 ruling_registry（P0-4.14"等独占解除，明日"） | — |
| C65 | L10 | **GREEN** | fullconnect 99_skipped_for_owner #1-#41 全量菜单待裁（含高频 10 项 #29/#34/#35/#36/#8/#14/#21/#25/#19/#20；经 rul | — |
| C268 | L2 | **GREEN** | P2五件结构性补强（防假绿三件套/晋升门阈值预登记/独立验证通道/三层对账日报/季度审计注册） | 62 |
| C342 | L4 | **GREEN** | 挖矿"万无一失不成立"处置（幽灵引用37处/142项实数/封矿复核11份） | — |
| C412 | L8 | **GREEN** | B.5 真终验（冻结车道落地面逐目录两轮、14 目录无缺面）+ 拆 tests/infrastructure 超时件 | — |
| C62 | L9 | **WAIT** | 日班移交两项：gov_audit 跨进程锁竞争楔死（块B）+L09 性能绊线 800ms | — |
| C346 | L2 | **GREEN** | CAPABILITY-OVERLAP 不恢复（收编进CREATE-GUARD）+禁用期回溯核查 | — |
| C304 | L2 | **GREEN** | T3 CREATE-GUARD 触发面登记（files_trigger）或 own-scope 差分 | — |
| C461 | L2 | **WAIT** | O-6 主区 164 枚他道暂存删除三分诊（搬迁/清理/误删） | — |
| C248 | L3 | **GREEN** | W-177 m1_data两车道同名文件合并 | — |
| C19 | L10 | **GREEN** | qmine R3：3 密钥门死触发定性呈报（registrar warn 现状） | — |
| C320 | L10 | **GREEN** | 甲-2 图15 M11/M14/M17 迁移挂 Owner 门（risk_tier human_gate 空） | — |
| C443 | L2 | **GREEN** | 新增待办 W-133..W-136 四件回流骨架 | — |
| C156 | L5 | **GREEN** | QMine二期矿·登记册数据卫生（字段改名486条+ruling decided/void 枚举立法） | — |
| C24 | L10 | **GREEN** | ROOR 223 册收敛 8 净删候选（证据链在 S4_registry_machine_governance/README.md §4；结构性净删 0） | — |
| C169 | L8 | **GREEN** | 施工清单4 IFC-007 契约级联钩子 | — |
| C475 | L8 | **WAIT** | trae_032 修正批五件 + step7 契约级联启用（B10-P3） | — |
| C430 | L4 | **GREEN** | W2 首路调研中途失败窄口径重投（主题 1-3/6 覆盖薄，未闭合三条之一） | — |
| C452 | L7 | **GREEN** | 波 2.4 号文缺失（quant_methodology 07/08/12） | — |
| C128 | L1 | **WAIT** | '_working 新件必须有 created'门（防回填后继续漏；终局菜单④） | — |
| C27 | L1 | **WAIT** | FMS-HYGIENE warn→block 翻转（现 warn 执法+3702 基线棘轮；翻 block 需存量清偿过半+判据改写，挂 Owner 菜单） | — |
| C30 | L4 | **GREEN** | docs/02_enterprise_architecture/02_domain_architecture_docs/ 76+ 大文件从未入 git（注意：I5 车道有'幻影区判据错案撤'记录，施工 | — |
| C61 | L4 | **GREEN** | 叶册 22 本 token 批落地（chief7_docs_staging 车道字节在 .aidrafts/st-chief7-20260928） | — |
| C129 | L4 | **WAIT** | 99_delivery_report.md §十七..廿八落库（存储第二波/镜像树裁定/陈化普查/死锁根因/记忆体检——盘面 640 行 vs HEAD 240 行，自称'已入册'实未落地） | — |
| C419 | L4 | **GREEN** | 终局报告 16 项任务对账（自称 7 完成/2 部分/7 未做） | — |
| C453 | L4 | **GREEN** | R-1..R-7 移交清单（叶子册/d5 五图/热册增量等） | — |
| C462 | L8 | **WAIT** | _working 10 件在册盘上无 + 全仓 175 件在册被删未提交 | — |
| C161 | L9 | **GREEN** | 后波③ C 类 412 行 fix_map 余量清偿+_working 2827 件陈化处置 | — |
| C127 | L9 | **GREEN** | _working 文件名→created 一次性回填批（1807 件元数据欠账） | — |
| C473 | L9 | **GREEN** | FMS 九本施工簿 S1-S9（每线一簿，挖干封矿） | — |

## 四、处方指针（复用既有工单，不新开处方）

- 挖矿处方卷=docs/_working/fullconnect_campaign/ 各域 per-F 卷（总表夜战骨架处方指针列）；施工序列=docs/_working/fullconnect_campaign/00_workorders.md（S1-S5+§四下一战役）；分诊六态=docs/_working/final_delivery_campaign/workorders_{governance,commit_clean,data_exam_factory,docs_misc}.md。
- 本块开口环节中已有工单无卡者（如 F115'R1-R3 最薄一刀'）按总表 §五建议补卡挂接，工单不重写。
- Owner 门位卡（等Owner 状态轴/§五 保留）本夜只登记不施工；清单见总表 §四 WAIT 行。

## 五、复核命令

```bash
# 本块环节数与总表 §三 行一致；卡数与总表 §四 该块行数一致（主挂接口径）
grep -c '^| F' docs/_working/master_tc_night/01_skeleton/05_block_governance_gates.md
```
