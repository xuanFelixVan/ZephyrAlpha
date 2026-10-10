---
blueprint_id: MOD-SIG-124
module_id: MOD-SIG-124
module_name: fake_move_distribution
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: production
stability: evolving
safety_level: M
ai_autonomy: human_gated
version: "0.1.1"
created: 2026-08-26
last_updated: 2026-08-26
owner: ZephyrAlpha-Owner
priority: P2
blueprint_level: module
domain_id: D_ASHARE_SIGNAL
path: src/zephyr/signal_ashare/ml_forecast/fake_move_distribution.py
granularity: file
responsibility_domain: 
---

# MOD-SIG-124 fake_move_distribution 蓝图（主力假动作与筹码派发识别）

> **module_id**: MOD-SIG-124 | **域**: D_ASHARE_SIGNAL | **优先级**: P2
> **来源**: B10-01425（AUD-DRAFT-001-DIGEST P2 波 P2-W05，CAND-TESTB-044，A1 模块27）
> 代码：`src/zephyr/signal_ashare/ml_forecast/fake_move_distribution.py`

## 0. 定位

假动作6模式规则库（假拉升真出货/假突破真派发/假吸筹真对倒/假洗盘真出货/假护盘真诱多/假反弹真派发词表闭合，各含表面行为+底层矛盾信号）+7维信号打分（主动买入占比/大单净流入/量能持续/板块跟涨率/拉升时段/底部筹码/龙虎榜注入数据）+>85%暂停追涨输出FakeMoveWarning。canonical承接TESTB-056归并。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/signal_ashare/ml_forecast/test_fake_move_distribution.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。

---

## 4. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 4.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/signal_ashare/ml_forecast/fake_move_distribution.py` | ✅ 已实现 | |

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
