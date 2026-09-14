---
ttl: task_bound
---

# 复活观察跨域协议 v1.0（图形域试点产物 → 策略/因子域接线规范）

> 产线：反过拟合自动认证方案 v1.0 续（Owner 令"全项目所有会衰减的东西都要有捞回机制"）。
> 图形域参考实现=MOD-SIG-149 pattern_lifecycle（本目录 resurrection-watch-plan.md）。

## 1. 统一生命周期（跨域状态词汇表）

```
candidate → active ⇄ probation → failed → retired(statistical|structural)
                                  ↑            │ 死后观察期
                                  └─ resurrected┘（复活闸通过）
resurrected 再失败满 RESURRECT_MAX_ATTEMPTS 次 → frozen（仅 Owner 门位解冻）
```

## 2. 接线四要素（各域按自身证据源适配）

1. **死后观察台账**：退役时登记死亡快照（退役日/当时主统计量/基线/死因分类）；
   退役后证据机器**继续**为该对象产出统计（数据不删=复活证据自动生长）；
2. **复活闸**：死后增量重跑本域认证判据，阈值**高于**初次认证（序贯 α 消耗：
   O'Brien-Fleming/Lan-DeMets——越早越保守，第 1 次 p<0.01、第 2 次 p<0.005）；
   增量样本门槛（图形域=n_new≥50，各域按事件频率预注册）；
3. **死因分类**：statistical（自动复活通道）/ structural（监管/数据源/机制变化→
   冻结自动复活，仅 Owner 门位）——死因登记强制；
4. **尝试预算**：复活失败满 2 次 → frozen，防"年年重测总有一年碰巧显著"。

## 3. 纪律（不可协商）

- 复活判据与阈值**预注册**（写进各域蓝图），改动=裁定留痕；
- 认定代码生成禁手填；运动员不兼任裁判（认证器只读统计）；
- structural 死亡对象对自动复活免疫——机器看不出游戏规则变了。

## 4. 图形域参考实现指针

- 状态机+死亡快照+复活闸：src/zephyr/signal_ashare/strategy_signal/pattern_lifecycle.py
- 台账：data/runtime/pattern_lifecycle_state.json（LifecycleStore safe_write CAS）
- 链序：marketize → certify（148 四闸）→ lifecycle 覆盖（149）→ weight_sync（failed/retired 不调权）
