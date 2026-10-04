---
blueprint_id: MOD-SIG-087
module_id: MOD-SIG-153
module_name: factor_result_bridge
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: L
ai_autonomy: ai_modifiable
version: "0.1.2"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_ASHARE_SIGNAL
path: src/zephyr/signal_ashare/factor_result_bridge.py
granularity: file
responsibility_domain: 
---

# MOD-SIG-153 factor_result_bridge 蓝图（D-SIGNAL-158 因子计算结果消费桥接器）

> **module_id**: MOD-SIG-153 | **域**: D_ASHARE_SIGNAL | **优先级**: P1
> **来源**: CAND-TESTB-027（B13-04307，AUD-DRAFT-001-DIGEST P1 波 W-P1-06）
> 代码：`src/zephyr/signal_ashare/factor_result_bridge.py`

## 0. 定位

D-FACTOR→D-SIGNAL 统一消费桥接（anti-corruption layer）：信号侧不再直连因子存储，
一律经本桥接器消费因子计算结果。版本化 schema 契约消费 + 版本兼容裁定 +
`is_degraded` 透传（D-SIGNAL-77 因子可用性监控语义，factor_availability_monitor）+
消费审计。CTR-002 消费契约适配器（B13-04308，W-P1-16）未建前经 provider 回调
注入取数，适配器落地后接线（前瞻兼容，不阻塞）。

## 1. 接口

```python
@dataclass(frozen=True) FactorResultBatch: schema_version/factor_values/as_of/is_degraded/metadata
@dataclass(frozen=True) ConsumptionVerdict: batch/accepted/degraded/version_action/reason
class FactorResultBridge(provider, *, supported_versions=("1.0",), audit_sink=None, clock=None):
    .consume(as_of=None) -> ConsumptionVerdict      # 取数→版本裁定→降级透传→审计
    .audit_log -> tuple[dict, ...]                   # 消费审计记录（不可变快照）
class FactorResultBridgeError(ZephyrBaseError)       # 未挂错误码（纪律⑦）
```

## 2. 不变量

- 版本裁定三态：exact（受支持版本直通）/ compatible（同主版本兼容透传，标记
  version_action="compatible"）/ unsupported（拒绝消费，fail-closed 产空批次
  is_degraded=True，绝不静默按错版本解析）。
- is_degraded 透传：上游批次 degraded 标记原样透传到 verdict 与审计，桥接器
  自身不制造降级（版本不支持除外，显式 reason）。
- 审计：每次消费产一条不可变审计记录（as_of/版本/条数/degraded/耗时），
  audit_sink 回调外置持久化（sink 异常不阻断消费，留痕降级）。
- 纯内存判定核心无 IO：取数经 provider 注入（契约适配器职责），桥接器不 import
  因子存储/Redis/CH。

## 3. 依赖

- MOD-SIG-088 无关；上游：CTR-002 消费契约适配器（B13-04308，未建，provider 注入点）
- factor/factor_availability_monitor.py（CAND-FAC-006 已建，is_degraded 语义真源）
- shared/contracts/factor_signal.py（FactorSignal 契约形态参照）

## 4. MVP 边界

- CTR-002 适配器接线、真实 Redis/CH provider 装配留运行时装配批；
  本模块只交付版本裁定 + 降级透传 + 消费审计判定核心。

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


