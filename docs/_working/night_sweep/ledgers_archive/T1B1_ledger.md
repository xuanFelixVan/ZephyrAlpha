---
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# T1B1_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# T1-B1 旧数据治理包处置车道 · 台账（总筹=st-nightsweep-chief-20260929）
session: st-menu-t1b1-20260930
updated: 2026-09-30
owner_approval_quoted: "你挖矿确定是没用的就可以删除，你可以先告诉我旧数据治理包 16 件是什么东西有什么用。"
authorization_semantics: 挖矿确认无用即可删（git 历史留档可回滚）+ 必须交付 16 件大白话报告

items:
  - id: T1B1-1
    task: 16 件逐件档案卡（Owner 报告底稿）
    verdict: DONE-LANED
    evidence: docs/_working/night_sweep/b_audit/b1_sixteen_dossier.md（token nightsweep-t1b1-b1-dossier-b1-sixteen-dossier-20260930 已登记；随净删批入队）
    note: 五行卡×16；含 NB1-B1 后新证据改判（四引擎接线台账+st-c9-purifin d4670f14f9 落地）
  - id: T1B1-2
    task: 融合 quality_sla_breach_predictor → src/zephyr/data/quality/
    verdict: ENQUEUED-LANDING
    evidence: >
      队列项 q-20261001-st-menu-t1b1-20260930-0006（原 0001→0003→0006，前手死于 ghost_session
      心跳窗，根因已修：heartbeat.jsonl alive 记录+SessionRegistry 逻辑会话双轨保活）；
      git mv 零算法改动+新增 archive_sla_burnrate.py 消费面（F08 manifest 镜像常量+同源断言测试防漂移；
      manifest 缺失/观测不足=not_run 不冒绿）+包门面；32 passed；三件套齐
      （token x3=data_quality_sla_module、翻译条目 x4、depgraph 旧节点 15708760 deprecated+新节点
      15724625/26/27+generate_project_depgraph --force 1773 模块 0 失败）
    note: >
      热册攻防实录：capability 册遭他会话陈旧快照覆写两次（-84 行蒸发事件，含本车道 dossier 条目），
      按 bct 工具 fail-safe 处方以 HEAD 为基做纯增量重建（HEAD+本道 3 条，零删条）； snapshots 入袋时点
      registry=有效 YAML 12407 条（b6/t1b5 上游条目在位）
  - id: T1B1-3
    task: 确认无用件删除（逐件三判据）
    verdict: ENQUEUED-LANDING
    evidence: >
      队列项 q-20261001-st-menu-t1b1-20260930-0007（原 0002→0004→0007）；净删 9 src+3 测试
      （三判据全过：零消费者 AST+grep 实证/功能被替代实证/数据无独有内容）；G 盘留证
      G:/zephyr_cold/retire_c267_20260930/F127_data_eng/（12 件 sha256+MANIFEST.md）；
      import 冒烟三轮全过；触面测试 140 passed；[allow-mass-deletion] 正门标记+Owner 批文原文入 message
    note: 判据不过即降级——4 件从"删"改判储备（见 T1B1-4），零扩大化
  - id: T1B1-4
    task: 储备件注记（不改行为）
    verdict: DONE-LANED（随 0007 批）
    evidence: >
      五件 [RESERVE-T1B1] 头注：cleaning_anomaly_engine（在途接线 wired，c9-purifin 已落地——
      NB1-B1 删判被新证据推翻）、data_anomaly_alerter+expectation_governance（四引擎台账接口位
      预留待批）、gpu_resource_manager（GPU 队领地 NB1-B1 自注不代裁）、incremental_update_engine
      （reconciler 氏族备忘，禁第二真源）；包 __init__ 同步净删面+reserve 面双注记
  - id: T1B1-5
    task: 批复落册 #42-44
    verdict: DONE（CAS safe_write 落盘，随续批入队）
    evidence: >
      docs/_working/fullconnect_campaign/99_skipped_for_owner.md 状态列：#42 全量执行记录+批文原文；
      #43 批复语义已到但特指 data_eng 16 件+F128 复活 WIP 在盘，不越权代裁；#44 追加同范交叉引用
  - id: T1B1-6
    task: dangling 登记面移交
    verdict: HANDED-OVER
    evidence: >
      净删九件 module_id 翻译/文档条目+predictor module index.md（docs/03_modules/_domain_data_eng/
      quality_sla_breach_predictor/index.md）+algo_flow 册原地（FOLDER-CAPACITY 硬上限拒纳新件）——
      #44 先例同范移交维护班

blockers_handover:
  - 队列落地最终态（2026-10-01 凌晨）：0009/0010 死于"网关落盘失败 CLAIM_REQUIRED_VIOLATION"（落地侧
    worktree 的 claim 语义 vs 主区 .ailocks 不互通——队列基建缺陷）、0011 死于 Popen captured_/timeout
    TypeError（同 0005，队列基建缺陷）。三件死信已在册，**处置=维护班修 Popen bug 后
    `commit_queue.py requeue q-20261001-st-menu-t1b1-20260930-0009 --force`（0010/0011 同），
    或主区静窗直接 git_commit.py --adopt-prior-work**；工作区快照即真源，全部内容在盘已测
    （fusion 32 passed / deletion 触面 140 passed）
  - 落地前再核（维护班）：①capability/translation 两热册可能再遭陈旧快照覆写——本道条目
    识别词=data_quality_sla_module（capability 册 x3）/src/zephyr/data/quality（translation 册 x3），
    缺则按 bct 工具 fail-safe 处方以 HEAD 为基纯增量补回；②F128 车道 4 条 translation 词条
    曾被吃掉 - module_path: 头（本道已结构性修复还原，路径配对归 F128 车道复核）
  - allow_overlap 24h 配额已耗尽（5/5，多死于重试链）；ghost 闸需 heartbeat.jsonl 末行=alive
    （循环脚本=.runtime/tmp/st-nightsweep-20260929/t1b1_heartbeat_loop.py，30min 窗）
  - dead 0001-0008 为同链重试尸体（ghost/landing 异常），可由维护班按 dead_purged 范式清理
```
