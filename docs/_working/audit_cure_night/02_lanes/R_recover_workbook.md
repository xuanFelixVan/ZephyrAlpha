---
ttl: task_bound
title: 审计闭合夜·车道 R（死袋复活）作业簿
created: 2026-10-08
sid: st-acure-r1
status: 三袋入队待传送带落地（reincarnation_count=2 后继化身续班）
completes_when: 裁定#490 授权的死袋复活车道各袋（q-20261008-st-acure-r1-0002/0003/0004+本簿）经传送带落地且 git log -1 --name-only 核归属零外来后，本簿转 done 归档
---

# 车道 R（死袋复活）作业簿（st-acure-r1，2026-10-08 审计闭合夜）

> 总包授权=裁定#490（落册中）。任务=把外部审计钉死的"死袋假完成簇"真正复活落地。
> 环境：reaper live（source=live）/Python 3.12.8/usercustomize 在岗；主区直改（--allow-non-worktree）；
> 提交唯一正门 git_commit.py；本班为同 sid 第二化身（前班 01:13-01:20 落两袋半后 pid 死亡，session_worktree 注册 reincarnation_count=2 续班）。

## 〇、前班遗产核账（git log 实证，非本班重做）

| commit | 袋 | 内容 | 读数 |
|--------|----|------|------|
| 4e53c66984 | mini-0003 写者腿 | scripts/start_paper_session.py（_PaperFillJsonlWriter，sim 域硬断言） | 随 d775bc3e45 9/9 passed |
| d775bc3e45 | mini-0003 续 | 写者接口对齐已落地 9 测套件（常量改名+注入缝，零语义变更） | 9/9 passed（commit 记录） |
| a3d2c65804 | mini-0002 缩面 | tests/backtest/test_lookahead_injection_red_ruler.py（只落测试件，放弃断锚） | 本班复验 16 passed |

→ 前班遗留半成品：tech_factor token 已 api.register 入 PG（v1）未落 YAML；三信号模块 no_mount_reason 已入 PG（v2）未落 YAML；本簿 token 未登记。本班清偿见 §一。

## 一、token 袋（两步铁律+投影正道——本班最大挖矿成果）

**死袋簇根因更正**：capability 册自 REG-CAPCAN-001 投影化后=YAML:=render(PG 账本快照)，REGISTRY-YAML-PARSE 门以 .runtime/projection/registry_projection_state.json 双指纹（content_sha256+ledger_revision）执法"私改投影册无效"。死袋档所述"夜班 45c1f0b224 原行被后续注册表落地漂移冲失"真相=多数为**合法 render 追平**（手改行不在 PG，render 即消失），少数为他车道落袋战争 ref 竞态。

**正道流程**（本班实证走通）：PG 意图 API（zephyr.governance.registry_ledger api.register/update）→ publish_snapshot(repo_root 显式) → registry_projection_generator --render → git_commit 提交渲染产物。

**清偿面**（PG 已在册，随任一次 render 落 HEAD）：
- 三信号模块 no_mount_reason（v2：研究面结构件（testing，G-B/C 族首件）：消费位候选未定，挂图申报随首个生产消费者接线批补报（C252 选型口径，禁造假消费位））
- entity_graph_uscc_bridge no_mount_reason（v2：数据治理消歧桥（只读提案器，四态提案零真实库写），非 TDM 决策节点对应物；挂图归属随数据治理域节点图扩容另批）
- tech_factor_pipeline token（v1，capability=tech_factor_pipeline，no_mount_reason=研究面接线件未实弹）
- 本簿 token（api.register OK_NOOP v1，acure_lane_r）

**投递史**（token 袋 3 次上限内如实记）：
1. 手术重建直投（HEAD+16 增行）→ SESSION-REQUIRED（前班注册过期）；改 --allow-overlap 后自动入队 q-20261008-st-acure-r1-0001。
2. 直投 v2（render 后 staging）→ REGISTRY-YAML-PARSE 私改指纹拦截 → 挖矿发现投影正道。
3. v3 render+publish_snapshot v98（entry_count=14397）直投 → LOCK_TIMEOUT×1 → allow_overlap 24h 限额 5 次触发（TRAE-079 fail 条件，逃生通道已封）→ 改 lock_files 正道又遇 CLAIM-REQUIRED→st-mx07-L11 活跃在册让位。
4. **终局**：三信号 no_mount_reason+tech_factor token+bridge no_mount_reason 已由他会话 render 批次带入 HEAD（poll 实证 count≥1）；本簿 token 在 PG 待下次 render。q-0001 手改字节废袋被 belt 判 ghost_session 死信（预期内，内容已被正道取代）。

## 二、逐袋六向台账

### 袋A q-20261007-st-mastertc-recover-0005（C232/C234/C235 三信号模块+三单测）→ 队列 q-20261008-st-acure-r1-0002

- ①卡面：event_axis（SEALED/BUSTED/BROKEN 互斥单选）/swing_sequence（缠论分型序列标注）/resonance_pair（共振判定器不点火）+三单测；六件 sha256 与袋档全等（65b223c3/b1271b45/b1c85a43/8eb2bb7b/cd8b02a6/4934f050）零重做。
- ②死因：CREATE-GUARD MAP-MOUNTS（三 src 新件未申报挂图面）。
- ③清偿：no_mount_reason 已落 HEAD（PG 正道）。
- ④依赖：depgraph 六节点在册（16427924/16427389/16427381 stable+16432500/16432496/16432491 generated，DatabaseService 实查）；翻译幽灵条目随码转真。
- ⑤冲突面：直投两连遭落袋战争 ref 竞态（gateway 报 OK 但 ref 被他会话占先，件仍 staged 零丢失）→ 改队列正门。
- ⑥残余：无。
- 单测：37 passed（13+12+12）。

### 袋C q-20261007-st-mastertc-recover-0003（C75 tech_factor_pipeline+单测）→ 队列 q-20261008-st-acure-r1-0003

- ①卡面：CNS-01 接线件（指标宽表→因子值面板→合成信号一键链，PIT 透传）+单测；字节全等（f69ffa96/451bd3b9）。
- ②死因：CREATE-GUARD 无 token。③清偿：token 已落 HEAD。④依赖：depgraph 16424134+16430419 在册。
- ⑤冲突面：无。⑥残余：消费挂载随 IC 跑批接线批补报。
- 单测：10 passed。

### 袋 final-0001（C122 桥等遗留面·缩面投递）→ 队列 q-20261008-st-acure-r1-0004

- ①卡面：C122 entity_graph_uscc_bridge+测试7、C156 check_registry_field_legality+测试5（create-guard-not-dup 逃生标记在档）、C324 reaper status 测试件；五件字节全等（28f053fa/6991711e/509486e6/f6f14b9e/715a4495）。
- ②死因：CREATE-GUARD MAP-MOUNTS（桥）。③清偿：no_mount_reason 已落 HEAD。
- ④缩面裁决：原袋 10 件中 L5_data 簿/qmine 簿/process_reaper.py/known_data_gaps.yaml/ext_05 设计稿五件已被他会话演进（字节≠袋档实证），投陈旧版=冲失他班成果禁投，留原车道重组。
- ⑤冲突面：reaper 测试对 HEAD 演进主件成立（实测定去留）。⑥残余：缩面五件移交原车道。
- 单测：桥 7 passed+校验器 5 passed+reaper 5 passed。

### 顺路处置（无主外来，台账留痕）

- src/zephyr/pf_alloc/core/portfolio_netting.py（staged 'A'，session registry 零在册属主）：__all__ Final 化修（safe_write_text CAS，after=25499358…）+py_compile 过——MUTABLE-CONST-WITHOUT-FINAL（own_scope=false 全量门）放行所需，按 FMS-HYGIENE"无主外来可顺路修"条款；件仍 staged 留其主车道成套落地（同批 blueprint/__init__/test 亦 staged），未随本班任何袋投递。

### 接管处置（TAKEOVER-PENDING 清偿，处方五件全执行）

- 前班化身（pid 42520 死亡）接管条目：stale claim gateway.release_files 精准释放后重 claim；worktree .aidrafts/st-acure-r1 dirty=0 无成果（留裁定通道）；心跳残件已清；死袋 q-0001 判废不 requeue；ledger --resolve st-acure-r1 --by st-acure-r1 已迁移 resolved/。

## 三、投递记录（每袋 ≤3 次铁律内）

| 袋 | 队列项 | 状态 | 单测读数 |
|----|--------|------|----------|
| token 袋（正道取代） | q-0001（dead: ghost_session，预期） | 被投影 render 正道取代 | 不适用 |
| 袋A | q-0002 | pending（车道优先） | 37 passed |
| 袋C | q-0003 | pending | 10 passed |
| final-0001 | q-0004 | pending | 7+5+5 passed |
| 本簿 | 待 token 落 HEAD 后投 | — | — |

## 四、OPEN_QUESTIONS（移交）

1. **落袋战争 ref 竞态**（本班直投两连丢：gateway 报 OK 但 ref 被占先，commit 对象孤儿化）：建议 Owner 门位评估"直投读后写原子性"——gateway commit 后 rev-parse HEAD≠自身时应报 COMMIT_RACE_Lost 而非 OK（本班两次假阳性 exit=0 靠 staged residual 异常+git log 核归属才发觉，宪法 §2.5 核归属纪律救命）。
2. **allow_overlap 24h 限额**：夜战多车道并发下 5 次限额易触顶；触顶后 lock_files 正道受 CLAIM-REQUIRED/他队活跃 claim 限制，队列成唯一出口（拥堵 29+ 时施工 AI 无速效通道）。
3. **REGISTRY-YAML-PARSE 指纹执法与 render 并发**：多车道同时 render+commit 时指纹互相失效（本班 5 连败根因）；宜文档化"render→commit 最小窗口"纪律或 gate 内重读 state。
4. **PG/YAML 双轨残余**：reconcile_registry 实跑 backfilled=0（G6 已追平），pg_only=1（本簿 token）待 publish；belt daemon 自带 reconcile 循环，暂无需人工。
5. **死袋档案更正**：q-20261007-st-mastertc-* 簇 dead_reason 所述"注册表漂移冲失"应更正为"投影化迁移期手改行非 PG 在册被合法 render 收敛"；死因治理对象=PG 意图 API 未普及，非会话互踩。
6. final-0001 缩面五件（L5_data 簿/qmine 簿/process_reaper.py/known_data_gaps.yaml/ext_05 设计稿）移交原车道按现势重组。

## 五、收尾核账

（传送带落地后填：q-0002/0003/0004+本簿 landed 哈希+git log -1 --name-only 逐袋核归属）
