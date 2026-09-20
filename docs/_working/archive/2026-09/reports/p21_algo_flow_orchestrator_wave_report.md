---
ttl: task_bound
session: st-btfix-p16-20260916
date: 2026-09-16
---

# P2-1 ALGO_FLOW orchestrator 域出仓批报告（st-btfix-p16-20260916，GW10 中小域 wave）

## 概要

承批9 三域 354 文件实证配方（dry-run 核数→出仓→幂等复扫→域测试→网关提交），orchestrator 域（`src/zephyr/orchestrator/`）单域 73 文件 ALGO_FLOW 内联块全量外迁一次完成。零失败、零 .bak 残留、幂等复扫干净。

| 项 | 数 | 备注 |
|----|----|----|
| 普查内联块文件 | 73 | 任务口径 75 为普查时点差（见自裁①），以工具现查为准 |
| dry-run 将产 yaml | 73 | 唯一路径 73（stem 碰撞预判修复后） |
| 正式出仓 externalized | 73 | failed=0，yaml 新建 73，external 锚 73，锚-yaml 链接零重复 |
| 幂等复扫 | 0 dryrun / 0 failed | 73 skipped（全部已带锚） |
| 全量 round-trip | 69 精确一致 + 4 文档化 reroute | 见自裁⑥ |
| 域测试（两轮） | 482 passed / 495 passed | 0 failed；第二轮含出仓器单测 5 + ALGO-FLOW-LINK 门禁测试 8 |
| 提交 | 见 §提交 | yaml+源码锚+工具+单测同批 |

外迁行数合计 2458 行内联块（dry-run block_lines 求和）。

## 工具最小修（本批新发现 bug，最小修+单测）

`externalize_algo_flow.py` 的 `_yaml_rel_for` 依赖"盘上 yaml 已存在"改道 `parent__stem`——同批内后处理文件的改道依赖 rglob 排序+落盘副作用，**dry-run 预测路径与正式跑不一致**（b9 映射改道雷同族）。orchestrator 域实证碰撞对：`task_queue.py`（域根）与 `core/task_queue.py`（子包）同 stem，dry-run 预测双双落 `task_queue.yaml`。

修法：新增 `_plan_stem_collision_remaps(targets)` 批开始前静态判定——同 domain_dir 内非 `__init__` 同 stem ≥2 文件时，域根件保平铺名、子包件确定性改道 `<parent>__<stem>.yaml`，处理顺序无关；`externalize()` 解析序=既有 yaml 反查 → 批级预判表 → 原推导。首版深度判断误用绝对路径 parts（Windows 盘符占 2 段）被单测当场红/绿闭环。单测 `tests/governance/generators/test_externalize_algo_flow_remap.py` 5 绿（无碰撞/碰撞改道/顺序无关/`__init__` 豁免/真实 orchestrator 清单）。

## 红蓝测试（T7）

| 场景 | 注入 | 结果 |
|------|------|------|
| RED-1 yaml 丢失 | 沙箱锚指向不存在 yaml | ALGO-FLOW-LINK **BLOCKED** ✓ |
| RED-2 坏块/幽灵 sot | yaml 块缺节点 + source_of_truth 指向不存在源 | ALGO-FLOW-LINK **BLOCKED** ✓ |
| RED-3 锚错位 | A 源身份锚指向 B 的 yaml | 门禁按存在性口径放行（设计边界，存在性+可解析+sot 回指不查 1:1 配对）；**自建配对校验器 CAUGHT** ✓ |
| BLUE control | 真实 148 件清单全量过门禁核心 | **PASS**；配对校验器 73/73 一致、0 重复、0 错位（本批后可作复核器复用） |

## 配套登记

- **创建令牌**：+73 条（`docs/03_modules/_domain_orchestrator/algo_flow/*`，capability `btfix_p1p2`，created_by st-btfix-p16-20260916）+ 本报告 1 条，经 `batch_creation_tokens.py`（CAS 一次成功）。
- **capability registry**：`capability_canonical_file_registry.yaml` 同批。该文件工作区另有他会话在途净增条目 5 条（scaffold.py×4 资源排班车道 + st-sopx×1，与本批 73 条零交集）——批9 两次背书"吸收=净增无害"惯例，随报告批一并落库并在提交后 `git log` 核实归属。
- **TDM/ALGO-NOTE-SYNC**：TDM 138 节点中 module_ref 指向 `src/zephyr/orchestrator/` 的为 **0**（唯一含 "orchestrator" 字样的 TDM-X-S1-06 指向 trading 域文件，不在本批触碰集）→ 无需 note_confirmed 推进，同 autonomy_core 零引用先例。

## 自裁记录（自主裁量，逐条留痕）

1. **75 vs 73**：任务口径"orchestrator 域 75 件"系普查时点差；现查 `grep -rl "\[ALGO_FLOW\]"`=73 文件/73 块，以工具/普查为准条款执行 73。域名带 orchestrator 的他域文件（autonomy_core/clone_guard/ex_core 等 20+ 文件）按域归属不碰。
2. **GOV-DOC-018 平铺容量**：73 ≤120（ERROR 阈值）→ 按任务口径不拆子目录（60 WARNING 阈值已超，落 WARNING 级留痕；后续域若增量可按 autonomy_core 镜像子目录先例重排，工具侧 `_existing_yaml_for` 反查保证幂等）。
3. **stem 碰撞**：见 §工具最小修。
4. **注册表 claim 冲突**：`capability_canonical_file_registry.yaml` 被 st-btfix-p15-20260916 网关 claim 持有（PID 存活+心跳 35.8 分 <3600s TTL，按双判据仍算存活）→ **不强抢释放**；本批主提交剔除注册表（148 件），注册表随报告批落库（届时 TTL 到期或按批9 吸收惯例处理）。
5. **FRONTEND-MAP 阻断**：首次提交尝试被 FRONTEND-MAP 硬阻——违规点 `F-RESWEEK-WEEKGRID→module:MOD-RESCHED-VIEW` 系 GW2 会话**在途未提交**内容（frontend_map.yaml 工作区 diff +08 行、resource_week_view 蓝图为 ?? 新文件，08:54/08:57 刚落盘，晚于 depgraph 上次同步 08:45）。按宪法 §3.4"他会话在途违规不代修、owner 责任制"等待其落地，不代修 frontend_map、不抢刷 depgraph（防半成品入图）；CAPABILITY-LOOKUP-REQUIRED 按 trae_077 补 `CapabilityLookup.find` 审计后重试。
6. **reroute 语义澄清**：非 `__init__` 文件 64 件的 `rerouted_to`=自身（extractor 经 external 锚解析回本文件，链路通的标注特性非改道）；9 个 `__init__.py` 中 4 个子包 init（core/execution/fault_tolerance/quality）终验路由到子文件图（工具头部注释文档化行为："富 docstring 遮蔽态解除，子文件自带图接管"）——该 4 件 yaml 块独立解析=迁移前记录 3/2 逐项一致，迁移无损。

## 提交

**主批 `36de8a4c`**（2026-09-16 09:42:27，148 文件）：73 源码锚 + 73 yaml + 出仓器最小修 + 单测。`git log -1 --name-only` 归属核实：src/zephyr 73 / docs/03_modules 73 / tests 1 / scripts 1，**frontend/config/api_server 零吸收**。

过闸路径实录（三次尝试，全为门禁语义而非本批工件问题）：

1. 第 1 次：CAPABILITY-LOOKUP-REQUIRED 阻断（会话未做能力反查审计）→ 补 `CapabilityLookup.find`×3 后放行条款重试（批9 同款）。
2. 第 2 次：FRONTEND-MAP 阻断——`F-RESWEEK-WEEKGRID→module:MOD-RESCHED-VIEW` 悬空系 st-resource 会话在途内容（恒跑门禁不按文件过滤，全体提交人同被阻）。按 §3.4 等待其落地：st-resource 09:34 落库 B1 批（aa253167d9，含 depgraph 设计节点登记 MOD-RESCHED-VIEW），复检 `check_frontend_map` fail=0，阻断自愈。
3. 第 3 次：PREFLIGHT SESSION-REQUIRED（失败提交 finally 释放 claim 后 pid 绑定会话随进程退出判死）→ 按裁定#252 保活模式补 pid=0 逻辑会话注册+分离式 heartbeat daemon（30s）→ 过闸落地。

**报告批**（本笔）：报告 .md + creation token（+1）+ `capability_canonical_file_registry.yaml`（本会话 73+1 条 + 他会话在途净增条目吸收，纯插入零冲突）。

## 跳过/待裁

无（目标空）。FRONTEND-MAP 等待落地为状态非跳过；GW2 落库后本批重提即过。

## 清理确认

- 出仓器 .bak：0 残留（find 全域核查）
- `.runtime/tmp/` 本批工件：dry-run JSON×2、运行 JSON×2、commit 清单/message——提交后清理
- red-blue 沙箱 `.runtime/tmp/redblue_p16/`：用后即清
- lock_files claim：73 源文件+工具+单测+报告，收尾 release-all
- 网关 claim：提交成功后 finally 自释放；剩余（报告/注册表）随报告批 release-only 兜底
