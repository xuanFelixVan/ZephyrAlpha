---
ttl: task_bound
---

# [BLUEPRINT] | docs/_working/pattern_line/resurrection-watch-plan.md |
<!-- [MODULE] MOD-SIG-149 -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] M -->

# 复活观察机制方案 v1.0——"死→观察→复活"生命周期闭环（图形域试点，2026-09-15）

> 状态：**v1.0 冻结待施工**。缘起：Owner 问"毙掉的东西能不能捞回来？衰减的东西
> 是不是全项目都需要捞回机制？"裁定：立项，图形域先行试点（数据管道全自动现成），
> 跑通完整案例后协议文档交策略/因子域接线。

## 一、核心洞察：退役日=天然无偏样本起点

我方"死"是状态不是删除：退役后检测照跑、事件照记。退役后积累的数据对该形态
是**干净的样本外证据**（死前任何数据作弊都不影响死后表现）——复活判定 therefore
只需在死后增量数据上重跑统计，无需人为"再试一次"。

## 二、机制设计（图形域试点）

### 生命周期状态机（MOD-SIG-149 pattern_lifecycle）
```
certified/probation/failed（148 每日产出）
  failed 连续 RETIRED_AFTER=20 个物化窗 → retired（登记死因快照）
  retired → 死后增量过复活闸 → resurrected（重入正常周期）
  resurrected 再连续 20 窗 failed → 二次退役；复活失败满 2 次 → frozen（Owner 门位解冻）
```
- **死因强制分类**：`statistical`（统计性，可自动复活）| `structural`（结构性：
  制度/数据源/规则变化，冻结自动复活，仅 Owner 门位）| 默认 statistical；
- 死亡快照：retired_at、当时 n_events/hit_rate/基线（复活检验的对照原点）；
- 台账 JSON 持久化（data/runtime/pattern_lifecycle_state.json，safe_write CAS，
  tmp_path 注入测试）；retired 状态回写认证表（前端自动显"退役"徽章）。

### 复活闸（比初次认证更高，序贯校正）
- 数据：死后增量 = 当前统计 − 死亡快照（n_new、hits_new 近似，口径声明）；
- 判据：**单侧二项检验 p < 0.01**（对基线）且 **n_new ≥ 50**；
- 序贯 α 预算（O'Brien-Fleming/Lan-DeMets 谱系：越早越保守）：第 1 次复活
  p<0.01，第 2 次 p<0.005；**复活失败满 2 次 → frozen**（尝试预算封顶）；
- 观察下限：死后成熟新事件 <50 个不判定（不猜）；
- 复活试验计入多重检验家族预算（每次尝试=一次额外的 look，阈值按上表收紧）。

### 链序与消费
- 链序不变：materialize → certify → weight_sync；lifecycle 更新在 certify 落表前
  执行（单写手：retired 覆盖当日三态，避免双写者打架）；
- 消费：weight_sync 对 retired 不调权（不录样本）；前端徽章四态
  认证/观察/未过/退役。

## 三、阈值预注册（改动=裁定留痕）

RETIRED_AFTER=20 ｜ 复活 p<0.01（二次 0.005）｜ n_new≥50 ｜ 尝试预算 2 ｜
死因分类 statistical/structural。梯子先例：O'Brien-Fleming 1979/Lan-DeMets 1993
（越早越保守的序贯 α 消耗）。

## 四、挖矿日志

| 轮 | 矿脉 | 判定 | 关键产出 |
|---|------|------|---------|
| R1 | 策略复活/衰减 | 部分 signal | Quantpedia 发表后衰减研究（收益淡化不消失=衰减-复活循环概念锚）+QuantEvolve arXiv 2510.18569（"跨 regime 长期存活"框架）；**无现成"复活协议"术语=自研但邻域有锚** |
| R2 | 序贯检验 α 预算 | **signal** | Lan-DeMets 1993 alpha spending+O'Brien-Fleming 1979（重复检验的保守边界，早期几乎不花 α）→ 复活重试门槛收紧的统计依据 |

终止：两轮双 signal，矿已见底（复活协议无业界现成真源=自研设计，判据全部锚定
既有统计正统）。

## 五、施工与验收
- pattern_lifecycle.py（MOD-SIG-149）+certifier 接线（单写手覆盖）+前端退役徽章；
- **验收案例（合成）**：单测模拟 45 个物化窗：certified→20×failed→retired（快照落）
  →死后增量 48/60 vs 0.5 基线（p≈1e-4<0.01）→resurrected→20×failed→二次退役
  →再复活→再失败→frozen——全循环在代码路径上跑通；
- 真实首跑：现存 56 个 failed 切片开始连续窗计数（真实 retired 最早约一个月后产生，
  届时死后观察自动生长）；协议文档交策略/因子域。
