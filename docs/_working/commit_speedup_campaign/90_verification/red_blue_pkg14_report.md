---
title: 包14 红蓝极限对抗报告（提交链治本夜战 7 场景）
session: st-commitspeed-tbl-20260924
date: 2026-09-26
lane: red_blue_pkg14
ttl: task_bound
---

# 包14 红蓝极限对抗报告（7 场景）

对抗原则：**每把尺先证明能红**（恒绿尺=无效尺）；全部对抗在 throwaway 沙盒
（tmp git 仓 + tmp 队列根 + 独立进程 / git 对象只读提取），零触碰生产活体。
红方"旧码复活器"=产品文件字节副本经锚定文本手术+importlib 独立装载
（每次手术断言产品文件 sha256 前后全等，防手术污染）。

## 0. 结果矩阵

| 场景 | 尺 | 红证（能红证据） | 蓝方结果 | 判定 |
|------|----|------------------|----------|------|
| S1 杀工复活（D3） | 单工异常→记档续跑/连错20收工/硬杀复活 | 旧码副本（首错即 raise）下 done=0、余件无人认领 | 瞬态单错全落地+streak 记档；恰 20 连错 GIVEUP；成功重置 streak；独立进程 os._exit(9) 硬杀→遗孤复活收齐零双落 | PASS |
| S2 双写者同路径 | B4 FIFO/C1 合批/路径锁/done==件数 | ①旧排序规则（qid 字典序）选错队首；②D4 手术副本（去 done 复查）幽灵二次 done（done 事件/qid=2） | created_at 序不倒挂；C1 并集+absorbed qid 零落状态目录；跨会话同路径零覆盖死信（prescription 在册）；幽灵被认领侧清除 | PASS |
| S3 故障注入 | 死信路径干净/无静默假绿 | ①环境失败走死信（09-10 事故旧语义副本）；②假绿状态写产出缺 landed_id 的 done 件 | git 锁占用→退回 pending+attempts+1 终止轮；landing 崩→死信+处方+不卡队；ENOSPC→大声抛出+重跑自愈 | PASS |
| S4 伪造与绕门 | POST-COMMIT-GUARD reset/D2 无旗残留 | ①W1 前副本 `_trusted_git_env` 旗渗入；②D2 步2 前副本 commit 调用无 internal_call 声明 | 手写 [GW:未注册sid] 裸 commit 被 reset+审计 forged_gw_marker；正门控制合法保留；外部调用（internal_call=False）提交成功后进程环境零旗残留；landing 全调用点 internal_call=True 动态取证 | PASS |
| S5 缓存投毒 | T7/B2 新键三连毒 | worktree 现行中间形态（df8507ac9b）对门源码毒**不判失**（攻击窗实证） | cb3c13b74f（dev 收口）门源码毒 miss/注册表毒 miss/HEAD 推进仍 hit+own 内容毒 miss | PASS（含发现 F-14-2） |
| S6 饿死与独占 | FIFO 不倒挂/C1 生效/毒药退避 | 关掉 B5 退避（产品自带 kill switch）→ 最老毒药件重新垄断队首 | 超大袋+5 小袋灌入落地序==到达序；attempts=4 退避让位、attempts=5 拾取即死信不白耗 landing；4 次小袋 C1 合 1 袋 | PASS（含缺陷 D-14-1） |
| S7 跨道连坐 | own-scope 隔离 warn 不阻断 | 旁路 own-scope 拆分（全量扫描旧形态）→ 外来违规连坐无辜提交人（门红） | own/foreign 拆分+外来审计 jsonl；真实门 NO-BARE-GETENV 在"外来违规、本件干净"下 passed=True；池化两车道各触自身文件零污染 | PASS |

复跑收口：`tests/governance/red_blue_pkg14/` **37 passed**（D3 同步后复跑）；
队列族回归 `test_commit_queue*` 7 套 **161 passed**。

## 1. 每场景要点

### S1 杀工复活（D3）
- 攻击：①认领段 per-worker 单次 RuntimeError；②持续异常；③`os._exit(9)` 硬杀独立 serializer 进程（非 belt，临时队列根）。
- 红证：手术副本把 `_worker` 两处 `err_streak>=20 → return/continue` 改 `raise`（=D3 前首错工死），同攻击 done=0（对照新码 done=3），与决策志 09-24 判别实验同形。
- 蓝方：`pool_wave.log` 就地记档（claim_raised streak=N）；GIVEUP 恰在第 20 连错、19 不出现；成功重置计数（19 错+成功+19 错→无 GIVEUP 全落地）；硬杀后遗孤 `_recover_orphans` 复活、dev 每文件恰 1 次提交。

### S2 双写者同路径（B4/C1/D4）
- 攻击：两会话同路径并发 enqueue（Barrier 同步）；构造 created_at 与 qid 字典序交错的到达序；同 qid 幽灵 pending（blob 换 v2、基底同步 dev）。
- 红证：旧排序在构造样本下队首选新件；D4 手术副本（`(root/"done"/head.name).exists()` 前缀短路）令幽灵二次 done。
- 蓝方发现的产品语义（非缺陷）：跨会话同路径=语义冲突，后件零覆盖死信回属主会话（66 号 §6.4/§9.1），死因+prescription 如实；路径锁体零重叠（overlap guard 实证）。
- 判据口径：done 事件/qid 恒等于 1（done 恒等于件数的完整形态）；landing 幂等三判（marker grep）为内容层第二道防线，红方旧码亦攻不破。

### S3 故障注入
- 攻击：①landing 抛 LandingEnvironmentError（index.lock 特征串）；②landing 抛 RuntimeError/返回 GATE-IMPORT-FAILED；③`_atomic_write` 注入 ENOSPC；④假绿 writer（吞 OSError 假装写）。
- 红证：旧语义副本（env 失败落普通死信）下"环境失败不死信"尺红；假绿 writer 实证产出缺 landed_id/landed_at 的 done 件（蓝尺的靶子）。
- 蓝方：env 失败退回 pending+attempts+1+last_failure 留痕；死信带 reason/prescription/owner_session 且不卡队；ENOSPC 大声抛出、重跑 `recovered=1` 收齐。

### S4 伪造与绕门
- 攻击：手写 `[GW:rb14-ghost-sid]`（未注册 sid）+`git commit --no-verify`（一次性沙盒仓+逐字节复制的真 post_commit_guard.sh+生产口径扁平注册表）。
- 蓝方：guard 判伪造 → `reset --soft HEAD~1`（HEAD 回退、改动回暂存、审计 violation=forged_gw_marker）；正门控制（注册键+GW env）保留。
- D2 三步验证：步1 gateway.commit 收 internal_call（缺省 False，外部调用可用且提交后 `ZEPHYR_COMMIT_GATEWAY` 零进程环境残留）；步2 landing 两调用点动态取证 internal_call=True（池化桩 gateway 截获 kwargs）；步5 `_trusted_git_env` 显式剔除 GW 旗且不动进程环境。
- 红证：W1 前副本（无 pop）旗渗入落地 plumbing 域；D2 步2 前副本（删 internal_call 实参）桩取证缺声明。

### S5 缓存投毒（T7/B2 新键）
- 攻击（三连毒）：改门源码一字节/改注册表字节/推进 HEAD，另加 own staged 内容一字节。
- 蓝方真源：**cb3c13b74f**（dev 已收口形态：spec_sha+GATE_INPUT_MANIFEST）以 `git show` 只读提取 blob→tmp 副本→独立模块名装载；门源码毒 miss、注册表毒 miss、还原可逆回 hit、HEAD 推进仍 hit、own 内容毒 miss。
- 红证：本 worktree 现行中间形态（df8507ac9b，键缺 spec_sha/manifest 分量）对门源码毒不判失——门源码修复/篡改后 10min TTL 内旧 passed=True 继续放行（投毒窗）。HEAD 毒在中间形态已防住（键不含 head_sha 是 df8507ac9b 的功劳）。

### S6 饿死与独占（B4/B5/C1）
- 攻击：超大袋（35 文件）+持续他会话小袋灌入；attempts=4/5 毒药件占最老位；产品自带 kill switch（`ZEPHYR_CQ_ATTEMPTS_BACKOFF=0`）作红方杠杆。
- 蓝方：落地序==created_at 序（35 文件集零丢失）；毒药退避=未来时刻让位新件；attempts≥5 拾取即死信不白耗 landing、同轮后续件照常落地；4 次同会话小袋 C1 合 1 袋（absorbed qid 零落状态目录）。
- 红证：退避关闭后最老毒药件重新垄断队首（饿死回潮形态复现），恢复退避即让位——同一构造两态相反，尺有判别力。

### S7 跨道连坐
- 攻击：车道 A 暂存干净件+车道 B 暂存裸 `os.environ.get` 违规件同暂存区；旁路 own-scope 拆分（monkeypatch `_split_own_foreign` 为全量透传）复现旧形态。
- 蓝方：`_split_own_foreign` own/foreign 零交叠+外来审计 jsonl（gate 名派生、归因字段在册）；真实门 NO-BARE-GETENV 对无辜提交人 passed=True 且审计点名外来件；空 scope 退化全量（保守面不改宽）；池化两车道并行落地每工 commit 只触本车道文件。

## 2. 发现的缺陷与处置

| 编号 | 级别 | 发现 | 处置 |
|------|------|------|------|
| D-14-1 | 缺陷（已修已落地） | `scripts/commit_queue.py` drain_queue 的 B5 attempts 耗尽死信出口**缺 prescription/owner_session**（M3.3 口径在 pool 支 R2-P1-2 已补三出口、drain 支同形态出口漏配；dev 亦未修，S6 红蓝实测抓到） | 已修并落地 dev=**bd8ba4d85a**（恰 6 行；S6 转绿；队列族回归 161 passed；落地前在 dev tip 字节上预验 S6 4/4+B5 14/14） |
| F-14-2 | 状态勘察（非新缺陷） | 本 worktree（csx-pkg5b）基于 df8507ac9b，**未含包7收口件 cb3c13b74f**（spec_sha/GATE_INPUT_MANIFEST 缺席）→ S5 三连毒的前两毒在该形态上不设防（仅本分支意义；dev 已封） | S5 蓝方以 dev blob 为真源验证通过；worktree 与 dev 的同步属会话收尾 merge 义务，本包不越权代并；知会总包 |
| F-14-3 | 观察项（未修） | `drain_queue_pool(max_items=N)` 的预算预扣语义：认领异常重试每次也预扣名额，持续异常会把预算耗光、提前收工留 pending（S1 调参时实测 done<件数现象）。产品语义=软上限+下轮自举自愈，未见内容丢失 | 登记 观察项；如需收敛可在后续包把"异常重试不预扣"与"预算耗光留 pending 告警"立项 |
| F-14-4 | 观察项（未修） | S2 实证跨会话同路径=死信回人工（解法=同步工作区后重新入队），路径锁只保证"互踩不可能"，不合并语义冲突——按 66 号 §6.4 属正确行为 | 无需修；处方链路已在（S2 断言 prescription 在册） |
| F-14-5 | 缺陷（已修已落地） | `_pool_wave_log` k 工并发 append 无锁=行丢失（S1 giveup 尺跑出 GIVEUP 计数 39/40，A3 装表取证面失真；只记不判语义不受影响） | 已修并落地 dev=**0a5b0569b9**（进程内锁 4 行；修复后 S1 giveup 连跑 6/6 全绿） |
| F-14-6 | 可移植性处置 | 证尺 7 例与检出基底绑定：S4 六尺依赖 D2 步1/2/5（在途=csx-pkg5b 未提交件）、S5 中间形态红证依赖 df8507ac9b 基——dev tip 直跑会 7 失败 | 已改 skipif 基座探针（D2 三标足迹/`_spec_sha` 在场探针），skip 原因均指认属主批；D2/包7 落地后自动启用 |

## 3. 红线遵守声明

- 未运行 `tests/governance/test_ops_guard_red_team.py`（地雷回避；S4 判据以沙盒实弹替代）。
- 未 kill 真 belt/reaper/任何生产进程；未写真队列目录与真 dev（S1 独立进程用例全部指向 tmp 队列根）。
- 无裸 git commit/plumbing/插队；红方手术全部在 tmp 字节副本上，产品文件 sha256 前后全等断言逐例在册。
- 未改任何门禁判据阈值；S5 的 manifest 注入只作用于 tmp 副本/本进程模块对象。
- 同失败 3 次跳过条款未触发（无场景达到 3 连败）。
- 唯一产品码改动=§2 D-14-1 修复（含 `scripts/commit_queue.py` 与 dev 的 F1 件先同步再叠加，避免旧基底整文件快照落地事故）。

## 4. 落地袋登记（队列正门）

| 袋 | 域 | 文件 | 结果 |
|----|----|------|------|
| 0154/0155 | scripts | scripts/commit_queue.py（D-14-1 修复） | 死信×2：落地工棚册账字段 stale（total_gates 99，装载数 102）——M5.2 确定性判别，非本袋内容问题 |
| （工作树账实复原） | registry | 本 worktree 的 in_process_gate_registry.yaml `total_gates: 99→102`（safe_write_text CAS；仅修本工作树环境，**不入袋**——dev 名册已自洽 103，落本件反成回退） | 环境复健 ✅ |
| 0156 | scripts | 同修复（旧基底快照） | 死信：基底 9120a7aafc 落后 dev（F1 等已在 dev 推进同路径）＝逐文件快进判定按设计拦下 |
| 0157 | scripts | scripts/commit.py 同修复，改以 **dev tip 快照**（一次性 detached worktree@dev，修复后 S6 4/4+B5 14/14 预验）入队 | **已落地 dev=bd8ba4d85a**（恰 6 行） |
| 0160 | tests（token 豁免） | tests/governance/red_blue_pkg14/ 全件（10 文件） | **已落地 dev=8b6c351c58** |
| 0161 | docs | 本报告+token 先行（commit_speedup_campaign_rb14） | **已落地 dev=ee02f45b66** |
| 0162 | scripts | F-14-5 记档锁修复 | **已落地 dev=0a5b0569b9** |
| 尾袋 | tests+docs | 证尺基座自适应（F-14-6 skipif）+本报告 F-14-5/F-14-6 补记 | 见 status |

死信处置实录：0154→换新袋 0155（复健册账后仍死＝判明第二因基底落后）→0156（换 dev
tip 快照源）落地。全程零改门禁判据、零插队、零触碰生产活体。
