---
module_id: MOD-DATA-072
title: "跨境网络双活传输层蓝图 — 双线路+热切换状态机"
doc_type: blueprint
status: Active
version: "0.1.3"
design_maturity: production
ttl: permanent
layer: L1_foundation
layer_name: foundation
functional_domain: data
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-09-16"
last_updated: "2026-09-16"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-DATA-072 跨境网络双活传输层 — 双线路+热切换状态机蓝图

> **module_id**: MOD-DATA-072 | **域**: D_DATA | **消费节点**: CAND-CRYPTO-002（行情 WS 跨境承载，候选）；CAND-CRYPTO-005（执行回传共用，候选）
> **出身**：裁定#262 后续路径执行批（st-transport-20260916，Owner 2026-09-16"解决所有欠账"令）——transport 双源节点（`src/zephyr/data/transport/__init__.py` + `cross_border_dual.py`）原挂 CAND-CRYPTO-009 无 MOD 锚，depgraph blueprint_id 空。本件=该模块的正式 MOD 蓝图注册+转正落位，设计真源保留引用。

## 1. 模块语义（摘自代码头/INVARIANTS）

境内基建↔境外交易所双线路传输层：主线路（PRIMARY）=HTTPS 直连（Caddy TLS 终结+DNS-01 证书+来源 IP 白名单），备用线路（BACKUP）=Cloudflare Tunnel（Access Service Token 鉴权、cloudflared 隧道、不暴露源站）；控制面走 CF、数据面正常直连、异常自动降级 CF。

热切换状态机三条纪律（94号 §7.2 外部实战血泪教训）：
1. 切备必须三感知同时成立——连接失败+吞吐下降+积压超阈值（5 秒桶），不能只看连接存活（"活着但跟不上"的主线路要主动绕开）；
2. 切回用纯时间驱动 60 秒探测，不依赖"积压=0"等发送中永远达不到的静态条件；
3. 积压计数器饱和递减（最低到零），防无符号下溢误判天文数字积压。

配套能力：cloudflared 隧道配置 YAML 生成（`render_cloudflared_config`）；`zephyr.data.transport` 包对外导出双线路状态机与配置类型。

## 2. 设计真源

docs/_working/archive/2026-09/design_memos/94_crypto_quant_expansion.md §7.2（v0.2.0，跨境网络双活与传输加工；候选登记=2026-08-26 外部材料审查批，Owner 裁定补登；骨架落盘=2026-08-28 AI-CAL-001）。

## 3. 注册说明

- 编号 MOD-DATA-072 于 2026-09-16 由 st-transport-20260916 会话分配注册（裁定#262 登记的后续路径：94号 crypto 施工批前先补齐 blueprint_id 绑定欠账，Owner"解决所有欠账"令）。
- 候选转正：CAND-CRYPTO-009 → MOD-DATA-072（candidate_module_registry 同批更新 status/promoted_to；同 commit 补两源文件头 [BLUEPRINT]+[A_module] 注释，generate_project_depgraph 再生后 blueprint_id 随扫描自然落位——正门且防复发）。
- 本蓝图只做身份注册与语义索引，不改模块行为；模块成熟度见代码头 [MATURITY]（skeleton/evolving）。

## 9. 依赖关系

- 上游：无外部依赖（骨架期零依赖；`zephyr.data.transport` 包仅聚合子模块导出）。
- 下游（设计预期）：候选 CAND-CRYPTO-002 行情 WS 长连接跨境承载；候选 CAND-CRYPTO-005 执行下单/回执回传共用双线路。
- 算法流外部化：`docs/03_modules/_domain_data/algo_flow/transport__init__.yaml`、`docs/03_modules/_domain_data/algo_flow/cross_border_dual.yaml`。

## 10. 产出物

- 源码：`src/zephyr/data/transport/__init__.py`（包导出）、`src/zephyr/data/transport/cross_border_dual.py`（状态机+配置生成）。
- 测试：`tests/zephyr/data/transport/test_cross_border_dual.py`。
- 运维预案（设计真源引用）：双线路全断时数据留边缘 WAL 指数退避重试（双层 WAL 故障域分离，94号 §7.2）。

---

## 11. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 11.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/data/transport/__init__.py` | ✅ 已实现 | |
| `src/zephyr/data/transport/cross_border_dual.py` | ✅ 已实现 | |

### 11.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §11（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-DATA-072`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-DATA-072` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-DATA-072` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-DATA-072 | MOD-DATA-072 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
