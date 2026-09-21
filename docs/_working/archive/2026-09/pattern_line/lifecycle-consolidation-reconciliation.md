---
ttl: task_bound
---

# [BLUEPRINT] | docs/_working/pattern_line/lifecycle-consolidation-reconciliation.md |
<!-- [MODULE] MOD-SIG-149 -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] M -->

# 两线合并对账报告——st-patmine 生命周期线 × st-automount C6 入库线（2026-09-15）

> 缘起：Owner 令"现在就做两线合并对账"。对账范围=并发期两家各自落地的策略生命周期
> 机器：本线（MOD-SIG-148/149/150）× st-automount 线（MOD-BT-187/188/189 +
> strategy_lifecycle_advisor）。

## 一、模块清单与判定

| 模块 | 归属线 | 职责 | 与对侧关系 |
|------|--------|------|-----------|
| bh_fdr.py（MOD-BT-187） | automount | 策略入库批 BH-FDR 门（dict 接口+逐条报告） | **FDR 第三实现**（见 §二单源裁定） |
| lifecycle_fsm.py（MOD-BT-188） | automount | 晋升 FSM：candidate→sim→production(Owner门)→retired + shelved 侧枝（复用 shared.lifecycle.state_machine 框架） | **与 149 不同轴**（见 §三词汇映射） |
| intake.py（MOD-BT-189） | automount | 入库编排（fail-closed 待验收⑥ Owner 复核后开启） | 无重叠（晋升侧专属） |
| strategy_lifecycle_advisor（scripts/backtest） | automount | 流转建议器：IS/OOS 衰减→decay_watch/reject/candidate/hold（只建议不终裁） | **与 MOD-SIG-150 部分重叠**（见 §四边界裁定） |
| pattern_evidence_certifier（MOD-SIG-148） | patmine | 图形切片四闸认证（BH-FDR/n_eff/分regime/收缩） | FDR 同族（§二） |
| pattern_lifecycle（MOD-SIG-149） | patmine | 图形衰减/复活覆盖层（certified/probation/failed/retired/resurrected/frozen） | FSM 不同轴（§三） |
| strategy_decay_certifier（MOD-SIG-150） | patmine | 策略衰减侧判定（DS 三态+连周退役建议+复活，台账制） | **与 advisor 部分重叠**（§四） |

## 二、FDR 三实现单源裁定

现存在三份 BH 族实现：148 `bh_adjust`（list 接口，图形切片族）、factor 域
`bhy_fdr`（BHY 任意依赖稳健版，numpy，含测试）、automount `bh_filter`（dict 接口
+逐条报告，策略入库批）。

**裁定**：
- **canonical=bhy_fdr**（BHY 依赖稳健+预注册阈值真源 90 号 §2+有测试），新增
  跨域认证需求一律导 bhy_fdr；
- 148 `bh_adjust` 保留（图形切片族已上线依赖），标注"收敛待办：换 bhy_fdr 底座、
  接口适配层过渡"；
- automount `bh_filter` 保留（intake 待验收⑥，不可动），验收通过后同上收敛；
- 三实现语义一致（BH step-up），差异仅在依赖校正（BHY c(m)=Σ1/i vs BH c=1）——
  收敛时以 BHY 为准（策略批内因子/策略常相关）。

## 三、FSM 词汇表对齐（两轴正交，映射表钉死）

两台 FSM **不同轴不冲突**，但 "retired" 同名异义必须钉死：

| automount FSM（晋升轴） | 149 生命周期（衰减轴） | 关系 |
|------------------------|----------------------|------|
| candidate | —（晋升侧前置） | 晋升判定归 187 门 |
| sim | —（未上线，无衰减语义） | |
| production | certified/probation（活跃期衰减监测=150 辖区） | 并存：production 是资格，certified/probation 是健康度 |
| retired（Owner 门翻转） | retired（衰减建议，150 产出） | **150 的 retired 建议=188 production→retired Owner 门的输入证据** |
| shelved | — | 留档侧枝，衰减轴不管 |

**规则钉死**：149/150 的 retired 永远是"建议"，production→retired 的门翻转归
automount FSM（Owner 门），两侧经台账衔接不互写状态。

## 四、双 advisor 边界裁定（唯一实质重叠）

- **automount advisor**（decay_watch/reject/candidate/hold）= **晋升资格建议**
  （能不能晋级/入库），扫描 translated_c4+oos_tested；
- **150 decay_certifier**（certified/probation/failed/retired/resurrected）=
  **在役健康度建议**（已上线后还灵不灵），扫描 strategy_screen 的 deflated_sharpe；
- 边界线=**上线时刻**：上线前归 advisor，上线后归 150；同一策略同一时刻只会被
  其中一侧管辖，建议不交叉不冲突；
- 落地动作：150 台账增注 `stage: post_production` 字段语义（本报告即裁定记录）；
  策略域会话消费时按 stage 路由两侧建议。

## 五、行动项清单

1. ~~FDR 单源裁定~~（本报告 §二，已裁定）；bhy_fdr 收敛待办挂 148 蓝图（下批）；
2. FSM 词汇映射表（§三）交 automount 线与策略域会话各执一份；
3. 150 台账 stage 字段语义裁定生效（本报告 §四）；
4. ~~C6 intake 验收⑥（Owner 复核）通过后，automount 侧 bh_filter 收敛 bhy_fdr~~
   → **已完成（Owner 通过，2026-09-15）**：bh_filter 决策核委托 bhy_fdr
   （arbitrary_dependence=False 保持预注册 BH 口径逐位一致；q≥1 退化态短路保留
   intake 契约；automount 全件 55 测试绿）；
   → **BHY 依赖稳健升级亦已完成（Owner 令"执行"，同日）**：arbitrary_dependence
   默认翻转为 True（c(m)=Σ1/i 保守校正生效，策略批内常相关语境门槛收紧），
   原 7 断言逐项验算全存活，automount 55 测试绿；
5. 双 advisor 并行运行一个季度后复盘是否物理合并（当前互补>合并收益）。

---

## 终局状态块（W8 第二圈 2026-09-21）

- 状态: A 已结案可归档
- 依据: lifecycle-consolidation-reconciliation.md 即两线合并对账收口产物+lifecycle-protocol-v2 定稿
- 归档/留场: archive/2026-09/pattern_line/
- 备注: resurrection-watch-plan 为观察哨注记随档；协议若被治理引用以归档后新路径为准（死亡证明映射见 working_cleanup_campaign 台账）
