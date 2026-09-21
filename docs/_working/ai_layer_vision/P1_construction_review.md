---
ttl: task_bound
title: AI 层 P1 复审报告（L2 既成事实逐项核验+问题分级+裁定清单）
owner: ZephyrAlpha-Owner
session: st-taskcards-exec-20260921
date: 2026-09-21
status: review_v2_d12
completes_when: P1 施工全部收官（本方案剩余批次清零）后随 ai_layer 车道归档转 archived
---

# AI 层 P1 复审报告 v2（裁定#392（D-12） 授权基线）

## 一、一句话结论

L2 收集库既成事实经逐项核验为 **8.5/9**（抢建时点 7.5/9，本班按 D-12 授权补齐 4 个验收测试件并核验登记面后，仅余"登记套件"半项：capability card 与 depgraph 节点登记缺凭证）；P1 其余面=OBJ_R S3/S4/S5 + OBJ_M C1-C8 + 七段 DESIGN 施工项全部未动，收尾批方案见同目录 P1_construction_plan.md。

## 二、复审基线与授权

- **追认依据**：裁定#392（D-12）（ruling_registry.yaml L5267 起）——"TC-07 L2 越批施工=追认既成事实（L2 收集库 8/9 项已被全流通车道抢建），授权按'复审 L2 既成事实+方案改收尾批'重写后施工，缺的 4 个验收测试件补齐"。本报告即该授权下的重写版复审；前一版复审/方案全历史零产出（TC-07 卡四路查证在案），无被替换对象。
- **既成事实**：commit 84007a1d6a（2026-09-19，st-ff-ailayer3-20260918）12 文件 2713 行——intake 族源码 7 件+建表器/快照生成器 2 件+测试 2 件+翻译册 1 件。
- **复审输入六源**：①TC-07 任务卡（含 verdict 进度提示）②ai_layer_vision/README.md §3.5 处置总表+§4 施工顺序 ③主文档 ai_layer_vision_and_roadmap_v1.md ④11 本 DESIGN（211-409 行全在，wc 实证）⑤成品先例 rule_replay.py（632 行）+tests（255 行，3ac3af3faa）⑥84007a1d6a 实物+本班测试实跑数字。前任聊天 rollout 件已不在盘（TC-07 卡预告），以①-⑤为基准。

## 三、L2 既成事实 9 项逐项核验（DESIGN §四 施工项清单对照）

| # | 施工项 | DESIGN 验收标准（摘） | 抢建时点（84007a1d6a） | 本班复审后（2026-09-21） | 判定 |
|---|--------|----------------------|----------------------|------------------------|------|
| 1 | DDL 登记器 apply_ai_intake_ddl.py | 幂等两次零错；表/视图/生成列齐全；CHECK 值域一致 | 成品 470 行在 HEAD | `--verify` 实测 `VERIFY ai_intake: OK`；test_schema（ai_intake_test_aibase）真 DDL 部署+DROP 全程零错（conftest 实证，本批 54 用例经它跑通） | ✅ 闭环 |
| 2 | 卡库服务 card_store.py | 单测绿（隔离，禁写生产路径）；非法流转被拒 | 成品 451 行；**测试缺** | 本班补 test_card_store.py 12 passed：状态机全枚举（前进/跳 rejected/禁跳跃/禁复活/intake 吸收）/CRUD 往返/elite 保优 3 条 rank>3 benched/防呆 schema 校验，写面全部落 test_schema | ✅ 闭环 |
| 3 | 查重服务 dedup.py | 中文近重复命中/改写不命中；五比对面逐一单测 | 成品 332 行+test_dedup 12 passed（唯一随批测试件） | 12 passed 复核在绿；known-gap 钉在册（轻改一个分句距离=6 漏检，见问题 P1-e） | ✅ 闭环（带在册 known-gap） |
| 4 | 入库闸 gate.py | 缺 labor_killed/单来源/超配额/换皮四类样本全部被拒且拒因正确 | 成品 406 行；**测试缺** | 本班补 test_gate.py 16 passed：四类样本验收全落——labor_killed 拒因 `labor_killed_missing`、单来源=封顶 L1 非拒绝（`cap_stage=="L1"`）、超配额 `quota_exceeded:<slug>:1/1`、换皮精确层 `duplicate_sha:<card_id>`；判据纯函数零 DB 全枚举 | ✅ 闭环 |
| 5 | 快照生成器 gen_intake_ref_snapshots.py | 产出零手工；重跑幂等；refreshed_at 刷新 | 成品 222 行 | test_dedup PG 用例实证 chart/indicator/algo_flow 三面快照 counts>0 且逐面登记（产出物在库即生成器产出实证）；生成器本体幂等重跑未单独断言（见 P2-d） | ✅ 闭环（间接实证） |
| 6 | 事件层 events.py→intake_events.py | 7 个轻 kind emit/drain/status；KillSwitch 停消费全保留；毒丸留档 | 成品 341 行（**改名留痕**：CREATE-GUARD basename 碰撞，死信 q-20260918-st-ff-ailayer2-20260918-0001 在案）；**测试缺** | 本班补 test_events.py 14 passed：emit 先落盘/未知 kind 与缺必填键拒/drain 成功出队重放零副作用/失败计 attempts 至 MAX_ATTEMPTS=3 判毒丸/毒丸停自动消费+purge 唯一清除口/KillSwitch 停消费全量保留（假探针确定性覆盖） | ✅ 闭环 |
| 7 | KPI 告警 kpi.py | 构造数据可触发贫矿降级/收紧两路告警；阈值读 YAML 非硬编码 | 成品 239 行；**测试缺** | 本班补 test_kpi.py 12 passed：evaluate_series 纯判据四路全枚举+边界（等于阈值不触发/None 周剔除）；test_schema 构造两域数据经 V3 视图实触发 demote（tooling 0%<5%）与 tighten（ai_eng 75%>30%）两路；阈值 tmp 注册表 fail-closed（缺文件/缺条目 AlertThresholdConfigError） | ✅ 闭环 |
| 8 | 登记套件 | 翻译/depgraph/capability card/阈值册/gate_registry 全绿 | 翻译册 +24 行随批；canonical 册 9 条已登记 | 翻译册 ✅（但含幽灵双条目，本班修）；阈值册 ✅（THD-INTAKE-001~004 在 alert_threshold_registry.yaml L813-881，source_code 反向锚定 kpi.py）；canonical 册 ✅（含 standards_governance/__init__.py 预登记，D-7 注记本班补）；**capability card 缺**（data/capability_cards/ 无 intake 族卡）+ **depgraph 设计节点登记无凭证**（见 P1-b/P1-c） | ⚠️ 半闭环 |
| 9 | 测试件 test_dedup/test_gate/test_card_store/test_events/test_kpi | 全绿；零生产路径写入；进回归批 | 仅 test_dedup 1/5（12 passed） | **5/5 全绿**：tests/ai_layer/ 目录 66 passed（含 conftest+test_dedup）；单文件 test_gate 16/test_card_store 12/test_events 14/test_kpi 12；全部零生产路径（写面=test_schema 临时 schema+tmp_path，PG 不可达=skip 而非假绿） | ✅ 闭环 |

**核验小结**：抢建时点 7.5/9（项 1-7 成品 7+项 8 记 0.5+项 9 记 0——任务卡口径将其计 7.5 系把项 3 的随批测试单独计 0.5）；本班补齐后 8.5/9，唯一未闭环=项 8 登记套件的 capability card 与 depgraph 节点两个登记动作（纯登记操作，无代码量，列入收尾批批次 1）。

### 设计偏差在案记录（非缺陷，判读依据）

1. **events.py 改名 intake_events.py**：施工期实测 CREATE-GUARD basename 碰撞（能力册 drift_detection_events 的 alias 裸词 events），改名系死信在案的非设计变更，件内语义与 DESIGN §三 完全一致（intake_events.py 模块头留痕）。
2. **card_store.write_conn 直连 depgraph 写角色**：DatabaseService.get_depgraph_conn 实测恒返 reader 角色（database_service.py:154 未透传 read_only），按 ig_* 图谱写入器同款处置直连+DEPGRAPH-WRITE-PATH 白名单留痕（req_ailayerB_03），DatabaseService 修复后回切。
3. **tokenize 用 bigram 而非 DESIGN §2.3 字面的一元组**：一元组下单字增改同时扰动 1 unigram+2 bigram 致近重复漏出 k=3；bigram 口径判据两侧更陡（dedup.py docstring 实证留痕）。属"口径的实证收敛"，非漂移。

## 四、11 本 DESIGN 状态盘点（P1 剩余面）

| 稿 | DESIGN 行数 | 施工项数 | 状态 |
|----|------------|---------|------|
| L1_perceive | 272 | 9 | 未施工（施工项 7 受 T3 双前置约束，README §3 在案） |
| L2_intake_library | 281 | 9 | **8.5/9**（本报告 §三） |
| L3_cleaning | 241 | 8 | 未施工 |
| L4_compare | 211 | 8 | 未施工（独立性 gate 立案挂 OBJ_R 四步） |
| L5_schedule_gate | 289 | 10 | 未施工（白名单 Owner 点头挂治理流程） |
| L6_ab_switch | 278 | 8 | 未施工（墓碑 TTL 净删=Owner 门位） |
| L7_heredity | 291 | 9 | 未施工 |
| OBJ_M_models | 409 | 8（C1-C8） | 未施工（**Owner 点名第二催**；C6 前置=OBJ_M-#1 路由表 Owner 终批） |
| OBJ_R_rules_standards | 246 | S1-S5 | **S1+S2 已落地**（rule_replay 632 行+17 用例 255 行，3ac3af3faa）；S3 治理立案前置/S4 依赖 gate_execution_stats≥1 窗/S5 依赖 Owner-4 |
| OBJ_S_perimeter | 307 | 8 | 未施工（S1 deny-list 可先行；OBJ_S-#2 registry 增字段待 Owner） |
| OBJ_T_tools | 329 | 9 | 未施工 |

依赖序真源=README §4：L2（已收尾）→L1 感知→L4 对比→L6 切换→L3 清洗→L5 排产→L7 传承，OBJ_M/T/S/R 同批；Owner 对 OBJ_M 点名提前（裁定#392 执行路由"照卡施工"承接）。逐本验收标准/接口契约核对记录：L2 全文核对见 §三；其余 10 本的核对随各批开单时按"施工项/验收标准引 DESIGN 原文"逐条落（施工方案 P1_construction_plan.md 每批五字段已挂 DESIGN 锚点），本复审不重复誊抄。

## 五、分级问题清单（P0 阻塞 / P1 应修 / P2 记录）

**P0（阻塞施工）**：无。4 缺测试件已按 D-12 授权补齐（本班活 A），生产 schema `VERIFY: OK`，无阻塞面。

**P1（应修，列入收尾批）**：

| # | 问题 | 证据 | 处置去向 |
|---|------|------|---------|
| a | 翻译册幽灵双条目：`intake/events.py`（L55581）与 `intake_events.py`（L55621）并存，旧路径实物已不存在 | sed 实证两条目；代码引用面 grep src/scripts/tests 零命中 | **本班活 C 修**（CAS 摘除旧行留注记） |
| b | capability card 缺：data/capability_cards/ 无 intake 族卡（渐进披露面断链） | ls 实证零命中 | 收尾批批次 1 补登记 |
| c | depgraph 设计节点登记无凭证：L2 施工无 apply_depgraph --add-design-node 留痕 | 无登记记录可查 | 收尾批批次 1 补登记并核 |
| d | canonical 册自身也有 `intake/events.py` 幽灵条目（L35828，ai_intake_l2 capability 段） | grep 实证 | 不在本班点名修改范围（红线"注册表只做两处点名修改"），**列收尾批批次 1 与 P1-a 同批处置**，处置前以本条为账实偏差留痕 |
| e | gate 近似层换皮防护弱于设计预期：中文轻改一个分句距离=6 漏出 k=3 | test_dedup known-gap 钉（断言漏检确实发生，判据收紧即红） | 判据收紧提案走 OBJ_R 通道（S3 同批）；不粉饰不改码 |
| f | 包外零消费者：intake_events 四个设计消费方（L1/L3-L4/L5/DataScheduler 唤醒）均未建成 | intake_events.py 头 [CONSUMERS] 实测改判留痕（R-021 型假声明已纠正） | 属七段未施工的自然状态，随各段落地接线；方案批次表已挂依赖 |
| g | card_store 写路径绕 DatabaseService 直连（reader 角色缺陷） | card_store.write_conn docstring+req_ailayerB_03 留痕 | 待 DatabaseService 修 read_only 透传后回切；DEPGRAPH-WRITE-PATH 白名单过渡 |

**P2（记录，无实害或低危）**：

| # | 问题 | 说明 |
|---|------|------|
| a | README §3.5 标题"真待 Owner（6 项）"为陈旧计数 | 正文实列 5 项且对账行写明 17+9+5=31（R9 改判未刷标题），无实害；README 归 ai_layer 目录人工面，随手批刷新 |
| b | DESIGN §四施工项 6 文件名 events.py 与实物 intake_events.py 不一致 | 改名留痕在案（源码头+本报告 §三），DESIGN 未回改——设计稿历史版本不改写惯例，以本条为指针 |
| c | conftest.py 定义 `pytestmark_pg` 变量但从未应用为 pytest marker | 死变量；test_dedup/test 本班四件均自带 needs_pg 不受影响；conftest 归原车道件，不在本班改动面 |
| d | gen_intake_ref_snapshots.py 幂等重跑无直接单测 | 产出物三面在库为间接实证；补测随 OBJ_R S4 体检器批顺带（重跑幂等断言一行） |
| e | kpi.handle_alert 的 demote/longtail 动作路无 schema 注入口（CardStore() 硬绑生产 schema） | 本班 test_kpi 按"测试禁写生产路径"铁律只测零 DB 的 unknown action 拒绝路；两路告警触发已由 evaluate/run 侧覆盖（DESIGN 施工项 7 验收口径="触发告警"）；给 handle_alert 加 schema 参数属源码小改，列收尾批批次 1 可选件 |

## 六、Max 裁定清单（含已裁注记）

| # | 事项 | 状态 | 依据/去向 |
|---|------|------|----------|
| 1 | L2 越批施工追认 | **已裁**：裁定#392（D-12） 追认既成事实，授权"复审+方案改收尾批+补 4 测试件" | ruling_registry.yaml L5267；本报告与同目录 P1_construction_plan.md 即授权产物 |
| 2 | standards_governance/__init__.py 两解 | **已裁**：裁定#392（D-7） = PEP420 隐式命名空间豁免+注册表条目改注对齐账实（零新文件，净零内收） | 同上；注册表注记本班活 C 落地 |
| 3 | D 类 13 项打包（Owner 授权代裁） | **已裁**：裁定#392 整包 active | 同上；本班仅消费 D-7/D-12 两项 |
| 4 | canonical 册 L35828 events.py 幽灵条目处置（同 P1-d） | 待裁（执行级）：建议随批次 1 按翻译册同款"CAS 摘除留注记"办理，无需新裁定 | 本报告留痕即可动 |
| 5 | gate 近似层判据收紧（P1-e known-gap） | 待裁（治理级）：收紧=改判据，须先改 L2 DESIGN §2.3 再施工（MODIFY-GUARD 纪律）；走 OBJ_R S3 提案通道 | OBJ_R 批携带 |
| 6 | OBJ_M-#1 路由表 api_providers 增删+免费窗合规终批 | 待裁（Owner 门位）：C6 施工前置，计费线/订阅=Owner 独占四类事 | README §3.5 真待 Owner 表既有项，非新增 |
| 7 | handle_alert 加 schema 注入口（P2-e） | 待裁（执行级，可选）：一行签名扩展+测试补断言 | 批次 1 可选件，默认不做（净零纪律：等真实第二 schema 消费者出现再扩） |

## 七、证据索引

- 抢建提交：`git show --stat 84007a1d6a`（12 文件 2713 行逐件清单）。
- 本班测试实跑：`python -m pytest tests/ai_layer/ -q` → **66 passed**；单文件 test_gate 16 / test_card_store 12 / test_events 14 / test_kpi 12（Python 3.12.8 原生配置，PG 可达无 skip）。
- 生产部署核验：`python scripts/ai_layer/apply_ai_intake_ddl.py --verify` → `VERIFY ai_intake: OK`。
- 阈值登记：alert_threshold_registry.yaml L813-881（THD-INTAKE-001~004）。
- 裁定登记：ruling_registry.yaml L5267 起（裁定#392 全文含 D-7/D-12）。
- 翻译册双条目：module_translation_registry.yaml L55581（幽灵）/L55621（真）；canonical 册幽灵：L35828；D-7 目标条目：canonical 册 L33174。

## 修订记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-09-21 | v2 | 裁定#392（D-12） 授权重写：L2 既成事实逐项核验+本班补 4 测试件后状态刷新+P0/P1/P2 分级+裁定清单（v1 零产出无实体，不占版本序列） |
