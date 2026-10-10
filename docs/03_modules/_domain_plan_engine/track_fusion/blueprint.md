---
blueprint_id: MOD-PLAN-020
module_id: MOD-PLAN-020
module_name: track_fusion
domain: D_PLAN
doc_type: blueprint
ttl: permanent
design_maturity: production
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.1"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_PLAN
path: src/zephyr/plan_engine/track_fusion.py
granularity: file
responsibility_domain: 
---

# MOD-PLAN-020 track_fusion 蓝图（四轨融合器 Multi-Track Fusion，v8.0）

> **module_id**: MOD-PLAN-020 | **域**: D_PLAN | **优先级**: P1
> **来源**: B10-01212（AUD-DRAFT-001-DIGEST P1 波 W-P1-19，CAND-PLAN-014，A1交易决策架构 §1.1）
> 代码：`src/zephyr/plan_engine/track_fusion.py`

## 0. 定位

四轨融合器（Multi-Track Fusion，v8.0）：输入轨道1/2 自动信号 + 轨道3 人工
指令 + 轨道4 应急指令，按**应急 > 人工 > 自动**优先级裁决输出统一目标仓位/
信号，冲突时升 L6 审查。TSV 现状注记：position_sizing_engine 头注明示
"不包含(阶段2):四轨融合(轨道2/3/4)"，轨道3人工/轨道4应急枚举已在
position_audit_logger（审计分类），融合器本身是真实缺口。

查重分工（W-P1-19 铁律③探查，均不复制）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| sell_signal_fusion_engine | MOD-SELL-007 | 卖出域多信号融合（置信度一致性） | 卖出域专用，不管四轨优先级与 L6 升级 |
| position_sizing_engine | MOD-POS-001 | Kelly+13 约束仓位裁决（轨道1 自动输入的消费方） | 头注明示四轨融合是阶段2 缺口；本模块裁决后**目标仓位由其精裁** |
| position_audit_logger | MOD-POS-009 | 审计落库（含轨道3/4 枚举分类） | 审计分类非融合器；本模块 verdict 供其落库（装配批） |

不做什么：不做 Kelly 精裁（归 MOD-POS-001）、不直接下单（只出 FusedDirective）、
不采集轨道信号（调用方注入）、AI 发现轨信号**必须**经 L6 审查（不可豁免）。

## 1. 裁决规则（确定性，纯函数）

- **优先级**：轨道4(EMERGENCY) > 轨道3(MANUAL) > 轨道1/2(AUTO)。
  应急信号在场 → 直接胜出（priority_track=4，strength=EMERGENCY_OVERRIDE）；
  无应急有人工 → 人工胜出（与自动轨冲突 → needs_l6_review=True 留痕）；
  仅自动 → 按下条。
- **自动轨融合**：轨道1+2 同向 → 强共振（STRONG_RESONANCE，target_weight
  取保守=min）；单轨在场 → 中等（MEDIUM）；轨道1/2 反向冲突 → 不出指令，
  升 L6 审查（CONFLICT_L6，directive=None）。
- **AI 发现轨**：任一在场信号 ai_discovered=True → needs_l6_review=True
  （不影响优先级裁决，只加审查标记）。
- Fail-Closed：track∉{1,2,3,4}/direction 非法/target_weight∉[0,1]/同轨
  多信号冲突 → TrackFusionError；空信号集 → directive=None + EMPTY 留痕。

## 2. 接口

```python
class TrackId(IntEnum): AUTO_1=1 / AUTO_2=2 / MANUAL=3 / EMERGENCY=4
class TrackDirection(str, Enum): LONG / REDUCE / EXIT / FLAT
@dataclass(frozen=True)
class TrackSignal: track / direction / target_weight / source / ai_discovered
@dataclass(frozen=True)
class FusedDirective: direction / target_weight / priority_track / strength / needs_l6_review / reason
class MultiTrackFusion: fuse(signals) -> FusedDirective
class TrackFusionError(Exception)  # error_code 待登记
```

## 3. 依赖前置

- MOD-POS-001 position_sizing_engine（裁决后目标仓位精裁消费方，node 10619503）。
- MOD-POS-009 position_audit_logger（轨道3/4 审计分类对齐，node 10619521）。

## 4. 验收标准

- 单测全绿（应急压制/人工优先与冲突升 L6/自动强共振与单轨中等/反向冲突不出
  指令/AI 发现轨强制 L6/空集与畸形输入 Fail-Closed）；tests/plan_engine 零回归。

---

## 5. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 5.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 5.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §5（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
