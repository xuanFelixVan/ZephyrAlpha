---
blueprint_id: MOD-SIG-087
module_id: MOD-SIG-087
module_name: signal_factory
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.1"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
responsibility_domain: 
---

# MOD-SIG-087 signal_factory 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B1-00149（C-028 信号工厂，裁定=做 P1）+
> 候选注册表 CAND-TESTB-002。代码：`src/zephyr/signal_ashare/strategy_signal/signal_factory.py`

## 0. 定位

信号散件众多、9 阶段生命周期工厂与密度预测增强输出未成统一信号工厂（深挖裁定理由）。
本模块是**信号从生成到入漏斗的统一收口**：9 阶段状态机 + 信号注册表 +
conditional_density_predictor（MOD-SIG-043）增强输出（分位数/置信度）+
信号质量（SIGQC）与拥挤度门挂接口 + 产出入漏斗。

与既有件边界：
- MOD-SIG-043 conditional_density_predictor：密度预测算法件，本工厂**消费其输出契约**
  （quantiles/confidence 注入位），不重写算法。
- MOD-SIG-086 selection_funnel_skeleton：漏斗骨架，本工厂产出 FUNNELED 信号**供其消费**，
  不实现漏斗逻辑。
- 策略生命周期 7 阶段（域蓝图 MOD-L03-001 strategy_lifecycle）：管策略，不管信号；正交。

## 1. 接口

```python
class SignalStage(str, Enum)  # 9 阶段封闭集，顺序不可跳跃
@dataclass(frozen=True) class SignalFactoryConfig
@dataclass(frozen=True) class SignalRecord       # 单信号全生命周期记录
@dataclass(frozen=True) class SignalFactoryResult
class SignalFactory:
    def register(self, draft: SignalDraft) -> SignalRecord            # IDEA 注册（幂等键）
    def advance(self, signal_id, *, density=None, quality=None,
                crowding=None) -> SignalRecord                        # 逐阶段推进+门禁
    def funnel_batch(self) -> list[SignalRecord]                      # FUNNELED 批量产出
```

9 阶段：DRAFT→VALIDATED→DENSITY_ENHANCED→QUALITY_GATED→CROWDING_GATED
→FUNNELED→RELEASED→EXPIRED→RETIRED（EXPIRED/RETIRED 为终态分支，正向主链 7 跳）。

## 2. 纪律

- 状态不可跳跃、不可倒退；非法迁移 ValueError（fail-closed）。
- 质量门/拥挤度门为注入 callable（SIGQC/拥挤度模块未建时默认放行并留 notes），
  分数落在记录上可追溯。
- frozen dataclass、to_dict JSON 可序列化；纯内存注册表，不直连 DB。
- 空 id/非法强度/负置信度 → ValueError。

## 3. 依赖

- import：conditional_density_predictor（MOD-SIG-043，DensityForecast 契约鸭子类型）。
- 上游：信号散件（各 analyzer）；下游：selection_funnel_skeleton（MOD-SIG-086，候选消费方）。

---

## 4. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 4.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/signal_ashare/strategy_signal/signal_factory.py` | ✅ 已实现 | |

### 4.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §4（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
