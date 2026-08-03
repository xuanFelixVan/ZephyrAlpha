---
ttl: permanent
doc_type: architecture_view
status: production
version: "1.0.0"
date: 2026-08-03
---

# 生成器自动触发机制（试点：battle_map）

> **文档状态**：已落地（2026-08-03）。试点 battle_map 跑通后已推广至 23 个生成器。
> 现状详见 [AGENTS.md §11.1.3](file:///d:/ZephyrAlpha/AGENTS.md)。本文件为设计起源归档。

## Context（为什么做）

**问题**：24 个生成器全部 `STARTUP=manual`，真源（DB/YAML）变更后文档不会自动更新。AI 基于过时文档写决策=幻觉风险；Owner 手动跑生成器=易遗漏。

**目标**：让生成器在真源变更后自动重生成，无需手动启动。本计划先试点 battle_map 1 个生成器，跑通机制后推广。

**用户决策**：
- DB 触发方式 = apply 内联同步调用（apply 写完 DB 后直接 import 调用生成器）
- 落地范围 = 先试点 battle_map 1 个

**核心矛盾与解法**：
- EventBus 是进程内单例，CLI 脚本退出即丢失 → 不用 EventBus 跨进程，改用进程内 import 调用
- YAML 手编无 apply 调用 → boot_hooks 启动时 mtime 对比兜底

## 架构设计

### 事件流（两条路径覆盖两类真源）

```
路径1·DB真源变更（实时）:
  apply_battle_map.py commit → reconcile_generators.reconcile("battle_map_db")
  → import generate_battle_map_diagram.regenerate() → 写 MD+HTML

路径2·YAML真源变更（启动时）:
  手编 module_translation_registry.yaml → git commit
  → 下次交易运行时启动 → boot_hooks 调 reconcile_generators.reconcile_stale()
  → mtime对比: YAML比产物新 → reconcile("battle_map_yaml") → 重生成
```

### 四个组件

| 组件 | 路径 | 角色 |
|---|---|---|
| 生成器注册表 | `docs/01_policies_and_standards/_registry/catalogs/generator_registry.yaml` | 真源：声明 {generator, trigger_sources, entry_function, module_path, input_sources, output_globs} |
| 统一编排器 | `scripts/governance/reconcile_generators.py` | 单一入口：`reconcile(source)` 查注册表调生成器；`reconcile_stale()` mtime 对比扫描 |
| 生成器改造 | `scripts/governance/d5_architecture/generators/generate_battle_map_diagram.py` | 新增 `regenerate(output_dir=None)->dict` 可调用接口 |
| apply 改造 | `scripts/governance/apply_battle_map.py` | `_execute_ops()` commit 后调用 reconcile |
| boot_hooks 改造 | `src/zephyr/trading/boot_hooks.py` | 注册 `_subscribe_governance_regeneration`：启动时调 reconcile_stale |

## 改造清单（5 文件，3 新建 2 改）

### 1. 新建 `generator_registry.yaml`（真源）
```yaml
# 生成器自动触发注册表（TRAE-062 规则数据真源=YAML）
# reconcile_generators.py 只读此表，禁止反向写入
generators:
  - name: battle_map
    module_path: scripts.governance.d5_architecture.generators.generate_battle_map_diagram
    entry_function: regenerate
    trigger_sources:
      - battle_map_db        # apply_battle_map 写 DB 后触发
      - battle_map_yaml      # YAML 叙事变更后触发
    input_sources:
      - db:battle_map_steps|anchors|edges
      - yaml:docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml#battle_map_steps
      - yaml:docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml#battle_map_cross_cutting
      - yaml:docs/01_policies_and_standards/_registry/catalogs/battle_map_domain_policy.yaml
    output_globs:
      - docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/*.md
      - docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/_zoomable_html/*.html
```

### 2. 新建 `reconcile_generators.py`（编排器）
核心函数：
- `reconcile(source: str) -> dict`：按 trigger_source 查注册表，import 生成器模块，调用 `entry_function()`，返回 {generator, status, outputs, elapsed}
- `reconcile_stale() -> dict`：遍历注册表，对比每个生成器 input_sources 的 mtime vs output_globs 的 mtime，输入更新则触发 reconcile
- 生成失败不抛异常，返回 `{"status": "failed", "error": ...}`（生成是派生，不阻断真源写入）
- 路径处理：用 `REPO_ROOT` 拼绝对路径，`sys.path.insert` 确保 import

### 3. 改造 `generate_battle_map_diagram.py`
- 从 `main()` L1436-1468 抽取核心逻辑为 `regenerate(output_dir: Path | None = None) -> dict`
  - 返回 `{"outputs": [path1, path2, ...], "steps": N, "edges": N, "anchors": N}`
  - 不 print（print 留在 main 里）
- `main()` 改为：`result = regenerate(); print(...); return 0`
- 文件头 `[STARTUP]` manual → `event_driven`（通过 reconcile_generators 编排器自动触发）

### 4. 改造 `apply_battle_map.py`
- `_execute_ops()` L595 `conn.commit()` 成功后（非 dry_run）插入：
```python
# 真源写入成功 → 自动派生重生成（编排器查 generator_registry.yaml）
try:
    from scripts.governance.reconcile_generators import reconcile
    regen = reconcile("battle_map_db")
    if regen.get("status") == "ok":
        print(f"  ↳ 自动重生成: {regen['generator']} ({len(regen.get('outputs',[]))} 文件)")
    else:
        print(f"  ⚠ 自动重生成失败（不阻断写入）: {regen.get('error')}", file=sys.stderr)
except Exception as e:
    print(f"  ⚠ 编排器不可用（不阻断写入）: {e}", file=sys.stderr)
```
- 关键：生成失败不阻断 apply（apply 是真源，生成是派生，§2.3 派生关系）

### 5. 改造 `boot_hooks.py`（YAML 兜底）
- 在 `register_boot_hooks()` 末尾新增 `_subscribe_governance_regeneration()`：
```python
def _subscribe_governance_regeneration() -> None:
    """启动时扫描生成器输入源 mtime，YAML 比产物新则重生成（§3.2 事件驱动·启动事件）."""
    try:
        from scripts.governance.reconcile_generators import reconcile_stale
        result = reconcile_stale()
        if result.get("regenerated"):
            logger.info("Governance regeneration: %d generators refreshed", len(result["regenerated"]))
    except Exception as e:
        logger.warning("Governance regeneration scan failed: %s", e, exc_info=True)
```
- 复用现有 boot_hooks 模式（try/except + logger，不阻断启动）

## 治理清单合规要点（C 类·施工时走完整 11 节）

| 节 | 关键合规决策 |
|---|---|
| §0.5 改动分类 | C 类（永久系统：reconcile 编排器 + boot_hooks 注册） |
| §1.4-1.6 自动机制 | 启动=boot_hooks 注册；运行=reconcile 内联调用；关闭=调用返回（无守护线程） |
| §2.2 真源唯一 | generator_registry.yaml 是单真源，apply/编排器只读；生成器产物是派生缓存 |
| §3.1 能现成不创造 | 复用 boot_hooks 模式 + REPO_ROOT；无现成编排器故新建 |
| §3.2 创造必全自动 | 事件驱动（apply写入+boot启动），boot_hooks 注册，无 cron/Timer/manual-only |
| §6.1 跨层契约 | apply_battle_map 的 `_execute_ops` 签名不变，只在 commit 后加调用 |
| §8.4 能力登记 | reconcile_generators.py 登记到 capability_registry + script_manifest |
| §11 depgraph | reconcile_generators.py 作为新模块登记依赖（apply_depgraph L1 铁律） |

## 验证方案

### 验证1·DB 触发（实时）
```
python scripts/governance/apply_battle_map.py --update-step --step-id BM-BUY-02 --field sort_order --value 21
# 预期：commit 后自动打印 "↳ 自动重生成: battle_map (16 文件)"
# 预期：battle_map_02_buy_flow.md 的 mtime 更新
```

### 验证2·YAML 触发（启动时）
```
# 手编 module_translation_registry.yaml 改一条叙事 → git commit
# 重启交易运行时（触发 boot_hooks）
# 预期：日志 "Governance regeneration: 1 generators refreshed"
# 预期：battle_map MD 的 mtime 晚于 YAML mtime
```

### 验证3·生成失败不阻断
```
# 故意破坏生成器（如改坏 regenerate 函数签名）
python scripts/governance/apply_battle_map.py --update-step ...
# 预期：apply 写入成功（exit 0），打印 "⚠ 自动重生成失败（不阻断写入）"
```

### 验证4·对齐器一致性
```
python scripts/governance/align_battle_map.py
# 预期：0 问题（自动重生成后文档与 DB 一致）
```

## 推广路径（试点后）

1. 试点 battle_map 跑通 → 验证机制可行
2. 推广到 4 个全景图生成器（depgraph/dataflowgraph/decisiongraph，apply 模式一致）
3. 按依赖关系逐步覆盖其余 20 个（YAML 类/代码类生成器触发源不同，需逐一梳理 input_sources）
4. 每推广一个，在 generator_registry.yaml 加一条
