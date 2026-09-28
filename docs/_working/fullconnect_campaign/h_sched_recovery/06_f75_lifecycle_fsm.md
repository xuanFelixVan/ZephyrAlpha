---
ttl: task_bound
title: F75 策略生命周期状态机（lifecycle FSM/词表对齐）——L08 复飞矿道案卷
session: zc-l08-20260927
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
4. **词表对齐层**：**无对应件——越界写入无拦截（本环节核心缺位，PR-B 3.6）**。

## 三、接线四态独立复核

- 总册 partial → **维持 partial**（PR-B 缺口重定位维持）。
- **骨架勘误（维持 PR-B 回写建议）**：partial 的真实差值非"FSM 未建"，而是：①production/shelved 越界写入（注册表词表无此二值，promotion_advisory.py:549+/:105 _DECISION_TARGET）②demote_decayed 语义分裂（治理词=decayed，FSM 落 shelved，decayed 成死态）③backtest/monitoring 两注册表态 FSM 无边。**死线=首个真实拍板日前必须清堵点 1/2，否则首例转正即写入词表外脏态**——与 F74 堵点 3（触达通道）联动后死线逼近。

## 四、缺口清单（PR-B 六缺口维持）

| # | 现象 | 处置 | 优先 |
|---|------|------|------|
| 1 | 词表对齐层缺位（三处硬伤） | 治理裁定二选一（FSM 映射 production→live+shelved 收编，或注册表收编 FSM 词）+双侧测试；首例拍板前死线 | **P0** |
| 2 | sim→decayed 衰减边缺位 | 随堵点 1 同批（加机器边+demote 目标态分支） | **P0** |
| 3 | 降级三档无 FSM 对应 | 挂实盘域（STD-LIVE-REDLINE-001 frozen 时同步） | P2 |
| 4 | 复活裁判未挂（regime 轮换复活语义） | 归 F73 联赛建库时定字段与裁判 | P1（邻域） |
| 5 | backtest/monitoring 两态处置 | w5_1 判据登记"不并"或补边，治理立案 | P2 |
| 6 | FSM 状态无独立持久化（by design，重建起点恒 candidate） | 词表对了重建语义自洽，随堵点 1 收口 | P2 |
| STALE 13/假绿 5 | **不属 F75**（归 F77 §四） | — | — |

## 五、自审闸三态

**部分挖干（复核维持）**：PR-B file:line 全证+三套词表逐值对照；本卷维持（F75 本体文件在盘未变，无当日新探针必要——decide 未曾发生=运行态无从变化）。三态=**partial 维持**。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
sed -n '59,63p;112,135p' src/zephyr/strategy_pipeline/lifecycle_fsm.py    # 五态七边
sed -n '56,60p' docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml  # 八态词表
grep -n "_DECISION_TARGET" src/zephyr/strategy_pipeline/promotion_advisory.py | head -3
python -m pytest tests/strategy_pipeline/test_lifecycle_fsm.py -q -o cache_dir=.runtime/tmp/pytest_cache_fullflow
```
