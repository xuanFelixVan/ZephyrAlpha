---
blueprint_id: MOD-RK-046
module_id: MOD-RK-046
module_name: risk_contagion_modeler
domain: D_RISK
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
domain_id: D_RISK
path: src/zephyr/risk/risk_contagion_modeler.py
granularity: file
responsibility_domain: 
---

# MOD-RK-046 risk_contagion_modeler 蓝图（风险传播建模器）

> **module_id**: MOD-RK-046 | **域**: D_RISK | **优先级**: P2
> **来源**: B14-04692（AUD-DRAFT-001-DIGEST P2 波 P2-W09，CAND-RSK-050，A9 M15-S01）
> 代码：`src/zephyr/risk/risk_contagion_modeler.py`

## 0. 定位

风险传播网络：板块/个股相关性+产业链边建图（边权注入）+冲击传导路径模拟（初始冲击沿边衰减传播）+传染评分（节点暴露度）+评分入风控参考输出+盘后运行语义。Diebold-Yilmaz思想轻量版。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/risk/test_risk_contagion_modeler.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。

---

## 4. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 4.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

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
