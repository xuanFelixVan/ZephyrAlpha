---
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# NE4_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# NE4 落地池基建卡点修复车道台账（第二夜总攻 Wave1）· 终稿
# sid=st-nightsweep2-ne4-20260930 总筹=st-nightsweep-chief-20260929
# 使命：k=4 落地池单工位 ~1.3h/项 卡点诊断+修复（Owner 已批排查授权 E4）

lane: NE4
session: st-nightsweep2-ne4-20260930
date: 2026-09-30
verdict: DONE-LANED(10aca61f22)

diagnosis:
  mission_hypothesis: GATE-PRECOMMIT-RUN 落地面前置 pre-commit run 子进程超时缺失
  verdict: 假设不成立——超时俱在（fast=300s / 全量=900s，fast_subset_ms=300031 实证钉死）；
    真病=超时后 fail-open 静默放行 + fast 超时后全量升级白付（双超时墙钟 1200s 零校验通过）
  evidence:
    - 账本面：4 工 landing_phase_stats 1444 例——gates 相位均值 423s/袋，
      总账 100.8h/173.4h（58%）；snapshot 43s 均值次之；sync/prestage 等均秒级
    - 通道面：precommit_channel_stats 552 例——p50=135s / p90=1201s / max=1212s；
      73 例（13.2%）双超时（fast 300s→全量 900s）后 infra_error=true 静默放行（门禁零执行）；
      79 例 infra_error 总计（14.3%）
    - 实证钉：w0 21:41:20 记录 total_ms=1201250 / fast_subset_ms=300031 / rc=-1 / infra_error=true
      （300s+900s=1200s 双超时结构自证）；修复挖矿中 w0 06:38 又添 total=1528s infra=true 实时实证
    - 慢袋挂账：bottleneck_ledger slow_item 最高 2219s；9/24 旧案 st-ailayer-final-0009
      total=4408s≈73min（mission 引的 53-73min 实证=该批，残差 4316s 已随 D7 装表收口）
    - 沙盘对照：pre-commit 纯框架开销 1.6s；Phase-A 快段 38 台逐台扫测无单台恶疾
      （最长 gate-frontmatter-audit 13.5s，多数 2-4s）——快段 40-130s/袋属 Windows
      38 台合法成本，调超时数值无收益，故不动 300/900
  why_slow_item_1_3h: 通道超时尾巴（1200s/1528s）+ gates 相位叠加 + 波次工熄火残留
    （pool_wave no_slot env_aborted 形态在案，D3 工不早退治本已落）

fix:
  what: 通道超时语义反转 fail-closed（判据/hook 集/超时数值零变化）
  where: src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py
    - _run_precommit_channel infra 分支分流：timeout 类→阻断（处方面=负载瞬态退避
      5-10min 后 requeue，连续超时报维护班）+ precommit_channel_timeout_block 审计事件
    - 非超时设施故障（pre-commit 不可用）保持 #341 fail-open 放行原语义
    - 回退手柄 env ZEPHYR_PRECOMMIT_TIMEOUT_FAILOPEN=1 一键恢复旧语义
  tests: tests/governance/test_commit_chain_campaign_20260922.py +3 例
    （超时阻断/回退手柄/非超时边界）——册共 32 绿；网关册 102 绿；ruff 双净
  avoided:
    - commit_queue_landing.py 他会在飞（git status MM 实证）→ 避让未动；
      landing 侧瞬态退回（LandingEnvironmentError 映射）留处方卷战役 Wave2 提案
    - 修复袋拒袋走死信+处方面（dead_letter_prescription+requeue 可复位），合规可见
    - 与提速批 wave2（7a4a7c9f24 gate-test 增量化 / 57ba32b227 锁退避+banner 尾读）
      同文件组合复验 32 绿，零冲突

before_after:
  before: 552 例通道 p50=135s / p90=1201s；73 例零校验放行（双超时 1200s 白付+破防）；
    活窗加样 w0 06:38 total=1528s infra=true
  after_activated_at: "2026-09-30 07:50（belt daemon os.execv 自愈重启 pid 17336→23572，
    HEAD tree 变更触发——非人工 kill，daemon 自带治本机制）"
  after_observed:
    - 通道运行 3 例：155s / 151s / 181s，rc 全正常，infra_error=0
    - 落地袋样本：22s / 25s / 217s / 420s（420s 例 snapshot=251s 主导，gates 仅 148s）
    - timeout_block 事件 0（窗口内无超时发生——尾部事件，行为已由 3 单测钉死）
    - 零校验放行=0（修复后窗口）
  honest_note: 本修不改成功路径成本（绿路径时长不变）；收益=1200s+ 隐形尾巴转为
    可见拒袋+处方（快速反弹、负载窗退避重投）+零校验放行归零；p50 进一步下降
    依赖处方卷战役 wave2（gate-test 收集域收窄等）互补推进

belt_health:
  - 06:15 heartbeat age=779s（波间空闲，非死亡）；07:50 起持续 age<30s
  - 06:41:02 w3 no_slot env_aborted=True（LandingEnvironmentError 终止波）——只记录未干预
  - 07:11-07:16 233 管道断裂大疫：9 会话 14+ 袋同因死信（含本车道 0001/0002），
    st-c9-final 3992e4b02/st-c9-f92 1a77e16148 同窗披露互证——环境级故障，值班/维护班域，
    本车道零干预，后续自愈
  - serializer lease 活体全程；reaper last_run 正常；零 kill

bags:
  fix_landing:
    qid_history: 0001(dead,233 疫情)→0002(dead,233 疫情)→0003(done但 noop，
      serializer 清暂存致快照=HEAD 旧版)→0004(done)
    landed_id: 10aca61f22cf4d8d3ffb1e48338efbb30b9e817f
    landed_at: "2026-09-30 07:51:05+08:00"
    files: 2 (git_commit_gateway.py + test_commit_chain_campaign_20260922.py)
    ownership_check: git show --name-only =恰 2 文件零吸收；HEAD 内容双 marker 在位
    content_recovery: 0003 noop 后内容经本会话编辑史确定性重放（4 hunk 逐字），
      0004 入队 blob 双件 HAS_MY_FIX=True 复验后落袋（3117cdd4 死袋恢复直提先例同款）
    verdict: DONE-LANED(10aca61f22)
```
