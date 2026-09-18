---
ttl: task_bound
completes_when: 总包据本处方修复后关闭
---

# 处方 req_verifier3_02 — `battle_map_domain_policy.yaml` 未挂 ROOR（尺子只能走降级发现通道）

请求方=`st-ff-verifier3-20260918`　处置方=总包（`registry_of_registries.yaml` 是热文件，
且 battle_map 族在册他车道名下，本车道不代改）

## 现象（本会话亲验）

验收仪 `flowthrough_verifier.py` 的 6 个论域真源里，两本治理册走 ROOR 反查
（RULE-REGISTRY：ROOR 是注册表发现的唯一真源；同时是 VOCAB-CHAIN 的治本要求——禁硬编码 SSoT 路径）：

| 真源 tag | registry_id 申报 | ROOR 反查结果 | 尺子实际发现方式（自标） |
|---|---|---|---|
| `B_functional_domain_registry` | `REG-FUNC-DOMAIN-001` | **命中** | `ROOR:REG-FUNC-DOMAIN-001` ✅ |
| `C_battle_map_domain_policy` | `REG-BATTLE-MAP-DOMAIN-POLICY` | **未命中** | `catalog_dir_fallback(ROOR 无此册)` ⚠️ |

取证命令（可复跑）：

```bash
grep -n -i "battle" docs/registry_of_registries.yaml          # → 0 命中（亲验）
grep -n -i "registry_id" docs/01_policies_and_standards/_registry/catalogs/battle_map_domain_policy.yaml
                                                               # → 0 命中（亲验：该册自身未声明 registry_id）
```

即：**不是尺子的反查写错了，是这本册根本没进 ROOR，且自身无 registry_id 可被匹配。**

## 为什么这算债而不算"已解决"

尺子当前行为是**诚实降级**（不猜路径、输出里显式写 `catalog_dir_fallback(ROOR 无此册)`、
不冒充 ROOR 命中），所以不会静默出错。但它意味着：
论域 6 源里有 1 源的发现**绕过了** RULE-REGISTRY 唯一真源，改为"目录 + basename 拼接"。
一旦该册改名或移位，尺子会在**论域推导**这一步静默拿到 MISSING，
而论域是"未归属=0"这类结论的**分母**——分母漂了，报表却照出，正是 R-024 那类"骨架式失误"的重演路径。

## 请办（二选一，本车道不代决）

1. **正解**：给 `battle_map_domain_policy.yaml` 头部补 `registry_id`，并在 ROOR
   对应 tier 登记 `registry_id → physical_path`（须由 battle_map 册的 owner 车道或总包做，
   涉及"注册表净删/新增"属 high 门位，见宪法 §5）。
2. **次解**：若裁定该册**不该**进 ROOR（例如它是 policy 而非 registry），则请总包改判
   尺子的 tag 语义——把 `C_battle_map_domain_policy` 从"治理册（须 ROOR）"降级为
   "配置件（可 literal 登记，与 `SRC_YAML` 同族）"，从而让 `literal(非治理册)` 成为其合法标注，
   消除"降级发现"这个误导性状态。

## 附：本车道已做的防扩散

尺子的 `_source_rel_path()` 对**每个**真源都返回 `(路径, 发现方式)` 二元组，
`_load_yaml()` 把 `found_by` 写进 meta 并随报表打印，
故任何源走了降级通道都会在产物里留名，不会被"路径反正拿到了"掩盖。
