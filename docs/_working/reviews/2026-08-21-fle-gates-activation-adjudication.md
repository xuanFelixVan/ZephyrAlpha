---
ttl: task_bound
---

# FLE gates 启用评估裁定书（#61 挂起项，2026-08-21 专项批 任务4）

> 授权：残余四项专项批交接指令 任务4——"CAND 登记+影响面评估+裁定启用范围（全启用/灰度子集/维持挂起）"。
> 前置裁定：#61（2026-08-19-night001-owner-decisions-adjudication.md §#61）——GATES_DIR 修正已落地；"FLE 48 gates 激活（补注册条目+类名推导修复+逐 gate 契约评审）属生产行为实质变更，登记 CAND 专项，不夹带本批"——本裁定承接该登记义务并补齐影响面实证。

---

## 一、影响面实证（2026-08-21，探针 .runtime/_b8_probe_fle_gates.py 全量模拟）

### 1.1 注册表层：条目丢失史

- 2026-05-19 7ed644a288（batch commit）重写 `src/zephyr/gates/_registry.yaml`（当时路径）：82 条 → 43 条，**43 条 `fle_self_defense` 条目全部丢失**（before fle=43 / after fle=0，git show 实证）。
- 现行真源 `gov_enforcement/rule_enforcement/_registry.yaml`（93 条）：`fle_self_defense` 条目=**0**。
- `auto_sync_all_registries.py::sync_fle_gates()` 具备再生能力（扫 `feedback_loop/gates/*.py` 自动登记），但**不跳过 `_` 前缀聚合模块**——`_governance_gates.py` 等 4 件会产出 `FLE--GOVERNANCE-GATES` 畸形 ID（stem 首字符下划线→replace 后前导连字符）。

### 1.2 加载层：类名推导实证（48 gate 文件全量 import 探针）

| 指标 | 实证值 |
|---|---|
| gate 文件发现 | 48（44 真实 + 4 个 `_` 前缀聚合模块） |
| import 成功 | 48/48 |
| **现行推导精确命中** | **0/48**（`gate_id.lower().replace("fle-","").split("_")`——gate_id 是连字符分隔，split("_") 永远整串单段，如 `Adversarial-validation`） |
| 修复后推导命中（连字符+下划线双分隔） | 36/48（12 miss=4 聚合模块+8 类名不规则门） |

现行推导 0 命中后走 fallback：`dir(module)` 字母序**首个 public 类**——对 safety_gate_l1_l27 等模块即 `ActionContext`（共享 dataclass）而非 gate 类；实例化 TypeError → 以类本体当实例 → `check/gate/audit/evaluate/validate` 五方法全无 → 返回 True。**即"激活不修推导"=加载任意类+恒 True 空转——纯仪式性激活**。

### 1.3 语义层：_evaluate_gate_method 契约失配（修复推导后的真实阻断面）

| 门族 | 首方法签名 | 现行求值路径 | 激活后行为 |
|---|---|---|---|
| L 系 17 门（safety_gate_l28_29…l66_67 + parameterized） | `evaluate(ctx) -> list[GateResult]` | evaluate 分支：`hasattr(result,"verdict")`=False（list 无）→ `bool(result)` | **语义反转**：空列表=零违规=干净 → `bool([])`=False → **误阻断**；非空=有违规 → True → 放行。完全反了 |
| action_reversibility | `gate(action, reversibility, autonomy_level)` 3 参 | `len(params)>=2 → True` | 恒 True 空转 |
| scope_creep_monitor | `audit(action_id, authorized_level, actual_scope)` 3 参 | 同上 | 恒 True 空转 |
| blueprint_validator | `validate(blueprint_files, code_files)` 2 参 | 同上 | 恒 True 空转 |
| data_quality_gate | `validate(data: dict)` 1 参 | 以 `"fle_action"` 字符串实参调用 | 预计 False/异常→True（异常才兜底 True；**返回 False 即误阻断**） |
| 23 门无五方法 | — | 五方法全 miss → True | 恒 True 空转 |

### 1.4 消费层：阻断语义真实存在

`scheduler.py:627-633`：`run_safety_gates` 结果任一 False → `blocked` 列表非空 → **FLE Act 阶段自愈动作被压制**（log warning + event 落库 + return）。触发条件：anomaly 进入 Act 阶段（非 30s poll 路径）。全链其余环节 fail-open 设计不变。

## 二、第一性原理

1. **门禁系统的第一美德是"语义诚实"**：gate 结果 False 必须有"确实检测到违规"的含义。当前激活路径下 False 的含义是"空列表/单参误调/任意类加载"——防护语义倒置，比无防护更危险（误阻断自愈动作+以为有防护）。
2. **激活=新功能上线**（#61 已定）：44 门逐门契约评审是激活的前提工序，不是激活的附带动作。灰度子集的前提是"子集语义已被实证正确"——L 系 17 门语义反转修复前，任何子集都不满足此前提。
3. **空转的真实危害是认知静默**（#61 依据）：治理动作应让"无防护"在注册/测试/文档层可见——本裁定+CAND 登记+tracker 翻账即完成该暴露义务；运行时从"静默空转"变"显性挂起"。
4. **FLE 自卫门禁守护的是 Act 阶段自愈动作**——该阶段属第三期 AI 自治域，当前生产未跑自治 Act 主链，无即时暴露面；激活紧迫性低，正确性门槛高。

## 三、裁定结果

**维持挂起**（三选项：全启用/灰度子集/维持挂起）。

1. **不启用**：不修推导的启用=仪式性空转（0/48+任意类 fallback）；修推导后的启用=L 系语义反转误阻断+data_quality 误阻断——两条路径都不满足"语义诚实"底线。
2. **CAND 登记转正**：CAND-FBL-002 落 candidate_module_registry.yaml（附完整施工清单：sync 脚本 `_` 模块跳过 + 类名推导连字符修复 + evaluate 分支 list 语义修正 + 44 门逐门契约评审 + L 系 17 门语义统一后灰度子集先行）。
3. **启用触发条件**（CAND trigger）：Owner 排期 + 三修复落地 + 逐门契约评审完成 + FLE Act 自治主链临近上线（第三期）。
4. tracker #61 行补登闭环：评估完工、CAND 已登记、启用维持挂起等 Owner 终审。

## 四、落地核验

| 项 | 证据 |
|---|---|
| 探针 | .runtime/_b8_probe_fle_gates.py（48 文件 import+推导命中+首方法签名全量输出 .out） |
| 丢失史 | git show 7ed644a288 前后 registry 对照（fle 43→0） |
| CAND | CAND-FBL-002（本批同 commit） |
| 回归 | 零代码变更，无需回归；tests/safety/test_scheduler_safety.py 现状全绿（fail-open 契约钉在测试） |

---

**裁定人**：专项统筹（Owner 授权调研裁定；启用施工属生产行为变更，维持挂起等 Owner 终审）
