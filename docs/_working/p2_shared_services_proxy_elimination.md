---
doc_type: construction_plan
status: active
title: "P2: shared_services proxy 层渐进式消除"
module_id: "MOD-ARCH_PROXY_ELIM"
version: "1.0.0"
created: "2026-06-29"
ttl: task_bound
completes_when: "24个proxy文件全部物理删除，~100处import指向真源，depgraph 24节点deprecated，capability_canonical_file_registry.yaml canonical指向真源，全量测试通过"
---

# P2: shared_services proxy 层渐进式消除

## 一、背景

`create_shared_services_proxies.py` 生成器（已 TRULY_DELETED）曾创建 24 个 proxy 文件，
位于 `src/zephyr/shared/shared_services/` 下，转发到真源（`zephyr.shared.*` /
`zephyr.infrastructure.*` / `zephyr.autonomy_core.*`）。

生成器已删除，但 24 个 proxy 文件遗留，被 ~100 处 import 引用，形成"假活"状态。

## 二、问题清单（7 个决策点）

| # | 问题 | 性质 |
|---|------|------|
| B1 | 24 proxy 整体去留（主决策：消除） | 架构债 |
| B2 | process_pool 断裂引用（已修复 commit 4eb2c9e7） | 已闭环 |
| B3 | `infra_06/cache.py` 真源路径错配（指向 infra.cache 而非 infra_06.cache） | 待修 |
| B4 | `events/` 子包半迁移状态（event_bus 已迁出，__init__.py 模式不一致） | 待修 |
| B5 | `capability_canonical_file_registry.yaml` session_continuity canonical 错指向 proxy | 待修 |
| B6 | ~100 处 import 迁移到真源 | 核心 |
| B7 | depgraph 24 节点状态同步 | 收尾 |

## 三、第一性原理裁定

proxy 层违反三条核心原则：
1. **真源唯一**——proxy 是真源的同步副本，增加同步成本
2. **向内收**——能用真源直接 import，无需多一层转发
3. **AI 可发现性**——AI 看到 import shared_services 会困惑哪个是真源

**裁定：proxy 层应消除。** 渐进式迁移，分批执行。

## 四、施工方案

### 阶段 1：逐 proxy 迁移（按引用数从少到多）

对每个 proxy 文件：
1. 搜索所有 import 该 proxy 的消费者
2. 修改消费者 import 指向真源
3. 更新消费者 `[DEPENDENCIES]` 头部注释
4. 删除 proxy 物理文件
5. `apply_depgraph.py --deprecate-node <node_id>` 软废弃 depgraph 节点

### 阶段 2：canonical 修正（B5）

修改 `capability_canonical_file_registry.yaml` 中 session_continuity 的 canonical，
从 proxy 指向真源。

### 阶段 3：独立 bug 修复（B3/B4）

- B3: `infra_06/cache.py` 真源路径错配（若 proxy 已删则无需修）
- B4: `events/` 子包半迁移归一（若 proxy 已删则无需修）

### 阶段 4：验证

- `python -m pytest tests/ -x -q` 全量测试通过
- `grep -r "shared_services" src/zephyr/` 确认零残留 import
- depgraph 24 节点全部 deprecated

## 五、约束

- 每批迁移通过 GitCommitGateway 提交（session_id: proxy-elim-batch-N）
- 改 depgraph.db 前必须 git commit 备份
- 每批迁移后运行相关测试确认无回归
- 不修改 human_gated 文件（除非 Owner 授权）

## 六、进度追踪

| 批次 | proxy 文件 | 引用数 | 状态 | commit |
|------|-----------|--------|------|--------|
| — | — | — | 未开始 | — |
