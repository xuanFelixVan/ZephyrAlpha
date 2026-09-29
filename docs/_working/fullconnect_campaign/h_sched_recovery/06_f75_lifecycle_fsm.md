---
ttl: task_bound
title: F75 策略生命周期状态机（lifecycle FSM/词表对齐）——L08 复飞矿道案卷
session: zc-l08-20260927
updated: 2026-09-29
---

# F75 · 策略生命周期状态机

> 总册行：H 段 F75，状态 partial，P1，挂 REG-STR-001。
> 本卷=09-27 复飞复测。基册=03_promotion_ab/04_lifecycle_fsm.md（PR-B 09-25 挖干，缺口重定位=词表对齐层缺位）。

## 一、六向台账（实证锚点）

| 向 | 内容（PR-B 证+本日文件复核） |
|----|------|
| 上游输入 | intake.py auto_intake 批内 candidate→sim（:319/:165-171）；PA-1 三条件实据（promotion_advisory.evaluate_sim_preauthorization :341）；Owner token（ZEPHYR_OWNER_APPROVAL_TOKEN） |
| 下游消费 | strategy_registry.yaml lifecycle_status（唯一持久真源，CAS）；decision 台账；_transition_lifecycle（:614）；daily_decision_orchestrator S4 已毕业包集（现空=安全态，裁定#305） |
| 自动化触发 | FSM 是库无自触发；流转两类=intake 批内自动（candidate→sim）+Owner 拍板 decide()（sim→production/shelved）；shelved→candidate/retired 机器边无发射方 |
| 真源与注册表 | lifecycle_fsm.py MOD-BT-188（复用 shared/lifecycle/state_machine.py 泛型基类）；注册表八态词表=strategy_registry.yaml schema:58（candidate/backtest/sim/paper/live/monitoring/decayed/retired）；骨架 §6 生命周期轴 |
| 门禁与质量尺 | SimPromotionGuard（三条件∧，无 context=False fail-closed）；OwnerTokenGuard（sha256 常量时间+未配置/空串拒）；candidate→production 无直连边；非法转换抛 InvalidTransitionError；MODIFY-GUARD=tests/strategy_pipeline/test_lifecycle_fsm.py |
| 当前运行状态 | **黄（维持）**：本体绿（五态七边+双 guard+测试在盘）；注册表 163 条目全 candidate/sim 两态（production 从未达成=转正从未发生）；词表对齐缺口=三套词表并存（FSM 五态/注册表八态/联赛 champion-challenger） |

## 二、子模块三级枚举（PR-B 六件维持）

1. **FSM 本体**：candidate/sim/production/shelved/retired 五态七边（lifecycle_fsm.py:112-135，边表 :123-131）。
2. **双 guard**：SimPromotionGuard（:66-84，PA-1 治本后实据评估迁 promotion_advisory 侧）；OwnerTokenGuard（:87-109）。
3. **消费方**：intake 自动流转（intake.py:128-/:165-171/:319；registry_writer.append_entries :170 CAS）；拍板流转执行（promotion_advisory.py:614-652，promote 先补走 c→sim 再 s→p，demote 走 c→sh 无守卫边）。
4. **词表对齐层**：**无对应件——越界写入无拦截（本环节核心缺位，PR-B 3.6）**。**〔过时标记 2026-09-29：词表单源件已落（909de5192c 裁定#417 配对袋），但写入侧接线缺=半落地，见卷末刷新批注〕**

## 三、接线四态独立复核

- 总册 partial → **维持 partial**（PR-B 缺口重定位维持）。
- **骨架勘误（维持 PR-B 回写建议）**：partial 的真实差值非"FSM 未建"，而是：①production/shelved 越界写入（注册表词表无此二值，promotion_advisory.py:549+/:105 _DECISION_TARGET）②demote_decayed 语义分裂（治理词=decayed，FSM 落 shelved，decayed 成死态）③backtest/monitoring 两注册表态 FSM 无边。**死线=首个真实拍板日前必须清堵点 1/2，否则首例转正即写入词表外脏态**——与 F74 堵点 3（触达通道）联动后死线逼近。

## 四、缺口清单（PR-B 六缺口维持）

| # | 现象 | 处置 | 优先 |
|---|------|------|------|
| 1 | 词表对齐层缺位（三处硬伤）**〔09-29 单源件已落、接线缺=半落地，见刷新批注〕** | 治理裁定二选一（FSM 映射 production→live+shelved 收编，或注册表收编 FSM 词）+双侧测试；首例拍板前死线 | **P0** |
| 2 | sim→decayed 衰减边缺位 **〔09-29 FSM 本体侧兑现、调用侧接线缺=半落地，见刷新批注〕** | 随堵点 1 同批（加机器边+demote 目标态分支） | **P0** |
| 3 | 降级三档无 FSM 对应 | 挂实盘域（STD-LIVE-REDLINE-001 frozen 时同步） | P2 |
| 4 | 复活裁判未挂（regime 轮换复活语义） | 归 F73 联赛建库时定字段与裁判 | P1（邻域） |
| 5 | backtest/monitoring 两态处置 | w5_1 判据登记"不并"或补边，治理立案 | P2 |
| 6 | FSM 状态无独立持久化（by design，重建起点恒 candidate） | 词表对了重建语义自洽，随堵点 1 收口 | P2 |
| STALE 13/假绿 5 | **不属 F75**（归 F77 §四） | — | — |

## 五、自审闸三态

**部分挖干（复核维持）**：PR-B file:line 全证+三套词表逐值对照；本卷维持（F75 本体文件在盘未变，无当日新探针必要——decide 未曾发生=运行态无从变化）。三态=**partial 维持**。**〔过时标记 2026-09-29："本体文件在盘未变"已失效——909de5192c+8033a3de49 两批改本体，且 HEAD 出现 3 红测试新开口，见卷末刷新批注〕**

## 刷新批注（2026-09-29 st-finaldel-freshb）

> 刷新基线：HEAD dev @ 0cacd4a64d（09-29）；对卷内真源跑 `git log --since=2026-09-28` 复核＋码面现读＋测试实跑。**本卷为半落地型刷新（件落、线未接），非全翻面。**

- **落地 commit（两件）**：
  - `909de5192c`（09-28，裁定#417 配对袋·词表单源化四件）：单源件 `src/zephyr/shared/lifecycle/registry_state_vocab.py`（FSM_STATE_TO_REGISTRY_STATE :77）落盘，`lifecycle_fsm.py` 消费接线 import+`REGISTRY_LIFECYCLE_ALIASES` 投影定义（:70-74，"FSM 词 production 写注册表时恒映射 live"）——卷 §二.4"词表对齐层无对应件"过时（件已在盘）。
  - `8033a3de49`（09-29 07:24，F75 缺口2·demote 真实边）：`build_strategy_fsm` 增 `initial_state` 参数（:125，非法值 ValueError fail-closed，默认 CANDIDATE 全兼容）+ SIM→SHELVED 真边在边表（:151 实锚）——缺口2 的 FSM 本体侧兑现。
- **本刷新实测的半落地缺口（新增红证）**：
  - **调用侧接线缺**：8033a3de49 提交说明声称的"②promotion_advisory._transition_lifecycle demote 分支按 lifecycle_now 起步走真实边"**未随 diff 落盘**（该 commit 只改 lifecycle_fsm.py+两测试件）；HEAD 现读 `promotion_advisory.py:687` 仍 `build_strategy_fsm(sid)`（未传 initial_state）。
  - **写入侧映射缺**：`REGISTRY_LIFECYCLE_ALIASES` 在注册表写入路径（decide→CAS 手术）无消费点，production→live 映射未生效。
  - **HEAD 测试 3 红（本日实跑）**：`test_promotion_advisory.py` 3 failed/26 passed——`test_demote_approve_flows_to_shelved` 断言 `from=sim` 实得 `from=candidate`（candidate 假起步缺陷仍在生产路径）；production→live 注册表映射断言红。**测试口径先行于生产接线=典型半落地。**
- **缺口状态修订**：缺口1 P0→**半落地**（单源件+投影定义在盘；写入侧映射接线缺）｜缺口2 P0→**半落地**（本体 initial_state 件在盘；调用侧接线缺；sim→decayed 目标态边仍未落，`_DECISION_TARGET` demote 仍=shelved :107）｜缺口3-6 维持。
- **自审闸三态（刷新后）**：**partial（维持且开口具体化：从"无对应件"收窄为"两侧接线各差一米"+HEAD 3 红测试）**——**首例真实拍板前死线条款依旧有效且更紧**（现拍板即触发词表外写入/假起步回执）；收口施工=①promotion_advisory 传 initial_state=lifecycle_now ②注册表写入侧接 REGISTRY_LIFECYCLE_ALIASES ③3 红测试转绿，均为小施工。
- **复跑**：`sed -n '70,74p;125,134p' src/zephyr/strategy_pipeline/lifecycle_fsm.py`（投影+initial_state）｜`grep -n "build_strategy_fsm(" src/zephyr/strategy_pipeline/promotion_advisory.py`（:687 无 initial_state=接线缺实证）｜`python -m pytest tests/strategy_pipeline/test_promotion_advisory.py -q -o cache_dir=.runtime/tmp/pytest_freshb`（3 红）。

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
sed -n '59,63p;112,135p' src/zephyr/strategy_pipeline/lifecycle_fsm.py    # 五态七边
sed -n '56,60p' docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml  # 八态词表
grep -n "_DECISION_TARGET" src/zephyr/strategy_pipeline/promotion_advisory.py | head -3
python -m pytest tests/strategy_pipeline/test_lifecycle_fsm.py -q -o cache_dir=.runtime/tmp/pytest_cache_fullflow
```
