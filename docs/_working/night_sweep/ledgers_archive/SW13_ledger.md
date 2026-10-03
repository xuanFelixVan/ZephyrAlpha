---
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# SW13_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# SW13 六图战役收口车道 · 台账（sid=st-nightsweep-sw13-20260929）
date: 2026-09-29
chief: st-nightsweep-chief-20260929

- id: SW13-C1（图本体两件+词表+宿主册+ROOR 收编落地）
  verdict: DONE-LANED(qid=q-20260929-st-nightsweep-sw13-20260929-0001, files=11)
  evidence: |
    挖矿裁定：审计簇 C113（members I4:I453/I3:I31/H38/H40/F41/I3:I23）所指"图14/15 图本体 yaml 缺+
    词表缺"实为**落地缺口而非生产缺口**——六图战役 st-mapbuild-20260924 已产出终版成品，
    但其 worktree 内 3 件为 untracked 孤儿（git log --all 全分支零 commit、无在队袋、会话已亡无 claim）。
    SW13 按"先挖后干+内收"收编：strategy_card_lifecycle_map.yaml sha16=3297a22f83934c81 与
    91 提案件 §10 execution_record.idempotency.sha16 逐字一致（3 runs same_sha256 的终版铁证）。
    落地件哈希锚：construction_workflow_map=254732370135ad20（2221 行，29 节点/34 边/7 反馈环，
    pending_anchors 17 诚实开账）；strategy_card_lifecycle_map=3297a22f83934c81（13 状态+17 迁移+
    13 禁边+56 条 card_ledger，anchor_source=registry）；card_state_vocabulary=288ef273321f89df
    （REG-CARDSTATE-VOCAB-001，13 值闭集）；experiment_registry 2.1→2.2 整拷（基线 blob 132f7b33
    与本批相同=纯增量，+56 CARD-*，L-HOST15 已按总包裁执行的迁移）；ROOR 增量手工重放
    （safe_write_text CAS before 2907be07→after 051b416f，+cardstate 行/EXP-001 计数 11→67/
    summary 由 check_registry_consistency.py --refresh-summary 机生 total 80 broken 0）。

- id: SW13-C2（红蓝对抗·先证能红→修绿）
  verdict: DONE-LANED(18/18 passed)
  evidence: |
    tests/governance/d5_architecture/test_fig14_fig15_map_bodies_adversarial.py（路径避开 chief7 在飞
    两测；tests/ 豁免 CREATE-GUARD）：3 绿控制组（真实图+词表零违例）+15 红案全点名——
    杀节点（FIG14-DANGLING-EDGE）/断边（FIG15-TRANSITION-DANGLING-FROM/TO）/伪造计数
    （total_nodes/total_transitions/registered_entries/by_node_type/total_values 全轴）/坏枚举
    （node_type/card_state/state value/词表值越闭集）+加验封卡就地复活（TERMINAL-REVIVE-INPLACE，
    M17 cross_instance=True 复活边不误伤）+悬空 revives 指针。红优先协议实击发：初版判据闭包轴
    误用词表集，kill-state 红案不出红（漏检）→判据修正为图自身状态集+词表集双轴→复跑全绿。
    独立加验：chief7 预放主区盘面的 validate_strategy_card_lifecycle_map.py（sha16=a3115a818e8a2f10
    =其袋 0329 blob 同物，只读复用未动其件）复跑=结构 0 错+8 实例红账，逐条等于 91 提案件
    §10 red_state_after_migration 已登记真实数据缺陷（F-05/F-07/X09/F-03×2/族账×3），零新增红。

- id: SW13-C3（规格卡+登记三件套）
  verdict: DONE-LANED(同 qid)
  evidence: |
    规格卡 docs/_working/night_sweep/fig14_fig15_spec.md（避让边界表/两图节点边数据源/
    TDM·depgraph 挂接/哈希锚/债务移交）；token 四件经 batch_creation_tokens.py 精确路径通道
    （capability=six_map_campaign，未触 --wide-prefix 防呆，工具零拒写）；翻译条目+depgraph
    设计节点 15387763 已登记；capability_lookup --find 空结果审计在案。

- id: SW13-C4（52 config token 宽前缀·I3:I23 处置）
  verdict: ADVANCED(本批不涉，现状登记)
  evidence: |
    I3:I23 为六图缺口簇成员卡（canonical.json C113 members），"52 config token 宽前缀"指既有
    config token 的历史登记形态。本批新增 4 token 全部走精确单文件前缀，--wide-prefix 旗未被
    触发、工具无拒写——无需按宽前缀现状处置，历史 52 件宽前缀治理留原审计车道。

- id: SW13-C5（避让记录）
  verdict: CROSSCHECK
  evidence: |
    ①chief7 两袋在飞 q-…-0329(40件)/0369(36件)（=总纲所记 0253/0293 同族尾袋，pending 实测）：
    含 validate_construction_steps.py、validate_strategy_card_lifecycle_map.py（其 blob a3115a81
    已被预放主区盘面 02:11，SW13 全程未改该件）、两图 adversarial 测试、fig14 簿 00/01——
    SW13 只做其袋不含的两图本体+词表+宿主册；其 _GOOD 控制组读 config/construction_workflow_map.yaml，
    本批落地即解除其缺图前置（协同非撞车）。
    ②st-s52-dispatch2/st-secbatch-dispatch2：pending 目录零命中（无在飞袋）。
    ③st-mapbuild-20260924 战役整合批 272 件（alignment_checklist 行/policy 17 锚块/三 gate/
    五生成器/ruling #414+#415 战役编号——与主区已占用 #414 存储终裁、#415 总包单写者撞号，
    其 §10 让号机制需再重编）：SW13 未代落，已在 99_pending_owner.md SW13 终态段登记待整合。
    ④job 领地核查：ROOR/experiment_registry/vocab index/module_translation/capability_canonical
    五个共享面在动手前逐一核对基线 blob，ROOR 基线漂移（3ea37c1→f207087，他队今晚落 3 册）改为
    增量重放而非整拷，零覆盖他队内容。

- id: SW13-C6（收口册）
  verdict: DONE-LANED(同 qid)
  evidence: docs/_working/map_build/99_pending_owner.md 追加「SW13 终态段」：落地件哈希表/验证留痕/
    三项未收口债务（chief7 袋/战役整合批/fig15 两判据口径待总包）。
```
